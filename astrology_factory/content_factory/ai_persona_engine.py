import os
import json
from google import genai
from google.genai import types
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Custom Exception
class GeminiAPIError(Exception): pass

class AIPersonaEngine:
    def __init__(self):
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
            
        self.system_prompt = """
        Eres un astrólogo experto, académico y sutil. Tu tono es HISTÓRICO y TEÓRICO, respaldado por la Astrología Mundana y el comportamiento estadístico de los planetas a través de los años.
        
        REGLA DE REDACCIÓN ASTRAL (OBLIGATORIA):
        NUNCA le digas al usuario "te vas a sentir así" o "hoy te pasa esto". Un tránsito masivo no afecta a todos igual.
        En lugar de eso, haz un buen ANÁLISIS CENTRAL DEL TRÁNSITO. Explica la teoría: qué pasa cuando este planeta toca a este otro, cómo se ha visto en el pasado, abriendo un abanico de posibilidades reales. Pon las cosas en su lugar con amabilidad y sutileza intelectual.
        
        REGLA VISUAL (OBLIGATORIA):
        Para los `prompts_visuales`, puedes pedir representaciones de energías y arquetipos, pero SIEMPRE de forma artística, metafórica o cinemática. 
        PROHIBIDO usar descripciones de videos de stock literales o mundanos. Usa `[illustration]` para arte o `[video]` para elementos cinemáticos/abstractos. Corta visualmente cada 4 segundos.
        
        REGLA DE CTA (OBLIGATORIA):
        El último párrafo del guion DEBE ser SIEMPRE un llamado a la acción para ir a la web. Como no personalizamos el video, aquí radica el valor:
        "Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto. Tu donación nos ayuda a seguir expandiendo esta biblioteca."
        El último prompt visual debe reflejar este cierre (ej. "[illustration] cosmic stars glowing portal cta link donation").
        
        Formato de Salida Obligatorio (JSON estricto):
        {
            "guion_audio": "El texto completo...",
            "prompts_visuales": [
                "[video] cosmic energy explosion red fire",
                "[illustration] warrior spirit bold aura"
            ]
        }
        """
        
        # Cargar contexto actualizado de producción
        context_path = os.path.join(os.path.dirname(__file__), "vademecum_contexto.md")
        if os.path.exists(context_path):
            with open(context_path, "r", encoding="utf-8") as f:
                vademecum = f.read()
            self.system_prompt += f"\n\nCONTEXTO DE PRODUCCIÓN ACTUAL:\n{vademecum}"
            
        # Cargar contexto desde vademecum.json (nuevo formato para API)
        json_path = os.path.join(os.path.dirname(__file__), "vademecum.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Tomar los últimos 10 eventos para no saturar el prompt
                recent_data = data[-10:] if len(data) > 10 else data
                json_context = "\n\n".join([f"[{item.get('timestamp', '')}] Evento: {item.get('event_name', '')}\nGuion: {item.get('guion', '')}" for item in recent_data])
                self.system_prompt += f"\n\nHISTORIAL EN VADEMECUM JSON (Últimos 10 videos):\n{json_context}"
            except Exception as e:
                print(f"Error reading vademecum.json: {e}")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(3), retry=retry_if_exception_type(GeminiAPIError))
    def _call_gemini(self, prompt):
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    response_mime_type="application/json",
                    temperature=0.8
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            # Re-raise para que Tenacity lo atrape y reintente
            print(f"[Gemini] Error 503 o de red, reintentando... ({e})")
            raise GeminiAPIError(e)

    def _call_groq(self, prompt):
        print("[Groq] Iniciando Fallback con Groq...")
        # Groq no soporta system_instruction en la config igual que gemini, lo pasamos en el array de mensajes
        messages = [
            {"role": "system", "content": self.system_prompt + "\nRESPONDE ÚNICAMENTE CON UN JSON VÁLIDO. NO ESCRIBAS TEXTO FUERA DEL JSON."},
            {"role": "user", "content": prompt}
        ]
        response = self.groq_client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def generate_content(self, astronomical_data, time_frame="Diario"):
        if not self.gemini_api_key and not self.groq_api_key:
            return None
            
        prompt = f"Aquí tienes el reporte astronómico ({time_frame}):\n{json.dumps(astronomical_data, indent=2)}\n\nRedacta el guion y los prompts en formato JSON."
        
        # 1. Intentar con Gemini (con reintentos)
        if self.gemini_client:
            try:
                return self._call_gemini(prompt)
            except Exception as e:
                print(f"Gemini falló definitivamente tras reintentos: {e}")
        
        # 2. Fallback a Groq
        if self.groq_client:
            try:
                return self._call_groq(prompt)
            except Exception as e:
                print(f"Groq también falló: {e}")
        
        # 3. Alerta de Emergencia si ambos fallan
        self._send_emergency_alert()
        return None

    def _send_emergency_alert(self):
        try:
            from email_dispatcher import EmailDispatcher
            dispatcher = EmailDispatcher()
            # Enviar la alerta solo al admin
            admin_email = os.environ.get("GMAIL_USER")
            if not admin_email: return
            
            body = "ALERTA TÁCTICA OCI-1: Ambas APIs (Gemini y Groq) han fallado o caducado. El sistema automático se ha detenido. Renueva las llaves en el archivo .env."
            dispatcher.send_email(
                to_email=admin_email,
                subject="🚨 CRÍTICO: Caída de APIs en Astrology Factory",
                body_html=f"<h3>Alerta de Sistema</h3><p>{body}</p>"
            )
            print("Correo de emergencia enviado al administrador.")
        except Exception as e:
            print(f"No se pudo enviar el correo de emergencia: {e}")

if __name__ == "__main__":
    engine = AIPersonaEngine()
    test_data = {"2026-09-08": {"planets": {"Sol": "Virgo"}}}
    print(engine.generate_content(test_data))
