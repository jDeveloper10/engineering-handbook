# 04 — Workflow obligatorio

> Pipeline de 16 pasos. Todo trabajo — feature, fix, proyecto nuevo — recorre este flujo. Los pasos
> pueden ser de 2 minutos, pero **no pueden saltarse en silencio**: si se salta uno, se declara y
> se justifica. El Workflow-Agent audita este pipeline; el Automation-Agent lo acorta.

```
Idea → Investigación → Arquitectura → Diseño → Desarrollo → Testing → Git → CI/CD
→ Deploy → Producción → Monitoreo → Errores → Optimización → Documentación
→ Retrospectiva → Automatización
```

## Definición operativa de cada paso

| # | Paso | Qué significa aquí (mínimo aceptable) | Herramienta actual |
|---|---|---|---|
| 1 | **Idea** | Registrarla en el MCP jcdigital (`update_project`) o en `29-Roadmap`. Una idea no registrada se pierde en WhatsApp/cabeza. | MCP jcdigital |
| 2 | **Investigación** | ¿Ya existe en el ecosistema? (handbook, workers-template, proyecto anterior). ¿Existe SaaS que lo resuelva por <$10/mes? 15 min máximo para features chicas. | IA + este OS |
| 3 | **Arquitectura** | Decidir: ¿Pages, Worker, o ambos? ¿Supabase o KV/R2? Escribir 5 líneas en el README del proyecto. Features chicas: heredan la arquitectura existente, paso = 0 min. | [06-Architecture.md](06-Architecture.md) |
| 4 | **Diseño** | Aplicar handbook `01_Frontend` (patrones ya definidos). No diseñar desde cero lo que el catálogo de estilos ya resolvió. | Handbook |
| 5 | **Desarrollo** | Código según estándares 08-13. IA básica ejecuta con checklist; IA potente revisa lo crítico (pagos/auth). | IA + handbook |
| 6 | **Testing** | Mínimo: build pasa + flujo crítico probado en preview. Pagos: [17-Testing.md](17-Testing.md) obligatorio. | Vite build, vitest |
| 7 | **Git** | Commit con formato de [19-Git-Standards.md](19-Git-Standards.md). **Diario.** Push siempre (regla: nada vive solo en el disco). | git |
| 8 | **CI/CD** | Objetivo: GitHub Actions valida build en cada push (HOY NO EXISTE — ítem #1 del roadmap). Mientras no exista: `npm run build` local antes de push. | GitHub Actions (pendiente) |
| 9 | **Deploy** | Frontend: push a `main` = deploy (Pages). Workers: `npx wrangler deploy` — objetivo: mover a CI (roadmap). Checklist pre-deploy de [25-Checklists.md](25-Checklists.md) §5. | Pages / wrangler |
| 10 | **Producción** | Verificar la URL real después de cada deploy (no asumir). Smoke test de 2 min: carga, consola sin errores, flujo crítico. | Navegador |
| 11 | **Monitoreo** | Hoy: manual (workers logs / dashboard CF). Objetivo: alertas a WhatsApp vía n8n+Baileys cuando un worker falla (roadmap). | CF dashboard → n8n |
| 12 | **Errores** | Todo error de producción se registra en [28-Knowledge-Base.md](28-Knowledge-Base.md) con causa raíz — el mismo error dos veces = falta una automatización o un test. | KB |
| 13 | **Optimización** | Solo con métrica antes/después ([24-Metrics.md](24-Metrics.md)). | Lighthouse, CF analytics |
| 14 | **Documentación** | README actualizado si cambió el uso; CLAUDE.md si cambió el contexto para IAs. No más que eso — la documentación pesada vive en el handbook. | — |
| 15 | **Retrospectiva** | 3 preguntas al cerrar: ¿qué tardó más de lo esperado? ¿qué hice a mano que era automatizable? ¿qué reutilizaría? Respuestas → KB. | KB |
| 16 | **Automatización** | Lo detectado en 15 entra a [23-Automations.md](23-Automations.md) con formato de decisión. El ciclo termina cuando la repetición muere. | n8n / scripts / skills |

## Las 3 preguntas permanentes (Workflow-Agent)

Sobre cada paso, continuamente:

1. **¿Puede eliminarse?** (ej.: paso 3 se elimina para features que heredan arquitectura)
2. **¿Puede automatizarse?** (ej.: paso 8-9 completos con Actions)
3. **¿Puede reducirse a un clic/comando?** (ej.: crear proyecto nuevo = 1 script, ver [23-Automations.md](23-Automations.md))

## Atajos válidos (declarados, no silenciosos)

- **Hotfix de producción:** 5→6→7→9→10, y los pasos saltados (retro, docs) se hacen dentro de las
  24h siguientes.
- **Experimento desechable:** vive en `E:\Pruebas`, exento del pipeline, PERO: si sobrevive 2
  semanas o se enseña a un cliente, entra al pipeline completo o se borra.
