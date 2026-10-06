---
title: "Patrón de Subida Segura a Cloudflare R2 sin Exponer Secretos"
category: 08_Cloud
doc_type: patron
tags: [cloud, r2, storage, upload, presigned-url, workers, seguridad]
summary: "Patrón arquitectónico obligatorio para subir archivos a Cloudflare R2 desde aplicaciones web (React/Vite) sin exponer jamás R2_ACCESS_KEY_ID ni R2_SECRET_ACCESS_KEY en el cliente. Implementación vía Presigned URLs y Worker Direct Binding."
keywords: [r2, cloudflare, s3, upload, presigned, signed-url, vite, seguridad, storage]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "Cloudflare Docs — R2 Object Storage / Presigned URLs"
  - "05_Security/SECRET_LEAK_PREVENTION_STANDARD.md"
  - "05_Security/SECURITY_ENGINEERING_STANDARD.md"
---

# PATRÓN DE SUBIDA SEGURA A CLOUDFLARE R2 (CERO SECRETOS EN FRONTEND)

> 🔒 **Regla Inquebrantable:** `R2_ACCESS_KEY_ID` y `R2_SECRET_ACCESS_KEY` son credenciales maestras que otorgan control total sobre tu bucket (lectura, escritura y borrado de todos los archivos). **Jamás deben llevar el prefijo `VITE_` ni estar presentes en el código frontend.**

---

## 1. El Error Común vs. La Solución Arquitectónica

```
❌ ERROR COMÚN (Exposición de Llaves Maestras):
[ Frontend (React/Vite) ] ──(con VITE_R2_SECRET_ACCESS_KEY)──► [ Cloudflare R2 ]
                                    ▲
                 Cualquier usuario puede borrar todo el bucket R2

✅ SOLUCIÓN 1: Worker Direct Binding (Para archivos pequeños / medianos < 100MB):
[ Frontend ] ──(1. formData con Auth Token)──► [ Cloudflare Worker ] ──(2. env.MY_BUCKET.put())──► [ R2 Bucket ]

✅ SOLUCIÓN 2: Presigned URLs (Para archivos grandes o subida directa optimizada):
[ Frontend ] ──(1. POST /api/upload/presign)──► [ Cloudflare Worker ] (Genera URL firmada con TTL de 5 min)
[ Frontend ] ◄──(2. Devuelve presignedUrl)─────┘
[ Frontend ] ──(3. PUT directo del binario a la presignedUrl)──► [ Cloudflare R2 ]
```

---

## 2. Implementación de Referencia (Worker Direct Upload)

### A. Backend (Cloudflare Worker)
En `wrangler.toml`, enlazas el bucket directamente sin necesidad de credenciales de AWS S3:

```toml
# wrangler.toml
name = "api-gateway"
main = "src/index.ts"
compatibility_date = "2026-08-01"

[[r2_buckets]]
binding = "UPLOADS_BUCKET"
bucket_name = "tu-bucket-nombre"
```

En tu endpoint de upload:

```typescript
// src/handlers/upload.ts
import { requireAuth } from '../middleware/auth'

export async function handleUpload(request: Request, env: Env) {
  // 1. Validar autenticación de usuario
  const user = await requireAuth(request, env)
  if (!user) {
    return new Response(JSON.stringify({ ok: false, error: 'Unauthorized' }), { status: 401 })
  }

  // 2. Extraer archivo de la petición
  const formData = await request.formData()
  const file = formData.get('file') as File | null

  if (!file) {
    return new Response(JSON.stringify({ ok: false, error: 'No file provided' }), { status: 400 })
  }

  // 3. Validar tipo y tamaño máximo (ej. máx 10MB para imágenes)
  const MAX_SIZE = 10 * 1024 * 1024
  if (file.size > MAX_SIZE) {
    return new Response(JSON.stringify({ ok: false, error: 'File too large (max 10MB)' }), { status: 413 })
  }

  // 4. Generar nombre único y seguro
  const extension = file.name.split('.').pop()
  const fileKey = `users/${user.id}/${crypto.randomUUID()}.${extension}`

  // 5. Guardar en R2 mediante el binding nativo del Worker (seguro y rápido)
  await env.UPLOADS_BUCKET.put(fileKey, file.stream(), {
    httpMetadata: { contentType: file.type }
  })

  // 6. Devolver la URL pública o clave del archivo
  const publicUrl = `https://recursos.tu-dominio.com/${fileKey}`
  return new Response(JSON.stringify({ ok: true, url: publicUrl }), {
    headers: { 'Content-Type': 'application/json' }
  })
}
```

---

### B. Frontend (React / Vite)

En el frontend, el componente solo envía el archivo a tu propio endpoint usando `fetch` estándar:

```typescript
// src/services/uploadService.ts
export async function uploadUserAvatar(file: File, userToken: string): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${import.meta.env.VITE_API_URL}/api/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userToken}`
    },
    body: formData
  })

  const result = await response.json()
  if (!result.ok) throw new Error(result.error || 'Error subiendo archivo')
  return result.url
}
```

* **Resultado:** El frontend **no conoce ni necesita ninguna clave de R2**. Si alguien inspecciona el bundle o las variables `.env`, solo verá la URL del endpoint.
