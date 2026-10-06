---
title: "Patrones de UI por Tipo de Contenido"
category: 01_Frontend
doc_type: patron
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

## 6. Más Allá de Cards, Menú Hamburguesa y Aside: Taxonomía Exhaustiva de Componentes de Interfaz

**[REQUIRED] REGLA DE DIVERSIDAD DE COMPONENTES (`FE-CARD-001` / `FE-010`):**
Está terminantemente prohibido caer en la "fatiga de cards" (*card fatigue*) o estructurar toda interfaz recurriendo mecánicamente por inercia a **cards idénticas, menú hamburguesa y aside**. El catálogo de una aplicación o web profesional es amplio, modular y multidimensional. Cada necesidad de visualización y flujo debe resolverse con el componente preciso de la siguiente taxonomía:

### 6.1 Taxonomía de Componentes de Interfaz Moderna

1. **Navegación:**
   - `Navbar`: Barra de navegación superior para rutas globales y branding.
   - `Sidebar`: Barra lateral o riel de navegación persistente para aplicaciones con múltiples niveles o herramientas de trabajo.
   - `Bottom Navigation`: Barra de navegación fija inferior para dispositivos móviles (3 a 5 accesos directos principales).
   - `Tabs`: Pestañas para alternar vistas o paneles dentro de un mismo nivel jerárquico sin recargar página.
   - `Breadcrumbs`: Migas de pan que indican la jerarquía de navegación y permiten retroceder niveles.
   - `Mega Menu`: Menú desplegable amplio estructurado por columnas/categorías para catálogos con gran volumen de secciones.
   - `Dropdown Menu`: Menú flotante compacto desplegado al interactuar sobre un botón o disparador.
   - `Command Palette`: Buscador interactivo modal por atajo de teclado (`Ctrl+K` / `Cmd+K`) para acciones y saltos de navegación instantáneos.

2. **Contenido:**
   - `Cards`: Contenedor autocontenido para ítems comparables (exclusivamente si cumple las 4 reglas de la Sección 4).
   - `Accordions`: Paneles colapsables ideales para FAQs o contenido secundario que ahorra espacio vertical.
   - `Carousels / Sliders`: Secuencia horizontal interactiva con controles de paginación/flechas para galerías o testimonios destacados.
   - `Grids`: Rejillas visuales ordenadas para estructurar componentes o imágenes.
   - `Listas`: Disposición vertical limpia con divisores sutiles, óptima para registros, transacciones o configuraciones.
   - `Timelines`: Secuencia cronológica o procedimental conectada con líneas y nodos (procesos, historial, roadmaps).
   - `Steppers`: Indicadores de progreso por pasos para wizards de registro, checkout o flujos secuenciales.
   - `Masonry Layouts`: Disposición en cascada de altura variable, ideal para portafolios visuales o galerías de inspiración.
   - `Feeds`: Flujo continuo de publicaciones, actividad o actualizaciones en orden cronológico inverso.

3. **Acciones:**
   - `Botones (Buttons)`: Botón estándar con variantes jerárquicas (primario, secundario, sutil, peligro).
   - `Floating Action Button (FAB)`: Botón de acción flotante principal fijado en una esquina (habitual en interfaces móviles).
   - `Split Button`: Botón dual que combina una acción primaria predeterminada con una flecha desplegable para variantes.
   - `Icon Button`: Botón compacto representado únicamente por un ícono accesible con `aria-label` obligatorio.
   - `Button Groups`: Conjunto de botones unidos visualmente para opciones mutuamente excluyentes o acciones coordinadas.

4. **Formularios y Captura de Datos:**
   - `Inputs`: Campos de texto, email, password, número y teléfono con validación en tiempo real.
   - `Textarea`: Campo multilínea con autoexpansión para descripciones largas o notas.
   - `Select`: Desplegable nativo para listas cortas y directas.
   - `Autocomplete / Combobox`: Campo de texto con lista filtrable dinámica para conjuntos de datos medios y grandes.
   - `Checkbox`: Selección múltiple de opciones independientes.
   - `Radio`: Selección única dentro de un grupo excluyente.
   - `Switch / Toggle`: Interruptor de activación/desactivación binaria de efecto inmediato.
   - `Range Slider`: Control deslizante para selección intuitiva de valores continuos o rangos numéricos.
   - `Date Picker`: Selector modal o desplegable de fechas y rangos temporales con calendario accesible.
   - `Time Picker`: Selector horario específico con horas y minutos.
   - `File Uploader`: Zona de subida de archivos con previsualización, barra de progreso y validación de tipos MIME y tamaño.
   - `Drag & Drop Zone`: Área interactiva para arrastrar y soltar archivos o reordenar elementos en pantalla.

5. **Ventanas y Capas (Overlays):**
   - `Modal`: Ventana flotante centrada con fondo oscurecido (*backdrop*) que bloquea la interacción subyacente para decisiones críticas.
   - `Dialog`: Ventana modal compacta para confirmaciones destructivas, avisos o preguntas directas (Aceptar / Cancelar).
   - `Drawer`: Panel lateral deslizante que emerge y se oculta fuera del lienzo (*off-canvas*) al activarse.
   - `Sheet`: Panel deslizante contextual (inferior *bottom sheet* en mobile, superior o lateral en desktop).
   - `Off-Canvas`: Contenedor oculto fuera de la pantalla que se desliza al presionar un disparador.
   - `Popover`: Ventana flotante no modal anclada contextualmente a un elemento específico para opciones rápidas.
   - `Tooltip`: Mensaje flotante breve de texto que aparece exclusivamente en hover/focus para aclarar la función de un control.
   - `Context Menu`: Menú flotante secundario que aparece al hacer clic derecho o mantener pulsado sobre un elemento específico.

6. **Feedback y Notificaciones:**
   - `Toast`: Notificación flotante temporal en una esquina, no bloqueante y con cierre automático.
   - `Snackbar`: Notificación breve en la parte inferior de la pantalla, generalmente con una acción rápida (ej. "Deshacer").
   - `Alert`: Bloque estático en la página para advertencias, errores críticos o avisos informativos.
   - `Banner`: Franja de ancho completo en la parte superior del layout para anuncios del sistema o alertas globales.
   - `Progress Bar`: Barra de avance continua o por porcentaje para operaciones asíncronas prolongadas.
   - `Spinner`: Indicador de carga rotatorio para acciones breves e inmediatas.
   - `Skeleton Loader`: Siluetas de pulso gris que imitan la forma del contenido antes de su carga, evitando el salto visual (*layout shift*).
   - `Empty State`: Vista dedicada para cuando una lista o sección no tiene datos (ilustración/ícono, explicación y botón de acción principal).
   - `Success / Error State`: Pantalla o bloque dedicado que comunica inequívocamente el resultado final de una operación.

7. **Datos y Tablas:**
   - `Tables`: Tablas HTML semánticas básicas para comparar pocos datos.
   - `Data Tables`: Tablas avanzadas con ordenamiento por columnas, paginación, filtros multicriterio, selección de filas y exportación.
   - `Pagination`: Controles numéricos o de página anterior/siguiente para navegación de grandes volúmenes de datos.
   - `Filters`: Paneles o botones de filtrado facetado por etiquetas, fechas o rangos.
   - `Sorting`: Controles explícitos de ordenamiento (alfabético, precio, fecha, relevancia).
   - `Search Bar`: Barra de búsqueda con limpieza rápida y sugerencias instantáneas.
   - `Chips / Tags`: Etiquetas compactas interactivas para clasificar, filtrar o remover atributos.
   - `Badges`: Indicadores numéricos o de estado (ej. "Pendiente", "Completado", "3 nuevos").
   - `Counters`: Marcadores numéricos visuales vinculados a datos reales.

8. **Elementos Visuales y Multimedia:**
   - `Avatar`: Imagen de perfil circular con iniciales de respaldo (*fallback*) y badge de estado en línea.
   - `Gallery`: Cuadrícula o mosaico organizado para exhibir colecciones de imágenes de alta calidad.
   - `Lightbox`: Visualizador a pantalla completa con fondo oscurecido para examinar fotos en alta resolución.
   - `Image Viewer`: Componente con zoom interactivo, paneo y rotación para catálogos o radiografías clínicas.
   - `Video Player`: Reproductor de video personalizado con controles accesibles, velocidad y marcas de tiempo.
   - `Charts`: Gráficos analíticos (líneas, barras, áreas, pastel) para series temporales y distribución.
   - `Graphs`: Redes de nodos y grafos para relaciones complejas.
   - `Gauges`: Indicadores radiales tipo velocímetro para medir rendimiento, cumplimiento o cuotas.
   - `Maps`: Mapas interactivos vectoriales o de geolocalización con marcadores personalizados.

9. **E-commerce:**
   - `Product Card`: Tarjeta de producto con foto, título, precio, badge de descuento y botón de compra/carrito.
   - `Cart Drawer`: Panel deslizante lateral para ver y gestionar el carrito sin salir de la página actual.
   - `Mini-Cart`: Desplegable compacto en el navbar para previsualizar los últimos artículos añadidos.
   - `Quantity Selector`: Control de incremento/decremento numérico con botones `+` y `-`.
   - `Price Block`: Bloque visual de precio con moneda, precio tachado anterior, impuestos y descuentos aplicados.
   - `Wishlist`: Botón interactivo de guardado en lista de deseos con feedback animado.
   - `Checkout Stepper`: Barra de progreso de compra por pasos (Dirección → Envío → Pago → Confirmación).
   - `Coupon Input`: Campo con validación inmediata para aplicar códigos de descuento.
   - `Rating / Reviews`: Estrellas interactivas con desglose numérico y lista de comentarios de clientes reales.

10. **LMS / Plataformas de Cursos:**
    - `Course Card`: Tarjeta de curso con portada, nivel, duración, instructor y badge de certificación.
    - `Lesson List`: Lista estructurada de lecciones con indicadores de completado, candado (bloqueado) y duración.
    - `Curriculum Accordion`: Acordeón colapsable por módulos o semanas formativas.
    - `Progress Tracker`: Barra circular o lineal que mide el porcentaje de avance del alumno en el temario.
    - `Video Lesson Player`: Reproductor de clases con velocidad variable, transcripción lateral y notas.
    - `Quiz`: Componente interactivo de evaluación con selección múltiple, tiempo límite y retroalimentación inmediata.
    - `Certificate Card`: Bloque visual conmemorativo con código de verificación QR y botón de descarga en PDF.
    - `Module Navigation`: Botones persistentes de "Lección anterior" y "Marcar y continuar".

11. **Dashboard y Analítica:**
    - `Stat Cards`: Tarjetas métricas individuales con cifra clave, delta porcentual comparativo y micro-gráfico (*sparkline*).
    - `KPI Widgets`: Bloques modulares con indicadores clave de rendimiento del negocio.
    - `Activity Feed`: Flujo cronológico de eventos o logs recientes del sistema.
    - `Quick Actions`: Fila o bloque de botones rápidos para las tareas más frecuentes del operador.
    - `Recent Items`: Lista compacta de los últimos documentos, registros o clientes consultados.
    - `Notifications Panel`: Panel lateral o desplegable con notificaciones no leídas y acciones de archivo.

12. **Headers Especiales:**
    - `Hero Section`: Sección de impacto principal sin clichés de IA (sin pill badges ni estadísticas ficticias obligatorias).
    - `Sticky Header`: Encabezado que permanece visible en la parte superior durante el scroll, optimizando accesos rápidos.
    - `Announcement Bar`: Franja delgada superior para mensajes clave, avisos de mantenimiento o promociones activas.
    - `Promo Banner`: Bloque visual destacado para campañas temporales con CTA dedicado.
    - `Search Header`: Encabezado centrado en la búsqueda para portales de documentación o bases de conocimiento.

13. **Footers:**
    - `Simple Footer`: Pie de página minimalista de una sola fila con copyright, enlaces legales y cambio de idioma.
    - `Mega Footer`: Pie de página de 4 a 6 columnas con sitemap completo, newsletter, redes y certificaciones.
    - `Social Links`: Fila de íconos vectoriales a redes sociales con estados hover calibrados.
    - `Newsletter Block`: Formulario compacto de captura de email con aviso de privacidad y botón de suscripción.

14. **Interacciones Modernas:**
    - `Swipe Actions`: Gestos táctiles de deslizamiento lateral en móvil para acciones rápidas (ej. borrar o archivar un ítem).
    - `Drag-and-Drop`: Arrastre visual para reordenar tareas (Kanban), subir archivos o personalizar paneles.
    - `Resizable Panels`: Paneles con divisor arrastrable para ajustar el ancho entre áreas de trabajo (ej. editor de código / preview).
    - `Collapsible Panels`: Paneles laterales que se contraen a una tira delgada de íconos para maximizar el área de datos.
    - `Infinite Scroll`: Carga progresiva de registros al alcanzar el final del scroll (solo aplicable a feeds informales).
    - `Pull-to-Refresh`: Gesto móvil de tirar hacia abajo para refrescar datos en tiempo real.
    - `Hover Cards`: Tarjeta flotante que se despliega al posar el cursor sobre un link para previsualizar información sin navegar.

15. **Estados de Interfaz:**
    - `Loading State`: Estado visual de espera activo mediante skeleton o spinner.
    - `Disabled State`: Estado desactivado con reducción de opacidad y `pointer-events: none` o atributo `disabled`.
    - `Locked Content`: Bloque con desenfoque o candado indicando que requiere suscripción o permisos superiores.
    - `Onboarding`: Secuencia de bienvenida guiada para nuevos usuarios.
    - `Walkthrough / Coach Marks`: Puntos de atención flotantes interactivos que destacan funciones clave de la pantalla.
    - `Confirmation Screen`: Pantalla de cierre que confirma una transacción o compra con resumen de operación.
    - `Error Page 404 / 500`: Páginas de error amigables con código de estado real, explicación clara y botón de retorno al inicio.

---

### 6.2 Distinciones Clave: Componentes que Suelen Confundirse

Es un error técnico grave tratar estos componentes como intercambiables:

| Componente | Definición y Comportamiento | Rol Semántico / Uso Correcto |
|---|---|---|
| **Sidebar** | Navegación lateral persistente y fija en el layout de la página (no flota ni desaparece al hacer clic afuera). | Menú principal de aplicaciones con alta jerarquía (dashboards, admin, herramientas). |
| **Aside** | Elemento semántico HTML (`<aside>`) para contenido tangencial o secundario al flujo principal. | Artículos relacionados, glosario, biografías de autor o widgets complementarios. |
| **Drawer** | Panel lateral deslizante que emerge y se oculta fuera del lienzo (*off-canvas*) al activarse. | Menú de navegación en mobile, carrito de compras lateral o panel de filtros rápidos. |
| **Sheet** | Panel deslizante similar al drawer, pero con flexibilidad direccional (puede emerger desde abajo como *bottom sheet*, arriba o los lados). | Formularios rápidos de edición o menús contextuales en dispositivos móviles. |
| **Modal** | Ventana emergente centrada con capa oscurecedora (*backdrop*) que toma el foco y bloquea el resto de la interfaz. | Decisiones críticas, confirmaciones destructivas, pasarelas de pago o creación de recursos principales. |
| **Popover** | Ventana flotante pequeña y no intrusiva, contextualmente anclada al botón o elemento que la disparó. | Selector de fecha en un botón, paleta de colores o detalles contextuales rápidos sin bloquear el fondo. |

---

### 6.3 Sistema Mínimo de Componentes (Design System Core)

**[REQUIRED]** Todo proyecto profesional o plataforma debe contar con un catálogo o librería base que implemente de forma nativa como mínimo los siguientes componentes esenciales antes de considerarse maduro:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               SISTEMA MÍNIMO DE COMPONENTES CORE                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1.  Navbar         (Navegación principal superior)                                                    │
│ 2.  Sidebar        (Navegación lateral fija de aplicación)                                            │
│ 3.  Drawer         (Panel deslizante lateral / carrito / filtros)                                     │
│ 4.  Modal          (Ventana emergente para flujos críticos)                                           │
│ 5.  Cards          (Contenedores de catálogo / ítems comparables)                                     │
│ 6.  Tabs           (Alternancia de paneles sin recarga)                                               │
│ 7.  Accordion      (Contenido colapsable y FAQs)                                                      │
│ 8.  Forms          (Colección completa de inputs, selects, toggles, textareas)                        │
│ 9.  Table          (Tablas semánticas y Data Tables con paginación)                                   │
│ 10. Toast          (Notificaciones no intrusivas con feedback de mutaciones)                          │
│ 11. Dropdown       (Menús flotantes de opciones y acciones)                                           │
│ 12. Tooltip        (Ayuda contextual accesible)                                                       │
│ 13. Skeleton       (Carga progresiva sin saltos de layout)                                            │
│ 14. Empty State    (Pantallas y bloques vacíos con guía y CTA de acción)                              │
│ 15. Pagination     (Control de páginas para grandes conjuntos de datos)                               │
│ 16. Search         (Barra de búsqueda con feedback dinámico)                                          │
│ 17. Filters        (Filtros por facetas y ordenamiento)                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

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
- [ ] ¿Evité la "fatiga de cards" recurriendo a la taxonomía completa de componentes (tabs, accordions, drawers, sheets, tables, steppers, etc.)?
- [ ] ¿Distinguí con rigor técnico entre Sidebar (fijo), Aside (semántico), Drawer (off-canvas lateral), Sheet (deslizante multidireccional), Modal (crítico bloqueante) y Popover (anclado no intrusivo)?
- [ ] ¿La plataforma o proyecto implementa el Sistema Mínimo de Componentes Core (Navbar + Sidebar + Drawer + Modal + Cards + Tabs + Accordion + Forms + Table + Toast + Dropdown + Tooltip + Skeleton + Empty State + Pagination + Search + Filters)?
