# 28 — Knowledge Base

> Memoria permanente del ecosistema: decisiones, lecciones, errores resueltos e inventario vivo.
> Se escribe con entradas cortas y fechadas. Las IAs consultan aquí ANTES de re-investigar o
> re-recomendar. Formato de entrada: `[fecha] [tipo] título — 2-6 líneas + fuente`.

## Decisiones vigentes (mini-ADRs)

- **[2026-07-20][decisión] jcdigital se queda en JSX** — el rediseño premium se hizo manteniendo
  JSX; migrar a TS es tarea separada, no mezclada con features. Fuente: sesión de rediseño.
- **[2026-07-20][decisión] E:\ = archivo, C:\trabajo = activo** — resuelve la duplicación de
  árboles `Trabajo`. Fuente: 07-Project-Structure.
- **[2026-07-20][decisión] Firebase congelado** — solo legacy; todo lo nuevo Supabase/Cloudflare.
  Fuente: stack canónico del handbook + 12-Firebase-Standards.

## Lecciones de producción

- **[2026-07][lección] Variables VITE_* requieren redeploy** — commit real "chore: trigger rebuild
  to pick up VITE_PAYMENT_WORKER_URL". Prevención: documentar variables ANTES del primer deploy
  (checklist §5).
- **[2026-07][lección] Wompi redirige con SU transactionId, no nuestro orderId** — el polling de
  /tienda/gracias resuelve por `by-transaction`. No "simplificar" ese endpoint. Fuente:
  OrderStatus.jsx.
- **[2026-07][lección] Las herramientas se abandonan sin fricción de uso** — MCP jcdigital quedó
  con un proyecto de ejemplo desde 2026-05. Prevención: registrar proyectos es paso 1 del workflow
  y parte de A1.

## Inventario vivo (estado migración Firebase — regla de 12-Firebase)

| Proyecto | Estado |
|---|---|
| tradingpropanel.web.app · ia-post.web.app · pwagastos.web.app · ingenius web.app | `activo-firebase` |
| jcdigital.online | `migrado` (Pages; quedan firebase.json/.firebaserc por borrar) |
| jonnyTrader | `híbrido` (Firestore+Supabase) — congelar Firebase, migrar por módulos |

## Errores conocidos y su causa raíz

- **[2026-07][error] uñapp: git corrupto con 32 cambios atrapados** — pendiente rescate
  (`git fsck`/re-init preservando working tree). No tocar el working tree hasta respaldarlo en zip.
- **[2026-07][error] Preview/screenshot congelado en panel oculto** — pestañas ocultas pausan rAF;
  las animaciones y capturas requieren panel visible. No es bug del sitio.

## Reglas

- **[REQUIRED]** Error de producción resuelto → entrada aquí (o T9 completo si tuvo impacto) en la
  misma sesión. El mismo error 2 veces = falta test/automatización (17-Testing).
- **[REQUIRED]** Decisión que sobrevive a la conversación → entrada aquí o en el CLAUDE.md del
  proyecto. Lo que no se registra, se re-discute — y eso es desperdicio (detector 4).
- **[RECOMMENDED]** Poda trimestral por el Knowledge-Agent: entradas obsoletas se marcan
  `[superada por X]`, no se borran.
