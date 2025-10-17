"""
Wild_Stream_Hub - Main FastAPI Application
Web-based control panel for managing RTMP livestreams via FFmpeg
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from datetime import timedelta
import aiofiles
import os

# Import our modules
from auth import (
    authenticate_user, 
    create_access_token, 
    decode_access_token, 
    Token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from monitor import monitor
from ffmpeg_manager import ffmpeg_manager
from stream_lists import stream_list_manager
from state_manager import state_manager

# Initialize FastAPI app
app = FastAPI(
    title="Wild_Stream_Hub",
    description="Web-based control panel for managing RTMP livestreams via FFmpeg",
    version="1.0.0"
)

# CORS middleware for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Request/Response Models
class StreamStartRequest(BaseModel):
    rtmp_url: str
    stream_key: str
    stream_list_name: str

class StreamListCreateRequest(BaseModel):
    list_name: str

class StreamResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# Dependency for protected routes
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return current user"""
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# Authentication Endpoints
@app.post("/login", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token
    Default credentials: username=admin, password=admin123
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Stream Management Endpoints
@app.post("/stream/start", response_model=StreamResponse, tags=["Stream"])
async def start_stream(
    request: StreamStartRequest,
    current_user = Depends(get_current_user)
):
    """
    Start FFmpeg streaming process using a stream list
    Requires authentication
    """
    # Get video paths from the stream list
    video_paths = await stream_list_manager.get_video_paths(request.stream_list_name)
    
    if not video_paths:
        return StreamResponse(
            success=False,
            message=f"No videos found in stream list '{request.stream_list_name}'"
        )
    
    # Configure stream parameters
    ffmpeg_manager.set_stream_config(
        rtmp_url=request.rtmp_url,
        stream_key=request.stream_key,
        video_list=video_paths
    )
    
    # Start the stream
    result = await ffmpeg_manager.start_stream()
    
    # Start monitoring timer if successful
    if result["success"]:
        monitor.start_stream_timer()
        # Save state for auto-recovery
        state_manager.save_stream_state(
            rtmp_url=request.rtmp_url,
            stream_key=request.stream_key,
            stream_list_name=request.stream_list_name
        )
    
    return StreamResponse(
        success=result["success"],
        message=result["message"],
        data=result if result["success"] else None
    )

@app.post("/stream/stop", response_model=StreamResponse, tags=["Stream"])
async def stop_stream(current_user = Depends(get_current_user)):
    """
    Stop FFmpeg streaming process
    Requires authentication
    """
    result = await ffmpeg_manager.stop_stream()
    
    # Stop monitoring timer
    if result["success"]:
        monitor.stop_stream_timer()
        # Clear state (manually stopped, don't auto-restart)
        state_manager.clear_stream_state()
    
    return StreamResponse(
        success=result["success"],
        message=result["message"]
    )

@app.get("/stream/status", tags=["Stream"])
async def get_stream_status(current_user = Depends(get_current_user)):
    """
    Get current stream status
    Returns stream info, bitrate, uptime, and system load
    Requires authentication
    """
    ffmpeg_status = ffmpeg_manager.get_status()
    
    full_status = monitor.get_full_status(
        ffmpeg_pid=ffmpeg_status.get("pid"),
        bitrate=ffmpeg_status.get("bitrate", "0 kb/s"),
        current_video=ffmpeg_status.get("current_video", "")
    )
    
    return {
        "success": True,
        "data": full_status
    }

# WebSocket endpoint for real-time monitoring
class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for connection in self.active_connections[:]:  # Create a copy to iterate
            try:
                await connection.send_json(message)
            except:
                # Remove disconnected clients
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """
    WebSocket endpoint for real-time monitoring
    Sends status updates every 1 second
    
    Note: In production, you should validate the JWT token here as well
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Get current status
            ffmpeg_status = ffmpeg_manager.get_status()
            full_status = monitor.get_full_status(
                ffmpeg_pid=ffmpeg_status.get("pid"),
                bitrate=ffmpeg_status.get("bitrate", "0 kb/s"),
                current_video=ffmpeg_status.get("current_video", "")
            )
            
            # Send to this client
            await websocket.send_json(full_status)
            
            # Wait 1 second before next update
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# Stream Lists Management Endpoints
@app.post("/stream-lists", response_model=StreamResponse, tags=["Stream Lists"])
async def create_stream_list(
    request: StreamListCreateRequest,
    current_user = Depends(get_current_user)
):
    """Create a new stream list (folder)"""
    result = await stream_list_manager.create_list(request.list_name)
    return StreamResponse(
        success=result["success"],
        message=result["message"],
        data=result if result["success"] else None
    )

@app.get("/stream-lists", tags=["Stream Lists"])
async def get_stream_lists(current_user = Depends(get_current_user)):
    """Get all stream lists"""
    lists = await stream_list_manager.get_all_lists()
    return {
        "success": True,
        "data": lists
    }

@app.get("/stream-lists/{list_name}/videos", tags=["Stream Lists"])
async def get_list_videos(
    list_name: str,
    current_user = Depends(get_current_user)
):
    """Get all videos in a specific stream list"""
    videos = await stream_list_manager.get_list_videos(list_name)
    return {
        "success": True,
        "data": videos
    }

@app.delete("/stream-lists/{list_name}", response_model=StreamResponse, tags=["Stream Lists"])
async def delete_stream_list(
    list_name: str,
    current_user = Depends(get_current_user)
):
    """Delete a stream list and all its contents"""
    result = await stream_list_manager.delete_list(list_name)
    return StreamResponse(
        success=result["success"],
        message=result["message"]
    )

@app.delete("/stream-lists/{list_name}/videos/{filename}", response_model=StreamResponse, tags=["Stream Lists"])
async def delete_video(
    list_name: str,
    filename: str,
    current_user = Depends(get_current_user)
):
    """Delete a video from a stream list"""
    result = await stream_list_manager.delete_video(list_name, filename)
    return StreamResponse(
        success=result["success"],
        message=result["message"]
    )

@app.post("/stream-lists/{list_name}/upload", response_model=StreamResponse, tags=["Stream Lists"])
async def upload_video(
    list_name: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload a video file to a stream list"""
    try:
        # Validate file extension
        allowed_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            return StreamResponse(
                success=False,
                message=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Get list path
        list_path = stream_list_manager._get_list_path(list_name)
        
        if not list_path.exists():
            return StreamResponse(
                success=False,
                message=f"Stream list '{list_name}' not found"
            )
        
        # Save file
        file_path = list_path / file.filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
                await f.write(chunk)
        
        return StreamResponse(
            success=True,
            message=f"Video '{file.filename}' uploaded successfully to '{list_name}'",
            data={
                "filename": file.filename,
                "size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
                "list_name": list_name
            }
        )
        
    except Exception as e:
        return StreamResponse(
            success=False,
            message=f"Failed to upload video: {str(e)}"
        )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Wild_Stream_Hub",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Wild_Stream_Hub API",
        "docs": "/docs",
        "health": "/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Wild_Stream_Hub API starting...")
    print("📡 WebSocket monitoring available at /ws/monitor")
    print("📚 API documentation available at /docs")
    print("🔐 Default credentials: admin / admin123")
    
    # Check if there's a stream to auto-restore
    saved_state = state_manager.get_stream_state()
    if saved_state and state_manager.should_auto_restart():
        print("🔄 Detected previous stream state, attempting to restore...")
        try:
            # Get video paths from the stream list
            video_paths = await stream_list_manager.get_video_paths(saved_state["stream_list_name"])
            
            if video_paths:
                # Configure stream
                ffmpeg_manager.set_stream_config(
                    rtmp_url=saved_state["rtmp_url"],
                    stream_key=saved_state["stream_key"],
                    video_list=video_paths
                )
                
                # Start the stream
                result = await ffmpeg_manager.start_stream()
                
                if result["success"]:
                    monitor.start_stream_timer()
                    print(f"✅ Stream auto-restored: {saved_state['stream_list_name']}")
                else:
                    print(f"❌ Failed to restore stream: {result['message']}")
            else:
                print(f"⚠️ No videos found in stream list: {saved_state['stream_list_name']}")
        except Exception as e:
            print(f"❌ Error restoring stream: {str(e)}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Wild_Stream_Hub...")
    
    # Stop any running streams
    if ffmpeg_manager.is_streaming:
        await ffmpeg_manager.stop_stream()
        monitor.stop_stream_timer()
    
    print("✅ Shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

