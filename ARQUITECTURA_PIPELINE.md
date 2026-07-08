# 🏗️ ARQUITECTURA DEL LABORATORIO — Bug Bounty Pipeline

> Documento de referencia. Leer COMPLETO antes de empezar cualquier sesión.
> Última actualización: 2026-07-08

---

## 1. ¿Cómo funciona el sistema completo?

```
┌─────────────────────────────────────────────────────────────┐
│                   SERVIDOR OCI (03:00 UTC)                  │
│                                                             │
│  [discovery_pasivo.py]  →  actual.json (7000 subdominios)   │
│         ↓ subfinder                                         │
│  [comparador.py]        →  delta_HOY.json (los NUEVOS)      │
│         ↓                                                   │
│  [analizador_ia.py] ←── FALTA CONSTRUIR ───→  analisis.json │
│    (llama a Groq/Gemini, clasifica, prioriza)               │
│         ↓                                                   │
│  [notificador.py]       →  Mensaje a Telegram               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
            │ Telegram
            ↓
┌───────────────────────────────────┐
│          TU CELULAR               │
│                                   │
│  "⚡ 3 objetivos críticos hoy:    │
│   - secrets.elastic.co (admin)    │
│   - api-dev.mongodb.com (api)     │
│   - vault-test.elastic.co (vault) │
│                                   │
│   Groq dice: atacar secrets       │
│   primero por X razón..."         │
└───────────────────────────────────┘
            │ Tú decides
            ↓
┌───────────────────────────────────┐
│       TU PC — BURP SUITE          │
│                                   │
│  Cargas burp_config_elastic.json  │
│  Navegas a secrets.elastic.co     │
│  Burp inyecta el header H1        │
│  Investigas manualmente           │
└───────────────────────────────────┘
```

---

## 2. Componentes existentes (ya construidos)

| Archivo | Dónde vive | Qué hace |
|---|---|---|
| `discovery_pasivo.py` | OCI: `~/plataforma_operativa/monitores/` | Busca subdominios con subfinder + crt.sh |
| `comparador.py` | OCI: `~/plataforma_operativa/monitores/` | Detecta subdominios nuevos vs. ayer |
| `run_pipeline.sh` | OCI: `~/plataforma_operativa/` | Orquesta discovery + comparador (cron 03:00 UTC) |
| `notificador.py` | OCI + local `LAB/api/` | Envía mensajes a Telegram |
| `llm_client.py` | local `LAB/api/` | Cliente Groq+Gemini con fallback |
| `burp_config_mongodb.json` | local `LAB/api/` | Configura Burp para MongoDB (scope + header H1) |

---

## 3. Lo que FALTA construir (próxima sesión)

### `analizador_ia.py` (EL MÁS IMPORTANTE)
Debe hacer esto, en este orden:
1. Leer `delta_HOY.json` del servidor (los subdominios nuevos del día).
2. Armar un prompt para Groq con la lista.
3. Groq filtra y prioriza: devuelve un TOP 5 con razones.
4. El resultado se pasa a `notificador.py` → Telegram.
5. Este script se agrega al final de `run_pipeline.sh`.

### `burp_config_elastic.json`
Igual que el de MongoDB pero con scope en `*.elastic.co`.

---

## 4. Estado de las claves (APIs y credenciales)

### En tu PC local (`LAB/api/.env`)
```
GROQ_API_KEY=...      ← Para el analizador IA
GEMINI_API_KEY=...    ← Fallback del analizador
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### En el servidor OCI (`~/plataforma_operativa/config/entorno.env`)
El pipeline del servidor necesita las mismas claves.
**Pendiente verificar:** ¿Tiene GROQ_API_KEY cargada? Si no, el analizador no funcionará en OCI.

### Verificar con este comando (ejecutar en tu terminal):
```bash
ssh -i /home/tomas2/WORKSPACE/tomas2/.ssh/id_rsa ubuntu@129.80.73.248 \
  "cat ~/plataforma_operativa/config/entorno.env"
```

---

## 5. Configuración de Burp Suite

### Para MongoDB (ya existe)
Archivo: `LAB/api/burp_config_mongodb.json`
- **Scope:** `cloud.mongodb.com`, `account.mongodb.com`
- **Header automático:** `X-HackerOne-Research: tomas244`
- **Cómo cargarlo:** Burp → Gear ⚙️ → Project options → Load → seleccionar el archivo.

### Para Elastic (pendiente crear)
Archivo: `LAB/api/burp_config_elastic.json` → **Crear en próxima sesión**
- **Scope:** `*.elastic.co` (wildcard)
- **Header automático:** `X-HackerOne-Research: tomas244`

---

## 6. ¿Puedo interactuar con la IA por Telegram?

**No, y no es necesario.** El flujo actual es:
- **OCI trabaja solo de noche** → analiza → te avisa por Telegram.
- **Tú recibes el resumen** → decides qué atacar → abres Burp.
- **No necesitas responder nada por Telegram.**

Si en el futuro quisieras dar comandos por Telegram (ej: "analiza tal dominio") eso requeriría un bot interactivo con webhook, que es una complejidad innecesaria por ahora. El objetivo es el primer ingreso, no el mejor bot.

---

## 7. Prompt para generar `analizador_ia.py` con Claude

Copia esto en Claude o donde prefieras para generar el código:

```
Necesito un script Python llamado `analizador_ia.py` para un laboratorio de Bug Bounty.

CONTEXTO:
- Tengo un archivo `resultados/delta_HOY.json` con subdominios nuevos detectados hoy.
- Formato del delta: {"timestamp": "...", "elastic.co": ["sub1.elastic.co", ...], "mongodb.com": [...]}
- Tengo un cliente LLM ya construido (`llm_client.py`) con función `completar(prompt, max_tokens)`.
- Tengo un notificador Telegram ya construido (`notificador.py`) con función `send_telegram(mensaje)`.

QUÉ DEBE HACER EL SCRIPT:
1. Leer el archivo delta más reciente de la carpeta `resultados/`.
2. Si no hay delta, terminar en silencio (no hay novedades).
3. Armar un prompt con todos los subdominios nuevos y enviarlo a la IA con este objetivo:
   "Eres un experto en Bug Bounty. De esta lista de subdominios, extrae el TOP 5 más interesante 
   para investigar. Prioriza palabras como: admin, api, dev, test, staging, secret, vault, jenkins, 
   internal, ci, auth, login, dashboard. Para cada uno explica en 1 línea por qué es interesante."
4. Recibir la respuesta de la IA.
5. Formatear un mensaje Markdown para Telegram y enviarlo.
6. Guardar la respuesta en `resultados/analisis_HOY.json` como registro.

RESTRICCIONES:
- Solo stdlib de Python + los dos módulos locales (llm_client.py, notificador.py).
- Debe ser robusto: si la IA falla, igualmente enviar los dominios sin analizar por Telegram.
- Ruta base: `/home/ubuntu/plataforma_operativa/`
```

---

## 8. Próximos pasos en orden de prioridad

1. **[Ahora]** Ejecutar: `ssh ubuntu@... "cat ~/plataforma_operativa/config/entorno.env"` para confirmar claves en OCI.
2. **[Próxima sesión]** Construir `analizador_ia.py` con el prompt de arriba + revisión.
3. **[Próxima sesión]** Agregar `analizador_ia.py` al `run_pipeline.sh`.
4. **[Próxima sesión]** Crear `burp_config_elastic.json`.
5. **[Cuando tengas cuenta H1 en Elastic]** Iniciar auditoría manual de subdominios críticos.
