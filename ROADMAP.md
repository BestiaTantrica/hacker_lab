# 🗺️ ROADMAP DEL LABORATORIO

> Este roadmap está basado **exclusivamente en el estado real del sistema** auditado el 2026-06-29.
> No contiene arquitecturas inventadas. Cada etapa produce un resultado funcional verificable.
> Una etapa no comienza hasta que la anterior esté completa y validada.

---

## ✅ ESTADO ACTUAL (Verificado 2026-06-29)

| Nodo | Componente | Estado |
|---|---|---|
| Local | `network-toolkit` v1.0.0 | ✅ Funcional. 13/14 tests OK. Bug menor en self-test. |
| Local | `portafolio-ciberseguridad` | ✅ Estructura completa, docs académicas. |
| Local | `caso fuerza bruta btc` | ⚠️ Herramientas listas, sin Git, sin resultado. |
| OCI | Red e instancia | ✅ Instancia operativa, Python 3.12.3, venv activo. |
| OCI | `discovery_pasivo.py` | ✅ Script existe y ejecutó. Resultado en `discovery_crudo.json`. |
| OCI | Comparador / `estado/previo.json` | ❌ No existe. Bloqueante para Etapa 2. |
| OCI | Logs operativos | ❌ `logs/` vacío. Sin registro de ejecuciones. |
| OCI | Cronjobs | ❌ Sin cron. Sin automatización. |

---

## 🔧 ETAPA 0 — Saneamiento del Laboratorio
**Duración estimada:** 1-2 días | **Objetivo:** Resolver los problemas detectados antes de construir sobre una base rota.

### Tareas:
- [ ] **[SEGURIDAD]** Las claves API de Groq y HackerOne están expuestas en texto plano en el workspace. Diseñar un mecanismo seguro de importación para que los scripts no dependan de credenciales hardcodeadas en archivos del repositorio.
- [ ] **[SEGURIDAD]** Mover los códigos 2FA de HackerOne (`códigos de respaldo h1`) a un gestor de contraseñas.
- [ ] **[BUG]** Corregir `network-toolkit/core/self_test.sh` línea 133: cambiar `"dnsutils"` por `"dig"` → resolverá el único test FAIL.
- [ ] **[ORDEN]** Hacer commit o `.gitignore` de los 10 archivos untracked del portafolio.
- [ ] **[VERIFICACIÓN OCI]** Leer contenido de `discovery_pasivo.py` y `discovery_crudo.json` para confirmar que el script funciona correctamente antes de avanzar.

**Criterio de éxito:** `./bin/net-toolkit --self-test` reporta **14/14 OK**. No hay credenciales viejas expuestas.

---

## 🌐 ETAPA 1 — Discovery Pasivo en OCI
**Estado: ⚠️ PARCIALMENTE COMPLETA** | **Prioridad:** Alta

### Qué existe:
- ✅ `~/plataforma_operativa/monitores/discovery_pasivo.py` (1648 bytes) — ejecutado al menos una vez.
- ✅ `~/plataforma_operativa/resultados/discovery_crudo.json` (92 bytes) — output real generado.
- ✅ `config/objetivos.txt` — lista de dominios configurada.
- ✅ `config/entorno.env` — credenciales con permisos correctos (600).

### ⚠️ PROBLEMA DETECTADO (pendiente confirmación):
`crt.sh` es accesible desde OCI (TLS OK), pero devolvió body vacío para `starbucks.com`. Hipótesis más probable: **timeout de query en el servidor de crt.sh** — dominios grandes con miles de entradas exceden su límite de tiempo de DB. **No es un bloqueo de IP.**

Acción antes de continuar: correr `curl -s -o /dev/null -w "%{http_code} | %{size_download}bytes | %{time_total}s\n" "https://crt.sh/?q=%.starbucks.com&output=json"` para confirmar el código HTTP y el tiempo de respuesta.

Si el tiempo supera ~10-15s y devuelve 0 bytes → confirma timeout de crt.sh. Solución: usar dominios más pequeños en `objetivos.txt`, o agregar reintentos con backoff al script.

### Qué falta para completar la etapa:
- [ ] Revisar el contenido de `discovery_pasivo.py` y validar que cumple los requisitos del CONTRATO_SUPERVISOR.md.
- [ ] Revisar `discovery_crudo.json`: ¿tiene formato correcto? ¿datos reales de subdominios?
- [ ] Agregar logging de ejecución a `~/plataforma_operativa/logs/`.
- [ ] Estandarizar el nombre del archivo de salida (actualmente `discovery_crudo.json`; el CONTRATO dice `actual.json`).

**Criterio de éxito:** Ejecución manual produce un JSON válido con subdominios reales + una línea de log en `logs/`.

---

## ⚖️ ETAPA 2 — Comparador de Deltas
**Duración estimada:** 1 semana | **Prioridad:** Alta

### Objetivo:
Crear un script que compare el JSON del discovery actual contra el histórico y calcule el Delta (activos nuevos o desaparecidos).

### Tareas:
- [ ] Crear `~/plataforma_operativa/monitores/comparador.py`.
- [ ] El comparador lee `resultados/ultimo.json` vs `resultados/anterior.json`.
- [ ] Si hay Delta, escribir `resultados/delta_YYYY-MM-DD.json`.
- [ ] Si no hay Delta, salir silenciosamente (sin log innecesario).

**Criterio de éxito:** Modificar manualmente un JSON y ejecutar el comparador → se genera un `delta_*.json` con los cambios.

---

## 📚 ETAPA 3 — Histórico y Registro de Ejecuciones
**Duración estimada:** 1 semana | **Prioridad:** Media

### Objetivo:
Implementar un sistema de registro que guarde fecha, resultado y estado de cada ejecución del discovery y el comparador.

### Tareas:
- [ ] Crear un log de ejecución estructurado en `~/plataforma_operativa/logs/ejecuciones.log`.
- [ ] Registrar: fecha, dominios consultados, subdominios encontrados, si hubo delta.
- [ ] Rotación de logs: si el log supera un tamaño definido (ej. 1 MB), comprimirlo.

**Criterio de éxito:** Tras 3 ejecuciones automáticas, el log contiene entradas legibles con timestamps.

---

## ⏰ ETAPA 4 — Automatización con Cron
**Duración estimada:** 2-3 días | **Prioridad:** Media

### Objetivo:
Configurar un cronjob en el Nodo OCI para ejecutar el pipeline (discovery → comparador → log) automáticamente cada 24 horas.

### Tareas:
- [ ] Crear un script orquestador `~/plataforma_operativa/run_pipeline.sh`.
- [ ] Configurar cron: `0 6 * * * /bin/bash ~/plataforma_operativa/run_pipeline.sh`.
- [ ] Verificar que el cron funciona con una ejecución de prueba.

**Criterio de éxito:** Al día siguiente de configurar el cron, existe un nuevo JSON de resultados con timestamp del día.

---

## 🤖 ETAPA 5 — Reorientación de IA a Asesor Paralelo 24/7
**Duración estimada:** 3 días | **Prioridad:** Media-Alta

### Objetivo:
Transformar la integración de IA en el servidor OCI para que funcione como un tutor/asesor interactivo 24/7 con contexto persistente del laboratorio. En lugar de gastar tokens analizando deltas automáticamente de forma ciega, la IA responderá a tus preguntas técnicas y te guiará para que aprendas en el proceso.

### Tareas:
- [ ] Crear un script interactivo `consultar_asesor.py` en el servidor OCI.
- [ ] Implementar un sistema de contexto local (que lea `actual.json` y `delta_*.json` bajo demanda) para que la IA sepa de qué activos le estás hablando.
- [ ] Configurar un alias en la terminal de OCI (ej: `asesor "cómo verifico este puerto?"`) para tener respuesta inmediata.
- [ ] Usar este asesor como mentor educativo de redes y comandos en tiempo real.

**Criterio de éxito:** Puedes ejecutar un comando en OCI para hablar con la IA y esta reconoce qué subdominios están activos en tu base de datos actual.


---

## 🔧 ETAPA 6 — Módulo 02 del network-toolkit (Futuro)
**Duración estimada:** 1 semana | **Prioridad:** Baja

### Objetivo:
Agregar un segundo módulo al `network-toolkit` local. Candidatos:
- `02_port_scan.sh` — Escaneo de puertos con `nmap` en modo silencioso.
- `02_dns_recon.sh` — Reconocimiento DNS pasivo de un dominio.

**Criterio de éxito:** El módulo aparece en el menú del toolkit y genera un reporte JSON/TXT.

---

> 📌 **Regla de oro del roadmap:** Si una etapa no tiene su criterio de éxito cumplido, la siguiente etapa no comienza.
