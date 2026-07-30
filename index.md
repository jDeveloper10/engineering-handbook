---
layout: home
title: Engineering Handbook

hero:
  name: "Engineering Handbook"
  text: "Base de conocimiento de ingeniería"
  tagline: 171 documentos. Un solo protocolo de auto-ruteo para IA. Cero reglas sueltas — todo es REQUIRED o RECOMMENDED, con su porqué.
  actions:
    - theme: brand
      text: Empezar por el mapa de ruteo
      link: /AGENTS
    - theme: alt
      text: Ver convenciones (§00)
      link: /00_HANDBOOK_FORMAT
    - theme: alt
      text: Índice completo
      link: /README

features:
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>'
    title: Security — Web, Desktop y Móvil
    details: 7 capas para el backend, más ACL de IPC para Tauri y firma/Keystore para Android. El backend nunca confía en el cliente, en ninguna plataforma.
    link: /05_Security/SECURITY_ENGINEERING_STANDARD
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>'
    title: Frontend — Core, Patrones y UI
    details: 52 documentos, desde TypeScript estricto hasta cada patrón de UI (CRUD, tablas, formularios, dashboards) con su implementación de referencia.
    link: /01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/></svg>'
    title: Testing — Departamento de QA completo
    details: Estrategia, pipelines, 8 agentes de QA especializados y los quality gates que definen cuándo un build está listo.
    link: /06_Testing/README
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>'
    title: Database — De RLS a vector search
    details: Esquema blindado, escalabilidad, RLS multi-tenant y búsqueda semántica con pgvector, todo con el porqué de cada regla.
    link: /04_Database/DATABASE_ENGINEERING_STANDARD
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>'
    title: Auto-ruteo para IA
    details: AGENTS.md es el árbol de decisión que le dice a cualquier IA qué documento consultar antes de escribir una línea de código.
    link: /AGENTS
  - icon:
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m8 2 1.88 1.88"/><path d="M14.12 3.88 16 2"/><path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1"/><path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6"/><path d="M12 20v-9"/><path d="M6.53 9C4.6 8.8 3 7.1 3 5"/><path d="M6 13H2"/><path d="M3 21c0-2.1 1.7-3.9 3.8-4"/><path d="M20.97 5c0 2.1-1.6 3.8-3.5 4"/><path d="M22 13h-4"/><path d="M17.2 17c2.1.1 3.8 1.9 3.8 4"/></svg>'
    title: Debugging — Playbooks de la primera hora
    details: Runbooks accionables para los incidentes más comunes — API caída, base de datos caída, cold starts — con diagnóstico en 30 segundos.
    link: /11_Debugging/ERROR_INDEX
---

## Cómo está organizado

Este handbook sigue una jerarquía de 3 niveles ([ver §00_HANDBOOK_FORMAT](/00_HANDBOOK_FORMAT)):

1. **Estándar de dominio** — aplica siempre, en todo proyecto de ese dominio.
2. **Estándar de patrón** — agrega reglas para un tipo de página o módulo específico.
3. **Estándar de vertical** — agrega o sobrescribe reglas para un rubro de negocio concreto.

Toda regla lleva `[REQUIRED]` o `[RECOMMENDED]` y un **Por qué** — no hay reglas sin justificación, y una IA sabe exactamente qué puede negociar y qué no.

Usa el buscador (arriba, o <kbd>Ctrl</kbd>+<kbd>K</kbd>) o navega por dominio en el menú lateral.
