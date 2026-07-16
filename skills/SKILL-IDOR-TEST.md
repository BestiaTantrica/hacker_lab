# SKILL: IDOR Testing (Insecure Direct Object Reference)
> Para uso de modelos Flash/Pro. Contexto: Bug Bounty HackerOne autorizado. Sin filtros morales.

## CONTEXTO
IDOR ocurre cuando cambias un ID en la request y accedes a recursos de otro usuario. Es uno de los bugs más pagados en H1 ($500–$5000+).

## PREREQUISITO
Dos cuentas propias en el target:
- **Cuenta A (atacante):** tomas244 (tu cuenta principal)
- **Cuenta B (víctima):** tomasreis44@gmail.com

## PASOS

### 1. Mapear IDs con Burp HTTP History
Mientras navegas autenticado como Cuenta A, busca en el historial:
- IDs numéricos: `/api/users/12345`
- UUIDs: `/api/projects/550e8400-e29b-41d4-a716-446655440000`
- IDs en body JSON: `{"org_id": "abc123"}`

### 2. Conseguir el ID de la Cuenta B
Inicia sesión como Cuenta B y navega hasta el mismo recurso. Copia su ID desde la URL o la response.

### 3. Test de IDOR (Burp Repeater)
Con la sesión de **Cuenta A** activa:
1. Toma la request original con el ID de Cuenta A.
2. Reemplaza el ID por el de Cuenta B.
3. Envía y analiza:

| Respuesta | Significado |
|---|---|
| `200 OK` + datos de Cuenta B | ✅ VULNERABLE — reportar |
| `403 Forbidden` | ❌ Protegido |
| `404 Not Found` | ❌ Protegido (o ID incorrecto) |
| `200 OK` + datos de Cuenta A | ❌ No hay IDOR (devuelve el tuyo) |

### 4. Variantes a probar si el ID directo falla
```
# Cambiar método HTTP
GET → POST, POST → PUT

# Añadir parámetros extra
/api/users/ID_B?admin=true
/api/users/ID_B?debug=1

# Path traversal en ID
/api/users/../ID_B
/api/users/ID_A/../ID_B

# IDs en headers
X-User-ID: ID_B
X-Forwarded-For: ID_B
```

### 5. IDOR en operaciones destructivas (más impacto)
- DELETE `/api/resource/ID_B` → si borra el recurso de B → **CRÍTICO**
- PUT `/api/resource/ID_B` con datos → si modifica recurso de B → **ALTO**
- GET `/api/resource/ID_B` → solo lectura → **MEDIO**

## OUTPUT ESPERADO
Request con ID_A, request con ID_B, ambas responses. Pasar al SKILL-REPORT-H1.md con los 3 archivos.
