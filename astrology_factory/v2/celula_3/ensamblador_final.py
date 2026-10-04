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

def verificar_final_no_negro(video: Path, umbral_luma: float = 20.0) -> bool:
    """Mide el brillo medio (0-255) de los últimos 0.4 s. Avisa si el final es oscuro."""
    cmd = ["ffmpeg", "-v", "error", "-sseof", "-0.4", "-i", str(video), "-an",
           "-vf", "scale=64:-1,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
           "-f", "null", "-"]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        vals = [float(l.split("=")[1]) for l in r.stdout.decode().splitlines()
                if "YAVG" in l and "=" in l]
        if not vals:
            return True
        media = sum(vals) / len(vals)
        if media < umbral_luma:
            warn(f"⚫ El final del video es OSCURO (brillo medio {media:.1f}/255). Revisar.")
            return False
        ok(f"Final del video con imagen (brillo medio {media:.1f}/255)")
        return True
    except Exception:
        return True

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS DE TRANSICIÓN — Lógica intra-toma vs inter-toma
# ═══════════════════════════════════════════════════════════════════════════════

# Transiciones SUAVES — clips de la misma toma (espejismos que fluyen)
TRANSICIONES_INTRA = ["fade", "dissolve"]

# Transiciones VÓRTICE — saltos entre tomas distintas (agujeros de gusano cósmicos)
# El Director de Arte elige la correcta según la emoción del beat.
# Si no hay datos, se usa una de estas al azar.
TRANSICIONES_VORTICE = ["dissolve", "fade", "smoothleft", "circlecrop", "pixelize", "distance", "radial", "hlslice"]

XFADE_DUR_INTRA   = 0.2    # segundos — suave, rápido para acompañar el relato
XFADE_DUR_VORTICE = 0.8    # segundos — fundido onírico pero dinámico


def leer_mapa_tomas() -> dict[str, dict]:
    """
    Lee lista_de_corte_{EVENTO_ID}.json desde TEMP_DIR y construye
    un mapa {nombre_video: {"num_toma": int, "transicion": str}}.
    La transición viene del Director de Arte (campo 'transicion_entrada').
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
                trans  = asig.get("transicion_entrada", "fade")
                if nombre:
                    mapa[nombre] = {"num_toma": num, "transicion": trans}
            if mapa:
                info(f"Mapa de tomas cargado: {len(mapa)} entradas (con transiciones del Director de Arte)")
                return mapa
        except Exception as e:
            warn(f"No se pudo leer lista_de_corte: {e}. Usando fallback por filename.")
    warn("lista_de_corte ausente — todos los empalmes tratados como inter-toma (vórtice).")
    return {}


def get_toma_de_clip(clip: Path, mapa: dict) -> int:
    """Devuelve el número de toma de un clip."""
    entry = mapa.get(clip.name)
    if isinstance(entry, dict):
        return entry["num_toma"]
    # Fallback: "clip_3.mp4" → 3
    try:
        return int(clip.name.split("_")[1])
    except (IndexError, ValueError):
        return hash(clip.name)


def get_transicion_de_clip(clip: Path, mapa: dict) -> str:
    """Devuelve la transición xfade recomendada por el Director de Arte para un clip."""
    entry = mapa.get(clip.name)
    if isinstance(entry, dict):
        return entry.get("transicion", "fade")
    return random.choice(TRANSICIONES_VORTICE)


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
        # Construir filter_complex xfade encadenado.
        #
        # PROBLEMA ORIGINAL: cada xfade solapa dos clips y ACORTA el video total
        # (Σ duraciones − Σ transiciones). El video terminaba antes que el audio,
        # se rellenaba congelando el último fotograma y las imágenes iban llegando
        # cada vez más temprano respecto al relato (desfase acumulado).
        #
        # SOLUCIÓN: cada transición se CENTRA en el límite narrativo (donde cambia
        # la idea del relato) y cada clip recibe un pequeño relleno (clone del
        # último fotograma, invisible porque está bajo el fundido) para cubrir
        # su parte del solape. Resultado: video total == Σ duraciones == audio.
        duraciones = [get_duracion_s(c) for c in clips]
        inputs_cmd = []
        for c in clips:
            inputs_cmd += ["-i", str(c)]

        mapa_tomas = leer_mapa_tomas()
        n = len(clips)

        # 1) Elegir tipo y duración de cada empalme i (entre clip i-1 y clip i)
        tipos = [None] * n
        trans = [0.0] * (n + 1)   # trans[i] = duración del empalme hacia el clip i; trans[0]=trans[n]=0
        for i in range(1, n):
            toma_prev = get_toma_de_clip(clips[i - 1], mapa_tomas)
            toma_curr = get_toma_de_clip(clips[i],     mapa_tomas)
            es_intra  = (toma_prev == toma_curr)
            if es_intra:
                tipos[i] = random.choice(TRANSICIONES_INTRA)
                dur_t    = XFADE_DUR_INTRA
                tipo_label = "Intra✨ "
            else:
                # Usar la transición que el Director de Arte asignó al clip de destino
                tipos[i] = get_transicion_de_clip(clips[i], mapa_tomas)
                dur_t    = XFADE_DUR_VORTICE
                tipo_label = "Vórtice🌀"
            # Nunca más de la mitad del clip más corto de los dos
            dur_t = min(dur_t, 0.5 * min(duraciones[i - 1], duraciones[i]))
            trans[i] = round(dur_t, 3)
            log(
                f"    [{tipo_label}] clip[{i-1}](toma {toma_prev}) "
                f"→ clip[{i}](toma {toma_curr}): {tipos[i]} ({trans[i]}s)",
                GRIS
            )

        # 2) Normalizar cada entrada (mismo fps/timebase/formato) y rellenar su cola
        partes = []
        for i in range(n):
            pad = (trans[i] + trans[i + 1]) / 2.0
            f = f"[{i}:v]fps=30,setsar=1,format=yuv420p,settb=AVTB"
            if pad > 0:
                f += f",tpad=stop_mode=clone:stop_duration={pad + 0.002:.6f}"
            partes.append(f + f"[n{i}]")

        # 3) Encadenar: el empalme i arranca en (límite narrativo − trans/2)
        label_prev = "n0"
        inicio_narrativo = 0.0
        for i in range(1, n):
            inicio_narrativo += duraciones[i - 1]          # S_i
            offset = inicio_narrativo - trans[i] / 2.0
            label_out = f"v{i:02d}"
            partes.append(
                f"[{label_prev}][n{i}]xfade=transition={tipos[i]}:"
                f"duration={trans[i]}:offset={offset:.6f}[{label_out}]"
            )
            label_prev = label_out

        # 4) Seguridad: el video debe cubrir exactamente el audio
        dur_video_esperada = sum(duraciones)
        dur_audio_esperada = get_duracion_s(audio)
        dur_faltante = dur_audio_esperada - dur_video_esperada
        info(f"Video esperado: {dur_video_esperada:.3f}s · Audio: {dur_audio_esperada:.3f}s · Diferencia: {dur_faltante:+.3f}s")

        if dur_faltante > 0.05:
            partes.append(f"[{label_prev}]tpad=stop_mode=clone:stop_duration={dur_faltante:.3f}[padded_v]")
            label_prev = "padded_v"
            
        # Añadir un leve fade out al final para "magia" en la transición final y evitar negro seco
        fade_start = (dur_video_esperada + max(0, dur_faltante)) - 0.5
        if fade_start > 0:
            partes.append(f"[{label_prev}]fade=t=out:st={fade_start}:d=0.5[final_v]")
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
        verificar_final_no_negro(master_final)
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
