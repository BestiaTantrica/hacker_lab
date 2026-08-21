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

elif [ "$MODE" == "--attack" ] || [ "$MODE" == "--attack-auth" ]; then
    # --------------------------------------------------------------------------
    # FASE 4: ESCANEO DE VULNERABILIDADES (nuclei)
    # FRENO DE RED CRITICO (Modo Nocturno Protegido):
    # -c 15 (15 plantillas simultaneas)
    # -bs 10 (tamano de lote de 10 hosts)
    # -rl 50 (50 peticiones HTTP por segundo como maximo)
    # --------------------------------------------------------------------------

    # Comprobar si se proporcionó un archivo de autenticación
    AUTH_FLAGS=""
    SCAN_TARGET_FILE="$TARGET_FILE"

    if [ "$MODE" == "--attack-auth" ]; then
        AUTH_FILE="$3"
        if [ ! -f "$AUTH_FILE" ]; then
             echo "Error: Para usar --attack-auth debes proporcionar un archivo con headers como tercer argumento."
             exit 1
        fi
        echo "[MODO AUTENTICADO] Inyectando cabeceras desde $AUTH_FILE"
        AUTH_HEADERS=$(cat "$AUTH_FILE" | tr -d '\n')

        # FILTRO AUTOMATICO: extrae el dominio raiz del primer header Cookie/Host
        # e.g. si el archivo dice "tiendanube.com" en cualquier URL, filtra solo esos subdominios
        # Detecta el dominio raiz desde el nombre del archivo de auth (e.g. auth_tiendanube.txt -> tiendanube)
        AUTH_BASENAME=$(basename "$AUTH_FILE" | sed 's/auth_//' | sed 's/\.txt//')
        FILTERED_TARGET="$RESULT_DIR/targets_auth_filtered_$FECHA.txt"
        grep -i "$AUTH_BASENAME" "$TARGET_FILE" > "$FILTERED_TARGET" || true
        FILTERED_COUNT=$(wc -l < "$FILTERED_TARGET")
        TOTAL_COUNT=$(wc -l < "$TARGET_FILE")
        echo "[FILTRO ACTIVO] Dominio: $AUTH_BASENAME | Targets: $FILTERED_COUNT de $TOTAL_COUNT totales"
        if [ "$FILTERED_COUNT" -eq 0 ]; then
            echo "Advertencia: No se encontraron URLs de $AUTH_BASENAME en el archivo de targets. Usando todos."
            SCAN_TARGET_FILE="$TARGET_FILE"
        else
            SCAN_TARGET_FILE="$FILTERED_TARGET"
        fi
    fi

    # Archivo de salida incremental (JSONL = una linea por finding, se escribe en tiempo real)
    OUTPUT_FILE="$RESULT_DIR/4_vulnerabilidades_${AUTH_BASENAME:-all}_$FECHA.jsonl"
    RESUME_FILE="$RESULT_DIR/nuclei_resume_${AUTH_BASENAME:-all}.cfg"
    echo "[Fase 4] Iniciando Nuclei... salida INCREMENTAL en: $OUTPUT_FILE"
    echo "[RESUME] Si se interrumpe, retomará desde: $RESUME_FILE"

    # Nuclei escribe CADA FINDING inmediatamente al archivo (modo streaming)
    # -me (markdown-export) NO se usa; -jsonl con -o escribe linea a linea al archivo
    $TOOLS_DIR/nuclei -l "$SCAN_TARGET_FILE" \
        -t cves/ -t exposed-panels/ -t misconfiguration/ -t vulnerabilities/ \
        -c 15 -bs 10 -rl 50 -timeout 10 \
        -jsonl -o "$OUTPUT_FILE" \
        -resume "$RESUME_FILE" \
        ${AUTH_HEADERS:+-H "$AUTH_HEADERS"}

    echo "========================================================================"
    echo "✅ ASALTO DE VULNERABILIDADES TERMINADO"
    echo "📂 Revisa tus resultados en: $RESULT_DIR/4_vulnerabilidades_$FECHA.json"
    
    echo "[Fase 5] Sincronizando con C2 Panel..."
    if [ -f "$OUTPUT_FILE" ]; then
        python3 /home/tomas2/WORKSPACE/LAB/espejo_oci1/monitores/parsear_nuclei.py --nuclei-json "$OUTPUT_FILE" --zone local
    else
        echo "Sin resultados para sincronizar (archivo vacio o no generado)."
    fi

    echo "⏳ [Fase 6] Cold Storage: Respaldando c2_db.sqlite desde OCI-2..."
    BACKUP_DIR="/home/tomas2/historial_profundo/backups_db"
    mkdir -p "$BACKUP_DIR"
    # Se ignora la comprobacion estricta de host key para ejecucion fluida
    scp -o StrictHostKeyChecking=no -i /home/tomas2/WORKSPACE/LAB/llave_oci ubuntu@143.47.115.34:/home/ubuntu/c2_panel/c2_db.sqlite "$BACKUP_DIR/c2_db_$FECHA.sqlite" 2>/dev/null || echo "⚠️ Advertencia: No se pudo conectar a OCI-2 para el respaldo."
    if [ -f "$BACKUP_DIR/c2_db_$FECHA.sqlite" ]; then
        echo "✅ Respaldo (Cold Storage) exitoso en: $BACKUP_DIR/c2_db_$FECHA.sqlite"
    fi
    echo "========================================================================"
else
    echo "❌ Error: Modo no reconocido. Usa --recon o --attack."
    exit 1
fi
