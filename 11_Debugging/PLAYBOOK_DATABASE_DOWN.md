---
title: "Incident Playbook: Database Down"
category: 11_Debugging
doc_type: runbook
tags: [incident, playbook, database, d1, supabase, outage]
summary: "Playbook ante base de datos caída: diagnóstico en 30 segundos, causas habituales como agotamiento del pool de conexiones, y código de circuit breaker con fallback."
keywords: [incident, playbook, database, d1, supabase, outage, down, ante, base, datos, caida, diagnostico, segundos, causas]
updated: 2026-07-29
status: current
---

# PLAYBOOK: DATABASE DOWN

## SÍNTOMA
La app carga, pero no hay datos. Todo devuelve `Error 500`. El log de errores está inundado de `Connection pool timeout`, `Database is uncontactable`, o `Query execution failed`.

## DIAGNÓSTICO EN 30 SEGUNDOS
1. **Cloudflare D1 Dashboard:** Revisa latencia media y ratio de errores. ¿Estás tocando el límite de filas leídas por segundo?
2. **Supabase Dashboard (si aplica):** ¿La CPU de la DB está al 100%? ¿Memoria llena?
3. **Logs:** ¿El error es de red (`timeout`) o de autorización (`RLS denied`)?

---

## CAUSAS Y SOLUCIONES DE HIERRO

### Causa 1: Connection Pool Agotado (Supabase/Postgres)
Miles de workers intentan abrir una conexión TCP a la base de datos simultáneamente.
**Solución:** PROHIBIDO conectar Cloudflare Workers directamente al puerto 5432 de Postgres. Es OBLIGATORIO usar Supabase Data API (REST) o un proxy como PgBouncer/Supavisor en modo Transaction.

### Causa 2: Query Bloqueante (Sin Índice)
Alguien hizo un `JOIN` a una tabla de 2 millones de filas sin índice. La CPU de la DB llegó a 100% y mató el resto de las consultas.
**Solución:** Ve a *Query Performance* en Supabase / D1. Identifica la query con `EXPLAIN ANALYZE`. **Máta la conexión (Kill PID)** y revierte el PR hasta que tenga un índice.

### Causa 3: RLS Policy Bloqueando (Error Silencioso)
Si Supabase devuelve arrays vacíos `[]` donde debería haber datos, la DB no está caída: las RLS policies cambiaron y el usuario quedó sin acceso.
**Solución:** Verifica que `auth.uid()` se está pasando correctamente en el Token JWT de Supabase desde el Worker.

### Causa 4: Migración Rota
Acabas de deployar y la DB está caída.
**Solución:** ES OBLIGATORIO ejecutar la migración de reversión (`down`). Si no tiene script de reversión, despide a quien aprobó el PR (broma, pero escríbele un warning severo).

### Causa 5: Rate Limiting
Si usas D1 y pasas las 100,000 queries gratuitas rápidas o el límite de concurrencia, recibirás errores de backoff.

---

## CÓDIGO: CIRCUIT BREAKER Y FALLBACK

Si la DB muere, el sitio no debería morir. ES OBLIGATORIO implementar un Circuit Breaker que devuelva caché (Stale data) en lugar de una pantalla en blanco.

```typescript
// Implementación de Lectura Resiliente con KV Fallback
export async function resilientQuery<T>(
  env: Env,
  cacheKey: string,
  queryFn: () => Promise<T>,
  ttlSeconds = 300
): Promise<T> {
  try {
    // 1. Intentar DB primero (con timeout ultra estricto de 3 segundos)
    const dbPromise = queryFn()
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('DB Timeout')), 3000)
    )
    
    const result = await Promise.race([dbPromise, timeoutPromise]) as T
    
    // 2. Si tuvo éxito, actualizar el KV como copia de seguridad en background (sin await)
    env.KV.put(cacheKey, JSON.stringify(result)).catch(e => console.error('KV Save Failed'))
    
    return result;
    
  } catch (error) {
    console.error('DB ERROR, ACTIVANDO FALLBACK KV:', error)
    
    // 3. CIRCUIT BREAKER ACTIVADO: Leer última versión conocida
    const backup = await env.KV.get(cacheKey, 'json')
    if (backup) {
      // Modificamos el objeto para avisarle al Frontend que los datos están desactualizados
      return { 
        ...backup as object, 
        _degraded: true, 
        _notice: "Estamos experimentando latencia. Datos en caché." 
      } as T
    }
    
    // 4. Si no hay DB ni caché, explotar con gracia
    throw new Error('Servicio temporalmente inaccesible.')
  }
}

// Uso en tu endpoint:
const activeProducts = await resilientQuery(
  env, 
  'products:active',
  () => env.DB.prepare('SELECT id, name, price_cents, active FROM products WHERE active = 1').all()
)
```

**Acción Frontend:** Si el frontend detecta `_degraded: true`, debe desactivar los botones de guardado y mostrar un banner amarillo que diga: *"Modo solo lectura: la base de datos está en mantenimiento."*
