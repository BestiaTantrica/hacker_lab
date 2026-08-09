# 🛡️ Autonomous SecOps & C2 Infrastructure

## 📌 Resumen del Proyecto
Este proyecto es una arquitectura de recolección de inteligencia y monitoreo pasivo (Asset Discovery) completamente autónoma y distribuida. Diseñada desde cero para operar bajo estrictas restricciones de hardware (Cloud Free Tier), orquesta herramientas avanzadas de ciberseguridad mediante un flujo de trabajo continuo (Pipeline), reportando todo a una consola centralizada de Comando y Control (C2).

**Rol:** Arquitecto de Infraestructura / DevSecOps  
**Enfoque:** Automatización, Eficiencia en la Nube, Redes Privadas y Desarrollo Backend.

---

## 🏗️ Arquitectura del Sistema (Topología)

El sistema opera sobre una **malla VPN privada (Tailscale)** que conecta servidores en la nube con hardware local, garantizando que el tráfico de gestión y los datos forenses estén 100% cifrados y fuera de la internet pública.

1. **Nodo OCI-1 (Reconocimiento Automático):**
   * Servidor en Oracle Cloud (Linux Ubuntu).
   * Ejecuta un Pipeline de 6 eslabones automatizado mediante `cron`.
   * **Motor (Go-Stack):** Orquesta herramientas líderes en la industria (`subfinder`, `alterx`, `httpx`, `katana`, `nuclei`) para descubrimiento y análisis de superficies de ataque.
   * **Resiliencia:** Implementación de un "RAM Watchdog" asíncrono para prevenir colapsos por falta de memoria (OOM), vital para entornos limitados (1GB RAM).

2. **Nodo OCI-2 (Cerebro y Panel C2):**
   * Servidor central que aloja la base de datos `SQLite` (modo WAL para alta concurrencia).
   * **Backend:** API REST desarrollada en **Python (FastAPI)**, sirviendo a través de `Uvicorn`.
   * **Frontend:** Interfaz web asíncrona (Vanilla JS/CSS) para clasificar vulnerabilidades mediante un sistema de estados (`Pendiente`, `Validado`, `Archivado`).
   * **Notificaciones:** Integración de Webhooks y bots de **Telegram** para alertas en tiempo real sobre latidos de red (Heartbeats) y hallazgos críticos.

3. **Nodos Locales (Heavy Lifters):**
   * Computadoras de escritorio integradas al clúster (Tailscale Swarm) para análisis bajo demanda y procesamiento forense pesado.

---

## 🛠️ Stack Tecnológico y Habilidades Demostradas

* **Cloud & Networking:** Oracle Cloud Infrastructure (OCI), Tailscale (Mesh VPN), Cloudflare Tunnels.
* **Backend & API:** Python 3, FastAPI, SQLite, JSONL processing.
* **Automatización (DevOps):** Bash Scripting avanzado, Systemd, Crontab, Pipelines de datos.
* **Herramientas de Ciberseguridad (Integración):** Nuclei, Katana, Subfinder, Httpx (ProjectDiscovery).
* **Control de Versiones & OPSEC:** Git, gestión segura de llaves SSH y tokens de API.

---

## 💡 Resoluciones Técnicas Destacadas (Problem Solving)

1. **Gestión Extrema de Memoria:** Se desarrolló un sistema `Circuit Breaker` para ejecutar binarios pesados (como `nuclei` y `katana`) en instancias de 1 OCPU / 1GB RAM sin colapsar el kernel, calculando el tamaño de los lotes de escaneo dinámicamente según la RAM disponible (`/proc/meminfo`).
2. **Motor Anti-Falsos Positivos:** Creación de un script intermedio (`poc_generator.py`) que purifica comandos de red crudos y aplica guardrails semánticos antes de inyectarlos en la base de datos de producción.
3. **Dead Man's Switch (Heartbeat):** Implementación de una señal de vida constante entre los servidores. Si el nodo recolector se cuelga, el C2 lo detecta y envía una alerta al administrador vía Telegram.

---

> *"No se trata solo de encontrar fallas; se trata de construir sistemas autónomos capaces de buscar, clasificar y reportar información a gran escala sin intervención humana."*
