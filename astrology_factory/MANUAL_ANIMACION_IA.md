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

## 2. Herramientas y Políticas de Créditos Gratuitos

### 🟢 Las que se RENUEVAN DIARIAMENTE (Uso Continuo):
1. **Kling AI ([klingai.com](https://klingai.com/)):**
   - **Créditos:** **66 créditos diarios** gratuitos (se resetean cada 24 hs, no acumulables).
   - **Rendimiento:** Alcanza para unas **6 generaciones diarias** (10 créditos c/u).
   - **Especialidad:** Rostros, coherencia física y retratos (`11_Humanos_Emociones`). Es el reemplazo directo y superior de Hailuo.
   - **Prompt Recomendado:** *"Subtle cinematic movement, deep slow breathing, dark wind gently moving hair, intense piercing gaze, steady camera, 8k cinematic realism."*

2. **PixVerse ([pixverse.ai](https://pixverse.ai/)):**
   - **Créditos:** **60 créditos diarios** gratuitos (se resetean a las 00:00 UTC, no acumulables).
   - **Rendimiento:** Permite unas 3-5 animaciones diarias.
   - **Especialidad:** Efectos de luz, partículas, destellos, velocidad y magia (`07_Espacio_Galaxias`, `14_Glitch_VFX`).
   - **Prompt Recomendado:** *"Electric sparks drifting, glowing aura pulsing slowly, dynamic volumetric light rays, smooth cinematic motion."*

3. **Luma Dream Machine ([lumalabs.ai/dream-machine](https://lumalabs.ai/dream-machine)):**
   - **Créditos:** Cupo de generaciones diarias gratuitas (con cola de espera estándar).
   - **Especialidad:** Zooms inmersivos, niebla, agua y texturas fluidas (`13_Abstracto_Fluidos`, `10_Naturaleza_Paisajes`).
   - **Prompt Recomendado:** *"Slow cinematic push in, mystical fog rolling, glowing ethereal light, dark atmospheric background."*

4. **Vidu AI ([vidu.studio](https://www.vidu.studio/)):**
   - **Créditos:** Check-in diario con recarga de créditos al iniciar sesión cada día.
   - **Especialidad:** Transiciones cinemáticas y dinamismo.

---

### 🔴 Las de PAQUETE ÚNICO (No renuevan a diario):
- **Hailuo AI (MiniMax):** Da un bono de bienvenida inicial de uso único (que expira a los pocos días). Una vez consumido, requiere plan de pago o crear otra cuenta.
- **RunwayML (Gen-2 / Gen-3):** Da 125 créditos fijos por única vez al registrarte y no se renuevan nunca más en la capa gratis.
- **Pika Labs:** Créditos mensuales limitados o de prueba inicial, no diarios.

---

## 3. Estrategia de Cosecha Diaria ("Daily Farm")

Para no gastar un solo centavo y alimentar la Bóveda todos los días:
1. **Entrar primero a Kling AI:** Gastar los 66 créditos diarios animando los retratos humanos (`11_Humanos_Emociones`).
2. **Entrar a PixVerse:** Gastar los 60 créditos diarios en texturas de energía y espacio (`13_Abstracto_Fluidos` / `07_Espacio_Galaxias`).
3. **Entrar a Luma Dream Machine:** Mandar a generar 2 o 3 tomas con niebla o paisajes mientras trabajas en otra cosa.
4. Si necesitas usar Hailuo de nuevo, se requiere registrarse con otra cuenta de correo debido a que su política es de paquete único.

---

## 4. Aislamiento de Cuentas Paralelas en Navegador

- En Google Chrome, **todas las ventanas de incógnito comparten la misma sesión y cookies**. Intentar abrir dos ventanas de incógnito para dos cuentas distintas causará colisión de sesiones y deslogueos.
- Para operar 2 a 4 cuentas en paralelo sin interferencias:
  1. Usar **Perfiles de Chrome independientes** (icono de perfil arriba a la derecha -> *"Añadir perfil"*). Cada perfil aísla 100% sus cookies y sesiones de Google.
  2. Alternar con ventanas normales y privadas de navegadores secundarios (Firefox / Brave).
- Ante el bloqueo temporal de Kling por "Peak Hours" (servidores saturados para cuentas gratuitas), rotar inmediatamente a PixVerse (60 créditos diarios) o Luma Dream Machine.
