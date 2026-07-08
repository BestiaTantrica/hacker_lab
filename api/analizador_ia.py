#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizador_ia.py — Módulo de Inteligencia Artificial para el Pipeline.
Analiza la lista de subdominios nuevos (delta), prioriza los de mayor riesgo 
usando Groq/Gemini, y envía el reporte detallado a Telegram.
"""

import os
import sys
import json
import glob
import datetime
from llm_client import completar
from notificador import send_telegram

# Configuración de rutas
BASE_DIR = os.path.expanduser("~/plataforma_operativa")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")

def obtener_ultimo_delta():
    """Busca el archivo delta_*.json más reciente en la carpeta de resultados."""
    patron = os.path.join(RESULT_DIR, "delta_*.json")
    archivos = glob.glob(patron)
    if not archivos:
        return None
    # Devolver el archivo con fecha de modificación más reciente
    return max(archivos, key=os.path.getmtime)

def cargar_delta(ruta):
    """Carga los dominios del archivo JSON delta."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            # El delta puede tener dominios agrupados por target
            # Ej: {"elastic.co": [...], "mongodb.com": [...]}
            return data.get("dominios", data)
    except Exception as e:
        print(f"Error cargando delta: {e}")
        return None

def analizar_con_ia(lista_dominios):
    """Envía la lista a la IA para categorizar y priorizar."""
    prompt = f"""
Eres un analista de seguridad y cazador de Bug Bounty senior. 
Analiza la siguiente lista de subdominios nuevos descubiertos en nuestra infraestructura y selecciona el TOP 5 de mayor interés para auditorías de seguridad.

Prioriza subdominios que apunten a:
- Paneles de administración o login (admin, login, auth, sso, portal, dashboard).
- Entornos de desarrollo/prueba expuestos (dev, test, staging, QA, sandbox, internal).
- Integración continua (jenkins, ci, gitlab, build).
- Gestión de credenciales u objetos sensibles (secrets, vault, key, database, db).

Lista de subdominios a analizar:
{json.dumps(lista_dominios, indent=2)}

Devuelve ÚNICAMENTE un listado en formato Markdown ordenado por prioridad del 1 al 5.
Para cada uno incluye:
- El subdominio en negrita.
- Una breve explicación de 1 sola línea de cuál es el vector de riesgo o por qué llama la atención.
"""
    try:
        # Llamamos al cliente LLM unificado (Groq con fallback a Gemini)
        respuesta = completar(prompt, max_tokens=1024)
        return respuesta.strip()
    except Exception as e:
        print(f"Error llamando al LLM: {e}")
        return None

def main():
    print("🤖 Iniciando analizador_ia.py...")
    ultimo_delta = obtener_ultimo_delta()
    if not ultimo_delta:
        print("ℹ️ No se encontraron archivos delta para analizar.")
        sys.exit(0)

    print(f"📄 Analizando archivo: {ultimo_delta}")
    delta_data = cargar_delta(ultimo_delta)
    if not delta_data:
        print("❌ El archivo delta está vacío o corrupto.")
        sys.exit(1)

    # Consolidar todos los subdominios de todos los targets en una sola lista
    todos_subdominios = []
    for target, subs in delta_data.items():
        if isinstance(subs, list):
            todos_subdominios.extend(subs)

    if not todos_subdominios:
        print("ℹ️ No se detectaron subdominios nuevos en el delta.")
        sys.exit(0)

    print(f"🔍 Procesando {len(todos_subdominios)} subdominios con IA...")
    
    # 1. Intentar el análisis con IA
    analisis = analizar_con_ia(todos_subdominios)
    
    # 2. Formatear mensaje para Telegram
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if analisis:
        mensaje_telegram = f"""*⚡ ALERTA DE MONITOREO ({fecha_hoy})*
Se encontraron {len(todos_subdominios)} subdominios nuevos.

*Top 5 prioridades de ataque según IA:*
{analisis}
"""
        # Guardar copia del análisis localmente
        ruta_analisis = os.path.join(RESULT_DIR, f"analisis_{fecha_hoy}.json")
        try:
            with open(ruta_analisis, "w", encoding="utf-8") as f:
                json.dump({"timestamp": fecha_hoy, "analisis": analisis}, f, indent=2)
            print(f"✅ Análisis guardado en {ruta_analisis}")
        except Exception as e:
            print(f"No se pudo guardar el análisis local: {e}")
    else:
        # Fallback robusto si falla la IA: mandar la lista cruda
        print("⚠️ IA no respondió. Aplicando fallback de lista cruda...")
        lista_cruda = "\n".join([f"- `{s}`" for s in todos_subdominios[:15]])
        if len(todos_subdominios) > 15:
            lista_cruda += f"\n- _...y {len(todos_subdominios) - 15} más_"
            
        mensaje_telegram = f"""*⚠️ ALERTA DE MONITOREO ({fecha_hoy}) (Sin análisis)*
Se detectaron {len(todos_subdominios)} nuevos subdominios pero la IA no estuvo disponible.

*Muestra de activos:*
{lista_cruda}
"""

    # 3. Enviar a Telegram
    exito = send_telegram(mensaje_telegram)
    if exito:
        print("🚀 Notificación enviada con éxito a Telegram.")
    else:
        print("❌ Error al enviar notificación de Telegram.")

if __name__ == "__main__":
    main()
