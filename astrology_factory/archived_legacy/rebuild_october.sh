#!/bin/bash
echo "Iniciando Borrón y Cuenta Nueva para Octubre..."

for dir in produccion/Semana*_Octubre_*; do
    if [[ "$dir" == *"Resumen"* ]]; then
        echo "Saltando semanal: $dir"
        continue
    fi
    event=$(basename "$dir")
    
    echo "----------------------------------------"
    echo "Destruyendo caché vieja de: $event"
    rm -f "$dir/guion.txt"
    rm -f "$dir/storyboard.txt"
    rm -f "$dir/"*.ass
    rm -f "$dir/"*_mixed.mp3
    rm -f "$dir/"*.mp4
    rm -f "$dir/"*.mp3

    echo "Escribiendo nuevo guion (CTA 5s) para: $event"
    venv/bin/python content_factory/ai_persona_engine.py "$event"
    
    echo "Renderizando video limpio para: $event"
    venv/bin/python content_factory/tts_local.py "$event"
    
done

echo "=== FÁBRICA OCTUBRE FINALIZADA ==="
