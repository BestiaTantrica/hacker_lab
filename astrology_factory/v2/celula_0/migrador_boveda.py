#!/usr/bin/env python3
"""
Script temporal para mover todos los assets sueltos en Assets_Reusables a una subcarpeta Legacy
para implementar la nueva Taxonomía Astrológica sin perder nada.
"""

import os
import shutil
from pathlib import Path

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables")
LEGACY_DIR = VAULT_BASE / "Legacy"

def migrar_a_legacy():
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Excluir las nuevas carpetas elementales y archivos del sistema
    exclusions = {"Fuego", "Agua", "Tierra", "Aire", "Legacy", "registry.json"}
    
    elementos_movidos = 0
    
    for item in VAULT_BASE.iterdir():
        if item.name in exclusions:
            continue
            
        destino = LEGACY_DIR / item.name
        print(f"Moviendo {item.name} -> Legacy/")
        shutil.move(str(item), str(destino))
        elementos_movidos += 1
        
    print(f"✅ Migración completada. Se movieron {elementos_movidos} elementos a Legacy.")

if __name__ == "__main__":
    migrar_a_legacy()
