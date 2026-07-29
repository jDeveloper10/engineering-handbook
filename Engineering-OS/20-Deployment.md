# 20 — Deployment

> Estado real: frontend jcdigital se despliega solo (Pages+Git ✅). Workers a mano. El resto de
> proyectos: mezcla de Firebase Hosting legacy, cosas sin deploy claro. Objetivo: **todo deploy
> es `git push` o un comando único documentado en el README.**
>
> Las reglas técnicas de deploy/rollback y la librería de fallos (B1-B7) viven en el handbook
> `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`. Este archivo define la matriz de deploy por tipo
> y el CI mínimo del ecosistema.
>
> **Ver también:**
> - [`DEPLOY_AND_FAILURES_STANDARD.md`](../07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md) — procedimientos
>   técnicos de deploy, rollback, y librería de 7 fallos reales con runbooks
> - [`25-Checklists.md`](25-Checklists.md) §5-6 — checklists de pre/post deploy
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Este archivo define QUÉ se despliega y CÓMO se conecta el deploy al flujo de
>   trabajo (Git → CI → deploy). El handbook `07_DevOps` define CÓMO se ejecuta técnicamente
>   cada deploy (comandos, rollback, qué hacer cuando falla). Para fallos de producción, la
>   librería B1-B7 en `DEPLOY_AND_FAILURES_STANDARD.md` es la primera fuente.

## Matriz de deploy por tipo

| Tipo | Método canónico | Estado |
|---|---|---|
| Frontend (React/Vite) | Cloudflare Pages conectado a GitHub, push a `main` | ✅ probado (jcdigital) |
| Worker | GitHub Actions + `cloudflare/wrangler-action` en push | ⬜ P0 roadmap — hoy manual |
| n8n / VPS Contabo | Flujo exportado como JSON versionado en repo + import | ⬜ definir en primer toque |
| Firebase Hosting (legacy) | Congelado — no se despliega más; migrar a Pages al tocar | según 12-Firebase |

## CI mínimo (el `ci.yml` estándar — plantilla en 26-Templates.md)

1. `npm ci`
2. `npm run build` (+ `tsc --noEmit` si TS)
3. (workers) `wrangler deploy` con `CLOUDFLARE_API_TOKEN` en GitHub Secrets — solo en push a main.

- **[REQUIRED]** Todo repo nuevo nace con `ci.yml` (lo genera A1). Repos activos existentes lo
  reciben según roadmap.
- **[REQUIRED]** Checklist pre-deploy ([25-Checklists.md](25-Checklists.md) §5) antes de todo
  deploy manual mientras existan.
- **[REQUIRED]** Post-deploy: smoke test de producción (§6). Un deploy no verificado no está
  terminado — regla de honestidad de 03-Global-Rules.
- **[REQUIRED]** Rollback documentado por proyecto en su README: Pages = re-deploy del deployment
  anterior en dashboard; Workers = `wrangler rollback` o redeploy del commit anterior.
- **[RECOMMENDED]** Variables de entorno: la lista completa vive en `.env.example`; los valores en
  Pages/Workers dashboard o GitHub Secrets. Nunca "está en mi cabeza".
