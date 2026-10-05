# 🎬 SUGERENCIAS DE EDICIÓN Y ENSAMBLAJE (FFMPEG)
*Para la IA Arquitecta / Nivel 3 o Scripts de Célula 3*

Estas sugerencias fueron recolectadas durante la generación del stock visual impulsado por IA. Su objetivo es maximizar el impacto emocional y onírico de los videos generados.

## 1. Encadenamiento Secuencial (Abstracción -> Emoción)
Para lograr que el espectador sienta el tránsito en el cuerpo, se sugiere la siguiente regla de montaje dinámico:
- **Capa Base (Background):** Mantener de fondo las imágenes "Abstractas" (espacio, abismo, agua fluida) con un sutil `zoompan`.
- **Capa Superior (Foreground):** Inyectar las imágenes de categoría `11_Humanos_Emociones` en los momentos exactos donde el guion (TTS) habla de los efectos psicológicos (Ej: "sentirás frustración", "cargas con un peso", "sombra inconsciente").
- **Técnica:** Utilizar el filtro `xfade` (con duraciones cortas de 0.5s) o animar la opacidad (canal alpha) para que las caras humanas aparezcan como "flashes oníricos" sobre el fondo astral. No usar cortes duros.

## 2. Satirización y Empatía (Rol 2 del Guion)
Las imágenes humanas/emocionales actúan como un anclaje. Cuando el JSON dicta la toma de *rol: efecto_cuerpo_emocion*, la Célula 2 debe forzar una búsqueda en la carpeta `11_Humanos_Emociones` en lugar de `07_Espacio_Galaxias`.

## 3. Composición Orgánica
- Queda **prohibido** colocar los renders humanos como cuadrados superpuestos (`overlay` plano).
- **Mandatorio:** Usar filtros de difuminado de bordes (`feathering`) al superponer. Esto se logra aplicando una máscara circular con degradado antes de superponer la cara de la persona sobre el fondo abstracto, respetando el "Arte Mixto y Emocional" de `PROJECT_RULES.md`.

## 4. Colimetría Consistente
Todas las imágenes de IA se generaron bajo la paleta estricta: Negro, Morado Oscuro, Cian/Agua, Dorado. Si se aplican filtros `colorchannelmixer` o `eq` durante el render final (Célula 3), asegurarse de que no sobresaturan estos tonos, ya que vienen nativamente corregidos desde la generación.
