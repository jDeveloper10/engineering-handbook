---
title: "CLOUDFLARE PLATFORM STANDARD"
category: cloud
tags:
  - standards
  - conventions
  - cloudflare
  - storage
  - limits-costs
  - workers
summary: "Nivel 1 del dominio Cloud. Define la plataforma Cloudflare: matriz de almacenamiento (Supabase, KV, R2, D1, DO, Queues), límites de Workers, WAF, rate limiting, Turnstile, DNS, cache CDN, costos por operación y observabilidad."
keywords:
  - pages
  - r2
  - kv
  - durable-objects
  - queues
  - d1
  - waf
  - turnstile
  - cdn
  - edge
updated: 2026-07-26
status: current
---

# CLOUDFLARE PLATFORM STANDARD

> Nivel 1 del handbook para el dominio Cloud. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica y después con implementación de referencia en el stack actual.
>
> **Qué cubre este documento:** la **plataforma** Cloudflare — qué servicio usar cuándo, configuración, límites y costos como criterios de diseño. **Qué NO cubre:** cómo escribir el código de un Worker (arquitectura interna, CORS, auth, validación) — eso vive en [`02_Backend/BACKEND_ENGINEERING_STANDARD.md`](../02_Backend/BACKEND_ENGINEERING_STANDARD.md) y no se repite aquí.
>
> **Contexto asumido:** developer solo / equipo muy pequeño, producto SaaS. Stack: Cloudflare Pages (frontend), Workers multi-worker (backend), R2 (archivos), Supabase como base de datos principal (no D1), y KV/Queues/Durable Objects según necesidad.
>
> **Sobre los números:** los límites y precios de Cloudflare cambian. Cada número de este documento es un **valor de referencia verificado el 2026-07-20** contra docs oficiales, no una ley — la regla real es siempre el objetivo/criterio que lo acompaña. Antes de diseñar algo que dependa de un límite exacto, verificar en `developers.cloudflare.com` (Workers → Platform → Limits, y la página de Pricing de cada producto).

---

## 00. Mapa de la plataforma (orientación en 20 líneas)

Cómo fluye un request del SaaS por las piezas que regula este documento:

```
Usuario / API client
   │
   ▼
DNS proxied (sección 09) ── la IP de origen nunca es pública
   │
   ▼
Edge de Cloudflare:
   WAF managed rules + rate limiting (10) ── corta abuso ANTES de facturar nada
   Cache CDN (08)                         ── un hit aquí no toca ningún worker
   │
   ├── ruta del frontend → Pages / static assets (05)  [requests gratis]
   │
   └── /api/* → Worker del dominio correspondiente (02, multi-worker del backend)
          │
          ├── service binding → otro worker interno (02)   [sin salir a Internet]
          ├── Supabase        → datos de negocio (01)      [fuente de verdad]
          ├── R2              → archivos (04)              [egress $0]
          ├── KV              → config/flags (03)          [eventual, solo lectura intensiva]
          ├── Queue           → trabajo diferido (06)      [el request no espera]
          └── Durable Object  → coordinación/contadores (07) [consistencia fuerte]
```

Regla de lectura del mapa: cuanto más arriba se resuelve un request (WAF → cache → static → worker), más barato y más rápido — el diseño empuja todo lo posible hacia arriba.

---

## 01. Matriz de decisión de almacenamiento

**[REQUIRED]** Antes de guardar cualquier dato nuevo, se elige el almacén con esta matriz — no "el que ya está bindeado en el worker". El criterio de decisión es: ¿qué consistencia necesita el dato, quién lo lee, y cuál es la fuente de verdad?

| Dato | Almacén | Criterio que lo decide |
|---|---|---|
| Datos de negocio (usuarios, suscripciones, pagos, entidades del SaaS) | **Supabase (Postgres)** | Necesita consistencia fuerte, transacciones, relaciones, RLS |
| Archivos binarios (avatares, uploads, exports, backups) | **R2** | Objetos grandes, egress gratis, no es dato relacional |
| Config/flags/datos que se leen mucho y cambian poco | **KV** | Lectura global de baja latencia, tolera minutos de staleness |
| Contadores, locks, estado en tiempo real, coordinación entre clientes | **Durable Objects** | Necesita consistencia fuerte + un único punto de escritura |
| Trabajo diferido (emails, webhooks salientes, procesamiento pesado) | **Queues** | No es almacenamiento — es tránsito con reintentos |
| Datos relacionales *edge-locales* de un solo worker, sin relación con el negocio | **D1** (excepcional) | Solo si Supabase no aplica — ver regla siguiente |

**Por qué:** cada almacén de Cloudflare tiene un modelo de consistencia distinto. Elegir por comodidad ("ya tengo el binding") produce bugs invisibles: un contador en KV pierde incrementos, un lock en KV no lockea, un dato de negocio en D1 queda huérfano del resto del modelo relacional.

**Ejemplos aplicados (casos reales del stack):**

```
"¿Dónde guardo el avatar del usuario?"
  → Binario, grande, no relacional → R2.
  → La URL/key del avatar (metadato) → columna en Supabase, junto al usuario.

"¿Dónde guardo cuántos requests hizo este usuario en el último minuto?"
  → Contador con escrituras concurrentes → Durable Object (o el Rate Limiting del edge, sección 10).
  → NUNCA KV (pierde incrementos) ni Supabase (una escritura por request mata la DB).

"¿Dónde guardo los feature flags por plan?"
  → Se lee en cada request, cambia poco, tolera minutos de staleness → KV.
  → La fuente de verdad editable → tabla en Supabase; un proceso la publica a KV al cambiar.

"¿Dónde guardo el estado de una suscripción de pago?"
  → Dato de negocio, consistencia fuerte, lo consultan varios workers → Supabase. Sin discusión.
```

**[REQUIRED]** La base de datos principal del SaaS es **Supabase, no D1**. D1 solo se considera para datos aislados, locales a un worker, sin relación con el modelo de negocio (ej. caché estructurada de un servicio externo, índice interno de un worker). Nunca datos de usuarios, pagos ni nada que el resto del sistema necesite consultar.

**Por qué:** el modelo de negocio ya vive en Supabase (auth, RLS, relaciones, dashboard, backups). Partir los datos de negocio entre dos bases de datos SQL crea el peor problema posible para un developer solo: dos fuentes de verdad sin transacciones entre sí, sin joins entre sí, con dos sistemas de migraciones. D1 además tiene límites de tamaño por base (referencia 2026: 10 GB por database — verificar en docs) que lo descartan como DB principal de un SaaS en crecimiento.

**[RECOMMENDED]** Si un dato podría vivir en dos almacenes y la duda persiste tras aplicar la matriz, va a Supabase. Es el default más barato de revertir: mover un dato de Postgres a KV después es trivial; reconstruir integridad relacional de datos regados en KV/D1 no lo es.

---

## 02. Workers — límites de plataforma como criterio de diseño

Estos límites definen qué diseño es viable, no son trivia. Valores de referencia verificados 2026-07-20 (plan Paid salvo indicación):

| Límite | Free | Paid | Implicación de diseño |
|---|---|---|---|
| Requests | 100.000/día | Sin límite (facturado) | Free solo para side-projects, no para el SaaS |
| CPU time por invocación | 10 ms | 30 s default, máx. 5 min configurable | La espera de I/O (`fetch`, Supabase, R2) **no** cuenta como CPU |
| Memoria | 128 MB | 128 MB | No bufferizar archivos grandes en memoria — streaming |
| Tamaño del worker (comprimido) | 3 MB | 10 MB | Vigilar dependencias; un SDK pesado puede comerse el bundle |
| Subrequests por invocación | 50 | 10.000 default (configurable hasta 10 M) | Loops de N llamadas por request escalan mal igual |
| Conexiones salientes simultáneas | 6 | 6 | Paralelizar de a lotes, no `Promise.all` de 50 fetches |

### Límites Duros Cloudflare (Cold Starts y Quotas)

**Workers:**
- **Cold start:** 0-400ms (primer request o después de inactividad).
- *Mitigación:* Scheduled CRON cada 5min para mantener warm.
- **CPU time:** 30s máximo (límite duro).

**R2:**
- **Objeto máximo:** 5TB (teórico), recomendado < 5GB.
- **Rate limiting:** 1000 writes/s por bucket.
- **No soporta partial uploads** (diferente a S3).

**Cuándo usar KV vs R2 (por límites):**
- **KV:** datos < 25MB, alta lectura, eventual consistency.
- **R2:** archivos grandes, consistencia fuerte, operaciones S3.

**[REQUIRED]** Ningún worker se diseña asumiendo CPU larga por request HTTP: el objetivo es mantener el CPU time típico por request en pocos milisegundos (el pricing cobra por CPU-ms — sección 13). Si una operación necesita CPU o duración sustancial (generar un PDF, procesar un archivo, llamar N APIs), no se hace inline en el request: se responde rápido y el trabajo se mueve a una Queue (sección 06) o, si es un flujo multi-paso con estado, a un Durable Object.

**Por qué:** un request HTTP síncrono ata la experiencia del usuario y el costo al peor caso del procesamiento. Mover el trabajo pesado fuera del request hace que el límite de CPU deje de ser un riesgo y que un pico de carga no degrade la latencia de todo el worker.

**[REQUIRED]** Archivos (uploads/downloads hacia R2) se manejan por **streaming** (`request.body` → R2, R2 → `Response`), nunca cargando el archivo completo a memoria con `arrayBuffer()` salvo que se necesite inspeccionarlo entero (ej. magic bytes de los primeros KB — leer solo lo necesario).

**Por qué:** con 128 MB de memoria por isolate, bufferizar un upload de 100 MB más su copia procesada mata el worker de forma intermitente — el tipo de bug que solo aparece en producción con el archivo grande de un usuario real.

**Implementación (streaming, no buffer):**
```js
// ❌ Carga todo el archivo a memoria antes de subirlo:
const buf = await request.arrayBuffer();
await env.BUCKET.put(key, buf);

// ✅ Stream directo del request al bucket (la memoria usada es constante):
await env.BUCKET.put(key, request.body, {
  httpMetadata: { contentType: request.headers.get("Content-Type") },
});

// ✅ Descarga: stream del bucket a la respuesta:
const obj = await env.BUCKET.get(key);
return new Response(obj.body, { headers: { "Content-Type": obj.httpMetadata.contentType } });
```

**[RECOMMENDED]** Fijar `limits.cpu_ms` explícito en la configuración de cada worker (ej. `cpu_ms: 1000` para un worker CRUD normal) como guardrail de costo: un bug con loop infinito se corta en 1 s en vez de quemar hasta 5 min de CPU facturable por request.

**Implementación (wrangler.toml):**
```toml
[limits]
cpu_ms = 1_000        # guardrail: este worker nunca debería necesitar más
```

**[RECOMMENDED]** Vigilar el tamaño del bundle en cada dependencia nueva (`wrangler deploy` reporta el tamaño comprimido). Criterio: si una dependencia agrega cientos de KB para una función que se puede escribir en 30 líneas, se escribe la función. El SDK de Supabase (`@supabase/supabase-js`) está aprobado; SDKs de AWS, ORMs pesados y librerías isomórficas grandes requieren justificación.

### Comunicación entre workers — service bindings

**[REQUIRED]** Cuando un worker del patrón multi-worker llama a otro worker de la misma cuenta, usa un **service binding**, nunca un `fetch` a la URL pública del otro worker.

**Por qué:** el service binding va directo de worker a worker sin salir a Internet: sin latencia de red pública, sin pagar un request extra (la invocación por binding no factura como request entrante nuevo — verificar pricing vigente), y sobre todo sin necesidad de que el worker destino exponga un endpoint público con su propia auth para tráfico que en realidad es interno. Un `fetch` a la URL pública convierte una llamada interna en superficie de ataque pública.

**Implementación (wrangler.toml del worker que llama):**
```toml
[[services]]
binding = "AUTH"           # env.AUTH.fetch(request) en el código
service = "auth-worker"
```

**[RECOMMENDED]** Un worker que solo recibe tráfico interno (solo lo llaman otros workers por binding) no tiene ruta pública: sin `routes`/`workers.dev` habilitado. Lo que no está expuesto no necesita defensa.

---

## 03. KV — solo para datos que toleran staleness

KV es **eventualmente consistente**: una escritura es visible de inmediato en la misma ubicación del edge, pero puede tardar hasta ~60 s (el `cacheTtl` de lectura, mínimo 30 s desde 2026-01) en verse en el resto del mundo. Además, escrituras concurrentes a la misma key se pisan: gana la última, sin merge.

**[REQUIRED]** En KV **nunca** se guarda:

- **Contadores ni acumuladores** (rate limits contados a mano, créditos, stock) — dos incrementos concurrentes se pisan y se pierde uno.
- **Locks o semáforos** — dos workers pueden leer "libre" a la vez; KV no puede garantizar exclusión mutua.
- **Datos leídos justo después de escribirse** (patrón write-then-read: crear algo y redirigir a la página que lo muestra) — la lectura puede llegar a otra ubicación y ver el valor viejo.
- **Nada donde perder una escritura o leer un valor viejo tenga costo de negocio** (estado de un pago, sesión que revoca acceso de inmediato).

Para todos esos casos: Durable Objects (consistencia fuerte, sección 07) o Supabase (transacciones).

**Por qué:** estos no son edge cases — son el comportamiento *documentado* de KV. Los bugs resultantes son intermitentes y dependen de la geografía del usuario, es decir, imposibles de reproducir en local, donde KV se comporta como consistente.

**[REQUIRED]** Lo que sí va en KV cumple los tres criterios: (1) se lee mucho más de lo que se escribe, (2) tolera minutos de valor viejo sin romper nada, (3) cada key la escribe un solo proceso (no hay escritores concurrentes de la misma key). Ejemplos válidos: feature flags, config pública, catálogo cacheado, tokens de servicios externos con horas de vida.

**[RECOMMENDED]** Toda key en KV lleva `expirationTtl` salvo que sea config permanente deliberada. **Por qué:** KV no tiene "vacuum" — sin TTL, los datos derivados se acumulan para siempre y nadie vuelve a limpiarlos; con TTL, el sistema se auto-limpia y el peor caso de un dato corrupto es su TTL.

**Implementación (referencia):**
```js
await env.CONFIG.put(`flags:${tenant}`, JSON.stringify(flags), { expirationTtl: 86_400 });
const raw = await env.CONFIG.get(`flags:${tenant}`, { cacheTtl: 300 }); // tolera 5 min de staleness → cachear 5 min
```

Límite de referencia (verificar en docs): valor máx. 25 MiB por key; 1 escritura/segundo por key; plan Free ~100k lecturas y ~1k escrituras por día — el free tier de escrituras es tan bajo que cualquier uso de KV como "base de datos" lo agota el primer día, otra señal de que KV es para leer, no para escribir.

---

## 04. R2 — objetos, acceso y ciclo de vida

**[REQUIRED]** Un bucket es **privado por defecto**. Solo se expone públicamente un bucket cuyo contenido es 100% público por diseño (assets de marketing, imágenes públicas del producto), y se expone vía **custom domain** conectado al bucket — nunca mezclando objetos públicos y privados en el mismo bucket "porque ya existía".

**Por qué:** el control de acceso de R2 es por bucket, no por objeto. Un solo objeto sensible en un bucket público es una filtración; separar por bucket hace la pregunta "¿esto puede ser público?" imposible de responder mal por accidente.

**[REQUIRED]** El acceso a objetos privados desde el navegador se hace con **URLs firmadas (presigned) de vida corta** generadas por un worker que ya validó la autorización del usuario — el objetivo es que la URL filtrada en un log o un chat expire sola; referencia práctica: minutos a pocas horas, nunca días. Alternativa igual de válida: el worker hace de proxy (`GET` → valida auth → `bucket.get()` → stream al cliente) cuando además se quiere ocultar la existencia del bucket o aplicar lógica por request.

**Por qué:** una URL sin expiración es una credencial permanente sin revocación. La decisión presigned-vs-proxy es de costo/control: presigned descarga el tráfico del worker (menos requests facturados); proxy da control por request (rate limit, watermark, logging) a cambio de pagar el request del worker.

**Implementación (presigned URL con `aws4fetch`, compatible con la API S3 de R2):**
```js
import { AwsClient } from "aws4fetch"; // librería mínima, no el SDK completo de AWS (sección 02)

const r2 = new AwsClient({ accessKeyId: env.R2_ACCESS_KEY_ID, secretAccessKey: env.R2_SECRET_ACCESS_KEY });
const url = new URL(`https://${env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${bucket}/${key}`);
url.searchParams.set("X-Amz-Expires", "900"); // 15 min — vida corta, la URL expira sola
const signed = await r2.sign(new Request(url), { aws: { signQuery: true } });
return ok({ url: signed.url }, corsHeaders); // el worker ya validó la autorización antes de firmar
```

**[REQUIRED]** CORS se configura **a nivel de bucket** solo cuando el navegador accede al bucket directamente (presigned URLs para upload/download), con `AllowedOrigins` explícitos del dominio del frontend — nunca `*` en un bucket que sirve contenido privado. Si el acceso es siempre vía worker-proxy, el CORS lo maneja el worker y el bucket no necesita política CORS.

**Implementación (CORS de bucket para upload directo con presigned URL):**
```json
[
  {
    "AllowedOrigins": ["https://app.midominio.com"],
    "AllowedMethods": ["GET", "PUT"],
    "AllowedHeaders": ["Content-Type"],
    "MaxAgeSeconds": 3600
  }
]
```

**[RECOMMENDED]** Reglas de lifecycle en todo bucket que acumula datos derivados o temporales: multipart uploads abortados se limpian (referencia: a los 7 días), exports/temporales expiran solos, y datos fríos que deben retenerse (backups, compliance) pasan a Infrequent Access (referencia 2026: $0.01/GB-mes vs $0.015 Standard, con costo de retrieval $0.01/GB — verificar en docs). **Por qué:** el almacenamiento es el único costo de R2 que crece solo y para siempre si nadie lo limpia; una regla de lifecycle es limpieza que no depende de que un humano se acuerde.

**Implementación (lifecycle, dashboard del bucket → Settings → Object lifecycle rules):**
```
Regla 1: prefix "tmp/"      → delete a los 7 días        (exports y temporales)
Regla 2: prefix "backups/"  → Infrequent Access a 30 días (retener barato, no borrar)
Regla 3: (todo el bucket)   → abort multipart uploads incompletos a los 7 días
```

**Egress gratis cambia las decisiones (vs S3).** En R2 la transferencia de salida cuesta $0 — lo que se paga es storage y operaciones (sección 13). Consecuencias de diseño que en AWS serían errores y aquí no:

- Servir archivos grandes directo a usuarios (videos, exports, descargas masivas) es viable sin CDN de pago intermedio.
- No hay razón de costo para comprimir/degradar agresivamente lo que se sirve — la variable de costo es cuántas *operaciones* se hacen, no cuántos GB salen.
- El anti-patrón cambia de dirección: en S3 se minimiza egress; en R2 se minimizan operaciones Class A/B por request (ej. no hacer un `head()` + `get()` cuando un `get()` basta, cachear en CDN lo cacheable — sección 08).

---

## 05. Pages — frontend estático + funciones mínimas

**[REQUIRED]** Pages sirve el frontend (build estático del SPA/SSG). La lógica de backend vive en los workers dedicados del patrón multi-worker (`02_Backend`), no regada en Pages Functions. Excepción aceptable: glue mínimo propio del frontend (headers, redirects, un proxy trivial), que se resuelve primero con `_headers`/`_redirects` antes que con código.

**Por qué:** el patrón multi-worker ya define dónde vive cada dominio de negocio (backend sección 07). Duplicar backend en Pages Functions crea una segunda población de endpoints con otro ciclo de deploy, otra config de secretos y sin las convenciones del estándar de backend. Nota 2026: Cloudflare orienta los proyectos nuevos hacia Workers con static assets como sucesor de Pages — no migrar lo existente sin razón, pero verificar el estado en docs antes de crear un proyecto nuevo.

**[REQUIRED]** Cada proyecto Pages define preview deployments (rama ≠ producción ⇒ URL de preview) y las env vars de preview apuntan a recursos de staging, nunca a producción. **Por qué:** el preview automático por PR es de las mejores features de Pages, pero un preview apuntando a la DB de producción convierte cada experimento en un riesgo real.

---

## 06. Queues — trabajo diferido con reintentos

**[REQUIRED]** Se mueve a una Queue todo trabajo que cumpla cualquiera de estas tres: (1) el usuario no necesita el resultado en la respuesta HTTP, (2) puede fallar y necesita reintento (llamar una API externa, enviar email, sincronizar un servicio), (3) llega en ráfagas que no se quieren procesar en ráfaga. Casos concretos del stack: envío de emails/notificaciones, post-procesamiento de webhooks (el webhook responde ack inmediato — backend sección 12 — y encola el resto), fan-out hacia servicios externos.

**Por qué:** un `fetch` a una API externa dentro del request del usuario hereda la latencia y la tasa de error de ese tercero. La cola convierte "falló el email" de un error 500 visible en un reintento automático invisible.

**[REQUIRED]** Todo consumer se configura con `max_retries` explícito y una **dead letter queue** — nunca la config por defecto sin DLQ, porque un mensaje que agota reintentos sin DLQ **se descarta silenciosamente** (comportamiento documentado). La DLQ debe tener un consumer mínimo o revisión periódica: una DLQ que nadie mira es el mismo descarte con un paso extra.

**Implementación (wrangler.toml):**
```toml
[[queues.consumers]]
queue = "emails"
max_batch_size = 10
max_retries = 5
retry_delay = 120            # backoff: no re-martillar a un tercero caído
dead_letter_queue = "emails-dlq"
```

**[REQUIRED]** Todo mensaje se procesa de forma **idempotente** (mismo principio que webhooks, backend sección 12): Queues garantiza *at-least-once*, así que el consumer puede recibir el mismo mensaje dos veces. El mensaje lleva un ID de operación y el efecto (insert, email, cobro) se aplica una sola vez por ID.

**Implementación (producer + consumer idempotente):**
```js
// Producer — en el handler HTTP, tras validar; el request responde sin esperar al efecto:
await env.EMAILS_QUEUE.send({ opId: crypto.randomUUID(), type: "welcome_email", userId });

// Consumer — el opId hace el efecto aplicable una sola vez:
async queue(batch, env) {
  for (const msg of batch.messages) {
    const { opId, type, userId } = msg.body;
    const done = await alreadyProcessed(env, opId);   // registro en Supabase (índice único por opId)
    if (done) { msg.ack(); continue; }
    try {
      await handle(type, userId, env);                 // relee el estado vigente desde Supabase
      await markProcessed(env, opId);
      msg.ack();
    } catch { msg.retry({ delaySeconds: 120 }); }      // reintento explícito con backoff
  }
}
```

**[RECOMMENDED]** El mensaje lleva referencias (IDs) y no payloads grandes: el consumer relee el estado actual desde Supabase/R2 al procesar. **Por qué:** además del límite de tamaño por mensaje (referencia: 128 KB — verificar en docs), un payload gordo encolado es una foto vieja del dato para cuando se procese; el ID obliga a leer la verdad vigente.

---

## 07. Durable Objects — cuándo se justifican

**[REQUIRED]** Un Durable Object se usa cuando el problema exige **un único punto de escritura con consistencia fuerte a escala de una entidad**: rate limiting serio por usuario/IP con contador exacto, coordinación en tiempo real (WebSockets de una sala/canal, presencia, colaboración), locks/semáforos, o una máquina de estados por entidad donde dos requests concurrentes no pueden pisarse. Es exactamente el complemento de la lista "nunca en KV" (sección 03).

**Por qué:** el DO es el único primitivo de Cloudflare que serializa accesos concurrentes a una entidad: todos los requests de la misma entidad llegan a la misma instancia única, en orden. Eso es lo que KV no puede dar y lo que en Supabase requeriría locks de Postgres con latencia de ida y vuelta a la región de la DB.

**[REQUIRED]** Un DO es sobre-ingeniería — y no se usa — cuando: el dato es de negocio y consultable (va a Supabase), es config de lectura global (KV), es trabajo diferido (Queue), o el "estado compartido" en realidad tolera eventual consistency. Test rápido: si no se puede nombrar la *entidad* cuyo acceso concurrente hay que serializar ("la sala X", "el contador del usuario Y"), no es un caso de DO.

**Por qué:** un DO es una instancia única por entidad — eso es su virtud y su costo: es un punto de serialización (throughput limitado por entidad), cobra duración además de requests, agrega una clase más con storage propio que respaldar y razonar, y sus datos quedan fuera del modelo consultable de Supabase. Para un developer solo, cada DO es un microservicio-con-estado más que mantener.

**Implementación (esqueleto del caso canónico — contador exacto por entidad):**
```js
export class UserRateLimiter {
  constructor(state) { this.state = state; }
  async fetch() {
    // Todos los requests del mismo usuario llegan a ESTA instancia, serializados:
    let count = (await this.state.storage.get("count")) ?? 0;
    if (count >= LIMIT) return new Response("limited", { status: 429 });
    await this.state.storage.put("count", count + 1);
    this.state.storage.setAlarm(Date.now() + 60_000); // el alarm resetea la ventana
    return new Response("ok");
  }
  async alarm() { await this.state.storage.deleteAll(); }
}
// En el worker: env.RATE_LIMITER.get(env.RATE_LIMITER.idFromName(userId)).fetch(...)
// idFromName(userId) = "la entidad a serializar" del test rápido de arriba.
```

**[RECOMMENDED]** El storage interno del DO guarda solo el estado operativo de la coordinación (el contador, la lista de conexiones, el estado de la máquina). Todo lo que el negocio necesite consultar o conservar se persiste en Supabase al cerrar el ciclo (fin de la sesión, snapshot periódico). **Por qué:** el storage del DO no tiene dashboard de consulta ni entra en los backups del modelo de negocio — es excelente memoria de trabajo y mal archivo histórico.

---

## 08. Cache — CDN y Cache API

**[REQUIRED]** La política de cache se decide por tipo de contenido, y el mecanismo es siempre headers correctos primero (el CDN de Cloudflare y el navegador los respetan solos):

| Contenido | Política (agnóstica) | Headers de referencia |
|---|---|---|
| Assets con hash en el nombre (JS/CSS/imgs del build) | Cachear "para siempre" — el hash cambia si el contenido cambia | `Cache-Control: public, max-age=31536000, immutable` |
| HTML de la app | No cachear en CDN (o revalidar siempre) — el HTML referencia el build vigente | `Cache-Control: no-cache` (o `max-age=0, must-revalidate`) |
| Respuestas de API autenticadas / por usuario | **Nunca** cachear en CDN compartida | `Cache-Control: private, no-store` |
| API pública idéntica para todos (catálogo, precios) | Cachear corto en edge, tolerando staleness definido | `Cache-Control: public, max-age=60` + `s-maxage` |
| Objetos de R2 servidos vía worker | Igual que assets si son inmutables; `private` si son por usuario | según el caso de arriba |

**Por qué:** los dos errores caros son simétricos: no cachear assets inmutables regala latencia y requests facturados en cada visita; cachear una respuesta autenticada en la CDN compartida sirve los datos de un usuario a otro — un incidente de seguridad, no de rendimiento.

**Implementación (archivo `_headers` en el build de Pages / static assets):**
```
/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*
  Cache-Control: no-cache
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

**[REQUIRED]** Nada por-usuario se cachea en cache compartida (CDN o Cache API). Si una respuesta depende del `Authorization` o de una cookie de sesión, lleva `private, no-store` y punto — la optimización de datos por usuario se hace en el cliente (React Query/SWR, dominio del frontend), no en el edge.

**[RECOMMENDED]** La Cache API (`caches.default`) dentro de un worker se reserva para respuestas *construidas* por el worker que son públicas y costosas de recomputar (agregaciones públicas, respuestas de terceros cacheables). Para assets y objetos ya cubiertos por el CDN con buenos headers, no agrega nada — es código extra para el mismo resultado. Nota operativa: la Cache API es por-datacenter (no global) y `cache.put` no aplica en todos los contextos — verificar en docs al usarla.

**[RECOMMENDED]** La invalidación se diseña para no necesitarse: contenido inmutable versionado por hash + TTLs cortos en lo mutable. El purge manual (`Purge Cache` por URL) es la herramienta de emergencia, no parte del flujo normal. **Por qué:** un sistema cuyo deploy requiere purge coordinado tiene una race condition permanente entre el deploy y el purge; el versionado por hash elimina la categoría entera de problema.

---

## 09. DNS

**[REQUIRED]** Todo registro DNS que apunta a algo servido por/detrás de Cloudflare (Pages, Workers, el SaaS mismo) va **proxied** (nube naranja). Es el default y la razón de usar Cloudflare: sin proxy no hay WAF, ni rate limiting, ni cache, ni ocultamiento de la IP de origen — un registro DNS-only publica la IP del origen y permite atacarlo directo, saltándose todas las reglas de la sección 10.

**[REQUIRED]** DNS-only (nube gris) se usa solo cuando el protocolo o el servicio lo exige y se documenta el porqué en el propio registro (campo comment): verificación de terceros que requiere ver el registro real, servicios no-HTTP en puertos no soportados por el proxy, o registros MX/SPF/DKIM (el mail no se proxea nunca).

**[RECOMMENDED]** Los registros DNS del dominio del SaaS se tratan como configuración versionada — como mínimo, un export periódico (la zona se exporta en formato BIND desde el dashboard) guardado en el repo de infraestructura. **Por qué:** DNS es el único sistema donde un cambio manual sin registro puede tumbar todo el producto y nadie recuerda cuál era el valor anterior.

---

## 10. WAF y rate limiting — base para un SaaS

**[REQUIRED]** Todo endpoint de autenticación y de escritura tiene rate limiting en el edge, antes de llegar al worker. Base mínima para el SaaS (los números son punto de partida a calibrar con tráfico real, no dogma):

- `/api/auth/*` (login, signup, reset password): límite agresivo por IP — objetivo: hacer inviable el credential stuffing sin molestar a un humano; referencia: ~5-10 requests/min por IP, con bloqueo temporal al excederlo.
- Endpoints de escritura (`POST/PUT/DELETE` de la API): límite laxo por IP — objetivo: cortar scripts desbocados y scraping, no usuarios legítimos; referencia: ~60-120/min por IP.
- Webhooks entrantes: límite dimensionado al proveedor que los envía (backend sección 11 exige que exista; aquí se define que la primera capa es el edge, no el worker).

**Por qué:** el rate limit en el edge se ejecuta antes de facturar el request del worker y antes de tocar Supabase — es la única capa que protege también el costo, no solo la disponibilidad. El rate limit dentro del worker (backend sección 11) es la segunda línea, no la primera.

**Implementación (regla de rate limiting en el dashboard — Security → WAF → Rate limiting rules):**
```
Regla "auth-brute-force":
  If:   http.request.uri.path wildcard "/api/auth/*"
  Rate: 10 requests / 1 min, por IP
  Then: Block por 10 min

Regla "write-abuse":
  If:   http.request.uri.path wildcard "/api/*"
        and http.request.method in {"POST" "PUT" "PATCH" "DELETE"}
  Rate: 100 requests / 1 min, por IP
  Then: Managed Challenge (no Block: un falso positivo humano puede resolverlo)
```

**[REQUIRED]** Las managed rules del WAF (core ruleset de Cloudflare) están activas en el dominio del SaaS. Se parte del ruleset gestionado y solo se agregan reglas custom cuando un ataque real lo pide — no se escribe un WAF casero por adelantado.

**[REQUIRED]** Bloqueo por país solo con una razón concreta y documentada (requisito legal, fraude medido desde una región sin usuarios legítimos) — nunca "por si acaso". **Por qué:** un SaaS vende globalmente por defecto; un país bloqueado por paranoia es mercado perdido en silencio, y los atacantes usan proxies del país permitido de todos modos.

**[RECOMMENDED]** "Under Attack Mode" (challenge a todo el tráfico) es un interruptor de emergencia durante un ataque activo, no un estado permanente — degrada la experiencia de todos los usuarios (interstitial de challenge) y rompe clientes de API. Si hay API pública, el modo se activa por regla sobre las rutas del frontend, no sobre `/api/*`, o los webhooks de terceros empezarán a fallar en silencio.

---

## 11. Turnstile

**[REQUIRED]** Turnstile (widget + verificación server-side del token en el worker) se coloca en todo formulario **público y anónimo** cuyo abuso cuesta dinero o reputación: signup (bloquea cuentas basura), formulario de contacto/soporte (bloquea spam), y reset de contraseña (bloquea enumeración de emails). La verificación del token en el servidor es la regla — el widget solo, sin `siteverify`, es decorativo.

**[REQUIRED]** Turnstile **no** se pone en flujos ya autenticados (el usuario ya demostró ser humano y tiene sesión; ahí la defensa es rate limiting, sección 10) ni en el login como primera medida — en login primero rate limiting agresivo, y Turnstile se agrega solo si hay credential stuffing medido que el rate limit no frena.

**Por qué:** cada challenge agrega fricción y un punto de fallo (usuarios con JS bloqueado, accesibilidad). El criterio es asimétrico: en formularios anónimos el costo del abuso lo paga el negocio y la fricción es aceptable; en flujos autenticados el abuso ya está acotado por la cuenta y la fricción solo castiga a usuarios legítimos.

**Implementación (verificación server-side en el worker, antes de la lógica del form):**
```js
const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    secret: env.TURNSTILE_SECRET_KEY,      // wrangler secret, nunca en el frontend
    response: token,                       // token que envió el widget desde el form
    remoteip: request.headers.get("CF-Connecting-IP"),
  }),
});
const { success } = await res.json();
if (!success) return fail("TURNSTILE_FAILED", "Verificación anti-bot fallida.", 403, corsHeaders);
```

---

## 12. Seguridad de la cuenta Cloudflare

La cuenta Cloudflare controla DNS, WAF, workers y buckets — comprometerla es comprometer todo el producto a la vez. Mismo nivel de criticidad que la cuenta de Supabase.

**[REQUIRED]** 2FA activo en la cuenta (idealmente con hardware key o TOTP, no SMS). Sin excepción — es la cuenta que puede redirigir el DNS del producto a cualquier lado.

**[REQUIRED]** La **Global API Key no se usa nunca** para nada: ni en scripts, ni en CI, ni "solo para probar". Todo acceso programático usa **API Tokens** con scope mínimo: permisos concretos (ej. `Workers Scripts:Edit`), recursos concretos (una zona, una cuenta), y idealmente TTL o restricción de IP para tokens de CI. Un token por proyecto/uso — el token de deploy de CI no es el token del script de backups.

**Por qué:** la Global API Key equivale a la contraseña de la cuenta: no expira, no tiene scope y no se puede limitar — filtrada en un log de CI o un `.env` comiteado, entrega la cuenta entera. Un token con scope filtrado en el mismo lugar entrega solo lo que ese token podía hacer, y se revoca sin romper el resto.

**Implementación (tokens típicos del stack, cada uno con lo mínimo que necesita):**
```
Token "ci-deploy-workers"    → Account.Workers Scripts: Edit          (solo esta cuenta; para CI)
Token "ci-deploy-pages"      → Account.Cloudflare Pages: Edit
Token "r2-backups"           → Account.Workers R2 Storage: Edit       (idealmente limitado al bucket)
Token "terraform-dns"        → Zone.DNS: Edit                         (solo la zona del SaaS)
```

**[REQUIRED]** Los tokens viven como secretos (secret del CI, `wrangler secret`, gestor de contraseñas) — nunca en código, wrangler.toml, ni documentación (refuerza backend sección 06 desde el lado de la plataforma).

**[RECOMMENDED]** Revisión periódica (referencia: trimestral) de la lista de API tokens activos y miembros de la cuenta, revocando lo que ya no se usa. **Por qué:** los tokens huérfanos de experimentos viejos son credenciales vivas que nadie recuerda haber creado — la revisión convierte "no sé qué tokens existen" en una lista corta y justificada.

---

## 13. Costos — qué acciones disparan gasto real

**[REQUIRED]** El diseño de cualquier feature identifica qué **unidades facturables** consume por request de usuario, porque en Cloudflare no se paga por servidor sino por operación. Las que importan en este stack (referencia Workers Paid/Standard, verificado 2026-07-20 — verificar precios vigentes en docs):

| Unidad facturable | Incluido/mes (Paid $5) | Excedente (referencia) | Cómo se dispara sin querer |
|---|---|---|---|
| Requests de Workers | 10 M | ~$0.30/M | Polling agresivo del frontend; proxy de assets que el CDN podía servir |
| CPU-ms de Workers | 30 M | ~$0.02/M CPU-ms | Parsing/crypto pesado inline; loops sobre datos grandes en el request |
| R2 Class A (escrituras/listas: `put`, `list`, multipart) | 1 M | ~$4.50/M | `list` en un loop; multipart de miles de partes; escribir logs a R2 objeto por objeto |
| R2 Class B (lecturas: `get`, `head`) | 10 M | ~$0.36/M | Servir cada asset vía worker+`get` sin cache CDN delante |
| R2 storage | 10 GB | ~$0.015/GB-mes | Buckets sin lifecycle acumulando derivados para siempre (sección 04) |
| Egress de R2 | ∞ | $0 | — (esta es la que no existe; sección 04) |

Notas de costo que cambian diseños: los **subrequests no se facturan** como requests (llamar de un worker a otro por service binding o a R2/KV no duplica el costo de request); los requests a **static assets** de Workers/Pages son gratis; un request servido desde el cache del CDN no toca el worker ni factura nada de esta tabla.

**Por qué:** en un modelo por-operación, un anti-patrón barato en dev (un `list` de R2 por page-view, polling cada 2 s) escala linealmente con los usuarios hasta ser la línea más cara de la factura — y ninguna alarma lo avisa si nadie lo diseñó como unidad facturable desde el principio.

**[REQUIRED]** Los límites del plan Free se usan como criterio de decisión, no como esperanza: el SaaS en producción corre en Workers Paid (los 10 ms de CPU y 100k requests/día del Free no son para tráfico real de producto), y el Free queda para experimentos y side-projects donde quedarse sin cuota a mitad del día es aceptable.

**[RECOMMENDED]** Alertas de facturación configuradas (notificaciones de uso en el dashboard) con umbral bajo — el objetivo es enterarse de un patrón de costo nuevo la semana que aparece, no en la factura del mes siguiente.

---

## 14. Observabilidad de plataforma

El *código* de logging (logs estructurados, request ID, qué nunca loguear) es dominio del backend (sección 10 de ese estándar). Aquí va lo que la plataforma debe tener configurado para que esos logs sirvan de algo.

**[REQUIRED]** Todo worker de producción tiene observabilidad habilitada (Workers Logs) — sin esto, `console.log` se descarta y el primer bug de producción se debuggea a ciegas. `wrangler tail` es la herramienta de diagnóstico en vivo; los logs persistidos son los que permiten investigar algo que pasó ayer (retención de referencia en el plan Paid: días, no meses — verificar en docs; si un evento debe conservarse más, se persiste como dato, no como log).

**Implementación (wrangler.toml):**
```toml
[observability]
enabled = true
head_sampling_rate = 1     # 100% mientras el tráfico es bajo; bajar cuando el volumen cueste
```

**[REQUIRED]** Existen alertas de notificación (dashboard → Notifications) como mínimo para: tasa de errores de Workers elevada, y disponibilidad/salud del dominio (Health Checks o equivalente sobre el endpoint principal de la API). Criterio: un developer solo no mira dashboards — el sistema tiene que avisarle; una caída que descubre un usuario antes que el dueño es un fallo de esta regla.

**[RECOMMENDED]** Las métricas del dashboard de Workers (invocation statuses: `exceededCpu`, `exceededResources`, errores) se revisan tras cada deploy significativo — los límites de la sección 02 fallan con esos códigos exactos, y verlos en métricas es la diferencia entre "un usuario reporta algo raro" y saber qué límite se está rozando antes de que sea un incidente.

---

## Checklist rápido antes de dar por terminada una feature que toca la plataforma

- [ ] ¿Cada dato nuevo pasó por la matriz de almacenamiento (sección 01) — y los datos de negocio quedaron en Supabase, no en D1/KV?
- [ ] ¿Nada de CPU/duración pesada inline en un request HTTP — trabajo pesado en Queue o DO, archivos por streaming, `cpu_ms` como guardrail?
- [ ] ¿Llamadas entre workers por service binding (no fetch a URL pública), y workers internos sin ruta pública?
- [ ] ¿Nada en KV que sea contador, lock, o dato write-then-read? ¿Keys de KV con TTL?
- [ ] ¿Buckets R2 privados por defecto, acceso por presigned URL corta o worker-proxy, CORS con orígenes explícitos, lifecycle en buckets que acumulan?
- [ ] ¿Backend en los workers dedicados (no en Pages Functions), previews de Pages apuntando a staging?
- [ ] ¿Consumers de Queues con `max_retries` + DLQ vigilada, mensajes idempotentes y con IDs (no payloads gordos)?
- [ ] ¿Cada Durable Object nuevo justifica una entidad concreta que serializar — y su estado de negocio termina en Supabase?
- [ ] ¿Headers de cache según tipo de contenido — assets con hash `immutable`, API autenticada `private, no-store`, nada por-usuario en cache compartida?
- [ ] ¿Registros DNS proxied salvo excepción documentada en el comment del registro?
- [ ] ¿Rate limiting en el edge sobre `/api/auth/*` y endpoints de escritura, WAF managed rules activas, ningún país bloqueado sin razón escrita?
- [ ] ¿Turnstile en signup/contacto/reset (con verificación server-side), y no en flujos autenticados?
- [ ] ¿2FA en la cuenta, cero usos de la Global API Key, tokens con scope mínimo por proyecto y guardados como secretos?
- [ ] ¿Identificadas las unidades facturables que consume la feature por request, y alertas de uso configuradas?
- [ ] ¿Observabilidad habilitada en el worker, y alertas de errores/salud que avisan solas?

---

## Workers como Backend Único (Principio Fundamental)

> Documento detallado: `02_Backend/WORKERS_AS_BACKEND.md`

**Workers NO es un complemento. Workers ES el backend.** No existe Express, Fastify, Django, Rails, Laravel, ni ningún otro framework de servidor en este stack. Todo el backend son Workers.

### Lo que Workers reemplaza

| Tecnología tradicional | Reemplazada por | Ganancia |
|---|---|---|
| Express / Fastify / Koa | Workers `fetch()` handler | Edge global, cold start < 5ms |
| Django / Rails / Laravel | Workers + Supabase | Sin servidores que administrar |
| AWS Lambda / GCP Functions | Workers | Cold start 5ms vs 2-3s |
| VPS / Docker / Kubernetes | Workers + Cloudflare | Escalado infinito, $0 idle |
| Nginx / Apache | Cloudflare CDN | Incluido, sin configurar |
| PM2 / systemd | No necesario | Workers no se "caen" |
| Load balancers | Cloudflare | Distribución global automática |
| SSL certificates | Cloudflare | Automático, renovación infinita |
| Redis | KV | Key-value en el Edge |
| RabbitMQ / SQS | Cloudflare Queues | Colas sin servidores |
| Socket.io / Pusher | Durable Objects | WebSockets en el Edge |

### Workflow estándar

```
1. Cliente (web/mobile/desktop/IoT)  →  fetch() a la URL del api-gateway Worker
2. Gateway: auth + rate limit + CORS  →  Service Binding al worker interno
3. Worker interno: valida (Zod) + consulta (Supabase/D1/KV/R2/Queues)
4. Responde JSON (o HTML / PDF / binario)
5. Si trabajo > 15s  →  Encolar en Queues + responder 202 Accepted
```

### Lo que NO reemplaza (infraestructura de datos)

| Necesidad | Solución | Por qué no Worker |
|---|---|---|
| Base de datos relacional | Supabase / D1 | Workers no tienen estado persistente |
| Archivos y objetos | R2 | Límite de 100MB en request body |
| Caché con TTL | KV | Workers son stateless por diseño |
| Jobs asíncronos | Queues | CPU máx 30s por invocación |
| WebSockets / estado | Durable Objects | Workers sin estado entre requests |
