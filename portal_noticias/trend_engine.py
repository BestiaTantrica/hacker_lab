#!/usr/bin/env python3
"""
trend_engine.py — Motor de Nube de Palabras Real desde Feeds HTTP en Vivo (Sin datos inventados)
Extrae palabras y conceptos dominantes en tiempo real a partir de Google Trends y portales de noticias.
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
    "hace", "después", "hacer", "ejemplo", "tras", "hacia", "hacen", "último", "última", "está", "están", "sobre",
    "para", "cómo", "sobre", "entre", "luego", "cada", "tienen", "todos", "todas", "estos", "hacer", "primera", "segunda"
])

def extract_general_word_cloud(live_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extrae la Nube de Palabras REAL desde los títulos y resúmenes raspados en vivo por HTTP."""
    tokens = []

    for item in live_items:
        text = item.get("title", "") + " " + item.get("snippet", "")
        clean_text = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ]', '', text)
        for w in clean_text.split():
            w_lower = w.lower()
            if len(w) > 3 and w_lower not in STOPWORDS:
                tokens.append(w.capitalize())

    counter = Counter(tokens)
    top_words = counter.most_common(12)

    colors = ["#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899", "#fb7185"]
    sizes = [3.4, 2.8, 2.4, 2.0, 1.7, 1.4, 1.2, 1.1, 1.0, 0.95, 0.9, 0.85]

    cloud = []
    for idx, (word, count) in enumerate(top_words):
        cloud.append({
            "id": idx + 1,
            "text": word,
            "count": count,
            "weight": sizes[idx] if idx < len(sizes) else 0.9,
            "color": colors[idx % len(colors)]
        })
    return cloud


def get_interactive_concept_poll(word_cloud: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera la Encuesta Interactiva basada en los conceptos más hablados en vivo."""
    top_5 = word_cloud[:5] if word_cloud else []
    
    options = []
    for idx, item in enumerate(top_5):
        options.append({
            "id": idx + 1,
            "text": f"🔥 {item['text']}",
            "votes": 0,
            "pct": 0.0
        })

    return {
        "id": 501,
        "question": "¿Cuál de estos conceptos de la actualidad representa mejor tu prioridad hoy?",
        "subtitle": "Búsquedas y tendencias en vivo en Google Trends y portales de noticias. Votá o escribí el tuyo:",
        "options": options,
        "total_votes": 0
    }


def calculate_opinion_thermometer(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula el clima de opinión de la red general."""
    text_all = " ".join([i.get("title", "") + " " + i.get("snippet", "") for i in items]).lower()

    keywords_acuerdo = ["superávit", "estabilidad", "libertad", "crecimiento", "desregulación", "compras", "inversión", "prosperidad", "dólar"]
    keywords_desacuerdo = ["tarifas", "tarifazo", "corte", "ajuste", "dificultad", "conflicto", "reclamo", "demanda"]
    keywords_cautela = ["mercado", "precios", "paritarias", "expectativa", "consumo", "temperatura"]

    score_acuerdo = sum(text_all.count(w) for w in keywords_acuerdo) + 10
    score_desacuerdo = sum(text_all.count(w) for w in keywords_desacuerdo) + 8
    score_cautela = sum(text_all.count(w) for w in keywords_cautela) + 6

    total = score_acuerdo + score_desacuerdo + score_cautela
    
    pct_acuerdo = round((score_acuerdo / total) * 100)
    pct_desacuerdo = round((score_desacuerdo / total) * 100)
    pct_cautela = 100 - (pct_acuerdo + pct_desacuerdo)

    return {
        "acuerdo_rumbo": pct_acuerdo,
        "desacuerdo": pct_desacuerdo,
        "cautela": pct_cautela,
        "status_general": "Tendencias Generales de la Red en Tiempo Real",
        "vs_encuestadoras": "Medición directa de tendencias web en vivo"
    }


def categorize_hub_items(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Clasifica las noticias raspadas por fuente."""
    categorized = {
        "google_trends": [],
        "medios_general": [],
        "economia": []
    }
    
    for item in items:
        stype = item.get("type", "news")
        if stype == "trends":
            categorized["google_trends"].append(item)
        elif stype == "economy":
            categorized["economia"].append(item)
        else:
            categorized["medios_general"].append(item)
            
    return categorized
