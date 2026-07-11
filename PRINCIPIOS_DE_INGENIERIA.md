# PRINCIPIOS DE INGENIERÍA DEL LABORATORIO

Estos principios aplican a cualquier IA que participe en el desarrollo del laboratorio.

## 1. La realidad tiene prioridad

Nunca asumir que una conversación representa el estado actual del proyecto.

Siempre verificar.

## 2. Fuente de verdad

Orden de prioridad:

1. Sistema de archivos.
2. Git.
3. Configuración efectiva.
4. Logs.
5. Documentación.
6. Conversaciones.

## 3. Auditoría antes que desarrollo

Antes de escribir código:

- inspeccionar
- comprender
- documentar

Después desarrollar.

## 4. Complejidad incremental

No agregar componentes que todavía no sean necesarios.

Resolver primero el problema actual.

## 5. Un único objetivo funcional

Cada etapa debe producir una mejora funcional verificable.

No comenzar la siguiente etapa hasta finalizar la actual.

## 6. IA bajo demanda

No utilizar modelos de IA si un proceso determinístico puede resolver la tarea.

La IA solo participa cuando agrega valor.

## 7. Optimización de recursos

Minimizar:

- CPU
- RAM
- llamadas a APIs
- consumo de cuotas gratuitas

## 8. Documentación continua

Cada cambio importante deberá reflejarse en la documentación del laboratorio.

## 9. No destruir información

Nunca eliminar componentes automáticamente.

Ante dudas:

- documentar
- informar
- esperar confirmación.

## 10. El laboratorio es un sistema

Todos los proyectos deben integrarse de forma coherente.

Las decisiones locales nunca deben perjudicar la arquitectura global.

## 11. Estrategia de Modelos y Gestión de Cuotas

Para optimizar costos, tokens y evitar la degradación del razonamiento ante límites de cuota (como el de Claude Sonnet 4.6), se establece el siguiente protocolo de selección de modelos:

### Roles y Selección de Modelos

| Modelo | Nivel | Caso de Uso Óptimo |
| :--- | :--- | :--- |
| **Gemini 3.5 Flash** | Medium / High | Tareas de código estándar, refactorizaciones simples, scripts de soporte, Git, y documentación técnica. |
| **Gemini 3.1 Pro** | Low / High | Análisis lógico, arquitectura de sistemas, diseño de pipelines y lógica de negocio. |
| **Claude Sonnet 4.6 (Thinking)** | ⭐ Máximo | Exclusivo para auditorías complejas de Bug Bounty, análisis de exploits complejos y redacción final de reportes de vulnerabilidades. |

### Tácticas de Trabajo para Evitar Delirios y Ahorrar Tokens

1. **Aislamiento de Tareas (Unidad de Trabajo Mínima)**:
   * Desarrollar código mediante funciones cortas e individuales. Evitar solicitar scripts completos de golpe.
   * Probar localmente cada componente antes de pasar al siguiente.
2. **Contexto Estricto y Acotado**:
   * No cargar archivos extensos innecesarios en la ventana de contexto.
   * Proveer solo las líneas de código que necesitan ser modificadas.
3. **Uso de Herramientas Deterministas**:
   * Utilizar la compilación y validación local de sintaxis (`py_compile`, tests unitarios) en lugar de pedirle a la IA análisis predictivos del código.
4. **Escalamiento de Modelos**:
   * Iniciar la tarea utilizando **Gemini 3.5 Flash**.
   * Si la tarea presenta fallos de lógica o bucles de error tras 2 reintentos, pasar a **Gemini 3.1 Pro**.
   * Reservar **Claude Sonnet** solo para el 5% de tareas críticas que requieran razonamiento avanzado de seguridad.
