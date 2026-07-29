# 10 — Cloudflare Standards

> Cloudflare es la plataforma por defecto del ecosistema (Pages, Workers, KV, R2). Reglas de uso
> operativo. Lo técnico (código de Workers, límites de plataforma, costos) vive en el handbook
> `08_Cloud`.
>
> **Ver también:** [`CLOUDFLARE_PLATFORM_STANDARD.md`](../08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md)
> — matriz de almacenamiento, límites, costos, WAF, D1, KV, R2, Queues, DO (números verificados
> 2026-07-20).
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Para decidir QUÉ servicio de Cloudflare usar (KV vs D1 vs R2 vs Supabase vs
>   Queues): consultar la matriz de `CLOUDFLARE_PLATFORM_STANDARD.md` sección 01 (matriz de
>   almacenamiento) y secciones 02-04 (detalle de Workers, KV, R2). Este archivo no contiene
>   esa información — contiene cómo se opera el servicio ya elegido.

## Pages (frontend)

- **[REQUIRED]** Todo frontend en producción se conecta por Git → deploy automático en push a
  `main` (patrón jcdigital). Prohibido subir `dist/` a mano.
- **[REQUIRED]** Variables `VITE_*` se configuran en el dashboard de Pages Y se documentan en
  `.env.example`. Cambiar una variable requiere redeploy (lección real: commit "chore: trigger
  rebuild to pick up VITE_PAYMENT_WORKER_URL" — ese ciclo se evita documentando la variable ANTES
  del primer deploy).

## Workers

- **[REQUIRED]** Deploy objetivo: GitHub Actions con `wrangler-action` en push (roadmap P0).
  Mientras no exista: `npx wrangler deploy` manual está permitido SOLO tras pasar el checklist
  pre-deploy de [25-Checklists.md](25-Checklists.md) §5.
- **[REQUIRED]** Almacenamiento: KV para estado pequeño (órdenes, sesiones — patrón worker-pago),
  R2 para archivos (productos vendidos), D1/Supabase para relacional. No usar KV como base de
  datos relacional.
- **[RECOMMENDED]** Un `wrangler.jsonc` por worker, con `compatibility_date` actualizada al crear
  el worker y congelada hasta que se pruebe una nueva.

## Costos

- **[RECOMMENDED]** Todo en plan free mientras sea posible; el primer servicio que exija plan de
  pago se registra en [24-Metrics.md](24-Metrics.md) (costo mensual) y en 21-Business.md (a qué
  ingreso se asocia).
