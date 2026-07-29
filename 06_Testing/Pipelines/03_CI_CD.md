# 03 — CI/CD: EL PIPELINE DE QA POR ETAPAS

> Documento del dominio Testing (06). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md): reglas `[REQUIRED]`/`[RECOMMENDED]`, capa agnóstica + implementación de referencia (GitHub Actions, React+Vite+TS en Cloudflare Pages, Workers con wrangler, Supabase).
>
> **Relación con DevOps:** el pipeline base `typecheck → tests → build` y el deploy a Cloudflare **ya están definidos** en [`07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 01 — este documento **lo extiende con más gates de calidad**, no lo reinventa. La seguridad de todo workflow cumple [`07_DevOps/GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 07 (permisos mínimos, pin por SHA, secretos en environment).
>
> Los nombres de scripts que usan estos workflows (`lint`, `typecheck`, `test`, `test:e2e:smoke`, etc.) son el contrato estándar definido en [07_AUTOMATION_GUIDE.md](../Guides/07_AUTOMATION_GUIDE.md) — idénticos en todos los proyectos.

---

## 01. Principio: no todo corre en cada push

**[REQUIRED]** El pipeline se divide en **tres etapas por frecuencia**, y cada check vive en la etapa más barata que aún lo hace útil:

| Etapa | Cuándo | Qué corre | Presupuesto |
|---|---|---|---|
| **CI rápido** | cada push / PR | lint → typecheck → unit+integration con gate de coverage → build → E2E smoke sobre el build | **< 10 min** |
| **Deploy** | merge/push a `main` | todo lo anterior + deploy staging → smoke contra staging → deploy prod → smoke contra prod | < 20 min |
| **Nightly** | diario (cron) + manual | E2E completo + regresión visual + Lighthouse CI + audit de dependencias + gitleaks full-history | sin límite (nadie lo espera) |

**Por qué:** un pipeline de 40 minutos en cada push muere por abandono — el dev deja de esperarlo, empieza a mergear "mientras corre", y el gate se vuelve decorativo. El feedback de PR debe llegar antes de que cambies de contexto (<10 min); todo lo que no cabe en ese presupuesto (E2E completo, visual, Lighthouse, escaneo de historial) se muda a nightly, donde la latencia no le cuesta a nadie. La regla de asignación: **un check corre en PR solo si (a) atrapa errores que bloquean el merge con frecuencia real y (b) cabe en el presupuesto**; lo demás corre en nightly y avisa por excepción.

**[REQUIRED]** El E2E de PR es **solo la suite smoke** (tests etiquetados `@smoke` — flujos críticos: login, flujo principal de negocio, checkout si existe; convención definida en [07_AUTOMATION_GUIDE.md](../Guides/07_AUTOMATION_GUIDE.md) sección 04). La suite E2E completa corre en nightly.

**Por qué:** el 80% del valor de E2E en un PR es "¿la app arranca y el flujo que paga las cuentas funciona?" — eso son 3-8 tests de 2-3 minutos. La cola larga de E2E (edge cases, todos los viewports) casi nunca es lo que rompe un PR y sí es lo que lo hace tardar 30 minutos.

---

## 02. Presupuesto de tiempo y cómo defenderlo

**[REQUIRED]** El feedback de PR llega en **menos de 10 minutos**. Si el pipeline lo supera de forma sostenida, se optimiza en este orden (del más barato al más caro):

1. **Cache** — dependencias npm y browsers de Playwright cacheados (ya incluido abajo). Un `npm ci` sin cache son 1-2 min tirados en cada run.
2. **Mover checks a nightly** — el candidato que creció (más tests visuales, más E2E) se degrada de PR a nightly.
3. **Shards de Playwright** — dividir la suite E2E en N jobs paralelos (`--shard=1/2`, `--shard=2/2`). Activar cuando la suite smoke supere ~5 min (plantilla comentada en el workflow de abajo).
4. **`concurrency` con cancelación** — dos pushes seguidos no corren dos pipelines completos: el nuevo cancela al viejo (ya incluido abajo).

**Por qué el orden:** cache y cancelación son gratis; mover checks reordena sin perder cobertura (la pierde de inmediatez, no de existencia); los shards multiplican minutos de runner consumidos — es la palanca correcta pero la última, porque cuesta cuota.

---

## 03. Política de gate fallido

**[REQUIRED]** **Un gate rojo bloquea el merge. No existe "mergear y arreglar después".** El check `ci` es status check requerido en la protección de `main` ([`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 03). Un test flaky no se skipea para pasar el gate: o se arregla, o se mueve a cuarentena nightly con un issue abierto — nunca desaparece en silencio.

**Por qué:** el gate es la única "segunda persona" que revisa el código de un dev solo. La primera vez que se mergea en rojo "porque es urgente", el gate deja de significar algo: el estado rojo se normaliza, los rojos nuevos se pierden entre los viejos, y en dos semanas nadie sabe si el rojo actual es el flaky conocido o una regresión real. Un pipeline solo protege si rojo = detenerse, siempre.

**[REQUIRED]** **Excepción de emergencia** (producción caída y el fix no puede esperar al pipeline): existe una sola vía documentada — el procedimiento de hotfix de emergencia del playbook [10_PLAYBOOK.md](../Guides/10_PLAYBOOK.md), que se apoya en la vía de escape deliberada de `enforce_admins: false` ([`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 03). Después del incidente, el commit de emergencia pasa el pipeline completo retroactivamente y se escribe el post-mortem ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 06). La excepción se usa, se registra y se cierra — no se convierte en atajo.

---

## 04. Workflow 1 — `ci.yml` (cada push y PR)

**[REQUIRED]** El workflow de CI: permisos mínimos (`contents: read`), concurrency que cancela runs obsoletos, cache de npm y de browsers, artefactos de Playwright **solo on-failure**, y timeouts por job para que un cuelgue no consuma la cuota.

**Implementación (`.github/workflows/ci.yml`):**

```yaml
name: ci

on:
  pull_request:
  push:
    branches-ignore: [main]   # main dispara deploy.yml, que repite estos gates

permissions:
  contents: read              # GITHUB_STANDARD §07: mínimo necesario

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true    # push nuevo cancela el pipeline del push viejo

env:
  NODE_VERSION: '22'

jobs:
  quality:
    name: lint · typecheck · unit · build
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm                       # cachea ~/.npm con key del lockfile
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test                  # vitest run --coverage → falla si no cumple thresholds
      - run: npm run build
      - name: Subir build para el job E2E
        uses: actions/upload-artifact@v4   # verificar versión vigente
        with:
          name: dist
          path: dist/
          retention-days: 1

  e2e-smoke:
    name: e2e smoke (preview build)
    needs: quality
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist
      - name: Cache de browsers de Playwright
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - name: Instalar chromium (solo si no está cacheado)
        if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium --with-deps
      - name: Instalar deps de sistema (con browsers cacheados)
        if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
      - run: npm run test:e2e:smoke        # playwright levanta `npm run preview` (webServer)
      - name: Reporte HTML + traces (solo si falla)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report-${{ github.run_id }}
          path: |
            playwright-report/
            test-results/
          retention-days: 7

# --- Shards: plantilla para cuando la suite smoke supere ~5 min (sección 02) ---
#  e2e-smoke:
#    strategy:
#      fail-fast: false
#      matrix:
#        shard: [1, 2]
#    steps:
#      ...
#      - run: npm run test:e2e:smoke -- --shard=${{ matrix.shard }}/2
```

**Notas de diseño:**

- **Dos jobs, no uno:** el E2E arranca solo si `quality` pasó — no gastar 3 min de browsers en un build que no typechequea. El build viaja como artefacto: el E2E prueba **el mismo build** que se validó, no uno recompilado.
- **El gate de coverage vive en `npm run test`** (thresholds en `vitest.config.ts`, sección 03 de [07_AUTOMATION_GUIDE.md](../Guides/07_AUTOMATION_GUIDE.md)) — el workflow no duplica números; si el umbral cambia, cambia en un solo lugar.
- **Artefactos solo on-failure:** el reporte HTML de Playwright y los traces son para depurar rojos; subirlos en verde es pagar storage por nada.
- **`branches-ignore: [main]`:** evita el doble run (ci.yml + deploy.yml) en el mismo push a `main` — los gates sobre `main` los repite `deploy.yml` (sección 05), porque el deploy no confía en un run previo de otra rama.

---

## 05. Workflow 2 — `deploy.yml` (merge a main)

**[REQUIRED]** El camino a producción es: **gates completos → deploy a staging → smoke contra staging → deploy a producción (environment protegido) → smoke contra producción.** Nada se salta etapas; el smoke post-deploy es el mismo `[REQUIRED]` de [`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 01, ahora automatizado.

**Por qué staging antes de prod:** el smoke contra staging atrapa la clase de error que el build no ve — env vars mal configuradas en la plataforma, bindings de worker rotos, CORS — con costo cero para usuarios. Para el frontend en Pages con conexión Git, los preview deployments por rama **ya son** el staging ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) secciones 03-04); este workflow deploya el **worker** a su env staging y valida la combinación.

**Implementación (`.github/workflows/deploy.yml`):**

```yaml
name: deploy

on:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: deploy-main
  cancel-in-progress: false   # NUNCA cancelar un deploy a mitad — se encolan

env:
  NODE_VERSION: '22'
  STAGING_URL: https://staging.tuapp.com      # ajustar por proyecto
  PRODUCTION_URL: https://tuapp.com           # ajustar por proyecto

jobs:
  gates:
    name: gates (pipeline completo sobre main)
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - run: npm run check          # lint + typecheck + test (coverage) + build — contrato de 07_AUTOMATION_GUIDE
      - name: Cache de browsers de Playwright
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium --with-deps
      - if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
      - run: npm run test:e2e:smoke   # smoke sobre el build local antes de tocar staging

  deploy-staging:
    needs: gates
    runs-on: ubuntu-latest
    timeout-minutes: 5
    environment: staging
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - name: Deploy del worker a staging
        uses: cloudflare/wrangler-action@<SHA>   # v3.x — SHA real, ver sección 07
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: deploy --env staging

  smoke-staging:
    needs: deploy-staging
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - name: Cache de browsers de Playwright
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium --with-deps
      - if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
      - name: Smoke E2E contra staging real
        run: npm run test:e2e:smoke
        env:
          PLAYWRIGHT_BASE_URL: ${{ env.STAGING_URL }}   # con BASE_URL, playwright no levanta webServer

  deploy-production:
    needs: smoke-staging
    runs-on: ubuntu-latest
    timeout-minutes: 5
    environment: production        # GITHUB_STANDARD §07: el token de prod SOLO vive aquí
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - name: Deploy del worker a producción
        uses: cloudflare/wrangler-action@<SHA>   # mismo SHA auditado que arriba
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: deploy
      # El frontend en Pages se deploya solo por la conexión Git al mergear a main
      # (DEPLOY_AND_FAILURES §03) — este workflow no lo duplica, solo lo verifica abajo.

  smoke-production:
    needs: deploy-production
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v5
      - name: Health check del worker
        run: curl --fail --silent --show-error --max-time 10 "${{ env.PRODUCTION_URL }}/api/health"
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - name: Cache de browsers de Playwright
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium --with-deps
      - if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
      - name: Smoke E2E contra producción
        run: npm run test:e2e:smoke
        env:
          PLAYWRIGHT_BASE_URL: ${{ env.PRODUCTION_URL }}
```

**[REQUIRED]** Si `smoke-production` falla: **rollback primero, diagnóstico después** — el criterio y las vías exactas (`wrangler rollback`, dashboard de Pages) están en [`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) secciones 02, 03 y 06. Este workflow no automatiza el rollback a propósito: un rollback automático mal calibrado (flaky del smoke) causa más incidentes de los que evita en un equipo de 1 — el rojo notifica, el humano decide con el runbook.

---

## 06. Workflow 3 — `nightly.yml` (diario)

**[REQUIRED]** Corre a diario (cron) y bajo demanda (`workflow_dispatch`): E2E completo con shards, regresión visual, Lighthouse CI (umbrales de [08_QUALITY_STANDARDS.md](../Strategy/08_QUALITY_STANDARDS.md)), audit de dependencias y gitleaks sobre el **historial completo**. Un fallo abre un issue — nightly que falla en silencio es nightly que no existe.

**Por qué cada pieza está aquí y no en PR:** el E2E completo y visual tardan demasiado (sección 01); Lighthouse fluctúa por red/runner y como gate de PR produce rojos falsos; el audit de dependencias cambia por CVEs nuevos, no por tus commits — correrlo por push da la misma alerta con más ruido; gitleaks full-history revisa lo que push protection ([`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 05) pudo no cubrir con patrones viejos.

**Implementación (`.github/workflows/nightly.yml`):**

```yaml
name: nightly

on:
  schedule:
    - cron: '0 6 * * *'        # 06:00 UTC diario
  workflow_dispatch:            # ejecutable a mano cuando haga falta

permissions:
  contents: read

env:
  NODE_VERSION: '22'

jobs:
  e2e-full:
    name: e2e completo (shard ${{ matrix.shard }})
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2]
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - run: npm run build
      - name: Cache de browsers de Playwright
        id: pw-cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - if: steps.pw-cache.outputs.cache-hit != 'true'
        run: npx playwright install chromium --with-deps
      - if: steps.pw-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
      - name: Suite E2E completa (incluye regresión visual @visual)
        run: npm run test:e2e -- --shard=${{ matrix.shard }}/2
      - name: Reporte + traces (solo si falla)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: nightly-playwright-shard-${{ matrix.shard }}
          path: |
            playwright-report/
            test-results/
          retention-days: 14

  lighthouse:
    name: lighthouse ci (budgets de 08_QUALITY_STANDARDS)
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - run: npm run build
      - run: npx lhci autorun    # lee lighthouserc.json (07_AUTOMATION_GUIDE sección 06)

  audit:
    name: audit de dependencias
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
      - run: npm ci
      - name: Vulnerabilidades high+ en dependencias de producción
        run: npm audit --omit=dev --audit-level=high
      # Complementa (no sustituye) a Dependabot alerts — GITHUB_STANDARD §06

  gitleaks:
    name: gitleaks full-history
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0         # historial COMPLETO — escanea todos los commits
      - uses: gitleaks/gitleaks-action@<SHA>   # v2.x — tercero: SHA real, ver sección 07
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      # Config: .gitleaks.toml en la raíz (07_AUTOMATION_GUIDE sección 07).
      # Si encuentra algo: GITHUB_STANDARD §08 — ROTAR primero, limpiar después.

  notify-failure:
    name: abrir issue si algo falló
    needs: [e2e-full, lighthouse, audit, gitleaks]
    if: failure()
    runs-on: ubuntu-latest
    timeout-minutes: 3
    permissions:
      contents: read
      issues: write              # único job con permiso extra, y solo este
    steps:
      - name: Crear issue con el enlace al run
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh issue create \
            --repo "$GITHUB_REPOSITORY" \
            --title "Nightly rojo — $(date -u +%Y-%m-%d)" \
            --body "Falló el nightly: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }} — revisar antes del próximo release (04_RELEASE_PROCESS.md)." \
            --label bug
```

**[RECOMMENDED]** Un nightly rojo se triaje el mismo día laboral: o es regresión real (se arregla), o es flaky/umbral desactualizado (se recalibra con registro). Dos nightlies rojos ignorados = el equipo ya aprendió a ignorar el nightly, y volvió decorativo — mismo mecanismo que la sección 03.

---

## 07. Seguridad transversal de los workflows

Resumen operativo de [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 07 aplicado a los tres workflows — la norma completa vive allá:

**[REQUIRED]** Todo workflow declara `permissions:` explícito al tope con el mínimo (`contents: read` en los tres); un job que necesita más (el `notify-failure` con `issues: write`) lo declara **a nivel de job**, no globalmente.

**[REQUIRED]** Actions de terceros pineadas por **SHA completo del commit** en todo workflow (obligatorio donde hay secretos). En este documento el placeholder `<SHA>` marca dónde va el SHA real:

| Action | Versión legible | Cómo obtener el SHA |
|---|---|---|
| `cloudflare/wrangler-action` | v3.x (verificar versión vigente) | `gh api repos/cloudflare/wrangler-action/commits/vX.Y.Z --jq .sha` |
| `gitleaks/gitleaks-action` | v2.x (verificar versión vigente) | `gh api repos/gitleaks/gitleaks-action/commits/vX.Y.Z --jq .sha` |

Las oficiales (`actions/checkout@v5`, `actions/setup-node@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`) pueden usar tag mayor. Al copiar el workflow a un proyecto: **reemplazar cada `<SHA>` por el SHA auditado y dejar el comentario con la versión legible al lado.** Un `<SHA>` sin reemplazar rompe el workflow a propósito — mejor que correr con un tag móvil.

**[REQUIRED]** `CLOUDFLARE_API_TOKEN` de producción vive en el **environment `production`**; el de staging, en el environment `staging`. Nunca como secretos planos de repo. Ningún workflow usa `pull_request_target` con checkout de código externo.

---

## Checklist final

**Etapas**
- [ ] ¿CI de PR corre solo lint + typecheck + unit/integration con coverage + build + E2E smoke, en <10 min?
- [ ] ¿E2E completo, visual, Lighthouse, audit y gitleaks full-history viven en nightly, no en PR?
- [ ] ¿Merge a main repite los gates y encadena staging → smoke → prod → smoke?

**Gates**
- [ ] ¿El check de CI es status check requerido en `main`; gate rojo = merge bloqueado, sin excepciones informales?
- [ ] ¿La única excepción es el hotfix de emergencia de 10_PLAYBOOK.md, con pipeline retroactivo y post-mortem?
- [ ] ¿Coverage gate en vitest.config.ts (un solo lugar), no duplicado en el workflow?
- [ ] ¿Smoke de producción rojo → rollback por runbook (DEPLOY_AND_FAILURES §06), nunca "seguro es flaky"?

**Mecánica de los workflows**
- [ ] ¿`permissions: contents: read` al tope de los tres workflows; permisos extra solo a nivel de job?
- [ ] ¿Terceros (`wrangler-action`, `gitleaks-action`) pineados por SHA real, con la versión legible en comentario?
- [ ] ¿Secretos de deploy en environments `staging`/`production`, no en secretos de repo?
- [ ] ¿Cache de npm (setup-node) y de browsers de Playwright (actions/cache) activos?
- [ ] ¿`concurrency` cancela runs obsoletos en CI y encola (sin cancelar) en deploy?
- [ ] ¿Reporte de Playwright y traces se suben solo on-failure, con retención corta?
- [ ] ¿Shards de Playwright activados si la suite supera ~5 min; nightly con `fail-fast: false`?
- [ ] ¿Nightly rojo abre issue automáticamente y se triaje el mismo día?
