#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
poc_generator.py -- M3-A: Active Proof-of-Concept Generator
=============================================================
Eslabon 5.5 del pipeline OCI-1.
Toma la evidencia cruda de Nuclei y produce:
  - triager_poc: curl limpio copiable para el reporte H1
  - poc_quality: HIGH / MEDIUM / UNVERIFIABLE

Sin dependencias externas. Solo stdlib.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from waf_mutator import sanitize_nuclei_curl
except ImportError:
    def sanitize_nuclei_curl(c):
        return c

# Calidades forenses posibles
QUALITY_HIGH = "HIGH"
QUALITY_MEDIUM = "MEDIUM"
QUALITY_UNVERIFIABLE = "UNVERIFIABLE"

# Templates de PoC por categoria de vulnerabilidad
_POC_TEMPLATES = {
    "subdomain_takeover": (
        "# Step 1: Confirm orphaned CNAME\n"
        "dig CNAME {host}\n\n"
        "# Step 2: Confirm unclaimed resource\n"
        "curl -s -i --max-time 10 --connect-timeout 5 \\\n"
        '  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \\\n'
        '  -H "Accept: text/html,application/xhtml+xml,*/*;q=0.8" \\\n'
        "  https://{host}"
    ),
    "cors": (
        "# CORS Misconfiguration PoC\n"
        "curl -s -i --max-time 10 --connect-timeout 5 \\\n"
        '  -H "Origin: https://evil.com" \\\n'
        '  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \\\n'
        '  -H "Accept: */*" \\\n'
        "  {url}\n\n"
        "# Vulnerable response shows:\n"
        "# Access-Control-Allow-Origin: https://evil.com\n"
        "# Access-Control-Allow-Credentials: true"
    ),
    "exposed_file": (
        "# Exposed Sensitive File PoC\n"
        "curl -s -o /dev/null -w '%{{http_code}} %{{size_download}} bytes\\n' \\\n"
        "  --max-time 10 --connect-timeout 5 \\\n"
        '  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \\\n'
        "  {url}\n\n"
        "# Then retrieve the content:\n"
        "curl -s --max-time 10 {url} | head -c 500"
    ),
    "secret_exposure": (
        "# Secret/Token Exposure in JS PoC\n"
        "curl -s --max-time 10 --connect-timeout 5 \\\n"
        '  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \\\n'
        "  {url} | grep -oP '(sk_live|AKIA|xox[baprs]|ghp_|AIza)[0-9a-zA-Z\\-_]+'"
    ),
    "s3_bucket": (
        "# S3 Bucket Misconfiguration PoC\n"
        "curl -s -i --max-time 10 --connect-timeout 5 {url}\n\n"
        "# Check for ListBucketResult (public listing) or NoSuchBucket (takeover available)"
    ),
    "default": (
        "curl -s -i --max-time 10 --connect-timeout 5 \\\n"
        '  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0" \\\n'
        '  -H "Accept: */*" \\\n'
        "  {url}"
    ),
}


def _detect_category(vuln_type: str, template_id: str = "") -> str:
    """Infiere la categoria de vulnerabilidad para seleccionar el template de PoC."""
    combined = (vuln_type + " " + template_id).lower()
    if any(k in combined for k in ["takeover", "subdomain", "cname", "orphan"]):
        return "subdomain_takeover"
    if any(k in combined for k in ["cors", "cross-origin", "access-control"]):
        return "cors"
    if any(k in combined for k in ["env", ".git", "backup", "config", "swagger", "openapi", "exposed", "disclosure", "secret"]):
        return "exposed_file"
    if any(k in combined for k in ["token", "api_key", "apikey", "stripe", "aws_key", "twilio", "slack_token"]):
        return "secret_exposure"
    if any(k in combined for k in ["s3", "bucket", "nosuchbucket"]):
        return "s3_bucket"
    return "default"


def sanitize_poc(evidence: dict) -> dict:
    """
    Enriquece el dict de evidencia con:
    - triager_poc: comando curl limpio para copiar en el reporte H1
    - poc_quality: HIGH / MEDIUM / UNVERIFIABLE

    Modifica el dict in-place. Compatible con el formato de parsear_nuclei.py.
    """
    raw_curl    = evidence.get("curl_command", "")
    matched_at  = evidence.get("matched_at", evidence.get("matched-at", ""))
    host        = evidence.get("host", matched_at)
    vuln_type   = evidence.get("vuln_type", "")
    template_id = evidence.get("template_id", "")
    extracted   = evidence.get("extracted", [])
    matcher     = evidence.get("matcher_name", "")

    target_url = matched_at or host or ""
    category = _detect_category(vuln_type, template_id)

    # --- Generar PoC ---
    if raw_curl:
        triager_poc = sanitize_nuclei_curl(raw_curl)
        poc_source = "nuclei_curl"
    else:
        template_str = _POC_TEMPLATES.get(category, _POC_TEMPLATES["default"])
        host_clean = host.replace("https://", "").replace("http://", "").rstrip("/")
        triager_poc = template_str.format(host=host_clean, url=target_url)
        poc_source = "generated_template"

    # --- Evaluar calidad ---
    has_curl      = bool(raw_curl and len(raw_curl) > 20)
    has_extracted = bool(extracted)
    has_matcher   = bool(matcher and matcher not in ("", "unknown", "none"))
    has_url       = bool(target_url and target_url.startswith("http"))

    if has_curl and (has_extracted or has_matcher):
        quality = QUALITY_HIGH
    elif has_curl or (has_url and has_matcher):
        quality = QUALITY_MEDIUM
    elif has_url:
        quality = QUALITY_MEDIUM
    else:
        quality = QUALITY_UNVERIFIABLE

    evidence["triager_poc"]  = triager_poc
    evidence["poc_quality"]  = quality
    evidence["poc_source"]   = poc_source
    return evidence


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== poc_generator.py -- Self Test ===\n")

    ev1 = {
        "template_id": "github-pages-takeover",
        "vuln_type": "GitHub Pages Takeover",
        "matched_at": "https://blog.target.com",
        "host": "blog.target.com",
        "curl_command": 'curl -s -k --no-color --silent -H "Host: blog.target.com" https://blog.target.com',
        "matcher_name": "There isn't a GitHub Pages site here",
        "extracted": [],
    }
    r1 = sanitize_poc(ev1)
    print("[Test 1] Quality: {} | Source: {}".format(r1["poc_quality"], r1["poc_source"]))
    print("PoC:\n{}\n".format(r1["triager_poc"]))

    ev2 = {
        "template_id": "cors-misconfig",
        "vuln_type": "CORS Misconfiguration",
        "matched_at": "https://api.target.com/v2/users",
        "host": "api.target.com",
        "curl_command": "",
        "matcher_name": "cors-reflect",
        "extracted": [],
    }
    r2 = sanitize_poc(ev2)
    print("[Test 2] Quality: {} | Source: {}".format(r2["poc_quality"], r2["poc_source"]))
    print("PoC:\n{}".format(r2["triager_poc"]))
