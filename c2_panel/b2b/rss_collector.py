#!/usr/bin/env python3
"""
rss_collector.py — Recolector en Tiempo Real de Tendencias y Noticias (Google Trends AR + Infobae + Ámbito + El Cronista)
Realiza peticiones HTTP en vivo a feeds RSS públicos sin datos simulados.
"""

import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any

LIVE_RSS_FEEDS = [
    {"name": "Google Trends AR", "url": "https://trends.google.com/trending/rss?geo=AR", "type": "trends"},
    {"name": "Infobae", "url": "https://www.infobae.com/arc/outboundfeeds/rss/", "type": "news"},
    {"name": "Ámbito Financiero", "url": "https://www.ambito.com/rss/home.xml", "type": "economy"},
    {"name": "El Cronista", "url": "https://www.cronista.com/files/rss/news.xml", "type": "economy"}
]

def fetch_live_rss_items() -> List[Dict[str, Any]]:
    """Obtiene noticias y búsquedas en tiempo real desde los servidores RSS oficiales."""
    items_collected = []

    for feed in LIVE_RSS_FEEDS:
        try:
            req = urllib.request.Request(
                feed["url"],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                channel_items = root.findall('.//item')

                for item in channel_items[:15]:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_elem = item.find('pubDate')
                    desc_elem = item.find('description')

                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else "#"
                    pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else "Hoy"
                    snippet = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                    # Limpiar etiquetas HTML del snippet si existen
                    snippet_clean = urllib.parse.unquote(snippet)
                    if "<" in snippet_clean:
                        import re
                        snippet_clean = re.sub(r'<[^>]+>', '', snippet_clean)

                    if title:
                        items_collected.append({
                            "source": feed["name"],
                            "type": feed["type"],
                            "title": title,
                            "snippet": snippet_clean[:180],
                            "link": link,
                            "pub_date": pub_date
                        })
        except Exception as e:
            print(f"⚠️ Warning consultando feed {feed['name']}: {e}", file=sys.stderr)

    return items_collected


def collect_all_data() -> Dict[str, Any]:
    """Colecta todos los datos en tiempo real de la red general."""
    live_items = fetch_live_rss_items()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_items": len(live_items),
        "live_feed_items": live_items
    }

if __name__ == "__main__":
    resultado = collect_all_data()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
