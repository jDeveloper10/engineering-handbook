---
title: "Estándar de Optimización Quirúrgica"
category: 00_Fundamentos
doc_type: estandar
tags: [optimización, rendimiento, costos, clean-code]
summary: "Reglas O-001 en adelante sobre los tres pilares de la optimización real: código más corto y legible (early returns, destructuring, operadores modernos), rendimiento medido y reducción de costo de infraestructura."
keywords: [optimizacion, rendimiento, costos, clean-code, quirurgica, o-001, adelante, tres, pilares, real, codigo, corto, legible, early]
updated: 2026-07-29
status: current
---

# ⚡ OPTIMIZACIÓN QUIRÚRGICA - CÓDIGO CORTO, RÁPIDO Y BARATO

La diferencia entre un desarrollador y un ingeniero real es escribir menos código que hace más, gasta menos recursos y cuesta menos dinero operativo.

---

## 🎯 LOS 3 PILARES DE LA OPTIMIZACIÓN REAL

1. **CÓDIGO CORTO Y EXPRESIVO** → Menos líneas, más legible, sin repetir
2. **OPTIMIZACIÓN DE RECURSOS** → Menos CPU, menos memoria, menos red
3. **OPTIMIZACIÓN POR COSTO** → Menos filas leídas = menos $$ (D1, R2, Workers)

---

# 📐 PILAR 1: CÓDIGO CORTO Y EXPRESIVO (O-001 a O-007)

## O-001: Early Returns (Adiós a los if-else anidados)

**[RECOMMENDED]** **Por qué:** cada nivel de anidamiento obliga a sostener en la cabeza todas las condiciones de los niveles superiores para entender uno interior. Salir temprano con una guarda reduce esa carga a una condición a la vez. Se desvía cuando la condición final es la única que importa y expresarla como guarda fragmentaría la lógica.

```typescript
// ❌ 30 líneas, 4 niveles de indentación, ILEGIBLE
async function processOrder(orderId: string) {
  if (orderId) {
    const order = await db.findOrder(orderId)
    if (order) {
      if (order.status === 'pending') {
        if (order.total > 0) {
          const result = await db.updateOrder(orderId, { status: 'paid' })
          if (result) {
            return { success: true, order: result }
          } else {
            return { success: false, error: 'Update failed' }
          }
        } else {
          return { success: false, error: 'Invalid total' }
        }
      } else {
        return { success: false, error: 'Order not pending' }
      }
    } else {
      return { success: false, error: 'Order not found' }
    }
  } else {
    return { success: false, error: 'No order ID' }
  }
}

// ✅ 15 líneas, 0 anidamiento, CLARÍSIMO
async function processOrder(orderId: string) {
  if (!orderId) return fail('No order ID')
  
  const order = await db.findOrder(orderId)
  if (!order) return fail('Order not found')
  if (order.status !== 'pending') return fail('Order not pending')
  if (order.total <= 0) return fail('Invalid total')
  
  const result = await db.updateOrder(orderId, { status: 'paid' })
  return result ? { success: true, order: result } : fail('Update failed')
}

const fail = (error: string) => ({ success: false, error })
```

## O-002: Destructuring + Alias (Código que se lee solo)

**[RECOMMENDED]** **Por qué:** nombrar explícitamente qué se extrae de un objeto documenta la forma de los datos en el punto de uso, sin tener que saltar a la definición. Se desvía cuando el objeto se usa completo o el destructuring anidado se vuelve más difícil de leer que el acceso directo.

```typescript
// ❌ Repetitivo, verboso, difícil de leer
const userName = user.name
const userEmail = user.email
const userAge = user.age
const userCity = user.address.city
const userStreet = user.address.street
const userZip = user.address.zipCode

// ✅ Una línea, legible, sin repetir "user" 6 veces
const { name: userName, email: userEmail, age: userAge, address: { city: userCity, street: userStreet, zipCode: userZip } } = user
```

## O-003: Operadores modernos (??, ?., ||=)

**[RECOMMENDED]** **Por qué:** `??` y `?.` distinguen "no existe" de "es falsy" (0, "", false), que es justo la distinción que `||` borra y que produce bugs sutiles con valores numéricos o booleanos legítimos en cero o falso.

```typescript
// ❌ 10 líneas para un valor por defecto
let userName
if (user.name !== null && user.name !== undefined) {
  userName = user.name
} else if (user.nickname !== null && user.nickname !== undefined) {
  userName = user.nickname
} else {
  userName = 'Anonymous'
}

// ✅ 1 línea, misma lógica
const userName = user.name ?? user.nickname ?? 'Anonymous'

// Optional chaining (evita crashes)
const city = user?.address?.city  // undefined si algo es null, sin error

// Asignación condicional
user.name ||= 'Anonymous'  // Solo asigna si name es falsy
```

## O-004: Map/Filter/Reduce en vez de bucles

**[RECOMMENDED]** **Por qué:** un `map` o `filter` declara la intención (transformar, seleccionar) sin exponer el mecanismo de iteración, lo que reduce el espacio de bugs (índices mal calculados, mutación accidental). Se desvía cuando el bucle necesita salir antes de tiempo o mantener estado complejo entre iteraciones, donde forzar un método funcional lo hace menos claro, no más.

```typescript
// ❌ 15 líneas, mutable, propenso a errores
const activeUsers = []
for (let i = 0; i < users.length; i++) {
  if (users[i].status === 'active') {
    activeUsers.push(users[i])
  }
}
const totalAge = 0
for (let i = 0; i < activeUsers.length; i++) {
  totalAge += activeUsers[i].age
}

// ✅ 3 líneas, inmutable, legible
const activeUsers = users.filter(u => u.status === 'active')
const totalAge = activeUsers.reduce((sum, u) => sum + u.age, 0)

// Combinado en una cadena:
const avgAge = users
  .filter(u => u.status === 'active')
  .map(u => u.age)
  .reduce((sum, age, _, arr) => sum + age / arr.length, 0)
```

## O-005: Pattern Matching con objetos (adiós switch-case)

**[RECOMMENDED]** **Por qué:** un `switch` sin `default` compila igual si se olvida un caso; un objeto de despacho falla de forma visible (`undefined`) o se puede tipar para que TypeScript exija exhaustividad. El error se mueve de "silencioso en producción" a "visible en desarrollo".

```typescript
// ❌ switch-case verboso
function getStatusColor(status: string) {
  switch (status) {
    case 'pending': return 'yellow'
    case 'paid': return 'green'
    case 'cancelled': return 'red'
    case 'refunded': return 'purple'
    default: return 'gray'
  }
}

// ✅ Objeto como mapa (más rápido, más corto)
const STATUS_COLORS: Record<string, string> = {
  pending: 'yellow',
  paid: 'green',
  cancelled: 'red',
  refunded: 'purple'
}
const getStatusColor = (status: string) => STATUS_COLORS[status] ?? 'gray'
```

## O-006: Funciones que se explican solas

**[RECOMMENDED]** **Por qué:** un nombre preciso es documentación que nunca se desactualiza, porque si se desactualiza el código deja de compilar contra sus propios usos. Un comentario sí puede quedar desincronizado del código que describe sin que nada lo señale.

```typescript
// ❌ Función larga, difícil de entender, imposible de testear
async function handleOrder(data: any) {
  // Validar
  if (!data.email || !data.email.includes('@')) throw new Error('Invalid email')
  if (!data.items || data.items.length === 0) throw new Error('No items')
  if (data.items.some(i => i.price < 0)) throw new Error('Negative price')
  
  // Calcular
  let total = 0
  let tax = 0
  for (const item of data.items) {
    total += item.price * item.quantity
    if (item.taxable) tax += item.price * item.quantity * 0.16
  }
  
  // Guardar
  const order = await db.orders.create({ total: total + tax, tax, items: data.items })
  
  // Notificar
  await emailService.send(data.email, 'Order created', `Total: ${total + tax}`)
  
  return order
}

// ✅ Funciones pequeñas, semánticas, testeables
const validateOrder = (data: OrderInput) => orderSchema.parse(data)
const calculateTotals = (items: Item[]) => items.reduce(
  (acc, item) => ({
    subtotal: acc.subtotal + item.price * item.quantity,
    tax: acc.tax + (item.taxable ? item.price * item.quantity * 0.16 : 0)
  }),
  { subtotal: 0, tax: 0 }
)
const createOrder = (data: OrderInput, totals: Totals) => db.orders.create({ ...data, ...totals })
const notifyUser = (email: string, total: number) => emailService.send(email, 'Order created', `Total: ${total}`)

async function handleOrder(data: OrderInput) {
  const validated = validateOrder(data)
  const totals = calculateTotals(validated.items)
  const order = await createOrder(validated, totals)
  await notifyUser(validated.email, totals.subtotal + totals.tax)
  return order
}
```

## O-007: Pipelines y composición

**[RECOMMENDED]** **Por qué:** una cadena de transformaciones nombradas se lee en el orden en que ocurre; el mismo cálculo anidado (`f(g(h(x)))`) se lee de adentro hacia afuera, al revés del orden de ejecución. Se desvía cuando solo hay uno o dos pasos, donde el pipeline añade indirección sin ganar claridad.

```typescript
// ❌ Variable intermedia para cada paso
const users = await fetchUsers()
const active = users.filter(u => u.active)
const adults = active.filter(u => u.age >= 18)
const emails = adults.map(u => u.email)

// ✅ Pipeline con pipe (una sola pasada)
const pipe = (...fns: Array<(v: unknown) => unknown>) => (x: unknown) => fns.reduce((v, f) => f(v), x)

const getActiveAdultEmails = pipe(
  fetchUsers,
  users => users.filter(u => u.active && u.age >= 18),
  users => users.map(u => u.email)
)

const emails = await getActiveAdultEmails()
```

---

# ⚡ PILAR 2: OPTIMIZACIÓN DE RECURSOS (O-008 a O-011)

## O-008: Memoización (no calcular dos veces)

**[RECOMMENDED]** **Por qué:** cachear el resultado de un cálculo puro evita repetirlo cuando las entradas no cambiaron, pero cada entrada cacheada consume memoria y con una función barata el coste del propio caché supera lo que ahorra. Se aplica donde se **midió** que el cálculo es costoso, no por defecto.

```typescript
// ❌ Recalcular en cada render
function ExpensiveComponent({ users }: Props) {
  const activeUsers = users.filter(u => u.status === 'active')
  const total = activeUsers.reduce((sum, u) => sum + u.total, 0)
  return <div>{total}</div>
}

// ✅ useMemo: solo recalcular cuando users cambia
function ExpensiveComponent({ users }: Props) {
  const { activeUsers, total } = useMemo(() => {
    const active = users.filter(u => u.status === 'active')
    return {
      activeUsers: active,
      total: active.reduce((sum, u) => sum + u.total, 0)
    }
  }, [users])
  
  return <div>{total}</div>
}

// Patrón avanzado: memoización con TTL (cache con expiración)
function memoizeWithTTL<A extends unknown[], T>(fn: (...args: A) => T, ttlMs = 60000) {
  const cache = new Map<string, { value: T; timestamp: number }>()
  
  return (...args: A) => {
    const key = JSON.stringify(args)
    const cached = cache.get(key)
    
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return cached.value
    }
    
    const value = fn(...args)
    cache.set(key, { value, timestamp: Date.now() })
    return value
  }
}
```

## O-009: Lazy Loading (cargar solo lo necesario)

**[RECOMMENDED]** **Por qué:** cargar un módulo o una relación antes de que se necesite consume tiempo y memoria que compiten con lo que el usuario sí está esperando ver. Se desvía en lo que forma parte de la ruta crítica de carga inicial (`FRONTEND_PERFORMANCE_STANDARD.md`: nunca `loading="lazy"` en el elemento LCP).

```typescript
// ❌ Cargar TODO el objeto (100KB)
const order = await db.query('SELECT * FROM orders WHERE id = $1', [orderId])
console.log(order.userEmail)  // Solo necesitamos el email

// ✅ Solo las columnas necesarias (1KB)
const { email } = await db.query(
  'SELECT email FROM orders WHERE id = $1',
  [orderId]
)

// ❌ Eager loading de relaciones
const user = await db.users.findUnique({
  where: { id: userId },
  include: { orders: true, invoices: true, settings: true }  // 1MB
})

// ✅ Lazy loading (solo cuando se necesita)
const user = await db.users.findUnique({ where: { id: userId } })  // 10KB
// Más tarde, si necesita órdenes:
const orders = await db.orders.findMany({ where: { userId } })
```

## O-010: Debounce y Throttle (no saturar)

**[RECOMMENDED]** **Por qué:** un input de búsqueda que dispara una petición por tecla satura la red y la API con peticiones que el usuario ni siquiera terminó de escribir. Se aplica a eventos de alta frecuencia disparados por el usuario (búsqueda, scroll, resize); no a acciones discretas como un clic.

```typescript
// ❌ Cada tecla dispara una query (100 queries = 100 lecturas)
function SearchBox() {
  const [query, setQuery] = useState('')
  
  useEffect(() => {
    fetchResults(query)  // 'a', 'ap', 'app', 'appl', 'apple'
  }, [query])
}

// ✅ Debounce: esperar 300ms después de la última tecla (1 query)
import { useDebouncedCallback } from 'use-debounce'

function SearchBox() {
  const [query, setQuery] = useState('')
  
  const debouncedSearch = useDebouncedCallback(
    (value: string) => fetchResults(value),
    300  // Solo busca 300ms después de dejar de escribir
  )
  
  return <input onChange={e => { setQuery(e.target.value); debouncedSearch(e.target.value) }} />
}
```

## O-011: Virtualización (renderizar solo lo visible)

**[RECOMMENDED]** **Por qué:** renderizar mil filas cuando solo veinte caben en pantalla gasta tiempo de layout y memoria en DOM que el usuario nunca ve. Se activa a partir de listas grandes (`FRONTEND_TABLE_PATTERNS.md`: >100 ítems); por debajo de ese umbral, virtualizar añade complejidad que el rendimiento no necesita.

```typescript
// ❌ 10,000 filas en el DOM = browser muerto
function Table({ data }: { data: Row[] }) {
  return data.map(row => <RowComponent key={row.id} data={row} />)
}

// ✅ Solo 20 filas visibles en el viewport
import { useVirtualizer } from '@tanstack/react-virtual'

function VirtualTable({ data }: { data: Row[] }) {
  const parentRef = useRef<HTMLDivElement>(null)
  
  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,  // Altura estimada de cada fila
    overscan: 5  // Renderizar 5 filas extra arriba/abajo
  })
  
  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div key={virtualRow.key} style={{ transform: `translateY(${virtualRow.start}px)` }}>
            <RowComponent data={data[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

# 💰 PILAR 3: OPTIMIZACIÓN POR COSTO (D1, Workers, R2) (O-012 a O-019)

## O-012: D1 - Cada fila leída CUESTA DINERO

**[REQUIRED]** **Por qué:** a diferencia de una base de datos con capacidad reservada, D1 factura por fila efectivamente leída: una consulta sin filtrar que escanea toda la tabla no es solo lenta, es una línea en la factura que crece con el tamaño de los datos. Diseñar la consulta para leer lo mínimo no es una optimización opcional, es lo que mantiene el coste predecible.

```sql
-- ❌ Escaneo completo de tabla = 50,000 filas leídas = $$$$
SELECT * FROM orders WHERE user_id = 'user_123'

-- ✅ Índice + columnas específicas = 5 filas leídas
CREATE INDEX idx_orders_user_id ON orders(user_id);

SELECT id, status, total_cents, created_at
FROM orders
WHERE user_id = 'user_123'
LIMIT 20;

-- ❌ JOIN sin índice = producto cartesiano
SELECT o.*, u.email
FROM orders o
JOIN users u ON o.user_id = u.id
-- Escanea: orders (50K) × users (10K) = 500M operaciones

-- ✅ JOIN con índice = solo las filas necesarias
CREATE INDEX idx_orders_user_id ON orders(user_id);
-- Escanea: 50 filas de orders + 50 lookups indexados en users = 100 operaciones
```

## O-013: D1 - Contar sin contar (evitar COUNT(*))

**[RECOMMENDED]** **Por qué:** `COUNT(*)` sobre una tabla grande escanea todas las filas para producir un solo número, y ese coste crece con el tamaño de la tabla en vez de mantenerse constante. Se desvía en tablas pequeñas o de bajo tráfico, donde el escaneo es barato y una tabla de contadores añadiría complejidad sin necesidad.

```sql
-- ❌ COUNT(*) en tabla gigante = escaneo completo
SELECT COUNT(*) FROM events WHERE user_id = 'user_123';
-- Lee 1 millón de filas aunque solo devuelva "1,000,000"

-- ✅ Mantener contadores en otra tabla
CREATE TABLE event_counts (
  user_id UUID PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0
);

-- Incrementar al insertar (EN LA MISMA TRANSACCIÓN)
BEGIN;
  INSERT INTO events (user_id, type, payload) VALUES ('user_123', 'login', '{}');
  UPDATE event_counts SET count = count + 1 WHERE user_id = 'user_123';
COMMIT;

-- Leer contador = 1 fila leída en vez de 1 millón
SELECT count FROM event_counts WHERE user_id = 'user_123';
```

## O-014: D1 - Paginación con cursores (nunca OFFSET)

**[REQUIRED]** **Por qué:** la misma razón que `DB-017`: `OFFSET` obliga a leer y descartar todas las filas anteriores a la página pedida, así que su coste crece con el número de página — y en D1 ese coste además se factura por fila leída (`O-012`), duplicando la penalización.

```sql
-- ❌ OFFSET escanea todas las filas anteriores
SELECT * FROM orders WHERE user_id = 'user_123' ORDER BY created_at DESC LIMIT 20 OFFSET 10000;
-- Lee 10,020 filas, descarta 10,000

-- ✅ Cursor va directo al punto
SELECT id, status, total_cents, created_at FROM orders 
WHERE user_id = 'user_123' 
  AND created_at < '2024-03-15T10:30:00Z'  -- Último cursor
ORDER BY created_at DESC 
LIMIT 20;
-- Lee exactamente 20 filas con índice
```

## O-015: Workers - Reducir tiempo de CPU (cuesta $)

**[RECOMMENDED]** **Por qué:** Cloudflare factura el tiempo de CPU del Worker, así que un cálculo ineficiente no solo es más lento, es más caro en cada invocación. Se prioriza donde el perfilado (`O-034`) muestra el cuello real; optimizar a ciegas cambia código simple por código rápido sin garantía de que el punto optimizado fuera el costoso.

```typescript
// ❌ Procesar todo en el worker (CPU time caro)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const data = await request.json()
    
    // Procesar imagen en el worker (20 segundos de CPU = CARO)
    const processed = await sharp(data.image).resize(800, 600).toBuffer()
    
    return new Response(processed)
  }
}

// ✅ Delegar trabajo pesado a servicios externos
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const data = await request.json()
    
    // Opción 1: Usar Cloudflare Images (servicio nativo, barato)
    const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${env.ACCOUNT_ID}/images/v1`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${env.CF_API_TOKEN}` },
      body: data.image
    })
    
    // Opción 2: Encolar trabajo pesado
    await env.QUEUE.send({ type: 'process_image', image: data.image })
    
    return Response.json({ status: 'processing' })
  }
}
```

## O-016: R2 - Streaming vs Buffer

**[REQUIRED]** **Por qué:** cargar un archivo completo en memoria antes de subirlo o servirlo hace que el consumo de memoria del Worker dependa del tamaño del archivo — y el límite de memoria del Worker es duro (`O-033`): superarlo no degrada, mata la petición. El streaming mantiene el consumo constante sin importar cuán grande sea el archivo.

```typescript
// ❌ Cargar archivo completo en memoria (128MB límite)
async function uploadFile(request: Request, env: Env) {
  const buffer = await request.arrayBuffer()  // Si es 200MB = CRASH
  
  await env.BUCKET.put('file.pdf', buffer)
}

// ✅ Streaming (sin límite de tamaño)
async function uploadFile(request: Request, env: Env) {
  if (!request.body) throw new Error('No body')
  
  await env.BUCKET.put('file.pdf', request.body)  // Stream directo
}

// ❌ Descargar archivo completo para leer metadatos
async function getMetadata(key: string, env: Env) {
  const object = await env.BUCKET.get(key)
  const buffer = await object.arrayBuffer()  // 500MB en memoria
  // Leer solo los primeros 100 bytes
  const metadata = buffer.slice(0, 100)
}

// ✅ Leer solo lo necesario con Range
async function getMetadata(key: string, env: Env) {
  const object = await env.BUCKET.get(key, {
    range: { offset: 0, length: 100 }  // Solo 100 bytes
  })
  return await object.arrayBuffer()  // Solo 100 bytes en memoria
}
```

## O-017: Caché agresiva (leer menos = costar menos)

**[RECOMMENDED]** **Por qué:** servir desde KV o caché evita repetir una consulta a D1 que ya se resolvió hace segundos, y cada consulta evitada es tanto más rápida para el usuario como más barata (`O-012`). Se desvía en datos que cambian por petición o donde la frescura es más importante que la velocidad.

```typescript
// ❌ Consultar DB por cada request
async function getProposals(userId: string) {
  return db.query('SELECT * FROM proposals WHERE user_id = $1', [userId])
}

// ✅ Cache en Workers KV para lecturas frecuentes
async function getProposals(userId: string, env: Env) {
  const cacheKey = `proposals:${userId}`
  
  // 1. Intentar cache
  const cached = await env.KV.get(cacheKey, 'json')
  if (cached) return cached
  
  // 2. Consultar DB
  const proposals = await db.query('SELECT id, title, status, created_at FROM proposals WHERE user_id = $1', [userId])
  
  // 3. Guardar en cache (TTL 5 minutos)
  await env.KV.put(cacheKey, JSON.stringify(proposals), { expirationTtl: 300 })
  
  return proposals
}

// Cache con stale-while-revalidate
async function getWithSWR(key: string, env: Env) {
  const cached = await env.KV.get(key, 'json')
  
  if (cached) {
    // Devolver cache inmediatamente
    // Refrescar en background
    fetch('/api/refresh-cache', { method: 'POST', body: JSON.stringify({ key }) })
    return cached
  }
  
  // Sin cache, consultar y guardar
  const fresh = await fetchFreshData(key)
  await env.KV.put(key, JSON.stringify(fresh), { expirationTtl: 300 })
  return fresh
}
```

## O-018: Batch Operations (agrupar queries)

**[RECOMMENDED]** **Por qué:** el problema N+1 —una consulta principal más una por cada resultado— convierte una operación de un viaje de red en decenas, y cada viaje añade latencia que se acumula. Agrupar en una sola consulta con `WHERE IN` o un `JOIN` mantiene la latencia constante sin importar cuántos resultados haya.

```typescript
// ❌ N+1 queries (1 query principal + N queries por cada resultado)
const orders = await db.query('SELECT * FROM orders WHERE user_id = $1', [userId])
for (const order of orders) {
  order.items = await db.query('SELECT * FROM order_items WHERE order_id = $1', [order.id])
}
// 101 queries para 100 órdenes

// ✅ JOIN o batch query
// Opción 1: JOIN
const orders = await db.query(`
  SELECT o.*, json_agg(oi.*) as items
  FROM orders o
  LEFT JOIN order_items oi ON o.id = oi.order_id
  WHERE o.user_id = $1
  GROUP BY o.id
`, [userId])
// 1 query

// Opción 2: Batch (WHERE IN)
const orders = await db.query('SELECT id, status, total_cents, created_at FROM orders WHERE user_id = $1', [userId])
const orderIds = orders.map(o => o.id)
const items = await db.query(
  'SELECT id, order_id, product_id, qty, unit_price_cents FROM order_items WHERE order_id = ANY($1)',
  [orderIds]
)
// 2 queries en vez de 101
```

## O-019: Compresión y minificación

**[RECOMMENDED]** **Por qué:** el tamaño del bundle se paga en cada carga inicial y en cada cold start (`O-037`), y en su mayoría es trabajo mecánico que el build ya automatiza. Se convierte en algo a vigilar activamente solo cuando una dependencia nueva lo dispara sin que nadie lo note.

```typescript
// ❌ Respuesta JSON sin comprimir (100KB)
return Response.json(data)

// ✅ Compresión automática (Cloudflare lo hace, pero asegúrate)
return Response.json(data, {
  headers: {
    'Content-Encoding': 'gzip',  // 100KB → 20KB
    'Cache-Control': 'public, max-age=300'
  }
})
```

---

# 🧠 PARTE 4: CÓDIGO CORTO AVANZADO (O-020 a O-025)

## O-020: Pattern Matching con Either/Result (Adiós try-catch)

**[RECOMMENDED]** **Por qué:** un `try-catch` no aparece en la firma de la función, así que quien la llama no sabe que puede fallar hasta que lo hace en producción. `Either`/`Result` convierte el posible error en parte del tipo de retorno, y TypeScript obliga a manejarlo antes de compilar. Se desvía en errores realmente excepcionales (fallos del runtime), donde una excepción sigue siendo el mecanismo correcto.

```typescript
// ❌ Try-catch anidados, código defensivo, ILEGIBLE
async function createOrder(data: any) {
  try {
    const validated = validateOrder(data)
    try {
      const order = await db.orders.create(validated)
      try {
        await emailService.send(validated.email, 'Order created')
        return { success: true, order }
      } catch (emailError) {
        await db.orders.delete(order.id)
        return { success: false, error: 'Email failed, order rolled back' }
      }
    } catch (dbError) {
      return { success: false, error: 'Database error' }
    }
  } catch (validationError) {
    return { success: false, error: 'Validation error' }
  }
}

// ✅ Either Monad - Flujo limpio, sin try-catch anidados

// 1. Definir tipos Either
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E }

const success = <T>(data: T): Result<T> => ({ success: true, data })
const failure = <E>(error: E): Result<never, E> => ({ success: false, error })

// 2. Encadenar operaciones con flatMap
function flatMap<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => Result<U, E>
): Result<U, E> {
  return result.success ? fn(result.data) : result
}

// 3. Pipeline limpio
async function createOrder(data: unknown): Promise<Result<Order>> {
  const validated = validateOrder(data)
  if (!validated.success) return validated
  
  const order = await db.orders.create(validated.data)
  if (!order.success) return order
  
  await emailService.send(validated.data.email, 'Order created')
  return order
}

// Uso:
const result = await createOrder(inputData)
if (result.success) {
  console.log('Orden creada:', result.data)
} else {
  console.error('Error:', result.error)
}
```

## O-021: Pipe y Flow (Programación Funcional de verdad)

**[RECOMMENDED]** **Por qué:** igual que `O-007`, encadenar transformaciones puras en el orden en que ocurren se lee de forma lineal; forzar `pipe` sobre una lógica que ya es lineal con dos pasos solo añade una capa de indirección.

```typescript
// ❌ Variables intermedias, difícil de seguir
async function processOrderFlow(input: unknown) {
  const step1 = validateOrder(input)
  if (step1.error) return step1
  
  const step2 = await enrichOrder(step1.data)
  if (step2.error) return step2
  
  const step3 = await calculateTaxes(step2.data)
  if (step3.error) return step3
  
  const step4 = await saveOrder(step3.data)
  return step4
}

// ✅ Pipe: composición funcional pura
type AsyncResult<T> = Promise<Result<T>>

function pipe<T1, T2, T3, T4>(
  fn1: (input: T1) => AsyncResult<T2>,
  fn2: (input: T2) => AsyncResult<T3>,
  fn3: (input: T3) => AsyncResult<T4>,
) {
  return async (input: T1): AsyncResult<T4> => {
    const r1 = await fn1(input)
    if (!r1.success) return r1
    
    const r2 = await fn2(r1.data)
    if (!r2.success) return r2
    
    return fn3(r2.data)
  }
}

// Uso: una línea, semántico, sin variables intermedias
const processOrder = pipe(validateOrder, enrichOrder, calculateTaxes)

// O con operador custom:
const result = await pipe(
  validateOrder,
  enrichOrder,
  calculateTaxes,
  saveOrder
)(inputData)
```

## O-022: Pattern Matching con ts-pattern

**[RECOMMENDED]** **Por qué:** sobre tipos unión discriminados, `ts-pattern` exige exhaustividad verificada por el compilador: añadir un caso nuevo al tipo y olvidar manejarlo se convierte en un error de compilación, no en un `undefined` en producción. Se reserva para lógica de ramificación real; una condición simple no lo necesita.

```typescript
import { match, P } from 'ts-pattern'

// ❌ Switch-case con bugs sutiles
function handlePayment(payment: Payment) {
  switch (payment.status) {
    case 'pending':
      return processPayment(payment)
    case 'completed':
      return sendReceipt(payment)
    case 'failed':
      return retryPayment(payment)
    // Si alguien agrega 'refunded', esto falla sin warning
    default:
      throw new Error(`Unknown status: ${payment.status}`)
  }
}

// ✅ Pattern matching exhaustivo (TypeScript obliga a cubrir todos los casos)
const handlePayment = (payment: Payment) =>
  match(payment)
    .with({ status: 'pending' }, p => processPayment(p))
    .with({ status: 'completed' }, p => sendReceipt(p))
    .with({ status: 'failed', attempts: P.when(n => n < 3) }, p => retryPayment(p))
    .with({ status: 'failed', attempts: 3 }, p => markAsLost(p))
    .with({ status: 'refunded' }, p => processRefund(p))
    .exhaustive()  // Error de compilación si falta algún caso

// Pattern matching con datos anidados
const handleEvent = (event: AppEvent) =>
  match(event)
    .with({ type: 'user_created' }, e => createWelcomeEmail(e.user))
    .with({ type: 'order_paid', order: { total: P.when(t => t > 1000) } }, e => 
      flagForReview(e.order)  // Órdenes > $1000 se revisan
    )
    .with({ type: 'order_paid' }, e => processNormalOrder(e.order))
    .with({ type: 'subscription_cancelled' }, e => scheduleWinback(e.user))
    .with({ type: P.union('api_error', 'timeout') }, e => alertOnCall(e))
    .exhaustive()
```

## O-023: Railway Oriented Programming (Errores como valores)

**[RECOMMENDED]** **Por qué:** encadenar pasos que pueden fallar sin que el error interrumpa el flujo de control hace explícito, en cada paso, qué ocurre si algo salió mal antes. Es la misma familia de `O-020`; se aplica donde hay una secuencia real de pasos falibles, no a una sola operación que puede fallar.

```typescript
// ❌ Excepciones para flujo de control (COSTOSO en CPU)
function divide(a: number, b: number): number {
  if (b === 0) throw new Error('Division by zero')
  return a / b
}

// ✅ Result Type: errores son valores, no excepciones
type Result<T, E = string> = 
  | { ok: true; value: T }
  | { ok: false; error: E }

const Ok = <T>(value: T): Result<T> => ({ ok: true, value })
const Err = <E>(error: E): Result<never, E> => ({ ok: false, error })

// Operaciones matemáticas seguras (sin exceptions)
const safeDivide = (a: number, b: number): Result<number> =>
  b === 0 ? Err('Division by zero') : Ok(a / b)

const safeSqrt = (n: number): Result<number> =>
  n < 0 ? Err('Cannot sqrt negative') : Ok(Math.sqrt(n))

// Composición de operaciones que pueden fallar
function calculateHypotenuse(a: number, b: number): Result<number> {
  const a2 = Ok(a * a)
  const b2 = Ok(b * b)
  
  if (!a2.ok || !b2.ok) return Err('Invalid input')
  
  const sum = a2.value + b2.value
  return safeSqrt(sum)
}

// Encadenar con bind (flatMap para Result)
function bind<T, U, E>(result: Result<T, E>, fn: (value: T) => Result<U, E>): Result<U, E> {
  return result.ok ? fn(result.value) : result
}

const result = bind(
  safeDivide(10, 2),
  quotient => bind(
    safeSqrt(quotient),
    sqrt => Ok(Math.round(sqrt))
  )
)
// { ok: true, value: 2 }
```

## O-024: Tagged Unions Discriminadas (TypeScript avanzado)

**[RECOMMENDED]** **Por qué:** una unión con un campo discriminante (`type: "a" | "b"`) permite que TypeScript reduzca el tipo automáticamente dentro de cada rama, sin *type assertions* ni comprobaciones manuales de qué campos existen. Es la base sobre la que `ts-pattern` (`O-022`) puede garantizar exhaustividad.

```typescript
// ❌ Strings mágicos + campos opcionales (imposible de tipar bien)
interface Order {
  status: string
  paidAt?: Date
  refundedAt?: Date
  cancelledAt?: Date
  cancelReason?: string
  refundAmount?: number
}

// ✅ Discriminated Union (TypeScript sabe qué campos existen en cada estado)
type Order = 
  | { status: 'draft' }
  | { status: 'pending_payment'; paymentUrl: string }
  | { status: 'paid'; paidAt: Date; transactionId: string }
  | { status: 'shipped'; paidAt: Date; shippedAt: Date; trackingNumber: string }
  | { status: 'delivered'; paidAt: Date; shippedAt: Date; deliveredAt: Date }
  | { status: 'cancelled'; cancelledAt: Date; reason: string }
  | { status: 'refunded'; paidAt: Date; refundedAt: Date; amount: number }

// TypeScript AUTOMÁTICAMENTE sabe qué campos existen
function getOrderSummary(order: Order): string {
  switch (order.status) {
    case 'draft':
      return 'Borrador sin pagar'
    case 'pending_payment':
      return `Pagar en: ${order.paymentUrl}`  // TypeScript sabe que paymentUrl existe
    case 'paid':
      return `Pagado el ${order.paidAt.toISOString()}`  // Sabe que paidAt existe
    case 'shipped':
      return `Enviado: ${order.trackingNumber}`  // Sabe que trackingNumber existe
    // TypeScript ERROR si olvidas un caso
  }
}
```

## O-025: Builder Pattern Tipado (Objetos complejos sin caos)

**[RECOMMENDED]** **Por qué:** un objeto con muchos campos opcionales construido a mano es fácil de crear en un estado inválido o incompleto. El builder tipado no compila hasta que los campos obligatorios están presentes, moviendo el error de tiempo de ejecución a tiempo de compilación. Se desvía en objetos con pocos campos, donde el builder añade ceremonia sin necesidad.

```typescript
// ❌ Constructor con 15 parámetros
const email = new Email(
  'user@email.com', 'Admin', 'Welcome', '<h1>Hi</h1>',
  undefined, undefined, true, 'high', undefined, undefined,
  'welcome-template', undefined, 'support@company.com', undefined, true
)

// ✅ Builder Pattern con tipos
class EmailBuilder {
  private email: Partial<Email> = {}
  
  to(address: string): this {
    this.email.to = address
    return this
  }
  
  from(name: string, address?: string): this {
    this.email.fromName = name
    this.email.fromAddress = address || 'noreply@company.com'
    return this
  }
  
  subject(text: string): this {
    this.email.subject = text
    return this
  }
  
  body(html: string): this {
    this.email.html = html
    return this
  }
  
  template(name: string, data?: Record<string, any>): this {
    this.email.template = name
    this.email.templateData = data
    return this
  }
  
  priority(level: 'high' | 'normal' | 'low'): this {
    this.email.priority = level
    return this
  }
  
  trackOpens(): this {
    this.email.trackOpens = true
    return this
  }
  
  build(): Email {
    if (!this.email.to) throw new Error('Email "to" is required')
    if (!this.email.subject) throw new Error('Subject is required')
    return this.email as Email
  }
}

// Uso: se lee como una historia
const email = new EmailBuilder()
  .to('user@email.com')
  .from('Admin Team')
  .subject('Welcome aboard!')
  .template('welcome', { name: 'User', plan: 'Pro' })
  .priority('high')
  .trackOpens()
  .build()
```

---

# 🗄️ PARTE 5: OPTIMIZACIÓN D1 (O-026 a O-031)
*Nota: Para detalles a profundidad de D1, consulta `04_Database/D1_OPTIMIZATION.md`.*

- **O-026**: Índices Parciales (Indexa solo lo que consultas usando `WHERE`).
- **O-027**: Índices Compuestos Estratégicos (Igualdad > Rango > Orden).
- **O-028**: Vistas Materializadas (Resultados pre-calculados para dashboards).
- **O-029**: WAL (Write-Ahead Log) y Performance (Transacciones en batch).
- **O-030**: Evitar Escrituras Fantasma (`UPDATE ... WHERE email IS DISTINCT FROM`).
- **O-031**: D1 + DO (Durable Objects) para hotspots (Visitas, likes).

---

# ⚡ PARTE 6: OPTIMIZACIÓN WORKERS (O-032 a O-037)
*Nota: Para detalles a profundidad de Workers, consulta `08_Cloud/WORKERS_OPTIMIZATION.md`.*

- **O-032**: Eliminar Cold Starts (CRON pings o tráfico natural).
- **O-033**: Memory Management (LRUCache con límite, no `Map` infinito).
- **O-034**: CPU Profiling (`performance.now()` en operaciones pesadas).
- **O-035**: Web Streams (`TransformStream`, procesar sin cargar en memoria).
- **O-036**: Service Bindings vs HTTP (Comunicación interna directa).
- **O-037**: Análisis de Bundle Size (Tree-shaking, minificación).

---

## 📊 TABLA DE IMPACTO DE OPTIMIZACIONES

| Técnica | Antes | Después | Ahorro |
|---------|-------|---------|--------|
| Early returns | 30 líneas | 15 líneas | 50% código |
| Either Monad | 4 try-catch | 1 pipeline | 75% nesting |
| Virtualización | 10K DOM nodes | 20 DOM nodes | 99.8% memoria |
| Índice parcial | 1M filas indexadas | 100K indexadas | 90% espacio |
| Vista materializada | 500ms query | 2ms query | 99.6% tiempo |
| Service Binding | 50ms latencia | 1ms latencia | 98% latencia |
| Streaming | 50MB memoria | 1KB memoria | 99.998% RAM |
| Debounce | 100 queries | 1 query | 99% lecturas D1 |
| Batch writes | 1000 writes | 1 write | 99.9% WAL |

---

## 🧪 CHECKLIST DE OPTIMIZACIÓN TOTAL

```markdown
## AUDITORÍA PRE-DEPLOY

### Código
- [ ] ¿Funciones < 20 líneas?
- [ ] ¿Early returns en vez de if-else anidados?
- [ ] ¿Either/Result en vez de excepciones (try-catch costosos)?
- [ ] ¿Pattern matching exhaustivo (ts-pattern)?
- [ ] ¿Sin variables intermedias innecesarias?

### Recursos (Memoria y UI)
- [ ] ¿Streaming (no arrayBuffer) para cargas/descargas grandes?
- [ ] ¿Debounce en inputs de búsqueda?
- [ ] ¿Virtualización para listas > 100 items?
- [ ] ¿Lazy loading de módulos/relaciones DB?

### D1 (Database y Costos)
- [ ] ¿Índices parciales (WHERE clause) donde aplique?
- [ ] ¿Índices compuestos en orden correcto (Igualdad -> Rango)?
- [ ] ¿Vistas materializadas para dashboards complejos?
- [ ] ¿COUNT evitado con tablas de contadores?
- [ ] ¿Batch writes (transacciones) en lugar de inserciones cíclicas?
- [ ] ¿UPDATE solo si el valor cambió (IS DISTINCT FROM)?

### Workers (CPU y Red)
- [ ] ¿CRON configurado para mantener warm (evitar cold starts)?
- [ ] ¿Caché LRU en memoria con límite estricto?
- [ ] ¿Profiling (`performance.now`) usado en desarrollo?
- [ ] ¿Service Bindings para peticiones internas en lugar de HTTP?
- [ ] ¿Bundle minimizado a < 500KB (Tree-shaking de dependencias grandes)?
```
