# 07 — Estructura de proyectos y residencia

## Regla de residencia (resuelve la fragmentación C:/E: detectada en auditoría)

```
C:\trabajo\Trabajo\
├── 00_AI_Systems\      ← agentes, MCPs, herramientas de IA en uso
├── 01_Clientes\        ← proyectos facturables activos
└── 02_Propios\         ← productos propios activos

E:\
├── ENGINEERING_HANDBOOK\   ← estándares + este OS (fuente de verdad)
├── Trabajo\05_Archive\     ← TODO lo terminado/abandonado (única carpeta de archivo)
├── Pruebas\                ← experimentos desechables (exentos de pipeline, ver 04-Workflow)
└── _Assets_Originales\     ← assets fuente
```

- **[REQUIRED]** Un proyecto vive en UN solo lugar. Si existe en ambos discos, la copia vieja se
  mueve a `05_Archive` el mismo día que se detecta.
- **[REQUIRED]** Activo = tocado en los últimos 60 días O en producción con usuarios. Todo lo demás
  se archiva. (La auditoría encontró ~60 proyectos; los activos reales son ~6.)
- **[REQUIRED]** Todo proyecto activo es repo git CON remote en `github.com/JCDIGITALL`. Sin
  excepciones — la auditoría encontró 41+ proyectos sin git/remote, incluido `workers-template`,
  la pieza de infraestructura más reutilizada del ecosistema.

## Estructura interna estándar (proyecto web típico)

```
<proyecto>/
├── src/               # componentes, pages, hooks, lib (ver handbook 01_Frontend)
├── public/
├── worker-*/          # workers del producto (si aplica), cada uno con su wrangler.jsonc
├── .github/workflows/ # ci.yml mínimo (build en push) — ver 20-Deployment.md
├── README.md          # plantilla de 26-Templates.md — qué es, cómo correr, cómo desplegar
├── CLAUDE.md          # contexto para IAs: stack, comandos, decisiones no obvias
├── .env.example       # TODAS las variables, sin valores
└── .gitignore         # cubre .env, .dev.vars, node_modules, dist, .wrangler
```

- **[REQUIRED]** README.md + CLAUDE.md + .env.example existen desde el día 1 (los genera la
  automatización de proyecto nuevo — ver 23-Automations.md A1).
- **[RECOMMENDED]** Nombres de carpeta: kebab-case, sin espacios ("Gaby and Beauty store" y
  "juego manuel" rompen tooling — renombrar al archivarlos o tocarlos).

## Workers

- Base: `workers-template` (6 workers: admin, auth, payments, trading, communications, user).
  **[REQUIRED]** Nuevo worker = copiar del template, nunca desde cero. El template mismo debe
  convertirse en repo git con remote (P0 del roadmap).
- Un worker por dominio de responsabilidad; los workers de un producto viven en el repo del
  producto (patrón JCDigital/worker-pago).
