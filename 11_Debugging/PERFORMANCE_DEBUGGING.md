---
title: "Performance Debugging"
category: 11_Debugging
tags: [performance, profiling, react, bundle]
status: current
---

# ⚡ Performance Debugging

Guía para diagnosticar aplicaciones lentas, ya sea en el renderizado (UI jank) o en el tiempo de carga (Load time).

## 1. Aplicación lenta al cargar (Load Time)

Si el First Contentful Paint (FCP) o Time to Interactive (TTI) es malo:

1. **Analizar el Bundle**: 
   - Genera el reporte de tamaño del bundle de Vite: `npm run build -- --profile` o usando plugins como `rollup-plugin-visualizer`.
   - Busca dependencias pesadas inesperadas (ej. importar todo `lodash` en lugar de `lodash/debounce`, o importar `moment` en lugar de `date-fns`).
   - Usa *Dynamic Imports* (`import()`) para componentes pesados que no se ven en la carga inicial (modales, dashboards complejos, gráficas).

2. **Network Tab (Waterfall)**:
   - Identifica peticiones secuenciales. Si el Componente A pide datos, termina, y luego renderiza Componente B que pide *más* datos, tienes un cuello de botella.
   - **Solución**: Hacer los fetches en paralelo en el componente padre con `Promise.all()`.

## 2. Aplicación lenta al interactuar (Render Jank)

Si al escribir en un input la pantalla se congela o hay lag:

1. **React Profiler**:
   - Abre React DevTools -> Profiler.
   - Graba la interacción (escribir en el input).
   - Revisa el panel "Flamegraph". Identifica qué componentes tomaron mucho tiempo y por qué renderizaron.
   - Si el motivo es *"Hook changed"* y no debía, revisa las dependencias de tus `useMemo`/`useCallback`.
   - Si el motivo es *"Props changed"*, pero lógicamente son las mismas, React asume que los objetos/arrays nuevos son props nuevas por referencia de memoria.

2. **Evitar Optimizaciones Prematuras**:
   - No envuelvas todo en `React.memo` a ciegas. `memo` tiene un costo de evaluación. Úsalo solo para listas largas o componentes realmente pesados de renderizar.
