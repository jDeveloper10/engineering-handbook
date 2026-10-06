---
title: "Estándar de Ingeniería para Sistemas Contables"
category: 16_Accounting
doc_type: estandar
tags: [contabilidad, accounting, partida-doble, ledger, auditoria, inmutabilidad, periodos, dinero, multi-empresa, controles-internos]
summary: "Reglas no negociables para construir software contable: partida doble, representación del dinero, inmutabilidad de lo contabilizado, atomicidad documento+asiento, numeración secuencial, cierre de períodos, cuentas configurables, conciliación de auxiliares, bitácora de auditoría, segregación de funciones y conservación de registros."
keywords: [contabilidad, partida doble, libro mayor, asiento, journal entry, general ledger, reverso, nota de credito, cierre contable, periodo cerrado, auditoria, GoBD, SAF-T, ISCA, COSO, segregacion de funciones, IAS 8, NIIF]
status: VERIFIED
confidence: 90%
reviewed: false
sources:
  - "Martin Fowler — Accounting Patterns (Account, Accounting Entry, Accounting Transaction, Reversal/Difference/Replacement Adjustment) — martinfowler.com/eaaDev/AccountingNarrative.html"
  - "Martin Fowler — Patterns of Enterprise Application Architecture: Money — martinfowler.com/eaaCatalog/money.html"
  - "ISO 4217 — Códigos de moneda y unidades menores (USD y PAB: 2 decimales)"
  - "BMF Alemania — GoBD (28-11-2019): trazabilidad, integridad, inmutabilidad y conservación de registros electrónicos"
  - "Francia — Art. 286 I 3° bis CGI y BOI-TVA-DECLA-30-10-30 (condiciones ISCA: inalterabilidad, seguridad, conservación, archivo)"
  - "Portugal — Portaria 363/2010 y 195/2020 (certificación de software de facturación: numeración sin saltos, cadena hash, SAF-T PT)"
  - "OCDE — Standard Audit File for Tax (SAF-T): exportación estructurada de libro mayor, auxiliares, activos e inventario"
  - "COSO 2013 Internal Control — Integrated Framework, Principio 10 (actividades de control, segregación de funciones)"
  - "IASB — NIC/IAS 8 Políticas contables, cambios en estimaciones y errores"
updated: 2026-10-05
---

# Estándar de Ingeniería para Sistemas Contables

> Nivel 1 del dominio `16_Accounting`. Aplica a todo software que registre hechos económicos: contabilidad general, facturación, cuentas por cobrar/pagar, inventario, nómina, activos fijos o bancos. Las reglas fiscales de un país viven en su documento de vertical (ej. [PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md](PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md)); la implementación del motor de contabilización está en [ACCOUNTING_POSTING_ENGINE_PATTERN.md](ACCOUNTING_POSTING_ENGINE_PATTERN.md).

Un sistema contable no es un CRUD con totales. Es un **registro legal**: los auditores, la autoridad fiscal y los tribunales asumen que lo que muestra es completo, exacto y no fue alterado. Un error silencioso aquí no es un bug de UI: es un estado financiero falso firmado por un contador.

---

## 1. Partida doble: el invariante central

### ACC-001 — Todo asiento cuadra **[REQUIRED]**

**Regla:** la suma de débitos de un asiento es exactamente igual a la suma de créditos, comparada en unidades monetarias mínimas (centavos), no con tolerancia de coma flotante. Un asiento que no cuadra no se guarda: se rechaza con un error explícito.

**Por qué:** la ecuación Activo = Pasivo + Patrimonio solo se sostiene si cada transacción la preserva. Un asiento descuadrado contamina la balanza de comprobación, el balance general y todo reporte derivado, y el error se vuelve imposible de localizar meses después.

### ACC-002 — Forma válida de un asiento **[REQUIRED]**

**Regla:** un asiento tiene al menos 2 líneas; cada línea afecta una sola cuenta y tiene **un solo lado** con valor (débito o crédito, nunca ambos ni ninguno); los importes son ≥ 0 (el signo lo da el lado, no un número negativo); todas las cuentas pertenecen a la misma empresa que el asiento.

**Por qué:** los importes negativos y las líneas con ambos lados vuelven ambiguos los reportes (¿un débito negativo es un crédito?) y rompen los filtros de auditoría. La validación de pertenencia evita que un asiento de la empresa A mueva una cuenta de la empresa B.

### ACC-003 — Los reportes se derivan del libro mayor **[REQUIRED]**

**Regla:** balance general, estado de resultados, balanza de comprobación y libro mayor se calculan **a partir de las líneas de asiento contabilizadas**, nunca a partir de las tablas de documentos (facturas, compras) ni de un campo "saldo" editable.

**Por qué:** si un reporte suma facturas y otro suma asientos, divergen en cuanto un documento no generó su asiento (o generó uno distinto). Una sola fuente de verdad hace que todos los reportes cuadren entre sí por construcción. Los campos de saldo cacheados (saldo de cliente, de cuenta) son optimizaciones y deben poder reconstruirse desde el mayor (ver ACC-012).

---

## 2. Dinero

### ACC-004 — Nunca coma flotante binaria para importes **[REQUIRED]**

**Regla:** los importes se almacenan y calculan como **enteros en la unidad mínima de la moneda** (centavos, según los decimales que define ISO 4217 para esa moneda) o en un tipo decimal exacto. Se prohíbe `float`/`double`/`REAL` como representación persistente de dinero. Hereda y especializa la regla DB-008 del handbook.

**Por qué:** `0.1 + 0.2 ≠ 0.3` en IEEE 754. En un mayor con miles de líneas, los errores de representación hacen que un asiento "cuadrado" difiera en 0.0000001 y que los totales no reconcilien. La comparación exacta de ACC-001 solo es posible con enteros o decimales exactos.

**IMPLEMENTACIÓN (TypeScript + SQLite/D1):** columnas `INTEGER` con sufijo `Cents`; conversión a texto solo en la capa de presentación.

```typescript
// DB-008 / ACC-004: importes en centavos (enteros)
type JournalLine = { accountId: string; debitCents: number; creditCents: number }

// Texto "1234.5" → 123450 centavos, sin pasar por coma flotante
const toCents = (input: string): number => {
  const m = /^(-)?(\d+)(?:\.(\d{1,2}))?$/.exec(input.trim())
  if (!m) throw new Error(`Importe inválido: ${input}`)
  const cents = Number(m[2]) * 100 + Number((m[3] ?? "").padEnd(2, "0"))
  return m[1] ? -cents : cents
}
```

**Nota de migración:** un sistema que ya guarda dinero en `REAL` debe migrar a enteros con un script que redondee cada valor a 2 decimales y verifique que la balanza siga cuadrando antes y después.

### ACC-005 — Redondeo explícito y en un solo lugar **[REQUIRED]**

**Regla:** el método de redondeo (ej. mitad hacia arriba) y el nivel en que se aplica (por línea o por documento) se definen una vez, se documentan y se usan en todo el sistema. Los impuestos se redondean según la norma fiscal aplicable. Cuando un monto se reparte (prorrateo, cuotas), los centavos residuales se asignan de forma determinista a una de las partes para que la suma de las partes sea exactamente el total.

**Por qué:** dos módulos que redondean distinto producen facturas cuyo ITBMS no coincide con el declarado y prorrateos que "pierden" un centavo. Fowler documenta exactamente este problema en el patrón Money.

### ACC-006 — La moneda viaja con el importe **[RECOMMENDED]**

**Regla:** si el sistema puede manejar más de una moneda, cada importe persistido lleva su código ISO 4217, y no se suman importes de monedas distintas sin conversión explícita con tasa y fecha. En sistemas monomoneda, la moneda se fija a nivel de empresa.

**Por qué:** sumar dólares con euros produce números sin significado; registrar la tasa permite recalcular diferencias cambiarias.

---

## 3. Inmutabilidad y correcciones

### ACC-007 — Lo contabilizado no se edita ni se borra **[REQUIRED]**

**Regla:** un asiento, factura, nota de crédito, cobro o pago en estado contabilizado/emitido es de solo lectura. Las correcciones se hacen con un **documento nuevo**: asiento de reverso, nota de crédito/débito o anulación con reverso automático. El documento original permanece visible, marcado como anulado, y enlazado a su corrección. Solo los borradores (nunca contabilizados) pueden editarse o eliminarse.

**Por qué:** es el requisito común de todas las normativas de software contable consultadas (GoBD "Unveränderbarkeit", condición de inalterabilidad ISCA en Francia, certificación portuguesa): el contenido original debe poder determinarse durante todo el período de conservación. Fowler llama a esto *Reversal Adjustment*: preserva la historia en lugar de reemplazarla.

### ACC-008 — Un reverso neutraliza, no duplica **[REQUIRED]**

**Regla:** al anular un asiento contabilizado, el original **sigue contabilizado** y se crea un asiento espejo (débitos ↔ créditos) que referencia al original. Nunca se marca el original como excluido **y** se crea además el reverso: eso resta el efecto dos veces.

**Por qué:** es un error real y frecuente. Si los reportes filtran "solo contabilizados" y el original pasa a "anulado", el reverso queda solo y el saldo termina con el signo contrario.

### ACC-009 — Errores de períodos anteriores **[RECOMMENDED]**

**Regla:** la corrección de un error material de un período ya cerrado se registra con un asiento de ajuste en un período abierto contra resultados acumulados, con referencia al error, y se revela según la NIC 8 / sección equivalente de NIIF para PYMES. El sistema no reabre períodos para "arreglar" silenciosamente un asiento viejo.

**Por qué:** la NIC 8 exige reexpresión retrospectiva en los estados financieros, pero los libros conservan la traza del error y de su corrección.

---

## 4. Atomicidad e idempotencia

### ACC-010 — Documento, asiento y saldos en una sola transacción **[REQUIRED]**

**Regla:** emitir un documento con efecto contable (factura, compra, cobro, pago, nota de crédito, ajuste de inventario) escribe en **una única unidad atómica**: el documento, sus líneas, su asiento con sus líneas, los saldos cacheados afectados y el registro de auditoría. Si cualquier paso falla, no queda nada escrito. Se prohíbe capturar y silenciar el error de contabilización (`catch` que solo registra en consola y continúa).

**Por qué:** un documento sin asiento es una venta que no existe para la contabilidad; un asiento sin documento es un movimiento sin soporte. Ambos son hallazgos de auditoría. Silenciar el error hace que el usuario crea que todo se registró.

**IMPLEMENTACIÓN:** transacción de base de datos (Postgres `BEGIN … COMMIT`); en Cloudflare D1, que no ofrece transacciones interactivas, `db.batch([...])` ejecuta todas las sentencias de forma atómica. Ver el patrón en [ACCOUNTING_POSTING_ENGINE_PATTERN.md](ACCOUNTING_POSTING_ENGINE_PATTERN.md).

### ACC-011 — Las operaciones de escritura son idempotentes **[RECOMMENDED]**

**Regla:** las operaciones que crean documentos contables aceptan una clave de idempotencia (o validan unicidad natural, ej. proveedor + número de factura del proveedor) para que un reintento de red no duplique la factura ni el asiento.

**Por qué:** un doble clic o un reintento automático no debe producir dos cobros del mismo cheque.

---

## 5. Numeración de documentos

### ACC-012 — Numeración secuencial, única y asignada por el sistema **[REQUIRED]**

**Regla:** cada tipo de documento (factura, nota de crédito, asiento, recibo) tiene una serie con numeración **correlativa** por empresa, generada por el servidor con un incremento atómico. El usuario no puede elegir, editar ni reutilizar números. Un número consumido por un documento anulado sigue ocupado (el documento anulado se conserva). Para documentos de terceros (factura del proveedor) se guarda el número externo como dato, con unicidad por proveedor.

**Por qué:** las autoridades fiscales usan la correlatividad para detectar ventas omitidas (la certificación portuguesa prohíbe saltos y reinicios). "Buscar el último y sumar 1" en la aplicación produce duplicados con dos usuarios simultáneos.

### ACC-013 — Encadenamiento de integridad **[RECOMMENDED]**

**Regla:** en sistemas que emiten documentos fiscales propios, cada documento emitido guarda un hash que incluye el hash del documento anterior de la misma serie (cadena hash), de modo que la alteración o eliminación de un documento intermedio sea detectable.

**Por qué:** es el mecanismo exigido por la certificación portuguesa y una forma barata de demostrar inalterabilidad (ISCA). Si el país exige factura electrónica autorizada por un tercero (ej. PAC en Panamá), la autorización cumple este rol para los documentos fiscales y la cadena sigue siendo útil para asientos internos.

---

## 6. Períodos contables

### ACC-014 — Los períodos cerrados bloquean escrituras **[REQUIRED]**

**Regla:** el sistema mantiene períodos (mensuales y/o anuales) con estado abierto/cerrado. Ninguna operación (documento, asiento, anulación, ajuste) puede registrarse con fecha contable dentro de un período cerrado; la validación ocurre en el servidor, en el mismo punto donde se valida el cuadre. Reabrir un período requiere un permiso específico y queda en la bitácora.

**Por qué:** una vez presentados estados financieros o declaraciones fiscales de un período, cualquier cambio posterior hace que los libros ya no coincidan con lo declarado.

### ACC-015 — Cierre anual con asiento de cierre **[REQUIRED]**

**Regla:** el cierre del ejercicio genera un asiento que lleva a cero las cuentas de resultado (ingresos y gastos) contra la cuenta de utilidades retenidas/resultados acumulados, y bloquea el período. El estado de resultados de un año nunca arrastra saldos del anterior.

**Por qué:** sin el asiento de cierre, la utilidad del año 2 incluye la del año 1 y el patrimonio no refleja los resultados acumulados.

---

## 7. Plan de cuentas y contabilización automática

### ACC-016 — Cuentas por defecto configurables, nunca códigos fijos en el código **[REQUIRED]**

**Regla:** la contabilización automática (ventas, ITBMS/IVA, cuentas por cobrar, inventario, costo de ventas, bancos, nómina…) usa un **mapeo de cuentas por empresa** editable por un usuario con permiso. El código fuente no contiene números de cuenta. Si falta una cuenta requerida, la operación falla con un mensaje que indica qué cuenta configurar; nunca se omite el asiento.

**Por qué:** cada empresa tiene su propio catálogo. Un código fijo (`'1030'`) funciona en la empresa de pruebas y falla en silencio en la primera empresa real que numera distinto.

### ACC-017 — Integridad del plan de cuentas **[REQUIRED]**

**Regla:** cada cuenta tiene un tipo (activo, pasivo, patrimonio, ingreso, gasto) que determina su saldo normal y su lugar en los estados financieros. No se elimina una cuenta con movimientos (se inactiva). No se cambia el tipo de una cuenta con movimientos. El código de cuenta es único por empresa.

**Por qué:** borrar o retipificar una cuenta con historia reescribe retroactivamente los estados financieros ya emitidos.

---

## 8. Auxiliares y conciliación

### ACC-018 — Los auxiliares cuadran con el mayor **[REQUIRED]**

**Regla:** el saldo total de cuentas por cobrar por cliente, cuentas por pagar por proveedor, inventario valorizado y activos fijos debe ser igual al saldo de su cuenta de control en el libro mayor. El sistema ofrece un reporte o verificación automática que compara ambos y señala diferencias.

**Por qué:** si el auxiliar de clientes dice B/.10,000 y la cuenta de control B/.9,500, alguno de los dos mintió; la conciliación periódica es lo que detecta documentos sin asiento o asientos manuales a cuentas de control.

### ACC-019 — Cuentas de control protegidas **[RECOMMENDED]**

**Regla:** las cuentas de control de auxiliares (clientes, proveedores, inventario) solo reciben movimientos desde sus módulos; los asientos manuales a esas cuentas se bloquean o exigen un permiso elevado y una justificación.

**Por qué:** un asiento manual a "Clientes" sin cliente asociado rompe ACC-018 de forma permanente.

---

## 9. Auditoría y trazabilidad

### ACC-020 — Bitácora de auditoría append-only **[REQUIRED]**

**Regla:** toda creación, emisión, anulación, cambio de configuración contable, cierre/reapertura de período, cambio de rol y acceso a funciones sensibles se registra con: usuario, empresa, acción, entidad e identificador, fecha/hora del servidor, IP y un resumen de los datos relevantes (antes/después en cambios). La bitácora no se puede editar ni borrar desde la aplicación y se conserva al menos el plazo legal de conservación de registros.

**Por qué:** la trazabilidad ("Nachvollziehbarkeit" en GoBD) exige poder reconstruir quién hizo qué. Una vista de "actividad" derivada de fechas de creación no sirve: no registra anulaciones, cambios ni accesos.

### ACC-021 — Cada asiento automático enlaza a su documento fuente **[REQUIRED]**

**Regla:** los asientos generados por documentos guardan el tipo y el identificador del documento origen, y el documento conoce sus asientos. Desde cualquier línea del mayor se puede llegar al documento que la originó (*drill-down*).

**Por qué:** un auditor muestrea líneas del mayor y pide su soporte; sin el enlace, eso es una búsqueda manual por fecha y monto.

---

## 10. Control interno y permisos

### ACC-022 — Permisos aplicados en el servidor, por acción **[REQUIRED]**

**Regla:** cada operación de la API verifica en el servidor que el usuario pertenece a la empresa activa y que su rol tiene el permiso de esa acción específica (registrar, contabilizar, anular, cerrar período, configurar cuentas, administrar usuarios). Ocultar botones en la interfaz no cuenta como control.

**Por qué:** un rol "solo lectura" que puede llamar directamente a la API de facturas no es solo lectura. Es la forma más común de que un control interno exista en papel pero no en el sistema.

### ACC-023 — Segregación de funciones **[RECOMMENDED]**

**Regla:** los permisos se diseñan para que una misma persona no pueda, sin un segundo control, registrar y aprobar/anular una transacción, crear un proveedor y pagarle, o reabrir un período y modificarlo. Donde la empresa es demasiado pequeña para separar personas, la bitácora (ACC-020) y la revisión periódica actúan como control compensatorio.

**Por qué:** COSO 2013 (principio 10) identifica la segregación de funciones incompatibles (autorización, registro, custodia, revisión) como característica clave de las actividades de control.

### ACC-024 — Aislamiento estricto entre empresas **[REQUIRED]**

**Regla:** en sistemas multiempresa, cada consulta y escritura filtra por la empresa activa de la sesión, y la empresa activa se establece en el servidor tras verificar la membresía del usuario. Nunca se acepta del cliente el identificador de empresa ni el rol como dato de confianza. Hereda TENANT-001.

**Por qué:** una fuga entre empresas expone información financiera confidencial de terceros.

---

## 11. Impuestos

### ACC-025 — Impuestos por línea, con tasas como datos versionados **[REQUIRED]**

**Regla:** la tasa de impuesto se determina por línea (producto/servicio, exento, tasa reducida o especial) y se guarda en la línea al emitir. Las tasas y tablas (impuesto al consumo, seguridad social, retenciones, renta) son **datos con fecha de vigencia**, no constantes en el código, para poder recalcular documentos históricos con la tasa que regía y aplicar cambios futuros sin desplegar código.

**Por qué:** las tasas cambian por ley (ej. la cuota patronal de la CSS en Panamá cambia en 2025, 2027 y 2029). Una constante en el código o recalcula facturas viejas con la tasa nueva, o exige un despliegue el día exacto del cambio.

### ACC-026 — Los impuestos se contabilizan en cuentas separadas **[REQUIRED]**

**Regla:** el impuesto cobrado en ventas (débito fiscal) y el pagado en compras (crédito fiscal) se registran en cuentas propias, separadas del ingreso y del gasto, para que la declaración se pueda conciliar con el mayor.

**Por qué:** la declaración mensual de impuestos debe coincidir con los saldos de esas cuentas; si el impuesto se mezcla con ventas, la conciliación es imposible.

---

## 12. Conservación, exportación y respaldo

### ACC-027 — Conservación por el plazo legal **[REQUIRED]**

**Regla:** los registros contables, documentos de soporte y bitácora se conservan, íntegros y legibles, al menos el plazo legal del país de la empresa (ver vertical del país), aunque el cliente cancele su suscripción. La eliminación de una empresa no borra físicamente sus registros contables antes de ese plazo; se desactiva y se archiva.

**Por qué:** la obligación de conservar es del contribuyente, pero si el software borra sus datos, el contribuyente queda incumpliendo sin saberlo.

### ACC-028 — Exportación estructurada completa **[RECOMMENDED]**

**Regla:** el sistema permite exportar el mayor, los auxiliares, los datos maestros (cuentas, clientes, proveedores, productos) y los documentos en un formato estructurado y documentado (CSV/JSON con esquema, o un formato tipo SAF-T de la OCDE), por rango de fechas.

**Por qué:** auditores y autoridades piden los datos en formato procesable; además garantiza portabilidad si el cliente cambia de software.

### ACC-029 — Respaldos verificados **[REQUIRED]**

**Regla:** la base de datos contable tiene respaldos automáticos, cifrados, fuera del proveedor principal o en otra región, con retención definida, y se prueba periódicamente la restauración completa.

**Por qué:** un respaldo que nunca se restauró es una hipótesis. La pérdida de libros contables es una infracción legal además de un incidente técnico.

---

## 13. Pruebas

### ACC-030 — Los invariantes contables tienen pruebas automáticas **[REQUIRED]**

**Regla:** existen pruebas automatizadas que verifican, para cada flujo que contabiliza (venta, compra, cobro, pago, nota de crédito, anulación, cierre, nómina, depreciación), que: (a) se genera exactamente el asiento esperado, (b) el asiento cuadra, (c) la balanza de comprobación sigue cuadrando, (d) los auxiliares cuadran con el mayor, y (e) una anulación devuelve los saldos al estado previo. Los cálculos fiscales tienen casos de prueba con valores de la norma.

**Por qué:** los errores contables son silenciosos: la pantalla funciona y el número está mal. Solo una prueba que compara contra el resultado esperado los detecta antes que el auditor. Hereda TEST-001.

---

## Checklist de verificación

- [ ] ACC-001/002: el servidor rechaza asientos descuadrados, con una sola línea, con ambos lados o con importes negativos.
- [ ] ACC-003: todos los estados financieros se calculan desde líneas de asiento contabilizadas.
- [ ] ACC-004/005: el dinero se guarda en centavos enteros o decimal exacto; un solo método de redondeo documentado.
- [ ] ACC-007/008: lo contabilizado es de solo lectura; anular crea reverso y el original sigue contando.
- [ ] ACC-010: documento + asiento + saldos + auditoría se escriben de forma atómica; sin `catch` silenciosos al contabilizar.
- [ ] ACC-012: numeración correlativa generada por el servidor con incremento atómico; sin edición manual.
- [ ] ACC-014/015: períodos cerrados bloquean escrituras en el servidor; cierre anual traslada resultados a utilidades retenidas.
- [ ] ACC-016/017: cero códigos de cuenta en el código fuente; cuentas con movimientos no se borran ni cambian de tipo.
- [ ] ACC-018: existe verificación de auxiliares contra cuentas de control.
- [ ] ACC-020/021: bitácora append-only con usuario, acción, entidad, IP; cada asiento enlaza a su documento.
- [ ] ACC-022/024: permisos y empresa activa verificados en el servidor en cada operación.
- [ ] ACC-025/026: tasas como datos con vigencia; impuestos en cuentas propias.
- [ ] ACC-027/028/029: conservación por plazo legal, exportación estructurada, respaldos con restauración probada.
- [ ] ACC-030: pruebas automáticas de invariantes por cada flujo contable.
