# Módulo de Revolución Solar (Paquete Premium)

## Arquitectura y Principios de Diseño

Este módulo implementa el pipeline de generación del **Video de Revolución Solar (10-15 minutos)** diseñado para entregarse de forma conjunta e integrada con el **Informe Escrito de Carta Natal (10 páginas)**.

---

### 1. Doble Geocodificación Obligatoria (Regla Maestra)

Todo cálculo de Retorno Solar requiere **dos pares de coordenadas geográficas independientes**:

1. **Coordenadas Natales (`lat_natal`, `lon_natal`, `dt_natal_local`, `utc_offset_natal`)**:
   - Calculan la Carta Natal base.
   - Determinan la posición exacta del Sol natal al segundo de arco (`sol_natal_deg`), que es el blanco astronómico al que debe retornar el Sol.

2. **Coordenadas de Retorno (`lat_rs`, `lon_rs`, `utc_offset_rs`, `ciudad_rs`)**:
   - Representan la ciudad donde el consultante **se encuentra físicamente en el instante exacto de su cumpleaños**.
   - Calculan las Casas Placidus de la Revolución Solar, el Ascendente anual y el Medio Cielo.
   - **Regla de Formulario**: El frontend o API de pedidos DEBE solicitar explícitamente:
     * *Lugar de nacimiento*
     * *Ciudad donde vas a pasar tu cumpleaños este año*
   - Si no se especifica, NO debe asumirse la ciudad de nacimiento sin confirmación expresa del usuario.

---

### 2. Componentes del Módulo

- `calculador_revolucion_solar.py`: Motor determinístico en Python con Swiss Ephemeris (`swisseph`) con convergencia Newton-Raphson (<0.1 segundos de arco de orbe solar).
- `graficador_biwheel.py`: Renderizador de ruedas concéntricas espaciales en Matplotlib con fondo `#080b12`, estrellas, anillo exterior de RS y aspectos de activación inter-cartas.
- `ensamblador_handoff_rs.py`: Compilador de super-prompts de handoff para Claude (Modo High) aplicando el ADN de autor (Tomás), voseo argentino maduro y el estándar de oro en 6 capítulos.
- `ejemplos_oro/`: Repositorio de guiones canónicos de referencia redactados por Claude High (`guion_oro_rs_tomas.md`).
- `generador_guion_rs_produccion.py`: Motor de producción masiva a costo $0 para clientes reales utilizando Gemini 3.8 Flash / Groq 120B guiado por Few-Shot prompting.
- `video_maker_premium.py`: Ensamblador de video con chunking modular por capítulos y concatenación gapless en FFmpeg. Integra blend progresivo de neón y zoompan astronómico hacia coordenadas (cx, cy).

---

### 3. Motor Visual Bi-Wheel y Enfoque Quirúrgico

1. **Preservación Total del Mandala**:
   - Nunca se elimina el contexto astrológico: signos zodiacales, 12 casas natales y de RS, planetas y aspectos base permanecen 100% visibles.
2. **Sistema de Enfoque Neón Aditivo**:
   - Detección astronómica de coordenadas de foco `(cx, cy)` según el tipo de elemento (planeta, casa o aspecto).
   - Generación sincronizada de pares `solo_base` (mandala limpio) y `foco` (con reticle lock, halos concéntricos y láseres de activación).
   - Mezcla progresiva vía FFmpeg `blend` acoplada al `zoompan` para encender los efectos mientras la cámara avanza.

### 4. Hoja de Ruta para Próximas Sesiones

- **Sincronización Narrativa Fina**: El Bi-Wheel inicia fijo (1.0x) para brindar contexto general y luego panea/zoomea quirúrgicamente hacia la zona exacta cuando la locución pronuncia el término clave.
- **Espiral Temporal 3D ("Tirabuzón de Retornos")**: Renderizado en perspectiva 3D del árbol temporal de cumpleaños, mostrando cómo la carta natal se proyecta año tras año en una hélice hasta la Revolución Solar actual.
- **Vitalidad de Cuerpos Celestes**: Respiración de luz en glifos, líneas de aspecto con flujo de energía y HUD cósmico limpio sin saturar la pantalla.
