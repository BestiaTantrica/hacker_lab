import requests
from http.cookiejar import MozillaCookieJar

cookies = MozillaCookieJar('/home/LAB/astrology_factory/v2/celula_4/cookies.txt')
cookies.load(ignore_discard=True, ignore_expires=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

try:
    response = requests.get('https://www.tiktok.com/passport/web/account/info/', cookies=cookies, headers=headers)
    data = response.json()
    if data.get('message') == 'success':
        user_info = data.get('data', {})
        print("USERNAME:", user_info.get('username'))
        print("EMAIL:", user_info.get('email'))
    else:
        print("FAILED TO GET INFO:", data)
except Exception as e:
    print("ERROR:", e)
