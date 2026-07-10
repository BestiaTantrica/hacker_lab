# 🧭 Guía de Ejecución: IDOR y CORS en MongoDB Atlas API

Esta guía te guiará paso a paso para extraer las cookies y IDs necesarios de tus dos cuentas de prueba (**Cuenta A - Tester** y **Cuenta B - Víctima**) y ejecutar la auditoría de seguridad automatizada mediante nuestro script local.

---

## 📋 Requisitos Previos

1. **Configuración de Navegadores:**
   *   **Cuenta A (Tester):** Utiliza el Chromium integrado en **Burp Suite** para aprovechar el monitoreo y las herramientas (tab de inspector/intruder) directamente.
   *   **Cuenta B (Víctima):** Utiliza tu navegador habitual (ej. Chrome/Brave).
2. Haber iniciado sesión en **MongoDB Atlas** en ambas cuentas.
3. **Herramientas del Kit:** Confirmamos que `instalar_kit.sh` instaló **dos herramientas** independientes en `/LAB/herramientas/bin/`: `dnsx` (resolución DNS rápida) y `httpx` (análisis HTTP/CORS). El script local las utiliza automáticamente.

---

## 🔍 Paso 1: Obtener los IDs (OrgID y ProjectID)

Los identificadores de organización y proyecto de MongoDB Atlas se extraen directamente de la URL:

1. Entra al panel de MongoDB Atlas de cada cuenta.
2. Mira la URL en el navegador:
   *   **Cuenta A:** `https://cloud.mongodb.com/v2#/org/6a4c0a54b388b65b11799a24/projects` (OrgID: `6a4c0a54b388b65b11799a24`)
   *   **Cuenta B (Víctima):** `https://cloud.mongodb.com/v2#/org/6a4d7d849d5dcab6abad6820/projects` (OrgID: `6a4d7d849d5dcab6abad6820`)
3. Haz clic en el proyecto principal de cada cuenta para obtener el **ProjectID** (el ID que aparece después de `/v2/` en la URL, ej. `6a4c0a54b388b65b11799a58`).

> 📝 **Anota estos 4 IDs:**
> *   `ORG_A` (Cuenta A) y `PROJ_A` (Cuenta A)
> *   `ORG_B` (Cuenta B: `6a4d7d849d5dcab6abad6820`) y `PROJ_B` (Cuenta B)

---

## 🍪 Paso 2: Obtener las Cookies de Sesión de la Cuenta A (Atacante)

Para que el script pueda hablar con la API de MongoDB, necesita la cookie de autenticación de tu **Cuenta A**. Puedes obtenerla fácilmente desde el navegador Firefox (donde tienes iniciada la sesión A):

1. En Firefox, presiona la tecla **F12** (o clic derecho -> *Inspeccionar*).
2. Ve a la pestaña **Almacenamiento** (Storage) en la barra superior del inspector.
3. En el menú de la izquierda, despliega **Cookies** y haz clic en `https://cloud.mongodb.com`.
4. En la tabla de la derecha verás una lista de cookies.
5. Selecciona cualquier fila, presiona `Ctrl + A` para seleccionar todo, luego clic derecho y selecciona **Copiar**.
6. Esto te dará un string largo con todas las cookies unidas por punto y coma (ej. `ajs_user_id=...; cloud-user=...; mms-session=...`).

---

## 🚀 Paso 3: Ejecutar la Auditoría Automatizada

Ya tenemos el script listo para realizar las peticiones cruzadas en `LAB/api/auditar_vectores.py`. 

1. Abre tu terminal local en tu PC.
2. Activa el entorno virtual del laboratorio:
   ```bash
   source /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/venv/bin/activate
   ```
3. Ejecuta el script pasándole las cookies de la **Cuenta A** y los IDs que anotaste en el paso 1:
   ```bash
   python3 /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/auditar_vectores.py "TU_STRING_DE_COOKIES_DE_CUENTA_A" ORG_A PROJ_A ORG_B PROJ_B
   ```

*Nota: Reemplaza `TU_STRING_DE_COOKIES_DE_CUENTA_A` por el string largo de cookies que copiaste en el Paso 2 (mantenlo entre comillas dobles).*

---

## 📊 Paso 4: Revisar el Reporte de Resultados

Una vez que termine la ejecución del script, este generará automáticamente un reporte Markdown detallado en:
📁 `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/AUDITORIAS/RESULTADO_AUDITORIA_VECTORES.md`

### Cómo interpretar los resultados del reporte:
*   **Vector 5 (AI Keys) con HTTP 200/201**: **¡Vulnerabilidad! 🚨** Indica que pudiste consultar las API Keys del modelo de IA de la Cuenta B (Víctima) utilizando las cookies de la Cuenta A (Tester).
*   **Vector 5 con HTTP 403 / 401**: **Seguro.** El sistema bloqueó correctamente el acceso.
*   **Vector 6 (CORS GET con Origin de Evil)**: Si en la columna de respuesta ves que `access-control-allow-origin` devuelve `https://evil.mongodb.com` y `access-control-allow-credentials` es `true`, **¡Vulnerabilidad! 🚨**
