---
title: "Plan de Escalabilidad, Observabilidad y Mantenimiento Post-Lanzamiento"
category: 08_Cloud
doc_type: estandar
tags: [cloud, escalabilidad, observabilidad, sentry, caching, backups, mantenimiento, sla]
summary: "Protocolo operativo para garantizar la estabilidad, observabilidad y escalabilidad de proyectos entregados: monitoreo de errores con Sentry, connection pooling de base de datos, caching en Edge de Cloudflare, políticas de backup y acuerdos de nivel de servicio (SLA)."
keywords: [escalabilidad, mantenimiento, sentry, cloudflare, cache, backups, supabase, pooling, sla]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md"
  - "04_Database/DATABASE_SCALABILITY_STANDARD.md"
  - "07_DevOps/OBSERVABILITY_STANDARD.md"
---

# PLAN DE ESCALABILIDAD, OBSERVABILIDAD Y MANTENIMIENTO POST-LANZAMIENTO

> **Objetivo:** Asegurar que los sistemas de los clientes soporten picos masivos de tráfico sin caerse, que cualquier error en producción se detecte antes de que el cliente lo note y establecer un modelo de mantenimiento recurrente para la agencia.

---

## 1. Observabilidad y Monitoreo de Errores en Tiempo Real

### Sentry para Frontend y Workers
**[REQUIRED]** Todo proyecto en producción debe integrar **Sentry** (o logger estructurado equivalente):
* **Frontend:** Captura excepciones no controladas de React, midiendo navegador, dispositivo y traza de error.
* **Cloudflare Workers:** Captura fallos 500 y latencias anormales en APIs.

```typescript
// src/lib/sentry.ts
import * as Sentry from '@sentry/react'

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.05,
    replaysOnErrorSampleRate: 1.0
  })
}
```

---

## 2. Escalabilidad de Base de Datos y Connection Pooling

**[REQUIRED]** Para evitar que picos de tráfico saturen el límite de conexiones de PostgreSQL:
1. **Connection Pooling con Supavisor (Supabase):**
   * Usar el puerto de pooler `6543` (modo transacción) para workers serverless de alto volumen.
2. **Índices Secundarios en Claves Foráneas (`DB-002`):**
   * Toda relación `user_id`, `order_id` o `org_id` debe tener un índice `B-Tree` para mantener consultas en < 5ms.
3. **Cero `SELECT *` (`DB-001`):**
   * Seleccionar únicamente las columnas requeridas para reducir ancho de banda y uso de memoria en la base de datos.

---

## 3. Caching Inteligente en el Edge (Cloudflare CDN)

Para soportar miles de peticiones simultáneas reduciendo las lecturas a la base de datos a casi cero:

```typescript
// Ejemplo en Worker para cachear respuestas públicas (ej. catálogo de productos)
export async function handleGetPublicCatalog(request: Request, env: Env, ctx: ExecutionContext) {
  const cache = caches.default
  const cacheKey = new Request(request.url, request)

  // 1. Buscar en la memoria caché del Edge
  let response = await cache.match(cacheKey)
  if (response) return response

  // 2. Si no está en caché, consultar la base de datos
  const data = await fetchCatalogFromDatabase(env)
  
  response = new Response(JSON.stringify({ ok: true, data }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=60, s-maxage=300' // 5 min en el Edge
    }
  })

  // 3. Guardar en caché en segundo plano sin retrasar al usuario
  ctx.waitUntil(cache.put(cacheKey, response.clone()))
  return response
}
```

---

## 4. Política de Respaldos (Backups) y Disaster Recovery

| Recurso | Frecuencia de Respaldo | Retención | Procedimiento de Restauración |
|---|---|---|---|
| **Base de Datos (Supabase)** | Diario automatizado (Point-in-Time Recovery) | 7 a 30 días | Restauración desde el dashboard de Supabase con 1 clic. |
| **Archivos / Storage (R2)** | Versionado de objetos activado | 30 días | Reversión de objetos eliminados accidentalmente. |
| **Código y Configuración** | Git (GitHub) con ramas protegidas | Permanente | Redeploy inmediato vía GitHub Actions. |

---

## 5. Acuerdos de Nivel de Servicio (SLA) para Clientes

Para contratos de mantenimiento mensual de la agencia:

* **P1 — Crítico (Sitio caído o pasarela de pago inaccesible):** Tiempo de respuesta < 2 horas.
* **P2 — Alto (Funcionalidad principal degradada):** Tiempo de respuesta < 6 horas.
* **P3 — Medio / Bajo (Ajustes de texto, cambios visuales menores):** Tiempo de respuesta < 24–48 horas hábiles.
