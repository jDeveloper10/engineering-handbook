---
title: "Checklist de Arranque de Proyecto"
category: 14_DX
doc_type: referencia
tags: [dx, checklist, bootstrap, setup]
summary: "Arranque de un proyecto nuevo paso a paso: prerequisitos por máquina, creación del repositorio desde plantilla, identidad del proyecto y colocación de cada secreto en su lugar."
keywords: [bootstrap, checklist, setup, repo, secretos, gh, plantilla]
updated: 2026-07-27
status: current
---

# PROJECT BOOTSTRAP CHECKLIST — proyecto nuevo, paso a paso

> Documento operativo del dominio DX (14). Es la ejecución del `[REQUIRED]` de bootstrap de [DX_STANDARD.md §01](DX_STANDARD.md): copy-paste de arriba a abajo, en orden. Cada paso tiene su comando (PowerShell, Windows) y su verificación — **no avanzas al siguiente hasta que la verificación pase**. Tiempo objetivo del checklist completo: < 1 hora (anotar el real — métrica de [DX_STANDARD §08](DX_STANDARD.md)).
>
> Cuando el script A1 `new-project.ps1` ([23-Automations](../Engineering-OS/23-Automations.md)) esté `activo`, automatiza los pasos 1-2; el resto sigue siendo este checklist.

---

## Paso 0 — Prerequisitos (una vez por máquina, no por proyecto)

```powershell
gh auth status          # GitHub CLI autenticado
wrangler whoami         # Cloudflare autenticado
supabase --version      # Supabase CLI instalado (login en paso 4)
node --version          # v20+
```

**Sabes que funcionó cuando:** los cuatro comandos responden sin error ni prompt de login. Si alguno falla, se resuelve ahora — no a mitad del checklist.

---

## Paso 1 — Crear repo desde el template

```powershell
gh repo create JCDIGITALL/<nombre> --template JCDIGITALL/template-saas --private --clone
cd <nombre>
npm install
npm run check
```

**Sabes que funcionó cuando:** `npm run check` termina en verde (lint + typecheck + test + build) sobre el clon recién creado. Si falla, el problema es del template — se arregla en `template-saas` (y se re-corre este paso), no con un parche local.

---

## Paso 2 — Identidad del proyecto

Renombrar los placeholders del template:

```powershell
# Editar a mano (o con Claude Code): 
#   package.json      → "name": "<nombre>"
#   wrangler.toml     → name = "<nombre>-worker"
#   CLAUDE.md         → rellenar todos los <> (plantilla en DX_STANDARD §05)
#   README.md         → rellenar T1 (26-Templates); el setup real se verifica en el paso 8
git add -A; git commit -m "chore: identidad del proyecto <nombre>"; git push
```

**Sabes que funcionó cuando:** `git grep -i "template-saas\|<nombre-placeholder>"` no devuelve nada, y `CLAUDE.md` no tiene ningún `<>` sin rellenar.

---

## Paso 3 — Secretos: cada uno en su lugar (y en ningún otro)

Mapa exacto — la regla madre es [05_Security §03](../05_Security/SECURITY_ENGINEERING_STANDARD.md); la ubicación en CI es [03_CI_CD §07](../06_Testing/Pipelines/03_CI_CD.md):

| Secreto | Dónde va | Comando |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` (deploy) | GitHub **environment** `production` (y `staging` si existe) — nunca secreto plano de repo | `gh secret set CLOUDFLARE_API_TOKEN --env production` |
| `SUPABASE_SERVICE_ROLE`, secretos de webhooks, API keys de terceros (Resend...) | Worker en producción: `wrangler secret put` — jamás `[vars]` del `wrangler.toml` | `wrangler secret put SUPABASE_SERVICE_ROLE` |
| Los mismos, para desarrollo local del Worker | `.dev.vars` (gitignoreado) | editar `.dev.vars` a mano |
| `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, URLs de workers | `.env` local (gitignoreado) + variables de build en CI/Pages — **públicas por definición**, solo lo diseñado para ser público | editar `.env`; espejo de nombres en `.env.example` |

```powershell
# Tras configurar cada secreto, actualizar los ejemplos (nombres sin valores):
#   .env.example  y  .dev.vars.example
```

**Sabes que funcionó cuando:** (a) `gh secret list --env production` muestra el token; (b) `wrangler secret list` muestra los del worker; (c) `git status` NO muestra `.env` ni `.dev.vars`; (d) ningún valor real aparece en `git grep -i "key\|token\|secret" -- ':!*.example'` sobre lo commiteado. Además: anota cada secreto en el **inventario de secretos** (nombre → dónde se usa → dónde se rota) — [05_Security §03](../05_Security/SECURITY_ENGINEERING_STANDARD.md) lo exige para poder rotar en emergencia.

---

## Paso 4 — Supabase: proyecto + primera migración

```powershell
supabase login
# Crear el proyecto en el dashboard (elegir región cercana a los usuarios) o via CLI/MCP.
supabase link --project-ref <ref-del-proyecto>

# Primera migración: NUNCA esquema a mano en el dashboard (04_Database — el dashboard de prod es solo lectura)
supabase migration new init_schema
# → escribir el SQL en supabase/migrations/<timestamp>_init_schema.sql
#   (tablas con created_at/updated_at, RLS habilitado en toda tabla — 05_Security §05)
supabase db push
```

**Sabes que funcionó cuando:** `supabase migration list` muestra `init_schema` aplicada en remoto, y en el dashboard (Table Editor, solo mirando) aparecen las tablas **con RLS habilitado**. Copiar URL y anon key a `.env` (paso 3, fila `VITE_*`).

---

## Paso 5 — Cloudflare: Worker + Pages + dominios

```powershell
# Worker (primer deploy manual para crear el recurso; después deploya el CI):
wrangler deploy

# Frontend: crear el proyecto Pages conectado al repo de GitHub (dashboard → Workers & Pages
# → Create → Pages → conectar JCDIGITALL/<nombre>; build: npm run build, output: dist)
# Dominios: añadir el custom domain al proyecto Pages y (si aplica) route al worker
```

**Sabes que funcionó cuando:** (a) `curl https://<nombre>-worker.<subdominio>.workers.dev/health` (o la ruta base) responde; (b) la URL `*.pages.dev` sirve la app; (c) si hay dominio propio, resuelve con certificado válido (candado en el navegador). Detalles de plataforma: [CLOUDFLARE_PLATFORM_STANDARD](../08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md).

---

## Paso 6 — CI verde

Los workflows `ci.yml` / `deploy.yml` / `nightly.yml` ya vienen del template ([03_CI_CD](../06_Testing/Pipelines/03_CI_CD.md)). Solo hay que verlos pasar con los secretos reales:

```powershell
git commit --allow-empty -m "ci: primer run con secretos configurados"
git push
gh run watch          # o: gh run list --limit 3
```

**Sabes que funcionó cuando:** el run de `ci.yml` termina ✓ en verde completo (lint → typecheck → test+coverage → build → e2e smoke) en < 10 min. Un CI verde por saltarse jobs no cuenta — abrir el run y confirmar que **todos** los jobs corrieron.

---

## Paso 7 — Primer deploy verificado

```powershell
git push               # push a main dispara deploy.yml (gates → staging → prod → smoke)
gh run watch
```

**Sabes que funcionó cuando:** `deploy.yml` en verde **y** verificación humana de un flujo real: abrir la URL de producción, ejecutar el flujo principal (login, o el flujo que paga las cuentas) de punta a punta. El smoke automático post-deploy ya corrió dentro del workflow ([03_CI_CD §05](../06_Testing/Pipelines/03_CI_CD.md)) — esta verificación manual es adicional solo en el primer deploy, para calibrar que el smoke prueba lo correcto.

---

## Paso 8 — Activar protecciones (con el pipeline ya verde)

Comandos completos y su porqué en [GITHUB_STANDARD §03 y §05](../07_DevOps/GITHUB_STANDARD.md); resumen ejecutable:

```powershell
# Branch protection de main (no force-push, no delete, require status checks):
#   → comando gh api completo en GITHUB_STANDARD §03 (verificar el context name = job del ci.yml)

# Secret scanning + push protection:
#   → comando gh api completo en GITHUB_STANDARD §05

# Dependabot alerts + updates (dependabot.yml ya viene en el template):
gh api -X PATCH "repos/JCDIGITALL/<nombre>" -f has_vulnerability_alerts=true
```

**Sabes que funcionó cuando:** (a) `git push --force origin main` es **rechazado** por el remoto (probarlo con un repo limpio es la única prueba real); (b) en Settings → Code security del repo, secret scanning y push protection figuran "Enabled"; (c) la protección exige el status check del CI antes de merge.

**Por qué al final y no al principio:** el status check requerido debe existir (paso 6) antes de poder exigirse; activar protecciones sobre un pipeline que aún no corre bloquea el propio bootstrap.

---

## Cierre — el proyecto está bootstrapped cuando:

- [ ] `npm run check` verde en local (paso 1)
- [ ] Cero placeholders; `CLAUDE.md` y `README.md` rellenados (paso 2)
- [ ] Secretos: cada uno en su lugar según la tabla, inventario actualizado, nada en el repo (paso 3)
- [ ] Migración `init_schema` aplicada, tablas con RLS (paso 4)
- [ ] Worker y Pages responden en sus URLs (+dominio si aplica) (paso 5)
- [ ] `ci.yml` verde con todos los jobs (paso 6)
- [ ] `deploy.yml` verde + flujo principal verificado a mano en producción (paso 7)
- [ ] Force-push rechazado, secret scanning + push protection activos, Dependabot on (paso 8)
- [ ] README de setup **re-ejecutado tal cual está escrito** (o corregido hasta que sea cierto) — el `[REQUIRED]` de [DX_STANDARD §06](DX_STANDARD.md)
- [ ] Tiempo total anotado en la métrica de bootstrap ([DX_STANDARD §08](DX_STANDARD.md)); si algo tomó >15 min por fricción de tooling → log de fricción / [23-Automations](../Engineering-OS/23-Automations.md)
