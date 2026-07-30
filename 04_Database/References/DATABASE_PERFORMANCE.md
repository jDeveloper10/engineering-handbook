---
title: "Performance de Base de Datos"
category: 04_Database
doc_type: referencia
tags: [performance, database, indexes, explain]
summary: "Conceptos para que la base de datos no sea el cuello de botella: cuándo y dónde crear índices, lectura de EXPLAIN ANALYZE, vacuum y bloat, y cómo evitar el problema N+1."
keywords: [performance, database, indexes, explain, base, datos, conceptos, cuello, botella, crear, indices, lectura, analyze, vacuum]
updated: 2026-07-29
status: current
---

# Performance de Base de Datos

Conceptos vitales para evitar que la base de datos sea el cuello de botella.

## 1. Índices: Cuándo y Dónde

**[REQUIRED]** Reglas de oro para crear índices:
1. Toda columna que se use habitualmente en un `WHERE` o un `JOIN`.
2. Toda columna que se use habitualmente para ordenar `ORDER BY`.
3. **No indexes** campos booleanos o con baja cardinalidad (ej. género o status activo/inactivo). Postgres simplemente ignorará el índice porque el "Seq Scan" es más rápido cuando las opciones son tan pocas.

## 2. Explain Analyze (EXPLAIN)

Nunca adivines por qué un query es lento. Usa `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE SELECT id, user_id, status, created_at FROM orders WHERE status = 'shipped';
```

**Lectura Rápida:**
- Si ves `Seq Scan` en una tabla grande: ¡Alerta! Postgres está leyendo fila por fila. Necesitas un índice.
- Si ves `Index Scan` o `Index Only Scan`: Bien hecho, está usando el B-Tree.

## 3. Vacuum y Bloat

Cuando haces un `UPDATE` o `DELETE` en Postgres, la fila vieja no se borra físicamente de inmediato. Se marca como muerta (dead tuple). Esto causa "Table Bloat" (hinchazón).
- Supabase tiene `autovacuum` habilitado por defecto, pero si haces borrados/actualizaciones masivas (millones de filas de un golpe), considera correr un `VACUUM ANALYZE nombre_tabla;` manualmente en horas de bajo tráfico.

## 4. Evitar Select N+1

El problema de llamar a la base de datos dentro de un bucle for.

**[ANTI-PATRÓN]**:
```javascript
const users = await db.getUsers();
for (const user of users) {
  // Hace 100 queries separadas
  const posts = await db.getPostsByUserId(user.id);
}
```

**[REQUIRED]**:
Usa el poder relacional de Supabase JS:
```javascript
const { data } = await supabase
  .from('users')
  .select(`
    id, name,
    posts ( id, title )
  `);
```
