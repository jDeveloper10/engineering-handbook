---
title: "Patrones de Notificaciones en Interfaz"
category: 01_Frontend
tags: [frontend, notificaciones, toast, accesibilidad]
summary: "Cuándo corresponde un toast, un banner, un badge o un centro de notificaciones, según si la información requiere acción inmediata, y sus requisitos de accesibilidad."
keywords: [toast, banner, badge, centro-notificaciones, aria-live, accesibilidad]
updated: 2026-07-27
status: current
---

# FRONTEND NOTIFICATIONS PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Contrastado contra Material Design y Nielsen Norman Group (interrupciones y jerarquía de urgencia).

---

## 1. Regla principal

**[REQUIRED]** El canal de notificación se elige según urgencia y persistencia necesaria, no todo se resuelve con un toast:

```
¿Requiere acción inmediata del usuario antes de continuar?
  Sí → Modal (bloqueante, ver FRONTEND_MODALS_PATTERNS.md)
  No → ¿Debe seguir visible hasta que el usuario la resuelva o la cierre?
         Sí → Banner (persistente, a nivel de página/app)
         No → Toast (transitorio, se auto-descarta)
¿Es solo un contador pasivo de algo pendiente de revisar?
  → Badge
```

---

## 2. Toast

**[REQUIRED]** Posición consistente en todo el producto — típicamente esquina superior o inferior derecha en desktop, ancho completo arriba o abajo en mobile. **[RECOMMENDED]** auto-dismiss ~4-6 segundos para éxito/info; los toasts de error no se auto-descartan solos, o usan un tiempo notablemente mayor — el usuario debe alcanzar a leerlos. **[REQUIRED]** el usuario siempre puede cerrar un toast manualmente, sin depender del auto-dismiss.

**[RECOMMENDED]** Máximo ~3 toasts visibles simultáneamente; el resto se encola.

---

## 3. Banner

**[RECOMMENDED]** Para avisos persistentes a nivel de página o de toda la app (ej. "Tu plan vence en 3 días", "Estás en modo de solo lectura"). Dismissible si no es crítico; si es crítico, permanece hasta que se resuelva la condición que lo generó.

---

## 4. Badge

**[REQUIRED]** Contador pasivo (ej. notificaciones no leídas en un ícono de navegación). **[REQUIRED]** no mostrar el número exacto cuando supera un umbral razonable (ej. "99+" en vez de "1,204") — el número exacto deja de aportar información útil pasado cierto punto.

---

## 5. Centro de notificaciones

**[RECOMMENDED]** Un panel/dropdown con historial de notificaciones se justifica cuando el producto genera notificaciones frecuentes que el usuario querría revisar después (no solo en el momento). Si las notificaciones son raras o siempre urgentes, un toast simple es suficiente y un centro de notificaciones es complejidad sin uso real.

---

## 6. Accesibilidad

**[REQUIRED]** `aria-live="polite"` para notificaciones informativas/de éxito (no interrumpen al lector de pantalla), `aria-live="assertive"` solo para errores críticos que requieren atención inmediata — mismo patrón ya usado en `FRONTEND_AUTH_PATTERNS.md`.

---

## 7. Anti-patrones

- ❌ Toast de error que se auto-cierra en 3 segundos, igual que uno de éxito.
- ❌ Todo tipo de aviso (éxito, error, promoción, recordatorio) usando el mismo canal sin jerarquía.
- ❌ Más de 3-4 toasts apilados simultáneamente compitiendo por atención.
- ❌ Badge mostrando un número de 4 dígitos exacto.
- ❌ `aria-live="assertive"` en notificaciones triviales, interrumpiendo al usuario de lector de pantalla sin necesidad.

---

## Checklist rápido

- [ ] ¿Canal elegido según urgencia/persistencia (árbol de la sección 1), no todo como toast?
- [ ] ¿Toasts de error visibles más tiempo o no auto-dismiss, siempre cerrables manualmente?
- [ ] ¿Máximo ~3 toasts simultáneos, resto en cola?
- [ ] ¿Badge trunca números grandes ("99+")?
- [ ] ¿`aria-live` correcto según criticidad?
