---
title: "Estrategias Avanzadas de Migración de Datos"
category: 04_Database
doc_type: estandar
tags: [database, migration, postgresql, d1, firebase, zero-downtime, backfill, rollback]
summary: "Estándar para migraciones de datos sin caídas (zero-downtime), doble escritura, backfill por lotes, migración PostgreSQL a D1, Firestore a Supabase y protocolos de rollback testeados."
keywords: [migration, data-migration, zero-downtime, d1, firestore, supabase, backfill, rollback, checksum, double-write]
updated: 2026-07-27
status: current
---

# 🗄️ ESTRATEGIAS AVANZADAS DE MIGRACIÓN DE DATOS

## 🎯 OBJETIVO
Garantizar la integridad, disponibilidad y consistencia de los datos durante cualquier proceso de reestructuración o migración de motor de base de datos, manteniendo disponibilidad continua (Zero-Downtime) y mecanismos de reversión inmediata.

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] MIG-001: NUNCA ejecutar una migración de datos sin un plan de Rollback verificado y testeado.** Si la migración falla a mitad de proceso, se debe poder restaurar el estado consistente previo sin pérdida de datos.

> **Por qué:** una migración que falla a mitad de camino sin plan de vuelta atrás deja la base en un estado intermedio que nadie diseñó — ni el esquema viejo ni el nuevo. Verificar el rollback antes de necesitarlo es la única forma de que exista cuando de verdad hace falta (misma razón que `DB-022`).

**[REQUIRED] MIG-002: Doble Escritura (Double-Write) obligatoria para migraciones Zero-Downtime.** El tráfico de producción debe escribir concurrentemente en el origen y destino durante la fase de sincronización activa.

> **Por qué:** cambiar el esquema de golpe exige una ventana de mantenimiento donde el tráfico se detiene; la doble escritura mantiene ambos esquemas sincronizados mientras el tráfico sigue vivo, así que el corte de servicio nunca es necesario.

**[REQUIRED] MIG-003: Backfills masivos SIEMPRE por lotes (chunked/batched).** NUNCA ejecutar un `UPDATE` o `INSERT INTO ... SELECT` sobre más de 5,000 filas en una sola transacción.

> **Por qué:** un `UPDATE` masivo sobre millones de filas retiene bloqueos el tiempo que tarda en completarse, y ese tiempo puede ser minutos en los que el resto de escrituras a esa tabla queda en espera. Trocearlo en lotes pequeños mantiene cada lote breve y no bloquea el tráfico real.

**[REQUIRED] MIG-004: Validación por Checksum y Row Count pre y post migración.** Ningún proceso de migración se da por concluido sin verificación matemática de paridad.

> **Por qué:** sin verificación matemática, una migración que "parece" haber funcionado puede haber perdido o duplicado filas en silencio — y ese tipo de corrupción no se nota hasta que alguien reporta un dato faltante semanas después.

---

## 🔄 1. ZERO-DOWNTIME MIGRATIONS (EXPANSION Y CONTRACCION)

Para cambiar el esquema de producción sin interrumpir el tráfico se aplica el patrón **Expand / Contract (Parallel Change)**.

```
Fase 1: Expandir   ──→ Añadir columna/tabla nueva (sin romper el código viejo)
Fase 2: Doble Write──→ Escribir en ambas columnas/tablas en cada request
Fase 3: Backfill   ──→ Migrar datos antiguos en lotes de fondo
Fase 4: Switch Read──→ Cambiar lecturas al nuevo esquema
Fase 5: Contraer   ──→ Eliminar columna/tabla antigua
```

### Código: Doble Escritura en Worker
```typescript
// ✅ CORRECTO: Doble escritura durante migración de tabla 'users' a 'profiles'
export async function createProfileDoubleWrite(userData: CreateUserInput, env: Env) {
  // 1. Escribir en esquema antiguo (origen)
  const legacyResult = await env.DB_OLD.prepare(
    'INSERT INTO legacy_users (id, email) VALUES (?, ?)'
  ).bind(userData.id, userData.email).run()

  // 2. Escribir en esquema nuevo (destino) sin fallar el request si el nuevo falla
  try {
    await supabase.from('profiles').insert({
      id: userData.id,
      email: userData.email,
      migrated_at: new Date().toISOString()
    })
  } catch (err) {
    console.error('[MIGRATION_DOUBLE_WRITE_FAIL]', err)
    await env.MIGRATION_LOGS.put(`fail:${userData.id}`, JSON.stringify(userData))
  }

  return legacyResult
}
```

---

## ⚡ 2. MIGRACIÓN DE POSTGRESQL A CLOUDFLARE D1

### Diferencias y Limitaciones Clave
| Característica | PostgreSQL (Supabase) | Cloudflare D1 (SQLite) |
|---|---|---|
| Motores / SQL | Postgres dialect completo | SQLite dialect |
| Tipos de Datos | ENUM, UUID, JSONB, TIMESTAMPTZ | TEXT, INTEGER, REAL, BLOB |
| Concurrencia | Concurrencia alta de escritura | Lectura ultra rápida / Escritura secuencial |
| Foreign Keys | Soporta `ON DELETE RESTRICT/CASCADE` | FKs deshabilitadas por defecto (activar PRAGMA) |

### Script de Conversión de Tipos y Export
```bash
# Exportar esquema Postgres preparado para D1
pg_dump --data-only --inserts --column-inserts \
  --quote-all-identifiers \
  -h db.xxx.supabase.co -U postgres -d postgres > dump_raw.sql

# Convertir tipos Postgres a SQLite (UUID -> TEXT, TIMESTAMPTZ -> TEXT)
sed -i 's/gen_random_uuid()/lower(hex(randomblob(16)))/g' dump_raw.sql
sed -i 's/now()/datetime("now")/g' dump_raw.sql

# Importar a Cloudflare D1
npx wrangler d1 execute my-production-db --file=dump_raw.sql
```

---

## 🚀 3. MIGRACIÓN DE FIRESTORE A SUPABASE (POSTGRESQL)

```typescript
// Script Node.js para migrar colecciones NoSQL de Firestore a PostgreSQL relacional
import admin from 'firebase-admin'
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)

async function migrateFirestoreUsersToSupabase() {
  const snapshot = await admin.firestore().collection('users').get()
  const BATCH_SIZE = 500
  let batch: Record<string, unknown>[] = []

  for (const doc of snapshot.docs) {
    const data = doc.data()
    batch.push({
      id: doc.id,
      email: data.email,
      name: data.displayName || 'Sin Nombre',
      created_at: data.createdAt?.toDate().toISOString() || new Date().toISOString()
    })

    if (batch.length >= BATCH_SIZE) {
      const { error } = await supabase.from('profiles').upsert(batch)
      if (error) throw error
      console.log(`[MIGRATED] ${batch.length} registros insertados`)
      batch = []
    }
  }

  if (batch.length > 0) {
    await supabase.from('profiles').upsert(batch)
  }
}
```

---

## 📦 4. BACKFILL EN LOTES Y VALIDACIÓN POR CHECKSUM

### Script de Backfill en Lotes (Batched Backfill)
```typescript
// Worker Job / CLI Script para poblar columnas sin bloquear la DB
export async function runChunkedBackfill(env: Env) {
  let lastId = '00000000-0000-0000-0000-000000000000'
  const CHUNK_SIZE = 1000
  let hasMore = true

  while (hasMore) {
    const { data: rows, error } = await supabase
      .from('documents')
      .select('id, title')
      .gt('id', lastId)
      .order('id', { ascending: true })
      .limit(CHUNK_SIZE)

    if (error || !rows || rows.length === 0) {
      hasMore = false
      break
    }

    // Procesar lote
    const updates = rows.map(r => ({
      id: r.id,
      slug: r.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
    }))

    await supabase.from('documents').upsert(updates)
    lastId = rows[rows.length - 1].id
    console.log(`[BACKFILL_PROGRESS] Procesados hasta ID: ${lastId}`)
  }
}
```

### Script de Validación por Checksum y Row Count
```sql
-- Verificar paridad de conteo y MD5 checksum pre/post migración
SELECT
  count(*) AS total_rows,
  md5(string_agg(id::text || email, '' ORDER BY id)) AS data_checksum
FROM profiles;
```

---

## 📋 CHECKLIST DE MIGRACIÓN

- [ ] Plan de Rollback escrito y probado en entorno de staging.
- [ ] Doble escritura activa y monitoreada durante la fase de transición.
- [ ] Backfills configurados en chunks <= 1,000 registros.
- [ ] Checksum de paridad ejecutado pre y post migración.
- [ ] Desactivación de scripts de doble escritura una vez confirmada la migración.
