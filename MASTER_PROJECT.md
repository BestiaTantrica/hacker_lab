# 🌐 MASTER PROJECT: DOCUMENTACIÓN MAESTRA DEL LABORATORIO

## 📌 1. Propósito y Visión General
Este documento constituye la **Fuente Única de Verdad (Single Source of Truth)** para el laboratorio personal de ciberseguridad y operaciones. Centraliza el estado actual, las políticas de desarrollo, el inventario de componentes y la gobernanza del proyecto completo, abarcando tanto el **Nodo Local (PC)** como el **Nodo Remoto (Oracle Cloud)**.

El objetivo a largo plazo es construir una **plataforma personal de operaciones de ciberseguridad (SecOps)** orientada a:
- El monitoreo pasivo y continuo de activos (*Asset Discovery*).
- Apoyo a programas de Bug Bounty (especialmente scopes wildcard en HackerOne).
- Automatización y observabilidad sin penalizar recursos.
- Crecimiento profesional y aprendizaje autónomo.

---

## ⚙️ 2. Filosofía de Ingeniería y Trabajo
El desarrollo del laboratorio se rige bajo los siguientes principios inquebrantables (definidos en [PRINCIPIOS_DE_INGENIERIA.md](file:///home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/PRINCIPIOS_DE_INGENIERIA.md)):
1. **La Realidad tiene Prioridad:** Siempre verificar el sistema de archivos, configuración y logs antes de asumir el estado de una conversación previa.
2. **Complejidad Incremental:** No agregar componentes ni agentes que no se necesiten hoy. Diseñar soluciones simples y deterministas antes de introducir inteligencia artificial.
3. **Un Único Objetivo Funcional:** El desarrollo se divide en etapas pequeñas. No se inicia un nuevo componente hasta que el anterior funcione y esté validado.
4. **Optimización de Recursos (Oracle Free Tier):** Diseñar código ligero compatible con una instancia de 1 OCPU y 1 GB de RAM, minimizando el consumo de APIs externas.
5. **OPSEC y Privacidad:** Jamás subir llaves API, credenciales o datos confidenciales de objetivos a modelos de IA públicos.

---

## 🖥️ 3. Estructura de Nodos del Laboratorio
El laboratorio se divide físicamente en dos entornos de ejecución:

### A. Nodo Local (PC de Desarrollo)
- **Función:** Desarrollo de herramientas, pruebas locales, análisis forense offline y almacenamiento de la documentación del portafolio.
- **Proyectos Clave:**
  - `network-toolkit`: Herramienta modular en Bash para diagnóstico de red y Honeypot Local (trampas pasivas y alertas Telegram).
  - `asalto_local.sh` ("Modo Bestia Protegido"): Infraestructura de escaneo local en dos fases (recon y attack) con límites de concurrencia y filtros de CDN para no saturar la red doméstica.
  - `juego_piloto_cibersec`: Piloto educativo "MicroSecure" (Attention Mining, Feed de micro-insights ciberseguridad, Gamificación 1-clic).
  - `portal_noticias`: Portal Público "Radar Prensa & Termómetro Social" (puerto `8001`, FastAPI + Uvicorn). Medición de sesgo mediático, encuestas reales en tiempo real (`portal_db.sqlite`), filtrado regional/provincial, captura de newsletter y Fábrica de Shorts MP4 con locución TTS en español (`espeak-ng` + FFmpeg).
  - `caso fuerza bruta btc`: Entorno de análisis forense y descifrado bayesiano para carteras Bitcoin (wallet.dat 2013).
  - `portafolio-ciberseguridad`: Estructura académica alineada con el Certificado de Ciberseguridad de Google.

### B. Nodo Oracle Cloud Infrastructure (OCI)
- **Función:** Ejecución continua de tareas de monitoreo pasivo (*Asset Discovery*) y servicios de recolección de subdominios.
- **Ficha Técnica (Instancia Always Free):**
  - **Instancia ID:** `ocid1.instance.oc1.iad.anuwcljt7n2xbfycw5atakquf5njpwaxom4g5v3xdjb7becvjwhpj5bevp6q`
  - **Nombre:** `Lab-Cybersec-Micro`
  - **Shape:** `VM.Standard.E2.1.Micro` (1 OCPU AMD EPYC 7551, 1 GB RAM)
  - **SO:** Ubuntu 24.04.4 LTS (Kernel 6.17.0-1011-oracle x86_64)
  - **IP Pública:** `129.80.73.248`
  - **IP Privada:** `10.0.1.120`
  - **Estructura Base:** `~/plataforma_operativa` y `~/workspace_lab`

---

## 📂 4. Estructura de Documentación Maestra — Columna Vertebral (`/LAB/`)
Toda la documentación estratégica y gobernanza reside en `/home/tomas2/WORKSPACE/LAB/`:
- **[MASTER_PROJECT.md](file:///home/tomas2/WORKSPACE/LAB/MASTER_PROJECT.md):** Portal maestro y estado global del laboratorio.
- **[ESTADO_OPERATIVO_OCI1.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI1.md):** Estado operativo de OCI-1 (Pipeline Go-Stack v2, Katana/Alterx, Motor Anti-FP M3, Resiliencia M1).
- **[ESTADO_OPERATIVO_OCI2.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI2.md):** Estado operativo de OCI-2 (Panel C2 FastAPI, Taxonomía M4, Exportación Forense, Hub Skills IA).
- **[.agents/rules](file:///home/tomas2/WORKSPACE/LAB/.agents/rules):** Reglas operativas obligatorias del agente de IA, mapa de la columna vertebral y protocolo de eficiencia de tokens.
- **[espejo_oci1/](file:///home/tomas2/WORKSPACE/LAB/espejo_oci1/):** Réplica de la infraestructura de recolección masiva Go-Stack, validadores de scope y generadores PoC.
- **[c2_panel/](file:///home/tomas2/WORKSPACE/LAB/c2_panel/):** Código fuente de la consola Web (C2) con UI de ciclo de vida (Pending/Validated/Archived).
- **[skills/](file:///home/tomas2/WORKSPACE/LAB/skills/):** Plantillas de Prompts de IA para formateo de reportes y análisis automático.

---

## 🚦 5. Estado de Integración y Modo Operativo
El pipeline de recolección masiva en **OCI-1** está formalmente conectado con el **Panel C2 (OCI-2)**.

**Estado Operativo Actual (Pipeline v2 + 4 Módulos Integrados):**
- **M1 - Resiliencia Activa:** OCI-1 cuenta con Watchdog RAM asíncrono y Heartbeat pasivo hacia OCI-2 para prevenir bloqueos por OOM (Out Of Memory).
- **M2 - Reconocimiento Avanzado:** `run_zone_pipeline.sh` orquesta 6 eslabones que incluyen `alterx`/`dnsx` para permutaciones in-memory y `katana` para recolección dinámica de endpoints JS y extracción pasiva de secretos.
- **M3 - Validación Forense:** Motor Anti-Falsos Positivos integrado. Valida targets contra HackerOne, purifica comandos `curl` (PoC Generator) y rota headers WAF antes de enviar a C2.
- **M4 - C2 Lifecycle & Exportación:** `sync_to_c2_panel()` inyecta vulnerabilidades en `c2_db.sqlite`. La UI permite gestionar la máquina de estados (`Pendiente` -> `Validado` -> `Archivado`) y exportar reportes Markdown/PDF con cero overhead.
- **Notificaciones por Filtrado de Valor:** Telegram alerta de latidos perdidos y hallazgos verificados de alta calidad.

---

## 🏛️ 6. El Proyecto de Vida: Plataforma Educativa Integral (MicroSecure)
El desarrollo denominado internamente como "juego_piloto_cibersec" no es un simple juego, sino el embrión del trabajo de vida del autor. 
Es un proyecto a gran escala concebido como una red social y plataforma de aprendizaje diseñada para integrar, defender y expandir los valores de la cultura occidental.

**Pilares Ideológicos y Fundamentos:**
1. **Educación Invertida (Pagar por Aprender):** Romper el paradigma del sistema educativo tradicional (ineficiente, burocrático y politizado). Si la educación es la barrera entre la civilización y la barbarie, y los gobiernos malgastan los recursos, el sistema debe rediseñarse para recompensar económicamente al que estudia (Attention Mining). Panza llena y mente libre para coordinar.
2. **Eficiencia y Tecnología (IA vs. Burocracia):** Eliminar tiempos muertos y currículas obsoletas impartidas por sistemas anacrónicos. El tiempo corre rápido y la IA debe ser el motor que personalice, acelere y haga dinámico el aprendizaje. No hay necesidad de que el estudio sea aburrido o bloqueante.
3. **Rescate del Capital Humano:** Contraponerse a la voracidad económica que deshumaniza (modelo basado puramente en la extracción y la propaganda masiva). La plataforma busca devolver la libertad y el valor a las personas mediante el conocimiento práctico, la lógica y los principios occidentales.
4. **Alcance Global:** Orientado a profesores, alumnos, padres y cualquier persona del mundo (especialmente de otras culturas) que desee integrarse al estilo de vida occidental basado en la libertad individual y el desarrollo.

