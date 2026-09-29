---
name: astro-video-production
description: >
  Pipeline completo de producción de videos astrológicos diarios para
  Astrology Factory (Portal Tarot Místico). Cubre desde el cálculo de
  efemérides hasta el render final con xfade. Leer ANTES de cualquier
  producción de video. Aplica a tránsitos generales (colectivos).
---

# SKILL: Producción de Video Astrológico (Astrology Factory)

> **Cuándo activar:** Cada vez que se inicie producción de un video diario o semanal del proyecto Astrology Factory. Leer COMPLETO antes de ejecutar cualquier comando.

---

## PASO 0 — Verificar Calendario Real (OBLIGATORIO)

Antes de crear CUALQUIER carpeta de producción:

```python
import calendar
calendar.prmonth(2026, 10)  # Verificar qué días tiene el mes
```

**Regla crítica:** Si Octubre empieza un Jueves, la Semana 1 SÓLO tiene:
`Semana1_Octubre_Jueves`, `Semana1_Octubre_Viernes`, `Semana1_Octubre_Sabado`, `Semana1_Octubre_Domingo`.

**NUNCA crear** `Semana1_Octubre_Lunes`, `Semana1_Octubre_Martes`, `Semana1_Octubre_Miercoles` si esos días no pertenecen a la Semana 1 real.

Calendario de Octubre 2026 (referencia):
- **Semana 1:** Jue 1 → Dom 4
- **Semana 2:** Lun 5 → Dom 11
- **Semana 3:** Lun 12 → Dom 18
- **Semana 4:** Lun 19 → Dom 25
- **Semana 5:** Lun 26 → Dom 31

---

## PASO 1 — Efemérides (OBLIGATORIO antes del guion)

```python
from astrology_engine.ephemeris_calculator import EphemerisCalculator
from datetime import datetime

calc = EphemerisCalculator()
pos = calc.calculate_planets(datetime(YYYY, MM, DD, 12, 0))
# signo = int(grados // 30), posición = grados % 30
```

Traducción de índices de signo (0-based):
`Aries=0, Tauro=1, Géminis=2, Cáncer=3, Leo=4, Virgo=5, Libra=6, Escorpio=7, Sagitario=8, Capricornio=9, Acuario=10, Piscis=11`

**Tránsitos a identificar en orden de prioridad:**
1. ¿Stellium (3+ planetas en el mismo signo)?
2. ¿Ingreso de planeta a nuevo signo ese día?
3. ¿Aspecto exacto Luna–planeta exterior (Plutón, Urano, Saturno, Neptuno)?
4. ¿Aspecto exacto entre planetas lentos?

---

## PASO 2 — Verificar Paleta en transit_palettes.json

```bash
cd /home/LAB/astrology_factory
venv/bin/python -c "
import json
d = json.load(open('content_factory/transit_palettes.json'))
print([t['name'] for t in d['transits']])
"
```

**Si el tránsito del día NO está en la lista:** AGREGARLO con estructura completa:
```json
{
  "name": "nombre_del_transito",
  "display_name": "Nombre Legible",
  "emotional_concepts": ["concepto1", "concepto2", "concepto3", "concepto4", "concepto5"],
  "palette": {"primary": "Color 1", "secondary": "Color 2", "accent": "Color 3"},
  "artistic_triads": {
    "raw_realism":     ["descripción imagen real 1", "descripción imagen real 2", "descripción imagen real 3"],
    "esoteric_art":    ["símbolo planetario", "arte ocultismo", "carta astrológica"],
    "abstract_glitch": ["textura abstracta", "fractal", "glitch digital"]
  }
}
```

---

## PASO 3 — Guion: Estructura de 5 Frases Exactas

**Tránsitos son COLECTIVOS. PROHIBIDO "tu carta natal", "tu casa", "tu ascendente".**

| # | Nombre | Contenido | Duración aprox |
|---|---|---|---|
| 1 | **Contexto Duro** | Planeta, signo, grado, fecha. Factual, astronómico. | ~3-4s |
| 2 | **Teoría/Historia** | Cómo operó este aspecto históricamente. Evocador. | ~4-5s |
| 3 | **Mecánica General** | El mecanismo energético de este tránsito. Descriptivo. | ~4-5s |
| 4 | **Sugestión Íntima** | Cómo integrarlo. Humano, cercano. Sin "te vas a sentir...". | ~4-5s |
| 5 | **CTA** | "Andá al link de mi perfil, ingresá tus datos exactos y calculá su efecto en tu propia vida." | ~3s |

---

## PASO 4 — Storyboard: Equilibrio Obligatorio (Regla 40/60)

**Fórmula de 7 escenas recomendada** (adaptable según tránsito):

```
Escena 1: [illustration] símbolo del planeta/signo en tránsito | id: planeta_signo_simbolo
Escena 2: [video]        naturaleza real / elemento del signo   | id: naturaleza_elemento
Escena 3: [illustration] textura abstracta / fractal oscuro      | id: abstraccion_glitch
Escena 4: [video]        naturaleza o cuerpo celeste en acción   | id: cosmos_real
Escena 5: [video]        persona real / emoción humana íntima    | id: emocion_humana
Escena 6: [illustration] geometría sagrada / cosmos oscuro       | id: geometria_cosmos
Escena 7: [illustration] portal cósmico / neon gateway           | id: cta_portal_neon
```

**Reglas de formato:**
- `[illustration]` → busca en Pixabay Illustrations. Agregar siempre: `-animal -cartoon -cute -vector -character -kids`
- `[video]` → busca en Pexels Videos portrait
- Cada `id:` debe ser único y descriptivo del tránsito

---

## PASO 5 — Mapa Frase→Arquetipo Visual (PHRASE_TO_ARCHETYPE)

El motor `video_maker.py` usa este mapa para seleccionar imágenes por frase:

| Frase | Arquetipo | Qué mostrar |
|---|---|---|
| 1 (Contexto) | `esoteric_art` | Símbolo del planeta/signo del tránsito, astronomía real |
| 2 (Historia) | `raw_realism` | Naturaleza cruda, océano, sombras, elemento del signo |
| 3 (Mecánica) | `abstract_glitch` | Texturas, fractales, glitch digital, energía abstracta |
| 4 (Sugestión) | `raw_realism` | Personas reales, manos, ojos, emoción humana cercana |
| 5 (CTA) | `cta_portal` | Portal cósmico, neon gateway, luz que llama, arco estelar |

---

## PASO 6 — Ejecutar Pipeline de Render

```bash
# Desde /home/LAB/astrology_factory/
venv/bin/python content_factory/tts_local.py NOMBRE_EVENTO
# Ejemplo: venv/bin/python content_factory/tts_local.py Semana3_Octubre_Lunes
```

**Esto ejecuta en secuencia:**
1. Edge-TTS → `{evento}.mp3`
2. Whisper (small) → `{evento}.ass`
3. `auto_image_finder.py` → assets en bóveda
4. `video_maker.py` Pass 1 → 28 clips `.mkv` (yuv420p, 1080x1920)
5. `video_maker.py` Pass 2 → xfade filter_complex (1.0s crossfade fijo)
6. Audio mixer 528Hz + acentos empáticos
7. Video final → Bóveda → Telegram

---

## REGLAS DE SCORING DE ASSETS — Pirámide Narrativa v5 (Sin Randomness)

El motor puntúa cada archivo con la escena específica como rey absoluto:

| Nivel | Puntos | Criterio | Ejemplo |
|---|---|---|---|
| **0** | **+50 / +25** | Match exacto / parcial del **ID de escena** del storyboard | `[scorpio_symbol_dark]` matchea `scorpio_symbol_dark_pix.jpg` |
| **1** | **+10/palabra** | Palabras de la **escena específica** que está sonando | Query `intense human eye` → `eye_truth.jpg` recibe +20 |
| 2 | +5 | Arquetipo de frase (`raw_realism`, `esoteric_art`, etc.) | Sin cambio respecto a v4 |
| 3 | +2 | Conceptos del tránsito (`emotional_concepts` del JSON) | Antes era +3, ahora es solo fallback |
| 3b | +1 | Triadas generales del tránsito | Antes era +2, solo guía suave |
| **P1** | **-50** | **Cross-render:** usado en las últimas **168h (7 días)** | Evita repetición Lunes→Martes del mismo tránsito |
| P2 | -100 | **In-render:** ya usado en este video | Sin cambio |

> [!CAUTION]
> **"Efecto Oso" — el bug que v5 elimina:** Ocurre cuando el tránsito domina el scoring.
> `stellium_escorpio_dark_transmutation.jpg` recibía +3 (tránsito) y aplastaba
> a `eye_truth.jpg` (+1) aunque el guión pedía un ojo humano.
> Con v5: el ojo recibe +20 (2 palabras × 10) y el oso solo +2 → el ojo gana.
> **Nunca revertir la pirámide ni aumentar el peso del tránsito por encima del de la escena.**

> [!IMPORTANT]
> **Formato de storyboard para activar Nivel 0 (+50):**
> ```
> [scorpio_symbol_dark] intense dark symbol on black background -animal -cartoon
> ```
> El ID entre corchetes activa el match exacto. Sin corchetes, el Nivel 1
> ya corrige el Efecto Oso pero el Nivel 0 queda inactivo.

**PROHIBIDO `random.sample()`.** Los assets se toman en orden de score descendente.

### Memoria Persistente Cross-Render

```python
# Path del historial (se crea automáticamente al primer render):
VAULT_HISTORY_PATH = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/historial_uso_assets.json"
# Formato: { "archivo.jpg": "2026-10-13T18:30:00" }
# Ventana de penalización: 168h (7 días = 1 ciclo semanal completo)
# Auto-limpieza: entradas > 14 días se purgan al guardar (el JSON siempre queda liviano)
```

La **penalización es blanda (-50, no -100)**: si la bóveda está casi vacía, el
asset reciente igual puede ganar sobre uno irrelevante. El sistema siempre
prioriza material fresco, pero nunca queda sin assets.

---

## DETECCIÓN DEL TRÁNSITO — REGLA CRÍTICA

> [!CAUTION]
> El nombre del evento (`Semana3_Octubre_Lunes`) **NO contiene** el nombre del
> tránsito (`stellium_escorpio`). Si el motor usa solo el nombre del evento para
> buscar el tránsito en el JSON, **todos los assets reciben score=0** y el motor
> elige por orden de filesystem → imágenes viejas, flores, cartoons.

**Fuentes de detección (en orden):**
```python
# El motor construye un corpus de texto leyendo TODOS estos archivos:
for src in ['transito.txt', 'guion.txt', 'storyboard.txt']:
    if exists(prod_dir/src):
        event_corpus += open(src).read().lower()

# Luego busca el tránsito con más palabras presentes en el corpus:
best_transit = max(all_transits, key=lambda t:
    count(t.name.words IN event_corpus))
```

**Verificación en consola:** El render debe imprimir:
```
🔭 Tránsito detectado: stellium_escorpio (score=2)
```
Si imprime `⚠️ No se encontró tránsito` → agregar `transito.txt` a la carpeta del evento con el nombre exacto del tránsito.

## TABLA DE TRANSICIONES xfade POR ASPECTO

La duración es **siempre `XFADE_DUR` = 0.40s fijo**. Solo varía el tipo:

| Aspecto | xfade | Lógica |
|---|---|---|
| **Conjunción** | `dissolve` | Fusión lenta — ambas imágenes superpuestas |
| **Trígono** | `fade` | Flujo armónico, transición natural |
| **Sextil** | `pixelize` | Oportunidad que aparece |
| **Cuadratura** | `fadeblack` | Tensión — ÚNICO caso válido para negro |
| **Oposición** | `slideleft` | Polaridad, fuerzas contrarias |
| **Quincuncio** | `pixelize` | Ajuste incómodo |
| **Stellium** | `dissolve` | Como conjunción |

> [!CAUTION]
> **NUNCA** aplicar `fadeblack` por keywords de escena (`dark`, `shadow`, etc.).
> `fadeblack` = imagen→negro→imagen. Eso crea el "vacío negro" entre imágenes
> que el usuario rechazó. El aspecto astrológico es la ÚNICA variable.
> Escorpio es conjunción → `dissolve` → fundido real entre imágenes.

## TIMING EDITORIAL (Constantes en video_maker.py)

```python
XFADE_DUR     = 0.40  # Crossfade de 0.4s — dissolve suave
FADE_DUR      = XFADE_DUR  # ⚠️ INVARIANTE: SIEMPRE igual a XFADE_DUR
                            # Si FADE_DUR ≠ XFADE_DUR → video más corto que audio
MAX_IMAGE_DUR = 3.0   # 3s por clip → ~2.6s visibles + 0.4s crossfade
MAX_VIDEO_DUR = 5.0   # 5s por clip → ~4.6s visibles
MIN_CLIP_DUR  = 0.80  # Mínimo absoluto (XFADE_DUR + margen)
```

**Math del timing (para entender el invariante):**
```
total_video = Σ(clip_dur_i) - (N-1) × XFADE_DUR
cada clip_dur_i = whisper_block_dur_i + FADE_DUR

Si FADE_DUR = XFADE_DUR:
  total_video ≈ Σ(whisper_block_dur_i) = audio_duration ✅

Si FADE_DUR = 0 y XFADE_DUR = 1.0:
  total_video = audio_dur - (N-1)×1.0 → con 28 clips: 43s - 27s = 16s ❌
```

---

## FILTRO ROBUSTO DE BÓVEDA

```python
valid_vault_files = [
    f for f in vault_files
    if os.path.isfile(f)              # sigue symlinks → descarta rotos
    and os.path.getsize(f) > 50_000  # mínimo 50KB
    and not f.endswith("_frame.jpg")  # excluir frames temporales de scoring
]
```

**Por qué `isfile` y no `exists`:** `os.path.exists()` devuelve `True` para symlinks rotos. `os.path.isfile()` sigue el symlink y verifica que el archivo destino exista físicamente. Los symlinks rotos producen frames negros en el render.

---

## CALIDAD DE BÓVEDA — Mantenimiento y Scraper Blindado

> [!IMPORTANT]
> El scoring v5 es correcto, pero **no puede elegir mejor que el material disponible**.
> Si la bóveda tiene un oso animado etiquetado como `cta_portal_cosmic.jpg`, el motor
> lo va a elegir porque el nombre matchea. La solución es la calidad del inventario.

### Filtros obligatorios del scraper (ya implementados)

```python
# Se agregan a TODAS las queries antes de enviarlas a Pixabay/Pexels:
EXCLUSION_QUERY_SUFFIX = " -cartoon -cute -kids -bear -baby -child -vector -clipart"

# Filtro post-API en Pixabay: si los tags contienen estos términos → descartar:
BAD_TAGS = ["cartoon", "cute", "kids", "child", "baby", "bear", "bunny", "kawaii"]

# Pixabay: usar image_type=photo para assets realistas (no illustration)
# Usar search_pixabay_illustrations() SOLO para escenas esotéricas/abstractas
```

**NUNCA quitar estas exclusiones** aunque parezca que "limitan los resultados" — son la barrera contra la basura.

### Protocolo de limpieza de bóveda (antes de cada sprint masivo)

```bash
VAULT="/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"

# 1. Detectar candidatos por nombre:
ls "$VAULT" | grep -iE "(child|baby|cute|kids|cartoon|bear|toy|doll|puppet|bunny|kawaii)"

# 2. Mover a cuarentena (NUNCA borrar directamente):
mkdir -p "$VAULT/../_cuarentena"
mv "$VAULT/archivo_sospechoso.jpg" "$VAULT/../_cuarentena/"
# El registry.json conserva el ID → el scraper no lo re-descarga
```

> [!CAUTION]
> **Nunca `rm` directo sobre assets.** Usar `_cuarentena/` siempre.
> Razón: `registry.json` registra los IDs descargados. Si borrás el archivo
> sin limpiar el registry, el scraper cree que ya lo tiene y nunca lo reemplaza.
> Con cuarentena, el asset queda fuera del scoring pero el registry sigue intacto.

### Señal de alerta: oso o imagen rara en el render

Si aparece una imagen indeseable → diagnóstico en orden:
1. ¿El storyboard usa `[scene_id]` exacto? → ¿ese ID existe en la bóveda como archivo malo?
2. ¿El nombre del archivo malo tiene palabras del query de la escena?
3. Mover a `_cuarentena/`, re-renderizar

---

## PROHIBICIONES ABSOLUTAS

- ❌ Carta natal en tránsitos generales
- ❌ `random.sample()` para seleccionar assets
- ❌ Imágenes repetidas en el mismo video
- ❌ Clips `.ts` en Pass 2 con `xfade` (usar `.mkv` + `yuv420p`)
- ❌ `-c:v copy` en el Pass 2 (prohíbe filtros de video)
- ❌ Assets < 50KB o symlinks rotos
- ❌ Imágenes de oficinas, gimnasios, gente feliz genérica, íconos YouTube
- ❌ Clipart, vectores, estética kids, cartoons

---

## APERTURA PARA PERSONALIZACIÓN FUTURA (Carta Natal)

> Este sistema está diseñado para tránsitos colectivos. Cuando se incorporen videos personalizados (carta natal individual), el `PHRASE_TO_ARCHETYPE` podrá extenderse con categorías como `natal_house`, `natal_aspect`, `personal_planet`. El motor de scoring ya acepta esta extensión sin modificar la lógica base.

---

*Creado: 2026-09-19 | Versión: 1.0 | Aprobado por: Tomás (Portal Tarot Místico)*
