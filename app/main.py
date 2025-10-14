from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

app = FastAPI()

BASE_STREAMS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'streams'))

class CreateListRequest(BaseModel):
    list_name: str

class StartStreamRequest(BaseModel):
    list_name: str
    rtmp_url: str
    stream_key: str
    bitrate: str = '4000k'

@app.get("/")
def root():
    return {"message": "Bienvenido a Wild_Stream_Hub API"}

@app.post("/create-list")
def create_list(req: CreateListRequest):
    list_dir = os.path.join(BASE_STREAMS_PATH, req.list_name)
    try:
        os.makedirs(list_dir, exist_ok=True)
        return {"status": "ok", "message": f"Lista '{req.list_name}' creada."}
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": "error", "message": str(e)})

@app.post("/start-stream")
def start_stream(req: StartStreamRequest):
    playlist_path = os.path.join(BASE_STREAMS_PATH, req.list_name, 'playlist.txt')
    ffmpeg_cmd = f"ffmpeg -re -stream_loop -1 -f concat -safe 0 -i {playlist_path} -c:v h264_nvenc -preset p4 -b:v {req.bitrate} -c:a aac -b:a 160k -f flv {req.rtmp_url}/{req.stream_key}"
    print(f"[DEBUG] Comando FFmpeg: {ffmpeg_cmd}")
    return {"status": "ok", "cmd": ffmpeg_cmd}
