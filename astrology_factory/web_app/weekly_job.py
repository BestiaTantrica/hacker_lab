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

def run_weekly_reports():
    print(f"[{datetime.datetime.now()}] Iniciando generación de reportes semanales...")
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        # Buscar suscriptores semanales
        cursor.execute("SELECT name, email, birth_date, birth_time FROM subscribers WHERE wants_weekly = 1")
        users = cursor.fetchall()
        
        if not users:
            print("No hay suscriptores para el reporte semanal.")
            conn.close()
            return
            
        ph = PersonalizedHoroscope()
            
        for name, email, birth_date, birth_time in users:
            print(f"Generando reporte semanal para: {email}")
            
            try:
                # Usamos mode='weekly' para enfocar la lectura en los próximos 7 días
                result = ph.generate_for_user(name, birth_date, birth_time, mode='weekly')
                
                if result.get("error"):
                    print(f"La IA falló para {email}, se agendará para reintento.")
                    # Agendar en pending_emails
                    cursor.execute(
                        "INSERT INTO pending_emails (user_email, status, error_log) VALUES (?, 'pending', 'Weekly AI Error')",
                        (email,)
                    )
                    conn.commit()
                else:
                    html_content = result.get("mensaje_personalizado", "")
                    
                    # Enviar correo (asumiendo que no hay audio para los semanales o usamos dummy)
                    success = send_email_with_audio(email, name, html_content, audio_path=None)
                    
                    if success:
                        print(f"Reporte semanal enviado a {email}")
                    else:
                        print(f"Fallo al enviar correo a {email}")
                        
            except Exception as e:
                print(f"Error procesando usuario {email}: {e}")
                traceback.print_exc()
                
        conn.close()
        print(f"[{datetime.datetime.now()}] Proceso semanal finalizado.")
        
    except Exception as e:
        print(f"Error crítico en weekly_job: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_weekly_reports()
