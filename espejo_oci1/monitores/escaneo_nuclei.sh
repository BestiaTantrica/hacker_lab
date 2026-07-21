#!/bin/bash
NUEVOS_ACTIVOS="resultados/nuevos_activos.txt"
RESULTADOS_NUCLEI="resultados/nuclei_$(date +%F).json"

if [ -s "$NUEVOS_ACTIVOS" ]; then
    echo "[*] Ejecutando Nuclei contra nuevos activos..."
    nuclei -l "$NUEVOS_ACTIVOS" -t cves/ -t exposures/ -t vulnerabilities/ -t misconfiguration/ -s critical,high,medium -silent -json-export "$RESULTADOS_NUCLEI"
    
    # Si encontró algo, mandamos la alerta a Telegram
    if [ -s "$RESULTADOS_NUCLEI" ]; then
        HALLAZGOS=$(jq -r '. | "🚨 [" + .info.severity + "] " + .info.name + "\nURL: " + .host' "$RESULTADOS_NUCLEI" | head -n 10)
        python3 monitores/../api/notificador.py "🔥 *Nuevas Vulnerabilidades (Nuclei)* 🔥
$HALLAZGOS
(Mostrando primeros resultados, revisa OCI-1)"
    fi
else
    echo "[*] No hay activos nuevos hoy para escanear con Nuclei."
fi
