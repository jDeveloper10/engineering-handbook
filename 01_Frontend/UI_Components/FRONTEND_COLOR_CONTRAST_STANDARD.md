---
title: "Estándar de Color y Contraste (Dark y Light Mode)"
category: 01_Frontend
doc_type: estandar
tags: [frontend, color, contraste, dark-mode, wcag]
summary: "Tokens de color por rol en lugar de colores sueltos, construcción de light y dark mode, contraste mínimo exigido por WCAG y paleta semántica de estados."
keywords: [color, contraste, wcag, dark-mode, light-mode, tokens, paleta]
updated: 2026-07-27
status: current
---

# FRONTEND COLOR & CONTRAST STANDARD (Dark Mode / Light Mode)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, secciones 1.2 y 1.9) y de [FRONTEND_ACCESSIBILITY_STANDARD.md](FRONTEND_ACCESSIBILITY_STANDARD.md) (sección 6, contraste). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> [FRONTEND_UI_STYLE_CATALOG.md](FRONTEND_UI_STYLE_CATALOG.md) da el punto de partida visual (qué paleta usar según el estilo elegido); este documento define las **reglas** con las que cualquier paleta —la del catálogo o una nueva— se construye y valida antes de usarse.

---

## 1. Regla principal

**[REQUIRED]** La paleta se construye por jerarquía visual, legibilidad y contraste — nunca se eligen colores solo por estética. Todo sistema de color valida explícitamente estos roles antes de darse por terminado: fondo, superficies, texto principal, texto secundario, bordes, estados (hover/activo/error/éxito), componentes interactivos.

---

## 2. Tokens por rol, no colores sueltos

**[REQUIRED]** Ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` 1.2 — se piensa en el rol del color, no en el hexadecimal. Set de tokens de referencia mínimo:

```
--bg-primary       --bg-secondary      --surface-card
--text-primary     --text-secondary    --text-disabled
--border-color      --brand-primary
--success           --warning           --error           --info
```

```
❌ background: #121212; button: #ff5500; text: white;
✅ background: var(--bg-primary); button: var(--brand-primary); text: var(--text-primary);
```

**Por qué:** un color suelto repetido en 40 componentes obliga a buscar y reemplazar 40 veces si cambia; un token cambia en un solo lugar.

---

## 3. Light Mode

**[RECOMMENDED]** Fondo principal claro pero no necesariamente blanco puro (`#FFFFFF`, `#F8FAFC`, `#F5F5F5` son válidos, elegido según cuánto "peso" se quiere en la superficie base).

**[REQUIRED]** Jerarquía de texto con contraste real, no solo tonos que "se ven bien":

| Rol | Uso | Contraste mínimo | Ejemplo |
|---|---|---|---|
| Texto primario | Títulos, información importante | 4.5:1 | `#111827` sobre blanco |
| Texto secundario | Descripciones, metadata | 4.5:1 (texto normal) o 3:1 si es grande | `#6B7280` sobre blanco |
| Texto disabled | Elementos deshabilitados | Debe leerse como "apagado" pero seguir siendo legible, no invisible | `#9CA3AF` |

**[RECOMMENDED]** Superficies (cards, modales, dropdowns) sobre fondo claro se diferencian con sombra suave + borde ligero, no solo con un blanco idéntico al fondo.

---

## 4. Dark Mode

**[REQUIRED]** Nunca negro puro (`#000000`) como fondo principal.

**Por qué:** el contraste máximo absoluto (blanco puro sobre negro puro) produce fatiga visual en sesiones largas y hace que cualquier diferencia de superficie sea invisible — todo se ve "igual de negro". Se usa un navy/gris muy oscuro (`#0F172A`, `#111827`, `#121212`).

**[REQUIRED]** Las superficies (cards) suben de luminosidad respecto al fondo, con diferencia perceptible:

```
Background: #0F172A
Card:       #1E293B   ← visiblemente más clara que el fondo, no el mismo tono
```

**[REQUIRED]** El texto principal en dark mode tampoco es blanco puro:

```
❌ #FFFFFF
✅ #F8FAFC
```

**Validación con lo ya construido en este handbook:** los tests de TradePulse (`pruebas/test_login_standard.html`, `test_dashboard_standard.html`) ya siguen esta regla sin que estuviera escrita todavía — `bg-deep #0b1220` / `bg-base #0f172a` / `bg-card #131f35` (tres niveles de superficie ascendente) y `ink-50 #f8fafc` como "blanco" de texto, nunca `#ffffff` puro. Esta sección formaliza lo que ya se venía haciendo bien.

---

## 5. Contraste obligatorio (WCAG)

**[REQUIRED]** — mismos números de `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 6, aplicados específicamente a la construcción de la paleta:

| Elemento | Contraste mínimo |
|---|---|
| Texto normal | 4.5:1 |
| Texto grande (≥18px, o ≥14px bold) | 3:1 |
| Componentes UI (bordes de input, iconos con significado, botones) | 3:1 |

La fila de "Componentes UI" es la que más se olvida — no solo el texto necesita contraste, un borde de input o un ícono de estado también, o se vuelven invisibles para usuarios con baja visión.

---

## 6. Paleta semántica

**[REQUIRED]** Los colores de estado se asignan por significado, no por convención estética suelta ("rojo porque sí"):

| Rol | Significado | Ejemplo |
|---|---|---|
| `success` | Confirmaciones, operaciones correctas | Verde — `#16a34a` / `#22c55e` |
| `warning` | Advertencias, algo requiere atención sin ser crítico | Ámbar — `#d97706` / `#f59e0b` |
| `error` / `danger` | Errores críticos, acciones destructivas | Rojo — `#dc2626` / `#ef4444` |
| `info` | Información neutral | Azul — `#3b82f6` |

Los valores exactos son intercambiables dentro de la misma familia semántica (ya se usó `#16a34a`/`#dc2626`/`#d97706` como ejemplo en `FRONTEND_ENGINEERING_STANDARD.md` 1.2) — lo que no se negocia es que cada rol tenga un significado fijo y consistente en todo el proyecto, nunca reasignado componente por componente.

---

## 7. Colores de marca — proporción

**[RECOMMENDED]** Regla heurística de proporción (no una ley matemática exacta, pero un punto de partida sólido): **~70% neutros, ~20% superficies/secundarios, ~10% color de marca.**

```
70%  fondo, texto, bordes (neutros)
20%  superficies secundarias, estados
10%  color de marca (CTAs, links, acentos)
```

**Por qué:** el color de marca pierde impacto si está en todas partes — reservarlo para lo que realmente quiere destacar (CTA primario, links, acentos puntuales) es lo que lo hace notorio cuando aparece.

---

## 8. Estados de componentes

**[REQUIRED]** Cada componente interactivo define sus estados con reglas de color consistentes — ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` 1.6 (estados visuales obligatorios); esta sección da la mecánica de color:

**Button:**
```
Default:   color de marca (--brand-primary)
Hover:     +10% luminosidad aprox.
Active:    -10% luminosidad aprox.
Disabled:  opacidad 40-50%, nunca un color totalmente distinto
```

**Input:**
```
Default:   borde neutral (--border-color)
Focus:     borde con --brand-primary + anillo de foco (focus-visible)
Error:     borde --error + mensaje asociado (ver FRONTEND_ENGINEERING_STANDARD.md 9.4)
Success:   borde --success (cuando aplica validación en tiempo real, ver FRONTEND_AUTH_PATTERNS.md sección 7)
```

---

## 9. Selector de tema: Light / Dark / Sistema

**[REQUIRED]** Ya exigido en `FRONTEND_ENGINEERING_STANDARD.md` 1.9 (estrategia por clase con toggle explícito). **[RECOMMENDED]** el selector ofrece 3 opciones, no 2: `Claro`, `Oscuro`, `Sistema` (sigue `prefers-color-scheme` del SO). La opción "Sistema" es el default sensato — respeta la preferencia del usuario sin que tenga que configurar nada, y sigue siendo overrideable manualmente.

---

## 10. Sombras y profundidad por modo

**[RECOMMENDED]** La sombra no comunica profundidad igual en los dos modos:

- **Light mode:** sombras más presentes (`shadow-md`, `shadow-lg`) — funcionan porque hay un fondo claro contra el que proyectar.
- **Dark mode:** sombras oscuras sobre fondo ya oscuro casi no se perciben. La profundidad se comunica mejor con **bordes sutiles** y **diferencia de luminosidad de superficie** (sección 4), no con sombra.

```
Dark mode:
Card:   #1E293B
Border: rgba(255,255,255,0.08)
```

---

## 11. Anti-patrones

- ❌ Colores hexadecimales sueltos repetidos en componentes en vez de tokens por rol.
- ❌ Negro puro (`#000000`) como fondo de dark mode.
- ❌ Blanco puro (`#FFFFFF`) como texto principal en dark mode.
- ❌ Card con el mismo tono exacto que el fondo (sin diferencia de superficie perceptible).
- ❌ Asignar rojo/verde/amarillo a un estado sin relación real con su significado semántico establecido.
- ❌ Color de marca usado en más del ~10-15% de la superficie visible, diluyendo su impacto.
- ❌ Sombra pesada como única forma de mostrar elevación en dark mode.
- ❌ Selector de tema con solo Claro/Oscuro, sin opción "Sistema".

---

## Checklist rápido

- [ ] ¿Paleta construida por rol (tokens), no por hex sueltos?
- [ ] ¿Fondo de dark mode es navy/gris oscuro, no negro puro; texto es `#F8FAFC`-like, no blanco puro?
- [ ] ¿Superficies (cards) con diferencia de luminosidad perceptible respecto al fondo?
- [ ] ¿Contraste validado: 4.5:1 texto normal, 3:1 texto grande y componentes UI?
- [ ] ¿Colores semánticos (success/warning/error/info) consistentes en todo el proyecto?
- [ ] ¿Color de marca reservado a ~10% de la superficie, no repartido por todas partes?
- [ ] ¿Cada componente interactivo define default/hover/active/focus/disabled/error con reglas de color claras?
- [ ] ¿Selector de tema incluye Sistema, no solo Claro/Oscuro?
