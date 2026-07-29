---
title: "Estándar de Monorepo (Turborepo)"
category: 09_Architecture
tags: [monorepo, turborepo, nx, typescript, ci, pnpm]
summary: "Monorepo con Turborepo: estructura de directorios, configuración base, diseño de los paquetes compartidos que son su razón de ser, y flujo de despliegue selectivo en CI."
keywords: [monorepo, turborepo, nx, typescript, ci, pnpm, estructura, directorios, configuracion, base, diseno, paquetes, compartidos, razon]
updated: 2026-07-27
status: current
---

# 🗂️ ESTÁNDAR DE MONOREPO (Turborepo)

## 🎯 ¿Qué es y cuándo usarlo?
Un **Monorepo** es un repositorio único que contiene múltiples proyectos relacionados (workers, frontend, paquetes compartidos). **Turborepo** es el orquestador de builds elegido porque: tiene caché de builds inteligente (no rebuildea lo que no cambió), escala a 100+ paquetes, es Zero-Config con TypeScript y se integra nativamente con Cloudflare Workers.

> **REGLA INQUEBRANTABLE:** Todo código compartido entre ≥ 2 proyectos (helpers de response, tipos TypeScript, schemas Zod) vive en un **paquete `packages/`** — NUNCA copiado entre proyectos. Copiar es crear deuda técnica garantizada. Ref: BACKEND_ENGINEERING_STANDARD.md §03 (módulo CORS compartido).

---

## 🏗️ 1. ESTRUCTURA DE DIRECTORIOS

```text
collabscribe/                     ← Raíz del monorepo
├── package.json                  ← workspaces: ["apps/*", "packages/*"]
├── turbo.json                    ← Configuración de pipelines
├── pnpm-workspace.yaml           ← pnpm workspaces
│
├── apps/                         ← Aplicaciones desplegables
│   ├── web/                      ← Frontend React (Cloudflare Pages)
│   ├── api-gateway/              ← Cloudflare Worker: punto de entrada
│   ├── auth-worker/              ← Cloudflare Worker: /api/auth/*
│   ├── docs-worker/              ← Cloudflare Worker: /api/documents/*
│   ├── teams-worker/             ← Cloudflare Worker: /api/teams/*
│   ├── notifs-worker/            ← Cloudflare Worker: /api/notifications/*
│   ├── search-worker/            ← Cloudflare Worker: /api/search/*
│   └── embeddings-worker/        ← Cloudflare Worker: Queue consumer
│
└── packages/                     ← Código compartido (nunca desplegado directamente)
    ├── shared-types/             ← Tipos TypeScript compartidos (Document, Team, User...)
    ├── shared-schemas/           ← Schemas Zod compartidos (validación frontend + backend)
    ├── shared-http/              ← Helpers: ok(), fail(), getCorsHeaders(), rateLimit()
    ├── shared-db/                ← Cliente Supabase + helpers de queries
    └── tsconfig/                 ← tsconfig.json base compartido
```

---

## ⚙️ 2. CONFIGURACIÓN BASE

### `turbo.json` (Pipelines)

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],     // Buildear dependencias antes que el proyecto
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "cache": false,              // Dev nunca se cachea
      "persistent": true
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "deploy": {
      "dependsOn": ["build", "test", "typecheck"],
      "outputs": []
    }
  }
}
```

### `pnpm-workspace.yaml`

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### `package.json` raíz

```json
{
  "name": "collabscribe",
  "private": true,
  "scripts": {
    "dev":       "turbo run dev",
    "build":     "turbo run build",
    "test":      "turbo run test",
    "lint":      "turbo run lint",
    "typecheck": "turbo run typecheck",
    "deploy":    "turbo run deploy"
  },
  "devDependencies": {
    "turbo":  "^2.0.0",
    "typescript": "^5.4.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

---

## 📦 3. PAQUETES COMPARTIDOS (El corazón del monorepo)

### `packages/shared-types` — Tipos TypeScript

```typescript
// packages/shared-types/src/index.ts
// Estos tipos son importados por el frontend Y por cada worker

export type MemberRole = 'owner' | 'admin' | 'editor' | 'viewer'
export type DocStatus = 'backlog' | 'draft' | 'review' | 'published' | 'archived'

export interface Team {
  id: string; name: string; slug: string
  created_at: string; updated_at: string
}

export interface Document {
  id: string; team_id: string; created_by: string
  title: string; content: string
  status: DocStatus; is_public: boolean
  created_at: string; updated_at: string
}

export interface TeamMember {
  team_id: string; user_id: string
  role: MemberRole; invited_at: string
}

// Respuesta envelope estándar del API (API_ENGINEERING_STANDARD.md §04)
export interface ApiResponse<T> {
  success: true; data: T
}
export interface ApiError {
  success: false; error: { code: string; message: string }
}
```

### `packages/shared-schemas` — Schemas Zod

```typescript
// packages/shared-schemas/src/documents.ts
import { z } from 'zod'

export const createDocumentSchema = z.object({
  team_id: z.string().uuid(),
  title:   z.string().min(1).max(500).trim(),
  content: z.string().max(5_000_000).default(''),
  status:  z.enum(['backlog', 'draft', 'review', 'published', 'archived']).default('draft')
})

export const updateDocumentSchema = createDocumentSchema.partial().omit({ team_id: true })

export type CreateDocumentInput = z.infer<typeof createDocumentSchema>
export type UpdateDocumentInput = z.infer<typeof updateDocumentSchema>
```

### `packages/shared-http` — Helpers de Response y CORS

```typescript
// packages/shared-http/src/response.ts
// Ref: BACKEND_ENGINEERING_STANDARD.md §01 — helper único, no repetido en cada worker

export function ok<T>(data: T, corsHeaders?: HeadersInit): Response {
  return new Response(JSON.stringify({ success: true, data }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', ...corsHeaders }
  })
}

export function fail(
  code: string,
  message: string,
  status: number,
  corsHeaders?: HeadersInit
): Response {
  return new Response(JSON.stringify({ success: false, error: { code, message } }), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders }
  })
}

// packages/shared-http/src/cors.ts
// Ref: BACKEND_ENGINEERING_STANDARD.md §03 — módulo compartido, NO copiado

const ALLOWED_ORIGINS: Record<string, string[]> = {
  production:  ['https://collabscribe.com', 'https://app.collabscribe.com'],
  staging:     ['https://staging.collabscribe.com'],
  development: ['http://localhost:3000', 'http://localhost:5173']
}

export function getCorsHeaders(environment: string, origin: string | null): HeadersInit {
  const allowed = ALLOWED_ORIGINS[environment] ?? []
  const isAllowed = origin && allowed.includes(origin)
  return {
    'Access-Control-Allow-Origin':  isAllowed ? origin : (allowed[0] ?? ''),
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age':       '86400'
  }
}
```

---

## 🚀 4. FLUJO DE DEPLOY EN CI (GitHub Actions)

Turborepo detecta qué apps cambiaron y solo despliega esas.

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v3
        with: { version: 9 }

      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }

      - run: pnpm install --frozen-lockfile

      # Turborepo Remote Cache (evita re-buildear lo que ya está cacheado en el servidor de CI)
      - name: Build
        run: pnpm turbo run build
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM:  ${{ secrets.TURBO_TEAM }}

      # Desplegar cada Worker independientemente
      - name: Deploy Workers
        run: pnpm turbo run deploy --filter="./apps/*-worker"
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}

      # Desplegar Frontend (Cloudflare Pages)
      - name: Deploy Frontend
        run: pnpm turbo run deploy --filter="./apps/web"
```

---

## 📋 CHECKLIST DE SETUP

- [ ] `pnpm` como package manager (no npm, no yarn — consistencia)
- [ ] `turbo.json` con pipeline `deploy` que depende de `build + test + typecheck`
- [ ] `packages/shared-http` importado por todos los workers (no copiado)
- [ ] `packages/shared-schemas` importado por frontend Y workers (single source of truth)
- [ ] `packages/shared-types` importado por todos (coherencia de contratos)
- [ ] Remote Cache de Turborepo configurado en CI (ahorra 5-10 min por deploy)
- [ ] Cada worker tiene su propio `wrangler.toml` con bindings específicos
- [ ] `.env.example` en la raíz con todas las variables necesarias documentadas
