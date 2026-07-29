# 25 — Checklists

> Biblioteca de verificación. Una IA básica puede ejecutar cualquiera de estas listas sin criterio
> propio: cada ítem es sí/no. El orden importa. "Hecho" = todos los ítems sí o su excepción
> declarada.

## §1 Antes de crear un proyecto

- [ ] ¿Ya existe algo en el ecosistema que hace esto? (buscar en inventario/KB — hay ~95 proyectos)
- [ ] ¿Tiene quién lo pague o qué métrica de negocio mueve? (21-Business; si no → E:\Pruebas)
- [ ] Nombre kebab-case sin espacios · ruta canónica de 07-Project-Structure
- [ ] Creado con la automatización A1 (o manualmente TODOS sus pasos: plantilla + git + remote + README + CLAUDE.md + .env.example + ci.yml)
- [ ] Registrado en el MCP jcdigital (nombre, categoría, prioridad, next)

## §2 Antes de escribir código

- [ ] Leí el CLAUDE.md del proyecto y el estándar del handbook del dominio que voy a tocar
- [ ] Sé qué paso del workflow (04) estoy ejecutando y cuáles se declararon saltados
- [ ] Si toco pagos/auth/datos de clientes: leí 16-Security y tengo plan de rollback
- [ ] Si la tarea la ejecuta IA básica: tiene el documento de patrón EN contexto

## §3 Antes de hacer commit

- [ ] Build pasa (`npm run build` / `tsc --noEmit`)
- [ ] Verificado en preview (móvil 375px + desktop si es UI)
- [ ] `git status` revisado: no entra ningún archivo de secretos ni basura (.wrangler, dist)
- [ ] Mensaje en formato Conventional Commits (19-Git-Standards)
- [ ] Push hecho (commit sin push no cuenta)

## §4 Antes de abrir un Pull Request (solo código crítico o de IA básica)

- [ ] §3 completo · descripción: qué cambia, por qué, cómo se probó
- [ ] Si es de IA básica sobre pagos/auth: revisión de IA potente solicitada explícitamente
- [ ] Sin cambios mezclados (una intención por PR)

## §5 Antes de desplegar

- [ ] §3 completo en el commit desplegado
- [ ] Variables de entorno nuevas ya configuradas en Pages/Workers dashboard Y en .env.example
- [ ] Si es worker de pagos: los tests de dinero (17-Testing §2) pasan
- [ ] Sé cómo hacer rollback (está en el README del proyecto)

## §6 Después de desplegar (antes de "publicar"/anunciar)

- [ ] URL de producción abre y carga < 3s
- [ ] Consola del navegador sin errores rojos
- [ ] Flujo crítico probado EN producción (compra de prueba, formulario, cotizador…)
- [ ] Responsive verificado en un móvil real o 375px
- [ ] Resultado anotado: `VERIFICADO <fecha>` en la sesión/KB

## §7 Antes de cerrar un proyecto (entrega a cliente / release final)

- [ ] README final: cómo correr, desplegar, rollback, variables
- [ ] Credenciales entregadas/rotadas — nada queda solo en el chat o la cabeza
- [ ] Retrospectiva del workflow (paso 15) hecha y volcada a KB
- [ ] ¿Algo de este proyecto se generaliza/revende? → anotado en 21-Business
- [ ] Registrado como `terminado` en el MCP jcdigital

## §8 Antes de abandonar/archivar un repositorio

- [ ] Todo commiteado y pusheado (si no hay remote: crearlo AUNQUE se archive — es el backup)
- [ ] Nota de 3 líneas en el README: por qué se archiva, qué funcionaba, qué se reutilizaría
- [ ] Movido a `E:\Trabajo\05_Archive` · eliminado de rutas activas y del launch.json si estaba
- [ ] Estado `terminado/pausado` en el MCP jcdigital
- [ ] Secretos del proyecto rotados si eran compartidos con otros proyectos
