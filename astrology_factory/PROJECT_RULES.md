# ASTROLOGY FACTORY — REGLAS DEL PROYECTO (ORQUESTACIÓN)

> **CONTEXTO DE PROYECTO:** Este es un motor de generación automatizada de videos astrológicos para redes sociales (YouTube Shorts / TikTok). Se basa en astrología real, cruda y empírica, transformada en arte digital.

## ESTADO ACTUAL (HANDOFF)
- **Octubre en Producción:** Estamos compilando los 8 videos de la **Semana 1 de Octubre (Venus en Escorpio)**.
- **Formato Semanal:** 8 videos en total (1 resumen semanal + 7 tránsitos diarios de la semana). 
- **Flujo FASE 1:** Producción de diarios. De a UNO POR VEZ. (Script -> Audio -> Visuals -> Render -> Aprobación).
- **Flujo FASE 2:** El resumen Semanal.

## REGLAS OPERATIVAS MAESTRAS
1. **BÓVEDA CENTRALIZADA (INAMOVIBLE):**
   - Ruta absoluta única: `/home/tomas2/MediaContingencia/Privada/Astrology_Vault`
   - Videos finales: `Videos_Finales/<Semana_Prefijo>/FINAL_<Evento>.mp4`
   - Assets: `Assets_Reusables/<Semana_Prefijo>/<id>.mp4`
   - *PROHIBIDO mover o renombrar esta bóveda.*
2. **VADEMÉCUM (ACTUALIZACIÓN AUTOMÁTICA):**
   - El JSON `vademecum.json` se alimenta de lo producido. Es la memoria para el Bot de respuestas. El usuario no lo actualiza manualmente.
3. **CASCADA DE ROLES:**
   - Para escribir guiones -> lee `content_factory/ROLE_SCRIPTWRITER.md`.
   - Para renderizar e imagen -> lee `produccion/ROLE_VIDEOMAKER.md`.

## Regla de Edición FFmpeg
**Timeline Estricto de Clips (Gapless)**: Cuando se subdivida una frase (phrase_dur) en múltiples micro-clips de imágenes/glitches en FFmpeg, la sumatoria de todas las duraciones de esos assets debe igualar exactamente el phrase_dur. El último clip del loop siempre debe absorber el tiempo residual matemáticamente para evitar que surjan frames negros durante la fase de concatenación.
