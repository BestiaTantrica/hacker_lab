# Manual de Animación I2V (Image-to-Video) para la Bóveda Astrológica

Este documento detalla el flujo de trabajo manual para tomar las imágenes estáticas (generadas por IA) y darles vida mediante herramientas gratuitas (Free Tiers) de la web. Estos videos animados se usarán luego como *b-roll premium* en los montajes finales.

---

## 1. Flujo de Trabajo General (Paso a Paso)

1. **Selección del Asset:** Ve a la carpeta `Astrology_Vault/Assets_Auditados/Imagenes/` y elige una imagen generada previamente (ej. `arte_propio_emocion_luna_cancer_...jpg`).
2. **Elección de Herramienta:** Selecciona la IA web más adecuada según el tipo de imagen (ver sección 2).
3. **Subida y Prompting:** Sube la imagen a la plataforma y escribe un "Motion Prompt" (instrucción de movimiento). Mantén el movimiento sutil para no romper la estética.
4. **Descarga y Guardado:** Una vez que la IA termine el video (generalmente de 3 a 5 segundos), descárgalo.
5. **Clasificación en la Bóveda:** Renombra el video usando nuestra nomenclatura y guárdalo en la carpeta correspondiente de videos:
   - `Astrology_Vault/Descargas_Crudas/Videos/11_Humanos_Emociones/` (Para retratos)
   - `Astrology_Vault/Descargas_Crudas/Videos/13_Abstracto_Fluidos/` (Para texturas y geometría)

---

## 2. Herramientas y Casos de Uso (Free Tiers)

### A. Hailuo AI (MiniMax) / Kling AI
**Especialidad:** Rostros humanos, realismo y coherencia física. Son las mejores IAs para mantener la cara del personaje sin que se deforme.
- **Caso de uso en el Proyecto:** Usar para las imágenes de la carpeta `11_Humanos_Emociones` (Los retratos cinemáticos).
- **Prompt Recomendado:** *"Subtle cinematic movement, deep breathing, wind gently blowing hair, highly emotional, steady camera, 8k resolution."*
- **Tip:** Evita pedir que el personaje hable o corra. Los movimientos sutiles (parpadear, respirar, girar un poco la cabeza) dan el efecto esotérico perfecto.

### B. Pika Labs
**Especialidad:** Control específico de zonas (Motion Brush).
- **Caso de uso en el Proyecto:** Excelente para imágenes donde queremos que el personaje se quede quieto pero el entorno se mueva (ej. El océano detrás del Sol en Piscis, o el fuego de Aries).
- **Cómo usar:** 
  1. Sube la imagen.
  2. Selecciona la herramienta "Motion Brush".
  3. Pinta solo el agua, el humo o el fuego.
  4. En los parámetros, dale fuerza al movimiento del fluido.
- **Prompt Recomendado:** *"Flowing neon fluid, glowing embers rising, seamless looping energy, mystical."*

### C. Luma Dream Machine
**Especialidad:** Movimientos de cámara dinámicos, paisajes inmersivos y transiciones de entornos.
- **Caso de uso en el Proyecto:** Para imágenes de `13_Abstracto_Fluidos` o montañas/paisajes (ej. Nodos en Capricornio).
- **Prompt Recomendado:** *"Slow cinematic push in, mystical fog rolling, glowing ethereal light, dark atmospheric background."*
- **Tip:** Luma es excelente para hacer zooms que te meten "dentro" de la carta astral o la geometría sagrada.

### D. PixVerse
**Especialidad:** Animación rápida con soporte de sujetos específicos. Es genial para pruebas rápidas si te quedas sin créditos en las otras.
- **Caso de uso en el Proyecto:** Para fondos mágicos, galaxias girando o estrellas brillantes.
- **Prompt Recomendado:** *"Stars twinkling, cosmic dust moving slowly, dark mystical space."*

---

## 3. Consideraciones Importantes

*   **Evitar Deformaciones:** Si la IA web deforma la imagen (ej. le salen tres manos o el ojo se derrite), descarta el video. Es preferible usar la imagen fija original con un efecto de zoom en nuestro editor final, a usar un mal video de IA.
*   **Renovación de Créditos:** Entra a todas estas plataformas con las cuentas gratuitas de tu equipo. Casi todas renuevan créditos de forma diaria o mensual. Quema los créditos diarios rotando entre las 5 IAs mencionadas.
