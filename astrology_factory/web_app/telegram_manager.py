import os
import sys
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "users.sqlite")

load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ Error: Falta TELEGRAM_BOT_TOKEN en .env")
    sys.exit(1)

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-3.6-flash"
]

def obtener_api_keys():
    keys = []
    for var_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_5", "GEMINI_API_KEY_6", "GEMINI_API_KEY_7", "GEMINI_API_KEY_TEXT", "GEMINI_API_KEY_WEB"]:
        val = os.getenv(var_name)
        if val and val not in keys:
            keys.append(val)
    return keys

def get_user_by_telegram_id(chat_id):
    """Busca al usuario en SQLite por su telegram_id permanente."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, birth_date, birth_time, birth_city FROM subscribers WHERE telegram_id = ?", (str(chat_id),))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error DB get_user: {e}")
        return None

def vincular_telegram_id(email, chat_id, username=None):
    """Guarda permanentemente el telegram_id en SQLite."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subscribers SET telegram_id = ?, telegram_username = ? WHERE lower(email) = lower(?)",
                (str(chat_id), str(username or ""), email.strip())
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error vinculando telegram_id: {e}")
        return False

def registrar_solicitud_pendiente(chat_id, email, request_type="horoscopo_hoy", error_msg=""):
    """Guarda en pending_telegram_requests si la IA falló para reintentar luego."""
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO pending_telegram_requests (chat_id, email, request_type, status, error_log)
                VALUES (?, ?, ?, 'pending', ?)
            ''', (str(chat_id), email, request_type, str(error_msg)[:300]))
            conn.commit()
            print(f"📌 Solicitud agendada para chat {chat_id} ({email}).")
    except Exception as e:
        print(f"Error guardando solicitud pendiente: {e}")

def llamar_ia_con_reintentos(prompt, system_instruction=None):
    """Intenta generar contenido rotando modelos y keys."""
    keys = obtener_api_keys()
    if not keys:
        return None

    for api_key in keys:
        for model_name in MODEL_CANDIDATES:
            try:
                client = genai.Client(api_key=api_key)
                config = types.GenerateContentConfig(temperature=0.7)
                if system_instruction:
                    config.system_instruction = system_instruction

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                # Intentar siguiente modelo o key
                continue
    return None

def generar_horoscopo_personalizado_texto(name, birth_date, birth_time, birth_city=""):
    today_str = datetime.now().strftime("%Y-%m-%d")
    system_instruction = (
        "Eres un Astrólogo profesional, cálido y profundo de 'Portal Tarot Místico'. "
        "Tu misión es redactar un 'Horóscopo y Clima Astral Personalizado' para el día de hoy, "
        "cruzando los tránsitos celestes actuales con la Carta Natal del consultante. "
        "Habla en segunda persona ('tú' o 'vos' rioplatense austero y cercano). "
        "Sé conciso pero inspirador, enfócate en el área de vida activada hoy (emocional, mental, decisiones o propósito). "
        "Usa emojis sobrios y cierra con una reflexión o consejo concreto de autor."
    )
    prompt = f"""Consultante: {name}
Fecha de nacimiento natal: {birth_date} a las {birth_time} (Lugar: {birth_city or 'No especificado'}).
Fecha actual del tránsito: {today_str}.

Por favor, redacta su reporte astral personalizado para hoy."""

    return llamar_ia_con_reintentos(prompt, system_instruction)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username if update.effective_user else ""
    user = get_user_by_telegram_id(chat_id)
    args = context.args or []

    # Caso 1: El usuario vino desde el botón del canal [start=horoscopo_hoy]
    if args and args[0] == "horoscopo_hoy":
        if user:
            user_id, name, email, birth_date, birth_time, birth_city = user
            await update.message.reply_text(
                f"✨ Saludos, {name}. Conectando con tu Carta Natal ({birth_date} · {birth_time})...\n"
                "Sintonizando los tránsitos de hoy para ti..."
            )
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            
            horoscopo = generar_horoscopo_personalizado_texto(name, birth_date, birth_time, birth_city)
            if horoscopo:
                await update.message.reply_text(horoscopo)
            else:
                # Persistencia en caso de fallo
                registrar_solicitud_pendiente(chat_id, email, request_type="horoscopo_hoy", error_msg="IA indisponible temporalmente")
                await update.message.reply_text(
                    "🌌 Tu solicitud ha quedado agendada en el Oráculo.\n\n"
                    "En este momento los canales cósmicos están experimentando alta demanda. "
                    "Tan pronto como se despejen, te entregaremos tu lectura personalizada aquí mismo de forma automática."
                )
        else:
            await update.message.reply_text(
                "🔮 *Horóscopo Diario Personalizado*\n\n"
                "Para calcular tu clima astral exacto, necesitamos conectarte con tu Carta Natal.\n\n"
                "• **Si ya estás registrado en la web**, vincula tu cuenta escribiendo:\n"
                "`/login tu@correo.com`\n\n"
                "• **Si aún no tienes cuenta**, regístrate gratis en [portaltarotmistico.com](https://www.portaltarotmistico.com) "
                "y vuelve aquí para recibir tus lecturas diarias.",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        return

    # Caso 2: Start normal
    if user:
        user_id, name, email, birth_date, birth_time, birth_city = user
        await update.message.reply_text(
            f"🔮 Bienvenido de vuelta, {name}.\n"
            f"Tu cuenta está vinculada ({email}). Tu carta natal está activa: {birth_date} a las {birth_time}.\n\n"
            "Puedes escribirme cualquier pregunta astrológica o solicitar tu horóscopo diario enviando: /hoy"
        )
    else:
        await update.message.reply_text(
            "🔮 *Bienvenido al Oráculo de Portal Tarot Místico en Telegram.*\n\n"
            "Para conectar con tu destino astral y reconocerte, por favor envíame el comando /login "
            "seguido del correo con el que te registraste en la web:\n\n"
            "`/login tu@correo.com`\n\n"
            "Si aún no estás registrado, ingresa gratis en [portaltarotmistico.com](https://www.portaltarotmistico.com).",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username if update.effective_user else ""
    
    if not context.args:
        await update.message.reply_text("Por favor, incluye tu correo. Ejemplo:\n/login tu@correo.com")
        return
        
    email = context.args[0].lower().strip()
    
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, birth_date, birth_time, birth_city FROM subscribers WHERE lower(email) = lower(?)", (email,))
            user = cursor.fetchone()
            
        if user:
            name, birth_date, birth_time, birth_city = user
            vincular_telegram_id(email, chat_id, username)
            await update.message.reply_text(
                f"✨ ¡Vínculo cósmico establecido, {name}!\n"
                f"Tu Carta Natal ({birth_date} a las {birth_time}) ha quedado vinculada permanentemente a este chat.\n\n"
                "¿Qué deseas consultar hoy con el Oráculo? También puedes pedir tu lectura del día con /hoy."
            )
        else:
            await update.message.reply_text(
                "❌ No encontré ese correo en nuestros registros de la web.\n"
                "Por favor, regístrate primero en https://www.portaltarotmistico.com con tus datos natales e intenta de nuevo."
            )
    except Exception as e:
        await update.message.reply_text("Ocurrió un error cósmico en el sistema. Intenta de nuevo en unos momentos.")
        print(f"Error DB Login: {e}")

async def hoy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando directo /hoy para pedir el horóscopo del día."""
    chat_id = update.effective_chat.id
    user = get_user_by_telegram_id(chat_id)
    
    if not user:
        await update.message.reply_text(
            "Para calcular tu clima astral personalizado, primero vincula tu cuenta con:\n`/login tu@correo.com`",
            parse_mode="Markdown"
        )
        return
        
    user_id, name, email, birth_date, birth_time, birth_city = user
    await update.message.reply_text(f"✨ Calculando el cielo de hoy para {name}...")
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    horoscopo = generar_horoscopo_personalizado_texto(name, birth_date, birth_time, birth_city)
    if horoscopo:
        await update.message.reply_text(horoscopo)
    else:
        registrar_solicitud_pendiente(chat_id, email, request_type="horoscopo_hoy", error_msg="IA indisponible temporalmente")
        await update.message.reply_text(
            "🌌 Tu solicitud ha quedado agendada en el Oráculo.\n"
            "Te enviaremos tu lectura en cuanto los canales astrales se descongestionen."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.channel_post or (update.message and getattr(update.message, 'forward_origin', None)):
        return

    if not update.message or not update.message.text:
        return
    
    if update.message.text.startswith('/'):
        return
        
    user = get_user_by_telegram_id(chat_id)
    if not user:
        await update.message.reply_text(
            "Para que pueda interpretar los astros según tu energía única, primero vincula tu correo registrado:\n`/login tu@correo.com`",
            parse_mode="Markdown"
        )
        return
        
    user_id, name, email, birth_date, birth_time, birth_city = user
    message = update.message.text
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    system_instruction = (
        "Eres la Inteligencia Artificial del Oráculo de 'Portal Tarot Místico'. "
        f"Estás hablando con {name}, nacida/o el {birth_date} a las {birth_time} en {birth_city or 'lugar no especificado'}. "
        "Responde de manera mística, empática y con rigor astrológico, basándote en que conoces su Carta Natal. "
        "Comunícate como un Astrólogo profesional. Sé conciso y amigable para un chat de Telegram."
    )
    
    reply = llamar_ia_con_reintentos(f"Mensaje de {name}: {message}", system_instruction)
    if reply:
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Las estrellas están momentáneamente nubladas. Vuelve a intentarlo en unos instantes.")

def run_bot():
    print(f"[{datetime.now()}] 🤖 Iniciando Telegram Oráculo con Persistencia SQLite y Fallback...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("hoy", hoy_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("📡 Escuchando mensajes...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
