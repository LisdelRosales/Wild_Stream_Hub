"""
System monitoring module for Wild_Stream_Hub
Collects CPU, GPU, RAM, and stream statistics
"""
import psutil
import time
from typing import Dict, Optional
from datetime import datetime

class SystemMonitor:
    """Monitor system resources and stream status"""
    
    def __init__(self):
        self.stream_start_time: Optional[float] = None
        self.stream_active = False
        
    def start_stream_timer(self):
        """Start tracking stream uptime"""
        self.stream_start_time = time.time()
        self.stream_active = True
        
    def stop_stream_timer(self):
        """Stop tracking stream uptime"""
        self.stream_start_time = None
        self.stream_active = False
        
    def get_stream_uptime(self) -> str:
        """Get formatted stream uptime"""
        if not self.stream_active or self.stream_start_time is None:
            return "00:00:00"
        
        elapsed = int(time.time() - self.stream_start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram_usage(self) -> Dict[str, float]:
        """Get RAM usage statistics"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent
        }
    
    def get_gpu_usage(self) -> Dict[str, any]:
        """
        Get GPU usage statistics
        Note: This is a basic implementation. For NVIDIA GPUs, 
        consider using nvidia-ml-py3 (pynvml) for more detailed stats.
        """
        try:
            # Try to get GPU info using nvidia-smi if available
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                values = result.stdout.strip().split(',')
                return {
                    "available": True,
                    "utilization": float(values[0].strip()),
                    "memory_used_mb": float(values[1].strip()),
                    "memory_total_mb": float(values[2].strip()),
                    "temperature": float(values[3].strip())
                }
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass
        
        # Fallback if nvidia-smi is not available
        return {
            "available": False,
            "utilization": 0.0,
            "memory_used_mb": 0.0,
            "memory_total_mb": 0.0,
            "temperature": 0.0
        }
    
    def get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage statistics"""
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
    
    def get_ffmpeg_stats(self, process_pid: Optional[int] = None) -> Dict[str, any]:
        """Get FFmpeg process statistics if running"""
        if process_pid is None:
            return {
                "running": False,
                "cpu_percent": 0.0,
                "memory_mb": 0.0
            }
        
        try:
            process = psutil.Process(process_pid)
            return {
                "running": True,
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": round(process.memory_info().rss / (1024**2), 2)
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                "running": False,
                "cpu_percent": 0.0,
                "memory_mb": 0.0
            }
    
    def get_full_status(self, ffmpeg_pid: Optional[int] = None, 
                       bitrate: str = "0 kb/s", 
                       current_video: str = "") -> Dict[str, any]:
        """Get complete system and stream status"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stream": {
                "active": self.stream_active,
                "uptime": self.get_stream_uptime(),
                "bitrate": bitrate,
                "current_video": current_video
            },
            "system": {
                "cpu": self.get_cpu_usage(),
                "ram": self.get_ram_usage(),
                "gpu": self.get_gpu_usage(),
                "disk": self.get_disk_usage()
            },
            "ffmpeg": self.get_ffmpeg_stats(ffmpeg_pid)
        }

# Global monitor instance
monitor = SystemMonitor()


