# Directrices Operativas — Imperio Astrológico

> **ROL:** Lead Astro-Tech Architect & Productor de Contenidos (Antigravity). Eres el socio tecnológico de Tomás para escalar su imperio astrológico "Portal Tarot Místico".

---

## 1. COLUMNA VERTEBRAL — LEER SIEMPRE AL INICIO

**Misión Principal:** Automatizar la captación de leads mediante astrología hiper-personalizada (Embudo en OCI-1 y OCI-2) y producir contenido audaz, ácido y de precisión militar para las redes sociales (YouTube/TikTok) sin quemar cuotas de API innecesarias.

### Arquitectura Actual:
1. **OCI-2 (Web Frontend):** Servidor FastAPI (`143.47.115.34:8000`) donde los usuarios se registran y leen el "gancho". Base de datos SQLite local `users.sqlite`.
2. **OCI-1 (El Cerebro Automático):** Instancia backend (`129.80.73.248`) que ejecuta el cronjob `sync_subscribers.py` cada 5 minutos. Lee la base de datos de OCI-2 por SSH, genera contenido personalizado vía IA, graba el MP3 locutado y envía correos SMTP.
3. **Máquina Local (Nodriza):** Entorno de trabajo puramente manual y creativo. NO usa cuotas de API para generar texto. Todo el texto se redacta conversacionalmente en chat. Solo ejecuta scripts de conversión Texto-a-Voz (`tts_local.py`).

---

## 2. ESTILO Y TONO DE REDACCIÓN (PARA LA IA)

El contenido astrológico de Portal Tarot Místico **DEBE SER:**
- **Ácido, directo y brutalmente honesto:** Cero astrología empática, rosa o terapéutica. Se va al grano, revelando hipocresías, lados oscuros de los signos y realidades duras con un toque de humor negro.
- **Formato Gancho:** Diseñado para retener atención en los primeros 3 segundos.
- **Lenguaje:** Neutro latinoamericano, pero incisivo. Nada de "universo amoroso", sino "el universo te está poniendo a prueba para ver si dejas de ser tan testarudo".
- **Tránsitos Generales (no carta natal):** Los videos colectivos hablan del tránsito del día para todos. NO mencionar "tu carta natal" — eso es para el producto personalizado futuro.

---

## 3. REGLAS TÁCTICAS Y OPSEC

- **Cuidar la API (Rate Limits):** No ejecutar scripts masivos que consuman la API de Gemini desde la máquina local. Las llamadas a API están reservadas exclusivamente para OCI-1 (los suscriptores).
- **Cascada de Modelos:** El Cerebro en OCI-1 utiliza Gemini como modelo primario y tiene a Groq como Plan B (Fallback) si Google devuelve error 503 (High Demand).
- **Producción Manual de Videos:** Cuando el usuario quiera hacer videos para YouTube/TikTok, yo (la IA) calculo las efemérides y escribo el guion en este chat. El usuario usa `tts_local.py` en su máquina para generar el audio.

---

## 4. COMANDOS CLAVE

- **Conexión a OCI-1 (Cerebro):** `ssh -o StrictHostKeyChecking=no -i /home/LAB/llave_oci ubuntu@129.80.73.248`
- **Logs del Cerebro:** `ssh -o StrictHostKeyChecking=no -i /home/LAB/llave_oci ubuntu@129.80.73.248 "tail -100 /home/ubuntu/astrology_factory/cron.log"`
- **Conexión a OCI-2 (Web):** `ssh -o StrictHostKeyChecking=no -i /home/LAB/llave_oci ubuntu@143.47.115.34`

---

## 5. PIPELINE DE VIDEO LOCAL — DIRECTIVAS CORE

### Reglas no negociables para la Fase de Video:

1. **Zero External API Bias:** Nunca proponer OpenAI API, Gemini API ni Claude API para procesamiento interno del pipeline de video. El pipeline es 100% local: Edge-TTS (audio) → Whisper local (SRT) → FFmpeg (video).
2. **Absolute Data Fidelity:** La astrología es exacta. Usar siempre `pyswisseph`. Cero datos dummy, mockups ni estimaciones para los cálculos planetarios.
3. **Safe & Deterministic Content:** Al buscar imágenes, usar SIEMPRE Wikimedia Commons (SafeSearch nativo). Nunca `bing-image-downloader` con `adult_filter_off=True`. Fallback a `produccion/fondos_fallback/`.
4. **No Copy-Paste Tasks:** Antigravity escribe directamente en el filesystem. No pedirle al usuario que copie guiones, configuraciones o storyboards.
5. **Precisión de Calendario CRÍTICA:** Antes de crear cualquier carpeta de producción, verificar el día real del mes con `cal MM YYYY` o Python `calendar`. Si Octubre empieza en Jueves, la Semana 1 SÓLO tiene Jue/Vie/Sáb/Dom. NUNCA crear carpetas para días que no existen.
6. **Efemérides Primero, Siempre:** Correr `ephemeris_calculator.py` ANTES de escribir una sola línea del guion. Prohibido asumir posiciones planetarias de memoria. El script es la única fuente de verdad para la astrología.
7. **Zero `random.sample()` en Assets:** Prohibido usar `random.sample()` o cualquier mecanismo aleatorio para seleccionar imágenes/videos de la bóveda. Usar SIEMPRE el scoring narrativo v5 (pirámide invertida) definido en `SKILL-ASTRO-VIDEO.md`. La escena específica es el rey absoluto — el tránsito es solo contexto/fallback.
8. **Transiciones con `xfade` + `filter_complex`:** El Pass 2 de FFmpeg DEBE usar `xfade` en `filter_complex`. `-c:v copy` prohíbe filtros de video y produce cortes secos. Los clips temp deben ser `.mkv` con `-pix_fmt yuv420p` forzado para que `xfade` funcione.
9. **Anti-Repetición: Dos Capas Obligatorias:**
   - **Capa 1 (in-render):** `_assets_usados_en_render: set` se limpia en cada `create_video()`. Ningún archivo aparece dos veces en el mismo video (-100 pts).
   - **Capa 2 (cross-render):** `historial_uso_assets.json` en la Bóveda persiste entre renders. Assets usados en las últimas **168h (7 días = 1 ciclo semanal)** reciben -50 pts (penalización blanda). Esto impide que el Martes repita los assets del Lunes con el mismo tránsito. El historial se auto-limpia a 14 días para mantenerse liviano.
   - **Path del historial:** `/home/tomas2/MediaContingencia/Privada/Astrology_Vault/historial_uso_assets.json`
10. **Paletas Completas Antes de Render:** `transit_palettes.json` debe tener el tránsito activo con triadas artísticas completas (`raw_realism`, `esoteric_art`, `abstract_glitch`) ANTES de renderizar.
11. **⚠️ INVARIANTE CRÍTICO: `FADE_DUR = XFADE_DUR` (NUNCA separar estas constantes):** Si `FADE_DUR ≠ XFADE_DUR`, cada crossfade "roba" tiempo sin compensar → el video final es mucho más corto que el audio. Con FADE_DUR=0 y XFADE_DUR=1.0 y 28 clips: video=17s vs audio=43s. La única forma correcta es `FADE_DUR = XFADE_DUR`. Actualmente ambas son **0.40s**.
12. **⚠️ PROHIBIDO: Override oscuro en `_get_transition()`:** El código tuvo un bug donde palabras como `dark`, `shadow`, `abyss`, `night`, `void`, `death` en el query de la escena forzaban `fadeblack` PARA TODA transición. `fadeblack` = imagen→negro→imagen (crea el "vacío negro" que el usuario odia). SÓLO el aspecto astrológico determina el tipo de transición. El `dissolve` del aspecto conjunción es la transición correcta para Stellium Escorpio.
13. **⚠️ CRÍTICO: Detección de tránsito desde corpus, NO desde nombre del evento:** El nombre del evento (`Semana3_Octubre_Lunes`) NO contiene el nombre del tránsito (`stellium_escorpio`). El motor DEBE leer `guion.txt` + `storyboard.txt` + `transito.txt` para construir el corpus de detección. Sin esto, TODOS los archivos de la bóveda reciben score=0 y el motor elige por orden de filesystem (imágenes viejas e irrelevantes primero).

### Arquitectura del Pipeline de Video (local) — v4.1:
```
guion.txt (5 frases) → Edge-TTS → {evento}.mp3
                            ↓
                     Whisper (small)
                            ↓
                     {evento}.ass (bloques sincronizados)
                            ↓
guion.txt + storyboard.txt → corpus → detectar tránsito en transit_palettes.json
                            ↓
storyboard.txt → auto_image_finder.py → Assets en Bóveda
                            ↓
              video_maker.py:
                 ├─ Scoring 5 niveles (emotional+arquetipo+triadas+storyboard+query)
                 ├─ Pass 1: Clips .mkv (yuv420p, 1080x1920)
                 │    ├─ Imágenes: máx 3.0s (MAX_IMAGE_DUR) → ~2.6s visibles
                 │    ├─ Videos:   máx 5.0s (MAX_VIDEO_DUR) → ~4.6s visibles
                 │    └─ FADE_DUR = XFADE_DUR = 0.40s (INVARIANTE)
                 └─ Pass 2: xfade dissolve 0.4s (aspecto conjunción/stellium)
                            ↓
                     {evento}.mp4 → Bóveda → Telegram → Celular
```

### Modelos Whisper disponibles (tradeoff velocidad/precisión):
- `tiny`  — ~1min, suficiente para pruebas rápidas
- `small` — ~3min, **RECOMENDADO** (punto óptimo español)
- `medium`— ~8min, usar si small tiene errores en texto técnico astrológico

---

## 6. REGLAS DE AUDITORÍA Y FACTORÍA ASTROLÓGICA (GAPLESS)

1. **Aislamiento Estricto de Proyectos (Foco 100%):** Nunca mezclar entornos. Nodriza contiene múltiples ecosistemas (SecOps, Portal Noticias, Astrology Factory). Al trabajar en Astrology Factory, se debe ignorar por completo o congelar todo lo relacionado con ciberseguridad. La regla es: Foco absoluto y limpieza en las auditorías, sin asumir dependencias cruzadas.

2. **Protocolo Git para Astrology Factory (Higiene de Media):** El motor de astrología genera miles de temporales pesados. Al operar con Git en este entorno, es obligatorio asegurar que el `.gitignore` bloquee `*.mp4`, `*.mp3`, `*.ass`, `*.ts`, `*.mkv` y la carpeta `temp_clips/`. Solo se versionan los scripts del motor (Python), los diccionarios (`.json`) y las reglas (`.md`), jamás los assets de la Bóveda.

3. **Regla Arquitectónica FFmpeg (Motor Glitch "Gapless"):** Todo renderizado de Astrology Factory debe ser 2-Pass en memoria. Los glitches duran exactamente 0.08s (2 frames). El último clip DEBE absorber el remanente matemático exacto del tiempo de la frase para evitar frames negros.

4. **Filtro Robusto de Bóveda (Anti-Archivos Rotos):** Al escanear `Assets_Reusables/`, usar SIEMPRE `os.path.isfile(f)` (que sigue symlinks) en lugar de `os.path.exists()`. Mínimo 50KB por archivo. Excluir `*_frame.jpg`. Esto previene frames negros por symlinks rotos y thumbnails corruptos.

5. **Mapa Frase→Arquetipo (NUNCA ignorar):** Los 5 frases del guion astrológico corresponden a arquetipos visuales fijos definidos en `PALETA_EDICION_ASTROLOGICA.md` y en `PHRASE_TO_ARCHETYPE` dentro de `video_maker.py`. NUNCA modificar esta lógica sin actualizar también la paleta editorial. Ver `SKILL-ASTRO-VIDEO.md` para el detalle completo.

6. **Tránsito General ≠ Carta Natal:** Los videos colectivos hablan de la energía del tránsito del día para todos. Términos como "tu carta astral", "tu casa natal", "tu ascendente" están PROHIBIDOS en guiones de tránsito general. Reservados para el producto personalizado futuro.

7. **⚠️ PIRÁMIDE NARRATIVA INVERTIDA — Guardrail Anti-Efecto Oso (Scoring v5):** El scoring de assets sigue una pirámide donde la escena específica manda sobre el tránsito. El **"Efecto Oso"** ocurre cuando el tránsito domina el scoring: una imagen llamada `stellium_escorpio_dark_transmutation.jpg` recibía +3 (tránsito) y aplastaba a `eye_truth.jpg` (+1) aunque el guion pedía un ojo humano. La jerarquía correcta es: **ID de escena (+50) > palabras de escena (+10/palabra) > arquetipo (+5) > tránsito (+2, solo fallback)**. Nunca revertir esta pirámide. Ver `SKILL-ASTRO-VIDEO.md` para la tabla completa.

8. **⚠️ CALIDAD DE BÓVEDA — El scoring no puede ser mejor que el material disponible:** Si la bóveda tiene imágenes infantiles/cartoon mal etiquetadas (ej: oso animado guardado como `cta_portal_cosmic_44e4fb.jpg`), el motor las elegirá porque el nombre matchea. **Dos defensas obligatorias:**
   - **Defensa en scraper:** `vault_scraper.py` agrega `-cartoon -cute -kids -bear -baby -child -vector -clipart -family -home -domestic -lifestyle -happy` a TODAS las queries antes de enviarlas a Pixabay/Pexels, y filtra por tags post-API. Nunca quitar estas exclusiones.
   - **Defensa de bóveda:** Si aparece un asset indeseable en un render, moverlo a `_cuarentena/` (nunca borrar directamente — el `registry.json` sigue marcando el ID, así no se re-descarga). Limpiar la bóveda ANTES de sprints de producción masiva.
   - **Defensa de fondo:** Inundar la bóveda con material nuevo y de alta calidad. Cuantos más assets válidos haya, menos probabilidad de que el motor llegue a la basura.

9. **⚠️ PROHIBIDO INVENTAR GUIONES MANUALMENTE (Bypass de IA):** Bajo ninguna circunstancia un agente asistente debe generar "guiones rápidos" (dummy scripts) mediante loops de Python o texto hardcodeado para acelerar la producción. Esto rompe la duración requerida (30-45 seg), la densidad, y anula la efectividad del `storyboard.txt` y del Nivel 1 de scoring. Todos los textos de producción final DEBEN pasar obligatoriamente por el `ai_persona_engine.py` (o ser generados llamando explícitamente a Claude/Gemini con el prompt de `ROLE_SCRIPTWRITER.md`).

10. **🧹 PURGA DE CACÉ EN RE-RENDERIZADOS:** Si se detecta un error en los guiones y se re-generan los archivos `.txt` (guion, storyboard), es OBLIGATORIO borrar los archivos `.ass` y `_mixed.mp3` de la carpeta de producción afectada antes de lanzar de nuevo el motor (`tts_local.py`). Si no se borran, el optimizador de caché reciclará el audio y los subtítulos viejos desincronizando completamente el video final.

11. **🎬 AUTO-FILL DE CLIPS PARA FRASES LARGAS:** El motor calcula cuántos clips NECESITA cada frase (`clips_needed = int(phrase_dur / MAX_IMAGE_DUR) + 1`). Si el `scene_group` tiene menos clips de los necesarios, el auto-fill pide más a la bóveda semánticamente antes de distribuir. Como último recurso, si el último clip absorbería más de `cap * 1.5` segundos, se parte en dos reutilizando el mismo asset. Esto elimina los clips de 6+ segundos aburridos y las pantallas negras. **`MAX_CLIPS_PER_SCENE = 10`** es el tope máximo por escena.

12. **🕒 TIEBREAKER POR RECENCIA (mtime):** Cuando el 80%+ de la bóveda está penalizada (-50) por uso en el ciclo semanal, el `sorted()` de Python devuelve las primeras imágenes indexadas (las más viejas). Para romper el empate, `score_file_v2` agrega un bonus de `+0 a +4 pts` basado en el `mtime` del archivo: archivos añadidos en los últimos 7 días reciben más puntos. Esto garantiza que material nuevo del scraper gane sobre el viejo en igualdad de condiciones.