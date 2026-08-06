#!/usr/bin/env python3
"""
Script de Purga Orientada a Eventos para c2_db.sqlite
Uso: python3 purga_eventual.py <target_a_purgar>
Ejemplo: python3 purga_eventual.py "empresa-vieja.com"
"""
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_db.sqlite')

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 purga_eventual.py <dominio_a_purgar>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"[*] Iniciando purga de deltas para el objetivo: {target}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Eliminar deltas
        # Asumiendo que la tabla se llama 'deltas' y la columna 'domain' (según el contexto habitual del panel C2)
        # NOTA: Ajustar si la tabla tiene una estructura diferente
        cursor.execute("DELETE FROM deltas WHERE domain LIKE ?", (f"%{target}%",))
        deleted_rows = cursor.rowcount
        conn.commit()
        
        print(f"[+] Se eliminaron {deleted_rows} registros de la tabla 'deltas'.")

        # Ejecutar VACUUM para recuperar espacio
        print("[*] Ejecutando VACUUM para compactar la base de datos...")
        cursor.execute("VACUUM")
        conn.commit()

        print("[+] Saneamiento completado con éxito.")
    except Exception as e:
        print(f"[-] Error durante la purga: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
