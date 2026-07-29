# ENGINEERING HANDBOOK — Formato y convenciones

> Este documento define **cómo está escrito** cada estándar del handbook, no reglas de código. Se lee una sola vez y se aplica a todos los dominios (`01_Frontend`, `02_Backend`, ...). Cualquier documento nuevo que se agregue al handbook sigue estas convenciones.

---

## 1. Toda regla es REQUIRED o RECOMMENDED

No hay reglas "sueltas". Cada regla del handbook está etiquetada:

- **REQUIRED** — no negociable. Si el código no la cumple, no está terminado. Una IA no debe generar código que la rompa salvo que el usuario lo pida explícitamente y por escrito en esa conversación.
- **RECOMMENDED** — el default esperado, pero puede haber una razón de contexto válida para desviarse (rendimiento medido, restricción del cliente, deadline). Cuando se desvía, se justifica en un comentario corto, no se omite en silencio.

Esto existe para que una IA sepa qué puede negociar y qué no. "Componentes bien organizados" es una opinión; "REQUIRED: un componente = una responsabilidad, máximo ~200 líneas" es una regla verificable.

## 2. Toda regla se escribe en dos capas: agnóstica + implementación

**Capa 1 — la regla (agnóstica de framework/librería).** Se expresa en unidades universales: píxeles, porcentajes, número de palabras, tiempo, sí/no. Nunca en clases de una librería específica.

**Capa 2 — implementación de referencia.** Un ejemplo concreto en el stack actual (React + Tailwind + TypeScript), etiquetado explícitamente como *implementación*, no como *la regla*.

```
❌ Mezclado (la regla y Tailwind son la misma cosa):
"Usa py-16 en mobile, py-24 en tablet, py-32 en desktop."

✅ Separado:
REGLA: El padding vertical de una sección va en 64px (mobile) / 96px (tablet) / 128px (desktop).
IMPLEMENTACIÓN (Tailwind): py-16 md:py-24 lg:py-32
```

Por qué importa: si mañana el stack cambia (Next.js, CSS Modules, otro framework), la regla sigue siendo válida — solo cambia la capa 2. La capa 1 es la que vive en este handbook a largo plazo; la capa 2 es reemplazable.

## 3. Los números son objetivos, no leyes arbitrarias

Ningún número aparece sin la razón que lo sostiene. En vez de "imagen <200KB" (que puede quedar obsoleto o parecer arbitrario), se escribe: "optimizar para cumplir Core Web Vitals (LCP <2.5s); como referencia práctica hoy, eso suele significar hero <200KB." El objetivo real (Core Web Vitals, legibilidad, accesibilidad AA) es la regla; el número es la heurística actual para lograrlo, y puede recalibrarse sin romper el estándar.

## 4. Jerarquía de especialización — 3 niveles

```
Nivel 1: Estándar de dominio       (ej. FRONTEND_ENGINEERING_STANDARD.md)
              ↓ aplica siempre, en todo proyecto de ese dominio
Nivel 2: Estándar de patrón        (ej. FRONTEND_LANDING_PATTERNS.md)
              ↓ agrega reglas para un tipo de página/módulo específico
Nivel 3: Estándar de vertical      (ej. TRADING_LANDING_STANDARD.md, SAAS_LANDING_STANDARD.md)
              ↓ agrega/sobrescribe reglas para un rubro de negocio específico
```

Regla de herencia: un documento de Nivel 2 o 3 **no repite** lo que ya dice el nivel anterior — solo agrega lo específico o declara explícitamente qué regla hereda y sobrescribe, y por qué. Un documento de Nivel 3 se crea solo cuando un rubro acumula 3+ reglas propias que no aplican a los demás verticales del mismo Nivel 2 — antes de eso, esas reglas viven como una nota dentro del documento de Nivel 2 (no se crea el archivo todavía). Hoy (2026-07-09) no existe ningún documento de Nivel 3 en el handbook — se crean bajo demanda, cuando un proyecto real lo justifique.

**Por qué los niveles se corresponden con Componentes vs Patrones:** el Nivel 1 de cada dominio define las piezas pequeñas y genéricas (en frontend: Button, Input, Card — sección 04). Los documentos de Nivel 2 definen patrones — combinaciones específicas de esas piezas que resuelven un problema de UX/negocio completo (Navbar, Dashboard, CRUD, Landing, Pricing). Diseñar pensando solo en componentes produce interfaces ensambladas sin criterio; pensar en patrones obliga a preguntar primero "¿qué problema estoy resolviendo?" antes de "¿qué pieza uso?". Ver ejemplo aplicado en `01_Frontend/FRONTEND_NAVIGATION_PATTERNS.md` sección 8.

## 5. Estructura interna de cada documento de dominio

1. Encabezado YAML con metadatos de trazabilidad.
2. Secciones numeradas por tema.
3. Cada regla: título → `[REQUIRED]`/`[RECOMMENDED]` → regla en capa agnóstica → **Por qué** (el motivo, no solo el qué — esto es lo que le permite a una IA generalizar a casos que el documento no cubrió explícitamente) → implementación de referencia si aplica.
4. Checklist final verificable, en el mismo orden que las secciones.

## 6. Metadatos de Trazabilidad y Confianza (Frontmatter YAML)

Todo documento nuevo generado para cubrir una laguna debe incluir los siguientes metadatos en su encabezado:

```yaml
---
title: "Título del Estándar"
category: dominio_o_carpeta
tags: [tag1, tag2]
summary: "Resumen ejecutivo de lo que regula este documento."
status: VERIFIED | DRAFT
confidence: 100% | 75%
reviewed: false
sources:
  - "IETF RFC 9110 (HTTP Semantics)"
  - "MDN Web Docs — Fetch API Specification"
  - "Cloudflare Workers Official Documentation"
updated: 2026-07-27
---
```

### Significado de los Campos:
- `status`: `VERIFIED` si fue validado cruzando 2+ fuentes de los Niveles 2 a 4 de la Jerarquía de Confianza. `DRAFT` si depende de inferencias de nivel 5/6.
- `confidence`: Nivel de certidumbre numérica (100% para RFCs/W3C/Doc Oficial, <80% para borradores).
- `reviewed`: `false` hasta que un ingeniero humano lo apruebe formalmente.
- `sources`: Lista explícita de especificaciones, RFCs o documentación oficial primaria consultada.

## 7. Mapa de dominios del handbook

```
ENGINEERING_HANDBOOK/
├── 00_HANDBOOK_FORMAT.md   ← este documento
├── 01_Frontend/
├── 02_Backend/
├── 03_API/
├── 04_Database/
├── 05_Security/
├── 06_Testing/
├── 07_DevOps/
├── 08_Cloud/
├── 09_Architecture/
├── 10_Product/
├── 11_Debugging/
├── 12_Documentation/
├── 13_AI_Rules/
├── 14_DX/
└── 15_Knowledge_System/
```
