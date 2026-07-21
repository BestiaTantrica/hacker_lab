# HOJA DE RUTA DEL LABORATORIO (Fuente Única de Verdad)

## Propósito

Este documento define el estado actual del laboratorio y cómo debe avanzar.

Cualquier IA (ChatGPT, Gemini, Antigravity u otra) debe seguir esta hoja de ruta.

No debe rediseñar la arquitectura completa en cada sesión.

No debe agregar complejidad innecesaria.

El objetivo es avanzar mediante pequeños logros funcionales.

---

# Regla principal

Solo se trabaja sobre UN objetivo funcional a la vez.

No comenzar un nuevo componente hasta que el anterior funcione completamente.

---

# Objetivo final (largo plazo)

Construir una plataforma personal de operaciones de ciberseguridad que permita:

- monitoreo continuo
- automatización
- observabilidad
- integración con IA
- apoyo a programas de Bug Bounty
- crecimiento profesional
- generación de ingresos

Este objetivo se alcanza por etapas.

No intentar implementarlo todo desde el inicio.

---

# Estado actual

## PC local

Existe un proyecto llamado `network-toolkit`.

Actualmente posee:

- arquitectura modular
- sistema de plugins
- logger
- reporter
- validator
- self-test
- módulo Health Check

Este proyecto continuará creciendo de manera independiente.

---

## Servidor Oracle

Existe una estructura inicial para la plataforma operativa.

Actualmente NO existen agentes inteligentes.

Solo existe la estructura base.

---

# Filosofía

La IA NO debe intentar resolver problemas que todavía no existen.

Primero deben construirse procesos simples.

Después se agregará inteligencia.

---

# Orden obligatorio de desarrollo

## ETAPA 1

Discovery pasivo.

Objetivo:

Generar correctamente un archivo JSON con activos descubiertos.

Nada más.

No usar IA.

No usar Groq.

No generar resúmenes.

Solo producir datos.

Cuando funcione, la etapa termina.

---

## ETAPA 2

Comparador.

Entrada:

JSON anterior.

JSON nuevo.

Salida:

Delta.

Detectar únicamente cambios.

No utilizar IA.

---

## ETAPA 3

Histórico.

Guardar resultados.

Consultar resultados anteriores.

Registrar fechas.

---

## ETAPA 4

Solo cuando exista un Delta real:

Integrar IA.

La IA analizará únicamente eventos nuevos.

Nunca analizar toda la información nuevamente.

---

## ETAPA 5

Supervisor.

Coordinar procesos.

No realizar análisis.

No reemplazar módulos.

Solo ejecutar tareas.

---

## ETAPA 6

Dashboard.

Visualización.

---

# Política de uso de IA

Las IA son caras.

Las cuotas gratuitas son limitadas.

Por lo tanto:

Nunca llamar un modelo si no existe un cambio real.

La IA solo participa cuando agrega valor.

---

# Política de APIs

Todas las APIs gratuitas tienen límites.

Cada módulo debe minimizar llamadas.

Debe existir caché cuando sea posible.

Debe evitar trabajo repetido.

---

# Forma de trabajar

Cada semana debe completarse un único objetivo funcional.

No comenzar el siguiente hasta terminar el anterior.

Cada etapa debe dejar un sistema funcionando.

---

# Cómo deben responder las IA

Las respuestas deben centrarse únicamente en el paso actual.

No proponer arquitecturas enormes.

No agregar componentes futuros.

No crear nuevos agentes si todavía no son necesarios.

Si una mejora puede esperar, debe anotarse para el futuro y continuar con el objetivo actual.

---

# Definición de éxito

Una semana es exitosa cuando existe una mejora funcional verificable.

No cuando existen más carpetas.

No cuando existen más diagramas.

No cuando existen más ideas.

Solo cuando existe una nueva capacidad funcionando correctamente.
