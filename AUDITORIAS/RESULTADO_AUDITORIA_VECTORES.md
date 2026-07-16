# 📊 REPORTE DE AUDITORÍA DE VECTORES DE MONGO

- **Ejecutado**: Automáticamente desde `auditar_vectores.py`
- **Cabecera obligatoria**: `X-HackerOne-Research: tomas244`
- **Cuenta A (Tester)**: Org ID `6a4c0a54b388b65b11799a24` | Proj ID `6a4c0a54b388b65b11799a58`
- **Cuenta B (Víctima)**: Org ID `6a4d7d849d5dcab6abad6820` | Proj ID `6a4d7d849d5dcab6abad6845`

## Resumen de Resultados

| Vector | Prueba | Endpoint | Status | Error Code | Response Preview / CORS Headers |
|---|---|---|---|---|---|
| Vector 4 (Billing) | Billing: payingOrg (Cuenta A - Propio) | `https://cloud.mongodb.com/billing/payingOrg/6a4c0a54b388b65b11799a24` | **404** | `N/A` | `{ "message":"Not Found", "url":"https://cloud.mongodb.com/billing/payingOrg/6a4c0a54b388b65b11799a24", "status":"404" }` |
| Vector 4 (Billing) | Billing: payingOrg (Cuenta B - Víctima) | `https://cloud.mongodb.com/billing/payingOrg/6a4d7d849d5dcab6abad6820` | **403** | `N/A` | `{"errorCode":"FORBIDDEN","version":"1","status":"ERROR"}` |
| Vector 4 (Billing) | Billing: payingOrg (Org Falsa) | `https://cloud.mongodb.com/billing/payingOrg/6a4d7d849d5dcab6abad0000` | **403** | `N/A` | `{"errorCode":"FORBIDDEN","version":"1","status":"ERROR"}` |
| Vector 4 (Billing) | Billing: SupportActiveDate (Cuenta A - Propio) | `https://cloud.mongodb.com/billing/orgs/6a4c0a54b388b65b11799a24/projectLevelSupportActiveDate` | **404** | `N/A` | `{ "message":"Not Found", "url":"https://cloud.mongodb.com/billing/orgs/6a4c0a54b388b65b11799a24/projectLevelSupportActiv` |
| Vector 4 (Billing) | Billing: SupportActiveDate (Cuenta B - Víctima) | `https://cloud.mongodb.com/billing/orgs/6a4d7d849d5dcab6abad6820/projectLevelSupportActiveDate` | **403** | `N/A` | `{"errorCode":"FORBIDDEN","version":"1","status":"ERROR"}` |
| Vector 4 (Billing) | Billing: SupportActiveDate (Org Falsa) | `https://cloud.mongodb.com/billing/orgs/6a4d7d849d5dcab6abad0000/projectLevelSupportActiveDate` | **403** | `N/A` | `{"errorCode":"FORBIDDEN","version":"1","status":"ERROR"}` |
| Vector 5 (AI Keys) | AI Keys: Paginated (Cuenta A -> Proy A) | `https://cloud.mongodb.com/aiModelApi/6a4c0a54b388b65b11799a24/apiKeys/project/6a4c0a54b388b65b11799a58/paginated?pageNum=1&itemsPerPage=100` | **200** | `N/A` | `{"links":[{"href":"https://cloud.mongodb.com/aiModelApi/6a4c0a54b388b65b11799a24/apiKeys/project/6a4c0a54b388b65b11799a5` |
| Vector 5 (AI Keys) | AI Keys: Paginated (Cuenta A -> Proy B) | `https://cloud.mongodb.com/aiModelApi/6a4d7d849d5dcab6abad6820/apiKeys/project/6a4d7d849d5dcab6abad6845/paginated?pageNum=1&itemsPerPage=100` | **200** | `N/A` | `<!DOCTYPE html> <html lang="en">  <head>       <title>Cloud: MongoDB Cloud</title>     <meta http-equiv="Content-Type" c` |
| Vector 5 (AI Keys) | AI Keys: Paginated (Cruzado Org A -> Proy B) | `https://cloud.mongodb.com/aiModelApi/6a4c0a54b388b65b11799a24/apiKeys/project/6a4d7d849d5dcab6abad6845/paginated?pageNum=1&itemsPerPage=100` | **200** | `N/A` | `<!DOCTYPE html> <html lang="en">  <head>       <title>Cloud: MongoDB Cloud</title>     <meta http-equiv="Content-Type" c` |
| Vector 5 (AI Keys) | AI Keys: Paginated (Cruzado Org B -> Proy A) | `https://cloud.mongodb.com/aiModelApi/6a4d7d849d5dcab6abad6820/apiKeys/project/6a4c0a54b388b65b11799a58/paginated?pageNum=1&itemsPerPage=100` | **200** | `N/A` | `{"links":[{"href":"https://cloud.mongodb.com/aiModelApi/6a4d7d849d5dcab6abad6820/apiKeys/project/6a4c0a54b388b65b11799a5` |
| Vector 6 (AuthCode GET) | AuthCode GET (Con Sesión) | `https://cloud.mongodb.com/user/authCodeCreationTimestamp` | **200** | `N/A` | `{"authCodeCreationTimestamp":1784089946902,"errorCode":"NONE","version":"1","status":"OK"}` |
| Vector 6 (CORS GET authenticated) | AuthCode GET (Con Sesión + Origin: evil.mongodb.com) | `https://cloud.mongodb.com/user/authCodeCreationTimestamp` | **403** | `N/A` | `ACAO: None | ACAC: None` |
| Vector 6 (CORS Preflight) | AuthCode OPTIONS (Preflight Origin: evil.mongodb.com) | `https://cloud.mongodb.com/user/authCodeCreationTimestamp` | **204** | `N/A` | `ACAO: https://evil.mongodb.com | ACAC: true` |

## Conclusiones Técnicas

### 1. Vector 4 — Enumeración de Billing
- Si los códigos de error difieren entre la Org B y la Org Falsa, se confirma un oráculo de divulgación de información.
- Si ambos retornan un HTML 404 genérico o el mismo código de error, el endpoint no es explotable para enumerar.

### 2. Vector 5 — AI API Keys IDOR
- Si el cruce (Org A consultando Proy B o viceversa) devuelve un status **200 OK** con resultados (o incluso vacío `[]` sin 403), representa una vulnerabilidad de control de acceso.
- Si devuelve **403 Forbidden** o **401 Unauthorized**, la protección de acceso está implementada de manera correcta.

### 3. Vector 6 — CORS / AuthCode
- Si el preflight de OPTIONS con Origin `https://evil.mongodb.com` refleja ese origin en la cabecera `Access-Control-Allow-Origin`, indica un bypass CORS explotable mediante XSS en cualquier subdominio.
