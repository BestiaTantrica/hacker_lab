# Regla de Arquitectura: Nodriza Autónoma y Scripts Centralizados

- **NUNCA** crear scripts manuales aislados para descargar, scrapear o catalogar.
- Todo scrapeo, recolección de arte (Pexels, Pollinations) o catalogación (Gemini Vision) **DEBE** ir integrado como una fase dentro del daemon principal asíncrono (`nodriza_autonoma.py`).
- **Límites obligatorios:** Cualquier proceso que descargue assets debe respetar estrictamente los límites de cuota de API (ej: rotación Hydra, límites bajos `--max 5`) y tener integrada la lógica de purga (borrado inteligente al superar los 50GB en la bóveda).
