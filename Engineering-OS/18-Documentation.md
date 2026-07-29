# 18 — Documentation

> La documentación de este ecosistema tiene UNA regla madre: se escribe la mínima que permita a
> una IA (o a Jeilin en 6 meses) retomar el proyecto sin arqueología. Todo lo demás es desperdicio.

## Los 3 documentos por proyecto (y nada más, por defecto)

| Documento | Responde a | Se actualiza cuando |
|---|---|---|
| `README.md` | ¿Qué es? ¿Cómo lo corro? ¿Cómo se despliega? ¿Qué variables necesita? | Cambia el uso |
| `CLAUDE.md` | ¿Qué necesita saber una IA? (stack, comandos, decisiones no obvias, qué NO tocar) | Cambia el contexto |
| `.env.example` | ¿Qué configuración existe? (claves sin valores) | Se agrega/quita variable |

- **[REQUIRED]** Los 3 existen en todo proyecto activo. Estado real detectado: ~45 de 60 proyectos
  sin README — se corrige SOLO en los activos (generar con plantilla de
  [26-Templates.md](26-Templates.md) es tarea perfecta para IA básica).
- **[REQUIRED]** El conocimiento transversal NO se duplica en READMEs: vive en el handbook
  (técnico) o en este OS (proceso) y se enlaza.
- **[REQUIRED]** Documentar decisiones, no código: cuando se tome una decisión no obvia (por qué
  KV y no D1, por qué este proveedor), 2-4 líneas en el CLAUDE.md del proyecto o en
  [28-Knowledge-Base.md](28-Knowledge-Base.md) si es transversal.
- **[RECOMMENDED]** Generación con IA: README/changelog/release notes los redacta IA básica desde
  plantilla + `git log`; Jeilin solo corrige. Nunca escribir documentación a mano desde cero.
