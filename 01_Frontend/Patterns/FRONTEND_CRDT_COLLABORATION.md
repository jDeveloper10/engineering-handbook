---
title: "Colaboración en Tiempo Real (CRDTs + Supabase)"
category: 01_Frontend
doc_type: estandar
tags: [yjs, crdt, realtime, collaboration, cursors, supabase]
summary: "Colaboración simultánea con CRDTs y Yjs: proveedor de sincronización sobre Supabase, integración con TipTap, cursores y avatares de colaboradores en vivo."
keywords: [yjs, crdt, realtime, collaboration, cursors, supabase, colaboracion, tiempo, real, crdts, simultanea, proveedor, sincronizacion, integracion]
updated: 2026-07-29
status: current
---

# 🤝 PATRÓN COLABORACIÓN EN TIEMPO REAL (CRDTs)

## 🎯 ¿Qué es y por qué importa?
Los **CRDTs (Conflict-free Replicated Data Types)** son estructuras de datos matemáticamente diseñadas para resolver ediciones concurrentes sin conflictos. Si dos usuarios editan la misma línea al mismo tiempo, un CRDT garantiza que ambos terminen con el mismo documento consistente, sin necesidad de un servidor de "quién tiene razón".

**Yjs** es la librería CRDT más madura del ecosistema. Se integra nativamente con TipTap via `@tiptap/extension-collaboration`.

> **[REQUIRED] REGLA:** Para documentos con > 1 editor simultáneo, el estado del editor NUNCA se sincroniza enviando el JSON completo en cada keystroke. Se sincronizan solo los **deltas** (diff binario de Yjs). PROHIBIDO usar un simple `onUpdate + POST` para colaboración: crearías un race condition de sobreescritura.
>
> **Por qué:** enviar el documento completo en cada pulsación de tecla satura la red con payloads que crecen con el tamaño del documento, y dos ediciones simultáneas enviando el JSON completo generan una condición de carrera donde la última en llegar sobreescribe a la otra. Sincronizar solo los deltas es lo que Yjs resuelve matemáticamente sin que ninguna edición se pierda.

---

## ⚙️ 1. INSTALACIÓN

```bash
npm install yjs @tiptap/extension-collaboration @tiptap/extension-collaboration-cursor y-supabase
# y-supabase: proveedor de sincronización Yjs sobre Supabase Realtime
```

---

## 💻 2. PROVEEDOR DE SINCRONIZACIÓN: `useYjsDocument`

El proveedor conecta el documento Yjs con Supabase Realtime como canal de broadcast para sincronizar los cambios binarios entre los usuarios conectados.

```tsx
import * as Y from 'yjs'
import { useEffect, useRef, useState } from 'react'
import { SupabaseProvider } from 'y-supabase'
import { supabase } from '@/lib/supabase'

export interface CollaboratorInfo {
  userId: string
  name: string
  color: string   // Color único por usuario (para cursor)
  avatar?: string
}

export function useYjsDocument(documentId: string, currentUser: CollaboratorInfo) {
  const ydocRef     = useRef<Y.Doc | null>(null)
  const providerRef = useRef<SupabaseProvider | null>(null)
  
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting')
  const [collaborators, setCollaborators] = useState<CollaboratorInfo[]>([])

  useEffect(() => {
    if (!documentId || !currentUser.userId) return

    // 1. Crear el documento Yjs (es el "estado compartido")
    const ydoc = new Y.Doc()
    ydocRef.current = ydoc

    // 2. Proveedor Supabase: envía y recibe diffs binarios por Realtime Broadcast
    const provider = new SupabaseProvider(supabase, {
      name: `document:${documentId}`,  // Canal único por documento
      document: ydoc,
      
      // Awareness: posición del cursor + metadata de cada usuario activo
      awareness: {
        user: {
          userId: currentUser.userId,
          name:   currentUser.name,
          color:  currentUser.color,
          avatar: currentUser.avatar
        }
      }
    })
    providerRef.current = provider

    // 3. Estado de conexión
    provider.on('status', (event: { status: 'connecting' | 'connected' | 'disconnected' }) => {
      setStatus(event.status)
    })

    // 4. Awareness: quién está conectado (cursores visibles)
    provider.awareness.on('change', () => {
      const states = Array.from(provider.awareness.getStates().entries())
      const active = states
        .filter(([clientId]) => clientId !== ydoc.clientID)
        .map(([, state]) => state.user as CollaboratorInfo)
        .filter(Boolean)
      setCollaborators(active)
    })

    return () => {
      provider.destroy()
      ydoc.destroy()
    }
  }, [documentId, currentUser.userId])

  return {
    ydoc: ydocRef.current,
    provider: providerRef.current,
    status,
    collaborators
  }
}
```

---

## 💻 3. EDITOR CON COLABORACIÓN (TipTap + Yjs)

```tsx
import { useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Collaboration from '@tiptap/extension-collaboration'
import CollaborationCursor from '@tiptap/extension-collaboration-cursor'
import { useYjsDocument } from '@/hooks/useYjsDocument'

export function CollaborativeEditor({
  documentId,
  currentUser,
  editable = true
}) {
  const { ydoc, provider, status, collaborators } = useYjsDocument(documentId, currentUser)

  const editor = useEditor({
    editable,
    extensions: [
      StarterKit.configure({
        history: false  // CRÍTICO: Yjs maneja el historial, no TipTap
      }),
      
      // 1. Colaboración CRDT (sincroniza el texto via Yjs)
      Collaboration.configure({
        document: ydoc  // El Y.Doc compartido
      }),
      
      // 2. Cursores múltiples visibles (Awareness de Yjs)
      CollaborationCursor.configure({
        provider: provider,
        user: {
          name:  currentUser.name,
          color: currentUser.color
        },
        render(user) {
          // Renderizar el cursor del colaborador con su nombre y color
          const cursor = document.createElement('span')
          cursor.classList.add('collaboration-cursor__caret')
          cursor.style.borderLeftColor = user.color

          const label = document.createElement('div')
          label.classList.add('collaboration-cursor__label')
          label.style.backgroundColor = user.color
          label.textContent = user.name
          
          cursor.insertBefore(label, null)
          return cursor
        }
      })
    ]
  }, [ydoc, provider])  // Re-crear el editor cuando cambie el provider

  return (
    <div className="relative">
      {/* Badge de estado de conexión */}
      <ConnectionStatus status={status} collaborators={collaborators} />

      {/* Avatares de colaboradores activos */}
      <CollaboratorAvatars collaborators={collaborators} />

      {/* Editor */}
      <EditorContent editor={editor} className="prose dark:prose-invert max-w-none p-8" />
    </div>
  )
}
```

---

## 🟢 4. UI: AVATARES DE COLABORADORES Y ESTADO

```tsx
// Avatares de colaboradores activos (como Google Docs)
function CollaboratorAvatars({ collaborators }: { collaborators: CollaboratorInfo[] }) {
  if (collaborators.length === 0) return null

  return (
    <div className="flex -space-x-2 mb-4">
      {collaborators.slice(0, 5).map(user => (
        <div
          key={user.userId}
          title={user.name}
          className="w-8 h-8 rounded-full border-2 border-background flex items-center justify-center text-xs text-white font-bold"
          style={{ backgroundColor: user.color }}
        >
          {user.name[0].toUpperCase()}
        </div>
      ))}
      {collaborators.length > 5 && (
        <div className="w-8 h-8 rounded-full border-2 border-background bg-surface flex items-center justify-center text-xs font-bold">
          +{collaborators.length - 5}
        </div>
      )}
    </div>
  )
}

// Indicador de estado de la conexión WebSocket
function ConnectionStatus({ status, collaborators }) {
  const colors = {
    connected:    'bg-green-500',
    connecting:   'bg-yellow-500 animate-pulse',
    disconnected: 'bg-red-500'
  }
  
  return (
    <div className="flex items-center gap-2 text-xs text-foreground/50 mb-2">
      <div className={`w-2 h-2 rounded-full ${colors[status]}`} />
      <span>
        {status === 'connected'    && `${collaborators.length} colaborador(es) activo(s)`}
        {status === 'connecting'   && 'Conectando...'}
        {status === 'disconnected' && 'Sin conexión — cambios guardados localmente'}
      </span>
    </div>
  )
}
```

---

## 🎨 5. ESTILOS CSS PARA LOS CURSORES

```css
/* globals.css — estilos para cursores CRDT */
.collaboration-cursor__caret {
  border-left: 2px solid currentColor;
  border-right: 2px solid currentColor;
  margin-left: -1px;
  margin-right: -1px;
  pointer-events: none;
  position: relative;
  word-break: normal;
}

.collaboration-cursor__label {
  border-radius: 4px 4px 4px 0;
  color: white;
  font-size: 11px;
  font-style: normal;
  font-weight: 600;
  left: -1px;
  line-height: normal;
  padding: 0.1rem 0.3rem;
  position: absolute;
  top: -1.5em;
  user-select: none;
  white-space: nowrap;
}
```

---

## 🔄 6. HISTORIAL DE VERSIONES (Time Travel con Yjs)

```typescript
// Cada N minutos, persistir un snapshot del documento en document_versions
// Esto es el "time travel" — no se necesita guardar cada operación Yjs

async function snapshotVersion(documentId: string, ydoc: Y.Doc, userId: string) {
  const content = JSON.stringify(ydoc.getMap('content').toJSON())

  const { data: lastVersion } = await supabase
    .from('document_versions')
    .select('version_num')
    .eq('document_id', documentId)
    .order('version_num', { ascending: false })
    .limit(1)
    .single()

  const nextVersion = (lastVersion?.version_num ?? 0) + 1

  await supabase.from('document_versions').insert({
    document_id: documentId,
    version_num: nextVersion,
    content,
    created_by: userId
  })
}
```

---

## ⚠️ LIMITACIONES Y CONSIDERACIONES

| Aspecto | Situación |
|---------|-----------|
| Persistencia Yjs | El doc Yjs vive en memoria/Supabase. Al reconectar, Supabase provee el estado actual. |
| Offline | Yjs soporta edición offline y merge al reconectar (FRONTEND_PWA_STANDARD.md). |
| Máx usuarios simultáneos | Sin límite técnico en Yjs, pero Supabase Realtime tiene caps de conexiones según tier. |
| Encriptado | El contenido viaja en texto plano por Supabase Realtime. Para E2E encryption: `[NO CUBIERTO - Tarea futura]`. |
