---
title: "Estándar de Cumplimiento Contable y Fiscal — Panamá"
category: 16_Accounting
doc_type: estandar
tags: [panama, contabilidad, itbms, factura-electronica, dgi, pac, sfep, cufe, css, nomina, decimo-tercer-mes, isr, niif, ley-52, conservacion]
summary: "Vertical Panamá del dominio contable: NIIF/NIIF para PYMES, conservación de registros (Código de Comercio art. 93 y Ley 52 de 2016), ITBMS (tasas, exenciones, formulario 430), factura electrónica (Ley 76 de 2019, SFEP, PAC, CUFE, contingencia), informe de compras 43, cuotas CSS (Ley 462 de 2025), seguro educativo, décimo tercer mes e ISR de asalariados."
keywords: [panama, itbms, 7%, 10%, 15%, formulario 430, informe 43, factura electronica, sfep, pac, cufe, decreto 766, ley 76 2019, css, ley 462, cuota patronal 13.25, seguro educativo, decimo tercer mes, isr articulo 700, ley 52 2016, ley 280 2021, niif pymes]
status: VERIFIED
confidence: 85%
reviewed: false
sources:
  - "DGI Panamá — Factura Electrónica, preguntas frecuentes (Decreto Ejecutivo 766 de 29-12-2020; PAC; CUFE; contingencia 72 h) — dgi.mef.gob.pa/_7FacturaElectronica/fpreguntas"
  - "Ley 76 de 2019 (obligación de facturar mediante equipos fiscales o el Sistema de Facturación Electrónica de Panamá)"
  - "Código Fiscal de Panamá, art. 1057-V (ITBMS) y DGI — Servicios y actividades exentas — dgi.mef.gob.pa/itbms"
  - "DGI — Formulario 430 (declaración mensual ITBMS) y Formulario 43 (informe de compras) — dgi.mef.gob.pa/DInforme"
  - "Código de Comercio de Panamá, art. 93; Ley 52 de 2016 (registros contables de personas jurídicas)"
  - "Ley 280 de 30-12-2021 (Contador Público Autorizado; adopción de NIIF y NIIF para PYMES por la Junta Técnica de Contabilidad)"
  - "Ley 462 de 18-03-2025 (reforma CSS) y comunicado CSS: cuota patronal 13.25% abr-2025 a feb-2027"
  - "Código Fiscal art. 700, modificado por Ley 8 de 15-03-2010 (tarifa ISR personas naturales)"
updated: 2026-10-05
---

# Estándar de Cumplimiento Contable y Fiscal — Panamá

> Nivel 3 (vertical de país). Hereda todas las reglas de [ACCOUNTING_SYSTEMS_STANDARD.md](ACCOUNTING_SYSTEMS_STANDARD.md) y solo agrega lo específico de Panamá. Las tasas y montos de este documento son **datos con vigencia** (ACC-025): deben cargarse como configuración fechada, no como constantes en el código, y verificarse contra la Gaceta Oficial / DGI / CSS antes de cada temporada fiscal.

> ⚠️ Este documento no sustituye asesoría tributaria. Cada valor indica su fuente; ante discrepancia prevalece la norma publicada en Gaceta Oficial.

---

## 1. Marco contable

### PA-001 — Estados financieros bajo NIIF / NIIF para PYMES **[REQUIRED]**
**Regla:** los estados financieros que genera el sistema (estado de situación financiera, estado de resultados, cambios en el patrimonio, flujos de efectivo) siguen la estructura de NIIF completas o NIIF para PYMES según la entidad. Las entidades sin obligación pública de rendir cuentas usan NIIF para PYMES.
**Por qué:** la Ley 280 de 2021 confirma la adopción de NIIF, NIIF para PYMES y NIA por la Junta Técnica de Contabilidad. Un software que solo produce balance y resultados queda corto: faltan flujo de efectivo y cambios en el patrimonio.

### PA-002 — Moneda **[REQUIRED]**
**Regla:** la moneda funcional por defecto es el balboa (PAB, ISO 4217 código 590), a la par con el dólar estadounidense (USD, 840); ambos con 2 decimales. Los importes se muestran como `B/.` o `$` según la preferencia de la empresa, sin conversión entre ellos.
**Por qué:** el balboa circula a la par del dólar; tratarlos como monedas distintas con tipo de cambio introduce diferencias cambiarias inexistentes.

---

## 2. Conservación de registros

### PA-003 — Conservar al menos 5 años **[REQUIRED]**
**Regla:** registros contables y documentación de soporte se conservan **mínimo 5 años** contados desde el último día del año calendario en que se completaron las transacciones (o desde el cese de operaciones de la persona jurídica). Los comprobantes que sustentan operaciones mercantiles se conservan además hasta la prescripción de las acciones que puedan derivarse de ellos. El sistema no permite eliminar datos contables de una empresa antes de ese plazo (ACC-027).
**Por qué:** Código de Comercio art. 93 y Ley 52 de 2016. El plazo es el mínimo legal; contratos o auditorías pueden exigir más.

### PA-004 — Entrega anual al agente residente **[RECOMMENDED]**
**Regla:** el sistema facilita exportar los registros contables del ejercicio cerrado (al 31 de diciembre) para entregarlos al agente residente antes del 30 de abril, y registrar el lugar donde se mantienen los registros.
**Por qué:** la Ley 52 de 2016 obliga a las personas jurídicas a proporcionar anualmente esa información al agente residente e informar cambios de ubicación en 15 días hábiles.

---

## 3. ITBMS

### PA-005 — Tasas por línea con vigencia **[REQUIRED]**
**Regla:** cada producto/servicio tiene una tasa de ITBMS configurable, guardada en la línea al emitir. Tasas vigentes (Código Fiscal art. 1057-V):

| Tasa | Aplica a (resumen) |
|---|---|
| 7% | Tarifa general de bienes y servicios |
| 10% | Bebidas alcohólicas y servicios de hospedaje |
| 15% | Productos derivados del tabaco |
| 0% / exento | Bienes y servicios exentos (p. ej. medicamentos, alimentos de la canasta, servicios médicos, educación formal; ver lista DGI) |

**Por qué:** una sola tasa fija del 7% cobra mal a hoteles, licoreras y comercios con productos exentos, y la declaración no cuadra.

### PA-006 — Débito y crédito fiscal en cuentas separadas **[REQUIRED]**
**Regla:** el ITBMS de ventas se acredita a "ITBMS por pagar" y el de compras se debita a "ITBMS crédito fiscal" (cuenta de activo) o, si la empresa lo prefiere, en débito a la misma cuenta de pasivo. El reporte de liquidación toma ambos saldos del libro mayor. Aplicación local de ACC-026.

### PA-007 — Declaración mensual (formulario 430) **[REQUIRED]**
**Regla:** el sistema produce la liquidación mensual de ITBMS (ventas gravadas por tasa, ventas exentas, compras con crédito, impuesto neto) para el formulario 430, cuyo plazo vence el **día 15 del mes siguiente** (o el siguiente día hábil). Muestra el vencimiento y alerta antes del plazo.
**Por qué:** DGI — formulario 430 y calendario de vencimientos.

### PA-008 — Informe de compras (formulario 43) **[RECOMMENDED]**
**Regla:** el sistema permite exportar el detalle mensual de compras e importaciones por proveedor (RUC, DV, monto, ITBMS) para el formulario 43, con vencimiento el **último día del mes siguiente**.
**Por qué:** obligatorio para contribuyentes con ingresos brutos ≥ B/.1,000,000 o activos ≥ B/.3,000,000 (DGI). Requiere que cada proveedor tenga RUC y dígito verificador registrados.

---

## 4. Factura electrónica (SFEP)

### PA-009 — Emisión por equipo fiscal o factura electrónica autorizada **[REQUIRED]**
**Regla:** las facturas de venta con validez fiscal se emiten mediante el **Sistema de Facturación Electrónica de Panamá (SFEP)** a través de un **PAC** (Proveedor Autorizado Calificado) habilitado por la DGI, o mediante equipo fiscal. Un PDF generado por el sistema **no es** factura fiscal: hasta que el PAC autoriza el documento, la factura es un comprobante interno.
**Por qué:** Ley 76 de 2019 y Decreto Ejecutivo 766 de 2020. Los contribuyentes que facturan más de B/.36,000 al año están obligados, y las empresas nuevas desde 2022 deben usar factura electrónica.

### PA-010 — Integración desacoplada con el PAC **[REQUIRED]**
**Regla:** la emisión electrónica se implementa detrás de una interfaz de proveedor (`emitir`, `consultarEstado`, `anular`, `descargar XML/PDF`) para poder cambiar de PAC sin tocar la lógica contable. Las credenciales del PAC se guardan como secretos del servidor, nunca en el cliente (SEC-002).
**Por qué:** cada PAC expone una API propia; acoplar el sistema a uno vuelve costoso cambiarlo.

### PA-011 — Guardar la evidencia de autorización **[REQUIRED]**
**Regla:** por cada documento autorizado se almacenan: CUFE (Código Único de Factura Electrónica), número de protocolo de autorización, fecha/hora de autorización, código QR o URL de consulta y el XML firmado. La factura impresa/PDF muestra CUFE y QR.
**Por qué:** el CUFE identifica de forma única el documento ante la DGI; el PAC solo conserva copias por un tiempo limitado (60 días según la DGI), por lo que la conservación de 5 años (PA-003) es responsabilidad del emisor.

### PA-012 — Correcciones con notas de crédito/débito electrónicas **[REQUIRED]**
**Regla:** una factura electrónica autorizada no se edita ni se elimina; se corrige con **nota de crédito** o **nota de débito** electrónica que referencia la factura original. Aplicación local de ACC-007.

### PA-013 — Modo de contingencia **[REQUIRED]**
**Regla:** si el PAC no responde, el sistema emite en contingencia, marca los documentos como pendientes y los envía para autorización al restablecerse la conexión, dentro del plazo permitido (**72 horas** según la DGI). La interfaz muestra el estado (pendiente, autorizado, rechazado) de cada documento y alerta los rechazados.
**Por qué:** detener la facturación por una caída del PAC detiene el negocio; dejar documentos sin autorizar más allá del plazo es incumplimiento.

---

## 5. Nómina

### PA-014 — Cuotas de seguridad social con vigencia **[REQUIRED]**
**Regla:** las cuotas se cargan como tabla con fecha de vigencia:

| Concepto | Trabajador | Empleador | Vigencia / fuente |
|---|---|---|---|
| CSS (salario) | 9.75% | 13.25% | Abr-2025 a feb-2027 (Ley 462 de 2025) |
| CSS (salario) | 9.75% | 14.25% | Desde mar-2027 (Ley 462 de 2025) |
| CSS (salario) | 9.75% | 15.25% | Desde mar-2029 (Ley 462 de 2025) |
| Seguro educativo | 1.25% | 1.50% | Vigente |
| Riesgos profesionales | — | Según actividad (CIIU) de la empresa | Tarifa asignada por la CSS; configurable por empresa |
| CSS sobre décimo tercer mes | 7.25% | Según tabla vigente de la CSS | Verificar tasa patronal antes de procesar |

**Por qué:** la Ley 462 de 2025 sube la cuota patronal de forma escalonada; un sistema con 12.25% fijo (tasa anterior) subdeclara la cuota patronal desde abril de 2025.

### PA-015 — Décimo tercer mes **[REQUIRED]**
**Regla:** el décimo se calcula como la suma de salarios devengados en el período ÷ 12, en tres partidas:

| Partida | Período | Pago |
|---|---|---|
| 1.ª | 16 dic – 15 abr | 15 de abril |
| 2.ª | 16 abr – 15 ago | 15 de agosto |
| 3.ª | 16 ago – 15 dic | 15 de diciembre |

Se usa el salario efectivamente devengado (incluye ingreso proporcional si el empleado entró o salió en el período). Se aplica la cuota obrera de CSS de 7.25% y la retención de ISR cuando el ingreso anual proyectado del empleado la exige.

### PA-016 — ISR de asalariados **[REQUIRED]**
**Regla:** la retención mensual se calcula proyectando la renta neta gravable anual y aplicando la tarifa del art. 700 del Código Fiscal (modificado por Ley 8 de 2010):

| Renta neta gravable anual | Impuesto |
|---|---|
| Hasta B/.11,000 | 0% |
| B/.11,000.01 – B/.50,000 | 15% sobre el excedente de B/.11,000 |
| Más de B/.50,000 | B/.5,850 + 25% sobre el excedente de B/.50,000 |

La retención del período = impuesto anual ÷ número de períodos de pago del año.
**Por qué:** las tablas simplificadas sobre el salario mensual menos cuotas difieren del cálculo anual en meses con ingresos variables; la proyección anual es el método de la norma.

### PA-017 — Planilla persistida y archivo para la CSS **[REQUIRED]**
**Regla:** cada planilla procesada se guarda como documento inmutable (empleado, devengado, deducciones, aportes patronales, neto) con su asiento contable, y se puede exportar en el formato que exija la CSS para su presentación. Una estimación en pantalla no reemplaza a la planilla registrada.
**Por qué:** los pagos de cuotas se declaran por planilla y deben coincidir con el mayor (ACC-018).

---

## 6. Datos maestros

### PA-018 — Identificación fiscal completa **[REQUIRED]**
**Regla:** clientes y proveedores contribuyentes registran tipo de contribuyente (natural/jurídico/extranjero), RUC o cédula **y dígito verificador (DV)**, validados por formato. La empresa emisora registra su RUC y DV.
**Por qué:** la factura electrónica y el informe 43 exigen RUC y DV del receptor/proveedor; un dato faltante produce rechazos del PAC.

---

## Checklist

- [ ] PA-001: el sistema genera los cuatro estados financieros NIIF / NIIF PYMES.
- [ ] PA-003: no es posible eliminar registros contables de menos de 5 años.
- [ ] PA-005/006/007: ITBMS por línea (7/10/15/exento), cuentas separadas, liquidación 430 con vencimiento día 15.
- [ ] PA-008: exportación del informe de compras 43.
- [ ] PA-009 a 013: emisión vía PAC detrás de una interfaz, CUFE/protocolo/QR/XML guardados, notas de crédito electrónicas, contingencia ≤ 72 h.
- [ ] PA-014: cuotas CSS y seguro educativo en tabla con vigencia (13.25% patronal hasta feb-2027).
- [ ] PA-015/016/017: décimo en tres partidas sobre lo devengado; ISR por proyección anual; planilla persistida con asiento.
- [ ] PA-018: RUC + DV en clientes, proveedores y empresa.
