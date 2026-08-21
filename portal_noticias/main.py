#!/usr/bin/env python3
"""
portal_noticias/main.py — Dashboard Analítico B2B (Puerto 8001)
Ingesta y análisis de sentimiento a partir de feeds RSS y menciones reales.
"""

import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from portal_noticias.rss_collector import collect_all_data
from portal_noticias.trend_engine import (
    calculate_opinion_thermometer,
    categorize_hub_items
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal_db.sqlite")

app = FastAPI(
    title="Inteligencia Social B2B | Panel Analítico",
    description="Plataforma interna de medición de sentimiento y análisis de tendencias",
    version="9.0.0"
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Limpiamos las tablas inútiles de encuestas y palabras customizadas si existen
    cur.execute("DROP TABLE IF EXISTS poll_votes")
    cur.execute("DROP TABLE IF EXISTS custom_words")
    conn.commit()
    conn.close()

init_db()


def get_live_data():
    """Genera los datos del Dashboard B2B en tiempo real raspando feeds HTTP reales."""
    raw_data = collect_all_data()
    live_items = raw_data.get("live_feed_items", [])

    thermometer = calculate_opinion_thermometer(live_items)
    categorized = categorize_hub_items(live_items)

    return {
        "timestamp": raw_data.get("timestamp"),
        "hub_items": live_items,
        "thermometer": thermometer,
        "categorized": categorized
    }


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Dashboard Ejecutivo Analítico."""
    data = get_live_data()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "data": data,
            "title": "INTELIGENCIA B2B | Panel de Monitoreo"
        }
    )


@app.get("/api/public/data")
async def get_public_data():
    """Endpoint JSON de datos crudos analíticos."""
    return get_live_data()


class LeadPayload(BaseModel):
    email: str

@app.post("/api/public/subscribe_lead")
async def subscribe_lead(payload: LeadPayload):
    """Registra el email de un cliente B2B interesado."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email inválido")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (email) VALUES (?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Suscripción registrada."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar suscripción")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
