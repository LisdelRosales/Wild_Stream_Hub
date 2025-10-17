"""
FFmpeg manager for Wild_Stream_Hub
Handles FFmpeg subprocess creation, management, and monitoring
"""
import asyncio
import subprocess
import os
import re
from typing import Optional, List, Dict
from pathlib import Path

class FFmpegManager:
    """Manages FFmpeg streaming processes"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_streaming = False
        self.current_video = ""
        self.current_bitrate = "0 kb/s"
        self.rtmp_url = ""
        self.stream_key = ""
        self.video_list: List[str] = []
        self.current_video_index = 0
        self._monitor_task: Optional[asyncio.Task] = None
        self._restart_count = 0
        self._max_restart_attempts = 5
        self._restart_delay = 5  # seconds
        self.auto_restart_enabled = True
        
    def set_stream_config(self, rtmp_url: str, stream_key: str, video_list: List[str]):
        """Configure streaming parameters"""
        self.rtmp_url = rtmp_url
        self.stream_key = stream_key
        self.video_list = video_list
        self.current_video_index = 0
        
    def _validate_video_files(self) -> bool:
        """Validate that all video files exist"""
        for video_path in self.video_list:
            if not os.path.exists(video_path):
                return False
        return True
    
    def _build_ffmpeg_command(self, video_path: str) -> List[str]:
        """
        Build FFmpeg command with NVENC hardware acceleration
        Optimized for RTX 2060 streaming
        """
        full_rtmp_url = f"{self.rtmp_url}/{self.stream_key}"
        
        command = [
            "ffmpeg",
            "-re",  # Read input at native frame rate
            "-hwaccel", "cuda",  # Use CUDA hardware acceleration
            "-hwaccel_output_format", "cuda",  # Keep frames in GPU memory
            "-i", video_path,  # Input file
            
            # Video encoding settings (NVENC)
            "-c:v", "h264_nvenc",  # NVENC H.264 encoder
            "-preset", "p4",  # Preset (p1-p7, p4 is balanced)
            "-tune", "ll",  # Low latency tuning
            "-b:v", "4500k",  # Video bitrate (adjust as needed)
            "-maxrate", "5000k",  # Maximum bitrate
            "-bufsize", "9000k",  # Buffer size
            "-g", "60",  # Keyframe interval (2 seconds at 30fps)
            "-profile:v", "high",  # H.264 profile
            
            # Audio encoding
            "-c:a", "aac",  # AAC audio codec
            "-b:a", "160k",  # Audio bitrate
            "-ar", "44100",  # Audio sample rate
            
            # Output format
            "-f", "flv",  # FLV format for RTMP
            full_rtmp_url,  # Output RTMP URL
            
            # Additional flags
            "-loglevel", "info",  # Log level for monitoring
            "-progress", "pipe:1",  # Progress to stdout
        ]
        
        return command
    
    async def start_stream(self) -> Dict[str, any]:
        """Start FFmpeg streaming process"""
        if self.is_streaming:
            return {
                "success": False,
                "message": "Stream is already running"
            }
        
        if not self.video_list:
            return {
                "success": False,
                "message": "No videos in the list"
            }
        
        if not self._validate_video_files():
            return {
                "success": False,
                "message": "One or more video files not found"
            }
        
        try:
            # Start with the first video
            video_path = self.video_list[self.current_video_index]
            self.current_video = os.path.basename(video_path)
            
            command = self._build_ffmpeg_command(video_path)
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            self.is_streaming = True
            
            # Start monitoring task
            self._monitor_task = asyncio.create_task(self._monitor_ffmpeg())
            
            return {
                "success": True,
                "message": f"Stream started successfully",
                "video": self.current_video,
                "pid": self.process.pid
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start stream: {str(e)}"
            }
    
    async def stop_stream(self) -> Dict[str, any]:
        """Stop FFmpeg streaming process"""
        if not self.is_streaming:
            return {
                "success": False,
                "message": "No stream is running"
            }
        
        try:
            # Cancel monitor task
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Terminate FFmpeg process
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            
            self.is_streaming = False
            self.current_video = ""
            self.current_bitrate = "0 kb/s"
            self.process = None
            
            return {
                "success": True,
                "message": "Stream stopped successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to stop stream: {str(e)}"
            }
    
    async def _monitor_ffmpeg(self):
        """Monitor FFmpeg output for bitrate and errors"""
        try:
            if not self.process or not self.process.stderr:
                return
            
            # Read stderr in a non-blocking way
            while self.is_streaming and self.process:
                # Check if process is still running
                if self.process.poll() is not None:
                    exit_code = self.process.poll()
                    
                    # Check if it was an error or normal completion
                    if exit_code != 0 and self.auto_restart_enabled:
                        print(f"⚠️ FFmpeg process ended with code {exit_code}, attempting restart...")
                        await self._handle_stream_failure()
                    else:
                        # Normal video completion, start next video
                        await self._start_next_video()
                    break
                
                # Read FFmpeg output line
                try:
                    line = self.process.stderr.readline()
                    if line:
                        # Extract bitrate from FFmpeg output
                        bitrate_match = re.search(r'bitrate=\s*(\d+\.?\d*\s*\w+bits/s)', line)
                        if bitrate_match:
                            self.current_bitrate = bitrate_match.group(1)
                            self._restart_count = 0  # Reset restart count on successful streaming
                except:
                    pass
                
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"Error monitoring FFmpeg: {str(e)}")
            if self.auto_restart_enabled:
                await self._handle_stream_failure()
    
    async def _handle_stream_failure(self):
        """Handle FFmpeg failure with retry logic"""
        if self._restart_count >= self._max_restart_attempts:
            print(f"❌ Max restart attempts ({self._max_restart_attempts}) reached. Stopping auto-restart.")
            self.is_streaming = False
            return
        
        self._restart_count += 1
        print(f"🔄 Restart attempt {self._restart_count}/{self._max_restart_attempts}")
        
        # Wait before restarting
        await asyncio.sleep(self._restart_delay)
        
        # Try to restart the stream
        try:
            video_path = self.video_list[self.current_video_index]
            self.current_video = os.path.basename(video_path)
            
            command = self._build_ffmpeg_command(video_path)
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Continue monitoring
            self._monitor_task = asyncio.create_task(self._monitor_ffmpeg())
            print(f"✅ Stream restarted successfully")
            
        except Exception as e:
            print(f"❌ Error restarting stream: {str(e)}")
            await self._handle_stream_failure()  # Retry again
    
    async def _start_next_video(self):
        """Start streaming the next video in the list"""
        if not self.video_list:
            self.is_streaming = False
            return
        
        # Move to next video (loop back to start if at end)
        self.current_video_index = (self.current_video_index + 1) % len(self.video_list)
        video_path = self.video_list[self.current_video_index]
        self.current_video = os.path.basename(video_path)
        
        try:
            command = self._build_ffmpeg_command(video_path)
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Continue monitoring
            self._monitor_task = asyncio.create_task(self._monitor_ffmpeg())
            
        except Exception as e:
            print(f"Error starting next video: {str(e)}")
            self.is_streaming = False
    
    def get_status(self) -> Dict[str, any]:
        """Get current streaming status"""
        return {
            "is_streaming": self.is_streaming,
            "current_video": self.current_video,
            "bitrate": self.current_bitrate,
            "video_count": len(self.video_list),
            "current_index": self.current_video_index,
            "pid": self.process.pid if self.process else None
        }

# Global FFmpeg manager instance
ffmpeg_manager = FFmpegManager()


