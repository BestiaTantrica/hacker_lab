#!/bin/bash
set -e
python3 v2/celula_3/mezclador_sonoro.py --opcion 2
python3 v2/celula_3/mezclador_sonoro.py --opcion 3
python3 v2/celula_3/ensamblador_final.py --opcion 2
python3 v2/celula_3/ensamblador_final.py --opcion 3
python3 v2/celula_3/ensamblador_final.py --opcion 4
