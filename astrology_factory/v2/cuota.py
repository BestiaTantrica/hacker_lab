#!/usr/bin/env python3
"""
🛑 CUOTA — Frenos y reguladores compartidos para las API keys de Gemini.

Reglas:
  * Solo se usan keys de producción interna (GEMINI_API_KEY*, SIN "_WEB").
    Las keys "_WEB" quedan reservadas para bots públicos / Carta Natal.
  * Se reparte el trabajo: siempre se usa la key con MENOS usos hoy.
  * Si una key responde "cuota diaria agotada", descansa hasta el reseteo
    (medianoche hora del Pacífico = 04:00 en Argentina). No se insiste.
  * Si es un límite por minuto, descansa 90 s y se prueba otra key.
  * Hay un ritmo mínimo entre llamadas (PAUSA_MIN_S) para ir lento y seguro.
  * Todo el estado se guarda en disco (sobrevive reinicios y procesos
    paralelos). Nada de /tmp.
"""

import fcntl
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
ESTADO_PATH = FACTORY_ROOT / "estado_cuota.json"
LOCK_PATH = FACTORY_ROOT / ".estado_cuota.lock"

PAUSA_MIN_S = float(os.getenv("CUOTA_PAUSA_MIN_S", "8"))       # entre llamadas (global)
BLOQUEO_MINUTO_S = 90                                           # límite por minuto
LIMITE_SUAVE_DIARIO = int(os.getenv("CUOTA_LIMITE_DIARIO", "200"))  # por key, para repartir

# Pacífico sin DST complicado: Google resetea a medianoche PT. Usamos UTC-8 (conservador:
# con DST real el reseteo ocurre 1 h antes, así que nunca despertamos demasiado temprano).
PT = timezone(timedelta(hours=-8))


def _cargar_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(FACTORY_ROOT / ".env")
    except ImportError:
        pass


def _ahora_pt() -> datetime:
    return datetime.now(PT)


def _hoy() -> str:
    return _ahora_pt().strftime("%Y-%m-%d")


def segundos_hasta_reset() -> int:
    ahora = _ahora_pt()
    manana = (ahora + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)
    return max(60, int((manana - ahora).total_seconds()))


def keys_produccion() -> dict:
    """{nombre_env: key} solo de producción interna (excluye _WEB), sin duplicados."""
    _cargar_env()
    out, vistos = {}, set()
    for nombre, valor in os.environ.items():
        if nombre.startswith("GEMINI_API_KEY") and "_WEB" not in nombre and valor and valor not in vistos:
            out[nombre] = valor
            vistos.add(valor)
    return dict(sorted(out.items()))


@contextmanager
def _estado():
    """Lee/escribe el estado con candado (seguro entre procesos)."""
    with open(LOCK_PATH, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            try:
                data = json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            if data.get("fecha") != _hoy():          # día nuevo: todo en cero
                data = {"fecha": _hoy(), "keys": {}, "ultima_llamada": 0.0,
                        "alerta_enviada": False}
            yield data
            tmp = ESTADO_PATH.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            os.replace(tmp, ESTADO_PATH)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _k(data, nombre):
    return data["keys"].setdefault(nombre, {"usos": 0, "bloqueada_hasta": 0.0, "motivo": ""})


def elegir_key():
    """Devuelve (nombre, key) de la key disponible con menos usos hoy, o None."""
    keys = keys_produccion()
    ahora = time.time()
    with _estado() as d:
        candidatas = []
        for nombre in keys:
            e = _k(d, nombre)
            if e["bloqueada_hasta"] > ahora:
                continue
            candidatas.append((e["usos"] >= LIMITE_SUAVE_DIARIO, e["usos"], nombre))
        if not candidatas:
            return None
        candidatas.sort()
        _, _, nombre = candidatas[0]
        return nombre, keys[nombre]


def esperar_ritmo():
    """Garantiza una pausa mínima entre llamadas, aun con varios procesos."""
    with _estado() as d:
        falta = PAUSA_MIN_S - (time.time() - d["ultima_llamada"])
        d["ultima_llamada"] = time.time() + max(0.0, falta)
    if falta > 0:
        time.sleep(falta)


def registrar_uso(nombre):
    with _estado() as d:
        _k(d, nombre)["usos"] += 1


def registrar_error(nombre, error) -> str:
    """Clasifica el error y frena la key si corresponde.
    Devuelve: 'diaria' | 'minuto' | 'otro'."""
    txt = str(error).lower()
    es_cuota = "429" in txt or "resource_exhausted" in txt or "quota" in txt
    if not es_cuota:
        return "otro"
    diaria = "perday" in txt or "per day" in txt or "daily" in txt
    with _estado() as d:
        e = _k(d, nombre)
        if diaria:
            e["bloqueada_hasta"] = time.time() + segundos_hasta_reset()
            e["motivo"] = "cuota diaria agotada"
            return "diaria"
        e["bloqueada_hasta"] = time.time() + BLOQUEO_MINUTO_S
        e["motivo"] = "límite por minuto"
        # Si ya rebotó muchas veces seguidas en el día, asumimos cuota diaria.
        e["rebotes"] = e.get("rebotes", 0) + 1
        if e["rebotes"] >= 3 and e["usos"] >= 20:
            e["bloqueada_hasta"] = time.time() + segundos_hasta_reset()
            e["motivo"] = "cuota diaria (rebotes repetidos)"
            return "diaria"
        return "minuto"


def todas_agotadas() -> bool:
    return elegir_key() is None


def segundos_hasta_proxima_key() -> int:
    keys = keys_produccion()
    ahora = time.time()
    with _estado() as d:
        esperas = [max(0, _k(d, n)["bloqueada_hasta"] - ahora) for n in keys]
    return int(min(esperas)) if esperas else segundos_hasta_reset()


def alerta_pendiente() -> bool:
    """True una sola vez por día (para no spamear Telegram)."""
    with _estado() as d:
        if d.get("alerta_enviada"):
            return False
        d["alerta_enviada"] = True
        return True


def resumen() -> str:
    keys = keys_produccion()
    ahora = time.time()
    lineas = [f"📊 Cuota Gemini {_hoy()} (límite suave {LIMITE_SUAVE_DIARIO}/key, pausa {PAUSA_MIN_S:.0f}s)"]
    with _estado() as d:
        for n in keys:
            e = _k(d, n)
            if e["bloqueada_hasta"] > ahora:
                mins = int((e["bloqueada_hasta"] - ahora) / 60)
                est = f"💤 {e['motivo']} (vuelve en {mins} min)"
            else:
                est = "✅ disponible"
            lineas.append(f"   {n}: {e['usos']} usos hoy — {est}")
    return "\n".join(lineas)


if __name__ == "__main__":
    print(resumen())
