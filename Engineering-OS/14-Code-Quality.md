# 14 — Code Quality

> Lo técnico por dominio vive en el handbook (cada dominio tiene su estándar de calidad). Aquí:
> las reglas transversales de calidad — las que aplican a FRONTEND + BACKEND + API + DB por igual
> — y cómo se verifican sin humanos.
>
> **Ver también:**
> - [`FRONTEND_ENGINEERING_STANDARD.md`](../01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md) §04 (component rules)
> - [`BACKEND_ENGINEERING_STANDARD.md`](../02_Backend/BACKEND_ENGINEERING_STANDARD.md) §13 (code quality)
> - [`FRONTEND_TYPESCRIPT_STANDARD.md`](../01_Frontend/Core/FRONTEND_TYPESCRIPT_STANDARD.md)
> - [`25-Checklists.md`](25-Checklists.md) §3 (pre-commit checklist)

- **[REQUIRED]** Definición de "terminado": build pasa + reglas REQUIRED del handbook cumplidas +
  checklist de commit ([25-Checklists.md](25-Checklists.md) §3) + verificado en preview/producción.
  Código que no cumple los 4 no se reporta como terminado.
- **[REQUIRED]** Un componente/función = una responsabilidad; ~200 líneas como señal de alarma
  (regla heredada del handbook). Al superarla, la IA propone la división en la misma sesión.
- **[REQUIRED]** Código muerto se elimina, no se comenta. Git es la papelera.
- **[REQUIRED]** Consistencia sobre preferencia: el código nuevo imita el estilo del archivo donde
  vive (densidad de comentarios, naming, idioma). Refactors de estilo masivos = tarea separada,
  nunca mezclada con features.
- **[REQUIRED]** ESLint + Prettier con la config estándar en todo proyecto nuevo (la genera la
  automatización A1 de [23-Automations.md](23-Automations.md)); legacy la adopta al primer toque
  serio. Estado real detectado: TypeScript estricto solo en Xworked/ingenusfx/patronesarmonicos —
  el resto converge de forma oportunista.
- **[RECOMMENDED]** Comentarios solo para lo que el código no puede decir (restricciones, porqués
  no obvios). Prohibido el comentario que narra la línea siguiente.
- **[RECOMMENDED]** Dependencias: cada `npm install` nuevo se justifica en el commit. Auditoría
  periódica del Repository-Agent: dependencia sin uso = se elimina.
