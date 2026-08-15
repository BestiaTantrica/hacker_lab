#!/usr/bin/env python3
"""
trend_engine.py — Motor de Clasificación Temática y Encuestas del Ecosistema Liberal
Agrupa contenidos en 5 Ejes: Streamers/YouTubers, Batalla Cultural (Laje), Geopolítica (Rucauf), Economía Libre y Medios Digitales.
"""

from typing import Dict, List, Any

def categorize_hub_items(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Clasifica los contenidos del Hub por los 5 ejes principales del ecosistema."""
    categorized = {
        "streamers_youtubers": [],
        "batalla_cultural": [],
        "geopolitica": [],
        "economia_gobierno": [],
        "medios_digitales": []
    }
    
    for item in items:
        cat = item.get("category", "streamers_youtubers")
        if cat in categorized:
            categorized[cat].append(item)
        else:
            categorized["streamers_youtubers"].append(item)
            
    return categorized


def extract_top_quotes(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extrae las frases bomba destacadas de influencers, streamers y referentes del día."""
    quotes = []
    for item in items:
        if item.get("quote"):
            quotes.append({
                "author": item.get("author"),
                "handle": item.get("handle", ""),
                "quote": item.get("quote"),
                "source": item.get("source"),
                "link": item.get("link")
            })
    return quotes[:8]


def get_active_polls() -> List[Dict[str, Any]]:
    """Encuestas Activas de la Comunidad Liberal & Batalla Cultural."""
    return [
        {
            "id": 301,
            "topic": "📺 Creadores & Streamers Favoritos",
            "question": "¿Qué tipo de formato o creador preferís para seguir la actualidad diaria?",
            "context": "Encuesta de Comunidad — Formatos digitales más valorados:",
            "options": [
                {"id": 1, "text": "🔥 YouTubers & Análisis Diario (Mate con Mote, Tipito Enojado, Peluca Milei).", "votes": 0},
                {"id": 2, "text": "🎙️ Streaming & Debates en Vivo (Carajo / La Misa, Break Cero, Neura).", "votes": 0},
                {"id": 3, "text": "🎓 Batalla Cultural & Filosofía (Agustín Laje, Axel Kaiser, FPP).", "votes": 0},
                {"id": 4, "text": "📰 Noticias Digitales Directas (La Derecha Diario).", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 302,
            "topic": "🌍 Geopolítica Occidental (Rucauf)",
            "question": "¿Cómo evaluás el nuevo posicionamiento estratégico internacional de Argentina?",
            "context": "Encuesta de Geopolítica — Alineación trasatlántica y comercio libre:",
            "options": [
                {"id": 1, "text": "🌐 Excelente: Nos consolida como potencia de libertad en el Atlántico Sur.", "votes": 0},
                {"id": 2, "text": "📈 Muy bueno: Atrae inversiones privadas RIGI en energía y minerales.", "votes": 0},
                {"id": 3, "text": "🔄 En desarrollo: Requiere acelerar acuerdos de libre comercio.", "votes": 0}
            ],
            "total_votes": 0
        },
        {
            "id": 303,
            "topic": "📈 Reformas & Desregulación",
            "question": "De las reformas estructurales en marcha, ¿cuál impacta más positivamente en el día a día?",
            "context": "Encuesta de Economía — Impacto en el sector privado y familias:",
            "options": [
                {"id": 1, "text": "🚫 Cero Inflación y fin del déficit fiscal como regla sagrada.", "votes": 0},
                {"id": 2, "text": "📜 Desregulación (Sturzenegger): Eliminación de trámites e impuestos distorsivos.", "votes": 0},
                {"id": 3, "text": "💼 Libertad de contratación y auge del crédito hipotecario/PyME.", "votes": 0}
            ],
            "total_votes": 0
        }
    ]
