# Agentes QA — índice y mapa de consolidación

> Estos "agentes" no son personas ni procesos daemon: son **roles que una IA (Claude Code) asume**
> al ejecutar una tarea de QA. Cada ficha es el prompt/contrato de ese rol. Developer solo:
> la única aprobación humana real es la de Jeilin (baselines visuales, GO/NO-GO final, rotaciones).

Se pidieron 18 agentes. Se consolidaron en **8** porque muchos eran la misma herramienta con
distinta suite, y 18 fichas = burocracia que nadie mantiene. Regla aplicada: **un agente por
herramienta+criterio de decisión, no por tipo de test**.

## Mapa 18 → 8

| # | Agente pedido | Vive en | Por qué |
|---|---------------|---------|---------|
| 1 | QA Manager | [QA-Manager-Agent](QA-Manager-Agent.md) | Único orquestador; decide qué corre y el GO/NO-GO. |
| 2 | Vitest | [Unit-Integration-Agent](Unit-Integration-Agent.md) | Vitest es la herramienta, no un rol aparte. |
| 3 | Unit Test | [Unit-Integration-Agent](Unit-Integration-Agent.md) | Mismo runner (Vitest), misma suite. |
| 4 | Integration Test | [Unit-Integration-Agent](Unit-Integration-Agent.md) | Mismo runner; solo cambia el scope (worker+DB vs función pura). |
| 5 | Playwright | [E2E-Agent](E2E-Agent.md) | Playwright es la herramienta del E2E, no un agente. |
| 6 | E2E | [E2E-Agent](E2E-Agent.md) | El rol base. |
| 7 | Smoke Test | [E2E-Agent](E2E-Agent.md) | Mismo runner, suite reducida (`--grep @smoke`). |
| 8 | Regression | [E2E-Agent](E2E-Agent.md) | Mismo runner, suite completa. "Regresión" es cuándo corres, no qué herramienta usas. |
| 9 | Responsive | [E2E-Agent](E2E-Agent.md) | Mismos tests bajo `projects` con viewports distintos. |
| 10 | Visual Regression | [Visual-Regression-Agent](Visual-Regression-Agent.md) | **Separado a propósito**: su output es visual y aprobar un baseline es decisión humana, no assert. |
| 11 | Accessibility | [Quality-Gates-Agent](Quality-Gates-Agent.md) | axe y Lighthouse corren juntos contra los mismos gates de `../08_QUALITY_STANDARDS.md`. |
| 12 | Performance | [Quality-Gates-Agent](Quality-Gates-Agent.md) | Ídem: un solo veredicto de "cumple budgets o no". |
| 13 | Security Scanner | [Security-Dependency-Agent](Security-Dependency-Agent.md) | Scanner y deps comparten pipeline (audit/gitleaks) y escalan igual a `05_Security`. |
| 14 | Dependency | [Security-Dependency-Agent](Security-Dependency-Agent.md) | Una dep vulnerable ES un hallazgo de seguridad; separarlos duplica el reporte. |
| 15 | Code Review | [Code-Review-Agent](Code-Review-Agent.md) | Rol propio: revisa diffs contra el handbook completo. |
| 16 | Documentation | [Documentation-Agent](Documentation-Agent.md) | Rol propio: docs que cambian junto al código. |
| 17 | Deployment | → **`07_DevOps`** | Desplegar no es QA. QA da el GO/NO-GO; DevOps ejecuta. |
| 18 | Monitoring | → **`07_DevOps`** | Observar producción es DevOps. QA consume sus alertas como trigger de regresión. |

## Flujo de colaboración

```
                       trigger: diff / pre-deploy / cron / alerta de 07_DevOps
                                          │
                                          ▼
                                 QA-Manager-Agent
                       (lee el diff → decide qué agentes corren)
        ┌─────────────┬─────────────┬────┴────────┬──────────────┬─────────────┐
        ▼             ▼             ▼             ▼              ▼             ▼
  Unit-Integration  E2E-Agent  Visual-Regression Quality-Gates Security-Dep  Code-Review
        │             │             │             │              │             │
        └─────────────┴─────────────┴──────┬──────┴──────────────┴─────────────┘
                                           │  reportes en formato fijo (ver cada ficha)
                                           ▼
                            QA-Manager: consolida → GO / NO-GO
                                           │
                     GO ──► 07_DevOps (deploy)        NO-GO ──► fix → re-run parcial
                                           │
                                           ▼
                              Documentation-Agent (post-merge:
                              README de workers, CHANGELOG, docs vs código)
```

Disparos laterales (sin pasar por el Manager):

- **E2E-Agent → Visual-Regression-Agent**: si un test funcional pasa pero el DOM cambió en zonas con snapshot.
- **Security-Dependency-Agent → `05_Security`**: hallazgo real (secreto, CVE explotable) escala fuera de QA.
- **Code-Review-Agent → Documentation-Agent**: si el diff toca código documentado y las docs no cambiaron.
- **Quality-Gates-Agent → E2E-Agent**: si un fix de perf/a11y tocó markup, se re-corre smoke.

## Documentos que estos agentes usan (por nombre exacto)

- `../02_TESTING_PIPELINE.md` — qué suite corre en qué momento (pre-commit / pre-deploy / cron).
- `../08_QUALITY_STANDARDS.md` — gates numéricos (coverage, Lighthouse, axe, budgets).
- `../09_METRICS.md` — métricas que el QA-Manager mantiene.
- `00_HANDBOOK_FORMAT.md` (raíz) — convenciones REQUIRED/RECOMMENDED que el Code-Review cita.

## Convención de las fichas

Toda ficha tiene las mismas secciones: Objetivo · Responsabilidades · Herramientas · Cuándo se
activa · Checklist de ejecución · Errores que detecta · **Qué NO puede detectar** (la sección más
valiosa: evita falsa confianza) · Formato del reporte · KPIs · Prioridad ante conflicto ·
Colaboración. Si una ficha crece más allá de ~120 líneas, se está convirtiendo en documentación
de herramienta — eso va al estándar del dominio, no aquí.
