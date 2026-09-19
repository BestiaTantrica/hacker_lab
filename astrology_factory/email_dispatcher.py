import json
import os
import sys

# Agregar la raíz del proyecto al path
sys.path.append(os.path.dirname(__file__))
from content_factory.personalized_horoscope import PersonalizedHoroscope

class EmailDispatcher:
    def __init__(self):
        self.horoscope_engine = PersonalizedHoroscope()
        
    def get_users_from_db(self):
        # Placeholder para la base de datos de usuarios
        return [
            {
                "name": "Juan Perez",
                "email": "juan@example.com",
                "birth_date": "1990-05-15",
                "birth_time": "08:30",
                "lat": -34.6037,
                "lon": -58.3816
            }
        ]
        
    def send_weekly_newsletter(self):
        print("Iniciando envío de correos masivos personalizados...")
        users = self.get_users_from_db()
        
        for user in users:
            print(f"Calculando estudio sociológico y tránsitos para {user['name']}...")
            
            # El motor unificado se encarga de cruzar la natal completa + inyectar el video_context
            result = self.horoscope_engine.generate_for_user(
                user["name"], 
                user["birth_date"], 
                user["birth_time"], 
                user["lat"], 
                user["lon"]
            )
            
            mensaje_html = result.get("mensaje_personalizado", "")
            
            print(f"Enviando correo a {user['email']}...")
            # Placeholder: Aquí iría la lógica SMTP real (SendGrid, Mailgun, etc.)
            
            # Para propósitos de debug, lo guardamos en un archivo
            with open(f"email_debug_{user['name'].replace(' ', '_')}.html", "w", encoding="utf-8") as f:
                f.write(mensaje_html)
                
        print("Envío finalizado.")

if __name__ == "__main__":
    dispatcher = EmailDispatcher()
    dispatcher.send_weekly_newsletter()
