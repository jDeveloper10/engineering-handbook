---
title: "Referencia de Elementos HTML"
category: 01_Frontend
tags: [frontend, html, referencia, semantica]
summary: "Referencia elemento por elemento con tabla de conversión de div-soup al elemento correcto: estructura, controles nativos, formularios, contenido y el landmark de búsqueda."
keywords: [html, referencia, div-soup, semantica, landmarks, formularios, search]
updated: 2026-07-27
status: current
---

# FRONTEND HTML ELEMENTS REFERENCE (Referencia por elemento)

> Nivel 2 del handbook. Complementa a [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md): aquel documento define la estructura de página (landmarks, jerarquía de headings, un `<main>`/`<h1>`); este baja al nivel de **elemento individual** — los elementos que las IAs usan mal o directamente ignoran. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Igual que en HTML_STRUCTURE, no hay capa de implementación separada por framework: la etiqueta es la regla, idéntica en React, Vue o HTML plano. Las únicas notas específicas de React (atributos camelCase, `htmlFor`) se marcan como *nota React*.
>
> Formato por elemento: **Cuándo usar / Cuándo NO / Error común de IA / Ejemplo mínimo**.

---

## 1. Regla maestra

**[REQUIRED]** Prohibido usar `<div>`/`<span>` cuando existe un elemento HTML con el significado equivalente. `<div>` y `<span>` son el último recurso: solo para agrupar por layout/estilo cuando ninguna etiqueta semántica aplica.

**Por qué:** un `<div>` no comunica nada al navegador, al lector de pantalla ni al buscador; el elemento nativo trae gratis teclado, foco, semántica, validación y comportamiento probado que de otro modo hay que reimplementar en JS (mal y con bugs).

Tabla de conversión div-soup → elemento correcto:

| ❌ div-soup típico de IA | ✅ Elemento correcto |
|---|---|
| `<div class="modal">` + overlay manual | `<dialog>` |
| `<div class="accordion">` + estado open en JS | `<details>` + `<summary>` |
| `<div onClick={...}>` | `<button>` |
| `<span class="link" onClick={navigate}>` | `<a href>` |
| `<div class="form">` con inputs sueltos | `<form>` |
| `<div class="form-group-title">` | `<fieldset>` + `<legend>` |
| `<span>` junto al input como etiqueta | `<label for>` |
| `<div class="image-card"><img/><div class="caption">` | `<figure>` + `<figcaption>` |
| `<span class="date">12/05/2026</span>` | `<time datetime="2026-05-12">` |
| `<span class="highlight">` en resultados de búsqueda | `<mark>` |
| `<div class="quote">` | `<blockquote>` (+ `cite`) |
| `<span class="code">` | `<code>` / `<pre><code>` |
| `<div class="progress-bar"><div style="width:60%">` | `<progress>` o `<meter>` |
| `<div class="term"><div class="definition">` | `<dl>` + `<dt>` + `<dd>` |
| `<div class="search-box">` | `<search>` + `<form>` |
| `<div class="result-output">` | `<output>` |

---

## 2. Estructura

`<header>`, `<main>`, `<footer>`, `<nav>`, `<section>`, `<article>`, `<aside>` ya están definidos en [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) secciones 2–3 y 12 (landmarks): estructura base, un solo `<main>`, cuándo usar cada uno. **Ese documento manda** — esta sección no lo repite; solo agrega los matices a nivel de elemento que las IAs suelen romper incluso cuando ya usan las etiquetas correctas.

### `<nav>` con etiqueta cuando hay más de uno
**[REQUIRED]** Si la página tiene 2+ `<nav>` (ej. navbar + breadcrumbs + links del footer), cada uno lleva `aria-label` distinto.
- **Error común de IA:** dos o tres `<nav>` anónimos en la misma página.
- **Por qué:** un lector de pantalla anuncia "navegación" para todos por igual; sin etiqueta son indistinguibles al saltar entre landmarks.
```html
✅ <nav aria-label="principal">…</nav> … <nav aria-label="migas de pan">…</nav>
```

### `<section>` sin heading no es `<section>`
**[REQUIRED]** Un `<section>` se justifica por tener (o poder tener) su propio heading. Si un bloque no tiene título ni tema propio, es un `<div>` de layout — y está bien que lo sea.
- **Error común de IA:** envolver cada bloque visual en `<section>` "para ser semántico", generando section-soup, tan vacío de significado como el div-soup.
- **Por qué:** `<section>` promete al lector de pantalla y al outline del documento "aquí empieza un tema"; usado como wrapper genérico, esa promesa se vuelve ruido.
```html
✅ <section aria-labelledby="pricing-h"><h2 id="pricing-h">Precios</h2>…</section>
✅ <div class="mx-auto max-w-6xl">…</div>   <!-- wrapper de layout: div está bien -->
```

### `<article>` para unidades repetidas autocontenidas
**[RECOMMENDED]** Cards de producto, posts, comentarios, resultados de búsqueda: cada ítem repetido que tiene sentido por sí solo fuera de contexto es un `<article>` (dentro de `<ul><li>` si forman una lista).
- **Cuándo NO:** paneles de UI (filtros, toolbars, widgets de dashboard) que no son contenido independiente — eso es `<section>` o `<div>`.
- **Error común de IA:** `<div class="card">` para todo; o al revés, `<article>` decorando cualquier caja con borde.
- **Por qué:** el lector de pantalla enumera artículos ("artículo 3 de 12") y los buscadores los tratan como unidades de contenido sindicables.
```html
✅ <ul><li><article><h3>Plan Pro</h3><p>$49/mes</p></article></li>…</ul>
```

---

## 3. Interactivos nativos

### `<button>` vs `<a>` — la regla de oro
**[REQUIRED]** Navega a otra URL/ruta → `<a href>`. Ejecuta una acción en la página (guardar, abrir modal, togglear) → `<button>`. Nunca `<div>`/`<span>` clickeable. Ya definido en HTML_STRUCTURE sección 6 — se repite aquí solo porque es el error #1 de las IAs.
- **Cuándo NO:** `<a href="#">` con `preventDefault` para acciones (es un botón disfrazado, rompe "abrir en pestaña nueva" y deja `#` en la URL); `<button>` que solo hace `navigate()` (rompe middle-click, Ctrl+click, hover-preview de URL y el crawleo del link).
- **Error común de IA:** en React Router, `<button onClick={() => navigate('/x')}>` en vez de `<Link to="/x">` (que renderiza un `<a>` real con `href`).
- **Por qué:** el elemento correcto trae gratis el comportamiento completo que el usuario espera — un `<a>` es un link con todos sus gestos del navegador; un `<button>` es focusable y se activa con Enter/Space sin JS extra. "Se ve como botón pero navega" se resuelve con CSS sobre `<a>`, nunca cambiando el elemento.
```html
✅ <a href="/precios">Ver precios</a>              <!-- navega -->
✅ <button type="button" onClick={abrirModal}>Eliminar</button>  <!-- acciona -->
```

### `<dialog>`
**[REQUIRED]** Todo modal usa `<dialog>` + `showModal()` (detalle de UX del patrón en [FRONTEND_MODALS_PATTERNS.md](../Patterns/FRONTEND_MODALS_PATTERNS.md)).
- **Cuándo usar:** modales de confirmación, formularios en overlay, lightboxes. `show()` (sin backdrop ni bloqueo) para diálogos no modales.
- **Cuándo NO:** para contenido que no interrumpe el flujo (usar sección normal); para menús desplegables y tooltips (usar `<details>` o el atributo `popover`).
- **Error común de IA:** `<div class="overlay"><div class="modal">` con foco, Escape, backdrop y scroll-lock reimplementados a mano — y casi siempre incompletos.
- **Por qué:** `showModal()` da gratis lo más difícil de reimplementar bien: focus-trap, cierre con Escape, `::backdrop`, fondo inert y render en la top layer (ningún `z-index` lo tapa).
```html
✅ <dialog ref={ref}>
     <h2>¿Eliminar factura?</h2>
     <form method="dialog"><button value="cancel">Cancelar</button><button value="ok">Eliminar</button></form>
   </dialog>
   // abrir con ref.current.showModal() — nunca solo con CSS display
```
`<form method="dialog">` cierra el dialog al enviar y deja el `value` del botón en `dialog.returnValue` — confirmación sin estado manual.

### `<details>` + `<summary>`
**[RECOMMENDED]** Acordeones, FAQs, secciones colapsables sin requisitos de animación compleja.
- **Cuándo usar:** FAQ de landing, "ver más" de contenido secundario, filtros avanzados colapsados.
- **Cuándo NO:** tabs (semántica distinta), navegación principal, contenido que SEO necesita indexar visible-first (el contenido dentro de `details` sí se indexa, pero el usuario lo ve colapsado).
- **Error común de IA:** `useState(open)` + `<div>` condicional + chevron rotado a mano, para algo que el navegador resuelve sin una línea de JS.
- **Por qué:** el par nativo es focusable, se opera con teclado, expone estado expandido/colapsado al lector de pantalla y funciona aunque el JS falle; la versión manual exige reimplementar todo eso y casi nunca se hace completo.
```html
✅ <details><summary>¿Cuánto cuesta?</summary><p>Desde $19/mes.</p></details>
```
Con el atributo `name` compartido, varios `<details name="faq">` se comportan como acordeón exclusivo (solo uno abierto) — también sin JS.

---

## 4. Formularios

### `<form>`
**[REQUIRED]** Todo grupo de campos que se envía junto vive dentro de un `<form>` con `<button type="submit">`, y el handler va en `onSubmit` del form, no en `onClick` del botón (ya exigido en HTML_STRUCTURE sección 7).
- **Cuándo NO:** un control aislado que muta estado local al instante (un toggle de tema, un filtro que aplica al cambiar) no necesita `<form>` — el form implica "conjunto de datos que se envía".
- **Error común de IA:** inputs sueltos en un `<div>` y un botón con `onClick`.
- **Por qué:** sin `<form>` se pierde el envío con Enter, la validación nativa (`required`, `type`), y el autofill correcto del navegador y los gestores de contraseñas (que buscan forms, no divs).
```jsx
✅ <form onSubmit={handleSubmit}> ... <button type="submit">Enviar</button></form>
```
**Nota React:** dentro de un `<form>`, todo `<button>` sin `type` es submit por defecto — los botones auxiliares (mostrar contraseña, agregar fila) llevan `type="button"` explícito o disparan submits fantasma.

### `<fieldset>` + `<legend>`
**[REQUIRED]** Grupos de radios/checkboxes que responden a una misma pregunta van en `<fieldset>` con la pregunta como `<legend>`.
- **Cuándo usar:** "Método de pago" con 3 radios; "Notificaciones" con varios checkboxes; pasos de un wizard.
- **Cuándo NO:** para envolver un único campo (ruido sin significado).
- **Error común de IA:** `<p class="font-bold">Método de pago</p>` + radios sueltos.
- **Por qué:** el lector de pantalla anuncia el `<legend>` junto a cada opción del grupo; con un `<p>` visualmente idéntico, lee cada radio sin saber a qué pregunta responde. Bonus: `disabled` en el `<fieldset>` deshabilita todos sus campos de una vez.
```html
✅ <fieldset><legend>Método de pago</legend>
     <label><input type="radio" name="pago" value="card" /> Tarjeta</label>
     <label><input type="radio" name="pago" value="transfer" /> Transferencia</label>
   </fieldset>
```

### `<label>`
**[REQUIRED]** Cada `<input>`/`<select>`/`<textarea>` tiene `<label>` asociado por `for`/`id` (o envolviendo al control). Nunca placeholder como único rótulo (razón de fondo en HTML_STRUCTURE sección 11).
- **Cuándo NO:** si el rótulo visible es imposible por diseño (ej. buscador icon-only), el nombre accesible se da igual (`aria-label`) — pero eso es la excepción justificada, no el default.
- **Error común de IA:** `<span>Email</span><input placeholder="Email" />` — el span no está asociado: click en el texto no enfoca el campo y el lector de pantalla anuncia un input sin nombre.
- **Por qué:** la asociación programática es lo que agranda el área de click al texto y le da nombre al campo para asistencia y autofill; la cercanía visual no asocia nada.
```jsx
✅ <label htmlFor="email">Email</label><input id="email" type="email" />
```
**Nota React:** `htmlFor` en vez de `for`.

### `<input type>` correcto
**[REQUIRED]** El `type` describe el dato, no el estilo. Mapa de decisión:

| Dato | `type` correcto |
|---|---|
| Email | `email` |
| Teléfono | `tel` |
| URL | `url` |
| Contraseña | `password` |
| Cantidad operable (edad, monto, unidades) | `number` |
| Código numérico no operable (postal, DNI, tarjeta, OTP) | `text` + `inputmode="numeric"` (+ `pattern`) |
| Fecha / hora | `date`, `time`, `datetime-local` |
| Término de búsqueda | `search` |
| Elección única / múltiple | `radio` / `checkbox` |
| Valor en rango continuo (volumen) | `range` |
| Archivo | `file` |

- **Cuándo NO `type="number"`:** códigos que "parecen números" pero no se suman — `number` les agrega spinners, permite `e`/`+`/`-` y borra ceros a la izquierda.
- **Error común de IA:** `type="text"` para todo — se pierde teclado móvil adecuado, validación nativa y autofill.
- **Por qué:** el `type` decide qué teclado abre el móvil, qué valida el navegador y qué autocompleta. Sumar `autocomplete` (`email`, `current-password`, `new-password`, `one-time-code`...) multiplica ese beneficio.
```html
✅ <input type="email" autocomplete="email" required />
✅ <input type="text" inputmode="numeric" autocomplete="postal-code" />
```

### `<select>`
**[RECOMMENDED]** Elegir 1 opción de una lista cerrada de ~5–15 valores conocidos.
- **Cuándo NO:** 2–4 opciones visibles de un vistazo (radios son más rápidos y muestran todo sin click); listas enormes o con búsqueda (combobox accesible); selección múltiple (checkboxes — el `<select multiple>` nativo es hostil en móvil).
- **Error común de IA:** dropdown custom de `<div>`s con `onClick` para una lista simple de países.
- **Por qué:** el nativo trae teclado, type-ahead y el picker optimizado de cada móvil; el custom pierde los tres y suma cientos de líneas. Solo se justifica un combobox custom cuando el requisito (búsqueda, avatares, multi-select) supera lo que `<select>` puede dar. Agrupar opciones largas con `<optgroup label>`.
```html
✅ <select id="pais" autocomplete="country-name"><option value="">Seleccionar…</option><option value="mx">México</option></select>
```

### `<textarea>`
**[REQUIRED]** Texto libre multilínea (comentarios, descripciones). Nunca un `<div contenteditable>` para capturar texto plano, ni un `<input>` para párrafos.
- **Cuándo NO:** una sola línea corta (nombre, asunto) → `<input type="text">`; edición rica real (negritas, listas) es el único caso legítimo de `contenteditable`, dentro de una librería de editor probada.
- **Error común de IA:** olvidar `rows` razonable y `maxLength` cuando el backend impone límite (el usuario descubre el límite recién en el error del servidor).
- **Por qué:** `<textarea>` participa en `<form>`, validación y autofill como cualquier campo; `contenteditable` no, y requiere sanitización manual de todo lo que entra.
```html
✅ <textarea id="mensaje" rows="4" maxLength="500"></textarea>
```
**Nota:** con CSS `field-sizing: content` crece con el contenido sin JS (progressive enhancement, aún sin soporte universal en 2026).

### `<output>`
**[RECOMMENDED]** Resultado de un cálculo derivado de inputs del usuario: total de un carrito, cuota calculada, contador de caracteres restantes.
- **Cuándo NO:** contenido estático o mensajes de estado del servidor (para eso, patrones de [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md)).
- **Error común de IA:** ignorarlo por completo y usar `<span>{total}</span>`.
- **Por qué:** `<output>` es una live region implícita (`aria-live="polite"` de serie): el lector de pantalla anuncia el nuevo valor cuando cambia, sin ARIA manual — exactamente lo que un total recalculado necesita.
```html
✅ <label for="monto">Monto</label><input id="monto" type="number" />
   <p>Cuota: <output for="monto">$1.250/mes</output></p>
```

---

## 5. Contenido

### `<figure>` + `<figcaption>`
**[RECOMMENDED]** Imagen/diagrama/bloque de código con leyenda, referenciable como unidad ("ver figura 2").
- **Cuándo NO:** imágenes decorativas o sin leyenda (basta `<img>`); no toda imagen necesita `<figure>`.
- **Error común de IA:** `<div><img/><p class="text-sm text-gray-500">Leyenda</p></div>`.
- **Por qué:** `<figcaption>` queda asociado programáticamente a la imagen — el lector de pantalla sabe que ese texto la describe; el `<p>` gris de al lado es solo proximidad visual.
```html
✅ <figure><img src="grafico.webp" alt="Ingresos 2025 por trimestre" /><figcaption>Ingresos 2025.</figcaption></figure>
```

### `<picture>` + `<source>`
**[RECOMMENDED]** Art direction (imagen distinta por breakpoint) o servir formatos modernos (AVIF/WebP) con fallback.
- **Cuándo NO:** solo cambiar el tamaño de la misma imagen → `srcset`/`sizes` en el `<img>` alcanza y es más simple.
- **Error común de IA:** renderizar dos `<img>` y togglear con CSS `hidden md:block` — el navegador descarga ambas; `<picture>` descarga solo la que aplica.
- **Por qué:** la selección ocurre antes de la descarga, no después. El `alt` (y `width`/`height`) van siempre en el `<img>` interno, nunca en `<source>`.
```html
✅ <picture>
     <source type="image/avif" srcset="hero.avif" />
     <img src="hero.jpg" alt="Dashboard de facturación" width="1200" height="630" />
   </picture>
```

### `<time datetime>`
**[REQUIRED]** Toda fecha/hora visible al usuario va en `<time>` con `datetime` en formato ISO 8601, sin importar cómo se muestre el texto (formato de display en [FRONTEND_FORMATTING_STANDARD.md](../Core/FRONTEND_FORMATTING_STANDARD.md)).
- **Cuándo NO:** duraciones vagas sin fecha concreta ("hace mucho tiempo") que no se pueden expresar en ISO.
- **Error común de IA:** `<span>hace 3 días</span>` o `<span>12/05/2026</span>` — ambiguo (¿12 de mayo o 5 de diciembre?) e ilegible para máquinas.
- **Por qué:** con `datetime` los buscadores obtienen la fecha exacta (fechas en SERP, ordenamiento de artículos) aunque el texto visible sea relativo o localizado.
```html
✅ <time datetime="2026-07-17">hace 3 días</time>
✅ <time datetime="2026-07-20T19:30-06:00">hoy 19:30</time>
```

### `<mark>`
**[RECOMMENDED]** Resaltar la parte relevante *en el contexto actual*: coincidencias de búsqueda en resultados, la fila/frase referenciada, texto citado que se está comentando.
- **Cuándo NO:** énfasis editorial permanente (`<strong>` importancia / `<em>` énfasis) ni decoración de marketing (CSS sobre `<span>`).
- **Error común de IA:** `<span class="bg-yellow-200">` para marcar coincidencias de búsqueda.
- **Por qué:** `<mark>` significa "relevante en este contexto" para tecnología de asistencia y trae resaltado por defecto; el span amarillo solo lo ve quien ve.
```html
✅ <li>Factura <mark>elect</mark>rónica</li>   <!-- query del usuario: "elect" -->
```

### `<blockquote>` + `cite`
**[RECOMMENDED]** Citas de fuente externa: testimonios, reseñas, fragmentos citados de otro documento.
- **Cuándo NO:** para indentar visualmente texto propio (eso es CSS); la atribución visible ("— Juan, CEO") va *fuera* del `<blockquote>` (típicamente `<figcaption>`), porque el autor no es parte de la cita.
- **Error común de IA:** testimonios de landing como `<div class="testimonial"><p>"…"</p></div>` sin semántica de cita, o la atribución metida dentro del blockquote.
- **Por qué:** la semántica de cita separa "voz externa" de "voz del sitio" — señal honesta para lectores y buscadores; el atributo `cite` (URL) documenta la fuente.
```html
✅ <figure>
     <blockquote cite="https://ejemplo.com/review"><p>Duplicamos conversión en 2 meses.</p></blockquote>
     <figcaption>— Ana Ruiz, CMO de Acme</figcaption>
   </figure>
```

### `<code>`, `<pre>`, `<kbd>`
**[REQUIRED]** Código inline → `<code>`; bloque multilínea preformateado → `<pre><code>`; teclas que el usuario presiona → `<kbd>`.
- **Cuándo NO:** `<pre>` para maquetar texto con espacios (eso es CSS `white-space`); `<code>` para cifras o nombres propios que solo quieres en monoespaciada.
- **Error común de IA:** `<span class="font-mono">` para todo — se pierde la distinción entre "esto es código", "esto es salida" (`<samp>`) y "presiona esta tecla".
- **Por qué:** la distinción importa para lectores de pantalla, para plugins de resaltado/copiado que buscan `pre > code`, y para que los buscadores no indexen código como prosa.
```html
✅ <p>Ejecuta <code>npm run dev</code> y presiona <kbd>Ctrl</kbd>+<kbd>C</kbd> para salir.</p>
```

### `<progress>` vs `<meter>`
**[REQUIRED]** Avance de una tarea en curso (upload, wizard, carga) → `<progress>`. Medición estática dentro de un rango conocido (uso de disco, fuerza de contraseña, score) → `<meter>` (con `low`/`high`/`optimum` si hay zonas buena/mala).
- **Cuándo NO:** `<progress>` para métricas que no avanzan (semánticamente dice "esto está en curso"); `<meter>` para porcentaje de completitud de una tarea.
- **Error común de IA:** la barra de `<div>` anidados con `style="width: 60%"` — invisible para lectores de pantalla.
- **Por qué:** ambos exponen valor, mínimo y máximo a la accesibilidad sin ARIA manual; `<progress>` sin `value` da estado indeterminado nativo (la animación de "cargando" gratis).
```html
✅ <progress max="100" value="60">60%</progress>
✅ <meter min="0" max="10" low="4" optimum="9" value="8">8/10</meter>
```

### `<address>`
**[RECOMMENDED]** Datos de contacto del autor/dueño del `<article>` o de la página (típico: footer con email, teléfono, dirección física de la empresa).
- **Cuándo NO:** direcciones postales arbitrarias dentro del contenido (la dirección de un envío, la sede de un evento) — `<address>` significa "contacto de este contenido", no "cualquier dirección".
- **Error común de IA:** el bloque de contacto del footer como `<div class="contact-info">`; o al revés, envolver toda dirección postal del contenido en `<address>`.
- **Por qué:** identifica de forma legible por máquinas a quién contactar por esta página/artículo — señal que consumen lectores y crawlers.
```html
✅ <footer><address>Acme SA — <a href="mailto:hola@acme.com">hola@acme.com</a></address></footer>
```

### `<dl>` / `<dt>` / `<dd>` vs `<ul>`/`<ol>`
**[REQUIRED]** Pares nombre→valor (specs de producto, metadata de un pedido, glosarios, la típica grilla "Estado: Activo / Plan: Pro") → `<dl>` con `<dt>` (término) y `<dd>` (valor). Ítems homogéneos sin estructura clave-valor → `<ul>`; si el orden importa (pasos, ranking) → `<ol>` (ya normado en HTML_STRUCTURE sección 8).
- **Cuándo NO:** `<dl>` para diálogos o pares arbitrarios que no son término→definición/clave→valor real.
- **Error común de IA:** la grilla de detalles como `<div class="grid"><span class="label">Estado</span><span>Activo</span>…</div>` — visualmente igual, semánticamente nada.
- **Por qué:** el lector de pantalla asocia cada `<dd>` con su `<dt>` ("Estado: Activo" como par, no como dos textos sueltos). Se puede seguir maquetando con Grid: CSS sobre `<dl>` funciona igual que sobre `<div>`.
```html
✅ <dl class="grid grid-cols-2"><dt>Estado</dt><dd>Activo</dd><dt>Plan</dt><dd>Pro</dd></dl>
```

---

## 6. `<search>` (landmark de búsqueda)

**[RECOMMENDED]** El bloque de búsqueda del sitio/app se envuelve en `<search>` (elemento del HTML Living Standard, soporte universal en navegadores desde 2023; equivale a `role="search"`).
- **Cuándo usar:** buscador global del navbar, búsqueda/filtrado de una tabla o listado.
- **Cuándo NO:** el formulario de un solo campo que no busca (newsletter) — `<search>` implica búsqueda/filtrado.
- **Error común de IA:** `<div class="search-bar">` — se pierde el landmark: los usuarios de lector de pantalla saltan directo a "búsqueda" igual que a "navegación".
- **Por qué:** completa el mapa de landmarks de HTML_STRUCTURE sección 12; el buscador es de los destinos más frecuentes de una página.
```html
✅ <search><form role="none" action="/buscar"><label for="q">Buscar</label><input type="search" id="q" name="q" /><button type="submit">Buscar</button></form></search>
```

---

## 7. Anti-patrones resumidos

- ❌ Modal, acordeón, barra de progreso o dropdown reconstruidos con `<div>` + JS cuando existe `<dialog>`, `<details>`, `<progress>`, `<select>`.
- ❌ `type="text"` para email, teléfono, fechas o números; `type="number"` para códigos que no se operan matemáticamente.
- ❌ Grupos de radios/checkboxes sin `<fieldset>`/`<legend>`.
- ❌ Fechas visibles sin `<time datetime>`.
- ❌ Pares clave→valor maquetados con spans en vez de `<dl>`.
- ❌ Citas y testimonios sin `<blockquote>`; código sin `<code>`/`<pre>`.
- ❌ `<section>` como sinónimo decorativo de `<div>` (section-soup).
- ❌ Buscador sin landmark `<search>`.

---

## Checklist rápido

- [ ] ¿Ningún `<div>`/`<span>` donde la tabla de la sección 1 indica un elemento semántico?
- [ ] ¿`<nav>` múltiples con `aria-label` distintos; `<section>` solo con tema/heading propio; ítems autocontenidos en `<article>`?
- [ ] ¿Navegación en `<a>`, acciones en `<button>` (con `type` explícito dentro de forms)?
- [ ] ¿Modales con `<dialog>` + `showModal()`; colapsables con `<details>`/`<summary>`?
- [ ] ¿Formularios con `<form>` + submit, grupos de opciones con `<fieldset>`/`<legend>`, todo campo con `<label>` asociado?
- [ ] ¿`type` e `inputmode`/`autocomplete` correctos en cada input; `<select>` solo para listas cerradas medianas?
- [ ] ¿Resultados calculados en `<output>`?
- [ ] ¿`<figure>`/`<figcaption>` para imágenes con leyenda; `<picture>` solo para formatos alternativos o art direction?
- [ ] ¿Fechas en `<time datetime>`; resaltado contextual en `<mark>`; citas en `<blockquote>`?
- [ ] ¿Código en `<code>`/`<pre>`; teclas en `<kbd>`; progreso en `<progress>`; mediciones en `<meter>`?
- [ ] ¿Contacto en `<address>`; pares clave→valor en `<dl>`/`<dt>`/`<dd>`?
- [ ] ¿Buscador envuelto en `<search>`?
