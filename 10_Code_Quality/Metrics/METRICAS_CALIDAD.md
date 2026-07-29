---
title: "Métricas de Calidad de Código"
category: 10_Code_Quality
doc_type: estandar
tags: [metrics, coverage, complexity]
summary: "Límites objetivos para medir deuda técnica y saber cuándo detener el desarrollo: complejidad ciclomática, cobertura de tests, tamaño del bundle y profundidad de componentes."
keywords: [metrics, coverage, complexity, metricas, calidad, codigo, limites, objetivos, medir, deuda, tecnica, saber, detener, desarrollo]
updated: 2026-07-27
status: current
---

# 📊 Métricas de Calidad de Código

Este estándar define los límites y métricas objetivas que usamos para medir la deuda técnica y saber cuándo es necesario detener el desarrollo de nuevas features para refactorizar.

## 1. Complejidad Ciclomática
Mide cuántos caminos lógicos (ifs, loops, switches) existen en una sola función.
- **[Límite Máximo]**: 15 por función.
- **[Solución]**: Extraer lógica de if/else a funciones más pequeñas, o usar un mapeo por objeto (diccionario) en lugar de switches largos (ver *Recetas de Refactoring*).

## 2. Cobertura de Tests (Test Coverage)
- **Componentes Core / UI Reutilizable**: 80% mínimo.
- **Lógica de Negocio / Workers**: 90% mínimo (escrutinio estricto porque no hay UI).
- **[Aclaración]**: No persigas el 100% escribiendo tests inútiles. Enfócate en los *edge cases* lógicos y paths críticos del negocio.

## 3. Tamaño del Bundle (Frontend)
- El JavaScript inicial (first load) enviado al cliente debe mantenerse **por debajo de 200kb gzipped**.
- Si un paquete pesado (ej. Lottie, librerías de gráficos 3D, PDF) se necesita en una sola pantalla, **[REQUIRED]** usar *Dynamic Imports* (`React.lazy`) para hacer split-code.

## 4. Profundidad de Componentes
- Si un árbol de componentes React requiere más de 5 niveles de anidación profundos, es candidato para una refactorización con Context API o Composición de Componentes (pasar `<children>`).
