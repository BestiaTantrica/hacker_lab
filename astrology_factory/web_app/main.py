from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys
import sqlite3
import os
import json
import urllib.parse
import httpx
from pathlib import Path

# Rutas absolutas y relativas al proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

from google import genai
try:
    from email_dispatcher import send_email_with_audio
except ImportError:
    from web_app.email_dispatcher import send_email_with_audio

app = FastAPI(title="Astrology Factory Web")

# Configure Gemini for web chat
api_key = os.environ.get("GEMINI_API_KEY_WEB", os.environ.get("GEMINI_API_KEY"))
if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None

# Rutas absolutas y relativas al proyecto
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

VIDEOS_FONDO_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/videos de espacio para fondo"
if os.path.isdir(VIDEOS_FONDO_DIR):
    app.mount("/videos_fondo", StaticFiles(directory=VIDEOS_FONDO_DIR), name="videos_fondo")

app.mount("/static", StaticFiles(directory=STATIC_DIR, follow_symlink=True), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

@app.head("/", include_in_schema=False)
async def head_index():
    return HTMLResponse(content="", status_code=200)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/terms", response_class=HTMLResponse)
async def read_terms(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html")

@app.get("/reloj", response_class=HTMLResponse)
async def read_reloj(request: Request):
    return templates.TemplateResponse(request=request, name="reloj.html")

@app.get("/privacy", response_class=HTMLResponse)
async def read_privacy(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html")

@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM subscribers")
    total_subscribers = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, name, email, birth_date, birth_time, birth_city FROM subscribers ORDER BY id DESC LIMIT 50")
    subscribers = cursor.fetchall()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM chat_logs")
        total_chats = cursor.fetchone()[0]
    except Exception:
        total_chats = 0
        
    conn.close()
    
    # Cargar publicaciones
    reg_path = os.path.join(PROJECT_DIR, "produccion", "registro_publicaciones.json")
    publicaciones = {}
    total_videos_ready = 0
    total_tiktoks_published = 0
    if os.path.exists(reg_path):
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                reg_data = json.load(f)
                publicaciones = reg_data.get("publicaciones", {})
                for p in publicaciones.values():
                    if p.get("video_generado") or p.get("estado_render") == "COMPLETADO":
                        total_videos_ready += 1
                    if p.get("estado_tiktok") == "PUBLICADO":
                        total_tiktoks_published += 1
        except Exception:
            pass

    # Chequeo de daemons en background
    import subprocess
    yt_bot_active = False
    telegram_bot_active = False
    try:
        ps_out = subprocess.check_output(["ps", "aux"]).decode()
        yt_bot_active = "youtube_comments_daemon" in ps_out
        telegram_bot_active = "daily_channel_job" in ps_out or "telegram" in ps_out
    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "total_subscribers": total_subscribers,
            "subscribers": subscribers,
            "total_chats": total_chats,
            "publicaciones": publicaciones,
            "total_videos_ready": total_videos_ready,
            "total_tiktoks_published": total_tiktoks_published,
            "yt_bot_active": yt_bot_active,
            "telegram_bot_active": telegram_bot_active,
        }
    )

@app.post("/api/admin/generate-reply")
async def generate_admin_reply(request: Request):
    try:
        data = await request.json()
        comment = data.get("comment", "").strip()
        platform = data.get("platform", "tiktok").lower()
        transit_info = data.get("transit", "Mercurio Retrógrado en Escorpio en cuadratura a Marte en Leo / Luna en Leo oposición Plutón en Acuario")

        if not comment:
            return JSONResponse(status_code=400, content={"status": "error", "message": "El comentario no puede estar vacío"})

        prompt = f"""
Actúa como Tomás, astrólogo y creador de 'Portal Tarot Místico'.
Tus datos natales: Sol y Mercurio en Aries a 22°, Ascendente Acuario a 22°, Luna en Sagitario a 5°.
Tu personalidad: Directo, lúcido, magnético, eléctrico, sin vueltas, pedagógico y con gancho. Tono argentino natural y maduro (voseo: 'mirá', 'fijate', 'tenés', 'andá a ver').
PROHIBICIONES ESTRICTAS:
1. NADA de esnobismo ni melosidad ('bebé', 'mi amor', 'hermosa alma').
2. NADA de tenebrismo escabroso ni mórbido (cero sangre, cero autopsias, cero vísceras).
3. NADA de clichés new-age o paganos vacíos ('Samhain', 'códices sagrados', 'seres de luz').
4. REGLA DE ORO DE REDES:
   - Si la plataforma es TikTok: NUNCA coloques URLs crudas ('portaltarotmistico.com', 'https://...'). TikTok penaliza y oculta comentarios con enlaces externos. Usa SIEMPRE: "en el link de mi perfil" o "link en mi bio".
   - Si es YouTube: puedes sugerir "en el link fijado o en mi perfil".
5. CONTEXTO DE LA WEB: Tenemos una herramienta interactiva gratuita en vivo: el 'Reloj Astrológico 2D' (en el link de la bio). Allí el seguidor ingresa su fecha y hora natal y ve exactamente qué casas y planetas suyos reciben el impacto en grados reales.

COMENTARIO DEL SEGUIDOR EN {platform.upper()}:
"{comment}"

CONTEXTO ASTRAL ACTUAL:
{transit_info}

Genera 3 opciones de respuesta breves (máximo 2 a 3 oraciones cada una), personalizadas según lo que mencionó el seguidor (planetas, signos, casas):
1. 'directa': Punzante, rápida, al hueso (estilo Aries). Despierta curiosidad y manda al link en bio.
2. 'pedagogica': Explica brevemente la mecánica de las casas o planetas que mencionó el usuario (estilo Acuario/Sagitario) y lo invita a verificar sus grados en el reloj del perfil.
3. 'alquimica': Enfocada en cómo no chocar contra la energía sino transmutarla en poder personal, cerrando con el llamado a la bio.

Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
{{
  "directa": "texto de la respuesta directa...",
  "pedagogica": "texto de la respuesta pedagógica...",
  "alquimica": "texto de la respuesta alquímica..."
}}
"""

        replies = None
        if gemini_client:
            for model_candidate in ['gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash-lite']:
                try:
                    response = gemini_client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                    )
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                    replies = json.loads(text)
                    if isinstance(replies, dict) and "directa" in replies:
                        break
                except Exception as e_gen:
                    print(f"Error generando respuestas con {model_candidate}: {e_gen}")
                    continue

        if not replies or not isinstance(replies, dict):
            # Fallback inteligente con el ADN de Tomás
            replies = {
                "directa": f"¡Esa configuración no come vidrio! ⚡ Tensión pura para mover fichas grandes. Entrá al link de mi perfil y poné tus datos en el reloj: te canta al grado exacto dónde te pega y cómo usarlo a tu favor.",
                "pedagogica": f"Tremendo mapa. Cuando esos planetas tocan esas casas, el choque te obliga a hacer consciente lo que venías barriendo bajo la alfombra. En el link de mi bio tenés el reloj interactivo para ver en vivo los orbes exactos de tu tránsito.",
                "alquimica": f"La tensión planetaria no vino a romperte, vino a exigirte maestría. Si dejás de reaccionar y mirás el eje exacto, lo transmutás en poder. Pasate por el link en mi perfil que el reloj te lo muestra servido."
            }

        return JSONResponse(content={"status": "success", "replies": replies})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/subscribe")
async def subscribe(
    background_tasks: BackgroundTasks,
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
                ON CONFLICT(email) DO UPDATE SET
                    name=excluded.name,
                    birth_date=excluded.birth_date,
                    birth_time=excluded.birth_time,
                    birth_city=excluded.birth_city
            ''', (name, email, birth_date, birth_time, birth_city))
            
            # Caching Predictivo: Agendar descarga de assets pre-compra
            try:
                cursor.execute('''
                    INSERT INTO pending_video_tasks (user_email, video_type, status)
                    VALUES (?, ?, ?)
                ''', (email, 'predictive_cache', 'downloading_assets'))
            except sqlite3.OperationalError:
                pass

        # Generar análisis de carta natal en tiempo real
        analysis_html = None
        try:
            from content_factory.personalized_horoscope import PersonalizedHoroscope
            ph = PersonalizedHoroscope()
            res = ph.generate_for_user(name, birth_date, birth_time)
            analysis_html = res.get("mensaje_personalizado", "")
            
            # Enviar email asíncrono si está configurado
            if analysis_html and not res.get("error"):
                try:
                    email_body = f"<h1>Hola {name}, aquí está tu lectura inicial:</h1><br>" + analysis_html
                    background_tasks.add_task(send_email_with_audio, email, "Bienvenido al Oráculo - Tu Primera Lectura", email_body)
                except Exception as email_err:
                    print("Error agendando email:", email_err)
        except Exception as e_gen:
            print("Error generando análisis inicial:", e_gen)

        return JSONResponse(content={
            "status": "success",
            "message": "¡Tu carta astral ha sido forjada con precisión astronómica!",
            "analysis": analysis_html
        })
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
async def chat_with_oracle(request: Request):
    try:
        content_type = request.headers.get("content-type", "")
        email = None
        message = None
        if "application/json" in content_type:
            body = await request.json()
            email = body.get("email")
            message = body.get("question") or body.get("message")
        else:
            form = await request.form()
            email = form.get("email")
            message = form.get("message") or form.get("question")

        if not message:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Mensaje requerido."})

        name = "Buscador de Sentido"
        birth_date = "desconocida"
        birth_time = "desconocida"

        if email:
            try:
                with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, birth_date, birth_time FROM subscribers WHERE email = ?", (email,))
                    user = cursor.fetchone()
                    if user:
                        name, birth_date, birth_time = user
            except Exception as e_db:
                print("Error consultando usuario en chat:", e_db)

        prompt = f"""Eres el Oráculo Lúcido de 'Portal Tarot Místico' (Astrology Factory).
Tu estilo es el de un astrólogo clínico y filosófico: lúcido, empático, sin clichés de autoayuda barata ni predicciones de salón.
Estás dialogando con {name}, cuyos datos natales son: fecha {birth_date}, hora {birth_time}.
Responde a su inquietud con perspicacia psicológica y geométrica, ayudándolo a entender qué arquetipo o casa está operando.
Sé conciso (máximo 2 párrafos breves), cálido y revelador.

Mensaje de {name}: {message}
"""
        reply = None
        if gemini_client:
            for model_candidate in ['gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash-lite']:
                try:
                    response = gemini_client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                    )
                    reply = response.text
                    if reply:
                        break
                except Exception as e_gen:
                    print(f"Error generando chat con {model_candidate}: {e_gen}")
                    continue

        if not reply:
            reply = f"El mandala celeste se encuentra en plena marea de mutación, {name}. Cada aspecto que experimentas actúa como un catalizador en tu mapa de vida. Observa la casa donde la tensión se manifiesta: allí reside el punto exacto donde la sombra te pide comprensión antes que reacción."

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
            conn.commit()

        # Sincronizar también con el archivo JSON de Célula 4
        token_file = Path(PROJECT_DIR) / "v2" / "celula_4" / "tiktok_token.json"
        token_file.parent.mkdir(parents=True, exist_ok=True)
        import json, time
        json_resp["expires_at"] = time.time() + json_resp.get("expires_in", 86400) - 300
        with open(token_file, "w", encoding="utf-8") as f:
            json.dump(json_resp, f, indent=4)
    except Exception as e:
        return HTMLResponse(f"<h1>Error guardando en BD:</h1><p>{str(e)}</p>")
        
    return HTMLResponse('''
        <div style="background-color: #0d0d0d; color: white; font-family: sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1 style="color:#00f2fe;">¡Autorización Exitosa!</h1>
            <p>El Access Token de TikTok ha sido guardado. Tus células ya pueden publicar videos.</p>
            
            <div style="margin-top: 30px; padding: 20px; border: 1px solid #333; border-radius: 10px; text-align: center;">
                <h3 style="color:#ccc;">(Para Revisión / Producción de TikTok)</h3>
                <p style="color:#888; font-size: 14px;">Prueba el flujo End-to-End de subida de video (Content Posting API)</p>
                <form action="/api/tiktok/test_upload" method="post">
                    <button type="submit" style="background-color: #ff0050; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold;">Subir Video de Prueba a TikTok</button>
                </form>
            </div>
            
            <a href="/" style="color: #00f2fe; margin-top: 20px;">Volver al inicio</a>
        </div>
    ''')

@app.post("/api/tiktok/test_upload")
async def test_upload_tiktok():
    # Endpoint de prueba usando el motor robusto de Célula 4
    try:
        import sys
        celula_path = os.path.join(PROJECT_DIR, "v2", "celula_4")
        if celula_path not in sys.path:
            sys.path.insert(0, celula_path)
        from publicador_tiktok_api import upload_video
        
        # Ruta de un video de prueba en el servidor
        video_path = Path(PROJECT_DIR) / "test_blend.mp4"
        if not video_path.exists():
            return HTMLResponse(f"<h1>Error:</h1><p>No se encontró el video de prueba {video_path}</p>")
            
        privacy = os.environ.get("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE")
        ok = upload_video(
            video_path=str(video_path),
            description="Portal Tarot Místico - Test de Producción #astrologia #transitos",
            privacy_level=privacy
        )
        
        if ok:
            return HTMLResponse(f'''
                <div style="background-color: #0d0d0d; color: white; font-family: sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h1 style="color:#00f2fe;">¡Video Subido y Confirmado con Éxito! 🚀</h1>
                    <p>El video fue transmitido y verificado en TikTok con privacidad: <b>{privacy}</b>.</p>
                    <a href="/" style="color: #00f2fe; margin-top: 20px;">Volver al inicio</a>
                </div>
            ''')
        else:
            return HTMLResponse('''
                <div style="background-color: #0d0d0d; color: white; font-family: sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <h1 style="color:#ff0050;">Error en la Publicación</h1>
                    <p>TikTok rechazó la subida o falló la verificación. Revisa la consola o los logs del servidor.</p>
                    <a href="/" style="color: #00f2fe; margin-top: 20px;">Volver al inicio</a>
                </div>
            ''')
    except Exception as e:
        return HTMLResponse(f"<h1>Error Interno:</h1><p>{str(e)}</p>")
