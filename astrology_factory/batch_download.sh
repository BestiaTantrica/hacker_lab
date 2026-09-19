#!/bin/bash
echo "🚀 Iniciando descarga en batch para la Semana 2 de Octubre..."

./venv/bin/python content_factory/vault_scraper.py "mars_sextile_uranus" 10
./venv/bin/python content_factory/vault_scraper.py "venus_square_mars" 10
./venv/bin/python content_factory/vault_scraper.py "moon_opposite_neptune" 10

echo "✅ Descarga en batch completada!"
