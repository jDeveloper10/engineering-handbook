---
title: "Estándar de Product Analytics, Funnels y A/B Testing"
category: 10_Product
tags: [analytics, posthog, funnels, ab-testing, feature-flags, durable-objects, cohort]
summary: "Estándar para analítica de producto con PostHog: instrumentación de eventos en cliente/servidor, análisis de embudos y cohortes, experimentos A/B y Feature Flags con Cloudflare KV y Durable Objects."
keywords: [posthog, analytics, funnels, cohort, ab-testing, feature-flags, retention, events]
updated: 2026-07-27
status: current
---

# 📊 ESTÁNDAR DE PRODUCT ANALYTICS Y EXPERIMENTACIÓN

## 🎯 OBJETIVO
Establecer un marco unificado de telemetría e instrumentación para medir la adopción de funcionalidades, retención de usuarios, rendimiento de embudos de conversión y ejecución segura de pruebas A/B.

---

## 🎯 REGLAS INQUEBRANTABLES

**ANALYTICS-001: Todo nuevo PRD DEBE incluir la lista de eventos de analítica a instrumentar.** Ninguna feature entra a desarrollo sin sus eventos de seguimiento definidos.

**ANALYTICS-002: NUNCA capturar PII ni datos sensibles en eventos de analítica.** Contraseñas, tokens, tarjetas de crédito o emails en texto plano deben ser filtrados antes del envío.

**ANALYTICS-003: Feature Flags gestionadas en el Edge.** Toda prueba A/B se evalúa en Cloudflare Workers (KV/Durable Objects) en < 5ms para evitar parpadeos de UI (Layout Shift).

---

## 📈 1. INSTRUMENTACIÓN DE EVENTOS CON POSTHOG

### Inicialización en Frontend (React)
```typescript
// src/lib/analytics.ts
import posthog from 'posthog-js'

export function initAnalytics() {
  if (typeof window === 'undefined') return

  posthog.init(import.meta.env.VITE_POSTHOG_KEY, {
    api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://app.posthog.com',
    autocapture: false, // Desactivar autocapture para control estricto de eventos
    capture_pageview: true,
    persistence: 'localStorage'
  })
}

export function trackEvent(eventName: string, properties?: Record<string, any>) {
  posthog.capture(eventName, properties)
}
```

### Eventos Estándar del Ecosistema
```typescript
// Nombres de eventos en snake_case: <objeto>_<acción>
trackEvent('document_created', { template: 'proposal', team_id: '123' })
trackEvent('checkout_started', { plan: 'pro', billing_cycle: 'monthly' })
trackEvent('feature_used', { feature_name: 'crdt_editor' })
```

---

## 🚩 2. FEATURE FLAGS Y EXPERIMENTACIÓN A/B EN EL EDGE

### Worker: Evaluación de Flags con Cloudflare KV
```typescript
// apps/api-gateway/src/middleware/featureFlags.ts
export async function getFeatureFlag(
  flagKey: string,
  userId: string,
  env: Env
): Promise<boolean> {
  // 1. Intentar KV
  const flagConfig = await env.KV.get(`flag:${flagKey}`, 'json') as { enabled: boolean; percentage: number } | null

  if (!flagConfig || !flagConfig.enabled) return false

  // 2. Rollout por porcentaje determinista (Hash determinista por userId)
  const hash = await crypto.subtle.digest(
    'SHA-256',
    new TextEncoder().encode(`${userId}:${flagKey}`)
  )
  const hashArray = Array.from(new Uint8Array(hash))
  const userScore = hashArray[0] % 100 // Valor de 0 a 99

  return userScore < flagConfig.percentage
}
```

---

## 🎯 3. ANÁLISIS DE EMBUDOS (FUNNELS) Y RETENCIÓN DE COHORTES

### Ejemplo de Embudo de Conversión Principal
```text
Paso 1: visitor_landing_page   ──→ (100% - Baseline)
Paso 2: user_signed_up         ──→ (Conversión Adquisición: 12%)
Paso 3: document_created       ──→ (Activación: 65% de registrados)
Paso 4: checkout_completed     ──→ (Monetización: 8% de activos)
```

---

## 📋 CHECKLIST DE PRODUCT ANALYTICS

- [ ] PostHog o herramienta de telemetría inicializada sin autocapture invasivo.
- [ ] Eventos nombrados según convención `<objeto>_<acción>`.
- [ ] PII y tokens excluidos de payloads de analítica.
- [ ] Feature Flags evaluadas en el Edge sin parpadeo de UI.
- [ ] Embudo de conversión documentado y visualizado en dashboard.
