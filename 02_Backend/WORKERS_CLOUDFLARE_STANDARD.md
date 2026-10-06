---
title: "Estándar de Cloudflare Workers"
category: 02_Backend
doc_type: estandar
tags: [workers, cloudflare, d1, kv, r2, serverless]
summary: "Estándar del dominio Backend para Cloudflare Workers: estructura, seguridad, D1/KV/R2, patrones de error, autenticación y deployment."
keywords: [workers, cloudflare, d1, kv, r2, wrangler, serverless, edge]
updated: 2026-08-30
status: current
---

# CLOUDFLARE WORKERS ENGINEERING STANDARD

> **Stack de referencia:** Cloudflare Workers + D1 (SQLite) + KV + R2 + Wrangler
> **Depende de:** BACKEND_ENGINEERING_STANDARD.md (Nivel 1), SECURITY_ENGINEERING_STANDARD.md
> **Aplica a:** Todo backend desplegado en Cloudflare Workers

---

## 01. Estructura del Worker

### 1.1 Organización por handler, no por archivo

**[REQUIRED]** Cada endpoint (o grupo de endpoints relacionados) vive en su propio archivo en `src/handlers/`. El `src/index.ts` solo enruta y exporta el fetch handler.

```
worker/
├── src/
│   ├── index.ts              # Router central
│   ├── middleware/
│   │   ├── auth.ts           # requireAuth(), requireAdmin()
│   │   ├── cors.ts           # corsHeaders(), withCORS()
│   │   ├── rate-limit.ts     # checkRateLimit()
│   │   └── validation.ts     # validateBody(schema)
│   ├── handlers/
│   │   ├── auth.ts           # POST /auth/login, /register, /refresh
│   │   ├── users.ts          # GET/POST/PATCH /users
│   │   └── orders.ts         # GET/POST /orders
│   ├── db/
│   │   ├── schema.ts         # Tipos generados de D1
│   │   └── queries.ts        # Queries tipadas
│   ├── lib/
│   │   ├── errors.ts         # AppError, errorResponse()
│   │   ├── response.ts       # ok(), fail(), jsonRes()
│   │   └── env.ts            # Variables de entorno tipadas
│   └── types.ts              # Tipos compartidos
├── migrations/               # Migraciones SQL
├── wrangler.toml             # Configuración
├── .dev.vars                 # Secrets locales (NUNCA en .env)
└── tsconfig.json
```

### 1.2 El Worker exporta UN handler

**[REQUIRED]** El `index.ts` exporta un objeto `{ fetch(request, env, ctx) }` que enruta internamente:

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/api/, '') || '/';
    const method = request.method;

    // CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    // Enrutamiento
    try {
      if (method === 'POST' && path === '/auth/login') {
        return withCORS(await handleLogin(request, env), request, env);
      }
      // ... más rutas
      return withCORS(jsonRes({ error: 'Not found' }, 404), request, env);
    } catch (err) {
      return withCORS(jsonRes({ error: 'Internal error' }, 500), request, env);
    }
  }
};
```

---

## 02. Variables de Entorno y Secrets

### 2.1 Separación estricta de secrets

**[REQUIRED]** Los secrets NUNCA viven en `.env` del frontend ni en el código fuente. Se inyectan mediante `wrangler secret put` en producción y `.dev.vars` en desarrollo.

```toml
# wrangler.toml — variables públicas (solo URLs y anon keys)
[vars]
API_URL = "https://api.tuapp.com"
SUPABASE_URL = "https://xxx.supabase.co"

# secrets (NUNCA en wrangler.toml — se configuran con wrangler secret put)
# JWT_SECRET = (usar wrangler secret put JWT_SECRET)
# STRIPE_SECRET_KEY = (usar wrangler secret put STRIPE_SECRET_KEY)
```

### 2.2 .dev.vars para desarrollo

**[REQUIRED]** Los secrets locales viven en `.dev.vars` (NUNCA en `.env`):

```bash
# .dev.vars (gitignored por defecto)
JWT_SECRET=tu-secret-local
STRIPE_SECRET_KEY=sk_test_...
```

### 2.3 Tipado de env

**[REQUIRED]** Definir la interfaz `Env` en `wrangler.toml` o en un archivo de tipos:

```typescript
// src/env.ts
export interface Env {
  // Variables públicas
  API_URL: string;
  SUPABASE_URL: string;
  
  // Secrets
  JWT_SECRET: string;
  STRIPE_SECRET_KEY: string;
  
  // Bindings
  DB: D1Database;
  CACHE: KVNamespace;
  BUCKET: R2Bucket;
}
```

---

## 03. D1 (SQLite en Edge)

### 3.1 Queries parametrizadas SIEMPRE

**[REQUIRED]** Nunca concatenar strings en queries. Siempre usar `.bind()`:

```typescript
// ❌ SQL INJECTION
const user = await env.DB.prepare(`SELECT * FROM users WHERE email = '${email}'`).first();

// ✅ PARAMETRIZADO
const user = await env.DB.prepare('SELECT id, email, name FROM users WHERE email = ?')
  .bind(email.trim().toLowerCase())
  .first();
```

### 3.2 Columnas explícitas (DB-001)

**[REQUIRED]** Nunca SELECT *. Especificar columnas:

```typescript
// ❌ DB-001 VIOLATION
const { results } = await env.DB.prepare('SELECT * FROM orders').all();

// ✅ COLUMNAS EXPLÍCITAS
const { results } = await env.DB.prepare(
  'SELECT id, status, total_cents, created_at FROM orders WHERE user_id = ?'
).bind(userId).all();
```

### 3.3 Transacciones con batch

**[REQUIRED]** Operaciones atómicas usan `env.DB.batch()`:

```typescript
await env.DB.batch([
  env.DB.prepare('UPDATE orders SET status = ? WHERE id = ?').bind('paid', orderId),
  env.DB.prepare('INSERT INTO order_events (order_id, event) VALUES (?, ?)').bind(orderId, 'payment_received'),
]);
```

### 3.4 Migraciones versionadas

**[REQUIRED]** Toda migración vive en `migrations/` con nombre incremental:

```
migrations/
├── 0001_create_users.sql
├── 0002_create_orders.sql
└── 0003_add_payment_fields.sql
```

**[REQUIRED]** Ejecutar migraciones con:
```bash
wrangler d1 migrations apply mi-db --remote
wrangler d1 migrations apply mi-db --local
```

---

## 04. Autenticación en Workers

### 4.1 JWT con jose

**[REQUIRED]** Usar `jose` para JWT (no jsonwebtoken, que no funciona en Workers):

```typescript
import { SignJWT, jwtVerify, importJWK } from 'jose';

async function createTokens(user: User, env: Env): Promise<TokenPair> {
  const secret = new TextEncoder().encode(env.JWT_SECRET);
  
  const accessToken = await new SignJWT({ uid: user.id, email: user.email, role: user.role })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('15m')  // REQUIRED: 15 minutos máximo
    .sign(secret);
    
  const refreshToken = await new SignJWT({ uid: user.id, type: 'refresh' })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(secret);
    
  return { accessToken, refreshToken };
}
```

### 4.2 Middleware de auth

**[REQUIRED]** Toda ruta protegida pasa por `requireAuth()`:

```typescript
async function requireAuth(request: Request, env: Env): Promise<User | null> {
  const token = getBearerToken(request);
  if (!token) return null;
  
  try {
    const { payload } = await jwtVerify(token, new TextEncoder().encode(env.JWT_SECRET));
    if (!payload.uid) return null;
    
    const user = await env.DB.prepare('SELECT id, email, role FROM users WHERE id = ?')
      .bind(payload.uid).first();
    return user as User | null;
  } catch {
    return null;
  }
}

async function requireAdmin(request: Request, env: Env): Promise<Response | User> {
  const user = await requireAuth(request, env);
  if (!user) return jsonRes({ error: 'Unauthorized' }, 401);
  if (user.role !== 'admin') return jsonRes({ error: 'Forbidden' }, 403);
  return user;
}
```

---

## 05. CORS en Workers

### 5.1 CORS con whitelist

**[REQUIRED]** Nunca `Access-Control-Allow-Origin: *`. Siempre orígenes explícitos:

```typescript
function corsHeaders(request: Request, env: Env): Record<string, string> {
  const origin = request.headers.get('Origin');
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(o => o.trim());
  const matched = origin && allowed.includes(origin) ? origin : allowed[0] || '';
  
  return {
    'Access-Control-Allow-Origin': matched,
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}
```

### 5.2 Preflight handler

**[REQUIRED]** Responder OPTIONS antes de cualquier lógica:

```typescript
if (request.method === 'OPTIONS') {
  return new Response(null, { status: 204, headers: corsHeaders(request, env) });
}
```

---

## 06. Respuestas Estándar

### 6.1 Envelope de respuesta

**[REQUIRED]** Toda respuesta usa el envelope `ok()` / `fail()`:

```typescript
function jsonRes(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function ok(data: unknown): Response {
  return jsonRes({ ok: true, data }, 200);
}

function fail(error: string, status = 400): Response {
  return jsonRes({ ok: false, error }, status);
}
```

### 6.2 Headers de seguridad

**[REQUIRED]** Agregar headers de seguridad en CADA respuesta:

```typescript
const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Strict-Transport-Security': 'max-age=63072000; includeSubDomains',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};
```

---

## 07. Rate Limiting

### 7.1 Rate limit con Durable Objects o KV

**[REQUIRED]** Toda API pública tiene rate limiting:

```typescript
async function checkRateLimit(
  request: Request, 
  env: Env, 
  config: { max: number; windowMs: number }
): Promise<{ allowed: boolean; remaining: number }> {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const key = `ratelimit:${ip}:${new URL(request.url).pathname}`;
  
  const now = Date.now();
  const windowStart = now - config.windowMs;
  
  // Usar KV para almacenar timestamps
  const raw = await env.CACHE.get(key);
  const timestamps: number[] = raw ? JSON.parse(raw) : [];
  const recent = timestamps.filter(t => t > windowStart);
  
  if (recent.length >= config.max) {
    return { allowed: false, remaining: 0 };
  }
  
  recent.push(now);
  await env.CACHE.put(key, JSON.stringify(recent), { expirationTtl: Math.ceil(config.windowMs / 1000) });
  
  return { allowed: true, remaining: config.max - recent.length };
}
```

---

## 08. Wrangler Configuration

### 8.1 wrangler.toml mínimo

**[REQUIRED]** Toda configuración de Workers sigue esta estructura:

```toml
name = "mi-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[vars]
API_URL = "https://api.tuapp.com"

[[d1_databases]]
binding = "DB"
database_name = "mi-db"
database_id = "xxx-xxx-xxx"

[[kv_namespaces]]
binding = "CACHE"
id = "xxx-xxx-xxx"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "mi-bucket"
```

### 8.2 Scripts de package.json

**[REQUIRED]** Scripts mínimos para Workers:

```json
{
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "typecheck": "tsc --noEmit",
    "db:migrate:local": "wrangler d1 migrations apply mi-db --local",
    "db:migrate:remote": "wrangler d1 migrations apply mi-db --remote",
    "db:studio": "wrangler d1 execute mi-db --remote --command 'SELECT id, email, created_at FROM users LIMIT 10'"
  }
}
```

---

## Checklist Pre-Deploy Workers

- [ ] `wrangler.toml` con binding de DB/KV/R2
- [ ] Secrets configurados con `wrangler secret put`
- [ ] `.dev.vars` en `.gitignore`
- [ ] CORS con orígenes explícitos
- [ ] Rate limiting implementado
- [ ] Queries parametrizadas (nunca concatenar)
- [ ] SELECT * eliminado
- [ ] JWT con TTL 15min (access) / 7d (refresh)
- [ ] Headers de seguridad en cada respuesta
- [ ] `wrangler deploy` funciona sin errores
