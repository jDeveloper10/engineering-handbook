---
title: "Estándar de Analítica y Gráficos"
category: 01_Frontend
tags: [frontend, charts, analytics, accesibilidad]
summary: "Reglas para visualización de datos: integridad del dato, el color nunca como único indicador, interactividad, accesibilidad de la información graficada y comportamiento responsive."
keywords: [charts, graficos, analytics, color, accesibilidad, responsive, anti-patrones]
updated: 2026-07-27
status: current
---

# FRONTEND ANALYTICS & CHARTS STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y de [FRONTEND_DASHBOARD_PATTERNS.md](FRONTEND_DASHBOARD_PATTERNS.md) sección 3 (elección de tipo de gráfico según el dato — ese punto no se repite aquí). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Especialmente relevante para este proyecto: un dashboard de trading usa literalmente rojo=pérdida/verde=ganancia — el peor caso posible para depender solo del color, porque el daltonismo rojo-verde es el más común (~8% de hombres).

---

## 1. Integridad de datos

**[REQUIRED]** El eje Y de un gráfico de barras siempre empieza en 0 — cortarlo para exagerar una diferencia distorsiona la magnitud real que el usuario percibe.

**[RECOMMENDED]** Un gráfico de línea de tendencia puede no empezar en 0 (para mostrar mejor la variación), pero si el corte es agresivo, se indica visualmente (una marca de eje quebrado) — nunca se oculta que el eje no arranca en cero.

**Por qué:** en un producto financiero, un gráfico que exagera visualmente una ganancia o pérdida no es solo mala práctica de diseño, es un problema de confianza real con el usuario.

---

## 2. Color nunca es el único indicador

**[REQUIRED]** Ninguna serie o estado crítico se diferencia **solo** por color — siempre hay un segundo indicador (ícono, patrón, texto, posición).

```
❌ Verde = ganancia, rojo = pérdida, sin nada más
✅ Verde + ▲ = ganancia, rojo + ▼ = pérdida
```

**Por qué:** el daltonismo rojo-verde es el más común (~8% de hombres) — exactamente la combinación que domina en dashboards financieros/de trading. Sin un segundo indicador, una parte real de usuarios no puede distinguir ganancia de pérdida de un vistazo.

**[RECOMMENDED]** Paleta apta para daltonismo cuando hay 3+ series en el mismo gráfico (evitar depender solo de tonos rojo/verde/marrón adyacentes).

---

## 3. Interactividad

**[RECOMMENDED]** Tooltip al hover/tap que muestra el valor exacto del punto — la forma visual del gráfico comunica tendencia, pero el usuario necesita el número preciso cuando lo pide.

---

## 4. Accesibilidad de datos

**[REQUIRED]** Un gráfico (SVG/canvas) no es accesible por sí solo para un lector de pantalla. Se provee una alternativa: tabla de datos visualmente oculta pero accesible (no `display:none`, sí `sr-only`/equivalente), o un resumen textual del hallazgo principal ("Rendimiento subió 18% en los últimos 30 días").

```html
<div role="img" aria-label="Rendimiento acumulado: tendencia creciente, +18% en 30 días">
  <svg>...</svg>
</div>
```

---

## 5. Responsive

Ver `FRONTEND_DASHBOARD_PATTERNS.md` sección 7 — en mobile se simplifican las series visibles y los ejes, no se encoge el mismo gráfico denso a un tamaño ilegible.

---

## 6. Anti-patrones

- ❌ Gráficos 3D — distorsionan la percepción de magnitud sin aportar información real.
- ❌ Más de 5-6 series/líneas en un mismo gráfico — se vuelve ilegible.
- ❌ Doble eje Y sin dejar clarísimo (leyenda, color de eje) a qué serie corresponde cada uno.
- ❌ Color como único diferenciador de un estado crítico (ganancia/pérdida, éxito/error).
- ❌ Eje Y de barras que no empieza en 0 sin justificación.
- ❌ Gráfico sin ninguna alternativa textual/accesible para lectores de pantalla.

---

## Checklist rápido

- [ ] ¿Eje Y de barras empieza en 0? ¿Corte de eje en líneas señalado visualmente si aplica?
- [ ] ¿Ningún estado crítico depende solo del color (ganancia/pérdida con ícono o texto adicional)?
- [ ] ¿Tooltip con valor exacto disponible?
- [ ] ¿Alternativa accesible (tabla oculta o resumen) para lectores de pantalla?
- [ ] ¿Máximo 5-6 series por gráfico, sin 3D, sin doble eje ambiguo?
