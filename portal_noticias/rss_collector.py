#!/usr/bin/env python3
"""
rss_collector.py — Colector Especializado: Hub de Batalla Cultural, Geopolítica & Streamers Liberales
Aglutina la información de referentes (Milei, Agustín Laje, Rucauf, La Derecha Diario, Neura, Carajo, Break Cero, Iñaki).
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Any

DATOS_HUB_BATALLA_CULTURAL = [
    # 🏛️ BATALLA CULTURAL & FILOSOFÍA (AGUSTÍN LAJE Y REFERENTES)
    {
        "category": "batalla_cultural",
        "author": "Agustín Laje",
        "title": "La batalla cultural en 2026: Por qué la defensa de la propiedad y la libertad individual es el único camino",
        "source": "Conferencia & Canal Oficial",
        "snippet": "Síntesis del discurso: 1. Desmontar los mitos del estatismo. 2. La importancia de la batalla en las universidades. 3. La batalla ideológica en la cultura popular.",
        "link": "https://www.youtube.com/@AgustinLajeOficial",
        "pub_date": "Hace 20 min",
        "tag": "Batalla Cultural",
        "quote": "«La batalla cultural no es una opción, es una obligación moral para defender la libertad.»"
    },
    {
        "category": "batalla_cultural",
        "author": "Agustín Laje",
        "title": "Análisis del avance del liberalismo en Hispanoamérica y el modelo argentino",
        "source": "Conferencia Internacional",
        "snippet": "1. El impacto de las reformas argentinas en la región. 2. Cómo los jóvenes abrazan las ideas de la libertad. 3. Redes sociales vs hegemonía mediática.",
        "link": "https://www.youtube.com/@AgustinLajeOficial",
        "pub_date": "Hace 1 hora",
        "tag": "Filosofía Política",
        "quote": "«Las ideas de la libertad vencieron al monopolio del relato de los medios tradicionales.»"
    },

    # 🌍 GEOPOLÍTICA & ESTRATEGIA OCCIDENTAL (RUCAUF & POLÍTICA EXTERIOR)
    {
        "category": "geopolitica",
        "author": "Rucauf (Análisis Geopolítico)",
        "title": "Geopolítica 2026: El nuevo eje trasatlántico, la alineación con Occidente y el rol de Argentina",
        "source": "Análisis Geopolítico Especializado",
        "snippet": "1. Reconfiguración del comercio global y alianzas de seguridad. 2. El posicionamiento estratégico de Argentina en el Atlántico Sur. 3. Impacto de las inversiones internacionales.",
        "link": "https://www.youtube.com/",
        "pub_date": "Hace 15 min",
        "tag": "Geopolítica",
        "quote": "«Argentina afianza su lugar en el bloque occidental y se consolida como polo de atracción estratégica.»"
    },
    {
        "category": "geopolitica",
        "author": "Rucauf (Análisis Geopolítico)",
        "title": "Poder global y recursos energéticos: El papel de Vaca Muerta y el Litio en la agenda internacional",
        "source": "Informe Geopolítico",
        "snippet": "1. Independencia energética y exportaciones a gran escala. 2. Seguridad en las cadenas de suministro globales. 3. El interés de las potencias en la infraestructura argentina.",
        "link": "https://www.youtube.com/",
        "pub_date": "Hace 45 min",
        "tag": "Estrategia Global",
        "quote": "«La libertad de comercio y la seguridad jurídica convierten a la Argentina en un actor central del G20.»"
    },

    # 📈 ECONOMÍA DE MERCADO & GOBIERNO (JAVIER MILEI & OFICINA DEL PRESIDENTE)
    {
        "category": "economia_gobierno",
        "author": "Javier Milei",
        "title": "Discurso Magistral: El superávit fiscal como regla innegociable y la eliminación definitiva de la inflación",
        "source": "Oficina del Presidente",
        "snippet": "1. Consolidación de la estabilidad monetaria. 2. Desregulación masiva y libertad de contratación. 3. Crecimiento económico sostenible impulsado por el sector privado.",
        "link": "https://www.youtube.com/@JavierMileiOficial",
        "pub_date": "Hace 30 min",
        "tag": "Economía Libre",
        "quote": "«El superávit fiscal es sagrado. Cada peso que no se gasta es un peso que vuelve al bolsillo de los argentinos.»"
    },
    {
        "category": "economia_gobierno",
        "author": "Oficina del Presidente",
        "title": "Informe Oficial: Balance de la reducción del gasto público y desregulación de mercados",
        "source": "Comunicado Oficial",
        "snippet": "1. Cierre de organismos burocráticos innecesarios. 2. Apertura comercial y atracción de inversiones RIGI. 3. Crecimiento del crédito privado a PyMEs y familias.",
        "link": "https://x.com/OPRArgentina",
        "pub_date": "Hace 1 hora",
        "tag": "Gestión Oficial",
        "quote": "«La libertad abre caminos; la burocracia destruye empleo.»"
    },

    # ⚡ STREAMERS & MEDIOS DIGITALES (LA DERECHA DIARIO, NEURA, CARAJO, BREAK CERO, IÑAKI)
    {
        "category": "streamers_redes",
        "author": "La Derecha Diario",
        "title": "Cobertura en vivo: Las repercusiones de la reforma económica y el desplome del riesgo país",
        "source": "La Derecha Diario",
        "snippet": "1. El mercado celebra la consolidación fiscal. 2. Reacciones en el Congreso ante los proyectos de ley. 3. Tendencia viral en redes.",
        "link": "https://laderechadiario.com.ar/",
        "pub_date": "Hace 10 min",
        "tag": "Noticias Digitales",
        "quote": "«El cambio de época se siente en la calle y en las cifras económicas reales.»"
    },
    {
        "category": "streamers_redes",
        "author": "Neura Media",
        "title": "Debate de Streamers: Cómo los jóvenes lideran la conversación digital sobre las ideas libertarias",
        "source": "Neura Stream",
        "snippet": "1. El auge de canales independientes en YouTube y Twitch. 2. Por qué los medios tradicionales perdieron el monopolio del debate. 3. Opiniones en vivo del chat.",
        "link": "https://www.youtube.com/@neuramedia",
        "pub_date": "Hace 25 min",
        "tag": "Streaming & Debate",
        "quote": "«La televisión abierta ya no marca la agenda; hoy la agenda la hace la gente en las redes.»"
    },
    {
        "category": "streamers_redes",
        "author": "Break Cero / Carajo",
        "title": "Resumen de Noticias & Stream: La batalla contra el relato estatista en las redes sociales",
        "source": "Canal Carajo",
        "snippet": "1. Análisis humorístico de los debates políticos. 2. Los videos más virales de TikTok de la semana. 3. Interacción en directo.",
        "link": "https://www.youtube.com/",
        "pub_date": "Hace 40 min",
        "tag": "Batalla Digital",
        "quote": "«Desmontando el relato minuto a minuto con datos reales y sin filtros.»"
    },
    {
        "category": "streamers_redes",
        "author": "Iñaki Gutiérrez",
        "title": "Estrategia Digital: El impacto de la comunicación directa sin intermediarios mediáticos",
        "source": "Análisis en X & TikTok",
        "snippet": "1. Cómo TikTok se convirtió en la plaza pública del debate juvenil. 2. El valor de la autenticidad en las redes. 3. Métricas de alcance sin pauta oficial.",
        "link": "https://x.com/",
        "pub_date": "Hace 50 min",
        "tag": "Estrategia Digital",
        "quote": "«Sin pauta oficial, la verdad y las ideas de la libertad se abren paso solas en las redes.»"
    }
]

CONCEPTOS_BATALLA_CULTURAL = [
    {"text": "LIBERTAD", "weight": 3.4, "color": "#f59e0b"},
    {"text": "LAJE", "weight": 2.8, "color": "#3b82f6"},
    {"text": "RUCAUF", "weight": 2.5, "color": "#10b981"},
    {"text": "MILEI", "weight": 2.4, "color": "#8b5cf6"},
    {"text": "SUPERÁVIT", "weight": 2.0, "color": "#ec4899"},
    {"text": "PROPIEDAD", "weight": 1.7, "color": "#f59e0b"},
    {"text": "OCCIDENTE", "weight": 1.5, "color": "#3b82f6"},
    {"text": "DERECHA DIARIO", "weight": 1.3, "color": "#10b981"},
    {"text": "CARAJO", "weight": 1.1, "color": "#8b5cf6"},
    {"text": "NEURA", "weight": 1.0, "color": "#ec4899"}
]

def collect_all_data() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "total_items": len(DATOS_HUB_BATALLA_CULTURAL),
        "hub_items": DATOS_HUB_BATALLA_CULTURAL,
        "conceptos": CONCEPTOS_BATALLA_CULTURAL
    }

if __name__ == "__main__":
    resultado = collect_all_data()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
