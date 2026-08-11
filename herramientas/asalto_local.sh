#!/bin/bash

# ==============================================================================
# 🚀 SCRIPT DE ASALTO LOCAL (BUG BOUNTY MODO BESTIA CON FRENOS)
# ==============================================================================
# Este script utiliza las herramientas Go-Stack para realizar un escaneo
# masivo. Está diseñado para no colapsar routers residenciales (frenos de red)
# y filtrar infraestructuras CDN (Cloudflare/Akamai).
#
# Uso:
#   ./asalto_local.sh --recon targets.txt       (Fases 1, 2, 3: Rápidas)
#   ./asalto_local.sh --attack urls_limpias.txt (Fase 4: Nuclei, Lenta/Nocturna)
# ==============================================================================

# 1. Definición de Rutas y Variables
TOOLS_DIR="/home/tomas2/WORKSPACE/LAB/herramientas/go-tools"
RESULT_DIR="/home/tomas2/WORKSPACE/LAB/herramientas/resultados_asalto"
FECHA=$(date +"%Y-%m-%d_%H%M")

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ Error: Faltan argumentos."
    echo "Uso:"
    echo "  ./asalto_local.sh --recon <archivo_dominios.txt>"
    echo "  ./asalto_local.sh --attack <archivo_urls_limpias.txt>"
    exit 1
fi

MODE="$1"
TARGET_FILE=$(realpath "$2")

if [ ! -f "$TARGET_FILE" ]; then
    echo "❌ Error: El archivo $TARGET_FILE no existe."
    exit 1
fi

mkdir -p "$RESULT_DIR"
cd "$RESULT_DIR"

echo "========================================================================"
echo "🔥 INICIANDO ASALTO LOCAL - MODO: $MODE - FECHA: $FECHA"
echo "📂 Guardando resultados en: $RESULT_DIR"
echo "========================================================================"

if [ "$MODE" == "--recon" ]; then
    # --------------------------------------------------------------------------
    # FASE 1: RECONOCIMIENTO DE SUBDOMINIOS (subfinder)
    # Límite: 50 hilos concurrentes
    # --------------------------------------------------------------------------
    echo "⏳ [Fase 1/3] Buscando subdominios con subfinder..."
    $TOOLS_DIR/subfinder -dL "$TARGET_FILE" -all -t 50 -o "1_subdominios_$FECHA.txt" -silent

    # --------------------------------------------------------------------------
    # FASE 2: RESOLUCIÓN DNS (dnsx)
    # FRENO RED: Límite de 30 hilos y 50 peticiones por segundo.
    # --------------------------------------------------------------------------
    echo "⏳ [Fase 2/3] Verificando cuáles están vivos (DNS) con dnsx..."
    $TOOLS_DIR/dnsx -l "1_subdominios_$FECHA.txt" -t 30 -rl 50 -silent -o "2_vivos_$FECHA.txt"

    # --------------------------------------------------------------------------
    # FASE 3: PROBING HTTP & FILTRO CDN (httpx)
    # FRENO RED: -t 20 y -rl 50.
    # FILTRO CDN: -exclude cdn (descarta Cloudflare, Akamai, etc. automáticamente)
    # --------------------------------------------------------------------------
    echo "⏳ [Fase 3/3] Escaneando puertos web y descartando CDNs (Cloudflare) con httpx..."
    $TOOLS_DIR/httpx -l "2_vivos_$FECHA.txt" -t 20 -rl 50 -exclude cdn -title -tech-detect -status-code -silent -o "3_web_$FECHA.txt"

    # Limpiamos el archivo de salida para quedarnos solo con las URLs puras
    cat "3_web_$FECHA.txt" | awk '{print $1}' > "3_urls_limpias_$FECHA.txt"

    echo "========================================================================"
    echo "✅ FASE DE RECONOCIMIENTO (RECON) TERMINADA"
    echo "📂 Lista de objetivos puros (sin CDN): $RESULT_DIR/3_urls_limpias_$FECHA.txt"
    echo "👉 Usa este archivo esta noche con: ./asalto_local.sh --attack 3_urls_limpias_$FECHA.txt"
    echo "========================================================================"

elif [ "$MODE" == "--attack" ]; then
    # --------------------------------------------------------------------------
    # FASE 4: ESCANEO DE VULNERABILIDADES (nuclei)
    # FRENO DE RED CRÍTICO (Modo Nocturno Protegido): 
    # -c 15 (15 plantillas simultáneas)
    # -bs 10 (tamaño de lote de 10 hosts)
    # -rl 50 (50 peticiones HTTP por segundo como máximo)
    # --------------------------------------------------------------------------
    echo "⏳ [Fase 4] Buscando vulnerabilidades con Nuclei (Frenos de Red Activados)..."
    $TOOLS_DIR/nuclei -l "$TARGET_FILE" -t cves/ -t exposed-panels/ -t misconfiguration/ -t vulnerabilities/ \
        -c 15 -bs 10 -rl 50 -timeout 10 -silent -o "4_vulnerabilidades_$FECHA.json" -jsonl

    echo "========================================================================"
    echo "✅ ASALTO DE VULNERABILIDADES TERMINADO"
    echo "📂 Revisa tus resultados en: $RESULT_DIR/4_vulnerabilidades_$FECHA.json"
    echo "========================================================================"
else
    echo "❌ Error: Modo no reconocido. Usa --recon o --attack."
    exit 1
fi
