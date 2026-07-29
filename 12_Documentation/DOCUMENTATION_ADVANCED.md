---
title: "Estándar Avanzado de Documentación Viva, Onboarding y Status Page"
category: 12_Documentation
tags: [documentation, changelog, storybook, onboarding, status-page, tooltips, openapi-diff]
summary: "Estándar para documentación avanzada y viva: Changelogs de API automáticos mediante diffs OpenAPI, despliegue de Storybook, guías de onboarding contextual e integración de Status Page."
keywords: [documentation, changelog, openapi-diff, storybook, onboarding, status-page, tooltips, walkthroughs]
updated: 2026-07-27
status: current
---

# 📚 ESTÁNDAR AVANZADO DE DOCUMENTACIÓN VIVA Y ONBOARDING

## 🎯 OBJETIVO
Mantener la documentación en perfecta sincronía con el código de producción, ofrecer guías de inicio rápido contextuales dentro de la aplicación y comunicar el estado operativo de los servicios.

---

## 🎯 REGLAS INQUEBRANTABLES

**DOC-001: Todo código de error devuelto por la API DEBE incluir un enlace a su documentación con la solución.**

**DOC-002: Detectar Breaking Changes en CI mediante OpenAPI Diff.** Si un PR altera un endpoint destruyendo la compatibilidad hacia atrás, la build debe fallar automáticamente.

---

## 🛑 1. DETECCIÓN DE BREAKING CHANGES EN API (OPENAPI DIFF)

```yaml
# .github/workflows/api-diff.yml
name: OpenAPI Breaking Changes Guard
on: [pull_request]

jobs:
  api-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generar OpenAPI actual
        run: pnpm run generate:openapi
      - name: Comparar con OpenAPI en main
        uses: oasdiff/oasdiff-action@v1
        with:
          base: 'https://api.collabscribe.com/api/docs/json'
          revision: './openapi.json'
          fail-on-diff: true
```

---

## 🌐 2. INTEGRACIÓN DE STATUS PAGE PÚBLICA

La infraestructura expone un endpoint `/health` público que es monitoreado por una plataforma de Status Page externa (ej. Better Stack / Statuspage.io).

```typescript
// GET /health
export async function handleHealthCheck(request: Request, env: Env): Promise<Response> {
  const dbOk = await checkSupabaseConnection()
  const kvOk = await checkKVConnection(env)

  const isHealthy = dbOk && kvOk

  return new Response(JSON.stringify({
    status: isHealthy ? 'HEALTHY' : 'DEGRADED',
    checks: { database: dbOk, kv: kvOk },
    timestamp: new Date().toISOString()
  }), {
    status: isHealthy ? 200 : 503,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

---

## 📋 CHECKLIST DE DOCUMENTACIÓN AVANZADA

- [ ] Respuestas de error conteniendo propiedad `doc_url` con la solución.
- [ ] Pipeline CI con validación OpenAPI Diff contra Breaking Changes.
- [ ] Endpoint `/health` expuesto para integración con Status Page.
- [ ] Catálogo Storybook desplegado de forma continua en Cloudflare Pages.
