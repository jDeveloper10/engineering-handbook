---
title: "Estándar de Seguridad e Integridad"
category: 05_Security
doc_type: estandar
tags: [seguridad, owasp, auth, cifrado, cors]
summary: "Estándar base del dominio: reglas S-001 a S-014 organizadas en siete capas de defensa, desde validación de entrada, CORS, autenticación y autorización hasta rate limiting, cifrado y cabeceras de seguridad."
keywords: [seguridad, owasp, auth, cifrado, cors, integridad, base, dominio, s-001, s-014, organizadas, siete, defensa, validacion]
updated: 2026-07-29
status: current
---

# 🔒 SEGURIDAD A PROFUNDIDAD - LA GUÍA DEFINITIVA

Esto no es teoría. Son **reglas de hierro quirúrgicas** que blindan cada capa. Sin excusas. Sin atajos.

---

## 🎯 LAS 7 CAPAS DE SEGURIDAD

```
Capa 1: Validación de Inputs       → NADA entra sin ser validado
Capa 2: CORS                       → Solo orígenes explícitos
Capa 3: Autenticación              → Quién eres (JWT, OAuth, Passkeys)
Capa 4: Autorización               → Qué puedes hacer (RBAC, RLS, ABAC)
Capa 5: Rate Limiting              → Cuántas veces puedes hacerlo
Capa 6: Cifrado                    → Datos ilegibles para extraños
Capa 7: Headers de Seguridad        → Defensa en el navegador
```

---

# 🛡️ CAPA 1: VALIDACIÓN DE INPUTS (La más importante)

El **80% de los ataques** entran por inputs mal validados.

## Regla S-001: NUNCA confiar en el frontend

**[REQUIRED]** **Por qué:** el frontend corre en la máquina del atacante: se edita, se saltan sus validaciones y se puede llamar al endpoint directamente con `curl`. La validación del cliente existe para dar buen feedback al usuario, no para proteger nada. Cualquier regla que solo viva en el frontend equivale a no existir.

```typescript
// ❌ Frontend valida, backend confía (HORRIBLE)
// frontend
if (email.includes('@')) {
  await fetch('/api/users', { body: JSON.stringify({ email }) })
}

// backend (SIN VALIDAR)
const { email } = await request.json()
await db.query('INSERT INTO users (email) VALUES ($1)', [email])

// ✅ VALIDACIÓN EN BACKEND (Zod)
import { z } from 'zod'

const createUserSchema = z.object({
  email: z
    .string()
    .trim()
    .toLowerCase()
    .email('Email inválido')
    .max(254, 'Email muy largo')
    .refine(email => {
      // Validar dominio tenga MX record (existe realmente)
      const domain = email.split('@')[1]
      const bannedDomains = ['tempmail.com', '10minutemail.com']
      return !bannedDomains.includes(domain)
    }, 'Dominio desechable no permitido')
    .refine(email => {
      // No permitir emails con caracteres peligrosos
      return !/[<>'"]/.test(email)
    }, 'Email contiene caracteres no permitidos'),
    
  password: z
    .string()
    .min(12, 'Mínimo 12 caracteres')
    .max(128, 'Máximo 128 caracteres')
    .regex(/[A-Z]/, 'Debe tener mayúscula')
    .regex(/[a-z]/, 'Debe tener minúscula')
    .regex(/[0-9]/, 'Debe tener número')
    .regex(/[^A-Za-z0-9]/, 'Debe tener carácter especial')
    .refine(pwd => {
      // No permitir contraseñas comunes
      const commonPasswords = ['Password123!', 'Admin123!@#' ]
      return !commonPasswords.includes(pwd)
    }, 'Contraseña muy común'),
    
  age: z
    .number()
    .int('Debe ser entero')
    .min(18, 'Debe ser mayor de edad')
    .max(120, 'Edad no válida'),
    
  username: z
    .string()
    .trim()
    .min(3)
    .max(30)
    .regex(/^[a-zA-Z0-9_-]+$/, 'Solo letras, números, guiones')
    .refine(name => {
      const reservedWords = ['admin', 'root', 'system', 'null', 'undefined']
      return !reservedWords.includes(name.toLowerCase())
    }, 'Nombre reservado'),
    
  website: z
    .string()
    .url('URL inválida')
    .refine(url => {
      // Solo permitir http/https
      return url.startsWith('https://') || url.startsWith('http://')
    })
    .refine(url => {
      // Bloquear SSRF (Server-Side Request Forgery)
      const parsed = new URL(url)
      const blockedHosts = ['localhost', '127.0.0.1', '0.0.0.0', '169.254.169.254']
      return !blockedHosts.includes(parsed.hostname)
    }, 'URL bloqueada por seguridad')
    .optional(),
    
  phone: z
    .string()
    .regex(/^\+?[1-9]\d{1,14}$/, 'Teléfono inválido (E.164)')
    .optional()
    .nullable(),
    
  bio: z
    .string()
    .max(500)
    .refine(text => {
      // Detectar XSS
      return !/<script|javascript:|onerror=|onload=/i.test(text)
    }, 'Contenido no permitido')
    .optional()
})
```

---

## Regla S-002: Sanitización DESPUÉS de validación

**[REQUIRED]** **Por qué:** sanitizar antes de validar puede transformar una entrada inválida en una que pasa la validación — el atacante controla la transformación. Validar primero rechaza lo que no cumple la forma esperada; sanitizar después limpia lo que ya se aceptó. El orden inverso convierte el sanitizador en un bypass.

```typescript
// Librería: DOMPurify (frontend) + sanitize-html (backend)

import sanitizeHtml from 'sanitize-html'

function sanitizeUserInput(input: string): string {
  return sanitizeHtml(input, {
    allowedTags: [],           // CERO HTML permitido
    allowedAttributes: {},     // CERO atributos
    disallowedTagsMode: 'discard',
    // Strip todo, solo queda texto plano
  })
}

// Proceso completo:
// 1. Validar con Zod (tipo, longitud, formato)
// 2. Sanitizar (eliminar HTML, scripts)
// 3. Escapar (para prevenir SQL injection - parametrizado)
// 4. Guardar

async function createComment(data: unknown) {
  // Paso 1: Validar
  const validated = commentSchema.parse(data)
  
  // Paso 2: Sanitizar
  validated.body = sanitizeHtml(validated.body, {
    allowedTags: ['b', 'i', 'em', 'strong', 'a'],
    allowedAttributes: {
      'a': ['href']
    },
    allowedSchemes: ['https', 'http']
  })
  
  // Paso 3: SQL parametrizado (escapado automático)
  const result = await db.query(
    'INSERT INTO comments (user_id, body) VALUES ($1, $2)',
    [validated.userId, validated.body]  // ← PARAMETRIZADO
  )
  
  return result
}
```

---

## Regla S-003: Validación de archivos (MÁS ALLÁ de la extensión)

**[REQUIRED]** **Por qué:** la extensión y el `Content-Type` los envía el cliente: renombrar `shell.php` a `foto.jpg` cuesta un segundo. Solo el contenido real del archivo (magic bytes) dice qué es. Sin esa comprobación, un formulario de subida de imágenes es una vía de ejecución de código o de almacenamiento de malware con tu dominio dando confianza.

```typescript
// ❌ Validar solo extensión (INÚTIL)
if (file.name.endsWith('.jpg')) {
  // Un atacante renombra virus.exe a virus.jpg y pasa
}

// ✅ Validación por MAGIC BYTES (bytes mágicos del archivo)
const MAGIC_BYTES = {
  'image/jpeg': [0xFF, 0xD8, 0xFF],
  'image/png': [0x89, 0x50, 0x4E, 0x47],
  'image/gif': [0x47, 0x49, 0x46, 0x38],
  'application/pdf': [0x25, 0x50, 0x44, 0x46],
  'application/zip': [0x50, 0x4B, 0x03, 0x04]
}

async function validateFileByMagicBytes(file: File): Promise<boolean> {
  const buffer = await file.arrayBuffer()
  const bytes = new Uint8Array(buffer.slice(0, 4))
  
  for (const [mimeType, magicBytes] of Object.entries(MAGIC_BYTES)) {
    if (magicBytes.every((byte, index) => bytes[index] === byte)) {
      return true
    }
  }
  
  return false
}

// Validación completa de archivos
const fileUploadSchema = z.object({
  file: z.instanceof(File).refine(
    async (file) => {
      // 1. Tamaño máximo
      if (file.size > 5 * 1024 * 1024) return false // 5MB max
      
      // 2. Tipo MIME
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
      if (!allowedTypes.includes(file.type)) return false
      
      // 3. Magic bytes (verificación real)
      const isValid = await validateFileByMagicBytes(file)
      if (!isValid) return false
      
      // 4. Nombre de archivo seguro
      const safeName = /^[a-zA-Z0-9._-]+$/.test(file.name)
      if (!safeName) return false
      
      // 5. No path traversal
      if (file.name.includes('..') || file.name.includes('/')) return false
      
      return true
    },
    'Archivo no válido o no permitido'
  )
})
```

---

## Regla S-004: Protección contra SQL Injection PROFUNDA

**[REQUIRED]** **Por qué:** la parametrización cubre los valores, pero no los identificadores (nombres de columna, `ORDER BY`, `LIMIT` dinámico), y ahí es donde reaparece la inyección después de que el equipo cree haberla resuelto. Todo fragmento que no pueda ir parametrizado se valida contra una lista blanca cerrada, nunca se escapa a mano.

```typescript
// ❌ JAMÁS concatenar strings en queries
const query = `SELECT * FROM users WHERE email = '${email}'`
// email = ' OR '1'='1' -- 
// Resultado: SELECT * FROM users WHERE email = '' OR '1'='1' --'

// ❌ TAMPOCO template literals con variables
const query = `SELECT * FROM users WHERE id = ${userId}`
// userId = '1; DROP TABLE users; --'

// ✅ SIEMPRE parametrizado
const result = await db.query(
  'SELECT id, email, status, password_hash FROM users WHERE email = $1 AND status = $2',
  [email, status]  // ← El driver escapa automáticamente
)

// ✅ Para queries dinámicas (order by, columnas)
// NUNCA permitir strings crudos, usar whitelist
const ALLOWED_COLUMNS = ['id', 'email', 'created_at', 'name']
const ALLOWED_DIRECTIONS = ['ASC', 'DESC']

function buildOrderClause(column: string, direction: string): string {
  if (!ALLOWED_COLUMNS.includes(column)) {
    throw new Error(`Columna no permitida: ${column}`)
  }
  if (!ALLOWED_DIRECTIONS.includes(direction.toUpperCase())) {
    throw new Error(`Dirección no permitida: ${direction}`)
  }
  return `ORDER BY ${column} ${direction.toUpperCase()}`
}

// Uso seguro:
const orderClause = buildOrderClause('created_at', 'DESC')
const result = await db.query(`SELECT id, email, created_at FROM users ${orderClause} LIMIT $1`, [limit])
```

---

# 🌐 CAPA 2: CORS (Cross-Origin Resource Sharing)

## Regla S-005: CORS EXPLÍCITO, NUNCA WILDCARD

**[REQUIRED]** **Por qué:** con `Access-Control-Allow-Origin: *` cualquier web puede leer las respuestas de tu API desde el navegador de tu usuario. Y el wildcard es incompatible con credenciales, así que quien lo pone suele acabar reflejando el `Origin` recibido — que es exactamente el mismo agujero con más pasos. La lista de orígenes se declara en el código.

```typescript
// ❌ ESTO ES UN CRIMEN DE GUERRA
app.use(cors())  // Permite TODO origen
app.use(cors({ origin: '*' }))  // LO MISMO

// ❌ TAMPOCO reflect origin (peligroso)
app.use(cors({ origin: true }))  // Refleja el origin del request

// ✅ CORS QUIRÚRGICO
const ALLOWED_ORIGINS = {
  production: ['https://omnisuite.com', 'https://app.omnisuite.com'],
  staging: ['https://staging.omnisuite.com'],
  development: ['http://localhost:3000', 'http://localhost:5173']
}

function getCorsConfig(env: string) {
  const origins = ALLOWED_ORIGINS[env] || []
  
  return {
    origin: (origin: string, callback: Function) => {
      // Bloquear requests sin origin (Postman, curl)
      if (!origin && env === 'production') {
        return callback(new Error('Origin required'), false)
      }
      
      if (origins.includes(origin)) {
        callback(null, true)
      } else {
        console.warn(`Origen bloqueado por CORS: ${origin}`)
        callback(new Error('Not allowed by CORS'), false)
      }
    },
    methods: ['GET', 'POST', 'PATCH', 'DELETE'],  // SOLO los que usas
    allowedHeaders: [
      'Content-Type',
      'Authorization',
      'X-Trace-Id',
      'X-Client-Version'
    ],
    exposedHeaders: [
      'X-RateLimit-Limit',
      'X-RateLimit-Remaining',
      'X-RateLimit-Reset'
    ],
    maxAge: 86400,  // Cache preflight por 24 horas
    credentials: true
  }
}

// Configuración en Cloudflare Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get('Origin')
    const allowedOrigins = env.ALLOWED_ORIGINS.split(',')
    
    // Preflight (OPTIONS)
    if (request.method === 'OPTIONS') {
      if (!origin || !allowedOrigins.includes(origin)) {
        return new Response('Forbidden', { status: 403 })
      }
      
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': origin,
          'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          'Access-Control-Max-Age': '86400'
        }
      })
    }
    
    // Request normal
    const response = await handleRequest(request, env)
    
    // Agregar headers CORS SOLO si origen permitido
    if (origin && allowedOrigins.includes(origin)) {
      response.headers.set('Access-Control-Allow-Origin', origin)
      response.headers.set('Access-Control-Allow-Credentials', 'true')
    }
    
    return response
  }
}
```

---

## Regla S-006: CORS por endpoint sensible

**[REQUIRED]** **Por qué:** una política CORS global es tan permisiva como su endpoint más laxo. Los endpoints que mueven dinero, cambian credenciales o exponen datos de otros usuarios necesitan su propia lista de orígenes, porque el coste de un error ahí no es el mismo que en un endpoint de lectura pública.

```typescript
// Endpoints públicos (sin auth) vs privados (con auth)

const CORS_PUBLIC = {
  origin: ['https://omnisuite.com'],
  methods: ['GET'],  // SOLO lectura
  maxAge: 3600
}

const CORS_PRIVATE = {
  origin: ['https://app.omnisuite.com'],
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  credentials: true,
  maxAge: 86400
}

// Aplicar según endpoint
export async function handlePublicProposal(request: Request) {
  // Cliente ve propuesta pública → CORS restrictivo
  return withCORS(request, CORS_PUBLIC, async () => {
    // lógica
  })
}

export async function handleDashboard(request: Request) {
  // Usuario autenticado → CORS completo
  return withCORS(request, CORS_PRIVATE, async () => {
    // lógica
  })
}
```

---

# 🔐 CAPA 3: AUTENTICACIÓN

## Regla S-007: JWT con rotación de tokens

**[REQUIRED]** **Por qué:** un JWT no se puede revocar: una vez emitido es válido hasta que expira, por eso el access token dura minutos y no días. El refresh token sí es revocable, y rotarlo en cada uso permite detectar el robo — si llega dos veces el mismo refresh token, alguien lo copió y se invalida toda la familia de sesión.

```typescript
// Tokens de acceso: vida corta (15 min)
// Refresh tokens: vida larga (7 días), rotación obligatoria

interface TokenPair {
  accessToken: string   // 15 minutos
  refreshToken: string  // 7 días
}

// Generar tokens
async function generateTokens(userId: string): Promise<TokenPair> {
  const accessToken = await signAccessToken({
    sub: userId,
    role: 'user',
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 900  // 15 minutos
  })
  
  const refreshToken = crypto.randomUUID()
  
  // Guardar refresh token en DB (hasheado)
  const hash = await hashToken(refreshToken)
  await db.query(
    'INSERT INTO refresh_tokens (user_id, token_hash, expires_at, family) VALUES ($1, $2, $3, $4)',
    [userId, hash, new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), crypto.randomUUID()]
  )
  
  return { accessToken, refreshToken }
}

// Rotación: refresh token viejo se invalida al usarlo
async function rotateRefreshToken(oldToken: string): Promise<TokenPair> {
  const hash = await hashToken(oldToken)
  
  // Buscar token
  const { rows } = await db.query(
    'SELECT id, user_id, expires_at, used FROM refresh_tokens WHERE token_hash = $1 AND used = false',
    [hash]
  )
  
  if (rows.length === 0) {
    // Token ya fue usado = POSIBLE ROBO
    // Invalidar TODA la familia de tokens
    await db.query(
      'UPDATE refresh_tokens SET used = true, revoked = true WHERE family = $1',
      [rows[0]?.family]
    )
    throw new Error('Token reutilizado - posible robo')
  }
  
  // Marcar como usado
  await db.query(
    'UPDATE refresh_tokens SET used = true WHERE token_hash = $1',
    [hash]
  )
  
  // Generar nuevo par
  return generateTokens(rows[0].user_id)
}
```

---

## Regla S-008: Passkeys (WebAuthn) - Sin contraseñas

**[RECOMMENDED]** **Por qué:** las passkeys eliminan de raíz el phishing y el credential stuffing porque la clave privada no sale del dispositivo y está ligada al dominio. Es el destino correcto, pero exigirlas hoy dejaría fuera a usuarios con dispositivos antiguos o entornos corporativos restringidos. Cuando no se adoptan, `S-013` (Argon2id) y MFA dejan de ser opcionales.

```typescript
// Registro de passkey (huella, Face ID, PIN)
async function registerPasskey(userId: string) {
  const challenge = crypto.randomBytes(32)
  
  // Guardar challenge temporal
  await redis.set(`webauthn:challenge:${userId}`, challenge.toString('base64'), 'EX', 300)
  
  const credential = await navigator.credentials.create({
    publicKey: {
      rp: { name: 'OmniSuite', id: 'omnisuite.com' },
      user: {
        id: new TextEncoder().encode(userId),
        name: 'user@omnisuite.com',
        displayName: 'Usuario'
      },
      challenge,
      pubKeyCredParams: [
        { type: 'public-key', alg: -7 },  // ES256
        { type: 'public-key', alg: -257 } // RS256
      ],
      authenticatorSelection: {
        authenticatorAttachment: 'platform',  // Solo biometría del dispositivo
        userVerification: 'required',         // Obligatorio verificar usuario
        residentKey: 'required'               // Almacenar en dispositivo
      },
      timeout: 60000,
      attestation: 'direct'
    }
  })
  
  // Verificar y guardar clave pública en DB
  await saveCredential(userId, credential)
}

// Login sin contraseña
async function loginWithPasskey() {
  const challenge = crypto.randomBytes(32)
  
  const assertion = await navigator.credentials.get({
    publicKey: {
      challenge,
      rpId: 'omnisuite.com',
      userVerification: 'required',
      timeout: 60000
    }
  })
  
  // Verificar firma con clave pública almacenada
  const isValid = await verifyAssertion(assertion)
  if (isValid) {
    // Generar JWT
    return generateTokens(userId)
  }
}
```

---

# 👮 CAPA 4: AUTORIZACIÓN

## Regla S-009: RBAC + RLS (Defensa en profundidad)

**[REQUIRED]** **Por qué:** comprobar permisos solo en la aplicación deja la base de datos abierta a cualquier ruta que se salte esa capa: un script de mantenimiento, un endpoint nuevo que olvidó el middleware, o una credencial filtrada. Dos capas independientes significan que un fallo en una no es una brecha, sino un incidente contenido.

```typescript
// Roles definidos como enum
enum Role {
  SUPER_ADMIN = 'super_admin',
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user',
  VIEWER = 'viewer'
}

// Matriz de permisos
const PERMISSIONS = {
  [Role.SUPER_ADMIN]: ['*'],
  [Role.ADMIN]: [
    'users:read', 'users:create', 'users:update',
    'proposals:read', 'proposals:create', 'proposals:update', 'proposals:delete',
    'billing:read', 'billing:manage'
  ],
  [Role.MANAGER]: [
    'users:read',
    'proposals:read', 'proposals:create', 'proposals:update',
    'billing:read'
  ],
  [Role.USER]: [
    'proposals:read', 'proposals:create', 'proposals:update',
    'profile:read', 'profile:update'
  ],
  [Role.VIEWER]: [
    'proposals:read'
  ]
}

// Middleware de autorización
function requirePermission(...requiredPermissions: string[]) {
  return async (request: Request, env: Env) => {
    const user = await authenticate(request, env)
    if (!user) return errorResponse('Unauthorized', 401)
    
    const userPermissions = PERMISSIONS[user.role] || []
    
    // Super admin tiene acceso total
    if (userPermissions.includes('*')) return { user }
    
    // Verificar cada permiso requerido
    const hasPermission = requiredPermissions.every(
      perm => userPermissions.includes(perm)
    )
    
    if (!hasPermission) {
      console.warn(`Usuario ${user.id} (${user.role}) intentó acceder a: ${requiredPermissions.join(', ')}`)
      return errorResponse('Forbidden - Insufficient permissions', 403)
    }
    
    return { user }
  }
}

// Uso:
app.get('/api/admin/users', requirePermission('users:read'), handleGetUsers)
app.post('/api/admin/billing', requirePermission('billing:manage'), handleBilling)
```

---

## Regla S-010: RLS en PostgreSQL (Última línea de defensa)

**[REQUIRED]** **Por qué:** RLS es la única comprobación que un atacante no puede saltarse cambiando de ruta de acceso, porque vive en el motor de datos y no en el código que lo consulta. En multi-tenant es lo que separa un bug de paginación de una fuga de datos entre clientes. Una tabla sin RLS activo es una tabla pública para cualquiera con la clave anónima.

```sql
-- RLS multi-tenant: Cada usuario ve SOLO sus datos

-- 1. Habilitar RLS
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;

-- 2. Política base: usuario ve sus propias propuestas
CREATE POLICY "user_own_proposals" ON proposals
  FOR ALL
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- 3. Política para admins: ven todas las propuestas de su tenant
CREATE POLICY "admin_tenant_proposals" ON proposals
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
        AND users.role IN ('admin', 'super_admin')
        AND users.tenant_id = proposals.tenant_id
    )
  );

-- 4. Política para viewers: solo lectura
CREATE POLICY "viewer_read_only" ON proposals
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
        AND users.role = 'viewer'
        AND users.tenant_id = proposals.tenant_id
    )
  );

-- 5. Política pública: cliente ve su propuesta por token
CREATE POLICY "public_by_token" ON proposals
  FOR SELECT
  TO anon
  USING (
    public_token = current_setting('request.headers')::json->>'x-public-token'
    AND expires_at > now()
  );
```

---

# ⏱️ CAPA 5: RATE LIMITING

## Regla S-011: Rate Limiting en 3 niveles

**[REQUIRED]** **Por qué:** un solo nivel siempre se puede rodear: por IP no frena a un atacante con proxies rotatorios; por usuario no frena el registro masivo de cuentas; por endpoint no frena a un atacante lento y distribuido. Los tres niveles cubren los huecos de los otros dos, y el coste de no tenerlos se paga en factura de infraestructura además de en seguridad.

```typescript
// Nivel 1: IP (sin auth)
// Nivel 2: Usuario (con auth)  
// Nivel 3: Endpoint (crítico)

class RateLimiter {
  private store: DurableObject
  
  async checkLimit(key: string, config: RateLimitConfig): Promise<RateLimitResult> {
    const now = Date.now()
    const window = config.windowMs || 60000
    
    // Obtener timestamps anteriores
    const timestamps = await this.store.get(key) || []
    const recent = timestamps.filter((t: number) => now - t < window)
    
    if (recent.length >= config.max) {
      const resetTime = recent[0] + window
      return { allowed: false, remaining: 0, reset: resetTime }
    }
    
    recent.push(now)
    await this.store.put(key, recent)
    
    return {
      allowed: true,
      remaining: config.max - recent.length,
      reset: now + window
    }
  }
}

// Configuraciones por nivel
const RATE_LIMITS = {
  // Nivel 1: IP (previene abuso básico)
  ip: {
    public: { max: 10, windowMs: 60000 },    // 10 req/min
    auth: { max: 30, windowMs: 60000 }       // 30 req/min
  },
  
  // Nivel 2: Usuario (previene abuso autenticado)
  user: {
    default: { max: 100, windowMs: 60000 },  // 100 req/min
    premium: { max: 300, windowMs: 60000 }   // 300 req/min
  },
  
  // Nivel 3: Endpoint (previene ataques dirigidos)
  endpoint: {
    login: { max: 5, windowMs: 300000 },     // 5 intentos en 5 min
    register: { max: 3, windowMs: 3600000 },  // 3 registros por hora
    fileUpload: { max: 10, windowMs: 60000 }, // 10 uploads/min
    passwordReset: { max: 2, windowMs: 3600000 } // 2 resets por hora
  }
}

// Middleware de rate limiting combinado
async function rateLimitMiddleware(request: Request, env: Env) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown'
  const user = await getAuthenticatedUser(request)
  const endpoint = new URL(request.url).pathname
  
  // 1. Rate limit por IP
  const ipKey = `ratelimit:ip:${ip}`
  const ipLimit = user ? RATE_LIMITS.ip.auth : RATE_LIMITS.ip.public
  const ipResult = await checkLimit(ipKey, ipLimit)
  if (!ipResult.allowed) return rateLimitResponse(ipResult)
  
  // 2. Rate limit por usuario (si está autenticado)
  if (user) {
    const userKey = `ratelimit:user:${user.id}`
    const userLimit = user.plan === 'premium' ? RATE_LIMITS.user.premium : RATE_LIMITS.user.default
    const userResult = await checkLimit(userKey, userLimit)
    if (!userResult.allowed) return rateLimitResponse(userResult)
  }
  
  // 3. Rate limit por endpoint crítico
  const endpointConfig = RATE_LIMITS.endpoint[endpoint]
  if (endpointConfig) {
    const endpointKey = `ratelimit:endpoint:${endpoint}:${ip}`
    const endpointResult = await checkLimit(endpointKey, endpointConfig)
    if (!endpointResult.allowed) return rateLimitResponse(endpointResult)
  }
  
  return null // Permitido
}
```

---

# 🔐 CAPA 6: CIFRADO

## Regla S-012: Cifrado en reposo (datos sensibles)

**[REQUIRED]** **Por qué:** el cifrado en reposo es lo que decide si una copia de la base de datos filtrada es un incidente reportable o un archivo inútil. Aplica a lo que causaría daño real al usuario si se publicara — tokens de terceros, documentos de identidad, datos de salud —, no a toda la tabla, porque cifrar lo que se filtra por consultas impide indexarlo.

```sql
-- Habilitar pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Datos que SIEMPRE van cifrados:
-- - API keys de terceros
-- - Tokens de acceso
-- - Datos de pago (PCI)
-- - Datos médicos (HIPAA)
-- - PII sensible (documentos, direcciones)

CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  provider TEXT NOT NULL,
  
  -- Cifrado con clave maestra de app
  api_key_encrypted BYTEA NOT NULL,
  
  -- Hash para búsqueda sin descifrar
  api_key_prefix TEXT NOT NULL,  -- Últimos 4 caracteres
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Insertar datos cifrados
INSERT INTO integrations (user_id, provider, api_key_encrypted, api_key_prefix)
VALUES (
  'user_123',
  'stripe',
  pgp_sym_encrypt(
    'sk_live_abc123xyz',
    current_setting('app.encryption_key')
  ),
  'xyz'
);

-- Buscar sin descifrar
SELECT id, user_id, provider, access_token_encrypted FROM integrations
WHERE user_id = 'user_123'
  AND provider = 'stripe';

-- Descifrar solo cuando es necesario
SELECT 
  id,
  provider,
  pgp_sym_decrypt(api_key_encrypted, current_setting('app.encryption_key')) AS api_key,
  api_key_prefix
FROM integrations
WHERE user_id = 'user_123';

-- NUNCA mostrar api_key en logs
-- NUNCA devolver api_key en endpoints públicos
-- NUNCA guardar api_key en texto plano
```

---

## Regla S-013: Hashing de contraseñas (Argon2id)

**[REQUIRED]** **Por qué:** una contraseña nunca se guarda de forma reversible, y no todos los hash sirven: MD5 y SHA se calculan a miles de millones por segundo en GPU. Argon2id está diseñado para ser costoso en memoria además de en CPU, que es lo que anula la ventaja del hardware especializado. Es la diferencia entre una filtración molesta y una catastrófica.

```typescript
import { hash, verify } from 'argon2'

// Argon2id: ganador del Password Hashing Competition
// Resistente a GPU, ASIC, side-channel, time-memory tradeoff

const HASHING_OPTIONS = {
  type: argon2id,
  memoryCost: 65536,    // 64 MB
  timeCost: 3,           // 3 iteraciones
  parallelism: 4,        // 4 hilos
  saltLength: 16,
  hashLength: 32
}

async function hashPassword(password: string): Promise<string> {
  return hash(password, HASHING_OPTIONS)
}

async function verifyPassword(hash: string, password: string): Promise<boolean> {
  return verify(hash, password)
}

// NUNCA usar:
// - MD5 (roto desde 2004)
// - SHA1 (roto desde 2017)
// - SHA256 simple (muy rápido = vulnerable a fuerza bruta)
// - bcrypt con cost < 12
```

---

# 🛡️ CAPA 7: HEADERS DE SEGURIDAD

## Regla S-014: Headers de seguridad OBLIGATORIOS

**[REQUIRED]** **Por qué:** estas cabeceras convierten al navegador en un aliado que aplica restricciones que tu código no puede imponer por sí solo: CSP limita el daño de un XSS que se te escapó, `X-Frame-Options` impide el clickjacking y HSTS elimina la ventana de degradación a HTTP. Son la capa más barata del handbook: se configuran una vez y protegen siempre.

```typescript
const SECURITY_HEADERS = {
  // Prevenir XSS
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' https://js.stripe.com",
    // ⚠️ EXCEPCIÓN DOCUMENTADA a SEC-001 — ver SECURITY_ADVANCED.md §1 para la justificación
    // completa. `'unsafe-inline'` SOLO en style-src, JAMÁS en script-src.
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' https://cdn.omnisuite.com data: blob:",
    "connect-src 'self' https://api.omnisuite.com wss://ws.omnisuite.com",
    "frame-src https://js.stripe.com",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; '),
  
  // Prevenir clickjacking
  'X-Frame-Options': 'DENY',
  
  // Prevenir MIME sniffing
  'X-Content-Type-Options': 'nosniff',
  
  // Prevenir XSS reflejado (navegadores antiguos)
  'X-XSS-Protection': '0',  // Obsoleto, CSP lo reemplaza
  
  // Forzar HTTPS por 2 años
  'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
  
  // Controlar qué información del referrer se envía
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Permisos del navegador
  'Permissions-Policy': [
    'camera=()',
    'microphone=()',
    'geolocation=(self)',
    'payment=()'
  ].join(', '),
  
  // Remover fingerprinting del servidor
  'Server': '',  // No revelar tecnología
  'X-Powered-By': ''  // No revelar framework
}

// Aplicar headers en cada respuesta
function addSecurityHeaders(response: Response): Response {
  const headers = new Headers(response.headers)
  
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    headers.set(key, value)
  }
  
  // Headers específicos para APIs
  if (response.headers.get('Content-Type')?.includes('application/json')) {
    headers.set('Cache-Control', 'no-store, no-cache, must-revalidate')
    headers.set('Pragma', 'no-cache')
  }
  
  return new Response(response.body, {
    status: response.status,
    headers
  })
}
```

---

# 🧪 CHECKLIST FINAL DE SEGURIDAD

```markdown
## AUDITORÍA DE SEGURIDAD PRE-DEPLOY

### Inputs (S-001 a S-004)
- [ ] ¿Todo input validado con Zod en backend?
- [ ] ¿Validación de tipos, longitud, formato, rango?
- [ ] ¿Sanitización HTML en campos de texto?
- [ ] ¿Queries parametrizadas (nunca concatenadas)?
- [ ] ¿Archivos validados por magic bytes, no extensión?
- [ ] ¿Path traversal prevenido en nombres de archivo?

### CORS (S-005 a S-006)
- [ ] ¿Orígenes explícitos, nunca wildcard?
- [ ] ¿Métodos HTTP restringidos (solo los necesarios)?
- [ ] ¿Headers expuestos controlados?
- [ ] ¿Preflight cacheado?
- [ ] ¿CORS diferente para endpoints públicos/privados?

### Autenticación (S-007 a S-008)
- [ ] ¿Access token ≤ 15 minutos?
- [ ] ¿Refresh token con rotación?
- [ ] ¿Detección de reuso de refresh token?
- [ ] ¿Passkeys/WebAuthn implementado?
- [ ] ¿Rate limiting en login (5 intentos/5min)?

### Autorización (S-009 a S-010)
- [ ] ¿RBAC implementado con matriz de permisos?
- [ ] ¿RLS en PostgreSQL para multi-tenancy?
- [ ] ¿Defensa en profundidad (app + DB)?
- [ ] ¿Super admin auditado?

### Rate Limiting (S-011)
- [ ] ¿Rate limit por IP?
- [ ] ¿Rate limit por usuario?
- [ ] ¿Rate limit por endpoint crítico?
- [ ] ¿429 con headers de límite?
- [ ] ¿Rate limit en endpoints públicos?

### Cifrado (S-012 a S-013)
- [ ] ¿Datos sensibles cifrados con pgcrypto?
- [ ] ¿Contraseñas hasheadas con Argon2id?
- [ ] ¿Clave maestra en variable de entorno?
- [ ] ¿Nunca mostrar datos cifrados en logs?

### Headers (S-014)
- [ ] ¿Content-Security-Policy configurado?
- [ ] ¿X-Frame-Options: DENY?
- [ ] ¿X-Content-Type-Options: nosniff?
- [ ] ¿Strict-Transport-Security?
- [ ] ¿Server/Powered-By removidos?

### Adicional
- [ ] ¿CSRF protection (SameSite cookies + tokens)?
- [ ] ¿Dependencias actualizadas (npm audit)?
- [ ] ¿Secrets en variables de entorno (nunca en código)?
- [ ] ¿Logs sin datos sensibles?
```
