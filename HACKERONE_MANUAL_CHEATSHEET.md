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
- Si es un Subdomain Takeover y no aparece, busca y selecciona:
  - `Improper Access Control - Generic (CWE-284)`
  - o `Security Misconfiguration`
- *Nota:* Los analistas corrigen esta categoría durante el triaje, por lo que una aproximación razonable es suficiente.

### C. Severity (Gravedad)
- Selecciona la opción **"Submit report with severity"**.
- En la calculadora CVSS o selector rápido, elige la criticidad acorde (ej. **High** para Subdomain Takeovers).
- Si la calculadora CVSS es muy compleja, simplemente selecciona "Submit report without severity" y deja que el equipo interno lo calcule.

### D. Título y Descripción (Proof of Concept)
- **Title:** Copia el título generado por la IA (ej. `Subdomain Takeover on dev-staging.shopify.com via Unclaimed AWS S3 Bucket`) y pégalo en el recuadro pequeño **"Title *"**.
- **Description:** 
  1. Haz clic en la caja grande blanca.
  2. Presiona `Ctrl + V` para pegar el reporte completo de la IA.
  3. **¡MUY IMPORTANTE! Limpieza:**
     - Si aparece texto basura al principio (ej. `## Summary: [add sum##`), **bórralo**. El reporte debe empezar limpio.
     - Ve al fondo de la caja de descripción y **borra TODA la plantilla predeterminada de la empresa** (ej. "Shops Used to Test", "Relevant Request IDs"). Tu reporte debe terminar exactamente donde termina nuestra sección de "Evidence / PoC".

### E. Impact (Impacto)
- Algunas empresas tienen una caja separada al final obligatoria llamada **"Impact *"**.
- Si existe, corta el texto debajo de nuestro título `## Impact:` en la descripción principal y pégalo allí.

### F. Evidencias Adjuntas (Imágenes/Videos)
- **Vulnerabilidades de Infraestructura (Takeovers, CORS, S3 Leaks):** No se requieren imágenes. El texto con los comandos (`curl`, `dig`) es superior y más rápido para el analista.
- **Vulnerabilidades Lógicas/Web (XSS, IDOR):** Sí requieren videos o capturas para demostrar el impacto visual. (Se automatizará en el futuro).

## 3. Advertencias de la Plataforma
- **Carteles de "ALTO - Su informe de XSS será N/A":** 
  - Son alertas automáticas genéricas. 
  - Si nuestro reporte **NO es un XSS** (como el Takeover), ignóralo marcando la casilla *"Entiendo que enviar este informe..."*. El sistema lo muestra a veces solo porque detectó la palabra "XSS" en nuestro texto de impacto.

## 4. Envío Final
- Haz clic en **Submit Report** (Enviar Informe).
- Verifica que la pantalla siguiente indique que el reporte está en estado **Nuevo (Abierto)**.
