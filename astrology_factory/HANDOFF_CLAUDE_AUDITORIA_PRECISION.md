# 🛡️ HANDOFF DE NIVEL 3: CLAUDE PRO (PRECISIÓN MILITAR & MOLDES DE ORO)
*Fecha: Octubre 2026 | Ecosistema: Astrology Factory / El Glifo Maestro*

Eres **Claude**, la IA de **NIVEL 3 (Arquitectura Sagrada, Precisión Militar y Moldes de Oro)** del ecosistema *Astrology Factory*.

> **POLÍTICA INQUEBRANTABLE DE TOKENS:**
> En este proyecto está estrictamente prohibido usar a Claude para tareas de rutina o revisión de tránsitos cotidianos (eso lo resuelve Swiss Ephemeris en C y Gemini Flash en Nivel 1).
> Tu tiempo y tokens se reservan **EXCLUSIVAMENTE** para ingeniería donde se exige **CERO ERROR** o para forjar los **MOLDES DE ORO CANÓNICOS** que luego imitan las IAs de producción.

---

## 🎯 MISIÓN 1 (CERO ERROR): WEBHOOK DE MERCADO PAGO EN FASTAPI CON CRIPTOGRAFÍA HMAC & IDEMPOTENCIA
En [web_app/main.py](file:///home/LAB/astrology_factory/web_app/main.py) ya tenemos la web tenebrista corriendo en producción en `portaltarotmistico.com` con el catálogo oficial en 3 productos ($1.560 ARS = 1 USD):
1. **Carta Natal Profunda + Oráculo** ($4.990 ARS)
2. **Reloj Astrológico 4K Live Wallpaper** ($2.990 ARS)
3. **Revolución Solar en Video** ($14.990 ARS)
* **Combo Tríada Sagrada (3 en 1)** ($16.990 ARS)

### Lo que necesitamos que diseñes con precisión militar:
El endpoint webhook en FastAPI (`/api/mercadopago/webhook`) que reciba las notificaciones de Mercado Pago y garantice:
1. **Validación Criptográfica de la Firma HMAC SHA-256:**
   * Validar el encabezado `x-signature` extrayendo el `ts` y el hash `v1`.
   * Verificar la firma contra `MERCADOPAGO_WEBHOOK_SECRET` y el ID del recurso para blindar el servidor contra ataques de suplantación (*spoofing*) o confirmaciones de pago falsificadas.
2. **Idempotencia Estricta en SQLite (Cero Doble Acreditación):**
   * Control transaccional con tabla `processed_payments` (campos: `payment_id`, `status`, `payer_email`, `product_id`, `created_at`).
   * Si Mercado Pago reenvía la notificación 3 o 4 veces por política de reintento, el sistema debe responder `HTTP 200 OK` de inmediato sin procesar dos veces el pedido.
3. **Activación Automática Inmediata (0 Segundos):**
   * Si el estado es `approved`:
     - Registrar en la base de datos la compra del usuario.
     - Generar un token único de acceso seguro para desbloqueo del producto (Carta Natal PDF o Enlace del Reloj Wallpaper).
     - Para Revolución Solar, dejar la tarea encolada en `pending_video_tasks` con status `queued_for_render_48h`.
     - Despachar el correo de confirmación con `BackgroundTasks`.

---

## 🎯 MISIÓN 2 (PRECISIÓN MATEMÁTICA & GLSL): LA ESFERA ARMILAR 3D (THREE.JS)
Para el producto premium **Reloj Astrológico 3D / Esfera Armilar**, necesitamos que diseñes la arquitectura geométrica y de materiales en Three.js / WebGL para integrarlo como selector `[ 2D Clásico | 3D Esfera Armilar ]` en el canvas:

1. **Geometría de los Anillos Sagrados:**
   * **Anillo Meridiano Exterior:** Radio `R`, fijo, orientado verticalmente.
   * **Anillo del Horizonte:** Nivelado a la latitud del observador (Buenos Aires `-34.6°`), con los 4 puntos cardinales (`N, S, E, W`).
   * **Anillo Eclíptico Sagrado:** Inclinado exactamente a `23.439°` (oblicuidad de la eclíptica) respecto al Ecuador celeste, con los 12 sectores zodiacales grabados analíticamente cada 30°.
   * **Centro `⊕`:** La Tierra como esfera con pátina geocéntrica.
2. **Material PBR Tenebrista (Estética Roberto Ferri):**
   * Especificar la configuración de materiales Three.js (`MeshStandardMaterial` o shader personalizado) para lograr:
     - Bronce antiguo y oro bruñido con rugosidad (`roughness: 0.25-0.35`, `metalness: 0.85-0.90`).
     - Iluminación dramática claroscuro (luz puntual cálida + luz cenital etérea).
     - 60-120 FPS sin consumo de CPU en el servidor ni sobrecalentamiento en celulares.

---

## 📋 ENTREGA ESPERADA DE CLAUDE PRO
1. **Archivo completo de integración para FastAPI:**
   * Código en Python para `web_app/mercadopago_webhook.py` con todas las funciones criptográficas y el modelo de datos SQLite listo para importar en `main.py`.
2. **Estructura Modular de Three.js para la Esfera Armilar:**
   * Código en JavaScript (`esfera_armilar_3d.js`) que monte la escena, los anillos concéntricos inclinados matemáticamente a 23.44° y los materiales de bronce/oro sin librerías pesadas externas.
