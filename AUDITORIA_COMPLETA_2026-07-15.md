# 🔎 AUDITORÍA COMPLETA DEL LABORATORIO
> Fecha: 2026-07-15 | Ejecutada por: Antigravity (Claude Sonnet 4.6)
> **Propósito:** Que Tomas sepa exactamente dónde está parado, qué existe, qué está roto, y qué es el único próximo paso.

---

## 1. MAPA DE TODOS LOS "PROMPTS DE PERSONALIDAD / CONTEXTO" DEL PROYECTO

Este es el problema raíz de la pérdida de contexto entre sesiones. Hay **demasiados documentos** intentando explicarle a la IA quién eres y qué haces. Se contradicen entre sí y están desactualizados.

| Archivo | Propósito | Estado | Acción |
|---|---|---|---|
| `LAB/HOJA_DE_RUTA.md` | Reglas filosóficas + etapas del OCI pipeline | ⚠️ Desactualizado (dice que el pipeline OCI no existe, pero ya funciona) | Archivar o fusionar en ESTADO_ACTUAL.md |
| `LAB/MASTER_PROJECT.md` | "Fuente única de verdad" del proyecto global | ⚠️ Desactualizado (dice que OCI no tiene scripts, pero ya los tiene corriendo) | Actualizar o fusionar |
| `LAB/ESTADO_ACTUAL.md` | Estado real del lab al 08/07 | ✅ El más actualizado pero **duplicado en sí mismo** (tiene la sección "Quién soy" dos veces al final) | Limpiar duplicado interno |
| `LAB/ARQUITECTURA_PIPELINE.md` | Cómo funciona el pipeline de OCI con IA | ✅ Bien documentado. Es el más útil para entender el sistema. | Conservar |
| `LAB/CONTEXTO_ACTIVO.md` | Target activo, cuentas, herramientas, restricciones | ✅ Más específico para sesiones de Bug Bounty | Conservar, pero actualizar estado de Elastic |
| `LAB/INVENTARIO.md` | Catálogo técnico detallado de todo | ⚠️ De Junio 29, muy desactualizado | Marcar como obsoleto |
| `LAB/ROADMAP.md` | Plan de etapas | ✅ Recién actualizado hoy (Julio 15) | Conservar |
| `LAB/DIRECTRICES_AGENTE.md` | Instrucciones para la IA sobre qué no hacer | ✅ Recién creado hoy | Conservar |
| `LAB/AUDITORIAS/kit_delegacion_ias.md` | Kit para delegar tareas a IAs | Para IA, no para Tomas | Revisar si se usa |
| `LAB/AUDITORIAS/kit_proximas_etapas.md` | Próximas etapas del pipeline | ⚠️ Probablemente desactualizado | Revisar |
| `LAB/api/.agent_memoria.md` | Memoria corta de PEGASO (agente CLI local) | ⚠️ Tiene tarea pendiente sin resolver: `chat_id` de Telegram | VER SECCIÓN 2 |

> [!WARNING]
> Hay **11 documentos** de contexto. Ninguna IA puede leerlos todos en cada sesión. Ese es el motivo del sesgo y la pérdida de contexto. La solución a largo plazo es consolidar en UN solo archivo de contexto que se lea primero en cada sesión.

---

## 2. ESTADO REAL DE CADA LÍNEA DE TRABAJO

### 🎯 LÍNEA 1: Bug Bounty MongoDB (HackerOne)

**Concepto clave (IDOR):** Para probar si MongoDB permite que un usuario acceda a datos de otro, necesitás DOS cuentas tuyas. La Cuenta A intenta ver recursos de la Cuenta B. Si puede → es un bug reportable.

**Tus cuentas de prueba (ya en el código):**

| Cuenta | Email | Rol | Org ID | Project ID |
|---|---|---|---|---|
| **A (Atacante)** | tomas244 (H1 alias) | El que hace las pruebas | `6a4c0a54b388b65b11799a24` | `6a4c0a54b388b65b11799a58` |
| **B (Víctima)** | tomasreis44@gmail.com | La "víctima" controlada | `6a4d7d849d5dcab6abad6820` | `6a4d7d849d5dcab6abad6845` |

**Resultados de la auditoría automatizada ya ejecutada:**

| Vector | Qué se probó | Resultado | ¿Es bug? |
|---|---|---|---|
| **V1 - IDOR usuarios** | Acceder a usuarios del cluster de Cuenta B | 303/403 | ❌ Control correcto |
| **V2 - CORS** | Reflejar Origin malicioso en endpoints normales | Origen fijo, no refleja | ❌ Control correcto |
| **V3 - IDOR cluster** | Acceder a config del cluster de Cuenta B | 303/403 | ❌ Control correcto |
| **V4 - Billing** | Billing de Cuenta B vs org falsa | Ambos dan mismo 403 | ❌ No hay oráculo |
| **V5 - AI Keys IDOR** | Acceder a API Keys de IA del Proyecto B | 200 con HTML de login | ⚠️ **INCONCLUSO** - Cookie vencida |
| **V6 - CORS Preflight** | OPTIONS con Origin evil.mongodb.com | `ACAO: evil.mongodb.com` + `ACAC: true` | ✅ **POSIBLE BUG** - Pero requiere XSS en subdominio para explotar |

> [!IMPORTANT]
> El V5 está **inconcluso porque la cookie de sesión usada estaba vencida o mal copiada**. Los cruces devolvieron una página HTML de login en vez de datos JSON. Repetirlo con cookie fresca es el único trabajo pendiente de MongoDB.

---

### 🎯 LÍNEA 2: Bug Bounty Elastic (HackerOne)

**¿Por qué te bloqueaste?**
La guía existente te pedía crear cuenta en Elastic Cloud → configurar Burp → navegar manualmente. Eso requiere tiempo y resulta frustrante. Pero hay trabajo valioso que no requiere cuenta.

**Subdominios críticos ya descubiertos (pipeline OCI):**
- 🔥 `secrets.elastic.co`
- 🔥 `vault-acc.elastic.co` / `vault-test.elastic.co`
- 🔥 `www.jenkins.elastic.co`
- 🟡 `www.internal-ci.elastic.co`, `staging-deepthought.elastic.co`

**Lo que falta:** Nunca se ejecutó `validador_headers.py` contra estos subdominios. Eso no requiere cuenta, no requiere Burp, se hace en un comando desde tu terminal.

---

### ⚙️ LÍNEA 3: Pipeline OCI (automatización)

| Componente | Estado |
|---|---|
| `subfinder` descubriendo subdominios | ✅ Corriendo diario a 03:00 UTC |
| `comparador.py` generando deltas | ✅ Funcional |
| Alertas a Telegram | ⚠️ `chat_id` tuvo problema en PEGASO — puede estar mal en `.env` del servidor OCI |
| `analizador_ia.py` (filtro IA) | ❌ Existe localmente pero **NO está desplegado en OCI todavía** |

---

## 3. ARQUITECTURA DEL SISTEMA (Diagrama simple)

```
CADA NOCHE (Servidor OCI en la nube)
┌─────────────────────────────────────────────────────┐
│  subfinder → subdominios de mongodb.com y elastic.co│
│  comparador.py → ¿hay algo nuevo hoy?               │
│  [FALTA DESPLEGAR] analizador_ia.py → filtra top 5  │
│  notificador.py → Telegram a tu celular             │
└─────────────────────────────────────────────────────┘

CUANDO VOS INVESTIGÁS (Tu PC)
┌─────────────────────────────────────────────────────┐
│  Sin cuenta → validador_headers.py (Elastic targets)│
│  Con cookie → auditar_vectores.py (MongoDB IDOR)    │
│  Con tráfico Burp → parseador_burp.py               │
│  Agente CLI → ./run en LAB/api/ (PEGASO)            │
└─────────────────────────────────────────────────────┘

SI ENCONTRÁS ALGO
└─ Redactar reporte usando LAB/skills/SKILL-REPORT-H1.md
```

---

## 4. DEUDA TÉCNICA (Ordenada por impacto)

| # | Problema | Por qué importa | Costo de arreglo |
|---|---|---|---|
| 🔴 1 | **V5 MongoDB inconcluso** (cookie vencida) | Podría ser el primer ingreso | **Bajo** — Loguear, copiar cookie, ejecutar script |
| 🔴 2 | **Elastic sin validar** (subdominios críticos nunca revisados) | Blancos de alto valor sin tocar | **Bajo** — Un comando local |
| 🟡 3 | **`chat_id` Telegram puede estar mal** | Alertas del pipeline podrían no llegar | **Bajo** — Verificar `.env` en OCI |
| 🟡 4 | **`analizador_ia.py` no está en OCI** | El pipeline no filtra inteligentemente | **Medio** — Desplegar archivo al servidor |
| 🟢 5 | **11 documentos de contexto desactualizados** | La IA se pierde en cada sesión nueva | **Alto** — Consolidar en 1 archivo maestro |

---

## 5. EL ÚNICO PRÓXIMO PASO (Para esta sesión)

**Objetivo:** Cerrar el Vector 5 de MongoDB.

**Por qué este:** Ya tenés el script escrito, los IDs hardcodeados, y el único bloqueante fue una cookie vencida. Es el trabajo con el menor esfuerzo y el mayor potencial de ingreso.

**Pasos exactos:**
1. Ir a `https://cloud.mongodb.com` en Firefox
2. Loguearte como **Cuenta A** (tu cuenta principal tomas244)
3. Abrir F12 → pestaña Network → clic en cualquier request a `cloud.mongodb.com`
4. En los Headers del request, copiar el valor completo de la línea `Cookie: ...`
5. En tu terminal ejecutar:
```bash
python3 /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/auditar_vectores.py "PEGAR_AQUI_LA_COOKIE_COMPLETA"
```
6. Leer el resultado en `LAB/AUDITORIAS/RESULTADO_AUDITORIA_VECTORES.md`

**Si V5 da 403** → MongoDB está cerrado, pasamos a Elastic con `validador_headers.py`.
**Si V5 da 200 con JSON de Cuenta B** → BUG CONFIRMADO, redactar reporte con `SKILL-REPORT-H1.md`.
