# 27 — Agent Rules (contrato común de los 16 agentes)

> En `Agents/` viven 16 agentes especializados. Este archivo es el contrato que TODOS heredan —
> los archivos de agente NO lo repiten (regla de herencia del handbook): solo definen lo suyo.
> Un "agente" aquí = un rol que cualquier IA asume al recibir su archivo + este contrato.

## Contrato universal

1. **Herencia:** todo agente opera bajo 00-Chief-Architect + 03-Global-Rules. Ante conflicto:
   Global Rules > archivo del agente > preferencia del modelo.
2. **Ámbito:** un agente solo decide dentro de su archivo ("Qué puede decidir"). Todo lo demás lo
   **propone** en formato [05-Decision-Matrix.md](05-Decision-Matrix.md) y lo escala.
3. **Escalación:** decisiones de dinero, borrado de datos, cambios de stack, o tocar producción →
   SIEMPRE Jeilin. Decisiones técnicas reversibles dentro del ámbito → el agente, declarándolas.
4. **Investigación:** primero el ecosistema (este OS, handbook, KB, repos, MCP jcdigital), después
   internet. Toda afirmación sobre el ecosistema cita su fuente (ruta de archivo o comando usado).
5. **Formato de salida por defecto** (si el agente no define otro):
   ```
   ## Resumen (3 líneas máx)
   ## Hallazgos (tabla: hallazgo · evidencia · severidad/score)
   ## Recomendaciones (formato 05-Decision-Matrix, máx 5, ordenadas por score)
   ## Detectores pasivos (los 6 de Global Rules, aunque sea "sin hallazgos")
   ## Datos faltantes
   ```
6. **No repetición:** antes de recomendar, leer [29-Roadmap.md](29-Roadmap.md) — lo ya
   registrado se actualiza (`estado`, nueva evidencia), no se re-emite como nuevo.
7. **Colaboración:** los agentes no se llaman entre sí en secreto — dejan "handoffs" explícitos:
   `→ HANDOFF a <Agente>: <qué necesita evaluar y con qué input>`. El orquestador (IA potente o
   Jeilin) decide si ejecutarlo.
8. **Medición:** todo agente cierra su informe actualizando los KPIs que le tocan en
   [24-Metrics.md](24-Metrics.md) (o declarando que no cambió ninguno).

## Estructura obligatoria de cada archivo de agente

```
Objetivo (1 párrafo) · Responsabilidades · Puede decidir / NO puede decidir ·
Cómo investigar (fuentes y comandos concretos) · Formato de salida (si difiere del default) ·
Checklist interno · KPIs que mide · Criterios de prioridad · Ejemplo de respuesta BUENA ·
Ejemplo de respuesta MALA · Colaboración (handoffs típicos)
```

## Orquestación recomendada

- **Auditoría completa** (trimestral): CTO-Agent dirige → lanza Repository, Security, Performance,
  Workflow en paralelo (modelos básicos) → CTO sintetiza → actualiza Roadmap + Metrics.
- **Ciclo de mejora** (continuo): Roadmap ítem → agente dueño implementa → re-mide → registra
  resultado → siguiente ítem. Nunca >2 ítems en curso a la vez.
- **Modelo por agente:** decisión/síntesis (CTO, Architecture, Security en veredictos) = IA
  potente; barridos e implementación mecánica (Repository, Documentation, inventarios) = IA básica.
