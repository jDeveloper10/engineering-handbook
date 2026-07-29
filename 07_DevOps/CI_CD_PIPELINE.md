---
title: "Estándar de CI/CD para Monorepo"
category: 07_DevOps
doc_type: estandar
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

**[RECOMMENDED]** **Por qué:** la regla real es que el pipeline solo debe reconstruir y desplegar lo que cambió; sin eso, un cambio de una línea paga el coste de todo el repositorio y el equipo acaba saltándose el pipeline. Turborepo es la implementación concreta de esa regla, no la regla: cualquier herramienta con grafo de dependencias y caché sirve.

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

**[REQUIRED]** **Por qué:** un gate que se ejecuta después del merge no es un gate, es un informe. La verificación tiene que correr sobre el PR, cuando el cambio todavía se puede rechazar sin coste y su autor tiene el contexto fresco.

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

**[REQUIRED]** **Por qué:** un despliegue manual es un procedimiento que se ejecuta distinto cada vez y que solo una persona sabe hacer. Automatizarlo por entorno hace que el despliegue sea reproducible, auditable y aburrido, que es exactamente lo que debe ser.

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

**[RECOMMENDED]** **Por qué:** exponer primero a una fracción del tráfico convierte un fallo global en uno acotado y detectable por métricas. Es recomendado porque exige volumen suficiente para que la muestra signifique algo: con poco tráfico, el canario no detecta nada y solo añade latencia al proceso.

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

**[REQUIRED]** **Por qué:** la capacidad de volver atrás es lo que hace que desplegar seguido sea seguro. Si revertir depende de que alguien esté despierto y recuerde el comando, la reacción tarda más que el incidente. Y un rollback que nunca se ha probado no existe.

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

**[RECOMMENDED]** **Por qué:** un entorno desplegado por PR permite revisar comportamiento en vez de solo leer el diff, y detecta lo que ningún test cubre. Es recomendado porque consume recursos por rama y en cambios sin superficie visible no aporta nada.

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
