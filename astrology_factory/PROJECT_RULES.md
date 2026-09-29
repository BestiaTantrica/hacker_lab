# ASTROLOGY FACTORY — REGLAS DEL PROYECTO (ORQUESTACIÓN)

> **CONTEXTO DE PROYECTO:** Este es un motor de generación automatizada de videos astrológicos para redes sociales (YouTube Shorts / TikTok). Se basa en astrología real, cruda y empírica, transformada en arte digital.

## ESTADO ACTUAL (HANDOFF)
- **Octubre en Producción (V2):** Estamos compilando los videos de la **Semana 1 de Octubre (Venus en Escorpio)** utilizando la nueva arquitectura "Navaja Suiza Fractal" (V2).
- **Arquitectura Activa:** Todo el flujo se ejecuta exclusivamente mediante las Células Madre (Scripts 0 a 3) documentados en `mapa_orquestador.md`. 
- **Flujo FASE 1:** Producción de videos cortos. Se ejecuta estrictamente siguiendo el "Flujo Canónico" del mapa orquestador.

## REGLAS OPERATIVAS MAESTRAS
1. **MAPA ORQUESTADOR:**
   - El archivo `mapa_orquestador.md` es la ÚNICA brújula válida para la ejecución de scripts.
   - Todo comando de generación, manipulación, ffmpeg o tts debe ejecutarse llamando a las células de la carpeta `v2/` con su respectiva `--opcion`.
   - **REGLA ABSOLUTA DE IA**: NUNCA improvises scripts sueltos ni saltes los pasos de la fábrica. Debes respetar SIEMPRE el flujo canónico (Célula 0 -> Célula 1 -> Célula 2 -> Célula 3). Cualquier problema de código se arregla DENTRO de la célula correspondiente, jamás creando contingencias externas.
2. **BÓVEDA CENTRALIZADA (INAMOVIBLE):**
   - Ruta absoluta única: `/home/tomas2/MediaContingencia/Privada/Astrology_Vault`
   - Descargas Nuevas (Cuarentena): `Descargas_Crudas/<Semana_Prefijo>/`
   - Assets Aprobados: `Assets_Auditados/<Semana_Prefijo>/`
   - Videos finales: `Videos_Finales/<Semana_Prefijo>/FINAL_<Evento>.mp4`
   - *PROHIBIDO mover o renombrar esta bóveda.*
3. **ADN DEL VIDEO (contexto_astrologico.json):**
   - Este JSON rige absolutamente todos los parámetros de los scripts V2 (queries, colores, textos, duraciones).

## Regla de Edición FFmpeg
**Timeline Estricto de Clips (Gapless)**: Las células en `v2/celula_3` usan el archivo `timeline_huecos.json` generado por la Célula 1 como ÚNICA fuente de verdad para los tiempos matemáticos. No se puede alterar este tiempo en post-producción; todo clip encaja milimétricamente.

## FASE 2: ECOSISTEMA COMUNITARIO (NODRIZA / AGENTES)
1. **Regla del Flujo de Tráfico:** 
   - Las redes sociales y Telegram son el "Front-Desk" (captura de atención). El objetivo principal de cualquier bot/agente en estas plataformas es derivar al usuario a la Web Oficial para que se registre y nos deje su carta astral real (para el estudio sociológico).
2. **Modelo Freemium y Monetización:**
   - **GRATIS:** Suscripción, chatear con el Agente en la web, Rectificación de Horario y Carta Natal básica por PDF/Mail.
   - **PAGO ($5-$10 USD):** Productos Premium (Videos de Carta Natal, Revolución Solar, Sinastrías). Los pagos se procesan externamente (MercadoPago/PayPal).
3. **Restricción de Infraestructura (Videos):**
   - El servidor principal NO aloja videos bajo ninguna circunstancia. Todo el contenido multimedia pesado generado para usuarios Premium debe ser entregado mediante enlaces externos (YouTube Oculto, Telegram privado, etc.).
4. **La Personalidad (InteractivePersonaEngine):**
   - El motor de IA (sea Gemini, Groq u otro) DEBE inyectar siempre el `MASTER_PROMPT.md` con la **carta astral completa del creador**. La IA no es genérica; es el alter-ego del creador (directa, picante, profunda).
5. **Base de Datos y Asincronía:**
   - Todo registro se centraliza en `users.sqlite`.
   - La preparación de assets para los videos Premium funciona con "Caching Predictivo" (registro de tareas pendientes en BD al momento de suscripción) para acelerar el render local posterior.

## 3. ESTRUCTURA DE LA NAVE NODRIZA (GOBERNANZA GLOBAL)
Toda interacción de IAs en este proyecto debe respetar la estructura de 3 niveles coordinada por la Célula Gobernante (`v2/nodriza/gobierno_enjambre.py`):
- **Nivel 1 (Ejecución):** IAs ligeras (Gemini Flash) y scripts automatizados encargados del trabajo repetitivo (renderización, clasificación masiva).
- **Nivel 2 (Diseño y Desarrollo):** IAs avanzadas (Antigravity/Pro) junto con el humano, encargadas de definir el "Arte Pícaro", nuevas estéticas y creación de herramientas.
- **Nivel 3 (Arquitectura):** IAs complejas (Claude) para resolver deudas técnicas profundas y reestructuraciones de bases de datos registradas en el estado global.
- **Regla:** Ningún agente debe improvisar tareas fuera de su nivel. Toda deuda técnica pesada debe registrarse en la Nodriza en lugar de intentar forzarse.

## 4. ESTÉTICA Y ARTE PÍCARO (FFMPEG)
- **Arte Mixto y Emocional:** El contenido debe mezclar imágenes descargadas con generación de IA para lograr un nivel onírico, sugiriendo emociones basadas en los tránsitos astrológicos.
- **Prohibición de "Cuadrados":** Queda estrictamente prohibido usar filtros `overlay` planos que resulten en parches cuadrados duros. Todo collage debe tener fusión artística.
- **Uso de Máscaras Alfa (Feathering):** Al superponer imágenes en FFmpeg, es obligatorio usar canales alfa (como el filtro `geq` con degradados esféricos) para difuminar los bordes y lograr una integración orgánica con el fondo.
- **Comportamiento Asíncrono y Enlazado:** Las imágenes en collages deben turnarse asíncronamente (usando `enable='between(...)'`), entrelazarse creando puentes narrativos, con tamaños orgánicos y aplicando sutiles derivas cinéticas (`sin`/`cos`) y acercamientos (`zoompan`).

## 5. TONO NARRATIVO Y DIRECCIÓN DE ARTE
- **Enfoque Sociológico/Energético:** La astrología aquí no es predictiva ni para "ganar likes". Es una herramienta de mapa energético diario (un salto de fe probabilístico). El guion debe estar escrito para que incluso los escépticos lo encuentren asertivo y útil como acompañamiento psicológico/sociológico. Nunca hablar de un solo signo sin enmarcarlo en el clima general del cielo.
- **Dinámica Visual (Foreground vs Background):** El video NO debe ser una secuencia literal de imágenes estáticas. La base (Background) debe ser un universo dinámico/espacial continuo. Las imágenes (Foreground) de arte sugestivo/simbólico flotan por encima con transparencia basada en su score de afinidad.
- **Transiciones Inteligentes, NO genéricas:** Prohibido usar `zoomin` violento para todos los cortes. Las transiciones deben variar según el contenido:
   - **Vórtices (`zoomin`, `radial`):** Solo usar cuando se cambia de tema, entre tomas, o cuando hay planetas involucrados en el guion.
   - **Fade suave (`fade` / opacidad):** Para transiciones de imágenes dentro de la misma toma.

## 6. FLUJO DE TRABAJO MULTI-AGENTE (Gemini + Claude)
- **Centralización Absoluta:** TODO el código modificado debe respetar las rutas absolutas declaradas en `contexto_astrologico.json`. Prohibido hardcodear rutas temporales del workspace del agente.
- **División de Tareas (Gemini vs Claude):**
   - **Gemini (Nivel 2):** Encargado de Auditoría, Planificación (`implementation_plan.md`), revisión de Git, validación del formato narrativo, y preparación del entorno.
   - **Claude (Nivel 3):** Encargado de la refactorización profunda de código (FFmpeg, Python). Gemini debe preparar un archivo `HANDOFF_CLAUDE.md` con las instrucciones exactas, modularizadas en Hilos 1 y 2, y esperar a que Claude devuelva el código funcional.

## REGLAS DE ARQUITECTURA VISUAL (CÉLULA 2 Y 3)
1. **Compensación de xfade (tpad)**: En `ensamblador_final.py`, el uso de fundidos (`xfade`) consume tiempo matemático del video. SIEMPRE se debe calcular la diferencia entre el audio y el video final (`dur_faltante`) y aplicar un filtro `tpad=stop_mode=clone` al final del grafo para congelar el último frame y evitar que el video se corte antes que la locución.
2. **Heurística Sugestiva (Nodriza)**: La asignación de imágenes NUNCA debe ser aleatoria ni basarse solo en roles. `nodriza_visual.py` DEBE otorgar un puntaje masivo si los `tags` del catálogo coinciden directamente con las palabras clave del `texto` del guion, y debe otorgar un bono base al `elemento_visual` que coincida con el contexto astrológico del día (`ADN["arquetipos"]["elemento"]`).
