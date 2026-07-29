---
title: "Architecture Decision Log (ADR)"
category: 09_Architecture
doc_type: referencia
tags: [adr, architecture, decisions, stack]
summary: "Registro central de las decisiones arquitectónicas inquebrantables del stack, cada una con su contexto y alternativas descartadas: Workers frente a Node, Supabase frente a Firebase, React Query frente a useEffect."
keywords: [adr, architecture, decisions, stack, decision, registro, central, decisiones, arquitectonicas, inquebrantables, contexto, alternativas, descartadas, workers]
updated: 2026-07-27
status: current
---

# 🏛️ ARCHITECTURE DECISION LOG (ADR)

Este documento centraliza las decisiones arquitectónicas fundamentales (ADR) de la empresa. Las decisiones aquí tomadas son **INQUEBRANTABLES** a menos que se presente una propuesta formal de re-evaluación en base a las condiciones estipuladas.

---

## ADR-001: Elección de Cloudflare Workers sobre Node.js + Docker

* **Estado:** Aceptado
* **Fecha:** 2024-01-15
* **Contexto:** Startup con < 10 devs, base de usuarios globales, sin equipo dedicado a DevOps ni SRE. Se necesita escalar desde cero hasta millones de requests con el menor costo inicial posible.
* **Alternativas consideradas:**
  1. **Node.js + Docker en AWS ECS:** Descartado. Requiere configuración extensa de VPCs, balanceadores de carga y un rol DevOps. Posee un cold start de 2-3s al escalar y un costo base de ~$50/mes incluso en idle.
  2. **Vercel Serverless Functions:** Descartado. Límite de timeout estricto de 10s en tier gratuito/pro, altos márgenes de markup sobre los servicios de AWS por debajo y fuerte vendor lock-in hacia el ecosistema Next.js.
  3. **Cloudflare Workers (Elegido):** Seleccionado. Cold start prácticamente nulo (< 5ms), despliegue en Edge global instantáneo, costo base en idle de $0 y facturación por milisegundo de CPU usado.
* **Consecuencias Positivas:** Deploy global instantáneo en < 5s, escalado virtualmente infinito sin administrar ni parchar servidores, barrera de entrada DevOps eliminada.
* **Consecuencias Negativas:** Límite estricto de CPU (30s) obligando a arquitectura asíncrona, carencia de acceso al file system tradicional (`fs`), y vendor lock-in a las APIs específicas de Cloudflare (KV, D1, Queues).
* **Riesgos Mitigados:** Utilizan APIs estándar de la Web (`fetch`, `Request`, `Response`), lo que facilita la potencial migración futura a entornos como Deno Deploy o Bun.
* **Cuándo re-evaluar:** Crecimiento del equipo de backend a > 50 devs, requerimientos de procesamiento muy pesado de ML/GPU en tiempo real, o persistencia constante de WebSockets > 2 horas.

---

## ADR-002: Elección de Supabase sobre Firebase o PostgreSQL directo

* **Estado:** Aceptado
* **Fecha:** 2024-01-20
* **Contexto:** Necesidad de una base de datos robusta, relacional para datos estructurados, pero con capacidades de Real-Time integradas para actualizaciones en vivo de UI, Auth segura y Row Level Security (RLS) para arquitecturas multi-tenant.
* **Alternativas consideradas:**
  1. **Firebase Firestore:** Descartado. Base de datos NoSQL que complica las relaciones complejas (sin JOINs verdaderos), vendor lock-in absoluto con Google, capacidades de querying y migraciones muy limitadas.
  2. **PostgreSQL directo (AWS RDS / DigitalOcean):** Descartado. Falta de Real-Time nativo sin montar servicios adicionales (ej. Debezium), no trae Auth integrada, lo que requiere mantener servidores de JWT y gestionar explícitamente los connection pools.
  3. **Supabase (Elegido):** Seleccionado. Motor PostgreSQL real, RLS integrado en el core, Real-Time nativo a través de subscripciones de base de datos, y módulo de Auth robusto incluido.
* **Consecuencias:** Consolidación de Auth, Base de Datos, Storage y Real-time en un solo proveedor y SDK. Facilita el RLS para aislar clientes en SaaS B2B.
* **Riesgos:** Posible rate limiting estricto en los tiers de entrada, cold starts de la base de datos si entra en modo pausa (tier gratuito) o cuellos de botella en el connection pool si no se usa Supavisor.
* **Cuándo re-evaluar:** Volúmenes masivos de datos que requieran arquitecturas analíticas específicas (TimescaleDB) o capacidades avanzadas de Full-Text Search (Elasticsearch) que superen a `pg_search`.

---

## ADR-003: Elección de React Query sobre useEffect + fetch

* **Estado:** Aceptado
* **Fecha:** 2024-02-01
* **Contexto:** Necesidad de manejar un estado asíncrono robusto en el frontend, con caching eficiente, deduping de requests, y soporte para mutaciones optimistas para mejorar la UX.
* **Alternativas consideradas:**
  1. **useEffect + fetch + useState:** Descartado. Alto boilerplate, carencia nativa de caché, sin estrategias de invalidación, muy propenso a race conditions y renderizados innecesarios. No soporta optimistic updates de forma limpia.
  2. **SWR (Vercel):** Descartado. Menos funcionalidades maduras out-of-the-box en comparación con React Query, específicamente en el manejo avanzado de dependencias de queries y mutaciones complejas.
  3. **React Query / TanStack Query (Elegido):** Seleccionado. Provee caché automática de primer nivel, manejo limpio de optimistic updates, reintentos automáticos, stale-while-revalidate nativo y excelentes DevTools.
* **Consecuencias:** Caché inteligente automática en todo el frontend, código de componentes purgado de lógica de fetching, mutaciones optimistas que brindan sensación de "app instantánea".
* **Riesgos:** Aumento del bundle size inicial (~13KB minzipped). 
* **Mitigación:** Configuración estricta de tree-shaking y lazy loading; el impacto es despreciable versus la estabilidad ganada.

---

## ADR-004: Elección de Zod sobre Yup o Joi

* **Estado:** Aceptado
* **Fecha:** 2024-02-15
* **Contexto:** Necesidad de un sistema de validación de esquemas (Schemas) fuertemente tipado que pueda ser compartido de manera idéntica entre el Frontend (formularios) y el Backend (APIs).
* **Alternativas consideradas:**
  1. **Yup:** Descartado. No posee inferencia nativa estricta hacia tipos de TypeScript (TS), requiere trabajo duplicado en muchos casos complejos.
  2. **Joi:** Descartado. Librería legacy muy pesada, no está optimizada para TypeScript nativamente y no soporta tree-shaking moderno.
  3. **Zod (Elegido):** Seleccionado. API funcional y declarativa, inferencia de tipos estática en TypeScript en una sola línea (`z.infer`), extremadamente ligero y 100% tree-shakeable. Excelente Developer Experience (DX).
* **Consecuencias:** DRY (Don't Repeat Yourself) absoluto en modelos de datos. Un solo esquema Zod define la validación runtime y genera la interfaz TypeScript compile-time. Permite validación ultrarrápida en el Edge (Workers).
* **Riesgos:** Librería relativamente nueva frente a estándares corporativos como Joi.
* **Mitigación:** Comunidad activa enorme, estable y fuertemente adoptada por todo el ecosistema de tRPC y React Hook Form.

---

## ADR-005: Elección de TypeScript estricto (strict: true)

* **Estado:** Aceptado
* **Fecha:** 2024-01-10
* **Contexto:** Equipos iterando rápido sobre lógicas de negocio críticas (facturación, SaaS). Necesidad de blindar el código contra errores en tiempo de ejecución (`undefined is not a function`).
* **Alternativas consideradas:**
  1. **JavaScript puro:** Descartado. Nula seguridad de tipos, propensión altísima a bugs silenciosos en producción, refactors a gran escala extremadamente peligrosos.
  2. **TypeScript con `strict: false`:** Descartado. Proporciona un falso sentido de seguridad. El tipo implícito `any` y la ausencia de chequeos estrictos de null se escapan fácilmente al CI/CD.
  3. **TypeScript con `strict: true` (Elegido):** Seleccionado. Fuerza cheques exhaustivos, prohíbe `any` implícitos, requiere comprobación de nulos y obliga a manejar todos los casos en un Switch/Pattern Matching.
* **Consecuencias:** Reducción drástica de bugs en producción (especialmente TypeErrors), mejor autocompletado en IDE, y confianza ciega en refactors masivos de código heredado.
* **Riesgos:** Fricción inicial y mayor tiempo de escritura en desarrolladores acostumbrados a JS, curva de aprendizaje en genéricos avanzados.
* **Mitigación:** Capacitación interna inicial y documentación clara de escape hatches explícitos y aprobados (como el uso *justificado* de `@ts-expect-error`).
