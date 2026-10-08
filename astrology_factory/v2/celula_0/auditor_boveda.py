#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script 0.1: auditor_boveda.py
Audita, limpia y categoriza los assets de la bóveda mediante curaduría manual.
NO toca tiempos, NO toca audio, NO renderiza.

Uso:
  python v2/celula_0/auditor_boveda.py --opcion 1  # Filtro Interactivo Manual [Y/N/R]
  python v2/celula_0/auditor_boveda.py --opcion 2  # Limpieza de basura (symlinks, <50KB)
  python v2/celula_0/auditor_boveda.py --opcion 3  # Reciclador Artístico → glitch_abstracto
  python v2/celula_0/auditor_boveda.py --opcion 4  # Extractor de keyframes
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image

try:
    from google import genai
except ImportError:
    genai = None

# ── Carga del entorno y ADN ──────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from v2 import cuota, db_visual

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

ASSETS_REUSABLES = Path(ADN["assets"]["paths"]["assets_reusables"])
ASSETS_AUDITADOS = Path(ADN["assets"]["paths"]["assets_auditados"])
GLITCH_DIR       = Path(ADN["assets"]["paths"]["glitch_abstracto"])
FORMATOS_VALIDOS = set(ADN["validaciones"]["formatos_validos"])
MIN_BYTES        = ADN["validaciones"]["min_size_bytes"]
EMOCION_DOMINANTE = ADN["arquetipos"]["emocion_dominante"]
COLORES_ADN      = ADN["estetica_visual"]["paleta_colores"]
CATEGORIAS_AUDITORIA = ADN.get("assets", {}).get("categorias_auditoria", {
    "01": "01_Signos_Zodiacales",
    "02": "02_Planetas",
    "03": "03_Elementos_Fuego",
    "04": "04_Elementos_Agua",
    "05": "05_Elementos_Tierra",
    "06": "06_Elementos_Aire",
    "07": "07_Espacio_Galaxias",
    "08": "08_Tarot_Misticismo",
    "09": "09_Geometria_Sagrada",
    "10": "10_Naturaleza_Paisajes",
    "11": "11_Humanos_Emociones",
    "12": "12_Rituales_Magia",
    "13": "13_Abstracto_Fluidos",
    "14": "14_Glitch_VFX",
    "15": "15_Astrologia_Cartas",
    "16": "16_Mitologia_Dioses",
    "17": "17_Objetos_Esotericos",
    "18": "18_General_B_Roll"
})

# ── Helpers ───────────────────────────────────────────────────────────────────

RESET = "\033[0m"
VERDE = "\033[92m"
ROJO  = "\033[91m"
CYAN  = "\033[96m"
AMARILLO = "\033[93m"
MAGENTA  = "\033[95m"

def log(msg, color=RESET):     print(f"{color}{msg}{RESET}")
def ok(msg):                   log(f"  ✅ {msg}", VERDE)
def err(msg):                  log(f"  ❌ {msg}", ROJO)
def info(msg):                  log(f"  ℹ️  {msg}", CYAN)
def warn(msg):                  log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def es_archivo_valido(path: Path) -> tuple[bool, str]:
    """Retorna (es_valido, razon_rechazo)."""
    if path.is_symlink() and not path.exists():
        return False, "symlink roto"
    if path.stat().st_size < MIN_BYTES:
        return False, f"tamaño insuficiente ({path.stat().st_size} bytes < {MIN_BYTES})"
    if path.suffix.lower().lstrip('.') not in FORMATOS_VALIDOS:
        return False, f"formato no válido ({path.suffix})"
    return True, ""

def listar_assets(directorio: Path) -> list[Path]:
    """Lista todos los archivos media en el directorio."""
    archivos = []
    for ext in FORMATOS_VALIDOS:
        archivos.extend(directorio.glob(f"*.{ext}"))
        archivos.extend(directorio.glob(f"*.{ext.upper()}"))
    return sorted(set(archivos))

def correr_ffmpeg(cmd: list, descripcion: str = "") -> bool:
    """Ejecuta un comando FFmpeg. Retorna True si tuvo éxito."""
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
        if result.returncode != 0:
            err(f"FFmpeg falló ({descripcion}): {result.stderr.decode()[-200:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        err(f"FFmpeg timeout ({descripcion})")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Filtro Interactivo Manual [Y/N/R] (Curaduría Principal)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_filtro_interactivo(dir_origen: Path = None, dir_destino: Path = None):
    """
    Abre cada asset, lo muestra (o informa sus datos), y pide [Y]=aprobar [N]=borrar [R]=renombrar.
    Los aprobados se copian a dir_destino.
    """
    dir_origen = dir_origen or ASSETS_REUSABLES
    dir_destino = dir_destino or ASSETS_AUDITADOS

    log(f"\n🎛️  OPCIÓN 1 — Filtro Interactivo Manual (Curaduría en {dir_origen.name})", MAGENTA)

    if not dir_origen.exists():
        err(f"Directorio no existe: {dir_origen}")
        sys.exit(1)

    asegurar_dir(dir_destino)
    archivos = listar_assets(dir_origen)

    if not archivos:
        warn("No se encontraron assets.")
        return

    info(f"Encontrados {len(archivos)} archivos.")
    log("  Comandos rápidos (Auto-categorización):", CYAN)
    for k, v in CATEGORIAS_AUDITORIA.items():
        log(f"    [{k}] {v}", CYAN)
    log("    [N] Borrar | [R] Renombrar | [S] Saltar | [Q] Salir", AMARILLO)

    aprobados = borrados = renombrados = saltados = 0

    for idx, archivo in enumerate(archivos, 1):
        log(f"\n[{idx}/{len(archivos)}] {archivo.name}", CYAN)
        size_kb = archivo.stat().st_size / 1024
        info(f"Tamaño: {size_kb:.1f} KB · Tipo: {archivo.suffix.upper()}")

        valido, razon = es_archivo_valido(archivo)
        if not valido:
            warn(f"⚠️  Archivo sospechoso: {razon}")

        # Intentar abrir con visualizador del sistema de forma automática
        viewer_proc = None
        try:
            if archivo.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                viewer_proc = subprocess.Popen(["gwenview", str(archivo)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif archivo.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                viewer_proc = subprocess.Popen(["ffplay", "-loop", "0", "-v", "quiet", "-x", "800", "-y", "600", str(archivo)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            info("(Visualizador nativo no disponible — decide por nombre y tamaño)")

        while True:
            accion = input("  → Acción [01-18/N/R/S/Q]: ").strip().upper()
            if accion.isdigit() and len(accion) == 1:
                accion = accion.zfill(2)

            if accion in CATEGORIAS_AUDITORIA:
                es_video = archivo.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                tipo_folder = "Videos" if es_video else "Imagenes"
                cat_folder = CATEGORIAS_AUDITORIA[accion]
                
                destino = dir_destino / tipo_folder / cat_folder / archivo.name
                asegurar_dir(destino.parent)
                
                shutil.move(archivo, destino)
                ok(f"Aprobado → {tipo_folder}/{cat_folder}/{archivo.name}")
                aprobados += 1
                break
            elif accion == 'N':
                archivo.unlink()
                warn(f"Borrado: {archivo.name}")
                borrados += 1
                break
            elif accion == 'R':
                nuevo = input("  Nuevo nombre (sin extensión): ").strip()
                cat = input("  Categoría [01-18] o Enter para General: ").strip()
                if cat.isdigit() and len(cat) == 1:
                    cat = cat.zfill(2)
                cat_folder = CATEGORIAS_AUDITORIA.get(cat, CATEGORIAS_AUDITORIA.get("18", "18_General_B_Roll"))
                
                if nuevo:
                    nuevo_path = archivo.parent / f"{nuevo}{archivo.suffix.lower()}"
                    archivo.rename(nuevo_path)
                    
                    es_video = nuevo_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                    tipo_folder = "Videos" if es_video else "Imagenes"
                    
                    destino = dir_destino / tipo_folder / cat_folder / nuevo_path.name
                    asegurar_dir(destino.parent)
                    
                    shutil.move(nuevo_path, destino)
                    ok(f"Renombrado y aprobado → {tipo_folder}/{cat_folder}/{nuevo_path.name}")
                    renombrados += 1
                else:
                    warn("Nombre vacío, saltando.")
                    saltados += 1
                break
            elif accion == 'S':
                info("Saltado.")
                saltados += 1
                break
            elif accion == 'Q':
                log("\n🛑 Sesión interrumpida por el usuario.", AMARILLO)
                break
            else:
                warn("Comando no reconocido.")
        
        # Cerrar el visualizador al pasar al siguiente asset
        if viewer_proc:
            try:
                viewer_proc.terminate()
            except Exception:
                pass
                
        if accion == 'Q':
            break

    log(f"\n{'─'*50}", CYAN)
    log(f"📊 RESUMEN: {aprobados} aprobados · {borrados} borrados · {renombrados} renombrados · {saltados} saltados", VERDE)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Limpieza de Basura
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_limpieza_basura(dir_origen: Path = None):
    """
    Elimina: symlinks rotos, archivos <50KB, formatos no reconocidos.
    Pide confirmación antes de borrar.
    """
    dir_origen = dir_origen or ASSETS_REUSABLES
    log(f"\n🗑️  OPCIÓN 2 — Limpieza de Basura en {dir_origen.name}", MAGENTA)

    if not dir_origen.exists():
        err(f"Directorio no existe: {dir_origen}")
        sys.exit(1)

    candidatos = []

    for archivo in dir_origen.iterdir():
        if not archivo.is_file() and not archivo.is_symlink():
            continue

        # Symlink roto
        if archivo.is_symlink() and not archivo.exists():
            candidatos.append((archivo, "symlink roto"))
            continue

        if not archivo.is_file():
            continue

        size = archivo.stat().st_size
        ext = archivo.suffix.lower().lstrip('.')

        if size < MIN_BYTES:
            candidatos.append((archivo, f"demasiado pequeño ({size/1024:.1f} KB)"))
        elif ext not in FORMATOS_VALIDOS and ext not in ('py', 'json', 'md', 'txt', 'sh', 'env'):
            candidatos.append((archivo, f"formato no válido (.{ext})"))

    if not candidatos:
        ok("La bóveda está limpia. No se encontraron archivos basura.")
        return

    log(f"\n⚠️  Se encontraron {len(candidatos)} archivos candidatos a eliminación:", AMARILLO)
    for archivo, razon in candidatos:
        warn(f"  {archivo.name}  [{razon}]")

    confirmacion = input(f"\n¿Eliminar los {len(candidatos)} archivos? [s/N]: ").strip().lower()
    if confirmacion != 's':
        info("Operación cancelada.")
        return

    eliminados = 0
    for archivo, razon in candidatos:
        try:
            archivo.unlink()
            ok(f"Eliminado: {archivo.name}")
            eliminados += 1
        except Exception as e:
            err(f"No se pudo eliminar {archivo.name}: {e}")

    log(f"\n📊 RESUMEN: {eliminados} archivos eliminados de {len(candidatos)} candidatos.", VERDE)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Reciclador Artístico → /glitch_abstracto
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_reciclador_artistico(dir_origen: Path = None):
    """
    Toma videos rotos o de mala calidad y los convierte en arte de transición:
    satura colores al extremo según la paleta del ADN JSON y los mueve a /glitch_abstracto.
    """
    dir_origen = dir_origen or ASSETS_REUSABLES
    log(f"\n🎨 OPCIÓN 3 — Reciclador Artístico (Arte Abstracto) en {dir_origen.name}", MAGENTA)

    if not dir_origen.exists():
        err(f"Directorio no existe: {dir_origen}")
        sys.exit(1)

    asegurar_dir(GLITCH_DIR)

    # Buscar candidatos: archivos pequeños o potencialmente corruptos
    candidatos_video = []
    for ext in ["mp4", "mov", "avi", "mkv", "webm"]:
        candidatos_video.extend(dir_origen.glob(f"*.{ext}"))
        candidatos_video.extend(dir_origen.glob(f"*.{ext.upper()}"))

    # Verificar cuáles están dañados (ffprobe)
    rotos = []
    for video in sorted(set(candidatos_video)):
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(video)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
        )
        if result.returncode != 0 or video.stat().st_size < MIN_BYTES * 2:
            rotos.append(video)

    if not rotos:
        info("No se encontraron videos rotos/pequeños para reciclar.")
        # Preguntar si quieren reciclar todos de todas formas
        resp = input("¿Reciclar TODOS los videos como arte abstracto? [s/N]: ").strip().lower()
        if resp != 's':
            return
        rotos = sorted(set(candidatos_video))

    log(f"\n♻️  {len(rotos)} videos para convertir en glitch art:", AMARILLO)
    for v in rotos:
        info(f"  {v.name}")

    # Construir filtro de color grading extremo basado en el ADN
    color_cfg = ADN["estetica_visual"]["color_grading_ffmpeg"]
    # Convertir color primario HEX a RGB para el filtro colorchannelmixer
    hex_color = COLORES_ADN["acento"].lstrip("#")
    r_bias = int(hex_color[0:2], 16) / 255 * 0.3
    g_bias = int(hex_color[2:4], 16) / 255 * 0.1
    b_bias = int(hex_color[4:6], 16) / 255 * 0.3

    convertidos = 0
    for video in rotos:
        salida = GLITCH_DIR / f"glitch_{video.stem}.mp4"
        log(f"\n  Procesando: {video.name} → {salida.name}", CYAN)

        vf_filtros = (
            f"eq=contrast={color_cfg['eq_contrast'] * 1.5}:"
            f"saturation={color_cfg['eq_saturation'] * 2.5}:"
            f"brightness={color_cfg['eq_brightness']},"
            f"hue=s=3.0,"
            f"colorchannelmixer="
            f"rr=1.2:rg={r_bias:.3f}:rb=0:"
            f"gr=0:gg=0.8:gb={g_bias:.3f}:"
            f"br={b_bias:.3f}:bg=0:bb=1.3,"
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video),
            "-vf", vf_filtros,
            "-c:v", "libx264",
            "-crf", "28",
            "-preset", "fast",
            "-an",  # Sin audio (son clips de transición)
            "-t", "10",  # Máximo 10s por glitch
            str(salida)
        ]

        if correr_ffmpeg(cmd, f"glitch {video.name}"):
            ok(f"Glitch creado: {salida.name}")
            convertidos += 1
        else:
            err(f"No se pudo convertir: {video.name}")

    log(f"\n📊 RESUMEN: {convertidos}/{len(rotos)} glitches creados en {GLITCH_DIR}", VERDE)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Extractor de Keyframes
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_extractor_keyframes(video_path: str = None, intervalo: float = 1.0, dir_origen: Path = None):
    """
    Convierte un video largo en paquetes de imágenes PNG de alta calidad.
    Si no se pasa video_path, lista los videos disponibles y pide selección.
    """
    dir_origen = dir_origen or ASSETS_REUSABLES
    log(f"\n🖼️  OPCIÓN 4 — Extractor de Keyframes en {dir_origen.name}", MAGENTA)

    if not video_path:
        # Listar videos disponibles
        videos = []
        for ext in ["mp4", "mov", "avi", "mkv", "webm"]:
            videos.extend(dir_origen.glob(f"*.{ext}"))
            videos.extend(dir_origen.glob(f"*.{ext.upper()}"))
        videos = sorted(set(videos))

        if not videos:
            err(f"No hay videos en {dir_origen}")
            sys.exit(1)

        log("\n📂 Videos disponibles:", CYAN)
        for i, v in enumerate(videos, 1):
            size_mb = v.stat().st_size / (1024 * 1024)
            print(f"  [{i}] {v.name}  ({size_mb:.1f} MB)")

        seleccion = input("\nSelecciona número de video (o 0 para cancelar): ").strip()
        if seleccion == '0' or not seleccion.isdigit():
            info("Cancelado.")
            return
        idx = int(seleccion) - 1
        if idx < 0 or idx >= len(videos):
            err("Selección inválida.")
            return
        video_path = str(videos[idx])

    video = Path(video_path)
    if not video.exists():
        err(f"Video no encontrado: {video_path}")
        sys.exit(1)

    # Obtener duración
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(video)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
    )
    try:
        duracion = float(result.stdout.decode().strip())
        frames_estimados = int(duracion / intervalo)
        info(f"Duración: {duracion:.1f}s · ~{frames_estimados} frames a extraer (cada {intervalo}s)")
    except Exception:
        warn("No se pudo determinar la duración. Continuando de todas formas...")

    # Confirmar intervalo
    nuevo_intervalo = input(f"Intervalo entre frames [{intervalo}s] (Enter=confirmar): ").strip()
    if nuevo_intervalo:
        try:
            intervalo = float(nuevo_intervalo)
        except ValueError:
            warn("Valor no válido, usando intervalo por defecto.")

    # Directorio de salida
    vault_base = Path(ADN["assets"]["boveda_base"])
    keyframes_dir = vault_base / "keyframes" / video.stem
    asegurar_dir(keyframes_dir)
    info(f"Exportando frames a: {keyframes_dir}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-vf", f"fps=1/{intervalo},scale=1080:-2",
        "-q:v", "2",  # Alta calidad JPEG
        str(keyframes_dir / "frame_%04d.jpg")
    ]

    ok_result = correr_ffmpeg(cmd, f"keyframes {video.name}")
    if ok_result:
        frames = list(keyframes_dir.glob("frame_*.jpg"))
        ok(f"{len(frames)} frames extraídos en {keyframes_dir}")
    else:
        err("Error al extraer keyframes.")

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 5 — Auditoría IA Masiva
# ═══════════════════════════════════════════════════════════════════════════════

def extraer_fotograma(video_path: Path, output_image_path: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-ss", "00:00:01",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "3",
        str(output_image_path)
    ]
    try:
        subprocess.run(cmd, check=True, timeout=30)
        return True
    except Exception:
        return False

def opcion_5_auditoria_ia_masiva(dir_origen: Path = None, dir_destino: Path = None):
    dir_origen = dir_origen or (VAULT_BASE / "Descargas_Crudas" / ADN["produccion"]["semana_prefijo"])
    dir_destino = dir_destino or ASSETS_AUDITADOS
    
    log(f"\\n🧠  OPCIÓN 5 — Auditoría IA Masiva en {dir_origen.name}", MAGENTA)
    
    if not dir_origen.exists():
        err(f"Directorio no existe: {dir_origen}")
        return
        
    if not genai:
        err("Falta librería google-genai. Ejecuta: pip3 install google-genai pillow")
        return
        
    asegurar_dir(dir_destino)
    db_visual.init_db()
    
    archivos = listar_assets(dir_origen)
    if not archivos:
        ok("No hay archivos para auditar.")
        return
        
    info(f"Se auditarán {len(archivos)} archivos.")
    
    SYSTEM_PROMPT = \"\"\"
Eres un auditor estricto de assets visuales esotéricos y astrológicos.
Analiza esta imagen minuciosamente.
REGLA DE RECHAZO INMEDIATO: Si la imagen contiene familias, niños, personas en entornos cotidianos modernos, oficinas, tecnología o es un collage barato, responde EXACTAMENTE Y SOLO la palabra: RECHAZADO.
SI PASA EL FILTRO (es decir, muestra el espacio, planetas, misticismo, texturas fluidas abstractas, símbolos, naturaleza épica o astrología auténtica):
Responde con una lista de etiquetas descriptivas separadas por comas. (Ejemplo: espacio, estrellas, oscuro, pluton, transformacion, misticismo).
Responde SOLO con RECHAZADO o con la lista de etiquetas. NADA MÁS.
    \"\"\"
    
    for idx, archivo in enumerate(archivos, 1):
        log(f"\\n[{idx}/{len(archivos)}] Analizando {archivo.name}...", CYAN)
        valido, razon = es_archivo_valido(archivo)
        if not valido:
            warn(f"Archivo inválido ({razon}), saltando.")
            continue
            
        es_video = archivo.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']
        
        # Preparar imagen a analizar
        if es_video:
            img_path = dir_origen / f"temp_frame_{archivo.stem}.jpg"
            if not extraer_fotograma(archivo, img_path):
                warn("No se pudo extraer fotograma.")
                continue
        else:
            img_path = archivo
            
        try:
            img = Image.open(img_path)
            img.thumbnail((1024, 1024))
        except Exception as e:
            warn(f"Error abriendo imagen {archivo.name}: {e}")
            if es_video and img_path.exists(): img_path.unlink()
            continue
            
        # Petición con manejo de CUOTA
        etiquetas = None
        rechazado = False
        
        while True:
            llave_elegida = cuota.elegir_key()
            if not llave_elegida:
                err("Todas las cuotas de Gemini están agotadas. Abortando script.")
                sys.exit(1)
                
            nombre_key, api_key = llave_elegida
            cuota.esperar_ritmo()
            
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=[SYSTEM_PROMPT, img]
                )
                
                cuota.registrar_uso(nombre_key)
                resultado = response.text.strip().upper()
                
                if "RECHAZADO" in resultado:
                    rechazado = True
                else:
                    etiquetas = [t.strip().lower() for t in response.text.strip().split(',') if t.strip()]
                    
                break # Salimos del loop de reintentos
            except Exception as e:
                tipo_err = cuota.registrar_error(nombre_key, e)
                warn(f"Error API con {nombre_key} ({tipo_err}). Intentando otra llave...")
                continue
                
        # Limpiar frame temporal
        if es_video and img_path.exists():
            img_path.unlink()
            
        if rechazado:
            warn("La IA RECHAZÓ el asset (no cumple los estándares).")
            db_visual.registrar_asset(archivo, 'video' if es_video else 'imagen', 'rechazado_por_ia')
            # Podemos moverlo a una carpeta de basura o eliminarlo
            archivo.unlink()
            info("Asset eliminado del disco.")
        elif etiquetas:
            ok(f"Aprobado! Etiquetas: {', '.join(etiquetas)}")
            
            # Mover a Assets_Auditados (como lo hacía la manual)
            tipo_folder = "Videos" if es_video else "Imagenes"
            destino = dir_destino / tipo_folder / "18_General_B_Roll" / archivo.name
            asegurar_dir(destino.parent)
            shutil.move(archivo, destino)
            
            db_visual.registrar_asset(destino, 'video' if es_video else 'imagen', 'aprobado', etiquetas)
            
# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 5 — Auditoría IA Masiva
# ═══════════════════════════════════════════════════════════════════════════════

def extraer_fotograma(video_path: Path, output_image_path: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-ss", "00:00:01",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "3",
        str(output_image_path)
    ]
    try:
        subprocess.run(cmd, check=True, timeout=30)
        return True
    except Exception:
        return False

def opcion_5_auditoria_ia_masiva(dir_origen: Path = None, dir_destino: Path = None):
    dir_origen = dir_origen or (VAULT_BASE / "Descargas_Crudas" / ADN["produccion"]["semana_prefijo"])
    dir_destino = dir_destino or ASSETS_AUDITADOS
    
    log(f"\\n🧠  OPCIÓN 5 — Auditoría IA Masiva en {dir_origen.name}", MAGENTA)
    
    if not dir_origen.exists():
        err(f"Directorio no existe: {dir_origen}")
        return
        
    if not genai:
        err("Falta librería google-genai. Ejecuta: pip3 install google-genai pillow")
        return
        
    asegurar_dir(dir_destino)
    db_visual.init_db()
    
    archivos = listar_assets(dir_origen)
    if not archivos:
        ok("No hay archivos para auditar.")
        return
        
    info(f"Se auditarán {len(archivos)} archivos.")
    
    SYSTEM_PROMPT = \"\"\"
Eres un auditor estricto de assets visuales esotéricos y astrológicos.
Analiza esta imagen minuciosamente.
REGLA DE RECHAZO INMEDIATO: Si la imagen contiene familias, niños, personas en entornos cotidianos modernos, oficinas, tecnología o es un collage barato, responde EXACTAMENTE Y SOLO la palabra: RECHAZADO.
SI PASA EL FILTRO (es decir, muestra el espacio, planetas, misticismo, texturas fluidas abstractas, símbolos, naturaleza épica o astrología auténtica):
Responde con una lista de etiquetas descriptivas separadas por comas. (Ejemplo: espacio, estrellas, oscuro, pluton, transformacion, misticismo).
Responde SOLO con RECHAZADO o con la lista de etiquetas. NADA MÁS.
    \"\"\"
    
    for idx, archivo in enumerate(archivos, 1):
        log(f"\\n[{idx}/{len(archivos)}] Analizando {archivo.name}...", CYAN)
        valido, razon = es_archivo_valido(archivo)
        if not valido:
            warn(f"Archivo inválido ({razon}), saltando.")
            continue
            
        es_video = archivo.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']
        
        if es_video:
            img_path = dir_origen / f"temp_frame_{archivo.stem}.jpg"
            if not extraer_fotograma(archivo, img_path):
                warn("No se pudo extraer fotograma.")
                continue
        else:
            img_path = archivo
            
        try:
            img = Image.open(img_path)
            img.thumbnail((1024, 1024))
        except Exception as e:
            warn(f"Error abriendo imagen {archivo.name}: {e}")
            if es_video and img_path.exists(): img_path.unlink()
            continue
            
        etiquetas = None
        rechazado = False
        
        while True:
            llave_elegida = cuota.elegir_key()
            if not llave_elegida:
                err("Todas las cuotas de Gemini están agotadas. Abortando script.")
                sys.exit(1)
                
            nombre_key, api_key = llave_elegida
            cuota.esperar_ritmo()
            
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=[SYSTEM_PROMPT, img]
                )
                
                cuota.registrar_uso(nombre_key)
                resultado = response.text.strip().upper()
                
                if "RECHAZADO" in resultado:
                    rechazado = True
                else:
                    etiquetas = [t.strip().lower() for t in response.text.strip().split(',') if t.strip()]
                    
                break # Salimos del loop de reintentos
            except Exception as e:
                tipo_err = cuota.registrar_error(nombre_key, e)
                warn(f"Error API con {nombre_key} ({tipo_err}). Intentando otra llave...")
                continue
                
        if es_video and img_path.exists():
            img_path.unlink()
            
        if rechazado:
            warn("La IA RECHAZÓ el asset (no cumple los estándares).")
            db_visual.registrar_asset(archivo, 'video' if es_video else 'imagen', 'rechazado_por_ia')
            archivo.unlink()
            info("Asset eliminado del disco.")
        elif etiquetas:
            ok(f"Aprobado! Etiquetas: {', '.join(etiquetas)}")
            
            tipo_folder = "Videos" if es_video else "Imagenes"
            destino = dir_destino / tipo_folder / "18_General_B_Roll" / archivo.name
            asegurar_dir(destino.parent)
            shutil.move(archivo, destino)
            
            db_visual.registrar_asset(destino, 'video' if es_video else 'imagen', 'aprobado', etiquetas)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌑 Auditor de Bóveda V2 — Célula Madre 0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Opciones disponibles:
  1  Filtro Interactivo manual [Y/N/R] (Curaduría Principal)
  2  Limpieza de basura (symlinks rotos, <50KB, formatos inválidos)
  3  Reciclador Artístico → /glitch_abstracto (arte de transición)
  4  Extractor de keyframes de videos largos
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Número de opción a ejecutar (1-4)")
    parser.add_argument("--video", type=str, default=None,
                        help="[Solo opcion 4] Ruta directa al video a extraer frames")
    parser.add_argument("--intervalo", type=float, default=1.0,
                        help="[Solo opcion 4] Intervalo en segundos entre frames (default: 1.0)")
    parser.add_argument("--directorio", type=str, default=None,
                        help="Ruta absoluta a un directorio personalizado para hacer curaduría generalizada")
    parser.add_argument("--salida", type=str, default=None,
                        help="Ruta absoluta a un directorio de destino personalizado")

    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌑 AUDITOR DE BÓVEDA V2", MAGENTA)
    log(f"  ADN activo: {ADN['produccion']['evento_id']}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    dir_custom = Path(args.directorio) if args.directorio else None
    dir_dest_custom = Path(args.salida) if args.salida else None
    
    if dir_custom and not dir_dest_custom:
        dir_dest_custom = dir_custom.parent / f"{dir_custom.name}_Auditados"

    if args.opcion == 1:
        opcion_1_filtro_interactivo(dir_custom, dir_dest_custom)
    elif args.opcion == 2:
        opcion_2_limpieza_basura(dir_custom)
    elif args.opcion == 3:
        opcion_3_reciclador_artistico(dir_custom)
    elif args.opcion == 4:
        opcion_4_extractor_keyframes(args.video, args.intervalo, dir_custom)
    elif args.opcion == 5:
        opcion_5_auditoria_ia_masiva(dir_custom, dir_dest_custom)

if __name__ == "__main__":
    main()
