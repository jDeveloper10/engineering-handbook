---
title: "Estándar de Code Review"
category: 10_Code_Quality
doc_type: estandar
tags: [code review, pr, pull request]
summary: "Reglas de oro de la revisión de código con checklist separado para el autor antes de pedir review y para el revisor, más el código de conducta de los comentarios."
keywords: [code-review, pr, pull-request, code, review, revision, codigo, checklist, separado, autor, pedir, revisor, conducta, comentarios]
updated: 2026-07-27
status: current
---

# 🕵️ Estándar de Code Review

Este documento detalla el checklist y las reglas de oro para las revisiones de código en este repositorio. Una revisión de código efectiva previene bugs, mantiene el estándar y comparte el conocimiento entre el equipo.

## Reglas de Oro

1. **[REQUIRED]** Ningún código llega a `main` sin al menos un *Approve*.
2. **[REQUIRED]** Las PRs deben ser pequeñas y enfocadas (menos de 400 líneas cambiadas idealmente).
3. **[RECOMMENDED]** Revisa la lógica y arquitectura, no el estilo. El estilo se delega a las herramientas de linting (ESLint, Prettier).

## Checklist del Autor (Antes de pedir review)
- [ ] Mi código pasa todos los tests y el linter local (`npm run lint`, `npm run test`).
- [ ] No he dejado `console.log()` innecesarios ni código comentado sin un `TODO`.
- [ ] He documentado con TSDoc las funciones públicas y casos complejos.
- [ ] He revisado mi propio diff (Files changed) antes de solicitar la revisión.

## Checklist del Revisor
- [ ] **Arquitectura:** ¿Sigue los estándares definidos en el handbook? (ej. separación de responsabilidades).
- [ ] **Rendimiento:** ¿Hay bucles ineficientes o renders innecesarios en React?
- [ ] **Seguridad:** ¿Se exponen datos sensibles? ¿Hay validación de inputs?
- [ ] **Testing:** ¿Se han incluido tests para cubrir la nueva lógica?

## Código de Conducta en Reviews
- Haz preguntas en lugar de dar órdenes: *"¿Consideraste usar un Set aquí en lugar de un Array?"* en vez de *"Cambia esto por un Set"*.
- Elogia el buen trabajo. Los comentarios no son solo para criticar.
