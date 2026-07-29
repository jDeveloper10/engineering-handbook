---
title: "API ENGINEERING STANDARD"
category: api
tags:
  - standards
  - conventions
  - rest-api
  - error-handling
  - validation
summary: "Nivel 1 del dominio API. Define el contrato hacia afuera del sistema: rutas, métodos HTTP, códigos de respuesta, envelope de respuesta, códigos de error estables, versionado, paginación, auth, rate limiting e idempotencia."
keywords:
  - rest
  - envelope
  - http-status
  - contracts
  - openapi
updated: 2026-07-26
status: current
---

# API ENGINEERING STANDARD

> Nivel 1 del handbook para el dominio API. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica y después con una implementación de referencia en el stack actual (Cloudflare Workers multi-worker, Supabase, frontend React).
>
> **Relación con el Backend:** [BACKEND_ENGINEERING_STANDARD.md](../02_Backend/BACKEND_ENGINEERING_STANDARD.md) define *cómo se construye* un worker (capas, helpers, middleware, logging). Este documento define *el contrato hacia afuera*: qué promete la API a cualquier cliente que la consuma (hoy, el frontend React; mañana, una app móvil o un tercero). Ninguna regla del Backend se repite aquí — cuando aplica, se declara "hereda de Backend §X".
>
> **Contexto de diseño:** developer solo / equipo muy pequeño, SaaS cuyo único consumidor actual es el propio frontend. Eso permite decisiones deliberadamente simples (sin versionado prematuro, sin OpenAPI completo) que este documento hace explícitas para que una IA no "mejore" la API agregando complejidad que nadie pidió.

---

## 01. Diseño de recursos y naming de rutas

**[REQUIRED]** Las rutas nombran **recursos** (sustantivos en plural, en inglés, `kebab-case`), no acciones: `/subscriptions`, `/payment-methods` — nunca `/getSubscriptions` ni `/createPayment`. La acción la expresa el método HTTP (sección 02).

**Por qué:** con recursos + métodos, un cliente (humano o IA) puede predecir la ruta de una operación sin leer documentación: si existe `GET /invoices`, existe con altísima probabilidad `GET /invoices/:id`. Con rutas-verbo cada endpoint es un caso especial que hay que memorizar.

**[REQUIRED]** Jerarquía de anidado: máximo 2 niveles (`/users/:id/subscriptions` sí; `/users/:id/subscriptions/:id/invoices/:id` no). Si un recurso anidado necesita accederse por su propio id, se promueve a ruta raíz (`/invoices/:id`) con el padre como filtro (`/invoices?subscription_id=...`).

**Por qué:** más de 2 niveles obliga al cliente a conocer toda la cadena de ids para llegar a un recurso que ya tiene id propio, y multiplica rutas equivalentes para el mismo dato — dos formas de pedir lo mismo es una fuente de bugs de caché y de autorización.

**[RECOMMENDED]** Apartarse de REST cuando la operación no es un CRUD sobre un recurso: acciones de negocio se modelan como sub-ruta verbo bajo el recurso, con POST: `POST /subscriptions/:id/cancel`, `POST /invoices/:id/retry-payment`. No se fuerza un `PATCH { status: "cancelled" }` cuando la operación tiene efectos colaterales (emails, webhooks, prorrateos) que un "cambio de campo" esconde.

**Por qué:** REST es un medio (predictibilidad), no un fin. Una acción disfrazada de cambio de estado miente sobre sus efectos; el verbo explícito documenta que ahí pasa algo más que un UPDATE.

**Implementación (multi-worker):** cada worker es dueño de un prefijo de ruta que coincide con su dominio de responsabilidad (hereda de Backend §07): `payments-worker` sirve `/payments/*` y `/invoices/*`; `user-worker` sirve `/users/*`. Un recurso nunca se sirve desde dos workers — el prefijo de ruta es el mapa público del patrón multi-worker.

---

## 02. Métodos HTTP y semántica

**[REQUIRED]** Los métodos se usan con su semántica estándar, sin excepciones:

| Método | Uso | Idempotente |
|---|---|---|
| GET | Leer. **Nunca** muta estado. | Sí |
| POST | Crear recurso / ejecutar acción de negocio | No (salvo sección 11) |
| PATCH | Actualización **parcial** — solo los campos enviados | No garantizada |
| PUT | Reemplazo **completo** del recurso | Sí |
| DELETE | Eliminar (o soft-delete, según el recurso) | Sí |

**Por qué la idempotencia importa:** navegadores, proxies y librerías de fetch reintentan automáticamente métodos idempotentes ante fallos de red. Un GET que muta o un PUT que no es realmente idempotente convierte cada reintento invisible en un efecto duplicado que nadie puede reproducir después.

**[REQUIRED]** Default para actualizaciones: **PATCH**. PUT solo cuando el cliente realmente envía la representación completa del recurso (raro en este SaaS). Un PATCH ignora campos ausentes; nunca los interpreta como "borrar el campo".

**Por qué:** el frontend casi siempre edita un subconjunto (un formulario de perfil no envía todas las columnas). Exigir PUT obligaría al cliente a leer-antes-de-escribir siempre, y un campo olvidado borraría datos en silencio.

**[REQUIRED]** DELETE sobre un recurso ya eliminado responde 404 (o 204 si se decide tratarlo como idempotente puro) — pero la decisión es una sola para toda la API, no por endpoint.

---

## 03. Códigos de estado

**[REQUIRED]** El código de estado HTTP refleja el resultado real. **Nunca** se responde `200` con un error en el body — un 200 con `{ success: false }` rompe todo lo que razona por status (caché HTTP, monitoreo, interceptores del frontend, reintentos automáticos).

**[REQUIRED]** Vocabulario acotado — estos y solo estos, salvo caso justificado por escrito:

| Código | Cuándo |
|---|---|
| 200 | GET/PATCH/PUT exitoso, y POST de acción de negocio |
| 201 | POST que creó un recurso (body: el recurso creado) |
| 204 | Éxito sin body (DELETE, y respuesta a preflight OPTIONS) |
| 400 | Input inválido: body, query params o headers que no pasan el schema |
| 401 | Sin token, token inválido o expirado |
| 403 | Token válido, pero sin permiso para este recurso |
| 404 | Recurso inexistente — **también** cuando existe pero pertenece a otro usuario |
| 409 | Conflicto de estado: duplicado, transición inválida (cancelar lo ya cancelado) |
| 429 | Rate limit excedido (hereda de Backend §11) |
| 500 | Error interno no previsto. Mensaje genérico, detalle solo en logs (Backend §09) |

**Por qué acotado:** un catálogo corto y estable permite que el interceptor del frontend maneje cada código con una sola rama global (401 → re-login, 429 → backoff, 500 → toast genérico). Cada código exótico (418, 451, 402...) es una rama más que alguien tiene que escribir y testear.

**Por qué 404 y no 403 para recursos ajenos:** responder 403 confirma a un atacante que el id existe — enumeración de recursos. 404 no filtra información. (Excepción consciente: recursos donde la existencia es pública por diseño.)

**[RECOMMENDED]** No usar 422 para validación — 400 cubre todo input inválido en esta API. Distinguir 400/422 es una sutileza que duplica ramas sin beneficio para un solo consumidor.

### 401/403 Decision Tree (Cross-domain)

**[REQUIRED]** Reglas exactas de orquestación cuando falla la autenticación/autorización:

1. **Interceptor HTTP global (Frontend)** detecta el `401`.
2. Si existe un *refresh token* → intenta renovar la sesión de forma invisible.
3. Si la renovación falla o no hay token → limpia el storage local + redirige a `/login?redirect={url}`.
4. **El Backend NUNCA redirige**, solo devuelve el `401` en formato JSON (`{ success: false, error: ... }`).
5. **Error 403 (prohibido)** → El frontend muestra la página de error 403 (ver `FRONTEND_ERROR_PAGES_STANDARD.md`), **NO redirige al login**. Redirigir al login un 403 atrapa al usuario en un loop infinito si ya está logueado pero no tiene permisos.

---

## 04. Formato de respuesta estándar

El envelope (`{ success: true, data }` / `{ success: false, error: { code, message } }`) y el helper único que lo construye **heredan de Backend §01 y §09** — no se redefinen aquí. Este documento agrega lo que el contrato promete al cliente:

**[REQUIRED]** `error.code` es un identificador estable en `SCREAMING_SNAKE_CASE`, legible por máquina, y es **parte del contrato**: el frontend puede hacer `if (error.code === "SUBSCRIPTION_ALREADY_CANCELLED")`. Renombrar un `code` existente es un breaking change (sección 07). `error.message` es para humanos, en español, y puede cambiar libremente — el cliente **nunca** hace lógica sobre el texto del message.

**Por qué:** separar máquina/humano en campos distintos es lo que permite mejorar los mensajes sin romper clientes, y traducirlos sin tocar lógica.

**[REQUIRED]** Los errores de validación (400) incluyen el detalle por campo, para que el frontend pinte el error junto al input y no como toast genérico:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Datos inválidos.",
    "details": [
      { "field": "email", "message": "Formato de email inválido." }
    ]
  }
}
```

**[REQUIRED]** Convenciones de los datos en `data`: claves en `snake_case` (coinciden con las columnas de Postgres/Supabase — sin capa de renombrado que mantener), fechas en ISO 8601 UTC (`2026-07-20T14:30:00Z`), montos de dinero en **enteros de la unidad mínima** (centavos) + campo `currency`, nunca floats.

**Por qué:** cada conversión de formato entre capas es un lugar donde desincronizarse; los floats en dinero producen errores de redondeo reales en sumas y prorrateos.

---

## 05. Paginación

**[REQUIRED]** Todo endpoint que lista una colección que crece con el uso (invoices, eventos, logs, mensajes) es paginado desde el día uno — nunca "devolver todo" con la promesa de paginar después, porque el frontend se construye asumiendo la lista completa y paginar después es un breaking change.

**[REQUIRED]** Defaults y límites: `limit` default **20**, máximo **100**. El objetivo real es mantener la respuesta por debajo de ~100KB y el query de DB por debajo del presupuesto de latencia del endpoint (<500ms p95); 20/100 es la heurística actual para lograrlo y puede recalibrarse por endpoint si se mide.

**[RECOMMENDED]** Estrategia según el caso:

- **Cursor** (`?cursor=...&limit=20`) para listas que el usuario final scrollea y que reciben inserciones constantes (feeds, historiales). El cursor es opaco para el cliente (ej. base64 de `created_at` + `id` del último ítem).
- **Offset** (`?page=2&limit=20`) aceptable para tablas de admin pequeñas y acotadas donde "saltar a la página 5" y el total importan más que la consistencia.

**Por qué:** con offset, una inserción entre página 1 y 2 duplica o saltea ítems, y `OFFSET 10000` obliga a la DB a leer y descartar 10.000 filas; el cursor es estable ante inserciones y de costo constante. Pero el cursor no puede saltar a una página arbitraria — por eso la regla es por caso de uso, no dogma.

**[REQUIRED]** La respuesta paginada declara cómo continuar, dentro del envelope estándar:

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": { "next_cursor": "eyJj...", "has_more": true, "limit": 20 }
}
```

(`next_cursor: null` cuando no hay más. En modo offset: `page`, `total_count`, `has_more`.)

**Implementación (Supabase):** cursor con `.gt()/.lt()` sobre `(created_at, id)` + `.order(...)` + `.limit(n + 1)` (el ítem extra revela `has_more` sin un `count` adicional); offset con `.range(from, to)`. Columnas explícitas siempre (hereda de Backend §13).

---

## 06. Filtrado y ordenado

**[REQUIRED]** Filtros y orden viajan como query params planos y predecibles: `?status=active&sort=created_at&order=desc`. Nada de mini-lenguajes de query (`?filter=status:eq:active`) — si un endpoint necesita búsqueda compleja, se crea un endpoint de búsqueda explícito, no un DSL genérico.

**Por qué:** un DSL de filtrado es una superficie de parsing, validación y seguridad enorme para un SaaS con un solo consumidor; los params planos se validan con el mismo schema que el body.

**[REQUIRED]** Los campos filtrables y ordenables son una **whitelist explícita por endpoint**, validada con schema (hereda de Backend §05). Un `sort` fuera de la whitelist responde 400 — jamás se interpola el valor del query param en el query de DB.

**Por qué:** sin whitelist, `?sort=password_hash` ordena (y por tanto filtra por inferencia binaria) columnas sensibles, y cualquier interpolación directa es inyección esperando su turno. La whitelist además protege a la DB: solo se permite ordenar por columnas indexadas.

**Implementación (zod):**
```ts
const listInvoicesQuery = z.object({
  status: z.enum(["draft", "paid", "void"]).optional(),
  sort: z.enum(["created_at", "amount"]).default("created_at"),
  order: z.enum(["asc", "desc"]).default("desc"),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  cursor: z.string().optional(),
});
```

---

## 07. Versionado

**[REQUIRED]** **No se versiona la API todavía.** Sin prefijo `/v1`, sin header de versión. El único consumidor es el propio frontend, que se despliega junto con los workers — versionar hoy es mantener dos contratos para cero clientes externos.

**Por qué:** el versionado existe para no romper clientes que no controlás. Mientras todos los clientes son propios y se despliegan coordinados, la "versión" es el deploy. Agregar `/v1` "por si acaso" es complejidad especulativa — exactamente lo que una IA tiende a agregar por defecto y este documento prohíbe.

**[REQUIRED]** El costo de esa decisión es la disciplina de **cambios compatibles primero**. Son compatibles (se hacen sin aviso): agregar campos a una respuesta, agregar campos **opcionales** al request, agregar endpoints, agregar valores a un enum **que el cliente trata con default case**. Son breaking (prohibidos sin migración): renombrar/eliminar campos o `error.code`s, volver requerido lo opcional, cambiar tipos o semántica de un campo, cambiar códigos de estado.

**Corolario para el cliente [REQUIRED]:** el frontend ignora campos desconocidos en las respuestas (no valida "exactamente estas claves y ninguna más") — es lo que hace baratos los cambios aditivos.

**[REQUIRED]** Cuando un breaking change sea inevitable: primero se agrega el campo/endpoint nuevo conviviendo con el viejo (expand), se migra el frontend, y solo entonces se elimina el viejo (contract) — nunca un deploy que rompe y arregla "a la vez", porque entre el deploy del worker y el del frontend hay usuarios con la versión anterior cargada en el navegador.

**[RECOMMENDED]** El día que exista un cliente que no controlás (API pública, app móvil con ciclo de release lento), ese es el disparador para introducir versionado — por prefijo de ruta (`/v2/...`), que es lo que el patrón de routing por prefijo de la sección 01 ya soporta sin tocar los workers existentes.

---

## 08. Validación de entrada y contratos compartidos

La validación con schema en el borde del worker hereda de Backend §05 (incluido: nunca confiar en que el frontend validó). Este documento agrega el contrato de tipos:

**[REQUIRED]** Los tipos del contrato (shapes de request/response, `error.code`s) tienen **una sola fuente de verdad compartida** entre frontend y workers — no dos declaraciones paralelas que alguien mantiene sincronizadas a mano.

**Por qué:** dos copias del mismo tipo divergen en silencio; el bug aparece como un `undefined` en producción, no como un error de compilación. Con fuente única, un cambio de contrato rompe la compilación de ambos lados — que es exactamente donde querés enterarte.

**Implementación (TypeScript + zod):** los schemas zod viven en un paquete compartido del monorepo (`shared/contracts/`), y los tipos se derivan de ellos — el schema valida en runtime en el worker y tipa en compile-time en ambos lados:

```ts
// shared/contracts/invoices.ts
export const createInvoiceBody = z.object({
  subscription_id: z.string().uuid(),
  amount_cents: z.number().int().positive(),
  currency: z.enum(["USD", "MXN"]),
});
export type CreateInvoiceBody = z.infer<typeof createInvoiceBody>;
```

**[RECOMMENDED]** Los tipos de las filas de la DB se generan desde Supabase (`supabase gen types typescript`) en el mismo paquete compartido, en vez de escribirse a mano — misma lógica de fuente única, aplicada al schema de la DB.

---

## 09. CORS — configuración correcta

La centralización del módulo CORS hereda de Backend §03. Este documento fija **qué valores** son correctos:

**[REQUIRED]** `Access-Control-Allow-Origin` responde con **el origin específico** del request si está en la whitelist de origins permitidos (los dominios del frontend), o no responde CORS en absoluto. Nunca `*` en una API autenticada.

**Por qué:** `*` significa "cualquier página web del mundo puede leer las respuestas de esta API desde el navegador de tus usuarios". Además, la especificación prohíbe combinar `Access-Control-Allow-Credentials: true` con origin `*` — el navegador bloquea la respuesta; la combinación no es solo insegura, es no-funcional. Y como la whitelist tiene varios origins (prod, staging, localhost), el header debe ecoar el origin concreto validado, junto con `Vary: Origin` para no envenenar cachés intermedias.

**[REQUIRED]** El preflight `OPTIONS` se responde antes del middleware de auth (un preflight nunca trae `Authorization`), con 204, y `Access-Control-Allow-Headers` incluye exactamente los headers que la API acepta: `Authorization, Content-Type, Idempotency-Key`. Un header custom nuevo (sección 11) que se olvida aquí produce errores CORS que parecen bugs de auth.

**[RECOMMENDED]** `Access-Control-Max-Age` para cachear el preflight y ahorrar un round-trip por request. El objetivo es reducir latencia percibida; como referencia, los navegadores capan este valor a un máximo propio (del orden de horas — verificar en docs oficiales el cap vigente por navegador), así que un valor de `86400` es seguro de declarar aunque el navegador lo recorte.

**Implementación (Workers):**
```ts
const ALLOWED_ORIGINS = ["https://app.example.com", "http://localhost:5173"];
function corsHeaders(request: Request) {
  const origin = request.headers.get("Origin");
  if (!origin || !ALLOWED_ORIGINS.includes(origin)) return {};
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET,POST,PATCH,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Idempotency-Key",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}
```

---

## 10. Autenticación en la API

El middleware `requireAuth` único hereda de Backend §04. Este documento fija el contrato de auth:

**[REQUIRED]** La API se autentica con `Authorization: Bearer <access_token>` donde el token es el JWT de sesión de Supabase Auth del usuario — nunca cookies propias, nunca API keys inventadas, nunca el token en query param (los query params terminan en logs y en el historial del navegador).

**[REQUIRED]** Todo endpoint es **autenticado por defecto**. Los endpoints públicos son una whitelist explícita y corta declarada en el router de cada worker (ej. `GET /health`, webhooks — que se autentican por firma, Backend §12, no por Bearer). Un endpoint sin auth es una decisión visible en el código, jamás un olvido posible.

**Por qué:** el fallo seguro. Si el default es "abierto salvo que se proteja", cada endpoint nuevo nace como potencial fuga; si el default es "cerrado salvo whitelist", el peor olvido posible es un 401 de más.

**[REQUIRED]** El worker verifica el token en **cada** request — nunca confía en un `user_id` que venga en el body o en la URL como identidad. El id del usuario autenticado sale exclusivamente del token verificado; un `user_id` en la ruta solo se usa tras comprobar que coincide con (o que el rol del token puede acceder a) ese recurso.

**Por qué:** el patrón `POST /users/:id/...` donde el handler cree en el `:id` es el IDOR clásico — cualquier usuario autenticado opera sobre cualquier otro cambiando un número en la URL.

**[RECOMMENDED]** Verificación del JWT **local** (firma + expiración contra las claves públicas de Supabase) en vez de un round-trip a `supabase.auth.getUser()` por request, en los endpoints de alto tráfico. Supabase soporta claves de firma asimétricas con endpoint JWKS para esto — verificar en docs oficiales el mecanismo vigente y su configuración antes de implementarlo; `getUser()` (que sí valida contra el servidor, incluyendo revocación) sigue siendo el default correcto para endpoints sensibles (pagos, cambios de cuenta).

**Por qué:** el trade-off real es latencia vs revocación inmediata — la verificación local no se entera de un logout/ban hasta que el token expira. La regla es elegir por endpoint según qué duele más, no aplicar uno de los dos a ciegas.

---

## 11. Idempotencia en escrituras críticas

**[REQUIRED]** Toda operación de escritura **no idempotente por naturaleza cuyo duplicado cuesta dinero o estado irrecuperable** (crear un pago, crear una suscripción, disparar un envío) acepta un header `Idempotency-Key` (UUID generado por el cliente por intento-de-operación, reutilizado en cada retry de ese intento). Mismo key ⇒ la API devuelve la respuesta original almacenada, sin re-ejecutar el efecto.

**Por qué:** el cliente no puede distinguir "el request nunca llegó" de "llegó, se ejecutó, y la respuesta se perdió". Sin idempotencia, su única opción segura es no reintentar (y perder operaciones) o reintentar (y duplicar cobros). Es el mismo principio que Backend §12 exige para webhooks entrantes, aplicado a la dirección opuesta: aquí el que reintenta es nuestro propio cliente.

**[REQUIRED]** El registro de keys usadas vive en un almacenamiento con **garantía real contra duplicados** para operaciones de dinero: una tabla de Postgres/Supabase con unique constraint sobre el key (el insert duplicado falla de forma atómica y ahí se responde el resultado guardado). Un almacenamiento eventualmente consistente (como Workers KV) **no** sirve como única barrera para pagos — dos requests casi simultáneos pueden ambos "no ver" el key y ejecutar el cobro dos veces.

**Por qué el detalle de consistencia:** la ventana de replicación de un store eventual es exactamente la ventana en la que ocurren los double-clicks y los retries agresivos — el caso que la idempotencia existe para cubrir.

**[RECOMMENDED]** Los registros de idempotencia expiran (referencia: 24h) — el objetivo es cubrir la ventana realista de retries del cliente sin acumular una tabla infinita, no garantizar unicidad eterna.

**[RECOMMENDED]** GET, PUT y DELETE no necesitan `Idempotency-Key` — ya son idempotentes por semántica (sección 02). No agregar el header donde no compra nada.

---

## 12. Timeouts y reintentos — qué promete la API

**[REQUIRED]** Presupuesto de latencia explícito: un endpoint síncrono responde en **<500ms p95**; el objetivo real es que la UI pueda mostrar resultado sin estados de carga eternos y que ningún request se acerque a los límites de ejecución del runtime. Todo trabajo que no cabe en ese presupuesto (envío de emails, generación de reportes, llamadas a terceros lentos) se responde `202`-style: se encola (Queues/Durable Objects, hereda el patrón de Backend §12) y el cliente consulta el estado por polling a un recurso de estado — no se mantiene el request abierto.

### API-007: Presupuesto de Latencia por Tipo de Endpoint

| Tipo de Endpoint | Latencia p95 | Justificación |
|---|---|---|
| CRUD estándar | <500ms | Presupuesto general |
| Dashboard / Analytics | <200ms | Percepción de instantaneidad |
| Webhooks entrantes | <100ms | Responder rápido, procesar después |
| Export / PDF | <30s | Jobs largos usan Queues |

**[REQUIRED] Para lograr <200ms en dashboards:**
1. Usar agregados precomputados (vistas materializadas o tablas de métricas/resumen acumulado).
2. NUNCA hacer agregaciones pesadas en tiempo real (`COUNT(*)`, `SUM()`) sobre tablas principales con millones de filas.
3. Usar índices compuestos `(team_id, day)` o `(user_id, created_at)` para queries de series temporales.
4. Definir encabezados de caché `Cache-Control: private, no-store` (datos por usuario/tenant, no caché compartida).
5. Frontend: Carga diferida (lazy load) de librerías de gráficos y Skeletons de UI del tamaño exacto del gráfico.

**Por qué:** además de la UX, el runtime impone límites duros de CPU por request según el plan (verificar en docs oficiales de Cloudflare Workers los valores vigentes del plan contratado) — diseñar endpoints largos es diseñar contra el techo de la plataforma.

**[REQUIRED]** Contrato de reintentos para el cliente (el frontend lo implementa en su capa de API): reintentar automáticamente **solo** requests idempotentes (GET/PUT/DELETE, y POST con `Idempotency-Key`), solo ante fallos de red / 429 / 5xx (nunca ante 4xx, que son deterministas), con backoff exponencial y un máximo de 2-3 intentos. Un 429 se respeta: si trae `Retry-After`, ese es el mínimo a esperar.

**Por qué:** los reintentos sin estas tres condiciones (idempotencia, clase de error correcta, backoff) son la receta del efecto duplicado y de la tormenta de retries que convierte una degradación breve en un incidente.

---

## 13. Documentación mínima viable del contrato

**[REQUIRED]** Cada worker documenta su contrato público en su `README.md` (extiende Backend §15, que ya exige README por worker): por endpoint — método + ruta, auth (público/Bearer/firma), shape de request y response (o referencia al schema compartido de la sección 08), `error.code`s que puede devolver, y si es paginado/idempotente. Formato: markdown simple, mantenido en el mismo PR que cambia el endpoint.

**Por qué markdown y no OpenAPI:** el consumidor principal de esta documentación es una IA generando código y el propio developer — ambos leen markdown en el repo con cero toolchain. Un spec OpenAPI completo es mantenimiento constante para un solo consumidor interno; es complejidad especulativa hoy (misma lógica que la sección 07).

**[REQUIRED]** La fuente de verdad de los *shapes* es el paquete de contratos compartido (sección 08) — el README enlaza a los schemas, no los transcribe. Documentación que duplica el tipo a mano miente en cuanto el tipo cambia.

**[RECOMMENDED]** El catálogo global de `error.code`s (los transversales: `UNAUTHORIZED`, `VALIDATION_ERROR`, `NOT_FOUND`, `RATE_LIMITED`, `INTERNAL`) vive en un solo archivo del paquete compartido, exportado como constantes — agregar un code nuevo pasa por ahí, lo que evita que dos workers inventen dos nombres para el mismo error.

**[RECOMMENDED]** Disparador para adoptar OpenAPI: el día que exista un consumidor externo (sección 07) — mismo evento que dispara el versionado. Antes de eso, no.

---

## Checklist rápido antes de dar por terminado un endpoint

- [ ] ¿Ruta con sustantivo plural, máximo 2 niveles de anidado, servida por el worker dueño del prefijo?
- [ ] ¿Método con semántica correcta — GET nunca muta, PATCH parcial como default, acciones de negocio como `POST /recurso/:id/accion`?
- [ ] ¿Status code del catálogo de la sección 03 — nunca 200 con error en el body, 404 (no 403) para recursos de otro usuario?
- [ ] ¿Errores con `code` estable del catálogo compartido + `details` por campo en validación?
- [ ] ¿`snake_case`, fechas ISO 8601 UTC, dinero en centavos enteros + `currency`?
- [ ] ¿Colección que crece → paginada desde el día uno, con `limit` default 20 / max 100 y bloque `pagination` en la respuesta?
- [ ] ¿`sort`/filtros validados contra whitelist explícita — nunca interpolados al query?
- [ ] ¿Sin `/v1` ni versionado; el cambio es aditivo, o siguió expand → migrar → contract?
- [ ] ¿Shapes de request/response desde el paquete de contratos compartido, no tipados dos veces?
- [ ] ¿CORS con origin ecoado desde whitelist + `Vary: Origin` — jamás `*`; header nuevo agregado al preflight?
- [ ] ¿Autenticado por defecto; identidad solo desde el token verificado, nunca del body/URL?
- [ ] ¿Escritura crítica con `Idempotency-Key` respaldado por unique constraint en Postgres (no solo KV)?
- [ ] ¿Trabajo >500ms encolado con recurso de estado, no request abierto?
- [ ] ¿README del worker actualizado en el mismo PR — endpoint, auth, codes, link a schemas?
