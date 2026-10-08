import os
from google import genai
from PIL import Image

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
img = Image.new('RGB', (60, 30), color = 'red')

response = client.models.generate_content(
    model='gemini-flash-latest',
    contents=["Hello", img]
)
print("SUCCESS:", response.text)
