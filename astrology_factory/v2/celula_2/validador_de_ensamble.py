#!/usr/bin/env python3
"""
🌓 CÉLULA MADRE 2 — Script 2.2: validador_de_ensamble.py
El guardián matemático. Lee lista_de_corte.json y lo transforma en
lista_de_corte_validada.json — el archivo sagrado que usa video_maker.py.
NUNCA ejecuta FFmpeg. Solo audita, mide y anota instrucciones.

Uso:
  python v2/celula_2/validador_de_ensamble.py --opcion 1   # Dry-run: verifica existencia y duración
  python v2/celula_2/validador_de_ensamble.py --opcion 2   # Calcula instrucciones trim/loop
  python v2/celula_2/validador_de_ensamble.py --opcion 3   # Reporte final → lista_de_corte_validada.json
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID    = ADN["produccion"]["evento_id"]
VAULT_BASE   = Path(ADN["assets"]["boveda_base"])
TEMP_DIR     = VAULT_BASE / "temp"
TOLERANCIA   = ADN["validaciones"]["tolerancia_duracion_ms"]
MAX_CLIPS    = ADN["validaciones"]["max_clips_video_corto_120s"]
MIN_DUR_CLIP = ADN["validaciones"]["min_duracion_clip_segundos"]
MAX_DUR_CLIP = ADN["validaciones"]["max_duracion_clip_segundos"]

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# ── I/O ──────────────────────────────────────────────────────────────────────

def cargar_lista_de_corte() -> dict:
    ruta = TEMP_DIR / f"lista_de_corte_{EVENTO_ID}.json"
    if not ruta.exists():
        err(f"lista_de_corte no encontrada: {ruta}")
        err("Primero ejecuta: asignador_semantico.py --opcion N")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

def guardar_lista_validada(lista: dict) -> Path:
    asegurar_dir(TEMP_DIR)
    ruta = TEMP_DIR / f"lista_de_corte_validada_{EVENTO_ID}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    ok(f"Lista validada guardada: {ruta}")
    return ruta

# ── ffprobe ───────────────────────────────────────────────────────────────────

FORMATOS_IMG = {".jpg", ".jpeg", ".png"}

def _es_imagen(path: Path) -> bool:
    return path.suffix.lower() in FORMATOS_IMG

def get_duracion_video_ms(path: Path) -> float | None:
    """
    Obtiene duración de un video en milisegundos usando ffprobe.
    Retorna None si el archivo no existe o está corrupto.
    """
    if not path.exists():
        return None
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        raw = result.stdout.decode().strip()
        if raw:
            return float(raw) * 1000.0
        return None
    except Exception:
        return None

def get_dimensiones_video(path: Path) -> tuple[int, int]:
    """Retorna (width, height). (0,0) si no se puede leer."""
    if not path.exists():
        return 0, 0
    cmd = [
        "ffprobe", "-v", "quiet",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0", str(path)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        partes = result.stdout.decode().strip().split(",")
        return int(partes[0]), int(partes[1])
    except Exception:
        return 0, 0

# ── Cálculo de instrucciones FFmpeg ──────────────────────────────────────────

def calcular_instruccion_ffmpeg(dur_video_ms: float, dur_hueco_ms: float) -> dict:
    """
    Determina la instrucción FFmpeg necesaria para que un video
    ocupe exactamente el hueco de tiempo requerido.

    Retorna dict con: accion_ffmpeg, requiere_loop, detalles.
    """
    # Tolerancia matemática: el video puede ser hasta TOLERANCIA ms más largo
    if dur_video_ms >= dur_hueco_ms - TOLERANCIA:
        # TRIM: el video es suficientemente largo, se corta al tiempo exacto
        return {
            "accion_ffmpeg":  "trim",
            "requiere_loop":  False,
            "start_trim_ms":  0.0,
            "end_trim_ms":    round(dur_hueco_ms, 3),
            "num_loops":      1,
            "dur_video_ms":   round(dur_video_ms, 3),
            "dur_hueco_ms":   round(dur_hueco_ms, 3),
            "sobrante_ms":    round(dur_video_ms - dur_hueco_ms, 3),
        }
    else:
        # LOOP: el video es más corto que el hueco, hay que repetirlo
        num_loops = math.ceil(dur_hueco_ms / dur_video_ms)
        dur_total_loopada = dur_video_ms * num_loops
        # Trim al final del loop para cortar al tiempo exacto
        return {
            "accion_ffmpeg":  "loop",
            "requiere_loop":  True,
            "start_trim_ms":  0.0,
            "end_trim_ms":    round(dur_hueco_ms, 3),
            "num_loops":      num_loops,
            "dur_video_ms":   round(dur_video_ms, 3),
            "dur_hueco_ms":   round(dur_hueco_ms, 3),
            "dur_total_loopada_ms": round(dur_total_loopada, 3),
            "faltante_ms":    round(dur_hueco_ms - dur_video_ms, 3),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Dry-Run: Verificación de Existencia y Duración
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_dry_run() -> tuple[list[dict], list[str]]:
    """
    Verifica que cada archivo asignado:
    1. Exista físicamente en disco
    2. Sea legible por ffprobe (no corrupto)
    3. Tenga una duración > 0

    Retorna (resultados_enriquecidos, lista_de_errores).
    """
    log("\n🔍 OPCIÓN 1 — Dry-Run: Verificación de Stock", MAGENTA)

    lista = cargar_lista_de_corte()
    asignaciones = lista.get("asignaciones", [])
    errores   = []
    warnings  = []
    resultados = []

    log(f"\n  Verificando {len(asignaciones)} tomas...", CYAN)
    log(f"  {'#':>2}  {'ROL':<22}  {'DUR_HUECO':>10}  {'STATUS':<12}  ARCHIVO", CYAN)
    log(f"  {'─'*80}", GRIS)

    for asig in asignaciones:
        num       = asig["num_toma"]
        rol       = asig.get("rol", "?")
        dur_hueco = asig["duracion_ms"]
        archivo   = asig.get("archivo_video")

        resultado = {**asig, "verificacion": {}}

        if not archivo:
            msg = f"Toma {num}: sin archivo asignado"
            errores.append(msg)
            resultado["verificacion"] = {
                "existe": False, "dur_video_ms": None,
                "es_valido": False, "error": "sin_archivo"
            }
            log(f"  {num:>2}  {rol:<22}  {dur_hueco/1000:>8.2f}s  {'❌ SIN FILE':<12}", ROJO)
            resultados.append(resultado)
            continue

        path = Path(archivo)

        # 1. Existencia física
        if not path.exists():
            msg = f"Toma {num}: archivo no existe: {path.name}"
            errores.append(msg)
            resultado["verificacion"] = {
                "existe": False, "dur_video_ms": None,
                "es_valido": False, "error": "no_existe"
            }
            log(f"  {num:>2}  {rol:<22}  {dur_hueco/1000:>8.2f}s  {'❌ NO EXISTE':<12}  {path.name[:35]}", ROJO)
            resultados.append(resultado)
            continue

        # 2. Duración: imágenes → el motor aplica zoompan al hueco; videos → ffprobe
        if _es_imagen(path):
            dur_video_ms = dur_hueco   # la imagen llena el slot entero vía zoompan
            resultado["verificacion"] = {
                "existe":       True,
                "dur_video_ms": round(dur_video_ms, 3),
                "dur_video_s":  round(dur_video_ms / 1000, 3),
                "es_valido":    True,
                "error":        None,
                "es_imagen":    True,
                "necesita_loop": False,
            }
            log(f"  {num:>2}  {rol:<22}  {dur_hueco/1000:>8.2f}s  {'📷 IMG':<12}  {path.name[:35]}", CYAN)
            resultados.append(resultado)
            continue

        dur_video_ms = get_duracion_video_ms(path)
        if dur_video_ms is None or dur_video_ms <= 0:
            msg = f"Toma {num}: ffprobe no pudo leer {path.name}"
            errores.append(msg)
            resultado["verificacion"] = {
                "existe": True, "dur_video_ms": None,
                "es_valido": False, "error": "ffprobe_fallo"
            }
            log(f"  {num:>2}  {rol:<22}  {dur_hueco/1000:>8.2f}s  {'❌ CORRUPTO':<12}  {path.name[:35]}", ROJO)
            resultados.append(resultado)
            continue

        # 3. Validaciones adicionales
        w, h = get_dimensiones_video(path)
        es_vertical = h > w if w > 0 and h > 0 else None

        if dur_video_ms < MIN_DUR_CLIP * 1000:
            warnings.append(f"Toma {num}: video muy corto ({dur_video_ms/1000:.2f}s < {MIN_DUR_CLIP}s mínimo)")

        resultado["verificacion"] = {
            "existe":           True,
            "dur_video_ms":     round(dur_video_ms, 3),
            "dur_video_s":      round(dur_video_ms / 1000, 3),
            "es_valido":        True,
            "error":            None,
            "resolucion":       f"{w}x{h}" if w else "desconocida",
            "es_vertical":      es_vertical,
            "necesita_loop":    dur_video_ms < dur_hueco,
        }

        status = "✅ OK" if not resultado["verificacion"]["necesita_loop"] else "🔄 LOOP"
        color  = VERDE if status == "✅ OK" else AMARILLO
        log(f"  {num:>2}  {rol:<22}  {dur_hueco/1000:>8.2f}s  {status:<12}  {path.name[:35]}", color)
        if resultado["verificacion"]["necesita_loop"]:
            log(f"       └ Video: {dur_video_ms/1000:.2f}s < Hueco: {dur_hueco/1000:.2f}s (requerirá loop)", AMARILLO)

        resultados.append(resultado)

    # Resumen
    num_ok     = sum(1 for r in resultados if r["verificacion"].get("es_valido"))
    num_loops  = sum(1 for r in resultados if r["verificacion"].get("necesita_loop"))
    num_img    = sum(1 for r in resultados if r["verificacion"].get("es_imagen"))
    num_err    = len(errores)

    log(f"\n  {'─'*50}", CYAN)
    log(f"  📊 RESUMEN DRY-RUN:", CYAN)
    log(f"     ✅ Válidos:   {num_ok}/{len(asignaciones)}", VERDE)
    log(f"     🔄 Necesitan loop: {num_loops}", AMARILLO)
    log(f"     📷 Imágenes (zoompan): {num_img}", CYAN)
    log(f"     ❌ Errores:   {num_err}", ROJO if num_err else VERDE)

    for w in warnings:
        warn(w)
    for e in errores:
        err(e)

    if num_err > 0:
        warn("Hay errores. Considera re-ejecutar asignador_semantico.py --opcion 4")

    return resultados, errores

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Cálculo de Instrucciones Trim / Loop
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_calcular_instrucciones() -> list[dict]:
    """
    Por cada toma en lista_de_corte.json, inyecta las instrucciones matemáticas
    exactas que video_maker.py usará en FFmpeg:
    - trim: cortar el video a la duración exacta del hueco
    - loop: repetir el video N veces y luego cortar

    No guarda archivo; retorna la lista enriquecida.
    """
    log("\n⚙️  OPCIÓN 2 — Cálculo de Instrucciones Trim/Loop", MAGENTA)

    resultados_dry, errores = opcion_1_dry_run()

    log(f"\n  Calculando instrucciones FFmpeg...", CYAN)
    log(f"  {'#':>2}  {'ROL':<20}  {'DUR_HUECO':>10}  {'DUR_VIDEO':>10}  ACCIÓN", CYAN)
    log(f"  {'─'*70}", GRIS)

    instrucciones = []
    for r in resultados_dry:
        num       = r["num_toma"]
        rol       = r.get("rol", "?")
        dur_hueco = r["duracion_ms"]
        verif     = r.get("verificacion", {})

        if not verif.get("es_valido"):
            # Sin video válido: marcar como pendiente con instrucción nula
            r["accion_ffmpeg"]  = "PENDIENTE_SIN_VIDEO"
            r["requiere_loop"]  = None
            log(f"  {num:>2}  {rol:<20}  {dur_hueco/1000:>8.2f}s  {'---':>10}  ⚠️  SIN VIDEO", AMARILLO)
            instrucciones.append(r)
            continue

        if verif.get("es_imagen"):
            r["accion_ffmpeg"]  = "zoompan"
            r["requiere_loop"]  = False
            log(f"  {num:>2}  {rol:<20}  {dur_hueco/1000:>8.2f}s  {'---':>10}  📷 ZOOMPAN (motor)", CYAN)
            instrucciones.append(r)
            continue

        dur_video_ms = verif["dur_video_ms"]
        instruccion  = calcular_instruccion_ffmpeg(dur_video_ms, dur_hueco)

        # Inyectar en el resultado
        r.update(instruccion)

        accion = instruccion["accion_ffmpeg"].upper()
        if instruccion["requiere_loop"]:
            detalle = f"x{instruccion['num_loops']} loops → trim a {instruccion['end_trim_ms']/1000:.3f}s"
            color   = AMARILLO
        else:
            sobrante = instruccion.get("sobrante_ms", 0)
            detalle  = f"trim → {instruccion['end_trim_ms']/1000:.3f}s (sobra {sobrante/1000:.3f}s)"
            color    = VERDE

        log(f"  {num:>2}  {rol:<20}  {dur_hueco/1000:>8.2f}s  {dur_video_ms/1000:>8.2f}s  {accion}: {detalle}", color)
        instrucciones.append(r)

    # Resumen de loops
    num_loops    = sum(1 for i in instrucciones if i.get("requiere_loop"))
    num_trims    = sum(1 for i in instrucciones if i.get("accion_ffmpeg") == "trim")
    num_zoompan  = sum(1 for i in instrucciones if i.get("accion_ffmpeg") == "zoompan")
    log(f"\n  {'─'*50}", CYAN)
    log(f"  📊 Instrucciones calculadas:", CYAN)
    log(f"     ✂️  Trim:           {num_trims}", VERDE)
    log(f"     🔄 Loop:           {num_loops}", AMARILLO if num_loops else VERDE)
    log(f"     📷 Zoompan (img): {num_zoompan}", CYAN)

    return instrucciones

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Reporte Final (El Handoff a video_maker.py)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_reporte_final():
    """
    Ejecuta Opción 1 + 2 internamente, consolida TODO en un único
    lista_de_corte_validada.json — el archivo sagrado para video_maker.py (FFmpeg Builder).

    Estructura final de cada entrada:
    {
      num_toma, rol, inicio_ms, fin_ms, duracion_ms, duracion_s,
      texto, etiqueta_visual, archivo_video, nombre_video,
      fuente_asignacion, accion_ffmpeg, requiere_loop,
      start_trim_ms, end_trim_ms, num_loops,
      dur_video_ms [verificado], resolucion, es_vertical
    }
    """
    log("\n📋 OPCIÓN 3 — Reporte Final (Handoff a video_maker.py)", MAGENTA)
    log("  Ejecutando verificación + cálculo de instrucciones...\n", GRIS)

    instrucciones = opcion_2_calcular_instrucciones()
    lista_original = cargar_lista_de_corte()

    # Verificar regla anti-spam: max clips para video corto
    total_s = lista_original.get("total_duracion_s", 0)
    num_clips = len(instrucciones)
    MAX_CLIPS_OVERRIDE = 30
    if total_s <= 120 and num_clips > MAX_CLIPS_OVERRIDE:
        err(f"🚨 BLOQUEO ANTI-SPAM: {num_clips} clips para video de {total_s:.1f}s")
        err(f"   Máximo permitido: {MAX_CLIPS_OVERRIDE} clips. Re-ejecuta asignador con menos tomas.")
        err("   El render NO procederá hasta resolver esto.")
        # Anotarlo en el JSON pero no abortar (el humano decide)
        bloqueado = True
    else:
        bloqueado = False

    # Verificar que todos los videos estén asignados
    sin_video = [i["num_toma"] for i in instrucciones if not i.get("archivo_video")]
    pendientes = [i["num_toma"] for i in instrucciones if i.get("accion_ffmpeg") == "PENDIENTE_SIN_VIDEO"]

    # Construir JSON final
    lista_validada = {
        "evento_id":        EVENTO_ID,
        "semana":           lista_original.get("semana", ""),
        "total_tomas":      num_clips,
        "total_duracion_s": total_s,
        "validado":         True,
        "bloqueado_anti_spam": bloqueado,
        "tomas_sin_video":  sin_video,
        "tomas_pendientes": pendientes,
        "resumen": {
            "num_trim":     sum(1 for i in instrucciones if i.get("accion_ffmpeg") == "trim"),
            "num_loop":     sum(1 for i in instrucciones if i.get("requiere_loop")),
            "num_sin_video":len(sin_video),
            "duracion_total_s": total_s,
        },
        "tomas": instrucciones
    }

    # ── Imprimir tabla resumen final ─────────────────────────────────────────
    log(f"\n{'═'*70}", VERDE)
    log(f"  📦 LISTA DE CORTE VALIDADA — HANDOFF A VIDEO_MAKER", VERDE)
    log(f"{'═'*70}", VERDE)
    log(f"  {'#':>2}  {'ROL':<20}  {'INICIO':>8}  {'FIN':>8}  {'ACCIÓN':<8}  ARCHIVO", CYAN)
    log(f"  {'─'*70}", GRIS)

    for t in instrucciones:
        num      = t["num_toma"]
        rol      = t.get("rol", "?")
        inicio_s = t["inicio_ms"] / 1000
        fin_s    = t["fin_ms"] / 1000
        accion   = (t.get("accion_ffmpeg") or "?").upper()[:6]
        archivo  = (t.get("nombre_video") or "⚠️  SIN VIDEO")[:38]

        if t.get("requiere_loop"):
            color = AMARILLO
            loops = t.get("num_loops", "?")
            accion_str = f"LOOP×{loops}"
        elif accion == "TRIM":
            color = VERDE
            accion_str = "TRIM  "
        else:
            color = ROJO
            accion_str = accion

        log(f"  {num:>2}  {rol:<20}  {inicio_s:>7.3f}s  {fin_s:>7.3f}s  {accion_str:<8}  {archivo}", color)

    log(f"{'═'*70}", VERDE)
    log(f"  Total: {num_clips} tomas · {total_s:.2f}s · "
        f"Trim:{lista_validada['resumen']['num_trim']} "
        f"Loop:{lista_validada['resumen']['num_loop']} "
        f"Sin video:{lista_validada['resumen']['num_sin_video']}", CYAN)

    if bloqueado:
        log(f"\n  🚨 ATENCIÓN: Producción BLOQUEADA por regla anti-spam.", ROJO)
        log(f"     Edita la asignación antes de pasar a video_maker.py.", ROJO)
    elif sin_video:
        log(f"\n  ⚠️  Hay {len(sin_video)} tomas sin video. Revisar antes de renderizar.", AMARILLO)
    else:
        log(f"\n  ✅ Todo en orden. Listo para video_maker.py.", VERDE)

    ruta = guardar_lista_validada(lista_validada)

    log(f"\n  ➡️  Siguiente: python content_factory/video_maker.py", AMARILLO)
    return str(ruta)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌓 Validador de Ensamble V2 — Célula Madre 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  1  Dry-run: verifica existencia, duración y validez de cada video asignado
  2  Calcula instrucciones FFmpeg (trim o loop) para cada toma
  3  Reporte final completo → lista_de_corte_validada.json (HANDOFF A VIDEO_MAKER)

Flujo recomendado: --opcion 3 (ejecuta 1 y 2 internamente de forma silenciosa)
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3], required=True)
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌓 VALIDADOR DE ENSAMBLE V2", MAGENTA)
    log(f"  ADN: {EVENTO_ID}", CYAN)
    log(f"  Tolerancia: {TOLERANCIA}ms · Max clips: {MAX_CLIPS}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:
        opcion_1_dry_run()
    elif args.opcion == 2:
        opcion_2_calcular_instrucciones()
    elif args.opcion == 3:
        opcion_3_reporte_final()

if __name__ == "__main__":
    main()
