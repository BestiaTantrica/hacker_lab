import os
import subprocess
import time

# Listas de componentes astrológicos
PLANETAS = [
    "Sol", "Luna", "Mercurio", "Venus", "Marte", "Jupiter",
    "Saturno", "Urano", "Neptuno", "Pluton", "Quiron", "Lilith"
]

SIGNOS = [
    "Aries", "Tauro", "Geminis", "Cancer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
]

def procesar_lote():
    total_videos = len(PLANETAS) * len(SIGNOS)
    actual = 0
    exitos = 0
    errores = []

    print("==================================================")
    print(f"🚀 INICIANDO ORQUESTADOR MASIVO: {total_videos} VIDEOS")
    print("==================================================\n")

    for planeta in PLANETAS:
        for signo in SIGNOS:
            actual += 1
            output_expected = f"assets_generados/{planeta.lower()}_{signo.lower()}.mp4"
            
            # Si el video ya existe, lo saltamos para poder pausar/reanudar el script sin perder progreso
            if os.path.exists(output_expected):
                print(f"[{actual}/{total_videos}] ⏭️ Saltando {planeta} en {signo} (Ya existe).")
                exitos += 1
                continue

            print(f"\n[{actual}/{total_videos}] 🎬 Generando: {planeta} en {signo}...")
            
            # Usar subprocess para aislar cada ejecución y limpiar memoria/temporales
            comando = f"./venv/bin/python fabrica_magica.py {planeta} {signo}"
            
            try:
                # Ejecutamos el script. Si falla, el check=True lanza excepción.
                subprocess.run(comando, shell=True, check=True)
                
                # Verificamos que efectivamente se haya creado el archivo
                if os.path.exists(output_expected):
                    exitos += 1
                    print(f"✅ Éxito: {planeta} en {signo}")
                else:
                    raise Exception("El comando terminó pero no se generó el MP4.")
            except KeyboardInterrupt:
                print("\n[!] CANCELADO POR EL USUARIO (Ctrl+C). Apagando Fábrica Mágica...")
                sys.exit(130)
            except subprocess.CalledProcessError as e:
                if e.returncode == 130:
                    print("\n[!] CANCELADO POR EL USUARIO (Ctrl+C en subproceso). Apagando Fábrica Mágica...")
                    sys.exit(130)
                print(f"❌ Error al generar {planeta} en {signo}: {e}")
                errores.append(f"{planeta} en {signo}")
            except Exception as e:
                print(f"❌ Error al generar {planeta} en {signo}: {e}")
                errores.append(f"{planeta} en {signo}")
            
            # Pequeña pausa para no saturar APIs (como Groq/Gemini o yt-dlp)
            time.sleep(2)

    print("\n==================================================")
    print(f"🏁 ORQUESTADOR FINALIZADO")
    print(f"✅ Exitosos: {exitos}/{total_videos}")
    print(f"❌ Errores: {len(errores)}")
    if errores:
        print("Videos que fallaron:")
        for err in errores:
            print(f"  - {err}")
    print("==================================================")

if __name__ == "__main__":
    # Aseguramos estar en el directorio correcto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    procesar_lote()
