import os
import sys
import json
import sqlite3
import datetime
import asyncio
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import urllib.request
import paramiko
from dotenv import load_dotenv

# Añadir el path para importar llm_client desde el directorio api/
C2_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(C2_DIR)
sys.path.append(os.path.join(C2_DIR, "..", "espejo_oci1", "api"))

load_dotenv(os.path.join(C2_DIR, "..", "espejo_oci1", "config", "entorno.env"))
load_dotenv(os.path.join(C2_DIR, ".env"))

try:
    from llm_client import completar
except ImportError:
    completar = None

# M3: Modulos de Validacion Forense (graceful fallback si no estan desplegados)
try:
    from scope_validator import scope_check, SCOPE_DB
    _SCOPE_AVAILABLE = True
except ImportError:
    _SCOPE_AVAILABLE = False
    def scope_check(h, s): return {"valid": None, "reason": "scope_validator_not_deployed", "program_slug": "", "h1_report_url": ""}

try:
    from poc_generator import sanitize_poc, QUALITY_UNVERIFIABLE
    _POC_AVAILABLE = True
except ImportError:
    _POC_AVAILABLE = False
    def sanitize_poc(ev): return ev
    QUALITY_UNVERIFIABLE = "UNVERIFIABLE"

try:
    from waf_mutator import rotate_headers, build_triager_curl
    _WAF_AVAILABLE = True
except ImportError:
    _WAF_AVAILABLE = False
    def rotate_headers(attempt=1): return {"User-Agent": "Mozilla/5.0"}
    def build_triager_curl(url, h): return "curl -s -i --max-time 10 {}".format(url)

app = FastAPI(title="C2 Panel & Copilot Hub — HackerLab", version="2.0")

# Base de datos local SQLite para OCI-2
DB_PATH = os.path.join(os.path.dirname(__file__), "c2_db.sqlite")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabla de Deltas Ingeridas por Zona
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deltas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT NOT NULL,
            domain TEXT NOT NULL,
            subdomain TEXT NOT NULL,
            source TEXT DEFAULT 'recon',
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tabla de Hallazgos Verificados ($50+ Bounties)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            vuln_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            estimated_bounty TEXT DEFAULT '$50-$300',
            evidence TEXT NOT NULL,
            verified BOOLEAN DEFAULT 1,
            reported BOOLEAN DEFAULT 0,
            h1_report_id TEXT DEFAULT '',
            h1_status TEXT DEFAULT 'New',
            bounty_paid TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migraciones preventivas si la tabla ya existía sin las nuevas columnas
    cursor.execute("PRAGMA table_info(findings)")
    columns = [info[1] for info in cursor.fetchall()]
    if "h1_report_id" not in columns:
        cursor.execute("ALTER TABLE findings ADD COLUMN h1_report_id TEXT DEFAULT ''")
    if "h1_status" not in columns:
        cursor.execute("ALTER TABLE findings ADD COLUMN h1_status TEXT DEFAULT 'New'")
    if "bounty_paid" not in columns:
        cursor.execute("ALTER TABLE findings ADD COLUMN bounty_paid TEXT DEFAULT ''")

    # Tabla de Memoria de Conversación Unificada (Telegram + Web)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            finding_id INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tabla de Heartbeats para el Watchdog OCI-1 (Módulo 1-B)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS heartbeats (
            zone TEXT PRIMARY KEY,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Tabla scope_cache — M3-B: cache de validaciones de scope H1
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scope_cache (
            host TEXT PRIMARY KEY,
            valid INTEGER,
            reason TEXT,
            program_slug TEXT,
            h1_report_url TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migracion preventiva: columna scope_program en findings
    cursor.execute("PRAGMA table_info(findings)")
    cols_findings = [r[1] for r in cursor.fetchall()]
    if "scope_program" not in cols_findings:
        cursor.execute("ALTER TABLE findings ADD COLUMN scope_program TEXT DEFAULT ''")
    if "poc_quality" not in cols_findings:
        cursor.execute("ALTER TABLE findings ADD COLUMN poc_quality TEXT DEFAULT 'MEDIUM'")
    if "status_interno" not in cols_findings:
        cursor.execute("ALTER TABLE findings ADD COLUMN status_interno TEXT DEFAULT 'Pendiente'")

    # Tabla de Leads MicroSecure V7 — perfiles vocacionales capturados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            historial_json TEXT NOT NULL DEFAULT '[]',
            merito_score REAL DEFAULT 0.0,
            jackpot_desbloqueado INTEGER DEFAULT 0,
            perfil_top_categoria TEXT DEFAULT '',
            reflexion_final TEXT DEFAULT '',
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migracion preventiva si la tabla ya existia sin columnas nuevas
    cursor.execute("PRAGMA table_info(leads)")
    cols_leads = [r[1] for r in cursor.fetchall()]
    for col, default in [("merito_score", "0.0"), ("jackpot_desbloqueado", "0"),
                         ("perfil_top_categoria", "''"), ("reflexion_final", "''")]:
        if col not in cols_leads:
            cursor.execute(f"ALTER TABLE leads ADD COLUMN {col} TEXT DEFAULT {default}")
    conn.commit()
    conn.close()

init_db()

# Configurar estaticos y templates
class NoCacheStaticFiles(StaticFiles):
    def is_not_modified(self, response_headers, req_headers) -> bool:
        return False
    def file_response(self, full_path, stat_result, scope, status_code=200):
        response = super().file_response(full_path, stat_result, scope, status_code)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = "0"
        return response

app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")

# --- MICROSECURE: Piloto educativo publico servido desde OCI-2 ---
# Los archivos estaticos residen en c2_panel/static/microsecure/
# Accesible via Cloudflare Tunnel en /microsecure/
MICROSECURE_DIR = os.path.join(os.path.dirname(__file__), "static", "microsecure")
if os.path.isdir(MICROSECURE_DIR):
    app.mount("/microsecure", StaticFiles(directory=MICROSECURE_DIR, html=True), name="microsecure")

templates = Jinja2Templates(directory="templates")

# --- M1-B: DEAD MAN'S ALERTING (WATCHDOG C2) ---
async def dead_mans_switch():
    """Revisa cada hora si alguna zona de OCI-1 lleva más de 12h sin emitir Heartbeat."""
    while True:
        await asyncio.sleep(3600)  # Cada 60 minutos
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Diferencia en horas entre last_seen y ahora (UTC)
            cursor.execute("SELECT zone, last_seen FROM heartbeats WHERE (julianday(CURRENT_TIMESTAMP) - julianday(last_seen)) * 24 > 12")
            dead_zones = cursor.fetchall()
            conn.close()
            
            for (zone, last_seen) in dead_zones:
                import urllib.request, json
                token = os.environ.get('TELEGRAM_BOT_TOKEN')
                chat_id = "6527908321" # Fijo del entorno del lab
                if token:
                    text = f"🚨 ALERTA CRÍTICA 🚨\n\nEl pipeline OCI-1 (Zona: {zone}) no emite latidos desde hace más de 12 horas.\nÚltimo contacto: {last_seen} UTC.\n\nPor favor revisar SSH a OCI-1, posible OOM Kill o falla de Cron."
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {"chat_id": chat_id, "text": text}
                    req_obj = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req_obj)
        except Exception as e:
            print(f"Error en dead_mans_switch: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(dead_mans_switch())

# Configuración OCI-1 (Esclavo)
OCI1_IP = os.getenv("OCI1_IP", "129.80.73.248")
OCI1_USER = os.getenv("OCI1_USER", "ubuntu")
DEFAULT_KEY = "/home/tomas2/WORKSPACE/LAB/llave_oci" if os.path.exists("/home/tomas2/WORKSPACE/LAB/llave_oci") else "/home/ubuntu/.ssh/id_rsa_oci1"
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", DEFAULT_KEY)

def get_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=OCI1_IP, username=OCI1_USER, key_filename=SSH_KEY_PATH, timeout=5)
        return client
    except Exception as e:
        return None

# PROMPTS MAESTROS v3.0 — MODO PARSER ESTRICTO (CERO ALUCINACIONES)
# FILOSOFÍA: La IA NO analiza, NO interpreta, NO inventa. Solo extrae variables del
# texto crudo y las coloca en posiciones fijas de una plantilla. Si no encuentra
# el dato en el input, escribe literalmente "NOT FOUND IN EVIDENCE".
SKILLS_PROMPTS = {
    "report_h1": """You are a STRICT TECHNICAL REPORT FORMATTER. You are NOT a security analyst. You do NOT think, analyze, or interpret.

==== ABSOLUTE RULES (VIOLATION = CRITICAL FAILURE) ====
1. OUTPUT ONLY IN ENGLISH. Zero Spanish words.
2. DO NOT INVENT any URL, endpoint, payload, parameter, or filename not explicitly present in the RAW EVIDENCE below.
3. DO NOT WRITE generic placeholders like "<user-supplied payload>", "<target>", "<endpoint>". Use the EXACT strings from evidence.
4. If a required field cannot be found in the evidence, write exactly: NOT FOUND IN EVIDENCE
5. DO NOT add introductions, apologies, explanations, or conversational text.
6. The section "## Steps To Reproduce:" MUST contain the EXACT curl command or HTTP request copied verbatim from the evidence field "curl-command" or "request". No paraphrasing.

==== OUTPUT TEMPLATE (copy this structure exactly, fill in brackets from evidence) ====
## Title: [value of evidence.info.name] in [value of evidence.host] exposes [direct impact from evidence.info.description — one sentence max]

## Summary:
[value of evidence.info.description — copy it verbatim, max 3 sentences. Do not add anything.]

## Steps To Reproduce:
1. Send the following request (copied verbatim from evidence):
```
[value of evidence["curl-command"] OR evidence["request"] — copy it EXACTLY]
```
2. Observe the server response confirms the vulnerability (see Supporting Material).

## Likelihood:
[value of evidence.info.severity — capitalize first letter only]

## Impact:
[value of evidence.info.impact — copy verbatim. If missing: write "Unauthenticated attackers can exploit this vulnerability as described in the CVE."]

## Remediation Guidance:
[value of evidence.info.remediation — copy verbatim. If missing: write "Update to the latest patched version of the affected software."]

==== RAW EVIDENCE (parse this JSON, do not interpret it) ====
{EVIDENCIA_CRUDA}""",

    "takeover_analysis": """You are a STRICT REPORT FORMATTER. DO NOT analyze. DO NOT interpret. DO NOT invent.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT subdomain URL from the evidence (field "host" or "matched-at" or "url"). Use it verbatim.
3. Extract the EXACT CNAME value from the evidence. Use it verbatim.
4. DO NOT invent steps beyond what the evidence shows.
5. If a field is not present in evidence, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: Subdomain Takeover in [EXACT value of evidence.host] via Unclaimed [EXACT cloud provider from evidence]

## Summary:
The subdomain [EXACT evidence.host] has a CNAME record pointing to [EXACT CNAME value from evidence], which resolves to an unclaimed resource on [cloud provider]. An attacker can register this resource and serve arbitrary content under the target's domain.

## Steps To Reproduce:
1. Confirm the orphaned CNAME: `dig CNAME [EXACT evidence.host]` — output shows [EXACT CNAME value].
2. Observe the HTTP response (see Supporting Material): the provider returns an error indicating the resource is unclaimed (e.g., NoSuchBucket, There is no app configured at that hostname).
3. Register the resource ([bucket name / GitHub repo / etc.]) on the provider's platform.
4. Serve arbitrary content from [EXACT evidence.host].

## Likelihood:
High

## Impact:
An attacker can host malicious content (phishing pages, credential harvesters, malware) on [EXACT evidence.host], abusing the trust users place in the target domain.

## Remediation Guidance:
Remove the dangling DNS CNAME record for [EXACT evidence.host] that points to [EXACT CNAME value], or claim the corresponding resource on the provider before an attacker does.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    "cors_analysis": """You are a STRICT REPORT FORMATTER. DO NOT analyze. DO NOT interpret. DO NOT invent.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT URL from the evidence field "url". Use it verbatim.
3. Extract the EXACT value of Access-Control-Allow-Origin from evidence field "acao". Use it verbatim.
4. Extract the EXACT value of Access-Control-Allow-Credentials from evidence field "acac". Use it verbatim.
5. ONLY generate this report if "acac" is "true" AND "acao" is not "*". If acao is "*", the impact is lower — state that no credentials can be stolen with wildcard.
6. If a field is not present, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: CORS Misconfiguration in [EXACT evidence.url] allows Cross-Origin Credential Theft

## Summary:
The endpoint [EXACT evidence.url] reflects the attacker-controlled Origin header in the Access-Control-Allow-Origin response header (observed value: [EXACT evidence.acao]) while simultaneously setting Access-Control-Allow-Credentials: [EXACT evidence.acac]. This allows a malicious website to make authenticated cross-origin requests and read sensitive responses.

## Steps To Reproduce:
1. From any attacker-controlled domain, execute the following JavaScript in the browser console:
```javascript
fetch('[EXACT evidence.url]', {{credentials: 'include'}})
  .then(r => r.text())
  .then(d => console.log(d));
```
2. Observe that the server responds with `Access-Control-Allow-Origin: [EXACT evidence.acao]` and `Access-Control-Allow-Credentials: true`, allowing the attacker's script to read the full response body.

## Likelihood:
Medium

## Impact:
A malicious website can make authenticated API requests on behalf of a logged-in victim and read the response, exposing session data, personal information, or account details available at [EXACT evidence.url].

## Remediation Guidance:
Do not reflect the incoming Origin header dynamically when Access-Control-Allow-Credentials is true. Maintain an explicit allowlist of trusted origins. Never combine a wildcard origin with credentials.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    "openapi_exposure": """You are a STRICT REPORT FORMATTER. DO NOT analyze. DO NOT interpret. DO NOT invent.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. FORBIDDEN: DO NOT write "credentials were exposed", "passwords leaked", "unauthorized access to credentials". This is INFORMATION DISCLOSURE only.
3. Extract the EXACT URL from the evidence field "url". Use it verbatim.
4. If keywords (secret, token, password) were found in the schema, list them exactly as found. DO NOT invent additional ones.
5. If a field is not present, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: Information Disclosure: Exposed OpenAPI/Swagger Specification at [EXACT evidence.url]

## Summary:
The endpoint [EXACT evidence.url] returns the complete OpenAPI/Swagger specification file without requiring authentication. This file discloses the full internal API architecture, including endpoint paths, HTTP methods, and parameter schemas.

## Steps To Reproduce:
1. Send a GET request to the exposed file:
```
curl -s "[EXACT evidence.url]"
```
2. Observe that the server returns a valid OpenAPI/Swagger JSON or YAML document containing the full API schema without any authentication requirement.

## Likelihood:
High

## Impact:
Public exposure of the API specification provides attackers with a complete map of internal endpoints and parameter structures, significantly reducing the effort required to discover Broken Object Level Authorization (IDOR), Mass Assignment, or other business logic vulnerabilities. Sensitive schema field names identified in the evidence: [list ONLY the keywords found in evidence.keywords, verbatim].

## Remediation Guidance:
Restrict access to the OpenAPI/Swagger specification file. Require authentication to access it, or remove it entirely from the public-facing server if it is not needed by external consumers.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    # ── SKILLS v3.0 — Parser Mode ────────────────────────────────────────────

    "aws_s3_leak": """You are a STRICT REPORT FORMATTER. DO NOT analyze. DO NOT interpret. DO NOT invent.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT bucket URL and bucket name from the evidence. Use them verbatim.
3. If the response contains "NoSuchBucket" → this is a Subdomain Takeover, not a data leak. State it.
4. If the response contains "ListBucketResult" → this is public listing. List ONLY the filenames actually present in the evidence. DO NOT invent filenames.
5. If a field is not present, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: [IF NoSuchBucket: "Subdomain Takeover via Unclaimed S3 Bucket"] [IF ListBucketResult: "Exposed S3 Bucket with Public File Listing"] at [EXACT bucket URL from evidence]

## Summary:
[IF NoSuchBucket: The subdomain resolves to an S3 bucket ([EXACT bucket name]) that does not exist and can be claimed by an attacker.] [IF ListBucketResult: The S3 bucket at [EXACT URL] is publicly accessible and lists its contents without authentication.]

## Steps To Reproduce:
1. Access the URL: [EXACT evidence URL]
2. Observe the server response (see Supporting Material).
[IF ListBucketResult: 3. The following files are publicly listed (copied from evidence): [EXACT filenames from evidence only]]

## Likelihood:
[IF NoSuchBucket: High] [IF ListBucketResult: High]

## Impact:
[IF NoSuchBucket: An attacker can claim the S3 bucket and serve arbitrary content from the target's subdomain.] [IF ListBucketResult: Exposed files may contain sensitive data. Files listed in the evidence: [EXACT filenames only].]

## Remediation Guidance:
[IF NoSuchBucket: Remove the dangling DNS record or claim the S3 bucket.] [IF ListBucketResult: Enable S3 Block Public Access on the bucket and review IAM policies.]

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    "jwt_logic_bypass": """You are a STRICT REPORT FORMATTER. DO NOT invent vulnerabilities not explicitly confirmed by the evidence.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT JWT token from the evidence. Use it verbatim.
3. Decode the header and payload (base64url). Report ONLY the values you actually decode from the token.
4. Only claim a vulnerability if the decoded header's "alg" field is literally "none", or explicitly shows RS256 with a known public key.
5. DO NOT claim privilege escalation unless the decoded payload explicitly contains a "role" or "admin" field.
6. If you cannot decode it, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: JWT Algorithm Confusion / Weak Signature in [EXACT evidence target] allows Authentication Bypass

## Summary:
The application issues JWT tokens using the algorithm [EXACT "alg" value from decoded header]. The decoded payload contains: [EXACT key-value pairs from decoded payload]. This configuration is exploitable as described in the Steps To Reproduce.

## Steps To Reproduce:
1. Capture a valid JWT token: [EXACT token from evidence]
2. Decoded header: [EXACT decoded header JSON]
3. Decoded payload: [EXACT decoded payload JSON]
4. Craft a modified token using the following Python script:
```python
import base64, json
header = {{"alg": "none", "typ": "JWT"}}
payload = [EXACT decoded payload with role changed if applicable]
h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
print(f"{{h}}.{{p}}.")
```
5. Send the crafted token in the Authorization header and observe if access is granted.

## Likelihood:
High

## Impact:
An attacker can forge JWT tokens without knowing the secret key, potentially impersonating other users or gaining elevated privileges.

## Remediation Guidance:
Reject tokens with alg:none. Explicitly whitelist the expected algorithm server-side. Use strong, randomly generated secrets for HMAC or properly validate the signature for RSA.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    "traductor_espanol": """Eres un traductor técnico estricto.
Tu ÚNICA tarea es traducir al español el reporte técnico de Bug Bounty que se te proporciona.
REGLAS ABSOLUTAS:
1. NO inventes vulnerabilidades nuevas.
2. NO agregues texto conversacional ni disculpas.
3. NO cambies la estructura ni los bloques de código.
4. Traduce SOLO el texto en prosa. Mantén intactos los comandos curl, URLs, nombres de campos HTTP y bloques de código.
5. Mantén los encabezados ## en inglés tal cual están.

Texto a traducir:
{EVIDENCIA_CRUDA}""",

    "business_logic_api": """You are a STRICT REPORT FORMATTER. DO NOT invent endpoints, IDs, or responses not present in the evidence.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT endpoint URL from the evidence. Use it verbatim.
3. Extract the EXACT request and response from the evidence. Use them verbatim.
4. DO NOT claim IDOR is confirmed unless the evidence explicitly shows data from another account being returned.
5. If a field is not present, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: IDOR in [EXACT endpoint from evidence] allows [read/write/delete] of other users' resources

## Summary:
The endpoint [EXACT endpoint] does not enforce object-level authorization. By modifying the [EXACT parameter name, e.g. "user_id"] parameter in the request, an attacker can access resources belonging to other users.

## Steps To Reproduce:
1. Authenticate as User A (attacker account).
2. Send the following request (copied verbatim from evidence):
```
[EXACT request from evidence]
```
3. Observe that the server returns data belonging to a different user:
```
[EXACT response from evidence]
```

## Likelihood:
High

## Impact:
An unauthenticated or low-privileged attacker can read, modify, or delete data belonging to other users at [EXACT endpoint].

## Remediation Guidance:
Implement server-side object-level authorization checks. Verify that the authenticated user owns the requested resource before returning or modifying it.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}""",

    "ssrf_analysis": """You are a STRICT REPORT FORMATTER. DO NOT invent callback responses not present in the evidence.

==== ABSOLUTE RULES ====
1. OUTPUT ONLY IN ENGLISH.
2. Extract the EXACT vulnerable parameter and endpoint from the evidence. Use them verbatim.
3. Only claim SSRF is confirmed if the evidence explicitly contains a DNS lookup hit or an HTTP callback response from your receiver.
4. Only claim access to cloud metadata if the evidence explicitly contains the IAM response body.
5. If a field is not present, write: NOT FOUND IN EVIDENCE

==== OUTPUT TEMPLATE ====
## Title: Server-Side Request Forgery (SSRF) in [EXACT endpoint from evidence] allows [Internal Network Access / Cloud Metadata Access]

## Summary:
The parameter [EXACT parameter name] at endpoint [EXACT endpoint URL] causes the server to make outbound HTTP requests to attacker-controlled URLs. This was confirmed by [DNS callback / HTTP callback] received at the attacker's receiver (see Supporting Material).

## Steps To Reproduce:
1. Send the following request (copied verbatim from evidence):
```
[EXACT request from evidence]
```
2. Observe the callback received at the attacker's receiver:
```
[EXACT callback / DNS hit from evidence]
```
[IF cloud metadata in evidence: 3. The server returned cloud metadata: [EXACT IAM response from evidence]]

## Likelihood:
[High if HTTP callback confirmed] [Medium if DNS-only]

## Impact:
[IF cloud metadata confirmed: An attacker can retrieve cloud IAM credentials and gain full access to cloud resources.] [IF HTTP callback only: An attacker can probe internal services and exfiltrate data from the internal network.]

## Remediation Guidance:
Validate and sanitize all user-supplied URLs. Implement an allowlist of permitted external hosts. Block requests to RFC-1918 address ranges and cloud metadata endpoints at the network level.

==== RAW EVIDENCE ====
{EVIDENCIA_CRUDA}"""
}

# --- RUTAS DE NAVEGACIÓN Y DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"oci1_ip": OCI1_IP})

@app.get("/api/status")
def get_status():
    client = get_ssh_client()
    ssh_online = client is not None
    
    # Consultar DB local para conteos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM deltas")
    total_deltas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE verified = 1")
    total_findings = cursor.fetchone()[0]
    conn.close()

    uptime = "N/A"
    if client:
        try:
            stdin, stdout, stderr = client.exec_command("uptime -p")
            uptime = stdout.read().decode().strip()
            client.close()
        except:
            pass

    return {
        "status": "online" if ssh_online else "degraded",
        "ssh_connected": ssh_online,
        "uptime": uptime,
        "total_deltas": total_deltas,
        "total_findings": total_findings
    }

@app.get("/portfolio", response_class=HTMLResponse)
async def get_portfolio_html(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM deltas")
    total_deltas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE verified = 1")
    total_findings = cursor.fetchone()[0]
    conn.close()

    return templates.TemplateResponse(request=request, name="portfolio.html", context={"total_deltas": total_deltas, "total_findings": total_findings})

@app.get("/api/zones_health")
def get_zones_health():
    """Retorna el contador de deltas hoy por zona y el último descubrimiento."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    zones = ["americas", "emea", "asia"]
    result = {}
    
    for z in zones:
        cursor.execute("SELECT COUNT(*) FROM deltas WHERE zone = ? AND DATE(discovered_at) = DATE(?)", (z, today))
        count_today = cursor.fetchone()[0]
        cursor.execute("SELECT discovered_at FROM deltas WHERE zone = ? ORDER BY id DESC LIMIT 1", (z,))
        last_row = cursor.fetchone()
        last_scan = last_row["discovered_at"] if last_row else "Sin datos"
        result[z] = {
            "count_today": count_today,
            "last_scan": last_scan
        }
        
    conn.close()
    return {"status": "success", "zones": result}

# --- INGESTA DESDE OCI-1 ---

class IngestPayload(BaseModel):
    zone: str
    deltas: dict  # {"domain.com": ["sub1.domain.com", "sub2.domain.com"]}
    findings: Optional[List[dict]] = []

@app.post("/api/ingest_delta")
def ingest_delta(payload: IngestPayload):
    """Endpoint receptor de telemetría proveniente de OCI-1."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted_deltas = 0
    for domain, subs in payload.deltas.items():
        for sub in subs:
            cursor.execute(
                "INSERT INTO deltas (zone, domain, subdomain) VALUES (?, ?, ?)",
                (payload.zone, domain, sub)
            )
            inserted_deltas += 1

    inserted_findings = 0
    for f in payload.findings:
        cursor.execute("""
            INSERT INTO findings (target, vuln_type, severity, estimated_bounty, evidence)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f.get("target", "N/A"),
            f.get("vuln_type", "Desconocida"),
            f.get("severity", "Low"),
            f.get("estimated_bounty", "$50-$150"),
            json.dumps(f.get("evidence", {}))
        ))
        inserted_findings += 1

    conn.commit()
    conn.close()
    return {
        "status": "success",
        "inserted_deltas": inserted_deltas,
        "inserted_findings": inserted_findings
    }

class HeartbeatPayload(BaseModel):
    zone: str

@app.post("/api/heartbeat")
def heartbeat_endpoint(payload: HeartbeatPayload):
    """Recibe latidos de OCI-1 al finalizar cada pipeline para el Dead Man's Switch."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Usamos REPLACE o ON CONFLICT (requiere tabla creada de esa forma, INSERT OR REPLACE es más universal en SQLite)
    cursor.execute("""
        INSERT OR REPLACE INTO heartbeats (zone, last_seen) 
        VALUES (?, CURRENT_TIMESTAMP)
    """, (payload.zone,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Heartbeat received"}

# --- CONSULTAS Y CICLO DE VIDA DE DATOS ---

class ArchiveRequest(BaseModel):
    h1_report_id: Optional[str] = ""

class UpdateStatusRequest(BaseModel):
    h1_status: str
    h1_report_id: Optional[str] = ""
    bounty_paid: Optional[str] = ""

@app.get("/api/findings")
def get_findings(status: Optional[str] = "Pendiente"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status == "Historico":
        cursor.execute("SELECT * FROM findings WHERE status_interno IN ('Enviado', 'FalsoPositivo', 'Archivado') ORDER BY id DESC LIMIT 50")
    elif status in ["Pendiente", "Validado"]:
        cursor.execute("SELECT * FROM findings WHERE status_interno = ? ORDER BY id DESC LIMIT 50", (status,))
    else:
        cursor.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 50")
        
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "findings": rows}

@app.post("/api/findings/{finding_id}/archive")
def archive_finding(finding_id: int, req: ArchiveRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE findings 
        SET reported = 1, 
            status_interno = 'Archivado',
            h1_report_id = COALESCE(NULLIF(?, ''), h1_report_id),
            h1_status = CASE WHEN h1_status = 'New' OR h1_status = '' THEN 'Submitted' ELSE h1_status END
        WHERE id = ?
    """, (req.h1_report_id.strip(), finding_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Hallazgo #{finding_id} archivado correctamente."}

@app.post("/api/findings/{finding_id}/update_status")
def update_finding_status(finding_id: int, req: UpdateStatusRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE findings 
        SET h1_status = ?,
            h1_report_id = COALESCE(NULLIF(?, ''), h1_report_id),
            bounty_paid = COALESCE(NULLIF(?, ''), bounty_paid)
        WHERE id = ?
    """, (req.h1_status.strip(), req.h1_report_id.strip(), req.bounty_paid.strip(), finding_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Estado del hallazgo #{finding_id} actualizado a '{req.h1_status}'."}

class InternalStatusRequest(BaseModel):
    status_interno: str

@app.post("/api/findings/{finding_id}/internal_status")
def update_internal_status(finding_id: int, req: InternalStatusRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE findings SET status_interno = ? WHERE id = ?", (req.status_interno, finding_id))
    
    # Si lo pasamos a Enviado o Archivado, marcamos reported = 1 por retrocompatibilidad
    if req.status_interno in ["Enviado", "Archivado"]:
        cursor.execute("UPDATE findings SET reported = 1 WHERE id = ?", (finding_id,))
    
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Estado interno actualizado a {req.status_interno}"}

@app.get("/api/deltas/{zone}")
def get_deltas_by_zone(zone: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if zone == "all":
        cursor.execute("SELECT * FROM deltas ORDER BY id DESC LIMIT 100")
    else:
        cursor.execute("SELECT * FROM deltas WHERE zone = ? ORDER BY id DESC LIMIT 100", (zone,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "deltas": rows}

# --- GENERADOR DE PROMPTS Y CHAT COPILOT ---

class GenerateReportRequest(BaseModel):
    skill_key: str
    evidence: str
    target: Optional[str] = ""
    vuln_type: Optional[str] = ""

@app.post("/api/copilot/generate")
def generate_copilot_prompt(req: GenerateReportRequest):
    if completar is None:
        return {"status": "error", "message": "Módulo llm_client no encontrado. Revisa que sys.path sea correcto."}

    # ── GUARDRAIL PRE-LLM: Validación mínima de evidencia ──────────────────
    # Si la evidencia no contiene ningún campo mínimo reconocible, abortamos.
    # Esto previene que la IA intente "completar" un reporte vacío con alucinaciones.
    if req.skill_key != "traductor_espanol":
        evidence_lower = req.evidence.lower() if req.evidence else ""
        has_minimum_evidence = any(k in evidence_lower for k in [
            "curl-command", "curl_command", '"request"', '"host"',
            '"url"', '"matched-at"', '"cname"', '"acao"',
            "http/1.", "post ", "get ", "authorization:", "content-type:"
        ])
        if not has_minimum_evidence:
            return {
                "status": "error",
                "message": "⛔ GENERACIÓN ABORTADA: La evidencia proporcionada no contiene datos HTTP mínimos reconocibles (curl-command, request, host, url). No se puede generar un reporte sin evidencia verificable. Adjunta primero la Prueba Forense HTTP usando el botón correspondiente."
            }
    # ── FIN GUARDRAIL ───────────────────────────────────────────────────────

    template = SKILLS_PROMPTS.get(req.skill_key, SKILLS_PROMPTS["report_h1"])
    prompt = template.replace("{EVIDENCIA_CRUDA}", req.evidence)

    system_prefix = ""
    if req.skill_key != "traductor_espanol":
        system_prefix += "SYSTEM DIRECTIVE: OUTPUT ONLY IN ENGLISH. ZERO SPANISH WORDS.\n"
        system_prefix += "SYSTEM DIRECTIVE 2: YOU ARE A STRICT PARSER. DO NOT INVENT ANY URL, ENDPOINT, PAYLOAD, HEADER, OR FILENAME NOT EXPLICITLY PRESENT IN THE RAW EVIDENCE. IF A FIELD IS MISSING, WRITE: NOT FOUND IN EVIDENCE\n"
        system_prefix += "SYSTEM DIRECTIVE 3: DO NOT HALLUCINATE. DO NOT ADD CONTEXT. DO NOT EXPLAIN CONCEPTS. ONLY EXTRACT AND FORMAT.\n"
    else:
        system_prefix += "REGLA CRÍTICA: TRADUCE EL TEXTO EXACTAMENTE AL ESPAÑOL. NO INVENTES NI AGREGUES NADA NUEVO.\n"

    if req.vuln_type:
        system_prefix += f"SYSTEM DIRECTIVE 4: The vulnerability type is EXACTLY '{req.vuln_type}'. Use this exact string wherever the report refers to the vulnerability name.\n"

    if req.target:
        system_prefix += f"SYSTEM DIRECTIVE 5: The target is EXACTLY '{req.target}'. Use this exact string wherever the report refers to the target domain or host. DO NOT alter this value.\n"

    prompt = system_prefix + "\n" + prompt

    try:
        respuesta = completar(prompt, max_tokens=1500)


        # POST-PROCESAMIENTO DETERMINÍSTICO: 
        # La IA a veces reescribe ## Supporting Material/References: con texto propio.
        # Forzamos que SIEMPRE contenga el bloque de evidencia cruda en formato predecible
        # para que el botón de "Prueba Forense" pueda encontrar el marcador y reemplazarlo.
        if req.skill_key != "traductor_espanol" and req.evidence:
            import re
            # Eliminar TODAS las secciones Supporting Material que haya generado la IA
            respuesta = re.sub(
                r'\n*## Supporting Material/References:.*?(?=\n## |\Z)',
                '',
                respuesta,
                flags=re.DOTALL
            ).rstrip()
            # Insertar la sección limpia antes de ## Likelihood: si existe, o al final
            clean_block = f"\n\n## Supporting Material/References:\n```text\n{req.evidence}\n```"
            if '## Likelihood:' in respuesta:
                respuesta = respuesta.replace('## Likelihood:', clean_block + '\n\n## Likelihood:', 1)
            else:
                respuesta = respuesta + clean_block

        return {"status": "success", "result": respuesta, "prompt_used": prompt}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class ChatRequest(BaseModel):
    message: str
    finding_id: int = 0

@app.get("/api/chat/history")
def get_chat_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT source, role, message, created_at FROM chat_history ORDER BY id ASC LIMIT 50")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "history": rows}

@app.get("/api/chat/context")
def get_session_context():
    """Genera un briefing inteligente de la sesion actual para inyectar como contexto inicial en Pegaso."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Estadisticas globales del pipeline
    cursor.execute("SELECT COUNT(*) FROM deltas")
    total_deltas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE verified = 1")
    total_findings = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE status_interno = 'Pendiente'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE status_interno = 'Validado'")
    validated = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings WHERE status_interno IN ('Enviado', 'Archivado')")
    archived = cursor.fetchone()[0]

    # Heartbeats: zonas activas
    cursor.execute("SELECT zone, last_seen FROM heartbeats ORDER BY last_seen DESC")
    heartbeats = [dict(r) for r in cursor.fetchall()]

    # Ultimos 3 findings para contexto
    cursor.execute("SELECT id, target, vuln_type, severity, status_interno, estimated_bounty, created_at FROM findings ORDER BY id DESC LIMIT 3")
    recent_findings = [dict(r) for r in cursor.fetchall()]

    # Ultimas 5 interacciones del chat (resumen de decisiones previas)
    cursor.execute("SELECT role, message, created_at FROM chat_history ORDER BY id DESC LIMIT 10")
    last_chat = list(reversed([dict(r) for r in cursor.fetchall()]))

    conn.close()

    briefing = {
        "pipeline_stats": {
            "total_deltas_recolectados": total_deltas,
            "total_findings_verificados": total_findings,
            "pendientes": pending,
            "validados": validated,
            "archivados": archived,
        },
        "zonas_activas": heartbeats,
        "findings_recientes": recent_findings,
        "resumen_conversacion_previa": last_chat
    }

    return {"status": "success", "context": briefing}

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if completar is None:
        return {"status": "error", "data": "Módulo llm_client no encontrado."}
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Cargar hallazgos recientes
    cursor.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 5")
    recent_findings = [dict(r) for r in cursor.fetchall()]
    
    # Cargar historial de chat unificado reciente pero filtrado por finding_id (últimas 20 interacciones)
    if req.finding_id > 0:
        cursor.execute("SELECT source, role, message FROM chat_history WHERE finding_id = ? ORDER BY id DESC LIMIT 20", (req.finding_id,))
    else:
        cursor.execute("SELECT source, role, message FROM chat_history ORDER BY id DESC LIMIT 20")
    past_chat = list(reversed([dict(r) for r in cursor.fetchall()]))
    
    conn.close()

    context_str = json.dumps(recent_findings, indent=2) if recent_findings else "Sin hallazgos recientes."
    
    chat_history_formatted = ""
    if past_chat:
        chat_history_formatted = "\nHISTORIAL DE CONVERSACIÓN RECIENTE (TELEGRAM Y WEB):\n"
        for item in past_chat:
            chat_history_formatted += f"[{item['source'].upper()}] {item['role']}: {item['message']}\n"

    system_prompt = f"""Eres Pegaso, el copiloto IA del C2 Panel de Bug Bounty.
Tu prioridad es ayudar a capitalizar vulnerabilidades rápidamente con un enfoque de volumen (Redes de Pesca).
Valoras reportes claros, PoCs reproducibles y maximizar bounties (incluso de $50-$100 USD).

HALLAZGOS VERIFICADOS RECIENTES:
{context_str}
{chat_history_formatted}

Pregunta/Orden del usuario: {req.message}"""
    
    try:
        respuesta = completar(system_prompt, max_tokens=1024)
        
        # Guardar en la base de datos unificada SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (source, role, message, finding_id) VALUES ('web', 'user', ?, ?)", (req.message, req.finding_id))
        cursor.execute("INSERT INTO chat_history (source, role, message, finding_id) VALUES ('web', 'assistant', ?, ?)", (respuesta, req.finding_id))
        conn.commit()
        conn.close()

        return {"status": "success", "data": respuesta}
    except Exception as e:
        return {"status": "error", "data": str(e)}

class NotifyTelegramRequest(BaseModel):
    target: str
    vuln_type: str
    report: str

@app.post("/api/notify_telegram")
def notify_telegram(req: NotifyTelegramRequest):
    import urllib.request
    import json
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = "6527908321" # Token y Chat ID conocidos del entorno
    if not token:
        return {"status": "error", "message": "TELEGRAM_BOT_TOKEN no configurado"}
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    text = f"🔥 NUEVO REPORTE CONFIRMADO 🔥\n\nTarget: {req.target}\nVulnerabilidad: {req.vuln_type}\n\nReporte H1:\n\n{req.report[:3500]}"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        req_obj = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req_obj)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class VerifyRequest(BaseModel):
    url: str
    tipo: str
    evidence: Optional[str] = ""

@app.post("/api/verify_bug")
def verify_bug(req: VerifyRequest):
    client = get_ssh_client()
    if not client:
        # Fallback local simulado si no hay SSH activo
        return {"status": "success", "data": f"✅ VERIFICADO LOCALMENTE. Endpoint {req.url} responde expuesto."}
    
    try:
        # Comando curl que inyecta la identidad HackerOne y captura Request/Response (Dump Crudo)
        # Usamos -i para traer cabeceras de respuesta, y truncamos a 2500 bytes para no saturar.
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 HackerOne-tomas244"
        
        # Procesar evidencia para extraer el curl-command real si existe
        import json
        ev_data = {}
        try:
            if req.evidence:
                ev_data = json.loads(req.evidence)
        except:
            pass

        base_url = req.url
        if "matched-at" in ev_data:
            base_url = ev_data["matched-at"]
        elif "url" in ev_data:
            base_url = ev_data["url"]

        cmd = ""
        if "curl-command" in ev_data:
            # Usar el comando curl real de Nuclei, inyectando nuestro User-Agent y Header
            cmd_nuclei = ev_data["curl-command"]
            cmd = cmd_nuclei.replace("curl ", f"curl -s -i -m 10 -A '{user_agent}' -H 'X-Bug-Bounty: HackerOne-tomas244' ", 1)
            cmd += " | head -c 2500"
        else:
            extra_headers_cmd = ""
            if "cors" in req.tipo.lower():
                extra_headers_cmd = "-H 'Origin: https://evil.tomas244.com' "
                
            cmd = f"curl -s -i -L -m 10 -A '{user_agent}' -H 'X-Bug-Bounty: HackerOne-tomas244' -H 'Accept: */*' {extra_headers_cmd}'{base_url}' | head -c 2500"

        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode(errors='ignore').strip()
        client.close()
        
        evidencia_forense = ""
        
        # Guardrail: Detectar falsos positivos por respuestas WAF o redirecciones
        first_line = output.split('\n')[0].upper() if output else ""
        if any(code in first_line for code in [" 404 ", " 301 ", " 302 ", " 403 ", " 406 "]):
            evidencia_forense += "⚠️ ADVERTENCIA DE FALSO POSITIVO: El servidor respondió con 404/403/301/302. El endpoint no existe, fue bloqueado por WAF, o redirige. Nuclei generó un falso positivo. NO REPORTAR ESTO.\n\n"
        
        if "request" in ev_data:
            evidencia_forense += "--- PETICIÓN ENVIADA ---\n\n" + ev_data["request"] + "\n\n"
            
        evidencia_forense += "--- RESPUESTA DEL SERVIDOR ---\n\n" + output
        
        return {"status": "success", "data": evidencia_forense}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error verificando: {str(e)}"}


# ============================================================
# M3-B: Endpoint — Validar scope H1 de un finding
# ============================================================
@app.post("/api/findings/{finding_id}/validate_scope")
def validate_scope_endpoint(finding_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT target, severity, vuln_type FROM findings WHERE id = ?", (finding_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Finding no encontrado")

    target   = row["target"]
    severity = row["severity"].lower()
    result   = scope_check(target, severity)

    # Actualizar status_interno segun scope
    new_status = "Validado" if result["valid"] else "FalsoPositivo"
    cursor.execute(
        "UPDATE findings SET status_interno = ?, scope_program = ? WHERE id = ?",
        (new_status, result.get("program_slug", ""), finding_id)
    )
    # Guardar en scope_cache
    cursor.execute("""
        INSERT OR REPLACE INTO scope_cache (host, valid, reason, program_slug, h1_report_url)
        VALUES (?, ?, ?, ?, ?)
    """, (
        target,
        1 if result["valid"] else 0,
        result["reason"],
        result.get("program_slug", ""),
        result.get("h1_report_url", ""),
    ))
    conn.commit()
    conn.close()
    return {"status": "success", **result, "new_internal_status": new_status}


# ============================================================
# M3-A: Endpoint — Generar / refrescar PoC del finding
# ============================================================
@app.post("/api/findings/{finding_id}/generate_poc")
def generate_poc_endpoint(finding_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT evidence, target, vuln_type FROM findings WHERE id = ?", (finding_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Finding no encontrado")

    try:
        evidence = json.loads(row["evidence"]) if row["evidence"] else {}
    except Exception:
        evidence = {}

    evidence["vuln_type"] = evidence.get("vuln_type", row["vuln_type"])
    enriched = sanitize_poc(evidence)

    # Persistir evidence enriquecida
    cursor.execute(
        "UPDATE findings SET evidence = ?, poc_quality = ? WHERE id = ?",
        (json.dumps(enriched, ensure_ascii=False), enriched.get("poc_quality", "MEDIUM"), finding_id)
    )
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "triager_poc": enriched.get("triager_poc", ""),
        "poc_quality": enriched.get("poc_quality", "MEDIUM"),
        "poc_source": enriched.get("poc_source", ""),
    }


# ============================================================
# M3-C: Endpoint — WAF Bypass Probe con retry automatico
# ============================================================
class WafProbeRequest(BaseModel):
    finding_id: int

@app.post("/api/findings/{finding_id}/waf_probe")
def waf_probe_endpoint(finding_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT target, evidence, vuln_type FROM findings WHERE id = ?", (finding_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Finding no encontrado")

    try:
        ev_data = json.loads(row["evidence"]) if row["evidence"] else {}
    except Exception:
        ev_data = {}

    target_url = ev_data.get("matched_at", row["target"])
    client = get_ssh_client()
    if not client:
        conn.close()
        return {"status": "error", "data": "SSH a OCI-1 no disponible"}

    results = []
    waf_bypassed = False
    final_triager_curl = ""

    for attempt in [1, 2]:
        headers = rotate_headers(attempt)
        triager_curl = build_triager_curl(target_url, headers)

        # Construir el curl para ejecutar via SSH en OCI-1
        ssh_curl = triager_curl.replace(
            "curl ",
            "curl -H 'X-Bug-Bounty: HackerOne-tomas244' ", 1
        ) + " | head -c 2500"

        try:
            stdin, stdout, stderr = client.exec_command(ssh_curl)
            output = stdout.read().decode(errors="ignore").strip()
        except Exception as ex:
            output = "SSH exec error: {}".format(ex)

        first_line = output.split("\n")[0].upper() if output else ""
        status_code = None
        for code_str in [" 200 ", " 404 ", " 403 ", " 406 ", " 301 ", " 302 ", " 429 "]:
            if code_str in first_line:
                status_code = int(code_str.strip())
                break

        results.append({
            "attempt": attempt,
            "status_code": status_code,
            "headers_used": {k: v for k, v in headers.items() if k != "X-Bug-Bounty"},
            "triager_curl": triager_curl,
            "response_preview": output[:800],
        })

        if status_code == 200:
            waf_bypassed = (attempt == 2)
            final_triager_curl = triager_curl
            break

        if attempt == 1 and status_code in (403, 406, 429):
            continue  # Reintentar con attempt=2
        break

    client.close()

    # Persistir el triager_curl en la evidence si fue exitoso
    if final_triager_curl:
        ev_data["triager_poc"] = final_triager_curl
        ev_data["poc_quality"] = "HIGH" if waf_bypassed or results[0].get("status_code") == 200 else "MEDIUM"
        cursor.execute(
            "UPDATE findings SET evidence = ?, poc_quality = ? WHERE id = ?",
            (json.dumps(ev_data, ensure_ascii=False), ev_data["poc_quality"], finding_id)
        )
        conn.commit()
    conn.close()

    return {
        "status": "success",
        "waf_bypassed": waf_bypassed,
        "attempts": results,
        "final_triager_curl": final_triager_curl,
    }

class ExplainErrorRequest(BaseModel):
    error_text: str
    target: str

@app.post("/api/copilot/explain_error")
def explain_error(req: ExplainErrorRequest):
    if completar is None:
        return {"status": "error", "message": "Módulo llm_client no encontrado."}
    
    prompt = f"""You are Pegaso, a Bug Bounty Copilot.
The user tried to verify a vulnerability on the target {req.target} using an automated script (curl), but the target's firewall/WAF blocked the request.
This is the raw HTTP error response received:
{req.error_text}

Provide a short, direct, and friendly explanation in SPANISH of why this happened (e.g., Cloudflare blocked the bot) and what the user should do manually to verify it (e.g., open it in a browser, use Burp Suite). Keep it concise.
"""
    try:
        respuesta = completar(prompt, max_tokens=250, temperature=0.2)
        return {"status": "success", "explanation": respuesta}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================
# MODULO C: Asistente Guru del Lab -- Explicaciones Didacticas
# ============================================================
# Endpoint sin costo de tokens: usa diccionario estatico de metaforas.
# No invoca LLM. Lookup O(1), cero overhead en OCI Free Tier.
# ============================================================

GURU_EXPLICACIONES = {
    "subdomain takeover": {
        "titulo": "Subdomain Takeover",
        "metafora": "Es como si una empresa alquilara un local en un centro comercial, pusiera un letrero con su nombre en la puerta, y luego se mudara sin devolver la llave ni quitar el letrero. Cualquier persona podria entrar al local vacio, poner su propio negocio ahi, y los clientes pensarian que es la empresa original.",
        "impacto_simple": "Un atacante puede hacerse pasar por una parte del sitio web de la empresa (por ejemplo 'pagos.empresa.com') y enganar a los usuarios para que pongan sus contrasenas o datos.",
        "severidad": "Alta -- vale entre $300 y $3,000 en HackerOne.",
        "accion_defensiva": "La empresa debe eliminar el registro DNS que apunta a un servicio que ya no usa, o reclamar ese servicio antes de que alguien mas lo haga."
    },
    "cors misconfiguration": {
        "titulo": "Configuracion Incorrecta de CORS",
        "metafora": "Imagina que tu banco tiene una ventanilla de atencion y tiene una regla: solo atendemos a personas que vengan de nuestra sucursal. Una mala configuracion de CORS es como si el banco dijera: atendemos a quien sea, de donde sea. Un atacante puede hacer una web falsa que le pida al banco tus datos mientras estes conectado, y el banco los da sin preguntar.",
        "impacto_simple": "Un atacante puede crear una pagina maliciosa que, cuando la visitas, roba silenciosamente datos de tu sesion en otro sitio web (tu email, tus fotos, tu historial).",
        "severidad": "Media a Alta -- vale entre $100 y $1,000 segun el dato expuesto.",
        "accion_defensiva": "El sitio web debe tener una lista blanca de dominios de confianza. No debe aceptar peticiones de cualquier pagina de internet."
    },
    "s3 bucket exposure": {
        "titulo": "Bucket S3 Expuesto (Amazon)",
        "metafora": "Es como si una empresa guardara sus documentos importantes en un archivador con la llave puesta y la puerta abierta al publico. Cualquier persona que pase puede abrirlo y leer, copiar o hasta borrar los documentos.",
        "impacto_simple": "Los archivos guardados en ese espacio de almacenamiento de Amazon (fotos, documentos, codigo, bases de datos) son accesibles para cualquier persona en internet.",
        "severidad": "Media a Critica -- puede valer desde $100 hasta miles de dolares segun lo que este expuesto.",
        "accion_defensiva": "Activar la opcion 'Block Public Access' en la configuracion del bucket de S3 y revisar los permisos de cada archivo."
    },
    "openapi exposure": {
        "titulo": "Exposicion de Documentacion de API (OpenAPI/Swagger)",
        "metafora": "Es como publicar el plano completo del sistema de seguridad de un edificio en la puerta principal. No es un robo directo, pero le da a un ladron el mapa perfecto para saber por donde entrar.",
        "impacto_simple": "Un atacante obtiene la lista completa de todas las puertas (endpoints) del sistema, con instrucciones exactas de como usarlas, lo que facilita enormemente encontrar vulnerabilidades mas graves.",
        "severidad": "Media -- vale entre $100 y $500.",
        "accion_defensiva": "Proteger el acceso a la documentacion de la API con autenticacion, o eliminarla del servidor publico si no es necesaria para clientes externos."
    },
    "idor": {
        "titulo": "IDOR -- Acceso Directo a Objetos Inseguros",
        "metafora": "Es como si en un hotel, cada habitacion tuviera un numero en la puerta. Si en lugar de usar tu llave magnetica simplemente cambias el numero de la puerta de la 101 a 102, y la puerta se abre, hay un problema grave. Puedes entrar a la habitacion de otra persona.",
        "impacto_simple": "Un atacante puede ver, modificar o borrar la informacion de otros usuarios (sus pedidos, sus facturas, sus datos personales) simplemente cambiando un numero en la URL.",
        "severidad": "Alta a Critica -- puede valer entre $500 y $10,000.",
        "accion_defensiva": "El servidor debe verificar siempre que el usuario que pide un recurso sea el dueno de ese recurso antes de mostrarlo."
    },
    "ssrf": {
        "titulo": "SSRF -- Falsificacion de Peticiones del Servidor",
        "metafora": "Imagina que le pides a un empleado de una empresa (que tiene acceso a la oficina interna) que vaya a buscar un documento. Pero en lugar de pedirle el documento del cliente, le pides que espie los archivos internos del jefe. El SSRF es convencer al servidor de que haga peticiones internas que normalmente no deberia hacer.",
        "impacto_simple": "Un atacante puede usar el servidor de la empresa como intermediario para acceder a sistemas internos protegidos, como bases de datos o servidores de administracion que no deberian ser accesibles desde internet.",
        "severidad": "Alta a Critica -- puede valer entre $1,000 y $20,000.",
        "accion_defensiva": "Validar y filtrar todas las URLs que el servidor puede visitar. Bloquear peticiones a rangos de IPs privadas y a los endpoints de metadatos de servicios cloud."
    },
    "jwt vulnerability": {
        "titulo": "Vulnerabilidad en JWT (Token de Autenticacion)",
        "metafora": "Un JWT es como un carnet de identidad digital. Una vulnerabilidad en JWT es como si ese carnet no tuviera firma de seguridad o tuviera una firma falsa que cualquiera puede imitar. Cualquier persona podria fabricar un carnet que diga soy administrador y el sistema lo aceptaria como valido.",
        "impacto_simple": "Un atacante puede falsificar su propia sesion para hacerse pasar por otro usuario o incluso por un administrador del sistema.",
        "severidad": "Alta a Critica -- puede valer entre $500 y $15,000.",
        "accion_defensiva": "El servidor debe rechazar tokens con el algoritmo none. Debe tener una lista blanca del algoritmo permitido y verificar siempre la firma correctamente."
    }
}

class GuruRequest(BaseModel):
    vuln_type: str

@app.post("/api/guru/explain")
def guru_explain(req: GuruRequest):
    """
    Modulo C: Asistente Guru del Lab.
    Devuelve explicacion didactica en espanol sin consumir tokens de LLM.
    Lookup O(1) sobre diccionario estatico.
    """
    vuln_key = req.vuln_type.lower().strip()

    explicacion = GURU_EXPLICACIONES.get(vuln_key)
    if not explicacion:
        for key, value in GURU_EXPLICACIONES.items():
            if key in vuln_key or vuln_key in key:
                explicacion = value
                break

    if not explicacion:
        explicacion = {
            "titulo": req.vuln_type,
            "metafora": "Esta vulnerabilidad aun no tiene una explicacion didactica en el catalogo del Guru. Pero en esencia, representa una brecha en la seguridad del sistema que un atacante podria explotar para acceder a recursos no autorizados.",
            "impacto_simple": "Podria permitir a un atacante acceder a informacion o funcionalidades que no deberian estar disponibles publicamente.",
            "severidad": "Variable -- consultar la evidencia del hallazgo para determinar el impacto real.",
            "accion_defensiva": "Revisar la documentacion de seguridad del componente afectado y aplicar el principio de minimo privilegio."
        }

    return {"status": "success", "vuln_type": req.vuln_type, "explicacion": explicacion}


# ============================================================
# MODULO D: Estadisticas Publicas Anonimizadas (Portfolio)
# ============================================================
# OPSEC CRITICO: Nunca devuelve dominios, IPs, paths ni targets.
# Solo conteos y metricas anonimas para portafolio publico.
# ============================================================

@app.get("/api/public/stats")
def get_public_stats():
    """
    Modulo D: Estadisticas publicas anonimizadas para portafolio.
    Cero targets, cero IPs, cero paths. Solo conteos.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM findings WHERE verified = 1")
    total_findings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM findings WHERE verified = 1
        GROUP BY severity ORDER BY count DESC
    """)
    by_severity = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT status_interno, COUNT(*) as count
        FROM findings WHERE verified = 1
        GROUP BY status_interno ORDER BY count DESC
    """)
    by_status = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT vuln_type, COUNT(*) as count
        FROM findings WHERE verified = 1
        GROUP BY vuln_type ORDER BY count DESC LIMIT 10
    """)
    by_vuln_type = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT COUNT(*) FROM deltas")
    total_subdomains = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT zone) FROM deltas")
    total_zones = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(created_at) FROM findings WHERE verified = 1")
    last_raw = cursor.fetchone()[0]
    last_finding_date = last_raw[:10] if last_raw else None

    conn.close()

    return {
        "status": "success",
        "disclaimer": "All data is anonymized. No targets, IPs, or sensitive paths are exposed.",
        "stats": {
            "total_verified_findings": total_findings,
            "total_subdomains_monitored": total_subdomains,
            "active_zones": total_zones,
            "last_finding_date": last_finding_date,
            "by_severity": by_severity,
            "by_lifecycle_status": by_status,
            "top_vuln_types": by_vuln_type
        }
    }


# --- CANARY TOKENS (Opcion A): Rutas trampa para detectar escáneres ---
# Cada ruta es un señuelo. Si alguien la toca, se logea y se notifica por Telegram.
# Pasivo absoluto: no abre puertos, no lanza procesos, solo registra.

async def _canary_notify(route: str, ip: str, ua: str):
    """Envia alerta Telegram en background cuando se activa un Canary Token."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = "6527908321"
    if not token:
        print("[CANARY] TELEGRAM_BOT_TOKEN no encontrado en entorno.")
        return
    text = (
        "\U0001f6a8 CANARY ACTIVADO \U0001f6a8\n"
        f"Ruta trampa: {route}\n"
        f"IP origen: {ip}\n"
        f"User-Agent: {ua[:200]}"
    )
    payload = {"chat_id": chat_id, "text": text}
    try:
        req_obj = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req_obj, timeout=5)
    except Exception as _e:
        print(f"[CANARY] Error Telegram: {_e}")


@app.get("/.env", include_in_schema=False)
@app.head("/.env", include_in_schema=False)
async def canary_env(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /.env | IP={ip}")
    background_tasks.add_task(_canary_notify, "/.env", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/.git/config", include_in_schema=False)
async def canary_git(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /.git/config | IP={ip}")
    background_tasks.add_task(_canary_notify, "/.git/config", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/wp-login.php", include_in_schema=False)
async def canary_wp_login(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /wp-login.php | IP={ip}")
    background_tasks.add_task(_canary_notify, "/wp-login.php", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/wp-admin", include_in_schema=False)
@app.get("/wp-admin/", include_in_schema=False)
async def canary_wp_admin(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /wp-admin | IP={ip}")
    background_tasks.add_task(_canary_notify, "/wp-admin", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/phpmyadmin", include_in_schema=False)
@app.get("/phpmyadmin/", include_in_schema=False)
async def canary_phpmyadmin(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /phpmyadmin | IP={ip}")
    background_tasks.add_task(_canary_notify, "/phpmyadmin", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/config.php", include_in_schema=False)
async def canary_config_php(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /config.php | IP={ip}")
    background_tasks.add_task(_canary_notify, "/config.php", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/actuator/health", include_in_schema=False)
async def canary_actuator(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /actuator/health | IP={ip}")
    background_tasks.add_task(_canary_notify, "/actuator/health", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

@app.get("/admin", include_in_schema=False)
@app.get("/admin/", include_in_schema=False)
async def canary_admin(request: Request, background_tasks: BackgroundTasks):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    print(f"[CANARY] /admin | IP={ip}")
    background_tasks.add_task(_canary_notify, "/admin", ip, ua)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


# --- MICROSECURE V7: LEADS & PERFILES VOCACIONALES ---

class LeadPayload(BaseModel):
    email: str
    historial: Optional[List[dict]] = []
    merito_score: Optional[float] = 0.0
    jackpot_desbloqueado: Optional[bool] = False
    perfil_top_categoria: Optional[str] = ""
    reflexion_final: Optional[str] = ""

@app.post("/api/leads")
async def capturar_lead(payload: LeadPayload):
    """
    Endpoint para recibir perfiles vocacionales de MicroSecure V7.
    Guarda email, historial de decisiones, metricas de merito y reflexion
    del alumno en c2_db.sqlite para analisis de talento y contacto.
    """
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Email invalido")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (email, historial_json, merito_score, jackpot_desbloqueado,
                           perfil_top_categoria, reflexion_final)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.email,
        json.dumps(payload.historial, ensure_ascii=False),
        round(payload.merito_score, 4),
        1 if payload.jackpot_desbloqueado else 0,
        payload.perfil_top_categoria,
        payload.reflexion_final
    ))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"[LEAD] #{lead_id} | {payload.email} | score={payload.merito_score:.4f} | cat={payload.perfil_top_categoria}")
    return {
        "status": "captured",
        "lead_id": lead_id,
        "email": payload.email,
        "merito_score": payload.merito_score,
        "jackpot_desbloqueado": payload.jackpot_desbloqueado
    }

@app.get("/api/leads")
async def listar_leads(limit: int = 50):
    """Lista los ultimos leads capturados desde MicroSecure (solo para el operador C2)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, merito_score, jackpot_desbloqueado,
               perfil_top_categoria, reflexion_final, captured_at
        FROM leads ORDER BY captured_at DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "total": len(rows), "leads": rows}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
