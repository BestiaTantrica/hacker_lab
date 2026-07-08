# 🔍 ANÁLISIS Y PLAYBOOK: MONGODB Bug Bounty (HackerOne)

> **Estado:** En ejecución — Tráfico capturado y analizado (2026-07-07)
> **Propósito:** Guía completa de referencia para esta campaña. Desde setup legal hasta paso a paso de cada vector.
> **Regla de uso:** Siempre leer la sección 2 (Marco Legal) antes de ejecutar cualquier prueba.

---

## 1. COMPARATIVA RÁPIDA: MONGODB vs. MEESHO

| Característica | Meesho | MongoDB | Veredicto |
| :--- | :--- | :--- | :--- |
| **Tiempo de Respuesta** | ~22 horas | **1 hora** | **MongoDB** |
| **Pago Mínimo (Low)** | $50 | **$100** | **MongoDB** |
| **Pago Promedio (Medium)** | $308 | **$500** | **MongoDB** |
| **Riesgo de Geobloqueo** | 🔴 Muy Alto | 🟢 Muy Bajo | **MongoDB** |
| **Entorno de Pruebas** | Cuentas compartidas | **Cuentas propias (Free Tier)** | **MongoDB** |

---

## 2. MARCO LEGAL Y SEGURIDAD ÉTICA ← LEER SIEMPRE PRIMERO

### ¿Qué está permitido?

El programa MongoDB en HackerOne dice explícitamente:

- ✅ Usar **tus propias cuentas** de MongoDB Atlas Free Tier para pruebas
- ✅ Crear **múltiples cuentas** para pruebas de IDOR entre ellas (esto es la forma CORRECTA y segura)
- ✅ Interceptar y repetir requests con Burp Suite sobre tus propias cuentas
- ✅ Reportar si descubres que podés acceder a datos de **otras** cuentas (pero solo por accidente, no por fuerza bruta)

### ¿Qué NO está permitido?

- ❌ **NO** acceder, leer ni modificar datos de cuentas que no sean tuyas
- ❌ **NO** adivinar o enumerar IDs al azar esperando dar con cuentas ajenas (bruteforce de IDs)
- ❌ **NO** usar escáneres automáticos (Nikto, nuclei, sqlmap, etc.)
- ❌ **NO** hacer pruebas de carga/DoS
- ❌ **NO** acceder a `feedback.mongodb.com` ni `learn.mongodb.com` (fuera de scope)

### La regla de oro para IDOR (la más importante)

> **Siempre se prueban IDORs entre DOS CUENTAS TUYAS.**
> Cuenta A intenta acceder a recursos de Cuenta B.
> Si puede verlos → bug reportable. Si no puede → control correcto.
> Nunca se prueba con cuentas de terceros desconocidos.

---

## 3. SETUP REQUERIDO: SEGUNDA CUENTA DE MONGODB

**¿Por qué necesitamos una segunda cuenta?**
Para probar IDOR (acceso no autorizado entre usuarios), necesitamos DOS cuentas. La Cuenta A intenta ver los datos de la Cuenta B. Si lo logra sin permiso → hay un bug. Sin segunda cuenta, no podemos demostrar el bug de forma ética ni legal.

### Paso a paso para crear la segunda cuenta

1. **Abrir una pestaña de incógnito** en el navegador (para no mezclar sesiones)
2. Ir a `https://account.mongodb.com/account/register`
3. Registrarse con tu **segunda dirección de email** (la que mencionaste)
4. Verificar el email
5. Crear un proyecto nuevo en MongoDB Atlas Free Tier
6. **Anotar los siguientes datos de la segunda cuenta:**

```
CUENTA B (segunda cuenta - víctima en las pruebas):
  Email:              tomasreis44@gmail.com
  OrgId:              6a4d7d849d5dcab6abad6820
  ProjectId:          6a4d7d849d5dcab6abad6845
  DatabaseName:       sample_mflix
  DatabaseUser:       victima
  DatabasePassword:   1213
  QueryFederationURL: mongodb://victima:1213@atlas-sql-6a4d7e55fb12fd51fb6d9572-5dxlth.a.query.mongodb.net/sample_mflix?ssl=true&authSource=admin
```

**¿Cómo encontrar el OrgId y ProjectId?**
- Logueate como Cuenta B en MongoDB Atlas
- Ir a tu proyecto → la URL será algo como: `https://cloud.mongodb.com/v2/6a4c0a54b388b65b11799a24#/clusters`
- El número de 24 caracteres en la URL **ES** tu ProjectId/OrgId
- También está en: Settings → Organization Settings → Organization ID

### ¿Qué es un ObjectId / hex ID de 24 caracteres?

MongoDB usa identificadores únicos de 24 caracteres hexadecimales (letras a-f y números 0-9). Ejemplo: `6a4c0a54b388b65b11799a24`. Los primeros 8 caracteres son un timestamp Unix — por eso dos cuentas creadas en momentos similares tendrán IDs parecidos, pero **no hacemos bruteforce de esto**. Lo que hacemos es tomar el ID real de nuestra Cuenta B y usarlo como "víctima conocida".

---

## 4. CONFIGURACIÓN BURP SUITE

### Header requerido por MongoDB (obligatorio en todos los requests)
```http
X-HackerOne-Research: tomas244
```

### Regla en Burp → Proxy → Settings → Match and Replace
- **Type:** `Request header`
- **Match:** (vacío)
- **Replace:** `X-HackerOne-Research: tomas244`

### Scope en Burp
Agregar estos dominios al scope (Use Advanced Scope Control):
- `cloud.mongodb.com`
- `account.mongodb.com`

---

## 5. RESULTADOS DEL ANÁLISIS DE TRÁFICO (2026-07-07)

El script `parseador_burp.py` procesó 59 MB de tráfico capturado con iterparse (sin saturar RAM).

| Métrica | Valor |
|---|---|
| Total requests | 10.007 |
| En scope `*.mongodb.com` | 10.006 |
| Endpoints únicos normalizados | 171 |
| APIs con respuesta JSON 200/201 | 8.662 |
| Requests con status anómalo | 18 |
| Configuraciones CORS con credenciales | 10 |

**Archivos generados por el parser:**
- `LAB/api/burp_analisis.json` — datos completos estructurados
- `LAB/api/burp_resumen.txt` — resumen legible

---

## 6. VECTORES DE ATAQUE — PLAYBOOKS DETALLADOS

> Para cada vector: instrucciones paso a paso en Burp, qué buscar en la respuesta, y cómo decirle a PEGASO que te ayude a documentarlo.

---

### VECTOR 1 🔴 — IDOR en Gestión de Usuarios de Cluster

**Qué es:** El endpoint `/nds/{projectId}/users` permite listar y crear usuarios de base de datos dentro de un cluster. Si el servidor no valida que el `projectId` en la URL pertenece a tu sesión, un usuario A podría ver o crear usuarios en el cluster de B.

**Por qué es prioritario:** Es el vector más clásico de IDOR en plataformas cloud. MongoDB gestiona miles de clusters de clientes. Si existe, es crítico (P1/P2 = $500–$5000).

**Prerequisito:** Tener la segunda cuenta (Cuenta B) con su ProjectId anotado.

#### Paso a paso en Burp Suite

1. **Loguearte como Cuenta A** (tu cuenta principal: `tomas244@wearehackerone.com`)
2. En Burp → **Proxy → HTTP History**
3. Buscar un request que diga `GET /nds/6a4c.../users` (tu ProjectId)
4. Click derecho → **Send to Repeater** (Ctrl+R)
5. En el panel Repeater, verás algo así:
   ```http
   GET /nds/6a4c0a54b388b65b11799a58/users HTTP/2
   Host: cloud.mongodb.com
   Cookie: [tus cookies de sesión de Cuenta A]
   ```
6. **Modificar el ProjectId** en la URL: reemplazá `6a4c0a54b388b65b11799a58` por el ProjectId de la Cuenta B
7. Click **Send**

#### Qué buscar en la respuesta

| Respuesta | Significado | Acción |
|---|---|---|
| `403 Forbidden` o `401` | El servidor validó correctamente. No hay bug. | Documentar como "control correcto". |
| `200 OK` con lista de usuarios | **BUG CONFIRMADO** — IDOR crítico | Hacer screenshot, guardar request/response completo, reportar |
| `404 Not Found` | El ProjectId de Cuenta B no existe o no es accesible. Puede ser control correcto o enumeración. | Probar con ProjectId verificado de Cuenta B. |
| `200 OK` con lista vacía `[]` | Ambiguo. Puede ser que Cuenta B no tenga usuarios o puede ser control correcto. | Primero crear un usuario en Cuenta B, luego repetir. |

#### Probar también el POST (creación de usuario)

Repetir los pasos pero con un request `POST /nds/{projectId_de_B}/users`:
```json
{"username": "test_idor", "password": "Test1234!", "roles": [{"roleName": "readAnyDatabase", "databaseName": "admin"}]}
```
Si devuelve `201 Created` → **crítico**: podés crear usuarios en clusters ajenos.

#### Prompt para PEGASO CLI (copiar y pegar en tu terminal)
```
Ejecuta: python3 /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/pegaso.py

Luego escribile esto:
"Ayudame a documentar un posible IDOR en MongoDB Atlas.
El endpoint es GET /nds/{projectId}/users.
Probé acceder con mi sesión de Cuenta A al ProjectId de Cuenta B.
La respuesta fue: [PEGA AQUÍ LA RESPUESTA DE BURP].
Evaluá la severidad según el programa de MongoDB en HackerOne y redactá un borrador de reporte."
```

---

### VECTOR 2 🔴 — CORS con Credenciales (Cross-Origin Resource Sharing)

**Qué es:** Cuando un navegador hace un request desde el sitio web A hacia el sitio web B, el servidor B puede autorizar eso con cabeceras CORS. El problema es que varios endpoints de MongoDB responden con `Access-Control-Allow-Credentials: true`, que significa que el navegador incluirá las cookies de sesión en ese request cross-origin.

**En términos simples:** Si hay un XSS (inyección de JavaScript) en cualquier subdominio de `mongodb.com`, esa vulnerabilidad combinada con el CORS permisivo se convierte automáticamente en robo de sesión completo.

**Endpoints detectados con CORS + credenciales:**
```
cloud.mongodb.com/user/logout          → ACAO: https://account.mongodb.com, ACAC: true
cloud.mongodb.com/user/shared          → ACAO: https://www.mongodb.com, ACAC: true
cloud.mongodb.com/ui/layout            → ACAO: https://account.mongodb.com, ACAC: true
account.mongodb.com/account/profile/userAuid → ACAO: https://cloud.mongodb.com, ACAC: true
```

**El único caso donde es bug reportable por sí solo (sin XSS):** Cuando el servidor refleja el `Origin` del request en el `Access-Control-Allow-Origin` de la respuesta — es decir, acepta cualquier dominio que le pidas. Eso se llama "CORS misconfiguration" y es reportable directamente.

#### Paso a paso en Burp Suite

1. Ir a **HTTP History** → buscar `GET /ui/layout` o `GET /user/shared`
2. **Send to Repeater**
3. En el Repeater, agregar este header al request:
   ```http
   Origin: https://evil.mongodb.com
   ```
4. Click **Send** y mirar la respuesta

#### Qué buscar en la respuesta

| Respuesta | Significado | Acción |
|---|---|---|
| `Access-Control-Allow-Origin: https://evil.mongodb.com` | **BUG** — El servidor refleja el Origin. | Reportar como CORS Misconfiguration. |
| `Access-Control-Allow-Origin: https://account.mongodb.com` | Control correcto (dominio fijo, no refleja). | No es bug en ese endpoint. |
| Sin cabecera `Access-Control-Allow-Origin` | No aplica CORS aquí. | No es bug. |

5. Probar también con `Origin: null`:
   ```http
   Origin: null
   ```
   Si devuelve `Access-Control-Allow-Origin: null` con `Access-Control-Allow-Credentials: true` → **bug crítico** (explotable desde iframes sandbox).

#### Prompt para PEGASO CLI
```
En PEGASO escribí:
"Encontré un posible CORS misconfiguration en MongoDB Atlas.
Endpoint: GET /ui/layout en cloud.mongodb.com
Envié Origin: https://evil.mongodb.com
La respuesta fue: [PEGA LA RESPUESTA COMPLETA].
¿Es esto un bug reportable? ¿Qué severidad tendría y cómo lo exploto en un PoC?"
```

---

### VECTOR 3 🟠 — IDOR en Endpoint Raíz del Cluster `/nds/{objectId}`

**Qué es:** Este es el endpoint que devuelve toda la información de configuración de un cluster de MongoDB Atlas. En nuestro tráfico apareció **6.393 veces** — es el polling principal del dashboard. Si el `{objectId}` no valida ownership, alguien puede leer la configuración de clusters ajenos.

**Información que devuelve este endpoint:** Nombre del cluster, región, proveedor de cloud (AWS/Azure/GCP), configuración de networking, estado, backups, etc.

#### Paso a paso en Burp Suite

Misma mecánica que Vector 1, pero con este endpoint:

1. Buscar `GET /nds/6a4c...` en History → Send to Repeater
2. Reemplazar el ObjectId por el ProjectId de tu Cuenta B
3. Enviar y analizar respuesta
4. También probar: `GET /nds/{projectId_B}/clusters` y `GET /nds/{projectId_B}/ipWhitelist`

#### Qué buscar

| Respuesta | Significado |
|---|---|
| `403` con tu ProjectId B real | Control correcto |
| `200` con datos del cluster de Cuenta B | **IDOR** — reportar |
| `404` | Puede ser que el cluster no exista en Cuenta B. Creá un cluster Free Tier en Cuenta B primero. |

---

### VECTOR 4 🟠 — Oracle de Enumeración en `/billing/`

**Qué es:** Dos endpoints de billing devolvieron `404` en nuestro tráfico. Un "oracle de enumeración" significa que el servidor te da pistas sobre si un recurso existe o no, aunque no te deje acceder. Si el mensaje de error es diferente para "no existe" vs "existe pero no tenés permiso", un atacante puede enumerar organizaciones válidas.

**Endpoints detectados:**
```
GET /billing/payingOrg/{orgId}                              → 404
GET /billing/orgs/{orgId}/projectLevelSupportActiveDate     → 404
```

#### Paso a paso

1. Buscar estos requests en Burp History → Send to Repeater
2. Probar con **tu propio OrgId** (debería dar algo diferente al 404)
3. Probar con el **OrgId de Cuenta B**
4. Probar con un **OrgId inventado** (ej: `000000000000000000000000`)
5. Comparar los 3 mensajes de error

#### Qué buscar

| Comparación | Significado |
|---|---|
| Los 3 dan exactamente el mismo error `{"errorCode": "ORG_NOT_FOUND"}` | No hay oracle. Control correcto. |
| Propio OrgId da `{"errorCode": "PAYMENT_METHOD_REQUIRED"}` y OrgId ajeno da `{"errorCode": "UNAUTHORIZED"}` | **Oracle de enumeración** — se puede saber si un OrgId existe o no. Reportar como Information Disclosure. |
| OrgId ajeno da `200` con datos de billing de otra org | **IDOR crítico en billing**. Reportar urgente. |

---

### VECTOR 5 🟡 — AI API Keys de Otros Proyectos

**Qué es:** MongoDB Atlas tiene una integración con modelos de IA (MongoDB AI / Atlas Vector Search). El endpoint `/aiModelApi/{objectId}/apiKeys/project/{objectId}` devuelve las API keys de IA configuradas para un proyecto.

**Endpoint detectado (6 hits, todos 200):**
```
GET /aiModelApi/{orgId}/apiKeys/project/{projectId}
```

#### Paso a paso

1. Buscar `aiModelApi` en Burp History → Send to Repeater
2. Tenés dos ObjectIds en la URL: el primero es probablemente el OrgId, el segundo el ProjectId
3. Probar reemplazando el ProjectId por el de tu Cuenta B
4. Si la Cuenta B no tiene API keys de IA configuradas, el test no es concluyente → primero configurar una API key en Cuenta B, luego repetir el test desde Cuenta A

#### Qué buscar

| Respuesta | Significado |
|---|---|
| `403` | Control correcto |
| `200` con API keys del proyecto B | **IDOR — disclosure de credentials** — alta severidad |

---

### VECTOR 6 🟡 — /user/authCodeCreationTimestamp (Responde 400 a CORS preflight)

**Qué es:** Este endpoint recibe requests con cabeceras CORS (OPTIONS y GET) pero devolvió un `400 Bad Request` cuando se le hizo el GET. Esto es inusual — normalmente un endpoint de solo lectura no debería dar 400 si no se le mandan datos malformados.

**Por qué importa:** Un `400` en un endpoint GET puede indicar que el servidor es sensible a ciertos parámetros del request. Vale la pena investigar si es manipulable.

#### Paso a paso

1. Buscar `authCodeCreationTimestamp` en Burp History
2. Ver exactamente qué request dio 400 (revisar las cabeceras completas)
3. En Repeater: quitar las cabeceras de a una por vez hasta aislar cuál causa el 400
4. Probar agregar/quitar el header `Origin`, cambiar el método (GET → POST → DELETE)

---

## 7. FLUJO DE TRABAJO CON PEGASO CLI

### Rol de PEGASO en las pruebas

PEGASO (`./run` en el directorio `LAB/api/`) actúa como tu copiloto técnico para:
- **Documentar hallazgos**: describís lo que encontraste, él redacta el borrador del reporte
- **Auditar git**: verificar qué cambios hay pendientes de commitear
- **Analizar respuestas**: le pegás la respuesta de Burp y te dice si es bug o no
- **Generar commits**: le pedís que commitee el trabajo del día

### Comandos de uso diario

**Iniciar PEGASO:**
```bash
cd /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api
./run
```

**Pedirle que audite el estado del proyecto:**
```
[Tú]> Auditá el estado del laboratorio: revisá git status en /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB y dame un resumen de qué archivos cambiaron hoy.
```

**Pedirle que commitee al final de una sesión:**
```
[Tú]> Hacé un git add y commit en /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB con el mensaje "Sesión 2026-07-07: análisis tráfico Burp + playbooks de ataque MongoDB". Verificá antes que no haya credenciales en los archivos.
```

**Pedirle que evalúe un hallazgo:**
```
[Tú]> Encontré esto en Burp. ¿Es reportable como bug de MongoDB en HackerOne?
Request: GET /nds/[ID_AJENO]/users HTTP/2
Response: 200 OK
Body: [{"username": "user_de_cuenta_b", ...}]
```

---

## 8. CONCEPTOS TÉCNICOS BÁSICOS (glosario)

| Término | Explicación simple |
|---|---|
| **ObjectId** | ID único de 24 letras/números hex que MongoDB usa para identificar recursos (orgs, proyectos, clusters). Ej: `6a4c0a54b388b65b11799a24` |
| **IDOR** | Insecure Direct Object Reference. Bug donde cambiás un ID en la URL y podés ver datos de otro usuario. |
| **CORS** | Mecanismo del navegador que controla qué sitios pueden hacer requests a otros. |
| **ACAC** | `Access-Control-Allow-Credentials: true` — permite que cookies viajen en requests cross-origin. |
| **Burp Repeater** | Herramienta de Burp Suite para modificar y reenviar requests manualmente. |
| **OrgId / GroupId / ProjectId** | En MongoDB Atlas son sinónimos según el contexto. El ID de tu "proyecto" o "grupo" dentro de una organización. |
| **Federation / SSO** | Sistema que permite que una empresa use sus propias cuentas corporativas (Active Directory, Okta) para loguearse en MongoDB. No aplica para cuentas Free Tier individuales. Ignorar este vector por ahora. |
| **Oracle de enumeración** | El servidor te dice si un recurso existe aunque no te deje acceder — eso es información que no debería revelar. |

---

## 9. PLAN DE ACCIÓN

### Sesión actual (completada ✅)
- [x] Capturar tráfico de navegación normal en MongoDB Atlas
- [x] Crear y ejecutar `parseador_burp.py` — 10.007 requests procesados
- [x] Identificar 171 endpoints únicos y 5 vectores de ataque

### Sesión de Pruebas (Completada ✅)
- [x] **Paso 1:** Crear segunda cuenta MongoDB Atlas con tu segundo email
- [x] **Paso 2:** Anotar OrgId y ProjectId de la segunda cuenta
- [x] **Paso 3:** En Burp Repeater: probar Vector 1 y Vector 3 (`/nds/{projectId}`) con el ProjectId de Cuenta B
- [x] **Paso 4:** Documentar resultado IDOR (303 Redirección = Control Correcto. Mitigado).
- [x] **Paso 5:** Probar Vector 2 (CORS Misconfiguration) inyectando `Origin: https://evil.mongodb.com` en `/ui/layout`.
- [x] **Paso 6:** Documentar resultado CORS (El servidor no refleja el origen malicioso = Control Seguro. Mitigado).

### Próxima sesión (Pendiente)
- [ ] Mapear los vectores restantes (Vector 4, 5 y 6) capturando tráfico nuevo y repitiendo la metodología de Repeater.

### Regla de sesión
**Una sesión = un vector probado = un resultado documentado.**
No pasar al Vector 2 sin terminar el Vector 1.

---

## 10. TRAMPAS CRÍTICAS (no hacer nunca)

- ❌ No usar escáneres automáticos (Nikto, nuclei, sqlmap)
- ❌ No hacer bruteforce de IDs desconocidos — solo usar IDs de tus propias cuentas
- ❌ No testear `feedback.mongodb.com`, `learn.mongodb.com`, `inm.mongodb.com`
- ❌ No hacer más de 10 requests manuales por minuto al mismo endpoint
- ❌ No guardar ni distribuir datos de otras cuentas si los encontrás accidentalmente

---

## 1. COMPARATIVA RÁPIDA: MONGODB vs. MEESHO

| Característica | Meesho | MongoDB | Veredicto / Ventaja |
| :--- | :--- | :--- | :--- |
| **Tiempo de Respuesta** | ~22 horas | **1 hora** | **MongoDB** (Soporte ultra rápido) |
| **Pago Mínimo (Low)** | $50 | **$100** | **MongoDB** (Paga el doble) |
| **Pago Promedio (Medium)**| $308 | **$500** | **MongoDB** (Mejores recompensas) |
| **Riesgo de Geobloqueo** | 🔴 Muy Alto (India) | 🟢 **Muy Bajo** (Global) | **MongoDB** (Usa WAF global para desarrolladores) |
| **Entorno de Pruebas** | Cuentas compartidas | **Cuentas propias (Free Tier)**| **MongoDB** (Mayor control sin interferencia) |
| **Header de Seguridad** | `X-Hackerone` | `X-HackerOne-Research` | **Ambos** (Requieren configuración en Burp) |

---

## 2. ESTRUCTURA Y ACTIVOS CLAVE EN SCOPE

MongoDB es un gigante de software, por lo que su alcance es muy amplio. Estos son los mejores activos para comenzar sin configuraciones complejas:

1. **MongoDB Atlas (Free Tier):**
   * **Qué es:** La plataforma de bases de datos cloud de MongoDB.
   * **Elegibilidad:** Las cuentas creadas en el nivel gratuito (Free Tier) son elegibles para recompensa.
   * **Regla de Registro:** Obligatorio registrarse usando el correo alias de HackerOne: `tomas244@wearehackerone.com`.

2. **Atlas IAM (`account.mongodb.com`):**
   * **Qué es:** El sistema de gestión de identidades y accesos (login, organizaciones, permisos).
   * **Interés:** Ideal para buscar fallos de control de acceso (IDOR, escalación de privilegios entre organizaciones de prueba).

3. **Dominios y Subdominios (`*.mongodb.com/*`):**
   * Incluye la documentación, soporte y páginas principales.
   * *Exclusión:* `feedback.mongodb.com` e `inm.mongodb.com` (terceros) están fuera de alcance.

---

## 3. CONFIGURACIÓN DEL ENTORNO LOCAL (BURP SUITE)

Para testear MongoDB de forma segura y autorizada, debemos modificar la regla de Burp Suite que creamos para Meesho.

### 3.1 Header Requerido por MongoDB
El programa solicita el siguiente header:
```http
X-HackerOne-Research: tomas244
```

### 3.2 Modificar la regla de "Match and Replace" en Burp
Para no enviar el header de Meesho a MongoDB, edita la regla en Burp Suite:
1. Ir a **Proxy** → **Proxy settings** → **Match and replace rules**.
2. Modifica la regla anterior (o añade una nueva y desactiva la de Meesho):
   * **Type:** `Request header`
   * **Match:** (dejar vacío)
   * **Replace:** `X-HackerOne-Research: tomas244`
   * **Comment:** `Header obligatorio MongoDB`

---

## 4. ESTRATEGIA DE PRUEBAS SIN RIESGO DE BLOQUEO

A diferencia de Meesho, MongoDB no bloquea por defecto las IPs residenciales de LATAM porque sus clientes son desarrolladores de todo el mundo.

1. **Navegación normal:** Intenta entrar directamente a `https://cloud.mongodb.com` sin VPN. Debería cargar al instante.
2. **Si hay WAF:** Si eventualmente experimentas bloqueos (muy poco probable), puedes reactivar el túnel SSH a tu OCI en Ashburn ya que las IPs de Oracle Cloud están permitidas en los servicios de MongoDB Atlas (muchos desarrolladores usan OCI para conectarse a MongoDB Atlas).

---

## 5. TRAMPAS CRÍTICAS ESPECÍFICAS DE MONGODB

*   ❌ **No usar escáneres automáticos:** El programa indica explícitamente que los escáneres suelen saturar sus sistemas y no generan reportes elegibles.
*   ❌ **Evitar DoS y pruebas de estrés:** No intentes tirar la base de datos ni saturar los endpoints de login (el OOM - Out of Memory autenticado se paga muy bajo).
*   ❌ **Learn.mongodb.com y feedback.mongodb.com:** Están gestionados por terceros. Reportar ahí = Reporte Inelegible.

---

## 6. PLAN DE ACCIÓN RECOMENDADO

### Sesión A (Esta sesión) — Validación y Registro
* [x] Analizar y comparar el programa de MongoDB.
* [x] Confirmar ausencia de bloqueos iniciales en la plataforma.
* [ ] Crear una cuenta en **MongoDB Atlas Free Tier** usando el alias `tomas244@wearehackerone.com`.

### Sesión B (Próxima sesión) — Mapeo de Atlas IAM
* [ ] Configurar el Scope en Burp Suite para: `account.mongodb.com` y `cloud.mongodb.com`.
* [ ] Activar la regla `X-HackerOne-Research: tomas244` en Burp.
* [ ] Capturar el flujo de creación de organización, invitación de usuarios y cambio de roles para buscar IDORs.
