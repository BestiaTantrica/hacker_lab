#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server_produccion.py
─────────────────────────────────────────────────────────────────────────────
Servidor de Renderizado y Ensamble Final para el Motor Bi-Wheel.
Recibe la captura WebM 1080p transmitida desde el navegador Canvas,
la ensambla con el audio completo de Tomás usando FFmpeg y exporta
el video definitivo en formato MP4 Broadcast (H.264 / AAC).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8088
BASE_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar/visor_cinematico")
OUTPUT_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/capitulo_1_produccion")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_FILE = BASE_DIR / "audio_capitulo1.mp3"
FINAL_VIDEO_MP4 = OUTPUT_DIR / "capitulo_1_vectorial_tomas.mp4"

render_completed_event = threading.Event()


class RenderHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_POST(self):
        if self.path == '/api/save_render':
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"\n[SERVER] Recibiendo captura de video WebM ({content_length / (1024*1024):.2f} MB)...")
            video_data = self.rfile.read(content_length)

            temp_webm = BASE_DIR / "temp_capture.webm"
            with open(temp_webm, "wb") as f:
                f.write(video_data)
            print(f"[SERVER] Archivo temporal guardado en: {temp_webm}")

            # Ensamble con FFmpeg
            print(f"[SERVER] Ensamblando video con audio oficial en: {FINAL_VIDEO_MP4}...")
            cmd = [
                "ffmpeg", "-y",
                "-i", str(temp_webm),
                "-i", str(AUDIO_FILE),
                "-vf", "scale=1920:1080",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(FINAL_VIDEO_MP4)
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                file_size_mb = FINAL_VIDEO_MP4.stat().st_size / (1024 * 1024)
                print(f"[SERVER] ✅ VIDEO GENERADO CON ÉXITO: {FINAL_VIDEO_MP4} ({file_size_mb:.2f} MB)")

                response = {
                    "status": "ok",
                    "output_file": str(FINAL_VIDEO_MP4),
                    "size_mb": round(file_size_mb, 2)
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))

                render_completed_event.set()

            except subprocess.CalledProcessError as err:
                print(f"[SERVER] ❌ Error en FFmpeg: {err.stderr.decode() if err.stderr else err}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(err)}).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    server = HTTPServer(('0.0.0.0', PORT), RenderHandler)
    print(f"[SERVER] Servidor Bi-Wheel activo en http://localhost:{PORT}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Servidor de Producción de Video Bi-Wheel")
    parser.add_argument("--auto-render", action="store_true", help="Lanza Chrome headless y graba automáticamente el video")
    args = parser.parse_args()

    # Si ya hay un servidor en el puerto 8088, matarlo para usar este handler enriquecido
    subprocess.run(["fuser", "-k", f"{PORT}/tcp"], capture_output=True)
    time.sleep(0.5)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.0)

    if args.auto_render:
        print("\n🚀 [AUTO-RENDER] Lanzando Google Chrome Headless en 1920x1080...")
        url = f"http://localhost:{PORT}/index.html?autorecord=1"
        chrome_cmd = [
            "/usr/bin/google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--autoplay-policy=no-user-gesture-required",
            url
        ]
        chrome_proc = subprocess.Popen(chrome_cmd)

        print("[AUTO-RENDER] Grabando coreografía (aprox. 122 segundos)...")
        # Esperar a que el evento de renderizado se complete (máx 150 segundos)
        completed = render_completed_event.wait(timeout=160)
        chrome_proc.terminate()

        if completed:
            print("\n🎉 [AUTO-RENDER] ¡PROCESO DE RENDERIZADO COMPLETADO!")
            print(f"🎬 Video Final: {FINAL_VIDEO_MP4}")
            sys.exit(0)
        else:
            print("\n❌ [AUTO-RENDER] Tiempo de espera agotado.")
            sys.exit(1)
    else:
        print("\nVisor listo. Puedes abrir http://localhost:8088 en tu navegador y hacer clic en 'Renderizar Video (MP4)'.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == '__main__':
    main()
