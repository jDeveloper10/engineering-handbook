---
title: "Estándar de Sistema de Iconos"
category: 01_Frontend
tags: [frontend, iconos, accesibilidad]
summary: "Tamaño de icono ligado a la tipografía que acompaña, nombre accesible según sea decorativo o significativo, y anti-patrones del uso de iconos."
keywords: [iconos, lucide, tamano, aria-hidden, nombre-accesible]
updated: 2026-07-27
status: current
---

# FRONTEND ICON SYSTEM STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 1.4 — ya exige una sola librería de iconos; este documento profundiza) y de [FRONTEND_ACCESSIBILITY_STANDARD.md](FRONTEND_ACCESSIBILITY_STANDARD.md) (nombre accesible). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).

---

## 1. Regla principal

**[REQUIRED]** Una sola librería/set de íconos por proyecto (ej. `lucide-react`), un solo estilo de renderizado (outline, filled o duotone — no mezclados), un solo grosor de trazo consistente en todo el proyecto.

**Por qué:** íconos de sets distintos tienen proporciones y grosores distintos entre sí — mezclarlos se nota de inmediato, aunque cada ícono individual se vea bien por separado.

---

## 2. Tamaño ligado a la tipografía

**[RECOMMENDED]** El tamaño del ícono se correlaciona con el texto que acompaña, no se elige al ojo:

| Contexto | Tamaño de referencia |
|---|---|
| Ícono inline junto a texto de body | ≈ misma altura que el texto (16-18px) |
| Ícono dentro de un botón | 16-20px |
| Ícono decorativo grande (hero, empty state) | 24-32px+ |

---

## 3. Nombre accesible

**[REQUIRED]** Todo botón de solo-ícono (sin texto visible) lleva `aria-label` describiendo la acción — ya aplicado consistentemente en los tests de este handbook (`aria-label="Mostrar contraseña"`, `aria-label="Cerrar menú"`, etc.).

**[REQUIRED]** Un ícono puramente decorativo que acompaña texto visible (el ícono de una card, un check junto a "Guardado") lleva `aria-hidden="true"` — evita que un lector de pantalla lo anuncie por separado y duplique la información que el texto ya da.

```html
<!-- Ícono con texto visible: decorativo, se oculta a AT -->
<span aria-hidden="true">✔</span> Guardado

<!-- Ícono solo, sin texto: necesita nombre accesible -->
<button aria-label="Cerrar"><svg>...</svg></button>
```

---

## 4. Anti-patrones

- ❌ Mezclar 2+ librerías de íconos (ej. `lucide-react` + `heroicons`) en el mismo proyecto.
- ❌ Botón de solo-ícono sin `aria-label`.
- ❌ Ícono decorativo sin `aria-hidden="true"`, leído dos veces por un lector de pantalla junto al texto que ya lo acompaña.
- ❌ Grosor de trazo inconsistente entre íconos del mismo set (mezclando variantes thin/regular/bold sin criterio).
- ❌ Tamaño de ícono elegido al ojo, sin relación con el texto que acompaña.

---

## Checklist rápido

- [ ] ¿Un solo set de íconos, un solo estilo de renderizado, en todo el proyecto?
- [ ] ¿Tamaño de ícono coherente con el texto que acompaña?
- [ ] ¿Todo ícono de solo-botón tiene `aria-label`?
- [ ] ¿Todo ícono decorativo junto a texto tiene `aria-hidden="true"`?
