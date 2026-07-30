---
title: "Estándar de Seguridad en Pasarelas de Pago (Stripe + Workers)"
category: 05_Security
doc_type: estandar
tags: [pagos, stripe, pci-dss, webhooks, idempotencia, security, rls, workers]
summary: "Estándar inquebrantable de seguridad para pasarelas de pago y suscripciones: compliance PCI DSS, tokenización en frontend, verificación de firmas de webhooks, idempotencia, precios en centavos y prevención de fraude."
keywords: [stripe, pagos, pci-dss, webhooks, idempotency, billing, subscriptions, PCI, centavos, payment-intent]
updated: 2026-07-27
status: current
---

# ESTÁNDAR DE SEGURIDAD EN PASARELAS DE PAGO (Stripe + Cloudflare Workers)

Esto es lo más delicado de cualquier SaaS. Un error en esta capa significa pérdida directa de dinero, cobros duplicados, demandas o violaciones graves de PCI DSS.

---

## LAS 8 REGLAS DE HIERRO DE PAGOS

---

## 0. ARQUITECTURA DE PAGOS SEGURA

```
Cliente (Frontend - Stripe Elements)
        │
        │ 1. Tarjeta ingresada en iframe de Stripe (NUNCA toca tu servidor)
        ▼
Stripe.js  ──→ Genera PaymentMethod (pm_xxx) / Token (tok_xxx)
        │
        │ 2. Envía pm_xxx o priceId (NUNCA datos de tarjeta ni precios)
        ▼
Tu Worker (Backend API)
        │ 3. Crea Checkout Session / PaymentIntent con precios definidos en backend
        ▼
Stripe API  ──→ Procesa cobro
        │
        │ 4. Webhook HTTP POST (stripe.com → tu Worker)
        ▼
Tu Worker (Webhook Handler)
        │ 5. Verifica firma del webhook (OBLIGATORIO) + Replay protection (KV)
        │ 6. Actualiza Supabase (suscripciones/pagos)
        └─→ Envía email de confirmación (NOTIFICATIONS_STANDARD.md)
```

---

## REGLA #1: NUNCA MANIPULES NI ALMACENES DATOS DE TARJETA (PCI DSS)

**[REQUIRED]** Está **estrictamente prohibido** recibir, procesar o tocar números de tarjeta, fechas de vencimiento o CVC en tu servidor/Worker. Viola la normativa PCI DSS y expone la empresa a multas destructivas.

```typescript
// ❌ ILEGAL Y PROHIBIDO (Viola PCI DSS)
const { cardNumber, expiry, cvc } = await request.json()
await stripe.charges.create({
  card: { number: cardNumber, exp_month: expiry, cvc: cvc }
})

// ✅ CORRECTO: Tokenización en el Frontend (Stripe Elements / Checkout)
// Frontend (React + Stripe.js):
const elements = useElements()
const cardElement = elements.getElement(CardElement)
const { paymentMethod, error } = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement!
})

// Backend (Worker): recibe pm_xxx (PaymentMethod ID)
const { paymentMethodId } = await request.json()
await stripe.paymentIntents.create({
  payment_method: paymentMethodId,  // pm_xxx, NUNCA la tarjeta
  amount: 5000,                      // $50.00 en centavos
  currency: 'usd'
})
```

---

## REGLA #2: VERIFICA SIEMPRE LA FIRMA DE LOS WEBHOOKS (Protección anti-suplantación)

**[REQUIRED]** Todo endpoint de webhook (`/webhooks/stripe`) DEBE verificar la firma HTTP en el header `stripe-signature` usando el secreto de webhook `STRIPE_WEBHOOK_SECRET`. Procesar webhooks sin verificar firma permite a cualquier atacante simular compras o suscripciones activas gratis.

```typescript
// apps/webhook-worker/src/stripe.ts
import Stripe from 'stripe'
import { ok, fail } from '@collabscribe/shared-http'

export async function handleStripeWebhook(request: Request, env: Env): Promise<Response> {
  const stripe = new Stripe(env.STRIPE_SECRET_KEY)
  const signature = request.headers.get('stripe-signature')

  if (!signature) {
    return fail('MISSING_SIGNATURE', 'Falta la firma del webhook', 400)
  }

  try {
    const body = await request.text()

    // 1. Verificar que el webhook viene REALMENTE de Stripe
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      env.STRIPE_WEBHOOK_SECRET
    )

    // 2. Protección contra Replay Attacks (KV TTL 7 días)
    const isReplay = await env.KV.get(`webhook_processed:${event.id}`)
    if (isReplay) {
      return ok({ message: 'Evento ya procesado (idempotente)' })
    }

    // 3. Procesar eventos de forma segura
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        await activateSubscription(session.client_reference_id!, session, env)
        break
      }
      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription
        await cancelSubscription(subscription.id, env)
        break
      }
      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice
        await handlePaymentFailed(invoice, env)
        break
      }
    }

    // Marcar evento como procesado para evitar replay attacks
    await env.KV.put(`webhook_processed:${event.id}`, '1', { expirationTtl: 7 * 24 * 3600 })

    return ok({ received: true })

  } catch (error: unknown) {
    console.error('[STRIPE_WEBHOOK_ERROR]', error instanceof Error ? error.message : error)
    return fail('INVALID_SIGNATURE', 'Firma de webhook inválida', 400)
  }
}
```

---

## REGLA #3: IDEMPOTENCIA EN COBROS (Evita cobros dobles)

**[REQUIRED]** Toda mutación de cobro (`paymentIntents.create`, `charges.create`) debe incluir un `idempotencyKey` generado unívocamente por intento de transacción. Si la red falla y la app reintenta, Stripe reconoce la clave y devuelve la respuesta anterior sin realizar un segundo cobro.

```typescript
// Backend (Worker)
async function createPaymentIntent(
  amountCents: number,
  customerId: string,
  idempotencyKey: string,
  env: Env
) {
  const stripe = new Stripe(env.STRIPE_SECRET_KEY)

  return await stripe.paymentIntents.create(
    {
      amount: amountCents,
      customer: customerId,
      currency: 'usd',
      automatic_payment_methods: { enabled: true }
    },
    {
      idempotencyKey // ← Mismo key = misma transacción, cero duplicados
    }
  )
}

// Frontend: genera el Idempotency-Key por intento de compra
const idempotencyKey = `pay_${userId}_${cartId}_${Date.now()}`
await fetch('/api/payments/checkout', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Idempotency-Key': idempotencyKey
  },
  body: JSON.stringify({ planId: 'pro' })
})
```

---

## REGLA #4: NUNCA CONFIRMES NI ACTIVES PAGOS DESDE EL FRONTEND

**[REQUIRED]** El frontend NUNCA activa una suscripción o entrega acceso a un recurso tras recibir la respuesta del cliente de Stripe. Los clientes pueden ser manipulados (modificando la respuesta JS). **Únicamente el webhook verificado de Stripe** en el backend puede activar planes, extender fechas de acceso o marcar facturas como pagadas.

```typescript
// ❌ INSEGURO Y PELIGROSO: Activar acceso porque el cliente lo dice
app.post('/api/payments/confirm', async (req, res) => {
  const { userId } = req.body
  // ⚠️ ¿Y si el atacante envió este POST manualmente sin pagar?
  await activateSubscription(userId)
})

// ✅ CORRECTO: El flujo de activación es 100% asíncrono y backend-only
// 1. Client inicia Stripe Checkout Session
// 2. Cliente paga en el iframe / Checkout de Stripe
// 3. Stripe envía webhook 'checkout.session.completed' a tu Worker
// 4. El Worker del webhook verifica firma y actualiza Supabase (DB)
```

---

## REGLA #5: ALMACENA SOLO METADATOS SEGUROS EN LA BASE DE DATOS

**[REQUIRED]** En la base de datos solo se almacenan referencias de Stripe (`stripe_customer_id`, `stripe_subscription_id`, `stripe_price_id`), los últimos 4 dígitos (`card_last4`) y la marca (`card_brand`) para visualización de la UI.

```sql
-- ❌ INSEGURO: Guardar campos sensibles en DB
-- NUNCA campos como card_number, cvc, exp_month en DB

-- ✅ ESQUEMA SEGURO DE SUSCRIPCIONES Y PAGOS
CREATE TABLE subscriptions (
  id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID        NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  team_id                UUID        REFERENCES teams(id) ON DELETE CASCADE,
  stripe_customer_id     TEXT        NOT NULL UNIQUE,
  stripe_subscription_id TEXT        NOT NULL UNIQUE,
  stripe_price_id        TEXT        NOT NULL,
  plan                   TEXT        NOT NULL CHECK (plan IN ('free', 'pro', 'enterprise')),
  status                 TEXT        NOT NULL CHECK (status IN ('active', 'past_due', 'canceled', 'trialing', 'unpaid')),
  current_period_start   TIMESTAMPTZ NOT NULL,
  current_period_end     TIMESTAMPTZ NOT NULL,
  canceled_at            TIMESTAMPTZ,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);

-- RLS: El usuario solo puede LEER su propia suscripción. Ninguna escritura via frontend.
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY sub_select_own ON subscriptions FOR SELECT
  USING ((SELECT auth.uid()) = user_id);
```

---

## REGLA #6: PRECIOS EN CENTAVOS (BIGINT), NUNCA FLOATS

**[REQUIRED]** Todo valor monetario se maneja como entero de la unidad mínima (`amount_cents` / `price_cents` de tipo `bigint` o `number` entero). Los números flotantes en IEEE 754 sufren de errores de precisión decimal (ej. `19.99 * 100` puede dar `1998.9999999999998`), causando descuadres financieros.

```typescript
// ❌ INSEGURO: Floats para dinero
const price = 19.99
await stripe.paymentIntents.create({
  amount: price * 100, // ⚠️ Riesgo de truncamiento o flotantes imprecisos
  currency: 'usd'
})

// ✅ CORRECTO: Integers / BigInt en centavos
const priceCents = 1999n // $19.99 exacto
await stripe.paymentIntents.create({
  amount: Number(priceCents), // 1999 centavos
  currency: 'usd'
})

// Conversión a UI (solo para formateo de presentación):
export const formatCurrency = (cents: number, currency = 'USD') =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100)
// formatCurrency(1999) → "$19.99"
```

---

## REGLA #7: PLANES Y PRECIOS DEFINIDOS SIEMPRE EN EL BACKEND

**[REQUIRED]** El frontend NUNCA envía el monto de un pago ni el precio de una suscripción en el payload del request. El frontend solo envía el identificador del plan (`planId: 'pro'`). El backend resuelve el precio y el `stripePriceId` desde una configuración inmutable server-side.

```typescript
// ❌ VULNERABLE: El cliente dice cuánto pagar
// Un atacante modifica el JSON en la consola a { plan: 'pro', price: 1 }
const { plan, price } = await request.json()

// ✅ CORRECTO: Configuración de planes en el Backend
const PLANS_CONFIG: Record<string, { priceCents: number; stripePriceId: string }> = {
  pro: {
    priceCents: 1999,
    stripePriceId: 'price_1NxxxPRO'
  },
  enterprise: {
    priceCents: 9999,
    stripePriceId: 'price_1NxxxENT'
  }
}

export async function createCheckoutSession(request: Request, env: Env) {
  const { planId } = await request.json()
  const plan = PLANS_CONFIG[planId]

  if (!plan) {
    return fail('INVALID_PLAN', 'El plan especificado no existe', 400)
  }

  const stripe = new Stripe(env.STRIPE_SECRET_KEY)
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{ price: plan.stripePriceId, quantity: 1 }],
    success_url: `${env.APP_URL}/dashboard?checkout=success`,
    cancel_url:  `${env.APP_URL}/pricing`,
    client_reference_id: request.headers.get('x-user-id')!
  })

  return ok({ url: session.url })
}
```

---

## REGLA #8: MANEJO ESTRUCTURADO DE ERRORES DE PAGO

**[REQUIRED]** Mapear los códigos de rechazo de Stripe a mensajes amigables y accionables para el usuario sin revelar detalles técnicos internos ni exponer datos de infraestructura.

```typescript
const STRIPE_ERROR_MAP: Record<string, { message: string; action: 'new_card' | 'retry' | 'support' }> = {
  'card_declined':       { message: 'Tu tarjeta fue rechazada. Intenta con otro método de pago.', action: 'new_card' },
  'insufficient_funds':  { message: 'Fondos insuficientes en la tarjeta.', action: 'new_card' },
  'expired_card':        { message: 'Tu tarjeta ha expirado. Actualiza la fecha de vencimiento.', action: 'new_card' },
  'incorrect_cvc':       { message: 'El código CVC es incorrecto.', action: 'retry' },
  'processing_error':    { message: 'Error temporal de procesamiento. Intenta nuevamente.', action: 'retry' },
  'rate_limit':          { message: 'Demasiados intentos. Espera unos minutos.', action: 'retry' }
}

export function formatStripeError(error: Stripe.StripeError) {
  const mapped = STRIPE_ERROR_MAP[error.code ?? ''] || {
    message: 'Ocurrió un error al procesar el pago. Por favor contacta a soporte.',
    action:  'support'
  }

  console.error('[STRIPE_PAYMENT_FAILED]', {
    code:         error.code,
    decline_code: error.decline_code,
    doc_url:      error.doc_url
  })

  return mapped
}
```

---

## SEGURIDAD ADICIONAL EN PASARELAS DE PAGO

### 1. Rate Limiting Estricto en Endpoints de Pago
```typescript
// Ref: ESTANDAR_RATE_LIMITING.md
// Máximo 3 intentos de creación de checkout/cobro por usuario en 5 minutos
const rateLimitResult = await rateLimit(request, env, 'authenticated', `payments:${userId}`)
if (rateLimitResult) return rateLimitResult // 429
```

### 2. Monitoreo Anti-Fraude
```typescript
// Si un usuario acumula > 5 pagos fallidos en 1 hora, bloquear temporalmente e inyectar alerta
async function checkFraudPattern(userId: string, env: Env) {
  const key = `failed_payments:${userId}`
  const count = await env.KV.get(key)
  const currentCount = count ? parseInt(count, 10) : 0

  if (currentCount >= 5) {
    console.warn(`[FRAUD_ALERT] Posible ataque de enumeración/tarjeteo por usuario ${userId}`)
    await sendSecurityAlertEmail(userId, 'Bloqueo preventivo por múltiples intentos fallidos', env)
    throw new Error('Cuenta bloqueada preventivamente por seguridad.')
  }

  await env.KV.put(key, (currentCount + 1).toString(), { expirationTtl: 3600 })
}
```

---

## CHECKLIST DE AUDITORÍA DE SEGURIDAD DE PAGOS

### Compliance PCI DSS (Mínimo Indispensable)
- [ ] ¿NUNCA se reciben ni procesan números de tarjeta, fechas o CVC en el backend/Worker?
- [ ] ¿Se utiliza Stripe Elements (iframe) o Stripe Checkout para la captura de tarjetas?
- [ ] ¿Se utiliza HTTPS en el 100% de las rutas de pago y checkout?
- [ ] ¿Los logs de Workers filtran y enmascaran cualquier token o payload sensible?

### Webhooks y Verificación
- [ ] ¿El handler de webhook verifica la firma usando `stripe.webhooks.constructEvent`?
- [ ] ¿Existe protección contra Replay Attacks chequeando y registrando el `event.id` en KV?
- [ ] ¿La activación de suscripciones ocurre NÚNICAMENTE en el handler del webhook verificado?
- [ ] ¿Toda mutación de cobro incluye un `Idempotency-Key` único?

### Precios e Integridad de Datos
- [ ] ¿Todos los valores monetarios se manejan como `bigint` / enteros en centavos?
- [ ] ¿Los planes y `stripePriceId` están definidos exclusivamente en el backend?
- [ ] ¿El frontend solo envía el ID de plan deseado, nunca el monto a cobrar?
- [ ] ¿Las políticas RLS impiden que un usuario modifique sus registros de suscripción en Supabase?
