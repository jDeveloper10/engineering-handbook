---
title: "Feature Kickstart (El Checklist Maestro)"
category: 00_Fundamentos
tags: [checklist, kickoff, feature, arquitectura]
status: current
---

# Feature Kickstart (El Checklist Maestro)

Este checklist de 77 preguntas es OBLIGATORIO antes de empezar a programar cualquier feature. Su propósito es extraer todas las dependencias ocultas, estados de error y reglas de plataforma para evitar bloqueos durante la implementación. 

Cópialo en la descripción de tu tarea (Jira/Linear) o úsalo como prompt inicial con una IA.

---

## FASE 0: Definición del Feature
- [ ] ¿Cuál es el problema exacto del usuario que estamos resolviendo?
- [ ] ¿Cuál es la métrica de éxito? (ej. el cliente puede pagar en < 10 segundos).
- [ ] ¿Hay diseños de UI/UX aprobados y casos de borde contemplados?

## FASE 1: Base de Datos (`04_Database`)
- [ ] ¿Qué tablas nuevas necesito? (Nombradas en `snake_case` plural).
- [ ] ¿He usado `uuid` generado aleatoriamente para los IDs expuestos?
- [ ] ¿Todos los montos monetarios están como `bigint` (centavos)?
- [ ] ¿Todas las fechas están como `timestamptz` (nunca `timestamp` sin zona)?
- [ ] ¿Cada Foreign Key tiene su propio `CREATE INDEX` explícito en la migración?
- [ ] ¿La migración incluye el bloque `DOWN` para rollback seguro?
- [ ] ¿La nueva tabla guarda datos sensibles que deban ser cifrados?
- [ ] **[RLS]** ¿La tabla expone o relaciona datos de usuarios? (Requiere RLS habilitado).
- [ ] **[RLS]** ¿Están diseñadas las políticas de INSERT, SELECT, UPDATE y DELETE (separadas)?
- [ ] **[RLS]** ¿Tengo un test conceptual de que el Usuario A NO puede borrar datos del B?
- [ ] ¿Los campos repetitivos deberían ser un `enum` o una tabla de catálogo?
- [ ] ¿La consulta principal usa `.select('id, name')` explícito en vez de `SELECT *`?
- [ ] ¿Hay búsquedas paginadas planificadas? (Usar limit/offset y count).
- [ ] ¿Hay lógicas de negocio ocultas en triggers? (PROHIBIDO. Mover al Worker).
- [ ] ¿La inserción múltiple requiere un `BEGIN/COMMIT` o un `SAVEPOINT`?

## FASE 2: API y Backend (`02_Backend`, `03_API`)
- [ ] ¿La ruta del endpoint nombra recursos en plural (ej. `/api/proposals`)?
- [ ] ¿Estoy usando `PATCH` para actualizaciones parciales (nunca `PUT`)?
- [ ] ¿El Worker que manejará esto es el correcto o debo crear un dominio nuevo?
- [ ] ¿El endpoint está dividido en Router → Middleware → Handler → Service?
- [ ] ¿Tengo un Schema de Zod estricto para validar el Body/Params de entrada?
- [ ] ¿Los errores se devuelven usando el formato `jsonResponse` estándar?
- [ ] ¿Los códigos de error son `SCREAMING_SNAKE_CASE` manejables por el front?
- [ ] ¿Hay rate limiting configurado? (Obligatorio en endpoints públicos).
- [ ] ¿Las variables de entorno requeridas están documentadas en el Worker?
- [ ] ¿Hay comunicación cross-worker usando Service Bindings?
- [ ] ¿El endpoint requiere paginación por defecto?
- [ ] ¿El endpoint maneja correctamente el CORS (preflight `OPTIONS`)?

## FASE 3: Frontend (`01_Frontend`)
### Estructura y Reglas
- [ ] ¿Cada componente nuevo está en un archivo único y exportado por nombre?
- [ ] ¿Tengo tipos estrictos (`type` o `interface`) para los Props? (Cero `any`).
- [ ] ¿Estoy evitando usar `index` de un map como `key` en listas dinámicas?
- [ ] ¿La lógica de negocio está delegada a custom hooks?

### Estados de UI (Los 4 Fantásticos)
- [ ] **Loading:** ¿Tengo un skeleton diseñado (no un spinner genérico de pantalla completa)?
- [ ] **Empty:** ¿Hay una ilustración + Copy + CTA para cuando no hay datos?
- [ ] **Error:** ¿El error es amigable ("Oops, reintenta") y permite hacer retry?
- [ ] **Success:** ¿El estado de éxito muestra un feedback claro (Toast/Redirección)?

### Datos y Formularios
- [ ] ¿Las peticiones al servidor se hacen OBLIGATORIAMENTE con React Query (no `useEffect`)?
- [ ] ¿Hay mutaciones optimistas implementadas para respuestas instantáneas al clic?
- [ ] ¿El formulario se valida en tiempo real con Zod y React Hook Form?
- [ ] ¿Los inputs de validación remota (ej. email) tienen debounce?
- [ ] ¿Tengo protección Dirty State (`beforeunload`) para no perder datos tipeados?
- [ ] ¿El botón de submit se deshabilita mientras `isPending` es true?

### UX de Listas Complejas
- [ ] Si cargo más de 1000 items, ¿tengo virtualización (Tanstack Virtual)?
- [ ] ¿Tengo filtros en URL (Search Params) para que la página sea compartible?
- [ ] ¿Tengo botones claros para ordenar la tabla?

## FASE 4: Casos de Borde (Lo que siempre se olvida)
- [ ] **Doble Clic:** ¿Qué pasa si el usuario clica el botón de "Pagar" dos veces rápidas?
- [ ] **Offline:** ¿El frontend maneja la pérdida de conexión elegantemente?
- [ ] **Timeouts:** ¿Si el backend tarda 30s, el frontend aborta la petición a los 15s?
- [ ] **Permisos cruzados:** ¿Qué pasa si un usuario copia el link ID de otro usuario?
- [ ] **Expiración:** ¿Un link público tiene vigencia? ¿Qué pasa al vencer?
- [ ] **Realtime:** Si usamos Supabase WebSockets, ¿el componente limpia su suscripción al desmontarse?
- [ ] **Imágenes rotas:** ¿Si un avatar no carga, hay un fallback visual?
- [ ] **Overflow:** ¿Qué pasa con un título de 200 caracteres sin espacios? ¿Rompe el layout flex?
- [ ] **Eliminación en cascada:** Al borrar un usuario, ¿se borran sus datos huérfanos?
- [ ] **Dark Mode:** ¿Los nuevos colores funcionan bien en modo oscuro?
- [ ] **Soft Delete:** ¿Necesito mantener el registro (`deleted_at`) en lugar de borrar la fila física?
- [ ] **Cold Starts:** ¿El feature tolera un pico de 1s de latencia si el Worker está frío?

## FASE 5: Testing (`06_Testing`)
- [ ] ¿He testeado los 4 estados de la UI (Loading, Empty, Error, Success)?
- [ ] ¿He probado que RLS bloquea los intentos de robo cruzado de datos?
- [ ] ¿He testeado cómo reacciona el form cuando la API devuelve un HTTP 500?
- [ ] ¿He escrito un test para la mutación optimista (el rollback en caso de fallo)?
- [ ] ¿El rate limiter fue probado empíricamente contra spam?
- [ ] ¿El schema de Zod fue puesto a prueba contra inyecciones y payloads extraños?
- [ ] ¿He pasado herramientas de accesibilidad (axe) sobre el nuevo HTML?
- [ ] ¿He testeado el diseño en un viewport de 320px (iPhone SE viejo)?

## FASE 6: Antes de Abrir el PR (`10_Code_Quality`)
- [ ] ¿He corrido la migración SQL (`up` y `down`) en una DB limpia local?
- [ ] ¿Verifiqué con `EXPLAIN ANALYZE` que no agregué queries N+1 en las tablas pesadas?
- [ ] ¿Los secretos nuevos están seteados con `wrangler secret put` en staging/prod?
- [ ] ¿Actualicé el README o CHANGELOG del repositorio?
- [ ] ¿Hay alguna nueva decisión de arquitectura que merezca un ADR?
- [ ] ¿El linter (`eslint`) y el verificador de tipos (`tsc --noEmit`) corren sin errores?
- [ ] ¿Borraron todos los `console.log` de debuggeo de mi rama?
- [ ] ¿El nombre de mi rama y mis commits siguen la convención `feat/`, `fix/`?
- [ ] ¿Verifiqué personalmente el Diff final en GitHub/GitLab antes de pedir revisión?
- [ ] **[CRÍTICO]** ¿Completo todos los checks del `FEATURE_PR_TEMPLATE.md`?
