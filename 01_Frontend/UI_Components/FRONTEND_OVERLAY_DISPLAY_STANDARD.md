# FRONTEND OVERLAY & DISPLAY STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1: secciones 01, 04 y 13). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Define la anatomía exacta de superposiciones (tooltip, popover, dropdown, command palette, date picker) y componentes de display (badge, avatar, tabs, accordion, progress, pagination, breadcrumb, timeline, divider) — para que una IA los genere con proporciones y comportamiento nivel Stripe/Linear de serie. **No repite** lo ya cubierto: modales y drawers viven en [FRONTEND_MODALS_PATTERNS.md](../Patterns/FRONTEND_MODALS_PATTERNS.md); toasts/banners/badge-contador en [FRONTEND_NOTIFICATIONS_PATTERNS.md](../Patterns/FRONTEND_NOTIFICATIONS_PATTERNS.md); skeleton/empty/error como *estados de pantalla* en [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md); el "cuándo usar" de tabs/breadcrumbs/command palette en [FRONTEND_NAVIGATION_PATTERNS.md](../Patterns/FRONTEND_NAVIGATION_PATTERNS.md) sección 6. Contrastado contra WAI-ARIA Authoring Practices, Radix UI y los sistemas de Stripe/Linear.

---

## 1. Reglas transversales a toda superposición

**[REQUIRED]** Toda superposición (tooltip, popover, dropdown, palette, date picker) cumple:

1. **Capa correcta** de la escala de [FRONTEND_ELEVATION_STANDARD.md](FRONTEND_ELEVATION_STANDARD.md) — nunca `z-index` inventado.
2. **Separación del trigger:** 4-8px entre el trigger y el panel flotante.
3. **Posicionamiento con colisión:** si no cabe abajo, se voltea arriba (flip); nunca se corta contra el borde del viewport.
4. **Cierre:** `Esc` siempre cierra; clic fuera cierra (salvo tooltip, que cierra al salir el hover/foco).
5. **Foco de vuelta al trigger** al cerrar cualquier overlay que haya tomado foco — mismo principio de `FRONTEND_MODALS_PATTERNS.md` sección 6.
6. **Animación de entrada** 200-300ms máximo, `ease-out` (hereda [FRONTEND_MOTION_STANDARD.md](FRONTEND_MOTION_STANDARD.md)); la salida puede ser más corta o instantánea.

**Por qué:** estas seis propiedades son lo que separa un dropdown "de sistema" de un `<div absolute>` pegado a mano — y son exactamente las que una IA omite cuando improvisa el overlay sin librería de posicionamiento (Radix, Floating UI).

---

## 2. Tooltip

### 2.1 Anatomía

**[REQUIRED]** Texto de 12-13px sobre fondo oscuro de alto contraste (o el inverso en dark mode), padding 6-8px vertical / 8-12px horizontal, radio 6px, **ancho máximo 250px** con wrap — un tooltip de una pantalla de ancho es un popover mal clasificado. Flecha opcional de 8px.

### 2.2 Comportamiento

- **[REQUIRED]** Delay de apertura de 300-500ms en hover; una vez abierto un tooltip, los tooltips hermanos abren sin delay mientras el mouse siga moviéndose entre triggers (patrón "warm-up" de Stripe/Radix). Cierre inmediato al salir.
- **[REQUIRED]** Abre también con foco de teclado (sin delay) — un control con tooltip que solo responde a mouse esconde información al usuario de teclado.
- **[REQUIRED]** Nunca información esencial **solo** en tooltip: el tooltip amplía o etiqueta, no es el único canal de un dato necesario para completar la tarea.

**Por qué:** el tooltip no existe en touch — en mobile no hay hover, así que todo lo que solo vive en tooltip es invisible para la mitad de los usuarios. Si el dato es esencial, va visible en el layout o en un popover que abre por tap.

- **[REQUIRED]** En mobile el tooltip se omite o se reemplaza por texto visible/popover — no simular "tooltip por tap" que compite con el tap real del control.

### 2.3 Accesibilidad y errores

- **[REQUIRED]** `role="tooltip"` en el panel + `aria-describedby` en el trigger apuntando a él. Si el tooltip es el *nombre* de un icon-button, entonces es `aria-label` en el botón y el tooltip solo lo duplica visualmente.
- **[REQUIRED]** El tooltip nunca contiene elementos interactivos (links, botones) — si los necesita, es un Popover (sección 3).
```tsx
// IMPLEMENTACIÓN (mínima; en la práctica usar Radix Tooltip que trae delay, warm-up y flip)
<button aria-describedby="tt-copy" aria-label="Copiar enlace" className="size-10 ...">
  <LinkIcon aria-hidden className="size-4" />
</button>
<div id="tt-copy" role="tooltip"
  className="max-w-62 rounded-md bg-neutral-900 px-3 py-1.5 text-xs text-white">
  Copiar enlace al portapapeles
</div>
```

- ❌ Errores de IA: tooltip que abre al clic (eso es popover); tooltip sobre un botón `disabled` (los elementos disabled no emiten eventos — envolver en un `<span>` que reciba el hover/foco); información crítica (límites, precios, errores) solo en tooltip.

---

## 3. Popover vs Dropdown menu

### 3.1 La distinción

**[REQUIRED]** Son dos componentes distintos, no dos nombres del mismo `<div>` flotante:

| | Dropdown menu | Popover |
|---|---|---|
| Contenido | **Lista de acciones/comandos** | Contenido libre (formulario corto, detalle, filtros) |
| Roles ARIA | `role="menu"` + `role="menuitem"` | Sin rol de menú; `role="dialog"` si toma foco |
| Teclado | Flechas mueven entre ítems, letra salta al ítem | `Tab` navega como en cualquier contenido |
| Ejemplo | Menú "..." de una fila de tabla | Selector de filtros, popover de fecha, mini-perfil |

**Por qué:** `role="menu"` promete al lector de pantalla un contrato de teclado específico (flechas, no Tab). Ponerlo sobre un popover con inputs lo rompe: el usuario de lector queda con un formulario que anuncia "menú" y no se puede tabular. Es de los errores ARIA más comunes en código generado.

### 3.2 Anatomía (dropdown menu)

**[REQUIRED]** Panel: radio 8px, padding vertical 4-6px, ancho mínimo 180px (nunca menor que el trigger). Ítem: altura 32-36px, padding horizontal 8-12px, texto 14px, ícono opcional 16px con gap 8px, radio interior 6px con margen 4px (estilo Linear). Separador entre grupos: línea de 1px con margen vertical 4px y `role="separator"`. Ítem destructivo en token `danger`, **siempre al final** del menú.

### 3.3 Comportamiento y teclado

**[REQUIRED]** Trigger con `aria-haspopup="menu"` + `aria-expanded`. Al abrir con teclado (`Enter`/`Space`/`↓`), el foco entra al primer ítem; `↓`/`↑` circulan, `Home`/`End` a extremos, `Esc` cierra y **devuelve el foco al trigger**, `Enter` ejecuta y cierra. Clic fuera cierra sin ejecutar.

**[RECOMMENDED]** Abrir por clic, no por hover — un menú de acciones que abre por hover se dispara accidentalmente y no existe en touch. (Hover-menu solo en navegación tipo mega-menu, ver `FRONTEND_NAVIGATION_PATTERNS.md`.)

```tsx
// IMPLEMENTACIÓN (estructura mínima; en la práctica usar Radix/Headless UI que la trae completa)
<button aria-haspopup="menu" aria-expanded={open} onClick={toggle}>Acciones</button>
{open && (
  <div role="menu" className="min-w-45 rounded-lg border bg-surface p-1 shadow-lg">
    <button role="menuitem" className="flex h-9 w-full items-center gap-2 rounded-md px-3 text-sm hover:bg-neutral-100">
      <PencilIcon aria-hidden className="size-4" /> Editar
    </button>
    <div role="separator" className="my-1 h-px bg-neutral-200" />
    <button role="menuitem" className="... text-danger">Eliminar</button>
  </div>
)}
```

### 3.4 Errores comunes de IA

- ❌ `role="menu"` en popovers con formularios, o en listas de links de navegación (los links usan nav/list normal).
- ❌ Menú sin navegación por flechas ni retorno de foco al trigger.
- ❌ Acción destructiva en medio del menú, sin separador ni color `danger`.
- ❌ Panel más angosto que el trigger, o pegado a 0px de él.

---

## 4. Command palette

Cuándo incluirla (apps densas, power users — no productos de uso esporádico): ya definido en `FRONTEND_NAVIGATION_PATTERNS.md` secciones 1 y 6. Aquí, la anatomía:

### 4.1 Anatomía

**[REQUIRED]** Modal centrado en el tercio superior de la pantalla (~15-20vh desde arriba), ancho 560-640px, radio 12px, elevación máxima de la escala. Estructura: input de búsqueda de 48-56px arriba (sin borde propio, separado por línea de 1px) → lista de resultados con altura máxima ~400px y scroll → footer opcional de 32px con hints de teclado (`↑↓ navegar · ↵ abrir · esc cerrar`).

**[REQUIRED]** Resultados agrupados con headers de grupo (11-12px uppercase, muted) — "Navegación", "Acciones", "Recientes". Ítem: 40-44px de alto, ícono 16px + label + atajo de teclado a la derecha en `<kbd>` muted.

### 4.2 Comportamiento

- **[REQUIRED]** Abre con `Cmd+K` (macOS) / `Ctrl+K` (Windows/Linux) — detectar plataforma para el hint visual. Es un dialog: focus trap, `Esc` cierra, foco vuelve al punto de origen (`FRONTEND_MODALS_PATTERNS.md` secciones 3 y 6 aplican).
- **[REQUIRED]** Búsqueda fuzzy (tolera errores de tipeo y coincidencias parciales: "crus" encuentra "Crear usuario"), con el primer resultado pre-resaltado — `Enter` inmediato ejecuta lo más probable.
- **[RECOMMENDED]** Con input vacío: mostrar recientes + acciones frecuentes, no un panel en blanco. Con 0 resultados: mensaje explícito (misma regla que Combobox en [FRONTEND_FORM_CONTROLS_STANDARD.md](FRONTEND_FORM_CONTROLS_STANDARD.md) sección 6).
- **[REQUIRED]** ARIA: es el mismo contrato combobox + listbox de `FRONTEND_FORM_CONTROLS_STANDARD.md` sección 6.3 (foco fijo en el input, `aria-activedescendant` para el resaltado), dentro de un `role="dialog"`.

- ❌ Errores de IA: búsqueda por `includes()` exacto (sin fuzzy); resultados sin agrupar; palette que no registra el atajo global o lo registra dos veces (una por render).

---

## 5. Badge / Chip / Tag

### 5.1 La distinción

**[REQUIRED]**

| | Badge (de estado) | Chip/Tag |
|---|---|---|
| Es | Etiqueta **de solo lectura**: estado, categoría, contador | Elemento **interactivo**: filtro activo, selección, token de input |
| Interacción | Ninguna (no clicable, no removible) | Clicable y/o removible con "×" |
| Altura | 20-24px | 24-32px (respetando touch target vía área táctil) |

El badge-contador de notificaciones ("99+") ya está definido en `FRONTEND_NOTIFICATIONS_PATTERNS.md` sección 4 — se hereda, no se redefine.

### 5.2 Anatomía y variantes

**[REQUIRED]** Badge: texto 12px medium, padding horizontal 8px, radio 6px o full; fondo suave del token semántico + texto oscuro del mismo token (ej. fondo `success` al 10-15%, texto `success` a contraste AA) — no fondo sólido saturado por defecto. **[REQUIRED]** El color va acompañado de texto (o punto + texto): "● Activo", nunca solo un punto de color — misma regla anti-solo-color de `FRONTEND_FORM_CONTROLS_STANDARD.md` 3.3.

**[REQUIRED]** Chip removible: el "×" es un icon-button real de ≥16px con `aria-label="Quitar {label}"`, no un span decorativo. Removible **solo** cuando quitar es una acción legítima del usuario (filtros aplicados, destinatarios, tags editables) — un chip de estado no lleva "×".

- ❌ Errores de IA: todo como badge sólido saturado gritando en la tabla; estado comunicado solo con punto de color; "×" sin nombre accesible; badges clicables sin ser botones reales.

---

## 6. Avatar

**Anatomía [REQUIRED]:** tamaños de la escala: 24px (listas densas, stacking), 32px (filas de tabla, comentarios), 40px (headers, perfiles en cards), 64px+ (página de perfil). Circular por defecto; texto de iniciales ≈ 40% del diámetro.

**Fallback [REQUIRED]:** sin imagen (o imagen rota), el avatar muestra **iniciales** (1-2 letras: nombre + apellido) sobre un fondo de color **determinístico derivado del nombre** (hash del string → paleta de tokens) — nunca aleatorio por render, para que la misma persona tenga siempre el mismo color. Último fallback (sin nombre): ícono genérico de usuario, no un cuadro vacío.

**Stacking [RECOMMENDED]:** solapamiento de ~1/3 del diámetro (ej. -8px en avatares de 24-32px), cada avatar con anillo de 2px del color del fondo para separarse; máximo 3-5 visibles + contador "+N" con el mismo tamaño y estilo. El orden apila el primero arriba (z decreciente hacia la derecha).

**Accesibilidad [REQUIRED]:** si el avatar acompaña el nombre visible, la imagen lleva `alt=""` (decorativa — el nombre ya está en texto); si el avatar está solo (stack, celda compacta), `alt` o `aria-label` con el nombre completo.

```tsx
// IMPLEMENTACIÓN — fallback determinístico + stack
const colors = ["bg-brand-500", "bg-emerald-500", "bg-amber-500", "bg-rose-500", "bg-violet-500"];
const colorFor = (name: string) =>
  colors[[...name].reduce((a, c) => a + c.charCodeAt(0), 0) % colors.length];

<div className="flex -space-x-2">
  {users.slice(0, 4).map((u) => (
    <span key={u.id} title={u.name}
      className={`flex size-8 items-center justify-center rounded-full ring-2 ring-surface
        text-xs font-medium text-white ${colorFor(u.name)}`}
      aria-label={u.name}>
      {initials(u.name)}
    </span>
  ))}
  {users.length > 4 && (
    <span className="flex size-8 items-center justify-center rounded-full bg-neutral-200 ring-2 ring-surface text-xs font-medium">
      +{users.length - 4}
    </span>
  )}
</div>
```

- ❌ Errores de IA: color de fallback aleatorio que cambia en cada render; `alt="avatar"` duplicando ruido; stacking sin anillo (masa de círculos ilegible); "+12" con estilo distinto al resto del stack.

---

## 7. Accordion

Cuándo usarlo (FAQ, contenido colapsable secundario): `FRONTEND_UI_PATTERNS.md` sección 2. Aquí el cómo:

**[REQUIRED]** Primera opción: `<details>/<summary>` nativos — traen gratis toggle, teclado y semántica, sin JavaScript. Un accordion custom solo se justifica para: animación de altura, "solo uno abierto a la vez" (comportamiento exclusivo), o estilos que `summary` no permite en los navegadores objetivo.

**Anatomía [REQUIRED]:** header clicable de 48-56px con el título (15-16px medium) + chevron de 16-20px a la derecha que **rota 180°** al abrir (100-150ms); contenido con padding 16px y línea separadora de 1px entre ítems. Todo el header es clicable, no solo el ícono.

**Custom [REQUIRED]:** header = `<button aria-expanded aria-controls="panel-id">` dentro de un heading del nivel correcto (`<h3><button>…</button></h3>`); panel con `role="region"` + `aria-labelledby` al botón. `Enter`/`Space` alternan.

**[RECOMMENDED]** Por defecto permitir varios abiertos; el modo exclusivo (abrir uno cierra el resto) solo cuando las secciones son alternativas mutuamente excluyentes — cerrar lo que el usuario abrió hace 5 segundos es hostil como default.

```html
<!-- IMPLEMENTACIÓN — nativo, cero JS -->
<details class="group border-b">
  <summary class="flex min-h-13 cursor-pointer list-none items-center justify-between py-4 font-medium">
    ¿Puedo cambiar de plan después?
    <svg aria-hidden class="size-4 transition-transform duration-150 group-open:rotate-180"><!-- chevron --></svg>
  </summary>
  <div class="pb-4 text-sm text-muted">Sí — el cambio se prorratea en la siguiente factura.</div>
</details>
```

- ❌ Errores de IA: `<div onClick>` como header sin botón real; chevron que no indica estado; reconstruir en JS lo que `<details>` da gratis para un FAQ simple.

---

## 8. Tabs

### 8.1 Tabs vs navegación de página

**[REQUIRED]** Decidir primero cuál de los dos es:

- **Tabs reales** (`role="tablist"`): alternan vistas del **mismo contexto sin cambiar de URL** — ej. "Vista previa / Código" dentro de un editor. Estado local.
- **Navegación con aspecto de tabs**: cada "tab" es una **URL propia** (settings/general, settings/seguridad) → son `<a>` dentro de `<nav>`, con `aria-current="page"` en el activo — **sin** roles de tab. Aplica `FRONTEND_NAVIGATION_PATTERNS.md`.

**Por qué:** si el contenido merece ser compartible, recargable o volver con el botón atrás, es navegación — los roles de tab romperían el modelo (el lector anuncia "pestaña" pero el navegador cambia de página). La heurística: ¿querrías mandar ese estado por link? → navegación.

### 8.2 Anatomía

**[REQUIRED]** Variante por defecto (subrayada, estilo Stripe/Linear): fila de tabs de 40px de alto, texto 14px medium, gap 16-24px entre tabs, línea base de 1px en todo el ancho, e **indicador activo de 2px** en `brand` sobre la línea base. Tab activo a contraste completo; inactivos en muted con hover que sube el contraste. Variante "pills" (fondo redondeado en el activo) para grupos cortos tipo segmented control.

### 8.3 ARIA y teclado

**[REQUIRED]** `role="tablist"` en el contenedor; cada tab `role="tab"` + `aria-selected` + `aria-controls="panel-id"`; panel `role="tabpanel"` + `aria-labelledby`. **Foco roving:** solo el tab activo tiene `tabindex="0"`, el resto `-1` — `Tab` entra al tablist una sola vez y salta directo al panel; `←`/`→` mueven entre tabs (con wrap en los extremos). **[RECOMMENDED]** Activación automática al mover con flechas si el cambio de panel es instantáneo; activación manual (flechas mueven foco, `Enter` activa) si cada panel dispara una carga.

```tsx
// IMPLEMENTACIÓN (estructura mínima)
<div role="tablist" aria-label="Vista" className="flex gap-6 border-b">
  <button role="tab" aria-selected={active === "preview"} aria-controls="panel-preview"
    tabIndex={active === "preview" ? 0 : -1}
    className={active === "preview" ? "h-10 border-b-2 border-brand-600 text-sm font-medium" : "h-10 text-sm text-muted"}>
    Vista previa
  </button>
  {/* ... */}
</div>
<div id="panel-preview" role="tabpanel" aria-labelledby="tab-preview">…</div>
```

- ❌ Errores de IA: roles de tab sobre links con URL (o viceversa); todos los tabs con `tabindex=0` (el usuario de teclado tabula por cada tab para llegar al contenido); sin navegación por flechas; indicador activo comunicado solo por color de texto sin subrayado/peso.

---

## 9. Progress / Skeleton / Spinner

### 9.1 Matriz de decisión

**[REQUIRED]** El indicador se elige por el tipo de espera, no por gusto (extiende `FRONTEND_STATES_PATTERNS.md` sección 1):

| Situación | Indicador |
|---|---|
| Primera carga de contenido con layout conocido (lista, tabla, card, página) | **Skeleton** |
| Acción puntual del usuario (submit, refresh de un widget, ítem de menú) | **Spinner** (en el control que la disparó, ver Button loading en `FRONTEND_FORM_CONTROLS_STANDARD.md` 2.3) |
| Proceso con % real conocido (upload, export, import, wizard) | **Progress bar determinada** — nunca un spinner si el % existe |
| Proceso largo sin % (>2-3s) | Progress indeterminada o spinner + texto de qué está pasando |

### 9.2 Skeleton

**[REQUIRED]** El skeleton tiene **las dimensiones del contenido real** que va a reemplazar — misma altura de fila, mismo ancho aproximado de columnas, mismo espacio de imagen. Objetivo real: CLS ≈ 0 (Core Web Vitals, `FRONTEND_ENGINEERING_STANDARD.md` 11.4) — si al llegar los datos el layout salta, el skeleton midió mal.

**[RECOMMENDED]** Bloques con radio 4-6px en tono neutral muted, animación `pulse` sutil (o shimmer), 1.5-2s de ciclo; cantidad de filas skeleton ≈ las que se esperan (3-8), no una sola barra genérica. Respetar `prefers-reduced-motion` (ver `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 8).

### 9.3 Spinner

**[REQUIRED]** Tamaños: 16px (dentro de botones/inputs), 20px (widgets), 24px (secciones). Track circular de 2px con arco en `brand` girando ~0.8-1s lineal. Con `role="status"` + texto accesible ("Cargando…" visible o `sr-only`) — un spinner mudo no existe para lector de pantalla.

### 9.4 Progress bar

**[REQUIRED]** Altura 4-8px, radio full, track neutral + relleno `brand`; `role="progressbar"` + `aria-valuemin/max/now` (omitir `aria-valuenow` = indeterminada). **[RECOMMENDED]** % o descripción textual visible junto a la barra en procesos largos ("Subiendo 3 de 12…"). La barra **nunca retrocede**; si el total cambia, se recalcula sin animar hacia atrás.

```tsx
// IMPLEMENTACIÓN — skeleton de una fila de lista con las medidas de la fila real (h-16, avatar 32px)
<div role="status" aria-label="Cargando contactos" className="divide-y">
  {Array.from({ length: 5 }).map((_, i) => (
    <div key={i} className="flex h-16 animate-pulse items-center gap-3 px-4">
      <div className="size-8 rounded-full bg-neutral-200" />
      <div className="flex-1 space-y-2">
        <div className="h-3.5 w-1/3 rounded bg-neutral-200" />
        <div className="h-3 w-1/2 rounded bg-neutral-100" />
      </div>
    </div>
  ))}
</div>

// Progress determinada — el % existe, se usa
<div role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct}
  className="h-1.5 w-full overflow-hidden rounded-full bg-neutral-200">
  <div className="h-full rounded-full bg-brand-600 transition-[width] duration-200" style={{ width: `${pct}%` }} />
</div>
```

- ❌ Errores de IA: spinner gigante centrado reemplazando una tabla (ya prohibido en `FRONTEND_TABLE_PATTERNS.md` 8); skeleton de 3 barritas genéricas que no miden lo que llega (CLS); upload con spinner teniendo el % disponible; spinner sin `role="status"`.

---

## 10. Pagination

Cuándo paginación vs scroll infinito: ya resuelto en `FRONTEND_TABLE_PATTERNS.md` sección 3 (numerada en back-office, infinito solo en feeds) — se hereda. Aquí, el componente:

**Anatomía [REQUIRED]:** botones de página de 32-40px (cuadrados, alineados con la escala de `FRONTEND_FORM_CONTROLS_STANDARD.md` 1.2), "Anterior"/"Siguiente" siempre presentes (disabled en los extremos, no ocultos — que no salte el layout), página actual con fondo `brand` o borde marcado. Con muchas páginas: primera + vecinas de la actual + última, con elipsis (`…` no clicable): `1 … 4 [5] 6 … 20`.

**[REQUIRED]** Contenedor `<nav aria-label="Paginación">`; cada página es link o botón con su número como texto; la actual con `aria-current="page"`; prev/next con `aria-label` ("Página anterior") si son solo íconos.

**[RECOMMENDED]** Mostrar el contexto "Mostrando 21-40 de 213" junto al control; en mobile, colapsar a prev/next + "Página 5 de 20".

- ❌ Errores de IA: renderizar los 200 números; ocultar prev en la página 1 (salto de layout); páginas como `<span onClick>`; sin `aria-current`.

---

## 11. Breadcrumb

Cuándo (jerarquías de 3+ niveles): `FRONTEND_NAVIGATION_PATTERNS.md` sección 6 — se hereda.

**Anatomía [REQUIRED]:** `<nav aria-label="Breadcrumb">` con `<ol>` horizontal; texto 13-14px; separador (`/` o chevron de 14-16px) con `aria-hidden="true"` — es decorativo, no contenido. Todos los niveles son links **excepto el último** (la página actual): texto plano o link con `aria-current="page"`, a contraste completo mientras los anteriores van en muted.

**[RECOMMENDED]** Con 5+ niveles o en mobile: colapsar los intermedios en un ítem "…" que abre un dropdown (sección 3) con los niveles ocultos — no dejar que el breadcrumb haga wrap a dos líneas.

Datos estructurados (`BreadcrumbList` de schema.org) para SEO: ver `FRONTEND_SEO_STANDARD.md` — no se duplican aquí.

```html
<nav aria-label="Breadcrumb">
  <ol class="flex items-center gap-2 text-sm">
    <li><a href="/productos" class="text-muted hover:text-foreground">Productos</a></li>
    <li aria-hidden="true" class="text-muted">/</li>
    <li aria-current="page" class="font-medium">Teclado MX-500</li>
  </ol>
</nav>
```

- ❌ Errores de IA: el último nivel como link a la misma página sin `aria-current`; separadores leídos por el lector ("slash, slash, slash"); breadcrumb como `<div>` de spans sin nav ni lista.

---

## 12. Date picker / Calendar

**[RECOMMENDED]** `<input type="date">` nativo primero: trae el picker correcto de cada plataforma, teclado y accesibilidad gratis, con la anatomía de Input de `FRONTEND_FORM_CONTROLS_STANDARD.md` sección 3. Un calendario custom solo se justifica con: **rango** de fechas (check-in/check-out), **restricciones visuales** (días deshabilitados/con disponibilidad que el usuario necesita *ver* para elegir), o comparación de dos meses lado a lado.

**Anatomía (custom) [REQUIRED]:** popover (sección 3, variante popover — no menu) con: header de mes/año + flechas prev/next (icon-buttons con `aria-label`), grid de 7 columnas con celdas de 36-40px, hoy marcado con borde o punto, seleccionado con fondo `brand`, días de otro mes en muted, deshabilitados sin hover y no seleccionables. En rango: extremos con fondo sólido, días intermedios con fondo suave continuo.

**[REQUIRED]** Teclado en el grid: flechas mueven por día, `PageUp/Down` por mes, `Home/End` a extremos de semana, `Enter` selecciona, `Esc` cierra devolviendo el foco al input. ARIA: `role="grid"`, celdas `role="gridcell"` + `aria-selected`, fecha completa como nombre accesible de cada celda ("viernes 24 de julio de 2026", no "24").

**[REQUIRED]** El usuario siempre puede **escribir** la fecha en el input además de clicarla en el calendario — un picker que solo acepta clics es lento para fechas lejanas (fecha de nacimiento: ~30 años de flechas).

- ❌ Errores de IA: calendario custom para un solo campo de fecha simple; celdas `<div>` sin teclado; fecha de nacimiento con picker de flechas mes a mes; nombre accesible de celda = solo el número del día.

---

## 13. Timeline

Cuándo (procesos, roadmaps, historiales — no cards numeradas): `FRONTEND_UI_PATTERNS.md` sección 2 — se hereda.

**Anatomía [REQUIRED]:** lista vertical `<ol>` (el orden es la información — no `<ul>` ni divs): marcador circular de 8-12px por ítem (en token semántico si comunica estado: `success` completado, `brand` actual, neutral pendiente) + línea conectora vertical de 2px en neutral entre marcadores + contenido con gap de 12-16px al marcador y 24-32px entre ítems. Timestamp en 12-13px muted, alineado consistente (arriba del contenido o en columna izquierda).

**[RECOMMENDED]** El estado del marcador acompaña con ícono (check en completados), no solo color (regla anti-solo-color); ítem actual puede enfatizarse con anillo. Para historiales largos, "Mostrar más" al final — no las 400 entradas de una vez.

```tsx
// IMPLEMENTACIÓN — ol con marcador + línea conectora
<ol className="space-y-6">
  {events.map((ev, i) => (
    <li key={ev.id} className="relative flex gap-4">
      {i < events.length - 1 && (
        <span aria-hidden className="absolute left-[5px] top-4 h-full w-0.5 bg-neutral-200" />
      )}
      <span className={`mt-1 size-3 shrink-0 rounded-full ${ev.done ? "bg-success" : "bg-neutral-300"}`} />
      <div>
        <p className="text-sm font-medium">{ev.title} {ev.done && <CheckIcon aria-label="Completado" className="inline size-3.5 text-success" />}</p>
        <time dateTime={ev.date} className="text-xs text-muted">{formatDate(ev.date)}</time>
      </div>
    </li>
  ))}
</ol>
```

- ❌ Errores de IA: timeline como cards en grid perdiendo la línea de conexión; `<div>`s sin lista ordenada; estado solo por color del punto.

---

## 14. Divider semántico

**[REQUIRED]** Distinguir dos casos:

- **Separación temática real** (entre secciones de contenido): `<hr>` — tiene semántica de separador nativa. Estilo: 1px, token de borde neutral, margen vertical de la escala de espaciado (16/24/32px según densidad).
- **Separación puramente visual** (entre celdas, dentro de un card): `border-*` de CSS en el contenedor — sin elemento extra que ensucie el DOM ni el árbol de accesibilidad.

Dentro de un `role="menu"`: `role="separator"` (sección 3.2). **[RECOMMENDED]** Divider con label ("o", "Hoy") : texto centrado de 12-13px muted con línea a cada lado — el texto es contenido real, no decorado, así que vive en el DOM como texto (patrón ya usado en `FRONTEND_AUTH_PATTERNS.md` para "o continúa con").

- ❌ Errores de IA: `<hr>` entre cada par de elementos "para que respire" (el espaciado de la escala 1.1 ya resuelve el ritmo — el divider se reserva para cortes temáticos reales); divs de 1px de alto en vez de `<hr>` donde sí hay corte temático.

---

## Checklist rápido

- [ ] Overlays: ¿capa de la escala de elevación, offset 4-8px, flip en colisión, `Esc` cierra, foco vuelve al trigger?
- [ ] Tooltip: ¿delay 300-500ms, abre con foco de teclado, nada esencial solo ahí, sin interactivos dentro, omitido en mobile?
- [ ] ¿Dropdown menu (`role="menu"` + flechas) solo para listas de acciones — nunca sobre popovers con contenido/formularios?
- [ ] Command palette: ¿Cmd/Ctrl+K, fuzzy, grupos, contrato combobox con foco en el input, recientes con input vacío?
- [ ] Badge = solo lectura con texto (no solo color); ¿chip removible solo cuando quitar es acción real, con "×" accesible?
- [ ] Avatar: ¿fallback de iniciales con color determinístico, stacking con anillo y "+N"?
- [ ] Accordion: ¿`details/summary` nativo primero; custom con button + `aria-expanded`?
- [ ] Tabs: ¿roles tablist/tab/tabpanel + foco roving + flechas — o links con `aria-current` si cada tab es una URL?
- [ ] ¿Skeleton para primera carga (a tamaño real — CLS ≈ 0), spinner para acciones, progress cuando hay % real?
- [ ] Pagination: ¿nav + `aria-current="page"`, prev/next siempre presentes, elipsis con muchas páginas?
- [ ] Breadcrumb: ¿`nav aria-label` + `ol`, separadores `aria-hidden`, último ítem con `aria-current`?
- [ ] Date picker: ¿nativo primero; custom solo por rango/restricciones, con teclado de grid completo y entrada tipeable?
- [ ] Timeline: ¿`<ol>` con marcadores + línea, estado no solo por color?
- [ ] ¿`<hr>` solo en cortes temáticos reales; bordes CSS para lo puramente visual?
