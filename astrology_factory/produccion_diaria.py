#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
produccion_diaria.py
─────────────────────────────────────────────────────────────────────────────
ORQUESTADOR CANÓNICO DE PRODUCCIÓN DIARIA — ASTROLOGY FACTORY V2

Este es el ÚNICO script maestro autorizado para producir videos diarios en
Astrology Factory. Está respaldado por la Regla Constitucional AGENTS.md
(Zero Ad-hoc Script Policy).

Pipeline End-to-End:
  1. Configuración de Contexto (contexto_astrologico.json) según fecha.
  2. Carga / Validación de Guion de Oro (ejemplos_oro_diarios.json / Guiones/).
  3. Célula 1: Síntesis Tomás Neural (+6%) + Whisper (.ass karaoke + timeline exacto).
  4. Célula 2: Nodriza Visual (selección DB-first anti-repetición 30 días + Reloj 2D).
  5. Célula 2: Validador de Ensamble (cálculo de slots gapless y tolerancias).
  6. Motor FFmpeg Single-Pass: content_factory/video_maker.py (diseño sonoro + ASS).
  7. Célula 4: Metadata y Despliegue a Bóveda + actualización de registro.

Uso:
  python produccion_diaria.py --fecha 2026-11-08
  python produccion_diaria.py --fecha 2026-11-07 --forzar
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

FACTORY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FACTORY_ROOT))

PYTHON_EXEC = FACTORY_ROOT / "venv" / "bin" / "python"
if not PYTHON_EXEC.exists():
    PYTHON_EXEC = Path(sys.executable)

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
REGISTRO_PATH = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"
EJEMPLOS_ORO_PATH = FACTORY_ROOT / "v2" / "celula_1" / "ejemplos_oro_diarios.json"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; BOLD = "\033[1m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")
def ok(msg): log(f"  ✅ {msg}", VERDE)
def info(msg): log(f"  ℹ️  {msg}", CYAN)
def warn(msg): log(f"  ⚠️  {msg}", AMARILLO)
def err(msg): log(f"  ❌ {msg}", ROJO)


def ejecutar_paso(cmd: list, descripcion: str, timeout: int = 300) -> bool:
    """Ejecuta un subproceso del pipeline e imprime el resultado."""
    info(f"Iniciando: {descripcion}...")
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        if proc.returncode != 0:
            err(f"Fallo en {descripcion} (Código {proc.returncode}):")
            if proc.stdout:
                print(proc.stdout[-800:])
            if proc.stderr:
                print(proc.stderr[-800:])
            return False
        ok(f"{descripcion} completado exitosamente.")
        return True
    except subprocess.TimeoutExpired:
        err(f"Timeout ({timeout}s) en {descripcion}.")
        return False
    except Exception as ex:
        err(f"Error inesperado en {descripcion}: {ex}")
        return False


def configurar_contexto(fecha_str: str) -> dict:
    """Actualiza contexto_astrologico.json para la fecha indicada con Swiss Ephemeris exacto."""
    info(f"Configurando ADN Astrológico para la fecha: {fecha_str}...")
    
    with open(ADN_PATH, "r", encoding="utf-8") as f:
        adn = json.load(f)

    # Buscar datos de la fecha en registro_publicaciones.json (solo si no es fallback Transito_Diario)
    pub_data = None
    if REGISTRO_PATH.exists():
        try:
            with open(REGISTRO_PATH, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
                candidate = reg.get("publicaciones", {}).get(fecha_str)
                if candidate and "Transito_Diario" not in candidate.get("evento_id", ""):
                    pub_data = candidate
        except Exception as e:
            warn(f"No se pudo leer registro_publicaciones: {e}")

    evento_id = f"{fecha_str}_Transito_Diario"
    evento_titulo = f"{fecha_str} | Tránsito Astrológico del Día"
    
    # Calcular efemérides exactas con Swiss Ephemeris
    try:
        from astrology_engine.clima_astral_engine import get_calc
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")
        dt_local = datetime(dt.year, dt.month, dt.day, 12, 0)
        calc = get_calc()
        carta = calc.calcular_carta("Tránsito Diario", dt_local, -34.6037, -58.3816, -3.0)

        cuerpos_personales = {"Sol", "Luna", "Mercurio", "Venus", "Marte"}
        cuerpos_todos = {"Sol", "Luna", "Mercurio", "Venus", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón"}

        aspectos_candidatos = []
        for a in carta.get("aspectos", []):
            c1, c2 = a["cuerpo1"], a["cuerpo2"]
            if (c1 in cuerpos_personales or c2 in cuerpos_personales) and c1 in cuerpos_todos and c2 in cuerpos_todos:
                aspectos_candidatos.append(a)

        # Priorizar aspectos que incluyan a la Luna si tienen orbe menor a 2.5° (el pulso diario)
        luna_aspectos = [a for a in aspectos_candidatos if ("Luna" in (a["cuerpo1"], a["cuerpo2"])) and a["orbe"] <= 2.5]
        if luna_aspectos:
            luna_aspectos.sort(key=lambda x: x["orbe"])
            aspecto_top = luna_aspectos[0]
        elif aspectos_candidatos:
            aspectos_candidatos.sort(key=lambda x: x["orbe"])
            aspecto_top = aspectos_candidatos[0]
        else:
            aspecto_top = carta["aspectos"][0]

        p1 = aspecto_top["cuerpo1"]
        p2 = aspecto_top["cuerpo2"]
        asp_tipo = aspecto_top["aspecto"]
        orbe = aspecto_top["orbe"]
        p1_info = carta["planetas"].get(p1, {})
        p2_info = carta["planetas"].get(p2, {})

        signo_1 = p1_info.get("signo", "Escorpio")
        signo_2 = p2_info.get("signo", "Escorpio")
        elem_1 = p1_info.get("elemento", "Agua")
        elem_2 = p2_info.get("elemento", "Agua")
        mod_1 = p1_info.get("modalidad", "Fijo")

        simbolos_planetas = {
            "Sol": "☉", "Luna": "☽", "Mercurio": "☿", "Venus": "♀",
            "Marte": "♂", "Júpiter": "♃", "Saturno": "♄", "Urano": "♅",
            "Neptuno": "♆", "Plutón": "♇", "Quirón": "⚷", "Lilith": "⚸"
        }
        simbolo_p1 = simbolos_planetas.get(p1, "☽")
        simbolo_p2 = simbolos_planetas.get(p2, "☿")

        evento_id_calc = f"{fecha_str}_{p1}_{asp_tipo}_{p2}_{signo_1}".replace(" ", "_").replace("ó", "o").replace("ú", "u").replace("í", "i")
        evento_titulo_calc = f"{fecha_str} | {p1} en {asp_tipo} con {p2} en {signo_1}"

        if not pub_data:
            evento_id = evento_id_calc
            evento_titulo = evento_titulo_calc
        else:
            evento_id = pub_data.get("evento_id", evento_id_calc)
            evento_titulo = pub_data.get("titulo", evento_titulo_calc)

        # Actualizar transito y arquetipos en el ADN para guionista y nodriza
        adn["transito"]["planeta"] = f"{p1} y {p2}"
        adn["transito"]["simbolo_planetario"] = f"{simbolo_p1} {simbolo_p2}"
        adn["transito"]["signo_destino"] = signo_1
        adn["transito"]["simbolo_signo"] = signo_1
        adn["transito"]["tipo_aspecto"] = f"{asp_tipo} (orbe {orbe:.2f}°)"
        adn["transito"]["intensidad"] = "muy alta" if orbe < 1.5 else "alta"
        adn["transito"]["fecha_exacta"] = fecha_str
        adn["transito"]["descripcion_breve"] = (
            f"El {fecha_str} la {p1} conecta con {p2} en {asp_tipo} a través de {signo_1} y {signo_2}. "
            f"Posiciones: {p1} en {p1_info.get('formato', signo_1)} y {p2} en {p2_info.get('formato', signo_2)}."
        )
        adn["transito"]["palabras_clave"] = [
            p1.lower(), p2.lower(), signo_1.lower(), signo_2.lower(),
            asp_tipo.lower(), elem_1.lower(), "astrolabio", "revelacion", "soberania"
        ]

        elem_final = elem_1 if elem_1 == elem_2 else f"{elem_1}/{elem_2}"
        adn["arquetipos"]["primario"] = f"La Tensión {p1}-{p2} en {signo_1}"
        adn["arquetipos"]["secundario"] = f"El Despliegue de {elem_final}"
        adn["arquetipos"]["sombra"] = "La Reactividad Inconsciente"
        adn["arquetipos"]["emocion_dominante"] = f"claridad y verdad sobre {signo_1.lower()}"
        adn["arquetipos"]["elemento"] = elem_final
        adn["arquetipos"]["modalidad"] = mod_1
        adn["arquetipos"]["planeta_regente"] = p2
        adn["arquetipos"]["simbolo_regente"] = simbolo_p2

        # Alinear con Guión de Oro o Registro si está pre-definido
        titulo_ref = (pub_data.get("titulo", "") if pub_data else "") + " " + evento_titulo
        if "Venus" in titulo_ref and "Marte" in titulo_ref:
            adn["transito"]["planeta"] = "Venus y Marte"
            adn["transito"]["simbolo_planetario"] = "♀ ♂"
            adn["transito"]["signo_destino"] = "Libra"
            adn["transito"]["simbolo_signo"] = "Libra"
            adn["transito"]["tipo_aspecto"] = "Oposición"
            adn["transito"]["intensidad"] = "muy alta"
            adn["transito"]["descripcion_breve"] = "Venus en Libra se opone a Marte en Leo: el eje vincular y la charla que nadie quiere empezar."
            adn["transito"]["palabras_clave"] = ["venus", "marte", "libra", "leo", "oposicion", "vinculos", "pareja", "astrolabio"]
            adn["arquetipos"]["primario"] = "La Tensión Vincular Venus-Marte"
            adn["arquetipos"]["secundario"] = "El Espejo y la Balanza"
            adn["arquetipos"]["sombra"] = "El Orgullo que no Cede"
            adn["arquetipos"]["emocion_dominante"] = "claridad y verdad sobre los vínculos"

    except Exception as e:
        warn(f"Cálculo de Swiss Ephemeris con fallback: {e}")
        if pub_data:
            evento_id = pub_data.get("evento_id", evento_id)
            evento_titulo = pub_data.get("titulo", evento_titulo)

    adn["produccion"]["fecha_publicacion"] = fecha_str
    adn["produccion"]["evento_id"] = evento_id
    adn["produccion"]["evento_titulo"] = evento_titulo
    adn["audio"]["voz_tts"]["voz"] = "es-AR-TomasNeural"
    adn["audio"]["voz_tts"]["velocidad"] = "+6%"

    with open(ADN_PATH, "w", encoding="utf-8") as f:
        json.dump(adn, f, indent=2, ensure_ascii=False)

    ok(f"ADN actualizado: ID={evento_id} · Título='{evento_titulo}'")
    return adn


def resolver_guion(adn: dict, fecha_str: str, guion_id_forzado: str = None, forzar: bool = False) -> Path:
    """Asegura que el guion esté listo en la Bóveda."""
    evento_id = adn["produccion"]["evento_id"]
    guiones_dir = Path(adn["assets"]["paths"]["guiones"])
    guiones_dir.mkdir(parents=True, exist_ok=True)
    
    guion_path = guiones_dir / f"guion_{evento_id}.json"
    if guion_path.exists() and not forzar:
        try:
            with open(guion_path, "r", encoding="utf-8") as gf:
                g_existente = json.load(gf)
            actualizado = False
            for t_ex in g_existente.get("tomas", []):
                if "locucion" in t_ex and not t_ex.get("texto"):
                    t_ex["texto"] = t_ex["locucion"]
                    actualizado = True
                if t_ex.get("num") == 1 and not t_ex.get("etiqueta_visual"):
                    t_ex["etiqueta_visual"] = "[TITULO_PLANETA]"
                    actualizado = True
                elif t_ex.get("num") == 5 and not t_ex.get("etiqueta_visual"):
                    t_ex["etiqueta_visual"] = "[CTA]"
                    actualizado = True
            if actualizado:
                with open(guion_path, "w", encoding="utf-8") as gf:
                    json.dump(g_existente, gf, indent=2, ensure_ascii=False)

            transito_existente = g_existente.get("transito", "")
            if "Venus" in transito_existente and "Marte" in transito_existente:
                adn["transito"]["planeta"] = "Venus y Marte"
                adn["transito"]["simbolo_planetario"] = "♀ ♂"
                adn["transito"]["signo_destino"] = "Libra"
                adn["transito"]["simbolo_signo"] = "Libra"
                adn["transito"]["tipo_aspecto"] = "Oposición"
                adn["transito"]["intensidad"] = "muy alta"
                adn["transito"]["descripcion_breve"] = "Venus en Libra se opone a Marte en Leo: el eje vincular y la charla que nadie quiere empezar."
                adn["transito"]["palabras_clave"] = ["venus", "marte", "libra", "leo", "oposicion", "vinculos", "pareja", "astrolabio"]
                adn["arquetipos"]["primario"] = "La Tensión Vincular Venus-Marte"
                adn["arquetipos"]["secundario"] = "El Espejo y la Balanza"
                adn["arquetipos"]["sombra"] = "El Orgullo que no Cede"
                adn["arquetipos"]["emocion_dominante"] = "claridad y verdad sobre los vínculos"
                with open(ADN_PATH, "w", encoding="utf-8") as af:
                    json.dump(adn, af, indent=2, ensure_ascii=False)
        except Exception:
            pass
        ok(f"Guion existente detectado: {guion_path.name}")
        return guion_path

    # Buscar en ejemplos_oro_diarios.json
    if EJEMPLOS_ORO_PATH.exists():
        try:
            with open(EJEMPLOS_ORO_PATH, "r", encoding="utf-8") as f:
                oro_data = json.load(f)
            
            guion_candidato = None
            for g in oro_data.get("guiones", []):
                if guion_id_forzado and g.get("id") == guion_id_forzado:
                    guion_candidato = g
                    break
                if g.get("fecha") == fecha_str:
                    guion_candidato = g
                    break

            if guion_candidato:
                info(f"Cargando Guion de Oro ({guion_candidato.get('id', 'ORO')})...")
                guion_candidato["evento_id"] = evento_id
                guion_candidato["fecha"] = fecha_str
                for t_oro in guion_candidato.get("tomas", []):
                    if "locucion" in t_oro and not t_oro.get("texto"):
                        t_oro["texto"] = t_oro["locucion"]
                    if t_oro.get("num") == 1 and not t_oro.get("etiqueta_visual"):
                        t_oro["etiqueta_visual"] = "[TITULO_PLANETA]"
                    elif t_oro.get("num") == 5 and not t_oro.get("etiqueta_visual"):
                        t_oro["etiqueta_visual"] = "[CTA]"
                with open(guion_path, "w", encoding="utf-8") as gf:
                    json.dump(guion_candidato, gf, indent=2, ensure_ascii=False)

                transito_cand = guion_candidato.get("transito", "")
                if "Venus" in transito_cand and "Marte" in transito_cand:
                    adn["transito"]["planeta"] = "Venus y Marte"
                    adn["transito"]["simbolo_planetario"] = "♀ ♂"
                    adn["transito"]["signo_destino"] = "Libra"
                    adn["transito"]["simbolo_signo"] = "Libra"
                    adn["transito"]["tipo_aspecto"] = "Oposición"
                    adn["transito"]["intensidad"] = "muy alta"
                    adn["transito"]["descripcion_breve"] = "Venus en Libra se opone a Marte en Leo: el eje vincular y la charla que nadie quiere empezar."
                    adn["transito"]["palabras_clave"] = ["venus", "marte", "libra", "leo", "oposicion", "vinculos", "pareja", "astrolabio"]
                    adn["arquetipos"]["primario"] = "La Tensión Vincular Venus-Marte"
                    adn["arquetipos"]["secundario"] = "El Espejo y la Balanza"
                    adn["arquetipos"]["sombra"] = "El Orgullo que no Cede"
                    adn["arquetipos"]["emocion_dominante"] = "claridad y verdad sobre los vínculos"
                    with open(ADN_PATH, "w", encoding="utf-8") as af:
                        json.dump(adn, af, indent=2, ensure_ascii=False)

                ok(f"Guion de Oro desplegado a: {guion_path.name}")
                return guion_path
        except Exception as e:
            warn(f"Error al leer ejemplos_oro_diarios.json: {e}")

    # Si no existe, invocar generador de guiones V2
    info("Generando guion con Célula 1...")
    gen_cmd = [
        str(PYTHON_EXEC),
        str(FACTORY_ROOT / "v2" / "celula_1" / "generador_guiones.py"),
        "--opcion", "1"
    ]
    if ejecutar_paso(gen_cmd, "Generador de Guiones V2"):
        if guion_path.exists():
            return guion_path

    raise FileNotFoundError(f"No se pudo resolver el guion para {evento_id} en {guion_path}")


def main():
    parser = argparse.ArgumentParser(description="Orquestador Canónico de Producción Diaria V2")
    parser.add_argument("--fecha", required=True, help="Fecha de publicación (AAAA-MM-DD)")
    parser.add_argument("--guion-id", default=None, help="ID de Guion de Oro opcional (ej: ORO_4)")
    parser.add_argument("--forzar", action="store_true", help="Forzar re-ejecución completa")
    args = parser.parse_args()

    fecha_str = args.fecha

    print(f"\n{BOLD}{MAGENTA}╔════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{MAGENTA}║      ASTROLOGY FACTORY V2 — ORQUESTADOR CANÓNICO DIARIO       ║{RESET}")
    print(f"{BOLD}{MAGENTA}║      Gobernado por AGENTS.md (Regla Zero Script Policy)       ║{RESET}")
    print(f"{BOLD}{MAGENTA}╚════════════════════════════════════════════════════════════════╝{RESET}\n")

    # 1. Configurar contexto
    adn = configurar_contexto(fecha_str)
    evento_id = adn["produccion"]["evento_id"]

    # 2. Resolver Guion
    guion_path = resolver_guion(adn, fecha_str, args.guion_id, args.forzar)

    # 3. Célula 1: Síntesis TTS y Timeline Matemático
    mp3_maestro = Path(adn["assets"]["paths"]["audio_master"]) / f"{evento_id}.mp3"
    timeline_maestro = Path(adn["assets"]["paths"]["timeline_huecos"]) / f"{evento_id}.json"
    ass_maestro = Path(adn["assets"]["paths"]["subtitulos"]) / f"{evento_id}.ass"

    if mp3_maestro.exists() and timeline_maestro.exists() and not getattr(args, 'forzar_tts', False):
        ok(f"Audio y Timeline ya existen ({mp3_maestro.name}). Reutilizando...")
    else:
        info("Lanzando Célula 1: Síntesis Neural Tomás (+6%) y Mapeo...")
        c1_cmd = [
            str(PYTHON_EXEC),
            str(FACTORY_ROOT / "v2" / "celula_1" / "cronometrador_y_tts.py"),
            "--opcion", "1",
            "--guion", str(guion_path)
        ]
        if not ejecutar_paso(c1_cmd, "Célula 1: TTS y Mapeo", timeout=180):
            sys.exit(1)

    # 3b. Célula 1: Subtítulos Karaoke ASS con Whisper
    if ass_maestro.exists() and not getattr(args, 'forzar_tts', False):
        ok(f"Subtítulos ASS ya existen ({ass_maestro.name}). Reutilizando...")
    else:
        info("Lanzando Célula 1: Generación de Subtítulos ASS con Whisper...")
        ass_cmd = [
            str(PYTHON_EXEC),
            str(FACTORY_ROOT / "v2" / "celula_1" / "cronometrador_y_tts.py"),
            "--opcion", "2",
            "--guion", str(guion_path)
        ]
        ejecutar_paso(ass_cmd, "Célula 1: Subtítulos ASS Karaoke", timeout=300)

    # 4. Célula 2: Nodriza Visual (Selección Semántica DB-First)
    info("Lanzando Célula 2: Nodriza Visual (Filtro anti-repetición 30 días)...")
    if args.forzar:
        reloj_viejo = FACTORY_ROOT / "produccion" / "clips_reloj_2d" / f"reloj_2d_{fecha_str}.mp4"
        if reloj_viejo.exists():
            try:
                reloj_viejo.unlink()
                info(f"Clip previo de reloj eliminado para regeneración forzada: {reloj_viejo.name}")
            except Exception:
                pass
        mixed_viejo = Path(adn["assets"]["paths"]["audio_master"]) / f"{evento_id}_mixed.mp3"
        if mixed_viejo.exists():
            try:
                mixed_viejo.unlink()
                info(f"Audio mixto previo eliminado para regeneración de frecuencias Solfeggio: {mixed_viejo.name}")
            except Exception:
                pass
        final_cand = Path(adn["assets"]["paths"]["videos_finales"]) / adn["produccion"]["semana_prefijo"] / f"FINAL_{evento_id}.mp4"
        boveda_dest = Path("/home/tomas2/Desktop/Boveda_Astrologia/Videos_Finales/Nov_W1") / f"FINAL_{evento_id}.mp4"
        for f_del in [final_cand, boveda_dest]:
            if f_del.exists():
                try:
                    f_del.unlink()
                    info(f"Video final previo eliminado para forzar render fresco: {f_del.name}")
                except Exception:
                    pass
    nodriza_cmd = [
        str(PYTHON_EXEC),
        str(FACTORY_ROOT / "v2" / "celula_2" / "nodriza_visual.py")
    ]
    if args.forzar:
        nodriza_cmd.append("--forzar")
    if not ejecutar_paso(nodriza_cmd, "Célula 2: Nodriza Visual"):
        sys.exit(1)

    # 5. Célula 2: Validador de Ensamble (Slots Gapless)
    info("Lanzando Célula 2: Validador de Ensamble (Cálculo de tolerancia)...")
    validador_cmd = [
        str(PYTHON_EXEC),
        str(FACTORY_ROOT / "v2" / "celula_2" / "validador_de_ensamble.py"),
        "--opcion", "3"
    ]
    if not ejecutar_paso(validador_cmd, "Célula 2: Validador de Ensamble"):
        sys.exit(1)

    # 6. Motor FFmpeg Single-Pass: video_maker.py
    info("Lanzando Motor de Renderizado FFmpeg Single-Pass...")
    maker_cmd = [
        str(PYTHON_EXEC),
        str(FACTORY_ROOT / "content_factory" / "video_maker.py"),
        evento_id
    ]
    if not ejecutar_paso(maker_cmd, "Motor FFmpeg Single-Pass", timeout=600):
        sys.exit(1)

    # 6b. Quality Gate Industrial: Validación Automática Estricta
    info("Lanzando Quality Gate Industrial (Validación Matemática y Editorial)...")
    vault_final_cand = Path(adn["assets"]["paths"]["videos_finales"]) / adn["produccion"]["semana_prefijo"] / f"FINAL_{evento_id}.mp4"
    timeline_path = Path(adn["assets"]["paths"]["timeline_huecos"]) / f"{evento_id}.json"
    corte_validada_path = Path(adn["assets"]["paths"]["temp"]) / f"lista_de_corte_validada_{evento_id}.json"

    from v2.auditor_calidad_industrial import auditar_entrega
    if not auditar_entrega(evento_id, vault_final_cand, timeline_path, corte_validada_path):
        err("El video NO superó el Quality Gate Industrial. Producción abortada sin publicar.")
        sys.exit(1)
    ok("Video certificado por el Quality Gate Industrial.")

    # 7. Post-producción: Despliegue y Registro
    info("Organizando master final en Bóveda y actualizando registros...")
    boveda_dest_dir = Path("/home/tomas2/Desktop/Boveda_Astrologia/Videos_Finales/Nov_W1")
    boveda_dest_dir.mkdir(parents=True, exist_ok=True)
    semana_dest_dir = FACTORY_ROOT / "produccion" / "semana_02nov_08nov"
    semana_dest_dir.mkdir(parents=True, exist_ok=True)

    final_name = f"FINAL_{evento_id}.mp4"
    dest_boveda = boveda_dest_dir / final_name
    dest_semana = semana_dest_dir / final_name

    videos_completos = FACTORY_ROOT / "produccion" / "videos_completos"
    master_candidatos = list(videos_completos.glob(f"*{evento_id}*.mp4"))
    vault_final_cand = Path(adn["assets"]["paths"]["videos_finales"]) / adn["produccion"]["semana_prefijo"] / final_name

    def copiar_seguro(src: Path, dst: Path):
        try:
            if src.resolve() != dst.resolve():
                shutil.copy(src, dst)
        except Exception:
            pass

    if vault_final_cand.exists():
        master_final_path = vault_final_cand
        copiar_seguro(master_final_path, dest_boveda)
        copiar_seguro(master_final_path, dest_semana)
        ok(f"Master actualizado en Bóveda Desktop: {dest_boveda}")
        ok(f"Master copiado a Semana: {dest_semana}")
    elif dest_boveda.exists():
        master_final_path = dest_boveda
        copiar_seguro(dest_boveda, dest_semana)
        ok(f"Master verificado en Bóveda: {dest_boveda}")
        ok(f"Master copiado a Semana: {dest_semana}")
    elif master_candidatos:
        master_final_path = master_candidatos[0]
        copiar_seguro(master_final_path, dest_boveda)
        copiar_seguro(master_final_path, dest_semana)
        ok(f"Master copiado a Bóveda: {dest_boveda}")
        ok(f"Master copiado a Semana: {dest_semana}")
    else:
        master_final_path = None

    # Actualizar registro_publicaciones.json
    if REGISTRO_PATH.exists() and master_final_path:
        try:
            with open(REGISTRO_PATH, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
            if "publicaciones" not in reg:
                reg["publicaciones"] = {}
            
            entry = reg["publicaciones"].get(fecha_str, {})
            entry["evento_id"] = evento_id
            entry["titulo"] = adn["produccion"]["evento_titulo"]
            entry["fecha_publicacion"] = fecha_str
            entry["video_generado"] = True
            entry["path_video"] = str(semana_dest_dir / f"FINAL_{evento_id}.mp4")
            entry["estado_render"] = "COMPLETADO"
            entry["notas"] = "Producido automáticamente por produccion_diaria.py (Pipeline V2)"
            reg["publicaciones"][fecha_str] = entry

            with open(REGISTRO_PATH, "w", encoding="utf-8") as wf:
                json.dump(reg, wf, indent=2, ensure_ascii=False)
            ok("registro_publicaciones.json actualizado con estado COMPLETADO.")
        except Exception as e:
            warn(f"Error al actualizar registro_publicaciones: {e}")

    # 8. Célula 4: Metadata Social
    info("Generando metadata social (Célula 4)...")
    meta_cmd = [
        str(PYTHON_EXEC),
        str(FACTORY_ROOT / "v2" / "celula_4" / "generador_metadata.py")
    ]
    ejecutar_paso(meta_cmd, "Célula 4: Generador de Metadata")

    print(f"\n{BOLD}{VERDE}╔════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{VERDE}║   PRODUCCIÓN EXITOSA — VIDEO DEL {fecha_str} LISTO EN BÓVEDA     ║{RESET}")
    print(f"{BOLD}{VERDE}╚════════════════════════════════════════════════════════════════╝{RESET}\n")


if __name__ == "__main__":
    main()

