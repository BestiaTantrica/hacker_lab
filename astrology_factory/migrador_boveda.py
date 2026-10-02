import os
import hashlib
import shutil

VAULT_ROOT = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault"
ASSETS_DIR = os.path.join(VAULT_ROOT, "Assets_Reusables")
DESC_CRUDAS = os.path.join(VAULT_ROOT, "Descargas_Crudas")

# Ignorar carpetas de producción final para no romperlas
IGNORE_FOLDERS = ["Descargas_Crudas", "Videos_Finales", "Guiones", "audio_master", "subtitulos", "Assets_Auditados"]

def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def clean_vault():
    seen_hashes = set()
    total_moved = 0
    total_deleted = 0
    
    print("🚀 Iniciando escaneo profundo de la bóveda...")
    
    for root, dirs, files in os.walk(VAULT_ROOT, topdown=False):
        # Ignorar rutas protegidas
        skip = False
        for ig in IGNORE_FOLDERS:
            if os.path.join(VAULT_ROOT, ig) in root:
                skip = True
                break
        if skip:
            continue
            
        for file in files:
            ext = file.lower().split('.')[-1]
            if ext in ['png', 'jpg', 'jpeg', 'webp', 'mp4']:
                filepath = os.path.join(root, file)
                
                try:
                    filehash = get_md5(filepath)
                except Exception as e:
                    print(f"Error leyendo {filepath}: {e}")
                    continue
                
                # Check duplicados
                if filehash in seen_hashes:
                    print(f"🗑️ Eliminando duplicado: {filepath}")
                    os.remove(filepath)
                    total_deleted += 1
                    continue
                
                seen_hashes.add(filehash)
                
                # Determinar destino
                is_video = ext == 'mp4'
                subfolder = "Videos" if is_video else "Imagenes"
                
                # Extraer semana
                semana = "General"
                parts = filepath.split('/')
                for p in parts:
                    if p.startswith("Oct_W"):
                        semana = p
                        break
                
                final_dest_dir = os.path.join(ASSETS_DIR, subfolder, semana)
                os.makedirs(final_dest_dir, exist_ok=True)
                dest_path = os.path.join(final_dest_dir, file)
                
                if filepath != dest_path:
                    # Evitar colisión de nombres
                    counter = 1
                    while os.path.exists(dest_path):
                        name, e = os.path.splitext(file)
                        dest_path = os.path.join(final_dest_dir, f"{name}_{counter}{e}")
                        counter += 1
                        
                    print(f"📦 Moviendo {file} -> {subfolder}/{semana}/")
                    shutil.move(filepath, dest_path)
                    total_moved += 1
        
        # Eliminar carpetas vacías (si no son del sistema)
        try:
            if not os.listdir(root):
                if root != ASSETS_DIR and root != VAULT_ROOT:
                    os.rmdir(root)
                    print(f"🧹 Carpeta vacía eliminada: {os.path.basename(root)}")
        except:
            pass

    print(f"\n✅ Migración completa.")
    print(f"   Archivos movidos/organizados: {total_moved}")
    print(f"   Clones duplicados eliminados: {total_deleted}")

if __name__ == "__main__":
    clean_vault()
