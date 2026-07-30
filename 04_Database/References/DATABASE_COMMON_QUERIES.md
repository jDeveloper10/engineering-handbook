---
title: "Queries Comunes Optimizadas"
category: 04_Database
doc_type: referencia
tags: [sql, postgres, queries, supabase]
summary: "Recetas de SQL y de cliente Supabase para operaciones diarias que suelen implementarse mal: paginación por cursor, búsqueda de texto completo, CTEs y upserts."
keywords: [sql, postgres, queries, supabase, comunes, optimizadas, recetas, cliente, operaciones, diarias, suelen, implementarse, paginacion, cursor]
updated: 2026-07-27
status: current
---

# Queries Comunes Optimizadas

Recetas de SQL y llamadas Supabase JS para operaciones de uso diario que suelen implementarse incorrectamente y afectar el rendimiento.

## 1. Paginación Eficiente (Cursor vs Offset)

**[ANTI-PATRÓN]**: Usar `OFFSET` para saltar muchas páginas (ej. `OFFSET 100000 LIMIT 50`) requiere que Postgres lea todas esas filas descartadas. Es letal en tablas grandes.

**[REQUIRED]** Usar **Cursor-based Pagination** (Keyset pagination) para tablas de alto volumen.

> **DB-001 aplica también aquí.** Estas recetas son las que una IA copia literalmente: cada `SELECT *`
> en un ejemplo se convierte en un `SELECT *` en producción. Columnas explícitas siempre, incluso
> cuando el punto del ejemplo es otro (la paginación).

**Supabase JS:**
```javascript
// Obtener los siguientes 50 a partir del último ID conocido
const { data, error } = await supabase
  .from('users')
  .select('id, email, display_name, created_at') // DB-001: nunca .select('*')
  .gt('id', last_seen_id) // "Greater Than" the last ID
  .order('id', { ascending: true })
  .limit(50);
```

**SQL Directo:**
```sql
SELECT id, email, display_name, created_at
FROM users
WHERE id > 'last_seen_uuid'
ORDER BY id ASC
LIMIT 50;
```

## 2. Búsqueda de Texto (Full-Text Search)

Evita usar `LIKE '%texto%'` para búsquedas en campos largos, ya que no puede usar índices B-Tree normales y forzará un escaneo secuencial.

**Supabase JS (usando Postgres Full Text Search):**
```javascript
const { data, error } = await supabase
  .from('articles')
  .select('title, body')
  .textSearch('title_body_search_vector', 'javascript & react');
```

> *Nota: Requiere configurar previamente una columna generada de tipo `tsvector` y aplicarle un índice `GIN` en la base de datos.*

## 3. CTEs (Common Table Expressions) y Upserts

Si necesitas insertar un registro, o actualizarlo si ya existe (ej. un perfil vinculado a un user_id).

**Supabase JS:**
```javascript
const { data, error } = await supabase
  .from('profiles')
  .upsert({ user_id: '123', name: 'John', updated_at: new Date() })
  .select();
```
*(Asegúrate de que `user_id` sea una Primary Key o tenga un constraint `UNIQUE`).*
