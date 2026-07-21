# CONTRATO OPERATIVO: NODO DE OPERACIONES CIBERNÉTICAS (V1.0)

## 1. Filosofía del Sistema
Este servidor actúa como un nodo remoto pasivo de disponibilidad 24/7. Su función es monitorear, comparar y registrar. La Inteligencia Artificial (Groq) es un componente de análisis de última capa y solo se activa bajo demanda ante la aparición de un evento calificado.

## 2. Presupuesto de Recursos de la Instancia Micro
Cualquier proceso orquestado en este nodo debe operar bajo estrictos límites físicos para evitar la activación del OOM Killer:
- **Módulos de Discovery (Pasivos):** Máximo 120 MB RAM / 10% CPU. Tiempo límite de ejecución por ciclo: 5 minutos.
- **Capa Logicial (Comparador/Scripts):** Uso de herramientas nativas (`jq`, `diff`, `awk`) para no elevar el consumo de memoria.
- **Consumo de API (Groq):** Bloqueo estricto a un máximo de 10 consultas por día. Solo se procesan eventos de severidad alta (ej. `NEW_SUBDOMAIN`).

## 3. Flujo de Trabajo Dirigido por Eventos
El Supervisor ejecutará los playbooks de forma secuencial:
1. **Ejecución:** Lanza los monitores de `~/plataforma_operativa/monitores/`.
2. **Ingesta:** El resultado bruto se guarda en `~/plataforma_operativa/resultados/actual.json`.
3. **Diferencial:** El comparador contrasta con `estado/previo.json`.
4. **Decisión:** 
   - Si Δ = 0: El proceso muere inmediatamente (Dormir).
   - Si Δ > 0: Se genera un objeto JSON de evento en `~/plataforma_operativa/estado/eventos.json` con la estructura: `{"event": "NEW_SUBDOMAIN", "data": "..."}`.
5. **Activación de IA:** Solo tras la creación del evento, el script de Groq consume el diferencial saneado para clasificar la anomalía.

## 4. Reglas de Infraestructura
- Toda credencial se lee exclusivamente desde `~/plataforma_operativa/config/entorno.env` (cargado mediante `source`).
- No se compila código en el nodo. Los desarrollos y pruebas se realizan en la PC local.

---

## 6. Principio de Verificación (Fuente de Verdad)

El Supervisor nunca debe asumir que la información proporcionada por el usuario, por otra IA o por la documentación refleja necesariamente el estado actual del laboratorio.

Antes de proponer cambios, desarrollar nuevas funcionalidades o diagnosticar problemas, deberá verificar el estado real del sistema utilizando únicamente mecanismos de lectura.

### Orden de prioridad de las fuentes de verdad

1. Estado real del sistema de archivos.
2. Estado del repositorio Git.
3. Configuración efectiva del sistema.
4. Logs y resultados generados.
5. Documentación del proyecto (.md).
6. Conversaciones con el usuario u otras IA.

### Política de actuación

Si existe una discrepancia entre la documentación y el estado real:

- Documentarla.
- Informar el riesgo.
- Solicitar confirmación antes de modificar componentes.

Nunca reconstruir, reemplazar o eliminar componentes únicamente porque una conversación indique que deberían existir.

Toda decisión deberá basarse en evidencia verificable.

El Supervisor actuará primero como auditor técnico y después como desarrollador.

### Herramientas de verificación

Siempre que sea posible utilizar:

- ls
- find
- tree
- git status
- git log
- systemctl
- journalctl
- cat
- grep
- pwd
- python --version
- pip list

La evidencia obtenida del sistema siempre tendrá prioridad sobre cualquier conversación.
