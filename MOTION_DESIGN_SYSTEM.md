# Motion Design System — JCDigital Engineering Handbook

> **Estándar Oficial de Animación, Transiciones y Movimiento Web**  
> Síntesis de Google Material Design, Apple HIG, Nielsen Norman Group, W3C WCAG y Vercel Web Interface Guidelines.

---

## 1. Principios Fundamentales del Movimiento (Core Philosophy)

1. **Intencional y con Propósito (Apple HIG & NN/g)**:
   - Toda animación debe comunicar jerarquía, estado, orientación espacial o feedback directo. Si no tiene un objetivo funcional claro, se elimina.
2. **Físico y Natural (Material Motion)**:
   - Los elementos no se mueven linealmente; aceleran al salir y desaceleran al llegar (curvas cúbicas Bézier).
3. **Rápido y Eficiente (Vercel Guidelines)**:
   - El movimiento nunca debe retrasar la productividad del usuario ni bloquear la interacción.
4. **Accesible por Defecto (W3C WCAG 2.1)**:
   - Soporte obligatorio y estricto para `@media (prefers-reduced-motion: reduce)`.

---

## 2. Tokens de Duración y Velocidad (Duration Scale)

| Token | Duración | Uso Recomendado |
| :--- | :--- | :--- |
| `--motion-fastest` | `100ms` | Micro-feedback de botones (`active:scale`), toggles de checkbox, switches. |
| `--motion-fast` | `150ms` | Estados hover, tooltips, badge highlights, cambios de color. |
| `--motion-normal` | `200ms` | Dropdowns, popovers, accordions, tabs pequeños. |
| `--motion-drawer` | `250ms` | Entradas/salidas de Drawers laterales, hojas móviles. |
| `--motion-modal` | `200ms` | Diálogos modales (`zoom-in` + `fade-in`). |
| `--motion-page` | `200ms - 250ms` | Transiciones suaves entre rutas/páginas (`opacity` + `translateY`). |

> **Regla de Oro:** Ninguna animación de interacción de usuario frecuente debe superar los **300ms**.

---

## 3. Curvas de Aceleración y Easing (Bézier Curves)

| Nombre | Valor CSS | Propósito |
| :--- | :--- | :--- |
| **Standard (Entrada & Movimiento)** | `cubic-bezier(0.16, 1, 0.3, 1)` | Desaceleración suave y natural para elementos que entran en pantalla (Modales, Drawers). |
| **Sharp / Exit (Salida)** | `cubic-bezier(0.4, 0, 1, 1)` | Salida rápida de elementos que abandonan la vista. |
| **Interactive (Hover/Active)** | `cubic-bezier(0.2, 0, 0, 1)` | Respuesta instantánea y táctil en botones y enlaces. |
| **Linear** | `linear` | **Únicamente** para spinners de carga (`spin`) o indicadores de progreso constante. |

---

## 4. Estándar de Implementación Técnica (Vercel Guidelines)

1. **GPU-Accelerated Only (Solo Propiedades Compuestas)**:
   - **Permitidas:** `transform` (`translate`, `scale`, `rotate`) y `opacity`.
   - **Prohibidas para animar:** `width`, `height`, `top`, `left`, `margin`, `padding`, `box-shadow` (causan *Layout Thrashing* y caídas de 60fps).
2. **Animaciones Cancelables / Interrumpibles**:
   - Si el usuario hace clic en cerrar antes de que termine de abrir un modal, la animación debe revertirse inmediatamente sin esperar el ciclo completo.
3. **CSS sobre JavaScript**:
   - Usar CSS Transitions y `@keyframes` nativos para aprovechar el hilo de renderizado del compositor del navegador.

---

## 5. Tabla Maestra de Componentes y Reglas

| Componente | Tipo de Movimiento | Duración | Easing | Transformación |
| :--- | :--- | :--- | :--- | :--- |
| **Botones** | Press Feedback | `100ms` | `ease-out` | `scale(0.98)` |
| **Hover Cards** | Elevación sutil | `150ms` | `ease-out` | `translateY(-2px)` |
| **Modales** | Entrada centrada | `150ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `scale(0.95) -> scale(1)`, `opacity(0 -> 1)` |
| **Drawers** | Entrada lateral | `200ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `translateX(100% -> 0)` |
| **Dropdowns** | Despliegue menú | `120ms` | `ease-out` | `translateY(-4px) -> translateY(0)`, `opacity` |
| **Badges / Pulses** | Alerta en vivo | `1.5s` | `ease-in-out` | `opacity(0.4 <-> 1)` en bucle |

---

## 6. Configuración Universal CSS (`index.css`)

```css
/* ==========================================================================
   JCDigital Motion Design System Tokens
   ========================================================================== */
:root {
  --ease-standard: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-interactive: cubic-bezier(0.2, 0, 0, 1);
  --ease-exit: cubic-bezier(0.4, 0, 1, 1);

  --dur-fastest: 100ms;
  --dur-fast: 150ms;
  --dur-normal: 200ms;
  --dur-drawer: 250ms;
}

/* Keyframes Estándar */
@keyframes jc-fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes jc-zoom-in {
  from { opacity: 0; transform: scale(0.96); }
  to   { opacity: 1; transform: scale(1); }
}

@keyframes jc-slide-right {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}

@keyframes jc-dropdown {
  from { opacity: 0; transform: translateY(-6px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* Clases de utilidad para Motion */
.motion-fade-in {
  animation: jc-fade-in var(--dur-fast) var(--ease-standard) forwards;
}

.motion-modal-zoom {
  animation: jc-zoom-in var(--dur-fast) var(--ease-standard) forwards;
}

.motion-drawer-slide {
  animation: jc-slide-right var(--dur-drawer) var(--ease-standard) forwards;
}

.motion-interactive-btn {
  transition: transform var(--dur-fastest) var(--ease-interactive),
              background-color var(--dur-fast) ease,
              box-shadow var(--dur-fast) ease;
}
.motion-interactive-btn:active {
  transform: scale(0.98);
}

/* Accesibilidad Estándar (W3C WCAG 2.1) */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
