#!/usr/bin/env python3
"""
portal_noticias/reportero_ejecutivo.py — Agente Analista B2B
Este script consulta al LLM para buscar prospectos corporativos y startups en Argentina.
"""

import os
import os
import sys
from datetime import datetime

# Añadir el path para importar llm_client desde el directorio api/
B2B_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(B2B_DIR, "..", "..", "espejo_oci1", "api"))

try:
    from llm_client import completar
except ImportError as e:
    def completar(prompt, max_tokens=512):
        return f"[ERROR IMPORT] No se pudo cargar llm_client: {e}"

def llamar_ia(prompt: str) -> str:
    """Envía el prompt a la IA mediante el cliente unificado (Groq -> Gemini)."""
    try:
        # Usamos el cliente unificado que maneja las API keys y los fallbacks automáticamente
        system_prompt = """Eres un especialista en OSINT corporativo. Tu objetivo es descubrir empresas reales de Argentina (startups, fintech, pymes tecnológicas) que podrían tener infraestructura web activa.
REGLAS ABSOLUTAS:
1. CERO ALUCINACIONES: Las empresas DEBEN existir. Prohibido inventar dominios o startups falsas.
2. Si no encuentras prospectos reales, di 'NO HAY DATOS'.
3. Sé extremadamente directo y conciso. Cero relleno.

"""
        return completar(system_prompt + prompt, max_tokens=1024, temperature=0.0)
    except Exception as e:
        return f"[ERROR API] La llamada falló: {str(e)} (Verificá que las API keys en entorno.env sean válidas)"

def generar_reporte_ejecutivo():
    print("🤖 Agente B2B: Buscando nuevos prospectos corporativos en Argentina...")
    
    instruccion = "Genera una lista de 5 empresas tecnológicas, startups, fintech o aseguradoras de ARGENTINA, que sean empresas reales. REGLA ESTRICTA: EXCLUYE TOTALMENTE bancos tradicionales grandes (Galicia, Santander) y empresas gigantes/unicornios (MercadoPago, Ualá). Enfócate SÓLO en startups medianas o empresas menos conocidas con infraestructura web. Por cada una, provee su dominio web (FORMATO LIMPIO: empresa.com.ar, sin http ni www) y una muy breve descripción."
    
    sintesis_ia = llamar_ia(instruccion)
    
    reporte_generado = f"""
=========================================================
🎯 AUTODESCUBRIMIENTO B2B - PROSPECTOS CORPORATIVOS
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
=========================================================

🧠 RESULTADOS DEL AGENTE OSINT:
{sintesis_ia}

=========================================================
Nota: Copiá el dominio de la empresa que te interese y 
pegálo en la barra 'Inyectar a OCI-1' para iniciar la caza.
"""
    
    reporte_path = os.path.join(os.path.dirname(__file__), "ultimo_reporte_b2b.txt")
    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(reporte_generado)
        
    return reporte_generado

if __name__ == "__main__":
    generar_reporte_ejecutivo()
