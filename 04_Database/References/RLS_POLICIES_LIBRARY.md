---
title: "Librería de Políticas RLS"
category: 04_Database
tags: [rls, security, supabase, postgres]
status: current
---

# 🔒 Librería de Políticas RLS (Supabase)

Las políticas Row Level Security (RLS) son el corazón de la seguridad en Supabase, permitiendo que la base de datos separe la data por usuario. 
Aquí tienes las políticas más comunes listas para copiar, pegar y adaptar.

## 1. Permitir a los usuarios leer/escribir SOLO su propia información

Ideal para tablas como `profiles`, `user_settings`, `personal_notes`. Requiere que la tabla tenga una columna (ej. `user_id`) que guarde el ID de autenticación.

```sql
-- Activar RLS en la tabla
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 1. READ: Solo el dueño puede leer
CREATE POLICY "Users can view own profile" 
ON public.profiles FOR SELECT
USING ( auth.uid() = user_id );

-- 2. INSERT: Solo el dueño puede insertar un registro consigo mismo como user_id
CREATE POLICY "Users can insert own profile" 
ON public.profiles FOR INSERT
WITH CHECK ( auth.uid() = user_id );

-- 3. UPDATE: Solo el dueño puede actualizar su propia fila
CREATE POLICY "Users can update own profile" 
ON public.profiles FOR UPDATE
USING ( auth.uid() = user_id )
WITH CHECK ( auth.uid() = user_id );
```

## 2. Lectura Pública, Escritura Privada (Propietario)

Ideal para tablas como `posts`, `public_comments`, `products`, donde todos (incluso anónimos o usuarios logueados que no son el autor) pueden ver, pero solo el autor original puede editar o borrar.

```sql
ALTER TABLE public.posts ENABLE ROW LEVEL SECURITY;

-- 1. READ: Cualquiera (incluido anon) puede leer
CREATE POLICY "Everyone can view posts" 
ON public.posts FOR SELECT
USING ( true );

-- 2. INSERT: Solo usuarios logueados pueden crear
CREATE POLICY "Authenticated users can create posts" 
ON public.posts FOR INSERT
TO authenticated
WITH CHECK ( auth.uid() = author_id );

-- 3. UPDATE/DELETE: Solo el dueño
CREATE POLICY "Users can update their own posts" 
ON public.posts FOR UPDATE
USING ( auth.uid() = author_id );
```

## 3. Acceso Basado en Roles (RBAC)

Si tienes una tabla `user_roles` o verificas roles en el JWT custom. En este ejemplo, asumimos una función de base de datos `is_admin()`.

```sql
-- READ: Solo usuarios admin pueden leer esta tabla
CREATE POLICY "Solo admins ven la tabla secreta"
ON public.secret_data FOR SELECT
USING ( is_admin() = true );
```
*(Asegúrate de que la función `is_admin()` esté bien definida y con `SECURITY DEFINER` si debe saltar RLS internamente para verificar roles).*
