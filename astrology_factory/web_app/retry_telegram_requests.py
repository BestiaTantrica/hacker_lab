import os
import sys
import sqlite3
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "users.sqlite")

load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Importar generador con reintentos desde telegram_manager
from telegram_manager import generar_horoscopo_personalizado_texto

async def process_pending_requests():
    print(f"[{datetime.now()}] 🔍 Revisando solicitudes pendientes de Telegram...")
    if not TOKEN:
        print("❌ Falta TELEGRAM_BOT_TOKEN.")
        return

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.chat_id, p.email, s.name, s.birth_date, s.birth_time, s.birth_city
            FROM pending_telegram_requests p
            LEFT JOIN subscribers s ON (p.chat_id = s.telegram_id OR lower(p.email) = lower(s.email))
            WHERE p.status = 'pending'
            LIMIT 10
        ''')
        pendientes = cursor.fetchall()
        
        if not pendientes:
            print("✨ No hay solicitudes de Telegram pendientes.")
            conn.close()
            return

        bot = Bot(token=TOKEN)
        
        for req_id, chat_id, email, name, birth_date, birth_time, birth_city in pendientes:
            print(f"Procesando solicitud pendiente #{req_id} para chat {chat_id} ({name or email})...")
            
            if not name or not birth_date:
                # No hay datos natales suficientes
                cursor.execute("UPDATE pending_telegram_requests SET status = 'failed', error_log = 'Sin datos natales' WHERE id = ?", (req_id,))
                conn.commit()
                continue
                
            horoscopo = generar_horoscopo_personalizado_texto(name, birth_date, birth_time, birth_city)
            if horoscopo:
                try:
                    mensaje = f"✨ *Tu Lectura Astral Personalizada (Agendada)* ✨\n\n{horoscopo}"
                    await bot.send_message(chat_id=chat_id, text=mensaje, parse_mode="Markdown")
                except Exception:
                    # Enviar sin parse_mode si falla por markdown
                    await bot.send_message(chat_id=chat_id, text=f"✨ Tu Lectura Astral Personalizada (Agendada) ✨\n\n{horoscopo}")
                    
                cursor.execute("UPDATE pending_telegram_requests SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (req_id,))
                conn.commit()
                print(f"✅ Solicitud #{req_id} entregada con éxito a {chat_id}.")
            else:
                print(f"⚠️ La IA sigue ocupada para solicitud #{req_id}. Se reintentará en el próximo ciclo.")
                
        conn.close()
    except Exception as e:
        print(f"❌ Error en process_pending_requests: {e}")

if __name__ == "__main__":
    asyncio.run(process_pending_requests())
