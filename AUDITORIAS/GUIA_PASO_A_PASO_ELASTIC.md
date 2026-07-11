# 📓 Guía de Configuración y Auditoría Manual: Elastic.co

Esta guía detalla los pasos que debes realizar manualmente en tu PC de desarrollo para configurar el entorno de pruebas multi-tenant y auditar los subdominios de Elastic de forma ética y segura, siguiendo los lineamientos del programa de Bug Bounty en HackerOne.

---

## 🎯 1. Estrategia de Modelos y Gestión de Cuotas (Ref. Sección 11)
Para optimizar el uso de tokens y cumplir con las políticas de seguridad:
* **Ejecución del Script de Validación:** La validación activa de cabeceras en producción se realiza desde tu terminal local utilizando `validador_headers.py`. Esto evita el escaneo automático desde la sesión principal de la IA o llamadas no autorizadas.
* **Modelo Utilizado:** **Gemini 3.5 Flash** para la generación de herramientas y documentación, reservando modelos más avanzados solo para auditorías lógicas complejas de vulnerabilidades confirmadas.

---

## 👥 2. Configuración de Cuentas de Prueba (Atacante y Víctima)

Para validar vulnerabilidades lógicas de aislamiento como **IDOR (Insecure Direct Object Reference)** o **CORS Misconfiguration**, necesitas simular un entorno multi-tenant real con dos identidades independientes.

### Paso 1: Crear la Cuenta A (Perfil Atacante)
1. Ve a [https://cloud.elastic.co/registration](https://cloud.elastic.co/registration).
2. Regístrate usando tu dirección de correo de HackerOne (ej. `tu_usuario@wearehackerone.com`).
3. Activa la cuenta mediante el correo de verificación.
4. Crea una instancia de prueba (Deployment) y anota los siguientes datos en una nota local:
   * **Organization ID** (ej: obtenido de la URL del panel de control).
   * **Deployment ID** (UUID del cluster de Elasticsearch/Kibana creado).
   * **Cookies de sesión** activas.

### Paso 2: Crear la Cuenta B (Perfil Víctima)
1. Abre una ventana de incógnito o utiliza un navegador secundario diferente.
2. Ve a [https://cloud.elastic.co/registration](https://cloud.elastic.co/registration).
3. Regístrate utilizando un alias diferente (ej. `tu_usuario+victima@wearehackerone.com`).
4. Crea una instancia de prueba independiente en esta cuenta.
5. Anota los datos de esta segunda cuenta:
   * **Organization ID de la Víctima**.
   * **Deployment ID de la Víctima**.
   * **API Keys o identificadores de recursos**.

---

## 🔌 3. Configuración de Burp Suite

El programa de Elastic requiere que identifiques tu tráfico claramente para evitar bloqueos del WAF o reportes falsos de intrusion.

### Paso 1: Añadir la Cabecera de Investigación Obligatoria
1. Abre **Burp Suite**.
2. Dirígete a **Proxy** -> **Proxy settings** -> **Match and Replace**.
3. Haz clic en **Add** para añadir una nueva regla:
   * **Type:** `Request header`
   * **Match:** (deja en blanco)
   * **Replace:** `X-HackerOne-Research: tu_usuario_h1`
   * **Comment:** Identificador de Bug Bounty para Elastic.
4. Asegúrate de que la regla esté activa (marcada con el check).

### Paso 2: Definir el Scope (Alcance)
1. Ve a **Target** -> **Scope settings**.
2. Añade las siguientes reglas en "Include in scope":
   * `https://*.elastic.co`
   * `https://*.swiftype.com`
   * `https://*.found.io`
3. En "Exclude from scope" añade los dominios expresamente excluidos:
   * `discuss.elastic.co`
   * `community.elastic.co`

---

## 🛠️ 4. Uso del Script de Validación de Cabeceras

Hemos creado el script `LAB/api/validador_headers.py`. Para ejecutarlo de forma segura en tu máquina local:

### Opción A: Analizar un objetivo específico
```bash
python3 LAB/api/validador_headers.py --target secrets.elastic.co --ignore-ssl
```

### Opción B: Analizar una lista de objetivos desde un archivo
1. Crea un archivo `objetivos_elastic.txt` en `LAB/api/` con los subdominios a auditar (uno por línea):
   ```text
   secrets.elastic.co
   vault-acc.elastic.co
   vault-test.elastic.co
   www.jenkins.elastic.co
   ```
2. Ejecuta el validador:
   ```bash
   python3 LAB/api/validador_headers.py --file LAB/api/objetivos_elastic.txt --ignore-ssl
   ```

### Qué analizar en los resultados del script:
1. **Código de estado:**
   * Si responde `403` o `401` en `www.jenkins.elastic.co`, verifica si hay algún recurso expuesto en rutas secundarias (ej: `/cli`, `/api`, `/asynchPeople/`).
   * Si `secrets.elastic.co` devuelve `200 OK`, investiga manualmente con Burp Suite qué tipo de datos o indexación expone.
2. **Ausencia de HSTS / CSP / X-Frame-Options:**
   * La falta de `X-Frame-Options` puede indicar susceptibilidad a Clickjacking (solo reportable si hay acciones sensibles de por medio).
   * La falta de `Content-Security-Policy` o configuraciones muy laxas aumentan el impacto de posibles vectores XSS.

---

## 🔬 5. Auditoría Manual Paso a Paso de Vectores Críticos

### Vector 1: IDOR en Elastic Cloud (cloud.elastic.co)
1. Inicia sesión en la **Cuenta A (Atacante)** en tu navegador proxyado con Burp Suite.
2. Captura peticiones del tipo `GET /api/deployments/<UUID_A>` o `POST /api/organizations/<ORG_ID_A>/...`.
3. Envía estas peticiones a **Burp Repeater**.
4. Reemplaza el `<UUID_A>` o `<ORG_ID_A>` por el `<UUID_B>` o `<ORG_ID_B>` de la **Cuenta B (Víctima)**.
5. Envía la petición:
   * **Vulnerable:** Si el servidor devuelve `200 OK` con información del recurso de la Cuenta B.
   * **Seguro:** Si devuelve `403 Forbidden` o `404 Not Found`.

### Vector 2: CORS Misconfiguration
1. Envía una petición hacia el dominio de la API de Elastic (ej. `cloud.elastic.co`) a **Burp Repeater**.
2. Añade o modifica la cabecera `Origin` en la solicitud:
   ```http
   Origin: https://evil.com
   ```
3. Envía la petición y revisa la respuesta:
   * **Vulnerable:** Si la respuesta contiene:
     ```http
     Access-Control-Allow-Origin: https://evil.com
     Access-Control-Allow-Credentials: true
     ```
     *(Esto permitiría a un sitio atacante leer datos confidenciales de la sesión del usuario).*

### Vector 3: Exposición de Jenkins (www.jenkins.elastic.co)
1. Accede a la URL con tu navegador.
2. Verifica si la consola principal es visible sin autenticación.
3. Si requiere inicio de sesión, comprueba:
   * Versión expuesta en las cabeceras HTTP (e.g. `X-Jenkins`).
   * Acceso a endpoints de Jenkins vulnerables como `/overallShareable`, `/securityRealm/user/...` o exploits públicos conocidos para la versión detectada.
