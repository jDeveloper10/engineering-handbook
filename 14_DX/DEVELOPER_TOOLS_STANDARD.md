---
title: "Estándar de Herramientas de Desarrollo y Productividad (DX Tools)"
category: 14_DX
doc_type: estandar
tags: [dx, cli, generators, eslint, hygen, plop, husky, devcontainer, vscode]
summary: "Estándar para herramientas de productividad de ingeniería: generadores de código (Plop/Hygen), reglas personalizadas de ESLint, snippets compartidos de VS Code, automatización con Husky y Dev Containers."
keywords: [dx, cli, generators, plop, hygen, eslint, husky, devcontainer, snippets, vscode]
updated: 2026-07-27
status: current
---

# ESTÁNDAR DE HERRAMIENTAS DE DESARROLLO Y PRODUCTIVIDAD

## OBJETIVO
Automatizar tareas repetitivas de desarrollo, garantizar entornos de trabajo 100% reproducibles y eliminar la fricción al crear nuevos componentes, módulos o Workers.

---

## REGLAS INQUEBRANTABLES

**[RECOMMENDED] DEV-001: Todo proyecto nuevo DEBE crearse mediante el script automatizado `new-project.ps1`.**

> **Por qué:** crear un proyecto a mano significa repetir manualmente decisiones ya tomadas (estructura, configuración, dependencias base), y cada repetición manual es una oportunidad de que diverja del resto de proyectos del handbook. Es recomendado porque incorporar un repositorio ya existente, que no pasó por el script, sigue siendo un caso legítimo y frecuente.

**[RECOMMENDED] DEV-002: Generadores de Código (Plop.js) para componentes y módulos.** NUNCA crear manualmente la estructura de carpetas de una feature.

> **Por qué:** crear a mano la estructura de una feature nueva es fácil de hacer de forma ligeramente distinta cada vez, y esa inconsistencia se acumula en el proyecto. Un generador la produce siempre igual. Es recomendado porque una feature con forma verdaderamente atípica no se beneficia de forzarla dentro de una plantilla genérica.

---

## 1. GENERADOR DE CÓDIGO CON PLOP.JS

```javascript
// plopfile.js - Generador de código para el Monorepo
export default function (plop) {
  plop.setGenerator('feature', {
    description: 'Crea una nueva feature con componentes, hooks y tests',
    prompts: [
      { type: 'input', name: 'name', message: 'Nombre de la feature (ej. document-editor):' }
    ],
    actions: [
      {
        type: 'add',
        path: 'src/features/{{kebabCase name}}/components/{{pascalCase name}}.tsx',
        templateFile: 'plop-templates/component.hbs'
      },
      {
        type: 'add',
        path: 'src/features/{{kebabCase name}}/hooks/use{{pascalCase name}}.ts',
        templateFile: 'plop-templates/hook.hbs'
      },
      {
        type: 'add',
        path: 'src/features/{{kebabCase name}}/tests/{{pascalCase name}}.test.tsx',
        templateFile: 'plop-templates/test.hbs'
      }
    ]
  })
}
```

---

## 2. DEV CONTAINER REPRODUCIBLE (`.devcontainer/devcontainer.json`)

```json
{
  "name": "SaaS Engineering DevContainer",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "tailwindlabs.tailwindcss",
        "eamodio.gitlens"
      ]
    }
  },
  "postCreateCommand": "pnpm install"
}
```

---

## CHECKLIST DE HERRAMIENTAS DX

- [ ] Generadores Plop/Hygen configurados para componentes y hooks.
- [ ] Configuración `.vscode/settings.json` y `extensions.json` en el repositorio.
- [ ] DevContainer activo para desarrollo en entornos aislados.
- [ ] Script de automatización de creación de proyectos operativo.
