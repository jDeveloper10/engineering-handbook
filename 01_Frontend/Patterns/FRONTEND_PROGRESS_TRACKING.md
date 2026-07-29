---
title: "Patrón Progress Tracking"
category: 01_Frontend
tags: [react, ux, background-jobs, sse, websockets, polling]
status: current
---

# ⏳ PATRÓN PROGRESS TRACKING (Jobs Largos)

## 🎯 ¿Qué es y cuándo usarlo?
Cualquier acción que tarde más de 5 segundos no puede depender de un simple spinner. Si el usuario procesa un CSV de 10,000 filas o genera un reporte en PDF, necesita feedback del progreso real para saber que la app no colapsó.

> **REGLA INQUEBRANTABLE:** Si un Job en el backend (Worker/Queue) tarda > 5s, DEBE tener seguimiento de progreso. PROHIBIDO dejar al usuario con una pantalla en blanco o spinner infinito sin ETA.

---

## 🚦 3 ESTRATEGIAS DE TRACKING (Cuándo usar cuál)

### 1. WebSockets / Supabase Realtime (Recomendado)
- **Cuándo:** La base de datos es Postgres (Supabase) y ya tenemos conexión persistente.
- **Cómo:** El backend inserta/actualiza filas en la tabla `jobs_status`. El frontend se suscribe a los cambios de su `job_id`.

### 2. Server-Sent Events (SSE) (Ideal para Edge/Workers)
- **Cuándo:** No hay base de datos realtime, pero el flujo es unidireccional (Server → Client).
- **Cómo:** Cloudflare Worker devuelve un `TransformStream` que va arrojando chunks de texto `data: 50%\n\n`. El frontend usa `EventSource`.

### 3. Polling con React Query (El Fallback Universal)
- **Cuándo:** No soportamos streams o conexiones persistentes, y la arquitectura es estrictamente REST API (Lambda/Workers básicos).
- **Cómo:** Hacemos fetch al endpoint `/jobs/123/status` cada 2 segundos.

---

## 💻 CÓDIGO: POLLING CON REACT QUERY (Estrategia 3)

La solución más robusta y fácil de implementar si tu Worker envía el progreso a una DB o KV.

```tsx
import { useQuery } from '@tanstack/react-query'

function useJobProgress(jobId: string) {
  return useQuery({
    queryKey: ['job-status', jobId],
    queryFn: async () => {
      const res = await fetch(`/api/jobs/${jobId}/status`)
      return res.json() as Promise<{
        status: 'pending' | 'processing' | 'completed' | 'failed',
        progress: number, // 0 to 100
        message: string,
        etaSeconds: number
      }>
    },
    // POLLING: Refetch cada 2s SOLO si el job sigue en proceso
    refetchInterval: (query) => {
      const state = query.state.data?.status
      return (state === 'pending' || state === 'processing') ? 2000 : false
    },
    enabled: !!jobId // Solo correr si hay ID
  })
}
```

---

## 💻 CÓDIGO: SERVER-SENT EVENTS (Estrategia 2)

**Backend (Cloudflare Worker - Stream Response):**
```typescript
app.get('/api/jobs/:id/stream', (c) => {
  const { readable, writable } = new TransformStream()
  const writer = writable.getWriter()
  const encoder = new TextEncoder()

  // Proceso largo en background
  c.executionCtx.waitUntil((async () => {
    for (let i = 1; i <= 10; i++) {
      await sleep(1000)
      writer.write(encoder.encode(`data: {"progress": ${i * 10}, "msg": "Fila ${i*1000}"}\n\n`))
    }
    writer.write(encoder.encode(`data: {"status": "completed"}\n\n`))
    writer.close()
  })())

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
})
```

**Frontend (React Hook SSE):**
```tsx
function useSSEProgress(jobId: string) {
  const [data, setData] = useState({ progress: 0, msg: 'Iniciando...', completed: false })

  useEffect(() => {
    if (!jobId) return
    const source = new EventSource(`/api/jobs/${jobId}/stream`)
    
    source.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      if (payload.status === 'completed') {
        setData(prev => ({ ...prev, progress: 100, msg: 'Completado!', completed: true }))
        source.close()
      } else {
        setData(prev => ({ ...prev, ...payload }))
      }
    }
    
    return () => source.close()
  }, [jobId])

  return data
}
```

---

## 🎨 UI: COMPONENTE PROGRESS BAR ANIMADO

Componente reutilizable, semántico e informativo.

```tsx
import { X, CheckCircle, AlertTriangle } from 'lucide-react'

export function JobProgressBar({ 
  progress, 
  message, 
  etaSeconds, 
  status, // 'processing' | 'completed' | 'failed'
  onCancel 
}) {
  const isFinished = status === 'completed'
  const isFailed = status === 'failed'

  return (
    <div className="w-full max-w-md p-4 bg-white border rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
          {isFinished && <CheckCircle className="w-4 h-4 text-green-500" />}
          {isFailed && <AlertTriangle className="w-4 h-4 text-red-500" />}
          {message}
        </span>
        <span className="text-sm font-bold text-gray-900">{progress}%</span>
      </div>
      
      {/* Barra Track */}
      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
        {/* Fill (Animado) */}
        <div 
          className={`h-full transition-all duration-500 ease-out ${
            isFinished ? 'bg-green-500' : isFailed ? 'bg-red-500' : 'bg-blue-600'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <div className="flex justify-between items-center mt-3 text-xs text-gray-500">
        {/* Estimación de tiempo */}
        <span>
          {!isFinished && !isFailed && etaSeconds > 0 
            ? `~${etaSeconds} segundos restantes` 
            : ''}
        </span>
        
        {/* Cancelar Job en vuelo */}
        {!isFinished && !isFailed && onCancel && (
          <button 
            onClick={onCancel}
            className="flex items-center text-red-600 hover:text-red-700"
          >
            <X className="w-3 h-3 mr-1" /> Cancelar
          </button>
        )}
      </div>
    </div>
  )
}
```
