#!/usr/bin/env python3
"""
trend_engine.py — Motor de Procesamiento de Tendencias, Nube de Palabras y Clima Social
Parte de 'portal_noticias'.
"""

import re
from collections import Counter
from typing import Dict, List, Any

# Palabras vacías en español a omitir en la nube
STOPWORDS = set([
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "nos", "durante",
    "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos",
    "hace", "después", "hacer", "ejemplo", "hace", "tras", "hacia", "hacen", "último", "última"
])

def extract_word_cloud(prensa: List[Dict[str, Any]], google_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Genera la lista de palabras clave más frecuentes con su ponderación para la Nube de Palabras."""
    words = []
    
    # 1. Extraer palabras de los titulares de noticias
    for item in prensa:
        text = item.get("title", "") + " " + item.get("snippet", "")
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = [w for w in clean_text.split() if len(w) > 3 and w not in STOPWORDS]
        words.extend(tokens)

    # 2. Extraer palabras de Google Trends (con peso doble)
    for trend in google_trends:
        kw = trend.get("keyword", "").lower()
        tokens = [w for w in kw.split() if len(w) > 3 and w not in STOPWORDS]
        words.extend(tokens * 2)

    counter = Counter(words)
    top_words = counter.most_common(12)
    
    # Normalizar tamaño visual (font-size em)
    if not top_words:
        return []
    max_count = top_words[0][1]
    
    cloud = []
    for word, count in top_words:
        weight = round(0.9 + (count / max_count) * 1.1, 2) # entre 0.9em y 2.0em
        cloud.append({"text": word.capitalize(), "count": count, "weight": weight})
        
    return cloud


def calculate_social_climate(prensa: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula el índice de Clima Social / Emoción Predominante."""
    all_titles = " ".join([p.get("title", "").lower() for p in prensa])
    
    tensor_tension = ["ajuste", "tarifas", "inflación", "despidos", "marcha", "protesta", "tensión", "conflicto"]
    tensor_esperanza = ["desaceleración", "bajada", "crecimiento", "acuerdo", "inversión", "superávit", "estabilidad"]
    tensor_incertidumbre = ["debate", "duda", "posturas", "espera", "congreso", "voto", "futuro"]

    tension_score = sum(all_titles.count(w) for w in tensor_tension) + 3
    esperanza_score = sum(all_titles.count(w) for w in tensor_esperanza) + 2
    incertidumbre_score = sum(all_titles.count(w) for w in tensor_incertidumbre) + 4

    total = tension_score + esperanza_score + incertidumbre_score
    
    pct_tension = round((tension_score / total) * 100)
    pct_esperanza = round((esperanza_score / total) * 100)
    pct_incertidumbre = 100 - (pct_tension + pct_esperanza)

    status_dominant = "Tensión & Cautela"
    if pct_esperanza > pct_tension and pct_esperanza > pct_incertidumbre:
        status_dominant = "Optimismo Moderado"
    elif pct_incertidumbre >= pct_tension and pct_incertidumbre >= pct_esperanza:
        status_dominant = "Expectativa / Incerteza"

    return {
        "status": status_dominant,
        "tension": pct_tension,
        "esperanza": pct_esperanza,
        "incertidumbre": pct_incertidumbre
    }


def get_active_poll() -> Dict[str, Any]:
    """Retorna la encuesta del Termómetro Social activa con perfilado sociológico sutil."""
    return {
        "id": 101,
        "question": "¿Cómo evaluás el rumbo económico y tu expectativa para los próximos 6 meses?",
        "context": "Frente a las variaciones en tarifas, inflación y salarios registradas en los medios esta semana:",
        "options": [
            {
                "id": 1,
                "text": "🌱 El esfuerzo actual vale la pena; habrá recuperación a mediano plazo.",
                "profile": "Reformista / Apoyo Fiscal",
                "votes": 342
            },
            {
                "id": 2,
                "text": "⚠️ El costo social es excesivo; se deben corregir las medidas urgentes.",
                "profile": "Crítico / Sensibilidad Social",
                "votes": 418
            },
            {
                "id": 3,
                "text": "🔄 Mantengo cautela; dependerá de si los ingresos le ganan a los gastos.",
                "profile": "Pragmático / Independiente",
                "votes": 215
            }
        ],
        "total_votes": 975
    }
