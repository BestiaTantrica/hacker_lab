import subprocess
import json
import os
import sys
import re

sys.path.append(os.path.dirname(__file__))
from content_factory.personalized_generator import PersonalizedGenerator
from content_factory.audio_generator import AudioGenerator
from email_dispatcher import send_email_with_audio, load_env

env = load_env()
if 'GEMINI_API_KEY' not in os.environ and 'GEMINI_API_KEY' in env:
    os.environ['GEMINI_API_KEY'] = env['GEMINI_API_KEY']

def fetch_pending_welcome():
    cmd = 'ssh -o StrictHostKeyChecking=no -i /home/LAB/llave_oci ubuntu@143.47.115.34 "python3 -c \\"import sqlite3, json; conn=sqlite3.connect(\'/home/ubuntu/c2_panel/database/users.sqlite\'); c=conn.cursor(); c.execute(\'SELECT name, email, birth_date, birth_time, birth_city FROM subscribers WHERE welcome_sent=0\'); cols=[d[0] for d in c.description]; print(json.dumps([dict(zip(cols, row)) for row in c.fetchall()]))\\""'
    try:
        res = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        if res:
            return json.loads(res)
    except Exception as e:
        print(f"Error conectando con OCI-2: {e}")
    return []

def mark_welcome_sent(email):
    cmd = f'ssh -o StrictHostKeyChecking=no -i /home/LAB/llave_oci ubuntu@143.47.115.34 "python3 -c \\"import sqlite3; conn=sqlite3.connect(\'/home/ubuntu/c2_panel/database/users.sqlite\'); conn.execute(\'UPDATE subscribers SET welcome_sent=1 WHERE email=?\', (\'{email}\',)); conn.commit()\\""'
    subprocess.call(cmd, shell=True)

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def process_subscribers():
    pending = fetch_pending_welcome()
    if not pending:
        print("No hay suscriptores pendientes de bienvenida.")
        return
        
    generator = PersonalizedGenerator()
    audio_gen = AudioGenerator("es-MX-JorgeNeural")
    
    # Directorio temporal para los audios
    os.makedirs("/tmp/audios_horoscopo", exist_ok=True)
    
    for user in pending:
        name = user['name']
        email = user['email']
        birth_date = user['birth_date']
        
        print(f"\n[+] Procesando nuevo usuario: {name} ({email})")
        
        # 1. Generar HTML con Gemini
        print("    Generando lectura astral...")
        html_content = generator.generate_welcome_email(name, email, birth_date)
        
        if "Error" in html_content:
            print(f"    Error detectado en la IA, saltando a {email}.")
            continue
            
        # 2. Generar MP3
        print("    Generando audio locutado...")
        plain_text = strip_html_tags(html_content)
        # Limpiar links para que no los lea
        plain_text = plain_text.replace("ACTIVAR MI HORÓSCOPO SEMANAL", "")
        plain_text = plain_text.replace("nuestro último video en YouTube", "nuestro canal")
        
        audio_path = f"/tmp/audios_horoscopo/{email}_bienvenida.mp3"
        audio_gen.generate_audio(plain_text, audio_path)
        
        # 3. Enviar el correo
        print(f"    Enviando correo a {email}...")
        success = send_email_with_audio(email, "Bienvenido a tu Mapa Astral | Astrología de Precisión", html_content, audio_path)
        
        if success:
            mark_welcome_sent(email)
            print(f"    Usuario marcado como 'welcome_sent=1' en la base de datos.")
        
        # Limpiar audio
        if os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    process_subscribers()
