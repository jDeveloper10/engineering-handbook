<div align="center" style="margin-bottom: 2rem;">

[![Author](https://img.shields.io/badge/Author-jDeveloper10-ff6b00?style=for-the-badge&logo=github)](https://github.com/jDeveloper10)
[![License](https://img.shields.io/badge/Propiedad%20Intelectual-jDeveloper10-black?style=for-the-badge&logo=shield)](LICENSE)

*Arquitectura, directrices y estándares de ingeniería desarrollados por **[@jDeveloper10](https://github.com/jDeveloper10)**.*

</div>

---
title: "Engineering Handbook — Portada"
category: root
doc_type: referencia
tags: [meta, indice, handbook]
summary: "Portada del handbook: qué es, estado de madurez por dominio y el stack de referencia que da contexto a todos los documentos."
keywords: [handbook, indice, estado, dominios, stack, portada]
updated: 2026-08-03
status: current
---

# ENGINEERING HANDBOOK

Manual de cómo desarrollar software — no un conjunto de prompts sueltos. Cada dominio (`01_Frontend`, `02_Backend`, ...) tiene sus propios documentos de estándares, escritos para que una IA (o yo) tome las mismas decisiones que tomaría un ingeniero senior consistente, en cualquier proyecto nuevo.

**Antes de leer cualquier dominio, leer [00_HANDBOOK_FORMAT.md](00_HANDBOOK_FORMAT.md)** — define las convenciones que todos los documentos siguen: reglas `REQUIRED`/`RECOMMENDED`, capa agnóstica + implementación de referencia, y la jerarquía de especialización (dominio → patrón → vertical).

## Estado por dominio

| # | Dominio | Estado | Documentos |
|---|---|---|---|
| 00 | Fundamentos | ✅ Completo | [SPEC_DRIVEN_DEVELOPMENT.md](00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md) (metodología: Spec → Zod → Test → Code → Verify) · [HISTORIA_INGENIERIA_SOFTWARE.md](00_Fundamentos/HISTORIA_INGENIERIA_SOFTWARE.md) (1945–2026) · [HISTORIA_INTERNET.md](00_Fundamentos/HISTORIA_INTERNET.md) |
| 01 | Frontend | ✅ Nivel 1 completo | [FRONTEND_ENGINEERING_STANDARD.md](01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md) (17 secciones) |
| | ↳ Nivel 2 | ✅ | [FRONTEND_UI_STYLE_CATALOG.md](01_Frontend/UI_Components/FRONTEND_UI_STYLE_CATALOG.md), [FRONTEND_LANDING_PATTERNS.md](01_Frontend/Patterns/FRONTEND_LANDING_PATTERNS.md), [FRONTEND_UI_PATTERNS.md](01_Frontend/Patterns/FRONTEND_UI_PATTERNS.md), [FRONTEND_NAVIGATION_PATTERNS.md](01_Frontend/Patterns/FRONTEND_NAVIGATION_PATTERNS.md), [FRONTEND_AUTH_PATTERNS.md](01_Frontend/Core/FRONTEND_AUTH_PATTERNS.md), [FRONTEND_DASHBOARD_PATTERNS.md](01_Frontend/Patterns/FRONTEND_DASHBOARD_PATTERNS.md), [FRONTEND_CRUD_PATTERNS.md](01_Frontend/Patterns/FRONTEND_CRUD_PATTERNS.md), [FRONTEND_TABLE_PATTERNS.md](01_Frontend/Patterns/FRONTEND_TABLE_PATTERNS.md), [FRONTEND_STATES_PATTERNS.md](01_Frontend/Patterns/FRONTEND_STATES_PATTERNS.md), [FRONTEND_NOTIFICATIONS_PATTERNS.md](01_Frontend/Patterns/FRONTEND_NOTIFICATIONS_PATTERNS.md), [FRONTEND_MODALS_PATTERNS.md](01_Frontend/Patterns/FRONTEND_MODALS_PATTERNS.md), [FRONTEND_SIDEBAR_PATTERNS.md](01_Frontend/Patterns/FRONTEND_SIDEBAR_PATTERNS.md), [FRONTEND_HTML_STRUCTURE_STANDARD.md](01_Frontend/Core/FRONTEND_HTML_STRUCTURE_STANDARD.md), [FRONTEND_RESPONSIVE_STANDARD.md](01_Frontend/Core/FRONTEND_RESPONSIVE_STANDARD.md), [FRONTEND_ACCESSIBILITY_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md), [FRONTEND_COLOR_CONTRAST_STANDARD.md](01_Frontend/UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md), [FRONTEND_ELEVATION_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ELEVATION_STANDARD.md), [FRONTEND_FORMATTING_STANDARD.md](01_Frontend/Core/FRONTEND_FORMATTING_STANDARD.md), [FRONTEND_ERROR_PAGES_STANDARD.md](01_Frontend/Patterns/FRONTEND_ERROR_PAGES_STANDARD.md), [FRONTEND_ANALYTICS_CHARTS_STANDARD.md](01_Frontend/Patterns/FRONTEND_ANALYTICS_CHARTS_STANDARD.md), [FRONTEND_MICROCOPY_STANDARD.md](01_Frontend/UI_Components/FRONTEND_MICROCOPY_STANDARD.md), [FRONTEND_ICON_SYSTEM_STANDARD.md](01_Frontend/UI_Components/FRONTEND_ICON_SYSTEM_STANDARD.md), [FRONTEND_MOTION_STANDARD.md](01_Frontend/UI_Components/FRONTEND_MOTION_STANDARD.md) |
| | ↳ Nivel 2 (nuevos) | ✅ | [FRONTEND_FORMS_PATTERNS.md](01_Frontend/Patterns/FRONTEND_FORMS_PATTERNS.md), [FRONTEND_FORM_CONTROLS_STANDARD.md](01_Frontend/UI_Components/FRONTEND_FORM_CONTROLS_STANDARD.md), [FRONTEND_OVERLAY_DISPLAY_STANDARD.md](01_Frontend/UI_Components/FRONTEND_OVERLAY_DISPLAY_STANDARD.md), [FRONTEND_REACT_STANDARD.md](01_Frontend/Core/FRONTEND_REACT_STANDARD.md), [FRONTEND_TYPESCRIPT_STANDARD.md](01_Frontend/Core/FRONTEND_TYPESCRIPT_STANDARD.md), [FRONTEND_HTML_ELEMENTS_REFERENCE.md](01_Frontend/UI_Components/FRONTEND_HTML_ELEMENTS_REFERENCE.md), [FRONTEND_SEO_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_SEO_STANDARD.md), [FRONTEND_PERFORMANCE_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_PERFORMANCE_STANDARD.md), [FRONTEND_PWA_I18N_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_PWA_I18N_STANDARD.md), [FRONTEND_OFFLINE_STANDARD.md](01_Frontend/Performance_SEO/FRONTEND_OFFLINE_STANDARD.md) |
| | ↳ Pendientes | ⬜ | FRONTEND_REAL_WORLD_ANALYSIS, Search & Filters, Settings, Profile, Checkout, Pricing, Wizards, Chat Interfaces, Calendar |
| 02 | Backend | ✅ Nivel 1 completo | [BACKEND_ENGINEERING_STANDARD.md](02_Backend/BACKEND_ENGINEERING_STANDARD.md) (17 secciones, multi-worker en Cloudflare) |
| 03 | API | ✅ Nivel 1 completo | [API_ENGINEERING_STANDARD.md](03_API/API_ENGINEERING_STANDARD.md) (contrato hacia afuera; envelope estándar ok/fail) |
| 04 | Database | ✅ Nivel 1 + Recetas | [DATABASE_ENGINEERING_STANDARD.md](04_Database/DATABASE_ENGINEERING_STANDARD.md), [DATABASE_COMMON_QUERIES.md](04_Database/References/DATABASE_COMMON_QUERIES.md), [RLS_POLICIES_LIBRARY.md](04_Database/References/RLS_POLICIES_LIBRARY.md), [DATABASE_MIGRATION_RECIPES.md](04_Database/References/DATABASE_MIGRATION_RECIPES.md), [DATABASE_PERFORMANCE.md](04_Database/References/DATABASE_PERFORMANCE.md) |
| 05 | Security | ✅ Nivel 1 + 2 + Toolkit | [SECURITY_ENGINEERING_STANDARD.md](05_Security/SECURITY_ENGINEERING_STANDARD.md), [SECRET_LEAK_PREVENTION_STANDARD.md](05_Security/SECRET_LEAK_PREVENTION_STANDARD.md) (cero secretos en bundles/Vite), [AUDIT_TOOLKIT_KALI_WSL.md](05_Security/AUDIT_TOOLKIT_KALI_WSL.md) (laboratorio Kali Linux en WSL 2: nmap, sslscan, ffuf, nuclei), [THREAT_MODEL.md](05_Security/THREAT_MODEL.md), [INCIDENT_RESPONSE.md](05_Security/INCIDENT_RESPONSE.md) |
| 06 | Testing (QA) | ✅ Completo | Departamento QA: [01_QA_STRATEGY](06_Testing/Strategy/01_QA_STRATEGY.md), [CHECKLIST_RELEASE_PRODUCCION.md](06_Testing/CHECKLIST_RELEASE_PRODUCCION.md) (checklist pre-entrega a cliente), [03_CI_CD](06_Testing/Pipelines/03_CI_CD.md), [05_BUG_LIFECYCLE](06_Testing/Guides/05_BUG_LIFECYCLE.md), [06_TEST_CHECKLIST](06_Testing/Strategy/06_TEST_CHECKLIST.md) + [Agents/](06_Testing/Agents/README.md) |
| 07 | DevOps | ✅ Nivel 1 + CI/CD | [GITHUB_STANDARD.md](07_DevOps/GITHUB_STANDARD.md), [GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md](07_DevOps/GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md) (pipeline CI/CD con lint, types, tests y secret scan), [DEPLOY_AND_FAILURES_STANDARD.md](07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) |
| 08 | Cloud | ✅ Nivel 1 + Patrones | [CLOUDFLARE_PLATFORM_STANDARD.md](08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md), [PATRON_R2_UPLOAD_SEGURO.md](08_Cloud/PATRON_R2_UPLOAD_SEGURO.md) (R2 sin secretos en React), [ESCALABILIDAD_Y_MANTENIMIENTO.md](08_Cloud/ESCALABILIDAD_Y_MANTENIMIENTO.md) (Sentry, pooling, cache y SLAs) |
| 09 | Architecture | ✅ Fase 1 completada | [STACK_SELECTION_MATRIX.md](09_Architecture/STACK_SELECTION_MATRIX.md) (matriz de selección de stack por cliente), [ARCHITECTURE_DECISION_LOG.md](09_Architecture/ARCHITECTURE_DECISION_LOG.md), [DIAGRAMAS_C4.md](09_Architecture/DIAGRAMAS_C4.md) |
| 10 | Code Quality | ✅ Fase 2 completada | [AGENCY_CODING_STANDARD.md](10_Code_Quality/AGENCY_CODING_STANDARD.md) (cero falsos 200, Zod en todo input, Clean Code), [CODE_REVIEW_STANDARD.md](10_Code_Quality/Reviews/CODE_REVIEW_STANDARD.md), [CODE_SMELLS_CATALOG.md](10_Code_Quality/Reviews/CODE_SMELLS_CATALOG.md) |
| 10b | Product / Clientes | ✅ Completo | [PRODUCT_REQUIREMENTS_STANDARD.md](10_Product/PRODUCT_REQUIREMENTS_STANDARD.md), [TEMPLATE_REQUERIMIENTOS_CLIENTE.md](10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md) (Discovery / Scope), [TEMPLATE_PROPUESTA_TECNICA.md](10_Product/TEMPLATES/TEMPLATE_PROPUESTA_TECNICA.md) (Hitos y Pagos) |
| 11 | Debugging | ✅ Fase 2 completada | [ERROR_INDEX.md](11_Debugging/ERROR_INDEX.md), [DEBUGGING_TOOLKIT.md](11_Debugging/DEBUGGING_TOOLKIT.md), [PERFORMANCE_DEBUGGING.md](11_Debugging/PERFORMANCE_DEBUGGING.md) |
| 12 | Documentation | ✅ Fase 1 completada | [DOCUMENTATION_STANDARD.md](12_Documentation/DOCUMENTATION_STANDARD.md), [TEMPLATE_ADR.md](12_Documentation/TEMPLATES/TEMPLATE_ADR.md), [TEMPLATE_README.md](12_Documentation/TEMPLATES/TEMPLATE_README.md) |
| 13 | AI Rules | ✅ Completo | [AI_WORKFLOW.md](13_AI_Rules/AI_WORKFLOW.md) (protocolo: clasificar tarea → leer estándar → verificar → implementar), [AI_PROMPTS_LIBRARY.md](13_AI_Rules/AI_PROMPTS_LIBRARY.md) |
| 14 | DX | ✅ Completo | [DX_STANDARD.md](14_DX/DX_STANDARD.md), [PROJECT_BOOTSTRAP_CHECKLIST.md](14_DX/PROJECT_BOOTSTRAP_CHECKLIST.md) (arranque paso a paso) |
| 15 | Knowledge System | ✅ Completo | [KNOWLEDGE_SYSTEM_STANDARD.md](15_Knowledge_System/KNOWLEDGE_SYSTEM_STANDARD.md), [RESEARCH_PROCESS.md](15_Knowledge_System/RESEARCH_PROCESS.md) · índice: [`tools/build-index.mjs`](tools/build-index.mjs) → `INDEX.json` |
| OS | Engineering OS | ✅ Control plane | [Operating Gate](Engineering-OS/32-Operating-Gate.md), [Feature Completeness Engine](Engineering-OS/33-Feature-Completeness-Engine.md), [Policy Profiles](Engineering-OS/34-Policy-Profiles.md), [Rule Registry](Engineering-OS/35-Rule-Registry.md) |

> **Arquitectura resuelta:** los dominios numerados `01–15` son la fuente de verdad técnica. `Engineering-OS/` es el plano operativo: activa perfiles, blueprints, registro de reglas y validadores; referencia las reglas técnicas por ID y no las duplica. Todo conflicto se reporta como defecto del handbook.
>
> **Frontmatter pendiente:** los documentos aún no llevan el frontmatter YAML del [Knowledge System](15_Knowledge_System/KNOWLEDGE_SYSTEM_STANDARD.md) (el retrofit quedó sin correr por corte de presupuesto). `node tools/build-index.mjs` ya genera `INDEX.json` y lo recogerá en cuanto se añada.

## Stack de referencia (contexto para todos los documentos)

- Frontend: React 19 + Vite + Tailwind + Framer Motion, TypeScript obligatorio
- Backend: Cloudflare Workers (multi-worker), template en `E:/workers-template`
- DB/Auth: Supabase
- Storage: R2 (Cloudinary en migración fuera)
- Email: Resend
- Automatización: n8n (VPS Contabo) + Baileys
- IA: OpenRouter → GPT-4o-mini
- Deploy: Cloudflare Pages + Workers + VPS Contabo
