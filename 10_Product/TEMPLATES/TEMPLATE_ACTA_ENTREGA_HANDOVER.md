---
title: "Acta de Entrega Formal, Handover y Traspaso de Cuentas"
category: 10_Product
doc_type: referencia
tags: [product, handover, entrega, offboarding, garantia, traspaso-cuentas]
summary: "Plantilla formal de Acta de Entrega, Handover técnico y Cesión de Propiedad Intelectual. Define la transferencia de credenciales (Cloudflare, Supabase, Stripe), el inicio del periodo de garantía de 30 días y la exoneración de responsabilidad por mal uso posterior."
keywords: [acta-entrega, handover, traspaso-cuentas, garantia, cierre-proyecto, propiedad-intelectual]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "10_Product/TEMPLATES/TEMPLATE_PROPUESTA_TECNICA.md"
  - "06_Testing/CHECKLIST_RELEASE_PRODUCCION.md"
---

# ACTA DE ENTREGA FINAL Y HANDOVER TÉCNICO

**Proyecto:** `[Nombre del Software / Plataforma]`  
**Cliente Receptor:** `[Nombre del Cliente / Empresa]`  
**Agencia Proveedora:** `[Nombre de tu Agencia]`  
**Fecha de Entrega:** `[AAAA-MM-DD]`

---

## 1. Declaración de Entrega y Criterios Cumplidos

Por medio de la presente acta, la **Agencia** hace entrega formal del software **`[Nombre del Proyecto]`** desarrollado según los términos del Documento de Especificación de Requerimientos y Propuesta Técnica aprobada.

El Cliente certifica que ha realizado las pruebas de usuario en conjunto con la Agencia y declara **recibido a satisfacción el sistema**.

---

## 2. Checklist de Traspaso de Cuentas y Accesos (Handover)

- [ ] **Acceso a Base de Datos (Supabase):** Proyecto transferido a la organización del cliente o credenciales maestras entregadas.
- [ ] **Hosting y DNS (Cloudflare):** Dominio apuntado y configurado en la cuenta de Cloudflare del cliente.
- [ ] **Pasarelas de Pago (Wompi / Stripe / NowPayments):** Webhooks en producción activos apuntando al backend del cliente.
- [ ] **Repositorio de Código (GitHub):** Código fuente completo transferido o repositorio entregado con ramas de release.
- [ ] **Cero Tarjetas Personales de la Agencia:** Verificado que ningún servicio en la nube quedó enlazado al método de pago de la agencia.

---

## 3. Garantía y Responsabilidad Post-Entrega

1. **Periodo de Garantía (30 Días):** A partir de esta fecha, el software cuenta con **30 días de garantía** para la corrección de errores o defectos técnicos directamente atribuibles al desarrollo original, sin costo adicional.
2. **Exclusión de Garantía:** La garantía no cubre fallos causados por modificaciones al código realizadas por terceros, caídas del proveedor de nube o cambios en APIs de terceros ajenos a la agencia.
3. **Mantenimiento Mensual:** Cualquier requerimiento nuevo o soporte posterior al periodo de garantía se regirá bajo el contrato de soporte mensual opcional.

---

## 4. Firmas de Aceptación

* **Por el Cliente (Aceptación de Entrega):**  
  Nombre: __________________________________  
  Firma: ___________________________________  Fecha: ____________

* **Por la Agencia (Líder de Desarrollo):**  
  Nombre: __________________________________  
  Firma: ___________________________________  Fecha: ____________
