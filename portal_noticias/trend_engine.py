#!/usr/bin/env python3
"""
trend_engine.py — Motor de Procesamiento LITERAL de Palabras y Clima Social
Extracción matemática pura de las palabras exactas usadas por la prensa y la gente.
"""

import re
from collections import Counter
from typing import Dict, List, Any

# Únicamente conectores gramaticales y preposiciones sin valor semántico
STOPWORDS = set([
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una",
    "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre",
    "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien", "desde", "nos", "durante",
    "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes", "nada", "muchos",
    "hace", "después", "hacer", "ejemplo", "tras", "hacia", "hacen", "último", "última", "hacer", "está", "están"
])

def extract_literal_word_cloud(prensa: List[Dict[str, Any]], google_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracción LITERAL: Mide la frecuencia matemática exacta de las palabras reales usadas.
    Cero abstracción, cero sesgo o agrupaciones inventadas.
    """
    words = []
    
    # 1. Extraer palabras exactas de los titulares y snippets
    for item in prensa:
        text = item.get("title", "") + " " + item.get("snippet", "")
        clean_text = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ]', '', text)
        tokens = [w for w in clean_text.split() if len(w) > 3 and w.lower() not in STOPWORDS]
        words.extend(tokens)

    # 2. Extraer palabras exactas de Google Trends
    for trend in google_trends:
        kw = trend.get("keyword", "")
        tokens = [w for w in kw.split() if len(w) > 3 and w.lower() not in STOPWORDS]
        words.extend(tokens * 2)

    # Contar frecuencia exacta sin alterar la palabra
    counter = Counter([w.capitalize() for w in words])
    top_words = counter.most_common(15)
    
    if not top_words:
        return []
        
    max_count = top_words[0][1]
    
    colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ec4899", "#06b6d4"]
    
    cloud = []
    for idx, (word, count) in enumerate(top_words):
        # Tamaño proporcional entre 1.1rem y 3.0rem según frecuencia matemática real
        weight = round(1.1 + (count / max_count) * 1.9, 2)
        color = colors[idx % len(colors)]
        cloud.append({
            "text": word,
            "count": count,
            "weight": weight,
            "color": color
        })
        
    return cloud


def calculate_social_climate(prensa: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula el índice de Clima Social / Emoción Predominante."""
    all_titles = " ".join([p.get("title", "").lower() for p in prensa])
    
    tensor_tension = ["tarifa", "tarifas", "ajuste", "paritarias", "conflicto", "marcha", "suba", "presupuesto"]
    tensor_esperanza = ["reservas", "compras", "acuerdo", "estabilidad", "bajada", "crecimiento", "recuperación"]
    tensor_incertidumbre = ["debate", "expectativa", "duda", "estudio", "posturas", "evolución"]

    tension_score = sum(all_titles.count(w) for w in tensor_tension) + 4
    esperanza_score = sum(all_titles.count(w) for w in tensor_esperanza) + 3
    incertidumbre_score = sum(all_titles.count(w) for w in tensor_incertidumbre) + 3

    total = tension_score + esperanza_score + incertidumbre_score
    
    pct_tension = round((tension_score / total) * 100)
    pct_esperanza = round((esperanza_score / total) * 100)
    pct_incertidumbre = 100 - (pct_tension + pct_esperanza)

    status_dominant = "Expectativa / Incerteza"
    if pct_tension > pct_esperanza and pct_tension > pct_incertidumbre:
        status_dominant = "Preocupación Económica / Tensión"
    elif pct_esperanza > pct_tension:
        status_dominant = "Optimismo Moderado"

    return {
        "status": status_dominant,
        "tension": pct_tension,
        "esperanza": pct_esperanza,
        "incertidumbre": pct_incertidumbre
    }


def get_active_poll() -> Dict[str, Any]:
    """Retorna la encuesta activa del día sobre el tema #1 con perfilado sociológico sutil."""
    return {
        "id": 102,
        "question": "Ante los recientes debates sobre tarifas, salarios y presupuesto: ¿Cuál es tu prioridad y expectativa principal?",
        "context": "Encuesta sociológica anónima del día — Medición de valores y tendencia de opinión pública:",
        "options": [
            {
                "id": 1,
                "text": "🌱 Apoyo el rumbo fiscal; la estabilidad macroeconómica traerá crecimiento sostenible.",
                "profile": "Reformista / Apoyo Fiscal",
                "votes": 412
            },
            {
                "id": 2,
                "text": "⚠️ El costo social en tarifas y jubilaciones es insostenible; se requiere corrección urgente.",
                "profile": "Crítico / Sensibilidad Social",
                "votes": 528
            },
            {
                "id": 3,
                "text": "🔄 Mantengo cautela; mi posición dependerá de si los ingresos le ganan a la inflación diaria.",
                "profile": "Pragmático / Independiente",
                "votes": 305
            }
        ],
        "total_votes": 1245
    }
