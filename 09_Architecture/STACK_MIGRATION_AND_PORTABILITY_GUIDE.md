---
title: "Guía Universal de Migración y Portabilidad de Stack (Frontend, Backend, Storage y BD)"
category: 09_Architecture
doc_type: runbook
tags: [arquitectura, migracion, portabilidad, stack, cloudflare, vps, docker, r2, s3, zero-lock-in]
summary: "Protocolo completo de migración y portabilidad universal del stack de la agencia: cómo migrar frontend (Pages -> VPS/Vercel), backend (Workers -> Node/Bun/Docker), storage (R2 -> S3/MinIO) y autenticación sin reescribir código y con cero tiempo de inactividad."
keywords: [migracion-stack, portabilidad, zero-lock-in, cloudflare-a-vps, workers-a-node, r2-a-s3, docker]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "09_Architecture/STACK_SELECTION_MATRIX.md"
  - "08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md"
  - "04_Database/References/DATABASE_DISASTER_RECOVERY_MIGRATION.md"
---

# GUÍA UNIVERSAL DE MIGRACIÓN Y PORTABILIDAD DE STACK

> 🌐 **Principio de Cero Vendor Lock-in:** Tu agencia nunca debe quedar atrapada en un único proveedor de nube. Si Cloudflare, Supabase, Vercel o cualquier tercero cambia sus términos o sufre un incidente grave, todo el sistema puede migrarse a un VPS independiente (Docker / Node / PostgreSQL / MinIO) en menos de 1 hora.

---

## 1. Matriz de Portabilidad del Stack

```
┌─────────────────┬───────────────────────────────┬───────────────────────────────┐
│ Capa del Stack  │ Proveedor Primario (Edge)     │ Proveedor Alternativo (VPS)   │
├─────────────────┼───────────────────────────────┼───────────────────────────────┤
│ Frontend        │ Cloudflare Pages              │ VPS con Nginx / Caddy / Vercel│
│ Backend / API   │ Cloudflare Workers (Hono/Web) │ Node.js / Bun con Docker      │
│ Base de Datos   │ Supabase (PostgreSQL)         │ PostgreSQL 16 en VPS Docker   │
│ DB Ligera Edge  │ Cloudflare D1 (SQLite)        │ Turso / SQLite local          │
│ Storage         │ Cloudflare R2                 │ AWS S3 / MinIO (Self-hosted)  │
│ Auth            │ Supabase Auth (JWT)           │ Better-Auth / Lucia en Node   │
└─────────────────┴───────────────────────────────┴───────────────────────────────┘
```

---

## 2. Migración del Backend: Cloudflare Workers ➔ Node.js / Bun / VPS

### Cómo diseñar APIs portables por diseño
**[REQUIRED]** Todos los endpoints de backend usan la **API estándar de la Web** (`Request`, `Response`, `fetch`, `Headers`). Si necesitas mover un Worker a un contenedor Docker en un VPS Hetzner o AWS:

```typescript
// server-node.ts (Adaptador portable para correr Workers en Node/Docker)
import { createServer } from 'node:http'
import workerHandler from './src/index.js' // Tu código original de Cloudflare Worker

// Polyfill ligero para convertir peticiones de Node a Web Request
const server = createServer(async (req, res) => {
  const url = `http://${req.headers.host}${req.url}`
  const webRequest = new Request(url, {
    method: req.method,
    headers: req.headers as HeadersInit,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? req : undefined,
    // @ts-ignore
    duplex: 'half'
  })

  // Ejecutar el mismo handler del Worker
  const webResponse = await workerHandler.fetch(webRequest, process.env)

  res.writeHead(webResponse.status, Object.fromEntries(webResponse.headers.entries()))
  const body = await webResponse.arrayBuffer()
  res.end(Buffer.from(body))
})

server.listen(3000, () => {
  console.log('✅ API corriendo en VPS / Docker en http://localhost:3000')
})
```

---

## 3. Migración del Storage: Cloudflare R2 ➔ AWS S3 / MinIO

Tanto R2 como S3 y MinIO comparten la misma API S3. Para migrar todos los terabytes de archivos sin programar scripts manuales:

```bash
# 1. Instalar rclone (Herramienta estándar de sincronización en la nube)
sudo apt install rclone

# 2. Configurar rclone.conf con R2 y S3/MinIO
# 3. Sincronizar en caliente (Copia todos los archivos de R2 a S3):
rclone sync r2:bucket-produccion s3:bucket-backup -P --transfers=16
```

---

## 4. Migración del Frontend: Cloudflare Pages ➔ VPS Nginx / Caddy

Si necesitas servir el frontend compilado (`dist/`) desde un servidor VPS propio:

### Configuración con Caddy (`Caddyfile` ultra-rápido con SSL automático):
```caddy
app.tudominio.com {
    root * /var/www/app/dist
    file_server
    try_files {path} /index.html
    encode gzip zstd

    header {
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

---

## 5. Migración de Dominio y DNS con Cero Downtime

Para cambiar de proveedor de hosting sin que ningún usuario experimente cortes:

```
┌────────────────────────────────┐
│ Paso 1: Bajar TTL a 60 segundos│ ➔ 24 horas antes de la migración.
└────────────────┬───────────────┘
                 │
┌────────────────▼───────────────┐
│ Paso 2: Desplegar en el nuevo  │ ➔ Verificar con curl en staging del nuevo host.
└────────────────┬───────────────┘
                 │
┌────────────────▼───────────────┐
│ Paso 3: Cambiar la IP en el DNS│ ➔ La propagación tomará solo 60 segundos.
└────────────────┬───────────────┘
                 │
┌────────────────▼───────────────┐
│ Paso 4: Restaurar TTL a 3600s  │ ➔ Una vez verificado el tráfico en el nuevo host.
└────────────────────────────────┘
```
