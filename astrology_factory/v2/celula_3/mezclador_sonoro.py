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

    # DISEÑO SONORO EVOLUTIVO SINTÉTICO:
    # 1. Cuenco Tibetano Izquierdo (Fundamental + 2 armónicos)
    # 2. Cuenco Tibetano Derecho (Frecuencia + 3Hz para beat binaural delta)
    # 3. Oleaje Marino (Ruido rosa con filtro paso bajo y trémolo muy lento simulando olas)
    # 4. Modulación (aphaser, aecho) y fade in/out
    
    filtro_sanacion = (
        f"[0:a]volume=1.0[voz];"
        f"aevalsrc='0.3*sin(2*PI*{hz}*t) + 0.15*sin(2*PI*{hz*2}*t) + 0.05*sin(2*PI*{hz*3}*t)':d={dur_s:.3f}[cuenco_l];"
        f"aevalsrc='0.3*sin(2*PI*{hz+3}*t) + 0.15*sin(2*PI*{(hz+3)*2}*t) + 0.05*sin(2*PI*{(hz+3)*3}*t)':d={dur_s:.3f}[cuenco_r];"
        f"[cuenco_l][cuenco_r]join=inputs=2:channel_layout=stereo[cuenco_stereo];"
        f"anoisesrc=c=pink:r=44100:a=0.08:d={dur_s:.3f},lowpass=f=300,tremolo=f=0.1:d=0.8[mar];"
        f"[cuenco_stereo][mar]amix=inputs=2:duration=first[sanacion_raw];"
        f"[sanacion_raw]aecho=0.8:0.9:1000|1500:0.3|0.2,aphaser=in_gain=0.4:out_gain=0.5:delay=3:decay=0.4:speed=0.2,tremolo=f=0.05:d=0.3,volume=-8dB[pad];"
        f"[pad]afade=t=in:st=0:d=4,afade=t=out:st={dur_s - 4:.3f}:d=4[pad_faded];"
        f"[voz][pad_faded]amix=inputs=2:duration=first:normalize=0[out]"
    )
    
    cmd_v2 = [
        "ffmpeg", "-y",
        "-i", str(mix_mp3),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", # Placeholder
        "-filter_complex", filtro_sanacion,
        "-map", "[out]",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(salida)
    ]

    exito = correr_ffmpeg(cmd_v2, f"Diseño Sonoro Sanador ({hz}Hz)", timeout=180)
    if exito and salida.exists():
        ok(f"Audio envolvente: {salida}")
        return str(salida)
    else:
        err("Falla en la síntesis. Copiando mix base como salida.")
        import shutil
        shutil.copy2(mix_mp3, salida)
        warn(f"Usando mix sin sanación: {salida}")
        return str(salida)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — SFX en Puntos de Transición
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_sfx_transiciones():
    """
    Inserta un SFX (campanilla/whoosh/ruido cósmico) exactamente en cada
    punto de transición entre tomas, leyendo los tiempos del timeline_huecos.json.
    Lee el archivo SFX del ADN o usa un tono sintético si no existe.
    """
    log("\n🔔 OPCIÓN 3 — SFX en Transiciones", MAGENTA)

    # Audio base
    mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}_binaural.mp3"
    if not mix_mp3.exists():
        mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}_mix.mp3"
    if not mix_mp3.exists():
        mix_mp3 = AUDIO_DIR / f"{EVENTO_ID}.mp3"
    if not mix_mp3.exists():
        err(f"Sin audio base disponible en {AUDIO_DIR}")
        sys.exit(1)

    # Cargar timeline para tiempos exactos de transición
    timeline_path = TIMELINE_DIR / f"{EVENTO_ID}.json"
    if not timeline_path.exists():
        err(f"Timeline no encontrado: {timeline_path}")
        sys.exit(1)
    with open(timeline_path, encoding="utf-8") as f:
        timeline = json.load(f)

    tomas = timeline.get("tomas", [])
    # Los puntos de transición = fin_s de cada toma (menos la última)
    transiciones_s = [t["fin_ms"] / 1000.0 for t in tomas[:-1]]

    info(f"Transiciones: {[f'{t:.3f}s' for t in transiciones_s]}")

    # SFX: usar el definido en ADN o generar tono sintético de 440Hz / 30ms
    sfx_path = AUDIO_CFG.get("sfx_transicion_path", "")
    sfx_existe = sfx_path and Path(sfx_path).exists()
    dur_sfx_ms = AUDIO_CFG.get("sfx_duracion_ms", 80)
    vol_sfx_db = AUDIO_CFG.get("sfx_volumen_db", -12)
    dur_total  = get_duracion_s(mix_mp3)
    salida_sfx = AUDIO_DIR / f"{EVENTO_ID}_sfx.mp3"

    # Construir filter_complex con adelays para cada transición
    # Estrategia: generar un SFX sintético y superponerlo en cada transición
    partes_filtro = []
    inputs_cmd    = ["-i", str(mix_mp3)]

    if sfx_existe:
        info(f"SFX externo: {Path(sfx_path).name} @ {vol_sfx_db}dB")
        for idx, t_s in enumerate(transiciones_s):
            inputs_cmd += ["-i", sfx_path]
            delay_ms = int(t_s * 1000)
            partes_filtro.append(
                f"[{idx+1}:a]volume={vol_sfx_db}dB,adelay={delay_ms}|{delay_ms}[sfx{idx}]"
            )
        amix_inputs = ";".join(partes_filtro)
        amix_labels = "".join(f"[sfx{i}]" for i in range(len(transiciones_s)))
        num_inputs  = len(transiciones_s) + 1
        filtro_full = (
            f"{amix_inputs};"
            f"[0:a]{amix_labels}amix=inputs={num_inputs}:duration=first:normalize=0[out]"
        )
        cmd = inputs_cmd + [
            "-filter_complex", filtro_full,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "2", str(salida_sfx)
        ]
    else:
        elemento = ADN.get("arquetipos", {}).get("elemento", "Agua").lower()
        info(f"Generando SFX sintético orgánico basado en elemento: {elemento.upper()}")
        
        partes_filtro = []
        for idx, t_s in enumerate(transiciones_s):
            delay_ms = int(t_s * 1000)
            dur_sfx_s = dur_sfx_ms / 1000.0
            
            # Síntesis matemática según elemento para salir de lo artificial
            if "agua" in elemento:
                # Pad ambiental etéreo
                expr = f"sin(2*PI*432*t) + 0.3*sin(2*PI*864*t)"
                vol_db = vol_sfx_db - 2
            elif "tierra" in elemento:
                # Drone profundo y orgánico
                expr = f"sin(2*PI*108*t) + 0.5*sin(2*PI*54*t)"
                vol_db = vol_sfx_db + 1
            elif "fuego" in elemento:
                # Resonancia cálida
                expr = f"sin(2*PI*256*t) + 0.5*sin(2*PI*128*t)"
                vol_db = vol_sfx_db
            else: # Aire
                # Viento/frecuencia sutil
                expr = f"sin(2*PI*528*t) + 0.2*sin(2*PI*1056*t)"
                vol_db = vol_sfx_db - 4

            # Usamos aevalsrc acotado con d=3 y le aplicamos fades (fade in de 1s, fade out de 1.5s)
            dur_sintesis = 3.0
            partes_filtro.append(
                f"aevalsrc=exprs='{expr}':d={dur_sintesis},volume={vol_db}dB,"
                f"afade=t=in:st=0:d=1.0,afade=t=out:st=1.5:d=1.5,"
                f"adelay={delay_ms}|{delay_ms}[sfx{idx}]"
            )
            
        amix_labels = "".join(f"[sfx{i}]" for i in range(len(transiciones_s)))
        num_inputs  = len(transiciones_s) + 1

        # No necesitamos lavfi inputs vacíos porque aevalsrc genera su propia fuente
        lavfi_inputs = []

        filtro_full = (
            ";".join(partes_filtro) + ";"
            f"[0:a]{amix_labels}amix=inputs={num_inputs}:duration=first:normalize=0[out]"
        )
        cmd = ["-i", str(mix_mp3)] + lavfi_inputs + [
            "-filter_complex", filtro_full,
            "-map", "[out]",
            "-c:a", "libmp3lame", "-q:a", "2", str(salida_sfx)
        ]
        cmd = ["ffmpeg", "-y"] + cmd

    if sfx_existe:
        cmd = ["ffmpeg", "-y"] + cmd

    exito = correr_ffmpeg(cmd, "SFX transiciones", timeout=120)

    if exito and salida_sfx.exists():
        ok(f"Audio con SFX: {salida_sfx}")
        info(f"Transiciones marcadas: {len(transiciones_s)}")
        return str(salida_sfx)
    else:
        warn("SFX falló. Usando audio base sin SFX.")
        import shutil
        shutil.copy2(mix_mp3, salida_sfx)
        return str(salida_sfx)

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
