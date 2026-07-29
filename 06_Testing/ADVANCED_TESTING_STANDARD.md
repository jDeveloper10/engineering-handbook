---
title: "Estándar Avanzado de Pruebas y QA"
category: 06_Testing
tags: [testing, k6, chaos-engineering, fast-check, percy, pact, stryker, coverage]
summary: "Estándar avanzado de pruebas de software: Pruebas de Carga con k6, Chaos Engineering, Property-based testing con fast-check, Visual Regression con Chromatic, Contract testing con Pact y Mutation testing con Stryker."
keywords: [k6, chaos-engineering, fast-check, percy, chromatic, pact, stryker, coverage, load-testing, mutation-testing]
updated: 2026-07-27
status: current
---

# 🧪 ESTÁNDAR AVANZADO DE PRUEBAS Y QA

## 🎯 OBJETIVO
Definir las técnicas de validación avanzadas para garantizar el rendimiento bajo presión, la resiliencia ante fallos catastróficos, la calidad visual y la cobertura efectiva de las aplicaciones.

---

## 🎯 REGLAS INQUEBRANTABLES

**TEST-001: Pruebas de Carga (k6) OBLIGATORIAS antes de cada release mayor.** Ninguna aplicación sale a producción sin validar que soporta el percentil 95 (P95) < 300ms al 150% de la carga esperada.

**TEST-002: La cobertura de código (Coverage) mínima es del 80%.** Los módulos de pagos, autenticación y seguridad exigen **95% de cobertura comprobada**.

**TEST-003: Pruebas de Mutación con Stryker > 70% Score.** Las pruebas no solo se miden por las líneas ejecutadas, sino por su capacidad real de detectar fallos inducidos.

---

## ⚡ 1. PRUEBAS DE CARGA Y ESTRÉS CON K6

### Script de Rendimiento k6
```javascript
// tests/load/k6-load-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up a 50 Virtual Users (VUs)
    { duration: '1m',  target: 200 }, // Carga sostenida de 200 VUs
    { duration: '30s', target: 0 }    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'], // 95% de peticiones por debajo de 300ms
    http_req_failed:   ['rate<0.01']  // Menos del 1% de errores HTTP
  }
}

export default function () {
  const res = http.get('https://api.collabscribe.com/api/public/documents/sample-token')
  check(res, {
    'status es 200': (r) => r.status === 200,
    'tiempo < 250ms': (r) => r.timings.duration < 250
  })
  sleep(1)
}
```

---

## 🎲 2. PROPERTY-BASED TESTING CON FAST-CHECK

Prueba funciones con cientos de inputs generados aleatoriamente para descubrir edge cases que ningún desarrollador imaginó.

```typescript
// tests/unit/sanitize.test.ts
import { test, expect } from 'vitest'
import fc from 'fast-check'
import { sanitizeInput } from '@/lib/sanitize'

test('Property: sanitizeInput NUNCA debe retornar etiquetas script', () => {
  fc.assert(
    fc.property(fc.string(), (randomString) => {
      const sanitized = sanitizeInput(randomString)
      expect(sanitized).not.toContain('<script>')
      expect(sanitized).not.toContain('</script>')
    })
  )
})
```

---

## 🎨 3. VISUAL REGRESSION TESTING CON CHROMATIC / PERCY

Detecta cambios involuntarios de estilo o pixel-shift en componentes React.

```typescript
// src/components/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button
}
export default meta

export const Primary: StoryObj<typeof Button> = {
  args: { variant: 'primary', children: 'Guardar Cambios' }
}

export const Danger: StoryObj<typeof Button> = {
  args: { variant: 'danger', children: 'Eliminar Cuenta' }
}
```

---

## 🤝 4. CONTRACT TESTING CON PACT

Garantiza que los cambios en el backend Worker no rompan el contrato consumido por el frontend React.

```typescript
// tests/contract/consumer.spec.ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact'

const provider = new PactV3({
  consumer: 'ReactFrontend',
  provider: 'DocsWorker'
})

test('Contrato API: Obtener documento por ID', async () => {
  provider
    .given('Existe el documento 123')
    .uponReceiving('Petición de detalle de documento')
    .withRequest({
      method: 'GET',
      path: '/api/documents/123'
    })
    .willRespondWith({
      status: 200,
      body: {
        success: true,
        data: {
          id: MatchersV3.string('123'),
          title: MatchersV3.string('Título de prueba')
        }
      }
    })

  await provider.executeTest(async (mockServer) => {
    const res = await fetch(`${mockServer.url}/api/documents/123`)
    const json = await res.json()
    expect(json.data.title).toBe('Título de prueba')
  })
})
```

---

## 🧬 5. MUTATION TESTING CON STRYKER

Inyecta mutaciones (bugs sintéticos) en tu código para comprobar si tus pruebas fallan como deberían.

```json
// stryker.config.json
{
  "$schema": "./node_modules/@stryker-mutator/core/schema/stryker-schema.json",
  "packageManager": "pnpm",
  "reporters": ["html", "clear-text", "progress"],
  "testRunner": "vitest",
  "coverageAnalysis": "perTest",
  "thresholds": { "high": 80, "low": 60, "break": 70 }
}
```

---

## 📋 CHECKLIST AVANZADO DE QA

- [ ] Pruebas de carga k6 ejecutadas en entorno Staging.
- [ ] Percentil P95 < 300ms y tasa de error < 1% bajo 200 VUs.
- [ ] Cobertura de código en Vitest >= 80% global.
- [ ] Score de mutación en Stryker >= 70%.
- [ ] Capturas de regresión visual verificadas en Chromatic/Percy.
