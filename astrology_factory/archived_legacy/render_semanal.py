import sys
import os
import subprocess
from datetime import datetime
from audio_generator import AudioGenerator

def update_vademecum(event_name, guion_text, prod_dir, base_dir):
    """Actualiza automáticamente el vademecum para que la API tenga contexto de lo generado."""
    vademecum_path = os.path.join(base_dir, "content_factory", "vademecum_contexto.md")
    
    entry = f"\n\n### Registro Automático: {event_name}\n"
    entry += f"- **Fecha de Render:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    entry += f"- **Guion Procesado:** {guion_text.strip()}\n"
    
    with open(vademecum_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print("📔 Vademécum actualizado automáticamente con este evento.")

def update_vademecum_json(event_name, guion_text, prod_dir, base_dir):
    """Actualiza automáticamente el vademecum en formato JSON para la API."""
    import json
    json_path = os.path.join(base_dir, "content_factory", "vademecum.json")
    data = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    
    entry_found = False
    for item in data:
        if item.get("event_name") == event_name:
            item["guion"] = guion_text.strip()
            item["timestamp"] = datetime.now().isoformat()
            entry_found = True
            break
            
    if not entry_found:
        data.append({
            "event_name": event_name,
            "timestamp": datetime.now().isoformat(),
            "guion": guion_text.strip()
        })
        
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("📔 Vademécum JSON actualizado automáticamente.")


def render_week(prefix):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prod_dir = os.path.join(base_dir, "produccion")
    
    if not os.path.exists(prod_dir):
        print(f"Error: No existe el directorio {prod_dir}")
        return

    folders_to_render = []
    for item in os.listdir(prod_dir):
        full_path = os.path.join(prod_dir, item)
        if os.path.isdir(full_path) and item.startswith(prefix):
            folders_to_render.append(item)
    
    if not folders_to_render:
        print(f"No se encontraron eventos para el prefijo '{prefix}'")
        return

    folders_to_render.sort()
    print(f"🚀 Iniciando Batch Render para {len(folders_to_render)} videos de la semana '{prefix}'...")
    
    video_maker_script = os.path.join(base_dir, "content_factory", "video_maker.py")
    audio_gen = AudioGenerator()
    
    success_count = 0
    for i, event in enumerate(folders_to_render, 1):
        print(f"\n" + "="*50)
        print(f"🎬 [{i}/{len(folders_to_render)}] Procesando: {event}")
        print("="*50)
        
        event_dir = os.path.join(prod_dir, event)
        guion_path = os.path.join(event_dir, "guion.txt")
        mp3_path = os.path.join(event_dir, f"{event}.mp3")
        
        # 1. Generar Audio si no existe
        if os.path.exists(guion_path):
            with open(guion_path, "r", encoding="utf-8") as f:
                guion_text = f.read()
                
            if not os.path.exists(mp3_path):
                print("🎙️ Audio faltante, generándolo ahora...")
                audio_gen.generate_audio(guion_text, mp3_path)
        else:
            print(f"❌ No hay guion.txt en {event}. Saltando...")
            continue
            
        # 2. Ejecutar el Orquestador de Edición (Editing Reviewer) que incluye Glitches
        reviewer_script = os.path.join(base_dir, "content_factory", "editing_reviewer.py")
        result = subprocess.run([sys.executable, reviewer_script, event])
        
        # 3. Registrar en Vademecum y copiar a la Bóveda
        if result.returncode == 0:
            print(f"✅ {event} renderizado correctamente.")
            update_vademecum(event, guion_text, prod_dir, base_dir)
            update_vademecum_json(event, guion_text, prod_dir, base_dir)
            
            # Copiar el video final a la Bóveda para centralizar con prefijo FINAL_
            parts = event.split("_")
            week_prefix = "_".join(parts[:2]) if len(parts) >= 2 else event
            boveda_dir = os.path.join("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Videos_Finales", week_prefix)
            os.makedirs(boveda_dir, exist_ok=True)
            final_mp4 = os.path.join(event_dir, f"{event}.mp4")
            if os.path.exists(final_mp4):
                import shutil
                destino = os.path.join(boveda_dir, f"FINAL_{event}.mp4")
                shutil.copy2(final_mp4, destino)
                print(f"      📂 Copiado a la Bóveda como {os.path.basename(destino)}")
                
            success_count += 1
        else:
            print(f"❌ Error al renderizar {event}.")

    print("\n" + "*"*50)
    print(f"🏁 Batch Render Finalizado. Videos exitosos: {success_count}/{len(folders_to_render)}")
    print("*"*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python render_semanal.py <Prefijo_Semana>")
    else:
        render_week(sys.argv[1])
