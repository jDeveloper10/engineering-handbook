---
title: "Proceso de Investigación Tecnológica Continua"
category: 15_Knowledge_System
doc_type: estandar
tags: [knowledge, investigacion, proceso, fuentes]
summary: "Cadencia y presupuesto de la investigación tecnológica, disparadores ad-hoc fuera de cadencia, el entregable RESEARCH_NOTE y la jerarquía de fuentes primarias admitidas."
keywords: [investigacion, cadencia, research-note, fuentes-primarias, disparadores]
updated: 2026-07-21
status: current
---

# RESEARCH_PROCESS — Investigación tecnológica continua

> **Propósito:** definir el proceso ejecutable por una IA (sesión dedicada de Claude Code) para
> mantener el stack vigilado sin caer en investigación infinita. Este documento es el **proceso
> operativo** del lado "radar tecnológico" del sistema de conocimiento; la memoria resultante la
> gobierna `Engineering-OS/Agents/Knowledge-Agent.md` y el filtro de adopción lo gobierna la
> matriz de `Engineering-OS/05-Decision-Matrix.md`. Este documento **no los reemplaza**: los
> conecta y los profundiza para el caso concreto de "salió algo nuevo, ¿nos importa?".
>
> **Depende de:** `00_HANDBOOK_FORMAT.md` (convenciones) · `05-Decision-Matrix.md` (matriz de
> adopción) · `Agents/Knowledge-Agent.md` (destino del conocimiento) · `Agents/Tool-Agent.md`
> (guardián anti-herramienta-nueva) · `KNOWLEDGE_SYSTEM_STANDARD.md` (frontmatter e indexación
> de las notas — ese documento manda sobre el formato de metadatos).
>
> **Consumidor:** una IA en sesión periódica acotada, no un humano con tiempo infinito.

---

## 1. Relación con los agentes de Engineering-OS (leer antes de ejecutar)

Este proceso hereda tres reglas ya establecidas y **no las re-litiga**:

- De **Tool-Agent**: nada entra al stack sin pasar la matriz de adopción de `05-Decision-Matrix.md`
  (sección "Matriz de adopción de tecnología"). Este proceso produce el *insumo* para esa matriz
  (la RESEARCH_NOTE), no un canal paralelo de adopción.
- De **Knowledge-Agent**: conocimiento ≠ noticia. Las noticias se pudren; solo lo reutilizable
  sobrevive. Una RESEARCH_NOTE es la forma intermedia: más que una noticia, menos que una entrada
  de KB — y solo asciende a `28-Knowledge-Base.md` o a un estándar si la recomendación se ejecuta.
- De **05-Decision-Matrix**: las "decisiones tipo ya tomadas" (Supabase para todo lo nuevo,
  Pages con Git, TypeScript obligatorio, etc.) no se reabren por hype. Reabrirlas requiere
  **nueva evidencia**, y esa evidencia se documenta en una RESEARCH_NOTE que lo diga explícitamente.

**Por qué:** el riesgo real de un proceso de investigación en un equipo de una persona no es
investigar poco — es que la investigación se convierta en excusa para reabrir decisiones cerradas
o adoptar herramientas sin filtro. Los guardianes ya existen; este proceso se subordina a ellos.

## 2. Cadencia y presupuesto

### 2.1 Sesión mensual rotativa [REQUIRED]

**Regla:** UNA sesión de investigación al mes, de ~1 hora de trabajo efectivo de IA, sobre UNA
sola área. Las áreas rotan en ciclo fijo de 4 meses:

| Mes del ciclo | Área | Qué cubre (con el stack real) |
|---|---|---|
| 1 | Frameworks | React, Vite, ecosistema de UI del handbook |
| 2 | Herramientas | wrangler, CLIs, MCPs propios, tooling de `14_DX` |
| 3 | Plataforma | Cloudflare Workers/Pages, Supabase (plataforma y `supabase-js`) |
| 4 | IA | Claude Code, modelos, skills/agentes, `13_AI_Rules` |

No se "investiga todo siempre": si durante el mes de Frameworks aparece algo interesante de
Supabase y no dispara ninguna condición de la sección 3, espera a su mes.

**Por qué:** un developer solo con IAs tiene presupuesto de atención, no de horas-hombre. La
rotación garantiza que ninguna área pasa más de 4 meses sin mirarse, y el tope de 1 hora obliga a
priorizar fuentes primarias en vez de leer internet entero. Un proceso sin tope de tiempo no se
ejecuta: se pospone para siempre o se come el día.

### 2.2 Presupuesto de salida [REQUIRED]

**Regla:** la sesión produce **0 a 2 RESEARCH_NOTEs**, nunca más. Si no hubo nada relevante,
la salida legítima es una línea en el registro de la sesión: "revisado <área> <mes>: sin cambios
que nos afecten" — eso también es un entregable (evita re-revisar lo mismo el próximo ciclo).

**Por qué:** hereda el criterio de Knowledge-Agent ("la mayoría de sesiones producen CERO
entradas"). Un proceso medido por volumen de notas produce ruido; medido por relevancia, produce
señal. Cero notas es un resultado válido y frecuente.

### 2.3 Guion de la sesión (para la IA que la ejecuta)

1. **(5 min)** Leer las RESEARCH_NOTEs previas del área (en `research/`) — ¿hay algún
   "re-evaluar en N meses" que ya venció? Si sí, ese tema entra primero.
2. **(35 min)** Revisar fuentes primarias del área (sección 5): changelogs desde la última
   revisión, roadmaps oficiales, avisos de deprecation, avisos de seguridad.
3. **(15 min)** Para cada hallazgo que pase el filtro de relevancia (sección 4.2): escribir la
   RESEARCH_NOTE con la plantilla de la sección 7.
4. **(5 min)** Cierre: registrar "área revisada + fecha + notas producidas (o cero)". Si alguna
   nota recomienda "adoptar", generar el HANDOFF correspondiente (sección 6).

## 3. Disparadores ad-hoc (fuera de cadencia)

**Regla [RECOMMENDED]:** además de la sesión mensual, se abre una mini-sesión de investigación
(≤30 min, 1 RESEARCH_NOTE máximo) solo cuando ocurre uno de estos eventos sobre una pieza del
stack real (React, Vite, wrangler, `supabase-js`, TypeScript, Tailwind):

1. **Release major** (cambio de versión mayor) de una dependencia directa de proyectos activos.
2. **Deprecation anunciada** de una API/servicio que el código en producción usa hoy.
3. **Vulnerabilidad crítica** (CVE alta/crítica o aviso oficial del proveedor) que afecta una
   versión desplegada. Este caso es el único que puede escalar a acción inmediata sin esperar
   el proceso completo — la seguridad de producción manda sobre la cadencia; el estándar de
   `05_Security` gobierna la respuesta, esta nota solo la documenta.

Todo lo demás — un framework nuevo, un post viral, "X mató a Y" — **no es disparador**. Si es
relevante de verdad, seguirá siéndolo en la sesión mensual de su área.

**Por qué:** los tres disparadores comparten una propiedad: son eventos de **fuente primaria con
consecuencia directa sobre código desplegado**. El hype no la tiene. Distinguirlos por esa
propiedad (y no por "qué tan interesante suena") es lo que hace el criterio ejecutable por una IA.

## 4. El entregable: RESEARCH_NOTE

### 4.1 Formato [REQUIRED]

**Regla:** toda investigación produce una RESEARCH_NOTE de **máximo 1 página** (~60 líneas de
markdown) con esta estructura fija, en este orden:

1. **Qué es** — 2-4 líneas, hechos verificables con fuente primaria enlazada.
2. **Qué cambia para NOSOTROS** — el impacto sobre el stack y los proyectos reales
   (React + Workers + Supabase, proyectos listados en el ecosistema), no en abstracto.
   Si la respuesta honesta es "nada", la nota termina aquí con recomendación "ignorar".
3. **Recomendación** — exactamente una de: `adoptar` · `probar en side-project` · `ignorar` ·
   `re-evaluar en N meses` (con N explícito).
4. **Documento del handbook a actualizar si se adopta** — ruta concreta (ej.
   `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` sección X). Si no se sabe qué documento
   tocaría, la recomendación no puede ser `adoptar` (señal de que no está entendido el impacto).

Se guarda en `15_Knowledge_System/research/YYYY-MM-<tema>.md` (tema en kebab-case, ej.
`2026-08-react-compiler-estable.md`) con el frontmatter definido en
`KNOWLEDGE_SYSTEM_STANDARD.md` — ese estándar es la autoridad sobre los campos de metadatos;
esta plantilla (sección 7) muestra un ejemplo y se ajusta a él si difieren.

**Por qué:** la estructura fija hace las notas comparables y consultables por una IA en segundos
("¿qué dijimos de Vite 7?"). El tope de 1 página fuerza la destilación: si no cabe en una página,
todavía no se entendió. Y el campo 4 es el candado del principio "handbook primero, código
después" — obliga a saber *dónde* aterrizaría el cambio antes de recomendarlo.

### 4.2 Filtro de relevancia (antes de escribir la nota)

Una nota solo se escribe si el hallazgo cumple al menos uno:

- Afecta código que está en producción o en desarrollo activo hoy.
- Elimina una fricción ya registrada (en el registro de DX de `14_DX` o en la KB).
- Cierra un "re-evaluar en N meses" pendiente de una nota anterior.
- Es un disparador ad-hoc de la sección 3.

Lo que no cumple ninguno, no genera nota. (Herencia directa del checklist de Knowledge-Agent:
"¿es conocimiento o es noticia?".)

## 5. Fuentes: primarias sobre hype

**Regla [REQUIRED]:** la investigación se basa en fuentes primarias. Orden de confianza:

1. **Changelogs y release notes oficiales** (GitHub releases de react, vite, wrangler,
   supabase-js; blogs oficiales de Cloudflare/Supabase/Anthropic).
2. **Documentación oficial y guías de migración** del proveedor.
3. **RFCs y roadmaps públicos** de los proyectos (para el campo "re-evaluar en N meses").
4. **Avisos de seguridad** (GitHub Security Advisories, avisos del proveedor).

Threads de opinión, rankings de popularidad, videos de "X está muerto" y benchmarks de terceros
**no son base de una RESEARCH_NOTE**. Como máximo sirven para enterarse de que algo existe; la
nota se escribe contra la fuente primaria o no se escribe.

**Por qué:** una IA es especialmente vulnerable a amplificar consenso de internet — el hype llega
pre-masticado y la fuente primaria hay que ir a leerla. Exigir la fuente primaria en la nota
(campo "Qué es" con enlace) hace el sesgo detectable en revisión: si no hay enlace oficial, la
nota no está terminada.

## 6. Regla anti-hype: el camino único a producción

**Regla [REQUIRED]:** nada nuevo se usa en un proyecto de producción sin cumplir LAS TRES
condiciones, en orden:

1. **Problema real ya sentido.** Existe fricción/limitación documentada ANTES de conocer la
   herramienta (registro de DX de `14_DX`, entrada de KB, bug repetido). "Es más moderno" no es
   un problema. Esta condición es la primera pregunta de la matriz de adopción de
   `05-Decision-Matrix.md` — aquí se endurece: el problema debe estar **escrito con fecha
   anterior** al hallazgo, no reconstruido a posteriori para justificarlo.
2. **Prueba en proyecto no crítico.** Un side-project, prototipo o proyecto interno lo usó de
   verdad (no un hello-world) y la RESEARCH_NOTE se actualizó con el resultado.
3. **El estándar se actualiza ANTES que el código de producción.** El documento del handbook
   identificado en el campo 4 de la nota se modifica primero (con la regla en capa agnóstica +
   implementación, según `00_HANDBOOK_FORMAT.md`), y solo después se escribe código de
   producción que lo use. **El handbook se actualiza primero, el código después.**

El orden importa: sin (1) no se hace (2); sin (2) no se hace (3). Saltarse un paso invalida la
adopción aunque la herramienta sea buena.

**Por qué (3) y no al revés:** si el código de producción adopta algo antes que el estándar, las
próximas sesiones de IA generarán código contra el estándar viejo y el proyecto queda partido en
dos convenciones — exactamente el híbrido Firebase+Supabase que la auditoría ya encontró en
jonnyTrader y que `05-Decision-Matrix.md` prohíbe repetir. El handbook es la fuente de verdad de
las IAs: si no está ahí, para las IAs no existe.

**HANDOFF de adopción:** cuando una nota concluye `adoptar`, la sesión genera la recomendación en
formato de 11 campos de `05-Decision-Matrix.md` (la nota es el insumo, no el sustituto) y la
entrega al flujo de decisión — la matriz ordena, Jeilin decide. Una RESEARCH_NOTE nunca autoriza
por sí sola tocar producción.

## 7. Plantilla de RESEARCH_NOTE

Copiar tal cual a `15_Knowledge_System/research/YYYY-MM-<tema>.md`. Si
`KNOWLEDGE_SYSTEM_STANDARD.md` define campos de frontmatter distintos, ese documento manda.

```markdown
---
tipo: research-note
fecha: YYYY-MM-DD
area: frameworks | herramientas | plataforma | ia
tema: <kebab-case, igual que el nombre del archivo>
disparador: sesion-mensual | release-major | deprecation | vulnerabilidad
recomendacion: adoptar | probar-side-project | ignorar | re-evaluar
re_evaluar: YYYY-MM   # solo si recomendacion = re-evaluar
estado: abierta | ejecutada | descartada | superada
---

# <Tema> — RESEARCH_NOTE YYYY-MM

## Qué es
2-4 líneas. Hechos, no adjetivos. Enlace a la fuente primaria (changelog/docs/RFC oficial).

## Qué cambia para NOSOTROS
Impacto concreto sobre el stack real (React/Vite, Workers/wrangler, Supabase/supabase-js) y
sobre proyectos nombrados. Qué código existente se ve afectado y cómo. Si la respuesta es
"nada hoy": decirlo y terminar con recomendación `ignorar` o `re-evaluar`.

## Recomendación
Una sola: **adoptar** / **probar en side-project** / **ignorar** / **re-evaluar en N meses**.
1-3 líneas de justificación. Si es `adoptar`: confirmar que cumple la condición (1) de la regla
anti-hype (enlace a la fricción documentada) y qué proyecto no crítico hará la condición (2).

## Handbook a actualizar si se adopta
- `<ruta/DOCUMENTO.md>` — sección/regla concreta que cambiaría y en qué sentido.
(Obligatorio si la recomendación es `adoptar` o `probar en side-project`; "ninguno" invalida
la recomendación de adoptar.)
```

Ciclo de vida del campo `estado`: nace `abierta` → pasa a `ejecutada` (se adoptó y el handbook
se actualizó — enlazar el commit/documento), `descartada` (se probó y no valió la pena — decir
por qué, para no re-investigarlo) o `superada` (un release posterior la dejó obsoleta — enlazar
la nota nueva, herencia del marcado `[superada por X]` de Knowledge-Agent: no se borra, se marca).

## 8. Checklist de la sesión de investigación

- [ ] ¿Es el área que toca este mes del ciclo (o un disparador legítimo de la sección 3)?
- [ ] ¿Revisé los "re-evaluar en N meses" vencidos antes de buscar temas nuevos?
- [ ] ¿La sesión cupo en ~1h (mensual) o ≤30 min (ad-hoc)?
- [ ] ¿Produje 0-2 notas, cada una de ≤1 página, con las 4 secciones y frontmatter?
- [ ] ¿Cada "Qué es" tiene enlace a fuente primaria (no threads/opinión)?
- [ ] ¿Cada "Qué cambia" habla del stack y proyectos REALES, no en abstracto?
- [ ] ¿Toda recomendación `adoptar` cumple: problema previo documentado + plan de prueba en
      no-crítico + documento del handbook identificado?
- [ ] ¿Generé el HANDOFF en formato de 11 campos para las notas `adoptar` (05-Decision-Matrix)?
- [ ] ¿Registré el cierre de sesión aunque haya producido cero notas?
