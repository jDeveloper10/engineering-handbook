---
title: "Debugging Toolkit"
category: 11_Debugging
tags: [tools, devtools, debugging]
status: current
---

# 🛠️ Debugging Toolkit

Manual rápido para diagnosticar y depurar la aplicación usando el set correcto de herramientas antes de recurrir a cambiar código "para ver si funciona".

## 1. Frontend (React / Navegador)

- **React Developer Tools**: Úsalo para identificar componentes que se renderizan innecesariamente (activa la opción *"Highlight updates when components render"*).
- **Chrome Network Tab**: Tu mejor amigo. Antes de asumir un bug en React, verifica el Network Tab. ¿La petición API salió? ¿Qué status HTTP volvió? ¿El JSON de respuesta está bien formado?
- **Preserve Log**: Activa "Preserve Log" en la consola del navegador al depurar redirecciones. Evitará que el error desaparezca al cambiar de página.

## 2. Backend / Edge (Cloudflare Workers)

- **Wrangler Tail**: `npx wrangler tail`. Usa este comando para ver los logs `console.log()` en vivo de tu Worker en producción.
- **Local Dev Server**: Inicia el backend local con `npm run dev` (wrangler dev) para capturar los logs directamente en la consola antes del deploy.

## 3. Base de Datos (Supabase / Postgres)

- **Supabase Dashboard**: Usa el tab "SQL Editor" para correr el query problemático aislado del backend y medir su velocidad.
- **Explain Analyze**: Si un query es lento, escribe `EXPLAIN ANALYZE` antes de la consulta. Postgres te devolverá el plan de ejecución y te dirá si hizo un *Sequential Scan* (lento) o usó un índice (rápido).
