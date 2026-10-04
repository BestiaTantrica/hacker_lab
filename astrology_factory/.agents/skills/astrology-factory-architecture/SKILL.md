---
name: astrology-factory-architecture
description: >-
  Mapa completo de arquitectura, módulos, convenciones y decisiones de diseño
  de la Astrology Factory V2. Activar cuando se modifique cualquier célula del
  pipeline, se agregue un módulo, o se debuguee el flujo de producción.
---

# Astrology Factory V2 — Arquitectura y Convenciones

## Estructura de Células

| Célula | Directorio         | Responsabilidad                                      |
|--------|--------------------|------------------------------------------------------|
| 0      | `v2/celula_0/`     | Clasificación y auditoría de assets (imágenes/video) |
| 1      | `v2/celula_1/`     | TTS, subtítulos Whisper, cronometrado                |
| 2      | `v2/celula_2/`     | Matching semántico + Director de Arte                |
| 3      | `v2/celula_3/`     | Ensamble FFmpeg final                                |

## Archivos Clave

```
v2/
├── cuota.py                            ← FRENO: gestor central de cuota Gemini
├── celula_0/
│   ├── auto_clasificador_ia.py         ← Clasifica: categoría 01-09 o 00 (descarte)
│   ├── nodriza_auditora.py             ← Demonio: lanza clasificador cada 15 min
│   └── generador_stock_sonoro.py
├── celula_2/
│   ├── nodriza_visual.py               ← Matching asset↔beat narrativo
│   ├── director_de_arte.py             ← Emoción + transición por beat (sin API)
│   └── validador_de_ensamble.py
└── celula_3/
    └── ensamblador_final.py            ← xfade gapless + mux audio
```

## Flujo de Producción

```
[Audio TTS] → celula_1 → {audio_master/, subtitulos/}
[Assets]    → celula_0 → Assets_Auditados/
[Timeline]  → celula_2 (nodriza_visual + director_de_arte)
                    ↓ lista_de_corte_{evento}.json
             celula_3 → MASTER_{evento}.mp4
```

## Sistema de Cuota (`cuota.py`)

- Keys: todas las `GEMINI_API_KEY*` del `.env`, **excepto** `_WEB`
- Estado persistido en `estado_cuota.json` (con `fcntl` lock multiproceso)
- Si AGOTADO → script sale con `sys.exit(0)`, no reintenta, no alerta
- Las 10 keys comparten cuota GCP: ~1500 req/día free tier
- Rotar keys = resiliencia, NO más cuota

## Director de Arte (`director_de_arte.py`)

**Costo de API: $0. Trabaja con vocabulario local.**

| Emoción          | xfade          | Tags visuales ideales               |
|------------------|----------------|-------------------------------------|
| `fuego`          | `fade`         | llama, cosmos, supernova, rojo      |
| `agua`           | `dissolve`     | océano, luna, cristal, azul         |
| `tierra`         | `smoothleft`   | piedra, mandala, geometría, oscuro  |
| `aire`           | `fadewhite`    | cosmos, galaxia, fractal, luz       |
| `misterio`       | `fadeblack`    | sombra, eclipse, humo, runa         |
| `revelacion`     | `fadewhite`    | luz, dorado, sol, espiral           |
| `llamada_accion` | `smoothleft`   | fractal, abstracto, fondo           |

```python
from celula_2.director_de_arte import (
    enriquecer_tomas,        # añade emocion/tags/transicion a lista de tomas
    score_semantico,         # bonus matching [0..3]
    opacidad_boost,          # ajuste alpha por emoción [±0.12]
    transicion_para_emocion, # nombre xfade para FFmpeg
)
```

## Categorías de Clasificación de Assets

- `"00"` → `Cuarentena_Visual/` (NUNCA borrar; solo mover)
- `"01"`–`"09"` → `Assets_Auditados/Imagenes/<categoria>/`

**Siempre rechazar:** familias, parejas, bebés, niños, selfies, bodas, personas cotidianas.

**Falsos positivos NASA (NO rechazar):** fotos con "baby nebula", "familiar beauty",
"earth smiled" en el TÍTULO del archivo — son imágenes espaciales válidas.

## Convenciones FFmpeg (ensamblador_final.py)

- Intra-toma: `fade` / `dissolve`, duración 0.2s
- Inter-toma: transición del Director de Arte, duración 0.8s
- Timing: xfade CENTRADO en el límite narrativo (no en el inicio del clip)
- Padding: `tpad=stop_mode=clone` cubre el solapamiento sin introducir negro
- `lista_de_corte_{evento}.json` lleva el campo `"transicion_entrada"` por toma

## Servicios systemd

```
nodriza_auditora.service   → ACTIVO    (Restart=on-failure, limit 3/5min)
nodriza_autonoma.service   → DISABLED  (duplicado — no reactivar)
```

Diagnóstico rápido:
```bash
systemctl --user status nodriza_auditora
journalctl --user -u nodriza_auditora -f
```

## Variables de Entorno (`.env`)

```
GEMINI_API_KEY_1 … _10   → pool (mismo proyecto GCP, cuota compartida)
GEMINI_API_KEY_WEB        → excluir de producción (solo para web)
GEMINI_API_KEY_TEXT       → texto / embeddings
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID → alertas (no abusar)
```

## Principios del Proyecto

- **Emoción primero:** el relato manda; las imágenes acompañan el beat
- **Imagen íntima al texto:** cada cambio de emoción narrativa = cambio de imagen
- **Sin personas cotidianas:** canal de astrología esotérica, no lifestyle
- **Voz AR:** `es-AR-TomasNeural` o Piper `es_AR`
- **Velocidad de API:** lento pero constante; nunca quemar el free tier de golpe
