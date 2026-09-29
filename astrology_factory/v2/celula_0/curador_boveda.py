#!/usr/bin/env python3
import os
import sys
import shutil
import hashlib
import re
from pathlib import Path

# Paths
DESKTOP_DIR = Path("/home/tomas2/Desktop/Boveda_Astrologia/")
AUDITADOS_DIR = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/")
UNIFIED_DIR = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Boveda_Unificada/")

def get_hash(filepath: Path) -> str:
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except Exception:
        return ""
    return hasher.hexdigest()

def clean_filename(name: str) -> str:
    # 1. Remove hash-like suffixes (e.g., _3d59de, -1a31e4)
    # This regex looks for an underscore or dash followed by 6+ hex characters right before the extension
    cleaned = re.sub(r'[_|-][a-f0-9]{6,12}(?=\.[a-zA-Z0-9]+$)', '', name)
    
    # 2. Convert spaces to underscores
    cleaned = cleaned.replace(' ', '_')
    
    # 3. Clean up double underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    return cleaned

def main():
    print("[*] Iniciando Curaduría de Bóveda (Deduplicación Matemática)")
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)
    
    seen_hashes = set()
    files_processed = 0
    clones_removed = 0
    unique_files = []
    
    dirs_to_scan = [DESKTOP_DIR, AUDITADOS_DIR]
    
    for d in dirs_to_scan:
        if not d.exists():
            print(f"[!] Directorio no encontrado: {d}")
            continue
            
        print(f"[*] Escaneando {d}...")
        for root, _, files in os.walk(d):
            for f in files:
                if not f.lower().endswith(('.mp4', '.jpg', '.jpeg', '.png', '.gif')):
                    continue
                    
                files_processed += 1
                filepath = Path(root) / f
                
                # Deduplication
                file_hash = get_hash(filepath)
                if file_hash in seen_hashes:
                    clones_removed += 1
                    continue
                    
                seen_hashes.add(file_hash)
                
                # New unified path
                new_name = clean_filename(f)
                
                # Ensure no naming collisions after cleaning
                unified_path = UNIFIED_DIR / new_name
                counter = 1
                while unified_path.exists() and get_hash(unified_path) != file_hash:
                    # Append counter if name exists but content is different
                    name_stem = unified_path.stem
                    ext = unified_path.suffix
                    unified_path = UNIFIED_DIR / f"{name_stem}_{counter}{ext}"
                    counter += 1
                
                # Copy instead of move for now (safer for testing), or move if user wants
                if not unified_path.exists():
                    shutil.copy2(filepath, unified_path)
                
                unique_files.append({
                    "original": f,
                    "new": unified_path.name,
                    "path": unified_path,
                    "type": "video" if f.lower().endswith('.mp4') else "image"
                })
                
                if files_processed % 100 == 0:
                    print(f"   ... Procesados {files_processed} archivos")

    print(f"\n[+] Curaduría completada.")
    print(f"    - Archivos totales escaneados: {files_processed}")
    print(f"    - Clones omitidos/eliminados: {clones_removed}")
    print(f"    - Archivos únicos en Boveda_Unificada: {len(unique_files)}")
    
    print("\n[*] Generando Galería HTML de Auditoría...")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Auditoría de Bóveda - Astrology Factory</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }
            h1 { text-align: center; color: #ff9800; border-bottom: 1px solid #333; padding-bottom: 10px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: #1e1e1e; border-radius: 8px; overflow: hidden; padding: 10px; text-align: center; border: 1px solid #333; }
            .media-container { width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; background: #000; overflow: hidden; margin-bottom: 10px;}
            img, video { max-width: 100%; max-height: 100%; object-fit: contain; }
            .filename { font-size: 0.9em; word-break: break-all; margin-bottom: 5px; color: #4caf50; }
            .original-filename { font-size: 0.7em; word-break: break-all; color: #888; text-decoration: line-through; }
        </style>
    </head>
    <body>
        <h1>Bóveda Unificada - Galería de Revisión</h1>
        <p style="text-align:center">Revisa estos assets para crear tus carpetas temáticas. Archivos únicos: """ + str(len(unique_files)) + """</p>
        <div class="grid">
    """
    
    for f in unique_files:
        html_content += f"""
        <div class="card">
            <div class="media-container">
        """
        if f["type"] == "video":
            html_content += f'<video src="file://{f["path"].absolute()}" controls muted loop></video>'
        else:
            html_content += f'<img src="file://{f["path"].absolute()}" loading="lazy">'
            
        html_content += f"""
            </div>
            <div class="filename">{f['new']}</div>
            <div class="original-filename">{f['original']}</div>
        </div>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    html_path = UNIFIED_DIR / "galeria_auditoria.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[+] ¡Galería creada! Ábrela en tu navegador: file://{html_path.absolute()}")

if __name__ == "__main__":
    main()
