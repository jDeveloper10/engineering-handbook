---
title: "Estándar Avanzado de CI/CD, Despliegues y Rollbacks"
category: 07_DevOps
doc_type: estandar
tags: [ci-cd, github-actions, rollbacks, blue-green, renovate, dependabot, security-scanning]
summary: "Estándar para pipelines avanzadas de CI/CD en GitHub Actions: migraciones automáticas de base de datos, desmarcado Blue/Green en Workers, rollback automático ante tasa de error > 1%, previsualizaciones por PR y auditoría de seguridad."
keywords: [ci-cd, github-actions, rollback, blue-green, dependabot, renovate, preview-environments, secret-rotation]
updated: 2026-07-27
status: current
---

# ESTÁNDAR AVANZADO DE CI/CD Y AUTOMATIZACIÓN DE DESPLIEGUES

## OBJETIVO
Definir los flujos de integración y despliegue continuos (CI/CD) para automatizar pruebas, migraciones de base de datos, escaneo de vulnerabilidades y revertir despliegues defectuosos de forma autónoma.

---

## REGLAS INQUEBRANTABLES

**[REQUIRED] CICD-001: Rollback Automático si la tasa de errores supera el 1% en los primeros 5 minutos.** Si tras un deploy el Health Check falla, Cloudflare retrotrae el tráfico al deployment previo inmediatamente.

> **Por qué:** un pico de errores tras un deploy detectado por una persona tarda minutos en notarse y más en revertirse; automatizar el rollback ante un umbral de error acota el incidente al tiempo que tarda el health check en detectarlo, no al tiempo que tarda un humano en despertarse.

**[REQUIRED] CICD-002: Escaneo de Vulnerabilidades y Secretos obligatorio en cada PR.** NUNCA fusionar código a `main` con vulnerabilidades severas o tokens expuestos.

> **Por qué:** un secreto o una vulnerabilidad severa que llega a `main` ya está en el historial de git para siempre, aunque se corrija después (ver `INCIDENT_RESPONSE.md`). Escanear en el PR es el único punto donde bloquear el problema no cuesta nada, porque el cambio todavía no se fusionó.

**[RECOMMENDED] CICD-003: Preview Environments por cada Pull Request.** Todo PR genera una URL de vista previa aislada en Cloudflare Workers / Pages.

> **Por qué:** un entorno de previsualización por PR permite revisar el comportamiento real antes de aprobar, no solo el diff. Es recomendado porque consume recursos de infraestructura por cada rama abierta, y en cambios sin superficie visible no aporta nada sobre leer el código.

---

## 1. WORKFLOW DE GITHUB ACTIONS CON ROLLBACK AUTOMÁTICO

```yaml
# .github/workflows/deploy.yml
name: Deployment Pipeline & Health Check

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }

      - run: pnpm install --frozen-lockfile
      - run: pnpm run check # Lint + Typecheck + Tests

      # Escaneo de Seguridad
      - name: Security Scan (Gitleaks)
        uses: gitleaks/gitleaks-action@v2

      # Despliegue de Workers
      - name: Deploy Workers to Cloudflare
        id: deploy
        run: npx wrangler deploy --env production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}

      # Health Check Post-Deploy con Rollback Automático
      - name: Post-Deploy Health Check
        run: |
          STATUS=$(curl -o /dev/null -s -w "%{http_code}" https://api.collabscribe.com/health)
          if [ "$STATUS" -ne 200 ]; then
            echo "❌ Health Check falló con status $STATUS. Iniciando Rollback..."
            npx wrangler rollback --env production
            exit 1
          fi
          echo "✅ Health Check exitoso."
```

---

## CHECKLIST DE CI/CD AVANZADO

- [ ] Escaneo de secretos (Gitleaks/Trufflehog) ejecutado en CI.
- [ ] Pruebas unitarias e integración en verde antes del paso de deploy.
- [ ] Health check automático post-deploy con script de `wrangler rollback`.
- [ ] Ambientes de previsualización (Preview URLs) activos por PR.
- [ ] Dependabot / Renovate configurados para parches automáticos.
