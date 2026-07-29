# 02 — Principios fundamentales

> 10 principios. Cada uno nace de un problema real detectado en la auditoría 2026-07, no de un
> libro. Si un principio deja de tener un problema real detrás, se retira.

1. **Commit diario o no existió.**
   *Origen:* el rediseño completo de jcdigital.online estuvo horas sin commitear; hay repos en E:\
   sin remote. Trabajo no commiteado = trabajo en riesgo. Regla operativa en [19-Git-Standards.md](19-Git-Standards.md).

2. **Si lo hiciste dos veces a mano, la tercera la hace una máquina.**
   *Origen:* configuración repetida de proyectos (ESLint, estructura, README) copiada a mano entre
   repos. Registro obligatorio en [23-Automations.md](23-Automations.md).

3. **Una herramienta sin uso es deuda, no activo.**
   *Origen:* MCP de proyectos con un solo "Proyecto de Ejemplo"; carpetas de infra montadas y
   abandonadas. Antes de construir una herramienta nueva: ¿por qué la anterior no se usó?

4. **El deploy no depende de la memoria.**
   *Origen:* frontend se despliega solo (Pages+Git) pero worker-pago requiere recordar
   `npx wrangler deploy`. Todo deploy debe ser: push → automático, o un comando único documentado.

5. **Lo que maneja dinero tiene el doble de verificación.**
   *Origen:* worker-pago procesa pagos reales (Wompi) sin tests ni CI. Código de pagos: tests
   mínimos + revisión antes de deploy, sin excepciones ([17-Testing.md](17-Testing.md)).

6. **Primero medir, después optimizar.**
   Ninguna optimización (performance, costos, UX) sin número antes y después
   ([24-Metrics.md](24-Metrics.md)). "Se siente más rápido" no es un dato.

7. **La IA básica ejecuta, la IA potente decide.**
   Tareas mecánicas y barridos → modelos baratos siguiendo checklists de este OS. Arquitectura,
   seguridad, prioridades → modelos potentes o Jeilin. Nunca al revés.

8. **Un solo lugar para cada cosa.**
   *Origen:* dos árboles `Trabajo` (C:\ y E:\) con estructura duplicada. Regla de residencia de
   proyectos en [07-Project-Structure.md](07-Project-Structure.md); duplicados se archivan, no
   conviven.

9. **Reutilizar antes que reconstruir.**
   Existe `workers-template`, existe el handbook, existen componentes probados. Todo proyecto nuevo
   empieza desde plantilla ([26-Templates.md](26-Templates.md)), nunca desde cero.

10. **Cada mejora cierra su ciclo.**
    Implementar → medir → registrar resultado en [29-Roadmap.md](29-Roadmap.md) → recién entonces
    la siguiente. Diez mejoras a medio terminar valen menos que dos cerradas.
