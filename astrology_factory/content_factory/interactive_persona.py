import os
import json
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

class InteractivePersonaEngine:
    def __init__(self):
        # Cargar variables de entorno desde el .env del proyecto
        load_dotenv("/home/LAB/astrology_factory/.env")
        
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
        else:
            self.gemini_client = None
            
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None
            
        self._load_base_personality()

    def _load_base_personality(self):
        # Leer el MASTER_PROMPT.md para inyectar la carta completa del creador
        master_prompt_path = "/home/LAB/.agents/MASTER_PROMPT.md"
        master_data = ""
        if os.path.exists(master_prompt_path):
            with open(master_prompt_path, "r", encoding="utf-8") as f:
                master_data = f.read()

        self.system_prompt = f"""
        ERES HERMES (El Agente Astrológico y Social Media Manager de Nodriza).
        Tu personalidad es EXACTAMENTE la misma que la de tu creador, descrita a continuación:
        
        {master_data}
        
        ===== REGLAS DE OPERACIÓN COMO AGENTE SOCIAL =====
        1. Tu tono es veloz (Aries), profundo (Sagitario) y disruptivo/tecnológico (Acuario).
        2. Eres directo al hueso. Cero complacencia "New Age" barata. Hablas de energías estadísticas, conjunciones y verdades duras.
        3. Cuando el usuario te hace una pregunta general de astrología o sobre cómo están los planetas hoy, responde brillantemente.
        4. OBLIGATORIO: Siempre, al final de tu respuesta, debes incluir un Call-to-Action seductor para que el usuario vaya a la Web a sacar su carta astral o ver su pronóstico exacto.
           Ejemplo: "Si querés ver cómo te pega esta tensión de Marte en tu vida real, andá a [NUESTRA WEB] y cargá tu fecha de nacimiento exacta."
        5. Respuestas cortas, pensadas para chat de Telegram o mensajes web rápidos (max 3-4 párrafos cortos).
        """

    def generate_chat_response(self, user_message, chat_history=None, is_registered=False, user_chart_data=None):
        if chat_history is None:
            chat_history = []
            
        # Ajustar el prompt dinámicamente si el usuario está registrado en la base de datos
        dynamic_prompt = self.system_prompt
        if is_registered and user_chart_data:
            dynamic_prompt += f"\n\n===== CONTEXTO DEL USUARIO ACTUAL =====\nEl usuario que te habla ESTÁ SUSCRITO. Sus datos astrológicos base son: {json.dumps(user_chart_data)}. Usa esta información sutilmente para darle una respuesta hiper-personalizada. NO le pidas que vaya a la web a cargar sus datos porque ya lo hizo. En su lugar, recuérdale que puede pedir su Revolución Solar o su Video Natal premium en la plataforma."
        elif not is_registered:
            dynamic_prompt += "\n\n===== CONTEXTO DEL USUARIO ACTUAL =====\nEste usuario es TRÁFICO FRÍO. No tenemos su carta astral. Tira una píldora de conocimiento y DERÍVALO A LA WEB para que se suscriba."

        if self.gemini_client:
            return self._call_gemini(user_message, dynamic_prompt, chat_history)
        elif self.groq_client:
            return self._call_groq(user_message, dynamic_prompt, chat_history)
        else:
            return "Error: No API keys configured."

    def _call_gemini(self, user_message, system_instruction, chat_history):
        try:
            # Simplificación para el chat: pasamos historial y el mensaje nuevo
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            full_prompt = f"Historial:\n{history_text}\n\nUsuario: {user_message}\n\nTu respuesta:"
            
            response = self.gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.85
                ),
            )
            return response.text
        except Exception as e:
            print(f"Error Gemini Chat: {e}")
            return "Mi enlace con la matriz cuántica (Gemini) está fluctuando. Intenta de nuevo."

    def _call_groq(self, user_message, system_instruction, chat_history):
        try:
            messages = [{"role": "system", "content": system_instruction}]
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})
            
            response = self.groq_client.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",
                temperature=0.85
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error Groq Chat: {e}")
            return "Mi enlace neuronal secundario (Groq) falló. Dame un respiro."

if __name__ == "__main__":
    engine = InteractivePersonaEngine()
    print(engine.generate_chat_response("Tengo a Plutón en casa 1, ¿es grave?"))
