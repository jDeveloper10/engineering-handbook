---
title: "Incident Playbook: Upload Fail"
category: 11_Debugging
tags: [incident, playbook, upload, r2, timeout]
status: current
---

# 🚨 PLAYBOOK: UPLOAD FAIL (CARGA INFINITA)

## 🩺 SÍNTOMA
El usuario intenta subir una imagen, documento o archivo y la UI se queda en estado de "Loading" o "Subiendo..." indefinidamente. No hay mensaje de error, no pasa nada.

## ⏱️ DIAGNÓSTICO EN 30 SEGUNDOS
1. **Frontend:** Abre la pestaña **Network** (DevTools). Busca el request POST/PUT. ¿Sigue en `pending`? ¿Tiró `CORS error`? ¿Dio HTTP 413 (Payload Too Large)?
2. **Backend:** Abre el dashboard de Cloudflare Workers. Busca excepciones recientes o *Memory Limit Exceeded*.
3. **Storage:** Revisa R2. ¿El archivo llegó pero el Worker no respondió?

---

## 🔍 CAUSAS Y SOLUCIONES DE HIERRO

### Causa 1: Timeout en el Frontend (Request Colgado)
Si la red es inestable, el request se cuelga eternamente.
**Solución:** ES OBLIGATORIO usar un `AbortController` con timeout. PROHIBIDO hacer `fetch` ciego.

### Causa 2: Worker Sin Memoria (128MB Default)
Si el archivo se procesa en el Worker (`request.arrayBuffer()`) y pesa más de 50MB, el Worker colapsa por RAM.
**Solución:** NUNCA procesar archivos grandes en RAM. Usar `Streams` directo a R2, o bien aumentar la memoria si es estrictamente necesario (no recomendado).
```toml
# wrangler.toml (Si necesitas más de 128MB, usar Unbound)
[limits]
memory = 256 # Máximo
```

### Causa 3: Archivo Excede el Límite de Cloudflare (100MB)
Cloudflare free/pro bloquea payloads > 100MB antes de tocar tu Worker.
**Solución:** ES OBLIGATORIO validar el tamaño del archivo en el cliente ANTES de enviarlo.

### Causa 4: Error de CORS
Si la subida va directa a un bucket R2 presigned, el CORS del bucket bloquea el `PUT`.
**Solución:** Configurar las reglas de CORS en el bucket R2.
```json
[
  {
    "AllowedOrigins": ["https://tu-app.com"],
    "AllowedMethods": ["PUT", "POST", "GET"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

### Causa 5: R2 Bucket No Existe o Permisos Rotos
El binding no está configurado en producción.
**Solución:** Validar el `wrangler.toml` y asegurar que `[[r2_buckets]]` apunte al bucket correcto en producción.

---

## 💻 CÓDIGO REAL: HOOK DE UPLOAD BLINDADO

ES OBLIGATORIO usar este hook (o su equivalente) para subir archivos. NUNCA crear implementaciones caseras sin timeout ni validación.

```tsx
import { useState, useRef } from 'react'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
const TIMEOUT_MS = 15000 // 15 segundos máximo

export function useFileUpload() {
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const abortControllerRef = useRef<AbortController | null>(null)

  const uploadFile = async (file: File, uploadUrl: string) => {
    // 1. VALIDACIONES INQUEBRANTABLES
    if (file.size > MAX_FILE_SIZE) {
      setError('El archivo excede el límite de 5MB.')
      return false
    }
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Formato no permitido. Solo JPG, PNG o PDF.')
      return false
    }

    setIsUploading(true)
    setError(null)
    setProgress(0)

    // 2. TIMEOUT CON ABORT CONTROLLER
    abortControllerRef.current = new AbortController()
    const timeoutId = setTimeout(() => {
      abortControllerRef.current?.abort()
    }, TIMEOUT_MS)

    try {
      // Simular progreso en frontend (XMLHttpRequest es necesario para progreso real, 
      // pero fetch no lo soporta nativo para upload, así que usamos un timer falso o delegamos al SDK)
      const progressInterval = setInterval(() => setProgress(p => Math.min(p + 10, 90)), 500)

      const response = await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type },
        signal: abortControllerRef.current.signal
      })

      clearInterval(progressInterval)
      clearTimeout(timeoutId)

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`)
      }

      setProgress(100)
      return true
    } catch (err: unknown) {
      clearTimeout(timeoutId)
      if (err instanceof Error && err.name === 'AbortError') {
        setError('Tiempo de espera agotado. Revisa tu conexión.')
      } else {
        setError('No pudimos subir el archivo. Inténtalo de nuevo.')
      }
      return false
    } finally {
      setIsUploading(false)
      abortControllerRef.current = null
    }
  }

  const cancelUpload = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setError('Subida cancelada por el usuario.')
    }
  }

  return { uploadFile, cancelUpload, isUploading, progress, error }
}
```
