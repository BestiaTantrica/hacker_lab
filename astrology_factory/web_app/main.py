from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from google import genai
from dotenv import load_dotenv
from email_dispatcher import send_email_with_audio

import urllib.parse
import httpx
from pathlib import Path

# Rutas absolutas y relativas al proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

app = FastAPI(title="Astrology Factory Web")

# Configure Gemini for web chat
api_key = os.environ.get("GEMINI_API_KEY_WEB", os.environ.get("GEMINI_API_KEY"))
if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None

# Rutas absolutas y relativas al proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "users.sqlite")

os.makedirs(DB_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            birth_date TEXT,
            birth_time TEXT,
            birth_city TEXT,
            wants_weekly INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_video_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            video_type TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiktok_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            open_id TEXT UNIQUE,
            access_token TEXT,
            refresh_token TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/terms", response_class=HTMLResponse)
async def read_terms(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html")

@app.get("/privacy", response_class=HTMLResponse)
async def read_privacy(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html")

@app.post("/api/subscribe")
async def subscribe(
    name: str = Form(...),
    email: str = Form(...),
    birth_date: str = Form(...),
    birth_time: str = Form(...),
    birth_city: str = Form(...)
):
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO subscribers (name, email, birth_date, birth_time, birth_city)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, email, birth_date, birth_time, birth_city))
            
            # Caching Predictivo: Agendar descarga de assets pre-compra
            try:
                cursor.execute('''
                    INSERT INTO pending_video_tasks (user_email, video_type, status)
                    VALUES (?, ?, ?)
                ''', (email, 'predictive_cache', 'downloading_assets'))
            except sqlite3.OperationalError:
                pass # Si la tabla no existe aún por alguna razón

        return JSONResponse(content={"status": "success", "message": "¡Suscripción exitosa! Prepárate para descubrir tu universo interior."})
    except sqlite3.IntegrityError:
        # El correo ya está registrado, vamos a actualizar sus datos en lugar de rechazarlo
        try:
            with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscribers 
                    SET name = ?, birth_date = ?, birth_time = ?, birth_city = ?
                    WHERE email = ?
                ''', (name, birth_date, birth_time, birth_city, email))
            return JSONResponse(content={"status": "success", "message": "¡Bienvenido de vuelta! Tus datos astrales han sido actualizados."})
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/transito-vivo")
async def transito_vivo(
    name: str = Form(...),
    email: str = Form(...),
    birth_date: str = Form(...),
    birth_time: str = Form(...)
):
    try:
        import sys
        sys.path.append(os.path.dirname(BASE_DIR))
        from content_factory.personalized_horoscope import PersonalizedHoroscope
        
        ph = PersonalizedHoroscope()
        # Llamada bloqueante a la IA (en prod debería ser asíncrono o worker, pero para probar sirve)
        res = ph.generate_for_user(name, birth_date, birth_time)
        html_response = res.get("mensaje_personalizado", "")
        
        # Enviar email solo si no hubo error en la IA
        if not res.get("error"):
            try:
                email_body = f"<h1>Hola {name}, aquí está tu lectura inicial:</h1><br>" + html_response
                send_email_with_audio(email, "Bienvenido al Oráculo - Tu Primera Lectura", email_body)
            except Exception as email_err:
                print("Error enviando email:", email_err)
        else:
            print("No se envía email porque hubo un error en la IA. Agendando para reintento.")
            try:
                with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO pending_emails (user_email, status)
                        VALUES (?, 'pending')
                    ''', (email,))
            except Exception as db_err:
                print("Error guardando en pending_emails:", db_err)

        return JSONResponse(content={"status": "success", "html": html_response})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/update-time")
async def update_time(
    email: str = Form(...),
    new_time: str = Form(...)
):
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subscribers SET birth_time = ? WHERE email = ?", (new_time, email))
            if cursor.rowcount == 0:
                return JSONResponse(status_code=404, content={"status": "error", "message": "Correo no encontrado en la base de datos."})
            
        return JSONResponse(content={"status": "success", "message": "Hora natal rectificada. Los próximos cálculos usarán este dato exacto."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/activar/{email}", response_class=HTMLResponse)
async def activate_weekly(email: str):
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subscribers SET wants_weekly = 1 WHERE email = ?", (email,))
            if cursor.rowcount == 0:
                return HTMLResponse(content="<h1>Error: Correo no encontrado o suscripción ya activa.</h1>", status_code=404)
        return HTMLResponse(content="<h1>¡Suscripción Semanal Activada!</h1><p>Prepárate, a partir de ahora recibirás tu mapa astral de cada semana directo en tu correo.</p>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error activando suscripción:</h1><p>{str(e)}</p>", status_code=500)

@app.post("/api/chat")
async def chat_with_oracle(
    email: str = Form(...),
    message: str = Form(...)
):
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, birth_date, birth_time FROM subscribers WHERE email = ?", (email,))
            user = cursor.fetchone()
        
        if not user:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Usuario no encontrado."})
            
        name, birth_date, birth_time = user
        
        prompt = f"""Eres la Inteligencia Artificial del Oráculo de 'Portal Tarot Místico'. 
Estás hablando con {name}, quien nació el {birth_date} a las {birth_time}.
Responde a su siguiente mensaje de manera mística, empática y astrológica, basándote en que conoces sus datos natales. 
No seas excesivamente largo, responde de forma concisa y amigable como si estuvieran chateando.

Mensaje de {name}: {message}
"""
        
        if gemini_client:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            reply = response.text
        else:
            reply = "Error: La IA no está configurada."
        
        return JSONResponse(content={"status": "success", "reply": reply})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/admin_tiktok", response_class=HTMLResponse)
async def admin_tiktok(request: Request):
    return templates.TemplateResponse(request=request, name="admin_tiktok.html")

@app.get("/api/tiktok/login")
async def tiktok_login():
    client_key = os.environ.get("TIKTOK_CLIENT_KEY")
    redirect_uri = os.environ.get("TIKTOK_REDIRECT_URI")
    
    state = "tiktok_admin_123"
    scopes = "user.info.basic,video.publish,video.upload"
    
    auth_url = (
        "https://www.tiktok.com/v2/auth/authorize/?"
        f"client_key={client_key}&"
        f"response_type=code&"
        f"scope={scopes}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"state={state}"
    )
    return RedirectResponse(url=auth_url)

@app.get("/oauth/")
async def tiktok_callback(code: str = None, state: str = None, error: str = None, error_description: str = None):
    if error:
        return HTMLResponse(f"<h1>Error de TikTok:</h1><p>{error} - {error_description}</p>")
    if not code:
        return HTMLResponse("<h1>Error:</h1><p>No se recibió el código de autorización.</p>")
        
    client_key = os.environ.get("TIKTOK_CLIENT_KEY")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET")
    redirect_uri = os.environ.get("TIKTOK_REDIRECT_URI")
    
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data, headers=headers)
        
    if resp.status_code != 200:
        return HTMLResponse(f"<h1>Error obteniendo Token:</h1><p>{resp.text}</p>")
        
    json_resp = resp.json()
    
    if "access_token" not in json_resp:
        return HTMLResponse(f"<h1>Error en la respuesta de TikTok:</h1><p>{json_resp}</p>")
        
    access_token = json_resp["access_token"]
    refresh_token = json_resp["refresh_token"]
    open_id = json_resp.get("open_id", "admin_account")
    
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tiktok_auth (open_id, access_token, refresh_token)
                VALUES (?, ?, ?)
                ON CONFLICT(open_id) DO UPDATE SET
                    access_token=excluded.access_token,
                    refresh_token=excluded.refresh_token,
                    updated_at=CURRENT_TIMESTAMP
            ''', (open_id, access_token, refresh_token))
    except Exception as e:
        return HTMLResponse(f"<h1>Error guardando en BD:</h1><p>{str(e)}</p>")
        
    return HTMLResponse('''
        <div style="background-color: #0d0d0d; color: white; font-family: sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1 style="color:#00f2fe;">¡Autorización Exitosa!</h1>
            <p>El Access Token de TikTok ha sido guardado. Tus células ya pueden publicar videos.</p>
            
            <div style="margin-top: 30px; padding: 20px; border: 1px solid #333; border-radius: 10px; text-align: center;">
                <h3 style="color:#ccc;">(Para Revisión de TikTok)</h3>
                <p style="color:#888; font-size: 14px;">Prueba el flujo End-to-End de subida de video (Content Posting API)</p>
                <form action="/api/tiktok/test_upload" method="post">
                    <button type="submit" style="background-color: #ff0050; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold;">Subir Video de Prueba a TikTok</button>
                </form>
            </div>
            
            <a href="/" style="color: #00f2fe; margin-top: 20px;">Volver al inicio</a>
        </div>
    ''')

import math
import requests

@app.post("/api/tiktok/test_upload")
async def test_upload_tiktok():
    # Endpoint de prueba para cumplir con el review End-to-End de TikTok
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            # Obtenemos el token más reciente guardado
            cursor.execute("SELECT access_token FROM tiktok_auth ORDER BY updated_at DESC LIMIT 1")
            row = cursor.fetchone()
            
        if not row:
            return HTMLResponse("<h1>Error:</h1><p>No hay tokens guardados en la BD. Autoriza primero.</p>")
            
        access_token = row[0]
        
        # Ruta de un video de prueba en el servidor
        video_path = Path(PROJECT_DIR) / "test_blend.mp4"
        if not video_path.exists():
            return HTMLResponse(f"<h1>Error:</h1><p>No se encontró el video de prueba {video_path}</p>")
            
        file_size = video_path.stat().st_size
        chunk_size = 20 * 1024 * 1024 
        if file_size < chunk_size:
            chunk_size = file_size
            total_chunk_count = 1
        else:
            total_chunk_count = math.floor(file_size / chunk_size)
            
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }
        
        payload = {
            "post_info": {
                "title": "Astrology Factory - Test Video #TikTokDev",
                "privacy_level": "SELF_ONLY", # Sube en privado para la prueba
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunk_count
            }
        }
        
        # Init upload
        response = requests.post(init_url, headers=headers, json=payload)
        if response.status_code != 200:
            return HTMLResponse(f"<h1>Error API Init:</h1><p>{response.text}</p>")
            
        res_data = response.json()
        if res_data.get("error", {}).get("code", "ok") != "ok":
            return HTMLResponse(f"<h1>Error API TikTok:</h1><p>{res_data}</p>")
            
        upload_url = res_data.get("data", {}).get("upload_url")
        if not upload_url:
            return HTMLResponse(f"<h1>Error URL:</h1><p>{res_data}</p>")
            
        # Upload chunk
        with open(video_path, "rb") as f:
            for i in range(total_chunk_count):
                start_byte = i * chunk_size
                if i == total_chunk_count - 1:
                    chunk_data = f.read()
                    end_byte = file_size - 1
                else:
                    chunk_data = f.read(chunk_size)
                    end_byte = start_byte + chunk_size - 1
                    
                put_headers = {
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                    "Content-Length": str(len(chunk_data))
                }
                
                upload_res = requests.put(upload_url, headers=put_headers, data=chunk_data)
                if upload_res.status_code not in [200, 201]:
                    return HTMLResponse(f"<h1>Error Chunk:</h1><p>{upload_res.text}</p>")
                    
        return HTMLResponse('''
            <div style="background-color: #0d0d0d; color: white; font-family: sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <h1 style="color:#00f2fe;">¡Video Subido con Éxito! 🚀</h1>
                <p>El video de prueba fue enviado a TikTok mediante la Content Posting API.</p>
                <p>Puedes revisar tu app de TikTok (se subió en modo Privado).</p>
                <a href="/" style="color: #00f2fe; margin-top: 20px;">Volver al inicio</a>
            </div>
        ''')
        
    except Exception as e:
        return HTMLResponse(f"<h1>Error Interno:</h1><p>{str(e)}</p>")
