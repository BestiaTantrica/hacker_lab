# Reglas de Arquitectura: Cadena de Producción Asíncrona (Nodriza)

Estas reglas se aplican a todo el desarrollo de la Célula 2 (y el manejo de assets visuales de la Astrology Factory) para proteger las cuotas de API y optimizar el render de video.

1. **Catalogación Asíncrona Estricta:** La catalogación visual con Gemini (Célula 2) debe ser SIEMPRE asíncrona mediante un daemon de fondo (`nodriza_autonoma.py`). NUNCA se debe catalogar en vivo durante el render de un video (`nodriza_visual.py`). El render solo lee de JSON estático.
2. **Límite de Disco:** Existe un límite estricto de 50GB en la bóveda visual (`Astrology_Vault`). El daemon debe monitorear y detener la recolección si se alcanza este límite.
3. **Rotación de Claves (Hydra):** El uso de Gemini Vision debe rotar obligatoriamente entre `GEMINI_API_KEY` y `GEMINI_API_KEY_TEXT` (u otras declaradas en `.env`) para maximizar la cuota gratuita diaria.
4. **Pacing de API:** Se debe respetar un límite de 10 peticiones por minuto en cualquier script de fondo que haga llamadas a IA para evitar errores 429.
5. **Carpetas Estándar:** No crear carpetas nuevas; el Inbox es `Descargas_Crudas/` y el destino catalogado es `Assets_Reusables/`.
