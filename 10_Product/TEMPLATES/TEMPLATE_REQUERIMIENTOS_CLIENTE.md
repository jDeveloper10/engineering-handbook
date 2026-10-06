---
title: "Plantilla de Requerimientos y Discovery de Cliente"
category: 10_Product
doc_type: referencia
tags: [product, cliente, discovery, requerimientos, scope, plantilla]
summary: "Plantilla formal de toma de requerimientos (Client Intake / Discovery Document). Define el problema de negocio, usuarios/roles, alcance funcional MVP vs fase 2, integraciones, SLAs y criterios de aceptación verificables."
keywords: [discovery, requerimientos, cliente, scope, mvp, criterios-aceptacion, intake, sla]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "10_Product/PRODUCT_REQUIREMENTS_STANDARD.md"
  - "00_HANDBOOK_FORMAT.md"
---

# DOCUMENTO DE ESPECIFICACIÓN DE REQUERIMIENTOS (DISCOVERY)

> **Uso:** Esta plantilla se completa durante la fase de Discovery con el cliente antes de escribir una sola línea de código o emitir una cotización final. Establece los límites claros del proyecto y evita la expansión descontrolada del alcance (*Scope Creep*).

---

## 1. Información General del Proyecto

* **Nombre del Proyecto:** `[Ej. TiendaGaby E-Commerce / App Móvil]`
* **Cliente / Empresa:** `[Nombre del Cliente / Razón Social]`
* **Responsable por parte del Cliente (Product Owner):** `[Nombre y Correo]`
* **Líder Técnico de la Agencia:** `[Nombre del Ingeniero]`
* **Fecha de Inicio:** `[AAAA-MM-DD]`
* **Fecha Objetivo de Lanzamiento (Go-Live):** `[AAAA-MM-DD]`

---

## 2. Objetivo de Negocio y Problema a Resolver

### 2.1 El Problema Actual
> *Describe qué dolor tiene el cliente hoy y por qué necesita este software.*
* *Ejemplo:* El cliente gestiona reservas por WhatsApp manualmente, perdiendo un 30% de clientes por demora en respuestas y solapamiento de horarios.

### 2.2 La Solución Propuesta
> *Describe el resultado esperado tras implementar el sistema.*
* *Ejemplo:* Sistema web y PWA de autoservicio con confirmación automática por WhatsApp y cobro de anticipos.

---

## 3. Tipos de Usuarios y Roles

| Rol de Usuario | Permisos / Qué puede hacer | Entorno de Acceso |
|---|---|---|
| **Cliente / Usuario Final** | Ver catálogo, reservar citas, pagar online, ver historial | Web Pública / Móvil |
| **Operador / Staff** | Ver agenda del día, marcar citas completadas | Panel Interno |
| **Administrador** | Gestionar precios, usuarios, ver métricas y finanzas | Panel Admin protegido |

---

## 4. Alcance Funcional: MVP (Fase 1) vs. Futuro (Fase 2)

> ⚠️ **Regla de Oro:** Lo que no esté explícitamente en la **Fase 1 (MVP)** queda fuera del alcance y requerirá una orden de cambio o cotización adicional.

### 4.1 En Alcance — Fase 1 (MVP Obligatorio)
- [ ] **Módulo 1: Autenticación:** Login con Magic Link / Correo y Google OAuth.
- [ ] **Módulo 2: Catálogo y Carrito:** Vista responsive de productos/servicios con filtros rápidos.
- [ ] **Módulo 3: Pasarela de Pago:** Integración con Wompi / Stripe / NowPayments (aprobación instantánea con webhook).
- [ ] **Módulo 4: Notificaciones:** Confirmación transaccional vía Email (Resend) o WhatsApp (Baileys/Meta API).
- [ ] **Módulo 5: Panel de Gestión:** Tabla CRUD de órdenes con filtros de fecha y exportación a CSV.

### 4.2 Fuera de Alcance — Fase 2 (Propuestas Futuras)
* Integración con software contable local antiguo.
* Modo offline completo con sincronización peer-to-peer.
* Soporte multi-idioma (se lanza inicialmente solo en Español).

---

## 5. Requerimientos No Funcionales y Restricciones Técnicas

* **Plataformas Soportadas:** Web Responsive (Mobile 375px+, Tablet, Desktop).
* **Rendimiento Objetivo:** Carga inicial < 2.5s (LCP) en conexiones 4G estándar.
* **Seguridad y Privacidad:** Aislamiento multi-tenant por RLS, cifrado HTTPS/TLS 1.3, cumplimiento de tratamiento de datos.
* **Disponibilidad:** 99.5% uptime en infraestructura Cloudflare Edge.

---

## 6. Integraciones de Terceros Necesarias

| Servicio | Proveedor | ¿Quién suministra la cuenta / API Key? |
|---|---|---|
| **Base de Datos / Auth** | Supabase | Agencia / Cliente |
| **Pasarela de Pagos** | Wompi / Stripe / NowPayments | Cliente (con credenciales de API) |
| **Envío de Correos** | Resend | Cliente / Agencia |
| **Almacenamiento de Archivos** | Cloudflare R2 | Agencia |

---

## 7. Criterios de Aceptación y Aprobación Final

El proyecto se considerará **terminado y listo para entrega final** cuando se cumplan las siguientes condiciones medibles:

1. [ ] Todos los flujos del MVP (Fase 1) funcionan en ambiente de Staging sin errores de consola.
2. [ ] El flujo de pago procesa cobros reales y actualiza la base de datos vía webhook en < 3 segundos.
3. [ ] La interfaz se adapta correctamente a dispositivos móviles (iOS Safari y Android Chrome).
4. [ ] Se aprueba el checklist de auditoría de seguridad y escaneo de secretos sin vulnerabilidades críticas.
5. [ ] Firma del acta de entrega y entrega de credenciales / acceso al cliente.
