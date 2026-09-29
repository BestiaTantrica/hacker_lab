import os
import sqlite3
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sys

# Agregar el directorio al path para poder importar InteractivePersonaEngine
sys.path.append(os.path.join(os.path.dirname(__file__), 'content_factory'))
from interactive_persona import InteractivePersonaEngine

# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DB_PATH = os.path.join(os.path.dirname(__file__), "web_app", "database", "users.sqlite")

# Inicializar Motor de IA
engine = InteractivePersonaEngine()

# Diccionario en memoria para el historial de chat (ID -> list)
# En un entorno real se guardaría en BD o Redis.
chat_histories = {}
MAX_HISTORY = 5

def setup_database():
    """Asegura que la tabla subscribers tenga la columna telegram_id"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Intentar añadir la columna (fallará silenciosamente si ya existe)
        try:
            cursor.execute("ALTER TABLE subscribers ADD COLUMN telegram_id TEXT")
            conn.commit()
            print("Columna telegram_id añadida a la base de datos.")
        except sqlite3.OperationalError:
            pass # La columna ya existe
        conn.close()
    except Exception as e:
        print(f"Error configurando DB: {e}")

def get_user_data(telegram_id):
    """Busca al usuario en la BD por su telegram_id"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscribers WHERE telegram_id = ?", (str(telegram_id),))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Para el prompt, armamos un diccionario con sus datos
            return {
                "nombre": user["name"],
                "fecha_nacimiento": user["birth_date"],
                "hora_nacimiento": user["birth_time"],
                "ciudad_nacimiento": user["birth_city"]
            }
    except Exception as e:
        print(f"Error leyendo DB: {e}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data = get_user_data(chat_id)
    
    if user_data:
        msg = f"¡Qué haces {user_data['nombre']}! Ya te tengo en el radar de Nodriza. Preguntame lo que quieras sobre tus tránsitos o energías."
    else:
        msg = "Bienvenido a Nodriza. Soy Hermes, tu puente a la matriz astrológica. Si ya te registraste en nuestra web, mandame `/email tu@correo.com` para sincronizar tu carta astral conmigo. Si sos nuevo, dispará tu duda."
    
    await update.message.reply_text(msg)

async def link_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Uso: /email tu@correo.com")
        return
        
    email = context.args[0].strip()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM subscribers WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("UPDATE subscribers SET telegram_id = ? WHERE email = ?", (str(chat_id), email))
            conn.commit()
            await update.message.reply_text(f"Sincronización completa. Hola {row[0]}. Ahora tu carta natal está cargada en mi sistema.")
        else:
            await update.message.reply_text("No encontré ese correo en la base de datos de Nodriza. Asegurate de haberte registrado en nuestra web primero.")
        conn.close()
    except Exception as e:
        await update.message.reply_text(f"Error de sistema: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    # 1. Obtener historial
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    history = chat_histories[chat_id]
    
    # 2. Verificar estado del usuario
    user_data = get_user_data(chat_id)
    is_registered = bool(user_data)
    
    # Notificar que está "escribiendo"
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    # 3. Generar respuesta con la IA
    response_text = engine.generate_chat_response(
        user_message=user_text,
        chat_history=history,
        is_registered=is_registered,
        user_chart_data=user_data
    )
    
    # 4. Actualizar historial
    history.append({"role": "user", "content": user_text})
    history.append({"role": "model", "content": response_text})
    if len(history) > MAX_HISTORY * 2:
        history = history[-MAX_HISTORY*2:]
    chat_histories[chat_id] = history
    
    # 5. Enviar respuesta
    await update.message.reply_text(response_text)

def main():
    if not TELEGRAM_TOKEN:
        print("ERROR: Falta TELEGRAM_BOT_TOKEN en .env")
        return
        
    setup_database()
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("email", link_email))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Hermes (Agente de Telegram) iniciando en modo Polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
