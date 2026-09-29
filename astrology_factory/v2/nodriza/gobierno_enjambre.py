#!/usr/bin/env python3
"""
🚀 NAVE NODRIZA — Script de Gobierno Global: gobierno_enjambre.py
Orquesta el flujo de trabajo de las IAs según los 3 niveles:
1. Ejecución (Flash)
2. Diseño y Desarrollo (Antigravity/Pro)
3. Arquitectura y Resolución Compleja (Claude)

Uso:
  python v2/nodriza/gobierno_enjambre.py --opcion 1  # Generar/Actualizar BITACORA_ESTADO_GLOBAL.md
  python v2/nodriza/gobierno_enjambre.py --opcion 2  # Preparar Handoff para Claude
  python v2/nodriza/gobierno_enjambre.py --opcion 3  # Asignar/Registrar nueva directiva (WIP)
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BITACORA_PATH = ROOT_DIR / "BITACORA_ESTADO_GLOBAL.md"
REGISTRO_TAREAS_PATH = ROOT_DIR / "v2" / "nodriza" / "tareas_nodriza.json"

def cargar_registro():
    if REGISTRO_TAREAS_PATH.exists():
        with open(REGISTRO_TAREAS_PATH, "r") as f:
            return json.load(f)
    return {
        "nivel_1_flash": [],
        "nivel_2_pro": [],
        "nivel_3_claude": [],
        "metricas": {}
    }

def guardar_registro(data):
    with open(REGISTRO_TAREAS_PATH, "w") as f:
        json.dump(data, f, indent=4)

def opcion_1_estado_global():
    print("🛸 Generando BITACORA_ESTADO_GLOBAL.md...")
    registro = cargar_registro()
    
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    contenido = f"""# 🛸 NAVE NODRIZA: BITÁCORA DE ESTADO GLOBAL
*Última actualización: {fecha}*

Este documento rige la coordinación de IAs en el ecosistema Astrology Factory.
**PROHIBIDO ROMPER EL ESQUEMA DE 3 NIVELES.**

---

## ⚡ NIVEL 1: EJECUCIÓN (IA: Gemini Flash / Scripts)
*Responsabilidad: Trabajos repetitivos, ejecución de comandos aprobados (Navaja Suiza), procesamiento masivo (ej. Clasificador de Videos).*

**Estado / Tareas Activas:**
{_formatear_lista(registro['nivel_1_flash'])}

---

## 🛠️ NIVEL 2: DISEÑO Y DESARROLLO (IA: Antigravity / Pro + Humano)
*Responsabilidad: Creación de nuevas células, ajuste de estéticas (ej. Fusionador Visual), lógicas de negocio inmediatas.*

**Estado / Decisiones Actuales:**
{_formatear_lista(registro['nivel_2_pro'])}

---

## 🧠 NIVEL 3: ARQUITECTURA PROFUNDA (IA: Claude)
*Responsabilidad: Resolución de deudas técnicas masivas, problemas de catalogación/curaduría compleja o re-estructuración de la base de datos.*

**Deudas Técnicas Pendientes (Handoff preparado):**
{_formatear_lista(registro['nivel_3_claude'])}

"""
    with open(BITACORA_PATH, "w") as f:
        f.write(contenido)
    
    print(f"✅ Bitácora generada en {BITACORA_PATH}")

def _formatear_lista(lista):
    if not lista:
        return "- (Vacío / Sin tareas pendientes)"
    return "\n".join([f"- [ ] {item}" for item in lista])

def opcion_2_handoff_claude():
    print("🧠 Preparando Super-Prompt de Handoff para Claude...")
    registro = cargar_registro()
    deudas = registro.get('nivel_3_claude', [])
    if not deudas:
        print("⚠️ No hay deudas técnicas registradas para Claude.")
        return

    print("\n" + "="*60)
    print("Copia este prompt y pásaselo a Claude:\n")
    print("Eres Claude, asumiendo el NIVEL 3 (Arquitectura) en Astrology Factory.")
    print("Contexto: Tenemos un enjambre de scripts en Python (Células 0 a 3).")
    print("Actualmente enfrentamos los siguientes bloqueos estructurales que el Nivel 2 dejó para ti:\n")
    for d in deudas:
        print(f"  - {d}")
    print("\nPor favor, analiza la arquitectura actual (puedes pedir ver mapa_orquestador.md) y propone una solución técnica robusta para esto.")
    print("="*60 + "\n")

def opcion_3_registrar_tarea(nivel, descripcion):
    registro = cargar_registro()
    clave = f"nivel_{nivel}"
    for k in registro.keys():
        if k.startswith(clave):
            registro[k].append(descripcion)
            guardar_registro(registro)
            print(f"✅ Tarea añadida a {k}: {descripcion}")
            # Autoregenerar la bitácora
            opcion_1_estado_global()
            return
    print("❌ Nivel inválido. Debe ser 1, 2 o 3.")

def opcion_4_ejecutar_fase_a():
    import subprocess
    print("🚀 INICIANDO FASE A: El Cerebro (Guion y Tiempos)")
    
    print("\n[1/2] Invocando Célula 1.1: generador_guiones.py --opcion 1")
    res1 = subprocess.run([sys.executable, "v2/celula_1/generador_guiones.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res1.returncode != 0:
        print("❌ Error en Célula 1.1. Abortando FASE A.")
        return

    print("\n[2/2] Invocando Célula 1.2: cronometrador_y_tts.py --opcion 1")
    res2 = subprocess.run([sys.executable, "v2/celula_1/cronometrador_y_tts.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res2.returncode != 0:
        print("❌ Error en Célula 1.2. Abortando FASE A.")
        return
        
    print("\n" + "="*60)
    print("⏸️ PAUSA TÁCTICA (FASE B)")
    print("El guion ha sido generado y los audios están listos.")
    print("Ve a revisar el guion en la carpeta temp/. Cura las imágenes necesarias para cada hueco.")
    print("Cuando hayas terminado, ejecuta: python v2/nodriza/gobierno_enjambre.py --opcion 5")
    print("="*60 + "\n")

def opcion_5_ejecutar_fase_c():
    import subprocess
    print("🚀 INICIANDO FASE C: El Cuerpo (Asignación y Ensamble)")
    
    print("\n[1/6] Invocando Célula 2.1: nodriza_visual.py --opcion 1")
    res1 = subprocess.run([sys.executable, "v2/celula_2/nodriza_visual.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res1.returncode != 0:
        print("❌ Error en Célula 2.1. Abortando FASE C.")
        return
        
    print("\n[2/6] Invocando Célula 2.2: validador_de_ensamble.py --opcion 3")
    res2 = subprocess.run([sys.executable, "v2/celula_2/validador_de_ensamble.py", "--opcion", "3"], cwd=ROOT_DIR)
    if res2.returncode != 0:
        print("❌ Error en Célula 2.2. Abortando FASE C.")
        return

    print("\n[3/7] Invocando Célula 3.0: mezclador_sonoro.py --opcion 1")
    res3_0 = subprocess.run([sys.executable, "v2/celula_3/mezclador_sonoro.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res3_0.returncode != 0:
        print("❌ Error en Célula 3.0 (Mezclador). Abortando FASE C.")
        return

    print("\n[4/7] Invocando Célula 3.1: fabrica_microclips.py --opcion 1")
    res3 = subprocess.run([sys.executable, "v2/celula_3/fabrica_microclips.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res3.returncode != 0:
        print("❌ Error en Célula 3.1. Abortando FASE C.")
        return

    print("\n[5/7] Invocando Célula 3.2: ensamblador_final.py --opcion 1")
    res4 = subprocess.run([sys.executable, "v2/celula_3/ensamblador_final.py", "--opcion", "1"], cwd=ROOT_DIR)
    if res4.returncode != 0:
        print("❌ Error en Célula 3.2 (Ensamble Xfade). Abortando FASE C.")
        return

    print("\n[6/7] Invocando Célula 3.3: ensamblador_final.py --opcion 3")
    res5 = subprocess.run([sys.executable, "v2/celula_3/ensamblador_final.py", "--opcion", "3"], cwd=ROOT_DIR)
    if res5.returncode != 0:
        print("❌ Error en Célula 3.3 (Subtítulos). Abortando FASE C.")
        return

    print("\n[7/7] Invocando Célula 3.4: ensamblador_final.py --opcion 4")
    res6 = subprocess.run([sys.executable, "v2/celula_3/ensamblador_final.py", "--opcion", "4"], cwd=ROOT_DIR)
    if res6.returncode != 0:
        print("❌ Error en Célula 3.4 (Despliegue). Abortando FASE C.")
        return

    print("\n✅ PRODUCCIÓN COMPLETADA EXITOSAMENTE.")

import sys

def main():
    parser = argparse.ArgumentParser(description="Nave Nodriza - Gobierno del Enjambre")
    parser.add_argument("--opcion", type=int, required=True, help="1: Bitácora 2: Handoff Claude 3: Registrar tarea 4: FASE A (Guion) 5: FASE C (Ensamble)")
    parser.add_argument("--nivel", type=int, help="Nivel de IA (1=Flash, 2=Pro, 3=Claude) (solo opcion 3)")
    parser.add_argument("--tarea", type=str, help="Descripción de la tarea (solo opcion 3)")

    args = parser.parse_args()

    if args.opcion == 1:
        opcion_1_estado_global()
    elif args.opcion == 2:
        opcion_2_handoff_claude()
    elif args.opcion == 3:
        if not args.nivel or not args.tarea:
            print("❌ Opcion 3 requiere --nivel y --tarea")
            sys.exit(1)
        opcion_3_registrar_tarea(args.nivel, args.tarea)
    elif args.opcion == 4:
        opcion_4_ejecutar_fase_a()
    elif args.opcion == 5:
        opcion_5_ejecutar_fase_c()
    else:
        print("❌ Opción inválida.")

if __name__ == "__main__":
    main()
