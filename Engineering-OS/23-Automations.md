# 23 — Automations

> Registro vivo de la pregunta obsesiva del Automation-Agent: **"¿qué hace Jeilin repetidamente?"**
> Cada repetición detectada entra aquí con formato de decisión y muere convertida en script, skill,
> flujo n8n o GitHub Action. Estado: `propuesta` → `en construcción` → `activa` → (si nadie la usa
> 30 días) `retirada`.

## Cola priorizada (2026-07, derivada de la auditoría)

### A1 — Crear proyecto nuevo en un comando · **P0 · propuesta**
- **Problema:** ~95 proyectos con estructura inconsistente: 46% sin git, ~50% sin README, 0 con
  CLAUDE.md, 0 con CI. Cada proyecto se configuró a mano, distinto.
- **Solución:** script `new-project.ps1 <nombre> <categoria>` que: crea carpeta en la ruta
  canónica (07-Project-Structure) → clona plantilla (Vite+TS+Tailwind o workers-template) →
  genera README/CLAUDE.md/.env.example/ci.yml desde [26-Templates.md](26-Templates.md) →
  `git init` + crea repo en GitHub (`gh repo create JCDIGITALL/<nombre> --private`) + push →
  registra el proyecto en el MCP jcdigital.
- **Esfuerzo:** S (2-4h) · **Horas ahorradas:** ~2h por proyecto nuevo, ~4-6/mes.
- **Medición:** próximo proyecto nuevo nace 100% conforme en <10 min.

### A2 — CI/CD en repos activos · **P0 · propuesta**
- **Problema:** deploy de workers manual y de memoria; build nunca validado antes de push.
- **Solución:** `ci.yml` estándar (build + deploy worker con wrangler-action) instalado por IA
  básica en los ~10 repos activos, empezando por JCDigital/worker-pago.
- **Esfuerzo:** S por repo · **Horas ahorradas:** ~1h/semana + elimina la clase entera de errores
  "olvidé desplegar el worker".
- **Medición:** push a main = worker desplegado sin intervención, 2 semanas sin deploy manual.

### A3 — Guardián de fin de día (commits) · **P1 · propuesta**
- **Problema:** 37/34/32/16/14 archivos sin commitear en 5 repos; ráfagas de meses.
- **Solución:** tarea programada (Windows Task Scheduler o n8n) que a las 20:00 recorre los repos
  activos, y si hay cambios sin commitear manda aviso por WhatsApp (Baileys) o Telegram (el MCP
  jcdigital ya tiene `send_telegram`). No auto-commitea: avisa (el commit lo hace Jeilin o su IA
  con mensaje real).
- **Esfuerzo:** S · **Horas ahorradas:** previene pérdidas (valor asegurador, no de horas).
- **Medición:** 0 repos con >10 archivos sin commitear al final de cualquier semana.

### A4 — README/CLAUDE.md masivo en activos · **P1 · propuesta**
- **Problema:** ~50% de proyectos sin README; 0 CLAUDE.md fuera de JCDigital.
- **Solución:** IA básica en lote: por cada repo activo, leer package.json + estructura y generar
  ambos archivos desde plantilla. Revisión rápida de Jeilin al final.
- **Esfuerzo:** S (IA básica) · **Horas ahorradas:** ~15 min por cada retomada de proyecto.

### A5 — Onboarding de cliente beauty · **P2 · propuesta**
- **Problema:** 8 proyectos del mismo vertical construidos casi desde cero cada vez.
- **Solución:** plantilla vertical (sitio + citas + catálogo) + formulario de datos del cliente →
  IA básica personaliza (colores, textos, servicios) → deploy con A1+A2. Objetivo: sitio nuevo en
  horas.
- **Esfuerzo:** L · **Horas ahorradas:** ~1-2 semanas por cliente del nicho. La automatización con
  mayor ROI de negocio del sistema.

### A6 — Alerta de errores de workers a WhatsApp · **P2 · propuesta**
- **Problema:** paso 11 del workflow (monitoreo) es "mirar el dashboard cuando me acuerdo".
- **Solución:** logs/errores de workers → n8n (VPS ya pagado) → WhatsApp/Telegram.
- **Esfuerzo:** M · **Medición:** enterarse de un error de producción por alerta antes que por un
  cliente.

### A7 — Limpieza de discos · **P2 · propuesta**
- **Problema:** 1.7GB de basura identificada (pnpm-store 904MB, xamp 767MB, tmp/install/logs).
- **Solución:** script de limpieza + regla de archivo (07-Project-Structure). Un comando, trimestral.
- **Esfuerzo:** XS.

## Reglas del registro

- **[REQUIRED]** Detectaste repetición (≥2 veces manual) → entra aquí con el formato de
  [05-Decision-Matrix.md](05-Decision-Matrix.md), aunque sea en estado `propuesta` con 2 líneas.
- **[REQUIRED]** Una automatización `activa` tiene dueño de mantenimiento (Jeilin o un flujo n8n
  monitoreado) y fecha de última ejecución verificada.
- **[REQUIRED]** Automatizar el proceso ANTES de documentarlo extensamente: si A1 existe, no hace
  falta un manual de "cómo crear proyectos".
