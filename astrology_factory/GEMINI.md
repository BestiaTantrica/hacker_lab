# Astrology Factory V2

Este proyecto produce videos cortos de astrología esotérica para redes sociales y productos web de alta gama.
El pipeline va de audio TTS → clasificación de assets → matching semántico → ensamble FFmpeg.

**Regla más importante de APIs:** NUNCA enviar peticiones a Gemini en batch; pasar siempre por `v2/cuota.py`.
Las 10 API keys comparten una sola cuota GCP (~1500 req/día). Trabajar lento pero sin quemar el free tier.

**🏛️ LEY SAGRADA DE CLAUDE PRO (NIVEL 3) - CERO TOKENS DESPERDICIADOS:**
- **PROHIBIDO** usar a Claude para auditar tránsitos diarios o tareas rutinarias de producción. Los tránsitos los calcula Swiss Ephemeris (`pyswisseph`) y los guiones los procesa Gemini Flash a costo cero.
- **CLAUDE SE USA EXCLUSIVAMENTE PARA DOS COSAS:**
  1. **Forjar MODELOS DE ORO CANÓNICOS**: Crear los moldes maestros perfectos (Few-Shot) para que Gemini Flash los imite infinitamente sin degradar calidad.
  2. **Programación de PRECISIÓN MILITAR (Cero Error)**: Criptografía y Webhooks de Mercado Pago (HMAC SHA-256, idempotencia estricta en SQLite), Shaders GLSL para WebGL 3D, y matemática pura.

**Arquitectura rápida:** celula_0 (clasifica assets) → celula_1 (TTS/subtítulos) →
celula_2 (matching + Director de Arte) → celula_3 (ensamble FFmpeg final).
