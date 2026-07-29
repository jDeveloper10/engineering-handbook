---
title: "Patrón Optimistic Mutations"
category: 01_Frontend
tags: [react-query, ux, mutations, optimistic-ui]
summary: "Mutaciones optimistas con React Query: hook genérico que actualiza la caché al instante, hace rollback ante error y ofrece deshacer, con tres ejemplos reales de UX instantánea."
keywords: [react-query, ux, mutations, optimistic-ui, optimistic, mutaciones, optimistas, react, query, hook, generico, actualiza, cache, instante]
updated: 2026-07-29
status: current
---

# ⚡ PATRÓN OPTIMISTIC MUTATIONS (Mutaciones Optimistas)

## 🎯 ¿Qué es y por qué es crítico?
Una **Mutación Optimista** es la técnica de actualizar la UI instantáneamente asumiendo que el request al servidor será exitoso, antes de que este siquiera responda. Si el request falla, la UI revierte silenciosamente al estado anterior (Rollback).
La latencia de red pasa de ser un obstáculo a ser completamente invisible para el usuario. La app se siente "instantánea".

> **REGLA INQUEBRANTABLE:** Toda mutación de cambio de estado simple (toggles, likes, mover tarjetas, reordenar) DEBE ser optimista. PROHIBIDO mostrar un spinner para un toggle de favorito. Si falla, rollback.

---

## 💻 HOOK GENÉRICO PARA MUTACIONES OPTIMISTAS

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

export function useOptimisticMutation<TData, TVariables, TContext>({
  mutationFn,
  queryKey,
  optimisticUpdate, // Función que dice cómo mutar la caché localmente
  successMessage
}: {
  mutationFn: (variables: TVariables) => Promise<TData>
  queryKey: readonly unknown[]
  optimisticUpdate: (oldData: TData | undefined, variables: TVariables) => TData
  successMessage?: string
}) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn,
    // 1. ON MUTATE: Se ejecuta INMEDIATAMENTE al llamar .mutate()
    onMutate: async (variables) => {
      // Cancelar queries en vuelo para que no pisen nuestra actualización optimista
      await queryClient.cancelQueries({ queryKey })

      // Snapshot del estado previo (para el rollback)
      const previousData = queryClient.getQueryData(queryKey)

      // Actualizar la caché local de forma optimista
      queryClient.setQueryData<TData>(queryKey, (old) => optimisticUpdate(old, variables))

      return { previousData } // Se pasa como context a onError/onSettled
    },
    // 2. ON ERROR: Falló la red o el backend
    onError: (err, variables, context) => {
      // ROLLBACK: Restaurar el snapshot guardado
      if (context?.previousData) {
        queryClient.setQueryData(queryKey, context.previousData)
      }
      toast.error('Ocurrió un error. Se han revertido los cambios.', {
        action: {
          label: 'Reintentar',
          onClick: () => mutationFn(variables) // Lógica de reintento manual
        }
      })
    },
    // 3. ON SETTLED: Siempre se ejecuta al final (éxito o error)
    onSettled: () => {
      // Invalidar para traer la verdad absoluta desde el servidor
      queryClient.invalidateQueries({ queryKey })
    },
    onSuccess: () => {
      if (successMessage) toast.success(successMessage)
    }
  })
}
```

---

## 🚀 3 EJEMPLOS REALES DE UX INSTANTÁNEA

### Ejemplo 1: Toggle de Favorito (Instantáneo)
```tsx
const { mutate: toggleFavorite } = useOptimisticMutation({
  queryKey: ['proposals'],
  mutationFn: (id: string) => api.toggleFavorite(id),
  optimisticUpdate: (oldProposals, id) => {
    // Si la caché está vacía, no hacemos nada
    if (!oldProposals) return oldProposals
    // Invertir el estado de favorito instantáneamente
    return oldProposals.map((p: Proposal) => 
      p.id === id ? { ...p, isFavorite: !p.isFavorite } : p
    )
  }
})

// Uso en UI:
<button onClick={() => toggleFavorite(proposal.id)}>
  <HeartIcon filled={proposal.isFavorite} /> {/* Cambia al instante */}
</button>
```

### Ejemplo 2: Cambio de Estado (Draft → Sent)
```tsx
const { mutate: updateStatus } = useOptimisticMutation({
  queryKey: ['proposal', proposalId],
  mutationFn: ({ id, status }) => api.updateStatus(id, status),
  optimisticUpdate: (oldProposal, variables) => {
    if (!oldProposal) return oldProposal
    return { ...oldProposal, status: variables.status }
  },
  successMessage: 'Propuesta enviada al cliente.'
})
```

### Ejemplo 3: Reordenar Items (Drag & Drop)
```tsx
const { mutate: reorderItems } = useOptimisticMutation({
  queryKey: ['board-items'],
  mutationFn: ({ items }) => api.saveOrder(items.map(i => i.id)),
  optimisticUpdate: (oldItems, variables) => {
    // variables.items ya tiene el nuevo orden dictado por la librería de Drag&Drop
    return variables.items 
  }
})
```

---

## 🛡️ MANEJO DE ERRORES: "DESHACER" (UNDO)

El rollback de `onError` garantiza la consistencia, pero brindar un botón "Reintentar" o "Deshacer" en un Toast es el toque final de UX:

```tsx
toast.error('Error al guardar el orden de las tarjetas.', {
  action: {
    label: 'Reintentar',
    onClick: () => retryMutation()
  }
})
```
