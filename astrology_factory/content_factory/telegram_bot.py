import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ Error: Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCCION_DIR = os.path.join(BASE_DIR, "produccion")
INBOX_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault"
os.makedirs(INBOX_DIR, exist_ok=True)

async def send_assets_to_telegram(evento_name):
    """
    Función para enviar el guion y el audio al celular del usuario.
    Se puede llamar desde tts_local.py
    """
    app = (Application.builder()
               .token(TOKEN)
               .read_timeout(120)
               .write_timeout(120)
               .connect_timeout(30)
               .build())
    
    evento_dir = os.path.join(PRODUCCION_DIR, evento_name)
    guion_path = os.path.join(evento_dir, "guion.txt")
    audio_path = os.path.join(evento_dir, f"{evento_name}.mp3")
    
    try:
        async with app:
            # Enviar Guion
            if os.path.exists(guion_path):
                with open(guion_path, "r", encoding="utf-8") as f:
                    texto = f.read()
                await app.bot.send_message(chat_id=CHAT_ID, text=f"📜 *Guion: {evento_name}*\n\n{texto}", parse_mode='Markdown')
                print("✅ Guion enviado a Telegram.")
            
            # Intentar enviar Video primero, si no, enviar Audio
            video_path = os.path.join(evento_dir, f"{evento_name}.mp4")
            if os.path.exists(video_path):
                with open(video_path, "rb") as f:
                    await app.bot.send_video(chat_id=CHAT_ID, video=f, caption="🎬 Tu video renderizado automáticamente.")
                print("✅ Video MP4 enviado a Telegram.")
            elif os.path.exists(audio_path):
                with open(audio_path, "rb") as f:
                    await app.bot.send_audio(chat_id=CHAT_ID, audio=f, title=evento_name, performer="Astrology Factory")
                print("✅ Audio enviado a Telegram.")
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {e}")

# --- RUTINAS DEL DAEMON BOT (PARA RECIBIR VIDEOS) ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 ¡Hola Arquitecto! Soy tu puente personal con CapCut. Mándame los videos terminados y los guardaré en tu bóveda.")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verificación de seguridad
    if str(update.message.chat_id) != CHAT_ID:
        await update.message.reply_text("❌ No tienes autorización para usar esta bóveda.")
        return
        
    media = update.message.video or update.message.document
    is_photo = False
    if not media and update.message.photo:
        media = update.message.photo[-1]  # La foto de mayor resolución
        is_photo = True
        
    if not media:
        return
        
    file_id = media.file_id
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if is_photo:
        file_name = f"imagen_{timestamp}_{file_id[-4:]}.jpg"
    else:
        orig_name = media.file_name if hasattr(media, 'file_name') and media.file_name else f"video_{file_id[-4:]}.mp4"
        # Insertar timestamp antes de la extensión
        name_part, ext = os.path.splitext(orig_name)
        if not ext:
            ext = ".mp4"
        file_name = f"{name_part}_{timestamp}{ext}"
        
    save_path = os.path.join(INBOX_DIR, file_name)
    
    await update.message.reply_text(f"⏳ Descargando y guardando {file_name} directo en tu Bóveda (Astrology_Vault)...")
    
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(save_path)
    
    await update.message.reply_text(f"✅ ¡Archivo guardado en la Bóveda!\nRuta: Astrology_Vault/{file_name}")
    print(f"📥 Nuevo archivo recibido de Telegram: {save_path}")

def run_daemon():
    """Inicia el bot en modo escucha (para correr de fondo)"""
    print("🤖 Iniciando Puente Telegram (Daemon)...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO | filters.PHOTO | filters.Document.IMAGE, handle_media))
    
    print("📡 Escuchando por nuevos videos desde tu celular...")
    app.run_polling()

if __name__ == "__main__":
    run_daemon()
