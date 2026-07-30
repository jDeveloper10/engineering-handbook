---
title: "Diagramas C4 y Modelado de Arquitectura"
category: 09_Architecture
doc_type: referencia
tags: [c4, diagramas, mermaid, arquitectura, cloudflare, edge, sequence]
summary: "Estándar completo de diagramación C4 y modelado visual para arquitectura Serverless/Edge: Diagramas de Contexto, Contenedores, Componentes, Flujos de Secuencia (Pagos y Tiempo Real) y Despliegue en Cloudflare."
keywords: [c4, mermaid, diagramas, arquitectura, secuencia, contenedores, edge, cloudflare, durable-objects]
updated: 2026-07-27
status: current
---

# MODELO C4 Y DIAGRAMACIÓN DE ARQUITECTURA

Este documento define la norma obligatoria para documentar la arquitectura visualmente usando el **modelo C4** y **Mermaid.js**. Los diagramas deben ser versionables en Git, legibles directamente en GitHub/Markdown y mantener coherencia con el stack **Cloudflare Workers + Supabase + React**.

---

## LAS 4 CAPAS DEL MODELO C4

```
Nivel 1: Contexto (System Context) ──→ Quién usa el sistema y qué sistemas externos se integran
Nivel 2: Contenedores (Container)   ──→ Apps desplegables, bases de datos y almacenamiento
Nivel 3: Componentes (Component)   ──→ Módulos internos de un Worker / servicio
Nivel 4: Código (Code)              ──→ UML / Flujos de clases (opcional para casos complejos)
```

---

## 1. DIAGRAMA C4 NIVEL 1: CONTEXTO DEL SISTEMA

Muestra el panorama general: cómo interactúan los usuarios (autenticados y anónimos) con la plataforma SaaS y con los servicios de terceros.

**[REQUIRED]** Todo nuevo sistema o producto debe incluir este diagrama en su documentación base.

```mermaid
C4Context
  title Diagrama de Contexto - SaaS Platform (Cloudflare Edge + Supabase)

  Person(usuario, "Usuario Registrado", "Accede a workspaces, documentos y colaboración vía Web/Mobile/Desktop")
  Person(cliente_anonimo, "Cliente Anónimo", "Accede a propuestas y documentos públicos mediante token único")
  
  System(saas, "SaaS Platform", "Core del sistema: API Gateway, Workers, React UI, Realtime y Storage")

  System_Ext(stripe, "Stripe API", "Procesamiento de pagos, facturas y suscripciones")
  System_Ext(resend, "Resend API", "Envío de correos transaccionales y resúmenes")
  System_Ext(expo_push, "Expo Push Service", "Notificaciones push para iOS (APNs) y Android (FCM)")
  System_Ext(github_oauth, "GitHub OAuth", "Autenticación de usuarios vía GitHub")
  System_Ext(google_oauth, "Google OAuth", "Autenticación de usuarios vía Google")
  
  Rel(usuario, saas, "Utiliza la plataforma", "HTTPS / WSS / JWT")
  Rel(cliente_anonimo, saas, "Visualiza contenido público", "HTTPS / Public Token")
  Rel(saas, stripe, "Crea cobros y recibe webhooks", "HTTPS / REST / Webhooks")
  Rel(saas, resend, "Envía emails transaccionales", "HTTPS / REST API")
  Rel(saas, expo_push, "Encola notificaciones móviles", "HTTPS / REST API")
  Rel(usuario, github_oauth, "Autentica identidad con", "OAuth 2.0")
  Rel(usuario, google_oauth, "Autentica identidad con", "OAuth 2.0")
```

---

## 2. DIAGRAMA C4 NIVEL 2: CONTENEDORES

Muestra las unidades de software desplegables, bases de datos y capas de almacenamiento en el Edge de Cloudflare y Supabase Cloud.

```mermaid
C4Container
  title Diagrama de Contenedores - Arquitectura Serverless / Edge

  Person(user, "Usuario Client", "Navegador Web / App Móvil / App Desktop")

  System_Boundary(cloudflare_edge, "Cloudflare Edge Global Network") {
    Container(frontend, "Frontend App", "React, TypeScript, Tailwind", "UI cliente servida globalmente vía Cloudflare Pages")
    Container(gateway, "API Gateway Worker", "Cloudflare Worker", "Punto de entrada único: Rate Limiting, Auth JWT, CORS y Ruteo")
    Container(workers_backend, "Micro-Workers Backend", "Cloudflare Workers", "Servicios de negocio independientes (docs, teams, notifs, billing)")
    Container(durable_objects, "Durable Objects", "Cloudflare DO", "Coordinación en tiempo real, cursores y WebSockets persistentes")
    Container(kv_cache, "Workers KV", "Cloudflare KV", "Caché global de baja latencia, feature flags y blacklist de tokens")
    Container(queues, "Cloudflare Queues", "Cloudflare Queues", "Cola de trabajos pesados asíncronos (> 15s)")
    Container(r2_storage, "R2 Storage", "Cloudflare R2", "Almacenamiento de objetos: imágenes, PDFs y assets de usuarios")
  }

  System_Boundary(supabase_cloud, "Supabase Managed Cloud") {
    ContainerDb(postgres_db, "PostgreSQL Database", "Supabase Postgres", "Base de datos relacional con RLS, pgvector e índices GIN")
    Container(supabase_auth, "Supabase Auth", "GoTrue Service", "Gestión de sesiones, JWT y proveedores OAuth")
    Container(supabase_realtime, "Supabase Realtime", "Elixir / WebSockets", "Motor de suscripciones de base de datos e In-App notifications")
  }

  Rel(user, frontend, "Carga UI estática", "HTTPS / CDN")
  Rel(user, gateway, "Peticiones API", "HTTPS / REST / JSON")
  Rel(user, durable_objects, "Conexión en tiempo real", "WSS / WebSockets")
  
  Rel(gateway, kv_cache, "Verifica rate-limit y caché", "KV API")
  Rel(gateway, workers_backend, "Delega peticiones internas", "Service Bindings (0ms RTT)")
  
  Rel(workers_backend, postgres_db, "Consultas con RLS / RPC", "PostgREST / HTTPS / SQL")
  Rel(workers_backend, r2_storage, "Streaming de archivos", "S3 API / R2 Binding")
  Rel(workers_backend, queues, "Encola jobs asíncronos", "Queue Binding")
  
  Rel(queues, workers_backend, "Consume jobs en batch", "Worker Queue Event")
  Rel(supabase_realtime, postgres_db, "Escucha WAL (Logical Replication)", "Postgres Extension")
```

---

## 3. DIAGRAMA C4 NIVEL 3: COMPONENTES (API GATEWAY)

Desglosa el funcionamiento interno del contenedor **API Gateway Worker** y su interacción vía **Service Bindings** con los micro-workers especializados.

```mermaid
C4Component
  title Diagrama de Componentes - API Gateway Worker

  Container_Boundary(api_gateway, "API Gateway Worker") {
    Component(router, "Router & Dispatcher", "TypeScript", "Rutea peticiones según la URL y método HTTP")
    Component(cors_mw, "CORS Middleware", "shared-http/cors", "Aplica cabeceras CORS quirúrgicas por entorno")
    Component(rate_mw, "Rate Limiter Middleware", "shared-http/rateLimit", "Verifica límites por IP / usuario en KV o DO")
    Component(auth_mw, "JWT Auth Middleware", "shared-http/auth", "Valida firmas JWT y extrae x-user-id")
    Component(response_lib, "Response Helper", "shared-http/response", "Estandariza respuestas ok() y fail()")
  }

  System_Ext(auth_worker, "Auth Worker", "Service Binding: env.AUTH_SERVICE")
  System_Ext(docs_worker, "Docs Worker", "Service Binding: env.DOCS_SERVICE")
  System_Ext(teams_worker, "Teams Worker", "Service Binding: env.TEAM_SERVICE")
  System_Ext(notif_worker, "Notifications Worker", "Service Binding: env.NOTIF_SERVICE")
  System_Ext(search_worker, "Search Worker", "Service Binding: env.SEARCH_SERVICE")

  Rel(router, cors_mw, "1. Valida origen CORS")
  Rel(router, rate_mw, "2. Evalúa límites de tráfico")
  Rel(router, auth_mw, "3. Verifica credenciales JWT")
  Rel(router, notif_worker, "Invoca /api/notifs/*", "Service Binding")
  Rel(router, docs_worker, "Invoca /api/docs/*", "Service Binding")
  Rel(router, teams_worker, "Invoca /api/teams/*", "Service Binding")
  Rel(router, search_worker, "Invoca /api/search/*", "Service Binding")
  Rel(router, auth_worker, "Invoca /api/auth/*", "Service Binding")
  Rel(router, response_lib, "Construye HTTP Response final")
```

---

## 4. DIAGRAMAS DE SECUENCIA

### 4.1 Flujo de Pago y Suscripción (Stripe → Worker → Webhook → Supabase)

Muestra cómo se procesa un pago seguro garantizando que el usuario **nunca** active suscripciones desde el cliente frontend (`PAYMENTS_SECURITY_STANDARD.md`).

```mermaid
sequenceDiagram
  autonumber
  actor Cliente as Cliente (Frontend)
  participant Worker as Worker API
  participant Stripe as Stripe API
  participant Webhook as Webhook Worker
  participant DB as Supabase Postgres
  participant Queue as Cloudflare Queue

  Cliente->>Worker: POST /api/payments/checkout (planId: "pro", Idempotency-Key)
  Worker->>Worker: Valida plan en backend (NUNCA precio del cliente)
  Worker->>Stripe: stripe.checkout.sessions.create({ line_items, client_reference_id })
  Stripe-->>Worker: Retorna Session URL
  Worker-->>Cliente: 200 OK (url: "https://checkout.stripe.com/c/pay/...")
  
  Cliente->>Stripe: Ingresa tarjeta en iframe / Checkout
  Stripe->>Stripe: Procesa el cobro exitosamente
  Stripe-->>Cliente: Redirige a /dashboard?checkout=success

  Note over Stripe,Webhook: Proceso Asíncrono Desacoplado de Confianza
  Stripe->>Webhook: POST /webhooks/stripe (stripe-signature)
  Webhook->>Webhook: 1. ConstructEvent(body, signature, secret)
  Webhook->>Webhook: 2. Verifica Replay Attack en KV (event.id)
  Webhook->>DB: 3. UPDATE subscriptions SET status='active' WHERE user_id=...
  DB-->>Webhook: OK
  Webhook->>Queue: 4. Encola email de confirmación
  Webhook-->>Stripe: 200 OK (received: true)
```

### 4.2 Flujo de Colaboración en Tiempo Real (WebSocket + Yjs + Durable Objects)

Demuestra cómo se sincronizan deltas CRDT y cursores múltiples entre colaboradores sin sobreescribir datos (`FRONTEND_CRDT_COLLABORATION.md`).

```mermaid
sequenceDiagram
  autonumber
  actor UserA as Usuario A (Editor)
  actor UserB as Usuario B (Editor)
  participant DO as Durable Object (DocRoom)
  participant Realtime as Supabase Realtime
  participant DB as Supabase Postgres

  UserA->>DO: 1. Conecta WebSocket (/doc/:id/ws)
  UserB->>DO: 2. Conecta WebSocket (/doc/:id/ws)
  Note over DO: Mantiene estado Y.Doc en memoria + Awareness

  UserA->>DO: 3. Envía delta Yjs (edición de texto)
  DO->>DO: 4. Merge de CRDT en memoria (Y.applyUpdate)
  DO-->>UserB: 5. Broadcast de delta a Usuario B (0ms RTT en Edge)

  UserB->>DO: 6. Envía posición de cursor { line: 12, col: 4 }
  DO-->>UserA: 7. Sync Awareness (renderiza cursor de B en UI de A)

  Note over DO,DB: Auto-Save diferido (Debounce / Snapshot)
  DO->>DB: 8. Persiste snapshot JSON en documents.content (cada 30s)
  DB-->>DO: OK
```

---

## 5. DIAGRAMA DE DESPLIEGUE (Deployment Architecture)

Ilustra la distribución física de la infraestructura en el Edge global de Cloudflare y la región de base de datos de Supabase.

```mermaid
deploymentDiagram
  title Diagrama de Despliegue Global - Cloudflare Edge + Supabase Region

  deploymentNode(user_device, "Dispositivo de Usuario", "Navegador Web / Mobile / Desktop") {
    node(browser, "Client Runtime (Vite/React)")
  }

  deploymentNode(cf_network, "Cloudflare Global Anycast Network (300+ Ciudades)", "Edge Infrastructure") {
    node(pages_cdn, "Cloudflare Pages", "Static Assets CDN")
    node(edge_worker, "Cloudflare Workers", "V8 Isolated Execution Contexts")
    node(edge_kv, "Cloudflare KV", "Distributed Key-Value Store")
    node(edge_r2, "Cloudflare R2", "S3-Compatible Object Store")
  }

  deploymentNode(aws_region, "Supabase Region (AWS us-east-1)", "Managed Cloud Provider") {
    node(pg_cluster, "PostgreSQL Cluster", "Primary DB + Read Replicas")
    node(gotrue, "GoTrue Auth Service", "OAuth & JWT Token Issuer")
  }

  browser -- pages_cdn : 1. Fetch HTML/JS/CSS (HTTP/3)
  browser -- edge_worker : 2. Peticiones API (HTTPS REST)
  edge_worker -- edge_kv : Read/Write Cache
  edge_worker -- edge_r2 : Streaming assets
  edge_worker -- pg_cluster : Connection Pooling (HTTPS / Transaction Mode)
  browser -- gotrue : Auth Tokens / Refresh
```

---

## HERRAMIENTAS Y REGLAS DE DOCUMENTACIÓN VISUAL

1. **Mermaid.js obligatorio:** Todos los diagramas del repositorio deben escribirse en bloque ```mermaid para permitir versionado Git en texto plano.
2. **Sin imágenes binarias sin fuente:** Queda prohibido subir diagramas PNG/JPG sin guardar el archivo fuente `.drawio` o `.excalidraw` en el mismo directorio.
3. **Mantenimiento en CI:** El pipeline de CI valida la sintaxis de todos los bloques Mermaid al ejecutar `npm run check`.
