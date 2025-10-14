<p align="center">
	<img src="https://img.shields.io/badge/FastAPI-async%20Python-green" />
	<img src="https://img.shields.io/badge/License-MIT-blue.svg" />
	<img src="https://img.shields.io/badge/Status-Alpha-orange" />
</p>

# Wild_Stream_Hub

> Plataforma web para gestionar canales de streaming, subir videos y lanzar streams a plataformas RTMP usando FFmpeg.

## 🚀 Características principales
- Crear canales/listas de reproducción
- Subir videos a cada canal
- Configurar URL RTMP y clave de stream
- Lanzar y detener streams con FFmpeg
- Ver estado en tiempo real

## 📦 Estructura del proyecto

```
Wild_Stream_Hub/
│
├── app/
│   ├── main.py              # backend FastAPI
│   ├── ffmpeg_manager.py    # control de procesos FFmpeg
│   └── utils.py             # helpers
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── config/
│   └── config.json
│
├── uploads/                 # carpeta temporal para subir
├── streams/                 # carpetas por canal/lista
├── logs/
│
├── requirements.txt
└── README.md
```

## 🛠️ Stack
- **API:** FastAPI
- **Frontend:** Bootstrap + Vanilla JS
- **Streaming:** FFmpeg (NVENC)
- **DB:** JSON (simple)
- **Sistema:** Debian + Python 3.8+

## ⚡ Instalación rápida

```bash
sudo apt install -y ffmpeg python3 python3-venv python3-pip
git clone https://github.com/LisdelRosales/Wild_Stream_Hub.git
cd Wild_Stream_Hub
pip install -r requirements.txt
```

## ▶️ Uso
1. Ejecuta el backend:
	 ```bash
	 uvicorn app.main:app --reload
	 ```
2. Abre el navegador en [http://localhost:8000](http://localhost:8000)

## 📑 Endpoints principales

| Método | Endpoint         | Descripción                        |
|--------|------------------|------------------------------------|
| GET    | `/`              | Bienvenida                         |
| POST   | `/create-list`   | Crear una nueva lista/canal        |
| POST   | `/start-stream`  | Lanzar stream (simulado)           |
| ...    | ...              | (Ver roadmap para más endpoints)   |

## 📋 Ejemplo de configuración (`config/config.json`)

```json
{
	"lists": [
		{
			"name": "TokyoChannel",
			"videos": ["video1.mp4", "video2.mp4"]
		}
	],
	"streams": {
		"TokyoChannel": {
			"rtmp_url": "rtmp://a.rtmp.youtube.com/live2",
			"stream_key": "xxxx-xxxx-xxxx",
			"status": "inactive"
		}
	},
	"settings": {
		"default_bitrate": "4000k"
	}
}
```

## 🤝 Contribuir
Lee [CONTRIBUTING.md](CONTRIBUTING.md) para saber cómo colaborar.

## 📄 Licencia
MIT
