# 08 — Frontend Standards (capa operativa)

> La autoridad técnica es el handbook: `E:\ENGINEERING_HANDBOOK\01_Frontend\` (Nivel 1 completo +
> 24 documentos de patrones). **Este archivo no repite reglas técnicas** — define solo las reglas
> operativas (cómo se usan los estándares en el flujo de trabajo de Jeilin).
>
> **Ver también:** [`FRONTEND_ENGINEERING_STANDARD.md`](../01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md)
> para reglas técnicas detalladas; [`FRONTEND_UI_STYLE_CATALOG.md`](../01_Frontend/UI_Components/FRONTEND_UI_STYLE_CATALOG.md)
> para el sistema de tokens.

## Orden de consulta para una IA que va a escribir UI

1. `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` — siempre.
2. El documento de patrón que corresponda a la pantalla (landing, dashboard, CRUD, tabla, modal,
   auth, navegación, estados, notificaciones…). Existe uno para casi todo — **buscar antes de
   inventar**.
3. `FRONTEND_UI_STYLE_CATALOG.md` + `E:\Pruebas\` (catálogo de +30 estilos UI ya construidos:
   glassmorphism, neumorphism, material, 8-bit, aurora…) — reutilizar antes de diseñar.

## Reglas operativas (las que el handbook no cubre)

- **[REQUIRED]** Proyectos nuevos: React 19 + Vite + TypeScript. Legacy en JSX (ej. jcdigital):
  se mantiene JSX; migración a TS solo como tarea explícita, nunca mezclada con features.
- **[REQUIRED]** Lo pesado se carga diferido: three.js/R3F, Remotion, charts → `lazy()` + chunk
  separado. Referencia real: `Hero3D` en jcdigital (chunk de 871KB que no bloquea el first paint).
  Un chunk inicial > 400KB gzip requiere justificación escrita.
- **[REQUIRED]** Toda vista nueva se verifica en preview (móvil 375px + desktop) antes de commit —
  checklist §4 de [25-Checklists.md](25-Checklists.md).
- **[RECOMMENDED]** IA básica genera componentes SOLO con el documento de patrón abierto en
  contexto; sin patrón en contexto, los resultados divergen del sistema (causa raíz de UI
  inconsistente entre proyectos detectada en auditoría).
