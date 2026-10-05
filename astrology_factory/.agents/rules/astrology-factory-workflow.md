---
name: astrology-factory-workflow
description: Reglas estrictas para la ejecución del pipeline de la Fábrica de Astrología V2.
---

# Reglas de Ejecución del Pipeline (Astrology Factory)

1. **Dependencia de Subtítulos (Bloqueante):** NUNCA se debe ejecutar la Fase C (Ensamblador Final) sin antes haber ejecutado la sincronización de subtítulos con Whisper (`v2/celula_1/cronometrador_y_tts.py --opcion 2`). Si se regenera el audio (Fase A), ES OBLIGATORIO regenerar el archivo `.ass`.
2. **Volumen Mínimo de Curaduría:** NUNCA iniciar la Fase C con menos de 10 assets visuales auditados en la bóveda para la semana en curso. Si el agente genera imágenes de contingencia, debe generar una batería completa (clips cortos, gifs, glitches, loops) para evitar que el `asignador_semantico` recicle basura de `Assets_Reusables` rompiendo la estética.
3. **Consistencia Estética:** No mezclar estilos. Si un video es "Dark Fantasy", purgar o aislar temporalmente los assets de otros estilos (ej. rompecabezas de stock) para que no se filtren en el ensamble.
4. **Voz Argentina (Preferencia):** Priorizar siempre voces de acento argentino (ej. `es-AR-TomasNeural` en Edge-TTS). Si se usa Piper TTS (local), buscar activamente modelos `es_AR` o hispanoamericanos neutros antes que España puro.

5. **Cuota de API — Freno Obligatorio:** NUNCA enviar peticiones a Gemini en batch o en bucle sin pasar por `v2/cuota.py`. El gestor limita la velocidad, rota keys y guarda estado en `estado_cuota.json`. Si responde `AGOTADO`, el script sale con `sys.exit(0)` — no reintenta, no alerta por Telegram. Las 10 keys pertenecen al mismo proyecto GCP y comparten una sola cuota (~1500 req/día free tier). Rotar keys da resiliencia ante errores puntuales, NO multiplica el límite.

6. **Servicios systemd — Una sola instancia:** Servicios registrados: `nodriza_auditora.service` (ACTIVO) y `nodriza_autonoma.service` (DISABLED — duplicado). NUNCA usar `Restart=always` en un servicio que consume API; usar `Restart=on-failure` con `StartLimitBurst=3` y `StartLimitIntervalSec=300`. Ante alertas repetidas de Telegram, verificar primero `systemctl --user list-units --state=running` antes de matar procesos manualmente.

7. **Imágenes prohibidas — Cuarentena automática:** El clasificador usa código `"00"` para descartar imágenes inapropiadas; éstas van a `Astrology_Vault/Cuarentena_Visual/` (nunca se borran). Categorías rechazadas: familias, parejas, bebés, niños, selfies, bodas, escenas domésticas, personas cotidianas. FALSOS POSITIVOS — NO mover a cuarentena: fotos NASA con palabras como "baby nebula", "familiar beauty" o "earth smiled" en el título; son imágenes espaciales válidas.

8. **Filtro Semántico Híbrido y Rotación de APIs:** La asignación visual (`nodriza_visual.py`) DEBE usar Inteligencia Artificial (Gemini) para elegir la imagen final, pero para no quemar tokens ni cuota, debe pre-filtrar localmente los 40 mejores assets matemáticamente y enviarle SOLO esos 40 al modelo (`elegir_mejor_asset_hibrido`). Las peticiones deben rotar aleatoriamente sobre todas las `GEMINI_API_KEY_*` disponibles en `.env` (excluyendo _WEB) para evadir el rate limit 429.


10. **Diseño del Gancho (Toma 1):** El primer clip (Gancho) NUNCA debe ser una imagen espacial estática genérica o planetas aburridos. Debe transmitir sensación de entrada profunda, viaje o explosión (ej. vórtices cósmicos, estallidos, semillas explotando, olas rompiendo). El prompt semántico debe forzar específicamente esta regla si el rol es "gancho".

11. **Niveles de Audio Orgánico:** En `mezclador_sonoro.py`, la música de sanación (cuencos, frecuencias orgánicas) NUNCA debe ahogarse bajo la voz. El volumen base debe ser `0.80`, y en los momentos de tensión/clímax debe elevarse dinámicamente a `1.40` para generar contrastes emocionales vivos. No usar volúmenes conservadores (ej. 0.30).
