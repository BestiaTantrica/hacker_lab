#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parseador_burp.py — Parser eficiente de tráfico Burp Suite (XML) para Bug Bounty MongoDB
==========================================================================================
Usa xml.etree.ElementTree.iterparse() para procesar archivos grandes (~60 MB)
de forma incremental, sin cargar el árbol completo en memoria.

Salida: JSON estructurado en LAB/api/burp_analisis.json
        Resumen legible en LAB/api/burp_resumen.txt

Uso:
    python3 parseador_burp.py [ruta_al_xml]
    # Si no se pasa ruta, usa la ruta por defecto del lab.
"""

import sys
import os
import re
import json
import base64
import urllib.parse
from xml.etree.ElementTree import iterparse
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XML  = os.path.join(SCRIPT_DIR, "trafico_burp.xml")
OUTPUT_JSON  = os.path.join(SCRIPT_DIR, "burp_analisis.json")
OUTPUT_TXT   = os.path.join(SCRIPT_DIR, "burp_resumen.txt")

# Dominios en scope (MongoDB HackerOne)
SCOPE_DOMINIOS = {
    "mongodb.com", "cloud.mongodb.com", "account.mongodb.com",
    "realm.mongodb.com", "charts.mongodb.com", "university.mongodb.com",
    "support.mongodb.com", "developer.mongodb.com",
}

# Códigos HTTP que nos interesan para análisis
CODIGOS_ANOMALOS  = {400, 401, 403, 404, 405, 409, 422, 429, 500, 502, 503}
CODIGOS_OK_API    = {200, 201, 204}

# Cabeceras de seguridad relevantes (a capturar si aparecen — o si FALTAN)
CABECERAS_SEGURIDAD = {
    "x-content-type-options", "x-frame-options", "strict-transport-security",
    "content-security-policy", "x-xss-protection", "access-control-allow-origin",
    "access-control-allow-credentials", "access-control-allow-methods",
    "x-ratelimit-limit", "x-ratelimit-remaining", "retry-after",
    "set-cookie", "authorization", "x-api-version", "x-request-id",
    "x-hackerone-research",
}

# Parámetros de interés en queries/body (possibles vectores)
PARAMS_INTERES = {
    "token", "key", "secret", "password", "passwd", "auth", "apikey",
    "api_key", "access_token", "refresh_token", "redirect", "next",
    "url", "callback", "origin", "host", "id", "user", "username",
    "email", "groupId", "orgId", "projectId", "clusterId", "userId",
}

# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------

def decodificar_content(texto: str, es_base64: bool) -> str:
    """Decodifica el contenido si está en base64, limpia NULLs."""
    if not texto:
        return ""
    if es_base64:
        try:
            decoded = base64.b64decode(texto.strip()).decode("utf-8", errors="replace")
            return decoded.replace("\x00", "")
        except Exception:
            return texto
    return texto.replace("\x00", "")


def extraer_cabeceras(raw: str) -> dict:
    """Extrae cabeceras HTTP de texto raw (request o response)."""
    cabeceras = {}
    lineas = raw.splitlines()
    # La primera línea es la request/status line, ignorar
    for linea in lineas[1:]:
        linea = linea.strip()
        if not linea:
            break  # Fin de cabeceras
        if ":" in linea:
            nombre, _, valor = linea.partition(":")
            cabeceras[nombre.strip().lower()] = valor.strip()
    return cabeceras


def extraer_body(raw: str) -> str:
    """Extrae el body HTTP (después de la línea en blanco)."""
    partes = raw.split("\r\n\r\n", 1)
    if len(partes) < 2:
        partes = raw.split("\n\n", 1)
    return partes[1].strip() if len(partes) == 2 else ""


def extraer_params_url(path: str) -> dict:
    """Extrae parámetros de query string."""
    if "?" not in path:
        return {}
    _, qs = path.split("?", 1)
    try:
        return dict(urllib.parse.parse_qsl(qs, keep_blank_values=True))
    except Exception:
        return {}


def extraer_params_body(body: str, content_type: str) -> dict:
    """Extrae parámetros del body según Content-Type."""
    params = {}
    ct = (content_type or "").lower()
    if not body:
        return params

    if "application/json" in ct or body.lstrip().startswith("{"):
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                params = {k: str(v)[:200] for k, v in data.items()}
        except Exception:
            pass
    elif "application/x-www-form-urlencoded" in ct:
        try:
            params = dict(urllib.parse.parse_qsl(body, keep_blank_values=True))
        except Exception:
            pass
    return params


def normalizar_path(path: str) -> str:
    """Normaliza el path sustituyendo IDs dinámicos por placeholders."""
    # UUID / ObjectID
    path = re.sub(
        r"/[0-9a-f]{24}(?=/|$)",   # MongoDB ObjectId
        "/{objectId}",
        path
    )
    path = re.sub(
        r"/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}(?=/|$)",
        "/{uuid}",
        path
    )
    # Números puros
    path = re.sub(r"/\d{4,}(?=/|$)", "/{id}", path)
    # Eliminar query string
    path = path.split("?")[0]
    return path


def params_son_interesantes(params: dict) -> list:
    """Devuelve la lista de parámetros que coinciden con PARAMS_INTERES."""
    return [k for k in params if k.lower() in PARAMS_INTERES]


def host_en_scope(host: str) -> bool:
    """True si el host está en scope MongoDB."""
    host = host.lower()
    return host in SCOPE_DOMINIOS or any(host.endswith("." + d) for d in SCOPE_DOMINIOS)


# ---------------------------------------------------------------------------
# PARSER PRINCIPAL
# ---------------------------------------------------------------------------

def parsear_burp(xml_path: str) -> dict:
    """
    Procesa el XML de Burp con iterparse para memoria eficiente.
    Devuelve un diccionario estructurado con todos los hallazgos.
    """
    print(f"[*] Procesando: {xml_path}")
    print(f"[*] Tamaño: {os.path.getsize(xml_path) / 1024 / 1024:.1f} MB")
    print("[*] Usando iterparse (streaming) — memoria controlada...")

    # Acumuladores
    endpoints_unicos  = defaultdict(lambda: {"métodos": set(), "status_codes": set(), "count": 0})
    hosts_unicos      = defaultdict(int)
    params_url_global = defaultdict(set)   # param -> set de paths donde aparece
    params_body_global= defaultdict(set)
    items_anomalos    = []
    items_ok_api      = []   # 200/201 con body JSON interesante
    cabeceras_vistas  = defaultdict(set)   # cabecera -> set de hosts
    cors_configs      = []
    parametros_sensibles_hallados = []

    total_items     = 0
    items_scope     = 0
    items_sin_scope = 0

    # --- Iterparse: bajo consumo de memoria ---
    context = iterparse(xml_path, events=("end",))

    for event, elem in context:
        if elem.tag != "item":
            continue

        total_items += 1
        if total_items % 500 == 0:
            print(f"  ... procesados {total_items} items", end="\r", flush=True)

        # Extraer campos del item
        host_elem = elem.find("host")
        host     = (host_elem.text or "").strip() if host_elem is not None else ""
        host_ip  = host_elem.get("ip", "") if host_elem is not None else ""

        url_elem = elem.find("url")
        url = ""
        if url_elem is not None:
            url = (url_elem.text or "").strip()

        method_elem = elem.find("method")
        method = (method_elem.text or "GET").strip().upper() if method_elem is not None else "GET"

        path_elem = elem.find("path")
        path = (path_elem.text or "/").strip() if path_elem is not None else "/"

        status_elem = elem.find("status")
        try:
            status = int((status_elem.text or "0").strip()) if status_elem is not None else 0
        except ValueError:
            status = 0

        resp_len_elem = elem.find("responselength")
        try:
            resp_len = int((resp_len_elem.text or "0").strip()) if resp_len_elem is not None else 0
        except ValueError:
            resp_len = 0

        mime_elem = elem.find("mimetype")
        mimetype = (mime_elem.text or "").strip().lower() if mime_elem is not None else ""

        request_elem = elem.find("request")
        req_b64  = (request_elem is not None) and request_elem.get("base64", "false") == "true"
        req_raw  = decodificar_content(request_elem.text or "", req_b64) if request_elem is not None else ""

        response_elem = elem.find("response")
        resp_b64 = (response_elem is not None) and response_elem.get("base64", "false") == "true"
        resp_raw = decodificar_content(response_elem.text or "", resp_b64) if response_elem is not None else ""

        # Liberar memoria del elemento ya procesado
        elem.clear()

        # ── FILTRO DE SCOPE ─────────────────────────────────────────────────
        if not host_en_scope(host):
            items_sin_scope += 1
            continue

        items_scope += 1
        hosts_unicos[host] += 1

        # ── ENDPOINT NORMALIZADO ─────────────────────────────────────────────
        path_norm = normalizar_path(path)
        endpoint_key = f"{host}{path_norm}"
        endpoints_unicos[endpoint_key]["métodos"].add(method)
        endpoints_unicos[endpoint_key]["status_codes"].add(status)
        endpoints_unicos[endpoint_key]["count"] += 1
        endpoints_unicos[endpoint_key].setdefault("host", host)
        endpoints_unicos[endpoint_key].setdefault("path", path_norm)

        # ── PARÁMETROS URL ───────────────────────────────────────────────────
        params_url = extraer_params_url(path)
        for p in params_url:
            params_url_global[p].add(path_norm)
            if p.lower() in PARAMS_INTERES:
                parametros_sensibles_hallados.append({
                    "tipo": "url",
                    "param": p,
                    "path": path,
                    "host": host,
                    "method": method,
                    "status": status,
                })

        # ── CABECERAS REQUEST ────────────────────────────────────────────────
        req_headers = extraer_cabeceras(req_raw) if req_raw else {}
        req_ct = req_headers.get("content-type", "")

        # ── PARÁMETROS BODY ──────────────────────────────────────────────────
        if method in ("POST", "PUT", "PATCH") and req_raw:
            body = extraer_body(req_raw)
            params_body = extraer_params_body(body, req_ct)
            for p in params_body:
                params_body_global[p].add(path_norm)
                if p.lower() in PARAMS_INTERES:
                    parametros_sensibles_hallados.append({
                        "tipo": "body",
                        "param": p,
                        "path": path,
                        "host": host,
                        "method": method,
                        "status": status,
                        "valor_preview": str(params_body[p])[:100],
                    })

        # ── CABECERAS RESPONSE ───────────────────────────────────────────────
        resp_headers = extraer_cabeceras(resp_raw) if resp_raw else {}
        for h in CABECERAS_SEGURIDAD:
            if h in resp_headers:
                cabeceras_vistas[h].add(host)

        # CORS específico
        acao = resp_headers.get("access-control-allow-origin", "")
        acac = resp_headers.get("access-control-allow-credentials", "")
        if acao:
            cors_entry = {
                "url": url,
                "host": host,
                "path": path,
                "method": method,
                "status": status,
                "acao": acao,
                "acac": acac,
            }
            # Solo guardamos los interesantes (wildcard o credenciales)
            if acao == "*" or (acao not in ("", "null") and acac.lower() == "true"):
                cors_configs.append(cors_entry)

        # ── ITEMS ANÓMALOS ───────────────────────────────────────────────────
        if status in CODIGOS_ANOMALOS:
            # Capturamos resumen, no el raw completo (ahorro de memoria)
            resp_preview = resp_raw[:800] if resp_raw else ""
            req_preview  = req_raw[:400]  if req_raw  else ""
            items_anomalos.append({
                "url": url,
                "host": host,
                "path": path,
                "method": method,
                "status": status,
                "resp_len": resp_len,
                "mimetype": mimetype,
                "req_headers_seg": {k: v for k, v in req_headers.items()
                                    if k.lower() in CABECERAS_SEGURIDAD},
                "resp_headers_seg": {k: v for k, v in resp_headers.items()
                                     if k.lower() in CABECERAS_SEGURIDAD},
                "resp_preview": resp_preview,
                "req_preview":  req_preview,
            })

        # ── ITEMS OK CON JSON (APIs interesantes) ────────────────────────────
        elif status in CODIGOS_OK_API and "json" in mimetype:
            resp_body_preview = extraer_body(resp_raw)[:600] if resp_raw else ""
            if resp_body_preview:  # Solo si tiene cuerpo
                items_ok_api.append({
                    "url": url,
                    "host": host,
                    "path": path,
                    "method": method,
                    "status": status,
                    "resp_len": resp_len,
                    "resp_body_preview": resp_body_preview,
                })

    print(f"\n[*] Procesamiento completo. Total items: {total_items}")

    # Serializar sets a listas para JSON
    endpoints_serial = {}
    for k, v in endpoints_unicos.items():
        endpoints_serial[k] = {
            "host":    v["host"],
            "path":    v["path"],
            "métodos": sorted(v["métodos"]),
            "status_codes": sorted(v["status_codes"]),
            "count":   v["count"],
        }

    params_url_serial = {k: sorted(v) for k, v in params_url_global.items()}
    params_body_serial= {k: sorted(v) for k, v in params_body_global.items()}
    cabeceras_serial  = {k: sorted(v) for k, v in cabeceras_vistas.items()}

    return {
        "metadata": {
            "archivo_origen": xml_path,
            "fecha_analisis": datetime.now().isoformat(),
            "total_items_xml": total_items,
            "items_en_scope":  items_scope,
            "items_fuera_scope": items_sin_scope,
        },
        "hosts": dict(sorted(hosts_unicos.items(), key=lambda x: -x[1])),
        "endpoints_unicos": endpoints_serial,
        "parametros_url": params_url_serial,
        "parametros_body": params_body_serial,
        "parametros_sensibles": parametros_sensibles_hallados,
        "items_anomalos": items_anomalos,
        "items_api_ok": items_ok_api,
        "cabeceras_seguridad_vistas": cabeceras_serial,
        "cors_interesante": cors_configs,
    }


# ---------------------------------------------------------------------------
# GENERADOR DE RESUMEN LEGIBLE
# ---------------------------------------------------------------------------

def generar_resumen(datos: dict) -> str:
    meta = datos["metadata"]
    hosts = datos["hosts"]
    endpoints = datos["endpoints_unicos"]
    params_s = datos["parametros_sensibles"]
    anomalos = datos["items_anomalos"]
    cors = datos["cors_interesante"]
    cabeceras = datos["cabeceras_seguridad_vistas"]
    api_ok = datos["items_api_ok"]

    lineas = []
    L = lineas.append

    L("=" * 70)
    L("  ANÁLISIS DE TRÁFICO BURP SUITE — MongoDB Bug Bounty Lab")
    L(f"  Generado: {meta['fecha_analisis']}")
    L("=" * 70)
    L("")
    L(f"ESTADÍSTICAS GENERALES")
    L(f"  Total items en XML          : {meta['total_items_xml']}")
    L(f"  Items en scope (*.mongodb.com): {meta['items_en_scope']}")
    L(f"  Items fuera de scope         : {meta['items_fuera_scope']}")
    L(f"  Endpoints únicos             : {len(endpoints)}")
    L("")

    L("─" * 70)
    L("HOSTS DESCUBIERTOS (en scope)")
    for host, count in hosts.items():
        L(f"  {host:<40} {count:>5} requests")
    L("")

    L("─" * 70)
    L("ENDPOINTS ÚNICOS (top 60 por hits)")
    top_endpoints = sorted(endpoints.values(), key=lambda x: -x["count"])[:60]
    for ep in top_endpoints:
        métodos = ",".join(ep["métodos"])
        codes   = ",".join(str(c) for c in ep["status_codes"])
        L(f"  [{métodos:<15}] [{codes:<20}] {ep['count']:>4}x  {ep['host']}{ep['path']}")
    L("")

    L("─" * 70)
    L(f"ITEMS CON STATUS ANÓMALO ({len(anomalos)} total)")
    # Agrupar por status
    por_status = defaultdict(list)
    for it in anomalos:
        por_status[it["status"]].append(it)
    for code in sorted(por_status.keys()):
        items_code = por_status[code]
        L(f"\n  [{code}] — {len(items_code)} requests")
        for it in items_code[:5]:
            L(f"    {it['method']:<7} {it['host']}{it['path']}")
            if it.get("resp_preview"):
                preview = it["resp_preview"][:200].replace("\n", " ")
                L(f"           Resp: {preview}")
        if len(items_code) > 5:
            L(f"    ... y {len(items_code) - 5} más (ver burp_analisis.json)")
    L("")

    L("─" * 70)
    L(f"PARÁMETROS SENSIBLES DETECTADOS ({len(params_s)} ocurrencias)")
    # Deduplicar por param+host
    vistos = set()
    for p in params_s:
        key = (p["param"], p["host"])
        if key not in vistos:
            vistos.add(key)
            L(f"  [{p['tipo'].upper():<5}] {p['param']:<20} en {p['host']}{p['path']} [{p['status']}]")
    L("")

    L("─" * 70)
    L(f"CONFIGURACIONES CORS INTERESANTES ({len(cors)} hallazgos)")
    for c in cors[:20]:
        L(f"  {c['host']}{c['path']}")
        L(f"    ACAO: {c['acao']}  |  ACAC: {c['acac']}  |  [{c['status']}]")
    L("")

    L("─" * 70)
    L("CABECERAS DE SEGURIDAD OBSERVADAS EN RESPONSES")
    for cab, hosts_set in sorted(cabeceras.items()):
        L(f"  {cab:<40} en {len(hosts_set)} host(s): {', '.join(sorted(hosts_set)[:3])}")

    L("")
    L("─" * 70)
    L(f"APIs JSON CON 200/201 (muestra de {min(len(api_ok), 20)} de {len(api_ok)})")
    for it in api_ok[:20]:
        L(f"  {it['method']:<7} {it['host']}{it['path']} ({it['resp_len']} bytes)")
        if it.get("resp_body_preview"):
            preview = it["resp_body_preview"][:180].replace("\n", " ")
            L(f"           {preview}")
    L("")

    L("=" * 70)
    L("VECTORES DE ATAQUE SUGERIDOS PARA REVISIÓN MANUAL:")
    L("")

    # Análisis automático de vectores
    vectores = []

    # CORS
    if cors:
        vectores.append(
            f"  [CORS] {len(cors)} endpoints con CORS permisivo detectados.\n"
            "         → Verificar si ACAO refleja el Origin del request (CORS bypass).\n"
            "         → Con ACAC: true, probar si incluye cookies de sesión."
        )

    # 401/403 en APIs
    c401 = [x for x in anomalos if x["status"] == 401]
    c403 = [x for x in anomalos if x["status"] == 403]
    if c401:
        vectores.append(
            f"  [AuthN] {len(c401)} requests con 401. Endpoints de autenticación.\n"
            "         → Probar tokens expirados, nulos o mal formados.\n"
            "         → Verificar si hay diferencia entre 401 con/sin cabecera Authorization."
        )
    if c403:
        vectores.append(
            f"  [AuthZ] {len(c403)} requests con 403. Posible IDOR o escalada de privilegios.\n"
            "         → Probar con otro orgId/groupId/userId en la misma ruta.\n"
            "         → Cambiar método HTTP (GET→POST, DELETE→PUT)."
        )

    # 500
    c500 = [x for x in anomalos if x["status"] == 500]
    if c500:
        vectores.append(
            f"  [Error] {len(c500)} requests con 500. Posible información en stack trace.\n"
            "         → Revisar resp_preview en burp_analisis.json.\n"
            "         → Probar payloads malformados en los mismos endpoints."
        )

    # Parámetros sensibles
    if params_s:
        ps_nombres = list({p["param"] for p in params_s})[:8]
        vectores.append(
            f"  [Params] Parámetros sensibles: {', '.join(ps_nombres)}\n"
            "         → Verificar si el servidor valida/sanitiza estos valores.\n"
            "         → Probar manipulación de IDs (IDOR), open redirect (redirect/url)."
        )

    for v in vectores:
        L(v)
        L("")

    L("=" * 70)
    L("Archivos de salida:")
    L(f"  JSON completo : {OUTPUT_JSON}")
    L(f"  Este resumen  : {OUTPUT_TXT}")
    L("=" * 70)

    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    xml_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XML

    if not os.path.isfile(xml_path):
        print(f"[ERROR] Archivo no encontrado: {xml_path}")
        sys.exit(1)

    datos = parsear_burp(xml_path)

    # Guardar JSON
    print(f"[*] Guardando JSON → {OUTPUT_JSON}")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    # Guardar resumen texto
    resumen = generar_resumen(datos)
    print(f"[*] Guardando resumen → {OUTPUT_TXT}")
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(resumen)

    # Imprimir resumen en consola también
    print()
    print(resumen)


if __name__ == "__main__":
    main()
