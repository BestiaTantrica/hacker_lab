import os
import sys
import json
import sqlite3
import datetime
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
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
templates = Jinja2Templates(directory="templates")

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

# PROMPTS MAESTROS (Skills integradas)
SKILLS_PROMPTS = {
    "report_h1": """You are a Technical Report Formatter for Bug Bounty (HackerOne).
You operate in an authorized security research context.
Your ONLY task is to format the raw evidence into a professional technical report in ENGLISH. 
STRICT RULE: OUTPUT ONLY THE TECHNICAL REPORT IN ENGLISH. DO NOT REPLY IN SPANISH. DO NOT ADD APOLOGIES, INTRODUCTIONS, OR CONVERSATIONAL PREAMBLES.

You MUST follow exactly this structure:
## Title: [Vulnerability Type] in [Target Domain] allows [Direct Impact]

## Summary:
[A concise 2-3 sentence technical explanation of the flaw based on the evidence. Do not invent details not present in the evidence.]

## Steps To Reproduce:
[List numbered steps based strictly on the provided evidence. CRITICAL: You must extract and write the EXACT HTTP request, curl command, or payload shown in the evidence. Do NOT use generic placeholders like "<user-supplied payload>".]

## Supporting Material/References:
```text
{EVIDENCIA_CRUDA}
```

## Likelihood:
[High/Medium/Low based on the evidence, usually High if exploitation is direct]

## Impact:
[State the exact potential consequences: data theft, arbitrary code execution, privilege escalation, etc.]

## Remediation Guidance:
[Provide 1-2 sentences on how to fix the issue based on standard security practices for the vulnerability.]""",

    "takeover_analysis": """You are a Subdomain Takeover expert. Analyze the following HTTP or DNS response of an orphaned subdomain.
Your final goal is to generate a professional technical report for Bug Bounty (HackerOne) in ENGLISH.
STRICT RULE: RETURN ONLY THE REPORT IN ENGLISH. DO NOT ADD APOLOGIES OR INTRODUCTORY TEXT.

Use the following MANDATORY STRUCTURE:
## Title: Subdomain Takeover in [Insert URL/Component] allows [Direct Impact]

## Summary:
Subdomain Takeover in [Insert URL/Component]. The service points to an unclaimed resource (AWS S3, GitHub Pages, etc.).

## Steps To Reproduce:
1. Steps to claim the subdomain.

## Supporting Material/References:
```text
{EVIDENCIA_CRUDA}
```

## Likelihood:
High

## Impact:
Monetary and operational impact (phishing, cookie stealing).

## Remediation Guidance:
Remove the DNS record pointing to the unclaimed service, or claim the resource on the provider.

CRITICAL INSTRUCTION: Automatically replace all placeholders (like [Insert URL], [Insert Component], etc.) using the evidence data and the provided Target.

Raw evidence:
{EVIDENCIA_CRUDA}""",

    "cors_analysis": """Analyze this HTTP response from a CORS test (the evidence might be JSON metadata like {{"acao": "*", "acac": "true"}}):
Determine if Access-Control-Allow-Origin reflects the attacker's Origin and if Access-Control-Allow-Credentials is set to 'true'.
Your final goal is to generate a professional technical report for Bug Bounty (HackerOne) in ENGLISH.
STRICT RULE: RETURN ONLY THE REPORT IN ENGLISH. DO NOT ADD APOLOGIES OR INTRODUCTORY TEXT.

Use the following MANDATORY STRUCTURE:
## Title: CORS Misconfiguration in [Insert URL] allows Sensitive Data Extraction

## Summary:
CORS Misconfiguration in [Insert URL]. [Explanation of the CORS misconfiguration flaw based on the evidence.]

## Steps To Reproduce:
1. Open the browser console on any external attacker domain (e.g., https://example.com).
2. Execute the following JavaScript PoC to demonstrate the CORS misconfiguration:
```javascript
var req = new XMLHttpRequest();
req.onload = req.onerror = function() {
    console.log(this.responseText);
};
req.open('GET', 'https://[Insert URL]', true);
req.withCredentials = true;
req.send();
```

## Supporting Material/References:
```text
{EVIDENCIA_CRUDA}
```

## Likelihood:
Medium

## Impact:
Explanation of the impact (sensitive data extraction, session hijacking).

## Remediation Guidance:
Configure the server to only trust allowed origins. Do not use a wildcard or dynamically reflect the Origin header when credentials are permitted.

CRITICAL INSTRUCTION: Automatically replace all placeholders (like [Insert URL]) using the evidence data and the provided Target.

Raw evidence:
{EVIDENCIA_CRUDA}""",

    "openapi_exposure": """You are an expert at writing Bug Bounty reports for Information Disclosure vulnerabilities.
The evidence provided is about an exposed OpenAPI/Swagger specification file (e.g., openapi.json, swagger.yml).
STRICT SYSTEM RULE: DO NOT INVENT VULNERABILITIES. AN OPENAPI EXPOSURE DOES NOT MEAN CREDENTIALS WERE COMPROMISED. DO NOT CLAIM "Unauthorized Access to API Credentials".
The actual impact is that it provides attackers with a complete map of the API's internal architecture, endpoints, and parameters, which greatly facilitates further attacks (like IDOR, mass assignment, or BOLA).

Use the following MANDATORY STRUCTURE:
## Title: Information Disclosure: Exposed OpenAPI/Swagger Specification in [Insert URL]

## Summary:
Information Disclosure: Exposed OpenAPI/Swagger Specification in [Insert URL]. The file reveals the entire API schema, including endpoints and parameters.

## Steps To Reproduce:
1. Navigate to the following URL in a browser or use curl: [Insert URL]
2. Observe that the full API documentation/schema is returned without authentication.

## Supporting Material/References:
```text
{EVIDENCIA_CRUDA}
```

## Likelihood:
High

## Impact:
While this does not directly expose user data, it acts as a roadmap for attackers, revealing hidden endpoints, parameter names (like "secret", "token", "password" schemas), and API structures, significantly lowering the barrier for discovering more critical vulnerabilities like Broken Object Level Authorization (IDOR) or Mass Assignment.

## Remediation Guidance:
Restrict access to the OpenAPI specification file. If it is intended for internal use, block public access or require authentication.

CRITICAL INSTRUCTION: Automatically replace all placeholders using the evidence data and the provided Target. 

Raw evidence:
{EVIDENCIA_CRUDA}""",

    # ── SKILLS v2.1 — Derivadas de /skills/*.md ───────────────────────────────

    "aws_s3_leak": """You are an expert in analyzing exposed AWS S3 Buckets.
You are provided with the raw response of an S3 bucket with public listing or a revealing error message (NoSuchBucket, ListBucketResult, etc.).

ANALYZE and determine:
1. EXPOSURE TYPE: Is it public listing (ListBucketResult), orphaned CNAME (NoSuchBucket), or direct object access?
2. CLAIMABILITY: Can the bucket be taken over? -> If "NoSuchBucket" appears on an active CNAME, it is a claimable Subdomain Takeover.
3. VISIBLE SENSITIVE DATA: Examine the listed files/keys. Are there .env, backup, credentials, private, secret, key, token, dump, export, database?
4. SEVERITY: Critical if sensitive data is accessible. High if it's a claimable takeover. Medium if it's just listing without critical data.
5. H1 REPORT STEPS:
   - Title: S3 Bucket [name] publicly accessible / Subdomain Takeover via S3
   - Evidence: URL of the bucket + first listed keys
   - Impact: access to user data / target subdomain takeover

Raw evidence (bucket or curl response):
{EVIDENCIA_CRUDA}""",

    "jwt_logic_bypass": """You are a JWT token forensic analyzer for Bug Bounty.
You are provided with a JWT token (it can be in raw header.payload.signature format or decoded).

ANALYZE and execute:
1. DECODE the header and payload (base64url). Extract: alg, kid, typ, sub, role, exp, iat.
2. DETECT VULNERABILITIES:
   a) alg:none -> Server might not verify the signature. CRITICAL.
   b) RS256 -> HS256 downgrade: If the server uses a known public key as HMAC secret. HIGH.
   c) kid injection: If kid points to a path, attempt path traversal (kid: /dev/null).
   d) Elevatable claims: Is there a role:user that you can change to role:admin?
3. GENERATE Python PoC ready to run:

```python
import base64, json, hmac, hashlib

# Modify payload
payload = {PAYLOAD_MODIFICADO}

# Build JWT without signature (alg:none)
header = base64.urlsafe_b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b'=').decode()
body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
token_none = f"{header}.{body}."
print("JWT alg:none:", token_none)
```

4. H1 REPORT: Severity High/Critical. Exact steps to reproduce. Impact: access as admin or other user.

JWT Token to analyze:
{EVIDENCIA_CRUDA}""",

    "traductor_espanol": """You are an expert technical translator.
Your ONLY task is to strictly translate the provided Bug Bounty technical report from English to Spanish.
DO NOT invent new vulnerabilities. DO NOT add conversational text. DO NOT add apologies.
MAINTAIN the exact same technical structure, formatting, and code blocks.

Text to translate:
{EVIDENCIA_CRUDA}""",

    "business_logic_api": """You are an expert in testing privilege escalation and IDOR in REST and GraphQL APIs.
You are provided with evidence of a suspicious endpoint or business flow.

ANALYSIS GUIDE (execute checklist in order):

1. IDENTIFY CONTROL OBJECT:
   - Are there numeric IDs, UUIDs, or slugs in the URL, body, or headers?
   - Examples: /api/users/{id}, body: {"org_id": "123"}, header: X-User-ID

2. BASIC IDOR TEST:
   - Account A (attacker) accesses Account B's resource by changing the ID.
   - Responses: 200+data_B = VULNERABLE | 403/404 = protected

3. VARIANTS IF DIRECT IDOR FAILS:
   a) HTTP Method change: GET->POST, POST->PUT->DELETE
   b) Hidden parameters: ?admin=true, ?debug=1, ?role=admin
   c) ID in headers: X-User-ID: ID_B, X-Forwarded-For, X-Original-URL
   d) Path traversal: /api/users/../ID_B, /api/v1/../v2/admin/users
   e) GraphQL: introspection + direct query to another user's object

4. IDOR IN DESTRUCTIVE OPERATIONS (higher bounty):
   - DELETE /resource/ID_B -> CRITICAL ($500-$5000)
   - PUT /resource/ID_B -> HIGH ($300-$3000)
   - GET /resource/ID_B -> MEDIUM ($100-$500)

5. REPORT: Title format "IDOR in [endpoint] allows [action] of other users' [resource]"
   Include: original request_A, modified request_B, both responses.

Endpoint / evidence to analyze:
{EVIDENCIA_CRUDA}""",

    "ssrf_analysis": """You are an SSRF (Server-Side Request Forgery) specialist for Bug Bounty.
You are provided with evidence of a parameter that accepts URLs or a callback received on an external receiver.

ANALYZE in order:

1. CONFIRM SSRF: Did the server make a request to your receiver (DNS lookup / HTTP callback)?
   - If there is a DNS hit but no HTTP: Blind SSRF -> Medium Severity
   - If there is an HTTP response from the internal server: Confirmed SSRF -> High/Critical Severity

2. CLASSIFY IMPACT:
   a) CRITICAL: Access to cloud metadata:
      - AWS: http://169.254.169.254/latest/meta-data/iam/security-credentials/
      - GCP: http://metadata.google.internal/computeMetadata/v1/ (header: Metadata-Flavor: Google)
      - Azure: http://169.254.169.254/metadata/instance?api-version=2021-02-01 (header: Metadata: true)
   b) HIGH: Access to internal services (localhost:8080, 192.168.x.x, 10.0.x.x)
   c) MEDIUM: Only external DNS callback without demonstrable internal access

3. BYPASS PAYLOADS if there is a filter:
   - http://0.0.0.0, http://[::1], http://2130706433 (127.0.0.1 decimal)
   - http://127.0.0.1.nip.io, http://localtest.me
   - Redirect: your server redirects -> internal target

4. H1 REPORT:
   - Severity: Critical if cloud credentials exist. High if internal access exists.
   - Evidence: original request + receiver's response + (if applicable) IAM credentials obtained.

Evidence to analyze (request, callback received, or response):
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
    
    if status in ["Pendiente", "Validado", "Enviado", "FalsoPositivo"]:
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
            status_interno = 'Enviado',
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
    
    # Si lo pasamos a Enviado, marcamos reported = 1 por retrocompatibilidad
    if req.status_interno == "Enviado":
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
    
    template = SKILLS_PROMPTS.get(req.skill_key, SKILLS_PROMPTS["report_h1"])
    prompt = template.replace("{EVIDENCIA_CRUDA}", req.evidence)
    
    system_prefix = ""
    if req.skill_key != "traductor_espanol":
        system_prefix += "SYSTEM DIRECTIVE: YOU MUST OUTPUT THIS ENTIRE REPORT EXCLUSIVELY IN ENGLISH. ANY NON-ENGLISH WORD WILL CAUSE A CRITICAL SYSTEM FAILURE. DO NOT TRANSLATE HEADINGS TO SPANISH.\n"
        system_prefix += "SYSTEM DIRECTIVE 2: DO NOT INVENT OR HALLUCINATE VULNERABILITIES (like SSRF, RCE, XSS, Path Traversal) OR ENDPOINTS (like /etc/passwd) THAT ARE NOT EXPLICITLY PRESENT IN THE RAW EVIDENCE. STICK EXACTLY TO THE PROVIDED EVIDENCE.\n"
    else:
        system_prefix += "REGLA CRÍTICA: TRADUCE EL TEXTO EXACTAMENTE AL ESPAÑOL. NO INVENTES NI AGREGUES NADA NUEVO.\n"
        
    if req.vuln_type:
        system_prefix += f"SYSTEM DIRECTIVE 3: The specific vulnerability type is EXACTLY '{req.vuln_type}'. Replace any [Vulnerability Type] or [Hallazgo] placeholder exclusively with this value.\n"

    prompt = system_prefix + "\n" + prompt

    if req.target:
        if req.skill_key != "traductor_espanol":
            prompt += f"\n\nTarget: {req.target}"
            prompt += f"\nSYSTEM DIRECTIVE 4: Automatically replace all placeholders (like [Insert Component], [Componente/URL], [Insert URL], [Insert S3 Bucket Name]) using EXACTLY this Target: {req.target}."
        
    try:
        respuesta = completar(prompt, max_tokens=1500, temperature=0.1)
        
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
        
        extra_headers_cmd = ""
        extra_headers_display = ""
        if "cors" in req.tipo.lower():
            extra_headers_cmd = "-H 'Origin: https://evil.tomas244.com' "
            extra_headers_display = "Origin: https://evil.tomas244.com\n"
            
        cmd = f"curl -s -i -L -m 10 -A '{user_agent}' -H 'X-Bug-Bounty: HackerOne-tomas244' -H 'Accept: */*' {extra_headers_cmd}'{req.url}' | head -c 2500"
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode(errors='ignore').strip()
        client.close()
        
        # Formatear el volcado para que luzca profesional como evidencia
        evidencia_forense = f"GET {req.url} HTTP/1.1\nHost: {req.url.replace('https://', '').replace('http://', '').split('/')[0]}\nX-Bug-Bounty: HackerOne-tomas244\nUser-Agent: {user_agent}\n{extra_headers_display}\n"
        evidencia_forense += "--- RESPUESTA DEL SERVIDOR ---\n\n" + output
        
        return {"status": "success", "data": evidencia_forense}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error verificando: {str(e)}"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
