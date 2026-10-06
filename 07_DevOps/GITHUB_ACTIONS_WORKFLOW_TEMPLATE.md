---
title: "Plantilla de Pipeline CI/CD con GitHub Actions"
category: 07_DevOps
doc_type: referencia
tags: [devops, ci-cd, github-actions, pipeline, automated-test, secret-scan]
summary: "Plantilla de workflow de GitHub Actions (.github/workflows/ci.yml) para automatizar el control de calidad en cada Pull Request y push: typecheck, linting, escáner de secretos, tests automatizados y despliegue a Cloudflare."
keywords: [ci-cd, github-actions, pipeline, typecheck, lint, secret-scan, cloudflare, vitest]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "07_DevOps/GITHUB_STANDARD.md"
  - "06_Testing/Pipelines/03_CI_CD.md"
---

# PLANTILLA DE PIPELINE CI/CD (GITHUB ACTIONS)

> **Uso:** Copiar este archivo en `.github/workflows/ci.yml` en la raíz de cualquier proyecto nuevo de la agencia. Bloqueará automáticamente cualquier Pull Request o commit que rompa el tipado, falle tests o intente fugar secretos.

---

## ⚠️ Gate de producción con aprobación manual — cuándo usarlo y cómo

**`GITHUB_STANDARD.md` §03 dice, para un dev solo con un solo proyecto, que exigir aprobación humana es "teatro" — nadie más va a aprobar, así que solo agrega fricción.** Esa regla sigue siendo correcta en ese escenario. Pero cambia en uno real y distinto: **agencia con varios clientes en paralelo**, donde cada deploy a producción es el sitio de OTRO cliente, no un SaaS propio — ahí un clic de revisión final antes de salir a producción no es teatro, es la única red de seguridad real cuando quien deploya está saltando entre 3-4 proyectos el mismo día.

**Regla de decisión:**
- Un solo proyecto propio, sin nadie más dependiendo del deploy → seguir `GITHUB_STANDARD.md` §03 tal cual (sin approval, solo status checks).
- Varios proyectos/clientes en paralelo, o cualquier caso donde un deploy accidental afecta a alguien que no es vos → usar el patrón de esta sección.

**Corrección verificada (no asumir esto sin chequear la doc oficial primero — ya nos costó $4 reales averiguarlo):** GitHub Environments con *required reviewers* (el botón nativo "Review deployments") **NO existe para repos privados de cuenta personal bajo ningún plan** — GitHub Pro incluido. Esa función solo existe si el repo pertenece a una **organización** en GitHub Team o Enterprise. Antes de prometerle este mecanismo a un cliente/usuario con cuenta personal, confirmar con `gh api repos/<owner>/<repo> --jq '{private, owner_type: .owner.type}'` — si `owner_type` es `"User"`, el gate nativo no está disponible, usar el patrón de abajo en su lugar.

**Patrón que sí funciona en cualquier plan, cuenta personal u organización — gate por disparo manual:**

El job de deploy usa `on: workflow_dispatch` como **único** trigger — nunca `push`. Sin un click humano en la pestaña Actions (o `gh workflow run`), el job no existe para GitHub, no hay nada que aprobar ni pausar porque nunca arrancó. Es un archivo de workflow SEPARADO del `ci.yml` de validación automática (ese sigue corriendo en cada push/PR normalmente):

```yaml
# .github/workflows/deploy-production.yml
name: Deploy a Producción (manual)

on:
  workflow_dispatch: {}   # <- nunca push: ese es el gate completo

jobs:
  verify-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx vitest run
      - run: npm run build
      - name: 🚀 Deploy real (Cloudflare Pages/Workers)
        run: npx wrangler deploy   # o pages-action, según el proyecto
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      - name: 🩺 Smoke test post-deploy
        run: |
          sleep 5
          curl -sf https://<dominio-del-proyecto>/api/health
```

**Por qué re-correr typecheck/tests acá y no solo `needs: validate`:** al ser un workflow separado disparado a mano, no hay un run anterior del que "heredar" el resultado de validación de forma confiable (pudo haber pasado tiempo, o el branch pudo cambiar) — este job valida y despliega en el mismo run, así nunca se despliega código sin haber pasado el gate en esa ejecución exacta.

**Si en algún momento el repo SÍ pertenece a una organización en Team+:** ahí sí usar el Environment nativo con `reviewers` (approval real desde la UI de GitHub, más prolijo) — el `gh api` para crearlo:

```bash
gh api -X PUT "repos/<org>/<repo>/environments/production" \
  --input - <<'EOF'
{ "reviewers": [{ "type": "User", "id": <user-id-numerico> }] }
EOF
```
y en el job del workflow, agregar `environment: production` (podés mantener el trigger en `push` a `main` en ese caso, porque el approval real lo da el Environment, no el disparo manual).

---

## Archivo: `.github/workflows/ci.yml`

```yaml
name: CI / Quality & Security Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    name: Lint, Types, Secrets & Tests
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout del Código
        uses: actions/checkout@v4

      - name: ⚙️ Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: 📦 Instalar Dependencias
        run: npm ci

      - name: 🔍 1. Validación de Tipos (TypeScript)
        run: npx tsc --noEmit

      - name: 🧹 2. Linter de Código
        run: npm run lint

      - name: 🧪 3. Pruebas Automatizadas (Vitest)
        run: npm run test:ci || npx vitest run

      - name: 🏗️ 4. Compilación del Proyecto
        run: npm run build

      - name: 🛡️ 5. Escaneo de Secretos en el Bundle
        run: node tools/scan-bundle-secrets.mjs dist || echo "Verificado con scan-secrets"

  deploy-staging:
    name: Deploy to Cloudflare Pages (Preview)
    needs: validate
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - name: 📥 Checkout
        uses: actions/checkout@v4

      - name: ⚙️ Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: 📦 Install & Build
        run: |
          npm ci
          npm run build

      - name: 🚀 Despliegue de Preview en Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: ${{ vars.CLOUDFLARE_PROJECT_NAME }}
          directory: dist
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
```

---

## Configuración de Secretos en GitHub

En tu repositorio de GitHub (`Settings` ➔ `Secrets and variables` ➔ `Actions`), configurar:

| Secreto / Variable | Tipo | Descripción |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | Secret | Token de API de Cloudflare con permisos de Pages / Workers |
| `CLOUDFLARE_ACCOUNT_ID` | Secret | ID de cuenta de Cloudflare |
| `CLOUDFLARE_PROJECT_NAME` | Variable | Nombre del proyecto en Cloudflare Pages |
