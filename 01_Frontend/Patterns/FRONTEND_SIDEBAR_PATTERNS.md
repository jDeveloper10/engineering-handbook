---
title: "Patrones de Sidebar"
category: 01_Frontend
tags: [frontend, sidebar, navegacion, responsive]
summary: "Patrones de barra lateral, jerarquía interna del contenido, reglas de agrupación, comportamiento responsive y anti-patrones frecuentes."
keywords: [sidebar, navegacion, colapsable, jerarquia, responsive, anti-patrones]
updated: 2026-07-27
status: current
---

# FRONTEND SIDEBAR PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y extiende [FRONTEND_NAVIGATION_PATTERNS.md](FRONTEND_NAVIGATION_PATTERNS.md) sección 4.7. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> El sidebar merece su propio documento porque en una app SaaS es el componente con el que el usuario interactúa más veces por sesión — un error de organización ahí se paga cada vez que alguien busca una opción, no una sola vez como con un error de landing. Contrastado contra Atlassian Design System e IBM Carbon (ambos documentan sidebars de apps densas en profundidad).

---

## 1. Regla principal

**[REQUIRED]** El sidebar existe para facilitar navegación persistente en aplicaciones con múltiples módulos — no se usa porque "se ve bien" o porque "así se ve una app profesional".

**Usarlo cuando:** Dashboard, CRM, ERP, panel administrativo, SaaS con varios módulos, herramientas internas.

**No usarlo en:** landing pages, blogs, portfolios, sitios de pocas páginas — ahí un sidebar permanente resta espacio y hace que un sitio de contenido se sienta (y pese) como una app. Ver `FRONTEND_NAVIGATION_PATTERNS.md` sección 1 (árbol de decisión navbar vs sidebar).

---

## 2. Patrones principales

### 2.1 Sidebar clásico

```
LOGO
🏠 Dashboard
👥 Usuarios
📦 Productos
📈 Reportes
⚙ Configuración
```

**[RECOMMENDED]** para apps con menos de ~7 módulos sin jerarquía interna — el más común, el usuario no tiene que aprenderlo. **Caso real:** GitHub (navegación de repositorio).

### 2.2 Sidebar colapsable

```
Expandido                    Colapsado
🏠 Dashboard                  🏠
👥 Usuarios                   👥
                              📦
```

**[RECOMMENDED]** cuando el espacio horizontal es crítico (herramientas con canvas/editor central que necesitan maximizar el área de trabajo).

### 2.3 Sidebar agrupado

```
GENERAL
Dashboard
Analytics
──────────
GESTIÓN
Usuarios
Productos
Pedidos
──────────
CONFIGURACIÓN
Cuenta
Facturación
```

**[REQUIRED]** a partir de ~7-8 módulos — sin agrupar, una lista larga se vuelve una búsqueda lineal ítem por ítem. **Caso real:** Supabase, Notion.

### 2.4 Sidebar con submenús

```
Usuarios ▾
  Usuarios
  Roles
  Permisos
──────────
Productos ▾
  Categorías
  Inventario
```

**[RECOMMENDED]** solo cuando un módulo tiene sub-secciones reales — no se agrega un nivel de anidación "por si acaso". **[REQUIRED]** máximo 2 niveles de profundidad (ver sección 6, anti-patrón de 3+ niveles).

### 2.5 Sidebar híbrido (iconos + expansión al hover)

```
Colapsado (solo iconos) → al pasar el mouse → se expande mostrando texto
```

**[RECOMMENDED]** para herramientas modernas densas donde se prioriza espacio pero no se quiere perder reconocibilidad. **Caso real:** Linear, Notion (modo compacto).

---

## 3. Jerarquía interna del contenido

**[REQUIRED]** Orden de arriba hacia abajo:

```
Logo
  ↓
Búsqueda (opcional)
  ↓
Navegación principal (agrupada si aplica)
  ↓
Separador
  ↓
Configuración
  ↓
Usuario / cuenta
```

**Por qué:** navegación operativa (lo que se usa a cada rato) va arriba, cerca del logo; lo administrativo (config, cuenta) va al fondo, separado — refleja frecuencia de uso real, no orden alfabético ni orden de creación de features.

---

## 4. Reglas

**[REQUIRED]**
- Un único elemento activo a la vez — nunca dos ítems marcados como activos simultáneamente (ver anti-patrón sección 6).
- Íconos consistentes (mismo grosor de trazo, mismo estilo — nunca mezclar sets de íconos distintos).
- Texto siempre visible cuando el sidebar está expandido — un sidebar expandido que muestra solo íconos no es "expandido", es un bug.
- Scroll independiente del sidebar si el menú es largo — el sidebar hace scroll propio, no arrastra el logo/usuario fuera de vista.
- Estados `hover`, `focus-visible` y `activo` visualmente distintos entre sí (ver `FRONTEND_ENGINEERING_STANDARD.md` 1.6).
- Responsive según sección 5.

**[RECOMMENDED]**
- Agrupar módulos relacionados (sección 2.3) en vez de una lista plana.
- Separadores visuales entre grupos.
- Profundidad máxima de 2 niveles (Logo → Grupo → Ítem, o Ítem → Submenú, nunca ambos anidados).
- Recordar si el usuario dejó el sidebar colapsado (persistir la preferencia, ej. `localStorage`).

---

## 5. Responsive

**[REQUIRED]**

| Breakpoint | Patrón |
|---|---|
| Desktop | Sidebar fijo (clásico, agrupado, o colapsable según sección 2) |
| Tablet | Sidebar colapsable (solo iconos por defecto, expandible) |
| Mobile | Drawer (overlay temporal, nunca fijo — ver `FRONTEND_NAVIGATION_PATTERNS.md` 5.5) |

**[REQUIRED]** Nunca un sidebar fijo ocupando media pantalla en mobile — ahí el patrón correcto es siempre Drawer, sin excepción.

---

## 6. Anti-patrones

- ❌ 20+ opciones en una lista plana sin agrupar.
- ❌ Más de 2 niveles de anidación (`Usuarios → Roles → Permisos → Especiales`).
- ❌ Dos elementos marcados como activos al mismo tiempo.
- ❌ Íconos de estilos/sets distintos para acciones similares.
- ❌ Sidebar saturado de colores decorativos que compiten con el color de "activo" (si todo es de color, nada resalta).

---

## 7. Árbol de decisión de variante

**[REQUIRED]** Una vez que `FRONTEND_NAVIGATION_PATTERNS.md` sección 1 ya determinó que el producto necesita un sidebar (no un navbar), este árbol elige la variante:

```
¿Menos de ~7 módulos, sin jerarquía interna?
  Sí → Sidebar clásico (2.1)

¿7+ módulos que se agrupan en categorías naturales?
  Sí → Sidebar agrupado (2.3)

¿Algún módulo tiene sub-secciones propias reales?
  Sí → Sidebar con submenús (2.4), máx. 2 niveles

¿El espacio horizontal es crítico (canvas/editor central)?
  Sí → Sidebar colapsable (2.2) o híbrido (2.5)

¿Es mobile?
  → Siempre Drawer, sin excepción (sección 5)
```

---

## 8. Arquitectura de información del sidebar

Esto es lo que casi nunca se documenta, y es más importante que el estilo visual: **el problema de un mal sidebar casi nunca es el diseño, es el orden.**

```
❌ Sin lógica (orden de creación de features, no de uso):
Dashboard
Configuración
Productos
Perfil
Usuarios
Reportes
Facturación

✅ Agrupado por dominio funcional:
🏠 General
  Dashboard
  Analytics
──────────
👥 Gestión
  Usuarios
  Clientes
  Productos
  Pedidos
──────────
💰 Finanzas
  Facturación
  Pagos
──────────
⚙ Sistema
  Configuración
  Perfil
```

**[REQUIRED]** Los grupos se definen por dominio funcional del negocio (a qué área pertenece la acción), no por orden alfabético ni por el orden en que se construyeron las features.

**Por qué:** agrupar por dominio reduce el tiempo que el usuario tarda en encontrar una opción — cuando busca "Facturación", su primer instinto es mirar en un grupo de dinero/finanzas, no escanear una lista plana de 12 ítems sin relación aparente entre sí. Es un problema de arquitectura de información, no de estética — una IA (o un dev apurado) genera sidebars funcionales con frecuencia, pero rara vez bien organizados, porque agregar cada ítem donde "cabe" en el momento es más rápido que pensar la taxonomía completa desde el principio.

---

## Checklist rápido

- [ ] ¿Se usa sidebar porque el producto lo justifica (múltiples módulos, uso prolongado), no por estética?
- [ ] ¿Variante elegida según el árbol de la sección 7?
- [ ] ¿Jerarquía interna Logo → Búsqueda → Nav → Separador → Config → Usuario?
- [ ] ¿Un único elemento activo, estados hover/focus-visible distintos?
- [ ] ¿Íconos consistentes entre sí?
- [ ] ¿Agrupado si hay 7+ módulos, máximo 2 niveles de profundidad?
- [ ] ¿Fijo en desktop, colapsable en tablet, Drawer en mobile?
- [ ] ¿Los grupos siguen dominio funcional del negocio, no orden alfabético ni de creación?
