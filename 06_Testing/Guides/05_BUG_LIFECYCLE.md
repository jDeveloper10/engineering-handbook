---
title: "Ciclo de Vida de un Bug"
category: 06_Testing
tags: [testing, bugs, issues, proceso]
summary: "De la captura al cierre: toda fuente termina en el mismo lugar, registro mínimo de un issue de bug, criterios objetivos de severidad P0 a P3 y la regla de que todo fix deja un test de regresión."
keywords: [bug, issue, severidad, p0, regresion, triage, gh]
updated: 2026-07-27
status: current
---

# 05 — BUG LIFECYCLE

> Ciclo de vida del bug para un developer solo, ejecutable por herramientas + agentes IA. Sigue [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Complementa, no duplica: los **incidentes** de producción (rollback, runbooks de fallos) son de `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`; los incidentes de **seguridad** son de `05_Security/INCIDENT_RESPONSE.md`. Este documento cubre el bug como *unidad de trabajo*: desde que existe hasta que deja un test que impide su regreso.
>
> Principio del documento: para un dev solo, el enemigo no es el bug — es el bug **perdido** (reportado en un chat y olvidado) y el bug **repetido** (arreglado dos veces porque el fix no dejó test). Todo lo que sigue ataca esas dos fugas.

---

## 1. Captura — toda fuente termina en el mismo lugar

**[REQUIRED]** Todo bug, venga de donde venga, termina como **GitHub Issue en el repo del proyecto** dentro de las 24h de conocerse. Fuentes y su vía de entrada:

| Fuente | Vía de entrada | Automatizable |
|---|---|---|
| Sentry (error en producción) | Integración GitHub de Sentry: alerta → issue con stack trace y link al evento | Sí — configurar una vez por proyecto |
| Usuario (email, chat, soporte) | El dev (o un agente IA con el texto del reporte) crea el issue con `gh issue create` | Parcial — flujo n8n email→issue si el volumen lo justifica |
| Test que falla en CI sobre `main` | Issue desde el run fallido (workflow con `gh issue create` on failure, o a mano desde el log) | Sí |
| Monitoring / healthcheck (cron, smoke post-deploy) | El check que falla crea el issue | Sí |
| El propio dev / agente IA lo nota trabajando | `gh issue create` en el momento — no "lo anoto después" | — |

**Por qué un solo lugar:** un dev solo no tiene bandeja compartida ni daily donde alguien recuerde el bug; lo que no está en el tracker no existe. GitHub Issues y no otra herramienta porque ya está pegado al código, al PR que lo arregla (`Fixes #N`) y al CLI (`gh`) que los agentes IA pueden operar sin UI.

**Implementación (crear el issue en 10 segundos):**
```bash
gh issue create \
  --title "Login: 500 al usar email con mayúsculas" \
  --label "bug,P1" \
  --body "Repro: login con Foo@bar.com -> 500. Esperado: login OK (case-insensitive).
Fuente: Sentry https://sentry.io/...  Desde: deploy abc1234"
```

---

## 2. Registro mínimo — qué debe tener un issue de bug

**[REQUIRED]** Cuatro campos, nada más (los campos que nadie llena se convierten en formularios muertos):

1. **Título**: síntoma observable, no diagnóstico ("500 al pagar con tarjeta AMEX", no "problema en el worker de pagos").
2. **Repro**: pasos mínimos o link al evento de Sentry. Si no hay repro todavía, decirlo explícitamente — un bug sin repro es una hipótesis.
3. **Esperado vs actual**: una línea cada uno.
4. **Labels**: `bug` + severidad `P0`–`P3` (sección 3).

**Por qué mínimo:** el costo de registrar tiene que ser menor que la tentación de no registrar. Plantillas largas producen bugs sin registrar, no bugs mejor documentados.

**Implementación (labels — se crean una vez por repo, va en el setup de [10_PLAYBOOK.md](10_PLAYBOOK.md) P1):**
```bash
gh label create P0 --color B60205 --description "Producción rota o datos en riesgo - drop everything"
gh label create P1 --color D93F0B --description "Funcionalidad core degradada - fix en 24h"
gh label create P2 --color FBCA04 --description "Bug real con workaround - esta semana/ciclo"
gh label create P3 --color C2E0C6 --description "Menor/cosmético - backlog con expiración"
```

---

## 3. Severidad P0–P3 — criterios objetivos

**[REQUIRED]** La severidad se asigna por criterios observables, no por sensación. Se pregunta en orden y se asigna la primera que aplique:

| Nivel | Criterio objetivo (basta uno) | Respuesta obligada |
|---|---|---|
| **P0** | Producción caída o inutilizable para todos; **o** se están corrompiendo/perdiendo/exponiendo datos de usuario; **o** el flujo de pago no cobra o cobra mal; **o** hay secreto expuesto | **Drop everything.** Ir AHORA a `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` §06 (rollback primero) o al runbook B que aplique; si es secreto/seguridad, `05_Security/INCIDENT_RESPONSE.md`. El issue se trabaja cuando el sangrado paró |
| **P1** | Un flujo crítico (auth, acción core, pago) falla para un subconjunto de usuarios o casos; sin workaround razonable | Fix en **<24h**; desplaza cualquier trabajo de features |
| **P2** | Bug real en funcionalidad no crítica, o crítico **con** workaround claro | Se arregla en el ciclo de trabajo actual (esa semana) |
| **P3** | Cosmético, edge case improbable, mejora disfrazada de bug | Backlog. **Expira**: si en 90 días nadie lo sufrió de nuevo ni se trabajó, se cierra con el comentario `stale` — sin culpa |

**Por qué criterios objetivos:** la severidad decide si esta noche se duerme o se deploya; esa decisión no puede depender del humor del momento, y un agente IA de triage necesita reglas evaluables, no vibes. **Por qué P3 expira:** un backlog de cientos de P3 es ruido que entierra a los P1; cerrar sin arreglar es una decisión honesta — reabrir cuesta un click si el bug reaparece.

**[REQUIRED] Triage automático.** El triage (asignar severidad + decidir siguiente acción) lo puede ejecutar un agente IA aplicando la tabla anterior, con una restricción: **un agente puede subir severidad por sí solo, pero bajar de P0/P1 a P2/P3 requiere confirmación del dev.** **Por qué la asimetría:** el costo de un falso P0 es una hora perdida; el costo de un P0 degradado a P2 es una noche de datos corruptos.

**[RECOMMENDED]** Triage batch: los P2/P3 no interrumpen — se procesan en una pasada periódica (`gh issue list --label bug --state open`), no según llegan. Solo P0/P1 interrumpen el trabajo en curso.

---

## 4. Regla de oro — todo fix deja un test de regresión

**[REQUIRED]** Un bug no está cerrado hasta que existe un **test automatizado que falla con el bug presente y pasa con el fix** — un test que, de haber existido, habría atrapado el bug antes del deploy. Orden obligatorio:

```
1. Escribir el test que reproduce el bug  → correrlo → debe FALLAR (rojo)
2. Escribir el fix                        → correrlo → debe PASAR (verde)
3. PR con fix + test juntos, "Fixes #N"   → gates → merge cierra el issue
```

**Por qué el test va primero:** ver el test en rojo es la única prueba de que el test detecta *ese* bug; un test escrito después del fix puede estar pasando por razones equivocadas y no proteger nada. **Por qué la regla es absoluta:** para un dev solo, la suite de regresión es la memoria del equipo — cada bug arreglado sin test es un bug que puede volver en silencio, y la segunda vez costará el mismo diagnóstico más la moral de "esto ya lo arreglé".

**[REQUIRED]** Nivel del test de regresión: **el más bajo que reproduzca el bug** ([01_QA_STRATEGY.md](../Strategy/01_QA_STRATEGY.md) §1). Bug de cálculo → unit; bug de contrato/handler → integración; bug que solo aparece con el flujo completo → E2E. No se añade un E2E por cada bug — eso invierte la pirámide en un año.

**[RECOMMENDED]** Excepción documentada: si reproducir el bug en test es desproporcionado (ej. condición de carrera dependiente de infra del proveedor), se permite cerrar sin test **solo** dejando en el issue: por qué no hay test + qué mitigación queda (timeout, retry, alerta de Sentry específica). La excepción escrita mantiene la regla honesta; la excepción silenciosa la mata.

---

## 5. Post-mortem de una línea (P0/P1)

**[REQUIRED]** Todo P0/P1 cerrado lleva, como último comentario del issue, un post-mortem de **una línea** con tres partes:

```
CAUSA: <qué falló de verdad> | GATE QUE FALTÓ: <por qué ningún gate lo atrapó> | AÑADIDO: <test/gate/regla nuevos, con link>
```

Ejemplo real de formato:
```
CAUSA: el worker asumía body JSON y Stripe manda form-encoded en un webhook | GATE QUE FALTÓ: no había test de integración de webhooks con payload real | AÑADIDO: tests/webhooks.spec.ts + fixture de payload Stripe (#142)
```

**Por qué una línea y no un documento:** el post-mortem enterprise (5 whys, timeline, asistentes) no sobrevive al contacto con un equipo de una persona — no se escribiría. Una línea sí se escribe, y contiene lo único accionable: **qué gate nuevo impide la repetición**. La pregunta "¿por qué ningún gate lo atrapó?" es la que mejora el sistema; sin ella, solo se arregló un bug. Coherente con 07_DevOps §06: un commit rollbackeado no se re-deploya sin esto.

**[RECOMMENDED]** Si tres post-mortems apuntan al mismo gate faltante, eso ya no es un bug: es un cambio al estándar de esta carpeta — [02_TESTING_PIPELINE.md](../Pipelines/02_TESTING_PIPELINE.md), [03_CI_CD.md](../Pipelines/03_CI_CD.md) o [08_QUALITY_STANDARDS.md](../Strategy/08_QUALITY_STANDARDS.md) tenían el hueco.

---

## 6. Estados del issue — el flujo completo

**[REQUIRED]** Un bug solo tiene 4 estados; se implementan con lo nativo de GitHub (open/closed + labels), sin tableros aparte que mantener:

```
ABIERTO (open + P0..P3)
   → EN FIX (open + branch/PR linkeado; "Fixes #N" en el PR)
   → CERRADO-ARREGLADO (closed por merge del PR; el PR contiene el test de regresión)
   → CERRADO-SIN-FIX (closed a mano + comentario: `duplicate` / `no-repro tras intentar` / `stale 90d` / `wontfix + razón`)
```

**Por qué sin tablero:** cada superficie extra (Jira, Notion, tablero kanban) es un lugar más que se desincroniza del código. `gh issue list --label P1 --state open` es el dashboard.

---

## Checklist final

- [ ] ¿Todo bug conocido está como GitHub Issue en <24h, venga de Sentry, usuario, CI o monitoring?
- [ ] ¿Sentry→GitHub configurado en cada proyecto en producción?
- [ ] ¿Cada issue de bug tiene: síntoma en el título, repro (o "sin repro" explícito), esperado/actual, label P0–P3?
- [ ] ¿La severidad se asignó con la tabla de criterios objetivos — y ningún agente IA degradó un P0/P1 sin confirmación?
- [ ] ¿Los P0 dispararon el runbook de 07_DevOps/05_Security ANTES de trabajar el issue?
- [ ] ¿Cada bug cerrado como arreglado tiene su test de regresión que se vio FALLAR antes del fix, al nivel más bajo posible?
- [ ] ¿Las excepciones a la regla de oro están escritas en el issue con su mitigación?
- [ ] ¿Todo P0/P1 cerrado tiene su post-mortem de una línea (causa | gate que faltó | añadido)?
- [ ] ¿Los P3 de >90 días se están cerrando como stale en vez de acumularse?
