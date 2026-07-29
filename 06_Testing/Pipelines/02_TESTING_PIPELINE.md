---
title: "Pipeline de Testing por Capa"
category: 06_Testing
doc_type: estandar
tags: [testing, pipeline, vitest, playwright]
summary: "Estándar técnico capa por capa: unitarios con Vitest, integración de Worker con datos, tests de componente con Testing Library, E2E con Playwright, regresión visual y reglas anti-flakiness."
keywords: [unit, integracion, componentes, e2e, regresion-visual, flaky, pipeline]
updated: 2026-07-21
status: current
---

# 02 — Testing Pipeline: estándar técnico por capa

> **Propósito:** definir CÓMO se escribe cada tipo de test (unit, integration, component, E2E, visual) en el stack actual: React 19 + Vite + TypeScript, Cloudflare Workers, Supabase, PWA. Herramientas: **Vitest** (unit/integration), **Testing Library** (componentes), **Playwright** (E2E + visual).
>
> **Herencia (no se repite aquí):**
> - `02_Backend/BACKEND_ENGINEERING_STANDARD.md` §14 — qué priorizar en backend: lógica de negocio con unit tests independientes del runtime, integración del worker para flujos críticos (auth, pagos, webhooks).
> - `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` §14 — pirámide de testing y el principio "se testea lo que rompe el negocio si falla, no un % como meta".
> - El QUÉ y CUÁNDO a nivel estrategia vive en el documento 01 de esta carpeta; los checklists operativos con comandos en `06_TEST_CHECKLIST.md`.
>
> **Audiencia principal: IAs (Claude Code).** Los tests de este ecosistema los escriben mayormente agentes. Por eso este documento es prescriptivo, con ejemplos completos correctos e incorrectos — un agente debe poder copiar la forma exacta sin inventar convenciones.

---

## 1. Unit tests (Vitest)

### 1.1 Qué se testea a nivel unit — y qué no

**[REQUIRED]** Se escriben unit tests para código con **lógica de decisión propia**:

- Lógica de negocio pura (cálculo de precios, prorrateos, estados de suscripción, reglas de permisos).
- Utils y helpers con ramas (`formatMoney`, parseo de fechas, slugify).
- Validadores y schemas (Zod/validaciones custom): casos válidos, inválidos y bordes.
- Reducers, máquinas de estado y hooks **con lógica** (no hooks que solo envuelven un fetch).

**[REQUIRED]** NO se escriben unit tests para:

- Componentes triviales de render (un `<Badge>` que solo pinta props) — sin ramas no hay nada que romper.
- Tipos de TypeScript — el typecheck ya es ese test.
- Librerías de terceros (no se testea que Zod valide o que Supabase devuelva datos) — ya están testeadas por sus autores.
- Configuración estática (constantes, objetos de config sin lógica).

**Por qué:** cada test tiene costo de mantenimiento. Un test de algo sin lógica no puede fallar por un bug real — solo falla cuando se refactoriza, generando ruido que entrena al equipo (y a las IAs) a ignorar tests rojos. Esto es especialmente crítico con agentes: una IA sin este criterio genera cientos de tests triviales que parecen cobertura y no protegen nada.

### 1.2 Estructura AAA y naming

**[REQUIRED]** Todo test sigue Arrange–Act–Assert, en ese orden, sin mezclar fases. `describe` nombra la **unidad** bajo prueba; `it` describe un **comportamiento en lenguaje de negocio** (qué hace, no cómo lo hace).

**Por qué:** el nombre del test es la especificación viva. `it('devuelve 0 de descuento si el cupón expiró')` documenta la regla de negocio y, cuando falla, dice exactamente qué se rompió. `it('works')` o `it('test calcDiscount 2')` no dicen nada — el que lee el rojo tiene que leer el código del test para entender qué pasó.

```ts
// ✅ Implementación de referencia
describe('calcularDescuento', () => {
  it('aplica el porcentaje del cupón sobre el subtotal', () => {
    // Arrange
    const cupon = buildCupon({ porcentaje: 20 });
    // Act
    const resultado = calcularDescuento(10_000, cupon);
    // Assert
    expect(resultado).toBe(2_000);
  });

  it('devuelve 0 si el cupón expiró', () => {
    const cupon = buildCupon({ expiraEn: new Date('2026-01-01') });
    vi.setSystemTime(new Date('2026-06-01'));
    expect(calcularDescuento(10_000, cupon)).toBe(0);
  });
});
```

### 1.3 Coverage: umbral como piso, no como meta

**[REQUIRED]** Umbral de cobertura en config, aplicado **solo a los directorios de lógica de negocio** (`src/lib`, `src/services` o equivalentes): **80% líneas / 75% branches**. El build de CI falla por debajo. No se configura umbral global sobre todo `src/`.

**Por qué esos números y no 100%:** el objetivo real es que **ninguna rama de lógica de negocio quede sin ejercitar por accidente** — 80/75 sobre los directorios de lógica detecta eso. Perseguir 100% obliga a testear ramas defensivas inalcanzables y getters triviales, produciendo tests que verifican implementación en vez de comportamiento (exactamente lo que `FRONTEND_ENGINEERING_STANDARD.md` §14 prohíbe). Este umbral no contradice ese principio: no es una meta a perseguir, es una **red de seguridad** que detecta cuando una IA agregó lógica sin su test. Si la cobertura real supera el piso, el piso no se sube automáticamente por eso.

```ts
// vitest.config.ts — implementación de referencia
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      include: ['src/lib/**', 'src/services/**'],
      thresholds: { lines: 80, branches: 75 },
    },
  },
});
```

### 1.4 Mocks: cuándo sí y cuándo son síntoma

**[REQUIRED]** Se mockea únicamente lo **no determinista o externo**: red (`fetch`), tiempo (`vi.useFakeTimers()` / `vi.setSystemTime()`), aleatoriedad (`vi.spyOn(Math, 'random')`), y clientes de servicios externos (Supabase, pasarela de pagos) en el borde del sistema.

**[REQUIRED]** Nunca se mockea el módulo bajo prueba ni sus colaboradores internos puros. Si un test necesita 4+ mocks para arrancar, no se escribe el mock número 5: se refactoriza la unidad (la lógica está acoplada a sus dependencias; extraer la función pura y testearla directo).

**Por qué:** un test lleno de mocks internos verifica que el código llama a sus propios mocks — pasa siempre, incluso con el bug presente. La necesidad de mockear mucho es la señal de diseño más fiable que existe: la lógica de negocio debería poder ejecutarse con objetos planos de entrada y salida (mismo principio que backend §14: services testeables sin el runtime de Cloudflare).

### 1.5 Fixtures y factories tipadas

**[REQUIRED]** Los datos de test se construyen con **factories tipadas con overrides parciales**, una por entidad, en `tests/factories/`. Prohibido copy-pastear objetos literales de 15 campos entre tests.

**Por qué:** cuando la entidad gana un campo, con factory se cambia 1 archivo y el typecheck avisa; con literales copiados se editan 40 tests. Además el override hace visible **qué campo importa para este test** — el resto es ruido relleno por la factory.

```ts
// tests/factories/usuario.ts — implementación de referencia
import type { Usuario } from '@/types';

export function buildUsuario(overrides: Partial<Usuario> = {}): Usuario {
  return {
    id: 'usr_test_001',
    email: 'test@ejemplo.com',
    plan: 'free',
    creadoEn: new Date('2026-01-01T00:00:00Z'),
    ...overrides,
  };
}
```

### 1.6 Ejemplo completo: test bueno vs test malo

```ts
// ❌ MALO — mockea la unidad, nombre sin significado, sin AAA, valor mágico copiado
it('test 1', async () => {
  vi.mock('./calcularPlan');
  const spy = vi.spyOn(servicio, 'obtenerPrecio').mockReturnValue(4990);
  const r = await servicio.obtenerPrecio('pro');
  expect(spy).toHaveBeenCalled();   // verifica que el mock fue llamado: no prueba nada
  expect(r).toBe(4990);             // verifica el valor que el propio test inyectó
});

// ✅ BUENO — unidad real, comportamiento de negocio, factory, borde explícito
describe('calcularPrecioPlan', () => {
  it('cobra el plan pro completo cuando no hay días restantes del plan anterior', () => {
    const suscripcion = buildSuscripcion({ plan: 'free' });
    expect(calcularPrecioPlan(suscripcion, 'pro')).toBe(4990);
  });

  it('prorratea el upgrade descontando los días ya pagados del ciclo actual', () => {
    vi.setSystemTime(new Date('2026-06-16')); // mitad del ciclo
    const suscripcion = buildSuscripcion({ plan: 'basic', cicloInicia: new Date('2026-06-01') });
    expect(calcularPrecioPlan(suscripcion, 'pro')).toBe(4990 - 1495); // pro - mitad de basic
  });
});
```

---

## 2. Integration tests (Worker + datos)

### 2.1 Worker completo por request/response

**[REQUIRED]** Los flujos críticos del Worker (auth, pagos, webhooks — herencia de backend §14) se testean **de request a response**, ejecutando el worker real en `workerd` con `@cloudflare/vitest-pool-workers`. **Estándar actual verificado (2026): Vitest 4.1+, plugin `cloudflareTest()` y `exports` de `cloudflare:workers`** — `SELF` está deprecado y `unstable_dev` de Wrangler es legacy: no se usan en código nuevo.

**Por qué:** el unit test del service no cubre routing, middleware de auth, CORS, parseo del body ni el formato del error — que es donde viven la mayoría de los bugs de un endpoint. Ejecutar en `workerd` (no en Node) garantiza que el test corre en el mismo runtime que producción, con los mismos bindings.

```ts
// apps/worker/vitest.config.ts — implementación de referencia
import { defineConfig } from 'vitest/config';
import { cloudflareTest } from '@cloudflare/vitest-pool-workers';

export default defineConfig({
  plugins: [cloudflareTest({ wrangler: { configPath: './wrangler.jsonc' } })],
});
```

```ts
// apps/worker/test/checkout.integration.test.ts
import { exports } from 'cloudflare:workers';
import { describe, it, expect } from 'vitest';

describe('POST /api/checkout', () => {
  it('rechaza la request sin token con 401 y error con code + message', async () => {
    const res = await exports.default.fetch(
      new Request('https://example.com/api/checkout', { method: 'POST' }),
    );
    expect(res.status).toBe(401);
    const body = await res.json();
    expect(body).toMatchObject({ code: 'unauthorized', message: expect.any(String) });
  });

  it('rechaza un body inválido con 400 antes de tocar la lógica de negocio', async () => {
    const res = await exports.default.fetch(
      new Request('https://example.com/api/checkout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${tokenDeTest()}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: 'inexistente' }),
      }),
    );
    expect(res.status).toBe(400);
  });
});
```

### 2.2 Datos: Supabase local vs mock del cliente

**[REQUIRED]** Criterio de decisión explícito:

| Se testea… | Herramienta |
|---|---|
| Lógica del service que USA datos (transformación, decisión) | **Mock del cliente Supabase** (interfaz mínima, no la librería entera) |
| Comportamiento que VIVE en la DB: RLS, constraints, triggers, funciones SQL, queries no triviales | **Supabase local** (`supabase start`) contra la instancia real |

**Por qué:** mockear el cliente para testear una policy de RLS es testear el mock — la policy real nunca se ejecuta y puede estar rota (riesgo directo de fuga de datos, ver backend §13). Al revés, levantar Postgres para verificar que un service formatea una fecha es lentitud gratuita. La frontera es: si el bug posible está en SQL/policies, la DB real es el sujeto del test; si está en TypeScript, el mock basta.

**[RECOMMENDED]** Los tests contra Supabase local siembran sus datos con las mismas factories de §1.5 (insertadas vía cliente con service role local) y limpian por `TRUNCATE` en `beforeEach` — cada test parte de un estado conocido, nunca del estado que dejó el test anterior.

---

## 3. Component tests (Testing Library)

### 3.1 Qué merece test de componente

**[RECOMMENDED]** Se testean componentes con **comportamiento condicional relevante**: formularios con validación, componentes que cambian según rol/estado (empty/loading/error — ver `01_Frontend/FRONTEND_STATES_PATTERNS.md`), interacciones con lógica (wizard, filtros, selección múltiple). No se testean componentes puramente presentacionales (ya excluidos en §1.1).

### 3.2 Queries y eventos

**[REQUIRED]** Las queries localizan elementos **como lo haría un usuario**: por rol accesible (`getByRole`), label (`getByLabelText`) o texto visible. Prohibido query por clase CSS, estructura del DOM (`container.querySelector('.card > div')`) o índice de nodo. `data-testid` solo como último recurso cuando no existe semántica accesible.

**Por qué:** una query por rol/label rompe solo si cambia lo que el usuario percibe — que es exactamente cuándo debe romper. Una query por clase rompe con cada refactor de estilos (falso rojo) y además **no rompe** cuando el botón pierde su label accesible (falso verde): testear por rol es también un test de accesibilidad gratis (refuerza `FRONTEND_ACCESSIBILITY_STANDARD.md`).

**[REQUIRED]** Interacciones con `userEvent` (que dispara la secuencia real de eventos: focus, keydown, input…), no con `fireEvent` directo.

```tsx
// implementación de referencia
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

it('muestra el error de email inválido al enviar y no llama al submit', async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<FormularioRegistro onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'no-es-un-email');
  await user.click(screen.getByRole('button', { name: 'Crear cuenta' }));

  expect(await screen.findByText('Ingresa un email válido')).toBeInTheDocument();
  expect(onSubmit).not.toHaveBeenCalled();
});
```

---

## 4. E2E (Playwright)

### 4.1 Estrategia de suites: smoke vs full

**[REQUIRED]** Dos suites con propósito distinto, separadas por tag:

- **`@smoke` — 5 a 10 flujos que, si fallan, el producto está caído:** registro, login, logout, el flujo core del negocio (lo que el cliente paga por hacer), y el CRUD principal. Corre en **cada deploy** y contra producción post-deploy. Presupuesto: < 5 minutos.
- **Full — todo lo demás** (casos de error, permisos, estados vacíos, viewports secundarios, visual). Corre **nightly y pre-release**.

**Por qué:** una sola suite grande en cada deploy crea la peor combinación: deploys lentos + presión por saltarse los tests. Separar por criticidad da feedback en minutos donde importa (¿puedo cobrar? ¿puede entrar el usuario?) y profundidad donde hay tiempo. El límite de 5–10 en smoke es deliberado: si todo es crítico, nada lo es.

```ts
// e2e/smoke/checkout.spec.ts
test('el usuario puede completar el flujo de compra @smoke', async ({ page }) => { /* … */ });
```

```bash
npx playwright test --grep @smoke        # suite de deploy
npx playwright test --grep-invert @smoke # resto (nightly)
```

### 4.2 Selectores y page objects

**[REQUIRED]** Selectores por rol accesible o `data-testid` — **nunca** clases CSS, XPath ni cadenas de `div > div:nth-child(3)`. Mismo fundamento que §3.2: el selector frágil rompe con cada cambio visual sin detectar bugs reales.

**[RECOMMENDED]** Page objects **ligeros**: funciones helper por página/flujo (`login(page, usuario)`, `crearProyecto(page, datos)`) que encapsulan selectores repetidos. No frameworks de page-object con herencia y estado — para un developer solo son más código que producto.

### 4.3 Auth por storageState [REQUIRED]

**[REQUIRED]** El login por UI se ejecuta **una vez** en un proyecto `setup`; los demás tests reutilizan la sesión vía `storageState`. Prohibido re-loguearse en cada test.

**Por qué:** re-login por test multiplica la duración de la suite (30–60s extra por test) y concentra la flakiness en el punto más frágil (el formulario de auth + Supabase Auth). El login ya tiene su propio test en smoke; repetirlo 40 veces no prueba nada nuevo.

```ts
// e2e/auth.setup.ts — implementación de referencia
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('autenticar usuario de test', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel('Contraseña').fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await page.context().storageState({ path: authFile });
});
```

```ts
// playwright.config.ts (fragmento)
projects: [
  { name: 'setup', testMatch: /auth\.setup\.ts/ },
  {
    name: 'desktop-1280',
    use: { viewport: { width: 1280, height: 800 }, storageState: 'playwright/.auth/user.json' },
    dependencies: ['setup'],
  },
],
```

`playwright/.auth/` va en `.gitignore` — es una sesión real, no se comitea.

### 4.4 Qué cubre la suite E2E (catálogo obligatorio)

**[REQUIRED]** La suite full cubre, para cada área del producto donde apliquen:

- **Formularios con validación:** submit válido, submit con campos inválidos (mensaje visible), doble submit bloqueado.
- **Modales:** abrir, confirmar, cancelar, cerrar con Escape (ver `FRONTEND_MODALS_PATTERNS.md`).
- **Estados vacíos y loading:** primera visita sin datos muestra el empty state, no un layout roto.
- **Errores de servidor:** mock de 500 con route interception — la UI muestra el error diseñado, no pantalla blanca:

```ts
test('muestra error amigable si la API de proyectos devuelve 500', async ({ page }) => {
  await page.route('**/api/projects', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ code: 'internal_error', message: 'Algo salió mal' }),
    }),
  );
  await page.goto('/proyectos');
  await expect(page.getByText('No pudimos cargar tus proyectos')).toBeVisible();
});
```

- **Rutas privadas:** visitar `/dashboard` sin sesión (test SIN `storageState`) redirige a `/login`.
- **404:** ruta inexistente muestra la página 404 diseñada (`FRONTEND_ERROR_PAGES_STANDARD.md`).
- **Permisos/roles:** un rol sin permiso no ve la acción restringida ni puede navegar directo a su URL.
- **Uploads/downloads:** `setInputFiles()` para subir; `page.waitForEvent('download')` para verificar descarga.

### 4.5 Matriz de viewports [REQUIRED]

**[REQUIRED]** La suite smoke corre en exactamente **3 anchos: 375px (mobile), 768px (tablet), 1280px (desktop)** — configurados como proyectos de Playwright.

**Por qué 3 y no 10:** los breakpoints del CSS del sistema son 3 (`FRONTEND_RESPONSIVE_STANDARD.md`); el layout solo puede cambiar al cruzar un breakpoint, así que testear 10 anchos es testear 7 veces el mismo layout. El objetivo es 1 ancho representativo por rango de breakpoint; si mañana el CSS gana un cuarto breakpoint, la matriz gana un cuarto ancho — el número sigue al CSS, no al revés.

### 4.6 Dark/light mode

**[RECOMMENDED]** Los flujos smoke se ejecutan al menos una vez con `colorScheme: 'dark'` emulado, verificando que el contenido crítico es visible (los bugs típicos: texto oscuro sobre fondo oscuro, ilustraciones invisibles).

```ts
await page.emulateMedia({ colorScheme: 'dark' });
```

### 4.7 PWA / offline

**[REQUIRED]** Toda ruta que el producto **promete** que funciona offline tiene un test que lo verifica; las que no lo prometen, no se testean offline.

```ts
test('el dashboard cacheado carga sin conexión', async ({ page, context }) => {
  await page.goto('/dashboard');                       // primera visita: puebla el cache del SW
  await page.waitForLoadState('networkidle');
  await context.setOffline(true);
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

**Por qué:** el service worker es de lo más difícil de verificar a mano (caches viejos, estados intermedios) y romperlo es silencioso — sin test, la promesa offline de la PWA se degrada sin que nadie lo note.

### 4.8 Errores de consola y requests fallidos como assertion global [REQUIRED]

**[REQUIRED]** Un fixture automático colecciona errores de consola, `pageerror` y requests fallidos durante cada test E2E y **falla el test** si hubo alguno no permitido explícitamente.

**Por qué:** un test puede pasar sus assertions mientras la página escupe errores de JS o 404s de assets — bugs reales que ninguna assertion puntual mira. Convertirlos en assertion global detecta la clase entera de bugs sin escribir un test por cada uno.

```ts
// e2e/fixtures.ts — implementación de referencia
import { test as base, expect } from '@playwright/test';

export const test = base.extend<{ vigilarErrores: void }>({
  vigilarErrores: [
    async ({ page }, use) => {
      const errores: string[] = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') errores.push(`console: ${msg.text()}`);
      });
      page.on('pageerror', (err) => errores.push(`pageerror: ${err.message}`));
      page.on('requestfailed', (req) => {
        if (req.failure()?.errorText !== 'net::ERR_ABORTED')
          errores.push(`request: ${req.url()} → ${req.failure()?.errorText}`);
      });
      await use();
      expect(errores, `Errores detectados en la página:\n${errores.join('\n')}`).toEqual([]);
    },
    { auto: true },
  ],
});

export { expect };
```

(Los tests que mockean un 500 a propósito — §4.4 — registran esa URL como permitida o no usan el fixture.)

### 4.9 Links rotos

**[RECOMMENDED]** Un test de crawl ligero: recorre los links internos de la navegación principal y el sitemap (si existe) y verifica que ninguno responde ≥400. No es un crawler completo — solo nav + footer + sitemap, suficiente para atrapar la ruta renombrada que dejó links muertos.

```ts
test('los links de la navegación no están rotos', async ({ page, request }) => {
  await page.goto('/');
  const hrefs = await page.locator('nav a[href^="/"], footer a[href^="/"]').evaluateAll(
    (as) => [...new Set(as.map((a) => (a as HTMLAnchorElement).getAttribute('href')!))],
  );
  for (const href of hrefs) {
    const res = await request.get(href);
    expect(res.status(), `Link roto: ${href}`).toBeLessThan(400);
  }
});
```

---

## 5. Visual regression (Playwright screenshots)

### 5.1 Qué páginas ameritan snapshot visual

**[RECOMMENDED]** Snapshot visual solo para: la landing (la cara comercial), el dashboard base (la pantalla más vista del producto), y los componentes de UI críticos del design system (botones, cards, formularios — una página de galería). **No** cada página del producto.

**Por qué:** cada snapshot es un archivo que alguien debe re-aprobar en cada cambio visual legítimo. Con 50 snapshots, cada ajuste de espaciado genera 50 diffs y la aprobación se vuelve un "aceptar todo" mecánico — que es exactamente el estado en el que un bug visual real pasa inadvertido. Pocos snapshots de alto valor mantienen la aprobación como un acto de revisión real.

### 5.2 Mecánica

**[REQUIRED]** `toHaveScreenshot()` con tolerancia explícita (`maxDiffPixelRatio: 0.02` como default del proyecto — suficiente para absorber antialiasing sin dejar pasar cambios de layout) y animaciones deshabilitadas. Los snapshots base se **versionan en el repo** junto a los tests.

```ts
// playwright.config.ts (fragmento)
expect: {
  toHaveScreenshot: { maxDiffPixelRatio: 0.02, animations: 'disabled' },
},
```

```ts
// e2e/visual/landing.spec.ts
test('la landing no cambió visualmente @visual', async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => document.fonts.ready);   // fonts cargadas antes del shot
  await expect(page).toHaveScreenshot('landing.png', { fullPage: true });
});
```

### 5.3 Estabilización [REQUIRED]

**[REQUIRED]** Antes de cada screenshot: animaciones off (config §5.2), `document.fonts.ready` esperado, y **datos deterministas** — la página del snapshot se alimenta con datos fijos (route interception con fixture JSON o usuario seed), nunca con datos vivos que cambian entre corridas. Fechas relativas ("hace 3 días") se congelan fijando el reloj o los datos.

**Por qué:** un snapshot con datos vivos falla cada día por razones que no son bugs, y un test que falla sin bug se termina ignorando o borrando — perdiendo la protección que motivó crearlo.

**[RECOMMENDED]** Los snapshots base se generan en el mismo entorno donde se comparan (CI Linux), no en la máquina local Windows — el rendering de fuentes difiere entre OS y produce diffs falsos permanentes. En la práctica: los tests `@visual` corren solo en CI, y la base se regenera con un job de CI, no localmente.

### 5.4 Flujo de aprobación de cambios

**[REQUIRED]** Cuando un cambio visual es intencional: (1) se revisa el diff que reporta Playwright (imagen actual vs esperada vs diff), (2) solo tras confirmar que el cambio es el buscado se regeneran las bases con `npx playwright test --grep @visual --update-snapshots`, (3) los snapshots actualizados se comitean **en el mismo commit** que el cambio de UI que los causó.

**Por qué:** `--update-snapshots` sin revisar el diff convierte el sistema en un sello de goma: aprueba cualquier cosa, incluido el bug. El commit conjunto deja en el historial la correspondencia cambio ↔ nueva base.

---

## 6. Anti-flakiness [REQUIRED]

**[REQUIRED]** Reglas no negociables para toda la suite:

1. **Web-first assertions con auto-wait.** Toda espera se expresa como assertion sobre el estado esperado (`await expect(locator).toBeVisible()`), que reintenta hasta el timeout. Prohibido `page.waitForTimeout(n)` — un sleep fijo es o demasiado corto (flaky) o demasiado largo (suite lenta), y casi siempre ambas cosas en máquinas distintas.

2. **Datos deterministas.** Los tests generan sus propios datos con seed conocido (factories §1.5, usuario E2E dedicado) y no dependen de estado dejado por otros tests ni de datos "que suelen estar" en el entorno. Cada test debe poder correr solo y en cualquier orden.

3. **Retries: 2 en CI, 0 en local.** `retries: process.env.CI ? 2 : 0`. En CI el retry absorbe fallas de infraestructura (red del runner, cold start); en local el fallo debe verse a la primera para depurarlo.

4. **Política de flaky:** un test que **necesitó** retry para pasar queda marcado (Playwright lo reporta como `flaky`) y se abre la tarea de arreglarlo esa misma semana. Si no se puede arreglar, **se borra**. Un test flaky tolerado enseña a ignorar los rojos, y ese hábito es más caro que no tener el test.

**Por qué la sección entera es REQUIRED:** la suite solo sirve si un rojo significa "hay un bug" el 100% de las veces. Con IAs escribiendo y ejecutando los tests el punto es aún más duro: un agente que aprende que "a veces falla porque sí" empezará a reintentar o descartar fallos legítimos.

```ts
// playwright.config.ts — implementación de referencia completa (fragmento)
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',
  retries: process.env.CI ? 2 : 0,
  forbidOnly: !!process.env.CI,
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.02, animations: 'disabled' } },
});
```

---

## Checklist final (mismo orden que las secciones)

- [ ] ¿Los unit tests cubren solo código con lógica de decisión, ninguno trivial? (§1.1)
- [ ] ¿AAA + `describe` = unidad, `it` = comportamiento de negocio? (§1.2)
- [ ] ¿Umbral 80/75 en config sobre los directorios de lógica, y CI falla por debajo? (§1.3)
- [ ] ¿Mocks solo de red/tiempo/random/servicios externos — y ningún test con 4+ mocks? (§1.4)
- [ ] ¿Datos de test vía factories tipadas, cero objetos copy-paste? (§1.5)
- [ ] ¿Flujos críticos del Worker testeados request→response con `cloudflareTest()` + `exports`? (§2.1)
- [ ] ¿RLS/constraints/SQL testeados contra Supabase local, no contra mocks? (§2.2)
- [ ] ¿Component tests con queries por rol/label y `userEvent` — nunca clases CSS? (§3)
- [ ] ¿Suite `@smoke` de 5–10 flujos < 5 min, separada de la full? (§4.1)
- [ ] ¿Selectores E2E por rol o testid, helpers ligeros? (§4.2)
- [ ] ¿Auth con `storageState` reutilizado vía proyecto setup? (§4.3)
- [ ] ¿Cubiertos: validación, modales, vacíos, loading, 500 mockeado, rutas privadas, 404, roles, uploads? (§4.4)
- [ ] ¿Smoke en 375/768/1280, dark mode emulado, offline donde se promete? (§4.5–4.7)
- [ ] ¿Fixture global de errores de consola/requests fallidos activo? (§4.8)
- [ ] ¿Snapshots visuales solo de páginas de alto valor, estabilizados, versionados, aprobados con revisión de diff? (§5)
- [ ] ¿Cero `waitForTimeout`, datos deterministas, retries 2 en CI, flaky arreglado o borrado? (§6)
