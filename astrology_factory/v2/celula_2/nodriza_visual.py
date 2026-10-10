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
FORMATOS_IMG   = {".jpg", ".jpeg", ".png"}
_VALIDOS_ADN   = {f".{e.lower().lstrip('.')}" for e in ADN.get("validaciones", {}).get("formatos_validos", [])}
FORMATOS_ACEPTADOS = (FORMATOS_VIDEO | FORMATOS_IMG) & _VALIDOS_ADN if _VALIDOS_ADN else (FORMATOS_VIDEO | FORMATOS_IMG)
MIN_SIZE_BYTES = int(ADN.get("validaciones", {}).get("min_size_bytes", 0))

TRANSICION_INTRA_TOMA = "fade"   # transición entre cortes de una misma toma

BLOQUEADOS = {
    "familia", "bebe", "family", "baby", "niño", "niña", "hogar", "niños", "pareja",
    "couple", "boda", "wedding", "multitud", "crowd", "niñez", "child", "persona",
    "hombre", "mujer", "gente", "people", "man", "woman", "person",
}
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
        cat[asset_id] = {
            "path_original":    ruta_abs,
            "path_video_final": ruta_abs,   # clave legada: prompt_semantico.py la exige no vacía (ya NO es un MP4 transmutado)
            "tipo":             "video" if p.suffix.lower() in FORMATOS_VIDEO else "imagen",
            "tags":             tags,
            "etiquetas_visuales": tags,
            "stats_uso":        stats_uso,
            # cachés de scoring (prefijo _ → nunca se envían a Gemini ni al JSON)
            "_bloqueado":       bool(_tokens(haystack) & BLOQUEADOS),
            "_iconica":         any(w in haystack for w in PALABRAS_ICONICAS),
            "_haystack":        haystack,
        }

    if not cat:
        err("Todos los assets aprobados en db_visual están ausentes o son inválidos en disco.")
        sys.exit(1)
    info(f"db_visual: {len(cat)} assets aprobados utilizables ({descartados} descartados por ausentes/inválidos).")
    return cat

# ── B. Scorer Emocional y Semántico ──────────────────────────────────────────

def calcular_score(toma: dict, asset_key: str, meta: dict, ultimos_usados: list) -> float:
    score = 0.5

    # NUNCA repetir un asset dentro del mismo video
    if asset_key in ultimos_usados:
        score -= 100.0

    # Rotación de stock: penaliza uso histórico en videos anteriores
    score -= len(meta.get("stats_uso", [])) * 10.0

    # Estética: bloquea personas/familia/etc.
    if meta["_bloqueado"]:
        score -= 999.0

    # Bonus semántico del Director de Arte (etiquetas de la DB vs emoción/texto de la toma)
    score += score_semantico(toma.get("texto", ""), toma.get("emocion", "aire"), meta["tags"])

    # Bonos por rol
    rol = toma.get("rol", "").lower()
    hay = meta["_haystack"]
    if "cta" in rol and any(k in hay for k in ("fractal", "abstract", "fondo")):
        score += 2.0
    if "gancho" in rol:
        if any(k in hay for k in ("fuego", "espacio", "luz")):
            score += 1.0
        if meta["tipo"] == "video":
            score += 0.5
    return score

def elegir_mejor_asset_local(toma: dict, cat: dict, ultimos_usados: list):
    mejor_score, mejor_key = -9999.0, None
    for key, meta in cat.items():
        s = calcular_score(toma, key, meta, ultimos_usados)
        if s > mejor_score:
            mejor_score, mejor_key = s, key
    return mejor_key

def elegir_mejor_asset_hibrido(toma: dict, cat: dict, ultimos_usados: list, gemini_clients: list):
    """Ranking local (top 40, sin bloqueados) → desempate creativo con Gemini → fallback local."""
    scores = sorted(
        ((calcular_score(toma, k, m, ultimos_usados), k) for k, m in cat.items()),
        key=lambda x: x[0], reverse=True,
    )
    top_40 = [k for s, k in scores[:40] if s > -500]
    if not top_40:
        return None

    if gemini_clients:
        cat_filtrado = {k: cat[k] for k in top_40}
        texto = toma.get("texto_narrador", toma.get("texto", ""))
        mejor = elegir_mejor_asset_con_gemini(
            random.choice(gemini_clients), texto, toma.get("rol", ""), cat_filtrado,
            ultimos_usados, toma.get("emocion", "indefinida"), ELEMENTO_ADN,
        )
        if mejor and mejor in cat_filtrado:
            return mejor
    return top_40[0]

def elegir_asset_gancho(cat: dict):
    """Video 'portal cósmico' que abre y cierra el video (loop). Prefiere el menos usado."""
    def _tags(m): return " ".join(m["tags"]).lower()
    videos = [k for k, m in cat.items() if m["tipo"] == "video" and not m["_bloqueado"]]
    candidatos = [k for k in videos if any(t in _tags(cat[k]) for t in TERMINOS_GANCHO)]
    if not candidatos:
        candidatos = [k for k in videos
                      if "07_espacio_galaxias" in cat[k]["_haystack"]
                      or "espacio" in _tags(cat[k]) or "cosmos" in _tags(cat[k])]
    if not candidatos:
        return None
    min_usos = min(len(cat[k]["stats_uso"]) for k in candidatos)
    return random.choice([k for k in candidatos if len(cat[k]["stats_uso"]) == min_usos])

# ── C. Plan de cortes (solo datos, ningún render) ────────────────────────────

def calcular_cortes_ritmicos(texto: str, duracion_total: float) -> list:
    """Cortes de ~2 s para un viaje sensorial dinámico. El último absorbe el residuo de redondeo."""
    n = max(1, int(duracion_total / 2.0))
    base = round(duracion_total / n, 3)
    cortes = [base] * n
    cortes[-1] = round(duracion_total - base * (n - 1), 3)
    return cortes

def planificar_cortes_de_toma(toma: dict, toma_idx: int, total_tomas: int, cat: dict,
                              ultimos_usados: list, gancho_id, gemini_clients: list):
    """
    Devuelve (cortes, protagonista_id). `cortes` es la lista de dicts del contrato JSON.
    Muta `ultimos_usados` (los assets elegidos quedan vetados para el resto del video).
    """
    es_primera = toma_idx == 0
    es_ultima  = toma_idx == total_tomas - 1
    duraciones = calcular_cortes_ritmicos(toma.get("texto", ""), toma["duracion_s"])

    if (es_primera or es_ultima) and gancho_id:
        protagonista = gancho_id
    else:
        protagonista = elegir_mejor_asset_hibrido(toma, cat, ultimos_usados, gemini_clients)

    idx_principal = len(duraciones) // 2 if len(duraciones) > 1 else 0
    elegidos = []
    for i in range(len(duraciones)):
        es_corte_inicial_video = es_primera and i == 0
        es_corte_final_video   = es_ultima and i == len(duraciones) - 1

        if (es_corte_inicial_video or es_corte_final_video) and gancho_id:
            elegido = gancho_id                      # loop: abre y cierra con el mismo portal
        elif i == idx_principal and protagonista:
            elegido = protagonista                   # honra la elección (Gemini / ranking)
        else:
            elegido = elegir_mejor_asset_local(toma, cat, ultimos_usados + elegidos) or protagonista
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
    return cortes, protagonista

def construir_entrada_corte(toma: dict, cortes: list, protagonista_id, cat: dict,
                            fuente: str = "nodriza_visual_db") -> dict:
    archivo = cat[protagonista_id]["path_original"] if protagonista_id and protagonista_id in cat else (
        cortes[0]["archivo"] if cortes else None
    )
    p = Path(archivo) if archivo else None
    return {
        "num_toma":           toma["num"],
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
        log(f"   Toma {t['num']} | {t.get('rol','?')} → emoción: {t['emocion']} | transición: {t['transicion_entrada']}", GRIS)

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
    for toma_idx, toma in enumerate(tomas):
        cortes, protagonista = planificar_cortes_de_toma(
            toma, toma_idx, len(tomas), cat, ultimos_usados, gancho_id, gemini_clients
        )
        if not cortes:
            err(f"Toma {toma['num']} no pudo ser asignada.")
            lista_de_corte["asignaciones"].append(construir_entrada_corte(toma, [], None, cat))
            continue

        info(f"Toma {toma['num']} ({toma['duracion_s']}s) → {len(cortes)} cortes.")
        for c in cortes:
            ok(f"Toma {toma['num']} → Corte {c['orden']}: {c['nombre']} [{c['tipo']}, {c['duracion_s']}s]")
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
    args = parser.parse_args()

    if args.opcion == 1:
        run_nodriza()
    else:
        err("Opción no válida para Nodriza Visual.")
