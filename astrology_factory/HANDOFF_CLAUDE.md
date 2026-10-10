Eres Claude, asumiendo el rol de IA de NIVEL 3 (Arquitectura Profunda) en el proyecto "Astrology Factory".
Tu tarea de hoy es saldar la deuda técnica de las **TAREAS 1 y 2 de la Bitácora Global** simultáneamente.

### 📌 CONTEXTO DEL PROBLEMA
El proyecto está transicionando a una Arquitectura V2, donde una Base de Datos SQLite (`assets_visuales.db`) creada por `v2/db_visual.py` debe ser la única fuente de la verdad para el stock visual.
Sin embargo, el renderizador final `content_factory/video_maker.py` sigue actuando como un monolito: usa `glob` para buscar archivos en crudo, aplica algoritmos de matching heurísticos muy costosos (`score_file_v2`) y pre-procesa el contenido duplicando archivos temporalmente.

### 🎯 TU MISIÓN (DOBLE REFACTORIZACIÓN)

#### 1. Consolidar el Pipeline Semántico en la Célula 2 (nodriza_visual.py)
Actualmente, `nodriza_visual.py` "transmuta" (convierte JPGs a MP4 usando FFmpeg) antes de pasarlos al motor. **ESTO SE DEBE ELIMINAR.**
*   **Modifica** `v2/celula_2/nodriza_visual.py` para que sus consultas semánticas consuman 100% de `db_visual.py` (usando etiquetas guardadas allí por el auditor).
*   **Elimina** la función `transmutar_imagen_a_video` o cualquier lógica que genere MP4 temporales a partir de imágenes estáticas previas al ensamble. La Célula 2 debe simplemente inyectar la ruta absoluta del JPG original en la `lista_de_corte_<evento_id>.json`.

#### 2. Desacoplamiento y Single-Pass en `video_maker.py`
El script `content_factory/video_maker.py` debe despojarse de TODA la lógica de NLP, heurística y lecturas directas a directorios.
*   **Elimina** todo uso de `glob`, la función local `score_file_v2` y la lógica de inferencia de energías astrológicas desde texto, ya que la Célula 2 ya hizo este trabajo.
*   **Modifica** el script para que actúe pura y exclusivamente como un "FFmpeg Builder". Su único input debe ser leer `lista_de_corte_validada_<evento_id>.json` (producido por `validador_de_ensamble.py`).
*   **Transmutación Dinámica (Single-Pass):** Añade la regla en el código de FFmpeg (en la construcción del `filter_complex`) para que si el `json` le manda un `.jpg` o `.png`, le aplique el movimiento de `zoompan` al vuelo, ahorrando lecturas y escrituras al disco.

### ⚠️ REGLAS INQUEBRANTABLES
1.  **Cero Alucinación de Rutas:** Respeta estrictamente los directorios declarados en el archivo `contexto_astrologico.json`. No hardcodees rutas temporales.
2.  **Calidad sobre Rapidez:** Si el código resultante excede el tamaño de un mensaje, utiliza las palabras "CONTINÚA EN LA PARTE 2" y espera que el usuario te dé permiso para seguir enviando código.
3.  **No elimines imports sin revisar:** Revisa cuidadosamente qué imports en `video_maker.py` se utilizan en `subtitle_generator` o `audio_mixer` antes de purgarlos.
4.  **Devuelve código completo y funcional.** No uses placeholders como `# ... resto del código ...`.

Responde a este prompt entregando primero el código refactorizado para `nodriza_visual.py`, y luego el de `video_maker.py`.
