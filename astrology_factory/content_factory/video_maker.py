"""
video_maker.py — v5 · FFmpeg Builder (Single-Pass)
──────────────────────────────────────────────────
Este script ya NO decide nada. Es un constructor de comandos FFmpeg.

  ÚNICO input de contenido : <paths.temp>/lista_de_corte_validada_<evento_id>.json
                             (producido por v2/celula_2/validador_de_ensamble.py --opcion 3)
  Rutas / render / aspecto : contexto_astrologico.json (nada hardcodeado)

Eliminado respecto a v4 (ahora es trabajo de la Célula 2 / db_visual):
  • glob / lectura directa de directorios de la bóveda
  • score_file_v2, PHRASE_TO_ARCHETYPE, transit_palettes.json, storyboard.txt, guion.txt
  • inferencia de energía/aspecto desde texto (el aspecto sale de ADN["transito"]["tipo_aspecto"])
  • símbolo watermark y movimiento "inteligente" deducidos del texto de la escena
  • historial de uso de assets (lo lleva nodriza_visual.py)
  • render en 2 pasadas con clips .mkv temporales (temp_clips/) y copia posterior a la bóveda

SINGLE-PASS: un solo `ffmpeg` con un único filter_complex:
  cada corte → [scale/crop | zoompan al vuelo si es JPG/PNG] → grading → xfade encadenado
  → subtítulos ASS quemados una sola vez → mux con el audio.
  Cero escrituras intermedias a disco.

Compatibilidad de imports (verificada, regla 3):
  • subtitle_generator.py importa solo os / json / whisper  → no depende de nada de este módulo.
  • audio_mixer.py importa solo os / subprocess / json       → no depende de nada de este módulo.
  • Ambos se importan como módulos hermanos, por eso se conserva `sys.path.append(<este directorio>)`.
  • glob, shutil, datetime/timedelta y _json_hist eran de uso EXCLUSIVO de este archivo
    (selección de assets, historial, copia a bóveda) y se purgaron junto con esa lógica.

RUNBOOK: el entry-point sigue siendo `python content_factory/video_maker.py [Nombre_Evento]`.
Sin argumento usa ADN["produccion"]["evento_id"].
"""

import json
import os
import subprocess
import sys
from pathlib import Path

CONTENT_FACTORY_DIR = Path(__file__).resolve().parent
FACTORY_ROOT        = CONTENT_FACTORY_DIR.parent
ADN_PATH            = FACTORY_ROOT / "contexto_astrologico.json"
PALETTES_PATH       = CONTENT_FACTORY_DIR / "astrology_palettes.json"

FORMATOS_IMG = {".jpg", ".jpeg", ".png"}

# ── Parámetros del Builder (no son rutas; las rutas viven en el ADN) ─────────
XFADE_DUR_DEFAULT = 0.40   # se sobreescribe con ADN["render"]["xfade_duracion_s"] si existe
SUPERSAMPLE       = 2      # las imágenes se amplían ×2 antes del zoompan (evita el "jitter" por redondeo)
ZOOM_BASE         = 1.08   # zoom máximo Ken Burns para imágenes normales
ZOOM_ICONICA      = 1.14   # zoom máximo para imágenes icónicas (tarot, signos, símbolos…)
MIN_FRAMES_IMG    = 2

# Transiciones xfade que FFmpeg 7.x acepta. Cualquier otra → "fade".
XFADE_VALIDAS = {
    "fade", "fadeblack", "fadewhite", "fadegrays", "dissolve", "distance", "pixelize",
    "radial", "circleopen", "circleclose", "vertopen", "vertclose", "horzopen", "horzclose",
    "wipeleft", "wiperight", "wipeup", "wipedown", "slideleft", "slideright", "slideup",
    "slidedown", "smoothleft", "smoothright", "smoothup", "smoothdown",
    "diagtl", "diagtr", "diagbl", "diagbr", "hlslice", "hrslice", "vuslice", "vdslice",
    "hblur", "zoomin",
}
XFADE_FALLBACK = "fade"


# ─────────────────────────────────────────────────────────────────────────────
# Configuración (ADN) y helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cargar_adn() -> dict:
    with open(ADN_PATH, encoding="utf-8") as f:
        return json.load(f)


def _configuracion(adn: dict) -> dict:
    render = adn["render"]
    w, h = (int(x) for x in render["resolucion"].split("x"))
    paths = adn["assets"]["paths"]
    return {
        "W": w,
        "H": h,
        "FPS": int(render["fps"]),
        "CRF": int(render.get("crf", 20)),
        "PRESET": render.get("ffmpeg_preset", "fast"),
        "XFADE": float(render.get("xfade_duracion_s", XFADE_DUR_DEFAULT)),
        "TEMP_DIR": Path(paths["temp"]),
        "AUDIO_DIR": Path(paths["audio_master"]),
        "SUB_DIR": Path(paths["subtitulos"]),
        "FINAL_DIR": Path(paths["videos_finales"]),
        "SEMANA": adn["produccion"]["semana_prefijo"],
        "ASPECTO": str(adn.get("transito", {}).get("tipo_aspecto", "")).lower(),
        "COLOR_GRADE": render.get("color_grade", {}),
    }


def _ffprobe_duracion(path: Path) -> float | None:
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    try:
        d = float(r.stdout.strip())
        return d if d > 0 else None
    except ValueError:
        return None


def _escape_filter(path: str) -> str:
    return path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def _es_imagen(path: str) -> bool:
    return Path(path).suffix.lower() in FORMATOS_IMG


def _xfade_valida(nombre: str | None) -> str:
    return nombre if nombre in XFADE_VALIDAS else XFADE_FALLBACK


# ─────────────────────────────────────────────────────────────────────────────
# Color grading (declarado, no inferido)
# ─────────────────────────────────────────────────────────────────────────────

def _filtro_grading(cfg: dict) -> str:
    """
    Prioridad: grading del aspecto declarado en el ADN (astrology_palettes.json) →
    color_grade del ADN render. Viñeta solo si ADN render.color_grade.vignette es true.
    """
    vf = None
    if PALETTES_PATH.exists():
        with open(PALETTES_PATH, "r", encoding="utf-8") as f:
            palettes = json.load(f)
        vf = palettes.get(cfg["ASPECTO"], {}).get("grading_vf")

    cg = cfg["COLOR_GRADE"]
    if not vf:
        vf = (f"eq=brightness={cg.get('brillo', 0.0):.3f}:contrast={cg.get('contraste', 1.0):.3f}"
              f":saturation={cg.get('saturacion', 1.0):.3f}:gamma={cg.get('gamma', 1.0):.3f}")
    if cg.get("vignette", False):
        vf += ",vignette=angle=PI/4"
    return vf


# ─────────────────────────────────────────────────────────────────────────────
# Lectura y validación de la lista de corte validada
# ─────────────────────────────────────────────────────────────────────────────

def _cargar_lista_validada(cfg: dict, evento: str) -> dict | None:
    ruta = cfg["TEMP_DIR"] / f"lista_de_corte_validada_{evento}.json"
    if not ruta.exists():
        print(f"❌ No existe {ruta}")
        print("   Ejecuta primero: nodriza_visual.py --opcion 1 → validador_de_ensamble.py --opcion 3")
        return None
    with open(ruta, encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("validado"):
        print(f"❌ {ruta.name} no está marcada como validada.")
        return None
    if data.get("bloqueado_anti_spam"):
        print("🚨 La lista de corte está BLOQUEADA por la regla anti-spam del validador. Edita la asignación.")
        return None
    if not data.get("tomas"):
        print(f"❌ {ruta.name} no contiene tomas.")
        return None
    return data


def _cortes_de_toma(toma: dict) -> list[dict]:
    """Cortes explícitos de la toma; si el JSON no trae 'cortes', un único corte con archivo_video."""
    cortes = toma.get("cortes")
    if cortes:
        return cortes
    if toma.get("archivo_video"):
        return [{
            "archivo": toma["archivo_video"],
            "duracion_s": float(toma.get("duracion_s") or toma.get("duracion_ms", 0) / 1000.0),
            "transicion_entrada": toma.get("transicion_entrada"),
            "es_iconica": False,
            "reverse": False,
        }]
    return []


def _planificar_slots(tomas: list[dict], dur_audio: float | None) -> list[dict] | None:
    """
    Aplana tomas → cortes y fija la duración de cada slot para que la línea de tiempo
    sea GAPLESS y coincida con el audio:
      · la 1ª toma arranca en 0; cada toma termina donde empieza la siguiente
      · la última toma se estira hasta la duración del audio (si es mayor)
      · las duraciones de los cortes se reescalan para sumar exactamente el hueco de su toma
    """
    tomas = sorted(tomas, key=lambda t: (t.get("inicio_ms", 0), t.get("num_toma", 0)))
    slots = []
    for k, toma in enumerate(tomas):
        cortes = _cortes_de_toma(toma)
        if not cortes:
            print(f"❌ Toma {toma.get('num_toma', k + 1)} sin cortes ni archivo_video.")
            return None

        inicio = 0.0 if k == 0 else toma["inicio_ms"] / 1000.0
        if k < len(tomas) - 1:
            fin = tomas[k + 1]["inicio_ms"] / 1000.0
        else:
            fin = max(toma["fin_ms"] / 1000.0, dur_audio or 0.0)
        objetivo = fin - inicio

        suma = sum(float(c.get("duracion_s", 0)) for c in cortes)
        if objetivo <= 0 or suma <= 0:
            print(f"❌ Toma {toma.get('num_toma', k + 1)}: duración inválida (hueco={objetivo:.3f}s, cortes={suma:.3f}s).")
            return None

        factor = objetivo / suma
        durs = [float(c["duracion_s"]) * factor for c in cortes]
        durs[-1] = objetivo - sum(durs[:-1])   # el último absorbe el residuo → suma exacta

        for j, (c, d) in enumerate(zip(cortes, durs)):
            slots.append({
                "toma": toma.get("num_toma", k + 1),
                "archivo": c["archivo"],
                "dur": d,
                "es_imagen": _es_imagen(c["archivo"]),
                "es_iconica": bool(c.get("es_iconica", False)),
                "reverse": bool(c.get("reverse", False)),
                "transicion": None if not slots else _xfade_valida(
                    c.get("transicion_entrada") or (toma.get("transicion_entrada") if j == 0 else None)
                ),
            })
    return slots


# ─────────────────────────────────────────────────────────────────────────────
# Audio y subtítulos (rutas del ADN)
# ─────────────────────────────────────────────────────────────────────────────

def _resolver_audio(cfg: dict, evento: str, aspecto: str, tomas: list[dict]) -> Path | None:
    """
    Mejor audio ya mezclado por la Célula 3: _sfx > _binaural > _mix.
    Si solo existe la narración cruda, se aplica el diseño sonoro legado (audio_mixer).
    """
    for sufijo in ("_sfx", "_binaural", "_mix"):
        p = cfg["AUDIO_DIR"] / f"{evento}{sufijo}.mp3"
        if p.exists():
            print(f"🔊 Audio: {p.name}")
            return p

    raw = cfg["AUDIO_DIR"] / f"{evento}.mp3"
    if not raw.exists():
        print(f"❌ No se encontró audio para '{evento}' en {cfg['AUDIO_DIR']}")
        return None

    if str(CONTENT_FACTORY_DIR) not in sys.path:
        sys.path.append(str(CONTENT_FACTORY_DIR))
    from audio_mixer import mix_frequency_layer
    guion_text = " ".join(t.get("texto", "") for t in tomas).strip()
    words_json = str(raw).replace(".mp3", "_words.json")
    return Path(mix_frequency_layer(str(raw), guion_text, words_json, aspecto, []))


def _resolver_ass(cfg: dict, evento: str) -> Path | None:
    ass = cfg["SUB_DIR"] / f"{evento}.ass"
    if ass.exists():
        print(f"💾 Subtítulos ASS: {ass.name}")
        return ass

    narracion = cfg["AUDIO_DIR"] / f"{evento}.mp3"
    if not narracion.exists():
        print("⚠️  Sin ASS ni narración cruda para transcribir. Se renderiza sin subtítulos.")
        return None

    if str(CONTENT_FACTORY_DIR) not in sys.path:
        sys.path.append(str(CONTENT_FACTORY_DIR))
    from subtitle_generator import generate_ass
    print("📝 Generando subtítulos con Whisper...")
    try:
        return Path(generate_ass(str(narracion), modelo="small",
                                 video_width=cfg["W"], video_height=cfg["H"]))
    except Exception as e:
        print(f"⚠️  Whisper falló ({e}). Sin subtítulos.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Constructor del filter_complex (Single-Pass)
# ─────────────────────────────────────────────────────────────────────────────

def _cadena_post(cfg: dict, grading: str) -> str:
    # `fps` va ÚLTIMO: setpts deja el frame rate indefinido (1/0) y xfade exige CFR en ambas entradas.
    return f"{grading},format=yuv420p,setsar=1,setpts=PTS-STARTPTS,fps={cfg['FPS']}"


def _cadena_imagen(i: int, slot: dict, largo: float, cfg: dict, grading: str) -> str:
    """
    TRANSMUTACIÓN DINÁMICA: JPG/PNG → clip con Ken Burns (zoompan) al vuelo, sin archivo intermedio.
    La imagen entra como UN solo frame (sin -loop); zoompan genera los `frames` de salida.
    Zoom determinista por número de frame de salida (`on`): alterna zoom-in / zoom-out por índice.
    """
    W, H, FPS = cfg["W"], cfg["H"], cfg["FPS"]
    frames = max(MIN_FRAMES_IMG, round(largo * FPS))
    sw, sh = W * SUPERSAMPLE, H * SUPERSAMPLE
    zmax = ZOOM_ICONICA if slot["es_iconica"] else ZOOM_BASE
    dz = zmax - 1.0
    z = f"1+{dz:.4f}*on/{frames}" if i % 2 == 0 else f"{zmax:.4f}-{dz:.4f}*on/{frames}"
    return (
        f"[{i}:v]scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},"
        f"setsar=1,format=yuv420p,"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
        f"{_cadena_post(cfg, grading)}[c{i}]"
    )


def _cadena_video(i: int, slot: dict, largo: float, cfg: dict, grading: str) -> str:
    W, H, FPS = cfg["W"], cfg["H"], cfg["FPS"]
    cadena = f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
    if slot["reverse"]:
        # Cierre en reversa: engancha con el inicio del loop (el corte es corto, el buffer es pequeño)
        cadena += f",trim=duration={largo:.4f},setpts=PTS-STARTPTS,reverse,setpts=PTS-STARTPTS"
    return f"{cadena},{_cadena_post(cfg, grading)}[c{i}]"


def construir_comando(slots: list[dict], audio: Path, ass: Path | None, salida: Path,
                      cfg: dict, grading: str) -> tuple[list[str], dict]:
    """Devuelve (comando_ffmpeg, resumen). Función pura: no toca el disco."""
    n = len(slots)
    FPS = cfg["FPS"]

    # Crossfade seguro: nunca más del 45% del slot más corto (cada clip participa en 2 transiciones)
    xfade = cfg["XFADE"]
    if n > 1:
        xfade = min(xfade, 0.45 * min(s["dur"] for s in slots))

    # Cada clip (menos el último) dura su slot + xfade: la transición cae sobre el inicio del slot siguiente
    largos = [s["dur"] + (xfade if i < n - 1 else 0.0) for i, s in enumerate(slots)]

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for i, (s, largo) in enumerate(zip(slots, largos)):
        if s["es_imagen"]:
            cmd += ["-i", s["archivo"]]
        else:
            cmd += ["-stream_loop", "-1", "-t", f"{largo:.4f}", "-i", s["archivo"]]
    cmd += ["-i", str(audio)]

    partes = []
    for i, (s, largo) in enumerate(zip(slots, largos)):
        partes.append(_cadena_imagen(i, s, largo, cfg, grading) if s["es_imagen"]
                      else _cadena_video(i, s, largo, cfg, grading))

    previo, acumulado = "[c0]", 0.0
    for k in range(1, n):
        acumulado += slots[k - 1]["dur"]
        salida_k = f"[x{k}]"
        partes.append(
            f"{previo}[c{k}]xfade=transition={slots[k]['transicion']}"
            f":duration={xfade:.4f}:offset={acumulado:.4f}{salida_k}"
        )
        previo = salida_k

    if ass is not None:
        partes.append(f"{previo}ass='{_escape_filter(str(ass))}',format=yuv420p[vout]")
    else:
        partes.append(f"{previo}format=yuv420p[vout]")

    cmd += [
        "-filter_complex", ";".join(partes),
        "-map", "[vout]", "-map", f"{n}:a:0",
        "-c:v", "libx264", "-crf", str(cfg["CRF"]), "-preset", cfg["PRESET"],
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest", str(salida),
    ]

    n_img = sum(1 for s in slots if s["es_imagen"])
    resumen = {
        "clips": n, "imagenes": n_img, "videos": n - n_img,
        "xfade": xfade, "duracion_s": sum(s["dur"] for s in slots),
    }
    return cmd, resumen


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline principal
# ─────────────────────────────────────────────────────────────────────────────

def create_video(evento_name: str | None = None) -> str | None:
    adn = _cargar_adn()
    cfg = _configuracion(adn)
    evento = evento_name or adn["produccion"]["evento_id"]
    if evento != adn["produccion"]["evento_id"]:
        print(f"⚠️  '{evento}' ≠ evento activo del ADN ({adn['produccion']['evento_id']}): "
              f"aspecto y semana se toman del ADN activo.")

    # 1. Único input de contenido
    lista = _cargar_lista_validada(cfg, evento)
    if lista is None:
        return None
    tomas = lista["tomas"]
    semana = lista.get("semana") or cfg["SEMANA"]

    # 2. Audio (define la duración total)
    audio = _resolver_audio(cfg, evento, cfg["ASPECTO"], tomas)
    if audio is None:
        return None
    dur_audio = _ffprobe_duracion(audio)
    if dur_audio is None:
        print(f"⚠️  ffprobe no pudo leer {audio.name}; se usa la duración de la lista de corte.")

    # 3. Slots gapless + verificación de que cada archivo exista (sin búsqueda alternativa)
    slots = _planificar_slots(tomas, dur_audio)
    if slots is None:
        return None
    faltantes = sorted({s["archivo"] for s in slots if not Path(s["archivo"]).is_file()})
    if faltantes:
        print("❌ Assets referenciados por la lista de corte que NO existen en disco:")
        for f in faltantes:
            print(f"   - {f}")
        return None

    # 4. Subtítulos y color
    ass = _resolver_ass(cfg, evento)
    grading = _filtro_grading(cfg)

    # 5. Un solo FFmpeg
    destino_dir = cfg["FINAL_DIR"] / semana
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"FINAL_{evento}.mp4"
    parcial = destino_dir / f"FINAL_{evento}.part.mp4"

    cmd, resumen = construir_comando(slots, audio, ass, parcial, cfg, grading)
    print(f"\n🎞️  {len(tomas)} tomas → {resumen['clips']} cortes "
          f"({resumen['videos']} videos + {resumen['imagenes']} imágenes con zoompan al vuelo)")
    print(f"⚡ Single-pass · aspecto [{cfg['ASPECTO'].upper() or 'N/A'}] · xfade {resumen['xfade']:.2f}s "
          f"· {resumen['duracion_s']:.2f}s · {cfg['W']}x{cfg['H']}@{cfg['FPS']}")

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, stdin=subprocess.DEVNULL)
    if res.returncode != 0:
        print(f"❌ FFmpeg error:\n{res.stderr[-3000:]}")
        if parcial.exists():
            parcial.unlink()
        return None

    os.replace(parcial, destino)
    print(f"\n✅ ¡Video listo! → {destino}")
    return str(destino)


if __name__ == "__main__":
    create_video(sys.argv[1] if len(sys.argv) > 1 else None)
