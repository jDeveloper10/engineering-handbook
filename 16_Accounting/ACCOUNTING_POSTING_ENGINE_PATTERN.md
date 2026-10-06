---
title: "Patrón: Motor de Contabilización (Posting Engine)"
category: 16_Accounting
doc_type: patron
tags: [contabilidad, posting, asiento, reverso, secuencias, atomicidad, d1, batch, idempotencia]
summary: "Implementación de referencia de un motor de contabilización: reglas de contabilización por documento, validación de cuadre y período, numeración atómica, escritura documento+asiento+saldos+auditoría en un solo lote atómico (Cloudflare D1 batch) y anulación por reverso."
keywords: [posting engine, posting rules, journal entry, reversal, sequence, d1 batch, atomic, accounting transaction, fowler]
status: VERIFIED
confidence: 90%
reviewed: false
sources:
  - "Martin Fowler — Accounting Patterns: Posting Rule, Accounting Transaction, Reversal Adjustment — martinfowler.com/eaaDev/AccountingNarrative.html"
  - "Cloudflare D1 — Database API: batch() ejecuta sentencias como una transacción (rollback si una falla) — developers.cloudflare.com/d1"
  - "SQLite — INSERT … ON CONFLICT DO UPDATE (UPSERT) y cláusula RETURNING — sqlite.org/lang_upsert.html, sqlite.org/lang_returning.html"
updated: 2026-10-05
---

# Patrón: Motor de Contabilización (Posting Engine)

> Implementa las reglas ACC-001, 002, 008, 010, 012, 014, 016, 020 y 021 de [ACCOUNTING_SYSTEMS_STANDARD.md](ACCOUNTING_SYSTEMS_STANDARD.md). Este documento no repite el porqué de esas reglas; define **cómo** se cumplen juntas.

## 1. Problema

Cada módulo (ventas, compras, bancos, nómina, inventario) necesita crear asientos. Si cada uno los arma por su cuenta aparecen: códigos de cuenta fijos distintos por módulo, asientos que fallan en silencio, numeración duplicada y documentos guardados sin su asiento cuando algo falla a mitad de camino.

## 2. Solución

Un único módulo — el motor — es el **único** código autorizado a escribir asientos. Los módulos de negocio le entregan una intención ("contabilizar la factura X") y el motor:

```
Documento de negocio
      │  1. Regla de contabilización del tipo de documento → líneas en términos de CLAVES de cuenta
      ▼
Resolver cuentas (mapeo por empresa, ACC-016)  ── falta una → error 422, nada se escribe
      │
      ▼
Validar: cuadre exacto en centavos (ACC-001), forma de líneas (ACC-002), período abierto (ACC-014)
      │
      ▼
Numerar: incremento atómico de la serie (ACC-012)
      │
      ▼
Armar UN lote: documento + líneas + asiento + líneas de asiento + saldos + auditoría (ACC-010, 020, 021)
      │
      ▼
db.batch(lote)  ── todo o nada
```

## 3. Restricciones

### PE-001 — Única puerta de escritura del mayor **[REQUIRED]**
Ningún handler de API inserta directamente en las tablas de asientos; todos pasan por el motor. **Por qué:** es la única forma de garantizar que toda línea del mayor pasó por las mismas validaciones.

### PE-002 — Las reglas de contabilización hablan en claves, no en cuentas **[REQUIRED]**
Una regla dice "débito a `RECEIVABLE`, crédito a `SALES` y a `TAX_PAYABLE`"; el motor traduce claves a cuentas con el mapeo de la empresa. **Por qué:** permite que cada empresa tenga su catálogo y que el código no contenga números de cuenta (ACC-016).

### PE-003 — Validar todo antes de escribir **[REQUIRED]**
Cuadre, período, pertenencia de cuentas, permisos y reglas de negocio (saldo pendiente suficiente, documento no anulado) se validan antes de construir el lote. **Por qué:** en bases sin transacciones interactivas no se puede "deshacer" a mitad del flujo; el lote atómico solo protege la escritura.

### PE-004 — El número se consume aunque el lote falle **[RECOMMENDED]**
La serie se incrementa con una sentencia atómica separada antes del lote. Si el lote falla, ese número queda como salto; el salto se registra en la bitácora con su causa. **Por qué:** es preferible un salto justificado a reutilizar un número (que es lo que ACC-012 prohíbe). Donde la base soporte transacciones completas, el incremento va dentro de la misma transacción y no hay saltos.

### PE-005 — Anular es contabilizar el espejo **[REQUIRED]**
Anular un documento crea, en el mismo lote, el asiento espejo de cada asiento del documento (con `reversalOfId`), marca el documento y el asiento original con fecha de anulación (sin excluirlos de los reportes) y revierte los saldos cacheados. **Por qué:** ACC-007 y ACC-008.

## 4. Implementación de referencia (TypeScript + Cloudflare D1)

> Esta es la capa 2: cambia si cambia el stack. En Postgres, sustituya `db.batch` por una transacción `BEGIN … COMMIT` y el incremento de secuencia puede ir dentro de ella.

### 4.1 Tipos

```typescript
// ACC-004: importes en centavos (enteros)
export type AccountKey = "CASH_BANK" | "RECEIVABLE" | "SALES" | "TAX_PAYABLE" | "TAX_CREDIT" | "PAYABLE" | "INVENTORY" | "COGS"

export interface PostingLine {
  account: AccountKey | { accountId: string }   // clave del mapeo o cuenta explícita (asientos manuales)
  debitCents: number
  creditCents: number
  memo?: string
}

export interface PostingRequest {
  companyId: string
  userId: string
  dateIso: string            // fecha contable (aaaa-mm-dd)
  description: string
  source: { type: "INVOICE" | "PAYMENT" | "BILL" | "VENDOR_PAYMENT" | "CREDIT_NOTE" | "MANUAL"; id: string }
  lines: PostingLine[]
}
```

### 4.2 Validación (ACC-001, ACC-002)

```typescript
export function assertBalanced(lines: { debitCents: number; creditCents: number }[]): void {
  if (lines.length < 2) throw new ValidationError("Un asiento necesita al menos dos líneas")
  let debitCents = 0
  let creditCents = 0
  for (const l of lines) {
    const ok = Number.isInteger(l.debitCents) && Number.isInteger(l.creditCents)
      && l.debitCents >= 0 && l.creditCents >= 0
      && (l.debitCents > 0) !== (l.creditCents > 0)
    if (!ok) throw new ValidationError("Cada línea debe tener un solo lado con importe positivo")
    debitCents += l.debitCents
    creditCents += l.creditCents
  }
  if (debitCents !== creditCents) {
    throw new ValidationError(`Asiento descuadrado: débitos ${debitCents} ≠ créditos ${creditCents} (centavos)`)
  }
}
```

### 4.3 Período abierto (ACC-014)

```typescript
export async function assertPeriodOpen(db: D1Database, companyId: string, dateIso: string): Promise<void> {
  const closed = await db
    .prepare(`SELECT name FROM AccountingPeriod
              WHERE companyId = ? AND isClosed = 1 AND date(startDate) <= date(?) AND date(endDate) >= date(?)
              LIMIT 1`)
    .bind(companyId, dateIso, dateIso)
    .first<{ name: string }>()
  if (closed) throw new ValidationError(`El período ${closed.name} está cerrado`)
}
```

### 4.4 Numeración atómica (ACC-012, PE-004)

Un solo `UPSERT … RETURNING` incrementa y devuelve el número; dos usuarios simultáneos nunca reciben el mismo.

```typescript
export async function nextNumber(db: D1Database, companyId: string, series: string, prefix: string, startAt = 1): Promise<string> {
  const row = await db
    .prepare(`INSERT INTO DocumentSequence (id, companyId, key, prefix, nextNumber, padding, updatedAt)
              VALUES (?, ?, ?, ?, ?, 6, ?)
              ON CONFLICT(companyId, key) DO UPDATE SET nextNumber = nextNumber + 1, updatedAt = excluded.updatedAt
              RETURNING nextNumber - 1 AS n, prefix, padding`)
    .bind(crypto.randomUUID(), companyId, series, prefix, startAt + 1, new Date().toISOString())
    .first<{ n: number; prefix: string; padding: number }>()
  if (!row) throw new Error("No se pudo asignar número de documento")
  return `${row.prefix}${String(row.n).padStart(row.padding, "0")}`
}
```

> Al crear la serie por primera vez en una empresa con documentos previos, `startAt` debe ser el mayor número existente + 1 para no colisionar con la numeración heredada.

### 4.5 Construir el lote y escribir (ACC-010, ACC-020, ACC-021)

```typescript
export async function post(db: D1Database, req: PostingRequest, extra: D1PreparedStatement[]): Promise<{ entryId: string; reference: string }> {
  const accounts = await resolveAccounts(db, req.companyId, req.lines)   // PE-002: falla con 422 si falta una
  const lines = req.lines.map((l) => ({ ...l, accountId: accounts(l.account) }))
  assertBalanced(lines)                                                   // PE-003
  await assertPeriodOpen(db, req.companyId, req.dateIso)
  const reference = await nextNumber(db, req.companyId, "JOURNAL", "AST-")

  const entryId = crypto.randomUUID()
  const now = new Date().toISOString()
  const statements = [
    ...extra,                                                             // documento, sus líneas, saldos de auxiliares
    db.prepare(`INSERT INTO "Transaction" (id, companyId, date, reference, description, type, status, sourceType, sourceId, createdBy, createdAt, updatedAt)
                VALUES (?, ?, ?, ?, ?, 'JOURNAL', 'POSTED', ?, ?, ?, ?, ?)`)
      .bind(entryId, req.companyId, req.dateIso, reference, req.description, req.source.type, req.source.id, req.userId, now, now),
    ...lines.map((l) => db
      .prepare(`INSERT INTO TransactionLine (id, transactionId, accountId, debitCents, creditCents, description, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?)`)
      .bind(crypto.randomUUID(), entryId, l.accountId, l.debitCents, l.creditCents, l.memo ?? null, now)),
    db.prepare(`INSERT INTO AuditLog (id, companyId, userId, action, entity, entityId, summary, createdAt) VALUES (?, ?, ?, 'POST', ?, ?, ?, ?)`)
      .bind(crypto.randomUUID(), req.companyId, req.userId, req.source.type, req.source.id, `${reference} — ${req.description}`, now),
  ]
  await db.batch(statements)                                              // todo o nada
  return { entryId, reference }
}
```

### 4.6 Regla de contabilización de una factura de venta

```typescript
// Débito: cuentas por cobrar (total) / Crédito: ventas (subtotal) e ITBMS por pagar (impuesto)
function invoicePostingLines(subtotalCents: number, taxCents: number): PostingLine[] {
  const lines: PostingLine[] = [
    { account: "RECEIVABLE", debitCents: subtotalCents + taxCents, creditCents: 0 },
    { account: "SALES", debitCents: 0, creditCents: subtotalCents },
  ]
  if (taxCents > 0) lines.push({ account: "TAX_PAYABLE", debitCents: 0, creditCents: taxCents })
  return lines
}
```

### 4.7 Anulación por reverso (PE-005)

```typescript
function reversalLines(original: { accountId: string; debitCents: number; creditCents: number }[]): PostingLine[] {
  return original.map((l) => ({ account: { accountId: l.accountId }, debitCents: l.creditCents, creditCents: l.debitCents }))
}
// El asiento original NO se excluye de los reportes: se marca voidedAt y el espejo lo neutraliza.
```

## 5. Reglas de contabilización de referencia

| Documento | Débito | Crédito |
|---|---|---|
| Factura de venta | Cuentas por cobrar (total) | Ventas / Ingresos por servicios (subtotal por línea) · Impuesto por pagar (impuesto) |
| Costo de la venta (productos con inventario) | Costo de ventas | Inventario |
| Cobro | Banco | Cuentas por cobrar |
| Nota de crédito a cliente | Ventas (subtotal) · Impuesto por pagar (impuesto) | Cuentas por cobrar (total) |
| Factura de compra | Inventario o gasto (subtotal por línea) · Impuesto crédito fiscal (impuesto) | Cuentas por pagar (total) |
| Pago a proveedor | Cuentas por pagar | Banco |
| Planilla | Gasto de sueldos · Gasto cuota patronal | Retenciones y cuotas por pagar · Banco / salarios por pagar |
| Depreciación | Gasto de depreciación | Depreciación acumulada |
| Cierre anual | Cada cuenta de ingreso (su saldo) | Cada cuenta de gasto (su saldo) · diferencia a utilidades retenidas |

## 6. Anti-patrones

```typescript
// ❌ ANTI-PATRÓN: código de cuenta fijo y error silenciado (viola ACC-016 y ACC-010)
const ventas = await prisma.account.findFirst({ where: { companyId, code: "4010" } })
if (!ventas) { console.warn("cuenta no encontrada"); return }   // la factura queda sin asiento

// ❌ ANTI-PATRÓN: numeración calculada en la aplicación (viola ACC-012)
const last = await prisma.invoice.findFirst({ orderBy: { invoiceNumber: "desc" } })
const next = Number(last.invoiceNumber.split("-")[1]) + 1        // dos usuarios → mismo número

// ❌ ANTI-PATRÓN: escrituras separadas sin atomicidad (viola ACC-010)
await prisma.invoice.create({ data })
await prisma.transaction.create({ data: entry })                 // si falla, la factura existe sin asiento
```

## 7. Checklist

- [ ] PE-001: búsqueda en el código de inserciones a la tabla de asientos fuera del motor = 0 resultados.
- [ ] PE-002: búsqueda de códigos de cuenta literales en el código de negocio = 0 resultados.
- [ ] PE-003: todas las validaciones ocurren antes de `batch()`.
- [ ] PE-004: la serie se incrementa con una sentencia atómica (`UPSERT … RETURNING` o transacción).
- [ ] PE-005: anular genera asiento espejo con `reversalOfId` y el original sigue contabilizado.
- [ ] Prueba automatizada por cada regla de contabilización de la tabla de la sección 5 (ACC-030).
