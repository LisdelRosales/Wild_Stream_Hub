
import os
import logging
from fastapi import FastAPI, Request, status, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.utils import PATHS, ensure_dirs, read_config, write_config
from app.ffmpeg_manager import FFmpegManager

API_TOKEN = os.environ.get("WILDSTREAM_API_TOKEN", "changeme123")

def verify_token(x_api_token: str = Header(...)):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI()
ensure_dirs()

logging.basicConfig(
    filename=os.path.join(PATHS["logs"], "wildstream.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

ffmpeg_manager = FFmpegManager()

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
def create_list(req: CreateListRequest, authorization: str = Header(None)):
    check_auth(authorization)
    if not req.list_name or not req.list_name.isalnum():
        return JSONResponse(status_code=400, content={"status": "error", "message": "Nombre de lista inválido. Usa solo letras y números."})
    list_dir = os.path.join(PATHS["streams"], req.list_name)
    if os.path.exists(list_dir):
        return JSONResponse(status_code=409, content={"status": "error", "message": f"La lista '{req.list_name}' ya existe."})
    try:
        os.makedirs(list_dir, exist_ok=False)
        # Persistir en config.json
        config = read_config()
        if "lists" not in config:
            config["lists"] = []
        config["lists"].append({"name": req.list_name, "videos": []})
        write_config(config)
        return {"status": "ok", "message": f"Lista '{req.list_name}' creada en {list_dir}."}
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": "error", "message": str(e)})


@app.post("/start-stream")
def start_stream(req: StartStreamRequest, authorization: str = Header(None)):
    check_auth(authorization)
    list_dir = os.path.join(PATHS["streams"], req.list_name)
    playlist_path = os.path.join(list_dir, 'playlist.txt')
    if not os.path.exists(list_dir):
        return JSONResponse(status_code=404, content={"status": "error", "message": f"La lista '{req.list_name}' no existe."})
    if not os.path.exists(playlist_path):
        return JSONResponse(status_code=404, content={"status": "error", "message": "No existe playlist.txt para esta lista."})
    # Validar que todos los archivos en playlist sean mp4
    try:
        with open(playlist_path, 'r') as f:
            for line in f:
                if line.strip().startswith("file "):
                    path = line.strip().split("'", 2)[1]
                    if not path.endswith('.mp4'):
                        return JSONResponse(status_code=400, content={"status": "error", "message": f"El archivo '{path}' no es mp4."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Error leyendo playlist: {e}"})
    ffmpeg_cmd = f"ffmpeg -re -stream_loop -1 -f concat -safe 0 -i {playlist_path} -c:v h264_nvenc -preset p4 -b:v {req.bitrate} -c:a aac -b:a 160k -f flv {req.rtmp_url}/{req.stream_key}"
    print(f"[DEBUG] Comando FFmpeg: {ffmpeg_cmd}")
    return {"status": "ok", "cmd": ffmpeg_cmd}
