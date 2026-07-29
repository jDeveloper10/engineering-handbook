# 10 — PLAYBOOK

> Procedimientos operativos del departamento de QA: qué hacer, en qué orden, con qué comandos. Sigue [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Cada procedimiento es ejecutable por el dev o por un agente IA (Claude Code) sin contexto adicional al de este handbook. Los runbooks de **incidentes de infraestructura** (Cloudflare caído, DNS, datos corruptos) NO están aquí — viven en `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` Parte B y este playbook los invoca cuando toca.
>
> Regla general de los playbooks (heredada de 07_DevOps Parte B): **se sigue el procedimiento en orden — no se improvisa.** Los pasos codifican en frío lo que bajo presión se olvida.

---

## P1 — "Voy a empezar un proyecto nuevo"

Setup de QA completo, en el orden en que cada pieza desbloquea la siguiente. Presupuesto: ~1 hora una vez; todo lo de abajo queda funcionando solo.

**[REQUIRED]** Orden y comandos (stack primario; versiones exactas, las vigentes al ejecutar):

```bash
# 1. Scaffold con TypeScript estricto (el primer gate es el compilador)
npm create vite@latest mi-app -- --template react-ts
cd mi-app && git init

# 2. Runner + component testing (02_TESTING_PIPELINE.md define cómo escribirlos)
npm i -D vitest @vitest/coverage-v8 @testing-library/react @testing-library/user-event jsdom msw
#    -> vitest.config.ts con coverage.thresholds { statements: 70 }  (09_METRICS §1)

# 3. E2E mínimo (02_TESTING_PIPELINE.md, capa E2E): instala browsers y crea config
npm init playwright@latest
#    -> playwright.config.ts: retries: 1 en CI (detección de flaky, 09_METRICS §3),
#       webServer para levantar la app, trace: 'on-first-retry'

# 4. Higiene: lint, secretos, código muerto
npm i -D eslint prettier knip
#    gitleaks es binario aparte: instalar y añadir a pre-commit + CI (07_AUTOMATION_GUIDE.md)

# 5. El pipeline (hereda 07_DevOps §01: typecheck→tests→build; 03_CI_CD.md añade el resto)
mkdir -p .github/workflows   # copiar ci.yml de 07_DevOps §01 y extenderlo con
                             # lint, coverage gate, E2E y gitleaks según 03_CI_CD.md
                             # (umbrales: 08_QUALITY_STANDARDS.md)

# 6. Labels de bugs (05_BUG_LIFECYCLE §2)
gh label create P0 --color B60205 --description "Prod rota/datos en riesgo - drop everything"
gh label create P1 --color D93F0B --description "Core degradado - fix en 24h"
gh label create P2 --color FBCA04 --description "Bug con workaround - esta semana"
gh label create P3 --color C2E0C6 --description "Menor - backlog con expiracion"

# 7. Branch protection: main solo mergeable con CI verde (GITHUB_STANDARD)
gh api repos/{owner}/{repo}/branches/main/protection -X PUT --input protection.json

# 8. Renovate (07_AUTOMATION_GUIDE.md): habilitar la app de GitHub + renovate.json con
#    agrupación y automerge de patch con CI verde
# 9. Sentry en el frontend y workers + integración GitHub (05_BUG_LIFECYCLE §1)
# 10. Si hay workers: npm i -D @cloudflare/vitest-pool-workers   (requiere Vitest ≥4.1)
#     Si hay Supabase: supabase init && supabase start  (tests de RLS, 02_TESTING_PIPELINE.md)
```

**Por qué este orden:** cada paso protege al siguiente — sin runner no hay gate de coverage, sin pipeline no sirve la branch protection, sin labels el primer bug ya entra desordenado. **El proyecto no recibe su primera feature hasta el paso 7**: la ventana "luego lo configuro" es donde nacen los proyectos sin tests del procedimiento P6.

**[REQUIRED]** Verificación de salida: un PR de prueba con un test que falla **no puede mergearse**; al arreglarlo, mergea solo. Si esa demostración no ocurre, el setup no está terminado.

---

## P2 — "Encontré un bug en producción"

**[REQUIRED]** En orden estricto:

```
1. ¿Cumple criterio P0? (05_BUG_LIFECYCLE §3: caída total, datos, pagos, secretos)
   SÍ → STOP: ir a 07_DevOps §06 (rollback primero) / Parte B / 05_Security.
        Este playbook continúa cuando el sangrado paró.
   NO → seguir.

2. Registrar (aunque vayas a arreglarlo ya — 10 segundos):
   gh issue create --title "<síntoma>" --label "bug,P1|P2" --body "<repro + fuente>"

3. Reproducir ANTES de arreglar: primero como test automatizado al nivel más bajo
   posible (unit → integración → E2E). Correrlo: debe FALLAR (rojo).
   Si no se puede reproducir → el issue queda 'sin repro' con lo que se sabe;
   añadir logging/alerta que capture la próxima ocurrencia. NO arreglar a ciegas.

4. Fix mínimo → test en verde → PR "Fixes #N" con fix + test juntos → gates → deploy.

5. Verificar en producción (smoke del flujo afectado, hereda 07_DevOps §01).

6. Si fue P0/P1: post-mortem de una línea en el issue (05_BUG_LIFECYCLE §5):
   CAUSA | GATE QUE FALTÓ | AÑADIDO
```

**Por qué "reproducir antes de arreglar":** un fix sin repro es una hipótesis deployada — si "funciona", no se sabe por qué, y si el bug era otro, ahora hay dos. El test rojo convierte la hipótesis en conocimiento y de paso cumple la regla de oro sin trabajo extra.

---

## P3 — "Un test E2E está flaky"

Señal de entrada: el mismo spec pasó en retry ≥2 veces en una semana (09_METRICS §3), o falla localmente "a veces".

**[REQUIRED]** Procedimiento:

```bash
# 1. Confirmar y acotar: correr SOLO ese spec muchas veces
npx playwright test tests/checkout.spec.ts --repeat-each 20 --workers 4
#    ¿Falla solo con paralelismo? -> sospecha datos compartidos entre tests.

# 2. Mirar el trace del fallo (no adivinar):
npx playwright show-trace test-results/<run>/trace.zip
```

3. Diagnóstico por causa típica, en orden de probabilidad:

| Causa | Señal en el trace | Fix |
|---|---|---|
| Espera manual (`waitForTimeout`, sleep) | El fallo es un timing distinto al esperado | Reemplazar por asserts auto-wait (`expect(locator).toBeVisible()`) — los sleeps están prohibidos en [02_TESTING_PIPELINE.md](../Pipelines/02_TESTING_PIPELINE.md) |
| Datos compartidos entre tests | Falla solo en paralelo o según orden | Cada test crea sus propios datos (usuario/registro único por test) |
| Estado que sobrevive entre tests | Pasa solo, falla en suite | Aislar: contexto/storage nuevo por test, limpiar en setup (no en teardown, que no corre si el test anterior murió) |
| Animaciones/transiciones | Click cae en elemento moviéndose | `reducedMotion: 'reduce'` en el config / esperar el estado final |
| Dependencia de servicio externo real | Falla correlacionada con el tercero | Mockear el tercero (MSW/route interception) — E2E testea NUESTRO sistema |
| El bug es real e intermitente | El trace muestra comportamiento incorrecto de la app | No es flaky: es un bug de carrera → P2 con el trace adjunto |

4. **Si no se puede arreglar hoy → cuarentena, nunca convivencia:**

```ts
test.fixme('checkout con cupón', async ({ page }) => { /* ... */ });
// + en el mismo commit:
// gh issue create --title "E2E flaky en cuarentena: checkout con cupón" --label "bug,P2"
```

**[REQUIRED]** La cuarentena tiene deadline (el ciclo siguiente): se arregla o **se borra el test** aceptando el hueco por escrito en el issue. **Por qué la línea dura:** un test flaky conviviendo en la suite enseña a ignorar el rojo — a la tercera falsa alarma, el pipeline entero pierde autoridad, que es el activo más caro del departamento. Un suite de 9 tests confiables protege más que uno de 10 con un mentiroso.

---

## P4 — "El pipeline está lento" (>10 min, 09_METRICS §2)

**[REQUIRED]** Medir antes de tocar — la lentitud siempre está concentrada en 1–2 pasos:

```bash
gh run view <run-id> --json jobs \
  --jq '.jobs[].steps[] | select(.conclusion!=null) | "\(.name): \(.startedAt) -> \(.completedAt)"'
```

2. Aplicar el fix del paso culpable, en orden de costo/beneficio:

| Paso lento | Fix | Nota |
|---|---|---|
| `npm ci` (2–4 min) | `cache: npm` en setup-node (ya en 07_DevOps §01) — verificar que de verdad hitea | El miss silencioso de cache es el clásico |
| E2E en serie | `--shard` en varios jobs de Actions + `fullyParallel: true` | Playwright paraleliza gratis; usarlo |
| E2E excesivos | ¿>15 specs? Pirámide invertida → bajar tests a component/integración ([01_QA_STRATEGY.md](../Strategy/01_QA_STRATEGY.md) §1) | El fix real no es infra, es dieta |
| Coverage en cada run | Coverage solo en el job de PR, no en cada push de la rama | El dato se necesita en el merge |
| Unit tests lentos | Buscar I/O real escondida (red, disco, DB) en tests "unit" — moverlos a integración o mockear el borde | Un unit >100ms es sospechoso |
| Build repetido | Reusar artefacto del build entre jobs (upload/download-artifact) en vez de rebuild | |

**[REQUIRED]** Lo que NO es un fix aceptable: quitar gates, mover E2E a "solo nightly" sin decisión escrita, o subir el presupuesto a 15 min "por ahora". **Por qué:** la respuesta correcta a "verificar cuesta caro" es abaratar la verificación, no verificar menos — verificar menos es un préstamo que cobra producción.

---

## P5 — "Quiero saltarme un gate por emergencia"

**[REQUIRED]** Solo hay UN caso legítimo: **producción está rota (P0), el fix está listo, y un gate falla por causa demostrablemente ajena al fix** (ej. el E2E de otro flujo está en rojo por flakiness conocida, o una dependencia del pipeline — registry, runner — está caída). Entonces:

```bash
# 1. Deuda ANTES del bypass (el orden es deliberado):
gh issue create --title "GATE SALTADO: <gate> en <PR/commit>" --label "P1" \
  --body "Motivo: <por qué era ajeno al fix>. Restaurar y verificar en <24h."

# 2. Bypass con rastro (admin merge sobre branch protection):
gh pr merge <n> --admin --squash

# 3. Vigilancia manual del deploy: smoke inmediato del flujo del fix Y del flujo
#    cuyo gate se saltó — el gate saltado era la vista que ahora no tienes.

# 4. Dentro de 24h: restaurar el gate, re-correr TODO el pipeline en main,
#    y cerrar el issue SOLO con pipeline completo en verde.
```

**[REQUIRED]** Nunca es legítimo saltarse un gate porque: "es un cambio chiquito" (07_DevOps §01: ese es justo el perfil del deploy que rompe), "tengo prisa" sin P0, "el test que falla es justo el del flujo que toco" (eso no es un gate roto — es el gate funcionando), o "lo arreglo en el siguiente PR".

**Por qué el issue va ANTES del bypass:** después del bypass la presión desaparece y la memoria también; la deuda registrada antes es la única versión que existe. Un gate saltado sin issue es un agujero permanente con apariencia de excepción puntual. **Por qué P1 y no P3:** un gate caído degrada la protección de *todos* los deploys siguientes, no solo del que pasó.

**[RECOMMENDED]** Si un gate necesita saltarse 2+ veces por la misma causa, el problema es el gate (flaky, lento, mal ubicado) — arreglarlo de raíz con P3/P4; las excepciones repetidas son la norma naciendo.

---

## P6 — "Heredé / retomo un proyecto sin tests"

**[REQUIRED]** Estrategia incremental — el orden importa más que la velocidad; NO intentar "escribir la suite entera" (nunca se termina y bloquea el trabajo real):

```
Fase 0 — Congelar el riesgo (día 1):
  - Pipeline mínimo de 07_DevOps §01 aunque el paso de tests esté casi vacío:
    typecheck (tsc --noEmit) + build como primeros gates.
    Si el typecheck explota con cientos de errores: strict en tsconfig pero
    excluyendo lo peor // @ts-expect-error documentados — nunca strict:false global.
  - gitleaks sobre TODO el historial (los repos heredados guardan sorpresas):
      gitleaks detect --source . --log-opts="--all"
    Algo apareció -> rotar YA (05_Security / GITHUB_STANDARD §08).

Fase 1 — Smoke E2E del flujo crítico (semana 1; ANTES que cualquier unit):
  - 1 a 3 specs Playwright de los flujos de la definición de crítico
    (01_QA_STRATEGY §1): login + la acción core + pago si existe.
  - Solo camino feliz. Son la alarma de incendios: no dicen dónde, dicen QUE arde.
  Por qué E2E primero aquí (inverso a la pirámide): con cero conocimiento del
  código, el E2E es el único test escribible sin entender internals, y es el que
  impide el desastre grande mientras aprendes el resto.

Fase 2 — Unit/integración SOLO en lo que tocas (regla permanente):
  - Cada bug arreglado -> su test de regresión (regla de oro, sin excepción ni en legacy).
  - Cada zona que modifiques -> characterization tests ANTES de cambiarla:
    tests que fijan el comportamiento ACTUAL (incluidas sus rarezas) para
    detectar lo que tu cambio altera. Luego cambias, con red.
  - Código que no tocas: no se testea retroactivamente. El coverage crece
    exactamente donde está el riesgo real (lo que cambia), que es donde paga.

Fase 3 — Ratchet (mes 1 en adelante):
  - Medir coverage actual y fijarlo como umbral: coverage 23% -> threshold 23.
    Cada PR puede subirlo, ninguno bajarlo. Subir el número del config cuando
    el real suba. Nunca fijar 70% de entrada: un gate imposible se apaga
    en una semana y con él la credibilidad de todos los demás.
  - Al alcanzar ~70%: el proyecto se rige por el estándar normal (09_METRICS §1)
    y P1 aplica completo (labels, Renovate, Sentry, axe, Lighthouse).
```

**Por qué esta secuencia:** protege primero contra el error catastrófico (smoke E2E), después contra el error probable (tests donde hay cambios), y solo al final persigue el número (ratchet). La inversa — empezar por coverage — produce tests de relleno en código muerto mientras el flujo de pago sigue sin alarma.

---

## Checklist final

- [ ] P1: ¿ningún proyecto recibe features antes de branch protection + pipeline con gates? ¿Se verificó con el PR-que-no-mergea?
- [ ] P2: ¿todo bug de producción pasó por: triage P0 → issue → repro en rojo → fix en verde → smoke → post-mortem si P0/P1?
- [ ] P3: ¿cada flaky terminó en fix, o en cuarentena con issue y deadline — jamás conviviendo en la suite?
- [ ] P4: ¿la lentitud se midió por paso antes de tocar nada, y el fix nunca fue "quitar gates"?
- [ ] P5: ¿cada gate saltado tiene su issue P1 creado ANTES del bypass y el gate restaurado en <24h?
- [ ] P6: ¿el proyecto heredado tiene smoke E2E crítico + gitleaks del historial ANTES de cualquier otra inversión, y el coverage funciona por ratchet, no por meta imposible?
