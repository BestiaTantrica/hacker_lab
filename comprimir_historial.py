#!/usr/bin/env python3
"""
Script interactivo para comprimir (summarize) el historial de chat en OCI-2.
Lee los registros antiguos, genera un resumen macro con IA, solicita confirmación
y limpia la base de datos manteniendo solo el resumen.
"""
import sqlite3
import os
import sys

# Ajustar el sys.path si es necesario para importar llm_client
C2_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(C2_DIR)
sys.path.append(os.path.join(C2_DIR, "..", "espejo_oci1", "api"))

try:
    from llm_client import completar
except ImportError:
    print("[-] Error: No se pudo importar llm_client. Asegúrate de estar en el entorno de C2.")
    sys.exit(1)

DB_PATH = os.path.join(C2_DIR, 'c2_db.sqlite')

def main():
    print("[*] Iniciando proceso de Compresión de Contexto de Chat History...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Seleccionar mensajes viejos (por ejemplo, todo excepto los últimos 10)
        # O podríamos comprimir los mensajes más viejos (los primeros 50)
        cursor.execute("SELECT id, source, role, message FROM chat_history ORDER BY id ASC LIMIT 50")
        rows = cursor.fetchall()

        if not rows:
            print("[i] No hay suficiente historial para comprimir.")
            return

        chat_text = ""
        max_id = 0
        for r in rows:
            chat_text += f"[{r['source'].upper()}] {r['role']}: {r['message']}\n"
            if r['id'] > max_id:
                max_id = r['id']

        print(f"[i] Se van a comprimir {len(rows)} mensajes (hasta ID {max_id}).")

        # Generar el resumen
        prompt = f"""Escribe un resumen ejecutivo y consolidado del siguiente historial de operaciones, enfocándote en las decisiones arquitectónicas clave, hallazgos importantes y acciones tomadas. Omite el ruido y mensajes triviales.
Historial:
{chat_text}"""
        
        print("[*] Generando resumen con IA (esto puede tomar unos segundos)...")
        resumen = completar(prompt, max_tokens=500)
        
        if not resumen:
            print("[-] No se pudo generar el resumen.")
            return

        print("\n" + "="*50)
        print("RESUMEN PROPUESTO:")
        print("="*50)
        print(resumen)
        print("="*50 + "\n")

        # Fricción operativa
        confirm = input("[?] ¿Aceptas reemplazar estos mensajes crudos por este resumen? (s/n): ")
        if confirm.lower() == 's':
            # Borrar los mensajes crudos
            cursor.execute("DELETE FROM chat_history WHERE id <= ?", (max_id,))
            
            # Insertar el resumen como un nuevo mensaje de sistema o assistant
            cursor.execute("INSERT INTO chat_history (source, role, message) VALUES ('system', 'assistant', ?)", (f"RESUMEN HISTÓRICO: {resumen}",))
            
            # Limpiar DB
            cursor.execute("VACUUM")
            conn.commit()
            print("[+] Historial comprimido y base de datos optimizada exitosamente.")
        else:
            print("[i] Operación cancelada. El historial se mantiene intacto.")

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
