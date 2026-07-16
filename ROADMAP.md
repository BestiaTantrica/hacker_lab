# 🗺️ ROADMAP DEL LABORATORIO

> Este roadmap refleja el **estado real del sistema** (Auditado 2026-07-15).
> No contiene arquitecturas inventadas. Cada etapa produce un resultado funcional verificable.
> Una etapa no comienza hasta que la anterior esté completa y validada.

---

## ✅ ESTADO ACTUAL (Verificado 2026-07-15)

| Nodo | Componente | Estado |
|---|---|---|
| Local | `network-toolkit` | ✅ Funcional. Movido a `/LAB/herramientas/`. |
| Local | `plataforma_operativa` | ✅ Movida a `/LAB/herramientas/`. |
| Local | `portafolio-ciberseguridad` | ✅ Limpio, contiene solo documentación y teoría. |
| Local | Archivos sensibles | ✅ `mongo` y `códigos de respaldo h1` movidos a `.boveda/`. |
| OCI | Pipeline Discovery | ✅ Operativo (03:00 UTC). Usa subfinder. `actual.json` se genera. |
| OCI | Comparador y Alertas | ✅ Operativo. Envia alertas de subdominios a Telegram. |

---

## 🚀 ETAPA 1 — Automatización del Análisis de Vulnerabilidades (Low-Hanging Fruits)
**Prioridad:** Alta | **Objetivo:** Resolver el "cuello de botella" manual de Burp Suite que detiene el progreso.

### Problema actual:
El pipeline en OCI encuentra subdominios nuevos y los manda por Telegram. Pero la revisión manual en Burp Suite de cada subdominio es lenta, repetitiva y frena el progreso. Se necesita automatizar la búsqueda de fallos fáciles de explotar.

### Tareas:
- [ ] **[NUCLEI]** Instalar y configurar `nuclei` de ProjectDiscovery (escáner automatizado de vulnerabilidades basadas en plantillas) en el servidor OCI o en el nodo local.
- [ ] **[PIPELINE]** Integrar `httpx` (para verificar qué subdominios descubiertos están vivos) y pasar sus resultados directamente a `nuclei`.
- [ ] **[ALERTAS]** Configurar Telegram para que no solo avise de "nuevos subdominios", sino de "vulnerabilidades críticas/medias encontradas automáticamente".
- [ ] **[MANUAL REDUCIDO]** Usar Burp Suite *únicamente* cuando `nuclei` detecta paneles de login ocultos, o para probar vectores lógicos complejos (IDOR) que la IA o Nuclei no pueden resolver.

**Criterio de éxito:** El pipeline de OCI descubre un subdominio, confirma si hay web activa (`httpx`), escanea vulnerabilidades conocidas automáticamente (`nuclei`), y solo avisa a Telegram si hay algo accionable que reportar.

---

## 🎯 ETAPA 2 — Ejecución en Objetivos Activos
**Prioridad:** Media-Alta

### Tareas:
- [ ] **MongoDB (`*.mongodb.com`):** Retomar auditoría de vectores pendientes en el entorno de Atlas (CORS/IDOR) solo sobre hallazgos curados.
- [ ] **Elastic (`*.elastic.co`):** Investigar manualmente los activos críticos ya descubiertos (`secrets.elastic.co`, `vault-*.elastic.co`, `www.jenkins.elastic.co`).

---

## 🤖 ETAPA 3 — Refactorización del Sistema de "Skills"
**Prioridad:** Media

### Tareas:
- [ ] **Auditar el directorio `LAB/skills/`**: Los prompts actuales están fallando o causando sesgos (hallazgo del 15 de Julio). Revisar la lógica de `SKILL-IDOR-TEST.md`, `SKILL-XSS-TEST.md`, etc.
- [ ] **Conversión a Flujos Deterministas:** Convertir las skills de IA en scripts o flujos deterministas (`bash`/`python`) siempre que sea posible, para no depender de que el LLM alucine instrucciones correctas de seguridad.

---

> 📌 **Regla de oro del roadmap:** Si una etapa no tiene su criterio de éxito cumplido, la siguiente etapa no comienza.
