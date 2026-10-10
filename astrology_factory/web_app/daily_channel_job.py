import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
from google import genai
from google.genai import types

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "-1003701234540"  # Portal Tarot Místico
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def send_daily_forecast():
    print(f"[{datetime.now()}] Iniciando generación del reporte astral diario para el canal...")
    
    # 1. Generar contenido con la IA
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        system_instruction = (
            "Eres un Astrólogo profesional y místico. Tu tarea es escribir un "
            "breve reporte del 'Clima Astral Diario' para un canal de Telegram de Tarot y Astrología. "
            "El mensaje debe ser para el colectivo (en plural o general). "
            "Debe incluir una introducción mística, los tránsitos más relevantes del día, y un consejo final. "
            "Usa emojis apropiados y mantén una longitud ideal para un mensaje de Telegram (no demasiado largo). "
            "Nunca uses saludos personalizados, ya que es para un canal público."
        )
        
        prompt = f"Por favor, redacta el clima astral general para hoy {datetime.now().strftime('%Y-%m-%d')}."
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
        )
        forecast_text = response.text
        
    except Exception as e:
        print(f"Error generando el contenido de IA: {e}")
        return

    # 2. Enviar a Telegram
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=CHANNEL_ID, text=forecast_text)
        print(f"[{datetime.now()}] ✅ Reporte astral diario enviado exitosamente al canal.")
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(send_daily_forecast())
