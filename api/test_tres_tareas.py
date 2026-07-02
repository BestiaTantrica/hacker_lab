#!/usr/bin/env python3
"""
test_tres_tareas.py — Prueba de asignación directa de tareas a los proveedores configurados.
Envía tareas diferentes a Groq y Gemini de forma directa.
"""

import sys
import os
import logging

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Añadir el path actual
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import completar, LLMError, PROVIDERS

# Definir 2 tareas diferentes
TAREAS = {
    "groq": {
        "descripcion": "Análisis rápido de puertos vulnerables",
        "prompt": "Identifica qué servicio corre comúnmente en el puerto 445 y menciona una vulnerabilidad histórica famosa asociada."
    },
    "gemini": {
        "descripcion": "Resumen de alcance de Bug Bounty",
        "prompt": "Resume el siguiente texto del programa de Bug Bounty en una lista de 3 puntos: 'El alcance incluye *.ejemplo.com. Se excluyen expresamente ataques DoS, ingeniería social, y escaneos de puertos agresivos. Las recompensas van desde $50 a $1000 dependiendo de la criticidad.'"
    }
}

def main():
    print("=" * 60)
    print("INICIANDO PRUEBA DE TAREAS CON PROVEEDORES DIRECTOS")
    print("=" * 60)

    for prov_name, info in TAREAS.items():
        provider = PROVIDERS[prov_name]
        print(f"\n🔹 Proveedor: {prov_name.upper()} — Tarea: {info['descripcion']}")
        
        if not provider.is_available():
            print(f"❌ SALTADO: El proveedor '{prov_name}' no tiene API Key configurada en el archivo .env.")
            continue

        try:
            print("⏳ Enviando prompt...")
            respuesta = completar(info['prompt'], max_tokens=150, provider_name=prov_name)
            print(f"✅ RESPUESTA ({prov_name.upper()}):\n{respuesta}")
        except LLMError as e:
            print(f"❌ ERROR al llamar a {prov_name}: {e}")
        except Exception as e:
            print(f"❌ ERROR inesperado en {prov_name}: {e}")
            
    print("\n" + "=" * 60)
    print("PRUEBA FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
