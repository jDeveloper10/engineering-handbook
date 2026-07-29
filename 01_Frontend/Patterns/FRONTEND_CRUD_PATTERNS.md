# FRONTEND CRUD PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y de [FRONTEND_UI_PATTERNS.md](FRONTEND_UI_PATTERNS.md) sección 3.3. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Ant Design y Atlassian Design System (fuertes en patrones CRUD de back-office).

---

## 1. Regla principal

**[REQUIRED]** Todo módulo CRUD sigue esta secuencia de pantallas/estados: **Listado → Crear/Editar → Confirmar eliminación**, cada una con su propio patrón — nunca un grid de cards por registro (ver `FRONTEND_UI_PATTERNS.md` sección 2).

```
Listado:  Header (título + "Crear nuevo") → Buscar/Filtros → Tabla → Paginación
Crear/Editar:  Modal (formulario corto) o página/drawer dedicado (formulario largo)
Eliminar:  Siempre con confirmación explícita
```

---

## 2. Vista de listado

**[REQUIRED]** Anatomía: título de la sección + CTA "Crear nuevo" visible arriba, buscador y filtros antes de la tabla, tabla de datos real (ver [FRONTEND_TABLE_PATTERNS.md](FRONTEND_TABLE_PATTERNS.md)), paginación al final.

---

## 3. Crear / Editar — modal vs página dedicada

**[REQUIRED]** Árbol de decisión:

```
¿El formulario tiene menos de ~5 campos y no necesita contexto adicional?
  Sí → Modal
  No → ¿El usuario se beneficia de ver la lista de fondo mientras completa?
         Sí → Drawer lateral
         No → Página dedicada con su propia URL
```

**Por qué:** un formulario largo dentro de un modal obliga a hacer scroll dentro de un contenedor pequeño y pierde la ventaja de tener una URL propia (no se puede compartir el link ni volver con el botón atrás del navegador).

---

## 4. Ver detalle

**[RECOMMENDED]** Master-Detail (tabla a la izquierda, panel de detalle a la derecha) cuando el usuario compara varios registros seguido; navegación a una página de detalle dedicada cuando el detalle es denso o el usuario típicamente entra a uno solo y trabaja ahí un rato.

---

## 5. Eliminar

**[REQUIRED]** Ninguna eliminación ocurre con un solo clic sin confirmación. El modal de confirmación nombra explícitamente el ítem a eliminar ("¿Eliminar el producto *Zapatilla Aero Flex*?") y, si la acción es irreversible, lo dice ("Esta acción no se puede deshacer").

**Por qué:** "¿Estás seguro?" genérico no da al usuario información para verificar que está borrando lo correcto — nombrar el ítem es lo que previene el error real.

---

## 6. Acciones en bulk

**[RECOMMENDED]** Para listados con muchos registros: selección múltiple (checkbox por fila + "seleccionar todos") habilita una barra de acciones masivas (eliminar, exportar, cambiar estado). Ver `FRONTEND_TABLE_PATTERNS.md` sección 5.

---

## 7. Feedback tras una acción

**[REQUIRED]** Crear, editar y eliminar confirman el resultado explícitamente — un toast de éxito (ver [FRONTEND_NOTIFICATIONS_PATTERNS.md](FRONTEND_NOTIFICATIONS_PATTERNS.md)) o una actualización visible inmediata en la tabla. El usuario nunca se queda sin saber si la acción funcionó.

**[RECOMMENDED]** Optimistic UI (actualizar la interfaz antes de confirmar respuesta del servidor) para acciones de bajo riesgo y reversibles; esperar confirmación real del servidor antes de reflejar el cambio en acciones irreversibles como eliminar.

---

## 8. Anti-patrones

- ❌ Eliminar sin modal de confirmación.
- ❌ Modal de confirmación genérico sin nombrar el ítem.
- ❌ Formulario de 15+ campos forzado dentro de un modal pequeño.
- ❌ Guardar sin dar ningún feedback visible de que funcionó.
- ❌ Listado de registros como grid de cards en vez de tabla.

---

## Checklist rápido

- [ ] ¿Listado con buscador, filtros, tabla y paginación, no cards?
- [ ] ¿Crear/Editar usa modal, drawer o página según la complejidad del formulario (árbol de la sección 3)?
- [ ] ¿Eliminar siempre pide confirmación nombrando el ítem?
- [ ] ¿Bulk actions disponibles si el listado es grande?
- [ ] ¿Toda acción (crear/editar/eliminar) da feedback explícito de éxito o error?
