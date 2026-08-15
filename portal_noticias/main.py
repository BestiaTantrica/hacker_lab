#!/usr/bin/env python3
"""
portal_noticias/main.py — Termómetro Social 360 & Medición de Opinión Pública (Puerto 8001)
Servidor dedicado para la plataforma de medición de opinión y contraste con encuestadoras.
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
from portal_noticias.trend_engine import (
    extract_concept_word_cloud,
    calculate_opinion_thermometer,
    categorize_hub_items,
    extract_top_quotes,
    get_active_polls
)
from portal_noticias.generar_short_diario import generate_short_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal_db.sqlite")

app = FastAPI(
    title="Termómetro Social 360 | Medición de Opinión Pública",
    description="Plataforma de Medición de Ideas, Opinión en Redes y Contraste de Encuestas",
    version="6.0.0"
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
    """Genera los datos del Termómetro Social en tiempo real."""
    raw_data = collect_all_data()
    hub_items = raw_data.get("hub_items", [])

    concept_cloud = extract_concept_word_cloud(hub_items)
    thermometer = calculate_opinion_thermometer(hub_items)
    categorized = categorize_hub_items(hub_items)
    top_quotes = extract_top_quotes(hub_items)
    polls = get_active_polls()

    # Cargar votos reales por cada encuesta desde SQLite
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    for p in polls:
        cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (p["id"],))
        v_counts = dict(cur.fetchall())
        tot = sum(v_counts.values())
        p["total_votes"] = tot
        for opt in p["options"]:
            opt_v = v_counts.get(opt["id"], 0)
            opt["votes"] = opt_v
            opt["pct"] = round((opt_v / tot) * 100, 1) if tot > 0 else 0.0

    conn.close()

    short_file = os.path.join(BASE_DIR, "static", "shorts", "short_del_dia.mp4")
    short_url = f"/static/shorts/short_del_dia.mp4?v={os.path.getmtime(short_file)}" if os.path.exists(short_file) else None

    return {
        "timestamp": raw_data.get("timestamp"),
        "hub_items": hub_items,
        "concept_cloud": concept_cloud,
        "thermometer": thermometer,
        "categorized": categorized,
        "top_quotes": top_quotes,
        "polls": polls,
        "short_url": short_url
    }


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Página de Inicio del Termómetro Social 360."""
    data = get_live_data()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "data": data,
            "title": "TERMÓMETRO SOCIAL 360 | Medición de Opinión Pública & Ideas"
        }
    )


@app.get("/api/public/data")
async def get_public_data():
    """Endpoint JSON de datos completos del termómetro."""
    return get_live_data()


class PublicVotePayload(BaseModel):
    poll_id: int
    option_id: int

@app.post("/api/public/vote")
async def submit_vote(payload: PublicVotePayload):
    """Procesa el voto del usuario para cualquier encuesta y devuelve porcentajes acumulados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO poll_votes (poll_id, option_id) VALUES (?, ?)", (payload.poll_id, payload.option_id))
        conn.commit()

        cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (payload.poll_id,))
        vote_counts = dict(cur.fetchall())
        conn.close()

        total = sum(vote_counts.values())
        polls = get_active_polls()
        target_poll = next((p for p in polls if p["id"] == payload.poll_id), polls[0])

        results = []
        for opt in target_poll["options"]:
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
            "poll_id": payload.poll_id,
            "total_votes": total,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando voto: {str(e)}")


class LeadPayload(BaseModel):
    email: str

@app.post("/api/public/subscribe_lead")
async def subscribe_lead(payload: LeadPayload):
    """Registra el email del usuario para el boletín diario del termómetro."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email inválido")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (email) VALUES (?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "¡Suscripción exitosa al Termómetro Social!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar suscripción")


@app.get("/api/public/generate_short")
async def api_generate_short():
    """Genera el Short MP4 promocional con NUBE DE PALABRAS ENTERA, MINI-ENCUESTA y REDIRECCIÓN A LA WEB."""
    data = get_live_data()
    concepts = [c["text"] for c in data.get("concept_cloud", [])]
    target_poll = data["polls"][0] if data.get("polls") else {}
    question = target_poll.get("question", "¿Estás de acuerdo con el rumbo económico?")
    options = [opt["text"] for opt in target_poll.get("options", [])]
    
    short_path = generate_short_video(
        concepts=concepts,
        poll_question=question,
        poll_options=options,
        base_url="http://localhost:8001/"
    )
    
    if short_path and os.path.exists(short_path):
        return {
            "status": "success",
            "download_url": "/static/shorts/short_del_dia.mp4?v=" + str(os.path.getmtime(short_path)),
            "message": "Short de video vertical 1080x1920 con Nube Completa y Mini-Encuesta generado exitosamente."
        }
    raise HTTPException(status_code=500, detail="No se pudo generar el video Short promocional")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
