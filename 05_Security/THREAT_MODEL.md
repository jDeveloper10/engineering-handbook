---
title: "Modelo de Amenazas — SaaS de Developer Solo"
category: 05_Security
doc_type: runbook
tags: [seguridad, threat-model, amenazas, hardening]
summary: "Ocho amenazas realistas para un developer solo sobre Cloudflare y Supabase, cada una con cómo ocurre, prevención, señales de detección, respuesta y recuperación, más un checklist de hardening priorizado."
keywords: [threat-model, amenazas, phishing, credential-stuffing, supply-chain, hardening]
updated: 2026-07-21
status: current
---

# THREAT MODEL — SaaS de developer solo sobre Cloudflare + Supabase

> Nivel 2 del dominio Security. Hereda todo de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) — no repite reglas de código; este documento modela **amenazas concretas** y qué hacer ante cada una. El runbook detallado de la primera hora vive en [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md).
>
> **Alcance deliberado:** amenazas realistas para un developer solo (o equipo de 2-3) con este stack. Quedan explícitamente fuera los escenarios enterprise que no aplican: insider threat corporativo, self-hosted CI runners, ataques a red interna de oficina, APTs dirigidos. El adversario típico aquí es automatizado y oportunista (bots, scanners, malware de commodity, phishing masivo) — y eso es una buena noticia: se defiende con higiene, no con un SOC.
>
> Formato por amenaza: **Cómo ocurre → Prevención → Detección (señales concretas) → Respuesta inmediata → Recuperación.**
>
> Realidad a asumir sin drama: en este modelo, la laptop del dev y sus cuentas (GitHub, Cloudflare, Supabase) **son** el perímetro. No hay "red corporativa"; hay una persona con sesiones abiertas a todo.

---

## A. Laptop del dev comprometida

**Cómo ocurre:** malware por descarga (paquete npm malicioso — ver amenaza D —, instalador falso, extensión de VSCode/navegador troyanizada), o acceso físico a un equipo sin cifrar. El botín no es la laptop: son las sesiones vivas (GitHub, Cloudflare, Supabase, email) y los secretos en disco (`.env`, `.dev.vars`, `~/.wrangler`, credenciales de `gh`).

**Prevención:**
- **[REQUIRED]** Disco cifrado (BitLocker en Windows) + bloqueo automático de pantalla.
- **[REQUIRED]** SO y navegador actualizados (las actualizaciones automáticas activadas, no "cuando pueda").
- **[REQUIRED]** Ningún secreto de producción en texto plano fuera de los archivos de entorno esperados: nada de secretos en notas, chats consigo mismo, capturas de pantalla o `secrets.txt` en el escritorio. **Por qué:** el malware de commodity busca patrones conocidos (`.env`, wallets, tokens de navegador); minimizar copias limita lo que encuentra.
- **[RECOMMENDED]** Cuenta del SO sin privilegios de admin para el trabajo diario.
- **[RECOMMENDED]** Password manager dedicado con vault bloqueado — no el almacén de passwords del navegador, que el malware exporta trivialmente.

**Detección:**
- Local: procesos/CPU anómalos, extensiones de navegador que no instalaste.
- Remota (la que de verdad funciona): logins desde IPs desconocidas en GitHub (Settings → Security log), Cloudflare (Audit Logs) y Supabase; commits o deploys que no hiciste; emails legítimos de "nuevo inicio de sesión" que no reconocés.

**Respuesta inmediata:**
1. Desconectar la máquina de la red.
2. Desde **otro dispositivo** (el teléfono cuenta): cambiar passwords y cerrar todas las sesiones de: email principal **primero** (con él se resetea todo lo demás), luego GitHub, Cloudflare, Supabase.
3. Tratar **todos** los secretos que tocaron esa máquina como filtrados → runbook (a) de [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md).

**Recuperación:**
- Reinstalación limpia del SO — no "pasar el antivirus y seguir": no se puede demostrar limpieza de un sistema comprometido.
- Restaurar solo datos; no restaurar binarios ni perfiles de navegador.
- Re-provisionar los secretos ya rotados (`.dev.vars`, `gh auth login`, `wrangler login`).
- Revisar los audit logs de los 3 proveedores buscando qué se hizo con las sesiones robadas durante la ventana.

---

## B. Cuenta de GitHub robada

**Cómo ocurre:** phishing del password (amenaza E), reuso de un password filtrado en otro sitio, o un PAT (personal access token) filtrado con scopes amplios. Con la cuenta, el atacante puede inyectar código al repo que se auto-deploya (Pages/Workers con integración Git) — es decir: **GitHub comprometido = deploy comprometido**.

**Prevención:**
- **[REQUIRED]** MFA con passkey o TOTP — verificar que el segundo factor no sea solo SMS.
- **[REQUIRED]** Password único, de password manager.
- **[REQUIRED]** PATs **fine-grained**: scope al repo concreto, permisos mínimos, expiración corta. Nunca un token clásico con `repo` global y sin caducidad. **Por qué:** el PAT es la versión robable de tu cuenta; su scope es el radio de daño.
- **[RECOMMENDED]** Commits firmados (SSH signing) + *vigilant mode*: hace visible ("unverified") un commit ajeno hecho en tu nombre.
- **[RECOMMENDED]** Branch protection en `main` aun siendo dev solo — te protege de tu propia cuenta robada, no de colegas.

**Detección:**
- Email de GitHub por login/dispositivo nuevo.
- Security log de la cuenta con eventos que no reconocés.
- Commits en el historial que no hiciste (badge "unverified" si firmás).
- Workflows de Actions ejecutados que no disparaste; deploy en Cloudflare cuyo commit no reconocés.

**Respuesta inmediata (desde sesión limpia, en este orden):**
1. Cambiar password.
2. `Settings → Sessions`: cerrar todas las sesiones.
3. Revocar todos los PATs y las OAuth/GitHub Apps no reconocidas (`Settings → Developer settings` y `Settings → Applications`).
4. Revisar webhooks y deploy keys de cada repo — un webhook agregado exfiltra cada push futuro.
5. Si hubo commits ajenos: tratar como deploy comprometido → runbook (c) de [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md).

**Recuperación:**
- Auditar `git log` completo desde la última actividad propia conocida.
- Revertir commits ajenos con revert explícito, no borrado silencioso del historial — querés el registro.
- Re-emitir PATs con scopes mínimos; verificar que la integración de deploy de Cloudflare apunta al estado sano.

---

## C. API key / secret filtrado (repo o frontend)

**Cómo ocurre:** las tres variantes reales:
1. Commit accidental de `.env`/`.dev.vars`, o un secreto hardcodeado "temporal" que se quedó.
2. Secreto puesto en una variable `VITE_*` que terminó embebida en el bundle público.
3. Secreto pegado en un issue, un log de CI o una captura de pantalla.

En repos públicos, los scanners de atacantes encuentran keys comiteadas **en minutos**, no en días.

**Prevención:**
- **[REQUIRED]** Sección 03 del estándar completa: `.gitignore` desde el commit 1, `wrangler secret put`, nada secreto en `VITE_*`, inventario de secretos.
- **[RECOMMENDED]** `gitleaks` como pre-commit hook.
- **[RECOMMENDED]** Una vez por release, grep del build del frontend buscando prefijos de keys conocidas: `grep -r "sb_secret\|whsec_\|re_" dist/` — barato, y atrapa la variante 2 antes que cualquier atacante.

**Detección:**
- Alerta de secret scanning de GitHub (llega incluso en repos públicos gratis).
- Email del proveedor ("detectamos tu key expuesta") — varios escanean repos públicos.
- Consumo anómalo: emails de Resend que no enviaste, requests/facturación inesperada en Cloudflare, filas o usuarios raros en Supabase.

**Respuesta inmediata:**
- **Rotar primero, limpiar después.** El orden importa: la key filtrada ya está copiada; reescribir el historial de git sin rotar es teatro.
- Runbook (a) de [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) con el orden exacto de rotación por proveedor.

**Recuperación:**
- Purgar del historial **después** de rotar (`git filter-repo`), o aceptar el historial sucio si el repo es privado y la key ya está muerta.
- Buscar en logs del proveedor qué hizo la key entre filtración y rotación: Resend (emails enviados), Supabase (Logs → API), Cloudflare (Audit Log).
- Post-mortem de una línea en el inventario: qué secreto, cómo se filtró, qué lo habría impedido.

---

## D. Dependencia npm maliciosa

**Cómo ocurre:** typosquatting (instalaste un nombre parecido al oficial), o un paquete legítimo cuyo maintainer fue comprometido publica una versión con malware — los ataques reales de 2023-2025 fueron casi todos esta segunda variante. Payload típico: un postinstall script que roba `.env`, tokens de npm/GitHub y wallets de la máquina del dev; o código runtime que exfiltra en producción.

**Prevención:**
- **[REQUIRED]** Sección 10 del estándar completa: lockfile + `npm ci`, nombres verificados contra docs oficiales, `npm audit` sin high/critical en producción.
- **[RECOMMENDED]** Regla de los ~7 días para versiones recién publicadas + `ignore-scripts` por defecto — estas dos matan la mayoría de los ataques de maintainer comprometido, que viven horas o pocos días antes de ser despublicados.

**Detección:**
- `npm audit` reportando malware (los paquetes comprometidos reciben advisory al descubrirse).
- Diff del lockfile con paquetes que no agregaste conscientemente — el diff del lockfile se lee, no se aprueba a ciegas.
- Tráfico de red saliente durante `npm install` hacia dominios desconocidos.
- Las señales de la amenaza A, si el payload ya corrió.

**Respuesta inmediata:**
1. Si un paquete instalado resulta malicioso: la máquina se trata como comprometida (amenaza A) — el postinstall ya corrió con tus permisos.
2. Todos los secretos accesibles desde esa máquina se tratan como filtrados (amenaza C → runbook (a)).
3. `npm uninstall` **no** cierra el incidente; solo quita la fuente.

**Recuperación:**
- La de la amenaza A (reinstalación limpia si el script llegó a ejecutar).
- Fijar en el lockfile la última versión conocida-buena del paquete afectado.
- Si era dependencia directa: evaluar reemplazarla o eliminarla — un maintainer comprometido una vez es una señal sobre el mantenimiento del paquete.

---

## E. Phishing / robo de sesión al dev

**Cómo ocurre:** email o DM imitando a GitHub/Cloudflare/Supabase/npm ("actividad sospechosa, verificá tu cuenta") que lleva a un login falso; o un ataque AiTM (adversary-in-the-middle) que captura password **y** código TOTP en tiempo real, o roba la cookie de sesión post-login. Los devs solos son blanco preferido: una cuenta, todo el reino.

**Prevención:**
- **[REQUIRED]** MFA en todo: email, GitHub, Cloudflare, Supabase, Contabo, npm si publicás. Donde exista la opción, **passkeys/WebAuthn** en vez de TOTP: están atadas al dominio y son inmunes al AiTM que sí captura códigos TOTP.
- **[REQUIRED]** Nunca loguearse desde un link recibido — siempre URL escrita a mano o bookmark. **Por qué:** la regla elimina la decisión bajo presión; no hay que "detectar" el phishing si jamás se navega desde el link.
- **[RECOMMENDED]** Logins de proveedores críticos guardados como bookmarks en carpeta dedicada — hace que la regla anterior no cueste nada.

**Detección:**
- Notificaciones de login que no reconocés.
- El password manager **no autocompleta** en la página de login: señal de dominio falso — tomarla en serio, jamás tipear el password a mano "porque el autofill falló".
- Sesiones activas desconocidas en los settings de cada proveedor.

**Respuesta inmediata:**
1. Si entregaste credenciales o sospechás sesión robada: en el servicio afectado — cambiar password → cerrar todas las sesiones → revocar tokens y apps autorizadas. En ese orden.
2. Si fue el email: el email primero, siempre (resetea todo lo demás).
3. Según el servicio: GitHub → amenaza B; Cloudflare/Supabase → amenaza H.

**Recuperación:**
- Audit log del servicio por acciones dentro de la ventana comprometida.
- Buscar mecanismos de persistencia dejados por el atacante: reglas de forwarding en el email, PATs nuevos, deploy keys, API tokens nuevos en Cloudflare, "authorized apps" nuevas en cualquier proveedor.

---

## F. Credential stuffing contra usuarios de la app

**Cómo ocurre:** bots prueban en tu login combos email:password filtrados de otros sitios. No es un ataque "a tu app" — es tráfico de fondo de internet contra cualquier endpoint de login público. Algún porcentaje de tus usuarios reusa passwords, así que algunos combos **van a funcionar**.

**Prevención:**
- **[REQUIRED]** Rate limits de Supabase Auth activos y dimensionados (dashboard → Auth → Rate Limits).
- **[REQUIRED]** Protección de contraseñas filtradas de Supabase Auth activada (verifica passwords contra corpus de leaks; confirmar disponibilidad en el plan actual del proyecto) + requisitos mínimos de password configurados.
- **[RECOMMENDED]** Turnstile también en login (no solo signup) cuando la app ya tenga usuarios que perder.
- **[RECOMMENDED]** MFA opcional ofrecida a los usuarios.

**Detección:**
- Auth logs de Supabase: ráfagas de `invalid credentials` repartidas en **muchos emails distintos** (stuffing) vs. muchos intentos sobre **un** email (targeting de una cuenta).
- Usuarios reportando "actividad que no fue mía".
- Picos de tráfico al endpoint de token sin pico de usuarios reales.

**Respuesta inmediata:**
1. Para cuentas comprometidas confirmadas: invalidar sus sesiones (ban temporal o revocación de sesiones vía admin API de Supabase) y forzar reset de password.
2. Notificar a los usuarios afectados con instrucción explícita de no reusar el password anterior.
3. Endurecer temporalmente rate limits; activar Turnstile en login si no estaba.

**Recuperación:**
- Dimensionar qué vio el atacante en cada cuenta tomada: con RLS bien hecha, el blast radius es exactamente los datos de ese usuario — verificarlo, no asumirlo.
- Documentar patrón de IPs/ASN; crear regla WAF si el ataque se repite desde la misma infraestructura.

---

## G. Scraping / abuso de endpoints públicos

**Cómo ocurre:** bots descubren tus endpoints públicos (Workers, forms, webhooks de n8n) por fuerza bruta de rutas o leyendo el JS del frontend (donde las URLs de los Workers son visibles por diseño). Consecuencias: costo (invocaciones, emails de Resend, filas basura), datos públicos cosechados en masa, y saturación del VPS de n8n — que, a diferencia de los Workers, **no escala solo**.

**Prevención:**
- **[REQUIRED]** Sección 07 del estándar completa: rate limit en todo endpoint público, Turnstile en forms con costo.
- **[REQUIRED]** VPS de Contabo: firewall que solo expone 443, SSH solo con key (idealmente restringido por IP o detrás de VPN), n8n con HTTPS y auth activada, webhooks de n8n con header secreto.
- **[RECOMMENDED]** Dominio de n8n detrás del proxy de Cloudflare (nube naranja) para heredar WAF y rate limiting también ahí.
- **[RECOMMENDED]** Endpoints públicos de solo-lectura con caché (Cache API / CDN): el scraping pega en caché, no en la DB.

**Detección:**
- Analytics de Cloudflare: picos de requests por ruta/IP/ASN sin correlato de usuarios.
- Facturación de Resend o invocaciones de Workers creciendo sin crecimiento de usuarios.
- VPS: CPU/RAM saturada; logs con rutas escaneadas (`/wp-admin`, `/.env` — ruido normal de internet; el **volumen** es la señal).

**Respuesta inmediata:**
1. Identificar el patrón (IP, ASN, user-agent, ruta) en analytics.
2. Regla WAF de bloqueo o challenge para ese patrón.
3. Si el abuso es contra un form: verificar que Turnstile + rate limit están **efectivamente activos** — no "configurados una vez y nunca verificados".

**Recuperación:**
- Limpiar datos basura generados (filas, colas de email).
- Recalibrar límites con lo aprendido: el límite correcto es el que este ataque habría tocado.
- Si scrapearon datos que no debían ser públicos: eso no es abuso, es un IDOR o una tabla sin RLS — tratar como incidente de acceso → runbook (b).

---

## H. Cuenta de Cloudflare o Supabase comprometida

**Cómo ocurre:** vía amenazas A/C/E (sesión robada, API token filtrado, phishing). Es el peor escenario del stack: Cloudflare comprometido = control de DNS, Workers, R2 y certificados — puede servir **cualquier cosa** bajo tu dominio; Supabase comprometido = todos los datos de todos los usuarios y el control de Auth.

**Prevención:**
- **[REQUIRED]** MFA en ambas cuentas (preferir passkeys — amenaza E).
- **[REQUIRED]** API tokens de Cloudflare con scope y TTL mínimos; la **Global API Key no se usa para nada**, jamás en tooling.
- **[REQUIRED]** Integraciones de terceros conectadas a Supabase solo vía mecanismos oficiales con scope al proyecto — nunca entregando el password del dashboard.
- **[RECOMMENDED]** Backup externo de la DB (export programado **fuera** de Supabase): un atacante con el dashboard puede borrar la DB *y* sus backups internos.
- **[RECOMMENDED]** El inventario de secretos registra qué API tokens de Cloudflare existen y para qué — para poder revocar con confianza.

**Detección:**
- Cloudflare Audit Log (Manage Account → Audit Log): cambios de DNS, Workers desplegados, tokens creados que no hiciste.
- Supabase: migraciones/funciones/usuarios admin que no creaste; cambios en Auth settings — especialmente redirect URLs y providers.
- Emails de login nuevo de ambos proveedores; usuarios reportando contenido raro bajo tu dominio.

**Respuesta inmediata (desde sesión limpia):**
1. Cambiar password + cerrar sesiones + revocar **todos** los API tokens del proveedor afectado.
2. Cloudflare: verificar de inmediato DNS y la lista de Workers/rutas contra lo esperado — quien controla DNS puede montar phishing de tus propios usuarios bajo tu dominio.
3. Supabase: rotar service_role/keys (runbook (a)) y revisar Auth settings completos.
4. Encadenar con runbook (b) o (c) según lo que el atacante haya tocado.

**Recuperación:**
- Reconstruir la confianza recurso por recurso contra una referencia conocida: los `wrangler.toml` del repo dicen qué Workers y rutas deben existir; las migraciones del repo dicen qué schema debe existir. **Esta es la razón de seguridad para que infra y schema vivan en el repo.**
- Restaurar la DB desde backup si hubo modificación de datos.
- Si el atacante tocó DNS: revisar también los registros de email (MX, SPF/DKIM en TXT) — un registro alterado le permite seguir recibiendo o enviando correo como vos después de expulsado.

---

## Checklist de hardening priorizado

**HOY (una sentada, ~1 hora — elimina los caminos de mayor daño):**
- [ ] MFA activada en: email principal, GitHub, Cloudflare, Supabase, Contabo — passkeys donde se pueda, nunca solo SMS.
- [ ] Password manager con passwords únicos en esas 5 cuentas (las 5 que se resetean entre sí).
- [ ] Confirmar que la Global API Key de Cloudflare no está en ningún tooling; solo API tokens con scope.
- [ ] Grep del repo y de `dist/` buscando secretos (`sb_secret`, `whsec_`, `re_`, `SERVICE_ROLE`); `.env*` y `.dev.vars` en `.gitignore`.
- [ ] RLS verificado en todas las tablas de `public` (Security Advisor de Supabase — 2 clicks).
- [ ] Disco de la laptop cifrado (BitLocker) y bloqueo automático activado.

**ESTA SEMANA (procedimientos y detección):**
- [ ] Inventario de secretos escrito (nombre → dónde se usa → dónde se rota) — prerequisito del runbook de incidentes.
- [ ] `gitleaks` como pre-commit hook.
- [ ] Rate limits de Supabase Auth revisados + protección de passwords filtrados activada (según plan).
- [ ] Turnstile en todo form público que genere costo (signup, contacto).
- [ ] Firewall del VPS: solo 443 + SSH con key; auth de n8n activada; webhooks de n8n con header secreto.
- [ ] Headers de seguridad + CSP en Report-Only desplegados (sección 06 del estándar).
- [ ] Leer [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) completo una vez, en frío — el runbook solo sirve si ya lo conocés cuando tiemblan las manos.

**ESTE MES (resiliencia):**
- [ ] Backup externo programado de la DB + **un restore de prueba realizado** — un backup no probado es una esperanza, no un backup.
- [ ] CSP pasado de Report-Only a bloqueante.
- [ ] PATs de GitHub auditados: fine-grained, scope mínimo, con expiración; commits firmados + vigilant mode.
- [ ] Dominio de n8n detrás del proxy de Cloudflare.
- [ ] Rotación de práctica de un secreto de bajo riesgo siguiendo el runbook (a) — ensayo del procedimiento real antes de necesitarlo.
- [ ] Revisión mensual en calendario: audit logs (GitHub/Cloudflare/Supabase), `npm audit`, Security Advisor, facturación/consumo de los 4 proveedores.
