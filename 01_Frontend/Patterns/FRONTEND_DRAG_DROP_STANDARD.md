---
title: "Patrón Drag & Drop"
category: 01_Frontend
tags: [dnd-kit, drag-drop, kanban, react, optimistic]
summary: "Drag and drop accesible con dnd-kit: tablero Kanban completo, helpers de manipulación de columnas e integración con mutaciones optimistas."
keywords: [dnd-kit, drag-drop, kanban, react, optimistic, drag, drop, accesible, tablero, completo, helpers, manipulacion, columnas, integracion]
updated: 2026-07-29
status: current
---

# 🃏 PATRÓN DRAG & DROP (dnd-kit)

## 🎯 ¿Qué es y cuándo usarlo?
**dnd-kit** es la librería oficial del ecosistema de shadcn/ui para drag & drop. Es accesible (ARIA), performante (cero dependencias de DOM imperativo) y funciona de forma nativa con React. Usar **SIEMPRE dnd-kit** — PROHIBIDO usar `react-beautiful-dnd` (no mantenida) o implementar drag & drop manual con `mousedown/mousemove`.

> **REGLA INQUEBRANTABLE:** Todo Drag & Drop DEBE ser **Optimistic** (FRONTEND_OPTIMISTIC_MUTATIONS.md). El estado visual cambia al instante al soltar. Si el guardado en el servidor falla, rollback inmediato con Toast de error.

---

## ⚙️ 1. INSTALACIÓN

```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

---

## 💻 2. TABLERO KANBAN COMPLETO

### 2.1 Hook: `useKanbanBoard`

```tsx
import { useState, useCallback } from 'react'
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners
} from '@dnd-kit/core'
import { arrayMove } from '@dnd-kit/sortable'
import { useOptimisticMutation } from '@/hooks/useOptimisticMutation'

export type KanbanCard = {
  id: string
  column_id: string
  title: string
  position: number
  document_id?: string
  assignee_id?: string
}

export type KanbanColumn = {
  id: string
  name: string
  position: number
  cards: KanbanCard[]
}

export function useKanbanBoard(teamId: string, initialColumns: KanbanColumn[]) {
  const [columns, setColumns] = useState<KanbanColumn[]>(initialColumns)
  const [activeCard, setActiveCard] = useState<KanbanCard | null>(null)

  // Configurar sensores táctiles y de puntero (accesibilidad)
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 }  // 8px mínimo antes de activar drag
    })
  )

  // Mutación optimista para mover card
  const { mutate: moveCard } = useOptimisticMutation({
    queryKey: ['kanban', teamId],
    mutationFn: ({ cardId, columnId, position }: { cardId: string; columnId: string; position: number }) =>
      api.moveCard(cardId, { column_id: columnId, position }),
    optimisticUpdate: (old: KanbanColumn[], { cardId, columnId, position }) => {
      // La UI ya está actualizada localmente (setColumns más abajo)
      // Este optimisticUpdate solo sincroniza la caché de React Query
      return old // ya fue mutado en onDragEnd
    },
    // En caso de error: el onError restaurará la caché y mostrará Toast
  })

  const onDragStart = (event: DragStartEvent) => {
    const card = findCard(columns, event.active.id as string)
    setActiveCard(card ?? null)
  }

  const onDragOver = (event: DragOverEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    const activeCol = findColumnByCard(columns, active.id as string)
    const overCol   = findColumnByCard(columns, over.id as string)
                      ?? findColumn(columns, over.id as string)

    if (!activeCol || !overCol || activeCol.id === overCol.id) return

    // Mover card entre columnas en tiempo real (visual inmediato)
    setColumns(prev => moveCardBetweenColumns(prev, active.id as string, overCol.id))
  }

  const onDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveCard(null)

    if (!over) return

    const activeCol = findColumnByCard(columns, active.id as string)
    const overCol   = findColumnByCard(columns, over.id as string)
                      ?? findColumn(columns, over.id as string)

    if (!activeCol || !overCol) return

    // Recalcular posiciones
    const targetCards = overCol.cards
    const overIndex   = targetCards.findIndex(c => c.id === over.id)
    const newPosition = overIndex >= 0 ? overIndex : targetCards.length

    // 1. Actualizar UI localmente (ya hecho en onDragOver)
    setColumns(prev => reorderCardsInColumn(prev, active.id as string, overCol.id, newPosition))

    // 2. Persistir en backend (optimistic: ya se ve el resultado)
    moveCard({
      cardId:   active.id as string,
      columnId: overCol.id,
      position: newPosition
    })
  }

  return { columns, activeCard, sensors, onDragStart, onDragOver, onDragEnd }
}
```

### 2.2 Componente: `KanbanBoard`

```tsx
import {
  DndContext, DragOverlay,
  closestCorners
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { useKanbanBoard } from '@/hooks/useKanbanBoard'

export function KanbanBoard({ teamId, initialColumns }) {
  const { columns, activeCard, sensors, onDragStart, onDragOver, onDragEnd } =
    useKanbanBoard(teamId, initialColumns)

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={onDragStart}
      onDragOver={onDragOver}
      onDragEnd={onDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map(column => (
          <KanbanColumn key={column.id} column={column} />
        ))}
      </div>

      {/* DragOverlay: la "sombra" que sigue al cursor durante el drag */}
      <DragOverlay>
        {activeCard ? (
          <KanbanCardItem card={activeCard} isDragging />
        ) : null}
      </DragOverlay>
    </DndContext>
  )
}

function KanbanColumn({ column }) {
  const cardIds = column.cards.map(c => c.id)

  return (
    <div className="flex flex-col w-72 bg-surface rounded-xl p-3 shrink-0">
      {/* Header de columna */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-sm text-foreground">{column.name}</h3>
        <span className="text-xs text-foreground/50 bg-surface-2 px-2 py-0.5 rounded-full">
          {column.cards.length}
        </span>
      </div>

      {/* Cards (sortable dentro de la columna) */}
      <SortableContext items={cardIds} strategy={verticalListSortingStrategy}>
        <div className="flex flex-col gap-2 min-h-[100px]">
          {column.cards.map(card => (
            <SortableCard key={card.id} card={card} />
          ))}
        </div>
      </SortableContext>

      {/* Botón añadir card */}
      <button className="mt-3 w-full py-2 text-sm text-foreground/50 hover:text-foreground hover:bg-surface-2 rounded-lg transition-colors">
        + Agregar documento
      </button>
    </div>
  )
}
```

### 2.3 Componente: `SortableCard`

```tsx
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

function SortableCard({ card }: { card: KanbanCard }) {
  const {
    attributes, listeners, setNodeRef,
    transform, transition, isDragging
  } = useSortable({ id: card.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1  // La card original se vuelve fantasma
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-background border rounded-lg p-3 cursor-grab active:cursor-grabbing shadow-sm hover:shadow-md transition-shadow"
    >
      <KanbanCardItem card={card} />
    </div>
  )
}

function KanbanCardItem({ card, isDragging = false }: { card: KanbanCard; isDragging?: boolean }) {
  return (
    <div className={isDragging ? 'opacity-80 shadow-xl' : ''}>
      <p className="text-sm font-medium text-foreground">{card.title}</p>
      {card.assignee_id && (
        <div className="mt-2 flex items-center gap-1">
          <UserAvatar userId={card.assignee_id} size="sm" />
        </div>
      )}
      {card.due_date && (
        <p className="mt-1 text-xs text-foreground/50">
          📅 {new Date(card.due_date).toLocaleDateString()}
        </p>
      )}
    </div>
  )
}
```

---

## 🔧 3. HELPERS DE MANIPULACIÓN DE COLUMNAS

```typescript
// Encontrar la card en cualquier columna
function findCard(columns: KanbanColumn[], cardId: string): KanbanCard | undefined {
  return columns.flatMap(c => c.cards).find(c => c.id === cardId)
}

// Encontrar la columna que contiene una card
function findColumnByCard(columns: KanbanColumn[], cardId: string): KanbanColumn | undefined {
  return columns.find(col => col.cards.some(c => c.id === cardId))
}

// Encontrar columna por su propio ID
function findColumn(columns: KanbanColumn[], colId: string): KanbanColumn | undefined {
  return columns.find(c => c.id === colId)
}

// Mover card entre columnas
function moveCardBetweenColumns(
  columns: KanbanColumn[],
  cardId: string,
  targetColId: string
): KanbanColumn[] {
  const card = findCard(columns, cardId)
  if (!card) return columns

  return columns.map(col => {
    if (col.cards.some(c => c.id === cardId)) {
      return { ...col, cards: col.cards.filter(c => c.id !== cardId) }
    }
    if (col.id === targetColId) {
      return { ...col, cards: [...col.cards, { ...card, column_id: targetColId }] }
    }
    return col
  })
}
```

---

## ✅ CHECKLIST

- [ ] `PointerSensor` con `activationConstraint.distance = 8` (evita drag accidental en clic)
- [ ] `DragOverlay` implementado para la sombra visual
- [ ] Cards con `opacity: 0.4` mientras se arrastran (estado fantasma)
- [ ] Mutación optimista con rollback automático en caso de error de red
- [ ] Recalcular `position` de todas las cards de la columna afectada al persistir
- [ ] Soporte táctil: `PointerSensor` lo cubre automáticamente
- [ ] ARIA: dnd-kit maneja `aria-grabbed`, `aria-dropeffect` automáticamente
