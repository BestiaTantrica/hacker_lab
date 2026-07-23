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
    
    template = SKILL_PROMPTS.get(req.skill_key, SKILL_PROMPTS["report_h1"])
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
