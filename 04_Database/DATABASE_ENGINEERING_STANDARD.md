---
title: "DATABASE ENGINEERING STANDARD"
category: database
tags:
  - standards
  - conventions
  - postgres
  - supabase
  - rls
  - migrations
  - naming
summary: "Nivel 1 del dominio Database. Define reglas de Postgres/Supabase: naming de tablas y columnas, tipos de datos, timestamps, constraints, índices, RLS, migraciones versionadas y backups."
keywords:
  - postgresql
  - sql
  - schema
  - row-level-security
  - auth
  - triggers
updated: 2026-07-26
status: current
---

# DATABASE ENGINEERING STANDARD

> Nivel 1 del handbook para el dominio Database. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica (Postgres relacional en general) y después con una implementación de referencia en el stack actual (Supabase/Postgres, consumido desde Cloudflare Workers).
>
> Contexto de operación: developer solo / equipo muy pequeño, productos SaaS. La consecuencia práctica: no hay un DBA que revise cada esquema ni un equipo que detecte un `float` guardando dinero seis meses después. La base de datos tiene que defenderse sola — con tipos correctos, constraints y RLS — porque nadie más la va a defender.
>
> Este documento lo consumen IAs (Claude Code) al generar esquemas, migraciones y queries. Por eso las convenciones son deliberadamente rígidas: una IA que encuentra `users`, `orders`, `order_items` con FKs `user_id`/`order_id` puede inferir el resto del esquema sin adivinar; una IA que encuentra `tblUsers`, `Orders` y `id_de_orden` mezclados va a producir queries inconsistentes con el resto del sistema.
>
> Relación con otros documentos: el acceso a datos desde workers (helpers, `select` explícito, service role solo server-side) ya está regulado en `02_Backend/BACKEND_ENGINEERING_STANDARD.md` sección 13 — aquí no se repite, se profundiza el lado de la base de datos.

---

## 00. Las 5 Reglas Inquebrantables de Base de Datos

**[REQUIRED]** Si rompes alguna de estas reglas, el PR será rechazado sin discusión. Son los cimientos de la estabilidad de los datos.

1. **DB-001: NUNCA `SELECT *`.** Cada consulta (SQL o Prisma/Supabase-js) DEBE especificar exactamente las columnas necesarias (`.select('id, name')`). El wildcard destruye la latencia y rompe contratos cuando se añaden columnas sensibles.
2. **DB-002: NUNCA FK sin índice explícito.** Toda clave foránea (`user_id references users(id)`) DEBE tener su propio `CREATE INDEX` en la misma migración. Sin índice, los deletes en cascada bloquean la tabla entera.
3. **DB-003: Migración sin DOWN = RECHAZADO.** Toda migración SQL debe ser reversible (incluir el script `down`). Si por naturaleza técnica es irreversible (ej: un `DROP TABLE` donde se borran datos masivos irreparables), DEBE justificarse explícitamente en el PR.
4. **DB-004: Mutaciones complejas requieren transacciones.** Múltiples escrituras dependientes DEBEN ocurrir dentro de un `BEGIN/COMMIT`. Si la base de datos no soporta transacciones distribuidas o anidadas con seguridad, se DEBE usar `SAVEPOINT` para manejo de errores granulares.
5. **DB-005: Todo dato PII o sensible DEBE estar cifrado.** Tokens, claves API o datos médicos NUNCA viven en texto plano. (Ver Seguridad).
6. **DB-006: NUNCA triggers para lógica de negocio.** Los triggers son invisibles en el código del servidor y una pesadilla de depurar. Usar triggers SOLO para auditoría (timestamps, history logs) o integridad referencial dura. La lógica de negocio va en el Worker.
7. **DB-007: RLS OBLIGATORIO.** Toda tabla que guarde datos vinculados a un usuario (tabla con `user_id`) DEBE tener habilitado Row Level Security (`ALTER TABLE x ENABLE ROW LEVEL SECURITY`). Cero excepciones.

---

## 01. Naming — una sola convención, sin excepciones

**[REQUIRED]** Tablas en `snake_case`, en plural: `users`, `orders`, `order_items`, `payment_methods`.

**[REQUIRED]** Columnas en `snake_case`, en singular: `email`, `created_at`, `stripe_customer_id`.

**[REQUIRED]** Foreign keys se nombran `<tabla_singular>_id`: la FK hacia `users` es `user_id`, hacia `orders` es `order_id`. Si una tabla tiene dos FKs a la misma tabla, se prefija el rol: `sender_id` y `recipient_id` (ambas hacia `users`), no `user_id_1` y `user_id_2`.

**[REQUIRED]** Nunca identificadores que requieran comillas en Postgres: nada de mayúsculas (`"Users"`), espacios, ni palabras reservadas (`user`, `order` a secas como nombre de tabla — por eso el plural también ayuda: `users` y `orders` no chocan con las palabras reservadas `user` y `order`).

**Por qué:** la consistencia de naming no es estética — es predictibilidad. Para una IA que genera queries, un esquema consistente convierte "adivinar el nombre de la columna" en "derivarlo mecánicamente": si existe la tabla `subscriptions` y la tabla `users`, la FK *tiene* que llamarse `user_id` y el join se escribe solo. Cada excepción a la convención es un lugar donde la IA (o yo, en seis meses) genera un query contra una columna que no existe. Y los identificadores con mayúsculas en Postgres obligan a comillas dobles en cada query para siempre — un impuesto permanente por una decisión de un segundo.

**Implementación (Postgres):**

```sql
create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users (id) on delete cascade,
  plan text not null,
  created_at timestamptz not null default now()
);
```

---

## 02. Tipos de datos — el tipo correcto es una regla de negocio

### 2.1 Primary keys: `uuid` por defecto, `bigint` cuando el volumen lo justifica

**[REQUIRED]** Toda tabla tiene una PK explícita llamada `id`. **[RECOMMENDED]** `uuid` (generada con `gen_random_uuid()`) como default para tablas cuyos IDs viajan al cliente (usuarios, órdenes, recursos de API).

**Por qué:** un `uuid` no es adivinable ni enumerable — con `bigint` secuencial, `/orders/1042` le dice a un atacante que existe `/orders/1041` y cuántas órdenes tiene el negocio. Además el `uuid` puede generarse en el cliente o el worker antes del insert, útil para operaciones idempotentes. Es la opción segura por defecto para un SaaS.

**[RECOMMENDED]** `bigint generated always as identity` para tablas internas de altísimo volumen que nunca exponen su ID (logs de eventos, tablas de auditoría, colas): ocupa la mitad (8 vs 16 bytes), y al ser secuencial produce índices B-tree más compactos y con mejor localidad de inserción que un uuid aleatorio.

**[REQUIRED]** Nunca `serial` — `generated always as identity` es el reemplazo estándar SQL y evita los problemas de permisos/ownership de las secuencias implícitas de `serial`.

### 2.2 Fechas: `timestamptz` siempre, `timestamp` nunca

**[REQUIRED]** Toda columna de fecha-hora es `timestamptz`. `timestamp` (sin zona) está prohibido.

**Por qué:** `timestamp` sin zona no guarda un instante — guarda una foto ambigua que significa cosas distintas según la zona horaria de quien la lee. Con usuarios en varias zonas (cualquier SaaS), servidor en UTC y Workers ejecutando en el edge de medio mundo, esa ambigüedad produce bugs de horas de diferencia imposibles de rastrear. `timestamptz` guarda el instante real (internamente en UTC) y lo convierte al leer. No cuesta nada más y elimina la clase entera de bugs.

**[RECOMMENDED]** `date` (sin hora) solo cuando el dato es genuinamente un día de calendario sin instante asociado (fecha de nacimiento, día de facturación) — no como atajo para "no me importa la hora".

### 2.3 Dinero: `numeric`, nunca `float`

**[REQUIRED]** Todo valor monetario se guarda como entero en la unidad mínima (`amount_cents bigint` + columna `currency`) — nunca `real`, `double precision` ni `float`.

**Por qué:** los flotantes binarios no pueden representar exactamente valores decimales como 0.10 — los errores de redondeo se acumulan y terminan en un balance que no cuadra por centavos, que es el peor bug posible en un SaaS con pagos: pequeño, silencioso y destructor de confianza. Y el entero-en-centavos (el modelo de Stripe) es además el formato que el contrato de API ya exige en las respuestas (`03_API` §04) — guardar centavos en la DB elimina una conversión permanente entre capas.

**[RECOMMENDED]** `numeric` (con precisión explícita, ej. `numeric(12,2)`) es la alternativa aceptable solo cuando se necesita aritmética decimal en SQL (agregaciones contables, tasas con más de 2 decimales) — y en ese caso la conversión a centavos ocurre en un solo helper del worker, no dispersa por endpoint. Nunca mezclar ambas convenciones en el mismo proyecto.

### 2.4 Texto: `text` por defecto

**[REQUIRED]** Columnas de texto usan `text`. No se usa `varchar(n)` como pseudo-validación.

**Por qué:** en Postgres, `text` y `varchar` tienen exactamente el mismo rendimiento y almacenamiento — `varchar(255)` no es "más eficiente", es un límite arbitrario heredado de MySQL que un día trunca un dato legítimo. Si un campo tiene un límite real de negocio (un handle de máximo 30 caracteres), eso es una regla de negocio y se expresa como `CHECK (char_length(handle) <= 30)`, que es explícito, tiene nombre y da un error claro.

### 2.5 `jsonb`: para datos genuinamente sin esquema, no para evitar modelar

**[RECOMMENDED]** `jsonb` (nunca `json`, que no se indexa y guarda texto crudo) cuando la forma del dato es genuinamente variable y opaca para el negocio: payloads crudos de webhooks, respuestas de APIs externas archivadas, preferencias libres de UI.

**[REQUIRED]** No usar `jsonb` para datos con estructura conocida y estable que el negocio consulta o filtra. Señales de alarma que indican que ese `jsonb` debía ser columnas o una tabla: se hace `WHERE data->>'status' = ...` con frecuencia, se necesita un CHECK o NOT NULL sobre un campo interno, o distintas filas guardan las mismas claves siempre.

**Por qué:** cada campo dentro de un `jsonb` renuncia a todo lo que este documento exige en las secciones 5 y 6 — tipos, NOT NULL, CHECK, FKs e índices simples. `jsonb` es una válvula de escape para lo que no se puede modelar, no un atajo para no modelar. Para una IA es además una trampa: un campo `metadata jsonb` no documenta qué claves existen, y el código que lo lee se llena de accesos a claves que quizá no están.

---

## 03. Columnas estándar en toda tabla

**[REQUIRED]** Toda tabla tiene como mínimo:

| Columna | Tipo | Regla |
|---|---|---|
| `id` | `uuid` o `bigint` (sección 2.1) | PK, nunca reutilizada |
| `created_at` | `timestamptz not null default now()` | inmutable después del insert |
| `updated_at` | `timestamptz not null default now()` | mantenida por trigger, no por el código |

**[REQUIRED]** `updated_at` se actualiza con un trigger de base de datos, no confiando en que cada UPDATE del código lo setee.

**Por qué:** si `updated_at` depende del código, vale exactamente lo que valga el UPDATE más descuidado que toque la tabla — un update manual desde el SQL editor, un script de migración de datos o un worker nuevo que lo olvida, y la columna miente para siempre. El trigger vive donde vive el dato y aplica sin excepción. `created_at`/`updated_at` en toda tabla cuestan nada y son la primera herramienta de debugging ("¿cuándo cambió esto?") en un equipo sin más observabilidad.

**Implementación (Supabase):** la extensión `moddatetime` viene disponible en Supabase:

```sql
create extension if not exists moddatetime schema extensions;

create trigger handle_updated_at
  before update on orders
  for each row execute procedure moddatetime (updated_at);
```

### 3.1 Soft delete: decisión explícita por tabla, no default global

**[RECOMMENDED]** Soft delete (`deleted_at timestamptz null`) solo en tablas donde el negocio lo necesita: datos que el usuario puede querer recuperar, o registros referenciados por historial que debe sobrevivir (una orden pagada no desaparece porque se borró el producto).

**[REQUIRED]** Si una tabla usa soft delete, *todas* las lecturas de esa tabla filtran `deleted_at is null` — en Supabase esto se resuelve en la política RLS de SELECT o en una vista, no confiando en que cada query lo recuerde. Y los UNIQUE de esa tabla se vuelven índices únicos parciales (`unique ... where deleted_at is null`), porque si no, un email "borrado" bloquea el re-registro para siempre.

**Por qué no por defecto:** el soft delete global es deuda disfrazada de prudencia — cada tabla con `deleted_at` complica cada query, cada UNIQUE y cada FK (¿qué significa una FK hacia una fila "borrada"?). Para borrado real con obligación de retención, el backup (sección 10) ya cubre la recuperación ante errores. Hard delete es el default; soft delete es una feature de negocio que se decide tabla por tabla.

---

## 04. Modelado — normalización pragmática

**[REQUIRED]** Punto de partida: tercera forma normal informal — cada hecho vive en un solo lugar. Si el nombre del plan aparece copiado en `subscriptions.plan_name` y en `plans.name`, uno de los dos va a estar desactualizado; la FK existe para eso.

**[REQUIRED]** Relaciones muchos-a-muchos se modelan con tabla puente con nombre propio: `users` ↔ `projects` se resuelve con `project_members (project_id, user_id, role, created_at)` — nunca con un array de IDs (`project_ids uuid[]`) ni un `jsonb` de miembros en una de las dos tablas.

**Por qué:** un array de FKs no es una FK — Postgres no valida que esos IDs existan, no puede hacer `on delete` sobre ellos, y el join inverso ("¿en qué proyectos está este usuario?") se vuelve un scan. La tabla puente da integridad referencial, índices en ambas direcciones y un lugar natural para los atributos de la relación (rol, fecha de ingreso), que siempre terminan apareciendo.

**[RECOMMENDED]** Denormalizar (copiar un dato) solo en dos casos legítimos, y documentando el porqué en un comentario de la migración:

1. **Snapshot histórico** — el dato *debe* congelarse: `order_items.unit_price` copia el precio al momento de la compra, porque el precio del producto cambia y la orden no debe cambiar con él. Esto no es denormalización por rendimiento, es corrección del modelo.
2. **Rendimiento medido** — un contador o agregado (`projects.member_count`) solo después de que un `explain analyze` mostró que el join/count real es un problema, y siempre mantenido por trigger o job, no por el código de aplicación.

**Por qué el orden importa:** denormalizar "por si acaso" crea el trabajo permanente de mantener copias sincronizadas para resolver un problema de rendimiento que todavía no existe. A la escala de un SaaS de equipo pequeño, Postgres hace joins de millones de filas sin despeinarse — el join no es el enemigo; el dato duplicado sin dueño sí.

---

## 05. Constraints — la integridad vive en la base de datos

**[REQUIRED]** `NOT NULL` es el default de toda columna; `NULL` se permite solo cuando "ausente" es un estado real del negocio (ej. `canceled_at`). Cada columna nullable es una rama `if` más en todo el código que la lee.

**[REQUIRED]** Reglas de dominio simples se expresan como `CHECK` con nombre: `check (amount_cents >= 0)`, `check (status in ('draft','active','canceled'))`, `check (char_length(handle) between 3 and 30)`.

**[REQUIRED]** Unicidad de negocio se declara con `UNIQUE` en la base — nunca solo con un "verifiqué antes de insertar" en el código, que pierde la carrera entre dos requests concurrentes.

**[REQUIRED]** Toda FK declara su `ON DELETE` explícitamente — la decisión de qué pasa con las filas hijas al borrar la madre es una decisión de negocio, no un default heredado:

- `on delete cascade` — el hijo no tiene sentido sin el padre (`order_items` → `orders`).
- `on delete restrict` — borrar el padre con hijos vivos es un error de negocio (no se borra un `plan` con suscripciones activas).
- `on delete set null` — el hijo sobrevive y el vínculo era opcional (`tickets.assigned_to` → `users`).

**Por qué la integridad vive en la DB y no solo en el código:** la base de datos es el único punto por el que pasan *todos* los caminos de escritura — cada worker, el SQL editor del dashboard, un script de un solo uso, el código que una IA genere el año que viene. Una validación en el código protege un camino; un constraint los protege todos, incluso contra requests concurrentes (los constraints son atómicos; un check-then-insert en el código no lo es). En un equipo de una persona sin QA, los constraints son el revisor que nunca duerme: convierten "dato corrupto descubierto en tres meses" en "error explícito en el momento de escribirlo". La validación en el worker (Backend sección 05) sigue existiendo — pero para dar buenos mensajes de error, no como única defensa.

```sql
create table order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references orders (id) on delete cascade,
  product_id uuid not null references products (id) on delete restrict,
  quantity int not null check (quantity > 0),
  unit_price_cents bigint not null check (unit_price_cents >= 0),
  created_at timestamptz not null default now(),
  unique (order_id, product_id)
);
```

---

## 06. Índices — los justos, en el lugar justo

**[REQUIRED]** Toda FK tiene un índice. Postgres **no** indexa FKs automáticamente (solo PKs y UNIQUE) — una FK sin índice hace que cada join por esa columna y cada `on delete` sobre la tabla madre escaneen la tabla hija completa.

**[REQUIRED]** Se indexan las columnas que aparecen con frecuencia en `WHERE` u `ORDER BY` de queries reales del producto (ej. `orders(user_id, created_at desc)` para "mis órdenes recientes"). Índices compuestos: la columna de igualdad primero, la de rango/orden después.

**[RECOMMENDED]** Índice parcial cuando solo se consulta un subconjunto estable de filas: `create index on orders (user_id) where status = 'pending'` — más pequeño, más rápido, y solo se actualiza cuando cambia una fila del subconjunto. El caso obligado ya apareció en 3.1: los UNIQUE de tablas con soft delete.

**[REQUIRED]** Ante una query lenta, el diagnóstico es `explain analyze` (mirar `Seq Scan` sobre tablas grandes donde se esperaba un índice), no agregar índices por intuición. En Supabase, además: el Query Performance del dashboard (basado en `pg_stat_statements`) muestra las queries más costosas acumuladas, y los Advisors señalan FKs sin índice e índices nunca usados.

**Por qué no indexar todo:** cada índice se paga en cada INSERT/UPDATE/DELETE (todos los índices de la tabla se actualizan) y en almacenamiento. Sobre-indexar una tabla de escritura frecuente puede costar más de lo que ahorra — y los índices que nadie usa son deuda pura. El criterio es siempre: índice porque una query real lo necesita, no porque la columna existe.

---

## 07. Row Level Security (Supabase) — la autorización vive junto al dato

**[REQUIRED]** RLS habilitado (`alter table ... enable row level security`) en **toda** tabla del schema `public` — sin excepción, incluso en tablas que "solo se acceden desde el worker". En Supabase, el schema `public` está expuesto por la API auto-generada (PostgREST): una tabla sin RLS es legible y escribible por cualquiera que tenga la publishable/anon key, que por definición es pública porque viaja en el frontend.

**Por qué:** este es el error más caro posible en Supabase, y es silencioso — la app funciona exactamente igual con y sin RLS, hasta que alguien abre la consola del navegador, copia la anon key y descarga la tabla entera. Habilitar RLS sin políticas deja la tabla cerrada (deny by default), que es el estado seguro: una tabla cerrada de más produce un bug visible; una tabla abierta de más produce una filtración invisible.

**[REQUIRED]** Patrón base para tablas con dueño — columna `user_id` + una política por operación:

```sql
alter table documents enable row level security;

create policy "select own documents" on documents
  for select using ((select auth.uid()) = user_id);

create policy "insert own documents" on documents
  for insert with check ((select auth.uid()) = user_id);

create policy "update own documents" on documents
  for update using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy "delete own documents" on documents
  for delete using ((select auth.uid()) = user_id);
```

Detalles que importan: `using` filtra las filas visibles/afectadas, `with check` valida las filas resultantes de INSERT/UPDATE (sin `with check`, un update podría reasignar la fila a otro usuario). Envolver `auth.uid()` en `(select auth.uid())` permite a Postgres evaluarlo una vez por query en vez de una vez por fila — es la forma recomendada por Supabase para que las políticas no degraden queries grandes.

**[REQUIRED]** El `service_role` key **bypasea RLS por completo** (el rol tiene el atributo `bypassrls`). Implicaciones no negociables: (1) nunca sale del servidor — ya exigido en Backend sección 13; (2) todo código que la usa debe hacer su propia autorización explícita (filtrar por el user autenticado en el query), porque RLS ya no lo protege; (3) por eso el default en Workers es operar con el token del usuario cuando la operación es "en nombre del usuario" (sección 09), y reservar el service role para operaciones genuinamente administrativas (webhooks, jobs, agregados cross-usuario).

**[RECOMMENDED]** Las políticas RLS son la *última* línea de autorización, no la única capa de lógica: reglas complejas de negocio (planes, límites, estados) viven en el worker, y RLS garantiza el invariante mínimo — "nadie lee ni escribe filas que no le pertenecen" — incluso si el worker tiene un bug.

---

## 08. Migraciones — el esquema vive en el repo

**[REQUIRED]** Todo cambio de esquema —tablas, columnas, índices, políticas RLS, triggers, extensiones— es una migración SQL versionada en el repositorio. El dashboard de Supabase en producción es de **solo lectura** para el esquema: nunca se crea ni altera nada a mano ahí.

**Por qué:** un cambio manual en producción es un cambio que no existe en ningún lado — no se puede revisar, ni reproducir en un entorno nuevo, ni entender seis meses después, y la próxima migración puede chocar contra un estado que el repo no conoce. Para un solo developer la tentación del dashboard es máxima ("es un cambio chiquito") y el costo también: el repo deja de ser la verdad, y una IA que lee el repo para generar código genera contra un esquema que ya no existe. Las migraciones son al esquema lo que git es al código.

**Implementación (Supabase CLI):**

```
supabase/migrations/
├── 20260701120000_create_users.sql
├── 20260703093000_create_orders.sql
└── 20260710150000_add_orders_status_index.sql
```

`supabase migration new <nombre>` crea el archivo; se prueba primero contra la base local (`supabase db reset`) o una branch de Supabase, y se aplica a producción con `supabase db push` (o CI). Nombres descriptivos de la acción: `create_orders`, `add_orders_status_index` — no `fix2`.

**[REQUIRED]** Con código ya desplegado, los cambios de esquema son **aditivos primero** (expand → migrate → contract). El worker desplegado y la migración no se aplican en el mismo instante — durante la ventana entre ambos, código viejo corre contra esquema nuevo. Renombrar o borrar una columna en un solo paso rompe producción durante esa ventana. El orden seguro:

1. **Expandir** — agregar la columna/tabla nueva (nullable o con default; el código viejo la ignora sin romperse).
2. **Migrar** — desplegar código que escribe/lee lo nuevo; backfill de datos si hace falta.
3. **Contraer** — solo cuando nada referencia lo viejo, una migración posterior lo elimina.

**[RECOMMENDED]** Columnas `NOT NULL` sobre tablas existentes se agregan en dos pasos (agregar con default o backfill → luego `set not null`), y en tablas grandes con cuidado de locks — un `alter table` que reescribe la tabla la bloquea mientras dura.

---

## 09. Queries desde Workers

**[REQUIRED]** Cero SQL construido por concatenación/interpolación de strings con input externo — sin excepciones. Con `supabase-js`, los métodos del query builder (`.eq()`, `.in()`, `.insert()`) parametrizan por diseño; si se necesita SQL arbitrario, va en una función de Postgres (`create function`) invocada con `.rpc('fn', { params })`, donde los parámetros son argumentos tipados, no texto pegado.

**Por qué:** la inyección SQL sigue siendo la vulnerabilidad más barata de explotar y la más barata de prevenir — la parametrización la elimina por construcción. La regla es absoluta precisamente para que una IA nunca tenga que juzgar si "este caso es seguro".

**[REQUIRED]** Columnas explícitas en cada select — ya es regla en Backend sección 13; desde el lado de la DB se agrega el porqué de esquema: `select('*')` acopla el código a *todas* las columnas presentes y futuras de la tabla. Cada columna nueva (quizá sensible, quizá pesada) viaja automáticamente a todos los consumidores que hicieron `*`, y el contrato real entre worker y tabla queda implícito.

**[REQUIRED]** N+1 prohibido: nunca un query por elemento de una lista dentro de un loop. Supabase/PostgREST resuelve relaciones en un solo request con selects anidados:

```js
// ❌ N+1: 1 query por orden
const { data: orders } = await supabase.from("orders").select("id, total_cents").eq("user_id", userId);
for (const o of orders) {
  const { data: items } = await supabase.from("order_items").select("...").eq("order_id", o.id);
}

// ✅ 1 solo request: embedding por la FK
const { data: orders } = await supabase
  .from("orders")
  .select("id, total_cents, created_at, order_items ( product_id, quantity, unit_price_cents )")
  .eq("user_id", userId);
```

**Por qué importa doble en Workers:** cada query desde un Worker es un round-trip HTTP al servidor de Supabase — no hay conexión persistente ni pool local. Un N+1 de 50 elementos son 50 round-trips secuenciales de red real; el mismo dato en un request llega en uno.

**[REQUIRED]** Toda lista que puede crecer sin límite se pagina en el servidor (`.range()`, o keyset por `created_at`/`id` para listas largas) — nunca "traer todo y cortar en el código".

**[RECOMMENDED]** Operaciones "en nombre del usuario" se ejecutan con el JWT del usuario (cliente creado con el token del request en el header `Authorization`), de modo que RLS aplica y autoriza; el service role queda para lo administrativo (sección 07). Así un bug de filtro en el worker degrada a "el usuario ve sus propios datos" en vez de "el usuario ve los datos de todos".

---

## 10. Backups y recuperación

**[REQUIRED]** Antes de poner datos reales de usuarios en producción, se conoce y documenta la respuesta a tres preguntas: ¿con qué frecuencia hay backup?, ¿cuánto se retiene?, ¿cuánto dato como máximo se pierde ante un desastre (RPO)? Si la respuesta depende del plan contratado del proveedor, se verifica en la documentación oficial vigente en ese momento — los detalles por plan cambian y no se citan aquí como si fueran fijos.

**Estado en Supabase (verificar en docs oficiales los detalles del plan contratado):** los planes de pago incluyen backups automáticos diarios; Point-in-Time Recovery (PITR) es un add-on que permite restaurar a un instante arbitrario, bajando el RPO de "hasta un día de datos perdidos" a minutos. Para un SaaS con datos transaccionales (pagos, órdenes), **[RECOMMENDED]** PITR activo — un día entero de órdenes perdidas no es un incidente, es el negocio.

**[REQUIRED]** El backup existe cuando el restore está probado, no antes. Al menos una vez antes del launch (y tras cambios grandes de esquema), se ejecuta una restauración real a un proyecto/entorno separado y se verifica que los datos están completos y la app arranca contra ellos. Un backup jamás restaurado es una esperanza, no un plan.

**Por qué:** el escenario más probable de pérdida de datos en un equipo de una persona no es la caída del proveedor — es un `update` sin `where` o una migración destructiva ejecutada por uno mismo (o por una IA con acceso a la base). El backup —y saber restaurarlo bajo presión, habiendo practicado— es la red de seguridad contra el propio error.

**[RECOMMENDED]** Los cambios destructivos deliberados (borrar tabla/columna con datos) se hacen con red doble: backup verificado reciente + la fase "contract" de la sección 08, nunca como primer paso.

---

## 11. Datos sensibles

**[REQUIRED]** Nunca se guardan en texto plano: contraseñas (en ninguna forma reversible), tokens de acceso/refresh de terceros sin cifrar, números completos de tarjeta (eso vive en el proveedor de pagos — se guarda el `customer_id`/`payment_method_id` de Stripe, jamás el PAN), ni secretos de API propios (esos van en secretos del Worker, Backend sección 06 — no en una tabla).

**[REQUIRED]** El hashing de contraseñas lo maneja Supabase Auth (bcrypt, en `auth.users`) — **nunca** se implementa un login propio con columna `password` en una tabla del schema `public`, ni se duplica el email/identidad fuera de Auth más allá de una tabla `profiles` referenciando `auth.users (id)`.

**Por qué:** el manejo de credenciales es el problema con mayor castigo por error y menor recompensa por resolverlo uno mismo — está completamente resuelto por la plataforma. Una tabla propia de passwords es la forma más rápida de convertir una filtración menor en una catástrofe.

**[REQUIRED]** PII (nombre, email, teléfono, dirección) se trata con minimización: se guarda solo la que el producto usa de verdad, se sabe en qué tablas vive (inventario mínimo documentado), y nunca aparece en logs (Backend sección 10) ni en tablas de eventos/analytics donde sobrevive fuera de control.

**[RECOMMENDED]** Secretos que la aplicación debe poder leer (API keys de terceros por usuario, tokens OAuth) se guardan cifrados — en Supabase, Vault cifra el valor en reposo y expone el descifrado solo vía SQL con los permisos adecuados; la alternativa agnóstica es cifrado a nivel de aplicación con la key fuera de la base. El criterio: si un dump de la tabla cae en manos equivocadas, esos valores no deben ser utilizables.

**[RECOMMENDED]** Para PII de alto riesgo más allá de lo básico (documentos de identidad, datos de salud, financieros detallados), la primera pregunta es si de verdad hay que guardarla — el dato que no se guarda es el único que no se puede filtrar.

---

## Checklist — antes de dar por terminado un esquema o una migración

**Naming y tipos**
- [ ] ¿Tablas `snake_case` plural, columnas `snake_case`, FKs `<tabla_singular>_id`, nada que requiera comillas?
- [ ] ¿PK `id` (`uuid` para IDs expuestos; `bigint identity` solo interno de alto volumen), nunca `serial`?
- [ ] ¿Toda fecha-hora es `timestamptz`? ¿Dinero en `*_cents bigint` + `currency` (alineado con `03_API` §04), jamás float?
- [ ] ¿`text` (+ CHECK si hay límite real) en vez de `varchar(n)`? ¿Cada `jsonb` es genuinamente sin esquema y no pereza de modelado?

**Columnas estándar y modelado**
- [ ] ¿`id`, `created_at`, `updated_at` en toda tabla, con `updated_at` por trigger?
- [ ] ¿Soft delete solo donde el negocio lo pide, con filtro garantizado (RLS/vista) y UNIQUE parciales?
- [ ] ¿Cada hecho en un solo lugar? ¿Muchos-a-muchos con tabla puente, no arrays de IDs?
- [ ] ¿Cada denormalización es snapshot histórico o rendimiento medido, documentada en la migración?

**Constraints e índices**
- [ ] ¿`NOT NULL` por defecto, CHECKs para dominios simples, UNIQUE en la base (no solo en código)?
- [ ] ¿Toda FK con `ON DELETE` explícito y decidido por negocio?
- [ ] ¿Toda FK indexada? ¿Índices respaldados por queries reales (y `explain analyze` ante lentitud), no por intuición?

**RLS y acceso**
- [ ] ¿RLS habilitado en TODA tabla de `public`, con políticas por operación (`using` + `with check`, `(select auth.uid())`)?
- [ ] ¿Todo camino que usa service role hace autorización explícita propia? ¿Operaciones de usuario con el JWT del usuario?

**Migraciones y queries**
- [ ] ¿El cambio es una migración versionada en el repo — cero cambios manuales en el dashboard de producción?
- [ ] ¿Aditiva primero (expand → migrate → contract) si hay código desplegado?
- [ ] ¿Queries parametrizadas siempre, columnas explícitas, sin N+1 (embedding), listas paginadas?

**Backups y datos sensibles**
- [ ] ¿Plan de backup conocido y documentado (frecuencia/retención/RPO, verificado en docs del plan)? ¿Restore probado al menos una vez?
- [ ] ¿Nada prohibido en texto plano (passwords, PAN, tokens sin cifrar)? ¿Auth de Supabase para credenciales, PII minimizada y fuera de logs?

---

## ⚡ REGLAS INQUEBRANTABLES (DB-001 a DB-009)

### DB-001: SELECT * PROHIBIDO
### DB-002: FK SIN ÍNDICE PROHIBIDO  
### DB-003: MIGRACIÓN SIN ROLLBACK PROHIBIDO
### DB-004: TRANSACCIÓN > 10 ROWS SIN SAVEPOINT PROHIBIDO
### DB-005: DATO SENSIBLE EN TEXTO PLANO PROHIBIDO
### DB-006: TRIGGER PARA LÓGICA DE NEGOCIO PROHIBIDO (solo auditoría)
### DB-007: RLS OBLIGATORIO EN TABLAS CON USER_ID
### DB-008: DINERO EN FLOAT/DOUBLE PROHIBIDO (solo bigint centavos)
### DB-009: FECHAS SIN TIMEZONE PROHIBIDO (solo timestamptz)
