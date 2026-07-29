---
title: "Recetas de Refactoring"
category: 10_Code_Quality
doc_type: referencia
tags: [refactoring, code quality, recipes]
summary: "Recetas paso a paso para limpiar deuda técnica: extraer un custom hook, reemplazar switches largos por diccionarios y simplificar Workers hinchados."
keywords: [refactoring, code-quality, recipes, recetas, paso, limpiar, deuda, tecnica, extraer, custom, hook, reemplazar, switches, largos]
updated: 2026-07-27
status: current
---

# 🛠️ Recetas de Refactoring

Estas recetas te guían paso a paso para limpiar código acoplado o deuda técnica en el proyecto, siguiendo los estándares del manual sin necesidad de buscar técnicas externas.

## Receta 1: Extraer un Custom Hook (React)

**Problema:** Un componente de UI tiene demasiada lógica de estado (fetching, formateo de datos, handlers complejos) mezclada con el renderizado.

**Paso a paso:**
1. Crea un archivo nuevo (ej. `useUserDashboard.ts`).
2. Mueve todos los `useState`, `useEffect` y funciones helper a ese hook.
3. El hook debe retornar únicamente los datos que la UI necesita renderizar y las funciones que la UI necesita disparar (eventos).
4. En el componente original, importa el hook: `const { data, loading, onSave } = useUserDashboard(userId)`.

## Receta 2: Reemplazar Switches Largos por Diccionarios (Objects/Maps)

**Problema:** Una función tiene un `switch` gigante que devuelve diferentes íconos o configuraciones según un string, rompiendo el principio Abierto/Cerrado.

**Paso a paso:**
1. Define un diccionario (Record en TS) fuera del ciclo de render:
   ```ts
   const STATUS_CONFIG: Record<Status, { color: string, icon: IconType }> = {
     'active': { color: 'green', icon: ActiveIcon },
     'pending': { color: 'yellow', icon: PendingIcon },
     // ...
   }
   ```
2. Reemplaza el `switch` por una búsqueda directa en el objeto: `const config = STATUS_CONFIG[status] ?? STATUS_CONFIG['default']`.

## Receta 3: Simplificar Workers Hinchados (Cloudflare)

**Problema:** Un archivo `index.ts` en un Worker de Cloudflare tiene 1000 líneas y maneja todo el enrutamiento y la lógica de negocio.

**Paso a paso:**
1. Instala un enrutador ligero como **Hono** si no está en uso.
2. Crea una carpeta `routes/` y separa los endpoints por dominio (ej. `routes/users.ts`).
3. Crea una carpeta `services/` y extrae la lógica de negocio pura, fuera del objeto `Request` de HTTP.
4. En el `index.ts` solo debe quedar la inicialización del enrutador y la vinculación de middlewares (CORS, Auth).
