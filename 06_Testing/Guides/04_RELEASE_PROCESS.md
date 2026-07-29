---
title: "Proceso de Release para un Dev Solo"
category: 06_Testing
doc_type: estandar
tags: [testing, release, semver, changelog]
summary: "Proceso completo de release: versionado SemVer pragmático, CHANGELOG generado con release-please, tags y GitHub Releases, y qué cuenta como release."
keywords: [release, semver, changelog, release-please, tags, github-releases]
updated: 2026-07-27
status: current
---

# 04 — RELEASE PROCESS: RELEASES PARA UN DEV SOLO

> Documento del dominio Testing (06). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md): reglas `[REQUIRED]`/`[RECOMMENDED]`, capa agnóstica + implementación de referencia (GitHub, conventional commits según [`07_DevOps/GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 02, deploy según [`07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md)).
>
> Contexto que calibra todo: **developer solo, SaaS con deploy continuo a Cloudflare.** Aquí "release" no es un evento trimestral con comité — es el acto de marcar un estado del código como versión nombrada, con changelog, después de que el pipeline completo ([03_CI_CD.md](../Pipelines/03_CI_CD.md)) lo validó. El objetivo del proceso es que cueste ~0 minutos de trabajo manual, porque un proceso de release que cuesta esfuerzo se deja de hacer.

---

## 00. El proceso en una tabla (referencia rápida)

| Pregunta | Respuesta | Sección |
|---|---|---|
| ¿Qué esquema de versión? | SemVer pragmático — la herramienta decide por el prefijo del commit | 01 |
| ¿Quién escribe el CHANGELOG? | release-please, desde conventional commits — nunca a mano | 02 |
| ¿Cómo se "corta" una versión? | Mergeando el Release PR que release-please mantiene abierto | 02, 04.1 |
| ¿Qué produce cada release? | Tag `vX.Y.Z` + GitHub Release + CHANGELOG commiteado, automático | 03 |
| ¿Cuándo algo ES un release? | Pipeline verde + deploy por el camino estándar + smoke de prod verde | 04 |
| ¿Y si el smoke de prod falla? | No hay release: hay incidente → rollback por runbook | 04, DEPLOY_AND_FAILURES §06 |
| ¿Feature a medias o riesgoso? | Flag (env var → KV), no rama larga; el flag tiene fecha de muerte | 05 |
| ¿Cuándo NO releasear? | Viernes noche / sin pipeline / con 3 semanas acumuladas | 06 |
| ¿Cuánto puede acumular el Release PR? | ~1 semana o ~15 commits, lo que llegue primero | 06 |
| ¿Qué se hace justo después? | ~30 min de observación: `wrangler tail`, flujo a mano, panel de errores | 04.5 |

---

## 01. Versionado — SemVer pragmático

**[REQUIRED]** El esquema de versionado es **SemVer pragmático**: `MAJOR.MINOR.PATCH`, donde para un SaaS sin API pública consumida por terceros la semántica se simplifica:

- **PATCH** — solo fixes (`fix:`), sin funcionalidad nueva.
- **MINOR** — funcionalidad nueva (`feat:`), el caso normal.
- **MAJOR** — cambio que rompe algo que alguien externo consume (API pública, webhook, formato de export) **o** un cambio de tal magnitud que quieres poder decir "desde la v3...". Raro en un SaaS: la mayoría de proyectos viven años en `1.x`.

**Por qué SemVer y no CalVer:** la decisión real no es filosófica sino operativa — los commits ya son Conventional Commits (`[REQUIRED]` en [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 02), y `feat:`/`fix:` **mapean mecánicamente** a MINOR/PATCH. Eso permite que la herramienta de la sección 02 calcule la versión sola, sin decisión humana por release. CalVer (`2026.07.1`) es atractivo para SaaS ("la versión no significa nada para el usuario"), pero rompe ese mapeo automático, y pierde la única señal que SemVer sí da gratis: distinguir de un vistazo "release de fixes" de "release con features". Cuando la herramienta decide la versión, SemVer cuesta cero — y lo que cuesta cero no se abandona.

**[RECOMMENDED]** **Salir de `0.x` en el primer deploy con usuarios reales.** La convención `0.x = "todo puede romper"` protege a consumidores de librerías; un SaaS con un usuario pagando ya no tiene ese permiso, lo diga el número o no. `1.0.0` en el primer release productivo evita además el modo especial de bump que las herramientas aplican a `0.x` (donde `feat:` no sube el minor igual).

**[RECOMMENDED]** No perseguir pureza SemVer: discutir 20 minutos si algo es minor o patch es exactamente el costo que este esquema elimina. La herramienta decide por el prefijo del commit; si eliges mal el prefijo, la versión sale "mal" y no pasa nada — es un SaaS, nadie hace `npm install` de tu app.

---

## 02. CHANGELOG generado — release-please

**[REQUIRED]** El CHANGELOG **no se escribe a mano**: se genera desde los conventional commits por herramienta. Un changelog manual en un equipo de 1 tiene dos destinos: se desactualiza o consume tiempo — ambos peores que el generado.

### 02.1 La elección: release-please sobre changesets

| Criterio | release-please | changesets |
|---|---|---|
| Input | los commits que **ya escribes** (conventional) | archivo `.changeset/*.md` extra **por cada cambio** |
| Trabajo extra por cambio | cero | un archivo + una decisión de bump |
| Diseñado para | apps/servicios con un flujo de release | monorepos de **librerías** npm multi-paquete |
| Modo de operación | mantiene un "Release PR" siempre actualizado; mergearlo = release | comando de versionado + publish |

**Por qué:** changesets brilla cuando varios autores deciden bumps de varios paquetes publicados a npm — nada de eso existe aquí. release-please convierte la disciplina de commits que el handbook ya exige en changelog + versión + tag + GitHub Release, sin ningún paso nuevo en el día a día. El flujo resultante: trabajas normal → release-please mantiene abierto un PR ("chore(main): release 1.4.0") con el CHANGELOG acumulado → cuando decides releasear, **mergeas ese PR** y todo lo demás (tag, GitHub Release, changelog commiteado, bump de `package.json`) ocurre solo.

### 02.2 El workflow

**Implementación (`.github/workflows/release-please.yml`)** — cumple [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 07: es action de terceros (googleapis, no `actions/*`) en un workflow con permisos de escritura → **pin por SHA obligatorio**:

```yaml
name: release-please

on:
  push:
    branches: [main]

permissions:
  contents: write          # crea tags, releases y el commit del CHANGELOG
  pull-requests: write     # mantiene el Release PR

concurrency:
  group: release-please
  cancel-in-progress: false

jobs:
  release-please:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: googleapis/release-please-action@<SHA>   # v5.x — SHA real (gh api repos/googleapis/release-please-action/commits/vX.Y.Z --jq .sha); verificar versión vigente
        with:
          release-type: node      # lee/actualiza la versión en package.json
```

**Notas:**
- `release-type: node` versiona `package.json` y genera `CHANGELOG.md` en la raíz. Para un repo sin `package.json` relevante, `release-type: simple`.
- Estos permisos de escritura son la excepción justificada al `contents: read` de los demás workflows ([03_CI_CD.md](../Pipelines/03_CI_CD.md) sección 07): es exactamente el trabajo de este workflow, y por eso el pin por SHA aquí no es negociable.
- Para configuración más fina, release-please acepta `release-please-config.json` + `.release-please-manifest.json` en la raíz — adoptarlos solo cuando el default moleste, no de entrada. El caso típico que lo amerita: querer que `chore:`/`refactor:` no ensucien el changelog, o dar nombres legibles a las secciones (verificar el schema vigente en el repo de release-please):

```jsonc
// release-please-config.json — opcional; el default sirve para arrancar
{
  "packages": {
    ".": {
      "release-type": "node",
      "changelog-sections": [
        { "type": "feat", "section": "Nuevo" },
        { "type": "fix", "section": "Arreglado" },
        { "type": "perf", "section": "Rendimiento" },
        { "type": "chore", "hidden": true },      // ruido interno: fuera del changelog
        { "type": "refactor", "hidden": true },
        { "type": "test", "hidden": true }
      ]
    }
  }
}
```

```json
{ ".": "1.0.0" }
```

(El segundo bloque es `.release-please-manifest.json` — la versión actual por paquete; con un solo paquete, una línea.)

### 02.3 El changelog se escribe al commitear

**[REQUIRED]** La calidad del CHANGELOG generado es exactamente la calidad de las descripciones de los commits — cada `feat:`/`fix:` de `main` se convierte en una línea que un lector va a ver. Por eso la descripción del commit se escribe **para el changelog**: qué cambió desde afuera, no cómo se implementó.

```
✅ feat(billing): add annual plan with 2 months discount
   → línea de changelog útil

❌ feat(billing): refactor PlanSelector + hook fixes
   → "refactor" no es un feat, y la línea no dice nada al lector
```

**Por qué:** es el mismo dato escrito una sola vez en el único momento en que el contexto está fresco. Si el commit se escribe mal, la alternativa es editar el changelog a mano después — es decir, el proceso manual que este documento elimina.

**[RECOMMENDED]** Fallback manual — si la herramienta se rompe o el repo no la tiene aún, la regla agnóstica (versión + tag + changelog por release) se cumple a mano; es más lento pero idéntico en resultado:

```bash
npm version minor                        # bump package.json + tag local vX.Y.Z
git push --follow-tags
gh release create v1.4.0 --generate-notes   # notas desde los commits/PRs del rango
```

---

## 03. Tags y GitHub Releases

**[REQUIRED]** Cada release produce un **tag anotado `vX.Y.Z` sobre el commit exacto** y una GitHub Release con el fragmento del changelog. Con release-please esto es automático al mergear el Release PR; la regla existe para que también se cumpla si algún día la herramienta cambia.

**Por qué:** el tag es la respuesta a las dos preguntas de todo incidente: *"¿qué versión exacta está en producción?"* y *"¿qué cambió entre la que funcionaba y esta?"* (`git diff v1.3.0..v1.4.0`). Sin tags, esas respuestas requieren arqueología de historial con producción caída — el peor momento para hacer arqueología. Además el tag es el punto de rollback por Git: `git revert`/re-deploy del tag anterior ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) secciones 02-03).

```bash
# ¿Qué hay en producción y qué cambió?
git tag --sort=-creatordate | head -3
git log --oneline v1.3.0..v1.4.0
git diff v1.3.0..v1.4.0 -- src/
```

**[REQUIRED]** Los tags de release son **inmutables**: un tag nunca se borra ni se re-apunta a otro commit. Si el release estaba mal, el siguiente release (patch) lo corrige — la historia de versiones registra lo que pasó, incluido el error.

**Por qué:** un tag movido convierte cada referencia histórica ("el bug apareció en v1.4.0") en información falsa retroactivamente, y es el mismo vector de confianza que motiva el pin por SHA de [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 07: lo que un nombre de versión señala no debe cambiar bajo tus pies.

**[RECOMMENDED]** CHANGELOG (para devs/IA que leen el repo) ≠ notas para usuarios. Cuando un release trae algo visible que amerita anuncio (in-app, email), ese texto se redacta aparte en lenguaje de usuario — el changelog técnico generado no se pega en un email. La mayoría de releases de un SaaS no ameritan anuncio; el changelog siempre existe igual.

---

## 04. Definición de release — cuándo algo ES un release

**[REQUIRED]** Un release existe solo cuando se cumplen **las tres**, en orden:

1. **Pipeline verde completo** sobre el commit releaseado: los gates de [03_CI_CD.md](../Pipelines/03_CI_CD.md) (lint, typecheck, unit+coverage, build, E2E smoke) — no un run viejo de otra rama, no "corrió ayer".
2. **Deploy por el camino estándar**: staging → smoke staging → producción, vía `deploy.yml` — nunca un `wrangler deploy` manual "porque es el release" (el deploy manual es la vía de emergencia de DEPLOY_AND_FAILURES, no la de release).
3. **Smoke post-deploy contra producción verde.** Un deploy sin smoke verificado **no está terminado** ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 01) — y por tanto no se tagea como release.

**Por qué el orden:** el tag debe apuntar a un estado *demostrado* bueno, no a uno *presuntamente* bueno. Si el smoke de producción falla, no hay release: hay un incidente, y aplica el runbook — **rollback primero, diagnóstico después** ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 06). El Release PR de release-please se mergea *después* de ver producción sana, no antes.

### 04.1 El ciclo completo, de commit a versión

```
commit conventional a main
        │
        ▼
deploy.yml: gates → staging → smoke → prod → smoke   (03_CI_CD.md §05 — CADA push)
        │                                  │
        │                                  └─ smoke rojo → rollback (runbook), no hay release
        ▼
release-please actualiza el Release PR (changelog + versión propuesta acumulándose)
        │
        ▼  (cuando decides "cortar versión" — prod sana, <1 semana acumulada)
merge del Release PR
        │
        ▼
tag vX.Y.Z + GitHub Release + CHANGELOG.md commiteado — automático
```

**[RECOMMENDED]** Leído de otra forma: **deploy continuo + release nombrado cuando aporta.** Cada merge a `main` llega a producción validado (eso es el deploy); el release agrupa lo desplegado bajo un número y un changelog cuando tiene sentido comunicarlo o anclarlo. Lo mejor de ambos mundos sin ceremonia.

### 04.2 Hotfix y release

**[REQUIRED]** Un hotfix de incidente (`fix:` urgente) sigue el flujo normal si el pipeline está sano — el pipeline tarda <10 min y es exactamente el tipo de cambio apurado que más lo necesita. La vía de emergencia con gates saltados existe solo bajo el procedimiento de [10_PLAYBOOK.md](10_PLAYBOOK.md), y al cerrar el incidente: el commit pasa el pipeline retroactivamente y se mergea el Release PR resultante — así el patch queda numerado y el changelog cuenta el incidente. Un hotfix sin release posterior es un cambio en producción que ninguna versión documenta.

### 04.3 Releases de varias piezas (frontend + worker + migración)

**[REQUIRED]** Cuando un release toca más de una pieza desplegable, el orden lo dicta la compatibilidad, no el número de versión: **migración expansiva de DB → worker → frontend → (días después) contracción de DB** — el patrón expandir→migrar→contraer de [`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 05. El tag del release se pone cuando **todas** las piezas están desplegadas y el smoke pasó; nunca se tagea con la combinación a medias (el runbook B1 de DEPLOY_AND_FAILURES existe precisamente para el deploy multi-pieza inconsistente).

**Por qué:** el rollback de un release multi-pieza solo es seguro si cada pieza intermedia era compatible con la anterior. Si el frontend nuevo asume un endpoint que el worker viejo no tiene, el orden inverso rompe durante la ventana de propagación aunque "todo esté en el mismo release".

### 04.4 Sin pre-releases ni release candidates

**[RECOMMENDED]** En este contexto no existen `v1.4.0-rc.1` ni betas versionadas. Los RC resuelven un problema de librerías y equipos grandes: validar con terceros antes de comprometerse a un contrato. Un SaaS de dev solo ya tiene mecanismos mejores y más baratos para lo mismo: preview deployments por rama (el "beta" gratuito de cada PR), staging con smoke en cada push a `main`, y feature flags (sección 05) para exponer un feature a producción sin exponerlo a usuarios. Añadir RCs sería duplicar esa maquinaria con un esquema de numeración extra que nadie consume.

### 04.5 La ventana de observación post-release

**[RECOMMENDED]** El smoke verde es el mínimo automatizado, no el final: los ~30 minutos posteriores al release se trabaja con producción "de reojo". Qué mirar, en orden de señal:

1. **Logs en vivo del worker** (`wrangler tail <worker>`) durante los primeros minutos — los 500 nuevos aparecen aquí antes que en cualquier reporte de usuario.
2. **El flujo principal a mano, una vez**, como usuario real — el smoke E2E prueba lo que se le dijo que pruebe; un humano nota lo que no se le ocurrió automatizar (estilos rotos, textos mal, lentitud).
3. **Panel de errores/latencia** que exista (dashboard de Cloudflare, logs de Supabase) comparado contra la línea base de ayer.

**Por qué:** la mayoría de los deploys rotos que pasan un smoke se manifiestan en los primeros minutos de tráfico real. Media hora de atención barata inmediatamente después cuesta menos que el mismo bug descubierto mañana por un usuario — y con la memoria del cambio todavía fresca, el diagnóstico es trivial. Esto es también el argumento operativo detrás del anti-patrón 1 de la sección 06: si no puedes dar esa media hora, no es el momento de releasear.

---

## 05. Feature flags — separar deploy de release

**[RECOMMENDED]** Cuando un cambio debe llegar a producción **desactivado** (feature a medias que no cabe en una rama corta, cambio riesgoso que quieres encender con producción observada, algo que se anuncia un día concreto), se usa un feature flag simple. Deploy = el código llega al servidor; release (del feature) = el flag se enciende.

**La escalera de sofisticación — subir solo el peldaño necesario:**

1. **Env var / variable de build** (`VITE_FEATURE_X=true` en Pages, var en `wrangler.toml` por env): el flag más barato. Sirve cuando encender/apagar puede esperar un redeploy (~2 min) y el estado es por-entorno (encendido en staging, apagado en prod). **Empieza aquí.**
2. **Flag en KV de Cloudflare** (el worker lee `FLAGS.get("feature_x")`): encendido/apagado **en segundos, sin deploy** (`wrangler kv key put`). Amerita cuando el apagado debe ser inmediato — el flag es también tu kill-switch si el feature falla en producción: apagar el flag es más rápido que cualquier rollback.
3. **Servicio de flags (por usuario, porcentajes, targeting):** para un dev solo, casi nunca — es infraestructura que mantener para un problema (rollouts graduales a segmentos) que todavía no tienes. Se adopta cuando exista la necesidad real, no antes.

**Por qué:** las ramas largas son la alternativa a los flags, y son peores — divergen, acumulan conflictos y violan la estrategia trunk-based de [`GITHUB_STANDARD.md`](../../07_DevOps/GITHUB_STANDARD.md) sección 01. El flag permite mergear e integrar a diario código apagado.

**Implementación (peldaño 1 — env var en ambos lados del stack):**

```toml
# wrangler.toml — worker
[vars]
FEATURE_NEW_CHECKOUT = "false"

[env.staging.vars]
FEATURE_NEW_CHECKOUT = "true"     # encendido en staging, apagado en prod
```

```ts
// Frontend (Vite) — la variable se fija en el dashboard de Pages por entorno
// (Preview vs Production — DEPLOY_AND_FAILURES §04) y se evalúa en build:
const newCheckout = import.meta.env.VITE_FEATURE_NEW_CHECKOUT === 'true';
return newCheckout ? <CheckoutV2 /> : <CheckoutV1 />;
```

```bash
# Peldaño 2 — kill-switch en KV, sin deploy:
wrangler kv key put --binding=FLAGS feature_new_checkout "on"
wrangler kv key put --binding=FLAGS feature_new_checkout "off"   # apagado en segundos
```

**[REQUIRED]** La contraparte si usas flags: **todo flag tiene fecha de muerte** — cuando el feature queda encendido para todos, el flag y el código muerto del camino viejo se borran en la misma semana. Un `if (flags.x)` permanente es deuda que multiplica los caminos a testear: con N flags vivos hay 2^N combinaciones posibles en producción y tu suite E2E prueba una. Los tests del feature nuevo se escriben con el flag encendido en el entorno de test — un feature que solo se testea apagado no está testeado.

---

## 06. Qué NO hacer

**[REQUIRED]** Anti-patrones de release, cada uno con su porqué — la lista existe porque los tres son tentadores justo cuando más daño hacen:

1. **Release viernes por la noche (o justo antes de vacaciones/viaje).** El costo de un release no es el deploy — es la *ventana de reacción* si sale mal. Un release a las 19:00 del viernes convierte cualquier fallo en un incidente de fin de semana atendido con cansancio, o peor, no atendido. Regla práctica: releasear cuando las próximas ~2 horas puedes mirar producción. Para un dev solo eso significa mañana o mediodía de día laboral. (Excepción obvia: el hotfix de un incidente activo se deploya cuando toca — eso es [10_PLAYBOOK.md](10_PLAYBOOK.md), no un release.)

2. **Release sin pipeline.** "Es solo un cambio de texto" es el perfil exacto del deploy que rompe producción ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 01): lo grande se prueba con miedo, lo chico se pushea con confianza injustificada. El pipeline tarda <10 min y corre solo — saltárselo no ahorra tiempo, ahorra *espera*, y cobra en incidentes.

3. **Acumular 3 semanas de cambios en un release.** El tamaño del release es el tamaño de tu superficie de diagnóstico: si el release lleva 40 commits y producción se rompe, el sospechoso es "alguno de 40"; si lleva 3, el diagnóstico es casi inmediato y el rollback casi gratis. Los releases grandes además se vuelven eventos con miedo, y el miedo los espacia más — el círculo vicioso exacto que el deploy continuo rompe. Regla práctica: si el Release PR de release-please acumula más de ~1 semana o más de ~15 commits, se mergea ya.

**[RECOMMENDED]** Otros dos menores pero reales: no releasear **para** salir a comer/dormir ("lo dejo deployando") — el smoke post-deploy se mira, no se presume; y no encadenar release + migración destructiva de DB en el mismo movimiento — la contracción de esquema va días después, con el patrón expandir→migrar→contraer ([`DEPLOY_AND_FAILURES_STANDARD.md`](../../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) sección 05).

---

## Checklist final

**Versionado y changelog**
- [ ] ¿SemVer pragmático con la versión calculada por herramienta desde conventional commits — cero decisión manual de número?
- [ ] ¿`1.0.0` desde el primer release con usuarios reales (sin quedarse en `0.x` "por humildad")?
- [ ] ¿CHANGELOG generado (release-please), nunca escrito a mano?
- [ ] ¿`release-please.yml` con `permissions` explícitos y la action pineada por SHA real (es de terceros con permisos de escritura)?
- [ ] ¿Descripciones de `feat:`/`fix:` escritas para el lector del changelog (qué cambió, no cómo)?

**El release en sí**
- [ ] ¿Cada release tiene tag `vX.Y.Z` sobre el commit exacto + GitHub Release con changelog?
- [ ] ¿Release solo con: pipeline verde sobre ese commit + deploy por el camino estándar + smoke de producción verde?
- [ ] ¿Smoke rojo = incidente y rollback por runbook, no "release con asterisco"?
- [ ] ¿El Release PR se mergea después de ver producción sana, documentando lo ya desplegado?
- [ ] ¿Hotfix de emergencia cerrado con pipeline retroactivo + release patch que lo documenta?
- [ ] ¿Release multi-pieza en orden de compatibilidad (DB expansiva → worker → frontend → contracción después) y tageado solo con todo desplegado?
- [ ] ¿Sin RCs ni pre-releases — previews por rama, staging y flags cumplen ese rol?
- [ ] ¿~30 min de observación post-release (`wrangler tail`, flujo principal a mano, panel de errores)?

**Flags y anti-patrones**
- [ ] ¿Feature incompleto o riesgoso detrás de flag (env var primero; KV cuando el apagado debe ser inmediato), no en rama larga?
- [ ] ¿Todo flag tiene fecha de muerte y se borra junto con el código del camino viejo; el feature se testea con el flag encendido?
- [ ] ¿Ningún release en viernes noche / antes de ausencias; siempre con ~2h de ventana de observación?
- [ ] ¿Cero releases sin pipeline, sin importar el tamaño del cambio?
- [ ] ¿Release PR mergeado antes de acumular ~1 semana / ~15 commits?
