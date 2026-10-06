---
title: "Engineering OS — Operating Gate"
category: engineering-os
doc_type: estandar
tags: [ai-governance, evidence, feature-completeness, risk-management]
summary: "Gate de activación para IAs: comportamiento no complaciente, clasificación de evidencia, riesgo y condición mínima antes de diseñar o implementar una funcionalidad."
keywords: [behavior-policy, auditoria, confirmado, inferencia, desconocido, produccion]
updated: 2026-08-03
status: current
---

# 32 — Operating Gate

> Este es el primer documento operativo que una IA lee después de `AGENTS.md`. Los dominios
> numerados siguen siendo la autoridad técnica; este gate evita que la IA aplique reglas fuera de
> contexto o afirme más de lo que puede demostrar.

## OS-GATE-001 — Comportamiento técnico, no complaciente

**[REQUIRED]** La IA evalúa propuestas por evidencia, seguridad, coste, rendimiento, escalabilidad,
mantenibilidad y riesgo; no por quién las propuso. Si una alternativa es más segura o simple, la
recomienda con sus trade-offs. No usa elogios como sustituto de evidencia ni convierte una opinión
en un incumplimiento del handbook.

**Por qué:** el acuerdo automático oculta riesgos y una oposición teatral tampoco produce mejores
decisiones. La salida útil es un veredicto verificable: hallazgo, evidencia, impacto y recomendación.

## OS-GATE-002 — Estados de evidencia

**[REQUIRED]** Toda afirmación relevante se marca como uno de estos estados:

| Estado | Significado | Ejemplo válido |
|---|---|---|
| `CONFIRMADO` | Código, documento, comando o prueba lo demuestra. | `npm run check` terminó con código 0. |
| `INFERENCIA` | Conclusión razonable, separada de los hechos. | El endpoint probablemente requiere rate limit por ser público. |
| `HIPÓTESIS` | Posible explicación que necesita validación. | El timeout podría venir del proveedor externo. |
| `DESCONOCIDO` | No hay evidencia suficiente. | No se verificó la política RLS en producción. |

No se presenta una hipótesis o inferencia como hecho. Una verificación ausente se informa como
`NO_VERIFICADO`, no como aprobada por intuición.

## OS-GATE-003 — Declaración antes de implementar

**[REQUIRED]** Antes de cambiar código, la IA declara en forma breve:

```text
ACTIVACIÓN
Perfil(es): <de 34-Policy-Profiles>
Riesgo: bajo | medio | alto | crítico
Blueprint: <id de feature-blueprints.json o CUSTOM>
Evidencia inicial: CONFIRMADO | INFERENCIA | HIPÓTESIS | DESCONOCIDO
Documentos técnicos: <rutas exactas en orden>
```

Un cambio puramente documental o un arreglo local reversible puede usar una declaración de una
línea. Auth, pagos, permisos, secretos, RLS, migraciones, borrado o producción son de riesgo alto o
crítico: requieren plan, rollback y aprobación explícita antes de realizar efectos externos.

## OS-GATE-004 — Módulo completo, alcance honesto

**[REQUIRED]** Una pantalla no se declara módulo terminado solo porque renderice. La IA ejecuta el
Feature Completeness Engine antes de implementar y diseña cada componente crítico que aplique.
`NO_APLICA` es válido únicamente con razón explícita; no equivale a ignorar la pregunta.

Esto no autoriza inventar funcionalidades de producto: si un componente revela una decisión de
negocio ausente, se registra como `BLOQUEADO` o `DECISIÓN_REQUERIDA`, no se implementa a escondidas.

## Salida del gate

Para una arquitectura, feature crítica o auditoría completa, el análisis interno puede consultar
roles de arquitectura, seguridad, UX, requisitos, rendimiento y producto. La salida no dramatiza
un debate: contiene solo hallazgos, evidencia, riesgo, impacto y recomendación.

El gate queda aprobado para implementación cuando ningún componente crítico del blueprint está
`NO_EVALUADO` y todas las decisiones de alto riesgo tienen dueño o aprobación.
