# 📍 ESTADO ACTUAL DEL LABORATORIO
> Última actualización: 2026-07-07 | Leer completo antes de escribir código o hacer sugerencias.

## Quién soy y qué quiero
Soy un investigador de Bug Bounty en construcción. El objetivo del laboratorio es **generar el primer ingreso real** mediante reportes de vulnerabilidades en programas de HackerOne. Todo lo que se construya debe acercar a ese objetivo.

## Target activo: MongoDB Atlas
- **Programa:** MongoDB en HackerOne — https://hackerone.com/mongodb
- **Scope:** `*.mongodb.com`, incluyendo `cloud.mongodb.com`
- **Herramienta de intercepción:** Burp Suite Pro, configurado como proxy
- **Header obligatorio:** `X-HackerOne-Research: [mi_usuario]` en cada request
- **Panel objetivo:** https://cloud.mongodb.com (MongoDB Atlas)
- **Estado:** Burp canalizando tráfico. Fase de reconocimiento activa.

## Infraestructura del laboratorio

### Nodo local (PC de desarrollo)
- **Workspace:** `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/`
- **Repo principal:** `LAB/` (git en `LAB/.git`)
- **Agente CLI:** `LAB/api/run` → lanza PEGASO (Gemini 2.5 Flash con tool calling bash + memoria persistente)
- **Credenciales:** `LAB/api/.env` — contiene GROQ_API_KEY, GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

### Nodo OCI (servidor Ubuntu 24.04 — siempre encendido)
- **IP:** `129.80.73.248`
- **SSH:** `ssh ubuntu@129.80.73.248`
- **Directorio del proyecto:** `~/plataforma_operativa/`
- **Venv Python:** `~/workspace_lab/venv/`
- **Cron activo:** `0 6 * * *` ejecuta `run_pipeline.sh` → discovery → comparador → log

### Pipeline de monitoreo (OCI, automático)
```
Cada día 6AM:
  discovery_pasivo.py  → consulta crt.sh → resultados/actual.json
  comparador.py        → actual vs previo → resultados/delta_YYYY-MM-DD.json (si hay cambios)
  notificador.py       → si hay delta → mensaje a Telegram
```
- **Estado:** ✅ Operativo. `actual.json` actualizado al 06/07 a las 06:01.
- **Delta existente:** `delta_2026-07-05.json` (subdominios nuevos detectados el 05/07)
- **Dominios monitoreados:** Configurados en `~/plataforma_operativa/config/objetivos.txt`

### Notificaciones Telegram
- **Bot TOKEN:** en `.env`
- **CHAT_ID:** en `.env`
- **Estado:** ✅ Verificado. Mensajes llegando al celular.

## Módulo de IA local
- **`LAB/api/llm_client.py`:** Cliente Python con fallback Groq → Gemini. Sin dependencias externas (solo stdlib).
- **`LAB/api/notificador.py`:** Envío a Telegram vía urllib. Sin dependencias externas.
- **`LAB/api/pegaso.py`:** Agente ReAct con historial (16 turnos) + memoria comprimida de largo plazo.

## Flujo de trabajo hacia el primer ingreso

```
1. [Telegram] "Nuevo subdominio en mongodb.com"
        ↓
2. [OCI] Leer resultados/delta_*.json — ¿qué subdominio apareció?
        ↓
3. [Burp] Navegar el subdominio nuevo con proxy activo
   Buscar: ¿Responde? ¿Panel de login? ¿API expuesta? ¿Headers de seguridad?
        ↓
4. [Manual] Investigar la superficie de ataque
   Prioridades: subdomain takeover, auth bypass, info disclosure, IDOR
        ↓
5. [HackerOne] Si hay vulnerabilidad real → reportar con evidencia
   Formato: descripción + pasos de reproducción + impacto + screenshots
        ↓
6. [Cobrar] Bounty de $50 a $5000+ según criticidad
```

## Reglas del laboratorio (NO ignorar)
1. Una sola tarea por sesión.
2. Verificar el estado real del sistema antes de escribir código.
3. No generar código duplicado ni documentación redundante.
4. Cada sesión termina con: qué se logró / qué quedó pendiente / cuál es el siguiente paso exacto.
5. Todo debe acercar al primer ingreso real.

## Pendientes inmediatos
- [ ] Revisar `delta_2026-07-05.json` en OCI — ¿qué subdominios nuevos aparecieron?
- [ ] Verificar que los dominios en `objetivos.txt` sean programas activos de HackerOne con bounty
- [ ] Conectar `notificador.py` al pipeline del OCI para alertas automáticas de delta
- [ ] Primer reporte real a HackerOne (objetivo principal de la siguiente fase)

## Cómo usar PEGASO (agente CLI local)
```bash
/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/run
# O si tenés el alias configurado:
pegaso
```
PEGASO tiene acceso bash al sistema local y puede ejecutar comandos. Hablale en lenguaje natural.
Su memoria persiste entre sesiones en `LAB/api/.agent_memoria.md`.
