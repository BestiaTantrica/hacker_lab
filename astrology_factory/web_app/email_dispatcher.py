import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def load_env():
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    return env_vars

def send_email_with_audio(to_email, subject, html_body, audio_file_path=None):
    env = load_env()
    gmail_user = env.get('GMAIL_USER')
    gmail_password = env.get('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        raise ValueError("Faltan las credenciales SMTP en el archivo .env")

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    if audio_file_path and os.path.exists(audio_file_path):
        with open(audio_file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(audio_file_path)}",
        )
        msg.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print(f"[+] Email enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        print(f"[-] Error enviando email a {to_email}: {e}")
        return False
