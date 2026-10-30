#!/usr/bin/env python3
"""
🤖 YOUTUBE COMMENTS AUTO-RESPONDER DAEMON 24/7
Portal Tarot Místico — Persona: Tomás (Sol/Mercurio Aries 22°, Asc Acuario 22°, Luna Sagitario 5°)

Objetivo:
- Monitorear comentarios nuevos en los videos/Shorts del canal.
- Clasificar comentarios (Hater/Escéptico, Pregunta Genuina, Agradecimiento, Spam).
- Responder con la voz y psique de Tomás: tajante, pragmático, sin insultos (100% YouTube Policy Safe),
  desarmando falacias y lanzando preguntas punzantes para incentivar el debate en hilos y disparar el algoritmo.
- Convertir interacciones en tráfico hacia portaltarotmistico.com.
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
    "gemini-3.6-flash",
    "gemini-3.8-flash"
]

def obtener_api_keys():
    """Recolecta todas las API keys de Gemini para rotación."""
    keys = []
    for var in [
        "GEMINI_API_KEY", "GEMINI_API_KEY_TEXT", "GEMINI_API_KEY_WEB",
        "GEMINI_API_KEY_5", "GEMINI_API_KEY_6", "GEMINI_API_KEY_7",
        "GEMINI_API_KEY_8", "GEMINI_API_KEY_9", "GEMINI_API_KEY_10"
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
    # Migración suave si la tabla ya existía sin parent_id
    try:
        cur.execute("ALTER TABLE comentarios_respondidos ADD COLUMN parent_id TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def contar_intervenciones_hilo(parent_id):
    """Cuenta cuántas veces respondió Tomás en este hilo específico."""
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
    """Verifica si el comentario ya fue procesado."""
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

def generar_respuesta_ia(autor, texto_comentario, contexto_video="", historial_hilo=None, num_intervenciones_tomas=0):
    """
    Genera la respuesta con la psique canónica de Tomás.
    Inteligencia Multi-Turno & Anti-Loro:
    - Conoce el hilo completo de conversación si viene de un debate.
    - Límite de intervenciones (máximo 2 por hilo para actuar como humano y no saturar).
    - Regla Anti-Loro: Prohibido repetir enlaces en turnos secundarios.
    - Silencio Inteligente: No interrumpe discusiones orgánicas entre terceros.
    """
    if num_intervenciones_tomas >= 2:
        return "", "THREAD_SATURATED", False

    regla_segundo_turno = ""
    if num_intervenciones_tomas == 1:
        regla_segundo_turno = (
            "\nREGLA DE SEGUNDO TURNO (ANTI-LORO CRÍTICA):\n"
            "- Ya participaste antes en este hilo. ESTÁ TERMINANTEMENTE PROHIBIDO incluir enlaces web o mencionar 'portaltarotmistico.com'.\n"
            "- Respondé con pura dialéctica, filosofía irónica o análisis psicológico en 1 o 2 oraciones contundentes.\n"
            "- No actúes como un loro comercial ni como un asistente complaciente. Sé un creador humano que da una estocada lúcida y se retira.\n"
        )

    contexto_hilo_str = ""
    if historial_hilo and len(historial_hilo) > 0:
        hilo_formateado = "\n".join([f"- @{m.get('autor')}: \"{m.get('texto')}\"" for m in historial_hilo])
        contexto_hilo_str = f"\nHISTORIAL PREVIO DEL HILO:\n{hilo_formateado}\n"

    system_instruction = (
        "Eres Tomás, creador y director de 'Portal Tarot Místico'.\n"
        "Tu configuración astrológica: Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10.\n"
        "Estás respondiendo comentarios en tus videos de YouTube Shorts y transmisiones.\n\n"
        "TU IDENTIDAD Y TONO:\n"
        "- Lente Cognitiva (Acuario 22°): Tratas a la gente como mentes pensantes. No te ofendés por nada. Ves la crítica o el odio como un síntoma psicológico predecible o pereza cognitiva.\n"
        "- Asertividad y Filo (Aries 22°): Directo al hueso, tajante, sin vueltas ni diplomacia falsa. No pides permiso para decir la verdad.\n"
        "- Filosofía e Ironía Lúcida (Sagitario 5°): Voseo rioplatense sobrio y elegante ('mirá', 'fijate', 'te cuento'). Humor sutil, cero solemnidad.\n\n"
        "REGLAS DE INTERVENCIÓN NATURAL HUMANA:\n"
        "1. NO INTERRUMPIR DEBATES ENTRE TERCEROS: Si dos o más usuarios están debatiendo entre ellos y ninguno te pregunta nada a vos ni menciona tu nombre, marcá 'debe_responder': false. Dejá que la comunidad debata orgánicamente.\n"
        "2. NUNCA PARECER UN BOT O LORO: Variá el vocabulario. Si el usuario te responde a una pregunta previa, dialogá con lo que dijo en lugar de repetir un speech prearmado.\n"
        f"{regla_segundo_turno}\n"
        "PROTOCOLO ESTRICTO ANTE HATERS Y ESCÉPTICOS:\n"
        "1. PROHIBICIÓN ABSOLUTA DE OFENSAS O INSULTOS: Cumplimiento 100% de las normas de la comunidad de YouTube. Nunca insultes ni uses descalificaciones soeces.\n"
        "2. DESARME PRAGMÁTICO Y QUIRÚRGICO: Exponé con calma y filo la contradicción del hater. Quien opina de astrología sin haber calculado su carta natal con efemérides astronómicas exactas no es un escéptico, es simplemente alguien opinando a ciegas.\n"
        "3. INCENTIVO AL ALGORITMO: La respuesta DEBE ser provocadora a nivel intelectual y terminar con una pregunta incisiva o un desafío directo que obligue a la persona (o a otros espectadores) a responderte. Los hilos largos de debate son lo que más empuja el video en el feed de YouTube.\n"
        "4. EMBUDO A LA WEB (Solo en turno 1): Desafialo a calcular su carta natal gratis en portaltarotmistico.com con Swiss Ephemeris para verificar sus datos antes de proyectar sus prejuicios.\n\n"
        "PROTOCOLO ANTE PREGUNTAS GENUINAS:\n"
        "- Sé claro, pedagógico y pragmático. Explicá que el signo solar es solo una fracción y que el impacto real depende de las casas y grados matemáticos.\n\n"
        "PROTOCOLO ANTE ELOGIOS / AGRADECIMIENTOS:\n"
        "- Agradecé con sobriedad rioplatense. 'Gracias por la lucidez. La clave es observar el cielo como un mapa operativo, no como una creencia'.\n\n"
        "PROTOCOLO ANTE SPAM Y BOTS (REGLA ALGORÍTMICA):\n"
        "- ESTAFAS Y PHISHING (categoria: SPAM, debe_responder: false): Promociones crypto, números de WhatsApp falsos o enlaces dudosos. NO RESPONDER: YouTube degrada el score de los canales que interactúan con redes de estafa.\n"
        "- TROLLS Y BOTS GENÉRICOS (categoria: HATER_SKEPTIC, debe_responder: true): Si es un troll, hater o escéptico sin enlaces de estafa, RESPONDÉLE con el filo y la ironía de Tomás. La controversia limpia alimenta la retención y el algoritmo.\n\n"
        "FORMATO DE SALIDA:\n"
        "Devuelve ÚNICAMENTE un JSON con este esquema:\n"
        "{\n"
        "  \"categoria\": \"HATER_SKEPTIC\" | \"GENUINE_QUESTION\" | \"PRAISE\" | \"SPAM\",\n"
        "  \"debe_responder\": true | false,\n"
        "  \"respuesta\": \"Texto exacto de la respuesta en español rioplatense (máximo 1 o 2 oraciones contundentes)\"\n"
        "}"
    )

    prompt = (
        f"Comentario nuevo recibido de: @{autor}\n"
        f"Texto del comentario: \"{texto_comentario}\"\n"
        f"Contexto del video: {contexto_video}\n"
        f"{contexto_hilo_str}\n"
        f"Número de intervenciones previas de Tomás en este hilo: {num_intervenciones_tomas}\n\n"
        f"Analizá el hilo y generá la respuesta de Tomás siguiendo las directrices."
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
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )
                if resp and resp.text:
                    data = json.loads(resp.text.strip())
                    return data.get("respuesta", ""), data.get("categoria", "GENUINE_QUESTION"), data.get("debe_responder", True)
            except Exception as e:
                # Rotar si hay rate limit o fallo de modelo
                continue

    return None, "ERROR", False

def procesar_comentarios(video_id=None, max_results=15, modo_simulacion=False):
    """
    Lee comentarios de YouTube y responde a los pendientes.
    Si falta el scope youtube.force-ssl, registra la respuesta en la base
    como SIMULATED_PENDING_SCOPE para no perderla y notifica.
    """
    init_db()
    youtube = get_youtube_client()
    if not youtube:
        print("⚠️ [Daemon] No se pudo inicializar el cliente de YouTube. Verificando...")
        return

    print(f"[{datetime.now()}] 🔍 Buscando nuevos comentarios en YouTube...")
    try:
        if video_id:
            req = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="time"
            )
        else:
            req = youtube.commentThreads().list(
                part="snippet",
                allThreadsRelatedToChannelId=os.getenv("YOUTUBE_CHANNEL_ID", ""),
                maxResults=max_results,
                order="time"
            )
        res = req.execute()
    except googleapiclient.errors.HttpError as http_err:
        if http_err.resp.status == 403 and "insufficientPermissions" in str(http_err):
            print("⚠️ [Aviso de Scopes] El token.json actual solo tiene permisos de subida (youtube.upload).")
            print("💡 Para activar respuestas automáticas en vivo en YouTube, ejecuta:")
            print("   python3 v2/celula_4/configurador_oauth.py")
            print("   (Ya hemos añadido el scope 'youtube.force-ssl' en la configuración).")
            return
        elif http_err.resp.status == 400 and not video_id:
            # Si no se pasó channel ID o falla allThreads, probar con el último video publicado
            print("ℹ️ Reintentando búsqueda con video específico del contexto...")
            adn_file = PROJECT_ROOT / "contexto_astrologico.json"
            if adn_file.exists():
                # Video del 29 oct: yTI2hIFoyT8
                return procesar_comentarios(video_id="yTI2hIFoyT8", max_results=max_results, modo_simulacion=modo_simulacion)
        print(f"❌ Error al consultar comentarios de YouTube: {http_err}")
        return
    except Exception as e:
        print(f"❌ Error inesperado al consultar comentarios: {e}")
        return

    items = res.get("items", [])
    print(f"📥 Comentarios recibidos: {len(items)}")

    for item in items:
        top_level = item.get("snippet", {}).get("topLevelComment", {})
        c_id = top_level.get("id")
        snippet = top_level.get("snippet", {})
        autor = snippet.get("authorDisplayName", "Usuario")
        texto = snippet.get("textOriginal", "")
        v_id = snippet.get("videoId", video_id or "desconocido")

        if not c_id or ya_fue_respondido(c_id):
            continue

        print(f"\n💬 Procesando comentario de @{autor}: \"{texto[:60]}...\"")
        respuesta, categoria, debe_responder = generar_respuesta_ia(autor, texto, contexto_video=f"Video ID: {v_id}")

        if not debe_responder or categoria == "SPAM" or not respuesta:
            print(f"⏩ Comentario ignorado (Categoría: {categoria})")
            registrar_respuesta(c_id, v_id, autor, texto, categoria, "", "SKIPPED")
            continue

        print(f"⚡ [Categoría: {categoria}] Respuesta generada:")
        print(f"   {respuesta}")

        if modo_simulacion:
            registrar_respuesta(c_id, v_id, autor, texto, categoria, respuesta, "SIMULATED")
            print(f"✅ Guardado en base de datos (Modo Simulación).")
            continue

        # Intentar publicar la respuesta en YouTube
        try:
            insert_req = youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": c_id,
                        "textOriginal": respuesta
                    }
                }
            )
            insert_req.execute()
            registrar_respuesta(c_id, v_id, autor, texto, categoria, respuesta, "POSTED")
            print(f"🚀 ¡Respuesta publicada exitosamente en YouTube!")
        except googleapiclient.errors.HttpError as err:
            if "insufficientPermissions" in str(err) or err.resp.status == 403:
                print(f"⚠️ Guardado en SQLite (Pendiente de scope youtube.force-ssl).")
                registrar_respuesta(c_id, v_id, autor, texto, categoria, respuesta, "SIMULATED_PENDING_SCOPE")
            else:
                print(f"❌ Error al insertar comentario en YouTube: {err}")
        except Exception as e:
            print(f"❌ Error al publicar: {e}")

def run_daemon(interval_seconds=300):
    """Bucle infinito del demonio 24/7."""
    print("=" * 60)
    print("🤖 INICIANDO DAEMON DE COMENTARIOS DE YOUTUBE 24/7")
    print(f"⏱️ Intervalo de escaneo: {interval_seconds} segundos")
    print("🎯 Persona Tomás: Aries 22° / Acuario 22° / Sagitario 5°")
    print("=" * 60)

    while True:
        try:
            procesar_comentarios(video_id="yTI2hIFoyT8")
        except Exception as e:
            print(f"⚠️ Error en ciclo del demonio: {e}")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Comments Responder Daemon")
    parser.add_argument("--once", action="store_true", help="Ejecutar una sola vez y salir")
    parser.add_argument("--simular", action="store_true", help="Modo simulación sin escribir en YouTube")
    parser.add_argument("--video", type=str, default="yTI2hIFoyT8", help="ID del video a monitorear")
    parser.add_argument("--intervalo", type=int, default=300, help="Segundos entre escaneos en modo daemon")
    args = parser.parse_args()

    if args.once:
        procesar_comentarios(video_id=args.video, modo_simulacion=args.simular)
    else:
        run_daemon(interval_seconds=args.intervalo)
