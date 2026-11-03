# 📜 INFORME DE HOJA DE RUTA Y PENDIENTES — ASTROLOGY FACTORY

* **ID de Hilo Antigravity:** `4227c4cd-6469-4951-8124-cec7ed3517b4`
* **Fecha de cierre de sesión:** Noche del 2 al 3 de Noviembre de 2026
* **Estado general:** Pipeline de 4 de Noviembre renderizado como base; arquitectura de subtítulos calibrada; bot de Telegram ajustado. Tareas críticas de evolución cinemática, admin y YouTube definidas para mañana.

---

## 🧭 1. EVOLUCIÓN CINEMÁTICA DEL VIDEO Y RELOJ (DIRECCIÓN DE ARTE)

### Diagnóstico actual
* El reloj base actual está nítido, pero le falta la emoción del viaje inmersivo. El zoom se sintió estático y el giro previo era demasiado acelerado.
* Las líneas directas y flechas del HUD resultan rígidas visualmente.

### Nueva Estrategia Visual para Mañana
1. **Fondo de Espacio Profundo Específico por Tránsito:**
   * Diseñar con IA (`generate_image`) una imagen cósmica dedicada según la energía del día (para Escorpio: nebulosa abisal oscura, filamentos magnéticos y destellos dorados).
   * Animar la imagen de fondo con interpolación de video/cámara lenta para dar profundidad espacial.
2. **Efecto Túnel Cósmico (Aparición del Mandala):**
   * En Toma 1, el video inicia con el fondo espacial nítido.
   * El mandala astrológico va materializándose paulatinamente entre las estrellas, emergiendo desde el fondo cósmico con giro pausado y armónico.
3. **Zoom Dinámico de Fusión (El Segundo Final):**
   * Añadir 1 segundo a la toma de apertura.
   * En ese segundo final, aplicar un **zoom acelerado y profundo directo sobre el grado zodiacal del tránsito activo** (ej: 12° Escorpio).
   * La duración del zoom coincide exactamente con la disolvencia (`xfade` de 0.75s) hacia la imagen tenebrista, generando un efecto cinematográfico de **inmersión, materialización y salto hiperespacial**.
4. **Cierre Inverso Simétrico (Toma 5):**
   * Inicia enfocado en la zona del tránsito y se aleja suavemente hacia el mandala completo.
   * El reloj completa las 24:00:00 hs con el destello áureo en los anillos y se funde de regreso hacia el fondo espacial.
5. **HUD Orgánico (Adiós líneas duras):**
   * Reemplazar las flechas y líneas geométricas por **viñetas o píldoras flotantes sutiles del mismo color del planeta**.
   * Las viñetas titilan/pulsan en sincronía armónica con el astro en el mandala.

---

## 🤖 2. AUTOMATIZACIÓN DEL BOT DE YOUTUBE (YOUTUBE COMMENTS DAEMON)

### Estado
* `configurador_oauth.py` ya fue corregido para solicitar el permiso faltante (`https://www.googleapis.com/auth/youtube.force-ssl`).
* **Paso manual pendiente:** Ejecutar `/home/LAB/astrology_factory/venv/bin/python3 v2/celula_4/configurador_oauth.py` en la terminal y dar consentimiento en el navegador de Google.

### Directivas de Comportamiento del Bot (Anti-Bot Humano)
* **Cero enlaces y cero "link en la bio":** La venta y conversión se hace manual. El bot jamás debe sonar comercial ni a spam.
* **Tono Tomás:** Respuestas breves, livianas, frescas, cool, empáticas pero directas al grano.
* **Estimulador de Debate Orgánico:** Si alguien comenta su signo o casa ("soy de virgo", "tengo casa 1 en leo"), el bot responde con una repregunta aguda y contextualizada que lo invite a reflexionar y responder de nuevo (disparando el algoritmo de YouTube Shorts).

---

## 💻 3. PANEL DE ADMINISTRACIÓN (`portaltarotmistico.com/admin`)

### 1. Centralización y Sincronización Real
* Resolver la inconsistencia donde los cambios de estado hechos desde el celular no se reflejan al abrir la PC.
* Asegurar que las mutaciones escriban directamente en el backend (SQLite/JSON centralizado en OCI) y que el frontend invalide caché de forma inmediata.

### 2. Simplificación Visual de la Tabla
* Eliminar la sobrecarga de carteles y botones duplicados.
* Implementar **un solo botón toggle de 2 estados por red**:
  * Modo 1: `[PROGRAMADO 🟡]`
  * Modo 2: `[PUBLICADO 🟢]`

### 3. Asistente IA de Redes con Máximo Contexto Astrológico
* **Selector de fecha:** Permitir elegir la fecha del video para cargar automáticamente los tránsitos calculados con Swiss Ephemeris.
* **Conciencia de Cadena Temporal:** Conectar el video de hoy con los tránsitos de ayer y mañana (publicamos 24h antes para permitir la verificación personal de la audiencia).
* **Avatar Tomás (Carta Natal Integrada):**
  * Carta de Tomás: Sol/Mercurio Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5° en Casa 10.
  * La IA debe cruzar los tránsitos del día con la propia carta de Tomás para responder en primera persona y transmitir la astrología desde la vivencia real y educativa, no como un vendedor genérico.

---

## 📱 4. BOT DE TELEGRAM (ACTUALIZACIÓN INMEDIATA REALIZADA)

* **Firma corregida en [web_app/telegram_manager.py](file:///home/LAB/astrology_factory/web_app/telegram_manager.py):**
  * *Antes:* `"Las cartas marcan el suelo, tu voluntad construye. Tomás · portaltarotmistico.com"`
  * *Ahora:* **`"El cielo describe el mapa, tu consciencia toma el timón. Tomás · portaltarotmistico.com"`**
  * Elimina por completo las referencias al Tarot/cartas y ancla la filosofía en la autonomía psicológica y astrológica.

---

## 📦 5. REGISTRO Y REPOSITORIO

* **Videos listos:**
  * 2 Noviembre: `PUBLICADO`
  * 3 Noviembre: `PROGRAMADO`
  * 4 Noviembre: `LISTO_AUDITORIA` (archivo: `produccion/semana_02nov_08nov/FINAL_2026-11-04_Mercurio_Cazimi_Escorpio.mp4`)
* **Repositorio Git:** Todos los scripts de prueba, generadores de reloj cinemático, roadmap de wallpapers y actualización de Telegram listos para commit de cierre.
