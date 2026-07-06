# 🛠️ KIT DE DELEGACIÓN PARA IAS LIBRES: MONITOREO Y DELTAS EN OCI

Este documento está diseñado para que puedas utilizar **modelos de IA gratuitos (ChatGPT, Gemini Web o Claude Free)** para avanzar y terminar el ciclo completo de monitoreo pasivo en tu servidor de Oracle Cloud (OCI). 

Dado que estas IAs web no tienen acceso directo a tus archivos ni a tu servidor, este kit les proporciona **todo el contexto necesario, el código de partida y los requisitos de diseño** para que te generen el código exacto y funcional a la primera.

También incluye una **guía paso a paso extremadamente detallada** para que sepas exactamente qué carpetas abrir, qué archivos crear, qué comandos ejecutar y cómo poner todo en marcha sin cometer errores.

---

## 📌 PARTE 1: AUDITORÍA DE ESTADO Y ARQUITECTURA
Actualmente, tu infraestructura de ciberseguridad se divide en dos entornos:
1. **Nodo Local (Tu PC):** Donde programas y tienes la documentación.
2. **Nodo Remoto (Servidor OCI - Oracle Cloud):** Una instancia virtual gratuita con Ubuntu 24.04, 1 GB de RAM y 2 GB de SWAP. Su IP pública es `129.80.73.248`.

### Flujo de Trabajo del Ciclo de Monitoreo:
```text
+-------------------------------------------------------------+
|                  NODO ORACLE CLOUD (OCI)                    |
|                                                             |
|  [cron] (Cada 24h)                                          |
|    │                                                        |
|    ├──> 1. [ discovery_pasivo.py ]                          |
|    │       Consulta crt.sh (APIs públicas de certificados)  |
|    │       Genera: resultados/actual.json                   |
|    │                                                        |
|    └──> 2. [ comparador.py ]                                |
|            Compara: resultados/actual.json                  |
|                      vs estado/previo.json                  |
|            ¿Hay activos nuevos (Delta Δ)?                   |
|              ├── [NO] -> Termina silenciosamente            |
|              └── [SÍ] -> Genera resultados/delta_*.json     |
|                           -> (Opcional) Llama a Groq/Gemini  |
+-------------------------------------------------------------+
```

### Rutas de Archivos Clave en OCI:
- Directorio raíz del proyecto: `~/plataforma_operativa`
- Configuraciones y tokens: `~/plataforma_operativa/config/entorno.env` (aquí están tus API Keys).
- Objetivos de búsqueda: `~/plataforma_operativa/config/objetivos.txt` (aquí pones los dominios, ej: `starbucks.com`).
- Entorno Virtual de Python: `~/workspace_lab/venv` (aislado de la máquina para no romper nada).

---

## 📖 PARTE 2: GUÍA PASO A PASO PARA EL USUARIO (¿Cómo operar en OCI?)

Sigue estas instrucciones al pie de la letra. No necesitas tener conocimientos previos de terminal.

### Paso 1: Abrir la terminal y conectarte al servidor OCI
1. En tu computadora local (PC), abre la aplicación **Terminal** (o Consola).
2. Para conectarte a tu servidor de Oracle Cloud por SSH, escribe el siguiente comando y presiona `Enter`:
   ```bash
   ssh -i ~/.ssh/id_rsa ubuntu@129.80.73.248
   ```
3. Si te pregunta algo sobre "authenticity of host" y si deseas continuar, escribe `yes` y presiona `Enter`.
4. Una vez dentro, verás que el texto de la consola cambia a algo como `ubuntu@lab-cybersec-micro:~$`. Ya estás dentro de tu servidor.

### Paso 2: Navegar a la carpeta del proyecto
1. Para ingresar al directorio donde vive el sistema de monitoreo, ejecuta:
   ```bash
   cd ~/plataforma_operativa
   ```
2. Para ver qué carpetas y archivos existen actualmente allí, ejecuta:
   ```bash
   ls -la
   ```
   Deberías ver carpetas como `config`, `monitores`, `resultados`, `estado` y `logs`.

### Paso 3: ¿Cómo crear o editar archivos usando `nano`?
`nano` es un editor de texto muy sencillo dentro de la terminal. Lo usaremos para crear o modificar los scripts que te devuelvan las IAs.
1. Para abrir un archivo (nuevo o existente), escribe:
   ```bash
   nano ruta/al/archivo.py
   ```
   *Ejemplo para el comparador:* `nano monitores/comparador.py`
2. Se abrirá una pantalla azul/grisácea donde puedes escribir.
3. **Copiar y Pegar:** Copia el código que te genere la IA web. En la terminal de Linux, para pegar usualmente debes hacer **Clic Derecho -> Pegar** o presionar `Ctrl + Shift + V` (en Windows/Linux).
4. **Guardar los cambios:**
   - Presiona `Ctrl + O` (guardar).
   - Presiona `Enter` para confirmar el nombre del archivo.
5. **Salir del editor:**
   - Presiona `Ctrl + X`. Si hiciste cambios y no guardaste, te preguntará si deseas guardar (`Y` para sí, `N` para no).

### Paso 4: ¿Cómo probar manualmente un script dentro del entorno virtual?
Para no romper el sistema y usar las librerías correctas, debemos ejecutar los scripts utilizando el ejecutable de Python del entorno virtual (`venv`):
1. Para ejecutar el script de discovery de forma manual:
   ```bash
   ~/workspace_lab/venv/bin/python monitores/discovery_pasivo.py
   ```
2. Para verificar que generó el archivo de resultados:
   ```bash
   cat resultados/actual.json
   ```

---

## 🤖 PARTE 3: MASTER PROMPTS PARA IAS WEB (Copiar y Pegar)

> [!TIP]
> **Recomendación de Modelo:** 
> - Usa **ChatGPT (GPT-4o)** o **Claude 3.5 Sonnet (Free)** para generar el código de Python y Bash, ya que son excelentes estructurando scripts limpios y manejando errores.
> - Usa **Gemini (1.5 Pro o 2.5 Flash)** si deseas analizar problemas de red, logs extensos o límites de APIs.

---

### 📋 MASTER PROMPT 1: Optimizar `discovery_pasivo.py` (Etapa 1)
**Instrucciones:** Copia el siguiente bloque de texto completo y pégalo en la IA web de tu elección.

```text
Actúa como un programador senior de Python experto en automatización y ciberseguridad.
Necesito optimizar y robustecer un script existente llamado `discovery_pasivo.py` que corre en una instancia Always Free de Oracle Cloud (Ubuntu, 1 GB RAM). El script debe extraer subdominios utilizando la API pública de crt.sh de forma pasiva.

CONTEXTO Y REQUISITOS DEL SCRIPT:
1. Rutas del Entorno (deben ser dinámicas o expandir el directorio home de forma segura usando os.path.expanduser):
   - Archivo de objetivos (lectura): ~/plataforma_operativa/config/objetivos.txt (contiene un dominio por línea, ej: starbucks.com).
   - Archivo de salida (escritura): ~/plataforma_operativa/resultados/actual.json
   - Archivo de log (escritura): ~/plataforma_operativa/logs/discovery.log
2. Robustez y Control de Errores:
   - crt.sh frecuentemente sufre timeouts o devuelve respuestas vacías (cuerpo vacío) cuando se le consulta por dominios grandes. El script NO debe fallar silenciosamente ni lanzar excepciones no controladas (como JSONDecodeError).
   - Si la petición HTTP falla o da timeout, debe registrarse detalladamente en el log y reintentar la llamada hasta 3 veces con una espera progresiva (backoff de 5s, 10s, 15s).
   - Si tras los reintentos sigue fallando, debe guardar en el log el error y no sobreescribir resultados/actual.json con datos corruptos o vacíos, preservando la última ejecución válida.
3. Estructura de Salida (JSON):
   Debe guardar un JSON con este formato exacto:
   {
     "timestamp": "2026-07-04T20:30:00Z",
     "dominios": {
       "ejemplo.com": ["sub1.ejemplo.com", "sub2.ejemplo.com"],
       "otro.com": []
     }
   }
   *Nota:* Debe limpiar los subdominios eliminando comodines (*.) y duplicados.
4. Logging profesional:
   - Usa el módulo standard `logging` de Python.
   - Debe registrar cuándo inicia el script, qué dominio está procesando, cuántos subdominios encontró, si hubo timeouts/errores de red, y cuándo finalizó.
5. Cero Dependencias:
   - Usa la biblioteca estándar 'urllib.request' y 'json' para evitar instalar dependencias de terceros (como requests).

Escribe el código completo de `discovery_pasivo.py` bien estructurado, modularizado y documentado.
```

---

### ⚖️ MASTER PROMPT 2: Crear el Comparador de Deltas `comparador.py` (Etapa 2)
**Instrucciones:** Copia el siguiente bloque de texto completo y pégalo en la IA web de tu elección.

```text
Actúa como un programador senior de Python. Necesito que escribas un script llamado `comparador.py` para un pipeline de monitoreo pasivo de activos en ciberseguridad. El script correrá en OCI (Oracle Cloud) y su función es identificar qué activos (subdominios) son NUEVOS en comparación con la última ejecución.

REQUISITOS DEL SCRIPT:
1. Ubicación del Script: ~/plataforma_operativa/monitores/comparador.py
2. Rutas del Sistema (usa os.path.expanduser para expandir ~ de forma segura):
   - Entrada actual: ~/plataforma_operativa/resultados/actual.json
   - Histórico previo: ~/plataforma_operativa/estado/previo.json
   - Salida del Delta (si hay cambios): ~/plataforma_operativa/resultados/delta_YYYY-MM-DD.json (reemplaza YYYY-MM-DD con la fecha actual).
   - Logs: ~/plataforma_operativa/logs/comparador.log
3. Lógica de Comparación:
   - Lee `actual.json` y `previo.json`. Ambos tienen la misma estructura JSON:
     {
       "timestamp": "...",
       "dominios": {
         "dominio.com": ["sub1.dominio.com", "sub2.dominio.com"]
       }
     }
   - Compara la lista de subdominios de cada dominio. Identifica si hay subdominios NUEVOS (que están en actual.json pero no en previo.json).
   - Si no existe el archivo `previo.json` (primera ejecución), debe tratar a TODOS los subdominios actuales como nuevos, generar el delta correspondiente y salir con éxito.
4. Salida Condicional (Delta):
   - Si NO hay subdominios nuevos (Delta = 0), el script debe terminar de forma silenciosa (código de salida 0) y escribir únicamente una línea en `comparador.log` indicando "Sin cambios detectados". No debe generar ningún archivo delta.json.
   - Si SÍ hay subdominios nuevos, debe generar el archivo `delta_YYYY-MM-DD.json` con la lista de activos nuevos y registrarlo en el log indicando cuántos nuevos se descubrieron.
     Formato de delta_*.json:
     {
       "timestamp": "2026-07-04T21:00:00Z",
       "nuevos_activos": {
         "dominio.com": ["nuevo1.dominio.com"]
       }
     }
5. Cero Dependencias:
   - Utiliza exclusivamente librerías estándar de Python (json, os, sys, datetime, logging).

Escribe el código completo de `comparador.py` robusto, limpio y listo para producción.
```

---

### ⏰ MASTER PROMPT 3: Orquestador Bash y Cronjob (Etapa 3 y 4)
**Instrucciones:** Copia el siguiente bloque de texto completo y pégalo en la IA web de tu elección.

```text
Actúa como un administrador de sistemas Linux y experto en automatización en Bash.
Necesito crear un script orquestador en Bash llamado `run_pipeline.sh` que ejecute de forma secuencial y segura nuestro pipeline de descubrimiento de subdominios en un servidor OCI.

REQUISITOS DEL ORQUESTADOR:
1. Ubicación del script: ~/plataforma_operativa/run_pipeline.sh
2. Flujo de ejecución secuencial:
   a. Cargar las variables de entorno si existe el archivo ~/plataforma_operativa/config/entorno.env.
   b. Activar el entorno virtual de Python en ~/workspace_lab/venv/bin/activate.
   c. Ejecutar el discovery pasivo:
      ~/workspace_lab/venv/bin/python ~/plataforma_operativa/monitores/discovery_pasivo.py
   d. Si el discovery falla (código de retorno diferente de 0), registrar el error en logs/pipeline.log y abortar.
   e. Si el discovery tiene éxito, ejecutar el comparador:
      ~/workspace_lab/venv/bin/python ~/plataforma_operativa/monitores/comparador.py
   f. Si el comparador tiene éxito:
      - Si se generó un nuevo delta (detectando la presencia de un archivo resultados/delta_*.json):
        - Rotar los estados: copiar resultados/actual.json a estado/previo.json para la próxima comparación.
        - Opcional/Futuro: Registrar en el log que se detectaron deltas y que están listos para análisis.
      - Si no se generó delta (salida silenciosa):
        - Copiar de todos modos resultados/actual.json a estado/previo.json para asegurar que el estado está al día.
3. Permisos de ejecución:
   - Explicar detalladamente qué comando usar para darle permisos de ejecución al script (`chmod +x`).
4. Programación en Cron:
   - Generar la línea exacta para agregar al crontab del usuario (`crontab -e`) para que este orquestador corra automáticamente todos los días a las 6:00 AM.
   - Asegurarse de redirigir la salida estándar y de error a un archivo logs/cron_output.log para diagnosticar problemas futuros.

Escribe el script completo `run_pipeline.sh` con manejo de errores, comentarios explicativos paso a paso y la guía para configurar el Cronjob.
```

---

## 🔮 FASE FUTURA: INTEGRACIÓN CON LA API DE IA LOCAL (Groq/Gemini)

Una vez que tengas funcionando las Etapas 1 a 4 con las IAs libres, puedes avanzar a la **Etapa 5 (Análisis Automático con IA)**. En tu carpeta `/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api` ya tienes un cliente listo (`llm_client.py`) que usa de forma gratuita las APIs de Groq y Gemini con un sistema de fallback automático. 

El comparador o el orquestador podrá invocar este cliente para analizar **únicamente** los subdominios listados en `delta_*.json`, ahorrando tokens y permitiéndote obtener un análisis de seguridad al instante sin costo alguno.

*¡Copia los prompts de arriba en ChatGPT, Gemini o Claude Web para obtener tus archivos de código y sigue el paso a paso para desplegarlos en tu terminal!*
