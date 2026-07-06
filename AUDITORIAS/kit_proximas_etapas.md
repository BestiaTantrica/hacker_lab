# 🗺️ KIT DE DELEGACIÓN — PRÓXIMAS ETAPAS DEL LABORATORIO

> Documento generado el 2026-07-05 al completar las Etapas 1 a 4 del ROADMAP.
> Sirve como punto de entrada para cualquier IA libre (ChatGPT, Claude, Gemini) 
> en las próximas sesiones de trabajo. Leer completo antes de pedir código.

---

## ✅ RESUMEN DE LO QUE ESTÁ HECHO Y FUNCIONANDO

El pipeline de monitoreo pasivo de activos de ciberseguridad está operativo al 100% en el Nodo OCI (Oracle Cloud). No necesita intervención manual.

| Etapa | Componente | Ubicación en OCI | Estado |
|---|---|---|---|
| 1 | `discovery_pasivo.py` | `~/plataforma_operativa/monitores/` | ✅ Funcionando |
| 2 | `comparador.py` | `~/plataforma_operativa/monitores/` | ✅ Funcionando |
| 3 | `run_pipeline.sh` | `~/plataforma_operativa/` | ✅ Funcionando |
| 4 | Cron automático | `crontab -l` (ubuntu@OCI) | ✅ 6AM diario |

### Cómo funciona el ciclo automatizado (sin intervención):
Cada mañana a las 6:00 AM el servidor OCI se activa solo y ejecuta la siguiente secuencia:
1. `discovery_pasivo.py` consulta la API pública `crt.sh` y descarga todos los subdominios de los dominios configurados en `config/objetivos.txt`. Los guarda en `resultados/actual.json`.
2. `comparador.py` compara ese resultado con el estado anterior (`estado/previo.json`). Si hay subdominios nuevos que no existían ayer, los escribe en `resultados/delta_YYYY-MM-DD.json`. Actualiza el estado para el día siguiente.
3. Si no hay cambios, el pipeline termina en silencio. El log queda en `logs/cron_output.log`.

### Infraestructura del servidor OCI:
- **IP pública:** `129.80.73.248`
- **Acceso SSH (desde tu PC):** `ssh -i ~/.ssh/id_rsa ubuntu@129.80.73.248`
- **Directorio del proyecto:** `~/plataforma_operativa`
- **Venv Python:** `source ~/workspace_lab/venv/bin/activate`
- **API Keys:** `~/plataforma_operativa/config/entorno.env` (GROQ_API_KEY y GEMINI_API_KEY)

### APIs de IA disponibles (ya configuradas, listas para usar):
- **Groq (Principal):** API Key en `entorno.env`. Modelo: `llama-3.1-8b-instant`. Gratuito.
- **Gemini (Fallback):** API Key en `entorno.env`. Modelo: `gemini-2.5-flash`. Gratuito.
- **Cliente Python local:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/llm_client.py` — cliente con fallback automático Groq → Gemini, sin dependencias externas.

---

## 🎯 PRÓXIMAS ETAPAS (en orden de prioridad)

> [!IMPORTANT]
> **REGLA: Una sola etapa por sesión.** No empezar la siguiente hasta que la anterior tenga su criterio de éxito verificado.

---

### 📋 ETAPA 5 — Configurar dominios reales de Bug Bounty
**Duración estimada:** 30 minutos | **Prioridad: ALTA — acerca al primer ingreso**

**Contexto:** El sistema actualmente monitorea `starbucks.com` y `github.com` como dominios de prueba. Estos NO son objetivos de Bug Bounty en los que puedas reportar vulnerabilidades y cobrar. Hay que reemplazarlos por programas reales de HackerOne que tengan **wildcard scope** (ej. `*.empresa.com`).

**Por qué wildcard scope:** Los programas con scope `*.empresa.com` te permiten buscar en TODOS los subdominios de esa empresa. Si el discovery encuentra un subdominio nuevo como `staging-api.empresa.com`, ese activo puede ser el camino a una vulnerabilidad.

**Tareas para esta etapa:**
- [ ] Abrir tu cuenta de HackerOne en el navegador: https://hackerone.com/programs
- [ ] Filtrar por: `Asset Type: Domain`, `Eligible for submission: Yes`, ordenar por `bounty`. Seleccionar 3 a 5 programas con scope `*.dominio.com`.
- [ ] Conectarte a OCI: `ssh -i ~/.ssh/id_rsa ubuntu@129.80.73.248`
- [ ] Editar el archivo de objetivos: `nano ~/plataforma_operativa/config/objetivos.txt`
- [ ] Reemplazar `starbucks.com` y `github.com` por los dominios reales de los programas elegidos (uno por línea, sin el `*.` al principio).
- [ ] Guardar (`Ctrl+O`, `Enter`, `Ctrl+X`) y ejecutar una prueba manual: `source ~/workspace_lab/venv/bin/activate && cd ~/plataforma_operativa && python3 monitores/discovery_pasivo.py`

**Criterio de éxito:** `resultados/actual.json` contiene subdominios reales de programas de Bug Bounty activos en HackerOne.

---

### 🤖 ETAPA 6 — Integración de IA en el Pipeline (Análisis de Deltas)
**Duración estimada:** 1 hora | **Prioridad: Media**

**Contexto:** El cliente LLM ya existe y funciona en `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/llm_client.py`. Solo necesita ser copiado al servidor OCI e invocado desde `run_pipeline.sh` cuando exista un archivo `delta_*.json`.

**MASTER PROMPT para generar el script de análisis:**
Pega este texto en ChatGPT, Claude o Gemini Web:

```text
Actúa como un programador senior de Python especialista en ciberseguridad y Bug Bounty.

Necesito que escribas un script llamado `analizar_delta.py` que se ejecuta en un servidor OCI (Ubuntu, Python 3.12).

CONTEXTO:
- Existe un pipeline de monitoreo pasivo que cada día descarga subdominios de empresas en programas de Bug Bounty.
- Cuando se detectan subdominios nuevos, se genera un archivo JSON: ~/plataforma_operativa/resultados/delta_YYYY-MM-DD.json
- Este script debe leer ese delta y analizarlo con una IA para ayudar al investigador de seguridad.

ESTRUCTURA DEL delta_*.json:
{
  "timestamp": "2026-07-05T21:00:00Z",
  "nuevos_activos": {
    "empresa.com": ["nuevo1.empresa.com", "nuevo2.empresa.com"]
  }
}

REQUISITOS:
1. El script recibe como argumento la ruta al archivo delta_*.json a analizar.
2. Para cada subdominio nuevo en el delta, llama a una API de IA con este prompt:
   "Eres un investigador de Bug Bounty. Se encontró un nuevo subdominio: [SUBDOMINIO]. Empresa: [DOMINIO]. Responde en 3 puntos breves: 1) ¿Qué tipo de activo es probablemente? 2) ¿Qué verificar primero? 3) ¿Qué herramienta usar para investigarlo?"
3. La API se llama usando HTTP puro con urllib.request (sin requests ni librerías externas).
4. URL de la API (Groq): https://api.groq.com/openai/v1/chat/completions
5. La API Key se carga desde la variable de entorno GROQ_API_KEY.
6. Guarda el análisis completo en: ~/plataforma_operativa/resultados/analisis_YYYY-MM-DD.txt
7. Si hay más de 10 subdominios nuevos, analiza solo los primeros 10 para no agotar la cuota.
8. Logging detallado a: ~/plataforma_operativa/logs/analisis.log
9. Cero dependencias: solo stdlib de Python (urllib, json, os, sys, logging, datetime).

Escribe el script completo, limpio y documentado.
```

**Tareas para esta etapa:**
- [ ] Obtener el código de `analizar_delta.py` de la IA externa usando el prompt de arriba.
- [ ] Guardar el script en `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/analizar_delta.py`.
- [ ] Subirlo a OCI: `scp -i ~/.ssh/id_rsa /home/tomas2/WORKSPACE/tomas2/WORKSPACE/analizar_delta.py ubuntu@129.80.73.248:~/plataforma_operativa/monitores/`
- [ ] Probarlo manualmente contra el delta existente: `~/workspace_lab/venv/bin/python monitores/analizar_delta.py resultados/delta_2026-07-05.json`
- [ ] Verificar que se generó `resultados/analisis_2026-07-05.txt`.
- [ ] Integrar la llamada en `run_pipeline.sh`: agregar la llamada al script solo si existe un archivo delta.

**Criterio de éxito:** Cuando el pipeline detecta activos nuevos, se genera automáticamente un archivo de análisis con observaciones de la IA sobre cada subdominio.

---

### 📱 ETAPA 7 — Notificaciones por Telegram
**Duración estimada:** 1 hora | **Prioridad: Media**

**Contexto:** Necesitas saber inmediatamente cuando el pipeline detecta un delta (subdominios nuevos) sin tener que conectarte al servidor a revisar los logs. Telegram tiene una API gratuita para enviar mensajes a un chat personal desde un script.

**Pasos preparatorios (hazlos antes de pedir código a la IA):**
1. Abre Telegram y busca el bot oficial `@BotFather`.
2. Escríbele: `/newbot` y sigue sus instrucciones. Elige un nombre como `labsec_monitor_bot`. 
3. BotFather te dará un **TOKEN** del estilo `1234567890:ABCDefGhIJKlmNoPQRstuVwxyz`. Guárdalo.
4. Busca el bot `@userinfobot` en Telegram y escríbele cualquier mensaje. Te responderá con tu **Chat ID** personal (un número, ej. `123456789`).

**MASTER PROMPT para generar el módulo de Telegram:**
Pega este texto en ChatGPT, Claude o Gemini Web:

```text
Actúa como un programador senior de Python.
Necesito un módulo Python llamado `notificador.py` para enviar mensajes a Telegram usando únicamente la biblioteca estándar (urllib, json). Sin dependencias externas.

REQUISITOS:
1. Función principal: send_telegram(message: str) -> bool
   - Lee el TELEGRAM_BOT_TOKEN y el TELEGRAM_CHAT_ID desde variables de entorno.
   - Envía el mensaje usando la API HTTP de Telegram: https://api.telegram.org/bot{TOKEN}/sendMessage
   - Devuelve True si fue exitoso, False si hubo error.
   - En caso de error, lo registra con logging pero no lanza una excepción (el pipeline no debe romperse por una falla de notificación).
2. El mensaje máximo es 4096 caracteres (límite de Telegram); si es más largo, truncarlo.
3. Puede ejecutarse como script directamente para hacer una prueba: python3 notificador.py "Mensaje de prueba"
4. Cero dependencias externas: solo urllib.request, json, os, sys, logging.

Escribe el módulo completo.
```

**Tareas para esta etapa:**
- [ ] Crear el bot en Telegram con @BotFather y obtener el TOKEN y CHAT_ID.
- [ ] Agregar al archivo `~/plataforma_operativa/config/entorno.env` en OCI las variables:
  ```
  TELEGRAM_BOT_TOKEN=tu_token_aqui
  TELEGRAM_CHAT_ID=tu_chat_id_aqui
  ```
- [ ] Obtener el código de `notificador.py` usando el prompt de arriba.
- [ ] Subirlo a OCI: `scp -i ~/.ssh/id_rsa /home/tomas2/WORKSPACE/tomas2/WORKSPACE/notificador.py ubuntu@129.80.73.248:~/plataforma_operativa/monitores/`
- [ ] Probarlo manualmente desde OCI: `~/workspace_lab/venv/bin/python monitores/notificador.py "Prueba del laboratorio"`
- [ ] Integrar en `run_pipeline.sh`: enviar mensaje a Telegram cuando se detecte un delta.

**Criterio de éxito:** Cuando el pipeline detecta activos nuevos, recibes un mensaje en tu Telegram personal con el resumen del delta.

---

## 💰 HOJA DE RUTA HACIA EL PRIMER INGRESO

Una vez que el pipeline esté monitoreando dominios reales de Bug Bounty (Etapa 5) y te notifique por Telegram cuando detecte activos nuevos (Etapa 7), el flujo de trabajo para capitalizar es el siguiente:

```
[Telegram: "2 nuevos subdominios en empresa.com"]
         |
         v
[Leer analisis_*.txt generado por la IA]
         |
         v
[Investigar manualmente el subdominio nuevo]
  - ¿Está en scope del programa de Bug Bounty?
  - ¿Responde a HTTP/HTTPS?
  - ¿Tiene panel de login? ¿API expuesta? ¿Headers de seguridad faltantes?
         |
         v
[Si encontrás una vulnerabilidad real]
  - Documentar con screenshots y pasos de reproducción
  - Reportar en HackerOne al programa correspondiente
  - Esperar la respuesta del equipo de seguridad de la empresa
         |
         v
[Recompensa (bounty) de $50 a $1000+ según criticidad]
```

> [!NOTE]
> **Tipos de vulnerabilidades más comunes en subdominios nuevos:**
> - **Subdomain Takeover:** El subdominio apunta a un servicio que ya no existe (S3, Heroku, GitHub Pages). Se puede "tomar" el control. Alta recompensa.
> - **Panel de administración expuesto:** El subdominio `admin.empresa.com` o `internal.empresa.com` accesible sin autenticación.
> - **Versiones antiguas de software:** El subdominio corre una versión desactualizada de WordPress, Jenkins, etc., con vulnerabilidades conocidas.
> - **Certificados SSL caducados o mal configurados:** No pagan mucho, pero construyen reputación.

---

## 📁 ARCHIVOS QUE DEBEN EXISTIR AL COMPLETAR TODAS LAS ETAPAS

### En el Nodo OCI (`~/plataforma_operativa/`):
```
config/
  entorno.env          ← API Keys (Groq, Gemini, Telegram) - permisos 600
  objetivos.txt        ← Dominios de Bug Bounty reales de HackerOne
monitores/
  discovery_pasivo.py  ← Etapa 1 ✅
  comparador.py        ← Etapa 2 ✅
  analizar_delta.py    ← Etapa 6 (pendiente)
  notificador.py       ← Etapa 7 (pendiente)
resultados/
  actual.json          ← Generado por discovery ✅
  delta_*.json         ← Generado cuando hay novedades ✅
  analisis_*.txt       ← Generado por IA (pendiente)
estado/
  previo.json          ← Estado histórico ✅
logs/
  discovery.log        ← Log del discovery ✅
  comparador.log       ← Log del comparador ✅
  cron_output.log      ← Log del cron ✅
  analisis.log         ← Log del analizador (pendiente)
run_pipeline.sh        ← Etapa 3 ✅
```

### En el Nodo Local (`/home/tomas2/WORKSPACE/tomas2/WORKSPACE/`):
```
portafolio-ciberseguridad/
  plataforma_operativa/
    monitores/
      discovery_pasivo.py   ← En Git ✅ (tras el commit de hoy)
      comparador.py         ← En Git ✅
    run_pipeline.sh         ← En Git ✅
LAB/
  api/
    llm_client.py           ← Cliente LLM con fallback Groq/Gemini ✅
    .env                    ← API Keys locales (NO en Git)
```

---

> 📌 **Regla de oro del roadmap:** Si una etapa no tiene su criterio de éxito cumplido, la siguiente etapa no comienza.
> Siempre verificar el estado real del sistema antes de escribir código nuevo.
