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
- `animador_espiral_3d.py`: Generador de la Espiral Temporal 3D ("Tirabuzón de Retornos Solares") que simula el paso del tiempo desde la Carta Natal (Z=0, oro) hasta la Revolución Solar anual (Z=Top, cian) en hiperlapso cinemático 1080p.

---

### 3. Motor Visual Bi-Wheel y Enfoque Quirúrgico

1. **Preservación Total del Mandala**:
   - Signos zodiacales, 12 casas natales y de RS, planetas con halos orbe y aspectos base permanecen 100% visibles.
2. **Coreografía de Cámara Fija -> Zoom Quirúrgico**:
   - Cada capítulo abre con un **plano general fijo (1.0x)** durante los primeros 4-6 segundos, con paneles pedagógicos completos para asimilar el contexto general.
   - En el enfoque específico (Portal, Sol, Luna, Marte, Saturno, aspectos), la cámara ejecuta un paneo y zoom profundo (1.75x) centrado al píxel en las coordenadas `(cx, cy)` del elemento, mientras los paneles exteriores se disuelven para dar paso al mandala expandido y sus retículos neón sin recorte tosco de texto.
3. **Espiral Temporal 3D ("Tirabuzón")**:
   - Animación 3D nativa generada en Python (Matplotlib 3D + NumPy + FFmpeg) a $0 costo que ilustra cómo el retorno solar de este año es la cima de un árbol de ciclos anuales que nacieron en la carta natal.
