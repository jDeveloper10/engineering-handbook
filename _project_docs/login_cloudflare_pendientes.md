# Pendientes de arquitectura — Login (Cloudflare Workers + D1 + Pages)

**Última actualización:** 2026-08-03
**Estado del proyecto:** sin usuarios en producción todavía
**Tipo de documento:** bitácora de decisiones de un proyecto concreto. **No es un estándar del handbook** — no lleva reglas `[REQUIRED]`/`[RECOMMENDED]` ni entra en `INDEX.json`. Los estándares que aplican viven en los dominios numerados; ver la tabla de la sección 0.

---

## 0. Dónde vive cada tema en el handbook

Este documento registra **qué se decidió en este proyecto y qué falta**. La regla general de cada tema ya está escrita en el handbook; cuando haya conflicto, manda el estándar, no esta bitácora.

| Tema de este documento | Estándar que lo regula |
|---|---|
| Hashing de contraseñas, sesiones, autorización | `05_Security/SECURITY_ENGINEERING_STANDARD.md` |
| Bloqueo progresivo de login, gestión de sesiones, MFA | `05_Security/AUTH_ADVANCED_STANDARD.md`, `05_Security/AUTH_MFA_STANDARD.md` |
| Rate limiting (secciones 4 y 5) | `05_Security/ESTANDAR_RATE_LIMITING.md` |
| Webhooks de pago, idempotencia, validación de monto | `05_Security/PAYMENTS_SECURITY_STANDARD.md` |
| Email transaccional, SPF/DKIM/DMARC, deliverability | `02_Backend/EMAIL_ADVANCED_STANDARD.md` |
| Worker como backend, estructura de carpetas, middleware | `02_Backend/WORKERS_AS_BACKEND.md`, `02_Backend/worker-template/` |
| Elección KV vs D1 vs R2, límites de plataforma | `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` |
| Transacciones, integridad referencial, normalización | `04_Database/DATABASE_ENGINEERING_STANDARD.md`, `04_Database/D1_OPTIMIZATION.md` |
| Cookies y estrategia de cache | `00_Fundamentos/COOKIES_CACHE_OPTIMIZATION.md` |
| Versionado de API, contratos de respuesta | `03_API/API_ENGINEERING_STANDARD.md` |
| Degradación ante fallas de dependencias | `02_Backend/GRACEFUL_DEGRADATION_PATTERN.md`, `02_Backend/RETRY_PATTERN.md`, `02_Backend/CIRCUIT_BREAKER_PATTERN.md` |
| Logs estructurados, correlación, alertas | `07_DevOps/OBSERVABILITY_STANDARD.md` |
| Estrategia de tests | `06_Testing/ADVANCED_TESTING_STANDARD.md` |

---

## 1. Sesiones en D1 en vez de KV (prioridad: media, no urgente)

**Situación actual:** las sesiones se guardan y consultan en D1.

**Recomendación oficial de Cloudflare:** usar Workers KV para datos de sesión — lecturas de alta frecuencia, poca modificación, no requiere consistencia inmediata. Fuente: https://developers.cloudflare.com/workers/platform/storage-options/

**Por qué no es urgente:** el problema es de throughput/latencia bajo carga alta, no un fallo de seguridad. Sin usuarios reales todavía, no hay evidencia de que esto esté causando un problema medible.

**Cuándo revisarlo:** antes de tener tráfico real sostenido, o si empieza a verse latencia alta / errores de D1 en el middleware de auth.

**Acción concreta cuando se aborde:**
- Mover tabla `sessions` (o equivalente) a KV: `key = token`, `value = { user_id, expires_at }`.
- D1 se queda como fuente de verdad de `users` (no cambia).
- Decidir modelo de expiración: TTL nativo de KV (`expirationTtl`) vs. campo manual.

---

## 2. Hashing de contraseñas — RESUELTO ✅

**Decisión tomada:** PBKDF2 vía Web Crypto (`SubtleCrypto`), corre en el Worker (nunca en el cliente). Motivo: único que funciona nativo dentro del límite de CPU sin dependencias externas ni costo recurrente.

**Descartado, con razón documentada:**
- **Argon2id vía Worker Rust/WASM** — sobre-ingeniería para la etapa actual del proyecto. Reconsiderar solo si se manejan datos de alto valor (financieros, salud, etc.).
- **Auth0 / proveedor externo** — facturación por MAU con curva de overage agresiva (casos reportados: de $240/mes a $10,000+/mes al escalar). No conviene para un stack que se reutiliza en múltiples proyectos, porque el costo se acumula por proyecto. Reconsiderar solo si se necesita SSO empresarial o compliance certificado (SOC2/HIPAA) que sea costoso implementar por cuenta propia.

---

## 3. Tokens de sesión por tipo de cliente — RESUELTO ✅

El backend (Worker) es idéntico sin importar el cliente (web, desktop, APK, IPA). Lo único que cambia es **dónde se guarda el token en el dispositivo**:

| Plataforma | Almacenamiento del token |
|---|---|
| Web | Cookie `httpOnly` + `Secure` + `SameSite` |
| Desktop | Keychain del SO (macOS/Windows/Linux) |
| Android | EncryptedSharedPreferences / Android Keystore |
| iOS | iOS Keychain Services |

**Pendiente de decidir:** esquema de un solo token vs. access token (corta duración) + refresh token (larga duración). Recomendado si se sabe de antemano que habrá cliente móvil/desktop, para no rediseñar el middleware después.

---

## 4. Checklist operativo — piezas que faltan para un login production-ready

**Bloqueantes antes de exponer a usuarios reales:**

- [ ] Generación del token de sesión con `crypto.getRandomValues()` (nunca `Math.random()`).
- [ ] Rate limiting en endpoints de login/registro (Cloudflare Rate Limiting Rules o contador propio en KV).
- [ ] Mensaje de error genérico en login ("credenciales inválidas") para evitar enumeración de usuarios — no diferenciar "email no existe" de "password incorrecta".
- [ ] Endpoint de logout que borra la key correspondiente en KV.
- [ ] Definir si cambiar el password invalida todas las sesiones activas del usuario.
- [ ] Validación de input: formato de email, longitud/complejidad mínima de password.
- [ ] Confirmar uso de prepared statements/bindings en D1 (no concatenación de strings) para evitar SQL injection.
- [ ] Turnstile en los formularios de login y registro (evita creación de cuentas automatizada / bots, gratis, se integra como widget + verificación server-side del token en el Worker).

**No bloqueantes, pero pendientes:**

- [ ] Esquema access token + refresh token (ver sección 3).
- [ ] Verificación de email al registrarse.
- [ ] Recuperación de password ("olvidé mi contraseña") — requiere proveedor SMTP externo, Cloudflare no tiene uno nativo (evaluar Resend/Mailgun).
- [ ] Configuración de CORS si el cliente móvil/desktop golpea el Worker desde otro origen.
- [ ] MFA a futuro — si se planea, afecta el esquema de `users` desde ahora.

---

## 5. Email transaccional (Resend) — deliverability y seguridad de OTP

**Deliverability (por qué cae en spam):**

- [ ] Verificar dominio propio en Resend (NO usar el dominio de pruebas por defecto).
- [ ] Configurar SPF en DNS del dominio (bajo 10 lookups).
- [ ] Configurar DKIM en DNS del dominio (clave RSA 2048+, rotación periódica).
- [ ] Configurar DMARC en modo `p=none` con reporting (RUA) inicialmente, subir a `p=quarantine` una vez confirmado que las fuentes legítimas pasan.
- [ ] Incluir versión texto plano junto al HTML en cada correo.
- [ ] Evitar patrones de contenido típicos de spam en asunto/cuerpo.

> **Nota:** desde nov-2025 Gmail rechaza (no solo filtra a spam) correo masivo sin autenticación correcta; Microsoft/Outlook exige lo mismo desde may-2025 para +5,000 correos/día. Sin SPF/DKIM/DMARC, los correos transaccionales (OTP, recuperación de password) pueden no llegar en absoluto, no solo caer en spam.

**Seguridad del OTP enviado por correo (bloqueante antes de usar en producción):**

- [ ] OTP de 6+ dígitos numéricos, o alfanumérico 6-8 caracteres.
- [ ] Expiración corta vía TTL nativo de KV (`expirationTtl`), 5-10 min.
- [ ] Límite de intentos de verificación por código (3-5 máx), luego invalidar.
- [ ] Rate limiting en el endpoint de verificación de OTP.
- [ ] Rate limiting en el endpoint que genera/reenvía el OTP.
- [ ] OTP guardado hasheado en KV (SHA-256 suficiente, no necesita PBKDF2 — la protección contra fuerza bruta la da el límite de intentos, no el hash).
- [ ] Invalidar OTP anterior al generar uno nuevo (evitar múltiples códigos válidos).
- [ ] Respuesta genérica sin revelar si el email existe o no.

---

## 6. Fundamentos de base de datos aplicados a este stack

**Transacciones / rollback (Atomicity de ACID):**

- D1 **NO** soporta `BEGIN TRANSACTION` / `ROLLBACK` clásico vía su API (limitación de diseño: SQLite solo permite una transacción de escritura abierta a la vez; permitir `BEGIN`/`ROLLBACK` expondría riesgo de bloquear toda la BD si un Worker falla sin hacer rollback).
- Alternativa: `db.batch([...])` — ejecuta varias sentencias preparadas de forma atómica (todas o ninguna), pero sin branching intermedio ni rollback personalizado.
- Si se usa un ORM (ej. Drizzle) con `.transaction()`, falla contra D1 — usar `batch()` en su lugar.
- Un solo `INSERT`/`UPDATE` ya es atómico por sí mismo, no necesita `batch()`. Usar `batch()` solo cuando una operación toque 2+ tablas que deban aplicarse juntas.

**Integridad referencial:**

- `FOREIGN KEY` en tablas futuras (ej. `sessions.user_id` → `users.id`) para evitar filas huérfanas.
- Evaluar `ON DELETE CASCADE` según el caso (ej. borrar usuario borra sus sesiones).

**Normalización:**

- Esquema actual de `users` cumple 3FN de forma natural (simple, sin redundancia).
- Revisar al agregar tablas relacionadas (evitar duplicar datos que deberían vivir en su propia tabla).

---

## 7. ORM vs Prepared Statements — aclaración de conceptos

**Corrección de concepto:** un ORM (Object-Relational Mapper) NO es como MVC, y NO es lo que previene SQL injection. Es una capa que traduce objetos/clases del código a filas de tabla relacional (ej. `db.users.findById(id)` en vez de SQL manual).

**Lo que sí previene SQL injection:** prepared statements / parameterized queries. Esto es independiente de usar o no un ORM — D1 los soporta nativamente:

```typescript
// VULNERABLE — concatenación de strings
await db.exec(`SELECT * FROM users WHERE email = '${email}'`);

// SEGURO — prepared statement nativo de D1, sin ORM
await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
```

**Para qué sirve un ORM entonces** (no es seguridad, es productividad):
- Menos SQL manual en queries complejas con joins.
- Tipado (autocompletado, errores en compilación con TypeScript).
- Gestión de migraciones.
- Portabilidad entre motores de BD.

**Decisión para este proyecto:** esquema actual simple (`users`, eventualmente `sessions`) → prepared statements nativos de D1 son suficientes, sin ORM, para no sumar una dependencia más al proyecto reutilizable. Reconsiderar Drizzle ORM si el esquema crece a muchas tablas con joins complejos (por legibilidad, no por seguridad — la seguridad ya está cubierta con `.bind()`).

> **Nota:** si en el futuro se usa Drizzle con D1, recordar que NO soporta `.transaction()` — usar `db.batch()` igual que con SQL crudo (ver sección 6).

---

## 8. Pasarela de pagos — PagueloFacil (torneos, cursos, suscripciones)

**Contexto de negocio:** Stripe no permite abrir cuenta directamente desde Panamá sin una LLC en EE.UU. — por eso se usa PagueloFacil, que sí opera de forma directa en Panamá.

**Flujo confirmado** (documentación oficial, "Enlace de Pago" / offsite checkout):

1. Backend hace `POST` a `LinkDeamon.cfm` con `CCLW` (código de comercio), `CMTN` (monto), `CDSC` (descripción), y opcionalmente `RETURN_URL` (hex), `PF_CF` (campos custom en JSON hex), `PARM_1` (parámetro custom), `EXPIRES_IN`.
2. Respuesta trae una URL de un solo uso — redirigir al usuario ahí. Debe generarse un enlace NUEVO por cada transacción (no reutilizable).
3. Usuario paga en el sitio de PagueloFacil, puede volver vía `RETURN_URL`.

**PUNTO CRÍTICO DE SEGURIDAD — bloqueante antes de implementar:**

- Los parámetros del `RETURN_URL` (redirect al navegador del usuario) **NO son prueba confiable de pago** — pasan por el cliente, pueden manipularse. Solo el webhook es fuente de verdad.
- El webhook NO se autoconfigura desde dashboard — hay que pedirlo a `customerservice@paguelofacil.com`.
- No se encontró documentación de firma HMAC / secreto compartido para verificar autenticidad del webhook (a diferencia de Stripe). **Pendiente:** preguntar directamente a soporte de PagueloFacil si existe firma, header de auth, o whitelist de IPs.
- **Mitigación mientras no se confirme lo anterior:** al recibir el webhook, NO confiar ciegamente en el payload — usar `codOper` (código de operación único) para hacer una consulta server-to-server contra la API de PagueloFacil y confirmar el estado real de la transacción antes de otorgar acceso.

**Validación de pago real (según documentación):**

- `status` debe ser `1` (Aprobada).
- `operationType` debe ser `CAPTURE`, `AUTH_CAPTURE`, o `RECURRENT` — únicos tipos que representan ingreso real de fondos. `AUTH`, `3DS`, `REVERSE`, `REVERSE_CAPTURE` NO son pagos acreditados.
- `codOper` = identificador único de la transacción → usar para idempotencia (evitar procesar el mismo pago dos veces si el webhook llega duplicado).

**Diseño pendiente:**

- [ ] Mapeo de producto → contenido: torneo (acceso puntual con fecha límite), curso (acceso permanente), suscripción (acceso mientras esté activa) — cada uno con lógica distinta de qué desbloquea el pago.
- [ ] Usar `PF_CF` o `PARM_1` para llevar el ID de producto/usuario a través del flujo de pago y poder mapearlo de vuelta en el webhook.
- [ ] Tabla de pagos/órdenes en D1 con estado (pendiente/confirmado) y `codOper` como referencia única (constraint `UNIQUE` para idempotencia).
- [ ] Confirmar con soporte PagueloFacil mecanismo de autenticación del webhook.

---

## 9. Cache y Cookies — referencia

**Cookies — dos usos distintos, no confundir:**

- **Cookie de sesión** (`httpOnly` + `Secure` + `SameSite`): estrictamente necesaria para que la app funcione, NO requiere banner de consentimiento.
- **Cookies de terceros** (analytics, marketing, píxeles): SÍ requieren consentimiento explícito (opt-in) bajo GDPR si hay visitantes de la UE — relevante porque se aceptan tarjetas internacionales. Mientras no se agreguen estas, no hace falta banner de cookies en absoluto.

Nunca guardar el token de sesión en `localStorage`/`sessionStorage` — accesible desde JS, vulnerable a XSS. Usar cookie `httpOnly` (web) o el almacenamiento seguro nativo por plataforma (ver sección 3).

**Cache de Cloudflare — tres mecanismos distintos, no intercambiables:**

1. **Cache de zona (CDN clásico):** assets estáticos cacheados automáticamente, sin configuración.
2. **Workers Cache:** Cloudflare devuelve respuestas HTTP cacheadas sin ejecutar el Worker — reduce latencia y CPU. Soporta header `Vary` (ej. `Vary: Accept-Language` para variantes por idioma).
3. **Cache API (programática):** control fino desde dentro del Worker, `cache.put()`/`cache.match()`, por datacenter de origen (no global automático).

**Patrón recomendado para contenido semi-dinámico** (ej. listado de torneos, catálogo de cursos): stale-while-revalidate. Ejemplo: `max-age=300, stale-while-revalidate=3600` — sirve versión cacheada mientras se refresca en background, sin que el usuario espere.

**Regla no negociable:** cualquier endpoint que dependa de sesión (login, rutas protegidas por auth middleware) debe llevar `Cache-Control: no-store` explícito — de lo contrario Cloudflare podría cachear una respuesta de un usuario y servírsela a otro.

---

## 10. Qué debe validarse en el backend (nunca confiar en el cliente)

**Principio base:** validación en frontend es UX, validación en backend es seguridad. Cualquier request puede saltarse el frontend (curl, Postman) — si algo importa para integridad de datos o negocio, se valida en backend sin excepción, aunque ya esté validado en frontend.

**Capas de validación:**

1. **Formato/tipo** — tipo de dato correcto, formato (email, longitud password), campos requeridos presentes. *(Ya implementado en `auth.validators.ts`.)*
2. **Reglas de negocio** — específico al dominio: ¿email ya existe? ¿hay cupos disponibles? ¿el usuario tiene permiso? ¿el monto coincide con el precio real?
3. **Autenticación** — ¿quién eres? Token de sesión válido, no expirado, correspondiente a un usuario que existe. *(Pendiente: `auth.middleware.ts`.)*
4. **Autorización** — ¿tienes permiso para ESTA acción específica? Distinto de autenticación. Ej: `/tournaments/:id/cancel` no basta con "está logueado" — hay que validar que sea el dueño/organizador de ESE torneo o un admin. *(Pendiente, no diseñado todavía.)*
5. **Integridad entre pasos de un flujo** — ej. webhook de pago: no solo validar `status`/`operationType`, también que el `reservationId`/`codOper` corresponda a una orden generada por el propio sistema, no uno inventado.
6. **Límites y abuso** — rate limiting (ya en checklist), tamaño máximo de payload, sanitización de input mostrado de vuelta en HTML (XSS) si en algún momento se muestra contenido generado por usuario.

**Los dos puntos más comúnmente ignorados — bloqueantes antes de producción:**

- [ ] El precio/monto de un pago SIEMPRE se calcula/busca en el backend a partir del ID de producto (`tournamentId`/`courseId`) — NUNCA se confía en un monto que venga del cliente en el request. El `CMTN` que se manda a PagueloFacil se calcula server-side.
- [ ] Diseñar capa de autorización (no solo autenticación) para cualquier endpoint que modifique/cancele/administre un recurso específico (no solo "¿está logueado?", sino "¿es el dueño de este recurso o admin?").
- [ ] `auth.middleware.ts` — validar token de sesión contra KV en rutas protegidas (diseñado conceptualmente, código pendiente).
- [ ] Límite de tamaño de payload en endpoints que reciben JSON del cliente.

---

## 11. Categorías que faltan pensar (no son features, son forma de pensar)

**"¿Qué pasa cuando esto falla?"** — no se ha aplicado a nada de lo construido:

- [ ] Si D1 está caído/lento, ¿el Worker responde con error claro o se cuelga?
- [ ] Si KV falla al leer sesión, ¿se trata como "no autenticado" o error 500? Decidirlo explícitamente, no dejar que pase por accidente.
- [ ] Si PagueloFacil está caído durante un intento de pago, ¿qué le llega al usuario y qué pasa con la reserva pendiente en el Durable Object?

**Testing** — no hay ni un test escrito todavía:

- [ ] Unitarios de `hash.ts` (`verifyPassword` rechaza incorrecto, mismo password + distinto salt = hash distinto).
- [ ] Test de concurrencia real en `TournamentCapacity` DO — simular múltiples `reserveSlot()` simultáneos y confirmar que el límite se respeta bajo carga, no solo en llamada única.

**Observabilidad** — más allá de "tener logs":

- [ ] Logs estructurados con ID de correlación (ej. `codOper`) para poder rastrear un pago específico end-to-end cuando un usuario reclame.

**Costos:**

- [ ] Revisar pricing de Durable Objects / KV writes / D1 pasado el free tier ANTES de que la factura sorprenda — especialmente con el patrón "un DO por torneo" si el volumen de torneos simultáneos crece.

**Backups y recuperación:**

- [ ] Confirmar (no asumir) si D1 tiene point-in-time recovery disponible en el plan usado, antes de necesitarlo en un incidente real.

**Versionado de API:**

- [ ] Evaluar prefijo `/v1/` desde el inicio — cambiar esquema de respuesta después de tener clientes (APK) en producción es más caro que empezar versionado.

**No es código, pero importa igual:**

- Documentar decisiones DENTRO del código (por qué X sobre Y), no solo en este `.md` aparte.
- Saber cuándo NO construir algo (ya aplicado varias veces: Argon2id, Docker, LLC) es tan parte de ingeniería como saber construir.

---

## Notas

- Arquitectura de datos (D1/KV/Workers) y algoritmo de hashing: decisiones cerradas.
- Punto 1 (D1 vs KV para sesiones) puede esperar hasta tener tráfico real o evidencia de degradación de performance.
- Antes de abrir registro público: resolver todos los ítems bloqueantes de la sección 4.
- Antes de activar verificación de email/OTP: resolver todos los ítems de la sección 5.
- Antes de implementar pagos: resolver los puntos críticos de la sección 8.
- Antes de exponer cualquier endpoint que modifique datos: resolver los puntos críticos de la sección 10 (precio server-side, autorización).
- Antes de considerar esto "producción real": revisar la sección 11 completa.
