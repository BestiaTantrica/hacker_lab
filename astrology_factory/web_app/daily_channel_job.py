import os
import sys
import asyncio
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Asegurar rutas absolutas para importar astrology_engine tanto local como en OCI
for p in [str(PROJECT_ROOT), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

if (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
elif (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
else:
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1003701234540")  # Canal Portal Tarot Místico

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

def obtener_contexto_produccion():
    """Lee el contexto astrológico y la metadata del video diario si existe."""
    adn_path = PROJECT_ROOT / "contexto_astrologico.json"
    if not adn_path.exists():
        return None
    try:
        with open(adn_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Aviso leyendo contexto: {e}")
        return None

def obtener_enlaces_video_hoy():
    """
    Lee produccion/registro_publicaciones.json para obtener los enlaces exactos
    del video del día en YouTube y TikTok. Si no hay link específico para hoy,
    usa el último publicado o el canal oficial para que nunca haya un enlace roto.
    """
    reg_path = PROJECT_ROOT / "produccion" / "registro_publicaciones.json"
    hoy_str = datetime.now().strftime("%Y-%m-%d")
    
    yt_fallback = "https://www.youtube.com/@PortalTarotMistico"
    tt_fallback = "https://www.tiktok.com/@portaltarotmistico"
    
    if not reg_path.exists():
        return yt_fallback, tt_fallback
        
    try:
        with open(reg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            pubs = data.get("publicaciones", {})
            if hoy_str in pubs:
                entry = pubs[hoy_str]
                yt = entry.get("youtube_url") or yt_fallback
                tt = entry.get("tiktok_url") or tt_fallback
                return yt, tt
            # Si no está hoy, tomar la más reciente con video disponible
            for f_key in sorted(pubs.keys(), reverse=True):
                if pubs[f_key].get("youtube_url"):
                    return pubs[f_key]["youtube_url"], pubs[f_key].get("tiktok_url") or tt_fallback
    except Exception as e:
        print(f"Aviso leyendo registro_publicaciones: {e}")
        
    return yt_fallback, tt_fallback

def generar_reporte_con_reintentos(adn_context=None):
    try:
        from astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
    except ImportError:
        try:
            from astrology_factory.astrology_engine.clima_astral_engine import obtener_resumen_cielo_hoy
        except ImportError:
            from clima_astral_engine import obtener_resumen_cielo_hoy

    cielo_datos = obtener_resumen_cielo_hoy()

    # Contexto del video diario
    info_video = ""
    if adn_context and "produccion" in adn_context:
        titulo_ev = adn_context["produccion"].get("evento_titulo", "")
        desc_tr = adn_context.get("transito", {}).get("descripcion_breve", "")
        info_video = f"\nTRANSITO PROTAGONISTA DEL VIDEO DE HOY: {titulo_ev}\nSINOPSIS: {desc_tr}\n"

    system_instruction = (
        "Eres Tomás, creador de 'Portal Tarot Místico' (Sol y Mercurio en conjunción en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10).\n"
        "Tu tarea es redactar el reporte del 'Clima Astral Diario' para el canal de Telegram, fundamentado estrictamente en los cálculos astronómicos reales de Swiss Ephemeris.\n\n"
        "MOLDE DE ORO CANÓNICO (Estilo de Tomás):\n"
        "- Lente Cognitiva (Acuario 22°): Tratas a la comunidad como adultos lúcidos. La astrología es cartografía psicológica, no superstición barata ni fatalismo.\n"
        "- Ritmo y Filo (Aries 22°): Directo al hueso. Cero rodeos, cero humo New Age ('el universo te abraza', 'vibraciones'). Lenguaje asertivo y claro.\n"
        "- Filosofía (Sagitario 5° / Rioplatense sobrio): Mirada panorámica, voseo rioplatense natural y respetuoso ('mirá', 'fijate', 'encontrás').\n\n"
        "PROHIBICIONES ESTRICTAS:\n"
        "- PROHIBIDO EL COACHING DE AUTOAYUDA O IMPERATIVOS: No des órdenes sobre la vida privada ('Auditá tus acuerdos', 'Cortá con esa relación', 'Poné límites ya'). El lector es un adulto libre.\n"
        "- PROHIBIDO EL REBUSCAMIENTO INFLADO: Nada de tecnicismos vacíos ('micromanagement emocional', 'vector tajante'). La profundidad real se explica con sencillez.\n\n"
        "ESTRUCTURA EXACTA DEL REPORTE:\n"
        "1. Título: ⚡ CLIMA ASTRAL | [Día de la semana y fecha en español]\n"
        "2. El Tránsito Protagonista: Menciona la colisión o aspecto principal activo (por ejemplo Mercurio en Escorpio vs Marte en Leo) y el signo/fase de la Luna.\n"
        "3. La Mecánica Psicológica (Extensión del video): Explica qué pasa en la mente y el comportamiento con este aspecto (por qué surge la necesidad de tener razón, la reactividad o la desconfianza oculta).\n"
        "4. La Brújula Lúcida: Una reflexión pragmática para no morder el anzuelo de la tensión hoy.\n"
        "5. Síntesis Visual (TikTok & Shorts): Invitá con naturalidad y sobriedad a ver el desglose dinámico en video de 60 segundos en TikTok y YouTube Shorts mediante los botones interactivos de acá abajo.\n"
        "6. Cierre:\n"
        "— Tomás · portaltarotmistico.com\n\n"
        "Longitud: Ágil, 4 o 5 párrafos concisos, con viñetas limpias si corresponde. Formato Markdown compatible con Telegram (usa *negritas* y _cursivas_ con cuidado)."
    )

    prompt = (
        f"Tomás, acá tenés los datos astronómicos calculados con Swiss Ephemeris para hoy:\n\n"
        f"{cielo_datos}\n"
        f"{info_video}\n"
        f"Redactá el reporte del Clima Astral para el canal, profundizando en el tránsito del video de hoy."
    )

    keys = obtener_api_keys()
    if not keys:
        print("❌ Error: No se encontraron GEMINI_API_KEY en las variables de entorno.")
        return None

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
                    print(f"⚠️ Error con {model_name}: {err_str[:120]}... Intentando alternativa...")
                    time.sleep(1)
        time.sleep(3)

    print("❌ Todos los reintentos de IA fallaron.")
    return None

async def send_daily_forecast():
    print(f"[{datetime.now()}] Iniciando despacho de Clima Astral Diario al canal de Telegram...")

    if not TELEGRAM_TOKEN:
        print("❌ Falta TELEGRAM_BOT_TOKEN en variables de entorno.")
        return

    adn = obtener_contexto_produccion()
    forecast_text = generar_reporte_con_reintentos(adn)
    if not forecast_text:
        print("❌ No se pudo generar el texto del reporte. Cancelando.")
        return

    # Enlaces dinámicos de retroalimentación multimedia del día
    youtube_url, tiktok_url = obtener_enlaces_video_hoy()
    print(f"🔗 Enlaces del video para hoy: YouTube: {youtube_url} | TikTok: {tiktok_url}")

    # Botones Interactivos Multicanal
    keyboard = [
        [
            InlineKeyboardButton("🎬 Ver en YouTube Shorts", url=youtube_url),
            InlineKeyboardButton("⚫ Ver en TikTok", url=tiktok_url)
        ],
        [
            InlineKeyboardButton("🔮 Solicitar mi Horóscopo Personalizado", url="https://t.me/PortalTarotBot?start=horoscopo_hoy")
        ],
        [
            InlineKeyboardButton("🌐 Mi Carta Natal en la Web", url="https://portaltarotmistico.com")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=forecast_text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        except Exception as parse_err:
            print(f"Aviso Markdown ({parse_err}). Reenviando en texto plano...")
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=forecast_text,
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
        print(f"[{datetime.now()}] ✅ Reporte astral diario y enlaces multimedia despachados exitosamente al canal.")
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(send_daily_forecast())
