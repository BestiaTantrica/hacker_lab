#!/bin/bash
# Disparador One-Shot para Publicación Programada en Meta (Instagram y Facebook)
# Programado para: 16 Noviembre 2026 - 20:00 hs (ART)
LOG_FILE="/home/LAB/astrology_factory/produccion/meta_publicacion.log"

echo "==================================================" >> "$LOG_FILE"
echo "[$(date)] 🚀 INICIANDO PUBLICACIÓN PROGRAMADA META (20:00 ART)..." >> "$LOG_FILE"
echo "Evento: 2026-11-17_Luna_Oposicion_Marte_Acuario" >> "$LOG_FILE"

/home/LAB/astrology_factory/venv/bin/python /home/LAB/astrology_factory/v2/celula_4/publicador_meta.py --evento 2026-11-17_Luna_Oposicion_Marte_Acuario >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "[$(date)] ✅ PUBLICACIÓN FINALIZADA con código: $EXIT_CODE" >> "$LOG_FILE"
echo "Limpiando tarea one-shot de crontab..." >> "$LOG_FILE"
(crontab -l 2>/dev/null | grep -v "disparador_programado_17nov.sh") | crontab -
echo "==================================================" >> "$LOG_FILE"

