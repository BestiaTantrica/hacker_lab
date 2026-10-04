#!/bin/bash
set -e

echo "=== NODRIZA VISUAL ==="
python3 v2/celula_2/nodriza_visual.py --opcion 1

echo "=== VALIDADOR ==="
python3 v2/celula_2/validador_de_ensamble.py --opcion 3

echo "=== FABRICA DE MICROCLIPS ==="
python3 v2/celula_3/fabrica_microclips.py --opcion 1

echo "=== MEZCLADOR SONORO ==="
python3 v2/celula_3/mezclador_sonoro.py --opcion 1
python3 v2/celula_3/mezclador_sonoro.py --opcion 3

echo "=== ENSAMBLADOR FINAL ==="
python3 v2/celula_3/ensamblador_final.py --opcion 1
python3 v2/celula_3/ensamblador_final.py --opcion 3
python3 v2/celula_3/ensamblador_final.py --opcion 4

echo "PIPELINE COMPLETO"
