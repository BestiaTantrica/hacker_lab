import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("ai_service")

# Model fallback cascade
GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest"
]

def get_available_keys(settings: Dict[str, Any]) -> List[str]:
    """Collects all configured Gemini keys without duplicates."""
    keys = []
    
    # 1. Primary key from settings or env
    primary = settings.get("gemini_api_key", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    if primary:
        for k in primary.replace("\n", ",").split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
                
    # 2. Backup key
    backup = settings.get("gemini_api_key_backup", "").strip() or os.getenv("GEMINI_API_KEY_BACKUP", "").strip()
    if backup:
        for k in backup.replace("\n", ",").split(","):
            k = k.strip()
            if k and k not in keys:
                keys.append(k)
                
    return keys

def execute_gemini_cascade(prompt: str, settings: Dict[str, Any], is_json: bool = False) -> Tuple[str, str]:
    """
    Executes prompt across available keys and models in cascade order.
    Returns (response_text, model_used).
    """
    keys = get_available_keys(settings)
    if not keys:
        raise Exception("No hay ninguna Gemini API Key configurada. Agrega al menos una en Configuración.")

    errors = []
    
    for key in keys:
        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            try:
                res = requests.post(url, json=payload, timeout=18)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            text = parts[0]["text"].strip()
                            return text, model
                    errors.append(f"Model {model}: respuesta vacía de Google")
                elif res.status_code == 429:
                    # Cuota excedida para esta key, probar con la siguiente key/modelo
                    errors.append(f"Key ...{key[-6:]} / {model}: Cuota excedida (429)")
                    break # Salta a la siguiente clave
                elif res.status_code == 404:
                    # Modelo en desuso o no disponible
                    errors.append(f"Model {model}: 404 No disponible")
                    continue # Prueba siguiente modelo
                else:
                    errors.append(f"Model {model}: HTTP {res.status_code}")
            except Exception as e:
                errors.append(f"Model {model}: error de conexión ({str(e)})")
                
    raise Exception(f"Todas las claves y modelos de IA fallaron. Detalles: {'; '.join(errors[:4])}")

def generate_social_content(product: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    """Generates viral social media pack for a product."""
    store_name = settings.get("store_name", "EcoMarvex")
    prompt = f"""
Eres el director de marketing digital de "{store_name}" (e-commerce argentino en ecomarvex.com).
Tu misión es crear una campaña viral para redes sociales (TikTok, Reels, Instagram) para vender este producto:

- Producto: {product.get('title')}
- Categoría: {product.get('category')}
- Precio de venta al público: ${product.get('sale_price', 0):,.0f} ARS
- Descripción: {product.get('description', '')}

Genera un JSON EXACTO con esta estructura:
{{
  "tiktok_hook": "Frase impactante de 3 segundos para captar la atención en TikTok o Instagram Reel",
  "tiktok_script": "Guión rápido de 30-45 segundos explicando qué mostrar en cámara y qué decir (paso a paso)",
  "instagram_caption": "Texto completo para el post de Instagram con emojis, beneficios del producto y llamada a comprar en ecomarvex.com (con cuotas y envíos a todo el país)",
  "hashtags": "8 a 10 hashtags virales (#EcoMarvex, #DropshippingArgentina, #Ofertas, etc.)",
  "selling_points": ["Beneficio clave 1", "Beneficio clave 2", "Beneficio clave 3"]
}}
Responde ÚNICAMENTE con el objeto JSON puro, sin bloques markdown de código.
"""
    raw_text, model_used = execute_gemini_cascade(prompt, settings, is_json=True)
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("\n", 1)[0]
    result = json.loads(raw_text.strip())
    result["model_used"] = model_used
    return result

def generate_whatsapp_reply(customer_message: str, product_title: Optional[str], settings: Dict[str, Any]) -> Dict[str, Any]:
    """Drafts an Argentine, friendly, and persuasive WhatsApp reply."""
    store_name = settings.get("store_name", "EcoMarvex")
    bank_alias = settings.get("bank_alias", "")
    bank_cbu = settings.get("bank_cbu", "")
    shipping_policy = settings.get("shipping_policy_text", "Envío a convenir / a cargo del comprador por Andreani o Correo Argentino")

    prompt = f"""
Eres el asistente de atención al cliente de la tienda online argentina "{store_name}" (ecomarvex.com).
Un cliente te escribió este mensaje por WhatsApp:
"{customer_message}"

{f'Producto consultado: {product_title}' if product_title else ''}
Datos de la tienda:
- Política de envíos: {shipping_policy}
- Datos bancarios si consulta para pagar por transferencia: Alias: {bank_alias} | CBU: {bank_cbu}
- Web oficial: https://ecomarvex.com

Instrucciones:
1. Responde con tono argentino cordial, cercano, educado y profesional (usa voseo natural: "Hola! Sí, tenemos disponible...", "Te comento...", "Podés comprarlo...").
2. Si pregunta por stock o envíos, aclara que despachamos a todo el país por correo y que el envío se coordina tras la compra.
3. Si pregunta cómo pagar, indícale que puede abonar con Mercado Pago (tarjetas/cuotas) o por Transferencia Bancaria directa con descuento.
4. Mantén la respuesta breve (máximo 3-4 párrafos cortos) con emojis adecuados para WhatsApp.

Devuelve solo el texto del mensaje listo para enviar por WhatsApp.
"""
    reply, model_used = execute_gemini_cascade(prompt, settings, is_json=False)
    return {"reply": reply, "model_used": model_used}

def ask_dropshipping_advisor(question: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Provides expert advice on winning products, Dropsheable suppliers, and pricing."""
    prompt = f"""
Eres un consultor experto en Dropshipping y e-commerce en Argentina, especializado en la plataforma Dropsheable (dropsheable.com.ar).
El dueño de la tienda online EcoMarvex te hace la siguiente consulta:
"{question}"

Pautas:
- Habla en español de Argentina con claridad ejecutiva.
- Considera el mercado argentino: costos de flete (Andreani/Correo Argentino $5.500-$8.500 ARS), comisiones de Mercado Pago (~6%-8%), márgenes de ganancia saludables (>40%-60%).
- Si pregunta por productos ganadores, sugiere nichos con alta rotación y poco volumen/peso (gadgets, belleza, accesorios para autos, hogar práctico).
- Si pregunta por Dropsheable, explícale cómo sincronizar stock, cómo elegir proveedores con buena reputación y cómo evitar quiebres de stock.

Devuelve una respuesta estructurada, fácil de leer, con viñetas y consejos concretos.
"""
    advice, model_used = execute_gemini_cascade(prompt, settings, is_json=False)
    return {"advice": advice, "model_used": model_used}

def analyze_dropsheable_query(mode: str, query: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes products, suppliers, shipping, and margins for Dropsheable Argentina."""
    prompt = f"""
Eres el director de abastecimiento y compras mayoristas para la tienda EcoMarvex (ecomarvex.com), experto absoluto en Dropsheable Argentina (dropsheable.com.ar).

Modo de consulta: {mode} (buscar proveedores para un producto / evaluar proveedor o categoría)
Consulta del usuario: "{query}"

Tu objetivo es darle una respuesta técnica, comercial y operativa precisa para el mercado argentino:
1. **Análisis de Costos y Márgenes:**
   - Precio de costo mayorista típico en Dropsheable vs. precio de reventa competitivo en Argentina (Mercado Libre y tiendas online).
   - Margen bruto y neto recomendado (teniendo en cuenta comisiones de pasarela de pago ~6% y logística).
2. **Impacto de la Logística y Envíos (¡Clave!):**
   - Dónde suelen estar radicados estos proveedores (CABA, GBA, interior).
   - Peso/volumen estimado del paquete y costo aproximado de flete con Andreani / Correo Argentino ($5.500 - $9.000 ARS).
   - Regla de oro: ¿Conviene vender este producto solo o en combo para absorber el flete?
3. **Criterios para elegir al Proveedor en Dropsheable:**
   - ¿Qué mirar en la ficha del proveedor en dropsheable.com.ar? (Stock mínimo recomendado >20 unidades para evitar quiebres, tiempo de despacho <24-48hs, packaging neutro sin marcas ajenas).
4. **Plan de Acción para Cargar en EcoMarvex:**
   - Recomendación de título vendedor, categoría y público objetivo.

Devuelve una respuesta estructurada con títulos claros, viñetas y tono argentino profesional.
"""
    advice, model_used = execute_gemini_cascade(prompt, settings, is_json=False)
    return {"analysis": advice, "model_used": model_used}
