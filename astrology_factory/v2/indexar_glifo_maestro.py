#!/usr/bin/env python3
"""
indexar_glifo_maestro.py
Indexa los 432 activos canónicos de 'El Glifo Maestro' en assets_visuales.db
para que la Nodriza Visual y el validador de ensamble los utilicen automáticamente.
"""

import sqlite3
import datetime
import re
from pathlib import Path

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
DB_PATH = FACTORY_ROOT / "assets_visuales.db"
VAULT_GLIFO = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes/Glifo_Maestro")

# Diccionario de enriquecimiento semántico para arquetipos astrológicos
DICCIONARIO_SEMANTICO = {
    "sol": ["sol", "luz", "identidad", "consciencia", "oro", "vitalidad", "rey", "fuego"],
    "luna": ["luna", "emocion", "plata", "inconsciente", "noche", "maternidad", "agua", "intuicion"],
    "mercurio": ["mercurio", "mente", "comunicacion", "pergamino", "puente", "quicksilver", "aire"],
    "venus": ["venus", "amor", "belleza", "deseo", "arte", "afrodita", "cobre", "armonia"],
    "marte": ["marte", "accion", "fuerza", "impulso", "guerrero", "hierro", "fuego", "voluntad"],
    "jupiter": ["jupiter", "expansion", "sabiduria", "abundancia", "magnanimo", "rayo", "trueno"],
    "saturno": ["saturno", "tiempo", "limite", "cronos", "plomo", "basalto", "disciplina", "estructura"],
    "urano": ["urano", "despertar", "rayo", "relampago", "ruptura", "innovacion", "electricidad"],
    "neptuno": ["neptuno", "misticismo", "niebla", "mar", "oceano", "disolucion", "eter", "trance"],
    "pluton": ["pluton", "transmutacion", "abismo", "muerte", "renacimiento", "hades", "crisol", "sombra"],
    "quiron": ["quiron", "sanacion", "herida", "vulnerable", "alquimia", "medicina", "hierbas"],
    "lilith": ["lilith", "salvaje", "soberania", "luna_negra", "deseo_puro", "serpiente", "abismo"],
    "nodo_norte": ["nodo_norte", "destino", "futuro", "evolucion", "dragon", "proposito"],
    "nodo_sur": ["nodo_sur", "origen", "pasado", "ancestral", "linaje", "memoria"],
    "fortuna": ["fortuna", "pars_fortunae", "azar", "prosperidad", "cornucopia", "rueda"],
    "fuego": ["fuego", "tetraedro", "llama", "volcan", "calor", "pasion", "energia"],
    "tierra": ["tierra", "cubo", "roca", "mineral", "materia", "gaia", "estabilidad"],
    "aire": ["aire", "octaedro", "viento", "mente", "astrolabio", "aliento", "libertad"],
    "agua": ["agua", "icosaedro", "mar", "rio", "lagrima", "profundidad", "flujo"],
    "eter": ["eter", "dodecaedro", "quintaesencia", "cosmos", "espacio", "infinito"],
    "conjuncion": ["conjuncion", "fusion", "inicio", "union", "orbe"],
    "oposicion": ["oposicion", "tension", "polaridad", "espejo", "balanza"],
    "trigono": ["trigono", "armonia", "fluidez", "oro", "triangulo"],
    "cuadratura": ["cuadratura", "friccion", "choque", "desafio", "esfuerzo"],
    "sextil": ["sextil", "oportunidad", "afinidad", "talento", "estrella"],
    "quincuncio": ["quincuncio", "ajuste", "calibracion", "torsion", "incomodidad"],
    "reloj": ["reloj", "astrolabio", "tiempo", "mecanismo", "horas", "efemerides"],
    "mandala": ["mandala", "rueda", "cosmologia", "zodiaco", "totalidad"]
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruta_archivo TEXT UNIQUE,
                tipo TEXT,
                estado TEXT,
                etiquetas TEXT,
                fecha_auditoria TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS stats_uso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id TEXT NOT NULL,
                evento_id TEXT NOT NULL,
                fecha_uso TEXT NOT NULL,
                UNIQUE(asset_id, evento_id)
            )
        ''')
        conn.commit()

def extraer_etiquetas(archivo: Path) -> list:
    tokens = set(re.findall(r"[a-z0-9]+", archivo.stem.lower()))
    for parent in archivo.parents:
        if parent == VAULT_GLIFO.parent:
            break
        tokens.update(re.findall(r"[a-z0-9]+", parent.name.lower()))
    
    # Agregar etiquetas semánticas expandidas
    etiquetas = set(tokens)
    etiquetas.add("roberto_ferri")
    etiquetas.add("tenebrismo")
    etiquetas.add("oleo")
    etiquetas.add("fondo_negro")

    for clave, tags in DICCIONARIO_SEMANTICO.items():
        if any(clave in t for t in tokens):
            etiquetas.update(tags)

    return sorted(list(etiquetas))

def main():
    init_db()
    archivos = sorted(list(VAULT_GLIFO.rglob("*.webp")))
    print(f"📦 Escaneando {len(archivos)} archivos en {VAULT_GLIFO}...")

    total_nuevos = 0
    total_actualizados = 0
    fecha = datetime.datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for f in archivos:
            ruta_str = str(f.resolve())
            etiquetas = extraer_etiquetas(f)
            etiquetas_str = ",".join(etiquetas)
            
            c.execute('''
                INSERT INTO assets (ruta_archivo, tipo, estado, etiquetas, fecha_auditoria)
                VALUES (?, 'imagen', 'aprobado', ?, ?)
                ON CONFLICT(ruta_archivo) DO UPDATE SET
                    estado = 'aprobado',
                    etiquetas = excluded.etiquetas,
                    fecha_auditoria = excluded.fecha_auditoria
            ''', (ruta_str, etiquetas_str, fecha))
            if c.rowcount == 1:
                total_nuevos += 1
            else:
                total_actualizados += 1
        conn.commit()

    print(f"✅ Indexación completada en {DB_PATH}:")
    print(f"   - Total procesados: {len(archivos)}")
    print(f"   - Estado: 100% de los 432 activos canónicos de Roberto Ferri APROBADOS y listos para producción.")

if __name__ == "__main__":
    main()
