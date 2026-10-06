---
title: "Dominio API — Índice"
category: 03_API
doc_type: referencia
tags: [api, indice]
summary: "Índice del dominio API. El estándar operativo vive en API_ENGINEERING_STANDARD.md."
keywords: [api, indice, rest, contratos]
updated: 2026-07-09
status: current
---

# Dominio API — Contratos, Envelopes e Idempotencia

Este dominio define los contratos de interfaz pública hacia el cliente, el formato de respuestas estándar `{ ok, data }` / `{ ok, error }`, y el procesamiento seguro de webhooks idempotentes.

## Documentos del Dominio

| Documento | Tipo | Descripción |
|---|---|---|
| [API_ENGINEERING_STANDARD.md](API_ENGINEERING_STANDARD.md) | Estándar | Contrato hacia afuera, envelope estándar, versionado y validación |
| [WEBHOOK_IDEMPOTENCY_STANDARD.md](WEBHOOK_IDEMPOTENCY_STANDARD.md) | Estándar | Procesamiento seguro e idempotente de webhooks (Stripe/Wompi/NowPayments) sin dobles cobros |
| [PAGUELOFACIL_INTEGRATION.md](PAGUELOFACIL_INTEGRATION.md) | Referencia | Forma real del webhook de PagueloFácil (Enlace de Pago): `customFields` por `nameOrLabel`, sin firma ni endpoint de re-verificación, `operationType` obligatorio |

