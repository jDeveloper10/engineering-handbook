---
title: "Guía de Automatización de QA"
category: 06_Testing
tags: [testing, automatizacion, setup, vitest, playwright]
summary: "Setup de QA copy-paste en menos de una hora: estructura de carpetas de tests, scripts de package.json como contrato, y configuración de Vitest, Playwright, ESLint y Lighthouse."
keywords: [setup, vitest, playwright, eslint, lighthouse, scripts, automatizacion]
updated: 2026-07-27
status: current
---

# 07 — AUTOMATION GUIDE: SETUP QA COPY-PASTE (<1 HORA)

> Documento del dominio Testing (06). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Este es el documento **operativo**: dota a cualquier proyecto nuevo del stack (React+Vite+TS, Workers, Supabase) del sistema QA completo en menos de una hora, copiando y ajustando lo mínimo. Los criterios de *qué* testear y los umbrales de calidad viven en los demás documentos de esta carpeta (estrategia, [08_QUALITY_STANDARDS.md](../Strategy/08_QUALITY_STANDARDS.md)); los workflows que consumen esto viven en [03_CI_CD.md](../Pipelines/03_CI_CD.md).
>
> Regla madre de este documento — **[REQUIRED]: mismos nombres, mismas rutas, mismas configs en todos los proyectos.** Un proyecto donde `npm run check` no existe o los tests viven en otra carpeta rompe los workflows de CI, la memoria muscular y a cualquier IA que trabaje sobre el repo asumiendo el estándar.

---

## 01. Estructura de carpetas de tests

**[REQUIRED]** Todo proyecto usa esta estructura — los workflows, las configs de abajo y los globs de coverage la asumen:

```
proyecto/
├── src/                         # código de la app
├── tests/
│   ├── unit/                    # unit + integration (Vitest) — espeja src/: tests/unit/lib/dates.test.ts prueba src/lib/dates.ts
│   ├── e2e/                     # E2E (Playwright) — *.spec.ts; smoke tests etiquetados @smoke en el título
│   ├── fixtures/                # datos de prueba compartidos (JSON, builders) — NUNCA datos reales de usuarios
│   └── setup.ts                 # setup global de Vitest (jest-dom, mocks globales)
├── eslint.config.js
├── vitest.config.ts
├── playwright.config.ts
├── lighthouserc.json
└── .gitleaks.toml
```

**Por qué `tests/` separado y no `*.test.ts` junto al código:** ambos funcionan; se estandariza uno para que sea idéntico en todos los repos. `tests/` separado hace triviales los globs de tooling (coverage solo mide `src/`, E2E y unit no se pisan) y deja `src/` como "solo código que shippea". Lo importante no es la opción — es que sea la misma siempre. `fixtures/` con datos reales es un incidente de privacidad esperando el `git push` — datos sintéticos siempre.

---

## 02. Scripts de `package.json` — el contrato

**[REQUIRED]** Estos nombres son **idénticos en todos los proyectos** — son el contrato que consumen los workflows de [03_CI_CD.md](../Pipelines/03_CI_CD.md), los git hooks (sección 08) y tu memoria muscular:

```jsonc
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",

    "test": "vitest run --coverage",              // unit+integration CON gate de coverage — lo que corre CI
    "test:unit": "vitest run",                    // rápido, sin coverage — para iterar local
    "test:watch": "vitest",                       // modo watch para TDD
    "test:e2e": "playwright test",                // suite E2E completa (nightly)
    "test:e2e:smoke": "playwright test --grep @smoke",   // solo flujos críticos (CI de PR)

    "lint": "eslint .",
    "typecheck": "tsc -b",                        // noEmit lo fijan los tsconfig del template de Vite
    "check": "npm run lint && npm run typecheck && npm run test && npm run build",

    "prepare": "simple-git-hooks"                 // instala los hooks en cada npm install (sección 08)
  }
}
```

**Por qué `check`:** es "todo el CI de PR menos el E2E, en local, con un solo comando". Antes de pushear algo grande, `npm run check` responde en minutos lo que el pipeline tardaría en rebotar. El workflow `deploy.yml` lo usa literalmente ([03_CI_CD.md](../Pipelines/03_CI_CD.md) sección 05) — si `check` pasa local, los gates de main pasan, por construcción.

---

## 03. `vitest.config.ts`

**[REQUIRED]** Coverage con provider `v8` y **thresholds como gate**: si la cobertura cae del umbral, `npm run test` falla — y con él, el CI. Los números de abajo son la heurística de arranque; el objetivo real (qué merece test y por qué) lo define la estrategia de esta carpeta y [08_QUALITY_STANDARDS.md](../Strategy/08_QUALITY_STANDARDS.md) — recalibrar allí, no borrar el gate aquí.

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    // jsdom: los tests de componentes React necesitan un DOM; para lógica pura
    // sobra 'node', pero un solo environment evita configs por-archivo.
    environment: 'jsdom',
    globals: true,                       // describe/it/expect sin imports
    setupFiles: ['./tests/setup.ts'],    // p. ej. import '@testing-library/jest-dom/vitest'
    include: ['tests/unit/**/*.test.{ts,tsx}'],
    exclude: ['tests/e2e/**', 'node_modules/**'],   // que Vitest jamás intente correr specs de Playwright

    coverage: {
      provider: 'v8',                    // sin instrumentación: mide con el coverage nativo del motor
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**'],               // solo código que shippea — configs y tests no cuentan
      exclude: ['src/**/*.d.ts', 'src/main.tsx', 'src/vite-env.d.ts'],
      thresholds: {
        // Heurística de arranque — el objetivo lo fija 08_QUALITY_STANDARDS.md.
        // Regla de trinquete: pueden subir, no bajar (bajar = decisión escrita).
        lines: 70,
        functions: 70,
        branches: 60,
        statements: 70,
      },
    },
  },
});
```

**Por qué v8 y no istanbul:** v8 usa el coverage nativo del motor de JS — sin paso de instrumentación, notablemente más rápido, precisión sobrada para un gate. **Por qué thresholds y no "coverage informativo":** un número que no bloquea nada es un número que nadie mira; el gate convierte la erosión de cobertura en un rojo el mismo día que ocurre.

---

## 04. `playwright.config.ts` y la convención `@smoke`

**[REQUIRED]** Convención de etiquetado: los tests de flujos críticos (login, flujo principal de negocio, pago si existe) llevan **`@smoke` en el título**; los de regresión visual, `@visual`. Los workflows filtran por grep — sin la etiqueta, el test no corre en PR ni en el smoke post-deploy.

```ts
// tests/e2e/auth.spec.ts — ejemplo de la convención
import { test, expect } from '@playwright/test';

test('login con magic link @smoke', async ({ page }) => {
  await page.goto('/login');
  // ...flujo crítico completo
});

test('dashboard se ve correcto @visual', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveScreenshot();   // regresión visual — corre en nightly
});
```

**[REQUIRED]** La config: reintentos solo en CI, screenshot solo en fallo, trace en el primer reintento, y `webServer` que se apaga solo cuando el target es una URL desplegada (`PLAYWRIGHT_BASE_URL` — así el MISMO comando sirve para el build local y para smoke contra staging/prod en [03_CI_CD.md](../Pipelines/03_CI_CD.md)):

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

// Sin PLAYWRIGHT_BASE_URL → build local servido por `vite preview` (requiere `npm run build` previo).
// Con PLAYWRIGHT_BASE_URL → target desplegado (staging/prod); no se levanta servidor.
const deployedTarget = process.env.PLAYWRIGHT_BASE_URL;
const baseURL = deployedTarget ?? 'http://localhost:4173';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,        // un test.only olvidado no puede poner verde falso en CI
  retries: process.env.CI ? 2 : 0,     // reintentos SOLO en CI: local, un flaky debe doler para que se arregle
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI
    ? [['list'], ['html', { open: 'never' }]]   // el HTML se sube como artefacto solo on-failure
    : [['html', { open: 'on-failure' }]],
  use: {
    baseURL,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',           // trace completo cuesta caro; en el retry ya sabes que interesa
    video: 'off',
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 720 } },
    },
    {
      name: 'chromium-mobile',
      use: { ...devices['Pixel 7'] },   // viewport móvil real — el 50%+ del tráfico SaaS
    },
    // firefox/webkit: agregar en nightly solo si aparecen bugs reales por navegador —
    // para un dev solo, chromium en 2 viewports es el 90% del valor por el 30% del tiempo.
  ],
  webServer: deployedTarget
    ? undefined
    : {
        command: 'npm run preview',
        url: 'http://localhost:4173',
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
```

**Por qué preview build y no `vite dev`:** el dev server no es lo que shippea — sirve módulos sin minificar, con HMR y sin los errores de empaquetado. El E2E prueba `dist/` real vía `vite preview`, el mismo artefacto que valida el pipeline y que llega a Pages.

---

## 05. ESLint — flat config esencial

**[REQUIRED]** ESLint 9+ con **flat config** (`eslint.config.js`, el formato por defecto desde ESLint 9 — el estándar vigente en 2026) y exactamente cuatro capas: JS recomendado, TypeScript recomendado, hooks de React y accesibilidad. Cero estilo (formato no es lint) y cero reglas artesanales al arrancar.

```js
// eslint.config.js
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import globals from 'globals';

export default tseslint.config(
  // Nunca lintear generados — ruido puro
  { ignores: ['dist', 'coverage', 'playwright-report', 'test-results', 'node_modules'] },

  js.configs.recommended,
  tseslint.configs.recommended,

  // Presets flat de los plugins — verificar el nombre exacto del preset en la versión instalada
  jsxA11y.flatConfigs.recommended,
  reactHooks.configs['recommended-latest'],

  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      globals: { ...globals.browser },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },

  {
    // Tests: entorno node + relajar lo que en tests es idiomático
    files: ['tests/**/*.{ts,tsx}'],
    languageOptions: {
      globals: { ...globals.node, ...globals.browser },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
);
```

**Por qué estas cuatro capas y no más:** `react-hooks` atrapa la clase de bug de React más cara (deps de efectos mal declaradas — bugs que solo aparecen en producción con timing real); `jsx-a11y` es el único recordatorio automático de accesibilidad que un dev solo va a tener; TS-recommended atrapa lo que el compilador deja pasar. Todo lo demás (import-sorting, estilo, reglas de proyecto) es opt-in posterior — un lint que grita 400 warnings el día uno se apaga el día dos. Nota 2026: ESLint 10 existe pero los plugins de React/a11y aún declaran peer de ESLint 9 — quedarse en 9 hasta que publiquen majors compatibles (verificar al instalar).

---

## 06. `lighthouserc.json`

**[REQUIRED]** Lighthouse CI corre en nightly ([03_CI_CD.md](../Pipelines/03_CI_CD.md) sección 06) contra el build estático. **Los umbrales no se inventan aquí: la fuente es [08_QUALITY_STANDARDS.md](../Strategy/08_QUALITY_STANDARDS.md)** — este archivo solo los ejecuta (performance ≥ 90, accesibilidad ≥ 95). Si los números cambian allá, se actualizan acá.

```json
{
  "ci": {
    "collect": {
      "staticDistDir": "./dist",
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["warn", { "minScore": 0.9 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

**Notas:** `numberOfRuns: 3` porque Lighthouse fluctúa — LHCI usa la mediana, que absorbe el run atípico. `seo` en `warn` y no `error`: en una app detrás de login el SEO de páginas internas es ruido; súbelo a `error` solo en el sitio público/landing. `staticDistDir` sirve `dist/` localmente — mide el build real sin depender de red ni de producción.

---

## 07. `.gitleaks.toml`

**[REQUIRED]** Config mínima en la raíz: reglas default de gitleaks + allowlist explícita de falsos positivos conocidos. La consume el job nightly full-history ([03_CI_CD.md](../Pipelines/03_CI_CD.md) sección 06) y complementa el push protection de [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 05. Si detecta algo: [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 08 — **rotar primero, limpiar después**.

```toml
# .gitleaks.toml — verificar sintaxis vigente de allowlist en docs de gitleaks al instalar
title = "gitleaks config del proyecto"

[extend]
# Heredar TODAS las reglas default (AWS, Stripe, JWT, claves privadas, etc.)
useDefault = true

[allowlist]
description = "Falsos positivos conocidos — cada entrada con su porqué"
paths = [
  '''package-lock\.json''',        # hashes de integridad disparan patrones de alta entropía
  '''tests/fixtures/.*''',         # datos SINTÉTICOS (sección 01) — si un secreto real vive aquí, el problema no es gitleaks
  '''.*\.snap''',
]
# La allowlist crece SOLO con falsos positivos verificados, nunca "para que pase".
# Ante la duda de si es un secreto real: es un secreto real (GITHUB_STANDARD §05).
```

---

## 08. Git hooks — simple-git-hooks + lint-staged

**[RECOMMENDED]** Pre-commit con **simple-git-hooks** (no husky, no lefthook) ejecutando **lint-staged** solo sobre los archivos staged.

**Por qué simple-git-hooks:** es la opción más liviana con margen — un paquete de ~10 KB sin dependencias cuya única función es escribir el hook en `.git/hooks`; se configura en 4 líneas del `package.json`. Husky trae más maquinaria (directorio `.husky/`, scripts de shell) para features que un dev solo no usa; lefthook es un binario Go excelente pero pensado para paralelizar hooks de equipos grandes — potencia que aquí es peso muerto. Criterio de salida: si algún día se necesitan hooks paralelos o por-carpeta, migrar a lefthook es un rato.

**[REQUIRED]** El pre-commit es **rápido (<5 s) y solo lintea lo staged**. Typecheck, tests y build NO van en pre-commit: el gate completo es el CI ([03_CI_CD.md](../Pipelines/03_CI_CD.md)) y el `npm run check` voluntario. Un pre-commit de 40 segundos entrena al dev a usar `--no-verify`, y un hook que se bypassea por costumbre protege exactamente nada — mejor un hook mínimo que se respeta siempre.

```jsonc
// package.json — agregar estas dos claves (los scripts ya están en la sección 02)
{
  "simple-git-hooks": {
    "pre-commit": "npx lint-staged"
  },
  "lint-staged": {
    "*.{ts,tsx}": "eslint --fix --max-warnings 0"
  }
}
```

```bash
# Activar (y se re-activa solo en cada npm install gracias al script "prepare"):
npx simple-git-hooks
```

---

## 09. Orden de instalación — comandos exactos

**[REQUIRED]** Sobre un proyecto Vite+React+TS recién creado (o existente), en este orden — cada bloque deja algo verificable funcionando antes del siguiente:

```bash
# 0) Base (solo proyecto nuevo)
npm create vite@latest mi-app -- --template react-ts
cd mi-app && npm install

# 1) Lint — ESLint 9 flat config (sección 05)
npm i -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks eslint-plugin-jsx-a11y globals
#    → crear eslint.config.js (sección 05) → verificar: npm run lint

# 2) Unit/integration — Vitest + Testing Library (sección 03)
npm i -D vitest @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
#    → crear vitest.config.ts + tests/setup.ts + carpetas de la sección 01
#    → escribir UN test trivial → verificar: npm run test:unit

# 3) E2E — Playwright (sección 04)
npm i -D @playwright/test
npx playwright install chromium
#    → crear playwright.config.ts + un spec @smoke del flujo principal
#    → verificar: npm run build && npm run test:e2e:smoke

# 4) Calidad y seguridad — Lighthouse CI + gitleaks (secciones 06-07)
npm i -D @lhci/cli
#    → crear lighthouserc.json → verificar: npm run build && npx lhci autorun
# gitleaks es un binario Go, no un paquete npm — local es opcional (el gate real es nightly):
#    Windows: winget install gitleaks   |   macOS: brew install gitleaks
#    → verificar: gitleaks git --no-banner .

# 5) Hooks — simple-git-hooks + lint-staged (sección 08)
npm i -D simple-git-hooks lint-staged
#    → agregar las claves al package.json + el script "prepare" → activar: npx simple-git-hooks
#    → verificar: un commit con un error de lint debe rebotar

# 6) Scripts + CI
#    → dejar los scripts EXACTOS de la sección 02 en package.json
#    → verificar el contrato completo: npm run check
#    → copiar ci.yml / deploy.yml / nightly.yml de 03_CI_CD.md a .github/workflows/
#      (reemplazar cada <SHA> por el SHA auditado y las URLs de staging/prod — 03_CI_CD.md sección 07)
#    → push → primer pipeline verde → marcar el check como requerido en la protección de main
```

**Por qué este orden:** lint primero porque no depende de nada y limpia el terreno; unit antes que E2E porque Vitest valida la config de TS/paths que Playwright también usará; hooks al final porque necesitan que `lint` ya funcione; CI al ultimísimo porque consume todos los scripts anteriores — copiar los workflows antes de que `npm run check` pase en local es garantizar un primer pipeline rojo sin información.

Versiones: los comandos instalan la última estable de cada paquete; los majors asumidos aquí (ESLint 9, Vitest con coverage v8, Playwright 1.x, LHCI 0.x) se verifican al instalar — si un major nuevo cambia la sintaxis de config, se actualiza este documento, no se congela el paquete.

---

## Checklist final

**Estructura y contrato**
- [ ] ¿`tests/unit`, `tests/e2e`, `tests/fixtures` (solo datos sintéticos), `tests/setup.ts`?
- [ ] ¿Los scripts de la sección 02 con esos nombres exactos; `npm run check` pasa en local?

**Configs**
- [ ] ¿Vitest con coverage v8, `include: src/**` y thresholds que FALLAN el run (trinquete: suben, no bajan)?
- [ ] ¿Playwright: `@smoke`/`@visual` por grep, retries solo CI, screenshot on-failure, trace on-first-retry, forbidOnly?
- [ ] ¿E2E contra preview build por defecto y contra `PLAYWRIGHT_BASE_URL` cuando se define — mismo comando?
- [ ] ¿ESLint 9 flat config con las 4 capas (js, ts, react-hooks, jsx-a11y) y generados ignorados?
- [ ] ¿lighthouserc.json con performance ≥ 0.90 y accessibility ≥ 0.95, tomados de 08_QUALITY_STANDARDS.md?
- [ ] ¿`.gitleaks.toml` con defaults heredados y allowlist solo de falsos positivos verificados?

**Hooks e instalación**
- [ ] ¿simple-git-hooks + lint-staged; pre-commit <5 s que solo lintea staged; script `prepare` presente?
- [ ] ¿Nada pesado (typecheck/tests/build) en pre-commit — eso vive en CI y en `check`?
- [ ] ¿Instalación en el orden de la sección 09, verificando cada bloque antes del siguiente?
- [ ] ¿Workflows copiados de 03_CI_CD.md con `<SHA>` y URLs reemplazados, y el check requerido en `main`?
