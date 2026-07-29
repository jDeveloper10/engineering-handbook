---
title: "Patrones de UI por Tipo de Contenido"
category: 01_Frontend
tags: [frontend, ui, patrones, cards]
summary: "Tabla de decisión que mapea tipo de contenido a patrón de presentación, patrones por tipo de página o módulo, cuándo sí corresponde una card y reglas de prueba social."
keywords: [patrones, cards, listas, comparacion, social-proof, decision, maquetado]
updated: 2026-07-27
status: current
---

# FRONTEND UI PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Este documento existe porque ciertos patrones de UI están sobrerrepresentados en los datos con los que se entrena una IA — Cards y Logo Clouds son los dos ejemplos más comunes — así que ante la duda una IA los genera para casi cualquier contenido, no porque sean la mejor opción. Este documento obliga a elegir el patrón por el tipo de información y el objetivo real de la pantalla, no por el componente más visto en el ecosistema de referencia (Stripe, Vercel, Linear, Notion, Tailwind UI...).

---

## 1. Regla principal

**[REQUIRED]** No elegir un patrón de UI porque es popular o porque aparece en la mayoría de landings/dashboards de referencia. Elegirlo porque es el más adecuado para el tipo de información y el objetivo de esa pantalla. Antes de diseñar una sección:

1. Identificar el tipo de información (¿son ítems comparables e independientes? ¿es una secuencia? ¿es una comparación de atributos? ¿son datos densos? ¿hay contenido real que sostenga el patrón, o solo 3-4 elementos sueltos?).
2. Elegir el patrón de la tabla de la sección 2 según ese tipo.
3. Si el patrón elegido coincide con el más común para ese caso (Cards para catálogo, Logo Cloud para prueba social), esa elección queda justificada por el contenido — no por costumbre.

**Por qué:** una interfaz donde todo es un grid de cards del mismo tamaño le da el mismo peso visual a todo, sin importar qué tan importante es cada cosa. Una sección de Logo Cloud con 4 logos sueltos en media pantalla vacía es el mismo problema con otro nombre: un patrón replicado porque "así se ve en Stripe/Vercel/Linear", sin que el contenido real lo sostenga. El resultado son landings que parecen "página de figuritas" o con huecos vacíos, en vez de comunicar jerarquía. Productos de referencia reales usan secciones con composición asimétrica, tablas, timelines, métricas — el patrón de moda solo donde el contenido lo justifica.

---

## 2. Tabla de decisión: tipo de contenido → patrón

**[REQUIRED]** Consultar esta tabla antes de maquetar cualquier sección nueva.

| Tipo de contenido | Patrón recomendado | Evitar | Por qué |
|---|---|---|---|
| Catálogo de productos | Cards (grid) | — | Ítems comparables, mismo peso, se escanean en paralelo |
| Servicios / beneficios | Feature Sections (secciones alternadas, split layout) o Bento Grid | 6 cards idénticas | Cada servicio necesita espacio para explicarse, no competir por atención igual que los demás |
| Proceso / cómo funciona | Timeline | Cards numeradas en grid | El orden y la progresión son la información clave, no ítems independientes |
| Roadmap | Timeline | Cards por etapa | Igual que proceso — la secuencia importa más que cada etapa aislada |
| Comparación de planes/productos | Tabla comparativa | Cards una al lado de otra | Comparar atributos requiere alinearlos en columnas/filas legibles |
| Precios | Pricing Table | Cards de precio "normales" (aceptable en landings simples de 2-3 planes) | Con 4+ planes o muchos features, una tabla evita repetir la misma lista en cada card |
| Dashboard / analítica | KPI tiles + gráficos + tabla | Todo en cards de texto | Datos densos necesitan visualización real (gráfico, tabla), no contenedores decorativos |
| FAQ | Accordion | Cards con preguntas | El contenido colapsable ahorra espacio; cards lo expone todo sin necesidad |
| Equipo | Lista de perfiles (vertical o fila) | Cards enormes con mucho padding | El foco es la persona + rol, no un contenedor decorativo |
| Testimonios | Carrusel o cita destacada única | Grid de cards de testimonio (aceptable si son 3 o menos) | Muchos testimonios en grid compiten entre sí; uno o dos bien destacados generan más confianza |
| Confianza / prueba social | Métricas + logos compactos, testimonio destacado, o certificaciones (ver sección 5) | Logo Cloud aislado ocupando media pantalla | Si solo hay 3-4 logos, la sección queda vacía y el usuario solo la scrollea para pasarla — no aporta jerarquía ni información real |
| Casos de éxito | Story layout (narrativa: contexto → problema → solución → resultado) | Cards genéricas | Un caso de éxito es una historia, no un dato aislado |
| Galería / portafolio | Masonry grid o Showcase | — | Aquí sí el contenido es naturalmente una colección visual |
| Búsqueda | Barra de búsqueda + resultados, o Command Palette para búsqueda global en apps | Resultados en cards decorativas | La densidad de resultados importa más que la decoración |
| Datos tabulares (listados admin) | Data table (ordenable, paginada) — ver [FRONTEND_TABLE_PATTERNS.md](FRONTEND_TABLE_PATTERNS.md) | Cards por fila en desktop | Una tabla permite escanear y comparar columnas; cards obligan a leer una por una |
| Estado vacío | Empty State dedicado (ilustración/ícono + mensaje + CTA) — ver [FRONTEND_STATES_PATTERNS.md](FRONTEND_STATES_PATTERNS.md) | Card vacía con texto genérico | El vacío es un momento de guía al usuario, no un contenedor más |

---

## 3. Patrones por tipo de página o módulo

### 3.1 Landing pages

Cubierto en [FRONTEND_LANDING_PATTERNS.md](FRONTEND_LANDING_PATTERNS.md) — la nota específica de este documento: la sección de Features/Beneficios de una landing **no** es automáticamente un grid de N cards iguales. Aplicar la tabla de la sección 2: si son 3-4 beneficios con espacio para explicar cada uno, usar Feature Sections alternadas (texto + imagen, invirtiendo el lado en cada bloque). Cards de beneficio solo si son 6+ ítems cortos y realmente comparables entre sí (ej. íconos + una línea cada uno).

```
❌ Servicios en grid de cards idénticas:
┌──────┐ ┌──────┐ ┌──────┐
│Card 1│ │Card 2│ │Card 3│
└──────┘ └──────┘ └──────┘

✅ Feature section alternada (estilo Stripe/Apple):
════════════════════════════════════
Título del beneficio
Texto explicando el beneficio en 2-3 líneas.
✔ Detalle 1   ✔ Detalle 2   ✔ Detalle 3
                                    [Imagen/mockup grande]
════════════════════════════════════
                  [Imagen/mockup grande]
Título del siguiente beneficio (invertido)
Texto explicando...
════════════════════════════════════
```

### 3.2 Dashboards

**[REQUIRED]** Estructura: fila de KPI tiles (métricas clave, 3-5 números grandes) → gráfico(s) de tendencia → tabla de detalle. **[REQUIRED]** los datos tabulares (transacciones, usuarios, pedidos) se muestran en una tabla real, no en cards una debajo de otra. Detalle completo en [FRONTEND_DASHBOARD_PATTERNS.md](FRONTEND_DASHBOARD_PATTERNS.md).

```
✅                                    ❌
┌KPI┐ ┌KPI┐ ┌KPI┐                    Card
──────────────                        Card
   Gráfico                            Card
──────────────                        Card
   Tabla                              Card (x50, una por fila de datos)
```

### 3.3 CRUD (listado + detalle)

**[REQUIRED]** Vista de listado: buscador + filtros + tabla + paginación — no un grid de cards por registro. **[RECOMMENDED]** al seleccionar un registro: layout Master-Detail (tabla a la izquierda, panel de detalle a la derecha) en desktop, o navegación a una vista de detalle dedicada — nunca una card que se expande con todos los campos del registro apilados. Detalle completo en [FRONTEND_CRUD_PATTERNS.md](FRONTEND_CRUD_PATTERNS.md).

```
Listado:  Buscar · Filtros · [Tabla] · Paginación
Detalle:  ┌─────────────┬─────────────┐
          │ Tabla        │ Detalle     │
          └─────────────┴─────────────┘
```

### 3.4 Formularios

Cubierto en `FRONTEND_ENGINEERING_STANDARD.md` sección 09 (Forms Rules) — sin patrón adicional aquí más allá de: un formulario largo no se corta en cards por sub-sección salvo que cada sub-sección sea un paso independiente de un wizard.

### 3.5 Autenticación (login/registro)

Cubierto en detalle en [FRONTEND_AUTH_PATTERNS.md](../Core/FRONTEND_AUTH_PATTERNS.md) — layouts, orden de campos, seguridad UX, recuperación de cuenta y accesibilidad específica. Nota rápida: el formulario de auth no necesita el contenedor visual de una card decorativa (sombras, bordes redondeados grandes) — es una tarea de una sola acción, no contenido para escanear.

### 3.6 E-commerce

**[RECOMMENDED]** El catálogo de productos sí usa Cards (ver sección 2 — es el caso donde el patrón es correcto). Los filtros van en un sidebar o panel colapsable, no en cards. El carrito es un drawer/panel lateral, no una card en el flujo de la página.

### 3.7 Perfil de usuario

**[RECOMMENDED]** Layout de dos columnas o tabs: avatar + info básica en un bloque, acciones/secciones en otro. No una sola card gigante que apila avatar, datos, preferencias y acciones sin separación visual.

### 3.8 Configuración (Settings)

**[REQUIRED]** Sidebar de navegación por categoría (General, Usuarios, Seguridad, Notificaciones) + panel de formulario a la derecha con la categoría activa — patrón Master-Detail. **[REQUIRED]** no una card por categoría de configuración en la misma pantalla.

### 3.9 Navegación

**[RECOMMENDED]** Sidebar para apps con profundidad (dashboards, admin), navbar horizontal para sitios de pocas secciones, tabs para alternar vistas dentro de una misma pantalla. La navegación nunca se resuelve como una lista de cards clicables. Árbol de decisión completo y catálogo de patrones en [FRONTEND_NAVIGATION_PATTERNS.md](FRONTEND_NAVIGATION_PATTERNS.md).

### 3.10 Gráficos y series de tiempo

**[REQUIRED]** Tendencias y series de tiempo se muestran con un gráfico real (línea, barra, área), no se intenta comunicar una tendencia con texto dentro de una card.

---

## 4. Cuándo sí usar Cards

Esta regla no prohíbe las cards — evita que sean el default automático. Son el patrón correcto cuando el contenido cumple **todas** estas condiciones:

- Los ítems son genuinamente comparables entre sí (mismo tipo de cosa: productos, posts, resultados de búsqueda, miniaturas de galería).
- El usuario necesita escanear varios en paralelo, no leer uno en profundidad.
- Cada ítem tiene aproximadamente el mismo peso de información (no uno con 3 líneas y otro con un párrafo).
- La cantidad es lo bastante grande (4+) como para que una tabla o timeline sería igual de forzada.

Ejemplo correcto: catálogo de productos, resultados de búsqueda, grid de posts de blog, galería de miniaturas.

---

## 5. Social Proof Rules

**[REQUIRED]** No usar Logo Cloud (fila de logos de clientes) como sección independiente de altura completa por defecto.

**Por qué:** el mismo sesgo que con Cards — Stripe, Vercel, Linear, Notion, OpenAI, Framer y Tailwind UI (referencias muy presentes en el entrenamiento de cualquier IA) usan una sección "Trusted by" con fila de logos, así que se replica el patrón aunque el proyecto real solo tenga 3-4 logos disponibles. El resultado: media pantalla casi vacía, con mucho espacio en blanco alrededor de 4 nombres, que el usuario solo scrollea para pasar. Eso es mala jerarquía visual — la sección ocupa peso visual que no está respaldado por contenido real.

**[REQUIRED]** Antes de usar logos para comunicar confianza, evaluar si el mensaje se transmite mejor con: métricas, un testimonio destacado, un caso de éxito, o certificaciones — cuál de estos tiene contenido real disponible y comunica más.

**[REQUIRED]** Si finalmente se usan logos:
- Deben complementar información (métricas o texto), nunca aparecer solos flotando en espacio vacío.
- No ocupar más del 10-15% del alto visible de la pantalla (viewport height).
- Sin grandes espacios en blanco alrededor — si el contenido es poco, el bloque debe ser compacto, no estirado para "llenar" una sección completa.

**Implementación — 4 variantes válidas, de mejor a más simple:**

```
Opción 1 — métricas + logos combinados (la más recomendada si hay datos reales):
   +2,400        $18M         97%          4.9★
   Traders       Volumen      Satisfacción  Calificación
   ────────────────────────────────────────────
   Nova Capital   Quantix   Rivera FX   Apex Trade

Opción 2 — testimonio destacado (si hay una cita fuerte, comunica más que logos):
   ★★★★★
   "Llevamos 18 meses usando la plataforma."
   Juan Pérez — CEO, Nova Capital

Opción 3 — franja pequeña de logos entre otras secciones (no una sección propia):
   Hero → Features → [franja de logos, ~40px de alto] → Más contenido

Opción 4 — logos integrados y compactos:
   Trabajamos con:  Nova · Quantix · Rivera        +2,400 traders activos
```

**Aplica también a:** `FRONTEND_LANDING_PATTERNS.md` sección 1, bloque "Social proof" — el bloque solo entra en el orden de la landing si hay contenido real que lo sostenga (métricas, logos con permiso de uso, testimonio); si no, se omite en vez de rellenarlo con espacio vacío.

---

## Checklist rápido antes de maquetar una sección nueva

- [ ] ¿Identifiqué el tipo de información antes de elegir el componente?
- [ ] ¿Consulté la tabla de la sección 2 en vez de usar Cards por default?
- [ ] Si elegí Cards, ¿cumple las 4 condiciones de la sección 4?
- [ ] ¿Datos tabulares en tabla real, no en cards apiladas?
- [ ] ¿Procesos/roadmaps en timeline, no en cards numeradas?
- [ ] ¿Comparaciones (precios, planes, productos) en tabla, no en cards paralelas repitiendo la misma lista?
- [ ] ¿La sección de beneficios de una landing tiene jerarquía visual real, o es un grid de N cards iguales?
- [ ] ¿La prueba social combina métricas/testimonio con los logos, en vez de un Logo Cloud aislado con espacio vacío?
- [ ] ¿Elegí cada patrón por el contenido disponible, no por costumbre del ecosistema de referencia?
