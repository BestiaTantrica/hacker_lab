#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PEGASO — Agente Autónomo CLI con memoria persistente
Basado en un motor ReAct manual e inmune a 429 de Gemini, usando llm_client.

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
    # Ya no es estrictamente obligatoria para el bucle interactivo principal,
    # pero la mantenemos por compatibilidad con otros scripts del lab.
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
# 3. HERRAMIENTA: EJECUCIÓN DE BASH
# --------------------------------------------------------------------------

def limitar_texto(texto: str, max_chars: int = 4000) -> str:
    """Devuelve las últimas líneas del texto que entren dentro de max_chars."""
    if not texto or len(texto) <= max_chars:
        return texto or ""
    lineas = texto.splitlines()
    resultado = []
    acumulado = 0
    for linea in reversed(lineas):
        if acumulado + len(linea) + 1 > max_chars:
            resultado.append(f"... [SALIDA TRUNCADA: {len(lineas) - len(resultado)} LÍNEAS ANTERIORES OMITIDAS] ...")
            break
        resultado.append(linea)
        acumulado += len(linea) + 1
    return "\n".join(reversed(resultado))


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
        stdout_filtrado = limitar_texto(resultado.stdout, max_chars=4000)
        stderr_filtrado = limitar_texto(resultado.stderr, max_chars=2000)
        
        partes = [
            f"[EXIT CODE]: {resultado.returncode}",
            f"[STDOUT]:\n{stdout_filtrado.strip() or '(vacío)'}",
            f"[STDERR]:\n{stderr_filtrado.strip() or '(vacío)'}",
        ]
        return "\n".join(partes)
    except subprocess.TimeoutExpired:
        return "[ERROR]: El comando excedió el timeout de 60 segundos."
    except Exception as e:
        return f"[EXCEPCIÓN]: {type(e).__name__}: {e}"


# --------------------------------------------------------------------------
# 4. MEMORIA: HISTORIAL ACOTADO + RESUMEN PERSISTENTE
# --------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(_SCRIPT_DIR, ".agent_session.json")
MEMORY_FILE  = os.path.join(_SCRIPT_DIR, ".agent_memoria.md")

MAX_HISTORY_ENTRIES = 16   # ~8 intercambios usuario/modelo en crudo
MAX_MEMORY_CHARS    = 4000 # tope del resumen persistente (~1000 tokens)


def cargar_historial():
    if not os.path.isfile(SESSION_FILE):
        return []
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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
        rol = c.get("role", "user")
        contenido = " ".join(
            p.get("text", "") for p in c.get("parts", []) if "text" in p
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
        nuevo_resumen = llm_client.completar(prompt, max_tokens=1024)
        return nuevo_resumen.strip() if nuevo_resumen else memoria_actual
    except Exception as e:
        print(f"[WARN] No se pudo comprimir memoria: {e}", file=sys.stderr)
        return memoria_actual


def guardar_historial(chat_history):
    try:
        if len(chat_history) > MAX_HISTORY_ENTRIES:
            exceso = len(chat_history) - MAX_HISTORY_ENTRIES
            turnos_viejos = chat_history[:exceso]
            historial_recortado = chat_history[exceso:]

            memoria_actual = cargar_memoria_persistente()
            memoria_nueva = resumir_turnos_viejos(None, turnos_viejos, memoria_actual)
            guardar_memoria_persistente(memoria_nueva)
        else:
            historial_recortado = chat_history

        temp_file = SESSION_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(historial_recortado, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, SESSION_FILE)
    except (KeyboardInterrupt, SystemExit):
        print("\n[WARN] Guardado de historial interrumpido por el usuario.", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] No se pudo guardar la sesión: {e}", file=sys.stderr)


def formatear_prompt_con_historial(instrucciones_sistema, historial, entrada_usuario):
    lineas = [instrucciones_sistema, "\n--- HISTORIAL DE CONVERSACIÓN ---"]
    for c in historial:
        rol = "Usuario" if c.get("role") == "user" else "Agente PEGASO"
        textos = []
        for part in c.get("parts", []):
            if "text" in part:
                textos.append(part["text"])
        lineas.append(f"{rol}: {' '.join(textos)}")
    lineas.append(f"Usuario: {entrada_usuario}")
    lineas.append("Agente PEGASO:")
    return "\n".join(lineas)


# --------------------------------------------------------------------------
# 5. IDENTIDAD DEL AGENTE + BUCLE PRINCIPAL (ReAct manual via llm_client)
# --------------------------------------------------------------------------

INSTRUCCIONES_SISTEMA_BASE = (
    "Eres el Agente PEGASO, un Administrador Linux y experto en Ciberseguridad "
    "al servicio de un investigador de Bug Bounty.\n"
    "Tu misión es auditar el sistema, asistir en tareas operativas y monitorear "
    "el pipeline de descubrimiento pasivo de activos.\n"
    "Tienes la capacidad de ejecutar comandos en el sistema del usuario de forma autónoma.\n"
    "Cuando necesites ejecutar un comando bash, debes escribirlo EXACTAMENTE dentro de un bloque "
    "de código markdown marcado como 'bash_run'. Por ejemplo:\n"
    "```bash_run\n"
    "whoami\n"
    "```\n"
    "El sistema ejecutará el comando por ti de inmediato y te devolverá el resultado.\n"
    "No des explicaciones adicionales ni justificaciones hasta recibir el resultado del comando.\n"
    "Cuando el usuario te pida que audites un paso, ejecuta los comandos necesarios "
    "y devuelve un informe breve con estado, hallazgos y siguiente acción recomendada.\n\n"
    "CRITICAL RULES FOR COMMAND EXECUTION:\n"
    "1. NEVER execute interactive commands that expect user inputs (e.g. passwords, confirmations, passphrases, ssh-keygen asking for passphrase).\n"
    "2. If you need to run SSH, ALWAYS append '-o BatchMode=yes' to prevent it from hanging or prompting. E.g. 'ssh -o BatchMode=yes ubuntu@IP \"command\"'.\n"
    "3. If you need to generate keys with ssh-keygen, ALWAYS use '-N \"\"' and other flags to make it completely silent and automatic.\n"
    "4. To audit the remote OCI server (129.80.73.248), you MUST connect to it via SSH. Do not execute local system administration commands (like systemctl status) on the user's host unless you intend to audit the local PC."
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
    cargar_dotenv()

    import llm_client
    import re

    historial = cargar_historial()
    memoria_persistente = cargar_memoria_persistente()

    print("=" * 55)
    print("  Agente PEGASO — Modo chat interactivo (Inmune a 429)")
    print("  Escribe 'salir' o Ctrl+C para terminar.")
    print("=" * 55)
    if venv_path:
        print(f"  venv: {venv_path}")
    if historial:
        print(f"  Historial: {len(historial)} entradas cargadas")
    if memoria_persistente:
        print(f"  Memoria: {len(memoria_persistente)} chars de largo plazo")
    print()

    while True:
        try:
            entrada = input("[Tú]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[PEGASO] Sesión guardada. Hasta luego.")
            guardar_historial(historial)
            break

        if entrada.lower() in ("salir", "exit", "quit"):
            print("[PEGASO] Sesión guardada. Hasta luego.")
            guardar_historial(historial)
            break
        if not entrada:
            continue

        # Añadir la entrada del usuario al historial
        historial.append({"role": "user", "parts": [{"text": entrada}]})

        intentos_loop = 0
        max_loop = 5
        
        while intentos_loop < max_loop:
            intentos_loop += 1
            
            prompt_sistema = construir_instrucciones(memoria_persistente)
            # Pasamos todo el historial acumulado en la sesión
            prompt_completo = formatear_prompt_con_historial(prompt_sistema, historial[:-1], historial[-1]["parts"][0]["text"])

            try:
                # Obtenemos la respuesta usando la cascada robusta (Groq -> Gemini)
                respuesta_texto = llm_client.completar(prompt_completo, max_tokens=1500)
                
                # Buscar si el modelo solicitó ejecutar un comando bash
                match = re.search(r"```bash_run\n(.*?)\n```", respuesta_texto, re.DOTALL)
                
                if match:
                    comando = match.group(1).strip()
                    print(f"\n[PEGASO ejecutando comando]: {comando}")
                    
                    # Ejecutar en la shell del usuario
                    resultado_ejecucion = ejecutar_comando_bash(comando)
                    
                    # Añadir la respuesta intermedia del modelo al historial
                    historial.append({"role": "model", "parts": [{"text": respuesta_texto}]})
                    
                    # Añadir el resultado de la ejecución al historial
                    resultado_mensaje = f"[RESULTADO DEL COMANDO BASH]:\n{resultado_ejecucion}"
                    historial.append({"role": "user", "parts": [{"text": resultado_mensaje}]})
                    
                    # Continuar el bucle para que el modelo procese el resultado
                    continue
                else:
                    # No hay herramientas, es la respuesta final
                    print(f"\n[PEGASO]> {respuesta_texto}\n")
                    historial.append({"role": "model", "parts": [{"text": respuesta_texto}]})
                    break
            except Exception as e:
                print(f"[ERROR durante la ejecución]: {e}")
                break
        
        # Guardar historial al final de cada turno interactivo
        guardar_historial(historial)


if __name__ == "__main__":
    main()
