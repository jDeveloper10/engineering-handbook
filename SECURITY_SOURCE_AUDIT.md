---
title: "Auditoría defensiva de código y superficie pública — Gruapp"
category: project_audit
doc_type: runbook
status: DRAFT
confidence: 95%
reviewed: false
updated: 2026-09-15
sources:
  - "Código actual de ViaYa/Gruapp (backend, web, mobile, backend-push)"
  - "Respuestas HTTP públicas de producción, 2026-09-15"
  - "ENGINEERING_HANDBOOK/05_Security/SECURITY_ENGINEERING_STANDARD.md"
  - "ENGINEERING_HANDBOOK/05_Security/SECRET_LEAK_PREVENTION_STANDARD.md"
  - "ENGINEERING_HANDBOOK/05_Security/ESTANDAR_RATE_LIMITING.md"
---

# Auditoría defensiva de código y superficie pública — Gruapp

## Alcance y método

Revisión **de solo lectura**: código, configuración, bundle existente y respuestas HTTP públicas. No se cambiaron rutas, datos, configuración ni se ejecutaron ataques de fuerza bruta, cargas maliciosas, IDOR contra cuentas ajenas ni despliegues.

La coordinación se registró primero en `AUDIT_COORDINATION.md` y `AI_COORDINATION.md`. Esta auditoría contradice conclusiones previas cuando la evidencia actual lo exige; no convierte una ausencia de evidencia en aprobación de producción.

| Control pedido | Evidencia usada | Veredicto |
|---|---|---|
| IDOR de vehículos/solicitudes | Rutas + servicios + pruebas de autorización | Protegido para recursos JSON; fotos son una excepción pública documentada. |
| Escalada de rol | Middleware y 153 pruebas locales | Protegido en rutas de rol revisadas. |
| Inyección SQL | 86 llamadas D1 revisadas; consultas dinámicas inspeccionadas | No se encontró interpolación de input en SQL. |
| Inyección/XSS almacenado | Zod/manual validation + sinks React/HTML | Sin sink XSS actual; faltan sanitización central y CSP web. |
| Secretos/tokens | escáner de bundle + búsqueda de fuente/logs | Sin secreto de proveedor hallado; hay exposición de tokens en logs y almacenamiento cliente. |
| Fuerza bruta | implementación y pruebas, no ataque en producción | Doble límite implementado; cobertura real de DO/fallback debe quedar como gate. |
| CORS/CSP/headers | `curl` real a producción + middleware | API fuerte salvo localhost en producción; CSP web falta. |
| Enumeración de usuarios | flujo register/login + tests | Login protegido; registro enumera. |
| Uploads | handlers y R2 service | Propiedad protegida; falta validación por magic bytes. |

## Hallazgos que bloquean la aprobación de seguridad

### SEC-01 — CORS de producción admite cualquier `localhost` con credenciales

**Severidad: P2 / Alta. Estado: confirmado en producción.**

**Caso de estudio.** La intención es que `ALLOWED_ORIGIN` sea una lista cerrada. Sin embargo, `getAllowedOrigin()` primero intenta la lista y luego permite `http://localhost:<cualquier puerto>` sin condicionar a desarrollo. Con la cookie `SameSite=None; Secure` y `Access-Control-Allow-Credentials: true`, una aplicación local que corra en un puerto arbitrario puede hacer lecturas y mutaciones autenticadas con la sesión del navegador.

**Evidencia de código.** `backend/src/middleware/cors.ts:29-31` permite `^http://localhost:\d+$` para cualquier entorno. `backend/src/utils/response.ts:120` crea la cookie de sesión con `SameSite=None`.

**Evidencia real (2026-09-15).** Preflight a `https://gruas-api.gruas-api.workers.dev/api/auth/me` con `Origin: http://localhost:3999` devolvió HTTP `204` y:

```http
Access-Control-Allow-Origin: http://localhost:3999
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: Content-Type, Authorization
```

El mismo preflight con `Origin: https://attacker.example` devolvió `403`, así que no es un comodín global; la excepción localhost sigue siendo una relajación de producción no justificada.

**Contradicción registrada.** `AI_COORDINATION.md` decía que CORS no reflejaba un origen malicioso. Eso es cierto para `https://attacker.example`, pero insuficiente: `http://localhost:3999` sí se refleja y es un origen no incluido en `backend/wrangler.toml` de producción.

**Recomendación.** Permitir localhost solamente si `ENVIRONMENT === 'development'`; en producción aceptar exclusivamente `ALLOWED_ORIGIN`. Añadir regresión que pruebe que `Origin: http://localhost:3999` recibe 403 bajo perfil production.

### SEC-02 — La web publicada no entrega CSP

**Severidad: P1 / Alta. Estado: confirmado en producción.**

**Caso de estudio.** La API JSON sí añade una CSP estricta, pero la aplicación web que ejecuta JavaScript y almacena el bearer token no tiene una CSP que reduzca el impacto de una inyección futura o de una dependencia comprometida.

**Evidencia real.** `curl -I https://gruapp.pages.dev/` devolvió 200 con `X-Content-Type-Options: nosniff` y `Referrer-Policy`, pero sin `Content-Security-Policy`, `Strict-Transport-Security`, `Permissions-Policy` ni `X-Frame-Options`. En el proyecto tampoco existe `frontend/web/public/_headers` ni configuración Pages equivalente; sólo hay `public/_redirects`.

**Recomendación.** Añadir `_headers` para la web con una CSP basada en sus orígenes reales (scripts propios; conexiones al Worker y, si se usa, proveedor de mapas), HSTS, `frame-ancestors 'none'`, `base-uri 'self'`, `object-src 'none'` y `Permissions-Policy` mínimo. Verificar el header desde `gruapp.pages.dev` después del deploy. No copiar la CSP de la API (`default-src 'none'`), porque rompería la SPA.

### SEC-03 — Tokens de sesión accesibles a JavaScript del navegador y al almacenamiento no cifrado de Expo

**Severidad: P2 / Alta. Estado: confirmado por código.**

**Caso de estudio.** El login devuelve el bearer token además de configurar cookie HttpOnly. La web lo guarda en `localStorage` y lo adjunta a cada llamada; la app lo guarda en `AsyncStorage`. Cualquier XSS en la web puede extraer el token. En móvil, `AsyncStorage` no es un almacén criptográfico de secretos y aumenta el impacto en dispositivos comprometidos/backups.

**Evidencia.** `frontend/web/src/services/api.ts:67-75,101-103,187` usa `localStorage('rescue_token')`; `mobile/services/storage.ts:211-223` usa `AsyncStorage('@gruapp_auth_token')`. La ausencia de CSP web está confirmada en SEC-02.

**Recomendación.** Para la web, migrar a la cookie HttpOnly ya emitida y dejar de devolver/persistir bearer tokens donde sea compatible con el WebSocket. Para Expo, usar `expo-secure-store` para el token. Esto requiere plan de migración de sesión y pruebas de logout/realtime, no un cambio cosmético.

### SEC-04 — Upload de fotos confía en `Content-Type`; no verifica contenido real

**Severidad: P2 / Media-Alta. Estado: confirmado por código.**

**Caso de estudio.** Un cliente autenticado puede enviar bytes arbitrarios y declarar `Content-Type: image/jpeg`. Los handlers sólo comparan ese header y el tamaño; R2 almacena el blob con ese mismo tipo. `nosniff` reduce ejecución en navegador, pero no convierte el archivo aceptado en una imagen ni evita almacenamiento de contenido no permitido.

**Evidencia.** `backend/src/routes/client/vehicles.ts:55-67` y `backend/src/routes/users/uploadPhoto.ts:25-35` validan header/tamaño; `backend/src/services/vehicle.service.ts:85-107` y `backend/src/services/userPhoto.service.ts:26-45` escriben directamente a R2. No hay lectura de magic bytes/decodificación de JPEG, PNG o WebP.

**Recomendación.** Antes de persistir, leer una ventana inicial y validar magic bytes para JPEG/PNG/WebP, imponer límite antes de cargar todo el blob y, si es posible, recodificar/normalizar la imagen. Añadir casos: HTML renombrado `.jpg`, JPEG truncado y WebP inválido → 400 sin objeto R2.

**ARREGLADO (Claude, 2026-09-15).** Nuevo `backend/src/utils/fileSignature.ts`
(`matchesDeclaredImageType`) lee los primeros bytes reales del `Blob` y los
compara contra la firma binaria del `Content-Type` declarado (JPEG `FF D8
FF`, PNG los 8 bytes de cabecera completos, WebP `RIFF....WEBP`). Se invoca
desde `uploadUserPhoto` y `uploadVehiclePhoto` justo antes del `.put()` a
R2 — el caso de estudio exacto de este hallazgo (HTML renombrado a `.jpg`)
ahora se rechaza con `400 VALIDATION_ERROR` antes de tocar el bucket.
Regresión: `backend/tests/regression.photo-upload-magic-bytes.test.ts` (5
tests, cubre ambos endpoints con el ataque real y con JPEG/PNG genuinos).
Suite completa 161/161, `tsc --noEmit` limpio, desplegado a producción
(`wrangler deploy`, Version ID `b263635f-6ad5-4d4d-818f-6d4e1a9659eb`) y
re-verificado en vivo con una cuenta desechable: el mismo payload que antes
se aceptaba ahora devuelve el error de validación en ambos endpoints; un
JPEG real sigue subiendo sin problema. Detalle completo en
`SECURITY_AUDIT_LIVE.md` §7. SEC-04 queda cerrado.

### SEC-05 — El Worker de APNs registra tokens completos al fallar una entrega

**Severidad: P2 / Media-Alta. Estado: confirmado por código.**

**Caso de estudio.** Los resultados de fallos incluyen `token: message.to`; el Worker escribe `JSON.stringify(failed)` en consola. Eso deja tokens de dispositivo/Live Activity completos en logs operativos, contradiciendo el contrato de `backend/src/utils/logger.ts` de no registrar tokens completos.

**Evidencia.** `backend-push/src/index.ts:143` y `:164`; las funciones `sendToApns` / `sendLiveActivityUpdate` construyen resultados con el token completo (`:78`, `:124`).

**Recomendación.** Nunca devolver el token desde esas funciones ni loguearlo. Registrar sólo conteo, status y un identificador no reversible (hash con secreto/rotado, o sufijo mínimo si se justifica). Crear prueba que falle un dispatch y aserte que el log no contiene el token.

### SEC-06 — Registro público revela si correo/teléfono ya existe

**Severidad: P3 / Media. Estado: confirmado por código y prueba.**

**Caso de estudio.** Login devuelve el mismo `401 Credenciales inválidas` para usuario existente e inexistente y tiene límite por identidad, pero registro devuelve `409` y mensajes distintos de duplicado. Un actor puede enumerar cuentas mediante el formulario de alta.

**Evidencia.** `backend/src/services/auth.service.ts:29-35` lanza `CONFLICT:Ya existe…`; `backend/src/routes/auth/register.ts:55-65` entrega 409 al cliente. `backend/tests/auth.test.ts:31-50` codifica esa conducta. En contraste, `auth.service.ts:67-77` y `backend/tests/auth.test.ts:91-112` confirman la protección correcta del login.

**Recomendación.** Definir la política explícita: si se permite revelar por UX, aceptarlo con rate-limit por identidad también en registro; si no, devolver respuesta indistinguible y canalizar la recuperación de cuenta. No afirmar “cero enumeración” mientras siga 409.

### SEC-07 — WebSocket acepta cookie cross-site y retransmite mensajes no autenticados por rol

**Severidad: P2 / Media. Estado: confirmado por código; explotación externa requiere conocer un `requestId`.**

**Caso de estudio.** El handshake valida que sea participante, pero no comprueba `Origin`. Tras conectar, el Durable Object no conserva identidad/rol y reenvía cualquier payload a todos los demás sockets. Un conductor puede enviar una ubicación arbitraria —el cliente web la acepta como ubicación del conductor— y una web externa con la cookie de un conductor podría abrir un socket si conoce el ID de la solicitud.

**Evidencia.** `backend/src/routes/realtime/socket.ts:16-42` no valida `Origin`; `backend/src/durable/realtimeChannel.ts:46-54` relay ciego; `frontend/web/src/features/towing/screens/Tracking.tsx:107-112` acepta `{type:'location',lat,lng}` sin emisor/firma. La cookie de `SameSite=None` está en `backend/src/utils/response.ts:120`.

**Recomendación.** Validar Origin en handshake contra allowlist; transportar identidad/rol verificable al Durable Object o separar canales publish-only para conductor. Validar schema/rangos de payload y aceptar eventos de ubicación exclusivamente de la identidad conductor asignada. Añadir tests de participante cliente intentando publicar ubicación y de Origin externo.

## Salvedades de autorización y propiedad

### IDOR de JSON: controles presentes, no equivalen a una autorización completa de fotos

**Evidencia positiva.**

- Solicitudes de cliente se resuelven por `id AND client_id` en `backend/src/db/serviceRequests.ts:142-153`; cancelación conserva el mismo `client_id` (`:425-469`).
- Vehículos se validan contra `vehicle.user_id === userId` antes de borrar/subir (`backend/src/services/vehicle.service.ts:54-62,88-91`).
- Mutaciones del conductor comprueban `request.driver_id === driverId` (`backend/src/services/driver.service.ts:257-259,354-356`).
- Órdenes de taller se consultan por `id AND workshop_id` (`backend/src/db/workshopOperations.ts:97-101`); la bahía se comprueba como perteneciente al taller (`backend/src/routes/workshop/operations.ts:65-69`).
- `backend/tests/authorization.test.ts` pasa con controles cliente→driver/admin 403 y rol refrescado desde D1. La suite completa ejecutada localmente el 2026-09-15: **153/153** pruebas pasan.

**Salvedad necesaria.** `GET /api/vehicles/:id/photo` y `GET /api/users/:id/photo` son explícitamente públicos (`backend/src/routes/vehicles/photo.ts`, `backend/src/routes/users/photo.ts`). IDs no secuenciales reducen enumeración, pero no aplican propiedad ni vencimiento: quien conozca un ID recibido durante un servicio puede recuperar la foto sin sesión. Es una decisión de privacidad que debe aprobarse explícitamente; no se puede contar como "IDOR cerrado" para fotos. Los IDs inexistentes dieron 404 real sin filtrar metadatos.

### Aceptar solicitudes no reafirma disponibilidad geográfica en la mutación

**Severidad: P2 / Media.** `listAvailableRequests()` filtra por estado, ubicación y radio, pero `acceptRequest()` sólo rechaza conductor suspendido/ocupado y `acceptServiceRequestAtomic()` sólo exige `status='pending' AND driver_id IS NULL` (`backend/src/services/driver.service.ts:139-183,194-207`; `backend/src/db/serviceRequests.ts:319-359`). Un conductor con un ID conocido puede intentar aceptar una solicitud fuera de su feed/radio; tampoco se exige `available` en el mutador. Los IDs aleatorios reducen descubrimiento, no sustituyen autorización contextual.

**Recomendación.** Revalidar perfil `available`, frescura de GPS y distancia dentro de la operación de aceptación antes del UPDATE atómico (o materializar la regla en el UPDATE). Cubrir el caso en test con dos conductores/una solicitud fuera del radio.

## Validación, SQL y XSS

### SQL injection: no confirmada en la revisión

Las consultas D1 revisadas usan `prepare(...).bind(...)`. Las pocas consultas en variables (`backend/src/db/admin.ts` y `backend/src/db/serviceRequests.ts:488-505`) se forman desde SQL fijo y un conjunto de estados hard-coded, no desde parámetros del usuario. No se encontró concatenación de input dentro de SQL. Esto no es una garantía futura: debe mantenerse una prueba/linter contra interpolación en `.prepare()`.

### Validación: base fuerte, con zona manual de taller

Auth, vehículos, solicitudes, cambios de estado y perfil usan schemas Zod estrictos en `backend/src/utils/schemas.ts`. Las operaciones de taller (`backend/src/routes/workshop/operations.ts:163-174`) usan helpers manuales en lugar de Zod: no aceptan strings vacíos ni exceden máximos básicos, pero no son `.strict()`, no limitan `duration_minutes` a no negativo y no centralizan reglas de formato. No hay evidencia de SQLi por ello, pero incumple S-001 y hace más probable una regresión.

### XSS almacenado: no hay exploit confirmado en los sinks actuales

Campos como `description`, `address`, `business_name` y nombres no se sanitizan en backend; sí tienen longitud/formato. La búsqueda no encontró `dangerouslySetInnerHTML`, `innerHTML`, `eval`, `document.write` ni `new Function` en web/mobile. React escapa texto por defecto. El único HTML generado, `frontend/web/src/features/history/screens/Receipt.tsx:73-99`, escapa `&`, `<` y `>` antes de crear el Blob.

Esto es **una salvedad, no una aprobación**: SEC-02 deja sin CSP a la web y no existe una capa de sanitización/encoding contractual para nuevos sinks. Añadir pruebas con payloads `<img onerror=...>` en descripción/nombre y verificar renderizado como texto tras una respuesta real.

## Fuerza bruta, respuestas y secretos

### Rate limiting

`backend/src/utils/rateLimit.ts` aplica límite por IP (10/min) y por identidad (10/15min) para login. `backend/tests/http-surface.test.ts:68-113` cubre 429 y `Retry-After`; las 153 pruebas pasaron. La llave IP usa `CF-Connecting-IP`, no `X-Forwarded-For`, lo correcto en Cloudflare.

**Salvedad de producción.** El código hace fallback a KV si falla Durable Object y finalmente fail-open si KV falla (`rateLimit.ts:109-169`). El binding DO está declarado en `backend/wrangler.toml`, pero esta auditoría no induce una caída de infraestructura: queda pendiente probar/monitorizar que producción no entra en fallback y no usar el resultado de tests locales como prueba de resistencia a rotación de IP.

### Respuestas sensibles y bundles

- `auth.service.ts:79-81` elimina `password_hash` antes de responder; `backend/tests/auth.test.ts:24-29` cubre explícitamente esa regresión.
- El escáner del handbook sobre `frontend/web/dist` y `frontend/web/src` devolvió **0 secretos detectados**. Búsqueda adicional no halló PEM, Stripe live keys, AWS keys ni variables `VITE_` sensibles; `VITE_API_URL` es una URL pública.
- `backend-push/wrangler.toml` sólo contiene el bundle ID; la clave APNs se obtiene desde bindings secretos, no está en fuente.
- El build de web (`frontend/web/package.json`) no ejecuta automáticamente el escáner de secretos. El resultado actual es bueno, pero falta el gate pre-build exigido por SEC-LEAK-003.

## Headers reales de producción

| Superficie | Resultado real | Veredicto |
|---|---|---|
| API `/api/health` | CSP `default-src 'none'`, HSTS, `nosniff`, DENY, `no-referrer`, no-store, Permissions Policy | Correcto. |
| API Origin `https://attacker.example` | Sin ACAO; OPTIONS 403 | Correcto. |
| API Origin `http://localhost:3999` | ACAO reflejado + credentials, OPTIONS 204 | Hallazgo SEC-01. |
| Web `https://gruapp.pages.dev/` | `nosniff`/Referrer Policy, pero sin CSP/HSTS/frame protection | Hallazgo SEC-02. |

## Gate de seguridad para producción

No otorgar el check de seguridad mientras estén abiertos SEC-01 a SEC-05. Antes de aprobar, exigir evidencia reproducible de:

1. CORS production rechaza localhost arbitrario y sólo permite el frontend publicado.
2. La web publicada entrega CSP/headers compatibles y CSP report-only o pruebas de flujo que demuestren que no rompe mapas/login.
3. Uploads falsificados por contenido se rechazan y no quedan en R2.
4. Logs de push no contienen tokens; test de regresión incluido.
5. Token web no queda disponible en `localStorage` y token móvil usa almacenamiento seguro.
6. IDOR de foto tiene política explícita y pruebas: o requiere autorización contextual, o se documenta qué fotos pueden ser públicas y por cuánto tiempo.

