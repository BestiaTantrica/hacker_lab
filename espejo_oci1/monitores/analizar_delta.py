#!/usr/bin/env python3
import os
import sys
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

log_file = os.path.expanduser("~/plataforma_operativa/logs/analisis.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
)

def analizar_subdominio(subdominio, dominio, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"Eres un investigador de Bug Bounty. Se encontró un nuevo subdominio: {subdominio}. Empresa: {dominio}. Responde en 3 puntos breves: 1) ¿Qué tipo de activo es probablemente? 2) ¿Qué verificar primero? 3) ¿Qué herramienta usar para investigarlo?"
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Error al analizar {subdominio}: {e}")
        return f"Error en el análisis de la IA: {e}"

def main():
    if len(sys.argv) < 2:
        logging.error("Falta el argumento del archivo delta JSON.")
        sys.exit(1)
        
    delta_path = sys.argv[1]
    if not os.path.exists(delta_path):
        logging.error(f"Archivo no encontrado: {delta_path}")
        sys.exit(1)
        
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logging.error("Variable de entorno GROQ_API_KEY no definida.")
        sys.exit(1)
        
    try:
        with open(delta_path, "r") as f:
            delta_data = json.load(f)
    except Exception as e:
        logging.error(f"Error al leer JSON: {e}")
        sys.exit(1)
        
    nuevos = delta_data.get("nuevos_activos", {})
    subdominios_totales = []
    for dom, subs in nuevos.items():
        for s in subs:
            subdominios_totales.append((s, dom))
            
    if not subdominios_totales:
        logging.info("No se encontraron subdominios nuevos para analizar.")
        sys.exit(0)
        
    subdominios_a_analizar = subdominios_totales[:10]
    logging.info(f"Iniciando análisis de {len(subdominios_a_analizar)} subdominios.")
    
    reporte_lineas = [f"=== INFORME DE ANÁLISIS DE DELTA ({datetime.now().isoformat()}) ===", ""]
    
    for sub, dom in subdominios_a_analizar:
        logging.info(f"Analizando: {sub}")
        resultado = analizar_subdominio(sub, dom, api_key)
        reporte_lineas.extend([f"[-] Subdominio: {sub}", f"[-] Dominio Base: {dom}", "Análisis:", resultado, "-"*40, ""])
        
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.expanduser(f"~/plataforma_operativa/resultados/analisis_{fecha_str}.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write("\n".join(reporte_lineas))
        
    logging.info(f"Análisis finalizado. Guardado en: {output_path}")

if __name__ == "__main__":
    main()
