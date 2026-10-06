---
title: "Matriz de Selección de Stack Tecnológico y Arquitectura"
category: 09_Architecture
doc_type: estandar
tags: [arquitectura, stack, decision-matrix, frontend, backend, database]
summary: "Matriz y árbol de decisión para elegir el stack tecnológico óptimo según el tipo de cliente, modelo de negocio, presupuesto y requisitos de escalabilidad (SaaS, E-commerce, Trading, Móvil, Desktop)."
keywords: [stack, decision-matrix, arquitectura, react, astro, workers, vps, supabase, tauri, expo]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "09_Architecture/ARCHITECTURE_DECISION_LOG.md"
  - "08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md"
---

# MATRIZ DE SELECCIÓN DE STACK Y ARQUITECTURA

> **Objetivo:** Definir una decisión técnica estandarizada, rápida y predecible para cada proyecto nuevo de la agencia, evitando la improvisación y garantizando que todo el equipo utilice stacks coherentes y testeados en producción.

---

## 1. Árbol de Decisión por Tipo de Proyecto

| Tipo de Proyecto | Frontend Recomendado | Backend / API | Base de Datos | Storage / CDN | Cuándo Elegir este Stack |
|---|---|---|---|---|---|
| **SaaS B2B / Dashboard** | React 19 + Vite + Tailwind | Cloudflare Workers (Multi-Worker) | Supabase (PostgreSQL + RLS) | Cloudflare R2 | Plataformas con múltiples usuarios, roles, métricas y autenticación compleja. |
| **Landing Page / Web Comercial** | Astro / React 19 + Tailwind | Cloudflare Worker Gateway | Cloudflare D1 / Supabase | Cloudflare Pages CDN | Sitios corporativos con foco en SEO, carga instantánea y conversión rápida. |
| **E-Commerce / Tienda Online** | React 19 + Vite (SPA / PWA) | Cloudflare Workers + Webhooks | Supabase / D1 | Cloudflare R2 | Tiendas con carrito, pasarelas de pago (Stripe/Wompi) y gestión de catálogo. |
| **App Móvil (iOS / Android)** | Expo (React Native) + TypeScript | Cloudflare Workers | Supabase (PostgreSQL) | Cloudflare R2 | Aplicaciones móviles híbridas que requieran notificaciones push y cámara. |
| **App de Escritorio (Desktop)** | Tauri v2 + React 19 | Rust Backend (IPC) | SQLite local + Supabase Sync | Local FS / R2 | Herramientas de escritorio que requieren uso intensivo de CPU o funcionamiento 100% offline. |
| **Trading / Realtime / Bots** | React 19 + Lightweight Charts | Workers + VPS (Node/Go/Python) | Supabase + Timescale/D1 | Cloudflare R2 | Bots de ejecución de órdenes, WebSockets de alta frecuencia y análisis de gráficos. |

---

## 2. Decisión Arquitectónica Clave: Edge Workers vs. VPS Dedicado

```
                               ¿Tu backend requiere...?
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     [ Tareas Serverless Estándar ]                 [ Procesos Continuos / Pesados ]
     • APIs REST / GraphQL CRUD                     • Bots de WhatsApp / Baileys activos 24/7
     • Autenticación y JWT                          • Sockets persistentes sin cortes
     • Webhooks de pago (Stripe/Wompi)              • Backtesting o cálculos ML intensivos
     • Transformación de datos                      • Tareas cron de larga duración (> 15 min)
                  │                                               │
                  ▼                                               ▼
      ✅ CLOUDFLARE WORKERS                            ✅ VPS DEDICADO (Hetzner / Contabo)
      • Latencia < 50ms global                         • Reverse proxy obligatorio con Caddy
      • Cero mantenimiento de SO                       • Firewall UFW estricto (solo 22, 80, 443)
      • Costos cercanos a cero                         • Docker Compose para aislamiento
```

---

## 3. Matriz de Almacenamiento de Datos

| Necesidad de Datos | Base de Datos Elegida | Razón Técnica |
|---|---|---|
| **Datos Relacionales con Roles Complejos** | **Supabase (Postgres)** | RLS como fuente de verdad inquebrantable (`TENANT-001`), autenticación integrada y Realtime. |
| **Contenido Estático / Blog / Catálogo Cacheable** | **Cloudflare D1 (SQLite Edge)** | Latencia ultra-baja en el Edge y bajo costo para lecturas masivas. |
| **Cache de Sesión / Rate Limiting / Tokens Temporales** | **Cloudflare KV** | Lecturas en < 10ms a nivel global con TTL automático. |
| **Archivos, Imágenes, Comprobantes y Videos** | **Cloudflare R2** | Almacenamiento compatible con S3 sin costos abusivos de egreso. |
