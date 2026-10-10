import os
import sys
import sqlite3
import datetime
import traceback

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)

from content_factory.personalized_horoscope import PersonalizedHoroscope
from web_app.email_dispatcher import send_email_with_audio

DB_PATH = os.path.join(BASE_DIR, "database", "users.sqlite")

def run_retries():
    print(f"[{datetime.datetime.now()}] Iniciando reintento de emails pendientes...")
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        # Buscar pendientes
        cursor.execute("SELECT id, user_email FROM pending_emails WHERE status = 'pending'")
        pendings = cursor.fetchall()
        
        if not pendings:
            print("No hay emails pendientes.")
            conn.close()
            return
            
        ph = PersonalizedHoroscope()
            
        for pending_id, email in pendings:
            print(f"Procesando reintento para: {email}")
            
            # Obtener datos del suscriptor
            cursor.execute("SELECT name, birth_date, birth_time FROM subscribers WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                print(f"Usuario {email} no encontrado en subscribers. Marcando como failed.")
                cursor.execute("UPDATE pending_emails SET status = 'failed' WHERE id = ?", (pending_id,))
                conn.commit()
                continue
                
            name, birth_date, birth_time = user
            
            try:
                res = ph.generate_for_user(name, birth_date, birth_time)
                
                if not res.get("error"):
                    html_response = res.get("mensaje_personalizado", "")
                    email_body = f"<h1>Hola {name}, aquí está tu lectura inicial:</h1><br>" + html_response
                    
                    send_email_with_audio(email, "Bienvenido al Oráculo - Tu Primera Lectura", email_body)
                    
                    cursor.execute("UPDATE pending_emails SET status = 'completed' WHERE id = ?", (pending_id,))
                    conn.commit()
                    print(f"Email enviado exitosamente a {email}.")
                else:
                    print(f"La IA volvió a fallar para {email}. Se reintentará en el próximo ciclo.")
            except Exception as e:
                print(f"Error procesando a {email}: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"Error crítico en reintentos: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    run_retries()
