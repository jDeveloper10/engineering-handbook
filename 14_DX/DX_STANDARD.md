---
title: "Estándar de Developer Experience"
category: 14_DX
tags: [dx, tooling, scripts, editor]
summary: "Un solo procedimiento de arranque de proyecto, scripts npm idénticos en todos los repositorios, configuración de editor versionada y snippets para los patrones repetidos."
keywords: [dx, bootstrap, scripts, npm, editor, snippets, template]
updated: 2026-07-27
status: current
---

# DX STANDARD

> Documento del dominio Developer Experience (14). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md): reglas `[REQUIRED]`/`[RECOMMENDED]`, capa agnóstica + implementación de referencia (Windows 10 + PowerShell, VS Code + Claude Code, React+Vite+TS / Cloudflare Workers / Supabase, GitHub).
>
> **Objetivo del dominio, en una línea medible:** minimizar dos tiempos — el que va de "idea" a "primer deploy en producción" (proyecto nuevo), y el que va de "abro el proyecto" a "estoy productivo" (proyecto existente). Todo lo demás en este documento existe para bajar uno de esos dos números.
>
> **Relación con otros documentos:**
> - El setup de QA copy-paste (<1h) **ya está definido** en [`06_Testing/07_AUTOMATION_GUIDE.md`](../06_Testing/Guides/07_AUTOMATION_GUIDE.md) — este documento lo referencia, no lo repite. El contrato de scripts npm (sección 02 de aquel documento) es la base de la sección 02 de este.
> - Las plantillas de documentos (README, CLAUDE.md, ci.yml, PRD...) viven en [`Engineering-OS/26-Templates.md`](../Engineering-OS/26-Templates.md) — este documento las hereda y, donde hace falta (CLAUDE.md), las extiende declarándolo.
> - La automatización A1 ("crear proyecto nuevo en un comando") está registrada en [`Engineering-OS/23-Automations.md`](../Engineering-OS/23-Automations.md) — la sección 01 de este documento define el **contenido** de esa automatización; el registro de su estado vive allá.
> - El checklist operativo paso a paso de proyecto nuevo vive en [`PROJECT_BOOTSTRAP_CHECKLIST.md`](PROJECT_BOOTSTRAP_CHECKLIST.md) (este mismo dominio).

---

## 01. Bootstrap de proyecto nuevo — un solo procedimiento

**[REQUIRED]** Existe **un** comando/procedimiento documentado que crea un proyecto nuevo con todo el stack configurado — estructura, configs, CI, handbook linkeado — en minutos, no en horas. Nadie configura un proyecto "a mano, de memoria": si el procedimiento no cubre algo, se corrige el procedimiento, no se improvisa.

**Por qué:** la auditoría de 2026-07 ([23-Automations](../Engineering-OS/23-Automations.md) A1) encontró ~95 proyectos con configuración inconsistente: 46% sin git, ~50% sin README, 0 con CLAUDE.md, 0 con CI. Esa dispersión no es falta de disciplina — es el costo natural de configurar a mano: cada proyecto nace como una foto de lo que recordabas ese día. Un template ejecutable convierte "el estándar" de documento a punto de partida físico: el proyecto nace conforme porque no hay forma de nacer distinto. Además, cada decisión de configuración (¿qué eslint? ¿qué tsconfig?) se toma **una vez** en el template en vez de N veces en N proyectos.

### 1.1 Dónde vive: repo template de GitHub

**Regla (agnóstica):** el punto de partida es un repositorio plantilla versionado, con el mismo ciclo de vida que cualquier código (se mejora por commits, tiene historia, se puede revisar). No es un zip, ni una carpeta que se copia, ni un gist.

**Implementación:** repo **`JCDIGITALL/template-saas`** marcado como *template repository* en GitHub. Crear proyecto:

```powershell
gh repo create JCDIGITALL/<nombre> --template JCDIGITALL/template-saas --private --clone
```

El script `new-project.ps1` de A1 ([23-Automations](../Engineering-OS/23-Automations.md)) envuelve este comando y añade lo que el template no puede saber: nombre real en `package.json`/`wrangler.toml`, registro en el MCP jcdigital, carpeta en la ruta canónica de [07-Project-Structure](../Engineering-OS/07-Project-Structure.md). Mientras A1 sea `propuesta`, el comando `gh` de arriba + el [PROJECT_BOOTSTRAP_CHECKLIST.md](PROJECT_BOOTSTRAP_CHECKLIST.md) **son** el procedimiento oficial — el checklist es ejecutable a mano hoy y se convierte en el guion del script mañana.

### 1.2 Contenido del template — el manifiesto

**[REQUIRED]** El template contiene exactamente esto (cada pieza referencia el estándar que la define — el template es la *materialización* de esos estándares, no una segunda fuente de verdad):

| Archivo/carpeta | Contenido | Estándar de origen |
|---|---|---|
| `package.json` | Scripts estandarizados (sección 02), deps del stack | [07_AUTOMATION_GUIDE §02](../06_Testing/Guides/07_AUTOMATION_GUIDE.md) |
| `tsconfig.json` + `tsconfig.app.json` + `tsconfig.node.json` | Los del template Vite react-ts, `strict: true` | Vite + [FRONTEND_REACT_STANDARD](../01_Frontend/Core/FRONTEND_REACT_STANDARD.md) |
| `eslint.config.js` | Flat config esencial | [07_AUTOMATION_GUIDE §05](../06_Testing/Guides/07_AUTOMATION_GUIDE.md) |
| `.prettierrc` | `{ "singleQuote": true, "semi": true, "printWidth": 100 }` | Este documento (única fuente: nadie más define formato) |
| `.gitignore` | El del GITHUB_STANDARD §02.1 (secretos, generados, ruido de SO) | [GITHUB_STANDARD §02.1](../07_DevOps/GITHUB_STANDARD.md) |
| `wrangler.toml` | Base con `name` placeholder, **sin secretos en `[vars]`** | [CLOUDFLARE_PLATFORM_STANDARD](../08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md), [SECURITY §03](../05_Security/SECURITY_ENGINEERING_STANDARD.md) |
| `src/` con `features/`, `components/`, `lib/` | Estructura por feature con subcarpetas fijas | [FRONTEND_REACT_STANDARD §01](../01_Frontend/Core/FRONTEND_REACT_STANDARD.md) |
| `tests/` (`unit/`, `integration/`), `e2e/` + configs de Vitest/Playwright | Setup QA completo, con un test trivial y un spec `@smoke` que pasan | [07_AUTOMATION_GUIDE §§01-04](../06_Testing/Guides/07_AUTOMATION_GUIDE.md) |
| `.github/workflows/ci.yml` + `deploy.yml` + `nightly.yml` | Pipeline por etapas | [03_CI_CD](../06_Testing/Pipelines/03_CI_CD.md) |
| `supabase/migrations/` (vacía) + `supabase/config.toml` | Migraciones versionadas desde el día 0 | [DATABASE_ENGINEERING_STANDARD](../04_Database/DATABASE_ENGINEERING_STANDARD.md) |
| `.vscode/settings.json` + `extensions.json` + snippets | Sección 03 y 04 de este documento | Este documento |
| `CLAUDE.md` | Plantilla de la sección 05 con `<>` por rellenar | Este documento (extiende T2 de 26-Templates) |
| `README.md` | Plantilla T1 con `<>` por rellenar | [26-Templates T1](../Engineering-OS/26-Templates.md) |
| `.env.example` + `.dev.vars.example` | Nombres de variables sin valores | [SECURITY §03](../05_Security/SECURITY_ENGINEERING_STANDARD.md) |
| `.gitleaks.toml`, hooks (`simple-git-hooks` + `lint-staged`) | Escaneo y gates locales | [07_AUTOMATION_GUIDE §§07-08](../06_Testing/Guides/07_AUTOMATION_GUIDE.md) |

**Implementación de referencia — `wrangler.toml` base del template** (lo mínimo que no viola [SECURITY §03](../05_Security/SECURITY_ENGINEERING_STANDARD.md)):

```toml
name = "PLACEHOLDER-worker"          # ← paso 2 del bootstrap lo renombra
main = "apps/worker/src/index.ts"
compatibility_date = "2026-01-01"    # actualizar al crear el proyecto, luego congelar por proyecto

# [vars] SOLO para valores públicos/no sensibles (feature flags, URLs).
# Secretos: `wrangler secret put` (prod) y .dev.vars (local) — NUNCA aquí.
[vars]
ENVIRONMENT = "development"

[observability]
enabled = true                       # logs estructurados desde el día 0 (CLOUDFLARE_PLATFORM_STANDARD §14)
```

**[REQUIRED]** El template **compila y pasa `npm run check` tal cual se clona** (con nombres placeholder). Un template que necesita arreglos antes del primer commit no es un template — es una lista de tareas disfrazada.

**[RECOMMENDED]** El template se re-valida trimestralmente: clonarlo, `npm install`, `npm run check`. Las dependencias envejecen; un template roto es peor que no tener template porque destruye la confianza en el procedimiento entero.

**Por qué un solo template y no varios:** hoy el stack canónico es uno (React+Vite+TS + Worker + Supabase). Un proyecto solo-frontend o solo-worker **borra** lo que no usa (borrar es un `rm -r` de 10 segundos; añadir a mano es una hora con errores). Se crea un segundo template solo cuando un tipo de proyecto haya necesitado borrar más de la mitad del template 3+ veces — misma lógica que la regla de Nivel 3 del [00_HANDBOOK_FORMAT](../00_HANDBOOK_FORMAT.md) §4.

---

## 02. Scripts npm — idénticos en todos los proyectos

**[REQUIRED]** Los nombres de scripts de `package.json` son **el contrato definido en [07_AUTOMATION_GUIDE.md §02](../06_Testing/Guides/07_AUTOMATION_GUIDE.md)** — este documento no los redefine, los eleva a regla de DX: `dev`, `build`, `preview`, `test`, `test:unit`, `test:watch`, `test:e2e`, `test:e2e:smoke`, `lint`, `typecheck`, `check`, `prepare`. Idénticos en todos los proyectos, sin alias creativos, sin variantes por proyecto.

**Regla operativa de DX:** en cualquier proyecto del portafolio, sin leer nada, estos cuatro comandos hacen lo esperado:

```powershell
npm run dev      # levanta el entorno local
npm run check    # "¿puedo pushear?" — lint + typecheck + test + build, igual que el CI
npm run test     # unit+integration con gate de coverage
npm run build    # produce el artefacto de deploy
```

El deploy no es un script npm ad-hoc por proyecto: **deploy = push a `main`** (lo ejecuta `deploy.yml`, [03_CI_CD §05](../06_Testing/Pipelines/03_CI_CD.md)). Si un proyecto necesita deploy manual de emergencia, el comando exacto está en su `README.md` y su `CLAUDE.md` — nunca solo en la memoria.

**Por qué:** un dev (o una IA) que cambia de proyecto no debe reaprender comandos — el costo de "¿aquí era `npm test` o `npm run test:all`?" es pequeño por vez pero se paga en cada cambio de contexto, y para una IA es peor: inventa el script que no existe. Los nombres idénticos son también lo que permite que `ci.yml` y los git hooks sean **el mismo archivo** en todos los repos.

**[REQUIRED]** Si un proyecto necesita un script extra (`db:types`, `seed`...), se **añade** sin tocar los nombres del contrato, y se documenta en el `CLAUDE.md` del proyecto (sección 05). Renombrar o eliminar un script del contrato rompe CI, hooks y memoria muscular a la vez — no se hace.

---

## 03. Configuración de editor versionada

**[RECOMMENDED]** Cada repo versiona su configuración de editor: el formato y los autofixes ocurren **al guardar**, idénticos en cualquier máquina (o tras un reinstall de Windows), sin depender de la configuración global del usuario.

**Por qué:** "format on save" es la diferencia entre un diff limpio y un PR con 200 líneas de cambios de indentación. Versionarlo en el repo (y no en la config de usuario) significa que el entorno se auto-configura al abrir la carpeta — un paso menos de onboarding, y una fuente menos de "en mi máquina se ve distinto". Es RECOMMENDED y no REQUIRED porque el gate real de formato/lint son los hooks y el CI ([07_AUTOMATION_GUIDE §08](../06_Testing/Guides/07_AUTOMATION_GUIDE.md)) — el editor es comodidad, el hook es la ley.

**Implementación — `.vscode/settings.json` (vive en el template):**

```jsonc
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" },
  "typescript.tsdk": "node_modules/typescript/lib",   // el TS del proyecto, no el del editor
  "files.eol": "\n",                                  // LF también en Windows — diffs limpios cross-OS
  "search.exclude": { "**/node_modules": true, "**/dist": true, "**/coverage": true }
}
```

**Implementación — `.vscode/extensions.json` (las esenciales, no un catálogo):**

```jsonc
{
  "recommendations": [
    "dbaeumer.vscode-eslint",        // lint en el editor (mismo eslint.config.js del repo)
    "esbenp.prettier-vscode",        // format on save
    "bradlc.vscode-tailwindcss",     // autocomplete + lint de clases Tailwind
    "anthropic.claude-code",         // Claude Code integrado al editor
    "supabase.vscode-supabase",      // opcional: verificar disponibilidad/nombre vigente en el marketplace
    "cloudflare.vscode-wrangler"     // opcional: idem
  ]
}
```

**[RECOMMENDED]** La lista se mantiene en 5-8 extensiones. Cada extensión extra es RAM, ruido y una pregunta más en el onboarding; si una extensión no se usa semanalmente, sale de `recommendations`.

---

## 04. Snippets — los patrones repetidos, a un tab de distancia

**[RECOMMENDED]** Los patrones de código que el handbook define y que se escriben una y otra vez existen como snippets versionados en el repo (llegan con el template, sección 01), de forma que la estructura correcta cueste menos que improvisar una incorrecta.

**Regla (agnóstica):** un snippet por cada patrón que (a) tiene estructura obligatoria definida en un estándar y (b) se crea ≥1 vez por semana. Hoy son cuatro:

| Prefijo | Genera | Estructura según |
|---|---|---|
| `hb-component` | Componente React: función nombrada, props tipadas, un archivo = una responsabilidad | [FRONTEND_REACT_STANDARD](../01_Frontend/Core/FRONTEND_REACT_STANDARD.md) |
| `hb-hook` | Hook de datos: TanStack Query envolviendo la función de `api/` | [FRONTEND_REACT_STANDARD §7](../01_Frontend/Core/FRONTEND_REACT_STANDARD.md) |
| `hb-route` | Ruta de Worker: validación de entrada → auth → lógica → envelope de respuesta | [03_API/API_ENGINEERING_STANDARD](../03_API/API_ENGINEERING_STANDARD.md), [SECURITY §04](../05_Security/SECURITY_ENGINEERING_STANDARD.md) |
| `hb-migration` | Migración SQL: comentario de intención, cambio aditivo, RLS si crea tabla | [DATABASE_ENGINEERING_STANDARD](../04_Database/DATABASE_ENGINEERING_STANDARD.md) |

**Implementación de referencia — un snippet del archivo (formato nativo de VS Code):**

```jsonc
// .vscode/handbook.code-snippets (extracto)
{
  "Hook de datos (TanStack Query)": {
    "prefix": "hb-hook",
    "scope": "typescript,typescriptreact",
    "body": [
      "import { useQuery } from '@tanstack/react-query';",
      "import { get${1:Entity} } from '../api/${2:entity}';",
      "",
      "export function use${1:Entity}(id: string) {",
      "  return useQuery({",
      "    queryKey: ['${2:entity}', id],",
      "    queryFn: () => get${1:Entity}(id),",
      "  });",
      "}"
    ],
    "description": "Hook de datos según FRONTEND_REACT_STANDARD §7: componente → hook → api/"
  }
}
```

**Dónde viven y formato:** `.vscode/handbook.code-snippets` en cada repo (formato nativo de snippets de VS Code, scope por lenguaje). La **copia maestra vive en el template** `template-saas` — se edita allá y llega a los proyectos nuevos sola; a los proyectos viejos se copia el archivo (1 archivo, sin build).

**Por qué `.code-snippets` y no snippets globales de usuario:** los globales mueren con la máquina y no le sirven a una IA; el archivo en el repo sobrevive reinstalls, viaja con el proyecto y es **legible por Claude Code** — un snippet versionado es simultáneamente atajo de teclado para el humano y ejemplo canónico para la IA. Prefijo `hb-` para que el autocompletado los agrupe y no colisionen con snippets de extensiones.

**Nota de límites:** un snippet es un esqueleto de ~15 líneas, no una plantilla de feature completa. Si el "snippet" necesita lógica de generación (nombres derivados, múltiples archivos), ya no es un snippet — es un generador, y entra por [23-Automations](../Engineering-OS/23-Automations.md) como propuesta.

---

## 05. CLAUDE.md por proyecto — el contexto que hace útil a la IA

**[REQUIRED]** Todo proyecto activo tiene un `CLAUDE.md` en la raíz. Extiende la plantilla T2 de [26-Templates](../Engineering-OS/26-Templates.md) (misma alma: qué es, stack/comandos, mapa, reglas) con lo que la práctica demostró que falta: **la lista explícita de estándares del handbook que aplican** y las verificaciones que la IA debe correr antes de dar algo por terminado. T2 queda como la versión mínima para proyectos legacy; los proyectos nuevos nacen con esta.

**Por qué:** Claude Code sin `CLAUDE.md` re-descubre el proyecto en cada sesión — y lo que no descubre, lo inventa (scripts que no existen, estructuras que no son las del repo, estándares que no aplican). El `CLAUDE.md` es la memoria externa del proyecto: convierte cada sesión de "explorar + adivinar" en "leer 40 líneas + trabajar". Es el archivo con mejor ratio esfuerzo/beneficio de todo el repo: ~15 minutos de escribirlo, minutos ahorrados en **cada** sesión de IA para siempre.

**Plantilla completa (así viene en el template, con `<>` por rellenar):**

```markdown
# <nombre> — contexto para IAs

## Qué es
<2-3 líneas: qué hace, para quién, estado (producción con clientes reales / desarrollo / experimento).>

## Stack y comandos
React 19 + Vite + TS + Tailwind · Cloudflare Workers (wrangler) · Supabase (Auth + Postgres + RLS)
- `npm run dev` — local (puerto <X>)
- `npm run check` — lint + typecheck + test + build; DEBE pasar antes de todo push
- Deploy: push a `main` = deploy vía CI (`deploy.yml`). Manual de emergencia: <comando o "no hay">
- Scripts extra de este proyecto: <lista o "ninguno">

## Estándares que aplican (E:\ENGINEERING_HANDBOOK)
Leer las reglas REQUIRED antes de generar código del área que toques:
- 01_Frontend/FRONTEND_REACT_STANDARD.md — estructura de features, hooks, data fetching
- 03_API/API_ENGINEERING_STANDARD.md — envelope de respuestas, error.codes
- 05_Security/SECURITY_ENGINEERING_STANDARD.md — §03 secretos, §04 auth, §05 RLS
- 04_Database/DATABASE_ENGINEERING_STANDARD.md — todo cambio de esquema es migración
- 06_Testing/01_QA_STRATEGY.md + 07_AUTOMATION_GUIDE.md — qué se testea y con qué
- <quitar los que no apliquen; añadir patrones específicos, ej. FRONTEND_CRUD_PATTERNS>

## Mapa del código
<3-6 líneas: qué vive dónde. Ej.: src/features/orders = flujo principal de negocio;
apps/worker = API; supabase/migrations = esquema (NUNCA tocar el dashboard).>

## Reglas específicas del proyecto
- <qué NO tocar y por qué — ej.: worker de pagos maneja dinero real: todo cambio lleva test>
- <decisiones ya tomadas que no se re-litigan — formato T8 mini-ADR de 26-Templates>

## Verificación antes de dar por terminado
- `npm run check` en verde. <+ pasos manuales si los hay: "probar flujo de pago en staging">
```

**[REQUIRED]** El `CLAUDE.md` se actualiza cuando cambia lo que describe (comando nuevo, decisión nueva, área nueva del mapa) — en el mismo commit que el cambio. Un `CLAUDE.md` desactualizado es peor que ninguno: la IA confía en él sin verificar.

**[RECOMMENDED]** Mantenerlo por debajo de ~80 líneas. Es un índice con opiniones, no documentación: cada línea que la IA debe leer en cada sesión cuesta contexto; lo que sea explicación larga va al README o al handbook y se referencia.

---

## 06. Documentación mínima de proyecto

**[REQUIRED]** Todo proyecto tiene un `README.md` según la plantilla T1 de [26-Templates](../Engineering-OS/26-Templates.md), con una regla de calidad adicional que T1 no explicita: la sección de setup lleva de "clon fresco" a "app corriendo local" en **máximo 5 pasos, y esos pasos están verificados** — alguien (tú en 6 meses, o una IA) los ejecutó tal cual están escritos y funcionaron.

**Por qué 5 pasos y verificados:** el README de setup es la única documentación con test posible: o funciona o no. Más de 5 pasos casi siempre significa que hay configuración manual que debería estar en el template, en un script o en `.env.example` — cada paso extra es fricción de onboarding multiplicada por cada vez que se retoma el proyecto. "Verificados" porque un setup que "debería funcionar" y no funciona cuesta más que no tener README: se pierde tiempo confiando en él.

**[RECOMMENDED]** Cuando el paso 3 de un setup falla, la corrección del README es **parte del fix**, no una tarea aparte. El momento de mayor calidad documental es justo cuando acabas de sufrir el error.

Qué NO es documentación mínima: wikis, docs de arquitectura por proyecto, changelogs manuales. El techo de documentación por proyecto es README (humanos) + CLAUDE.md (IAs) + migraciones/mini-ADRs (decisiones). Más que eso, para un equipo de 1, es inventario que caduca.

---

## 07. Retomar un proyecto existente — el ritual de retorno

**[RECOMMENDED]** Volver a un proyecto tras semanas/meses sigue siempre el mismo ritual de 4 pasos, en orden — y se cronometra (es la métrica de onboarding de la sección 08):

```powershell
# 1. Leer README (setup) y CLAUDE.md (estado, reglas, mapa) — 5 min máximo
# 2. Sincronizar y verificar que el suelo es firme:
git pull; npm install
npm run check          # ¿el proyecto está sano ANTES de tocar nada?
# 3. Levantar local:
npm run dev
# 4. Si algo del ritual falló o mintió (README desactualizado, check rojo heredado):
#    arreglarlo AHORA es la primera tarea de la sesión, no una nota para después.
```

**Por qué el ritual es fijo:** el costo real de retomar un proyecto no es leer código — es reconstruir contexto ("¿cómo se corría esto? ¿en qué estado quedó?"). Con scripts idénticos (sección 02), CLAUDE.md al día (sección 05) y README verificado (sección 06), ese contexto está externalizado y el ritual son <15 minutos mecánicos. El paso 2 antes de tocar nada distingue "esto ya estaba roto" de "yo lo rompí" — la confusión entre ambos es de las fricciones más caras que existen. Y la regla del paso 4 es el mecanismo de mantenimiento de todo este dominio: la documentación se repara exactamente en el momento en que su mentira se detecta.

**Por qué es RECOMMENDED y no REQUIRED:** el ritual es el default esperado, pero un hotfix urgente de producción legítimamente va directo al grano — con la deuda anotada.

---

## 08. Métricas de DX — honestas y accionables

**[RECOMMENDED]** Se miden exactamente tres cosas, con reloj real, no con impresiones:

| Métrica | Cómo se mide | Objetivo (heurística 2026) |
|---|---|---|
| **Tiempo de bootstrap** | De `gh repo create` a primer deploy verificado en producción (checklist completo de [PROJECT_BOOTSTRAP_CHECKLIST](PROJECT_BOOTSTRAP_CHECKLIST.md)) | < 1 hora; el objetivo de A1 es < 10 min hasta CI verde |
| **Tiempo de onboarding** | De `git clone` (o "abro un proyecto que no toco hace 1+ mes") a `npm run dev` sirviendo la app | < 15 min siguiendo solo el README |
| **Fricción registrada** | Contador de entradas del log de fricción (abajo) por mes | Tendencia a la baja; 0 repetidas |

**Por qué estas tres y no un dashboard:** son las únicas que (a) se miden sin infraestructura —un reloj y una nota— y (b) tienen dueño de acción directo: bootstrap lento → arreglar template/checklist; onboarding lento → arreglar README/`.vscode`; fricción repetida → automatizar. Una métrica sin acción asociada es decoración.

**[REQUIRED] El log de fricción:** cada vez que algo de tooling te cuesta **más de 15 minutos** (una config que no funciona, un comando que hay que redescubrir, un setup que falla), se anota en el momento — una línea: fecha, qué, cuántos minutos. El log vive donde ya viven las repeticiones detectadas: una entrada nueva o el engorde de una existente en [23-Automations](../Engineering-OS/23-Automations.md) (formato de su regla: ≥2 veces manual → propuesta).

**Por qué es REQUIRED siendo tan pequeño:** la fricción de tooling es invisible por diseño — se paga en momentos de frustración que se olvidan en cuanto se resuelven, así que nunca compite contra features en la priorización. El log la convierte en dato. Es literalmente el mecanismo de entrada del proceso de mejora de DX: sin log, este documento se congela; con log, cada trimestre hay una lista real de qué automatizar ordenada por minutos perdidos.

**Métricas que NO se usan:** líneas de código generadas, número de commits, "velocidad" subjetiva. Miden actividad, no fricción, y son manipulables hasta por uno mismo.

---

## Checklist final

**Bootstrap (01):**
- [ ] ¿El proyecto nació de `template-saas` (`gh repo create --template`) o del script A1 — cero configuración "a mano, de memoria"?
- [ ] ¿El template contiene todas las piezas de la tabla 1.2 y pasa `npm run check` recién clonado?

**Scripts (02):**
- [ ] ¿`dev`, `build`, `check`, `test` (y el resto del contrato de [07_AUTOMATION_GUIDE §02](../06_Testing/Guides/07_AUTOMATION_GUIDE.md)) existen con esos nombres exactos?
- [ ] ¿Los scripts extra del proyecto están documentados en su CLAUDE.md, sin renombrar los del contrato?

**Editor (03):**
- [ ] ¿`.vscode/settings.json` (format on save + ESLint autofix + LF) y `extensions.json` (≤8 extensiones) versionados en el repo?

**Snippets (04):**
- [ ] ¿`.vscode/handbook.code-snippets` presente, con los 4 patrones (`hb-component`, `hb-hook`, `hb-route`, `hb-migration`) al día con sus estándares?

**CLAUDE.md (05):**
- [ ] ¿Existe, sigue la plantilla (stack/comandos, estándares aplicables, mapa, reglas, verificación) y refleja el estado actual del repo?
- [ ] ¿Se actualizó en el mismo commit que el último cambio que lo afectaba?

**README (06):**
- [ ] ¿Setup en ≤5 pasos, ejecutados tal cual al menos una vez con éxito?

**Ritual de retorno (07):**
- [ ] ¿La última retomada de proyecto siguió el ritual (leer → check → dev) y lo que mintió se arregló en esa misma sesión?

**Métricas (08):**
- [ ] ¿El último bootstrap y el último onboarding tienen tiempo anotado?
- [ ] ¿Toda fricción de >15 min del último mes está en el log de [23-Automations](../Engineering-OS/23-Automations.md)?
