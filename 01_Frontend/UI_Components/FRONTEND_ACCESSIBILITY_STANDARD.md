---
title: "Estándar de Accesibilidad Web"
category: 01_Frontend
tags: [frontend, accesibilidad, wcag, aria]
summary: "Nivel de conformidad objetivo y su implementación: base semántica, navegación por teclado, gestión de foco, la regla de oro de ARIA, contraste y respeto por prefers-reduced-motion."
keywords: [accesibilidad, wcag, aria, teclado, foco, contraste, reduced-motion]
updated: 2026-07-27
status: current
---

# FRONTEND ACCESSIBILITY STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 13 — que se mantiene como el resumen `REQUIRED` de siempre) y de [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) (la base semántica de la que depende toda accesibilidad real). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Se separa de HTML Structure a propósito, aunque están muy relacionados: HTML Structure define *qué etiqueta usar*; este documento define *cómo se comporta la interfaz* para alguien que navega con teclado, lector de pantalla, o con baja visión. Una IA puede necesitar consultar uno sin el otro según la tarea.

---

## 1. Nivel de conformidad objetivo

**[REQUIRED]** WCAG 2.1 nivel **AA** es el estándar por defecto en todo proyecto — no A (insuficiente para producción real) ni AAA (over-engineering salvo que el rubro lo exija: salud, gobierno, banca regulada). Si un proyecto específico requiere AAA, se documenta esa excepción en el propio repo, no se asume por defecto.

---

## 2. Base semántica

**[REQUIRED]** Toda accesibilidad real empieza en el HTML correcto — ver [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) completo. Este documento no repite esas reglas, las asume como punto de partida.

---

## 3. Navegación por teclado

**[REQUIRED]** Todo elemento interactivo es alcanzable y operable con `Tab`/`Shift+Tab`, `Enter`/`Space`, y `Esc` donde aplica — sin trampas de foco (el usuario nunca queda atrapado sin poder salir de un componente con teclado).

**[REQUIRED]** El orden de tabulación sigue el orden natural del DOM. **[REQUIRED]** prohibido `tabindex` positivo (`tabindex="1"`, `"2"`...) para forzar un orden custom — rompe el orden natural y es casi imposible de mantener consistente al agregar elementos nuevos. `tabindex="0"` (agregar al orden natural) y `tabindex="-1"` (sacar del orden, útil para foco programático) sí son válidos.

**[RECOMMENDED]** Un "skip link" (enlace oculto que aparece al enfocar, "Saltar al contenido principal") al inicio de la página en apps con navegación larga — evita que un usuario de teclado tenga que tabular por todo el navbar/sidebar en cada carga de página para llegar al contenido.

**[RECOMMENDED]** Atajos de teclado (Command Palette, `Esc` para cerrar, `/` para buscar) en apps densas de uso frecuente — ver `FRONTEND_NAVIGATION_PATTERNS.md` sección 6 (Command Palette).

---

## 4. Gestión de foco

**[REQUIRED]** Modales y drawers atrapan el foco mientras están abiertos (focus trap) y lo devuelven al elemento que los abrió al cerrarse — ver `FRONTEND_MODALS_PATTERNS.md` secciones 3 y 6.

**[REQUIRED]** Al abrir un modal/drawer, el foco se mueve explícitamente al primer elemento interactivo o al título del modal — nunca se queda en el elemento de fondo que lo disparó mientras el modal ya está visualmente abierto.

**[REQUIRED]** `focus-visible` nunca se elimina sin un reemplazo — un indicador de foco visible siempre existe para navegación por teclado (ya en `FRONTEND_ENGINEERING_STANDARD.md` 13.3).

---

## 5. ARIA — regla de oro

**[REQUIRED]** "No ARIA es mejor que ARIA mal usado" (principio oficial de las WAI-ARIA Authoring Practices). Se usa HTML semántico nativo primero (sección 2); ARIA solo se agrega para lo que el HTML no puede expresar por sí solo — típicamente **estado dinámico**:

| Atributo | Para qué |
|---|---|
| `aria-expanded` | Un elemento colapsable (accordion, dropdown) está abierto o cerrado |
| `aria-selected` | Un ítem dentro de un grupo (tab, opción de lista) está seleccionado |
| `aria-current` | El ítem de navegación activo (`aria-current="page"`) |
| `aria-live` | Región que anuncia cambios dinámicos sin que el usuario la enfoque — `polite` para info, `assertive` solo para errores críticos (ya usado en `FRONTEND_AUTH_PATTERNS.md` y `FRONTEND_NOTIFICATIONS_PATTERNS.md`) |
| `aria-label` / `aria-labelledby` | Nombre accesible cuando no hay texto visible (ej. un botón de solo ícono) |
| `role="dialog"` + `aria-modal` | Modales (ver `FRONTEND_MODALS_PATTERNS.md` sección 6) |

**[REQUIRED]** Nunca agregar un `role` que contradiga el elemento nativo (ej. `role="button"` sobre un `<button>` ya es redundante e innecesario; sobre un `<div>` es el mínimo aceptable solo si de verdad no se puede usar `<button>`, y aun así requiere replicar manualmente el soporte de teclado que `<button>` ya trae gratis).

---

## 6. Contraste

**[REQUIRED]** Mínimo WCAG AA — 4.5:1 texto normal, 3:1 texto grande (≥18px o ≥14px bold) — validado al definir los tokens de color del design system (`FRONTEND_ENGINEERING_STANDARD.md` 1.2), no al final del proyecto. Ver también `FRONTEND_UI_STYLE_CATALOG.md` sección "Cómo pasar un estilo del catálogo a tokens" — varios estilos vibrantes (Cyberpunk, Vaporwave, Web3) necesitan ajuste explícito de contraste antes de usarse en texto real. Reglas completas de construcción de paleta (dark/light mode, componentes UI también requieren 3:1) en [FRONTEND_COLOR_CONTRAST_STANDARD.md](FRONTEND_COLOR_CONTRAST_STANDARD.md).

---

## 7. Contenido no textual

**[REQUIRED]** `alt` descriptivo en imágenes con significado; `alt=""` explícito en decorativas (ya en `FRONTEND_ENGINEERING_STANDARD.md` 13.5). **[RECOMMENDED]** transcripción o subtítulos si el producto incluye audio/video con información relevante para la tarea.

---

## 8. Movimiento y animación

**[REQUIRED]** Respetar la preferencia del sistema `prefers-reduced-motion` — animaciones decorativas (Framer Motion, transiciones grandes) se reducen o eliminan para el usuario que la activó, especialmente relevante en este stack porque Framer Motion se usa activamente (`FRONTEND_ENGINEERING_STANDARD.md`, stack de referencia).

**Por qué:** para una parte real de usuarios (trastornos vestibulares, migrañas), animación grande no controlada es un problema de accesibilidad real, no solo una preferencia estética.

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

Sistema completo de duración/easing en [FRONTEND_MOTION_STANDARD.md](FRONTEND_MOTION_STANDARD.md).

---

## 9. Formularios accesibles

Cubierto en `FRONTEND_ENGINEERING_STANDARD.md` sección 9.4 y, para autenticación específicamente, en `FRONTEND_AUTH_PATTERNS.md` sección 14 — labels asociados, errores anunciables vía `aria-describedby`/`aria-live`. Este documento no lo repite.

---

## 10. Testing de accesibilidad

**[REQUIRED]** Antes de dar una feature grande por terminada:
1. Navegar el flujo completo solo con teclado (sin mouse) — confirmar que nada queda inalcanzable.
2. Probar el flujo crítico con un lector de pantalla básico (VoiceOver en Mac, NVDA en Windows) — confirmar que lo que se anuncia tiene sentido.
3. Validar contraste de los colores reales usados, no solo de los tokens en abstracto.

**[RECOMMENDED]** Correr un linter automático (axe, Lighthouse accessibility audit) como red de seguridad adicional — **[REQUIRED]** un linter automático nunca reemplaza el paso 1 y 2: las herramientas automáticas detectan quizás el 30-40% de los problemas reales de accesibilidad (falta de `alt`, contraste, HTML inválido), pero no pueden evaluar si el orden de foco tiene sentido o si un lector de pantalla comunica la información correcta.

---

## 11. Anti-patrones

- ❌ `tabindex` positivo para forzar un orden de tabulación custom.
- ❌ Modal sin focus trap, o que no devuelve el foco al cerrar.
- ❌ `role="button"` en un `<div>` cuando `<button>` habría funcionado igual.
- ❌ `aria-live="assertive"` en notificaciones triviales, interrumpiendo innecesariamente al usuario de lector de pantalla.
- ❌ Animación grande sin respetar `prefers-reduced-motion`.
- ❌ Confiar solo en un linter automático (axe/Lighthouse) sin haber navegado el flujo con teclado ni probado con lector de pantalla.
- ❌ Corregir accesibilidad "al final" del proyecto en vez de validarla junto con cada feature.

---

## Checklist rápido

- [ ] ¿HTML semántico como base (`FRONTEND_HTML_STRUCTURE_STANDARD.md`), ARIA solo para lo que el HTML no puede expresar?
- [ ] ¿Navegable completo por teclado, sin `tabindex` positivo, sin trampas de foco?
- [ ] ¿Modales con focus trap y devolución de foco al cerrar?
- [ ] ¿`aria-live` correcto según criticidad (`polite` vs `assertive`)?
- [ ] ¿Contraste AA validado en los colores reales, no solo en abstracto?
- [ ] ¿`prefers-reduced-motion` respetado en animaciones grandes?
- [ ] ¿Se probó el flujo crítico con teclado y con un lector de pantalla, no solo con un linter automático?
