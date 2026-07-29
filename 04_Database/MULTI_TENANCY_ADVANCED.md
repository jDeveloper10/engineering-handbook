---
title: "Estándar Avanzado de Multi-Tenancy y Aislamiento de Datos"
category: 04_Database
tags: [database, multi-tenancy, rls, postgres, supabase, tenant-isolation, white-labeling]
summary: "Estándar para arquitecturas Multi-Tenant: comparación de estrategias (DB per tenant vs Schema vs RLS), políticas de RLS para aislamiento estricto, onboarding automatizado de organizaciones, rate-limiting por tenant y backups isolados."
keywords: [multi-tenancy, tenant, rls, supabase, postgres, tenant-isolation, white-labeling, rate-limiting]
updated: 2026-07-27
status: current
---

# 🏢 ESTÁNDAR AVANZADO DE MULTI-TENANCY Y AISLAMIENTO DE DATOS

## 🎯 OBJETIVO
Definir la arquitectura y los controles de seguridad para servir a múltiples organizaciones o empresas (Tenants) en una sola infraestructura compartida, garantizando la privacidad y el aislamiento absoluto de los datos.

---

## 🎯 REGLAS INQUEBRANTABLES

**TENANT-001: RLS (Row Level Security) es la fuente de verdad inquebrantable para aislamiento.** NUNCA confiar únicamente en la cláusula `WHERE tenant_id = ...` del código de la aplicación.

**TENANT-002: Todo schema multi-tenant DEBE incluir `tenant_id UUID NOT NULL`** en todas las tablas que contengan datos de clientes.

**TENANT-003: Rate Limiting aislado por Tenant.** Un tenant con tráfico masivo o bajo ataque no puede degradar el servicio de los demás tenants (Noisy Neighbor Problem).

---

## 📊 1. COMPARATIVA DE ARQUITECTURAS MULTI-TENANT

| Estrategia | Aislamiento | Costo Infraestructura | Mantenimiento / Migraciones | Recomendación |
|---|---|---|---|---|
| **Database por Tenant** | 🟢 Máximo | 🔴 Muy Alto ($$$) | 🔴 Complejo (N DBs) | Solo Enterprise Dedicado |
| **Schema por Tenant** | 🟡 Alto | 🟡 Medio | 🟡 Complejo | Proyectos Medianos |
| **RLS en Tabla Compartida** | 🟢 Alto (Criptográfico/DB) | 🟢 Mínimo ($) | 🟢 Simple (1 sola DB) | **Estándar por Defecto (`[REQUIRED]`)** |

---

## 🔐 2. POLÍTICAS RLS PARA AISLAMIENTO DE TENANT EN SUPABASE

```sql
-- Función helper para obtener el tenant_id del JWT actual
CREATE OR REPLACE FUNCTION current_tenant_id()
RETURNS UUID AS $$
  SELECT NULLIF(current_setting('request.jwt.claims', true)::json->>'tenant_id', '')::uuid;
$$ LANGUAGE sql STABLE;

-- Aplicación de RLS en tabla compartida 'documents'
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Política de Lectura: El usuario solo ve filas de su propio tenant
CREATE POLICY tenant_isolation_select ON documents
  FOR SELECT
  USING (
    tenant_id = current_tenant_id() AND
    EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.team_id = current_tenant_id()
        AND team_members.user_id = auth.uid()
    )
  );

-- Política de Inserción: Fuerza que el tenant_id coincida con la sesión
CREATE POLICY tenant_isolation_insert ON documents
  FOR INSERT
  WITH CHECK (
    tenant_id = current_tenant_id()
  );
```

---

## 🚀 3. ONBOARDING AUTOMATIZADO DE UN TENANT NUEVO

```typescript
// Worker API: POST /api/tenants/onboard
export async function handleTenantOnboarding(request: Request, env: Env) {
  const { tenantName, adminEmail } = await request.json()

  // 1. Crear registro de Tenant (Team)
  const { data: team, error: teamError } = await supabase
    .from('teams')
    .insert({ name: tenantName, slug: tenantName.toLowerCase().replace(/\s+/g, '-') })
    .select('id')
    .single()

  if (teamError) return fail('ONBOARDING_FAILED', teamError.message, 500)

  // 2. Asignar rol de Owner al administrador
  await supabase.from('team_members').insert({
    team_id: team.id,
    user_id: request.headers.get('x-user-id')!,
    role: 'owner'
  })

  // 3. Poblar datos por defecto (Seed inicial del tenant)
  await supabase.from('documents').insert({
    tenant_id: team.id,
    title: '¡Bienvenido a tu Workspace!',
    content: 'Este es tu primer documento colaborativo.'
  })

  return ok({ tenantId: team.id })
}
```

---

## 📋 CHECKLIST DE MULTI-TENANCY

- [ ] Todas las tablas de datos de clientes contienen `tenant_id UUID NOT NULL`.
- [ ] RLS activo y probado con usuarios de tenants distintos (verificación anti-leak).
- [ ] Función helper `current_tenant_id()` validando claims JWT.
- [ ] Rate Limiting configurado con clave `tenant:${tenantId}`.
