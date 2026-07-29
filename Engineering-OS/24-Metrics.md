# 24 — Metrics

> Tablero del sistema. Cada score: 0-100, con fórmula verificable — nada de sensaciones. Se
> recalcula en cada auditoría (mensual recomendado) y después de cada mejora del roadmap para
> medir si de verdad mejoró (regla de análisis continuo). **Baseline 2026-07-20 = la auditoría de
> este OS.**

## Scores

| Score | Fórmula (verificable) | Baseline 2026-07 | Objetivo 90 días |
|---|---|---|---|
| **Developer Score** | % de días laborales con ≥1 commit push (últimos 30d) | ~20 (ráfagas) | 70 |
| **Architecture Score** | % de proyectos activos 100% en stack canónico (sin híbridos Firebase/Supabase) | ~60 | 80 |
| **Automation Score** | automatizaciones `activas` / repeticiones detectadas en 23-Automations | 0/7 → 0 | 4/7 → 57 |
| **Performance Score** | promedio Lighthouse móvil (performance) de los sitios en producción | `DATO FALTANTE` (medir) | ≥85 |
| **Security Score** | 100 − (20×críticos + 10×altos + 3×medios abiertos del informe de seguridad) | pendiente informe | ≥90 |
| **Business Score** | % de proyectos activos con modelo de ingreso escrito en 21-Business | ~30 | 70 |
| **Documentation Score** | % de activos con README+CLAUDE.md+.env.example | ~10 | 100 |
| **Technical Debt Score** (más alto = menos deuda) | 100 − (repos sin remote×2 + repos con >10 cambios sin commitear×5 + duplicados activos×5), piso 0 | ~15 | 75 |
| **Maintainability Score** | % de activos que una IA puede levantar solo con README (`npm i && npm run dev` funciona) | `DATO FALTANTE` (probar) | 90 |
| **Scalability Score** | % de flujo idea→producción sin pasos manuales (pasos automatizados/16) | ~30 (5/16) | 60 |
| **Learning Score** | temas de 22-Learning cerrados con resultado verificable / trimestre | 0 | 2 |
| **ROI Score** | horas recuperadas/mes × valor hora − costos herramientas | `DATO FALTANTE` (valor hora) | positivo y creciente |

## Contadores de tiempo y dinero

| Métrica | Cómo se estima | Valor actual |
|---|---|---|
| Tiempo perdido semanal | horas en tareas de la lista 23-Automations aún manuales | ~6-8h (estimado auditoría) |
| Tiempo automatizable | suma de "horas ahorradas" de automatizaciones `propuesta` | ~5-7h/semana |
| Horas recuperadas | suma de "horas ahorradas" de automatizaciones `activas` | 0 (ninguna activa aún) |
| Costo mensual | VPS Contabo + dominios + APIs de pago | `DATO FALTANTE` (listar) |
| Costo optimizado | costo tras aplicar recomendaciones de costos del roadmap | — |

## Reglas

- **[REQUIRED]** Después de implementar cualquier ítem del roadmap: recalcular SOLO los scores que
  ese ítem prometía mover y anotar en [29-Roadmap.md](29-Roadmap.md): `mejoró (X→Y)` /
  `sin efecto` / `empeoró`. Sin efecto dos veces seguidas = la recomendación era mala; se
  documenta en la KB para no repetirla.
- **[REQUIRED]** Los `DATO FALTANTE` se resuelven una sola vez (medición o dato de Jeilin) y se
  fijan aquí con fecha.
- **[RECOMMENDED]** Recalcular todo el tablero: 1×/mes, tarea perfecta para IA básica con este
  archivo + los comandos git/lighthouse como receta.
