#!/usr/bin/env python3
"""
🌔 CÉLULA MADRE 3 — Script 3.3: ensamblador_final.py
El ensamblador gapless. Une todos los microclips en el video maestro,
quema subtítulos, y hace el despliegue final a la bóveda.
JAMÁS improvises un comando FFmpeg. Todo viene del JSON validado.

Uso:
  python v2/celula_3/ensamblador_final.py --opcion 1   # Ensamble Xfade Gapless
  python v2/celula_3/ensamblador_final.py --opcion 2   # Ensamble Corte Duro
  python v2/celula_3/ensamblador_final.py --opcion 3   # Quema subtítulos .ass
  python v2/celula_3/ensamblador_final.py --opcion 4   # Despliegue: mueve, limpia, notifica
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID    = ADN["produccion"]["evento_id"]
SEMANA       = ADN["produccion"]["semana_prefijo"]
VAULT_BASE   = Path(ADN["assets"]["boveda_base"])
AUDIO_DIR    = Path(ADN["assets"]["paths"]["audio_master"])
MICRO_DIR    = Path(ADN["assets"]["paths"]["microclips"]) / EVENTO_ID
SUB_DIR      = Path(ADN["assets"]["paths"]["subtitulos"])
TIMELINE_DIR = Path(ADN["assets"]["paths"]["timeline_huecos"])
TEMP_DIR     = VAULT_BASE / "temp"
FINAL_DIR    = Path(ADN["assets"]["paths"]["videos_finales"]) / SEMANA

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT  = os.getenv("TELEGRAM_CHAT_ID", "")
RENDER         = ADN["render"]
PRESET         = RENDER.get("ffmpeg_preset", "fast")
CRF            = RENDER.get("crf", 20)
XFADE_DUR      = RENDER.get("xfade_duracion_s", 0.3)

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def correr_ffmpeg(cmd: list, descripcion: str, timeout: int = 600) -> bool:
    log(f"\n  🎬 {descripcion}", GRIS)
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        if result.returncode != 0:
            err(f"FFmpeg falló ({descripcion}):\n{result.stderr.decode()[-600:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        err(f"FFmpeg timeout ({timeout}s): {descripcion}")
        return False
    except FileNotFoundError:
        err("FFmpeg no encontrado.")
        sys.exit(1)

def get_duracion_s(path: Path) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
           "-of", "csv=p=0", str(path)]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        raw = r.stdout.decode().strip()
        return float(raw) if raw else 0.0
    except Exception:
        return 0.0

def listar_clips_ordenados() -> list[Path]:
    """Lista los microclips ordenados por número de toma."""
    if not MICRO_DIR.exists():
        return []
    clips = [f for f in MICRO_DIR.iterdir()
             if f.is_file() and f.suffix == ".mp4" and f.name.startswith("clip_")]
    return sorted(clips, key=lambda p: int(p.name.split("_")[1]))

def buscar_audio_final() -> Path | None:
    """Busca el mejor audio disponible: _sfx > _binaural > _mix > original."""
    for sufijo in ["_sfx", "_binaural", "_mix", ""]:
        ruta = AUDIO_DIR / f"{EVENTO_ID}{sufijo}.mp3"
        if ruta.exists():
            info(f"Audio seleccionado: {ruta.name}")
            return ruta
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS DE TRANSICIÓN — Lógica intra-toma vs inter-toma
# ═══════════════════════════════════════════════════════════════════════════════

# Transiciones SUAVES — clips de la misma toma (espejismos que fluyen)
TRANSICIONES_INTRA = ["fade"]

# Transiciones VÓRTICE — saltos entre tomas distintas (agujeros de gusano cósmicos)
TRANSICIONES_VORTICE = ["fade"]

XFADE_DUR_INTRA   = 1.5    # segundos — suave, cruzado largo onírico
XFADE_DUR_VORTICE = 2.5    # segundos — contundente, fundido onírico largo


def leer_mapa_tomas() -> dict[str, int]:
    """
    Lee lista_de_corte_{EVENTO_ID}.json desde TEMP_DIR y construye
    un mapa {nombre_video: num_toma}.
    Si el archivo no existe o falla, retorna {} para que el fallback
    por nombre de archivo tome el control.
    """
    ruta = TEMP_DIR / f"lista_de_corte_{EVENTO_ID}.json"
    if ruta.exists():
        try:
            with open(ruta, encoding="utf-8") as f:
                data = json.load(f)
            mapa = {}
            for asig in data.get("asignaciones", []):
                nombre = asig.get("nombre_video", "")
                num    = asig.get("num_toma", 0)
                if nombre:
                    mapa[nombre] = num
            if mapa:
                info(f"Mapa de tomas cargado: {len(mapa)} entradas")
                return mapa
        except Exception as e:
            warn(f"No se pudo leer lista_de_corte: {e}. Usando fallback por filename.")
    warn("lista_de_corte ausente — todos los empalmes tratados como inter-toma (vórtice).")
    return {}


def get_toma_de_clip(clip: Path, mapa: dict[str, int]) -> int:
    """
    Devuelve el número de toma de un clip.
    Prioridad: mapa (lista_de_corte) → inferencia desde clip_N.mp4 → hash único.
    """
    if clip.name in mapa:
        return mapa[clip.name]
    # Fallback: "clip_3.mp4" → 3
    try:
        return int(clip.name.split("_")[1])
    except (IndexError, ValueError):
        # Hash único → nunca intra-toma (comportamiento inter-toma seguro)
        return hash(clip.name)


# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Ensamble Xfade Gapless
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_xfade_gapless():
    """
    Une todos los microclips con transiciones xfade suaves (cross-dissolve).
    El timing se basa en las duraciones exactas del timeline_huecos.json.
    Luego mux-ea el audio final.
    Salida: MASTER_<evento>.mp4 en /temp/
    """
    log("\n🎞️  OPCIÓN 1 — Ensamble Xfade Gapless", MAGENTA)

    clips = listar_clips_ordenados()
    if not clips:
        err(f"No hay microclips en {MICRO_DIR}")
        err("Primero ejecuta: fabrica_microclips.py --opcion 1")
        sys.exit(1)

    audio = buscar_audio_final()
    if not audio:
        err(f"No hay audio en {AUDIO_DIR}")
        sys.exit(1)

    info(f"Clips a ensamblar: {len(clips)}")
    for c in clips:
        info(f"  {c.name} ({get_duracion_s(c):.3f}s)", )

    asegurar_dir(TEMP_DIR)
    master_video = TEMP_DIR / f"MASTER_{EVENTO_ID}_noaudio.mp4"
    master_final = TEMP_DIR / f"MASTER_{EVENTO_ID}.mp4"

    if len(clips) == 1:
        # Un solo clip: no necesita xfade
        info("Solo un clip. Ensamblando sin xfade.")
        shutil.copy2(clips[0], master_video)
    else:
        # Construir filter_complex xfade encadenado
        # xfade requiere saber el offset exacto acumulado por duración de clips
        xfade_dur = XFADE_DUR
        duraciones = [get_duracion_s(c) for c in clips]

        # Generar los inputs de FFmpeg
        inputs_cmd = []
        for c in clips:
            inputs_cmd += ["-i", str(c)]

        # Construir la cadena de xfade con transiciones variables:
        # · Intra-toma (mismo nodo narrativo) → dissolve suave
        # · Inter-toma (cambio de tema)        → vórtice cósmico (zoomin/radial/...)
        partes      = []
        label_prev  = "0:v"
        offset_acum = 0.0

        # Cargar mapa de tomas para discriminar cada empalme
        mapa_tomas = leer_mapa_tomas()

        for i in range(1, len(clips)):
            toma_prev = get_toma_de_clip(clips[i - 1], mapa_tomas)
            toma_curr = get_toma_de_clip(clips[i],     mapa_tomas)
            es_intra  = (toma_prev == toma_curr)

            if es_intra:
                tipo_transicion = random.choice(TRANSICIONES_INTRA)
                dur_trans       = XFADE_DUR_INTRA
                tipo_label      = "Intra✨ "
            else:
                tipo_transicion = random.choice(TRANSICIONES_VORTICE)
                dur_trans       = XFADE_DUR_VORTICE
                tipo_label      = "Vórtice🌀"

            log(
                f"    [{tipo_label}] clip[{i-1}](toma {toma_prev}) "
                f"→ clip[{i}](toma {toma_curr}): {tipo_transicion} ({dur_trans}s)",
                GRIS
            )

            offset_acum += duraciones[i - 1] - dur_trans
            label_out    = f"v{i:02d}"

            partes.append(
                f"[{label_prev}][{i}:v]xfade=transition={tipo_transicion}:"
                f"duration={dur_trans}:offset={offset_acum:.6f}[{label_out}]"
            )
            label_prev = label_out

        # Calcular compensación para el video final
        dur_video_esperada = offset_acum + duraciones[-1]
        dur_audio_esperada = get_duracion_s(audio)
        dur_faltante = dur_audio_esperada - dur_video_esperada

        if dur_faltante > 0.05:
            # Agregamos tpad para congelar el último frame durante el tiempo faltante
            partes.append(f"[{label_prev}]tpad=stop_mode=clone:stop_duration={dur_faltante:.3f}[final_v]")
            label_prev = "final_v"

        filtro_complex = ";".join(partes)
        mapa_video     = f"[{label_prev}]"

        cmd_video = (
            ["ffmpeg", "-y", "-threads", "2"] +
            inputs_cmd +
            ["-filter_complex", filtro_complex,
             "-map", mapa_video,
             "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF),
             "-pix_fmt", "yuv420p",
             str(master_video)]
        )

        if not correr_ffmpeg(cmd_video, "xfade gapless", timeout=600):
            err("Ensamble xfade falló. Intentando concat simple como fallback...")
            return _concat_simple(clips, audio, master_final)

    # Mux: video + audio
    dur_video = get_duracion_s(master_video)
    dur_audio = get_duracion_s(audio)
    info(f"Video: {dur_video:.3f}s · Audio: {dur_audio:.3f}s")

    cmd_mux = [
        "ffmpeg", "-y", "-threads", "2",
        "-i", str(master_video),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(master_final)
    ]

    if correr_ffmpeg(cmd_mux, "mux video+audio", timeout=300):
        ok(f"Master generado: {master_final}")
        ok(f"Duración: {get_duracion_s(master_final):.3f}s")
        return str(master_final)
    else:
        err("Mux falló.")
        sys.exit(1)

def _concat_simple(clips: list[Path], audio: Path, salida: Path) -> str:
    """Fallback: concat duro sin xfade usando concat demuxer."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")
        lista_path = f.name

    master_video = salida.parent / f"MASTER_{EVENTO_ID}_noaudio.mp4"
    cmd = [
        "ffmpeg", "-y", "-threads", "2", "-f", "concat", "-safe", "0",
        "-i", lista_path,
        "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF),
        "-pix_fmt", "yuv420p",
        str(master_video)
    ]
    os.unlink(lista_path)
    correr_ffmpeg(cmd, "concat fallback", timeout=600)

    cmd_mux = ["ffmpeg", "-y", "-threads", "2", "-i", str(master_video), "-i", str(audio),
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(salida)]
    correr_ffmpeg(cmd_mux, "mux fallback")
    ok(f"Master (fallback concat): {salida}")
    return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Ensamble Corte Duro
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_corte_duro():
    """
    Concatena clips con corte duro (sin transición de fade).
    Más rápido, ideal para estilo glitch o ritmo urbano.
    """
    log("\n✂️  OPCIÓN 2 — Ensamble Corte Duro", MAGENTA)

    clips = listar_clips_ordenados()
    if not clips:
        err(f"No hay microclips en {MICRO_DIR}")
        sys.exit(1)

    audio  = buscar_audio_final()
    salida = TEMP_DIR / f"MASTER_{EVENTO_ID}.mp4"

    info(f"Concatenando {len(clips)} clips con corte duro...")

    # Concat demuxer (stream copy si todos tienen el mismo codec/resolución)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")
        lista_path = f.name

    asegurar_dir(TEMP_DIR)
    master_video = TEMP_DIR / f"MASTER_{EVENTO_ID}_noaudio.mp4"

    cmd_concat = [
        "ffmpeg", "-y", "-threads", "2",
        "-f", "concat", "-safe", "0",
        "-i", lista_path,
        "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF),
        "-pix_fmt", "yuv420p",
        str(master_video)
    ]

    if not correr_ffmpeg(cmd_concat, "concat duro", timeout=600):
        os.unlink(lista_path)
        sys.exit(1)
    os.unlink(lista_path)

    if audio:
        cmd_mux = [
            "ffmpeg", "-y", "-threads", "2",
            "-i", str(master_video),
            "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(salida)
        ]
        correr_ffmpeg(cmd_mux, "mux audio corte duro", timeout=300)
    else:
        shutil.move(str(master_video), str(salida))

    ok(f"Master corte duro: {salida}")
    return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Quema Subtítulos .ass
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_quemar_subtitulos():
    """
    Quema el archivo .ass sobre el video MASTER generado.
    Requiere que MASTER_<evento>.mp4 exista en /temp/.
    Salida: MASTER_<evento>_sub.mp4
    """
    log("\n📝 OPCIÓN 3 — Quemar Subtítulos .ass", MAGENTA)

    master = TEMP_DIR / f"MASTER_{EVENTO_ID}.mp4"
    if not master.exists():
        err(f"Master no encontrado: {master}")
        err("Primero ejecuta: --opcion 1 o --opcion 2")
        sys.exit(1)

    # Buscar .ass
    ass = SUB_DIR / f"{EVENTO_ID}.ass"
    if not ass.exists():
        # Fallback a .srt
        srt = SUB_DIR / f"{EVENTO_ID}.srt"
        if srt.exists():
            ass = srt
            warn(f".ass no encontrado. Usando .srt: {srt.name}")
        else:
            err(f"Subtítulos no encontrados: {ass}")
            err("Ejecuta: cronometrador_y_tts.py --opcion 2")
            sys.exit(1)

    salida = TEMP_DIR / f"MASTER_{EVENTO_ID}_sub.mp4"

    # Quemar subtítulos con filtro subtitles (soporta .ass y .srt)
    # Escapar la ruta para FFmpeg (caracteres especiales)
    ass_escaped = str(ass.resolve()).replace("\\", "/").replace(":", "\\:")
    if ass.suffix == ".ass":
        filtro_sub = f"ass='{ass_escaped}'"
    else:
        filtro_sub = f"subtitles='{ass_escaped}'"

    cmd = [
        "ffmpeg", "-y", "-threads", "2",
        "-i", str(master),
        "-vf", filtro_sub,
        "-c:v", "libx264", "-preset", PRESET, "-crf", str(CRF),
        "-c:a", "copy",
        str(salida)
    ]

    if correr_ffmpeg(cmd, f"quemar {ass.suffix}", timeout=600):
        ok(f"Video con subtítulos: {salida}")
        info(f"Duración: {get_duracion_s(salida):.3f}s")
        return str(salida)
    else:
        err("Quema de subtítulos falló.")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Despliegue Final
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_despliegue():
    """
    Mueve el video final a /Videos_Finales/<semana>/FINAL_<evento>.mp4,
    limpia los archivos temporales de /temp/, y notifica por Telegram.
    """
    log("\n🚀 OPCIÓN 4 — Despliegue Final", MAGENTA)

    # Buscar el mejor candidato para el video final
    candidatos = [
        TEMP_DIR / f"MASTER_{EVENTO_ID}_sub.mp4",
        TEMP_DIR / f"MASTER_{EVENTO_ID}.mp4",
    ]
    video_final_src = None
    for c in candidatos:
        if c.exists():
            video_final_src = c
            break

    if not video_final_src:
        err(f"No hay video master en {TEMP_DIR}")
        err("Ejecuta primero --opcion 1 (y --opcion 3 si hay subtítulos).")
        sys.exit(1)

    asegurar_dir(FINAL_DIR)
    destino = FINAL_DIR / f"FINAL_{EVENTO_ID}.mp4"

    # Mover el video final
    shutil.copy2(video_final_src, destino)
    ok(f"Video final copiado: {destino}")
    info(f"Tamaño: {destino.stat().st_size / (1024*1024):.1f}MB")
    info(f"Duración: {get_duracion_s(destino):.3f}s")

    # Limpiar /temp/ conservando solo el JSON sagrado del timeline
    archivos_a_limpiar = [
        TEMP_DIR / f"MASTER_{EVENTO_ID}_noaudio.mp4",
        TEMP_DIR / f"MASTER_{EVENTO_ID}.mp4",
        TEMP_DIR / f"MASTER_{EVENTO_ID}_sub.mp4",
        TEMP_DIR / f"lista_de_corte_{EVENTO_ID}.json",
        TEMP_DIR / f"lista_de_corte_validada_{EVENTO_ID}.json",
    ]
    limpios = 0
    for f in archivos_a_limpiar:
        if f.exists():
            f.unlink()
            limpios += 1
    info(f"Archivos temporales limpiados: {limpios}")

    # Notificar por Telegram (si está configurado)
    if TELEGRAM_TOKEN and TELEGRAM_CHAT:
        _notificar_telegram(destino)
    else:
        warn("Telegram no configurado (TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID vacíos en .env).")
        info("El video está listo en la bóveda.")

    log(f"\n{'═'*55}", VERDE)
    log(f"  🎉 PRODUCCIÓN COMPLETADA", VERDE)
    log(f"  📁 {destino}", CYAN)
    log(f"{'═'*55}", VERDE)
    return str(destino)


def _notificar_telegram(video_path: Path):
    """Envía el video por Telegram, comprimiendo un proxy si excede 50MB. Usa caption en lugar de mensaje separado."""
    evento_titulo = ADN["produccion"]["evento_titulo"]
    planeta       = ADN["transito"]["planeta"]
    signo         = ADN["transito"]["signo_destino"]
    dur           = get_duracion_s(video_path)
    size_mb       = video_path.stat().st_size / (1024 * 1024)

    video_a_enviar = video_path
    mensaje = (
        f"🎬 *Video listo*: _{evento_titulo}_\n"
        f"🌌 {planeta} → {signo}\n"
        f"⏱️ Duración: {dur:.1f}s · 📦 Tamaño original: {size_mb:.1f}MB\n"
        f"📁 `{video_path.name}`"
    )

    if size_mb >= 50:
        warn(f"Video original ({size_mb:.1f}MB) excede límite de Telegram. Creando proxy 720p ligero...")
        proxy_path = video_path.with_name("proxy_" + video_path.name)
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", "scale=-2:720",
            "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "128k", str(proxy_path)
        ]
        import subprocess
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if proxy_path.exists() and proxy_path.stat().st_size / (1024*1024) < 50:
            video_a_enviar = proxy_path
            mensaje += "\n⚠️ _Versión proxy comprimida_ (Master HD en bóveda local)"
            info(f"Proxy creado exitosamente: {proxy_path.stat().st_size / (1024*1024):.1f}MB")
        else:
            warn("El proxy sigue superando 50MB o falló. Se aborta notificación Telegram para no enviar mensajes vacíos.")
            if proxy_path.exists(): proxy_path.unlink()
            return

    url_video = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    try:
        import urllib.request
        with open(video_a_enviar, 'rb') as video_file:
            from urllib.request import Request
            boundary = b"----FormBoundaryTelegram"
            
            body = bytearray()
            # Chat ID
            body.extend(b'--' + boundary + b'\r\n')
            body.extend(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n')
            body.extend(TELEGRAM_CHAT.encode() + b'\r\n')
            
            # Caption
            body.extend(b'--' + boundary + b'\r\n')
            body.extend(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
            body.extend(mensaje.encode() + b'\r\n')
            
            # Parse Mode
            body.extend(b'--' + boundary + b'\r\n')
            body.extend(b'Content-Disposition: form-data; name="parse_mode"\r\n\r\n')
            body.extend(b'Markdown\r\n')
            
            # Video
            body.extend(b'--' + boundary + b'\r\n')
            body.extend(b'Content-Disposition: form-data; name="video"; filename="' + video_a_enviar.name.encode() + b'"\r\n')
            body.extend(b'Content-Type: video/mp4\r\n\r\n')
            body.extend(video_file.read() + b'\r\n')
            body.extend(b'--' + boundary + b'--\r\n')
            
            req = Request(url_video, data=bytes(body),
                          headers={"Content-Type": f"multipart/form-data; boundary={boundary.decode()}"},
                          method="POST")
            urllib.request.urlopen(req, timeout=300)
            ok("🎬 ¡Video enviado exitosamente por Telegram!")
    except Exception as e:
        warn(f"Envío de video por Telegram falló: {e}")
    finally:
        if video_a_enviar != video_path and video_a_enviar.exists():
            video_a_enviar.unlink()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌔 Ensamblador Final V2 — Célula Madre 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  1  Ensamble Xfade Gapless (cross-dissolve entre clips)
  2  Ensamble Corte Duro (sin transición, estilo glitch)
  3  Quemar subtítulos .ass sobre el MASTER (requiere --opcion 1 ó 2 antes)
  4  Despliegue: mover a Videos_Finales/, limpiar /temp/, notificar Telegram

Flujo de producción: 1 → 3 → 4
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4], required=True)
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌔 ENSAMBLADOR FINAL V2", MAGENTA)
    log(f"  ADN: {EVENTO_ID} | Semana: {SEMANA}", CYAN)
    log(f"  Clips: {MICRO_DIR}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:   opcion_1_xfade_gapless()
    elif args.opcion == 2: opcion_2_corte_duro()
    elif args.opcion == 3: opcion_3_quemar_subtitulos()
    elif args.opcion == 4: opcion_4_despliegue()

if __name__ == "__main__":
    main()
