#!/usr/bin/env python3
"""
🤖 YOUTUBE COMMENTS AUTO-RESPONDER DAEMON 24/7 (Multi-Turno + Tono Fresco Rioplatense)
Portal Tarot Místico — Persona: Tomás (Sol/Mercurio Aries 22°, Asc Acuario 22°, Luna Sagitario 5°)

Objetivo:
- Monitorear comentarios nuevos y respuestas a hilos en los videos/Shorts del canal.
- Detección inteligente de hilos (Multi-Turno): Si un usuario re-contesta, Tomás sigue la charla naturalmente.
- Tono 100% fresco, rioplatense, pícaro, cercano y humano (CERO robot, cero solemnidad, cero sermones).
- Soporte para generar y publicar el primer comentario fijado (Pinned Comment).
- Persistencia e idempotencia estricta en SQLite.
"""

import os
import sys
import time
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Asegurar importación de rutas de la factoría
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
for p in [str(PROJECT_ROOT), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

if (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
elif (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
else:
    load_dotenv()

from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import googleapiclient.errors

DB_PATH = PROJECT_ROOT / "database" / "youtube_comments.sqlite"
TOKEN_PATH = PROJECT_ROOT / "v2" / "celula_4" / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

MODEL_CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite"
]

def obtener_api_keys():
    """Recolecta todas las API keys de Gemini para rotación, priorizando las más rápidas."""
    keys = []
    for var in [
        "GEMINI_API_KEY_WEB", "GEMINI_API_KEY_WEB_TEXT", "GEMINI_API_KEY_TEXT",
        "GEMINI_API_KEY", "GEMINI_API_KEY_5", "GEMINI_API_KEY_6",
        "GEMINI_API_KEY_7", "GEMINI_API_KEY_8", "GEMINI_API_KEY_9", "GEMINI_API_KEY_10"
    ]:
        v = os.getenv(var)
        if v and v not in keys:
            keys.append(v)
    for k, v in os.environ.items():
        if k.startswith("GEMINI_API_KEY") and v and v not in keys:
            keys.append(v)
    return keys

def init_db():
    """Crea la tabla de comentarios si no existe y asegura columnas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comentarios_respondidos (
            comment_id TEXT PRIMARY KEY,
            parent_id TEXT,
            video_id TEXT,
            author_name TEXT,
            comment_text TEXT,
            categoria TEXT,
            respuesta_ia TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied_at TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE comentarios_respondidos ADD COLUMN parent_id TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def contar_intervenciones_hilo(parent_id):
    """Cuenta cuántas veces respondió Tomás en este hilo específico según la base de datos."""
    if not parent_id:
        return 0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM comentarios_respondidos 
        WHERE (parent_id = ? OR comment_id = ?) AND status IN ('POSTED', 'SIMULATED')
    """, (parent_id, parent_id))
    cnt = cur.fetchone()[0]
    conn.close()
    return cnt

def ya_fue_respondido(comment_id):
    """Verifica si este comentario puntual ya fue procesado."""
    if not comment_id:
        return True
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM comentarios_respondidos WHERE comment_id = ?", (comment_id,))
    res = cur.fetchone()
    conn.close()
    return res is not None

def registrar_respuesta(comment_id, video_id, author_name, comment_text, categoria, respuesta_ia, status, parent_id=None):
    """Guarda la respuesta en SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO comentarios_respondidos 
        (comment_id, parent_id, video_id, author_name, comment_text, categoria, respuesta_ia, status, replied_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (comment_id, parent_id, video_id, author_name, comment_text, categoria, respuesta_ia, status, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_youtube_client():
    """Obtiene el cliente autenticado de YouTube."""
    if not TOKEN_PATH.exists():
        print("❌ [YouTube Client] No se encontró token.json en v2/celula_4/token.json")
        return None
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_PATH, 'w') as f:
                    f.write(creds.to_json())
            else:
                print("⚠️ [YouTube Client] El token está expirado y sin refresh_token.")
                return None
        return googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"⚠️ [YouTube Client] Error al cargar credenciales: {e}")
        return None

def obtener_contexto_video(v_id):
    """Obtiene título, contexto y cadena temporal del video a partir de su ID."""
    contexto_video = f"Video ID: {v_id}"
    cadena_temporal = ""
    try:
        reg_path = PROJECT_ROOT / "produccion" / "registro_publicaciones.json"
        if reg_path.exists():
            with open(reg_path, "r", encoding="utf-8") as rf:
                reg_data = json.load(rf)
            pubs = reg_data.get("publicaciones", {})
            fechas = sorted(pubs.keys())
            for idx, f_key in enumerate(fechas):
                pub = pubs[f_key]
                if pub.get("youtube_video_id") == v_id:
                    contexto_video = f"Video de fecha {f_key}: '{pub.get('titulo')}'"
                    partes = []
                    if idx > 0:
                        f_prev = fechas[idx - 1]
                        partes.append(f"- AYER ({f_prev}): '{pubs[f_prev].get('titulo')}'")
                    partes.append(f"- HOY ({f_key} - ESTE VIDEO): '{pub.get('titulo')}'")
                    if idx < len(fechas) - 1:
                        f_next = fechas[idx + 1]
                        partes.append(f"- MAÑANA ({f_next}): '{pubs[f_next].get('titulo')}'")
                    cadena_temporal = "\n".join(partes)
                    break
    except Exception:
        pass
    return contexto_video, cadena_temporal

def generar_respuesta_ia(autor, texto_comentario, contexto_video="", cadena_temporal="", historial_hilo=None, num_intervenciones_tomas=0):
    """
    Genera la respuesta con la personalidad fresca y canónica de Tomás.
    Voz: Joven, argentino (voseo), canchero, lúcido, con chispa, cero robot/pastor.
    Multi-turno: Conoce el hilo completo y responde en contexto natural.
    """
    if num_intervenciones_tomas >= 2:
        return "", "THREAD_SATURATED", False

    regla_segundo_turno = ""
    if num_intervenciones_tomas >= 1:
        regla_segundo_turno = (
            "\nREGLA DE SEGUNDO TURNO (RE-RESPUESTA DEL USUARIO):\n"
            "- Ya charlaste con este usuario antes en este hilo y te acaba de re-contestar.\n"
            "- TERMINANTEMENTE PROHIBIDO poner enlaces o promocionar la web.\n"
            "- Seguile la conversación a lo que acaba de decir. Si tiró un chiste, reite ('jajaja tal cual') y hacé un remate gracioso o cómplice.\n"
            "- Cerrá la interacción con calidez y naturalidad humana en 1 o 2 oraciones cortitas.\n"
        )

    contexto_hilo_str = ""
    if historial_hilo and len(historial_hilo) > 0:
        hilo_formateado = "\n".join([f"- @{m.get('autor')}: \"{m.get('texto')}\"" for m in historial_hilo])
        contexto_hilo_str = f"\nHISTORIAL COMPLETO DEL HILO HASTA AHORA:\n{hilo_formateado}\n"

    system_instruction = (
        "Sos Tomás, creador de 'Portal Tarot Místico'. Tu carta natal: Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10.\n"
        "Estás respondiendo comentarios en tus videos de YouTube (Shorts y videos largos) desde tu celular, charlando mano a mano con tu gente.\n\n"
        "PERSONALIDAD Y ESTILO (100% HUMANO Y FRESCO):\n"
        "- Voseo rioplatense genuino: 'mirá', 'fijate', 'contame', 'de una', 'olvidate', 'posta', 'jajaja', 'che'.\n"
        "- Actitud: Canchero, lúcido, con chispa, sin pelos en la lengua, pero re buena onda y cómplice con la comunidad.\n"
        "- CERO ROBOT, CERO SOLEMNIDAD: Terminantemente prohibido hablar como profesor, predicador o gurú de autoayuda. NUNCA uses frases acartonadas como 'el mapa operativo', 'despejar el humo', 'pereza cognitiva' o sermones sobre la vida.\n"
        "- HUMOR Y REFLEJOS RÁPIDOS: Si el usuario tira un chiste, ironía o algo casual (ej: 'las nubes que me cortan internet jajaj'), no te pongas a filosofar. Reite y seguile el juego con picardía y un remate divertido ('Jajajaja contra el wifi y las tormentas no hay tránsito en Escorpio que te salve 💀').\n"
        "- CONCISIÓN: Respuestas cortas (1 o 2 oraciones breves máximo). Que parezca escrito en 5 segundos por alguien de carne y hueso.\n\n"
        "PAUTAS POR TIPO DE COMENTARIO:\n"
        "1. CHISTES / COMENTARIOS CASUALES / INFORMALES: Responder con humor, risa y complicidad.\n"
        "2. BUENA ONDA / ELOGIOS / MANIFESTACIÓN ('abundancia!', 'genio', 'gracias'): Responder con buena vibra, calidez y entusiasmo sincero, sin juzgar ni dar lecciones ('¡De una! Que se destrabe todo lo que esté frenado 🙌 ¿Por dónde sentís que viene, laburo o proyectos?').\n"
        "3. PREGUNTAS ASTROLÓGICAS REALES: Explicá cortito y al pie, con onda práctica.\n"
        "4. HATERS / ESCÉPTICOS: Ironía tranquila, sin insultos ni enojo. Picante pero simpático ('Jajaja el típico que opina sin haber visto ni un grado de su carta. Calculala primero y después me contás 😉').\n"
        "5. REGLA ANTI-SPAM DE ENLACES: Prohibido spamear 'portaltarotmistico.com' o links en cada respuesta. Solo sugerir la web o el reloj astrológico si el usuario pregunta explícitamente por su carta natal, compatibilidad o grados matemáticos.\n"
        f"{regla_segundo_turno}\n"
        "FORMATO DE SALIDA:\n"
        "Devuelve ÚNICAMENTE un JSON con este esquema:\n"
        "{\n"
        "  \"categoria\": \"HATER_SKEPTIC\" | \"GENUINE_QUESTION\" | \"PRAISE\" | \"SPAM\",\n"
        "  \"debe_responder\": true | false,\n"
        "  \"respuesta\": \"Texto exacto de la respuesta en español rioplatense (1 o 2 oraciones breves y frescas)\"\n"
        "}"
    )

    cadena_str = f"\nCADENA TEMPORAL DE TRÁNSITOS DEL CANAL:\n{cadena_temporal}\n" if cadena_temporal else ""
    prompt = (
        f"Comentario a responder de: @{autor}\n"
        f"Texto del comentario: \"{texto_comentario}\"\n"
        f"Contexto del video actual: {contexto_video}\n"
        f"{cadena_str}"
        f"{contexto_hilo_str}\n"
        f"Número de intervenciones previas de Tomás en este hilo: {num_intervenciones_tomas}\n\n"
        f"Respondé como Tomás con frescura y naturalidad humana."
    )

    keys = obtener_api_keys()
    if not keys:
        return None, "SPAM", False

    for model in MODEL_CANDIDATES:
        for key in keys:
            try:
                client = genai.Client(api_key=key)
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.8,
                        response_mime_type="application/json"
                    )
                )
                if resp and resp.text:
                    clean_text = resp.text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.startswith("```"):
                        clean_text = clean_text[3:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    clean_text = clean_text.strip()
                    data = json.loads(clean_text)
                    return data.get("respuesta", ""), data.get("categoria", "GENUINE_QUESTION"), data.get("debe_responder", True)
            except Exception:
                continue

    return None, "ERROR", False

def generar_comentario_fijado_ia(contexto_video="", cadena_temporal=""):
    """Genera un comentario inicial ultra-breve y magnético para fijar (Pinned Comment)."""
    prompt = (
        f"Contexto del video: {contexto_video}\n"
        f"Cadena temporal: {cadena_temporal}\n\n"
        "Redacta el PRIMER COMENTARIO FIJADO (Pinned Comment) para este video de YouTube Shorts / canal.\n"
        "REGLA CRÍTICA DE BREVEDAD:\n"
        "- Máximo 2 líneas muy cortas (menos de 120 caracteres en total). Cero textos largos.\n"
        "- Debe leerse completo de un vistazo en el celular sin que YouTube corte con 'ver más'.\n"
        "- Línea 1: Pregunta directa y canchera al hueso para incentivar comentarios (ej: '👁️ ¿En qué casa te cae hoy? Los leo acá abajo 👇')\n"
        "- Línea 2: Enlace directo y limpio al reloj (ej: 'Reloj en vivo al grado exacto: portaltarotmistico.com')\n"
        "Devuelve ÚNICAMENTE las 2 líneas de texto, sin comillas ni preámbulos."
    )
    keys = obtener_api_keys()
    for model in MODEL_CANDIDATES:
        for key in keys:
            try:
                client = genai.Client(api_key=key)
                resp = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7
                    )
                )
                if resp and resp.text:
                    texto = resp.text.strip().strip('"')
                    return texto
            except Exception:
                continue
    return "👁️ ¿En qué casa te cae hoy? Te leo abajo 👇\nReloj en vivo al grado exacto: portaltarotmistico.com"

def publicar_comentario_fijado(video_id, texto=None, modo_simulacion=False):
    """Publica un comentario de primer nivel para fijar en el video."""
    youtube = get_youtube_client()
    if not youtube:
        print("❌ [Pinned Comment] No se pudo autenticar cliente de YouTube.")
        return False

    contexto_video, cadena_temporal = obtener_contexto_video(video_id)
    if not texto:
        texto = generar_comentario_fijado_ia(contexto_video, cadena_temporal)

    print(f"\n📌 [Pinned Comment] Video {video_id}:")
    print(f"   \"{texto}\"")

    if modo_simulacion:
        print("✅ [Modo Simulación] Comentario no enviado a la API de YouTube.")
        return True

    try:
        req = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": texto
                        }
                    }
                }
            }
        )
        res = req.execute()
        new_id = res.get("id")
        print(f"🚀 ¡Comentario inicial publicado exitosamente! (ID: {new_id})")
        print("💡 Podés entrar a YouTube Studio y hacer clic en 'Fijar' para que quede arriba de todo.")
        registrar_respuesta(new_id, video_id, "@portaltarotmistico", texto, "PINNED_COMMENT", texto, "POSTED")
        return True
    except Exception as e:
        print(f"❌ Error al publicar comentario fijado: {e}")
        return False

def procesar_comentarios(video_id=None, max_results=20, modo_simulacion=False):
    """
    Lee comentarios de YouTube y responde inteligentemente a los pendientes,
    soportando tanto comentarios raíz como respuestas anidadas (hilos multi-turno).
    """
    init_db()
    youtube = get_youtube_client()
    if not youtube:
        print("⚠️ [Daemon] No se pudo inicializar el cliente de YouTube. Verificando credenciales...")
        return

    CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCaSKtvaO4kGR9yVUIQEknaA")
    print(f"[{datetime.now()}] 🔍 Buscando nuevos comentarios en YouTube...")
    try:
        if video_id:
            req = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=max_results,
                order="time"
            )
        else:
            req = youtube.commentThreads().list(
                part="snippet,replies",
                allThreadsRelatedToChannelId=CHANNEL_ID,
                maxResults=max_results,
                order="time"
            )
        res = req.execute()
    except googleapiclient.errors.HttpError as http_err:
        if http_err.resp.status == 403 and "insufficientPermissions" in str(http_err):
            print("⚠️ [Aviso de Scopes] Se requiere el scope 'youtube.force-ssl'.")
            return
        elif http_err.resp.status == 400 and not video_id:
            # Fallback a video reciente si falla búsqueda general
            print("ℹ️ Reintentando búsqueda con video del registro...")
            reg_path = PROJECT_ROOT / "produccion" / "registro_publicaciones.json"
            if reg_path.exists():
                try:
                    with open(reg_path, "r", encoding="utf-8") as rf:
                        reg_data = json.load(rf)
                    pubs = reg_data.get("publicaciones", {})
                    for f_key in sorted(pubs.keys(), reverse=True):
                        v_id = pubs[f_key].get("youtube_video_id")
                        if v_id:
                            return procesar_comentarios(video_id=v_id, max_results=max_results, modo_simulacion=modo_simulacion)
                except Exception:
                    pass
        print(f"❌ Error al consultar comentarios de YouTube: {http_err}")
        return
    except Exception as e:
        print(f"❌ Error inesperado al consultar comentarios: {e}")
        return

    items = res.get("items", [])
    print(f"📥 Hilos de comentarios recibidos: {len(items)}")

    for item in items:
        thread_id = item.get("id")
        top_level = item.get("snippet", {}).get("topLevelComment", {})
        top_snippet = top_level.get("snippet", {})
        top_author = top_snippet.get("authorDisplayName", "Usuario")
        top_text = top_snippet.get("textOriginal", "")
        v_id = top_snippet.get("videoId", video_id or "desconocido")
        top_author_channel_id = top_snippet.get("authorChannelId", {}).get("value")

        # 1. Obtener contexto del video
        contexto_video, cadena_temporal = obtener_contexto_video(v_id)

        # 2. Respuestas en el hilo
        replies_raw = item.get("replies", {}).get("comments", [])
        total_reply_count = item.get("snippet", {}).get("totalReplyCount", len(replies_raw))

        # Si hay más respuestas que las devueltas en snippet, traer el hilo completo
        if total_reply_count > len(replies_raw):
            try:
                full_replies_req = youtube.comments().list(
                    part="snippet",
                    parentId=thread_id,
                    maxResults=50
                )
                full_res = full_replies_req.execute()
                replies_raw = full_res.get("items", [])
            except Exception:
                pass

        # Ordenar cronológicamente (antiguos primero, recientes al final)
        replies_sorted = sorted(replies_raw, key=lambda x: x.get("snippet", {}).get("publishedAt", ""))

        # Construir historial completo del debate
        historial_hilo = [{"autor": top_author, "texto": top_text}]
        for r in replies_sorted:
            r_snip = r.get("snippet", {})
            historial_hilo.append({
                "autor": r_snip.get("authorDisplayName", "Usuario"),
                "texto": r_snip.get("textOriginal", "")
            })

        # 3. Contar intervenciones previas de Tomás en este hilo
        intervenciones_live = 0
        if top_author_channel_id == CHANNEL_ID or top_author.lower() in ["@portaltarotmistico", "portaltarotmistico"]:
            intervenciones_live += 1
        for r in replies_sorted:
            r_snip = r.get("snippet", {})
            r_auth = r_snip.get("authorDisplayName", "").lower()
            r_ch = r_snip.get("authorChannelId", {}).get("value")
            if r_ch == CHANNEL_ID or r_auth in ["@portaltarotmistico", "portaltarotmistico"]:
                intervenciones_live += 1

        num_intervenciones = max(contar_intervenciones_hilo(thread_id), intervenciones_live)

        # 4. Determinar si hay un mensaje nuevo al que responder
        target_comment_id = None
        target_author = None
        target_text = None

        if not replies_sorted:
            # Caso A: Hilo sin respuestas aún (solo el comentario raíz)
            if not ya_fue_respondido(thread_id):
                if top_author_channel_id != CHANNEL_ID and top_author.lower() not in ["@portaltarotmistico", "portaltarotmistico"]:
                    target_comment_id = thread_id
                    target_author = top_author
                    target_text = top_text
        else:
            # Caso B: Hilo con respuestas. Miramos el último comentario de la cadena
            last_reply = replies_sorted[-1]
            last_snip = last_reply.get("snippet", {})
            last_id = last_reply.get("id")
            last_author = last_snip.get("authorDisplayName", "Usuario")
            last_text = last_snip.get("textOriginal", "")
            last_channel_id = last_snip.get("authorChannelId", {}).get("value")

            # Si el último comentario fue del canal de Tomás, no hay nada pendiente que responder
            if last_channel_id == CHANNEL_ID or last_author.lower() in ["@portaltarotmistico", "portaltarotmistico"]:
                continue

            # Si este comentario del usuario ya fue procesado, no repetir
            if ya_fue_respondido(last_id):
                continue

            # Si Tomás ya intervino 2 veces en este hilo, no saturar al usuario
            if num_intervenciones >= 2:
                print(f"⏩ Hilo {thread_id} completó {num_intervenciones} intervenciones. Dejando espacio.")
                registrar_respuesta(last_id, v_id, last_author, last_text, "THREAD_SATURATED", "", "SKIPPED", parent_id=thread_id)
                continue

            target_comment_id = last_id
            target_author = last_author
            target_text = last_text

        if not target_comment_id:
            continue

        print(f"\n💬 Procesando intervención en hilo (Turno {num_intervenciones + 1})")
        print(f"   Autor: @{target_author} | Texto: \"{target_text}\"")

        respuesta, categoria, debe_responder = generar_respuesta_ia(
            target_author, 
            target_text, 
            contexto_video=contexto_video, 
            cadena_temporal=cadena_temporal,
            historial_hilo=historial_hilo,
            num_intervenciones_tomas=num_intervenciones
        )

        if not debe_responder or categoria == "SPAM" or not respuesta:
            print(f"⏩ Comentario ignorado (Categoría: {categoria})")
            registrar_respuesta(target_comment_id, v_id, target_author, target_text, categoria, "", "SKIPPED", parent_id=thread_id)
            continue

        print(f"⚡ [Categoría: {categoria}] Respuesta generada:")
        print(f"   {respuesta}")

        if modo_simulacion:
            registrar_respuesta(target_comment_id, v_id, target_author, target_text, categoria, respuesta, "SIMULATED", parent_id=thread_id)
            print(f"✅ Guardado en base de datos (Modo Simulación).")
            continue

        # Publicar la respuesta en el hilo (en YouTube, parentId siempre es el ID del hilo raíz)
        try:
            insert_req = youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": thread_id,
                        "textOriginal": respuesta
                    }
                }
            )
            insert_req.execute()
            registrar_respuesta(target_comment_id, v_id, target_author, target_text, categoria, respuesta, "POSTED", parent_id=thread_id)
            print(f"🚀 ¡Respuesta publicada exitosamente en YouTube!")
        except googleapiclient.errors.HttpError as err:
            if "insufficientPermissions" in str(err) or err.resp.status == 403:
                print(f"⚠️ Guardado en SQLite (Pendiente de scope youtube.force-ssl).")
                registrar_respuesta(target_comment_id, v_id, target_author, target_text, categoria, respuesta, "SIMULATED_PENDING_SCOPE", parent_id=thread_id)
            else:
                print(f"❌ Error al insertar comentario en YouTube: {err}")
        except Exception as e:
            print(f"❌ Error al publicar: {e}")

def run_daemon(interval_seconds=60, video_id=None):
    """Bucle infinito del demonio 24/7."""
    print("=" * 60)
    print("🤖 INICIANDO DAEMON DE COMENTARIOS DE YOUTUBE 24/7 (Multi-Turno)")
    print(f"⏱️ Intervalo de escaneo: {interval_seconds} segundos")
    print(f"🎯 Modo: {'Canal completo (todos los videos)' if not video_id else f'Video específico: {video_id}'}")
    print("🎯 Persona Tomás: Rioplatense fresco / Aries 22° / Acuario 22° / Sagitario 5°")
    print("=" * 60)

    while True:
        try:
            procesar_comentarios(video_id=video_id)
        except Exception as e:
            print(f"⚠️ Error en ciclo del demonio: {e}")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Comments Responder Daemon (Multi-Turno + Pinned)")
    parser.add_argument("--once", action="store_true", help="Ejecutar una sola vez y salir")
    parser.add_argument("--simular", action="store_true", help="Modo simulación sin escribir en YouTube")
    parser.add_argument("--video", type=str, default=None, help="ID de un video específico (por defecto: monitorea todo el canal)")
    parser.add_argument("--intervalo", type=int, default=60, help="Segundos entre escaneos en modo daemon (default: 60)")
    parser.add_argument("--fijar", action="store_true", help="Generar y publicar un comentario fijado para el video indicado en --video")
    parser.add_argument("--texto-fijar", type=str, default=None, help="Texto manual para el comentario fijado (opcional)")
    args = parser.parse_args()

    if args.fijar:
        if not args.video:
            print("❌ Para fijar un comentario debes especificar --video <ID_DEL_VIDEO>")
            sys.exit(1)
        publicar_comentario_fijado(args.video, texto=args.texto_fijar, modo_simulacion=args.simular)
    elif args.once:
        procesar_comentarios(video_id=args.video, modo_simulacion=args.simular)
    else:
        run_daemon(interval_seconds=args.intervalo, video_id=args.video)
