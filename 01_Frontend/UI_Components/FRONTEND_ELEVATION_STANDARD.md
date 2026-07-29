# FRONTEND ELEVATION STANDARD (Z-Index)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 01 Design System). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Existe porque el `z-index` es de los valores que más rápido se vuelve deuda técnica: cada elemento flotante nuevo (dropdown, modal, toast, tooltip) recibe un número "que funcione" en el momento, y a los pocos meses el proyecto tiene `z-index: 9999999` en algún lado porque nadie recuerda la jerarquía real. El propio dashboard de este handbook (`pruebas/test_dashboard_standard.html`) se construyó con `z-30`/`z-40`/`z-50` sin una escala documentada detrás — funciona porque el orden relativo quedó bien por casualidad, no por regla.

---

## 1. Regla principal

**[REQUIRED]** Toda la app usa una única escala de capas con nombre, no números arbitrarios o crecientes ad-hoc. Un elemento flotante nuevo se ubica en la capa que le corresponde por lo que es, no por "qué número no esté usado todavía".

---

## 2. Escala estándar

**[REQUIRED]**

| Capa | Uso | Valor de referencia |
|---|---|---|
| Base | Contenido normal del documento | `auto` / 0 |
| Sticky | Headers/toolbars pegajosos dentro del flujo (`position: sticky`) | 10 |
| Dropdown / Popover | Menús desplegables, date pickers, autocomplete | 20 |
| Overlay de navegación | Sidebar mobile, drawers (ver `FRONTEND_SIDEBAR_PATTERNS.md`, `FRONTEND_MODALS_PATTERNS.md`) | 30 |
| Modal backdrop | Fondo oscurecido detrás de un modal | 40 |
| Modal / Dialog | Contenido del modal, justo encima de su propio backdrop | 41 |
| Toast / Notificaciones | Siempre visibles por encima de cualquier overlay activo (ver `FRONTEND_NOTIFICATIONS_PATTERNS.md`) | 50 |
| Tooltip | La capa más alta — debe verse incluso dentro de un modal abierto | 60 |

**Por qué este orden y no otro:** un tooltip que aparece dentro de un modal tiene que ganarle al modal; un toast de confirmación tiene que verse aunque haya un drawer abierto detrás. La jerarquía sigue "qué tan efímero e independiente del contexto es el elemento", no el orden en que se construyó cada componente.

---

## 3. Implementación

**[RECOMMENDED]** Capas con nombre en la configuración, no números sueltos en cada componente — mismo principio que los tokens de color (`FRONTEND_COLOR_CONTRAST_STANDARD.md` sección 2): se piensa en el rol, no en el número.

```ts
// tailwind.config.ts
zIndex: {
  sticky: "10",
  dropdown: "20",
  overlay: "30",
  "modal-backdrop": "40",
  modal: "41",
  toast: "50",
  tooltip: "60",
}
```

```tsx
<header className="sticky top-0 z-sticky">...</header>
<div className="fixed inset-0 z-modal-backdrop">...</div>
<div role="dialog" className="z-modal">...</div>
```

---

## 4. Reglas adicionales

**[REQUIRED]** `z-index` solo tiene efecto en un elemento posicionado (`relative`, `absolute`, `fixed`, `sticky`) — no se agrega a un elemento con `position: static` esperando que haga algo.

**[REQUIRED]** Ningún componente nuevo introduce un valor fuera de la escala de la sección 2 (nada de `z-index: 999`, `9999`, `2147483647`) — si un elemento parece necesitar "ganarle a todo", eso significa que falta una capa en la escala, se agrega ahí formalmente, no se hackea con un número gigante.

---

## 5. Anti-patrones

- ❌ `z-index: 9999` (o mayor) como solución rápida para "que se vea encima".
- ❌ Números que escalan indefinidamente cada vez que se agrega un elemento flotante nuevo (`z-51`, `z-52`, `z-53`...).
- ❌ `z-index` en un elemento sin `position` explícito.
- ❌ Un tooltip o toast con z-index menor que el de un modal — deben poder aparecer por encima de cualquier cosa.

---

## Checklist rápido

- [ ] ¿El elemento flotante usa una de las capas nombradas de la sección 2, no un número inventado?
- [ ] ¿Tiene `position` explícito (`relative`/`absolute`/`fixed`/`sticky`)?
- [ ] ¿Un tooltip/toast sigue siendo visible por encima de un modal abierto?
- [ ] ¿Ningún valor fuera de la escala (nada de 4+ dígitos)?
