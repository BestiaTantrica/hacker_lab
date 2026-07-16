# DIRECTRICES DEL AGENTE IA (ANTIGRAVITY / CLAUDE)
> **ESTRICTO CUMPLIMIENTO:** Leer esto al inicio de cualquier sesión de resolución de problemas para evitar los errores del pasado.

## 1. El Ecosistema Actual (NO INVENTAR RUEDAS NUEVAS)
El usuario **ya construyó soluciones** para los cuellos de botella de Burp Suite. Antes de sugerir pruebas manuales o herramientas externas, verificar y usar los siguientes "eslabones" existentes en `LAB/api/`:
- **`parseador_burp.py`**: Parsea un archivo `trafico_burp.xml` gigante de forma incremental y saca un JSON con todos los endpoints, anomalías y parámetros de interés. *Este es el reemplazo de la revisión manual.*
- **`auditar_vectores.py`**: Automatiza las pruebas de IDOR y CORS (Vectores 4, 5 y 6) en MongoDB cruzando credenciales de Cuenta A y Cuenta B. 
- **`analizador_ia.py`**: Pasa el delta de subdominios por Groq para que la IA priorice los 5 mejores.

## 2. Gestión del Espacio de Trabajo (No desordenar)
- `/LAB/`: Es el core del proyecto (`ARQUITECTURA_PIPELINE.md`, `CONTEXTO_ACTIVO.md`).
- `/LAB/herramientas/`: Contiene el binario de subfinder, dnsx, httpx, nuclei y la `plataforma_operativa`.
- `/portafolio-ciberseguridad/`: **SOLO DOCUMENTACIÓN ACADÉMICA**. 

## 3. Sistema de "Skills" (`LAB/skills/`)
Son guías/prompts creadas por el usuario para usarlas cuando **no tiene créditos de IA (Claude/Opus)**. No son código que "falla" técnicamente, sino directrices para su análisis mental. No las borres ni las critiques, son su salvavidas offline.

## 4. Flujo del Laboratorio (Pipeline OCI)
`discovery_pasivo.py` → `comparador.py` (saca deltas) → `analizador_ia.py` (filtra top 5) → `notificador.py` (Telegram).
*La IA en OCI es un asesor pasivo, no debe usarse para procesar logs crudos, para eso usamos `httpx` y `nuclei` (ya instalados en `/LAB/herramientas/bin/`).*
