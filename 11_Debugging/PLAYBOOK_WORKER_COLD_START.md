---
title: "Incident Playbook: Worker Cold Start"
category: 11_Debugging
tags: [incident, playbook, workers, performance, cold-start]
summary: "Playbook ante latencia intermitente por cold start de Workers: cómo confirmarlo en 30 segundos, soluciones ordenadas de menor a mayor dificultad y health check de latencia."
keywords: [incident, playbook, workers, performance, cold-start, worker, cold, start, ante, latencia, intermitente, confirmarlo, segundos, soluciones]
updated: 2026-07-27
status: current
---

# 🚨 PLAYBOOK: WORKER COLD START (LATENCIA INTERMITENTE)

## 🩺 SÍNTOMA
Los usuarios se quejan de que "a veces la app es rápida y a veces tarda un segundo entero en responder". Los monitores de Uptime muestran picos ocasionales de latencia de 400-800ms.

## ⏱️ DIAGNÓSTICO EN 30 SEGUNDOS
1. Ve al dashboard de Cloudflare Workers → Metrics. Busca picos en la latencia p99 y p90, mientras la mediana (p50) es estable.
2. Inspect en el navegador: Si el header `cf-worker-start` no coincide o es muy lento respecto al TTFB (Time To First Byte), el Worker estaba dormido.
3. El *Cold Start* es el tiempo que tarda Cloudflare en inicializar el *V8 isolate* y cargar tu código Javascript en memoria global.

---

## 🔍 SOLUCIONES (DE MENOR A MAYOR DIFICULTAD)

### Solución 1: El CRON Warm-up (La curita rápida)
Si tu aplicación tiene bajo tráfico (ej: un SaaS corporativo que nadie usa a las 3 AM), los Workers se duermen. 
**Regla:** ES OBLIGATORIO configurar un CRON trigger para evitar el deep sleep.

```toml
# wrangler.toml
[triggers]
crons = ["*/5 * * * *"] # Ping cada 5 minutos
```

```typescript
// src/index.ts
export default {
  async scheduled(event: ScheduledEvent, env: Env) {
    if (event.cron === "*/5 * * * *") {
      // Un simple fetch para mantener el isolate vivo
      // NUNCA toques la DB aquí para no sumar costos
      return;
    }
  },
  // ... resto del worker
}
```

### Solución 2: Reducir el Bundle Size a Muerte
Cloudflare cobra (en tiempo) el parseo de tu Javascript inicial. Si tu Worker pesa 3MB porque importaste toda la librería `aws-sdk` o `lodash`, el cold start durará 800ms.
**Regla:** PROHIBIDO subir bundles de más de 500KB a Workers.

1. Usa `wrangler deploy --dry-run --outdir dist/` para ver el peso.
2. Haz importaciones explícitas: `import { format } from 'date-fns'` NUNCA `import dateFns from 'date-fns'`.

### Solución 3: Eliminar Carga Global Pesada
Cualquier código fuera del bloque `fetch` se ejecuta en el cold start.
```typescript
// ❌ HORRIBLE: Este regex enorme o configuración se parsea en el cold start de cada isolate.
const GIGANTIC_DICTIONARY = JSON.parse('... 500KB de texto ...') 

export default {
  async fetch(...) { ... }
}
```

### Solución 4: Workers Unbound (Para cargas CPU intensivas)
Si el problema no es el arranque sino que la petición requiere más de 50ms de CPU continuos, el plan gratuito de Cloudflare limitará la petición.
**Solución:** Cambia a uso Unbound si realizas criptografía, manipulación de imágenes o procesamientos pesados.

---

## 💻 CÓDIGO: HEALTH CHECK DE LATENCIA

Implementa este endpoint para medir empíricamente cuándo ocurre un cold start vs tiempo de DB.

```typescript
// En tu router del Worker (ej: Hono)
let isWarm = false; // Variable global del isolate
const isolateId = crypto.randomUUID();

app.get('/api/health', async (c) => {
  const start = performance.now();
  
  const wasWarm = isWarm;
  isWarm = true; // Si es false, sabemos 100% que fue cold start
  
  // Pingeamos D1 rápido
  const dbStart = performance.now();
  await c.env.DB.prepare("SELECT 1").first();
  const dbTime = performance.now() - dbStart;
  
  const totalTime = performance.now() - start;

  return c.json({
    status: 'ok',
    isolateId, // Si cambia en el siguiente request, fue a otro servidor Edge
    wasWarm,
    metrics: {
      dbLatencyMs: Math.round(dbTime),
      workerCpuMs: Math.round(totalTime - dbTime),
      totalLatencyMs: Math.round(totalTime)
    }
  });
});
```

**Métrica clave:** Monitorea este endpoint. Si `wasWarm` es false constantemente, tu tráfico está muy distribuido o la memoria global está reventando y Cloudflare te expulsa.
