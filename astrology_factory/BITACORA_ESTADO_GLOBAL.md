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
  - Total archivado y validado en Bóveda: 46 imágenes + 11 videos cinemáticos (110+ segundos continuos).
- [x] **Robustez Total del Bot y Canal de Telegram (Producción OCI-2)**:
  - **Resolución de caída intermitente**: `daily_channel_job.py` refactorizado con 3 ciclos de reintento, rotación automática entre 6 API keys del `.env` y fallback entre modelos (`gemini-2.5-flash`, `3.8-flash`, `3.6-flash`).
  - **Botón Inline de Personalización**: Cada reporte diario en el canal público ahora incluye el botón con deep-link `[ 🔮 Solicitar mi Horóscopo Personalizado ]` hacia `https://t.me/PortalTarotBot?start=horoscopo_hoy`.
  - **Persistencia en SQLite**: Migrada la tabla `subscribers` con `telegram_id` y `telegram_username` permanentes (se eliminó la dependencia volátil de memoria RAM).
  - **Tolerancia a fallos y entrega diferida**: Creada la tabla `pending_telegram_requests` y el worker `retry_telegram_requests.py` (ejecutado cada 10 min en cron de OCI) para agendar y despachar automáticamente lecturas si la IA experimenta saturación temporal.
  - Servicio `telegrambot.service` actualizado y verificado en ejecución en OCI.
- [x] **Guía Maestra de Curaduría de Assets Astrológicos**:
  - Documento creado en `produccion/GUIA_CURADURIA_STOCK_ASTROLOGICO.md` con la taxonomía SSoT para SQLite (`img_abstracto_*`, `img_emocion_*`, `vid_*`), especificaciones de búsqueda por planeta/signo y prompts optimizados para animación I2V en Luma / Pixverse sin gastar APIs.
- [ ] **Hoja de Ruta Inmediata**:
  - Iniciar **Capítulo 5: Los Dioses del Cambio y la Transformación Transpersonal** (Urano en Sagitario C10, Neptuno en Sagitario C10, Plutón en Libra C8/C9).
  - Continuar con Capítulo 6 (Medio Cielo en Escorpio) y Capítulo 7 (La Gran Oposición Sol/Mercurio vs Saturno/Plutón).
  - Integración de los clips e imágenes sugestivas/transiciones en el pipeline de renderizado y montaje final.
  - Extender la coreografía de navegación a los Capítulos 2 a 6.




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
