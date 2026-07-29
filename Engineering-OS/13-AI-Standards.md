# 13 — AI Standards (integrar IA en productos y en el flujo de trabajo)

> Este archivo cubre dos caras de la IA en el ecosistema: (a) IA dentro de productos que
> vendemos a clientes, y (b) IA como fuerza de trabajo interna. El **protocolo de razonamiento
> para IAs que escriben código** (cómo clasificar tareas, qué documentos leer, cómo reportar)
> no está aquí — vive en `13_AI_Rules/AI_WORKFLOW.md`.
>
> **Ver también:**
> - [`AI_WORKFLOW.md`](../13_AI_Rules/AI_WORKFLOW.md) — protocolo obligatorio para cualquier IA
>   que genere o revise código contra el handbook.
> - [`AI_PROMPTS_LIBRARY.md`](../13_AI_Rules/AI_PROMPTS_LIBRARY.md) — prompts reutilizables.
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Una IA que va a escribir código sigue **primero** `AI_WORKFLOW.md`
>   (clasificar tarea → leer estándar → verificar → implementar). Este archivo no es un
>   reemplazo de ese protocolo — son reglas operativas sobre cómo se integra IA en productos
>   y cómo se divide el trabajo entre modelos.

## IA dentro de productos

- **[REQUIRED]** Ruta por defecto: OpenRouter → GPT-4o-mini (stack canónico). Modelo más caro solo
  con justificación por la matriz de decisión (¿la calidad extra la paga el cliente/producto?).
- **[REQUIRED]** Toda llamada a LLM en producción pasa por un worker (nunca desde el frontend con
  la key expuesta), con: timeout, manejo de error visible al usuario, y límite de tokens/costo por
  request.
- **[REQUIRED]** Registrar en el README del proyecto: modelo usado, costo estimado por 1k
  requests, y qué pasa si el proveedor cae (fallback o mensaje de error digno).
- **[RECOMMENDED]** Prompts de producción viven en archivos versionados (no strings inline
  regados), con changelog cuando se ajustan.

## IA como fuerza de trabajo (el "equipo" de Jeilin)

- **[REQUIRED]** División de trabajo por capacidad del modelo:
  - **IA potente** (Claude potente, GPT frontier): arquitectura, seguridad, revisión de pagos,
    priorización, redacción de estándares, síntesis de auditorías.
  - **IA básica** ("IA tonta"): generación de componentes CON patrón del handbook en contexto,
    barridos de inventario, renombrados masivos, README desde plantilla, tests desde ejemplos.
  - Regla del 00-Chief-Architect: *la básica ejecuta, la potente decide.* Nunca darle a la básica
    una decisión de arquitectura ni a la potente una tarea mecánica de 200 archivos.
- **[REQUIRED]** Toda IA que trabaje en el ecosistema recibe como contexto mínimo: este OS
  (README + 03-Global-Rules) + el CLAUDE.md del proyecto. Sin ese contexto, sus salidas no se
  integran directo — las revisa una IA potente o Jeilin.
- **[REQUIRED]** Salidas de IA básica en código crítico (pagos, auth, datos de clientes) SIEMPRE
  pasan revisión de IA potente antes de merge. En código no crítico: basta el checklist de commit.
- **[RECOMMENDED]** Dónde ya se ahorra trabajo con IA (mantener): generación de código con
  handbook, auditorías (como esta), redesigns completos. Dónde falta explotar (candidatos en
  [23-Automations.md](23-Automations.md)): revisión automática de PRs, generación de tests para
  workers, análisis de logs de producción, generación de contenido para las webs de clientes,
  changelogs automáticos.

## MCPs propios

- Existen: `jcdigital` (gestión de proyectos + Telegram), `blender-mcp`, `roblox-mcp`. Regla de
  herramienta viva (principio 3): un MCP que no se usa 30 días se archiva o se conecta de verdad
  al flujo. El MCP jcdigital es la memoria de proyectos del OS — alimentarlo es parte del paso 1
  del workflow.
