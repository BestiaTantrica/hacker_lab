"""
llm_client.py — Cliente LLM con fallback en cascada (Groq y Gemini)
===================================================================
Modelos soportados:
  1. Groq (Principal - Free Tier)
  2. Gemini Flash (Fallback 1)

Diseño:
  - Usa únicamente la biblioteca estándar de Python 'urllib.request' y 'json' (cero dependencias).
  - Permite realizar fallback en cascada por defecto.
  - Permite llamar a un proveedor específico directamente usando completar(prompt, provider_name="nombre").
"""

import os
import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

# Configuración del logger
logger = logging.getLogger(__name__)

def _cargar_dotenv():
    """Carga variables de entorno desde múltiples rutas posibles."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(script_dir, ".env"),
        os.path.join(script_dir, "..", "config", "entorno.env"),
        os.path.expanduser("~/plataforma_operativa/config/entorno.env"),
    ]
    for ruta in candidatos:
        ruta = os.path.normpath(ruta)
        if not os.path.isfile(ruta):
            continue
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, _, valor = linea.partition("=")
                clave = clave.strip()
                valor = valor.strip().strip('"').strip("'")
                if clave and clave not in os.environ:
                    os.environ[clave] = valor
        return

_cargar_dotenv()

class LLMProvider(ABC):
    """Interfaz base común para todos los proveedores."""
    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si las claves necesarias están configuradas."""
        pass

    @abstractmethod
    def completar(self, prompt: str, max_tokens: int = 512) -> str:
        """Realiza la llamada HTTP al proveedor y retorna el texto limpio."""
        pass


# Helper para realizar peticiones POST JSON usando urllib estándar con User-Agent
def _post_json(url: str, headers: dict, payload: dict, timeout: int = 25) -> dict:
    data_bytes = json.dumps(payload).encode("utf-8")
    
    # Asegurar un User-Agent estándar para evitar bloqueos como el 1010 de Cloudflare
    headers = headers.copy()
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code}: {err_body}") from e
    except Exception as e:
        raise RuntimeError(f"Error de red/conexión: {e}") from e


# ---------------------------------------------------------------------------
# 1. Groq
# ---------------------------------------------------------------------------
class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

    def is_available(self) -> bool:
        return bool(self.api_key)

    def completar(self, prompt: str, max_tokens: int = 512) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }
        
        data = _post_json(url, headers, payload, timeout=20)
        return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# 2. Google Gemini (Flash)
# ---------------------------------------------------------------------------
class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    def is_available(self) -> bool:
        return bool(self.api_key)

    def completar(self, prompt: str, max_tokens: int = 512) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens
            }
        }

        data = _post_json(url, headers, payload, timeout=25)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Respuesta inesperada de Gemini: {data}") from e


# ---------------------------------------------------------------------------
# Cadena de ejecución y mapeo
# ---------------------------------------------------------------------------
PROVIDERS = {
    "groq": GroqProvider(),
    "gemini": GeminiProvider()
}

PROVIDER_CHAIN: list[LLMProvider] = [
    PROVIDERS["groq"],
    PROVIDERS["gemini"]
]

def completar(prompt: str, max_tokens: int = 512, provider_name: str = None) -> str:
    """
    Intenta resolver la petición.
    - Si se especifica provider_name, llama directamente a ese proveedor sin fallback.
    - Si no se especifica, recorre los proveedores disponibles en cascada (Groq -> Gemini).
    """
    if provider_name:
        name_clean = provider_name.lower().strip()
        if name_clean not in PROVIDERS:
            raise ValueError(f"Proveedor '{provider_name}' no soportado. Opciones: {list(PROVIDERS.keys())}")
        
        provider = PROVIDERS[name_clean]
        if not provider.is_available():
            raise LLMError(f"El proveedor '{provider_name}' fue invocado directamente pero no tiene API Key configurada.")
        
        logger.info("[%s] Invocación directa...", provider.name)
        return provider.completar(prompt, max_tokens=max_tokens)

    # Comportamiento por defecto: cascada/fallback
    errors = []
    MAX_RETRIES = 3
    
    for provider in PROVIDER_CHAIN:
        if not provider.is_available():
            logger.debug("[%s] omitido (sin API key configurada)", provider.name)
            continue

        intentos = 0
        while intentos < MAX_RETRIES:
            try:
                logger.info("[%s] intentando completado... (Intento %d/%d)", provider.name, intentos + 1, MAX_RETRIES)
                respuesta = provider.completar(prompt, max_tokens=max_tokens)
                logger.info("[%s] completado con éxito (%d caracteres)", provider.name, len(respuesta))
                return respuesta
            except Exception as exc:
                err_msg = str(exc)
                logger.warning("[%s] falló: %s", provider.name, err_msg)
                
                if "429" in err_msg or "rate limit" in err_msg.lower() or "RESOURCE_EXHAUSTED" in err_msg:
                    intentos += 1
                    if intentos < MAX_RETRIES:
                        logger.info("⏳ Límite de API alcanzado. Esperando 20 segundos antes de reintentar...")
                        import time
                        time.sleep(20)
                        continue
                
                errors.append(f"[{provider.name}] falló: {err_msg}")
                break

    raise LLMError("Todos los proveedores en cascada fallaron:\n" + "\n".join(errors))



class LLMError(Exception):
    """Excepción general cuando la cascada de modelos no logra completarse."""
    pass
