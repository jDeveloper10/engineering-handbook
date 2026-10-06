---
title: "Engineering OS — Rule Registry"
category: engineering-os
doc_type: referencia
tags: [policy-as-code, rules, validators, traceability]
summary: "Registro legible por máquina de reglas críticas, perfiles, severidad, fuente y mecanismo de verificación."
keywords: [registry, validation, enforcement, exceptions, rule-id]
updated: 2026-08-03
status: current
---

# 35 — Rule Registry

El registro [`rule-registry.json`](rule-registry.json) convierte IDs de regla en datos verificables.
Cada entrada declara fuente, perfiles, severidad y mecanismo de cumplimiento. No reemplaza el texto
normativo: enlaza la política ejecutable con su autoridad humana.

## OS-REG-001 — Una regla, una fuente y un verificador honesto

**[REQUIRED]** Ninguna regla crítica se anuncia como automatizada sin indicar exactamente qué
validador y qué superficie cubre. `lint-handbook`, por ejemplo, valida bloques de ejemplo Markdown;
no prueba el código de todos los proyectos.

## OS-REG-002 — Registry válido en CI

**[REQUIRED]** `npm run validate:os` comprueba IDs únicos, referencias a documentos existentes,
perfiles y blueprints consistentes, además de que las reglas críticas globales de `AGENTS.md` estén
registradas. Un documento puede explicar una regla; el registry es la fuente para automatización.

## Modelo de enforcement

| Modo | Significado |
|---|---|
| `automated-handbook-example` | Un linter cubre ejemplos del handbook, no repos externos. |
| `automated-project-metadata` | Doctor comprueba estructura y manifiestos sin alterar el proyecto. |
| `test-or-review` | Requiere prueba, inspección contextual o ambos. |

Un estado `test-or-review` es deliberado: fingir una regex para verificar autorización o RLS sería
peor que declarar el límite del validador.
