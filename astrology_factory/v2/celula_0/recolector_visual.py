#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script 0.0: recolector_visual.py
Obtiene y descarga assets crudos a /Descargas_Crudas/<semana>/.
SIEMPRE descarga a cuarentena. NUNCA toca /Assets_Reusables/ ni /Assets_Auditados/.
El auditor_boveda.py es quien decide qué pasa a la bóveda real.

Mejoras sobre V1:
  ✅ Destino de cuarentena separado (/Descargas_Crudas/) — no contamina la bóveda
  ✅ Lee queries directamente del ADN JSON (sin transit_palettes.json externo)
  ✅ Registry por sesión/semana (no global corruptible)
  ✅ Queries construidas desde palabras_clave + palabras_visuales + arquetipos
  ✅ Filtro de exclusión post-descarga más agresivo
  ✅ Soporte para clonar repositorios de arte esotérico permitidos

Uso:
  python v2/celula_0/recolector_visual.py --opcion 1              # Búsqueda temática alineada al ADN
  python v2/celula_0/recolector_visual.py --opcion 2              # Scraping arquetipos puros (planetas)
  python v2/celula_0/recolector_visual.py --opcion 3              # Clonar repositorios de arte esotérico
  python v2/celula_0/recolector_visual.py --opcion 4              # Purga de /Descargas_Crudas/
  python v2/celula_0/recolector_visual.py --opcion 1 --max 20     # Máximo 20 assets por query
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
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

import requests

# ── Rutas (del ADN) ───────────────────────────────────────────────────────────
VAULT_BASE   = Path(ADN["assets"]["boveda_base"])
SEMANA       = ADN["produccion"]["semana_prefijo"]
EVENTO_ID    = ADN["produccion"]["evento_id"]

# ★ CLAVE: Directorio de cuarentena separado de la bóveda ★
DESCARGAS_DIR   = VAULT_BASE / "Descargas_Crudas" / SEMANA
REGISTRY_PATH   = DESCARGAS_DIR / f"registry_{EVENTO_ID}.json"

# ── Credenciales ───────────────────────────────────────────────────────────────
PEXELS_API_KEY  = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")   # En .env — nunca hardcodeada

# ── Colores de terminal ────────────────────────────────────────────────────────
RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)
def dim(msg):               log(f"     {msg}", GRIS)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# ── Términos de exclusión — aprendidos del V1 ─────────────────────────────────
EXCLUSION_TAGS = {
    "bear", "oso", "child", "baby", "cute", "kids", "cartoon", "toy",
    "doll", "puppet", "bunny", "rabbit", "unicorn", "fairy", "princess",
    "kawaii", "chibi", "anime", "clipart", "vector", "sticker",
    "family", "home", "mother", "father", "parent", "domestic",
    "kitchen", "living", "bedroom", "house", "garden", "backyard",
    "smile", "happy", "cheerful", "lifestyle", "wedding", "birthday",
    "christmas", "easter", "holiday", "santa"
}

# Sufijo que se agrega a TODAS las queries enviadas a las APIs
EXCLUSION_SUFFIX = (
    " -cartoon -cute -kids -bear -baby -child -vector -clipart"
    " -family -home -domestic -lifestyle -happy -wedding"
)

# ── Registry por sesión (no global) ──────────────────────────────────────────

def cargar_registry() -> set:
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_registry(registry: set):
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(registry), f, indent=2)

# ── Lectura del ADN para construir queries ────────────────────────────────────

def construir_queries_adn() -> list[dict]:
    """
    Lee el ADN activo y construye queries temáticas inteligentes.
    Retorna lista de {query_str, prioridad, fuente}.
    """
    queries = []
    planeta      = ADN["transito"]["planeta"]
    signo        = ADN["transito"]["signo_destino"]
    palabras_kw  = ADN["transito"]["palabras_clave"]
    palabras_vis = ADN["estetica_visual"]["palabras_visuales"]
    arquetipo    = ADN["arquetipos"]["primario"]
    emocion      = ADN["arquetipos"]["emocion_dominante"].replace("_", " ")
    elemento     = ADN["arquetipos"]["elemento"]

    # Tier 1: Queries planetarias directas (alta precisión)
    queries.append({"q": f"{planeta} {signo} astrology dark", "prioridad": 1, "fuente": "transito_directo"})
    queries.append({"q": f"{planeta} planet cosmos space dark", "prioridad": 1, "fuente": "planeta_puro"})
    queries.append({"q": f"{signo} zodiac esoteric dark fantasy", "prioridad": 1, "fuente": "signo_puro"})

    # Tier 2: Queries visuales del ADN (medio alcance)
    for palabra_vis in palabras_vis[:5]:  # Top 5 visuales
        queries.append({"q": f"{palabra_vis} dark mystical", "prioridad": 2, "fuente": "visual_adn"})

    # Tier 3: Arquetipos + emoción (mayor cobertura)
    queries.append({"q": f"{arquetipo} mythology dark fantasy", "prioridad": 3, "fuente": "arquetipo"})
    queries.append({"q": f"{emocion} {elemento} water mystical", "prioridad": 3, "fuente": "emocion_elemento"})

    # Tier 4: Keywords astrológicas selectas
    for kw in palabras_kw[:4]:
        queries.append({"q": f"{kw} dark esoteric occult", "prioridad": 4, "fuente": "keyword_adn"})

    return queries

def construir_queries_arquetipos() -> list[dict]:
    """
    Construye queries específicas para los arquetipos puros (planetas, símbolos, cosmos).
    """
    queries = []
    planetas = ["saturn", "pluto", "neptune", "mars", "venus", "moon", "mercury", "jupiter", "uranus"]
    estilos  = ["space nebula", "cosmos dark", "astronomy space", "planet surface dark", "solar system dark"]

    # Los planetas como objetos visuales puros
    for p in planetas:
        queries.append({"q": f"{p} planet space dark", "prioridad": 1, "fuente": "planeta_arquetipo"})

    # Escenas cósmicas de alta calidad
    for e in estilos:
        queries.append({"q": e, "prioridad": 2, "fuente": "escena_cosmica"})

    # Astrología esotérica: círculos, runas, símbolos
    simbolos = ["zodiac wheel", "birth chart astrology", "rune stone ancient", "sacred geometry",
                "occult symbols dark", "alchemy symbols", "tarot dark mystical"]
    for s in simbolos:
        queries.append({"q": s, "prioridad": 3, "fuente": "simbolo_esoterico"})

    return queries

# ── Repositorios de arte esotérico permitidos ─────────────────────────────────

REPOS_ARTE_ESOTERICO = [
    {
        "nombre": "NASA Images (Dominio Público)",
        "tipo": "api",
        "url_base": "https://images-api.nasa.gov/search",
        "queries": ["nebula", "galaxy", "planet", "cosmos", "space dark", "saturn", "jupiter"],
        "formato": "jpg"
    },
    {
        "nombre": "Wikimedia Commons — Arte Esotérico",
        "tipo": "wikimedia",
        "queries": [
            "tarot card artwork", "zodiac illustration historical",
            "alchemical illustration", "astrology chart historical",
            "occult manuscript illustration"
        ],
        "categoria": "esoteric"
    },
    {
        "nombre": "Archive.org — Arte Vintage Esotérico",
        "tipo": "archive_org",
        "colecciones": [
            "prelinger",
            "feature_films_otrcat"
        ]
    }
]

# ── Descarga de archivos ───────────────────────────────────────────────────────

def limpiar_nombre(texto: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '_', texto).strip('_').lower()[:50]

def tiene_tags_prohibidos(tags_str: str) -> bool:
    tags_lower = tags_str.lower()
    return any(t in tags_lower for t in EXCLUSION_TAGS)

def descargar_archivo(url: str, destino: Path, descripcion: str = "") -> bool:
    try:
        headers = {"User-Agent": "AstrologyEngine/2.0 (educational)"}
        r = requests.get(url, headers=headers, timeout=30, stream=True)
        if r.status_code == 200:
            with open(destino, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_kb = destino.stat().st_size / 1024
            if size_kb < 50:  # Descartar si muy pequeño (basura)
                destino.unlink()
                dim(f"Descartado por tamaño ({size_kb:.1f}KB): {descripcion}")
                return False
            return True
        else:
            dim(f"HTTP {r.status_code} para: {descripcion}")
    except Exception as e:
        dim(f"Error descarga: {e}")
    return False

# ── Búsquedas en APIs ─────────────────────────────────────────────────────────

def buscar_pexels_videos(query: str, per_page: int = 15) -> list:
    if not PEXELS_API_KEY:
        warn("PEXELS_API_KEY no configurada en .env")
        return []
    safe_q = (query + EXCLUSION_SUFFIX).strip()
    url = (f"https://api.pexels.com/videos/search"
           f"?query={requests.utils.quote(safe_q)}"
           f"&per_page={per_page}&orientation=portrait")
    try:
        r = requests.get(url, headers={"Authorization": PEXELS_API_KEY}, timeout=15)
        if r.status_code == 200:
            return r.json().get("videos", [])
        else:
            dim(f"Pexels HTTP {r.status_code}")
    except Exception as e:
        dim(f"Pexels error: {e}")
    return []

def buscar_pixabay_fotos(query: str, per_page: int = 15, tipo: str = "photo") -> list:
    if not PIXABAY_API_KEY:
        warn("PIXABAY_API_KEY no configurada en .env")
        return []
    
    # Pixabay has a 100 char limit for the 'q' parameter
    safe_q = (query + " -cartoon -cute -kids -vector -clipart").strip()
    if len(safe_q) > 100:
        safe_q = safe_q[:100].rsplit(' ', 1)[0]
        
    url = (f"https://pixabay.com/api/"
           f"?key={PIXABAY_API_KEY}"
           f"&q={requests.utils.quote(safe_q)}"
           f"&image_type={tipo}"
           f"&orientation=vertical"
           f"&per_page={per_page}"
           f"&safesearch=true"
           f"&min_width=800")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            hits = r.json().get("hits", [])
            # Filtro post-API de tags — aprendido del V1
            return [h for h in hits if not tiene_tags_prohibidos(h.get("tags", ""))]
        else:
            dim(f"Pixabay HTTP {r.status_code}")
    except Exception as e:
        dim(f"Pixabay error: {e}")
    return []

def buscar_nasa_images(query: str, max_results: int = 8) -> list[dict]:
    """Busca en NASA Image & Video Library (Dominio Público)."""
    url = f"https://images-api.nasa.gov/search?q={requests.utils.quote(query)}&media_type=image"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            items = r.json().get("collection", {}).get("items", [])[:max_results]
            resultados = []
            for item in items:
                links = item.get("links", [])
                for link in links:
                    if link.get("rel") == "preview":
                        # Construir URL de alta resolución
                        href = link.get("href", "")
                        # Reemplazar thumb por original
                        href_hd = href.replace("~thumb", "~orig")
                        resultados.append({
                            "url": href_hd,
                            "titulo": item.get("data", [{}])[0].get("title", "nasa_image")
                        })
                        break
            return resultados
    except Exception as e:
        dim(f"NASA API error: {e}")
    return []

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Búsqueda Temática Alineada al ADN
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_busqueda_tematica(max_por_query: int = 5):
    """
    Lee el ADN activo, construye queries semánticas y descarga a /Descargas_Crudas/.
    Fuentes: Pexels (videos) + Pixabay (fotos) + NASA (cosmos, dominio público).
    """
    log("\n🎯 OPCIÓN 1 — Búsqueda Temática Alineada al ADN", MAGENTA)
    log(f"   Evento:  {ADN['produccion']['evento_titulo']}", CYAN)
    log(f"   Destino: {DESCARGAS_DIR}", CYAN)

    asegurar_dir(DESCARGAS_DIR)
    registry = cargar_registry()
    queries = construir_queries_adn()

    log(f"\n📋 {len(queries)} queries generadas desde el ADN:", CYAN)
    for q in queries:
        dim(f"  [{q['prioridad']}] {q['q']}  ({q['fuente']})")

    total_descargados = 0
    semana_clean = limpiar_nombre(SEMANA)

    for q_data in queries:
        query    = q_data["q"]
        fuente   = q_data["fuente"]
        prioridad = q_data["prioridad"]

        log(f"\n🔍 Query: \"{query}\"", AMARILLO)

        descargados_esta_query = 0
        query_clean = limpiar_nombre(query)

        # ── Pixabay Fotos ───────────────────────────────────────────────────
        if descargados_esta_query < max_por_query:
            fotos = buscar_pixabay_fotos(query, per_page=max_por_query * 2)
            for foto in fotos:
                if descargados_esta_query >= max_por_query:
                    break
                f_id = f"pix_i_{foto['id']}"
                if f_id in registry:
                    continue
                url = foto.get("largeImageURL") or foto.get("webformatURL")
                if not url:
                    continue
                destino = DESCARGAS_DIR / f"{semana_clean}_{fuente}_{query_clean}_{f_id}.jpg"
                dim(f"↓ Pixabay foto: {destino.name}")
                if descargar_archivo(url, destino, str(destino.name)):
                    ok(f"Descargado: {destino.name}")
                    registry.add(f_id)
                    guardar_registry(registry)
                    descargados_esta_query += 1
                    total_descargados += 1
                    time.sleep(1)

        # ── NASA (solo para queries de prioridad 1 — espacio/cosmos) ────────
        if prioridad <= 2 and any(w in query.lower() for w in ["space", "cosmos", "planet", "nebula", "galaxy"]):
            nasa_results = buscar_nasa_images(query, max_results=3)
            for item in nasa_results:
                n_id = f"nasa_{limpiar_nombre(item['titulo'])}"
                if n_id in registry:
                    continue
                destino = DESCARGAS_DIR / f"{semana_clean}_nasa_{limpiar_nombre(item['titulo'])}.jpg"
                dim(f"↓ NASA: {destino.name}")
                if descargar_archivo(item["url"], destino, str(destino.name)):
                    ok(f"Descargado: {destino.name}")
                    registry.add(n_id)
                    guardar_registry(registry)
                    total_descargados += 1
                    time.sleep(0.5)

        time.sleep(2)  # Pausa entre queries para respetar rate limits

    # ── Fondos Animados Abstractos (Pexels) ─────────────────────────────
    log("\n🌌 Buscando Fondos Abstractos Animados (sin humanos)", AMARILLO)
    elemento = ADN["arquetipos"]["elemento"]
    planeta  = ADN["transito"]["planeta"]
    queries_fondos = [
        f"{elemento} element abstract flowing fluid dark",
        f"{planeta} planet cosmos space nebula animation",
        "sacred geometry esoteric symbols dark looping"
    ]
    
    for q_fondo in queries_fondos:
        videos = buscar_pexels_videos(q_fondo, per_page=max_por_query)
        descargados_fondo = 0
        q_fondo_clean = limpiar_nombre(q_fondo)
        
        for v in videos:
            if descargados_fondo >= 3:  # Máximo 3 de cada fondo
                break
            v_id = f"pex_v_{v['id']}"
            if v_id in registry: continue
            
            files = v.get("video_files", [])
            candidatos = [f for f in files if 1200 <= f.get("width", 0) <= 1920]
            if not candidatos: candidatos = [f for f in files if f.get("width", 0) >= 1080]
            if not candidatos: candidatos = files
            if not candidatos: continue
            candidatos.sort(key=lambda x: abs(x.get("width", 0) - 1080))
            
            url = candidatos[0].get("link", "")
            if not url: continue
            
            destino = DESCARGAS_DIR / f"{semana_clean}_fondo_animado_{q_fondo_clean}_{v_id}.mp4"
            dim(f"↓ Pexels fondo animado: {destino.name}")
            if descargar_archivo(url, destino, str(destino.name)):
                ok(f"Descargado fondo: {destino.name}")
                registry.add(v_id)
                guardar_registry(registry)
                descargados_fondo += 1
                total_descargados += 1
                time.sleep(1.5)

    log(f"\n{'─'*55}", CYAN)
    log(f"📊 TOTAL DESCARGADO: {total_descargados} assets en {DESCARGAS_DIR}", VERDE)
    info("Siguiente paso → auditor_boveda.py --opcion 1 (Curaduría Manual Interactiva)")

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Scraping Arquetipos Puros (Planetas y Símbolos)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_arquetipos_puros(max_por_query: int = 5):
    """
    Descarga assets de arquetipos cósmicos puros: planetas reales, nebulosas,
    símbolos astrológicos, runas y geometría sagrada.
    Prioriza NASA (dominio público) + Pixabay illustraciones.
    """
    log("\n🪐 OPCIÓN 2 — Scraping Arquetipos Puros", MAGENTA)
    log(f"   Destino: {DESCARGAS_DIR}", CYAN)

    asegurar_dir(DESCARGAS_DIR)
    registry = cargar_registry()
    queries = construir_queries_arquetipos()
    semana_clean = limpiar_nombre(SEMANA)
    total_descargados = 0

    log(f"\n📋 {len(queries)} queries de arquetipos:", CYAN)
    for q in queries[:8]:
        dim(f"  {q['q']}")
    if len(queries) > 8:
        dim(f"  ... y {len(queries)-8} más")

    for q_data in queries:
        query     = q_data["q"]
        fuente    = q_data["fuente"]
        query_clean = limpiar_nombre(query)

        log(f"\n🔍 Query arquetipo: \"{query}\"", AMARILLO)

        # Prioridad: NASA para cosmos/planetas reales
        if any(w in query.lower() for w in ["planet", "nebula", "galaxy", "space", "cosmos", "saturn", "jupiter"]):
            nasa_results = buscar_nasa_images(query, max_results=max_por_query)
            for item in nasa_results:
                n_id = f"nasa_{limpiar_nombre(item['titulo'])}"
                if n_id in registry:
                    continue
                destino = DESCARGAS_DIR / f"{semana_clean}_{fuente}_nasa_{limpiar_nombre(item['titulo'])}.jpg"
                dim(f"↓ NASA: {destino.name}")
                if descargar_archivo(item["url"], destino, str(destino.name)):
                    ok(f"Descargado: {destino.name}")
                    registry.add(n_id)
                    guardar_registry(registry)
                    total_descargados += 1
                    time.sleep(0.5)

        # Pixabay ilustraciones para símbolos esotéricos
        fotos = buscar_pixabay_fotos(query, per_page=max_por_query * 2, tipo="illustration")
        for foto in fotos[:max_por_query]:
            f_id = f"pix_i_{foto['id']}"
            if f_id in registry:
                continue
            url = foto.get("largeImageURL") or foto.get("webformatURL")
            if not url:
                continue
            destino = DESCARGAS_DIR / f"{semana_clean}_{fuente}_{query_clean}_{f_id}.jpg"
            dim(f"↓ Pixabay ilus: {destino.name}")
            if descargar_archivo(url, destino, str(destino.name)):
                ok(f"Descargado: {destino.name}")
                registry.add(f_id)
                guardar_registry(registry)
                total_descargados += 1
                time.sleep(1)

        time.sleep(2)

    log(f"\n{'─'*55}", CYAN)
    log(f"📊 ARQUETIPOS DESCARGADOS: {total_descargados} assets en {DESCARGAS_DIR}", VERDE)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Clonado de Arte Esotérico Permitido
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_clonar_repositorios():
    """
    Descarga repositorios enteros de arte esotérico de dominio público.
    Fuentes: NASA Image API, Wikimedia Commons, Archive.org.
    Todo bajo licencias permisivas verificadas.
    """
    log("\n🗂️  OPCIÓN 3 — Clonado de Arte Esotérico", MAGENTA)
    log(f"   Destino base: {DESCARGAS_DIR}", CYAN)

    asegurar_dir(DESCARGAS_DIR)
    registry = cargar_registry()
    total_descargados = 0
    semana_clean = limpiar_nombre(SEMANA)

    # ── NASA: lote completo de cosmos ────────────────────────────────────────
    log("\n🚀 NASA Image Library (Dominio Público / No Copyright)", AMARILLO)
    for repo in REPOS_ARTE_ESOTERICO:
        if repo["tipo"] != "api":
            continue
        for query in repo["queries"]:
            log(f"  📡 NASA query: {query}", CYAN)
            resultados = buscar_nasa_images(query, max_results=10)
            for item in resultados:
                n_id = f"nasa_{limpiar_nombre(item['titulo'])}"
                if n_id in registry:
                    dim(f"  Ya descargado: {item['titulo']}")
                    continue
                destino = DESCARGAS_DIR / f"{semana_clean}_nasa_{limpiar_nombre(item['titulo'])}.jpg"
                if descargar_archivo(item["url"], destino, item['titulo']):
                    ok(f"NASA: {destino.name}")
                    registry.add(n_id)
                    guardar_registry(registry)
                    total_descargados += 1
                    time.sleep(0.3)
            time.sleep(1)

    # ── Wikimedia Commons — Arte histórico esotérico ─────────────────────────
    log("\n🏛️  Wikimedia Commons (CC / Dominio Público)", AMARILLO)
    wikimedia_queries = [
        "tarot card historical illustration",
        "zodiac medieval manuscript",
        "alchemy illustration historical",
        "astrology chart 17th century",
        "occult manuscript drawing"
    ]
    for query in wikimedia_queries:
        log(f"  📖 Wikimedia query: {query}", CYAN)
        url_api = (
            f"https://commons.wikimedia.org/w/api.php"
            f"?action=query&list=search"
            f"&srsearch={requests.utils.quote(query)}"
            f"&srnamespace=6"  # namespace 6 = archivos
            f"&srlimit=8"
            f"&format=json"
        )
        try:
            r = requests.get(url_api, timeout=15,
                             headers={"User-Agent": "AstrologyEngineV2/1.0"})
            if r.status_code != 200:
                dim(f"  Wikimedia HTTP {r.status_code}")
                continue
            resultados_wiki = r.json().get("query", {}).get("search", [])
            for item in resultados_wiki:
                titulo = item.get("title", "").replace("File:", "")
                w_id = f"wiki_{limpiar_nombre(titulo)}"
                if w_id in registry:
                    continue
                # Obtener URL directa del archivo
                url_info = (
                    f"https://commons.wikimedia.org/w/api.php"
                    f"?action=query&titles=File:{requests.utils.quote(titulo)}"
                    f"&prop=imageinfo&iiprop=url&iiurlwidth=1200&format=json"
                )
                r2 = requests.get(url_info, timeout=10,
                                  headers={"User-Agent": "AstrologyEngineV2/1.0"})
                if r2.status_code != 200:
                    continue
                pages = r2.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    info_list = page.get("imageinfo", [])
                    if not info_list:
                        continue
                    img_url = info_list[0].get("thumburl") or info_list[0].get("url")
                    if not img_url:
                        continue
                    ext = Path(img_url).suffix.lower()
                    if ext not in ['.jpg', '.jpeg', '.png']:
                        dim(f"  Formato omitido: {ext} — {titulo[:40]}")
                        continue
                    destino = DESCARGAS_DIR / f"{semana_clean}_wiki_{limpiar_nombre(titulo)}{ext}"
                    dim(f"  ↓ Wikimedia: {destino.name}")
                    if descargar_archivo(img_url, destino, titulo):
                        ok(f"Wikimedia: {destino.name}")
                        registry.add(w_id)
                        guardar_registry(registry)
                        total_descargados += 1
                        time.sleep(0.5)
                    break
        except Exception as e:
            dim(f"  Error Wikimedia: {e}")
        time.sleep(1.5)

    # ── Resumen final ────────────────────────────────────────────────────────
    log(f"\n{'─'*55}", CYAN)
    log(f"📊 REPOSITORIOS CLONADOS: {total_descargados} assets en {DESCARGAS_DIR}", VERDE)
    info("Siguiente paso → auditor_boveda.py --opcion 1 (Curaduría Manual Interactiva)")

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Purga de Descargas Crudas
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_purga():
    """
    Vacía la carpeta /Descargas_Crudas/<semana>/ y elimina el registry de sesión.
    Pide confirmación doble antes de ejecutar.
    """
    log("\n🗑️  OPCIÓN 4 — Purga de Descargas Crudas", MAGENTA)

    if not DESCARGAS_DIR.exists():
        info(f"La carpeta ya está vacía o no existe: {DESCARGAS_DIR}")
        return

    # Contar archivos
    archivos = list(DESCARGAS_DIR.rglob("*"))
    archivos_media = [f for f in archivos if f.is_file()]
    size_total_mb = sum(f.stat().st_size for f in archivos_media) / (1024 * 1024)

    log(f"\n⚠️  Contenido a eliminar:", AMARILLO)
    log(f"   Carpeta:  {DESCARGAS_DIR}", AMARILLO)
    log(f"   Archivos: {len(archivos_media)}", AMARILLO)
    log(f"   Tamaño:   {size_total_mb:.1f} MB", AMARILLO)

    confirmacion_1 = input("\n¿Confirmas la purga? [escribe 'PURGAR' en mayúsculas]: ").strip()
    if confirmacion_1 != "PURGAR":
        info("Purga cancelada.")
        return

    confirmacion_2 = input("⚠️  ÚLTIMA CONFIRMACIÓN — ¿Eliminar TODO el contenido? [s/N]: ").strip().lower()
    if confirmacion_2 != "s":
        info("Purga cancelada.")
        return

    try:
        shutil.rmtree(DESCARGAS_DIR)
        DESCARGAS_DIR.mkdir(parents=True, exist_ok=True)
        ok(f"Carpeta purgada y recreada: {DESCARGAS_DIR}")
        info("Registry de sesión eliminado. El próximo recolector empieza desde cero.")
    except Exception as e:
        err(f"Error durante la purga: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌑 Recolector Visual V2 — Célula Madre 0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Opciones disponibles:
  1  Búsqueda temática alineada al ADN (Pexels + Pixabay + NASA)
  2  Scraping arquetipos puros (planetas, cosmos, símbolos esotéricos)
  3  Clonado de repositorios de arte esotérico (NASA, Wikimedia, Archive.org)
  4  Purga de /Descargas_Crudas/ para reiniciar búsqueda

Todos los assets se descargan a:
  {VAULT_BASE}/Descargas_Crudas/{SEMANA}/
NUNCA a /Assets_Reusables/ directamente.
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Número de opción (1-4)")
    parser.add_argument("--max", type=int, default=5,
                        help="[Opciones 1 y 2] Máximo de assets por query (default: 5)")

    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌑 RECOLECTOR VISUAL V2", MAGENTA)
    log(f"  ADN:     {ADN['produccion']['evento_id']}", CYAN)
    log(f"  Semana:  {SEMANA}", CYAN)
    log(f"  Destino: Descargas_Crudas/{SEMANA}/  (CUARENTENA)", AMARILLO)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:
        opcion_1_busqueda_tematica(args.max)
    elif args.opcion == 2:
        opcion_2_arquetipos_puros(args.max)
    elif args.opcion == 3:
        opcion_3_clonar_repositorios()
    elif args.opcion == 4:
        opcion_4_purga()

if __name__ == "__main__":
    main()
