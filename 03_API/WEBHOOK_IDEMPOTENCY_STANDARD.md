---
title: "Estándar de Idempotencia y Resiliencia en Webhooks (Pagos y Eventos)"
category: 03_API
doc_type: estandar
tags: [api, webhooks, idempotency, pagos, stripe, wompi, nowpayments, resiliencia]
summary: "Protocolo de procesamiento seguro e idempotente de webhooks externos (Wompi, Stripe, NowPayments, WhatsApp). Uso de llaves de idempotencia, deduplicación en base de datos, validación criptográfica de firmas HMAC y manejo de reintentos sin duplicar cobros ni pedidos."
keywords: [webhooks, idempotencia, idempotency-key, pagos, firma-hmac, deduplicacion, transacciones]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "03_API/API_ENGINEERING_STANDARD.md"
  - "02_Backend/BACKEND_ENGINEERING_STANDARD.md"
---

# ESTÁNDAR DE IDEMPOTENCIA Y RESILIENCIA EN WEBHOOKS

> 💳 **Regla Inquebrantable (`API-IDEMP-001`):** Un webhook de pago o evento externo NUNCA debe procesarse dos veces. Los proveedores de pago (Stripe, Wompi, NowPayments) reintentan el envío de webhooks si hay latencia en la red. Si el backend no es **idempotente**, el cliente sufrirá dobles cobros, dobles créditos o activaciones duplicadas.

---

## 1. El Flujo Idempotente Seguro

```
[ Webhook de Pasarela ] ──► ( 1. Verificar Firma HMAC ) ──► ( 2. Bloqueo por Idempotency Key )
                                                                      │
                                         ┌────────────────────────────┴────────────────────────────┐
                                         ▼                                                         ▼
                                 [ ¿Ya Procesado? ]                                      [ ¿Primera vez? ]
                                         │                                                         │
                                         ▼                                                         ▼
                             ✅ Responder 200 OK                                   ⚙️ Procesar Pago en DB
                             (Ignorar duplicado)                                   ✅ Marcar 'PROCESSED'
                                                                                   ✅ Responder 200 OK
```

---

## 2. Esquema SQL para Registro de Idempotencia

```sql
CREATE TABLE IF NOT EXISTS public.processed_webhooks (
    idempotency_key TEXT PRIMARY KEY, -- ej. 'wompi_evt_987654321' o 'np_inv_12345'
    provider TEXT NOT NULL,           -- 'wompi', 'stripe', 'nowpayments'
    event_type TEXT NOT NULL,         -- 'payment.success', 'invoice.paid'
    status TEXT NOT NULL DEFAULT 'processing', -- 'processing', 'completed', 'failed'
    payload JSONB,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_processed_webhooks_processed_at ON public.processed_webhooks(processed_at);
```

---

## 3. Implementación Estándar en Cloudflare Worker

```typescript
import { verifyHmacSignature } from '../utils/crypto'

export async function handlePaymentWebhook(request: Request, env: Env) {
  // 1. Validar firma criptográfica (Evita atacantes enviando webhooks falsos)
  const signature = request.headers.get('x-signature') || request.headers.get('x-nowpayments-sig')
  const rawBody = await request.text()

  const isValid = await verifyHmacSignature(rawBody, signature, env.PAYMENT_WEBHOOK_SECRET)
  if (!isValid) {
    return new Response(JSON.stringify({ ok: false, error: 'Firma HMAC inválida' }), { status: 401 })
  }

  const event = JSON.parse(rawBody)
  const idempotencyKey = `${event.provider}_${event.event_id || event.payment_id}`

  // 2. Intentar registrar la llave de idempotencia
  const { data: existing } = await env.SUPABASE
    .from('processed_webhooks')
    .select('status')
    .eq('idempotency_key', idempotencyKey)
    .single()

  if (existing?.status === 'completed') {
    // Ya fue procesado exitosamente antes -> Responder 200 OK inmediato para calmar al proveedor
    return new Response(JSON.stringify({ ok: true, message: 'Evento ya procesado previamente' }), { status: 200 })
  }

  // 3. Registrar estado 'processing'
  await env.SUPABASE.from('processed_webhooks').upsert({
    idempotency_key: idempotencyKey,
    provider: event.provider,
    event_type: event.type,
    status: 'processing'
  })

  // 4. Ejecutar la lógica de negocio (Activar suscripción, acreditar saldo, etc.)
  try {
    await executePaymentActivation(event.data, env)

    // 5. Marcar como completado
    await env.SUPABASE
      .from('processed_webhooks')
      .update({ status: 'completed' })
      .eq('idempotency_key', idempotencyKey)

    return new Response(JSON.stringify({ ok: true }), { status: 200 })
  } catch (err) {
    console.error('[WEBHOOK_ERROR]', err)
    // Marcar como fallido para permitir reintento si fue un error transitorio
    await env.SUPABASE
      .from('processed_webhooks')
      .update({ status: 'failed' })
      .eq('idempotency_key', idempotencyKey)

    return new Response(JSON.stringify({ ok: false, error: 'Fallo al procesar webhook' }), { status: 500 })
  }
}
```
