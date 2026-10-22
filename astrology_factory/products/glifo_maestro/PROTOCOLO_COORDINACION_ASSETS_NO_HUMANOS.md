# 📜 PROTOCOLO DE COORDINACIÓN INTER-HILOS · ASTROLOGY FACTORY
*Sincronización de Producción Visual: Hilo Somático (Humanos) vs. Hilo Simbólico (No Humanos)*
*Referencia de Sesión Activa: `17a47ed4-ed1e-4d1b-9cca-183b7c204cbe`*
*Fecha de Emisión: 21 de Octubre, 2026*

---

## 1. DIVISIÓN DE ROLES EN EQUIPO

Para evitar duplicación de esfuerzos, colisiones en el Vault y asegurar coherencia estética en el producto final (*El Glifo Maestro* y la app de *Astrology Factory*), el trabajo se divide en dos frentes complementarios:

| Frente de Trabajo | Hilo Responsable | Alcance del Contenido | Estética y Reglas |
| :--- | :--- | :--- | :--- |
| **A. Alfabeto Somático (Figuras)** | **Hilo Actual** (`17a47ed4-...`) | Arquetipos planetarios y zodiacales representados por **figuras humanas** (Roberto Ferri, desnudo académico sacro, acciones somáticas primarias). | Formato vertical `9:16`, fondo betún negro azabache (`#000000`), claroscuro tenebrista, óleo sobre lino crudo. |
| **B. Alfabeto Inorgánico (Símbolos)** | **Tu Hilo Hermano (No Humanos)** | **Cero figuras humanas**. Glifos astrológicos, sigilos, sellos herméticos, geometría sagrada, orbes celestes puros, talismanes y objetos arquetípicos. | Coherencia con la paleta de materiales (oro bruñido, plata selenita, bronce oscuro, hierro forjado, obsidiana). Fondo `#000000` o transparente. |

---

## 2. DÓNDE Y CÓMO GUARDAR LOS ASSETS NO HUMANOS

El agente del otro hilo debe depositar todas las imágenes terminadas en las rutas canónicas del **Vault de Contingencia**:

### Rutas Absolutas en el Vault:
Base principal:
`/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/`

1. **Glifos Geométricos, Sigilos y Sellos Herméticos:**
   `.../Assets_Auditados/Imagenes/09_Geometria_Sagrada/`
   *Ejemplo: `sigilo_marte_hierro_forjado.webp`, `glifo_venus_cobre_alquimico.webp`*
2. **Símbolos y Glifos de los 12 Signos Zodiacales:**
   `.../Assets_Auditados/Imagenes/01_Signos_Zodiacales/`
   *Ejemplo: `glifo_aries_fuego_primordial.webp`, `glifo_tauro_tierra_solida.webp`*
3. **Planetas Celestes / Orbes Cósmicos (Sin figuras):**
   `.../Assets_Auditados/Imagenes/02_Planetas/`
   *Ejemplo: `orbe_marte_roca_carmesí.webp`, `orbe_saturno_anillos_plata.webp`*
4. **Cartas, Fondos y Texturas Sagradas:**
   `.../Assets_Auditados/Imagenes/15_Astrologia_Cartas/` o `.../13_Abstracto_Fluidos/`

---

## 3. GUÍA Y DIRECTIVAS ESPECÍFICAS PARA CHATGPT (DALL-E 3)

Dado que este frente se trabajará con **ChatGPT (DALL-E 3)**, se deben tener en cuenta las particularidades de cómo DALL-E interpreta y reescribe los prompts:

### A. Cómo evitar que DALL-E meta personas o manos:
DALL-E 3 tiende a dibujar manos sosteniendo el objeto si no se le frena en seco. Indicale a ChatGPT:
> *"Genera la imagen con DALL-E 3 como un objeto o símbolo puramente aislado. NO debe haber personas, manos, rostros ni siluetas humanas. Es un macro de geometría sagrada / sigilo / orbe flotando en el centro sobre fondo negro puro."*
> En inglés para el prompt interno de DALL-E: *"A pure isolated metaphysical symbol centered against a solid pitch-black background (#000000). Strictly non-human, geometric, and macro-focused. Completely devoid of human figures, hands, or silhouettes."*

### B. Formatos nativos de DALL-E 3:
- **Para Glifos, Sigilos y Sellos Circulares:** Pedir formato cuadrado (`1024x1024` / `1:1`). Son ideales para recortar o usar como iconos y elementos centrales.
- **Para Cartas, Orbes y Fondos Verticales:** Pedir formato vertical (`1024x1792` / vertical `9:16`).

### C. Coherencia de Materiales con el Estilo Roberto Ferri:
Para que los dibujos de ChatGPT armonicen a la perfección con los cuerpos al óleo de Roberto Ferri generados en el hilo principal, pedile a ChatGPT que use materiales alquímicos nobles:
- **Sol:** Oro antiguo bruñido con pátina y filigrana solar (*burnished antique gold, warm amber glow*).
- **Luna:** Plata selenita pulida, marfil tallado y nácar líquido (*polished selenite silver, mother-of-pearl sheen*).
- **Mercurio:** Bronce oscuro finamente torneado y filamentos de azogue (*slender oxidized bronze, liquid quicksilver mercury*).
- **Venus:** Cobre forjado rosado, esmeralda cruda y terciopelo musgo (*hand-forged rose copper, raw emerald crystal*).
- **Marte:** Hierro oscuro forjado al rojo con ascuas sutiles (*forged black iron, red-hot steel edge, glowing embers*).

---

## 4. CÓMO GUARDAR LOS ARCHIVOS DE CHATGPT EN EL VAULT

Las imágenes generadas y descargadas desde ChatGPT deben guardarse o convertirse a `.webp` (o `.png`) en las carpetas correspondientes del Vault:

- **Sigilos y Geometría Sagrada:**
  `/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/09_Geometria_Sagrada/`
- **Glifos Zodiacales:**
  `/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/01_Signos_Zodiacales/`
- **Planetas / Orbes Celestes (Sin personas):**
  `/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/02_Planetas/`

**Nombres de archivo:** `sigilo_marte_hierro.webp`, `glifo_sol_oro.webp`, etc. (minúsculas, `snake_case`).

---

## 5. INTEGRACIÓN FINAL
En la aplicación de *Astrology Factory*, cada carta o pantalla combinará la **figura humana de Roberto Ferri** (de este hilo) con el **sigilo/glifo alquímico de ChatGPT** (del hilo hermano), logrando una estética cohesiva y de primer nivel.
