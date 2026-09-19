import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from content_factory.audio_generator import AudioGenerator

def main():
    parser = argparse.ArgumentParser(description="Generador de Voz Local")
    parser.add_argument("evento", help="Nombre de la carpeta del evento (ej: 2026-10-05_Venus_Escorpio)")
    args = parser.parse_args()
    
    evento = args.evento
    base_dir = os.path.dirname(os.path.dirname(__file__))
    produccion_dir = os.path.join(base_dir, "produccion", evento)
    
    script_path = os.path.join(produccion_dir, "guion.txt")
    if not os.path.exists(script_path):
        print(f"❌ Error: No se encontró 'guion.txt' en {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read().strip()
        
    if not text:
        print("❌ Error: El archivo 'guion.txt' está vacío.")
        return
        
    output_path = os.path.join(produccion_dir, f"{evento}.mp3")
    
    print(f"🎙️ Generando voz con Edge-TTS para el evento: {evento}...")
    generator = AudioGenerator("es-MX-JorgeNeural")
    generator.generate_audio(text, output_path)
    print(f"✅ ¡Voz generada con éxito! Archivo guardado en: {output_path}")

    # Generar video final con FFmpeg
    print("🎬 Generando video automáticamente...")
    from video_maker import create_video
    create_video(evento)

    # Enviar al celular vía Telegram
    print("📲 Enviando archivos al celular (Telegram)...")
    import shutil
    
    # Intentar copiar a la Bóveda Centralizada
    parts = evento.split('_')
    if len(parts) >= 2:
        semana_folder = f"{parts[0]}_{parts[1]}"
    else:
        semana_folder = "Otros"
        
    vault_base = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Videos_Finales"
    vault_folder = os.path.join(vault_base, semana_folder)
    out_video = os.path.join(produccion_dir, f"{evento}.mp4")
    
    if os.path.exists(out_video):
        try:
            os.makedirs(vault_folder, exist_ok=True)
            vault_dest = os.path.join(vault_folder, f"FINAL_{evento}.mp4")
            shutil.copy2(out_video, vault_dest)
            print(f"📦 Video guardado en la bóveda: {vault_dest}")
        except Exception as e:
            print(f"⚠️ Error al copiar a la bóveda: {e}")
            
    from telegram_bot import send_assets_to_telegram
    import asyncio
    
    # Check if there is already a running event loop, if so use run_coroutine_threadsafe or create a new task.
    # Actually, asyncio.run works fine here because we are in main() and generator.generate_audio uses its own run internally, 
    # but generator.generate_audio has already finished its asyncio.run.
    asyncio.run(send_assets_to_telegram(evento))

if __name__ == "__main__":
    main()
