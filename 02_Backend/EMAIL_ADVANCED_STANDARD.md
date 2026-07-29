---
title: "Estándar Avanzado de Envíos de Email y Entregabilidad"
category: 02_Backend
tags: [email, resend, react-email, tracking, webhooks, warming, spam-score, ab-testing]
summary: "Estándar para entregabilidad avanzada de emails: plantillas versionadas con React Email, A/B testing de asuntos, tracking respetuoso de privacidad, webhook de rebotes (bounces), calentamiento de IP/dominio y análisis de spam."
keywords: [email, resend, react-email, tracking, webhooks, bounces, spam, warming, ab-testing]
updated: 2026-07-27
status: current
---

# 📧 ESTÁNDAR AVANZADO DE CORREOS ELECTRÓNICOS Y ENTREGABILIDAD

## 🎯 OBJETIVO
Optimizar la entregabilidad a bandeja de entrada (Inbox Rate), gestionar reputación de dominios, procesar eventos de rebote (Bounces) y medir el rendimiento de campañas e emails transaccionales.

---

## 🎯 REGLAS INQUEBRANTABLES

**EMAIL-001: Email Transaccional entregado en < 5 segundos.** Todos los correos de sistema (magic links, verificaciones, 2FA) deben encolarse y procesarse con prioridad ultra-alta.

**EMAIL-002: Limpieza inmediata de direcciones rebotadas (Bounces / Complaints).** Si Resend notifica un rebote duro (`hard_bounce`) o queja por spam (`complaint`), la dirección DEBE marcarse como deshabilitada en la base de datos de inmediato.

**EMAIL-003: Autenticación de Dominio Completa (SPF, DKIM, DMARC p=reject).** Queda prohibido enviar correos desde dominios sin registros DMARC configurados.

---

## 🔔 1. WEBHOOK DE EVENTOS DE EMAIL (RESEND)

```typescript
// apps/notif-worker/src/webhooks/resend.ts
export async function handleResendWebhook(request: Request, env: Env): Promise<Response> {
  const payload = await request.json() as {
    type: 'email.sent' | 'email.delivered' | 'email.bounced' | 'email.complained'
    data: { email_id: string; to: string[]; created_at: string }
  }

  switch (payload.type) {
    case 'email.bounced':
    case 'email.complained': {
      const emailAddress = payload.data.to[0]
      console.warn(`[EMAIL_BOUNCE_COMPLAINT] Deshabilitando email: ${emailAddress}`)
      
      // EMAIL-002: Marcar como inactivo para proteger la reputación del dominio
      await supabase
        .from('profiles')
        .update({ email_disabled: true, bounce_reason: payload.type })
        .eq('email', emailAddress)
      break
    }
    case 'email.delivered':
      console.info(`[EMAIL_DELIVERED] ID: ${payload.data.email_id}`)
      break
  }

  return new Response('OK', { status: 200 })
}
```

---

## 🧪 2. A/B TESTING DE ASUNTOS DE CORREO

```typescript
export function selectEmailSubject(userId: string, variantA: string, variantB: string): string {
  // Selección determinista 50/50 basada en el ID del usuario
  const charCode = userId.charCodeAt(userId.length - 1)
  return charCode % 2 === 0 ? variantA : variantB
}
```

---

## 📋 CHECKLIST AVANZADO DE EMAIL

- [ ] Registros SPF, DKIM y DMARC `p=reject` validados en DNS.
- [ ] Webhook de Resend configurado para capturar `email.bounced` y `email.complained`.
- [ ] Supabase actualiza `email_disabled = true` al recibir un rebote duro.
- [ ] Plantillas React Email validadas sin HTML crudo.
- [ ] Tiempo de entrega de emails transaccionales < 5 segundos.
