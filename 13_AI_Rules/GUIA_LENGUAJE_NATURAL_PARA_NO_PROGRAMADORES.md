---
title: "Guía de Prompts en Lenguaje Natural para Usuarios No Programadores"
category: 13_AI_Rules
doc_type: guia
tags: [ai, prompts, lenguaje-natural, no-programadores, automatizacion, agency-os]
summary: "Guía para usar el Handbook con IA sin saber programación: ejemplos de frases cotidianas que cualquier persona puede escribir y cómo la IA auto-detecta la arquitectura, plantillas, reglas y código correcto."
keywords: [lenguaje-natural, no-programadores, prompts-simples, auto-deteccion, ai-prompts]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "13_AI_Rules/AI_WORKFLOW.md"
  - "CHEATSHEET_OPERATIVO.md"
---

# GUÍA DE LENGUAJE NATURAL PARA USUARIOS NO PROGRAMADORES

> 💡 **Objetivo:** No necesitas ser ingeniero de software ni memorizar tecnicismos (Zod, RLS, Webhooks, Idempotency) para construir sistemas con este Handbook. Solo pídele a la IA en español cotidiano y el **Servidor MCP** auto-detectará la arquitectura y los estándares correctos.

---

## 🗣️ Ejemplos de Frases Cotidianas vs. Lo que la IA Ejecuta Automáticamente

| Lo que tú le pides a la IA en palabras simples | Lo que la IA auto-detecta y ejecuta por detrás |
|---|---|
| *"Quiero crear una tienda online para vender ropa y cobrar con tarjeta"* | ➔ Selecciona stack (React/Astro + Supabase + Wompi/Stripe + R2).<br>➔ Aplica regla `MONEY-001` (precios en servidor) y crea webhook seguro. |
| *"Tengo un archivo Excel con 5,000 clientes viejos, mételos a la base de datos"* | ➔ Ejecuta `GUIA_MIGRACION_DATOS_CLIENTE.md`.<br>➔ Genera script en Node con Zod, sanitiza teléfonos y sube en lotes de 500. |
| *"El cliente me pidió un botón nuevo para enviar WhatsApp que no estaba en el contrato"* | ➔ Carga `TEMPLATE_CHANGE_REQUEST.md`.<br>➔ Redacta la orden de cambio con costo adicional y tiempo extra para firma. |
| *"Quiero que los administradores vean todo pero los empleados solo sus ventas"* | ➔ Carga `PATRON_RBAC_PERMISOS.md`.<br>➔ Crea tablas de roles y políticas RLS con helper `has_permission()`. |
| *"¿Cómo le cobro a un cliente por una app y qué le pongo en la propuesta?"* | ➔ Carga `TEMPLATE_PROPUESTA_TECNICA.md`.<br>➔ Genera propuesta formal con 4 hitos y esquema de pago 30/30/20/20. |
| *"Ya terminé la web del cliente, ¿cómo se la entrego para que no me reclame después?"* | ➔ Carga `TEMPLATE_ACTA_ENTREGA_HANDOVER.md`.<br>➔ Checklist de traspaso de cuentas en la nube y activa los 30 días de garantía. |
| *"Se cayó el servidor de pagos o da error al comprar"* | ➔ Carga `WEBHOOK_IDEMPOTENCY_STANDARD.md` e `INCIDENT_RESPONSE.md`.<br>➔ Audita llaves de idempotencia y firmas HMAC. |

---

## ⚡ El Único Prompt que Necesitas Recordar

Si quieres que la IA resuelva cualquier problema en tu proyecto, solo dile:

```text
"Actúa como el equipo técnico de mi agencia. Consulta el MCP del Engineering Handbook y resuelve esto: [Escribe aquí tu petición en tus propias palabras]."
```

La IA llamará a `auto_assist`, encontrará el estándar exacto y programará la solución siguiendo las 10 reglas de oro sin que tengas que preocuparte por los detalles técnicos.
