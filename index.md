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
  - icon: 🔒
    title: Security — Web, Desktop y Móvil
    details: 7 capas para el backend, más ACL de IPC para Tauri y firma/Keystore para Android. El backend nunca confía en el cliente, en ninguna plataforma.
    link: /05_Security/SECURITY_ENGINEERING_STANDARD
  - icon: 🎨
    title: Frontend — Core, Patrones y UI
    details: 52 documentos, desde TypeScript estricto hasta cada patrón de UI (CRUD, tablas, formularios, dashboards) con su implementación de referencia.
    link: /01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD
  - icon: 🧪
    title: Testing — Departamento de QA completo
    details: Estrategia, pipelines, 8 agentes de QA especializados y los quality gates que definen cuándo un build está listo.
    link: /06_Testing/README
  - icon: 🗄️
    title: Database — De RLS a vector search
    details: Esquema blindado, escalabilidad, RLS multi-tenant y búsqueda semántica con pgvector, todo con el porqué de cada regla.
    link: /04_Database/DATABASE_ENGINEERING_STANDARD
  - icon: 🧠
    title: Auto-ruteo para IA
    details: AGENTS.md es el árbol de decisión que le dice a cualquier IA qué documento consultar antes de escribir una línea de código.
    link: /AGENTS
  - icon: 🐛
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
