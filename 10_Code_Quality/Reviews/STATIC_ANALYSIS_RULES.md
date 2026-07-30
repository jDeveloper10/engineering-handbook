---
title: "Reglas de Análisis Estático (Linter)"
category: 10_Code_Quality
doc_type: estandar
tags: [eslint, prettier, static analysis]
summary: "Base conceptual de la configuración de análisis estático: reglas core de ESLint, formateo con Prettier y la configuración estricta de TypeScript."
keywords: [eslint, prettier, static-analysis, analisis, estatico, linter, base, conceptual, configuracion, core, formateo, estricta, typescript]
updated: 2026-07-27
status: current
---

# Reglas de Análisis Estático

Este documento lista la base conceptual detrás de nuestra configuración de ESLint, Prettier y TypeScript. Las herramientas de análisis estático automatizan el code review para que los humanos se enfoquen en la arquitectura.

## 1. Reglas Core (ESLint)

- **[RECOMMENDED]** `no-console`: Solo se permiten `console.info` o `console.error`. Los `console.log` sueltos deben eliminarse antes de hacer commit.
  **Por qué:** un `console.log` de depuración olvidado no rompe nada, así que ninguna herramienta lo bloquea — pero se acumulan y terminan filtrando datos internos a la consola del navegador de producción. Advertencia, no error, porque durante el desarrollo activo estorbar cada `console.log` frena más de lo que ayuda.
- **[REQUIRED]** `react-hooks/exhaustive-deps`: **JAMÁS** silenciar esta regla (`// eslint-disable-next-line`). Si hay dependencias que causan ciclos infinitos, el problema es de arquitectura del efecto, no del linter.
  **Por qué:** esta regla existe porque un efecto con dependencias incompletas lee valores obsoletos (*stale closures*) de forma silenciosa — no falla, simplemente usa datos viejos, y ese bug no se manifiesta en desarrollo con datos pequeños. Silenciarla no arregla el ciclo infinito, solo esconde la señal que apuntaba a la causa real.
- **[REQUIRED]** `@typescript-eslint/no-explicit-any`: El uso de `any` está prohibido. Si desconoces un tipo, usa `unknown` y valida en tiempo de ejecución.
  **Por qué:** `any` desactiva el chequeo de tipos en todo lo que toca, así que un error de forma de datos que TypeScript debería atrapar en compilación llega intacto a producción. `unknown` obliga a validar antes de usar, que es la garantía que `any` finge dar sin darla (ver `FE-001`).
- **[RECOMMENDED]** `@typescript-eslint/explicit-function-return-type`: Para funciones exportadas, mejora la predictibilidad.
  **Por qué:** un tipo de retorno explícito documenta el contrato de la función y evita que un cambio interno altere silenciosamente lo que devuelve. Es recomendado porque en funciones internas cortas la inferencia de TypeScript ya es exacta, y forzar la anotación ahí es ruido sin ganancia.

## 2. Formateo (Prettier)

**[REQUIRED]** Prettier es la fuente de verdad única para el estilo del código. No debatimos en PRs si se usan comillas simples o dobles, ni dónde va el corchete.

**Por qué:** el estilo de formato no tiene una respuesta correcta objetiva, así que discutirlo en cada PR es tiempo de revisión gastado en algo que una herramienta resuelve en milisegundos. Automatizarlo elimina la discusión de raíz en vez de intentar ganarla cada vez.
- El formateo se ejecuta automáticamente en pre-commit usando `husky` + `lint-staged`.

## 3. TypeScript Estricto

**[REQUIRED]** En `tsconfig.json`, las siguientes opciones son **obligatorias**:

**Por qué:** cada una de estas banderas cierra un agujero conocido del chequeo de tipos por defecto — `strict` activa el conjunto completo, `noImplicitAny` impide que un tipo no anotado se convierta en `any` sin que nadie lo pidiera, `strictNullChecks` obliga a manejar `null`/`undefined` en vez de asumir que un valor siempre existe, y `noUnusedLocals` atrapa variables muertas que suelen delatar lógica a medio borrar.
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
