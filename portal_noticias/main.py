#!/usr/bin/env python3
"""
portal_noticias/main.py — Servidor Web Público (Ground News Hispano + Termómetro Social)
Independiente del C2 Panel, orientado al público, retenimiento y visualización de tendencias.
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
from portal_noticias.trend_engine import extract_word_cloud, calculate_social_climate, get_active_poll

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="Radar Prensa & Termómetro Social",
    description="Portal Público de Monitoreo de Sesgo Mediático y Tendencias Sociales",
    version="1.0.0"
)

# Estáticos y Plantillas
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Estado en memoria / Caché ligero para no saturar RSS en cada request
CACHE_DATA = None

def get_or_update_data():
    global CACHE_DATA
    if CACHE_DATA is None:
        raw_data = collect_all_data()
        prensa = raw_data.get("prensa", [])
        trends = raw_data.get("google_trends", [])
        reddit = raw_data.get("reddit", [])

        word_cloud = extract_word_cloud(prensa, trends)
        climate = calculate_social_climate(prensa)
        poll = get_active_poll()

        CACHE_DATA = {
            "timestamp": raw_data.get("timestamp"),
            "prensa": prensa,
            "google_trends": trends,
            "reddit": reddit,
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
            "title": "Radar de Medios & Termómetro Social | Argentina"
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

    # Calcular porcentajes
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("portal_noticias.main:app", host="0.0.0.0", port=8001, reload=True)
