---
title: "Estándar de Monorepo"
category: 09_Architecture
doc_type: estandar
tags: [monorepo, pnpm, turborepo, workspace, arquitectura]
summary: "Estándar del dominio Arquitectura para monorepos: estructura, workspaces, dependencias, scripts y deployment."
keywords: [monorepo, pnpm, workspace, turborepo, arquitectura, packages]
updated: 2026-08-30
status: current
---

# MONOREPO ENGINEERING STANDARD

> **Stack de referencia:** pnpm workspaces + Turborepo (opcional)
> **Depende de:** ARCHITECTURE_STANDARD.md
> **Aplica a:** Todo proyecto con múltiples paquetes/apps en un solo repo

---

## 01. Estructura

### 1.1 Estructura de carpetas

**[REQUIRED]** Monorepo con apps/ y packages/:

```
mi-monorepo/
├── apps/
│   ├── web/                    # Frontend principal
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── mobile/                 # App móvil (Expo/React Native)
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                    # Backend (Worker/Express)
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── shared/                 # Tipos, utils compartidos
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── ui/                     # Componentes UI compartidos
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── contracts/              # Schemas Zod compartidos
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── package.json                # Root
├── pnpm-workspace.yaml
├── tsconfig.json               # Base tsconfig
└── turbo.json                  # (Opcional) Turborepo config
```

### 1.2 pnpm-workspace.yaml

**[REQUIRED]** Definir workspaces:

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

### 1.3 package.json root

**[REQUIRED]** Scripts en el root:

```json
{
  "name": "mi-monorepo",
  "private": true,
  "scripts": {
    "dev": "pnpm --parallel -r run dev",
    "dev:web": "pnpm --filter @mi/web dev",
    "dev:api": "pnpm --filter @mi/api dev",
    "build": "pnpm --parallel -r run build",
    "build:web": "pnpm --filter @mi/web build",
    "lint": "pnpm --parallel -r run lint",
    "typecheck": "pnpm --parallel -r run typecheck",
    "test": "pnpm --parallel -r run test",
    "clean": "pnpm --parallel -r run clean"
  },
  "devDependencies": {
    "typescript": "^5.8.3"
  }
}
```

---

## 02. Dependencias

### 2.1 Dependencias compartidas en root

**[REQUIRED]** Dependencias de desarrollo compartidas viven en root:

```json
// package.json root
{
  "devDependencies": {
    "typescript": "^5.8.3",
    "eslint": "^9.0.0",
    "prettier": "^3.0.0"
  }
}
```

### 2.2 Dependencias de app en su package.json

**[REQUIRED]** Cada app declara sus dependencias:

```json
// apps/web/package.json
{
  "name": "@mi/web",
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@mi/ui": "workspace:*",
    "@mi/contracts": "workspace:*"
  }
}
```

### 2.3 Paquetes internos con "workspace:*"

**[REQUIRED]** Referenciar paquetes internos con `workspace:*`:

```json
// apps/web/package.json
{
  "dependencies": {
    "@mi/shared": "workspace:*",   // ← Referencia interna
    "react": "^19.0.0"             // ← Dependencia externa
  }
}
```

---

## 03. TypeScript

### 3.1 tsconfig base compartido

**[REQUIRED]** tsconfig.json en root con config compartida:

```jsonc
// tsconfig.json root
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  }
}
```

### 3.2 Herencia de tsconfig

**[REQUIRED]** Cada app hereda del root:

```jsonc
// apps/web/tsconfig.json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@mi/ui": ["../../packages/ui/src"],
      "@mi/shared": ["../../packages/shared/src"]
    }
  },
  "include": ["src"]
}
```

---

## 04. Paquetes Internos

### 4.1 Paquete shared

**[REQUIRED]** Utils y tipos compartidos:

```typescript
// packages/shared/src/index.ts
export * from './types';
export * from './utils';
export * from './constants';
```

### 4.2 Paquete ui

**[REQUIRED]** Componentes UI compartidos:

```typescript
// packages/ui/src/index.ts
export { Button } from './Button';
export { Card } from './Card';
export { Input } from './Input';
```

### 4.3 Paquete contracts

**[REQUIRED]** Schemas Zod compartidos frontend↔backend:

```typescript
// packages/contracts/src/orders.ts
import { z } from 'zod';

export const CreateOrderSchema = z.object({
  productId: z.string().uuid(),
  quantity: z.number().int().min(1).max(100),
  notes: z.string().max(500).optional(),
});

export type CreateOrder = z.infer<typeof CreateOrderSchema>;
```

---

## 05. Scripts

### 5.1 Scripts por paquete

**[REQUIRED]** Cada paquete tiene scripts mínimos:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint src/",
    "typecheck": "tsc --noEmit",
    "test": "vitest"
  }
}
```

### 5.2 Scripts de filtrado

**[REQUIRED]** Usar `pnpm --filter` para ejecutar en paquetes específicos:

```bash
# Desarrollar solo web
pnpm --filter @mi/web dev

# Build solo api
pnpm --filter @mi/api build

# Typecheck todos
pnpm --parallel -r run typecheck
```

---

## 06. Deployment

### 6.1 Deploy independiente

**[REQUIRED]** Cada app se despliega independientemente:

```json
// apps/web/package.json
{
  "scripts": {
    "deploy": "wrangler pages deploy dist --project-name mi-web"
  }
}

// apps/api/package.json
{
  "scripts": {
    "deploy": "wrangler deploy"
  }
}
```

### 6.2 CI/CD por paquete

**[REQUIRED]** GitHub Actions por paquete:

```yaml
# .github/workflows/web.yml
name: Deploy Web
on:
  push:
    paths: ['apps/web/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - run: pnpm install
      - run: pnpm --filter @mi/web build
      - run: pnpm --filter @mi/web deploy
```

---

## Checklist Monorepo

- [ ] pnpm-workspace.yaml configurado
- [ ] Estructura apps/ y packages/
- [ ] tsconfig base compartido
- [ ] Dependencias compartidas en root
- [ ] Paquetes internos con workspace:*
- [ ] Scripts de filtrado configurados
- [ ] CI/CD por paquete
- [ ] Paquetes shared, ui, contracts
