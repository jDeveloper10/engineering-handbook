---
title: "Estándar de Animación y Movimiento"
category: 01_Frontend
doc_type: estandar
tags: [frontend, animacion, motion, accesibilidad]
summary: "Escala de duración y easing para animaciones, reutilización mediante variantes, respeto obligatorio por prefers-reduced-motion y prohibición de animaciones que bloqueen la interacción."
keywords: [animacion, motion, duracion, easing, framer-motion, reduced-motion]
updated: 2026-07-27
status: current
---

# FRONTEND MOTION STANDARD (Animación)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y de [FRONTEND_ACCESSIBILITY_STANDARD.md](FRONTEND_ACCESSIBILITY_STANDARD.md) sección 8 (`prefers-reduced-motion`, no se repite aquí). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Relevante porque Framer Motion ya está en el stack de referencia (`FRONTEND_ENGINEERING_STANDARD.md`) — sin un sistema, "tenerlo disponible" se convierte en "animar todo porque se puede".

---

## 1. Regla principal

**[REQUIRED]** La animación comunica algo — relación causa-efecto (un modal que crece desde el botón que lo abrió), feedback de estado (loading, éxito, error), o dirección de navegación. No se anima por decoración sin propósito.

---

## 2. Escala de duración

**[RECOMMENDED]**

| Tipo de movimiento | Duración |
|---|---|
| Micro-interacción (hover, toggle, focus) | 100-150ms |
| Transición de UI (abrir modal, cambiar tab, dropdown) | 200-300ms |
| Transición grande (cambio de página/vista completa) | 300-400ms |

**[REQUIRED]** Nada que el usuario espera activamente (un modal abriendo, un dropdown desplegando) supera ~400-500ms — más que eso se percibe como lento, no como elegante.

---

## 3. Easing

**[RECOMMENDED]** `ease-out` para elementos que entran (aceleran hacia el punto final, se sienten responsivos); `ease-in` para elementos que salen; `ease-in-out` para transiciones continuas de un estado a otro sin entrada/salida clara.

---

## 4. Reutilización (Framer Motion)

**[RECOMMENDED]** Variants de animación definidos una sola vez y reutilizados (`fadeIn`, `slideUp`, etc.) en vez de reescribir configuración de animación distinta en cada componente — mismo principio que los tokens de diseño (`FRONTEND_ENGINEERING_STANDARD.md` sección 01): consistencia por sistema, no por memoria de cada desarrollador.

---

## 5. Accesibilidad

Ver `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 8 — toda animación no esencial respeta `prefers-reduced-motion`. **[REQUIRED]** ninguna animación bloquea la interacción del usuario mientras corre (un botón no debe quedar inoperable durante su propia animación de feedback).

---

## 6. Anti-patrones

- ❌ Animar todo (fade + slide en cada elemento) sin que comunique nada específico.
- ❌ Duraciones elegidas al azar, sin relación con la escala de la sección 2.
- ❌ Animaciones de más de 500ms en interacciones que el usuario espera activamente.
- ❌ Configuración de animación reescrita distinta en cada componente en vez de variants reutilizables.
- ❌ Ignorar `prefers-reduced-motion`.
- ❌ Un elemento no interactuable mientras su propia animación de entrada/salida está en curso.

---

## Checklist rápido

- [ ] ¿Cada animación comunica algo (causa-efecto, feedback, dirección), no decoración sin propósito?
- [ ] ¿Duración dentro de la escala de la sección 2?
- [ ] ¿Easing apropiado según si el elemento entra, sale, o transiciona?
- [ ] ¿Variants reutilizables en vez de configuración repetida por componente?
- [ ] ¿`prefers-reduced-motion` respetado, sin bloquear interacción durante la animación?
