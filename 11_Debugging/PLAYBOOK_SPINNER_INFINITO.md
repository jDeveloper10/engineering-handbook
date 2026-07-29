---
title: "Incident Playbook: Spinner Infinito"
category: 11_Debugging
doc_type: runbook
tags: [incident, playbook, ui, loading, react]
summary: "Playbook ante una interfaz colgada en estado de carga: diagnóstico en 30 segundos, causas habituales y checklist de diez puntos de depuración."
keywords: [incident, playbook, ui, loading, react, spinner, infinito, ante, interfaz, colgada, estado, carga, diagnostico, segundos]
updated: 2026-07-27
status: current
---

# 🚨 PLAYBOOK: SPINNER INFINITO

## 🩺 SÍNTOMA
La interfaz se queda colgada con un spinner girando eternamente (en un botón, en toda la página o en una tabla). El usuario no puede interactuar.

## ⏱️ DIAGNÓSTICO EN 30 SEGUNDOS
1. **Network Tab:** ¿Hay un request atascado en `pending`? ¿O el request ya terminó y la UI no se enteró?
2. **Console:** ¿Hay un error rojo gigante que frenó la ejecución de JavaScript impidiendo que `setLoading(false)` se ejecute?
3. **React DevTools:** Selecciona el componente con el spinner. ¿El estado `isLoading` es `true` y nada lo está cambiando?

---

## 🔍 CAUSAS Y SOLUCIONES DE HIERRO

### Causa 1: Promesa No Resuelta (Try sin Finally)
Si un error ocurre dentro de un bloque `try` y no hay un bloque `finally`, el `setLoading(false)` jamás se ejecuta.
**Solución:** ES OBLIGATORIO mutar los estados de carga en el bloque `finally`.

```tsx
// ❌ PROHIBIDO
setLoading(true)
try {
  await api.submit()
  setLoading(false) // Si submit() falla, el spinner NUNCA se quita.
} catch (e) {
  console.error(e)
}

// ✅ OBLIGATORIO
setLoading(true)
try {
  await api.submit()
} catch (e) {
  handleError(e)
} finally {
  setLoading(false) // Siempre se quita
}
```

### Causa 2: Estado Actualizado en Componente Desmontado
Inicias un request, navegas a otra ruta, el request termina e intenta hacer `setLoading(false)` pero el componente ya no existe.
**Solución:** El estado local no importa si el componente se desmontó, pero si hay leaks de memoria, es mejor cancelar el request con un `AbortController` en el unmount (React Query lo hace automático).

### Causa 3: API No Responde (Sin Timeout)
El servidor está caído, pero la conexión no se cierra, dejando el request en el limbo.
**Solución:** Todo `fetch` manual DEBE tener un AbortSignal con timeout. (Ver Playbook Upload Fail).

### Causa 4: useEffect en Bucle Infinito
Un efecto se dispara, cambia un estado, lo que re-renderiza y dispara el efecto de nuevo. La app colapsa y el spinner no avanza.
**Solución:** NUNCA uses objetos o funciones en el array de dependencias sin envolverlos en `useMemo` o `useCallback`.

### Causa 5: React Query en Retry Perpetuo
React Query reintenta 3 veces por defecto con backoff. Si la red falla, el spinner puede durar 30 segundos.
**Solución:** Configurar reintentos agresivamente bajos para queries orientadas a usuario.

```tsx
// ✅ Configuración estricta en el QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Solo reintentar una vez
      staleTime: 5 * 60 * 1000,
    },
    mutations: {
      retry: 0, // Nunca reintentar mutaciones a ciegas
    }
  },
})
```

### Causa 6: Error Silencioso de CORS o Red
El navegador bloquea el request por CORS ANTES de salir a la red. El catch captura un `TypeError: Failed to fetch`. Si no tienes feedback visual, el usuario se queda con el spinner.
**Solución:** ES OBLIGATORIO mostrar Toasts/Alertas en los bloques `catch`.

---

## 📋 CHECKLIST DE 10 PUNTOS DE DEBUGGING

Ejecuta esto sin piedad cuando veas un spinner infinito:

1. [ ] **F5 (Refresh)**: ¿Se arregla? Era un estado corrupto en memoria.
2. [ ] **Consola JS**: ¿Hay errores en rojo que rompieron el render cycle?
3. [ ] **Network Tab**: Filtra por `Fetch/XHR`. ¿Hay requests en estado `Pending`?
4. [ ] **CORS**: ¿El request falló con `CORS error` instantáneamente?
5. [ ] **Finally Block**: Revisa el código del botón. ¿El `setLoading(false)` está dentro de un `finally`?
6. [ ] **Hooks de Terceros**: Si usas un hook (ej: `useUser`), ¿devuelve un estado `isLoading` atascado?
7. [ ] **WebSockets**: Si dependes de un mensaje WS para quitar el spinner, ¿se desconectó el socket?
8. [ ] **Deadlock Visual**: ¿Hay una superposición de un modal invisible bloqueando los clicks?
9. [ ] **Bloqueo del Hilo Principal**: Haz un Profiling en Chrome. ¿Hay una tarea larga de JS de 5 segundos que congeló la UI?
10. [ ] **React Error Boundary**: ¿La UI falló de forma invisible y quedó en una versión rota del DOM? (Implementar ErrorBoundaries).
