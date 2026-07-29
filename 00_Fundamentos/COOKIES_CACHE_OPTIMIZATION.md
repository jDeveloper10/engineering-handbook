---
title: "Estándar de Cookies, Caché y Optimizaciones de Alto Rendimiento"
category: 00_Fundamentos
doc_type: estandar
tags: [cookies, cache, kv, browser-cache, cdn, stale-while-revalidate, early-hints, http3, brotli, bundle-splitting, performance]
summary: "Guía maestra y quirúrgica sobre cookies seguras (HttpOnly, SameSite, rotación de refresh tokens), las 4 capas de caché (Browser, CDN, KV, Materialized Views), Early Hints 103, HTTP/3, Brotli y bundle splitting."
keywords: [cookies, httponly, samesite, refresh-token, cache, cache-control, kv, cache-aside, stale-while-revalidate, early-hints, brotli, lazy-loading, bundle-splitting, vite, lcp, ttfb]
updated: 2026-07-27
status: current
---

# 🍪⚡ ESTÁNDAR DE COOKIES, CACHÉ Y OPTIMIZACIONES DE ALTO RENDIMIENTO

Este documento es el estándar definitivo para la gestión de cookies seguras, la arquitectura de caché en 4 niveles y la aplicación de optimizaciones avanzadas de red y frontend en el stack **Cloudflare Workers + Supabase + React/Vite**.

---

## 🍪 1. COOKIES: GUÍA COMPLETA Y SEGURIDAD

### 1.1 ¿Qué es una cookie y cuáles son sus tipos?

Una **Cookie** es un pequeño fragmento de texto (máximo 4KB) enviado por el servidor mediante la cabecera `Set-Cookie` y almacenado por el navegador, que vuelve a enviarse automáticamente en cada petición posterior hacia el mismo origen (`Cookie: ...`).

| Tipo | Ejemplo | ¿Funciona la app sin ella? | ¿Requiere consentimiento? |
|---|---|---|---|
| **Esenciales** | Tokens de sesión HTTP, CSRF, estado de auth | ❌ No funciona | 🚫 No requiere |
| **Preferencias** | Tema (dark/light), idioma, moneda | ✅ Sí funciona | 🚫 No (si es 1st party) |
| **Analíticas** | PostHog, Google Analytics | ✅ Sí funciona | ⚠️ **SÍ requiere** (`LEGAL_COMPLIANCE_STANDARD.md`) |
| **Marketing** | Meta Pixel, Google Ads | ✅ Sí funciona | ⚠️ **SÍ requiere** |

---

### 1.2 Manipulación de Cookies en Cloudflare Workers

#### Establecer Cookies en una Respuesta (`Set-Cookie`)
```typescript
// apps/api-gateway/src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response = new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        // Múltiples cookies enviadas en la cabecera Set-Cookie
        'Set-Cookie': [
          `session_id=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=900`,
          `theme=dark; Path=/; Max-Age=31536000; SameSite=Lax`,
          `lang=es; Path=/; Max-Age=31536000; SameSite=Lax`
        ].join(', ')
      }
    })
    return response
  }
}
```

#### Helper para Parsear Cookies desde la Petición (`Cookie`)
```typescript
// shared-http/cookies.ts
export function parseCookies(request: Request): Record<string, string> {
  const cookieHeader = request.headers.get('Cookie') || ''
  if (!cookieHeader) return {}

  return Object.fromEntries(
    cookieHeader.split('; ').map(cookieStr => {
      const [key, ...valueParts] = cookieStr.split('=')
      return [key.trim(), valueParts.join('=').trim()]
    })
  )
}

// Uso en un Worker:
const cookies = parseCookies(request)
const theme = cookies.theme ?? 'system'
const lang  = cookies.lang  ?? 'es'
```

---

### 1.3 Flags de Seguridad Obligatorios para Cookies de Autenticación

```
Set-Cookie: refresh_token=abc123secret; HttpOnly; Secure; SameSite=Strict; Path=/api/auth; Max-Age=604800
```

- **`HttpOnly` [REQUIRED]:** Bloquea el acceso a la cookie desde JavaScript (`document.cookie`). Elimina la clase entera de ataques de robo de sesión por XSS.
- **`Secure` [REQUIRED]:** Garantiza que la cookie SOLO viaje a través de conexiones cifradas HTTPS.
- **`SameSite=Strict` [REQUIRED]:** Previene ataques CSRF. La cookie no se enviará si la petición proviene de un sitio de terceros. (Usar `SameSite=Lax` para permitir enlaces externos entrantes).
- **`Path=/api/auth` [REQUIRED]:** Restringe la cookie al subconjunto de rutas que realmente la necesitan.
- **`Max-Age=604800` [REQUIRED]:** Expiración explícita en segundos (7 días).

---

### 1.4 Patron Real: Autenticación con Access Token + Refresh Token Rotativo

- **Access Token:** Se entrega en el JSON de respuesta. El frontend lo almacena **únicamente en memoria** (React State / Zustand). Expira en 15 minutos (900s).
- **Refresh Token:** Se entrega en una cookie `HttpOnly; Secure; SameSite=Strict`. El frontend NUNCA lo lee. Expira en 7 días.

```typescript
// POST /api/auth/login
export async function handleLogin(request: Request, env: Env): Promise<Response> {
  const { email, password } = await request.json()
  const user = await validateUser(email, password, env)

  if (!user) return fail('INVALID_CREDENTIALS', 'Credenciales incorrectas', 401)

  const accessToken  = await signAccessToken(user.id)    // 15 min
  const refreshToken = await createRefreshToken(user.id) // 7 días

  return new Response(
    JSON.stringify({
      success: true,
      data: { access_token: accessToken, expires_in: 900 }
    }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': `refresh_token=${refreshToken}; HttpOnly; Secure; SameSite=Strict; Path=/api/auth; Max-Age=604800`
      }
    }
  )
}

// POST /api/auth/refresh (Rotación de Refresh Token)
export async function handleRefresh(request: Request, env: Env): Promise<Response> {
  const cookies = parseCookies(request)
  const oldRefreshToken = cookies.refresh_token

  if (!oldRefreshToken) return fail('UNAUTHORIZED', 'No hay refresh token en cookies', 401)

  const userId = await validateRefreshToken(oldRefreshToken, env)
  if (!userId) return fail('UNAUTHORIZED', 'Token inválido o expirado', 401)

  // ROTACIÓN: Invalidar el refresh token usado y emitir uno nuevo
  await invalidateRefreshToken(oldRefreshToken, env)
  const newRefreshToken = await createRefreshToken(userId)
  const newAccessToken  = await signAccessToken(userId)

  return new Response(
    JSON.stringify({
      success: true,
      data: { access_token: newAccessToken, expires_in: 900 }
    }),
    {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': `refresh_token=${newRefreshToken}; HttpOnly; Secure; SameSite=Strict; Path=/api/auth; Max-Age=604800`
      }
    }
  )
}
```

---

## ⚡ 2. CACHÉ EN 4 NIVELES: ARQUITECTURA MAESTRA

```
Nivel 1: Browser Cache     ──→ Header Cache-Control (Gratis, en dispositivo del usuario)
Nivel 2: CDN Edge Cache    ──→ Cloudflare Cache API (Respuesta servida en 300+ ciudades)
Nivel 3: Application Cache ──→ Cloudflare KV / Redis (Cache-Aside para lecturas de DB)
Nivel 4: Database Cache    ──→ Vistas Materializadas + Índices PostgreSQL en Supabase
```

---

### Nivel 1: Browser Cache (`Cache-Control`)

#### Assets Estáticos con Hash (`app-a1b2c3.js`)
```typescript
return new Response(staticAsset, {
  headers: {
    'Content-Type': 'application/javascript',
    'Cache-Control': 'public, max-age=31536000, immutable' // 1 año (inmutable)
  }
})
```

#### Documentos HTML (Revalidación Estricta)
```typescript
return new Response(htmlContent, {
  headers: {
    'Content-Type': 'text/html',
    'Cache-Control': 'public, max-age=0, must-revalidate'
  }
})
```

#### APIs Dinámicas con Stale-While-Revalidate
```typescript
return new Response(JSON.stringify(data), {
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=60, stale-while-revalidate=300'
    // Sirve contenido cacheado 60s. Si vence, sirve contenido viejo hasta 300s mientras refresca en background
  }
})
```

---

### Nivel 2: CDN Edge Cache (Cloudflare CDN)

Cloudflare cachea automáticamente extensiones estáticas (`.css`, `.js`, `.jpg`, `.png`, `.svg`, `.woff2`, `.pdf`). Para controlar el caché explícitamente desde un Worker:

```typescript
// Forzar caché en CDN de Cloudflare
return new Response(JSON.stringify(publicCatalog), {
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=3600',        // Browser: 1 hora
    'CDN-Cache-Control': 'public, max-age=604800'  // Cloudflare CDN: 7 días
  }
})

// Garantizar NO-CACHE en peticiones autenticadas o sensibles
return new Response(JSON.stringify(userData), {
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store, no-cache, must-revalidate, private',
    'CDN-Cache-Control': 'no-store'
  }
})
```

---

### Nivel 3: Application Cache (Patrón Cache-Aside con Cloudflare KV)

```typescript
// Lectura con Cache-Aside
export async function getDocumentsList(userId: string, env: Env) {
  const cacheKey = `docs_list:${userId}`

  // 1. Intentar leer de KV
  const cached = await env.KV.get(cacheKey, 'json')
  if (cached) {
    console.info('[KV_CACHE_HIT]', cacheKey)
    return cached
  }

  // 2. KV Miss: Consultar Supabase Postgres
  console.info('[KV_CACHE_MISS]', cacheKey)
  const { data, error } = await supabase
    .from('documents')
    .select('id, title, status, updated_at') // DB-001: NUNCA SELECT *
    .eq('user_id', userId)
    .is('deleted_at', null)
    .order('updated_at', { ascending: false })

  if (error) throw error

  // 3. Guardar en KV con TTL de 5 minutos (300 segundos)
  await env.KV.put(cacheKey, JSON.stringify(data), { expirationTtl: 300 })

  return data
}

// Invalidar caché en mutaciones
export async function createDocument(userId: string, docData: Record<string, unknown>, env: Env) {
  const { data, error } = await supabase
    .from('documents')
    .insert({ ...docData, user_id: userId })
    .select()
    .single()

  if (error) throw error

  // Invalidación activa de caché
  await env.KV.delete(`docs_list:${userId}`)

  return data
}
```

---

### Nivel 4: Database Cache (Vistas Materializadas en Postgres)

```sql
-- ❌ INSEGURO / LENTO: Agregación masiva en cada request
-- SELECT status, COUNT(*), SUM(amount_cents) FROM orders GROUP BY status;

-- ✅ VISTA MATERIALIZADA PRE-CALCULADA (Consulta en 1ms)
CREATE MATERIALIZED VIEW mv_monthly_revenue_summary AS
SELECT
  team_id,
  status,
  COUNT(*) as total_orders,
  SUM(amount_cents) as total_revenue_cents
FROM orders
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY team_id, status;

CREATE UNIQUE INDEX idx_mv_monthly_revenue ON mv_monthly_revenue_summary(team_id, status);

-- Refresco automático cada 15 minutos con pg_cron
SELECT cron.schedule(
  'refresh_revenue_summary',
  '*/15 * * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_revenue_summary'
);
```

---

### 📊 MATRIZ MAESTRA DE ESTRATEGIAS DE CACHÉ

| Tipo de Dato | Estrategia | TTL Replicación | Ubicación |
|---|---|---|---|
| Assets estáticos (JS, CSS, Img) | **Cache-First (Immutable)** | 1 Año (`31536000s`) | Browser + Cloudflare CDN |
| Documentos HTML | **Network-First (Revalidate)** | 0s (`must-revalidate`) | Browser + CDN |
| Respuestas API públicas (catálogos) | **Stale-While-Revalidate** | 60s max-age / 300s stale | CDN + Workers KV |
| Respuestas API privadas (listados) | **Cache-Aside** | 5 Minutos (`300s`) | Workers KV |
| Sesiones & Auth Tokens | **Cache-Aside** | 15 Minutos (`900s`) | Workers KV |
| Configuración & Feature Flags | **Cache-First** | 1 Hora (`3600s`) | Workers KV |
| Datos en Tiempo Real / Websockets | **No Cache** | 0s | Durable Objects |
| Transacciones & Pagos | **No Cache (`no-store`)** | 0s | Database Direct |

---

## 🚀 3. OPTIMIZACIONES AVANZADAS DE RENDIMIENTO DE RED Y FRONTEND

### 3.1 Early Hints (HTTP 103) en Cloudflare Workers
Permite informar al navegador sobre recursos críticos que debe pre-cargar mientras el servidor aún genera el HTML final.

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    if (url.pathname === '/') {
      const hints = [
        '</assets/app.css>; rel=preload; as=style',
        '</assets/app.js>; rel=preload; as=script',
        '</fonts/inter.woff2>; rel=preload; as=font; crossorigin'
      ]

      return new Response(htmlContent, {
        status: 200,
        headers: {
          'Content-Type': 'text/html',
          'Link': hints.join(', '),
          'Early-Hints': hints.join(', ')
        }
      })
    }
    return new Response('Not found', { status: 404 })
  }
}
```

---

### 3.2 HTTP/3 (QUIC) & Compresión Brotli
- **HTTP/3 (QUIC):** Activado automáticamente en Cloudflare. Elimina el bloqueo de cabeza de línea (Head-of-Line Blocking) y ofrece 0-RTT en reconexiones móviles.
- **Compresión Brotli:** Comprime entre un 20% y 30% más que Gzip. Cloudflare comprime automáticamente archivos `text/html`, `text/css`, `application/javascript` y `application/json`.

---

### 3.3 Resource Hints en HTML (`preload`, `prefetch`, `dns-prefetch`)

```html
<!-- PRELOAD: Recursos críticos para la página actual -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/main.css" as="style">

<!-- PREFETCH: Recursos probables para la SIGUIENTE navegación -->
<link rel="prefetch" href="/assets/dashboard.js">

<!-- DNS-PREFETCH / PRECONNECT: Resolver DNS/TLS de APIs externas de antemano -->
<link rel="preconnect" href="https://api.collabscribe.com">
<link rel="dns-prefetch" href="https://js.stripe.com">
```

---

### 3.4 Lazy Loading y Code Splitting en React / Vite

#### Lazy Loading de Componentes
```tsx
import React, { lazy, Suspense } from 'react'

const HeavyDashboardChart = lazy(() => import('@/components/HeavyDashboardChart'))

export function AnalyticsPage() {
  return (
    <div>
      <h1>Métricas del Equipo</h1>
      <Suspense fallback={<div className="h-64 bg-surface animate-pulse rounded-lg" />}>
        <HeavyDashboardChart />
      </Suspense>
    </div>
  )
}
```

#### Bundle Splitting Manual en `vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor:  ['react', 'react-dom', 'react-router-dom'],
          ui:      ['lucide-react', '@radix-ui/react-dialog'],
          editor:  ['@tiptap/react', '@tiptap/starter-kit', 'yjs'],
          charts:  ['recharts']
        }
      }
    }
  }
})
```

---

## 📊 Presupuestos de Rendimiento (Performance Budgets)

| Métrica | Valor Límite (Target) | Herramienta de Medición |
|---|---|---|
| **LCP** (Largest Contentful Paint) | **< 2.5s** | Lighthouse / Web Vitals |
| **FID / INP** (Interaction to Next Paint) | **< 100ms** | Chrome Web Vitals |
| **CLS** (Cumulative Layout Shift) | **< 0.1** | Lighthouse |
| **TTFB** (Time to First Byte) | **< 200ms** | Cloudflare Analytics |
| **Bundle Initial Size** | **< 150KB (Gzip)** | Vite Bundle Visualizer |
| **KV Cache Hit Rate** | **> 85%** | Cloudflare Workers Analytics |
