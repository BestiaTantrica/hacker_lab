# 📦 INVENTARIO TÉCNICO DEL LABORATORIO

> Última auditoría: 2026-06-29 | Auditado por: Antigravity AI
> El Nodo Oracle no pudo auditarse de forma directa (sin acceso SSH desde el sandbox). La sección correspondiente se basa en documentación previa y el `informe_despliegue_oci.txt`.

---

## 🖥️ NODO LOCAL — PC de Desarrollo

### Directorio Raíz del Workspace
`/home/tomas2/WORKSPACE/tomas2/WORKSPACE/`

| Ítem | Tipo | Estado | Descripción | Problema Detectado |
|---|---|---|---|---|
| `LAB/` | Directorio | ✅ Activo | Documentación maestra del laboratorio | — |
| `portafolio-ciberseguridad/` | Repositorio Git | ✅ Activo | Portfolio académico con network-toolkit anidado | Archivos sin seguimiento (no committeados) |
| `caso fuerza bruta btc/` | Directorio (sin Git) | ⚠️ Incompleto | Caso de análisis forense Bitcoin wallet.dat 2013 | No está bajo control de versiones; `hash_real.txt` vacío |
| `informe_despliegue_oci.txt` | Archivo | ✅ Referencia | Ficha técnica del despliegue OCI (2026-06-27) | — |
| `api agente hackerone monitor` | Archivo (sin extensión) | ⚠️ Riesgo | Script-comandos para configurar OCI. Contiene una API key de Groq en texto plano | **SEGURIDAD: Credencial expuesta en workspace (GROQ_API_KEY en línea 2)** |
| `códigos de respaldo h1` | Archivo (sin extensión) | ⚠️ Riesgo | Códigos de recuperación 2FA de HackerOne en texto plano | **SEGURIDAD: Datos sensibles en workspace sin cifrar** |
| `How to read a Wireshark TCP_HTTP log.md` | Archivo | ✅ Referencia | Guía de lectura de logs de red | Ubicado en la raíz, debería estar en el portafolio |
| `Cybersecurity incident report.docx` | Archivo | ⚠️ Pendiente clasificar | Reporte de incidente de ciberseguridad | Fuera de la estructura del portafolio |
| `Security incident report template.docx` | Archivo | ⚠️ Pendiente clasificar | Plantilla de reporte de incidente | Fuera de la estructura del portafolio |

---

### Proyecto: `portafolio-ciberseguridad`
**Ruta:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/portafolio-ciberseguridad/`
**Git:** Inicializado. Rama `main`. 4 commits. Sincronizado con `origin/main`.

| Directorio/Archivo | Estado | Descripción |
|---|---|---|
| `01_Identidad_Profesional/career_identity.md` | ✅ Completo | Career Identity Statement orientado a Bug Bounty y SecOps |
| `02_Marcos_de_Referencia/NIST_CSF.md` | ✅ Completo | Resumen del NIST Cybersecurity Framework |
| `02_Marcos_de_Referencia/RMF.md` | ✅ Completo | Resumen del NIST Risk Management Framework |
| `02_Marcos_de_Referencia/auditoria ficticia/` | ✅ Completo | Auditoría completa de "Botium Toys" con documentación y checklists |
| `02_Marcos_de_Referencia/known_exploited_vulnerabilities.csv` | ⚠️ Sin commit | CSV de vulnerabilidades explotadas (CISA KEV). Archivo grande; no committeado |
| `03_Manuales_Forense/preservacion_evidencias.md` | ✅ Completo | Guía de preservación y orden de volatilidad |
| `03_Manuales_Forense/plantilla_custodia.md` | ✅ Completo | Plantilla de cadena de custodia |
| `04_Laboratorio_IA/README.md` | ✅ Completo | Documentación de uso de IA para SecOps |
| `05_fichas_de_proceso/` | ⚠️ Sin commit | Evidencias forenses (pcap, wtmp, logs, reportes). No committeadas |
| `network-toolkit/` | ✅ Activo (ver detalle abajo) | Subproyecto principal de herramienta de red |
| Archivos `.docx` sueltos en raíz | ⚠️ Pendiente | Archivos Coursera sin clasificar. Generan ruido en el repo |

**Commits registrados:**
1. `0a4b5ac` — Inicializar estructura de portfolio y cimientos de aprendizaje
2. `1e86855` — Refinar Career Identity Statement para Bug Bounty
3. `258ac6e` — Inicializar arquitectura core del network-toolkit
4. `224bf17 (HEAD)` — Agregar self-test, validación y módulo Health Check

---

### Subproyecto: `network-toolkit`
**Ruta:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/portafolio-ciberseguridad/network-toolkit/`
**Versión:** `1.0.0` | **Licencia:** Incluida | **Estado general:** ✅ Funcional (13/14 tests OK)

| Componente | Archivo | Estado | Responsabilidad |
|---|---|---|---|
| **Entry Point** | `bin/net-toolkit` | ✅ Funcional | Orquestador principal, inicializa entorno, lanza UI |
| **Configuración** | `conf/toolkit.conf` | ✅ Funcional | Variables globales de rutas y nivel de log |
| **Logger** | `core/logger.sh` | ✅ Funcional | Escritura a archivo de log y stderr para errores |
| **Manejador de errores** | `core/error_handler.sh` | ✅ Funcional | Intercepta señales y errores fatales, limpia `/tmp` |
| **Validador** | `core/validator.sh` | ✅ Funcional | Pre-validación de entorno (directorios + `curl`/`jq`) |
| **Cargador de módulos** | `core/module_loader.sh` | ✅ Funcional | Auto-descubrimiento de plugins en `modules/*.sh` |
| **Interfaz de usuario** | `core/ui.sh` | ✅ Funcional | Menú interactivo con banner ASCII |
| **Reporter** | `core/reporter.sh` | ✅ Funcional | Exporta reportes sanitizados en `.txt` y `.json` |
| **Self-Test** | `core/self_test.sh` | ✅ Funcional | Suite de 14 pruebas de autodiagnóstico |
| **Plantilla módulo** | `modules/00_template.sh` | ✅ Funcional | Interfaz estándar para nuevos módulos |
| **Health Check** | `modules/01_health_check.sh` | ✅ Funcional | Diagnóstico integral L2→L7 con reporte JSON/TXT |
| `install.sh` | — | ✅ Funcional | Instalador de dependencias del sistema |
| `logs/` | — | ✅ Con datos | Contiene logs del toolkit y de sesiones anteriores |
| `reports/` | — | ✅ Con datos | Contiene reporte generado el 2026-06-27 |
| `tests/` | — | ⚠️ Vacío | Directorio de tests pero sin archivos de prueba unitaria |
| `docs/` | — | ⚠️ Vacío | Directorio de documentación técnica vacío |
| `lib/` | — | ⚠️ Vacío | Directorio de librerías compartidas vacío |
| `assets/` | — | ⚠️ Vacío | Directorio de assets vacío |
| `tmp/` | — | ✅ Presente | Directorio de archivos temporales (se limpia automáticamente) |

**Test FAIL detectado (self-test):**
- `[ FAIL ] Validación de dependencias externas (APT)` — El self-test busca el comando `dnsutils` como ejecutable, pero ese es el *nombre del paquete APT*, no el binario. Los binarios reales (`dig`, `nslookup`) sí están presentes. Es un **bug de nomenclatura en `self_test.sh` línea 133**: debe reemplazarse `"dnsutils"` por `"dig"`.

**Dependencias del sistema requeridas:**
| Herramienta | Presente | Instalada via |
|---|---|---|
| `curl` | ✅ `/usr/bin/curl` | APT |
| `jq` | ✅ `/usr/bin/jq` | APT |
| `nmap` | ✅ `/usr/bin/nmap` | APT |
| `dig` | ✅ `/usr/bin/dig` | APT (dnsutils) |
| `nslookup` | ✅ `/usr/bin/nslookup` | APT (dnsutils) |
| `ip` | Asumido ✅ | iproute2 |
| `ping` | Asumido ✅ | iputils-ping |

---

### Proyecto: `caso fuerza bruta btc`
**Ruta:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/caso fuerza bruta btc/`
**Git:** ❌ No inicializado | **Estado:** ⚠️ Incompleto

| Archivo | Estado | Descripción |
|---|---|---|
| `generator.py` | ✅ Completo | Generador de micro-diccionario bayesiano (10 tiers de probabilidad) para hashcat |
| `generador_local.py` | ✅ Completo | Versión simplificada del generador (prototipo inicial) |
| `bitcoin2john.py` | ✅ Presente | Script estándar para extraer hash de `wallet.dat` en formato John/Hashcat |
| `micro_diccionario.txt` | ✅ Generado | Diccionario de ~100 KB generado por `generator.py` |
| `hash.txt` | ✅ Presente | Hash Bitcoin Core (modo 11300) listo para usar con hashcat |
| `hash_real.txt` | ❌ Vacío | Se esperaba el hash real del reto; actualmente vacío |
| `lote_01.txt` | ✅ Presente | Diccionario básico generado por `generador_local.py` (primera iteración) |
| `wallet.dat` | ✅ Presente | Cartera Bitcoin Core 2013 del reto público (@marcebit) |

**Objetivo:** Recuperar la contraseña del `wallet.dat` 2013 usando las variantes lingüísticas del español rioplatense (ej. "billetera"/"wallet") con hashcat en modo 11300.

---

## ☁️ NODO ORACLE CLOUD (OCI)

> ✅ **Datos verificados:** El usuario ejecutó diagnósticos en el servidor y compartió la salida real. Los datos a continuación reflejan el estado real del sistema al 2026-06-29 23:04 ART.

| Elemento | Detalle | Estado |
|---|---|---|
| **Instancia** | Lab-Cybersec-Micro | ✅ AVAILABLE |
| **Shape** | VM.Standard.E2.1.Micro (1 OCPU, 1 GB RAM) | ✅ Always Free |
| **SO** | Ubuntu 24.04.4 LTS | ✅ Activo |
| **IP Pública** | `129.80.73.248` | ✅ Asignada |
| **Python venv** | Python 3.12.3 en `~/workspace_lab/venv/` | ✅ Operativo |
| **Librerías venv** | `requests`, `groq` (instaladas por `setup_micro.sh`) | ✅ Instaladas |
| **SWAP** | 2 GB configurado (via `setup_micro.sh`) | ✅ Configurado |
| **Cronjobs** | Sin crontab definido | ❌ No configurado |
| **`config/entorno.env`** | Credenciales (GROQ_API_KEY, etc.) | ✅ Presente (permisos 600) |
| **`config/objetivos.txt`** | Lista de dominios objetivo | ✅ Presente (14 bytes — 1 dominio aprox.) |
| **`monitores/discovery_pasivo.py`** | Script de discovery pasivo | ✅ Existe y funcionó (1648 bytes) |
| **`resultados/discovery_crudo.json`** | Output del último discovery | ✅ Generado (92 bytes) |
| **`CONTRATO_SUPERVISOR.md`** | Reglas operativas del nodo | ✅ Presente y detallado |
| **`HOJA_DE_RUTA.md`** | Copia de la hoja de ruta local | ✅ Sincronizado |
| **`agentes/`** | Directorio para agentes futuros | ⚠️ Vacío |
| **`api/`** | Directorio para wrappers de API | ⚠️ Vacío |
| **`estado/`** | Estado persistente entre ejecuciones | ⚠️ Vacío (falta `previo.json`) |
| **`inventario/`** | Inventario de activos descubiertos | ⚠️ Vacío |
| **`logs/`** | Logs de ejecución | ⚠️ Vacío |
| **`playbooks/`** | Playbooks del supervisor | ⚠️ Vacío |

**Estructura real verificada en OCI:**
```
~/plataforma_operativa/            (última mod: 2026-06-29 23:28)
├── CONTRATO_SUPERVISOR.md         ✅ Reglas operativas del nodo (3355 bytes)
├── HOJA_DE_RUTA.md                ✅ Copia de hoja de ruta local (3528 bytes)
├── agentes/                       ⚠️ VACÍO — Reservado para futuros agentes
├── api/                           ⚠️ VACÍO — Reservado para wrappers de API
├── config/
│   ├── entorno.env                ✅ Credenciales (600 - solo ubuntu)
│   └── objetivos.txt              ✅ Lista de dominios objetivo (~1 dominio)
├── estado/                        ⚠️ VACÍO — Falta previo.json para el comparador
├── inventario/                    ⚠️ VACÍO
├── logs/                          ⚠️ VACÍO — Sin logs de ejecución aún
├── monitores/
│   └── discovery_pasivo.py        ✅ Script operativo (1648 bytes, ejecutado)
├── playbooks/                     ⚠️ VACÍO
└── resultados/
    └── discovery_crudo.json       ✅ Output real del último discovery (92 bytes)

~/workspace_lab/                   (última mod: 2026-06-27 23:37)
├── config/                        ⚠️ VACÍO
├── datos_crudos/                  ⚠️ VACÍO
├── herramientas/                  ⚠️ VACÍO
├── logs/                          ⚠️ VACÍO
├── scripts/                       ⚠️ VACÍO
└── venv/                          ✅ Python 3.12.3 + requests + groq

~/setup_micro.sh                   ✅ Script de bootstrap (swap + venv)
```

**Hallazgo crítico — Estado real vs. documentado:**

La Etapa 1 del Roadmap (Discovery Pasivo) está **parcialmente completa**. El script `discovery_pasivo.py` existe y produjo un resultado (`discovery_crudo.json`). Sin embargo:
- No hay cron configurado (sin automatización)
- `estado/` está vacío (falta el archivo `previo.json` para que el comparador pueda funcionar)
- Los logs están vacíos (no hay registro de ejecuciones previas)
- El contenido exacto del script y del JSON resultante está **pendiente de verificación**

---

### Módulo: `LAB/api/`
**Ruta:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/`
**Estado:** ✅ Nuevo — Implementado 2026-07-02 (Definido para Groq y Gemini)

| Archivo | Estado | Descripción |
|---|---|---|
| `llm_client.py` | ✅ Funcional | Cliente LLM puro (sin dependencias) con fallback en cascada: Groq → Gemini Flash |
| `.env.example` | ✅ Presente | Plantilla de variables de entorno con Groq y Gemini |
| `test_tres_tareas.py` | ✅ Funcional | Script de prueba para Groq y Gemini de forma directa |

**Proveedores implementados:**
| Proveedor | Estado | Variable de entorno | Modelo por defecto |
|---|---|---|---|
| Groq | ✅ Operacional | `GROQ_API_KEY` | `llama-3.1-8b-instant` |
| Gemini Flash | ✅ Operacional | `GEMINI_API_KEY` | `gemini-2.5-flash` |

**Despliegue en OCI:** Copiar `llm_client.py` a `~/plataforma_operativa/api/`. Credenciales en `~/plataforma_operativa/config/entorno.env` (con permisos 600).

---

## 🐛 PROBLEMAS DETECTADOS

| # | Severidad | Componente | Descripción | Acción Recomendada |
|---|---|---|---|---|
| 1 | 🔴 ALTA | `api agente hackerone monitor` | GROQ_API_KEY expuesta en texto plano en el workspace | Verificar si fue commiteada a Git; si sí → rotar inmediatamente |
| 2 | 🔴 ALTA | `códigos de respaldo h1` | Códigos 2FA de HackerOne en texto plano en el workspace | Cifrar con GPG o mover a un gestor de contraseñas |
| 3 | 🔴 ALTA | OCI `discovery_pasivo.py` | **crt.sh es accesible desde OCI** (TLS handshake OK, IP 91.199.212.73 resuelta). Pero devuelve body vacío para `starbucks.com`. Causa probable: **timeout del lado del servidor de crt.sh** para dominios con miles de entradas. La query `%.starbucks.com` es muy costosa para su DB. El script no distingue body vacío de error real. | Probar con un dominio de alcance menor. Agregar validación: si `response.text` está vacío, registrar como error en log y no guardar JSON vacío. Confirmar con `curl -w "%{http_code} %{size_download}bytes %{time_total}s"` |
| 4 | 🟡 MEDIA | OCI `discovery_pasivo.py` | No hay logging a `~/plataforma_operativa/logs/`. Los errores y resultados solo van a stdout, que se pierde si se ejecuta vía cron | Agregar `logging` a archivo en el script antes de configurar el cron |
| 5 | 🟡 MEDIA | OCI `resultados/` | Nombre del archivo de salida (`discovery_crudo.json`) no coincide con lo que define el CONTRATO_SUPERVISOR.md (`actual.json`). Incoherencia que romperá el comparador futuro | Estandarizar el nombre a `actual.json` o actualizar el CONTRATO |
| 6 | 🟡 MEDIA | OCI `estado/` | Directorio vacío: no existe `previo.json`. Sin él, el comparador de la Etapa 2 no puede funcionar | Al finalizar un discovery exitoso, copiar `actual.json` → `estado/previo.json` |
| 7 | 🟡 MEDIA | OCI RAM | RAM en idle: 416 MB usados / 954 MB total. Margen libre reducido (99 MB libre, 537 MB disponible con caché) | Monitorear consumo durante ejecución del discovery. El SWAP de 2 GB activo es el colchón de seguridad |
| 8 | 🟡 MEDIA | `network-toolkit/core/self_test.sh` | Bug en test #12: verifica el paquete `dnsutils` como ejecutable en vez del binario `dig` | Corregir línea 133: reemplazar `"dnsutils"` por `"dig"` |
| 9 | 🟡 MEDIA | `caso fuerza bruta btc/` | Directorio sin control de versiones Git | Decidir si se agrega al portafolio o se mantiene como espacio de trabajo privado |
| 10 | 🟡 MEDIA | OCI `config/objetivos.txt` | Solo contiene `starbucks.com` (14 bytes = 1 dominio). Scope muy reducido para Bug Bounty útil | Ampliar con más dominios de programas HackerOne con wildcard scope |
| 11 | 🟢 BAJA | `portafolio-ciberseguridad/` | Múltiples archivos `.docx` y `.pdf` de Coursera sueltos en la raíz del repo | Mover a `_coursera_materials/` o excluir con `.gitignore` |
| 12 | 🟢 BAJA | `portafolio-ciberseguridad/` | 10 archivos sin seguimiento (untracked) en git status | Hacer commit o añadir a `.gitignore` |
| 13 | 🟢 BAJA | `network-toolkit/tests/`, `docs/`, `lib/`, `assets/` | Directorios vacíos creados pero sin contenido | Agregar `.gitkeep` o documentar como planificados |
| 14 | 🟢 BAJA | OCI `workspace_lab/` | 5 de 6 subdirectorios vacíos (`config`, `datos_crudos`, `herramientas`, `logs`, `scripts`) | Definir qué va en cada uno o eliminar los que no se usarán |

---

## 📋 ANÁLISIS TÉCNICO DEL SCRIPT `discovery_pasivo.py`

**Código fuente auditado:** `~/plataforma_operativa/monitores/discovery_pasivo.py` (1648 bytes, Python 3.12.3)

### Qué hace bien:
- ✅ Lee dominios objetivo desde un archivo externo (no hardcodeado)
- ✅ Consulta `crt.sh` con timeout rígido de 15 segundos
- ✅ Elimina comodines (`*.`) de los resultados
- ✅ Deduplica subdominios con `set()`
- ✅ Genera JSON estructurado con timestamp UTC

### Gaps identificados:

```
GAP 1: Fallo silencioso
  Cuando requests lanza una excepción, el bloque except la imprime
  por stdout y retorna []. El JSON final queda con arrays vacíos
  sin distinguir "no hay subdominios" de "fallo de red".
  → El comparador de Etapa 2 interpretará [] como resultado válido.

GAP 2: Sin logging persistente
  Todo va a stdout. Si se ejecuta vía cron, el output se pierde
  a menos que se redirija explícitamente (>> logs/discovery.log).

GAP 3: Nombre de archivo fijo
  OUTPUT_FILE = "discovery_crudo.json" (siempre el mismo nombre).
  Cada ejecución sobreescribe la anterior sin historial.
  El CONTRATO_SUPERVISOR habla de "actual.json".

GAP 4: Sin validación del resultado
  No verifica si la lista de subdominios está vacía antes de guardar.
  Un JSON con [] es indistinguible de un error de conectividad.
```

### Resultado del último run (2026-06-29T23:37:55 UTC):
```json
{
  "timestamp": "2026-06-29T23:37:55.476299",
  "dominios": {
    "starbucks.com": []
  }
}
```
**Diagnóstico:** Array vacío para `starbucks.com` es anómalo. Este dominio tiene más de 1000 entradas en crt.sh. Alta probabilidad de fallo de conectividad OCI → crt.sh en el momento de ejecución, capturado silenciosamente por el `except`.
