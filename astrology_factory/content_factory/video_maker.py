"""
video_maker.py — v4 (Single-Pass FFmpeg + Glitch Engine Ready)
────────────────────────────────────────────────────────────────
Novedades respecto a v3:
  • Storyboard generado por Gemini desde el guion (concordancia imagen-relato)
  • Pexels Videos como background: movimiento real, sin Ken Burns artificial
  • Imágenes estáticas como fallback con scale+crop pan suave
  • Símbolo astrológico watermark (♏♎✦☽☉) en escenas relevantes
  • Color grading por energía + vignette (heredado de v3)
  • Arquitectura SINGLE-PASS en memoria (filter_complex global), ultra rápida
  • Auto-copia a Bóveda al finalizar

RUNBOOK: No llamar a este archivo directamente si se desean glitches astrológicos.
El punto de entrada correcto es `editing_reviewer.py`, que detecta el aspecto, inyecta
los glitches visuales y luego invoca este script como backend de renderizado.
"""

import os
import subprocess
import sys
import glob
import shutil

FPS      = 25
FADE_DUR = 0.0

FONT_SYMBOL = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
FONT_TEXT   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_audio_duration(mp3_path: str) -> float:
    cmd = ["ffprobe", "-i", mp3_path, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 60.0


def parse_ass_durations(ass_path: str) -> list[tuple[float, float]]:
    """Extrae (start_sec, end_sec) de cada línea de diálogo."""
    dialogues = []
    if not os.path.exists(ass_path):
        return dialogues
    
    with open(ass_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("Dialogue:"):
                parts = line.split(",", 9)
                if len(parts) >= 10:
                    start_str, end_str = parts[1], parts[2]
                    def time_to_sec(t_str):
                        h, m, s = t_str.split(":")
                        return int(h)*3600 + int(m)*60 + float(s)
                    dialogues.append((time_to_sec(start_str), time_to_sec(end_str)))
    return dialogues


def _escape_filter(path: str) -> str:
    return path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


# ─────────────────────────────────────────────────────────────────────────────
# Color grading por energía astrológica
# ─────────────────────────────────────────────────────────────────────────────

def _color_filter(aspect: str) -> str:
    import json
    db_path = os.path.join(os.path.dirname(__file__), "astrology_palettes.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            palettes = json.load(f)
            if aspect in palettes:
                return palettes[aspect]["grading_vf"]
    return "eq=brightness=0.0:saturation=1.1:contrast=1.05,curves=r='0/0 0.5/0.53 1/0.98'"


# ─────────────────────────────────────────────────────────────────────────────
# Transiciones variadas por energía
# ─────────────────────────────────────────────────────────────────────────────

def _get_transition(query_to: str) -> str:
    q = query_to.lower()
    # Usamos fade a negro para escenas oscuras o del espacio,
    # y fundido suave (dissolve) para el resto (transición sin transición).
    if any(k in q for k in ["scorpio", "shadow", "dark", "space", "universe", "cosmos", "night"]):
        return "fadeblack"
    return "dissolve"


# ─────────────────────────────────────────────────────────────────────────────
# Símbolo astrológico watermark
# ─────────────────────────────────────────────────────────────────────────────

def _symbol_filter(query: str) -> str | None:
    """Devuelve filtro drawtext con símbolo astrológico, o None si no aplica."""
    q = query.lower()
    if "scorpio" in q:    symbol = "\u265f"   # ♏ (fallback: usar texto)
    elif "venus" in q:    symbol = "\u2640"   # ♀
    elif "balance" in q or "scale" in q or "libra" in q: symbol = "\u264e"  # ♎
    elif "moon" in q:     symbol = "\u263d"   # ☽
    elif any(k in q for k in ["star", "cosmos", "universe"]): symbol = "\u2736"  # ✶
    elif "sun" in q or "solar" in q: symbol = "\u2609"  # ☉
    else:
        return None

    if not os.path.exists(FONT_SYMBOL):
        return None

    esc_font = _escape_filter(FONT_SYMBOL)
    return (f"drawtext=fontfile='{esc_font}'"
            f":text='{symbol}'"
            f":fontsize=72:fontcolor=white@0.22"
            f":x=w-100:y=55")


# ─────────────────────────────────────────────────────────────────────────────
# Ken Burns Dinámico y Rápido (Crop animado)
# ─────────────────────────────────────────────────────────────────────────────

def _kenburnspan_filter(idx: int, clip_dur: float) -> str:
    OW, OH = 1080, 1920
    # Alternar entre 1.05 y 1.15 de zoom para más variación de velocidad
    zoom = 1.08 if idx % 2 == 0 else 1.15
    iw, ih = int(OW * zoom), int(OH * zoom)
    dx, dy = iw - OW, ih - OH
    cx, cy = dx // 2, dy // 2
    D = f"{clip_dur:.4f}"
    
    # 8 variaciones de movimiento (rectos y diagonales)
    motion = idx % 8
    if   motion == 0: x, y = f"{dx}*t/{D}", str(cy)                 # Pan right
    elif motion == 1: x, y = f"{dx}*(1-t/{D})", str(cy)             # Pan left
    elif motion == 2: x, y = str(cx), f"{dy}*t/{D}"                 # Pan down
    elif motion == 3: x, y = str(cx), f"{dy}*(1-t/{D})"             # Pan up
    elif motion == 4: x, y = f"{dx}*t/{D}", f"{dy}*t/{D}"           # Pan down-right
    elif motion == 5: x, y = f"{dx}*(1-t/{D})", f"{dy}*(1-t/{D})"   # Pan up-left
    elif motion == 6: x, y = f"{dx}*t/{D}", f"{dy}*(1-t/{D})"       # Pan up-right
    else:             x, y = f"{dx}*(1-t/{D})", f"{dy}*t/{D}"       # Pan down-left
    
    return f"scale={iw}:{ih}:force_original_aspect_ratio=increase,crop={iw}:{ih},crop={OW}:{OH}:x='{x}':y='{y}'"


# ─────────────────────────────────────────────────────────────────────────────
# Bóveda Automática
# ─────────────────────────────────────────────────────────────────────────────

def _copy_to_vault(evento_name: str, out_video: str):
    # Extraer prefijo de semana: "Semana2_Octubre_Lunes" → "Semana2_Octubre"
    parts = evento_name.split("_")
    semana_prefix = "_".join(parts[:2]) if len(parts) >= 2 else "Misc"
    vault_dir = f"/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Videos_Finales/{semana_prefix}"
    
    print(f"\n📦 Copiando a Bóveda automática: {vault_dir}")
    try:
        os.makedirs(vault_dir, exist_ok=True)
        dest = os.path.join(vault_dir, f"FINAL_{evento_name}.mp4")
        shutil.copy2(out_video, dest)
        print(f"   ✅ ¡Copiado exitoso! → {dest}")
    except Exception as e:
        print(f"   ❌ Error al copiar a Bóveda: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline principal
# ─────────────────────────────────────────────────────────────────────────────

def create_video(evento_name: str) -> str | None:
    base_dir  = os.path.dirname(os.path.dirname(__file__))
    prod_dir  = os.path.join(base_dir, "produccion", evento_name)
    mp3_path  = os.path.join(prod_dir, f"{evento_name}.mp3")
    out_video = os.path.join(prod_dir, f"{evento_name}.mp4")
    ass_path  = None

    if not os.path.exists(mp3_path):
        print(f"❌ No se encontró el audio: {mp3_path}")
        return None

    # ── 1. Subtítulos ASS ────────────────────────────────────────────────────
    sys.path.append(os.path.dirname(__file__))
    from subtitle_generator import generate_ass
    
    ass_cached = os.path.join(prod_dir, f"{evento_name}.ass")
    if os.path.exists(ass_cached):
        print(f"💾 ASS cacheado encontrado → skip Whisper ({ass_cached})")
        ass_path = ass_cached
    else:
        print("📝 Generando subtítulos con Whisper...")
        try:
            ass_path = generate_ass(mp3_path, modelo="small",
                                     video_width=1080, video_height=1920)
        except Exception as e:
            print(f"⚠️  Whisper falló ({e}). Sin subtítulos.")

    # ── 2. Leer Storyboard y Aspecto ───────────────────────────
    guion_path      = os.path.join(prod_dir, "guion.txt")
    storyboard_path = os.path.join(prod_dir, "storyboard.txt")
    
    aspect = "conjuncion"
    if os.path.exists(guion_path):
        text = open(guion_path, encoding='utf-8').read().lower()
        if "cuadratura" in text: aspect = "cuadratura"
        elif "oposicion" in text or "oposición" in text: aspect = "oposicion"
        elif "conjuncion" in text or "conjunción" in text: aspect = "conjuncion"
        elif "sextil" in text: aspect = "sextil"
        elif "trigono" in text or "trígono" in text: aspect = "trigono"
        elif "quincuncio" in text: aspect = "quincuncio"

    print("\n🤖 Leyendo storyboard...")
    if not os.path.exists(storyboard_path):
        print("   ⚠️  No hay storyboard.txt. El buscador usará fallbacks genéricos.")


    # ── 3. Preparación de Entorno ────────────────────────────────
    print("\n🎬 Generando Arquitectura de Bóveda Offline...")

    palettes_path = os.path.join(os.path.dirname(__file__), "transit_palettes.json")
    transit_concepts = []
    if os.path.exists(palettes_path):
        import json
        with open(palettes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Find if this event is a transit (e.g. moon_in_aries) or contains it
            for t in data.get("transits", []):
                if t["name"] in evento_name.lower():
                    transit_concepts = t.get("emotional_concepts", [])
                    break

    if transit_concepts:
        print(f"   🌟 Tránsito detectado. Usando {len(transit_concepts)} conceptos puros.")
        raw_queries = [f"{evento_name.lower()} {c}" for c in transit_concepts]
    elif os.path.exists(storyboard_path):
        with open(storyboard_path) as f:
            raw_queries = [l.strip() for l in f if l.strip()]
    else:
        raw_queries = []
        
    final_queries = []
    
    # ── 4. Calcular tiempos ──────────────────────────────────────────────────
    duracion_total = get_audio_duration(mp3_path)
    dialogues: list[tuple[float, float]] = []
    
    # Leemos subtitulos
    raw_dialogues = []
    if ass_path and os.path.exists(ass_path):
        raw_dialogues = parse_ass_durations(ass_path)
        
    if not raw_dialogues:
        print("❌ Error: No se encontraron subtítulos para sincronizar.")
        return None
        
    M = len(raw_dialogues)
    
    # ── 3.5. Buscar Assets en Bóveda Local ────────────────────────────────────
    import glob, random
    VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"
    GLITCH_DIR = os.path.join(VAULT_DIR, "Glitches_Source")
    
    vault_files = glob.glob(os.path.join(VAULT_DIR, "*.*"))
    glitch_files = glob.glob(os.path.join(GLITCH_DIR, "*.*"))
    
    if not vault_files:
        print("❌ Bóveda vacía. Espera a que el Vault Scraper descargue assets.")
        return None

    num_scenes = len(raw_queries) if raw_queries else max(1, M // 3)
    scene_groups = {}
    
    for s_idx in range(num_scenes):
        scene_groups[s_idx] = []
        
        # Matching semántico: rotar entre los conceptos disponibles (raw_queries)
        if raw_queries:
            query = raw_queries[s_idx % len(raw_queries)]
        else:
            query = ""
            
        query_words = set(query.lower().replace('_', ' ').split())
        
        def score_file(f):
            filename = os.path.basename(f).lower().replace('.mp4', '').replace('.jpg', '')
            file_words = set(filename.replace('_', ' ').split())
            return len(query_words.intersection(file_words))
            
        best_files = sorted(vault_files, key=score_file, reverse=True)
        # Randomizamos ligeramente los mejores N archivos para no repetir siempre el mismo video exacto
        top_n = min(10, len(best_files))
        if top_n > 0:
            main_f = random.choice(best_files[:top_n])
        else:
            main_f = vault_files[0] if vault_files else None
            
        main_type = "video" if main_f and main_f.endswith(".mp4") else "image"
        if main_f:
            scene_groups[s_idx].append((main_f, main_type, False))
        
        # N glitch assets (determinado por num_pulses, max 4)
        db_path = os.path.join(os.path.dirname(__file__), "astrology_palettes.json")
        palettes = {}
        if os.path.exists(db_path):
            import json
            with open(db_path, "r", encoding="utf-8") as f:
                palettes = json.load(f)
                
        n_glitches = min(4, palettes.get(aspect, {}).get("num_pulses", 1))
        
        # Seleccionar glitches directamente de la bóveda de Glitches (si hay) y randomizar
        if glitch_files:
            best_glitches = sorted(glitch_files, key=score_file, reverse=True)
            top_g = min(10, len(best_glitches))
        else:
            best_glitches = best_files
            top_g = top_n
            
        for g_idx in range(n_glitches):
            g_f = random.choice(best_glitches[:max(1, top_g)]) if best_glitches else main_f
            if g_f:
                g_type = "video" if g_f.endswith(".mp4") else "image"
                scene_groups[s_idx].append((g_f, g_type, True))
            
        final_queries.append(query)
        
    queries = final_queries
    
    # Calcular los tiempos
    # Para cada frase, calculamos su duración total (hasta el inicio de la siguiente)
    final_bg_files = []
    final_queries = []
    
    # Map cada Whisper chunk i a un scene index (s_idx)
    s_idx_list = []
    num_scenes = max(scene_groups.keys()) + 1 if scene_groups else 1
    for i in range(M):
        s_idx = min(int(i * num_scenes / M), num_scenes - 1)
        s_idx_list.append(s_idx)
        
    for i in range(M):
        s = raw_dialogues[i][0]
        if i == 0: s = 0.0 # El primer clip arranca siempre en 0
        
        e = raw_dialogues[i+1][0] if i < M - 1 else duracion_total
        phrase_dur = e - s
        
        s_idx = s_idx_list[i]
        if s_idx not in scene_groups or not scene_groups[s_idx]:
            continue # Skip si no hay imagenes en este grupo
            
        # Distribuir las imágenes de la escena entre los chunks que la comparten
        chunks_sharing = [j for j in range(M) if s_idx_list[j] == s_idx]
        num_chunks = len(chunks_sharing)
        pos = chunks_sharing.index(i)
        
        group = scene_groups[s_idx]
        K_total = len(group)
        
        # Asignar un subconjunto de imágenes a este chunk específico
        imgs_per_chunk = max(1, K_total // num_chunks)
        start_idx = pos * imgs_per_chunk
        end_idx = start_idx + imgs_per_chunk
        
        if pos == num_chunks - 1:
            end_idx = K_total # El último chunk se lleva el resto
            
        my_images = group[start_idx:end_idx]
        if not my_images: 
            my_images = group # fallback seguro
            
        K = len(my_images)
        
        if K == 1:
            dialogues.append((s, e))
            final_bg_files.append(my_images[0])
            final_queries.append(queries[s_idx])
        else:
            # Edición Psicológica Prorrateada Exacta
            glitches = [x for x in my_images if x[2]]
            normals = [x for x in my_images if not x[2]]
            
            num_g = len(glitches)
            glitch_total = num_g * 0.08
            
            if glitch_total >= phrase_dur:
                # Frase demasiado corta, usamos solo 1 imagen normal
                dialogues.append((s, e))
                final_bg_files.append(normals[0] if normals else my_images[0])
                final_queries.append(queries[s_idx])
            else:
                rem_time = phrase_dur - glitch_total
                main_dur = min(2.0, rem_time * 0.6)
                num_flashes = len(normals) - 1
                if num_flashes > 0:
                    flash_dur = (rem_time - main_dur) / num_flashes
                else:
                    # Si hay una sola imagen normal, ella absorbe todo el tiempo residual
                    main_dur = rem_time
                    flash_dur = 0
                
                # Orden sugestivo: normal flash -> main -> glitch -> flash...
                ordered_group = []
                if len(normals) >= 2:
                    ordered_group.append(normals[1])
                    ordered_group.append(normals[0])
                    for j in range(2, len(normals)):
                        ordered_group.append(normals[j])
                elif len(normals) == 1:
                    ordered_group.append(normals[0])
                
                ordered_group.extend(glitches)
                
                # Para asegurar el loop perfecto sin frames negros, el último es siempre normal
                if ordered_group and ordered_group[-1][2] == True:
                    if normals:
                        ordered_group.append(normals[0])

                curr_time = s
                for j, asset in enumerate(ordered_group):
                    is_g = asset[2]
                    
                    if j == len(ordered_group) - 1:
                        # El último clip absorbe milisegundos restantes exactos para no desfasar
                        dur = e - curr_time
                    elif is_g:
                        dur = 0.08
                    elif asset == (normals[0] if normals else None):
                        dur = main_dur
                    else:
                        dur = flash_dur
                        
                    if dur >= 0.04:
                        dialogues.append((curr_time, curr_time + dur))
                        final_bg_files.append(asset)
                        final_queries.append(queries[s_idx])
                    curr_time += dur

    if dialogues and dialogues[-1][1] < duracion_total:
        last_s, last_e = dialogues[-1]
        dialogues[-1] = (last_s, duracion_total)

    bg_files = final_bg_files
    queries = final_queries
    N = len(bg_files)
    
    print(f"\\n🎞️  {M} frases mapeadas a {N} cortes dinámicos psicológicos")
    
    # Tiempos de transición (inicio de cada escena desde la 2ª) para chimes
    transition_times = [dialogues[i][0] for i in range(1, len(dialogues))]


    n_videos = sum(1 for _, t, _ in bg_files if t == "video")
    n_imgs   = len(bg_files) - n_videos

    print(f"   {n_videos} videos + {n_imgs} imágenes | Color grading astrológico | Vignette")

    # ── 5. 2-Pass FFmpeg Builder ──────────────────────────────────────────────
    print(f"\n⚡ Procesando {N} clips de forma acelerada (2-Pass)...")

    temp_dir = os.path.join(prod_dir, "temp_clips")
    os.makedirs(temp_dir, exist_ok=True)
    
    clip_files = []
    glitch_timestamps = []

    for idx, ((bg_path, bg_type, is_g), query) in enumerate(zip(bg_files, queries)):
        tipo_icon = "📹" if bg_type == "video" else "🖼️ "
        print(f"   [{idx+1}/{N}] Renderizando {tipo_icon} clip {idx:02d}...")

        start_sec, end_sec = dialogues[idx]
        clip_dur = (end_sec - start_sec) + FADE_DUR
        if is_g:
            glitch_timestamps.append(start_sec)
            
        if idx == N - 1:
            clip_dur += 2.0

        # Pass 1: Renderizar clip individual (1 a la vez) con sus filtros exactos
        clip_out = os.path.join(temp_dir, f"clip_{idx:02d}.ts") # .ts es ideal para concat rápido
        
        cmd = ["ffmpeg", "-y"]
        if bg_type == "image":
            cmd.extend(["-loop", "1", "-t", f"{clip_dur:.4f}", "-i", bg_path])
            f_scale = _kenburnspan_filter(idx, clip_dur)
        else:
            # Todos los videos deben tener stream_loop -1 para no quedar cortos por redondos matemáticos
            cmd.extend(["-stream_loop", "-1", "-t", f"{clip_dur:.4f}", "-i", bg_path])
            f_scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

        filters = [f_scale]
        filters.append(_color_filter(aspect))
        filters.append("vignette=angle=PI/4")
        
        sym = _symbol_filter(query)
        if sym:
            filters.append(sym)
            
        filters.append(f"fps={FPS},format=yuv420p,setsar=1")
        
        # Quemamos el subtítulo global con offset de tiempo (setpts) para que lea la porción correcta del ASS
        if ass_path and os.path.exists(ass_path):
            esc = _escape_filter(ass_path)
            filters.append(f"setpts=PTS+({start_sec}/TB),ass='{esc}',setpts=PTS-({start_sec}/TB)")
        
        chain = ",".join(filters)
        
        cmd.extend([
            "-vf", chain,
            "-c:v", "libx264", "-crf", "23",
            "-preset", "veryfast",
            "-aspect", "9:16",
            clip_out
        ])
        
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
             print(f"❌ Error renderizando clip {idx:02d}.")
             return None
        clip_files.append(clip_out)

    # Diseño Sonoro Empático (Capa Musical + SFX)
    sys.path.append(os.path.dirname(__file__))
    from audio_mixer import mix_frequency_layer
    guion_text = ""
    script_path = os.path.join(prod_dir, "guion.txt")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            guion_text = f.read().strip()
    words_json_path = mp3_path.replace(".mp3", "_words.json")
    mixed_path = mix_frequency_layer(mp3_path, guion_text, words_json_path, aspect, glitch_timestamps)

    # Escribir lista de clips para concatenar
    list_path = os.path.join(temp_dir, "clips.txt")
    with open(list_path, "w") as f:
        for c in clip_files:
            f.write(f"file '{os.path.basename(c)}'\n")

    print("\n🎬 Ejecutando ensamble final (Concat Instantáneo)...")
    
    # Pass 2: Pegar todos los clips sin re-codificar el video (c:v copy) y sumar el audio mixto final
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-i", mixed_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest", # Para asegurar que termina justo donde termina el clip más corto
        out_video
    ]
    
    res = subprocess.run(concat_cmd, capture_output=True, text=True, cwd=temp_dir)
    
    if res.returncode != 0:
        print(f"❌ FFmpeg error en concat:\n{res.stderr[-3000:]}")
        return None

    print(f"\n✅ ¡Video listo! → {out_video}")
    
    # ── 6. Copia a Bóveda Automática ───────────────────────────────────────────
    _copy_to_vault(evento_name, out_video)
    
    return out_video

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python video_maker.py <Nombre_Evento>")
    else:
        create_video(sys.argv[1])
