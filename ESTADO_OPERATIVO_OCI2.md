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
- **Hub de Prompts & Skills Integradas (`SKILLS_PROMPTS`):**
  - `report_h1`: Generación de borrador de reporte formal en inglés para HackerOne con inferencia automática del programa.
  - `takeover_analysis`: Evaluación de CNAMEs huérfanos con formato H1 e inferencia de programa.
  - `cors_analysis`: Validación y PoC JS para ACAO/ACAC con formato H1 e inferencia de programa.
  - `aws_s3_leak`, `jwt_logic_bypass`, `ssrf_analysis`, `business_logic_api`, `bounty_argentina_pyme`.

---

## 2. Endpoints de Ingesta y Comunicación
- `POST /api/ingest_delta`: Ingesta directa de telemetría desde OCI-1 (`deltas` y `findings`).
- `GET /api/status`: Diagnóstico SSH en tiempo real hacia OCI-1.
- `GET /api/findings` & `GET /api/deltas/{zone}`: Consultas de telemetría para la interfaz web.
- `POST /api/copilot/generate`: Ejecución de skills de IA pasando la evidencia cruda.
- `POST /api/chat`: Chat interactivo con **Pegaso**, aislado por `finding_id` con ventana de memoria de hasta 20 mensajes.
- `POST /api/verify_bug`: Verificación en vivo de objetivos mediante invocaciones SSH `curl` contra OCI-1.
- `POST /api/notify_telegram`: Envío limpio de reportes aprobados en Markdown directamente al bot de Telegram.

---

## 3. Conexión con OCI-1 y Flujo Global
1. **OCI-1 (Red de Pesca):** Recolecta subdominios (`mass_recon.py`), filtra novedades (`comparador.py`) y verifica exploits (`explotador_automatico.py`).
2. **Puente HTTP/API:** OCI-1 envía la información digerida a `POST /api/ingest_delta` en OCI-2.
3. **OCI-2 (Panel C2 & IA):** Almacena hallazgos en `c2_db.sqlite`, los muestra en la interfaz web split-screen, permite verificar en vivo desde OCI-1, aislar memoria de chat por PoC e inferir el programa HackerOne para envío inmediato a Telegram.

---

## 4. Tareas Pendientes y Evolución UI (Para la Próxima Sesión)
- **Archivado de Reportes:** Implementar lógica para que cuando el usuario haga clic en "Abrir e Inyectar en HackerOne", el `finding` cambie de estado a `reported = true` (o se archive) y desaparezca de la lista principal de bugs activos en el Dashboard.
- **Historial de Reportes:** Crear una vista secundaria o modal en el Panel C2 para consultar el archivo histórico de vulnerabilidades enviadas/resueltas, leyendo los hallazgos archivados de `c2_db.sqlite`.
- **Guía de Reporte:** Guiar al usuario paso a paso en el flujo de envío de HackerOne en el inicio del próximo hilo.
