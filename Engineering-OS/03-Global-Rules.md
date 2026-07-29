# 03 — Reglas globales (no negociables)

> Aplican a TODA IA, en TODO proyecto, en TODA tarea. Formato del handbook: cada regla es
> [REQUIRED]. Si una IA no puede cumplir una regla, se detiene y lo dice — no improvisa.

## Sobre información y honestidad

- **[REQUIRED] Nunca asumir información.** Si falta un dato, se responde con
  `DATO FALTANTE: <qué falta> — <cómo conseguirlo>`. Inventar rutas, precios, métricas o nombres de
  servicios es la falta más grave del sistema.
- **[REQUIRED] Nunca repetir recomendaciones.** Antes de recomendar, consultar
  [29-Roadmap.md](29-Roadmap.md) y [28-Knowledge-Base.md](28-Knowledge-Base.md). Si ya existe:
  referenciar y actualizar estado, no re-emitir.
- **[REQUIRED] Toda decisión se justifica** con al menos uno: un hallazgo de auditoría, una métrica
  de [24-Metrics.md](24-Metrics.md), una regla del handbook, o una restricción declarada por Jeilin.
- **[REQUIRED] Reportar resultados fielmente.** Si un test falla, se muestra el error. Si un paso
  se saltó, se dice. "Debería funcionar" no es un estado válido; los estados válidos son:
  `VERIFICADO`, `NO VERIFICADO (motivo)`, `FALLÓ (evidencia)`.

## Sobre recomendaciones

- **[REQUIRED]** Toda recomendación usa el formato completo de
  [05-Decision-Matrix.md](05-Decision-Matrix.md): Problema · Impacto · Esfuerzo · Prioridad ·
  Beneficio esperado · Tiempo estimado · Horas ahorradas · Riesgo · Dependencias · Plan ·
  Cómo medir el éxito.
- **[REQUIRED]** Priorizar siempre por impacto/esfuerzo, nunca por novedad o interés técnico.
- **[REQUIRED]** Toda propuesta de proceso incluye la pregunta: *¿esto se puede automatizar en vez
  de documentar?* y la respuesta explícita.

## Sobre código

- **[REQUIRED]** El handbook manda: `E:\ENGINEERING_HANDBOOK` es la autoridad técnica. Una IA no
  genera código que rompa una regla REQUIRED del dominio correspondiente.
- **[REQUIRED]** Código de pagos, auth o datos de clientes: no se toca sin leer
  [16-Security.md](16-Security.md) y sin plan de rollback.
- **[REQUIRED]** Secretos jamás en código, commits, logs ni respuestas de chat. Existencia de un
  secreto se reporta como "existe X en `<archivo>`", nunca con su valor.
- **[REQUIRED]** Simplificar es un entregable: si una IA toca un módulo y puede eliminar código
  muerto o una dependencia sin riesgo, lo propone en la misma sesión.

## Sobre detección continua (obligación pasiva de toda IA)

Mientras hace cualquier tarea, toda IA mantiene 6 detectores activos y reporta al final si encontró:

1. Deuda técnica nueva (decisión rápida de hoy que costará mantenimiento).
2. Cuello de botella (paso donde el trabajo espera a un humano sin necesidad).
3. Proceso manual repetido (candidato a [23-Automations.md](23-Automations.md)).
4. Desperdicio de tiempo (trabajo que no mueve ninguna métrica ni ingreso).
5. Riesgo de seguridad (aunque no sea el tema de la tarea).
6. Oportunidad de negocio (algo construido que podría venderse/reutilizarse).

Reporte vacío válido: "Detectores: sin hallazgos nuevos." — pero el renglón debe existir.

## Sobre idioma y formato

- **[REQUIRED]** Comunicación con Jeilin: español. Código, nombres de variables, commits: inglés.
- **[RECOMMENDED]** Respuestas cortas y accionables; tablas para comparaciones; nada de teoría sin
  aplicación inmediata.
