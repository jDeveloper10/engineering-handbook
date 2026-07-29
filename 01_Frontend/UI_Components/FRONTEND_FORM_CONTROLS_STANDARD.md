---
title: "Estándar de Controles de Formulario"
category: 01_Frontend
doc_type: estandar
tags: [frontend, componentes, formularios, accesibilidad]
summary: "Reglas transversales a todo control y especificación de cada uno: button, input, textarea, select nativo frente a custom, checkbox, radio, switch y combobox con autocompletado."
keywords: [button, input, textarea, select, checkbox, radio, switch, combobox, autocomplete]
updated: 2026-07-27
status: current
---

# FRONTEND FORM CONTROLS STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1: secciones 01 tokens, 04 Component Rules, 09 Forms Rules, 13 Accessibility). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Este documento define la **anatomía exacta** (medidas, estados, ARIA) de cada control de entrada, para que un componente generado por una IA salga con proporciones y comportamiento de nivel Stripe/Linear de serie — no un botón genérico con padding improvisado. Complementa, no repite: la validación de formularios vive en `FRONTEND_ENGINEERING_STANDARD.md` sección 09; los estados obligatorios (default/hover/focus-visible/active/disabled/loading) los exige la sección 1.6 — aquí se definen los **valores concretos** de cada estado por componente. Contrastado contra WAI-ARIA Authoring Practices, Apple HIG y los sistemas de Stripe/Linear/Radix.

---

## 1. Reglas transversales a todo control

### 1.1 Focus ring único

**[REQUIRED]** Todos los controles comparten el mismo indicador de foco: anillo de 2px, separado 2px del borde del control (offset), en el color de marca, con contraste ≥3:1 contra el fondo. Nunca `outline: none` sin este reemplazo (hereda `FRONTEND_ENGINEERING_STANDARD.md` 13.3).

**Por qué:** un foco consistente es lo que hace que una app se sienta "de sistema" al navegar con teclado; cada control con su propio estilo de foco se percibe como piezas pegadas.

**Implementación (Tailwind):** `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2`

### 1.2 Alturas alineadas entre controles

**[REQUIRED]** Controles que conviven en la misma fila (input + botón, select + botón) usan la **misma altura** de la escala: 32 / 40 / 48px. El tamaño base de toda la app es 40px.

**Por qué:** un input de 42px junto a un botón de 40px se ve "casi bien" — que es peor que mal, porque el ojo detecta el desalineo sin poder nombrarlo. Es el error más frecuente en UI generada por IA.

### 1.3 Transiciones

**[RECOMMENDED]** Cambios de estado (hover, focus) transicionan en 100-150ms con `ease-out` — hereda la escala de [FRONTEND_MOTION_STANDARD.md](FRONTEND_MOTION_STANDARD.md) sección 2. Solo se transicionan `color`, `background-color`, `border-color`, `box-shadow`, `opacity` — nunca `width`/`height` en estados (causa layout shift).

### 1.4 Touch target

**[REQUIRED]** Área táctil mínima de 44×44px en mobile para todo control, aunque el elemento visual sea menor (checkbox de 16px con padding táctil hasta 44px) — hereda [FRONTEND_RESPONSIVE_STANDARD.md](../Core/FRONTEND_RESPONSIVE_STANDARD.md) sección 5.

### 1.5 Elemento nativo primero

**[REQUIRED]** `<button>`, `<input>`, `<select>`, `<textarea>` nativos antes que reconstrucciones con `<div>` — hereda [FRONTEND_ACCESSIBILITY_STANDARD.md](FRONTEND_ACCESSIBILITY_STANDARD.md) sección 5 ("no ARIA es mejor que ARIA mal usado"). Este documento marca explícitamente el punto en que un control custom se justifica (ver Select, sección 4).

---

## 2. Button

### 2.1 Anatomía

**[REQUIRED]** Tres tamaños, ningún valor fuera de esta tabla:

| Tamaño | Altura | Padding horizontal | Texto | Ícono | Gap ícono-texto | Radio |
|---|---|---|---|---|---|---|
| `sm` | 32px | 12px | 14px medium | 16px | 6px | 6px |
| `md` (default) | 40px | 16px | 14px medium | 16px | 8px | 8px |
| `lg` | 48px | 20px | 16px medium | 20px | 8px | 8px |

- Icon-button (solo ícono): **cuadrado**, mismo alto que el tamaño (32×32 / 40×40 / 48×48), ícono centrado.
- El texto no hace wrap: un botón es una línea; si el texto no cabe, el texto es demasiado largo (ver [FRONTEND_MICROCOPY_STANDARD.md](FRONTEND_MICROCOPY_STANDARD.md)).

**Implementación (Tailwind, md):** `h-10 px-4 rounded-lg text-sm font-medium inline-flex items-center justify-center gap-2`

### 2.2 Estados obligatorios

**[REQUIRED]** Valores concretos (ejemplo sobre variante primary; el patrón — oscurecer un paso al hover, otro al presionar — aplica a todas):

| Estado | Valor |
|---|---|
| `default` | Fondo token `brand-600`, texto blanco |
| `hover` | Fondo un paso más oscuro (`brand-700`), transición 150ms |
| `focus-visible` | Ring de la sección 1.1 (el hover NO es el indicador de foco) |
| `active` | Fondo dos pasos más oscuro (`brand-800`); opcional `scale(0.98)` |
| `disabled` | Opacidad 50%, `cursor: not-allowed`, sin reaccionar a hover |
| `loading` | Spinner de 16px, interacción bloqueada, **ancho intacto** (ver 2.3) |

### 2.3 Loading sin cambiar de ancho

**[REQUIRED]** Un botón en estado loading conserva exactamente su ancho: el label se vuelve invisible (no se desmonta) y el spinner se superpone centrado — nunca reemplazar el texto por el spinner en el flujo.

**Por qué:** si el ancho cambia, todo lo que está al lado del botón salta (layout shift) justo en el momento en que el usuario está mirando ahí. Es la diferencia visible entre un producto pulido y uno genérico.

```tsx
// IMPLEMENTACIÓN (React + Tailwind)
<button disabled={loading} aria-busy={loading} className="relative ...">
  <span className={loading ? "invisible" : undefined}>Guardar cambios</span>
  {loading && <Spinner className="absolute inset-0 m-auto size-4" />}
</button>
```

### 2.4 Variantes — jerarquía

**[REQUIRED]** Máximo **1 botón primary visible por vista** (pantalla, modal o sección de formulario). Si dos acciones "parecen" primarias, una de las dos no lo es.

**Por qué:** el primary le dice al usuario "esta es la acción esperada aquí". Dos primaries compitiendo anulan esa señal — el resultado es una pantalla donde todo grita y nada guía.

| Variante | Apariencia | Cuándo |
|---|---|---|
| `primary` | Fondo sólido `brand` | La acción principal de la vista (Guardar, Continuar, Crear) |
| `secondary` | Borde 1px + fondo superficie | Acciones frecuentes no principales (Cancelar, Exportar) |
| `ghost` | Sin borde; fondo solo al hover | Acciones terciarias, toolbars, acciones por fila de tabla |
| `destructive` | Fondo sólido `danger` | Solo la confirmación final de una acción destructiva (dentro del modal de `FRONTEND_MODALS_PATTERNS.md` sección 4); el trigger que abre esa confirmación es secondary/ghost con texto `danger` |
| `link` | Texto con estilo de enlace | Acción menor dentro de texto corrido |

**Implementación (variantes declarativas, hereda `FRONTEND_ENGINEERING_STANDARD.md` 10.3):**

```tsx
// Un solo componente Button con mapas de variante/tamaño — nunca clases sueltas repetidas
const sizes = {
  sm: "h-8 px-3 text-sm gap-1.5 rounded-md",
  md: "h-10 px-4 text-sm gap-2 rounded-lg",
  lg: "h-12 px-5 text-base gap-2 rounded-lg",
};
const variants = {
  primary: "bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800",
  secondary: "border border-neutral-300 bg-surface hover:bg-neutral-50 active:bg-neutral-100",
  ghost: "hover:bg-neutral-100 active:bg-neutral-200",
  destructive: "bg-danger text-white hover:bg-danger/90",
};
```

### 2.5 Accesibilidad

- **[REQUIRED]** `<button>` real, con `type` explícito: `type="button"` por defecto, `type="submit"` solo en el submit del formulario. (Sin `type`, un botón dentro de `<form>` es submit implícito — bug clásico de IA: un botón "Cancelar" que envía el formulario.)
- **[REQUIRED]** Todo icon-button lleva `aria-label` descriptivo de la acción ("Eliminar filtro", no "ícono de X") — hereda [FRONTEND_ICON_SYSTEM_STANDARD.md](FRONTEND_ICON_SYSTEM_STANDARD.md) sección 3.
- **[RECOMMENDED]** En loading, `aria-busy="true"` y el nombre accesible se conserva (por eso el label se oculta con `visibility`, no se desmonta).
- **[RECOMMENDED]** Para botones deshabilitados que el usuario necesita entender *por qué* lo están, preferir `aria-disabled="true"` + bloquear el handler en vez de `disabled` (que los saca del orden de tabulación y los vuelve invisibles para lector de pantalla).

### 2.6 Errores comunes de IA

- ❌ `<div onClick>` como botón (pierde teclado, foco y semántica gratis).
- ❌ Botón sin `type` dentro de un formulario.
- ❌ Primary para todas las acciones de la pantalla.
- ❌ Spinner que reemplaza el texto y encoge el botón.
- ❌ Icon-button sin `aria-label`.
- ❌ Alturas inventadas (38px, 42px) que no alinean con los inputs vecinos.

---

## 3. Input / Textarea

### 3.1 Anatomía

**[REQUIRED]** Estructura vertical de un campo, de arriba hacia abajo:

```
Label            14px medium, margen inferior 6px
[ Control ]      altura 40px, padding horizontal 12px, borde 1px, radio 8px, texto 14px
Helper / Error   texto 12-14px, margen superior 6px
```

- Ícono decorativo dentro del input: 16px, a 12px del borde; el padding del lado del ícono sube a 36-40px.
- **[REQUIRED]** En mobile el texto del input es ≥16px — iOS hace zoom automático sobre inputs con texto menor, rompiendo el layout.
- Textarea: mismas reglas, altura mínima 80px (~3 líneas), `resize: vertical` únicamente (resize horizontal rompe el layout de la columna).
- **[RECOMMENDED]** El espacio del mensaje de error se reserva (min-height en el contenedor del helper) o se acepta el empuje — pero nunca un error que se superpone al siguiente campo.

**Implementación (Tailwind):** `h-10 px-3 rounded-lg border border-neutral-300 text-sm md:text-sm text-base`

### 3.2 Estados obligatorios

**[REQUIRED]**

| Estado | Valor |
|---|---|
| `default` | Borde neutral (contraste ≥3:1 contra el fondo), fondo superficie |
| `hover` | Borde un paso más oscuro |
| `focus` | Borde `brand` + ring de la sección 1.1 (en inputs el foco por clic también se muestra: usar `focus`, no solo `focus-visible`) |
| `disabled` | Fondo muted, texto atenuado, `cursor: not-allowed` |
| `readonly` | Fondo muted pero texto a contraste completo (se puede leer y copiar) — visualmente distinto de disabled |
| `error` | Ver 3.3 |

### 3.3 Estado de error: borde + ícono + mensaje

**[REQUIRED]** Un campo inválido comunica el error por **tres canales**: borde en token `danger` + ícono de error dentro o junto al campo + mensaje de texto debajo. Nunca solo el cambio de color.

**Por qué:** ~8% de los hombres tiene alguna forma de daltonismo — un borde que pasó de gris a rojo puede ser literalmente invisible para ellos. El ícono y el texto son los canales redundantes que exige WCAG 1.4.1 (no comunicar solo con color).

```tsx
// IMPLEMENTACIÓN
<label htmlFor="email" className="text-sm font-medium">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error"
  className="h-10 border-danger pr-9 ..." />
<p id="email-error" className="mt-1.5 flex items-center gap-1 text-sm text-danger">
  <AlertCircleIcon aria-hidden className="size-4" /> Ingresa un email válido
</p>
```

### 3.4 Variantes

- Con ícono decorativo (búsqueda, email) — el ícono lleva `aria-hidden`.
- Con prefijo/sufijo fijo (`https://`, `.com`, `$`): bloque adosado con fondo muted, misma altura, un solo borde continuo.
- Con acción embebida (mostrar/ocultar contraseña): icon-button de 32px dentro del input de 40px — con su `aria-label` (regla 2.5).

### 3.5 Accesibilidad

- **[REQUIRED]** Todo input tiene `<label>` visible asociado por `htmlFor`/`id`. El placeholder **no** es el label: desaparece al escribir y su contraste típico no cumple AA. Placeholder solo para formato de ejemplo (`nombre@empresa.com`).
- **[REQUIRED]** Error: `aria-invalid="true"` + `aria-describedby` apuntando al id del mensaje (ver 3.3) — así el lector de pantalla anuncia el error al enfocar el campo.
- **[RECOMMENDED]** `autocomplete` correcto (`email`, `current-password`, `name`) e `inputmode` en campos numéricos (`inputmode="numeric"` para códigos) — teclado correcto en mobile.

### 3.6 Errores comunes de IA

- ❌ Placeholder como único label.
- ❌ Error comunicado solo con borde rojo.
- ❌ Mensaje de error sin `aria-describedby` (visible pero mudo para lector de pantalla).
- ❌ Texto de 14px en mobile (zoom forzado de iOS).
- ❌ `resize` libre en textarea rompiendo la columna del formulario.

---

## 4. Select — nativo vs custom

### 4.1 Cuándo cada uno

**[REQUIRED]** `<select>` nativo por defecto. Un select custom (listbox propio) solo se justifica cuando se necesita al menos una de estas capacidades, que el nativo no tiene:

1. Búsqueda/filtrado dentro de las opciones (→ en realidad es un Combobox, sección 6).
2. Selección múltiple usable (el `<select multiple>` nativo es inusable en la práctica).
3. Render rico en las opciones (avatares, íconos, descripciones de dos líneas).

**Por qué:** el nativo trae gratis teclado, lector de pantalla, y el picker correcto en cada plataforma (rueda en iOS, lista en Android). Un custom reconstruye todo eso a mano — y la versión IA típica reconstruye solo el clic, dejando teclado y mobile rotos. El costo del custom solo se paga cuando compra una capacidad real.

### 4.2 Anatomía (nativo estilizado)

**[REQUIRED]** Mismas medidas que Input (altura 40px, padding 12px, radio 8px). Se estiliza quitando la apariencia por defecto y agregando chevron propio de 16px a 12px del borde derecho — el elemento sigue siendo `<select>`.

```tsx
// IMPLEMENTACIÓN
<div className="relative">
  <select className="h-10 w-full appearance-none rounded-lg border px-3 pr-9 text-sm">
    <option>Opción A</option>
  </select>
  <ChevronDownIcon aria-hidden className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2" />
</div>
```

### 4.3 Estados, accesibilidad y errores

- Estados: los mismos de Input (3.2), incluido error por tres canales (3.3).
- Custom: `role="listbox"` + `role="option"` + `aria-selected`, trigger con `aria-expanded` y `aria-haspopup="listbox"`, navegación con flechas + Enter + Esc, tipeo salta a la opción (type-ahead). Si esto suena a mucho trabajo, es la señal de volver al nativo.
- ❌ Error de IA: dropdown custom de `<div>`s para 5 opciones planas, sin teclado ni type-ahead — todo costo, ninguna capacidad nueva.

---

## 5. Checkbox / Radio / Switch

### 5.1 La distinción semántica (la que las IAs mezclan)

**[REQUIRED]**

| Control | Semántica | Efecto |
|---|---|---|
| Radio | Elegir **exactamente una** opción de un grupo **visible** (2-5 opciones; con 6+ usar Select) | Se aplica al enviar el formulario |
| Checkbox | Selección **múltiple**, o un booleano dentro de un formulario (acepto términos) | Se aplica al enviar el formulario |
| Switch | Booleano con **efecto inmediato** — al accionarlo, el cambio ya ocurrió, sin botón Guardar | Inmediato |

**Por qué:** el switch hereda su significado del interruptor físico: accionar = hecho. Un switch que además requiere "Guardar cambios" miente dos veces (parece aplicado y no lo está; y al salir sin guardar se pierde en silencio). Inversamente, un checkbox que dispara un efecto inmediato sorprende — el usuario esperaba marcarlo y confirmar después. Si la pantalla tiene botón de guardar → checkbox; si no lo tiene → switch.

### 5.2 Anatomía

**[REQUIRED]**

| Control | Medidas |
|---|---|
| Checkbox | Caja de 16×16px, radio 4px, check de 12px; gap al label 8px |
| Radio | Círculo de 16×16px; punto interior de 8px al seleccionar; gap al label 8px |
| Switch | Track de 36-44×20-24px totalmente redondeado; thumb circular 4px menor que el alto del track, desplazamiento animado 100-150ms |

- **[REQUIRED]** Touch target de 44px en mobile (regla 1.4): el `<label>` envuelve control + texto y el padding del label completa el área — el usuario toca el texto, no caza la caja de 16px.
- Grupo vertical: gap de 12px entre opciones; el label de cada opción es clicable siempre.

### 5.3 Estados obligatorios

**[REQUIRED]** `default` (borde neutral, fondo superficie) / `hover` (borde más oscuro) / `focus-visible` (ring 1.1) / `checked` (fondo `brand`, marca blanca) / `disabled` (opacidad 50%, también sobre el label) / checkbox además soporta `indeterminate` (raya horizontal — para "seleccionar todos" parcial en tablas, ver `FRONTEND_TABLE_PATTERNS.md` sección 5).

### 5.4 Accesibilidad

- **[REQUIRED]** Checkbox y radio son `<input type="checkbox|radio">` nativos (visualmente ocultos con `appearance-none` o `sr-only` + caja dibujada, pero el input existe y recibe el foco).
- **[REQUIRED]** Un grupo de radios va dentro de `<fieldset>` con `<legend>` (la pregunta del grupo); comparten `name`. Flechas mueven la selección dentro del grupo — comportamiento nativo, gratis.
- **[REQUIRED]** Switch: `<button role="switch" aria-checked>` (o input checkbox con `role="switch"`). Se acciona con Space/Enter. Su label indica el estado encendido ("Notificaciones por email"), y **el cambio se confirma** con feedback si la operación es remota (toast de `FRONTEND_NOTIFICATIONS_PATTERNS.md`, o revert visual + error si falla).

**Implementación (grupo de radios + switch):**

```tsx
// Radio group — fieldset con legend, label clicable de 44px en mobile
<fieldset className="space-y-3">
  <legend className="text-sm font-medium">Frecuencia de facturación</legend>
  {opciones.map((op) => (
    <label key={op.id} className="flex min-h-11 cursor-pointer items-center gap-2 md:min-h-0">
      <input type="radio" name="billing" value={op.id} className="size-4 accent-brand-600" />
      <span className="text-sm">{op.label}</span>
    </label>
  ))}
</fieldset>

// Switch — efecto inmediato, con revert si la operación remota falla
<button role="switch" aria-checked={enabled} onClick={toggle}
  className={`h-6 w-11 rounded-full p-0.5 transition-colors duration-150
    ${enabled ? "bg-brand-600" : "bg-neutral-300"}`}>
  <span className={`block size-5 rounded-full bg-white transition-transform duration-150
    ${enabled ? "translate-x-5" : ""}`} />
</button>
```

### 5.5 Errores comunes de IA

- ❌ Switch dentro de un formulario con botón "Guardar" (o checkbox con efecto inmediato) — la confusión #1.
- ❌ Radios para selección múltiple, o checkboxes donde solo una opción es válida.
- ❌ `<div>` pintado como checkbox sin input real detrás.
- ❌ Touch target = solo la caja de 16px en mobile.
- ❌ Radios sin `fieldset`/`legend`: el lector de pantalla lee opciones sueltas sin la pregunta.

---

## 6. Autocomplete / Combobox

### 6.1 Anatomía

**[REQUIRED]** Input de texto (anatomía de la sección 3, altura 40px) + panel flotante:

- Panel: mismo ancho que el input (mínimo), radio 8px, elevación de dropdown (ver [FRONTEND_ELEVATION_STANDARD.md](FRONTEND_ELEVATION_STANDARD.md)), separado 4px del input, altura máxima 240-320px con scroll interno.
- Opción: altura 32-36px, padding horizontal 12px, la opción resaltada (por flechas o hover) con fondo muted — **una sola** opción resaltada a la vez.
- El texto que coincide con lo tecleado **[RECOMMENDED]** se resalta en bold dentro de cada opción.

### 6.2 Comportamiento

- **[REQUIRED]** Con 0 resultados el panel muestra un mensaje explícito ("Sin resultados para 'x'", + acción de crear si el flujo lo permite: "Crear 'x'") — nunca un panel vacío ni un panel que se cierra en silencio, que el usuario lee como "está roto".
- **[RECOMMENDED]** Búsqueda remota: debounce de 200-300ms y estado de carga visible dentro del panel (spinner de 16px o skeleton de opciones) — no congelar la lista anterior sin señal.
- **[RECOMMENDED]** Al abrir con valor ya seleccionado, la opción seleccionada aparece marcada (check de 16px a la derecha).

### 6.3 Accesibilidad — el contrato ARIA completo

**[REQUIRED]** Este es el patrón ARIA compuesto más fácil de romper; el contrato mínimo:

```html
<input role="combobox" aria-expanded="true|false" aria-controls="listbox-id"
       aria-autocomplete="list" aria-activedescendant="opcion-activa-id" />
<ul id="listbox-id" role="listbox">
  <li id="op-1" role="option" aria-selected="false">…</li>
</ul>
```

**[REQUIRED]** Teclado: `↓`/`↑` mueven el resaltado (el foco del DOM **permanece en el input** — se comunica con `aria-activedescendant`), `Enter` selecciona, `Esc` cierra sin seleccionar (segunda pulsación limpia el input), `Tab` cierra y avanza. Escribir filtra siempre.

```tsx
// IMPLEMENTACIÓN (esqueleto de comportamiento; Radix/Headless UI/cmdk lo traen resuelto)
<div className="relative">
  <input role="combobox" aria-expanded={open} aria-controls="opts" aria-autocomplete="list"
    aria-activedescendant={activeId} value={query} onChange={onQuery} onKeyDown={onKeys}
    className="h-10 w-full rounded-lg border px-3 text-sm" />
  {open && (
    <ul id="opts" role="listbox"
      className="absolute top-full mt-1 max-h-80 w-full overflow-auto rounded-lg border bg-surface p-1 shadow-lg">
      {results.length === 0 && <li className="px-3 py-2 text-sm text-muted">Sin resultados para "{query}"</li>}
      {results.map((r) => (
        <li key={r.id} id={`op-${r.id}`} role="option" aria-selected={r.id === selectedId}
          className={`flex h-9 items-center rounded-md px-3 text-sm ${r.id === activeId ? "bg-neutral-100" : ""}`}>
          {r.label}
        </li>
      ))}
    </ul>
  )}
</div>
```

### 6.4 Errores comunes de IA

- ❌ Mover el foco del DOM a las opciones (el usuario pierde el cursor de texto).
- ❌ Panel vacío o cerrado en silencio con 0 resultados.
- ❌ `aria-expanded` que nunca se actualiza, o listbox sin `role="option"` en los ítems.
- ❌ Filtrar en remoto sin debounce (una request por tecla).

---

## 7. Slider

**[REQUIRED]** Solo para valores donde la precisión exacta no importa (volumen, brillo, rango de precios aproximado). Si el usuario necesita un número exacto, el slider se acompaña de un input numérico sincronizado o se usa solo el input.

**Anatomía [REQUIRED]:** track de 4-6px de alto totalmente redondeado, porción recorrida en `brand`, resto en neutral; thumb circular de 16-20px (touch target 44px, regla 1.4); el **valor actual visible** siempre — como texto junto al slider o tooltip sobre el thumb al arrastrar — la posición sola no es información suficiente.

**Estados:** thumb con `hover` (halo suave), `focus-visible` (ring 1.1), `active` (thumb crece a ~110%), `disabled` (opacidad 50%, sin arrastre).

**Accesibilidad [REQUIRED]:** partir de `<input type="range">` (trae teclado y ARIA gratis). Flechas ±1 paso, `PageUp/Down` ±10%, `Home/End` a los extremos. Si es custom: `role="slider"` + `aria-valuemin/max/now` + `aria-valuetext` cuando el número crudo no se entiende ("$1.200", no "1200").

```tsx
// IMPLEMENTACIÓN — nativo estilizado, valor siempre visible
<div>
  <div className="mb-1.5 flex justify-between text-sm">
    <label htmlFor="budget" className="font-medium">Presupuesto mensual</label>
    <output htmlFor="budget" className="tabular-nums">${value.toLocaleString()}</output>
  </div>
  <input id="budget" type="range" min={100} max={5000} step={100} value={value}
    onChange={(e) => setValue(e.target.valueAsNumber)}
    className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-neutral-200 accent-brand-600" />
</div>
```

- ❌ Error de IA: slider para elegir cantidad exacta (ej. "3 asientos") donde un input numérico o stepper es lo correcto; thumb de 12px imposible de agarrar en mobile; valor comunicado solo por la posición del thumb.

---

## 8. File input

Las reglas de flujo de subida (validación de tipo/peso, errores, múltiples archivos) pertenecen a los patrones de formularios — si existe `FRONTEND_FORMS_PATTERNS.md` en esta carpeta, hereda de ahí; mientras no exista, aplica `FRONTEND_ENGINEERING_STANDARD.md` sección 09. Lo específico del **control**:

- **[REQUIRED]** El control real es `<input type="file">` (oculto visualmente si se estiliza); el trigger visible es un Button secondary (sección 2) o una dropzone — nunca un `<div>` sin input detrás (pierde teclado y el picker nativo de mobile).
- **[REQUIRED]** `accept` declarado con los tipos permitidos, y los límites (tipos, peso máximo) escritos como helper text **antes** de elegir el archivo — no como error después.
- **[REQUIRED]** Archivo seleccionado: mostrar nombre + peso + botón de quitar (icon-button con `aria-label="Quitar archivo"`). Durante la subida: barra de progreso real si hay % (ver [FRONTEND_OVERLAY_DISPLAY_STANDARD.md](FRONTEND_OVERLAY_DISPLAY_STANDARD.md) sección Progress).
- **[RECOMMENDED]** Dropzone (área punteada de ~120px de alto, drag & drop) solo cuando subir archivos es tarea central de la pantalla; para un adjunto ocasional, botón simple.

---

## Checklist rápido

- [ ] ¿Focus ring único (2px + offset 2px) en todos los controles, nunca eliminado sin reemplazo?
- [ ] ¿Alturas solo de la escala 32/40/48px, alineadas entre controles vecinos?
- [ ] ¿Touch targets ≥44px en mobile, incluidos checkbox/radio de 16px vía label?
- [ ] Button: ¿máximo 1 primary por vista, `type` explícito, loading sin cambiar ancho, icon-buttons con `aria-label`?
- [ ] Input: ¿label real (no placeholder), error con borde + ícono + mensaje + `aria-invalid`/`aria-describedby`, 16px en mobile?
- [ ] Select: ¿nativo salvo búsqueda/multi/render rico?
- [ ] ¿Radio = una de opciones visibles, checkbox = múltiple/booleano con submit, switch = efecto inmediato sin Guardar?
- [ ] Combobox: ¿contrato ARIA completo, foco en el input, flechas + Enter + Esc, mensaje con 0 resultados?
- [ ] Slider: ¿valor actual visible, `input type="range"` base, solo para valores no exactos?
- [ ] File input: ¿input real detrás del trigger, límites visibles antes, archivo listado con quitar?
- [ ] ¿Todos los estados de 1.6 del estándar principal definidos con los valores concretos de este documento?
