# 06_Testing — Departamento de QA

> Índice del dominio Testing/QA del handbook. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md). Contexto: **developer solo, sin testers ni QA humano** — el departamento de QA es un sistema de herramientas + agentes IA (Claude Code) que ejecutan estos documentos. Ningún procedimiento de esta carpeta puede tener como paso obligatorio "un humano revisa manualmente".

---

## Principio rector

**Nada llega a producción sin pasar los gates automatizados.**

No es un eslogan: es la única forma de que un dev solo tenga QA real. No hay un equipo que pruebe lo que tú no probaste; o lo atrapa una máquina antes del deploy, o lo atrapa un usuario después. Todo lo demás en esta carpeta — la pirámide, los gates, las métricas, los playbooks — existe para hacer ese principio barato de cumplir y caro de violar.

Corolarios:

1. **El pipeline es el departamento de QA.** Hereda de `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` sección 01 el pipeline mínimo (typecheck → tests → build); este dominio lo **extiende** con más gates (lint, coverage, E2E, seguridad, accesibilidad) — nunca lo contradice ni lo duplica.
2. **Un test que no puede fallar no es un test.** Cada test se escribe para atrapar una clase concreta de error; si no se sabe qué error atraparía, no se escribe.
3. **Todo bug arreglado deja un test de regresión** que lo habría atrapado (regla de oro, [05_BUG_LIFECYCLE.md](Guides/05_BUG_LIFECYCLE.md)).
4. **Métrica que no dispara decisiones, se elimina** ([09_METRICS.md](Strategy/09_METRICS.md)).

---

## Mapa del departamento

El número es el identificador estable de cada documento. Los documentos 02, 03, 04, 06, 07, 08 y la carpeta `Agents/` los mantienen sus propios dueños — este README solo los mapea.

| # | Documento | Qué define |
|---|---|---|
| — | `README.md` (este) | Índice, principio rector, qué leer para qué |
| 01 | [01_QA_STRATEGY.md](Strategy/01_QA_STRATEGY.md) | **La estrategia**: pirámide de tests adaptada a dev solo, qué se automatiza vs riesgo residual, matriz de herramientas elegidas y descartadas, cuándo escribir cada tipo de test, qué NO testear |
| 02 | [02_TESTING_PIPELINE.md](Pipelines/02_TESTING_PIPELINE.md) | **Cómo se escribe cada tipo de test** (unit, integration, component, E2E, visual) en el stack actual: Vitest, Testing Library, Playwright, Workers, Supabase |
| 03 | [03_CI_CD.md](Pipelines/03_CI_CD.md) | **El pipeline de QA por etapas** en GitHub Actions: qué corre en cada push/PR/merge y cómo |
| 04 | [04_RELEASE_PROCESS.md](Guides/04_RELEASE_PROCESS.md) | **Releases para un dev solo**: versionado, proceso de release sobre el deploy de 07_DevOps |
| 05 | [05_BUG_LIFECYCLE.md](Guides/05_BUG_LIFECYCLE.md) | **Ciclo de vida del bug**: captura, registro, severidades P0–P3 con criterios objetivos, triage, regla de oro del test de regresión, post-mortem de una línea |
| 06 | [06_TEST_CHECKLIST.md](Strategy/06_TEST_CHECKLIST.md) | **Checklists operativos por momento** (commit → push → merge → release → deploy → post-deploy): qué corre cuándo y con qué comando |
| 07 | [07_AUTOMATION_GUIDE.md](Guides/07_AUTOMATION_GUIDE.md) | **Setup QA copy-paste**: dotar a un proyecto nuevo del sistema QA completo en <1 hora |
| 08 | [08_QUALITY_STANDARDS.md](Strategy/08_QUALITY_STANDARDS.md) | **Quality gates del build**: los umbrales y verificaciones que bloquean (lint, coverage, seguridad, a11y, performance) |
| 09 | [09_METRICS.md](Strategy/09_METRICS.md) | **Métricas**: las 7 que importan a un dev solo, cómo se recolectan solas, y qué decisión dispara cada una |
| 10 | [10_PLAYBOOK.md](Guides/10_PLAYBOOK.md) | **Procedimientos operativos**: proyecto nuevo, bug en producción, test flaky, pipeline lento, saltarse un gate, proyecto heredado sin tests |
| — | [Agents/](Agents/README.md) | Instrucciones para que agentes IA (Claude Code) ejecuten este departamento: QA-Manager, Unit-Integration, E2E, Quality-Gates, Visual-Regression, Code-Review, Security-Dependency, Documentation |

---

## Qué leer para qué

| Situación | Ir a |
|---|---|
| "¿Qué tests escribo para esta feature?" | [01_QA_STRATEGY.md](Strategy/01_QA_STRATEGY.md) sección 4 |
| "¿Qué herramienta uso / por qué esta y no otra?" | [01_QA_STRATEGY.md](Strategy/01_QA_STRATEGY.md) sección 3 |
| "Voy a escribir un test (unit/integración/component/E2E)" | [02_TESTING_PIPELINE.md](Pipelines/02_TESTING_PIPELINE.md) |
| "¿Qué corre en CI, en qué orden, y qué bloquea el merge?" | [03_CI_CD.md](Pipelines/03_CI_CD.md) + [08_QUALITY_STANDARDS.md](Strategy/08_QUALITY_STANDARDS.md) + `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` §01 |
| "Voy a sacar un release" | [04_RELEASE_PROCESS.md](Guides/04_RELEASE_PROCESS.md) |
| "Encontré/me reportaron un bug" | [05_BUG_LIFECYCLE.md](Guides/05_BUG_LIFECYCLE.md); si es en producción, primero [10_PLAYBOOK.md](Guides/10_PLAYBOOK.md) P2 |
| "¿Esto es P0 o puede esperar?" | [05_BUG_LIFECYCLE.md](Guides/05_BUG_LIFECYCLE.md) sección 3 |
| "¿Qué comandos corro antes de commit/push/merge/deploy?" | [06_TEST_CHECKLIST.md](Strategy/06_TEST_CHECKLIST.md) |
| "Quiero montar el QA de un proyecto en <1 hora" | [07_AUTOMATION_GUIDE.md](Guides/07_AUTOMATION_GUIDE.md) + [10_PLAYBOOK.md](Guides/10_PLAYBOOK.md) P1 |
| "¿Cuál es el umbral exacto de cada gate?" | [08_QUALITY_STANDARDS.md](Strategy/08_QUALITY_STANDARDS.md) |
| "¿Vamos bien? ¿Qué número miro?" | [09_METRICS.md](Strategy/09_METRICS.md) |
| "Empiezo proyecto nuevo / heredé uno sin tests / flaky / pipeline lento / emergencia" | [10_PLAYBOOK.md](Guides/10_PLAYBOOK.md) |
| "Voy a configurar un agente IA para QA" | [Agents/](Agents/README.md) |

---

## Relación con otros dominios

- **`07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`** — el dueño del pipeline, del deploy y del rollback. Este dominio agrega los gates que corren *dentro* de ese pipeline y define qué test faltó cuando un rollback ocurre. Los runbooks de incidentes viven allá (Parte B); el ciclo del *bug* vive acá.
- **`07_DevOps/GITHUB_STANDARD.md`** — seguridad de workflows, branch protection; los gates de 04 se implementan bajo esas reglas.
- **`05_Security/`** — el modelo de amenazas y la respuesta a incidentes de seguridad; esta carpeta solo cubre los scanners automatizados (gates en [08_QUALITY_STANDARDS.md](Strategy/08_QUALITY_STANDARDS.md), setup en [07_AUTOMATION_GUIDE.md](Guides/07_AUTOMATION_GUIDE.md)).
- **`02_Backend/worker-template/`** — el template de worker debe nacer cumpliendo esta carpeta (tests incluidos).
- **`Engineering-OS/17-Testing.md`** — resumen operativo; esta carpeta es la versión completa y canónica.

## Estado

Los 10 documentos + `Agents/` existen (2026-07-20). Ante cualquier conflicto entre documentos de esta carpeta: la **estrategia** (01) manda sobre la implementación (02–08); el **pipeline base** de `07_DevOps` manda sobre todos en lo que respecta a deploy y rollback.
