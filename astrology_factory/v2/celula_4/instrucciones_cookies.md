# 🍪 Extracción de Cookies para TikTok (Automatización)

Dado que elegimos tener la vía de automatización web (bot) como contingencia para publicar en TikTok sin esperar la aprobación de la API Oficial, necesitamos que el bot se "disfrace" de tu navegador.

Para esto, tenés que exportar las "cookies" (los datos de tu sesión iniciada) de TikTok.

## Pasos a seguir (Solo se hace una vez):

1. **Instalá una extensión para extraer cookies** en Google Chrome. Te recomiendo encarecidamente **"EditThisCookie"** o **"Get cookies.txt LOCALLY"** desde la Chrome Web Store.
2. Entrá a [TikTok.com](https://www.tiktok.com) desde tu compu y **asegurate de haber iniciado sesión** con la cuenta de Astrology Factory.
3. Una vez logueado en TikTok, hacé clic en el ícono de la extensión que instalaste (arriba a la derecha en Chrome).
4. Usá la opción de **Exportar (Export)**. Esto va a copiar todo el texto al portapapeles o descargar un archivo `cookies.txt`.
5. Si lo copió al portapapeles, abrí el Bloc de Notas (o cualquier editor de texto), pegalo y guardalo como `cookies.txt`.
6. Moví ese archivo `cookies.txt` a la siguiente carpeta:
   `/home/LAB/astrology_factory/v2/celula_4/`

> [!WARNING]
> Tu archivo `cookies.txt` es literalmente la llave maestra de tu cuenta. No lo compartas con nadie ni lo subas a internet. El script lo leerá localmente.

Cuando hayas guardado el archivo ahí, el publicador de TikTok ya podrá iniciar sesión automáticamente y subir tus videos.
