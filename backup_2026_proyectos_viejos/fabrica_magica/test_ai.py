import os, json
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
prompt = """Genera un guion para Sol en Aries.
Reglas: Humos acido, directo.
Devuelve SOLO un JSON valido con esta estructura, sin markdown, sin nada mas:
{"hook": "Frase lapidaria corta", "body": "Dos oraciones explicando el patron toxico real", "stats": "Iniciativa 10/10, Constancia 1/10"}"""
res = client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama3-8b-8192"
)
try:
    data = json.loads(res.choices[0].message.content.strip())
    print("EXITO JSON:")
    print(data)
except Exception as e:
    print("ERROR:", e)
    print("CONTENT:", res.choices[0].message.content)
