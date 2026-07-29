# FRONTEND MODALS & DRAWERS PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 13 Accessibility). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Apple HIG (sheets/popovers) y Nielsen Norman Group (cuándo NO usar modales — es una de sus reglas más citadas).

---

## 1. Regla principal — árbol de decisión

**[REQUIRED]**

```
¿Cuánto contenido/contexto necesita el usuario conservar?
│
├─ Acción corta y enfocada, bloquear intencionalmente tiene sentido
│    → Modal
│
├─ Contenido más largo, o el usuario se beneficia de ver el fondo
│    (filtros, carrito, detalle rápido de un ítem de una lista)
│    → Drawer lateral
│
└─ Contenido complejo/formulario largo que merece URL propia,
   compartible, con botón atrás del navegador funcionando
    → Página dedicada
```

---

## 2. Cuándo NO usar un modal

**[REQUIRED]** no usar modal para:
- Formularios largos (5+ campos o multi-sección) — usar página dedicada o un Wizard.
- Contenido que el usuario querría compartir por URL o volver a encontrar después.
- Confirmaciones triviales de bajo riesgo — un modal para "¿Guardar cambios?" en una acción reversible es fricción innecesaria; un toast o guardado automático resuelve mejor.

**Por qué:** un modal interrumpe el flujo del usuario a propósito — se justifica solo cuando esa interrupción aporta algo (evitar un error costoso, enfocar una decisión puntual). Usarlo por defecto para todo entrena al usuario a cerrar modales sin leerlos.

---

## 3. Anatomía

**[REQUIRED]** Overlay que atenúa el fondo, contenido del modal centrado, botón de cerrar explícito (visible, no solo implícito). **[REQUIRED]** foco atrapado dentro del modal mientras está abierto (focus trap) — Tab no debe poder salir del modal hacia el contenido de fondo.

**[REQUIRED]** Se cierra con: botón de cerrar, tecla `Esc`, y clic fuera del modal — **excepto** cuando hay una acción destructiva en progreso o cambios sin guardar, donde clic-fuera no debe cerrar accidentalmente (o pide confirmación antes).

---

## 4. Modal de confirmación destructiva

**[REQUIRED]** Ver `FRONTEND_CRUD_PATTERNS.md` sección 5 — nombra explícitamente el ítem afectado y la consecuencia ("Esta acción no se puede deshacer"), nunca un "¿Estás seguro?" genérico.

---

## 5. Drawer

**[RECOMMENDED]** Se abre desde el lado derecho por defecto (convención estándar para contenido complementario en interfaces LTR). Ancho fijo en desktop, pantalla completa en mobile.

---

## 6. Accesibilidad

**[REQUIRED]** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` apuntando al título del modal. **[REQUIRED]** el foco vuelve al elemento que abrió el modal cuando se cierra (mismo principio que `FRONTEND_NAVIGATION_PATTERNS.md` sobre menús).

---

## 7. Anti-patrones

- ❌ Modal dentro de modal — nunca. Si una acción dentro de un modal necesita otro flujo, se reemplaza el contenido del mismo modal o se cierra y navega.
- ❌ Modal que no se puede cerrar con `Esc`.
- ❌ Drawer usado para una confirmación trivial de sí/no.
- ❌ Clic fuera cerrando un modal con una acción destructiva en progreso sin avisar.
- ❌ Foco que no vuelve al elemento original al cerrar, dejando al usuario de teclado "perdido" en la página.

---

## Checklist rápido

- [ ] ¿Modal, Drawer o página elegidos según el árbol de la sección 1, no por defecto?
- [ ] ¿Se evitó el modal para formularios largos o contenido que merece URL propia?
- [ ] ¿Focus trap activo, `Esc` y clic fuera cierran (salvo acción destructiva en curso)?
- [ ] ¿Confirmación destructiva nombra el ítem y la consecuencia?
- [ ] ¿`role="dialog"` + `aria-modal` + `aria-labelledby`, foco vuelve al abrir/cerrar?
- [ ] ¿Ningún modal anidado dentro de otro modal?
