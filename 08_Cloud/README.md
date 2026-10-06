---
title: "Dominio Cloud — Índice"
category: 08_Cloud
doc_type: referencia
tags: [cloud, indice]
summary: "Índice del dominio Cloud. El estándar operativo de la plataforma vive en CLOUDFLARE_PLATFORM_STANDARD.md."
keywords: [cloud, indice, cloudflare, workers, edge]
updated: 2026-07-09
status: current
---

# Dominio Cloud — Plataforma y Patrones

Este dominio define la infraestructura y patrones operativos de computación y almacenamiento en el Edge (Cloudflare).

## Documentos del Dominio

| Documento | Tipo | Descripción |
|---|---|---|
| [CLOUDFLARE_PLATFORM_STANDARD.md](CLOUDFLARE_PLATFORM_STANDARD.md) | Estándar | Plataforma completa: límites, Workers, KV, D1, R2, Queues, Durable Objects y WAF |
| [PATRON_R2_UPLOAD_SEGURO.md](PATRON_R2_UPLOAD_SEGURO.md) | Patrón | Subida segura a R2 sin exponer llaves maestras en Vite/React |
| [PATRON_GENERACION_PDF_EDGE.md](PATRON_GENERACION_PDF_EDGE.md) | Patrón | Generación de PDFs en Cloudflare Workers |
| [ESCALABILIDAD_Y_MANTENIMIENTO.md](ESCALABILIDAD_Y_MANTENIMIENTO.md) | Estándar | Monitoreo con Sentry, connection pooling, caching en Edge y SLAs |
