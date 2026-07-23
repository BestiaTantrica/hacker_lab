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
  - `network-toolkit`: Herramienta modular en Bash para diagnóstico de red.
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

## 📂 4. Estructura de Documentación Maestra (`/LAB/`)
Toda la documentación estratégica reside en el directorio `/home/tomas2/WORKSPACE/LAB/`:
- **[MASTER_PROJECT.md](file:///home/tomas2/WORKSPACE/LAB/MASTER_PROJECT.md):** (Este archivo) Portal maestro y estado global.
- **[ESTADO_OPERATIVO_OCI1.md](file:///home/tomas2/WORKSPACE/LAB/ESTADO_OPERATIVO_OCI1.md):** Estado de la Red de Pesca automatizada en OCI-1.
- **[espejo_oci1/](file:///home/tomas2/WORKSPACE/LAB/espejo_oci1/):** Réplica de la infraestructura de ingestión pasiva y escaneo masivo (OCI-1).
- **[c2_panel/](file:///home/tomas2/WORKSPACE/LAB/c2_panel/):** Código fuente de la consola Web / Cerebro en OCI-2 (Base de Datos + Hub de Prompts IA + Alertas Telegram).
- **[skills/](file:///home/tomas2/WORKSPACE/LAB/skills/):** Plantillas de Prompts de IA para formateo de reportes y análisis automático.

---

## 🚦 5. Estado de Integración y Siguiente Paso
Actualmente, el repositorio ha sido completamente purgado de deudas técnicas (scripts manuales, wordlists obsoletas y guías estáticas). 

**Siguiente paso prioritario:**
Finalizar el desarrollo y sincronización del **Web C2 Panel (OCI-2)** para consumir directamente la API/JSONs de **OCI-1**, integrando la Base de Datos central y el Hub de Prompts de IA para la gestión de alertas y generación de reportes con 1 solo clic.
