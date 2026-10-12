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
- [x] Motor matemático (Swiss Ephemeris) y graficador de rueda profesional (Matplotlib con Ascendente en 180° y aspectos).
- [x] Estándar de Oro (Few-Shot) generado con Claude para Tomás y Messi (`ejemplos_oro/`).
- [x] Motor de producción automatizado en `generador_carta_natal.py` con arquitectura modular en 6 bloques (~10 páginas sin riesgo de recortes ni degradación).
- [x] Incorporación formal de la Sección 10 en `PROJECT_RULES.md` vía `/learn` (Invariantes de calidad, tono pedagógico de autor, cero sinastría, rutas absolutas para imágenes y chunking modular).

---

## 🧠 NIVEL 3: ARQUITECTURA PROFUNDA (IA: Claude)
*Responsabilidad: Resolución de deudas técnicas masivas, problemas de catalogación/curaduría compleja o re-estructuración de la base de datos.*

**Deudas Técnicas Pendientes (Handoff preparado):**
- [x] TAREA 1: Arquitectura de la Base de Datos Visual (SQLite). **[COMPLETADO]**
- [x] TAREA 2: Refactorización Inteligente de la Célula 2 y Single-Pass en FFmpeg. **[COMPLETADO]**
- [ ] TAREA 3: Integración de la Célula Acuñadora (Tokenización Web3 / IPFS).
- [ ] TAREA 4 (PREMIUM): Soporte de "Chunking" en `video_maker.py` (o creación de `video_maker_premium.py`) para compilar videos largos sin colapsar FFmpeg.
- [ ] TAREA 5 (PREMIUM): Creación de un `motor_narrativo_premium.py` en la Célula 1 para estructurar guiones astrológicos extendidos (Revolución Solar) por capítulos.
