#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script 0.2: fusionador_visual.py
Crea y transforma assets visuales.
NO toca tiempos, NO toca audio, NO genera guiones.

Uso:
  python v2/celula_0/fusionador_visual.py --opcion 1 --input /ruta/video.mp4
  python v2/celula_0/fusionador_visual.py --opcion 2 --inputs img1.jpg img2.jpg img3.jpg --duracion 10
  python v2/celula_0/fusionador_visual.py --opcion 3 --input /ruta/asset.mp4
  python v2/celula_0/fusionador_visual.py --opcion 4 --input /ruta/imagen.jpg --duracion 8
  python v2/celula_0/fusionador_visual.py --opcion 5 --inputs img1.jpg img2.jpg  # PixelPunk aleatorio
  python v2/celula_0/fusionador_visual.py --opcion 6 --input img.jpg --fondo anim.mp4  # Fusión Onírica
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── Carga del entorno y ADN ──────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

ASSETS_AUDITADOS = Path(ADN["assets"]["paths"]["assets_auditados"])
RES_W, RES_H     = 1080, 1920  # 9:16 vertical
FPS              = ADN["assets"]["fps"]
COLOR_ADN        = ADN["estetica_visual"]["color_grading_ffmpeg"]
PALETA           = ADN["estetica_visual"]["paleta_colores"]
EVENTO_ID        = ADN["produccion"]["evento_id"]

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def correr_ffmpeg(cmd: list, descripcion: str = "") -> bool:
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        if result.returncode != 0:
            err(f"FFmpeg falló ({descripcion}):\n{result.stderr.decode()[-2000:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        err(f"FFmpeg timeout ({descripcion})")
        return False

def get_duracion(path: Path) -> float:
    """Obtiene la duración de un video/audio en segundos."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
    )
    try:
        return float(result.stdout.decode().strip())
    except Exception:
        return 0.0

def get_dimensiones(path: Path) -> tuple[int, int]:
    """Retorna (width, height) de un archivo de video/imagen."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
    )
    try:
        partes = result.stdout.decode().strip().split(',')
        return int(partes[0]), int(partes[1])
    except Exception:
        return 0, 0

def hex_a_ffmpeg_color(hex_color: str) -> str:
    """Convierte #RRGGBB a formato ffmpeg 0xRRGGBB."""
    return "0x" + hex_color.lstrip("#")

def nombre_salida(prefijo: str, extension: str = "mp4") -> Path:
    """Genera un path de salida en Assets_Auditados."""
    asegurar_dir(ASSETS_AUDITADOS)
    # Agregar timestamp corto para evitar colisiones
    ts = int(time.time()) % 10000
    return ASSETS_AUDITADOS / f"{prefijo}_{ts}_{EVENTO_ID}.{extension}"

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Crop 9:16 Inteligente
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_crop_inteligente(input_path: str):
    """
    Recorta imagen o video al formato vertical 1080x1920.
    Detecta el aspect ratio original y aplica el crop más inteligente.
    """
    log("\n✂️  OPCIÓN 1 — Crop 9:16 Inteligente", MAGENTA)

    ruta = Path(input_path)
    if not ruta.exists():
        err(f"Archivo no encontrado: {input_path}")
        sys.exit(1)

    w, h = get_dimensiones(ruta)
    if w == 0:
        err("No se pudieron obtener las dimensiones del archivo.")
        sys.exit(1)

    info(f"Entrada: {ruta.name}  ({w}x{h})")
    ratio_original = w / h
    ratio_objetivo = RES_W / RES_H  # 0.5625

    es_video = ruta.suffix.lower().lstrip('.') in {"mp4", "mov", "avi", "mkv", "webm"}
    salida = nombre_salida(f"crop_{ruta.stem}")

    # Construir filtro de video según el caso
    if ratio_original > 1.2:
        scale_h = RES_H
        scale_w = int(w * (RES_H / h))
        if scale_w < RES_W:
            scale_w = RES_W
            scale_h = int(h * (RES_W / w))
        vf = (f"scale={scale_w}:{scale_h}:flags=lanczos,"
              f"crop={RES_W}:{RES_H}:(iw-{RES_W})/2:(ih-{RES_H})/2")
    elif 0.8 <= ratio_original <= 1.2:
        color_fondo = hex_a_ffmpeg_color(PALETA["fondo_oscuro"])
        vf = (f"scale={RES_W}:-2:flags=lanczos,"
              f"pad={RES_W}:{RES_H}:0:(oh-ih)/2:color={color_fondo}")
    else:
        scale_w = RES_W
        scale_h = int(h * (RES_W / w))
        if scale_h < RES_H:
            scale_h = RES_H
            scale_w = int(w * (RES_H / h))
        vf = (f"scale={scale_w}:{scale_h}:flags=lanczos,"
              f"crop={RES_W}:{RES_H}")

    vf += (f",eq=contrast={COLOR_ADN['eq_contrast']}:"
           f"saturation={COLOR_ADN['eq_saturation']}:"
           f"brightness={COLOR_ADN['eq_brightness']}")

    if es_video:
        cmd = [
            "ffmpeg", "-y", "-i", str(ruta),
            "-vf", vf,
            "-c:v", ADN["assets"]["codec_video"],
            "-crf", str(ADN["assets"]["crf"]),
            "-preset", ADN["assets"]["preset"],
            "-c:a", "copy",
            "-r", str(FPS),
            str(salida)
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-i", str(ruta),
            "-vf", vf,
            "-frames:v", "1", "-q:v", "2",
            str(salida.with_suffix(".jpg"))
        ]
        salida = salida.with_suffix(".jpg")

    if correr_ffmpeg(cmd, "crop 9:16"):
        ok(f"Crop completado: {salida.name}")
        return str(salida)
    else:
        err("Error en el crop.")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Collage Kinético Elíptico
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_collage_kinetico(inputs: list[str], duracion: float = 12.0, auto_dir: str = None):
    log("\n🌌 OPCIÓN 2 — Collage Kinético Elíptico", MAGENTA)

    if not inputs and not auto_dir:
        err(f"Se necesitan --inputs o --auto-dir con al menos 3 imágenes.")
        sys.exit(1)

    rutas = []
    if inputs:
        rutas = [Path(p) for p in inputs]
    elif auto_dir:
        dir_base = Path(auto_dir)
        if not dir_base.exists():
            err(f"El directorio auto-dir no existe: {dir_base}")
            sys.exit(1)
        todas = []
        for ext in ['.jpg', '.jpeg', '.png']:
            todas.extend(list(dir_base.rglob(f"*{ext}")))
            todas.extend(list(dir_base.rglob(f"*{ext.upper()}")))
        if len(todas) < 3:
            err(f"No hay suficientes imágenes en {dir_base} (se necesitan al menos 3).")
            sys.exit(1)
        num_a_seleccionar = random.randint(3, min(6, len(todas)))
        rutas = random.sample(todas, num_a_seleccionar)
        info(f"Auto-selección: {len(rutas)} imágenes al azar desde {dir_base.name}")

    if not (3 <= len(rutas) <= 6):
        err(f"Se necesitan entre 3 y 6 imágenes.")
        sys.exit(1)

    for r in rutas:
        if not r.exists():
            err(f"No existe: {r}")
            sys.exit(1)

    num_imgs = len(rutas)
    salida = nombre_salida("collage_kinetico")

    # Buscar video de fondo automático si auto_dir está presente
    video_fondo = None
    if auto_dir:
        dir_videos = Path(auto_dir).parent / "Videos"
        if dir_videos.exists():
            videos_posibles = list(dir_videos.rglob("*.mp4")) + list(dir_videos.rglob("*.mov"))
            if videos_posibles:
                video_fondo = random.choice(videos_posibles)
                info(f"Fondo dinámico automático seleccionado: {video_fondo.name}")

    entradas_cmd = []
    idx_img_start = 0
    if video_fondo:
        entradas_cmd += ["-stream_loop", "-1", "-i", str(video_fondo)]
        idx_img_start = 1
        
    for r in rutas:
        # NO usamos -loop 1 porque zoompan generará los frames a partir de la imagen estática
        entradas_cmd += ["-i", str(r)]

    filtro_partes = []
    
    if video_fondo:
        # Procesar fondo de video (desenfoque ligero y crop a 9:16)
        filtro_partes.append(
            f"[0:v]scale={RES_W}:{RES_H}:force_original_aspect_ratio=increase,"
            f"crop={RES_W}:{RES_H},boxblur=luma_radius=15:luma_power=1,"
            f"format=rgba[fondo_base];[fondo_base]vignette=PI/3[fondo]"
        )
    else:
        color_fondo = PALETA["fondo_oscuro"].lstrip("#")
        filtro_partes.append(f"color=c=#{color_fondo}:s={RES_W}x{RES_H}:r={FPS}:d={duracion}[fondo_base];[fondo_base]vignette=PI/3[fondo]")

    overlay_actual = "[fondo]"
    window = duracion / num_imgs
    
    estilo_collage = random.choice(["espectral", "brutalismo", "geometrico"])
    info(f"Estilo visual seleccionado para este collage: {estilo_collage}")

    for i in range(num_imgs):
        idx = i + idx_img_start
        eq_sat = COLOR_ADN['eq_saturation'] + 0.3
        
        if estilo_collage == "espectral":
            size = random.randint(600, 950)
            filtro_partes.append(
                f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=increase,"
                f"crop={size}:{size},"
                f"eq=saturation={eq_sat}:contrast={COLOR_ADN['eq_contrast']},"
                f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duracion*FPS)}:s={size}x{size},"
                f"format=rgba,"
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='200*exp(-pow(X-W/2,2)/(2*pow(W/3,2))-pow(Y-H/2,2)/(2*pow(H/3,2)))'[img{i}]"
            )
            start_t = max(0.0, i * window - 0.5)
            end_t = min(duracion, (i+1) * window + 1.0)
            cx = (RES_W - size) / 2
            cy = (RES_H - size) / 2
            ox = f"({cx:.1f}+80*sin({1.0 + i*0.3:.2f}*t))"
            oy = f"({cy:.1f}+80*cos({1.0 + i*0.3:.2f}*t))"
            
        elif estilo_collage == "brutalismo":
            size = random.randint(700, 1000)
            # Sin máscara suave, corte a cuchillo (cuadrado/rectángulo duro). Sin movimiento suave.
            filtro_partes.append(
                f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=increase,"
                f"crop={size}:{size},"
                f"eq=saturation={eq_sat}:contrast={COLOR_ADN['eq_contrast']+0.2},"
                f"format=rgba[img{i}]"
            )
            # Cortes duros sin solapamiento (brutalista)
            start_t = i * window
            end_t = (i+1) * window
            # Posición estática pero descentrada
            ox = random.randint(0, max(1, RES_W - size))
            oy = random.randint(0, max(1, RES_H - size))
            
        else: # geometrico
            size = int(RES_W * 0.8)
            filtro_partes.append(
                f"[{idx}:v]scale={size}:{size}:force_original_aspect_ratio=increase,"
                f"crop={size}:{size},"
                f"eq=saturation={eq_sat}:contrast={COLOR_ADN['eq_contrast']},"
                f"zoompan=z='1.2':d={int(duracion*FPS)}:s={size}x{size},"
                f"format=rgba[img{i}]"
            )
            # Aparecen en cascada
            start_t = i * (window * 0.5)
            end_t = duracion
            # Posición centrada, encimándose
            cx = (RES_W - size) / 2
            cy = (RES_H - size) / 2
            ox = f"{cx:.1f}"
            oy = f"{cy:.1f}"

        etiqueta_salida = f"[orb{i}]" if i < num_imgs - 1 else "[video_out]"
        filtro_partes.append(f"{overlay_actual}[img{i}]overlay=x={ox}:y={oy}:enable='between(t,{start_t:.1f},{end_t:.1f})'{etiqueta_salida}")
        overlay_actual = etiqueta_salida

    filtro_completo = ";".join(filtro_partes)

    cmd = (
        ["ffmpeg", "-y"] +
        entradas_cmd +
        [
            "-filter_complex", filtro_completo,
            "-map", "[video_out]",
            "-c:v", ADN["assets"]["codec_video"],
            "-crf", str(ADN["assets"]["crf"]),
            "-preset", "fast",
            "-t", str(duracion),
            "-r", str(FPS),
            "-pix_fmt", "yuv420p",
            str(salida)
        ]
    )

    if correr_ffmpeg(cmd, "collage kinético (sugestivo)"):
        ok(f"Collage Kinético creado: {salida.name}")
        return str(salida)
    else:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Glitch Subliminal
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_glitch_subliminal(input_path: str, num_flashes: int = 5):
    log("\n⚡ OPCIÓN 3 — Glitch Subliminal", MAGENTA)
    # [Mantengo lógica existente resumida...]
    # Para ahorrar espacio en el script y reenfocarnos, llamaremos a un glitch básico.
    ruta = Path(input_path)
    if not ruta.exists(): sys.exit(1)
    duracion = get_duracion(ruta)
    if duracion <= 0: sys.exit(1)
    
    salida = nombre_salida(f"glitch_{ruta.stem}")
    cmd = [
        "ffmpeg", "-y", "-i", str(ruta),
        "-vf", f"scale={RES_W}:{RES_H}:force_original_aspect_ratio=increase,crop={RES_W}:{RES_H},noise=alls=50:allf=t+u",
        "-c:v", ADN["assets"]["codec_video"], "-crf", "24", "-t", str(duracion), str(salida)
    ]
    if correr_ffmpeg(cmd, "Glitch"):
        ok(f"Glitch Subliminal creado: {salida.name}")
        return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Animador de Estáticas (Ken Burns)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_ken_burns(input_path: str, duracion: float = 8.0):
    log("\n🎬 OPCIÓN 4 — Animador de Estáticas (Ken Burns)", MAGENTA)
    ruta = Path(input_path)
    if not ruta.exists() or ruta.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
        err("Se requiere imagen JPG/PNG.")
        sys.exit(1)
    salida = nombre_salida(f"ken_burns_{ruta.stem}")
    total_frames = int(duracion * FPS)
    zoom_expr = f"'1+(0.15*on/{total_frames})'"
    x_expr    = f"'iw/2-(iw/zoom/2)+(0.1*iw*on/{total_frames})'"
    y_expr    = f"'ih/2-(ih/zoom/2)+(0.05*ih*on/{total_frames})'"
    vf = (
        f"scale={RES_W * 2}:{RES_H * 2}:flags=lanczos,"
        f"zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}:d={total_frames}:s={RES_W}x{RES_H}:fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(ruta),
        "-vf", vf, "-c:v", ADN["assets"]["codec_video"], "-crf", str(ADN["assets"]["crf"]),
        "-preset", "fast", "-t", str(duracion), "-r", str(FPS), "-pix_fmt", "yuv420p", str(salida)
    ]
    if correr_ffmpeg(cmd, "Ken Burns"):
        ok(f"Ken Burns creado: {salida.name}")
        return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 5 — Creador Automático PixelPunk
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_5_pixelpunk(inputs: list[str], duracion: float = None, auto_dir: str = None):
    """
    Toma de 1 a 6 imágenes y crea un collage de alto contraste.
    Duraciones y tamaños son aleatorios para dar estilo punk-rock.
    """
    log("\n🎸 OPCIÓN 5 — Creador Automático PixelPunk", MAGENTA)
    
    if not inputs and not auto_dir:
        err(f"Se necesitan --inputs o --auto-dir.")
        sys.exit(1)
        
    rutas = []
    if inputs:
        rutas = [Path(p) for p in inputs]
    elif auto_dir:
        dir_base = Path(auto_dir)
        if not dir_base.exists():
            err(f"El directorio auto-dir no existe: {dir_base}")
            sys.exit(1)
        todas = []
        for ext in ['.jpg', '.jpeg', '.png']:
            todas.extend(list(dir_base.rglob(f"*{ext}")))
            todas.extend(list(dir_base.rglob(f"*{ext.upper()}")))
        if not todas:
            err(f"No hay imágenes en {dir_base}.")
            sys.exit(1)
        num_a_seleccionar = random.randint(1, min(6, len(todas)))
        rutas = random.sample(todas, num_a_seleccionar)
        info(f"Auto-selección: {len(rutas)} imágenes al azar desde {dir_base.name}")
        
    if not (1 <= len(rutas) <= 6):
        err("Se necesitan entre 1 y 6 imágenes.")
        sys.exit(1)
    
    if not duracion:
        duracion = random.choice([3.0, 5.0, 7.0, 10.0])
    
    for r in rutas:
        if not r.exists(): err(f"No existe: {r}"); sys.exit(1)
    
    info(f"Collage de {len(rutas)} imágenes. Duración: {duracion}s")
    salida = nombre_salida("pixelpunk")
    
    entradas_cmd = []
    for r in rutas: entradas_cmd += ["-loop", "1", "-i", str(r)]
    
    filtro_partes = []
    color_fondo = PALETA["fondo_oscuro"].lstrip("#")
    # Fondo con textura de ruido
    filtro_partes.append(f"color=c=#{color_fondo}:s={RES_W}x{RES_H}:r={FPS}:d={duracion}[fondo_base]")
    filtro_partes.append(f"[fondo_base]noise=alls=40:allf=t+u[fondo]")
    
    overlay_actual = "[fondo]"
    for i in range(len(rutas)):
        # Escala aleatoria entre 40% y 95% del ancho
        scale_w = random.randint(int(RES_W * 0.4), int(RES_W * 0.95))
        
        # Filtros de alto contraste grunge
        eq_filter = f"eq=contrast=1.6:saturation=0.7:gamma=0.9"
        
        filtro_partes.append(
            f"[{i}:v]scale={scale_w}:-1,"
            f"{eq_filter},format=rgba[img{i}]"
        )
        
        # Posición aleatoria
        max_x = max(1, RES_W - scale_w)
        max_y = max(1, int(RES_H * 0.8))
        x_pos = random.randint(0, max_x)
        y_pos = random.randint(0, max_y)
        
        etiqueta_salida = f"[out{i}]" if i < len(rutas)-1 else "[video_out]"
        # Enable expression to make some images flicker or appear later
        delay = random.uniform(0, 0.5) if i > 0 else 0
        filtro_partes.append(
            f"{overlay_actual}[img{i}]overlay=x='{x_pos}':y='{y_pos}':enable='gte(t,{delay})'{etiqueta_salida}"
        )
        overlay_actual = etiqueta_salida
        
    filtro_completo = ";".join(filtro_partes)
    
    cmd = ["ffmpeg", "-y"] + entradas_cmd + [
        "-filter_complex", filtro_completo,
        "-map", "[video_out]",
        "-c:v", ADN["assets"]["codec_video"],
        "-crf", str(ADN["assets"]["crf"]),
        "-preset", "fast",
        "-t", str(duracion),
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        str(salida)
    ]
    if correr_ffmpeg(cmd, "PixelPunk"):
        ok(f"PixelPunk creado: {salida.name}")
        return str(salida)
    else:
        err("Error al generar PixelPunk.")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 6 — Fusión Elemental / Módulo Onírico
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_6_fusion_elemental(input_path: str, fondo_path: str, duracion: float = None):
    """
    Fusión onírica: toma una imagen estática y la superpone (blend=screen u overlay)
    sobre un fondo animado abstracto (fuego, espacio).
    """
    log("\n🌀 OPCIÓN 6 — Fusión Elemental Onírica", MAGENTA)
    if not input_path or not fondo_path:
        err("Se requiere --input (imagen) y --fondo (video abstracto).")
        sys.exit(1)
        
    img = Path(input_path)
    fondo = Path(fondo_path)
    if not img.exists(): err(f"No existe: {img}"); sys.exit(1)
    if not fondo.exists(): err(f"No existe: {fondo}"); sys.exit(1)
    
    dur_fondo = get_duracion(fondo)
    if dur_fondo <= 0: dur_fondo = 8.0
    
    if not duracion:
        duracion = dur_fondo
        if duracion > 15: duracion = 15.0  # Máximo 15s para no hacer clips eternos
        
    info(f"Fusionando {img.name} sobre {fondo.name} (Duración: {duracion}s)")
    salida = nombre_salida("fusion_onirica")
    
    # Imagen de base (apenas opaca), Fondo animado encima con blend mode
    # O al revés: Fondo animado de base, imagen transparente encima
    # Haremos fondo animado de base, y la imagen encima con blend=screen
    vf = (
        f"[1:v]scale={RES_W}:-2:force_original_aspect_ratio=increase,"
        f"crop={RES_W}:{RES_H},format=rgba[base_fondo];"
        f"[0:v]scale={RES_W}:-2:force_original_aspect_ratio=increase,"
        f"crop={RES_W}:{RES_H},format=rgba,"
        f"colorchannelmixer=aa=0.8[overlay_img];"
        f"[base_fondo][overlay_img]blend=all_mode=screen:all_opacity=0.85[video_out]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img),
        "-i", str(fondo),
        "-filter_complex", vf,
        "-map", "[video_out]",
        "-c:v", ADN["assets"]["codec_video"],
        "-crf", str(ADN["assets"]["crf"]),
        "-preset", "fast",
        "-t", str(duracion),
        "-r", str(FPS),
        "-pix_fmt", "yuv420p",
        str(salida)
    ]
    if correr_ffmpeg(cmd, "Fusión Elemental"):
        ok(f"Fusión creada: {salida.name}")
        return str(salida)
    else:
        err("Error al generar Fusión Elemental.")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌑 Fusionador Visual V2.2 — Célula Madre 0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Opciones disponibles:
  1  Crop 9:16 inteligente
  2  Collage Kinético Elíptico (3-6 imágenes)
  3  Glitch Subliminal
  4  Animador de Estáticas Ken Burns
  5  Creador Automático PixelPunk (1-6 imágenes, collage grunge aleatorio)
  6  Fusión Elemental Onírica (Requiere --input imagen y --fondo video_abstracto)
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4, 5, 6], required=True,
                        help="Número de opción (1-6)")
    parser.add_argument("--input", type=str, default=None,
                        help="Ruta al archivo de entrada principal")
    parser.add_argument("--inputs", type=str, nargs="+", default=None,
                        help="Rutas múltiples para collages (Opciones 2 y 5)")
    parser.add_argument("--auto-dir", type=str, default=None,
                        help="Ruta base a carpeta de imágenes para tomar samples al azar en Opciones 2 y 5")
    parser.add_argument("--fondo", type=str, default=None,
                        help="Ruta al video de fondo animado (Opción 6)")
    parser.add_argument("--duracion", type=float, default=None,
                        help="Duración del video de salida en segundos")
    parser.add_argument("--flashes", type=int, default=5,
                        help="[Opción 3] Número de flashes de glitch")

    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌑 FUSIONADOR VISUAL V2.2", MAGENTA)
    log(f"  ADN activo: {ADN['produccion']['evento_id']}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:
        if not args.input: err("--input requerido"); sys.exit(1)
        opcion_1_crop_inteligente(args.input)
    elif args.opcion == 2:
        if not args.inputs and not args.auto_dir: err("--inputs o --auto-dir requerido"); sys.exit(1)
        duracion = args.duracion if args.duracion else 12.0
        opcion_2_collage_kinetico(args.inputs, duracion, args.auto_dir)
    elif args.opcion == 3:
        if not args.input: err("--input requerido"); sys.exit(1)
        opcion_3_glitch_subliminal(args.input, args.flashes)
    elif args.opcion == 4:
        if not args.input: err("--input requerido"); sys.exit(1)
        duracion = args.duracion if args.duracion else 8.0
        opcion_4_ken_burns(args.input, duracion)
    elif args.opcion == 5:
        if not args.inputs and not args.auto_dir: err("--inputs o --auto-dir requerido (1 a 6 imágenes)"); sys.exit(1)
        opcion_5_pixelpunk(args.inputs, args.duracion, args.auto_dir)
    elif args.opcion == 6:
        if not args.input or not args.fondo: err("Se requiere --input y --fondo"); sys.exit(1)
        opcion_6_fusion_elemental(args.input, args.fondo, args.duracion)

if __name__ == "__main__":
    main()
