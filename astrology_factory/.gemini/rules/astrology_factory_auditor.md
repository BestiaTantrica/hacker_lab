---
description: Reglas estrictas para el procesamiento de assets, límites de API y auditoría visual en Astrology Factory.
---
# Reglas de Auditoría y Procesamiento de Assets

1. **Uso de SDK**: Para interactuar con Gemini en Python, usar siempre la librería oficial nueva `google-genai` (no la deprecada `google.generativeai`).
2. **Manejo de Modelos y 503**: Al usar la capa gratuita de Google AI Studio, usar SIEMPRE el modelo `gemini-flash-latest` para evadir errores 503 (UNAVAILABLE) por alta demanda en modelos específicos.
3. **Límites de Cuota (Rate Limits)**: Para tareas masivas en capa gratuita, forzar un `time.sleep(6.0)` (10 RPM) entre peticiones para evitar bloqueos por cuotas.
4. **Videos vs Imágenes**: NUNCA enviar videos completos (.mp4) a la API de Gemini Vision para clasificación masiva. Extraer el primer frame usando `ffmpeg` o similar, guardarlo como imagen temporal, y enviarlo a la API.
5. **Auditoría UI**: Al crear scripts de clasificación manual, los archivos aprobados deben MOVERSE (`shutil.move`) del directorio de origen, nunca copiarse, garantizando que el usuario pueda interrumpir y reanudar sesiones sin ver repetidos.
6. **Orquestación de APIs (Anti-Colisiones)**: En ecosistemas multi-célula, sharding de llaves es obligatorio. Procesos de visión (ej. Clasificador) deben usar `GEMINI_API_KEY`, mientras que procesos de texto/TTS concurrentes deben usar una llave paralela (ej. `GEMINI_API_KEY_TEXT`) para evadir el límite 429 de la capa gratuita.
7. **Contexto Semántico Recursivo**: Cuando Gemini asigne assets a un guion, nunca pasar solo el nombre del archivo. Usar siempre `rglob("*")` para extraer e inyectar el nombre de la carpeta padre (la `categoria`) en el prompt. Esto multiplica la precisión del modelo semántico.
8. **Estabilidad Git (Nave Nodriza)**: Cada vez que una Célula o Hilo logre estabilizarse, se debe hacer un commit inmediatamente antes de pasar al siguiente nivel de arquitectura, asegurando puntos de restauración orgánicos.
