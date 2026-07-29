# FRONTEND UI STATES PATTERNS (Loading / Empty / Error)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 4.2 — estados obligatorios en componentes con datos). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> La sección 4.2 del estándar principal exige que estos 4 estados existan (loading, error, empty, success). Este documento define **cómo diseñar cada uno bien**, no solo que deben estar presentes. Contrastado contra Nielsen Norman Group (percepción de espera, mensajes de error) y Material Design (skeletons).

---

## 1. Loading states

**[REQUIRED]** Skeleton (placeholder con la forma del contenido que va a cargar) para contenido con layout conocido — listas, tablas, cards. **[RECOMMENDED]** spinner solo para acciones puntuales cortas (submit de un botón, una acción de menos de ~2 segundos).

**Por qué:** un skeleton reduce la percepción de espera porque el usuario ya ve la estructura que viene — un spinner genérico no comunica cuánto ni qué está cargando, y para listas/tablas se siente más lento aunque tarde lo mismo.

```
❌ Spinner centrado reemplazando toda una tabla de 10 filas
✅ 10 filas skeleton con el mismo layout que las filas reales
```

**[REQUIRED]** Ninguna carga queda sin límite de tiempo percibido — si una acción puede tardar mucho, se comunica progreso o al menos que sigue en curso, nunca un spinner que simplemente podría estar colgado.

---

## 2. Empty states

**[REQUIRED]** Todo estado vacío tiene: mensaje claro de qué significa el vacío + una acción si existe una. **[REQUIRED]** distinguir el motivo del vacío:

| Motivo | Mensaje | CTA |
|---|---|---|
| Nunca hubo datos (cuenta nueva) | "Aún no tienes productos" | "Crear tu primer producto" |
| Vacío por filtros/búsqueda activa | "No encontramos resultados para 'x'" | "Limpiar filtros" |
| Vacío permanente (sin acción posible) | Mensaje descriptivo | Sin CTA forzado |

**Por qué:** "No hay datos" genérico no le dice al usuario si el problema es que no ha hecho nada todavía, o que su búsqueda no encontró nada — son dos situaciones con acciones siguientes completamente distintas.

---

## 3. Error states

**[REQUIRED]** El mensaje de error es accionable, sin jerga técnica ni código de estado crudo (ver `FRONTEND_ENGINEERING_STANDARD.md` sección 6.3, `AppError`). **[REQUIRED]** si el error es de red/temporal, se ofrece un botón de reintentar.

```
❌ "Error 500"
✅ "No pudimos cargar tus órdenes. [Reintentar]"
```

**[RECOMMENDED]** Distinguir error a nivel de componente/sección (solo esa parte de la pantalla falla, el resto sigue usable) de error a nivel de página completa (Error Boundary de `FRONTEND_ENGINEERING_STANDARD.md` sección 2.2) — un error de un widget no debería tumbar toda la pantalla.

---

## 4. Estado sin conexión

**[RECOMMENDED]** Si el producto lo amerita (uso mobile, conexión inestable esperable), un estado explícito de "sin conexión" distinto del error genérico — con reintento automático al recuperar conexión si es viable.

---

## 5. Copy — tono y longitud

**[REQUIRED]** Mensajes de loading/empty/error en el idioma del usuario, cortos (1 línea principal + máximo 1 línea de apoyo), sin tecnicismos. Mismo principio ya aplicado en `FRONTEND_AUTH_PATTERNS.md` sección 9, generalizado a cualquier estado de la app.

---

## 6. Anti-patrones

- ❌ Spinner que puede quedar girando indefinidamente sin timeout ni mensaje de "esto está tardando más de lo normal".
- ❌ Empty state genérico ("No hay datos") sin distinguir motivo ni ofrecer acción.
- ❌ Mensaje de error que es solo un ícono roto o un código sin texto.
- ❌ Un error de un widget tumbando toda la pantalla en vez de aislarse.
- ❌ Loading con spinner centrado reemplazando layouts conocidos (listas/tablas) en vez de skeleton.

---

## Checklist rápido

- [ ] ¿Loading usa skeleton para layouts conocidos, spinner solo para acciones puntuales cortas?
- [ ] ¿Empty state distingue "nunca hubo datos" de "vacío por filtro", con CTA correspondiente?
- [ ] ¿Error accionable, sin jerga técnica, con reintentar si es de red?
- [ ] ¿Error de un componente aislado no tumba toda la pantalla?
- [ ] ¿Copy corto, en el idioma del usuario, sin códigos técnicos?
