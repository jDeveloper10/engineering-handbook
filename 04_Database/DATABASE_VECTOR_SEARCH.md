---
title: "Búsqueda Vectorial y Semántica (pgvector)"
category: 04_Database
tags: [pgvector, embeddings, búsqueda-semántica, openai, postgres]
summary: "Búsqueda semántica con pgvector: configuración de la base, generación y guardado de embeddings desde un Worker, endpoint que combina full-text y semántica, y búsqueda difusa."
keywords: [pgvector, embeddings, busqueda-semantica, openai, postgres, busqueda, vectorial, semantica, configuracion, base, generacion, guardado, worker, endpoint]
updated: 2026-07-29
status: current
---

# 🔍 BÚSQUEDA VECTORIAL Y SEMÁNTICA (pgvector)

## 🎯 ¿Qué es y cuándo usarlo?
La **búsqueda por texto completo** (FTS con pg_trgm / GIN) resuelve búsquedas exactas y por trigrams. La **búsqueda semántica** resuelve búsquedas por *significado* — si un usuario busca "cómo hacer deploy" encontrará documentos que hablan de "despliegue a producción" aunque no contengan la palabra exacta.

La búsqueda semántica usa **embeddings**: vectores numéricos de alta dimensión que representan el significado del texto. `pgvector` es la extensión de Postgres que almacena y consulta esos vectores con operaciones de similitud coseno.

> **REGLA INQUEBRANTABLE:** La búsqueda semántica es un **complemento**, no un reemplazo de FTS. El flujo correcto es: primero FTS (rápido, sin costo) → luego semántica solo si FTS devuelve < 3 resultados o el usuario activa explícitamente "búsqueda inteligente". PROHIBIDO llamar a la API de embeddings en cada request sin gestión de caché.

---

## ⚙️ 1. CONFIGURACIÓN DE LA BASE DE DATOS

```sql
-- Habilitar la extensión pgvector (Supabase la tiene disponible)
CREATE EXTENSION IF NOT EXISTS vector;

-- Añadir columna de embedding a la tabla documents
-- text-embedding-3-small de OpenAI produce vectores de 1536 dimensiones
ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Índice HNSW para búsqueda aproximada ultra-rápida (mejor que IVFFlat para < 1M filas)
-- El índice se crea sobre la columna de embedding usando distancia coseno
CREATE INDEX idx_documents_embedding
  ON documents
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- FUNCIÓN SQL para búsqueda semántica (invocable desde el Worker)
CREATE OR REPLACE FUNCTION search_documents_semantic(
  query_embedding vector(1536),
  p_team_id       UUID,
  match_threshold FLOAT DEFAULT 0.75,
  match_count     INT   DEFAULT 10
)
RETURNS TABLE (
  id          UUID,
  title       TEXT,
  status      doc_status,
  similarity  FLOAT
)
LANGUAGE sql STABLE AS $$
  SELECT
    d.id,
    d.title,
    d.status,
    1 - (d.embedding <=> query_embedding) AS similarity   -- distancia coseno → similitud
  FROM documents d
  WHERE
    d.team_id   = p_team_id
    AND d.deleted_at IS NULL
    AND d.embedding IS NOT NULL
    AND 1 - (d.embedding <=> query_embedding) > match_threshold
  ORDER BY d.embedding <=> query_embedding   -- menor distancia = más similar
  LIMIT match_count;
$$;
```

---

## 💻 2. WORKER: GENERACIÓN Y GUARDADO DE EMBEDDINGS

Los embeddings se generan cuando se crea o actualiza un documento. Para no bloquear el request del usuario, se encolan en un **Cloudflare Queue**.

### 2.1 Encolado del Job de Embedding

```typescript
// En el handler de crear/actualizar documento
export async function handleUpdateDocument(request: Request, env: Env) {
  const body = await request.json()
  const { id, title, content } = updateDocumentSchema.parse(body)

  // 1. Guardar el documento normalmente (sin esperar el embedding)
  const { data: doc, error } = await supabase
    .from('documents')
    .update({ title, content, updated_at: new Date().toISOString() })
    .eq('id', id)
    .select('id, title, content')
    .single()

  if (error) throw error

  // 2. Encolar el job de embedding (asíncrono, no bloquea el response)
  // Ref: CLOUDFLARE_PLATFORM_STANDARD.md — Queues para trabajo asíncrono
  await env.EMBEDDINGS_QUEUE.send({
    documentId: doc.id,
    text: `${doc.title}\n\n${doc.content}`  // Título + contenido para el embedding
  })

  return ok(doc)
}
```

### 2.2 Worker Consumidor del Queue

```typescript
// Worker independiente: embeddings-worker
export default {
  async queue(batch: MessageBatch<{ documentId: string; text: string }>, env: Env) {
    for (const message of batch.messages) {
      try {
        await generateAndSaveEmbedding(message.body, env)
        message.ack()
      } catch (error) {
        console.error(`[EMBEDDING] Error for ${message.body.documentId}:`, error)
        message.retry()   // Reintento automático (Queue lo gestiona)
      }
    }
  }
}

async function generateAndSaveEmbedding(
  { documentId, text }: { documentId: string; text: string },
  env: Env
) {
  // 1. Truncar texto a máximo 8191 tokens (límite de text-embedding-3-small)
  const truncatedText = text.slice(0, 30000)

  // 2. Llamar a la API de OpenAI
  // Ref: CIRCUIT_BREAKER_PATTERN.md + RETRY_PATTERN.md para llamadas externas
  const response = await fetchWithRetry('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: truncatedText
    }),
    maxRetries: 3
  })

  if (!response.ok) throw new Error(`OpenAI error: ${response.status}`)

  const { data } = await response.json() as { data: [{ embedding: number[] }] }
  const embedding = data[0].embedding

  // 3. Guardar en Supabase (con service_role — DB §07: bypasea RLS)
  const { error } = await supabase
    .from('documents')
    .update({ embedding: `[${embedding.join(',')}]` })  // pgvector acepta formato string
    .eq('id', documentId)

  if (error) throw error
}
```

---

## 💻 3. ENDPOINT DE BÚSQUEDA (FTS + Semántica combinados)

```typescript
// GET /api/search?q=&team_id=&mode=smart
export async function handleSearch(request: Request, env: Env) {
  const url    = new URL(request.url)
  const q      = url.searchParams.get('q') ?? ''
  const teamId = url.searchParams.get('team_id') ?? ''
  const mode   = url.searchParams.get('mode') ?? 'text'   // 'text' | 'smart'

  if (q.length < 2) return ok({ results: [], mode: 'none' })

  // PASO 1: Siempre intentar FTS primero (rápido, gratis)
  const { data: textResults, error: ftsError } = await supabase
    .from('documents')
    .select('id, title, status, updated_at')
    .eq('team_id', teamId)
    .is('deleted_at', null)
    .textSearch('title || \' \' || content', q, {
      type: 'websearch',     // Soporta comillas, AND, OR, -exclusiones
      config: 'english'
    })
    .limit(10)

  if (ftsError) throw ftsError

  // PASO 2: Búsqueda semántica solo si el usuario la pide (mode=smart)
  // o si FTS devolvió menos de 3 resultados
  if (mode !== 'smart' && textResults.length >= 3) {
    return ok({ results: textResults, mode: 'text' })
  }

  // PASO 3: Generar embedding de la query y buscar por similitud
  // Solo si tenemos API Key de OpenAI configurada
  if (!env.OPENAI_API_KEY) {
    return ok({ results: textResults, mode: 'text' })
  }

  const embeddingResponse = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ model: 'text-embedding-3-small', input: q })
  })

  const { data: embData } = await embeddingResponse.json() as { data: { embedding: number[] }[] }
  const queryEmbedding = embData[0].embedding

  // PASO 4: Invocar la función SQL de búsqueda semántica
  const { data: semanticResults, error: semError } = await supabase
    .rpc('search_documents_semantic', {
      query_embedding: `[${queryEmbedding.join(',')}]`,
      p_team_id:       teamId,
      match_threshold: 0.70,
      match_count:     10
    })

  if (semError) {
    // Fallar gracefully: devolver solo los resultados de texto
    return ok({ results: textResults, mode: 'text', warning: 'semantic_unavailable' })
  }

  // PASO 5: Fusionar y deduplicar resultados (text + semantic)
  const textIds = new Set(textResults.map(r => r.id))
  const merged = [
    ...textResults.map(r => ({ ...r, source: 'text' })),
    ...semanticResults
      .filter(r => !textIds.has(r.id))  // Evitar duplicados
      .map(r => ({ ...r, source: 'semantic' }))
  ]

  return ok({ results: merged, mode: 'smart' })
}
```

---

## ⚙️ 4. BÚSQUEDA FUZZY CON pg_trgm

Para tolerancia a errores tipográficos (ej: "despliege" → "despliegue"):

```sql
-- El índice GIN con pg_trgm ya está en la migración base (DATABASE_ENGINEERING_STANDARD.md §06)
-- Solo necesitamos la query correcta desde el Worker:

-- Umbral de similitud trigram (0.3 = tolera errores moderados)
SET pg_trgm.similarity_threshold = 0.3;

SELECT id, title, similarity(title, 'despliege') AS sim
FROM documents
WHERE title % 'despliege'   -- Operador de similitud trigram
ORDER BY sim DESC
LIMIT 10;
```

```typescript
// En el Worker: fuzzy search como fallback si FTS no da resultados
const { data: fuzzyResults } = await supabase
  .rpc('search_documents_fuzzy', {
    query_text: q,
    p_team_id:  teamId,
    similarity_threshold: 0.3
  })
```

```sql
-- Función SQL para fuzzy search
CREATE OR REPLACE FUNCTION search_documents_fuzzy(
  query_text           TEXT,
  p_team_id            UUID,
  similarity_threshold FLOAT DEFAULT 0.3
)
RETURNS TABLE (id UUID, title TEXT, similarity FLOAT)
LANGUAGE sql STABLE AS $$
  SELECT id, title, similarity(title, query_text)
  FROM documents
  WHERE team_id = p_team_id
    AND deleted_at IS NULL
    AND title % query_text
  ORDER BY similarity(title, query_text) DESC
  LIMIT 10;
$$;
```

---

## 💰 GESTIÓN DE COSTOS

| Operación | Costo (text-embedding-3-small) | Estrategia |
|-----------|-------------------------------|------------|
| Generar embedding de documento | ~$0.00002 por 1000 tokens | Solo al crear/actualizar |
| Búsqueda semántica de query | ~$0.00002 por búsqueda | Solo en `mode=smart` o FTS < 3 resultados |
| Re-indexar todos los docs | $0.02 por 1M tokens | Job batch nocturno |

> Si el costo de embeddings es una preocupación, usar el modelo **`text-embedding-3-small`** (más barato que `ada-002`) o cachear los embeddings de queries frecuentes en Workers KV con TTL de 1 hora.
