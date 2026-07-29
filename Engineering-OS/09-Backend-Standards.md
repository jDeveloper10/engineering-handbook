# 09 — Backend Standards (capa operativa)

> Autoridad técnica: `E:\ENGINEERING_HANDBOOK\02_Backend\BACKEND_ENGINEERING_STANDARD.md`
> (fundado en el código real de workers-template). Este archivo define solo el uso operativo — no
> repite reglas técnicas de implementación.
>
> **Ver también:** [`BACKEND_ENGINEERING_STANDARD.md`](../02_Backend/BACKEND_ENGINEERING_STANDARD.md)
> para reglas técnicas (capas, validación, handlers, servicios);
> [`API_ENGINEERING_STANDARD.md`](../03_API/API_ENGINEERING_STANDARD.md) para el contrato de API.

## Reglas operativas

- **[REQUIRED]** Backend nuevo = Cloudflare Worker desde `workers-template` (admin, auth,
  payments, trading, communications, user + Pages Functions). Elegir el worker cuyo dominio
  corresponda y adaptarlo. Express/VPS solo si Workers no puede (procesos largos, binarios) — y
  eso pasa por la matriz de adopción de [05-Decision-Matrix.md](05-Decision-Matrix.md).
- **[REQUIRED]** Todo endpoint devuelve el formato `{ success, data | error }` (patrón ya usado en
  worker-pago y el template — no inventar formatos nuevos por proyecto).
- **[REQUIRED]** Todo worker que maneja dinero o auth: validación de firma en webhooks, CORS con
  lista de orígenes explícita, rate limiting básico. Ver [16-Security.md](16-Security.md).
- **[REQUIRED]** Variables de entorno: `.dev.vars` local (gitignored) + `wrangler secret put` en
  producción. Nunca en `wrangler.toml/jsonc`.
- **[RECOMMENDED]** Node/Express existente (N8N_SERVER, whatsapp-notifier, academy-exit-survey) se
  mantiene donde está; al tocarlo, evaluar migración a Worker o a n8n con la matriz — no migrar
  por deporte.
