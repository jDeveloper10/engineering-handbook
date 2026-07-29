---
title: "Patrón: React Query + Supabase Realtime"
category: 01_Frontend
tags: [react-query, realtime, supabase, websockets]
status: current
---

# Patrón: Integración de React Query y Supabase Realtime

## El Problema
Supabase Realtime empuja actualizaciones instantáneas desde Postgres al frontend vía WebSockets. Sin embargo, nuestro gestor de estado global es React Query, que asume un modelo de *fetch/polling*. 

Si te suscribes a eventos en los `useEffect` sueltos de tus componentes y mutas estados locales (`useState`), el caché global de React Query quedará obsoleto (desincronizado). La fuente de verdad del Frontend debe ser SIEMPRE React Query.

## La Solución: Hook de Suscripción que Invalida Caché

El patrón exige crear un hook especializado `useRealtimeSubscription` que no muta datos directamente, sino que ordena a React Query **invalidar y refetchear** las queries afectadas cuando ocurre un evento, o aplica optimistic updates sobre el caché si el payload contiene toda la información.

### 1. El Hook Maestro

```tsx
// src/hooks/useRealtimeSubscription.ts
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useQueryClient } from '@tanstack/react-query';

type SubscriptionStatus = 'SUBSCRIBED' | 'CLOSED' | 'TIMED_OUT' | 'CHANNEL_ERROR';

interface RealtimeOptions {
  table: string;
  filter?: string; // ej: "user_id=eq.123"
  event?: 'INSERT' | 'UPDATE' | 'DELETE' | '*';
  queryKeysToInvalidate?: string[][]; // ej: [['proposals'], ['notifications']]
  onEvent?: (payload: RealtimePostgresChangesPayload<Record<string, unknown>>) => void;
}

export function useRealtimeSubscription({ 
  table, 
  filter, 
  event = '*', 
  queryKeysToInvalidate,
  onEvent 
}: RealtimeOptions) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<SubscriptionStatus>('CLOSED');

  useEffect(() => {
    // 1. Canal único basado en tabla y filtro para evitar colisiones
    const channelName = `realtime:${table}:${filter || 'all'}`;
    
    const channel = supabase.channel(channelName)
      .on(
        'postgres_changes',
        { event, schema: 'public', table, filter },
        (payload) => {
          // 2. Acción 1: Invalidar queries automáticamente para que React Query haga fetch
          if (queryKeysToInvalidate) {
            queryKeysToInvalidate.forEach(queryKey => {
              queryClient.invalidateQueries({ queryKey });
            });
          }
          
          // 3. Acción 2: Callback custom (ej. lanzar un Toast de éxito)
          if (onEvent) onEvent(payload);
        }
      )
      .subscribe((status, err) => {
        setStatus(status as SubscriptionStatus);
        if (err) console.error(`Error de Realtime en ${channelName}:`, err);
      });

    // 4. Cleanup OBLIGATORIO para evitar memory leaks y websockets duplicados
    return () => {
      supabase.removeChannel(channel);
    };
  }, [table, filter, event, queryClient]); // Dependencias estrictas

  return { status };
}
```

### 2. Uso en un Componente

**[REQUIRED] Regla:** NUNCA subscribirse directamente en un `useEffect` usando Supabase crudo dentro de un componente de vista. SIEMPRE usar este hook o un derivado específico del dominio.

```tsx
// src/features/proposals/ProposalDashboard.tsx
import { useRealtimeSubscription } from '@/hooks/useRealtimeSubscription';
import { useProposals } from './hooks/useProposals';
import { toast } from 'sonner';

export function ProposalDashboard({ userId }) {
  const { data: proposals } = useProposals();

  // Mantenemos sincronizada la lista de propuestas en tiempo real
  const { status } = useRealtimeSubscription({
    table: 'proposals',
    filter: `freelancer_id=eq.${userId}`,
    event: 'UPDATE',
    queryKeysToInvalidate: [['proposals']], // Hará que useProposals() repida los datos
    onEvent: (payload) => {
      if (payload.new.status === 'accepted') {
        toast.success(`La propuesta ha sido aceptada por el cliente! 🎉`);
      }
    }
  });

  return (
    <div>
      <Badge status={status} /> {/* SUBSCRIBED, CLOSED... */}
      <ProposalTable data={proposals} />
    </div>
  );
}
```

## Reglas Inquebrantables

1. **Limpieza (Cleanup) Obligatoria:** Todo hook que genere un channel `supabase.channel()` debe devolver una función cleanup que invoque `removeChannel()`. Un componente desmontado que no cierre su canal dejará una conexión Zombie WebSocket gastando cuota y RAM.
2. **Filtros Estrictos (RLS Proxy):** Supabase Realtime no evalúa RLS de la misma forma al vuelo para conexiones masivas a menos que se configure estrictamente. El parámetro `filter` DEBE usarse siempre para limitar qué eventos bajan al cliente (ej. `filter: "user_id=eq.123"`). No suscribirse a la tabla global.
