---
title: "Métricas de QA"
category: 06_Testing
doc_type: estandar
tags: [testing, metricas, coverage, web-vitals]
summary: "Las métricas que se miden y las dos reglas que gobiernan su uso: coverage, duración del pipeline, tasa de tests inestables, Web Vitals de producción y tasa de éxito de despliegue."
keywords: [metricas, coverage, pipeline, flaky-rate, web-vitals, deployment-success]
updated: 2026-07-27
status: current
---

# 09 — METRICS

> Las métricas de calidad que le importan a un developer solo, cómo se recolectan **automáticamente** y — lo central — **qué decisión dispara cada una**. Sigue [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Los números concretos son heurísticas atadas a un objetivo (formato §3): se recalibran si el objetivo lo pide, nunca por comodidad.

---

## 0. Las dos reglas que gobiernan este documento

**[REQUIRED] Una métrica que no dispara decisiones se elimina.** Cada métrica de este documento declara su umbral y la acción concreta cuando lo cruza. Si en 2 revisiones consecutivas una métrica no cambió ninguna decisión, sale del documento. **Por qué:** para un dev solo, mirar dashboards es tiempo que no se escribe producto; una métrica decorativa es peor que ninguna porque da sensación de control sin darlo.

**[REQUIRED] Cero dashboards alimentados a mano.** Toda métrica de este documento se recolecta sola (CI, plataforma, Sentry) o se calcula con un comando/script sobre datos que ya existen (runs de Actions, issues, deployments). Si una métrica requiere que alguien anote algo en una hoja, está mal diseñada y se rediseña o se elimina. **Por qué:** los registros manuales de un equipo de una persona duran dos semanas; después miden la disciplina de anotar, no la calidad del software.

**[RECOMMENDED]** Cadencia: las métricas 1–3 son **gates** (se miran solas en cada PR, porque bloquean); las 4–7 se revisan en una pasada mensual de ~15 min, ejecutable por un agente IA con los comandos de cada sección que reporte solo los umbrales cruzados.

---

## 1. Coverage de tests

| | |
|---|---|
| **Objetivo real** | Detectar zonas de lógica importante sin ninguna red — no "alcanzar un número" |
| **Umbral** | El canónico vive en [02_TESTING_PIPELINE.md](../Pipelines/02_TESTING_PIPELINE.md): 80% líneas / 75% branches **sobre los directorios de lógica de negocio** (no global — el global invita a inflar con tests de relleno). Este documento lo monitorea, no lo define |
| **Recolección** | `vitest run --coverage` (provider v8) en cada PR; `coverage.thresholds` en `vitest.config.ts` hace fallar el run por debajo — cero pasos manuales |
| **Decisión que dispara** | Baja del umbral → el PR no mergea: o se testea lo nuevo, o se justifica excluir el archivo (config, generated) en la config de coverage — decisión visible en el diff |

**Por qué 70 y por qué NO subirlo artificialmente:** 70% obliga a cubrir la lógica real sin obligar a testear glue code, barrels y ramas defensivas. Subir el umbral (85, 95, 100) no compra más protección: compra tests de relleno que no pueden fallar por bugs reales pero sí fallan en refactors — coste sin señal (Goodhart, ver [01_QA_STRATEGY.md](01_QA_STRATEGY.md) §5). El umbral solo sube si sube *solo* — si el coverage orgánico vive en 85%, ratchet a 80 para impedir regresión; nunca al revés.

**Implementación:**
```ts
// vitest.config.ts
test: {
  coverage: {
    provider: 'v8',
    // umbral canónico de 02_TESTING_PIPELINE: acotado a lógica de negocio, no global
    thresholds: { 'src/features/**': { lines: 80, branches: 75 } },
    exclude: ['**/*.config.*', '**/types/**', 'src/generated/**'],
  },
},
```

---

## 2. Duración del pipeline de CI

| | |
|---|---|
| **Objetivo real** | Que el loop "push → veredicto" sea tan corto que nunca compense saltárselo, y que un fix de producción no espere en cola |
| **Presupuesto** | **<10 min** total el pipeline de PR; <5 min la parte bloqueante pre-merge si E2E se paraleliza |
| **Recolección** | GitHub Actions lo registra solo. Consulta: `gh run list --workflow ci --limit 20 --json durationMs,conclusion` |
| **Decisión que dispara** | 3 runs seguidos >10 min → ejecutar [10_PLAYBOOK.md](../Guides/10_PLAYBOOK.md) P4 (pipeline lento) antes de añadir un solo test más |

**Por qué 10 minutos:** es el punto donde el comportamiento humano cambia, y con agentes pasa igual: por debajo, esperas el resultado y corriges en caliente; por encima, cambias de contexto, acumulas PRs sin mergear y nace la tentación de "mergeo sin esperar" — que es el principio del fin de los gates. Además es el techo para que el camino de emergencia (fix → pipeline → deploy) quepa dentro del MTTR objetivo (métrica 7).

---

## 3. Flaky rate de E2E

| | |
|---|---|
| **Objetivo real** | Que un fallo de E2E signifique "hay un bug" y no "tira el dado otra vez" — proteger la confianza en la suite |
| **Umbral** | <2% de runs con algún test que pasó en retry (flaky); un mismo spec flaky 2+ veces en una semana → cuarentena inmediata |
| **Recolección** | Playwright con `retries: 1` en CI: todo test que falla y pasa en retry queda marcado `flaky` en el reporte JSON del run — la detección es un subproducto gratis de los retries. Consulta histórica: blob reports de los últimos runs o `gh run list` |
| **Decisión que dispara** | Spec sobre umbral → cuarentena + issue, procedimiento [10_PLAYBOOK.md](../Guides/10_PLAYBOOK.md) P3. La cuarentena tiene deadline: se arregla o se borra — un E2E permanentemente en cuarentena es un E2E que no existe pero cobra mantenimiento |

**Por qué el umbral es tan bajo:** la flakiness es compuesta — con 10 specs al 2% de flakiness cada uno, ~1 de cada 5 pipelines falla en falso; a la tercera falsa alarma, el instinto es re-run sin mirar, y ese día la suite dejó de proteger. El flaky no es una molestia: es el cáncer de la señal.

---

## 4. Web Vitals de producción

| | |
|---|---|
| **Objetivo real** | Que el producto sea usable en los dispositivos reales de los usuarios — lo que Lighthouse en CI (laboratorio) no garantiza |
| **Umbral** | p75 real: LCP <2.5s, INP <200ms, CLS <0.1 (los "good" de Core Web Vitals — verificar valores vigentes en web.dev, Google los recalibra) |
| **Recolección** | RUM sin código propio: Cloudflare Web Analytics (un `<script>` una vez) y/o Sentry Performance ya integrado. Nadie anota nada |
| **Decisión que dispara** | Vital en "poor" p75 sostenido → issue `P2` de performance con la métrica en el título; si coincide con un deploy reciente → tratarlo como regresión del deploy (correlacionar y considerar revert). El gate de laboratorio (Lighthouse CI, [08_QUALITY_STANDARDS.md](08_QUALITY_STANDARDS.md)) además se endurece para atrapar esa clase de regresión antes del deploy |

**Por qué p75 y no promedio:** el promedio esconde exactamente a los usuarios que sufren; p75 es el estándar de la industria (Google/CrUX) para decir "la mayoría de la gente, incluidos los de móvil malo, está bien".

---

## 5. Deployment success rate

| | |
|---|---|
| **Objetivo real** | Confianza para deployar seguido — deploys pequeños y frecuentes son la mitigación #1 de 07_DevOps B1 |
| **Umbral** | ≥95% de deploys a producción terminan verdes (pipeline + smoke post-deploy OK) en el mes |
| **Recolección** | `gh run list --workflow ci --branch main --json conclusion` — el ratio se calcula con un comando; los deploys ya quedan registrados por Actions |
| **Decisión que dispara** | <95% → mirar en qué paso mueren los deploys: si mueren en gates, el problema es calidad pre-push (¿se está corriendo el pipeline local antes de pushear?); si mueren en el paso de deploy/smoke, el problema es DevOps → revisar 07_DevOps §01–03 |

**Por qué importa a un dev solo:** cuando deployar da miedo, se deploya menos y más grande, lo que rompe más, lo que da más miedo — esta métrica detecta la espiral antes de que se instale.

---

## 6. Rollback rate

| | |
|---|---|
| **Objetivo real** | Medir cuántos cambios rotos **atraviesan** todos los gates — es la métrica de calidad de los gates mismos |
| **Umbral** | <5% de los deploys del mes requieren rollback |
| **Recolección** | Cada rollback ya deja rastro sin esfuerzo extra: el post-mortem de una línea de [05_BUG_LIFECYCLE.md](../Guides/05_BUG_LIFECYCLE.md) §5 (obligatorio tras rollback por 07_DevOps §06). Contar issues con esos post-mortems en el mes |
| **Decisión que dispara** | ≥5% → leer los post-mortems del mes juntos y buscar el patrón en el campo "GATE QUE FALTÓ": si 2+ apuntan a la misma clase de hueco (ej. "sin test de integración de X"), el fix no es otro test suelto — es un cambio al estándar (02_TESTING_PIPELINE / 03_CI_CD / 08_QUALITY_STANDARDS) |

**Por qué es la métrica más informativa de la lista:** coverage y pipeline verde miden lo que los gates *ven*; el rollback rate mide lo que los gates *no vieron*. Es el feedback loop del departamento entero.

---

## 7. MTTR (tiempo medio de resolución de P0/P1)

| | |
|---|---|
| **Objetivo real** | Que el camino de emergencia (detectar → mitigar) esté engrasado — para un dev solo el MTTR es personal: es la duración de tu peor noche |
| **Umbral** | P0: mitigado (rollback/flag off) en <1h desde detección; P1: resuelto en <24h |
| **Recolección** | Timestamps que ya existen: creación del issue (detección) → comentario de mitigación o merge del fix. Cálculo: `gh issue list --label P0,P1 --state closed --json createdAt,closedAt` + resta. Cero anotación manual |
| **Decisión que dispara** | P0 >1h → el post-mortem debe responder específicamente *qué paso del camino fue lento* (¿detección tardía → falta alerta de Sentry/healthcheck? ¿mitigación lenta → el rollback no era limpio → violación de 07_DevOps §05-06?) y arreglar **ese paso**, no prometer "estar más atento" |

**Por qué mitigación y no fix para P0:** el reloj de P0 mide sangrado, y el sangrado lo para el rollback o el feature flag en minutos — el fix de raíz puede tardar lo que necesite una vez que producción respira (07_DevOps §06: rollback primero, diagnóstico después).

---

## 8. Métricas deliberadamente EXCLUIDAS

**[RECOMMENDED]** No trackear, aunque el mundo enterprise las venda: **número de tests** (vanity — 3.000 tests malos < 300 buenos), **tests escritos por semana** (mide actividad, no protección), **velocity/story points** (no hay equipo que sincronizar), **bugs cerrados por mes** (incentiva cerrar, no prevenir), **coverage por encima del umbral como "score"** (ver métrica 1). **Por qué dejarlo escrito:** la lista de exclusión evita re-litigar cada métrica de moda; si alguien (humano o IA) propone añadir una métrica, la carga de la prueba es nombrar la decisión que dispararía.

---

## Checklist final

- [ ] ¿Cada métrica activa disparó o pudo disparar una decisión en las últimas 2 revisiones? ¿Las que no, se eliminaron?
- [ ] ¿Ninguna métrica requiere anotación manual para existir?
- [ ] ¿Coverage como gate en vitest.config con el umbral canónico de 02_TESTING_PIPELINE (80/75 sobre lógica de negocio), exclusiones visibles y sin inflación artificial?
- [ ] ¿Pipeline <10 min — y si no, se ejecutó el playbook P4 antes de seguir añadiendo tests?
- [ ] ¿Retries=1 en Playwright CI y specs flaky yendo a cuarentena con deadline (P3 del playbook)?
- [ ] ¿RUM activo (Cloudflare Web Analytics/Sentry) y Vitals p75 en "good"?
- [ ] ¿Deploy success ≥95% y rollback rate <5% — y los post-mortems del mes leídos en conjunto buscando el gate faltante común?
- [ ] ¿MTTR de P0 <1h medido con timestamps de issues, y cada exceso explicado por el paso lento concreto?
- [ ] ¿La revisión mensual cabe en 15 min / la ejecuta un agente con los comandos `gh` de este documento?
