---
title: "Estándar de Documentación de Proyectos y APIs"
category: 12_Documentation
doc_type: estandar
tags: [documentation, claude-md, openapi, swagger, changelog, readme, typedoc, storybook]
summary: "Estándar integral de documentación para código, APIs y repositorios: plantilla CLAUDE.md / AGENTS.md por proyecto, generación automática de OpenAPI 3.1 con Hono + Zod, TypeDoc, Storybook, plantillas de CHANGELOG y README."
keywords: [documentation, claude.md, agents.md, openapi, swagger, hono, typedoc, storybook, changelog, semver, readme]
updated: 2026-07-27
status: current
---

# 📚 ESTÁNDAR DE DOCUMENTACIÓN DE PROYECTOS Y APIS

> **Objetivo:** Garantizar que todo repositorio y API del ecosistema sea auto-documentado, comprensible para desarrolladores humanos e interprete sin ambigüedad por agentes de IA.

---

## 🎯 LAS 5 REGLAS INQUEBRANTABLES DE DOCUMENTACIÓN

1. **[REQUIRED] Todo repositorio DEBE incluir un `CLAUDE.md` o `AGENTS.md` en la raíz.** Es el mapa de contexto primario para IAs.
2. **[REQUIRED] Toda API expuesta DEBE generar su especificación OpenAPI 3.1 automáticamente.** Cero especificaciones escritas a mano que se desactualizan.
3. **[REQUIRED] El código es auto-descriptivo por defecto.** Los comentarios documentan el *por qué* (why), nunca el *qué* (what).
4. **[REQUIRED] Las versiones y cambios siguen SemVer y Keep a Changelog.** Todo release documenta sus novedades en `CHANGELOG.md`.
5. **[REQUIRED] Las funciones y utilidades compartidas llevan bloques TSDoc.**

---

## 🤖 1. ESTÁNDAR CLAUDE.MD / AGENTS.MD POR REPOSITORIO

**[REQUIRED]** Todo repositorio del portafolio DEBE contener un archivo `CLAUDE.md` en la raíz. Este archivo proporciona el contexto técnico inmediato para asistentes de IA y desarrolladores.

```markdown
# CLAUDE.md — Contexto de Ingeniería para IA

## 🛠️ Stack Tecnológico
- **Frontend**: React + TypeScript + TailwindCSS + shadcn/ui
- **Backend**: Cloudflare Workers (patrón Multi-Worker)
- **Base de datos**: Supabase (PostgreSQL) + D1
- **Monorepo**: Turborepo + pnpm workspaces
- **Testing**: Vitest + Playwright

## 📁 Estructura del Repositorio
apps/
├── web/              # App Frontend React (Cloudflare Pages)
├── api-gateway/      # Worker API Gateway principal
├── docs-worker/      # Worker de gestión de documentos
└── notif-worker/     # Worker de envío de notificaciones (Email/Push)
packages/
├── shared-types/     # Tipos de TypeScript compartidos
├── shared-schemas/   # Schemas de Zod (Frontend + Backend)
└── shared-http/      # Helpers HTTP: ok(), fail(), getCorsHeaders()

## ⚡ Comandos Principales
- `pnpm dev`          # Inicia todos los proyectos en desarrollo
- `pnpm build`        # Compila todas las apps y paquetes
- `pnpm check`        # Ejecuta linting + typecheck + tests (pre-push)
- `pnpm test`         # Tests unitarios e integración con Vitest
- `pnpm test:e2e`     # Tests E2E con Playwright

## 📐 Reglas del Proyecto (Sin Excepciones)
- **NUNCA** usar `any` en TypeScript. Usar `unknown` y estrechar con Zod.
- **NUNCA** usar `export default` en utilidades o componentes (solo en handlers de Workers/Pages).
- **SIEMPRE** implementar 4 estados en componentes async (Loading, Empty, Error, Success).
- **SIEMPRE** usar React Query para data fetching en el frontend.
- **SIEMPRE** validar datos de entrada en el backend con Zod.
- **NUNCA** escribir `SELECT *` en la base de datos (especificar columnas).

## 📚 Documentación Relacionada
- **Engineering Handbook**: `../ENGINEERING_HANDBOOK/AGENTS.md`
- **API Swagger**: `http://localhost:8787/api/docs`
```

---

## 🌐 2. ESTÁNDAR OPENAPI 3.1 Y SWAGGER (APIs)

**[REQUIRED]** Todas las APIs desarrolladas en Cloudflare Workers deben autogenerar la especificación **OpenAPI 3.1** a partir de tipos y validaciones de Zod usando `Hono` o `@hono/zod-openapi`. Queda prohibido mantener JSON/YAML de OpenAPI manualmente.

```typescript
// apps/docs-worker/src/index.ts
import { OpenAPIHono, createRoute, z } from '@hono/zod-openapi'
import { swaggerUI } from '@hono/swagger-ui'

const app = new OpenAPIHono()

// Schema de respuesta estándar (API_ENGINEERING_STANDARD.md)
const UserSchema = z.object({
  id: z.string().uuid().openapi({ example: '123e4567-e89b-12d3-a456-426614174000' }),
  email: z.string().email().openapi({ example: 'usuario@collabscribe.com' }),
  name: z.string().openapi({ example: 'Ana García' }),
  created_at: z.string().datetime()
})

// Definición de Ruta con OpenAPI
const getUsersRoute = createRoute({
  method: 'get',
  path: '/api/v1/users',
  tags: ['Usuarios'],
  summary: 'Listar usuarios del equipo',
  description: 'Retorna una lista paginada de usuarios pertenecientes al equipo autenticado.',
  security: [{ bearerAuth: [] }],
  request: {
    query: z.object({
      cursor: z.string().optional().openapi({ description: 'ISO timestamp del último registro' }),
      limit: z.coerce.number().min(1).max(100).default(20).openapi({ description: 'Cantidad de registros' })
    })
  },
  responses: {
    200: {
      description: 'Lista de usuarios recuperada exitosamente',
      content: {
        'application/json': {
          schema: z.object({
            success: z.boolean().openapi({ example: true }),
            data: z.object({
              items: z.array(UserSchema),
              nextCursor: z.string().nullable(),
              hasMore: z.boolean()
            })
          })
        }
      }
    },
    401: { description: 'Token de autenticación faltante o inválido' },
    429: { description: 'Límite de peticiones superado (Rate Limit)' }
  }
})

// Implementación del handler
app.openapi(getUsersRoute, async (c) => {
  const { cursor, limit } = c.req.valid('query')
  // Lógica de obtención de datos...
  return c.json({
    success: true,
    data: { items: [], nextCursor: null, hasMore: false }
  }, 200)
})

// Endpoints de Documentación Auto-generados
app.doc('/api/docs/json', {
  openapi: '3.1.0',
  info: {
    title: 'CollabScribe API',
    version: '1.0.0',
    description: 'Documentación oficial auto-generada para la API de CollabScribe'
  }
})

// Swagger UI accesible en navegador
app.get('/api/docs', swaggerUI({ url: '/api/docs/json' }))

export default app
```

---

## ⚙️ 3. GENERACIÓN AUTOMÁTICA DE DOCUMENTACIÓN

El pipeline de documentación se ejecuta de forma automática en CI/CD:

```
TypeScript (TSDoc) ──→ TypeDoc     ──→ Publica HTML en Cloudflare Pages (/docs/code)
Componentes React  ──→ Storybook   ──→ Publica Catálogo de UI (/docs/components)
Workers / Routes   ──→ OpenAPI/Zod ──→ Swagger UI (/api/docs)
```

### 3.1 TypeDoc para paquetes y utilidades TypeScript
```json
// package.json
{
  "scripts": {
    "docs:code": "typedoc --out docs/code src/index.ts"
  }
}
```

### 3.2 Workflow de GitHub Actions para Documentación
```yaml
# .github/workflows/docs.yml
name: Deploy Documentation
on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: pnpm }
      
      - run: pnpm install --frozen-lockfile
      - run: pnpm run docs:code
      
      - name: Deploy a Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: 'collabscribe-docs'
          directory: 'docs/code'
```

---

## 📜 4. TEMPLATE DE CHANGELOG.MD

**[REQUIRED]** Todo proyecto mantendrá un `CHANGELOG.md` estructurado según [Keep a Changelog](https://keepachangelog.com/) y siguiendo [SemVer](https://semver.org/).

```markdown
# Changelog — CollabScribe

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]
### Added
- Colaboración de texto en tiempo real con Yjs y CRDTs.

## [1.2.0] — 2026-07-25
### Added
- Autenticación multifactor con TOTP y Passkeys (`AUTH_MFA_STANDARD.md`).
- Búsqueda semántica con vectores (`pgvector`) en el backend.

### Changed
- Migración de API Gateway a arquitectura de Service Bindings sin latencia.
- Optimización de consultas D1 reduciendo lecturas en un 40%.

### Fixed
- Corrección de bug en re-ordenamiento optimista de tableros Kanban.

### Security
- Implementación de firmas estrictas en webhooks de Stripe y protección anti-replay.

## [1.1.0] — 2026-06-10
### Added
- Editor de texto enriquecido con TipTap.
- Exportación de documentos a PDF en el Edge.

## [1.0.0] — 2026-05-01
### Added
- Release inicial de la plataforma CollabScribe.
```

---

## 📑 5. TEMPLATE DE README.MD POR REPOSITORIO

**[REQUIRED]** Estructura obligatoria para el `README.md` de todo repositorio:

```markdown
# 🚀 Nombre del Proyecto

> Descripción corta en una sola línea sobre qué hace este proyecto.

[![Build Status](https://img.shields.io/github/actions/workflow/status/JCDIGITALL/proyecto/ci.yml?branch=main)](https://github.com/JCDIGITALL/proyecto/actions)
[![Coverage](https://img.shields.io/codecov/c/github/JCDIGITALL/proyecto)](https://codecov.io/gh/JCDIGITALL/proyecto)
[![License](https://img.shields.io/github/license/JCDIGITALL/proyecto)](LICENSE)

## 🛠️ Stack Tecnológico
- **Frontend**: React, TypeScript, TailwindCSS
- **Backend**: Cloudflare Workers
- **DB**: Supabase PostgreSQL

## 📋 Requisitos Previos
- Node.js >= 20.0.0
- pnpm >= 9.0.0
- Wrangler CLI (`npm i -g wrangler`)

## ⚡ Instalación y Setup Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/JCDIGITALL/proyecto.git
cd proyecto

# 2. Instalar dependencias
pnpm install

# 3. Copiar variables de entorno
cp .env.example .env

# 4. Iniciar entorno de desarrollo
pnpm dev
```

## 📜 Scripts Disponibles

| Comando | Descripción |
|---|---|
| `pnpm dev` | Inicia servidor de desarrollo local |
| `pnpm build` | Compila el proyecto para producción |
| `pnpm check` | Corre linters, typecheck y tests unitarios |
| `pnpm test` | Ejecuta la suite de pruebas unitarias |

## 📁 Estructura del Código

```text
src/
├── components/     # Componentes de UI reutilizables
├── features/       # Módulos organizados por funcionalidad de negocio
├── hooks/          # Hooks personalizados de React
├── lib/            # Clientes de API, utilidades y helpers
└── index.ts        # Punto de entrada principal
```

## 🤝 Contribución y Estándares
Por favor revisa el [Engineering Handbook](../ENGINEERING_HANDBOOK/AGENTS.md) antes de enviar un Pull Request.

## 📄 Licencia
Este proyecto está bajo la Licencia MIT.
```
