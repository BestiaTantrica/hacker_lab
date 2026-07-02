#!/usr/bin/env python3
"""
ejemplo_uso.py — Ejemplo de uso del cliente LLM con fallback

Ejecutar:
  export GROQ_API_KEY="tu_clave"
  python3 ejemplo_uso.py

O cargar desde archivo:
  set -a && source .env && set +a && python3 ejemplo_uso.py
"""

import logging
import os
import sys

# Configurar logging para ver qué proveedor se usa
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# Agregar el directorio padre al path si se ejecuta directamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMError, completar

# --- Ejemplo: análisis de subdominio para Bug Bounty ---
PROMPT = """
Eres un asistente de bug bounty. Se encontró un nuevo subdominio: staging-api.ejemplo.com

Responde en 3 puntos breves:
1. ¿Qué tipo de activo es probablemente?
2. ¿Qué verificar primero?
3. ¿Qué herramienta usar?
"""

if __name__ == "__main__":
    try:
        respuesta = completar(PROMPT, max_tokens=300)
        print("\n=== Respuesta del LLM ===")
        print(respuesta)
    except LLMError as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
