---
title: "AGENTS.md — Sistema de Decisión Central, Auto-Ruteo y Motor de Auditoría Autónoma"
category: root
doc_type: referencia
tags: [auto-routing, decision-tree, agent-rules, standards, architecture, security, core, trust-hierarchy, audit-scorecard, backlog-generator]
summary: "El cerebro central del Engineering Handbook. Guía de auto-ruteo obligatorio, reglas inquebrantables y checklist de revisión para trabajar de forma segura y consistente."
keywords: [agents.md, decision-tree, auto-routing, ai-rules, inquebrantables, hierarchy, checklist, standards, trust-hierarchy, scorecard, backlog]
updated: 2026-08-05
status: current
---

# AGENTS.md — Sistema de Decisión Central, Auto-Ruteo y Motor de Auditoría Autónoma

> Este documento es la fuente de verdad operativa del handbook. Antes de planear, escribir código o entregar una solución, lee este archivo, identifica el dominio de la tarea, consulta el estándar correcto y aplica las reglas obligatorias.

---

## Regla de oro

1. No escribas código todavía.
2. Clasifica el problema por dominio: base de datos, backend, frontend, seguridad, devops o producto.
3. Abre y lee el estándar específico antes de implementar.
4. Aplica las reglas marcadas como REQUIRED sin omitir validaciones.
5. Verifica la entrega con el checklist corto antes de cerrar la tarea.

---

## Gate de activación antes de implementar

Antes de declarar una funcionalidad lista para producción, la IA debe revisar:

1. [Engineering-OS/32-Operating-Gate.md](Engineering-OS/32-Operating-Gate.md) para perfil, riesgo y evidencia.
2. [Engineering-OS/34-Policy-Profiles.md](Engineering-OS/34-Policy-Profiles.md) para confirmar el perfil aplicable.
3. [Engineering-OS/33-Feature-Completeness-Engine.md](Engineering-OS/33-Feature-Completeness-Engine.md) para completar la matriz de cobertura.
4. [Engineering-OS/35-Rule-Registry.md](Engineering-OS/35-Rule-Registry.md) y [Engineering-OS/36-Validation-Pipeline.md](Engineering-OS/36-Validation-Pipeline.md) para validar reglas y pipeline.

Si la tarea expone una laguna del handbook, detén la implementación, documenta el gap, investiga con la jerarquía de confianza y genera un borrador antes de avanzar.

---

## Mapa rápido de decisión

Usa este mapa para encontrar el estándar correcto:

- Metodología y Flujo: [00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md](00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md) (Spec → Zod → Test → Code → Verify)
- Base de datos: [04_Database/README.md](04_Database/README.md) y [04_Database/DATABASE_ENGINEERING_STANDARD.md](04_Database/DATABASE_ENGINEERING_STANDARD.md)
- Backend y API: [02_Backend/BACKEND_ENGINEERING_STANDARD.md](02_Backend/BACKEND_ENGINEERING_STANDARD.md), [03_API/API_ENGINEERING_STANDARD.md](03_API/API_ENGINEERING_STANDARD.md), [02_Backend/WORKERS_CLOUDFLARE_STANDARD.md](02_Backend/WORKERS_CLOUDFLARE_STANDARD.md), [02_Backend/FIREBASE_ENGINEERING_STANDARD.md](02_Backend/FIREBASE_ENGINEERING_STANDARD.md), [02_Backend/SUPABASE_ENGINEERING_STANDARD.md](02_Backend/SUPABASE_ENGINEERING_STANDARD.md) y [02_Backend/WEBSOCKETS_STANDARD.md](02_Backend/WEBSOCKETS_STANDARD.md)
- Frontend: [01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md](01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md), [01_Frontend/Core/FRONTEND_TAILWIND_V4_STANDARD.md](01_Frontend/Core/FRONTEND_TAILWIND_V4_STANDARD.md) y [01_Frontend/Patterns/PWA_STANDARD.md](01_Frontend/Patterns/PWA_STANDARD.md)
- Calidad de Código: [10_Code_Quality/AGENCY_CODING_STANDARD.md](10_Code_Quality/AGENCY_CODING_STANDARD.md) (Cero falsos 200, Zod en todo input, Clean Code)
- Seguridad: [05_Security/README.md](05_Security/README.md) y [05_Security/SECRET_LEAK_PREVENTION_STANDARD.md](05_Security/SECRET_LEAK_PREVENTION_STANDARD.md)
- DevOps, Cloud y Arquitectura: [07_DevOps/README.md](07_DevOps/README.md), [08_Cloud/README.md](08_Cloud/README.md), [08_Cloud/ESCALABILIDAD_Y_MANTENIMIENTO.md](08_Cloud/ESCALABILIDAD_Y_MANTENIMIENTO.md), [09_Architecture/STACK_SELECTION_MATRIX.md](09_Architecture/STACK_SELECTION_MATRIX.md) y [09_Architecture/MONOREPO_STANDARD.md](09_Architecture/MONOREPO_STANDARD.md)
- Testing & QA de Release: [06_Testing/CHECKLIST_RELEASE_PRODUCCION.md](06_Testing/CHECKLIST_RELEASE_PRODUCCION.md) y [06_Testing/README.md](06_Testing/README.md)
- Sistemas contables y fiscales: [16_Accounting/README.md](16_Accounting/README.md), [16_Accounting/ACCOUNTING_SYSTEMS_STANDARD.md](16_Accounting/ACCOUNTING_SYSTEMS_STANDARD.md), [16_Accounting/ACCOUNTING_POSTING_ENGINE_PATTERN.md](16_Accounting/ACCOUNTING_POSTING_ENGINE_PATTERN.md) y, para Panamá, [16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md](16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md)
- Producto, Clientes e IA: [10_Product/README.md](10_Product/README.md), [10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md](10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md), [12_Documentation/DOCUMENTATION_STANDARD.md](12_Documentation/DOCUMENTATION_STANDARD.md) y [13_AI_Rules/AI_WORKFLOW.md](13_AI_Rules/AI_WORKFLOW.md)

---

## Reglas inquebrantables críticas

| ID | Regla | Nota |
|---|---|---|
| DB-001 | No usar SELECT * | Especificar columnas explícitas |
| DB-002 | Toda FK debe tener índice secundario | Evitar cuellos de botella |
| DB-008 | No usar float/double para dinero | Usar bigint o centavos |
| S-001 | Todo payload debe validarse con Zod | Frontend y backend |
| S-005 | No usar CORS wildcard en entornos autenticados | Seguridad primero |
| FE-001 | No usar any en TypeScript | Usar unknown y estrechar tipos |
| FE-005 | Todo componente async debe manejar Loading, Empty, Error y Success | Estados UI obligatorios |
| MONEY-001 | Los precios no se definen en el frontend | El backend resuelve monto y priceId |
| AUTH-003 | Magic links con TTL máximo de 15 min y un solo uso | Seguridad de acceso |
| AUTH-004 | Invitaciones de equipo con TTL 48h, token revocable y rate-limit | Excepción controlada |
| SEC-001 | CSP estricta en todas las respuestas HTTP | Evitar XSS y ejecución insegura |
| SEC-002 | Cero secretos en bundles de cliente (Vite/APK/Tauri) | APIs privadas siempre por backend proxy |
| TENANT-001 | RLS es la fuente de verdad para aislamiento multi-tenant | No bypass de capa |
| TEST-001 | Bugs P0/P1 y seguridad exigen test de regresión | Prueba automatizada obligatoria antes de cerrar fix |
| FE-009 | Cero pill badges flotantes sobre H1 y cero vanity metrics ficticias | Prohibido en landings: no va NUNCA salvo pedido explícito del usuario |
| FE-010 | Diversidad de componentes y cero fatiga de cards | Prohibido encapsular toda la UI en cards, hamburguesa y aside; usar taxonomía completa de FRONTEND_UI_PATTERNS.md |
| ACC-001 | Todo asiento contable cuadra exactamente (débitos = créditos en centavos) | Validado en el servidor; ver 16_Accounting |
| ACC-007 | Lo contabilizado no se edita ni se borra | Corregir con reverso o nota de crédito |
| ACC-010 | Documento + asiento + saldos + auditoría en una operación atómica | Prohibido silenciar errores de contabilización |
| ACC-016 | Cero códigos de cuenta contable en el código fuente | Cuentas por defecto configurables por empresa |

---

## Lo que una IA nunca debe hacer

- Colocar pill badges flotantes sobre el `<h1>` (chips tipo "[Award] AVAL...") o filas de métricas ficticias (+1,800 egresadas, 99.2%): **esto es obligatorio, no va NUNCA a menos de que el usuario lo pida explícitamente**.
- Diseñar interfaces homogéneas metiendo todo en cards repetitivas, menú hamburguesa y aside por defecto: diversificar usando el sistema completo de componentes (tabs, acordeones, drawers, sheets, tablas, timelines, steppers, etc.).
- Inventar librerías, patrones o configuraciones que no pertenezcan al stack oficial.
- Usar any en TypeScript o desactivar strict mode.
- Usar SELECT * o crear FK sin índice secundario.
- Silenciar errores con try/catch vacíos o devolver 200 OK falsos.
- Enviar PII o datos sensibles a modelos externos sin anonimización.
- Basar decisiones en blogs personales o tutoriales como fuente principal.

---

## Lo que una IA siempre debe hacer

- Consultar este archivo antes de actuar.
- Leer el estándar relevante antes de implementar.
- Aplicar las reglas REQUIRED del dominio.
- Estandarizar respuestas API con ok() y fail().
- Usar React Query para fetching y evitar useEffect descontrolado para mutaciones.
- Mantener naming consistente: snake_case en DB y camelCase en TypeScript.

---

## Checklist corto de entrega

- [ ] Consulté el estándar correcto para el dominio.
- [ ] Apliqué las reglas REQUIRED y no omití validaciones.
- [ ] El código cumple con TypeScript estricto y sin any indebido.
- [ ] Los datos de entrada están validados con Zod.
- [ ] Si el componente es async, maneja Loading, Empty, Error y Success.
- [ ] Las respuestas API siguen el envelope estándar.
- [ ] Incluí pruebas para el flujo exitoso y los casos de error.
- [ ] Si hubo cambios de base de datos, preparé migración y rollback.

---

## Jerarquía de confianza

Cuando no exista una guía en el handbook, la investigación debe seguir este orden de prioridad:

1. Handbook propio.
2. Especificaciones oficiales y estándares formales.
3. Documentación oficial de la tecnología.
4. Marcos de seguridad y estándares reconocidos.
5. Fuentes de comunidad, solo como apoyo secundario.

Evita usar blogs personales, Medium o tutoriales como única fuente.

---

## Auditoría y calidad del handbook

Si una tarea modifica documentación del handbook, debe verificar el estado del repositorio con:

```bash
npm run lint
```

El lint valida patrones bloqueantes como SELECT *, any, CORS wildcard, JWT en localStorage, CSP inseguro y HTML crudo en correos.

Cuando falte cobertura, emite una estructura formal de missing_document y, si aplica, un draft_document con impacto, fuentes y reglas afectadas antes de avanzar.
