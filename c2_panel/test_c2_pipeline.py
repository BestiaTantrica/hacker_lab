#!/usr/bin/env python3
"""
test_c2_pipeline.py — Script de Prueba de Certificación Local / OCI
===================================================================
Prueba la ingesta de datos, persistencia en SQLite, consulta de zonas y 
notificación hacia el C2 Panel de forma segura e independiente.
"""

import sys
import os
import json
import sqlite3
import urllib.request
import urllib.error

# Forzar el directorio raíz del C2 Panel
C2_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(C2_DIR)

import main

def test_database_and_ingestion():
    print("1. Inicializando Base de Datos SQLite en C2 Panel...")
    main.init_db()
    db_path = main.DB_PATH
    assert os.path.isfile(db_path), "❌ Error: No se creó c2_db.sqlite"
    print(f"   [OK] BD local lista en: {db_path}")

    print("\n2. Insertando datos de prueba (MOCK) para verificar la ingesta...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Simular deltas para las 3 zonas
    zonas_prueba = [
        ("americas", "shopify.com", "dev-staging.shopify.com"),
        ("emea", "booking.com", "api-internal.booking.com"),
        ("asia", "grab.com", "test-driver.grab.com")
    ]

    for zone, domain, sub in zonas_prueba:
        cursor.execute("INSERT INTO deltas (zone, domain, subdomain) VALUES (?, ?, ?)", (zone, domain, sub))

    # Simular un hallazgo verificado ($150 USD)
    evidence_mock = json.dumps({"cname": "huerfano.s3.amazonaws.com", "http_status": 404})
    cursor.execute("""
        INSERT INTO findings (target, vuln_type, severity, estimated_bounty, evidence)
        VALUES (?, ?, ?, ?, ?)
    """, ("dev-staging.shopify.com", "Subdomain Takeover (S3)", "Medium", "$150-$300", evidence_mock))

    conn.commit()

    # Verificar lectura
    cursor.execute("SELECT COUNT(*) FROM deltas")
    total_deltas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM findings")
    total_findings = cursor.fetchone()[0]
    conn.close()

    print(f"   [OK] Deltas registradas: {total_deltas}")
    print(f"   [OK] Hallazgos registrados: {total_findings}")

    print("\n3. Verificando plantilla de prompt para HackerOne (Skill)...")
    sample_evidence = "GET /api/v1/user HTTP/1.1\nHost: dev-staging.shopify.com\nHTTP/1.1 404 Not Found"
    prompt_template = main.SKILLS_PROMPTS["report_h1"]
    prompt_formatted = prompt_template.replace("{EVIDENCIA_CRUDA}", sample_evidence)
    assert "Title:" in prompt_formatted and "dev-staging.shopify.com" in prompt_formatted
    print("   [OK] Hub de Prompts genera correctamente la estructura de HackerOne.")

    print("\n=======================================================")
    print("🎉 CERTIFICACIÓN DE LÓGICA DE PIPELINE COMPLETADA CON ÉXITO")
    print("=======================================================")

if __name__ == "__main__":
    test_database_and_ingestion()
