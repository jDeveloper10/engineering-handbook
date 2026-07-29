---
title: "Índice de Patrones (Resolución Rápida)"
category: 00_Fundamentos
tags: [index, patrones, faq, arquitectura]
status: current
---

# Índice de Patrones (Resolución Rápida)

Si no sabes por dónde empezar a programar un requerimiento, busca tu caso de uso en esta tabla. En lugar de preguntar a Google "Cómo hacer X", usa los estándares de la casa.

| Necesito... | Archivo a consultar | Enfoque Principal / Patrón |
|-------------|---------------------|---------------------------|
| **Base de Datos & SQL** | | |
| Nombrar una tabla nueva | `04_Database/DATABASE_ENGINEERING_STANDARD.md` | Plural, `snake_case`, PK UUID |
| Manejar montos monetarios (USD, EUR) | `04_Database/DATABASE_ENGINEERING_STANDARD.md` | Columna `bigint` guardando centavos |
| Filtrar acceso según el usuario | `04_Database/DATABASE_ENGINEERING_STANDARD.md` | RLS (Row Level Security) Obligatorio |
| Dar acceso público a un recurso seguro | `04_Database/PATRON_ACCESO_PUBLICO_RLS.md` | `public_token` (UUID) en tabla + JWT claims custom |
| Prevenir borrado accidental de data | `04_Database/DATABASE_ENGINEERING_STANDARD.md` | Migración con Down, Soft Delete (`deleted_at`) |
| **Backend & Workers** | | |
| Crear una nueva ruta de API | `02_Backend/BACKEND_ENGINEERING_STANDARD.md` | Router → Middleware → Handler → Service |
| Devolver un error al frontend | `03_API/API_ENGINEERING_STANDARD.md` | Formato `{ success: false, error: { code, message } }` |
| Conectar dos workers internos | `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` | Service Bindings (no expuestos a internet) |
| Proteger de spam/fuerza bruta | `05_Security/ESTANDAR_RATE_LIMITING.md` | Middleware de Rate Limit + `CF-Connecting-IP` |
| Validar el body de una Request HTTP | `02_Backend/BACKEND_ENGINEERING_STANDARD.md` | Esquemas Zod obligatorios |
| **Archivos & Multimedia** | | |
| Subir una foto de perfil (1MB) | `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` | Subida a R2 vía Streaming (no ArrayBuffer en RAM) |
| Generar un archivo PDF | `08_Cloud/PATRON_GENERACION_PDF_EDGE.md` | `pdf-lib` inyectando texto sobre plantilla estática |
| Exponer imagen protegida a un usuario | `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` | Presigned URLs temporales a bucket privado |
| **Frontend & UI (React)** | | |
| Llamar a la API al cargar componente | `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` | React Query `useQuery` (PROHIBIDO `useEffect` fetch) |
| Actualizar estado UI tras botón (ej. Like) | `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` | React Query Mutación Optimista + Rollback en error |
| Prevenir que usuario pierda datos al cerrar | `01_Frontend/FRONTEND_FORMS_PATTERNS.md` | Dirty State protection (`beforeunload`) |
| Mostrar que la página está cargando | `01_Frontend/FRONTEND_STATES_PATTERNS.md` | Skeletons contextuales (no spinner genérico) |
| Si no hay resultados de búsqueda | `01_Frontend/FRONTEND_STATES_PATTERNS.md` | Empty State ilustrado con CTA claro |
| Manejar caída 500 del servidor | `01_Frontend/FRONTEND_ERROR_PAGES_STANDARD.md` | ErrorBoundary genérico con botón de "Reintentar" |
| Validar un email antes de enviar el form | `01_Frontend/FRONTEND_FORMS_PATTERNS.md` | Zod resolver + Debounce asíncrono para colisiones |
| Manejar conexión caída (offline) | `01_Frontend/FRONTEND_OFFLINE_STANDARD.md` | Dexie.js (IndexedDB) con sincronización manual |
| Recibir notificaciones en tiempo real | `01_Frontend/FRONTEND_REALTIME_PATTERN.md` | Hook `useRealtimeSubscription` (WebSockets) |
| **Seguridad & DevOps** | | |
| Leer un secreto (API KEY) sin hardcodear | `02_Backend/BACKEND_ENGINEERING_STANDARD.md` | `env.SECRET_KEY` + `wrangler secret put` |
| Validar permisos cross-tenant | `05_Security/SECURITY_ENGINEERING_STANDARD.md` | RLS es la fuente de verdad (defensa en profundidad) |
| Renderizar contenido HTML de terceros | `05_Security/SECURITY_ENGINEERING_STANDARD.md` | DOMPurify estricto antes de `dangerouslySetInnerHTML` |
| Manejar picos de lentitud en API | `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` | Conocer Cold Starts del Worker y tolerarlos UI |
| **Quality & Decisiones** | | |
| Qué probar/testear imperativamente | `06_Testing/` (Módulo) | Test 401/403, 500, RLS cross-tenant, Optimistic Rollback |
| Tomar una decisión arquitectónica nueva | `09_Architecture/ARCHITECTURE_DECISION_LOG.md` | Escribir un ADR (Architecture Decision Record) previo al PR |
| Hacer un Pull Request exitoso | `10_Code_Quality/FEATURE_PR_TEMPLATE.md` | Seguir el Checklist de PR a rajatabla |
| Diagnosticar timeout infinito | `11_Debugging/PLAYBOOK_CAIDA_API.md` | Network tab -> límites Cloudflare -> timeout React |
