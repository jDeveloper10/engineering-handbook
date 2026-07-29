# FRONTEND TABLE PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y de [FRONTEND_UI_PATTERNS.md](FRONTEND_UI_PATTERNS.md) sección 2 (Datos tabulares). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Ant Design, IBM Carbon y Material Design (los tres documentan tablas densas extensamente).

---

## 1. Regla principal

**[REQUIRED]** Datos tabulares se muestran en una tabla real (columnas alineadas, ordenable), nunca convertidos en cards apiladas por decisión de diseño — la única excepción válida es un colapso responsive deliberado en mobile (sección 7).

---

## 2. Anatomía

**[REQUIRED]** Header de columnas (con indicador de ordenamiento activo), filas de datos, acciones por fila, paginación.

**[RECOMMENDED]** Acciones por fila: si son 1-2 acciones, botones inline visibles; si son 3+, un menú de "..." (kebab/dots) para no saturar la fila.

---

## 3. Paginación vs scroll infinito

**[REQUIRED]** Paginación numerada (con salto a página específica) para vistas de administración/back-office, donde el usuario necesita ubicar un registro concreto. **[RECOMMENDED]** scroll infinito solo para feeds de consumo donde no importa "llegar a una página exacta" (ej. un feed de actividad).

**Por qué:** en un panel admin, "ir directo a la página 12" es una necesidad real; el scroll infinito la hace imposible.

---

## 4. Columnas

**[REQUIRED]** Mostrar por defecto solo las columnas relevantes para la tarea principal, no todas las que existen en el modelo de datos. **[RECOMMENDED]** si hay 8+ columnas posibles, ofrecer un selector de columnas visibles (column picker) en vez de mostrarlas todas siempre.

---

## 5. Ordenamiento y selección

**[REQUIRED]** Click en el header de una columna ordenable, con indicador visual claro de cuál está activa y en qué dirección (asc/desc). **[RECOMMENDED]** selección múltiple vía checkbox por fila + "seleccionar todos" cuando el listado soporta bulk actions (ver `FRONTEND_CRUD_PATTERNS.md` sección 6).

---

## 6. Estados de fila

**[REQUIRED]** `hover`, `selected` y `disabled` visualmente distinguibles — misma regla de estados obligatorios de `FRONTEND_ENGINEERING_STANDARD.md` sección 1.6, aplicada a filas.

---

## 7. Responsive

**[REQUIRED]** El colapso a mobile es una decisión explícita, no "scroll horizontal silencioso" como única solución:

- Si la tabla tiene pocas columnas realmente críticas, se priorizan esas 2-3 en mobile y el resto se accede expandiendo la fila.
- Si el contenido es poco denso por fila, colapsar a un patrón de lista/card por fila es válido — pero es una decisión de este documento, no la regla general anti-cards de `FRONTEND_UI_PATTERNS.md`, que sigue aplicando en desktop.

---

## 8. Estados de la tabla completa

**[REQUIRED]** Loading (skeleton rows, no un spinner que reemplaza toda la tabla), vacío (mensaje + CTA si aplica) y error, siguiendo [FRONTEND_STATES_PATTERNS.md](FRONTEND_STATES_PATTERNS.md).

---

## 9. Anti-patrones

- ❌ Miles de filas sin paginación ni virtualización.
- ❌ Todas las columnas posibles mostradas siempre, sin priorización.
- ❌ Ordenamiento sin indicador visual de cuál columna/dirección está activa.
- ❌ Scroll horizontal silencioso en mobile como única respuesta responsive, sin haber evaluado priorizar columnas.
- ❌ Reemplazar el spinner de carga por una tabla completamente en blanco sin skeleton.

---

## Checklist rápido

- [ ] ¿Es una tabla real, no cards, salvo colapso responsive deliberado?
- [ ] ¿Paginación numerada en back-office, scroll infinito solo en feeds de consumo?
- [ ] ¿Solo columnas relevantes por defecto, column picker si hay muchas posibles?
- [ ] ¿Ordenamiento con indicador visual claro?
- [ ] ¿Estados hover/selected/disabled distinguibles?
- [ ] ¿Loading con skeleton rows, vacío con CTA, error accionable?
- [ ] ¿Responsive con prioridad de columnas explícita, no solo scroll horizontal?
