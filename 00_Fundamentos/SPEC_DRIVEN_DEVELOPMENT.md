---
title: "Metodología de Desarrollo: Spec-Driven y Contratos Primero"
category: 00_Fundamentos
doc_type: estandar
tags: [metodologia, spec-driven, tdd, zod, contratos, flujo-trabajo]
summary: "Protocolo obligatorio de desarrollo para la agencia: Especificación -> Contrato Zod -> Prueba Unitaria -> Implementación -> Verificación. Elimina la improvisación y garantiza que el código cumpla exactamente con los requerimientos."
keywords: [spec-driven, contratos, zod, tdd, flujo, desarrollo, metodologia, testing]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "00_HANDBOOK_FORMAT.md"
  - "13_AI_Rules/AI_WORKFLOW.md"
  - "06_Testing/Strategy/01_QA_STRATEGY.md"
---

# METODOLOGÍA DE DESARROLLO: SPEC-DRIVEN & CONTRATOS PRIMERO

> **Principio Fundamental:** Escribir código sin una especificación y un esquema de validación previo es programar a ciegas. Este protocolo define los **5 pasos obligatorios** que sigue todo desarrollador o agente de IA antes de dar por completada una funcionalidad.

---

## 🔄 El Flujo de los 5 Pasos

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. SPEC         │ ──► │ 2. SCHEMA (ZOD) │ ──► │ 3. TEST (QA)    │ ──► │ 4. CODE         │ ──► │ 5. VERIFY       │
│ Escribir qué    │     │ Definir contrato│     │ Escribir test   │     │ Implementar     │     │ Validar en verde│
│ debe hacer      │     │ de entrada/salida│    │ que falla (Red) │     │ la lógica (Green│     │ y sin errores   │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

### Paso 1: Especificación (Spec)
Antes de crear un archivo `.ts` o `.tsx`, redacta en 5 líneas qué problema resuelve la función o endpoint, qué recibe y qué responde.
* *Ejemplo:* Endpoint para registrar el pago de una suscripción. Recibe `{ planId, paymentMethod }`, calcula el monto en el servidor y devuelve `{ ok: true, checkoutUrl }`.

---

### Paso 2: Definición del Contrato con Zod (`S-001`)
**[REQUIRED]** Se crea el esquema Zod de validación estricta para la entrada y la salida:

```typescript
// src/schemas/paymentSchema.ts
import { z } from 'zod'

export const CreatePaymentInputSchema = z.object({
  planId: z.enum(['pro_monthly', 'pro_annual', 'lifetime']),
  paymentMethod: z.enum(['card', 'crypto', 'wompi']),
  affiliateCode: z.string().max(20).optional()
})

export type CreatePaymentInput = z.infer<typeof CreatePaymentInputSchema>
```

---

### Paso 3: Prueba Automatizada Primero (Test-First)
**[REQUIRED]** Escribir la prueba que define el comportamiento esperado antes de programar la lógica interna:

```typescript
// tests/payment.test.ts
import { describe, it, expect } from 'vitest'
import { handleCreatePayment } from '../src/handlers/payment'

describe('Payment Handler', () => {
  it('debe rechazar un plan inválido con 400 Bad Request', async () => {
    const req = new Request('https://api.test/payment', {
      method: 'POST',
      body: JSON.stringify({ planId: 'plan_inexistente', paymentMethod: 'card' })
    })
    const res = await handleCreatePayment(req, mockEnv)
    expect(res.status).toBe(400)
    const json = await res.json()
    expect(json.ok).toBe(false)
  })
})
```

---

### Paso 4: Implementación de la Lógica (Clean Code)
Se codifica la solución manteniendo funciones puras, legibles y de una sola responsabilidad:

```typescript
// src/handlers/payment.ts
import { CreatePaymentInputSchema } from '../schemas/paymentSchema'

export async function handleCreatePayment(request: Request, env: Env) {
  const body = await request.json().catch(() => null)
  const validation = CreatePaymentInputSchema.safeParse(body)

  if (!validation.success) {
    return new Response(JSON.stringify({
      ok: false,
      error: 'Datos de entrada inválidos',
      details: validation.error.flatten()
    }), { status: 400, headers: { 'Content-Type': 'application/json' } })
  }

  // Lógica de negocio autoritativa (MONEY-001)
  const checkoutUrl = await generateCheckout(validation.data, env)
  return new Response(JSON.stringify({ ok: true, checkoutUrl }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

---

### Paso 5: Verificación y Cierre
Ejecutar la suite de pruebas localmente:
```bash
npm run test
npm run check
```
Si la prueba pasa en verde y no hay violaciones de linter ni tipos TypeScript, la tarea pasa a revisión.
