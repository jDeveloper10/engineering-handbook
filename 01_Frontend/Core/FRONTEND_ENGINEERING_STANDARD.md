---
title: "FRONTEND ENGINEERING STANDARD"
category: 01_Frontend
doc_type: estandar
tags:
  - standards
  - conventions
  - design-tokens
  - components
  - react
  - accessibility
  - performance
summary: "Nivel 1 del dominio Frontend. Define las reglas base de todo proyecto frontend: design system (spacing, colores, tipografía, grid), arquitectura por feature, componentes, estado, API integration, TypeScript, routing, formularios, CSS, performance, seguridad y accesibilidad."
keywords:
  - ui
  - architecture
  - state-management
  - css
  - testing
  - git
  - bundle
updated: 2026-07-26
status: current
---

# FRONTEND ENGINEERING STANDARD

> Nivel 1 del handbook. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica y después con una implementación de referencia en el stack actual (React + TypeScript + Tailwind).
>
> Documentos de Nivel 2 que dependen de este: [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md), [FRONTEND_LANDING_PATTERNS.md](../Patterns/FRONTEND_LANDING_PATTERNS.md), [FRONTEND_UI_PATTERNS.md](../Patterns/FRONTEND_UI_PATTERNS.md), [FRONTEND_NAVIGATION_PATTERNS.md](../Patterns/FRONTEND_NAVIGATION_PATTERNS.md), [FRONTEND_AUTH_PATTERNS.md](FRONTEND_AUTH_PATTERNS.md), [FRONTEND_DASHBOARD_PATTERNS.md](../Patterns/FRONTEND_DASHBOARD_PATTERNS.md), [FRONTEND_CRUD_PATTERNS.md](../Patterns/FRONTEND_CRUD_PATTERNS.md), [FRONTEND_TABLE_PATTERNS.md](../Patterns/FRONTEND_TABLE_PATTERNS.md), [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md), [FRONTEND_NOTIFICATIONS_PATTERNS.md](../Patterns/FRONTEND_NOTIFICATIONS_PATTERNS.md), [FRONTEND_MODALS_PATTERNS.md](../Patterns/FRONTEND_MODALS_PATTERNS.md), [FRONTEND_SIDEBAR_PATTERNS.md](../Patterns/FRONTEND_SIDEBAR_PATTERNS.md), [FRONTEND_HTML_STRUCTURE_STANDARD.md](FRONTEND_HTML_STRUCTURE_STANDARD.md), [FRONTEND_RESPONSIVE_STANDARD.md](FRONTEND_RESPONSIVE_STANDARD.md), [FRONTEND_ACCESSIBILITY_STANDARD.md](../UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md), [FRONTEND_COLOR_CONTRAST_STANDARD.md](../UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md), [FRONTEND_ELEVATION_STANDARD.md](../UI_Components/FRONTEND_ELEVATION_STANDARD.md), [FRONTEND_FORMATTING_STANDARD.md](FRONTEND_FORMATTING_STANDARD.md), [FRONTEND_ERROR_PAGES_STANDARD.md](../Patterns/FRONTEND_ERROR_PAGES_STANDARD.md), [FRONTEND_ANALYTICS_CHARTS_STANDARD.md](../Patterns/FRONTEND_ANALYTICS_CHARTS_STANDARD.md), [FRONTEND_MICROCOPY_STANDARD.md](../UI_Components/FRONTEND_MICROCOPY_STANDARD.md), [FRONTEND_ICON_SYSTEM_STANDARD.md](../UI_Components/FRONTEND_ICON_SYSTEM_STANDARD.md), [FRONTEND_MOTION_STANDARD.md](../UI_Components/FRONTEND_MOTION_STANDARD.md).
>
> Objetivo: que cualquier proyecto nuevo, generado por IA o por mí, sea mantenible por otra persona (o por mí en 6 meses) sin arqueología de código.

---

## 01. UX/UI Design System

### 1.1 Spacing en escala fija

**[REQUIRED]** Todo espaciado (margin, padding, gap) sale de una escala fija predefinida, nunca de un valor libre elegido a ojo.

```
Escala base 8 (px): 4  8  16  24  32  48  64  96
```

**Por qué:** un valor libre (`margin: 37px`) no es reproducible ni comparable entre componentes — cada desarrollador (o cada generación de IA) improvisa un número distinto para "lo mismo". La escala fija hace que el espaciado sea una decisión de sistema, no de gusto momentáneo.

**Implementación (Tailwind):** la escala de espaciado por defecto de Tailwind ya sigue base-4 (`p-1`=4px ... `p-8`=32px). Un valor fuera de la escala (`p-[13px]`) requiere comentario explicando por qué.

### 1.2 Colores como tokens semánticos

**[REQUIRED]** Los colores viven en un único lugar centralizado y se nombran por su significado (`success`, `danger`, `warning`, `brand`), no por el color en sí (`green`, `red`). Ningún componente escribe un color hardcodeado.

**Por qué:** si el color se nombra `green` y la marca cambia su verde por turquesa, hay que buscar y reemplazar en todo el código. Si se nombra `success`, el token cambia una vez en un solo archivo.

**Implementación (Tailwind):**
```ts
// tailwind.config.ts
colors: {
  brand: { 50: "#eff6ff", 500: "#3b82f6", 900: "#1e3a8a" },
  success: "#16a34a",
  danger: "#dc2626",
  warning: "#d97706",
}
```

Reglas completas de construcción de paleta, contraste, dark/light mode y estados de color por componente en [FRONTEND_COLOR_CONTRAST_STANDARD.md](../UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md) (Nivel 2).

### 1.3 Tipografía en escala fija

**[REQUIRED]** Máximo 2 familias tipográficas por proyecto y una escala de tamaños fija (no "se ve bien así"). **[RECOMMENDED]** valores concretos de referencia: 12 / 14 / 16 / 18 / 20 / 24 / 30 / 36px, y 3 pesos (regular 400, medium 500, bold 700).

**Por qué:** más de 2 familias o pesos indistintos es indecisión de diseño disfrazada de variedad — el usuario percibe inconsistencia, no riqueza visual.

### 1.4 Grid y breakpoints

**[REQUIRED]** Los breakpoints responsive son fijos y consistentes en todo el proyecto, no inventados por componente. **[RECOMMENDED]** valores de referencia: 640 / 768 / 1024 / 1280 / 1536px, contenedor máximo de contenido ~1280px.

### 1.5 Un componente por elemento de UI repetido

**[REQUIRED]** Botones, cards, inputs: un solo componente con variantes (`variant`, `size`), nunca el mismo patrón visual copiado con clases sueltas en 3+ lugares distintos. Detalle completo en sección 04.

### 1.6 Estados visuales obligatorios

**[REQUIRED]** Todo elemento interactivo define explícitamente: `default`, `hover`, `active/pressed`, `focus-visible` (ver sección 13), `disabled`, y `loading` si aplica. Un botón sin estado `disabled` visualmente distinto es un bug de diseño, no un detalle menor.

### 1.7 Imágenes

**[REQUIRED]** `width`/`height` explícitos (evita layout shift), `alt` descriptivo o `alt=""` si es decorativa. **[RECOMMENDED]** formato moderno (`webp`/`avif` con fallback), lazy loading por defecto salvo el elemento LCP de la página.

### 1.8 Responsive mobile-first

**[REQUIRED]** El estilo base se escribe para mobile (~375px) y se agranda con breakpoints hacia arriba, nunca al revés. Se valida en al menos 3 anchos: mobile (375px), tablet (768px), desktop (1280px) antes de dar un componente por terminado. Estándar completo (tamaños fluidos, touch-friendly, comportamiento por componente, checklist de validación) en [FRONTEND_RESPONSIVE_STANDARD.md](FRONTEND_RESPONSIVE_STANDARD.md) (Nivel 2).

### 1.9 Dark mode

**[RECOMMENDED]** Si el proyecto tiene dark mode: **[REQUIRED]** estrategia por clase (toggle explícito), no solo `prefers-color-scheme` — el usuario debe poder overridear la preferencia del sistema. Cada color del token tiene su par claro/oscuro definido, no un override disperso por componente. Reglas completas (fondo/superficie/texto correctos por modo, nunca negro ni blanco puro) en [FRONTEND_COLOR_CONTRAST_STANDARD.md](../UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md) sección 3-4.

### 1.10 Catálogo de estilos visuales

Cuando un proyecto necesita una identidad visual específica (glassmorphism, brutalism, minimalismo, etc.), la referencia de tokens por estilo está en [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md) (Nivel 2). Se elige un estilo, se extraen sus tokens y se cargan siguiendo 1.1-1.9.

### 1.11 Landing pages

Reglas adicionales específicas de landing (estructura de bloques, jerarquía de CTAs) en [FRONTEND_LANDING_PATTERNS.md](../Patterns/FRONTEND_LANDING_PATTERNS.md) (Nivel 2).

### 1.12 Selección de patrón de UI — no Cards por defecto

**[REQUIRED]** Antes de maquetar cualquier sección, elegir el patrón de UI (Cards, Timeline, Tabla, Feature Section, Accordion, KPI tiles, etc.) según el tipo de información, no usar Cards automáticamente porque es el patrón más fácil de repetir. Tabla de decisión completa y patrones por tipo de página (landing, dashboard, CRUD, settings, etc.) en [FRONTEND_UI_PATTERNS.md](../Patterns/FRONTEND_UI_PATTERNS.md) (Nivel 2).

**Por qué:** la card está sobrerrepresentada en los datos de entrenamiento de cualquier IA — es la opción "segura" ante la duda, no necesariamente la más adecuada. Usarla por defecto para todo produce interfaces sin jerarquía visual (grid de N cards idénticas) en vez de composiciones con peso y estructura real.

### 1.13 Navegación

Patrones de navbar, sidebar y navegación mobile en [FRONTEND_NAVIGATION_PATTERNS.md](../Patterns/FRONTEND_NAVIGATION_PATTERNS.md) (Nivel 2). Complementa la sección 08 (Routing Rules) de este documento.

---

## 02. Frontend Architecture

### 2.1 Organización por feature, no por tipo de archivo

**[REQUIRED]** La primera línea de organización del código es el feature de negocio (`features/orders/`), no el tipo técnico de archivo (`components/`, `hooks/`, `services/` como carpetas de primer nivel).

**Por qué:** con organización por tipo, cambiar una funcionalidad obliga a tocar 4 carpetas distintas y nada se puede borrar limpio. Con organización por feature, borrar `features/orders/` no deja huérfanos en otras carpetas — esa es la prueba de que la arquitectura es correcta.

### 2.2 Aislamiento de fallos

**[REQUIRED]** Un error en un feature no debe tumbar la aplicación completa. Se logra con: error boundaries por feature/ruta (ver sección 06), sin estado global compartido innecesario, sin importar lógica interna de un feature desde otro.

### 2.3 Flujo de dependencia unidireccional

**[REQUIRED]** Dentro de un feature, la dependencia va siempre hacia abajo: UI → hooks → servicios de datos. Un componente **nunca** llama a la capa de red directamente (ver sección 06).

---

## 03. Project Structure

### 3.1 Convención de nombres

**[REQUIRED]** — tabla de referencia:

| Tipo | Convención | Ejemplo |
|---|---|---|
| Carpeta | `kebab-case` | `order-history/` |
| Componente | `PascalCase` | `OrderRow.tsx` |
| Hook | `camelCase`, prefijo `use` | `useOrders.ts` |
| Utilidad pura | `camelCase` | `formatCurrency.ts` |
| Constante | `UPPER_SNAKE_CASE` | `MAX_RETRY_ATTEMPTS` |
| Tipo/Interface | `PascalCase` | `interface OrderPayload` |
| Variable booleana | `is`/`has`/`should` + descripción | `isLoading` |
| Handler (prop recibida) | `onX` | `onSubmit` |
| Handler (implementación) | `handleX` | `handleSubmit` |

**Por qué:** un nombre predecible se encuentra sin buscar — la convención reduce la carga cognitiva de "¿cómo se llamaba esto?" tanto para un humano como para una IA generando código nuevo consistente con el resto del repo.

### 3.2 Idioma: código en inglés, contenido en español — nunca mezclados

**[REQUIRED]** Dos categorías, cada una en un solo idioma, sin excepción:

- **Código** (variables, funciones, componentes, props, clases CSS, nombres de archivo, claves de objetos internos) → **siempre en inglés**. Es la convención universal de la industria — mantiene compatibilidad con librerías, tooling, y con cualquier desarrollador (o IA) que se sume al proyecto sin importar su idioma nativo.
- **Contenido visible al usuario** (UI copy, botones, mensajes de error, notificaciones, emails, mensajes de WhatsApp) → **siempre en español**, el idioma real de los usuarios finales (Panamá/Colombia).

**[REQUIRED]** Nunca se mezclan los dos dentro del mismo elemento: ni una palabra en inglés suelta dentro de un texto en español visible al usuario, ni una palabra en español dentro de un identificador de código.

```
❌ function guardarUsuario() { ... }         → nombre de función en español
❌ const userNombre = ...                     → identificador mezclado
❌ Botón "Guardar cambios" al lado de otro "Submit" en la misma pantalla
❌ "Click aquí para continuar"                → anglicismo innecesario colado en copy en español
✅ function saveUser() { ... }
✅ const userName = ...
✅ Ambos botones: "Guardar cambios" / "Continuar"
```

**[RECOMMENDED]** Comentarios de código en español está bien (así se documenta este mismo handbook) — pero un comentario no arranca en un idioma y termina en otro.

**Por qué:** el código mezclado por idioma se vuelve impredecible de buscar (¿fue `usuario` o `user`?) y el copy mezclado se lee como traducido a medias, lo cual el usuario final percibe como poco profesional. Esta regla es de todo el handbook, no solo de frontend — se replica cuando se construyan `02_Backend` (mensajes de API), `07_DevOps` y cualquier dominio con contenido cara al usuario.

### 3.3 API pública por feature (barrels controlados)

**[REQUIRED]** Cada feature expone solo lo público desde un único punto de entrada. **[REQUIRED]** prohibido un barrel que re-exporta todo desde cualquier subcarpeta o barrels anidados en cascada.

**Por qué:** es la causa #1 de dependencias circulares y de bundles que no hacen tree-shaking.

```ts
// features/orders/index.ts ✅
export { OrderList } from "./components/OrderList";
export { useOrders } from "./hooks/useOrders";
export type { Order } from "./types";
// NO exportar internals (OrderRow, formatOrderStatus)
```

---

## 04. Component Rules

### 4.1 Un componente, una responsabilidad

**[REQUIRED]** Un componente hace una sola cosa. **[RECOMMENDED]** como heurística de tamaño: ~150-200 líneas sin imports/tipos — superarlo es señal (no ley) de que conviene dividir.

**Por qué el tamaño es heurística y no ley:** el número en sí no es lo que importa — lo que importa es si el componente mezcla responsabilidades (fetch + validación + formato + 3 vistas). Un componente de 250 líneas con una sola responsabilidad clara puede estar bien; uno de 120 líneas que hace 4 cosas distintas está mal. Preguntas para decidir: ¿tiene estado no relacionado entre sí?, ¿renderiza secciones visualmente independientes?, ¿mezcla lógica de negocio con presentación?

```tsx
// ❌ Mezcla fetch + formato + 3 estados visuales
function OrderPage() {
  const [orders, setOrders] = useState([]);
  useEffect(() => { fetch("/api/orders")... }, []);
  // ...
}

// ✅ Dividido por responsabilidad
function OrderPage() {
  const { data, isLoading, isError, error } = useOrders();
  if (isLoading) return <OrderListSkeleton />;
  if (isError) return <ErrorState message={error.message} />;
  if (!data?.length) return <EmptyState message="No hay órdenes aún" />;
  return <OrderList orders={data} />;
}
```

### 4.2 Estados obligatorios en componentes que consumen datos

**[REQUIRED]** Todo componente que obtiene datos maneja explícitamente 4 estados: loading, error, empty, success. Ninguno se omite en producción — ver ejemplo arriba en 4.1. Cómo diseñar bien cada uno (skeleton vs spinner, tipos de empty state, copy de error) en [FRONTEND_STATES_PATTERNS.md](../Patterns/FRONTEND_STATES_PATTERNS.md) (Nivel 2).

### 4.3 UI separada de lógica

**[REQUIRED]** Un componente presentacional no sabe de dónde vienen los datos ni cómo se calculan — los recibe por props o por un hook dedicado.

```
ProductCard/
├── ProductCard.tsx       # presentación pura
├── useProductCard.ts     # lógica no trivial (ej. cálculo de descuento)
├── types.ts
└── ProductCard.test.tsx
```

### 4.4 Props

**[REQUIRED]** Interface explícita, nunca `props: any`. **[RECOMMENDED]** máximo ~7 props — más que eso, agrupar en objeto de configuración o dividir el componente. **[REQUIRED]** evitar prop drilling de más de 2 niveles — usar Context o recomponer el árbol.

### 4.5 Composición sobre configuración

**[RECOMMENDED]** Preferir componer componentes pequeños sobre un componente con muchas props booleanas activando variantes.

```tsx
// ❌ 15 props booleanas
<Card showHeader showFooter compact hasShadow hasBorder rounded ... />
// ✅ Composición
<Card><Card.Header/><Card.Body/><Card.Footer/></Card>
```

Antes de asumir que el patrón visual correcto es una `Card`, ver [FRONTEND_UI_PATTERNS.md](../Patterns/FRONTEND_UI_PATTERNS.md) — no siempre lo es (sección 1.12).

### 4.6 Reutilización: shared vs feature

**[REQUIRED]** Un componente usado en 2+ features sube a `shared/`. Uno usado en 1 solo feature se queda ahí — no se sube "por si acaso".

**Por qué:** subir código "por si se reutiliza después" genera acoplamiento a un único caso de uso real disfrazado de código compartido, y complica el componente con flexibilidad que nadie usa todavía.

---

## 05. State Management

**[REQUIRED]** Árbol de decisión — se usa la primera opción de la lista que resuelva el problema, en este orden:

1. **UI state local** (`useState`/`useReducer`) — vive en el componente que lo necesita.
2. **Lift state up** — dos componentes hermanos comparten estado → sube al padre común.
3. **Server state** (React Query/SWR) — cualquier dato que viene del backend.
4. **Global state** (Context o store como Zustand) — solo lo verdaderamente transversal (usuario autenticado, permisos, config de la app).

**[REQUIRED]** Server state y client/UI state **nunca se mezclan en el mismo store**.

**Por qué:** meter datos de servidor en `useState` + `useEffect` manual es la causa más común de "loading infinito" y datos desincronizados — una librería de server state ya resuelve cache, revalidación y race conditions; reimplementarlo a mano reintroduce esos bugs.

```ts
// ✅ Server state
function useOrders() {
  return useQuery({ queryKey: ["orders"], queryFn: () => apiClient.get<Order[]>("/orders") });
}
// ✅ Global UI state — nunca datos que vengan del backend
const useAuthStore = create<{ user: User | null; setUser: (u: User|null)=>void }>((set)=>({
  user: null, setUser: (user) => set({ user }),
}));
```

---

## 06. API Integration

### 6.1 Cliente único

**[REQUIRED]** Toda llamada de red pasa por un cliente centralizado. Ningún componente ni hook llama a la capa de red directamente.

```ts
class ApiClient {
  constructor(private baseUrl: string) {}
  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, { headers: this.buildHeaders() });
    if (!res.ok) throw normalizeError(res);
    return res.json();
  }
  private buildHeaders() {
    const token = getAuthToken();
    return { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }) };
  }
}
export const apiClient = new ApiClient(import.meta.env.VITE_API_URL);
```

### 6.2 Contratos tipados

**[REQUIRED]** Cada endpoint tiene un tipo de request/response explícito. **[REQUIRED]** cuando el dato viene de fuera de tu control (backend de terceros, respuesta que puede cambiar sin aviso), se valida en runtime, no solo se asume el tipo de TypeScript.

```ts
const OrderSchema = z.object({ id: z.string(), amount: z.number(), status: z.enum(["pending","paid","failed"]) });
type Order = z.infer<typeof OrderSchema>;
```

### 6.3 Errores normalizados

**[REQUIRED]** Todo error de red se normaliza a una forma conocida antes de llegar al componente. El componente nunca trabaja con el error crudo de la petición.

```ts
interface AppError { code: string; message: string; cause?: unknown; }
```

Mensaje al usuario: accionable, sin stack traces ni códigos internos. El detalle técnico va a logging, no a la UI.

### 6.4 BFF cuando hay múltiples backends

**[RECOMMENDED]** Si el frontend habla con más de un backend (ej. Supabase + Workers + terceros) y la agregación es compleja, esa orquestación vive en un Worker (BFF), no en el cliente.

**Por qué:** evita exponer múltiples API keys al cliente y evita duplicar lógica de agregación si hay más de un frontend consumiendo los mismos datos.

### 6.5 Variables de entorno tipadas

**[REQUIRED]** Un único punto de acceso a variables de entorno, validado al arrancar. No se accede a la variable de entorno cruda dispersa por el código.

```ts
const env = { apiUrl: import.meta.env.VITE_API_URL as string };
if (!env.apiUrl) throw new Error("VITE_API_URL no está definida");
export default env;
```

### 6.6 El frontend no tiene lógica de backend — la autoridad vive en el Worker

**[REQUIRED]** El frontend **no ejecuta lógica de servidor**: nada de acceso directo a la base de datos, ni reglas de negocio autoritativas, ni validación que se dé por definitiva. Toda validación real de entrada, toda regla de negocio y todo acceso a datos (D1/R2/KV) viven en el **Worker** (`02_Backend/BACKEND_ENGINEERING_STANDARD.md` §00 y §05). La validación del cliente (zod + react-hook-form, sección 9.2) existe **solo para UX** — feedback inmediato mientras el usuario escribe — y el Worker la **re-valida siempre**, porque el cliente es manipulable (DevTools, requests directos a la API, extensiones).

**Por qué:** un chequeo que solo vive en el frontend no existe para un atacante — se saltea con un `fetch` directo al endpoint. Además, duplicar la regla de negocio en el cliente crea dos fuentes de verdad que divergen. El frontend presenta y da feedback; el Worker decide. Un mismo esquema `zod` puede compartirse entre ambos, pero la ejecución autoritativa es la del servidor, nunca la del cliente — el cliente nunca asume "como validé en el form, va a pasar", siempre trata la respuesta del Worker (`success/error`, sección 6.3) como la verdad.

---

## 07. TypeScript Rules

### 7.1 TypeScript siempre

**[REQUIRED]** Todo proyecto nuevo usa TypeScript desde el primer commit, aunque sea un prototipo rápido.

**Por qué:** esto cierra directamente una deuda técnica ya identificada de TS inconsistente entre proyectos — "lo tipo después" nunca pasa en la práctica.

### 7.2 Modo estricto

**[REQUIRED]** `strict: true` en `tsconfig.json` en todo proyecto.

### 7.3 Prohibido `any`

**[REQUIRED]** Si el tipo real no se conoce, se usa `unknown` y se valida (con `zod` u otro parser), no `any`.

**Excepción documentada:** `// TODO: tipar (fecha/ticket)` sobre código de terceros sin tipos, nunca como default permanente.

### 7.4 `type` vs `interface`

**[RECOMMENDED]** `interface` para formas de objetos/props; `type` para uniones, tuplas y tipos derivados.

### 7.5 Discriminated unions para estados

**[RECOMMENDED]** Modelar estados mutuamente excluyentes como union discriminada, no como flags booleanos combinables.

```ts
type FetchState<T> =
  | { status: "idle" } | { status: "loading" }
  | { status: "error"; error: AppError } | { status: "success"; data: T };
```

**Por qué:** evita el anti-patrón `{ data?: T; loading: boolean; error?: string }`, donde el compilador permite combinaciones imposibles (`loading: true` y `data` presente a la vez).

### 7.6 No duplicar tipos entre capas

**[REQUIRED]** Si el backend genera tipos (Supabase, OpenAPI codegen), esos son la fuente de verdad — no se re-escriben a mano en frontend.

---

## 08. Routing Rules

### 8.1 Rutas centralizadas

**[REQUIRED]** La definición de rutas vive en un solo lugar del proyecto (`app/routes/`), no dispersa dentro de cada feature.

### 8.2 Code splitting por ruta

**[REQUIRED]** Toda ruta que no sea la primera pantalla se carga de forma diferida (`lazy`/`import()`), no se manda todo el árbol de features en el bundle inicial.

**Por qué:** impacta directamente el tiempo de carga inicial, que es el Core Web Vital más visible para el usuario (ver sección 11).

### 8.3 Rutas protegidas centralizadas

**[REQUIRED]** La lógica de "¿puede ver esto?" vive en un solo componente/guard, no repetida como `if (!user)` dentro de cada página.

Ver también [FRONTEND_NAVIGATION_PATTERNS.md](../Patterns/FRONTEND_NAVIGATION_PATTERNS.md) (Nivel 2) para qué patrón de navegación (navbar, sidebar, bottom nav) corresponde a cada tipo de producto.

### 8.4 Nomenclatura de rutas

**[RECOMMENDED]** URLs en `kebab-case`. **[REQUIRED]** params del router tipados explícitamente, no asumidos sin chequeo cuando el componente los necesita sí o sí.

---

## 09. Forms Rules

Para formularios de autenticación (login, registro, recuperación de contraseña) ver [FRONTEND_AUTH_PATTERNS.md](FRONTEND_AUTH_PATTERNS.md) (Nivel 2) — cubre layouts, orden de campos, seguridad UX y accesibilidad específica de auth además de estas reglas base.

### 9.1 Librería de formularios + validación declarativa

**[REQUIRED]** para formularios de 3+ campos: gestión de estado y validación con una librería declarativa (ej. `react-hook-form` + `zod`), no `useState` manual por campo.

**Por qué:** el manejo manual duplica lógica de validación entre campos y no escala — cada campo nuevo repite el mismo patrón de estado/error a mano.

```tsx
const LoginSchema = z.object({ email: z.string().email(), password: z.string().min(8) });
const { register, handleSubmit, formState: { errors } } = useForm({ resolver: zodResolver(LoginSchema) });
```

### 9.2 Validación en dos capas

**[REQUIRED]** La validación del cliente es solo UX (feedback inmediato) — **nunca** es la única línea de defensa. La validación real vuelve a ocurrir en el backend (ver `05_Security` del handbook).

### 9.3 Estados de formulario

**[REQUIRED]** `idle → submitting → success | error`. El submit se deshabilita durante `submitting` (evita doble-envío).

### 9.4 Accesibilidad de formularios

**[REQUIRED]** Todo input tiene `<label>` asociado (no solo `placeholder`). Errores anunciados vía `aria-describedby` + `aria-invalid`.

---

## 10. CSS Architecture

### 10.1 Un solo enfoque de estilos por proyecto

**[REQUIRED]** No mezclar Tailwind + CSS Modules + styled-components + SCSS en el mismo proyecto. Se elige uno.

### 10.2 Orden de clases determinístico

**[RECOMMENDED]** Formateo automático del orden de clases (ej. `prettier-plugin-tailwindcss`) para que no dependa del criterio de quien escribe.

### 10.3 Variantes declarativas, no condicionales sueltos

**[RECOMMENDED]** Variantes de un componente definidas de forma declarativa (ej. `cva`), no cadenas de `if`/template strings repetidas.

### 10.4 `@apply` con moderación

**[RECOMMENDED]** Solo para patrones de bajo nivel reusados por 10+ elementos, nunca como forma de "no escribir clases en el JSX" — eso reintroduce el problema de estilos desconectados del markup que consumen.

---

## 11. Performance

### 11.1 Presupuesto de bundle

**[RECOMMENDED]** Auditar el tamaño del bundle inicial antes de cada release grande (no solo cuando "se siente lento"). Objetivo orientativo: bundle de entrada liviano — el número exacto depende del proyecto, lo que no se negocia es medirlo, no asumirlo.

### 11.2 Memoización con evidencia, no por defecto

**[REQUIRED]** `useMemo`/`useCallback`/`React.memo` se agregan cuando hay evidencia medida de un problema de rendimiento, no preventivamente en cada componente.

**Por qué:** memoización innecesaria añade complejidad de lectura y en varios casos empeora el rendimiento (comparación de dependencias cuesta más que el render que evita).

### 11.3 Listas largas

**[RECOMMENDED]** Listas con muchos elementos (decenas a cientos) usan virtualización, no renderizan todo el DOM de una vez.

### 11.4 Core Web Vitals como objetivo real

**[REQUIRED]** LCP < 2.5s, INP < 200ms, CLS < 0.1, medidos en condiciones reales (no solo en localhost) antes de marcar una feature grande como terminada.

**Por qué este número no es arbitrario:** son los umbrales que Google usa para clasificar una página como "buena experiencia" y afectan directamente SEO y conversión — no es una preferencia interna, es un estándar de la industria.

---

## 12. Frontend Security

> Detalle ampliado en `05_Security` (pendiente en el handbook). Esto es lo específico de frontend.

### 12.1 Nunca confiar en el cliente

**[REQUIRED]** Toda validación de negocio real (permisos, precios, límites) se re-valida en el backend. El frontend valida solo para UX.

### 12.2 Cero secretos en el bundle

**[REQUIRED]** Ninguna API key privada ni credencial de terceros en código que se compile al cliente. Si algo requiere secreto, esa llamada pasa por el BFF (sección 6.4).

### 12.3 XSS

**[REQUIRED]** Prohibido interpolar HTML de usuario sin sanitizar. `dangerouslySetInnerHTML` (o equivalente) solo con contenido saneado explícitamente y justificado en comentario.

### 12.4 Dependencias

**[RECOMMENDED]** Auditoría de dependencias antes de releases grandes; no agregar paquetes de baja confianza para resolver algo trivial.

---

## 13. Accessibility

> Resumen `REQUIRED` de siempre. Profundidad completa (ARIA, gestión de foco, testing de accesibilidad, `prefers-reduced-motion`) en [FRONTEND_ACCESSIBILITY_STANDARD.md](../UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md) (Nivel 2).

### 13.1 HTML semántico primero

**[REQUIRED]** Elementos nativos (`button`, `a`, `nav`, `main`) sobre `div` con eventos simulados. Un `div` con click sin rol ni soporte de teclado es un bloqueador de accesibilidad. Estándar completo (qué etiqueta usar en cada caso, jerarquía de headings, landmarks) en [FRONTEND_HTML_STRUCTURE_STANDARD.md](FRONTEND_HTML_STRUCTURE_STANDARD.md) (Nivel 2).

### 13.2 Navegación por teclado

**[REQUIRED]** Todo elemento interactivo es alcanzable y operable por teclado, sin trampas de foco. Modales devuelven el foco al cerrarse.

### 13.3 `focus-visible` nunca se elimina sin reemplazo

**[REQUIRED]** Un indicador de foco visible siempre existe para navegación por teclado.

### 13.4 Contraste

**[REQUIRED]** Contraste mínimo WCAG AA (4.5:1 texto normal, 3:1 texto grande), validado al definir la paleta, no al final del proyecto.

**Por qué este número no es arbitrario:** es el estándar internacional de accesibilidad (WCAG 2.1 AA); por debajo de eso, una parte real de usuarios no puede leer el contenido.

### 13.5 Texto alternativo

**[REQUIRED]** `alt` descriptivo en imágenes con significado; `alt=""` explícito en decorativas.

---

## 14. Testing

**[RECOMMENDED]** Pirámide de testing: unit (funciones puras y hooks complejos) > component (Testing Library, para lógica condicional relevante) > e2e (solo golden paths críticos: login, checkout, flujo principal).

**[REQUIRED]** No se persigue % de cobertura como meta — se testea lo que rompe el negocio si falla.

**Por qué:** perseguir un porcentaje produce tests que verifican implementación en vez de comportamiento, y da falsa sensación de seguridad.

**[RECOMMENDED]** No testear: detalles de implementación interna, snapshots exactos de CSS, librerías de terceros ya testeadas.

---

## 15. Git Workflow

**[RECOMMENDED]** Ramas con prefijo + descripción (`feature/order-history`, `fix/login-redirect`).

**[REQUIRED]** Commits en formato Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).

**[RECOMMENDED]** PR revisable en menos de ~20 minutos; features grandes se parten en PRs incrementales.

**[REQUIRED]** Antes de mergear: build, typecheck y lint pasan; sin `console.log` de debug ni código comentado "por si acaso".

---

## 16. Documentation

**[REQUIRED]** Cada repo tiene un `README.md`: qué es, cómo correrlo local (con `.env.example`), stack, dónde está desplegado.

**[RECOMMENDED]** Comentarios solo para el "por qué" no obvio (restricción oculta, workaround de un bug específico) — nunca repitiendo lo que el código ya dice.

**[RECOMMENDED]** Cambios de arquitectura grandes se documentan en 2-3 párrafos (contexto, decisión, consecuencias) — ADR ligero.

---

## 17. Build & Deployment

**[REQUIRED]** `.env.example` versionado sin valores reales; `.env.local`/`.env.production` nunca en git.

**[RECOMMENDED]** Todo PR genera un preview deploy antes de mergear a producción.

**[REQUIRED]** CI mínimo (typecheck + lint + build + tests relevantes) bloqueando el deploy si falla.

---

## Checklist rápido antes de dar por terminado un componente/feature

- [ ] ¿Usa tokens del design system (color/spacing/tipografía), cero valores mágicos? (01)
- [ ] ¿Vive en la carpeta de feature correcta, expone solo API pública? (02, 03)
- [ ] ¿Una responsabilidad clara, UI separada de lógica? (04)
- [ ] ¿Server state y UI/global state nunca mezclados? (05)
- [ ] ¿Toda llamada a datos pasa por el cliente único, con errores normalizados? (06)
- [ ] ¿Tipado estricto, sin `any`, contratos validados en runtime si el dato es externo? (07)
- [ ] ¿Formularios con validación declarativa y estados idle/submitting/success/error? (09)
- [ ] ¿Loading/error/empty/success manejados explícitamente? (04.2)
- [ ] ¿Accesible por teclado, con foco visible, labels y contraste AA? (13)
- [ ] ¿Test si la lógica lo amerita? (14)
- [ ] ¿Commit sigue Conventional Commits? (15)
