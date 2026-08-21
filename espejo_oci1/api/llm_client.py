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

def _load_env_file(filepath):
    """Carga variables desde un archivo .env si existe, usando bibliotecas estándar."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key, val = parts[0].strip(), parts[1].strip()
                        val = val.strip('"\'')
                        os.environ[key] = val

# Configuración del logger
logger = logging.getLogger(__name__)

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
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "entorno.env")
        _load_env_file(env_path)
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

    def is_available(self) -> bool:
        return bool(self.api_key)

    def completar(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
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

    def completar(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }

        data = _post_json(url, headers, payload, timeout=25)
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Respuesta inesperada de Gemini: {data}") from e


# ---------------------------------------------------------------------------
# 3. OpenRouter (Fallback 2)
# ---------------------------------------------------------------------------
class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free").strip()

    def is_available(self) -> bool:
        return bool(self.api_key)

    def completar(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000", # Necesario para OpenRouter
            "X-Title": "C2 Copilot"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        data = _post_json(url, headers, payload, timeout=25)
        return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Cadena de ejecución y mapeo
# ---------------------------------------------------------------------------
PROVIDERS = {
    "groq": GroqProvider(),
    "gemini": GeminiProvider(),
    "openrouter": OpenRouterProvider()
}

PROVIDER_CHAIN: list[LLMProvider] = [
    PROVIDERS["groq"],
    PROVIDERS["gemini"],
    PROVIDERS["openrouter"]
]

def completar(prompt: str, max_tokens: int = 512, provider_name: str = None, temperature: float = 0.0) -> str:
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
        return provider.completar(prompt, max_tokens=max_tokens, temperature=temperature)

    # Comportamiento por defecto: cascada/fallback
    errors = []
    for provider in PROVIDER_CHAIN:
        if not provider.is_available():
            logger.debug("[%s] omitido (sin API key configurada)", provider.name)
            continue

        try:
            logger.info("[%s] intentando completado...", provider.name)
            respuesta = provider.completar(prompt, max_tokens=max_tokens, temperature=temperature)
            logger.info("[%s] completado con éxito (%d caracteres)", provider.name, len(respuesta))
            return respuesta
        except Exception as exc:
            err_msg = f"[{provider.name}] falló: {exc}"
            logger.warning(err_msg)
            errors.append(err_msg)

    raise LLMError("Todos los proveedores en cascada fallaron:\n" + "\n".join(errors))


class LLMError(Exception):
    """Excepción general cuando la cascada de modelos no logra completarse."""
    pass
