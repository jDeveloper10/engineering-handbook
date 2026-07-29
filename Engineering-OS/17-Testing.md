# 17 — Testing

> Estado real (auditoría 2026-07): no existe ni un test automatizado en el ecosistema, incluido
> el worker que procesa pagos reales. Este archivo define el mínimo pragmático para un equipo
> de una persona. El departamento de QA completo (estrategia, pipeline, CI/CD, agentes
> especializados) vive en el handbook `06_Testing`.
>
> **Ver también:**
> - [`06_Testing/01_QA_STRATEGY.md`](../06_Testing/Strategy/01_QA_STRATEGY.md) — estrategia completa
> - [`06_Testing/08_QUALITY_STANDARDS.md`](../06_Testing/Strategy/08_QUALITY_STANDARDS.md) — quality gates
> - [`06_Testing/Agents/README.md`](../06_Testing/Agents/README.md) — 8 agentes de QA
>
> ## Regla de relación con el handbook
>
> - **[REQUIRED]** Este archivo es la capa operativa del testing (qué probar primero, con qué
>   prioridad, quién escribe los tests). Las definiciones técnicas (vitest config, cobertura
>   requerida, tipos de test) viven en `06_Testing`. Si este archivo dice "no hagas tests de UI"
>   y el QA strategy dice otra cosa, gana el QA strategy — porque el handbook es la autoridad
>   técnica y este archivo solo la adapta al contexto de un dev solo.

## Pirámide invertida pragmática

1. **[REQUIRED] Build como primer test.** `npm run build` (y `tsc --noEmit` en TS) pasa antes de
   todo push. Es gratis y atrapa la mitad de los errores. CI lo hará automático (roadmap P0).
2. **[REQUIRED] Tests de lógica de dinero.** worker-pago y todo worker de pagos futuros: vitest
   con casos mínimos — creación de orden, validación de firma de webhook, transición de estados
   (PENDING→COMPLETED/FAILED), URL de descarga solo con orden COMPLETED. Son ~6 tests que
   protegen el 100% del riesgo económico directo.
3. **[REQUIRED] Smoke test post-deploy** (manual hoy, automatizable): la URL carga, consola sin
   errores, flujo crítico del producto funciona (en jcdigital: cotizador calcula y tienda lista
   productos).
4. **[RECOMMENDED] Tests de UI:** no por ahora. Con un solo dev, el costo de mantenerlos supera su
   valor; la verificación en preview del checklist de commit cubre el caso. Revisar esta decisión
   si aparece un segundo mantenedor o un producto con >100 usuarios activos.

## Reglas para IAs

- IA que toca lógica de pagos/auth: escribe o actualiza los tests del punto 2 EN el mismo cambio.
- IA básica puede GENERAR tests desde ejemplos existentes; una IA potente revisa las aserciones
  (un test que siempre pasa es peor que ninguno).
- Un bug de producción repetido = test de regresión obligatorio antes de cerrar el fix
  (registrado en [28-Knowledge-Base.md](28-Knowledge-Base.md)).
