---
title: "30 — Handbook Audit (Baseline 2026-07-26)"
category: knowledge
tags:
  - conventions
  - checklists
  - standards
  - performance
summary: "Auditoría baseline del Engineering Handbook y Engineering-OS: fortalezas, áreas de mejora, scores cualitativos y recomendaciones accionables. Captura el estado del ecosistema al 2026-07-26 como referencia para medir progreso."
keywords:
  - engineering-os
  - audit
  - health-check
  - solapamiento
  - frontmatter
  - retrieval
  - consistency
  - baseline
updated: 2026-07-26
status: current
---

# 30 — Handbook Audit (Baseline 2026-07-26)

> Baseline del ecosistema completo. Se recalcula después de cada ronda de mejoras del roadmap para
> medir si el sistema de estándares de verdad mejora. **Fecha de referencia:** 2026-07-26.
>
> **Qué audita:** el handbook completo (`01_Frontend` a `15_Knowledge_System` + `Engineering-OS/`
> + `AGENTS.md`/`CLAUDE.md`). **Qué NO audita:** el código de los proyectos reales (eso es trabajo
> de los agentes de QA en `06_Testing/Agents/`).
>
> **Consumidor:** cualquier IA en sesión de mejora del [handbook](../README.md) o antes de una decisión
> arquitectónica grande. No necesita leerse completo — la tabla de scores y las recomendaciones
> bastan para diagnóstico rápido.
>
> **Nota para IAs:** esta auditoría fue realizada por una IA externa (Buffy/Freebuff) como
> segunda opinión sobre el estado del handbook. No es auto-análisis ni proviene de una sesión de
> ENGINEERING_INTELLIGENCE — es una revisión fresca desde cero.

---

## Scores de salud (0-100)

Cada score es cualitativo con evidencia verificable. Se actualizan en cada re-auditoría.

| Score | Baseline 2026-07-26 | Fórmula / criterio |
|---|---|---|
| **Architecture Score** | 65 | Claridad de la estructura general, separación de niveles, relación entre Engineering-OS y dominios numerados. Penaliza el solapamiento no resuelto. |
| **Coverage Score** | 78 | % de dominios con contenido sustancial (11/15 con documentos, 4 en README-only ≈ 73%; ajuste +5 por profundidad de los existentes). |
| **Consistency Score** | 55 | % de documentos que siguen el formato REQUIRED/RECOMMENDED, tienen frontmatter completo y siguen el vocabulario de tags. Penaliza fuerte: solo 1/90+ tiene frontmatter. |
| **Retrieval Score** | 60 | Capacidad de una IA para encontrar el documento correcto. INDEX.json existe pero sin frontmatter la mayoría de metadatos están vacíos. Penaliza confiar solo en keywords sobre títulos. |
| **Adoption Readiness** | 70 | ¿Puede una IA llegar, leer AGENTS.md + AI_WORKFLOW.md, y producir código consistente? Sí — el auto-ruteo funciona. Penaliza la falta de frontmatter (la IA no puede filtrar bien). |
| **Maintainability Score** | 75 | ¿Es sostenible agregar/quitar documentos? El formato y la jerarquía son limpios. Penaliza el solapamiento Engineering-OS ↔ dominios (dos fuentes de verdad = doble mantenimiento). |
| **Overall Health** | 67 | Media simple de los scores superiores. Baseline para medir mejora. |

---

## 1. Fortalezas — qué funciona bien

### 1.1 Arquitectura de capas (Nivel 1 → 2 → 3)

**Hallazgo:** la separación en 3 niveles (dominio → patrón → vertical) y 2 capas (regla agnóstica +
implementación de referencia) es el punto más fuerte del handbook. Resuelve el problema real de que
los estándares queden obsoletos cuando cambia el stack.

**Evidencia:** `00_HANDBOOK_FORMAT.md` §2 y §4 — cada regla se escribe en píxeles/porcentajes
(capa 1) y aparte en Tailwind/React (capa 2). Una regla sobrevive aunque el stack pase de Tailwind
a CSS Modules.

**Por qué importa:** la mayoría de los handbooks se escriben en la sintaxis del framework de moda
y mueren con él. Este diseño es intencionalmente framework-agnostic en la capa normativa.

### 1.2 Sistema REQUIRED / RECOMMENDED

**Hallazgo:** el sistema de etiquetas binarias con reglas claras de negociación (`[REQUIRED]` no se
rompe sin confirmación del usuario; `[RECOMMENDED]` se puede desviar con justificación) es exactamente
lo que necesita una IA para saber qué puede negociar y qué no.

**Evidencia:** `00_HANDBOOK_FORMAT.md` §1 + `13_AI_Rules/AI_WORKFLOW.md` §3 (jerarquía de conflicto).
Sin esto, una IA tiende a ser demasiado complaciente o demasiado rígida — los dos extremos.

**Por qué importa:** sin un sistema de etiquetas, toda regla tiene el mismo peso y la IA no tiene
criterio para priorizar. Con REQUIRED/RECOMMENDED, la decisión está codificada en el estándar mismo.

### 1.3 Auto-ruteo para IA (`AGENTS.md` + `AI_WORKFLOW.md`)

**Hallazgo:** el mecanismo de que la IA sepa sola qué documentos leer antes de escribir código — sin
preguntarle rutas al usuario — es un patrón que debería ser estándar en todos los codebases con IA.

**Evidencia:** `AGENTS.md` §"Regla de arranque" + `AI_WORKFLOW.md` §1 (tabla de clasificación
tarea→documentos) + §2 (orden de lectura). El protocolo completo: clasificar → leer en orden →
verificar → implementar.

**Por qué importa:** el error típico de una IA no es romper una regla que leyó, sino no leer el
documento que la contenía. El auto-ruteo convierte ese error en imposible.

### 1.4 Cobertura por dominio

**Hallazgo:** de 15 dominios planeados, 11 tienen contenido sustancial. Frontend solo tiene 27+
documentos Nivel 2 cubriendo desde HTML semántico hasta PWA e i18n. Testing tiene un departamento
de QA completo con 8 agentes modelados.

**Evidencia:** [README.md raíz](../README.md) — tabla de estado por dominio. Frontend ✅ Nivel 1 + Nivel 2 (27 docs),
Backend ✅, API ✅, Database ✅, Security ✅ (con threat model + incident response), Testing ✅
(10 documentos + 8 agentes), DevOps ✅, Cloud ✅, AI Rules ✅, DX ✅, Knowledge System ✅.

**Por qué importa:** para un equipo de 1 persona, tener este nivel de documentación operable por
IA es el multiplicador de fuerza más grande posible.

### 1.5 Agentes de QA modelados

**Hallazgo:** los 8 agentes de QA (Code-Review, E2E, Visual-Regression, Unit-Integration, Security,
Documentation, Quality-Gates, QA-Manager) con roles, ámbitos y handoffs claros es un enfoque muy
maduro.

**Evidencia:** [06_Testing/Agents/README.md](../06_Testing/Agents/README.md) — mapa de consolidación 18→8 roles. Cada agente tiene
objetivo, responsabilidades, checklist y KPIs.

**Por qué importa:** modelar los roles de QA como agentes ejecutables por IA es el puente entre
"tener un estándar" y "que la IA lo verifique automáticamente".

### 1.6 Biblioteca de fallos y lecciones reales

**Hallazgo:** el handbook no es teórico — `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` tiene una
librería de fallos B1-B7 con runbooks, y `28-Knowledge-Base.md` tiene lecciones de producción
reales (Wompi transactionId, variables VITE_* requiriendo redeploy).

**Evidencia:** 28-Knowledge-Base.md — entradas `[lección]` con fecha y fuente. No es teoría, es
experiencia destilada.

**Por qué importa:** una librería de fallos con runbooks vale más que cualquier teoría de deploy.
Demuestra que el handbook nace de experiencia real, no de buenas intenciones.

---

## 2. Áreas de mejora

### 2.1 Solapamiento Engineering-OS ↔ dominios 01-15 (CRÍTICO)

**Hallazgo:** 47 documentos en `Engineering-OS/` se superponen conceptualmente con los dominios
numerados. Por ejemplo:
- `Engineering-OS/16-Security.md` vs `05_Security/SECURITY_ENGINEERING_STANDARD.md`
- `Engineering-OS/19-Git-Standards.md` vs `07_DevOps/GITHUB_STANDARD.md`
- `Engineering-OS/08-Frontend-Standards.md` vs `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md`

**Evidencia:** el propio [README.md raíz](../README.md) lo reconoce: *"Engineering-OS/ (47 docs) y los dominios
numerados 01–15 se solapan en varios temas... riesgo de dos fuentes de verdad divergentes."*

**Impacto:** una IA que consulta ambos puede encontrar reglas contradictorias o versiones distintas
del mismo concepto. La resolución de conflictos (`AI_WORKFLOW.md` §3) no cubre este caso porque
asume que el conflicto es entre niveles del mismo árbol.

**Recomendación:** los dominios numerados como fuente de verdad técnica; Engineering-OS como capa
de índice/visión/proceso. Engineering-OS debe referenciar los dominios, no repetirlos.

### 2.2 Frontmatter YAML faltante (~99% de documentos)

**Hallazgo:** solo `15_Knowledge_System/KNOWLEDGE_SYSTEM_STANDARD.md` tiene frontmatter YAML
completo. ~90 documentos no lo tienen. El INDEX.json está generado, pero sin metadatos
estructurados la mayoría de entradas tienen campos vacíos.

**Evidencia:** [INDEX.json](../INDEX.json) — campo `has_frontmatter: false` en 89/90 entradas. El vocabulario
controlado de tags existe (KNOWLEDGE_SYSTEM_STANDARD.md §02) pero ningún documento lo usa.

**Impacto:** el sistema de retrieval se basa en keywords sobre INDEX.json, pero sin frontmatter
los únicos campos poblados son `title` y `path`. Cualquier búsqueda por tag, categoría o keyword
devuelve resultados vacíos. El sistema de conocimiento es RAG-ready en teoría pero no en práctica.

**Recomendación:** retrofit de frontmatter por lotes (IA básica puede procesar 10-15 docs/sesión).
Priorizar los documentos más consultados: `AI_WORKFLOW.md`, `FRONTEND_ENGINEERING_STANDARD.md`,
`BACKEND_ENGINEERING_STANDARD.md`, `AGENTS.md`.

### 2.3 4 dominios vacíos (09 Architecture, 10 Product, 11 UX/UI, 12 Documentation)

**Hallazgo:** Architecture, Product, UX/UI y Documentation están en README-only. Son dominios
importantes para la completitud del sistema.

**Evidencia:** `09_Architecture/README.md` (74 tokens), `10_Product/README.md` (59 tokens),
`11_UX_UI/README.md` (78 tokens), `12_Documentation/README.md` (61 tokens).

**Impacto:**
- **Architecture (09):** sin mapa de cómo se conectan frontend ↔ Workers ↔ Supabase ↔ R2 ↔
  Cloudflare, no hay visión sistémica. Los documentos individuales asumen que quien lee ya conoce
  las conexiones.
- **Product (10):** para un dev solo, tener estándares de priorización (RICE, ICE) y validación de
  features es crítico para no construir lo que nadie usa.
- **UX/UI (11):** distinto de Frontend (código) — aquí vivirá research, personas, flujos de diseño.
  Sin esto, el diseño es reactivo.
- **Documentation (12):** paradójicamente, el dominio de documentación está vacío en un handbook
  que predica documentación.

**Recomendación:** escribir Architecture primero — es el prerequisito para los demás. Product y
Documentation después. UX/UI puede esperar a que haya investigación real que documentar.

### 2.4 Stack híbrido con legados en migración

**Hallazgo:** Firebase listado como "legacy en salida" y Cloudinary también en migración a R2.
Tener 2 sistemas activos en migración duplica la carga mental y operativa.

**Evidencia:** `Engineering-OS/28-Knowledge-Base.md` — tabla de estado de migración Firebase
(3 proyectos activos-firebase, 1 migrado, 1 híbrido). `README.md` raíz: "Cloudinary en migración fuera".

**Impacto:** cada nuevo proyecto requiere decidir qué sistema usar. Cada bug puede estar en el
sistema nuevo o en el legacy. La migración parcial es más cara que la completa en términos de
decisión por proyecto.

**Recomendación:** documentar una *ventana de migración* con deadline. Mientras tanto, el estándar
de stack canónico debe ser explícito: "todo proyecto nuevo → Supabase + R2; Firebase/Cloudinary
solo para mantenimiento de proyectos existentes".

### 2.5 No hay tests para los standards

**Hallazgo:** los standards definen cómo debe ser el código, pero no hay tests automatizados que
verifiquen que una IA *realmente* los siguió.

**Evidencia:** no existe ningún script, CI job o gate que compare el output de la IA contra las
reglas REQUIRED de los documentos aplicables.

**Impacto:** un estándar sin verificación es una recomendación, no una regla. La diferencia entre
"tener un handbook" y "que el handbook se aplique" es la verificación.

**Recomendación:** diseñar un sistema de *rules-as-tests* — un script que, dado un diff y el
documento aplicable, verifique las reglas REQUIRED más verificables automáticamente (naming,
estructura de carpetas, presencia de tokens, etc.). No necesita cubrir todo — cubrir el 20% de
reglas que generan el 80% de los bugs ya es una mejora enorme.

---

## 3. Recomendaciones accionables

Priorizadas por impacto / esfuerzo. Formato: `[score]` = impacto estimado en Overall Health.

| # | Recomendación | Impacto | Esfuerzo | Score + |
|---|---|---|---|---|
| R1 | **Resolver solapamiento Engineering-OS ↔ dominios**: Engineering-OS referencias los dominios, no los duplica. Un solo commit por archivo de Engineering-OS. | Alto | M (2-3h) | +8 |
| R2 | **Frontmatter batch 1**: agregar frontmatter a los 10 documentos más consultados (AI_WORKFLOW, AGENTS, FRONTEND_ENGINEERING, BACKEND_ENGINEERING, API_ENGINEERING, DATABASE_ENGINEERING, SECURITY_ENGINEERING, CLOUDFLARE_PLATFORM, REACT_STANDARD, LANDING_PATTERNS). | Alto | XS (IA, ~20 min) | +6 |
| R3 | **Frontmatter batch 2**: el resto de documentos con contenido. ~80 docs, pero IA básica puede procesar 10-15/sesión → 5-6 sesiones. | Alto | S (5-6 sesiones de IA) | +5 |
| R4 | **Escribir Architecture (09)**: mapa de conexiones, flujo de datos, responsabilidades de cada pieza del stack. | Alto | M (3-4h) | +7 |
| R5 | **Documentar ventana de migración Firebase/Cloudinary** con deadline y criterios de aceptación. | Medio | XS (30 min) | +3 |
| R6 | **Diseñar sistema rules-as-tests**: MVP que verifique 3-5 reglas REQUIRED verificables automáticamente. | Medio | S (2-3h) | +4 |
| R7 | **Escribir Product (10)**: estándar de priorización y validación de features. | Medio | M (2-3h) | +3 |
| R8 | **Escribir Documentation (12)**: cómo documentar proyectos, READMEs, CLAUDE.md. | Medio | S (1-2h) | +3 |

**Orden recomendado:** R1 → R2 → R4 → R3 → R6 → R5 → R7 → R8
(separar solapamiento primero, después retrieval, después arquitectura, después tests).

---

## 4. Registro de re-evaluación

Se llena al re-ejecutar esta auditoría.

| Fecha | Overall Health | Antes → Después | Cambios desde baseline | Veredicto |
|---|---|---|---|---|
| 2026-07-26 | 67 | — | Baseline inicial | — |
| — | — | — | — | — |

---

## 5. Checklist de la auditoría

- [ ] Leí los documentos clave: `00_HANDBOOK_FORMAT.md`, `README.md`, `AGENTS.md`,
      `AI_WORKFLOW.md`, varios Nivel 1 de dominio, varios Nivel 2 de patrón.
- [ ] Evalué cada score con evidencia verificable (citas a archivos, tokens, conteos).
- [ ] Separé fortalezas de áreas de mejora — sin mezclar cumplidos con críticas.
- [ ] Cada área de mejora tiene: hallazgo + evidencia + impacto + recomendación.
- [ ] Las recomendaciones tienen prioridad (impacto/esfuerzo) y score esperado.
- [ ] Declaré el contexto de esta auditoría (IA externa, no auto-análisis).
- [ ] Datos faltantes declarados como tales, no inventados.
