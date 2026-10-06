---
title: "Dominio Accounting — Índice"
category: 16_Accounting
doc_type: referencia
tags: [contabilidad, accounting, indice]
summary: "Índice del dominio de sistemas contables: estándar general (ACC-001 a ACC-030), patrón del motor de contabilización y vertical de cumplimiento fiscal de Panamá."
keywords: [contabilidad, accounting, ledger, partida doble, panama, itbms, factura electronica, nomina]
updated: 2026-10-05
status: current
---

# Dominio Accounting — Sistemas contables y fiscales

Reglas para construir software que registra hechos económicos con valor legal: contabilidad general, facturación, cuentas por cobrar/pagar, inventario, nómina, activos fijos y bancos.

## Documentos del dominio

| Documento | Tipo | Nivel | Descripción |
|---|---|---|---|
| [ACCOUNTING_SYSTEMS_STANDARD.md](ACCOUNTING_SYSTEMS_STANDARD.md) | Estándar | 1 | Partida doble, dinero en centavos, inmutabilidad, atomicidad, numeración, períodos, cuentas configurables, auxiliares, auditoría, permisos, impuestos, conservación y pruebas (ACC-001 a ACC-030) |
| [ACCOUNTING_POSTING_ENGINE_PATTERN.md](ACCOUNTING_POSTING_ENGINE_PATTERN.md) | Patrón | 2 | Motor de contabilización único: reglas por documento, validación, numeración atómica, lote atómico (D1 batch) y anulación por reverso (PE-001 a PE-005) |
| [PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md](PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md) | Estándar | 3 (Panamá) | NIIF/PYMES, conservación 5 años, ITBMS y formularios 430/43, factura electrónica (SFEP, PAC, CUFE, contingencia), CSS (Ley 462), décimo tercer mes, ISR (PA-001 a PA-018) |

## Reglas inquebrantables del dominio

| ID | Regla |
|---|---|
| ACC-001 | Todo asiento cuadra exactamente (débitos = créditos, en centavos) |
| ACC-004 | Dinero en enteros (centavos) o decimal exacto; nunca coma flotante (hereda DB-008) |
| ACC-007 | Lo contabilizado no se edita ni se borra: se corrige con reverso o nota de crédito |
| ACC-010 | Documento + asiento + saldos + auditoría en una sola operación atómica |
| ACC-012 | Numeración correlativa asignada por el servidor con incremento atómico |
| ACC-014 | Los períodos cerrados bloquean escrituras en el servidor |
| ACC-016 | Cero códigos de cuenta en el código: cuentas por defecto configurables por empresa |
| ACC-020 | Bitácora de auditoría append-only |
| ACC-022 | Permisos verificados en el servidor por acción |

## Cuándo leer qué

- **Diseñar o revisar cualquier módulo contable** → estándar general, completo.
- **Escribir código que crea asientos** → además, el patrón del motor.
- **Cliente en Panamá** (impuestos, factura electrónica, nómina) → además, la vertical de Panamá. Para otro país, crear su vertical siguiendo la misma estructura.
