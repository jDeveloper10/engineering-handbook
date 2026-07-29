---
title: "IA y Machine Learning en Producción"
category: 13_AI_Rules
tags: [ai, ml, rag, embeddings, pgvector, gateway, streaming, sse, kv-cache]
summary: "Estándar para producción de funciones con IA/ML: arquitectura RAG con pgvector, AI Gateway con rate-limiting y métricas, streaming con SSE, caché KV para prompts y sanitización de PII."
keywords: [ai, ml, rag, pgvector, ai-gateway, cloudflare, sse, streaming, prompt, caching]
updated: 2026-07-27
status: current
---

# 🤖 IA Y MACHINE LEARNING EN PRODUCCIÓN

## 🎯 OBJETIVO
Definir los estándares para construir e integrar capacidades de Inteligencia Artificial (LLMs, Embeddings, RAG, Streaming) de forma eficiente, económica, segura y escalable en el Edge.

---

## 🎯 REGLAS INQUEBRANTABLES

**AI-001: NUNCA enviar PII ni datos sensibles del usuario a modelos externos sin anonimización.** Emails, nombres, números de tarjeta o claves deben ser filtrados antes de ser incluidos en un prompt.

**AI-002: Respuestas con IA SIEMPRE transmitidas por Streaming (Server-Sent Events - SSE).** Ningún usuario debe esperar 10 segundos ante una pantalla en blanco mientras un LLM genera una respuesta completa.

**AI-003: Caché agresiva de respuestas en Workers KV.** Si una consulta idéntica ya fue respondida recientemente, servir desde KV sin invocar la API del modelo.

---

## 🧠 1. ARQUITECTURA RAG (RETRIEVAL AUGMENTED GENERATION)

```
Petición del Usuario ──→ 1. Genera Embedding (OpenAI) ──→ 2. Busca en pgvector (Supabase)
                                                                 │
Respuesta Stream ◄── 4. Prompt a LLM con contexto ◄── 3. Recupera Top-K Fragmentos
```

```typescript
// apps/docs-worker/src/rag.ts
export async function handleRAGQuery(request: Request, env: Env): Promise<Response> {
  const { query, teamId } = await request.json()

  // 1. Anonimizar PII antes de procesar (AI-001)
  const sanitizedQuery = query.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL_REDACTED]')

  // 2. Intentar lectura de Caché KV (AI-003)
  const cacheKey = `rag:${teamId}:${sanitizedQuery}`
  const cachedResponse = await env.KV.get(cacheKey)
  if (cachedResponse) {
    return new Response(cachedResponse, { headers: { 'Content-Type': 'text/plain' } })
  }

  // 3. Generar embedding y buscar fragmentos en pgvector
  const { data: documents } = await supabase.rpc('search_documents_semantic', {
    query_embedding: await generateEmbedding(sanitizedQuery, env),
    p_team_id: teamId,
    match_threshold: 0.75,
    match_count: 3
  })

  const contextText = documents?.map(d => d.content).join('\n---\n') || ''

  // 4. Invocar LLM con streaming (SSE)
  return streamLLMResponse(sanitizedQuery, contextText, env)
}
```

---

## 🌊 2. STREAMING DE RESPUESTAS CON SERVER-SENT EVENTS (SSE)

```typescript
// Transmisión de tokens en tiempo real desde Cloudflare Worker al Cliente
export function streamLLMResponse(prompt: string, context: string, env: Env): Response {
  const { readable, writable } = new TransformStream()
  const writer = writable.getWriter()
  const encoder = new TextEncoder()

  // Ejecución en segundo plano sin bloquear el inicio de la respuesta
  ;(async () => {
    const aiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        stream: true,
        messages: [
          { role: 'system', content: `Responde basándote en el contexto:\n${context}` },
          { role: 'user', content: prompt }
        ]
      })
    })

    const reader = aiResponse.body?.getReader()
    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      await writer.write(value)
    }

    await writer.close()
  })()

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  })
}
```

---

## 📋 CHECKLIST DE IA EN PRODUCCIÓN

- [ ] Anonimización de PII implementada antes de enviar datos a LLMs.
- [ ] Streaming Server-Sent Events (SSE) configurado para respuestas de generación.
- [ ] Búsqueda semántica con pgvector y umbral >= 0.75.
- [ ] Caché KV activa para prompts y consultas frecuentes.
- [ ] Cuotas de Rate Limiting por usuario para prevenir abuso de costos de API.
