---
title: "Plantilla de Orden de Cambio de Alcance (Change Request)"
category: 10_Product
doc_type: referencia
tags: [product, scope-creep, change-request, cliente, comercial, contratos]
summary: "Plantilla formal de Orden de Cambio (Change Request) para gestionar peticiones de clientes fuera del alcance inicial (MVP / Discovery). Documenta el impacto técnico, costo adicional y ajuste del cronograma."
keywords: [change-request, scope-creep, orden-cambio, alcance, presupuesto, cronograma]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "10_Product/PRODUCT_REQUIREMENTS_STANDARD.md"
  - "10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md"
---

# ORDEN DE CAMBIO DE ALCANCE (CHANGE REQUEST)

**Proyecto:** `[Nombre del Proyecto]`  
**Cliente:** `[Nombre del Cliente]`  
**Número de Solicitud:** `CR-001`  
**Fecha:** `[AAAA-MM-DD]`

---

## 1. Descripción de la Nueva Funcionalidad Solicitada

> *Describe qué solicitó el cliente y por qué no formaba parte del documento original de Discovery / MVP.*
* **Solicitud:** El cliente solicita agregar integración con facturación electrónica local DIAN / SAT además del cobro estándar con pasarela.

---

## 2. Evaluación de Impacto Técnico y Arquitectura

* **Módulos Afectados:** Backend Worker de pagos, esquema de base de datos de órdenes y formulario de checkout.
* **Riesgo:** Bajo / Medio. No compromete la arquitectura existente, pero requiere un webhook adicional.

---

## 3. Impacto en Cronograma y Presupuesto

| Concepto | Estimación Original | Impacto del Cambio | Nuevo Total |
|---|---|---|---|
| **Tiempo de Entrega** | 4 semanas | + 1 semana adicional | **5 semanas** |
| **Inversión Económica** | `$ [Monto Original]` | `+ $ [Costo Adicional]` | **`$ [Nuevo Total]`** |

---

## 4. Aprobación y Firmas

El cliente acepta que la inclusión de este cambio pospone la fecha de entrega acordada y autoriza el valor adicional indicado.

* **Firma del Cliente (Product Owner):** ___________________________  **Fecha:** ____________
* **Firma Líder Técnico Agencia:** ___________________________  **Fecha:** ____________
