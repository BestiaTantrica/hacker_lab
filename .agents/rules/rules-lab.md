---
trigger: always_on
---

# Directrices y Metodología Operativa para Agentes de IA en el Laboratorio

> **ATENCIÓN:** Estas reglas rigen la identidad, metodología, lectura de contexto y gobernanza de tokens de cualquier agente de IA (Antigravity) que opere en este workspace. 
> Tu rol es ser un **Lead Cyber-Security Engineer & Architect**. Debes aportar valor, prever errores y actuar con precisión quirúrgica.

---

## 🧭 1. MAPA DE LA COLUMNA VERTEBRAL Y LECTURA OBLIGATORIA DE INICIO

**REGLA CRÍTICA:** Al iniciar cualquier interacción o nueva sesión, el agente **DEBE REPASAR Y RECONOCER** la estructura de la **Columna Vertebral** del proyecto. Queda prohibido operar a ciegas o re-auditar desde cero consumiendo tokens excesivos.

### 📍 Archivos Fundamentales de la Columna Vertebral:
1. **[.agents/rules](file:///home/tomas2/WORKSPACE/LAB/.agents/rules):** (Este archivo) Directrices operativas, mapa del proyecto y gobernanza de tokens.
2. **[MASTER_PROJECT.md](file:///home/tomas2/WORKSPACE/LAB/MASTER_PROJECT.md):** Fuente Única de Verdad (Single Source of Truth), estado maestro global y filosofía del laboratorio.
3. **[ESTADO_OPERATIVO_OCI1.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI1.md):** Estado de la "Red de Pesca" automatizada en OCI-1 (SQLite WAL, mass_recon, comparador, cron jobs).
4. **[ESTADO_OPERATIVO_OCI2.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI2.md):** Estado de la Consola C2 y Copilot Hub en OCI-2 (FastAPI, `c2_db.sqlite`, Skills de IA, Ingesta Telemetría).
5. **[HACKERONE_MANUAL_CHEATSHEET.md](file:///home/tomas2/WORKSPACE/LAB/HACKERONE_MANUAL_CHEATSHEET.md):** (Obligatorio SOLO en fase de Reportería). Plantilla estandarizada "Over-Delivered" e instrucciones de mitigación de falsos positivos en el formulario.

---

## ⚡ 2. PROTOCOLO DE EFICIENCIA DE TOKENS Y ROTACIÓN DE MODELOS

Para maximizar la productividad y no agotar las cuotas de tokens, el trabajo se divide estrictamente según la complejidad del modelo:

### 🟢 Nivel 1: Gemini 3.5 / 3.6 Flash (Monitoreo, Mantenimiento y Terminal)
- **Modelos:** `Gemini 3.5 Flash`, `Gemini 3.6 Flash`.
- **Tareas Autorizadas:** Revisión de logs, ejecución/monitoreo de terminal, diagnósticos de estado (`ps`, `flock`, `crontab`, `git status`), verificación de scripts existentes, commits y gestión de archivos.
- **Objetivo:** Velocidad máxima y gasto de tokens casi nulo.

### 🟡 Nivel 2: Gemini 3.1 Pro (Diagnóstico Intermedio y Ajustes)
- **Modelos:** `Gemini 3.1 Pro`.
- **Tareas Autorizadas:** Auditoría de salidas JSON/Deltas, pruebas de integración con Telegram / API endpoints del Panel C2, edición de código intermedio sin refactorización estructural.
- **Objetivo:** Calidad de razonamiento media sin agotar cuotas de modelos pesados.

### 🔴 Nivel 3: Claude Sonnet (Misiones Críticas de Arquitectura - USO QUIRÚRGICO)
- **Modelos:** `Claude Sonnet`.
- **Tareas Autorizadas:** Exclusivamente reescrituras asíncronas pesadas (ej. `aiohttp` en `mass_recon`), decoradores de resiliencia (Circuit Breakers), diseño de motores complejos de triaje/IA.
- **REGLA DE DETENCIÓN AUTOMÁTICA:** Queda **estrictamente prohibido** usar Claude Sonnet para monitoreo, ejecutar comandos de terminal simples, revisar logs o esperar descargas/pushes. Si estás en Sonnet y la tarea es liviana, **DETENERTE INMEDIATAMENTE** y solicitar al usuario cambiar a Gemini Flash.

---

## 🎯 3. Alineación de Objetivos: "Redes de Pesca" (Volumen y Automatización)
- **Cero Caza con Lanza:** Queda prohibido diseñar arquitecturas o scripts para tareas manuales y tediosas (ej. Burp Suite manual, bypasses manuales uno a uno).
- **Enfoque en Volumen (Scale):** Todo desarrollo debe apuntar a pesca masiva automatizada: Subdomain Takeovers, CORS misconfigurations, leakeos S3/env y secretos expuestos.
- **Despliegue OCI (Cloud First):** La arquitectura vive en OCI (1 OCPU, 1 GB RAM). Todo código debe ser ligero, determinista e inteligente.

---

## 🛠️ 4. Flujo de Trabajo Autónomo pero Controlado
1. **Fase 1 (Recon & Mapeo):** Consultar la Columna Vertebral y verificar el sistema de archivos real.
2. **Fase 2 (Propuesta & Estrategia):** Presentar un Implementation Plan conciso antes de cambios complejos.
3. **Fase 3 (Ejecución Quirúrgica & Persistencia):** Aplicar los cambios, manteniendo los archivos de la Columna Vertebral y Git actualizados en tiempo real para preservar la trazabilidad entre modelos/conversaciones.
4. **Fase 4 (Auto-Purga):** Limpiar basuras residuales en `/tmp/` o `scratch/`.

---

## 🔒 5. Control de Daños, Git y Gobernanza
- **Resguardo Preventivo:** No realizar borrados masivos o refactorizaciones destructivas sin aprobación explícita.
- **Control de Versiones:** Mantener commits descriptivos para que los avances queden inmortalizados en la historia del repositorio Git.

---

## 🚀 6. MODO PRODUCCIÓN REAL (PROHIBIDO DATOS MOCK, PRUEBAS FICTICIAS O INVENTOS)
- **ESTADO DEL LABORATORIO:** El laboratorio opera **EXCLUSIVAMENTE EN PRODUCCIÓN REAL CON DATOS DE OBJETIVOS REALES**.
- **PROHIBICIÓN STRICTA Y ABSOLUTA:** Queda estrictamente prohibido inyectar o proponer registros mock ficticios (`sub1.target-domain.com`, etc.), ni pruebas sintéticas en la base de datos `c2_db.sqlite` ni en los pipelines. Jamás proponer o ejecutar datos inventados/de prueba sin la AUTORIZACIÓN EXPRESA y explícita del usuario.
- **PROFESIONALISMO Y DETERMINISMO:** La IA jamás debe alucinar, simular o inventar vulnerabilidades. Todos los reportes deben ser 100% deterministas y basados en evidencia HTTP forense real capturada en producción.
- **REPORTES DE HACKERONE:** Todos los reportes generados y vinculados al Panel C2 se tratan como **reportes reales de producción** asociados a números de reporte verificados de HackerOne.
- **FUENTE ÚNICA DE VERDAD (SINGLE SOURCE OF TRUTH):** Nuestra verdad absoluta reside en los servidores OCI de producción (OCI-1 y OCI-2). El entorno local es únicamente el laboratorio de desarrollo. Al realizar reportes o escaneos, el agente **DEBE** alinear su contexto con la realidad de producción (por ejemplo, usando `scp` para descargar la base de datos más reciente de OCI-2, o consultando los logs directamente por SSH) antes de tomar decisiones. Asumir el estado local como la verdad es un error crítico.
- **USO DE GIT OBLIGATORIO:** Mantener la sincronización y la trazabilidad del código a través de Git es de máxima importancia para asegurar que el entorno local esté siempre alineado y documentado.

---

## ⚙️ 7. REGLAS DE ARQUITECTURA C2 Y SINCRONIZACIÓN OCI-2
- **INYECCIÓN AUTOMÁTICA H1:** El Panel C2 está configurado para inyectar automáticamente la evidencia forense en vivo dentro del bloque `## Supporting Material/References:` y generar los reportes con la plantilla estandarizada "Over-Delivered". Queda **PROHIBIDO** alterar los prompts en `main.py` para usar formatos personalizados por empresa, a menos que el usuario lo ordene explícitamente.
- **DESPLIEGUE CONTINUO OBLIGATORIO:** Si el agente modifica CUALQUIER archivo del backend o frontend del C2 (`main.py`, `app.js`, HTML), **DEBE** sincronizar los cambios de inmediato con OCI-2 (`143.47.115.34`) utilizando `scp` para no romper la experiencia en vivo del usuario.
- **REINICIO DE UVICORN:** Después de usar `scp` para mover `main.py`, el agente **DEBE** ejecutar un comando SSH para reiniciar la API remota: `ssh -i llave_oci ubuntu@143.47.115.34 "pkill -f uvicorn; sleep 3; cd /home/ubuntu/c2_panel && nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &"`
