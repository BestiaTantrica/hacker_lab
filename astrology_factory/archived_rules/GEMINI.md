# Astrology Factory — Reglas del Proyecto

## DIRECTIVA DE PRE-EJECUCIÓN (REGLA DE ORO)
**PROHIBIDO INVENTAR O CREAR PROCESOS A CIEGAS.**
Antes de modificar, crear o eliminar CUALQUIER script, archivo o flujo del proyecto, el agente está obligado a:
1. Releer la estructura del proyecto mediante la exploración activa (`list_dir`, `grep_search`, `view_file`).
2. Entender *dos veces* cómo funciona el ecosistema actual (los scripts `video_maker.py`, `audio_mixer.py`, `tts_local.py`, etc.).
3. Asegurarse de no estar superponiendo una solución nueva sobre una existente.
4. Identificar exactamente dónde encaja la modificación para no romper la cadena de automatización (Vademécum → Guion → TTS → Video → Bóveda).

## SIEMPRE leer al inicio de cada conversación
- /home/LAB/astrology_factory/HANDOFF.md
- /home/LAB/astrology_factory/PRODUCTION_RULES.md
- /home/LAB/astrology_factory/content_factory/vademecum_contexto.md (últimos eventos)

## BÓVEDA CENTRALIZADA (INAMOVIBLE)
- Ruta única: /home/tomas2/MediaContingencia/Privada/Astrology_Vault
- Videos finales: Astrology_Vault/Videos_Finales/<Semana>/FINAL_<Evento>.mp4
- Assets: Astrology_Vault/Assets_Reusables/<Semana>/<id>.mp4|.jpg
- El acceso directo del Escritorio apunta a esta ruta — NO es la bóveda real.
- PROHIBIDO proponer mover la bóveda.

## TIMING DE VIDEO — REGLA CARDINAL
- El timing LO DICTA SIEMPRE el bloque ASS de Whisper. Nunca valores fijos.
- Cada clip visual dura EXACTAMENTE lo que dura su bloque de narración (ASS).
- La imagen se adapta al relato. NUNCA al revés.
- Usar parse_ass_durations() → (start_sec, end_sec) por bloque de diálogo.
- clip_dur = (ass_end - ass_start) + FADE_DUR  (FADE_DUR = 0.5s)
- Imagen principal por escena: MÁX 2.0–2.5s. Nunca clips de larga duración en shorts.
- PROHIBIDO agregar padding arbitrario grande al último clip: genera cola muerta.
- División pareja = SOLO fallback si no existe archivo ASS.

## ESTRUCTURA DE CARPETAS DE PRODUCCIÓN
Cada evento en produccion/<Evento>/:
  - <Evento>.mp3, .mp4, .ass, guion.txt, storyboard.txt
  - assets/  ← TODO el caché visual aquí (_bg.*, _clip_*.mp4)

## FLUJO DE PRODUCCIÓN — FASE 1 → FASE 2
- FASE 1: Se producen los 7 tránsitos diarios, de A UNO POR VEZ.
  Renderizar → Mostrar al usuario → Esperar OK → Avanzar al siguiente.
  Nunca lanzar el batch completo sin validación.
- FASE 2: Una vez aprobados todos los diarios de la semana/mes,
  se genera el Video Semanal sintetizando esos tránsitos. La semana
  se extrae de los diarios, nunca al revés.

## GENERACIÓN AUTÓNOMA DE GUIONES (SIN PREGUNTAR)
- El agente genera el texto de los tránsitos de forma autónoma.
  NUNCA preguntar "de dónde salen los textos" o "pasame el guion".
- La base de todo texto es siempre:
    1. Los motores astrológicos del proyecto (datos reales, no inventados).
    2. El vademecum.json y vademecum_contexto.md como historial.
    3. Los documentos existentes en produccion/<Evento>/ si los hay.
- PROHIBIDO mezclar la API del bot servidor (ai_persona_engine.py) con
  la generación local de guiones de video. Son dos cosas distintas.
- Estructura obligatoria del relato:
    [1] Contexto astrológico clínico (qué planeta, casa, tránsito, fecha)
    [2] Sugestión constructiva de cómo afrontarlo (sin chamuyo ni autoayuda vaga)
    [3] CTA contextual al final:
        - Teaser del próximo tránsito del día siguiente ("Mañana atención a...")
        - O enlace al video semanal correspondiente ("En mi resumen semanal...")
        - O invitación a seguir la serie de la semana
        - Nunca un CTA genérico vacío

## ESTILO VISUAL Y DINAMISMO
- Equilibrio imágenes/videos: priorizar imágenes para los shorts (más cambios
  de plano = más dinamismo), pero si un video encaja y su duración es moderada
  y medida al formato, se incluye. No hay prohibición absoluta de videos,
  hay criterio editorial.
- Storyboard: partir la narración en bloques MÁS CORTOS para forzar más
  cambios de imagen, ritmo visual rápido, y transiciones que acentúen
  las palabras clave del subtítulo.
- PROHIBIDO: stock mundano (persona en gym, oficina, calle).
- OBLIGATORIO: cosmos, naturaleza extrema, arte digital, surrealismo, tarot,
  pinturas al óleo, arte abstracto, energías/nebulosas.

## DISEÑO SONORO INTELIGENTE Y EMPÁTICO (SUGESTIÓN ACÚSTICA)
El audio de los videos no debe tener "efectos de sonido" vulgares (campanillas en cada corte, golpes) ni ruidos sintéticos intrusivos. Se debe seguir una precisión clínica y emocional basada en dos capas:

1. **La Cortina de Seda (Frecuencia Base):**
   - Siempre debe reinar una frecuencia o pad armónico sutil de fondo (ej: 396Hz, 528Hz).
   - Debe ser constante, muy envolvente pero con volumen sutil (-15dB a -20dB) para abrigar la voz sin taparla ni saturar.

2. **Diseño Sonoro por Palabras Clave (Keyframes Emocionales):**
   - El sonido dinámico se dispara por CONCEPTOS en el relato, no por los cortes mecánicos de video.
   - **Mecánica:** El motor de audio debe cruzar los tiempos de subtítulos (Whisper) para encontrar palabras o arquetipos clave en la línea de tiempo. 
   - **Ejemplo:** Si el relato dice "Aries" o "fuego", en ese segundo exacto ingresa sutilmente una frecuencia o sonido intenso, alcanza su pico durante el concepto, y luego vuelve a desvanecerse (fade-out) dejando solo la cortina de seda original.

## AUTOAPRENDIZAJE Y ESTANDARIZACIÓN CONTINUA
- Al finalizar cada video aprobado, revisar si algo del flujo debe refinarse.
- Las reglas de este archivo se actualizan con /learn cuando el usuario corrige
  o mejora el proceso. Cada corrección es un aprendizaje permanente.
- Este proyecto es una maquinaria de generación de contenido: cada eslabón
  (motores astrológicos → guion → voz → video → bóveda → vademecum) debe
  integrarse sin fricción y sin que el usuario tenga que pegar ningún paso manualmente.

## EL USUARIO NO TOCA LA TERMINAL
La IA ejecuta todo. El vademécum se actualiza automáticamente post-render.

## RUNBOOK — PRODUCCIÓN DE UN TRÁNSITO (PARA CUALQUIER AGENTE)

### PREREQUISITO: antes de cualquier acción, leer:
  - GEMINI.md (este archivo)
  - HANDOFF.md
  - PRODUCTION_RULES.md
  - content_factory/vademecum_contexto.md (últimos eventos renderizados)

### PASO 1 — Crear carpeta del evento (si no existe)
  mkdir -p /home/LAB/astrology_factory/produccion/<Evento>/assets/

### PASO 2 — Redactar guion.txt (5 frases exactas)
  ⚠️ USAR CLAUDE para este paso. Requiere:
    - Precisión astrológica clínica (planeta, casa, fecha exacta)
    - Tono constructivo, cero chamuyo
    - CTA contextual en la frase 5 (teaser próximo tránsito / enlace semanal)
  Estructura:
    Frase 1: Contexto astrológico duro (qué tránsito, qué fecha)
    Frase 2: Efecto en el cuerpo/emoción/vínculo (específico)
    Frase 3: Por qué ocurre (mecánica astrológica del tránsito)
    Frase 4: Cómo afrontarlo constructivamente
    Frase 5: CTA — teaser del próximo tránsito o enlace al resumen semanal

### PASO 3 — Redactar storyboard.txt (exactamente N líneas = N frases del guion)
  ⚠️ USAR CLAUDE para este paso. Requiere criterio editorial.
  Formato: [tipo] descripción en inglés evocadora | id: nombre_unico
  Tipos: [illustration] o [video]
  Criterio: priorizar [illustration] para ritmo rápido.
    [video] solo si encaja y tiene duración moderada.
  PROHIBIDO: stock mundano (gym, oficina, calle, persona comiendo).
  REGLA CARDINAL: N líneas storyboard == N frases guion. Siempre.

### PASO 4 — Ejecutar pipeline completo (puede hacerlo cualquier agente)
  cd /home/LAB/astrology_factory
  venv/bin/python content_factory/tts_local.py <Evento>
  Esto hace: TTS → Whisper ASS → Pexels/Pixabay assets → Render → Telegram

### PASO 5 — Copia a Bóveda (AUTOMÁTICA — no requiere acción manual)
  video_maker.py llama a _copy_to_vault() al finalizar el render.
  El archivo queda en:
  /home/tomas2/MediaContingencia/Privada/Astrology_Vault/Videos_Finales/<Semana>/FINAL_<Evento>.mp4
  Si el agente detecta que el archivo NO está en la Bóveda tras el render,
  debe copiarlo manualmente con:
  cp produccion/<Evento>/<Evento>.mp4 \
     /home/tomas2/MediaContingencia/Privada/Astrology_Vault/Videos_Finales/<Semana>/FINAL_<Evento>.mp4
  y reportar el error como BUG en video_maker.py.

### PASO 6 — Esperar OK del usuario antes de avanzar al siguiente video.

## CUÁNDO USAR CLAUDE vs MODELO MENOR

| Tarea | Modelo recomendado | Por qué |
|---|---|---|
| Redactar guion astrológico | ⚠️ CLAUDE | Requiere precisión clínica y tono empático sin chamuyo |
| Diseñar storyboard | ⚠️ CLAUDE | Requiere criterio editorial: qué imagen evoca cada emoción |
| Diagnosticar errores en logs | ⚠️ CLAUDE | Detecta errores silenciosos (Wikimedia fallback, N_escenas mismatch) |
| Ejecutar pipeline técnico | ✅ Gemini/cualquier modelo | Pasos mecánicos y repetibles |
| Copiar archivos a Bóveda | ✅ Gemini/cualquier modelo | Operación de filesystem sin criterio editorial |
| Verificar validación N_escenas | ✅ Gemini/cualquier modelo | El script lo dice explícitamente |
| Actualizar vademecum | ✅ Automático | Lo hace render_semanal.py solo |

## PUNTOS FRÁGILES A MONITOREAR EN CADA RENDER

1. ✅ Validación N_frases == N_escenas (en video_maker.py — falla explícitamente si no coinciden)
2. ⚠️ Si el log dice "Wikimedia" en todas las escenas → problema con Pixabay/Pexels API (.env)
3. ⚠️ Al final del batch verificar: success_count == total_folders. Si no, hay guion faltante.
4. ℹ️ La voz es Jorge Neural (México). Para Argentina: cambiar a es-AR-TomasNeural en audio_generator.py
5. ✅ CACHÉ DE WHISPER: Si <Evento>.ass ya existe, NO volver a correr Whisper. Usar el .ass existente.
   Violación = render innecesariamente lento (3-8 min extra por video).
   create_video() DEBE chequear esto ANTES de llamar a generate_ass().
6. ✅ El punto de entrada del pipeline de video es editing_reviewer.py, NO video_maker.py directamente.
   editing_reviewer.py detecta el aspecto astrológico, inyecta glitches, y luego llama a video_maker.py.
   Llamar a video_maker.py solo = video sin glitches.

## RITMO EDITORIAL DEL STORYBOARD (variable, no fijo)
Regla: más conceptos en una frase → más imágenes para esa frase.

  Densidad ALTA (frase menciona 2+ planetas, casa, aspecto):
    → 3-4 escenas para esa frase. Ritmo ágil, muchos cortes.
    Ej: "Mercurio y Venus en Escorpio con la Luna en Géminis aceleran..."
         → 3 imágenes: símbolo Mercurio | símbolo Venus | símbolo Luna

  Densidad MEDIA (concepto principal + emoción):
    → 2 escenas para esa frase.
    Ej: "Tu intuición está amplificada. No racionalices lo que sentís."
         → 2 imágenes: ojo intuitivo | figura contenida

  Densidad BAJA (reflexión simple o CTA):
    → 1 escena.
    Ej: "Vas al link de mi perfil y ponés tu fecha de nacimiento."
         → 1 imagen: portal cósmico/link brillante

  Total típico: 8-14 escenas para un guion de 5 frases.
  El número total NO está fijado. Lo decide la lectura del guion.
  NUNCA fijar un tiempo por imagen (no 4s, no 3s, no nada fijo).

## CTA FINAL — PORTAL WEB (última escena de CADA video)
La última frase y escena SIEMPRE apunta al portal donde:
  - La persona ingresa su fecha de nacimiento
  - Recibe su carta astral personalizada con el tránsito de la semana
  - Puede hacer donación voluntaria para apoyar el canal
  - El canal recaba retroalimentación astrológica real de la audiencia

  Modelo de frase CTA:
  "Si querés saber exactamente cómo te afecta este tránsito,
   vas al link de mi perfil, ponés tu fecha y recibís tu lectura
   personalizada. El apoyo al canal es con lo que puedas."

  Escena visual del CTA: siempre [illustration] con portal/estrellas/glow.
  NUNCA ícono genérico de YouTube ni teléfono mundano.

## FORMATO DE QUERY EN STORYBOARD
Cada línea = ESTILO ARTÍSTICO + CONCEPTO/EMOCIÓN ASTROLÓGICA.
Estilos válidos: baroque oil painting | cyberpunk neon | watercolor indigo |
                 tarot card ornate | surrealist art | cosmic digital art |
                 sacred geometry | ink wash painting | rococo celestial

  MALO:  "dark background scorpio"
  BUENO: "cyberpunk neon scorpio glyph dark energy"

  MALO:  "person feeling intuition"
  BUENO: "watercolor indigo eye intuition surreal art"

  Consultar siempre PRODUCTION_RULES.md — sección PALETA DE ESTILOS VISUALES.

## GLITCH ENGINE — PALETA ASTROLÓGICA (REGLA DE PRODUCCIÓN)
Los glitches son VISIBLES (no subliminales). El espectador percibe el corte psicológico.
Se inyectan ENTRE clips, en el momento del corte, via editing_reviewer.py.

Pulsos por aspecto (ya implementado en editing_reviewer.py):
| Aspecto     | Pulsos | Duración/frame | Efecto FFmpeg principal              |
|-------------|--------|----------------|--------------------------------------|
| Cuadratura  |   4    | 0.10–0.15s     | rgbashift fuerte (rh=5,bv=5) + noise |
| Oposición   |   2    | 0.12–0.15s     | negate + colorlevels                 |
| Conjunción  |   1    | 0.20–0.25s     | eq=saturation=3.0 + gblur=sigma=2   |
| Trígono     |   3    | 0.10s          | rgbashift suave (rh=2,bv=2)          |
| Sextil      | = Trígono (agrupados en código como 'trigono')            |

Flujo: editing_reviewer.py detecta aspecto del guion.txt → genera secuencias de glitch
→ las inyecta en assets/<scene>_3_bg.mp4 → llama a video_maker.py.
NUNCA llamar a video_maker.py directamente si se quieren glitches en el video final.
