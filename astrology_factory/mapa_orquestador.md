# 🧭 MAPA ORQUESTADOR V2 — "La Navaja Suiza Fractal"
## GPS del Enjambre · Astrology Engine V2

> **REGLA ABSOLUTA PARA LA IA EJECUTORA (FLASH):**
> JAMÁS improvises un comando FFmpeg. JAMÁS. Si necesitas renderizar, transformar, cortar o unir algo,
> DEBES invocar el script correspondiente con `--opcion N`. Este archivo es tu única brújula.
> Si el script que necesitas no existe aún, reporta la ausencia y espera instrucciones.

---

## 📦 ESTRUCTURA DE RUTAS CANÓNICAS

```
/home/tomas2/MediaContingencia/Privada/Astrology_Vault/
├── Descargas_Crudas/          ★ CUARENTENA — assets recién descargados, NO tocar directamente
│   └── <Semana_Prefijo>/      ← salida de recolector_visual.py
├── Assets_Reusables/          ← Bóveda de assets crudos (SOLO LECTURA hasta auditoría)
│   └── <Semana_Prefijo>/      ← ej. Oct_W1/
├── Assets_Auditados/          ← Assets aprobados, renombrados y listos (salida de Célula 0)
│   └── <Semana_Prefijo>/
├── glitch_abstracto/          ← Assets rotos convertidos en arte de transición
├── audio_master/              ← TTS + mezclas (salida de Célula 1)
├── subtitulos/                ← .ass y .srt generados (salida de Célula 1)
├── timeline_huecos/           ← JSONs de tiempos matemáticos (salida de Célula 1)
├── Videos_Finales/
│   └── <Semana_Prefijo>/
│       └── FINAL_<Evento>.mp4
└── temp/                      ← Archivos temporales
```

/home/LAB/astrology_factory/
├── mapa_orquestador.md        ← ESTE ARCHIVO (no modificar sin autorización)
├── contexto_astrologico.json  ← ADN activo del video en curso
├── PROJECT_RULES.md           ← Reglas permanentes del proyecto
├── content_factory/
│   └── video_maker.py         ← [MOTOR] Renderizador FFmpeg Single-Pass
└── v2/                        ← Todos los scripts Navaja Suiza V2
    ├── celula_0/
    │   ├── recolector_visual.py   ← [0.0] NUEVO: descarga a cuarentena
    │   ├── auditor_boveda.py      ← [0.1] audita, aprueba y llena SQLite
    │   └── fusionador_visual.py   ← [0.2] transforma y crea
    ├── celula_1/
    │   ├── generador_guiones.py
    │   └── cronometrador_y_tts.py
    ├── celula_2/
    │   ├── nodriza_autonoma.py        ← [Daemon] Scraper, arte IA y catalogador
    │   ├── nodriza_visual.py          ← [2.1] Ensamblador semántico y fractal
    │   └── validador_de_ensamble.py   ← [2.2] Check matemático y output a video_maker
    └── celula_4/
        ├── generador_metadata.py
        ├── publicador_mock.py
        └── IDEA_TOKENIZACION_WEB3.md  ← Idea: Tokenización / Acuñadora NFT

---

## 🗺️ DIRECTORIO DE SCRIPTS — REFERENCIA RÁPIDA

| Script | Célula | Función Principal |
| :----- | :----- | :---------------- |
| `recolector_visual.py` | 🌑 0 | **[PASO 0]** Descarga assets temáticos a cuarentena /Descargas_Crudas/ |
| `auditor_boveda.py` | 🌑 0 | Limpia, audita con Gemini Vision, llena SQLite y promueve a la bóveda |
| `fusionador_visual.py` | 🌑 0 | Transforma y crea nuevos assets visuales |
| `generador_guiones.py` | 🌒 1 | Escribe el guion a partir del ADN JSON |
| `cronometrador_y_tts.py` | 🌒 1 | Genera TTS, subtítulos y el JSON de tiempos |
| `nodriza_autonoma.py` | 🌓 2 | [Daemon] Control de bóveda, recolección periódica y catalogación asíncrona |
| `nodriza_visual.py` | 🌓 2 | Matching semántico consultando SQLite, genera lista de corte pura |
| `validador_de_ensamble.py` | 🌓 2 | Audita JSON, chequea rutas, emite `lista_de_corte_validada.json` |
| `video_maker.py` | 🎬 | **Motor de Render.** Toma el JSON validado y ejecuta 1 solo comando FFmpeg |
| `generador_metadata.py` | 🪐 4 | Prepara metadata SEO (títulos, tags, descripción) |
| `publicador_mock.py` | 🪐 4 | Sube a YouTube (vía API) y actualiza estados |

---

## 🌑 CÉLULA MADRE 0: Laboratorio y Curaduría Visual

> **FLUJO INTERNO DE CÉLULA 0:**
> `recolector_visual.py` (descarga) → `auditor_boveda.py` (aprueba) → `fusionador_visual.py` (transforma)
> NUNCA saltar el recolector descargando assets a mano directamente a /Assets_Reusables/.

---

### Script `v2/celula_0/recolector_visual.py`
*Obtiene assets crudos. Destino exclusivo: /Descargas_Crudas/. JAMÁS toca la bóveda real.*
*API KEY de Gemini guardada en .env — nunca hardcodeada.*

```
python v2/celula_0/recolector_visual.py --opcion 1           # Búsqueda temática alineada al ADN
python v2/celula_0/recolector_visual.py --opcion 1 --max 10  # Hasta 10 assets por query
python v2/celula_0/recolector_visual.py --opcion 2           # Scraping arquetipos puros (planetas)
python v2/celula_0/recolector_visual.py --opcion 3           # Clonar repositorios de arte esotérico
python v2/celula_0/recolector_visual.py --opcion 4           # Purga de /Descargas_Crudas/
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | contexto_astrologico.json | /Descargas_Crudas/<semana>/ | Lee palabras_clave + palabras_visuales + arquetipos del ADN. Busca en Pexels + Pixabay + NASA. Registry de sesión por semana (no global). |
| 2 | contexto_astrologico.json | /Descargas_Crudas/<semana>/ | Queries de planetas puros, nebulosas, geometría sagrada, símbolos esotéricos. Prioriza NASA (dominio público). |
| 3 | Repos configurados en el script | /Descargas_Crudas/<semana>/ | Clona NASA Image Library, Wikimedia Commons histórico esotérico. Solo licencias permisivas verificadas. |
| 4 | /Descargas_Crudas/<semana>/ | (vacío) | Purga la cuarentena para reiniciar búsqueda. Requiere confirmación doble. |

---

### Script `v2/celula_0/auditor_boveda.py`
*Prepara los assets y puebla la Base de Datos Visual SQLite.*

```
python v2/celula_0/auditor_boveda.py --opcion 1   # Filtro Interactivo manual [Y/N/R]
python v2/celula_0/auditor_boveda.py --opcion 2   # Limpieza de basura (symlinks rotos, <50KB)
python v2/celula_0/auditor_boveda.py --opcion 3   # Reciclador Artístico → /glitch_abstracto
python v2/celula_0/auditor_boveda.py --opcion 4   # Extractor de keyframes de videos largos
python v2/celula_0/auditor_boveda.py --opcion 5   # Auditoría IA Masiva y Registro SQLite
```

---

### Script `v2/celula_0/fusionador_visual.py`
*Crea y transforma assets. No toca audio ni tiempos.*

```
python v2/celula_0/fusionador_visual.py --opcion 1   # Crop 9:16 inteligente
python v2/celula_0/fusionador_visual.py --opcion 2   # Collage Kinético Elíptico
python v2/celula_0/fusionador_visual.py --opcion 3   # Glitch Subliminal
python v2/celula_0/fusionador_visual.py --opcion 4   # Animador de Estáticas (Ken Burns)
```

---

## 🌒 CÉLULA MADRE 1: Narrativa, Voz y Tiempos

### Script `v2/celula_1/generador_guiones.py`
*Escribe el guion. Lee el ADN. No toca audio ni video.*

```
python v2/celula_1/generador_guiones.py --opcion 1   # Guion diario (tránsito del día)
python v2/celula_1/generador_guiones.py --opcion 2   # Guion semanal/resumen
python v2/celula_1/generador_guiones.py --opcion 3   # Guion horóscopo personalizado
python v2/celula_1/generador_guiones.py --opcion 4   # Inyector de CTA dinámicos (<5s)
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | contexto_astrologico.json | /temp/guion_<evento>.json | Guion diario: N tomas JSON estructuradas (rol, texto, etiqueta_visual). Inyecta efemérides reales con EphemerisCalculator. |
| 2 | contexto_astrologico.json | /temp/guion_<evento>_semanal.json | Guion semanal condensado en 5 tomas. Narrativa de los tránsitos de la semana. |
| 3 | contexto_astrologico.json + --natal /ruta.json | /temp/guion_<evento>_personal_<nombre>.json | Horóscopo personalizado. Contrasta carta natal real vs tránsito activo. Sin datos mock. |
| 4 | /temp/guion_<evento>.json | Guion modificado in-place | Reemplaza la toma de CTA por uno nuevo generado (<15 palabras, <5s). |

---

### Script `v2/celula_1/cronometrador_y_tts.py`
*El corazón matemático. Genera audio y tiempos. No renderiza video.*

```
python v2/celula_1/cronometrador_y_tts.py --opcion 1   # Síntesis TTS → MP3
python v2/celula_1/cronometrador_y_tts.py --opcion 2   # Subtítulos .ass (TikTok/cinemático)
python v2/celula_1/cronometrador_y_tts.py --opcion 3   # Subtítulos .srt clásicos
python v2/celula_1/cronometrador_y_tts.py --opcion 4   # MAPEO GAPLESS → timeline_huecos.json
```

> **REGLA GAPLESS:** La Opción 1 produce el `timeline_huecos.json` SAGRADO.
> El timing lo decide SOLO este script. Ningún otro script de las Células 2 cambia duraciones.

---

## 🌓 CÉLULA MADRE 2: Inteligencia de Asignación (El Matching)

### Script `v2/celula_2/nodriza_autonoma.py` (Daemon)
*Se ejecuta en segundo plano (Fase A: Recolecta cada 1h / Fase B: Cataloga cada 5m).*

### Script `v2/celula_2/nodriza_visual.py`
*Consulta la base de datos `assets_visuales.db` y asigna assets semánticamente a los huecos.*

```bash
python v2/celula_2/nodriza_autonoma.py                 # Ejecuta el Daemon en background
python v2/celula_2/nodriza_visual.py --opcion 1        # Match y renderiza lista de corte
```

---

### Script `v2/celula_2/validador_de_ensamble.py`
*El guardián matemático. Audita existencia y genera JSON puro de instrucciones.*

```
python v2/celula_2/validador_de_ensamble.py --opcion 1   # Dry-run: existencia
python v2/celula_2/validador_de_ensamble.py --opcion 2   # Calcula instrucciones trim/loop
python v2/celula_2/validador_de_ensamble.py --opcion 3   # Reporte final → lista_de_corte_validada.json
```

> **REGLA:** Usar `--opcion 3` siempre en producción.

---

## 🎬 MOTOR DE RENDER FINAL (FFmpeg Single-Pass)

> AVISO: Este script es el ÚNICO lugar donde se ejecuta FFmpeg para ensamblar el video final.
> No razona, no elige assets, no corrige. Solo ejecuta lo que el JSON validado dictamina.

### Script `content_factory/video_maker.py`

```bash
python content_factory/video_maker.py
```

| Entrada | Salida | Descripción |
| :------ | :----- | :---------- |
| `/temp/lista_de_corte_validada_<evento>.json` | `FINAL_<evento>.mp4` en bóveda | **Single-Pass Rendering.** Construye un único `filter_complex`. Aplica `zoompan` al vuelo a las imágenes estáticas, procesa color grading, xfade encadenado y quema subtítulos. Todo en un solo comando. |

---

## 🪐 CÉLULA MADRE 4: Redes, Distribución y Tokenización (Web3)

### Script `v2/celula_4/generador_metadata.py` & `publicador_mock.py`
*Generación de descripciones SEO, tags, y subida a plataformas (YouTube/TikTok).*

### 💡 NUEVA IDEA: La Célula Acuñadora de NFTs (Web3)
*Detalles en: `v2/celula_4/IDEA_TOKENIZACION_WEB3.md`*

---

## 🔁 FLUJO CANÓNICO COMPLETO

```
╔══════════════════════════════════════════════════════════╗
║  FASE PRE-PRODUCCIÓN: Guion + Audio + Assets             ║
╠══════════════════════════════════════════════════════════╣
[1]  Editar contexto_astrologico.json           ← ADN del video (evento, colores, keywords)

[2]  generador_guiones.py --opcion 1            ← Guion diario (lee el ADN)
[3]  cronometrador_y_tts.py --opcion 1          ← TTS → MP3 + timeline_huecos.json
[4]  cronometrador_y_tts.py --opcion 2          ← Whisper → .ass
╠══════════════════════════════════════════════════════════╣
║  FASE RECOLECCIÓN: Descarga temática alineada al guion   ║
╠══════════════════════════════════════════════════════════╣
[5]  recolector_visual.py --opcion 1            ← Descarga temática (ADN → /Descargas_Crudas/)
╠══════════════════════════════════════════════════════════╣
║  FASE AUDITORÍA: Cuarentena → Bóveda (SQLite)            ║
╠══════════════════════════════════════════════════════════╣
[6]  auditor_boveda.py --opcion 5               ← Audita con IA y guarda etiquetas en DB SQLite
╠══════════════════════════════════════════════════════════╣
║  FASE MATCHING: Assets ↔ Tiempos                         ║
╠══════════════════════════════════════════════════════════╣
[7]  nodriza_visual.py --opcion 1               ← Match assets vía SQLite
[8]  validador_de_ensamble.py --opcion 3        ← Check matemático y emite validación final
╠══════════════════════════════════════════════════════════╣
║  FASE RENDER: FFmpeg Single-Pass                          ║
╠══════════════════════════════════════════════════════════╣
[9]  video_maker.py                             ← Lee lista validada y ensambla todo al vuelo.
╚══════════════════════════════════════════════════════════╝
```

---

## 🚨 ERRORES PROHIBIDOS (LECCIONES DEL V1 + V2)

| NUNCA hagas esto | HAZ esto en su lugar |
| :--- | :--- |
| Pre-renderizar imágenes (transmutar a MP4) | Pasar el path crudo del JPG y usar `zoompan` dinámico en video_maker. |
| Buscar archivos con `glob` para asignar | Usar consultas a la base de datos `assets_visuales.db`. |
| Hardcodear la API Key de Gemini en el código | Siempre leer de .env con os.getenv("GEMINI_API_KEY") |
| Mover o renombrar la Bóveda | La ruta de la Bóveda es SAGRADA e INAMOVIBLE |
