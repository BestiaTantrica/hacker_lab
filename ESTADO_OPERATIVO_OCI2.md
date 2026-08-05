# Estado Operativo de OCI-2 (Panel C2 & Copilot Hub)

> Auditoría y Documentación de Consola Web C2 - 2026-07-25

El directorio `c2_panel/` alberga el servidor del **Web C2 Panel (OCI-2)**, la consola centralizada de observabilidad, ingesta de telemetría y hub de prompts de IA para el laboratorio.

---

## 1. Arquitectura y Componentes Base
- **Servidor Web / API Framework:** FastAPI (`c2_panel/main.py`) ejecutándose en puerto `8000`.
- **Base de Datos Central (`c2_db.sqlite`):**
  - Tabla `deltas`: Registro de subdominios descubiertos por zona (`zone`, `domain`, `subdomain`, `discovered_at`).
  - Tabla `findings`: Registro de vulnerabilidades verificadas (`target`, `vuln_type`, `severity`, `estimated_bounty`, `evidence`, `verified`, `reported`).
  - Tabla `chat_history`: Registro de interacciones unificadas aisladas por hallazgo (`source`, `role`, `message`, `finding_id`, `created_at`).
  - Tabla `heartbeats`: Registro del último latido emitido por cada zona de OCI-1, utilizado para el Dead Man's Switch (`zone`, `last_seen`).
- **Hub de Prompts & Skills Integradas (`SKILLS_PROMPTS`):**
  - `report_h1`: Generación de borrador de reporte formal en inglés para HackerOne con inferencia automática del programa.
  - `takeover_analysis`: Evaluación de CNAMEs huérfanos con formato H1 e inferencia de programa.
  - `cors_analysis`: Validación y PoC JS para ACAO/ACAC con formato H1 e inferencia de programa.
  - `aws_s3_leak`, `jwt_logic_bypass`, `ssrf_analysis`, `business_logic_api`, `bounty_argentina_pyme`.

---

## 2. Endpoints de Ingesta, Comunicación y Monitoreo
- `POST /api/ingest_delta`: Ingesta directa de telemetría desde OCI-1 (`deltas` y `findings`). Evidence ahora incluye `triager_poc`, `poc_quality`, `scope_program`.
- `POST /api/heartbeat`: Recibe el latido pasivo desde OCI-1 al finalizar cada pipeline de forma segura. Si el background loop (Dead Man's Switch) detecta >12h sin latidos, envía alerta a Telegram.
- `GET /api/status`: Diagnóstico SSH en tiempo real hacia OCI-1.
- `GET /api/findings` & `GET /api/deltas/{zone}`: Consultas de telemetría para la interfaz web.
- `POST /api/copilot/generate`: Ejecución de skills de IA pasando la evidencia cruda.
- `POST /api/chat`: Chat interactivo con **Pegaso**, aislado por `finding_id`.
- `GET /api/chat/context`: Inyección automática de memoria de sesión (estadísticas, heartbeats, hallazgos e historial de chat previo) para dar contexto a Pegaso al inicio.
- `POST /api/verify_bug`: Verificación en vivo de objetivos mediante invocaciones SSH `curl` contra OCI-1.
- `POST /api/notify_telegram`: Envío limpio de reportes aprobados en Markdown directamente al bot de Telegram.
- **M3-B `POST /api/findings/{id}/validate_scope`**: Valida si el target está in-scope H1.
- **M3-A `POST /api/findings/{id}/generate_poc`**: Sanitiza curl de Nuclei → `triager_poc` copiable.
- **M3-C `POST /api/findings/{id}/waf_probe`**: Sonda live via SSH curl con rotación de WAF headers.

---

## 3. Conexión con OCI-1 y Flujo Global
1. **OCI-1 (Red de Pesca):** Recolecta subdominios, filtra novedades y verifica exploits.
2. **Puente HTTP/API:** OCI-1 envía la información digerida a `POST /api/ingest_delta` en OCI-2.
3. **OCI-2 (Panel C2 & IA):** Almacena hallazgos en `c2_db.sqlite`, gestiona el ciclo de vida de los bugs (Pendiente → Validado → Archivado) y provee interfaz de memoria contextual para Pegaso.

---

## 4. Estado de Implementación (Actualizado)
- **Archivado de Reportes:** ✅ Implementado. Ciclo de vida M4 activo (Pending -> Validated -> Archived).
- **Exportación Forense:** ✅ Implementado. Reportes nativos Markdown y PDF exportables desde UI sin overhead.
- **Memoria de IA (Pegaso):** ✅ Implementado. Endpoint `/api/chat/context` inyecta el estado de OCI-1/OCI-2 sin gastar tokens extra en cada mensaje.
- **MicroSecure & Botonera de Enlaces:** ✅ Implementado. Servidor estático en `/microsecure/`, centro de enlaces en UI y vista HTML dedicada en `/portfolio`.
- **Tokens Canario (Señuelos Pasivos):** ✅ Implementado. 8 rutas trampa (`/.env`, `/.git/config`, etc.) con notificaciones automáticas a Telegram en background.
