# ENGINEERING OS — Jeilin Castro

> Sistema operativo de ingeniería. Fuente única de verdad para **toda IA** que trabaje con Jeilin
> (Claude, ChatGPT, Gemini, Codex, modelos locales, agentes MCP). No es documentación: es un manual
> operativo. Una IA nueva debe poder colaborar leyendo solo este sistema.

**Versión:** 1.0.0 · **Creado:** 2026-07-20 · **Basado en:** auditoría real de `C:\trabajo` + `E:\` (repos, git, deploys, herramientas)

---

## Cómo usar este sistema (para una IA que llega por primera vez)

Orden de lectura mínimo obligatorio (15 min):

1. [00-Chief-Architect.md](00-Chief-Architect.md) — quién eres cuando trabajas aquí y cómo decidir.
2. [01-Mission.md](01-Mission.md) — contexto de Jeilin, sus proyectos y objetivos.
3. [03-Global-Rules.md](03-Global-Rules.md) — reglas no negociables.
4. [04-Workflow.md](04-Workflow.md) — el pipeline obligatorio de 16 pasos.
5. [27-Agent-Rules.md](27-Agent-Rules.md) — si actúas como un agente especializado, tu contrato.

Después, según la tarea:

| Si la tarea es… | Lee además |
|---|---|
| Escribir código frontend | [08-Frontend-Standards.md](08-Frontend-Standards.md) → handbook `01_Frontend/` |
| Escribir un Worker / API | [09-Backend-Standards.md](09-Backend-Standards.md), [10-Cloudflare-Standards.md](10-Cloudflare-Standards.md) |
| Base de datos / auth | [11-Supabase-Standards.md](11-Supabase-Standards.md), [12-Firebase-Standards.md](12-Firebase-Standards.md) |
| Integrar IA | [13-AI-Standards.md](13-AI-Standards.md) |
| Crear un proyecto nuevo | [07-Project-Structure.md](07-Project-Structure.md), [25-Checklists.md](25-Checklists.md) §1, [26-Templates.md](26-Templates.md) |
| Commit / PR / deploy | [19-Git-Standards.md](19-Git-Standards.md), [20-Deployment.md](20-Deployment.md), [25-Checklists.md](25-Checklists.md) |
| Auditar / recomendar mejoras | [05-Decision-Matrix.md](05-Decision-Matrix.md), [24-Metrics.md](24-Metrics.md), `Agents/` |
| Decisión de negocio / precio | [21-Business.md](21-Business.md) |
| Auditar el handbook / health check | [30-Audit.md](30-Audit.md) |
| Seguimiento de mejoras | [29-Roadmap.md](29-Roadmap.md) + [30-Audit.md](30-Audit.md) |
| Roadmaps y recursos externos | [31-General-Resources.md](31-General-Resources.md) |

## Relación con el ENGINEERING_HANDBOOK

```
E:\ENGINEERING_HANDBOOK\          ← CÓMO se escribe el código (estándares técnicos por dominio)
E:\ENGINEERING_HANDBOOK\Engineering-OS\   ← CÓMO se trabaja (proceso, decisiones, agentes, negocio)
```

Regla de herencia (la misma del handbook): **este OS no repite reglas técnicas que ya viven en el
handbook** — las referencia. Si encuentras contradicción entre un archivo del OS y el handbook, gana
el handbook en lo técnico y el OS en lo operativo, y se documenta la inconsistencia en
[28-Knowledge-Base.md](28-Knowledge-Base.md).

## Mapa completo

| Bloque | Archivos |
|---|---|
| Identidad y reglas | 00-Chief-Architect · 01-Mission · 02-Core-Principles · 03-Global-Rules |
| Proceso | 04-Workflow · 05-Decision-Matrix · 25-Checklists · 26-Templates |
| Técnico | 06-Architecture · 07-Project-Structure · 08→13 Standards · 14-Code-Quality · 15-Performance · 16-Security · 17-Testing |
| Entrega | 18-Documentation · 19-Git-Standards · 20-Deployment |
| Estrategia | 21-Business · 22-Learning-Roadmap · 23-Automations · 29-Roadmap |
| Sistema | 24-Metrics · 27-Agent-Rules · 28-Knowledge-Base · `Agents/` (16 agentes) · 30-Audit · 31-General-Resources |

## Mantenimiento del OS

- Cada cambio real en el ecosistema (nuevo proyecto, migración, automatización creada) actualiza el
  archivo correspondiente **en el mismo commit/sesión** — un OS desactualizado es peor que ninguno.
- [29-Roadmap.md](29-Roadmap.md) se re-evalúa después de cada mejora implementada: se mide contra
  [24-Metrics.md](24-Metrics.md) y se registra el resultado (mejoró / no mejoró / empeoró) antes de
  pasar al siguiente ítem. Esa es la regla de "análisis continuo".
- Versionado: este directorio vive dentro de un repo git. Cambios de estructura → bump de versión
  aquí; cambios de contenido → solo commit.

## Changelog

- **1.0.0** (2026-07-20) — Creación inicial a partir de la auditoría de ecosistema (inventario C:\ y E:\, auditoría de seguridad, análisis de flujo de JCDigital).
