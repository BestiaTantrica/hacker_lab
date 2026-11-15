# MANDATO SUPREMO: PROTOCOLO DE PRODUCCIÓN DIARIA (ZERO AD-HOC SCRIPTS)

> **ATENCIÓN A TODOS LOS AGENTES (Antigravity, Claude, Argon, Gemini):**
> Este repositorio cuenta con una arquitectura modular V2 completamente probada y funcional.
> El usuario ha experimentado frustración extrema y pérdida de tiempo por agentes que "inventaron la rueda" creando scripts ad-hoc diarios (`preparar_video_XX.py`, `ensamblador_XX.py`, `video_XX.py`), hardcodeando duraciones fijas y copiando imágenes viejas.
> **ESTAS REGLAS SON DE ACATAMIENTO OBLIGATORIO Y ESTRICTO SIN NINGUNA EXCEPCIÓN.**

---

## 1. PROHIBICIÓN TOTAL DE SCRIPTS AD-HOC
- **PROHIBIDO** crear nuevos scripts de ensamblaje o preparación diaria (ej: `preparar_video_08_noviembre.py`, `ensamblador_8_noviembre.py`).
- **PROHIBIDO** hardcodear rutas fijas a archivos de imagen específicos de días anteriores (ej: volver a usar siempre la misma escultura, la misma balanza o el mismo fondo espacial).
- **PROHIBIDO** forzar duraciones estáticas en FFmpeg independientes de la voz (ej: poner 39.6s cuando la voz dura 28s genera 11 segundos de silencio mortal).

---

## 2. EL ÚNICO COMANDO CANÓNICO DE PRODUCCIÓN
Toda orden de producción diaria (del 7, del 8, del 9, etc.) se ejecuta **ÚNICA Y EXCLUSIVAMENTE** a través del orquestador unificado:

```bash
/home/LAB/astrology_factory/venv/bin/python /home/LAB/astrology_factory/produccion_diaria.py --fecha YYYY-MM-DD
```

O a través del botón **"🎬 PRODUCIR VIDEO V2"** en el Panel de Administración Web (`http://localhost:8000/admin`).

---

## 3. LEYES MATEMÁTICAS Y EDITORIALES INMUTABLES
1. **El Audio es el Reloj Maestro:**
   - La duración total del video y de cada escena está gobernada al milisegundo por la locución real medida con Whisper (`timeline_huecos.json`).
   - El video dura exactamente lo que dura la voz. Cero silencio al final.
2. **Rotación Visual Estricta (30 Días Anti-Repetición):**
   - La Célula 2 (`v2/celula_2/nodriza_visual.py`) selecciona assets de `assets_visuales.db` asegurando que ningún asset utilizado en los últimos 30 días sea reusado.
   - El Reloj 2D / Astrolabio Sagrado se genera dinámicamente con las efemérides astronómicas exactas del día de Swiss Ephemeris.
3. **Tono y Voz Editorial (Tomás):**
   - Voseo rioplatense auténtico, profundidad psicológica, cero clichés de horóscopo ("fijate", "la trampa de hoy", "cae la máscara").
   - CTA comercial directo a la acción: "Contá en qué signo tenés a [Planeta]... y entrá al link del perfil para ver qué casa te enciende este aspecto."
4. **Diseño Sonoro Multicapa:**
   - FFmpeg single-pass integra la frecuencia Solfeggio del aspecto (ducking bajo voz) + stock sonoro ambiental.

---

## 4. RESPUESTA ANTE EL USUARIO
Cuando Tomás pida producir un día (ej: *"Hacete el del 8"*, *"Producir 2026-11-08"*):
1. **NO propongas hacer un script nuevo.**
2. Ejecuta inmediatamente:
   `/home/LAB/astrology_factory/venv/bin/python /home/LAB/astrology_factory/produccion_diaria.py --fecha YYYY-MM-DD`
3. Reporta el progreso de las células y la entrega del archivo final en:
   `/home/tomas2/Desktop/Boveda_Astrologia/Videos_Finales/Nov_W1/FINAL_YYYY-MM-DD_[Evento].mp4`

