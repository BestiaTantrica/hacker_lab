# 🕵️ Análisis de Seguridad: Elastic (HackerOne)

## 1. Perfil del Programa
- **Plataforma:** HackerOne
- **Tiempos de Respuesta:** Muy rápidos (Triaje: ~6 días, Resolución: ~4 meses)
- **Recompensas:** Generosas (Críticos: $3,000 - $9,000 | Altos: $1,500 - $4,000)
- **Foco Principal:** Productos de la suite Elastic (Elasticsearch, Kibana, Logstash, APM, Beats), Elastic Cloud (`cloud.elastic.co`) e infraestructura SaaS relacionada.

## 2. Alcance Principal (In-Scope)
- **Cloud y SaaS:**
  - `*.elastic.co` (Todo incluido salvo exclusiones explícitas)
  - `cloud.elastic.co` (Requiere cuenta de prueba con correo `@wearehackerone.com`)
  - `*.swiftype.com`
  - `*.found.io` (Infraestructura interna)
- **Productos Core (Descargables / Docker / Código):**
  - Kibana, Elasticsearch, Logstash, Fleet Server, Enterprise Search.
  - Agentes APM y Beats (Filebeat, Packetbeat, etc.)
- **Cadena de Suministro (Supply Chain):**
  - Repositorios de GitHub (`https://github.com/elastic`) y flujos de trabajo en `.github/workflows`.
  - Fugas de credenciales en servicios de compilación (Buildkite, Github Actions).

## 3. Reglas Críticas y Exclusiones (Out-of-Scope)
Para no perder tiempo ni reputación, **NUNCA reportar:**
1. **Falta de Bypass CSP en XSS:** Los XSS que no logran eludir la Política de Seguridad de Contenido (CSP) se pagan muy bajo o son rechazados.
2. **Clickjacking / CSRF sin impacto:** Si no hay acciones sensibles de por medio, no es válido.
3. **Ataques Volumétricos (DoS/DDoS):** Estrictamente prohibidos.
4. **Privilegios de Administrador:** Vulnerabilidades que requieren acceso previo de administrador/root ("cruzar la frontera del admin al kernel no es un problema de seguridad para ellos").
5. **Dominios excluidos:** `*.keephq.dev`, `discuss.elastic.co`, `community.elastic.co`, Wikis de Github, `*.jina.ai`, entre otros.

## 4. Vectores de Ataque Prioritarios para nuestro Laboratorio

### Vector 1: Elastic Cloud (cloud.elastic.co) - Aislamiento e IDORs
- **Objetivo:** Probar el panel de administración de cuentas de nube.
- **Acción:** Crear dos cuentas (`cuenta_A@wearehackerone.com` y `cuenta_B@wearehackerone.com`).
- **Pruebas:** 
  - Intentar que la Cuenta A modifique, elimine o acceda a instancias, despliegues o facturación de la Cuenta B manipulando IDs en las peticiones.
  - SSRF autenticado en la creación de monitores (Elastic Synthetics).

### Vector 2: Adquisición de Subdominios (Subdomain Takeover)
- **Objetivo:** El alcance wildcard (`*.elastic.co`, `*.swiftype.com`, `*.found.io`) es inmenso.
- **Acción:** Monitoreo pasivo diario (Ya configurado en OCI).
- **Pruebas:** Si el OCI detecta un subdominio que apunta a un servicio desvinculado (AWS S3, GitHub Pages, Heroku), documentar y reportar inmediatamente.

### Vector 3: Supply Chain y Github Actions
- **Objetivo:** Inyección de comandos en CI/CD o fugas de secretos.
- **Acción:** Revisar repositorios de `https://github.com/elastic`.
- **Pruebas:** Analizar `.github/workflows` buscando configuraciones vulnerables (ej: `pull_request_target` mal implementado, uso inseguro de variables, etc.).

### Vector 4: Exposición de APIs Internas
- **Objetivo:** Encontrar instancias de Elasticsearch/Kibana internas expuestas sin autenticación.
- **Pruebas:** Monitorear puertos `9200`, `5601` en los subdominios descubiertos.

## 5. Metodología de Trabajo y Siguientes Pasos
1. **Infraestructura:** Esperar a que el OCI genere el primer `delta_*.json` para `elastic.co`.
2. **Cuentas de Prueba:** Crear las cuentas de prueba en `cloud.elastic.co` usando el alias de HackerOne.
3. **Configuración de Burp:** Añadir el header `X-HackerOne-Research: <usuario>` a Burp Suite para todo el tráfico hacia `*.elastic.co`.
