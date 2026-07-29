# 01 — QA STRATEGY

> Nivel 1 del dominio Testing. Define **qué** se testea, **con qué**, **cuándo** y **qué no** — los documentos 02–08 implementan cada pieza. Sigue [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md): regla agnóstica primero, implementación de referencia después (stack actual: React 19 + Vite + TypeScript, Cloudflare Workers, Supabase).
>
> Contexto que calibra todo el documento: **developer solo, SaaS, sin QA humano**. El "departamento de QA" es este handbook ejecutado por herramientas reales + agentes IA (Claude Code). Eso implica dos cosas: (1) cada test compite por tiempo de la única persona del equipo — un test caro de mantener es deuda, no activo; (2) la inspiración viene de cómo hacen QA Google/Stripe/Vercel/Shopify (pirámide, quality gates, feature flags, canary), pero **adaptada**: se toma el principio, no el aparato. Cero cargo-cult enterprise: nada de test plans en documentos Word, comités de release ni matrices de trazabilidad.

---

## 1. El modelo: pirámide de tests adaptada a dev solo

**[REQUIRED]** La distribución de tests sigue la pirámide clásica (muchos unitarios, algunos de integración, pocos E2E), con estas proporciones **objetivo** — son heurística de equilibrio, no cuota a rellenar:

```
        /  E2E  \        ~5%   — 5 a 15 specs por proyecto, SOLO flujos críticos
       / integr. \       ~25%  — bordes del sistema: handlers de worker, RLS, API
      /   unit    \      ~70%  — lógica pura + componentes con comportamiento
```

**Por qué esta forma y no otra:**

- **Los unit son la base porque son los únicos que escalan con una persona sola.** Corren en milisegundos, fallan señalando la línea exacta, y no tienen dependencias que se caigan. Cuando Vitest re-ejecuta en <1s al guardar, el test es parte del loop de escritura, no una fase posterior.
- **Los de integración cubren la clase de bug que los unit no ven:** el contrato entre piezas (el handler que parsea mal el body, la policy RLS que deja pasar al usuario equivocado, el worker que asume una env var que no existe). Son más lentos y con más setup, por eso son menos.
- **Los E2E son pocos porque su costo es no-lineal.** Cada E2E añade superficie de flakiness (red, timing, datos), tarda segundos-minutos, y cuando falla no dice dónde está el bug — dice "algo en este flujo murió". Google los llama la "capa que se paga cara"; para un dev solo, más de ~15 specs E2E significa pasar más tiempo manteniendo tests que escribiendo producto. Se reservan para los flujos donde un fallo = negocio parado: signup/login, la acción core del SaaS, el pago.
- **Nota sobre la "testing trophy"** (la variante que engorda integración): en este stack, los tests de componentes React con Testing Library ocupan ese punto medio — se cuentan aquí como "unit/component" porque corren igual de rápido en jsdom/browser mode. La discusión pirámide vs trofeo es menos importante que la regla operativa: **empuja cada test al nivel más bajo que pueda atrapar el bug.**

**[REQUIRED]** Un flujo es "crítico" (y merece E2E) si cumple al menos una: (a) su fallo impide usar el producto (auth, onboarding), (b) mueve dinero (checkout, subscripción), (c) destruye o expone datos de usuario. Todo lo demás se cubre con capas inferiores.

**[RECOMMENDED]** Anti-síntomas de pirámide invertida — si aparecen, rebalancear: el suite completo tarda >10 min; un cambio de una línea rompe >5 tests; hay E2E para variantes de formularios que un component test cubriría.

---

## 2. Qué se automatiza (todo lo que bloquea) vs riesgo residual documentado

**[REQUIRED]** Se automatiza y actúa como gate (orden y workflows en [03_CI_CD.md](../Pipelines/03_CI_CD.md); umbrales exactos en [08_QUALITY_STANDARDS.md](08_QUALITY_STANDARDS.md)):

| Verificación | Herramienta | Gate |
|---|---|---|
| Contratos de tipos | `tsc --noEmit` | Bloquea (hereda de 07_DevOps §01) |
| Lógica y regresiones | Vitest (unit + integración) | Bloquea (hereda de 07_DevOps §01) |
| Build empaquetable | `vite build` / `wrangler deploy --dry-run` | Bloquea (hereda de 07_DevOps §01) |
| Flujos críticos | Playwright E2E | Bloquea |
| Lint + formato | ESLint + Prettier | Bloquea (barato, cero juicio) |
| Coverage mínimo | Vitest coverage (v8) | Bloquea bajo el umbral de [09_METRICS.md](09_METRICS.md) |
| Secretos en el repo | gitleaks | Bloquea |
| Accesibilidad automática | axe-core en E2E | Bloquea violaciones `critical`/`serious` |
| Performance | Lighthouse CI | Bloquea bajo presupuesto ([08_QUALITY_STANDARDS.md](08_QUALITY_STANDARDS.md)) |
| Código muerto / deps sin uso | knip | Reporta (no bloquea; ver [08_QUALITY_STANDARDS.md](08_QUALITY_STANDARDS.md)) |
| Deps vulnerables/viejas | Renovate + `npm audit` | PR automático; `critical` bloquea |
| Post-deploy | Smoke test producción | Hereda de 07_DevOps §01 |

**[REQUIRED]** Lo que NO se automatiza se acepta como **riesgo residual por escrito** — la diferencia entre riesgo aceptado y punto ciego es que el primero está en esta lista:

| Riesgo residual | Por qué se acepta | Mitigación parcial |
|---|---|---|
| Juicio estético / "se ve raro" | Automatizarlo (visual regression pixel-perfect) genera más falsos positivos que bugs reales atrapados a esta escala | El propio dev usa el producto; screenshots de Playwright en fallos |
| Cross-browser exótico (Safari viejo, Android low-end) | Mantener una granja de dispositivos no es viable para un dev solo | Playwright corre chromium+firefox+webkit; errores reales llegan por Sentry |
| Emails reales entregados (spam, rendering en clientes) | Testear la entrega real requiere infra dedicada | Test de integración hasta el borde del proveedor; el contenido se testea como unit |
| UX (¿el flujo es *entendible*?) | Ninguna máquina mide confusión | Analytics de abandono; feedback de usuarios |
| Carga/estrés a escala | Un SaaS pre-tracción no tiene ese perfil de tráfico; Workers/Supabase escalan antes que el código propio | Presupuestos de performance (08_QUALITY_STANDARDS); revisar si el tráfico crece 10x |

**Por qué:** perseguir el 100% de automatización es el error simétrico a no automatizar nada — las últimas verificaciones cuestan 10x y atrapan 0.1x. La lista de residuales se revisa cuando cambia el contexto (ej. si el producto empieza a facturar fuerte, "carga/estrés" sale de la lista y se automatiza).

---

## 3. Matriz de herramientas — elegidas, justificación, descartadas

**[REQUIRED]** Una sola herramienta por categoría en todos los proyectos del stack primario. **Por qué:** cada herramienta extra es una config más que mantener, una versión más que actualizar y un contexto más que un agente IA debe cargar; la uniformidad hace que todo proyecto se sienta igual al abrirlo.

| Categoría | Elegida | Por qué (verificado 2026) | Descartadas y por qué |
|---|---|---|---|
| Test runner | **Vitest 4** | Nativo de Vite: misma pipeline de transformación que la app (TS/ESM sin config extra), watch re-ejecuta por grafo de módulos en <1s, API compatible con Jest, coverage v8 integrado. Requiere Vite ≥6 y Node ≥20 | **Jest**: pipeline paralela a Vite (config duplicada, transformers), watch más lento, ESM históricamente doloroso. Solo gana en React Native (que no usamos) y monorepos legacy |
| E2E | **Playwright** | Auto-wait que elimina la causa #1 de flakiness, chromium+firefox+webkit con una API, paralelismo y sharding gratis en CI, trace viewer para depurar fallos sin re-ejecutar, `webServer` levanta la app solo | **Cypress**: corre dentro del browser (limita multi-tab/origen), paralelismo real atado a servicio pago, solo interceptación parcial de browsers. **Selenium**: API de bajo nivel, sin auto-wait, mantenimiento caro — estándar solo donde hay requisitos legacy |
| Component testing | **Testing Library** (`@testing-library/react`) sobre Vitest | Queries por rol/texto accesible = tests acoplados al comportamiento del usuario, no al DOM interno; es además presión gratis hacia accesibilidad | **Enzyme**: muerto (sin soporte React moderno); testear internals de componentes viola la sección 6 |
| Tests de Workers | **`@cloudflare/vitest-pool-workers`** | Corre los tests *dentro* de workerd local (Miniflare): bindings y APIs del runtime reales, storage aislado por test. Estado: **open beta**, requiere Vitest ≥4.1 — verificar breaking changes en docs oficiales al actualizar | Mockear `fetch`/bindings a mano: tests que pasan contra un runtime imaginario |
| Mock de APIs externas | **MSW** (Mock Service Worker) | Intercepta a nivel de red: el mismo mock sirve para unit, component y (si hace falta) Playwright; el código de producción no sabe que está mockeado | Stubs de `fetch` por test: se dispersan y divergen del contrato real |
| DB / RLS | **Supabase CLI local** (`supabase start`) + tests de policies | La única forma honesta de testear RLS es ejecutarla contra Postgres real con JWTs de distintos roles | Mockear el cliente de Supabase para lógica de negocio: sí (unit); mockearlo para *seguridad*: nunca |
| Performance | **Lighthouse CI** (`@lhci/cli`) | Gratis, corre en Actions contra preview URL, presupuestos versionados en repo, mide lo mismo que mira Google | **Calibre/SpeedCurve**: excelentes, pero pagos y orientados a equipos. **PageSpeed API a mano**: sin assertions ni historia |
| Accesibilidad | **axe-core** vía `@axe-core/playwright` | Motor estándar de-facto (lo usan Lighthouse y los grandes); se inyecta en los E2E existentes — cero suite aparte | **Pa11y**: envuelve motores similares con otro runner más que mantener |
| Secret scanning | **gitleaks** | Binario único, rápido, corre en pre-commit y en CI, baseline para falsos positivos | **truffleHog**: más pesado; git-secrets (AWS): estancado |
| Código muerto | **knip** | Encuentra exports, archivos y dependencias sin uso en proyectos TS modernos; reemplaza a 3 herramientas | depcheck/ts-prune: sin mantenimiento activo, knip los absorbió como estándar |
| Actualización de deps | **Renovate** | Agrupa updates (un PR, no veinte), automerge configurable para patch/minor con CI verde — crítico cuando una sola persona revisa PRs | **Dependabot**: aceptable (cero config, nativo GitHub) pero sin agrupación fina ni automerge maduro; el ruido de PRs es el problema real de un dev solo. Se mantiene Dependabot **security alerts** activado (gratis y pasivo) |
| Errores en producción | **Sentry** | Captura + sourcemaps + alertas; es la fuente #2 de bugs en [05_BUG_LIFECYCLE.md](../Guides/05_BUG_LIFECYCLE.md) | Logs a mano: sin agregación ni stack traces simbolizados |

**[RECOMMENDED]** Portabilidad al stack secundario — la regla (una herramienta por categoría, pirámide igual) es agnóstica; solo cambia la capa 2:

- **Node puro** (CLIs, scripts): mismo Vitest — funciona sin Vite.
- **Python**: pytest + coverage.py + ruff; pirámide y gates idénticos.
- **Electron**: Playwright tiene soporte para Electron (experimental — verificar estado en docs oficiales antes de apostarle); unit/component idénticos al stack web.
- **PWA**: todo lo anterior + auditoría PWA de Lighthouse y test explícito del comportamiento offline del service worker.

---

## 4. Cuándo escribir cada tipo de test

**[REQUIRED] Nueva feature** — los tests se escriben en el mismo PR que la feature, nunca "después":

1. Lógica de negocio (cálculos, validaciones, transformaciones) → **unit**, apuntando a extraerla en funciones puras testeables sin mock.
2. Componente UI con comportamiento (condicionales, estados, interacción) → **component test**. Componente puramente presentacional → no se testea (sección 6).
3. Endpoint/handler nuevo → **integración** (pool-workers): request real → response real, casos feliz + auth fallida + input inválido.
4. ¿Toca un flujo crítico (sección 1)? → actualizar/añadir el **E2E** de ese flujo. Si no, no hay E2E nuevo.

**Por qué "mismo PR":** el test escrito con la feature cuesta minutos (el contexto está cargado); el test escrito después cuesta horas (hay que reconstruir el contexto) y en la práctica de un dev solo, "después" = nunca.

**[REQUIRED] Bug encontrado** — regla de oro (detalle en [05_BUG_LIFECYCLE.md](../Guides/05_BUG_LIFECYCLE.md)): primero el test que reproduce el bug (rojo), después el fix (verde). El test se escribe **antes** del fix porque es la única prueba de que el test de verdad atrapa ese bug — un test escrito después del fix puede pasar por casualidad.

**[REQUIRED] Refactor** — no se escriben tests nuevos para el refactor; los existentes **son** la red que lo hace posible (si cambian los asserts, no era refactor, era cambio de comportamiento). Si la zona a refactorizar no tiene tests: primero *characterization tests* que fijen el comportamiento actual (aunque el comportamiento actual incluya rarezas), después el refactor. Ver [10_PLAYBOOK.md](../Guides/10_PLAYBOOK.md) P6.

**[RECOMMENDED] Código generado por IA** — mismo estándar que el humano, con un énfasis: la IA que genera el código no "aprueba" sus propios tests como gate; el gate es el pipeline. Un agente puede escribir código y tests, pero el merge lo decide CI verde, no la confianza del agente.

---

## 5. Qué NO testear

**[REQUIRED]** No perseguir 100% de coverage. El umbral vive en [09_METRICS.md](09_METRICS.md) (~70%) y **no se sube artificialmente**. **Por qué:** pasado cierto punto, el coverage adicional se compra testeando getters, ramas imposibles y glue code — tests que no pueden fallar por un bug real pero sí fallan en cada refactor. Coverage es un detector de *huecos* (¿qué zona importante quedó sin tocar?), no una meta (Goodhart: cuando la métrica es la meta, deja de medir).

**[REQUIRED]** No testear implementación, testear comportamiento observable. Prohibido: asserts sobre estado interno de componentes, verificar que "se llamó el método X interno", tests que conocen el orden de llamadas privadas. **Por qué:** son tests que fallan cuando refactorizas sin bug y pasan cuando hay bug sin refactor — señal invertida. Heurística: si el test rompe al renombrar una variable privada, está mal escrito.

**[REQUIRED]** No testear la librería ni la plataforma. No se verifica que React renderice, que Supabase filtre un `.eq()`, que Zod valide un email, ni que Workers rutee. **Por qué:** eso ya lo testean sus autores con más recursos; nuestro test solo re-testea su suite con peor cobertura. Se testea **nuestro uso**: que la query tenga el filtro correcto, que el schema Zod declare los campos correctos.

**[RECOMMENDED]** Evitar también: snapshot tests grandes (nadie lee un diff de 300 líneas — se aprueban a ciegas, que es lo contrario de un test), tests de estilos estáticos (color, padding — eso es juicio visual, riesgo residual de la sección 2), y tests de tipos que TypeScript ya garantiza (`expect(typeof x).toBe('string')` sobre algo tipado `string`).

---

## Checklist final

- [ ] ¿La distribución real de tests se aproxima a ~70/25/5 y los E2E son ≤15 specs, solo flujos críticos (auth, acción core, pago)?
- [ ] ¿Cada verificación automatizada de la tabla de la sección 2 existe y bloquea lo que dice bloquear?
- [ ] ¿Todo riesgo no automatizado está en la lista de residuales, con su mitigación?
- [ ] ¿El proyecto usa exactamente las herramientas de la matriz (Vitest 4, Playwright, Testing Library, pool-workers, MSW, Supabase CLI, Lighthouse CI, axe-core, gitleaks, knip, Renovate, Sentry)? ¿Cualquier desviación está justificada por escrito?
- [ ] ¿Los tests de una feature van en el mismo PR que la feature?
- [ ] ¿Cada bug arreglado dejó su test de regresión escrito ANTES del fix?
- [ ] ¿Los refactors se apoyan en tests existentes o characterization tests — nunca en "se ve bien"?
- [ ] ¿Nadie está subiendo coverage testeando trivialidades, testeando internals, o re-testeando librerías?
