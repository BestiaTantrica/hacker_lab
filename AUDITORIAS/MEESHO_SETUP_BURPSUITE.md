# 🛡️ GUÍA DE INSTALACIÓN Y CONFIGURACIÓN — ENTORNO BUG BOUNTY
## Meesho · HackerOne · Usuario: tomas244

> **Sistema operativo:** Linux (Ubuntu/Debian)  
> **Objetivo:** Configurar el entorno de pruebas completo antes de tocar meesho.com  
> **Regla:** Cada paso tiene su verificación. No avanzar al siguiente sin confirmar el anterior.

---

## ÍNDICE

1. [¿Qué vamos a instalar y por qué?](#1-qué-vamos-a-instalar-y-por-qué)
2. [FASE 1 — Instalar Burp Suite Community](#2-fase-1--instalar-burp-suite-community)
3. [FASE 2 — Instalar el certificado SSL de Burp en el navegador](#3-fase-2--instalar-el-certificado-ssl-de-burp-en-el-navegador)
4. [FASE 3 — Configurar el header X-Hackerone automático](#4-fase-3--configurar-el-header-x-hackerone-automático)
5. [FASE 4 — Configurar el Scope (solo meesho.com)](#5-fase-4--configurar-el-scope-solo-meeshocom)
6. [FASE 5 — Verificación completa del entorno](#6-fase-5--verificación-completa-del-entorno)
7. [Estado del Roadmap completo tras esta sesión](#7-estado-del-roadmap-completo-tras-esta-sesión)

---

## 1. ¿Qué vamos a instalar y por qué?

| Herramienta | Para qué sirve | Costo |
|---|---|---|
| **Burp Suite Community Edition** | Proxy que intercepta el tráfico HTTP/HTTPS entre tu navegador y el servidor. Te permite ver, modificar y reenviar peticiones. Es la herramienta fundamental de todo bug bounty hunter. | Gratis |
| **Certificado CA de Burp** | Burp actúa como "hombre en el medio" para leer HTTPS. El navegador necesita confiar en su certificado para no bloquearlo. | Gratis (parte de Burp) |

**Lo que NO instalaremos hoy:** Nikto, sqlmap, nmap, ni ningún escáner automático. Meesho los prohíbe explícitamente y su uso resulta en descalificación.

---

## 2. FASE 1 — Instalar Burp Suite Community

### Paso 1.1 — Descargar Burp Suite

Abre una terminal (`Ctrl+Alt+T`) y ejecuta:

```bash
# 1. Ir a la carpeta de descargas
cd ~/Downloads

# 2. Descargar el instalador de Burp Suite Community para Linux
wget "https://portswigger.net/burp/releases/download?product=community&type=Linux" \
     -O burpsuite_community_linux.sh

# 3. Verificar que se descargó correctamente (debe mostrar un número de bytes > 0)
ls -lh burpsuite_community_linux.sh
```

**Verificación 1.1:** El archivo debe pesar más de 100 MB. Si pesa 0 bytes o pocos KB, la descarga falló. Repetir el paso.

---

### Paso 1.2 — Alternativa si wget falla (descarga manual)

Si el paso anterior falla:
1. Abrir el navegador
2. Ir a: **https://portswigger.net/burp/communitydownload**
3. Seleccionar **"Linux (64-bit)"**
4. Guardar el archivo `.sh` en `~/Downloads/`

---

### Paso 1.3 — Dar permisos de ejecución e instalar

```bash
# 1. Dar permiso de ejecución al instalador
chmod +x ~/Downloads/burpsuite_community_linux.sh

# 2. Ejecutar el instalador
~/Downloads/burpsuite_community_linux.sh
```

Se abrirá una ventana gráfica de instalación. Seguir estos pasos dentro del instalador:
1. **"Next"** en la pantalla de bienvenida
2. **"Next"** para confirmar la ruta de instalación (dejar el valor por defecto)
3. **"Next"** para crear acceso directo en el menú de aplicaciones
4. **"Install"** para comenzar la instalación
5. **"Finish"** cuando termine

**Verificación 1.3:**
```bash
# Verificar que Burp Suite quedó instalado
ls ~/BurpSuiteCommunity/
# Debe mostrar archivos incluyendo "BurpSuiteCommunity"
```

---

### Paso 1.4 — Ejecutar Burp Suite por primera vez

```bash
# Ejecutar Burp Suite
~/BurpSuiteCommunity/BurpSuiteCommunity &
```

O buscarlo en el menú de aplicaciones de tu sistema operativo.

Al abrir, te preguntará:
- **"Start Burp"**: Seleccionar **"Temporary project"** → **"Next"** → **"Use Burp defaults"** → **"Start Burp"**

> [!NOTE]
> En la versión Community, los proyectos son temporales (se pierden al cerrar). Para bug bounty, esto es suficiente porque documentaremos todo por capturas de pantalla.

**Verificación 1.4:** Burp Suite abre y muestra el Dashboard principal con pestañas: Dashboard, Target, Proxy, Repeater, etc.

---

## 3. FASE 2 — Instalar el certificado SSL de Burp en el navegador

**Por qué es necesario:** Meesho usa HTTPS. Burp necesita descifrar ese tráfico para mostrarte los requests. Para hacerlo, actúa como intermediario y usa su propio certificado SSL. El navegador rechazaría ese certificado (mostraría error de seguridad) a menos que le digamos que confíe en él.

**Método: Instalar el certificado en Firefox** (recomendado, Firefox tiene su propio almacén de certificados)

### Paso 2.1 — Activar el proxy en Burp

Dentro de Burp Suite:
1. Ir a la pestaña **"Proxy"**
2. Ir a **"Proxy settings"** (o "Options" en versiones anteriores)
3. Verificar que el listener está activo: debe aparecer `127.0.0.1:8080` con el estado **"Running"**

**Verificación 2.1:** La entrada `127.0.0.1:8080` tiene un checkmark verde o el estado "Running".

---

### Paso 2.2 — Descargar el certificado de Burp

Con Burp Suite corriendo y el proxy activo en el puerto 8080:

**Opción A — Desde el navegador (recomendado):**
1. Abrir Firefox
2. Ir a: **http://burpsuite** (con Burp corriendo, esta URL especial funciona)
3. Hacer clic en **"CA Certificate"** para descargar el certificado
4. Guardar como `burp_ca.der` en `~/Downloads/`

**Opción B — Si la URL no funciona:**
1. Ir a: **http://127.0.0.1:8080**
2. Hacer clic en **"CA Certificate"**

---

### Paso 2.3 — Instalar el certificado en Firefox

1. Abrir Firefox
2. Ir a **Configuración** (ícono de hamburguesa ☰ arriba a la derecha)
3. Buscar "certificado" en la barra de búsqueda de configuración
4. Hacer clic en **"Ver certificados..."**
5. Ir a la pestaña **"Autoridades"**
6. Hacer clic en **"Importar..."**
7. Seleccionar el archivo `burp_ca.der` descargado en el paso anterior
8. Marcar las dos opciones:
   - ✅ **"Confiar en esta CA para identificar sitios web"**
   - ✅ **"Confiar en esta CA para identificar usuarios de correo"**
9. Hacer clic en **"Aceptar"**

**Verificación 2.3:** En la lista de autoridades, buscar "PortSwigger". Debe aparecer "PortSwigger CA".

---

### Paso 2.4 — Configurar el proxy en Firefox

1. En Firefox, ir a **Configuración** → buscar "proxy"
2. Hacer clic en **"Configuración de la conexión..."**
3. Seleccionar **"Configuración manual del proxy"**
4. Completar:
   - Proxy HTTP: `127.0.0.1` | Puerto: `8080`
   - Marcar: ✅ **"Usar este proxy también para HTTPS"**
   - En "Sin proxy para": dejar vacío por ahora
5. Hacer clic en **"Aceptar"**

> [!IMPORTANT]
> **RECUERDA DESACTIVAR EL PROXY cuando termines de hacer pruebas.** Con el proxy activo, TODO el tráfico de Firefox pasa por Burp, incluyendo tu banca online y correo. Solo actívalo cuando estés haciendo pruebas de bug bounty.

**Verificación 2.4 — Test de HTTPS:**
1. Con Burp corriendo y el proxy activo en Firefox
2. Ir a **https://meesho.com**
3. La página debe cargar SIN mostrar error de certificado
4. En Burp → pestaña **"Proxy"** → **"HTTP History"** → debe aparecer el request a meesho.com

---

## 4. FASE 3 — Configurar el header X-Hackerone automático

**Por qué:** El programa de Meesho exige que todos los requests de prueba incluyan el header `X-Hackerone: tomas244`. Si olvidas incluirlo, tus pruebas pueden ser consideradas tráfico maliciario no autorizado.

**Solución:** Configurar Burp para que lo inyecte automáticamente en TODOS los requests hacia meesho.com y supplier.meesho.com, sin que tengas que recordarlo manualmente.

### Paso 3.1 — Configurar Match and Replace en Burp

Dentro de Burp Suite:
1. Ir a la pestaña **"Proxy"**
2. Ir a **"Proxy settings"**
3. Desplazarse hacia abajo hasta la sección **"Match and replace rules"**
4. Hacer clic en **"Add"** (o el botón `+`)
5. Completar el formulario:
   - **Type:** `Request header`
   - **Match:** (dejar vacío — significa "agregar siempre")
   - **Replace:** `X-Hackerone: tomas244`
   - **Comment:** `Header obligatorio programa Meesho`
6. Hacer clic en **"OK"** para guardar

**Verificación 3.1:**
1. Con la regla activa y el proxy de Firefox apuntando a Burp
2. Ir a **https://meesho.com** en Firefox
3. En Burp → **"Proxy"** → **"HTTP History"**
4. Hacer clic en cualquier request a meesho.com
5. En el panel de request (panel inferior izquierdo), verificar que aparece la línea:
   ```
   X-Hackerone: tomas244
   ```

Si el header aparece en el request: ✅ configuración correcta.

---

## 5. FASE 4 — Configurar el Scope (solo meesho.com)

**Por qué:** Burp registra TODO el tráfico que pasa por él. Si navegas por YouTube, Gmail, etc. con el proxy activo, Burp captura eso también. Configurar el scope limita la captura solo a los objetivos autorizados, y evita confusión y ruido.

### Paso 4.1 — Definir el scope en Burp

Dentro de Burp Suite:
1. Ir a la pestaña **"Target"**
2. Ir a la sub-pestaña **"Scope settings"** (o "Scope")
3. En la sección **"Include in scope"**, hacer clic en **"Add"**
4. Agregar la primera entrada:
   - **Protocol:** `https`
   - **Host or IP range:** `meesho.com`
   - **Port:** `443`
   - **File:** `.*` (cualquier ruta)
   - Hacer clic en **"OK"**
5. Agregar segunda entrada (hacer clic en **"Add"** de nuevo):
   - **Protocol:** `https`
   - **Host or IP range:** `*.meesho.com`
   - **Port:** `443`
   - **File:** `.*`
   - Hacer clic en **"OK"**
6. Agregar tercera entrada:
   - **Protocol:** `https`
   - **Host or IP range:** `supplier.meesho.com`
   - **Port:** `443`
   - **File:** `.*`
   - Hacer clic en **"OK"**

---

### Paso 4.2 — Activar filtro de scope en el historial

1. En **"Proxy"** → **"HTTP History"**
2. Hacer clic en el filtro de la parte superior (dice algo como "Filter: Hiding…")
3. Marcar: ✅ **"Show only in-scope items"**
4. Hacer clic en **"Apply"**

A partir de ahora, el historial solo mostrará tráfico de meesho.com.

**Verificación 4.2:**
1. Navegar a **https://meesho.com** en Firefox
2. Navegar a **https://google.com** en Firefox
3. En Burp → **"Proxy"** → **"HTTP History"**
4. Debe aparecer el request a meesho.com
5. NO debe aparecer ningún request a google.com

---

## 6. FASE 5 — Verificación completa del entorno

Antes de tocar el programa de Meesho, ejecutar esta checklist completa:

### ✅ Checklist de verificación final

```
□ 1. Burp Suite Community está instalado y abre sin errores
□ 2. El listener de Burp está activo en 127.0.0.1:8080
□ 3. Firefox tiene el certificado CA de Burp instalado (aparece PortSwigger en Autoridades)
□ 4. Firefox tiene el proxy configurado: 127.0.0.1:8080
□ 5. https://meesho.com carga SIN error de certificado con el proxy activo
□ 6. Los requests a meesho.com aparecen en Proxy > HTTP History
□ 7. Cada request a meesho.com incluye el header "X-Hackerone: tomas244"
□ 8. El scope está configurado: solo meesho.com y *.meesho.com en scope
□ 9. El filtro del historial está en "Show only in-scope items"
□ 10. Se puede iniciar sesión en meesho.com con número 6666666661 y OTP 999999
□ 11. Se puede iniciar sesión en supplier.meesho.com con suppliertest-1@meeshoai.com
```

**Si todos los ítems están marcados: el entorno está listo para iniciar pruebas.**

---

### Test de login completo (paso a paso)

**Para meesho.com:**
1. Firefox con proxy activo hacia Burp
2. Ir a https://meesho.com
3. Hacer clic en "Login" o "Sign In"
4. Ingresar número de móvil: `6666666661`
5. Cuando pida OTP: ingresar `999999`
6. Si falla: hacer clic en "Reenviar OTP" e ingresar `999999` de nuevo
7. **Verificar en Burp:** En HTTP History, los requests del login deben incluir `X-Hackerone: tomas244`

**Para supplier.meesho.com:**
1. En el mismo Firefox (con proxy activo)
2. Ir a https://supplier.meesho.com
3. Ingresar email: `suppliertest-1@meeshoai.com`
4. Ingresar contraseña: `Hackerone @123 $`
5. **Verificar en Burp:** El request de login debe incluir `X-Hackerone: tomas244`

---

## 7. Estado del Roadmap completo tras esta sesión

### Lo completado hasta hoy

| Etapa | Descripción | Estado |
|---|---|---|
| **Cuenta HackerOne** | Usuario: tomas244 | ✅ |
| **Método de pago** | PayPal configurado | ✅ |
| **Identity verification** | Se activa sola al primer reporte aceptado | ✅ (automático) |
| **Pipeline OCI Etapa 1-4** | Discovery + comparador + cron diario | ✅ |
| **Instalación Burp Suite** | Esta sesión | ← AQUÍ ESTAMOS |

### Las próximas sesiones en orden

| Sesión | Objetivo | Duración estimada |
|---|---|---|
| **Esta sesión** | Instalar y verificar Burp Suite | 45-60 min |
| **Próxima sesión A** | Exploración de meesho.com y supplier.meesho.com. Mapear todos los endpoints de la API navegando normalmente. No buscar bugs todavía. | 1 hora |
| **Próxima sesión B** | Primera búsqueda activa: Business Logic en supplier.meesho.com. Probar si suppliertest-1 puede ver datos de suppliertest-2. | 1-2 horas |
| **Sesión de pipeline** | Agregar meesho.com al objetivos.txt del pipeline OCI. Monitoreo pasivo automático. | 30 min |

### Regla de oro que aplica aquí también
> No iniciar la exploración activa hasta que los 11 puntos de la checklist estén marcados.

---

## APÉNDICE: Referencia rápida de credenciales

> [!CAUTION]
> No compartir esto con nadie. No guardar en sistemas cloud no cifrados.

```
USERNAME H1:         tomas244
HEADER OBLIGATORIO:  X-Hackerone: tomas244
EMAIL ALIAS H1:      tomas244@wearehackerone.com

--- MEESHO WEB / APP ---
Número 1: 6666666661  OTP: 999999
Número 2: 6666666662  OTP: 999999

--- SUPPLIER PANEL ---
User 1: suppliertest-1@meeshoai.com  Pass: Hackerone @123 $
User 2: suppliertest-2@meeshoai.com  Pass: Hackerone @123 $

--- CONTACTO MEESHO ---
Solo por HackerOne (NUNCA por email directo)
Email conocido: security@meesho.com (solo referencia, NO usar)
```

---

*Documento generado el 2026-07-06. Verificar estado del entorno al inicio de cada sesión de pruebas.*
