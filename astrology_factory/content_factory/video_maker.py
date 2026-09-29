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
import json as _json_hist
from datetime import datetime, timedelta

FPS          = 25
XFADE_DUR     = 0.40  # Crossfade de 0.4s: dissolve suave, ambas imágenes superpuestas
FADE_DUR     = XFADE_DUR  # CRÍTICO: igual a XFADE_DUR para que video == audio matemáticamente
MAX_IMAGE_DUR = 3.0   # 3s por clip = 2.6s visibles + 0.4s crossfade (el viewer ve 2.6s limpios)
MAX_VIDEO_DUR = 5.0   # Videos: 5s por clip = 4.6s visibles + 0.4s crossfade
MIN_CLIP_DUR  = XFADE_DUR + 0.4  # Mínimo para que el crossfade tenga margen (0.8s)
MAX_CLIPS_PER_SCENE = 10  # Límite superior de clips por escena (auto-fill hasta este tope)

# ── Memoria Persistente de Assets ────────────────────────────────────────────
# Reemplaza el set volátil anterior. Persiste entre renders para evitar
# repetición entre días consecutivos con el mismo tránsito (ej: Lunes→Martes).
VAULT_HISTORY_PATH = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/historial_uso_assets.json"
HISTORY_WINDOW_HOURS = 168  # 7 días = 1 ciclo semanal completo de contenido
PENALIZACION_RECIENTE = -50.0  # Penalización blanda: permite reuso si no hay alternativa

# Cache en memoria para el render actual (no duplicar dentro del mismo video)
_assets_usados_en_render: set = set()

def _load_history() -> dict:
    """Carga el historial persistente {basename: iso_timestamp}."""
    if os.path.exists(VAULT_HISTORY_PATH):
        try:
            with open(VAULT_HISTORY_PATH, "r", encoding="utf-8") as _hf:
                return _json_hist.load(_hf)
        except Exception:
            return {}
    return {}

def _save_history(history: dict):
    """Guarda historial, limpiando entradas más viejas de 14 días (2 ciclos semanales).
    Esto mantiene el archivo liviano sin borrar datos aún relevantes."""
    cutoff = datetime.utcnow() - timedelta(days=14)
    cleaned = {k: v for k, v in history.items()
               if datetime.fromisoformat(v) > cutoff}
    os.makedirs(os.path.dirname(VAULT_HISTORY_PATH), exist_ok=True)
    with open(VAULT_HISTORY_PATH, "w", encoding="utf-8") as _hf:
        _json_hist.dump(cleaned, _hf, indent=2)

def _mark_used(filepath: str, history: dict):
    """Registra un asset como usado ahora mismo (en memoria y en disco)."""
    _assets_usados_en_render.add(filepath)
    history[os.path.basename(filepath)] = datetime.utcnow().isoformat()

def _is_recently_used(filepath: str, history: dict) -> bool:
    """True si el asset fue usado en la ventana de HISTORY_WINDOW_HOURS."""
    basename = os.path.basename(filepath)
    if basename not in history:
        return False
    used_at = datetime.fromisoformat(history[basename])
    return (datetime.utcnow() - used_at) < timedelta(hours=HISTORY_WINDOW_HOURS)

# Mapeo Guion → Arquetipo Visual (para los 5 frases del guion astrológico)
# La clave es el índice de frase (0-4), el valor es la categoría de triada a priorizar
PHRASE_TO_ARCHETYPE = {
    0: "esoteric_art",    # Frase 1: Contexto duro  → símbolo planetario, zodiaco, astronomía
    1: "raw_realism",     # Frase 2: Teoría/Historia → naturaleza real, océano, sombras
    2: "abstract_glitch", # Frase 3: Mecánica        → texturas, fractales, glitch
    3: "raw_realism",     # Frase 4: Sugestión íntima → personas reales, manos, ojos
    4: "cta_portal",      # Frase 5: CTA             → portal cósmico, neon, gateway
}
# Keywords de búsqueda para el CTA (no está en las triadas JSON)
_CTA_KEYWORDS = {"portal", "cosmic", "neon", "gateway", "glow", "cta", "link", "universe", "nebula"}

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

# Tabla de transiciones xfade por aspecto astrológico
# Devuelve (transition_name, duration_sec)
_ASPECT_TRANSITIONS = {
    "conjuncion":  ("dissolve",   0.40),  # Fusión, unión lenta
    "trigono":     ("fade",       0.50),  # Flujo armónico
    "sextil":      ("pixelize",   0.30),  # Oportunidad que aparece
    "cuadratura":  ("fadeblack",  0.20),  # Tensión, corte agresivo
    "oposicion":   ("slideleft",  0.30),  # Polaridad, fuerzas opuestas
    "quincuncio":  ("pixelize",   0.25),  # Ajuste incómodo
}

def _get_transition(aspect: str, query_to: str) -> tuple[str, float]:
    """Retorna (xfade_type, XFADE_DUR) según aspecto astrológico.
    
    REGLA: La duración SIEMPRE es XFADE_DUR (constante global) para mantener
    el timing matemático correcto (FADE_DUR = XFADE_DUR en los clips).
    Solo varía el TIPO de transición según el aspecto.
    
    NO aplicar override por keywords de escena — fadeblack crea negro entre
    imágenes, que es exactamente lo que el usuario NO quiere. El aspecto
    astrológico es la única variable para el tipo de transición.
    """
    base_transition, _ = _ASPECT_TRANSITIONS.get(aspect, ("dissolve", XFADE_DUR))
    return (base_transition, XFADE_DUR)


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

def _smart_movement_filter(idx: int, clip_dur: float, query: str) -> str:
    OW, OH = 1080, 1920
    q = query.lower()
    
    # Evaluar la energía de la escena
    es_dinamica = any(k in q for k in ["mars", "uranus", "fire", "action", "tension", "sudden", "strike", "anger", "fast"])
    
    # Zoom muy sutil para no marear ni perder detalle
    zoom_max = 1.04 if es_dinamica else 1.02
    iw, ih = int(OW * zoom_max), int(OH * zoom_max)
    D = f"{clip_dur:.4f}"
    
    # Variar el tipo de movimiento según si es dinámica o no
    if not es_dinamica:
        # Energía calmada: Zoom microscópico 1.01, sin paneo
        x = f"(in_w-{OW})/2"
        y = f"(in_h-{OH})/2"
    else:
        # Energía dinámica: Zoom levísimo 1.03, sin paneo lateral (solo centrado)
        x = f"(in_w-{OW})/2"
        y = f"(in_h-{OH})/2"
        
    return f"scale={iw}:{ih}:force_original_aspect_ratio=increase,crop={OW}:{OH}:x='{x}':y='{y}'"


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
    global _assets_usados_en_render
    _assets_usados_en_render = set()  # Limpiar cache en-memoria en cada render
    _uso_history = _load_history()    # Cargar historial persistente cross-render
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
    import glob
    VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"
    GLITCH_DIR = os.path.join(VAULT_DIR, "Glitches_Source")

    vault_files = glob.glob(os.path.join(VAULT_DIR, "*.*"))
    glitch_files = glob.glob(os.path.join(GLITCH_DIR, "*.*"))

    # Filtro robusto: os.path.isfile() sigue symlinks y verifica existencia real.
    # Mínimo 50KB para descartar thumbs corruptos. Excluir frames temporales.
    valid_vault_files = [
        f for f in vault_files
        if os.path.isfile(f)              # sigue symlinks → descarta rotos
        and os.path.getsize(f) > 50_000  # mínimo 50KB
        and not f.endswith("_frame.jpg")  # excluir frames temporales de scoring
    ]
    
    if not valid_vault_files:
        print("❌ Bóveda vacía. Espera a que el Vault Scraper descargue assets.")
        return None

    num_scenes = len(raw_queries) if raw_queries else max(1, M // 3)
    scene_groups = {}
    
    # Número total de frases del guión (por defecto 5)
    N_PHRASES = 5

    # ── Detectar tránsito activo: buscar en múltiples fuentes (orden de prioridad) ──
    # El nombre del evento (ej: "Semana3_Octubre_Lunes") no contiene el tránsito.
    # Las fuentes correctas son: transito.txt, guion.txt, storyboard.txt.
    import json as _json
    _transit_triads_by_cat: dict[str, list[str]] = {}
    _transit_emotional: list[str] = []
    _storyboard_keywords: set = set()  # keywords directas del storyboard para scoring fallback

    # Construir corpus de texto del evento desde guion + storyboard + transito.txt
    _event_corpus = evento_name.lower().replace("_", " ")
    for _src_name in ["transito.txt", "guion.txt", "storyboard.txt"]:
        _src_path = os.path.join(prod_dir, _src_name)
        if os.path.exists(_src_path):
            with open(_src_path, "r", encoding="utf-8") as _sf:
                _txt = _sf.read().lower()
                _event_corpus += " " + _txt
                # Extraer keywords del storyboard (las palabras del id: y descripción)
                if _src_name == "storyboard.txt":
                    for _line in _txt.splitlines():
                        _line = _line.strip()
                        if _line.startswith("["):
                            # Limpiar negaciones y marcadores
                            _clean = _line.replace("-animal","").replace("-cartoon","").replace("-cute","").replace("-vector","").replace("-character","").replace("-kids","")
                            _words = set(_clean.replace("|","").replace("_"," ").split())
                            _storyboard_keywords |= {w for w in _words if len(w) > 3}

    palettes_path_vm = os.path.join(os.path.dirname(__file__), "transit_palettes.json")
    if os.path.exists(palettes_path_vm):
        with open(palettes_path_vm, "r", encoding="utf-8") as _pf:
            _pdata = _json.load(_pf)
        _best_match_score = 0
        _best_transit = None
        for _t in _pdata.get("transits", []):
            # Contar cuántas palabras del nombre del tránsito aparecen en el corpus
            _twords = [w for w in _t["name"].lower().split("_") if len(w) > 2]
            _match_count = sum(1 for w in _twords if w in _event_corpus)
            if _match_count > _best_match_score:
                _best_match_score = _match_count
                _best_transit = _t
        if _best_transit:
            _transit_emotional = _best_transit.get("emotional_concepts", [])
            _at = _best_transit.get("artistic_triads", {})
            for _cat in ["raw_realism", "esoteric_art", "abstract_glitch"]:
                _transit_triads_by_cat[_cat] = _at.get(_cat, [])
            print(f"   🔭 Tránsito detectado: {_best_transit['name']} (score={_best_match_score})")
        else:
            print("   ⚠️  No se encontró tránsito en JSON. Usando keywords del storyboard para scoring.")

    def score_file_v2(f: str, query_words: set, archetype_cat: str = "",
                      scene_id: str = "") -> float:
        """Scoring NARRATIVO — la escena específica manda. (Diagnóstico v5)

        PIRÁMIDE INVERTIDA (la coherencia del relato domina sobre el tránsito):
        +50  Match exacto de ID de escena en el filename
        +10  Palabras de la escena específica que está sonando
        + 5  Arquetipo de frase (raw_realism / esoteric_art / etc.)
        + 2  Conceptos del tránsito (ahora contexto/fallback)
        + 4  Bonus de recencia mtime (tiebreaker cuando la bóveda está saturada)
        -50  Asset usado en las últimas 168h (penalización blanda cross-render)
        -100 Asset ya usado en ESTE render (descarte dentro del video)
        """
        filename = os.path.basename(f).lower()
        filename_noext = filename.replace(".mp4", "").replace(".jpg", "").replace(".png", "")
        file_words = set(filename_noext.replace("_", " ").replace("-", " ").split())

        score = 0.0

        # ── Nivel 0 (+50): Match exacto de ID de escena ──────────────────────
        # Si el filename contiene el ID de storyboard (ej: scorpio_symbol_dark),
        # es una imagen descargada PARA esta escena → máxima prioridad.
        if scene_id and scene_id.strip():
            sid_words = set(scene_id.lower().replace("_", " ").split())
            if len(sid_words) > 1 and sid_words <= file_words:  # subset exacto
                score += 50.0
            elif sid_words & file_words:  # match parcial del ID
                score += 25.0

        # ── Nivel 1 (+10/palabra): Palabras de la ESCENA ESPECÍFICA ──────────
        # La narrativa local es la ley. Esto era Nivel 5 con +1 → ahora es el rey.
        scene_matches = query_words & file_words
        score += float(len(scene_matches)) * 10.0

        # ── Nivel 2 (+5): Arquetipo de la frase ──────────────────────────────
        if archetype_cat and archetype_cat != "cta_portal":
            for kw in _transit_triads_by_cat.get(archetype_cat, []):
                twords = set(kw.lower().split())
                if twords & file_words:
                    score += 5.0
        if archetype_cat == "cta_portal":
            if _CTA_KEYWORDS & file_words:
                score += 5.0

        # ── Nivel 3 (+2): Conceptos del tránsito (ahora solo contexto/fallback) ──
        # Reducido de +3 a +2, y ya NO es el nivel dominante.
        for concept in _transit_emotional:
            cwords = set(concept.lower().split())
            if cwords & file_words:
                score += 2.0
        # Triadas generales del tránsito (fallback)
        for _cat_triads in _transit_triads_by_cat.values():
            for triad in _cat_triads:
                twords = set(triad.lower().split())
                if twords & file_words:
                    score += 1.0  # Reducido: solo guía suave

        # ── Penalización cross-render: usado en las últimas 72h (-50) ─────────
        # Blanda: permite reuso si la bóveda está vacía, pero prioriza material fresco.
        if _is_recently_used(f, _uso_history):
            score += PENALIZACION_RECIENTE

        # ── Penalización in-render: ya usado en ESTE video (-100) ─────────────
        if f in _assets_usados_en_render:
            score -= 100.0

        # ── Penalización absoluta a basura/mundano (-1000) ─────────────
        garbage_words = {"baby", "babies", "bebé", "niño", "niña", "kid", "kids", "child", "children", "toddler", "family", "funny", "dog", "cat", "pet", "home", "casual", "cute", "meme", "vlog"}
        if garbage_words & file_words:
            score -= 1000.0

        return score

    for s_idx in range(num_scenes):
        scene_groups[s_idx] = []

        # Determinar qué frase del guión corresponde a esta escena (0-4)
        phrase_idx = min(int(s_idx * N_PHRASES / num_scenes), N_PHRASES - 1)
        archetype_cat = PHRASE_TO_ARCHETYPE.get(phrase_idx, "")

        # Matching semántico: rotar entre los conceptos disponibles (raw_queries)
        if raw_queries:
            query = raw_queries[s_idx % len(raw_queries)]
        else:
            query = ""

        # Extraer scene_id: si el query tiene formato "[id] descripcion", extraemos el id
        scene_id = ""
        _q_stripped = query.strip()
        if _q_stripped.startswith("["):
            _bracket_end = _q_stripped.find("]")
            if _bracket_end > 0:
                scene_id = _q_stripped[1:_bracket_end].strip()
                query = _q_stripped[_bracket_end+1:].strip()

        query_words = set(query.lower().replace("_", " ").split())

        # Ordenar por score NARRATIVO — la escena específica manda (Diagnóstico v5)
        best_files = sorted(
            valid_vault_files,
            key=lambda f: score_file_v2(f, query_words, archetype_cat, scene_id),
            reverse=True
        )

        # Tomar los primeros MAX_CLIPS_PER_SCENE únicos no usados EN ESTE render
        # Más clips en el grupo = el auto-fill de frases largas tiene material de donde elegir
        selected_files = []
        for f in best_files:
            if f not in _assets_usados_en_render:
                selected_files.append(f)
                if len(selected_files) >= MAX_CLIPS_PER_SCENE:
                    break
        # Fallback: si todos ya fueron usados en este render, tomar los mejores rankeados
        if not selected_files:
            selected_files = best_files[:MAX_CLIPS_PER_SCENE]

        for main_f in selected_files:
            _mark_used(main_f, _uso_history)
            main_type = "video" if main_f.endswith(".mp4") else "image"
            scene_groups[s_idx].append((main_f, main_type, False))

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
            # Edición Astrológica: calcular cuántas imágenes NECESITA esta frase.
            # Regla de densidad: corte cada MAX_IMAGE_DUR segundos como máximo.
            # Si phrase_dur=12s y MAX_IMAGE_DUR=3s → necesitamos mínimo 4 clips.
            clips_needed = max(1, int(phrase_dur / MAX_IMAGE_DUR) + 1)
            max_fitting = max(1, int(phrase_dur / MIN_CLIP_DUR))
            effective_K = min(K, min(clips_needed, max_fitting))

            # ── AUTO-FILL: si la frase necesita más clips de los que tiene el grupo ──
            # Pedir más clips a la bóveda con el mismo query semántico de la escena.
            if clips_needed > K and len(valid_vault_files) > K:
                _q_words_local = set(queries[s_idx].lower().replace("_", " ").split())
                _extra_candidates = sorted(
                    valid_vault_files,
                    key=lambda ff: score_file_v2(ff, _q_words_local,
                                                  PHRASE_TO_ARCHETYPE.get(
                                                      min(int(s_idx * N_PHRASES / num_scenes), N_PHRASES - 1), ""
                                                  )),
                    reverse=True
                )
                _extra_added = 0
                for _ef in _extra_candidates:
                    if _extra_added >= (clips_needed - K):
                        break
                    if _ef not in _assets_usados_en_render and _ef not in [x[0] for x in my_images]:
                        _ef_type = "video" if _ef.endswith(".mp4") else "image"
                        my_images.append((_ef, _ef_type, False))
                        _mark_used(_ef, _uso_history)
                        _extra_added += 1
                K = len(my_images)
                effective_K = min(K, clips_needed)

            normals = my_images[:effective_K]
            effective_K = len(normals)

            # Distribuir equitativamente — sin cap de MAX_IMAGE_DUR en la asignación inicial:
            # el cap se aplica clip a clip para que el sobrante se redistribuya en el siguiente.
            dur_per_img = phrase_dur / effective_K
            curr_time = s

            for j, asset in enumerate(normals):
                bg_path_j, bg_type_j, _ = asset
                cap = MAX_VIDEO_DUR if bg_type_j == "video" else MAX_IMAGE_DUR

                if j == effective_K - 1:
                    # Último slot: absorbe remanente (mantiene audio sync)
                    dur = e - curr_time
                    # Si el remanente es exageradamente largo (>cap*1.5), partir en dos
                    if dur > cap * 1.5 and len(normals) < MAX_CLIPS_PER_SCENE:
                        # Reciclar el mismo asset una vez más para llenar el hueco
                        mid = curr_time + cap
                        dialogues.append((curr_time, mid))
                        final_bg_files.append(asset)
                        final_queries.append(queries[s_idx])
                        curr_time = mid
                        dur = e - curr_time
                    
                    dialogues.append((curr_time, curr_time + dur))
                    final_bg_files.append(asset)
                    final_queries.append(queries[s_idx])
                    curr_time += dur
                else:
                    dur = min(dur_per_img, cap)
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
    calculated_clip_durs = []
    glitch_timestamps = []

    for idx, ((bg_path, bg_type, is_g), query) in enumerate(zip(bg_files, queries)):
        tipo_icon = "📹" if bg_type == "video" else "🖼️ "
        print(f"   [{idx+1}/{N}] Renderizando {tipo_icon} clip {idx:02d}...")

        start_sec, end_sec = dialogues[idx]
        clip_dur = (end_sec - start_sec) + FADE_DUR
            
        if idx == N - 1:
            clip_dur += 2.0
            
        calculated_clip_durs.append(clip_dur)

        # Pass 1: Renderizar clip individual con sus filtros exactos
        # Usamos .mkv en lugar de .ts para compatibilidad con xfade en Pass 2
        clip_out = os.path.join(temp_dir, f"clip_{idx:02d}.mkv")
        
        cmd = ["ffmpeg", "-y"]
        if bg_type == "image":
            cmd.extend(["-loop", "1", "-t", f"{clip_dur:.4f}", "-i", bg_path])
            f_scale = _smart_movement_filter(idx, clip_dur, query)
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
            "-x264-params", "bframes=0:keyint=25", # Previene marcos negros en la concatenación de .ts
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

    print("\n🎬 Ejecutando ensamble final con crossfades astrológicos (xfade {XFADE_DUR}s)...")

    # Pass 2: Concat con xfade real — crossfade de 1s entre TODOS los clips
    # El crossfade simultáneo evita frames negros y funde las imágenes suavemente.
    xf_name, _xf_base = _get_transition(aspect, queries[0] if queries else "")
    n_clips = len(clip_files)

    if n_clips == 1:
        # Clip único: no hay transición, pass directo
        concat_cmd = [
            "ffmpeg", "-y",
            "-i", clip_files[0],
            "-i", mixed_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", out_video
        ]
    else:
        # Construir filter_complex con xfade encadenado entre todos los clips
        # Usamos las duraciones calculadas matemáticamente en Pass 1 para precisión Gapless
        clip_durs = calculated_clip_durs

        # xfade siempre a XFADE_DUR (1.0s) — crossfade simultáneo que funde suavemente
        filter_parts = []
        last_label = "[0:v]"
        cumulative = 0.0
        for i in range(1, n_clips):
            # La transición de cada clip puede tener override oscuro (fadeblack)
            # pero la DURACIÓN siempre es XFADE_DUR para mantener coherencia editorial
            q_i = queries[i] if i < len(queries) else ""
            xf_i, _ = _get_transition(aspect, q_i)  # solo usamos el tipo, no la dur base
            xf_d_i = XFADE_DUR  # duración fija: 1.0s siempre
            offset = max(0.05, cumulative + clip_durs[i - 1] - xf_d_i)
            out_label = f"[v{i}]" if i < n_clips - 1 else "[vout]"
            filter_parts.append(
                f"{last_label}[{i}:v]xfade=transition={xf_i}:duration={xf_d_i:.3f}:offset={offset:.4f}{out_label}"
            )
            last_label = out_label
            cumulative += clip_durs[i - 1] - xf_d_i

        fc = "; ".join(filter_parts)

        # Construir inputs
        concat_cmd = ["ffmpeg", "-y"]
        for cf in clip_files:
            concat_cmd.extend(["-i", cf])
        concat_cmd.extend(["-i", mixed_path])
        concat_cmd.extend([
            "-filter_complex", fc,
            "-map", "[vout]",
            "-map", f"{n_clips}:a:0",
            "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
            "-pix_fmt", "yuv420p",   # forzar pixel format uniforme → evita errores xfade
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            out_video
        ])
        print(f"   \u2728 Crossfade {xf_i} {XFADE_DUR}s × {n_clips-1} transiciones [{aspect.upper()}]")

    res = subprocess.run(concat_cmd, capture_output=True, text=True, cwd=temp_dir)

    if res.returncode != 0:
        print(f"⚠️  xfade falló (posible incompatibilidad de pixel format). Reintentando con concat simple...")
        # Fallback: concat clásico sin transición si xfade falla
        list_path = os.path.join(temp_dir, "clips.txt")
        with open(list_path, "w") as lf:
            for c in clip_files:
                lf.write(f"file '{os.path.basename(c)}'\n")
        fallback_cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-i", mixed_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", out_video
        ]
        res = subprocess.run(fallback_cmd, capture_output=True, text=True, cwd=temp_dir)
        if res.returncode != 0:
            print(f"❌ FFmpeg error en concat:\n{res.stderr[-3000:]}")
            return None

    print(f"\n✅ ¡Video listo! → {out_video}")
    
    # ── 6. Persistir historial de uso de assets ──────────────────────────────
    _save_history(_uso_history)
    print(f"💾 Historial de assets actualizado ({len(_uso_history)} entradas).")

    # ── 7. Copia a Bóveda Automática ───────────────────────────────────────────
    _copy_to_vault(evento_name, out_video)
    
    return out_video

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python video_maker.py <Nombre_Evento>")
    else:
        create_video(sys.argv[1])
