---
title: "FRONTEND OFFLINE STANDARD"
category: 01_Frontend
doc_type: estandar
tags:
  - standards
  - conventions
  - offline
  - sync
summary: "Nivel 2 del dominio Frontend. Define la estrategia offline-first para PWAs o aplicaciones con requisitos de disponibilidad sin conexión."
keywords:
  - offline
  - dexie
  - indexeddb
  - sync
  - pwa
updated: 2026-07-27
status: current
---

# FRONTEND OFFLINE STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).

---

## 1. Estrategia Offline-First

**[REQUIRED]** Cuando la aplicación (o parte de ella) requiere funcionar sin conexión a internet de manera transparente (ej: recolectores en campo, modo lectura en vuelo), el diseño es *Offline-First*.

### Stack:
- **Dexie.js** (wrapper IndexedDB) para datos locales relacionales.
- **Service Worker** (Workbox) para cachear assets estáticos y shell de la app.
- **Sincronización con Supabase Realtime** al detectar reconexión.

---

## 2. Manejo de colecciones grandes (ej: 10k registros)

**[REQUIRED]** Para manejar listados masivos que deben estar disponibles offline:

1. **Primera carga:** Fetch inicial a la API → Guardar en Dexie.
2. **Siguientes cargas:** Leer siempre desde Dexie local (latencia de 0ms).
3. **Filtros/orden:** Hacerse directamente contra Dexie (soporta índices rápidos). No depender del backend para el filtrado.
4. **Al reconectar:** Hacer diff entre local y remoto (sync bidireccional en background).

---

## 3. Conflictos de estado y Sincronización

**[REQUIRED]** La política de resolución de conflictos debe estar definida antes de permitir escrituras offline:

- **Estrategia por defecto:** "Last Write Wins" (Gana la última escritura) basándose en un `updated_at` (timestamp UTC).
- **Si el conflicto es crítico** (ej: dos usuarios editaron la misma factura en offline): Se asigna un flag `needs_review: true` y la UI debe renderizar un banner alertando al usuario para que resuelva manualmente.

## Checklist rápido

- [ ] ¿Los datos viven en Dexie.js como fuente de verdad local para las lecturas?
- [ ] ¿Los filtros y ordenamiento sobre miles de filas ocurren en IndexedDB usando índices, no iterando arrays en memoria?
- [ ] ¿Hay un estado visual que indique al usuario que está en modo offline?
- [ ] ¿La resolución de conflictos usa timestamps UTC o deriva en revisión manual explícita?
