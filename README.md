<div align="center">

# ⚡ ENGINEERING HANDBOOK
### *Operating System, Architecture & Engineering Standards*

[![Live Documentation](https://img.shields.io/badge/📖_Live_Portal-handbook--explorer.pages.dev-ff6b00?style=for-the-badge&logo=cloudflare&logoColor=white)](https://master.handbook-explorer.pages.dev/README)
[![Author](https://img.shields.io/badge/Author-jDeveloper10-18181b?style=for-the-badge&logo=github&logoColor=white)](https://github.com/jDeveloper10)
[![Documents](https://img.shields.io/badge/Documents-171+_Standards-3b82f6?style=for-the-badge&logo=files&logoColor=white)](INDEX.json)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge&logo=shield)](LICENSE)

<p align="center">
  <b>Sistema operativo de ingeniería, patrones de arquitectura y directrices de desarrollo para software de alta escala y agentes de Inteligencia Artificial.</b>
</p>

---

[🌐 Explorar Portal Web](https://master.handbook-explorer.pages.dev/README) • [🏗️ Dominios de Arquitectura](#-mapa-de-dominios-de-ingeniería) • [🛠️ Stack Oficial](#️-stack-tecnológico-oficial) • [🤖 Protocolo para IAs](#-operación-con-agentes-de-ia) • [📜 Licencia](#-propiedad-intelectual)

</div>

<br />

## 🌟 Pilares Fundamentales

<table>
  <tr>
    <td width="50%">
      <h3>⚡ Edge-First & Serverless</h3>
      <p>Arquitectura distribuida de ultra baja latencia con <b>Cloudflare Workers, D1 SQL, R2 Object Storage</b> y Durable Objects para tiempo real con costo operativo mínimo.</p>
    </td>
    <td width="50%">
      <h3>🛡️ Zero-Trust & Finanzas Blindadas</h3>
      <p>Manejo de dinero en centavos enteros (evitando fallos de coma flotante), prevención de fugas de secretos en bundles, idempotencia y auditoría de seguridad Kali/WSL.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🎨 UI/UX & Rendimiento Extremo</h3>
      <p>Estándares modernos con <b>React 19, TypeScript estricto, Tailwind CSS y Vite</b>. Accesibilidad WCAG AA, code-splitting dinámico y soporte offline.</p>
    </td>
    <td width="50%">
      <h3>🤖 AI-First & Automation</h3>
      <p>Directrices mandatorias para <b>Antigravity, Cursor, Claude Code y Copilot</b>. Flujos estandarizados mediante <code>AGENTS.md</code> y registro de políticas unificado.</p>
    </td>
  </tr>
</table>

<br />

## 🗺️ Mapa de Dominios de Ingeniería

| Dominio | Área Técnica | Estado | Documentos Clave |
| :---: | :--- | :---: | :--- |
| **01** | **Frontend & UI/UX** | ✅ Activo | [FRONTEND_STYLE_CATALOG](01_Frontend/UI_Components/FRONTEND_UI_STYLE_CATALOG.md) • [REACT_STANDARD](01_Frontend/Core/FRONTEND_REACT_STANDARD.md) • [TYPESCRIPT_STANDARD](01_Frontend/Core/FRONTEND_TYPESCRIPT_STANDARD.md) • [PERFORMANCE_STANDARD](01_Frontend/Performance_SEO/FRONTEND_PERFORMANCE_STANDARD.md) • [SEO_STANDARD](01_Frontend/Performance_SEO/FRONTEND_SEO_STANDARD.md) |
| **02** | **Backend Serverless** | ✅ Activo | [BACKEND_ENGINEERING_STANDARD](02_Backend/BACKEND_ENGINEERING_STANDARD.md) (Multi-worker Cloudflare, clean architecture y tipado estricto) |
| **03** | **API Design** | ✅ Activo | [API_ENGINEERING_STANDARD](03_API/API_ENGINEERING_STANDARD.md) (Contrato unificado con envelope <code>ok/fail</code> y códigos de error estándar) |
| **04** | **Database & SQL** | ✅ Activo | [DATABASE_ENGINEERING_STANDARD](04_Database/DATABASE_ENGINEERING_STANDARD.md) • [RLS_POLICIES_LIBRARY](04_Database/References/RLS_POLICIES_LIBRARY.md) • [DATABASE_PERFORMANCE](04_Database/References/DATABASE_PERFORMANCE.md) |
| **05** | **Security & Audits** | ✅ Activo | [SECURITY_ENGINEERING_STANDARD](05_Security/SECURITY_ENGINEERING_STANDARD.md) • [SECRET_LEAK_PREVENTION](05_Security/SECRET_LEAK_PREVENTION_STANDARD.md) • [AUDIT_TOOLKIT_KALI](05_Security/AUDIT_TOOLKIT_KALI_WSL.md) |
| **06** | **QA & Testing** | ✅ Activo | [QA_STRATEGY](06_Testing/Strategy/01_QA_STRATEGY.md) • [CHECKLIST_RELEASE_PRODUCCION](06_Testing/CHECKLIST_RELEASE_PRODUCCION.md) • [CI_CD_PIPELINE](06_Testing/Pipelines/03_CI_CD.md) |
| **07** | **DevOps & CI/CD** | ✅ Activo | [GITHUB_STANDARD](07_DevOps/GITHUB_STANDARD.md) • [GITHUB_ACTIONS_WORKFLOW](07_DevOps/GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md) • [DEPLOY_STANDARD](07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) |
| **08** | **Cloud & Storage** | ✅ Activo | [CLOUDFLARE_PLATFORM_STANDARD](08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md) • [PATRON_R2_UPLOAD_SEGURO](08_Cloud/PATRON_R2_UPLOAD_SEGURO.md) • [ESCALABILIDAD](08_Cloud/ESCALABILIDAD_Y_MANTENIMIENTO.md) |
| **09** | **Architecture** | ✅ Activo | [STACK_SELECTION_MATRIX](09_Architecture/STACK_SELECTION_MATRIX.md) • [ARCHITECTURE_DECISION_LOG](09_Architecture/ARCHITECTURE_DECISION_LOG.md) • [DIAGRAMAS_C4](09_Architecture/DIAGRAMAS_C4.md) |
| **10** | **Code Quality** | ✅ Activo | [AGENCY_CODING_STANDARD](10_Code_Quality/AGENCY_CODING_STANDARD.md) (Validación Zod estricta, Clean Code) • [CODE_REVIEW_STANDARD](10_Code_Quality/Reviews/CODE_REVIEW_STANDARD.md) |
| **10b** | **Product & Clients** | ✅ Activo | [PRODUCT_REQUIREMENTS_STANDARD](10_Product/PRODUCT_REQUIREMENTS_STANDARD.md) • [TEMPLATE_REQUERIMIENTOS](10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md) • [TEMPLATE_PROPUESTA](10_Product/TEMPLATES/TEMPLATE_PROPUESTA_TECNICA.md) |
| **11** | **Debugging** | ✅ Activo | [ERROR_INDEX](11_Debugging/ERROR_INDEX.md) • [DEBUGGING_TOOLKIT](11_Debugging/DEBUGGING_TOOLKIT.md) • [PERFORMANCE_DEBUGGING](11_Debugging/PERFORMANCE_DEBUGGING.md) |
| **12** | **Documentation** | ✅ Activo | [DOCUMENTATION_STANDARD](12_Documentation/DOCUMENTATION_STANDARD.md) • [TEMPLATE_ADR](12_Documentation/TEMPLATES/TEMPLATE_ADR.md) |
| **13** | **AI Engineering** | ✅ Activo | [AI_WORKFLOW](13_AI_Rules/AI_WORKFLOW.md) • [AI_PROMPTS_LIBRARY](13_AI_Rules/AI_PROMPTS_LIBRARY.md) • [NATURAL_LANGUAGE_GUIDE](13_AI_Rules/GUIA_LENGUAJE_NATURAL_PARA_NO_PROGRAMADORES.md) |
| **14** | **DX & Tooling** | ✅ Activo | [DX_STANDARD](14_DX/DX_STANDARD.md) • [PROJECT_BOOTSTRAP_CHECKLIST](14_DX/PROJECT_BOOTSTRAP_CHECKLIST.md) |
| **15** | **Knowledge OS** | ✅ Activo | [KNOWLEDGE_SYSTEM_STANDARD](15_Knowledge_System/KNOWLEDGE_SYSTEM_STANDARD.md) • [RESEARCH_PROCESS](15_Knowledge_System/RESEARCH_PROCESS.md) • [INDEX.json](INDEX.json) |
| **OS** | **Engineering OS** | ✅ Control | [Operating Gate](Engineering-OS/32-Operating-Gate.md) • [Feature Engine](Engineering-OS/33-Feature-Completeness-Engine.md) • [Rule Registry](Engineering-OS/35-Rule-Registry.md) |

<br />

## 🛠️ Stack Tecnológico Oficial

```
Frontend   │ React 19 + TypeScript + Vite + Tailwind CSS + Lucide Icons
Backend    │ Cloudflare Workers (TypeScript) / Serverless Edge Microservices
Database   │ Supabase / Cloudflare D1 (SQL con Migraciones Atómicas)
Storage    │ Cloudflare R2 (Firmas temporales presignadas)
Auth & RLS │ JWT con expiración controlada + Row Level Security (RLS)
CI/CD      │ GitHub Actions (Validación de Types, Lint y Secret Scanning)
Deployment │ Cloudflare Pages + Workers (Despliegues atómicos Zero-Downtime)
```

<br />

## 🤖 Operación con Agentes de IA

Este Handbook está optimizado para su consumo automático por modelos y agentes de desarrollo (*Antigravity, Claude Code, Cursor, Copilot*):

1. **Protocolo Obligatorio:** En la raíz de cada proyecto, incluir en `AGENTS.md` la referencia mandatoria hacia este Handbook.
2. **Ciclo de Ejecución:** `Clasificar Tarea` ➔ `Consultar Estándar en Handbook` ➔ `Planificar` ➔ `Implementar` ➔ `Verificar`.
3. **Mantenimiento Continuo:** Toda nueva solución o lección aprendida en producción se incorpora de forma declarativa con formato `DO / DON'T`.

<br />

---

## 📜 Propiedad Intelectual

<div align="center">

**Engineering Handbook** es propiedad intelectual de **[@jDeveloper10](https://github.com/jDeveloper10)**.  
Todos los derechos reservados © 2026.

*Prohibida su redistribución, duplicación o uso comercial no autorizado sin el consentimiento expreso del autor.*

</div>
