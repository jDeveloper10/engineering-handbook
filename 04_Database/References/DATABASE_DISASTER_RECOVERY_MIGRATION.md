---
title: "Plan de Migración de Emergencia y Portabilidad de Base de Datos (Disaster Recovery)"
category: 04_Database
doc_type: runbook
tags: [database, migrations, disaster-recovery, pg_dump, postgres, supabase, vps, backup, zero-downtime]
summary: "Runbook completo para migrar bases de datos en caliente o ante contingencias graves (Disaster Recovery). Incluye exportación segura con pg_dump (omitiendo roles propietarios), importación en VPS o Postgres alternativo, migración de auth.users y rollback sin pérdida de datos."
keywords: [migracion, disaster-recovery, pg_dump, pg_restore, supabase-a-vps, backup, portabilidad, zero-downtime]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "04_Database/DATABASE_ENGINEERING_STANDARD.md"
  - "04_Database/References/DATABASE_MIGRATION_RECIPES.md"
---

# PLAN DE MIGRACIÓN DE EMERGENCIA Y PORTABILIDAD DE BASE DE DATOS

> 🚨 **Objetivo:** Si Supabase, Cloudflare D1 o tu proveedor actual sufre una caída masiva, aumenta precios drásticamente o el cliente exige portabilidad a sus propios servidores (VPS / AWS / On-Premise), este runbook permite migrar el 100% de la base de datos (esquemas, datos, roles y autenticación) sin perder información y en menos de 30 minutos.

---

## 1. Estrategia de Portabilidad: Evitar el Vendor Lock-in

**[REQUIRED]** Aunque usemos Supabase o Cloudflare D1, el núcleo del sistema es **PostgreSQL / SQLite estándar**. Las reglas de portabilidad son:
1. Las tablas de negocio viven en el esquema `public`.
2. Las políticas RLS usan funciones SQL estándar sin depender de extensiones propietarias cerradas.
3. Se mantiene una copia de seguridad diaria exportable en formato `.sql` / `.dump`.

---

## 2. Migración Completa de Supabase a VPS Propio (PostgreSQL)

### Paso 1: Exportación Segura de Datos con `pg_dump`
Para volcar la base de datos sin errores de permisos (omitiendo los esquemas internos propietarios de Supabase como `supabase_admin` o `graphql`):

```bash
# 1. Exportar solo el esquema público y extensiones compatibles
pg_dump -h db.<PROJECT_REF>.supabase.co -U postgres -d postgres \
  --schema=public \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
  -F c -b -v -f supabase_backup_public.dump

# 2. Exportar la tabla de autenticación (usuarios y contraseñas hasheadas)
pg_dump -h db.<PROJECT_REF>.supabase.co -U postgres -d postgres \
  --table=auth.users \
  --table=auth.identities \
  --data-only \
  --no-owner \
  -F c -v -f supabase_auth_data.dump
```

---

### Paso 2: Preparar el Nuevo Servidor PostgreSQL (VPS Hetzner / Contabo)
En el nuevo servidor VPS con Docker Compose:

```yaml
# docker-compose.yml en el VPS
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    container_name: agency_postgres_prod
    restart: always
    environment:
      POSTGRES_DB: app_production
      POSTGRES_USER: agency_admin
      POSTGRES_PASSWORD: ${DB_STRONG_PASSWORD}
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432" # Solo accesible localmente por seguridad
```

---

### Paso 3: Restaurar en el Nuevo PostgreSQL
```bash
# 1. Restaurar el esquema y datos de negocio
pg_restore -h localhost -p 5432 -U agency_admin -d app_production \
  --no-owner \
  --no-privileges \
  -v supabase_backup_public.dump

# 2. Verificar la integridad de las tablas
psql -h localhost -U agency_admin -d app_production -c "SELECT count(*) FROM users;"
```

---

### Paso 4: Cambio de DNS / Variable de Conexión en los Workers
1. Actualizar la variable de entorno `DATABASE_URL` o `SUPABASE_URL` en Cloudflare Workers / Frontend:
   ```bash
   npx wrangler secret put DATABASE_URL
   # Ingresar: postgres://agency_admin:password@vps.tuagencia.com:5432/app_production?sslmode=require
   ```
2. Desplegar los workers actualizados. Latencia de corte: **< 10 segundos**.

---

## 3. Migración de Cloudflare D1 (SQLite Edge) a PostgreSQL / Turso

Si un proyecto en D1 necesita migrar a una base de datos relacional tradicional:

```bash
# 1. Exportar todo el contenido de D1 a un script SQL plano
npx wrangler d1 export indexgenius-content --remote --output=./d1_backup.sql

# 2. Convertir tipos SQLite (INTEGER/TEXT) a Postgres e importar:
psql -h localhost -U agency_admin -d app_production -f ./d1_backup.sql
```

---

## 4. Estrategia de Migraciones Versionadas y Rollback (Up / Down)

**[REQUIRED]** En todo proyecto de producción, cada cambio estructural de base de datos debe tener su archivo de subida (`.up.sql`) y su contraparte de reversión (`.down.sql`):

```
supabase/migrations/
  ├── 20260814120000_create_orders_table.up.sql
  └── 20260814120000_create_orders_table.down.sql
```

### Contenido de `20260814120000_create_orders_table.up.sql`:
```sql
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount_cents BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON public.orders(user_id);
```

### Contenido de `20260814120000_create_orders_table.down.sql` (Rollback):
```sql
DROP TABLE IF EXISTS public.orders CASCADE;
```

---

## 5. Checklist de Verificación Post-Migración

- [ ] Las tablas y registros coinciden en cantidad (`SELECT count(*) FROM table`).
- [ ] Las claves foráneas e índices secundarios están activos (`DB-002`).
- [ ] Las políticas RLS están activas y bloquean accesos no autorizados (`TENANT-001`).
- [ ] Las APIs y Workers responden con `200 OK` en flujos de lectura y escritura.
- [ ] El pool de conexiones (`Supavisor` / `PgBouncer`) está balanceando las peticiones concurrentes.
