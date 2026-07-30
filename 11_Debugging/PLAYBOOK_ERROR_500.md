---
title: "Incident Playbook: Error 500 Global"
category: 11_Debugging
doc_type: runbook
tags: [incident, playbook, error-500, crash, workers]
summary: "Playbook ante error 500 global: diagnóstico en 30 segundos, causas frecuentes de crash en Workers y manejador de errores global blindado."
keywords: [incident, playbook, error-500, crash, workers, error, global, ante, diagnostico, segundos, causas, frecuentes, manejador, errores]
updated: 2026-07-27
status: current
---

# PLAYBOOK: ERROR 500 GLOBAL (CRASH)

## SÍNTOMA
Los usuarios reportan un mensaje genérico de "Something went wrong" (Error HTTP 500). Puede ser en un solo endpoint o en toda la aplicación.

## DIAGNÓSTICO EN 30 SEGUNDOS
1. **Cloudflare Dashboard (Workers):** Observa los **Exceptions** (errores no controlados) en tiempo real. Activa el Tail Logging (Logs en vivo).
2. **Si no hay logs:** Significa que Cloudflare bloqueó la ejecución *antes* de que iniciara (falta variable de entorno, binding roto o error de sintaxis JS).
3. **Sentry/Logflare:** ¿Hay un stack trace que apunte a un `undefined is not an object` o a un fallo de parseo JSON?

---

## CAUSAS Y SOLUCIONES DE HIERRO

### Causa 1: Excepción No Controlada (JSON parsing)
Alguien intentó parsear el body de un request como JSON sin un bloque `try/catch`.
**Solución:** PROHIBIDO llamar a `request.json()` ciegamente. Validar siempre con Zod.

### Causa 2: Variables de Entorno Faltantes
Desplegaste a Producción pero olvidaste añadir un secreto (ej. `STRIPE_KEY`).
**Solución:** ES OBLIGATORIO tener una validación de variables de entorno al arranque. Si faltan, crashear en build-time, no en run-time.

### Causa 3: D1 Query Mal Formada
Añadiste un string no parametrizado y rompió la sintaxis SQL.
**Solución:** NUNCA inyectar strings en `DB.prepare()`. Siempre usar `?` o bindings de Prisma/Drizzle.

### Causa 4: Service Binding o R2 Inaccesible
El entorno de Producción no tiene configurado el R2 Bucket.
**Solución:** Validar el `wrangler.toml` de producción (`env.production`).

### Causa 5: Límite de Tiempo Excedido (CPU > 30s)
Tu worker se quedó iterando un bucle gigante. Cloudflare lo mató por la fuerza.
**Solución:** Encolar tareas pesadas en Cloudflare Queues.

---

## CÓDIGO: GLOBAL ERROR HANDLER BLINDADO

El Worker NUNCA debe devolver el string puro de Cloudflare "Error 1101". ES OBLIGATORIO envolver toda la aplicación con un interceptor de errores globales.

### 1. El Global Boundary (Hono/Express)

```typescript
import { Hono } from 'hono'

const app = new Hono()

// Middleware de Logs
app.use('*', async (c, next) => {
  const start = Date.now()
  await next()
  console.log(`[${c.req.method}] ${c.req.url} - ${c.res.status} - ${Date.now() - start}ms`)
})

// EL ESCUDO FINAL: Error Handler Global
app.onError((err, c) => {
  // 1. Loggear en Sentry / Logflare / Consola (con Stack trace)
  console.error('🔥 CRITICAL ERROR:', err)
  console.error('Stack:', err.stack)

  // 2. Distinguir errores operacionales (400) de bugs (500)
  if (err.name === 'ZodError') {
    return c.json({ error: 'Validación incorrecta', details: err }, 400)
  }

  // 3. Fallback genérico para 500 (NUNCA exponer secretos o DB queries al frontend)
  return c.json({ 
    success: false,
    error: 'Error interno del servidor.',
    code: 'INTERNAL_ERROR',
    traceId: c.req.header('cf-ray') // Crucial para buscarlo en logs de CF
  }, 500)
})
```

### 2. Degradación Graceful en Frontend (React)

NUNCA dejes la pantalla en blanco. ES OBLIGATORIO usar un Error Boundary global o de sección.

```tsx
// React Error Boundary (para renders caídos)
import { ErrorBoundary } from 'react-error-boundary'

function FallbackUI({ error, resetErrorBoundary }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-center">
      <h3 className="text-red-800 font-bold">Uy, algo se rompió por aquí.</h3>
      <p className="text-sm text-red-600 mb-4">No te preocupes, nuestros ingenieros ya fueron notificados.</p>
      
      {/* Permitir al usuario reintentar sin recargar la página */}
      <button 
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Reintentar carga
      </button>
      
      {/* ID de seguimiento para que lo envíen a soporte */}
      <p className="mt-2 text-xs text-gray-400">Trace ID: {error.message.split('Trace:')[1]}</p>
    </div>
  )
}

// Uso: Envuelve componentes riesgosos (ej. Dashboard)
<ErrorBoundary FallbackComponent={FallbackUI}>
  <DashboardMetrics />
</ErrorBoundary>
```
