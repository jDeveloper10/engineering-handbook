---
title: "Estándar de Robustez, Resiliencia y Concurrencia de Base de Datos"
category: 04_Database
doc_type: estandar
tags: [database, resiliencia, robustez, concurrencia, deadlocks, circuit-breaker, google-sre, sqlite, d1, postgres]
summary: "Reglas DB-026 a DB-031 inspiradas en Google SRE y patrones de alta disponibilidad: mitigación de deadlocks, reintentos exponenciales con jitter, transacciones atómicas, fail-fast timeouts y circuit breakers para la capa de datos."
keywords: [database, resiliencia, robustez, google-sre, deadlocks, backoff, jitter, circuit-breaker, d1, sqlite, postgres, pool, saturation]
updated: 2026-10-05
status: current
---

# ESTÁNDAR DE ROBUSTEZ, RESILIENCIA Y CONCURRENCIA DE BASE DE DATOS (DB-026 a DB-031)

> Documento del dominio Database (04). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md).
> Complementa a [DATABASE_SCALABILITY_STANDARD.md](DATABASE_SCALABILITY_STANDARD.md) y a [D1_OPTIMIZATION.md](D1_OPTIMIZATION.md).
> Este documento define las reglas de ingeniería para que la base de datos no sufra caídas catastróficas (*cascading failures*), bloqueos mutuos (*deadlocks*) ni corrupción de datos bajo concurrencia extrema, aplicando los principios del **Site Reliability Engineering (SRE) de Google**.

---

## REGLAS INQUEBRANTABLES

### DB-026: Reintentos Obligatorios con Exponential Backoff y Full Jitter ante Bloqueos Transitorios

**[REQUIRED]** **Por qué:** Cuando múltiples clientes compiten por escribir en la misma tabla o base de datos (como `SQLITE_BUSY` en Cloudflare D1 o serialización en Postgres), un reintento inmediato genera el efecto estampida (*Thundering Herd*), saturando la base de datos justo cuando intenta recuperarse. Añadir un factor exponencial con aleatoriedad (*Jitter*) dispersa las peticiones en el tiempo y permite que la contención se resuelva limpiamente.

**Agnóstico:** Ante un error transitorio de bloqueo (`SQLITE_BUSY`, `40001 serialization_failure`, `55P03 lock_not_available`), la aplicación debe reintentar un máximo de 3 a 5 veces con una espera calculada como:
```
sleep = random_between(0, min(max_delay, base_delay * (2 ^ attempt)))
```

**Implementación de Referencia (TypeScript):**
```typescript
export async function withDbRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  baseDelayMs = 50
): Promise<T> {
  let attempt = 0;
  while (true) {
    try {
      return await operation();
    } catch (err: unknown) {
      attempt++;
      const isTransient = err instanceof Error && (
        err.message.includes('SQLITE_BUSY') ||
        err.message.includes('D1_ERROR') ||
        err.message.includes('deadlock detected') ||
        err.message.includes('could not serialize')
      );
      if (!isTransient || attempt > maxRetries) {
        throw err;
      }
      // Full Jitter exponencial: evita estampidas simultáneas
      const maxDelay = baseDelayMs * Math.pow(2, attempt);
      const jitterDelay = Math.floor(Math.random() * maxDelay);
      await new Promise((resolve) => setTimeout(resolve, jitterDelay));
    }
  }
}
```

---

### DB-027: Fail-Fast Obligatorio mediante Statement y Query Timeouts

**[REQUIRED]** **Por qué:** Una consulta colgada o bloqueada por un lock acapara una conexión del pool y consume recursos de memoria indefinidamente. Si entran 50 consultas similares, agotan el pool de conexiones en segundos. Cortar rápido protege la salud de todos los demás usuarios del sistema.

**Agnóstico:** Toda consulta y mutación a la base de datos debe tener un tiempo de vida máximo estricto (3 a 5 segundos). Si la base de datos o el driver no responde en ese tiempo, se debe abortar la ejecución inmediatamente arrojando un error claro de timeout.

**Implementación (SQL / Prisma / Cloudflare Workers):**
```typescript
export function withDbTimeout<T>(promise: Promise<T>, timeoutMs = 5000): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(`Database query timeout tras ${timeoutMs}ms`)), timeoutMs)
    )
  ]);
}
```

---

### DB-028: Transacciones Atómicas Aisladas contra Condiciones de Carrera

**[REQUIRED]** **Por qué:** Leer un valor (ej. balance contable o stock de producto) y actualizarlo en dos sentencias separadas sin transacción atómica produce inconsistencias matemáticas cuando dos usuarios ejecutan la acción al mismo milisegundo (Race Condition).

**Agnóstico:** Las operaciones que alteran balances, inventarios o estados contables deben ejecutarse en un único bloque atómico (o sentencia SQL atómica).

```sql
-- ❌ INSUFICIENTE: Carrera si dos usuarios compran a la vez
-- SELECT stock FROM productos WHERE id = 1;
-- UPDATE productos SET stock = stock - 1 WHERE id = 1;

-- ✅ SEGURO: Mutación atómica con verificación en la misma sentencia
UPDATE productos 
SET stock = stock - 1 
WHERE id = 1 AND stock >= 1;
```

En Cloudflare D1 (donde Prisma no soporta transacciones interactivas), es **REQUIRED** usar `db.batch([...])` mediante el binding nativo para agrupar las mutaciones en una sola transacción SQLite atómica.

---

### DB-029: Disyuntor (Circuit Breaker) para Protección de la Capa de Datos

**[RECOMMENDED]** **Por qué:** Principio de Google SRE: si la base de datos está caída o devolviendo errores continuos, seguir enviando el 100% de las consultas de usuarios entrantes solo prolonga la agonía. El disyuntor abre el circuito tras N fallos consecutivos y responde de inmediato con degradación elegante (error 503 controlado o datos en caché) durante un tiempo de enfriamiento.

**Estados del Circuit Breaker:**
1. **CLOSED (Normal):** Todas las consultas pasan a la base de datos.
2. **OPEN (Protección):** La BD falló 5 veces consecutivas. Las consultas se rechazan de inmediato sin tocar la BD durante 15 segundos.
3. **HALF-OPEN (Prueba):** Se permite pasar 1 consulta de prueba. Si triunfa, se cierra el circuito; si falla, se vuelve a abrir.

---

### DB-030: Monitoreo de Saturación del Pool de Conexiones (The 4 Golden Signals)

**[RECOMMENDED]** **Por qué:** En motores relacionales (Postgres, MySQL), el número de conexiones simultáneas es finito (`max_connections`). Si el uso activo del pool supera el 80%, el sistema está a segundos de una caída total.

**Regla:** Mantener pools de conexiones dimensionados con poolers transaccionales (como PgBouncer / Supabase Transaction Pooler) y nunca instanciar un nuevo cliente de base de datos en cada invocación de función sin reutilizar la conexión.

---

## 2. CHECKLIST DE ROBUSTEZ DE BASE DE DATOS

- [ ] Toda query o mutación en endpoints críticos cuenta con timeout estricto (<5s).
- [ ] Los endpoints con alta contención de escritura implementan `withDbRetry` con Exponential Backoff y Jitter.
- [ ] No existen lecturas seguidas de escrituras no atómicas sobre saldos, stock o finanzas.
- [ ] En Cloudflare D1 se utiliza `db.batch()` para mutaciones multipaso indivisibles.
- [ ] Las consultas complejas o de reportes han sido validadas con `EXPLAIN QUERY PLAN` para verificar que usan índices.
- [ ] El sistema degrada con elegancia cuando la base de datos no está disponible.
