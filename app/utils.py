import json
import threading

# ...existing code...

_config_lock = threading.Lock()

def read_config():
	"""Lee el archivo config.json de forma segura."""
	with _config_lock:
		try:
			with open(PATHS["config"], "r") as f:
				return json.load(f)
		except Exception:
			return {}

def write_config(data):
	"""Escribe el archivo config.json de forma segura."""
	with _config_lock:
		with open(PATHS["config"], "w") as f:
			json.dump(data, f, indent=2)

"""
utils.py
---------
Funciones auxiliares y utilidades para el backend Wild_Stream_Hub.
Incluye configuración centralizada de rutas absolutas.
"""

import os

# Cambia este path según tu entorno Debian
BASE_PATH = os.environ.get("WILDSTREAM_BASE_PATH", "/mnt/main-storage/Wild_Stream_Hub")

PATHS = {
	"streams": os.path.join(BASE_PATH, "streams"),
	"uploads": os.path.join(BASE_PATH, "uploads"),
	"logs": os.path.join(BASE_PATH, "logs"),
	"config": os.path.join(BASE_PATH, "config", "config.json"),
	"static": os.path.join(BASE_PATH, "static"),
}

def ensure_dirs():
	"""Crea las carpetas necesarias si no existen."""
	for key, path in PATHS.items():
		if key != "config":
			os.makedirs(path, exist_ok=True)
