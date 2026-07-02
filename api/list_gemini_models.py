#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

def main():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Error: GEMINI_API_KEY no está configurada en el entorno.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    print(f"Consultando modelos disponibles en Gemini con tu API Key...")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            print("\n✅ Modelos disponibles para tu clave:")
            for m in data.get("models", []):
                print(f" - {m.get('name')} ({m.get('displayName')})")
    except urllib.error.HTTPError as e:
        print(f"\n❌ Error HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")

if __name__ == "__main__":
    # Cargar .env si existe
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
    main()
