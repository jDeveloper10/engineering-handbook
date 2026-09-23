---
title: "Runbook — YouTube Live no listado con Cloudflare Workers"
category: 08_Cloud
doc_type: runbook
tags: [youtube, live-streaming, oauth, cloudflare-workers, pages, prism-live, kv]
summary: "Procedimiento reproducible para conectar un canal de YouTube, crear directos no listados desde un panel de administración y restringir su visualización a usuarios matriculados."
keywords: [youtube-data-api, oauth-2, liveBroadcasts, liveStreams, prism-live, cloudflare, pages, workers, kv, directo-no-listado]
updated: 2026-09-23
status: VERIFIED
confidence: 95%
reviewed: false
sources:
  - "Google for Developers — YouTube Data API: Broadcasts and Streams"
  - "Google for Developers — OAuth 2.0 for Web Server Applications"
  - "YouTube Help — Create a live stream with an encoder"
  - "Cloudflare Workers Docs — Secrets"
---

# Runbook — YouTube Live no listado con Cloudflare Workers

> Implementación de referencia: Monica Academy, React/Vite en Cloudflare Pages y Hono en Cloudflare Workers. El patrón es reutilizable para plataformas de cursos que necesitan emitir desde PRISM Live Studio u otro codificador, sin exponer una URL pública en el catálogo.

## 1. Resultado y alcance

Este flujo reemplaza soluciones WebRTC gratuitas no operables a gran escala por la infraestructura de YouTube:

```text
Dirección / panel admin
  └─ crea un directo no listado desde el Campus
       ├─ Worker crea liveStream + liveBroadcast y los vincula
       ├─ Worker guarda el ID de YouTube y el curso asociado en KV
       └─ Campus muestra el embed exclusivamente a alumnas matriculadas

PRISM Live Studio (teléfono de la instructora)
  └─ transmite al mismo canal de YouTube
       └─ YouTube entrega el video a las alumnas autorizadas
```

La plataforma no retransmite ni almacena el video. YouTube gestiona ingestión, transcodificación y ancho de banda; el Worker únicamente orquesta OAuth, la creación del directo y el control de acceso del Campus.

### Decisiones de producto aplicadas

- Cada directo se crea con privacidad `unlisted`.
- La URL cambia por cada nuevo directo; el Campus la actualiza automáticamente, sin copiar y pegar enlaces.
- La sala queda disponible para las alumnas autorizadas al crear el directo. Antes de que PRISM emita, YouTube puede mostrar la espera del evento.
- El acceso a la cámara/ID no se devuelve a visitantes sin matrícula en el curso vinculado.
- VDO.Ninja se conserva como alternativa de legado, pero no es la solución recomendada de producción por su dependencia de WebSocket/WebRTC y red P2P.

## 2. Requisitos externos que no se pueden automatizar

Antes de probar el flujo, la dueña del canal debe completar estos requisitos en YouTube:

1. Verificar el número de teléfono del canal para habilitar live streaming.
2. Esperar la activación de YouTube si el canal fue habilitado recientemente; Google puede tardar hasta 24 horas.
3. Iniciar sesión en PRISM Live Studio con la misma cuenta propietaria del canal.
4. Mantener una conexión móvil o Wi-Fi estable al transmitir.

OAuth y la API **no evitan** la verificación de YouTube. Si falla, la API suele devolver un error indicando que el canal no está habilitado para transmisiones en vivo.

## 3. Configuración de Google Cloud

### 3.1 Crear el proyecto y habilitar la API

En [Google Cloud Console](https://console.cloud.google.com/):

1. Crear un proyecto específico para la academia, separado de proyectos personales o de otros clientes.
2. Abrir **APIs & Services** y habilitar **YouTube Data API v3**.
3. Configurar la marca de OAuth con el nombre público de la academia y correo de soporte de la dueña.
4. Elegir audiencia **External**. Mientras la app esté en `Testing`, añadir explícitamente la cuenta de la instructora en **Test users**.

La configuración de Monica Academy se creó como proyecto `monica-academy-live`, con la cuenta propietaria agregada como usuaria de prueba. No guardar correos, IDs de proyecto ni credenciales personales en documentación pública reutilizable.

### 3.2 Crear el cliente OAuth

Crear un cliente de tipo **Web application** y configurar este redirect URI exacto:

```text
https://monicarioscursos.online/youtube/callback
```

El redirect URI debe coincidir byte a byte en Google Cloud y en el backend. No usar el dominio `workers.dev`: el callback debe cargar la aplicación Pages que conserva la sesión del panel administrativo.

El alcance solicitado por el flujo es:

```text
https://www.googleapis.com/auth/youtube
```

Este alcance permite crear streams, broadcasts y enlaces no listados. Debe pedirlo únicamente una pantalla de Dirección autenticada; nunca desde una vista pública o de alumna.

## 4. Secretos del Worker

Los secretos se cargan en el Worker, no en `wrangler.toml`, `.env` del frontend ni variables `VITE_*`.

| Secreto | Uso | Exposición permitida |
|---|---|---|
| `YOUTUBE_OAUTH_CLIENT_ID` | Identifica el cliente OAuth ante Google | Solo Worker por consistencia operativa |
| `YOUTUBE_OAUTH_CLIENT_SECRET` | Intercambia el código OAuth y renueva el token | Solo Worker |
| `YOUTUBE_OAUTH_STATE_SECRET` | Marca la configuración OAuth del entorno | Solo Worker |

Desde `backend/`, cargar valores sin imprimirlos ni pegarlos en la terminal compartida:

```bash
pnpm exec wrangler secret put YOUTUBE_OAUTH_CLIENT_ID
pnpm exec wrangler secret put YOUTUBE_OAUTH_CLIENT_SECRET
pnpm exec wrangler secret put YOUTUBE_OAUTH_STATE_SECRET
pnpm exec wrangler secret list
```

`wrangler secret list` permite comprobar que existen los nombres, pero nunca devuelve sus valores. Si se crea un segundo secreto del cliente OAuth en Google, mantener ambos solo durante la transición y deshabilitar/borrar el anterior después de validar que el nuevo funciona.

## 5. Archivos y rutas implementadas

Repositorio de referencia: `/home/JDeveloper/Escritorio/tranbajo/Trabajo/01_Clientes/MONICA ACADEMY`.

| Archivo | Responsabilidad |
|---|---|
| `backend/src/types.ts` | Declara los bindings secretos de YouTube para el Worker. |
| `backend/src/handlers/live.ts` | OAuth, persistencia en KV, creación de stream/broadcast, vinculación y control de acceso. |
| `backend/src/index.ts` | Registra rutas administrativas con `requireAuth('instructor', 'admin')`. |
| `frontend/src/components/admin/live/AdminLivePanel.tsx` | Botones “Conectar canal de YouTube” y “Crear y abrir directo”. |
| `frontend/src/components/auth/YouTubeOAuthCallback.tsx` | Recibe `code` y `state` en Pages y los envía autenticadamente al Worker. |
| `frontend/src/main.tsx` | Enruta `/youtube/callback` al callback OAuth sin renderizar la landing. |

### Rutas privadas

| Método y ruta | Propósito |
|---|---|
| `GET /api/admin/live/youtube/connection` | Devuelve si el entorno tiene secretos y si ya existe un canal conectado; nunca devuelve tokens. |
| `POST /api/admin/live/youtube/authorize` | Crea un `state` de un solo uso en KV y devuelve la URL de consentimiento de Google. |
| `POST /api/admin/live/youtube/exchange` | Valida `state`, intercambia el código OAuth y guarda el refresh token en KV. |
| `POST /api/admin/live/youtube/broadcast` | Crea/recupera el stream RTMP, crea un broadcast no listado, lo vincula y actualiza la clase activa. |

Todas requieren rol `instructor` o `admin`. Los tokens se guardan bajo claves internas de KV y nunca forman parte de la respuesta HTTP, los logs ni el bundle de Vite.

## 6. Flujo OAuth y persistencia

```text
1. Dirección pulsa “Conectar canal de YouTube”.
2. Worker guarda state aleatorio + userId en KV con TTL de 10 minutos.
3. Navegador abre accounts.google.com con response_type=code.
4. Google redirige a /youtube/callback de Pages.
5. Callback envía code + state al Worker con el Bearer de la sesión actual.
6. Worker valida que el state existe y pertenece al mismo userId; después lo borra.
7. Worker intercambia el code y persiste refresh_token en KV.
8. Para futuras operaciones, Worker renueva access_token con refresh_token.
```

La asociación `state → userId` evita que un código OAuth iniciado por otra sesión pueda ser reclamado por una cuenta administrativa distinta. El TTL evita que estados abandonados permanezcan indefinidamente en KV.

## 7. Creación de un directo y control de acceso

Al pulsar **Crear y abrir directo**, Dirección selecciona un curso y escribe el título. El Worker:

1. Comprueba que el curso existe.
2. Renueva el token OAuth si es necesario.
3. Busca un `liveStream` existente en el canal; crea uno RTMP si no existe.
4. Crea un `liveBroadcast` con `privacyStatus: unlisted`.
5. Vincula broadcast y stream mediante `liveBroadcasts.bind`.
6. Guarda el ID de video y el curso en la configuración activa de KV.
7. Crea una entrada de agenda para la clase.

El endpoint público autenticado `/api/live/status` aplica esta regla:

```text
Personal de Dirección → puede leer la configuración.
Alumna no matriculada → no recibe cámara ni ID de YouTube.
Alumna matriculada + directo activo → recibe el ID para el embed.
```

La verificación de matrícula ocurre en el Worker, no solo por ocultar un botón en React.

## 8. Operación diaria para la instructora

1. Entrar al Campus con rol Dirección.
2. Abrir **Clases en Vivo & Agenda**.
3. La primera vez, pulsar **Conectar canal de YouTube** y aceptar el consentimiento de Google con la cuenta propietaria del canal.
4. Seleccionar el curso, revisar el título y pulsar **Crear y abrir directo**.
5. En el teléfono, abrir PRISM Live Studio, elegir YouTube y la misma cuenta de Mónica; empezar a transmitir.
6. Las alumnas matriculadas entran en **Clases en Vivo** dentro del Campus. No se les envía una URL manual.
7. Al terminar, cerrar la transmisión desde Dirección y finalizar la emisión en PRISM/YouTube.

Si se desea conservar la grabación, YouTube la procesa en el mismo evento. El registro de la clase puede actualizarse posteriormente con el enlace de grabación conforme a la política académica.

## 9. Publicación y verificación

El despliegue aplicado fue:

```bash
# Desde el monorepo
pnpm --filter @monica-academy/backend test
pnpm --filter @monica-academy/frontend build
pnpm --filter @monica-academy/backend build

# Backend
cd backend
pnpm exec wrangler deploy

# Frontend Pages
pnpm exec wrangler pages deploy ../frontend/dist --project-name monica-academy --branch main
```

Estado de referencia al 2026-09-23:

- Worker: `https://monica-academy-backend.monicarioscursos.workers.dev`
- Sitio: `https://monicarioscursos.online`
- Commit de implementación: `1db9008` (`feat: automate unlisted YouTube Live classes`)
- Verificación realizada: typecheck frontend/backend, build frontend/backend y 99 pruebas backend aprobadas.

Tras un deploy, verificar al menos:

```bash
curl -fsS https://monica-academy-backend.monicarioscursos.workers.dev/api/health
curl -sSI https://monicarioscursos.online/youtube/callback
```

La ruta de conexión debe responder `401` sin Bearer token. Eso es correcto: confirma que no es una API administrativa pública.

## 10. Diagnóstico rápido

| Síntoma | Diagnóstico y acción |
|---|---|
| “YouTube Live no está configurado” | Ejecutar `wrangler secret list`; verificar los tres nombres `YOUTUBE_OAUTH_*` en el Worker de producción. |
| Google muestra `redirect_uri_mismatch` | Comparar el redirect URI registrado con `https://monicarioscursos.online/youtube/callback`; no debe haber slash adicional ni dominio distinto. |
| Google no deja conceder acceso | Confirmar que la cuenta está en **Test users** mientras la app OAuth siga en Testing. |
| Error al crear el directo | Verificar que el canal tiene live streaming habilitado y que pasaron las horas de activación de YouTube. Consultar `wrangler tail monica-academy-backend` mientras se reproduce. |
| Alumna ve una sala vacía | Confirmar que PRISM está transmitiendo al mismo canal y que el directo se creó para el curso en el que esa alumna está matriculada. |
| Alumna no ve la cámara | Confirmar matrícula y que el directo sigue activo. No resolver exponiendo la URL de YouTube en el frontend. |
| Se rotó el secreto OAuth | Subir el secreto nuevo al Worker, probar conexión, después deshabilitar y borrar el secreto anterior en Google Cloud. |

## 11. Límites y mantenimiento

- La app OAuth está en modo Testing: admite hasta 100 usuarios de prueba. Para incorporar múltiples instructores sin gestión manual, completar publicación/verificación de OAuth según las políticas vigentes de Google.
- Un directo no listado reduce descubrimiento público, pero no es DRM: una alumna que obtenga la URL podría compartirla. La protección principal del Campus es la autorización previa al embed.
- Los refresh tokens en KV son credenciales sensibles. Si se sospecha de una exposición, revocar el acceso de la aplicación en la cuenta de Google, borrar la clave de tokens de KV, rotar el secreto OAuth y reconectar el canal.
- Antes de cambiar scopes, privacidad, URLs de callback o lógica de acceso, crear un deployment preview y probar con una cuenta de prueba diferente a la propietaria.

