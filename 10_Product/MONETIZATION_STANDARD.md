---
title: "Estándar de Monetización, Pricing y Facturación"
category: 10_Product
doc_type: estandar
tags: [monetization, stripe, pricing, freemium, usage-based, billing, invoices, vat]
summary: "Estándar para esquemas de monetización y cobranza: planes (Free, Pro, Enterprise), facturación basada en uso (Usage-based billing), periodos de prueba, cálculo de impuestos con Stripe Tax y generación de facturas PDF."
keywords: [monetization, stripe, pricing, freemium, billing, invoices, usage-based, VAT, tax]
updated: 2026-07-27
status: current
---

# 💰 ESTÁNDAR DE MONETIZACIÓN Y COBRANZA

## 🎯 OBJETIVO
Definir los modelos de precios, la estrategia freemium, el cobro por métricas de uso (Metered Billing) y el cumplimiento de impuestos globales para maximizar el MRR (Monthly Recurring Revenue).

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] MONEY-001: Precios NUNCA definidos en el frontend.** El frontend envía identificadores de plan (`planId: 'pro'`); el Worker resuelve montos e IDs de Stripe server-side (`PAYMENTS_SECURITY_STANDARD.md`).

> **Por qué:** un precio que viaja desde el frontend es un precio que el usuario puede editar antes de enviarlo — la misma razón que `PAYMENTS_SECURITY_STANDARD.md` regla #7. El frontend solo puede pedir un plan por su identificador; el monto lo decide el Worker consultando su propia fuente de verdad.

**[REQUIRED] MONEY-002: Reintento suave de cobros fallidos (Dunning Management).** Ante un pago fallido (`past_due`), se conceden 7 días de gracia con notificaciones antes de revocar accesos.

> **Por qué:** cancelar la suscripción en el primer intento de cobro fallido castiga a usuarios cuyo problema es una tarjeta caducada, no falta de intención de pagar. Un periodo de gracia con reintentos recupera esos casos, que en la práctica son la mayoría de los fallos de cobro.

**[REQUIRED] MONEY-003: Impuestos (VAT / Sales Tax) calculados automáticamente.** Integración con Stripe Tax para cobro exacto de impuestos según la ubicación geográfica del cliente.

> **Por qué:** el IVA y el sales tax varían por jurisdicción y cambian con el tiempo; calcularlos a mano es una fuente garantizada de errores de cumplimiento fiscal que además escala con cada país nuevo que se suma. Delegarlo a un servicio especializado traslada ese riesgo fuera del producto.

---

## 💳 1. TABLA DE NIVELES DE PRECIO (PRICING TIERS)

| Nivel (Tier) | Precio | Límites | Características |
|---|---|---|---|
| **Free** | $0/mes | 3 Documentos, 1 Usuario | Funciones básicas, soporte de comunidad |
| **Pro** | $19.99/mes | Documentos Ilimitados, 5 Usuarios | Exportación PDF, IA, Soporte Prioritario |
| **Enterprise** | $99.99/mes | Usuarios Ilimitados, SSO SAML | SLA 99.9%, DPA personalizable, Account Manager |

---

## 📈 2. FACTURACIÓN BASADA EN USO (USAGE-BASED BILLING)

```typescript
// Reportar uso consumido a Stripe Metered Billing desde un Worker
import Stripe from 'stripe'

export async function reportUsageToStripe(
  subscriptionItemId: string,
  quantity: number,
  env: Env
) {
  const stripe = new Stripe(env.STRIPE_SECRET_KEY)

  // Reportar metros consumidos (ej. Créditos de IA usados)
  await stripe.subscriptionItems.createUsageRecord(
    subscriptionItemId,
    {
      quantity,
      timestamp: Math.floor(Date.now() / 1000),
      action: 'increment'
    }
  )
}
```

---

## 📑 3. GENERACIÓN DE FACTURAS PDF

```typescript
// Ref: PATRON_GENERACION_PDF_EDGE.md — Generar factura PDF en el Edge con pdf-lib
import { PDFDocument, rgb } from 'pdf-lib'

// FE-001 + DB-008: la factura es un documento de dinero — tipo explícito, monto en centavos enteros.
interface InvoiceData {
  number: string
  customerName: string
  amountCents: number      // DB-008: NUNCA float para dinero
  currency: 'USD' | 'MXN'
}

export async function generateInvoicePDF(invoiceData: InvoiceData): Promise<Uint8Array> {
  const pdfDoc = await PDFDocument.create()
  const page = pdfDoc.addPage([600, 400])

  page.drawText(`FACTURA DE COMPRA: #${invoiceData.number}`, { x: 50, y: 350, size: 20 })
  page.drawText(`Cliente: ${invoiceData.customerName}`, { x: 50, y: 310, size: 12 })
  page.drawText(`Monto Total: $${(invoiceData.amountCents / 100).toFixed(2)} USD`, { x: 50, y: 280, size: 14 })

  return await pdfDoc.save()
}
```

---

## 📋 CHECKLIST DE MONETIZACIÓN

- [ ] Estructura de planes configurada en Stripe Dashboard.
- [ ] Precios y Stripe Price IDs resueltos 100% en backend Workers.
- [ ] Stripe Tax activado para cálculo de IVA / VAT por país.
- [ ] Periodo de gracia de 7 días ante fallos de pago (`invoice.payment_failed`).
- [ ] Facturas PDF generadas y enviadas automáticamente por email.
