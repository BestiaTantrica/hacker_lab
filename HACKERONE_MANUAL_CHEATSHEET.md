# Ayuda Memoria: Proceso Semi-Manual de Envío en HackerOne

Este documento detalla los pasos finales obligatorios (manuales) que se deben seguir tras presionar el botón `[🚀 Abrir e Inyectar en HackerOne]` desde el C2 Panel, para garantizar que el reporte formal redactado por la IA se envíe correctamente.

## 1. Verificación Inicial en la Pantalla de H1
Al abrirse la pestaña de HackerOne:
- **El reporte ya debe estar en tu portapapeles.** (El botón del panel lo copia automáticamente).
- Estarás en la página oficial del programa correspondiente (ej. `hackerone.com/shopify/reports/new`).

## 2. Paso a Paso en el Formulario

### A. Asset (Activo)
- Usa el buscador **"Select the attack surface of this issue"**.
- Selecciona el dominio exacto o la opción Wildcard (`*.empresa.com`) que coincida con nuestro target.
- *Nota:* Asegúrate de que el asset elegido tenga la etiqueta "Eligible for bounty".

### B. Weakness (Debilidad / CWE)
- Usa el buscador **"Select the type of the potential issue"**.
- Busca la debilidad correspondiente (ej. `Information Disclosure` para archivos OpenAPI, o `Improper Access Control` para Takeovers).
- *Nota:* Los analistas corrigen esta categoría durante el triaje, por lo que una aproximación razonable es suficiente.

### C. Severity (Gravedad)
- Selecciona la opción **"Submit report with severity"** (si aplica y la conoces) o **"Submit report without severity"** (recomendado para Information Disclosure, dejando que el equipo interno lo calcule).

### D. Título y Descripción
- **Title:** El portapapeles pegará el reporte completo. **Corta** la primera línea que dice `## Title: ...` y pégala en el recuadro pequeño **"Title *"**.
- **Description:** 
  1. Haz clic en la caja grande blanca.
  2. El resto del reporte ya debería estar pegado ahí, estructurado perfectamente con los bloques `## Summary:`, `## Steps To Reproduce:`, `## Supporting Material/References:`, `## Likelihood:`, `## Impact:`, y `## Remediation Guidance:`.
  3. **¡MUY IMPORTANTE! Limpieza:**
     - El reporte generado por el C2 Panel incluye TODAS las secciones recomendadas. **Esto sobrescribe cualquier plantilla predeterminada de la empresa**, asegurando que entregamos la información más completa posible (Over-Delivered).
     - Si la empresa tenía una plantilla por defecto en la caja (ej. "Shops Used to Test"), **bórrala**. Tu reporte debe ser el único texto en la caja.

### E. Falsos Positivos de la Interfaz
- A veces, HackerOne lee la evidencia (ej. `x-frame-options: SAMEORIGIN`) y lanza advertencias amarillas: *"Parece que estás a punto de enviar un informe de clickjacking..."*.
- **Ignóralas con confianza.** Marca la casilla *"Entiendo que enviar este informe podría afectar mis puntos de reputación"* y continúa. Es un robot básico leyendo logs; los analistas humanos leerán tu excelente `## Summary`.

### F. Evidencias Adjuntas (Imágenes/Videos)
- **Vulnerabilidades de Infraestructura (Takeovers, CORS, S3 Leaks, OpenAPI):** No se requieren imágenes. El bloque de código con los comandos HTTP reales (inyectado desde OCI-1) es la prueba de oro definitiva.
- **Vulnerabilidades Lógicas/Web (XSS, IDOR):** Sí requieren videos o capturas para demostrar el impacto visual. (Se automatizará en el futuro).

## 3. Advertencias de la Plataforma
- **Carteles de "ALTO - Su informe de XSS será N/A":** 
  - Son alertas automáticas genéricas. 
  - Si nuestro reporte **NO es un XSS** (como el Takeover), ignóralo marcando la casilla *"Entiendo que enviar este informe..."*. El sistema lo muestra a veces solo porque detectó la palabra "XSS" en nuestro texto de impacto.

## 4. Envío Final
- Haz clic en **Submit Report** (Enviar Informe).
- Verifica que la pantalla siguiente indique que el reporte está en estado **Nuevo (Abierto)**.
