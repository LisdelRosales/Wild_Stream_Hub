"""
Stream Lists Manager for Wild_Stream_Hub
Handles creation, management, and video organization for stream lists
"""
import os
import shutil
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import aiofiles

class StreamListManager:
    """Manages stream lists (folders) and their videos"""
    
    def __init__(self, base_path: str = "/mnt/main-storage/stream-lists"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _get_list_path(self, list_name: str) -> Path:
        """Get full path for a stream list"""
        return self.base_path / list_name
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize list name for filesystem"""
        import re
        # Remove invalid characters
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        return name.lower()
    
    async def create_list(self, list_name: str) -> Dict[str, any]:
        """Create a new stream list (folder)"""
        try:
            sanitized_name = self._sanitize_name(list_name)
            list_path = self._get_list_path(sanitized_name)
            
            if list_path.exists():
                return {
                    "success": False,
                    "message": f"Stream list '{sanitized_name}' already exists"
                }
            
            list_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "message": f"Stream list '{sanitized_name}' created successfully",
                "list_name": sanitized_name,
                "path": str(list_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create stream list: {str(e)}"
            }
    
    async def get_all_lists(self) -> List[Dict[str, any]]:
        """Get all stream lists with their info"""
        try:
            lists = []
            
            if not self.base_path.exists():
                return lists
            
            for item in self.base_path.iterdir():
                if item.is_dir():
                    # Count videos in the list
                    video_count = len([f for f in item.iterdir() if f.is_file() and f.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.flv']])
                    
                    # Calculate total size
                    total_size = sum(f.stat().st_size for f in item.iterdir() if f.is_file())
                    
                    lists.append({
                        "name": item.name,
                        "path": str(item),
                        "video_count": video_count,
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
            
            return sorted(lists, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            print(f"Error getting stream lists: {str(e)}")
            return []
    
    async def delete_list(self, list_name: str) -> Dict[str, any]:
        """Delete a stream list and all its contents"""
        try:
            list_path = self._get_list_path(list_name)
            
            if not list_path.exists():
                return {
                    "success": False,
                    "message": f"Stream list '{list_name}' not found"
                }
            
            shutil.rmtree(list_path)
            
            return {
                "success": True,
                "message": f"Stream list '{list_name}' deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete stream list: {str(e)}"
            }
    
    async def get_list_videos(self, list_name: str) -> List[Dict[str, any]]:
        """Get all videos in a specific stream list"""
        try:
            list_path = self._get_list_path(list_name)
            
            if not list_path.exists():
                return []
            
            videos = []
            video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v']
            
            for file_path in list_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                    stat = file_path.stat()
                    
                    videos.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": file_path.suffix.lower()
                    })
            
            return sorted(videos, key=lambda x: x['filename'])
            
        except Exception as e:
            print(f"Error getting videos for list '{list_name}': {str(e)}")
            return []
    
    async def delete_video(self, list_name: str, filename: str) -> Dict[str, any]:
        """Delete a video from a stream list"""
        try:
            list_path = self._get_list_path(list_name)
            video_path = list_path / filename
            
            if not video_path.exists():
                return {
                    "success": False,
                    "message": f"Video '{filename}' not found in list '{list_name}'"
                }
            
            video_path.unlink()
            
            return {
                "success": True,
                "message": f"Video '{filename}' deleted from list '{list_name}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete video: {str(e)}"
            }
    
    async def get_video_paths(self, list_name: str) -> List[str]:
        """Get all video file paths in a stream list for FFmpeg"""
        try:
            list_path = self._get_list_path(list_name)
            
            if not list_path.exists():
                return []
            
            video_paths = []
            video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v']
            
            for file_path in list_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                    video_paths.append(str(file_path))
            
            return sorted(video_paths)
            
        except Exception as e:
            print(f"Error getting video paths for list '{list_name}': {str(e)}")
            return []

# Global stream list manager instance
stream_list_manager = StreamListManager()
