---
title: "Optimización Workers"
category: 02_Backend
tags: [cloudflare, workers, optimización, edge]
summary: "Reglas O-032 a O-035 de optimización avanzada de Cloudflare Workers: eliminar cold starts, no saturar los 128MB de memoria, perfilado de CPU y procesamiento con Web Streams."
keywords: [cloudflare, workers, optimizacion, edge, o-032, o-035, avanzada, eliminar, cold, starts, saturar, 128mb, memoria, perfilado]
updated: 2026-07-29
status: current
---

# ⚡ OPTIMIZACIÓN AVANZADA DE WORKERS (Cloudflare)

## O-032: Eliminar Cold Starts

```typescript
// ❌ Cold start: primer request después de inactividad = 200-400ms
// Usuario recibe latencia alta en horas de poco tráfico

// ✅ Solución 1: CRON cada 5 minutos (mantiene el worker warm)
// wrangler.toml
[triggers]
crons = ["*/5 * * * *"]

// src/index.ts
export default {
  async scheduled(event: ScheduledEvent, env: Env) {
    // Auto-ping: mantener warm
    if (event.cron === "*/5 * * * *") {
      await fetch('https://api.omnisuite.com/health')
    }
  },
  
  async fetch(request: Request, env: Env) {
    // Worker normal
  }
}

// ✅ Solución 2: Múltiples workers para distribuir tráfico
// Si tienes 10 workers, el tráfico los mantiene warm naturalmente
```

## O-033: Memory Management (No saturar los 128MB)

```typescript
// ❌ Memory leak: datos globales que nunca se limpian
const cache = new Map()  // Esto crece indefinidamente

export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url)
    
    // Esto NUNCA se limpia
    cache.set(url.pathname, await fetchData(url))
    
    return Response.json(cache.get(url.pathname))
  }
}

// ✅ Cache con límite y TTL
class LRUCache<T> {
  private cache = new Map<string, T>()
  private maxSize: number
  
  constructor(maxSize = 100) {
    this.maxSize = maxSize
  }
  
  get(key: string) {
    const value = this.cache.get(key)
    if (value) {
      // Mover al final (más reciente)
      this.cache.delete(key)
      this.cache.set(key, value)
    }
    return value
  }
  
  set(key: string, value: T, ttlMs = 60000) {
    if (this.cache.size >= this.maxSize) {
      // Eliminar el más antiguo
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }
    
    this.cache.set(key, value)
    
    // Auto-eliminar después de TTL
    setTimeout(() => this.cache.delete(key), ttlMs)
  }
}

const cache = new LRUCache<unknown>(50)  // Máximo 50 entradas
```

## O-034: CPU Profiling (Encontrar cuellos de botella)

```typescript
// ❌ Sin profiling: no sabes qué es lento
async function handleRequest(request: Request, env: Env) {
  const data = await request.json()
  const user = await authenticate(data.token)
  const orders = await db.getOrders(user.id)
  const enriched = await enrichOrders(orders)
  return Response.json(enriched)
}

// ✅ Profiling manual (en desarrollo)
async function profile<T>(name: string, fn: () => Promise<T>): Promise<T> {
  const start = performance.now()
  const result = await fn()
  const duration = performance.now() - start
  
  console.log(JSON.stringify({
    operation: name,
    duration_ms: Math.round(duration),
    timestamp: new Date().toISOString()
  }))
  
  return result
}

async function handleRequest(request: Request, env: Env) {
  const data = await profile('parse_json', () => request.json())
  const user = await profile('authenticate', () => authenticate(data.token))
  const orders = await profile('db_query', () => db.getOrders(user.id))
  const enriched = await profile('enrich', () => enrichOrders(orders))
  return Response.json(enriched)
}

// Output:
// {"operation":"parse_json","duration_ms":2}
// {"operation":"authenticate","duration_ms":15}
// {"operation":"db_query","duration_ms":245}  ← CUELLO DE BOTELLA
// {"operation":"enrich","duration_ms":8}
```

## O-035: Web Streams (Procesar datos sin cargar en memoria)

```typescript
// ❌ Cargar archivo completo en memoria
async function processCSV(request: Request, env: Env) {
  const text = await request.text()  // 50MB en memoria = CRASH
  const lines = text.split('\n')
  
  for (const line of lines) {
    const [name, email] = line.split(',')
    await db.insert('users', { name, email })
  }
}

// ✅ Streaming: procesar línea por línea
async function processCSV(request: Request, env: Env) {
  const reader = request.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    
    // Procesar todas las líneas completas
    buffer = lines.pop() || ''  // Última línea (incompleta) se guarda
    
    for (const line of lines) {
      const [name, email] = line.split(',')
      await db.insert('users', { name, email })
    }
  }
}

// ✅ TransformStream: procesar y devolver streaming
async function transformCSVtoJSON(request: Request, env: Env) {
  const { readable, writable } = new TransformStream()
  const writer = writable.getWriter()
  
  const reader = request.body!.getReader()
  const decoder = new TextDecoder()
  const encoder = new TextEncoder()
  
  // Primer objeto JSON
  writer.write(encoder.encode('['))
  
  let first = true
  let buffer = ''
  
  const processStream = async () => {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        const [name, email] = line.split(',')
        const json = JSON.stringify({ name, email })
        
        if (!first) writer.write(encoder.encode(','))
        else first = false
        
        writer.write(encoder.encode(json))
      }
    }
    
    writer.write(encoder.encode(']'))
    writer.close()
  }
  
  processStream()
  
  return new Response(readable, {
    headers: { 'Content-Type': 'application/json' }
  })
}
```

## O-036: Service Bindings vs HTTP (Comunicación interna eficiente)

```typescript
// ❌ HTTP entre servicios (sale a internet y vuelve)
// Latencia: 50-100ms
const response = await fetch('https://auth.omnisuite.com/verify', {
  headers: { 'Authorization': token }
})

// ✅ Service Binding (comunicación interna, sin salir a internet)
// Latencia: < 1ms
// wrangler.toml
[[services]]
binding = "AUTH_SERVICE"
service = "auth-service"

// Uso:
const response = await env.AUTH_SERVICE.fetch(
  new Request('https://internal/verify', {
    headers: { 'Authorization': token }
  })
)

// ✅ Durable Objects para estado compartido (sin DB)
export class SessionStore {
  private sessions: Map<string, Session> = new Map()
  
  async getSession(sessionId: string): Promise<Session | null> {
    return this.sessions.get(sessionId) || null
  }
  
  async setSession(sessionId: string, session: Session): Promise<void> {
    this.sessions.set(sessionId, session)
  }
}
```

## O-037: Análisis de Bundle Size

```bash
# ❌ Bundle gigante (> 1MB) = Cold start más lento

# ✅ Analizar bundle con wrangler
npx wrangler deploy --dry-run --outdir dist/

# Ver tamaño de cada archivo
npx wrangler deploy --dry-run --outdir dist/ | grep -E "\.js|\.wasm"

# Si un archivo > 100KB, considerar:
# 1. Tree-shaking (importar solo lo necesario)
# 2. Code splitting (dividir en módulos)
# 3. Dependencies externas (usar CDN para librerías grandes)
```

```typescript
// ❌ Importar toda la librería
import _ from 'lodash'  // 70KB
const result = _.groupBy(users, 'status')

// ✅ Importar solo la función necesaria
import groupBy from 'lodash/groupBy'  // 2KB
const result = groupBy(users, 'status')

// ❌ Importar todo moment
import moment from 'moment'  // 230KB

// ✅ Usar date-fns (tree-shakeable, más pequeño)
import { format, addDays } from 'date-fns'  // 3KB
```
