#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditor_calidad_industrial.py — Quality Gate Automático V2
─────────────────────────────────────────────────────────────────────────────
Valida matemáticamente y editorialmente el producto final antes de declararlo
APROBADO en la Bóveda. Si algún control falla, aborta y reporta la causa exacta.
"""

import sys
import json
import subprocess
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY_ROOT))

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; AMARILLO = "\033[93m"

def ok(m): print(f"{VERDE}  ✅ [CALIDAD] {m}{RESET}")
def err(m): print(f"{ROJO}  ❌ [FALLA CALIDAD] {m}{RESET}")
def info(m): print(f"{CYAN}  ℹ️  [CALIDAD] {m}{RESET}")

def auditar_entrega(evento_id: str, video_path: Path, timeline_path: Path, lista_corte_path: Path) -> bool:
    info(f"Iniciando Quality Gate Industrial para: {evento_id}...")

    # 1. Comprobar existencia y peso del video
    if not video_path.exists():
        err(f"El archivo de video final no existe: {video_path}")
        return False
    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb < 5.0:
        err(f"El video pesa menos de 5MB ({size_mb:.2f}MB). Posible render incompleto.")
        return False
    ok(f"Archivo de video válido ({size_mb:.2f} MB)")

    # 2. Comprobar duración con ffprobe vs Timeline
    if not timeline_path.exists():
        err(f"Timeline no encontrado: {timeline_path}")
        return False
    with open(timeline_path, encoding="utf-8") as f:
        timeline = json.load(f)
    dur_esperada = timeline.get("total_duracion_s") or (timeline.get("total_duracion_ms", 0) / 1000.0)

    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(video_path)
    ]
    p = subprocess.run(probe_cmd, capture_output=True, text=True)
    try:
        dur_real = float(p.stdout.strip())
    except Exception:
        err(f"No se pudo leer la duración del video con ffprobe: {p.stderr}")
        return False

    dif = abs(dur_real - dur_esperada)
    if dif > 0.60:
        err(f"Desfase excesivo entre video ({dur_real:.2f}s) y audio ({dur_esperada:.2f}s). Diferencia: {dif:.3f}s")
        return False
    ok(f"Sincronía perfecta: Video={dur_real:.2f}s | Audio={dur_esperada:.2f}s (Dif: {dif:.3f}s)")

    # 3. Comprobar lista de corte (Loop y Astrolabio)
    if not lista_corte_path.exists():
        err(f"Lista de corte validada no encontrada: {lista_corte_path}")
        return False
    with open(lista_corte_path, encoding="utf-8") as f:
        corte_data = json.load(f)
    
    tomas = corte_data.get("tomas") or corte_data.get("asignaciones", [])
    if len(tomas) < 5:
        err(f"Se esperaban al menos 5 tomas, se encontraron {len(tomas)}")
        return False

    # Verificar Loop T1 y T5
    t1_cortes = tomas[0].get("cortes", [])
    t5_cortes = tomas[-1].get("cortes", [])
    if t1_cortes and t5_cortes:
        t1_primero = Path(t1_cortes[0].get("archivo", "")).name
        t5_ultimo = Path(t5_cortes[-1].get("archivo", "")).name
        if t1_primero != t5_ultimo:
            err(f"Loop roto: Toma 1 empieza con '{t1_primero}' pero Toma 5 termina con '{t5_ultimo}'")
            return False
        ok(f"Loop infinito verificado: T1 y T5 comparten el portal '{t1_primero}'")

    # Verificar Astrolabio en Toma 3
    t3_cortes = tomas[2].get("cortes", [])
    t3_archivo = t3_cortes[0].get("archivo", "") if t3_cortes else tomas[2].get("archivo_video", "")
    if "reloj_2d" not in t3_archivo:
        err(f"Toma 3 no contiene el Astrolabio 2D (archivo={t3_archivo})")
        return False
    ok(f"Toma 3 contiene el Astrolabio 2D verificado ({Path(t3_archivo).name})")

    # 4. Comprobar resolución vertical 9:16
    res_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=p=0", str(video_path)
    ]
    p_res = subprocess.run(res_cmd, capture_output=True, text=True)
    res_str = p_res.stdout.strip()
    if res_str != "1080,1920":
        err(f"Resolución no estándar: {res_str} (Debe ser 1080x1920)")
        return False
    ok("Resolución vertical 1080x1920 (9:16) confirmada")

    print(f"\n{VERDE}🏆 QUALITY GATE INDUSTRIAL: 100% APROBADO{RESET}\n")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: auditor_calidad_industrial.py <evento_id> <video_path> <timeline_path> <lista_corte_path>")
        sys.exit(1)
    ev_id = sys.argv[1]
    v_path = Path(sys.argv[2])
    t_path = Path(sys.argv[3])
    c_path = Path(sys.argv[4])
    if not auditar_entrega(ev_id, v_path, t_path, c_path):
        sys.exit(1)
    sys.exit(0)
