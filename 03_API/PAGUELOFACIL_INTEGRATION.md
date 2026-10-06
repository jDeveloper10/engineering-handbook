---
title: "Integración con PagueloFácil (Enlace de Pago) — Referencia de Campos Reales y Gotchas"
category: 03_API
doc_type: referencia
tags: [api, webhooks, pagos, paguelofacil, panama, centroamerica, pasarela, enlace-de-pago]
summary: "Referencia empírica de la integración de PagueloFácil (Enlace de Pago): forma real del payload del webhook, por qué customFields no llega con las claves que enviaste, por qué no existe endpoint de re-verificación, y el modelo de seguridad que sí funciona sin firma de webhook ni API de consulta."
keywords: [paguelofacil, linkdeamon, enlace-de-pago, webhook, codOper, idtx, operationType, customFields, PF_CF, panama]
updated: 2026-09-23
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "https://developers.paguelofacil.com/guias/enlace-de-pago (documentación oficial, consultada 2026-09-23)"
  - "Payload real de producción capturado en incidente real (Monica Academy, 2026-09-22/23) — ver logs de ese proyecto"
  - "Chat de soporte de PagueloFácil (customerservice@paguelofacil.com) confirmando ausencia de secreto de webhook autoconfigurable"
---

# Integración con PagueloFácil (Enlace de Pago)

PagueloFácil es una pasarela de pago panameña. Este documento existe porque su comportamiento real
diverge en varios puntos clave de lo que su propia documentación (y el sentido común basado en
Stripe/Wompi) sugiere, y esa divergencia causó un incidente real en producción: **una transacción
real, cobrada y aprobada, nunca matriculó a la alumna** porque el código asumía nombres de campo y
un modelo de seguridad que PagueloFácil simplemente no tiene. Todo lo de aquí está verificado contra
un payload real, no contra la documentación sola — la documentación por sí sola no hubiera bastado
para detectar el problema de `customFields`.

Si vas a integrar PagueloFácil "Enlace de Pago" (`LinkDeamon.cfm`) en un proyecto nuevo, lee esto
completo antes de escribir el webhook handler.

---

## 0. Lo que PagueloFácil NO ofrece (y que sí asumen Stripe/Wompi)

**[REQUIRED]** No diseñes la integración asumiendo que estas capacidades existen — no existen:

| Capacidad que Stripe/Wompi sí dan | PagueloFácil |
|---|---|
| Secreto de firma de webhook autoconfigurable desde el panel | ❌ No existe. Soporte confirmó por chat que el webhook se activa manualmente con solo la URL, sin ningún secreto propio que el comercio pueda generar. |
| Endpoint REST para re-consultar el estado de una transacción después del hecho | ❌ No existe ninguno documentado. `developers.paguelofacil.com/guias/enlace-de-pago` dice explícitamente que hay que escribirle a soporte para "posibles capacidades de consulta". Cualquier endpoint `/rest/tx/:id` que veas mencionado en foros o repos no oficiales **no está confirmado** — probado empíricamente contra `secure.paguelofacil.com` y `api.pfserver.net` con un `idtx` real de una transacción real aprobada: 404 en ambos. |
| `customFields` del webhook indexado por el `id` que tú definiste | ❌ Se indexa por `nameOrLabel`, no por `id` (ver sección 2). |
| Un identificador de transacción único que el navegador reciba de vuelta en el redirect | ❌ El `returnUrl` solo trae de vuelta `PARM_1`/`PARM_2` (lo que tú hayas puesto ahí) — nunca `codOper` ni `idtx` automáticamente. |

**Consecuencia de diseño:** sin secreto de webhook ni endpoint de consulta, tu única defensa real
contra un webhook forjado es (a) revalidar monto/moneda/curso contra tu catálogo real en el
servidor, nunca confiar en el monto del payload a ciegas, y (b) la regla de `operationType`
(sección 3). Documenta esto explícitamente en tu propio código — de lo contrario, un desarrollador
futuro (o una IA) intentará "arreglarlo" agregando una verificación server-to-server que fabrica un
endpoint inexistente, como pasó aquí.

---

## 1. Flujo completo

```
1. Tu backend arma un POST a LinkDeamon.cfm con: CCLW, CMTN, CDSC, RETURN_URL (hex),
   PF_CF (hex del JSON de customFields), PARM_1, PARM_2, EXPIRES_IN.
2. PagueloFácil responde con { data: { url, code } } -- `code` es el código del LINK
   (formato "LK-XXXXXXXX"), no de una transacción todavía.
3. Rediriges a la alumna a `data.url`.
4. La alumna paga en la interfaz de PagueloFácil.
5. PagueloFácil hace POST a tu webhook configurado (ver sección 2 para la forma real).
6. PagueloFácil redirige el navegador de la alumna a
   `RETURN_URL?PARM_1=<lo que pusiste>&PARM_2=<lo que pusiste>` -- SIN ningún ID de
   transacción propio. Diseña PARM_1/PARM_2 asumiendo que es lo ÚNICO que tu pantalla de
   retorno podrá usar para encontrar la orden.
```

**Bases URL confirmadas para `LinkDeamon.cfm`:**
- Producción: `https://secure.paguelofacil.com/LinkDeamon.cfm`
- Sandbox: `https://sandbox.paguelofacil.com/LinkDeamon.cfm`

---

## 2. Forma REAL del payload del webhook (verificado con una transacción real)

```json
{
  "date": "2026-09-22T23:37:04",
  "codOper": "LK-U7WRXNQHBN41",
  "idtx": 13953231,
  "status": 1,
  "operationType": "AUTH_CAPTURE",
  "totalPay": "0.35",
  "requestPayAmount": 0.35,
  "authStatus": "00",
  "cardType": "MC",
  "email": "alumna@ejemplo.com",
  "name": "nombre completo en minúsculas",
  "messageSys": "Transaction is approved",
  "relatedTx": "LK-XWHKSU8RBOHF",
  "customFields": {
    "Cursos": "unas-acrilicas-profesional",
    "Email Alumna": "alumna@ejemplo.com",
    "Nombre Alumna": "Nombre Completo",
    "ID de Orden": "ecc8aeec-f5c0-4110-8dc1-2197169d5f46"
  }
}
```

### 2.1 `codOper` NO es el ID de la transacción

`codOper` es el código del **link de pago** (el mismo que `LinkDeamon.cfm` devolvió como `data.code`
al crearlo). Es estable para ese link, no identifica de forma única "este cobro específico" en un
sentido transaccional. `idtx` es el ID numérico interno de la transacción — pero como no hay
endpoint de consulta, tampoco sirve para re-verificar nada; solo es útil como dato de auditoría.

### 2.2 `customFields` se indexa por `nameOrLabel`, NO por `id` — el gotcha que causó el incidente

Cuando armas `PF_CF` para `LinkDeamon.cfm`, cada campo lleva `{ id, nameOrLabel, type, value }`:

```json
[{ "id": "courseSlugs", "nameOrLabel": "Cursos", "type": "hidden", "value": "curso-x,curso-y" }]
```

**Es intuitivo asumir que el webhook te devuelve `customFields.courseSlugs`. Es falso.**
PagueloFácil reconstruye el objeto usando **`nameOrLabel` como clave**, no `id`:

```json
"customFields": { "Cursos": "curso-x,curso-y" }
```

Si tu parser busca `customFields.courseSlugs`, siempre da `undefined` — silenciosamente, sin
ningún error — y si tu lógica de negocio depende de ese campo (ej. "a qué le doy acceso"), el
webhook completo falla sin dejar ningún rastro si no logueas el payload crudo antes de fallar.

**[REQUIRED]** Al mapear `customFields`, usa el `nameOrLabel` exacto que enviaste como clave de
lectura. Si necesitas robustez ante que el formato cambie, soporta ambas claves (`nameOrLabel` y
`id`) con `||`, pero el `nameOrLabel` es el que realmente llega.

### 2.3 Un array en `PF_CF` viaja como string separado por comas, no como array

Si tu `value` es una lista (ej. varios cursos en un mismo checkout), en `PF_CF` solo puedes mandar
un string (`selectedSlugs.join(',')`). El webhook te lo devuelve como ese mismo string, no como
array — tienes que hacer `.split(',').map(s => s.trim())` vos mismo.

### 2.4 Nombres de campo con mayúsculas/minúsculas inconsistentes

El payload real usa `totalPay` y `requestPayAmount` (minúscula inicial) para el monto — **no**
`TotalPay` (mayúscula), que es lo que uno esperaría por convención .NET/ColdFusion (el backend de
PagueloFácil corre sobre ColdFusion, de ahí `LinkDeamon.cfm`). Si tu chequeo de monto es
case-sensitive y solo cubre `TotalPay`, nunca va a encontrar el monto real y tu validación
anti-fraude de "monto pagado == monto esperado" queda simplemente sin ejecutarse (falla abierta o
cerrada según cómo esté escrito el `if`).

**[REQUIRED]** Al extraer el monto, cubre explícitamente: `totalPay`, `requestPayAmount`, `amount`,
`TotalPay`, `total` (todas las variantes vistas en la práctica o mencionadas en foros).

---

## 3. La regla real de acreditación: `status` no basta, hace falta `operationType`

Documentación oficial: **solo se considera un pago acreditado si `status === 1` Y
`operationType` está en `{CAPTURE, AUTH_CAPTURE, RECURRENT}`**. Un `AUTH` sin captura, un
`REVERSE`/`REVERSE_CAPTURE`, o un `3DS` de solo verificación pueden traer `status: 1` sin
representar dinero realmente acreditado.

```typescript
const operationType = String(rawBody.operationType || '').toUpperCase();
const isAccredited = rawBody.status === 1 &&
  ['CAPTURE', 'AUTH_CAPTURE', 'RECURRENT'].includes(operationType);
```

Validar solo `status === 1` es **necesario pero no suficiente**.

---

## 4. Cómo correlacionar el retorno del navegador con la transacción real

El `RETURN_URL` que configuras solo recibe de vuelta `PARM_1` y `PARM_2` — lo que tú hayas puesto
ahí al crear el link, nunca un ID generado por PagueloFácil. Diseño recomendado:

1. Genera tu **propio** `orderId` (UUID) en el servidor al crear el link de cobro.
2. Mándalo en `PARM_2` (o dentro de `PF_CF` con `nameOrLabel: "ID de Orden"` para que también
   viaje en el webhook).
3. Al guardar el registro de la venta/matrícula tras el webhook, usa **ese `orderId`** como
   referencia primaria — no `codOper` ni `idtx`.
4. Tu pantalla de retorno (`/pago-exitoso` o equivalente) lee `PARM_2` de la URL y consulta tu
   propio backend por ese `orderId` — nunca por `codOper`/`idTx`/`session_id`, que el navegador
   jamás va a traer de un flujo real de PagueloFácil.

Sin este diseño, tu pantalla de "pago confirmado" funciona en desarrollo (donde uno prueba pasando
el parámetro "correcto" a mano) pero **nunca funciona con un pago real**, porque el parámetro que
el navegador realmente recibe no es el que el código busca.

---

## 5. Idempotencia: marca "procesado" solo DESPUÉS de completar la acción de negocio

**[REQUIRED]** No escribas la clave de idempotencia (KV/DB) antes de validar el payload
completo. Si marcas "procesado" y LUEGO una validación posterior falla (ej. un bug de parseo como
el de la sección 2.2), esa transacción real, ya cobrada, queda **permanentemente bloqueada** —
ningún reintento futuro del webhook (ni siquiera después de arreglar el bug) puede volver a
procesarla, porque tu propio sistema cree que ya la procesó.

```typescript
// ❌ Mal: marca "procesado" antes de saber si el resto del flujo va a funcionar
await kv.put(dedupeKey, 'PROCESSED', { expirationTtl: WEEK });
if (!customerEmail || !courseSlugs.length) return errorResponse(...); // ya quedó envenenada

// ✅ Bien: valida todo, ejecuta la acción de negocio, y SOLO ENTONCES marca procesado
if (!customerEmail || !courseSlugs.length) return errorResponse(...);
await enrollStudent(...);
await kv.put(dedupeKey, 'PROCESSED', { expirationTtl: WEEK });
```

El `get` de chequeo ("¿ya se procesó?") sí debe ir al principio, antes de hacer trabajo duplicado —
solo el `put` de "ya quedó procesado" se mueve al final.

---

## 6. Checklist para una integración nueva de PagueloFácil

- [ ] Loguea el body crudo completo del webhook (al menos temporalmente) antes de parsear nada —
      es la única forma de descubrir divergencias de formato como la de `customFields` sin
      quemar transacciones reales para averiguarlo.
- [ ] `customFields` se lee por `nameOrLabel`, no por `id`.
- [ ] Campos de lista van como string separado por comas en `PF_CF`, hay que hacer `.split(',')`.
- [ ] Monto: cubrir `totalPay`/`requestPayAmount` además de las variantes con mayúscula.
- [ ] Acreditación real = `status === 1` **Y** `operationType` en `{CAPTURE, AUTH_CAPTURE, RECURRENT}`.
- [ ] No fabricar un endpoint de re-verificación server-to-server sin confirmarlo primero con
      soporte (`customerservice@paguelofacil.com`) — probablemente no existe.
- [ ] La referencia de tu venta/matrícula usa un `orderId` propio (enviado en `PARM_2` y/o
      `PF_CF`), no `codOper` ni `idtx` — es lo único que el navegador recibe de vuelta.
- [ ] La marca de idempotencia se escribe solo después de completar la acción de negocio, no antes
      de validar el payload.
- [ ] Revalidar monto/moneda/curso contra el catálogo real del servidor en cada webhook —
      es la defensa principal contra un payload forjado, dado que no hay firma ni endpoint de
      consulta.

Ver también: [WEBHOOK_IDEMPOTENCY_STANDARD.md](WEBHOOK_IDEMPOTENCY_STANDARD.md) para el patrón
general (Stripe/Wompi/NowPayments) del que este documento es un caso especial con menos garantías
del lado del proveedor.
