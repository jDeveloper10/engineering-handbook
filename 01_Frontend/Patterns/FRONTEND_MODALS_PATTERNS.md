---
title: "Patrones de Modales y Drawers"
category: 01_Frontend
doc_type: patron
tags: [frontend, modal, drawer, slide-over, accesibilidad, ux]
summary: "Árbol de decisión entre modal, drawer lateral, in-line editing y página completa, matriz según cantidad de campos, anatomía UX de edición y accesibilidad."
keywords: [modal, drawer, slide-over, dialog, in-line editing, confirmacion, focus-trap, accesibilidad]
updated: 2026-09-02
status: current
---

# FRONTEND MODALS & DRAWERS PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 13 Accessibility). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Apple HIG (sheets/popovers), Nielsen Norman Group (cuándo NO usar modales), LogRocket Blog y Untitled UI Design System.

---

## 1. Matriz de Decisión: ¿Qué componente usar para Crear o Editar?

**[REQUIRED]** La elección del componente de UI para capturar o editar datos no es una decisión estética — se rige por la **densidad de campos y el contexto que el usuario necesita conservar**:

| Si el formulario tiene... | La mejor opción de UI es... | Por qué y Cuándo usarlo |
|---|---|---|
| **Solo 1 o 2 campos específicos** | **Edición en Línea (In-line Editing)** | Directo en la fila o bloque de texto sin abrir ninguna ventana (ej. cambiar estado, rol o precio rápido). Cero clics extra, ultra veloz. Requiere botón de confirmar (✓) y cancelar (✗). |
| **1 a 8 campos (Rápido)** | **Modal (Diálogo Centrado)** | Acción corta, enfocada y reversible (ej. confirmación, cambio de contraseña puntual, asignar etiqueta). Bloquea intencionalmente para enfocar la atención sin perder la vista previa. |
| **8 a 15 campos (Medio)** | **Drawer / Panel Lateral (Slide-over)** | Emerge desde el borde derecho (30% a 50% de la pantalla). Mucho mayor espacio vertical para scroll natural, mantiene visible la tabla o listado de fondo, fluido e integrado (estilo Notion, HubSpot, Jira, Linear). Ideal para entidades completas como productos, insumos, clientes o citas. |
| **Más de 15 campos (Largo / Complejo)** | **Página Completa Dedicada (Full-Page Form)** | Formularios masivos divididos en secciones o tabs internas (ej. onboarding corporativo, configuración de cuenta, checkout multidivisa). Espacio ilimitado, URL propia compartible y botón de regreso visible. |

---

## 2. Tipos de Modales de Producto y Casos Reales

1. **Modal de "Vista Rápida" (Quick View):**
   - Permite ver especificaciones, fotos secundarias y tallas sin salir del catálogo principal ni recargar la página.
   - *Elementos clave:* Carrusel visual, selector de atributos y botón directo de acción.

2. **Modal de Selección de Plan o Configuración:**
   - Detiene el flujo para que el usuario tome una decisión obligatoria previa al checkout o activación.
   - *Elementos clave:* Comparativa de opciones, CTA principal visible y botón de cierre claro si no se desea avanzar.

3. **Panel Lateral / Drawer de Carrito y Confirmación:**
   - Emerge tras agregar un ítem o iniciar el cobro, permitiendo al usuario revisar el resumen de la orden y ver el total en vivo sin abandonar la pantalla de selección.
   - *Elementos clave:* Lista con steppers de cantidad (+/-), desglose de costos/impuestos y CTA destacado de "Cobrar" o "Continuar".

4. **Modal de Onboarding y Novedades:**
   - Recorrido interactivo guiado al ingresar por primera vez a un módulo.
   - *Elementos clave:* Pasos numerados (1 de 3), ilustración y botón de "Siguiente" o "Saltar".

---

## 3. Anatomía UX Obligatoria de un Formulario de Edición

**[REQUIRED]** Cuando se abre un Modal o Drawer para editar un registro existente:

1. **Datos precargados obligatorios:**
   - Todos los campos deben inicializarse con los valores actuales del registro. El usuario nunca debe encontrar campos vacíos en modo edición.
2. **Campos bloqueados (Read-only / Deshabilitados):**
   - Datos de auditoría o identificadores inmutables (ID único, fecha de creación) se muestran en texto plano o con campo deshabilitado visualmente claro.
3. **Estructura limpia (Sin micro-títulos):**
   - Título directo: "Editar Insumo: [Nombre]" o "Modificar Cita".
   - Prohibido agregar micro-títulos pill decorativos encima del encabezado (`UI-NO-MICROTITLES`).
4. **Botones de acción en el pie:**
   - **Botón Principal (Derecha):** Semántica de acción ("Guardar cambios", "Actualizar", "Confirmar"). Nunca "Aceptar" genérico.
   - **Botón Secundario (Izquierda / Junto al principal):** "Cancelar" (cierra la ventana descartando cambios sin tocar la base de datos).

---

## 4. Cuándo NO usar un modal centrado

**[REQUIRED]**
- Formularios de más de 8 campos: pasar inmediatamente a **Drawer lateral (Slide-over)** o **Página completa**.
- Formularios con scroll interno vertical incómodo en pantallas de laptop o tablets.
- Pantallas donde el usuario necesita consultar datos de la fila de fondo mientras edita.

---

## 5. Accesibilidad y Comportamiento Técnico

**[REQUIRED]**
- **Overlay:** Fondo opaco (`backdrop-blur`) que atenúa el fondo.
- **Focus Trap:** El foco del teclado (`Tab`) queda atrapado dentro del modal/drawer mientras permanezca abierto.
- **Cierre accesible:** Cierre mediante botón "X" superior derecho, tecla `Esc` y clic en el backdrop (a menos que haya cambios sin guardar o proceso en curso).
- **Semántica ARIA:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` vinculado al título.
- **Restauración de foco:** Al cerrarse, el foco regresa al botón que detonó la apertura.

---

## 6. Anti-patrones

- ❌ Forzar formularios de 10+ campos dentro de un modal centrado con scroll diminuto.
- ❌ Modal dentro de modal (anidación prohibida).
- ❌ Botones genéricos "Aceptar" / "OK" en vez de acciones explícitas ("Guardar cambios").
- ❌ Modal que no se puede cerrar con la tecla `Esc`.
- ❌ Abrir un formulario de edición con campos vacíos.

---

## Checklist rápido

- [ ] ¿Componente elegido según la matriz (In-line <=2, Modal <=8, Drawer 8-15, Página >15)?
- [ ] ¿Datos actuales precargados al editar?
- [ ] ¿Botones con texto de acción claro ("Guardar cambios" / "Cancelar")?
- [ ] ¿Overlay con focus trap y tecla `Esc` funcionando?
- [ ] ¿Sin micro-títulos decorativos sobre el encabezado?
