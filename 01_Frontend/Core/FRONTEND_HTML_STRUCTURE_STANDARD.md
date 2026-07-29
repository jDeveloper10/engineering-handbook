---
title: "Estándar de Estructura HTML Semántica"
category: 01_Frontend
tags: [frontend, html, semantica, accesibilidad]
summary: "Estructura base de una página con HTML5 semántico: qué etiqueta usa cada región, jerarquía de headings, un solo h1 por página y cuándo corresponde button frente a enlace."
keywords: [html5, semantica, landmarks, headings, h1, button, accesibilidad]
updated: 2026-07-27
status: current
---

# FRONTEND HTML STRUCTURE STANDARD (Semantic HTML)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 13.1) y del estándar [W3C/WHATWG HTML Living Standard](https://html.spec.whatwg.org/) — este documento no inventa reglas, traduce el estándar oficial de la plataforma web a reglas verificables. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> A diferencia de otros documentos del handbook, estas reglas no tienen "capa de implementación" separada por framework — HTML semántico es idéntico en React, Vue, HTML plano o cualquier stack, porque la regla vive en la etiqueta misma, no en cómo se genera.
>
> Por qué existe: la IA (y muchos devs) por defecto genera `<div><div><div>` anidados porque es la opción más "segura" y flexible — exactamente el mismo sesgo que con Cards ([FRONTEND_UI_PATTERNS.md](../Patterns/FRONTEND_UI_PATTERNS.md)). Un `<div>` no comunica nada al navegador, a un lector de pantalla, ni a un motor de búsqueda. Las etiquetas semánticas sí.

---

## 1. Regla principal

**[REQUIRED]** Usar la etiqueta HTML semántica correcta antes de recurrir a `<div>`. Un `<div>` solo se usa cuando no existe una etiqueta con significado apropiado para ese contenido (ej. un wrapper puramente de layout sin significado propio).

---

## 2. Estructura base de una página

**[REQUIRED]**

```
<body>
  <header>...</header>
  <nav>...</nav>
  <main>
    <section>...</section>
    <section>...</section>
  </main>
  <aside>...</aside>
  <footer>...</footer>
</body>
```

```
❌ <div class="header"><div class="navbar"><div class="content"><div class="footer">
✅ <header><nav><main><footer>
```

---

## 3. Cuándo usar cada etiqueta

### `<header>`
Cabecera de una página **o de una sección** (una página puede tener varios `<header>`, uno por cada `<article>`/`<section>` que lo necesite, además del de la página).

### `<nav>`
Solo navegación. **[REQUIRED]** no meter dentro de un `<nav>` formularios, banners promocionales ni imágenes decorativas que no sean parte de la navegación misma.

### `<main>`
**[REQUIRED]** Uno solo por página, siempre. Contiene el contenido principal, no el chrome de la app (sidebar, header, footer quedan fuera).

```
❌ dos <main> en la misma página
✅ un único <main>, con el contenido central de esa vista
```

### `<section>`
Agrupa contenido temáticamente relacionado, típicamente con su propio heading. Ejemplo en una landing: `<section>` para Hero, `<section>` para Pricing, `<section>` para FAQ (ver `FRONTEND_LANDING_PATTERNS.md`).

### `<article>`
Contenido independiente, que tendría sentido por sí solo fuera de contexto (se podría sindicar/reusar). Ejemplos: una noticia, un post de blog, una card de producto, un comentario.

### `<aside>`
Contenido secundario respecto al contenido principal de la página. Ejemplos: un sidebar de navegación (ver [FRONTEND_SIDEBAR_PATTERNS.md](../Patterns/FRONTEND_SIDEBAR_PATTERNS.md)), un panel de branding/testimonio en un layout Split Screen de auth (`FRONTEND_AUTH_PATTERNS.md` 2.1), publicidad, contenido relacionado.

### `<footer>`
Pie de página o de una sección — igual que `<header>`, puede repetirse por sección, no solo al final del documento.

---

## 4. Jerarquía de headings

**[REQUIRED]** Los niveles de heading (`h1`-`h6`) nunca se saltan — se usan en orden descendente según profundidad real del contenido, no según el tamaño visual deseado (el tamaño se controla con CSS, no eligiendo un heading más chico).

```
❌ <h1> → <h3> → <h5>  (saltos de nivel)
✅ <h1> → <h2> → <h3> → <h4>  (jerarquía completa)
```

---

## 5. Un solo `<h1>` por página

**[REQUIRED]** Cada página/vista tiene exactamente un `<h1>` — el título principal de esa pantalla. Ya exigido en `FRONTEND_LANDING_PATTERNS.md` 2.2 para landings; aquí se generaliza a cualquier tipo de página (dashboard, CRUD, auth).

```
❌ <h1>Inicio</h1> ... <h1>Cursos</h1>
✅ <h1>Trading Academy</h1>
```

---

## 6. Elementos interactivos: `<button>` vs `<a>`

**[REQUIRED]**
- Si dispara una acción en la página (guardar, abrir un modal, enviar un formulario) → `<button>`.
- Si navega a otra URL/ruta → `<a>`.

```
❌ <div onclick="save()">Guardar</div>
✅ <button onClick={save}>Guardar</button>

❌ <button onClick={() => navigate("/productos")}>Productos</button>
✅ <a href="/productos">Productos</a>
```

**Por qué:** un `<div>` con `onClick` no es alcanzable por teclado ni anunciado como interactivo por un lector de pantalla sin trabajo extra (`role`, `tabIndex`, manejo manual de `Enter`/`Space`) — `<button>` y `<a>` ya traen ese comportamiento gratis, correcto, y probado por el navegador.

---

## 7. Formularios

**[REQUIRED]** Todo formulario usa `<form>`, cada campo tiene su `<label>` asociado, el envío ocurre por un `<button type="submit">` dentro del `<form>` (permite que `Enter` funcione sin JS adicional — ver `FRONTEND_AUTH_PATTERNS.md` sección 3).

```
❌ <div><input placeholder="Email" /></div>
✅ <form><label for="email">Email</label><input id="email" /><button type="submit">Enviar</button></form>
```

Detalle de validación y estados de formulario en `FRONTEND_ENGINEERING_STANDARD.md` sección 09 — esta regla es solo la estructura semántica base.

---

## 8. Listas

**[REQUIRED]** Contenido repetido/enumerable usa `<ul>`/`<ol>` + `<li>`, no una secuencia de `<div>`.

```
❌ <div>Item 1</div><div>Item 2</div><div>Item 3</div>
✅ <ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>
```

---

## 9. Tablas

**[REQUIRED]** Datos tabulares reales usan `<table><thead><tbody><tr><td>` — nunca se simulan con Grid/Flex de `<div>` cuando el contenido es genuinamente tabular (ver [FRONTEND_TABLE_PATTERNS.md](../Patterns/FRONTEND_TABLE_PATTERNS.md)). **[REQUIRED]** en la dirección inversa: `<table>` nunca se usa para maquetar layout que no es una tabla de datos — esa práctica quedó obsoleta desde que existe CSS Grid/Flexbox.

---

## 10. Imágenes

**[REQUIRED]** `alt` siempre presente — descriptivo si la imagen aporta información, `alt=""` explícito si es puramente decorativa (nunca omitido). **[RECOMMENDED]** `loading="lazy"` salvo en el elemento LCP de la página (ver `FRONTEND_ENGINEERING_STANDARD.md` 1.7 y `FRONTEND_LANDING_PATTERNS.md` 3.1).

---

## 11. Inputs

**[REQUIRED]** Todo `<input>` (y `<select>`, `<textarea>`) tiene un `<label>` asociado vía `for`/`id` — nunca depender solo del `placeholder` como sustituto de label (ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` 9.4 y `FRONTEND_AUTH_PATTERNS.md` 3; esta es la razón semántica de fondo: el `placeholder` desaparece al escribir y no lo leen todos los lectores de pantalla de la misma forma que un `<label>`).

---

## 12. Landmark elements y tecnología de asistencia

**[REQUIRED]** `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` son *landmarks* — un lector de pantalla puede saltar directamente entre ellos (ej. "ir al contenido principal", "ir a la navegación") sin tener que recorrer todo el documento de forma lineal. Cada `<div class="header">` sin la etiqueta real le quita esa capacidad de navegación directa al usuario.

---

## 13. Anti-patrones

- ❌ Todo el árbol de la página hecho con `<div>` anidados sin una sola etiqueta semántica.
- ❌ Botones hechos con `<div>`/`<span>` + `onClick`.
- ❌ Links de navegación hechos con `<button>` (o viceversa).
- ❌ Más de un `<h1>` en la misma página.
- ❌ Saltar niveles de heading (`h1` → `h3`).
- ❌ Formularios sin `<label>` asociado a cada campo.
- ❌ Imágenes sin atributo `alt`.
- ❌ Más de un `<main>` en la misma página.

---

## Checklist rápido

- [ ] ¿La estructura base usa `header`/`nav`/`main`/`section`/`aside`/`footer` en vez de divs con clases descriptivas?
- [ ] ¿Un único `<main>` y un único `<h1>` por página?
- [ ] ¿Jerarquía de headings sin saltos de nivel?
- [ ] ¿Acciones en `<button>`, navegación en `<a>`?
- [ ] ¿Formularios con `<form>`/`<label>`/`<button type="submit">`?
- [ ] ¿Contenido repetido en `<ul>`/`<li>`, datos tabulares en `<table>`?
- [ ] ¿Toda imagen con `alt` (descriptivo o `alt=""`)?
- [ ] ¿Todo input con `<label>` asociado, no solo placeholder?
