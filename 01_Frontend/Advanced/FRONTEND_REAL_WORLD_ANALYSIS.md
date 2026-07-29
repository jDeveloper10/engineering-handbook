---
title: "Análisis de Design Systems Públicos del Mundo Real"
category: 01_Frontend
tags: [frontend, design-system, analisis, spacing, tipografia]
summary: "Análisis comparado de design systems públicos (Atlassian, Material, otros): por qué la grilla operativa real es de 4px y no de 8, cómo estructuran tipografía, color en tres capas y librerías de componentes."
keywords: [design-system, spacing, grilla-4px, tipografia, tokens, dark-mode, componentes]
updated: 2026-07-27
status: current
---

# FRONTEND REAL WORLD ANALYSIS — Cómo construyen UI los mejores design systems públicos

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) sección 01 y complementa [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md): el catálogo describe *identidades visuales* (qué se ve); este documento analiza *decisiones de sistema* (por qué los productos de referencia se ven profesionales). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> **Método:** análisis de documentación pública oficial (consultada 2026-07-20) de: GitHub Primer, Shopify Polaris, IBM Carbon, Atlassian Design System, Radix (Colors + Primitives), Vercel Geist, Stripe (blog de ingeniería + docs de Stripe Apps) y Linear (blog oficial). Cada afirmación lleva su fuente. Cuando algo no está documentado públicamente, se dice explícitamente ("no documentado — inferido de X") en vez de inventarse.
>
> **Organización:** por decisión de diseño, no por empresa — el lector pregunta "¿cómo se hace un spacing scale?", no "¿qué hace IBM?".

---

## 1. Spacing: todos viven en la grilla de 4px

### Qué hace cada sistema

| Sistema | Base | Escala (px) | Fuente |
|---|---|---|---|
| GitHub Primer | 4px | 2, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 64, 80, 96, 112, 128 | [primer.style/foundations/primitives/size](https://primer.style/foundations/primitives/size) |
| Shopify Polaris | 4px | 0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 112, 128 | [polaris-react.shopify.com/tokens/space](https://polaris-react.shopify.com/tokens/space) |
| IBM Carbon | "múltiplos de 2, 4 y 8" | 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 160 (spacing-01…13) | [carbondesignsystem.com/elements/spacing/overview](https://carbondesignsystem.com/elements/spacing/overview/) |
| Atlassian | 8px (`space.100`), con sub-pasos de 2/4/6 | 0, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80 | [atlassian.design/foundations/spacing](https://atlassian.design/foundations/spacing) |

### Dónde convergen

1. **Nadie usa base 8 pura.** Incluso Atlassian, que declara 8px como unidad, define 2/4/6/12/20 — la grilla operativa real es de 4px (con 2px como excepción mínima). La "base 8" es narrativa; la práctica es base 4.
2. **La escala es densa abajo y rala arriba.** Entre 2 y 24px hay pasos cada 2-4px (donde vive el padding de componentes); a partir de 32px los saltos son de 8-16px (layout). Ningún sistema tiene la misma densidad de pasos en todo el rango.
3. **12px y 20px existen en los 4 sistemas.** No son valores "raros": 12px es el padding interno de componente más usado y 20px un intermedio real entre 16 y 24.
4. **~13-18 pasos totales**, y Atlassian les asigna rangos de uso explícitos: 0-8px para gaps icono-texto y padding compacto, 12-24px para padding de contenedores, 32-80px para separación entre bloques de página ([fuente](https://atlassian.design/foundations/spacing)).
5. **Primer añade una capa semántica de densidad**: `--stack-gap-condensed/normal/spacious` en vez de números crudos en componentes ([fuente](https://primer.style/foundations/primitives/size)).

### Regla extraíble

**[RECOMMENDED]** Escala de espaciado en grilla de 4px con densidad decreciente: `2 4 8 12 16 20 24 32 40 48 64 80 96` — y asignar rangos de uso (≤8 micro-gaps, 12-24 padding de componente, ≥32 layout). Esto **matiza** la escala de 1.1 del estándar de Nivel 1 (`4 8 16 24 32 48 64 96`): los 4 sistemas incluyen 12 y 20; omitirlos empuja a improvisar justo en el rango más usado.

---

## 2. Tipografía: una familia, pocos pesos, line-height en la grilla

### Qué hace cada sistema

| Sistema | Familia | Escala de tamaños | Pesos | Fuente |
|---|---|---|---|---|
| Primer | System stack (+ Mona Sans VF propia) | 12, 14, 16, 20, 32, 40px (xs→2xl); código 13px | 300/400/500/600 | [primer.style/foundations/primitives/typography](https://primer.style/foundations/primitives/typography) |
| Polaris | Inter + system stack | 11, 12, 13, 14, 16, 18, 20, 22, 24, 30, 32, 36, 40px | 450/550/650/700 (variable font) | [polaris-react.shopify.com/tokens/font](https://polaris-react.shopify.com/tokens/font) |
| Carbon | IBM Plex (propia, open source) | Fórmula única desde y₀=12px: `Xn = Xn-1 + {INT[(n-2)/4]+1} × 2` | Light/Regular/SemiBold recomendados | [carbondesignsystem.com/elements/typography/overview](https://carbondesignsystem.com/elements/typography/overview/) |
| Atlassian | Atlassian Sans (propia); Charlie Sans solo marketing | Headings 12-32px (7 niveles); body 12/14/16 con **14 por defecto** | Regular/Medium/Bold | [atlassian.design/foundations/typography](https://atlassian.design/foundations/typography) |
| Vercel Geist | Geist Sans / Geist Mono (propias) | Clases por rol: `heading-72…14`, `copy-24…13`, `button-16/14/12` (cada clase fija size+line-height+letter-spacing+weight juntos; valores numéricos no publicados en la página consultada) | no publicados | [vercel.com/geist/text](https://vercel.com/geist/text) |
| Linear | Inter (body) + Inter Display (headings) | no documentada públicamente | — | [linear.app/blog/how-we-redesigned-the-linear-ui](https://linear.app/blog/how-we-redesigned-the-linear-ui) |

### Dónde convergen

1. **Body de producto denso: 13-14px, no 16.** Atlassian fija 14px como default de body; la escala de Polaris concentra pasos en 12-14; Carbon arranca su fórmula en 12px con set "productive" para tareas. El 16px como body es de sitios de contenido, no de apps de trabajo.
2. **Máximo 3-4 pesos, y los densos evitan el bold 700.** Primer llega hasta semibold 600; Carbon recomienda Light/Regular/SemiBold. El énfasis en UI densa se hace con 500-600, no con 700 (Polaris usa números atípicos 450-650 porque Inter variable les permite calibrar fino).
3. **Line-height alineado a la grilla de 4px.** Primer lo declara explícito: valores sin unidad que "align to the 4px grid" ([fuente](https://primer.style/foundations/typography)); Polaris define line-heights en px fijos múltiplos de 4 (12→48px).
4. **Dos sets según contexto, no una sola escala.** Carbon separa "productive" (denso, tareas) de "expressive" (editorial, responsivo) ([fuente](https://carbondesignsystem.com/elements/typography/overview/)); Geist separa por rol (heading/copy/label/button); Linear separa Inter (body) de Inter Display (headings).
5. **La fuente propia es branding, el fallback es system.** Primer, Carbon, Atlassian, Vercel y Shopify (Inter) cargan una familia con personalidad pero el stack cae a system fonts — nadie depende de la webfont para funcionar.
6. **Tokens tipográficos empaquetados, no sueltos.** Geist y Carbon no exponen "font-size" aislado: cada estilo fija tamaño+line-height+peso+tracking como unidad. Elegir un tamaño y un line-height por separado es un error de sistema.

### Regla extraíble

**[RECOMMENDED]** 1 familia UI (+1 mono si hay código/datos), escala con más pasos entre 12-24px que arriba, body 14px en apps densas (16px solo en contenido largo), pesos 400/500/600 (700 reservado a display/marketing), line-height siempre múltiplo de 4px, y definir estilos completos (tamaño+línea+peso juntos) en vez de tamaños sueltos. Matiza la sección 1.3 del Nivel 1 (que sugiere 400/500/700).

---

## 3. Color: primitivos → semánticos → componente, y dark mode por re-mapeo

### Arquitectura de tokens (los 4 grandes coinciden en 3 capas)

| Sistema | Capa primitiva | Capa semántica | Dark mode | Fuente |
|---|---|---|---|---|
| Primer | Escalas base 0-13 ("never used directly in code") | Funcionales (`fgColor-muted`, `borderColor-*`) + componente (`focus-outlineColor`) | Escala neutral **invertida** en dark: los tokens funcionales no cambian de nombre, cambian su referencia | [primer.style/foundations/color/overview](https://primer.style/foundations/color/overview) |
| Carbon | 10 grados por matiz (10-100) + negro/blanco | Core tokens por rol: `$text-primary`, `$layer`, `$border-subtle` | 4 temas (White, Gray 10, Gray 90, Gray 100); `$text-secondary` mapea a Gray 70 o Gray 30 según tema; en dark cada capa apilada es un paso **más clara** | [carbondesignsystem.com/elements/color/overview](https://carbondesignsystem.com/elements/color/overview/) |
| Polaris | escala interna | `--p-color-[categoría]-[rol]-[estado]`: categorías bg/text/border/icon; roles brand/info/success/caution/warning/critical/magic/inverse; estados hover/active/selected/disabled | vía tokens semánticos | [polaris-react.shopify.com/tokens/color](https://polaris-react.shopify.com/tokens/color) |
| Atlassian | 9 matices saturados + neutrales (ramps separados light/dark) + alpha | `color.[propiedad].[rol].[énfasis].[estado]` — ej. `color.background.brand.bold.hovered` | "Each color design token maps to a different value for each theme" — el desarrollador nunca mapea a mano | [atlassian.design/foundations/color](https://atlassian.design/foundations/color) |

### Los pasos de la escala tienen función asignada, no son decorativos

- **Radix Colors (base de shadcn), 12 pasos por escala:** 1-2 fondos de app, 3-5 fondos de componente (default/hover/pressed), 6-8 bordes (6 no-interactivo, 7 interactivo, 8 fuerte/focus), 9-10 color sólido (9 = máximo croma), 11-12 texto (bajo/alto contraste). Dark mode: alias mutables que re-mapean pasos, no una segunda paleta. [radix-ui.com/colors/docs/palette-composition/understanding-the-scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)
- **Vercel Geist, 10 escalas × 10 pasos:** 100-300 fondos, 400-600 bordes, 700-800 fondos de alto contraste, 900-1000 texto/iconos; P3 donde el display lo soporta. [vercel.com/geist/colors](https://vercel.com/geist/colors)

### Contraste garantizado por construcción, no verificado a mano

- **Stripe** reconstruyó su paleta en espacio **CIELAB** (percepción humana, no RGB) con una regla de emparejamiento: dos colores a **≥5 niveles de distancia garantizan 4.5:1** (texto pequeño) y **≥4 niveles garantizan 3:1** (texto grande/iconos). [stripe.com/blog/accessible-color-systems](https://stripe.com/blog/accessible-color-systems)
- **Linear** migró de HSL a **LCH** y redujo sus variables de tema de **98 a 3** (color base, acento, contraste) — el sistema deriva todo lo demás, incluidos temas de alto contraste automáticos. [linear.app/blog/how-we-redesigned-the-linear-ui](https://linear.app/blog/how-we-redesigned-the-linear-ui)

### Cuántos grises usan de verdad

Primer: 14 pasos neutrales (0-13). Carbon: 10 grados de gris + negro/blanco. Radix/Geist: 12 y 10 pasos. Convergencia: **10-14 pasos de neutral, y el neutral hace casi todo el trabajo de la UI** — los matices de acento son pocos y con rol semántico (success/danger/warning/info), no decorativo.

### Regla extraíble

**[RECOMMENDED]** Tres capas: primitivos (escala 10-12 pasos por matiz, nunca usados directo en componentes) → semánticos (`bg/text/border/icon + rol + estado`) → por componente solo si hace falta. Dark mode = los mismos tokens semánticos re-mapeados (con neutral invertido y superficies que se **aclaran** al apilarse), jamás una segunda paleta duplicada. Un rol de color (success, danger) necesita su mini-escala (fondo sutil, borde, sólido, hover, texto), no un solo hex — esto **matiza** el ejemplo de 1.2 del Nivel 1 (`success: "#16a34a"` como valor único).

---

## 4. Componentes: la anatomía de Button que se repite en todos

### Variantes: 3-4 niveles de énfasis + peligro como eje aparte

| Sistema | Jerarquía documentada | Fuente |
|---|---|---|
| Carbon | Primary / Secondary / Tertiary / Ghost + Danger (en 3 estilos) | [carbondesignsystem.com/components/button/usage](https://carbondesignsystem.com/components/button/usage/) |
| Primer | Primary / Default / Invisible + Danger | [primer.style/components/button](https://primer.style/components/button) |
| Polaris | Primary / Secondary / Tertiary / Plain + `tone` success/critical ortogonal a la variante | [polaris-react.shopify.com/components/actions/button](https://polaris-react.shopify.com/components/actions/button) |
| Atlassian | Default / Primary / Subtle / Warning / Danger (página de usage cargó parcial; variantes confirmadas solo por el listado de componentes) | [atlassian.design/components/button](https://atlassian.design/components/button/usage) |

Convergencias duras:

1. **Un solo primary por pantalla.** Carbon: "Primary buttons should only appear once per screen". Primer: "Never put more than one in a group… rarely use more than one per page". Es la regla más repetida de todo el análisis.
2. **Danger no es una variante más de color: se usa "sparingly" y suele pedir confirmación** (Primer), y Polaris lo restringe a acciones "difícil o imposible de deshacer".
3. **Alturas (Carbon, el único que las publica completas):** sm 32px / md 40px / lg 48px / xl 64px / 2xl 80px; el rango de trabajo de una app es 32-48px con 40px como talla común ([carbondesignsystem.com/components/button/style](https://carbondesignsystem.com/components/button/usage/)). Primer y Polaris nombran 3-4 tallas sin publicar px en las páginas consultadas — la banda 32/40/48 es convergencia inferida de Carbon + práctica observable, no estándar universal documentado.

### Lo que documentan como "no hacer" (Carbon y Polaris son los más explícitos)

- No usar botones como navegación (Carbon).
- No dos botones de alto énfasis juntos; no mezclar tallas en un grupo (Carbon).
- No centrar el label (peculiaridad Carbon: label alineado a la izquierda, ícono a la derecha).
- No truncar labels; no ALL CAPS; verbo fuerte primero; sin artículos ("Add menu item", no "Add a menu item") (Polaris).
- **No deshabilitar botones como default:** Primer recomienda evitar `disabled` (rompe navegación por teclado) y usar un estado "inactive" que conserva contraste y puede explicar por qué no está disponible.
- No danger icon-only sin label visible (Carbon).

### Regla extraíble

**[REQUIRED]** Button del sistema: máximo 4 niveles de énfasis + tono destructivo aparte; exactamente un primary por vista; acciones destructivas piden confirmación. **[RECOMMENDED]** alturas 32/40/48px (base 4) y preferir "inactive con explicación" sobre `disabled` mudo. El "no hacer" se documenta junto al componente — los sistemas maduros invierten tanto en anti-patrones como en ejemplos.

---

## 5. Densidad y layout: contenedor ~1280px y densidad como dimensión del sistema

### Datos publicados

- **Primer:** breakpoints 320/544/768/1012/1280/1400px; páginas completas limitadas a **xlarge 1280px** (1232px visuales tras padding de 24px) "to prevent overly long line lengths"; regiones de layout: header, content, panel izquierdo/derecho, footer; 1 columna <768px, 2 desde 768, 3 opcional ≥1400. [primer.style/foundations/layout](https://primer.style/foundations/layout)
- **Carbon (2x Grid):** unidad mini de **8px**; grid de **16 columnas** en Large+; breakpoints 320/672/1056/1312/1584px; gutter total 32px (16+16), padding 16px constante. [carbondesignsystem.com/elements/2x-grid/overview](https://carbondesignsystem.com/elements/2x-grid/overview/)
- **Densidad conmutable:** Primer expone gaps `condensed/normal/spacious` como tokens ([fuente](https://primer.style/foundations/primitives/size)); Carbon duplica su tipografía en sets productive/expressive y su Button en large-productive vs large-expressive ([fuente](https://carbondesignsystem.com/components/button/usage/)). La densidad no es un hack por pantalla: es una dimensión oficial con tokens propios.
- **Polaris** documenta el principio, no los números: proximidad = relación percibida, y componentes "sized appropriately based on their job" — compactos para tareas menores, grandes para las importantes. [polaris-react.shopify.com/design/space](https://polaris-react.shopify.com/design/space)
- **Anchos de sidebar:** ninguno de los sistemas consultados publica un ancho fijo de sidebar en las páginas revisadas — no documentado; el rango 240-280px que se ve en GitHub/Linear/Slack es medición empírica, no norma escrita.

### Regla extraíble

**[RECOMMENDED]** Contenido principal limitado a ~1280px (coincide con la sección 1.4 del Nivel 1 y con Primer); los breakpoints exactos NO convergen entre sistemas (Carbon 672/1056/1584 vs Primer 544/1012/1400 vs Tailwind 640/1024/1536) — lo que converge es tener 4-6 fijos y no inventarlos por componente. Si el producto tiene pantallas densas y cómodas, la densidad se modela como token (`condensed/normal/spacious`), no con overrides ad-hoc.

---

## 6. Navegación y jerarquía: shell persistente + teclado como primera clase

1. **Shell de app = header global + panel izquierdo opcional.** Carbon lo formaliza como "UI Shell": header (nivel más alto de navegación) + left panel (navegación del producto) + right panel (acciones de sistema), con la regla espacial "left-to-right translates to product-to-global" — lo del producto a la izquierda, lo global (perfil, notificaciones, switcher) a la derecha, en orden fijo. [carbondesignsystem.com/components/UI-shell-header/usage](https://carbondesignsystem.com/components/UI-shell-header/usage/)
2. **Command palette como capa de navegación paralela.** GitHub la documenta oficialmente: Ctrl/Cmd+K para navegar, buscar y ejecutar comandos con sugerencias contextuales según dónde estás ([docs.github.com/en/get-started/accessibility/github-command-palette](https://docs.github.com/en/get-started/accessibility/github-command-palette)). Vercel y Linear usan el mismo atajo (convención de facto; en Linear, inferido del producto — su doc pública no detalla el shortcut).
3. **La jerarquía de navegación se refina con alineación, no con decoración.** El rediseño de Linear invirtió en "reduce visual noise, maintain visual alignment, and increase the hierarchy and density of navigation elements" — alinear labels, iconos y botones vertical y horizontalmente en el sidebar; cambios que el usuario "siente" sin poder señalarlos. [linear.app/blog/how-we-redesigned-the-linear-ui](https://linear.app/blog/how-we-redesigned-the-linear-ui)

### Regla extraíble

**[RECOMMENDED]** En apps: header global + sidebar de producto (árbol de decisión ya en `FRONTEND_NAVIGATION_PATTERNS.md` y `FRONTEND_SIDEBAR_PATTERNS.md`); utilidades globales siempre a la derecha del header en orden estable. Para herramientas de uso diario, Cmd/Ctrl+K con búsqueda contextual es el estándar de facto de la categoría.

---

## 7. Estados y feedback: los estados se diseñan, no se improvisan

### Empty states (Carbon los tipifica)

Carbon distingue **3 tipos con tratamientos distintos**: (a) sin datos aún / primer uso — enseñar qué irá ahí y cómo empezar; (b) resultado de acción del usuario — ej. búsqueda sin resultados, sugerir ajustar filtros; (c) error/permisos/configuración — máxima especificidad para auto-recuperarse. Anatomía: imagen opcional + título breve y positivo ("Start by adding data assets", no "You don't have data") + cuerpo + acción primaria + CTA secundaria opcional. Reglas clave: el empty state **reemplaza el elemento entero** (que un screen reader no anuncie una tabla vacía) y "don't lead the user into a dead end". [carbondesignsystem.com/patterns/empty-states-pattern](https://carbondesignsystem.com/patterns/empty-states-pattern/)

### Loading (Carbon)

- **Skeleton** solo para componentes contenedores (tiles, tablas, cards, listas) y solo si la carga dura "a moment or two"; **nunca** en toasts, menús overflow ni modales.
- **Loading indicator** (inline o full-screen) para acciones del usuario en proceso; si tomará más que unos momentos → **progress indicator**; si tomará minutos → notificación al terminar.
- **Progressive loading** por lotes: estructura → contenido → imágenes/interactivos.
[carbondesignsystem.com/patterns/loading-pattern](https://carbondesignsystem.com/patterns/loading-pattern/)

### Errores (Polaris tiene la guía de escritura más completa)

- Decir **qué pasó y qué hacer**, con datos concretos; prohibido el jargon ("invalid"), la disculpa excesiva y el "we/us".
- Severidad por color: rojo = crítico que bloquea; amarillo = advertencia que puede escalar.
- Posición: **junto al elemento con problema** (inline); banner para errores de página con acción ("Couldn't deposit payout. Update your details, and we'll retry automatically."); toast solo mensajes breves ("Connection timed out").
- Múltiples errores: "To save this product, make 2 changes: …" — nunca "There are 2 errors on this page".
[polaris-react.shopify.com/content/error-messages](https://polaris-react.shopify.com/content/error-messages)

### Regla extraíble

Ya cubierta en `FRONTEND_STATES_PATTERNS.md` (que coincide casi 1:1 con Carbon: skeleton para layouts conocidos, spinner solo acciones cortas, empty por motivo). Lo que este análisis **agrega**: (1) el empty state reemplaza el elemento entero por accesibilidad; (2) skeleton está prohibido en overlays (toast/modal/menú); (3) el título del empty state se redacta en positivo-accionable, no describiendo la carencia.

---

## 8. Accesibilidad como contrato del sistema, no como auditoría final

1. **Radix Primitives garantiza el comportamiento por contrato:** componentes que "follow the WAI-ARIA authoring practices guidelines", con atributos `aria`/`role`, **focus management** (ej. AlertDialog mueve el foco al botón Cancel al abrir) y **keyboard navigation** resueltos de serie y testeados contra tecnologías asistivas reales. Lo único que queda a cargo del desarrollador son los labels accesibles. [radix-ui.com/primitives/docs/overview/accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility)
   **Por qué importa para elegir primitivas:** un Dialog/Select/Menu accesible correcto son cientos de líneas de detalle (focus trap, restore, tipeo predictivo, roving tabindex). Construirlo a mano y bien es un proyecto en sí; por eso shadcn/ui se construye **encima** de Radix en vez de reimplementar — se hereda el contrato ARIA y solo se aporta el estilo.
2. **El contraste se resuelve en la paleta, no componente a componente:** Stripe (niveles con contraste garantizado por distancia, sección 3) y Linear (tema de alto contraste derivado automáticamente de 3 variables) empujan la garantía WCAG al sistema de color.
3. **Decisiones de componente motivadas por a11y:** Primer desaconseja `disabled` (rompe teclado); Carbon exige que el empty state reemplace la tabla (screen readers); Stripe Apps **restringe el styling custom** de terceros justamente para proteger contraste y consistencia — solo el indicador de marca admite color libre ([docs.stripe.com/stripe-apps/design](https://docs.stripe.com/stripe-apps/design)).

### Regla extraíble

**[REQUIRED]** Los componentes con comportamiento complejo (dialog, dropdown, select, tabs, tooltip, popover) se construyen sobre primitivas con contrato ARIA documentado (Radix o equivalente), no desde `div`s propios. **[RECOMMENDED]** El contraste AA se garantiza en la definición de la paleta (pares válidos por construcción), complementando `FRONTEND_COLOR_CONTRAST_STANDARD.md` y `FRONTEND_ACCESSIBILITY_STANDARD.md`.

---

## 9. Lo que separa a Stripe/Linear de un diseño genérico — las 10 decisiones

Síntesis de todo lo anterior. Un diseño "tipo Bootstrap" y uno "tipo Linear" usan las mismas piezas; difieren en estas decisiones de restraint:

1. **Un acento, neutrales trabajando.** Linear reduce el tema a 3 variables (base, acento, contraste); en Geist 2 de cada 10 escalas son grises y los fondos son una escala propia. Genérico = 5 colores compitiendo; referencia = 10-14 grises finos + 1 acento con rol. (secc. 3)
2. **Color perceptual, no RGB a ojo.** CIELAB (Stripe) / LCH (Linear): pasos que *se ven* equidistantes y contraste garantizado por matemática. (secc. 3)
3. **Grilla de 4px sin excepciones — incluida la tipografía.** Line-heights múltiplos de 4 (Primer, Polaris): texto, iconos y cajas caen en la misma retícula, y eso es lo que hace que "todo alinee" sin que se note por qué. (secc. 1-2)
4. **Jerarquía tipográfica estricta y contenida:** body 13-14px, énfasis con 500-600 (no bold 700 por todos lados), una familia. La jerarquía sale de 3 pesos y 6-8 tamaños, no de 13 tamaños usados a la vez. (secc. 2)
5. **Espaciado generoso donde importa, denso donde se trabaja:** rangos de uso asignados a la escala (Atlassian) y densidad como token conmutable (Primer condensed/spacious, Carbon productive/expressive), no un padding uniforme mediocre para todo. (secc. 1, 5)
6. **Bordes y sombras contenidos:** bordes 1px del paso 6-7 de la escala (Radix), sombras mínimas; en dark, profundidad por luminosidad de capas (Carbon: cada capa un paso más clara), no por sombras. (secc. 3)
7. **Microinteracciones sutiles y rápidas.** Los sistemas consultados no publican duraciones exactas (no documentado — la banda ~100-200ms para micro-interacción viene de Material/NNg y ya está en `FRONTEND_MOTION_STANDARD.md` secc. 2); lo observable en Linear es que la animación nunca retrasa al usuario — su rediseño invirtió en alineación y jerarquía, no en movimiento decorativo.
8. **Tokens semánticos de punta a punta:** ningún hex en componentes; dark mode y theming son un re-mapeo, no un fork. Es la diferencia entre "tenemos dark mode" y "el dark mode se ve bien". (secc. 3)
9. **Teclado y command palette de primera clase:** Cmd+K, navegación completa por teclado, foco gestionado (GitHub, Linear, Radix). El mouse es una opción, no un requisito. (secc. 6, 8)
10. **Los estados son pantallas diseñadas:** empty states que enseñan el camino, skeletons con la forma real, errores que dicen qué hacer. Bootstrap te da el componente; el sistema de referencia te dice qué pasa cuando no hay datos. (secc. 7)

---

## 10. Tabla final: decisión → convergencia → regla para este handbook

| Decisión | Convergencia entre sistemas | Regla adoptada (y dónde vive) |
|---|---|---|
| Base de spacing | Grilla 4px universal (aun quien declara base 8) | Ya en `FRONTEND_ENGINEERING_STANDARD.md` 1.1 — **ampliar escala con 12 y 20px** (secc. 1) |
| Forma de la escala | Densa 2-24px, rala 32+; rangos de uso asignados | Adoptar rangos: ≤8 micro, 12-24 componente, ≥32 layout (secc. 1, nuevo matiz) |
| Familias tipográficas | 1 UI + 1 mono; fallback system siempre | Ya en 1.3 del Nivel 1 (máx. 2 familias) — consistente |
| Body size en apps | 13-14px (Atlassian default 14) | Matiz a 1.3: 14px body en producto denso; 16px solo lectura larga (secc. 2) |
| Pesos | 3 pesos; tope semibold 600 en UI densa | Matiz a 1.3 (dice 400/500/700): preferir 400/500/600 en apps (secc. 2) |
| Line-height | Múltiplo de 4px, empaquetado con el tamaño | Nuevo — adoptar en proyectos junto a 1.1/1.3 (secc. 2) |
| Arquitectura de color | Primitivos → semánticos → componente; roles con estados | Extiende 1.2 del Nivel 1 y `FRONTEND_COLOR_CONTRAST_STANDARD.md`: cada rol es una mini-escala, no un hex (secc. 3) |
| Grises | 10-14 pasos neutrales con función por paso (Radix 1-12) | Adoptar mapa de usos de Radix como referencia al armar paletas (secc. 3) |
| Dark mode | Re-mapeo de tokens semánticos; superficies se aclaran al apilar | Ya en `FRONTEND_COLOR_CONTRAST_STANDARD.md` secc. 4 y `FRONTEND_ELEVATION_STANDARD.md` — consistente; refuerzo: neutral invertido estilo Primer (secc. 3) |
| Contraste | Garantizado por construcción de paleta (Stripe ≥5 niveles = 4.5:1) | Complementa `FRONTEND_COLOR_CONTRAST_STANDARD.md` (secc. 3, 8) |
| Button | ≤4 énfasis + danger aparte; 1 primary por vista; alturas 32/40/48 | Extiende secc. 04 del Nivel 1; regla "1 primary por vista" adoptar como REQUIRED (secc. 4) |
| Disabled | Evitar disabled mudo; estado inactive con explicación (Primer) | Matiz a 1.6 del Nivel 1 (secc. 4) |
| Contenedor | ~1280px máx. (Primer 1280; handbook 1280) | Ya en 1.4 del Nivel 1 — confirmado (secc. 5) |
| Breakpoints | NO convergen en valores exactos; sí en tener 4-6 fijos | 1.4 del Nivel 1 correcto como está: fijos y consistentes > valores "estándar" (secc. 5) |
| Densidad | Token conmutable (condensed/normal/spacious; productive/expressive) | Nuevo — considerar en dashboards (`FRONTEND_DASHBOARD_PATTERNS.md`, `FRONTEND_TABLE_PATTERNS.md`) (secc. 5) |
| Navegación app | Header global + sidebar producto; global a la derecha; Cmd+K | Ya en `FRONTEND_NAVIGATION_PATTERNS.md` / `FRONTEND_SIDEBAR_PATTERNS.md`; Cmd+K nuevo para herramientas diarias (secc. 6) |
| Empty/loading/error | Tipificados con anatomía fija; skeleton solo contenedores | Ya en `FRONTEND_STATES_PATTERNS.md`; agregar: reemplazo total del elemento + skeleton prohibido en overlays (secc. 7) |
| Redacción de errores | Qué pasó + qué hacer, sin jargon; severidad por color | Ya en `FRONTEND_MICROCOPY_STANDARD.md` y `FRONTEND_STATES_PATTERNS.md` — consistente con Polaris (secc. 7) |
| Primitivas accesibles | Comportamiento ARIA por contrato (Radix), no artesanal | Adoptar como REQUIRED para componentes overlay/selección (secc. 8; complementa `FRONTEND_ACCESSIBILITY_STANDARD.md`) |
| Motion | Duraciones no publicadas por estos sistemas | Mantener `FRONTEND_MOTION_STANDARD.md` secc. 2 (100-150ms micro) como fuente interna (secc. 9.7) |

---

## Fuentes consultadas (verificadas 2026-07-20)

- GitHub Primer: [primer.style/foundations/primitives/size](https://primer.style/foundations/primitives/size) · [primitives/typography](https://primer.style/foundations/primitives/typography) · [color/overview](https://primer.style/foundations/color/overview) · [layout](https://primer.style/foundations/layout) · [components/button](https://primer.style/components/button)
- Shopify Polaris: [tokens/space](https://polaris-react.shopify.com/tokens/space) · [tokens/font](https://polaris-react.shopify.com/tokens/font) · [tokens/color](https://polaris-react.shopify.com/tokens/color) · [components/actions/button](https://polaris-react.shopify.com/components/actions/button) · [content/error-messages](https://polaris-react.shopify.com/content/error-messages) · [design/space](https://polaris-react.shopify.com/design/space)
- IBM Carbon: [elements/spacing](https://carbondesignsystem.com/elements/spacing/overview/) · [elements/typography](https://carbondesignsystem.com/elements/typography/overview/) · [elements/color](https://carbondesignsystem.com/elements/color/overview/) · [elements/2x-grid](https://carbondesignsystem.com/elements/2x-grid/overview/) · [components/button](https://carbondesignsystem.com/components/button/usage/) · [patterns/empty-states-pattern](https://carbondesignsystem.com/patterns/empty-states-pattern/) · [patterns/loading-pattern](https://carbondesignsystem.com/patterns/loading-pattern/) · [components/UI-shell-header](https://carbondesignsystem.com/components/UI-shell-header/usage/)
- Atlassian Design System: [foundations/spacing](https://atlassian.design/foundations/spacing) · [foundations/typography](https://atlassian.design/foundations/typography) · [foundations/color](https://atlassian.design/foundations/color)
- Radix: [colors/understanding-the-scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale) · [primitives/accessibility](https://www.radix-ui.com/primitives/docs/overview/accessibility)
- Vercel Geist: [geist/text](https://vercel.com/geist/text) · [geist/colors](https://vercel.com/geist/colors)
- Stripe: [blog/accessible-color-systems](https://stripe.com/blog/accessible-color-systems) · [docs.stripe.com/stripe-apps/design](https://docs.stripe.com/stripe-apps/design)
- Linear: [blog/how-we-redesigned-the-linear-ui](https://linear.app/blog/how-we-redesigned-the-linear-ui) · [linear.app/method](https://linear.app/method) (cargó parcial: solo estructura de secciones)
- GitHub Docs: [command palette](https://docs.github.com/en/get-started/accessibility/github-command-palette)

> Nota de método: las páginas de Carbon se consultaron vía el repositorio público `carbon-design-system/carbon-website` (mismo contenido que el sitio) porque el sitio renderizado excedía el límite del fetcher. La página de usage del Button de Atlassian cargó parcial — sus variantes se citan con esa reserva en la sección 4.
