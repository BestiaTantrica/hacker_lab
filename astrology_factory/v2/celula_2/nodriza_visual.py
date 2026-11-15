#!/usr/bin/env python3
"""
🌓 CÉLULA MADRE 2.0 — LA NODRIZA VISUAL  (v3 · DB-first · zero-render)

Rol único: DECIDIR qué asset visual va en cada corte de cada toma.
NO renderiza, NO transmuta, NO escribe MP4/JPG temporales.

  Fuente de verdad semántica : v2/db_visual.py  (assets_visuales.db, estado='aprobado')
  Fuente de rutas/directorios: contexto_astrologico.json
  Salida                     : <paths.temp>/lista_de_corte_<evento_id>.json
                               → validador_de_ensamble.py → lista_de_corte_validada_<evento_id>.json
                               → content_factory/video_maker.py (FFmpeg Builder, single-pass)

Contrato de salida (cada elemento de "asignaciones"):
  Campos históricos (los consume validador_de_ensamble.py):
      num_toma, rol, inicio_ms, fin_ms, duracion_ms, duracion_s, texto, etiqueta_visual,
      emocion, transicion_entrada, archivo_video, nombre_video, fuente_asignacion,
      requiere_loop, accion_ffmpeg
      · archivo_video = ruta ABSOLUTA del asset ORIGINAL (jpg/png/mp4) elegido como protagonista.
  Campo nuevo:
      cortes: [ {orden, asset_id, archivo, nombre, tipo("imagen"|"video"), duracion_s,
                 es_iconica, reverse, transicion_entrada}, ... ]
      · archivo = ruta ABSOLUTA original. Si es JPG/PNG, video_maker aplica zoompan al vuelo.

Historial de uso (rotación de stock): consolidado en assets_visuales.db (tabla stats_uso).
vault_catalog.json queda deprecado — la SQLite es la ÚNICA fuente de verdad.
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import google.genai as genai

from v2 import db_visual

# ── Director de Arte (semántica local, sin API) ────────────────────────────
from v2.celula_2.director_de_arte import (
    enriquecer_tomas,
    score_semantico,
)
from v2.celula_2.prompt_semantico import elegir_mejor_asset_con_gemini

# ── ADN: única fuente de rutas ───────────────────────────────────────────────
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID        = ADN["produccion"]["evento_id"]
SEMANA           = ADN["produccion"]["semana_prefijo"]
PATHS            = ADN["assets"]["paths"]
ASSETS_AUDITADOS = Path(PATHS["assets_auditados"])
TIMELINE_DIR     = Path(PATHS["timeline_huecos"])
TEMP_DIR         = Path(PATHS["temp"])
ELEMENTO_ADN     = ADN.get("arquetipos", {}).get("elemento", "")

FORMATOS_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
FORMATOS_IMG   = {".jpg", ".jpeg", ".png", ".webp"}
_VALIDOS_ADN   = {f".{e.lower().lstrip('.')}" for e in ADN.get("validaciones", {}).get("formatos_validos", [])}
FORMATOS_ACEPTADOS = (FORMATOS_VIDEO | FORMATOS_IMG) & _VALIDOS_ADN if _VALIDOS_ADN else (FORMATOS_VIDEO | FORMATOS_IMG)
MIN_SIZE_BYTES = int(ADN.get("validaciones", {}).get("min_size_bytes", 0))

TRANSICION_INTRA_TOMA = "dissolve"   # disolución suave y onírica entre cortes para sugestión positiva

BLOQUEADOS = {
    "familia", "bebe", "family", "baby", "niño", "niña", "hogar", "niños", "pareja",
    "couple", "boda", "wedding", "multitud", "crowd", "niñez", "child"
}
BLOQUEADOS_REDES = {
    "desnudo", "desnuda", "nude", "nudity", "torso_desnudo", "cuerpo_desnudo",
    "anatomia_expuesta", "genital", "pezon", "pezones", "sensual", "erotico", "erotica",
    "tanga", "calzon", "calzones", "lenceria", "ropa_interior", "descartes", "descartes_exploratorios",
    "lilith_v", "lilith_v1", "lilith_v2", "lilith_v3", "lilith_v4", "lilith_v5", "lilith_v6",
    "seno", "senos", "anadyomene", "reclinada", "contrapposto", "desnudez",
    "gluteo", "gluteos", "nalga", "nalgas", "torso_manos", "ferri_sin_disco", "fetal"
}

# ── Taxonomía Visual para Rotación y Diversidad de Tomas ──
CATEGORIA_FIGURA_HUMANA = {
    "escultura", "estatua", "busto", "mano", "rostro", "brazo", "figura",
    "soberano", "dios", "arquetipo", "guardian", "anciano", "guerrero", "personaje",
    "imposicion", "manos", "rostro_soberano", "hombre", "mujer",
    "humano", "humanos", "persona", "personas", "retrato", "retratos",
    "emocion", "emociones", "mirada", "ojos", "sabio", "alquimista", "sacerdote",
    "figura_humana", "durmiente", "perfil"
}
CATEGORIA_SIMBOLO = {
    "simbolo", "sigilo", "tarot", "carta", "orbe", "circulo",
    "mandala", "geometria", "sello", "alquimia", "disco"
}
CATEGORIA_PAISAJE = {
    "paisaje", "montaña", "bosque", "desierto", "cielo", "mar", "oceano",
    "templo", "horizonte", "portal", "cosmos", "espacio", "universo",
    "nebulosa", "estrellas", "galaxia", "abismo"
}
CATEGORIA_ELEMENTO = {
    "fuego", "agua", "humo", "plasma", "rayo", "vortice", "calor",
    "fluido", "ceniza", "onda", "niebla", "energia"
}

def obtener_familia_asset(nombre: str) -> str:
    """
    Extrae la familia o prompt base de un asset para evitar variantes casi idénticas en el mismo video.
    Limpia sufijos de timestamps, números de iteración, '_variante', '_var', '_alt', etc.
    """
    stem = Path(nombre).stem.lower()
    stem = re.sub(r'_(variante|var|alt|version|v\d+)', '', stem)
    stem = re.sub(r'_\d{6,}(_\d+)*$', '', stem)
    stem = re.sub(r'(_\d+){1,3}$', '', stem)
    stem = re.sub(r'_(variante|var|alt|version|v\d+)', '', stem)
    return stem.strip('_')

FORZAR_ACTIVO = "--forzar" in sys.argv

def clasificar_categoria_asset(haystack: str) -> str:
    tokens = _tokens(haystack)
    if tokens & CATEGORIA_PAISAJE:
        return "paisaje"
    if tokens & CATEGORIA_FIGURA_HUMANA:
        return "figura_humana"
    if tokens & CATEGORIA_ELEMENTO:
        return "elemento"
    if tokens & CATEGORIA_SIMBOLO:
        return "simbolo"
    return "general"

PALABRAS_ICONICAS = (
    "tarot", "carta", "simbolo", "dios", "persona", "planeta",
    "arquetipo", "astrologia", "signo", "constelacion",
)
TERMINOS_GANCHO = ("vórtice", "tunel", "túnel", "viaje", "explosión", "agujero", "estallido")

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# ── Clientes Multiplexados (Hydra) ─────────────────────────────────────────

def inicializar_clientes_gemini() -> list:
    """Crea un cliente por cada GEMINI_API_KEY* distinta. Se llama SOLO al ejecutar la Nodriza."""
    keys = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and "_WEB" not in k and v]
    keys = list(dict.fromkeys(keys))  # sin duplicados, conserva orden
    clientes = []
    for key in keys:
        try:
            clientes.append(genai.Client(api_key=key))
        except Exception:
            pass
    if not clientes:
        err("No se encontraron llaves de API de Gemini válidas en .env")
        sys.exit(1)
    return clientes

# ── Lectura del timeline ─────────────────────────────────────────────────────

def cargar_timeline() -> dict:
    ruta = TIMELINE_DIR / f"{EVENTO_ID}.json"
    if not ruta.exists():
        err(f"Timeline no encontrado: {ruta}")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# ── A. Catálogo semántico: 100% SQLite ───────────────────────────────────────

def _tokens(texto: str) -> set:
    """Palabras sueltas de un texto; los guiones bajos del auditor ('agua_oscura') separan palabras."""
    return set(re.findall(r"[a-záéíóúüñ0-9]+", texto.lower().replace("_", " ")))

def cargar_catalogo_desde_db() -> dict:
    """
    Construye el catálogo en memoria SOLO desde db_visual (estado='aprobado').
    No recorre directorios, no infiere etiquetas por nombre de archivo, no lee .json sidecar.
    Un asset aprobado cuyo archivo ya no existe en disco se descarta (integridad, no búsqueda).

    Clave del catálogo (asset_id) = nombre de archivo; si dos archivos comparten nombre,
    se desambigua como '<carpeta>/<nombre>'.
    """
    filas = db_visual.obtener_todos_los_assets_aprobados()
    if not filas:
        err("db_visual no tiene assets 'aprobado'. Ejecuta primero el auditor de bóveda.")
        sys.exit(1)

    usos_db = db_visual.obtener_todos_los_usos()
    validos, descartados = [], 0
    for ruta, etiquetas in filas:
        p = Path(ruta)
        if (p.suffix.lower() not in FORMATOS_ACEPTADOS
                or p.name.endswith("_frame.jpg")
                or "descartes_exploratorios" in str(p)
                or not p.is_file()
                or (MIN_SIZE_BYTES and p.stat().st_size < MIN_SIZE_BYTES)):
            descartados += 1
            continue
        validos.append((p, etiquetas or ""))

    conteo = {}
    for p, _ in validos:
        conteo[p.name] = conteo.get(p.name, 0) + 1

    cat = {}
    for p, etiquetas in validos:
        asset_id = p.name if conteo[p.name] == 1 else f"{p.parent.name}/{p.name}"
        tags = [t.strip() for t in etiquetas.split(",") if t.strip()]
        ruta_abs = str(p.resolve())
        stats_uso = [e for e in usos_db.get(asset_id, []) if e != EVENTO_ID]  # re-render idempotente
        haystack = " ".join(tags + [ruta_abs]).lower()

        # Filtro estricto de moderación para redes sociales (cero desnudos, cero ban en IG/TikTok)
        if any(k in haystack for k in BLOQUEADOS_REDES) or bool(_tokens(haystack) & BLOQUEADOS):
            descartados += 1
            continue

        cat[asset_id] = {
            "path_original":    ruta_abs,
            "path_video_final": ruta_abs,   # clave legada: prompt_semantico.py la exige no vacía (ya NO es un MP4 transmutado)
            "tipo":             "video" if p.suffix.lower() in FORMATOS_VIDEO else "imagen",
            "tags":             tags,
            "etiquetas_visuales": tags,
            "stats_uso":        stats_uso,
            # cachés de scoring (prefijo _ → nunca se envían a Gemini ni al JSON)
            "_bloqueado":       False,
            "_bloqueado_redes": False,
            "_iconica":         any(w in haystack for w in PALABRAS_ICONICAS),
            "_haystack":        haystack,
            "_categoria":       clasificar_categoria_asset(haystack),
        }

    if not cat:
        err("Todos los assets aprobados en db_visual están ausentes o son inválidos en disco.")
        sys.exit(1)
    info(f"db_visual: {len(cat)} assets aprobados utilizables ({descartados} descartados por ausentes/inválidos).")
    return cat

# ── B. Scorer Emocional y Semántico ──────────────────────────────────────────

def calcular_score(toma: dict, asset_key: str, meta: dict, ultimos_usados: list, categoria_previa: str = None) -> float:
    score = 0.5

    # NUNCA repetir un asset dentro del mismo video
    if asset_key in ultimos_usados:
        return -99999.0

    # VETO ROTUNDO a variantes del mismo prompt / familia visual en el mismo video
    nombre_asset = Path(meta.get("path_original", asset_key)).name
    familia = obtener_familia_asset(nombre_asset)
    for u in ultimos_usados:
        if familia and obtener_familia_asset(Path(u).name) == familia:
            return -99999.0

    # Rotación de stock: penaliza uso histórico en videos anteriores
    score -= len(meta.get("stats_uso", [])) * 10.0

    # Estética: bloquea personas/familia/etc.
    if meta["_bloqueado"]:
        score -= 999.0

    # Moderación de seguridad para TikTok y YouTube (cero desnudos en redes)
    if meta.get("_bloqueado_redes", False):
        score -= 999.0

    # Regla de Diversidad Visual Estricta: Prohibir encadenar dos tomas de la misma categoría
    # (ej. jamás dos paisajes seguidos, jamás dos símbolos seguidos)
    cat_asset = meta.get("_categoria", "general")
    if categoria_previa and cat_asset != "general" and cat_asset == categoria_previa:
        score -= 50.0
    elif cat_asset == "figura_humana" and categoria_previa in ("paisaje", "simbolo", "elemento"):
        # Incentivo para alternar con esculturas y figuras humanas solemnes
        score += 20.0

    # Bonus semántico del Director de Arte (etiquetas de la DB vs emoción/texto de la toma)
    score += score_semantico(toma.get("texto", ""), toma.get("emocion", "aire"), meta["tags"])

    hay = meta["_haystack"]

    # ── Anclaje Astrológico Riguroso con el Tránsito Real del ADN ──
    transito = ADN.get("transito", {})
    planeta_str = transito.get("planeta", "")
    planetas_transito = [p.strip().lower() for p in planeta_str.replace(" y ", ",").split(",") if p.strip()]

    signos_todos = [
        "aries", "tauro", "geminis", "cancer", "leo", "virgo",
        "libra", "escorpio", "sagitario", "capricornio", "acuario", "piscis"
    ]
    # Detectar todos los signos involucrados en la geometría celeste del día
    signos_transito = []
    desc_transito = transito.get("descripcion_breve", "").lower()
    for s in signos_todos:
        if s in desc_transito or s == transito.get("signo_destino", "").lower():
            if s not in signos_transito:
                signos_transito.append(s)

    elemento_transito = ADN.get("arquetipos", {}).get("elemento", "").lower()

    # Prioridad altísima si el asset pertenece a los signos o planetas del tránsito
    for s in signos_transito:
        if s in hay:
            score += 15.0
    for p in planetas_transito:
        if p and p in hay:
            score += 14.0
    for el in elemento_transito.split("/"):
        el = el.strip()
        if el and el in hay:
            score += 5.0

    # Veto estricto a signos zodiacales ajenos/contradictorios que NO forman parte del tránsito
    for s in signos_todos:
        if s not in signos_transito:
            if f"_{s}" in hay or f"/{s}/" in hay or f"_{s}_" in hay or f"/{s}_" in hay:
                score -= 40.0

    # Priorizar Glifos sagrados, Sigilos y Casas reales de la astrología
    if any(k in hay for k in ("glifo_", "sigilo_", "orbe_", "aspecto_", "casa_")):
        score += 8.0

    # Descartar estética cyber-mecánica o prótesis futuristas (ajenas al misticismo sagrado)
    if "cyber" in hay or "protesis" in hay:
        score -= 50.0

    # Bonos por rol
    rol = toma.get("rol", "").lower()
    if "cta" in rol and any(k in hay for k in ("fractal", "abstract", "fondo", "glifo", "orbe")):
        score += 4.0
    if "gancho" in rol:
        if any(k in hay for k in ("fuego", "espacio", "luz", "abismo", "orbe", "vortice")):
            score += 2.0
        if meta["tipo"] == "video":
            score += 1.0
    return score

def elegir_mejor_asset_local(toma: dict, cat: dict, ultimos_usados: list, categoria_previa: str = None):
    mejor_score, mejor_key = -9999.0, None
    for key, meta in cat.items():
        s = calcular_score(toma, key, meta, ultimos_usados, categoria_previa)
        if s > mejor_score:
            mejor_score, mejor_key = s, key
    return mejor_key

def elegir_mejor_asset_hibrido(toma: dict, cat: dict, ultimos_usados: list, gemini_clients: list, categoria_previa: str = None):
    """Ranking local semántico (top 40, sin bloqueados) ordenado por score del Director de Arte."""
    scores = sorted(
        ((calcular_score(toma, k, m, ultimos_usados, categoria_previa), k) for k, m in cat.items()),
        key=lambda x: x[0], reverse=True,
    )
    top_40 = [k for s, k in scores[:40] if s > -500]
    if not top_40:
        return None
    return top_40[0]

def elegir_asset_gancho(cat: dict):
    """Asset 'portal cósmico' / espacio profundo que abre y cierra el video (loop). Prefiere el menos usado."""
    def _tags(m): return " ".join(m["tags"]).lower()
    videos = [k for k, m in cat.items() if m["tipo"] == "video" and not m["_bloqueado"]]
    candidatos = [k for k in videos if any(t in _tags(cat[k]) for t in TERMINOS_GANCHO)]
    if not candidatos:
        candidatos = [k for k in videos
                      if "07_espacio_galaxias" in cat[k]["_haystack"]
                      or "espacio" in _tags(cat[k]) or "cosmos" in _tags(cat[k])]
    if not candidatos:
        # Fallback a imágenes de espacio profundo / galaxias / singularidad para loop infinito
        candidatos = [
            k for k, m in cat.items()
            if not m["_bloqueado"] and (
                "07_espacio_galaxias" in m["_haystack"]
                or any(t in _tags(m) for t in TERMINOS_GANCHO)
                or any(w in m["_haystack"] for w in ["espacio", "galaxia", "nebulosa", "cosmos", "agujero_negro", "singularidad"])
            )
        ]
    if not candidatos:
        return None
    min_usos = min(len(cat[k]["stats_uso"]) for k in candidatos)
    return random.choice([k for k in candidatos if len(cat[k]["stats_uso"]) == min_usos])

# ── C. Plan de cortes (solo datos, ningún render) ────────────────────────────

def calcular_cortes_ritmicos(texto: str, duracion_total: float, es_astrolabio: bool = False) -> list:
    """
    Ritmo visual cinematográfico adaptativo y sugestión positiva:
    - Toma del Astrolabio (Toma 3): 1 plano secuencia continuo con zoom y HOLD.
    - Tomas narrativas (> 5.0s): 2 cortes dinámicos (3.0s - 4.2s) para mantener el dinamismo,
      aprovechar la variedad de obras visuales y acompañar la evolución psicológica del relato.
    - Tomas breves (<= 5.0s): 1 corte íntegro.
    """
    if es_astrolabio or duracion_total <= 5.0:
        return [round(duracion_total, 3)]
    n = 2
    base = round(duracion_total / n, 3)
    return [base, round(duracion_total - base, 3)]

def planificar_cortes_de_toma(toma: dict, toma_idx: int, total_tomas: int, cat: dict,
                              ultimos_usados: list, gancho_id, gemini_clients: list,
                              categoria_previa: str = None):
    """
    Devuelve (cortes, protagonista_id, categoria_elegida). `cortes` es la lista de dicts del contrato JSON.
    Muta `ultimos_usados` (los assets elegidos quedan vetados para el resto del video).
    Garantiza:
    1. Toma 3 (medio): Reloj Astrológico 2D / Astrolabio para la mecánica celeste.
    2. Cero duplicados de assets en el mismo video.
    3. Diversidad visual estricta (no dos paisajes o dos símbolos seguidos).
    """
    es_primera = toma_idx == 0
    es_tercera = toma_idx == 2  # Toma 3: El Reloj Astrológico en el medio
    es_ultima  = toma_idx == total_tomas - 1
    duraciones = calcular_cortes_ritmicos(toma.get("texto", ""), toma["duracion_s"], es_astrolabio=es_tercera)

    fecha_pub = ADN.get("produccion", {}).get("fecha_publicacion", "2026-11-03")
    clip_apertura = FACTORY_ROOT / "produccion" / "clips_reloj_2d" / f"reloj_2d_{fecha_pub}_apertura.mp4"
    clip_cierre = FACTORY_ROOT / "produccion" / "clips_reloj_2d" / f"reloj_2d_{fecha_pub}_cierre.mp4"

    # Si existen clips duales del Reloj 2D (Loop Continuo de 24h: inicio y fin del día):
    if es_primera and clip_apertura.exists():
        cortes = [{
            "orden": 0,
            "asset_id": f"reloj_2d_{fecha_pub}_apertura",
            "archivo": str(clip_apertura),
            "nombre": clip_apertura.name,
            "tipo": "video",
            "duracion_s": toma["duracion_s"],
            "es_iconica": True,
            "reverse": False,
            "transicion_entrada": None,
        }]
        return cortes, f"reloj_2d_{fecha_pub}_apertura", "simbolo"

    if es_ultima and clip_cierre.exists():
        cortes = [{
            "orden": 0,
            "asset_id": f"reloj_2d_{fecha_pub}_cierre",
            "archivo": str(clip_cierre),
            "nombre": clip_cierre.name,
            "tipo": "video",
            "duracion_s": toma["duracion_s"],
            "es_iconica": True,
            "reverse": False,
            "transicion_entrada": toma.get("transicion_entrada", "fade"),
        }]
        return cortes, f"reloj_2d_{fecha_pub}_cierre", "simbolo"

    if (es_primera or es_ultima) and gancho_id:
        protagonista = gancho_id
    elif es_tercera and not (clip_apertura.exists() and clip_cierre.exists()):
        # Prioridad para Toma 3 solo si NO hay Doble Reloj 2D (Apertura y Cierre):
        fecha_pub = ADN.get("produccion", {}).get("fecha_publicacion", "2026-11-02")
        reloj_clip_path = FACTORY_ROOT / "produccion" / "clips_reloj_2d" / f"reloj_2d_{fecha_pub}.mp4"
        if not reloj_clip_path.exists() or reloj_clip_path.stat().st_size < 1_000_000 or FORZAR_ACTIVO:
            try:
                from v2.celula_2.generador_reloj_cinematico import capturar_clip_reloj_cinematico
                reloj_clip_path = capturar_clip_reloj_cinematico(fecha_pub, duracion_s=toma["duracion_s"], forzar=True)
            except Exception as e:
                print(f"  [Warn] No se pudo capturar reloj 2D cinemático al vuelo: {e}")
                try:
                    from v2.celula_2.grabar_reloj_2d import capturar_clip_reloj
                    reloj_clip_path = capturar_clip_reloj(f"{fecha_pub}T12:00:00", duracion_s=toma["duracion_s"])
                except Exception as ex:
                    print(f"  [Warn] Fallback reloj 2D básico también falló: {ex}")
        
        if reloj_clip_path and Path(reloj_clip_path).exists():
            cortes = [{
                "orden": 0,
                "asset_id": f"reloj_2d_{fecha_pub}",
                "archivo": str(reloj_clip_path),
                "nombre": Path(reloj_clip_path).name,
                "tipo": "video",
                "duracion_s": toma["duracion_s"],
                "es_iconica": True,
                "reverse": False,
                "transicion_entrada": toma.get("transicion_entrada", "fade"),
            }]
            return cortes, f"reloj_2d_{fecha_pub}", "simbolo"

        reloj_candidatos = [
            k for k, v in cat.items()
            if any(term in k.lower() or term in v.get("etiquetas", "") for term in ["reloj", "astrolabio", "mandala"])
            and k not in ultimos_usados
        ]
        if reloj_candidatos:
            protagonista = random.choice(reloj_candidatos)
        else:
            protagonista = elegir_mejor_asset_hibrido(toma, cat, ultimos_usados, gemini_clients, categoria_previa)
    else:
        protagonista = elegir_mejor_asset_hibrido(toma, cat, ultimos_usados, gemini_clients, categoria_previa)

    idx_principal = len(duraciones) // 2 if len(duraciones) > 1 else 0
    elegidos = []
    for i in range(len(duraciones)):
        es_corte_inicial_video = es_primera and i == 0
        es_corte_final_video   = es_ultima and i == len(duraciones) - 1

        if es_corte_inicial_video and gancho_id:
            elegido = gancho_id                      # apertura con portal cósmico
        elif es_corte_final_video and gancho_id:
            elegido = gancho_id                      # loop infinito perfecto: cierra con el portal que abre el video
        elif i == idx_principal and protagonista and protagonista not in elegidos and protagonista not in ultimos_usados:
            elegido = protagonista                   # honra la elección principal
        else:
            elegido = elegir_mejor_asset_local(toma, cat, ultimos_usados + elegidos, categoria_previa)
            # Fallback estricto anti-duplicados y anti-familia de prompt
            familias_usadas = {
                obtener_familia_asset(Path(cat[x]["path_original"]).name if x in cat else Path(x).name)
                for x in (ultimos_usados + elegidos) if x
            }
            nom_elegido = Path(cat.get(elegido, {}).get("path_original", elegido)).name if elegido else ""
            if not elegido or elegido in (ultimos_usados + elegidos) or obtener_familia_asset(nom_elegido) in familias_usadas:
                disponibles = [
                    k for k in cat.keys()
                    if k not in (ultimos_usados + elegidos)
                    and obtener_familia_asset(Path(cat[k]["path_original"]).name) not in familias_usadas
                ]
                elegido = random.choice(disponibles) if disponibles else (elegido or protagonista)
        elegidos.append(elegido)

    cortes = []
    for i, (dur, asset_id) in enumerate(zip(duraciones, elegidos)):
        if not asset_id:
            continue
        meta = cat[asset_id]
        ultimos_usados.append(asset_id)
        es_corte_final_video = es_ultima and i == len(duraciones) - 1
        cortes.append({
            "orden":      i,
            "asset_id":   asset_id,
            "archivo":    meta["path_original"],          # ← ruta ORIGINAL; jamás un MP4 derivado
            "nombre":     Path(meta["path_original"]).name,
            "tipo":       meta["tipo"],
            "duracion_s": dur,
            "es_iconica": meta["_iconica"],
            "reverse":    bool(es_corte_final_video and gancho_id and asset_id == gancho_id and meta["tipo"] == "video"),
            "transicion_entrada": (
                None if (toma_idx == 0 and i == 0)
                else toma.get("transicion_entrada", "fade") if i == 0
                else TRANSICION_INTRA_TOMA
            ),
        })
    cat_elegida = cat[protagonista].get("_categoria", "general") if protagonista and protagonista in cat else "general"
    return cortes, protagonista, cat_elegida

def construir_entrada_corte(toma: dict, cortes: list, protagonista_id, cat: dict,
                            fuente: str = "nodriza_visual_db") -> dict:
    archivo = cat[protagonista_id]["path_original"] if protagonista_id and protagonista_id in cat else (
        cortes[0]["archivo"] if cortes else None
    )
    p = Path(archivo) if archivo else None
    num_t = toma.get("num") or toma.get("num_toma", 1)
    return {
        "num_toma":           num_t,
        "rol":                toma.get("rol", ""),
        "inicio_ms":          toma["inicio_ms"],
        "fin_ms":             toma["fin_ms"],
        "duracion_ms":        toma["duracion_ms"],
        "duracion_s":         toma["duracion_s"],
        "texto":              toma.get("texto", ""),
        "etiqueta_visual":    toma.get("etiqueta_visual"),
        "emocion":            toma.get("emocion", "aire"),
        "transicion_entrada": toma.get("transicion_entrada", "fade"),
        "archivo_video":      str(p) if p else None,
        "nombre_video":       p.name if p else None,
        "fuente_asignacion":  fuente,
        "requiere_loop":      None,
        "accion_ffmpeg":      None,
        "cortes":             cortes,
    }

# ── Ejecución Principal ──────────────────────────────────────────────────────

def run_nodriza():
    log("\n🧠 NODRIZA VISUAL 3.0 — Asignación Semántica (db_visual → lista_de_corte)", MAGENTA)

    gemini_clients = inicializar_clientes_gemini()
    timeline = cargar_timeline()

    # Director de Arte: emoción, tags ideales y transición xfade por toma
    tomas = enriquecer_tomas(timeline.get("tomas", []))
    log("🎬 Director de Arte activado: emociones y transiciones asignadas", MAGENTA)
    for t in tomas:
        num_toma = t.get("num") or t.get("num_toma", "?")
        log(f"   Toma {num_toma} | {t.get('rol','?')} → emoción: {t['emocion']} | transición: {t['transicion_entrada']}", GRIS)

    cat = cargar_catalogo_desde_db()
    gancho_id = elegir_asset_gancho(cat)
    if gancho_id:
        info(f"Portal de gancho/cierre (loop): {gancho_id}")
    else:
        warn("Sin video de gancho en db_visual: el loop inicio/cierre queda desactivado.")

    lista_de_corte = {
        "evento_id":        EVENTO_ID,
        "semana":           SEMANA,
        "total_duracion_s": timeline.get("total_duracion_s", sum(t["duracion_s"] for t in tomas)),
        "asignaciones":     [],
    }

    ultimos_usados: list = []
    categoria_actual = None
    for toma_idx, toma in enumerate(tomas):
        num_t = toma.get("num") or toma.get("num_toma", toma_idx + 1)
        cortes, protagonista, categoria_actual = planificar_cortes_de_toma(
            toma, toma_idx, len(tomas), cat, ultimos_usados, gancho_id, gemini_clients, categoria_actual
        )
        if not cortes:
            err(f"Toma {num_t} no pudo ser asignada.")
            lista_de_corte["asignaciones"].append(construir_entrada_corte(toma, [], None, cat))
            continue

        info(f"Toma {num_t} ({toma['duracion_s']}s) → {len(cortes)} cortes.")
        for c in cortes:
            ok(f"Toma {num_t} → Corte {c['orden']}: {c['nombre']} [{c['tipo']}, {c['duracion_s']}s]")
        lista_de_corte["asignaciones"].append(construir_entrada_corte(toma, cortes, protagonista, cat))

    # Persistir uso en SQLite (idempotente: limpia el evento actual antes de re-registrar)
    db_visual.limpiar_uso_evento(EVENTO_ID)
    for asset_id in dict.fromkeys(ultimos_usados):
        db_visual.registrar_uso(asset_id, EVENTO_ID)

    asegurar_dir(TEMP_DIR)
    ruta = TEMP_DIR / f"lista_de_corte_{EVENTO_ID}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista_de_corte, f, ensure_ascii=False, indent=2)
    ok(f"Lista de corte guardada: {ruta}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--opcion", type=int, default=1)
    parser.add_argument("--fecha", type=str, default=None, help="Fecha YYYY-MM-DD")
    parser.add_argument("--forzar", action="store_true", help="Forzar regeneración")
    args = parser.parse_args()

    if args.opcion == 1:
        run_nodriza()
    else:
        err("Opción no válida para Nodriza Visual.")
