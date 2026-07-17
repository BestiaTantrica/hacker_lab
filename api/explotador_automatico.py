#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
explotador_automatico.py — Bug Hunter Automático sobre delta OCI
================================================================
Corre DESPUÉS del pipeline de descubrimiento nocturno.
Lee el delta de subdominios nuevos y busca bugs reales:
  1. Subdomain Takeover (pago alto: $300-$3000)
  2. CORS misconfiguration con credenciales (pago medio: $200-$500)
  3. Archivos sensibles expuestos (.env, backups, configs) (pago bajo-medio: $100-$300)
  4. Endpoints de admin abiertos sin auth

Notifica a Telegram SOLO cuando encuentra algo explotable.
Se puede integrar en run_pipeline.sh de OCI.

Uso local:  python3 explotador_automatico.py
Uso OCI:    python3 explotador_automatico.py --delta /ruta/delta.json
"""

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
# Telegram — mismo bot que usa el pipeline OCI
# Leer de env vars o del archivo de config del pipeline
TELEGRAM_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN",
    "8986579944:AAGIXxsLkitZ99J53yNa88-WxMnXQFc9Fd4"
)
TELEGRAM_CHAT_ID = os.environ.get(
    "TELEGRAM_CHAT_ID",
    "6527908321"
)

# Rutas del pipeline OCI (o local)
DELTA_DIR_OCI   = "/home/ubuntu/plataforma_operativa/resultados/"
DELTA_DIR_LOCAL = str(Path(__file__).parent.parent / "resultados")

# Request settings
TIMEOUT = 8
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
}
MAX_SUBDOMINIOS = 500  # Límite por ejecución para no exceder rate limits

# ─────────────────────────────────────────────────────────────────────────────
# FINGERPRINTS DE SUBDOMAIN TAKEOVER
# Fuente: https://github.com/EdOverflow/can-i-take-over-xyz
# ─────────────────────────────────────────────────────────────────────────────
TAKEOVER_FINGERPRINTS = [
    # (servicio, texto_en_respuesta, status_codes_vulnerables)
    ("GitHub Pages",    "There isn't a GitHub Pages site here",   [404]),
    ("GitHub Pages",    "For root URLs (like http://example.com/) you must provide an index",  [404]),
    ("Heroku",          "No such app",                             [404]),
    ("Heroku",          "herokucdn.com/error-pages/no-such-app",   [404]),
    ("AWS S3",          "NoSuchBucket",                            [404, 403]),
    ("AWS S3",          "The specified bucket does not exist",     [404]),
    ("Azure",           "404 Web Site not Found",                  [404]),
    ("Azure",           "This Azure site is temporarily unavailable", [404]),
    ("Shopify",         "Sorry, this shop is currently unavailable", [404]),
    ("Fastly",          "Fastly error: unknown domain",            [404]),
    ("Surge.sh",        "project not found",                       [404]),
    ("Wordpress.com",   "Do you want to register",                 [404]),
    ("Tumblr",          "There's nothing here.",                   [404]),
    ("Ghost",           "The thing you were looking for is no longer here", [404]),
    ("Zendesk",         "Help Center Closed",                      [404]),
    ("Zendesk",         "This help center no longer exists",       [404]),
    ("Freshdesk",       "There is no helpdesk with the URL",       [404]),
    ("Unbounce",        "The requested URL was not found on this server", [404]),
    ("Pantheon",        "The gods are wise",                       [404]),
    ("Readme.io",       "Project doesnt exist",                    [404]),
    ("Intercom",        "This page is reserved for artistic dog photos", [404]),
    ("JetBrains",       "is not a registered IntelliJ Platform IDE", [404]),
    ("Pingdom",         "Sorry, couldn't find the status page",   [404]),
    ("Statuspage.io",   "page not found",                          [404]),
    ("UserVoice",       "This UserVoice subdomain is currently available", [404]),
    ("HubSpot",         "This page isn't available",               [404]),
    ("Campaign Monitor","Double check the URL",                    [404]),
    ("Mailchimp",       "isn't a Mailchimp list",                  [404]),
]

# Rutas de archivos sensibles a probar
EXPOSED_PATHS = [
    "/.env",
    "/.env.local",
    "/.env.production",
    "/.env.backup",
    "/config.json",
    "/config.yml",
    "/config.yaml",
    "/secrets.json",
    "/wp-config.php",
    "/wp-config.php.bak",
    "/.git/config",
    "/.git/HEAD",
    "/backup.zip",
    "/backup.sql",
    "/db.sql",
    "/database.sql",
    "/dump.sql",
    "/phpinfo.php",
    "/info.php",
    "/test.php",
    "/admin",
    "/admin/",
    "/administrator",
    "/api/v1/users",
    "/api/v2/users",
    "/api/users",
    "/swagger.json",
    "/swagger-ui.html",
    "/openapi.json",
    "/api-docs",
    "/.DS_Store",
    "/robots.txt",
    "/sitemap.xml",
    "/.well-known/security.txt",
    "/server-status",
    "/server-info",
    "/.htpasswd",
    "/.htaccess",
]

# Palabras clave que indican exposición real en archivos
SENSITIVE_KEYWORDS = [
    "password", "passwd", "secret", "api_key", "apikey", "token",
    "database", "db_pass", "mysql", "postgres", "mongodb",
    "aws_access", "aws_secret", "S3_BUCKET", "STRIPE_KEY",
    "private_key", "BEGIN RSA", "BEGIN EC", "BEGIN PGP",
]


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def telegram(msg):
    """Enviar alerta a Telegram. Solo se llama cuando hay un bug real."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log(f"[TELEGRAM] (sin config) {msg[:80]}")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        log(f"[TELEGRAM ERROR] {e}")


def get_cname(dominio):
    """Obtener CNAME de un dominio vía dig."""
    try:
        result = subprocess.run(
            ["dig", "+short", "CNAME", dominio],
            capture_output=True, text=True, timeout=5
        )
        cname = result.stdout.strip()
        return cname if cname else None
    except Exception:
        return None


def http_probe(url, extra_headers=None, allow_redirects=True):
    """Hacer GET y devolver (status, headers, body[:2000], url_final)."""
    h = {**HEADERS, **(extra_headers or {})}
    try:
        r = requests.get(url, headers=h, timeout=TIMEOUT,
                         verify=False, allow_redirects=allow_redirects)
        return r.status_code, dict(r.headers), r.text[:3000], r.url
    except requests.exceptions.ConnectionError:
        return None, {}, "", url
    except requests.exceptions.Timeout:
        return None, {}, "", url
    except Exception:
        return None, {}, "", url


def cargar_delta(path=None):
    """Carga el delta más reciente del pipeline OCI."""
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    # Buscar el delta más reciente automáticamente
    for base in [DELTA_DIR_OCI, DELTA_DIR_LOCAL]:
        if not os.path.isdir(base):
            continue
        archivos = sorted(
            [f for f in os.listdir(base) if f.startswith("delta_") and f.endswith(".json")],
            reverse=True
        )
        if archivos:
            ruta = os.path.join(base, archivos[0])
            log(f"Cargando delta: {ruta}")
            with open(ruta) as f:
                return json.load(f)

    log("⚠️  No se encontró ningún archivo delta. Especificá --delta /ruta/archivo.json")
    return {}


def extraer_subdominios(delta):
    """Extrae la lista de subdominios del delta (acepta múltiples formatos)."""
    # Formato 1: {"nuevos_activos": ["sub1.domain.com", ...]}
    if "nuevos_activos" in delta:
        return delta["nuevos_activos"]
    # Formato 2: lista directa
    if isinstance(delta, list):
        return delta
    # Formato 3: cualquier lista en el primer nivel
    for key, val in delta.items():
        if isinstance(val, list) and val:
            return val
    return []


# ─────────────────────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────────────────────
def test_subdomain_takeover(subdominio):
    """
    Test 1: Subdomain Takeover
    Detecta si el subdominio tiene un CNAME apuntando a un servicio externo
    que ya no está reclamado → podemos registrarlo y tomar control.
    Pago típico: $300 - $3000 en H1.
    """
    hallazgos = []

    # Prueba HTTPS y HTTP
    for scheme in ["https", "http"]:
        url = f"{scheme}://{subdominio}"
        status, headers, body, _ = http_probe(url)
        if status is None:
            continue

        for servicio, fingerprint, statuses_malos in TAKEOVER_FINGERPRINTS:
            if status in statuses_malos and fingerprint.lower() in body.lower():
                # Confirmar con CNAME
                cname = get_cname(subdominio)
                msg = (
                    f"🚨 SUBDOMAIN TAKEOVER\n"
                    f"Subdominio: {subdominio}\n"
                    f"Servicio vulnerable: {servicio}\n"
                    f"CNAME: {cname or 'N/A'}\n"
                    f"HTTP Status: {status}\n"
                    f"Fingerprint: '{fingerprint}'\n"
                    f"URL: {url}\n"
                    f"Severidad: ALTA ($300-$3000)\n"
                    f"Acción: registrar el recurso externo para tomar control"
                )
                log(msg)
                telegram(msg)
                hallazgos.append({
                    "tipo": "subdomain_takeover",
                    "subdominio": subdominio,
                    "servicio": servicio,
                    "cname": cname,
                    "status": status,
                    "url": url,
                })
                return hallazgos  # Un takeover por subdominio es suficiente

    return hallazgos


def test_cors(subdominio):
    """
    Test 2: CORS misconfiguration
    Busca endpoints que reflejen el Origin del atacante + Allow-Credentials: true
    → permite robar datos del usuario autenticado via JS cross-origin.
    Pago típico: $200 - $500.
    """
    hallazgos = []
    EVIL_ORIGIN = "https://evil.tomas244.com"

    endpoints_a_probar = [
        "/api/v2/tickets",
        "/api/v2/contacts",
        "/api/v2/users",
        "/api/v1/users",
        "/api/",
        "/api",
        "/graphql",
        "/v1/",
        "/v2/",
    ]

    for scheme in ["https"]:
        for ep in endpoints_a_probar:
            url = f"{scheme}://{subdominio}{ep}"
            status, headers, body, _ = http_probe(
                url,
                extra_headers={"Origin": EVIL_ORIGIN}
            )
            if status is None:
                break  # Subdominio no responde, saltar

            acao = headers.get("Access-Control-Allow-Origin", "")
            acac = headers.get("Access-Control-Allow-Credentials", "").lower()

            # Vulnerable: refleja el origin del atacante Y permite credenciales
            if acao == EVIL_ORIGIN and acac == "true":
                msg = (
                    f"🚨 CORS MISCONFIGURATION\n"
                    f"URL: {url}\n"
                    f"ACAO: {acao}\n"
                    f"ACAC: {acac}\n"
                    f"HTTP Status: {status}\n"
                    f"Severidad: MEDIA-ALTA ($200-$500)\n"
                    f"Impacto: JS cross-origin puede leer respuestas autenticadas"
                )
                log(msg)
                telegram(msg)
                hallazgos.append({
                    "tipo": "cors",
                    "url": url,
                    "acao": acao,
                    "acac": acac,
                })

    return hallazgos


def test_exposed_files(subdominio):
    """
    Test 3: Archivos sensibles expuestos
    Busca rutas comunes con información sensible: .env, configs, backups, etc.
    Pago típico: $100 - $300.
    """
    hallazgos = []

    for path in EXPOSED_PATHS:
        url = f"https://{subdominio}{path}"
        status, headers, body, _ = http_probe(url, allow_redirects=False)

        if status is None:
            break  # Subdominio no responde

        # Solo analizar respuestas 200 con contenido sustancial
        if status == 200 and len(body) > 20:
            body_lower = body.lower()

            # Verificar que realmente contiene info sensible
            palabras_encontradas = [
                kw for kw in SENSITIVE_KEYWORDS
                if kw.lower() in body_lower
            ]

            if palabras_encontradas:
                msg = (
                    f"🚨 ARCHIVO SENSIBLE EXPUESTO\n"
                    f"URL: {url}\n"
                    f"Status: {status}\n"
                    f"Palabras clave: {', '.join(palabras_encontradas[:5])}\n"
                    f"Preview: {body[:200]}\n"
                    f"Severidad: MEDIA ($100-$300)"
                )
                log(msg)
                telegram(msg)
                hallazgos.append({
                    "tipo": "exposed_file",
                    "url": url,
                    "keywords": palabras_encontradas,
                    "preview": body[:200],
                })
            elif path in ["/.git/HEAD", "/.git/config"]:
                # .git expuesto sin keywords también es válido
                if "ref:" in body or "[core]" in body:
                    msg = (
                        f"🚨 REPOSITORIO GIT EXPUESTO\n"
                        f"URL: {url}\n"
                        f"Contenido: {body[:100]}\n"
                        f"Severidad: ALTA — puede contener secrets del código"
                    )
                    log(msg)
                    telegram(msg)
                    hallazgos.append({
                        "tipo": "git_exposed",
                        "url": url,
                        "body": body[:200],
                    })

        time.sleep(0.1)  # Evitar rate limiting

    return hallazgos


def test_open_redirect(subdominio):
    """
    Test 4: Open Redirect
    Parámetros de redirección que pueden ser abusados para phishing.
    Pago típico: $50 - $200 (depende del programa).
    """
    hallazgos = []
    payloads = [
        "/?redirect=https://evil.com",
        "/?url=https://evil.com",
        "/?next=https://evil.com",
        "/?return=https://evil.com",
        "/?goto=https://evil.com",
        "/login?next=https://evil.com",
        "/auth?redirect_uri=https://evil.com",
    ]

    for payload in payloads:
        url = f"https://{subdominio}{payload}"
        status, headers, body, final_url = http_probe(url, allow_redirects=True)

        if status is None:
            break

        from urllib.parse import urlparse
        
        # Si el dominio final es realmente evil.com → redirección exitosa
        final_domain = urlparse(final_url).netloc
        if final_domain == "evil.com":
            msg = (
                f"⚠️  OPEN REDIRECT\n"
                f"URL original: {url}\n"
                f"URL final: {final_url}\n"
                f"Severidad: BAJA-MEDIA ($50-$200)"
            )
            log(msg)
            telegram(msg)
            hallazgos.append({
                "tipo": "open_redirect",
                "url": url,
                "redirige_a": final_url,
            })
            break  # Un open redirect por subdominio es suficiente

    return hallazgos


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Explotador automático de bugs en subdominios nuevos")
    parser.add_argument("--delta", help="Ruta al archivo delta JSON del pipeline OCI")
    parser.add_argument("--subdominio", help="Testear un solo subdominio (modo debug)")
    parser.add_argument("--max", type=int, default=MAX_SUBDOMINIOS, help=f"Máximo de subdominios a testear (default: {MAX_SUBDOMINIOS})")
    args = parser.parse_args()

    print("=" * 60)
    print("  EXPLOTADOR AUTOMÁTICO — Bug Hunter sobre Delta OCI")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Modo: un solo subdominio (debug/manual)
    if args.subdominio:
        subdominios = [args.subdominio]
    else:
        delta = cargar_delta(args.delta)
        subdominios = extraer_subdominios(delta)
        if isinstance(subdominios, dict):
            subdominios = list(subdominios.keys())
        elif not isinstance(subdominios, list):
            subdominios = list(subdominios)

    if not subdominios:
        log("❌ Sin subdominios para testear. Revisá el delta o usá --subdominio DOMINIO")
        sys.exit(1)

    log(f"🎯 Total subdominios a testear: {min(len(subdominios), args.max)}")

    todos_los_hallazgos = []
    testeados = 0

    for sub in subdominios[:args.max]:
        testeados += 1
        sub = sub.strip()
        if not sub:
            continue

        log(f"[{testeados}/{min(len(subdominios), args.max)}] Testeando: {sub}")

        hallazgos_sub = []
        hallazgos_sub += test_subdomain_takeover(sub)
        hallazgos_sub += test_cors(sub)
        hallazgos_sub += test_exposed_files(sub)
        hallazgos_sub += test_open_redirect(sub)

        todos_los_hallazgos.extend(hallazgos_sub)
        time.sleep(0.2)  # Pausa entre subdominios

    # Resumen final
    print("\n" + "=" * 60)
    print(f"  RESUMEN FINAL — {testeados} subdominios testeados")
    print("=" * 60)

    if todos_los_hallazgos:
        tipos = {}
        for h in todos_los_hallazgos:
            t = h["tipo"]
            tipos[t] = tipos.get(t, 0) + 1

        print(f"  🚨 BUGS ENCONTRADOS: {len(todos_los_hallazgos)}")
        for tipo, count in tipos.items():
            print(f"    → {tipo}: {count}")

        # Guardar resultados
        output = f"resultados/explotador_{datetime.now().strftime('%Y-%m-%d')}.json"
        os.makedirs("resultados", exist_ok=True)
        with open(output, "w") as f:
            json.dump(todos_los_hallazgos, f, indent=2)
        log(f"Resultados guardados en {output}")

        telegram(
            f"✅ EXPLOTADOR COMPLETADO\n"
            f"Subdominios testeados: {testeados}\n"
            f"Bugs encontrados: {len(todos_los_hallazgos)}\n"
            f"Detalle: {json.dumps(tipos)}"
        )
    else:
        print("  ✅ Sin bugs encontrados en este delta.")
        log("Sin hallazgos que reportar.")

    print("=" * 60)


if __name__ == "__main__":
    main()
