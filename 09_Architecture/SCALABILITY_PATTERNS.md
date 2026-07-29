---
title: "Patrones Avanzados de Escalabilidad Horizontal y Resiliencia"
category: 09_Architecture
doc_type: patron
tags: [scalability, sharding, r2, multipart, load-shedding, graceful-degradation, queues]
summary: "Estándar para arquitectura de ultra-alta escalabilidad: sharding de D1, subida multipart en R2 para archivos > 100MB, descarte de carga (Load Shedding), degradación elegante y planificación de capacidad."
keywords: [scalability, sharding, d1, r2, multipart, load-shedding, graceful-degradation, capacity-planning]
updated: 2026-07-27
status: current
---

# ⚡ PATRONES AVANZADOS DE ESCALABILIDAD HORIZONTAL

## 🎯 OBJETIVO
Definir los patrones de diseño para absorber picos de tráfico extremos, distribuir el almacenamiento de forma masiva y garantizar que el sistema se degrade de forma elegante antes de colapsar.

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] SCALE-001: Degradación Elegante (Graceful Degradation) bajo saturación.** Si el sistema detecta alta latencia, deshabilita funciones secundarias (búsqueda semántica, estadísticas) para preservar el flujo principal (lectura y pagos).

> **Por qué:** sin degradación elegante, un pico de tráfico que satura una función secundaria (búsqueda, recomendaciones) arrastra con ella a las funciones críticas por compartir los mismos recursos. Apagar lo secundario a tiempo es lo que mantiene vivo lo esencial.

**[REQUIRED] SCALE-002: Descarte de Carga (Load Shedding) en el Gateway.** Rechazar peticiones no críticas con HTTP 503 cuando la cola de peticiones supere los umbrales de seguridad.

> **Por qué:** sin descarte de carga, un sistema saturado sigue aceptando peticiones que no puede atender a tiempo, y la cola crece hasta que todo colapsa junto. Rechazar con 503 lo que ya no se puede servir a tiempo es lo que evita ese colapso total.

**[REQUIRED] SCALE-003: Subida Multipart en R2 para archivos > 100MB.** NUNCA cargar archivos grandes directamente en memoria del Worker.

> **Por qué:** la misma razón que `O-016`: cargar un archivo grande completo en memoria antes de subirlo hace que el consumo dependa del tamaño del archivo, y el límite de memoria del Worker es duro. La subida multipart mantiene el consumo constante sin importar cuán grande sea el archivo.

---

## 📦 1. SUBIDA MULTIPART A R2 (ARCHIVOS GRANDES)

```typescript
// Iniciar subida multipart para archivos pesados (hasta 5TB)
export async function handleMultipartUpload(request: Request, env: Env) {
  const { fileName, contentType } = await request.json()

  const upload = await env.MY_BUCKET.createMultipartUpload(fileName, {
    httpMetadata: { contentType }
  })

  return ok({
    uploadId: upload.uploadId,
    key: upload.key
  })
}
```

---

## 🛡️ 2. LOAD SHEDDING Y DEGRADACIÓN ELEGANTE

```typescript
// Middleware de protección contra sobrecarga en el API Gateway
export async function applyLoadShedding(request: Request, env: Env) {
  const currentLoad = await env.KV.get('system_health:load')

  if (currentLoad === 'CRITICAL') {
    const url = new URL(request.url)
    // Descartar tráfico no crítico (ej. recomendaciones, métricas)
    if (url.pathname.startsWith('/api/analytics') || url.pathname.startsWith('/api/recommendations')) {
      return new Response(JSON.stringify({
        success: false,
        error: { code: 'SERVICE_DEGRADED', message: 'Servicio operando en modo de capacidad reducida.' }
      }), { status: 503, headers: { 'Retry-After': '60' } })
    }
  }
}
```

---

## 📋 CHECKLIST DE ESCALABILIDAD

- [ ] Estrategia de sharding definida para cargas masivas en D1/Postgres.
- [ ] Subida multipart implementada para objetos R2 > 100MB.
- [ ] Middleware de Load Shedding activo en el API Gateway.
- [ ] Degradación elegante configurada para mantener activos los flujos de pago y lectura.
