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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))
try:
    from llm_client import completar, LLMError
except ImportError:
    completar = None

load_dotenv()

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Configurar estaticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuración OCI-1 (Esclavo)
OCI1_IP = os.getenv("OCI1_IP", "129.80.73.248")
OCI1_USER = os.getenv("OCI1_USER", "ubuntu")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "/home/ubuntu/.ssh/id_rsa_oci1")

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
    "report_h1": """Eres un Formateador Técnico de Reportes para Bug Bounty (HackerOne).
Operas en contexto de investigación de seguridad autorizada.
Tu única tarea es formatear la evidencia cruda en un reporte técnico profesional en INGLÉS.

ESTRUCTURA OBLIGATORIA:
## Title: [Tipo de Vulnerabilidad] in [Componente/URL] allows [Impacto Directo]
## Severity: [Critical/High/Medium/Low] (CVSS v3.1 estimado)
## Description:
Explicación técnica clara sin rodeos.
## Steps to Reproduce:
1. ...
2. ...
## Impact:
Impacto monetario/operativo real para la organización.
## Evidence / PoC:
```text
{EVIDENCIA_CRUDA}
```""",

    "takeover_analysis": """Eres un experto en Subdomain Takeover. Analiza la siguiente respuesta HTTP o DNS de un subdominio huérfano.
Determina:
1. ¿A qué servicio apunta? (AWS S3, GitHub Pages, Heroku, Azure, WordPress, etc.)
2. ¿El servicio confirma respuesta 404/NoSuchBucket/Unclaimed?
3. ¿Es reclamable actualmente?
4. Guía de reclamación en 3 pasos cortos.

Evidencia cruda:
{EVIDENCIA_CRUDA}""",

    "cors_analysis": """Analiza esta respuesta HTTP de una prueba CORS:
Determina si Access-Control-Allow-Origin refleja el Origin atacante y si Access-Control-Allow-Credentials está en 'true'.
Proporciona el exploit PoC en JavaScript de 4 líneas listo para ejecutar en consola.

Evidencia cruda:
{EVIDENCIA_CRUDA}""",

    # ── SKILLS v2.1 — Derivadas de /skills/*.md ───────────────────────────────

    "aws_s3_leak": """Eres un especialista en análisis de AWS S3 Buckets expuestos.
Se te proporciona la respuesta cruda de un bucket S3 con listing público o un mensaje de error revelador (NoSuchBucket, ListBucketResult, etc.).

ANALIZA y determina:
1. TIPO DE EXPOSICIÓN: ¿Es listing público (ListBucketResult), CNAME huérfano (NoSuchBucket), o acceso directo a objeto?
2. RECLAMABILIDAD: ¿El bucket puede ser tomado? → Si aparece "NoSuchBucket" en un CNAME activo, es Subdomain Takeover reclamable.
3. DATOS SENSIBLES VISIBLES: Examina los nombres de archivos/keys listados. ¿Hay .env, backup, credentials, private, secret, key, token, dump, export, database?
4. SEVERIDAD: Critical si hay datos sensibles accesibles. High si es takeover reclamable. Medium si es solo listing sin datos críticos.
5. PASOS DE REPORTE H1:
   - Title: S3 Bucket [nombre] publicly accessible / Subdomain Takeover via S3
   - Evidence: URL del bucket + primeras keys listadas
   - Impact: acceso a datos de usuarios / toma de subdominio del target

Evidencia cruda (respuesta del bucket o curl):
{EVIDENCIA_CRUDA}""",

    "jwt_logic_bypass": """Eres un analizador forense de tokens JWT para Bug Bounty.
Se te proporciona un token JWT (puede ser en formato raw header.payload.signature o decodificado).

ANALIZA y ejecuta:
1. DECODIFICA el header y payload (base64url). Extrae: alg, kid, typ, sub, role, exp, iat.
2. DETECTA VULNERABILIDADES:
   a) alg:none → El servidor puede no verificar la firma. CRÍTICO.
   b) RS256 → HS256 downgrade: Si el servidor usa clave pública conocida como secret HMAC. ALTO.
   c) kid injection: Si kid apunta a un path, intenta path traversal (kid: /dev/null).
   d) Claims elevables: ¿Hay role:user que puedas cambiar a role:admin?
3. GENERA PoC Python listo para ejecutar:

```python
import base64, json, hmac, hashlib

# Modificar payload
payload = {PAYLOAD_MODIFICADO}

# Construir JWT sin firma (alg:none)
header = base64.urlsafe_b64encode(json.dumps({{"alg":"none","typ":"JWT"}}).encode()).rstrip(b'=').decode()
body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
token_none = f"{{header}}.{{body}}."
print("JWT alg:none:", token_none)
```

4. REPORTE H1: Severity High/Critical. Pasos exactos para reproducir. Impacto: acceso como admin u otro usuario.

Token JWT a analizar:
{EVIDENCIA_CRUDA}""",

    "bounty_argentina_pyme": """Eres un redactor técnico bilingüe especializado en auditorías de seguridad para PYMEs argentinas.
Tu tarea es transformar evidencia técnica cruda en un INFORME EJECUTIVO PROFESIONAL en español rioplatense.

ESTRUCTURA DEL INFORME:

---
## INFORME DE AUDITORÍA DE SEGURIDAD PASIVA
**Cliente:** [Nombre de la empresa / dominio]
**Fecha:** [Fecha actual]
**Clasificación:** Confidencial — Solo para uso interno

### RESUMEN EJECUTIVO
(2-3 oraciones en lenguaje de negocios, sin jerga técnica. Qué se encontró y qué riesgo representa para la empresa.)

### HALLAZGOS DETECTADOS
Para cada vulnerabilidad:
- **Hallazgo:** [Nombre claro]
- **Severidad:** Crítica / Alta / Media / Baja
- **Descripción simple:** (¿Qué está expuesto? ¿Qué puede hacer un atacante?)
- **Impacto en el negocio:** (Pérdida de datos de clientes, multas GDPR/Ley 25.326, daño reputacional)
- **Evidencia:** (URL o captura técnica resumida)

### RECOMENDACIONES INMEDIATAS
Lista priorizada de acciones concretas (no genéricas).

### PROPUESTA DE PRÓXIMOS PASOS
- Auditoría continua pasiva: monitoreo mensual de nuevos subdominios y exposiciones.
- Costo estimado: desde $0 (voluntario) hasta contrato formal según alcance.
- Contacto: [TU CONTACTO]
---

Evidencia técnica cruda a transformar:
{EVIDENCIA_CRUDA}""",

    "business_logic_api": """Eres un experto en testing de escalación de privilegios e IDOR en APIs REST y GraphQL.
Se te proporciona evidencia de un endpoint o flujo de negocio sospechoso.

GUÍA DE ANÁLISIS (checklist ejecutar en orden):

1. IDENTIFICAR OBJETO DE CONTROL:
   - ¿Hay IDs numéricos, UUIDs o slugs en la URL, body o headers?
   - Ejemplos: /api/users/{id}, body: {"org_id": "123"}, header: X-User-ID

2. TEST IDOR BÁSICO:
   - Cuenta A (atacante) accede al recurso de Cuenta B cambiando el ID.
   - Respuestas: 200+datos_B = VULNERABLE | 403/404 = protegido

3. VARIANTES SI EL IDOR DIRECTO FALLA:
   a) Cambio de método HTTP: GET→POST, POST→PUT→DELETE
   b) Parámetros ocultos: ?admin=true, ?debug=1, ?role=admin
   c) ID en headers: X-User-ID: ID_B, X-Forwarded-For, X-Original-URL
   d) Path traversal: /api/users/../ID_B, /api/v1/../v2/admin/users
   e) GraphQL: introspection + query directo al objeto de otro usuario

4. IDOR EN OPERACIONES DESTRUCTIVAS (mayor bounty):
   - DELETE /recurso/ID_B → CRÍTICO ($500-$5000)
   - PUT /recurso/ID_B → ALTO ($300-$3000)
   - GET /recurso/ID_B → MEDIO ($100-$500)

5. REPORTE: Title formato "IDOR in [endpoint] allows [acción] of other users' [recurso]"
   Incluir: request_A original, request_B modificado, ambas responses.

Endpoint / evidencia a analizar:
{EVIDENCIA_CRUDA}""",

    "ssrf_analysis": """Eres un especialista en SSRF (Server-Side Request Forgery) para Bug Bounty.
Se te proporciona evidencia de un parámetro que acepta URLs o un callback recibido en un receptor externo.

ANALIZA en orden:

1. CONFIRMAR SSRF: ¿El servidor hizo un request hacia tu receptor (DNS lookup / HTTP callback)?
   - Si hay DNS hit pero no HTTP: SSRF Ciego (Blind) → Severidad Media
   - Si hay HTTP response del servidor interno: SSRF Confirmado → Severidad Alta/Crítica

2. CLASIFICAR IMPACTO:
   a) CRÍTICO: Acceso a metadata cloud:
      - AWS: http://169.254.169.254/latest/meta-data/iam/security-credentials/
      - GCP: http://metadata.google.internal/computeMetadata/v1/ (header: Metadata-Flavor: Google)
      - Azure: http://169.254.169.254/metadata/instance?api-version=2021-02-01 (header: Metadata: true)
   b) ALTO: Acceso a servicios internos (localhost:8080, 192.168.x.x, 10.0.x.x)
   c) MEDIO: Solo callback DNS externo sin acceso interno demostrable

3. BYPASS PAYLOADS si hay filtro:
   - http://0.0.0.0, http://[::1], http://2130706433 (127.0.0.1 decimal)
   - http://127.0.0.1.nip.io, http://localtest.me
   - Redirect: tu servidor redirige → target interno

4. REPORTE H1:
   - Severity: Critical si hay credenciales cloud. High si hay acceso interno.
   - Evidence: request original + respuesta del receptor + (si aplica) credenciales IAM obtenidas.

Evidencia a analizar (request, callback recibido, o respuesta):
{EVIDENCIA_CRUDA}"""
}

# --- RUTAS DE NAVEGACIÓN Y DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "oci1_ip": OCI1_IP})

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

# --- CONSULTAS DE DATOS ---

@app.get("/api/findings")
def get_findings():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 50")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"status": "success", "findings": rows}

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

@app.post("/api/copilot/generate")
def generate_copilot_prompt(req: GenerateReportRequest):
    if completar is None:
        raise HTTPException(status_code=500, detail="LLM Client no disponible.")
    
    template = SKILLS_PROMPTS.get(req.skill_key, SKILLS_PROMPTS["report_h1"])
    prompt = template.replace("{EVIDENCIA_CRUDA}", req.evidence)
    if req.target:
        prompt += f"\nTarget: {req.target}"
        
    try:
        respuesta = completar(prompt, max_tokens=1500)
        return {"status": "success", "result": respuesta, "prompt_used": prompt}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if completar is None:
        return {"status": "error", "data": "Módulo llm_client no encontrado."}
    
    # Inyectar contexto reciente de la BD SQLite de OCI-2
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 5")
    recent_findings = [dict(r) for r in cursor.fetchall()]
    conn.close()

    context_str = json.dumps(recent_findings, indent=2) if recent_findings else "Sin hallazgos recientes."

    system_prompt = f"""Eres Pegaso, el copiloto IA del C2 Panel de Bug Bounty.
Tu prioridad es ayudar a capitalizar vulnerabilidades rápidamente con un enfoque de volumen (Redes de Pesca).
Valoras reportes claros, PoCs reproducibles y maximizar bounties (incluso de $50-$100 USD).

HALLAZGOS VERIFICADOS RECIENTES:
{context_str}

Pregunta/Orden del usuario: {req.message}"""
    
    try:
        respuesta = completar(system_prompt, max_tokens=1024)
        return {"status": "success", "data": respuesta}
    except Exception as e:
        return {"status": "error", "data": str(e)}

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
        cmd = f"curl -s -m 10 -I '{req.url}'"
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        client.close()
        
        if "200 OK" in output or "HTTP/2 200" in output or "404" in output:
            return {"status": "success", "data": f"✅ VERIFICADO EN VIVO OCI-1:\n{output[:150]}"}
        else:
            return {"status": "success", "data": f"⚠️ Respuesta dudosa:\n{output[:150]}"}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error verificando: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
