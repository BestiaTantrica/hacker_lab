#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEGASO — Agente Autónomo CLI con memoria persistente
Basado en google-genai / gemini-2.5-flash

Uso:
    python3 pegaso.py           → Modo chat interactivo (historial + memoria)
    ./run                       → Igual (el launcher busca el venv automáticamente)

Memoria:
    .agent_session.json   → Historial crudo reciente (últimos 16 turnos)
    .agent_memoria.md     → Resumen comprimido de largo plazo (~4000 chars)
"""

import os
import sys
import json
import glob
import subprocess
import importlib

# --------------------------------------------------------------------------
# 1. ARQUITECTURA DE ENTORNO VIRTUAL (PEP 668)
# --------------------------------------------------------------------------

VENV_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv"),
    "/home/tomas2/workspace_lab/venv",
    os.path.join(os.getcwd(), "venv"),
]


def localizar_venv():
    for candidato in VENV_CANDIDATES:
        candidato = os.path.abspath(candidato)
        if os.path.isdir(candidato) and os.path.isfile(
            os.path.join(candidato, "bin", "python3")
        ):
            return candidato
    return None


def activar_venv(venv_path):
    if not venv_path:
        return
    bin_dir = os.path.join(venv_path, "bin")
    os.environ["VIRTUAL_ENV"] = venv_path
    path_actual = os.environ.get("PATH", "")
    if bin_dir not in path_actual.split(os.pathsep):
        os.environ["PATH"] = bin_dir + os.pathsep + path_actual
    os.environ.pop("PYTHONHOME", None)
    patrones = [
        os.path.join(venv_path, "lib", "python3.*", "site-packages"),
        os.path.join(venv_path, "lib64", "python3.*", "site-packages"),
    ]
    for patron in patrones:
        for sp in glob.glob(patron):
            if sp not in sys.path:
                sys.path.insert(0, sp)


def pip_del_venv(venv_path):
    if not venv_path:
        return None
    for nombre in ("pip3", "pip"):
        ruta = os.path.join(venv_path, "bin", nombre)
        if os.path.isfile(ruta):
            return ruta
    return None


def asegurar_google_genai(venv_path):
    try:
        import google.genai  # noqa: F401
        return
    except ImportError:
        pass

    pip_exec = pip_del_venv(venv_path)
    print("[PEGASO] Instalando dependencia 'google-genai'...", file=sys.stderr)
    try:
        if pip_exec:
            subprocess.run(
                [pip_exec, "install", "--quiet", "--disable-pip-version-check", "google-genai"],
                check=True,
            )
        else:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet",
                 "--disable-pip-version-check", "google-genai"],
                check=True,
            )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo instalar google-genai: {e}", file=sys.stderr)
        sys.exit(1)

    importlib.invalidate_caches()
    try:
        import google.genai  # noqa: F401
    except ImportError:
        print("[ERROR] google-genai instalado pero no importable. Revisa el venv.", file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------
# 2. CARGA DE CREDENCIALES (.env nativo — sin dependencias externas)
# --------------------------------------------------------------------------

def cargar_dotenv():
    """Busca .env en el directorio del script y en el directorio actual."""
    rutas = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    for ruta in rutas:
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
        break  # Usa el primero que encuentre


# --------------------------------------------------------------------------
# 3. HERRAMIENTA: EJECUCIÓN DE BASH (tool calling para el modelo)
# --------------------------------------------------------------------------

def ejecutar_comando_bash(comando: str) -> str:
    """Ejecuta un comando de shell en el sistema del usuario y devuelve el resultado.

    Usa esto para explorar el sistema de archivos, revisar procesos, auditar
    crontab, instalar paquetes, escribir archivos o cualquier tarea que
    normalmente requeriría que el usuario abra una terminal.

    Args:
        comando: El comando bash exacto a ejecutar (se ejecuta con /bin/bash -c).

    Returns:
        Un string con el código de salida, STDOUT y STDERR del comando,
        o el detalle de la excepción si algo falla.
    """
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=60,
        )
        partes = [
            f"[EXIT CODE]: {resultado.returncode}",
            f"[STDOUT]:\n{resultado.stdout.strip() or '(vacío)'}",
            f"[STDERR]:\n{resultado.stderr.strip() or '(vacío)'}",
        ]
        return "\n".join(partes)
    except subprocess.TimeoutExpired:
        return "[ERROR]: El comando excedió el timeout de 60 segundos."
    except Exception as e:
        return f"[EXCEPCIÓN]: {type(e).__name__}: {e}"


# --------------------------------------------------------------------------
# 4. MEMORIA: HISTORIAL ACOTADO + RESUMEN PERSISTENTE
# --------------------------------------------------------------------------

# Los archivos se guardan junto al script, no en el cwd, para que la memoria
# sobreviva sin importar desde qué directorio se ejecute pegaso.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(_SCRIPT_DIR, ".agent_session.json")
MEMORY_FILE  = os.path.join(_SCRIPT_DIR, ".agent_memoria.md")

MAX_HISTORY_ENTRIES = 16   # ~8 intercambios usuario/modelo en crudo
MAX_MEMORY_CHARS    = 4000 # tope del resumen persistente (~1000 tokens)


def cargar_historial(types_mod):
    if not os.path.isfile(SESSION_FILE):
        return []
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [types_mod.Content.model_validate(item) for item in data]
    except Exception as e:
        print(f"[WARN] No se pudo cargar la sesión previa: {e}", file=sys.stderr)
        return []


def cargar_memoria_persistente():
    if not os.path.isfile(MEMORY_FILE):
        return ""
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def guardar_memoria_persistente(texto):
    texto = texto.strip()
    if len(texto) > MAX_MEMORY_CHARS:
        # Quedarse con la parte más reciente (ya viene ordenada cronológicamente)
        texto = texto[-MAX_MEMORY_CHARS:]
    temp_file = MEMORY_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(texto)
        os.replace(temp_file, MEMORY_FILE)
    except Exception as e:
        print(f"[WARN] No se pudo guardar la memoria persistente de forma atómica: {e}", file=sys.stderr)


def resumir_turnos_viejos(client, turnos_viejos, memoria_actual):
    """
    Convierte los turnos que van a descartarse en una lista compacta de
    datos útiles, fusionándolos con la memoria persistente existente.
    """
    texto_turnos = []
    for c in turnos_viejos:
        rol = c.role
        contenido = " ".join(
            p.text for p in (c.parts or []) if getattr(p, "text", None)
        )
        if contenido.strip():
            texto_turnos.append(f"[{rol}] {contenido.strip()}")

    if not texto_turnos:
        return memoria_actual

    prompt = (
        "Sos un compresor de memoria para un agente de sistemas. "
        "A continuación hay memoria previa y turnos de conversación que van a "
        "descartarse. Generá una lista breve en viñetas SOLO con información "
        "útil y duradera (decisiones tomadas, datos del sistema/servidor, "
        "tareas pendientes, preferencias del usuario, rutas o configuraciones "
        "relevantes). Descartá saludos, chit-chat y cosas ya resueltas sin "
        "valor futuro. No repitas puntos ya cubiertos en la memoria previa. "
        "Máximo 15 viñetas, español, sin explicaciones extra.\n\n"
        f"--- MEMORIA PREVIA ---\n{memoria_actual or '(vacía)'}\n\n"
        f"--- TURNOS A COMPRIMIR ---\n" + "\n".join(texto_turnos)
    )

    try:
        import llm_client
        # Usamos llm_client.completar que tiene fallback Groq -> Gemini y timeouts estrictos
        nuevo_resumen = llm_client.completar(prompt, max_tokens=1024)
        return nuevo_resumen.strip() if nuevo_resumen else memoria_actual
    except Exception as e:
        print(f"[WARN] No se pudo comprimir memoria: {e}", file=sys.stderr)
        return memoria_actual


def guardar_historial(client, chat):
    """
    Guarda el historial crudo acotado a MAX_HISTORY_ENTRIES.
    Lo que se descarta se comprime y se funde en la memoria persistente.
    """
    try:
        historial = chat.get_history()

        if len(historial) > MAX_HISTORY_ENTRIES:
            exceso = len(historial) - MAX_HISTORY_ENTRIES
            turnos_viejos = historial[:exceso]
            historial_recortado = historial[exceso:]

            memoria_actual = cargar_memoria_persistente()
            memoria_nueva = resumir_turnos_viejos(client, turnos_viejos, memoria_actual)
            guardar_memoria_persistente(memoria_nueva)
        else:
            historial_recortado = historial

        data = [c.model_dump(mode="json", exclude_none=True) for c in historial_recortado]
        temp_file = SESSION_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, SESSION_FILE)
    except (KeyboardInterrupt, SystemExit):
        print("\n[WARN] Guardado de historial interrumpido por el usuario.", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] No se pudo guardar la sesión: {e}", file=sys.stderr)


# --------------------------------------------------------------------------
# 5. IDENTIDAD DEL AGENTE + BUCLE PRINCIPAL
# --------------------------------------------------------------------------

INSTRUCCIONES_SISTEMA_BASE = (
    "Eres el Agente PEGASO, un Administrador Linux y experto en Ciberseguridad "
    "al servicio de un investigador de Bug Bounty. "
    "Tu misión es auditar el sistema, asistir en tareas operativas y monitorear "
    "el pipeline de descubrimiento pasivo de activos. "
    "Al usuario le cuesta ejecutar comandos complejos: no le des instrucciones para "
    "copiar y pegar; usa tu herramienta Bash para hacer el trabajo directamente. "
    "Cuando detectes un problema, propone una solución concreta. "
    "Cuando el usuario te pida que audites un paso, ejecuta los comandos necesarios "
    "y devuelve un informe breve con estado, hallazgos y siguiente acción recomendada."
)


def construir_instrucciones(memoria_persistente):
    if not memoria_persistente:
        return INSTRUCCIONES_SISTEMA_BASE
    return (
        f"{INSTRUCCIONES_SISTEMA_BASE}\n\n"
        "--- MEMORIA DE LARGO PLAZO (hechos útiles de sesiones anteriores) ---\n"
        f"{memoria_persistente}\n"
        "--- FIN DE MEMORIA ---\n"
        "Usá esta memoria como contexto, pero priorizá siempre lo que el "
        "usuario diga ahora si hay contradicción."
    )


def main():
    venv_path = localizar_venv()
    activar_venv(venv_path)
    asegurar_google_genai(venv_path)
    cargar_dotenv()

    from google import genai
    from google.genai import types

    keys_disponibles = []
    # Clave primaria
    key_primaria = os.environ.get("GEMINI_API_KEY")
    if key_primaria:
        keys_disponibles.append(key_primaria)
    
    # Buscar claves secundarias (GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.)
    idx = 2
    while True:
        key_extra = os.environ.get(f"GEMINI_API_KEY_{idx}")
        if key_extra:
            keys_disponibles.append(key_extra)
            idx += 1
        else:
            break

    if not keys_disponibles:
        print(
            "[ERROR] No se encontró GEMINI_API_KEY (ni en el entorno ni en .env).",
            file=sys.stderr,
        )
        sys.exit(1)

    key_index = 0
    api_key = keys_disponibles[key_index]

    # Configuración de timeout de 30 segundos y reintentos acotados (max 3 intentos)
    # para evitar bloqueos infinitos de tenacity
    http_opts = types.HttpOptions(
        timeout=30000,  # 30 segundos
        retry_options=types.HttpRetryOptions(
            attempts=3,
            initial_delay=1.0,
            max_delay=5.0
        )
    )
    client = genai.Client(api_key=api_key, http_options=http_opts)

    historial_previo = cargar_historial(types)
    memoria_persistente = cargar_memoria_persistente()

    chat = client.chats.create(
        model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
        history=historial_previo,
        config=types.GenerateContentConfig(
            system_instruction=construir_instrucciones(memoria_persistente),
            tools=[ejecutar_comando_bash],
        ),
    )

    print("=" * 55)
    print("  Agente PEGASO — Modo chat interactivo")
    print("  Escribe 'salir' o Ctrl+C para terminar.")
    print("=" * 55)
    if venv_path:
        print(f"  venv: {venv_path}")
    if historial_previo:
        print(f"  Historial: {len(historial_previo)} entradas cargadas")
    if memoria_persistente:
        print(f"  Memoria: {len(memoria_persistente)} chars de largo plazo")
    print()

    while True:
        try:
            entrada = input("[Tú]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[PEGASO] Sesión guardada. Hasta luego.")
            guardar_historial(client, chat)
            break

        if entrada.lower() in ("salir", "exit", "quit"):
            print("[PEGASO] Sesión guardada. Hasta luego.")
            guardar_historial(client, chat)
            break
        if not entrada:
            continue

        try:
            respuesta = chat.send_message(entrada)
            texto = respuesta.text if respuesta.text else "(sin texto de respuesta)"
            print(f"\n[PEGASO]> {texto}\n")
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower():
                if len(keys_disponibles) > 1:
                    print(f"\n[PEGASO] Cuota agotada en la clave {key_index + 1}. Rotando a clave de respaldo...", file=sys.stderr)
                    key_index = (key_index + 1) % len(keys_disponibles)
                    api_key = keys_disponibles[key_index]
                    try:
                        historial_actual = chat.get_history()
                        client = genai.Client(api_key=api_key, http_options=http_opts)
                        chat = client.chats.create(
                            model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
                            history=historial_actual,
                            config=types.GenerateContentConfig(
                                system_instruction=construir_instrucciones(memoria_persistente),
                                tools=[ejecutar_comando_bash],
                            ),
                        )
                        print("[PEGASO] Clave de respaldo cargada con éxito. Reintentando tu mensaje...\n", file=sys.stderr)
                        respuesta = chat.send_message(entrada)
                        texto = respuesta.text if respuesta.text else "(sin texto de respuesta)"
                        print(f"\n[PEGASO]> {texto}\n")
                    except Exception as re_err:
                        print(f"[ERROR tras rotación]: {re_err}")
                else:
                    print(f"[ERROR durante la ejecución]: {e}\n(Tip: Configura GEMINI_API_KEY_2 en tu .env para rotar claves automáticamente)")
            else:
                print(f"[ERROR durante la ejecución]: {e}")
        finally:
            guardar_historial(client, chat)


if __name__ == "__main__":
    main()
