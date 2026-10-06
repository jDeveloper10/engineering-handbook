---
title: "Estándar de Supabase"
category: 02_Backend
doc_type: estandar
tags: [supabase, postgresql, rls, realtime, auth]
summary: "Estándar del dominio Backend para Supabase: PostgreSQL, RLS, Auth, Realtime, Edge Functions y patrones de uso."
keywords: [supabase, postgresql, rls, row-level-security, realtime, edge-functions, auth]
updated: 2026-08-30
status: current
---

# SUPABASE ENGINEERING STANDARD

> **Stack de referencia:** Supabase (PostgreSQL + Auth + Realtime + Edge Functions)
> **Depende de:** BACKEND_ENGINEERING_STANDARD.md (Nivel 1), SECURITY_ENGINEERING_STANDARD.md, DATABASE_ENGINEERING_STANDARD.md
> **Aplica a:** Todo proyecto que use Supabase como backend

---

## 01. Supabase Client Configuration

### 1.1 Cliente único

**[REQUIRED]** Un solo archivo de configuración de Supabase:

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
});
```

### 1.2 Variables de entorno

**[REQUIRED]** Solo valores PÚBLICOS en el frontend:

```bash
# ✅ PERMITIDO en frontend (.env.local)
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_xxx

# ❌ PROHIBIDO en frontend
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # ← NUNCA en frontend
```

### 1.3 Service Role SOLO en backend

**[REQUIRED]** La `service_role` key NUNCA se usa en el frontend:

```typescript
// ❌ PROHIBIDO en frontend
import { createClient } from '@supabase/supabase-js';
const supabase = createClient(url, SERVICE_ROLE_KEY); // Salta RLS

// ✅ CORRECTO — solo en Workers/Edge Functions
const supabaseAdmin = createClient(url, SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false }
});
```

---

## 02. Row Level Security (RLS)

### 2.1 RLS SIEMPRE habilitado

**[REQUIRED]** Toda tabla tiene RLS habilitado. Sin excepciones:

```sql
-- ✅ REQUIRED
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- ❌ PROHIBIDO — tabla pública sin RLS
-- (cualquiera con la anon key puede leer todo)
```

### 2.2 Patrones de RLS

**[REQUIRED]** Implementar RLS según el patrón de acceso:

```sql
-- Patrón 1: Usuario ve solo sus datos
CREATE POLICY "user_own_data" ON orders
  FOR ALL TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Patrón 2: Admin ve todo
CREATE POLICY "admin_all" ON orders
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
        AND profiles.role = 'admin'
    )
  );

-- Patrón 3: Lectura pública, escritura autenticada
CREATE POLICY "public_read" ON products
  FOR SELECT TO anon
  USING (true);

CREATE POLICY "admin_write" ON products
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
        AND profiles.role = 'admin'
    )
  );
```

### 2.3 Verificar RLS activo

**[REQUIRED]** Verificar RLS antes de cada deploy:

```sql
-- Query para verificar RLS
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND rowsecurity = false;
-- Resultado debe ser vacío (todas las tablas tienen RLS)
```

---

## 03. Supabase Auth

### 3.1 Configuración de Auth

**[REQUIRED]** Configurar Auth en un solo lugar:

```typescript
// src/lib/auth.ts
import { supabase } from './supabase';

export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.trim().toLowerCase(),
    password,
  });
  
  if (error) throw error;
  return data;
}

export async function signUpWithEmail(email: string, password: string, metadata?: Record<string, unknown>) {
  const { data, error } = await supabase.auth.signUp({
    email: email.trim().toLowerCase(),
    password,
    options: { data: metadata },
  });
  
  if (error) throw error;
  return data;
}

export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}

export async function getCurrentUser() {
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error || !user) return null;
  return user;
}
```

### 3.2 Listener de sesión

**[REQUIRED]** Escuchar cambios de sesión:

```typescript
// src/lib/auth.ts
export function onAuthStateChange(callback: (user: User | null) => void) {
  return supabase.auth.onAuthStateChange((event, session) => {
    callback(session?.user ?? null);
  });
}
```

### 3.3 Magic Links

**[REQUIRED]** Configurar TTL y uso:

```typescript
// Magic link con expiración de 15 minutos (configurar en Supabase Dashboard)
const { error } = await supabase.auth.signInWithOtp({
  email,
  options: {
    emailRedirectTo: `${window.location.origin}/auth/callback`,
  },
});
```

---

## 04. Queries con Supabase

### 4.1 Queries tipadas

**[REQUIRED]** Generar tipos desde Supabase CLI:

```bash
supabase gen types typescript --project-id xxx > src/types/database.types.ts
```

```typescript
// src/types/database.types.ts (generado, no editar manualmente)
import type { Database } from './database.types';

type Tables = Database['public']['Tables'];
type Order = Tables['orders']['Row'];
type OrderInsert = Tables['orders']['Insert'];
```

### 4.2 Patrones de query

**[REQUIRED]** Usar el builder de Supabase, no SQL raw:

```typescript
// ✅ Builder tipado
const { data, error } = await supabase
  .from('orders')
  .select('id, status, total_cents, created_at')
  .eq('user_id', userId)
  .order('created_at', { ascending: false })
  .limit(20);

// ❌ SQL raw (pierde tipado)
const { data, error } = await supabase.rpc('get_orders', { p_user_id: userId });
```

### 4.3 Manejo de errores

**[REQUIRED]** Siempre manejar errores de Supabase:

```typescript
const { data, error } = await supabase.from('orders').select('id, user_id, total, status');

if (error) {
  console.error('Supabase error:', error.message);
  throw new AppError('DATABASE_ERROR', 'Error al obtener órdenes');
}

// data es seguro de usar aquí
```

---

## 05. Realtime

### 5.1 Suscripciones a cambios

**[REQUIRED]** Usar Realtime para datos en vivo:

```typescript
// Escuchar cambios en tiempo real
const channel = supabase
  .channel('orders-changes')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'orders', filter: `user_id=eq.${userId}` },
    (payload) => {
      console.log('Order changed:', payload);
      // Actualizar estado local
    }
  )
  .subscribe();

// Cleanup
return () => {
  supabase.removeChannel(channel);
};
```

### 5.2 Broadcast para eventos no persistentes

**[REQUIRED]** Usar Broadcast para eventos efímeros (typing indicators, notifications):

```typescript
// Enviar
await supabase.channel('room').send({
  type: 'broadcast',
  event: 'typing',
  payload: { userId, isTyping: true },
});

// Recibir
supabase.channel('room').on('broadcast', { event: 'typing' }, (payload) => {
  // Manejar typing indicator
}).subscribe();
```

---

## 06. Edge Functions

### 6.1 Estructura

**[REQUIRED]** Edge Functions en `supabase/functions/`:

```
supabase/
├── functions/
│   ├── _shared/
│   │   ├── cors.ts
│   │   └── auth.ts
│   ├── process-payment/
│   │   └── index.ts
│   └── send-email/
│       └── index.ts
└── config.toml
```

### 6.2 CORS en Edge Functions

**[REQUIRED]** CORS explícito en cada function:

```typescript
// supabase/functions/_shared/cors.ts
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://tuapp.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export function handleCORS(req: Request): Response | null {
  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  return null;
}
```

### 6.3 Service Role en Edge Functions

**[REQUIRED]** Usar service_role solo en Edge Functions:

```typescript
// supabase/functions/process-payment/index.ts
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const supabaseAdmin = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
);
```

---

## 07. Generación de Tipos

### 7.1 Tipos desde Supabase CLI

**[REQUIRED]** Regenerar tipos después de cada migración:

```bash
# Instalar Supabase CLI
npm install -g supabase

# Login
supabase login

# Generar tipos
supabase gen types typescript --project-id tu-project-id > src/types/database.types.ts
```

### 7.2 Uso de tipos generados

**[REQUIRED]** Importar tipos desde el archivo generado:

```typescript
import type { Database } from '@/types/database.types';

type Tables = Database['public']['Tables'];
type Order = Tables['orders']['Row'];
type Profile = Tables['profiles']['Row'];
```

---

## Checklist Pre-Deploy Supabase

- [ ] RLS habilitado en TODAS las tablas
- [ ] Service role key NUNCA en frontend
- [ ] Anon key en `.env.local` (no en código)
- [ ] Tipos generados después de cada migración
- [ ] Queries con builder (no raw SQL en frontend)
- [ ] Errores de Supabase manejados
- [ ] Realtime configurado para datos en vivo
- [ ] Edge Functions con CORS explícito
