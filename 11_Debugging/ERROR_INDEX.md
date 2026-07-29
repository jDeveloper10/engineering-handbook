---
title: "Índice de Errores Global"
category: 11_Debugging
doc_type: referencia
tags: [errors, debugging, troubleshooting]
summary: "Índice unificado de los 20 errores más frecuentes de todo el stack con su causa y solución, agrupados por frontend, backend en el edge y base de datos."
keywords: [errors, debugging, troubleshooting, indice, errores, global, unificado, frecuentes, stack, causa, solucion, agrupados, frontend, backend]
updated: 2026-07-27
status: current
---

# 🚨 Índice de Errores (Troubleshooting)

Este es el índice unificado (Top 20) de errores comunes a lo largo de todo el stack de la aplicación (Frontend, Backend, Database, Cloud). 
El propósito de este documento es **reducir la dependencia de Google** (Zero-Google). Si encuentras un error, busca primero aquí.

## Frontend (React / TypeScript)

| Error | Posible Causa | Solución Rápida |
|-------|---------------|-----------------|
| `Cannot read property 'map' of undefined` | Estás intentando mapear un array que aún no ha cargado de la API (es `undefined` en el primer render). | Usa Optional Chaining: `data?.map()`, o renderiza condicionalmente: `if (!data) return <Skeleton/>`. |
| `Too many re-renders` | Estás mutando estado de React directamente en el cuerpo del render, o dentro de un evento sin usar callback (ej. `onClick={setCount(1)}`). | Pasa una función al evento: `onClick={() => setCount(1)}`. |
| `Hydration failed because the initial UI does not match what was rendered on the server` | (Si usas SSR/Next.js) El HTML generado en el servidor difiere del que el navegador intenta montar (ej. fechas, uso de `window`). | Usa un hook `useEffect` o `useMounted` para renderizar contenido específico del cliente después del montaje. |
| `React Hook "useEffect" is called conditionally` | Estás llamando a un Hook dentro de un `if` o después de un `return` temprano, rompiendo el orden de Hooks. | Mueve todos los hooks a la parte superior del componente. No los anides en condicionales. |
| `TS2322: Type 'X' is not assignable to type 'Y'` | Conflicto de tipado de TypeScript. Suele ocurrir al pasar props que esperan un tipo exacto y se les pasa algo más genérico. | Asegúrate de usar la interfaz correcta o hacer un cast explícito (`as Y`) solo si estás 100% seguro de los datos. |

## Backend / Edge (Cloudflare Workers)

| Error | Posible Causa | Solución Rápida |
|-------|---------------|-----------------|
| `Worker exceeded CPU time limit` | Un bucle infinito, regex ineficiente, o procesamiento criptográfico muy pesado que supera los límites (10ms a 50ms según plan). | Mueve el trabajo pesado a **Cloudflare Queues** o optimiza el bucle. El Edge es para respuestas rápidas. |
| `TypeError: fetch failed` o `Network connection lost` | El Worker está intentando hacer una petición HTTP a una URL externa que está caída, o no has usado `await`. | Asegúrate de usar `await fetch()`. Maneja los errores con bloques `try/catch`. |
| `Uncaught (in promise) Error: The script will never generate a response` | El handler principal de Fetch no retornó una instancia de `Response`, o se olvidó un `return` en una rama de un condicional. | Revisa que todos los caminos lógicos retornen un `new Response(...)`. |
| `Cross-Origin Request Blocked (CORS)` | El navegador bloqueó la llamada a la API porque el Worker no devolvió los headers `Access-Control-Allow-Origin`. | Añade middleware CORS en Hono/Router que inyecte los headers apropiados (`Access-Control-Allow-Origin: *` o tu dominio). |
| `KV/R2 limit exceeded` | Superaste los límites de llamadas gratuitas de lectura/escritura de los servicios de almacenamiento de Cloudflare. | Implementa caché de lectura (Cache API) delante del KV para reducir la carga, o revisa el tier de facturación. |

## Database (Supabase / Postgres)

| Error | Posible Causa | Solución Rápida |
|-------|---------------|-----------------|
| `new row violates row-level security policy for table "X"` | Tienes activado RLS en la tabla, pero el usuario autenticado (o anon) no cumple las condiciones de la política `INSERT`/`UPDATE`. | Revisa tus políticas RLS en Supabase. Asegúrate de estar pasando el JWT correctamente si accedes por API. |
| `duplicate key value violates unique constraint` | Intentas insertar un registro con un valor (ej. email) que ya existe y la columna tiene un índice `UNIQUE`. | Haz un `SELECT` previo para verificar, o usa `INSERT ... ON CONFLICT DO UPDATE/NOTHING` (Upsert). |
| `deadlock detected` | Dos transacciones concurrentes están intentando actualizar las mismas filas en orden opuesto. | Asegúrate de actualizar las tablas siempre en el mismo orden lexicográfico en todo el backend. |
| `relation "X" does not exist` | La tabla no existe, te equivocaste de esquema, o faltó ejecutar las migraciones. | Corre las migraciones (`supabase db push`) y verifica si estás apuntando al esquema `public`. |
| `JWT expired` o `Auth session missing` | El token de acceso del usuario ha caducado y no se ha refrescado. | En el cliente (React), maneja la lógica para renovar la sesión o redirige a `/login`. |
