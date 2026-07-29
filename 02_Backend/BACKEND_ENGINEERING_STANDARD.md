---
title: "BACKEND ENGINEERING STANDARD"
category: 02_Backend
doc_type: estandar
tags:
  - standards
  - conventions
  - workers
  - rest-api
  - validation
  - error-handling
summary: "Nivel 1 del dominio Backend. Define la arquitectura multi-worker, handlers, servicios, middleware (auth, CORS, logging), validación, formato de respuesta, manejo de errores y testing para Cloudflare Workers."
keywords:
  - cloudflare-workers
  - handlers
  - middleware
  - services
  - deployment
updated: 2026-07-26
status: current
---

# BACKEND ENGINEERING STANDARD

> Nivel 1 del handbook para el dominio Backend. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica y después con una implementación de referencia en el stack actual (Cloudflare Workers, patrón multi-worker, Supabase).
>
> Este documento está fundado en el código real de `E:\workers-template` (13 workers en producción), no en una convención genérica de Node/Express. Cada regla marcada con "Evidencia real" cita el problema exacto ya presente en ese template — esto no es teoría, es deuda técnica medible hoy: `getCorsHeaders()` está redefinida idéntica en 7 de 13 workers, el chequeo de `Authorization: Bearer` está copiado en 6, y `createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY)` se repite 40 veces en todo el template.
>
> Objetivo: que un worker nuevo, escrito por una IA o por mí, no repita la misma deuda que ya tienen los 13 actuales.

---

## 00. Plataforma — el backend SIEMPRE es un Worker, nunca Pages Functions

**[REQUIRED]** El backend de todo proyecto se despliega como un **Cloudflare Worker** independiente (patrón multi-worker, sección 07), **nunca** como Pages Functions embebidas en el deploy del frontend. Frontend (Cloudflare Pages / assets estáticos) y backend (Worker) son **dos despliegues separados**: el frontend consume la API del Worker por su URL, con CORS centralizado (sección 03).

**Por qué:** todos los backends de este handbook son Workers standalone — es la convención fija del stack, no una decisión que se replantea por proyecto. Un Worker se versiona, observa (sección 10), escala y despliega (sección 16) de forma independiente del frontend; meter la lógica de backend dentro de `functions/` de Pages la acopla al ciclo de build del frontend, parte el runtime en dos y rompe la reutilización de todos los patrones de este estándar (que están fundados en `E:\workers-template`, no en Pages Functions). Ante la pregunta "¿Pages Functions o Worker?": siempre Worker.

**Implementación (Cloudflare):** carpeta/proyecto de worker propia con su `wrangler.jsonc` (`main`, `compatibility_date`, bindings D1/R2/KV), deploy con `wrangler deploy`. El frontend en Pages apunta a la URL del Worker vía variable de entorno (`VITE_API_URL` o equivalente); los bindings de datos (D1, R2, KV) viven en el **Worker**, no en el proyecto de Pages. La autenticación viaja por `Authorization: Bearer <token>` (sección 04), no por cookie de sesión acoplada al dominio — coherente con que la API es un servicio aparte consumido cross-origin.

---

## 01. API Response Format

**[REQUIRED]** Toda respuesta HTTP (éxito o error) se construye con un helper único reutilizado en todo el worker, nunca `JSON.stringify(...)` + `headers: {...}` repetido en cada rama del handler.

**Evidencia real:** en `user-worker/src/index.js` y `auth-worker/src/index.js`, el bloque `new Response(JSON.stringify({ error: ... }), { status, headers: { 'Content-Type': 'application/json', ...corsHeaders } })` aparece copiado 4-6 veces por archivo, con el `Content-Type` y el spread de `corsHeaders` repetidos a mano cada vez — un olvido de una sola coma rompe esa respuesta en silencio.

**Implementación (Cloudflare Workers):**
```js
function jsonResponse(body, status, corsHeaders) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders },
  });
}
const ok = (data, corsHeaders) => jsonResponse({ success: true, data }, 200, corsHeaders);
const fail = (code, message, status, corsHeaders) =>
  jsonResponse({ success: false, error: { code, message } }, status, corsHeaders);
```

**[REQUIRED]** La forma del error (`{ success: false, error: { code, message } }`) coincide con el `AppError` que espera el cliente de API del frontend (`FRONTEND_ENGINEERING_STANDARD.md` sección 6.3) — el backend y el frontend de este handbook comparten el mismo contrato de error, no dos formatos que alguien tiene que traducir en el medio.

---

## 02. Arquitectura del Worker — capas, no todo en `fetch()`

**[REQUIRED]** Un worker separa: **router** (qué ruta llama a qué handler) → **middleware** (auth, CORS) → **handler** (orquesta, sin lógica de negocio pesada) → **service** (lógica de negocio) → **acceso a datos** (Supabase/R2/KV). No toda la lógica vive dentro del único bloque `if (path === ...)` de `fetch()`.

**Evidencia real:** `user-worker/src/index.js` tiene el chequeo de auth, la validación del `Content-Type`, el parseo de `multipart/form-data`, la detección de tipo de archivo por magic bytes, el límite de tamaño, y la subida a R2 — todo en un único bloque `if` de ~70 líneas dentro de `fetch()`. Mismo problema que un componente de frontend que hace fetch + validación + formato + render en un solo lugar (`FRONTEND_ENGINEERING_STANDARD.md` sección 04).

**Implementación:**
```
worker-name/
├── src/
│   ├── index.js          # solo router + arma la Response final
│   ├── middleware/
│   │   ├── cors.js
│   │   └── auth.js
│   ├── handlers/
│   │   └── uploadAvatar.js
│   ├── services/
│   │   └── avatarService.js
│   └── lib/
│       └── response.js   # jsonResponse/ok/fail de la sección 01
└── wrangler.toml
```

---

## 03. CORS centralizado

**[REQUIRED]** `getCorsHeaders()` vive en un solo módulo compartido, no redefinida por worker.

**Evidencia real:** la misma función (idéntica salvo el método permitido) está copiada en `admin-worker`, `auth-worker`, `communications-worker`, `payments-worker`, `trading-worker` y `user-worker` — 6 copias del mismo código, que ya empezaron a divergir levemente entre sí (algunos incluyen `Access-Control-Allow-Credentials`, otros no).

**[RECOMMENDED]** Si el patrón multi-worker sigue creciendo, ese módulo compartido vive en un paquete interno (`shared/http/cors.js`) importado por cada worker, no copiado.

---

## 04. Autenticación — middleware único, no repetido por ruta

**[REQUIRED]** La validación de `Authorization: Bearer <token>` + `supabase.auth.getUser(token)` es una función reusada (`requireAuth(request, env)`), no reescrita en cada handler.

**Evidencia real:** el bloque `if (!authHeader?.startsWith('Bearer '))` seguido de `supabase.auth.getUser(token)` aparece igual en `user-worker` y `auth-worker`, y se repetirá en cada worker nuevo que necesite auth si no se centraliza ahora.

**Implementación:**
```js
async function requireAuth(request, env) {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return { error: fail("UNAUTHORIZED", "No autorizado.", 401) };
  const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
  const { data: { user }, error } = await supabase.auth.getUser(authHeader.replace("Bearer ", ""));
  if (error || !user) return { error: fail("UNAUTHORIZED", "Token inválido o expirado.", 401) };
  return { user, supabase };
}
```

---

## 05. Validación de entrada

**[REQUIRED]** El body/params de cada request se valida contra un schema (`zod`, mismo que usa el frontend — `FRONTEND_ENGINEERING_STANDARD.md` sección 6.2), no con `if` sueltos verificando campo por campo.

**Evidencia real:** en `user-worker`, la validación del archivo subido es una cadena de `if (!file)`, `if (typeof file === 'string')`, `if (!file.type?.startsWith('image/'))` sin un schema — frágil ante un caso no previsto, y sin mensaje de error consistente entre validaciones.

**[REQUIRED]** El backend **nunca** confía en que el frontend ya validó — la validación del cliente es solo UX (`FRONTEND_ENGINEERING_STANDARD.md` sección 9.2); la única validación real es la del servidor.

---

## 06. Variables de entorno — validadas una vez, no por ruta

**[REQUIRED]** Las variables de entorno requeridas se validan al primer punto de entrada del worker, no repetidas como `if (!env.SUPABASE_URL || !env.SUPABASE_SERVICE_ROLE_KEY)` dentro de cada rama.

**Evidencia real:** ese chequeo aparece calcado en `user-worker` y `auth-worker`.

**[REQUIRED]** Secretos nunca se comitean — se configuran con `wrangler secret put <NAME>`, documentados como comentario al inicio del archivo o en el `README.md` del worker. Esto ya se hace bien en el template actual (ver encabezado de `user-worker/src/index.js`) — se mantiene como estándar, no se cambia.

---

## 07. Patrón multi-worker — un worker, una responsabilidad

**[REQUIRED]** Cada worker tiene un dominio de responsabilidad claro (auth, pagos, trading, usuarios...) — mismo principio que la arquitectura por feature del frontend (`FRONTEND_ENGINEERING_STANDARD.md` sección 02), aplicado a nivel de servicio en vez de a nivel de carpeta.

**[REQUIRED]** Antes de agregar una ruta nueva a un worker existente, se pregunta: ¿esta ruta pertenece al dominio de este worker, o es un dominio nuevo que merece su propio worker? Agregar de más a un worker existente porque "ya está desplegado" reproduce el mismo anti-patrón que un componente de frontend que crece sin límite.

---

## 08. TypeScript

**[REQUIRED]** Todo worker **nuevo** se escribe en TypeScript desde el primer commit — mismo estándar no-negociable que el frontend (`FRONTEND_ENGINEERING_STANDARD.md` sección 07).

**Estado real:** los 13 workers de `workers-template` están en JavaScript plano, sin tipos. Esto es deuda técnica ya identificada (ver memoria de proyecto), no un ejemplo a seguir. **[RECOMMENDED]** migrar un worker a TS quede como parte del próximo cambio importante en ese worker, no una migración forzada de golpe de los 13 al mismo tiempo.

---

## 09. Manejo de errores

**[REQUIRED]** Errores devueltos al cliente siguen el contrato de la sección 01 (`{ success: false, error: { code, message } }`), con `code` estable (`UNAUTHORIZED`, `VALIDATION_ERROR`, `NOT_FOUND`...) que el frontend puede usar para lógica condicional, y `message` en español, seguro de mostrar al usuario (mismo principio de `FRONTEND_ENGINEERING_STANDARD.md` sección 6.3 — nunca un stack trace ni detalle interno).

**[REQUIRED]** El detalle técnico real del error (para debugging) se registra en logs del lado del servidor (sección 10), nunca se envía al cliente.

---

## 10. Logging y observabilidad

**[REQUIRED]** Logs estructurados (objeto, no string concatenado a mano) para poder filtrarlos después. **[REQUIRED]** nunca se loguea un secreto, token completo, o dato personal sensible — un token se trunca o se omite del log.

**[RECOMMENDED]** Cada request lleva un identificador de correlación (request ID) para poder rastrear un caso específico across logs cuando un usuario reporta un problema.

---

## 11. Rate limiting y abuso

**[REQUIRED]** Todo endpoint público que recibe input externo sin autenticación previa (webhooks, formularios públicos) tiene algún límite de tasa — sin esto, un endpoint como `mt5-webhook-worker` o `telegram-worker` es un vector de abuso directo.

**[RECOMMENDED]** Cloudflare Rate Limiting o un contador en KV/Durable Object como primera línea de defensa antes de llegar a la lógica de negocio.

---

## 12. Webhooks

**[REQUIRED]** Todo webhook entrante (MT5, Telegram, pagos) verifica la firma/token del remitente antes de procesar el payload — nunca se confía en un POST solo porque llegó a la URL correcta.

**[REQUIRED]** El procesamiento es idempotente — un webhook puede reintentarse/duplicarse por el proveedor, procesar el mismo evento dos veces no debe duplicar el efecto (ej. cobrar dos veces, enviar la señal dos veces).

**[RECOMMENDED]** Responder rápido (ack inmediato) y procesar trabajo pesado de forma asíncrona (Queue/Durable Object) en vez de bloquear la respuesta HTTP con lógica larga.

---

## 13. Acceso a datos (Supabase)

**[REQUIRED]** La `SUPABASE_SERVICE_ROLE_KEY` (acceso admin, bypassea Row Level Security) solo se usa server-side — nunca llega al frontend (ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` sección 12.2, reforzado aquí desde el lado que sí la posee).

**[REQUIRED]** Columnas explícitas en cada `select()` (`.select('status, role, created_at')`, no `.select('*')` por defecto) — ya se hace bien en varias partes del template actual, se mantiene como estándar: evita traer columnas sensibles o pesadas que la ruta no necesita.

**[RECOMMENDED]** Decidir explícitamente, por tabla, si la autorización se resuelve con Row Level Security de Postgres o a nivel de aplicación (el Service Role la bypassea) — no asumir que RLS protege algo que en realidad se accede siempre con la key admin.

---

## 14. Testing

**[REQUIRED]** Lógica de negocio (services) con unit tests, independiente del runtime de Cloudflare. **[RECOMMENDED]** tests de integración del `fetch()` del worker con `@cloudflare/vitest-pool-workers` (o Miniflare) para los flujos críticos (auth, pagos, webhooks).

**Estado real:** ningún worker del template tiene tests hoy — mismo principio que el frontend (`FRONTEND_ENGINEERING_STANDARD.md` sección 14): no se persigue cobertura total, se prioriza lo que rompe el negocio si falla (auth, pagos, procesamiento de señales).

---

## 15. Documentación por worker

**[REQUIRED]** Cada worker documenta, como mínimo: qué hace, variables de entorno requeridas, bindings (R2/KV/D1) requeridos. Ya se hace bien como comentario al inicio de `index.js` en varios workers del template — el estándar es formalizar eso en un `README.md` por worker a medida que crece, no solo un comentario.

---

## 16. Despliegue

**[REQUIRED]** Un `wrangler.toml` por worker con `compatibility_date` explícito (no omitido). Secretos vía `wrangler secret put`, nunca en el `.toml` ni comiteados. **[RECOMMENDED]** entornos separados (dev/staging/prod) cuando el worker maneja datos reales de usuarios (pagos, auth) — no todos los workers lo necesitan desde el día uno.

---

## 17. Git Workflow

Mismas reglas que `FRONTEND_ENGINEERING_STANDARD.md` sección 15 (Conventional Commits, PR revisable, CI mínimo antes de mergear) — no se duplican aquí, aplican igual a los workers.

---

## Checklist rápido antes de dar por terminado un worker/endpoint

- [ ] ¿Respuestas (éxito y error) construidas con un helper único, no `JSON.stringify` repetido?
- [ ] ¿Router → middleware → handler → service → datos, no todo en el bloque de `fetch()`?
- [ ] ¿CORS y auth centralizados, no copiados de otro worker?
- [ ] ¿Input validado con schema, nunca confiando en que el frontend ya validó?
- [ ] ¿Variables de entorno validadas una vez, secretos nunca comiteados?
- [ ] ¿Worker nuevo en TypeScript?
- [ ] ¿Error devuelto con `code` + `message` en español, sin detalle técnico?
- [ ] ¿Webhooks con verificación de firma e idempotencia?
- [ ] ¿`SUPABASE_SERVICE_ROLE_KEY` solo server-side, columnas explícitas en cada `select()`?
- [ ] ¿Test al menos del flujo crítico si el worker maneja auth/pagos/señales?

---

## 18. Workers como Único Backend

**[REQUIRED]** Este stack no tiene Express, Fastify, Django, ni VPS. Workers es el backend para TODOS los clientes: web, mobile (React Native/Expo), desktop (Tauri), IoT.

Documento completo: `02_Backend/WORKERS_AS_BACKEND.md`

Reglas rápidas:
- **WORKER-001:** Un solo stack de Workers para todos los clientes.
- **WORKER-002:** NUNCA un framework de servidor tradicional.
- **WORKER-003:** Lógica de negocio en Services, no en el handler.
- **WORKER-004:** Comunicación interna siempre con Service Bindings, nunca HTTP.

---

## 19. Notificaciones (Email + Push + In-App)

**[REQUIRED]** Todo sistema de notificaciones sigue el estándar `02_Backend/NOTIFICATIONS_STANDARD.md`.

### Canales disponibles

| Canal | Tecnología | Cuándo usarlo |
|---|---|---|
| Email | Resend + React Email | Transaccional, magic links, resúmenes semanales |
| Web Push | VAPID + Service Worker | Usuarios en navegador (online o con permisos) |
| Mobile Push | Expo Push → FCM/APNs | App React Native/Expo instalada |
| In-App | Supabase Realtime | Usuario activo en la app (badge + lista) |

### Reglas críticas

**[REQUIRED] NOTIF-001:** Email NUNCA con HTML crudo. Siempre React Email templates en `packages/email-templates`.

**[REQUIRED] NOTIF-002:** Emails se encolan en `NOTIF_QUEUE`. El handler HTTP no espera el envío.

**[REQUIRED] NOTIF-003:** VAPID private key solo en secretos del Worker. NUNCA en variables del frontend.

**[REQUIRED] NOTIF-004:** Push subscriptions con error 410 (expiradas) se eliminan automáticamente.

**[REQUIRED] NOTIF-005:** Mobile push usa Expo Push Service. NUNCA FCM ni APNs directo.

### Ejemplo mínimo de uso

```typescript
// Desde cualquier Worker, encolar una notificación — NUNCA await directo
await env.NOTIF_QUEUE.send({
  channel:  'email',
  template: 'invitation',
  to:       recipientEmail,
  data:     { inviterName: user.name, teamName: team.name, joinUrl }
})

await env.NOTIF_QUEUE.send({
  channel: 'web-push',
  userId:  recipientId,
  payload: { title: 'Nueva mención', body: `${user.name} te mencionó en ${doc.title}`, url: `/docs/${doc.id}` }
})
```
