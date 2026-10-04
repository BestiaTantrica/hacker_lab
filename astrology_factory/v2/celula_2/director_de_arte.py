#!/usr/bin/env python3
"""
🎬 DIRECTOR DE ARTE — Célula 2
Lee el texto de cada toma del timeline y decide:
  1. La EMOCIÓN del beat (local, sin gastar API)
  2. Las PALABRAS CLAVE visuales para mejorar el matching semántico
  3. La TRANSICIÓN xfade más adecuada para ese cambio de escena

Se usa como módulo importable desde nodriza_visual.py y ensamblador_final.py.
No hace llamadas a la API de Gemini — trabaja con reglas locales de vocabulario.
"""

from __future__ import annotations
import re
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# VOCABULARIO EMOCIONAL
# Cada emoción tiene:
#   - palabras que la activan en el texto del narrador
#   - los tags visuales ideales en el catálogo de assets
#   - la transición xfade preferida y la alternativa
# ─────────────────────────────────────────────────────────────────────────────

EMOCIONES: dict[str, dict] = {
    "fuego": {
        "palabras_clave": [
            "arde", "ardor", "quema", "quemar", "llama", "brasa", "calor",
            "fiebre", "pasión", "urgencia", "explosión", "estalla", "explosiv",
            "marte", "sagitario", "aries", "acción", "impulso", "energía",
            "chispa", "detonar", "detonación",
        ],
        "tags_visuales": [
            "fuego", "llama", "rojo", "naranja", "brasa", "magma", "lava",
            "tormenta solar", "fuego abstracto"
        ],
        "xfade_principal": "fade",
        "xfade_alternativo": "fadewhite",
        "opacidad_boost": 0.12,   # imágenes más sólidas, más presentes
    },
    "agua": {
        "palabras_clave": [
            "agua", "profundid", "océano", "mar", "rio", "fluye", "fluir",
            "inunda", "sumerge", "lágrima", "llanto", "sensible", "sentir",
            "escorpio", "piscis", "cáncer", "venus", "emocional",
            "intuitiv", "inconsciente", "abismo",
        ],
        "tags_visuales": [
            "agua", "océano", "azul", "profundo", "transparente", "reflejo",
            "cristal", "niebla", "vapor",
        ],
        "xfade_principal": "dissolve",
        "xfade_alternativo": "fadeblack",
        "opacidad_boost": -0.05,   # más etéreo, más difuso
    },
    "tierra": {
        "palabras_clave": [
            "tierra", "raíz", "enraiz", "peso", "gravedad", "solidez", "sólido",
            "construye", "construir", "base", "cimiento", "capricornio", "tauro",
            "virgo", "trabajo", "disciplina", "estructura", "estabilidad",
        ],
        "tags_visuales": [
            "tierra", "piedra", "montaña", "raíz", "oscuro", "mineral",
            "geometría", "mandala", "espiral", "arquitectura sagrada",
        ],
        "xfade_principal": "smoothleft",
        "xfade_alternativo": "fade",
        "opacidad_boost": 0.0,
    },
    "aire": {
        "palabras_clave": [
            "aire", "viento", "vuelo", "expansión", "libertad", "mente",
            "pensamiento", "idea", "acuario", "géminis", "libra", "mercurio",
            "júpiter", "horizonte", "viaje", "apertura",
            "posibilidad", "visión", "claridad",
        ],
        "tags_visuales": [
            "cielo", "nubes", "viento", "fractal", "abstracto", 
            "geometría sagrada", "luz", "blanco", "celeste"
        ],
        "xfade_principal": "fadewhite",
        "xfade_alternativo": "fade",
        "opacidad_boost": -0.08,   # casi etéreo
    },
    "cosmos": {
        "palabras_clave": [
            "espacio", "cosmos", "universo", "planeta", "estrella", "galaxia",
            "nebulosa", "astral", "constelación", "satélite", "luna", "sol",
            "plutón", "urano", "neptuno", "saturno", "marte", "venus",
        ],
        "tags_visuales": [
            "cosmos", "galaxia", "estrella", "espacio", "nebulosa", 
            "supernova", "luna", "planetas", "vía láctea"
        ],
        "xfade_principal": "fade",
        "xfade_alternativo": "dissolve",
        "opacidad_boost": 0.05,
    },
    "misterio": {
        "palabras_clave": [
            "sombra", "oscuridad", "secreto", "oculto", "velado", "abismo",
            "ketu", "nodo sur", "karma", "pasado",
            "ancestral", "inconsciente", "profundo", "umbral", "portal",
            "transformación", "muerte", "renacer",
        ],
        "tags_visuales": [
            "oscuro", "negro", "sombra", "luna negra", "eclipse", "penumbra",
            "humo", "niebla", "misterio", "esotérico", "runa",
        ],
        "xfade_principal": "fadeblack",
        "xfade_alternativo": "dissolve",
        "opacidad_boost": -0.1,
    },
    "revelacion": {
        "palabras_clave": [
            "revela", "revelar", "desvela", "claridad", "verdad", "comprende",
            "entende", "insight", "darse cuenta", "el momento", "ahora",
            "hoy", "este tránsito", "apertura", "luz", "despeja", "ilumina",
        ],
        "tags_visuales": [
            "luz", "dorado", "sol", "amanecer", "espiral", "fractal",
            "geometría sagrada", "mandala", "portal",
        ],
        "xfade_principal": "fadewhite",
        "xfade_alternativo": "fade",
        "opacidad_boost": 0.1,
    },
    "llamada_accion": {
        "palabras_clave": [
            "sígueme", "sigue", "comenta", "comparte", "guarda", "activa",
            "activen", "notificación", "link", "enlace", "bio", "perfil",
            "únete", "cta", "ahora", "hoy mismo", "no te pierdas",
        ],
        "tags_visuales": [
            "fractal", "abstracto", "espiral", "geometría"
        ],
        "xfade_principal": "smoothleft",
        "xfade_alternativo": "fade",
        "opacidad_boost": 0.05,
    },
}

# Emoción por defecto si no se detecta ninguna
EMOCION_DEFAULT = "aire"

# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES PÚBLICAS
# ─────────────────────────────────────────────────────────────────────────────

def detectar_emocion(texto: str, rol: Optional[str] = None) -> str:
    """
    Detecta la emoción dominante de un beat a partir de su texto.
    No hace llamadas a la API — trabaja con vocabulario local.
    Devuelve el nombre de la emoción (clave de EMOCIONES).
    """
    if not texto:
        return _emocion_por_rol(rol)

    texto_lower = texto.lower()

    # Si el rol ya lo dice claramente, priorizarlo
    if rol:
        rol_lower = rol.lower()
        if "cta" in rol_lower or "llamada" in rol_lower:
            return "llamada_accion"
        if "gancho" in rol_lower:
            return "revelacion"

    # Contar hits por emoción
    scores: dict[str, int] = {e: 0 for e in EMOCIONES}
    for emocion, data in EMOCIONES.items():
        for kw in data["palabras_clave"]:
            if kw in texto_lower:
                scores[emocion] += 1

    mejor = max(scores, key=lambda e: scores[e])
    if scores[mejor] == 0:
        return _emocion_por_rol(rol)
    return mejor


def _emocion_por_rol(rol: Optional[str]) -> str:
    """Emoción de fallback según el rol narrativo."""
    if not rol:
        return EMOCION_DEFAULT
    rol = rol.lower()
    if "gancho" in rol:
        return "revelacion"
    if "cuerpo" in rol or "efecto" in rol:
        return "agua"
    if "mecanica" in rol or "astrologica" in rol:
        return "tierra"
    if "cta" in rol or "llamada" in rol:
        return "llamada_accion"
    if "afrontar" in rol or "constructiv" in rol:
        return "fuego"
    return EMOCION_DEFAULT


def tags_visuales_para_emocion(emocion: str) -> list[str]:
    """Tags visuales ideales para buscar en el catálogo de assets."""
    return EMOCIONES.get(emocion, EMOCIONES[EMOCION_DEFAULT])["tags_visuales"]


def transicion_para_emocion(emocion: str, alternativo: bool = False) -> str:
    """Nombre de transición xfade para una emoción dada."""
    data = EMOCIONES.get(emocion, EMOCIONES[EMOCION_DEFAULT])
    return data["xfade_alternativo"] if alternativo else data["xfade_principal"]


def opacidad_boost(emocion: str) -> float:
    """Ajuste de opacidad (±) según la emoción. Se suma al alpha base."""
    return EMOCIONES.get(emocion, EMOCIONES[EMOCION_DEFAULT]).get("opacidad_boost", 0.0)


def score_semantico(texto_toma: str, emocion_toma: str, tags_asset: list[str]) -> float:
    """
    Calcula un bonus semántico para el matching imagen-beat.
    Devuelve un float en [0.0, 3.0] que se suma al score base.
    """
    if not tags_asset:
        return 0.0

    tags_ideales = tags_visuales_para_emocion(emocion_toma)
    tags_lower = [t.lower() for t in tags_asset]
    texto_lower = texto_toma.lower()

    bonus = 0.0
    # Cada tag visual ideal que aparece en los tags del asset suma
    for tag in tags_ideales:
        if any(tag in t for t in tags_lower):
            bonus += 0.6

    # Cada palabra clave del texto que aparece en los tags suma
    palabras_texto = set(re.findall(r"\b\w{4,}\b", texto_lower))
    for palabra in palabras_texto:
        if any(palabra in t for t in tags_lower):
            bonus += 0.3

    return min(bonus, 3.0)


def enriquecer_tomas(tomas: list[dict]) -> list[dict]:
    """
    Toma la lista de tomas del timeline y añade a cada una:
      - 'emocion': string detectado localmente
      - 'tags_visuales_ideales': lista de tags recomendados
      - 'transicion_entrada': xfade recomendado para la transición con la toma anterior
    Devuelve la lista enriquecida (no modifica las originales).
    """
    enriquecidas = []
    for toma in tomas:
        t = dict(toma)
        emocion = detectar_emocion(t.get("texto", ""), t.get("rol"))
        t["emocion"] = emocion
        t["tags_visuales_ideales"] = tags_visuales_para_emocion(emocion)
        t["transicion_entrada"] = transicion_para_emocion(emocion)
        enriquecidas.append(t)
    return enriquecidas


# ─────────────────────────────────────────────────────────────────────────────
# Demo rápida (python director_de_arte.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ejemplos = [
        {"num": 1, "rol": "gancho",                   "texto": "La densidad estalla... y de pronto... el aire vuelve a quemar"},
        {"num": 2, "rol": "efecto_cuerpo_emocion",    "texto": "Este cuatro de octubre la llegada de la Luna a Sagitario abre el horizonte"},
        {"num": 3, "rol": "mecanica_astrologica",     "texto": "Lo sentimos en el pulso mientras el sextil entre la Luna y Saturno estabiliza"},
        {"num": 4, "rol": "afrontarlo_constructivamente", "texto": "Es un tránsito que invita a observar hacia dónde apunta el deseo"},
        {"num": 5, "rol": "cta",                      "texto": "Sígueme para no perderte el próximo tránsito"},
    ]
    print("\n🎬 DIRECTOR DE ARTE — Demo\n")
    for t in enriquecer_tomas(ejemplos):
        print(f"  Toma {t['num']} | rol: {t['rol']}")
        print(f"    Emoción detectada : {t['emocion']}")
        print(f"    Tags ideales      : {t['tags_visuales_ideales'][:4]}")
        print(f"    Transición xfade  : {t['transicion_entrada']}")
        print()
