# FRONTEND RESPONSIVE STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, secciones 1.4 y 1.8) y de [FRONTEND_HTML_STRUCTURE_STANDARD.md](FRONTEND_HTML_STRUCTURE_STANDARD.md). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Va junto a los otros documentos que definen el sistema visual: [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md) (identidad visual), este documento (comportamiento por tamaño de pantalla), y la sección 13 del estándar principal (accesibilidad). Ninguno de los tres es opcional ni "se hace al final" — se validan durante el diseño, no después.

---

## 1. Regla principal

**[REQUIRED]** Toda interfaz se piensa y valida en todos los tamaños de pantalla **antes** de darse por terminada — nunca se diseña solo para desktop y se "encoge" después. El proceso es mobile-first: se construye y valida primero en el breakpoint más chico, y se agrega comportamiento hacia pantallas más grandes, no al revés.

**Por qué:** diseñar desktop-first y encoger después casi siempre produce mobile roto (sidebars aplastados, texto ilegible, botones imposibles de tocar) porque las decisiones de layout ya asumieron espacio que no existe en mobile. Empezar por la restricción más dura (la pantalla más chica) obliga a resolver lo esencial primero.

---

## 2. Breakpoints estándar

**[REQUIRED]** Los mismos 4 rangos conceptuales en todo el handbook — no se inventan breakpoints custom por componente:

| Rango conceptual | Ancho | Prefijo (Tailwind) |
|---|---|---|
| Mobile | 320px – 639px | (base, sin prefijo) |
| Tablet | 640px – 1023px | `sm:` / `md:` |
| Desktop | 1024px – 1439px | `lg:` |
| Large | 1440px+ | `xl:` / `2xl:` |

Estos rangos son la forma conceptual de los valores exactos ya definidos en `FRONTEND_ENGINEERING_STANDARD.md` 1.4 (640/768/1024/1280/1536px) — no son un sistema nuevo, es la misma escala explicada por rango de uso.

---

## 3. Tamaños fluidos, no fijos

**[REQUIRED]** El contenido (contenedores, cards, secciones) usa ancho/alto relativos (`%`, `max-width`, `min-height`) — no un ancho y alto fijos en píxeles, salvo elementos que son intrínsecamente de tamaño fijo (íconos, avatares, badges).

```
❌ width: 500px; height: 300px;
✅ width: 100%; max-width: 500px; min-height: auto;
```

**Por qué:** un tamaño fijo no responde a nada — en una pantalla más angosta que el valor fijo, el contenido se desborda o fuerza scroll horizontal no intencional.

---

## 4. Comportamiento responsive por componente

**[REQUIRED]** Todo componente reusable define explícitamente cómo se comporta en cada breakpoint — no se asume que "Tailwind ya lo resuelve" sin decidirlo. El comportamiento específico de cada tipo de componente ya está definido en su documento correspondiente — este documento no lo repite, apunta a la fuente:

| Componente | Comportamiento responsive definido en |
|---|---|
| Grid de cards | `FRONTEND_UI_PATTERNS.md` (columnas según breakpoint) |
| Navbar | `FRONTEND_NAVIGATION_PATTERNS.md` 3.5 (nunca copia desktop, prioridad explícita) |
| Sidebar | `FRONTEND_SIDEBAR_PATTERNS.md` sección 5 (fijo → colapsable → Drawer) |
| Tablas | `FRONTEND_TABLE_PATTERNS.md` sección 7 (prioridad de columnas, nunca solo scroll horizontal silencioso) |
| Formularios | Sección 9 de este documento |
| Landing (bloques) | `FRONTEND_LANDING_PATTERNS.md` sección 7 |
| Modales/Drawers | `FRONTEND_MODALS_PATTERNS.md` sección 5 (Drawer a pantalla completa en mobile) |

---

## 5. Touch-friendly

**[REQUIRED]** Área táctil mínima de ~44×44px por elemento interactivo (referencia: Apple HIG y Material Design coinciden en este mínimo), con separación suficiente entre controles adyacentes para no generar toques accidentales.

**Por qué (Fitts's Law):** el tiempo/precisión para acertar un objetivo depende de su tamaño y distancia — un botón chico y pegado a otro no solo se ve mal en mobile, es objetivamente más lento y propenso a error de tocar.

**[REQUIRED]** Ningún control depende **únicamente** de `:hover` para ser usable — en touch no existe hover. Una acción que en desktop aparece solo al pasar el mouse necesita un equivalente siempre visible o accesible por tap en mobile.

```
❌ "Ver detalles" que solo aparece con :hover
✅ "Ver detalles →" siempre visible, o revelado por tap explícito
```

---

## 6. Imágenes responsive

**[REQUIRED]** Se combinan dos cosas, no una sola: `width`/`height` como atributos HTML (definen la proporción intrínseca y previenen layout shift — ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` 1.7) **más** una regla CSS que las deja escalar (`max-width: 100%; height: auto`, o el equivalente `w-full h-auto` de Tailwind). No son reglas contradictorias: los atributos HTML fijan la relación de aspecto, el CSS controla el tamaño real renderizado.

```html
<img src="foto.jpg" alt="..." width="800" height="600" class="w-full h-auto" />
```

---

## 7. Tipografía responsive

**[REQUIRED]** El texto de interfaz (body, labels, UI en general) usa la escala tipográfica fija de `FRONTEND_ENGINEERING_STANDARD.md` 1.3, que ya es responsive por definición al cambiar de clase por breakpoint (ej. `text-4xl sm:text-5xl lg:text-6xl`, como ya se usa en `FRONTEND_LANDING_PATTERNS.md` sección 6).

**[RECOMMENDED]** Para headlines de display muy grandes (hero, marketing) que están fuera de la escala base, `clamp()` (o equivalente) es una alternativa válida a los escalones por breakpoint — pero no reemplaza la escala fija del design system para el resto del texto de la interfaz, solo aplica a esos casos de display grande donde una transición fluida se ve mejor que saltos discretos.

```css
/* Válido para un headline de display, no para texto de UI general */
font-size: clamp(2rem, 5vw, 5rem);
```

---

## 8. Tablas

Ver `FRONTEND_TABLE_PATTERNS.md` sección 7 — decisión explícita entre priorizar columnas, colapsar a lista, o scroll horizontal, nunca "se ve como se vea" sin decidirlo.

---

## 9. Formularios

**[REQUIRED]** Formularios con layout de múltiples columnas en desktop colapsan a una sola columna en mobile — nunca se fuerzan 2 columnas en una pantalla de 375px.

```
Desktop:  Nombre        Apellido
          Email         Teléfono
          [ Guardar ]

Mobile:   Nombre
          Apellido
          Email
          Teléfono
          [ Guardar ]
```

---

## 10. Validación obligatoria antes de dar una UI por terminada

**[REQUIRED]** Antes de marcar cualquier pantalla como lista, se valida contra estas preguntas — no es opcional, es parte de la definición de "terminado" (ver también `FRONTEND_ENGINEERING_STANDARD.md` 1.8):

- ¿Cómo se ve en el breakpoint mobile más angosto (320px)?
- ¿Cómo se ve en tablet (768px) y en desktop (1024px+)?
- ¿Qué pasa si el texto real es más largo que el texto de prueba usado al diseñar (nombres largos, traducciones)?
- ¿Qué pasa si una lista/tabla tiene muchos más elementos de los usados en el mockup (cientos, no 3-5)?
- ¿Todo elemento interactivo sigue siendo usable por touch, no solo por mouse?

---

## 11. Anti-patrones

- ❌ Diseñar y validar solo en desktop, "arreglar mobile después".
- ❌ Ancho/alto fijos en contenido que debería fluir.
- ❌ Sidebar de desktop simplemente aplastado en mobile en vez de convertirse en Drawer.
- ❌ Una acción que solo existe en `:hover`, sin equivalente táctil.
- ❌ `<img>` sin `width`/`height` (layout shift) o sin CSS que permita escalar.
- ❌ Formulario de 2+ columnas forzado en una pantalla de 375px.
- ❌ Tabla ancha con scroll horizontal silencioso como única respuesta, sin haber evaluado prioridad de columnas.

---

## Checklist rápido

- [ ] ¿Se diseñó y validó mobile-first, no desktop-first "encogido" después?
- [ ] ¿Breakpoints de la escala estándar (320/640/1024/1440), sin valores custom por componente?
- [ ] ¿Contenido con tamaños fluidos, fijos solo en íconos/avatares/badges?
- [ ] ¿Cada componente tiene su comportamiento responsive definido explícitamente (tabla de la sección 4)?
- [ ] ¿Áreas táctiles ≥44×44px, sin depender solo de hover?
- [ ] ¿Imágenes con `width`/`height` + CSS que permite escalar?
- [ ] ¿Formularios colapsan a una columna en mobile?
- [ ] ¿Se validó con texto largo y con muchos elementos, no solo con el dato de prueba ideal?
