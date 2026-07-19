import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import paramiko
from dotenv import load_dotenv

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

@app.post("/api/execute_exploit")
def execute_exploit():
    client = get_ssh_client()
    if not client:
        return {"status": "error", "data": "No se pudo conectar a OCI-1."}
    
    try:
        # Ejecutamos el eslabon en OCI-1. Limitado a 50 subdominios para que no se cuelgue la UI mucho tiempo.
        # En una arquitectura real, esto deberia ser asincrono con Celery/Redis, pero por ahora bloqueamos y esperamos.
        command = "python3 /home/ubuntu/plataforma_operativa/monitores/explotador_automatico.py --max 50"
        stdin, stdout, stderr = client.exec_command(command, timeout=300) # Esperamos hasta 5 mins
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        client.close()
        
        if error and not output:
             return {"status": "error", "data": error}
             
        return {"status": "success", "data": output + "\n" + error}
    except Exception as e:
        if client: client.close()
        return {"status": "error", "data": f"Excepción ejecutando script: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
