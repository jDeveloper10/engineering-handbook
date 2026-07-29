---
title: "Estándar de TypeScript en Frontend"
category: 01_Frontend
tags: [frontend, typescript, tipos, zod]
summary: "Configuración base de tsconfig y reglas de tipado: prohibición de any con sus alternativas, tipos de dominio derivados y nunca redeclarados, props, eventos y la decisión entre type e interface."
keywords: [typescript, tsconfig, any, unknown, zod, props, type, interface]
updated: 2026-07-27
status: current
---

# FRONTEND TYPESCRIPT STANDARD

> Nivel 2 del handbook. Depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, en especial su sección 07 — TypeScript Rules) y sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). **Nada de lo que el Nivel 1 ya regula se repite** — se declara "hereda de Frontend §X" y se profundiza.
>
> Lo que ya está resuelto arriba y aquí solo se referencia: TS obligatorio desde el primer commit (Frontend §7.1), `strict: true` (§7.2), prohibición de `any` (§7.3), criterio base `type` vs `interface` (§7.4), discriminated unions para estados de fetch (§7.5), no duplicar tipos entre capas (§7.6), naming de tipos (§3.1), validación runtime en bordes (§6.2).
>
> Alcance: configuración del compilador, cómo fluyen los tipos del dominio desde los contratos, y los patrones de tipado que una IA debe usar por defecto al escribir componentes React.

---

## 01. `tsconfig` base

### 1.1 Flags obligatorias

**[REQUIRED]** `strict: true` **hereda de Frontend §7.2**. Además, todo proyecto frontend activa estas flags — cada una con su porqué, porque una IA que no entiende el motivo tiende a "resolver" el error apagando la flag:

```jsonc
// tsconfig.json — base de todo proyecto frontend
{
  "compilerOptions": {
    "strict": true,                       // hereda de Frontend §7.2
    "noUncheckedIndexedAccess": true,     // 1.1.a
    "verbatimModuleSyntax": true,         // 1.1.b
    "noEmit": true,                       // 1.1.c — Vite/esbuild transpila; tsc solo chequea
    "skipLibCheck": true                  // 1.1.d
  }
}
```

**a) `noUncheckedIndexedAccess`** — el acceso por índice (`items[0]`, `record[key]`) tipa como `T | undefined`, no `T`.
**Por qué:** sin la flag, el compilador miente: `items[0]` puede ser `undefined` en runtime pero tipa `T`, y el crash aparece como `cannot read properties of undefined` en producción. Con la flag, el compilador obliga a decidir el caso vacío en cada acceso — que es exactamente el estado "empty" que Frontend §4.2 ya obliga a manejar en UI, ahora garantizado por el compilador.

**b) `verbatimModuleSyntax`** — los imports que solo son tipos se escriben `import type { ... }`, y el compilador lo verifica.
**Por qué:** Vite/esbuild transpilan archivo por archivo sin analizar el grafo completo; un import de tipo escrito como import de valor puede quedar en el bundle, arrastrar un módulo entero que debía desaparecer, o crear ciclos de import en runtime que no existen en tipos. La flag hace explícito y verificable qué se borra al compilar.

**c) `noEmit: true`** — `tsc` es solo el verificador; quien emite JS es Vite.
**Por qué:** dos emisores producen dos verdades. El `typecheck` del CI (hereda de Frontend §17) es `tsc --noEmit`.

**d) `skipLibCheck: true`** — no re-chequear los `.d.ts` de `node_modules`.
**Por qué:** los conflictos entre tipos de terceros no son accionables desde este repo y su chequeo multiplica el tiempo de CI. El código propio sigue chequeado completo.

### 1.2 Flags recomendadas

**[RECOMMENDED]** `noFallthroughCasesInSwitch` (los `switch` sobre uniones de la sección 08 no caen en silencio) y `erasableSyntaxOnly` (TS ≥5.8; prohíbe la sintaxis con emisión propia — `enum`, namespaces con valores, parameter properties — haciendo cumplir por compilador la sección 08). `exactOptionalPropertyTypes` queda a criterio por proyecto: es la más estricta con `?`, pero fricciona con librerías que no la adoptan — si se activa, se activa desde el commit 1, no a mitad de proyecto.

**[REQUIRED]** Las flags no se apagan para silenciar un error puntual. Si un archivo de borde necesita una excepción, se resuelve en ese archivo (sección 09), nunca bajando el `tsconfig` de todo el proyecto.

---

## 02. Prohibido `any` — las alternativas

La prohibición **hereda de Frontend §7.3** (incluida su única excepción documentada con `TODO`). Este documento fija **qué se escribe en su lugar**, porque "no uses any" sin alternativa produce `as` en cascada, que es peor:

### 2.1 `unknown` + narrowing en los bordes

**[REQUIRED]** Todo dato cuyo tipo real no se conoce en compile-time (respuesta de red, `JSON.parse`, `catch`, `postMessage`, localStorage) entra como `unknown` y se estrecha antes de usarse:

```ts
// Borde de red → schema zod del contrato (la vía normal — ver sección 03)
const data: unknown = await res.json();
const order = orderSchema.parse(data); // Order tipado y validado

// catch — el error SIEMPRE es unknown, nunca se asume Error
try { ... } catch (err: unknown) {
  const appError = normalizeError(err); // Frontend §6.3 — de unknown a AppError
}

// Narrowing manual solo donde no hay schema (datos internos triviales)
if (typeof value === "string") { /* value: string */ }
if (value instanceof Date) { /* value: Date */ }
```

> **`catch (err: any)` NO es una excepción tolerada — es una violación de `FE-001`.** Se aclara
> explícitamente porque es el error más repetido: el tipo de la cláusula `catch` es `unknown` en
> modo estricto, y anotarlo como `any` para poder leer `err.message` sin narrowing desactiva el
> compilador justo en el camino de error, que es donde menos se testea. La forma correcta es
> `catch (err: unknown)` + `normalizeError(err)`, como arriba.

**Por qué `unknown` y no `any`:** `any` desactiva el compilador hacia afuera — se propaga por cada expresión que lo toca y el error explota lejos de su origen. `unknown` es la misma flexibilidad de entrada pero el compilador **obliga** a demostrar el tipo antes de usarlo: el costo de la validación queda en el borde, donde pertenece.

### 2.2 Genéricos en vez de `any` en funciones

**[REQUIRED]** Una función que opera sobre "cualquier tipo" preservándolo usa un genérico, no `any`:

```ts
// ❌ pierde el tipo: el caller recibe any
function firstOrNull(items: any[]): any { return items[0] ?? null; }
// ✅ lo preserva
function firstOrNull<T>(items: T[]): T | null { return items[0] ?? null; }
```

**[RECOMMENDED]** Genéricos con la mínima restricción necesaria (`<T extends { id: string }>` si solo se usa `id`), y sin genéricos que se usan una sola vez en la firma — un `<T>` que no conecta dos posiciones de la firma no aporta información y se reemplaza por el tipo concreto o `unknown`.

---

## 03. Tipos del dominio: derivados, nunca redeclarados

**Hereda de Frontend §7.6** (los tipos generados son la fuente de verdad) y de **API §08** (los schemas zod compartidos son el contrato único frontend↔workers). Este documento fija la mecánica en frontend:

### 3.1 Dos fuentes, cero copias manuales

**[REQUIRED]** Todo tipo de dominio del frontend proviene de una de dos fuentes, por `import` — nunca se redeclara su shape a mano:

| Dato | Fuente de verdad | Cómo se consume |
|---|---|---|
| Contratos de API (request/response, `error.code`s) | Schemas zod en `shared/contracts/` | `z.infer<typeof schema>` — el paquete exporta el tipo junto al schema |
| Filas/vistas de base de datos | Tipos generados por Supabase (`database.types.ts`, regenerado por CLI) | `Tables<"orders">`, `TablesInsert<"orders">` |

```ts
// ❌ Redeclarado a mano — divergirá en silencio del contrato real
interface Order { id: string; amount: number; status: string }

// ✅ Derivado de la fuente
import { orderSchema, type Order } from "shared/contracts/orders"; // Order = z.infer<typeof orderSchema>
import type { Tables } from "@/shared/types/database.types";
type ProfileRow = Tables<"profiles">;
```

**Por qué:** una copia manual compila hoy y miente mañana — cuando el Worker agrega un campo o la migración cambia una columna, el tipo copiado no se entera y el bug aparece como `undefined` en producción (el porqué completo en API §08). El `import` convierte cada cambio de contrato en un error de compilación en el lugar exacto a corregir.

### 3.2 Tipos de UI derivados del dominio

**[REQUIRED]** Cuando la UI necesita una variación de un tipo de dominio (menos campos, campos calculados), se **deriva** con utility types (sección 07) desde el tipo fuente — heredando así sus cambios futuros — y vive en el `types.ts` del feature (React Standard §1.2):

```ts
// features/orders/types.ts
import type { Order } from "shared/contracts/orders";
export type OrderSummary = Pick<Order, "id" | "status" | "amount">;
export type OrderWithTotals = Order & { formattedTotal: string };
```

---

## 04. Props de componentes

**Hereda de Frontend §4.4** (interface explícita, nunca `any`, máximo ~7 props) y **§3.1** (PascalCase). Este documento agrega la forma exacta:

### 4.1 Interface con nombre, exportada

**[REQUIRED]** Las props de todo componente se declaran en una `interface` con nombre `<Componente>Props`, **exportada** desde el archivo del componente. Prohibido el tipo inline anónimo en la firma para componentes no triviales.

**Por qué exportada:** los consumidores legítimos (tests, wrappers, Storybook, otro componente que reenvía props) la importan en vez de redeclarar el shape — la redeclaración local de props ajenas es la versión en miniatura del anti-patrón de la sección 03.

### 4.2 `children` tipado explícito

**[REQUIRED]** Si el componente acepta children, la interface lo declara: `children: React.ReactNode` (o `ReactNode | undefined` explícito si es opcional). No se usa `React.FC` para obtenerlo implícito ni se deja sin tipar.

**Por qué:** `children` implícito no dice si el componente lo renderiza o lo ignora; explícito, la interface es el contrato completo. Si children debe ser algo más restringido (una función render-prop: `children: (item: T) => ReactNode`), el tipo lo documenta y el compilador lo exige.

### 4.3 Variantes excluyentes: discriminated union, no booleanas combinables

**[REQUIRED]** Extiende **Frontend §7.5** (que lo aplica a estados de fetch) a las props: cuando un componente tiene modos mutuamente excluyentes, las props se modelan como union discriminada — nunca como booleanas u opcionales combinables que permiten estados imposibles. Es la contraparte de tipos de la señal "3+ booleanas" de React Standard §2.1.

```tsx
// ❌ El compilador acepta <Alert dismissible onDismiss={undefined}> y <Alert href="#" onClick={...}>
export interface AlertProps {
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;   // ¿requerido si dismissible? el tipo no lo dice
  href?: string;            // ¿link o botón? ambiguo
  onClick?: () => void;
}

// ✅ Cada variante declara exactamente lo que necesita; las mezclas no compilan
export type AlertProps = { message: string } & (
  | { kind: "static" }
  | { kind: "dismissible"; onDismiss: () => void }
  | { kind: "link"; href: string }
);

function Alert(props: AlertProps) {
  switch (props.kind) {
    case "dismissible": return /* props.onDismiss existe y es requerido aquí */;
    case "link":        return /* props.href existe; onDismiss ni siquiera tipa */;
    case "static":      return /* ... */;
  }
}
```

**Por qué:** con opcionales combinables, los estados inválidos se descubren en runtime o en review; con la union, **no compilan** — y una IA que consume el componente recibe del propio tipo la lista cerrada de variantes válidas, sin leer la implementación.

---

## 05. Eventos y handlers tipados

**[REQUIRED]** Todo handler tipa su evento con los tipos de React parametrizados por el elemento — nunca `(e: any)` ni el parámetro sin tipo (que con `strict` es error, no se "resuelve" con `any`):

```tsx
function handleClick(e: React.MouseEvent<HTMLButtonElement>) { ... }
function handleChange(e: React.ChangeEvent<HTMLInputElement>) { ... }   // e.target.value tipa string
function handleSubmit(e: React.FormEvent<HTMLFormElement>) { e.preventDefault(); ... }
function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) { ... }
```

**[RECOMMENDED]** Dos simplificaciones válidas: (a) si el handler no usa el evento, se omite el parámetro (`onClick={() => setOpen(true)}`); (b) si el handler es inline, TS infiere el tipo del evento por contexto y no hace falta anotarlo.

**[REQUIRED]** Los handlers que un componente recibe por props se tipan con la semántica del dominio, no re-exponiendo el evento DOM sin necesidad: `onSelect: (orderId: string) => void` mejor que `onSelect: (e: React.MouseEvent) => void`. El naming `onX`/`handleX` hereda de Frontend §3.1.

**Por qué:** un evento tipado da autocompletado y chequeo sobre `target`/`currentTarget`; un handler de prop tipado por dominio desacopla al padre del detalle de DOM del hijo — el padre no debería romperse porque el hijo cambió un `<button>` por un `<div role="button">`.

---

## 06. `type` vs `interface`

El criterio **hereda de Frontend §7.4**: `interface` para shapes de objetos y props; `type` para uniones, tuplas y derivados. Este documento solo agrega los desempates que el Nivel 1 no cubre:

**[RECOMMENDED]**
- Un shape que **es** una union (como `AlertProps` en 4.3) se declara con `type` — las interfaces no expresan uniones; la union gana sobre la preferencia por interface.
- Extensión: `interface X extends Y` sobre intersecciones `&` encadenadas cuando se extiende un shape — los errores del compilador son más legibles y la intención más clara.
- No se aprovecha la declaration merging de `interface` como feature (redeclarar para "agregar" campos): si un tipo necesita crecer, se edita su declaración única. Merging solo para augmentar módulos de terceros, con comentario.

**Por qué existe un criterio fijo:** técnicamente son intercambiables en el 90% de los casos — precisamente por eso, sin regla cada archivo elige distinto y el repo pierde la uniformidad que hace el código predecible para la siguiente generación (humana o IA).

---

## 07. Utility types: derivar, no duplicar

**[REQUIRED]** Cuando un tipo es "como T pero con menos/más/opcional", se deriva del tipo fuente con utility types — nunca se escribe a mano un shape paralelo que repita campos de otro tipo:

| Necesidad | Se escribe | Nunca |
|---|---|---|
| Subconjunto de campos | `Pick<Order, "id" \| "status">` | interface nueva copiando 2 campos |
| Todo menos algunos campos | `Omit<Order, "internalNotes">` | copia con campos borrados |
| Todo opcional (patch/draft) | `Partial<TablesUpdate<"orders">>` | copia con `?` en cada campo |
| Mapa por clave | `Record<OrderStatus, string>` | objeto tipado a mano por cada status |
| Valor de una union por clave | `Extract<AlertProps, { kind: "link" }>` | redeclarar la variante |

**Por qué:** un tipo derivado se actualiza solo cuando cambia la fuente (renombrar un campo de `Order` corrige o rompe compilación en cada derivado — visible); una copia manual queda desincronizada en silencio. Es la sección 03 aplicada dentro del propio frontend.

**[RECOMMENDED]** `Parameters<>`/`ReturnType<>` solo para tipos de terceros que no exportan el tipo que necesitás — para código propio, se exporta el tipo con nombre en lugar de excavarlo de una firma (el tipo excavado produce errores ilegibles y acopla al orden de parámetros).

---

## 08. Enums: no usar — union de literales

**[REQUIRED]** Prohibido `enum` (y `const enum`). Los conjuntos cerrados de valores se modelan como union de literales; si además se necesita iterar los valores en runtime, la fuente es un array `as const` (o el `z.enum` del contrato, que ya provee ambos):

```ts
// ❌ enum
enum OrderStatus { Pending = "pending", Paid = "paid", Failed = "failed" }

// ✅ union de literales (solo tipos)
type OrderStatus = "pending" | "paid" | "failed";

// ✅ cuando hace falta la lista en runtime (un <select>, un map de labels)
const ORDER_STATUSES = ["pending", "paid", "failed"] as const;
type OrderStatus = (typeof ORDER_STATUSES)[number];

// ✅ y si el valor viene del contrato, ya existe: z.enum de shared/contracts (API §08)
type OrderStatus = z.infer<typeof orderSchema>["status"];
```

**Por qué:**
1. **`enum` emite JavaScript** — es de las pocas construcciones de TS que no se borran al compilar. Rompe la premisa "TS = JS + tipos", genera código en el bundle, y es incompatible con `erasableSyntaxOnly` (sección 1.2) y hostil a la transpilación aislada de Vite/esbuild — `const enum`, directamente, no funciona de forma segura con transpiladores archivo-a-archivo.
2. **La union es estructural:** una función que acepta `OrderStatus` acepta el literal `"paid"` directo; con enum hay que importar el enum en cada call site para pasar `OrderStatus.Paid` — fricción sin ganancia de seguridad.
3. **Coherencia con el contrato:** los `error.code`s y los valores cerrados del API ya viajan como literales de `z.enum` (API §03 y §08) — usar `enum` en frontend crearía la segunda declaración paralela que la sección 03 prohíbe.

**[RECOMMENDED]** Para exhaustividad al ramificar sobre la union: `switch` con chequeo de agotamiento (`default: { const _exhaustive: never = value; }` o helper `assertNever`) — agregar un literal nuevo rompe la compilación en cada `switch` que no lo maneja, que es el comportamiento deseado.

---

## 09. Assertions (`as`): solo en la frontera, con comentario

**[REQUIRED]** `as` (y `as unknown as`, y `!` non-null) están prohibidos en lógica de aplicación. Se admiten **solo en la frontera con lo no tipado** — donde el conocimiento del tipo existe pero el compilador no puede verlo — y **siempre con un comentario de una línea que explica por qué la assertion es verdadera**:

```ts
// ✅ Frontera admitida — el compilador no puede saberlo, el comentario lo justifica
// import.meta.env no está tipado por defecto; validado no-vacío 2 líneas abajo (Frontend §6.5)
const apiUrl = import.meta.env.VITE_API_URL as string;

// getElementById tipa Element|null; #root existe en index.html y es el mount de la SPA
const root = document.getElementById("root") as HTMLElement;

// ❌ Prohibido — "as" para callar al compilador dentro de la app
const order = (await res.json()) as Order;        // esto se hace con schema.parse (sección 03)
const item = items.find(isActive) as Item;        // esto es narrowing o manejo del undefined
```

**Jerarquía de preferencia antes de llegar a `as`:** (1) validación runtime con el schema si el dato es externo (hereda de Frontend §6.2), (2) narrowing con type guard, (3) `satisfies` cuando el objetivo es *verificar* que un valor cumple un tipo sin ensancharlo ni forzarlo — `satisfies` chequea, `as` afirma sin chequear:

```ts
// ✅ satisfies: valida el shape y conserva los tipos literales — errores visibles, cero riesgo
const STATUS_LABELS = { pending: "Pendiente", paid: "Pagada", failed: "Fallida" } satisfies Record<OrderStatus, string>;
```

**Por qué:** cada `as` es una promesa que el compilador no verifica — es el único punto del sistema de tipos donde el error de tipos vuelve a ser posible en runtime. Concentrarlos en la frontera y comentarlos los vuelve auditables: al depurar un tipo mentiroso, la lista de sospechosos es corta y cada uno explica su coartada.

---

## Checklist rápido — TypeScript de un feature terminado

- [ ] ¿`tsconfig` con `strict` + `noUncheckedIndexedAccess` + `verbatimModuleSyntax` + `noEmit`, sin flags apagadas para silenciar errores? (01)
- [ ] ¿Cero `any` — bordes con `unknown` + schema/narrowing, funciones genéricas donde se preserva tipo? (02)
- [ ] ¿Todo tipo de dominio importado de `shared/contracts/` (`z.infer`) o de los tipos generados de Supabase — ninguno redeclarado a mano? (03)
- [ ] ¿Props en `interface` `<Componente>Props` exportada, `children: ReactNode` explícito? (04)
- [ ] ¿Variantes excluyentes como discriminated union — cero combinaciones imposibles que compilen? (04)
- [ ] ¿Eventos con `React.XEvent<Elemento>`, handlers de props tipados por dominio? (05)
- [ ] ¿`type`/`interface` según el criterio de Frontend §7.4 y los desempates de la sección 06? (06)
- [ ] ¿Tipos "como T pero..." derivados con Pick/Omit/Partial/Record — cero shapes paralelos copiados? (07)
- [ ] ¿Cero `enum` — uniones de literales, `as const` cuando hace falta runtime, exhaustividad con `never`? (08)
- [ ] ¿Cada `as`/`!` solo en frontera, con comentario que lo justifica; `satisfies` donde solo hay que verificar? (09)
