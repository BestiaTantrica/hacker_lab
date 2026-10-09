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
    while True:
        for cat in CATEGORIES:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Lanzando vault_scraper.py para: {cat}")
            subprocess.run(["python3", "/home/LAB/astrology_factory/content_factory/vault_scraper.py", cat])
            time.sleep(10)  # Breve pausa entre categorías para no saturar

        # Pausa de 1 hora después de revisar TODAS las categorías
        print(f"⏳ Terminó el ciclo completo de 18 categorías. Durmiendo 1 hora antes de volver a empezar...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
