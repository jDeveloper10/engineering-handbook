---
title: "Plantilla de README de Proyecto"
category: 12_Documentation
doc_type: referencia
tags: [documentation, plantilla, readme]
summary: "Plantilla de README para un proyecto o servicio: inicio rápido, contenido del repositorio, arquitectura breve, variables de entorno, testing y referencias."
keywords: [readme, plantilla, inicio-rapido, variables-entorno, testing]
updated: 2026-07-27
status: current
---

# [Nombre del Proyecto / Servicio]

> Descripción de una línea sobre qué hace este proyecto.

## Inicio Rápido

```bash
# Instalación de dependencias
npm install

# Correr en desarrollo
npm run dev
```

## Qué hay aquí

- **Stack:** [Ej. React, Vite, Tailwind, Cloudflare Workers]
- **Propósito:** [Explica en 2 párrafos para qué sirve y qué problema resuelve de negocio]

## Arquitectura (Breve)

*(Puedes incluir un diagrama Mermaid o enlace a `09_Architecture`)*
- `src/api`: Endpoints o Workers.
- `src/components`: UI components.

## Variables de Entorno (.env)

| Variable | Requerido | Descripción |
|----------|-----------|-------------|
| `API_URL` | Sí | URL del backend. |
| `DB_PASS` | Sí | Contraseña de Supabase. |

## Testing

```bash
npm run test
```

## Referencias
- Enlace a Figma
- Enlace al tablero de tareas (Jira/Linear)
