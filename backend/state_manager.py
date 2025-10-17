"""
State Manager for Wild_Stream_Hub
Handles persistence and restoration of streaming state
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

class StateManager:
    """Manages persistent state for stream restoration"""
    
    def __init__(self, state_file: str = "/mnt/main-storage/wild_stream_hub/stream_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
    def save_stream_state(self, rtmp_url: str, stream_key: str, stream_list_name: str):
        """Save current stream configuration"""
        try:
            state = {
                "active": True,
                "rtmp_url": rtmp_url,
                "stream_key": stream_key,
                "stream_list_name": stream_list_name,
                "timestamp": datetime.utcnow().isoformat(),
                "auto_restart": True
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving state: {str(e)}")
            return False
    
    def clear_stream_state(self):
        """Clear stream state (when manually stopped)"""
        try:
            state = {
                "active": False,
                "rtmp_url": None,
                "stream_key": None,
                "stream_list_name": None,
                "timestamp": datetime.utcnow().isoformat(),
                "auto_restart": False
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error clearing state: {str(e)}")
            return False
    
    def get_stream_state(self) -> Optional[Dict]:
        """Get saved stream state"""
        try:
            if not self.state_file.exists():
                return None
                
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            return state if state.get("active") else None
        except Exception as e:
            print(f"Error loading state: {str(e)}")
            return None
    
    def should_auto_restart(self) -> bool:
        """Check if stream should auto-restart"""
        state = self.get_stream_state()
        return state is not None and state.get("auto_restart", False)

# Global state manager instance
state_manager = StateManager()

