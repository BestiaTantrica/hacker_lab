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
├── microclips/                ← Clips procesados con color grading (salida de 3.1)
├── audio_master/              ← TTS + mezclas finales (salida de 1.2 y 3.2)
├── subtitulos/                ← .ass y .srt generados (salida de 1.2)
├── timeline_huecos/           ← JSONs de tiempos matemáticos (salida de 1.2 opcion 4)
├── Videos_Finales/
│   └── <Semana_Prefijo>/
│       └── FINAL_<Evento>.mp4
└── temp/                      ← Archivos temporales (se limpian con 3.3 opcion 4)

/home/LAB/astrology_factory/
├── mapa_orquestador.md        ← ESTE ARCHIVO (no modificar sin autorización)
├── contexto_astrologico.json  ← ADN activo del video en curso
├── PROJECT_RULES.md           ← Reglas permanentes del proyecto
└── v2/                        ← Todos los scripts Navaja Suiza V2
    ├── celula_0/
    │   ├── recolector_visual.py   ← [0.0] NUEVO: descarga a cuarentena
    │   ├── auditor_boveda.py      ← [0.1] audita y aprueba
    │   └── fusionador_visual.py   ← [0.2] transforma y crea
    ├── celula_1/
    │   ├── generador_guiones.py
    │   └── cronometrador_y_tts.py
    ├── celula_2/
    │   ├── nodriza_autonoma.py        ← [Daemon] Scraper, arte IA y catalogador
    │   ├── nodriza_visual.py          ← [2.1] Ensamblador semántico y fractal
    │   └── validador_de_ensamble.py
    ├── celula_3/
    │   ├── fabrica_microclips.py
    │   ├── mezclador_sonoro.py
    │   └── ensamblador_final.py
    └── celula_4/
        ├── generador_metadata.py
        ├── publicador_mock.py
        └── IDEA_TOKENIZACION_WEB3.md  ← Idea: Tokenización / Acuñadora NFT
```

---

## 🗺️ DIRECTORIO DE SCRIPTS — REFERENCIA RÁPIDA

| Script | Célula | Función Principal |
| :----- | :----- | :---------------- |
| `recolector_visual.py` | 🌑 0 | **[PASO 0]** Descarga assets temáticos a cuarentena /Descargas_Crudas/ |
| `auditor_boveda.py` | 🌑 0 | Limpia, audita con Gemini Vision y promueve a la bóveda |
| `fusionador_visual.py` | 🌑 0 | Transforma y crea nuevos assets visuales |
| `generador_guiones.py` | 🌒 1 | Escribe el guion a partir del ADN JSON |
| `cronometrador_y_tts.py` | 🌒 1 | Genera TTS, subtítulos y el JSON de tiempos |
| `nodriza_autonoma.py` | 🌓 2 | [Daemon] Control de bóveda, recolección periódica y catalogación asíncrona |
| `nodriza_visual.py` | 🌓 2 | Matching semántico fractal, opacidad y preparación de chunks |
| `validador_de_ensamble.py` | 🌓 2 | Audita y bloquea errores matemáticos pre-render |
| `fabrica_microclips.py` | 🌔 3 | Renderiza clips individuales con color grading |
| `mezclador_sonoro.py` | 🌔 3 | Mezcla audio (voz + música + SFX) |
| `ensamblador_final.py` | 🌔 3 | Ensambla el master final gapless |
| `generador_metadata.py` | 🪐 4 | Prepara metadata SEO (títulos, tags, descripción) |
| `publicador_mock.py` | 🪐 4 | Sube a YouTube (vía API) y actualiza estados |
| *(Futuro)* `minting_nft.py` | 🪐 4 | *Boceto: Automatiza la acuñación Web3 de los videos/assets* |

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

> **Por qué existe /Descargas_Crudas/:**
> En V1, el scraper descargaba directo a /Assets_Reusables/ contaminando assets buenos con basura.
> Ahora TODO pasa por cuarentena → auditoría → bóveda. Sin atajos.

---

### Script `v2/celula_0/auditor_boveda.py`
*Prepara los assets. No toca tiempos ni audio.*

```
python v2/celula_0/auditor_boveda.py --opcion 1   # Auditoría Gemini Vision (renombrado IA)
python v2/celula_0/auditor_boveda.py --opcion 2   # Filtro Interactivo manual [Y/N/R]
python v2/celula_0/auditor_boveda.py --opcion 3   # Limpieza de basura (symlinks rotos, <50KB)
python v2/celula_0/auditor_boveda.py --opcion 4   # Reciclador Artístico → /glitch_abstracto
python v2/celula_0/auditor_boveda.py --opcion 5   # Extractor de keyframes de videos largos
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | /Assets_Reusables/<semana>/ | Archivos renombrados in-place | Gemini Vision describe el contenido y renombra |
| 2 | /Assets_Reusables/<semana>/ | Aprobados / eliminados / renombrados | Visor nativo con teclado [Y]=aprobar [N]=borrar [R]=renombrar |
| 3 | /Assets_Reusables/<semana>/ | Archivos borrados | Elimina symlinks rotos, archivos <50KB y formatos irrecuperables |
| 4 | /Assets_Reusables/<semana>/ | /glitch_abstracto/<semana>/ | Salva archivos rotos saturando colores según emoción del ADN JSON |
| 5 | Video largo (path directo) | /keyframes/<nombre>/ | Exporta frames PNG cada N segundos |

---

### Script `v2/celula_0/fusionador_visual.py`
*Crea y transforma assets. No toca audio ni tiempos.*

```
python v2/celula_0/fusionador_visual.py --opcion 1   # Crop 9:16 inteligente
python v2/celula_0/fusionador_visual.py --opcion 2   # Collage Kinético Elíptico
python v2/celula_0/fusionador_visual.py --opcion 3   # Glitch Subliminal
python v2/celula_0/fusionador_visual.py --opcion 4   # Animador de Estáticas (Ken Burns)
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | Imagen/video apaisado | /Assets_Auditados/<semana>/ | Crop vertical 9:16 centrando la acción |
| 2 | 3-6 imágenes | collage_kinetico.mp4 | Sistema orbital con movimiento perpetuo, sin frames negros |
| 3 | Asset limpio (path) | glitch_<nombre>.mp4 | Crea flashes de 0.08s con aberración cromática o inversión negativa |
| 4 | Imagen JPG/PNG | anim_<nombre>.mp4 | Efecto Ken Burns (pan & zoom cinemático) |

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
| 3 | contexto_astrologico.json + --natal /ruta.json | /temp/guion_<evento>_personal_<nombre>.json | Horóscopo personalizado. Contrasta carta natal real vs tránsito activo. Sin datos mock. Default: carta natal de Tomás. |
| 4 | /temp/guion_<evento>.json | Guion modificado in-place | Reemplaza la toma de CTA por uno nuevo generado (<15 palabras, <5s). Fallback a pool local si Gemini no responde. |

---

### Script `v2/celula_1/cronometrador_y_tts.py`
*El corazón matemático. Genera audio y tiempos. No renderiza video.*

```
python v2/celula_1/cronometrador_y_tts.py --opcion 1   # Síntesis TTS → MP3
python v2/celula_1/cronometrador_y_tts.py --opcion 2   # Subtítulos .ass (TikTok/cinemático)
python v2/celula_1/cronometrador_y_tts.py --opcion 3   # Subtítulos .srt clásicos
python v2/celula_1/cronometrador_y_tts.py --opcion 4   # MAPEO GAPLESS → timeline_huecos.json
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | /temp/guion_<evento>.json | /audio_master/<evento>.mp3 + /timeline_huecos/<evento>.json | **TODO EN UNO:** Sintetiza un MP3 por toma (edge-tts), mide con ffprobe, concatena y genera el timeline gapless. Sin Whisper, matemática pura. |
| 2 | /audio_master/<evento>.mp3 | /subtitulos/<evento>.ass | Whisper → .ass cinemático estilo karaoke TikTok. Timestamps por palabra. Colores del ADN. |
| 3 | /audio_master/<evento>.mp3 | /subtitulos/<evento>.srt | Whisper → .srt clásico para YouTube. |
| 4 | /temp/guion_<evento>.json + audio maestro | /timeline_huecos/<evento>.json | Recalcula el timeline sin re-sintetizar. Si no hay MP3 de tomas, distribuye por proporción de palabras. |

> **REGLA GAPLESS:** La Opción 1 produce el `timeline_huecos.json` SAGRADO.
> El timing lo decide SOLO este script. Ningún otro script de las Células 2 o 3 cambia duraciones.

---

## 🌓 CÉLULA MADRE 2: Inteligencia de Asignación (El Matching)

### Script `v2/celula_2/nodriza_autonoma.py` (Daemon)
*Se ejecuta en segundo plano (Fase A: Recolecta cada 1h / Fase B: Cataloga cada 5m).*
*Usa Hydra keys. Controla límite de 50GB.*

### Script `v2/celula_2/nodriza_visual.py`
*Lee el catálogo asíncrono y hace matching semántico. Crea los chunks fractales.*

```bash
python v2/celula_2/nodriza_autonoma.py                 # Ejecuta el Daemon en background
python v2/celula_2/nodriza_visual.py --opcion 1        # Match y renderiza lista de corte
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | timeline_huecos.json + /Assets_Auditados/<semana>/ | /temp/lista_de_corte_<evento>.json | Gemini recibe nombres de video + narrativa de cada toma y elige el más apropiado. Fallback a random si Gemini falla. |
| 2 | timeline_huecos.json + /Assets_Auditados/<semana>/ | /temp/lista_de_corte_<evento>.json | Busca el nombre de etiqueta_visual en el nombre del archivo. Si no hay match, fallback random sin repetir contiguos. |
| 3 | timeline_huecos.json + /Assets_Auditados/<semana>/ | /temp/lista_de_corte_<evento>.json | Aleatorio puro, garantizando que no se repita el mismo video en tomas contiguas. Ideal para glitch art. |
| 4 | timeline_huecos.json + /Assets_Auditados/ (todas) | /temp/lista_de_corte_<evento>.json | Si el stock de la semana es insuficiente, amplía la búsqueda a semanas pasadas. Usa Gemini si hay API o random si no. |

---

### Script `v2/celula_2/validador_de_ensamble.py`
*El guardián matemático. No renderiza. Solo audita y anota instrucciones para Célula 3.*
*Su salida es el archivo SAGRADO que usará fabrica_microclips.py.*

```
python v2/celula_2/validador_de_ensamble.py --opcion 1   # Dry-run: existencia + duración con ffprobe
python v2/celula_2/validador_de_ensamble.py --opcion 2   # Calcula instrucciones trim/loop
python v2/celula_2/validador_de_ensamble.py --opcion 3   # Reporte final → lista_de_corte_validada.json
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | /temp/lista_de_corte_<evento>.json | Reporte en consola | Verifica existencia física y lee duración real con ffprobe. Detecta archivos corruptos y faltantes. |
| 2 | /temp/lista_de_corte_<evento>.json | Lista enriquecida en memoria | Por cada toma: si video >= hueco → trim. Si video < hueco → loop (calcula num_loops). Inyecta start_trim_ms / end_trim_ms. |
| 3 | /temp/lista_de_corte_<evento>.json | /temp/lista_de_corte_validada_<evento>.json | Ejecuta Opción 1 + 2 internamente. Genera el JSON final con TODAS las instrucciones fusionadas. Bloquea si anti-spam >10 clips. |

> **REGLA:** Usar `--opcion 3` siempre en producción. Las opciones 1 y 2 son para diagnóstico.

---

## 🌔 CÉLULA MADRE 3: El Motor de Fuerza Bruta (FFmpeg)

> AVISO: Estos scripts son el ÚNICO lugar donde se ejecuta FFmpeg.
> No razonan, no corrigen. Solo ejecutan lo que los JSON de Células 0-2 calcularon y validaron.

### Script `v2/celula_3/fabrica_microclips.py`

```
python v2/celula_3/fabrica_microclips.py --opcion 1   # Render con filtros de color grading
python v2/celula_3/fabrica_microclips.py --opcion 2   # Render raw/limpio sin filtros
python v2/celula_3/fabrica_microclips.py --opcion 3   # Render mudo para archivo
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | asignacion_enriquecida.json | /microclips/<evento>/clip_N_<dur>s.mp4 | Crop 9:16 + Vignette + Color Grading astrológico |
| 2 | asignacion_enriquecida.json | /microclips/<evento>/clip_N_<dur>s.mp4 | Sin filtros de color, solo crop y duración exacta |
| 3 | asignacion_enriquecida.json | /archivo/<evento>/clip_N_mudo.mp4 | Sin audio, para archivo reutilizable |

---

### Script `v2/celula_3/mezclador_sonoro.py`

```
python v2/celula_3/mezclador_sonoro.py --opcion 1   # Voiceover + música de fondo
python v2/celula_3/mezclador_sonoro.py --opcion 2   # Inyecta pad de frecuencias (528Hz)
python v2/celula_3/mezclador_sonoro.py --opcion 3   # Inserta SFX en puntos de transición
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | <evento>.mp3 + música (path) | /audio_master/<evento>_mix.mp3 | Voz + música a -18dB |
| 2 | <evento>_mix.mp3 | /audio_master/<evento>_binaural.mp3 | Añade pad de 528Hz u otra frecuencia del ADN |
| 3 | <evento>_mix.mp3 + timeline_huecos.json | /audio_master/<evento>_sfx.mp3 | Campanillas exactamente en cada transición de toma |

---

### Script `v2/celula_3/ensamblador_final.py`

```
python v2/celula_3/ensamblador_final.py --opcion 1   # Xfade Gapless (disuelto)
python v2/celula_3/ensamblador_final.py --opcion 2   # Corte Duro (sin fade)
python v2/celula_3/ensamblador_final.py --opcion 3   # Quema subtítulos .ass
python v2/celula_3/ensamblador_final.py --opcion 4   # Despliegue: mueve, limpia, notifica
```

| Opción | Entrada | Salida | Descripción |
| :----: | :------ | :----- | :---------- |
| 1 | /microclips/<evento>/ + <evento>_sfx.mp3 | MASTER_<evento>.mp4 | Xfade gapless basado en matemáticas de timeline_huecos.json |
| 2 | /microclips/<evento>/ + <evento>_sfx.mp3 | MASTER_<evento>.mp4 | Concatena con corte duro |
| 3 | MASTER_<evento>.mp4 + <evento>.ass | MASTER_<evento>_sub.mp4 | Quema el .ass sobre el master |
| 4 | MASTER_<evento>_sub.mp4 | FINAL_<evento>.mp4 en bóveda | Mueve a Videos_Finales, limpia /temp/, notifica por Telegram |

---

## 🪐 CÉLULA MADRE 4: Redes, Distribución y Tokenización (Web3)

> AVISO: Esta célula se encarga del empaquetado final, metadata y publicación.
> Actualmente posee scripts básicos de publicación, pero **se encuentra en fase de expansión conceptual** hacia Web3.

### Script `v2/celula_4/generador_metadata.py` & `publicador_mock.py`
*Generación de descripciones SEO, tags, y subida a plataformas (YouTube).*

### 💡 NUEVA IDEA: La Célula Acuñadora de NFTs (Web3)
*Detalles en: `v2/celula_4/IDEA_TOKENIZACION_WEB3.md`*

Se ha propuesto que la Célula 4 extienda su responsabilidad al ecosistema Web3, funcionando como el pipeline de cierre:
1. **Publicación y Subasta:** Mientras el video se publica en YouTube, por detrás se extrae un fotograma clave en alta resolución, o un render especial, y se sube automáticamente a IPFS (Pinata).
2. **Minting Automatizado:** Se emite una transacción hacia un Smart Contract (ERC-721 en Polygon/Arbitrum) para acuñar el activo como NFT ("El Tránsito Astrológico del Día").
3. **Cross-Selling:** La descripción de YouTube inyectada por el generador de metadata incluirá el link directo a la subasta o marketplace (ej. OpenSea).
4. **Pases de Utilidad:** Los NFTs funcionarán también como *Access Tokens* para material premium en Discord/Telegram.

Esta infraestructura descentralizada delega la validación de la red a terceros (Infura/Alchemy) y funciona 100% de fondo sin requerir nodos pesados ni PC especial.

---

## 🔁 FLUJO CANÓNICO COMPLETO

```
╔══════════════════════════════════════════════════════════╗
║  FASE PRE-PRODUCCIÓN: Guion + Audio + Assets             ║
╠══════════════════════════════════════════════════════════╣
[1]  Editar contexto_astrologico.json           ← ADN del video (evento, colores, keywords)

[2]  generador_guiones.py --opcion 1            ← Guion diario (lee el ADN)
[3]  cronometrador_y_tts.py --opcion 1          ← TTS → MP3
[4]  cronometrador_y_tts.py --opcion 2          ← Whisper → .ass
[5]  cronometrador_y_tts.py --opcion 4          ← Mapeo → timeline_huecos.json  ★ SAGRADO
╠══════════════════════════════════════════════════════════╣
║  FASE RECOLECCIÓN: Descarga temática alineada al guion   ║
╠══════════════════════════════════════════════════════════╣
[6]  recolector_visual.py --opcion 1            ← Descarga temática (ADN → /Descargas_Crudas/)
     └ alternativa: --opcion 2 para arquetipos puros (planetas/cosmos)
     └ alternativa: --opcion 3 para clonar repos completos
╠══════════════════════════════════════════════════════════╣
║  FASE AUDITORÍA: Cuarentena → Bóveda                     ║
╠══════════════════════════════════════════════════════════╣
[7]  auditor_boveda.py --opcion 1               ← Gemini Vision audita /Descargas_Crudas/
     └ alternativa: --opcion 2 si se prefiere revisar manualmente
╠══════════════════════════════════════════════════════════╣
║  FASE MATCHING: Assets ↔ Tiempos                         ║
╠══════════════════════════════════════════════════════════╣
[8]  nodriza_visual.py --opcion 1               ← Match assets auditados ↔ huecos (Opacidad fractal)
[9]  validador_de_ensamble.py --opcion 1        ← Check matemático (suma = duración audio)
[10] validador_de_ensamble.py --opcion 2        ← Check anti-spam (bloqueo >7 clips)
╠══════════════════════════════════════════════════════════╣
║  FASE RENDER: FFmpeg (solo ejecuta, no decide)            ║
╠══════════════════════════════════════════════════════════╣
[11] fabrica_microclips.py --opcion 1           ← Render con color grading
[12] mezclador_sonoro.py --opcion 1             ← Mezcla audio
[13] mezclador_sonoro.py --opcion 3             ← SFX en transiciones
[14] ensamblador_final.py --opcion 1            ← Ensamble Xfade Gapless
[15] ensamblador_final.py --opcion 3            ← Quema subtítulos .ass
[16] ensamblador_final.py --opcion 4            ← Despliegue + notificación Telegram
╚══════════════════════════════════════════════════════════╝
```

---

## 🚨 ERRORES PROHIBIDOS (LECCIONES DEL V1 + V2)

| NUNCA hagas esto | HAZ esto en su lugar |
| :--- | :--- |
| Descargar assets directo a /Assets_Reusables/ | Usar recolector_visual.py → /Descargas_Crudas/ → auditor |
| Improvisar un ffmpeg directo | Llamar al script con --opcion N |
| Rellenar huecos con videos aleatorios | Se encarga nodriza_visual.py por defecto si Gemini se queda sin cuota |
| Cambiar duraciones en Célula 3 | El timing lo decide SOLO cronometrador_y_tts.py --opcion 4 |
| Usar queries genéricas sin keywords del ADN | recolector_visual.py --opcion 1 lee el ADN automáticamente |
| Usar un registry global compartido entre semanas | Cada semana tiene su propio registry_{evento_id}.json |
| Hardcodear la API Key de Gemini en el código | Siempre leer de .env con os.getenv("GEMINI_API_KEY") |
| Mover o renombrar la Bóveda | La ruta de la Bóveda es SAGRADA e INAMOVIBLE |
| Meter >7 clips en video <=60s | El validador_de_ensamble.py --opcion 2 lo bloqueará |
