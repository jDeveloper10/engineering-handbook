---
title: "Workers como Backend Único"
category: 02_Backend
tags: [workers, backend, cloudflare, arquitectura, migration]
summary: "Workers reemplaza TODO backend tradicional: Express, Django, Laravel, VPS, Docker, Kubernetes. Este documento es la fuente de verdad sobre qué puede hacer un Worker y cómo se estructura el backend completo."
keywords: [workers-as-backend, serverless, edge, microservicios, migration]
updated: 2026-07-27
status: current
---

# ⚡ WORKERS COMO BACKEND ÚNICO

> Este documento tiene una sola tesis: **Workers ES el backend. No existe Express, Fastify, Django, Rails, Laravel, VPS, ni Docker en este stack.** Todo lo que un servidor tradicional hace, un Worker lo hace mejor, más barato y sin administración.

---

## 🎯 REGLAS INQUEBRANTABLES

**WORKER-001: Un solo stack de Workers para TODOS los clientes.**
La misma API sirve web, mobile (React Native/Expo), desktop (Tauri), IoT y cualquier cliente HTTP. NUNCA Workers separados por plataforma.

**WORKER-002: NUNCA usar framework de servidor tradicional.**
`Express`, `Fastify`, `Koa`, `Hono` (modo servidor), `Django`, `Rails`, `Laravel`, `FastAPI` — ninguno. El handler `fetch()` de Workers es el reemplazo. No admite debate.

**WORKER-003: Lógica de negocio en Services, NUNCA en el handler.**
Ver `BACKEND_ENGINEERING_STANDARD.md §02` — capas `router → middleware → handler → service → datos`.

**WORKER-004: Comunicación interna SIEMPRE con Service Bindings.**
Workers internos se llaman con `env.SERVICE_NAME.fetch()`. NUNCA con HTTP entre Workers propios — eso añade latencia de red innecesaria y expone endpoints internos.

---

## 🏗️ ARQUITECTURA: DE DONDE VIENES → A DONDE VAS

```
❌ ARQUITECTURA TRADICIONAL (lo que se elimina)

Cliente  →  VPS/Docker (Express/Nginx)  →  PostgreSQL / Redis
              │
              ├── SSL manual
              ├── PM2 / systemd
              ├── Nginx config
              ├── Load balancer
              └── Ops team


✅ ARQUITECTURA WORKERS (lo que se adopta)

Cliente  →  api-gateway (Worker público)
                  │
                  ├── auth-worker     (Service Binding, interno)
                  ├── docs-worker     (Service Binding, interno)
                  ├── billing-worker  (Service Binding, interno)
                  ├── search-worker   (Service Binding, interno)
                  └── webhook-worker  (público: /webhooks/stripe)
                  │
                  └── Infraestructura
                        ├── Supabase   (PostgreSQL + Auth + Realtime)
                        ├── D1         (métricas, logs ligeros)
                        ├── R2         (archivos: imágenes, PDFs)
                        ├── KV         (caché, feature flags, sesiones)
                        ├── Queues     (jobs asíncronos > 15s)
                        └── DO         (WebSockets, rate limiting con estado)
```

---

## ✅ TODO LO QUE UN WORKER PUEDE HACER

| Funcionalidad | Cómo en Workers | Referencia |
|---|---|---|
| REST API | `fetch()` handler con router | `BACKEND_ENGINEERING_STANDARD.md §02` |
| GraphQL | GraphQL Yoga (Edge-compatible) | `— [pendiente de documentar]` |
| WebSockets | Durable Objects | `CLOUDFLARE_PLATFORM_STANDARD.md §DO` |
| Autenticación JWT | `supabase.auth.getUser(token)` | `BACKEND_ENGINEERING_STANDARD.md §04` |
| Rate Limiting | Durable Objects o Upstash Redis | `ESTANDAR_RATE_LIMITING.md` |
| CORS | Módulo `shared-http/cors.ts` | `BACKEND_ENGINEERING_STANDARD.md §03` |
| Validación | Zod (mismo que frontend) | `SECURITY_ENGINEERING_STANDARD.md S-001` |
| CRUD Postgres | Supabase client con RLS | `DATABASE_ENGINEERING_STANDARD.md` |
| File Upload | Streaming directo a R2 | `CLOUDFLARE_PLATFORM_STANDARD.md §R2` |
| File Download | Presigned URLs R2 o streaming | `CLOUDFLARE_PLATFORM_STANDARD.md §R2` |
| Email | Resend + React Email templates | `NOTIFICATIONS_STANDARD.md §email` |
| Notificaciones Push Web | VAPID + Service Worker | `NOTIFICATIONS_STANDARD.md §vapid` |
| Notificaciones Push Mobile | Expo Push (FCM/APNs) | `NOTIFICATIONS_STANDARD.md §mobile` |
| Notificaciones In-App | Supabase Realtime | `FRONTEND_REALTIME_PATTERN.md` |
| Webhooks (Stripe, GitHub...) | Handler público con verificación de firma | Este documento §webhook |
| Pagos | Stripe SDK (Edge-compatible) | `— [pendiente de documentar]` |
| PDF Generation | `pdf-lib` (Edge-compatible) | `PATRON_GENERACION_PDF_EDGE.md` |
| Image Processing | Cloudflare Images API o WASM | `HEAVY_COMPUTE_STANDARD.md` |
| Cron Jobs | `scheduled()` handler en wrangler | Este documento §scheduled |
| Colas de trabajo | Cloudflare Queues | `CLOUDFLARE_PLATFORM_STANDARD.md §Queues` |
| Caché | KV + `Cache API` | `WORKERS_OPTIMIZATION.md` |
| Feature Flags | KV (key = flag, value = JSON) | `WORKERS_OPTIMIZATION.md` |
| A/B Testing | KV + lógica en el handler | `WORKERS_OPTIMIZATION.md` |
| SSR / HTML streaming | `HTMLRewriter` o render a string | `— [pendiente]` |
| Proxy reverso | `fetch()` a cualquier API externa | Este documento §proxy |

---

## ❌ LO QUE UN WORKER NO PUEDE HACER (con alternativa)

| Limitación | Restricción | Alternativa |
|---|---|---|
| PostgreSQL directo | No hay TCP raw | Supabase REST/RPC |
| CPU > 30 segundos | Límite de CPU del runtime | Queues + Container Workers |
| Archivos > 100MB en body | Límite de request size | R2 multipart upload directo |
| Filesystem local | Stateless, no hay disco | R2 para objetos |
| GPU / ML inference | Sin GPU en el Edge | Cloudflare AI Gateway / Workers AI |
| WebSockets "nativos" | Sin estado entre requests | Durable Objects |
| Librerías Node.js que usan `fs`, `net`, `tls` | Sin APIs de Node en Workers | Reemplazar por fetch + R2 |

---

## 📦 ESTRUCTURA DEL BACKEND

```
apps/
├── api-gateway/              ← ÚNICO punto de entrada público
│   ├── src/
│   │   ├── index.ts          ← fetch() handler principal
│   │   ├── router.ts         ← Dirige a Service Bindings internos
│   │   ├── middleware/
│   │   │   ├── auth.ts       ← JWT verification
│   │   │   ├── rate-limit.ts ← Límites por IP/usuario
│   │   │   └── cors.ts       ← Orígenes permitidos
│   │   └── lib/
│   │       ├── response.ts   ← ok(), fail() — nunca repetidos
│   │       └── circuit-breaker.ts
│   └── wrangler.toml
│
├── auth-worker/              ← /api/auth/* (registro, login, refresh)
├── docs-worker/              ← /api/documents/* (CRUD documentos)
├── teams-worker/             ← /api/teams/* (equipo, miembros)
├── billing-worker/           ← /api/billing/* (Stripe, suscripciones)
├── notif-worker/             ← interno: email + push
├── search-worker/            ← /api/search/*
├── webhook-worker/           ← /webhooks/* (Stripe, GitHub — público)
└── embeddings-worker/        ← Queue consumer (pgvector embedding jobs)
```

---

## 🔄 MIGRACIÓN DESDE BACKEND TRADICIONAL

```typescript
// ❌ ANTES — Express
app.post('/api/proposals', authMiddleware, validateBody, async (req, res) => {
  try {
    const proposal = await db.proposals.create(req.body)
    res.json({ success: true, data: proposal })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// ✅ DESPUÉS — Worker (misma lógica, runtime diferente y mejor)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)

    if (url.pathname === '/api/proposals' && request.method === 'POST') {
      const corsHeaders = getCorsHeaders(env.ENVIRONMENT, request.headers.get('Origin'))

      // Capa 1: Auth
      const { data: { user }, error: authError } = await supabase.auth.getUser(
        request.headers.get('Authorization')?.replace('Bearer ', '') ?? ''
      )
      if (authError || !user) return fail('UNAUTHORIZED', 'Token inválido', 401, corsHeaders)

      // Capa 2: Validación (Zod)
      const body = await request.json()
      const validated = proposalSchema.parse(body)

      // Capa 3: Persistencia
      const { data, error } = await supabase
        .from('proposals')
        .insert({ ...validated, created_by: user.id })
        .select('id, title, status, created_at')  // DB-001: NUNCA SELECT *
        .single()
      if (error) return fail('DB_ERROR', error.message, 500, corsHeaders)

      return ok(data, corsHeaders)
    }

    return fail('NOT_FOUND', 'Ruta no encontrada', 404, {})
  }
}
```

La lógica es idéntica. El runtime: Edge global, cold start < 5ms, $0 idle.

---

## ⏰ CRON JOBS (Scheduled Workers)

```typescript
// wrangler.toml
// [[triggers]]
// crons = ["0 9 * * 1"]  ← Cada lunes a las 9am UTC

export default {
  // Handler HTTP normal
  async fetch(request: Request, env: Env): Promise<Response> { ... },

  // Handler de cron — se ejecuta según la configuración de wrangler.toml
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(runWeeklyDigest(env))
  }
}

async function runWeeklyDigest(env: Env) {
  // 1. Obtener usuarios con digest activo
  const { data: users } = await supabase
    .from('profiles')
    .select('id, email, display_name')
    .eq('weekly_digest', true)

  // 2. Para cada usuario, encolar el email (no esperar en el cron)
  for (const user of users ?? []) {
    await env.NOTIF_QUEUE.send({
      type: 'weekly-digest',
      userId: user.id,
      email: user.email
    })
  }
}
```

---

## 🔔 WEBHOOKS EXTERNOS (Stripe, GitHub, etc.)

```typescript
// apps/webhook-worker/src/stripe.ts
export async function handleStripeWebhook(request: Request, env: Env) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature') ?? ''

  // OBLIGATORIO: verificar la firma antes de procesar CUALQUIER dato
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, signature, env.STRIPE_WEBHOOK_SECRET)
  } catch {
    return fail('INVALID_SIGNATURE', 'Firma de webhook inválida', 400, {})
  }

  switch (event.type) {
    case 'customer.subscription.created':
      await handleSubscriptionCreated(event.data.object, env)
      break
    case 'customer.subscription.deleted':
      await handleSubscriptionCanceled(event.data.object, env)
      break
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object, env)
      break
  }

  return ok({ received: true })
}
```

---

## 📋 CHECKLIST DE NUEVO WORKER

Antes de crear un Worker nuevo, verificar:

- [ ] ¿Tiene su propio `wrangler.toml` con `name`, `main`, `compatibility_date`?
- [ ] ¿Tiene solo los bindings que necesita (D1, R2, KV, Queues)?
- [ ] ¿La ruta que sirve es exclusiva (nunca compartida con otro Worker)?
- [ ] ¿Los handlers usan `ok()` y `fail()` del módulo `shared-http`?
- [ ] ¿El CORS viene del módulo `shared-http/cors`, no redefinido?
- [ ] ¿La autenticación es un middleware, no copiada en cada handler?
- [ ] ¿Los logs incluyen `traceId` propagado desde el gateway?
- [ ] ¿Los secretos están en las variables de entorno, nunca en el código?

---

## 🏆 LO QUE ELIMINAS AL ADOPTAR WORKERS

| Eliminado | Por qué | Ahorro anual estimado |
|---|---|---|
| VPS ($20-500/mes) | Workers escala infinito $0 idle | $240-6000 |
| Docker / Kubernetes | Sin contenedores que orquestar | Tiempo de ops |
| Nginx / Caddy | Cloudflare CDN incluido | $0 explícito, tiempo de config |
| PM2 / systemd | Workers no se "caen" | Tiempo de ops |
| SSL renovaciones | Automático en Cloudflare | Tiempo de ops |
| Load balancers ($15-50/mes) | Distribución global automática | $180-600 |
| Server monitoring | Workers Analytics incluido | $10-50/mes |
| OS updates | Sin servidores que actualizar | Tiempo de ops |
