---
title: "Optimización D1 (Base de Datos)"
category: 04_Database
doc_type: estandar
tags: [d1, sqlite, optimización, rendimiento]
summary: "Reglas O-026 en adelante para Cloudflare D1: índices parciales y compuestos con el orden de columnas correcto, vistas materializadas y comportamiento del write-ahead log."
keywords: [d1, sqlite, optimizacion, rendimiento, base, datos, o-026, adelante, cloudflare, indices, parciales, compuestos, orden, columnas]
updated: 2026-07-29
status: current
---

# OPTIMIZACIÓN AVANZADA D1 (Cloudflare Database)

## O-026: Índices Parciales (Indexa solo lo que consultas)

**[RECOMMENDED]** **Por qué:** si las consultas siempre filtran por un subconjunto (registros activos, no borrados), indexar la tabla entera gasta espacio y ralentiza escrituras a cambio de nada. Es recomendado porque exige que el filtro del índice coincida exactamente con el de la consulta: si divergen, el índice deja de usarse en silencio.

```sql
-- ❌ Índice en toda la tabla (gigante, lento, caro)
CREATE INDEX idx_orders_status ON orders(status);
-- Indexa TODAS las filas, incluso las que nunca consultas

-- ✅ Índice parcial: solo filas activas (el 90% de queries)
CREATE INDEX idx_orders_active ON orders(created_at, user_id)
  WHERE status IN ('pending', 'paid', 'shipped');
-- Solo indexa el 10% de las filas = 10x más rápido, 10x menos espacio

-- Índice parcial para búsquedas de texto en productos activos
CREATE INDEX idx_products_search ON products 
  USING GIN(to_tsvector('spanish', name || ' ' || description))
  WHERE deleted_at IS NULL AND stock > 0;

-- Índice parcial para notificaciones no leídas
CREATE INDEX idx_notifications_unread ON notifications(created_at DESC)
  WHERE read_at IS NULL;
```

## O-027: Índices Compuestos Estratégicos (Orden de columnas IMPORTA)

**[REQUIRED]** **Por qué:** un índice compuesto solo sirve desde su primera columna hacia la derecha: el orden correcto es igualdad, luego rango, luego ordenación. Con el orden equivocado el índice existe, ocupa espacio y no se usa — el peor de los dos mundos, y además invisible sin mirar el plan de ejecución.

```sql
-- Regla de oro: columnas de igualdad primero, luego rangos, luego orden

-- Query típica:
SELECT id, user_id, status, total_cents, created_at FROM orders 
WHERE user_id = 'user_123'           -- Igualdad (=)
  AND status = 'paid'                -- Igualdad (=)
  AND created_at > '2024-01-01'      -- Rango (>)
ORDER BY created_at DESC;            -- Orden

-- ✅ Índice perfecto para esta query
CREATE INDEX idx_orders_perfect ON orders(
  user_id,        -- 1. Igualdad
  status,         -- 2. Igualdad
  created_at DESC -- 3. Rango + Orden (mismo campo)
);

-- ❌ Mal orden (el índice no se usa)
CREATE INDEX idx_orders_bad ON orders(
  created_at,     -- Rango primero = índice inútil para filtrar por user_id
  status,
  user_id
);
```

## O-028: Vistas Materializadas (Resultados pre-calculados)

**[RECOMMENDED]** **Por qué:** recalcular la misma agregación en cada visita de un panel es trabajo repetido que en D1 se paga por fila leída. Es recomendado porque introduce desfase: los datos son de la última actualización, y no todo caso de uso lo tolera.

```sql
-- ❌ Calcular dashboard cada vez (query pesada cada 5 segundos)
SELECT 
  status,
  COUNT(*) as total,
  SUM(total_cents) as revenue
FROM orders
WHERE created_at > now() - interval '30 days'
GROUP BY status;

-- ✅ Vista materializada (calculada 1 vez, leída 1000 veces)
CREATE MATERIALIZED VIEW dashboard_30days AS
SELECT 
  status,
  COUNT(*) as total,
  SUM(total_cents) as revenue
FROM orders
WHERE created_at > now() - interval '30 days'
GROUP BY status;

-- Crear índice en la vista materializada
CREATE UNIQUE INDEX idx_dashboard_status ON dashboard_30days(status);

-- Refrescar cada 5 minutos
SELECT cron.schedule('refresh-dashboard', '*/5 * * * *', 
  'REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_30days'
);

-- Consultar la vista (instantáneo, sin cálculos)
SELECT day, orders_count, revenue_cents FROM dashboard_30days WHERE status = 'paid';
```

## O-029: WAL (Write-Ahead Log) y Performance

**[RECOMMENDED]** **Por qué:** el registro de escritura anticipada permite que las lecturas no se bloqueen con las escrituras, que es el patrón dominante en una aplicación web. Entender su comportamiento evita atribuir a la consulta una lentitud que en realidad es contención.

```sql
-- D1 usa SQLite, que tiene WAL mode por defecto
-- Pero hay optimizaciones que puedes hacer:

-- 1. Transacciones en batch (NO una por una)
-- ❌ 1000 inserts individuales = 1000 escrituras WAL
for (const item of items) {
  await db.execute('INSERT INTO order_items (order_id, name, price) VALUES (?, ?, ?)', 
    [orderId, item.name, item.price]
  )
}

-- ✅ 1 transacción = 1 escritura WAL
BEGIN;
  INSERT INTO order_items (order_id, name, price) VALUES (?, ?, ?), (?, ?, ?), ...;
COMMIT;

-- 2. Configurar synchronous = NORMAL (no FULL)
-- En D1 no puedes cambiarlo, pero en SQLite local sí:
PRAGMA synchronous = NORMAL;  -- Menos fsync = más rápido
PRAGMA journal_mode = WAL;     -- WAL mode = lecturas no bloquean escrituras
PRAGMA cache_size = -64000;    -- 64MB de caché
PRAGMA temp_store = MEMORY;    -- Temporales en memoria
```

## O-030: Evitar Escrituras Fantasma (Useless writes)

**[REQUIRED]** **Por qué:** en D1 cada fila escrita cuesta dinero y provoca invalidación de caché, así que escribir un valor idéntico al que ya estaba es puro desperdicio con efecto secundario. Comprobar antes de escribir es más barato que la escritura que se evita.

```sql
-- ❌ UPDATE aunque no cambie nada (escritura innecesaria)
UPDATE users SET email = 'same@email.com' WHERE id = 'user_123';
-- Aunque el email no cambió, D1 escribe en WAL = costo

-- ✅ Solo UPDATE si realmente cambió
UPDATE users 
SET email = 'new@email.com',
    updated_at = now()
WHERE id = 'user_123' 
  AND email IS DISTINCT FROM 'new@email.com';  -- Solo si es diferente

-- ❌ Contador con SELECT + UPDATE (race condition + 2 queries)
const { count } = await db.query('SELECT view_count FROM posts WHERE id = ?', [postId])
await db.query('UPDATE posts SET view_count = ? WHERE id = ?', [count + 1, postId])

-- ✅ UPDATE atómico (1 query, sin race condition)
UPDATE posts SET view_count = view_count + 1 WHERE id = ?;
```

## O-031: D1 + DO (Durable Objects) para hotspots

**[RECOMMENDED]** **Por qué:** cuando muchas peticiones compiten por la misma fila, la base de datos se convierte en el punto de contención y ninguna optimización de consulta lo arregla. Un Durable Object serializa ese acceso en memoria. Es recomendado porque añade un componente con estado, y solo compensa cuando el hotspot está medido.

```typescript
// Problema: Contador de visitas en D1
// 1000 visitas/segundo = 1000 writes/segundo en D1 = CARO

// Solución: Durable Object absorbe writes, persiste a D1 cada 10 segundos

export class VisitCounter {
  private visits: Map<string, number> = new Map()
  
  async increment(postId: string): Promise<number> {
    const current = this.visits.get(postId) || 0
    this.visits.set(postId, current + 1)
    return current + 1
  }
  
  async flush() {
    // Persistir a D1 cada 10 segundos
    for (const [postId, count] of this.visits) {
      await db.execute(
        'UPDATE posts SET view_count = view_count + ? WHERE id = ?',
        [count, postId]
      )
    }
    this.visits.clear()
  }
}
```
