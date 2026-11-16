"""
audio_mixer.py — Diseño sonoro para tránsitos astrológicos
Capas:
  1. PAD ARMÓNICO (Cortina de Seda): fundamental + 3ra + 5ta a -15dB constante.
  2. KEYWORDS (Diseño empático): Acentos tonales en frecuencias específicas disparados
     por las marcas de tiempo (words.json) de conceptos clave.
"""

import os, subprocess, json

FREQ_MAP = {
    # Cortina de seda detect
    "escorpio": 396, "pluton": 396, "sombra": 396, "miedo": 396, "culpa": 396,
    "urano": 417, "ruptura": 417, "cambio": 417, "liberacion": 417,
    "venus": 528, "amor": 528, "sanacion": 528, "luna_llena": 528,
    "libra": 639, "vinculo": 639, "relacion": 639, "pareja": 639,
    "mercurio": 741, "marte": 741, "accion": 741, "decision": 741,
    "neptuno": 852, "intuicion": 852, "revelacion": 852,
    
    # Adicionales para Miercoles
    "intenso": 396, "intensidad": 396, "deseo": 528, "verdad": 852, "magnetica": 528
}

DEFAULT_FREQ  = 528
PAD_DB        = -14   # Cortina de seda con presencia armónica real y envolvente
ACCENT_DB     = -10   # Acentos tonales perceptibles en palabras clave
FADE_SEC      = 2.0   # Fade in/out del pad base

def detect_freq(text: str) -> int:
    t = text.lower()
    for kw, f in FREQ_MAP.items():
        if kw in t:
            return f
    return DEFAULT_FREQ

def _get_duration(mp3_path: str) -> float:
    probe = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", mp3_path],
        capture_output=True, text=True)
    return float(probe.stdout.strip() or 30)

def mix_frequency_layer(
    mp3_path: str,
    guion_text: str = "",
    words_json_path: str | None = None,
    aspect: str = "conjuncion",
    glitch_timestamps: list[float] = None
) -> str:
    """
    Mezcla un diseño sonoro hipnótico y envolvente:
      - Cuenco tibetano acústico real (armónicos naturales y campanas).
      - Biosfera espacial y mantras profundos de la Bóveda.
      - Sub-drone armónico afinado a la frecuencia Solfeggio del aspecto (filtrado cálido, cero pitidos).
    """
    if not os.path.exists(mp3_path):
        return mp3_path
        
    if glitch_timestamps is None:
        glitch_timestamps = []

    # Cargar paletas de afinación astrológica
    db_path = os.path.join(os.path.dirname(__file__), "astrology_palettes.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            palettes = json.load(f)
    else:
        palettes = {}

    aspect_norm = str(aspect).lower().replace("ó", "o").replace("í", "i").replace("á", "a").replace("é", "e").replace("ú", "u").strip()
    conf = palettes.get(aspect_norm, {})
    hz = conf.get("base_freq", detect_freq(guion_text))
    
    dur  = _get_duration(mp3_path)
    out  = mp3_path.replace(".mp3", "_mixed.mp3")

    print(f"🎵 Atmósfera Hipnótica: Cuencos Tibetanos + Biosfera Cósmica + Sub-Drone Solfeggio {hz}Hz")

    # ── Capas Acústicas Reales (Bóveda Sagrada) ──
    cuenco_path = "/home/tomas2/Desktop/Boveda_Astrologia/Assets_Auditados/Audios/cuenco_tibetano_largo_raw.mp3"
    ambient_path = "/home/tomas2/Desktop/Boveda_Astrologia/Assets_Auditados/Audios/ambient_space_biosphere_raw.mp3"
    om_path = "/home/tomas2/Desktop/Boveda_Astrologia/Assets_Auditados/Audios/Om_Mantra_Bowls.mp3"
    
    has_cuenco = os.path.exists(cuenco_path)
    has_ambient = os.path.exists(ambient_path)
    has_om = os.path.exists(om_path)

    fade_out_st = max(0, dur - FADE_SEC)

    # Sub-drone cálido en la frecuencia Solfeggio (terciopelo grave, bajo filtrado, CERO silbido estridente)
    inputs = [
        "-i", mp3_path,
        "-f", "lavfi", "-i", f"sine=frequency={hz}:sample_rate=44100"
    ]

    fg_subdrone = (
        f"[1:a]atrim=duration={dur:.2f},lowpass=f=320,chorus=0.7:0.9:55:0.4:0.25:2,"
        f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
        f"volume=-24dB,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[subdrone];"
    )

    current_idx = 2
    mix_lbls = "[narr][subdrone]"
    total_mix_inputs = 2

    fg_cuenco = ""
    if has_cuenco:
        inputs += ["-stream_loop", "-1", "-i", cuenco_path]
        fg_cuenco = (
            f"[{current_idx}:a]atrim=duration={dur:.2f},aecho=0.8:0.7:60:0.3,"
            f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
            f"volume=-14dB,lowpass=f=3500,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[cuenco];"
        )
        mix_lbls += "[cuenco]"
        total_mix_inputs += 1
        current_idx += 1

    fg_ambient = ""
    if has_ambient:
        inputs += ["-stream_loop", "-1", "-i", ambient_path]
        fg_ambient += (
            f"[{current_idx}:a]atrim=duration={dur:.2f},"
            f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
            f"volume=-17dB,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[amb];"
        )
        mix_lbls += "[amb]"
        total_mix_inputs += 1
        current_idx += 1

    fg_om = ""
    if has_om:
        inputs += ["-stream_loop", "-1", "-i", om_path]
        fg_om = (
            f"[{current_idx}:a]atrim=duration={dur:.2f},"
            f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
            f"volume=-22dB,lowpass=f=1800,aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[om];"
        )
        mix_lbls += "[om]"
        total_mix_inputs += 1
        current_idx += 1

    fg_final = (
        f"[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[narr];"
        f"{mix_lbls}amix=inputs={total_mix_inputs}:duration=first:normalize=0[out]"
    )

    filter_graph = fg_subdrone + fg_cuenco + fg_ambient + fg_om + fg_final

    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", filter_graph,
            "-map", "[out]", "-ac", "2", "-ar", "44100", "-q:a", "2", out])

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️  audio_mixer falló: {r.stderr[-400:]}")
        return mp3_path

    print(f"   ✅ Atmósfera sonora acústica hipnótica mezclada → {os.path.basename(out)}")
    return out
