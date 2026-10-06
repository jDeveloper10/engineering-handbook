---
title: "Cheatsheet Operativo del Engineering Handbook (Guía de Bolsillo)"
category: root
doc_type: referencia
tags: [cheatsheet, guia-rapida, resumen, comandos, reglas-oro, agency-os]
summary: "Guía de bolsillo de 1 página: las 10 reglas inquebrantables, comandos frecuentes de terminal, buscador instantáneo y cómo trabajar en el día a día sin abrumarse con 190+ documentos."
keywords: [cheatsheet, guia-rapida, comandos, reglas-oro, buscador, flujo-diario]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "AGENTS.md"
  - "00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md"
---

# CHEATSHEET OPERATIVO DE 1 PÁGINA (AGENCY-OS)

> ⚡ **¿Cómo trabajar con 190+ documentos sin abrumarte?**  
> **No los leas todos.** El Handbook funciona por **demanda (*Just-In-Time*)**: solo consultas el documento exacto para la tarea que estás haciendo hoy.

---

## 🔍 1. Buscador Rápido en Terminal (Encuentra cualquier estándar en 1 segundo)

En lugar de buscar carpetas manualmente, usa el buscador del CLI:

```bash
npm run find <tema>
```

* *Ejemplos:*
  * `npm run find pagos` ➔ Te muestra el estándar de webhooks, idempotencia y Stripe.
  * `npm run find cliente` ➔ Te entrega las plantillas de Discovery, Propuesta y Change Request.
  * `npm run find rls` ➔ Te muestra la biblioteca de políticas multi-tenant y RBAC.
  * `npm run find migracion` ➔ Te da el runbook de Disaster Recovery y portabilidad a VPS.
  * `npm run find mobile` ➔ Te da los patrones responsive de 375px y touch targets.

---

## 🔄 2. El Flujo de Trabajo en 4 Pasos para Cualquier Tarea

```
┌───────────────────────────────┐
│ 1. ¿Qué tarea vas a hacer?    │ ➔ Clasifica: DB, Backend, Frontend, Pagos o Cliente.
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ 2. Encuentra el estándar      │ ➔ Ejecuta `npm run find <tema>` o consulta `AGENTS.md`.
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ 3. Aplica la regla REQUIRED   │ ➔ Escribe: Spec ➔ Zod Schema ➔ Test ➔ Código.
└──────────────┬────────────────┘
               │
┌──────────────▼────────────────┐
│ 4. Verifica antes de cerrar   │ ➔ Corre `npm run check` y `npm run scan-secrets`.
└───────────────────────────────┘
```

---

## 🛡️ 3. Las 10 Reglas Inquebrantables de Bolsillo

| ID | Regla | ¿Qué significa en la práctica? |
|---|---|---|
| **S-001** | **Zod en Todo Input** | Todo JSON del frontend y todo body/param del backend pasa por `.safeParse()`. |
| **ERR-001** | **Cero Falsos 200 OK** | Si algo falló, devuelve `400`/`401`/`500` con envelope `{ ok: false, error, code }`. |
| **SEC-002** | **Cero Secretos en Vite** | Prohibido usar `VITE_` para API keys privadas o JWTs; las llamadas privadas van por Workers. |
| **MONEY-001** | **Precios en el Servidor** | El frontend jamás define precios ni montos; se calculan en el backend en **centavos** (`bigint`). |
| **DB-001** | **No `SELECT *`** | Especificar columnas explícitas para reducir uso de RAM y ancho de banda. |
| **DB-002** | **Índices en Foreign Keys** | Toda relación `user_id`, `org_id` o `order_id` debe tener un índice `CREATE INDEX`. |
| **TENANT-001**| **Aislamiento por RLS** | En apps multi-tenant, la base de datos aísla por `organization_id` con Row Level Security. |
| **FE-001** | **Cero `any` en TypeScript** | Usar `unknown` con type guards de Zod o interfaces explícitas. |
| **FE-005** | **Los 4 Estados UI** | Todo componente async maneja: *Loading, Empty, Error y Success*. |
| **API-IDEMP** | **Webhooks Idempotentes** | Registrar `idempotency_key` para que ningún pago se cobre dos veces. |
| **FE-009** | **Cero Pill Badges & Cero Vanity Metrics** | Prohibido en landings: pastillas decorativas sobre H1 y filas de métricas ficticias son de cumplimiento obligatorio: no van NUNCA a menos de que el usuario lo pida explícitamente. |
| **FE-010** | **Diversidad de Componentes (No solo Cards)** | Prohibido encapsular toda la UI en cards, hamburguesa y aside; usar la taxonomía completa (tabs, drawers, sheets, tables, timelines, accordions) y el core de 17 componentes. |

---

## 🛠️ 4. Comandos Frecuentes de la Agencia

```bash
# Buscar un estándar o plantilla
npm run find <termino>

# Validar todo el Handbook (Linter + Re-indexación)
npm run check

# Escanear el bundle de frontend en busca de secretos expuestos
npm run scan-secrets

# Lanzar la red neuronal visual del Handbook
Ver_Red_Handbook.bat
```
