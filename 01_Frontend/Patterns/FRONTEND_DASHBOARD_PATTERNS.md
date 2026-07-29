---
title: "Patrones de Dashboard"
category: 01_Frontend
doc_type: patron
tags: [frontend, dashboard, kpi, patrones]
summary: "Composición de un dashboard: tiles de KPI, gráficos, filtros de rango de fecha, densidad de información y cómo comunicar la frescura de los datos."
keywords: [dashboard, kpi, graficos, filtros, densidad, frescura]
updated: 2026-07-27
status: current
---

# FRONTEND DASHBOARD PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y de [FRONTEND_UI_PATTERNS.md](FRONTEND_UI_PATTERNS.md) sección 3.2. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Material Design, Atlassian Design System e IBM Carbon (fuentes de referencia para dashboards densos) — ver memoria de fuentes UX del handbook.

---

## 1. Regla principal

**[REQUIRED]** Un dashboard se estructura en capas de densidad creciente, de arriba hacia abajo: **KPIs (resumen) → gráficos (tendencia) → tabla (detalle)**. Nunca se reemplaza esta jerarquía por una grilla de cards de texto (ver `FRONTEND_UI_PATTERNS.md` sección 2).

```
Header: título + rango de fecha + filtros
──────────────────────────────
KPI  KPI  KPI  KPI
──────────────────────────────
Gráfico(s) de tendencia
──────────────────────────────
Tabla de detalle (paginada, ordenable)
```

---

## 2. KPI tiles

**[REQUIRED]** Cada KPI muestra: valor grande, label descriptivo, y **delta/tendencia respecto al periodo anterior** (ej. "+12% vs mes pasado"), no solo el número aislado.

**Por qué:** un número sin contexto de comparación no dice si es bueno o malo — "1,204 usuarios" no informa nada por sí solo; "1,204 usuarios (+8% vs semana pasada)" sí.

**[RECOMMENDED]** color semántico en el delta (`success` para positivo, `danger` para negativo) — pero validado contra el significado real: una caída en "tickets de soporte abiertos" es positiva, no negativa. El color no se asigna mecánicamente por signo matemático.

---

## 3. Gráficos

**[RECOMMENDED]** Tipo de gráfico según el dato, no por preferencia visual:

| Dato | Gráfico |
|---|---|
| Tendencia en el tiempo | Línea o área |
| Comparación entre categorías | Barras |
| Composición de un total (máx. 5-6 segmentos) | Dona/pie |
| Composición con más de 6 segmentos | Barras apiladas o tabla — un pie con 15 segmentos es ilegible |

Detalle de implementación de gráficos (integridad de datos, accesibilidad, color) en [FRONTEND_ANALYTICS_CHARTS_STANDARD.md](FRONTEND_ANALYTICS_CHARTS_STANDARD.md) — esta sección cubre solo la elección de tipo dentro de un dashboard.

---

## 4. Filtros de fecha/rango

**[RECOMMENDED]** Selector de rango con presets (`Hoy`, `7 días`, `30 días`, `Rango personalizado`) — el usuario rara vez necesita un date picker libre como primera opción, los presets cubren el 90% de los casos.

---

## 5. Densidad de información

**[REQUIRED]** No sobrecargar una sola vista con demasiados widgets. Si el dashboard crece más allá de ~6-8 bloques de contenido, se agrupa en tabs o secciones navegables, no se apila todo en scroll infinito vertical.

---

## 6. Frescura de los datos

**[REQUIRED]** Si los datos no son en tiempo real, se indica explícitamente cuándo se actualizaron por última vez ("Actualizado hace 2 min") — un dashboard sin esa indicación hace que el usuario no sepa si puede confiar en lo que ve. Ese texto se **calcula** con `Intl.RelativeTimeFormat`, nunca se hardcodea — ver [FRONTEND_FORMATTING_STANDARD.md](../Core/FRONTEND_FORMATTING_STANDARD.md).

---

## 7. Responsive

**[REQUIRED]** Los KPI tiles se apilan en columnas menores en mobile (2 columnas en vez de 4-5), y los gráficos se simplifican (menos series visibles simultáneas) en vez de encogerse ilegibles.

---

## 8. Estados

Estado vacío (sin datos aún, cuenta nueva), de carga y de error de un dashboard siguen [FRONTEND_STATES_PATTERNS.md](FRONTEND_STATES_PATTERNS.md) — con la particularidad de que el estado vacío de un dashboard suele necesitar guiar al usuario hacia la primera acción que generaría datos (ej. "Aún no tienes órdenes — crea tu primer producto").

---

## 9. Anti-patrones

- ❌ Reemplazar KPIs + gráfico + tabla por una grilla de cards de texto.
- ❌ Mostrar un número sin delta/comparación de contexto.
- ❌ Gráfico de pie con más de 6-7 segmentos.
- ❌ Dashboard sin indicación de última actualización cuando los datos no son en vivo.
- ❌ Todos los widgets posibles en una sola pantalla sin agrupar por sección/tab.

---

## Checklist rápido

- [ ] ¿Estructura en capas KPI → gráfico → tabla, no cards sueltas?
- [ ] ¿Cada KPI muestra delta/contexto, no solo el número?
- [ ] ¿Tipo de gráfico elegido según el dato (tendencia/comparación/composición)?
- [ ] ¿Rango de fecha con presets?
- [ ] ¿Última actualización indicada si no es tiempo real?
- [ ] ¿KPIs y gráficos responsive, no solo encogidos?
- [ ] ¿Estados vacío/carga/error definidos, con guía de acción en el vacío?
