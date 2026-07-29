---
title: "Patrón Circuit Breaker"
category: 02_Backend
doc_type: patron
tags: [resiliencia, api, circuit-breaker, fallos, dependencias]
summary: "Circuit breaker para dependencias externas: los tres estados del interruptor, umbrales recomendados de apertura y recuperación, implementación en TypeScript e integración con Stripe."
keywords: [resiliencia, api, circuit-breaker, fallos, dependencias, circuit, breaker, externas, tres, estados, interruptor, umbrales, recomendados, apertura]
updated: 2026-07-27
status: current
---

# 🔌 PATRÓN CIRCUIT BREAKER (Corta-Corriente)

## 🎯 ¿Qué es y por qué es crítico?
Un **Circuit Breaker** actúa como un interruptor de seguridad. Si un servicio externo (ej. Stripe, SendGrid) comienza a fallar continuamente, el interruptor "salta" (se abre) bloqueando temporalmente las peticiones hacia ese servicio para evitar colapsar nuestro propio sistema, agotar los connection pools, y empeorar la caída del tercero.

> **[REQUIRED] REGLA:** Todo servicio externo DEBE estar envuelto en un Circuit Breaker. PROHIBIDO hacer `fetch` desnudo a APIs de terceros en producción.
>
> **Por qué:** un `fetch` desnudo a una API de terceros que se degrada no falla rápido: se queda esperando el timeout completo en cada petición, acumulando conexiones abiertas hasta agotar los recursos del propio servicio. El circuit breaker es lo que convierte esa espera en un fallo inmediato y contenido (ver `API-009`).

## 🔄 Los 3 Estados (Diagrama)

```text
                  +--------------------------------+
                  |                                |
       (Fallo < 5)|                                v (Éxitos = 3)
      +-----------+--------+            +----------+---------+
      |                    |            |                    |
      |       CLOSED       |            |     HALF_OPEN      |
      |   (Flujo normal)   |            |  (Prueba control)  |
      |                    |            |                    |
      +--------+-----------+            +----------+---------+
               |                                   ^
               | (Fallo = 5 en 30s)                |
               v                                   | (Pasaron 30s)
      +--------+-----------+                       |
      |                    |                       |
      |        OPEN        +-----------------------+
      | (Requests cortados)|
      |                    |
      +--------------------+
```

## ⚙️ Configuración Recomendada
* **Failure Threshold:** 5 fallos en 30s → Transición a **OPEN** (Rechazo inmediato).
* **Recovery Time:** 30s en estado OPEN → Transición a **HALF_OPEN**.
* **Success Threshold:** 3 éxitos consecutivos en HALF_OPEN → Transición a **CLOSED**.

---

## 💻 IMPLEMENTACIÓN (TypeScript)

Esta clase está diseñada para vivir globalmente en el *V8 Isolate* de un Cloudflare Worker, o ser instanciada en un Durable Object para estado persistido entre peticiones.

```typescript
export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN'

export interface CircuitBreakerConfig {
  failureThreshold?: number // Cuántos fallos abren el circuito
  recoveryTimeMs?: number   // Cuánto tiempo esperar antes de intentar HALF_OPEN
  successThreshold?: number // Cuántos éxitos cierran el circuito
  onStateChange?: (state: CircuitState, serviceName: string) => void
}

export class CircuitBreaker {
  private state: CircuitState = 'CLOSED'
  private failures = 0
  private successes = 0
  private nextAttempt = 0
  
  private readonly failureThreshold: number
  private readonly recoveryTimeMs: number
  private readonly successThreshold: number
  private readonly serviceName: string
  private readonly onStateChange: (state: CircuitState, serviceName: string) => void

  constructor(serviceName: string, config: CircuitBreakerConfig = {}) {
    this.serviceName = serviceName
    this.failureThreshold = config.failureThreshold ?? 5
    this.recoveryTimeMs = config.recoveryTimeMs ?? 30000 // 30s
    this.successThreshold = config.successThreshold ?? 3
    this.onStateChange = config.onStateChange ?? (() => {})
  }

  private transition(newState: CircuitState) {
    this.state = newState
    this.onStateChange(newState, this.serviceName)
  }

  async execute<T>(action: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() > this.nextAttempt) {
        this.transition('HALF_OPEN')
      } else {
        throw new Error(`Circuit Breaker OPEN for ${this.serviceName}`)
      }
    }

    try {
      const result = await action()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess() {
    if (this.state === 'HALF_OPEN') {
      this.successes++
      if (this.successes >= this.successThreshold) {
        this.successes = 0
        this.failures = 0
        this.transition('CLOSED')
      }
    } else {
      this.failures = 0 // Resetea en caso de CLOSED continuo
    }
  }

  private onFailure() {
    if (this.state === 'HALF_OPEN') {
      this.nextAttempt = Date.now() + this.recoveryTimeMs
      this.transition('OPEN')
    } else {
      this.failures++
      if (this.failures >= this.failureThreshold) {
        this.nextAttempt = Date.now() + this.recoveryTimeMs
        this.transition('OPEN')
      }
    }
  }
}
```

## 🚀 EJEMPLO DE USO (Integración Stripe y Logflare/Sentry)

```typescript
// Instancia global en el scope del Worker (se mantiene en memoria caliente)
const stripeCircuit = new CircuitBreaker('Stripe API', {
  failureThreshold: 5,
  recoveryTimeMs: 30000,
  onStateChange: (state, name) => {
    // Integración crítica con Logs / Alertas
    console.warn(`[ALERT] El circuito de ${name} cambió a estado: ${state}`)
    // Aquí podrías enviar un evento a Sentry o Logflare
    // logflare.send({ message: `Circuit ${name} is ${state}`, level: 'critical' })
  }
})

// FE-001: el payload de un pago NUNCA es `any` — es la ruta donde el chequeo de tipos más importa.
// MONEY-001/DB-008: monto en centavos enteros, nunca float; el backend resuelve el precio.
interface StripeChargePayload {
  amount_cents: number
  currency: 'USD' | 'MXN'
  customer_id: string
  payment_method_id: string
  idempotency_key: string  // API §11: duplicar un cobro cuesta dinero real
}

export async function processPayment(paymentData: StripeChargePayload) {
  try {
    return await stripeCircuit.execute(async () => {
      const res = await fetch('https://api.stripe.com/v1/charges', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${ENV.STRIPE_KEY}` },
        body: JSON.stringify(paymentData)
      })
      
      // Los 500 y 429 son fallos. Los 400 son errores de usuario, NO rompen el circuito.
      if (res.status >= 500 || res.status === 429) throw new Error('Stripe Down')
      return await res.json()
    })
  } catch (error) {
    // El circuito está abierto o la request falló. 
    // Aplicar Fallback (GRACEFUL DEGRADATION)
    return { success: false, message: 'Plataforma de pagos en mantenimiento temporal.' }
  }
}
```
