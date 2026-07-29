---
title: "Estándar de Microcopy y UX Writing"
category: 01_Frontend
tags: [frontend, microcopy, ux-writing, tono]
summary: "Tono consistente en todo el producto, glosario de un concepto una palabra, capitalización de botones y etiquetas, redacción de CTAs y límites de longitud y puntuación."
keywords: [microcopy, ux-writing, tono, glosario, cta, capitalizacion]
updated: 2026-07-27
status: current
---

# FRONTEND MICROCOPY / UX WRITING STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, sección 3.2 — código en inglés, contenido en español). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Es la continuación natural de la sección 3.2: ese punto dice *en qué idioma* se escribe el contenido; este documento dice *cómo* se escribe dentro de ese idioma — tono, terminología, capitalización, consistentes en todo el producto.

---

## 1. Regla principal

**[REQUIRED]** Todo el copy visible al usuario sigue un tono y una terminología únicos en todo el producto — no se decide palabra por palabra ni pantalla por pantalla.

---

## 2. Tono: tuteo, consistente en todo el producto

**[REQUIRED]** Se elige tuteo ("tú") o formal ("usted") una vez, para todo el producto — nunca mezclado en la misma pantalla ni entre pantallas distintas.

**[RECOMMENDED]** Tuteo por defecto para productos consumer/prosumer en el mercado LatAm (más cercano, natural para SaaS) — formal solo si el producto es explícitamente B2B enterprise o para un sector donde se espera formalidad (gobierno, salud regulada).

```
❌ "Inicia sesión para ver tus señales" ... "Complete el formulario para continuar"
✅ "Inicia sesión para ver tus señales" ... "Completa el formulario para continuar"
```

---

## 3. Glosario de términos — un concepto, una palabra

**[REQUIRED]** Cada concepto del producto tiene **un solo nombre**, usado siempre igual en toda la interfaz — nunca dos sinónimos para lo mismo.

```
❌ "Señal" en el dashboard, "Alerta" en las notificaciones, "Aviso" en el email — los tres refiriéndose a lo mismo
✅ "Señal" en todos lados
```

**[RECOMMENDED]** Mantener un glosario vivo por proyecto (una tabla simple: término → definición → dónde se usa) — el punto de referencia para cualquiera (humano o IA) que agregue una pantalla nueva.

---

## 4. Capitalización de botones y labels

**[REQUIRED]** Sentence case (solo la primera palabra con mayúscula) en botones, labels y títulos de UI — no Title Case (Cada Palabra En Mayúscula), que es un anglicismo tipográfico ajeno al español.

```
❌ "Crear Cuenta Nueva"
✅ "Crear cuenta nueva"
```

---

## 5. CTAs

Ver `FRONTEND_LANDING_PATTERNS.md` sección 4.3 — verbo de acción + beneficio, nunca genérico ("Enviar", "Click aquí"). Esta regla no es solo de landing, aplica a cualquier CTA del producto.

---

## 6. Longitud y puntuación

**[RECOMMENDED]** Botones y labels cortos (2-4 palabras) — descripciones, ayudas y mensajes de error pueden ser más largos cuando lo ameritan. **[RECOMMENDED]** sin punto final en labels/botones cortos; sí en oraciones completas (mensajes de error, descripciones).

---

## 7. Mensajes de error y estados

Cubierto en detalle en `FRONTEND_ENGINEERING_STANDARD.md` sección 6.3, `FRONTEND_AUTH_PATTERNS.md` sección 9, y `FRONTEND_STATES_PATTERNS.md` sección 5 — sin jerga técnica, accionables. Este documento no lo repite, solo confirma que el tono (sección 2) y el glosario (sección 3) aplican igual ahí.

---

## 8. Anti-patrones

- ❌ Mezclar tú/usted en la misma pantalla o entre pantallas del mismo producto.
- ❌ El mismo concepto con dos nombres distintos según la pantalla.
- ❌ Title Case En Cada Botón De La Interfaz.
- ❌ CTA genérico ("Enviar", "Click aquí", "Más información").
- ❌ Mensaje de error con jerga técnica o código crudo (ya cubierto en otros documentos, se repite el error si no se sigue el glosario/tono acá).

---

## Checklist rápido

- [ ] ¿Tuteo o formal, el mismo en todo el producto, sin mezclar?
- [ ] ¿Cada concepto tiene un único nombre en toda la interfaz?
- [ ] ¿Sentence case en botones/labels, no Title Case?
- [ ] ¿CTAs con verbo de acción + beneficio, no genéricos?
- [ ] ¿Longitud apropiada según el tipo de texto (corto en botones, más largo en ayudas)?
