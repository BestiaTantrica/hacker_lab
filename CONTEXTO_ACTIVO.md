# 🎯 CONTEXTO ACTIVO DEL LAB — Ciberguardia
> **ATENCIÓN IA:** Lee este archivo antes de sugerir acciones. Este es el estado real y actual del laboratorio.

## 📌 Objetivo Principal
**Primer ingreso real en Bug Bounty** a través de la plataforma HackerOne.

## 🎯 Target Actual
- **Programa:** MongoDB Atlas
- **Vector Activo:** IDOR y CORS en la API (`/nds/` endpoints)
- **Cuentas de prueba:**
  - `Cuenta A` (Atacante/Tester)
  - `Cuenta B` (Víctima)

## 🛠️ Herramientas y Eslabones
El flujo de trabajo se basa en herramientas Go de ProjectDiscovery, combinadas con scripts Python propios para adaptar los resultados.

**Kit Externo Instalado (en `LAB/herramientas/bin`):**
1. `subfinder` (Recon pasivo)
2. `dnsx` (Resolución y filtrado DNS)
3. `httpx` (Verificación de endpoints activos)
4. `nuclei` (Automatización de vulnerabilidades basadas en templates YAML)

**Cadena de Scripts Propios:**
- `diagnostico_oci.py`: Para controlar el pipeline pasivo en Oracle Cloud.
- `Burp Suite`: Herramienta principal de testing manual e IDOR (con headers de X-HackerOne-Research configurados).

## 🚫 Restricciones y Reglas (¡Cumplir estrictamente!)
1. **Evitar falsos positivos:** No reportar nada sin un **PoC (Proof of Concept) verificable y completo**.
2. **Tokens de IA:** Evitar procesar miles de líneas de logs crudos con la IA. Usar herramientas locales (`grep`, `jq`, `httpx`, `nuclei`) para filtrar primero. La IA solo entra a razonar cuando hay datos filtrados.
3. **Automatización progresiva:** Construir "eslabones de scripts" paso a paso para que el humano ejecute fácilmente.
4. **Validación:** No asumir que un subdominio es vulnerable solo porque una herramienta lo diga (ej. Takeovers falsos en Fastly). Validar siempre el *HTTP body*.
5. **IA en el Servidor (Asesor Paralelo 24/7):** No usar la IA del servidor OCI para analizar deltas automáticamente de forma ciega. Su propósito es actuar como un asesor paralelo 24/7 con contexto persistente del laboratorio, al cual el usuario pueda consultar directamente para educarse, guiarse y resolver dudas de comandos o redes sin perder tiempo.

## 🚀 Próxima Tarea Inmediata
- Realizar pruebas de **IDOR manual y semi-automatizado** cruzando sesiones entre la Cuenta A y la Cuenta B en MongoDB Atlas mediante Burp Suite.
- Modificar el pipeline de OCI para reorientar el script de IA hacia este enfoque de Asesor Paralelo 24/7.

