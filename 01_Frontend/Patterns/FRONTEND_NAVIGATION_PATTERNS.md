---
title: "Patrones de Navegación"
category: 01_Frontend
tags: [frontend, navegacion, navbar, sidebar]
summary: "Árbol y matriz de decisión para elegir el patrón de navegación principal según el tipo de producto, reglas transversales y patrones complementarios fuera del navbar y el sidebar."
keywords: [navegacion, navbar, sidebar, menu, breadcrumb, tabs, decision]
updated: 2026-07-27
status: current
---

# FRONTEND NAVIGATION PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Igual que con Cards ([FRONTEND_UI_PATTERNS.md](FRONTEND_UI_PATTERNS.md)), la navegación tiene un patrón por defecto sobrerrepresentado (navbar horizontal clásico) que no siempre es el correcto. Este documento cataloga las variantes reales, cuándo usar cada una, cuándo evitarla, y las reglas transversales para no romper lo básico.

---

## 1. Árbol de decisión

**[REQUIRED]** Antes de elegir un patrón de navegación, recorrer este árbol — no partir directo del navbar clásico porque es el más común.

```
¿Qué tipo de producto es?
│
├─ Landing / marketing
│    └─ ¿Menos de ~7 secciones?
│         Sí → Navbar clásico (2.1)
│         No → Navbar + Mega Menu (2.9), agrupar en dropdown
│
├─ Dashboard / panel interno
│    └─ ¿El usuario pasa horas trabajando ahí?
│         Sí → Sidebar (2.7) o Top + Sidebar (2.8)
│         No (uso ocasional, pocas pantallas) → Navbar simplificado
│
├─ App / producto mobile-first
│    └─ Bottom Navigation (sección 5)
│
└─ Herramienta para usuarios avanzados (editor, IDE, panel técnico denso)
     └─ Command Palette (sección 5) + navegación mínima visible

Independiente del tipo de producto:
¿Una sección del navbar tiene más de ~20 ítems? → Mega Menu (2.9), nunca un dropdown simple sobrecargado
```

---

## 2. Matriz de decisión rápida

**[RECOMMENDED]** Referencia directa cuando ya se sabe el tipo de producto — los ejemplos reales son para entender el contexto de uso, no para copiar literal.

| Producto | Patrón recomendado | Ejemplos reales |
|---|---|---|
| Landing / marketing | Navbar clásico | Stripe, Vercel |
| Dashboard / SaaS interno | Sidebar, o Top + Sidebar | GitHub, Supabase |
| CRM / múltiples módulos | Sidebar + Topbar | Notion, Linear |
| E-commerce | Navbar + Mega Menu | — |
| Blog / editorial | Navbar clásico | — |
| Portfolio / marca personal | Minimal | — |
| App mobile-first | Bottom Navigation | Apps nativas iOS/Android |
| Editor / herramienta avanzada | Command Palette | VS Code, Linear, Raycast |

---

## 3. Regla principal

**[REQUIRED]** El patrón de navegación se elige según el tipo de producto y su profundidad (cuántas secciones/niveles tiene) — usando el árbol de la sección 1 — no se copia el navbar clásico por costumbre.

---

## 4. Patrones de navegación principal

### 4.1 Navbar clásico

```
Logo     Inicio  Servicios  Precios  Contacto     [Iniciar sesión] [Comenzar]
```

**[RECOMMENDED]** para landing, SaaS y sitios corporativos — es el patrón más reconocible, el usuario no tiene que aprenderlo. **Casos reales:** Stripe, Vercel.

### 4.2 Navbar centrado

```
              Logo
Inicio   Productos   Soporte   Empresa        Buscar
```

**[RECOMMENDED]** cuando la marca es el foco (estilo Apple) — da sensación premium, pero requiere que el logo sea fuerte por sí solo.

### 4.3 Navbar dividido

```
Inicio  Productos          LOGO          Contacto  Login
```

**[RECOMMENDED]** variante elegante de la clásica, usa el logo como punto de equilibrio visual en vez de esquina izquierda.

### 4.4 Minimal

```
LOGO                                                    ☰
```

**[RECOMMENDED]** cuando el contenido debe dominar sin distracción (portfolio, editorial, landing de producto muy visual) — toda la navegación vive detrás de un solo trigger.

### 4.5 Navbar transparente sobre el Hero

```
Antes de scroll (sobre imagen del Hero):     Después de hacer scroll:
──────────────────────────────               █████████████████████
LOGO   Inicio  Servicios  Contacto            LOGO   Inicio  Servicios  Contacto
──────────────────────────────               █████████████████████
```

**[RECOMMENDED]** para landings con Hero visual fuerte (imagen/video de fondo). **[REQUIRED]** si se usa, el contraste del texto de navegación sobre la imagen debe validar AA igual que cualquier texto (ver `FRONTEND_ENGINEERING_STANDARD.md` 13.4) — y cambia a fondo sólido al hacer scroll, nunca se queda transparente sobre contenido claro.

### 4.6 Floating navbar

```
        ╭────────────────────────────╮
        │ LOGO   Inicio  Productos  Contacto │
        ╰────────────────────────────╯
```

**[RECOMMENDED]** estética moderna (Apple, Vercel) — no toca los bordes del viewport, flota con margen. Encaja bien con estilos Glassmorphism/Aurora del [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md). **Casos reales:** Apple, Vercel, Linear (sitio de marketing).

**Cuándo NO usarlo:**
- Aplicaciones internas — el margen flotante resta espacio vertical, y ahí el espacio es crítico (el usuario lo usa horas, no segundos).
- Cuando hay muchas acciones/enlaces — el floating funciona con navegación corta; con 6-7 ítems + CTA ya se ve apretado.
- Dashboards de uso intensivo — prioriza densidad de información sobre estética.

### 4.7 Sidebar navigation

```
LOGO
Dashboard
Usuarios
Productos
Reportes
Configuración
```

**[REQUIRED]** para dashboards y paneles de administración con 5+ secciones — ver `FRONTEND_UI_PATTERNS.md` secciones 3.2 y 3.8 (Dashboards, Settings). **Casos reales:** GitHub (navegación de repositorio), Supabase, Notion.

**Cuándo NO usarlo:**
- Landing o sitio de contenido — un sidebar permanente hace que un sitio simple se sienta (y pese) como una app.
- Menos de 4-5 secciones — el overhead de un sidebar fijo no se justifica; un navbar simple alcanza.
- Mobile — el sidebar colapsa a otro patrón (drawer o bottom nav), nunca se muestra fijo en pantallas angostas.

Variantes (clásico, colapsable, agrupado, con submenús, híbrido), jerarquía interna y arquitectura de información completas en [FRONTEND_SIDEBAR_PATTERNS.md](FRONTEND_SIDEBAR_PATTERNS.md).

### 4.8 Top + Sidebar

```
─────────── Top: Buscar · Perfil ───────────
Dashboard
Usuarios
Reportes
```

**[RECOMMENDED]** para la mayoría de paneles administrativos con múltiples módulos: el top bar lleva búsqueda global y perfil/cuenta, el sidebar lleva la navegación estructural. No es la única opción válida — herramientas como Figma, Trello o Jira usan variantes con menos chrome fijo (toolbar contextual, board-first) porque el contenido central (el board, el canvas) es el protagonista, no la navegación entre módulos.

### 4.9 Mega menu

```
Productos ▾
──────────────────────
Producto A   Documentación
Producto B   Recursos
Producto C
──────────────────────
```

**[RECOMMENDED]** solo cuando una sección del navbar clásico ya no alcanza — más de ~20 ítems en una categoría que no caben en un dropdown simple. **Casos reales:** e-commerce grandes, sitios corporativos con múltiples líneas de producto.

**Cuándo NO usarlo:**
- Menos de 20 ítems en la categoría — un dropdown simple es más rápido de escanear.
- Mobile — un mega menu no se adapta bien a pantallas angostas; ahí colapsa a un acordeón dentro del menú mobile.

---

## 5. Reglas transversales

### 5.1 Máximo de enlaces principales

**[RECOMMENDED]** 6-7 enlaces de primer nivel como máximo. Lo que no entra, se agrupa en un dropdown o mega menu ("Más", o una categoría contenedora).

**Por qué:** más opciones visibles no ayudan a decidir más rápido — abruma y diluye la opción que realmente importa (el CTA).

```
❌ Inicio · Nosotros · Servicios · Cursos · Academia · Clientes · Casos · Blog · Noticias · Eventos · Partners · Contacto
✅ Inicio · Servicios · Precios · Recursos ▾ · Contacto        [Comenzar]
```

### 5.2 Jerarquía de acciones — un solo CTA destacado

**[REQUIRED]** Nunca dos botones con el mismo peso visual en la navegación. La acción secundaria (`Iniciar sesión`) va como texto o botón ghost; la acción primaria (`Comenzar`, `Registrarse`) lleva el color de marca — misma regla de jerarquía de CTA que `FRONTEND_LANDING_PATTERNS.md` 4.1.

### 5.3 Logo

**[REQUIRED]** El logo siempre es clicable y siempre navega a la raíz (home o dashboard principal, según el tipo de producto).

### 5.4 Sticky vs fijo vs estático

**[RECOMMENDED]** En landing, un navbar sticky (se mantiene visible al hacer scroll) suele mejorar la conversión — el CTA nunca desaparece. **[REQUIRED]** en dashboard/app, la navegación (sidebar o top bar) es fija siempre — el usuario la necesita disponible mientras trabaja, no solo al llegar. **[REQUIRED]** el bloque sticky/fijo no ocupa más del ~10% de la altura del viewport — si crece más que eso, está compitiendo con el contenido que el usuario vino a ver.

### 5.5 Mobile nunca copia el layout de desktop

**[REQUIRED]** El patrón mobile se diseña como su propia versión, no se encoge el navbar de desktop. **[REQUIRED]** define explícitamente qué se mantiene siempre visible (típicamente: logo + CTA principal + trigger de menú) y qué se mueve detrás del menú — nunca se ocultan elementos "porque no caben" sin decidir la prioridad, y nunca se oculta navegación importante sin dejar al menos el trigger del menú como reemplazo accesible.

```
Desktop:  Logo   Inicio  Servicios  Precios  Contacto   [Comenzar]
Mobile:   Logo                                [Comenzar]   ☰
```

### 5.6 Jerarquía interna

**[REQUIRED]** Orden de importancia visual dentro del navbar: Logo → Navegación → CTA. No se mezclan (ej. un link de navegación con más peso visual que el CTA).

### 5.7 Espaciado

**[REQUIRED]** Se aplica `FRONTEND_ENGINEERING_STANDARD.md` 1.1 — el espaciado interno del navbar (gap entre links, padding) sale de la escala fija, nunca de un valor libre (`margin-left: 53px`).

### 5.8 Responsive con prioridad explícita

**[REQUIRED]** Qué se oculta primero en pantallas angostas es una decisión de producto, no un accidente de que "ya no cabe". Se define qué elementos son prescindibles (ej. links secundarios antes que el CTA) antes de implementar los breakpoints.

---

## 6. Otros patrones de navegación (fuera del navbar/sidebar)

| Patrón | Cuándo usarlo | Casos reales |
|---|---|---|
| Bottom Navigation | Apps móvil-first con 3-5 secciones raíz — el pulgar alcanza el borde inferior más fácil que el superior | Apps nativas iOS/Android |
| Breadcrumbs | Jerarquías profundas (3+ niveles) — permite volver atrás sin depender del botón del navegador | — |
| Tabs | Alternar entre vistas relacionadas dentro del mismo contexto/pantalla | — |
| Stepper | Procesos multi-paso donde el usuario debe ver en qué paso está (checkout, onboarding) | — |
| Pagination | Listados largos paginados desde el servidor | — |
| Wizard Navigation | Flujo guiado obligatorio, paso a paso, sin saltos libres (setup inicial complejo) | — |
| Context Menu | Acciones secundarias sobre un ítem específico (clic derecho o menú de 3 puntos) | — |
| Dropdown Menu | Opciones agrupadas bajo un trigger, cuando no ameritan espacio permanente en pantalla | — |
| Drawer | Panel deslizante temporal (carrito, filtros, detalle rápido) sin abandonar la pantalla activa | — |
| Command Palette (⌘K) | Power users en apps densas que prefieren teclado sobre clics — **evitar** si el público no es técnico o el uso es esporádico | VS Code, Linear, Raycast, Notion |
| Dock Navigation | Apps tipo herramienta creativa con muchas acciones frecuentes — poco común, evaluar con cuidado antes de usarlo | — |
| FAB (Floating Action Button) | Una sola acción primaria muy frecuente en mobile (ej. "crear nuevo") | — |

---

## 7. Anti-patrones

**[REQUIRED]** Ninguno de estos entra en producción sin una razón documentada explícita:

- ❌ Navbar con más de 7-8 enlaces sin agrupar — abruma y diluye el CTA (5.1).
- ❌ Dos CTA con el mismo peso visual — el usuario no sabe cuál es la acción principal (5.2).
- ❌ Logo que no navega a home — rompe una expectativa universal de navegación (5.3).
- ❌ Bloque sticky/fijo que ocupa más del ~10% de la altura del viewport — resta espacio al contenido real (5.4).
- ❌ Menú hamburguesa en desktop cuando sobra espacio para mostrar los enlaces — esconder navegación sin necesidad no es "limpio", es fricción.
- ❌ Ocultar navegación importante en mobile sin dejar un reemplazo accesible (ni un trigger de menú) — el usuario se queda sin forma de navegar (5.5).
- ❌ Menús de 3+ niveles anidados en una landing simple — sobre-ingeniería para el volumen de contenido real.
- ❌ Sidebar permanente en una landing o sitio de pocas páginas — confunde el tipo de producto y quita espacio (4.7).

---

## 8. Por qué este documento existe — Componentes vs Patrones

El handbook piensa en dos niveles, no en una lista plana de piezas:

```
Nivel de Componentes (FRONTEND_ENGINEERING_STANDARD.md sección 04)
  Button · Input · Card · Avatar · Badge
              ↓ se combinan para formar
Nivel de Patrones (este documento + FRONTEND_UI_PATTERNS.md + FRONTEND_LANDING_PATTERNS.md)
  Navbar · Hero · Dashboard · CRUD · Pricing · Timeline · FAQ · Auth · Settings · Wizard · Profile · Checkout
```

Un componente es una pieza pequeña y genérica. Un patrón es la combinación específica de componentes que resuelve un problema de UX completo (cómo se navega, cómo se muestra confianza, cómo se compra). Diseñar pensando solo en componentes produce interfaces ensambladas sin criterio — "necesito una Card" en vez de "necesito mostrar un proceso" — mientras que pensar en patrones obliga a preguntar primero "¿qué problema de UX estoy resolviendo?" antes de "¿qué pieza uso?".

---

## Checklist rápido antes de implementar una navegación

- [ ] ¿Recorrí el árbol de decisión (sección 1) en vez de partir del navbar clásico por costumbre?
- [ ] ¿El patrón elegido corresponde al tipo de producto, con casos reales de referencia que tengan sentido para ese contexto?
- [ ] ¿Máximo 6-7 enlaces de primer nivel, resto agrupado?
- [ ] ¿Un solo CTA con peso visual destacado, nunca dos botones iguales?
- [ ] ¿Logo clicable, navega a home/raíz?
- [ ] ¿Sticky en landing, fijo en dashboard/app, sin superar ~10% del alto del viewport?
- [ ] ¿Versión mobile diseñada aparte, con prioridad explícita de qué se oculta primero y un reemplazo accesible?
- [ ] ¿Jerarquía Logo → Navegación → CTA respetada?
- [ ] ¿Espaciado interno en la escala fija del design system?
- [ ] ¿Ningún anti-patrón de la sección 7 presente sin justificación documentada?
