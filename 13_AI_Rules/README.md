---
title: "Dominio 13: AI Rules — Índice y Estándares"
category: 13_AI_Rules
doc_type: referencia
tags: [ai-rules, indice, standards, post-mortem, colaboracion]
summary: "Índice de gobernanza y directivas para agentes de Inteligencia Artificial que colaboran en proyectos de JDeveloper: perfiles de toma de decisiones, patrones de éxito en producción, post-mortems de fallos críticos y flujos de trabajo."
keywords: [ia, indice, razonamiento, post-mortem, cerrojos, iaspro, vitest, handoff]
updated: 2026-09-22
status: current
---

# 🤖 Dominio 13: AI Rules (Gobernanza y Protocolos de Agentes de IA)

Este dominio recopila los estándares obligatorios de interacción, razonamiento técnico y colaboración entre el desarrollador humano (**JDeveloper**) y los agentes autónomos (**Antigravity**, **Claude Code**, **OpenAI Codex**).

---

## 📑 Documentos Activos en este Dominio

### 1. Documentos de Referencia Operativa y Experiencia Real (2026)

| Documento | Tipo | Descripción |
|---|---|---|
| **[LECCIONES_APRENDIDAS_Y_CASOS_REALES_MULTI_IA.md](LECCIONES_APRENDIDAS_Y_CASOS_REALES_MULTI_IA.md)** | `patron` | **Catálogo de aciertos (lo bueno), post-mortems de dolores de cabeza (lo malo), casos FB-001/TOCTOU/Codemagic y la doctrina de las 4 pruebas obligatorias en suites de Vitest.** |
| **[PERFIL_DE_COLABORACION_JDEVELOPER.md](PERFIL_DE_COLABORACION_JDEVELOPER.md)** | `referencia` | **Perfil de toma de decisiones de JDeveloper, mapa de repositorios montados, expectativas de producto y directivas para no romper flujos.** |

### 2. Estándares Fundacionales de IA

| Documento | Tipo | Descripción |
|---|---|---|
| **[AI_WORKFLOW.md](AI_WORKFLOW.md)** | `estandar` | Flujo de trabajo estándar: análisis de requisitos, elección de estándar aplicable y verificación antes de implementar. |
| **[AI_PROMPTS_LIBRARY.md](AI_PROMPTS_LIBRARY.md)** | `referencia` | Biblioteca canónica de prompts para auditoría, refactorización y depuración guiada. |
| **[MCP_TOOLS_STANDARD.md](MCP_TOOLS_STANDARD.md)** | `estandar` | Estándar de integración del Model Context Protocol (MCP) y herramientas de terminal compartidas. |
| **[AI_ML_PRODUCTION.md](AI_ML_PRODUCTION.md)** | `estandar` | Requisitos para despliegue y consumo de modelos de machine learning en producción. |

---

## 🔒 Regla Innegociable para toda IA

Antes de escribir código o sugerir cambios de arquitectura en cualquier repositorio:
1. Consultar el **[PERFIL_DE_COLABORACION_JDEVELOPER.md](PERFIL_DE_COLABORACION_JDEVELOPER.md)** para alinearse al contexto del cliente.
2. Comprobar que no se incurra en ninguno de los antipatrones documentados en **[LECCIONES_APRENDIDAS_Y_CASOS_REALES_MULTI_IA.md](LECCIONES_APRENDIDAS_Y_CASOS_REALES_MULTI_IA.md)** (cero fake success, cero parches cosméticos, cero mocks en staging/producción).
