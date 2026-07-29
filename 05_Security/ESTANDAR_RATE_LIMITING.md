---
title: "Estándar de Rate Limiting"
category: 05_Security
doc_type: estandar
tags: [rate-limit, ddos, seguridad, workers]
summary: "Rate limiting en Cloudflare Workers contra fuerza bruta, password spraying y enumeración de identificadores, con las reglas inquebrantables de por dónde y cómo aplicarlo."
keywords: [rate-limit, ddos, seguridad, workers, rate, limiting, cloudflare, contra, fuerza, bruta, password, spraying, enumeracion, identificadores]
updated: 2026-07-27
status: current
---

# Estándar de Rate Limiting (Cloudflare Workers)

## El Problema
Endpoints desprotegidos son vectores de ataques de fuerza bruta (DDoS aplicativo, password spraying, enumeración de IDs, adivinación de tokens públicos). Sin un estándar, cada desarrollador crea su propia versión ineficiente basada en contadores en KV (lo cual viola la regla de Cloudflare de *NUNCA guardar contadores en KV* debido a la eventual consistencia).

## La Solución

Cloudflare Workers carece de una API nativa gratuita de Rate Limiting en código (WAF es a nivel dominio). Para implementar rate limit a nivel aplicativo (endpoints específicos) se debe utilizar un **Durable Object (DO)** o un servicio especializado (Upstash Redis).
Aquí se define el middleware de uso genérico.

### Límites por Defecto

- **[REQUIRED] Endpoints Públicos (Ej. `/api/public/proposals/:token`):** Máximo 10 requests / minuto por IP.
- **[REQUIRED] Endpoints Autenticados (Ej. APIs estándar):** Máximo 100 requests / minuto por Usuario/IP.

### 1. Middleware Reusable

Todo manejador de ruta que requiera límite debe invocar este middleware antes de ejecutar la lógica de negocio.
La llave (`key`) para usuarios anónimos SIEMPRE es el header `CF-Connecting-IP`. Para usuarios logueados, puede ser el `user.id`.

```javascript
// src/middleware/rateLimit.js
import { fail } from '../lib/response.js';

export async function rateLimit(request, env, limitType = 'public', customKey = null) {
  // 1. Determinar llave única
  const ip = request.headers.get('CF-Connecting-IP') || '127.0.0.1';
  const key = customKey || (limitType === 'public' ? ip : request.headers.get('Authorization') || ip);
  
  // 2. Determinar límite
  const limit = limitType === 'public' ? 10 : 100;
  const windowSeconds = 60;

  // 3. Invocar Binding del Rate Limiter (Asumimos uso de servicio interno o Upstash/DO)
  // [Aquí se abstrae la lógica del proveedor real. Ejemplo genérico asumiendo Upstash Redis]
  const isAllowed = await env.RATE_LIMITER_SERVICE.check(key, limit, windowSeconds);

  if (!isAllowed) {
    return fail("RATE_LIMIT_EXCEEDED", "Demasiadas peticiones. Intenta de nuevo en un minuto.", 429);
  }

  return null; // Pasó el límite
}
```

### 2. Uso en el Router

```javascript
// src/index.js
import { rateLimit } from './middleware/rateLimit.js';
import { handlePublicProposal } from './handlers/public.js';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith('/api/public/proposals/')) {
      // REGLA: Todo endpoint público DEBE tener rate limiting
      const rateLimitResponse = await rateLimit(request, env, 'public');
      if (rateLimitResponse) return rateLimitResponse;

      return handlePublicProposal(request, env);
    }
  }
}
```

## Reglas Inquebrantables

1. **[REQUIRED] Rechazo por defecto (429):** La respuesta DEBE usar el HTTP Status 429 (Too Many Requests) y el código de error en el body DEBE ser `RATE_LIMIT_EXCEEDED` exactamente. El Frontend depende de esta cadena para mostrar los mensajes correctos.
2. **[REQUIRED] CF-Connecting-IP:** Para endpoints públicos, la identificación unívoca del atacante viene en el header `CF-Connecting-IP`. Usar otro header como `X-Forwarded-For` puede ser vulnerado (spoofing), mientras que `CF-Connecting-IP` está garantizado y sellado por Cloudflare en el Edge.
