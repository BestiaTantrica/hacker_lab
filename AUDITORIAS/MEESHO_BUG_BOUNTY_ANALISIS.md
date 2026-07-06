# 🔍 ANÁLISIS COMPLETO: PROGRAMA BUG BOUNTY — MEESHO (HackerOne)

> **Estado:** Análisis realizado el 2026-07-06  
> **Propósito:** Verificar si el laboratorio actual está listo para operar en este programa  
> **Nivel de riesgo reputacional:** ALTO si se procede sin leer esto completo

---

## ⚠️ VEREDICTO INICIAL (leer antes que nada)

> [!CAUTION]
> **Este programa tiene restricciones severas que la mayoría de principiantes ignora y que destruyen su reputación antes de empezar.** Leer la sección de "Trampas críticas para novatos" antes de abrir cualquier herramienta.

**Conclusión general:** El programa ES viable como primer objetivo, pero requiere preparación específica. El laboratorio actual cubre el 40% de lo necesario. El 60% restante son conocimientos y procesos manuales que deben adquirirse.

---

## 1. IDENTIDAD EN HACKERONE — VERIFICAR ANTES DE TODO

**Problema identificado:** No sabes con certeza si tu usuario es `Tomas2` o `tomas244`.

**Impacto de no saberlo:** Existe una regla crítica en el programa:
> *"Incluya el siguiente encabezado HTTP en todas las solicitudes de prueba: `X-Hackerone: <h1-username>`"*

Si envías el header con el usuario incorrecto, el equipo de Meesho puede:
- Rechazar el reporte por no seguir las instrucciones del programa
- No asociar las pruebas a tu cuenta
- Marcar tu cuenta como sospechosa

**Acción obligatoria ANTES de cualquier prueba:**
1. Ir a: https://hackerone.com/settings/profile (ya logueado)
2. Tu username exacto aparece en la URL del perfil o en el campo "Username"
3. Anotarlo: `X-Hackerone: TU_USERNAME_EXACTO`
4. Ese string se incluirá en CADA petición HTTP que hagas a Meesho durante las pruebas

---

## 2. ESTRUCTURA DEL PROGRAMA — MAPA COMPLETO

### 2.1 Tipo de programa
- **Plataforma:** HackerOne
- **Tipo de scope:** CERRADO (solo acepta reportes dentro del scope definido)
- **Pago:** Garantizado en máximo 1 mes desde recepción del reporte
- **Comunicación:** SOLO a través de HackerOne. Nunca por email directo, redes sociales, ni WhatsApp.

### 2.2 Activos EN scope (donde PUEDES probar)

| Activo | URL/Descripción | Tipo | Credenciales disponibles |
|--------|----------------|------|--------------------------|
| **Web Meesho** | meesho.com | Web/Plataforma | Número 6666666661 / OTP 999999 |
| **App Android Meesho** | Play Store | Móvil (solo análisis estático) | Número 6666666661 / OTP 999999 |
| **App iOS Meesho** | App Store | Móvil (solo análisis estático) | Número 6666666661 / OTP 999999 |
| **Valmo Mobile** | App móvil | Móvil (solo análisis estático) | Número 6666666661 / OTP 999999 |
| **Panel de Proveedores** | supplier.meesho.com | Web/Plataforma | suppliertest-1@meeshoai.com / Hackerone @123 $ |

> [!IMPORTANT]
> **Las aplicaciones móviles SOLO aceptan análisis estático (reversing del APK/IPA).** No puedes reportar vulnerabilidades encontradas en el tráfico de red de las apps o en su comportamiento en tiempo de ejecución.

### 2.3 Activos FUERA de scope (donde NO puedes probar aunque los encuentres)
- Cualquier dominio no listado arriba
- Sistemas de terceros (pasarelas de pago, analytics, atención al cliente)
- Paneles de administración internos
- Sistemas de empleados
- Afiliadas y empresas del grupo que no estén explícitamente mencionadas

---

## 3. TABLA DE RECOMPENSAS — QUÉ PUEDES GANAR

### 3.1 Rangos por categoría

| Categoría | Bajo | Medio | Alto | Crítico |
|-----------|------|-------|------|---------|
| **Apps Móviles** (solo análisis estático) | $100–$250 | $250–$800 | $800–$1,700 | $1,700–$2,500 |
| **Web y Plataforma** | $50–$150 | $150–$600 | $600–$1,200 | $1,200–$2,000 |

### 3.2 Cómo se determina la severidad
- Meesho usa **CVSS (Common Vulnerability Scoring System)**
- El equipo de seguridad de Meesho asigna el score CVSS, no tú
- La recompensa se calcula sobre ese score exacto
- **La decisión final de recompensa es DISCRECIONAL del equipo de Meesho**

### 3.3 Estadísticas reales del programa (datos públicos)
| Métrica | Valor |
|---------|-------|
| Recompensa promedio (Bajo) | $96 |
| Recompensa promedio (Medio) | $308 |
| Tiempo hasta primera respuesta | ~22 horas |
| Tiempo hasta triage | ~4 días |
| Tiempo hasta recompensa | ~1.5 semanas |
| Tiempo total hasta resolución | ~1 mes y 3 semanas |

> [!NOTE]
> El 45.83% de los reportes reciben recompensa en nivel bajo, el 29.17% en nivel medio. El ~25% restante no recibe recompensa (fuera de scope, duplicado, informativo). Esto es normal.

---

## 4. CREDENCIALES DE PRUEBA — CÓMO USARLAS

### 4.1 Para apps de consumo (Meesho Web, Android, iOS, Valmo)
```
Número de móvil 1: 6666666661
Número de móvil 2: 6666666662
OTP (ambos): 999999
Nota: Si el OTP falla, tocar "Reenviar" e ingresar 999999 de nuevo
```

### 4.2 Para panel de proveedores (supplier.meesho.com)
```
Usuario 1: suppliertest-1@meeshoai.com
Usuario 2: suppliertest-2@meeshoai.com
Contraseña: Hackerone @123 $
```

### 4.3 Reglas de uso de credenciales (CRÍTICAS)
- ❌ NO cambiar contraseñas ni emails de estas cuentas
- ❌ NO cambiar configuración de seguridad
- ❌ NO realizar transacciones financieras reales
- ❌ NO acceder a datos de usuarios reales
- ❌ NO bloquear, suspender ni escalar privilegios
- ❌ NO compartir estas credenciales con nadie
- ✅ Usar una cuenta por vez para pruebas normales
- ✅ Usar las dos cuentas solo para pruebas que requieren interacción entre usuarios

### 4.4 Header HTTP obligatorio en TODAS las peticiones
```http
X-Hackerone: TU_USERNAME_EXACTO
```
Este header se incluye en cada request que hagas mientras pruebas. En Burp Suite se configura como header global en el proxy (Proxy > Options > Match and Replace).

---

## 5. QUÉ VULNERABILIDADES TIENEN POSIBILIDAD REAL DE PAGO

### 5.1 VIABLE en web (meesho.com y supplier.meesho.com)

| Vulnerabilidad | Probabilidad de pago | Dificultad para novato |
|---|---|---|
| IDOR con impacto real (acceder datos de otro usuario) | Alta | Media |
| XSS almacenado con impacto real (no auto-XSS) | Alta | Media |
| SQL Injection | Alta | Alta |
| SSRF con exfiltración | Alta | Alta |
| Broken Access Control (acceder a funciones de admin) | Alta | Media |
| Business Logic Flaws (descuentos, precios, cupones, flujos de pago) | Media | **Baja** ← empezar aquí |
| Subdomain Takeover (si el pipeline detecta uno válido) | Alta | Baja-Media |

### 5.2 EXPLÍCITAMENTE RECHAZADO (no perder tiempo)

> [!WARNING]
> Reportar estas vulnerabilidades destruye tu ratio de señal/ruido en HackerOne. Un ratio bajo te bloquea el acceso a programas privados de mayor pago.

- Rate limiting sin proof of concept de abuso real
- Clickjacking
- CSRF en login/logout/acciones no autenticadas
- Auto-XSS (XSS que solo afecta a tu propia sesión)
- Open redirect sin cadena de ataque demostrada
- Headers de seguridad faltantes (CSP, HSTS, X-Frame-Options)
- SSL/TLS warnings
- Enumeración de usuarios por registro/login
- SPF/DKIM/DMARC sin email spoofing demostrado en proveedor real
- Certificate pinning faltante
- Datos en texto claro cuando el tráfico va por TLS
- Secretos en APK sin impacto demostrado
- Vulnerabilidades que requieren acceso físico al dispositivo
- CORS mal configurado sin impacto demostrado
- DoS/DDoS

### 5.3 YA CONOCIDOS — Reportar esto = cierre inmediato como duplicado
El programa lista estos issues como conocidos (Known Issues):
1. Inyección de HTML en módulo de tickets en supplier.meesho.com
2. Problemas de eliminación de cuentas con abuso de descuento primer pedido
3. XSS almacenado via carga de archivos en supplier.meesho.com
4. Omisión de OTP en actualización de datos bancarios en supplier.meesho.com
5. Omisión de OTP de datos bancarios/UPI en apps móviles de Meesho

---

## 6. PROCESO COMPLETO DE REPORTE — PASO A PASO

### 6.1 Antes de empezar a probar
1. Confirmar username exacto de HackerOne (ver sección 1)
2. Instalar Burp Suite Community (portswigger.net/burp/communitydownload — gratis)
3. Configurar Burp como proxy del navegador
4. Agregar header `X-Hackerone: TU_USERNAME` como header global en Burp (Proxy > Options > Match and Replace)
5. Registrarse en Meesho usando `TU_USERNAME@wearehackerone.com` (para crear cuenta propia si lo necesitas)
6. Para registro por teléfono: usar el número de prueba 6666666661 con OTP 999999

### 6.2 Durante las pruebas
- Documentar CADA paso (capturas de pantalla, requests en Burp)
- Guardar el request completo (con headers) y la response completa
- **NO explotar** más allá de lo necesario para demostrar el impacto
- Si encuentras acceso admin o RCE: PARAR y reportar de inmediato
- NO almacenar datos de usuarios reales más de lo estrictamente necesario
- Borrar cualquier dato de usuario real después de reportar

### 6.3 Estructura de un reporte válido — Plantilla

```
TÍTULO: [Tipo de vuln] en [endpoint/función] permite [impacto específico]
Ejemplo: "IDOR en /api/v1/orders/{id} permite ver pedidos de cualquier usuario"

═══════════════════════════════════════════

DESCRIPCIÓN DEL PROBLEMA
[Qué es la vulnerabilidad, por qué es un riesgo, qué datos/sistemas afecta]

═══════════════════════════════════════════

IMPACTO
[Qué puede hacer un atacante real. Ser concreto:
"Un atacante autenticado puede acceder a los datos de pedido de cualquier otro usuario,
incluyendo nombre, dirección de entrega y datos de pago parciales"]

═══════════════════════════════════════════

PASOS PARA REPRODUCIR

1. Iniciar sesión en supplier.meesho.com con suppliertest-1@meeshoai.com
2. Navegar a [URL exacta]
3. Interceptar el request con Burp Suite
4. Observar el parámetro [X] con el valor [A] (pertenece a la cuenta 1)
5. Modificar el valor [A] por [B] (pertenece a la cuenta 2)
6. Reenviar el request
7. Observar que la response contiene datos de la cuenta 2

═══════════════════════════════════════════

PRUEBA DE CONCEPTO (PoC)

[Capturas de pantalla numeradas de cada paso]
[Request HTTP completo — con el header X-Hackerone visible]
[Response HTTP completa]
[Video si el ataque es complejo de seguir en imágenes]

Request de ejemplo:
GET /api/v1/orders/12345 HTTP/1.1
Host: meesho.com
X-Hackerone: TU_USERNAME
Authorization: Bearer [token_cuenta_1]
...

Response (contiene datos de otra cuenta):
{"order_id": "12345", "user_name": "otro_usuario", ...}

═══════════════════════════════════════════

SEVERIDAD PROPUESTA: Medium (CVSS ~5.5)
Justificación: Afecta confidencialidad de datos de usuarios. No requiere privilegios especiales.
No permite modificación ni elevación de privilegios.

═══════════════════════════════════════════

REMEDIACIÓN RECOMENDADA
Verificar en el backend que el order_id solicitado pertenece al usuario autenticado
antes de devolver los datos. Implementar control de acceso basado en propiedad del recurso.
```

### 6.4 Después de enviar el reporte
- Primera respuesta: ~22 horas
- Triage: ~4 días
- Si aceptan y asignan recompensa: el pago llega en ~1.5 semanas
- Si rechazan: NO argumentar agresivamente. Pedir aclaración educadamente si hay duda legítima.
- **NUNCA divulgar públicamente** el hallazgo sin autorización escrita de Meesho

---

## 7. PROCESO DE COBRO — DESDE EL REPORTE HASTA EL DINERO

### 7.1 Configurar pago ANTES del primer reporte
URL: https://hackerone.com/settings/payment_preferences

| Método | Disponibilidad | Comisión |
|--------|---------------|---------|
| PayPal | Global | ~2-5% |
| Bank Transfer (SWIFT) | Global | Varía por banco |
| Bitcoin | Global | Baja |
| Gift Cards | Algunos países | 0% |

> [!IMPORTANT]
> Configurar el método de pago ANTES de enviar reportes. Si llega una recompensa sin método configurado, el dinero queda en espera en HackerOne hasta que lo configures. No se pierde, pero hay que completar los datos.

### 7.2 Flujo de pago
```
1. Reporte enviado en HackerOne
        ↓
2. Triage por equipo de Meesho (~4 días)
        ↓
3. Aceptado como válido
        ↓
4. Meesho asigna severidad y monto
        ↓
5. Meesho paga a HackerOne
        ↓
6. HackerOne transfiere al método configurado
        ↓ (~1.5 semanas desde aceptación)
7. Dinero en tu cuenta
```

### 7.3 Posible solicitud de documentación
El programa advierte que puede solicitar información de identificación o pago para cumplir con requisitos legales. Tener disponible:
- Identificación oficial
- Información fiscal local si es requerida

### 7.4 Impuestos
El ingreso de bug bounty se declara como trabajo independiente. Consultar contador local sobre la forma correcta de declararlo en Argentina.

---

## 8. RESTRICCIONES LEGALES IMPORTANTES

- **Jurisdicción:** Ley de la India, tribunales de Bangalore. Si hay conflicto legal, se resuelve allí.
- **Argentina:** No está en lista de países sancionados → Puedes participar sin restricción.
- **Confidencialidad:** PERMANENTE hasta autorización escrita de Meesho. Ni siquiera mencionar que encontraste algo.
- **No vender info:** Prohibido vender, licenciar, transferir o subastar cualquier información de vulnerabilidades a terceros, brokers, dark web, etc. Esto incluye antes y después de reportar.

---

## 9. QUÉ TIENE EL LABORATORIO ACTUAL vs QUÉ FALTA

### 9.1 Lo que el laboratorio YA tiene (útil para Meesho)

| Componente | Estado | Utilidad para Meesho |
|---|---|---|
| Pipeline de discovery de subdominios (OCI) | ✅ Etapas 1-4 funcionando | **Alta** — puede monitorear meesho.com y supplier.meesho.com |
| Cliente LLM (Groq/Gemini) | ✅ Listo | **Media** — analizar hallazgos, borradores de reportes |
| Cuenta HackerOne | ✅ Creada | **Crítica** — necesaria para participar |

### 9.2 Lo que FALTA (bloqueante para operar)

| Qué falta | Prioridad | Acción concreta |
|---|---|---|
| Username exacto de H1 confirmado | 🔴 CRÍTICA | Revisar hackerone.com/settings/profile |
| Método de pago configurado en H1 | 🔴 CRÍTICA | Settings > Payment Preferences |
| Burp Suite instalado | 🔴 CRÍTICA | portswigger.net/burp/communitydownload |
| Header X-Hackerone configurado en Burp | 🔴 CRÍTICA | Proxy > Options > Match and Replace |
| Conocimiento básico de IDOR/Business Logic | 🔴 ALTA | PortSwigger Web Security Academy (gratis) |
| Conocimiento de CVSS básico | 🟡 MEDIA | first.org/cvss/calculator/3.1 |
| APKTool + jadx para análisis estático (si se quiere probar apps) | 🟡 MEDIA | GitHub (gratuitos) |

---

## 10. TRAMPAS CRÍTICAS PARA NOVATOS

> [!CAUTION]
> Cada uno de estos errores puede resultar en cierre de reportes como spam, baja del signal score, o expulsión del programa. Un signal score bajo en H1 es muy difícil de recuperar.

| # | Trampa | Consecuencia | Cómo evitarla |
|---|---|---|---|
| 1 | Reportar sin PoC funcional | Cerrado como informativo | SIEMPRE demostrar el impacto con requests reales |
| 2 | Reportar cosas de la lista "fuera de scope" | Cerrado + baja de signal | Leer la lista completa antes de cada sesión |
| 3 | No incluir header X-Hackerone | Posible rechazo / cuenta marcada | Configurarlo como header global en Burp |
| 4 | Usar escáneres automáticos agresivos | Descalificación | Solo pruebas manuales con Burp |
| 5 | Registrarse con email personal en Meesho | No pueden verificar tu identidad | Usar TU_USERNAME@wearehackerone.com |
| 6 | Crear múltiples cuentas en Meesho | Descalificación + posible expulsión | Solo usar las dos cuentas de prueba provistas |
| 7 | Reportar issues de la lista "Known Issues" | Cerrado como duplicado inmediato | Memorizar los 5 issues conocidos listados |
| 8 | Contactar fuera de HackerOne | Descalificación | Solo comunicación dentro de la plataforma |
| 9 | Divulgar el hallazgo en redes sociales | Acción legal + expulsión | Confidencialidad absoluta hasta autorización escrita |
| 10 | Modificar contraseñas/configs de las cuentas de prueba | Expulsión + pérdida de acceso futuro | Solo leer y probar, nunca modificar configuración |

---

## 11. PLAN DE ACCIÓN POR SESIONES

### Sesión A — HOY (45 minutos) PREPARACIÓN OBLIGATORIA
- [ ] Ir a hackerone.com → Confirmar el username exacto
- [ ] Ir a Settings > Payment Preferences → Configurar PayPal o método elegido
- [ ] Descargar Burp Suite Community (portswigger.net/burp/communitydownload)
- [ ] Unirse al programa de Meesho en HackerOne si no está hecho

### Sesión B — ENTORNO DE PRUEBAS (1 hora)
- [ ] Instalar y configurar Burp Suite como proxy del navegador
- [ ] Crear regla "Match and Replace" en Burp para inyectar `X-Hackerone: TU_USERNAME` automáticamente
- [ ] Iniciar sesión en meesho.com con número 6666666661 / OTP 999999
- [ ] Explorar la app con Burp interceptando: mapear los endpoints de la API
- [ ] Iniciar sesión en supplier.meesho.com con suppliertest-1@meeshoai.com
- [ ] Hacer lo mismo con el panel de proveedores

### Sesión C — PRIMERA BÚSQUEDA (1-2 horas)
- **Objetivo:** Business Logic vulnerabilities (más asequibles para novatos)
- **Qué buscar en el panel de proveedores:**
  - ¿Se puede acceder a datos de suppliertest-2 estando logueado como suppliertest-1? (IDOR)
  - ¿Se pueden ver/modificar órdenes de otras cuentas cambiando IDs en los requests?
  - ¿Hay endpoints que devuelven más datos de los que deberían?
  - ¿Los precios o descuentos se validan en el servidor o solo en el cliente?

### Sesión D — PIPELINE DE MONITOREO (Etapa 5 del ROADMAP existente)
- Agregar meesho.com y supplier.meesho.com al `objetivos.txt` del pipeline OCI
- El cron diario empezará a monitorear subdominios nuevos de Meesho automáticamente
- Si aparece un subdominio no documentado → posible Subdomain Takeover o panel expuesto

---

## 12. RESUMEN EJECUTIVO

### ¿Está el laboratorio listo para operar?
**NO al 100%. Faltan Burp Suite, confirmación de username y método de pago.**

### ¿Es Meesho un buen primer programa?
**SÍ, con condiciones:**
- Credenciales de prueba ya disponibles (no necesitas gestionar cuentas propias)
- Tiempos de respuesta razonables para un principiante
- Pago garantizado en 1 mes
- Rangos de recompensa alcanzables para hallazgos bajos/medios ($96-$308 promedio)

### ¿Cuál es el ÚNICO paso de esta sesión?
**Confirmar el username exacto de HackerOne y configurar el método de pago.**
Sin eso, todo lo demás está bloqueado.

---

*Análisis generado el 2026-07-06. Verificar siempre contra la política actualizada en HackerOne antes de cada sesión de pruebas. La política de Meesho fue actualizada el 12/02/2026.*
