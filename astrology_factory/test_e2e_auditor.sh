#!/bin/bash
# test_e2e_auditor.sh
# Script para correr el Flujo Canónico End-to-End con logs y freno de emergencia.

set -e  # Salir inmediatamente si un comando falla

LOG_FILE="auditoria_e2e_$(date +%Y%m%d_%H%M%S).log"
FACTORY_DIR="/home/tomas2/WORKSPACE/LAB/astrology_factory"

echo "==========================================================" | tee -a "$LOG_FILE"
echo "🚀 INICIANDO AUDITORÍA END-TO-END DE LA FÁBRICA ASTROLÓGICA" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
echo "Todos los logs detallados se guardarán en: $LOG_FILE"

cd "$FACTORY_DIR"

function run_step() {
    local paso="$1"
    local comando="$2"
    echo -e "\n⏳ EJECUTANDO: $paso" | tee -a "$LOG_FILE"
    echo "Comando: $comando" | tee -a "$LOG_FILE"
    
    # Ejecutamos el comando guardando el log (mantiene el código de salida)
    set -o pipefail
    $comando 2>&1 | tee -a "$LOG_FILE"
    set +o pipefail
    
    echo "✅ ÉXITO: $paso completado." | tee -a "$LOG_FILE"
}

# --- Célula 1: Narrativa ---
run_step "Generar Guion Diario" "python3 v2/celula_1/generador_guiones.py --opcion 1"
run_step "Síntesis de Voz (TTS -> MP3) y Timeline" "python3 v2/celula_1/cronometrador_y_tts.py --opcion 1"
run_step "Generar Subtítulos (.ass)" "python3 v2/celula_1/cronometrador_y_tts.py --opcion 2"

# --- Célula 2: Matching Visual ---
run_step "Asignación Semántica de Videos" "python3 v2/celula_2/nodriza_visual.py --opcion 1"
run_step "Auditoría Matemática y Ensamble" "python3 v2/celula_2/validador_de_ensamble.py --opcion 3"

# --- Célula 3: FFmpeg Engine ---
run_step "Fábrica de Microclips (Color Grading)" "python3 v2/celula_3/fabrica_microclips.py --opcion 1"
run_step "Mezcla Sonora (Voz + Música)" "python3 v2/celula_3/mezclador_sonoro.py --opcion 1"
run_step "Pad Binaural (Frecuencias Sanadoras)" "python3 v2/celula_3/mezclador_sonoro.py --opcion 2"
run_step "Inyección de SFX en transiciones" "python3 v2/celula_3/mezclador_sonoro.py --opcion 3"
run_step "Ensamble Final (Xfade Gapless)" "python3 v2/celula_3/ensamblador_final.py --opcion 1"
run_step "Quemado de Subtítulos" "python3 v2/celula_3/ensamblador_final.py --opcion 3"
run_step "Despliegue a Bóveda" "python3 v2/celula_3/ensamblador_final.py --opcion 4"

echo -e "\n==========================================================" | tee -a "$LOG_FILE"
echo "🎉 TEST E2E COMPLETADO EXITOSAMENTE 🎉" | tee -a "$LOG_FILE"
echo "Si ves este mensaje, la fábrica está operando al 100% de su capacidad." | tee -a "$LOG_FILE"
echo "Revisa la bóveda en Videos_Finales para ver tu video." | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
