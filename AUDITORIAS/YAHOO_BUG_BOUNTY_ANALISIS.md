# 🕵️ Análisis de Seguridad: Yahoo / Verizon Media (HackerOne)

## 1. Perfil del Programa
- **Plataforma:** HackerOne (https://hackerone.com/yahoo)
- **Tiempos de Respuesta:** Rápidos. El triaje suele tardar entre 2 y 5 días.
- **Recompensas:** Sí. Pagan recompensas basadas en la severidad (CVSS).
- **Foco Principal:** Activos web de la marca Yahoo, AOL, Flickr, HuffPost y sus respectivas infraestructuras de red.

## 2. Alcance Principal (In-Scope Wildcards)
El programa posee un alcance sumamente extenso. Los dominios primarios para nuestro pipeline de monitoreo pasivo son:
- `*.yahoo.com`
- `*.aol.com`
- `*.flickr.com`
- `*.huffpost.com`

## 3. Reglas Críticas e Identificación de Tráfico
Para evitar bloqueos del WAF o reportes rechazados, sigue estas reglas:
- **Cabecera Obligatoria de Identificación:** Debes incluir en todas tus solicitudes HTTP de prueba la siguiente cabecera:
  ```http
  X-HackerOne-Research: tomas244
  ```
- **Prohibido:** Ataques volumétricos (DDoS), escaneos automáticos agresivos que degraden el servicio, e ingeniería social contra empleados.

## 4. Vectores de Ataque Prioritarios para nuestro Laboratorio
Debido al inmenso tamaño del scope y la existencia de miles de servidores antiguos, nos enfocaremos en:
1. **Fugas de Información y Archivos Expuestos:**
   - Buscar rutas como `.git/`, `.env`, archivos de configuración expuestos (`config.json`, `settings.yml`) o respaldos de bases de datos (`backup.sql`, `dump.zip`).
2. **Subdomain Takeovers:**
   - Monitorear el pipeline pasivo para detectar subdominios inactivos que apunten a servicios externos (S3, GitHub Pages, Fastly, Shopify) que hayan sido dados de baja por Yahoo pero cuyo registro CNAME aún apunte allí.
3. **Paneles de Administración Expuestos:**
   - Buscar paneles de Jenkins, Kibana, Jira o consolas de administración sin autenticación o con credenciales por defecto.

## 5. Próximos Pasos de Integración
1. Unirse al programa de Yahoo en HackerOne.
2. Añadir `yahoo.com`, `aol.com` y `flickr.com` al archivo `config/objetivos.txt` en el servidor OCI.
