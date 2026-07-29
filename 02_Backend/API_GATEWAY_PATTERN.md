# Patrón API Gateway para Microservicios (API-007 a API-012)

## 🎯 Problema
Con 8+ microservicios, exponerlos directamente crea:
- Autenticación duplicada en cada servicio
- Rate limiting inconsistente
- CORS complejo (8 orígenes diferentes)
- Debugging imposible sin trazabilidad

## 🏗️ Solución: API Gateway como punto único de entrada

---

## ⚡ ARQUITECTURA

```
Cliente → API Gateway (Worker público)
              ├── Auth Service (interno, Service Binding)
              ├── Billing Service (interno)
              ├── Reports Service (interno)
              ├── Notifications Service (interno)
              └── Search Service (interno)
```

---

## ⚡ REGLAS INQUEBRANTABLES

### API-007: GATEWAY COMO ÚNICO PUNTO DE ENTRADA

```typescript
// apps/api-gateway/src/index.ts
import { authenticate } from './middleware/auth'
import { rateLimit } from './middleware/rate-limit'
import { routeToService } from './router'

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)
    const traceId = request.headers.get('x-trace-id') || crypto.randomUUID()
    
    // Capa 1: Rate Limiting Global
    const rateLimitResult = await rateLimit(request, env)
    if (!rateLimitResult.allowed) {
      return new Response('Rate limit exceeded', { status: 429 })
    }
    
    // Capa 2: Autenticación (solo rutas protegidas)
    if (!url.pathname.startsWith('/public/')) {
      const auth = await authenticate(request, env)
      if (!auth.authenticated) {
        return new Response('Unauthorized', { status: 401 })
      }
      request = new Request(request, {
        headers: {
          ...request.headers,
          'x-user-id': auth.userId,
          'x-trace-id': traceId
        }
      })
    }
    
    // Capa 3: Ruteo a servicio interno
    return routeToService(request, env, traceId)
  }
}
```

---

### API-008: SERVICE BINDINGS PARA COMUNICACIÓN INTERNA

```typescript
// apps/api-gateway/wrangler.toml
name = "api-gateway"
main = "src/index.ts"

[[services]]
binding = "AUTH_SERVICE"
service = "auth-service"

[[services]]
binding = "BILLING_SERVICE"
service = "billing-service"

# ... resto de servicios
```

**Llamada interna (sin salir a Internet):**
```typescript
async function callAuthService(env: Env, path: string, options: RequestInit) {
  const response = await env.AUTH_SERVICE.fetch(
    new Request(`https://internal${path}`, options)
  )
  return response
}
```

---

### API-009: CIRCUIT BREAKER PARA SERVICIOS EXTERNOS

```typescript
// src/circuit-breaker.ts
class CircuitBreaker {
  private failures = 0
  private lastFail = 0
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'
  
  async call<T>(service: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFail > 30000) {
        this.state = 'HALF_OPEN'
      } else {
        throw new Error('Circuit breaker open')
      }
    }
    
    try {
      const result = await service()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }
  
  private onSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }
  
  private onFailure() {
    this.failures++
    this.lastFail = Date.now()
    if (this.failures >= 5) {
      this.state = 'OPEN'
    }
  }
}
```

---

### API-010: RETRY CON EXPONENTIAL BACKOFF + JITTER

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options)
      
      // Retry solo en errores 5xx o 429
      if (response.status >= 500 || response.status === 429) {
        throw new Error(`Server error: ${response.status}`)
      }
      
      return response
    } catch (error) {
      if (attempt === maxRetries) throw error
      
      // Exponential backoff: 1s, 2s, 4s + jitter
      const backoff = Math.pow(2, attempt) * 1000
      const jitter = Math.random() * 1000
      await new Promise(resolve => setTimeout(resolve, backoff + jitter))
    }
  }
  
  throw new Error('Max retries exceeded')
}
```

---

### API-011: BULKHEAD (AISLAMIENTO DE RECURSOS)

**Regla:**
Cada servicio tiene su propio Worker. Si Billing falla, Auth y Search siguen funcionando.

```typescript
// Gateway maneja fallos de servicios individuales
async function routeToService(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url)
  
  try {
    if (url.pathname.startsWith('/api/billing')) {
      return await env.BILLING_SERVICE.fetch(request)
    }
    if (url.pathname.startsWith('/api/search')) {
      return await env.SEARCH_SERVICE.fetch(request)
    }
    // ...
  } catch (error) {
    // Fallback: si servicio caído, no tumba todo el Gateway
    return new Response(JSON.stringify({
      error: 'SERVICE_UNAVAILABLE',
      service: getServiceFromPath(url.pathname)
    }), { status: 503 })
  }
}
```

---

### API-012: VERSIONADO DE API

```typescript
// Rutas versionadas
export const routes = {
  '/api/v1/proposals': handleProposalsV1,
  '/api/v2/proposals': handleProposalsV2, // Nuevo contrato
}

// Header para versionado alternativo
const version = request.headers.get('Accept-Version') || 'v1'
```

---

## 📋 CHECKLIST API GATEWAY

- [ ] Gateway es único punto de entrada público
- [ ] Autenticación centralizada (no duplicada)
- [ ] Rate limiting global implementado
- [ ] Service Bindings para comunicación interna
- [ ] Circuit Breaker en servicios externos
- [ ] Retry con exponential backoff
- [ ] Trace ID propagado a todos los servicios
- [ ] Health check de cada servicio
