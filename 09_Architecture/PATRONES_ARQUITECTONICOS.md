---
title: "Patrones Arquitectónicos"
category: 09_Architecture
doc_type: estandar
tags: [patterns, cloudflare, edge, jamstack, realtime, websockets, durable-objects, polling]
summary: "Arquitectura general de los proyectos sobre edge y Jamstack, y cuándo aplicar patrones específicos: event-driven con colas, coordinación de estado con Durable Objects, WebSockets como reemplazo obligatorio del polling, y capas de caché."
keywords: [patterns, cloudflare, edge, jamstack, arquitectonicos, arquitectura, general, proyectos, aplicar, especificos, event-driven, colas, coordinacion, estado, polling, websocket, realtime, pub-sub]
updated: 2026-09-14
status: current
---

# Patrones Arquitectónicos

Este documento define la arquitectura general de nuestros proyectos y en qué casos usar patrones específicos. Nuestro stack base se apoya fuertemente en el **Edge Computing** (Cloudflare) y bases de datos gestionadas (Supabase).

## 1. Arquitectura Base (The Edge-Jamstack)

La arquitectura estándar para cualquier nuevo producto es:
- **Frontend**: SPA / SSG (React) hosteado globalmente en Cloudflare Pages.
- **Backend / API**: Funciones *Serverless/Edge* en Cloudflare Workers.
- **Data Layer**: Supabase (Postgres) consumido desde los Workers o directamente con RLS (Row Level Security).

### ¿Cuándo usar este patrón?
Es la opción **por defecto** (`[REQUIRED]` como punto de partida). Escala automáticamente, reduce latencia (Edge) y mantiene la base de código simple y serverless.

## 2. Event-Driven (Colas y Asincronía)

**[REQUIRED]** Cuando una solicitud HTTP al Worker tarda más de 500ms o requiere procesamiento pesado (ej. enviar 100 emails, procesar imágenes, integraciones con IA de largo tiempo), **NO** se debe bloquear la respuesta HTTP.

### Implementación con Cloudflare Queues
1. El Worker recibe el Request.
2. Valida datos y encola un mensaje (`await env.MY_QUEUE.send(data)`).
3. Responde HTTP 202 Accepted.
4. Un Consumer Worker procesa la cola de fondo.

## 3. Estado Consistente y Coordinación (Durable Objects)

**[RECOMMENDED]** Cuando se requiere coordinación estricta en tiempo real o mantener estado en memoria entre múltiples conexiones (ej. WebSockets, juegos multiplayer, contadores exactos, lock distribuido).
*No usar como base de datos primaria, siempre volcar estado final a Postgres/D1.*

### 3.1 Nunca hagas polling contra la base de datos — [REQUIRED]

**Regla:** si un cliente necesita enterarse de un cambio (estado de un pedido, ubicación en vivo, una lista que puede tener algo nuevo), la solución por defecto es un **evento empujado por WebSocket a través de un Durable Object**, no un `setInterval` haciendo `GET`/`PATCH` cada N segundos. Cada dato que cambia de verdad ya nace como un evento en algún handler del backend (se creó un pedido, se aceptó, cambió de estado, se movió el conductor) — ese es el punto exacto donde hay que **publicar**, no un punto donde el cliente tiene que **preguntar**.

**Por qué es una regla, no una preferencia de estilo:** el polling multiplica el costo por el número de clientes conectados y por la frecuencia del intervalo, sin importar si hubo o no un cambio real — en un plan gratuito de D1/Postgres esto agota la cuota de lecturas/escrituras mucho antes de tener tráfico real. Un WebSocket cuesta una conexión abierta (barata, con Hibernation API en Durable Objects ni siquiera consume tiempo de cómputo mientras está inactiva) y transmite exactamente los eventos que ocurren, ni uno más.

**Patrón de referencia — "canal" genérico de pub/sub sobre un Durable Object:**

```ts
// Un solo Durable Object, reutilizable para cualquier "canal" (un pedido, el feed
// de un usuario, una sala): el nombre del canal ES el id de la instancia
// (`namespace.idFromName(canal)`), así que no hace falta una clase por caso de uso.
export class RealtimeChannelDO {
  constructor(private readonly state: DurableObjectState) {}

  async fetch(request: Request): Promise<Response> {
    if (request.headers.get('Upgrade') === 'websocket') {
      const pair = new WebSocketPair();
      this.state.acceptWebSocket(pair[1]); // Hibernation API: sin cómputo mientras está idle.
      return new Response(null, { status: 101, webSocket: pair[0] });
    }
    if (request.method === 'POST') {
      const body = await request.text();
      for (const ws of this.state.getWebSockets()) ws.send(body);
      return new Response(null, { status: 204 });
    }
    return new Response('Not found', { status: 404 });
  }

  // Relay directo entre participantes del mismo canal (ej. conductor → cliente).
  webSocketMessage(sender: WebSocket, message: string) {
    for (const ws of this.state.getWebSockets()) if (ws !== sender) ws.send(message);
  }
}
```

- **Publicar desde un handler REST ya existente** (ej. al aceptar un pedido): el Worker hace un `stub.fetch('https://x/publish', { method: 'POST', body: JSON.stringify(evento) })` contra `namespace.get(namespace.idFromName('pedido:' + id))` — el mismo patrón que ya usa `checkRateLimit` para hablarle a `RateLimiterDO`, solo que en vez de contar, reparte.
- **Suscribirse desde el cliente**: una sola conexión WebSocket abierta mientras la pantalla esté activa, no un temporizador. La primera carga de datos sigue siendo un `fetch` normal (una vez, no un intervalo) — el WebSocket solo reemplaza las lecturas *repetidas* para detectar cambios.
- **Ubicación en vivo** (ej. un conductor en camino): el conductor manda su posición por el mismo WebSocket en vez de un `PATCH` cada pocos segundos — la posición nunca toca la base de datos en cada tick, solo se retransmite en memoria a quien esté escuchando. Si además hace falta la última posición conocida para una consulta SQL (ej. "conductores disponibles en este radio"), esa sí se guarda en la base, pero en su propio ciclo, deliberadamente más espaciado (decenas de segundos, no cada tick) — son dos necesidades distintas (tiempo real para un observador vs. frescura suficiente para un query) y no comparten la misma cadencia de escritura.

**Cuándo el polling SÍ es aceptable (la excepción, no la regla):** un caso puntual y explícitamente justificado — por ejemplo, revisar el estado de un proceso externo de terceros que no tiene webhooks (una build de CI, un procesamiento de pago asíncrono sin callback) y donde no existe ningún evento propio que publicar. Incluso ahí, preferir el intervalo más largo que la experiencia tolere, nunca "cada pocos segundos por si acaso".

## 4. Patrones de Caché

- **Nivel 1 (CDN)**: Archivos estáticos en Cloudflare Pages, con TTL largo y validación in-band.
- **Nivel 2 (Edge Cache)**: Respuestas API guardadas en la Cache API (`caches.default`) de Workers.
- **Nivel 3 (KV Cache)**: Datos de base de datos de lectura frecuente y mutación lenta, almacenados en Cloudflare KV para evitar latencia hacia Supabase.

---

> **Nota Anti-Patrones**: 
> - **NO** construyas monolitos tradicionales (ej. Express en EC2 o Heroku) sin un ADR justificado que explique por qué el Edge es insuficiente.
> - **NO** leas de la base de datos dentro de un bucle `for` en los Workers; la latencia de red arruinará el tiempo de ejecución.
