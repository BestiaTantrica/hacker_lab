#!/bin/bash
echo "Iniciando renderización de Octubre con CTA corregidos..."
for dir in produccion/Semana*_Octubre_*; do
    if [[ "$dir" == *"Resumen"* ]]; then
        continue
    fi
    event=$(basename "$dir")
    
    # Check if guion.txt exists
    if [ ! -f "$dir/guion.txt" ]; then
        echo "Saltando $event, no hay guion."
        continue
    fi
    
    echo "Renderizando: $event"
    venv/bin/python content_factory/tts_local.py "$event"
done
