import os
import sys
import subprocess
from pathlib import Path

# 1. Cargar variables desde el archivo .env local
def cargar_env():
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Limpiar comillas si existen
                    value = value.strip('"').strip("'")
                    os.environ[key.strip()] = value

cargar_env()

# Verificar que la API KEY esté cargada
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY no encontrada en el entorno ni en el archivo .env.")
    sys.exit(1)

from google import genai
from google.genai import types

# 2. Inicialización del Cliente
client = genai.Client()

# 3. Herramienta de ejecución Bash
def ejecutar_comando_bash(comando: str) -> str:
    """Ejecuta un comando en la terminal de forma local y devuelve la salida estándar o error."""
    try:
        resultado = subprocess.run(
            comando, shell=True, capture_output=True, text=True, timeout=30
        )
        return f"STDOUT:\n{resultado.stdout}\nSTDERR:\n{resultado.stderr}"
    except Exception as e:
        return f"EXCEPCIÓN: {str(e)}"

herramientas_disponibles = {
    "ejecutar_comando_bash": ejecutar_comando_bash
}

# 4. Configuración del Sistema
instrucciones_sistema = (
    "Eres el Agente PEGASO, un Administrador de Sistemas Linux experto. "
    "Tienes permiso explícito para auditar y operar el sistema mediante la función `ejecutar_comando_bash`. "
    "Sé quirúrgico, estructural y preciso. Analiza minuciosamente las salidas de los comandos antes de proponer cambios."
)

prompt_usuario = " ".join(sys.argv[1:])
if not prompt_usuario:
    print("Error: Envía una instrucción o consulta.")
    sys.exit(1)

# 5. Inicialización del Chat (Mantiene el contexto durante la ejecución de herramientas)
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=instrucciones_sistema,
        tools=[ejecutar_comando_bash],
        temperature=0.2
    )
)

# 6. Bucle Agéntico (ReAct Loop)
response = chat.send_message(prompt_usuario)

while response.function_calls:
    for call in response.function_calls:
        func_name = call.name
        func_args = call.args
        
        if func_name in herramientas_disponibles:
            resultado_accion = herramientas_disponibles[func_name](**func_args)
            
            response = chat.send_message(
                types.Part.from_function_response(
                    name=func_name,
                    response={"result": resultado_accion}
                )
            )
        else:
            print(f"Función no soportada: {func_name}")
            sys.exit(1)

print(response.text)
