---
title: "Estándar de Escalabilidad de Base de Datos"
category: 04_Database
doc_type: estandar
tags: [postgresql, escalabilidad, rendimiento, integridad]
summary: "Reglas DB-010 a DB-025 sobre los cuatro pilares de una base de datos escalable: esquema sin huecos, rendimiento quirúrgico, integridad absoluta y operabilidad."
keywords: [postgresql, escalabilidad, rendimiento, integridad, base, datos, db-010, db-025, cuatro, pilares, escalable, esquema, huecos, quirurgico]
updated: 2026-07-27
status: current
---

# Estándar de Escalabilidad de Base de Datos (DB-010 a DB-025)

Las siguientes reglas son de hierro para garantizar bases de datos robustas, escalables y sin huecos, independientemente del motor o plataforma (PostgreSQL, Supabase, MySQL). 

## 🎯 LOS 4 PILARES DE UNA BASE DE DATOS INDESTRUCTIBLE

1. **ESQUEMA BLINDADO** → Sin huecos estructurales
2. **RENDIMIENTO QUIRÚRGICO** → Escala sin degradarse
3. **INTEGRIDAD ABSOLUTA** → Datos consistentes SIEMPRE
4. **OPERABILIDAD** → Migraciones, backups, rollbacks

---

## 📐 PILAR 1: ESQUEMA BLINDADO (Sin Huecos)

### DB-010: NUNCA CONFIAR EN LA APLICACIÓN PARA VALIDAR

**[REQUIRED]** **Por qué:** la aplicación cambia, se reescribe y gana rutas de acceso nuevas (un script de migración, un panel de administración, una integración); el esquema sobrevive a todas ellas. Una restricción que solo vive en el código se salta el día que alguien escribe en la tabla sin pasar por ese código.

La base de datos es la última línea de defensa. NUNCA asumas que el backend o el frontend validaron los datos correctamente.

**❌ Horrible (Hueco gigante):**
```sql
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,  -- Puede ser NULL, FK sin índice
  total TEXT,        -- TEXT para dinero = pesadilla
  status TEXT,       -- Cualquier string = caos
  created_at TEXT    -- TEXT para fecha = sin timezone
);
```

**✅ Indestructible:**
```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  total_cents BIGINT NOT NULL CHECK (total_cents >= 0),
  status order_status NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  CONSTRAINT fk_orders_user 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE RESTRICT -- NUNCA CASCADE para datos críticos
);

-- Enum para estados (no strings libres)
CREATE TYPE order_status AS ENUM (
  'draft', 'pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded'
);

-- Índice SIEMPRE en FK
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### DB-011: CONSTRAINTS CHECK PARA TODO LO VALIDABLE

**[REQUIRED]** **Por qué:** un CHECK convierte un dato imposible en un error inmediato en vez de en una fila corrupta que se descubre meses después, cuando ya contaminó informes y decisiones. Limpiar datos malos a posteriori cuesta órdenes de magnitud más que impedir su entrada.

**✅ Blindado con CHECK:**
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL CHECK (length(name) BETWEEN 3 AND 200),
  price_cents BIGINT NOT NULL CHECK (price_cents > 0),
  stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
  email TEXT NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  discount_percent INTEGER CHECK (discount_percent BETWEEN 0 AND 100),
  sku TEXT NOT NULL UNIQUE CHECK (length(sku) = 10)
);
```

### DB-012: ENUMS + CHECK CONSTRAINTS = COMBO PERFECTO

**[RECOMMENDED]** **Por qué:** el ENUM documenta el dominio de valores dentro del propio esquema y el CHECK cubre las combinaciones que el ENUM no puede expresar. Se marca como recomendado porque añadir un valor a un ENUM de PostgreSQL requiere migración, y en dominios que cambian rápido una tabla de catálogo con FK envejece mejor.

Ideal para tablas de auditoría.
```sql
CREATE TYPE audit_action AS ENUM ('INSERT', 'UPDATE', 'DELETE', 'RESTORE');

CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  action audit_action NOT NULL,
  old_data JSONB,
  new_data JSONB,
  changed_by UUID NOT NULL REFERENCES users(id),
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Cada registro de auditoría debe tener datos
  CHECK (old_data IS NOT NULL OR new_data IS NOT NULL)
);
```

### DB-013: PARTICIONAMIENTO ANTES DE QUE DUELA

**[RECOMMENDED]** **Por qué:** particionar una tabla que ya tiene millones de filas exige ventana de mantenimiento; hacerlo desde el principio es gratis. Es recomendado y no obligatorio porque particionar una tabla que nunca crecerá añade complejidad operativa sin devolver nada: la decisión depende del volumen previsto, no del gusto.

Para tablas de alta mutación (logs, eventos) que llegarán a millones de filas.

```sql
CREATE TABLE events (
  id UUID DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  PRIMARY KEY (id, created_at) -- La clave de partición DEBE estar en PK
) PARTITION BY RANGE (created_at);

-- Crear función automatizada de particiones
CREATE OR REPLACE FUNCTION create_monthly_partition() RETURNS void AS $$ ... $$;
-- Programar con pg_cron
SELECT cron.schedule('create-partitions', '0 0 1 * *', 'SELECT create_monthly_partition()');
```

---

## ⚡ PILAR 2: RENDIMIENTO QUIRÚRGICO

### DB-014: ÍNDICES QUE REALMENTE IMPORTAN

**[REQUIRED]** **Por qué:** cada índice acelera lecturas y penaliza cada escritura, además de ocupar disco y memoria. Indexar por reflejo produce tablas donde escribir es lento y donde el planificador tiene demasiadas opciones malas. El índice se justifica con una consulta real, no con una intuición.

```sql
-- 1. Índice compuesto para queries comunes
CREATE INDEX idx_orders_user_status_created 
  ON orders(user_id, status, created_at DESC);

-- 2. Índice parcial (indexar solo lo activo, que es el 90% de las queries)
CREATE INDEX idx_orders_active 
  ON orders(created_at) WHERE status IN ('pending', 'paid', 'shipped');

-- 3. Índice covering (incluye columnas para no leer la tabla real)
CREATE INDEX idx_orders_covering 
  ON orders(user_id, status) INCLUDE (total_cents, created_at);

-- 4. Índice GIN para JSONB
CREATE INDEX idx_events_payload ON events USING GIN(payload jsonb_path_ops);
```

### DB-015: EXPLAIN ANALYZE ANTES DE CADA DEPLOY

**[REQUIRED]** **Por qué:** una consulta se comporta distinto con mil filas que con un millón, y el entorno de desarrollo casi siempre tiene mil. `EXPLAIN ANALYZE` es la única forma de ver el plan real en vez de suponerlo, y detecta el `Seq Scan` que en producción se traduce en un incidente.

**NUNCA** deployar una query compleja en producción sin antes evaluarla localmente con `EXPLAIN ANALYZE`. Evalúa si estás causando un `Seq Scan` evitable.

### DB-016: CONNECTION POOLING OBLIGATORIO (Y LA DIFERENCIA CON POLLING)

**[REQUIRED]** **Por qué:** PostgreSQL asigna un proceso por conexión, así que el límite se agota mucho antes de lo que la intuición sugiere — y en un entorno serverless, donde cada invocación puede abrir la suya, se agota en minutos. Sin pooling, el modo de fallo no es lentitud: es la base entera rechazando conexiones.

> [!CAUTION]
> **POLLING vs POOLING: ¡NO SON LO MISMO!**
> 
> **POLLING (Odioso e ineficiente)**: Un bucle `setInterval` preguntando a la API "¿ya cambió? ¿ya cambió?". Destruye la batería y satura el servidor con requests basura. **ESTÁ PROHIBIDO**. Usa WebSockets, SSE o Supabase Realtime en su lugar.
> 
> **POOLING (Elegante y obligatorio)**: Mantener un conjunto de conexiones de base de datos *ya abiertas* listas para reutilizarse. Evita el altísimo costo de crear y destruir conexiones TCP para cada query.

**✅ PgBouncer + Pool configurado:**
```javascript
import { Pool } from 'pg'
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,           // Máximo 20 conexiones REUTILIZABLES
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
})

const client = await pool.connect()
try {
  await client.query('BEGIN')
  // ...
  await client.query('COMMIT')
} finally {
  client.release() // LIBERAR AL POOL, NUNCA CERRAR DE GOLPE
}
```

### DB-017: PAGINACIÓN CON CURSORES, NUNCA OFFSET

**[REQUIRED]** **Por qué:** `OFFSET` obliga al motor a leer y descartar todas las filas anteriores, de modo que el coste crece con el número de página: la última página de un listado grande es la consulta más cara del sistema. El cursor va directo al punto y su coste es constante.

`OFFSET` escanea y descarta todas las filas previas. En bases de datos grandes, esto colapsa la CPU.

```sql
-- ✅ CURSOR (va directo al punto usando índice)
-- DB-001: columnas explícitas incluso en ejemplos de paginación — el `SELECT *` de un
-- ejemplo termina copiado en producción tal cual.
SELECT id, user_id, total_cents, currency, status, created_at
FROM orders
WHERE created_at < '2024-01-15T10:30:00Z'
ORDER BY created_at DESC LIMIT 20;
```

---

## 🔒 PILAR 3: INTEGRIDAD ABSOLUTA

### DB-018: TRANSACCIONES CON SAVEPOINT

**[RECOMMENDED]** **Por qué:** en una carga masiva, un único registro inválido no debería tirar el lote completo. El SAVEPOINT permite descartar solo lo que falló. Es recomendado porque en operaciones donde la atomicidad total es el requisito (un cobro, una transferencia), el comportamiento correcto es justamente el contrario: todo o nada.

Si haces inserts masivos y falla un registro, un SAVEPOINT evita descartar todo el lote.

```sql
BEGIN;
SAVEPOINT batch_1;
INSERT INTO order_items VALUES ...; -- 10 filas
SAVEPOINT batch_2;
INSERT INTO order_items VALUES ...; -- 10 filas
-- Si falla batch_3:
ROLLBACK TO SAVEPOINT batch_2; -- Solo pierdes las últimas 10
COMMIT; -- Guardas las primeras 20
```

### DB-019: SOFT DELETE + HARD DELETE PROGRAMADO

**[REQUIRED]** **Por qué:** el borrado accidental es la pérdida de datos más común, y sin soft delete la única recuperación es restaurar un backup completo. Pero conservarlo indefinidamente choca con el derecho de supresión del RGPD: por eso el par completo, marcado lógico más purga programada, no solo la primera mitad.

```sql
-- Soft Delete: Ocultarlo
ALTER TABLE orders ADD COLUMN deleted_at TIMESTAMPTZ;
UPDATE orders SET deleted_at = now() WHERE id = '123';

-- Política RLS
CREATE POLICY "Solo ver activos" ON orders FOR SELECT USING (deleted_at IS NULL);

-- Purga (Hard Delete) diferida (Borrar todo lo mayor a 90 días)
SELECT cron.schedule('purge-deleted', '0 3 * * 0', $$
  DELETE FROM orders WHERE deleted_at < now() - interval '90 days'
$$);
```

### DB-020: VERSIONADO DE REGISTROS (HISTORIAL)

**[RECOMMENDED]** **Por qué:** saber quién cambió qué y cuándo es imprescindible para auditoría y para resolver disputas, y un trigger lo garantiza aunque el cambio venga por una vía que no pasa por la aplicación. Es recomendado porque duplica el volumen escrito: se aplica a los registros con valor legal o económico, no a todos.

Si cambian las propuestas, guarda el histórico usando Triggers de base de datos.
*(Ver sección de triggers de PostgreSQL en la implementación de la regla)*

### DB-021: INTEGRIDAD REFERENCIAL EN CASCADA CONTROLADA

**[REQUIRED]** **Por qué:** la acción de la clave foránea se elige, nunca se acepta por defecto sin pensarla: un `CASCADE` puesto por comodidad convierte el borrado de una fila en el borrado silencioso de miles. `RESTRICT` falla ruidosamente, que es el comportamiento correcto cuando no se ha decidido nada.

- `RESTRICT` (Por Defecto): No deja borrar si hay dependencias (ej. usuarios, productos).
- `SET NULL`: Deja el registro hijo vivo pero anula la FK (ej. categorías borradas).
- `CASCADE`: Solo para datos NO críticos o transitorios (ej. sesiones, items que no tienen sentido sin el padre).

---

## 🛠️ PILAR 4: OPERABILIDAD

### DB-022: MIGRACIONES CON UP Y DOWN TESTEADO

**[REQUIRED]** **Por qué:** el momento en que se necesita el `DOWN` es siempre el peor posible: producción rota y con prisa. Escribirlo entonces garantiza escribirlo mal. Y un `DOWN` que nunca se ejecutó no es un plan de reversión, es una suposición.

Toda migración debe contener ambas vías. No confíes en "hago otra migración para arreglarlo" durante un incidente.

### DB-023: BACKUPS AUTOMATIZADOS + VERIFICACIÓN

**[REQUIRED]** **Por qué:** un backup que nunca se ha restaurado no se sabe si es un backup — sabotea desde un dump truncado hasta un cifrado cuya clave se perdió. La restauración periódica es lo que convierte una suposición en una garantía, y es la mitad que casi todo el mundo se salta.

Un backup que no ha sido probado no es un backup. Automatizar `pg_dump`, restaurarlo internamente con `pg_restore` temporal para validar y mandarlo a un bucket R2.

### DB-024: RÉPLICAS DE LECTURA PARA QUERIES PESADAS

**[RECOMMENDED]** **Por qué:** separar informes pesados del tráfico transaccional evita que un dashboard tumbe la aplicación. Es recomendado porque introduce retraso de replicación: leer de la réplica justo después de escribir devuelve datos viejos, y no todo flujo lo tolera.

Separa la carga configurando un Pool primario (Write) y un Pool réplica (Read) si la infraestructura de Supabase lo permite.

### DB-025: MONITOREO DE RENDIMIENTO CONTINUO

**[RECOMMENDED]** **Por qué:** la degradación de una base de datos es gradual y silenciosa: nadie nota el índice que dejó de usarse hasta que la consulta tarda diez segundos. Vigilar las estadísticas del motor convierte una emergencia futura en una tarea de mantenimiento planificada.

Verifica periódicamente `pg_stat_statements` (para queries lentas), `pg_stat_user_tables` (para seq_scans anómalos) y `pg_stat_user_indexes` (para índices huérfanos).

---

## 🧪 CHECKLIST DE BD INDESTRUCTIBLE

### Esquema
- [ ] ¿Todas las PK son UUID? (no exponer IDs secuenciales)
- [ ] ¿Todas las FK tienen índice explícito?
- [ ] ¿Todos los campos monetarios son BIGINT (centavos)?
- [ ] ¿Todas las fechas son TIMESTAMPTZ?
- [ ] ¿Todos los estados son ENUM (no TEXT libre)?
- [ ] ¿Constraints CHECK en precio, stock, email, etc.?
- [ ] ¿Tablas con +10M filas tienen particionamiento?

### Rendimiento
- [ ] ¿Índices compuestos para queries frecuentes?
- [ ] ¿Índices parciales para queries específicas?
- [ ] ¿Connection pooling configurado?
- [ ] ¿Paginación con cursores (nunca offset)?
- [ ] ¿EXPLAIN ANALYZE ejecutado localmente?

### Integridad
- [ ] ¿Transacciones con SAVEPOINT para grandes inserciones?
- [ ] ¿Soft delete + purga diferida?
- [ ] ¿Historial con Triggers para registros críticos?
- [ ] ¿Acción correcta (RESTRICT, SET NULL, CASCADE) en FKs?
- [ ] ¿RLS para multi-tenancy?

### Operabilidad
- [ ] ¿Toda migración tiene UP y DOWN?
- [ ] ¿Monitoreo activo para detectar queries lentas e índices sin usar?
