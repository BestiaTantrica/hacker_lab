from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from google import genai
from dotenv import load_dotenv
from email_dispatcher import send_email_with_audio

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


