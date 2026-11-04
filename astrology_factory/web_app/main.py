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

    response = templates.TemplateResponse(
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
    # Anti-caché estricto para evitar discrepancias Celular ↔ PC
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.post("/api/admin/registrar-manual")
async def registrar_publicacion_manual(request: Request):
    try:
        data = await request.json()
        fecha = data.get("fecha", "").strip()
        titulo = data.get("titulo", "").strip()
        youtube_url = data.get("youtube_url", "").strip()
        tiktok_url = data.get("tiktok_url", "").strip()
        
        if not fecha:
            return JSONResponse(status_code=400, content={"status": "error", "message": "La fecha es obligatoria (YYYY-MM-DD)"})
            
        reg_path = os.path.join(PROJECT_DIR, "produccion", "registro_publicaciones.json")
        reg_data = {"publicaciones": {}}
        if os.path.exists(reg_path):
            with open(reg_path, "r", encoding="utf-8") as f:
                reg_data = json.load(f)
                
        pubs = reg_data.setdefault("publicaciones", {})
        existente = pubs.get(fecha, {})
        
        pubs[fecha] = {
            "evento_id": existente.get("evento_id", f"{fecha}_Manual"),
            "titulo": titulo or existente.get("titulo", f"Tránsito {fecha}"),
            "youtube_video_id": existente.get("youtube_video_id"),
            "youtube_url": youtube_url or existente.get("youtube_url"),
            "tiktok_url": tiktok_url or existente.get("tiktok_url"),
            "estado_youtube": data.get("estado_youtube") or ("PUBLICADO" if youtube_url else existente.get("estado_youtube", "PUBLICADO")),
            "estado_tiktok": data.get("estado_tiktok") or ("PUBLICADO" if tiktok_url else existente.get("estado_tiktok", "PROGRAMADO")),
            "fecha_publicacion": fecha,
            "video_generado": True,
            "path_video": existente.get("path_video"),
            "estado_render": existente.get("estado_render", "MANUAL"),
            "origen": "REGISTRO_MANUAL_ADMIN"
        }
        
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(reg_data, f, indent=2, ensure_ascii=False)
            
        return JSONResponse({"status": "success", "message": f"Publicación del {fecha} guardada con éxito en el registro"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/admin/actualizar-estado-redes")
async def actualizar_estado_redes(request: Request):
    """Actualización rápida de estado (PUBLICADO/PROGRAMADO/PENDIENTE) desde el radar (1-Click Toggle)."""
    try:
        data = await request.json()
        fecha = data.get("fecha", "").strip()
        campo = data.get("campo", "").strip().lower()
        estado = data.get("estado", "").strip()
        
        if not fecha:
            return JSONResponse(status_code=400, content={"status": "error", "message": "La fecha es requerida"})
            
        reg_path = os.path.join(PROJECT_DIR, "produccion", "registro_publicaciones.json")
        if not os.path.exists(reg_path):
            return JSONResponse(status_code=404, content={"status": "error", "message": "Registro no encontrado"})
            
        with open(reg_path, "r", encoding="utf-8") as f:
            reg_data = json.load(f)
            
        pubs = reg_data.setdefault("publicaciones", {})
        pub = pubs.get(fecha)
        if not pub:
            return JSONResponse(status_code=404, content={"status": "error", "message": f"Evento de fecha {fecha} no encontrado"})
            
        # Actualización por campo directo (Toggle 1-Click)
        if campo == "youtube" and estado:
            pub["estado_youtube"] = estado
        elif campo == "tiktok" and estado:
            pub["estado_tiktok"] = estado
            
        # Soporte para payload directo
        if "estado_tiktok" in data:
            pub["estado_tiktok"] = data["estado_tiktok"]
        if "tiktok_url" in data and data["tiktok_url"]:
            pub["tiktok_url"] = data["tiktok_url"]
        if "estado_youtube" in data:
            pub["estado_youtube"] = data["estado_youtube"]
        if "youtube_url" in data and data["youtube_url"]:
            pub["youtube_url"] = data["youtube_url"]
            
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(reg_data, f, indent=2, ensure_ascii=False)
            
        return JSONResponse({
            "status": "success", 
            "message": f"Estado de {fecha} actualizado en {campo.upper() or 'redes'}",
            "estado_youtube": pub.get("estado_youtube"),
            "estado_tiktok": pub.get("estado_tiktok")
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/admin/astronomia-fecha")
async def obtener_astronomia_fecha(fecha: str):
    """Calcula datos astronómicos exactos de Swiss Ephemeris y cadena temporal para una fecha YYYY-MM-DD."""
    try:
        from datetime import datetime
        dt = datetime.strptime(fecha, "%Y-%m-%d")
        
        # 1. Calcular con Swiss Ephemeris
        from astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
        cielo = obtener_resumen_cielo_hoy(dt)
        
        # 2. Buscar en registro de publicaciones para la cadena temporal
        reg_path = os.path.join(PROJECT_DIR, "produccion", "registro_publicaciones.json")
        titulo_hoy = ""
        cadena_ayer = ""
        cadena_manana = ""
        if os.path.exists(reg_path):
            with open(reg_path, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
            pubs = reg.get("publicaciones", {})
            fechas = sorted(pubs.keys())
            if fecha in pubs:
                titulo_hoy = pubs[fecha].get("titulo", "")
                idx = fechas.index(fecha)
                if idx > 0:
                    f_prev = fechas[idx - 1]
                    cadena_ayer = f"{f_prev}: {pubs[f_prev].get('titulo', '')}"
                if idx < len(fechas) - 1:
                    f_next = fechas[idx + 1]
                    cadena_manana = f"{f_next}: {pubs[f_next].get('titulo', '')}"
                    
        return JSONResponse({
            "status": "success",
            "fecha": fecha,
            "titulo": titulo_hoy,
            "resumen_astronomico": cielo,
            "cadena_ayer": cadena_ayer,
            "cadena_manana": cadena_manana
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/admin/generate-reply")
async def generate_admin_reply(request: Request):
    try:
        data = await request.json()
        comment = data.get("comment", "").strip()
        platform = data.get("platform", "tiktok").lower()
        transit_info = data.get("transit", "Luna en Virgo inconjunción Neptuno / Luna en Leo conjunción Marte")
        cadena_temporal = data.get("cadena", "")
        cadena_str = f"\nCADENA TEMPORAL (AYER ↔ HOY ↔ MAÑANA):\n{cadena_temporal}\n" if cadena_temporal else ""

        if not comment:
            return JSONResponse(status_code=400, content={"status": "error", "message": "El comentario no puede estar vacío"})

        prompt = f"""
Actúa como Tomás, astrólogo y creador de 'Portal Tarot Místico'.
Tus datos natales: Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10.
Tu personalidad: Directo, lúcido, con chispa, canchero, empático y 100% humano. Voseo argentino rioplatense auténtico ('mirá', 'fijate', 'tenés', 'de una', 'jajaja', 'olvidate', 'posta', 'che').

REGLA DE ORO DE RESPUESTAS INDIVIDUALES (CERO AUTOBOMBO / CERO ROBOT):
1. ESTÁ TERMINANTEMENTE PROHIBIDO poner links, mencionar 'link en bio', 'mi perfil', 'portaltarotmistico.com' o mandar a ver el reloj. El llamado a la acción va ÚNICAMENTE en el comentario fijado (pinned comment), nunca en las respuestas a la gente.
2. Hablá como una persona de carne y hueso que charla con su comunidad en TikTok / YouTube: cercano, con onda, cero acartonamiento, cero sermones solemnes o de autoayuda.
3. Si el comentario es un chiste, ironía o algo casual, reite y seguile el juego. Si es una duda astrológica, contestale concreto y al pie con buena onda.

COMENTARIO DEL SEGUIDOR EN {platform.upper()}:
"{comment}"

CONTEXTO ASTRAL ACTUAL (Tránsitos y efemérides):
{transit_info}
{cadena_str}

Genera 3 opciones de respuesta breves, humanas y frescas (máximo 1 o 2 oraciones cada una):
1. 'directa': Rápida, canchera, al hueso (estilo Aries), con remate o humor si amerita.
2. 'pedagogica': Empática, explica la energía o responde la duda sin tecnicismos pesados (estilo Acuario/Sagitario), como un amigo que sabe de astrología.
3. 'alquimica': Disparadora o con repregunta curiosa que incite al usuario a seguir comentando para alimentar el algoritmo orgánicamente (sin enlaces).

Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
{{
  "directa": "texto de la respuesta directa...",
  "pedagogica": "texto de la respuesta pedagógica...",
  "alquimica": "texto de la respuesta disparadora..."
}}
"""

        replies = None
        if gemini_client:
            for model_candidate in ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']:
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
            replies = {
                "directa": "¡Totalmente! Esa energía no come vidrio: cuando se activa, o la dirigís vos o te pasa por encima ⚡",
                "pedagogica": "Es un aspecto intenso. La clave no es pelear contra la corriente sino ordenar lo que venías haciendo en piloto automático.",
                "alquimica": "¿Sentís que te está pegando más en lo personal o en el laburo? Contame cómo lo venís llevando 👇"
            }

        return JSONResponse(content={"status": "success", "replies": replies})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/admin/astral-consultant")
async def astral_consultant(request: Request):
    """Asesor astrológico rápido con contexto de tránsitos, videos y tono de Tomás."""
    try:
        data = await request.json()
        pregunta = data.get("pregunta", "").strip()
        fecha = data.get("fecha", "").strip()
        transit_info = data.get("transit", "").strip()
        cadena_temporal = data.get("cadena", "").strip()
        
        if not pregunta:
            return JSONResponse(status_code=400, content={"status": "error", "message": "La consulta no puede estar vacía"})

        prompt = f"""
Sos el Asesor Astrológico y Co-Piloto Creativo de Tomás (creador de Portal Tarot Místico).
Tu misión es darle a Tomás respuestas rápidas, lúcidas y súper prácticas sobre el estudio de los tránsitos que analizamos en los videos, o ayudarlo a pulir y reformular respuestas e ideas creativas.

PERFIL DE TOMÁS:
Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5°. Rioplatense, fresco, directo, cero clichés solemnes ni solemnidad new-age.

CONTEXTO ASTROLÓGICO DEL DÍA ({fecha or 'Activo'}):
- Aspectos / Efemérides: {transit_info or 'Tránsitos activos del ciclo'}
- Cadena temporal: {cadena_temporal or 'No especificada'}

CONSULTA / PEDIDO DE TOMÁS:
"{pregunta}"

INSTRUCCIONES DE RESPUESTA:
1. Sé súper claro, pragmático y al grano (máximo 2 párrafos o bullet points claros).
2. Si pide ideas de remate, ganchos o pulir un texto, dáselas listas para copiar en tono rioplatense fresco.
3. Si pregunta por casas, grados o mecánica astrológica, explicale el por qué concreto en la vida real sin rodeos académicos aburridos.
"""
        answer = None
        if gemini_client:
            for model_candidate in ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-3.5-flash']:
                try:
                    resp = gemini_client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                    )
                    if resp and resp.text:
                        answer = resp.text.strip()
                        break
                except Exception as e:
                    print(f"Error consultor astral con {model_candidate}: {e}")
                    continue
                    
        if not answer:
            answer = "Este tránsito pide foco y acción consciente. Es ideal para ordenar prioridades sin quemarse la cabeza con pequeñeces."
            
        return JSONResponse({"status": "success", "respuesta": answer})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/api/admin/generate-pinned-comment")
async def generate_admin_pinned_comment(request: Request):
    """Generador de Comentarios Fijados (Pinned Comments) de alta conversión y debate."""
    try:
        data = await request.json()
        platform = data.get("platform", "tiktok").lower()
        fecha = data.get("fecha", "3 de Noviembre").strip()
        transit = data.get("transit", "Luna entra en Virgo en inconjunción con Neptuno: ordenar sin quemarse la cabeza").strip()

        prompt = f"""
Actúa como Tomás, astrólogo y creador de 'Portal Tarot Místico'.
Tus datos natales: Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5°.
Tono: Auténtico argentino rioplatense, directo, lúcido, canchero y con chispa.
Misión: Redactar el PRIMER COMENTARIO FIJADO (Pinned Comment) para el video del día: {fecha} ({transit}).

REGLA CRÍTICA DE BREVEDAD (CERO PARRAFADAS):
- MÁXIMO 2 LÍNEAS CORTAS (menos de 120 caracteres en total). Debe leerse en 1 segundo en el celular sin botón 'ver más'.
- Si la plataforma es TikTok: Usa siempre 'en el link de mi perfil' o 'link en bio'.
- Si es YouTube: Usa 'portaltarotmistico.com'.

Genera 3 opciones ULTRA-BREVES:
1. 'conversion': Pregunta directa sobre el tránsito + llamado al reloj (ej: '🔮 ¿En qué casa te cae hoy? Te leo abajo 👇\\nReloj en vivo: {("portaltarotmistico.com" if platform == "youtube" else "link en mi bio")}')
2. 'comunidad': Pregunta para disparar debate y comentarios + link breve.
3. 'alquimica': Advertencia o consejo lúcido de 1 frase corta + link.

Responde ÚNICAMENTE en JSON con la siguiente estructura:
{{
  "conversion": "línea 1\\nlínea 2",
  "comunidad": "línea 1\\nlínea 2",
  "alquimica": "línea 1\\nlínea 2"
}}
"""
        pinned = None
        if gemini_client:
            for model_candidate in ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite']:
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
                    pinned = json.loads(text)
                    if isinstance(pinned, dict) and "conversion" in pinned:
                        break
                except Exception as e_gen:
                    print(f"Error generando pinned comment con {model_candidate}: {e_gen}")
                    continue

        link_dest = "portaltarotmistico.com" if platform == "youtube" else "link en mi bio"
        if not pinned or not isinstance(pinned, dict):
            pinned = {
                "conversion": f"🔮 ¿En qué casa te cae hoy? Te leo abajo 👇\nReloj interactivo en vivo: {link_dest}",
                "comunidad": f"👇 Contame tu signo y casa. Los leo a todos.\nVer grados exactos: {link_dest}",
                "alquimica": f"⚡ No luches contra lo que hoy se ordena.\nChequeá tu mapa al grado exacto: {link_dest}"
            }

        return JSONResponse(content={
            "status": "success", 
            "pinned": pinned,
            "pinned_comments": {
                "conversion": pinned.get("conversion", ""),
                "community": pinned.get("comunidad", pinned.get("community", "")),
                "alchemical": pinned.get("alquimica", pinned.get("alchemical", ""))
            }
        })
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
