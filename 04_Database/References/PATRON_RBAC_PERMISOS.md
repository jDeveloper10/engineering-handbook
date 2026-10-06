---
title: "Patrón Oficial de Roles y Permisos (RBAC Multi-tenant)"
category: 04_Database
doc_type: patron
tags: [database, postgres, supabase, rbac, roles, permisos, multi-tenant, rls]
summary: "Esquema SQL y patrón reutilizable de control de acceso basado en roles (RBAC) para PostgreSQL y Supabase. Incluye tablas de roles, permisos, asignación de usuarios y funciones de verificación para RLS (has_permission)."
keywords: [rbac, roles, permisos, supabase, postgres, rls, multi-tenant, autorizacion]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "04_Database/References/RLS_POLICIES_LIBRARY.md"
  - "04_Database/DATABASE_ENGINEERING_STANDARD.md"
---

# PATRÓN OFICIAL DE ROLES Y PERMISOS (RBAC)

> 🔐 **Objetivo:** Un esquema SQL universal y reutilizable para gestionar permisos granulares (*Admin, Manager, Operador, Cliente*) en cualquier proyecto de la agencia, blindado por Row Level Security (RLS) en la base de datos.

---

## 1. Esquema SQL Estándar de RBAC

```sql
-- 1. Tabla de Roles del Sistema
CREATE TABLE IF NOT EXISTS public.roles (
    id TEXT PRIMARY KEY, -- 'admin', 'manager', 'operator', 'client'
    description TEXT NOT NULL
);

-- 2. Tabla de Permisos Granulares
CREATE TABLE IF NOT EXISTS public.permissions (
    id TEXT PRIMARY KEY, -- 'orders.create', 'orders.read', 'orders.delete', 'users.manage'
    description TEXT NOT NULL
);

-- 3. Tabla Intermedia: Permisos por Rol
CREATE TABLE IF NOT EXISTS public.role_permissions (
    role_id TEXT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id TEXT NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- 4. Asignación de Roles a Usuarios
CREATE TABLE IF NOT EXISTS public.user_roles (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id TEXT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    org_id UUID, -- Opcional para aplicaciones multi-empresa
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON public.user_roles(user_id);
```

---

## 2. Función Helper de Verificación de Permisos en RLS

**[REQUIRED]** Esta función se ejecuta dentro de las políticas RLS para verificar si el usuario logueado tiene el permiso requerido:

```sql
CREATE OR REPLACE FUNCTION public.has_permission(required_permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM public.user_roles ur
    JOIN public.role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
      AND rp.permission_id = required_permission
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;
```

---

## 3. Ejemplo de Uso en Políticas RLS

```sql
-- Habilitar RLS
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- 1. Política de Lectura: El usuario ve sus propias órdenes O un usuario con permiso 'orders.read' ve todas
CREATE POLICY "Lectura de ordenes" ON public.orders
FOR SELECT USING (
  auth.uid() = user_id OR public.has_permission('orders.read')
);

-- 2. Política de Eliminación: Solo usuarios con permiso 'orders.delete'
CREATE POLICY "Eliminacion de ordenes" ON public.orders
FOR DELETE USING (
  public.has_permission('orders.delete')
);
```
