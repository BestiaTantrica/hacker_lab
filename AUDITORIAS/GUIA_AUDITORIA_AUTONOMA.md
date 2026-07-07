# 🛠️ GUÍA OPERATIVA DE AUDITORÍA AUTÓNOMA CON GEMINI CLI

Esta guía te permite operar como el analista de seguridad en tu PC, utilizando tu CLI local de Gemini para auditar el tráfico sin consumir tokens en nuestra sesión principal. 

---

## 1. FLUJO DE TRABAJO DIARIO (PC Local + CLI)

```text
[ Burp Suite (Navegación en Atlas) ]
                │
                ▼ (Interceptar Request/Response interesantes)
  [ Copiar a Archivos de Texto Temporales ]
                │
                ▼
  [ Auditar con Gemini CLI usando Prompts ]
                │
                ▼ (Si se detecta un Bug)
[ Crear Reporte de Vulnerabilidad en Git ]
```

---

## 2. TAREAS OPERATIVAS DETALLADAS (Paso a Paso en Burp)

### Tarea 1: Búsqueda de IDOR (Insecure Direct Object Reference)
*   **Acción:** Ve a la Consola de Atlas, crea un proyecto, borra un proyecto, o cambia el nombre de tu proyecto.
*   **En Burp (HTTP History):** Busca peticiones `POST`, `PUT`, `DELETE` o `GET` que contengan identificadores en la URL o en el cuerpo.
    *   *Ejemplo de ID:* `5f4d8e9c0b1a23456789def0` (formato típico de IDs de base de datos de MongoDB).
*   **Auditoría con CLI:** Guarda la petición en un archivo temporal `req.txt` y ejecuta en tu terminal:
    ```bash
    gemini "Actúa como especialista en seguridad web. Analiza esta petición de MongoDB Atlas. Si tengo dos cuentas de prueba de Atlas (Org A y Org B), ¿cómo puedo intentar modificar este request para acceder o alterar recursos de la Org B estando autenticado en la Org A? Busca campos de ID de organización, proyecto o usuario susceptibles a IDOR." --files req.txt
    ```

### Tarea 2: Escalación de Privilegios (Mapeo de Roles)
*   **Acción:** Ve a la sección de Accesos (Database Access u Organization Access), crea un usuario de base de datos con permisos mínimos (ej. solo lectura).
*   **En Burp (HTTP History):** Intercepta la petición de creación del usuario. Busca el parámetro que define el rol o los privilegios.
    *   *Ejemplo de parámetro:* `"roles": [{"roleName": "read", "databaseName": "admin"}]`.
*   **Auditoría con CLI:** Guarda la petición en `req.txt` y ejecuta:
    ```bash
    gemini "Actúa como auditor de APIs. Analiza esta petición de asignación de roles. ¿Qué ocurre si intento inyectar roles de administrador como 'atlasAdmin' o 'root' en este JSON? ¿El backend sanitiza los roles o depende del cliente?" --files req.txt
    ```

### Tarea 3: Modificación del Perfil (Mass Assignment / Parameter Pollution)
*   **Acción:** Modifica la configuración de facturación, nombre de usuario o datos de contacto.
*   **En Burp (HTTP History):** Busca la petición `PATCH` o `PUT` que envía los datos en formato JSON.
*   **Auditoría con CLI:** Guarda la petición en `req.txt` y ejecuta:
    ```bash
    gemini "Actúa como analista de seguridad web. Analiza esta petición de actualización de datos de perfil en MongoDB Atlas. ¿Qué otros parámetros del sistema (como campos de estado de cuenta, flags de facturación o roles de administrador) podría intentar añadir al payload JSON para verificar si el backend los acepta de forma insegura (Mass Assignment)?" --files req.txt
    ```

---

## 3. CÓMO USAR EL SERVIDOR OCI (24/7 AUTOMÁTICO)

El servidor OCI en Ashburn se encarga de la **fase pasiva de recolección de información**. Así es como lo mantendremos operando sin tu intervención constante:

1.  **Cambiar Objetivos en OCI:**
    *   Conéctate a tu OCI: `ssh -i ~/.ssh/id_rsa ubuntu@129.80.73.248`
    *   Edita el archivo de objetivos: `nano ~/plataforma_operativa/config/objetivos.txt`
    *   Reemplaza el contenido por los dominios de MongoDB que están en el alcance del programa:
        ```text
        mongodb.com
        evergreen-ci
        ```
    *   Guarda y sal (`Ctrl+O`, `Enter`, `Ctrl+X`).

2.  **Monitoreo Automático:**
    *   El script de descubrimiento pasivo se ejecutará automáticamente a las 6:00 AM.
    *   Buscará nuevos subdominios de MongoDB y comparará el resultado con el día anterior.
    *   Si encuentra un subdominio nuevo, generará un archivo delta.
    *   **En la próxima etapa:** Agregaremos el notificador de Telegram al servidor para que recibas en tu celular un aviso cada vez que aparezca un subdominio nuevo de MongoDB sin que tengas que entrar al servidor a revisar.

---

## 4. COMANDOS DE CONSOLA BASH Y GIT DE USO RÁPIDO

Para mantener todo el progreso guardado y auditado, usa estos comandos desde la raíz de tu workspace local (`/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB`):

*   **Ver el estado actual de los archivos:**
    ```bash
    git status
    ```
*   **Añadir un archivo de reporte nuevo al repositorio:**
    ```bash
    git add AUDITORIAS/mi_reporte.md
    ```
*   **Confirmar los cambios (Commit):**
    ```bash
    git commit -m "feat: Agregar reporte preliminar de vulnerabilidad en MongoDB Atlas"
    ```
*   **Ver los últimos cambios realizados:**
    ```bash
    git log -n 5 --oneline
    ```
