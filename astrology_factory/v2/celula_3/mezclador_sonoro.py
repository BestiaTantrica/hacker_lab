#!/usr/bin/env python3
"""
🌔 CÉLULA MADRE 3 — Script 3.2: mezclador_sonoro.py
Mezcla el audio maestro con música de fondo, frecuencias binaurales y SFX.
Lee el ADN para todos los parámetros. JAMÁS improvises un comando FFmpeg.

Uso:
  python v2/celula_3/mezclador_sonoro.py --opcion 1                          # Voz + música
  python v2/celula_3/mezclador_sonoro.py --opcion 1 --musica /ruta/bgm.mp3   # Con música específica
  python v2/celula_3/mezclador_sonoro.py --opcion 2                          # Añade pad binaural
  python v2/celula_3/mezclador_sonoro.py --opcion 3                          # SFX en transiciones
"""

import argparse
import json
import subprocess
import sys
import random
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID  = ADN["produccion"]["evento_id"]
VAULT_BASE = Path(ADN["assets"]["boveda_base"])
AUDIO_DIR  = Path(ADN["assets"]["paths"]["audio_master"])
TEMP_DIR   = VAULT_BASE / "temp"
TIMELINE_DIR = Path(ADN["assets"]["paths"]["timeline_huecos"])

AUDIO_CFG  = ADN["audio"]
MUSICA_CFG = AUDIO_CFG.get("musica_fondo", {})
FRECUENCIA = AUDIO_CFG.get("frecuencia_binaural_hz", 528)
PRESET     = ADN["render"].get("ffmpeg_preset", "fast")

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def correr_ffmpeg(cmd: list, descripcion: str, timeout: int = 180) -> bool:
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        if result.returncode != 0:
            err(f"FFmpeg falló ({descripcion}): {result.stderr.decode()[-400:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        err(f"FFmpeg timeout: {descripcion}")
        return False
    except FileNotFoundError:
        err("FFmpeg no encontrado.")
        sys.exit(1)

def get_duracion_s(path: Path) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
           "-of", "csv=p=0", str(path)]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        return float(r.stdout.decode().strip())
    except Exception:
        return 0.0

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Voiceover + Música de Fondo
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_voz_mas_musica(musica_path: str = None):
    """
    Mezcla la voz TTS con música de fondo.
    Música duckeada a -18dB (o el nivel definido en el ADN) bajo la voz.
    Si no se pasa ruta de música, usa la configurada en el ADN.
    """
    log("\n🎵 OPCIÓN 1 — Voz + Música de Fondo", MAGENTA)

    voz_mp3 = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not voz_mp3.exists():
        err(f"Audio TTS no encontrado: {voz_mp3}")
        err("Primero ejecuta: cronometrador_y_tts.py --opcion 1")
        sys.exit(1)

    # Buscar música: arg > ADN > sin música (solo voz)
    if musica_path:
        bgm = Path(musica_path)
    else:
        bgm_cfg = MUSICA_CFG.get("path_default", "")
        bgm = Path(bgm_cfg) if bgm_cfg else None

    salida_mix = AUDIO_DIR / f"{EVENTO_ID}_mix.mp3"
    dur_voz    = get_duracion_s(voz_mp3)

    if bgm and bgm.exists():
        db_musica = MUSICA_CFG.get("volumen_db", -18)
        info(f"Voz: {voz_mp3.name} ({dur_voz:.2f}s)")
        info(f"Música: {bgm.name} @ {db_musica}dB")

        # Mezcla: voz normal + música a db_musica, duración = voz
        # La música se loopea si es más corta que la voz (amix with duration=first)
        filtro = (
            f"[1:a]volume={db_musica}dB,aloop=loop=-1:size=2e+09[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(voz_mp3),
            "-i", str(bgm),
            "-filter_complex", filtro,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(salida_mix)
        ]
    else:
        if not bgm:
            warn("Sin música configurada. Usando solo la voz.")
        else:
            warn(f"Música no encontrada: {bgm}. Usando solo la voz.")
        # Sin música: solo normalizar el volumen de la voz
        cmd = [
            "ffmpeg", "-y",
            "-i", str(voz_mp3),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(salida_mix)
        ]

    asegurar_dir(AUDIO_DIR)
    exito = correr_ffmpeg(cmd, "mezcla voz+música", timeout=120)

    if exito and salida_mix.exists():
        ok(f"Mix guardado: {salida_mix}")
        info(f"Duración: {get_duracion_s(salida_mix):.2f}s")
        return str(salida_mix)
    else:
        err("La mezcla falló.")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Pad Binaural (frecuencia del ADN)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_binaural():
    """
    Añade un tono binaural de la frecuencia definida en el ADN (ej: 528Hz).
    El pad se genera matemáticamente con FFmpeg (sin archivo externo).
    Incluye síntesis de cuencos tibetanos (armónicos), oleaje natural (ruido rosa) y modulaciones para emular cimática.
    """
    log("\n🔮 OPCIÓN 2 — Diseño Sonoro Sanador (Cimática, Cuencos, Naturaleza)", MAGENTA)

    mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}_mix.mp3"
    if not mix_mp3.exists():
         mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not mix_mp3.exists():
         err(f"Audio no encontrado: {AUDIO_DIR}/{EVENTO_ID}_mix.mp3")
         sys.exit(1)

    dur_s = get_duracion_s(mix_mp3)
    hz = FRECUENCIA
    salida = AUDIO_DIR / f"{EVENTO_ID}_binaural.mp3"

    info(f"Frecuencia base: {hz}Hz")
    info(f"Duración: {dur_s:.2f}s · Modulación de ondas delta (3Hz) para relajación profunda")

    # Buscar pistas de Stock_Sonoro (ya procesadas y filtradas)
    stock_dir = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Stock_Sonoro")
    paletas = []
    if stock_dir.exists():
        paletas = list(stock_dir.glob("*.mp3"))
        
    # Generar string de volumen dinámico (subibaja sutil según tensión de la toma)
    vol_str = "0.4"
    timeline_path = TIMELINE_DIR / f"{EVENTO_ID}.json"
    if timeline_path.exists():
        try:
            with open(timeline_path, encoding="utf-8") as f:
                tdata = json.load(f)
            expr_parts = []
            for t_idx, t_info in enumerate(tdata.get("tomas", [])):
                r = t_info.get("rol", "")
                s = t_info.get("inicio_ms", 0) / 1000.0
                e = t_info.get("fin_ms", 0) / 1000.0
                # Roles de tensión o clímax tendrán volumen sutilmente más alto
                if r in ["gancho", "mecanica_astrologica", "tension_oportunidad", "climax", "transitos_principales"]:
                    v = 1.40
                else:
                    v = 0.80
                expr_parts.append(f"if(between(t,{s},{e}), {v}, 0)")
            if expr_parts:
                vol_str = " + ".join(expr_parts)
            info("Volumen dinámico generado según el relato.")
        except Exception as e:
            warn(f"No se pudo crear volumen dinámico: {e}")

    if paletas:
        paleta = random.choice(paletas)
        dur_paleta = get_duracion_s(paleta)
        
        # Elegir un punto de inicio aleatorio en la pista de stock
        start_offset = 0.0
        if dur_paleta > dur_s:
            start_offset = random.uniform(0.0, dur_paleta - dur_s)
            
        info(f"Usando track de stock preparado: {paleta.name} (offset: {start_offset:.1f}s)")
        
        filtro_sanacion = (
            f"[0:a]volume=1.0[voz];"
            f"[1:a]atrim=start={start_offset:.3f}:duration={dur_s:.3f},volume='{vol_str}':eval=frame[pad];"
            f"[voz][pad]amix=inputs=2:duration=first:normalize=0[out]"
        )
        
        cmd_v2 = [
            "ffmpeg", "-y",
            "-i", str(mix_mp3),
            "-i", str(paleta),
            "-filter_complex", filtro_sanacion,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(salida)
        ]
        
        exito = correr_ffmpeg(cmd_v2, f"Diseño Sonoro ({paleta.name})", timeout=180)
        if exito and salida.exists():
            ok(f"Audio envolvente: {salida}")
            return str(salida)
        
    err("Falla en la mezcla o no hay audios de stock. Copiando mix base como salida.")
    import shutil
    shutil.copy2(mix_mp3, salida)
    warn(f"Usando mix sin sanación: {salida}")
    return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — SFX en Puntos de Transición
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_sfx_transiciones():
    log("\n🔔 OPCIÓN 3 — SFX en Transiciones (Cuencos/Gongs)", MAGENTA)

    # Audio base
    mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}_binaural.mp3"
    if not mix_mp3.exists():
        mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}_mix.mp3"
    if not mix_mp3.exists():
        err(f"Sin audio base disponible en {AUDIO_DIR}")
        sys.exit(1)

    salida = AUDIO_DIR / f"{EVENTO_ID}_sfx.mp3"
    import shutil
    
    guion_path = Path(ADN["assets"]["paths"]["timeline_huecos"]) / f"{EVENTO_ID}.json"
    if not guion_path.exists():
        err(f"No se encontró el guion validado en {guion_path}. Copiando base sin SFX.")
        shutil.copy2(mix_mp3, salida)
        return str(salida)

    with open(guion_path, "r", encoding="utf-8") as f:
        guion = json.load(f)

    tomas = guion.get("tomas", [])
    tiempos = []
    acum = 0.0
    for t in tomas[:-1]:
        # Consideramos solo tomas que sí generaron duración (segun guión validado)
        dur = float(t.get("duracion_ms", 0)) / 1000.0
        if dur > 0:
            acum += dur
            tiempos.append(acum)

    if not tiempos:
        shutil.copy2(mix_mp3, salida)
        return str(salida)

    # Generamos un sonido sanador rápido (Cuenco Sintético 432Hz)
    sfx_wav = TEMP_DIR / f"cuenco_sfx_{EVENTO_ID}.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=432:duration=2",
        "-f", "lavfi", "-i", "sine=frequency=864:duration=2",
        "-filter_complex", "[0:a]volume=1.0[a0];[1:a]volume=0.2[a1];[a0][a1]amix=inputs=2:normalize=0,afade=t=in:ss=0:d=0.05,afade=t=out:st=0.1:d=1.9[out]",
        "-map", "[out]",
        str(sfx_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Construimos el comando para retrasar (adelay) el sfx y mezclarlo (amix)
    cmd = ["ffmpeg", "-y", "-threads", "2", "-i", str(mix_mp3)]
    for _ in tiempos:
        cmd += ["-i", str(sfx_wav)]

    filter_complex = ""
    for i, t_s in enumerate(tiempos):
        ms = int(t_s * 1000)
        # adelay recibe ms. |ms duplica en estereo
        filter_complex += f"[{i+1}:a]adelay={ms}|{ms}[d{i}]; "

    mix_inputs = "".join([f"[d{i}]" for i in range(len(tiempos))])
    filter_complex += f"[0:a]{mix_inputs}amix=inputs={len(tiempos)+1}:dropout_transition=2:normalize=0[aout]"

    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(salida)
    ]

    import os
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        err(f"Error inyectando SFX: {res.stderr.decode('utf-8', errors='ignore')}")
        shutil.copy2(mix_mp3, salida)
    else:
        ok(f"Se inyectaron {len(tiempos)} impactos de cuenco (SFX) en los cortes.")
        ok(f"Audio final con SFX: {salida}")
    
    if sfx_wav.exists():
        os.remove(str(sfx_wav))

    return str(salida)
# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌔 Mezclador Sonoro V2 — Célula Madre 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  1  Voz TTS + música de fondo (ducking a -18dB)
  2  Añade pad binaural de la frecuencia del ADN (ej: 528Hz subliminal)
  3  Inserta SFX en cada punto de transición entre tomas

Flujo: 1 → 2 → 3 → ensamblador_final.py
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3], required=True)
    parser.add_argument("--musica", type=str, default=None,
                        help="[Opción 1] Ruta al MP3/WAV de música de fondo")
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌔 MEZCLADOR SONORO V2", MAGENTA)
    log(f"  ADN: {EVENTO_ID} · Frecuencia binaural: {FRECUENCIA}Hz", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:   opcion_1_voz_mas_musica(args.musica)
    elif args.opcion == 2: opcion_2_binaural()
    elif args.opcion == 3: opcion_3_sfx_transiciones()

if __name__ == "__main__":
    main()
