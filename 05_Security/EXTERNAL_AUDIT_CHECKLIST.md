---
title: "Checklist de Verificación Externa — qué replicar y cómo probarlo tú mismo"
category: 05_Security
doc_type: referencia
tags: [checklist, auditoria-externa, cors, csp, headers, rls, vps, verificacion]
summary: "Catálogo de prácticas confirmadas por auditoría de caja negra real (curl, nmap, Supabase Advisors) contra los proyectos en producción del usuario el 2026-08-11 — qué salió bien, en qué proyecto se verificó, y el comando exacto para volver a probarlo en cualquier proyecto nuevo."
keywords: [cors, csp, rls, headers de seguridad, nmap, supabase, vps, checklist pre-lanzamiento]
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "Auditoría de caja negra real ejecutada el 2026-08-11 (curl + nmap + Supabase Advisors MCP) contra ~15 dominios en producción del usuario"
  - "OWASP ASVS v4.0.3 — respaldo de las prácticas verificadas"
  - "SECURITY_ENGINEERING_STANDARD.md — reglas S-001…S-014 de este handbook, referenciadas donde aplica"
updated: 2026-08-11
---

# CHECKLIST DE VERIFICACIÓN EXTERNA

> Este documento no inventa reglas nuevas. Es la prueba de que las reglas de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) funcionan, sacada de auditar tus propios proyectos desde afuera — como lo haría un atacante, sin credenciales previas. Cada punto trae **en qué proyecto se confirmó** y **el comando para volver a probarlo** en el próximo.

---

## 1. Lo que ya haces bien — replícalo tal cual

### 1.1 CORS: lista blanca real, nunca el Origin reflejado

La falla común es devolver `Access-Control-Allow-Origin: <lo que el navegador mande en Origin>` — eso deja pasar a cualquier sitio. Lo correcto es una whitelist fija que ignora lo que pida el atacante.

**Verificado en:** `api.gabybeautysupply.com` (TiendaGaby), `keitlin-api.keitlinacademy.workers.dev`, `api.grouplegacy.club` — probé con `Origin: https://evil-attacker.com` y con un segundo origin distinto: el header de respuesta **no cambió**, siguió devolviendo el dominio legítimo.

**Cómo probarlo en el próximo proyecto:**
```bash
curl -s -D - -o /dev/null -H "Origin: https://cualquier-cosa-inventada.com" "https://tu-api.com" | grep -i access-control-allow-origin
```
Si el valor que sale es exactamente `https://cualquier-cosa-inventada.com` (lo que tú mandaste), está mal — está reflejando. Si sale tu dominio real fijo, está bien.

### 1.2 CSP sin `unsafe-inline` / `unsafe-eval`, `connect-src` acotado

**Verificado en:** `grouplegacy.club` — la mejor CSP de todo lo auditado: `script-src 'self'` a secas, `connect-src` limita a los dominios propios exactos (no comodines), `frame-ancestors 'none'`, `form-action 'self'`.

**Contraejemplo real (lo que NO hacer):** `jonnytrader.com` tiene `connect-src 'self' https: wss:` — el comodín `https:` permite conectar a *cualquier* dominio HTTPS del planeta. Frente a un XSS, esa CSP no protege casi nada.

**Cómo probarlo:**
```bash
curl -s -D - -o /dev/null "https://tu-sitio.com" | grep -i content-security-policy
```
Revisa a mano: si `script-src` tiene `unsafe-inline`/`unsafe-eval`, o si `connect-src`/`frame-src` tienen un esquema pelado (`https:`, `wss:`) en vez de dominios exactos, está débil. Usa `grouplegacy.club` como plantilla.

### 1.3 Headers base completos

**Verificado en:** la mayoría de proyectos con dominio custom (ingenusfx, jonnyTrader, legacy-club, gabyandbeauty.com). **Contraejemplo:** `xworked.online` no tenía ninguno.

**Mínimo a copiar siempre:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
```

**Cómo probarlo:**
```bash
curl -s -D - -o /dev/null "https://tu-sitio.com" | grep -iE "strict-transport|x-content-type|x-frame|referrer-policy"
```

### 1.4 Endpoints internos exigen auth real — nunca públicos por defecto

**Verificado en:** `admin-worker`, `payments-worker`, `chat-worker` (ingenusfx), `keitlin-api`, `gaby-academy-api`, `api.grouplegacy.club`, `unapp-api` — todos responden `401` sin token, incluso en su URL directa `.workers.dev` que bypassea el dominio custom.

**Cómo probarlo:** pega la URL del worker sin ningún header de auth. Si responde con datos (`200` + JSON con contenido real) en vez de `401`/`403`, está mal.

### 1.5 El bundle de frontend no filtra secretos de servidor

**Verificado en:** `danianailsbeauty.online/admin` — descargué el JS de producción (687 KB) y lo revisé buscando `service_role`, `sk_live`, claves privadas: nada. Solo config client-safe (Firebase client config, Cloudinary cloud name, site keys de reCAPTCHA — esas sí son públicas por diseño).

**Cómo probarlo:**
```bash
curl -s "https://tu-sitio.com" | grep -oE '/assets/[a-zA-Z0-9_.-]*\.js' # encuentra el bundle
curl -s "https://tu-sitio.com/ese-bundle.js" | grep -aoE "(service_role|sk_live_|sk_test_|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
```
Si algo de eso imprime resultado, hay una clave de servidor en el cliente — S-001 roto.

### 1.6 Buckets R2/S3 públicos sin listado de directorio

**Verificado en:** 6 buckets `pub-*.r2.dev` en uso (TiendaGaby, MadelineWeb, etc.) — todos devuelven `404` al pedir listado (`?list-type=2`), solo sirven objetos por key exacta.

**Cómo probarlo:**
```bash
curl -s -o /dev/null -w "%{http_code}\n" "https://pub-tu-bucket.r2.dev/?list-type=2"
```
`404` o `403` está bien. Un `200` con XML de objetos listados es una fuga — cualquiera puede enumerar todo lo que subiste.

### 1.7 VPS: la app nunca expone su puerto directo, solo el reverse proxy

**Verificado en:** VPS del bot de WhatsApp de TiendaGaby (Hetzner) — la app Node corre en el puerto 3000, pero **no es alcanzable desde afuera**. Solo `22` (SSH), `80` y `443` (Caddy) están abiertos; Caddy además rechaza servir contenido si el `Host`/SNI no coincide con un dominio configurado.

**Cómo probarlo:**
```bash
nmap -Pn -p- --open tu-vps-ip   # o al menos --top-ports 100
```
Si ves el puerto de tu app (3000, 5000, 8000, lo que sea) abierto directo, falta el reverse proxy o el firewall.

### 1.8 `.env` nunca trackeado en git

**Verificado en:** `MadelineWeb` — tenía un `CLOUDFLARE_API_TOKEN` en texto plano en disco, pero `.gitignore` lo excluye y `git ls-files` confirma que nunca se subió al remoto.

**Cómo probarlo antes de cada push:**
```bash
git ls-files | grep -E "^\.env"   # no debe imprimir nada
git check-ignore -v .env          # debe confirmar que está ignorado
```

### 1.9 TLS sin cifrados débiles

**Verificado en:** el hosting compartido de `torneoProgramacion` (BanaHosting) — `nmap --script ssl-enum-ciphers` calificó **A en todos los cifrados**, sin RC4 ni export ciphers, certificado Let's Encrypt vigente.

**Cómo probarlo:**
```bash
nmap -Pn --script ssl-enum-ciphers -p 443 tu-dominio.com
```

---

## 2. Lo que salió mal — la prueba de por qué estas reglas existen

No son advertencias abstractas. Son cosas que encontré rotas de verdad el 2026-08-11:

| Falla real encontrada | Proyecto | Consecuencia verificada |
|---|---|---|
| RLS deshabilitado en tablas públicas de Supabase | jonnyTrader | Leí en vivo, sin login, las señales de trading y el balance real de la cuenta ($9,903.92) con la anon key del bundle |
| Puerto de base de datos abierto a todo internet | torneoProgramacion (MySQL 3306) | Cualquier IP del mundo puede intentar conectar, no solo tu app |
| CORS wildcard (`*`) en endpoints POST que aceptan `Authorization` | keitlin-email, keitlin-upload, jonnytrader.com `/api/broadcast-new` | No pude confirmar si exigen auth interna — si no, cualquier sitio los invoca directo |
| Funciones `SECURITY DEFINER` ejecutables por `anon` sin revisar qué validan internamente | jonnyTrader / Supabase | `tukiosko_set_user_role` es invocable sin sesión — corre saltándose RLS |
| CSP con comodín `https:`/`wss:` en `connect-src` | jonnytrader.com | Ante un XSS, se puede exfiltrar a cualquier destino HTTPS |

**Regla derivada, para todo proyecto nuevo:** antes de dar por "lanzado" cualquier proyecto con Supabase, correr `get_advisors` (tipo `security`) contra el proyecto — habría atrapado el problema de jonnyTrader el mismo día que se creó la tabla, no meses después en una auditoría externa.

---

## 3. Checklist de pre-lanzamiento — cópialo para cada dominio nuevo

```bash
D="tu-dominio.com"

# 1. Headers base
curl -s -D - -o /dev/null "https://$D" | grep -iE "strict-transport|x-content-type|x-frame|content-security-policy|referrer-policy"

# 2. CORS no reflejado
curl -s -D - -o /dev/null -H "Origin: https://evil-test.com" "https://api.$D" | grep -i access-control-allow-origin

# 3. Endpoints protegidos responden 401, no datos
curl -s -o /dev/null -w "%{http_code}\n" "https://api.$D/ruta-que-deberia-requerir-auth"

# 4. Bundle sin secretos de servidor
curl -s "https://$D" | grep -oE '/assets/[a-zA-Z0-9_.-]*\.js' | head -1

# 5. Puertos del VPS/origin (si no está detrás de Cloudflare)
nmap -Pn --top-ports 50 "$D"

# 6. Si usa Supabase: advisors de seguridad
#    (vía MCP: get_advisors project_id=<id> type=security)
```

Si los seis pasan, el proyecto está al nivel de tus mejores implementaciones (`grouplegacy.club`, el VPS de TiendaGaby). Si alguno falla, ya sabes exactamente qué sección de este documento te dice cómo se ve la versión correcta.
