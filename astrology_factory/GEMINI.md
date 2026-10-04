# Astrology Factory V2

Este proyecto produce videos cortos de astrología esotérica para redes sociales.
El pipeline va de audio TTS → clasificación de assets → matching semántico → ensamble FFmpeg.

**Regla más importante:** NUNCA enviar peticiones a Gemini en batch; pasar siempre por `v2/cuota.py`.
Las 10 API keys comparten una sola cuota GCP (~1500 req/día). Trabajar lento pero sin quemar el free tier.

**Arquitectura rápida:** celula_0 (clasifica assets) → celula_1 (TTS/subtítulos) →
celula_2 (matching + Director de Arte) → celula_3 (ensamble FFmpeg final).

**Skill de referencia completo:** activar `astrology-factory-architecture` para mapa detallado de módulos,
emociones↔transiciones, variables de entorno, convenciones FFmpeg y servicios systemd.
