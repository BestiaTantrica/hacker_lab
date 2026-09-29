#!/bin/bash
set -e
echo "1. Nodriza..."
python3 v2/celula_2/nodriza_visual.py --opcion 1
echo "2. Validate..."
cp /home/tomas2/MediaContingencia/Privada/Astrology_Vault/temp/lista_de_corte_resaca_eclipse_oct03.json /home/tomas2/MediaContingencia/Privada/Astrology_Vault/temp/lista_de_corte_validada_resaca_eclipse_oct03.json
echo "3. Fabrica..."
python3 v2/celula_3/fabrica_microclips.py --opcion 1
echo "4. Ensamblador Op1..."
python3 v2/celula_3/ensamblador_final.py --opcion 1
echo "5. Ensamblador Op3..."
python3 v2/celula_3/ensamblador_final.py --opcion 3
echo "6. Ensamblador Op4..."
python3 v2/celula_3/ensamblador_final.py --opcion 4
echo "Done!"
