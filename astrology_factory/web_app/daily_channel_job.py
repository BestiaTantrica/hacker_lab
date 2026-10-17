import os
import asyncio
import time
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from google import genai
from google.genai import types

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "-1003701234540"  # Portal Tarot Místico

# Modelos en orden de preferencia y estabilidad
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-3.6-flash"
]

def obtener_api_keys():
    """Recolecta todas las API keys disponibles para rotar si hay 429 o 503."""
    keys = []
    for var_name in ["GEMINI_API_KEY", "GEMINI_API_KEY_5", "GEMINI_API_KEY_6", "GEMINI_API_KEY_7", "GEMINI_API_KEY_TEXT", "GEMINI_API_KEY_WEB"]:
        val = os.getenv(var_name)
        if val and val not in keys:
            keys.append(val)
    return keys

def generar_reporte_con_reintentos():
    system_instruction = (
        "Eres un Astrólogo profesional y místico. Tu tarea es escribir un "
        "breve reporte del 'Clima Astral Diario' para un canal de Telegram de Tarot y Astrología. "
        "El mensaje debe ser para el colectivo (en plural o general). "
        "Debe incluir una introducción mística, los tránsitos astrológicos más relevantes del día, y un consejo final. "
        "Usa emojis apropiados y mantén una longitud ideal para un mensaje de Telegram (conciso, legible, inspirador). "
        "Nunca uses saludos personalizados, ya que es para un canal público."
    )
    prompt = f"Por favor, redacta el clima astral general para hoy {datetime.now().strftime('%Y-%m-%d')}."

    keys = obtener_api_keys()
    if not keys:
        print("❌ Error: No se encontraron GEMINI_API_KEY en las variables de entorno.")
        return None

    # Intentar con rotación de keys y modelos
    for intento in range(1, 4):
        for api_key in keys:
            for model_name in MODEL_CANDIDATES:
                try:
                    print(f"[{datetime.now()}] Generando reporte con modelo {model_name} (Intento {intento})...")
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7,
                        )
                    )
                    if response and response.text:
                        print(f"[{datetime.now()}] ✅ Contenido generado con éxito usando {model_name}.")
                        return response.text.strip()
                except Exception as e:
                    err_str = str(e)
                    print(f"⚠️ Error con {model_name} / key: {err_str[:120]}... Intentando alternativa...")
                    time.sleep(2)
        print(f"[{datetime.now()}] Pausa de 10s antes del siguiente ciclo de reintento...")
        time.sleep(10)

    print("❌ Todos los reintentos de IA fallaron.")
    return None

async def send_daily_forecast():
    print(f"[{datetime.now()}] Iniciando job de reporte astral diario para el canal...")
    
    forecast_text = generar_reporte_con_reintentos()
    if not forecast_text:
        print("❌ No se pudo generar el reporte. Cancelando envío.")
        return

    # 2. Configurar botón de personalización
    # Abre chat privado con el bot con el parámetro deep-link 'horoscopo_hoy'
    keyboard = [
        [InlineKeyboardButton("🔮 Solicitar mi Horóscopo Personalizado", url="https://t.me/PortalTarotBot?start=horoscopo_hoy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 3. Enviar a Telegram con tolerancia a formato
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        try:
            # Primero intentamos con Markdown
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=forecast_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as parse_err:
            print(f"Aviso: Falló Markdown ({parse_err}). Enviando en texto plano...")
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=forecast_text,
                reply_markup=reply_markup
            )
        print(f"[{datetime.now()}] ✅ Reporte astral diario enviado exitosamente al canal con botón de personalización.")
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(send_daily_forecast())
