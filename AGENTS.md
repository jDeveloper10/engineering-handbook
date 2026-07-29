---
title: "AGENTS.md — Sistema de Decisión Central, Auto-Ruteo y Motor de Auditoría Autónoma"
category: root
tags: [auto-routing, decision-tree, agent-rules, standards, architecture, security, core, trust-hierarchy, audit-scorecard, backlog-generator]
summary: "El cerebro central del Engineering Handbook. Guía de auto-ruteo obligatorio, jerarquía de resolución de conflictos, catálogo de reglas inquebrantables, Jerarquía de Confianza (Trust Hierarchy), generador de backlog de lagunas técnicos y motor de auditoría con Scorecard y mapas de calor."
keywords: [agents.md, decision-tree, auto-routing, ai-rules, inquebrantables, hierarchy, checklist, standards, trust-hierarchy, scorecard, backlog]
updated: 2026-07-27
status: current
---

# 🧠 AGENTS.md — Sistema de Decisión Central, Auto-Ruteo y Motor de Auditoría Autónoma

> Este documento es el **CEREBRO Y MANUAL DE OPERACIONES OBLIGATORIO** que toda IA (Claude Code, Antigravity, ChatGPT, Cursor, Copilot o subagentes autónomos) debe leer y procesar antes de planificar, analizar o escribir una sola línea de código en este repositorio.

---

## ⚡ REGLA CERO: LEE ESTO ANTES DE HACER CUALQUIER COSA

Si eres un modelo de Inteligencia Artificial o un Agente Autónomo ejecutando una tarea:

1. **NO escribas código todavía.**
2. **NO asumas patrones, rutas ni librerías** basadas en tu entrenamiento genérico.
3. **Clasifica el dominio de la tarea** usando el **Árbol de Decisión** en la Sección 1.
4. **Abre y lee el archivo específico** que el árbol indica (lee solo el documento relevante, no toda la base de datos).
5. **Aplica las Reglas Inquebrantables (`[REQUIRED]`)** sin negociar ni omitir validaciones.
6. **Verifica la solución** utilizando el **Checklist Pre-Entrega (Sección 7)** antes de responder o enviar un Pull Request.
7. **Emite la Auditoría y Scorecard del Handbook (Sección 9)** al final de cada propuesta de arquitectura o análisis.

> 🔴 **SI UNA TAREA TIENE LAGUNAS DE COBERTURA (`[HANDBOOK INCOMPLETO]`):**
> 1. Detén la generación de código y emite la estructura `missing_documents` con el impacto de dependencias y el objeto `task` de Backlog.
> 2. Ejecuta la investigación aplicando la **Jerarquía de Confianza (Trust Hierarchy)** descrita en la Sección 8 (Nivel 2 al Nivel 5).
> 3. Genera automáticamente el borrador (`status: DRAFT`, `confidence: XX%`, `reviewed: false`) siguiendo `00_HANDBOOK_FORMAT.md`.
> 4. Tras la aprobación humana, integra el estándar en la carpeta correspondiente, re-indexa con `node tools/build-index.mjs` y actualiza las tablas de ruteo en este `AGENTS.md`.

---

## 🌳 1. ÁRBOL DE DECISIÓN PRINCIPAL: ¿QUÉ ARCHIVO CONSULTAR?

Clasifica la necesidad del usuario o del sistema y navega directamente al archivo Markdown indicado.

---

### 🗄️ 1.1 BASE DE DATOS (`04_Database/`)

- **¿Crear tabla, vista o esquema SQL inicial?**
  👉 [DATABASE_ENGINEERING_STANDARD.md](04_Database/DATABASE_ENGINEERING_STANDARD.md)
  *Reglas clave:* Usar `UUID` para IDs, `TIMESTAMPTZ` para fechas, `snake_case`, activar RLS en cada tabla.

- **¿Reglas de escalabilidad, FKs e índices?**
  👉 [DATABASE_SCALABILITY_STANDARD.md](04_Database/DATABASE_SCALABILITY_STANDARD.md)
  *Reglas clave:* Toda Foreign Key exige un índice secundario. Usar centavos (`bigint`) para dinero.

- **¿Optimizar lecturas/escrituras en Cloudflare D1 (SQLite Edge)?**
  👉 [D1_OPTIMIZATION.md](04_Database/D1_OPTIMIZATION.md)
  *Reglas clave:* Minimizar filas leídas, usar `stmt.raw()`, batching de queries en una sola petición HTTP.

- **¿Acceso público seguro con tokens RLS?**
  👉 [PATRON_ACCESO_PUBLICO_RLS.md](04_Database/PATRON_ACCESO_PUBLICO_RLS.md)
  *Reglas clave:* Políticas de lectura pública condicionadas a token UUID indivinable y estado `is_public = TRUE`.

- **¿Búsqueda semántica, embeddings y vectores (`pgvector`)?**
  👉 [DATABASE_VECTOR_SEARCH.md](04_Database/DATABASE_VECTOR_SEARCH.md)
  *Reglas clave:* `text-embedding-3-small` de OpenAI (1536 dims), índice HNSW con distancia coseno, fallback a FTS.

- **¿Migración de datos Zero-Downtime, D1 o Firestore → Supabase?**
  👉 [DATA_MIGRATION_STRATEGIES.md](04_Database/DATA_MIGRATION_STRATEGIES.md)
  *Reglas clave:* Patrón Expand/Contract, doble escritura, backfill en chunks <= 1000, checksum de validación pre/post.

- **¿Aislamiento de datos Multi-Tenant con Supabase RLS?**
  👉 [MULTI_TENANCY_ADVANCED.md](04_Database/MULTI_TENANCY_ADVANCED.md)
  *Reglas clave:* `tenant_id UUID NOT NULL` en todas las tablas, helper `current_tenant_id()`, RLS de aislamiento estricto.

- **¿Copiar políticas RLS probadas para tablas compartidas?**
  👉 [RLS_POLICIES_LIBRARY.md](04_Database/References/RLS_POLICIES_LIBRARY.md)

- **¿Consultar recetas de queries comunes (paginación, joins)?**
  👉 [DATABASE_COMMON_QUERIES.md](04_Database/References/DATABASE_COMMON_QUERIES.md)

- **¿Ver recetas de migración UP/DOWN de esquemas?**
  👉 [DATABASE_MIGRATION_RECIPES.md](04_Database/References/DATABASE_MIGRATION_RECIPES.md)

---

### ⚙️ 1.2 BACKEND Y API (`02_Backend/` & `03_API/`)

- **¿Crear un nuevo Cloudflare Worker o endpoint REST?**
  👉 [BACKEND_ENGINEERING_STANDARD.md](02_Backend/BACKEND_ENGINEERING_STANDARD.md)
  *Reglas clave:* Router → Middleware → Handler → Service → Data. Usar helpers `ok()` y `fail()`.

- **¿Arquitectura de Workers como backend único (sin VPS/Express)?**
  👉 [WORKERS_AS_BACKEND.md](02_Backend/WORKERS_AS_BACKEND.md)
  *Reglas clave:* Workers es el único backend para Web, Mobile, Desktop e IoT. NUNCA Express/Django/VPS.

- **¿Diseñar la API Gateway y Service Bindings entre Workers?**
  👉 [API_GATEWAY_PATTERN.md](02_Backend/API_GATEWAY_PATTERN.md)
  *Reglas clave:* Gateway expone rutas públicas; invoca Workers internos vía `env.SERVICE.fetch()` (0ms RTT).

- **¿Proteger llamadas a servicios externos con Circuit Breaker?**
  👉 [CIRCUIT_BREAKER_PATTERN.md](02_Backend/CIRCUIT_BREAKER_PATTERN.md)
  *Reglas clave:* 5 fallos en 30s habren el circuito (OPEN). Recovery time 30s.

- **¿Reintentos con Exponential Backoff y Jitter?**
  👉 [RETRY_PATTERN.md](02_Backend/RETRY_PATTERN.md)
  *Reglas clave:* Decorrelate Jitter para evitar thundering herd problem en peticiones fallidas.

- **¿Implementar fallback y degradación elegante bajo sobrecarga?**
  👉 [GRACEFUL_DEGRADATION_PATTERN.md](02_Backend/GRACEFUL_DEGRADATION_PATTERN.md)

- **¿Procesar tareas pesadas (>15s, PDF, reportes, Queues)?**
  👉 [HEAVY_COMPUTE_STANDARD.md](02_Backend/HEAVY_COMPUTE_STANDARD.md)
  *Reglas clave:* Responder 202 Accepted encolando el trabajo en Cloudflare Queues.

- **¿Sincronización bidireccional y estrategia Offline-First?**
  👉 [SYNC_STRATEGIES.md](02_Backend/SYNC_STRATEGIES.md)
  *Reglas clave:* Cola offline en IndexedDB (Dexie.js), Last Write Wins / CRDTs, tracking de estado.

- **¿Envío de Emails (Resend + React Email)?**
  👉 [NOTIFICATIONS_STANDARD.md](02_Backend/NOTIFICATIONS_STANDARD.md)
  *Reglas clave:* NUNCA HTML crudo. Usar plantillas React Email en `packages/email-templates`.

- **¿Emails avanzados (Rebotes, entregabilidad, A/B Testing)?**
  👉 [EMAIL_ADVANCED_STANDARD.md](02_Backend/EMAIL_ADVANCED_STANDARD.md)
  *Reglas clave:* Webhook para `bounces` y `complaints`, deshabilitar email inmediatamente en Supabase.

- **¿Notificaciones Web Push (VAPID) y Mobile Push (Expo)?**
  👉 [NOTIFICATIONS_STANDARD.md](02_Backend/NOTIFICATIONS_STANDARD.md)
  *Reglas clave:* VAPID private key en secretos del Worker. Expo Push Service para iOS/Android.

- **¿Definir el contrato de respuestas API, status codes y errores?**
  👉 [API_ENGINEERING_STANDARD.md](03_API/API_ENGINEERING_STANDARD.md)
  *Reglas clave:* Envelope `{ success: true, data: ... }` o `{ success: false, error: { code, message } }`.

- **¿Optimizar consumo de CPU, memoria y bindings en Workers?**
  👉 [WORKERS_OPTIMIZATION.md](02_Backend/WORKERS_OPTIMIZATION.md)

---

### 🎨 1.3 FRONTEND — CORE Y PATRONES DE UX (`01_Frontend/`)

- **¿Crear un nuevo componente React o definir arquitectura de UI?**
  👉 [FRONTEND_ENGINEERING_STANDARD.md](01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md)

- **¿Reglas de React (hooks personalizados, estado, React Query)?**
  👉 [FRONTEND_REACT_STANDARD.md](01_Frontend/Core/FRONTEND_REACT_STANDARD.md)
  *Reglas clave:* Custom hooks para lógica, React Query para fetching, cero `useEffect` para mutaciones.

- **¿Estándar de TypeScript estricto, Zod e interfaces?**
  👉 [FRONTEND_TYPESCRIPT_STANDARD.md](01_Frontend/Core/FRONTEND_TYPESCRIPT_STANDARD.md)
  *Reglas clave:* NUNCA `any`. Usar `unknown` y estrechar tipos con Schemas de Zod.

- **¿Estructura HTML5 semántica y accesibilidad nativa?**
  👉 [FRONTEND_HTML_STRUCTURE_STANDARD.md](01_Frontend/Core/FRONTEND_HTML_STRUCTURE_STANDARD.md)

- **¿Diseño adaptativo (Responsive Breakpoints, Mobile-First)?**
  👉 [FRONTEND_RESPONSIVE_STANDARD.md](01_Frontend/Core/FRONTEND_RESPONSIVE_STANDARD.md)

- **¿Implementar autenticación en cliente (Login, OAuth, RLS)?**
  👉 [FRONTEND_AUTH_PATTERNS.md](01_Frontend/Core/FRONTEND_AUTH_PATTERNS.md)

- **¿Desarrollar aplicación móvil con React Native y Expo?**
  👉 [MOBILE_ENGINEERING_STANDARD.md](01_Frontend/Core/MOBILE_ENGINEERING_STANDARD.md)
  ⚠️ **Obligatorio leer también** [MOBILE_SECURITY_STANDARD.md](05_Security/MOBILE_SECURITY_STANDARD.md) — un APK es código publicado.

- **¿Desarrollar aplicación de escritorio con Tauri y React?**
  👉 [DESKTOP_ENGINEERING_STANDARD.md](01_Frontend/Core/DESKTOP_ENGINEERING_STANDARD.md)
  ⚠️ **Obligatorio leer también** [DESKTOP_SECURITY_STANDARD.md](05_Security/DESKTOP_SECURITY_STANDARD.md) — el webview no es de confianza.

- **¿Manejar los 4 estados de UI (Loading, Empty, Error, Success)?**
  👉 [FRONTEND_STATES_PATTERNS.md](01_Frontend/Patterns/FRONTEND_STATES_PATTERNS.md)
  *Reglas clave:* OBLIGATORIO implementar los 4 estados en todo componente asíncrono.

- **¿Formularios simples con validación Zod?**
  👉 [FRONTEND_FORMS_PATTERNS.md](01_Frontend/Patterns/FRONTEND_FORMS_PATTERNS.md)

- **¿Formularios complejos de múltiples pasos (>10 campos)?**
  👉 [FRONTEND_MULTISTEP_FORMS.md](01_Frontend/Patterns/FRONTEND_MULTISTEP_FORMS.md)

- **¿Mutaciones optimistas instantáneas (sin spinners)?**
  👉 [FRONTEND_OPTIMISTIC_MUTATIONS.md](01_Frontend/Patterns/FRONTEND_OPTIMISTIC_MUTATIONS.md)

- **¿Pantallas CRUD completas (lista + detalle + edición)?**
  👉 [FRONTEND_CRUD_PATTERNS.md](01_Frontend/Patterns/FRONTEND_CRUD_PATTERNS.md)

- **¿Tablas avanzadas con paginación y ordenamiento?**
  👉 [FRONTEND_TABLE_PATTERNS.md](01_Frontend/Patterns/FRONTEND_TABLE_PATTERNS.md)

- **¿Chat en tiempo real con Supabase Realtime?**
  👉 [FRONTEND_REALTIME_CHAT.md](01_Frontend/Patterns/FRONTEND_REALTIME_CHAT.md)

- **¿Notificaciones In-App en tiempo real?**
  👉 [FRONTEND_REALTIME_PATTERN.md](01_Frontend/Patterns/FRONTEND_REALTIME_PATTERN.md)

- **¿Editor de texto enriquecido WYSIWYG (TipTap)?**
  👉 [FRONTEND_RICH_TEXT_EDITOR.md](01_Frontend/Patterns/FRONTEND_RICH_TEXT_EDITOR.md)

- **¿Colaboración simultánea multitrabajador con Yjs / CRDTs?**
  👉 [FRONTEND_CRDT_COLLABORATION.md](01_Frontend/Patterns/FRONTEND_CRDT_COLLABORATION.md)

- **¿Drag & Drop accesibles (Kanban, listas) con `@dnd-kit`?**
  👉 [FRONTEND_DRAG_DROP_STANDARD.md](01_Frontend/Patterns/FRONTEND_DRAG_DROP_STANDARD.md)

---

### 🎨 1.4 FRONTEND — DISEÑO VISUAL, PERFORMANCE, SEO Y PWA

- **¿Catálogo de estilos, paleta de colores y design tokens?**
  👉 [FRONTEND_UI_STYLE_CATALOG.md](01_Frontend/UI_Components/FRONTEND_UI_STYLE_CATALOG.md)

- **¿Contraste de colores y accesibilidad visual (WCAG AA)?**
  👉 [FRONTEND_COLOR_CONTRAST_STANDARD.md](01_Frontend/UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md)

- **¿Sistema de sombras, elevaciones y orden z-index?**
  👉 [FRONTEND_ELEVATION_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ELEVATION_STANDARD.md)

- **¿Sistema de iconos (Lucide React) y tamaños?**
  👉 [FRONTEND_ICON_SYSTEM_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ICON_SYSTEM_STANDARD.md)

- **¿Animaciones y micro-interacciones de UI?**
  👉 [FRONTEND_MOTION_STANDARD.md](01_Frontend/UI_Components/FRONTEND_MOTION_STANDARD.md)

- **¿Microcopy (textos de interfaz, alertas y mensajes)?**
  👉 [FRONTEND_MICROCOPY_STANDARD.md](01_Frontend/UI_Components/FRONTEND_MICROCOPY_STANDARD.md)

- **¿Temas dinámicos Dark/Light con variables CSS?**
  👉 [FRONTEND_THEMES_STANDARD.md](01_Frontend/UI_Components/FRONTEND_THEMES_STANDARD.md)

- **¿Accesibilidad web nivel AA y manejo de foco por teclado?**
  👉 [FRONTEND_ACCESSIBILITY_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md)

- **¿Accesibilidad Avanzada (Focus Trap, WCAG 2.1 AA, axe)?**
  👉 [FRONTEND_ACCESSIBILITY_ADVANCED.md](01_Frontend/UI_Components/FRONTEND_ACCESSIBILITY_ADVANCED.md)

- **¿Optimizar rendimiento web (LCP, bundle splitting, lazy)?**
  👉 [FRONTEND_PERFORMANCE_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_PERFORMANCE_STANDARD.md)

- **¿Configurar meta tags básicos y SEO para la web?**
  👉 [FRONTEND_SEO_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_SEO_STANDARD.md)

- **¿SEO Avanzado (Schema.org JSON-LD, sitemap, hreflang)?**
  👉 [FRONTEND_SEO_ADVANCED.md](01_Frontend/Performance_SEO/FRONTEND_SEO_ADVANCED.md)

- **¿Convertir la app en Progressive Web App (PWA)?**
  👉 [FRONTEND_PWA_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_PWA_STANDARD.md)

- **¿PWA Avanzado (Background Sync, Badging, File System)?**
  👉 [FRONTEND_PWA_ADVANCED.md](01_Frontend/Performance_SEO/FRONTEND_PWA_ADVANCED.md)

- **¿Estrategias de funcionamiento Offline?**
  👉 [FRONTEND_OFFLINE_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_OFFLINE_STANDARD.md)

- **¿Soporte multi-idioma (i18n básico con React)?**
  👉 [FRONTEND_I18N_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_I18N_STANDARD.md)

- **¿i18n Avanzado (Lenguajes RTL, pluralización, Intl API)?**
  👉 [FRONTEND_I18N_ADVANCED.md](01_Frontend/Performance_SEO/FRONTEND_I18N_ADVANCED.md)

---

### 🔒 1.5 SEGURIDAD Y CUMPLIMIENTO (`05_Security/`)

- **¿Validaciones Zod, protección XSS, SQLi, CORS, JWT?**
  👉 [SECURITY_ENGINEERING_STANDARD.md](05_Security/SECURITY_ENGINEERING_STANDARD.md)

- **¿Configurar Rate Limiting por IP o Usuario?**
  👉 [ESTANDAR_RATE_LIMITING.md](05_Security/ESTANDAR_RATE_LIMITING.md)

- **¿Autenticación Multifactor (TOTP, Passkeys, Magic Links)?**
  👉 [AUTH_MFA_STANDARD.md](05_Security/AUTH_MFA_STANDARD.md)
  *Reglas clave:* `AUTH-003` para login (15 min), `AUTH-004` para invitaciones a equipos (48h, excepción).

- **¿Magic Link de Login?**
  👉 [AUTH_MFA_STANDARD.md](05_Security/AUTH_MFA_STANDARD.md) (`AUTH-003`: TTL 15 min, un solo uso).

- **¿Invitación a Equipo por Email?**
  👉 [AUTH_MFA_STANDARD.md](05_Security/AUTH_MFA_STANDARD.md) (`AUTH-004`: TTL 48h, token propio revocable).

- **¿Dashboard con métricas o analytics?**
  👉 [API_ENGINEERING_STANDARD.md](03_API/API_ENGINEERING_STANDARD.md) (`API-007`: Presupuesto latencia < 200ms p95, vistas materializadas).

- **¿Autenticación Avanzada (SAML SSO, Social OAuth, Sessions)?**
  👉 [AUTH_ADVANCED_STANDARD.md](05_Security/AUTH_ADVANCED_STANDARD.md)

- **¿Ciberseguridad Avanzada (CSP, SRI, DNSSEC, security.txt)?**
  👉 [SECURITY_ADVANCED.md](05_Security/SECURITY_ADVANCED.md)

- **¿Seguridad de una app de ESCRITORIO (Tauri): IPC, updater, secretos, code signing?**
  👉 [DESKTOP_SECURITY_STANDARD.md](05_Security/DESKTOP_SECURITY_STANDARD.md)
  *Reglas clave:* `DSEC-001` ACL de capabilities mínima (nunca scope `**`), `DSEC-002` canonicalizar rutas ANTES de validar el prefijo, `DSEC-004` cero secretos en el binario + tokens en el keychain del SO, `DSEC-005` updater con firma verificada.

- **¿Seguridad de una app MÓVIL / APK (Android): firma, TLS, Keystore, OTA?**
  👉 [MOBILE_SECURITY_STANDARD.md](05_Security/MOBILE_SECURITY_STANDARD.md)
  *Reglas clave:* `MSEC-001` `EXPO_PUBLIC_*` es público literalmente (cero secretos en el bundle), `MSEC-002` keystore fuera del repo + Play App Signing, `MSEC-004` tokens en SecureStore (nunca AsyncStorage), `MSEC-008` la detección de root es señal, no puerta.

- **¿Qué documento de seguridad aplica a mi plataforma? ¿Qué NO está cubierto?**
  👉 [05_Security/README.md](05_Security/README.md) (mapa de cobertura y alcance declarado).

- **¿Procesamiento Seguro de Pagos con Stripe (PCI DSS)?**
  👉 [PAYMENTS_SECURITY_STANDARD.md](05_Security/PAYMENTS_SECURITY_STANDARD.md)

- **¿Cumplimiento Legal (GDPR, CCPA, DPA, Términos, Cookies)?**
  👉 [LEGAL_COMPLIANCE_STANDARD.md](05_Security/LEGAL_COMPLIANCE_STANDARD.md)

- **¿Respuesta ante incidentes y filtraciones de datos?**
  👉 [INCIDENT_RESPONSE.md](05_Security/INCIDENT_RESPONSE.md)

- **¿Análisis de modelo de amenazas (Threat Modeling)?**
  👉 [THREAT_MODEL.md](05_Security/THREAT_MODEL.md)

---

### ☁️ 1.6 CLOUD, ARQUITECTURA Y DEVOPS (`07_DevOps/`, `08_Cloud/`, `09_Architecture/`)

- **¿Operar Cloudflare (Workers, KV, R2, D1, Queues, DO)?**
  👉 [CLOUDFLARE_PLATFORM_STANDARD.md](08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md)

- **¿Generación de PDFs en el Edge con `pdf-lib`?**
  👉 [PATRON_GENERACION_PDF_EDGE.md](08_Cloud/PATRON_GENERACION_PDF_EDGE.md)

- **¿Documentar decisiones de arquitectura (ADRs)?**
  👉 [ARCHITECTURE_DECISION_LOG.md](09_Architecture/ARCHITECTURE_DECISION_LOG.md)

- **¿Crear diagramas de arquitectura C4 con Mermaid.js?**
  👉 [DIAGRAMAS_C4.md](09_Architecture/DIAGRAMAS_C4.md)

- **¿Patrones arquitectónicos generales (CQRS, Event-Driven)?**
  👉 [PATRONES_ARQUITECTONICOS.md](09_Architecture/PATRONES_ARQUITECTONICOS.md)

- **¿Patrones de escalabilidad (Sharding, Load Shedding, R2 Multipart)?**
  👉 [SCALABILITY_PATTERNS.md](09_Architecture/SCALABILITY_PATTERNS.md)

- **¿Estructura de Monorepo con Turborepo y pnpm?**
  👉 [MONOREPO_STANDARD.md](09_Architecture/MONOREPO_STANDARD.md)

- **¿Configurar pipelines de CI/CD con GitHub Actions?**
  👉 [CI_CD_PIPELINE.md](07_DevOps/CI_CD_PIPELINE.md)

- **¿CI/CD Avanzado (Rollbacks automáticos, Blue/Green)?**
  👉 [CI_CD_ADVANCED.md](07_DevOps/CI_CD_ADVANCED.md)

- **¿Observabilidad, trazabilidad y monitoreo de logs?**
  👉 [OBSERVABILITY_STANDARD.md](07_DevOps/OBSERVABILITY_STANDARD.md)

- **¿Infraestructura como código con Terraform / Wrangler?**
  👉 [INFRA_AS_CODE.md](07_DevOps/INFRA_AS_CODE.md)

- **¿Estrategias de despliegue y prevención de caídas?**
  👉 [DEPLOY_AND_FAILURES_STANDARD.md](07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md)

- **¿Convenciones de Git, ramas, PRs, commits y uso de GitHub?**
  👉 [GITHUB_STANDARD.md](07_DevOps/GITHUB_STANDARD.md)
  *Alcance:* Uso de Git/GitHub como cliente. Construir un servidor Git (Git Forge) está fuera de alcance (`[HANDBOOK INCOMPLETO]`).

---

### 🎯 1.7 PRODUCTO, MONETIZACIÓN, IA Y HERRAMIENTAS (`10_Product/`, `12_Documentation/`, `13_AI_Rules/`, `14_DX/`)

- **¿Escribir un PRD de Requisitos de Producto para IAs?**
  👉 [PRODUCT_REQUIREMENTS_STANDARD.md](10_Product/PRODUCT_REQUIREMENTS_STANDARD.md)

- **¿Analytics de producto (PostHog, Funnels, A/B Testing)?**
  👉 [PRODUCT_ANALYTICS_STANDARD.md](10_Product/PRODUCT_ANALYTICS_STANDARD.md)

- **¿Estrategia de monetización, precios y facturación?**
  👉 [MONETIZATION_STANDARD.md](10_Product/MONETIZATION_STANDARD.md)

- **¿Reglas de flujo de trabajo y pair-programming con IA?**
  👉 [AI_WORKFLOW.md](13_AI_Rules/AI_WORKFLOW.md)

- **¿Catálogo de prompts optimizados para ingeniería?**
  👉 [AI_PROMPTS_LIBRARY.md](13_AI_Rules/AI_PROMPTS_LIBRARY.md)

- **¿Servidores y Herramientas MCP (Model Context Protocol)?**
  👉 [MCP_TOOLS_STANDARD.md](13_AI_Rules/MCP_TOOLS_STANDARD.md)

- **¿Desplegar IA y ML en Producción (RAG, pgvector, SSE)?**
  👉 [AI_ML_PRODUCTION.md](13_AI_Rules/AI_ML_PRODUCTION.md)

- **¿Estándar de documentación (CLAUDE.md, OpenAPI/Swagger)?**
  👉 [DOCUMENTATION_STANDARD.md](12_Documentation/DOCUMENTATION_STANDARD.md)

- **¿Documentación avanzada (OpenAPI diff, Storybook, Status Page)?**
  👉 [DOCUMENTATION_ADVANCED.md](12_Documentation/DOCUMENTATION_ADVANCED.md)

- **¿Developer Experience (Bootstrap, Scripts npm, VS Code)?**
  👉 [DX_STANDARD.md](14_DX/DX_STANDARD.md)

- **¿Generadores de código Plop y DevContainers?**
  👉 [DEVELOPER_TOOLS_STANDARD.md](14_DX/DEVELOPER_TOOLS_STANDARD.md)

- **¿Cookies seguras, 4 niveles de caché y optimizaciones de red?**
  👉 [COOKIES_CACHE_OPTIMIZATION.md](00_Fundamentos/COOKIES_CACHE_OPTIMIZATION.md)

---

### 🐛 1.8 DEBUGGING E INCIDENTES (`11_Debugging/`)

- **¿El upload de archivos falla o se queda en cargando?**
  👉 [PLAYBOOK_UPLOAD_FAIL.md](11_Debugging/PLAYBOOK_UPLOAD_FAIL.md)

- **¿Spinner de carga infinito en la interfaz?**
  👉 [PLAYBOOK_SPINNER_INFINITO.md](11_Debugging/PLAYBOOK_SPINNER_INFINITO.md)

- **¿Cloudflare Worker con cold start o ejecución lenta (> 1s)?**
  👉 [PLAYBOOK_WORKER_COLD_START.md](11_Debugging/PLAYBOOK_WORKER_COLD_START.md)

- **¿Base de datos Supabase o D1 caída o con timeouts?**
  👉 [PLAYBOOK_DATABASE_DOWN.md](11_Debugging/PLAYBOOK_DATABASE_DOWN.md)

- **¿Error HTTP 500 genérico sin contexto?**
  👉 [PLAYBOOK_ERROR_500.md](11_Debugging/PLAYBOOK_ERROR_500.md)

- **¿API caída o devolviendo HTTP 503?**
  👉 [PLAYBOOK_CAIDA_API.md](11_Debugging/PLAYBOOK_CAIDA_API.md)

- **¿Índice global de códigos de error runtime?**
  👉 [ERROR_INDEX.md](11_Debugging/ERROR_INDEX.md)

---

## 📊 2. MATRIZ DE PRIORIDAD Y ORDEN DE EJECUCIÓN

Cuando una tarea requiera múltiples componentes (ejemplo: "Crear pantalla de pagos con formulario y backend"), **la IA DEBE procesar y aplicar las reglas en este orden estricto:**

```
1. SEGURIDAD & COMPLIANCE   ──→ PAYMENTS_SECURITY_STANDARD / SECURITY_ENGINEERING_STANDARD
2. BASE DE DATOS & RLS      ──→ DATABASE_ENGINEERING_STANDARD / MULTI_TENANCY_ADVANCED
3. BACKEND & API CONTRACT   ──→ WORKERS_AS_BACKEND / API_ENGINEERING_STANDARD
4. FRONTEND & ESTADOS UI    ──→ FRONTEND_REACT_STANDARD / FRONTEND_STATES_PATTERNS
5. TESTING & VERIFICACIÓN   ──→ ADVANCED_TESTING_STANDARD / TEST_CHECKLIST
6. DEVOPS & CI/CD          ──→ CI_CD_PIPELINE / DEPLOY_AND_FAILURES
```

> **REGLA DE ORO DE PRIORIDAD:** *"Si existe un conflicto entre entregar rápido o cumplir con la seguridad/RLS, LA SEGURIDAD SIEMPRE GANA. Sin excepciones."*

---

## ⚡ 3. JERARQUÍA DE CONFLICTO Y NIVELES DE REGLAS

Si dos documentos o patrones parecen dar instrucciones contradictorias, aplica la siguiente escala de precedencia:

1. **Reglas Inquebrantables de Nivel 1 (`[REQUIRED]` con ID de regla):** Tienen prioridad absoluta sobre cualquier otra sugerencia (ejemplo: `DB-001`, `S-001`, `WORKER-001`, `MONEY-001`).
2. **Estándares de Dominio Principal:** Instrucciones marcadas como `[REQUIRED]` en archivos `*_ENGINEERING_STANDARD.md`.
3. **Patrones Recomendados (`[RECOMMENDED]`):** Buenas prácticas de UX o arquitectura.
4. **Sugerencias y Guías (`[SUGGESTED]` / Templates):** Ejemplos de referencia y plantillas.

---

## 📋 4. CATÁLOGO DE REGLAS INQUEBRANTABLES CRÍTICAS

- **`DB-001`**: NUNCA usar `SELECT *`. Especificar columnas explícitas en cada consulta SQL.
- **`DB-002`**: Toda Foreign Key DEBE tener un índice secundario asociado.
- **`DB-008`**: NUNCA usar `float` o `double` para montos de dinero. Usar `bigint` o enteros en centavos.
- **`S-001`**: Todo payload de entrada (frontend y backend) DEBE ser validado con un schema de Zod.
- **`S-005`**: NUNCA configurar CORS con wildcard `*` en entornos autenticados.
- **`S-007`**: NUNCA guardar tokens JWT en `localStorage`. Usar cookies `HttpOnly; Secure; SameSite=Strict`.
- **`WORKER-001`**: Un solo stack de Workers para todos los clientes (Web, Mobile, Desktop).
- **`WORKER-002`**: NUNCA usar frameworks de servidor tradicional (Express, Fastify, Django, Laravel).
- **`FE-001`**: NUNCA usar `any` en TypeScript. Usar `unknown` y estrechar tipos.
- **`FE-005`**: Todo componente asíncrono DEBE manejar los 4 estados de UI (Loading, Empty, Error, Success).
- **`NOTIF-001`**: NUNCA enviar HTML crudo en correos. Usar plantillas versionadas de React Email.
- **`MONEY-001`**: Precios NUNCA definidos en el frontend. El backend resuelve el monto y el `stripePriceId`.
- **`MIG-001`**: NUNCA ejecutar una migración de datos sin un plan de Rollback verificado.
- **`SYNC-001`**: NUNCA perder datos del usuario por un conflicto de sincronización.
- **`AI-001`**: NUNCA enviar PII ni datos sensibles del usuario a modelos externos sin anonimización.
- **`SEO-001`**: Toda página pública DEBE incluir datos estructurados JSON-LD válidos según Schema.org.
- **`AUTH-001`**: Bloqueo progresivo en login (máximo 5 intentos fallidos en 5 minutos).
- **`AUTH-003`**: Magic Links de Login con TTL máximo de 15 minutos y un solo uso.
- **`AUTH-004`**: Invitaciones a equipo con TTL extendido de 48h (excepción justificada por UX, token propio revocable, rate-limit 10/h).
- **`API-007`**: Presupuesto de latencia por tipo de endpoint (Dashboards < 200ms, CRUD < 500ms, Webhooks < 100ms).
- **`TENANT-001`**: RLS es la fuente de verdad inquebrantable para aislamiento multi-tenant.
- **`CICD-001`**: Rollback automático si la tasa de errores supera el 1% post-deploy.
- **`PWA-001`**: La aplicación DEBE funcionar offline con los datos de las últimas 24 horas.
- **`A11Y-001`**: Todo elemento interactivo DEBE ser accesible por teclado.
- **`I18N-001`**: NUNCA hardcodear cadenas de texto en componentes UI.
- **`SEC-001`**: Content Security Policy (CSP) estricta en todas las respuestas HTTP.
- **`SCALE-003`**: Subida Multipart en R2 para archivos > 100MB.

---

## 🚫 5. LO QUE UNA IA NUNCA DEBE HACER (ANTI-PATRONES PROHIBIDOS)

- ❌ **NUNCA** escribir código de producción sin consultar previamente el documento estándar correspondiente.
- ❌ **NUNCA** inventar librerías, estándares o configuraciones que no pertenezcan al stack oficial.
- ❌ **NUNCA** usar `any` en TypeScript o desactivar `strict: true`.
- ❌ **NUNCA** usar `export default` en utilidades o componentes. **Excepciones cerradas (`FE-004`):** (1) handlers de Workers/Pages; (2) archivos de ruta/layout de frameworks de *file-based routing* que lo exigen técnicamente — Expo Router, Next.js App Router; (3) archivos de configuración de herramientas (`vite.config.ts`, `playwright.config.ts`, `eslint.config.js`), que no son ni utilidades ni componentes.
- ❌ **NUNCA** usar `SELECT *` en la base de datos (especificar columnas explícitas).
- ❌ **NUNCA** crear Foreign Keys sin un índice secundario asociado.
- ❌ **NUNCA** silenciar errores con bloques `try { ... } catch {}` vacíos o retornar fallbacks falsos `200 OK`.
- ❌ **NUNCA** inventar un estándar usando únicamente blogs, Medium o StackOverflow como fuente principal.

---

## ✅ 6. LO QUE UNA IA SIEMPRE DEBE HACER (COMPORTAMIENTOS OBLIGATORIOS)

- ✅ **SIEMPRE** consultar este `AGENTS.md` como punto de arranque antes de actuar.
- ✅ **SIEMPRE** abrir y leer el archivo Markdown específico del mapa de ruteo antes de generar código.
- ✅ **SIEMPRE** aplicar las Reglas Inquebrantables (`[REQUIRED]`) del dominio sin omitir validaciones.
- ✅ **SIEMPRE** estructurar los componentes async de React con los 4 estados de UI (Loading, Empty, Error, Success).
- ✅ **SIEMPRE** estandarizar respuestas API con la envolvente `ok()` y `fail()`.
- ✅ **SIEMPRE** utilizar `React Query` para data fetching (cero `useEffect` descontrolados).
- ✅ **SIEMPRE** nombrar tablas y columnas de base de datos en `snake_case` y código TypeScript en `camelCase`.

---

## 🎯 7. CHECKLIST RÁPIDO PRE-ENTREGA (13 PUNTOS OBLIGATORIOS)

- [ ] **1. Estándar:** ¿Consulté el documento estándar correspondiente en el Árbol de Decisión?
- [ ] **2. Inquebrantables:** ¿Se cumplen todas las Reglas Inquebrantables asociadas al dominio?
- [ ] **3. TypeScript:** ¿El código está en modo estricto sin uso de `any` ni `export default` indebido?
- [ ] **4. Validación:** ¿Los datos de entrada son validados con Zod tanto en frontend como en backend?
- [ ] **5. Estados UI:** ¿El componente de UI maneja los 4 estados (Loading, Empty, Error, Success)?
- [ ] **6. Response Envelope:** ¿Las respuestas de la API utilizan el helper envelope estándar `ok()` o `fail()`?
- [ ] **7. Rate Limiting:** ¿Se aplicó Rate Limiting si es un endpoint o función pública?
- [ ] **8. Data Fetching:** ¿El data fetching usa React Query (y no `useEffect` directo)?
- [ ] **9. Naming:** ¿Las tablas y columnas en la DB usan `snake_case` y el código TypeScript `camelCase`?
- [ ] **10. SQL:** ¿Las consultas SQL especifican columnas explícitas (sin `SELECT *`)?
- [ ] **11. Pruebas:** ¿Se incluyeron pruebas (unitarias o de integración) para el flujo exitoso y los casos de error?
- [ ] **12. Migración:** ¿Si hubo cambios de base de datos, se generó la migración con scripts UP y DOWN?
- [ ] **13. Trazabilidad:** ¿Se citaron las reglas y archivos del Handbook aplicados en la respuesta/PR?
- [ ] **14. Coherencia del Handbook:** si la entrega **modificó archivos del handbook**, ¿corrió `npm run lint` en verde? (ver §11)

---

## 🧪 11. PROTOCOLO ANTI-CONTRADICCIÓN (el handbook se audita a sí mismo)

El riesgo estructural de un handbook con cientos de bloques de código es que **un ejemplo viole la regla que el propio handbook exige**. Cuando eso pasa, una IA que copia el ejemplo genera código no conforme *citando el handbook como fuente* — el error se propaga con la autoridad del documento. Auditar esto a mano no escala y no se sostiene en el tiempo.

**[REQUIRED]** Todo PR que modifique un `.md` del handbook corre el validador antes de mergear:

```bash
npm run lint
```

`tools/lint-handbook.mjs` escanea **solo los bloques de código** (la prosa que enuncia una regla no es una violación) y verifica los patrones de: `DB-001` (SELECT *), `FE-001` (`any`), `S-005` (CORS wildcard), `S-007` (JWT en localStorage), `SEC-001` (CSP unsafe-inline/eval), `NOTIF-001` (HTML crudo en email), catch vacío, y `DB-008` (dinero en float, como aviso de revisión manual). Exit code 1 si hay violaciones bloqueantes → apto para CI (`CICD-002`).

### Las tres formas válidas de que un patrón "prohibido" aparezca en el handbook

El linter las reconoce y **no** las cuenta como violación. Cualquier otra aparición es un bug del handbook:

| Forma | Cómo se marca | Ejemplo |
|---|---|---|
| **Anti-ejemplo didáctico** | Línea o contexto con `❌`, `ANTI-PATRÓN`, `JAMÁS`, `INCORRECTO` | `` // ❌ app.use(cors({ origin: '*' })) `` |
| **Excepción justificada** | Comentario que contiene literalmente `EXCEPCIÓN DOCUMENTADA` + el motivo + el riesgo aceptado + la vía de eliminación | CSP `style-src 'unsafe-inline'` en `SECURITY_ADVANCED.md §1` |
| **Prosa normativa** | Línea de lista/checklist que enuncia la regla | `- [ ] **DB-001:** no hay un solo SELECT *` |

**[REQUIRED]** Una excepción **nunca** se declara solo apagando el linter. El marcador `EXCEPCIÓN DOCUMENTADA` obliga a escribir, en el mismo lugar: (1) por qué la regla no aplica aquí, (2) qué riesgo se acepta a cambio, (3) bajo qué condición se elimina la excepción. Una excepción sin esos tres campos es deuda disfrazada de decisión.

**[REQUIRED]** Cuando el linter detecta una violación real, la corrección es **arreglar el ejemplo**, no relajar la regla ni agregar el marcador de excepción para silenciarlo. Bajar la regla al nivel del código que la incumple invierte la relación: el handbook deja de ser la autoridad y pasa a documentar lo que ya se hizo mal.

---

## 🌐 8. JERARQUÍA DE CONFIANZA Y CLASIFICACIÓN KNOWLEDGETYPE (TRUST HIERARCHY & KNOWLEDGE TAXONOMY)

Cuando una tarea o tema técnico **NO exista** en el Engineering Handbook (`[HANDBOOK INCOMPLETO]`), la IA actúa en rol de **Auditor + Investigador + Curador + Arquitecto de Conocimiento**, ejecutando una investigación autónoma respetando la siguiente **Jerarquía de Confianza de 7 Niveles** y clasificando el conocimiento investigado:

### 8.1 Nivel de Confianza de Fuentes (7-Tier Trust Hierarchy)

```
[ Nivel 1: 100% — Engineering Handbook (Fuente de Verdad Primaria) ]
                       │ (Si existe aquí: DETENTE. No investigues nada)
                       ▼
[ Nivel 2: 99%  — Especificaciones Oficiales (ISO, IEC, RFC, IETF, W3C, WHATWG, ECMA, Unicode, POSIX) ]
                       │
                       ▼
[ Nivel 3: 98%  — Documentación Oficial de Tecnología (React, TypeScript, Node, Postgres, Cloudflare, Supabase, etc.) ]
                       │
                       ▼
[ Nivel 4: 97%  — Marcos de Seguridad y Estándares (OWASP ASVS, NIST CSF, NIST SP 800, MITRE, CIS, PCI DSS) ]
                       │
                       ▼
[ Nivel 5: 95%  — Investigaciones & Tech Blogs de Élite (IEEE, ACM, Google/Meta/Cloudflare/Netflix/Stripe Engineering) ]
                       │
                       ▼
[ Nivel 6: 80%  — Comunidad (GitHub Discussions, Issues, StackOverflow — Solo evidencia secundaria) ]
                       │
                       🚫 PROHIBIDO (0%)
[ Nivel 7: 0%   — Blogs personales, Medium, Dev.to, YouTube, Tutoriales o IA como fuente principal ]
```

### 8.2 Sistema de Clasificación `KnowledgeType` (Peso Normativo)

Toda afirmación, regla o recomendación DEBE etiquetarse según su peso normativo exacto:

```yaml
KnowledgeType:
  MANDATORY:
    description: "Especificación oficial e inquebrantable (ej. RFC 9110, ISO/IEC, W3C)."
    weight: 1.00
  STANDARD:
    description: "Estándar de la industria formalmente aceptado (ej. OWASP ASVS, NIST, PCI DSS)."
    weight: 0.95
  BEST_PRACTICE:
    description: "Buena práctica respaldada por documentación oficial del proyecto (ej. Docs de React/Cloudflare/Postgres)."
    weight: 0.90
  RECOMMENDATION:
    description: "Recomendación u orientación de diseño del fabricante de la tecnología."
    weight: 0.80
  EXPERIMENTAL:
    description: "Funcionalidad o especificación experimental no consolidada."
    weight: 0.50
  COMMUNITY:
    description: "Consenso empírico de comunidad. NUNCA normativo."
    weight: 0.30
  UNKNOWN:
    description: "Sin evidencia suficiente. Respuesta obligatoria cuando no se pueda demostrar."
    weight: 0.00
```

---

## 📊 9. MOTOR DE AUDITORÍA FORMAL, MÉTRICAS RIGUROSAS Y BACKLOG

La IA puede ejecutar cualquiera de los siguientes marcos de auditoría formales:
- **Calidad y Arquitectura:** ISO 25010 (31 Subcaracterísticas), ISO 29148, ISO 12207, ISO 15288.
- **Seguridad y Privacidad:** ISO 27001, ISO 27002, OWASP ASVS, OWASP Top 10, OWASP API, NIST CSF, NIST 800-53, NIST 800-63, PCI DSS, CIS Benchmarks.
- **Protocolos y Especificaciones:** WCAG 2.2, RFC HTTP (9110/6265), RFC JWT, OAuth2, PKCE, OpenAPI, GraphQL Spec, OpenTelemetry.

### 9.1 Regla de Precisión Matemática en Métricas
- ❌ **PROHIBIDO** emitir porcentajes o scores arbitrarios o estimaciones a ojo.
- ✅ **OBLIGATORIO** calcular las métricas mediante la ratio matemática exacta:
  $$\text{Cobertura} = \frac{\text{Ítems Cubiertos Directamente}}{\text{Total Ítems Evaluados}}$$

### 9.2 Formato Estricto de Cita de Evidencia
Toda afirmación o regla citada DEBE incluir sus metadatos verificables:
- **Documento:** [`01_Frontend/Patterns/FRONTEND_CRDT_COLLABORATION.md`](01_Frontend/Patterns/FRONTEND_CRDT_COLLABORATION.md)
- **Versión / Fecha:** `2026-07-26` | **Estado:** `VERIFIED`
- **KnowledgeType:** `BEST_PRACTICE` | **Reglas:** `FRONTEND_CRDT-001`

### 9.3 Estructura `missing_document` y Borradores (`draft_document`)
Cuando el Handbook no cubra un área, la IA generará la estructura formal:

```yaml
missing_document:
  target_document: 01_Frontend/Patterns/FRONTEND_PLUGIN_ARCHITECTURE_STANDARD.md
  priority: CRITICAL
  reason: "Requisito de extensión por terceros no cubierto en Handbook."
  blocked_features:
    - Marketplace de Plugins
    - Sandbox de código de terceros
  recommended_sources:
    - "W3C WebAssembly Core Specification (Nivel 2 / MANDATORY)"
    - "MDN iFrame Sandbox API Specification (Nivel 3 / BEST_PRACTICE)"
  estimated_sections:
    - Isolation & WASM Sandboxing Model
    - Extension Host Event Loop
  knowledge_type: STANDARD
```

Si la IA genera un borrador técnico pre-aprobación, utilizará el bloque:

```yaml
draft_document:
  status: DRAFT
  confidence: 96%
  review_required: true
  sources:
    - "RFC 9110 HTTP Semantics (Nivel 2 / MANDATORY)"
  reason: "Expansión autónoma del Handbook bajo Jerarquía de Confianza."
  affected_documents:
    - 03_API/API_ENGINEERING_STANDARD.md
  affected_rules:
    - API-007
```

---

## 🔍 10. CHECKLIST AUTOMÁTICO DE CALIDAD AUDITADA

Antes de entregar cualquier propuesta de arquitectura o documento, la IA ejecutará y verificará internamente:

- [ ] **Duplicados:** Sin reglas o párrafos repetidos.
- [ ] **Contradicciones:** Sin inconsistencias con `AGENTS.md` ni entre subdocumentos.
- [ ] **Reglas Huérfanas:** Toda regla pertenece a un estándar y tiene un identificador único.
- [ ] **Documentos Huérfanos:** Todos los archivos están enlazados en el Árbol de Decisión de `AGENTS.md`.
- [ ] **Enlaces Rotos:** Todos los enlaces son rutas relativas y apuntan a archivos existentes.
- [ ] **Naming:** Nombres de archivo y reglas siguen la convención UPPERCASE/snake_case.
- [ ] **Decisiones e Incompatibilidades:** Evaluado el impacto en retrocompatibilidad (Breaking Changes).
- [ ] **Evidencia:** Cero especulaciones; si algo no es demostrable, responder `UNKNOWN`.

---

## 🔄 11. CICLO COMPLETO DE EXPANDIBILIDAD AUTÓNOMA (THE SELF-EXPANDING LOOP)

```text
[ 1. Usuario solicita Feature / Arquitectura ]
                     │
                     ▼
[ 2. Análisis de Cobertura en Handbook (169 Docs) ]
                     │
                     ▼
[ 3. ¿Existe laguna? ── (NO) ──→ Entregar solución 100% VERIFIED ]
                     │
                    (SÍ)
                     ▼
[ 4. Emitir missing_document + Blast Radius + Task Backlog ]
                     │
                     ▼
[ 5. Investigación en Jerarquía de Confianza (Nivel 2 a Nivel 5) + KnowledgeType ]
                     │
                     ▼
[ 6. Generar Borrador del Nuevo Estándar (draft_document, status: DRAFT) ]
                     │
                     ▼
[ 7. Esperar Aprobación Humana (reviewed: true) ]
                     │
                     ▼
[ 8. Integrar al Handbook, Re-indexar (build-index.mjs) y Actualizar AGENTS.md ]
                     │
                     ▼
[ 9. Cobertura incrementada ──→ Retomar respuesta de Arquitectura ]
```
