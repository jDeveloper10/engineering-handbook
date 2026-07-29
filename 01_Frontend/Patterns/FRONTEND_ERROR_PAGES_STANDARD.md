# FRONTEND ERROR PAGES STANDARD (404 / 500 / Sin acceso)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 2.2 Error Boundaries) y de [FRONTEND_STATES_PATTERNS.md](FRONTEND_STATES_PATTERNS.md) (errores a nivel de componente). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Distinto de `FRONTEND_STATES_PATTERNS.md`: ese documento cubre cuando *una parte* de la pantalla falla (un widget, una tabla). Este cubre cuando *toda la pantalla* no puede mostrarse — ruta inexistente, error no capturado, falta de permiso.

---

## 1. Regla principal

**[REQUIRED]** Toda app define explícitamente 4 pantallas de error a nivel de página, no solo el error de componente: **404** (ruta no existe), **403** (sin permiso), **500 / error no capturado** (algo se rompió), y el estado offline si el producto lo amerita (ver `FRONTEND_STATES_PATTERNS.md` sección 4).

**[REQUIRED]** Ninguna de estas pantallas es una página en blanco desconectada del resto del producto — el header/logo/navegación básica siguen visibles, para que el usuario no sienta que "salió" de la app.

---

## 2. 404 — Ruta no existe

**[REQUIRED]** Mensaje claro en el idioma del usuario, no solo "Error 404" o un código sin contexto. CTA explícito para recuperarse: volver al inicio, o buscar si el producto tiene búsqueda.

```
❌ 404
✅ No encontramos esta página. [Volver al inicio]
```

---

## 3. 403 — Sin permiso

**[REQUIRED]** Se distingue explícitamente de un 404 — decir que el recurso existe pero el usuario no tiene acceso, no simular que no existe.

**Excepción documentada:** si por razones de seguridad se prefiere no confirmar la existencia de un recurso (mismo principio que `FRONTEND_AUTH_PATTERNS.md` sección 13, no revelar si un email existe), esa decisión se toma a propósito y se documenta — no es el comportamiento por defecto.

---

## 4. 500 / Error no capturado

**[REQUIRED]** Capturado por un Error Boundary (`FRONTEND_ENGINEERING_STANDARD.md` sección 2.2) a nivel de sección o de página — un error en una parte de la app no debería tumbar toda la sesión del usuario si se puede evitar.

**[REQUIRED]** Mensaje genérico y accionable al usuario ("Algo salió mal. Inténtalo de nuevo."), nunca un stack trace o detalle técnico crudo — mismo principio que `FRONTEND_ENGINEERING_STANDARD.md` sección 6.3. **[REQUIRED]** el error real se registra automáticamente en el sistema de logging del equipo (Sentry u equivalente) — el usuario nunca es la única fuente de reporte de un bug de producción.

**[RECOMMENDED]** Un botón de "Reintentar" cuando el error es plausible que sea temporal (fallo de red), y "Volver al inicio" siempre disponible como salida segura.

---

## 5. Anti-patrones

- ❌ Página de error en blanco, sin logo ni navegación, que rompe la continuidad visual del producto.
- ❌ "Error 404" o "Error 500" sin ningún texto explicativo ni acción siguiente.
- ❌ Stack trace o mensaje técnico crudo mostrado al usuario.
- ❌ Un error de una sección tumbando toda la aplicación por no tener Error Boundary.
- ❌ Un error de producción real que solo se entera el equipo si el usuario decide reportarlo manualmente.

---

## Checklist rápido

- [ ] ¿Existen pantallas dedicadas para 404, 403 y error no capturado, no solo una genérica?
- [ ] ¿Header/navegación siguen visibles en la pantalla de error?
- [ ] ¿403 se distingue de 404, salvo excepción de seguridad documentada?
- [ ] ¿El error real se registra automáticamente para el equipo (no depende de que el usuario reporte)?
- [ ] ¿Mensaje accionable, sin detalle técnico crudo, con salida clara (reintentar / volver al inicio)?
