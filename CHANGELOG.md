# 📋 CHANGELOG DEL LABORATORIO

Historial de cambios y eventos del laboratorio. Registrar aquí cada modificación relevante.

Formato: `[YYYY-MM-DD] [TIPO] Descripción`
Tipos: `FEAT` (nueva función), `FIX` (corrección), `DOCS` (documentación), `INFRA` (infraestructura), `SEC` (seguridad), `AUDIT` (auditoría)

---

## 2026-06-29

### [AUDIT] Auditoría Maestra del Laboratorio
- Realizada auditoría completa del Nodo Local (PC) por Antigravity AI.
- Inventariados todos los proyectos, scripts, dependencias y estados.
- Detectados 10 problemas clasificados por severidad (ver `INVENTARIO.md`).
- Creada la estructura completa de documentación en `/LAB/`.
- Auditado el nodo OCI parcialmente (sin acceso SSH directo desde el sandbox del agente).

### [DOCS] Creación de la Estructura Documental `/LAB/`
- Creado `MASTER_PROJECT.md` — Portal maestro y estado global.
- Creado `ARQUITECTURA.md` — Diagramas de flujo y políticas de diseño.
- Creado `INVENTARIO.md` — Catálogo técnico completo del laboratorio.
- Creado `ROADMAP.md` — Plan de desarrollo por etapas funcionales.
- Creado `CHANGELOG.md` — Este archivo.
- Integrados documentos previos: `HOJA_DE_RUTA.md` y `PRINCIPIOS_DE_INGENIERIA.md` (preexistentes).

---

## 2026-06-27

### [FEAT] `network-toolkit` v1.0.0 — Health Check Module + Self-Test
- Commit `224bf17`: Agregado framework de self-test (14 pruebas), capa de validación y módulo `01_health_check.sh`.
- El health check realiza diagnóstico integral L2→L7 (sistema, interfaces, config, conectividad, servicios).
- Genera reportes en formato JSON y TXT en `reports/`.

### [INFRA] Despliegue de Nodo Oracle Cloud (OCI)
- Creada topología de red limpia `VCN-Lab-Cybersec` (10.0.0.0/16) con DNS nativo habilitado.
- Desplegada instancia `Lab-Cybersec-Micro` (VM.Standard.E2.1.Micro, Ubuntu 24.04.4 LTS).
- IP pública asignada: `129.80.73.248`.
- Estado: `AVAILABLE`, free-tier-retained confirmado.
- Documentado en `informe_despliegue_oci.txt`.

### [FEAT] `network-toolkit` — Arquitectura Core Inicial
- Commit `258ac6e`: Inicializada arquitectura modular con sistema de plugins.
- Core: `logger.sh`, `error_handler.sh`, `module_loader.sh`, `reporter.sh`, `ui.sh`, `validator.sh`.
- Entry point: `bin/net-toolkit`. Configuración centralizada en `conf/toolkit.conf`.

---

## 2026-06-12

### [AUDIT] Análisis Forense Wallet Bitcoin 2013
- Creado directorio `caso fuerza bruta btc/` con `wallet.dat` del reto público @marcebit.
- Desarrollado `generator.py`: generador de micro-diccionario bayesiano con 10 tiers de probabilidad.
- Generado `micro_diccionario.txt` (~100 KB, prioridad lingüística en español rioplatense).
- Target: hashcat modo 11300 con `hash.txt` extraído de `wallet.dat` con `bitcoin2john.py`.

---

## 2026-06-03

### [AUDIT] Auditoría Ficticia Botium Toys
- Creados documentos de auditoría en `02_Marcos_de_Referencia/auditoria ficticia/`.
- Incluye: scope/goals/risk assessment, categorías de control, checklist de controles y cumplimiento.

---

## 2026-06-01

### [FEAT] Inicialización del Portafolio de Ciberseguridad
- Commit `0a4b5ac`: Creada estructura inicial del portafolio.
- Directorios: `01_Identidad_Profesional`, `02_Marcos_de_Referencia`, `03_Manuales_Forense`, `04_Laboratorio_IA`.
- Commit `1e86855`: Refinado el Career Identity Statement con enfoque en Bug Bounty.
