# 05 — Matriz de decisión

> Formato obligatorio de TODA recomendación en este ecosistema, y las escalas para puntuar.
> Sin este formato, una recomendación no entra al roadmap.

## Formato de recomendación (obligatorio, 11 campos)

```markdown
### [ID-corto] Título de la recomendación

- **Problema:** qué está mal HOY, con evidencia (archivo, repo, métrica, hallazgo de auditoría).
- **Impacto:** qué mejora y cuánto (Alto/Medio/Bajo + estimación numérica si existe).
- **Esfuerzo:** XS (<1h) · S (1-4h) · M (1-2 días) · L (1 semana) · XL (>1 semana).
- **Prioridad:** P0 (esta semana) · P1 (este mes) · P2 (este trimestre) · P3 (algún día).
- **Beneficio esperado:** en qué métrica de 24-Metrics.md se verá.
- **Tiempo estimado:** horas concretas de implementación.
- **Horas ahorradas:** por semana o por mes, estimadas honestamente (0 es un valor válido).
- **Riesgo:** qué puede romperse + plan de rollback en una línea.
- **Dependencias:** qué debe existir antes (otra recomendación, un acceso, una decisión de Jeilin).
- **Plan de implementación:** pasos numerados, el primero ejecutable HOY.
- **Cómo medir el éxito:** el número/hecho verificable a los 7-30 días.
```

## Cálculo de prioridad

```
Score = (Impacto × Frecuencia) / (Esfuerzo × Riesgo)
```

- Impacto: 1-5 (5 = protege dinero/trabajo; 4 = ahorra horas semanales; 3 = ahorra horas mensuales;
  2 = calidad; 1 = estético).
- Frecuencia: 1-5 (5 = duele a diario; 1 = duele una vez al año).
- Esfuerzo: XS=1, S=2, M=3, L=4, XL=5.
- Riesgo: 1-3 (1 = reversible en minutos; 3 = toca pagos/producción).

P0 = score ≥ 6 · P1 = 3-6 · P2 = 1.5-3 · P3 = < 1.5. La matriz ordena; Jeilin decide.

## ROI (cuando hay dinero o tiempo medible)

```
ROI mensual = (horas ahorradas/mes × valor hora) + ingresos nuevos − costo mensual de la solución
```

Valor hora de referencia: usar la tarifa efectiva de proyectos cliente (si no está calculada:
`DATO FALTANTE` — pedirla a Jeilin una sola vez y registrarla en 21-Business.md).

## Matriz de adopción de tecnología (antes de agregar CUALQUIER cosa al stack)

| Pregunta | Si la respuesta es NO |
|---|---|
| ¿Resuelve un problema que el stack actual no resuelve? | No se adopta. |
| ¿Se mantiene solo (SaaS/managed) o Jeilin deberá operarlo? | Si hay que operarlo: +1 nivel de esfuerzo. |
| ¿Tiene plan gratuito o costo < $10/mes al inicio? | Requiere justificación de negocio en 21-Business.md. |
| ¿Una IA básica puede trabajar con él siguiendo el handbook? | Si no: solo para proyectos donde Jeilin trabaje directo. |
| ¿Reemplaza a algo? (entra 1 → sale 1) | Acumular tecnología duplicada está prohibido — ej. real de la auditoría: Firebase+Supabase híbrido en jonnyTrader. |

## Decisiones tipo ya tomadas (no re-litigar; cambiarlas requiere nueva evidencia)

| Decisión | Resolución | Motivo |
|---|---|---|
| ¿Dónde viven los proyectos nuevos? | `C:\trabajo\Trabajo\<categoria>` | E:\ queda como archivo/históricos; auditoría encontró estructura duplicada C:/E: |
| ¿Pages o Workers para frontend? | Pages con integración Git | Deploy automático ya probado en jcdigital |
| ¿Supabase o Firebase? | Supabase para todo lo nuevo; Firebase solo legacy en salida | Declarado en handbook; híbridos generan doble mantenimiento |
| ¿TypeScript? | Obligatorio en proyectos nuevos; migración oportunista en legacy | Handbook lo exige; mitad del ecosistema ya lo usa |
| ¿Monorepo o multi-repo? | Multi-repo por producto (frontend + worker juntos si son un producto, como JCDigital) | Coincide con la práctica real existente |
