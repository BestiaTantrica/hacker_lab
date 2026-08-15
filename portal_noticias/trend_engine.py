#!/usr/bin/env python3
"""
trend_engine.py — Motor de Análisis Dual (Prensa vs Redes), Taxonomía Emocional y Multi-Encuestas
Procesa agendas mediáticas y ciudadanas, desacople/divergencia %, sub-nubes por 4 emociones y encuestas temáticas.
"""

import re
from collections import Counter
from typing import Dict, List, Any

STOPWORDS = set([
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "nos", "durante",
    "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos",
    "hace", "después", "hacer", "ejemplo", "tras", "hacia", "hacen", "último", "última", "está", "están", "sobre"
])

# DICCIONARIOS DE EMOCIONALIDAD Y TEMAS
TENSION_KEYWORDS = set(["presupuesto", "tarifa", "tarifas", "ajuste", "paritarias", "conflicto", "marcha", "suba", "gremio", "gremios", "coparticipación"])
INCERTIDUMBRE_KEYWORDS = set(["dólar", "dolar", "banco", "central", "congreso", "mercado", "expectativa", "duda", "debate", "cambios", "consumo", "indec"])
ESPERANZA_KEYWORDS = set(["reservas", "compras", "acuerdo", "estabilidad", "bajada", "crecimiento", "recuperación", "obras", "turismo", "producción"])
INDIGNACION_KEYWORDS = set(["tarifazo", "jubilaciones", "corte", "aumento", "servicio", "servicios", "suba", "boleto", "transporte", "gasto", "inflación"])

def clean_tokens(text: str) -> List[str]:
    clean_text = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ]', '', text)
    return [w.capitalize() for w in clean_text.split() if len(w) > 3 and w.lower() not in STOPWORDS]

def extract_dual_word_clouds(prensa: List[Dict[str, Any]], redes: List[Dict[str, Any]], google_trends: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera las nubes separadas de Prensa Tradicional vs Redes Sociales y el Score de Divergencia."""
    words_prensa = []
    for item in prensa:
        text = item.get("title", "") + " " + item.get("snippet", "")
        words_prensa.extend(clean_tokens(text))

    for trend in google_trends:
        words_prensa.extend(clean_tokens(trend.get("keyword", "")) * 3)

    words_redes = []
    for post in redes:
        text = post.get("content", "") + " " + post.get("top_comment", "")
        words_redes.extend(clean_tokens(text))

    counter_prensa = Counter(words_prensa)
    counter_redes = Counter(words_redes)

    top_prensa = counter_prensa.most_common(10)
    top_redes = counter_redes.most_common(10)

    # Cálculo de Desacople / Divergencia de Agenda (%)
    set_p = set([w[0].lower() for w in top_prensa])
    set_r = set([w[0].lower() for w in top_redes])
    intersection = set_p.intersection(set_r)
    union = set_p.union(set_r)
    similarity = len(intersection) / len(union) if union else 1.0
    divergence_score = round((1.0 - similarity) * 100)

    colors_p = ["#3b82f6", "#60a5fa", "#93c5fd", "#1d4ed8", "#2563eb"]
    colors_r = ["#ec4899", "#f43f5e", "#fb7185", "#8b5cf6", "#a855f7"]
    sizes = [3.2, 2.4, 2.0, 1.6, 1.3, 1.1, 1.0, 0.95, 0.9, 0.85]

    cloud_prensa = []
    for idx, (word, count) in enumerate(top_prensa):
        cloud_prensa.append({
            "text": word,
            "count": count,
            "weight": sizes[idx] if idx < len(sizes) else 0.9,
            "color": colors_p[idx % len(colors_p)],
            "source": "prensa"
        })

    cloud_redes = []
    for idx, (word, count) in enumerate(top_redes):
        cloud_redes.append({
            "text": word,
            "count": count,
            "weight": sizes[idx] if idx < len(sizes) else 0.9,
            "color": colors_r[idx % len(colors_r)],
            "source": "redes"
        })

    return {
        "cloud_prensa": cloud_prensa,
        "cloud_redes": cloud_redes,
        "divergence_score": divergence_score
    }


def extract_emotional_clouds(prensa: List[Dict[str, Any]], redes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera las 4 nubes emocionales filtrables con artículos de prensa y posts de redes emparejados."""
    spectrums = {
        "tension": {"title": "🔴 Tensión & Conflicto", "keywords": TENSION_KEYWORDS, "color": "#f59e0b"},
        "incertidumbre": {"title": "🟠 Incerteza & Preocupación", "keywords": INCERTIDUMBRE_KEYWORDS, "color": "#3b82f6"},
        "esperanza": {"title": "🟢 Esperanza & Estabilidad", "keywords": ESPERANZA_KEYWORDS, "color": "#10b981"},
        "indignacion": {"title": "🟣 Indignación Ciudadana", "keywords": INDIGNACION_KEYWORDS, "color": "#ec4899"}
    }

    result = {}
    for emo_key, spec in spectrums.items():
        kws = spec["keywords"]
        
        emo_words = []
        matched_prensa = []
        matched_redes = []

        for p in prensa:
            txt = (p.get("title", "") + " " + p.get("snippet", "")).lower()
            if any(k in txt for k in kws):
                matched_prensa.append(p)
                emo_words.extend(clean_tokens(txt))

        for r in redes:
            txt = (r.get("content", "") + " " + r.get("top_comment", "")).lower()
            if r.get("emotion") == emo_key or any(k in txt for k in kws):
                matched_redes.append(r)
                emo_words.extend(clean_tokens(txt))

        cnt = Counter([w for w in emo_words if any(k in w.lower() for k in kws) or len(w) > 4])
        top_w = cnt.most_common(8)

        cloud_tags = []
        sizes = [2.8, 2.2, 1.8, 1.5, 1.2, 1.0, 0.95, 0.9]
        for idx, (word, count) in enumerate(top_w):
            cloud_tags.append({
                "text": word,
                "count": count,
                "weight": sizes[idx] if idx < len(sizes) else 0.9,
                "color": spec["color"]
            })

        result[emo_key] = {
            "title": spec["title"],
            "color": spec["color"],
            "word_cloud": cloud_tags,
            "prensa": matched_prensa[:4],
            "redes": matched_redes[:4]
        }

    return result


def calculate_social_climate(prensa: List[Dict[str, Any]], redes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula el clima social combinando prensa y redes sociales."""
    all_text = " ".join([p.get("title", "").lower() for p in prensa]) + " " + " ".join([r.get("content", "").lower() for r in redes])

    score_tension = sum(all_text.count(w) for w in TENSION_KEYWORDS) + 8
    score_esperanza = sum(all_text.count(w) for w in ESPERANZA_KEYWORDS) + 5
    score_incertidumbre = sum(all_text.count(w) for w in INCERTIDUMBRE_KEYWORDS) + 6
    score_indignacion = sum(all_text.count(w) for w in INDIGNACION_KEYWORDS) + 7

    total = score_tension + score_esperanza + score_incertidumbre + score_indignacion
    
    pct_tension = round((score_tension / total) * 100)
    pct_esperanza = round((score_esperanza / total) * 100)
    pct_incertidumbre = round((score_incertidumbre / total) * 100)
    pct_indignacion = 100 - (pct_tension + pct_esperanza + pct_incertidumbre)

    return {
        "status": "Preocupación Económica & Tensión Tarifaria",
        "tension": pct_tension,
        "esperanza": pct_esperanza,
        "incertidumbre": pct_incertidumbre,
        "indignacion": pct_indignacion
    }


def get_active_polls() -> List[Dict[str, Any]]:
    """Suite de Múltiples Encuestas Activas (Abarcabilidad Total en 3 Ejes)."""
    return [
        {
            "id": 101,
            "topic": "⚡ Tarifas & Costo de Vida",
            "question": "¿Cómo impacta el nuevo esquema de tarifas y transporte en tu presupuesto mensual?",
            "context": "Encuesta 1 de 3 — Abarcabilidad en servicios y consumo diario:",
            "options": [
                {"id": 1, "text": "🔴 Impacto alto: Tuve que ajustar consumos y reducir salidas.", "votes": 0},
                {"id": 2, "text": "🟡 Impacto moderado: Absorbo el costo recortando otros gastos menores.", "votes": 0},
                {"id": 3, "text": "🟢 Bajo impacto: Mantengo mi nivel habitual de gastos fijos.", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 102,
            "topic": "💼 Trabajo & Paritarias",
            "question": "Paritarias y Salarios 2026: ¿Qué expectativa tenés sobre la evolución de tu ingreso?",
            "context": "Encuesta 2 de 3 — Clima laboral y poder adquisitivo:",
            "options": [
                {"id": 1, "text": "🌱 Los aumentos le ganarán a la inflación proyectada.", "votes": 0},
                {"id": 2, "text": "⚠️ El salario correrá por detrás del ritmo de aumentos.", "votes": 0},
                {"id": 3, "text": "🔄 Situación neutra: Empate técnico con los precios de alimentos.", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 103,
            "topic": "🏛️ Prioridad Presupuestaria",
            "question": "Debate Presupuesto 2026: ¿Cuál debería ser la prioridad de asignación de recursos?",
            "context": "Encuesta 3 de 3 — Agenda de inversión pública y federalismo:",
            "options": [
                {"id": 1, "text": "🧱 Obras públicas e infraestructura en transporte y provincias.", "votes": 0},
                {"id": 2, "text": "🎓 Educación universitaria, salud pública y ciencia.", "votes": 0},
                {"id": 3, "text": "📈 Consolidación del superávit fiscal y compras de reservas.", "votes": 0}
            ],
            "total_votes": 0
        }
    ]
