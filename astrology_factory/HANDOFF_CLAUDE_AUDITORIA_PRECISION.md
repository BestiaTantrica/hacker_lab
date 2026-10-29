# 🛡️ HANDOFF DE AUDITORÍA NIVEL 3: CLAUDE PRO (PRECISIÓN MATEMÁTICA, TRÁNSITOS & SEGURIDAD)
*Fecha: 28-29 de Octubre de 2026 | Proyecto: Astrology Factory & El Glifo Maestro*

Eres **Claude**, asumiendo el rol de **IA de NIVEL 3 (Arquitectura Profunda y Calidad Máxima)** en el ecosistema *Astrology Factory*.
Tu misión en este sprint es auditar y certificar 3 áreas críticas antes de que la producción audiovisual y la monetización escalen a gran volumen:

---

## 🎯 OBJETIVOS DE LA AUDITORÍA DE CLAUDE PRO

### 1. 🔭 Precisión Matemática: Motor JS del Reloj (`reloj_engine.js`) vs. Swiss Ephemeris (`pyswisseph`)
**Situación:**
El astrolabio dinámico en tiempo real (`reloj_engine.js`) corre en el cliente a 60 FPS usando elementos orbitales keplerianos J2000 y aproximaciones trigonométricas de Jean Meeus.
Acabamos de realizar la telemetría empírica contrastando el motor JS contra `pyswisseph` (Swiss Ephemeris oficial de NASA/Astrodienst en C) para la fecha actual (29 Octubre 2026 02:00 UTC):

| Astro / Ángulo | Swiss Ephemeris (Oficial) | Motor JS (`reloj_engine.js`) | Desviación (Delta) | Evaluación |
| :--- | :--- | :--- | :--- | :--- |
| **Sol ☉** | `215.6628°` (Escorpio 5°39') | `215.6662°` (Escorpio 5°40') | **+0.0034°** (<12 arcsec) | 🟢 Precisión Quirúrgica |
| **Luna ☽** | `75.3057°` (Géminis 15°18') | `75.0469°` (Géminis 15°02') | **-0.2588°** (~15 arcmin) | 🟡 Desviación menor |
| **Ascendente** | `82.4884°` (Géminis 22°29') | `82.48°` | **<0.01°** | 🟢 Precisión Impecable |
| **Medio Cielo (MC)**| `9.8412°` (Aries 9°50') | `9.84°` | **<0.01°** | 🟢 Precisión Impecable |

**Preguntas para Claude Pro:**
1. Para la **Luna**: En `reloj_engine.js` usamos una serie truncada de 11 términos periódicos. ¿Qué 2 o 3 términos adicionales de perturbación solar/eclíptica (de los coeficientes de Brown/Meeus) nos recomiendas incorporar para reducir el error de la Luna por debajo de `0.05°` sin degradar el rendimiento a 60 FPS en el canvas?
2. Para las **Casas Astrológicas**: El MC y ASC son exactos por trigonometría esférica. Las casas intermedias actualmente se grafican espaciadas a 30° desde el ASC (Equal House). ¿Recomiendas implementar la fórmula analítica en JS de las cúspides intermedias de Placidus o Porfirio, o mantener Equal House geocéntrico con ASC en el horizonte izquierdo?

---

### 2. ⚡ Rigor Astrológico de los Tránsitos Diarios (29 Octubre a 1 Noviembre 2026)
Hemos calculado las efemérides exactas para la semana en curso:
* **29 de Octubre:** Mercurio retrógrado en Escorpio (19°) Cuadratura Marte en Leo (17°) (orbe 1.67°) + Sol en Escorpio (6°) Cuadratura Plutón en Acuario (3°).
* **30 de Octubre:** **Mercurio retrógrado en Escorpio Cuadratura Partil Exacta Marte en Leo (orbe de apenas 0.32°!)** + Sol en Escorpio Trígono Luna en Cáncer (1.08°).
* **31 de Octubre (Samhain):** Luna en Cáncer (20°) Trígono Mercurio retrógrado en Escorpio (17°) (orbe 3.17°) + Mercurio/Marte en tensión sostenida (1.17°).
* **1 de Noviembre (Luna Menguante):** Luna en Leo (4°) Oposición Partil Plutón en Acuario (3°) (orbe 1.37°) + Sextil Partil Urano en Géminis (0.15°) + Cuadratura Sol en Escorpio.

**Preguntas para Claude Pro:**
1. ¿El encuadre psicológico y clínico que definimos (evitar la autoayuda barata, enfocar en la tensión entre "la palabra como bisturí / orgullo defensivo" y "el trono personal vs la colmena colectiva") es impecable desde la óptica de la astrología psicológica arquetípica (Greene, Arroyo, Sasportas)?
2. ¿Hay algún matiz o punto ciego en esta combinación fija (Escorpio, Leo, Acuario) que debamos blindar en los guiones audiovisuales para evitar malas interpretaciones fatalistas en la audiencia?

---

### 3. 🛡️ Auditoría de Seguridad & Embudo de Pagos (`web_app/main.py`)
En `web_app/main.py`:
* Se desplegó la pasarela de Mercado Pago con Alias directo (`vida.rucula`, 15% OFF) y botón QR, además de los enlaces de checkout con cuotas automáticas y PayPal.
* El endpoint `/api/subscribe` procesa los datos natales y responde de forma asíncrona mediante `BackgroundTasks` para entregar la carta natal en milisegundos sin bloquear el servidor.
* El endpoint `/api/chat` rota entre modelos Flash (`gemini-3.8-flash`, `3.7-flash`, `3.6-flash`, `3.5-flash-lite`) con fallback estricto para evitar errores 500 o caídas de sesión.

**Preguntas para Claude Pro:**
1. ¿Qué mejoras de sanitización, rate limiting por IP (ej. `slowapi`) o validación de inputs recomiendas para blindar `web_app/main.py` contra abusos de bots o spam masivo en producción OCI-2?
2. Si implementamos el webhook de Mercado Pago para verificación automática 24/7 sin revisión humana de comprobante, ¿cuál es la estructura canónica recomendada para validar la firma `x-signature` (HMAC SHA-256) garantizando estricta idempotencia en SQLite?

---

## 📋 FORMATO DE RESPUESTA ESPERADO
Claude, por favor estructura tu respuesta en 3 secciones ejecutables:
1. **Solución Matemática para `reloj_engine.js`** (fórmulas y código JS drop-in para calibración de la Luna y casas).
2. **Dictamen Astrológico de los Tránsitos** (claves narrativas y arquetípicas para los guiones de los 4 días).
3. **Recomendaciones de Seguridad & Webhook Mercado Pago** (código FastAPI para webhook idempotente con HMAC).
