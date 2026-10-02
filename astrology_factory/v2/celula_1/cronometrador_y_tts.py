#!/usr/bin/env python3
"""
🌒 CÉLULA MADRE 1 — Script 1.2: cronometrador_y_tts.py
El corazón matemático del enjambre.
Genera audio TTS por toma, mide duraciones exactas, concatena y produce
el timeline_huecos.json que toda la Célula 3 respeta como ley.
NO renderiza video. NO toca assets visuales.

Uso:
  python v2/celula_1/cronometrador_y_tts.py --opcion 1   # TTS + mapeo matemático (TODO en uno)
  python v2/celula_1/cronometrador_y_tts.py --opcion 2   # Whisper → .ass (karaoke TikTok)
  python v2/celula_1/cronometrador_y_tts.py --opcion 3   # Whisper → .srt (clásico YouTube)
  python v2/celula_1/cronometrador_y_tts.py --opcion 4   # Recalcular timeline_huecos.json
  python v2/celula_1/cronometrador_y_tts.py --opcion 1 --guion /ruta/guion.json
"""

import argparse
import json
import os
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

EVENTO_ID     = ADN["produccion"]["evento_id"]
VAULT_BASE    = Path(ADN["assets"]["boveda_base"])
TEMP_DIR      = VAULT_BASE / "temp"
AUDIO_DIR     = Path(ADN["assets"]["paths"]["audio_master"])
SUB_DIR       = Path(ADN["assets"]["paths"]["subtitulos"])
TIMELINE_DIR  = Path(ADN["assets"]["paths"]["timeline_huecos"])

AUDIO_CFG     = ADN["audio"]
VOZ_TTS       = AUDIO_CFG["voz_tts"]

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

GUIONES_DIR   = Path(ADN["assets"]["paths"].get("guiones", VAULT_BASE / "Guiones"))

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def cargar_guion(guion_path: str = None) -> dict:
    """Carga el guion JSON. Busca en /Guiones/ si no se especifica ruta."""
    if guion_path:
        ruta = Path(guion_path)
    else:
        ruta = GUIONES_DIR / f"guion_{EVENTO_ID}.json"
    if not ruta.exists():
        err(f"Guion no encontrado: {ruta}")
        err("Primero ejecuta: generador_guiones.py --opcion 1")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

def get_duracion_ms(path: Path) -> float:
    """
    Obtiene la duración de un archivo de audio en milisegundos usando ffprobe.
    Retorna 0.0 si falla.
    """
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        raw = result.stdout.decode().strip()
        return float(raw) * 1000  # convertir a ms
    except Exception as e:
        warn(f"ffprobe falló en {path.name}: {e}")
        return 0.0

def correr_comando(cmd: list, descripcion: str = "", timeout: int = 120) -> tuple[bool, str]:
    """Ejecuta un comando. Retorna (éxito, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        stderr = result.stderr.decode()
        if result.returncode != 0:
            return False, stderr
        return True, stderr
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except FileNotFoundError as e:
        return False, f"Comando no encontrado: {e}"

def sintetizar_toma_tts(texto: str, num_toma: int, tmp_dir: Path,
                         voz: str, velocidad: str, tono: str) -> Path | None:
    """
    Sintetiza una sola toma con edge-tts humanizado (troceado por comas/puntos con micro-pausas).
    Si falla, reintenta. Si vuelve a fallar, usa Piper TTS local.
    """
    if not texto.strip():
        err(f"Toma {num_toma}: texto vacío, omitiendo.")
        return None

    salida = tmp_dir / f"toma_{num_toma:02d}.mp3"

    # Humanización: Le damos la toma entera a Edge-TTS para que mantenga la fluidez y pausas naturales
    try:
        exito_toma = False
        salida_tts_pura = tmp_dir / f"toma_{num_toma:02d}_pura.mp3"
        
        for intento in range(1, 4):  # Hasta 3 intentos
            cmd = [
                str(FACTORY_ROOT / "venv" / "bin" / "edge-tts"),
                "--voice", voz,
                "--text", texto,
                "--write-media", str(salida_tts_pura)
            ]
            
            # Dinamismo sutil en velocidad para no sonar monótono
            import random
            rate_pct = random.choice(["+0%", "+2%", "+4%"])
            pitch_hz = random.choice(["-1Hz", "+0Hz", "+1Hz"])
            
            cmd.append(f"--rate={rate_pct}")
            cmd.append(f"--pitch={pitch_hz}")

            exito, stderr = correr_comando(cmd, f"TTS toma {num_toma}", timeout=45)
            if exito and salida_tts_pura.exists() and salida_tts_pura.stat().st_size > 1000:
                exito_toma = True
                break
            else:
                import time
                time.sleep(2)
                
        if not exito_toma:
            raise Exception(f"Edge-TTS falló en la toma {num_toma}")
        
        # Agregamos solo una pequeña pausa al final para respirar entre tomas
        pausa_ms = random.randint(200, 300)
        cmd_silence = ["ffmpeg", "-y", "-i", str(salida_tts_pura), "-af", f"apad=pad_dur={pausa_ms/1000.0}", "-c:a", "libmp3lame", "-q:a", "2", str(salida)]
        correr_comando(cmd_silence, "Agregando micro-silencio final", timeout=20)
        
        if not salida.exists():
            # Fallback
            import shutil
            shutil.copy(salida_tts_pura, salida)
            
        info(f"Toma {num_toma}: sintetizada HUMANIZADA EXITOSAMENTE con Edge-TTS (fluida).")
        return salida
                
    except Exception as e:
        warn(f"Toma {num_toma}: edge-tts falló completamente ({e}). Intentando Piper TTS (Local)...")
        # --- FALLBACK PIPER ---
        try:
            piper_model = FACTORY_ROOT / "v2" / "modelos_piper" / "es_ES-davefx-medium.onnx"
            if not piper_model.exists():
                raise FileNotFoundError("Modelo Piper faltante")
                
            salida_wav = tmp_dir / f"toma_{num_toma:02d}.wav"
            cmd = [str(FACTORY_ROOT / "venv" / "bin" / "piper"), "--model", str(piper_model), "--output_file", str(salida_wav)]
            proc = subprocess.run(cmd, input=texto.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            
            if proc.returncode == 0 and salida_wav.exists() and salida_wav.stat().st_size > 100:
                cmd_ffmpeg = ["ffmpeg", "-y", "-i", str(salida_wav), "-c:a", "libmp3lame", "-q:a", "2", str(salida)]
                correr_comando(cmd_ffmpeg, f"Convertir Piper WAV a MP3")
                if salida.exists():
                    info(f"Toma {num_toma}: sintetizada EXITOSAMENTE con Piper TTS.")
                    return salida
        except Exception as e2:
            err(f"Piper TTS fallback falló: {e2}")

    err(f"Toma {num_toma}: no se pudo sintetizar con ninguna voz.")
    return None

def concatenar_audios(lista_mp3: list[Path], salida: Path) -> bool:
    """
    Concatena una lista de MP3 en un único archivo usando ffmpeg concat demuxer.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                     delete=False, encoding='utf-8') as f:
        for mp3 in lista_mp3:
            f.write(f"file '{mp3.resolve()}'\n")
        lista_path = f.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", lista_path,
        "-c:a", "libmp3lame", "-q:a", "2",
        str(salida)
    ]
    exito, stderr = correr_comando(cmd, "concat audios", timeout=120)
    os.unlink(lista_path)

    if not exito:
        err(f"Error al concatenar audios: {stderr[-300:]}")
    return exito

def construir_timeline_huecos(tomas_con_duracion: list[dict]) -> dict:
    """
    Construye el JSON de timeline_huecos a partir de las duraciones medidas.
    Cada hueco tiene: num, rol, inicio_ms, fin_ms, duracion_ms, texto.
    """
    timeline = {
        "evento_id": EVENTO_ID,
        "total_duracion_ms": 0,
        "total_duracion_s": 0,
        "num_tomas": len(tomas_con_duracion),
        "tomas": []
    }

    cursor_ms = 0.0
    for toma in tomas_con_duracion:
        dur_ms = toma["duracion_ms"]
        entry  = {
            "num":         toma["num"],
            "rol":         toma.get("rol", f"toma_{toma['num']}"),
            "inicio_ms":   round(cursor_ms, 3),
            "fin_ms":      round(cursor_ms + dur_ms, 3),
            "duracion_ms": round(dur_ms, 3),
            "duracion_s":  round(dur_ms / 1000, 6),
            "texto":       toma.get("texto", ""),
            "etiqueta_visual": toma.get("etiqueta_visual")
        }
        timeline["tomas"].append(entry)
        cursor_ms += dur_ms

    timeline["total_duracion_ms"] = round(cursor_ms, 3)
    timeline["total_duracion_s"]  = round(cursor_ms / 1000, 6)
    return timeline

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Síntesis TTS + Mapeo Matemático (TODO en uno)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_tts_y_mapeo(guion_path: str = None):
    """
    FLUJO COMPLETO HOLÍSTICO:
    1. Lee guion_<evento>.json
    2. Concatena todos los textos y los envía a Edge-TTS en una sola pasada.
    3. Edge-TTS genera el master MP3 y un archivo de subtítulos VTT.
    4. Se parsea el VTT para mapear matemáticamente cuándo empieza y termina cada toma.
    5. Genera /timeline_huecos/<evento>.json con tiempos al milisegundo.
    Esto garantiza fluidez absoluta (cero silencios robóticos).
    """
    log("\n🎙️  OPCIÓN 1 — Síntesis TTS Holística + Mapeo VTT", MAGENTA)

    guion = cargar_guion(guion_path)
    tomas = guion.get("tomas", [])
    if not tomas:
        err("El guion no tiene tomas.")
        sys.exit(1)

    voz       = VOZ_TTS["voz"]
    velocidad = "+0%"
    tono      = "+0Hz"

    info(f"Tomas a sintetizar: {len(tomas)}")
    info(f"Voz: {voz}  Velocidad: {velocidad}  Tono: {tono}")

    asegurar_dir(AUDIO_DIR)
    asegurar_dir(TIMELINE_DIR)

    salida_mp3      = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    salida_timeline = TIMELINE_DIR / f"{EVENTO_ID}.json"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # 1. Preparar texto maestro (Inyectando vida y pausas esotéricas)
        textos = []
        for t in tomas:
            txt = t.get("texto", "").strip()
            # Truco de cadencia: Cambiamos el punto final por puntos suspensivos
            # para que Edge-TTS baje el tono lentamente, sonando reflexivo/humano.
            if txt.endswith('.') or txt.endswith(','):
                txt = txt[:-1] + '...'
            else:
                txt += '...'
            textos.append(txt)
            
        master_text = " ".join(textos)
        vtt_path = tmp_path / "master.vtt"
        mp3_pura = tmp_path / "master_pura.mp3"

        log(f"\n{'─'*50}", CYAN)
        log(f"  FASE 1: Síntesis Holística Edge-TTS", CYAN)
        log(f"{'─'*50}", CYAN)

        cmd = [
            str(FACTORY_ROOT / "venv" / "bin" / "edge-tts"),
            "--voice", voz,
            "--text", master_text,
            "--write-media", str(mp3_pura),
            "--write-subtitles", str(vtt_path),
            f"--rate={velocidad}",
            f"--pitch={tono}"
        ]
        
        exito, stderr = correr_comando(cmd, "Edge-TTS Master Synthesis", timeout=120)
        
        if not exito or not mp3_pura.exists() or not vtt_path.exists():
            err(f"Fallo crítico en Edge-TTS: {stderr}")
            sys.exit(1)
            
        info("Síntesis maestra completada exitosamente.")

        # 2. Parsear VTT para mapear tomas
        import re
        
        def time_to_ms(t_str):
            h, m, s_ms = t_str.split(':')
            s, ms = s_ms.split(',')
            return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)

        with open(vtt_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            
        subs = []
        current_sub = {}
        for line in lines:
            if '-->' in line:
                start, end = line.split(' --> ')
                current_sub['start_ms'] = time_to_ms(start)
                current_sub['end_ms'] = time_to_ms(end)
            elif line.strip() and not line.strip().isdigit() and 'WEBVTT' not in line:
                current_sub['text'] = line.strip()
                subs.append(current_sub)
                current_sub = {}
                
        tomas_con_duracion = []
        toma_idx = 0
        toma_chars_needed = len(re.sub(r'\s+', '', tomas[toma_idx].get('texto', '')))
        toma_chars_found = 0
        
        # El primer clip empieza en 0
        toma_start_ms = 0
        
        for sub in subs:
            sub_chars = len(re.sub(r'\s+', '', sub['text']))
            toma_chars_found += sub_chars
            
            if toma_chars_found >= toma_chars_needed - 3: # Tolerancia de caracteres
                dur_ms = sub['end_ms'] - toma_start_ms
                tomas_con_duracion.append({
                    "num": tomas[toma_idx]["num"],
                    "rol": tomas[toma_idx].get("rol", f"toma_{tomas[toma_idx]['num']}"),
                    "duracion_ms": dur_ms,
                    "texto": tomas[toma_idx].get("texto", ""),
                    "etiqueta_visual": tomas[toma_idx].get("etiqueta_visual")
                })
                toma_idx += 1
                if toma_idx < len(tomas):
                    toma_chars_needed = len(re.sub(r'\s+', '', tomas[toma_idx].get('texto', '')))
                    toma_chars_found = 0
                    toma_start_ms = sub['end_ms']
                    
        if toma_idx < len(tomas):
            warn(f"No se pudieron mapear {len(tomas) - toma_idx} tomas usando el VTT.")

        # 3. Copiar el mp3 al destino final
        import shutil
        shutil.copy(mp3_pura, salida_mp3)

        log(f"\n{'─'*50}", CYAN)
        log(f"  FASE 2: Generación del Timeline de Huecos", CYAN)
        log(f"{'─'*50}", CYAN)

        timeline = construir_timeline_huecos(tomas_con_duracion)
        with open(salida_timeline, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2, ensure_ascii=False)

        info(f"Timeline guardado en: {salida_timeline.name}")
        info(f"Audio final guardado en: {salida_mp3.name}")
        
        dur_total_ms = timeline['total_duracion_ms']

    # Imprimir resumen final
    log(f"\n{'═'*55}", VERDE)
    log(f"  📊 RESUMEN OPCIÓN 1", VERDE)
    log(f"{'═'*55}", VERDE)
    log(f"  MP3 maestro:  {salida_mp3}", CYAN)
    log(f"  Timeline:     {salida_timeline}", CYAN)
    log(f"  Tomas:        {len(tomas_con_duracion)}", CYAN)
    log(f"  Duración:     {timeline['total_duracion_s']:.3f}s", CYAN)
    log(f"\n  Desglose por toma:", CYAN)
    for t in timeline["tomas"]:
        bar = "█" * int(t["duracion_s"] * 3)
        log(f"    [{t['num']}] {t['rol']:25s} {t['duracion_s']:6.3f}s  {bar}", GRIS)
    log(f"{'═'*55}", VERDE)
    log(f"\n  ➡️  Siguiente: auditor_boveda.py --opcion 1", AMARILLO)

    return str(salida_mp3), str(salida_timeline)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Subtítulos .ass (karaoke TikTok)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_subtitulos_ass(guion_path: str = None):
    """
    Genera subtítulos .ass estilo karaoke/TikTok usando Whisper sobre el MP3 maestro.
    Si Whisper no genera .ass directamente, convierte su JSON a .ass con estilo propio.
    """
    log("\n📝 OPCIÓN 2 — Subtítulos .ass (karaoke TikTok)", MAGENTA)

    mp3_maestro = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not mp3_maestro.exists():
        err(f"MP3 maestro no encontrado: {mp3_maestro}")
        err("Primero ejecuta: --opcion 1 para generar el audio.")
        sys.exit(1)

    asegurar_dir(SUB_DIR)
    salida_ass = SUB_DIR / f"{EVENTO_ID}.ass"
    salida_json = SUB_DIR / f"{EVENTO_ID}_whisper.json"

    info(f"Procesando con Whisper (modelo: {AUDIO_CFG['whisper']['modelo']})...")
    info(f"Input: {mp3_maestro}")

    # Ejecutar Whisper — salida JSON para máximo control
    modelo_whisper = "small"
    idioma_whisper = AUDIO_CFG["whisper"]["idioma"]

    cmd_whisper = [
        str(FACTORY_ROOT / "venv" / "bin" / "whisper"), str(mp3_maestro),
        "--model", modelo_whisper,
        "--language", idioma_whisper,
        "--output_format", "json",
        "--word_timestamps", "True",
        "--output_dir", str(SUB_DIR),
        "--task", "transcribe"
    ]

    info("Ejecutando Whisper (puede tardar ~30s según el modelo)...")
    exito, stderr = correr_comando(cmd_whisper, "whisper json", timeout=900)

    if not exito:
        err(f"Whisper falló: {stderr[-400:]}")
        sys.exit(1)

    # Whisper guarda el JSON con el nombre del archivo de entrada
    whisper_json = SUB_DIR / f"{EVENTO_ID}.json"
    if not whisper_json.exists():
        err(f"Whisper no generó el JSON esperado en: {whisper_json}")
        sys.exit(1)

    with open(whisper_json, encoding="utf-8") as f:
        whisper_data = json.load(f)

    # Convertir a .ass con estilo cinemático oscuro
    ass_contenido = generar_ass_desde_whisper(whisper_data)

    with open(salida_ass, "w", encoding="utf-8") as f:
        f.write(ass_contenido)

    ok(f"Subtítulos .ass generados: {salida_ass}")
    info("Estilo: letras amarillas, contorno negro, posición baja, animación karaoke")
    return str(salida_ass)

def segundos_a_ass(segundos: float) -> str:
    """Convierte segundos float a formato ASS H:MM:SS.cc"""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = segundos % 60
    cs = int((s % 1) * 100)
    s = int(s)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generar_ass_desde_whisper(whisper_data: dict) -> str:
    """
    Convierte el JSON de Whisper a .ass con estilo TikTok/cinemático oscuro.
    Usa timestamps a nivel de PALABRA si están disponibles.
    """
    paleta = ADN["estetica_visual"]["paleta_colores"]

    # Convertir HEX a BGR (formato ASS: &HAABBGGRR)
    def hex_a_ass_color(hex_color: str, alpha: int = 0) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"

    color_primario  = hex_a_ass_color(paleta["acento"])      # Rojo/naranja brillante
    color_outline   = hex_a_ass_color("#000000")              # Contorno negro
    color_shadow    = hex_a_ass_color(paleta["fondo_oscuro"]) # Sombra oscura
    color_highlight = hex_a_ass_color(paleta["dorado"])       # Dorado para karaoke

    ass_header = f"""[Script Info]
Title: {ADN['produccion']['evento_titulo']}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTokDark,Montserrat,68,{color_primario},{color_highlight},{color_outline},{color_shadow},-1,0,0,0,100,100,0.5,0,1,3.5,1.5,2,60,60,200,1
Style: Subtitle,Montserrat,54,&H00FFFFFF,{color_highlight},{color_outline},{color_shadow},0,0,0,0,100,100,0,0,1,2.5,1,2,60,60,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = []
    segmentos = whisper_data.get("segments", [])

    for seg in segmentos:
        # Preferir timestamps a nivel de palabra si existen
        palabras = seg.get("words", [])
        if palabras:
            # Agrupar palabras en bloques de 3-5 para ritmo TikTok
            BLOQUE = 4
            for i in range(0, len(palabras), BLOQUE):
                grupo = palabras[i:i+BLOQUE]
                t_inicio = grupo[0].get("start", seg["start"])
                t_fin    = grupo[-1].get("end",   seg["end"])
                # Construir texto con efecto karaoke {\k} por palabra
                texto_kara = ""
                for p in grupo:
                    dur_cs = int((p.get("end", t_fin) - p.get("start", t_inicio)) * 100)
                    texto_kara += f"{{\\k{dur_cs}}}{p.get('word', '').strip()} "
                texto_kara = texto_kara.strip()
                lines.append(
                    f"Dialogue: 0,{segundos_a_ass(t_inicio)},{segundos_a_ass(t_fin)},"
                    f"TikTokDark,,0,0,0,,{texto_kara}"
                )
        else:
            # Fallback: segmento completo como línea simple
            t_inicio = seg.get("start", 0)
            t_fin    = seg.get("end",   t_inicio + 3)
            texto    = seg.get("text", "").strip()
            lines.append(
                f"Dialogue: 0,{segundos_a_ass(t_inicio)},{segundos_a_ass(t_fin)},"
                f"Subtitle,,0,0,0,,{texto}"
            )

    return ass_header + "\n".join(lines) + "\n"

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Subtítulos .srt (clásico YouTube)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_subtitulos_srt():
    """
    Genera subtítulos .srt estándar usando Whisper.
    Ideal para YouTube o como backup del .ass.
    """
    log("\n📄 OPCIÓN 3 — Subtítulos .srt (YouTube)", MAGENTA)

    mp3_maestro = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not mp3_maestro.exists():
        err(f"MP3 maestro no encontrado: {mp3_maestro}")
        err("Primero ejecuta: --opcion 1")
        sys.exit(1)

    asegurar_dir(SUB_DIR)
    salida_srt = SUB_DIR / f"{EVENTO_ID}.srt"

    modelo_whisper = "small"
    idioma_whisper = AUDIO_CFG["whisper"]["idioma"]

    cmd_whisper = [
        str(FACTORY_ROOT / "venv" / "bin" / "whisper"), str(mp3_maestro),
        "--model", modelo_whisper,
        "--language", idioma_whisper,
        "--output_format", "srt",
        "--output_dir", str(SUB_DIR),
        "--task", "transcribe"
    ]

    info(f"Ejecutando Whisper (modelo: {modelo_whisper})...")
    exito, stderr = correr_comando(cmd_whisper, "whisper srt", timeout=300)

    if not exito:
        err(f"Whisper falló: {stderr[-400:]}")
        sys.exit(1)

    # Whisper guarda el .srt con el nombre del input
    whisper_srt = SUB_DIR / f"{EVENTO_ID}.srt"
    if whisper_srt.exists():
        ok(f"Subtítulos .srt generados: {whisper_srt}")
        # Contar entradas
        contenido = whisper_srt.read_text(encoding="utf-8")
        num_entries = contenido.count("\n\n")
        info(f"Entradas de subtítulo: {num_entries}")
    else:
        err("Whisper no generó el .srt esperado.")
        sys.exit(1)

    return str(salida_srt)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Regenerar Timeline Huecos
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_regenerar_timeline(guion_path: str = None):
    """
    Recalcula el timeline_huecos.json a partir de los MP3 de tomas existentes
    o del audio maestro + guion. Útil si el audio fue editado manualmente.
    No requiere re-sintetizar con edge-tts.
    """
    log("\n⏱️  OPCIÓN 4 — Regenerar Timeline Huecos", MAGENTA)

    guion = cargar_guion(guion_path)
    tomas = guion.get("tomas", [])

    mp3_maestro = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not mp3_maestro.exists():
        err(f"MP3 maestro no encontrado: {mp3_maestro}")
        err("No se puede recalcular sin el audio maestro.")
        sys.exit(1)

    dur_total_ms = get_duracion_ms(mp3_maestro)
    info(f"Duración del MP3 maestro: {dur_total_ms:.1f}ms = {dur_total_ms/1000:.2f}s")
    info(f"Tomas en el guion: {len(tomas)}")

    # Estrategia 1: Buscar los MP3 temporales de tomas si existen
    # (guardados en /temp/tomas_<evento>/)
    tomas_dir = TEMP_DIR / f"tomas_{EVENTO_ID}"
    tomas_con_duracion = []

    if tomas_dir.exists():
        mp3_tomas = sorted(tomas_dir.glob("toma_*.mp3"))
        if len(mp3_tomas) == len(tomas):
            info(f"Encontrados {len(mp3_tomas)} MP3 de tomas en {tomas_dir}")
            for toma, mp3 in zip(tomas, mp3_tomas):
                dur_ms = get_duracion_ms(mp3)
                tomas_con_duracion.append({**toma, "duracion_ms": dur_ms})
            info("Usando duraciones medidas de los MP3 individuales.")
        else:
            warn(f"MP3 de tomas ({len(mp3_tomas)}) no coincide con tomas del guion ({len(tomas)}).")

    # Estrategia 2: Distribuir la duración total proporcionalmente por número de palabras
    if not tomas_con_duracion:
        warn("No hay MP3 de tomas. Distribuyendo duración proporcionalmente por palabras.")
        total_palabras = sum(len(t.get("texto", "").split()) for t in tomas)
        if total_palabras == 0:
            err("El guion no tiene texto.")
            sys.exit(1)
        for toma in tomas:
            palabras = len(toma.get("texto", "").split())
            proporcion = palabras / total_palabras
            dur_ms = dur_total_ms * proporcion
            tomas_con_duracion.append({**toma, "duracion_ms": dur_ms})
        warn("⚠️  Tiempos son aproximados. Para precisión matemática, usa --opcion 1.")

    asegurar_dir(TIMELINE_DIR)
    timeline = construir_timeline_huecos(tomas_con_duracion)

    # La última toma absorbe el tiempo residual para garantizar que la suma = total real
    if tomas_con_duracion:
        suma_actual = timeline["total_duracion_ms"]
        residuo     = dur_total_ms - suma_actual
        if abs(residuo) > 0.1:
            timeline["tomas"][-1]["duracion_ms"]   += residuo
            timeline["tomas"][-1]["fin_ms"]        += residuo
            timeline["tomas"][-1]["duracion_s"]     = timeline["tomas"][-1]["duracion_ms"] / 1000
            timeline["total_duracion_ms"]            = dur_total_ms
            timeline["total_duracion_s"]             = dur_total_ms / 1000
            info(f"Residuo de {residuo:.2f}ms absorbido en la última toma (regla gapless).")

    salida = TIMELINE_DIR / f"{EVENTO_ID}.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    ok(f"Timeline regenerado: {salida}")
    info(f"Duración total: {timeline['total_duracion_s']:.3f}s")
    for t in timeline["tomas"]:
        log(f"  Toma {t['num']:>2}: {t['inicio_ms']:>8.1f}ms → {t['fin_ms']:>8.1f}ms  ({t['duracion_s']:.3f}s)", GRIS)

    return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌒 Cronometrador y TTS V2 — Célula Madre 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Opciones disponibles:
  1  Síntesis TTS (edge-tts por toma) + Mapeo Matemático → timeline_huecos.json
  2  Whisper → .ass cinemático (karaoke TikTok, timestamps por palabra)
  3  Whisper → .srt clásico (YouTube)
  4  Regenerar timeline_huecos.json (sin re-sintetizar TTS)

IMPORTANTE: La opción 1 es el paso fundacional. 2, 3 y 4 dependen de su salida.
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4], required=True)
    parser.add_argument("--guion", type=str, default=None,
                        help="Ruta al JSON del guion (default: /temp/guion_<evento>.json)")
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌒 CRONOMETRADOR Y TTS V2", MAGENTA)
    log(f"  ADN:     {EVENTO_ID}", CYAN)
    log(f"  Salidas: {AUDIO_DIR}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:
        opcion_1_tts_y_mapeo(args.guion)
    elif args.opcion == 2:
        opcion_2_subtitulos_ass(args.guion)
    elif args.opcion == 3:
        opcion_3_subtitulos_srt()
    elif args.opcion == 4:
        opcion_4_regenerar_timeline(args.guion)

if __name__ == "__main__":
    main()
