---
name: astrology-factory-workflow
description: Reglas estrictas para la ejecución del pipeline de la Fábrica de Astrología V2.
---

# Reglas de Ejecución del Pipeline (Astrology Factory)

1. **Dependencia de Subtítulos (Bloqueante):** NUNCA se debe ejecutar la Fase C (Ensamblador Final) sin antes haber ejecutado la sincronización de subtítulos con Whisper (`v2/celula_1/cronometrador_y_tts.py --opcion 2`). Si se regenera el audio (Fase A), ES OBLIGATORIO regenerar el archivo `.ass`.
2. **Volumen Mínimo de Curaduría:** NUNCA iniciar la Fase C con menos de 10 assets visuales auditados en la bóveda para la semana en curso. Si el agente genera imágenes de contingencia, debe generar una batería completa (clips cortos, gifs, glitches, loops) para evitar que el `asignador_semantico` recicle basura de `Assets_Reusables` rompiendo la estética.
3. **Consistencia Estética:** No mezclar estilos. Si un video es "Dark Fantasy", purgar o aislar temporalmente los assets de otros estilos (ej. rompecabezas de stock) para que no se filtren en el ensamble.
4. **Voz Argentina (Preferencia):** Priorizar siempre voces de acento argentino (ej. `es-AR-TomasNeural` en Edge-TTS). Si se usa Piper TTS (local), buscar activamente modelos `es_AR` o hispanoamericanos neutros antes que España puro.
