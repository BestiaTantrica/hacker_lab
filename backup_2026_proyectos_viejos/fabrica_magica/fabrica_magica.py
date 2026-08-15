import os
import sys
import re
import asyncio
import subprocess
import math
import urllib.parse
import json

# ---------------------------------------------------------------------------
# PATHS Y ENV
# ---------------------------------------------------------------------------
C2_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.abspath(os.path.join(C2_DIR, "..", "..", "espejo_oci1", "api"))
sys.path.append(API_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(API_DIR, "..", "config", "entorno.env"))

try:
    from llm_client import completar
except ImportError:
    print("Error: No se pudo importar llm_client.")
    sys.exit(1)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ---------------------------------------------------------------------------
# MAPA DE MEMES: Fondo Atmosferico + Secuencia de Remates (Montaje Rápido)
# ---------------------------------------------------------------------------
MEME_POR_SIGNO = {
    "Aries":       {"fondo": "fire sparks slow motion", "pips": ["sprinting fast extreme", "falling down fail", "bomb explosion fire"]},
    "Tauro":       {"fondo": "green forest nature",     "pips": ["solid brick wall", "pushing heavy object hard", "pig sleeping mud"]},
    "Geminis":     {"fondo": "fast clouds time lapse",  "pips": ["two mirrors reflection", "person talking very fast", "clown laughing"]},
    "Cancer":      {"fondo": "rain window dark",        "pips": ["theatrical crying", "eating ice cream alone", "baby throwing tantrum"]},
    "Leo":         {"fondo": "golden glitter falling",  "pips": ["looking in mirror confident", "crown gold", "peacock feathers showing off"]},
    "Virgo":       {"fondo": "clean white desk",        "pips": ["dusting cleaning perfectly", "stress pulling hair", "ruler measuring exact"]},
    "Libra":       {"fondo": "pink clouds pastel",      "pips": ["shopping bags many", "indecisive choosing", "makeup mirror beauty"]},
    "Escorpio":    {"fondo": "dark ocean deep",         "pips": ["intense stare eyes", "snake attacking", "dark shadow figure"]},
    "Sagitario":   {"fondo": "running horses field",    "pips": ["running away fast", "packing suitcase fast", "party drinking crazy"]},
    "Capricornio": {"fondo": "dark mountains peak",     "pips": ["boss business meeting angry", "counting money cash", "brick wall barrier"]},
    "Acuario":     {"fondo": "neon lights abstract",    "pips": ["weird scientist crazy", "alien ufo flying", "robot dancing"]},
    "Piscis":      {"fondo": "underwater bubbles",      "pips": ["sleeping dreaming floating", "confused looking around", "crying emotional"]},
}

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def run_cmd(cmd, timeout_secs=300):
    print(f"[*] CMD: {cmd[:80]}...")
    try:
        subprocess.run(cmd, shell=True, check=True, timeout=timeout_secs)
    except subprocess.TimeoutExpired:
        raise Exception(f"Timeout ({timeout_secs}s)")
    except KeyboardInterrupt:
        print("\n[!] CANCELADO.")
        sys.exit(130)

def limpiar_para_tts(texto):
    """Elimina /10 para que TTS diga 'Iniciativa 10' en vez de fracción."""
    texto = re.sub(r'(\d+)/10', r'\1', texto)
    texto = texto.replace('"', "'")
    return texto

# ---------------------------------------------------------------------------
# GENERACION DE GUION con IA
# ---------------------------------------------------------------------------

def generate_script(planeta, signo):
    print(f"[*] Consultando IA para {planeta} en {signo} (Modo Stand-Up Acido)...")
    prompt = f"""Sos un comediante de stand-up despiadado especializado en astrologia. Destruí a {planeta} en {signo}.
Reglas: Cero piedad. Humor muy negro, acido y directo. No uses lenguaje tecnico ni generico ("eres impulsivo"). Usa metaforas ridiculas y dolorosas de la vida cotidiana.
Ejemplo Aries: "Empezas 5 proyectos antes de desayunar y a las 10 AM ya te aburriste de todos. Tu paciencia dura lo que un pedo en una canasta y tu unica estrategia es cabecear paredes."

Devuelve UNICAMENTE un objeto JSON valido con esta estructura, sin markdown:
{{
  "gancho": "El patron toxico mas patetico de esta posicion. (Ej: Te enojas porque el microondas tarda 30 segundos). Max 15 palabras.",
  "verdad": "El remate doloroso. (Ej: Confundis hiperactividad con progreso). Max 15 palabras.",
  "stats": "Dos stats ridiculos X/10. Ej: Cabecear paredes 10/10, Terminar algo 0/10."
}}"""
    try:
        res = completar(prompt, max_tokens=250)
        if "```json" in res: res = res.split("```json")[1].split("```")[0].strip()
        elif "```" in res: res = res.split("```")[1].split("```")[0].strip()
            
        data = json.loads(res)
        guion = f"{data.get('gancho', '')} {data.get('verdad', '')} {data.get('stats', '')}".strip()
        if not guion: raise ValueError("JSON vacio")
        return guion
    except Exception as e:
        print(f"[!] Fallo la IA ({e}). Usando hardcoded fallback.")
        return f"{planeta} en {signo}. Empezas mil cosas y no terminas ninguna. Paciencia cero."

# ---------------------------------------------------------------------------
# TTS (Velocidad +10% para ritmo enérgico pero sin fallos)
# ---------------------------------------------------------------------------

async def generate_voice(text, output_audio):
    print("[*] Generando voz (TTS)...")
    text_tts = limpiar_para_tts(text)
    text_tts = text_tts.replace("'", "'\\''")
    cmd = f"./venv/bin/edge-tts --voice 'es-MX-JorgeNeural' --rate='+10%' --text '{text_tts}' --write-media {output_audio}"
    run_cmd(cmd, timeout_secs=60)

# ---------------------------------------------------------------------------
# PEXELS: descargar un video por query
# ---------------------------------------------------------------------------

def pexels_download(query, output_path, orientation="landscape"):
    # Limitamos la resolucion para evitar timeouts de 120s bajando 4K
    print(f"[*] Pexels ({orientation}): '{query}'...")
    encoded = urllib.parse.quote(query)
    # size=medium trae resoluciones mas manejables (ej. 1080p o 720p)
    api_url = f"https://api.pexels.com/videos/search?query={encoded}&per_page=8&orientation={orientation}&size=medium"

    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: {PEXELS_API_KEY}", api_url],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)

    if not data.get("videos"):
        raise Exception(f"Pexels: sin resultados para '{query}'")

    # Elegir el mejor MP4 disponible (mayor resolucion)
    video_url, best_w = None, 0
    for video in data["videos"]:
        for vfile in video.get("video_files", []):
            w = vfile.get("width", 0)
            if vfile.get("file_type") == "video/mp4" and w > best_w:
                video_url, best_w = vfile["link"], w
        if video_url and best_w >= 1280:
            break

    if not video_url:
        raise Exception(f"Pexels: no MP4 valido para '{query}'")

    print(f"[*] Descargando {best_w}px...")
    subprocess.run(["curl", "-s", "-L", "-o", output_path, video_url], timeout=120, check=True)

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 10000:
        raise Exception(f"Descarga fallida: {output_path}")
    print(f"[*] OK: {os.path.getsize(output_path)//1024}KB")

# ---------------------------------------------------------------------------
# AUDIO UTILS
# ---------------------------------------------------------------------------

def get_audio_duration(audio_file):
    cmd = f'./ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_file}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 30.0

def generar_srt(texto, duration, filepath):
    """Genera SRT cortando el texto en chunks de maximo 3 palabras"""
    words = texto.split()
    chunks = [" ".join(words[i:i+3]) for i in range(0, len(words), 3)]
    tpw = duration / max(len(words), 1)

    def fmt(s):
        return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s-math.floor(s))*1000):03d}"

    with open(filepath, "w", encoding="utf-8") as f:
        t = 0.0
        for i, chunk in enumerate(chunks):
            d = tpw * len(chunk.split())
            f.write(f"{i+1}\n{fmt(t)} --> {fmt(t+d)}\n{chunk}\n\n")
            t += d

# ---------------------------------------------------------------------------
# MERGE FINAL: Meme PIP Montaje Rapido (Kuleshov Effect)
# ---------------------------------------------------------------------------

def merge_layers(bg_file, pip_files, audio_file, output_file, texto):
    print("[*] Componiendo Arquitectura Meme PIP de Montaje Rapido...")
    duration = get_audio_duration(audio_file)
    srt_path = "temp/subtitulos.srt"
    generar_srt(texto, duration, srt_path)

    # Subtitulos enormes
    style = "Alignment=2,FontName=Arial Bold,FontSize=20,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,Outline=4,Shadow=0,MarginV=100"

    # Filtros:
    # 0: bg_dark
    # 1,2,3: Los 3 PIPS. Los recortamos cuadrados (800x800), borde blanco (20px) -> 840x840. Duracion 1.5s c/u.
    # Concat 3 veces para asegurar que llene el audio (1.5*3 = 4.5s * 3 = 13.5s total loop).
    filters = "[0:v]setpts=1.3*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,eq=brightness=-0.4[bg_dark];"
    
    concat_inputs = ""
    for i in range(1, 4):
        # Aceleramos los videos comicos (setpts=0.8*PTS) para darle efecto caotico, cortamos a 1.5s
        filters += f"[{i}:v]setpts=0.8*PTS,scale=800:800:force_original_aspect_ratio=increase,crop=800:800,pad=840:840:20:20:white,setsar=1,fps=30,trim=duration=1.5[pip{i}];"
    
    # Hacemos loop del montaje (clip1, clip2, clip3) infinitamente
    filters += "[pip1][pip2][pip3]concat=n=3:v=1:a=0[pip_seq];"
    filters += "[pip_seq]loop=loop=-1:size=500[pip_montage];"
    filters += "[bg_dark][pip_montage]overlay=(W-w)/2:250[merged];"
    filters += f"[merged]subtitles={srt_path}:force_style='{style}'[out]"

    inputs_cmd = f'-stream_loop -1 -i "{bg_file}" '
    for pf in pip_files:
        inputs_cmd += f'-i "{pf}" '

    cmd = (
        f'./ffmpeg -y '
        f'{inputs_cmd}'
        f'-i "{audio_file}" '
        f'-filter_complex "{filters}" '
        f'-map "[out]" -map 4:a:0 '
        f'-c:v libx264 -crf 23 -preset fast -c:a aac '
        f'-t {duration} "{output_file}"'
    )
    run_cmd(cmd, timeout_secs=600)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

async def main():
    if len(sys.argv) < 3:
        print("Uso: python fabrica_magica.py <Planeta> <Signo>")
        sys.exit(1)

    planeta, signo = sys.argv[1], sys.argv[2]

    os.makedirs("temp", exist_ok=True)
    os.makedirs("assets_generados", exist_ok=True)

    audio_f   = "temp/voice.mp3"
    bg_f      = "temp/bg_fondo.mp4"
    output_f  = f"assets_generados/{planeta.lower()}_{signo.lower()}.mp4"

    # Limpiar temp anterior
    for archivo in os.listdir("temp"):
        os.remove(os.path.join("temp", archivo))

    print("==================================================")
    print(f" FABRICA: {planeta} en {signo} (Kuleshov PIP)")
    print("==================================================")

    guion = generate_script(planeta, signo)
    print(f"\n[GUION]:\n{guion}")

    # 1. Voz
    await generate_voice(guion, audio_f)

    # 2. Videos
    meme_conf = MEME_POR_SIGNO.get(signo, {"fondo": "dark abstract energy", "pips": ["person falling", "explosion", "clown"]})
    
    print(f"\n[INFO] Descargando Fondo (Vertical): {meme_conf['fondo']}")
    try:
        pexels_download(meme_conf['fondo'], bg_f, orientation="portrait")
    except Exception as e:
        print(f"[!] Fallo fondo: {e}")
        sys.exit(1)

    pip_files = []
    for i, pip_query in enumerate(meme_conf["pips"]):
        pf = f"temp/pip_{i}.mp4"
        print(f"\n[INFO] Descargando PIP {i} (Horizontal): {pip_query}")
        try:
            pexels_download(pip_query, pf, orientation="landscape")
            pip_files.append(pf)
        except Exception as e:
            print(f"[!] Fallo PIP {i}: {e}. Duplicando anterior o fondo.")
            if len(pip_files) > 0:
                import shutil
                shutil.copy(pip_files[-1], pf)
                pip_files.append(pf)
            else:
                import shutil
                shutil.copy(bg_f, pf)
                pip_files.append(pf)

    # 3. Componer
    merge_layers(bg_f, pip_files, audio_f, output_f, guion)

    print("==================================================")
    print(f"EXITO -> {output_f}")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
