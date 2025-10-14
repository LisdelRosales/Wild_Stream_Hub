
"""
ffmpeg_manager.py
------------------
Módulo para gestionar procesos FFmpeg como subprocesos, monitorear estado y reinicio automático.
"""


import subprocess
import threading

class FFmpegManager:
	"""Gestor de procesos FFmpeg para múltiples canales."""
	def __init__(self):
		self.processes = {}  # {list_name: subprocess.Popen}
		self.lock = threading.Lock()

	def start_stream(self, list_name, ffmpeg_cmd, log_path):
		with self.lock:
			if list_name in self.processes and self.processes[list_name].poll() is None:
				return False, "Stream ya activo para este canal."
			log_file = open(log_path, 'a')
			proc = subprocess.Popen(ffmpeg_cmd, shell=True, stdout=log_file, stderr=log_file)
			self.processes[list_name] = proc
			return True, f"Stream lanzado para {list_name} (PID {proc.pid})"

	def stop_stream(self, list_name):
		with self.lock:
			proc = self.processes.get(list_name)
			if proc and proc.poll() is None:
				proc.terminate()
				return True, f"Stream detenido para {list_name}"
			return False, "No hay stream activo para este canal."

	def status(self, list_name=None):
		with self.lock:
			if list_name:
				proc = self.processes.get(list_name)
				if proc:
					return proc.poll() is None
				return False
			# Estado de todos
			return {k: (p.poll() is None) for k, p in self.processes.items()}
