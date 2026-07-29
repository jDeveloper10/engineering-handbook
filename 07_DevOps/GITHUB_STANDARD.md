# GITHUB STANDARD

> Nivel 1 del handbook para el dominio DevOps — Git como herramienta y GitHub como plataforma. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md): cada regla es `[REQUIRED]` o `[RECOMMENDED]`, escrita primero de forma agnóstica (aplica a cualquier forge: GitHub, GitLab, Gitea) y después con la implementación de referencia en el stack actual (GitHub, cuenta `JCDIGITALL`, gh CLI).
>
> Contexto que calibra todas las reglas: **developer solo / equipo muy pequeño**, SaaS en producción. Las reglas descartan deliberadamente la burocracia de equipos grandes (GitFlow, PR obligatorio con 2 approvals, CODEOWNERS) y conservan lo que sí protege a un equipo de 1: que `main` siempre funcione, que ningún secreto toque el historial, y que la cuenta — el único punto de acceso a todo — sea difícil de robar.
>
> Este documento es la versión completa y canónica; `Engineering-OS/19-Git-Standards.md` es el resumen operativo diario y es compatible con lo que sigue.

---

## ⚠️ ALCANCE DE ESTE DOCUMENTO

Este documento cubre el **USO de Git y GitHub** como plataforma de desarrollo.
**NO cubre la construcción de un servidor Git (Git Forge)** desde cero.

### Lo que SÍ cubre:
- Conventional commits
- Trunk-based branching
- Pull Request workflow
- Branch protection rules
- CI/CD con GitHub Actions
- Secrets protection (Gitleaks)
- Code review process

### Lo que NO cubre (FUERA DE ALCANCE):
- Git Smart HTTP Protocol (`git-receive-pack`, `git-upload-pack`)
- Packfile parsing y delta compression
- SHA-1/SHA-256 object storage interno
- Three-way merge engine en el servidor
- Diff calculation engine
- Construcción de un clon de GitHub/GitLab/Gitea

### Si necesitas construir un servidor Git:
- Usa GitLab CE, Gitea, o Gogs como base.
- NO construyas uno desde cero salvo justificación crítica.
- Si es absolutamente necesario, crea `07_DevOps/GIT_SERVER_PROTOCOL_STANDARD.md` siguiendo el protocolo de `[HANDBOOK INCOMPLETO]` en `AGENTS.md`.

---

## 01. Estrategia de ramas — trunk-based simplificado

**[REQUIRED]** El modelo de ramas es: **una rama principal (`main`) siempre desplegable + ramas cortas (horas o pocos días, nunca semanas)** que nacen de `main` y vuelven a `main`. No existen ramas permanentes de entorno (`develop`, `staging`, `release/*`).

**Por qué:** GitFlow existe para coordinar a muchas personas con releases programados; para un dev solo, cada rama permanente extra es un lugar más donde el código diverge y un merge más que puede fallar, sin que nadie se beneficie de la separación. El costo de integración crece con el tiempo de vida de la rama — ramas cortas = conflictos triviales; ramas de semanas = merges de miedo. La separación de entornos se resuelve en la plataforma de deploy (preview deployments por rama, sección 04 de `DEPLOY_AND_FAILURES_STANDARD.md`), no en la topología de Git.

**[REQUIRED]** Para cambios que caben en una sesión de trabajo, commit directo a `main` es válido (equipo de 1 — coherente con `Engineering-OS/19-Git-Standards.md`). Rama separada `feat/<nombre>` o `fix/<nombre>` cuando aplica al menos uno:

1. El cambio va a quedar a medias entre sesiones y rompería `main` si se pusheara incompleto.
2. El cambio toca código crítico (auth, pagos, migraciones de DB) y quiere revisarse con calma en un PR antes de merge.
3. El cambio lo hizo una IA de forma autónoma sobre código crítico.

**Por qué:** la regla real no es "usa ramas" sino "**`main` siempre desplegable**" — porque `main` está conectada a deploy automático (Pages) y un push roto es un deploy roto en producción. La rama es el mecanismo para cumplir eso cuando el trabajo no cabe entero en un push, no un ritual.

**[RECOMMENDED]** Ramas con prefijo por tipo: `feat/`, `fix/`, `chore/`, `docs/` — mismo vocabulario que los commits (sección 02), para que el nombre de la rama ya diga qué clase de cambio contiene.

**Implementación (gh CLI):**
```bash
git switch -c feat/checkout-stripe        # nace de main actualizada
# ... trabajo, commits ...
git push -u origin feat/checkout-stripe
gh pr create --fill                        # PR opcional (criterio arriba)
gh pr merge --squash --delete-branch       # squash: 1 rama corta = 1 commit limpio en main
```

**[RECOMMENDED]** Merge por **squash** para ramas cortas: el historial de `main` queda como una secuencia de cambios completos y desplegables, no de commits `wip:` intermedios. La excepción: ramas donde cada commit intermedio tiene valor propio de bisect/rollback — ahí merge normal.

---

## 02. Commits

**[REQUIRED]** Formato Conventional Commits pragmático, en inglés:

```
tipo(scope opcional): descripción imperativa en minúscula

feat(auth): add magic link login
fix(worker): handle empty webhook payload
chore: bump wrangler to 4.x
```

Tipos válidos: `feat`, `fix`, `chore`, `docs`, `refactor`, `perf`, `test`. Prefijo `wip:` válido solo para el commit de cierre de día con trabajo a medias (ritual de `Engineering-OS/19-Git-Standards.md`), nunca como estado final de una rama que se mergea.

**Por qué:** el formato no es estética — es metadata parseable. Permite generar changelogs, buscar `git log --grep "^fix"` cuando algo se rompió, y que una IA que lee el historial entienda la intención de cada cambio sin leer el diff. "Pragmático" significa: no se exige body ni footer ni `BREAKING CHANGE:` salvo que aporten; un `fix: typo` de una línea es un commit completo.

**[REQUIRED]** Un commit = un cambio lógico. No commits "fin del día" que mezclan un fix, dos features y un refactor — cuando uno de esos cambios resulta ser el bug, `git revert` y `git bisect` se vuelven inútiles porque revertir uno revierte todos.

### 02.1 Qué NUNCA se commitea

**[REQUIRED]** Nunca entran al historial, bajo ninguna circunstancia:

- **Secretos**: API keys, tokens, passwords, `serviceAccount*.json`, claves privadas (`*.pem`, `id_rsa`).
- **Archivos de entorno con valores**: `.env`, `.env.*` (excepto `.env.example` con placeholders), `.dev.vars`.
- **Dependencias**: `node_modules/` — se reconstruyen con `npm ci` desde el lockfile.
- **Artefactos generados**: `dist/`, `build/`, `.wrangler/`, coverage — se regeneran desde el fuente; commitearlos garantiza que diverjan de él.
- **Bases de datos locales y dumps con datos reales** (`*.sqlite`, `*.dump`).

**Por qué:** un secreto en Git es público para efectos prácticos aunque el repo sea privado — queda en cada clon, en cada fork, en el reflog, y sobrevive al `git rm` (el historial lo conserva). Los generados y dependencias inflan el repo y producen diffs ilegibles que entierran el cambio real. El lockfile (`package-lock.json`) **sí** se commitea: es la única garantía de builds reproducibles.

**[REQUIRED]** `.gitignore` base de todo repo del stack (se crea en el primer commit, no "después"):

```gitignore
# Secretos y entorno
.env
.env.*
!.env.example
.dev.vars
*.pem
serviceAccount*.json

# Dependencias y generados
node_modules/
dist/
build/
.wrangler/
coverage/

# Ruido de SO/editor
.DS_Store
Thumbs.db
*.log
```

**[RECOMMENDED]** La lista de variables de entorno requeridas vive en un `.env.example` commiteado con placeholders — así el repo documenta qué necesita sin exponer valores (coherente con `Engineering-OS/20-Deployment.md`).

---

## 03. Protección de `main`

**[REQUIRED]** La rama principal tiene protección activada en la plataforma, con este perfil mínimo realista para dev solo:

| Ajuste | Valor | Negociable |
|---|---|---|
| Bloquear force-push a `main` | Sí | No |
| Bloquear borrado de `main` | Sí | No |
| Require status checks (CI verde antes de merge de PR) | Sí, cuando el repo tiene CI | No |
| Require pull request antes de merge | Opcional | Sí (equipo de 1) |
| Require approvals | No | — |

**Por qué:** el force-push es la única operación Git que destruye historia remota — un `git push --force` equivocado (o una IA con acceso al repo que lo ejecute) puede borrar semanas de trabajo sin recuperación fácil. Bloquearlo cuesta cero fricción diaria. En cambio, exigir PR + approval a un equipo de 1 es teatro: nadie más va a aprobar, así que solo agrega un click. Los status checks sí valen: son la única "revisión" automática que existe cuando no hay segundo humano — un merge no puede entrar con typecheck o tests rotos.

**Implementación (gh CLI — verificar sintaxis exacta del endpoint en docs oficiales si cambia):**
```bash
gh api -X PUT "repos/JCDIGITALL/<repo>/branches/main/protection" \
  --input - <<'EOF'
{
  "required_status_checks": { "strict": false, "contexts": ["ci"] },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

**[RECOMMENDED]** `enforce_admins: false` en equipo de 1 — deja una vía de escape deliberada para emergencias (hotfix con CI caído), que se usa conscientemente y no como atajo habitual. Si el equipo crece a 2+, pasa a `true`.

---

## 04. Seguridad de la cuenta

La cuenta de GitHub es el punto único de acceso a **todo** el código, los secretos de CI y los deploys. Comprometerla equivale a comprometer el negocio completo — por eso esta sección tiene más `[REQUIRED]` que ninguna otra.

### 04.1 Autenticación

**[REQUIRED]** 2FA activado con **app TOTP o llave de seguridad hardware — nunca SMS** como método primario ni como fallback.

**Por qué:** el SMS es vulnerable a SIM-swapping — el atacante no necesita tu teléfono, solo convencer a la operadora de portar tu número. Una app TOTP o una llave FIDO2 no tienen ese vector. GitHub permite eliminar SMS como fallback; hacerlo.

**[RECOMMENDED]** Passkeys como método de login principal: resistentes a phishing por diseño (la credencial está ligada al dominio real — un sitio falso `github-login.com` no puede usarla) y más rápidas que password+TOTP.

**[REQUIRED]** Los recovery codes de 2FA se guardan en el gestor de contraseñas — no en un archivo del repo, no en notas sin cifrar. Perderlos con el teléfono = cuenta bloqueada permanentemente.

### 04.2 Tokens (PAT)

**[REQUIRED]** Todo token de acceso personal es **fine-grained, con fecha de expiración, y scope mínimo** (solo los repos que necesita, solo los permisos que necesita). **Nunca classic tokens sin expiración.**

**Por qué:** un classic token con scope `repo` y sin expiración es una llave maestra eterna: quien lo obtenga (un log filtrado, un `.env` commiteado, un paquete npm malicioso que lee variables de entorno) tiene acceso total a todos los repos, para siempre, hasta que alguien se dé cuenta. Un token fine-grained expira solo y limita el daño a un repo y unas operaciones concretas — convierte una catástrofe en un incidente.

**Implementación:** GitHub → Settings → Developer settings → Fine-grained tokens. Expiración máxima 90 días; regla práctica: si un token "necesita" no expirar, lo que realmente se necesita es una GitHub App o el `GITHUB_TOKEN` efímero de Actions (sección 07).

**[REQUIRED]** Un token comprometido o sospechoso se revoca primero y se investiga después — revocar es gratis, esperar no.

### 04.3 Claves SSH

**[REQUIRED]** Claves SSH de tipo **ed25519** con **passphrase**. Nunca RSA-1024/DSA (obsoletas), nunca sin passphrase en una máquina de trabajo.

**Por qué:** ed25519 es el estándar actual (claves cortas, rápidas, sin los parámetros débiles históricos de RSA). La passphrase es la segunda capa: sin ella, cualquiera que copie el archivo `~/.ssh/id_ed25519` (malware, laptop robada, backup expuesto) tiene tu identidad Git. Con `ssh-agent` la passphrase se escribe una vez por sesión — el costo diario es casi cero.

```bash
ssh-keygen -t ed25519 -C "jeilincastro989@gmail.com"   # pedirá passphrase: ponerla
gh ssh-key add ~/.ssh/id_ed25519.pub --title "laptop-2026"
```

**[RECOMMENDED]** Una clave por máquina (título descriptivo), no la misma clave copiada entre máquinas — así revocar la de una laptop perdida no corta el acceso desde las demás.

---

## 05. Secret scanning y push protection

**[REQUIRED]** En todo repo: **secret scanning + push protection habilitados**. En repos públicos GitHub los ofrece gratis; en privados, verificar disponibilidad del plan en docs oficiales — si la plataforma no lo cubre, un hook local pre-push con un scanner (p. ej. `gitleaks`) cumple la misma regla agnóstica: *ningún push llega al remoto sin pasar por un detector de secretos*.

**Por qué:** la protección post-hoc (alerta cuando el secreto **ya** está en el historial) llega tarde — a ese punto el secreto está comprometido y hay que rotarlo (sección 08). Push protection actúa **antes**: rechaza el push que contiene el patrón de un secreto, cuando todavía es un archivo local corregible con `git commit --amend`. Es la diferencia entre prevenir el incendio y que suene la alarma.

```bash
gh api -X PATCH "repos/JCDIGITALL/<repo>" --input - <<'EOF'
{ "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" } } }
EOF
```

**[REQUIRED]** Si push protection bloquea un push, la opción "bypass" solo se usa para falsos positivos evidentes (un string de ejemplo en docs). Si hay duda de si es un secreto real: es un secreto real.

---

## 06. Dependabot

**[REQUIRED]** **Dependabot alerts habilitado** en todo repo activo: aviso automático cuando una dependencia tiene una vulnerabilidad conocida (CVE).

**Por qué:** un dev solo no lee advisories de seguridad de sus 300 dependencias transitivas — nadie lo hace. La alerta automática es el único mecanismo realista por el cual un `lodash` vulnerable en producción llega a tu atención antes de que lo explote alguien.

**[RECOMMENDED]** Dependabot security updates (PRs automáticos que parchean la vulnerabilidad) habilitado — convierte la alerta en un fix listo para mergear.

**[RECOMMENDED]** Auto-merge de PRs de Dependabot solo cuando se cumplen **todas**:

1. El bump es **patch o minor de una dependencia directa no crítica** (no major, no nada que toque auth/pagos/crypto).
2. El repo tiene **CI real que lo valida** (typecheck + tests + build — sección 01 de `DEPLOY_AND_FAILURES_STANDARD.md`) como status check requerido.
3. El update es de **seguridad** o de una dependencia de desarrollo.

Sin CI que lo valide, auto-merge es mergear a ciegas: peor que no actualizar. Majors siempre a mano — cambian contratos.

**Nota de coherencia con QA:** `06_Testing/01_QA_STRATEGY.md` adopta **Renovate** como generador de PRs de actualización (agrupación + automerge fino). Si un repo adopta Renovate, los *security updates* de Dependabot se desactivan en ese repo — **un solo generador de PRs de dependencias, nunca ambos**. Las *alerts* de Dependabot (esta sección, REQUIRED) se mantienen siempre: son pasivas y gratuitas.

```bash
# .github/dependabot.yml mínimo
# version: 2
# updates:
#   - package-ecosystem: "npm"
#     directory: "/"
#     schedule: { interval: "weekly" }
#     open-pull-requests-limit: 5
```

---

## 07. GitHub Actions con seguridad

El runner de CI ejecuta código con acceso a los secretos de deploy — es el eslabón que los atacantes de supply-chain atacan hoy. Cuatro reglas cubren los vectores principales:

**[REQUIRED] Permisos mínimos del token de CI por workflow.** Todo workflow declara `permissions:` explícito al tope, con lo mínimo que necesita — nunca se hereda el default permisivo del repo.

```yaml
permissions:
  contents: read          # lo único que necesita un workflow de build/test
```

**Por qué:** el `GITHUB_TOKEN` implícito puede, por default, escribir en el repo. Si una dependencia comprometida ejecuta código dentro del job, hereda esos permisos: puede pushear commits, crear releases, alterar el repo. `permissions: contents: read` reduce el botín de un job comprometido a "leer un repo que ya podía leer".

**[REQUIRED] Pin por SHA de toda action de terceros en workflows que tocan secretos** (deploy, publicación). Actions oficiales de GitHub (`actions/*`) pueden usar tag mayor; todo lo demás, SHA completo:

```yaml
- uses: actions/checkout@v4                                  # oficial: tag OK
- uses: cloudflare/wrangler-action@<SHA-completo>            # terceros: SHA real de la versión auditada
  # ^ obtener el SHA del release que auditaste (gh api repos/cloudflare/wrangler-action/commits/vX.Y.Z)
  #   y mantener al lado el comentario con la versión legible (ej. v3.14.0)
```

**Por qué:** un tag (`@v3`) es un puntero móvil — si la cuenta del autor de la action es comprometida, el atacante re-apunta el tag a código que exfiltra `secrets.CLOUDFLARE_API_TOKEN`, y todos los repos que usan `@v3` lo ejecutan en su siguiente run sin cambiar una línea. Esto ya ocurrió en ataques reales de supply-chain. Un SHA es inmutable: lo que auditaste es lo que corre. Actualizar el SHA es un chore consciente, no un evento silencioso.

**[REQUIRED] Nunca `pull_request_target` (ni `workflow_run` con contexto privilegiado) combinado con checkout del código del PR externo.**

**Por qué:** `pull_request_target` corre con los secretos del repo base; si además hace checkout del código del PR, cualquier desconocido que abra un PR ejecuta su código con tus secretos. Es la receta canónica de robo de secretos en repos públicos. Para validar PRs externos: `pull_request` normal (sin secretos). Si un flujo parece necesitar ambas cosas a la vez, se rediseña en dos workflows (uno sin privilegios que valida, otro privilegiado que no toca código externo) — verificar el patrón exacto en docs oficiales.

**[REQUIRED] Secretos de deploy a producción viven en un *environment* con protección, no como secretos planos de repo.** Secretos de repo: solo para lo que cualquier workflow puede usar sin riesgo (p. ej. un token de solo-lectura). El token que deploya a producción va en un environment `production` que solo los workflows sobre `main` pueden referenciar.

**Por qué:** un secreto de repo es accesible desde cualquier workflow de cualquier rama — un experimento en una rama, o un workflow modificado por error, puede leerlo. El environment ata el secreto a la condición "solo desde `main`", que es exactamente la única ruta legítima hacia producción.

---

## 08. Si un secreto llegó al historial

**[REQUIRED]** El orden es innegociable: **1) ROTAR el secreto, 2) recién después limpiar el historial.** Nunca al revés, nunca "solo limpiar".

**Por qué — la regla que más gente entiende mal:** reescribir la historia de Git **no invalida el secreto**. El secreto es válido hasta que el proveedor lo revoque, y ya puede haber sido copiado: bots escanean commits públicos de GitHub en **segundos** desde el push; además sobrevive en clones locales, forks, cachés de la plataforma y en cualquier CI que lo haya loggeado. Limpiar el historial sin rotar es cerrar la puerta con el ladrón ya adentro. La limpieza es higiene (que no siga a la vista); la rotación es la mitigación real.

**Procedimiento:**

```bash
# 1. ROTAR YA — en el proveedor (Cloudflare, Supabase, Stripe...):
#    revocar la clave expuesta, generar una nueva, actualizarla donde se usa
#    (wrangler secret put, GitHub environment secrets, .dev.vars local).

# 2. Verificar qué alcanzó a usar la clave vieja (logs del proveedor) — ¿hubo uso ajeno?

# 3. Limpiar el historial (git-filter-repo, sucesor recomendado de BFG):
pip install git-filter-repo
git clone --mirror git@github.com:JCDIGITALL/<repo>.git
cd <repo>.git
git filter-repo --replace-text <(echo "LA_CLAVE_EXPUESTA==>***REMOVED***")
git push --force --mirror
# (requiere levantar temporalmente el bloqueo de force-push de la sección 03 — y re-activarlo al terminar)

# 4. Re-clonar en local (el clon viejo conserva la historia sucia).
# 5. Cerrar la alerta de secret scanning como "revoked".
# 6. Post-mortem de una línea: ¿por qué push protection no lo paró? (¿estaba apagado? ¿patrón no cubierto? → gitleaks local)
```

**[REQUIRED]** Esto aplica igual si el secreto solo estuvo expuesto minutos, o si el repo es privado — "privado" reduce la probabilidad, no la convierte en cero, y el costo de rotar es minutos.

---

## Checklist final

**Ramas y commits**
- [ ] ¿`main` desplegable en todo momento; trabajo largo o crítico en rama corta con prefijo?
- [ ] ¿Commits en formato `tipo(scope): descripción`, un cambio lógico por commit?
- [ ] ¿`.gitignore` base presente desde el primer commit; `.env.example` sin valores reales?
- [ ] ¿Cero secretos, `node_modules/`, ni generados en el historial?

**Protección y cuenta**
- [ ] ¿`main` con force-push y borrado bloqueados; status checks requeridos si hay CI?
- [ ] ¿2FA con app/llave (sin SMS ni como fallback); recovery codes en el gestor de contraseñas?
- [ ] ¿Todos los PAT fine-grained, con expiración y scope mínimo; cero classic tokens vivos?
- [ ] ¿SSH ed25519 con passphrase, una clave por máquina?

**Plataforma**
- [ ] ¿Secret scanning + push protection habilitados en cada repo?
- [ ] ¿Dependabot alerts activo; auto-merge solo patch/minor no crítico con CI verde?
- [ ] ¿Workflows con `permissions:` mínimo declarado; actions de terceros pineadas por SHA donde hay secretos?
- [ ] ¿Ningún `pull_request_target` con checkout de código externo; secretos de prod en environment, no en repo?
- [ ] ¿Si un secreto tocó el historial: rotado ANTES de limpiar, historial limpiado, alerta cerrada?
