#!/bin/bash
set -e

echo "=== NODRIZA VISUAL ==="
python3 v2/celula_2/nodriza_visual.py --opcion 1

echo "=== VALIDADOR ==="
python3 v2/celula_2/validador_de_ensamble.py --opcion 3

echo "=== VIDEO MAKER (Single-Pass FFmpeg Builder) ==="
python3 content_factory/video_maker.py

echo "PIPELINE V2 COMPLETO ✅"
