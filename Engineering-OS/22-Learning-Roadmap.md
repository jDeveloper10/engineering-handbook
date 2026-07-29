# 22 — Learning Roadmap

> Jeilin es autodidacta por diseño (principio de su marca). Este archivo dirige ese aprendizaje
> hacia lo que el ecosistema necesita, en orden de retorno — no hacia lo que esté de moda.

## Criterio

Se aprende lo que (a) desbloquea un ítem del [29-Roadmap.md](29-Roadmap.md), o (b) reduce
dependencia de terceros en algo crítico, o (c) sube el precio cobrable por proyecto. Máximo 1 tema
activo a la vez.

## Cola priorizada (2026-07)

| # | Tema | Por qué (evidencia del ecosistema) | Resultado verificable |
|---|---|---|---|
| 1 | **GitHub Actions básico** | 0 CI en ~95 proyectos; workers se despliegan a mano | `ci.yml` corriendo en JCDigital y worker-pago desplegando solo |
| 2 | **Testing con vitest (lo mínimo)** | 0 tests en código que cobra dinero real | Los ~6 tests de worker-pago escritos y en CI |
| 3 | **Git de rescate** | uñapp corrupto con 32 cambios atrapados; miedo al historial = commits en ráfagas | uñapp recuperado; reflog/fsck/stash dominados |
| 4 | **Supabase RLS a fondo** | Stack canónico declara Supabase; RLS mal hecho = brecha de datos de clientes | Políticas de un proyecto real auditadas y documentadas |
| 5 | **n8n avanzado + Baileys** | VPS ya pagado; automatizaciones de [23-Automations.md](23-Automations.md) lo usan | 2 automatizaciones del roadmap corriendo en n8n |
| 6 | **Prompting de sistema para IA básica** | El OS depende de que modelos baratos ejecuten bien | Checklist de una tarea ejecutada por IA básica sin correcciones |

**Recursos externos relacionados:** [31-General-Resources.md](31-General-Resources.md) — roadmaps y guías generales de desarrollo.

## Reglas

- **[REQUIRED]** Aprender construyendo sobre proyectos reales del ecosistema, nunca con tutoriales
  desconectados (el tema 1 se aprende instalando CI en JCDigital, no en un repo de juguete).
- **[REQUIRED]** Al cerrar un tema: 5-10 líneas de "lo que ahora sé hacer" en
  [28-Knowledge-Base.md](28-Knowledge-Base.md) + actualizar esta cola.
- **[RECOMMENDED]** Las IAs potentes actúan como tutores del tema activo: explican mientras
  implementan, para que el conocimiento quede en Jeilin y no solo en el chat.
