# Astrology Factory - Handoff (Contexto Actualizado)

Este documento contiene el estado exacto del proyecto al momento de iniciar una nueva conversación. Sirve para que la IA se ponga al día instantáneamente y no repita errores.

## 0. DIRECTIVA DE PRE-EJECUCIÓN (REGLA DE ORO)
**PROHIBIDO INVENTAR O CREAR PROCESOS A CIEGAS.**
Antes de modificar, crear o eliminar CUALQUIER script, archivo o flujo del proyecto, el agente está obligado a:
1. Releer la estructura del proyecto (`list_dir`, `grep_search`, `view_file`).
2. Entender *dos veces* cómo funciona el ecosistema actual.
3. Asegurarse de no estar superponiendo una solución nueva sobre una existente.
4. Identificar exactamente dónde encaja la modificación para no romper la cadena de automatización.
## 1. Reglas Operativas (ROLES DE TRABAJO)
- **El usuario NO toca la terminal**: La IA (vos) debe ejecutar absolutamente TODOS los comandos, crear archivos y compilar videos usando tus herramientas (ej. `run_command`).
- **Actualización Automática**: El "Vademécum" (registro de lo que se produce) debe actualizarse automáticamente vía scripts, para que la API de horóscopos (`ai_persona_engine.py`) siempre tenga el contexto de los videos generados. El usuario NO debe hacer esto a mano.

## 2. Estado del Proyecto
- **Motor de Video (`video_maker.py`)**: Funciona perfecto (Edge-TTS, Whisper, FFmpeg, Color Grading).
- **Formato de 8 Videos por Semana**: 
  - 1 Video Semanal (60-90 segundos) como "previa y acompañamiento" al hueso.
  - 7 Videos Diarios (30-40 segundos) para profundizar en el tránsito de cada día.
- **Orquestación (`render_semanal.py`)**: Batch render para los 8 videos.

## 3. Reglas Estrictas de Producción (Astrología de Grado Militar)
- **Realismo y Precisión**: Foco en empatía y psicología, pero realista.
- **CERO CHAMUYO**: Prohibido usar "consejos bonitos" o frases de autoayuda. Es un pronóstico clínico.
- **Tiempos Exactos**: Remarcar cuándo ocurre la acción ("hoy a la mañana").

## 4. Próximo Paso Inmediato
Estamos compilando los 8 videos de la **Semana 1 de Octubre (Venus en Escorpio)**.
Se debe implementar un mecanismo automatizado para que, al generarse estos guiones, pasen directo a un registro (`vademecum.json` o similar) que sea leído por la API del bot de respuestas.

## 5. Reglas de Producción
Ver /home/LAB/astrology_factory/PRODUCTION_RULES.md — es obligatorio leerlo al inicio de cada conversación.
