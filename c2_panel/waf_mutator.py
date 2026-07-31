#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
waf_mutator.py -- M3-C: Smart WAF Bypass & Header Mutator
==========================================================
Rotacion deterministica de headers HTTP para evadir bloqueos
403/406 en sondas de verificacion forense.

Sin dependencias externas. Solo stdlib.
Uso: from waf_mutator import rotate_headers, build_triager_curl, sanitize_nuclei_curl
"""

import shlex

# ----------------------------------------------------------------------------
# POOL DE USER-AGENTS REALES (browsers modernos verificados)
# Seleccion deterministica por indice (attempt % len) -- reproducible
# ----------------------------------------------------------------------------
UA_POOL = [
    # attempt=1 -> Chrome 124 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # attempt=2 -> Firefox 125 Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # attempt=3 -> Safari 17 macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    # attempt=4 -> Edge 124 Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # attempt=5 -> Chrome Mobile Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
]

# IPs del rango 104.x (Cloudflare CDN range) usadas en X-Forwarded-For.
# Objetivo: simular un request que viene de detras de un reverse proxy CDN.
# NO falsifica la IP real de OCI-1 (eso es inmutable a nivel socket).
# Algunos WAFs enterprise priorizan este header para rate-limiting.
_XFF_POOL = [
    "104.20.32.14",  "104.20.35.100", "104.18.200.1",
    "104.16.160.1",  "104.17.80.5",   "104.21.64.1",
    "104.22.10.20",  "104.26.8.15",   "172.67.128.1",
    "172.67.200.50",
]

# Headers internos del pipeline que NO deben aparecer en el PoC del triager
_INTERNAL_HEADERS = frozenset({"X-Bug-Bounty", "X-Real-IP", "X-Originating-IP"})

# Flags de Nuclei que no son validos/legibles en un PoC para triager H1
_NUCLEI_FLAGS_TO_REMOVE = frozenset({
    "--proxy", "-k", "-silent", "--silent", "-nc", "--no-color",
    "-j", "--jsonl", "-debug", "--debug", "-v", "--verbose",
    "-timeout", "-rate-limit", "--rate-limit",
})


def rotate_headers(attempt: int = 1) -> dict:
    """
    Devuelve headers HTTP con seleccion deterministica segun 'attempt'.
    Deterministico = misma entrada siempre produce el mismo resultado.
    Esto garantiza reproducibilidad forense (auditable).

    attempt=1 -> headers conservadores (alta compatibilidad WAF basico)
    attempt=2 -> headers con X-Forwarded-For (evasion rate-limit por IP)
    attempt=3 -> headers minimalistas (anti-bot-detection agresivo)
    """
    idx = (attempt - 1) % len(UA_POOL)
    ua = UA_POOL[idx]

    base = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Bug-Bounty": "HackerOne-tomas244",
    }

    if attempt >= 2:
        xff_idx = (attempt * 7) % len(_XFF_POOL)
        xff_ip = _XFF_POOL[xff_idx]
        base["X-Forwarded-For"] = xff_ip
        base["X-Real-IP"] = xff_ip
        base["X-Originating-IP"] = xff_ip

    if attempt >= 3:
        ua_min = UA_POOL[(attempt - 1) % len(UA_POOL)]
        xff_min = _XFF_POOL[(attempt * 3) % len(_XFF_POOL)]
        return {
            "User-Agent": ua_min,
            "Accept": "*/*",
            "X-Forwarded-For": xff_min,
            "X-Bug-Bounty": "HackerOne-tomas244",
        }

    return base


def build_triager_curl(url: str, headers: dict, method: str = "GET", body: str = "") -> str:
    """
    Genera el comando curl exacto con los headers usados.
    Listo para copiar en el reporte HackerOne sin modificacion.
    Omite headers internos del pipeline (X-Bug-Bounty, X-Real-IP, etc).
    Salida: una sola linea ejecutable.
    """
    parts = ["curl", "-s", "-i", "--max-time", "10", "--connect-timeout", "5"]

    if method.upper() != "GET":
        parts.extend(["-X", method.upper()])

    for k, v in headers.items():
        if k not in _INTERNAL_HEADERS:
            parts.extend(["-H", "{}: {}".format(k, v)])

    if body:
        parts.extend(["-d", body])

    parts.append(url)
    return " ".join(shlex.quote(p) for p in parts)


def sanitize_nuclei_curl(raw_curl: str) -> str:
    """
    Limpia el curl-command crudo de Nuclei:
    - Elimina flags internos (-k, --silent, --proxy, etc)
    - Agrega --max-time y --connect-timeout si faltan
    - Sustituye UA de pipeline por UA de browser real
    - Retorna comando de una sola linea para PoC del triager
    """
    if not raw_curl:
        return ""

    try:
        tokens = shlex.split(raw_curl)
    except ValueError:
        return raw_curl.replace("\\\n", " ").strip()

    cleaned = []
    skip_next = False
    has_max_time = False
    has_connect_timeout = False

    for i, tok in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        tok_base = tok.split("=")[0]
        if tok_base in _NUCLEI_FLAGS_TO_REMOVE:
            # Si el flag usa valor separado, saltar el siguiente token tambien
            if "=" not in tok and i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                skip_next = True
            continue

        if tok in ("--max-time", "-m"):
            has_max_time = True
        if tok == "--connect-timeout":
            has_connect_timeout = True

        cleaned.append(tok)

    if not has_max_time:
        cleaned.insert(1, "--max-time")
        cleaned.insert(2, "10")
    if not has_connect_timeout:
        cleaned.insert(1, "--connect-timeout")
        cleaned.insert(2, "5")

    result = " ".join(cleaned)

    # Sustituir UA interno del pipeline por Firefox real
    result = result.replace(
        "HackerOne-tomas244",
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
    )
    return result


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== waf_mutator.py -- Self Test ===\n")
    for a in [1, 2, 3]:
        h = rotate_headers(a)
        ua_short = h["User-Agent"][:60]
        xff = h.get("X-Forwarded-For", "(none)")
        print("Attempt {}: UA={}... XFF={}".format(a, ua_short, xff))

    print("\n=== Triager Curl (attempt=2) ===")
    h2 = rotate_headers(2)
    print(build_triager_curl("https://api.target.com/v1/users", h2))

    print("\n=== Nuclei Curl Sanitizer ===")
    raw = 'curl -s -k --no-color --silent -timeout 5 -H "Host: test.com" https://test.com/api'
    print(sanitize_nuclei_curl(raw))
