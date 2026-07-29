# DEPLOY AND FAILURES STANDARD

> Nivel 1 del handbook para el dominio DevOps — cómo se despliega y qué hacer cuando algo falla en producción. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md): cada regla es `[REQUIRED]` o `[RECOMMENDED]`, primero agnóstica de plataforma y después con implementación de referencia en el stack actual (Cloudflare Pages + Workers vía wrangler, Supabase como DB, VPS Contabo con n8n).
>
> Contexto: developer solo, SaaS. Eso significa que **la persona que deploya es la misma que hará el rollback a las 2am** — cada regla está calibrada para que el camino de emergencia sea corto, esté escrito, y no dependa de la memoria bajo estrés. La Parte B (librería de fallos) existe porque durante un incidente no se piensa bien: se sigue un runbook.
>
> Este documento es la versión completa y canónica; `Engineering-OS/20-Deployment.md` es el resumen operativo y es compatible con lo que sigue.

---

# PARTE A — DEPLOY

## 01. Pipeline mínimo — nada llega a producción sin pasar por él

**[REQUIRED]** Todo deploy a producción pasa antes por, en este orden: **typecheck → tests → build**. Si cualquiera falla, no hay deploy. Sin excepciones "porque es un cambio chiquito".

**Por qué:** los tres pasos atrapan clases distintas de error y cuestan minutos: el typecheck atrapa contratos rotos (la clase de error más común al editar rápido), los tests atrapan regresiones de lógica, y el build atrapa errores que solo aparecen al empaquetar (imports rotos, env vars de build faltantes). "Cambio chiquito" es precisamente el perfil del deploy que rompe producción — el grande se prueba con miedo; el chiquito se pushea con confianza injustificada.

**Implementación (`.github/workflows/ci.yml` — seguridad del workflow según `GITHUB_STANDARD.md` sección 07):**
```yaml
name: ci
on:
  push: { branches: [main] }
  pull_request:
permissions:
  contents: read
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm test -- --run
      - run: npm run build
  deploy:
    needs: ci
    if: github.ref == 'refs/heads/main'
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@<SHA-pineado>   # ver GITHUB_STANDARD 07
        with: { apiToken: '${{ secrets.CLOUDFLARE_API_TOKEN }}' }
```

**[RECOMMENDED]** Mientras exista deploy manual con `wrangler deploy` desde local (estado actual de los workers), el mismo pipeline se corre a mano antes: `npx tsc --noEmit && npm test && wrangler deploy`. El objetivo es que el manual desaparezca — deploy manual es deploy sin registro y sin pipeline garantizado.

**[REQUIRED]** Post-deploy: smoke test de producción — un request real al endpoint crítico del servicio desplegado (curl al health/ruta principal, o abrir la app y ejecutar el flujo principal). Un deploy no verificado no está terminado.

---

## 02. Deploy de Workers (wrangler)

**[REQUIRED]** El deploy de un worker es `wrangler deploy` desde el directorio del worker, con `wrangler.toml` versionado en el repo (con `compatibility_date` explícito — ya exigido en `BACKEND_ENGINEERING_STANDARD.md` sección 16). Nunca ediciones de código en el dashboard de Cloudflare: lo que corre en producción debe existir en Git.

**Por qué:** un cambio hecho en el dashboard no está en el historial, no pasó el pipeline, y el siguiente `wrangler deploy` desde el repo lo pisa en silencio — es la receta del "funcionaba ayer y nadie sabe por qué dejó de funcionar".

**[REQUIRED]** Rollback de un worker — dos vías, en orden de preferencia:

```bash
# Vía 1 — rollback nativo a una versión previa ya subida (segundos):
wrangler versions list          # ver id de la versión anterior estable
wrangler rollback [version-id]  # sin id, wrangler ofrece elegir interactivamente

# Vía 2 — re-deploy del commit anterior (cuando la vía 1 no aplica, p. ej. hay que
# revertir también un cambio de bindings/config):
git log --oneline -5
git checkout <commit-estable> -- . && wrangler deploy   # o git revert + push si hay CI
```

**Por qué dos vías:** `wrangler rollback` restaura el **código** de una versión previa, pero verificar en docs oficiales qué pasa exactamente con secretos/bindings cambiados entre versiones — cuando el deploy roto incluyó cambios de configuración, re-deployar el commit anterior completo (código + `wrangler.toml`) es la vía sin ambigüedad.

**[RECOMMENDED]** Antes de deployar un cambio riesgoso de worker: `wrangler versions upload` (sube sin activar) + gradual deployment para dividir tráfico entre versión vieja y nueva — verificar sintaxis actual en docs oficiales. Para el caso común de dev solo, deploy directo + rollback rápido es aceptable.

---

## 03. Deploy de Pages

**[REQUIRED]** Los frontends se despliegan por **conexión Git**: push a `main` = deploy a producción, push a cualquier otra rama = **preview deployment** con URL propia. Deploy manual (`wrangler pages deploy <dir>`) solo como vía de emergencia, no como método habitual.

**Por qué:** la conexión Git da tres cosas gratis que el deploy manual no: cada deploy queda atado a un commit exacto (rollback trivial), cada rama tiene una URL de preview para probar antes de mergear (esto sustituye al entorno "staging" que un dev solo no quiere mantener), y no existe el estado "lo que está en producción no está en el repo".

**[REQUIRED]** Rollback de Pages: dashboard → proyecto → Deployments → deployment anterior estable → **Rollback / Retry deployment** (restaura ese build exacto en la URL de producción, en segundos, sin rebuild). Alternativa equivalente: `git revert` del commit malo + push (tarda un build completo, pero deja el historial correcto). Para sangrado inmediato: dashboard; después, el revert para que Git refleje la realidad.

---

## 04. Variables por entorno

**[REQUIRED]** Tres entornos con variables **separadas y nunca compartidas**: desarrollo local, preview, producción. Una variable de producción (service role keys, tokens de pago live) jamás existe en el entorno de preview o en un `.env` local.

**Por qué:** el accidente clásico es un preview deployment — accesible por URL pública — corriendo con la key admin de la base de producción, o un experimento local escribiendo en datos reales. La separación física de valores es lo único que hace ese accidente imposible en vez de improbable.

**Implementación por pieza del stack:**

| Entorno | Workers | Pages | Dónde viven los valores |
|---|---|---|---|
| Local | `.dev.vars` (gitignoreado) | `.env` local (gitignoreado) | solo en tu máquina |
| Preview | `[env.staging]` en `wrangler.toml` + `wrangler secret put --env staging` | variables de "Preview" en dashboard | plataforma |
| Producción | `wrangler secret put <NAME>` | variables de "Production" en dashboard | plataforma |

**[REQUIRED]** La **lista** de variables requeridas está versionada (`.env.example` / comentario en `wrangler.toml`); los **valores** nunca (coherente con `GITHUB_STANDARD.md` sección 02.1). El worker valida sus env vars al arrancar (`BACKEND_ENGINEERING_STANDARD.md` sección 06) — así una variable faltante falla ruidoso en el primer request, no silencioso en el décimo.

---

## 05. Migraciones de DB — expandir → migrar → contraer

**[REQUIRED]** Todo cambio de esquema que acompaña un cambio de código se hace en el patrón de tres fases, porque **durante un deploy siempre conviven la versión vieja y la nueva del código** (requests en vuelo, rollback posible, Workers propagándose):

```
Fase 1 — EXPANDIR (deploy de DB, compatible con código viejo):
  agregar la columna/tabla nueva SIN quitar la vieja; nueva columna nullable o con default.
  → el código viejo sigue funcionando; el esquema ya soporta al nuevo.

Fase 2 — MIGRAR (deploy de código + backfill):
  deployar código que escribe en lo nuevo (y lee de ambos si hace falta);
  backfill de datos históricos en batch.
  → si este deploy falla, rollback de código es seguro: el esquema viejo sigue ahí.

Fase 3 — CONTRAER (días después, cuando nadie lee lo viejo):
  quitar la columna/tabla vieja, agregar constraints NOT NULL definitivos.
  → recién aquí el esquema deja de soportar el código viejo — y ya no importa.
```

**Por qué:** la migración "de un golpe" (renombrar columna + deployar código que usa el nombre nuevo) tiene una ventana donde el código viejo escribe contra un esquema que ya no lo soporta — errores 500 durante el deploy, y peor: **hace el rollback imposible**, porque volver al código viejo requiere revertir también la DB, con datos nuevos ya escritos. Expandir→migrar→contraer garantiza que en cada fase el rollback de código sea seguro sin tocar la DB.

**[REQUIRED]** Orden respecto al deploy: **la migración expansiva va ANTES del código que la usa; la contracción va DESPUÉS de que ningún código desplegado use lo viejo.** Nunca deployar código que asume un esquema que aún no existe.

**[REQUIRED]** Migraciones como archivos SQL versionados en el repo y aplicadas por herramienta (`supabase migration new <nombre>` / `supabase db push`, o el sistema de migraciones que use el proyecto) — nunca SQL a mano en el editor de la consola contra producción sin archivo que lo registre.

**[RECOMMENDED]** Antes de una migración destructiva (DROP, cambio de tipo con pérdida): verificar que existe backup restaurable (sección B7) — el costo es un click de verificación; el ahorro es la sección B7 entera.

---

## 06. Rollback vs fix-forward — el criterio

**[REQUIRED]** Cuando un deploy rompe producción, la decisión por defecto es **rollback primero, diagnosticar después**. Fix-forward solo cuando se cumplen las tres:

1. La causa es **obvia y el fix es de una línea evidente** (typo en env var, import roto) — no una hipótesis.
2. El fix tarda **menos que el rollback** en llegar a producción.
3. El rollback **no es limpio**: el deploy incluyó una migración de fase 2+ o efectos de datos que volver atrás no deshace.

**Por qué:** bajo presión, "casi tengo el fix" es la frase que convierte 5 minutos de incidente en una hora — cada intento de fix es un deploy más sin pipeline mental completo, sobre un sistema ya roto. El rollback es el único movimiento con resultado conocido: vuelve al último estado que se sabía bueno. La condición 3 es la excepción real: si la DB ya avanzó, el rollback de código puede empeorar las cosas — por eso la sección 05 existe: mantener el rollback siempre limpio.

**[REQUIRED]** Después de todo rollback: el commit roto **no se re-deploya** hasta que la causa esté identificada y cubierta por un test o check que la habría atrapado. Rollback sin post-mortem = mismo incidente en dos semanas.

---

# PARTE B — LIBRERÍA DE FALLOS

> **[REQUIRED]** Durante un incidente se sigue el runbook en orden — no se improvisa el diagnóstico. Cada runbook: síntomas → diagnóstico en orden (del más probable/barato al más raro/caro) → mitigación → prevención. **Por qué:** el orden de diagnóstico codifica, en frío, la probabilidad real de cada causa; seguirlo evita el sesgo caliente de saltar a la hipótesis interesante en vez de la probable.

## B1. Deploy falló a mitad

**Síntomas:** el pipeline/`wrangler deploy` terminó con error; o terminó "OK" pero producción sirve una mezcla (frontend nuevo contra worker viejo, o viceversa).

**Diagnóstico en orden:**
1. ¿En qué paso murió? Log del job de Actions (`gh run view --log-failed`) o salida de wrangler. Si murió en typecheck/test/build → **producción no fue tocada**, no es incidente, es un fix normal.
2. Si murió durante el paso de deploy: ¿qué quedó activo? `wrangler deployments list` / `wrangler versions list` para el worker; dashboard → Deployments para Pages. Comparar contra `git log`.
3. Si el deploy era multi-pieza (worker + frontend + migración): identificar cuáles piezas entraron y cuáles no — el peligro no es la pieza fallida, es la **combinación inconsistente** de las que sí entraron.

**Mitigación:** llevar todas las piezas a un estado consistente conocido — normalmente rollback de las piezas que sí entraron (secciones 02/03) al estado previo, luego re-intentar el deploy completo desde cero. No "completar a mano" la pieza faltante deployándola suelta: eso salta el pipeline.

**Prevención:** deploys pequeños y frecuentes (menos piezas por deploy = menos combinaciones a medio camino); orden de deploy compatible (sección 05: DB expansiva primero, código después); y donde frontend y worker deben cambiar juntos, código nuevo tolerante al contrato viejo durante la ventana de propagación.

## B2. Worker devuelve 500 en producción

**Síntomas:** usuarios reportan error; el frontend recibe 500/`fetch failed` de un worker.

**Diagnóstico en orden:**
1. **¿Correlaciona con un deploy?** `wrangler deployments list` — si el último deploy fue hace minutos/horas: rollback ya (sección 06), diagnóstico después.
2. Logs en vivo: `wrangler tail <worker-name>` mientras se reproduce el error — muestra la excepción real (los errores devueltos al cliente son opacos por diseño, `BACKEND_ENGINEERING_STANDARD.md` sección 09; el detalle está en el log).
3. ¿Es el worker o su dependencia? Si el log muestra fallo llamando a Supabase/API externa → ir a B4 (o al status del proveedor externo). El 500 del worker puede ser el síntoma, no la enfermedad.
4. ¿Env var/secreto faltante o rotado? Típico tras rotar una key (`GITHUB_STANDARD.md` sección 08) y olvidar `wrangler secret put` en este worker. `wrangler secret list` muestra los nombres definidos (no los valores).
5. ¿Límites del runtime? CPU time excedido, subrequests, tamaño de respuesta — el log de `wrangler tail` lo indica (verificar límites vigentes del plan en docs oficiales).

**Mitigación:** paso 1 si hubo deploy reciente. Si es secreto faltante: `wrangler secret put` y verificar. Si es dependencia caída: el worker debe degradar (devolver error claro y rápido), y el incidente se persigue en el runbook del proveedor.

**Prevención:** smoke test post-deploy (sección 01) — atrapa el 500 minutos después del deploy en vez de cuando lo reporta un usuario; checklist de rotación de secretos que lista **todos** los lugares donde vive cada secreto; logs estructurados con request ID (`BACKEND_ENGINEERING_STANDARD.md` sección 10) para que el paso 2 tarde minutos y no horas.

## B3. Cloudflare caído

**Síntomas:** TODO falla a la vez — Pages, Workers, hasta el dashboard. Errores 5xx con página de error de Cloudflare (52x), o timeouts globales.

**Diagnóstico en orden:**
1. **Verificar que es Cloudflare y no tú**: abrir `https://www.cloudflarestatus.com` (fuera de la red de Cloudflare precisamente para esto) — buscar incidente activo en Workers/Pages/la región. Contrastar con un tercero (downdetector, ¿otros sitios sobre Cloudflare fallan?).
2. Si el status page está verde: NO es Cloudflare — volver a B2/B5 (el error 52x también aparece cuando **tu** origen/worker falla; un 522 es "no pude conectar con tu origen", no "Cloudflare está caído").

**Mitigación — qué SÍ puedes hacer:** confirmar el alcance (¿solo Workers? ¿solo una región?); comunicar a usuarios por un canal que no dependa de Cloudflare (email, Telegram vía n8n en el VPS si está sano, redes); suscribirte al incidente en el status page; anotar hora de inicio para el post-incidente.
**Qué NO puedes hacer (y no debes intentar):** no hay rollback ni re-deploy que arregle la infraestructura del proveedor — deployar "a ver si se arregla" durante un incidente del proveedor solo añade una variable; migrar de proveedor en caliente no es una opción real de dev solo. Se espera, se comunica, y se documenta.

**Prevención:** el canal de aviso a usuarios (n8n en el VPS) vive deliberadamente **fuera** de Cloudflare — no depender del proveedor caído para avisar que el proveedor está caído. Aceptar el riesgo residual por escrito: para un SaaS de este tamaño, el uptime de Cloudflare es mejor que cualquier alternativa que un dev solo pueda operar.

## B4. Supabase caído o degradado

**Síntomas:** los workers responden pero todo lo que toca DB/auth falla; logins caídos; timeouts en queries que normalmente son instantáneas.

**Diagnóstico en orden:**
1. `https://status.supabase.com` + dashboard del proyecto (¿el proyecto está "paused"? — en plan free, los proyectos se pausan por inactividad).
2. ¿Caído o degradado? Probar una query mínima (`select 1`) desde el SQL editor o un endpoint de health. Si responde lento pero responde → degradación: puede ser incidente del proveedor **o** una query tuya (¿deploy reciente con N+1 o índice faltante? — correlacionar con deploys, y mirar el query performance del dashboard).
3. ¿Es solo auth, solo DB, o todo? Supabase son varios servicios; el status page los separa.

**Mitigación:** si es incidente del proveedor: igual que B3 — comunicar y esperar; verificar que los workers degradan con un error claro y rápido (timeout corto) y no cuelgan requests. Si es proyecto pausado: restaurarlo desde el dashboard. Si es degradación por query propia: rollback del deploy que la introdujo.

**Prevención:** timeouts explícitos en toda llamada del worker a Supabase (un backend que espera para siempre convierte degradación en caída total); plan pago para el proyecto de producción (sin pausas por inactividad, y con point-in-time recovery — que además es prerequisito de B7).

## B5. DNS roto / SSL vencido

**Síntomas:** `DNS_PROBE_FINISHED_NXDOMAIN` o "no se puede encontrar el servidor" (DNS), o advertencia de certificado / `ERR_SSL_*` (SSL). A veces solo en algunos usuarios/redes (propagación).

**Diagnóstico en orden:**
1. ¿Resuelve el dominio? `nslookup app.tudominio.com 1.1.1.1` y contra un segundo resolver (`8.8.8.8`) — si uno resuelve y otro no: propagación o caché, no configuración.
2. ¿Qué dice el certificado? `curl -vI https://app.tudominio.com` — mirar fechas de validez y emisor en la salida.
3. ¿Cambió algo? Registros DNS en el dashboard de Cloudflare (¿registro borrado/editado por accidente? ¿proxy naranja desactivado?); ¿venció el **dominio** mismo? (`whois` — dominio vencido se manifiesta primero como DNS roto).
4. Para SSL en Cloudflare: el certificado edge es automático — si venció, revisar en el dashboard SSL/TLS el estado del certificado y el modo (Full/Flexible); un modo mal configurado da errores 52x/loops de redirect, no exactamente "SSL vencido".

**Mitigación:** registro DNS borrado → recrearlo (por eso la prevención de abajo); dominio vencido → renovarlo YA (hay periodo de gracia, pero horas cuentan); problema de cert edge → verificar en docs oficiales el re-issue del certificado universal, o soporte de Cloudflare.

**Prevención:** **exportar la zona DNS a un archivo versionado en un repo** (dashboard → DNS → export, o API) cada vez que se edita — recrear una zona de memoria bajo presión es exactamente lo que este archivo evita; auto-renew del dominio activado con método de pago vigente; recordatorio de vencimiento del dominio en calendario independiente del auto-renew.

## B6. n8n / VPS caído

**Síntomas:** automatizaciones dejan de correr (avisos de Telegram que no llegan, flujos que no se disparan); la UI de n8n no carga; SSH no conecta.

**Diagnóstico en orden (de la capa más externa a la más interna):**
1. ¿El VPS responde? `ping <ip-vps>` y `ssh usuario@<ip-vps>`. Si ni ping ni SSH: panel de Contabo (¿VPS apagado? ¿mantenimiento del proveedor? ¿factura impaga?) y status/avisos de Contabo.
2. Con SSH dentro: ¿está vivo el proceso? `docker ps` (si n8n corre en Docker) o `systemctl status n8n`. ¿Se quedó sin recursos? `df -h` (disco lleno — la causa #1 real de "el VPS se murió solo": logs y ejecuciones de n8n llenan el disco), `free -m` (RAM/OOM), `docker logs n8n --tail 100`.
3. ¿n8n arriba pero flujos fallando? Revisar ejecuciones fallidas en la UI — puede ser una credencial vencida de un servicio externo, no el VPS.

**Mitigación:** disco lleno → limpiar (`docker system prune`, purgar historial de ejecuciones de n8n, logrotate) y reiniciar el servicio; proceso muerto → `docker restart n8n` / `systemctl restart n8n`; VPS muerto → reinicio desde el panel de Contabo; si el VPS no vuelve → restaurar desde snapshot/backup del panel.

**Prevención:** los flujos de n8n **exportados como JSON y versionados en un repo** (coherente con `Engineering-OS/20-Deployment.md`) — el VPS debe ser reconstruible, no una pieza única e irrepetible; restart automático del contenedor (`restart: unless-stopped`); poda automática del historial de ejecuciones de n8n (env vars `EXECUTIONS_DATA_PRUNE*` — verificar nombres exactos en docs de n8n); un healthcheck externo barato (un worker con cron trigger que hace ping a n8n y avisa si no responde — el monitor vive en Cloudflare, el monitoreado en Contabo: fallo cruzado detectable en ambas direcciones).

## B7. Datos corruptos en la DB por un bug

**Síntomas:** los servicios están "verdes" pero los datos están mal — un bug escribió valores incorrectos, borró filas, o duplicó registros durante horas antes de notarse. El incidente más peligroso de la lista: no hay página de error, solo datos silenciosamente envenenados.

**Diagnóstico en orden:**
1. **Parar la hemorragia primero**: identificar y desactivar la escritura culpable (rollback del deploy que introdujo el bug, o desactivar el flujo/endpoint que escribe). Restaurar datos mientras el bug sigue escribiendo es achicar el bote con el grifo abierto.
2. Acotar el daño: ¿desde cuándo? (correlacionar con el deploy del bug — el historial de deploys da el timestamp exacto); ¿qué tablas/filas? Query que enumere los registros afectados (`updated_at >= <timestamp del deploy>` + condición del valor corrupto). Guardar esa lista.
3. ¿Los datos corruptos dispararon efectos externos? (emails enviados, cobros, webhooks salientes) — esos no se arreglan con un restore de DB y necesitan su propia lista.

**Mitigación — elegir la vía según el alcance:**
- **Restore selectivo (la vía por defecto):** cuando el daño está acotado a tablas/filas identificables y el resto de la DB siguió recibiendo datos buenos. Restaurar el backup/PITR **a una base o proyecto aparte** (nunca sobre producción), extraer de ahí solo las filas afectadas, y repararlas en producción con UPDATEs dirigidos y auditados (guardar el script). Preserva todo lo bueno escrito después del bug.
- **Point-in-time recovery completo (la vía nuclear):** volver toda la DB al instante anterior al bug. Solo cuando el daño es masivo/inacotable **y** se acepta perder TODO lo escrito después de ese punto — incluidos los datos legítimos de otros usuarios. En un SaaS con escrituras concurrentes esto casi nunca es aceptable pasados más que minutos; por eso el default es el selectivo.
- En ambos casos: anunciar mantenimiento/pausar escrituras durante la reparación si la reparación es sensible a escrituras concurrentes.

**Prevención:** PITR habilitado en el proyecto de producción **antes** de necesitarlo (en Supabase es addon de plan pago — verificar retención contratada en docs oficiales; sin PITR, este runbook se reduce a "restaurar el backup diario y perder hasta 24h"); migraciones y deploys que tocan escrituras críticas detrás del patrón de la sección 05 (rollback limpio = menos ventana de corrupción); constraints en la DB (`NOT NULL`, `CHECK`, FKs, unique) — el bug de aplicación que viola un constraint falla ruidoso en el primer insert en vez de corromper en silencio durante horas; y **ensayar el restore una vez en frío**: un backup jamás restaurado es una hipótesis, no un backup.

---

## Checklist final

**Parte A — Deploy**
- [ ] ¿Typecheck + tests + build pasan antes de todo deploy, sin excepción por tamaño del cambio?
- [ ] ¿Smoke test de producción después de cada deploy?
- [ ] ¿Workers deployados solo desde el repo con wrangler (cero ediciones en dashboard); rollback conocido (`wrangler rollback` / re-deploy de commit)?
- [ ] ¿Pages conectado a Git; previews por rama; rollback por dashboard documentado?
- [ ] ¿Variables separadas local/preview/prod; ningún secreto de prod en preview o local; lista en `.env.example`?
- [ ] ¿Migraciones en expandir→migrar→contraer; expansiva antes del código, contracción después; SQL versionado?
- [ ] ¿Ante deploy roto: rollback por defecto; fix-forward solo con causa obvia + más rápido + rollback no limpio?
- [ ] ¿Post-mortem antes de re-deployar un commit revertido?

**Parte B — Fallos**
- [ ] ¿Incidente = seguir el runbook en orden, no improvisar?
- [ ] ¿Deploy a medias: estado consistente primero (rollback de piezas entradas), nunca "completar a mano"?
- [ ] ¿Worker 500: correlacionar con deploy → `wrangler tail` → dependencias → secretos?
- [ ] ¿"Cloudflare caído" verificado en cloudflarestatus.com antes de tocar nada (52x puede ser tu origen)?
- [ ] ¿Timeouts explícitos hacia Supabase; proyecto de prod en plan sin pausas y con PITR?
- [ ] ¿Zona DNS exportada y versionada; auto-renew del dominio activo?
- [ ] ¿Flujos n8n exportados a repo; poda de ejecuciones; healthcheck cruzado Cloudflare↔VPS?
- [ ] ¿Datos corruptos: parar la escritura ANTES de restaurar; restore selectivo a base aparte por defecto; PITR contratado y restore ensayado en frío?
