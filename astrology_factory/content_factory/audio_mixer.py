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
PAD_DB        = -18   # Cortina de seda, muy sutil
ACCENT_DB     = -12   # Acentos tonales, emergen levemente sobre el pad
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
    Mezcla capa de frecuencias (Pad Triádico + Acentos empáticos + Glitch SFX).
    """
    if not os.path.exists(mp3_path):
        return mp3_path
        
    if glitch_timestamps is None:
        glitch_timestamps = []

    # Cargar paletas
    db_path = os.path.join(os.path.dirname(__file__), "astrology_palettes.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            palettes = json.load(f)
    else:
        palettes = {}

    conf = palettes.get(aspect, {})
    hz = conf.get("base_freq", detect_freq(guion_text))
    ratios = conf.get("pad_ratios", [1.0, 1.25, 1.5])
    
    hz1 = round(hz * ratios[0])
    hz2 = round(hz * ratios[1])
    hz3 = round(hz * ratios[2])
    
    dur  = _get_duration(mp3_path)
    out  = mp3_path.replace(".mp3", "_mixed.mp3")

    print(f"🎵 Pad de Seda {hz}Hz + armónicos @ {PAD_DB}dB")

    inputs = ["-i", mp3_path,
              "-f","lavfi","-i",f"sine=frequency={hz1}:sample_rate=44100",
              "-f","lavfi","-i",f"sine=frequency={hz2}:sample_rate=44100",
              "-f","lavfi","-i",f"sine=frequency={hz3}:sample_rate=44100"]

    fade_out_st = max(0, dur - FADE_SEC)

    # Pad de seda
    fg_pad = (
        f"[1:a]atrim=duration={dur:.2f},"
        f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
        f"volume={PAD_DB}dB[p1];"
        f"[2:a]atrim=duration={dur:.2f},"
        f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
        f"volume={PAD_DB-4}dB[p2];"
        f"[3:a]atrim=duration={dur:.2f},"
        f"afade=t=in:d={FADE_SEC},afade=t=out:st={fade_out_st:.2f}:d={FADE_SEC},"
        f"volume={PAD_DB-8}dB[p3];"
        f"[p1][p2][p3]amix=inputs=3:normalize=0[pad];"
    )

    # Acentos empáticos por palabras clave
    accent_parts = []
    n_accents = 0
    if words_json_path and os.path.exists(words_json_path):
        with open(words_json_path, "r", encoding="utf-8") as f:
            words_data = json.load(f)
        
        # Filtrar palabras que disparan acentos
        for w in words_data:
            word = w.get("word", "")
            start = w.get("start", 0)
            if word in FREQ_MAP:
                # Generamos un tono puro de 3 segundos con fade in de 1s y fade out de 2s
                accent_hz = FREQ_MAP[word]
                delay_ms = int(start * 1000)
                lbl = f"k{n_accents}"
                idx = 4 + n_accents
                inputs += [
                    "-f","lavfi","-i",
                    f"sine=frequency={accent_hz}:sample_rate=44100:duration=3.0"
                ]
                accent_parts.append(
                    f"[{idx}:a]afade=t=in:d=1,afade=t=out:st=1:d=2,"
                    f"volume={ACCENT_DB}dB,adelay={delay_ms}|{delay_ms}[{lbl}];"
                )
                n_accents += 1

    # SFX de Glitches (Sintéticos)
    glitch_parts = []
    glitch_sfx = conf.get("glitch_sfx", "anoisesrc=c=white:d=0.08")
    
    n_glitches = 0
    for g_time in glitch_timestamps:
        delay_ms = int(g_time * 1000)
        lbl = f"g{n_glitches}"
        idx = 4 + n_accents + n_glitches
        
        inputs += [
            "-f", "lavfi", "-i", glitch_sfx
        ]
        glitch_parts.append(
            f"[{idx}:a]volume={ACCENT_DB}dB,adelay={delay_ms}|{delay_ms}[{lbl}];"
        )
        n_glitches += 1

    fg_glitches = "".join(glitch_parts)
    
    total_mix_inputs = 2 # narr + pad
    mix_lbls = "[narr][pad]"
    
    if n_accents > 0:
        accent_str = "".join(accent_parts)
        accent_lbls = "".join(f"[k{i}]" for i in range(n_accents))
        fg_accents = accent_str + f"{accent_lbls}amix=inputs={n_accents}:normalize=0[accents];"
        mix_lbls += "[accents]"
        total_mix_inputs += 1
    else:
        fg_accents = ""
        
    if n_glitches > 0:
        glitch_lbls = "".join(f"[g{i}]" for i in range(n_glitches))
        fg_glitches += f"{glitch_lbls}amix=inputs={n_glitches}:normalize=0[glitches];"
        mix_lbls += "[glitches]"
        total_mix_inputs += 1

    fg_final = (
        f"[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[narr];"
        f"{mix_lbls}amix=inputs={total_mix_inputs}:duration=first:normalize=0[out]"
    )
    
    if n_accents > 0: print(f"   ✨ {n_accents} Acentos Empáticos generados a lo largo del guion")
    if n_glitches > 0: print(f"   ⚡ {n_glitches} SFX de Glitches inyectados en la mezcla")

    filter_graph = fg_pad + fg_accents + fg_glitches + fg_final

    cmd = (["ffmpeg","-y"] + inputs +
           ["-filter_complex", filter_graph,
            "-map","[out]","-ac","2","-ar","44100","-q:a","2", out])

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"⚠️  audio_mixer falló: {r.stderr[-400:]}")
        return mp3_path

    print(f"   ✅ Audio inteligente mezclado → {os.path.basename(out)}")
    return out
