# SKILL: Subdomain Takeover Testing
> Para uso de modelos Flash/Pro. Contexto: Bug Bounty HackerOne autorizado.

## CONTEXTO
Un subdominio apunta (CNAME) a un servicio externo (Heroku, GitHub Pages, S3, Azure, etc.) que ya no existe o no está reclamado. Podés registrar ese servicio y tomar control del subdominio.

## PASOS

### 1. Detectar CNAMEs colgantes (dangling)
```bash
# Para una lista de subdominios
cat subdominios_crudos.txt | dnsx -cname -o cnames.txt

# Ver los resultados
cat cnames.txt | grep -iE "heroku|github|s3|azure|vercel|netlify|shopify|fastly|squarespace|cargo|launchrock|unbounce|surge|bitbucket"
```

### 2. Verificar si el servicio está sin reclamar
Para cada CNAME encontrado:
```bash
curl -s https://SUBDOMINIO.TARGET.com | head -50
```

Respuestas que indican takeover posible:

| Servicio | Respuesta vulnerable |
|---|---|
| GitHub Pages | `There isn't a GitHub Pages site here` |
| Heroku | `No such app` |
| AWS S3 | `NoSuchBucket` |
| Azure | `404 Web Site not Found` |
| Shopify | `Sorry, this shop is currently unavailable` |
| Fastly | `Fastly error: unknown domain` |

### 3. Reclamar el servicio (según plataforma)

**GitHub Pages:**
1. Crear repo: `github.com/TU_USUARIO/NOMBRE_DEL_SUBDOMINIO`
2. En Settings → Pages → Custom Domain → escribir el subdominio vulnerable
3. Verificar que sirve contenido desde el subdominio del target

**Heroku:**
1. `heroku create NOMBRE-DEL-APP-EN-CNAME`
2. `heroku domains:add SUBDOMINIO.TARGET.com`

**AWS S3:**
1. Crear bucket con el nombre exacto del CNAME (ej: `assets.target.com`)
2. Habilitar Static Website Hosting

### 4. Crear PoC mínimo (sin daño)
Subir un archivo `index.html` con contenido inocuo:
```html
<h1>Subdomain Takeover PoC - Bug Bounty Research</h1>
<p>Este subdominio fue tomado con fines de investigación de seguridad autorizada.</p>
<p>Investigador: tomas244 (HackerOne)</p>
```

### 5. Verificar y documentar
```bash
curl -s https://SUBDOMINIO.TARGET.com
# Debe devolver tu index.html
```

Screenshot de: el CNAME en DNS, la respuesta del servicio sin reclamar, y tu contenido servido.

## CRITERIO DE REPORTE
- Tomar el subdominio y mostrar que sirve tu contenido → **ALTO/CRÍTICO**
- Solo detectar el CNAME sin reclamar → NO reportar sin PoC. H1 rechaza sin evidencia.

## OUTPUT ESPERADO
3 screenshots + el comando dig que muestra el CNAME. Pasar a SKILL-REPORT-H1.md.
