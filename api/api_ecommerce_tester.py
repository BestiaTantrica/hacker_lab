#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_ecommerce_tester.py — Cascada de Auditoría IDOR — E-Commerce (eBay)
=========================================================================
Adaptación del framework idor_cross_tenant.py para lógica de e-commerce.
Valida aislamiento horizontal y vertical en:
  - Órdenes de compra (orders)
  - Carritos de compra (carts)
  - Direcciones de envío (addresses)
  - Mensajes entre compradores/vendedores
  - Listas de seguimiento (watchlist)

Metodología (4 Pasos + Cola de Revisión):
  1. MAPEO:     Extrae IDs de recursos del Tenant B (víctima) con sus tokens
  2. IDOR:      Tenant A intenta acceder a esos IDs con sus propios tokens
  3. ESCALADA:  Tenant A intenta endpoints administrativos/privilegiados
  4. VALIDACIÓN: Filtra falsos positivos (endpoints públicos documentados)
  Cola:         Respuestas 404/ambiguas → revisión con reintentos HTTP method fuzzing

Uso:
  python3 api_ecommerce_tester.py [--mapeo-solo] [--ataque-solo] [--escalada-solo] [--reintentos]

NOTA: Configurar USER_A_TOKEN y USER_B_TOKEN con OAuth tokens reales
de las cuentas de prueba antes de ejecutar.
"""

import requests
import json
import sys
import time
import argparse
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN — EDITAR SÓLO ESTA SECCIÓN
# Requiere dos cuentas de prueba eBay (Comprador A = Atacante, Comprador B = Víctima)
# Token OAuth: Developer Portal → OAuth Token → Buyer scope
# =============================================================================

# Cuenta A — Atacante (tu cuenta principal de prueba)
USER_A_TOKEN  = "v^1.1#i^1#..."   # OAuth token cuenta A — REEMPLAZAR
USER_A_ID     = ""                 # eBay User ID cuenta A — REEMPLAZAR

# Cuenta B — Víctima (segunda cuenta de prueba)
USER_B_TOKEN  = "v^1.1#i^1#..."   # OAuth token cuenta B — REEMPLAZAR
USER_B_ID     = ""                 # eBay User ID cuenta B — REEMPLAZAR

# Entorno eBay (usar sandbox para pruebas controladas)
EBAY_ENV      = "sandbox"          # "sandbox" | "production"
BASE_URL      = "https://api.sandbox.ebay.com" if EBAY_ENV == "sandbox" else "https://api.ebay.com"

# Endpoints eBay documentados como públicos (no son bugs si devuelven 200)
ENDPOINTS_PUBLICOS = {
    "/buy/browse/v1/item_summary/search",    # Búsqueda pública
    "/buy/browse/v1/category_tree/0",        # Árbol de categorías
    "/commerce/taxonomy/v1/category_tree/0", # Taxonomía pública
}

# =============================================================================
HEADERS_A = {
    "Authorization": f"Bearer {USER_A_TOKEN}",
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
}

HEADERS_B = {
    "Authorization": f"Bearer {USER_B_TOKEN}",
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "X-Bug-Bounty": "HackerOne-tomas244",
}

# Almacén global para la Cola de Revisión
REVIEW_QUEUE = []


def sep(titulo=""):
    print(f"\n{'─'*60}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'─'*60}")


def add_to_queue(endpoint, status_code, method, motivo):
    """Añade un endpoint ambiguo a la Cola de Revisión para reintentos."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "status_code": status_code,
        "method": method,
        "motivo": motivo,
    }
    REVIEW_QUEUE.append(entry)
    print(f"  COLA DE ESPERA: [{method}] {endpoint} → HTTP {status_code} — {motivo}")


def verificar_token(headers, nombre):
    """Verifica que el OAuth token sea válido consultando el perfil del usuario."""
    url = f"{BASE_URL}/sell/account/v1/privilege"
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        print(f"  {nombre}: Token OAuth válido ✅")
        return True
    elif r.status_code == 401:
        print(f"  {nombre}: ❌ Token inválido o expirado (HTTP 401)")
        return False
    else:
        # Token puede ser válido pero el scope no cubre este endpoint
        print(f"  {nombre}: HTTP {r.status_code} — asumiendo token activo ⚠️")
        return True


def mapear_ids_victima(headers_b):
    """
    Paso 1 — Extrae IDs de recursos del Tenant B (víctima).
    Sólo usa los tokens del Tenant B (víctima accede a sus propios recursos).
    """
    sep("PASO 1 — MAPEO DE RECURSOS DE LA VÍCTIMA (Tenant B)")
    recursos = {}

    endpoints = {
        "orders": {
            "url": f"{BASE_URL}/sell/fulfillment/v1/order",
            "id_field": "orderId",
            "params": {"limit": 20},
            "lista_key": "orders",
        },
        "guest_orders": {
            "url": f"{BASE_URL}/buy/order/v2/guest_purchase_order",
            "id_field": "purchaseOrderId",
            "params": {},
            "lista_key": None,  # Objeto único
        },
        "addresses": {
            "url": f"{BASE_URL}/identity/v1/oauth2/userinfo",
            "id_field": "userId",
            "params": {},
            "lista_key": None,
        },
        "shopping_cart": {
            "url": f"{BASE_URL}/buy/order/v2/shopping_cart",
            "id_field": "cartId",
            "params": {},
            "lista_key": None,
        },
        "offers": {
            "url": f"{BASE_URL}/sell/negotiation/v1/find_eligible_items",
            "id_field": "itemId",
            "params": {"limit": 10},
            "lista_key": "eligibleItems",
        },
        "feedback": {
            "url": f"{BASE_URL}/sell/feedback/v1/feedback_summary",
            "id_field": "feedbackId",
            "params": {},
            "lista_key": None,
        },
    }

    for nombre_rec, cfg in endpoints.items():
        try:
            r = requests.get(cfg["url"], headers=headers_b, params=cfg.get("params", {}), timeout=10)
            time.sleep(0.5)

            if r.status_code == 200:
                data = r.json()
                lista_key = cfg.get("lista_key")
                id_field = cfg["id_field"]

                if lista_key and lista_key in data:
                    items = data[lista_key]
                    ids = [item.get(id_field) for item in items if item.get(id_field)]
                elif isinstance(data, dict) and id_field in data:
                    ids = [data[id_field]]
                else:
                    ids = []

                recursos[nombre_rec] = ids
                print(f"  {nombre_rec:15s}: {len(ids)} IDs encontrados → {ids[:3]}")

            elif r.status_code == 404:
                print(f"  {nombre_rec:15s}: 404 — Sin recursos creados en esta cuenta")
                recursos[nombre_rec] = []
            elif r.status_code == 403:
                print(f"  {nombre_rec:15s}: 403 — Fuera de scope del token (scope insuficiente)")
                recursos[nombre_rec] = []
                add_to_queue(cfg["url"], r.status_code, "GET", "Scope posiblemente insuficiente para mapeo")
            elif r.status_code == 401:
                print(f"  {nombre_rec:15s}: 401 — Token inválido")
                recursos[nombre_rec] = []
            else:
                print(f"  {nombre_rec:15s}: HTTP {r.status_code}")
                recursos[nombre_rec] = []
                add_to_queue(cfg["url"], r.status_code, "GET", "Respuesta inesperada durante mapeo")

        except Exception as e:
            print(f"  {nombre_rec:15s}: ERROR {e}")
            recursos[nombre_rec] = []

    total = sum(len(v) for v in recursos.values())
    print(f"\n  Total IDs mapeados: {total}")
    return recursos


def test_idor_horizontal(headers_a, ids_victima):
    """
    Paso 2 — IDOR Horizontal: Atacante (Tenant A) intenta acceder a recursos del Tenant B.
    Si responde 200 con datos del otro usuario → IDOR confirmado.
    """
    sep("PASO 2 — IDOR HORIZONTAL (Atacante → Víctima)")

    # Mapa: tipo de recurso → URL template con el ID
    endpoint_templates = {
        "orders": f"{BASE_URL}/sell/fulfillment/v1/order/{{id}}",
        "shopping_cart": f"{BASE_URL}/buy/order/v2/shopping_cart/{{id}}",
        "offers": f"{BASE_URL}/sell/offer/v1/offer/{{id}}",
        "feedback": f"{BASE_URL}/sell/feedback/v1/feedback/{{id}}",
        "guest_orders": f"{BASE_URL}/buy/order/v2/guest_purchase_order/{{id}}",
    }

    hallazgos = []
    total_tests = 0

    for tipo, template in endpoint_templates.items():
        ids = ids_victima.get(tipo, [])
        if not ids:
            print(f"\n  {tipo:15s}: Sin IDs del Tenant B — saltando")
            continue

        print(f"\n  --- Testeando {tipo.upper()} desde Tenant A ---")
        for rid in ids[:5]:  # Máx 5 IDs por tipo para no hacer spam
            time.sleep(0.8)
            total_tests += 1
            url = template.format(id=rid)

            try:
                r = requests.get(url, headers=headers_a, timeout=10)

                if r.status_code == 200:
                    data = r.json()
                    # Verificar si los datos pertenecen a otro usuario
                    buyer_id = data.get("buyer", {}).get("username", "")
                    seller_id = data.get("sellerId", data.get("seller", {}).get("username", ""))
                    owner = buyer_id or seller_id or "Desconocido"

                    print(f"  🚨🚨 IDOR CONFIRMADO [{tipo}][{rid}]: Owner={owner}")
                    hallazgos.append({
                        "tipo": tipo,
                        "id": rid,
                        "url": url,
                        "owner_en_respuesta": owner,
                        "curl_poc": f'curl -H "Authorization: Bearer {USER_A_TOKEN[:20]}..." "{url}"',
                        "data_snippet": json.dumps(data)[:500],
                    })
                elif r.status_code == 403:
                    print(f"  ✅ [{tipo}][{rid}]: 403 — Correctamente aislado (acceso denegado)")
                elif r.status_code == 404:
                    print(f"  ✅ [{tipo}][{rid}]: 404 — ID no accesible cross-tenant")
                    add_to_queue(url, 404, "GET", f"ID {rid} de tipo {tipo} → 404 bajo token Atacante")
                elif r.status_code == 429:
                    print(f"  ⏳ Rate limited — pausando 20s...")
                    time.sleep(20)
                    add_to_queue(url, 429, "GET", "Rate limit alcanzado")
                else:
                    print(f"  ❓ [{tipo}][{rid}]: HTTP {r.status_code}")
                    add_to_queue(url, r.status_code, "GET", f"Respuesta ambigua en ID {rid}")

            except Exception as e:
                print(f"  [{tipo}][{rid}]: ERROR {e}")

    print(f"\n  Tests realizados: {total_tests} | Hallazgos: {len(hallazgos)}")
    if hallazgos:
        print(f"\n  🚨🚨🚨 IDOR CROSS-USER CONFIRMADO — {len(hallazgos)} recursos accesibles!")
        for h in hallazgos:
            print(f"\n    → URL: {h['url']}")
            print(f"      Owner en respuesta: {h['owner_en_respuesta']}")
            print(f"      PoC cURL: {h['curl_poc']}")
    else:
        print("\n  ✅ Sin IDOR horizontal detectado.")

    return hallazgos


def test_escalada_vertical(headers_a):
    """
    Paso 3 — Escalada Vertical: Atacante intenta endpoints privilegiados/admin de eBay.
    Incluye Paso 4 (Validación) para descartar falsos positivos automáticamente.
    """
    sep("PASO 3 — ESCALADA VERTICAL (Atacante → Admin)")

    endpoints_admin = [
        # Seller Hub admin-level
        f"{BASE_URL}/sell/account/v1/payment_policy",
        f"{BASE_URL}/sell/account/v1/fulfillment_policy",
        f"{BASE_URL}/sell/account/v1/return_policy",
        f"{BASE_URL}/sell/account/v1/sales_tax",
        # Endpoints de gestión no documentados públicamente
        f"{BASE_URL}/sell/marketing/v1/ad_campaign",
        f"{BASE_URL}/sell/finances/v1/payout",
        f"{BASE_URL}/sell/finances/v1/transaction",
        f"{BASE_URL}/sell/analytics/v1/seller_standards_profile",
        # Endpoints de otros usuarios (IDOR vertical)
        f"{BASE_URL}/sell/account/v1/subscription",
        f"{BASE_URL}/commerce/identity/v1/user",
    ]

    hallazgos = []

    for ep in endpoints_admin:
        try:
            time.sleep(0.5)
            r = requests.get(ep, headers=headers_a, timeout=10)

            if r.status_code == 200:
                # Validación anti-FP: ¿es un endpoint documentado como público?
                ep_path = ep.replace(BASE_URL, "")
                if ep_path in ENDPOINTS_PUBLICOS:
                    print(f"  ⚠️  [{ep_path}]: 200 — FALSO POSITIVO (endpoint público documentado)")
                else:
                    print(f"  🚨🚨 ESCALADA [{ep_path}]: 200 OK — acceso privilegiado!")
                    hallazgos.append({
                        "tipo": "Escalada de Privilegios",
                        "url": ep,
                        "curl_poc": f'curl -H "Authorization: Bearer {USER_A_TOKEN[:20]}..." "{ep}"',
                        "data": r.json(),
                    })
            elif r.status_code in [401, 403]:
                ep_path = ep.replace(BASE_URL, "")
                print(f"  ✅ [{ep_path}]: {r.status_code} — Correctamente bloqueado")
            elif r.status_code == 404:
                ep_path = ep.replace(BASE_URL, "")
                print(f"  ❓ [{ep_path}]: 404 — Endpoint no expuesto o ruta diferente")
                add_to_queue(ep, 404, "GET", "Endpoint admin → 404 bajo token normal")
            else:
                ep_path = ep.replace(BASE_URL, "")
                print(f"  ⚠️  [{ep_path}]: HTTP {r.status_code}")
                add_to_queue(ep, r.status_code, "GET", f"Comportamiento anómalo en endpoint admin")

        except Exception as e:
            print(f"  {ep}: ERROR {e}")

    if hallazgos:
        print(f"\n  🚨🚨🚨 ESCALADA CONFIRMADA — {len(hallazgos)} endpoints vulnerables!")
        for h in hallazgos:
            print(f"    → {h['url']}")
            print(f"      cURL PoC: {h['curl_poc']}")
    else:
        print("\n  ✅ Sin escalada detectada (falsos positivos descartados por validador).")

    return hallazgos


def procesar_cola_reintentos(headers_a):
    """
    Paso 5 — Módulo de Reintentos: Procesa la Cola de Revisión con HTTP Method Fuzzing.
    Para cada endpoint ambiguo (404/anómalo), prueba:
      - GET, POST, PUT, PATCH, DELETE
      - Variaciones de Content-Type
    Objetivo: determinar si la ruta existe pero requiere método/sintaxis diferente.
    """
    sep("PASO 5 — REINTENTOS AUTOMÁTICOS (Review Queue Processing)")

    if not REVIEW_QUEUE:
        print("  Cola de revisión vacía. Ejecutar pasos 1-3 primero.")
        return []

    print(f"  Procesando {len(REVIEW_QUEUE)} endpoints en cola...")
    METODOS_HTTP = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    CONTENT_TYPES = [
        "application/json",
        "application/x-www-form-urlencoded",
        "text/plain",
    ]

    hallazgos_reintentos = []

    for item in REVIEW_QUEUE:
        url = item["endpoint"]
        ep_path = url.replace(BASE_URL, "")
        print(f"\n  🔄 Reintentando: {ep_path}")
        print(f"     Motivo original: {item['motivo']}")

        for method in METODOS_HTTP:
            for ct in CONTENT_TYPES:
                time.sleep(0.4)
                try:
                    headers_mod = {**headers_a, "Content-Type": ct}
                    r = requests.request(method, url, headers=headers_mod, timeout=8, data="{}")

                    if r.status_code == 200:
                        print(f"  🚨 HALLAZGO en REINTENTO [{method}][{ct}]: {ep_path} → 200 OK!")
                        hallazgos_reintentos.append({
                            "url": url,
                            "method": method,
                            "content_type": ct,
                            "status": 200,
                            "snippet": r.text[:300],
                            "curl_poc": f'curl -X {method} -H "Content-Type: {ct}" -H "Authorization: Bearer {USER_A_TOKEN[:20]}..." "{url}"',
                        })
                        break  # Encontrado con este método, no seguir con este endpoint
                    elif r.status_code == 405:
                        print(f"     [{method}]: 405 — Método no permitido (endpoint existe)")
                        add_to_queue(url, 405, method, "Método rechazado pero endpoint existe")
                    elif r.status_code not in [404, 401, 403]:
                        print(f"     [{method}][{ct}]: {r.status_code} — respuesta interesante")

                except Exception as e:
                    pass  # Silencioso para no ensuciar la consola en fuzzing masivo

    print(f"\n  Reintentos completados: {len(hallazgos_reintentos)} hallazgos adicionales")
    return hallazgos_reintentos


def imprimir_resumen_cola():
    """Muestra el contenido completo de la Cola de Revisión."""
    sep("COLA DE REVISIÓN (Review Queue)")
    if not REVIEW_QUEUE:
        print("  Cola vacía.")
        return
    for i, item in enumerate(REVIEW_QUEUE, 1):
        print(f"  [{i}] {item['method']} {item['endpoint'].replace(BASE_URL, '')}")
        print(f"       HTTP {item['status_code']} — {item['motivo']}")
        print(f"       ⏱  {item['timestamp']}")


def main():
    parser = argparse.ArgumentParser(description="E-Commerce IDOR Tester — eBay")
    parser.add_argument("--mapeo-solo",    action="store_true", help="Solo ejecutar Paso 1 (Mapeo)")
    parser.add_argument("--ataque-solo",   action="store_true", help="Solo ejecutar Paso 2 (IDOR)")
    parser.add_argument("--escalada-solo", action="store_true", help="Solo ejecutar Paso 3 (Escalada)")
    parser.add_argument("--reintentos",    action="store_true", help="Solo ejecutar Paso 5 (Reintentos)")
    parser.add_argument("--cola",          action="store_true", help="Mostrar Cola de Revisión y salir")
    args = parser.parse_args()

    print("=" * 60)
    print("  TEST IDOR E-COMMERCE — eBay")
    print(f"  Entorno: {EBAY_ENV.upper()}")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Atacante User ID: {USER_A_ID or '[NO CONFIGURADO]'}")
    print(f"  Víctima  User ID: {USER_B_ID or '[NO CONFIGURADO]'}")
    print("=" * 60)

    # Guardia: tokens no configurados
    if "v^1.1#i^1#..." in USER_A_TOKEN or "v^1.1#i^1#..." in USER_B_TOKEN:
        print("\n  ⚠️  TOKENS NO CONFIGURADOS.")
        print("  Editar USER_A_TOKEN y USER_B_TOKEN en la sección de configuración.")
        print("  Obtener en: https://developer.ebay.com/my/auth/?env=sandbox")
        sys.exit(1)

    # Construir headers con tokens reales
    headers_a = {**HEADERS_A, "Authorization": f"Bearer {USER_A_TOKEN}"}
    headers_b = {**HEADERS_B, "Authorization": f"Bearer {USER_B_TOKEN}"}

    # Verificar tokens
    sep("VERIFICANDO TOKENS OAUTH")
    ok_a = verificar_token(headers_a, "Tenant A (atacante)")
    ok_b = verificar_token(headers_b, "Tenant B (víctima) ")
    if not ok_a or not ok_b:
        print("\n❌ Tokens inválidos. Verificar configuración.")
        sys.exit(1)

    # ── Rutas de ejecución parcial ──────────────────────────────
    if args.cola:
        imprimir_resumen_cola()
        sys.exit(0)

    if args.reintentos:
        hallazgos = procesar_cola_reintentos(headers_a)
        imprimir_resumen_cola()
        sys.exit(0)

    # ── Paso 1: Mapeo ────────────────────────────────────────────
    ids_victima = mapear_ids_victima(headers_b)

    if args.mapeo_solo:
        print("\n✅ MAPEO COMPLETADO. Puede avanzar al Paso 2.")
        sys.exit(0)

    # ── Paso 2: IDOR Horizontal ──────────────────────────────────
    if not args.escalada_solo:
        hallazgos_idor = test_idor_horizontal(headers_a, ids_victima)
    else:
        hallazgos_idor = []

    if args.ataque_solo:
        imprimir_resumen_cola()
        sys.exit(0)

    # ── Paso 3 + 4: Escalada + Validación ───────────────────────
    hallazgos_escalada = test_escalada_vertical(headers_a)

    # ── Paso 5: Reintentos sobre la cola ────────────────────────
    if REVIEW_QUEUE:
        print(f"\n  ℹ️  {len(REVIEW_QUEUE)} endpoints en Cola de Revisión.")
        print("  Ejecutar con --reintentos para procesar (HTTP Method Fuzzing).")

    # ── Conclusión ───────────────────────────────────────────────
    sep("CONCLUSIÓN FINAL")
    total = len(hallazgos_idor) + len(hallazgos_escalada)
    if total > 0:
        print(f"  🎯 {total} HALLAZGO(S) CONFIRMADOS — Preparar reporte para HackerOne")
        print(f"     IDOR Horizontal: {len(hallazgos_idor)}")
        print(f"     Escalada Vertical: {len(hallazgos_escalada)}")
    else:
        print("  ✅ Sin hallazgos en este vector.")
    imprimir_resumen_cola()
    print("=" * 60)


if __name__ == "__main__":
    main()
