# ENGINEERING_INTELLIGENCE — Auto-análisis del propio trabajo

> **Propósito:** definir el proceso ejecutable por una IA (sesión dedicada de Claude Code) que
> mira el trabajo YA hecho — git, sesiones de IA, bugs, fricción — y lo convierte en un puñado de
> acciones de mejora concretas. Es el lado "espejo" del sistema de conocimiento: RESEARCH_PROCESS
> mira hacia afuera (qué cambió en el mundo); este proceso mira hacia adentro (qué nos está
> costando trabajo a nosotros).
>
> **Depende de:** `00_HANDBOOK_FORMAT.md` (convenciones) · `Agents/Knowledge-Agent.md` (destino
> de las lecciones y sus KPIs de repetición) · `Agents/Tool-Agent.md` (dueño del inventario de
> herramientas y su uso real) · `Agents/Opportunity-Agent.md` (dueño de activos dormidos y
> anti-oportunidades de negocio) · `14_DX` (registro de fricción y destino de snippets/templates)
> · `06_Testing` (destino de gates nuevos) · `05-Decision-Matrix.md` (formato si una acción
> escala a recomendación mayor).
>
> **Consumidor:** una IA en sesión mensual acotada de ~30 min. No es una auditoría, no es un
> retro largo, no es un reporte para leer — es una máquina de encontrar 1-3 acciones que valgan
> la pena.

---

## 1. Relación con los agentes de Engineering-OS (leer antes de ejecutar)

Este proceso **no crea un agente nuevo** — es la rutina operativa que alimenta a tres agentes
existentes, cada uno dueño de su territorio:

- **Knowledge-Agent** es el dueño de la KB y del detector "preguntas/decisiones repetidas". Este
  proceso ejecuta ese detector con cadencia fija y le entrega el resultado; la decisión de qué
  entra a `28-Knowledge-Base.md` y qué asciende a estándar sigue siendo suya (vía
  Documentation-Agent cuando una lección se repite en 3+ proyectos).
- **Tool-Agent** es el dueño del principio "herramienta sin uso 30 días → conectar o archivar".
  La pregunta 4 de la sesión (sección 3) es la ejecución mensual de ese principio; el retiro o
  conexión de la herramienta es un HANDOFF a Tool-Agent, no una acción que este proceso ejecuta
  por su cuenta (Tool-Agent verifica uso real y handoffs con otros agentes antes de retirar).
- **Opportunity-Agent** es el dueño de activos dormidos y anti-oportunidades de negocio. Si este
  proceso tropieza con una señal de ese tipo (ej. una línea de proyectos que solo genera bugs y
  ningún ingreso), la registra como HANDOFF a Opportunity-Agent — no la desarrolla aquí. Este
  proceso se limita a ingeniería: repetición de trabajo, bugs, fricción, herramientas.

**Por qué:** los agentes definen QUIÉN es dueño de cada decisión; lo que faltaba era el CUÁNDO y
el CÓMO sistemáticos. Sin cadencia, "detectar repetición" solo ocurre cuando alguien se acuerda —
es decir, nunca. Este documento aporta la cadencia y el guion; la autoridad no se mueve.

## 2. Señales que se recolectan (pasivas — cero instrumentación nueva)

**Regla [REQUIRED]:** el proceso trabaja SOLO con señales que ya existen como subproducto del
trabajo normal. Prohibido instrumentar, trackear o pedir registro manual adicional para
alimentarlo.

| Señal | Dónde vive ya | Qué pregunta responde | A dónde apunta el hallazgo |
|---|---|---|---|
| Historial de git | `git log` de los repos activos del mes | ¿Qué tipo de cambio se repite? (mismos archivos de config retocados, mismo tipo de fix, mismo boilerplate commiteado) | Script/template en `14_DX`, o regla de estándar |
| Sesiones de Claude Code | Transcripts/historial de sesiones de los proyectos | ¿Qué se le pide a la IA una y otra vez con las mismas palabras? | Snippet/template/skill/estándar en `14_DX` — si hay que explicárselo a la IA cada vez, falta un documento |
| Issues/bugs del mes | Issues de los repos, fixes en git, entradas T9 de la KB | ¿Qué CLASE de bug apareció más de una vez? (no el bug puntual — la clase: "otra vez CORS", "otra vez un null de supabase-js sin manejar") | Regla nueva en el estándar del dominio, o gate en `06_Testing` |
| Fricción de DX | El registro de fricción que define `14_DX` | ¿Qué estorbó al trabajar? (ya registrado en el momento en que dolió) | Lo que `14_DX` prescriba para esa fricción |

**Por qué pasivas:** un developer solo no va a mantener un sistema de métricas sobre sí mismo —
todo proceso que exija registro manual extra muere en dos semanas (la KB de Knowledge-Agent ya
opera bajo el mismo supuesto: se captura al cierre de sesiones, no con formularios). Las cuatro
fuentes de la tabla se generan solas; la sesión mensual solo las lee.

**Límite práctico [RECOMMENDED]:** la lectura de señales cubre el último mes (desde la sesión
anterior), no el histórico completo. `git log --since` y los transcripts del mes bastan; si un
patrón es real, aparecerá dentro de la ventana.

## 3. La sesión mensual [REQUIRED]

**Regla:** una sesión de ~30 minutos al mes (recomendado: anclada a la sesión mensual de
RESEARCH_PROCESS, mismo día, para que ninguna de las dos se olvide). La sesión responde CUATRO
preguntas fijas, siempre las mismas, en este orden:

### P1 — ¿Qué hice ≥3 veces a mano este mes?
Buscar en git y transcripts: el mismo setup repetido, el mismo prompt largo re-escrito, la misma
secuencia de comandos, el mismo bloque de código adaptado.
**→ Acción tipo: automatizar** — script, skill de Claude Code, template o snippet en `14_DX`.

### P2 — ¿Qué decisión tomé ≥2 veces?
Buscar en transcripts y commits: la misma pregunta resuelta dos veces ("¿dónde van los tipos
compartidos?", "¿cómo nombro este worker?"), con o sin el mismo resultado.
**→ Acción tipo: documentar como estándar** — la regla maestra del handbook: una decisión que se
toma dos veces se documenta para no tomarla una tercera. Destino: el estándar del dominio
correspondiente, o la KB si aún no da para regla (criterio de ascenso: Knowledge-Agent →
Documentation-Agent).

### P3 — ¿Qué clase de bug se repitió?
Buscar en issues/fixes del mes: dos bugs distintos de la misma clase cuentan como repetición.
**→ Acción tipo: regla o gate** — regla en el estándar del dominio (si es de diseño/convención) o
gate verificable en `06_Testing` (si una verificación automática lo habría atrapado). Preferir el
gate cuando ambos aplican: una regla se puede ignorar, un gate no.

### P4 — ¿Qué herramienta pagada o instalada NO usé este mes?
Cruzar el inventario de Tool-Agent contra uso real del mes (logs, flujos, git).
**→ Acción tipo: eliminar** — HANDOFF a Tool-Agent para conectar o archivar (su principio de 30
días; la verificación final de "nadie más la usa" es suya).

**Por qué estas cuatro y no más:** cada pregunta tiene umbral numérico (≥3, ≥2, ≥2, =0 usos) y
acción tipo predefinida — una IA puede responderlas sin juicio abierto y sin alargar la sesión.
Preguntas del tipo "¿cómo me sentí trabajando este mes?" no son ejecutables por una IA ni
producen acciones; quedan fuera a propósito.

## 4. El entregable

**Regla [REQUIRED]:** la sesión produce UN archivo en
`15_Knowledge_System/intelligence/YYYY-MM.md` con:

- **Hallazgos: 5-10 líneas en total.** Una línea por hallazgo con su evidencia mínima
  (ej. "P1: configuré CORS a mano en 3 workers — commits a1b2c3, d4e5f6, 07g8h9").
- **Acciones: máximo 3**, cada una con dueño ejecutor y tamaño. El dueño por defecto es "una IA
  en la próxima sesión de trabajo" — si una acción no la puede ejecutar una IA con el handbook
  en la mano, está mal formulada (partirla o convertirla en recomendación de 11 campos para
  `05-Decision-Matrix.md` si es grande de verdad).
- **Seguimiento de la sesión anterior:** estado de las acciones del mes pasado
  (`hecha` / `pendiente` / `descartada + por qué`). Una acción `pendiente` dos meses seguidos
  se descarta o se re-formula más pequeña — no se arrastra indefinidamente.

No es un reporte largo que nadie lee: si el archivo pasa de ~30 líneas, sobra texto, no faltan
hallazgos. Hubo meses sin nada que valga la pena: el archivo dice "sin hallazgos accionables" y
las 4 preguntas con respuesta vacía — eso también cuenta como sesión ejecutada (y alimenta la
regla de la sección 5).

Frontmatter según `KNOWLEDGE_SYSTEM_STANDARD.md`; ejemplo de referencia (ese estándar manda si
difieren):

```markdown
---
tipo: intelligence
fecha: YYYY-MM-DD
periodo: YYYY-MM
acciones_propuestas: 0-3
acciones_mes_anterior: X hechas / Y pendientes / Z descartadas
---

# Engineering Intelligence — YYYY-MM

## Hallazgos (5-10 líneas)
- P1 (≥3 veces a mano): ...evidencia...
- P2 (decisión repetida): ...evidencia...
- P3 (clase de bug repetida): ...evidencia...
- P4 (herramienta sin uso): ...evidencia...

## Acciones (máximo 3)
1. [tipo: automatizar|documentar|gate|eliminar] Qué + dónde aterriza (ruta del handbook/14_DX)
   + dueño (IA/Jeilin) + tamaño (XS/S).
2. ...
3. ...

## Seguimiento del mes anterior
- Acción 1 de YYYY-MM: hecha | pendiente | descartada (por qué).
```

**Por qué máximo 3 acciones:** herencia directa del checklist de Opportunity-Agent ("máximo 3
oportunidades por informe — cartera corta o no es priorización"). Diez acciones propuestas y cero
ejecutadas vale menos que una propuesta y una ejecutada. Y el tamaño importa: acciones XS/S
(≤4h, escala de `05-Decision-Matrix.md`) se ejecutan; las L/XL se posponen para siempre — si un
hallazgo pide una acción grande, el entregable correcto es la recomendación de 11 campos, no una
"acción" que no va a pasar.

## 5. Criterio de éxito honesto [REQUIRED]

**Regla:** este proceso se mide por **acciones ejecutadas**, no por reportes generados. El
seguimiento de la sección 4 es el instrumento de medición: cada sesión cuenta cuántas acciones
del mes anterior se hicieron de verdad.

**Cláusula de auto-degradación:** si DOS meses consecutivos la sesión no produce ninguna acción
que valga la pena ejecutar (cero propuestas, o propuestas que el seguimiento muestra descartadas
por triviales), la cadencia baja a **trimestral** — y se registra en el archivo del mes en que se
decide. Se vuelve a mensual cuando un trimestre produzca 2+ acciones ejecutadas (señal de que el
ritmo de trabajo volvió a generar material).

**Por qué:** el proceso predica "elimina lo que no se usa" (P4) y "no acumules reportes que nadie
lee"; sería incoherente que él mismo fuera un reporte mensual sin consecuencias. Un proceso de
mejora que no obedece su propia regla anti-desperdicio es la primera cosa que debería eliminar.
La degradación es a trimestral y no a cero porque las señales (git, bugs, fricción) se siguen
acumulando solas — el costo de leerlas cada 3 meses es bajo y el detector de repeticiones de
Knowledge-Agent lo necesita con alguna cadencia.

## 6. Anti-patrones (qué NO es este proceso)

- **No es una auditoría del ecosistema.** Eso es trabajo de los agentes de Engineering-OS con su
  propio alcance. Aquí: último mes, cuatro preguntas, 30 minutos.
- **No es un diario.** "Este mes trabajé mucho en el rediseño" es el ejemplo MALO de
  Knowledge-Agent — sin patrón repetido y evidencia, no es hallazgo.
- **No propone herramientas nuevas.** Si una acción parece pedir una herramienta nueva, el orden
  es el de Tool-Agent: ¿qué herramienta YA poseída lo resuelve? Lo nuevo pasa por
  RESEARCH_PROCESS y la matriz de adopción, nunca directo desde aquí.
- **No re-litiga decisiones registradas.** Si P2 detecta una decisión repetida que YA está
  documentada, el hallazgo no es "documentarla" sino "¿por qué el documento no se está
  consultando?" — eso es el KPI de fallo de Knowledge-Agent (decisión re-discutida que ya estaba
  registrada) y el HANDOFF va hacia allá: quizá el documento está mal enlazado desde el
  CLAUDE.md del proyecto, no ausente.

## 7. Checklist de la sesión

- [ ] ¿Leí las 4 fuentes pasivas del último mes (git, transcripts, issues, registro DX) y nada más?
- [ ] ¿Respondí las 4 preguntas fijas con sus umbrales (≥3, ≥2, ≥2 clase, 0 usos)?
- [ ] ¿Cada hallazgo tiene evidencia concreta (commits, sesión, issue), no impresión?
- [ ] ¿Hallazgos en 5-10 líneas y máximo 3 acciones, cada una con dueño y tamaño XS/S?
- [ ] ¿Las acciones grandes se convirtieron en recomendación de 11 campos en vez de "acción"?
- [ ] ¿Registré el estado de las acciones del mes anterior (hecha/pendiente/descartada)?
- [ ] ¿Los hallazgos de territorio ajeno salieron como HANDOFF (Tool-Agent, Opportunity-Agent,
      Knowledge-Agent) en vez de ejecutarse aquí?
- [ ] ¿Apliqué la cláusula de auto-degradación si llevamos 2 meses sin acciones que valgan?
- [ ] ¿La sesión cupo en ~30 min y el archivo en ~30 líneas?
