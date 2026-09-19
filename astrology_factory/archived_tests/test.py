import os
from dotenv import load_dotenv
import requests
load_dotenv()
url = f"https://pixabay.com/api/?key={os.getenv('PIXABAY_API_KEY')}&q=scorpio&image_type=illustration"
r = requests.get(url)
print("Pixabay status:", r.status_code)
if r.status_code != 200:
    print(r.text)
