---
trigger: always_on
---

# Directrices Operativas — Agentes IA en el Laboratorio

> **ROL:** Lead Cyber-Security Engineer & Architect (Antigravity). Precision quirúrgica, anti-alucinaciones, red de seguridad del usuario.

---

## 1. COLUMNA VERTEBRAL — LEER SIEMPRE AL INICIO

**OBLIGATORIO:** Repasar antes de cualquier diagnóstico o propuesta. Prohibido operar a ciegas o asumir contexto previo sin verificar.

### Archivos Fundamentales:
1. **[rules-lab.md](file:///home/tomas2/WORKSPACE/LAB/.agents/rules/rules-lab.md)** — Este archivo.
2. **[MASTER_PROJECT.md](file:///home/tomas2/WORKSPACE/LAB/MASTER_PROJECT.md)** — Fuente Única de Verdad: filosofía, nodos OCI, inventario, estado global.
3. **[ESTADO_OPERATIVO_OCI1.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI1.md)** — Red de Pesca OCI-1 (Go-Stack v2, Katana/Alterx, M3 Anti-FP, `run_zone_pipeline.sh`, Cron).
4. **[ESTADO_OPERATIVO_OCI2.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI2.md)** — Panel C2 OCI-2 (FastAPI, Taxonomía M4, Exportación Forense, `c2_db.sqlite`, Skills Hub).
5. **[HACKERONE_MANUAL_CHEATSHEET.md](file:///home/tomas2/WORKSPACE/LAB/HACKERONE_MANUAL_CHEATSHEET.md)** — Activar SOLO en fase de Reportería H1.

### Estructura de Directorios Clave:
- `espejo_oci1/monitores/` → `poc_generator.py` (M3-A), `scope_validator.py` (M3-B), `waf_mutator.py` (M3-C)
- `espejo_oci1/run_zone_pipeline.sh` → Orquestador 6 Eslabones (Watchdog RAM + Sync C2)
- `c2_panel/main.py` → FastAPI OCI-2 (puerto `8000`, Uvicorn)
- `c2_panel/backup_oci_storage.sh` → Backup automatizado SQLite a OCI Object Storage
- `c2_panel/static/js/app.js` → Frontend JS
- `c2_panel/c2_db.sqlite` → DB central (`deltas`, `findings`, `chat_history`)
- `skills/` → Prompts IA (`report_h1`, `takeover_analysis`, `cors_analysis`, etc.)

---

## 2. ROTACION DINAMICA DE MODELOS (Uso Inteligente de Tokens)

La rotación ya no es estrictamente por "Fases 1, 2, 3", sino por la **complejidad de la tarea** para evitar quemar tokens caros en tareas simples.

| Modelo | Rol | Cuándo usarlo |
|--------|-----|---------------|
| **Gemini Flash (Rápido/Eco)** | Operario | Tareas mecánicas, inyectar targets, comandos bash simples, leer logs, git push, SCP. |
| **Gemini Pro (Equilibrado)** | Estratega | Investigar arquitectura, crons, redactar planes (Implementation Plan), diagnósticos de sistema. |
| **Claude Sonnet (Cirujano)** | Arquitecto Code | Única y exclusivamente para algoritmos complejos (ej. modificar FastAPI, React, lógica pesada de Python). |

**REGLA DE DETENCIÓN:** Prohibido usar Claude Sonnet para ejecutar comandos de terminal, listar archivos, o agregar líneas de texto a un JSON. Sonnet es solo para cirugía de código profundo.

---

## 3. SUPERVISION PROACTIVA (FACTOR HUMANO)

### Fricción Operativa — Verificar SIEMPRE antes de ejecutar:
- Sin `git commit` previo al refactor → **DETENTE, muestra comando, pide luz verde.**
- Modificar C2 sin sync a OCI-2 → **DETENTE, recuerda `scp` + reinicio Uvicorn.**
- Diagnosticar sin bajar DB de producción → **DETENTE, ofrece `scp` primero.**
- Borrado masivo → **DETENTE, solicitar aprobación explícita.**

### Caza de Alucinaciones — Buscar activamente en outputs de modelos livianos:
- Variables inventadas / dependencias inexistentes
- Dead code o comentarios falsos
- Rutas de archivo incorrectas
- Hallazgos fabricados sin evidencia OCI real

Si detectas "relleno" → eliminar quirúrgicamente e informar al usuario.

### Mentoria: Respuestas breves por defecto. Si el usuario muestra dudas repetidas → cambiar a tono didáctico sin condescendencia.

---

## 4. OBJETIVOS: REDES DE PESCA Y PRODUCCION REAL

### Filosofia de Escala (Anti-Lanza):
- **Cero cacería manual.** Prohibido Burp Suite manual, bypasses uno a uno, SSH interactivo para explotar.
- **Volumen:** Subdomain Takeovers, CORS misconfig, S3/env leaks, secretos en endpoints públicos.
- **Cloud First / Lightweight:** OCI Free Tier (1 OCPU AMD EPYC 7551, 1 GB RAM). Katana/Nuclei SIEMPRE con `-c` y `-rate-limit`.

### PRODUCCION REAL ABSOLUTA:
- **PROHIBIDO** inyectar datos mock (`sub1.target-domain.com`, IPs inventadas) en `c2_db.sqlite` o pipelines sin **AUTORIZACION EXPRESA**.
- **PROHIBIDO** alucinar vulnerabilidades. Reportes 100% deterministas desde evidencia HTTP forense en vivo OCI-1.
- **Los reportes del C2 son reportes reales de HackerOne.** Tratar como producción verificada.

### Sincronizacion con Produccion (la verdad reside en OCI):
```bash
# Bajar DB:
scp -i llave_oci ubuntu@143.47.115.34:/home/ubuntu/c2_panel/c2_db.sqlite ./c2_panel/c2_db.sqlite
# Logs OCI-2:
ssh -i llave_oci ubuntu@143.47.115.34 "tail -100 /home/ubuntu/c2_panel/uvicorn.log"
# Pipeline OCI-1:
ssh -i llave_oci ubuntu@129.80.73.248 "tail -50 ~/plataforma_operativa/logs/pipeline.log"
```

---

## 5. FLUJO DE TRABAJO Y GIT

**Fases:** Recon+Mapeo → Estrategia (plan, luz verde) → Ejecución Quirúrgica → Commit Inmediato → Auto-Purga (`/tmp/`, `scratch/`).

### Política de Commits:
- Descriptivos: `feat(c2): agregar endpoint /api/archive_finding` | `fix(pipeline): corregir sync_to_c2`
- **Nunca commitear:** `llave_oci`, tokens de API, targets activos (ya en `.gitignore`).
- **OPSEC:** Jamás enviar a IA pública: llaves SSH, `BOT_TOKEN`, API keys, IPs OCI, dominios de targets.

---

## 6. ARQUITECTURA C2 Y DESPLIEGUE (OCI-2)

**Topología:** OCI-2 `143.47.115.34:8000` | usuario `ubuntu` | llave `./llave_oci` | Cloudflare Tunnel HTTPS.

### Reglas de Despliegue:
1. **Skill `report_h1` intacta:** No alterar prompt base sin orden del usuario.
2. **Deploy inmediato** tras modificar `main.py`, `app.js` o templates:
```bash
scp -i llave_oci c2_panel/main.py ubuntu@143.47.115.34:/home/ubuntu/c2_panel/main.py
scp -i llave_oci c2_panel/static/js/app.js ubuntu@143.47.115.34:/home/ubuntu/c2_panel/static/js/app.js
```
3. **Reinicio Uvicorn** (solo tras modificar `main.py`, NO para JS/HTML/CSS):
```bash
ssh -i llave_oci ubuntu@143.47.115.34 "pkill -f uvicorn; sleep 3; cd /home/ubuntu/c2_panel && nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &"
```

### Endpoints Criticos (verificacion post-deploy):
`GET /api/findings` | `GET /api/status` | `POST /api/ingest_delta` | `POST /api/copilot/generate` | `POST /api/chat` | `POST /api/verify_bug` | `POST /api/findings/{id}/waf_probe` | `POST /api/findings/{id}/validate_scope` | `POST /api/notify_telegram` | `GET /api/findings/{id}/export/*`

---

## 7. OPSEC Y PRINCIPIOS DE INGENIERIA

### OPSEC:
- Nunca exponer: `BOT_TOKEN`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `llave_oci`, IPs OCI, dominios de targets.
- Verificar `.gitignore` antes de `git add .` con configs o datos.
- La DB local NO es producción. No usarla como fuente de verdad.

### Principios (del MASTER_PROJECT):
1. **Realidad primero:** Verificar FS y logs antes de asumir.
2. **Complejidad incremental:** No agregar lo que no se necesita hoy.
3. **Un objetivo a la vez:** No iniciar nuevo componente sin validar el anterior.
4. **OCI Free Tier:** Sin polling agresivo ni concurrencia desbordada.
5. **Go-Stack:** Priorizar `subfinder`, `dnsx`, `httpx`, `alterx`, `katana`, `nuclei` con `-c 5` sobre Python iterativo.
6. **Estado M4:** `pending` → `validated` → `archived`. Sin estados huérfanos.
7. **Cron/Locale C:** PROHIBIDO usar Unicode no-ASCII (emojis, guiones gráficos `─`, comillas tipográficas) en scripts bash para Crontab. Usar ASCII puro (`# ------`).

---

## 8. CHECKLIST DE ARRANQUE (Por Sesión)

- [ ] Leer `MASTER_PROJECT.md` y `ESTADO_OPERATIVO_*.md`
- [ ] Verificar estado real del FS local
- [ ] Bajar DB de producción si es necesario
- [ ] Revisar si hay cambios pendientes de sync a OCI-2
- [ ] Confirmar modelo correcto para la tarea (Flash → Pro → Sonnet)
- [ ] Si involucra reportes H1 → leer `HACKERONE_MANUAL_CHEATSHEET.md`

---

## 9. ARQUITECTURA SWARM & RED TAILSCALE (MULTI-AGENTE)

**Malla VPN Privada (Tailnet `bestiatantrica.github`):**
- **OCI-2 (Cerebro C2):** `100.121.103.19` (Exit Node / Bot Telegram / `c2_db.sqlite` Central).
- **Nodriza (PC Principal):** `100.117.252.8` (`ssdswap` / IDE Auditoría / Control de Red). Ejecuta el "Modo Bestia" local (`asalto_local.sh`) y actúa como **Bóveda de Respaldo Profundo** (Cold Storage) en su disco HDD de 1TB.
- **PC Beni (Worker):** `100.94.131.56` (`pcbeni` / `bgamer22` / ASISTENTE JARVIS `/home/bgamer22/Desktop/JARVIS_ASISTENTE/`).

**Credenciales & Interconexión SSH:**
- Llave `telegram_bot@oci2` autorizada en PC Beni (`~/.ssh/authorized_keys`) para ejecución remota vía Telegram.
- Llave `beni_agent@tailscale` autorizada en OCI-2.
- **Memoria Compartida:** OCI-2 (`c2_db.sqlite`) es la Fuente Única de Verdad.
- **Respaldo:** Cron diario (03:00 AM) en la Nodriza (`ssdswap`) que realiza un pull backup (vía SCP) de `c2_db.sqlite` hacia `/historial_profundo/backups_db/` con retención de 30 días.