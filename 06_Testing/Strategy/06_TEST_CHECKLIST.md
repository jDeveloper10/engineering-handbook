---
title: "Checklists de Test por Momento"
category: 06_Testing
doc_type: referencia
tags: [testing, checklist, proceso]
summary: "Qué corre antes de commit, de push, de merge, de release, de deploy y después del deploy, cada uno con su presupuesto de tiempo explícito."
keywords: [checklist, commit, push, merge, release, deploy, presupuesto]
updated: 2026-07-21
status: current
---

# 06 — Test Checklists: qué corre en cada momento

> **Propósito:** checklists operativos copy-paste por momento del ciclo (commit → push → merge → release → deploy → post-deploy), más las plantillas de cobertura para features nuevas y bugs. El CÓMO de cada tipo de test vive en `02_TESTING_PIPELINE.md`; este documento solo dice **qué corre cuándo y con qué comando**.
>
> **Principio rector:** cada gate corre lo máximo que cabe en su presupuesto de tiempo — rápido y parcial cerca del teclado, lento y completo cerca de producción. Un gate que tarda más de lo tolerable se saltea, y un gate que se saltea no existe.

---

## 1. Antes de commit (presupuesto: < 30 segundos)

Corre local, en cada commit. Solo lo afectado — el objetivo es feedback inmediato, no certeza total (esa llega en CI).

- [ ] Lint sin errores
- [ ] Typecheck sin errores
- [ ] Unit tests **afectados por los archivos cambiados** en verde

```bash
npm run lint
npx tsc --noEmit
npx vitest run --changed
```

**Por qué `--changed` y no la suite entera:** Vitest resuelve el grafo de imports y ejecuta solo los tests que tocan los archivos modificados — segundos en vez de minutos. Si el pre-commit tarda 3 minutos, en una semana se comitea con `--no-verify`, y el gate muere.

---

## 2. Antes de push

Todo lo anterior, más la suite unit/component completa del paquete tocado.

- [ ] Checklist de commit (§1) en verde
- [ ] Suite completa de unit + component del frontend en verde
- [ ] Si se tocó un worker: su suite de integración en verde

```bash
npx vitest run                                  # frontend: unit + component
npx vitest run --config apps/worker/vitest.config.ts   # worker tocado (workerd)
```

---

## 3. Antes de merge (CI, presupuesto: < 10 minutos)

El gate de verdad: nada se mergea a `main` en rojo. Corre en CI, no en la máquina local.

- [ ] Lint + typecheck de todo el repo
- [ ] Unit + component + integration completos, **con coverage y umbral aplicado** (80/75 sobre lógica — `02_TESTING_PIPELINE.md` §1.3)
- [ ] E2E smoke (`@smoke`) contra build de preview, en los 3 viewports
- [ ] Cero tests marcados `flaky` en el reporte — si aparece uno, se arregla o se borra antes de mergear (`02_TESTING_PIPELINE.md` §6.4)

```bash
npm run lint && npx tsc --noEmit
npx vitest run --coverage
npx vitest run --config apps/worker/vitest.config.ts
npx playwright test --grep @smoke
```

---

## 4. Antes de release (nightly o pre-release)

Todo lo anterior, más la profundidad que no cabe en cada merge.

- [ ] E2E full (todo lo que no es `@smoke`): errores mockeados, permisos, vacíos, offline, dark mode, links
- [ ] Visual regression en verde — o diffs revisados uno a uno y bases regeneradas a conciencia
- [ ] Coverage no bajó respecto del release anterior (el umbral es piso, no licencia para bajar)

```bash
npx playwright test --grep-invert @smoke
npx playwright test --grep @visual
# solo si el diff visual es un cambio intencional ya revisado:
npx playwright test --grep @visual --update-snapshots
```

---

## 5. Antes de deploy

- [ ] El commit a deployar pasó el gate de merge (§3) — se deploya un commit de `main` verde, nunca un branch sin CI
- [ ] Migraciones de DB aplicadas y verificadas en local/staging antes que el código que las necesita
- [ ] Variables de entorno y secretos del entorno destino verificados (`wrangler secret list` para workers — backend §16)

```bash
supabase db push --dry-run     # revisar qué migraría antes de migrar
wrangler secret list
```

---

## 6. Después de deploy (smoke en producción, < 5 minutos)

El deploy no está terminado hasta que esto pasa. Si falla: rollback primero, diagnóstico después.

- [ ] Smoke E2E contra la URL de producción, con el usuario de test dedicado de prod
- [ ] Health check del worker responde 200
- [ ] Sin errores nuevos en los logs del worker durante los primeros minutos

```bash
BASE_URL=https://app.tudominio.com npx playwright test --grep @smoke
curl -s -o /dev/null -w "%{http_code}" https://api.tudominio.com/health
wrangler tail --format pretty
```

**Por qué smoke también en producción:** CI prueba el código; producción prueba además DNS, secretos reales, la instancia real de Supabase y el CDN. La mayoría de los "funciona en CI pero no en prod" viven exactamente en esa diferencia.

---

## 7. Checklist: qué debe cubrir el test de una feature nueva

Ninguna feature está terminada con solo el happy path. Mínimo obligatorio:

- [ ] **Happy path** — el flujo completo funciona de punta a punta
- [ ] **Validación** — input inválido muestra el mensaje de error diseñado y no ejecuta la acción
- [ ] **Error de red** — con la API respondiendo 500 (route interception), la UI muestra el error amigable, no pantalla blanca
- [ ] **Estado vacío** — la feature sin datos muestra su empty state, no un layout roto
- [ ] **Mobile (375px)** — el flujo es completable en el viewport mobile, no solo en desktop
- [ ] Si la feature tiene lógica de negocio: unit tests de esa lógica (bordes incluidos), no solo el E2E
- [ ] Si toca permisos/roles: el rol sin permiso no puede ejecutarla ni por UI ni navegando directo a la URL

**Por qué:** el happy path es el único caso que el developer ya probó a mano mil veces — los bugs viven en los otros cuatro. Esta lista es el contrato mínimo que una IA debe cumplir al implementar una feature antes de declararla lista.

---

## 8. Checklist: test de un bug

Todo bug que llegó a producción (o a reporte) recibe su test de regresión **antes** del fix:

- [ ] El test reproduce el bug **exacto** reportado (mismos datos, mismo flujo — no una versión genérica)
- [ ] El test **falla** contra el código actual (rojo confirmado — si pasa, no reprodujo el bug)
- [ ] Se aplica el fix
- [ ] El test **pasa** con el fix (verde confirmado) y el resto de la suite sigue en verde
- [ ] El test queda en la suite permanente, nombrado por el comportamiento (`it('no duplica el cobro si el webhook llega dos veces')`), no por el ticket (`it('fix bug 231')`)

```bash
npx vitest run ruta/al/nuevo.test.ts   # paso 2: confirmar el rojo ANTES del fix
```

**Por qué el rojo previo es obligatorio:** un test escrito después del fix que nunca se vio fallar puede estar testeando otra cosa (o nada) y dar verde con el bug presente. El ciclo rojo→fix→verde es la única prueba de que el test detecta ese bug — y garantiza que ese bug específico no puede volver sin que la suite lo grite.

---

## Resumen: la escalera completa

| Momento | Qué corre | Presupuesto |
|---|---|---|
| Commit | lint + typecheck + unit afectados (`--changed`) | < 30 s |
| Push | suite unit/component completa + integración del worker tocado | < 3 min |
| Merge (CI) | todo + coverage con umbral + E2E `@smoke` en 3 viewports | < 10 min |
| Release | E2E full + visual + revisión de diffs | sin límite (nightly) |
| Deploy | verificación de migraciones + secretos del entorno | < 2 min |
| Post-deploy | `@smoke` contra producción + health + logs | < 5 min |
