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
  - **Preservación Total del Mandala**: Se restauraron signos (alpha=0.38), 12 casas natales y de RS, glifos de planetas y red de aspectos completa para mantener 100% el contexto cósmico.
  - **Sistema de Enfoque Neón Aditivo**: Destello de halos concéntricos, mira telescópica (reticle lock) en coordenadas astronómicas exactas, aura de casas/portales y láser de aspectos de activación.
  - **Blend Progresivo y Zoom Profundo (1.0x -> 1.75x)**: Generación pareada `solo_base` y `foco` para evitar ghosting de títulos; encendido cinemático con zoom dirigido a coordenadas (cx, cy).
- [ ] **Hoja de Ruta Inmediata (Próxima Sesión)**:
  - **Coreografía de Cámara y Sincronización con Guion**: Eliminar micro-cortes y transiciones innecesarias. Al inicio del capítulo el plano es fijo (1.0x) para asimilar el mandala completo; luego realiza paneo/zoom quirúrgico al punto exacto cuando el audio lo nombra.
  - **Espiral Temporal 3D ("Tirabuzón de Retornos Solares")**: Prototipar animación en espiral/hélice temporal desde la carta natal (Z=0) subiendo año a año hasta la Revolución Solar actual para dar profundidad y volumen visual.
  - **Vitalidad Planetaria y Placer Visual**: Pulsos sutiles en los glifos activos, partículas de energía sobre los aspectos láser y HUD estelar limpio.

---

## 🧠 NIVEL 3: ARQUITECTURA PROFUNDA (IA: Claude)
*Responsabilidad: Resolución de deudas técnicas masivas, problemas de catalogación/curaduría compleja o re-estructuración de la base de datos.*

**Deudas Técnicas Pendientes (Handoff preparado):**
- [x] TAREA 1: Arquitectura de la Base de Datos Visual (SQLite). **[COMPLETADO]**
- [x] TAREA 2: Refactorización Inteligente de la Célula 2 y Single-Pass en FFmpeg. **[COMPLETADO]**
- [ ] TAREA 3: Integración de la Célula Acuñadora (Tokenización Web3 / IPFS).
- [x] TAREA 4 (PREMIUM): Soporte de "Chunking" y creación de `video_maker_premium.py` para videos de 10-15 min sin saturación de memoria. **[COMPLETADO]**
- [x] TAREA 5 (PREMIUM): Motor de producción narrativa modular en 6 capítulos para Revolución Solar (`generador_guion_rs_produccion.py`). **[COMPLETADO]**
