---
title: "Recetas de Migraciones de Base de Datos"
category: 04_Database
doc_type: referencia
tags: [migrations, sql, supabase, zero-downtime]
summary: "Recetas de migración sin downtime: añadir una columna obligatoria, renombrar una columna y crear índices de forma segura sobre tablas en producción."
keywords: [migrations, sql, supabase, zero-downtime, recetas, migraciones, base, datos, migracion, downtime, anadir, columna, obligatoria, renombrar]
updated: 2026-07-27
status: current
---

# 🔄 Recetas de Migraciones

Las migraciones en Supabase/Postgres pueden romper el entorno de producción si no se hacen con cuidado. Estas recetas aseguran **Zero-Downtime Migrations**.

## 1. Añadir una Columna Obligatoria (`NOT NULL`)

**[PELIGRO]**: Si haces `ALTER TABLE ... ADD COLUMN ... NOT NULL` en una tabla con millones de filas, Postgres reescribirá la tabla entera y bloqueará las escrituras, causando caída de la API.

**[REQUIRED] Receta Segura:**
1. Añadir la columna admitiendo nulos.
   ```sql
   ALTER TABLE users ADD COLUMN age INT;
   ```
2. Actualizar las filas existentes (en lotes si son millones).
   ```sql
   UPDATE users SET age = 18 WHERE age IS NULL;
   ```
3. Añadir el constraint de `NOT NULL`.
   ```sql
   ALTER TABLE users ALTER COLUMN age SET NOT NULL;
   ```

## 2. Renombrar una Columna (Zero-Downtime)

Si renombras una columna con `ALTER TABLE RENAME`, el código backend viejo fallará al intentar leerla hasta que el nuevo deploy finalice.

**[REQUIRED] Receta Segura:**
1. Crea la nueva columna.
   ```sql
   ALTER TABLE users ADD COLUMN full_name TEXT;
   ```
2. Sincroniza los datos con un Trigger, para que cada inserto en `old_name` vaya a `full_name`.
3. Haz el deploy del código para que lea y escriba en `full_name`.
4. Borra la columna vieja `old_name` en una migración futura.

## 3. Crear Índices de Forma Segura

Crear un índice normal bloquea las escrituras en la tabla hasta que el índice termine de construirse.

**[REQUIRED] Receta Segura:**
Siempre usa `CONCURRENTLY` para crear índices en producción.
```sql
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```
*(Nota: No se puede usar `CONCURRENTLY` dentro de una transacción `BEGIN ... COMMIT`).*
