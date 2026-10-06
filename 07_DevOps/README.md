---
title: "Dominio DevOps — Índice"
category: 07_DevOps
doc_type: referencia
tags: [devops, indice]
summary: "Índice del dominio DevOps: pipelines de CI/CD, despliegue, infraestructura como código y observabilidad."
keywords: [devops, indice, ci-cd, deploy, iac, observabilidad]
updated: 2026-07-09
status: current
---

# Dominio DevOps — CI/CD, Despliegues y Automatización

Este dominio define las prácticas de Git, flujos de integración y despliegue continuo (CI/CD), secret scanning y manejo de fallos en producción.

## Documentos del Dominio

| Documento | Tipo | Descripción |
|---|---|---|
| [GITHUB_STANDARD.md](GITHUB_STANDARD.md) | Estándar | Gestión de repositorios, cuentas, PATs, Actions y secret scanning |
| [DEPLOY_AND_FAILURES_STANDARD.md](DEPLOY_AND_FAILURES_STANDARD.md) | Estándar | Despliegues, rollbacks y catálogo de fallos B1–B7 |
| [CI_CD_PIPELINE.md](CI_CD_PIPELINE.md) | Estándar | Pipeline unificado de integración y entrega continua |
| [GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md](GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md) | Plantilla | Workflow YAML (.github/workflows/ci.yml) para lint, types, tests y preview |
| [INFRA_AS_CODE.md](INFRA_AS_CODE.md) | Estándar | Configuración declarativa con Wrangler y Docker |
| [OBSERVABILITY_STANDARD.md](OBSERVABILITY_STANDARD.md) | Estándar | Métricas, logs estructurados y telemetría |
| [PLAYBOOK_IOS_TESTFLIGHT_SIN_MAC.md](PLAYBOOK_IOS_TESTFLIGHT_SIN_MAC.md) | Runbook | Compilar y publicar iOS en TestFlight desde Linux (sin Mac) con GitHub Actions o EAS, y 6 incidentes reales |
| [PLAYBOOK_CREDENCIALES_MULTI_APP_APPLE_GOOGLE.md](PLAYBOOK_CREDENCIALES_MULTI_APP_APPLE_GOOGLE.md) | Runbook | Credenciales Apple/Google reutilizables entre apps de distintos clientes (patrón agencia) y automatización de submission, con 11 incidentes reales |
| [PLAYBOOK_EXPO_LIVE_ACTIVITIES.md](PLAYBOOK_EXPO_LIVE_ACTIVITIES.md) | Runbook | Live Activities (Dynamic Island / lock screen) con actualizaciones por push en Expo managed: módulo local + config plugin de targets, sin eyectar |

