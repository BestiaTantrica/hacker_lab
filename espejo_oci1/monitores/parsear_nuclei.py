#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parsear_nuclei.py — Conversor de hallazgos Nuclei → C2 Panel (OCI-2)
=====================================================================
Eslabón 5 del pipeline. Lee el JSON-Lines de salida de nuclei,
los convierte al formato de la API de OCI-2 (/api/ingest_delta),
sincroniza con el C2 Panel y notifica a Telegram solo si hay
hallazgos de valor real ($50+).

Uso: python3 parsear_nuclei.py --nuclei-json /ruta/nuclei.json --zone americas
"""

import argparse
import json
import os
import sys
import logging
from pathlib import Path

# ── Importar notificador del mismo directorio ─────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from notificador import sync_to_c2_panel, notificar_hallazgos_valor
except ImportError as e:
    print(f"[FATAL] No se pudo importar notificador.py: {e}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Mapeo de severidad nuclei → bounty estimado ───────────────────────────────
BOUNTY_MAP = {
    "critical": "$500-$3000",
    "high":     "$200-$1000",
    "medium":   "$100-$500",
    "low":      "$50-$100",
    "info":     "$0 (Informativo)",
}

# ── Templates de alta prioridad para notificación Telegram inmediata ──────────
HIGH_PRIORITY_TEMPLATES = {
    "takeovers",
    "aws-bucket-takeover",
    "s3-bucket-takeover",
    "github-pages-takeover",
    "heroku-takeover",
    "azure-takeover",
}


def parse_nuclei_jsonl(nuclei_json_path: str) -> list[dict]:
    """
    Lee el archivo JSONL de nuclei y devuelve una lista de hallazgos
    en el formato que espera la API de OCI-2 (/api/ingest_delta).

    Cada línea del JSONL de nuclei tiene la forma:
    {
      "template-id": "aws-bucket-takeover",
      "info": {"name": "AWS Bucket Takeover", "severity": "high", ...},
      "host": "sub.example.com",
      "matched-at": "https://sub.example.com",
      "curl-command": "curl -X GET ...",
      "matcher-name": "...",
      ...
    }
    """
    findings = []

    if not os.path.exists(nuclei_json_path):
        log.error("Archivo de nuclei no encontrado: %s", nuclei_json_path)
        return findings

    with open(nuclei_json_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                finding = json.loads(line)
            except json.JSONDecodeError as e:
                log.warning("Línea %d inválida: %s", line_num, e)
                continue

            template_id   = finding.get("template-id", "unknown")
            info          = finding.get("info", {})
            severity      = info.get("severity", "info").lower()
            name          = info.get("name", template_id)
            host          = finding.get("host", "")
            matched_at    = finding.get("matched-at", host)
            curl_command  = finding.get("curl-command", "")
            matcher_name  = finding.get("matcher-name", "")
            extracted_results = finding.get("extracted-results", [])

            # ── Guardrail 1: Filtrar informativos sin impacto ──────────────
            if severity == "info" and template_id not in HIGH_PRIORITY_TEMPLATES:
                log.debug("Saltando finding informativo: %s", template_id)
                continue

            # ── Guardrail 2: Verificar que hay evidencia concreta ──────────
            # Un hallazgo sin curl-command o sin matcher es sospechoso.
            has_evidence = bool(curl_command or matcher_name or extracted_results)
            if not has_evidence and severity not in ("critical", "high"):
                log.warning(
                    "Hallazgo '%s' sin evidencia concreta (curl/matcher). Omitido para evitar falso positivo.",
                    name
                )
                continue

            # ── Construir la evidencia forense estructurada ────────────────
            evidence = {
                "template_id":  template_id,
                "matched_at":   matched_at,
                "severity":     severity,
                "curl_command": curl_command,
                "matcher_name": matcher_name,
            }
            if extracted_results:
                evidence["extracted"] = extracted_results[:5]  # Cap a 5 items

            # Agregar datos extra si los hay (útil para exposures de tokens)
            for key in ("extracted-results", "response-time", "ip"):
                if finding.get(key):
                    evidence[key] = finding[key]

            # ── Mapear al formato del C2 Panel ────────────────────────────
            c2_finding = {
                "target":           matched_at or host,
                "vuln_type":        name,
                "severity":         severity.capitalize(),
                "estimated_bounty": BOUNTY_MAP.get(severity, "$50-$200"),
                "evidence":         json.dumps(evidence, ensure_ascii=False),
                "verified":         True,  # Nuclei lo verificó en vivo
            }

            findings.append(c2_finding)
            log.info(
                "✅ Hallazgo procesado: [%s] %s → %s",
                severity.upper(), name, matched_at
            )

    return findings


def main():
    parser = argparse.ArgumentParser(description="Parsear salida de Nuclei y sincronizar con C2 Panel")
    parser.add_argument("--nuclei-json", required=True, help="Ruta al archivo JSONL de salida de nuclei")
    parser.add_argument("--zone",        required=True, help="Zona geográfica (ej: americas, emea, asia)")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("Parseando hallazgos de Nuclei — Zona: %s", args.zone)
    log.info("Archivo de entrada: %s", args.nuclei_json)

    # ── Parsear el JSONL de Nuclei ────────────────────────────────────────
    findings = parse_nuclei_jsonl(args.nuclei_json)

    if not findings:
        log.info("Sin hallazgos de valor tras filtrado. No se sincroniza ni notifica. ✅")
        log.info("=" * 60)
        sys.exit(0)

    log.info("Total hallazgos válidos para sincronizar: %d", len(findings))

    # ── Sincronizar con C2 Panel (OCI-2) ─────────────────────────────────
    # El deltas_dict se deja vacío: los deltas ya los maneja comparador.py.
    # Solo enviamos los findings verificados por Nuclei.
    sync_ok = sync_to_c2_panel(
        zone=args.zone,
        deltas_dict={},
        findings=findings,
    )

    if sync_ok:
        log.info("✅ Hallazgos sincronizados exitosamente con C2 Panel (OCI-2).")
    else:
        log.warning("⚠️  Fallo de sincronización con C2 Panel. Posible offline de OCI-2.")

    # ── Notificar a Telegram solo los hallazgos de valor ($50+) ──────────
    findings_valiosos = [
        f for f in findings
        if f.get("severity", "").lower() not in ("info", "low")
    ]

    if findings_valiosos:
        log.info("📲 Notificando %d hallazgo(s) de valor a Telegram...", len(findings_valiosos))
        notificar_hallazgos_valor(findings_valiosos)
    else:
        log.info("Sin hallazgos de suficiente valor para notificar a Telegram.")

    log.info("=" * 60)
    log.info("Eslabón 5 finalizado correctamente.")


if __name__ == "__main__":
    main()
