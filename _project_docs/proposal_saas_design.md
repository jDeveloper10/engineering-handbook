# Diseño Arquitectónico: SaaS de Gestión de Propuestas Comerciales

Este documento diseña la aplicación de principio a fin, adhiriéndose **estrictamente** a las reglas definidas en el Engineering Handbook. Cuando el manual presenta una fisura o un vacío de conocimiento, se marca explícitamente con `[NO CUBIERTO POR HANDBOOK]`.

---

## FASE 1: DISEÑO DE BASE DE DATOS (Supabase / Postgres)

### 1.1 Esquema SQL y Migración (UP)

```sql
-- UP MIGRATION
BEGIN;

-- Extensión para UUIDs si no está habilitada
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Tabla de Clientes
CREATE TABLE clients (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    freelancer_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name text NOT NULL,
    company text,
    email text NOT NULL,
    phone text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- REGLA DB-002: FK con índice explícito
CREATE INDEX idx_clients_freelancer_id ON clients(freelancer_id);

-- 2. Tabla de Propuestas
CREATE TABLE proposals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    freelancer_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    status text NOT NULL CHECK (status IN ('draft', 'sent', 'accepted', 'rejected', 'expired')),
    template_type text NOT NULL DEFAULT 'minimalist',
    public_token uuid UNIQUE DEFAULT gen_random_uuid(), -- Token para acceso sin login
    internal_notes text, -- [REGLA DB-005] Idealmente, si hubiera datos muy sensibles de negocio, irían cifrados. Aquí asumimos texto normal o aplicar pgcrypto.
    sent_at timestamptz,
    expires_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_proposals_freelancer_id ON proposals(freelancer_id);
CREATE INDEX idx_proposals_client_id ON proposals(client_id);
CREATE INDEX idx_proposals_public_token ON proposals(public_token);

-- 3. Tabla de Ítems (Líneas de la propuesta)
CREATE TABLE proposal_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id uuid NOT NULL REFERENCES proposals(id) ON DELETE CASCADE,
    service_name text NOT NULL,
    estimated_hours numeric(10,2) NOT NULL, -- Horas puede tener decimales
    hourly_rate_cents bigint NOT NULL,     -- REGLA 2.3: Dinero en bigint (centavos)
    total_cents bigint NOT NULL,           -- Calculado/guardado en centavos
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_proposal_items_proposal_id ON proposal_items(proposal_id);

COMMIT;
```

### 1.2 Migración (DOWN) - [REGLA DB-003]

```sql
-- DOWN MIGRATION
BEGIN;
DROP TABLE IF EXISTS proposal_items CASCADE;
DROP TABLE IF EXISTS proposals CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
COMMIT;
```

### 1.3 Row Level Security (RLS) - [REGLA DB-007]

```sql
-- Habilitar RLS OBLIGATORIO
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposal_items ENABLE ROW LEVEL SECURITY;

-- Políticas para Freelancer (Autenticado)
CREATE POLICY "Freelancer ve sus clientes" ON clients FOR SELECT USING (auth.uid() = freelancer_id);
CREATE POLICY "Freelancer inserta sus clientes" ON clients FOR INSERT WITH CHECK (auth.uid() = freelancer_id);
CREATE POLICY "Freelancer edita sus clientes" ON clients FOR UPDATE USING (auth.uid() = freelancer_id);
CREATE POLICY "Freelancer elimina sus clientes" ON clients FOR DELETE USING (auth.uid() = freelancer_id);

-- Políticas para Propuestas
CREATE POLICY "Freelancer gestiona sus propuestas" ON proposals FOR ALL USING (auth.uid() = freelancer_id);
CREATE POLICY "Freelancer gestiona items" ON proposal_items FOR ALL USING (
    EXISTS (SELECT 1 FROM proposals WHERE id = proposal_items.proposal_id AND freelancer_id = auth.uid())
);

-- Política para Cliente Público (Acceso sin login)
CREATE POLICY "Cliente público lee propuesta por token" ON proposals FOR SELECT 
    USING (public_token::text = current_setting('request.jwt.claims', true)::json->>'public_token'); 
    -- [NO CUBIERTO POR HANDBOOK] Tuve que inferir la estrategia de cómo un usuario anónimo (cliente) pasa el token RLS a Supabase sin tener una sesión `auth.uid()`. El handbook no detalla el patrón de "Autenticación anónima por token en RLS".

CREATE POLICY "Cliente público actualiza estado (aceptar/rechazar)" ON proposals FOR UPDATE
    USING (public_token::text = current_setting('request.jwt.claims', true)::json->>'public_token')
    WITH CHECK (status IN ('accepted', 'rejected'));
```

---

## FASE 2: API Y BACKEND (Cloudflare Workers)

### 2.1 Diseño de Endpoints
- `GET /api/proposals?page=1&limit=20` (Paginado)
- `POST /api/proposals`
- `GET /api/proposals/:id`
- `PATCH /api/proposals/:id` (Nunca PUT)
- `GET /api/public/proposals/:token` (Endpoint cliente)
- `PATCH /api/public/proposals/:token/status`

### 2.2 Arquitectura del Worker

```javascript
// src/index.js (Router)
import { handleGetProposals, handleUpdateStatus } from './handlers/proposals.js';
import { requireAuth } from './middleware/auth.js';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/proposals' && request.method === 'GET') {
      const auth = await requireAuth(request, env);
      if (auth.error) return auth.error;
      return handleGetProposals(request, env, auth.user);
    }
    // ...
  }
}
```

```javascript
// src/handlers/proposals.js (Handler -> Service)
import { proposalSchema } from '../lib/schemas.js'; // Zod compartida
import { getProposals } from '../services/proposalService.js';
import { jsonResponse, ok, fail } from '../lib/response.js'; // FORMATO ESTÁNDAR

export async function handleGetProposals(request, env, user) {
  try {
    // Validar query params de paginación (Zod)
    const { page, limit } = getPagination(request);
    
    // NUNCA lógica aquí. Se delega al service.
    const data = await getProposals(env, user.id, page, limit);
    return ok(data);
  } catch (error) {
    return fail("INTERNAL_ERROR", "Error al procesar la solicitud", 500); // SCREAMING_SNAKE_CASE
  }
}
```

---

## FASE 3: FRONTEND (React + TS + Tailwind + Shadcn)

### 3.1 Estructura del Componente (Estados Obligatorios)

```tsx
// src/features/proposals/ProposalDashboard.tsx
import { useProposals } from './hooks/useProposals';
import { SkeletonTable } from '@/components/ui/SkeletonTable';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorDisplay } from '@/components/ui/ErrorDisplay';

export function ProposalDashboard() {
  const { data, isLoading, isError, error, refetch } = useProposals(); // React Query

  if (isLoading) return <SkeletonTable rows={5} />;
  if (isError) return <ErrorDisplay message={error.message} onRetry={refetch} />;
  if (!data || data.length === 0) return <EmptyState title="No hay propuestas" cta="Crear nueva" />;

  return (
     // Success state con datos reales
     <ProposalTable data={data} />
  );
}
```

### 3.2 Formulario y Validación Asíncrona (Debounce & Dirty State)

```tsx
// [REGLAS APLICADAS: Zod, Dirty State, Async Validation]
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDebouncedCallback } from 'use-debounce';

export function ClientForm() {
  const form = useForm({ resolver: zodResolver(clientSchema) });
  
  // Protección contra pérdida de datos
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (form.formState.isDirty) e.preventDefault();
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [form.formState.isDirty]);

  // Validación asíncrona (ej: email único)
  const checkEmail = useDebouncedCallback(async (email: string) => {
    const exists = await api.checkClientEmail(email);
    if (exists) form.setError('email', { message: "El cliente ya existe" });
  }, 500);

  // ...
}
```

### 3.3 Mutación Optimistic (React Query)

```tsx
const mutation = useMutation({
  mutationFn: updateProposalStatus,
  onMutate: async (newProposal) => {
    await queryClient.cancelQueries({ queryKey: ['proposals'] });
    const previous = queryClient.getQueryData(['proposals']);
    
    // Optimistic Update
    queryClient.setQueryData(['proposals'], (old) => 
      old.map(p => p.id === newProposal.id ? { ...p, status: newProposal.status } : p)
    );
    return { previous };
  },
  onError: (err, newProposal, context) => {
    // Rollback
    queryClient.setQueryData(['proposals'], context.previous);
    toast.error("Error al actualizar la propuesta.");
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['proposals'] });
  }
});
```

---

## FASE 4: REAL-TIME Y NOTIFICACIONES

```tsx
// Supabase Realtime Subscription en Frontend
// [NO CUBIERTO POR HANDBOOK] Tuve que inferir cómo estructurar limpiamente la suscripción a WebSockets dentro de la arquitectura de estado global / React Query, ya que el handbook no menciona el patrón exacto para hidratar React Query desde eventos Realtime.

useEffect(() => {
  const channel = supabase
    .channel('public:proposals')
    .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'proposals', filter: `freelancer_id=eq.${user.id}` }, 
      (payload) => {
        if (payload.new.status === 'accepted') {
          toast.success(`¡Propuesta aceptada!`);
          queryClient.invalidateQueries(['proposals']); // Trigger re-fetch
        }
      }
    )
    .subscribe();

  return () => { supabase.removeChannel(channel); };
}, []);
```

---

## FASE 5: PDF Y ARCHIVOS (Cloudflare Platform)

1. **Upload de Logos a R2**:
   - `PUT /api/logos` usa **Streaming**. El Worker recibe el `request.body` y lo pasa directamente a `env.MY_BUCKET.put(key, request.body)`. Nunca usa `await request.arrayBuffer()` para evitar matar la memoria RAM del Worker (Límite 128MB).
   - El Bucket de R2 es privado. Para mostrar el logo en la UI, el backend genera y devuelve una URL firmada (*Presigned URL*).

2. **Generación de PDF en el Edge**:
   - `[NO CUBIERTO POR HANDBOOK] Tuve que inferir cómo generar un PDF en Cloudflare Workers.` Bibliotecas clásicas de Node como `puppeteer` o `pdfkit` pesado no corren en el límite de CPU (30s) ni entorno V8 del Edge. Asumo el uso de `pdf-lib` (que es Edge-compatible) para llenar un PDF pre-existente, o un API externo (API Binding) encargado del renderizado HTML-to-PDF.

---

## FASE 6: SEGURIDAD

1. **CORS Centralizado**: El Worker principal expone `Access-Control-Allow-Origin: https://mi-saas.com` explícito, rechazando orígenes salvajes.
2. **Defensa en profundidad**: 
   - Capa 1: Worker valida que el JWT pertenezca al `freelancer_id`.
   - Capa 2: Supabase RLS valida que el registro consultado corresponda a ese mismo ID.
3. **Tokens Públicos**: El cliente accede con `https://mi-saas.com/p/:public_token`. Ese token es un UUID inyectado en un custom header o parametrizado para que RLS permita lectura a esa fila específica sin JWT.
4. **Rate Limiting**: `[NO CUBIERTO POR HANDBOOK]` Tuve que inferir la estrategia de Rate Limiting. Cloudflare tiene Rate Limiting en el WAF (capa de firewall) que se configura en el dashboard/Terraform, o requiere implementar lógica manual con Durable Objects / KV, lo cual no está estandarizado en los documentos provistos.
