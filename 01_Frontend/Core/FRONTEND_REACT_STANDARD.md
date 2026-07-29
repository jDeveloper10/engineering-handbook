---
title: "FRONTEND REACT STANDARD"
category: frontend
tags:
  - react
  - typescript
  - components
  - forms
  - performance
  - standards
summary: "Nivel 2 del dominio Frontend. Define cómo se escribe React en concreto: estructura de carpetas por feature, composición sobre configuración, custom hooks, useEffect como último recurso, Context, matriz de estado, data fetching con TanStack Query, Suspense/lazy, performance y APIs de React 19."
keywords:
  - hooks
  - tanstack-query
  - context-api
  - suspense
  - error-boundaries
  - code-splitting
  - jsx
updated: 2026-07-26
status: current
---

# FRONTEND REACT STANDARD

> Nivel 2 del handbook. Depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Regla de herencia: **nada de lo que el Nivel 1 ya regula se repite aquí** — cuando una regla de este documento se apoya en una del Nivel 1, se declara "hereda de Frontend §X" y solo se agrega la profundización.
>
> Alcance: cómo se escribe React en concreto — estructura interna de features, hooks, efectos, Context, estado, data fetching, Suspense, performance y APIs de React 19. El contrato con los Workers (envelope, `error.code`s, schemas compartidos) lo define [03_API/API_ENGINEERING_STANDARD.md](../../03_API/API_ENGINEERING_STANDARD.md); los estados visuales de loading/empty/error los define [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md). Los tipos se rigen por [FRONTEND_TYPESCRIPT_STANDARD.md](FRONTEND_TYPESCRIPT_STANDARD.md).
>
> Stack de referencia: React 19 + Vite + TypeScript estricto + Tailwind, SPA con React Router, data fetching contra Cloudflare Workers.

---

## 01. Estructura de carpetas por feature

### 1.1 Estructura interna estándar de un feature

**[REQUIRED]** La organización por feature (no por tipo) **hereda de Frontend §2.1**; los barrels controlados **heredan de Frontend §3.3**. Lo que este documento agrega es la estructura *interna* obligatoria de cada feature:

```
REGLA (agnóstica): cada unidad de negocio agrupa su UI, su lógica reusable,
su acceso a datos y sus tipos en subcarpetas fijas con nombres fijos.
No se inventan subcarpetas nuevas por proyecto.

IMPLEMENTACIÓN (React + Vite):
src/
├── app/                    # composición de la app: router, providers, layout raíz
│   ├── routes/             # definición de rutas (hereda de Frontend §8.1)
│   └── providers/          # QueryClientProvider, ThemeProvider, AuthProvider
├── features/
│   └── orders/
│       ├── components/     # componentes exclusivos del feature
│       ├── hooks/          # custom hooks del feature (useOrders, useOrderFilters)
│       ├── api/            # funciones de acceso a datos (ver sección 07)
│       ├── types.ts        # tipos propios del feature (los del contrato NO viven aquí, ver TS §03)
│       └── index.ts        # única API pública (hereda de Frontend §3.3)
├── shared/                 # componentes/hooks usados por 2+ features (hereda de Frontend §4.6)
│   ├── components/
│   ├── hooks/
│   └── lib/                # apiClient, env, utilidades puras
└── main.tsx
```

**Por qué esto es crítico cuando el código lo genera una IA:** una IA no "recuerda" el proyecto entre sesiones — decide dónde poner cada archivo a partir del patrón que ve. Si la estructura es predecible (todo hook de datos de orders vive en `features/orders/hooks/`), la IA coloca el archivo nuevo en el único lugar posible y encuentra el existente sin buscar. Si cada feature inventa su propia estructura, cada generación nueva improvisa una distinta y el repo diverge en semanas. La predictibilidad de la estructura es la memoria externa de la IA.

### 1.2 Tabla de decisión: dónde va cada archivo

**[REQUIRED]** Ante la duda, se resuelve con esta tabla — no se crea una carpeta nueva:

| Archivo nuevo | Va en |
|---|---|
| Componente usado solo por el feature X | `features/x/components/` |
| Componente usado por 2+ features | `shared/components/` (hereda de Frontend §4.6) |
| Hook con lógica de UI del feature X | `features/x/hooks/` |
| Función que llama a un endpoint del feature X | `features/x/api/` |
| Tipo derivado del contrato compartido | se importa de `shared/contracts/` — no se crea archivo |
| Tipo puramente de UI del feature X | `features/x/types.ts` |
| Página/ruta | componente en `features/x/components/`, registro en `app/routes/` |
| Provider global (tema, auth, query client) | `app/providers/` |
| Utilidad pura sin dominio (formatDate) | `shared/lib/` |

**[REQUIRED]** Un feature **no importa internals de otro feature** (hereda de Frontend §2.2 y §3.3): solo lo que el otro exporta en su `index.ts`. Si dos features necesitan lo mismo, eso sube a `shared/`.

---

## 02. Composición sobre configuración

**Hereda de Frontend §4.5** (composición preferida sobre props booleanas) y **§4.4** (máximo ~7 props). Este documento agrega el criterio operativo y el patrón concreto:

### 2.1 Señal de alarma: 3+ props booleanas de variante

**[REQUIRED]** Cuando un componente acumula **3 o más props booleanas que activan variantes visuales o de estructura** (`showHeader`, `compact`, `withIcon`...), se detiene y se repiensa antes de agregar la cuarta. Las salidas, en orden de preferencia:

1. **`children`** — si la variación es "qué contenido va adentro", el padre lo pasa como contenido, no como flag.
2. **Compound components** — si la variación es "qué secciones existen y en qué orden".
3. **Union discriminada de variantes** — si las variantes son mutuamente excluyentes (ver [FRONTEND_TYPESCRIPT_STANDARD.md](FRONTEND_TYPESCRIPT_STANDARD.md) §04).

**Por qué 3 es el umbral:** 3 booleanas independientes ya son 8 combinaciones posibles, la mayoría nunca diseñadas ni testeadas. Cada flag nueva duplica el espacio de estados. Una IA que recibe un componente con flags tiende a agregar "una flag más" porque es el cambio local más barato — esta regla la obliga a pagar el costo de recomponer antes de que el componente sea irrecuperable.

### 2.2 Compound components: el patrón de referencia

**[RECOMMENDED]** Implementación con propiedades estáticas sobre el componente padre; el padre define el layout, los hijos se declaran donde se usan:

```tsx
// features/orders/components/OrderCard.tsx
function OrderCard({ children }: { children: React.ReactNode }) {
  return <article className="rounded-lg border p-4">{children}</article>;
}
OrderCard.Header = function Header({ children }: { children: React.ReactNode }) {
  return <header className="mb-2 font-medium">{children}</header>;
};
OrderCard.Actions = function Actions({ children }: { children: React.ReactNode }) {
  return <footer className="mt-4 flex justify-end gap-2">{children}</footer>;
};

// Uso: el consumidor compone; no hay showHeader / showActions / compact
<OrderCard>
  <OrderCard.Header>Orden #{order.id}</OrderCard.Header>
  <p>{order.summary}</p>
  <OrderCard.Actions><Button>Ver detalle</Button></OrderCard.Actions>
</OrderCard>
```

**[RECOMMENDED]** Si los sub-componentes necesitan compartir estado implícito (ej. `Tabs`/`Tabs.Panel`), ese estado viaja por un Context **interno y privado del componente**, nunca por props que el consumidor deba cablear. Esto no viola la sección 05: es Context de alcance local, no de aplicación.

---

## 03. Custom hooks

El naming `use*` en camelCase **hereda de Frontend §3.1**; la separación UI/lógica **hereda de Frontend §4.3**. Este documento agrega cuándo extraer y cómo diseñar el hook:

### 3.1 Cuándo extraer un custom hook

**[REQUIRED]** Se extrae un custom hook cuando se cumple al menos una:

1. La lógica con estado se **usa en 2+ componentes** (misma regla de reutilización que Frontend §4.6 aplicada a lógica).
2. La lógica **merece testearse aislada** de la UI (cálculos con estado, máquinas de estado de un flujo, debounce/polling), aunque hoy se use una sola vez.

**[RECOMMENDED]** No se extrae "por si acaso" lógica trivial de un solo `useState` usada una vez — un hook prematuro es la versión con estado del componente subido a `shared/` por si acaso (mismo porqué que Frontend §4.6).

### 3.2 Un hook = una responsabilidad

**[REQUIRED]** Un hook hace una cosa nombrable en su propio nombre: `useOrders` obtiene órdenes; `useOrderFilters` maneja filtros; `useDebounce` hace debounce. Un hook que obtiene datos **y** maneja el formulario de filtros **y** sincroniza la URL son tres hooks compuestos por el componente, no uno.

**Por qué:** un hook multipropósito no se puede reusar parcialmente (quien quiere solo los filtros carga también el fetching) y su test necesita montar todo. Además, para una IA el nombre del hook es el contrato: si `useOrders` hace tres cosas, la IA que lo consume no puede predecir sus efectos sin leer la implementación.

**[RECOMMENDED]** Forma de retorno: para 1-2 valores, tupla (`[value, setValue]`, estilo `useState`); para 3+, objeto con nombres (`{ data, isLoading, refetch }`). Nunca tuplas largas posicionales.

---

## 04. `useEffect` es último recurso

### 4.1 La regla

**[REQUIRED]** `useEffect` se usa **solo para sincronizar con algo externo a React**. Antes de escribir un efecto se verifica que el caso esté en la lista blanca de 4.2; si no está, el código va a otro lugar (4.3). Un `useEffect` fuera de la lista requiere comentario justificando por qué ninguna alternativa aplica.

**Por qué:** el efecto es el mecanismo con más bugs por unidad de línea en React — corre después del render, se re-dispara por dependencias mal declaradas, produce cascadas de renders y race conditions. La mayoría de los `useEffect` en código real no sincronizan con nada externo: son data fetching que pertenece a la capa de datos (sección 07) o estado derivado que se calcula en render. Las IAs sobre-generan `useEffect` porque abunda en su entrenamiento — esta regla existe para contrarrestar exactamente ese sesgo.

### 4.2 Los 4 usos legítimos

**[REQUIRED]** Lista cerrada — un efecto es legítimo solo si:

1. **Suscripción a un sistema externo:** event listeners de `window`/`document`, WebSocket, `BroadcastChannel`, `matchMedia`, visibilidad de la página. Siempre con cleanup que des-suscribe.
2. **Integración con una librería imperativa no-React:** un chart, un mapa, un editor que se instancia sobre un nodo DOM y se destruye en cleanup.
3. **Manipulación del DOM que React no expresa declarativamente:** mover el foco tras una acción, medir un elemento, hacer scroll a una posición. (Si es solo "al montar", evaluar primero un ref callback — ver sección 10.5.)
4. **Timers y sincronización con el tiempo:** `setInterval`/`setTimeout` cuyo ciclo de vida depende del montaje del componente, con cleanup que cancela.

### 4.3 Lo que NO es un efecto — y a dónde va

**[REQUIRED]** Tabla de redirección:

| Anti-patrón con `useEffect` | Dónde va en realidad |
|---|---|
| Fetch de datos al montar (`useEffect` + `fetch` + `setState`) | Capa de datos: TanStack Query vía `features/x/api/` (sección 07). Hereda de Frontend §05: server state nunca a mano |
| Estado derivado (`useEffect` que calcula `total` cuando cambia `items`) | Se calcula en render: `const total = items.reduce(...)`. Si es costoso y está medido, `useMemo` (sección 09) |
| Resetear estado cuando cambia una prop | Prop `key` en el componente para remontarlo, o cálculo en render |
| Reaccionar a un evento del usuario (efecto que observa un booleano `submitted`) | El código va en el event handler que disparó el cambio |
| Encadenar estados (`useEffect` que setea B cuando cambia A) | Un solo evento setea todo lo necesario; o `useReducer` si la transición es compleja |
| Notificar al padre de un cambio | El padre pasa el callback y el hijo lo llama en el handler |

---

## 05. Context

### 5.1 Solo estado de baja frecuencia de cambio

**[REQUIRED]** Context de aplicación se usa **solo para estado que cambia pocas veces por sesión**: tema claro/oscuro, sesión de auth, idioma, configuración de la app. **Prohibido** para estado que cambia por tecla, por scroll, por movimiento de mouse o en cada respuesta del servidor.

**Por qué:** cada cambio de valor de un Context re-renderiza **todos** los componentes que lo consumen, sin importar qué parte del valor usan. Un Context con el texto de un input re-renderiza el árbol entero en cada tecla. React no ofrece suscripción parcial a Context — para estado de alta frecuencia se usa estado local (input), server state (sección 07) o un store global con selectores (sección 06).

**Nota de jerarquía:** el estado que viaja por Context sigue siendo el escalón 4 del árbol de decisión que **hereda de Frontend §05** — llegar a Context ya requiere haber descartado local y lifting.

### 5.2 Split de contexts por dominio

**[REQUIRED]** Un Context por dominio de estado, no un `AppContext` monolítico: `ThemeContext`, `AuthContext` separados. Si un dominio expone valor y acciones y las acciones son estables, se separan en dos contexts (`AuthStateContext` / `AuthActionsContext`) cuando haya consumidores que solo disparan acciones.

**Por qué:** con un Context monolítico, cambiar el tema re-renderiza a quien solo lee el usuario. El split hace que cada consumidor se suscriba exactamente a lo que usa — es la única forma de granularidad que Context ofrece.

**[RECOMMENDED]** Cada Context se expone con un hook con guard, nunca consumiendo `useContext` crudo en componentes:

```tsx
// app/providers/auth.tsx
const AuthContext = createContext<AuthSession | null>(null);

export function useAuthSession(): AuthSession {
  const ctx = useContext(AuthContext);
  if (ctx === null) throw new Error("useAuthSession requiere <AuthProvider> en el árbol");
  return ctx;
}
```

---

## 06. Estado: matriz de decisión

**Hereda de Frontend §05** el árbol de 4 escalones y la prohibición de mezclar server state con client state. Este documento lo convierte en matriz operativa y fija la librería:

### 6.1 La matriz

**[REQUIRED]** Se recorre en orden y se usa la **primera fila** que aplique:

| ¿El estado...? | Herramienta | Ejemplos |
|---|---|---|
| ...lo usa un solo componente | `useState` / `useReducer` local | input controlado, modal abierto, tab activa |
| ...lo comparten hermanos cercanos | Lift al padre común más bajo | filtro que afecta lista y contador |
| ...viene del backend (se puede recargar) | **Server state: TanStack Query** (sección 07) | órdenes, perfil, catálogo — todo lo que responde un Worker |
| ...es global y cambia poco | Context (sección 05) | tema, sesión auth, idioma |
| ...es global, de cliente, y cambia seguido | Store global con selectores (Zustand) | carrito offline-first, estado de un editor multi-panel |

**[REQUIRED]** La última fila se usa solo si las cuatro anteriores fallaron. En la práctica, tras mover el server state a TanStack Query y lo infrecuente a Context, **queda muy poco estado genuinamente global de cliente** — un store global que crece es señal de server state mal clasificado, no de una app compleja.

### 6.2 Server state: TanStack Query, no SWR

**[REQUIRED]** La librería de server state del stack es **TanStack Query**. Se fija una y no se mezclan las dos en un proyecto (mismo porqué que Frontend §10.1: un solo enfoque por problema).

**Por qué TanStack Query y no SWR:** ambas resuelven cache/revalidación/dedupe, pero el contrato con los Workers necesita más que GETs: **mutations de primera clase** con `onMutate`/`onError`/`onSettled` (base de los optimistic updates de 7.4), invalidación selectiva por query key tras cada mutación, y devtools de inspección de cache. SWR es más pequeña pero deja las mutaciones y la invalidación estructurada como ejercicio al lector — exactamente la parte donde una IA improvisa distinto cada vez. Si el proyecto fuera 100% lectura, SWR bastaría; este stack no lo es.

**[REQUIRED]** Query keys con convención fija por feature: `[feature, entidad, params]` — ej. `["orders", "list", { status }]`, `["orders", "detail", orderId]`. La invalidación usa prefijos (`["orders"]` invalida todo el feature).

---

## 07. Data fetching

### 7.1 La capa `api/` por feature

**[REQUIRED]** Cada feature tiene su carpeta `api/` con: (a) funciones de request que usan el cliente único (**hereda de Frontend §6.1** — la función de `api/` es el único lugar que lo toca) y (b) los hooks de query/mutation que las envuelven. Los componentes consumen **solo los hooks**, nunca las funciones de request (hereda de Frontend §2.3: UI → hooks → datos).

**[REQUIRED]** Las funciones de `api/` están tipadas contra los **schemas zod del paquete de contratos compartido** (hereda de API §08 — fuente única de tipos request/response) y desenvuelven el envelope de API §03: hacia adentro del frontend viaja `data` tipado o un `AppError` con el `error.code` estable del contrato — nunca el envelope crudo.

```ts
// features/orders/api/getOrders.ts
import { orderListResponse, type OrderListResponse } from "shared/contracts/orders";
import { apiClient } from "@/shared/lib/apiClient"; // desenvuelve envelope y normaliza AppError (Frontend §6.3)

export async function getOrders(params: { status?: string }): Promise<OrderListResponse> {
  const data = await apiClient.get("/orders", { params });
  return orderListResponse.parse(data); // valida en runtime el borde (Frontend §6.2)
}

// features/orders/api/useOrders.ts
export function useOrders(params: { status?: string }) {
  return useQuery({ queryKey: ["orders", "list", params], queryFn: () => getOrders(params) });
}
```

### 7.2 Estados de query → patrones de UI

**[REQUIRED]** Los cuatro estados obligatorios de Frontend §4.2 se mapean 1:1 desde la query, y cada uno se renderiza según [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md):

| Estado de la query | Condición | Patrón (STATES_PATTERNS) |
|---|---|---|
| Loading | `isPending` | §1 — skeleton con la forma del contenido final |
| Error | `isError` | §3 — mensaje accionable según `error.code`, con retry |
| Empty | success y `data` vacío | §2 — empty state con acción |
| Success | success con datos | contenido real |

**[RECOMMENDED]** Refetch en background (`isFetching` con datos ya presentes) **no** vuelve a mostrar el skeleton — se muestra el dato actual con indicador discreto. Volver a loading en cada revalidación es el anti-patrón de parpadeo de STATES_PATTERNS §6.

### 7.3 Manejo de errores por `error.code`

**[REQUIRED]** La lógica de UI ante errores discrimina por `error.code` del contrato (hereda de API §03: el `code` es estable, el `message` no). Prohibido hacer lógica sobre el texto del mensaje.

### 7.4 Optimistic updates

**[RECOMMENDED]** Se aplican solo cuando se cumplen las dos condiciones:

1. **Acción reversible** — si el servidor falla, deshacer en la UI no confunde ni pierde trabajo (marcar favorito, toggle de estado, reordenar).
2. **Alta frecuencia / feedback inmediato esperado** — el usuario la repite muchas veces y esperar el round-trip al Worker en cada una se siente roto.

Acciones irreversibles o de alto costo (pagar, eliminar definitivo, enviar) **nunca** son optimistas: muestran estado `submitting` real (hereda de Frontend §9.3).

**[REQUIRED]** Todo optimistic update implementa rollback: snapshot del cache antes de mutar, restauración en `onError` (con aviso al usuario de que la acción no se aplicó — no silencioso), invalidación en `onSettled` para reconciliar con el servidor:

```ts
const toggleFavorite = useMutation({
  mutationFn: (id: string) => api.toggleFavorite(id),
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: ["orders"] });
    const previous = queryClient.getQueryData(["orders", "list"]);
    queryClient.setQueryData(["orders", "list"], (old) => optimisticToggle(old, id));
    return { previous };
  },
  onError: (_err, _id, ctx) => {
    queryClient.setQueryData(["orders", "list"], ctx?.previous); // rollback
    toast.error("No se pudo guardar el cambio"); // copy según STATES_PATTERNS §5
  },
  onSettled: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
});
```

---

## 08. Suspense, lazy y error boundaries

### 8.1 Code splitting por ruta

**[REQUIRED]** Hereda de Frontend §8.2 (toda ruta no inicial se carga diferida). Implementación de referencia en este stack: `React.lazy` + `Suspense` en la definición central de rutas:

```tsx
// app/routes/index.tsx
const OrdersPage = lazy(() => import("@/features/orders/components/OrdersPage"));

<Route path="/orders" element={
  <Suspense fallback={<PageSkeleton />}>
    <OrdersPage />
  </Suspense>
} />
```

**[RECOMMENDED]** Splitting adicional por debajo de la ruta solo para bloques pesados y de aparición condicional (un editor, un chart grande, un modal complejo) — no se hace `lazy` de componentes pequeños: cada chunk agrega un round-trip.

### 8.2 Error boundaries por región

**[REQUIRED]** Una sola error boundary en el root **no basta** (profundiza Frontend §2.2): se colocan en tres niveles, y el fallo se contiene en el nivel más bajo posible:

| Nivel | Qué protege | Qué muestra al fallar |
|---|---|---|
| Root | catástrofe total | pantalla de error general con recarga ([FRONTEND_ERROR_PAGES_STANDARD.md](../Patterns/FRONTEND_ERROR_PAGES_STANDARD.md)) |
| Layout/página (por ruta) | una página rota | error de página; navbar/sidebar siguen vivos y navegables |
| Widget (bloque independiente: chart, panel, feed) | un bloque roto | error inline del tamaño del bloque, con retry; el resto de la página funciona |

**Por qué:** con una sola boundary en root, un `undefined` en un chart secundario tira abajo la sesión completa del usuario. El radio de explosión de un error debe ser proporcional a la importancia del bloque que falló.

**[REQUIRED]** Toda `Suspense` boundary de carga tiene una error boundary asociada al mismo nivel — un chunk que falla al descargarse (deploy nuevo, red) es un error esperado, no una pantalla blanca.

### 8.3 Fallbacks que no saltan

**[REQUIRED]** El fallback de una `Suspense` boundary reserva **el mismo espacio** que el contenido final: skeleton con las dimensiones del layout real (misma altura de fila, mismo aspect-ratio del chart), no un spinner centrado que colapsa la altura.

**Por qué:** un fallback de tamaño distinto produce layout shift al resolverse — rompe directamente el objetivo CLS < 0.1 que **hereda de Frontend §11.4**, y el salto se percibe como página rota. La forma del skeleton la define STATES_PATTERNS §1; esta regla fija que además su caja externa sea estable.

---

## 09. Performance

Presupuesto de bundle, memoización con evidencia y Core Web Vitals **heredan de Frontend §11.1, §11.2 y §11.4**. Este documento agrega el flujo de trabajo y dos reglas concretas:

### 9.1 Default: no memoizar

**[RECOMMENDED]** El default al escribir un componente es **cero** `memo`/`useMemo`/`useCallback`. El flujo para agregar memoización (que hace cumplible el "con evidencia medida" de Frontend §11.2): (1) síntoma percibido o INP fuera de umbral → (2) grabación en React DevTools Profiler → (3) identificar el componente que re-renderiza caro y por qué prop/estado → (4) memoizar **ese punto**, no el árbol → (5) volver a medir. La medición se anota en el PR (qué se midió, antes/después) — es la justificación escrita que exige el formato del handbook para desviarse del default.

**Nota React 19:** si el proyecto activa React Compiler, la memoización manual sobrante se elimina en vez de mantenerse "por si acaso" — el compilador la hace redundante y su presencia confunde sobre dónde hubo problemas reales.

### 9.2 Keys estables

**[REQUIRED]** La `key` de cada elemento de una lista es un identificador estable del dato (`order.id`), **nunca el índice** en listas que pueden reordenarse, filtrarse, o crecer/decrecer por el frente. Índice como key se tolera solo en listas estáticas que jamás cambian de orden ni de tamaño durante la vida del componente.

**Por qué:** con índice como key, al insertar o reordenar, React empareja por posición: el estado interno de cada fila (inputs, selección, animaciones) queda pegado a la posición vieja y aparece en la fila equivocada. Es un bug de datos visto por el usuario, no una sutileza de rendimiento.

### 9.3 Virtualización para listas largas

**[RECOMMENDED]** Profundiza Frontend §11.3 con umbral operativo: una lista que puede superar **~100 items renderizados a la vez** se virtualiza (ej. `@tanstack/react-virtual`); por debajo, el DOM completo con keys estables es más simple y suficiente. El número es heurística, no ley (formato §3): el objetivo real es INP < 200ms y scroll fluido — una lista de 80 filas con celdas muy pesadas puede necesitar virtualización antes; una de 300 `<li>` de texto plano puede no necesitarla aún. Paginar o "cargar más" desde la API es preferible a virtualizar cuando el usuario no necesita todo el conjunto (ver [FRONTEND_TABLE_PATTERNS.md](../Patterns/FRONTEND_TABLE_PATTERNS.md)).

---

## 10. React 19: qué se usa de este release

> Verificado contra React 19.x estable (19.0 dic-2024; APIs vigentes a la fecha de este documento). Si una API cambia de estado en releases futuros, se actualiza esta sección, no se congela el stack.

### 10.1 Formularios: Actions + `useActionState`

**[RECOMMENDED]** Para formularios contra los Workers, el submit se modela como Action de React 19: función async pasada a `<form action={...}>`, con `useActionState` para el estado del resultado y pending integrado. Esto implementa los estados `idle → submitting → success | error` que **hereda de Frontend §9.3** con soporte nativo, en lugar de cablear `isSubmitting` a mano. Convive con `react-hook-form` + zod (Frontend §9.1): la librería valida y gestiona campos; la Action ejecuta el submit.

```tsx
const [result, submitAction, isPending] = useActionState(
  async (_prev: FormResult | null, formData: FormData) => {
    const parsed = loginSchema.safeParse(Object.fromEntries(formData));
    if (!parsed.success) return { status: "error", code: "VALIDATION_ERROR" } as const;
    return login(parsed.data); // features/auth/api/ — devuelve FormResult, no lanza al render
  },
  null,
);
// <button disabled={isPending}> cumple el anti-doble-envío de Frontend §9.3
```

### 10.2 `useOptimistic`

**[RECOMMENDED]** Para optimismo local dentro de una Action (un toggle, un item agregado a una lista visible) se usa `useOptimistic` — revierte solo automáticamente si la Action falla. Para optimismo sobre **cache de servidor compartido entre componentes**, el patrón sigue siendo el de mutations de la sección 7.4. Criterio: ¿el dato optimista vive solo en este componente mientras dura la Action? → `useOptimistic`. ¿Debe verse reflejado en todo consumidor de la query? → TanStack Query.

### 10.3 `ref` como prop — `forwardRef` prohibido en código nuevo

**[REQUIRED]** En React 19, los componentes de función reciben `ref` como prop normal. Código nuevo **no usa `forwardRef`**; al tocar un componente que lo usa, se migra en ese mismo cambio (es mecánico).

```tsx
// ✅ React 19
interface InputProps extends React.ComponentPropsWithRef<"input"> { label: string }
function TextInput({ label, ref, ...props }: InputProps) {
  return <label>{label}<input ref={ref} {...props} /></label>;
}
```

**Por qué:** `forwardRef` está deprecado en 19 y es puro ruido de wrapping; mantener ambos estilos en el repo hace que cada generación de IA elija uno al azar.

### 10.4 `use` y `<Context>` directo

**[RECOMMENDED]** Para leer Context se puede usar `use(MiContext)` (funciona dentro de condicionales, a diferencia de `useContext`) — pero la vía estándar sigue siendo el hook con guard de 5.2, que ya encapsula la lectura. Como provider, se usa `<MiContext value={...}>` directamente; `<MiContext.Provider>` es sintaxis legacy y no se escribe en código nuevo.

**[REQUIRED]** `use(promise)` con Suspense **no** reemplaza a TanStack Query para server state: `use` no aporta cache, revalidación ni mutations, y una promesa creada en render se re-crea en cada render. Se admite solo para recursos ya cacheados/estables pasados desde arriba. El data fetching sigue siendo la sección 07.

### 10.5 Cleanup en ref callbacks

**[RECOMMENDED]** Los ref callbacks pueden devolver función de cleanup en React 19 — para "hacer algo cuando el nodo aparece y deshacerlo cuando desaparece" (observers, medición) esto reemplaza al par `useEffect` + ref, y reduce aún más los efectos legítimos del tipo 3 de la sección 4.2.

### 10.6 Qué no se adopta (todavía)

**[RECOMMENDED]** No se usan en producción APIs experimentales o de canal inestable (`<Activity>` fuera de su uso documentado estable, APIs de server components — esta SPA no tiene servidor React). Regla general: solo APIs marcadas estables en la documentación oficial de la versión que fija el `package.json`.

---

## Checklist rápido — feature React terminado

- [ ] ¿El feature sigue la estructura `components/ hooks/ api/ types.ts index.ts`, y cada archivo nuevo está donde dice la tabla 1.2? (01)
- [ ] ¿Ningún componente acumula 3+ props booleanas de variante — se usó children / compound / union discriminada? (02)
- [ ] ¿Cada custom hook tiene una sola responsabilidad y se extrajo por reuso real o testeo aislado? (03)
- [ ] ¿Cada `useEffect` está en la lista de 4 usos legítimos — cero fetching y cero estado derivado en efectos? (04)
- [ ] ¿Context solo para estado de baja frecuencia, un context por dominio, consumido vía hook con guard? (05)
- [ ] ¿Cada pieza de estado pasó por la matriz 6.1 — server state solo en TanStack Query, query keys `[feature, entidad, params]`? (06)
- [ ] ¿Todo fetching pasa por `api/` tipado con los schemas del contrato compartido, y la UI discrimina errores por `error.code`? (07)
- [ ] ¿Estados de query mapeados a STATES_PATTERNS, sin skeleton en refetch de background? (07)
- [ ] ¿Optimistic updates solo en acciones reversibles, siempre con rollback + aviso en error? (07)
- [ ] ¿Rutas lazy con Suspense, error boundaries en root + página + widget, fallbacks del mismo tamaño que el contenido? (08)
- [ ] ¿Cero memoización sin medición de Profiler anotada, keys estables (nunca índice en listas mutables), virtualización si la lista supera ~100 items? (09)
- [ ] ¿Forms con Actions/`useActionState`, `ref` como prop (sin `forwardRef` nuevo), `use`/`useOptimistic` solo en sus casos definidos? (10)
