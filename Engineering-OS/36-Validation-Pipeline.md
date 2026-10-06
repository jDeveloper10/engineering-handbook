---
title: "Engineering OS — Validation Pipeline"
category: engineering-os
doc_type: estandar
tags: [ci, validators, quality-gates, verification]
summary: "Pipeline local y CI que verifica integridad del handbook, registro ejecutable, blueprints y documentación antes de integrar cambios."
keywords: [doctor, check, github-actions, index, lint, verification]
updated: 2026-08-03
status: current
---

# 36 — Validation Pipeline

## OS-PIPE-001 — Gates reproducibles

**[REQUIRED]** El handbook pasa los mismos gates localmente y en CI:

```powershell
npm run lint
npm run validate:os
npm run test:os
npm run docs:build
npm run verify-index
```

`npm run check` los agrupa. `verify-index` no modifica `INDEX.json`; `build-index` es la acción
explícita que se ejecuta al cambiar documentación indexada y cuyo resultado se versiona.

## OS-PIPE-002 — Diagnóstico de proyecto

**[REQUIRED]** Antes de declarar que un repositorio cumple el OS, ejecutar:

```powershell
npm run doctor -- <ruta-del-proyecto>
```

El resultado distingue `PASS`, `MISSING` y `N/A`, muestra perfiles detectados y evidencia de ruta.
Con `--strict`, un requisito de metadata ausente hace fallar el proceso; sin esa opción sirve para
inventario y priorización sin bloquear migraciones legacy.

## OS-PIPE-003 — Evidencia de cierre

La respuesta final nunca sustituye al verificador. Debe citar los comandos ejecutados, sus
resultados, la matriz de blueprint y lo que permanece `NO_VERIFICADO`, `BLOQUEADO` o `DESCONOCIDO`.
