---
title: "Estándar de Requisitos de Producto (PRD) para Ingeniería e IA"
category: 10_Product
doc_type: estandar
tags: [product, prd, rice, user-stories, kpi, north-star, backlog]
summary: "Estándar para la definición de requisitos de producto (PRDs): plantilla estructurada para interpretación por agentes IA, matriz de priorización RICE, User Story Mapping y definición de métricas North Star."
keywords: [prd, product, rice, user-story, user-story-mapping, north-star, kpi, backlog, requirements]
updated: 2026-07-27
status: current
---

# 🎯 ESTÁNDAR DE REQUISITOS DE PRODUCTO (PRD)

> **Objetivo:** Definir una metodología clara e inequívoca para redactar Requisitos de Producto (PRDs) que permitan a desarrolladores y agentes de IA implementar features con **cero ambigüedad**, alineados con objetivos de negocio medibles.

---

## 🎯 LAS 5 REGLAS INQUEBRANTABLES DE PRODUCTO

1. **[REQUIRED] Ninguna feature se codifica sin un PRD previo** que responda el *Problema*, los *Criterios de Aceptación* y el *Modelo de Datos*.
2. **[REQUIRED] Todos los PRD deben incluir Criterios de Aceptación verificables** en formato de checklist `[ ]`.
3. **[REQUIRED] Las prioridades se evalúan con el puntaje RICE.** No se prioriza por capricho ni "sensación".
4. **[REQUIRED] Toda funcionalidad nueva define su métrica de impacto** (North Star o KPI secundario).
5. **[REQUIRED] Los PRD especifican los 4 estados de UI** (Loading, Empty, Error, Success) para orientar el desarrollo frontend.

---

## 📄 1. PLANTILLA DE PRD (PRODUCT REQUIREMENTS DOCUMENT)

**[REQUIRED]** Estructura estándar a utilizar para proponer e implementar cualquier nueva funcionalidad:

```markdown
# PRD: [Nombre de la Feature / Módulo]

## 🎯 1. Problema de Negocio
[1-2 frases descriptivas: ¿Qué problema real experimenta el usuario? ¿Qué ineficiencia o dolor resuelve?]

## 🎯 2. Objetivo y Métrica de Éxito
- **Objetivo Principal**: [Ej: "Reducir el tiempo de creación de propuestas de 15 minutos a menos de 2 minutos."]
- **Métrica Clave (KPI)**: [Ej: "Aumentar la tasa de conversión de propuestas enviadas en un 25%."]

## 👤 3. Usuarios y Caso de Uso
- **Arquetipo Principal**: Freelancer / Administrador de Equipo
- **Frecuencia de Uso**: Diaria / Varias veces por semana
- **Contexto**: El usuario necesita generar un documento profesional mientras está en una llamada con un cliente.

## 🏗️ 4. Requisitos Funcionales

### RF-001: Crear documento desde plantilla predefinida
- **Prioridad**: P0 (Crítico / MVP)
- **Descripción**: El usuario selecciona una plantilla del catálogo y el sistema genera la estructura inicial.
- **Criterios de Aceptación**:
  - [ ] El catálogo muestra al menos 3 plantillas base.
  - [ ] Al hacer clic en "Usar plantilla", se crea un documento nuevo en estado `draft`.
  - [ ] El título por defecto es "[Nombre Plantilla] - [Fecha actual]".
  - [ ] El tiempo de generación en pantalla es < 500ms.

### RF-002: Enviar propuesta por correo electrónico
- **Prioridad**: P0 (Crítico / MVP)
- **Descripción**: Permite enviar el enlace público del documento al cliente final por correo.
- **Criterios de Aceptación**:
  - [ ] El modal de envío requiere el correo del destinatario y un mensaje opcional.
  - [ ] El correo se procesa asíncronamente vía `NOTIF_QUEUE` (`NOTIFICATIONS_STANDARD.md`).
  - [ ] Se utiliza la plantilla React Email `invitation` / `notification`.
  - [ ] El sistema registra el evento en `activity_log`.

---

## 🔒 5. Requisitos No Funcionales
- **Rendimiento**: Carga de la vista inicial en < 300ms (LCP).
- **Seguridad**: RLS habilitado en la base de datos (`DATABASE_ENGINEERING_STANDARD.md`). Accesos públicos vía token UUID indivinable.
- **Accesibilidad**: Cumplimiento WCAG 2.1 Nivel AA.
- **Internacionalización**: Todos los textos extraídos a namespaces i18n (`FRONTEND_I18N_STANDARD.md`).

---

## 🗄️ 6. Modelo de Datos Afectado
- **Tablas a crear/modificar**: `documents`, `document_versions`
- **Campos principales**: `public_token UUID`, `status doc_status`
- **Reglas RLS**: Lectura pública permitida únicamente si `is_public = TRUE` y el `public_token` coincide.

---

## ⚙️ 7. Contrato de API
- `POST /api/v1/documents` — Crea un documento nuevo
- `GET /api/v1/documents/:id` — Obtiene el detalle del documento
- `POST /api/v1/documents/:id/publish` — Genera el token de acceso público

---

## 🎨 8. Especificación de UI/UX
- **Estados de Interfaz obligatorios**:
  - **Loading**: Skeleton animado de 3 filas.
  - **Empty**: Ilustración + mensaje "No tienes documentos creados. Empieza con una plantilla." + CTA primario.
  - **Error**: Banner de alerta de peligro con botón "Reintentar".
  - **Success**: Grid de tarjetas de documentos.

---

## 🧪 9. Plan de Pruebas y Validación
- [ ] **Unit Testing**: Validar schemas de Zod con datos válidos e inválidos.
- [ ] **Integration**: Probar flujo de creación y encolado de correo en el Worker.
- [ ] **RLS Testing**: Verificar que el Usuario B no pueda leer documentos del Usuario A.
```

---

## 📊 2. MATRIZ DE PRIORIZACIÓN RICE

Para decidir qué construir primero en el backlog, se calcula el **RICE Score**:

$$\text{RICE Score} = \frac{\text{Reach (Alcance)} \times \text{Impact (Impacto)} \times \text{Confidence (Confianza \%)}}{\text{Effort (Esfuerzo Personas-Semana)}}$$

### Escala de Medición:
- **Reach (Alcance)**: Número de usuarios impactados por mes.
- **Impact (Impacto)**: `3` = Masivo, `2` = Alto, `1` = Moderado, `0.5` = Bajo.
- **Confidence (Confianza)**: `100%` = Datos comprobados, `80%` = Basado en métricas, `50%` = Hipótesis.
- **Effort (Esfuerzo)**: Semanas de trabajo de 1 desarrollador (`1`, `2`, `4`, `8`).

### Ejemplo de Matriz RICE:

| Feature / Funcionalidad | Reach | Impact | Confidence | Effort | RICE Score | Prioridad |
|---|---|---|---|---|---|---|
| Plantillas de propuesta | 1,000 | 3 | 80% | 2 | **1,200** | 🔴 P0 (Ahora) |
| Exportación a PDF en Edge | 800 | 2 | 90% | 2 | **720** | 🟡 P1 (Siguiente) |
| Firma digital con dibujo | 300 | 3 | 50% | 4 | **112.5** | 🟢 P2 (Backlog) |
| Integración con Notion | 100 | 1 | 50% | 3 | **16.6** | ⚪ Descartado |

---

## 🗺️ 3. USER STORY MAPPING TEMPLATE

El **User Story Map** organiza el backlog en dos dimensiones: el flujo del usuario (horizontal) y la profundidad de entrega (vertical por versiones).

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│ BACKBONE (Actividades del Usuario)                                              │
├──────────────┬──────────────────┬─────────────────┬──────────────┬──────────────┤
│ 1. Onboarding│ 2. Creación      │ 3. Edición      │ 4. Envío     │ 5. Cobro     │
├──────────────┴──────────────────┴─────────────────┴──────────────┴──────────────┤
│ WALKING SKELETON (MVP - Versión 1.0)                                           │
│ • Registro   │ • Documento en   │ • Editor texto  │ • Enlace     │ • Integración│
│   email/pass │   blanco         │   básico        │   público    │   Stripe     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 2 (Mejora de UX y Retención)                                          │
│ • OAuth      │ • Plantillas     │ • Markdown /    │ • Enviar por │ • Facturas   │
│   Google/GH  │   predefinidas   │   TipTap WYSIWYG│   email      │   en PDF     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ITERACIÓN 3 (Colaboración Avanzada)                                             │
│ • Roles      │ • Importar       │ • CRDTs / Yjs   │ • Push Notif │ • Pagos      │
│   RBAC       │   archivos .md   │   tiempo real   │   y VAPID    │   recurrentes│
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 4. MÉTRICAS DE PRODUCTO (NORTH STAR & KPIS)

Toda feature debe estar conectada con la salud global del producto.

### 4.1 North Star Metric (La estrella guía)
La métrica única que mejor captura el valor entregado al usuario:

> **North Star de CollabScribe:** *"Documentos colaborativos creados y exportados por semana"*

### 4.2 Tablero de KPIs por etapa del Embudo

| Etapa | KPI | Objetivo |
|---|---|---|
| **Adquisición** | Visitas a Landing → Signups | Tasa de conversión > 8% |
| **Activación** | Usuarios que crean su 1er doc en < 24h | > 65% de nuevos registros |
| **Retención** | Retención de usuarios D30 (30 días) | > 40% de la cohorte |
| **Monetización** | Conversión Free → Plan Pro | > 5% de usuarios activos |
| **Referencia** | Invitaciones enviadas a compañeros | > 1.5 invitaciones/usuario |
