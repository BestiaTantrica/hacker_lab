#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Daemon: pulmon_recolector.py
El pulmón del sistema. Se ejecuta en segundo plano (o en una terminal) para:
1. Controlar el límite de 50GB en la Bóveda, moviendo assets viejos a Revision_Manual.
2. Descargar assets crudos usando recolector_visual.py.
3. Generar arte sintético usando generador_arte_ia.py.
4. Clasificarlos en la Bóveda usando auditor_boveda.py.
5. Dormir 30 minutos y repetir.
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
import json

FACTORY_ROOT = Path(__file__).resolve().parents[2]

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
try:
    with open(ADN_PATH, encoding="utf-8") as f:
        ADN = json.load(f)
except Exception:
    print("❌ No se encontró contexto_astrologico.json")
    sys.exit(1)

VAULT_BASE = Path(ADN["assets"]["boveda_base"])
AUDITADOS_DIR = VAULT_BASE / "Assets_Auditados"
REVISION_DIR = VAULT_BASE / "Revision_Manual"
REVISION_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE_BYTES = 50 * 1024 * 1024 * 1024 # 50 GB
TARGET_FREE_BYTES = 2 * 1024 * 1024 * 1024 # 2 GB a liberar cuando se llena

def get_directory_size(directory: Path):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def purge_if_needed():
    if not AUDITADOS_DIR.exists():
        return
        
    current_size = get_directory_size(AUDITADOS_DIR)
    print(f"📊 Tamaño actual de Bóveda: {current_size / (1024**3):.2f} GB / 50.00 GB")
    
    if current_size > MAX_SIZE_BYTES:
        print("⚠️ LÍMITE DE 50GB SUPERADO. Moviendo archivos antiguos a /Revision_Manual...")
        # Recolectar todos los archivos con su fecha de modificación
        all_files = []
        for dirpath, _, filenames in os.walk(AUDITADOS_DIR):
            for f in filenames:
                fp = Path(dirpath) / f
                if fp.is_file():
                    all_files.append((fp, fp.stat().st_mtime, fp.stat().st_size))
        
        # Ordenar por fecha (más viejos primero)
        all_files.sort(key=lambda x: x[1])
        
        freed_bytes = 0
        for fp, mtime, size in all_files:
            if freed_bytes >= TARGET_FREE_BYTES:
                break
                
            dest = REVISION_DIR / fp.name
            if dest.exists():
                dest = REVISION_DIR / f"{int(time.time())}_{fp.name}"
            
            try:
                shutil.move(str(fp), str(dest))
                freed_bytes += size
                print(f"  -> Movido: {fp.name} ({(size/1024/1024):.2f} MB)")
            except Exception as e:
                print(f"  ❌ Error moviendo {fp.name}: {e}")
                
        print(f"✅ Purga completada. Se movieron {(freed_bytes / 1024 / 1024):.2f} MB a Revision_Manual.")
    else:
        print("✅ Espacio dentro de los límites saludables.")

def run_script(script_name, args=None):
    if args is None:
        args = []
    script_path = FACTORY_ROOT / "v2" / "celula_0" / script_name
    print(f"\n🚀 Ejecutando: {script_name} {' '.join(args)}")
    try:
        subprocess.run(["python3", str(script_path)] + args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ El script {script_name} terminó con errores (código {e.returncode}).")

def main():
    print("="*50)
    print("🫁 INICIANDO PULMÓN RECOLECTOR (DAEMON)")
    print("="*50)
    
    while True:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando ciclo respiratorio...")
        
        # 1. Control de espacio y cuarentena
        purge_if_needed()
        
        # 2. Recolección de Assets de Internet (Pixabay/Pexels)
        run_script("recolector_visual.py", ["--opcion", "1", "--max", "15"])
        run_script("recolector_visual.py", ["--opcion", "2", "--max", "5"])
        
        # 3. Creación de Arte IA propio
        run_script("generador_arte_ia.py")
        
        # 4. Auditoría y Clasificación (Gemini Vision)
        run_script("auditor_boveda.py", ["--opcion", "1"])
        
        print("\n💤 Ciclo completado. Durmiendo 30 minutos...")
        # Barra de progreso simple
        for i in range(30):
            sys.stdout.write(f"\rEsperando... {30-i} min restantes.")
            sys.stdout.flush()
            time.sleep(60)
        print("\rDespertando...                      ")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Pulmón detenido por el usuario.")
        sys.exit(0)
