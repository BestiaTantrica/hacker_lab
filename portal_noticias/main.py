#!/usr/bin/env python3
"""
portal_noticias/main.py — Servidor Web Público (Ground News Hispano + Termómetro Social + Shorts con Voz Narrada)
Servidor dedicado para el portal público en el puerto 8001.
"""

import os
import sqlite3
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from portal_noticias.rss_collector import collect_all_data
from portal_noticias.trend_engine import extract_literal_word_cloud, calculate_social_climate, get_active_poll
from portal_noticias.generar_short_diario import generate_short_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal_db.sqlite")

app = FastAPI(
    title="Radar Prensa & Termómetro Social",
    description="Portal Público de Monitoreo de Sesgo Mediático, Tendencias y Fábrica de Shorts",
    version="2.1.0"
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Inicializar tablas de Leads y Votos
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


def get_live_data():
    """Genera los datos en tiempo real directo desde los colectores y la DB sin caché estática congelada."""
    raw_data = collect_all_data()
    prensa = raw_data.get("prensa", [])
    trends = raw_data.get("google_trends", [])
    reddit = raw_data.get("reddit", [])
    youtube = raw_data.get("youtube", [])

    word_cloud = extract_literal_word_cloud(prensa, trends)
    climate = calculate_social_climate(prensa)
    poll = get_active_poll()

    # Cargar votos reales registrados en SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (poll["id"],))
    vote_counts = dict(cur.fetchall())
    conn.close()

    total = sum(vote_counts.values())
    poll["total_votes"] = total
    for opt in poll["options"]:
        opt["votes"] = vote_counts.get(opt["id"], 0)

    return {
        "timestamp": raw_data.get("timestamp"),
        "prensa": prensa,
        "google_trends": trends,
        "reddit": reddit,
        "youtube": youtube,
        "word_cloud": word_cloud,
        "climate": climate,
        "poll": poll
    }


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Página de Inicio Pública."""
    data = get_live_data()
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
    return get_live_data()


class PublicVotePayload(BaseModel):
    poll_id: int
    option_id: int

@app.post("/api/public/vote")
async def submit_vote(payload: PublicVotePayload):
    """Procesa el voto del usuario, lo guarda en SQLite y devuelve los porcentajes acumulados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO poll_votes (poll_id, option_id) VALUES (?, ?)", (payload.poll_id, payload.option_id))
        conn.commit()

        # Recalcular conteo exacto de la DB
        cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (payload.poll_id,))
        vote_counts = dict(cur.fetchall())
        conn.close()

        total = sum(vote_counts.values())
        poll = get_active_poll()

        results = []
        for opt in poll["options"]:
            v_cnt = vote_counts.get(opt["id"], 0)
            pct = round((v_cnt / total) * 100, 1) if total > 0 else 0.0
            results.append({
                "id": opt["id"],
                "text": opt["text"],
                "votes": v_cnt,
                "percentage": pct
            })

        return {
            "status": "success",
            "total_votes": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando voto: {str(e)}")


class LeadPayload(BaseModel):
    email: str

@app.post("/api/public/subscribe_lead")
async def subscribe_lead(payload: LeadPayload):
    """Registra el email de un usuario interesado en el newsletter diario."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email inválido")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (email) VALUES (?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "¡Suscripción exitosa al Newsletter Diario!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar suscripción")


@app.get("/api/public/generate_short")
async def api_generate_short():
    """Genera el Short MP4 con voz hablada en español del día y devuelve la ruta de descarga."""
    data = get_live_data()
    top_word = data["word_cloud"][0]["text"] if data["word_cloud"] else "PRESUPUESTO"
    question = data["poll"]["question"]
    
    short_path = generate_short_video(top_word, question)
    if short_path and os.path.exists(short_path):
        return {
            "status": "success",
            "download_url": "/static/shorts/short_del_dia.mp4?v=" + str(os.path.getmtime(short_path)),
            "message": "Short de video vertical 1080x1920 con voz en off generado exitosamente."
        }
    raise HTTPException(status_code=500, detail="No se pudo generar el video Short con voz")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
