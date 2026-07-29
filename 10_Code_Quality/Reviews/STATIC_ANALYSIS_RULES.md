---
title: "Reglas de Análisis Estático (Linter)"
category: 10_Code_Quality
tags: [eslint, prettier, static analysis]
status: current
---

# 🤖 Reglas de Análisis Estático

Este documento lista la base conceptual detrás de nuestra configuración de ESLint, Prettier y TypeScript. Las herramientas de análisis estático automatizan el code review para que los humanos se enfoquen en la arquitectura.

## 1. Reglas Core (ESLint)

- **`no-console`**: (Warning) Solo se permiten `console.info` o `console.error`. Los `console.log` sueltos deben eliminarse antes de hacer commit.
- **`react-hooks/exhaustive-deps`**: (Error) **JAMÁS** silenciar esta regla (`// eslint-disable-next-line`). Si hay dependencias que causan ciclos infinitos, el problema es de arquitectura del efecto, no del linter.
- **`@typescript-eslint/no-explicit-any`**: (Error) El uso de `any` está prohibido. Si desconoces un tipo, usa `unknown` y valida en tiempo de ejecución.
- **`@typescript-eslint/explicit-function-return-type`**: (Recomendado) Para funciones exportadas, mejora la predictibilidad.

## 2. Formateo (Prettier)

Prettier es la fuente de verdad única para el estilo del código. No debatimos en PRs si se usan comillas simples o dobles, ni dónde va el corchete.
- El formateo se ejecuta automáticamente en pre-commit usando `husky` + `lint-staged`.

## 3. TypeScript Estricto

En `tsconfig.json`, las siguientes opciones son **obligatorias**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true
  }
}
```

> **Nota:** Si estás migrando un proyecto heredado (Engineering-OS base), puedes habilitar estas reglas de forma paulatina para no romper el build instantáneamente.
