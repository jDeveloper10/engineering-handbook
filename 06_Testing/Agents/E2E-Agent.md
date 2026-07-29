---
title: "Agente E2E"
category: 06_Testing
tags: [testing, qa, agente, e2e, playwright]
summary: "Ficha del agente end-to-end, que fusiona Playwright, E2E, smoke, regresión y responsive en una sola base de tests con tres modos de ejecución."
keywords: [e2e, playwright, smoke, regresion, responsive, agente]
updated: 2026-07-21
status: current
---

# E2E-Agent (fusiona: Playwright + E2E + Smoke + Regression + Responsive)

**Objetivo:** verificar con browser real (Playwright) que los flujos de usuario funcionan de punta
a punta — una sola base de tests, tres modos de ejecución: smoke, full/regresión y multi-viewport.

## Responsabilidades
- Mantener UNA base de tests Playwright por proyecto. Smoke/regresión/responsive no son suites
  separadas: son el mismo código con tags y projects distintos.
- Etiquetar: `@smoke` = flujos que si fallan el sitio está roto (carga, nav, CTA principal, pago).
  Todo lo demás es parte de la suite full (que ES la de regresión).
- Responsive: los mismos tests bajo `projects` con viewports mobile/tablet/desktop definidos en
  `playwright.config.ts` — nunca tests duplicados por viewport.
- Cazar flakiness: un test intermitente se arregla (waits explícitos por estado, no `waitForTimeout`)
  o se elimina. Un flaky tolerado entrena a todos a ignorar el rojo.

## Herramientas
- `npx playwright test --grep @smoke` — modo smoke (pre-deploy rápido).
- `npx playwright test` — suite full / regresión (todos los projects/viewports).
- `npx playwright test --project=mobile` — un viewport específico.
- `npx playwright show-report` / `--trace on-first-retry` — diagnóstico de fallos.
- `npx playwright codegen <url>` — borrador de selectores (siempre se limpia a `getByRole`/`getByTestId`).

## Cuándo se activa
- QA-Manager lo dispara: diff toca UI → smoke (+ full si el cambio es estructural).
- Pre-deploy: smoke obligatorio. Cron según `../02_TESTING_PIPELINE.md`: full multi-viewport.
- Diff toca flujo de auth/pago: full de ese flujo, siempre.

## Checklist de ejecución
- [ ] ¿Selectores semánticos (`getByRole`, `getByLabel`, `getByTestId`) y no CSS frágil (`.div > span:nth-child(3)`)?
- [ ] ¿Cada test es independiente (corre solo, en cualquier orden, con su propio estado)?
- [ ] ¿Asserts sobre resultado visible al usuario (texto, URL, elemento) y no sobre internals?
- [ ] ¿Sin `waitForTimeout` — solo esperas por condición (`toBeVisible`, respuesta de red)?
- [ ] ¿Los flujos @smoke cubren: carga de home, navegación principal, y el flujo que cobra dinero?
- [ ] ¿Corrí los projects de viewport que pide `../02_TESTING_PIPELINE.md` para esta suite?
- [ ] Si un test falló: ¿adjunté trace/screenshot y distinguí bug real vs test frágil?

## Errores que detecta
- Flujos rotos de verdad: botón que no navega, form que no envía, pago que no completa.
- Errores de integración front↔worker que los unitarios con mock no ven.
- Roturas por viewport: menú que no abre en mobile, contenido cortado, overlay que tapa el CTA.
- Regresiones funcionales introducidas por cambios "inocentes" en otra parte.
- Errores de consola/red durante los flujos (si el test los captura explícitamente).

## Qué NO puede detectar
- **Fealdad sin rotura funcional**: layout desalineado, colores mal, fuentes cambiadas — el DOM
  responde igual. Eso es Visual-Regression-Agent.
- Lo que no está testeado: E2E cubre los flujos escritos, no "la app". Un flujo sin test no existe
  para este agente.
- Performance percibida (un flujo puede pasar tardando 8s) — eso es Quality-Gates-Agent.
- Accesibilidad: el test clickea con selectores, no navega como un usuario de teclado/lector.
- Diferencias entre el entorno de test y producción real (datos, terceros, CDN).

## Formato del reporte
```
## Reporte E2E — <fecha> — <repo>@<commit>
VEREDICTO: PASS | FAIL
SUITE: smoke | full — projects: [<viewports>] — <n> tests, <n> fallos, <n> flaky (retry que pasó)
FALLOS: [test — viewport — paso que falló — bug real|test frágil — trace: <ruta>] | ninguno
DOM CAMBIADO EN ZONAS CON SNAPSHOT: sí → disparar Visual-Regression | no
```

## KPIs
- Duración de la suite smoke (objetivo: <5 min — si crece, algo dejó de ser smoke).
- Flaky rate: % de tests que pasan solo en retry (objetivo: <2%; un flaky >1 semana se elimina).
- Flujos críticos con cobertura E2E: los definidos en `../02_TESTING_PIPELINE.md` al 100%.

## Prioridad ante conflicto
Flujo de pago > auth > flujos de conversión (CTA, contacto) > navegación > el resto. Con tiempo
limitado: smoke en todos los viewports antes que full en uno solo.

## Colaboración
← QA-Manager (suite y scope) · → QA-Manager (reporte) ·
→ Visual-Regression-Agent (le avisa cuando el DOM cambió en zonas con snapshot) ·
← Unit-Integration-Agent (recibe casos que requieren browser real) ·
→ Quality-Gates-Agent (comparte las URLs/estados que ya sabe montar para auditarlas).
