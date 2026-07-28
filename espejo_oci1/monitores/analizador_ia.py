#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizador_ia.py — Eslabón Final de la Cascada de Pesca
=========================================================
Corre DESPUÉS del explotador_automatico.py en el pipeline por zona.
Su lógica es en cascada estricta:

1. Carga el delta de subdominios nuevos del día y zona.
2. Aplica un scoring determinístico (sin IA) para pre-priorizar candidatos.
3. Consulta a la IA con el TOP de candidatos priorizados (no al azar).
4. Integra los hallazgos verificados del explotador en el análisis final.
5. Envía UN SOLO mensaje a Telegram con el link al C2 Panel para actuar.

No duplica alertas. No informa si no hay nada accionable.
"""

import os
import sys
import json
import glob
import argparse
import datetime
from llm_client import completar
from notificador import send_telegram

# Configuración de rutas
BASE_DIR = os.path.expanduser("~/plataforma_operativa")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")
C2_PANEL_URL = os.environ.get("C2_PANEL_URL", "http://localhost:8000")

# ─────────────────────────────────────────────────────────────────────────────
# SCORING DETERMINÍSTICO — Priorizar antes de quemar tokens de IA
# ─────────────────────────────────────────────────────────────────────────────
SCORING_RULES = [
    # (keywords que deben estar TODAS presentes, puntos)
    (["admin", "dev"],      5),
    (["admin", "staging"],  5),
    (["secret", "api"],     5),
    (["vault"],             4),
    (["jenkins"],           4),
    (["admin"],             3),
    (["staging"],           3),
    (["dev"],               2),
    (["api"],               2),
    (["internal"],          2),
    (["auth"],              2),
    (["login"],             2),
    (["dashboard"],         2),
    (["portal"],            2),
    (["sandbox"],           2),
    (["qa"],                1),
    (["test"],              1),
    (["git"],               1),
    (["status"],            1),
    (["private"],           1),
]

def calcular_score(subdominio: str) -> int:
    """Calcula un score de riesgo para un subdominio según sus keywords."""
    sub_lower = subdominio.lower()
    score = 0
    for keywords, puntos in SCORING_RULES:
        if all(kw in sub_lower for kw in keywords):
            score += puntos
    return score


def obtener_ultimo_delta(zona: str = "all"):
    """Busca el archivo delta más reciente para la zona indicada."""
    if zona != "all":
        patron = os.path.join(RESULT_DIR, f"delta_{zona}_*.json")
    else:
        patron = os.path.join(RESULT_DIR, "delta_*.json")

    archivos = glob.glob(patron)
    if not archivos:
        return None
    return max(archivos, key=os.path.getmtime)


def cargar_delta(ruta: str) -> dict:
    """Carga los dominios del archivo JSON delta."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("nuevos_activos", data.get("dominios", data))
    except Exception as e:
        print(f"Error cargando delta: {e}")
        return {}


def cargar_hallazgos_explotador() -> list:
    """
    Carga el reporte de hallazgos del explotador_automatico.py de hoy.
    Estos son bugs YA VERIFICADOS con PoC real ($50-$3000 USD).
    """
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    ruta = os.path.join(RESULT_DIR, f"explotador_{fecha_hoy}.json")
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def analizar_con_ia(candidatos_priorizados: list) -> str | None:
    """
    Envía el TOP de candidatos ya scored a la IA para análisis final.
    La IA recibe candidatos PRE-FILTRADOS y priorizados, no basura aleatoria.
    """
    if not candidatos_priorizados:
        return None

    lista_formateada = "\n".join(
        [f"{i+1}. {item['sub']} (score={item['score']})"
         for i, item in enumerate(candidatos_priorizados)]
    )

    prompt = f"""Eres un cazador de Bug Bounty senior especializado en infraestructura cloud y APIs.
Estos subdominios ya fueron pre-filtrados por un scoring algorítmico de riesgo.
Tu tarea es analizar los TOP 5 más prometedores y explicar en 1 línea el vector de ataque específico.

Considera vectores como: Subdomain Takeover, credenciales expuestas, endpoints de admin sin auth,
entornos de staging con datos reales, y misconfiguraciones de CORS o JWT.

Subdominios candidatos (ordenados por score de riesgo):
{lista_formateada}

Devuelve SOLO la lista numerada 1-5 en Markdown con el subdominio en **negrita** y el vector de riesgo."""

    try:
        respuesta = completar(prompt, max_tokens=512)
        return respuesta.strip()
    except Exception as e:
        print(f"Error llamando al LLM: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Analizador IA — Eslabón final de la cascada")
    parser.add_argument("--zone", default="all", help="Zona del pipeline (americas/emea/asia/all)")
    args = parser.parse_args()

    print(f"🤖 Iniciando analizador_ia.py para zona: {args.zone}")

    # ── Cargar delta del día ───────────────────────────────────────────────────
    ultimo_delta = obtener_ultimo_delta(args.zone)
    if not ultimo_delta:
        print("ℹ️ No se encontró delta para analizar. Cascada finalizada sin acción.")
        sys.exit(0)

    print(f"📄 Delta: {ultimo_delta}")
    delta_data = cargar_delta(ultimo_delta)
    if not delta_data:
        print("❌ El archivo delta está vacío o corrupto.")
        sys.exit(1)

    # ── Consolidar subdominios ─────────────────────────────────────────────────
    todos_subdominios = []
    for target, subs in delta_data.items():
        if isinstance(subs, list):
            todos_subdominios.extend(subs)

    if not todos_subdominios:
        print("ℹ️ Sin subdominios nuevos en el delta. Cascada finalizada sin acción.")
        sys.exit(0)

    # ── Cargar hallazgos verificados del explotador (PoCs reales) ─────────────
    hallazgos_verificados = cargar_hallazgos_explotador()
    print(f"🐛 Hallazgos verificados por explotador hoy: {len(hallazgos_verificados)}")

    # ── Scoring y priorización determinística ─────────────────────────────────
    candidatos_con_score = [
        {"sub": sub, "score": calcular_score(sub)}
        for sub in todos_subdominios
        if calcular_score(sub) > 0  # solo los que tienen score > 0
    ]
    candidatos_con_score.sort(key=lambda x: x["score"], reverse=True)
    top_candidatos = candidatos_con_score[:30]  # Top 30 al LLM, mucho más enfocado que 100 aleatorios

    print(f"🔍 Candidatos con score>0: {len(candidatos_con_score)} de {len(todos_subdominios)} totales.")

    # ── Análisis IA sobre TOP candidatos pre-priorizados ──────────────────────
    analisis_ia = None
    if top_candidatos:
        analisis_ia = analizar_con_ia(top_candidatos[:15])  # Máximo 15 para control de tokens

    # ── Construir mensaje unificado para Telegram ──────────────────────────────
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")

    # Sección de hallazgos verificados (PoCs reales — esto es lo prioritario)
    seccion_hallazgos = ""
    if hallazgos_verificados:
        tipos_str = ", ".join(set(h.get("tipo", "?") for h in hallazgos_verificados))
        seccion_hallazgos = (
            f"\n🚨 *{len(hallazgos_verificados)} PoC(s) verificado(s):* {tipos_str}\n"
            f"👉 Abre el C2 Panel para generar el reporte en 1 clic.\n"
        )
    else:
        seccion_hallazgos = "\n✅ Sin hallazgos explotables confirmados en este ciclo.\n"

    # Sección de análisis IA (contexto para investigación manual)
    seccion_ia = ""
    if analisis_ia:
        seccion_ia = f"\n*🤖 Top candidatos para revisión manual:*\n{analisis_ia}\n"
    elif top_candidatos:
        # Fallback: top 5 por score sin IA
        lista_fallback = "\n".join(
            [f"- `{c['sub']}` (score={c['score']})" for c in top_candidatos[:5]]
        )
        seccion_ia = f"\n*📋 Top por scoring (IA no disponible):*\n{lista_fallback}\n"

    mensaje_telegram = (
        f"⚡ *RED DE PESCA — INFORME ZONA {args.zone.upper()} ({fecha_hoy})*\n"
        f"📊 {len(todos_subdominios)} subdominios nuevos procesados\n"
        f"{seccion_hallazgos}"
        f"{seccion_ia}"
        f"🚀 [👉 ABRIR C2 PANEL]({C2_PANEL_URL})"
    )


    # ── Guardar análisis local ─────────────────────────────────────────────────
    ruta_analisis = os.path.join(RESULT_DIR, f"analisis_{args.zone}_{fecha_hoy}.json")
    try:
        with open(ruta_analisis, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": fecha_hoy,
                "zona": args.zone,
                "total_subdominios": len(todos_subdominios),
                "hallazgos_verificados": len(hallazgos_verificados),
                "top_candidatos_score": top_candidatos[:10],
                "analisis_ia": analisis_ia,
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Análisis guardado en {ruta_analisis}")
    except Exception as e:
        print(f"No se pudo guardar análisis local: {e}")

    # ── Enviar a Telegram ──────────────────────────────────────────────────────
    exito = send_telegram(mensaje_telegram)
    if exito:
        print("🚀 Informe unificado enviado a Telegram.")
    else:
        print("❌ Error al enviar a Telegram.")


if __name__ == "__main__":
    main()
