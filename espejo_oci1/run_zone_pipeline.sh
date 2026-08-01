#!/bin/bash
# run_zone_pipeline.sh - Cascada de Pesca por Zona Horaria v2 (Go-Stack)
# ========================================================================
# Uso: ./run_zone_pipeline.sh [americas_1|emea_1|asia_1|...]
#
# Flujo ESTRICTO (cascada lineal, 6 eslabones, sin paralelismos):
#   1. mass_recon.py --zone ZONA      -> SQLite (subfinder + crt.sh)
#   2. comparador.py --zone ZONA      -> delta_{zona}_FECHA.json
#   3. dnsx + httpx                   -> live_hosts_{zona}_FECHA.txt (filtro DNS/HTTP)
#   4. nuclei                         -> nuclei_{zona}_FECHA.json (vulns reales)
#   5. parsear_nuclei.py              -> sync C2 Panel + Telegram (solo si hay bugs reales)
#   6. GC Dinamico & Heartbeat        -> Mantiene OCI-1 limpio e informa latido.
#
# Si cualquier eslabon critico falla, la cascada se detiene.
# Telegram SOLO se activa si nuclei encuentra vulnerabilidades confirmadas o Dead Man.

set -euo pipefail

ZONA="${1:-americas}"
BASE="/home/ubuntu/plataforma_operativa"
VENV="/home/ubuntu/workspace_lab/venv/bin/python3"
LOG="${BASE}/logs/pipeline_${ZONA}.log"
FECHA=$(date -u +%Y-%m-%d)
RESULTADO_DIR="${BASE}/resultados"

# -- Variables de entorno ------------------------------------------------------
# Cargar desde entorno.env sin usar 'source' (set -euo pipefail friendly)
if [ -f "${BASE}/config/entorno.env" ]; then
    while IFS='=' read -r key val; do
        key="${key%%#*}"
        key="${key// /}"
        val="${val// /}"
        val="${val//\"/}"
        val="${val//\'/}"
        [[ -z "$key" ]] && continue
        export "$key"="$val"
    done < <(grep -E '^[A-Z_]+=.+' "${BASE}/config/entorno.env" || true)
fi

C2_PANEL_URL="${C2_PANEL_URL:-http://localhost:8000}"

# -- ANTI-OVERLAP GUARD (flock) ------------------------------------------------
LOCKFILE="/tmp/pipeline_${ZONA}.lock"
exec 200>"$LOCKFILE"
flock -n 200 || {
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [WARN] [$ZONA] Pipeline ya en ejecucion (lockfile activo). Abortando para evitar colision de RAM." | tee -a "$LOG"
    exit 0
}
# -----------------------------------------------------------------------------

log()   { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [INFO]  [$ZONA] $1" | tee -a "$LOG"; }
warn()  { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [WARN]  [$ZONA] $1" | tee -a "$LOG"; }
error() { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [ERROR] [$ZONA] $1" | tee -a "$LOG"; exit 1; }

# -- TITLE-M1-A: Watchdog RAM & Circuit Breaker --------------------------------
# Previene OOM Killers catastroficos si dnsx/httpx/nuclei desbordan la memoria.
watchdog_ram() {
    while true; do
        for p in "dnsx" "httpx" "nuclei" "alterx" "katana"; do
            PID=$(pgrep -x "$p" | head -n 1)
            if [ -n "$PID" ]; then
                # Obtener Resident Set Size (memoria fisica usada en KB)
                RSS=$(ps -o rss= -p "$PID" 2>/dev/null | awk '{print $1}')
                if [ -n "$RSS" ] && [ "$RSS" -ge 768000 ]; then # 750MB = ~768000 KB
                    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [CRITICAL] Watchdog: Proceso $p (PID $PID) excedio 750MB RAM. Abortando proceso de forma segura." >> "$LOG"
                    kill -15 "$PID" 2>/dev/null || true
                    sleep 2
                    kill -9 "$PID" 2>/dev/null || true
                fi
            fi
        done
        sleep 5
    done
}
watchdog_ram &
WATCHDOG_PID=$!
trap "kill -9 $WATCHDOG_PID 2>/dev/null || true; rm -f $LOCKFILE" EXIT INT TERM

log "============================================================"
log " INICIANDO CASCADA v2 - ZONA: ${ZONA^^}"

# -- Eslabon 1: Descubrimiento Masivo (mass_recon.py -> SQLite) ----------------
log "Eslabon 1/5: Descubrimiento masivo (mass_recon.py)"
$VENV "${BASE}/monitores/mass_recon.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error " mass_recon.py fallo. Cascada detenida."
log " Eslabon 1 completado."

# -- Eslabon 2: Comparador de Deltas -> delta JSON ------------------------------
log "Eslabon 2/5: Comparador de deltas (comparador.py)"
$VENV "${BASE}/monitores/comparador.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error " comparador.py fallo. Cascada detenida."

# Verificar si existe delta con subdominios nuevos hoy
DELTA_FILE="${RESULTADO_DIR}/delta_${ZONA%%_*}_${FECHA}.json"
if [ ! -f "$DELTA_FILE" ]; then
    log "  Sin subdominios nuevos en la zona ${ZONA} hoy. Cascada finalizada limpiamente."
    exit 0
fi
log " Eslabon 2 completado: delta encontrado -> ${DELTA_FILE}"

# -- Extraer lista de subdominios del delta JSON -------------------------------
SUBS_RAW="${RESULTADO_DIR}/subs_raw_${ZONA}_${FECHA}.txt"
python3 -c "
import json, sys
with open('${DELTA_FILE}') as f:
    data = json.load(f)
activos = data.get('nuevos_activos', {})
subs = []
for domain_subs in activos.values():
    subs.extend(domain_subs)
print('\n'.join(sorted(set(subs))))
" > "$SUBS_RAW" 2>/dev/null || error " No se pudo extraer subdominios del delta."

TOTAL_SUBS=$(wc -l < "$SUBS_RAW" | tr -d ' ')
if [ "$TOTAL_SUBS" -eq 0 ]; then
    log "  El delta existe pero esta vacio. Cascada finalizada."
    rm -f "$SUBS_RAW"
    exit 0
fi
log " Subdominios extraidos del delta: ${TOTAL_SUBS}"

# -- Eslabon 3: Filtro DNS + HTTP Probing (dnsx | httpx) ----------------------
# Objetivo: Eliminar dominios muertos (NXDOMAIN) antes de escanear.
#           Esto reduce el ruido del 70% al ~0% en falsos positivos por timeout.
log "Eslabon 3/5: Filtro DNS y HTTP Probing (dnsx -> httpx)"

LIVE_DNS="${RESULTADO_DIR}/live_dns_${ZONA}_${FECHA}.txt"
LIVE_HTTP="${RESULTADO_DIR}/live_http_${ZONA}_${FECHA}.txt"

# dnsx: Filtro DNS con Alterx (Permutaciones dinamicas TITLE-M2-C).
# piping in-memory evita escritura masiva en disco. Watchdog controla memoria de dnsx/alterx.
timeout 2h bash -c "cat \"$SUBS_RAW\" | alterx -silent | dnsx -resp-only -retry 2 -t 100 -silent -o \"$LIVE_DNS\"" \
    >> "$LOG" 2>&1 || warn "  alterx/dnsx fallo o supero el timeout de 2h. Usando lista raw sin filtro DNS."

if [ ! -s "$LIVE_DNS" ]; then
    warn "  dnsx no resolvio ningun host vivo. Sin objetivos para escanear."
    rm -f "$SUBS_RAW" "$LIVE_DNS"
    exit 0
fi

TOTAL_DNS=$(wc -l < "$LIVE_DNS" | tr -d ' ')
log " Hosts resueltos por DNS: ${TOTAL_DNS} / ${TOTAL_SUBS}"

# httpx: Probing HTTP/S. Descarta hosts sin servicio web activo.
# -sc: status code. -title: titulo de la pagina (deteccion de takeovers).
# -cname: extrae el CNAME real (clave para takeover fingerprinting).
# -tech-detect: detecta tecnologias (filtra WordPress falso en empresas Go/K8s).
# -timeout 5: timeouts agresivos para no bloquear.
# -t 50: 50 goroutines HTTP concurrentes.
# -json: salida en JSON enriquecido para el C2 Panel.
HTTPX_JSON="${RESULTADO_DIR}/httpx_${ZONA}_${FECHA}.json"
timeout 2h httpx \
    -list "$LIVE_DNS" \
    -sc \
    -title \
    -cname \
    -tech-detect \
    -follow-redirects \
    -timeout 5 \
    -t 50 \
    -silent \
    -json \
    -o "$HTTPX_JSON" \
    >> "$LOG" 2>&1 || warn "  httpx tuvo errores parciales o supero timeout de 2h. Continuando con lo disponible."

# Generar la lista final de hosts vivos para nuclei (solo URLs)
if [ -s "$HTTPX_JSON" ]; then
    python3 -c "
import sys, json
with open('${HTTPX_JSON}') as f:
    for line in f:
        try:
            obj = json.loads(line.strip())
            url = obj.get('url') or obj.get('host', '')
            if url:
                print(url)
        except Exception:
            continue
" > "$LIVE_HTTP" 2>/dev/null
fi

if [ ! -s "$LIVE_HTTP" ]; then
    warn "  httpx no encontro ningun host con servicio HTTP activo."
    rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON"
    exit 0
fi

TOTAL_HTTP=$(wc -l < "$LIVE_HTTP" | tr -d ' ')
log " Eslabon 3 completado: ${TOTAL_HTTP} hosts HTTP activos listos para escanear."

# -- Eslabon 3.5: Katana Crawling & JS Extraction (TITLE-M2-A) ----------------
# Extraemos rutas y archivos JS dinamicos desde los hosts vivos.
log "Eslabon 3.5/5: Extraccion dinamica y JS Crawling (katana)"
KATANA_RAW="${RESULTADO_DIR}/katana_raw_${ZONA}_${FECHA}.txt"
KATANA_JS="${RESULTADO_DIR}/katana_js_${ZONA}_${FECHA}.txt"

# -depth 2 -js-crawl para escarbar en JS.
# Throttling OCI Free Tier: -c 5 -rate-limit 30
timeout 1h katana \
    -list "$LIVE_HTTP" \
    -depth 2 \
    -js-crawl \
    -jsluice \
    -c 5 \
    -rate-limit 30 \
    -silent \
    -o "$KATANA_RAW" \
    >> "$LOG" 2>&1 || warn " katana fallo o supero timeout de 1h."

if [ -f "$KATANA_RAW" ]; then
    grep -iE "\.js$" "$KATANA_RAW" | sort -u > "$KATANA_JS" || true
    TOTAL_JS=$(wc -l < "$KATANA_JS" 2>/dev/null | tr -d ' ')
    log " Rutas JS extraidas por Katana: ${TOTAL_JS:-0}"
else
    touch "$KATANA_JS"
fi

# -- Eslabon 4: Escaneo de Vulnerabilidades (nuclei + Passive JS Scanner) -----
# Objetivo: Detectar vulnerabilidades reales con PoC determinista.
# Categorias seleccionadas para Bug Bounty de alto valor:
#   - takeovers/  -> Subdomain Takeovers ($300-$3000)
#   - exposures/  -> Secretos, .env, tokens ($100-$500)
#   - misconfiguration/ -> CORS, headers mal configurados ($100-$300)
# Severidades: critical, high, medium (sin "low" ni "info" que generan ruido)
log "Eslabon 4/5: Escaneo de vulnerabilidades y secretos en JS (nuclei)"

NUCLEI_JSON="${RESULTADO_DIR}/nuclei_${ZONA}_${FECHA}.json"
NUCLEI_JS_JSON="${RESULTADO_DIR}/nuclei_js_${ZONA}_${FECHA}.json"

# Pasada base (takeovers, misconfigurations, exposures genericos) sobre hosts
timeout 2h nuclei \
    -list "$LIVE_HTTP" \
    -t /home/ubuntu/nuclei-templates/http/takeovers/ \
    -t /home/ubuntu/nuclei-templates/http/exposures/ \
    -t /home/ubuntu/nuclei-templates/http/misconfiguration/ \
    -severity critical,high,medium \
    -rate-limit 50 \
    -bulk-size 25 \
    -concurrency 10 \
    -timeout 8 \
    -no-httpx \
    -jsonl \
    -o "$NUCLEI_JSON" \
    -silent \
    >> "$LOG" 2>&1 || warn "  nuclei base finalizo con errores o supero timeout de 2h."

# Pasada focalizada (TITLE-M2-B) en busqueda de tokens/secretos sobre los .js extraidos
if [ -s "$KATANA_JS" ]; then
    log "Eslabon 4.5/5: Passive JS Secret Scanner (nuclei sobre .js)"
    timeout 1h nuclei \
        -list "$KATANA_JS" \
        -t /home/ubuntu/nuclei-templates/http/exposures/ \
        -severity critical,high,medium \
        -rate-limit 50 \
        -bulk-size 25 \
        -concurrency 10 \
        -timeout 8 \
        -jsonl \
        -o "$NUCLEI_JS_JSON" \
        -silent \
        >> "$LOG" 2>&1 || warn "  nuclei JS finalizo con errores o supero timeout de 1h."
        
    # Unificar hallazgos de JS con el JSON principal para C2
    if [ -s "$NUCLEI_JS_JSON" ]; then
        cat "$NUCLEI_JS_JSON" >> "$NUCLEI_JSON"
    fi
fi

if [ ! -s "$NUCLEI_JSON" ]; then
    log "  Nuclei no encontro vulnerabilidades reales en zona ${ZONA}. Continuando para enviar Deltas y Heartbeat."
    rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON"
    touch "$NUCLEI_JSON"
    TOTAL_BUGS=0
else
    TOTAL_BUGS=$(wc -l < "$NUCLEI_JSON" | tr -d ' ')
    log " Nuclei encontro ${TOTAL_BUGS} hallazgo(s) verificado(s)."
fi
log " Eslabon 4 completado."

# -- Eslabon 5: Parsear + Sincronizar C2 Panel + Notificar Telegram ------------
log "Eslabon 5/5: Sincronizando con C2 Panel y notificando Telegram (parsear_nuclei.py)"
$VENV "${BASE}/monitores/parsear_nuclei.py" \
    --nuclei-json "$NUCLEI_JSON" \
    --delta-json "$DELTA_FILE" \
    --zone "$ZONA" \
    >> "$LOG" 2>&1 || warn "  parsear_nuclei.py fallo, pero el escaneo fue exitoso."

# -- Limpieza de archivos temporales de trabajo --------------------------------
# Se mantienen: NUCLEI_JSON (evidencia forense), DELTA_FILE (historial)
# Se eliminan: archivos temporales del proceso de filtrado
rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON" "$KATANA_RAW" "$KATANA_JS" "$NUCLEI_JS_JSON"
log " Archivos temporales directos limpiados."

# -- Eslabon 6: Garbage Collection Dinamico y Heartbeat (M1-B & M1-C) -----------
log "Eslabon 6/6: GC Dinamico y Passive Heartbeat"

# 1. Capacity-Based Auto-Purge (M1-C)
DISK_USAGE=$(df /home/ubuntu | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -ge 85 ]; then
    warn " Uso de disco critico al ${DISK_USAGE}%. Iniciando Purga Dinamica..."
    
    # Loop de purga: de mas viejo a mas nuevo hasta bajar al 75%
    while [ "$DISK_USAGE" -ge 75 ]; do
        # Buscar el .json o .txt mas antiguo, excepto el de hoy (usando awk/sort si es necesario, o ls por orden de tiempo invertido)
        # Se asume formato seguro. No se falla el script si ocurre un error temporal.
        OLDEST=$(ls -1t "$RESULTADO_DIR"/*_*.json "$RESULTADO_DIR"/*_*.txt 2>/dev/null | tail -n 1)
        if [ -z "$OLDEST" ]; then break; fi # No hay mas archivos para borrar
        
        rm -f "$OLDEST"
        DISK_USAGE=$(df /home/ubuntu | tail -1 | awk '{print $5}' | sed 's/%//')
    done
    log " Purga finalizada. Uso de disco actual: ${DISK_USAGE}%"
fi

# Respaldo higienico pasivo (> 14 dias)
find "$RESULTADO_DIR" -type f -name "*_*.json" -mtime +14 -exec rm -f {} \; 2>/dev/null || true
find "$RESULTADO_DIR" -type f -name "*_*.txt" -mtime +14 -exec rm -f {} \; 2>/dev/null || true
find "${BASE}/logs" -type f -name "*.log" -mtime +14 -exec rm -f {} \; 2>/dev/null || true

# 2. Passive Heartbeat al C2 (M1-B)
curl -s -X POST "${C2_PANEL_URL}/api/heartbeat" \
     -d "{\"zone\": \"$ZONA\"}" \
     -H "Content-Type: application/json" >/dev/null 2>&1 || warn " Heartbeat no pudo contactar al C2."

log " CASCADA v2 ZONA ${ZONA^^} COMPLETADA EXITOSAMENTE - ${TOTAL_BUGS} hallazgo(s) procesado(s)."
log "============================================================"
