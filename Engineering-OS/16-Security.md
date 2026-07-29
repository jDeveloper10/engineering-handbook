# 16 — Security

> Reglas de seguridad operativas + seguimiento de hallazgos abiertos. Las reglas técnicas
> detalladas (amenazas, hardening, incident response, OWASP top 10) viven en el handbook
> `05_Security`. Este archivo contiene las reglas que la auditoría real de 2026-07-20 demostró
> necesarias para este ecosistema específico, más el tracker de hallazgos abiertos (S1-S9).
>
> **Ver también:**
> - [`SECURITY_ENGINEERING_STANDARD.md`](../05_Security/SECURITY_ENGINEERING_STANDARD.md) — reglas
>   técnicas detalladas (auth, RLS, rate limiting, CORS, webhooks, secretos)
> - [`THREAT_MODEL.md`](../05_Security/THREAT_MODEL.md) — 8 amenazas reales del ecosistema
> - [`INCIDENT_RESPONSE.md`](../05_Security/INCIDENT_RESPONSE.md) — runbook de la primera hora
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Las reglas técnicas de seguridad (CORS, webhooks, RLS, secretos) se definen
>   en `SECURITY_ENGINEERING_STANDARD.md`. Este archivo las refuerza con contexto operativo
>   (los hallazgos S1-S9 como evidencia de por qué existen). Si hay contradicción, gana el
>   handbook `05_Security`.
> - **[REQUIRED]** El tracker de hallazgos (tabla S1-S9) es responsabilidad operativa de este
>   archivo — los hallazgos se actualizan aquí cuando se cierran. Pero la regla técnica que
>   previene cada hallazgo se documenta en el estándar de seguridad, no solo aquí.

## Reglas (las que la auditoría demostró necesarias)

- **[REQUIRED] `.gitignore` con `.env*` y `.dev.vars` en TODO repo.** No `.env` a secas: el
  crítico #1 se coló porque el ignore no cubría `.env.local`.
- **[REQUIRED] Clave commiteada = clave quemada.** Se rota PRIMERO, se limpia el historial después
  (BFG/filter-repo). El orden inverso da falsa seguridad.
- **[REQUIRED] Supabase: prohibido `with check (true)` y políticas `for all using(true)`** fuera
  de una rama de desarrollo. Toda policy de INSERT lleva su `with check` explícito de ownership.
  (Origen: escalación a admin posible en JeilinOrganizacion.)
- **[REQUIRED] Firestore: deny-by-default al final** (`match /{document=**} { allow read, write: if false; }`).
  El patrón correcto YA existe en Planilla/DeliveryApp/jonnyTrader — copiarlo, no reinventarlo.
- **[REQUIRED] Webhooks de pago: firma verificada con comparación constant-time** — patrón
  canónico: `worker-pago/src/webhook.ts` (timingSafeEqual). Nada de `===` sobre HMACs.
- **[REQUIRED] CORS en workers: allowlist explícita** (patrón worker-pago), nunca `*` en endpoints
  con datos o dinero.
- **[REQUIRED] Antes de `git init` en carpeta vieja: revisar qué hay** — el crítico #2 eran .env
  stageados a un commit de quedar en la historia.
- **[RECOMMENDED]** Reusar `E:\auditory` (auditor propio) como segundo barrido trimestral.

## Hallazgos abiertos (2026-07-20) — actualizar estado al cerrar

| # | Sev | Hallazgo | Acción | Estado |
|---|---|---|---|---|
| S1 | 🔴 | `webtradingpro/.env.local` commiteado con CTRADER_CLIENT_SECRET, ALPHA_VANTAGE_API_KEY, DERIV_API_TOKEN | Rotar las 3 claves HOY → purgar historial → `.gitignore` a `.env*` | ABIERTO |
| S2 | 🔴 | `IA-compilation`: `backendamazon.env`/`frontrndenviroment.env` stageados (DB_PASSWORD, AUTH_SECRET, BING_KEY) | `git reset HEAD` de ambos → `.gitignore` → rotar si hubo push | ABIERTO |
| S3 | 🔴 | `JeilinOrganizacion/supabase_admins.sql`: cualquier usuario autenticado puede insertarse como admin (`with check(true)` en `for all`) | Policy de INSERT explícita con check de admin | ABIERTO |
| S4 | 🔴 | `JeilinOrganizacion/supabase_schema.sql`: `anon` con acceso total a clientes/proyectos/cobros/tareas/ideas | Políticas por `auth.uid()` antes de cualquier exposición | ABIERTO |
| S5 | 🟠 | `IA-compilation/firestore.rules`: catch-all `read: true` + write autenticado global | Deny-by-default (copiar patrón Planilla) | ABIERTO |
| S6 | 🟡 | `.gitignore` sin `.dev.vars`/`.env*` en ~17 repos | Lote de IA básica (1 comando por repo) | ABIERTO |
| S7 | 🟡 | `ingenusfx/payments-worker`: firma NOWPayments con `===` (no constant-time) | Copiar timingSafeEqual de worker-pago | ABIERTO |
| S8 | 🟡 | `IA-compilation/storage.rules`: escritura cruzada en `/images/{imageId}` | Limitar a carpeta del usuario | ABIERTO |
| S9 | 🟡 | `mcps/mcp-jcdigital/.env` con TELEGRAM_TOKEN real, carpeta sin git NI .gitignore preparado | Crear .gitignore ANTES de cualquier git init | ABIERTO |

**Fortalezas confirmadas (mantener como patrón):** worker-pago (CORS+firma+secrets) ·
workers-template (secrets documentados sin valores) · Firestore rules de Planilla/DeliveryApp/
torneoProgramacion/jonnyTrader.

**Security Score baseline** (fórmula 24-Metrics): 100 − (4×20 + 1×10 + 4×3) = **0 (piso)** →
objetivo 30 días: cerrar S1-S5 = 88.
