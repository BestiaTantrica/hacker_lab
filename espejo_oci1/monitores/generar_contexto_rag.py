#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_contexto_rag.py — Inyección de Contexto Dinámico (RAG)
Genera CEREBRO_CONTEXTO.txt en OCI-1 resumiendo los últimos hallazgos de Subdominios y Nuclei.
Debe ser ejecutado al final de run_pipeline.sh
"""

import os
import json
import glob
import datetime

BASE_DIR = os.path.expanduser("~/plataforma_operativa")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")
CONTEXT_FILE = os.path.join(RESULT_DIR, "CEREBRO_CONTEXTO.txt")

def main():
    print("🧠 Generando contexto RAG para Pegaso...")
    context_lines = []
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context_lines.append(f"Última actualización de contexto: {fecha}")
    
    # 1. Resumen de subdominios descubiertos
    actual_json = os.path.join(RESULT_DIR, "actual.json")
    if os.path.exists(actual_json):
        try:
            with open(actual_json, "r") as f:
                data = json.load(f)
                total_subs = 0
                targets_count = 0
                for target, subs in data.items():
                    if isinstance(subs, list):
                        total_subs += len(subs)
                        targets_count += 1
                context_lines.append(f"- Se monitorean {targets_count} targets con un total de {total_subs} subdominios activos en actual.json.")
        except Exception as e:
            context_lines.append("- Error leyendo actual.json")
    else:
        context_lines.append("- No hay archivo actual.json disponible.")

    # 2. Resumen del último análisis de IA
    analisis_files = glob.glob(os.path.join(RESULT_DIR, "analisis_*.json"))
    if analisis_files:
        ultimo_analisis = max(analisis_files, key=os.path.getmtime)
        try:
            with open(ultimo_analisis, "r") as f:
                data = json.load(f)
                context_lines.append(f"\n- Último Análisis de Subdominios (IA) [{data.get('timestamp', 'N/A')}]:")
                analisis_text = data.get("analisis", "")
                context_lines.append(analisis_text[:800] + ("...\n(truncado)" if len(analisis_text)>800 else ""))
        except:
            pass

    # 3. Resumen de Escaneo Masivo (Nuclei)
    # Soporte tanto para json como txt
    nuclei_json = os.path.join(RESULT_DIR, "nuclei_results.json")
    nuclei_txt = os.path.join(RESULT_DIR, "nuclei_results.txt")
    
    nuclei_file = None
    if os.path.exists(nuclei_json):
        nuclei_file = nuclei_json
    elif os.path.exists(nuclei_txt):
        nuclei_file = nuclei_txt
        
    if nuclei_file:
        try:
            with open(nuclei_file, "r") as f:
                lines = f.readlines()
                high_count = sum(1 for l in lines if '"info-severity":"high"' in l.lower() or '[high]' in l.lower())
                medium_count = sum(1 for l in lines if '"info-severity":"medium"' in l.lower() or '[medium]' in l.lower())
                critical_count = sum(1 for l in lines if '"info-severity":"critical"' in l.lower() or '[critical]' in l.lower())
                
                context_lines.append(f"\n- Alertas de Vulnerabilidades (Nuclei):")
                context_lines.append(f"  Críticas: {critical_count} | Altas: {high_count} | Medias: {medium_count}")
                
                if critical_count + high_count > 0:
                    context_lines.append("  Muestra de hallazgos severos:")
                    hallazgos_mostrados = 0
                    for l in lines:
                        if 'high' in l.lower() or 'critical' in l.lower():
                            if hallazgos_mostrados < 5:
                                context_lines.append(f"    - {l.strip()[:150]}")
                                hallazgos_mostrados += 1
        except Exception as e:
            context_lines.append(f"- Error analizando logs de Nuclei: {e}")
    else:
        context_lines.append("\n- Escaneo Masivo (Nuclei): Aún no hay resultados de Nuclei guardados.")

    with open(CONTEXT_FILE, "w") as f:
        f.write("\n".join(context_lines))
    print(f"✅ Contexto RAG escrito exitosamente en {CONTEXT_FILE}")

if __name__ == "__main__":
    main()
