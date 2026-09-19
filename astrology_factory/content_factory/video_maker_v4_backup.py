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
FADE_DUR = 0.5

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

def _color_filter(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["scorpio", "venus", "shadow", "dark", "duality", "contrast"]):
        return ("eq=brightness=-0.07:saturation=1.4:contrast=1.2,"
                "curves=r='0/0 0.5/0.45 1/0.85':b='0/0 0.5/0.55 1/0.93'")
    elif any(k in q for k in ["balance", "harmony", "scales", "light", "warm", "golden"]):
        return ("eq=brightness=0.03:saturation=1.1:contrast=1.05,"
                "curves=r='0/0 0.5/0.58 1/1.0':g='0/0 0.5/0.52 1/0.97':"
                "b='0/0 0.5/0.42 1/0.80'")
    elif any(k in q for k in ["star", "cosmos", "space", "universe", "planet", "night"]):
        return ("eq=brightness=-0.12:saturation=1.6:contrast=1.25,"
                "curves=r='0/0 0.5/0.35 1/0.70':b='0/0 0.5/0.65 1/1.0'")
    else:
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

    # ── 2. Leer Storyboard (Generado en la sesión) ───────────────────────────
    guion_path      = os.path.join(prod_dir, "guion.txt")
    storyboard_path = os.path.join(prod_dir, "storyboard.txt")
    print("\n🤖 Leyendo storyboard...")
    if not os.path.exists(storyboard_path):
        print("   ⚠️  No hay storyboard.txt. El buscador usará fallbacks genéricos.")


    # ── 3. Descargar assets (videos/imágenes) ────────────────────────────────
    print("\n🎬 Buscando assets visuales...")
    from auto_image_finder import get_automated_background
    if not get_automated_background(evento_name, prod_dir):
        print("❌ Sin assets visuales.")
        return None

    # Leer assets encontrados (video o imagen)
    assets_dir = os.path.join(prod_dir, "assets")
    bg_files: list[tuple[str, str]] = []
    
    if os.path.exists(storyboard_path):
        with open(storyboard_path) as f:
            raw_queries = [l.strip() for l in f if l.strip()]
    else:
        raw_queries = []
        
    final_queries = []
    
    for idx in range(30):
        found_any = False
        for sub in range(5):
            mp4 = os.path.join(assets_dir, f"{idx:02d}_{sub}_bg.mp4")
            jpg = os.path.join(assets_dir, f"{idx:02d}_{sub}_bg.jpg")
            if os.path.exists(mp4):
                bg_files.append((mp4, "video"))
                found_any = True
                final_queries.append(raw_queries[idx] if idx < len(raw_queries) else "")
            elif os.path.exists(jpg):
                bg_files.append((jpg, "image"))
                found_any = True
                final_queries.append(raw_queries[idx] if idx < len(raw_queries) else "")
                
        # Compatibilidad con archivos viejos sin subindice
        if not found_any:
            mp4_old = os.path.join(assets_dir, f"{idx:02d}_bg.mp4")
            jpg_old = os.path.join(assets_dir, f"{idx:02d}_bg.jpg")
            if os.path.exists(mp4_old):
                bg_files.append((mp4_old, "video"))
                final_queries.append(raw_queries[idx] if idx < len(raw_queries) else "")
            elif os.path.exists(jpg_old):
                bg_files.append((jpg_old, "image"))
                final_queries.append(raw_queries[idx] if idx < len(raw_queries) else "")
            else:
                break

    if not bg_files:
        print("❌ No se encontraron assets.")
        return None

    queries = final_queries

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
    
    # Agrupar bg_files por idx (frase)
    import re
    scene_groups = {}
    for (f, t) in bg_files:
        m = re.search(r'(\d+)_(\d+)_bg', os.path.basename(f))
        if m:
            s_idx = int(m.group(1))
            if s_idx not in scene_groups:
                scene_groups[s_idx] = []
            scene_groups[s_idx].append((f, t))
            
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
            # Edición Psicológica: Imagen principal (index 0) tiene máx 2.5s.
            # El resto se divide entre las demás.
            main_dur = min(2.5, phrase_dur * 0.6)
            flash_dur = (phrase_dur - main_dur) / (K - 1)
            
            # Orden sugestivo: Flash 1 -> Main -> Flash 2 -> Flash 3...
            ordered_group = []
            if K >= 2:
                ordered_group.append(my_images[1])
                ordered_group.append(my_images[0])
                for j in range(2, K):
                    ordered_group.append(my_images[j])
                    
            curr_time = s
            for j, asset in enumerate(ordered_group):
                if asset == my_images[0]:
                    dur = main_dur
                else:
                    dur = flash_dur
                dialogues.append((curr_time, curr_time + dur))
                curr_time += dur
                final_bg_files.append(asset)
                final_queries.append(queries[s_idx])

    if dialogues and dialogues[-1][1] < duracion_total:
        last_s, last_e = dialogues[-1]
        dialogues[-1] = (last_s, duracion_total)

    bg_files = final_bg_files
    queries = final_queries
    N = len(bg_files)
    
    print(f"\\n🎞️  {M} frases mapeadas a {N} cortes dinámicos psicológicos")
    
    # Tiempos de transición (inicio de cada escena desde la 2ª) para chimes
    transition_times = [dialogues[i][0] for i in range(1, len(dialogues))]


    n_videos = sum(1 for _, t in bg_files if t == "video")
    n_imgs   = len(bg_files) - n_videos

    print(f"   {n_videos} videos + {n_imgs} imágenes | Color grading astrológico | Vignette")

    # ── 5. Single-Pass FFmpeg Builder ──────────────────────────────────────────
    print(f"\n⚡ Ensamblando {N} clips en una sola pasada (Single-Pass)...")

    inputs = []
    filter_chains = []
    
    for idx, ((bg_path, bg_type), query) in enumerate(zip(bg_files, queries)):
        tipo_icon = "📹" if bg_type == "video" else "🖼️ "
        print(f"   [{idx+1}/{N}] {tipo_icon} {query[:38]}… → corte limpio")

        start_sec, end_sec = dialogues[idx]
        clip_dur = (end_sec - start_sec) + FADE_DUR
        if idx == N - 1:
            clip_dur += 2.0

        if bg_type == "image":
            inputs.extend(["-loop", "1", "-t", f"{clip_dur:.4f}", "-i", bg_path])
            f_scale = _kenburnspan_filter(idx, clip_dur)
        else:
            inputs.extend(["-stream_loop", "-1", "-t", f"{clip_dur:.4f}", "-i", bg_path])
            f_scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

        filters = [f_scale]
        filters.append(_color_filter(query))
        filters.append("vignette=angle=PI/4")
        
        sym = _symbol_filter(query)
        if sym:
            filters.append(sym)
            
        filters.append(f"fps={FPS},format=yuv420p,setsar=1")
        
        chain = ",".join(filters)
        filter_chains.append(f"[{idx}:v]{chain}[v{idx}]")
        
    # Diseño Sonoro Empático
    sys.path.append(os.path.dirname(__file__))
    from audio_mixer import mix_frequency_layer
    guion_text = ""
    script_path = os.path.join(prod_dir, "guion.txt")
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            guion_text = f.read().strip()
    words_json_path = mp3_path.replace(".mp3", "_words.json")
    mixed_path = mix_frequency_layer(mp3_path, guion_text, words_json_path)
    
    inputs.extend(["-i", mixed_path])
    audio_idx = N
    
    concat_inputs = "".join([f"[v{i}]" for i in range(N)])
    filter_chains.append(f"{concat_inputs}concat=n={N}:v=1:a=0[vconcat]")
    video_out = "[vconcat]"
    
    if ass_path and os.path.exists(ass_path):
        esc = _escape_filter(ass_path)
        filter_chains.append(f"{video_out}ass='{esc}'[vout]")
        map_video = "[vout]"
    else:
        map_video = video_out
        
    complex_filter = ";".join(filter_chains)
    
    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", complex_filter,
        "-map", map_video,
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-crf", "23",
        "-maxrate", "2500k", "-bufsize", "5000k",
        "-preset", "veryfast",
        "-c:a", "aac", "-pix_fmt", "yuv420p",
        out_video
    ]
    
    print("\n🎬 Ejecutando render final en FFmpeg...")
    # Log cmd to file
    with open("ffmpeg_cmd_debug.sh", "w") as f:
        f.write(" ".join(cmd))
    
    with open("ffmpeg_run.log", "w") as log_file:
        result = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    
    if result.returncode != 0:
        with open("ffmpeg_run.log", "r") as log_file:
            err = log_file.read()
        print(f"❌ FFmpeg error:\n{err[-3000:]}")
        if ass_path and "ass" in err.lower():
            print("⚠️  Reintentando sin subtítulos...")
            filter_chains.pop() # remove ass
            map_video = video_out
            complex_filter = ";".join(filter_chains)
            cmd = [
                "ffmpeg", "-y", *inputs,
                "-filter_complex", complex_filter,
                "-map", map_video, "-map", f"{audio_idx}:a",
                "-c:v", "libx264", "-crf", "23", "-maxrate", "2500k", "-bufsize", "5000k",
                "-preset", "veryfast", "-c:a", "aac", "-pix_fmt", "yuv420p",
                out_video
            ]
            r2 = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if r2.returncode != 0:
                print(f"❌ Fallo definitivo: {r2.stderr[-3000:]}")
                return None
        else:
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
