---
title: "Estándar de Codificación y Calidad de Agencia"
category: 10_Code_Quality
doc_type: estandar
tags: [code-quality, clean-code, error-handling, zod, envelope, typescript]
summary: "Reglas de codificación obligatorias para la agencia: validación estricta de inputs con Zod, tratamiento real de errores (prohibido try/catch vacíos y falsos 200 OK), formato de envelope estándar { ok, data } / { ok, error } y principios de Clean Code pragmático."
keywords: [clean-code, error-handling, zod, envelope, typescript, estandares, calidad]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "02_Backend/BACKEND_ENGINEERING_STANDARD.md"
  - "03_API/API_ENGINEERING_STANDARD.md"
  - "10_Code_Quality/Reviews/CODE_REVIEW_STANDARD.md"
---

# ESTÁNDAR DE CODIFICACIÓN Y CALIDAD DE AGENCIA

> **Objetivo:** Garantizar que todo el código escrito en la agencia (por humanos o IAs) sea predecible, seguro, fácil de mantener por cualquier miembro del equipo y libre de vicios clásicos de programación.

---

## 1. Reglas Inquebrantables de Manejo de Errores

### ERR-001: Tratar los Errores como Errores (Cero Falsos 200 OK)

**[REQUIRED]** Si una operación falla (falló la base de datos, credenciales inválidas, saldo insuficiente o input erróneo), **el código de estado HTTP DEBE reflejar el fallo** (`400`, `401`, `403`, `404`, `422`, `500`).

* ❌ **PROHIBIDO:** Devolver `HTTP 200 OK` con un cuerpo `{ error: "No autorizado" }` o `{ success: false }`.
* ❌ **PROHIBIDO:** Bloques `try { ... } catch (e) {}` vacíos que silencian excepciones sin loguear ni propagar.

```typescript
// ❌ CÓDIGO MALO (Falso 200 y error silenciado):
try {
  await db.update(...)
} catch (e) {
  return new Response(JSON.stringify({ ok: false, error: 'Ocurrió un error' }), { status: 200 })
}

// ✅ CÓDIGO CORRECTO:
try {
  const result = await db.update(...)
  return new Response(JSON.stringify({ ok: true, data: result }), { status: 200 })
} catch (err) {
  console.error('[DATABASE_ERROR]', err)
  return new Response(JSON.stringify({
    ok: false,
    error: 'No se pudo actualizar el registro',
    code: 'DB_UPDATE_FAILED'
  }), { status: 500 })
}
```

---

### ERR-002: Formato de Envelope Estándar en Todas las Respuestas

**[REQUIRED]** Toda respuesta de API JSON debe seguir estrictamente el contrato canónico definido en `02_Backend/BACKEND_ENGINEERING_STANDARD.md §01` y `03_API/API_ENGINEERING_STANDARD.md §04`:

```typescript
// 1. Respuesta Exitosa:
interface ApiResponseSuccess<T> {
  success: true
  data: T
}

// 2. Respuesta de Error:
interface ApiResponseError {
  success: false
  error: {
    code: string        // Código máquina estable en SCREAMING_SNAKE_CASE (ej. "INVALID_CREDENTIALS")
    message: string     // Mensaje legible para humanos en español
    details?: unknown   // Detalles de validación Zod o campo si aplica
  }
}
```

---

## 2. Validación Rigurosa de Entradas (`S-001`)

**[REQUIRED]** Ni el backend ni el frontend confían en datos sin validar:
* **Frontend:** Valida formularios con Zod antes de enviar la petición (mejora UX y feedback inmediato).
* **Backend:** Valida el body, los query params y las cabeceras con Zod antes de ejecutar cualquier lógica o consulta a base de datos.
* Todo schema Zod descarta propiedades no declaradas (`.strict()` o descarte automático de `safeParse`).

---

## 3. Principios de Clean Code Pragmático

1. **Funciones Cortas y Enfocadas:** Una función hace una sola cosa bien y no debe exceder de ~40 líneas.
2. **Early Returns (Evitar el código pirámide):** Retornar de inmediato en las condiciones de error o borde para mantener el flujo principal en el nivel de indentación raíz:
   ```typescript
   // ✅ CORRECTO:
   function processOrder(order: Order, user: User) {
     if (!user.isActive) return { success: false, error: { code: 'USER_INACTIVE', message: 'Usuario inactivo' } }
     if (order.items.length === 0) return { success: false, error: { code: 'EMPTY_ORDER', message: 'Orden vacía' } }
     
     // Flujo principal limpio
     return executeOrder(order)
   }
   ```
4. **Matriz Única de Nomenclatura Global [REQUIRED]:**
   Para eliminar ambigüedad entre dominios, todo el código y archivos siguen esta tabla canónica sin excepciones:

   | Elemento | Convención | Ejemplo |
   |---|---|---|
   | **Carpetas / Directorios** | `kebab-case` | `features/order-checkout/`, `ui-components/` |
   | **Componentes React** | `PascalCase` (`.tsx`) | `OrderSummary.tsx`, `UserCard.tsx` |
   | **Hooks** | `camelCase` con prefijo `use` | `useAuth.ts`, `useWindowSize.ts` |
   | **Utilidades / Servicios / Handlers** | `camelCase` | `formatCurrency.ts`, `authService.ts` |
   | **Variables y Funciones** | `camelCase` | `userProfile`, `calculateSubtotal()` |
   | **Tipos e Interfaces** | `PascalCase` | `OrderState`, `ApiResponseSuccess` |
   | **Base de Datos (Tablas y Columnas)** | `snake_case` | `order_items`, `created_at` |
   | **Rutas y Endpoints HTTP** | `kebab-case` | `/api/v1/user-profiles`, `/auth/refresh-token` |

