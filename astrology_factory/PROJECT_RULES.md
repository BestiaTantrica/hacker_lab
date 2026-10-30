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
- **Nivel 1 (Ejecución):** IAs ligeras (Gemini Flash, edge-tts, scripts Python/FFmpeg) encargadas del trabajo masivo y repetitivo a costo cero.
- **Nivel 2 (Diseño y Desarrollo):** IAs intermedias/avanzadas (Antigravity IDE / Gemini Pro) junto con el humano, encargadas de orquestar, integrar componentes, auditar entornos y mantener la web y pipelines corriendo.
- **Nivel 3 (Arquitectura Sagrada & Moldes de Oro - Claude Pro):** 
  * **PROHIBICIÓN ESTRICTA:** Queda TERMINANTEMENTE PROHIBIDO gastar tokens de Claude Pro en revisar tránsitos diarios, auditar tareas de rutina o tareas que Swiss Ephemeris / Gemini Flash resuelven en Nivel 1.
  * **ROL EXCLUSIVO DE CLAUDE PRO (CERO TOKENS DESPERDICIADOS):**
    1. **Forjar MODELOS DE ORO CANÓNICOS (Few-Shot Golden Datasets):** Crear una única vez los moldes maestros perfectos de guiones y narrativas (como los 3 guiones de oro en `ejemplos_oro_diarios.json` o los de Revolución Solar de Tomás/Messi) para que los modelos de producción los imiten indefinidamente.
    2. **Ingeniería de PRECISIÓN MILITAR / CERO ERROR:** Programar exclusivamente los módulos donde un fallo destruye dinero o seguridad: Webhook criptográfico de Mercado Pago (firmas HMAC SHA-256, idempotencia estricta en SQLite contra dobles cobros o confirmaciones falsas), Shaders GLSL para WebGL 3D (Esfera Armilar) y calibración analítica de alta matemática.

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
   - **Gemini (Nivel 2):** Encargado de Auditoría, Planificación, revisión de Git, validación del formato narrativo, ejecución de pipelines y preparación del entorno.
   - **Claude (Nivel 3):** Encargado EXCLUSIVAMENTE de forjar moldes maestros (Guiones de Oro) y código de infraestructura crítica de CERO ERROR (Mercado Pago Webhook, Shaders GLSL 3D). NUNCA para revisión de tránsitos cotidianos.

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


## 9. PUBLICACIÓN EN TIKTOK (ESTRATEGIA CANÓNICA: COOKIES / AUTOMATION)
1. **Estrategia Primaria Operativa (Cookies Web Automation)**:
   - Se utiliza **Automatización Web (`cookies.txt` / Playwright)** para subir borradores o videos finales.
   - **Causa Mandatoria:** La API V2 en modo Inbox (`SEND_TO_USER_INBOX`) no traslada títulos ni descripciones, obligando a redactar a mano en el celular. La subida vía web con cookies garantiza inyección 100% automatizada de título, descripción completa y hashtags.
2. **TikTok Developer API (En Revisión)**:
   - Mantener el registro de la app en TikTok Developer Console únicamente para obtener aprobación de `Direct Post` (`video.publish`) en producción.
   - Mientras la app permanezca sin auditar o limitada a Sandbox, la vía de producción diaria es la automatización por cookies.
3. **Integración Obligatoria del Reloj 2D en Videos Diarios**:
   - Todo video de tránsito futuro debe incorporar al menos 1 o 2 tomas del Reloj Astrológico 2D (`web_app/templates/reloj.html`) con zooms sutiles a los planetas y aspectos en conflicto/armonía, cumpliendo triple función: didáctica astral clara, branding orgánico y ahorro de cuotas de generación de imágenes IA.


## 10. PRODUCTOS PREMIUM Y LECTURAS ASTRALES (CARTA NATAL / REVOLUCIÓN SOLAR)

1. **Aislamiento Estricto por Producto (Zero-Mixing)**:
   - Cada producto comercial reside de forma autónoma en `products/<nombre_producto>/` (ej: `products/carta_natal/`).
   - PROHIBIDO cruzar o importar scripts, vademécums o historiales de videos diarios dentro de los generadores de cartas natales o reportes escritos.

2. **ADN del Autor y Tono de Redacción (Regla Tomás)**:
   - La carta natal de Tomás (Aries/Acuario/Sagitario) es el **sistema operativo de redacción**: directo al hueso, lúcido, pedagógico, enérgico y con voseo argentino maduro.
   - **Estructura Didáctica Obligatoria**: Todo astro y casa debe explicarse bajo la tríada: *qué es, cómo funciona y por qué* (educar al consultante antes de interpretar).
   - **PROHIBIDO el Humo y la Cursilería**: Vetado terminantemente el lenguaje new-age barroco ("mar primordial", "carro lunar", "códice cósmico").
   - **PROHIBIDA la Sinastría con el Autor**: El autor jamás menciona sus propios planetas ni se compara con el consultante. Su carta es su motor interno de mirada.
   - **PROHIBIDO Prohibir Temas**: No censurar temas de la vida real (dinero, cuerpo, relaciones, profesión). Se abordan con psicología profunda y sin conjeturas baratas de horóscopo.

3. **Arquitectura Híbrida "Gold Standard" (Claude + APIs Producción)**:
   - **Matemática y Gráficos (100% Python determinístico, costo $0)**: Swiss Ephemeris (`swisseph`) para posiciones, casas Placidus y aspectos. Ruedas en Matplotlib con **Ascendente fijo a la izquierda (180° / 9 en punto)**, aspectos en el centro y fondo espacial.
   - **Claude como Arquitecto / Molde de Oro**: Se utiliza a Claude para forjar los reportes de referencia (`ejemplos_oro/`).
   - **APIs de Producción (Gemini 3.8 / Groq 120b)**: Generan los pedidos individuales de clientes inyectando los ejemplos de Claude como Few-Shot, logrando calidad de autor a costo y tiempo mínimos.

4. **Visualización de Gráficos en Markdown**:
   - Todo render o imagen de rueda incrustada en reportes Markdown DEBE usar rutas absolutas (`![caption](/home/tomas2/.../imagen.png)`). Las rutas relativas no resuelven en la interfaz y rompen la experiencia de usuario.

5. **Generación Modular por Capítulos (Chunking de Alta Resolución sin Cortes)**:
   - Para reportes extensos de 10 páginas (~4.000 a 5.000 palabras), la redacción por IA NUNCA debe ejecutarse en una sola llamada ni en bloques amontonados de 4 capítulos.
   - Debe dividirse en 5 o 6 llamadas modulares y consecutivas (Preliminares/Estructura, Trinidad de Identidad, Planetas Personales, Estructura Social/Kármica, Fuerzas Transpersonales/Vocación, Geometría de Aspectos y Cierre).
   - Esto evita recortes por límites de tokens de salida (`MAX_TOKENS`), garantiza profundidad analítica y respeta la pedagogía de cada sección sin apurar ni resumir la conclusión.

6. **Cálculo de Revolución Solar: Doble Geocodificación Obligatoria**:
   - Todo cálculo de Revolución Solar (Retorno Solar) exige estrictamente dos conjuntos de coordenadas geográficas independientes:
     1) `coordenadas_natales` (latitud, longitud, fecha, hora natal): determinan la Carta Natal base y el grado zodiacal exacto al que debe retornar el Sol al segundo de arco.
     2) `coordenadas_retorno` (latitud, longitud, ciudad y huso horario del lugar donde la persona se encuentra físicamente al momento de su retorno): determinan el Ascendente anual, el Medio Cielo anual y las 12 Casas Placidus de la Revolución Solar.
   - **Regla de Formulario/Producto**: Los formularios de compra y APIs del producto deben solicitar obligatoriamente tanto el lugar de nacimiento como la ciudad de cumpleaños/residencia para ese año. Prohibido asumir que la persona pasa su retorno en la ciudad natal sin confirmación expresa.

7. **Invariante de Renderizado UI (Prevención de Glitches LaTeX)**:
   - PROHIBIDO el uso del signo de dólar `$` suelto en respuestas de texto o documentación (ej: precios o costos). En la interfaz de Antigravity, el signo de dólar activa el modo de fórmulas matemáticas de LaTeX (`$...$`), colapsando espacios, comprimiendo tipografía en cursiva y provocando parpadeos/saltos de pantalla molestos para el usuario. Escribir siempre: `0 USD`, `costo cero`, `gratuito` o escaparlo estrictamente como `\$`.

8. **Pedagogía Audiovisual en Videos de Revolución Solar (Iluminación Dinámica)**:
   - En informes escritos (PDF/Markdown), las leyendas de texto explicativas al pie son útiles para lectura pausada. En el formato de **video (10-15 minutos)**, los textos estáticos pequeños son ilegibles y saturan al espectador.
   - En el renderizador de video (`video_maker_premium.py`), la pedagogía de la rueda Bi-Wheel se implementa mediante **iluminación focalizada y contraste dinámico**:
     * Al explicar el Ascendente anual (el portal), la rueda atenúa el fondo y hace brillar en cian fluorescente únicamente la flecha marcadora y la Casa Natal sobre la que aterriza.
     * Al analizar un aspecto mayor (ej: cuadratura u oposición), la rueda entra en penumbra y se ilumina exclusivamente la cuerda que une ambos planetas.

9. **Roadmap Futuro: Visor Astrológico Interactivo (Web3 / App)**:
   - Se establece en la arquitectura de Astrology Factory la creación futura de un **Visor Web Interactivo** donde el consultante pueda explorar su rueda Bi-Wheel dinámicamente, posando el cursor o tocando cada planeta o aspecto para desplegar la interpretación psicológica en tiempo real.

11. **Curaduría Audiovisual Dirigida y Edición Cinematográfica de la Rueda (Revolución Solar)**:
    - **Estado (2026-10-12)**: El pipeline técnico funciona end-to-end (video de 11.4 min en 1080p verificado), pero la edición es rígida y el stock es genérico o insuficiente. Es la deuda prioritaria del producto.
    - **La rueda nunca se muestra estática y completa durante más de unos segundos**: mostrar el gráfico entero repetidas veces no aclara nada y mata la estética. Cada aparición debe tener:
      1. *Zoom dirigido* (Ken Burns hacia coordenadas calculadas) sobre el sector, planeta, casa o cuerda del que habla la locución en ese momento.
      2. *Resaltado selectivo*: la cuerda de aspecto o el planeta en cuestión brilla (grosor/color/glow) y el resto de la rueda queda en penumbra.
      3. *Etiqueta grande y breve* en pantalla (ej. "Saturno RS en cuadratura al Sol natal"), legible en TV y móvil; nunca texto chico.
    - **Implementación preferida (costo cero)**: Matplotlib ya conoce las coordenadas exactas de cada planeta, casa y cuerda. Generar variantes PNG por foco (rueda atenuada + elemento resaltado) y animar el zoom con `zoompan`/crop de FFmpeg hacia esas coordenadas. El foco se elige según las menciones de planetas y aspectos en cada tramo del guion.
    - **Stock**: queda vetada la selección aleatoria por carpeta cuando la locución aborda metáforas concretas (fragua, cuerpo, pactos, dinero, límites). Mapear escena con asset de forma semántica y enriquecer la Bóveda con piezas dirigidas (T2I/I2V) por arquetipo de casa y planeta.
    - **Ritmo**: duración variable de planos, disoluciones suaves (`xfade`) y movimiento continuo para sostener 12 a 15 minutos de atención.

10. **Invariante de Estabilidad en Pipelines y Procesos Activos**:
    - PROHIBIDO modificar parámetros internos, cuotas, ratios o lógica de scripts operativos (como `vault_scraper.py`, `video_maker.py`, etc.) sin instrucción explícita del usuario.
    - Cuando el usuario indique "reanudar", "seguir descargando" o "encargarse", el agente debe limitarse a verificar el estado, reiniciar procesos caídos o ejecutar el flujo con la configuración vigente, sin alterar el código fuente.
