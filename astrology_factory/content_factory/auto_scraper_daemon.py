import time
import subprocess
import os
import sys

CATEGORIES = [
    "01_Signos_Zodiacales", "02_Planetas", "03_Elementos_Fuego", "04_Elementos_Agua",
    "05_Elementos_Tierra", "06_Elementos_Aire", "07_Espacio_Galaxias", "08_Tarot_Misticismo",
    "09_Geometria_Sagrada", "10_Naturaleza_Paisajes", "11_Humanos_Emociones", "12_Rituales_Magia",
    "13_Abstracto_Fluidos", "14_Glitch_VFX", "15_Astrologia_Cartas", "16_Mitologia_Dioses",
    "17_Objetos_Esotericos", "18_General_B_Roll"
]

def main():
    print("🛸 Inciando Auto-Scraper Daemon. Bucle infinito activado.")
    idx = 0
    while True:
        cat = CATEGORIES[idx % len(CATEGORIES)]
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Lanzando vault_scraper.py para: {cat}")
        
        # Llama al scraper
        subprocess.run(["python3", "/home/LAB/astrology_factory/content_factory/vault_scraper.py", cat])
        
        # Siguiente categoría
        idx += 1
        
        # Pausa de 1 hora entre categorías para proteger las APIs
        print(f"⏳ Terminó {cat}. Durmiendo 1 hora antes de la próxima categoría...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
