---
title: "Worker Template (Implementación de Referencia)"
category: 02_Backend
tags: [backend, template, workers, referencia]
summary: "Implementación de referencia que cumple todos los puntos del estándar de backend: arquitectura de carpetas, comandos disponibles y configuración inicial."
keywords: [template, worker, referencia, arquitectura, comandos, setup]
updated: 2026-07-10
status: current
---

# Worker Template (Reference Implementation)

Este proyecto es una implementación de referencia (`template`) que cumple con todos los puntos exigidos en el `BACKEND_ENGINEERING_STANDARD.md`. 

**No debes poner código en producción que no cumpla con esta base.**

## Arquitectura

- **Router (`src/index.ts`)**: Recibe el request de Cloudflare, verifica variables de entorno y despacha al handler correspondiente.
- **Middleware (`src/middleware/`)**: Autenticación reutilizable (`auth.ts`) y CORS centralizado (`cors.ts`).
- **Handlers (`src/handlers/`)**: Deserializan el request HTTP, validan los datos (Zod), y llaman a los Services.
- **Services (`src/services/`)**: Lógica de negocio e interacciones con Supabase. Independientes de HTTP.
- **Lib (`src/lib/`)**: Utilidades transversales como `logger.ts`, `env.ts` y el helper obligatorio `response.ts`.

## Comandos

```bash
# Instalar dependencias
npm install

# Iniciar servidor local
npm run dev

# Desplegar
npm run deploy
```

## Configuración Inicial

1. **Variables de entorno (Desarrollo)**: 
   Crea un archivo `.dev.vars` con:
   ```env
   SUPABASE_URL="https://your-project.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY="tu-clave-secreta-service-role"
   ```

2. **Secretos (Producción)**:
   ```bash
   wrangler secret put SUPABASE_SERVICE_ROLE_KEY
   ```
   *Nota: Nunca pongas secretos reales en el `wrangler.toml`.*
