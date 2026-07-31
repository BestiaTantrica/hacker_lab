#!/bin/bash
# run_zone_pipeline.sh — Cascada de Pesca por Zona Horaria v2 (Go-Stack)
# ========================================================================
# Uso: ./run_zone_pipeline.sh [americas_1|emea_1|asia_1|...]
#
# Flujo ESTRICTO (cascada lineal, 5 eslabones, sin paralelismos):
#   1. mass_recon.py --zone ZONA      → SQLite (subfinder + crt.sh)
#   2. comparador.py --zone ZONA      → delta_{zona}_FECHA.json
#   3. dnsx + httpx                   → live_hosts_{zona}_FECHA.txt (filtro DNS/HTTP)
#   4. nuclei                         → nuclei_{zona}_FECHA.json (vulns reales)
#   5. parsear_nuclei.py              → sync C2 Panel + Telegram (solo si hay bugs reales)
#
# Si cualquier eslabón crítico falla, la cascada se detiene.
# Telegram SOLO se activa si nuclei encuentra vulnerabilidades confirmadas.

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
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [WARN] [$ZONA] Pipeline ya en ejecución (lockfile activo). Abortando para evitar colisión de RAM." | tee -a "$LOG"
    exit 0
}
# -----------------------------------------------------------------------------

log()   { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [INFO]  [$ZONA] $1" | tee -a "$LOG"; }
warn()  { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [WARN]  [$ZONA] $1" | tee -a "$LOG"; }
error() { echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [ERROR] [$ZONA] $1" | tee -a "$LOG"; exit 1; }

log "============================================================"
log "🌐 INICIANDO CASCADA v2 — ZONA: ${ZONA^^}"

# -- Eslabón 1: Descubrimiento Masivo (mass_recon.py → SQLite) ----------------
log "Eslabón 1/5: Descubrimiento masivo (mass_recon.py)"
$VENV "${BASE}/monitores/mass_recon.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error "❌ mass_recon.py falló. Cascada detenida."
log "✅ Eslabón 1 completado."

# -- Eslabón 2: Comparador de Deltas → delta JSON ------------------------------
log "Eslabón 2/5: Comparador de deltas (comparador.py)"
$VENV "${BASE}/monitores/comparador.py" --zone "$ZONA" >> "$LOG" 2>&1 \
    || error "❌ comparador.py falló. Cascada detenida."

# Verificar si existe delta con subdominios nuevos hoy
DELTA_FILE="${RESULTADO_DIR}/delta_${ZONA%%_*}_${FECHA}.json"
if [ ! -f "$DELTA_FILE" ]; then
    log "ℹ️  Sin subdominios nuevos en la zona ${ZONA} hoy. Cascada finalizada limpiamente."
    exit 0
fi
log "✅ Eslabón 2 completado: delta encontrado → ${DELTA_FILE}"

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
" > "$SUBS_RAW" 2>/dev/null || error "❌ No se pudo extraer subdominios del delta."

TOTAL_SUBS=$(wc -l < "$SUBS_RAW" | tr -d ' ')
if [ "$TOTAL_SUBS" -eq 0 ]; then
    log "ℹ️  El delta existe pero está vacío. Cascada finalizada."
    rm -f "$SUBS_RAW"
    exit 0
fi
log "📋 Subdominios extraídos del delta: ${TOTAL_SUBS}"

# -- Eslabón 3: Filtro DNS + HTTP Probing (dnsx | httpx) ----------------------
# Objetivo: Eliminar dominios muertos (NXDOMAIN) antes de escanear.
#           Esto reduce el ruido del 70% al ~0% en falsos positivos por timeout.
log "Eslabón 3/5: Filtro DNS y HTTP Probing (dnsx → httpx)"

LIVE_DNS="${RESULTADO_DIR}/live_dns_${ZONA}_${FECHA}.txt"
LIVE_HTTP="${RESULTADO_DIR}/live_http_${ZONA}_${FECHA}.txt"

# dnsx: Filtro DNS. Solo pasa subdominios con resolución IP real.
# -resp-only: solo los que resolvieron. -retry 2: evita falsos negativos.
# -t 150: 150 goroutines concurrentes (ajustado a la RAM de OCI-1).
dnsx \
    -list "$SUBS_RAW" \
    -resp-only \
    -retry 2 \
    -t 100 \
    -silent \
    -o "$LIVE_DNS" \
    >> "$LOG" 2>&1 || warn "⚠️  dnsx falló. Usando lista raw sin filtro DNS."

if [ ! -s "$LIVE_DNS" ]; then
    warn "⚠️  dnsx no resolvió ningún host vivo. Sin objetivos para escanear."
    rm -f "$SUBS_RAW" "$LIVE_DNS"
    exit 0
fi

TOTAL_DNS=$(wc -l < "$LIVE_DNS" | tr -d ' ')
log "🔍 Hosts resueltos por DNS: ${TOTAL_DNS} / ${TOTAL_SUBS}"

# httpx: Probing HTTP/S. Descarta hosts sin servicio web activo.
# -sc: status code. -title: título de la página (detección de takeovers).
# -cname: extrae el CNAME real (clave para takeover fingerprinting).
# -tech-detect: detecta tecnologías (filtra WordPress falso en empresas Go/K8s).
# -timeout 5: timeouts agresivos para no bloquear.
# -t 50: 50 goroutines HTTP concurrentes.
# -json: salida en JSON enriquecido para el C2 Panel.
HTTPX_JSON="${RESULTADO_DIR}/httpx_${ZONA}_${FECHA}.json"
httpx \
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
    >> "$LOG" 2>&1 || warn "⚠️  httpx tuvo errores parciales. Continuando con lo disponible."

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
    warn "⚠️  httpx no encontró ningún host con servicio HTTP activo."
    rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON"
    exit 0
fi

TOTAL_HTTP=$(wc -l < "$LIVE_HTTP" | tr -d ' ')
log "✅ Eslabón 3 completado: ${TOTAL_HTTP} hosts HTTP activos listos para escanear."

# -- Eslabón 4: Escaneo de Vulnerabilidades (nuclei) --------------------------
# Objetivo: Detectar vulnerabilidades reales con PoC determinista.
# Categorías seleccionadas para Bug Bounty de alto valor:
#   - takeovers/  → Subdomain Takeovers ($300-$3000)
#   - exposures/  → Secretos, .env, tokens ($100-$500)
#   - misconfiguration/ → CORS, headers mal configurados ($100-$300)
# Severidades: critical, high, medium (sin "low" ni "info" que generan ruido)
log "Eslabón 4/5: Escaneo de vulnerabilidades (nuclei)"

NUCLEI_JSON="${RESULTADO_DIR}/nuclei_${ZONA}_${FECHA}.json"

nuclei \
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
    >> "$LOG" 2>&1 || warn "⚠️  nuclei finalizó con errores parciales. Revisando resultados disponibles."

if [ ! -s "$NUCLEI_JSON" ]; then
    log "ℹ️  Nuclei no encontró vulnerabilidades reales en zona ${ZONA}. Cascada finalizada limpiamente."
    rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON" "$NUCLEI_JSON"
    exit 0
fi

TOTAL_BUGS=$(wc -l < "$NUCLEI_JSON" | tr -d ' ')
log "🚨 Nuclei encontró ${TOTAL_BUGS} hallazgo(s) verificado(s)."
log "✅ Eslabón 4 completado."

# -- Eslabón 5: Parsear + Sincronizar C2 Panel + Notificar Telegram ------------
log "Eslabón 5/5: Sincronizando con C2 Panel y notificando Telegram (parsear_nuclei.py)"
$VENV "${BASE}/monitores/parsear_nuclei.py" \
    --nuclei-json "$NUCLEI_JSON" \
    --zone "$ZONA" \
    >> "$LOG" 2>&1 || warn "⚠️  parsear_nuclei.py falló, pero el escaneo fue exitoso."

# -- Limpieza de archivos temporales de trabajo --------------------------------
# Se mantienen: NUCLEI_JSON (evidencia forense), DELTA_FILE (historial)
# Se eliminan: archivos temporales del proceso de filtrado
rm -f "$SUBS_RAW" "$LIVE_DNS" "$LIVE_HTTP" "$HTTPX_JSON"
log "🧹 Archivos temporales limpiados."

log "🏁 CASCADA v2 ZONA ${ZONA^^} COMPLETADA EXITOSAMENTE — ${TOTAL_BUGS} hallazgo(s) procesado(s)."
log "============================================================"
