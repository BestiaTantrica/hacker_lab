# 📐 ARQUITECTURA DE LA PLATAFORMA DE OPERACIONES

## 🔌 1. Mapa de Flujo de Información (Diagrama ASCII)

El siguiente diagrama detalla cómo se interconectan los nodos, cómo se gestiona el código y cómo fluye la información operativa desde la recolección pasiva hasta el análisis con IA.

```text
+---------------------------------------------------------+
|                  NODO LOCAL (PC)                        |
|                                                         |
|  [ network-toolkit ]      [ caso fuerza bruta btc ]     |
|   Diagnóstico de Red       Análisis Forense wallet.dat  |
|          |                                              |
|          +------------+                                 |
|                       v                                 |
|             [ portafolio-cybersec ]                     |
|               Repositorio Local                         |
+-----------------------|---------------------------------+
                        | (git push)
                        v
+---------------------------------------------------------+
|                     GIT / GITHUB                        |
|                                                         |
|             Control de versiones remoto                 |
+-----------------------|---------------------------------+
                        | (git pull / deploy)
                        v
+---------------------------------------------------------+
|                NODO ORACLE CLOUD (OCI)                  |
|                                                         |
|  ~/plataforma_operativa                                 |
|    |                                                    |
|    +--> [ monitores/discovery_pasivo.py ] <---+ (Cron)  |
|                   |                           |         |
|                   v                           |         |
|         Genera: [ resultados/nuevo.json ]     |         |
|                   |                           |         |
|                   v                           |         |
|         [ comparador.py ] (Etapa 2) <---------+         |
|           Compara: nuevo.json vs anterior.json          |
|                   |                                     |
|                   +---> ¿Hay Cambios (Delta Δ)?         |
|                               |                         |
|                      [NO]     | [SÍ]                    |
|                       |       v                         |
|                       |     Invocar: [ IA - Groq ]      |
|                       |     (Analiza SOLO el Delta)     |
|                       |       |                         |
|                       v       v                         |
|              +--------------------------+               |
|              |  [ resultados/logs/ ]    |               |
|              |  Historial & Diagnóstico |               |
|              +--------------------------+               |
+---------------------------------------------------------+
```

---

## 🔄 2. Flujo de Datos Técnico

1. **Planificación y Código (Nodo Local):**
   El código de la plataforma se desarrolla y prueba localmente en el PC del usuario. Se gestiona bajo control de versiones con Git y se sincroniza con el repositorio remoto.
2. **Despliegue (Nodo Oracle):**
   El Nodo Oracle descarga las actualizaciones del código. La infraestructura utiliza un entorno virtual aislado de Python (`~/workspace_lab/venv/`) para ejecutar los procesos.
3. **Recolección Pasiva (Discovery):**
   Un script de Python (`discovery_pasivo.py`), ejecutado periódicamente mediante tareas programadas de sistema (`cron`), realiza consultas no intrusivas a APIs públicas de certificados (ej. `crt.sh`) para extraer subdominios y activos de un alcance de HackerOne. Los resultados se guardan en un archivo estructurado en JSON.
4. **Cálculo de Delta (Comparador):**
   El comparador procesa el archivo JSON recién generado contra el registro histórico anterior.
   - Si **no hay cambios**, el proceso termina silenciosamente para ahorrar procesamiento y cuota de red.
   - Si **se detectan nuevos activos (Delta)**, se registra el hallazgo en el histórico y se pasa el delta a la siguiente fase.
5. **Enriquecimiento Inteligente (IA - Groq):**
   La API de Groq es invocada **únicamente** si se detectan deltas reales. Analiza el tipo de activo descubierto (ej. subdominio con patrón de desarrollo, panel administrativo expuesto) y genera una alerta estructurada.
6. **Registro e Historial:**
   Se escriben los logs en `~/plataforma_operativa/logs/` y se actualiza el archivo maestro de activos.

---

## 🔒 3. Políticas y Restricciones de Diseño

- **Fricción Cero de Procesamiento:** La CPU y la RAM de la instancia Always Free de Oracle (1 GB RAM) no deben saturarse. Queda prohibida la ejecución de escaneos masivos activos directos (como `nmap` de puertos completos o fuerza bruta agresiva de directorios).
- **Control de Costos y Cuotas:** El uso de la IA está condicionado al cálculo previo del Delta. Bajo ninguna circunstancia se debe enviar la base de datos completa de activos a la API en cada ejecución, limitando las solicitudes exclusivamente a nuevos descubrimientos.
- **Aislamiento de Entorno:** Todos los scripts de Python en la nube deben ejecutarse dentro del entorno virtual (`~/workspace_lab/venv/bin/python`) para evitar colisiones con librerías globales de la instancia.
