#!/usr/bin/env python3
"""
🌔 CÉLULA MADRE 3 — Script 3.1: fabrica_microclips.py
El motor de renderizado de clips individuales.
Lee lista_de_corte_validada.json y produce un microclip MP4 por toma.
ES EL ÚNICO LUGAR donde se ejecuta FFmpeg para video. JAMÁS improvises un comando.

Uso:
  python v2/celula_3/fabrica_microclips.py --opcion 1   # Render con color grading astrológico
  python v2/celula_3/fabrica_microclips.py --opcion 2   # Render raw/limpio (sin filtros)
  python v2/celula_3/fabrica_microclips.py --opcion 3   # Render mudo (sin audio) para archivo
  python v2/celula_3/fabrica_microclips.py --opcion 1 --toma 3  # Renderizar solo una toma
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID   = ADN["produccion"]["evento_id"]
VAULT_BASE  = Path(ADN["assets"]["boveda_base"])
TEMP_DIR    = VAULT_BASE / "temp"
MICRO_DIR   = Path(ADN["assets"]["paths"]["microclips"]) / EVENTO_ID

# Parámetros de render del ADN
RENDER      = ADN["render"]
RESOLUCION  = RENDER["resolucion"]               # "1080x1920"
W, H        = [int(x) for x in RESOLUCION.split("x")]
FPS         = RENDER["fps"]                      # 30
COLOR_GRADE = RENDER["color_grade"]
PRESET      = RENDER.get("ffmpeg_preset", "fast")
CRF         = RENDER.get("crf", 20)

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def cargar_lista_validada() -> dict:
    ruta = TEMP_DIR / f"lista_de_corte_validada_{EVENTO_ID}.json"
    if not ruta.exists():
        err(f"lista_de_corte_validada no encontrada: {ruta}")
        err("Primero ejecuta: validador_de_ensamble.py --opcion 3")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

def correr_ffmpeg(cmd: list, descripcion: str, timeout: int = 300) -> bool:
    """Ejecuta un comando FFmpeg. Retorna True si exitoso."""
    cmd_str = " ".join(str(c) for c in cmd)
    log(f"\n  🎬 {descripcion}", GRIS)
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
        )
        if result.returncode != 0:
            stderr = result.stderr.decode()
            err(f"FFmpeg falló ({descripcion}): {stderr[-400:]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        err(f"FFmpeg timeout ({timeout}s): {descripcion}")
        return False
    except FileNotFoundError:
        err("FFmpeg no encontrado. Instala con: sudo apt install ffmpeg")
        sys.exit(1)

def nombre_clip(num_toma: int, dur_s: float) -> str:
    return f"clip_{num_toma:02d}_{dur_s:.3f}s.mp4"

# ── Filtros FFmpeg ────────────────────────────────────────────────────────────

def construir_filtro_color_grading() -> str:
    """
    Construye el filtro de color grading a partir de los parámetros del ADN.
    Lee: brillo, contraste, saturacion, tono_cielo (LUT si existe).
    NUNCA improvises valores — todos vienen del ADN.
    """
    cg       = COLOR_GRADE
    brillo   = cg.get("brillo",      0.0)
    contrast = cg.get("contraste",   1.0)
    satura   = cg.get("saturacion",  1.0)
    gamma    = cg.get("gamma",       1.0)
    vignette = cg.get("vignette",    True)
    lut_path = cg.get("lut_path",    "")

    partes = []

    # 1. Loop o trim: ya manejado antes del filtro
    # 2. Escalar y cropear a 9:16 portrait sin distorsión
    partes.append(
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}"
    )
    # 3. Color grading con eq (brightness/contrast/saturation/gamma)
    partes.append(
        f"eq=brightness={brillo:.3f}:contrast={contrast:.3f}"
        f":saturation={satura:.3f}:gamma={gamma:.3f}"
    )
    # 4. LUT opcional
    if lut_path and Path(lut_path).exists():
        partes.append(f"lut3d='{lut_path}'")
        
    # ESTILOS DINÁMICOS ALEATORIOS PARA MICROCLIPS
    import random
    estilo_microclip = random.choice(["vignette_suave", "grano_cine", "vignette_fuerte", "limpio"])
    
    if estilo_microclip == "vignette_suave" and vignette:
        partes.append("vignette=angle=PI/5:mode=backward")
    elif estilo_microclip == "vignette_fuerte":
        partes.append("vignette=angle=PI/3:mode=backward")
    elif estilo_microclip == "grano_cine":
        # Ruido sutil para textura cinematográfica
        partes.append("noise=alls=20:allf=t+u")
        if vignette:
            partes.append("vignette=angle=PI/4:mode=backward")
            
    # 6. FPS constante
    partes.append(f"fps={FPS}")

    return ",".join(partes)

def construir_filtro_raw() -> str:
    """Filtro mínimo: solo crop 9:16 + FPS. Sin color grading."""
    return (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"fps={FPS}"
    )

# ── Render de un solo clip ────────────────────────────────────────────────────

def renderizar_toma(toma: dict, filtro_vf: str, con_audio: bool = False) -> Path | None:
    """
    Renderiza una sola toma a microclip MP4.
    Lee accion_ffmpeg, start_trim_ms, end_trim_ms, num_loops del JSON.
    Retorna la ruta del clip generado, o None si falla.
    """
    num       = toma["num_toma"]
    archivo   = toma.get("archivo_video")
    accion    = toma.get("accion_ffmpeg", "trim")
    dur_s     = toma.get("duracion_s", 0)
    start_ms  = toma.get("start_trim_ms", 0.0)
    end_ms    = toma.get("end_trim_ms", dur_s * 1000)
    num_loops = toma.get("num_loops", 1)

    if not archivo:
        err(f"Toma {num}: sin archivo de video. No se puede renderizar.")
        return None

    src  = Path(archivo)
    if not src.exists():
        err(f"Toma {num}: archivo no existe: {src}")
        return None

    salida = MICRO_DIR / nombre_clip(num, dur_s)
    asegurar_dir(MICRO_DIR)

    start_s = start_ms / 1000.0
    end_s   = end_ms   / 1000.0
    dur_s_exact = end_s - start_s

    if accion == "loop":
        # LOOP: usar el demuxer de loop de FFmpeg
        # -stream_loop N = repetir N veces el input COMPLETO, luego trim
        cmd = [
            "ffmpeg", "-y", "-threads", "2",
            "-stream_loop", str(num_loops),
            "-i", str(src),
            "-t", f"{dur_s_exact:.6f}",
            "-vf", filtro_vf,
            "-c:v", "libx264",
            "-preset", PRESET,
            "-crf", str(CRF),
            "-pix_fmt", "yuv420p",
            "-an",  # Sin audio en los microclips (el audio va por separado)
            str(salida)
        ]
    else:
        # TRIM: cortar del video original al tiempo exacto
        cmd = [
            "ffmpeg", "-y", "-threads", "2",
            "-ss", f"{start_s:.6f}",
            "-i", str(src),
            "-t", f"{dur_s_exact:.6f}",
            "-vf", filtro_vf,
            "-c:v", "libx264",
            "-preset", PRESET,
            "-crf", str(CRF),
            "-pix_fmt", "yuv420p",
            "-an",
            str(salida)
        ]

    exito = correr_ffmpeg(cmd, f"Toma {num:02d} [{accion}] → {salida.name}", timeout=180)

    if exito and salida.exists() and salida.stat().st_size > 1000:
        ok(f"Clip {num:02d}: {salida.name} ({salida.stat().st_size/1024:.1f}KB)")
        return salida
    else:
        err(f"Toma {num}: falló el render. Revisa FFmpeg logs.")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Render con Color Grading Astrológico
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_render_color_grading(solo_toma: int = None):
    """
    Renderiza todos los microclips aplicando el color grading completo del ADN:
    Crop 9:16 + EQ (brillo/contraste/saturación/gamma) + LUT opcional + Viñeta.
    """
    log("\n🎨 OPCIÓN 1 — Render con Color Grading Astrológico", MAGENTA)

    lista    = cargar_lista_validada()
    tomas    = lista.get("tomas", [])
    filtro   = construir_filtro_color_grading()

    if lista.get("bloqueado_anti_spam"):
        err("🚨 La lista está BLOQUEADA por regla anti-spam. Resolvel antes de renderizar.")
        sys.exit(1)

    if solo_toma:
        tomas = [t for t in tomas if t["num_toma"] == solo_toma]
        if not tomas:
            err(f"Toma {solo_toma} no encontrada en la lista.")
            sys.exit(1)
        info(f"Renderizando solo toma {solo_toma}")

    info(f"Color grading: brillo={COLOR_GRADE.get('brillo',0)} · contraste={COLOR_GRADE.get('contraste',1)} · saturación={COLOR_GRADE.get('saturacion',1)}")
    info(f"Resolución: {RESOLUCION} · FPS: {FPS} · CRF: {CRF} · Preset: {PRESET}")
    info(f"Tomas a renderizar: {len(tomas)}")

    clips_ok    = []
    clips_fail  = []
    t_inicio    = time.time()

    for i, toma in enumerate(tomas, 1):
        log(f"\n  [{i}/{len(tomas)}] Toma {toma['num_toma']} [{toma.get('rol','?')}] "
            f"— {toma.get('duracion_s', 0):.3f}s", CYAN)
        clip = renderizar_toma(toma, filtro)
        if clip:
            clips_ok.append(clip)
        else:
            clips_fail.append(toma["num_toma"])

    elapsed = time.time() - t_inicio
    log(f"\n{'═'*55}", VERDE)
    log(f"  📊 RENDER COMPLETO en {elapsed:.1f}s", VERDE)
    log(f"     ✅ Exitosos: {len(clips_ok)}/{len(tomas)}", VERDE)
    log(f"     ❌ Fallidos: {len(clips_fail)}", ROJO if clips_fail else VERDE)
    log(f"     📁 Output:  {MICRO_DIR}", CYAN)
    if clips_fail:
        warn(f"Tomas fallidas: {clips_fail}")
    log(f"\n  ➡️  Siguiente: ensamblador_final.py --opcion 1", AMARILLO)
    return [str(c) for c in clips_ok]

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Render Raw / Limpio (sin filtros de color)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_render_raw(solo_toma: int = None):
    """
    Renderiza microclips SIN color grading. Solo crop 9:16 y FPS constante.
    Útil para revisar el timing antes de aplicar efectos, o para archivar.
    """
    log("\n📹 OPCIÓN 2 — Render Raw (sin color grading)", MAGENTA)

    lista  = cargar_lista_validada()
    tomas  = lista.get("tomas", [])
    filtro = construir_filtro_raw()

    if solo_toma:
        tomas = [t for t in tomas if t["num_toma"] == solo_toma]

    info(f"Tomas: {len(tomas)} · Filtro: solo crop {RESOLUCION} + {FPS}fps")

    clips_ok   = []
    clips_fail = []

    for i, toma in enumerate(tomas, 1):
        log(f"\n  [{i}/{len(tomas)}] Toma {toma['num_toma']} — {toma.get('duracion_s', 0):.3f}s", CYAN)
        clip = renderizar_toma(toma, filtro)
        if clip:
            clips_ok.append(clip)
        else:
            clips_fail.append(toma["num_toma"])

    log(f"\n  ✅ {len(clips_ok)} clips raw · ❌ {len(clips_fail)} fallidos", VERDE)
    return [str(c) for c in clips_ok]

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Render Mudo (sin audio, para archivo)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_render_mudo(solo_toma: int = None):
    """
    Renderiza microclips con color grading PERO sin audio embebido.
    Idéntico a opción 1 (la opción 1 ya genera sin audio: -an).
    Esta opción además guarda los clips en una subcarpeta /archivo/
    para reutilización en futuros videos.
    """
    log("\n🗄️  OPCIÓN 3 — Render Mudo para Archivo", MAGENTA)

    lista    = cargar_lista_validada()
    tomas    = lista.get("tomas", [])
    filtro   = construir_filtro_color_grading()
    archivo_dir = VAULT_BASE / "microclips_archivo" / EVENTO_ID
    asegurar_dir(archivo_dir)

    if solo_toma:
        tomas = [t for t in tomas if t["num_toma"] == solo_toma]

    info(f"Destino de archivo: {archivo_dir}")
    info(f"Tomas: {len(tomas)}")

    global MICRO_DIR
    MICRO_DIR_ORIG = MICRO_DIR
    MICRO_DIR = archivo_dir  # Redirigir salida al directorio de archivo

    clips_ok   = []
    clips_fail = []
    for i, toma in enumerate(tomas, 1):
        log(f"\n  [{i}/{len(tomas)}] Toma {toma['num_toma']} → {archivo_dir.name}/", CYAN)
        clip = renderizar_toma(toma, filtro, con_audio=False)
        if clip:
            clips_ok.append(clip)
        else:
            clips_fail.append(toma["num_toma"])

    MICRO_DIR = MICRO_DIR_ORIG  # Restaurar

    ok(f"{len(clips_ok)} clips archivados en {archivo_dir}")
    return [str(c) for c in clips_ok]

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌔 Fábrica de Microclips V2 — Célula Madre 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  1  Render con color grading astrológico (producción)
  2  Render raw/limpio sin filtros de color (revisión)
  3  Render mudo para archivo reutilizable

  --toma N  Renderizar solo la toma N (para pruebas rápidas)
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3], required=True)
    parser.add_argument("--toma", type=int, default=None,
                        help="Renderizar solo la toma N")
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌔 FÁBRICA DE MICROCLIPS V2", MAGENTA)
    log(f"  ADN: {EVENTO_ID}", CYAN)
    log(f"  Output: {MICRO_DIR}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:   opcion_1_render_color_grading(args.toma)
    elif args.opcion == 2: opcion_2_render_raw(args.toma)
    elif args.opcion == 3: opcion_3_render_mudo(args.toma)

if __name__ == "__main__":
    main()
