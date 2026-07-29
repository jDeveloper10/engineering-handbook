# 26 — Templates

> Plantillas copiables. Regla: nunca escribir estos documentos desde cero — copiar, rellenar
> `<>`, borrar lo que no aplique. IA básica los rellena; Jeilin corrige.

## T1 — README.md de proyecto

```markdown
# <nombre>

<1 línea: qué es y para quién.>

## Stack
<React 19 + Vite + TS + Tailwind | Worker | ...> · Deploy: <Pages auto | wrangler | CI>

## Correr local
npm install && npm run dev   # <puerto>
# Variables: copiar .env.example → .env y completar

## Deploy
<push a main = deploy | comando único>
## Rollback
<cómo volver al deploy anterior, 1-2 líneas>

## Decisiones no obvias
- <por qué X y no Y — 1 línea c/u>
```

## T2 — CLAUDE.md de proyecto

```markdown
# <nombre> — contexto para IAs

Leer primero: E:\ENGINEERING_HANDBOOK\Engineering-OS\ (README + 03-Global-Rules).

## Qué es
<2-3 líneas de propósito y estado (producción/desarrollo).>

## Stack y comandos
<stack> · `npm run dev` · `npm run build` · deploy: <método>

## Mapa
<src/... 3-6 líneas de qué vive dónde>

## Reglas específicas
- <qué NO tocar y por qué (ej.: worker-pago maneja dinero real)>
- <decisiones tomadas que no se re-litigan>
```

## T3 — ci.yml estándar (frontend; añadir bloque wrangler para workers)

```yaml
name: CI
on: { push: { branches: [main] } }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run build
  # workers: job deploy con cloudflare/wrangler-action@v3 y secret CLOUDFLARE_API_TOKEN
```

## T4 — PRD / alcance de cliente (antes de codear — regla de 21-Business)

```markdown
# PRD — <cliente/proyecto>
**Objetivo de negocio:** <qué gana el cliente>
**Precio y plan:** $<X> — <Landing Express $150 | Business Pro $250 | Elite Shop $310 + extras>
**Alcance incluido:** <lista cerrada>  ·  **Fuera de alcance:** <lista explícita>
**Contenido que entrega el cliente:** <textos, fotos, accesos> — sin esto no se agenda
**Fecha objetivo:** <fecha> · **Definición de terminado:** checklist §6 + <criterio del cliente>
```

## T5 — Issue / tarea

```markdown
**Qué:** <1 línea> · **Por qué ahora:** <impacto> · **Done cuando:** <verificable>
```

## T6 — Bug report

```markdown
**Dónde:** <URL/proyecto> · **Esperado:** · **Ocurre:** · **Pasos:** 1..2..3
**Evidencia:** <error de consola/log> · **Severidad:** <rompe dinero | rompe flujo | cosmético>
```

## T7 — Feature request → usar T5 + campo "¿Quién lo paga?" (21-Business).

## T8 — Decisión de arquitectura (mini-ADR, va en CLAUDE.md o KB)

```markdown
**Decisión:** <qué se eligió> · **Contexto:** <problema> · **Alternativas:** <qué se descartó y por qué>
**Consecuencias:** <qué aceptamos a cambio> · **Fecha:**
```

## T9 — Post mortem (errores de producción)

```markdown
**Qué pasó:** · **Impacto:** <tiempo caído, clientes afectados> · **Causa raíz:**
**Detección:** <cómo nos enteramos — si fue "un cliente avisó", A6 sube de prioridad>
**Fix:** · **Prevención:** <test/automatización creada> · → copiar a 28-Knowledge-Base
```

## T10 — Release notes / changelog

```markdown
## <versión o fecha>
- <feat|fix>: <qué cambió en lenguaje de usuario, no de código>
(generar con IA básica desde `git log --oneline <desde>..HEAD`, luego pulir)
```

## Prompts reutilizables para IA

**T11 — Prompt base (toda tarea):**
```
Trabajas bajo el Engineering OS de Jeilin (E:\ENGINEERING_HANDBOOK\Engineering-OS).
Reglas activas: 03-Global-Rules. Tarea: <qué>. Proyecto: <ruta> (lee su CLAUDE.md).
Entregable: <qué exactamente>. Al final reporta: estado (VERIFICADO/NO VERIFICADO/FALLÓ) + detectores (deuda/cuellos/manual/desperdicio/seguridad/negocio).
```

**T12 — Revisión de código:**
```
Revisa <archivos/PR> contra: (1) reglas REQUIRED del handbook <dominio>, (2) 16-Security si toca pagos/auth,
(3) checklist §3. Reporta SOLO problemas con archivo:línea + fix concreto. Sin elogios ni resúmenes.
```

**T13 — Debugging:**
```
Bug: <T6 rellenado>. Antes de proponer fix: reproduce o explica por qué no puedes; identifica causa raíz
(no síntoma); propone el fix mínimo + test de regresión si es código de dinero. No refactorices de paso.
```

**T14 — Arquitectura:**
```
Decisión: <pregunta>. Usa 05-Decision-Matrix (incluida matriz de adopción). Contexto obligatorio:
06-Architecture + stack canónico. Entrega: T8 rellenado con 2+ alternativas reales y tu recomendación.
```

**T15 — Optimización:**
```
Objetivo: <métrica de 24-Metrics a mover>. Paso 1: MEDIR baseline y reportarlo. Paso 2: hipótesis
ordenadas por impacto/esfuerzo. Paso 3: implementar la #1. Paso 4: re-medir y reportar delta real.
Prohibido optimizar sin baseline.
```

**T16 — Documentación:**
```
Genera <README|CLAUDE.md|changelog> de <ruta> usando la plantilla <T1|T2|T10> de 26-Templates.
Fuentes: package.json, estructura real, git log. Lo que no puedas verificar: márcalo DATO FALTANTE, no lo inventes.
```
