import os
import sys
import sqlite3
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Cargar configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "users.sqlite")

load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Gemini usa GEMINI_API_KEY_WEB o GEMINI_API_KEY
api_key = os.getenv("GEMINI_API_KEY_WEB", os.getenv("GEMINI_API_KEY"))
if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    gemini_client = None

if not TOKEN:
    print("❌ Error: Falta TELEGRAM_BOT_TOKEN en .env")
    sys.exit(1)

# Diccionario temporal en memoria para rastrear el estado del chat
user_sessions = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        "🔮 Bienvenido al Oráculo de Portal Tarot Místico en Telegram.\n\n"
        "Para conectar con tu destino astral y reconocerte, por favor envíame el comando /login seguido de tu correo electrónico con el que te registraste en la web.\n\n"
        "Ejemplo:\n/login tu@correo.com"
    )

async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("Por favor, incluye tu correo. Ejemplo:\n/login tu@correo.com")
        return
        
    email = context.args[0].lower().strip()
    
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, birth_date, birth_time FROM subscribers WHERE email = ?", (email,))
            user = cursor.fetchone()
            
        if user:
            name, birth_date, birth_time = user
            user_sessions[chat_id] = {
                "email": email,
                "name": name,
                "birth_date": birth_date,
                "birth_time": birth_time
            }
            await update.message.reply_text(f"✨ Vínculo establecido, {name}. Conozco tu carta astral ({birth_date} a las {birth_time}).\n¿Qué le quieres preguntar al universo hoy?")
        else:
            await update.message.reply_text("❌ No encontré ese correo en nuestros registros de la web. Por favor, regístrate primero en portaltarotmistico.com.")
    except Exception as e:
        await update.message.reply_text("Ocurrió un error cósmico. Intenta de nuevo más tarde.")
        print(f"Error DB: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if update.channel_post:
        print(f"📡 Post detectado en el canal: {update.channel_post.chat.title} (ID: {chat_id})")
        return
        
    if update.message and getattr(update.message, 'forward_origin', None):
        print(f"📡 Mensaje reenviado desde: {update.message.forward_origin}")
        return

    if not update.message or not update.message.text:
        return
    
    # Ignorar comandos si entran acá
    if update.message.text.startswith('/'):
        return
        
    if chat_id not in user_sessions:
        await update.message.reply_text("Para que pueda leer los astros por ti, primero ingresa tu correo con el comando:\n/login tu@correo.com")
        return
        
    user = user_sessions[chat_id]
    message = update.message.text
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    prompt = f"""Eres la Inteligencia Artificial del Oráculo de 'Portal Tarot Místico'. 
Estás hablando con {user['name']}, cuya fecha de nacimiento natal es {user['birth_date']} a las {user['birth_time']}.
Responde a su siguiente mensaje de manera mística, empática y astrológica, basándote en que conoces sus datos natales. 
Comunícate como un Astrólogo profesional. Si el usuario utiliza frases coloquiales o modismos para indicar que hubo un problema o error, compréndelos metafóricamente y no te lo tomes literal.
No seas excesivamente largo, responde de forma concisa y amigable como si estuvieran chateando por Telegram.

Mensaje de {user['name']}: {message}
"""
    
    try:
        if gemini_client:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("La IA no está configurada correctamente.")
    except Exception as e:
        await update.message.reply_text("Las estrellas están nubladas en este momento. Vuelve a intentarlo en un instante.")
        print(f"Error Gemini: {e}")

def run_bot():
    print("🤖 Iniciando Telegram Oráculo...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("📡 Escuchando mensajes...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
