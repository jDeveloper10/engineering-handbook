---
title: "Engineering OS — Feature Completeness Engine"
category: engineering-os
doc_type: estandar
tags: [feature-blueprints, requirements, quality-gates, production-ready]
summary: "Motor que transforma una solicitud de funcionalidad en una matriz verificable de componentes, decisiones y evidencias antes de implementar."
keywords: [login, crud, payments, definition-of-done, blueprint, matriz-completitud]
updated: 2026-08-03
status: current
---

# 33 — Feature Completeness Engine

## OS-FCE-001 — Plan antes de código

**[REQUIRED]** Toda funcionalidad usa un blueprint de `feature-blueprints.json` o declara uno
`CUSTOM` antes de implementación. Ejecutar:

```powershell
npm run blueprint -- authentication
```

La herramienta genera una matriz con estos estados permitidos: `EXISTE`, `DISEÑADO`, `NO_APLICA`,
`BLOQUEADO`, `DECISIÓN_REQUERIDA` y `NO_EVALUADO`.

**Por qué:** una lista de temas no garantiza que se evaluaron. La matriz obliga a asignar estado,
evidencia y responsable a cada componente que normalmente se olvida.

## OS-FCE-002 — Condición de inicio

**[REQUIRED]** No comienza la implementación si un componente `critical` del blueprint está
`NO_EVALUADO`. Para continuar, debe estar diseñado, ya existir, ser no aplicable con justificación,
o estar bloqueado por una decisión que el usuario debe tomar.

Un bloqueo no se resuelve inventando alcance. Ejemplo: el blueprint de autenticación exige decidir
el proveedor y el ciclo de sesión; no obliga a agregar SSO si el producto no lo pide.

## Baseline de producción

Cada feature nueva debe evaluar, como mínimo, requisitos funcionales y no funcionales, casos de uso
y borde, seguridad, UX/UI, accesibilidad, validación cliente/servidor, lógica de negocio,
arquitectura, datos, API, permisos, auditoría, logging, errores, estados asíncronos, rendimiento,
escalabilidad, pruebas y documentación. Un blueprint especial agrega requisitos del dominio.

## Blueprints incluidos

| ID | Para qué se usa | Componentes críticos añadidos |
|---|---|---|
| `production-feature` | Cualquier feature | Baseline completo y decisiones explícitas. |
| `authentication` | Login, registro, recuperación | identidad, sesión, recuperación, antiabuso, eventos de seguridad. |
| `admin-crud` | Gestión administrativa de entidades | autorización, auditoría, borrado/restauración, exportación y límites. |
| `payments` | Cobros, suscripciones, reembolsos | precio en servidor, idempotencia, webhook firmado y conciliación. |

Los artefactos están en [`feature-blueprints.json`](feature-blueprints.json). El JSON es la fuente
ejecutable; esta página explica su uso y no duplica sus componentes.

## Cierre de la funcionalidad

La matriz se adjunta al reporte final junto con los validadores ejecutados. Compilar no es prueba de
completitud: un componente sin verificador queda `NO_VERIFICADO` y no puede presentarse como listo.
