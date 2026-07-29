# Estructura del Proyecto: Engineering Handbook

Este proyecto es un **Manual de Ingeniería de Software** que contiene estándares, convenciones y patrones de diseño estructurados por dominios. Su objetivo es asegurar que tanto humanos como IA tomen decisiones técnicas consistentes basadas en reglas bien definidas.

A continuación se detalla la estructura de carpetas y los archivos Markdown (`.md`) de cada dominio:

## Raíz del Proyecto
- **`00_HANDBOOK_FORMAT.md`**: Define convenciones de formato de los documentos (reglas `REQUIRED`/`RECOMMENDED`, niveles de abstracción).
- **`README.md`**: Muestra el estado del manual y el stack tecnológico (React, Cloudflare, Supabase, etc.).
- **`AGENTS.md`**: Reglas de auto-ruteo para agentes IA.
- **`INDEX.json`**: Índice automático para búsqueda.

---

## Dominios (Carpetas)

### `00_Fundamentos`
- **`HISTORIA_INGENIERIA_SOFTWARE.md`**: Evolución de la Ingeniería de Software (1945–2026).
- **`HISTORIA_INTERNET.md`**: Historia de Internet y la web (1962–2026).

### `01_Frontend`
El dominio más extenso, estructurado en estándares generales y patrones específicos:
- **`FRONTEND_ENGINEERING_STANDARD.md`**: Estándar principal (Nivel 1) con 17 secciones clave.
- **Patrones Visuales y de UI**: `FRONTEND_UI_STYLE_CATALOG.md` (Catálogo de UI), `FRONTEND_UI_PATTERNS.md`, `FRONTEND_COLOR_CONTRAST_STANDARD.md`, `FRONTEND_ICON_SYSTEM_STANDARD.md`, `FRONTEND_ELEVATION_STANDARD.md`, `FRONTEND_MOTION_STANDARD.md`.
- **Componentes de la App**: `FRONTEND_LANDING_PATTERNS.md` (Landings), `FRONTEND_DASHBOARD_PATTERNS.md` (Paneles), `FRONTEND_NAVIGATION_PATTERNS.md` (Menús), `FRONTEND_SIDEBAR_PATTERNS.md`.
- **Gestión de Datos y Formularios**: `FRONTEND_CRUD_PATTERNS.md` (Vistas CRUD), `FRONTEND_TABLE_PATTERNS.md` (Tablas), `FRONTEND_FORMS_PATTERNS.md` (Formularios generales), `FRONTEND_FORM_CONTROLS_STANDARD.md` (Inputs, selects).
- **Estados y Feedback**: `FRONTEND_STATES_PATTERNS.md` (Cargando, vacío, errores), `FRONTEND_NOTIFICATIONS_PATTERNS.md` (Toast, alertas), `FRONTEND_MODALS_PATTERNS.md`, `FRONTEND_OVERLAY_DISPLAY_STANDARD.md`, `FRONTEND_ERROR_PAGES_STANDARD.md`.
- **Reglas Técnicas Core**: `FRONTEND_REACT_STANDARD.md` (Buenas prácticas en React), `FRONTEND_TYPESCRIPT_STANDARD.md` (Tipado), `FRONTEND_HTML_STRUCTURE_STANDARD.md`, `FRONTEND_HTML_ELEMENTS_REFERENCE.md`.
- **Optimización, Accesibilidad y Offline**: `FRONTEND_RESPONSIVE_STANDARD.md` (Mobile-first), `FRONTEND_ACCESSIBILITY_STANDARD.md` (a11y), `FRONTEND_SEO_STANDARD.md`, `FRONTEND_PERFORMANCE_STANDARD.md`, `FRONTEND_PWA_I18N_STANDARD.md`, `FRONTEND_OFFLINE_STANDARD.md` (Estrategia offline-first).

### `02_Backend`
- **`BACKEND_ENGINEERING_STANDARD.md`**: Estándares del desarrollo backend y arquitectura multi-worker (Cloudflare Workers).

### `03_API`
- **`API_ENGINEERING_STANDARD.md`**: Diseño de contratos de API, comunicación, respuestas y métodos HTTP (hereda de Backend).

### `04_Database`
- **`DATABASE_ENGINEERING_STANDARD.md`**: Estándares base de Postgres / Supabase.
- **`DATABASE_COMMON_QUERIES.md`**, **`DATABASE_MIGRATION_RECIPES.md`**, **`DATABASE_PERFORMANCE.md`**: Recetas de consultas optimizadas, migraciones seguras y profiling de performance.
- **`RLS_POLICIES_LIBRARY.md`**: Políticas de Row Level Security listas para copiar.

### `05_Security`
- **`SECURITY_ENGINEERING_STANDARD.md`**: Reglas y prácticas generales de seguridad.
- **`THREAT_MODEL.md`**: Modelado de 8 amenazas reales de la industria y su mitigación priorizada.
- **`INCIDENT_RESPONSE.md`**: Runbook o guía de respuesta rápida (primera hora) ante un incidente de seguridad.

### `06_Testing` (QA automatizado)
Departamento de calidad y pruebas automatizadas:
- **`README.md`**: Índice general de QA y Testing.
- **`01_QA_STRATEGY.md` a `05_BUG_LIFECYCLE.md`**: Documentos sobre estrategia, pipelines, CI/CD, procesos de lanzamiento y ciclo de vida de los bugs.
- **`06_TEST_CHECKLIST.md` a `10_PLAYBOOK.md`**: Checklists de pruebas, guía de automatización, estándares de calidad y métricas.
- **`Agents/README.md`**: Descripción de roles de QA y mapeo para agentes.

### `07_DevOps`
- **`GITHUB_STANDARD.md`**: Normas de repositorios, uso de Github Actions, secretos (PATs) y branch policies.
- **`DEPLOY_AND_FAILURES_STANDARD.md`**: Estándares de deploy, cómo hacer rollback y una librería de solución a fallos comunes (B1-B7).

### `08_Cloud`
- **`CLOUDFLARE_PLATFORM_STANDARD.md`**: Matriz de uso de infraestructura Cloudflare: Workers KV, R2, Queues, Durable Objects, reglas WAF y análisis de costos.

### `09_Architecture`
- **`ARCHITECTURE_DECISION_LOG.md`**: Registro (ADL) con los Architecture Decision Records (ADRs).
- **`DIAGRAMAS_C4.md`**: Guía para modelar sistemas con C4 y Mermaid.
- **`PATRONES_ARQUITECTONICOS.md`**: Patrones base (Edge, Jamstack, Event-Driven).

### `10_Code_Quality`
- **`CODE_REVIEW_STANDARD.md`**: Reglas y checklist para hacer pull requests (PRs).
- **`CODE_SMELLS_CATALOG.md`** y **`REFACTORING_RECIPES.md`**: Catálogo de malos olores en código React/TS y recetas para refactorizarlos.
- **`METRICAS_CALIDAD.md`** y **`STATIC_ANALYSIS_RULES.md`**: Reglas de ESLint, Prettier, complejidad y coverage.

### `11_Debugging`
- **`ERROR_INDEX.md`**: Índice global unificado (Troubleshooting) para solucionar los errores más comunes de todo el stack.
- **`DEBUGGING_TOOLKIT.md`** y **`PERFORMANCE_DEBUGGING.md`**: Herramientas y trucos de profiling en React y Workers.
- **`INCIDENT_PLAYBOOKS/`**: Guías paso a paso para diagnosticar caídas de API o Base de datos.

### `12_Documentation`
- **`DOCUMENTATION_STANDARD.md`**: Estándar principal sobre qué y cómo documentar.
- **`TEMPLATES/`**: Plantillas listas para usar como `TEMPLATE_ADR.md` y `TEMPLATE_README.md`.

### `13_AI_Rules`
- **`AI_WORKFLOW.md`**: Protocolo obligatorio que siguen las IA para clasificar tareas y verificar estándares antes de generar código.
- **`AI_PROMPTS_LIBRARY.md`**: 11 prompts listos y reutilizables por tipo de tarea.

### `14_DX` (Developer Experience)
- **`DX_STANDARD.md`**: Configuración unificada para que el código sea predecible (scripts de npm, estructura base).
- **`PROJECT_BOOTSTRAP_CHECKLIST.md`**: Pasos para arrancar un proyecto nuevo sin errores de inicio.

### `15_Knowledge_System`
- **`KNOWLEDGE_SYSTEM_STANDARD.md`**: Reglas sobre cómo guardar conocimiento, metadatos y asegurar compatibilidad RAG (búsqueda inteligente de información).
- **`RESEARCH_PROCESS.md`**: Flujos para investigar y documentar correctamente.
- **`ENGINEERING_INTELLIGENCE.md`**: Fundamentos sobre inteligencia en procesos de software.

---

### Otras Carpetas / Sistemas
- **`tools/`**: Herramientas utilitarias de Node.js (ej. generador del índice de búsqueda inteligente `build-index.mjs`).
- **`Engineering-OS/`**: Capa heredada de documentos de arquitectura. Actualmente está en transición para fusionarse con los dominios numerados y evitar desactualizaciones.
