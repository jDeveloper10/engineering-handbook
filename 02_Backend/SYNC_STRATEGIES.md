---
title: "Estrategias de Sincronización de Datos (Offline-First y Conflict Resolution)"
category: 02_Backend
doc_type: estandar
tags: [sync, offline-first, crdt, last-write-wins, indexeddb, react-query, workers]
summary: "Estándar para sincronización de datos bidireccional entre clientes y el servidor: cola offline con IndexedDB/Dexie, resolución de conflictos (LWW vs CRDTs), tracking de estados y hook useSync."
keywords: [sync, offline, bidireccional, crdt, last-write-wins, dexie, indexeddb, react-query, conflict-resolution, offline-queue]
updated: 2026-07-27
status: current
---

# ESTRATEGIAS DE SINCRONIZACIÓN DE DATOS (OFFLINE-FIRST)

## OBJETIVO
Garantizar la continuidad operativa de aplicaciones web, móviles y de escritorio sin conexión a internet, manteniendo la coherencia de datos y resolviendo conflictos de sincronización sin pérdida de información del usuario.

---

## REGLAS INQUEBRANTABLES

**[REQUIRED] SYNC-001: NUNCA perder datos del usuario por un conflicto de sincronización.** Si dos escrituras entran en conflicto y no se pueden fusionar automáticamente, el estado anterior DEBE preservarse en un borrador de conflicto.

> **Por qué:** en un flujo offline-first el usuario edita sin red y confía en que su trabajo se guardará; si un conflicto de sincronización se resuelve descartando una de las dos escrituras sin avisar, el usuario pierde trabajo sin enterarse hasta que ya es tarde para recuperarlo.

**[REQUIRED] SYNC-002: Todo registro offline DEBE incluir metadatos de sincronización:** `client_updated_at`, `server_updated_at`, `sync_status` (`pending`, `syncing`, `synced`, `conflict`, `failed`).

> **Por qué:** sin metadatos de sincronización no hay forma de saber qué escritura es más reciente, cuál ya se envió y cuál sigue pendiente — son los datos que la resolución de conflictos y el reintento necesitan para funcionar, no un adorno del esquema.

**[REQUIRED] SYNC-003: Sincronización Incremental por defecto.** NUNCA descargar el dataset completo; solicitar únicamente registros modificados después del último `last_synced_at`.

> **Por qué:** descargar el dataset completo en cada sincronización desperdicia ancho de banda y batería en proporción al tamaño total de los datos, no al tamaño de lo que realmente cambió — y en móvil esa diferencia se paga en datos del usuario.

---

## 1. MATRIZ DE ESTRATEGIAS DE RESOLUCIÓN DE CONFLICTOS

| Estrategia | Algoritmo | Caso de Uso | Complejidad |
|---|---|---|---|
| **Last Write Wins (LWW)** | Gana el timestamp más reciente | Datos simples (perfil, configuraciones) | 🟢 Baja |
| **CRDTs (State-based / Operation-based)** | Fusión matemática sin conflictos | Editores colaborativos, contadores, listas | 🟡 Media |
| **Manual User Resolution** | Presenta UI de conflicto al usuario | Formularios complejos, contratos, documentos | 🔴 Alta |

---

## 2. COLA OFFLINE EN EL CLIENTE (IndexedDB + Dexie.js)

```typescript
// src/lib/db.ts - Base de datos IndexedDB local para el cliente
import Dexie, { Table } from 'dexie'

export interface OfflineMutation {
  id?: number
  client_id: string
  action: 'CREATE' | 'UPDATE' | 'DELETE'
  entity: string
  payload: Record<string, unknown>
  status: 'pending' | 'syncing' | 'failed'
  created_at: number
}

class AppOfflineDatabase extends Dexie {
  mutations!: Table<OfflineMutation>

  constructor() {
    super('AppOfflineDatabase')
    this.version(1).stores({
      mutations: '++id, client_id, action, entity, status, created_at'
    })
  }
}

export const offlineDb = new AppOfflineDatabase()
```

---

## 3. HOOK EN REACT: `useSync` CON REACT QUERY Y DEXIE

```tsx
// src/hooks/useSync.ts
import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { offlineDb } from '@/lib/db'

export function useSync() {
  const queryClient = useQueryClient()
  const [isSyncing, setIsSyncing] = useState(false)
  const [pendingCount, setPendingCount] = useState(0)

  useEffect(() => {
    // Actualizar contador de mutaciones pendientes
    const interval = setInterval(async () => {
      const count = await offlineDb.mutations.where('status').equals('pending').count()
      setPendingCount(count)
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const triggerSync = async () => {
    if (isSyncing || !navigator.onLine) return
    setIsSyncing(true)

    try {
      const pendingMutations = await offlineDb.mutations
        .where('status')
        .equals('pending')
        .toArray()

      for (const mutation of pendingMutations) {
        // Marcar como en proceso
        await offlineDb.mutations.update(mutation.id!, { status: 'syncing' })

        try {
          const res = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mutation)
          })

          if (res.ok) {
            // Eliminar de la cola al confirmar sincronización
            await offlineDb.mutations.delete(mutation.id!)
          } else {
            await offlineDb.mutations.update(mutation.id!, { status: 'failed' })
          }
        } catch (err) {
          await offlineDb.mutations.update(mutation.id!, { status: 'pending' })
          break // Si se cae la red, pausar la sincronización
        }
      }

      // Invalidar caché de React Query para refrescar UI
      await queryClient.invalidateQueries()
    } finally {
      setIsSyncing(false)
    }
  }

  // Escuchar eventos de reconexión de red
  useEffect(() => {
    window.addEventListener('online', triggerSync)
    return () => window.removeEventListener('online', triggerSync)
  }, [])

  return { triggerSync, isSyncing, pendingCount }
}
```

---

## 4. WORKER HANDLER: SINCRONIZACIÓN INCREMENTAL

```typescript
// POST /api/sync
export async function handleSyncEndpoint(request: Request, env: Env) {
  const userId = request.headers.get('x-user-id')!
  const { client_id, action, entity, payload, client_updated_at } = await request.json()

  // 1. Obtener estado actual en el servidor
  const { data: serverRecord } = await supabase
    .from(entity)
    .select('id, updated_at')
    .eq('id', payload.id)
    .single()

  // 2. Conflict Resolution (Last Write Wins)
  if (serverRecord) {
    const serverTime = new Date(serverRecord.updated_at).getTime()
    const clientTime = new Date(client_updated_at).getTime()

    if (serverTime > clientTime) {
      // Conflicto: El servidor tiene una versión más reciente
      return fail('SYNC_CONFLICT', 'El registro en el servidor fue modificado recientemente.', 409)
    }
  }

  // 3. Aplicar mutación
  const { data, error } = await supabase
    .from(entity)
    .upsert({ ...payload, user_id: userId, updated_at: new Date().toISOString() })

  if (error) return fail('SYNC_ERROR', error.message, 500)

  return ok({ synced: true, data })
}
```

---

## CHECKLIST DE SINCRONIZACIÓN

- [ ] Registro local en IndexedDB con Dexie.js para mutaciones offline.
- [ ] Listener de reconexión `window.addEventListener('online', triggerSync)`.
- [ ] Indicador de estado visual en la UI (`pending`, `syncing`, `synced`, `conflict`).
- [ ] Resolución de conflictos LWW o modal de intervención manual ante HTTP 409.
- [ ] Invalidation de React Query tras sincronizar exitosamente.
