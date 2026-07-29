# 19 — Git Standards

> Los hallazgos que motivan este archivo: 41+ proyectos sin git/remote, 54 archivos sin commitear
> en Xworked, 134 en ingenusfx, ráfagas de meses sin commits en jcdigital, commits históricos
> mezclando idiomas y formatos.
>
> Las reglas técnicas de GitHub (cuentas, PATs, Actions, secret scanning, branch protection)
> viven en el handbook `07_DevOps/GITHUB_STANDARD.md`. Este archivo define las reglas operativas
> de uso diario de git.
>
> **Ver también:** [`GITHUB_STANDARD.md`](../07_DevOps/GITHUB_STANDARD.md) — setup de repos,
> Actions, PATs, secret scanning, branch protection.
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** `GITHUB_STANDARD.md` gobierna la configuración de GitHub (repos, Actions,
>   secretos, ramas). Este archivo gobierna el uso diario de git (cuándo commitear, cómo
>   nombrar commits, qué no committear). No hay duplicación: si el standard estableciera
>   "branch protection en main", esa regla ganaría sobre "commit directo a main" de este
>   archivo — la regla más restrictiva prevalece para proteger la rama de producción.

## Reglas

- **[REQUIRED] Todo proyecto activo = repo git + remote en `github.com/JCDIGITALL`.** Crear repo
  es parte de crear proyecto (automatización A1). Un proyecto sin remote es un proyecto que un
  disco dañado puede borrar de la historia.
- **[REQUIRED] Commit diario en todo proyecto tocado ese día.** Fin de sesión de trabajo = commit
  + push, aunque el trabajo esté a medias (`wip:` es un prefijo válido para eso). Nunca cerrar el
  día con >20 archivos modificados sin commitear.
- **[REQUIRED] Formato de mensaje:** Conventional Commits en inglés:
  `feat|fix|chore|docs|refactor|perf|test(scope): descripción imperativa`.
  El historial real ya converge a esto (feat/fix/chore/docs) — se formaliza, no se inventa.
- **[REQUIRED] `main` siempre desplegable** en repos conectados a Pages (push a main = deploy en
  producción). Trabajo experimental largo → rama `feat/<nombre>`; para cambios de una sesión,
  commit directo a main es aceptable (equipo de 1).
- **[REQUIRED] `.gitignore` mínimo en todo repo:** `.env`, `.dev.vars`, `node_modules/`, `dist/`,
  `.wrangler/`. Verificado por el checklist de commit.
- **[REQUIRED] Nunca commitear:** secretos, `serviceAccount*.json`, `.env` con valores, bases de
  datos locales. Si ya pasó: rotar la clave ANTES de limpiar el historial (la clave ya es pública
  para efectos prácticos).
- **[RECOMMENDED] PRs:** solo para cambios que Jeilin quiera revisar con calma o que una IA básica
  haya hecho en código crítico. El resto: commit directo. Un equipo de 1 no necesita burocracia de
  equipo de 20.

## Ritual de cierre de día (2 minutos, automatizable — ver 23-Automations A3)

```
por cada repo tocado hoy:
  git add -A && git commit -m "wip|feat|fix: <qué quedó>" && git push
```
