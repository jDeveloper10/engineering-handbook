# 15 — Performance

> Principio 6: primero medir, después optimizar. El rendimiento es un feature (filosofía pública
> de jeilin.castro — el sitio del zapatero no puede ser lento). Las reglas técnicas detalladas
> (Core Web Vitals, optimización de assets, lazy loading, caching) viven en el handbook
> `01_Frontend/FRONTEND_PERFORMANCE_STANDARD.md`. Este archivo define los presupuestos concretos
> del ecosistema y las reglas operativas de medición.
>
> **Ver también:**
> - [`FRONTEND_PERFORMANCE_STANDARD.md`](../01_Frontend/Performance_SEO/FRONTEND_PERFORMANCE_STANDARD.md) — reglas
>   técnicas detalladas (9.132 tokens, 16 secciones)
> - [`FRONTEND_ENGINEERING_STANDARD.md`](../01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md) §11 —
>   performance como criterio de diseño
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Los presupuestos de abajo (LCP <2.5s, INP <200ms, CLS <0.1) son heurísticas
>   operativas del ecosistema de Jeilin — heredan de los objetivos del performance standard
>   pero los ajustan a la realidad de los proyectos actuales. Si el standard se actualiza,
>   estos números se recalibran, no se ignoran.

## Presupuestos (objetivo real: Core Web Vitals verdes en móvil)

| Métrica | Objetivo | Heurística práctica hoy |
|---|---|---|
| LCP | < 2.5s móvil | hero image < 200KB; chunk inicial < 400KB gzip |
| INP | < 200ms | animaciones en transform/opacity (nunca layout) |
| CLS | < 0.1 | dimensiones explícitas en imágenes/embeds |
| Worker p50 | < 100ms | KV/cache antes que fetch externo en el hot path |

- **[REQUIRED]** Medición con Lighthouse (móvil) antes y después de cualquier tarea etiquetada
  "optimización". Sin número previo, la tarea se rechaza.
- **[REQUIRED]** Librerías pesadas (three.js/R3F ~870KB, Remotion, charts) SIEMPRE en `lazy()` +
  chunk separado — caso de referencia: Hero3D de jcdigital. Detectadas en el ecosistema:
  jcdigital (three), ingenusfx (three), Xworked (Remotion) — los tres deben cumplir esta regla.
- **[REQUIRED]** Imágenes: WebP/AVIF para fotografía, dimensiones explícitas, `loading="lazy"`
  fuera del viewport inicial. Los PNG de proyectos (screenshots de portafolio) son candidatos
  permanentes a compresión.
- **[REQUIRED]** Caching en Workers: respuestas de catálogo/productos con `Cache-Control` o cache
  API; el worker no recalcula lo que no cambió (ej.: `/api/products` de worker-pago es cacheable).
- **[RECOMMENDED]** Auditoría trimestral del Performance-Agent sobre los proyectos EN PRODUCCIÓN
  (no sobre los 60 — sobre los ~6 activos), con la skill `web-perf` cuando esté disponible.
