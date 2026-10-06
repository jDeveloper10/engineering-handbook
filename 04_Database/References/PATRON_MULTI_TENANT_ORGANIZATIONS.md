---
title: "Patrón de Arquitectura Multi-Tenant (Organizaciones y Equipos)"
category: 04_Database
doc_type: patron
tags: [database, multi-tenant, rls, organizaciones, tenant-isolation, b2b, supabase]
summary: "Esquema y arquitectura estándar para aplicaciones SaaS B2B Multi-tenant: tabla de organizaciones (tenants), miembros con roles, invitaciones con token seguro e inquebrantable aislamiento de datos por RLS (TENANT-001)."
keywords: [multi-tenant, tenant-isolation, organizaciones, saas, b2b, rls, supabase, invitaciones]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "04_Database/DATABASE_ENGINEERING_STANDARD.md"
  - "04_Database/References/PATRON_RBAC_PERMISOS.md"
---

# PATRÓN DE ARQUITECTURA MULTI-TENANT (ORGANIZACIONES)

> 🏢 **Regla Inquebrantable (`TENANT-001`):** En una plataforma multi-tenant, un cliente o empresa NUNCA debe poder ver, modificar ni inferir la existencia de los datos de otra empresa. El aislamiento reside en **Row Level Security (RLS)** a nivel de base de datos, no en filtros manuales de frontend.

---

## 1. Esquema SQL Estándar Multi-Tenant

```sql
-- 1. Tabla de Organizaciones / Empresas (Tenants)
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL, -- ej. 'acme-corp' para subdominios o URLs
    plan TEXT NOT NULL DEFAULT 'starter',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Tabla de Membresías (Usuarios dentro de Organizaciones)
CREATE TABLE IF NOT EXISTS public.organization_members (
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'billing')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_user_id ON public.organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_org_id ON public.organization_members(organization_id);

-- 3. Tabla de Invitaciones de Equipo (AUTH-004: TTL 48h y token revocable)
CREATE TABLE IF NOT EXISTS public.organization_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '48 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 2. Tablas de Negocio con `organization_id` Obligatorio

**[REQUIRED]** Toda tabla de negocio (proyectos, clientes, facturas, productos) DEBE incluir la columna `organization_id` y su índice secundario (`DB-002`):

```sql
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_organization_id ON public.projects(organization_id);
```

---

## 3. Función Helper y Políticas RLS de Aislamiento Estricto

```sql
-- 1. Helper: Obtener los IDs de organizaciones a los que pertenece el usuario autenticado
CREATE OR REPLACE FUNCTION public.get_user_organizations()
RETURNS TABLE (org_id UUID) AS $$
BEGIN
  RETURN QUERY
  SELECT organization_id
  FROM public.organization_members
  WHERE user_id = auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- 2. Habilitar RLS en tablas de negocio
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

-- 3. Política RLS: El usuario solo puede consultar o modificar datos de sus organizaciones
CREATE POLICY "Aislamiento multi-tenant de proyectos" ON public.projects
FOR ALL USING (
  organization_id IN (SELECT org_id FROM public.get_user_organizations())
);
```
