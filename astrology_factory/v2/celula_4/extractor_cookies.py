#!/usr/bin/env python3
import browser_cookie3
import http.cookiejar
import json
import os

def extract_tiktok_cookies():
    print("🍪 Extrayendo cookies de navegadores...")
    cookies_path = '/home/LAB/astrology_factory/v2/celula_4/cookies.txt'
    
    with open(cookies_path, 'w') as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
        f.write("# This is a generated file!  Do not edit.\n\n")

    found_cookies = False

    # Check Chrome
    try:
        cj_chrome = browser_cookie3.chrome(domain_name='tiktok.com')
        for cookie in cj_chrome:
            found_cookies = True
            append_cookie(cookies_path, cookie)
    except Exception as e:
        print(f"No se pudieron leer cookies de Chrome: {e}")

    # Check Chromium
    try:
        cj_chromium = browser_cookie3.chromium(domain_name='tiktok.com')
        for cookie in cj_chromium:
            found_cookies = True
            append_cookie(cookies_path, cookie)
    except Exception as e:
        print(f"No se pudieron leer cookies de Chromium: {e}")

    if found_cookies:
        print(f"✅ ¡Cookies extraídas exitosamente a {cookies_path}!")
    else:
        print("❌ No se encontraron cookies de TikTok en ningún navegador.")

def append_cookie(path, cookie):
    with open(path, 'a') as f:
        domain = cookie.domain
        initial_dot = 'TRUE' if domain.startswith('.') else 'FALSE'
        c_path = cookie.path
        secure = 'TRUE' if cookie.secure else 'FALSE'
        expires = str(cookie.expires) if cookie.expires else '0'
        name = cookie.name
        value = cookie.value
        f.write(f"{domain}\t{initial_dot}\t{c_path}\t{secure}\t{expires}\t{name}\t{value}\n")

if __name__ == '__main__':
    extract_tiktok_cookies()
