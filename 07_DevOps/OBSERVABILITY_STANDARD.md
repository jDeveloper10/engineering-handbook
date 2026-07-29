# Estándar de Observabilidad (OBS)

## 🎯 Objetivo
Garantizar que cualquier fallo en producción pueda ser diagnosticado, trazado y resuelto en menos de 15 minutos, incluso en arquitecturas distribuidas con 8+ servicios.

---

## ⚡ REGLAS INQUEBRANTABLES

### OBS-001: TODO SERVICIO DEBE EMITIR LOGS ESTRUCTURADOS (JSON)

**Regla:** 
NUNCA usar `console.log(string)`. SIEMPRE usar logs estructurados en formato JSON.

**Violación:**
```typescript
console.log("Usuario creado: " + userId)
```

**Correcto:**
```typescript
console.log(JSON.stringify({
  level: "INFO",
  service: "auth-service",
  trace_id: "abc-123",
  user_id: userId,
  action: "user_created",
  timestamp: new Date().toISOString(),
  duration_ms: 150
}))
```

---

### OBS-002: TODO REQUEST DEBE TENER TRACE_ID

**Regla:**
Cada request que entra al sistema genera un `trace_id` único (UUID v4). Este ID se propaga a TODOS los servicios que toca.

**Implementación en API Gateway:**
```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const traceId = request.headers.get('x-trace-id') || crypto.randomUUID()
    
    // Inyectar en logs
    const log = (msg: string) => console.log(JSON.stringify({
      trace_id: traceId,
      service: 'api-gateway',
      message: msg
    }))
    
    log('request_started')
    
    // Propagar a servicios internos
    const response = await fetch('https://auth.internal', {
      headers: { 'x-trace-id': traceId }
    })
    
    log('request_completed')
    return response
  }
}
```

---

### OBS-003: TODO ERROR DEBE IR A SENTRY/LOGFLARE

**Regla:**
NUNCA atrapar errores sin reportarlos. Usar Sentry (Workers) o Logflare (Cloudflare).

```typescript
import * as Sentry from '@sentry/cloudflare'

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      // Lógica de negocio
      return new Response("OK")
    } catch (error) {
      Sentry.captureException(error, {
        tags: { service: 'billing-service' },
        extra: { userId: request.headers.get('x-user-id') }
      })
      return new Response("Error", { status: 500 })
    }
  }
}
```

---

### OBS-004: MÉTRICAS DE NEGOCIO EN TIEMPO REAL

**Regla:**
Todo evento de negocio (compra, registro, cancelación) DEBE emitirse como métrica.

**Implementación con Cloudflare Analytics Engine:**
```typescript
// src/metrics.ts
export function trackEvent(env: Env, event: {
  name: string
  user_id: string
  properties: Record<string, any>
}) {
  env.ANALYTICS.writeDataPoint({
    blobs: [event.name, event.user_id],
    doubles: [event.properties.value || 0],
    indexes: [event.name]
  })
}

// Uso:
await trackEvent(env, {
  name: 'proposal_accepted',
  user_id: 'user_123',
  properties: { value: proposal.total_cents }
})
```

---

### OBS-005: ALERTAS CON ESCALAMIENTO (P1-P4)

**Niveles de severidad:**

| Nivel | Nombre | Respuesta | Ejemplo |
|-------|--------|-----------|---------|
| P1 | Crítico | < 5 min (on-call) | API caída, pagos no funcionan |
| P2 | Alto | < 30 min | Feature roto, degradación |
| P3 | Medio | < 4 horas | Bug no crítico, performance |
| P4 | Bajo | < 24 horas | Cosmético, mejora |

**Configuración de alerta (Cloudflare Workers):**
```typescript
export function checkThreshold(metric: string, value: number): 'P1' | 'P2' | null {
  const thresholds = {
    'error_rate': { p1: 0.05, p2: 0.01 },    // 5% errores = P1
    'latency_p95': { p1: 5000, p2: 1000 },    // 5s = P1
    'payment_failure': { p1: 0.10, p2: 0.05 }  // 10% fallos = P1
  }
  
  const threshold = thresholds[metric]
  if (!threshold) return null
  if (value >= threshold.p1) return 'P1'
  if (value >= threshold.p2) return 'P2'
  return null
}
```

---

### OBS-006: HEALTH CHECK EN TODO SERVICIO

**Regla:**
Todo servicio DEBE exponer un endpoint `/health` que retorne:
- Estado del servicio
- Latencia de dependencias (DB, Redis, etc.)
- Versión del deploy

```typescript
export async function healthCheck(env: Env): Promise<Response> {
  const checks: Record<string, any> = {
    service: 'auth-service',
    status: 'healthy',
    version: env.VERSION || '1.0.0',
    timestamp: new Date().toISOString()
  }
  
  // Verificar DB
  const dbStart = Date.now()
  try {
    await env.DB.exec('SELECT 1')
    checks.database = { status: 'healthy', latency_ms: Date.now() - dbStart }
  } catch (error) {
    checks.database = { status: 'unhealthy', error: error.message }
  }
  
  // Verificar Redis
  const redisStart = Date.now()
  try {
    await env.REDIS.ping()
    checks.redis = { status: 'healthy', latency_ms: Date.now() - redisStart }
  } catch (error) {
    checks.redis = { status: 'unhealthy', error: error.message }
  }
  
  return new Response(JSON.stringify(checks, null, 2), {
    headers: { 'Content-Type': 'application/json' }
  })
}
```

---

## 📊 STACK DE OBSERVABILIDAD RECOMENDADO

| Herramienta | Uso | Costo |
|-------------|-----|-------|
| **Logflare** | Logs centralizados (Workers) | Gratis hasta 5GB/mes |
| **Sentry** | Error tracking | Gratis hasta 5K eventos |
| **Cloudflare Analytics** | Métricas de negocio | Incluido en Workers Paid |
| **Uptime Robot** | Health checks externos | Gratis 50 monitores |
| **Statuspage** | Página de status pública | Gratis (open source) |

---

## 🧪 CHECKLIST DE OBSERVABILIDAD

- [ ] ¿Todos los servicios emiten logs en JSON?
- [ ] ¿Cada request tiene trace_id?
- [ ] ¿Errores van a Sentry/Logflare?
- [ ] ¿Métricas de negocio están definidas?
- [ ] ¿Alertas P1-P4 configuradas?
- [ ] ¿Todos los servicios tienen /health?
- [ ] ¿Dashboard de monitoreo existe (Grafana/Logflare)?
- [ ] ¿On-call definido para P1?
