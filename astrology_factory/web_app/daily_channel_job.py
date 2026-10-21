import os
import asyncio
import time
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, ".env")):
    load_dotenv(os.path.join(BASE_DIR, ".env"))
elif os.path.exists(os.path.join(os.path.dirname(BASE_DIR), ".env")):
    load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))
else:
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "-1003701234540"  # Portal Tarot Místico

# Modelos en orden de preferencia y estabilidad
MODEL_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.6-flash"
]

def obtener_api_keys():
    """Recolecta todas las API keys disponibles para rotar si hay 429 o 503."""
    keys = []
    for var_name in [
        "GEMINI_API_KEY", "GEMINI_API_KEY_TEXT", "GEMINI_API_KEY_WEB",
        "GEMINI_API_KEY_5", "GEMINI_API_KEY_6", "GEMINI_API_KEY_7",
        "GEMINI_API_KEY_8", "GEMINI_API_KEY_9", "GEMINI_API_KEY_10"
    ]:
        val = os.getenv(var_name)
        if val and val not in keys:
            keys.append(val)
    for k, v in os.environ.items():
        if k.startswith("GEMINI_API_KEY") and v and v not in keys:
            keys.append(v)
    return keys

def generar_reporte_con_reintentos():
    try:
        from astrology_factory.astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
    except ImportError:
        try:
            from astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
        except ImportError:
            from clima_astral_engine import obtener_resumen_cielo_hoy

    cielo_datos = obtener_resumen_cielo_hoy()

    system_instruction = (
        "Eres Tomás, astrólogo titular y creador de 'Portal Tarot Místico' (Sol y Mercurio en conjunción en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10).\n"
        "Tu tarea es redactar el reporte del 'Clima Astral Diario' para el canal de Telegram, fundamentado estrictamente en los cálculos astronómicos reales de Swiss Ephemeris que recibes en el mensaje.\n\n"
        "DIRECTIVAS DE TU PERSONALIDAD Y ENFOQUE:\n"
        "1. Lente Cognitiva (Ascendente Acuario 22°): Tratas a la comunidad como adultos inteligentes y lúcidos. La astrología no es magia supersticiosa, fatalismo ni adivinación barata: es cartografía simbólica y psicológica. No buscas adeptos ni fieles dependientes; buscas poner luz, enseñar y traducir la complejidad celeste a un entendimiento claro y liberador.\n"
        "2. Ritmo y Voz (Sol y Mercurio en Aries 22°): Directo al punto. Cero rodeos, cero humo New Age ('el universo te abraza', 'energías mágicas', 'vibraciones'). Lenguaje despierto, asertivo, transparente y con filo.\n"
        "3. Filosofía y Tono (Luna en Sagitario 5° / Rioplatense sobrio): Mirada panorámica ('The Big Picture'). Voseo rioplatense natural, sobrio y respetuoso ('mirá', 'fijate', 'encontrás').\n\n"
        "PROHIBICIONES ESTRICTAS:\n"
        "- PROHIBIDO EL COACHING DE PELUQUERÍA / AUTOAYUDA IMPERATIVA: Queda terminantemente vetado dar órdenes o recetas imperativas sobre la vida privada de la gente ('Auditá tus acuerdos', 'Hacé esto', 'No seas cobarde', 'Cortá con esa relación', 'Poné límites ya'). No eres un sargento ni un gurú de autoayuda; el lector es un adulto libre y para su mapa personal está el botón de horóscopo personalizado.\n"
        "- PROHIBIDO EL REBUSCAMIENTO PSEUDOINTELECTUAL: Nada de palabrerío inflado o confuso ('vector psicológico tajante', 'micromanagement emocional', 'armonía de utilería'). La profundidad real se explica con sencillez y precisión técnica.\n"
        "- PROHIBIDO OLVIDAR LOS ASTROS: El informe debe fundarse en los datos astronómicos reales provistos (la Luna, su signo y fase actual, y los aspectos dominantes con sus planetas).\n\n"
        "ESTRUCTURA DEL REPORTE (formato ágil y limpio para Telegram):\n"
        "1. Título: CLIMA ASTRAL | [Día de la semana y fecha en español]\n"
        "2. El Mapa Celeste de Hoy: Menciona la Luna (signo y fase lunar actual) y los aspectos protagonistas calculados para hoy.\n"
        "3. La Mecánica y Enseñanza: Explica qué principios arquetípicos entran en juego y cómo opera esa interacción cósmica (educa al lector: explica qué significa la tensión o fluidez entre esos planetas específicos).\n"
        "4. El Clima Colectivo: Describe cómo se siente esa atmósfera en el ambiente general (conversaciones, ritmo mental, sensaciones compartidas en lo social).\n"
        "5. La Brújula del Día: Una síntesis sobria y reflexiva para observar la jornada con lucidez (sin imperativos de autoayuda).\n"
        "6. Cierre de autor:\n"
        "— Tomás · portaltarotmistico.com\n\n"
        "Longitud: Conciso, ágil, 4 o 5 párrafos cortos con subtítulos o viñetas limpias si corresponde."
    )
    prompt = f"Tomás, acá tenés los datos astronómicos calculados con Swiss Ephemeris para hoy:\n\n{cielo_datos}\n\nRedactá el Clima Astral de hoy para el canal."

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
                            temperature=0.6,
                        )
                    )
                    if response and response.text:
                        print(f"[{datetime.now()}] ✅ Contenido generado con éxito usando {model_name}.")
                        return response.text.strip()
                except Exception as e:
                    err_str = str(e)
                    print(f"⚠️ Error con {model_name} / key: {err_str[:120]}... Intentando alternativa...")
                    time.sleep(1)
        print(f"[{datetime.now()}] Pausa de 5s antes del siguiente ciclo de reintento...")
        time.sleep(5)

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
