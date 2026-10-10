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
4. **CUOTA DE API (FRENO OBLIGATORIO):**
   - TODO script que interactúe con la API de Gemini DEBE importar y usar `v2/cuota.py`. Queda estrictamente prohibido usar clientes nativos de forma aislada o hacer peticiones en bucle sin control. `cuota.py` maneja las pausas (429 Too Many Requests), rota las llaves del `.env` y usa locks multiproceso. Usa siempre `cuota.elegir_key()` y `cuota.esperar_ritmo()`.

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
- **Arte Mixto y Emocional (Generación Dual):** El contenido debe mezclar imágenes descargadas con generación de IA para lograr un nivel onírico. Toda generación de IA debe cubrir dos vertientes:
   1. *Abismo Cósmico (Background)*: Representaciones fluidas para el fondo (`13_Abstracto_Fluidos`).
   2. *Reacción Humana (Foreground)*: Sátiras o representaciones psicológicas para el primer plano (`11_Humanos_Emociones`), encadenadas con `xfade` cuando el guion refiera emociones.
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
## 7. REGLAS DE GENERACIÓN DE CONTENIDO ASTROLÓGICO (EL CEREBRO Y EL CORAZÓN)
1. **La Verdad Astrológica (Motor de Efemérides):** La IA (Célula 1) NUNCA debe inventar significados de tránsitos. Debe cruzar obligatoriamente los cálculos matemáticos de `pyswisseph` con el Oráculo centralizado (`astrology_engine/lexico_astrologico.json`). El Léxico manda sobre cualquier dato preconcebido de la IA.
2. **Tono de Traducción (Masa + Técnica):** El guionista de la Célula 1 actúa como un puente empático. Debe explicar el clima astral de manera visceral (cómo se siente en el cuerpo y la calle), pero **DEBE incluir referencias técnicas sutiles** (Ej: Nombrar explícitamente "Esta Cuadratura entre la Luna y Plutón...") para no perder la profundidad astrológica.
3. **El Pulmón Recolector (Daemon):** La recolección de videos (Pexels) y la generación de arte sintético (Gemini -> Pollinations.ai) corren en un daemon unificado (`pulmon_recolector.py`). Este proceso debe dormir 30 minutos por ciclo para no quemar las APIs ni colapsar la Bóveda.
4. **Arte Sintético:** Todo arte generado por la IA debe llevar el prefijo `arte_propio_` y enviarse obligatoriamente a `/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/` en sus respectivas categorías (`13_Abstracto_Fluidos` o `11_Humanos_Emociones`).

## 8. DIRECTRICES ARQUITECTÓNICAS V2 (SINGLE-PASS Y SSOT)
1. **Single-Pass Rendering (FFmpeg)**: Prohibido el pre-renderizado de assets (transmutar JPGs a MP4 temporalmente). Las imágenes estáticas deben enviarse crudas (rutas absolutas) al renderizador final (`video_maker.py`). Cualquier efecto de movimiento (ej. Ken Burns / `zoompan`) debe aplicarse dinámicamente ("al vuelo") dentro del `filter_complex` en el comando FFmpeg final.
2. **Base de Datos Visual como "Single Source of Truth" (SSoT)**: Cero lecturas ciegas al sistema de archivos. Todo script que necesite assets visuales debe consultarlos exclusivamente a través de la base de datos SQLite (`assets_visuales.db` gestionada por `db_visual.py`). El motor de renderizado (`video_maker.py`) es "tonto": no elige assets por heurística ni `glob`, solo obedece las rutas absolutas indicadas en el archivo JSON de corte validado.
