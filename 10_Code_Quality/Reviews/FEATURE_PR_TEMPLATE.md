---
title: "Plantilla OBLIGATORIA de Pull Request"
category: 10_Code_Quality
tags: [pr, code-review, checklist, github]
summary: "Plantilla obligatoria de pull request para configurar en el repositorio: descripción del feature, checklist que no admite saltos, validación de reglas inquebrantables y evidencia visual."
keywords: [pr, code-review, checklist, github, plantilla, obligatoria, pull, request, configurar, repositorio, descripcion, feature, admite, saltos]
updated: 2026-07-29
status: current
---

# Plantilla OBLIGATORIA de Pull Request (FEATURE_PR_TEMPLATE.md)

Este documento debe configurarse como plantilla predeterminada en `.github/pull_request_template.md`. 
**Si un PR se abre sin completar los checklists aplicables, se rechaza automáticamente.**

```markdown
## Descripción del Feature
[Describe brevemente qué hace este PR, por qué es necesario, y un link a Jira/Linear]

---

## 🛑 CHECKLIST OBLIGATORIO (No saltar nada)

### 🗄️ Database (SIEMPRE PRIMERO)
- [ ] Se generó la migración SQL (Archivo `YYYYMMDD_name.sql`).
- [ ] La migración incluye un script de `DOWN` probado localmente para rollback.
- [ ] Toda nueva Foreign Key tiene un índice explícito (`CREATE INDEX`).
- [ ] **Políticas RLS:** Se agregaron/modificaron políticas de INSERT, SELECT, UPDATE y DELETE.
- [ ] No se usó `SELECT *` en ninguna consulta nueva en el código.
- [ ] Se comprobó el rendimiento (ej. no introduce un N+1 masivo en un endpoint popular).

### ⚙️ API y Backend
- [ ] Endpoints implementados siguiendo la convención Plural (`/api/resources`).
- [ ] Toda mutación tiene validación severa de Input usando **Zod**.
- [ ] Se implementó Rate Limiting en endpoints públicos/sensibles.
- [ ] Los códigos de error (`SCREAMING_SNAKE_CASE`) están listados en la documentación/frontend.
- [ ] No se comitearon secretos; se documentan en el README del worker las nuevas ENV_VARS necesarias.

### 🎨 Frontend
- [ ] **Los 4 Estados:** El componente principal implementa estados de `Loading` (Skeleton), `Empty`, `Error` (Retry), y `Success`.
- [ ] **React Query:** Toda llamada a API usa hooks de TanStack Query (no `useEffect` fetch).
- [ ] **Mutación Optimista:** Los toggles y acciones rápidas actualizan el UI al instante y aplican rollback en caso de fallo (`onError`).
- [ ] **Formularios:** Tienen prevención de Dirty State (`beforeunload`).
- [ ] TypeScript estricto: Ningún `any` o `@ts-ignore` añadido.

### 🔒 Seguridad
- [ ] Las consultas a base de datos están parametrizadas o manejan RLS correctamente.
- [ ] Los tokens temporales / links públicos expiran y usan validaciones UUID en Edge.
- [ ] Rate limiting (WAF o Middleware) verificado para proteger la base de datos de DDoS aplicativo.

### 🧪 Testing
- [ ] Se escribieron tests unitarios/E2E cubriendo el Happy Path y al menos un caso de error (401/403/500).
- [ ] Test cruzado de RLS (Usuario A NO ve datos de Usuario B).

### 📝 Documentación
- [ ] El CHANGELOG o README fue actualizado si es un cambio crítico de configuración.
- [ ] Si se tomó una decisión arquitectónica mayor, se enlazó el ADR correspondiente.

---

## ⚡ VALIDACIÓN DE REGLAS INQUEBRANTABLES
*(Aceptar conscientemente)*
- [ ] **DB-001:** Juro que no hay un solo `SELECT *`.
- [ ] **DB-002:** Juro que puse índices a todas mis FKs.
- [ ] **DB-003:** Juro que puedo hacer rollback a mi migración de base de datos.
- [ ] **DB-007:** Juro que mi nueva tabla que guarda usuarios TIENE RLS activado.
- [ ] **FE-TS:** Juro que no inyecté deuda técnica de TypeScript con `any`.

---

## Evidencia Visual (Opcional pero muy recomendado)
[Adjuntar capturas de pantalla o un video corto en MP4 mostrando el feature (Estados vacío, loading y error!)]
```
