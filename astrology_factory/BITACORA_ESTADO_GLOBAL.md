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
  - **Rediseño Completo a Tenebrismo Oscuro (`#030408`)**: Se eliminó el fondo blanco/pastel antiguo; la web entera ahora corre sobre lienzo cósmico oscuro con orbe vivo en el fondo.
  - **Catálogo Oficial Segmentado en 3 Productos (Cotización $1.560 ARS = 1 USD)**:
    1. 📜 **Carta Natal Profunda + Oráculo IA** ($4.990 ARS / ~$3.20 USD | Transf: $4.240 ARS): PDF de 35+ págs + oráculo interactivo.
    2. ⏱ **Reloj Astrológico Vivo 4K Live Wallpaper** ($2.990 ARS / ~$1.90 USD | Transf: $2.540 ARS): Astrolabio en tiempo real geolocalizado con efemérides autónomas en JS para PC y móvil.
    3. 🎬 **Revolución Solar Cinemática en Video** ($14.990 ARS / ~$9.60 USD | Transf: $12.740 ARS): Película oracular de 10-15 min con voz hipnótica y el orbe proyectando los 12 meses de tu año personal.
    * 👑 **Tríada Sagrada Completa (Combo 3 en 1)**: $16.990 ARS / ~$10.90 USD | Transf: $14.440 ARS (Ahorro del 30%).
  - **Flujo de Pago y Entrega Automatizada 24/7 (Sin Trabajo Manual)**:
    * Eliminada la promesa de "10 minutos":
    * **Carta Natal y Reloj Wallpaper**: Activación inmediata y automática 24/7 (0 segundos de espera, validado por Mercado Pago/email).
    * **Revolución Solar en Video**: Plazo de 24 a 48 hs para renderizado cinematográfico 4K dedicado (percepción de artesanía de alta gama).
  - **Inyección de Guiones de Oro Canónicos (Claude Pro) en Célula 1 (`v2/celula_1/`)**:
    * Auditoría geométrica y poética realizada por Claude Pro para los 3 arquetipos canónicos:
      1. *ORO_1 (Tensión y Fuego)*: Oposición Marte Cáncer - Plutón Capricornio (180°).
      2. *ORO_2 (Marea Psicológica y Agua)*: Conjunción Luna - Neptuno en Piscis (0°).
      3. *ORO_3 (Estructura y Límite de Tierra)*: Trígono Mercurio Virgo - Saturno Capricornio (120°).
    * Archivados en `v2/celula_1/ejemplos_oro_diarios.json` e inyectados como *Few-Shot Learning* en `v2/celula_1/generador_guiones.py`.
    * Garantía de matemática estricta: Swiss Ephemeris en C (`pyswisseph`) calcula y valida todos los aspectos en producción antes de pasárselos a la IA.
  - **Planificación Reloj 3D Pro (Esfera Armilar 3D)**:
    * Se definió arquitectura WebGL / Three.js con materiales PBR (bronce y oro) y cámara 360° libre, ejecutada 100% en el cliente (0% de carga en el servidor Oracle Free Tier). Previsto selector `[ 2D Clásico | 3D Esfera Armilar ]`.
  - **Mecánica Horológica de Escape & Destellos por Vuelta (`reloj_engine.js`)**:
    * **Partículas Cósmicas Exclusivamente Exteriores**: 220 partículas en 3 capas de profundidad que orbitan únicamente fuera del orbe (`r >= 555px`), sin atravesar jamás el mandala sagrado.
    * **Rayos Horológicos Notorios**: Hilos sagrados de bronce y oro de 1.8px conectando el centro `⊕` con los carriles exteriores con fulgor translúcido.
    * **Chimes de Vuelta Completa**: Al segundo 60 el carril de segundos destella y la gema de minutos avanza con un pulso áureo; a los 60 min el carril de minutos pulsa y el medallón de horas emite una corona solar; a las 00:00 h se dispara una onda de choque luminosa por todos los carriles.
    * **12 Casas Enriquecidas**: Sombreado de sectores y cuadrantes tenebristas, cúspides con oropel y gemas de remate, y medallones con números romanos en tipografía Cinzel.
    * **Arquitectura de las 4 Esquinas Libres**: Inspector cósmico anclado en esquina inferior izquierda, reloj digital en esquina superior derecha, y responsive adaptado para laptops (`max-height: 720px`).
  - **Video Diario & Cierre Comercial (`ensamblar_video_diario.py`)**: Guión con Gemini Flash Lite y regla sagrada en `ROLE_SCRIPTWRITER.md` para Toma 5 con CTA de venta directa a la bio/web.
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

---

## 🌟 HITO ALCANZADO (27/10/2026): REDISEÑO TENEBRISTA SACRO DEL RELOJ CÓSMICO & ORBE PERMANENTE
- [x] **Geocentrismo Alquímico & Centro 100% Despejado**:
  - Eliminado el disco opaco de 130px que tapaba el cruce de aspectos y confundía el centro con el Sol.
  - El centro ahora es el **Punto Cero del Observador / La Tierra `⊕`** en radio de 28px, semi-traslúcido y etéreo. El cruce sagrado de las líneas de aspectos euclidianos (trígonos, cuadraturas, oposiciones, sextiles) queda 100% visible y limpio.
- [x] **3 Carriles Exteriores Horológicos (Horas, Minutos, Segundos)**:
  - Implementados 3 carriles concéntricos en el perímetro exterior del orbe (`radii.trackHours`, `trackMinutes`, `trackSeconds`):
    * Carril Horas (24h): Pista de bronce antiguo con arco de carga áureo y medallón alquímico.
    * Carril Minutos (60m): Pista de plata envejecida y cobre con barra de oro bruñido y prisma romboide.
    * Carril Segundos (60s): Barrido continuo ultra fluido a 60fps con estela de cometa y chispa ámbar resplandeciente.
    * Escala horaria exterior grabada con 24 números romanos en Cinzel.
    * Tres hilos o rayos etéreos tenues que viajan desde el centro por debajo de todo el mandala hacia los tres marcadores de tiempo.
- [x] **Arquitectura de las 4 Esquinas Libres**:
  - Mandala 100% libre de tarjetas o tooltips flotantes sobre el centro.
  - *Top-Left:* Glifo Maestro, Marca y Coordenadas GPS del observador.
  - *Top-Right:* Reloj Digital Sideral, Fecha y Botones de acción (Inmersivo, Wallpaper, Portal).
  - *Bottom-Left:* **Astro-Inspector HUD** (tarjeta fija de cristal ahumado sacro que proyecta los datos del astro o casa seleccionada sin tapar el orbe).
  - *Bottom-Right:* Controles compactos (Play/Pausa, Hora actual, saltos -1h/+1h, velocidad 1x/60x/3600x, selector de fondo y botón `⟲ 1.0x` para reset de cámara).
- [x] **Cámara Virtual Interactiva (Zoom & Pan en Canvas)**:
  - Zoom nativo en canvas mediante rueda del ratón (`wheel`) de 0.55x a 4.5x centrado en coordenadas del cursor.
  - Arrastre y paneo libre con mouse (`mousedown` / `mousemove` / `mouseup`).
  - Hit-testing transformado matemáticamente para mantener precisión de selección con cualquier nivel de zoom.
- [x] **Viaje Estelar Cósmico en 3 Capas de Profundidad**:
  - Sistema de 160 partículas cósmicas: polvo nebular profundo, estrellas guía parpadeantes y chispas ámbar veloces con difracción óptica en cruz.
- [x] **El Orbe Alquímico como Fondo Omnipresente de la Web (`index.html`)**:
  - El orbe y reloj cósmico en vivo es ahora el fondo omnipresente en pantalla completa detrás de toda la navegación.
  - Efecto de cámara cósmica dinámica: al scrollear o enfocar formularios/modales, el orbe retrocede sutilmente (`scale: 0.85; opacity: 0.38; filter: blur(1.5px)`) superponiendo las tarjetas de cristal ahumado sacro sin salirse nunca de la experiencia.

---

## 🛡️ PROTOCOLO DE AUDITORÍA PERIÓDICA CON CLAUDE PRO (CALIDAD, SEGURIDAD & MATEMÁTICA)
*Propósito: Revisiones sistemáticas para blindar la plataforma contra fallos de seguridad, derivas matemáticas o degradación de calidad antes de escalar en producción.*

### 1. Auditoría Matemática de Precisión Astronómica (Swiss Ephemeris vs Kepler)
- **Situación:** El reloj visual en JS usa aproximaciones keplerianas refinadas (~0.05° a 0.2° de desviación), ideales para 60 FPS en el navegador sin lag.
- **Misión Claude Pro:** Contrastar periódicamente las salidas de coordenadas del motor JS frente a `pyswisseph` (Swiss Ephemeris oficial de NASA/Astrodienst en Python) y formular tablas de calibración o factores de corrección periódica para garantizar certificación astrológica profesional.

### 2. Auditoría de Seguridad y Resiliencia en Pagos (Mercado Pago & Webhooks)
- **Situación:** Integrado alias oficial (`vida.rucula`, 15% OFF) y pasarela automática de Mercado Pago para tarjetas y cuotas 24/7.
- **Misión Claude Pro:** Auditar el endpoint webhook en FastAPI (`web_app/main.py`) verificando:
  * Validación criptográfica de firmas HMAC (`x-signature` con `x-request-id` y clave secreta de webhook).
  * Control estricto de idempotencia en SQLite (evitar ataques de repetición o dobles activaciones).
  * Blindaje contra spoofing y confirmaciones fraudulentas de pago.

### 3. Evolución Gráfica a WebGL / Shaders GLSL (Fase Astrolabio 3D Pro)
- **Situación:** Motor 2D en Canvas optimizado al máximo nivel vectorial tenebrista.
- **Misión Claude Pro:** Redacción y optimización de Vertex y Fragment Shaders en GLSL para Three.js:
  * Materiales PBR metálicos (bronce envejecido, oro bruñido y pátina oscura).
  * Refracción de lente y profundidad de campo (DoF) cósmica sin penalizar la GPU.
  * Mantener 60-120 FPS sin consumo de CPU en el servidor ni calentamiento en el cliente.

