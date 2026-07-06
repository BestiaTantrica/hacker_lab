# 🤖 PROMPTS DE AUDITORÍA DE RESULTADOS (CLI DE GEMINI / IA EXTERNA)

Este documento contiene los prompts exactos que debes utilizar para que una IA audite los resultados de tu pipeline de descubrimiento (los archivos JSON generados en el servidor OCI) y los logs de tus pruebas manuales con Burp Suite.

Está diseñado para cumplir el objetivo del laboratorio: automatizar el análisis de activos para maximizar la posibilidad de encontrar vulnerabilidades cobrables en Meesho.

---

## 1. Auditoría Masiva de Resultados OCI usando Gemini CLI
Si tienes instalado un CLI de Gemini o utilizas una herramienta de terminal que interactúe con el modelo, puedes pedirle que lea toda la carpeta de resultados (`resultados/` en tu servidor OCI) y te genere un reporte táctico.

### Comando para el CLI (apuntando a la carpeta de resultados):

```bash
gemini "Actúa como un cazador de recompensas (bug bounty hunter) senior. Voy a proporcionarte los archivos JSON de mi directorio de resultados del monitoreo pasivo de Meesho. Tu objetivo es auditar estos resultados para decirme dónde debo enfocar mis pruebas manuales. 

Por favor, analiza todos los subdominios nuevos encontrados en los deltas y entrégame un reporte estructurado con:
1. Top 5 Objetivos Críticos: Subdominios que probablemente expongan paneles de administración, entornos de pruebas (staging/dev), APIs internas, portales de proveedores o servicios desactualizados. Explica exactamente por qué los seleccionas.
2. Riesgo de Subdomain Takeover: Identifica si algún subdominio tiene formato de servicio de terceros en la nube (ej. aws, heroku, zendesk) que deba verificar.
3. Vectores de Ataque: Para el objetivo más crítico que encuentres, descríbeme las 3 primeras pruebas manuales que debo ejecutar con mi proxy (Burp Suite)." --files ./resultados/*.json
```

*(Nota: Ajusta `--files` según la sintaxis exacta de tu herramienta CLI particular)*

---

## 2. Auditoría de Deltas (Nuevos Subdominios) por Interfaz Web
Si descargas el archivo `delta_YYYY-MM-DD.json` desde OCI a tu PC y lo subes a ChatGPT, Claude o Gemini Web.

**Sube el archivo JSON y pega este prompt:**

> "Actúa como un analista de ciberseguridad ofensiva y cazador de recompensas (bug bounty hunter) senior. He adjuntado el archivo de resultados de mi pipeline de descubrimiento pasivo (delta de subdominios nuevos) para el programa de recompensas oficial de Meesho.
> 
> Necesito que analices la lista de subdominios descubiertos e identifiques los objetivos de mayor valor estratégico. Por favor, audita el archivo y entrégame:
> 
> 1. **Filtro de Alto Valor:** Extrae y lista los subdominios que tengan palabras clave interesantes (api, dev, stg, admin, supplier, test, internal, corp).
> 2. **Evaluación de Riesgo:** Para cada uno de esos subdominios interesantes, ¿qué tipo de vulnerabilidad es más probable encontrar según su nomenclatura? (Ej: si es un subdominio de API, buscar IDORs o Broken Access Control).
> 3. **Plan de Acción:** Enumera los 3 siguientes pasos exactos y comandos (sin usar escáneres ruidosos) que debería ejecutar para validar si estos subdominios están activos y si tienen servicios expuestos."

---

## 3. Auditoría de Peticiones HTTP (Logs de Burp Suite)
Durante tus pruebas en `supplier.meesho.com` u otros paneles, cuando encuentres una petición interesante (por ejemplo, al actualizar tu perfil o enviar un formulario), puedes pedirle a la IA que la audite en busca de vulnerabilidades de Business Logic o IDOR.

En Burp Suite: Selecciona el Request y el Response, haz clic derecho -> "Copy to file" (o simplemente cópialos como texto).

**Prompt para auditar la petición:**

> "Actúa como un auditor de seguridad web experto. Estoy analizando la aplicación `supplier.meesho.com` dentro de un programa oficial de bug bounty.
> 
> He interceptado esta petición y respuesta HTTP. Mi objetivo es encontrar vulnerabilidades de Business Logic, IDOR, Broken Access Control o Inyecciones de datos, las cuales están permitidas y son recompensadas en el programa.
> 
> **[PEGA AQUÍ EL REQUEST COMPLETO CON HEADERS, INCLUYENDO X-Hackerone]**
> 
> **[PEGA AQUÍ EL RESPONSE COMPLETO CON HEADERS Y BODY]**
> 
> Por favor audita este flujo de comunicación y responde:
> 1. ¿Ves algún parámetro predecible (como IDs numéricos, UUIDs predecibles) que sea candidato para un ataque IDOR (Insecure Direct Object Reference)?
> 2. ¿Hay parámetros que controlen estado, roles o precios que pueda intentar manipular (Business Logic)?
> 3. ¿El servidor expone información sensible excesiva en el cuerpo de la respuesta JSON que no debería estar ahí (Mass Assignment / Data Exposure)?
> 4. ¿Qué modificaciones exactas me sugieres hacer en el Request (parámetros a cambiar, borrar o duplicar) para intentar forzar una vulnerabilidad en mi siguiente prueba?"

---

## 4. Auditoría de Flujos Multi-Paso (Business Logic)
Si estás probando el flujo de creación de una tienda o producto en `supplier.meesho.com` usando las dos cuentas de prueba.

**Prompt para auditar lógica de negocio:**

> "Actúa como un experto en pruebas de Lógica de Negocio (Business Logic Flaws). Estoy auditando el panel de proveedores de Meesho. 
> 
> He documentado este flujo de 3 pasos que realiza un usuario normal al [DESCRIPCIÓN DE LA ACCIÓN, ej. agregar un producto o modificar datos bancarios]:
> 
> 1. Petición POST a /api/paso1 con parámetros [X]
> 2. Petición GET a /api/paso2
> 3. Petición POST a /api/paso3 finalizando el proceso
> 
> Mi objetivo es romper esta lógica. ¿Cómo auditarías este flujo?
> Piensa en:
> - ¿Qué pasa si me salto el paso 2 y voy directo al 3?
> - ¿Qué pasa si uso el token de autorización de mi Cuenta B para el paso 3 de mi Cuenta A?
> - ¿Qué ataques de "condición de carrera" (Race Condition) podrían aplicarse aquí?
> 
> Dame un plan estructurado de 3 escenarios maliciosos para probar en Burp Suite."
