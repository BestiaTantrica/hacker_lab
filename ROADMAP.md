# 🗺️ ROADMAP DEL LABORATORIO

> Este roadmap refleja el **estado real del sistema** (Auditado 2026-07-15).
> No contiene arquitecturas inventadas. Cada etapa produce un resultado funcional verificable.
> Una etapa no comienza hasta que la anterior esté completa y validada.

---

## ✅ ESTADO ACTUAL (Verificado 2026-07-15)

| Nodo | Componente | Estado |
|---|---|---|
| Local | `network-toolkit` | ✅ Funcional. Movido a `/LAB/herramientas/`. |
| Local | `plataforma_operativa` | ✅ Movida a `/LAB/herramientas/`. |
| Local | `portafolio-ciberseguridad` | ✅ Limpio, contiene solo documentación y teoría. |
| Local | Archivos sensibles | ✅ `mongo` y `códigos de respaldo h1` movidos a `.boveda/`. |
| OCI | Pipeline Discovery | ✅ Operativo (03:00 UTC). Usa subfinder. `actual.json` se genera. |
| OCI | Comparador y Alertas | ✅ Operativo. Envia alertas de subdominios a Telegram. |

---

## 🚀 ETAPA 1 — Pipeline OCI-1 (Terminada)
**Prioridad:** Alta | **Estado:** ✅ Completado
Se ha establecido el músculo de recolección en la instancia OCI-1 (1GB AMD). 
- Descubrimiento diario automatizado (`subfinder`).
- Explotación automática de bugs de bajo esfuerzo/alta recompensa (`explotador_automatico.py`): Subdomain Takeovers, CORS, archivos expuestos (.env).
- Alertas a Telegram.

---

## 🎯 ETAPA 2 — El Cerebro OCI-2 (Panel C2 Ligero)
**Prioridad:** Máxima | **Objetivo:** Montar un centro de mando visual para no depender de la consola y poder operar desde el celular.

### Problema actual:
Manejar todo desde la terminal requiere saber comandos y estar en la PC. El usuario necesita un sistema de un clic ("Point and Shoot") para capitalizar rápido.

### Tareas:
- [ ] **Desplegar Panel Web (FastHTML/Streamlit) en OCI-2 (12GB ARM):** Una web privada, protegida con contraseña, que lea los hallazgos de OCI-1 y los muestre en tarjetas (cards).
- [ ] **Acciones de 1 clic:** Botones en el panel como "Revisar CORS", "Extraer Secretos JS", que ejecuten los scripts en segundo plano.
- [ ] **Integración de IA (Groq):** Un botón de "Generar Reporte HackerOne" que use Groq (Llama 3) para redactar el ticket perfecto en base al bug encontrado, listo para copiar y pegar.

**Criterio de éxito:** El usuario puede entrar desde su celular a una IP web, ver un Subdomain Takeover detectado en `shopify.com`, presionar "Generar Reporte", copiar el texto y cobrar.

---

## 🤖 ETAPA 3 — Extractor de Secretos (El Motor de Dinero)
**Prioridad:** Media-Alta
- [ ] **Implementar Extractor JS:** Script para OCI-2 que descargue el código de las webs encontradas por OCI-1 y busque tokens de AWS o Stripe usando Regex. Esto tiene cero burocracia y paga directo.

---

> 📌 **Regla de oro:** Cero burocracia. Si algo requiere logins manuales tediosos, cuentas complejas o adivinar lógica, se descarta. El enfoque es *Volumen Automatizado* (pescar con red, no con caña).
