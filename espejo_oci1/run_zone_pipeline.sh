#!/bin/bash
# run_zone_pipeline.sh — Cascada de Pesca por Zona Horaria
# =========================================================
# Uso: ./run_zone_pipeline.sh [americas|emea|asia]
# 
# Flujo ESTRICTO (cascada lineal, sin paralelismos):
#   1. mass_recon.py --zone ZONA      → actual_{zona}.json
#   2. comparador.py --zone ZONA      → delta_{zona}_FECHA.json
#   3. explotador_automatico.py       → hallazgos verificados ($50+)
#   4. notificador → Telegram         → link al C2 Panel (SOLO si hay hallazgos)
#
# Si cualquier eslabón falla, la cascada se detiene. Sin Telegram si no hay bugs reales.

set -euo pipefail

ZONA="${1:-americas}"
BASE="/home/ubuntu/plataforma_operativa"
VENV="/home/ubuntu/workspace_lab/venv/bin/python3"
LOG="${BASE}/logs/pipeline_${ZONA}.log"
C2_PANEL_URL="${C2_PANEL_URL:-http://localhost:8000}"

log() { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [INFO] [$ZONA] $1" | tee -a "$LOG"; }
error() { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [ERROR] [$ZONA] $1" | tee -a "$LOG"; exit 1; }

log "============================================================"
log "🌐 INICIANDO CASCADA — ZONA: ${ZONA^^}"

# ── Eslabón 1: Descubrimiento Masivo ──────────────────────────────────────────
log "Eslabón 1: Descubrimiento masivo (mass_recon.py)"
$VENV "${BASE}/monitores/mass_recon.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error "❌ mass_recon.py falló. Cascada detenida."
log "✅ Eslabón 1 completado: actual_${ZONA}.json generado."

# ── Eslabón 2: Comparador de Deltas ───────────────────────────────────────────
log "Eslabón 2: Comparador de deltas (comparador.py)"
$VENV "${BASE}/monitores/comparador.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error "❌ comparador.py falló. Cascada detenida."

# Verificar si existe un delta con subdominios nuevos hoy
DELTA_FILE=$(ls -t "${BASE}/resultados/delta_${ZONA}_$(date -u +%Y-%m-%d).json" 2>/dev/null | head -1 || true)
if [ -z "$DELTA_FILE" ]; then
    log "ℹ️  Sin subdominios nuevos en la zona ${ZONA} hoy. Cascada finalizada limpiamente."
    exit 0
fi
log "✅ Eslabón 2 completado: delta encontrado en $DELTA_FILE"

# ── Eslabón 3: Verificador de Exploits ────────────────────────────────────────
log "Eslabón 3: Verificador de exploits (explotador_automatico.py)"
EXPLOTADOR_OUTPUT=$($VENV "${BASE}/monitores/explotador_automatico.py" --delta "$DELTA_FILE" --max 500 2>&1)
echo "$EXPLOTADOR_OUTPUT" >> "$LOG"

# Buscar si hubo hallazgos reales guardados
REPORTE_HOY="${BASE}/resultados/explotador_$(date -u +%Y-%m-%d).json"
if [ ! -f "$REPORTE_HOY" ] || [ "$(cat "$REPORTE_HOY")" = "[]" ]; then
    log "ℹ️  Sin hallazgos verificados en zona ${ZONA}. No se notifica a Telegram. Cascada finalizada."
    exit 0
fi

TOTAL_BUGS=$(python3 -c "import json; data=json.load(open('$REPORTE_HOY')); print(len(data))" 2>/dev/null || echo "N/A")
log "✅ Eslabón 3 completado: $TOTAL_BUGS hallazgo(s) verificado(s)."

# ── Eslabón 4: Notificación Telegram (link al C2 Panel) ───────────────────────
log "Eslabón 4: Notificando a Telegram con link al C2 Panel."
python3 -c "
import sys
sys.path.append('${BASE}/monitores')
from notificador import send_telegram

msg = (
    '🎯 *RED DE PESCA — ALERTA DE VALOR*\n\n'
    '🌐 *Zona:* ${ZONA^^}\n'
    '🐛 *Bugs verificados:* ${TOTAL_BUGS}\n\n'
    '📋 *Acción:* Abre el C2 Panel, revisa los hallazgos y genera el reporte H1 en 1 clic.\n\n'
    '🔗 *Panel:* ${C2_PANEL_URL}'
)
send_telegram(msg)
print('Telegram enviado.')
" >> "$LOG" 2>&1 || log "⚠️  Telegram falló pero el pipeline finalizó correctamente."

log "🏁 CASCADA ZONA ${ZONA^^} COMPLETADA EXITOSAMENTE."
log "============================================================"
