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

## 3. ESTÁNDARES TÉCNICOS PARA EL HILO DE SÍMBOLOS

1. **Formato:** Archivos `.webp` de alta resolución (mínimo `768x1344` para vertical, o `1024x1024` para sellos/glifos circulares).
2. **Nomenclatura Estricta:** 
   - Minúsculas y guiones bajos (`snake_case`).
   - Cero espacios, cero mayúsculas, cero tildes.
   - Nombres auto-descriptivos: `[categoria]_[arquetipo]_[material/accion].webp`
3. **Evitar la Trampa de Tokens de FLUX:**
   - En FLUX no existe negative prompt. Describir **solo lo que sí existe** en positivo.
   - Para fondos limpios sin elementos flotantes parásitos: *"isolated on a solid flat pitch-black background (#000000), dramatic studio lighting, macro photography of forged metal / carved stone"*.
4. **Registro:** Cada vez que el hilo hermano guarde un asset en el Vault, debe registrar el nombre, seed y prompt en la documentación técnica para mantener la paridad con este hilo.

---

## 4. INTEGRACIÓN FINAL
En la interfaz de la aplicación, cada Arquetipo somático producido por este hilo (ej. *Venus Anadyómene* o *Marte Primal*) se ensamblará en capas con el glifo/sigilo inorgánico producido por el hilo hermano, creando una tarjeta astrológica rica y multidimensional.
