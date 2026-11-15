#!/usr/bin/env python3
"""
🌒 CÉLULA MADRE 1 — Script 1.1: generador_guiones.py
Redacta guiones astrológicos leyendo el ADN JSON.
Salida siempre en JSON estructurado, nunca texto libre.
NO toca audio, NO toca video, NO toca tiempos.

Uso:
  python v2/celula_1/generador_guiones.py --opcion 1              # Guion diario
  python v2/celula_1/generador_guiones.py --opcion 2              # Guion semanal/resumen
  python v2/celula_1/generador_guiones.py --opcion 3              # Horóscopo personalizado
  python v2/celula_1/generador_guiones.py --opcion 3 --natal /ruta/carta.json
  python v2/celula_1/generador_guiones.py --opcion 4              # Inyectar CTA en toma 7
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

# ── Carga del entorno y ADN ──────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EVENTO_ID      = ADN["produccion"]["evento_id"]
SEMANA         = ADN["produccion"]["semana_prefijo"]
VAULT_BASE     = Path(ADN["assets"]["boveda_base"])
TEMP_DIR       = VAULT_BASE / "temp"
ROLE_PATH      = FACTORY_ROOT / "content_factory" / "ROLE_SCRIPTWRITER.md"

# ── Carta natal de Tomás (default para horóscopo personal) ───────────────────
NATAL_DEFAULT = {
    "nombre": "Tomás",
    "fecha": "1995-10-23",
    "hora": "14:30",
    "lugar": "Buenos Aires, Argentina",
    "lat": -34.6037,
    "lon": -58.3816,
    "utc_offset": -3,
    "planetas": {
        "Sol": "Escorpio",
        "Luna": "Aries",
        "Mercurio": "Escorpio",
        "Venus": "Libra",
        "Marte": "Virgo",
        "Júpiter": "Sagitario",
        "Saturno": "Piscis",
        "Urano": "Capricornio",
        "Neptuno": "Capricornio",
        "Plutón": "Escorpio",
        "Ascendente": "Aries"
    }
}

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def cargar_role_scriptwriter() -> str:
    """Carga el prompt de rol del guionista."""
    if ROLE_PATH.exists():
        return ROLE_PATH.read_text(encoding="utf-8")
    warn(f"ROLE_SCRIPTWRITER.md no encontrado en {ROLE_PATH}. Usando rol genérico.")
    return "Eres un astrólogo profesional y guionista experto en contenido para redes sociales."

import time
import google.genai as genai

# Importar el gestor de cuotas
sys.path.append(str(FACTORY_ROOT))
from v2 import cuota

def generar_con_gemini_cuota(prompt: str, modelos: list) -> str:
    """Envía un prompt a Gemini usando el rotador de llaves de cuota.py."""
    for intento in range(4): # Intentar con 4 llaves distintas si hace falta
        elegida = cuota.elegir_key()
        if not elegida:
            err("Todas las cuotas de Gemini están agotadas. Abortando script.")
            sys.exit(1)
            
        nombre, key = elegida
        cuota.esperar_ritmo()
        
        try:
            client = genai.Client(api_key=key)
        except Exception as e:
            warn(f"Error inicializando cliente con {nombre}: {e}")
            continue
            
        for model_name in modelos:
            try:
                info(f"Intentando con modelo: {model_name} (Llave {nombre})")
                respuesta = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                texto_raw = respuesta.text
                cuota.registrar_uso(nombre)
                return texto_raw
            except Exception as e:
                tipo = cuota.registrar_error(nombre, e)
                if tipo == "otro":
                    warn(f"Fallo no relacionado a cuota con {model_name} en {nombre}: {e}")
                else:
                    warn(f"Fallo de cuota en {nombre} ({tipo}). Saltando a otra llave...")
                    break # Salimos del loop de modelos para pedir una llave nueva a cuota.py
                    
    err("Imposible generar guion tras multiples intentos y llaves por cuota de API. Abortando.")
    sys.exit(1)

def obtener_panorama_astral_completo() -> dict:
    """
    Calcula posiciones actuales y las cruza para encontrar aspectos,
    luego los traduce usando el Oráculo (lexico_astrologico.json).
    """
    try:
        from astrology_engine.ephemeris_calculator import EphemerisCalculator
        from astrology_engine.aspects_matcher import AspectsMatcher
        
        calc = EphemerisCalculator()
        matcher = AspectsMatcher()
        ahora = datetime.datetime.utcnow()
        posiciones = calc.calculate_planets(ahora)
        
        if not posiciones: return {}
        
        aspectos_crudos = matcher.find_aspects(posiciones)
        
        # Cargar Lexico
        lexico_path = FACTORY_ROOT / "astrology_engine" / "lexico_astrologico.json"
        lexico = {}
        if lexico_path.exists():
            with open(lexico_path, encoding="utf-8") as f:
                lexico = json.load(f)
                
        # Construir string descriptivo
        resultado = {
            "posiciones": posiciones,
            "aspectos_detectados": aspectos_crudos,
            "texto_traducido": ""
        }
        
        if aspectos_crudos:
            texto = "\n=== RED DE ASPECTOS ACTIVOS EN EL CIELO HOY ===\n"
            for a in aspectos_crudos:
                p1 = a['p1']
                p2 = a['p2']
                asp = a['aspect']
                
                significado_p1 = lexico.get("planetas", {}).get(p1, "")
                significado_p2 = lexico.get("planetas", {}).get(p2, "")
                significado_asp = lexico.get("aspectos", {}).get(asp, "")
                
                texto += f"- {p1} y {p2} interactúan (Geometría: {asp})\n"
                if significado_asp:
                    texto += f"  Tensión de la interacción: {significado_asp}\n"
                if significado_p1:
                    texto += f"  Fuerza 1 ({p1}): {significado_p1}\n"
                if significado_p2:
                    texto += f"  Fuerza 2 ({p2}): {significado_p2}\n"
                texto += "\n"
            resultado["texto_traducido"] = texto
        
        return resultado
    except Exception as e:
        warn(f"No se pudo calcular panorama astral completo: {e}")
        return {}

def limpiar_json_gemini(texto: str) -> str:
    """
    Limpia la respuesta de Gemini eliminando bloques de código markdown.
    Maneja ```json ... ``` y ``` ... ```.
    """
    texto = texto.strip()
    # Eliminar bloques de código markdown
    texto = re.sub(r'^```(?:json)?\s*', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\s*```$', '', texto, flags=re.MULTILINE)
    texto = texto.strip()
    return texto

GUIONES_DIR = Path(ADN["assets"]["paths"].get("guiones", VAULT_BASE / "Guiones"))

def guardar_guion(guion_data: dict, sufijo: str = "") -> Path:
    """Guarda el guion JSON en /Guiones/guion_<evento><sufijo>.json"""
    asegurar_dir(GUIONES_DIR)
    nombre = f"guion_{EVENTO_ID}{sufijo}.json"
    ruta = GUIONES_DIR / nombre
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(guion_data, f, ensure_ascii=False, indent=2)
    ok(f"Guion guardado: {ruta}")
    return ruta

FRASES_PROHIBIDAS_CLICHES = [
    "la trampa:",
    "la trampa es",
    "la maestría de hoy",
    "pulseada",
    "pulseadas",
    "nuestra biografía",
    "hagan clic",
    "ustedes",
    "vosotros",
    "veneno",
    "destruís todo",
    "abismo",
    "rabia envenenada",
    "cae la careta",
    "se caen las caretas",
    "caen las caretas",
    "enlace de la bio",
    "link de la bio",
    "andá a mi link",
    "entrá al link de mi perfil",
    "link de mi perfil",
    "aire se vuelve denso",
    "denso y eléctrico",
    "danza de los astros"
]

def validar_estructura_guion(guion_data: dict, num_tomas_esperadas: int = 5) -> bool:
    """Verifica que el JSON tenga la estructura y calidad editorial correcta."""
    valido, razon = validar_guion_editorial(guion_data, num_tomas_esperadas)
    if not valido:
        err(f"Validación editorial falló: {razon}")
        return False
    return True

def validar_guion_editorial(guion_data: dict, num_tomas_esperadas: int = 5) -> tuple[bool, str]:
    """
    Validador léxico, estructural y de tono editorial de Tomás.
    Verifica que el guion sea auténtico, conciso y libre de clichés.
    """
    if "tomas" not in guion_data:
        return False, "El JSON no contiene la clave 'tomas'"
    tomas = guion_data["tomas"]
    if not isinstance(tomas, list) or len(tomas) != num_tomas_esperadas:
        return False, f"Se esperaban exactamente {num_tomas_esperadas} tomas, se recibieron {len(tomas) if isinstance(tomas, list) else 'ninguna'}"

    total_palabras = 0
    for i, t in enumerate(tomas):
        texto = t.get("texto", "").strip()
        if not texto:
            return False, f"Toma {i+1} tiene texto vacío"
        
        words = texto.split()
        total_palabras += len(words)
        texto_lower = texto.lower()

        # Revisar clichés prohibidos en cada toma
        for f in FRASES_PROHIBIDAS_CLICHES:
            if f in texto_lower:
                return False, f"Toma {i+1} contiene la frase/cliché prohibido: '{f}'"

        # Verificar ausencia de tuteo neutro despersonalizado
        for pronombre in [" tú ", " ti ", "contigo"]:
            if pronombre in f" {texto_lower} ":
                return False, f"Toma {i+1} usa tuteo neutro ('{pronombre.strip()}'). Debe usar voseo rioplatense ('vos', 'te', 'mirá', 'sentís')."

    if total_palabras < 65 or total_palabras > 105:
        return False, f"El guion tiene {total_palabras} palabras. El estándar de Tomás es de 75 a 95 palabras."

    toma_3 = tomas[2].get("texto", "").lower()
    terminos_toma3 = ["reloj", "astrolabio", "cielo", "grados", "aspecto", "cuadratura", "conjunción", "oposición", "trígono", "sextil", "choque", "conecta"]
    if not any(k in toma_3 for k in terminos_toma3):
        return False, "Toma 3 no hace referencia visual al reloj/astrolabio o los grados celestes."

    toma_5 = tomas[4].get("texto", "").lower()
    if not any(k in toma_5 for k in ["perfil", "link", "casa", "carta"]):
        return False, "Toma 5 no contiene un CTA válido hacia el link del perfil / carta natal."

    return True, "OK"

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 1 — Guion Diario (Tránsito)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_1_guion_diario():
    """
    Genera el guion del video diario leyendo el ADN completo.
    Salida: /temp/guion_<evento>.json con estructura de N tomas.
    """
    log("\n✍️  OPCIÓN 1 — Guion Diario", MAGENTA)

    role_text   = cargar_role_scriptwriter()
    transito    = ADN["transito"]
    arquetipos  = ADN["arquetipos"]
    produccion  = ADN["produccion"]
    num_tomas   = 5

    # Calcular efemérides reales y cruzar aspectos
    panorama = obtener_panorama_astral_completo()
    efemerides_str = ""
    if panorama:
        efemerides_str = "\n\nPOSICIONES PLANETARIAS REALES (calculadas ahora):\n"
        for planeta, grado in panorama["posiciones"].items():
            efemerides_str += f"  {planeta}: {grado:.1f}°\n"
        if panorama.get("texto_traducido"):
            efemerides_str += panorama["texto_traducido"]

    # Leer termometro_global si existe
    termometro_str = ""
    termometro_path = TEMP_DIR / "termometro_actual.json"
    if termometro_path.exists():
        try:
            with open(termometro_path, "r", encoding="utf-8") as f:
                term = json.load(f)
                termometro_str = f"""
=== CONTEXTO DEL MUNDO REAL (Termómetro Global) ===
Clima emocional: {term.get('clima_emocional', '')}
Temas dominantes: {', '.join(term.get('temas_dominantes', []))}
Foco regional (Argentina): {term.get('foco_argentina', '')}
Arquetipo social activo: {term.get('arquetipo_social', '')}
-> Capta sutilmente este Zeitgeist para darle peso real al relato, sin nombrar noticias explícitas.
"""
        except Exception as e:
            warn(f"No se pudo cargar termometro_actual.json: {e}")

    # Cargar Guiones Canónicos de Oro (Estándar Canónico de Tomás)
    ejemplos_oro_path = FACTORY_ROOT / "v2" / "celula_1" / "ejemplos_oro_diarios.json"
    ejemplos_oro_str = ""
    if ejemplos_oro_path.exists():
        try:
            with open(ejemplos_oro_path, "r", encoding="utf-8") as f:
                oro_data = json.load(f)
                ejemplos_oro_str = "\n=== GUIONES DE ORO CANÓNICOS (VOZ Y PERSONALIDAD REAL DE TOMÁS) ===\n"
                ejemplos_oro_str += "Debes imitar con máxima fidelidad la estructura, calidez empática, sabiduría psicológica, concisión (~65-75 palabras en total) y la personalidad cercana, lúcida y educativa de Tomás:\n"
                for g in oro_data.get("guiones", []):
                    ejemplos_oro_str += f"\n[MODELO CANÓNICO DE TOMÁS: {g['titulo']} - {g['transito']}]\n"
                    for t in g.get("tomas", []):
                        ejemplos_oro_str += f"  Toma {t['num']} ({t.get('rol', '')}): \"{t['locucion']}\"\n"
        except Exception as e:
            warn(f"No se pudieron cargar ejemplos de oro: {e}")

    p1_nombre = transito['planeta'].split(' y ')[0] if ' y ' in transito['planeta'] else transito['planeta']

    feedback_retry = ""
    guion_data = None
    CANDIDATE_MODELS = ['gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'gemini-flash-latest']

    for intento in range(1, 4):
        info(f"Generando guion (Intento {intento}/3)...")

        prompt = f"""
{role_text}
{termometro_str}
{ejemplos_oro_str}

=== ADN DEL TRÁNSITO ===
Evento: {produccion['evento_titulo']}
Fecha publicación: {produccion['fecha_publicacion']}
Tránsito: {transito['planeta']} ({transito['simbolo_planetario']}) — Signo: {transito['signo_destino']} ({transito['simbolo_signo']})
Tipo: {transito['tipo_aspecto']} — Intensidad: {transito['intensidad']}
Descripción: {transito['descripcion_breve']}
Palabras clave: {', '.join(transito['palabras_clave'])}

Arquetipo primario: {arquetipos['primario']}
Arquetipo secundario: {arquetipos['secundario']}
Emoción dominante: {arquetipos['emocion_dominante'].replace('_', ' ')}
Elemento: {arquetipos['elemento']} — Modalidad: {arquetipos['modalidad']}

Tono del guion: Educador empático, brújula lúcida, psicológico, cercano.
{efemerides_str}

=== REGLAS EDITORIALES DE TOMÁS (5 TOMAS EXACTAS - VISCERAL Y HUMANO) ===
1. TOMA 1 [gancho_fecha_continuidad] (15-20 palabras):
   Apertura directa interpelando al cuerpo, a la mente o a una situación humana concreta del día.
   PROHIBIDO frases gaseosas cósmicas ("el aire es denso y eléctrico", "la danza de los astros").
2. TOMA 2 [mecanica_psicologica] (16-20 palabras):
   Traduce la tensión psíquica real a lo cotidiano (vínculos, laburo, la mandíbula apretada, el mensaje que esquivás).
   PROHIBIDO moralizar o usar fórmulas enlatadas como "La trampa:". Toca la fibra de la experiencia humana.
3. TOMA 3 [mecanica_celeste_reloj2d] (16-20 palabras):
   Conexión orgánica con el Astrolabio / reloj en vivo. Nombra los planetas, grados exactos y el aspecto sin rigidez.
4. TOMA 4 [brujula_lucida] (16-20 palabras):
   El anclaje lúcido y maduro para transitar la energía sin desgaste reactivo ni autoengaño. Sé conciso y sobrio.
5. TOMA 5 [cta / cierre humano] (12-16 palabras):
   Cierre dúctil que genera conversación genuina o pausa reflexiva:
   - Pregunta directa al pecho para comentar ("¿Con quién estás peleando en serio hoy? Dejámelo abajo.")
   - Anclaje para guardar el video ("Guardate esto para cuando baje la espuma.")
   - Diagnóstico cercano de carta ("Fijate en qué casa tenés este signo o dejame tu signo y lo vemos.")
   PROHIBIDO rotundamente decir "andá a mi link", "link en bio" o sonar a vendedor barato.

=== FORMATO ESTRICTO ===
- Voseo rioplatense impecable ("mirá", "fijate", "registralo", "decidilo", "soltá", "bancate", "sentís").
- CERO tuteo neutro ("tú", "ti", "contigo").
- CERO dramatismo sensacionalista ("veneno", "destrucción", "abismo").
- Extensión total: ENTRE 75 Y 95 PALABRAS NETAS en todo el guion (locución ágil de ~30 a 33 segundos).
- Puntuación natural y fluida: usá comas, puntos seguidos y guiones. PROHIBIDAS las elipsis repetitivas (...).
{feedback_retry}

Devuelve ÚNICAMENTE un JSON válido con esta estructura:
{{
  "evento_id": "{EVENTO_ID}",
  "titulo": "{produccion['evento_titulo']}",
  "tomas": [
    {{"num": 1, "rol": "gancho_fecha_continuidad", "texto": "...", "etiqueta_visual": "[TITULO_PLANETA]"}},
    {{"num": 2, "rol": "mecanica_psicologica", "texto": "...", "etiqueta_visual": null}},
    {{"num": 3, "rol": "mecanica_celeste_reloj2d", "texto": "...", "etiqueta_visual": null}},
    {{"num": 4, "rol": "brujula_lucida", "texto": "...", "etiqueta_visual": null}},
    {{"num": 5, "rol": "cta", "texto": "...", "etiqueta_visual": "[CTA]"}}
  ]
}}
"""

        texto_raw = generar_con_gemini_cuota(prompt, CANDIDATE_MODELS)
        try:
            texto_limpio = limpiar_json_gemini(texto_raw)
            data_parsed = json.loads(texto_limpio)
            es_valido, motivo = validar_guion_editorial(data_parsed, num_tomas)
            if es_valido:
                guion_data = data_parsed
                ok("Guion validado editorialmente con éxito.")
                break
            else:
                warn(f"Intento {intento} rechazado: {motivo}")
                feedback_retry = f"\n⚠️ RECHAZO EN INTENTO ANTERIOR: {motivo}. Corrige esto estrictamente: respeta 65-78 palabras, voseo rioplatense y cero clichés."
        except Exception as e:
            warn(f"Error al decodificar JSON en intento {intento}: {e}")

    if not guion_data:
        err("No se pudo generar un guion que cumpla los estándares editoriales de Tomás tras 3 intentos.")
        sys.exit(1)

    # Mostrar preview
    log("\n📄 PREVIEW DEL GUION APROBADO:", CYAN)
    total_palabras = 0
    for toma in guion_data["tomas"]:
        palabras = len(toma["texto"].split())
        total_palabras += palabras
        log(f"  [{toma['num']}] {toma['rol'].upper()} ({palabras}p): {toma['texto']}", GRIS)
    log(f"  -> Total de palabras: {total_palabras} (Objetivo: 65-78)", VERDE)

    ruta = guardar_guion(guion_data)
    return str(ruta)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 2 — Guion Semanal / Resumen
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_2_guion_semanal():
    """
    Genera un guion de resumen semanal condensando los 7 tránsitos de la semana.
    Lee el ADN del evento semanal y genera una narrativa cohesiva.
    """
    log("\n📅 OPCIÓN 2 — Guion Semanal / Resumen", MAGENTA)

    role_text  = cargar_role_scriptwriter()
    produccion = ADN["produccion"]
    transito   = ADN["transito"]
    arquetipos = ADN["arquetipos"]

    # Para el semanal, 5 tomas (estructura condensada)
    estructura_semanal = [
        {"num": 1, "rol": "apertura_semanal",    "dur_max": 10, "instruccion": "Qué semana es, qué energía general domina. Frase de impacto."},
        {"num": 2, "rol": "transitos_principales","dur_max": 15, "instruccion": "Los 2-3 tránsitos más importantes de la semana y qué activan."},
        {"num": 3, "rol": "tension_oportunidad",  "dur_max": 12, "instruccion": "La tensión principal de la semana y la oportunidad que esconde."},
        {"num": 4, "rol": "consejo_semanal",      "dur_max": 12, "instruccion": "Una acción concreta o actitud para navegar bien esta semana."},
        {"num": 5, "rol": "cta_semanal",          "dur_max": 5,  "instruccion": "CTA: máximo 15 palabras. Invitar sutilmente a la web o link del perfil."},
    ]
    num_tomas = len(estructura_semanal)

    tomas_desc = ""
    for t in estructura_semanal:
        tomas_desc += f"\n  - Toma {t['num']} [{t['rol']}] (máx. {t['dur_max']}s): {t['instruccion']}"

    prompt = f"""
{role_text}

=== RESUMEN SEMANAL ===
Semana: {SEMANA}
Tránsito principal: {transito['planeta']} en {transito['signo_destino']}
Período: {produccion['fecha_publicacion']}
Planeta regente de la semana: {arquetipos['planeta_regente']} ({arquetipos['simbolo_regente']})
Emoción dominante: {arquetipos['emocion_dominante'].replace('_', ' ')}
Elemento: {arquetipos['elemento']}

=== ESTRUCTURA ({num_tomas} TOMAS) ==={tomas_desc}

=== INSTRUCCIÓN CRÍTICA ===
Devuelve ÚNICAMENTE este JSON sin texto adicional ni markdown:

{{
  "evento_id": "{EVENTO_ID}_semanal",
  "titulo": "Resumen Semanal — {SEMANA}",
  "tipo": "semanal",
  "tomas": [
    {{"num": 1, "rol": "apertura_semanal", "texto": "...", "etiqueta_visual": "[TITULO_SEMANA]"}},
    {{"num": 2, "rol": "transitos_principales", "texto": "...", "etiqueta_visual": null}},
    {{"num": 3, "rol": "tension_oportunidad", "texto": "...", "etiqueta_visual": null}},
    {{"num": 4, "rol": "consejo_semanal", "texto": "...", "etiqueta_visual": null}},
    {{"num": 5, "rol": "cta_semanal", "texto": "...", "etiqueta_visual": "[CTA]"}}
  ]
}}
"""

    info(f"Enviando prompt semanal a Gemini...")
    CANDIDATE_MODELS = ['gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'gemini-flash-latest']
    
    try:
        texto_raw = generar_con_gemini_cuota(prompt, CANDIDATE_MODELS)
        texto_limpio = limpiar_json_gemini(texto_raw)
        guion_data = json.loads(texto_limpio)

        if not validar_estructura_guion(guion_data, num_tomas):
            err("El guion semanal no pasó la validación.")
            sys.exit(1)

        log("\n📄 PREVIEW SEMANAL:", CYAN)
        for toma in guion_data["tomas"]:
            log(f"  [{toma['num']}] {toma['rol']}: {toma['texto'][:80]}...", GRIS)

        ruta = guardar_guion(guion_data, sufijo="_semanal")
        return str(ruta)

    except json.JSONDecodeError as e:
        err(f"Gemini no devolvió JSON válido: {e}")
        sys.exit(1)
    except Exception as e:
        err(f"Error: {e}")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 3 — Horóscopo Personalizado (contraste tránsito vs. carta natal)
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_3_horoscopo_personalizado(natal_path: str = None):
    """
    Genera un guion personalizado contrastando el tránsito activo con la carta natal real.
    Si no se pasa --natal, usa la carta natal de Tomás (alter-ego astrológico).
    ¡CERO datos mock! Usa la carta natal real y el EphemerisCalculator.
    """
    log("\n🌟 OPCIÓN 3 — Horóscopo Personalizado", MAGENTA)

    # Cargar carta natal
    if natal_path:
        natal_ruta = Path(natal_path)
        if not natal_ruta.exists():
            err(f"Carta natal no encontrada: {natal_path}")
            sys.exit(1)
        with open(natal_ruta, encoding="utf-8") as f:
            natal = json.load(f)
        info(f"Carta natal cargada: {natal_ruta.name}")
    else:
        natal = NATAL_DEFAULT
        info("Usando carta natal de Tomás (alter-ego astrológico por defecto)")

    # Calcular posiciones actuales con ephemeris real
    posiciones_actuales = calcular_posiciones_actuales()
    if not posiciones_actuales:
        warn("No se pudieron calcular efemérides en tiempo real. Usando datos del ADN.")

    role_text  = cargar_role_scriptwriter()
    transito   = ADN["transito"]
    arquetipos = ADN["arquetipos"]
    produccion = ADN["produccion"]

    # Construir descripción de la carta natal
    planetas_natal = natal.get("planetas", {})
    natal_str = f"Carta Natal de {natal.get('nombre', 'Usuario')} ({natal.get('fecha', '?')}):\n"
    for planeta, posicion in planetas_natal.items():
        natal_str += f"  {planeta}: {posicion}\n"

    # Construir efemérides actuales
    efemerides_str = f"\nTRÁNSITO ACTIVO ({produccion['fecha_publicacion']}):\n"
    efemerides_str += f"  {transito['planeta']} ingresa a {transito['signo_destino']}\n"
    if posiciones_actuales:
        efemerides_str += "\nPOSICIONES CALCULADAS HOY:\n"
        for p, g in posiciones_actuales.items():
            efemerides_str += f"  {p}: {g:.1f}°\n"

    # Estructura: 7 tomas personalizadas
    estructura = ADN["guion"]["estructura_tomas"]
    num_tomas  = len(estructura)
    tomas_desc = ""
    for t in estructura:
        tomas_desc += f"\n  - Toma {t['num']} [{t['rol']}] (máx. {t['duracion_max_segundos']}s): {t['instruccion']}"

    prompt = f"""
{role_text}

=== MODO: HORÓSCOPO PERSONALIZADO ===
Debes analizar RIGUROSAMENTE cómo el tránsito actual impacta específicamente en la carta natal
del usuario. No generes interpretaciones genéricas. Identifica qué casa natal activa el tránsito,
si forma aspectos con planetas natales (conjunción, oposición, cuadratura, trígono, sextil en un
orbe de 5°), y qué parte de la vida personal está siendo tocada.

{natal_str}
{efemerides_str}

Arquetipo dominante del tránsito: {arquetipos['primario']}
Elemento: {arquetipos['elemento']} — Emoción: {arquetipos['emocion_dominante'].replace('_', ' ')}

=== ESTRUCTURA PERSONAL ({num_tomas} TOMAS) ==={tomas_desc}

=== INSTRUCCIÓN CRÍTICA ===
Devuelve ÚNICAMENTE este JSON. Sin markdown, sin explicaciones:

{{
  "evento_id": "{EVENTO_ID}_personal",
  "titulo": "{produccion['evento_titulo']} — Para {natal.get('nombre', 'Ti')}",
  "tipo": "personalizado",
  "nombre_usuario": "{natal.get('nombre', 'Usuario')}",
  "aspectos_activados": ["lista de aspectos encontrados"],
  "tomas": [
    {{"num": 1, "rol": "gancho", "texto": "...", "etiqueta_visual": "[TITULO_PLANETA]"}},
    ... ({num_tomas} tomas en total)
  ]
}}
"""

    info("Enviando análisis personalizado a Gemini...")
    CANDIDATE_MODELS = ['gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'gemini-flash-latest']

    try:
        texto_raw = generar_con_gemini_cuota(prompt, CANDIDATE_MODELS)
        texto_limpio = limpiar_json_gemini(texto_raw)
        guion_data = json.loads(texto_limpio)

        if not validar_estructura_guion(guion_data, num_tomas):
            err("El guion personalizado no pasó la validación.")
            sys.exit(1)

        # Mostrar aspectos detectados
        if "aspectos_activados" in guion_data:
            info(f"Aspectos detectados: {', '.join(guion_data['aspectos_activados'])}")

        log("\n📄 PREVIEW PERSONAL:", CYAN)
        for toma in guion_data["tomas"]:
            log(f"  [{toma['num']}] {toma['rol']}: {toma['texto'][:80]}...", GRIS)

        sufijo = f"_personal_{natal.get('nombre', 'user').lower()}"
        ruta = guardar_guion(guion_data, sufijo=sufijo)
        return str(ruta)

    except json.JSONDecodeError as e:
        err(f"Gemini no devolvió JSON válido: {e}")
        sys.exit(1)
    except Exception as e:
        err(f"Error: {e}")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# OPCIÓN 4 — Inyector de CTA Dinámico
# ═══════════════════════════════════════════════════════════════════════════════

def opcion_4_inyectar_cta(guion_path: str = None):
    """
    Lee el guion_<evento>.json existente, genera un nuevo CTA para la Toma 7
    y lo reemplaza. El CTA nuevo siempre es < 5 segundos (~15 palabras máx).
    """
    log("\n📣 OPCIÓN 4 — Inyector de CTA Dinámico", MAGENTA)

    # Buscar guion existente
    if guion_path:
        ruta_guion = Path(guion_path)
    else:
        ruta_guion = GUIONES_DIR / f"guion_{EVENTO_ID}.json"

    if not ruta_guion.exists():
        err(f"Guion no encontrado: {ruta_guion}")
        err("Primero ejecuta --opcion 1 para generar el guion.")
        sys.exit(1)

    with open(ruta_guion, encoding="utf-8") as f:
        guion_data = json.load(f)

    tomas = guion_data.get("tomas", [])
    if not tomas:
        err("El guion no tiene tomas.")
        sys.exit(1)

    # Encontrar la toma de CTA (rol = "cta" o última toma)
    toma_cta = None
    idx_cta  = -1
    for i, t in enumerate(tomas):
        if t.get("rol") == "cta":
            toma_cta = t
            idx_cta  = i
            break
    if toma_cta is None:
        # Fallback: última toma
        idx_cta  = len(tomas) - 1
        toma_cta = tomas[idx_cta]
        warn(f"No se encontró toma con rol 'cta'. Usando toma {idx_cta+1} como fallback.")

    info(f"CTA actual (toma {toma_cta['num']}): {toma_cta['texto']}")

    # CTA directo aprobado por el usuario
    nuevo_cta = "Para ver en qué casa te cae este aspecto, entrá al link de mi perfil."
    
    palabras  = len(nuevo_cta.split())
    info(f"CTA seleccionado ({palabras} palabras): {nuevo_cta}")

    guion_data["tomas"][idx_cta]["texto"] = nuevo_cta
    guion_data["tomas"][idx_cta]["etiqueta_visual"] = "[CTA]"
    guion_data["_cta_inyectado"] = True
    guion_data["_cta_timestamp"] = datetime.datetime.now().isoformat()

    with open(ruta_guion, "w", encoding="utf-8") as f:
        json.dump(guion_data, f, ensure_ascii=False, indent=2)

    ok(f"CTA inyectado en {ruta_guion}")
    ok(f"Toma {toma_cta['num']}: \"{nuevo_cta}\"")
    return str(ruta_guion)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="🌒 Generador de Guiones V2 — Célula Madre 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Opciones disponibles:
  1  Guion diario (tránsito activo del ADN JSON)
  2  Guion semanal/resumen
  3  Horóscopo personalizado (carta natal vs tránsito)
  4  Inyectar CTA dinámico en la Toma 7 del guion existente
        """
    )
    parser.add_argument("--opcion", type=int, choices=[1, 2, 3, 4], required=True)
    parser.add_argument("--natal", type=str, default=None,
                        help="[Opción 3] Ruta al JSON de carta natal del usuario")
    parser.add_argument("--guion", type=str, default=None,
                        help="[Opción 4] Ruta al JSON de guion a modificar")
    args = parser.parse_args()

    log(f"\n{'═'*55}", MAGENTA)
    log(f"  🌒 GENERADOR DE GUIONES V2", MAGENTA)
    log(f"  ADN: {ADN['produccion']['evento_id']}", CYAN)
    log(f"  Evento: {ADN['produccion']['evento_titulo']}", CYAN)
    log(f"{'═'*55}", MAGENTA)

    if args.opcion == 1:
        opcion_1_guion_diario()
    elif args.opcion == 2:
        opcion_2_guion_semanal()
    elif args.opcion == 3:
        opcion_3_horoscopo_personalizado(args.natal)
    elif args.opcion == 4:
        opcion_4_inyectar_cta(args.guion)

if __name__ == "__main__":
    main()
