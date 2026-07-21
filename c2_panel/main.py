import os
import sys
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
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

app = FastAPI(title="C2 Panel - HackerLab")

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
        print(f"Error conectando a SSH: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "oci1_ip": OCI1_IP})

@app.get("/api/status")
def get_status():
    client = get_ssh_client()
    if not client:
        return {"status": "offline", "message": "No se pudo conectar a OCI-1"}
    
    try:
        stdin, stdout, stderr = client.exec_command("uptime -p")
        uptime = stdout.read().decode().strip()
        
        # Consultamos cuantos targets hay en el archivo de OCI-1
        stdin, stdout, stderr = client.exec_command("wc -l /home/ubuntu/plataforma_operativa/resultados/actual.json 2>/dev/null || echo 0")
        targets_count = stdout.read().decode().strip().split()[0]
        
        client.close()
        return {"status": "online", "uptime": uptime, "targets": targets_count}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "message": str(e)}

@app.get("/api/raw_data")
def get_raw_data():
    client = get_ssh_client()
    if not client:
        return {"status": "offline", "data": "No se pudo conectar a OCI-1 para extraer datos."}
    
    try:
        # Extraemos las ultimas lineas del archivo actual.json (telemetría real)
        stdin, stdout, stderr = client.exec_command("tail -n 100 /home/ubuntu/plataforma_operativa/resultados/actual.json 2>/dev/null || echo 'No hay datos de descubrimiento aún.'")
        raw_output = stdout.read().decode().strip()
        
        client.close()
        return {"status": "success", "data": raw_output}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error leyendo datos: {str(e)}"}

@app.get("/api/get_poc")
def get_poc():
    client = get_ssh_client()
    if not client:
        return {"status": "offline", "data": "No se pudo conectar a OCI-1."}
    
    try:
        # Extraemos el ultimo Proof of Concept generado automáticamente por los scripts
        stdin, stdout, stderr = client.exec_command("cat /home/ubuntu/plataforma_operativa/resultados/ultimo_poc.txt 2>/dev/null || echo 'Aún no se ha generado un PoC. El sistema debe ejecutar un eslabón de explotación primero.'")
        poc_output = stdout.read().decode().strip()
        
        client.close()
        return {"status": "success", "data": poc_output}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error leyendo PoC: {str(e)}"}

class ExploitRequest(BaseModel):
    tipo: str

class EcommerceRequest(BaseModel):
    paso: str  # "mapeo", "ataque", "escalada", "reintentos", "completo"

def _run_remote_command(command: str, timeout: int = 300):
    """Helper: ejecuta un comando en OCI-1 via SSH y retorna (output, error)."""
    client = get_ssh_client()
    if not client:
        return None, "No se pudo conectar a OCI-1"
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode().strip()
        error  = stderr.read().decode().strip()
        client.close()
        return output, error
    except Exception as e:
        if client: client.close()
        return None, str(e)

class VerifyRequest(BaseModel):
    url: str
    tipo: str

@app.post("/api/verify_bug")
def verify_bug(req: VerifyRequest):
    """
    Verifica en vivo si un bug sigue activo.
    Hace una petición HTTP GET rápida desde OCI-1 hacia la URL del bug.
    """
    client = get_ssh_client()
    if not client:
        return {"status": "offline", "data": "No se pudo conectar a OCI-1."}
    
    try:
        # Hacemos curl a la URL, con timeout corto
        cmd = f"curl -s -m 10 -I '{req.url}'"
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        
        # Validacion basica
        is_verified = False
        if req.tipo == "Secreto Expuesto en JS":
            is_verified = "200 OK" in output or "HTTP/2 200" in output
        elif req.tipo == "subdomain_takeover":
            is_verified = "404 Not Found" in output or "NoSuchBucket" in output
            
        client.close()
        
        if is_verified:
            return {"status": "success", "data": "✅ VERIFICADO EN VIVO. El endpoint sigue expuesto."}
        else:
            return {"status": "success", "data": f"⚠️ ATENCIÓN: El servidor respondió:\n{output[:100]}...\nVerificar manualmente."}
            
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error verificando: {str(e)}"}

@app.get("/api/get_motor_results")
def get_motor_results():
    """Obtiene los resultados de la cosecha nocturna (Secretos JS y Explotador Automático)"""
    client = get_ssh_client()
    if not client:
        return {"status": "offline", "data": "No se pudo conectar a OCI-1."}
    
    try:
        # Extraer secretos
        stdin, stdout, stderr = client.exec_command("cat /home/ubuntu/plataforma_operativa/resultados/secretos_js.json 2>/dev/null || echo '[]'")
        secretos = stdout.read().decode().strip()
        if not secretos or secretos == "[]": secretos = "[]"
        
        # Extraer ultimo reporte del explotador
        stdin, stdout, stderr = client.exec_command("cat $(ls -t /home/ubuntu/plataforma_operativa/resultados/explotador_*.json 2>/dev/null | head -1) 2>/dev/null || echo '[]'")
        explotador = stdout.read().decode().strip()
        if not explotador or explotador == "[]": explotador = "[]"
        
        client.close()
        
        return {
            "status": "success",
            "secretos": secretos,
            "explotador": explotador
        }
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Error leyendo resultados: {str(e)}"}


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if completar is None:
        return {"status": "error", "data": "Módulo llm_client no encontrado."}
    
    # Intentamos leer el contexto RAG de OCI-1
    contexto_rag = ""
    client = get_ssh_client()
    if client:
        try:
            stdin, stdout, stderr = client.exec_command("cat /home/ubuntu/plataforma_operativa/resultados/CEREBRO_CONTEXTO.txt 2>/dev/null || echo ''")
            contexto_rag = stdout.read().decode().strip()
            client.close()
        except Exception:
            if client: client.close()

    # Prompt base para darle contexto al agente
    system_prompt = f"""Eres Pegaso, el asistente de IA integrado en el C2 Panel de Bug Bounty.
Tu objetivo es ayudar al usuario a analizar vulnerabilidades, entender logs y redactar reportes.
Si el usuario menciona "Cola de Revisión" o "actual.json", puedes inferir su contexto de Bug Bounty.
Sé directo, conciso y profesional.

CONTEXTO ACTUAL DEL SISTEMA (RAG):
{contexto_rag if contexto_rag else "No hay contexto dinámico disponible."}

Mensaje del usuario: {req.message}"""
    
    try:
        respuesta = completar(system_prompt, max_tokens=1024)
        return {"status": "success", "data": respuesta}
    except Exception as e:
        return {"status": "error", "data": str(e)}

class CmdRequest(BaseModel):
    command: str
    token: str

@app.post("/api/cmd")
def execute_raw_command(req: CmdRequest):
    """
    MIRROR WEB PARA IA:
    Permite al agente LLM ejecutar comandos shell directamente en OCI-1.
    Usa el token definido en variables de entorno o un fallback.
    """
    secret_token = os.getenv("C2_ADMIN_TOKEN", "pegaso-admin-2026")
    if req.token != secret_token:
        return {"status": "error", "data": "Token de autorización inválido."}
    
    output, error = _run_remote_command(req.command)
    if output is None:
        return {"status": "error", "data": error}
    return {"status": "success", "data": output + ("\n" + error if error else "")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
