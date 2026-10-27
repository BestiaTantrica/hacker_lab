# 🛸 NAVE NODRIZA: BITÁCORA DE ESTADO GLOBAL
*Última actualización: 2026-10-15 23:45:00*

Este documento rige la coordinación de IAs en el ecosistema Astrology Factory.
**PROHIBIDO ROMPER EL ESQUEMA DE 3 NIVELES.**

---

## ⚡ NIVEL 1: EJECUCIÓN (IA: Gemini Flash / Scripts)
*Responsabilidad: Trabajos repetitivos, ejecución de comandos aprobados (Navaja Suiza), procesamiento masivo (ej. Clasificador de Videos).*

**Estado / Tareas Activas:**
- [ ] Descargar por tandas (1000 assets) para Octubre
- [x] **Aprobación de App TikTok (Producción)**: Resuelta la observación de consistencia de marca (*Brand Consistency*). Generados favicons multirresolución (`favicon.ico`, 32x32, 16x16, 180x180) y `app_icon.png` desde `logo_tiktok_1024.jpeg`. Integrados en `index.html`, `terms.html`, `privacy.html` y endpoint `/favicon.ico` en FastAPI. Desplegado en vivo en OCI-2 (`portaltarotmistico.com`) y solicitud reenviada a revisión con éxito.
- [ ] Procesar automatización de TikTok (En espera del veredicto final de revisión)

---

## 🛠️ NIVEL 2: DISEÑO Y DESARROLLO (IA: Antigravity / Pro + Humano)
*Responsabilidad: Creación de nuevas células, ajuste de estéticas (ej. Fusionador Visual), lógicas de negocio inmediatas.*

**Estado / Decisiones Actuales:**
- [x] **Ecosistema Web Tenebrista & Reloj Astrológico en Tiempo Real (`web_app/`)**:
  - **Rediseño Completo a Tenebrismo Oscuro (`#030408`)**: Se eliminó el fondo blanco/pastel antiguo; la web entera ahora corre sobre lienzo cósmico oscuro con partículas estelares sutiles en Canvas.
  - **Embudo de Conversión Progresivo en 2 Pasos**: Formulario dividido en Paso 1 (Identidad: Nombre + Email) y Paso 2 (Coordenadas: Fecha + Hora + Ciudad) para eliminar agobio de leads.
  - **Pasarela de Confianza Integrada**: Banner 15% OFF Transferencia Directa (`vida.rucula`) con copiado en 1 clic + pasarela Mercado Pago (cuotas, débito, QR) y PayPal internacional ($10 USD).
  - **Reloj Astrológico Universal Pro (`reloj_engine.js`)**:
    * Bisel horológico exterior de bronce con 24 Números Romanos (I a XII) estilo Astrolabio de Praga.
    * Orbes planetarios en 3D con iluminación especular, volumen metálico y penumbra tenebrista.
    * Hit-testing interactivo en hover/touch: retícula áurea telescópica y tooltips de cristal oscuro con datos reales (grado, casa, significados y aspectos activos).
    * Modo Wallpaper puro con auto-desvanecimiento tras 3.8s de inactividad, tecla `H` de inmersión y parámetro URL `?mode=wallpaper`.
  - **Video Diario & Cierre Comercial (`ensamblar_video_diario.py`)**: Guión con Gemini Flash Lite y regla sagrada en `ROLE_SCRIPTWRITER.md` para Toma 5 con CTA de venta directa a la bio/web.
- [ ] **Roadmap Pendiente para Próxima Sesión (Observaciones de Tomás)**:
  - [ ] **Evolución del Reloj Antiguo (Mecánica Analógica)**: Incorporar manecillas/agujas mecánicas de época (Sol / Luna / Tiempo) para que la lectura horaria analógica sea protagonista y relegar el reloj digital.
  - [ ] **Ergonomía de Textos e Inspector**: Asegurar que los tooltips y rótulos no tapen el orbe ni las líneas de aspectos (reubicación lateral / inspector HUD exterior).
  - [ ] **Definición de las 12 Casas**: Mayor contraste visual, trazos y nitidez en las cúspides de casas sobre el fondo animado.
  - [ ] **Sincronización a Producción OCI-2**: Empujar cambios auditados a `portaltarotmistico.com` vía rsync/ssh.
- [x] Limpieza de basura técnica V1 y deprecación de la Célula 3 (Mover scripts a `archived_legacy`).
- [x] Producto 1 (Carta Astral Premium): Arquitectura de aislamiento completada en `products/carta_natal/`.
- [x] Producto 2 (Revolución Solar en Video + Carta Astral): Pipeline integral completado en `products/revolucion_solar/`:
  - Cálculo de retorno exacto con Swiss Ephemeris (`calculador_revolucion_solar.py`).
  - Graficador Bi-Wheel espacial pedagógico en 16:9 con Ascendente natal fijo a 180° (`graficador_biwheel.py`).
  - Handoff y Guiones de Oro forjados con Claude High para Tomás y Messi (`ejemplos_oro/`).
  - Motor masivo de generación de guiones a costo cero con Gemini 3.8 Flash / Groq (`generador_guion_rs_produccion.py`).
  - Renderizador de video modular en micro-escenas TS y ensamble final sin recodificación (`video_maker_premium.py`), verificado con caso Camila (11.4 min en 1080p / 312 MB).
- [x] **Mejora del Motor Bi-Wheel y Zoom Dinámico (`products/revolucion_solar/`)**:
  - **Preservación Total del Mandala**: Se restauraron signos (alpha=0.38), 12 casas natales y de RS, planetas y red de aspectos completa para mantener 100% el contexto cósmico.
  - **Sistema de Enfoque Neón Aditivo**: Destello de halos concéntricos, mira telescópica (reticle lock) en coordenadas astronómicas exactas, aura de casas/portales y láser de aspectos de activación.
  - **Planetas como Gemas Radiantes**: Orbes celestes con halo atmosférico y micro-badges circulares de cristal oscuro para los 10 planetas natales (oro) y de RS (cian).
  - **Eliminación de Transiciones Redundantes y Coreografía Fija -> Zoom**:
    * Apertura de capítulo en **Plano General Fijo (1.0x)**: El espectador asimila toda la carta sin movimiento brusco.
    * Enfoques específicos por astro/casa: Paneo y zoom quirúrgico (1.0x -> 1.75x) centrado al píxel en `(cx, cy)`.
    * Paneles laterales disueltos en zoom: Los paneles explicativos están en la toma fija y se disuelven suavemente al acercarse la cámara, eliminando recortes toscos de texto.
  - **Espiral Temporal 3D ("Tirabuzón de Retornos Solares") (`animador_espiral_3d.py`)**:
    * Generador 3D a costo cero en Python/Matplotlib 3D/FFmpeg.
    * Conecta la Carta Natal en la base (Z=0, oro) con la Revolución Solar en la cima (Z=Top, cian) a través de una hélice de anillos temporales y haz de luz ascendente en hiperlapso (4.0s @ 25fps).
- [x] **Piedra Angular V3: Navegador Cinemático Vectorial Perfeccionado (`visor_cinematico/`)**:
  - **Corrección Angular y Desbloqueo de Acuario**: Resuelto el cálculo continuo de sectores zodiacales (eliminada la discontinuidad de módulo en 360°), visualizando con nitidez impecable el sector y glifo de Acuario en el horizonte izquierdo.
  - **Rótulos de Texto en los 12 Signos**: Integrados los nombres en mayúsculas (`♒ ACUARIO`, `♓ PISCIS`, `♈ ARIES`, etc.) con tipografía `Outfit` junto a glifos cromáticos ampliados (22px) con resplandor elemental.
  - **Ejes Cardinales y Ascendente Protagonistas**:
    * Eje Horizontal (180°): Línea dorada gruesa (3px) con badge flotante `◀ ASC: ♒ ACUARIO 21° 54'`.
    * Descendente (0°): Badge `DSC: ♌ LEO 21° 54' ▶`.
    * Medio Cielo (MC en Escorpio 16°40') y Fondo de Cielo (IC en Tauro 16°40') con líneas y badges dedicados.
  - **Agrandado y Legibilidad Máxima**:
    * Orbes planetarios ampliados a 22px de radio (dorados natales y cian RS) con glifos interiores a 20px bold.
    * Badges de nombre y grado agrandados a 12px bold con alto contraste.
    * Números de casas natales (1 a 12) enmarcados en chapas circulares nítidas de 12px bold.
  - **Líneas de Aspectos Euclidianos Vivas**: Aumentada la opacidad base a 0.40 (línea 1.6px) para que toda la geometría sagrada sea visible en reposo, manteniendo el resplandor neón concentrado al activarse o seleccionarse.
- [x] **Voz Humana Argentina / Rioplatense (`es-AR-TomasNeural`)**:
  - Eliminado el sintetizador robótico gallego.
  - Actualizado `edge-tts` a 7.3.1 y activada la voz argentina masculina de alta fidelidad `es-AR-TomasNeural` con cadencia reflexiva (`--rate=-3%`, `--pitch=-1Hz`) y silencios naturales respirables entre actos.
  - Master de audio del Capítulo 1 re-sintetizado con éxito (145.54 segundos) y sincronizado con `video_director.js`.
- [x] **Producción Cinemática de Metamorfosis (Luma Dream Machine + T2I 9:16)**:
  - Implementada arquitectura de 4 keyframes continuos por astro para generación en Luma multi-imagen (clips de 10s continuos sin zoom estático).
  - **Capítulo 1 (100%)**: Sol en Aries, Luna en Sagitario, Ascendente en Acuario (12 keyframes + 3 videos).
  - **Capítulo 2 (100%)**: Mercurio en Aries, Venus en Piscis, Marte en Libra + variante (13 keyframes + 3 videos).
  - **Capítulo 3 (100%)**: Júpiter en Escorpio, Saturno en Libra + variante stock (9 keyframes + 2 videos).
  - **Capítulo 4 (100%)**: Quirón en Tauro, Lilith en Sagitario, Nodos Lunares (12 keyframes + 3 videos).
  - **Capítulo 5 (100%)**: Urano en Sagitario, Neptuno en Sagitario, Plutón en Libra (12 keyframes + 3 videos).
  - **Capítulo 6 (100%)**: Medio Cielo en Escorpio (4 keyframes + 1 video).
  - **Capítulo 7 (100% Clímax)**: La Gran Oposición Eje 3-9 Sol/Mercurio vs Saturno/Plutón (4 keyframes + 1 video).
  - **CARTA NATAL DE TOMÁS 100% COMPLETADA EN BÓVEDA**: 66 imágenes curadas + 16 videos cinemáticos continuos de metamorfosis (160+ segundos continuos de metraje vertical 9:16).
- [x] **Robustez Total del Bot y Canal de Telegram (Producción OCI-2)**:
  - **Resolución de caída intermitente**: `daily_channel_job.py` refactorizado con 3 ciclos de reintento, rotación automática entre 10 API keys del `.env` y fallback entre modelos (`gemini-3.8-flash`, `3.6-flash`).
  - **Integración Nativa con Swiss Ephemeris (`clima_astral_engine.py`)**: Eliminada la "ceguera astronómica" de la IA. El sistema calcula en vivo la posición exacta de los 10 planetas, fase lunar (grados y arquetipo) y aspectos mayores con orbe estricto antes de redactar.
  - **Reforma Editorial de Autor (Cero Coaching de Peluquería)**: Erradicado el formato de autoayuda imperativa ("Auditá tus acuerdos", "no seas cobarde"). El reporte diario ahora es pedagógico, cartográfico y lúcido: 1) Mapa celeste real, 2) Mecánica y enseñanza de arquetipos, 3) Clima colectivo social, 4) Brújula del día.
  - **Horóscopo Personalizado con Casas Reales (`telegram_manager.py`)**: El botón interactivo `[ 🔮 Solicitar mi Horóscopo Personalizado ]` y el comando `/hoy` calculan la Carta Natal exacta del usuario (casas Placidus) y cruzan qué casas y planetas natales están siendo activados por los tránsitos del día con Swiss Ephemeris.
  - **Persistencia en SQLite**: Migrada la tabla `subscribers` con `telegram_id` y `telegram_username` permanentes (se eliminó la dependencia volátil de memoria RAM).
  - **Tolerancia a fallos y entrega diferida**: Creada la tabla `pending_telegram_requests` y el worker `retry_telegram_requests.py` (ejecutado cada 10 min en cron de OCI) para agendar y despachar automáticamente lecturas si la IA experimenta saturación temporal.
  - Servicio `telegrambot.service` actualizado y verificado en ejecución en OCI.
- [x] **Guía Maestra de Curaduría de Assets Astrológicos**:
  - Documento creado en `produccion/GUIA_CURADURIA_STOCK_ASTROLOGICO.md` con la taxonomía SSoT para SQLite (`img_abstracto_*`, `img_emocion_*`, `vid_*`), especificaciones de búsqueda por planeta/signo y prompts optimizados para animación I2V en Luma / Pixverse sin gastar APIs.
- [x] **Salto de Paradigma V3: El Glifo Maestro (Alfabeto Modular Astrológico)**:
  - Superado el modelo de combinatoria infinita rígida (fuerza bruta).
  - Documento canónico redactado en `produccion/ARQUITECTURA_GLIFO_MAESTRO_ALFABETO_MODULAR.md`.
  - Cobertura 100% de la astrología occidental en 45 arquetipos universales (90 imágenes maestras): 12 Astros, 4 Ángulos (con Ascendente como núcleo de encarnación), 12 Signos, 12 Casas y 5 Aspectos Mayores.
  - Fórmulas de composición y animación no reduccionistas que integran obligatoriamente la Casa terrenal y el Contexto Global del cielo.
  - Nueva identidad visual de autor ("Tenebrismo Figurativo Sagrado") inspirada en el realismo místico contemporáneo (Roberto Ferri, Caravaggio), eliminando el plástico y la sobresaturación digital de IA.
- [ ] **Hoja de Ruta Inmediata**:
  - [x] **Hito 100% Completado: El Glifo Maestro (135 Prompts Canónicos)**:
    - **Fase 1 (16 Arquetipos / 48 Prompts)** en `products/glifo_maestro/PROMPTS_FASE1_TRIPTICOS_GLIFO_MAESTRO.md`: 5 Astros Personales, 5 Transpersonales, 2 Puntos Kármicos (Quirón, Lilith) y 4 Ángulos Sagrados (ASC, DSC, MC, IC) con la regla del Tríptico (V1 Rostro/Torso, V2 Torsión/Espalda, V3 Gesto/Herida) bajo desnudo académico puro de Roberto Ferri.
    - **Fases 2, 3 y 4 (29 Arquetipos / 87 Prompts)** en `products/glifo_maestro/PROMPTS_FASE2_MACROCOSMOS_CASAS_ASPECTOS.md`:
      * 12 Signos Zodiacales (Macrocosmos elemental al óleo de betún, Caspar David Friedrich + Denis Villeneuve, cero personas).
      * 12 Casas Astrológicas (Arquitectura sacra tenebrista, brutalismo y Piranesi, monolitos de basalto y luz cenital).
      * 5 Aspectos Mayores (Geometría sagrada vincular, anatomía entrelazada estilo *Eros e Anteros* de Ferri).
  - [ ] **Siguiente Paso Crítico**: Renderizado y Curaduría de Imágenes en FLUX.1 [dev] (arrancando por el Bloque 1: Sol, Luna, Mercurio, Venus, Marte y Ascendente).
  - [ ] **Montaje y Renderizado**: Integrar los 16 clips cinemáticos de la Carta Natal de Tomás y preparar el pipeline de animación I2V con el Glifo.




---

## 🧠 NIVEL 3: ARQUITECTURA PROFUNDA (IA: Claude)
*Responsabilidad: Resolución de deudas técnicas masivas, problemas de catalogación/curaduría compleja o re-estructuración de la base de datos.*

**Deudas Técnicas Pendientes (Handoff preparado):**
- [x] TAREA 1: Arquitectura de la Base de Datos Visual (SQLite). **[COMPLETADO]**
- [x] TAREA 2: Refactorización Inteligente de la Célula 2 y Single-Pass en FFmpeg. **[COMPLETADO]**
- [ ] TAREA 3: Integración de la Célula Acuñadora (Tokenización Web3 / IPFS).
- [x] TAREA 4 (PREMIUM): Soporte de "Chunking" y creación de `video_maker_premium.py` para videos de 10-15 min sin saturación de memoria. **[COMPLETADO]**
- [x] TAREA 5 (PREMIUM): Motor de producción narrativa modular en 6 capítulos para Revolución Solar (`generador_guion_rs_produccion.py`). **[COMPLETADO]**

---

## 📌 PAUTAS CRÍTICAS DE REDISEÑO (FEEDBACK TOMÁS - 15/10/2026)
1. **Rigor Astrológico en Líneas de Aspectos**:
   - Las líneas son RECTAS euclidianas (cuerdas entre planetas), NUNCA curvas senoidales.
   - En reposo deben ser suaves para no saturar; solo se iluminan con fuerza los aspectos activos que el locutor menciona.
2. **Planetas Grandes y con Glifos Claros**:
   - No más puntos minúsculos. Deben ser orbes celestes de gran tamaño con sus símbolos (☉, ☽, ☿, ♀, etc.) y grados legibles.
3. **Limpieza del Fondo**:
   - Eliminar el sembrado aleatorio de puntos blancos (estrellas falsas) que ensucian la lectura técnica de los grados y casas.
4. **Continuidad Dinámica (Sin Cortes Bruscos de Diapositiva)**:
   - Eliminar el pegado tosco de clips estáticos o espirales aislados.
   - La animación debe ser un viaje continuo: parte de la Carta Natal -> los planetas transitan y giran describiendo el paso de los años -> se acopla el anillo exterior de la Revolución Solar 2026.
   - La cámara viaja fluidamente (zoom cinematográfico continuo) hacia la Casa 9 / Ascendente en Libra SIN borrar el resto de la carta (el mandala completo permanece vivo en el fondo).
5. **Títulos Flotantes Minimalistas**:
   - Cero carteles gigantescos o parrafadas de informe. Solo badges flotantes elegantes y grandes con fundido suave (`fade-in/out`), sincronizados al relato oral.
