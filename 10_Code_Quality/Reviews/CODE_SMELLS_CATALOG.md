---
title: "Catálogo de Code Smells"
category: 10_Code_Quality
tags: [code smells, refactoring, react]
status: current
---

# 👃 Catálogo de Code Smells

Un "code smell" (olor de código) es un síntoma superficial que usualmente corresponde a un problema más profundo en el sistema. A continuación los más comunes en nuestro stack (React/TS) y por qué evitarlos.

## 1. Prop Drilling Excesivo
**Síntoma:** Pasar props a través de 4 o más niveles de componentes que no los usan, solo para hacerlos llegar a un hijo lejano.
**Solución:** Usa la **Context API** para estado global, o **Composición de Componentes** (pasar componentes como `children`).

```tsx
// ❌ SMELL:
function Grandparent({ user }) { return <Parent user={user} /> }
function Parent({ user }) { return <Child user={user} /> }

// ✅ MEJOR (Composición):
function Grandparent({ user }) { 
  return <Parent><Child user={user} /></Parent> 
}
```

## 2. useEffects "Inflados" o en Cascada
**Síntoma:** Un `useEffect` que hace demasiadas cosas diferentes, o múltiples efectos que se disparan en cadena, uno actualizando un estado que dispara el siguiente.
**Solución:** Extrae la lógica de fetch a un custom hook (ej. `useQuery` con React Query) y asegúrate de que los efectos solo sincronicen datos con sistemas externos, no estado interno de React.

## 3. Comentarios como Desodorante
**Síntoma:** Funciones largas explicadas paso a paso con comentarios porque el código es ilegible.
**Solución:** Extrae bloques lógicos a funciones más pequeñas con nombres descriptivos (Self-documenting code).

## 4. Anidamiento Profundo (Arrow Code)
**Síntoma:** `if` dentro de un `if` dentro de un `for`, dejando el código en forma de flecha (`>`).
**Solución:** Usa **Return Temprano (Guard Clauses)**.

```ts
// ❌ SMELL:
function process(user) {
  if (user) {
    if (user.isActive) {
      // do something
    }
  }
}

// ✅ MEJOR:
function process(user) {
  if (!user || !user.isActive) return;
  // do something
}
```
