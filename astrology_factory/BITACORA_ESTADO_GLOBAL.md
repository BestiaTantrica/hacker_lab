# 🛸 NAVE NODRIZA: BITÁCORA DE ESTADO GLOBAL
*Última actualización: 2026-10-11 22:20:00*

Este documento rige la coordinación de IAs en el ecosistema Astrology Factory.
**PROHIBIDO ROMPER EL ESQUEMA DE 3 NIVELES.**

---

## ⚡ NIVEL 1: EJECUCIÓN (IA: Gemini Flash / Scripts)
*Responsabilidad: Trabajos repetitivos, ejecución de comandos aprobados (Navaja Suiza), procesamiento masivo (ej. Clasificador de Videos).*

**Estado / Tareas Activas:**
- [ ] Descargar por tandas (1000 assets) para Octubre
- [ ] Procesar automatización de TikTok (En espera de aprobación)

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
- [ ] **Hoja de Ruta Inmediata**:
  - Sincronización fina de los paneos con las marcas de tiempo exactas del audio (Whisper/Edge-TTS).
  - Integrar la espiral 3D como obertura introductoria antes del Capítulo 1 en el render final.

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
