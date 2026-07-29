# INCIDENT RESPONSE — runbook de la primera hora

> Nivel 2 del dominio Security. Hereda de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md); las amenazas que llevan a cada escenario están modeladas en [THREAT_MODEL.md](THREAT_MODEL.md). Este documento es un **runbook operativo**: qué hacer, en qué orden, con qué comando — pensado para leerse bajo estrés, por vos o por una IA asistiendo en vivo.
>
> **Prerequisito que se cumple HOY, no durante el incidente:** el inventario de secretos (estándar, sección 03) existe y está al día. Sin él, el paso "rotar todo lo afectado" es adivinanza.

---

## Triage en 60 segundos — ¿qué runbook aplica?

| Síntoma | Runbook |
|---|---|
| Alerta de secret scanning, key en un commit, secreto en el bundle, `.env` expuesto | **(a) Secreto filtrado** |
| Laptop posiblemente comprometida (malware, paquete npm malicioso instalado) | **(a)** para todos los secretos de la máquina + amenaza A del threat model |
| Filas/usuarios que no creaste, mutaciones masivas, un usuario viendo datos ajenos | **(b) Actividad anómala en la DB** |
| Consumo de Resend/Workers/DB sin correlato de usuarios | **(a)** si apunta a key usada por terceros; **(b)** si apunta a acceso a datos |
| Código en producción que no escribiste (worker o frontend) | **(c) Deploy comprometido** |
| Login ajeno en GitHub / Cloudflare / Supabase | Amenaza B/H del threat model → encadena con **(a)/(c)** según lo tocado |

Los runbooks se encadenan: un incidente real rara vez es uno solo. Cada runbook indica cuándo saltar a otro.

---

## Reglas generales (aplican a los tres escenarios)

**[REQUIRED] Contener antes que investigar.** Primero se corta el acceso del atacante (rotar, revocar, bloquear, rollback), después se averigua qué pasó. El orden inverso regala minutos de acceso a cambio de curiosidad.

**Por qué:** el daño crece con el tiempo de acceso, no con el tiempo de ignorancia. Los logs van a seguir ahí después de rotar; el atacante no va a esperar a que termines de leerlos.

**[REQUIRED] Trabajar desde una sesión limpia.** Si el escenario implica posible compromiso de la laptop o de una cuenta (amenazas A/B/E/H), los pasos se ejecutan desde un dispositivo o perfil no comprometido. Rotar un secreto desde la máquina que lo está exfiltrando es rotarlo hacia el atacante.

**[REQUIRED] Anotar mientras se actúa.** Una nota simple con timestamps: qué se encontró, qué se rotó, a qué hora. No es burocracia — es lo que después permite saber qué ventana de logs revisar y qué quedó pendiente.

**[REQUIRED] Rotar significa el ciclo completo:** emitir nuevo → desplegar nuevo → revocar viejo → **verificar viejo muerto**. Los cuatro pasos.

**Por qué el orden dentro del ciclo:** revocar antes de desplegar tira la app abajo (aceptable si el abuso es activo — se decide conscientemente, no por accidente); desplegar sin revocar deja la puerta abierta; no verificar deja la duda para siempre.

---

## (a) Secreto filtrado

### Minuto 0-5 — alcance

1. Identificar **qué** secreto(s) y **desde cuándo** (fecha del commit, o del deploy del bundle que lo contiene).
2. Contra el inventario de secretos: ¿qué puede hacer ese secreto y qué workers/servicios lo usan?
3. Regla de decisión sobre la urgencia:
   - Filtración en repo **público** o en el bundle del frontend → asumir copiado por terceros (los scanners tardan minutos).
   - Repo **privado** → asumir copiado igualmente y rotar; solo cambia la urgencia, nunca la acción.

### Minuto 5-45 — rotación, en este orden

El orden va de "más poder / más expuesto" a menos, y deja GitHub al final porque sus tokens no suelen estar desplegados en runtime.

**1. Cloudflare** (si lo filtrado es un API token de CF, o secretos que viven en Workers):

- API token filtrado: dashboard → My Profile → API Tokens → **Roll** (o Delete) sobre el token afectado. Aprovechar para matar todo token no reconocido.
- Secretos de Workers (p. ej. la `service_role` que un worker usa):
```
# en el directorio de cada worker afectado (el inventario dice cuáles):
wrangler secret list                             # confirmar qué secretos tiene este worker
wrangler secret put SUPABASE_SERVICE_ROLE_KEY    # pega el valor NUEVO (emitido en el paso 2)
# el put re-deploya el worker con el secreto nuevo; repetir por worker afectado
```

**2. Supabase** (si lo filtrado es `service_role`, keys de API o el JWT secret):

- Dashboard → Settings → API.
- Proyectos con las **API keys nuevas** (`sb_secret_...` / `sb_publishable_...`): rotar la secret key genera una nueva y permite revocar la vieja **sin** tocar sesiones de usuarios.
- Proyectos **legacy** (keys `anon`/`service_role` como JWTs firmados con el JWT secret): rotar exige regenerar el **JWT secret**, lo que invalida ambas keys **y todas las sesiones de usuarios activas**. Hacerlo igual si la `service_role` se filtró: una `service_role` viva en manos ajenas es acceso total a la DB; unos re-logins no son precio.
- Verificar en docs oficiales cuál esquema usa el proyecto — idealmente **antes** del incidente, y anotarlo en el inventario.
- Tras rotar: `wrangler secret put` del valor nuevo en cada worker que lo usa (paso 1) y actualizar `.dev.vars` local.

**3. Resend** (si se filtró una API key `re_...`):

1. Dashboard de Resend → API Keys → crear key nueva con scope mínimo (solo sending, dominio concreto).
2. `wrangler secret put RESEND_API_KEY` en los workers que envían email.
3. Borrar la key vieja y verificar que ya no aparece en el dashboard.
4. Revisar el log de emails enviados durante la ventana — un atacante con key de Resend manda phishing **desde tu dominio verificado**.

**4. Signing secrets de webhooks** (`whsec_...` de Resend/Svix u otros):

- Regenerar el signing secret en el dashboard del proveedor → `wrangler secret put` del nuevo en el worker receptor.
- La ventana de firmas inválidas dura segundos y los proveedores reintentan: aceptable.

**5. GitHub** (si se filtró un PAT o hay sospecha sobre la cuenta):

```
gh auth status        # ¿qué identidad y scopes tiene el CLI ahora mismo?
```
- PATs: Settings → Developer settings → Personal access tokens → revocar el filtrado **y** los no reconocidos.
- Re-emitir fine-grained, con scope y expiración mínimos.
- Re-autenticar el CLI: `gh auth login`.
- Si hay señales de uso ajeno de la cuenta (no solo del token): amenaza B completa del threat model.

**6. Otros, según inventario:**

- Header secreto de los webhooks de n8n: cambiarlo en el flujo de n8n y en el worker que lo llama.
- Tokens de R2: dashboard → R2 → API tokens → crear nuevo con scope al bucket → borrar el viejo.
- Credenciales del VPS (SSH, panel de Contabo) si estuvieron en lo filtrado.

### Minuto 45-60 — verificación y ventana de daño

- **Verificar que lo viejo está muerto:** un request de prueba con la key vieja debe devolver 401/403. Sin esta prueba, la rotación es una creencia.
- Revisar la ventana filtración→rotación en los logs de cada proveedor:
  - Resend: emails enviados que no reconocés.
  - Supabase: Logs → API / Auth — accesos con la key filtrada.
  - Cloudflare: Audit Log + métricas de Workers.
- Si hay evidencia de uso ajeno contra la DB → encadenar con el runbook **(b)**.
- **Después** (no antes) limpiar la fuente: quitar el secreto del código, purgar historial si amerita (`git filter-repo`), o re-deployar el frontend sin la variable.
- Actualizar el inventario con la fecha de rotación.

---

## (b) Actividad anómala en la DB

### Minuto 0-10 — foto y primera pregunta

1. **Capturar evidencia antes de que rote:** dashboard de Supabase → Logs: exportar/copiar los API logs y Postgres logs de la ventana sospechosa (la retención de logs es limitada — capturar primero, analizar después).
2. Foto de la actividad viva, en el SQL Editor:
```sql
select pid, usename, application_name, client_addr, state, query, query_start
from pg_stat_activity
where state <> 'idle'
order by query_start;
```
3. **Primera pregunta: ¿por dónde entró?** Tres respuestas, tres caminos:
   - **Credencial admin filtrada** (`service_role`, password de Postgres, sesión del dashboard) → es el escenario (a): rotar YA (paso 2 del runbook (a)), después volver aquí.
   - **Agujero de autorización** (tabla sin RLS, política mal escrita, IDOR en un worker) → continuar en el paso 4.
   - **Cuenta de usuario individual comprometida** (credential stuffing — amenaza F) → invalidar las sesiones de esa cuenta y seguir el flujo de la amenaza F; este runbook sigue aplicando solo si tocó datos de **otros** usuarios.

### Minuto 10-40 — contener el agujero

4. Buscar el agujero más común primero — tablas expuestas:
```sql
select schemaname, tablename
from pg_tables
where schemaname = 'public' and rowsecurity = false;
```
5. Toda tabla que aparezca: `alter table public.<t> enable row level security;` **ya**.
   - Con RLS habilitada y sin políticas, la tabla queda cerrada para `anon`/`authenticated` (fail closed).
   - Eso puede romper features legítimas: **preferible roto-y-cerrado a abierto.** Las políticas correctas se escriben después, con calma.
6. Revisar el Security Advisor (Advisors → Security) por el resto del catálogo: vistas security definer, funciones con `search_path` mutable, políticas laxas.
7. Si el vector fue un endpoint de un worker (IDOR): sacar la ruta de servicio — respuesta 503 en esa ruta, o `wrangler deploy` de una versión con el handler deshabilitado — hasta tener el fix. No se deja el endpoint vivo "mientras lo arreglo".
8. Si hay exfiltración o mutación masiva **activa en este momento** y el agujero no aparece: opción nuclear = pausar el proyecto de Supabase (dashboard → Settings → Pause). Baja toda la app. La decisión es un cálculo explícito: ¿el daño por minuto supera el costo del downtime?

### Minuto 40-60 — daño y estado

9. **Backup ahora, antes de reparar datos:** un export manual inmediato congela el estado post-incidente para análisis, y es la red de seguridad si la reparación sale mal — aunque existan backups automáticos.
10. Dimensionar el daño con los logs capturados: ¿qué tablas y filas, lectura o escritura, cuántos usuarios afectados, entre qué horas? Por escrito.
    - Esto define si hay que notificar a usuarios — y, según jurisdicción y tipo de datos, si existe obligación legal de notificar. Esa evaluación es post-primera-hora, pero **la evidencia que la alimenta se captura ahora**.
11. Reparar datos: revertir las mutaciones identificadas a mano, o restaurar las tablas afectadas desde un backup previo al incidente (dashboard → Database → Backups / PITR según plan).
12. Antes de cerrar el incidente:
    - Fix real del agujero (políticas correctas, handler con filtro por dueño).
    - Un test que **reproduce el acceso que el atacante logró** y verifica que ya no funciona — el test es la prueba de cierre, no la sensación de haberlo arreglado.

---

## (c) Deploy comprometido

### Minuto 0-15 — volver a un estado bueno conocido

1. **Workers** — identificar y revertir al último deploy propio, por cada worker afectado:
```
wrangler deployments list      # en el directorio del worker: versiones, fuente (Git/upload) y fecha
wrangler rollback              # revierte al deployment anterior (o pasar el ID de la versión buena)
```
   - Si no podés determinar cuál versión es la buena: rollback a la última cuya fecha/hora reconocés como actividad tuya.
2. **Pages (frontend)** — dashboard → el proyecto → Deployments:
   - Identificar el último deployment cuyo commit reconocés.
   - Menú del deployment → **Rollback**.
   - (Verificar en docs oficiales si la versión actual de wrangler expone esto por CLI; el dashboard siempre puede.)
3. **Desactivar los auto-deploys** mientras dure el incidente (pausar la integración Git de Pages/Workers Builds en el dashboard). **Por qué:** si el atacante controla el repo, cada rollback tuyo es seguido de un push suyo — sin este paso, el runbook es una carrera que perdés.

### Minuto 15-40 — cortar el origen

4. ¿Cómo llegó el deploy? Dos orígenes posibles; no son excluyentes — ante la duda, revisar ambos.

**Origen A — vía Git** (el atacante empujó código al repo). Desde sesión limpia:
```
git log --all --format='%h %an %ae %ad %s' --since='7 days ago'    # commits que no reconocés
gh api repos/{owner}/{repo}/events --paginate                       # eventos recientes, con actor
gh api repos/{owner}/{repo}/hooks                                   # webhooks que no agregaste
gh api repos/{owner}/{repo}/keys                                    # deploy keys ajenas
```
   - Si hay actividad ajena → ejecutar la respuesta de la amenaza B completa (password, sesiones, PATs, OAuth apps) **antes** de reactivar auto-deploys.

**Origen B — deploy directo a Cloudflare** (sin commit — el atacante tiene una credencial de CF):
   - `wrangler deployments list` muestra la fuente de cada versión (upload directo vs Git).
   - Uploads directos ajenos → respuesta de la amenaza H: password de CF, cierre de sesiones, revocación de **todos** los API tokens. El rollback no sirve mientras el token del atacante siga vivo.

5. Si el vector fue una **dependencia maliciosa** (el código malo entró en un build propio, sin cuenta robada):
   - Rollback (paso 1-2) + fijar el lockfile a la última versión buena del paquete.
   - La máquina de build (tu laptop) se trata según la amenaza A del threat model.

### Minuto 40-60 — daño y reconstrucción

6. **¿Qué hizo el código malicioso mientras estuvo vivo?** Leer el diff del deploy malo — el commit ajeno, o la versión descargada desde el dashboard de Workers:
   - ¿Exfiltraba requests (credenciales de usuarios en tránsito)?
   - ¿Servía malware o redirigía a usuarios?
   - ¿Leía secretos del worker o tocaba la DB?
7. Encadenar según la respuesta:
   - Veía secretos del worker → runbook **(a)** para esos secretos.
   - Leía/escribía la DB → runbook **(b)**.
   - Capturaba credenciales de usuarios en login → invalidar sesiones + forzar reset de password de los usuarios del período + notificarlos.
8. Verificar la integridad de lo que quedó desplegado: la lista de Workers y rutas del dashboard contra los `wrangler.toml` del repo — el atacante puede haber dejado un worker o una ruta extra que el rollback no toca.
9. Reactivar auto-deploys solo cuando se cumplan las tres: cuenta de origen asegurada + repo limpio + deploy actual verificado.

---

## Checklist final (después de cualquiera de los tres)

- [ ] ¿Todo secreto afectado pasó el ciclo completo: nuevo emitido → desplegado → viejo revocado → viejo verificado muerto (request de prueba con 401/403)?
- [ ] ¿El inventario de secretos quedó actualizado (fechas de rotación, secretos nuevos)?
- [ ] ¿Los logs de la ventana del incidente quedaron capturados antes de expirar por retención?
- [ ] ¿La ventana de daño está dimensionada por escrito: qué se accedió/modificó/envió, entre qué horas, cuántos usuarios?
- [ ] ¿Usuarios afectados notificados si sus datos o sesiones se comprometieron (y evaluada la obligación legal según datos y jurisdicción)?
- [ ] ¿El agujero raíz tiene fix desplegado + test que demuestra que el acceso del atacante ya no funciona?
- [ ] ¿Sesiones y tokens revisados en TODOS los proveedores tocados, no solo el del incidente: GitHub, Cloudflare, Supabase, Resend, email, VPS?
- [ ] ¿Auto-deploys reactivados conscientemente (no quedaron pausados por olvido)?
- [ ] ¿Post-mortem de 5 líneas escrito: qué pasó, cómo entró, qué lo habría prevenido, qué regla del estándar faltaba o no se cumplió?
- [ ] Si faltaba una regla: ¿se propuso la actualización a [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) o [THREAT_MODEL.md](THREAT_MODEL.md)?
