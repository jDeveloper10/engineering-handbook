---
title: "Estándar Maestro de Optimización de Consultas SQL y Rendimiento de Base de Datos"
category: 04_Database
doc_type: estandar
tags: [database, sql, postgres, optimizacion, indices, explain-analyze, cursor-pagination, n1, performance]
summary: "Guía definitiva y reglas de optimización de consultas SQL en PostgreSQL, Supabase y D1: eliminación de SELECT *, índices compuestos y parciales, paginación por cursor, eliminación del problema N+1 con JSON relacional, lectura de EXPLAIN (ANALYZE, BUFFERS) y conteos rápidos."
keywords: [optimizacion-sql, indices, explain-analyze, seq-scan, index-only-scan, n1-problem, cursor-pagination, postgres, supabase, d1]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "04_Database/DATABASE_ENGINEERING_STANDARD.md"
  - "04_Database/References/DATABASE_PERFORMANCE.md"
  - "04_Database/References/DATABASE_COMMON_QUERIES.md"
---

# ESTÁNDAR MAESTRO DE OPTIMIZACIÓN DE CONSULTAS SQL

> ⚡ **Regla de Rendimiento #1:** El 95% de la lentitud de una aplicación no está en el backend ni en el frontend, sino en **consultas SQL mal escritas, escaneos secuenciales innecesarios (`Seq Scan`) o falta de índices estratégicos**.

---

## 1. Las 7 Leyes Inquebrantables de Optimización

| ID de Regla | Anti-Patrón (Lento / Peligroso) | Solución Optimizada (Rápida / Eficiente) |
|---|---|---|
| **DB-001** | `SELECT` con comodín `*` | `SELECT id, name, created_at` (Columnas Explícitas) |
| **DB-002** | Claves Foráneas (FK) sin índice secundario | `CREATE INDEX idx_orders_user_id ON orders(user_id)` |
| **DB-IDX-002** | Indexar toda la tabla completa | Índices Parciales (`CREATE INDEX ... WHERE status = 'pending'`) |
| **DB-PAG-001** | Paginación `LIMIT 50 OFFSET 100000` | Paginación por Cursor Keyset (`WHERE id > last_id`) |
| **DB-N1-001** | Bucle for con consulta adentro | Joins relacionales o `json_agg()` en 1 sola consulta |
| **DB-FTS-001** | Búsqueda `WHERE name LIKE '%juan%'` | Índices GIN con `pg_trgm` o vectores `tsvector` |
| **DB-CNT-001** | `SELECT COUNT(*)` en tablas millonarias | Tablas contadoras con triggers o `reltuples` de Postgres |

---

## 2. Índices Estratégicos: B-Tree, Compuestos y Parciales

### A. Índices Parciales (`DB-IDX-002`) — Ahorra hasta 80% de RAM
Si consultas frecuentemente filas con un estado específico (ej. órdenes pendientes o usuarios activos), **no indexes toda la tabla**. Indexa solo el subconjunto:

```sql
-- ❌ INEFICIENTE: Indexa millones de órdenes ya completadas o archivadas
CREATE INDEX idx_orders_status ON orders(status);

-- ✅ OPTIMIZADO (Índice Parcial): Solo pesa unos pocos Kilobytes en memoria
CREATE INDEX idx_orders_pending ON orders(user_id, created_at)
WHERE status = 'pending';
```

---

### B. Índices Compuestos y la Regla del Prefijo Izquierdo
Cuando filtras por múltiples columnas (`WHERE tenant_id = X AND created_at > Y`), crea un índice compuesto ordenado por **Igualdad primero, Rango después**:

```sql
-- Orden óptimo: (Igualdad, Rango)
CREATE INDEX idx_tenant_orders ON orders(tenant_id, created_at DESC);
```

---

## 3. Paginación por Cursor (Keyset) vs. Muerte por `OFFSET`

### ¿Por qué `OFFSET` destruye el rendimiento?
Con `OFFSET 100000 LIMIT 20`, PostgreSQL tiene que leer y procesar 100,020 filas en disco para luego descartar las primeras 100,000.

### Implementación Óptima por Cursor (`DB-PAG-001`):
```sql
-- ✅ TIEMPO CONSTANTE (< 2ms sin importar si estás en la página 1 o en la 50,000):
SELECT id, title, amount_cents, created_at
FROM orders
WHERE tenant_id = 'tenant-uuid' 
  AND created_at < '2026-08-01T12:00:00Z' -- Último timestamp visto
ORDER BY created_at DESC
LIMIT 20;
```

---

## 4. Eliminación Radical del Problema N+1 con Agregaciones JSON

**[ANTI-PATRÓN N+1]**: Consultar clientes y luego en un bucle hacer 1 consulta de pedidos por cada cliente (100 clientes = 101 consultas a BD).

### Solución en 1 Sola Consulta con `json_agg()` en PostgreSQL:
```sql
-- ✅ 1 SOLA CONSULTA QUE TRAE TODO EL ÁRBOL RELACIONAL:
SELECT 
    u.id,
    u.email,
    COALESCE(
        json_agg(
            json_build_object(
                'id', o.id,
                'amount_cents', o.amount_cents,
                'status', o.status
            )
        ) FILTER (WHERE o.id IS NOT NULL), '[]'
    ) AS recent_orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.created_at > (now() - INTERVAL '30 days')
WHERE u.organization_id = 'org-uuid'
GROUP BY u.id, u.email;
```

---

## 5. Cómo Interpretar `EXPLAIN (ANALYZE, BUFFERS)`

**[REQUIRED]** Antes de declarar una consulta como lista para producción, ejecútala con `EXPLAIN (ANALYZE, BUFFERS)` en el editor SQL:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, email, created_at 
FROM users 
WHERE organization_id = 'a7c8...' AND is_active = true;
```

### Tabla de Diagnóstico Rápido:

| Salida en el Plan | Diagnóstico | Acción Correctiva |
|---|---|---|
| **`Seq Scan`** | 🔴 Escaneo secuencial (leyendo todo el disco). | Crear un índice en la columna del `WHERE`. |
| **`Index Scan`** | 🟡 Lee el índice y luego va a la tabla por las columnas. | Normal y aceptable para la mayoría de consultas. |
| **`Index Only Scan`** | 🟢 **El Santo Grial.** Todas las columnas pedidas están en el índice; cero accesos a la tabla. | Añadir columnas de salida con `INCLUDE (col1, col2)`. |
| **`Buffers: shared read=...`** | ⚠️ Leyendo de disco mecánico/SSD lento. | Ajustar RAM o reducir el tamaño del índice. |
| **`Buffers: shared hit=...`** | 🟢 Leyendo directamente de la memoria RAM (Caché). | Excelente rendimiento. |

---

## 6. Conteos Rápidos en Tablas con Millones de Filas

Hacer `SELECT COUNT(*)` en una tabla de 10 millones de filas bloquea CPU porque Postgres debe verificar la visibilidad MVCC de cada fila.

### Soluciones Optimizadas:

1. **Conteo Instantáneo Estimado (< 1ms para métricas de panel):**
   ```sql
   SELECT reltuples::BIGINT AS estimated_count 
   FROM pg_class 
   WHERE relname = 'orders';
   ```

2. **Tabla de Contadores (Counter Table con Trigger):**
   Mantener una tabla `tenant_stats (tenant_id, total_orders)` que se actualiza con triggers `+1` / `-1` en cada inserción o borrado.
