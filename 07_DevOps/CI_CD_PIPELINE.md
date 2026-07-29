---
title: "Estándar de CI/CD para Monorepo"
category: 07_DevOps
tags: [devops, ci-cd, monorepo, pipeline]
summary: "Reglas CI-001 a CI-006 para automatizar lint, test, build y deploy en monorepos con múltiples servicios, con checklist previo al despliegue."
keywords: [ci-cd, monorepo, lint, build, deploy, workers, pipeline]
updated: 2026-07-27
status: current
---

# Estándar de CI/CD para Monorepo (CI-001 a CI-006)

## 🎯 Objetivo
Automatizar linting, testing, building y deploy para monorepos con múltiples servicios (Workers, frontends, packages).

---

## ⚡ REGLAS INQUEBRANTABLES

### CI-001: MONOREPO CON TURBOREPO (O NX)

**Estructura obligatoria:**
```
monorepo/
├── apps/
│   ├── web/              # React frontend
│   ├── api-gateway/      # Cloudflare Worker
│   ├── auth-service/     # Cloudflare Worker
│   └── docs/             # Documentación
├── packages/
│   ├── shared/           # Tipos, schemas, utils
│   ├── ui/               # Componentes React compartidos
│   └── config/           # ESLint, TypeScript, Prettier
└── turbo.json
```

**`turbo.json`:**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "type-check": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "deploy": {
      "dependsOn": ["build", "test", "lint"],
      "cache": false
    }
  }
}
```

---

### CI-002: GITHUB ACTIONS - PIPELINE POR PR

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run lint
      
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run type-check
      
  test:
    runs-on: ubuntu-latest
    needs: [lint, type-check]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test
      
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      - uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

---

### CI-003: DEPLOY AUTOMÁTICO POR ENTORNO

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      
      - name: Deploy API Gateway
        run: npx wrangler deploy --env staging
        working-directory: apps/api-gateway
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
          
      - name: Deploy Auth Service
        run: npx wrangler deploy --env staging
        working-directory: apps/auth-service
        
      - name: Deploy Frontend
        run: npx wrangler pages deploy dist --project-name omnisuite
        working-directory: apps/web

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      
      - name: Deploy all services
        run: npx turbo run deploy --filter=./apps/*
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
          
      - name: Health check
        run: |
          curl -f https://api.omnisuite.com/health || exit 1
          
      - name: Notify deploy
        uses: slackapi/slack-github-action@v1
        with:
          payload: '{"text": "✅ Deploy completado: omnisuite.com"}'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

### CI-004: CANARY DEPLOYMENTS

```yaml
# Canary: 10% → 50% → 100%
- name: Canary deploy (10%)
  run: |
    npx wrangler deploy --env production --canary 10%
    
- name: Monitor error rate (5 min)
  run: |
    sleep 300
    curl -f https://api.omnisuite.com/metrics/error-rate | \
      jq '.rate < 0.01' || (echo "Rollback!" && exit 1)
      
- name: Full deploy (100%)
  if: success()
  run: npx wrangler deploy --env production
```

---

### CI-005: ROLLBACK AUTOMÁTICO

```bash
# scripts/rollback.sh
#!/bin/bash
SERVICE=$1
ENVIRONMENT=$2

echo "⏪ Rolling back $SERVICE in $ENVIRONMENT..."

# Obtener último deploy estable
LAST_STABLE=$(wrangler deployments list --env $ENVIRONMENT | grep "$SERVICE" | head -1 | awk '{print $1}')

# Rollback
wrangler rollback $LAST_STABLE --env $ENVIRONMENT

# Notificar
curl -X POST $SLACK_WEBHOOK -d "{\"text\": \"⏪ ROLLBACK: $SERVICE → $LAST_STABLE\"}"
```

---

### CI-006: PREVIEW DEPLOYMENTS POR PR

```yaml
# .github/workflows/preview.yml
name: Preview Deploy
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      
      - name: Deploy preview
        run: |
          npx wrangler pages deploy dist \
            --project-name omnisuite \
            --branch preview-${{ github.event.pull_request.number }}
            
      - name: Comment PR with URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `🚀 Preview: https://preview-${context.issue.number}.omnisuite.pages.dev`
            })
```

---

## 📋 CHECKLIST PRE-DEPLOY

- [ ] Todos los tests pasan
- [ ] Linting sin errores
- [ ] TypeScript sin errores
- [ ] Build exitoso
- [ ] Security audit limpio
- [ ] Migraciones de DB ejecutadas
- [ ] Variables de entorno configuradas
- [ ] Rollback plan documentado
- [ ] Health checks funcionando
