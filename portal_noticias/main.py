#!/usr/bin/env python3
"""
portal_noticias/main.py — Servidor Web Público (Ground News Hispano + Termómetro Social + Fábrica de Shorts)
Servidor dedicado para el portal público en el puerto 8001.
"""

import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from portal_noticias.rss_collector import collect_all_data
from portal_noticias.trend_engine import extract_literal_word_cloud, calculate_social_climate, get_active_poll
from portal_noticias.generar_short_diario import generate_short_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal_db.sqlite")

app = FastAPI(
    title="Radar Prensa & Termómetro Social",
    description="Portal Público de Monitoreo de Sesgo Mediático, Tendencias y Fábrica de Shorts",
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Inicializar tabla de Leads / Emails
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
    conn.commit()
    conn.close()

init_db()

CACHE_DATA = None

def get_or_update_data():
    global CACHE_DATA
    if CACHE_DATA is None:
        raw_data = collect_all_data()
        prensa = raw_data.get("prensa", [])
        trends = raw_data.get("google_trends", [])
        reddit = raw_data.get("reddit", [])
        youtube = raw_data.get("youtube", [])

        word_cloud = extract_literal_word_cloud(prensa, trends)
        climate = calculate_social_climate(prensa)
        poll = get_active_poll()

        CACHE_DATA = {
            "timestamp": raw_data.get("timestamp"),
            "prensa": prensa,
            "google_trends": trends,
            "reddit": reddit,
            "youtube": youtube,
            "word_cloud": word_cloud,
            "climate": climate,
            "poll": poll
        }
    return CACHE_DATA


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Página de Inicio Pública."""
    data = get_or_update_data()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "data": data,
            "title": "Radar Prensa & Termómetro Social | Argentina"
        }
    )


@app.get("/api/public/data")
async def get_public_data():
    """Endpoint JSON de datos crudos de tendencias y clima social."""
    return get_or_update_data()


class PublicVotePayload(BaseModel):
    poll_id: int
    option_id: int

@app.post("/api/public/vote")
async def submit_vote(payload: PublicVotePayload):
    """Procesa el voto del usuario y devuelve porcentajes en tiempo real."""
    data = get_or_update_data()
    poll = data["poll"]
    
    if poll["id"] != payload.poll_id:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")

    updated = False
    for opt in poll["options"]:
        if opt["id"] == payload.option_id:
            opt["votes"] += 1
            poll["total_votes"] += 1
            updated = True
            break
            
    if not updated:
        raise HTTPException(status_code=400, detail="Opción inválida")

    results = []
    total = max(poll["total_votes"], 1)
    for opt in poll["options"]:
        pct = round((opt["votes"] / total) * 100, 1)
        results.append({
            "id": opt["id"],
            "text": opt["text"],
            "votes": opt["votes"],
            "percentage": pct
        })

    return {
        "status": "success",
        "total_votes": poll["total_votes"],
        "results": results
    }


class LeadPayload(BaseModel):
    email: str

@app.post("/api/public/subscribe_lead")
async def subscribe_lead(payload: LeadPayload):
    """Registra el email de un usuario interesado en informes semanales de tendencias."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email inválido")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (email) VALUES (?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "¡Suscripción exitosa al Informe Sociológico Semanal!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al registrar suscripción")


@app.get("/api/public/generate_short")
async def api_generate_short():
    """Genera el Short MP4 del día y devuelve la ruta de descarga."""
    data = get_or_update_data()
    top_word = data["word_cloud"][0]["text"] if data["word_cloud"] else "TARIFAS"
    question = data["poll"]["question"]
    
    short_path = generate_short_video(top_word, question)
    if short_path and os.path.exists(short_path):
        return {
            "status": "success",
            "download_url": "/static/shorts/short_del_dia.mp4",
            "message": "Short de video vertical 1080x1920 generado exitosamente."
        }
    raise HTTPException(status_code=500, detail="No se pudo generar el video Short")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
