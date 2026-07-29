---
title: "Patrón Retry (Exponential Backoff + Jitter)"
category: 02_Backend
tags: [resiliencia, api, retry, backoff, jitter]
summary: "Reintentos con backoff exponencial y jitter: qué errores se reintentan y cuáles no, por qué el backoff lineal provoca thundering herd, e implementación integrada con una API crítica."
keywords: [resiliencia, api, retry, backoff, jitter, exponential, reintentos, exponencial, errores, reintentan, lineal, provoca, thundering, herd]
updated: 2026-07-29
status: current
---

# ♻️ PATRÓN RETRY CON EXPONENTIAL BACKOFF Y JITTER

## 🎯 ¿Qué es y por qué es crítico?
Cuando una petición de red falla transitoriamente, reintentar es la solución lógica. Sin embargo, un **Backoff Lineal** (ej: reintentar cada 2 segundos) o sin **Jitter** (aleatoriedad) crea el "Thundering Herd Problem" (Estampida): si 10,000 clientes fallan, los 10,000 reintentarán exactamente a los 2 segundos, haciendo colapsar nuevamente el servicio.

El **Exponential Backoff** duplica la espera (1s, 2s, 4s, 8s). El **Jitter** le suma o resta un 25% aleatorio a ese tiempo para dispersar las peticiones en el tiempo.

> **REGLA INQUEBRANTABLE:** NUNCA reintentar ciegamente en errores 4xx (excepto 429). Un 404 o un 400 jamás se arreglarán reintentando; solo quemas CPU y generas facturación innecesaria.

---

## 🚦 POLÍTICA DE REINTENTOS POR TIPO DE ERROR

| Status | Descripción | Acción Requerida |
|--------|-------------|------------------|
| **429** | Too Many Requests | **RETRY** utilizando el header `Retry-After` (si existe), sino backoff. |
| **503** | Service Unavailable | **RETRY INMEDIATO** (o backoff rápido), es fallo temporal del balanceador. |
| **500/502/504** | Errores del Servidor | **RETRY** con Exponential Backoff completo + Jitter. |
| **400/401/403/404** | Error de Cliente | **FAIL FAST** (Crashear de inmediato). No reintentar jamás. |

---

## 💻 IMPLEMENTACIÓN BATTLETESTED (TypeScript)

Esta función `fetchWithRetry` está optimizada para Cloudflare Workers, utilizando `AbortController` global.

```typescript
interface RetryOptions extends RequestInit {
  maxRetries?: number
  baseDelayMs?: number
  maxDelayMs?: number
  timeoutMs?: number // Timeout global para TODO el ciclo
}

export async function fetchWithRetry(url: string, options: RetryOptions = {}): Promise<Response> {
  const {
    maxRetries = 3,
    baseDelayMs = 1000,
    maxDelayMs = 16000,
    timeoutMs = 30000,
    ...fetchOptions
  } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  
  // Fusionar signal si ya venía uno, o usar el local
  const signal = fetchOptions.signal || controller.signal

  try {
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(url, { ...fetchOptions, signal })

        // Casos de éxito o errores cliente (NO reintentar)
        if (response.ok || (response.status >= 400 && response.status < 500 && response.status !== 429)) {
          return response
        }

        // Si es 429, buscar Retry-After
        let delay = 0
        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After')
          if (retryAfter) delay = parseInt(retryAfter, 10) * 1000 // asumiendo segundos
        }

        // Si no se sobreescribió por un 429, calcular Exponential Backoff + Jitter
        if (!delay) {
          // Exponential: 1000, 2000, 4000...
          const exponentialDelay = Math.min(baseDelayMs * (2 ** attempt), maxDelayMs)
          // Jitter: +/- 25% aleatorio
          const jitter = (Math.random() - 0.5) * 0.5 * exponentialDelay
          delay = exponentialDelay + jitter
        }

        if (attempt === maxRetries) {
          throw new Error(`Fallo tras ${maxRetries} reintentos. Status: ${response.status}`)
        }

        console.warn(`[RETRY] Intento ${attempt + 1}/${maxRetries} falló (${response.status}). Esperando ${Math.round(delay)}ms...`)
        
        // Espera asíncrona sin bloquear el event loop
        await new Promise(resolve => setTimeout(resolve, delay))
        
      } catch (error: unknown) {
        // Si el usuario o el timeout canceló, no reintentamos
        if (error instanceof Error && error.name === 'AbortError') throw error
        
        // Errores de red (DNS fail, connection refused) sí se reintentan
        if (attempt === maxRetries) throw error
        
        const delay = Math.min(baseDelayMs * (2 ** attempt), maxDelayMs)
        const jitter = (Math.random() - 0.5) * 0.5 * delay
        await new Promise(resolve => setTimeout(resolve, delay + jitter))
      }
    }
    
    throw new Error('Unreachable code')
  } finally {
    clearTimeout(timeoutId)
  }
}
```

## 🚀 EJEMPLO: INTEGRACIÓN CON API CRÍTICA (Stripe)

```typescript
// FE-001: payload tipado explícitamente — es una ruta de dinero, no un `any`.
interface StripePaymentPayload {
  amount_cents: number
  currency: 'USD' | 'MXN'
  customer_id: string
  payment_method_id: string
  idempotency_key: string
}

export async function createStripePayment(payload: StripePaymentPayload) {
  // Las llamadas de pago son críticas. Reintentamos hasta 4 veces,
  // con un delay máximo de 10 segundos, y un timeout general de 30s.
  
  const response = await fetchWithRetry('https://api.stripe.com/v1/charges', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${STRIPE_KEY}` },
    body: JSON.stringify(payload),
    maxRetries: 4,
    baseDelayMs: 500, // Empieza en 500ms -> 1s -> 2s -> 4s
    maxDelayMs: 10000,
    timeoutMs: 30000
  })

  return response.json()
}
```
