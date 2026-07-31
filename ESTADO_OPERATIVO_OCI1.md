# Estado Operativo de OCI-1 (Espejo Local)

> **Actualización:** 2026-07-31 — Pipeline v2 con Go-Stack ProjectDiscovery activo.

El directorio `espejo_oci1/` refleja la estructura del servidor remoto encargado de la recolección masiva automatizada.

## 1. Arquitectura de Eslabones Presente (Pipeline v2 — Go-Stack)
En `espejo_oci1/monitores/` y `espejo_oci1/` se encuentran los eslabones del nuevo pipeline automatizado:
- `mass_recon.py`: Eslabón 1. Descubre subdominios usando `subfinder` (en PATH `/usr/local/bin`) + crt.sh como fallback. Guarda en `oci1_db.sqlite` (WAL mode).
- `comparador.py`: Eslabón 2. Consulta SQLite las últimas 24h y genera `delta_{zona}_FECHA.json`.
- `dnsx` + `httpx` (binarios Go): Eslabón 3. Filtran subdominios sin DNS real y hacen probing HTTP masivo para sacar CNAMEs, titles y tech-stack. **Elimina la causa raíz de los falsos positivos.**
- `nuclei` (v3.3.0): Eslabón 4. Escanea únicamente hosts HTTP vivos con plantillas `takeovers/`, `exposures/`, `misconfiguration/` en severidad `critical,high,medium`. Genera `nuclei_{zona}_FECHA.json`.
- `parsear_nuclei.py`: Eslabón 5. Lee el JSONL de nuclei, aplica guardrails anti-falso-positivo, sincroniza con OCI-2 (`POST /api/ingest_delta`) y notifica a Telegram.
- **Circuit Breaker & GC**: Eslabón 6 y Wrappers. Se integró un Watchdog de RAM asíncrono para abortar `dnsx`/`httpx`/`nuclei` si exceden 750MB. Al final de la cascada, evalúa el `%` de uso de disco: si excede 85%, lanza purga dinámica (Watermark GC) iterativa para no reventar el Free Tier. También emite un `Heartbeat` al C2.

### Herramientas instaladas en OCI-1 (`/usr/local/bin/`):
- `subfinder` v2.14.0 ✅
- `dnsx` v1.2.1 ✅ (**nuevo**)
- `httpx` v1.6.8 ✅ (**nuevo, binario Go - no el wrapper Python**)
- `katana` v1.1.0 ✅ (**nuevo** — disponible para crawling, no integrado aún en pipeline)
- `nuclei` v3.3.0 ✅ (ya existía, **ahora integrado** en el pipeline v2)

## 2. Volumen de Datos Generados
El pipeline está generando volúmenes masivos de inteligencia en `espejo_oci1/resultados/`:
- `actual.json` pesa **25 MB**, indicando una recolección extensiva de targets (HackerOne wildcards).
- Existen deltas diarios sustanciales (ej. `delta_2026-07-18.json` de **23.5 MB**, `delta_2026-07-16.json` de **2.9 MB**).
- El analizador de IA está resumiendo estos deltas exitosamente (`analisis_YYYY-MM-DD.json` rondan los 1.5KB), lo que demuestra que el puente de compresión de datos funciona.

## 3. Conclusión Operativa
OCI-1 funciona exitosamente como la "red de pesca" automatizada. Genera una gran cantidad de datos crudos (deltas) y los filtra a través de la IA. El objetivo inmediato a partir de ahora es garantizar que el Panel C2 (OCI-2) lea estos resúmenes sin ahogarse en los JSON masivos, y continuar ampliando los exploits automáticos (como nuclei) evitando cualquier test manual que requiera sesiones.
