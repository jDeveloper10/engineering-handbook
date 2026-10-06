---
title: "Plantilla de Contrato de Mantenimiento Mensual y Soporte SLA (Retainer)"
category: 10_Product
doc_type: referencia
tags: [product, comercial, soporte, mantenimiento, retainer, sla, contrato]
summary: "Plantilla de Acuerdo de Nivel de Servicio (SLA) y Mantenimiento Mensual Recurrente para clientes. Define niveles de severidad (P1/P2/P3), horas incluidas de desarrollo menor, respaldos periódicos y costos de hosting."
keywords: [mantenimiento, soporte, retainer, sla, contrato-soporte, recurrente, garantia]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "08_Cloud/ESCALABILIDAD_Y_MANTENIMIENTO.md"
  - "10_Product/TEMPLATES/TEMPLATE_ACTA_ENTREGA_HANDOVER.md"
---

# ACUERDO DE MANTENIMIENTO MENSUAL, SOPORTE Y SLA (RETAINER)

**Cliente:** `[Nombre del Cliente / Empresa]`  
**Proveedor:** `[Nombre de tu Agencia / Estudio]`  
**Plataforma Soportada:** `[Nombre del Software]`  
**Vigencia:** Mensual renovable automáticamente  
**Tarifa Mensual:** `$ [Monto USD / Moneda Local] / mes`

---

## 1. Servicios Incluidos en el Plan Mensual

* 🛡️ **Monitoreo de Disponibilidad 24/7:** Detección y respuesta ante caídas del servidor o fallos de DNS.
* 📦 **Respaldos Automáticos:** Verificación diaria de copias de seguridad de la base de datos y archivos.
* 🔄 **Actualizaciones de Seguridad:** Parches de librerías, dependencias npm y reglas de WAF en Cloudflare.
* ⏱️ **Bolsa de Horas de Desarrollo Menor:** Hasta **`[X] horas mensuales`** (no acumulables) para ajustes menores de texto, colores, banners o mejoras pequeñas sin cotización extra.

---

## 2. Acuerdos de Nivel de Servicio (SLA) y Tiempos de Respuesta

| Nivel de Severidad | Definición | Tiempo Máximo de Respuesta | Tiempo Objetivo de Solución |
|---|---|:---:|:---:|
| **P1 — Crítico** | El sitio está completamente inaccesible o la pasarela de pagos no procesa cobros. | **< 2 horas** | < 6 horas |
| **P2 — Alto** | Una funcionalidad importante no funciona (ej. no se envían correos de confirmación), pero el resto opera. | **< 6 horas** | < 24 horas |
| **P3 — Normal / Menor** | Ajustes visuales, dudas de uso o cambios dentro de la bolsa de horas. | **< 24–48 horas hábiles** | Según complejidad |

---

## 3. Exclusiones del Servicio de Mantenimiento

* Desarrollo de módulos completamente nuevos que no formaban parte del alcance original (se cotizan vía *Change Request*).
* Costos de infraestructura de terceros (Cloudflare, Supabase, Resend, dominios), los cuales son facturados directamente por los proveedores a la tarjeta del cliente.

---

## 4. Firmas del Acuerdo

* **Por el Cliente:** ___________________________  **Fecha:** ____________
* **Por la Agencia:** ___________________________  **Fecha:** ____________
