#!/usr/bin/env python3
"""
portal_noticias/main.py — Termómetro Social 360 & Medición de Opinión Pública (Puerto 8001)
Plataforma de medición de tendencias generales, encuestas interactivas por conceptos y generador de shorts anzuelo.
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
    extract_general_word_cloud,
    get_interactive_concept_poll,
    calculate_opinion_thermometer,
    categorize_hub_items,
    extract_top_quotes
)
from portal_noticias.generar_short_diario import generate_short_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal_db.sqlite")

app = FastAPI(
    title="Termómetro Social 360 | Medición de Opinión Pública",
    description="Plataforma de Medición de Ideas, Nube General y Encuestas de Tendencias",
    version="7.0.0"
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
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
    prensa_items = raw_data.get("prensa", [])
    redes_items = raw_data.get("redes", [])
    trends_items = raw_data.get("google_trends", [])

    # Extraer Nube de Palabras General (red general sin nombres)
    concept_cloud = extract_general_word_cloud(prensa_items, redes_items, trends_items)
    
    # Si la nube viene vacía por falta de feeds remotos, usar fallback de conceptos generales
    if not concept_cloud:
        fallback_words = ["LIBERTAD", "SUPERÁVIT", "TARIFAS", "INFLACIÓN", "DÓLAR", "PARITARIAS", "PROPIEDAD", "DESREGULACIÓN"]
        colors = ["#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899"]
        sizes = [3.4, 2.8, 2.4, 2.0, 1.7, 1.4, 1.2, 1.0]
        concept_cloud = [{
            "id": idx + 1,
            "text": w,
            "count": 10 - idx,
            "weight": sizes[idx],
            "color": colors[idx % len(colors)]
        } for idx, w in enumerate(fallback_words)]

    concept_poll = get_interactive_concept_poll(concept_cloud)
    thermometer = calculate_opinion_thermometer(hub_items)
    categorized = categorize_hub_items(hub_items)
    top_quotes = extract_top_quotes(hub_items)

    # Cargar votos de la encuesta por concepto
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (concept_poll["id"],))
    v_counts = dict(cur.fetchall())
    
    # Cargar palabras personalizadas
    cur.execute("SELECT word, COUNT(*) FROM custom_words GROUP BY word ORDER BY COUNT(*) DESC LIMIT 8")
    custom_words_summary = cur.fetchall()

    conn.close()

    tot = sum(v_counts.values())
    concept_poll["total_votes"] = tot
    for opt in concept_poll["options"]:
        opt_v = v_counts.get(opt["id"], 0)
        opt["votes"] = opt_v
        opt["pct"] = round((opt_v / tot) * 100, 1) if tot > 0 else 0.0

    short_file = os.path.join(BASE_DIR, "static", "shorts", "short_del_dia.mp4")
    short_url = f"/static/shorts/short_del_dia.mp4?v={os.path.getmtime(short_file)}" if os.path.exists(short_file) else None

    # Texto de comentario automatizado listo para copiar
    top_words_str = ", ".join([c["text"] for c in concept_cloud[:4]])
    comment_text_copy = (
        f"🔥 TERMÓMETRO SOCIAL AR — ¿Estás de acuerdo con lo que más se habla hoy en redes?\n"
        f"☁️ Tendencias: {top_words_str}...\n"
        f"👇 Sumá tu voto o proponé tu propia palabra en el link:\n"
        f"🌐 http://localhost:8001/"
    )

    return {
        "timestamp": raw_data.get("timestamp"),
        "hub_items": hub_items,
        "concept_cloud": concept_cloud,
        "concept_poll": concept_poll,
        "custom_words": custom_words_summary,
        "thermometer": thermometer,
        "categorized": categorized,
        "top_quotes": top_quotes,
        "short_url": short_url,
        "comment_text_copy": comment_text_copy
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
            "title": "TERMÓMETRO SOCIAL AR | Nube de Ideas & Encuestas en Vivo"
        }
    )


@app.get("/api/public/data")
async def get_public_data():
    """Endpoint JSON de datos completos."""
    return get_live_data()


class PublicVotePayload(BaseModel):
    poll_id: int
    option_id: int

@app.post("/api/public/vote")
async def submit_vote(payload: PublicVotePayload):
    """Procesa el voto de una opción de la encuesta por concepto."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO poll_votes (poll_id, option_id) VALUES (?, ?)", (payload.poll_id, payload.option_id))
        conn.commit()

        cur.execute("SELECT option_id, COUNT(*) FROM poll_votes WHERE poll_id = ? GROUP BY option_id", (payload.poll_id,))
        vote_counts = dict(cur.fetchall())
        conn.close()

        total = sum(vote_counts.values())
        data = get_live_data()
        target_poll = data["concept_poll"]

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


class CustomWordPayload(BaseModel):
    word: str

@app.post("/api/public/submit_custom_word")
async def submit_custom_word(payload: CustomWordPayload):
    """Permite al usuario proponer y registrar su propia palabra/concepto en el termómetro."""
    clean_w = payload.word.strip().upper()
    if not clean_w or len(clean_w) < 2 or len(clean_w) > 30:
        raise HTTPException(status_code=400, detail="Palabra inválida")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO custom_words (word) VALUES (?)", (clean_w,))
        conn.commit()
        
        cur.execute("SELECT word, COUNT(*) FROM custom_words GROUP BY word ORDER BY COUNT(*) DESC LIMIT 8")
        top_custom = cur.fetchall()
        conn.close()
        
        return {
            "status": "success",
            "message": f"¡Palabra '{clean_w}' registrada exitosamente!",
            "top_custom_words": top_custom
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error guardando palabra personalizada")


class LeadPayload(BaseModel):
    email: str

@app.post("/api/public/subscribe_lead")
async def subscribe_lead(payload: LeadPayload):
    """Registra el email del usuario para recibir el boletín del termómetro."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email inválido")
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO leads (email) VALUES (?)", (payload.email.strip(),))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "¡Suscripción exitosa!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar suscripción")


@app.get("/api/public/generate_short")
async def api_generate_short():
    """Genera el Short MP4 minimalista (Anzuelo Visual) y el texto de comentario listo para copiar."""
    data = get_live_data()
    concepts = [c["text"] for c in data.get("concept_cloud", [])]
    
    short_path = generate_short_video(
        concepts=concepts,
        base_url="http://localhost:8001/"
    )
    
    if short_path and os.path.exists(short_path):
        return {
            "status": "success",
            "download_url": "/static/shorts/short_del_dia.mp4?v=" + str(os.path.getmtime(short_path)),
            "comment_text_copy": data["comment_text_copy"],
            "message": "Short Anzuelo Visual generado exitosamente."
        }
    raise HTTPException(status_code=500, detail="No se pudo generar el video Short promocional")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
