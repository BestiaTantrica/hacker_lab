#!/usr/bin/env python3
"""
trend_engine.py — Motor de Clasificación Temática y Encuestas de Batalla Cultural
Agrupa contenidos en 4 Ejes: Batalla Cultural, Geopolítica Rucauf, Economía Libre y Streamers/Redes.
"""

from typing import Dict, List, Any

def categorize_hub_items(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Clasifica los contenidos del Hub por los 4 ejes principales."""
    categorized = {
        "batalla_cultural": [],
        "geopolitica": [],
        "economia_gobierno": [],
        "streamers_redes": []
    }
    
    for item in items:
        cat = item.get("category", "batalla_cultural")
        if cat in categorized:
            categorized[cat].append(item)
        else:
            categorized["batalla_cultural"].append(item)
            
    return categorized


def extract_top_quotes(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extrae las frases bomba destacadas del día para compartir en redes."""
    quotes = []
    for item in items:
        if item.get("quote"):
            quotes.append({
                "author": item.get("author"),
                "quote": item.get("quote"),
                "source": item.get("source"),
                "link": item.get("link")
            })
    return quotes[:6]


def get_active_polls() -> List[Dict[str, Any]]:
    """Encuestas Activas de Batalla Cultural & Reformas de Estado."""
    return [
        {
            "id": 201,
            "topic": "🏛️ Batalla de las Ideas",
            "question": "¿Cuál considerás que es la prioridad clave en la batalla cultural hoy?",
            "context": "Encuesta 1 — Formación de pensamiento y defensa de la libertad:",
            "options": [
                {"id": 1, "text": "🎓 Dar la batalla en las universidades e instituciones educativas.", "votes": 0},
                {"id": 2, "text": "📱 Derribar el relato en redes sociales y medios digitales.", "votes": 0},
                {"id": 3, "text": "📈 Demostrar con datos el éxito de la economía de libre mercado.", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 202,
            "topic": "🌍 Geopolítica Occidental",
            "question": "Análisis Geopolítico (Rucauf): ¿Cómo evaluás la inserción internacional de Argentina?",
            "context": "Encuesta 2 — Posicionamiento trasatlántico e inversiones:",
            "options": [
                {"id": 1, "text": "🌐 Excelente: Nos afianza como polo de atracción y seguridad en el Atlántico Sur.", "votes": 0},
                {"id": 2, "text": "👍 Positiva: Atrae inversiones privadas RIGI en energía y minerales.", "votes": 0},
                {"id": 3, "text": "🔄 En proceso: Requiere mayor integración comercial estratégica.", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 203,
            "topic": "📺 Formatos de Difusión",
            "question": "¿A través de qué vía te informás y seguís los análisis políticos?",
            "context": "Encuesta 3 — Nuevos medios vs prensa tradicional:",
            "options": [
                {"id": 1, "text": "📺 Streams en YouTube / Twitch (Neura, Carajo, Break Cero).", "votes": 0},
                {"id": 2, "text": "📱 X (Twitter), TikTok y canales directos de referentes.", "votes": 0},
                {"id": 3, "text": "📰 Portales digitales especializados (La Derecha Diario).", "votes": 0}
            ],
            "total_votes": 0
        }
    ]
