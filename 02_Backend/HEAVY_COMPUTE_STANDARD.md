---
title: "Estándar de Cómputo Pesado"
category: 02_Backend
tags: [backend, workers, containers, performance]
summary: "Reglas HC-001 a HC-004 para trabajo que excede el límite de CPU de un Worker: Workers para lógica ligera, Containers para cómputo pesado, con árbol de decisión rápida."
keywords: [cpu, limite, workers, containers, computo-pesado, colas]
updated: 2026-07-27
status: current
---

# Estándar de Cómputo Pesado (HC-001 a HC-004)

## 🎯 Problema
Cloudflare Workers tienen límite de CPU de 30 segundos. Algoritmos como:
- Machine Learning (predicciones, clasificaciones)
- Optimización de rutas (TSP, VRP)
- Procesamiento de video/imágenes pesado
- Reportes masivos (millones de registros)
...exceden este límite.

## 🏗️ Solución: Workers para lógica ligera + Containers para cómputo pesado

---

## ⚡ REGLAS INQUEBRANTABLES

### HC-001: TODO CÓMPUTO > 15s DEBE IR A CONTAINER

**Regla de decisión:**
| Duración estimada | Dónde ejecutar | Tecnología |
|-------------------|----------------|------------|
| < 15s | Cloudflare Worker | TypeScript |
| 15s - 10min | Cloud Run / Fargate | Node.js, Python |
| 10min - 1hora | Batch Job (GCP/AWS) | Python, Go |
| > 1 hora | Kubernetes Job | Cualquiera |

---

### HC-002: PATRÓN COLA + WORKER → CONTAINER

```typescript
// 1. Worker recibe request y encola trabajo pesado
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { videoUrl } = await request.json()
    
    // Encolar trabajo
    const jobId = crypto.randomUUID()
    await env.QUEUE.send({
      id: jobId,
      type: 'process_video',
      payload: { videoUrl },
      status: 'queued'
    })
    
    // Responder inmediatamente
    return Response.json({ jobId, status: 'processing' })
  }
}
```

```python
# 2. Container en Cloud Run procesa el trabajo
import os
from google.cloud import tasks_v2

def process_video(job_id: str, video_url: str):
    # Descargar video
    video = download(video_url)
    
    # Procesar (puede tardar 10 minutos)
    processed = heavy_ml_processing(video)
    
    # Guardar resultado
    upload_to_r2(processed, f"processed/{job_id}.mp4")
    
    # Notificar completado
    requests.post(f"https://api.omnisuite.com/webhooks/jobs/{job_id}", json={
        "status": "completed",
        "result_url": f"https://cdn.omnisuite.com/processed/{job_id}.mp4"
    })
```

---

### HC-003: PROGRESS TRACKING PARA TRABAJOS LARGOS

```typescript
// Worker expone endpoint de status
export async function getJobStatus(jobId: string, env: Env): Promise<Response> {
  const job = await env.KV.get(`job:${jobId}`, 'json')
  
  return Response.json({
    id: job.id,
    status: job.status, // queued | processing | completed | failed
    progress: job.progress, // 0-100
    estimated_completion: job.eta,
    result_url: job.result_url
  })
}

// Frontend puede hacer polling o WebSocket
const { data: job } = useQuery({
  queryKey: ['job', jobId],
  queryFn: () => fetch(`/api/jobs/${jobId}`).then(r => r.json()),
  refetchInterval: job => job?.status === 'processing' ? 5000 : false
})
```

---

### HC-004: WORKER SPIN-UP PARA CÓMPUTO MEDIO

```typescript
// Para tareas de 15-30s: usar Worker con más memoria
// wrangler.toml
[env.production]
cpu_ms = 30000  # Máximo permitido
memory = "256MB" # Subir de 128MB default

// Si necesita más: evaluar migrar a Container
```

---

## 📊 DECISIÓN RÁPIDA

| Tarea | Tiempo | Solución |
|-------|--------|----------|
| Generar PDF propuesta | 2s | Worker (pdf-lib) |
| Procesar CSV 10K filas | 8s | Worker (streaming) |
| Optimizar rutas 50 puntos | 45s | Cloud Run |
| Entrenar modelo ML | 30min | Batch Job |
| Procesar video 4K | 10min | Cloud Run + GPU |
