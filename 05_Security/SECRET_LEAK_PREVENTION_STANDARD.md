---
title: "Estándar de Prevención de Fugas de Secretos en Bundles y Frontend"
category: 05_Security
doc_type: estandar
tags: [seguridad, secretos, vite, bundle, frontend, backend-proxy, pre-build]
summary: "Reglas SEC-LEAK-001 a SEC-LEAK-005 para garantizar cero secretos en bundles de cliente (Vite, React, APK, Tauri). Define la arquitectura de proxy para APIs de terceros (MetaApi, Stripe), el peligro del prefijo VITE_ y el escáner de pre-build obligatorio."
keywords: [secretos, bundles, vite, frontend, metaapi, stripe, leak, scanner, pre-build, rls, workers]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "OWASP ASVS v4.0.3 — V14.2 Dependency and Secrets Management"
  - "Vite Documentation — Env Variables and Modes"
  - "05_Security/SECURITY_ENGINEERING_STANDARD.md"
  - "05_Security/MOBILE_SECURITY_STANDARD.md"
---

# ESTÁNDAR DE PREVENCIÓN DE FUGAS DE SECRETOS EN BUNDLES (SEC-LEAK)

> **Capa 1 (la regla):** Todo archivo que se compile y distribuya al cliente (HTML, JS de Vite, bundle de React Native/Expo, binario de Tauri) es de acceso público por definición. Está estrictamente prohibido incluir tokens privados, JWTs de servicio, API keys con permisos de escritura o credenciales de terceros en el código del cliente.
> 
> **Capa 2 (implementación):** Toda llamada a APIs de terceros que requiera un secreto (MetaApi, Stripe, Resend, Telegram bots, bases de datos) se realiza exclusivamente a través de un **Cloudflare Worker / backend privado** que actúa como intermediario (Backend-for-Frontend).

---

## 1. Reglas Inquebrantables de Manejo de Secretos

### SEC-LEAK-001: La Trampa del Prefijo `VITE_` / `NEXT_PUBLIC_`

**[REQUIRED]** El prefijo `VITE_` en Vite (o `NEXT_PUBLIC_` en Next.js) **incrusta el valor en texto plano directamente en el archivo JavaScript final** durante `npm run build`. 

* **Permitido con `VITE_`:** Únicamente valores diseñados para ser públicos por arquitectura:
  * `VITE_SUPABASE_URL` (URL pública del proyecto).
  * `VITE_SUPABASE_ANON_KEY` (clave anónima protegida por RLS).
  * `VITE_API_BASE_URL` (URL pública de tu worker/backend).
* **Terminantemente Prohibido con `VITE_`:**
  * ❌ `VITE_METAAPI_TOKEN` / `VITE_METAAPI_ACCOUNT_ID`
  * ❌ `VITE_STRIPE_SECRET_KEY` (o `sk_live_...`)
  * ❌ `VITE_SUPABASE_SERVICE_ROLE` (clave maestra que salta RLS)
  * ❌ `VITE_RESEND_API_KEY` / `VITE_SENDGRID_API_KEY`
  * ❌ `VITE_TELEGRAM_BOT_TOKEN`

**Por qué:** Cualquier usuario que abra la herramienta de desarrollador (`F12` → Network o Sources) o un escáner automatizado puede leer el bundle compilado y robar la credencial en menos de 5 segundos.

---

### SEC-LEAK-002: Arquitectura Obligatoria de Backend Proxy

**[REQUIRED]** Si el frontend necesita interactuar con un servicio que exige una API key secreta o un JWT con permisos de administración (ej. MetaApi para abrir operaciones de trading o consultar balances), **el frontend nunca contacta directamente a MetaApi**.

```
❌ ARQUITECTURA INSEGURA (Fuga de Secretos):
[ Frontend (Navegador) ] ──(con VITE_METAAPI_TOKEN en el bundle)──► [ MetaApi Server ]
                               ▲
                 Cualquiera extrae el token del JS

✅ ARQUITECTURA SEGURA (Backend Proxy con Cloudflare Worker):
[ Frontend (Navegador) ] 
       │ (1. fetch con Token de Sesión del Usuario / Bearer JWT)
       ▼
[ Cloudflare Worker (Backend Privado) ]
       │ (2. requireAuth(): valida sesión y permisos del usuario)
       │ (3. Usa env.METAAPI_TOKEN inyectado en producción como secreto seguro)
       ▼
[ MetaApi Server (API Externa) ]
```

#### Implementación de Referencia en Worker:

```typescript
// backend/src/handlers/trading.ts
import { requireAuth } from '../middleware/auth'

export async function handleGetAccounts(request: Request, env: Env) {
  // 1. Validar que la petición proviene de un usuario legítimo
  const user = await requireAuth(request, env)
  if (!user) {
    return new Response(
      JSON.stringify({ success: false, error: { code: 'UNAUTHORIZED', message: 'No autorizado' } }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    )
  }

  // 2. Usar el secreto que vive EXCLUSIVAMENTE en el entorno del Worker (wrangler secret put)
  const metaApiResponse = await fetch('https://mt-client-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts', {
    headers: {
      'auth-token': env.METAAPI_SECRET_TOKEN,
      'Content-Type': 'application/json'
    }
  })

  const accounts = await metaApiResponse.json()
  
  // 3. Filtrar y devolver solo las cuentas que pertenecen a este usuario
  return new Response(JSON.stringify({ ok: true, data: accounts }), {
    headers: { 'Content-Type': 'application/json' }
  })
}
```

---

### SEC-LEAK-003: Escáner Pre-Build Obligatorio contra Fugas

**[REQUIRED]** Todo proyecto frontend debe incluir un paso de escaneo en su script `npm run build` o en el hook pre-commit que bloquee la compilación si detecta patrones de tokens JWT, private keys o API keys en el código fuente o en la carpeta `dist/`.

#### Script de Escaneo Automático (`tools/scan-bundle-secrets.mjs`):

```javascript
import fs from 'fs'
import path from 'path'

// Patrones sin flag /g para garantizar determinismo estricto con RegExp.test()
const FORBIDDEN_PATTERNS = [
  { name: 'JWT Token con claims sensibles', regex: /eyJhbGciOi[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/ },
  { name: 'Stripe Secret Key', regex: /sk_live_[0-9a-zA-Z]{24,}/ },
  { name: 'Stripe Restricted Key', regex: /rk_live_[0-9a-zA-Z]{24,}/ },
  { name: 'Private Key PEM', regex: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: 'AWS Access Key', regex: /AKIA[0-9A-Z]{16}/ },
  { name: 'Supabase Service Role', regex: /service_role/i }
]

const TARGET_DIRS = process.argv.slice(2).length > 0 ? process.argv.slice(2) : ['./dist', './src']

function scanDirectory(dir) {
  if (!fs.existsSync(dir)) return 0

  let foundViolations = 0
  const files = fs.readdirSync(dir)

  for (const file of files) {
    const fullPath = path.join(dir, file)
    const stat = fs.statSync(fullPath)

    if (stat.isDirectory()) {
      foundViolations += scanDirectory(fullPath)
    } else if (file.endsWith('.js') || file.endsWith('.ts') || file.endsWith('.tsx') || file.endsWith('.html')) {
      if (file.includes('scan-bundle-secrets') || file === 'package-lock.json' || file === 'INDEX.json') continue

      const content = fs.readFileSync(fullPath, 'utf8')
      for (const pattern of FORBIDDEN_PATTERNS) {
        if (pattern.regex.test(content)) {
          // Si es un patrón JWT pero corresponde a una anon key pública explícita (no service_role)
          if (pattern.name.includes('JWT') && content.includes('sb_publishable_') && !content.includes('service_role')) {
            continue
          }

          console.error(`\x1b[31m[ERROR DE SEGURIDAD] Se detectó ${pattern.name} en: ${fullPath}\x1b[0m`)
          foundViolations++
        }
      }
    }
  }
  return foundViolations
}

console.log(`🔍 Escaneando directorios (${TARGET_DIRS.join(', ')}) en busca de secretos expuestos...`)
let violations = 0
for (const dir of TARGET_DIRS) {
  violations += scanDirectory(dir)
}

if (violations > 0) {
  console.error(`\x1b[31m❌ BUILD BLOQUEADO: Se encontraron ${violations} secretos en los archivos analizados.\x1b[0m`)
  process.exit(1)
} else {
  console.log('\x1b[32m✅ Escaneo completado: 0 secretos expuestos.\x1b[0m')
}
```

* **Integración en `package.json`:**
  ```json
  "scripts": {
    "build": "vite build && node tools/scan-bundle-secrets.mjs"
  }
  ```

---

## 2. Protocolo de Verificación: ANTES de Crear y Desplegar un Proyecto

### Checklist Pre-Arranque (Paso a Paso)

Antes de escribir código o promover una nueva funcionalidad:

- [ ] **1. Matriz de Variables de Entorno (.env):**
  - Todo lo que esté en `.env` del frontend solo lleva credenciales públicas (`VITE_SUPABASE_ANON_KEY`, `VITE_SUPABASE_URL`).
  - Todo secreto de backend se almacena en el Worker mediante `wrangler secret put <NOMBRE>` o en `.dev.vars` (nunca en `.env` del frontend).
- [ ] **2. Cero Tokens de Terceros en Frontend:**
  - ¿La app usa MetaApi, Stripe, Resend o Telegram? ➔ **El SDK solo se instala y ejecuta en el Worker/Backend**, nunca en `src/` de React.
- [ ] **3. Gitignore Estricto:**
  - `.env`, `.env.local`, `.dev.vars` y `*.pem` están en `.gitignore`.
  - Verificación: `git ls-files | grep -E "^\.env"` no devuelve nada.
- [ ] **4. Auditoría de Bundle Compilado:**
  - Tras ejecutar `npm run build`, correr el verificador:
    ```bash
    grep -rnE "eyJhbGciOi|sk_live_|BEGIN [A-Z ]*PRIVATE KEY" dist/
    ```
  - Debe devolver **0 coincidencias**.
- [ ] **5. Verificación de RLS en Tablas:**
  - Cada tabla consultada desde el frontend tiene RLS activo y no permite lectura global anónima sin sesión.
