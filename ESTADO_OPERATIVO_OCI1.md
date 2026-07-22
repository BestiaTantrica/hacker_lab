# Estado Operativo de OCI-1 (Espejo Local)

> Auditoría de automatización (Redes de Pesca) - 2026-07-22

El directorio `espejo_oci1/` refleja la estructura del servidor remoto encargado de la recolección masiva automatizada.

## 1. Arquitectura de Eslabones Presente
En `espejo_oci1/monitores/` se encuentran los eslabones clave del pipeline automatizado:
- `discovery_pasivo.py`: Primer eslabón. Descubre subdominios sin autenticación usando herramientas como subfinder o crt.sh.
- `comparador.py`: Segundo eslabón. Compara el `actual.json` con el `previo.json` para generar deltas diarios.
- `analizador_ia.py` & `analizar_delta.py`: Tercer eslabón. Procesa los deltas con modelos de lenguaje para clasificar los objetivos.
- `notificador.py`: Envía alertas (Telegram) con los resúmenes del analizador.
- `explotador_automatico.py`: Script para intentar cobrar vulnerabilidades rápidas (takeovers, CORS, etc.).
- `escaneo_nuclei.sh`: Script de bash para ejecutar plantillas Nuclei masivamente sobre los deltas.

*Nota de limpieza:* Existen scripts residuales de la etapa manual (caza con lanza) que accidentalmente están en este espejo (`auditor_freshdesk.py`, `idor_cross_tenant.py`). Estos deberían eliminarse en la próxima sincronización para mantener el servidor enfocado únicamente en la automatización a gran escala.

## 2. Volumen de Datos Generados
El pipeline está generando volúmenes masivos de inteligencia en `espejo_oci1/resultados/`:
- `actual.json` pesa **25 MB**, indicando una recolección extensiva de targets (HackerOne wildcards).
- Existen deltas diarios sustanciales (ej. `delta_2026-07-18.json` de **23.5 MB**, `delta_2026-07-16.json` de **2.9 MB**).
- El analizador de IA está resumiendo estos deltas exitosamente (`analisis_YYYY-MM-DD.json` rondan los 1.5KB), lo que demuestra que el puente de compresión de datos funciona.

## 3. Conclusión Operativa
OCI-1 funciona exitosamente como la "red de pesca" automatizada. Genera una gran cantidad de datos crudos (deltas) y los filtra a través de la IA. El objetivo inmediato a partir de ahora es garantizar que el Panel C2 (OCI-2) lea estos resúmenes sin ahogarse en los JSON masivos, y continuar ampliando los exploits automáticos (como nuclei) evitando cualquier test manual que requiera sesiones.
