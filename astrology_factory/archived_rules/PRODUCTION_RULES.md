# ASTROLOGY FACTORY — REGLAS PERMANENTES DE PRODUCCIÓN
# Leer este archivo al inicio de CADA conversación sobre este proyecto.
# Fuente de verdad: /home/LAB/astrology_factory/HANDOFF.md + este archivo

## REGLA 1: BÓVEDA CENTRALIZADA (INAMOVIBLE)
- Ruta absoluta única: /home/tomas2/MediaContingencia/Privada/Astrology_Vault
- Videos finales: Astrology_Vault/Videos_Finales/<Semana_Prefijo>/FINAL_<Evento>.mp4
- Assets reutilizables: Astrology_Vault/Assets_Reusables/<Semana_Prefijo>/<id>.mp4
- PROHIBIDO proponer mover la bóveda.

## REGLA 2: TIMING — LA IMAGEN SE ADAPTA A LA NARRACIÓN (NO AL REVÉS)
- El timing LO DICTA SIEMPRE el bloque ASS de Whisper.
- parse_ass_durations() → (start_sec, end_sec) por bloque de diálogo.
- clip_dur = (ass_end - ass_start) + FADE_DUR (FADE_DUR = 0.5s)
- Imagen principal de cada escena: MÁX 2.0–2.5s para sostener el ritmo del short.
- PROHIBIDO agregar padding arbitrario grande (>1s) al último clip. Genera cola muerta.
- División pareja = SOLO fallback si no existe archivo ASS.

## REGLA 3: ESTRUCTURA DE CARPETAS
produccion/<Evento>/
  ├── <Evento>.mp3, .mp4, .ass
  ├── guion.txt, storyboard.txt
  └── assets/  ← TODO el caché visual aquí, nunca suelto en la raíz

## REGLA 4: FORMATO SEMANAL
- 8 videos/semana: 1 semanal (60-90s) + 7 diarios (30-40s)
- Orquestación: render_semanal.py Semana1_Octubre

## REGLA 5: ESTILO VISUAL
PROHIBIDO: stock mundano (persona en gym, oficina, calle)
OBLIGATORIO: cosmos, naturaleza extrema, arte digital, surrealismo, tarot,
             pinturas al óleo, arte abstracto, energías/nebulosas
El relato SIEMPRE ancla en astrología clínica (planeta, casa, tránsito, fecha).

## REGLA 6: API vs PRODUCCIÓN LOCAL
- ai_persona_engine.py = API del bot servidor. NO usarla para batch local.
- Guiones y storyboards = manuales o scripts locales, CERO llamadas API innecesarias.

## REGLA 7: EL USUARIO NO TOCA LA TERMINAL
- La IA ejecuta todo. El vademécum se actualiza automáticamente post-render.

## REGLA 8: VADEMÉCUM
- Texto: /home/LAB/astrology_factory/content_factory/vademecum.txt
- JSON:  /home/LAB/astrology_factory/content_factory/vademecum.json
- Se actualiza automáticamente. Últimos 10 eventos = contexto del bot.

---

## PALETA DE ESTILOS VISUALES (NUNCA OLVIDAR)

Estos son los estilos que funcionaron en los videos semanales exitosos.
Todo nuevo storyboard debe referenciar explícitamente estos estilos en las queries.
NO usar descriptions genéricas como "dark background" o "sunset". 
Usar siempre el estilo como prefijo de la query.

### ESTILOS PERMITIDOS Y EJEMPLOS DE QUERY:

**Arte Digital Fantasia / Cosmic:**
  - "cosmic energy explosion colorful digital art"
  - "glowing aura spiritual energy field abstract animation"
  - "universe nebula stars deep space colorful artistic"
  - "ethereal light energy flowing cosmic background"

**Cyberpunk / Neon:**
  - "cyberpunk neon astrology symbol glowing circuit"
  - "neon scorpion silhouette dark background digital"
  - "futuristic glowing runes neon purple cosmic"
  - "cyberpunk tarot card neon aesthetic"

**Tarot / Arte Ocultista:**
  - "tarot card illustration the tower dramatic"
  - "tarot major arcana oil painting baroque ornate"
  - "occult mystic sigil glowing dark background art"
  - "hermetic symbol golden ratio sacred geometry glow"

**Barroco / Rococó:**
  - "baroque oil painting dramatic emotional figures"
  - "rococo ornate celestial feminine oil painting"
  - "renaissance dramatic chiaroscuro emotional scene"
  - "classical oil painting cosmic allegorical figures"

**Punk / Trash Aesthetic:**
  - "punk collage astrology zine aesthetic dark"
  - "grunge cosmic torn paper texture mystic"
  - "anarchic energy chaotic abstract neon dark"

**Watercolor / Acuarela:**
  - "watercolor cosmic galaxy abstract emotional"
  - "ink wash painting meditative dark landscape"
  - "indigo watercolor universe abstract spiritual"

**Surrealismo:**
  - "surreal dreamscape melting clock emotional"
  - "dali style surreal cosmic figure abstract"
  - "surrealist oil painting psychological landscape"

**Animaciones / Energy Loops (para [video]):**
  - "particle energy flow abstract loop dark background"
  - "cosmic dust particles slow motion abstract"
  - "glowing orb pulsating energy mystical dark"
  - "ink in water slow motion abstract art"
  - "lava lamp psychedelic color abstract loop"

### REGLA DE ORO DEL STORYBOARD:
Cada query de storyboard debe incluir UN ESTILO del listado arriba + UNA EMOCIÓN
o concepto astrológico. Nunca solo el concepto sin el estilo visual.

MALO:  "scales of justice"
BUENO: "baroque oil painting dramatic scales of justice golden light"

MALO:  "person feeling sad"
BUENO: "surrealist oil painting psychological landscape of grief indigo"

MALO:  "stars at night"
BUENO: "cosmic nebula deep space colorful digital art spiritual energy"
