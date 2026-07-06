# 🔍 ANÁLISIS DE PROGRAMA: MONGODB (HackerOne)

> **Estado:** Prospecto analizado el 2026-07-06  
> **Propósito:** Evaluar viabilidad frente a Meesho y preparar el entorno de pruebas.  
> **Nivel de riesgo reputacional:** BAJO (Programa maduro, reglas claras para investigadores).

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
