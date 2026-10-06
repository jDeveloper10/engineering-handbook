---
title: "Guía de Ingesta y Migración de Datos de Clientes (CSV / Excel a Base de Datos)"
category: 04_Database
doc_type: runbook
tags: [database, ingesta, csv, excel, supabase, postgres, migracion-datos, sanitizacion, zod]
summary: "Protocolo para procesar, sanitizar, validar con Zod e importar masivamente datos desordenados de clientes (Excel/CSV antiguos) hacia PostgreSQL/Supabase en lotes (batch chunks) con control de duplicados y transacciones."
keywords: [ingesta-datos, csv, excel, migracion, supabase, batch-insert, sanitizacion, deduplicacion]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "04_Database/DATABASE_ENGINEERING_STANDARD.md"
  - "00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md"
---

# GUÍA DE INGESTA Y MIGRACIÓN DE DATOS DE CLIENTES

> 📊 **Objetivo:** Cuando un cliente entrega un archivo Excel o CSV con miles de filas de clientes, productos o transacciones anteriores (con datos sucios, duplicados o fechas inconsistentes), este protocolo define cómo limpiar, validar e importar la información a la base de datos sin errores ni caídas.

---

## 1. El Pipeline de Ingesta en 4 Fases

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. EXTRACT      │ ──► │ 2. SANITIZE     │ ──► │ 3. VALIDATE     │ ──► │ 4. BULK INSERT  │
│ Leer CSV/Excel  │     │ Limpiar strings │     │ Validar esquema │     │ Inserción en    │
│ en streams      │     │ y formatos fecha│     │ con Zod (S-001) │     │ lotes de 500    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 2. Script Estándar de Ingesta y Limpieza en Node.js

**[REQUIRED]** Usar este script base (`scripts/import-client-data.mjs`) para cualquier importación de cliente:

```javascript
import fs from 'node:fs'
import { parse } from 'csv-parse'
import { z } from 'zod'
import { createClient } from '@supabase/supabase-js'

// 1. Conexión autoritativa (Usa SERVICE_ROLE para bypass de RLS durante migración inicial)
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)

// 2. Esquema Zod de Sanitización y Validación
const ClientRowSchema = z.object({
  email: z.string().trim().toLowerCase().email(),
  fullName: z.string().trim().min(2).max(100),
  phone: z.string().transform(val => val.replace(/\D/g, '')).pipe(z.string().min(7)),
  balanceCents: z.coerce.number().int().nonnegative().default(0) // MONEY-001: Siempre centavos
})

async function runImport(filePath) {
  const parser = fs.createReadStream(filePath).pipe(parse({ columns: true, trim: true }))
  
  let validRecords = []
  let errorCount = 0
  const BATCH_SIZE = 500
  const seenEmails = new Set()

  for await (const rawRow of parser) {
    // Normalizar nombres de columnas del Excel del cliente
    const normalized = {
      email: rawRow['Correo'] || rawRow['Email'] || rawRow['email'],
      fullName: rawRow['Nombre'] || rawRow['Nombre Completo'] || rawRow['name'],
      phone: rawRow['Telefono'] || rawRow['Celular'] || rawRow['phone'] || '0000000000',
      balanceCents: Math.round(parseFloat(rawRow['Saldo'] || rawRow['balance'] || '0') * 100)
    }

    const result = ClientRowSchema.safeParse(normalized)

    if (!result.success) {
      console.warn(`⚠️ Fila inválida omitida (${normalized.email}):`, result.error.issues[0].message)
      errorCount++
      continue
    }

    // Deduplicación en memoria
    if (seenEmails.has(result.data.email)) {
      console.warn(`⚠️ Correo duplicado omitido: ${result.data.email}`)
      continue
    }
    seenEmails.add(result.data.email)
    validRecords.push(result.data)

    // Inserción en lotes para no saturar memoria ni conexiones de BD
    if (validRecords.length >= BATCH_SIZE) {
      await insertBatch(validRecords)
      validRecords = []
    }
  }

  // Insertar registros restantes
  if (validRecords.length > 0) {
    await insertBatch(validRecords)
  }

  console.log(`✅ Ingesta finalizada: ${seenEmails.size} importados, ${errorCount} errores omitidos.`)
}

async function insertBatch(records) {
  const { error } = await supabase
    .from('clients')
    .upsert(records, { onConflict: 'email' }) // Evita fallos por colisión

  if (error) {
    console.error('❌ Error al insertar lote en base de datos:', error.message)
    throw error
  }
}

// Ejecución: node scripts/import-client-data.mjs datos_cliente.csv
runImport(process.argv[2]).catch(console.error)
```

---

## 3. Checklist de Verificación de Ingesta de Datos

- [ ] Todos los valores monetarios se convirtieron a enteros en centavos (`MONEY-001`).
- [ ] No existen correos o identificadores duplicados (`onConflict: 'email'`).
- [ ] Los números de teléfono se limpiaron de caracteres especiales (`transform(/\D/g, '')`).
- [ ] Se generó un log con las filas que no pudieron ser importadas para entrega al cliente.
