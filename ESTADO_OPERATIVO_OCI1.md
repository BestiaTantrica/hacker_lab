# Estado Operativo de OCI-1 (Espejo Local)

> **Actualización:** 2026-07-31 — Pipeline v2 con Go-Stack ProjectDiscovery activo.

El directorio `espejo_oci1/` refleja la estructura del servidor remoto encargado de la recolección masiva automatizada.

## 1. Arquitectura de Eslabones Presente (Pipeline v2 — Go-Stack)
En `espejo_oci1/monitores/` y `espejo_oci1/` se encuentran los eslabones del nuevo pipeline automatizado:
- `mass_recon.py`: Eslabón 1. Descubre subdominios usando `subfinder` (en PATH `/usr/local/bin`) + crt.sh como fallback. Guarda en `oci1_db.sqlite` (WAL mode).
- `comparador.py`: Eslabón 2. Consulta SQLite las últimas 24h y genera `delta_{zona}_FECHA.json`.
- `alterx` + `dnsx` + `httpx` (binarios Go): Eslabón 3. Generan permutaciones masivas en memoria y filtran subdominios sin DNS real, luego hacen probing HTTP masivo para sacar CNAMEs y tech-stack.
- `katana`: Eslabón 3.5. Hace crawling dinámico sobre los hosts HTTP vivos para extraer rutas Javascript ocultas (`-js-crawl`).
- `nuclei` (v3.3.0): Eslabón 4. Ejecuta doble pasada: una sobre hosts vivos (takeovers, misconfigurations) y una ultra-focalizada en secretos/tokens sobre los archivos `.js` descubiertos por katana. Genera `nuclei_{zona}_FECHA.json`.
- `parsear_nuclei.py`: Eslabón 5. Lee el JSONL de nuclei, aplica guardrails anti-falso-positivo (M3-A+M3-B), sincroniza con OCI-2 (`POST /api/ingest_delta`) y notifica a Telegram.
- **M3-A `poc_generator.py`**: Eslabón 5.5. Sanitiza el `curl-command` crudo de Nuclei → `triager_poc` copiable. Evalúa `poc_quality` = HIGH / MEDIUM / UNVERIFIABLE.
- **M3-B `scope_validator.py`**: Pre-filtro (Guardrail 3). Valida el host contra SCOPE_DB (44 programas H1). Filtra severidad mínima por programa. Deduplica via SHA-256 cross-ejecución. `calculate_batch_size()` ajusta dinámicamente el número de subdominios según RAM disponible (`/proc/meminfo`).
- **M3-C `waf_mutator.py`**: Mutación de headers para evadir 403/406 en sondas. Pool de 5 UA reales. `rotate_headers(attempt)` determinístico. Integrado en `explotador_automatico.py` con retry automático en attempt=2.
- **Circuit Breaker & GC**: Eslabón 6 y Wrappers. Watchdog de RAM asíncrono (750MB límite). Heartbeat al C2.


### Herramientas instaladas en OCI-1 (`/usr/local/bin/`):
- `subfinder` v2.14.0 ✅
- `alterx` v0.1.0 ✅ (**nuevo**)
- `dnsx` v1.2.1 ✅ (**nuevo**)
- `httpx` v1.6.8 ✅ (**nuevo, binario Go - no el wrapper Python**)
- `katana` v1.1.0 ✅ (**ahora integrado** en Eslabón 3.5 para JS Extraction)
- `nuclei` v3.3.0 ✅ (**ahora integrado** en el pipeline v2 para Pasive JS Secret Scanner)

## 2. Volumen de Datos Generados
El pipeline está generando volúmenes masivos de inteligencia en `espejo_oci1/resultados/`:
- `actual.json` pesa **25 MB**, indicando una recolección extensiva de targets (HackerOne wildcards).
- Existen deltas diarios sustanciales (ej. `delta_2026-07-18.json` de **23.5 MB**, `delta_2026-07-16.json` de **2.9 MB**).
- El analizador de IA está resumiendo estos deltas exitosamente (`analisis_YYYY-MM-DD.json` rondan los 1.5KB), lo que demuestra que el puente de compresión de datos funciona.

## 3. Conclusión Operativa
OCI-1 funciona exitosamente como la "red de pesca" automatizada. Genera una gran cantidad de datos crudos (deltas) y los filtra a través de la IA. El objetivo inmediato a partir de ahora es garantizar que el Panel C2 (OCI-2) lea estos resúmenes sin ahogarse en los JSON masivos, y continuar ampliando los exploits automáticos (como nuclei) evitando cualquier test manual que requiera sesiones.
