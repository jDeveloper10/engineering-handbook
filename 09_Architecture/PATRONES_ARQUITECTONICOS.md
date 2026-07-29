---
title: "Patrones Arquitectónicos"
category: 09_Architecture
tags: [patterns, cloudflare, edge, jamstack]
summary: "Arquitectura general de los proyectos sobre edge y Jamstack, y cuándo aplicar patrones específicos: event-driven con colas, coordinación de estado con Durable Objects y capas de caché."
keywords: [patterns, cloudflare, edge, jamstack, arquitectonicos, arquitectura, general, proyectos, aplicar, especificos, event-driven, colas, coordinacion, estado]
updated: 2026-07-27
status: current
---

# Patrones Arquitectónicos

Este documento define la arquitectura general de nuestros proyectos y en qué casos usar patrones específicos. Nuestro stack base se apoya fuertemente en el **Edge Computing** (Cloudflare) y bases de datos gestionadas (Supabase).

## 1. Arquitectura Base (The Edge-Jamstack)

La arquitectura estándar para cualquier nuevo producto es:
- **Frontend**: SPA / SSG (React) hosteado globalmente en Cloudflare Pages.
- **Backend / API**: Funciones *Serverless/Edge* en Cloudflare Workers.
- **Data Layer**: Supabase (Postgres) consumido desde los Workers o directamente con RLS (Row Level Security).

### ¿Cuándo usar este patrón?
Es la opción **por defecto** (`[REQUIRED]` como punto de partida). Escala automáticamente, reduce latencia (Edge) y mantiene la base de código simple y serverless.

## 2. Event-Driven (Colas y Asincronía)

**[REQUIRED]** Cuando una solicitud HTTP al Worker tarda más de 500ms o requiere procesamiento pesado (ej. enviar 100 emails, procesar imágenes, integraciones con IA de largo tiempo), **NO** se debe bloquear la respuesta HTTP.

### Implementación con Cloudflare Queues
1. El Worker recibe el Request.
2. Valida datos y encola un mensaje (`await env.MY_QUEUE.send(data)`).
3. Responde HTTP 202 Accepted.
4. Un Consumer Worker procesa la cola de fondo.

## 3. Estado Consistente y Coordinación (Durable Objects)

**[RECOMMENDED]** Cuando se requiere coordinación estricta en tiempo real o mantener estado en memoria entre múltiples conexiones (ej. WebSockets, juegos multiplayer, contadores exactos, lock distribuido).
*No usar como base de datos primaria, siempre volcar estado final a Postgres/D1.*

## 4. Patrones de Caché

- **Nivel 1 (CDN)**: Archivos estáticos en Cloudflare Pages, con TTL largo y validación in-band.
- **Nivel 2 (Edge Cache)**: Respuestas API guardadas en la Cache API (`caches.default`) de Workers.
- **Nivel 3 (KV Cache)**: Datos de base de datos de lectura frecuente y mutación lenta, almacenados en Cloudflare KV para evitar latencia hacia Supabase.

---

> **Nota Anti-Patrones**: 
> - **NO** construyas monolitos tradicionales (ej. Express en EC2 o Heroku) sin un ADR justificado que explique por qué el Edge es insuficiente.
> - **NO** leas de la base de datos dentro de un bucle `for` en los Workers; la latencia de red arruinará el tiempo de ejecución.
