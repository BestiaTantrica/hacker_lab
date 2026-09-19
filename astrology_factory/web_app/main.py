from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI(title="Astrology Factory Web")

# Rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DB_PATH = os.path.join(BASE_DIR, "database", "users.sqlite")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/subscribe")
async def subscribe(
    name: str = Form(...),
    email: str = Form(...),
    birth_date: str = Form(...),
    birth_time: str = Form(...),
    birth_city: str = Form(...)
):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subscribers (name, email, birth_date, birth_time, birth_city)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, birth_date, birth_time, birth_city))
        conn.commit()
        conn.close()
        return JSONResponse(content={"status": "success", "message": "¡Suscripción exitosa! Prepárate para descubrir tu universo interior."})
    except sqlite3.IntegrityError:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Este correo ya está registrado."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/transito-vivo")
async def transito_vivo(
    name: str = Form(...),
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
        return JSONResponse(content={"status": "success", "html": res.get("mensaje_personalizado", "")})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/activar/{email}", response_class=HTMLResponse)
async def activate_weekly(email: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET wants_weekly = 1 WHERE email = ?", (email,))
        if cursor.rowcount == 0:
            conn.close()
            return HTMLResponse(content="<h1>Error: Correo no encontrado o suscripción ya activa.</h1>", status_code=404)
        conn.commit()
        conn.close()
        return HTMLResponse(content="<h1>¡Suscripción Semanal Activada!</h1><p>Prepárate, a partir de ahora recibirás tu mapa astral de cada semana directo en tu correo.</p>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error activando suscripción:</h1><p>{str(e)}</p>", status_code=500)

VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault"
os.makedirs(VAULT_DIR, exist_ok=True)

@app.get("/vault", response_class=HTMLResponse)
async def vault_form():
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Subir a Bóveda</title>
    <style>body{font-family:sans-serif;text-align:center;padding:50px;background:#111;color:#fff;} input[type="file"]{margin:20px;padding:10px;} button{padding:10px 20px;font-size:16px;background:#44f;color:#fff;border:none;border-radius:5px;cursor:pointer;} .dl-btn{background:#28a745; margin-top: 30px; display:inline-block; text-decoration:none; color:#fff; border-radius:5px;}</style>
    </head>
    <body>
        <h2>Astrology Vault - Subida Directa</h2>
        <form action="/vault/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <button type="submit">Guardar en Bóveda</button>
        </form>
        
        <hr style="margin:40px 0; border-color:#333;">
        <h2>Videos Listos para Descargar</h2>
        <a href="/download_video" class="dl-btn" style="padding:15px 30px; font-weight:bold;">📥 Descargar Video Semana 2 (60s)</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/download_video")
async def download_video():
    video_path = "/home/LAB/astrology_factory/produccion/Semana2_Octubre_Luna_Aries/Semana2_Octubre_Luna_Aries.mp4"
    return FileResponse(video_path, filename="Semana2_Octubre_Luna_Aries.mp4", media_type="video/mp4")

@app.post("/vault/upload")
async def upload_to_vault(file: UploadFile = File(...)):
    import datetime, shutil
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(file.filename)
        new_name = f"web_{timestamp}{ext}"
        save_path = os.path.join(VAULT_DIR, new_name)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return HTMLResponse(content=f"<h1>¡Archivo guardado con éxito!</h1><p>Nombre en bóveda: {new_name}</p><a href='/vault'>Subir otro</a>")
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)

