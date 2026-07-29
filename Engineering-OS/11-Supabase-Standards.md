# 11 — Supabase Standards

> Supabase es la base de datos/auth por defecto para proyectos nuevos (decisión del stack
> canónico). Las reglas técnicas de base de datos (tipos, constraints, migraciones, RLS,
> backups) viven en el handbook `04_Database`. Este archivo solo agrega reglas operativas
> específicas de Supabase como plataforma.
>
> **Ver también:** [`DATABASE_ENGINEERING_STANDARD.md`](../04_Database/DATABASE_ENGINEERING_STANDARD.md)
> — estándar técnico completo de Postgres/Supabase (tipos, constraints, RLS, migraciones,
> backups, nomenclatura).
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Este archivo no reemplaza `DATABASE_ENGINEERING_STANDARD.md`. Las reglas
>   técnicas de esquema (naming de tablas, tipos de columna, timestamps, constraints,
>   migraciones, políticas RLS) se definen allí y se heredan aquí. Si hay contradicción,
>   gana el handbook `04_Database`.

- **[REQUIRED]** RLS activado en TODA tabla desde su creación. Una tabla sin políticas RLS no se
  considera terminada; `allow all` solo en desarrollo y nunca llega a producción. El
  Security-Agent audita esto en cada proyecto con Supabase.
- **[REQUIRED]** Migraciones versionadas (carpeta `supabase/migrations` o `apply_migration` vía
  MCP) — nunca cambios de esquema a mano en el dashboard sin registrar el SQL en el repo.
- **[REQUIRED]** `service_role` key SOLO en workers/backend (secret), jamás en frontend. En
  frontend solo `anon` key + RLS.
- **[REQUIRED]** Antes de crear tablas: revisar el esquema existente (`list_tables`) — la
  auditoría detectó tendencia a reconstruir en vez de reutilizar.
- **[RECOMMENDED]** Realtime solo donde el usuario lo percibe (precios, chat, señales de trading);
  para lo demás, fetch normal — cada canal realtime tiene costo de conexión.
- **[RECOMMENDED]** Tipos TypeScript generados (`generate_typescript_types`) tras cada migración,
  commiteados al repo.

## Nota sobre Firebase

Proyectos que hoy usan ambos (ej. jonnyTrader con Firestore + Supabase): congelar Firebase (no
crecer su uso), migrar módulo a módulo cuando se toquen. Ver [12-Firebase-Standards.md](12-Firebase-Standards.md).
