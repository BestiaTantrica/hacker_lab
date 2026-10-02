import google.genai as genai
import json
import time

def elegir_mejor_asset_con_gemini(client, toma_texto, rol, cat, ultimos_usados, emocion_dominante, elemento_astro):
    prompt = f"""
Eres el Director de Arte de un video astrológico profundo y poético.
Tu tarea es elegir el MEJOR asset visual de nuestra bóveda para acompañar el siguiente texto (Toma: {rol}):
TEXTO: "{toma_texto}"

Emoción dominante del evento: {emocion_dominante}
Elemento astrológico: {elemento_astro}

CATÁLOGO DE ASSETS DISPONIBLES:
"""
    for key, meta in cat.items():
        if not meta.get("path_video_final"): continue
        tags = ", ".join(meta.get("tags", []))
        elemento = meta.get("elemento_visual", "Abstracto")
        prompt += f"- ID: {key} | Elemento: {elemento} | Tags: {tags}\n"

    prompt += f"""
Assets usados recientemente (EVITAR REPETIR SI ES POSIBLE): {", ".join(ultimos_usados)}

Reglas:
1. Elige el asset cuyo "Elemento" o "Tags" mejor resuenen de forma SUGERENTE y SUTIL con el texto.
2. Si el texto habla de fuego o urgencia, busca algo ígneo o intenso. Si habla de emociones profundas, agua.
3. Responde ÚNICAMENTE con el ID del asset elegido. Nada más.
"""
    
    for i in range(3):
        try:
            res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            key = res.text.strip()
            if key in cat: return key
            # Si responde con comillas o similar
            key_clean = key.replace('"', '').replace("'", "")
            if key_clean in cat: return key_clean
            
            # Fallback iterativo
            for k in cat.keys():
                if k in key: return k
                
        except Exception as e:
            time.sleep(2)
            
    return None
