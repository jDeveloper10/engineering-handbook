---
title: "Autenticación MFA: TOTP, Passkeys y Magic Links"
category: 05_Security
tags: [mfa, totp, webauthn, passkeys, magic-link, auth, supabase]
summary: "Autenticación de segundo factor completa: TOTP con aplicaciones de autenticación, passkeys WebAuthn biométricas, y magic links de login e invitaciones a equipo con sus TTL y reglas de un solo uso."
keywords: [mfa, totp, webauthn, passkeys, magic-link, auth, supabase, autenticacion, magic, links, segundo, factor, completa, aplicaciones]
updated: 2026-07-29
status: current
---

# 🔐 AUTENTICACIÓN AVANZADA: MFA, PASSKEYS Y MAGIC LINKS

## 🎯 ¿Por qué esto es crítico?
Una contraseña sola no es suficiente en 2024. El 81% de los brechas de datos involucran contraseñas comprometidas. Este estándar cubre las 3 formas de autenticación fuerte que el stack Supabase soporta: **TOTP** (Google Authenticator), **Passkeys** (WebAuthn/biométrico) y **Magic Links** (email sin contraseña).

> **REGLA INQUEBRANTABLE:** Todo SaaS con datos de usuarios DEBE ofrecer al menos TOTP como segundo factor. Para invitaciones a equipos, el Magic Link es OBLIGATORIO — PROHIBIDO enviar contraseñas temporales por email.
>
> **`AUTH-003` vs `AUTH-004` — no son la misma regla aunque ambas se llamen "magic link".** `AUTH-003` (15 min, un solo uso) rige el login: reemplaza una contraseña, así que su ventana de exposición debe ser mínima. `AUTH-004` (48h default, un solo uso, revocable) rige las invitaciones a equipo: es una oferta de membresía, no una sesión, y alguien puede tardar en revisar su email. Ver §3.0 para la tabla de decisión completa. Un magic link de invitación con TTL de 15 minutos genera invitaciones vencidas y reenvíos constantes — es tan incorrecto como un magic link de login con TTL de 48h, que deja una ventana de secuestro de sesión abierta un día y medio.

---

## 🔢 PARTE 1: TOTP (Two-Factor Authentication con Google Authenticator)

Supabase Auth tiene soporte nativo para MFA TOTP desde 2023. No se necesita ninguna librería extra.

### 1.1 Habilitar MFA en el proyecto Supabase

```sql
-- Ejecutar en el SQL Editor de Supabase
-- (No hay SQL directo: se habilita en el Dashboard > Auth > Settings > MFA)
-- Pero sí necesitamos guardar el estado MFA del usuario en la tabla de perfiles:
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE;
```

### 1.2 Flujo de Enrolamiento (Frontend)

```tsx
import { supabase } from '@/lib/supabase'
import { useState } from 'react'
import QRCode from 'react-qr-code'

export function MFASetup({ onComplete }: { onComplete: () => void }) {
  const [qrUri, setQrUri]     = useState<string | null>(null)
  const [factorId, setFactorId] = useState<string | null>(null)
  const [code, setCode]       = useState('')
  const [error, setError]     = useState<string | null>(null)

  // PASO 1: Generar el código QR para escanear
  const startSetup = async () => {
    const { data, error } = await supabase.auth.mfa.enroll({
      factorType: 'totp',
      friendlyName: 'CollabScribe Authenticator'
    })

    if (error) { setError(error.message); return }

    setQrUri(data.totp.qr_code)     // URI otpauth:// para el QR
    setFactorId(data.id)            // ID del factor para verificar
  }

  // PASO 2: Verificar el código de 6 dígitos
  const verifyCode = async () => {
    if (!factorId) return

    const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
      factorId
    })
    if (challengeError) { setError(challengeError.message); return }

    const { error: verifyError } = await supabase.auth.mfa.verify({
      factorId,
      challengeId: challenge.id,
      code         // Código de 6 dígitos del Authenticator
    })

    if (verifyError) {
      setError('Código incorrecto. Inténtalo de nuevo.')
      return
    }

    // MFA activado exitosamente
    await supabase
      .from('profiles')
      .update({ mfa_enabled: true })
      .eq('id', (await supabase.auth.getUser()).data.user?.id)

    onComplete()
  }

  return (
    <div className="max-w-sm mx-auto space-y-6">
      <h2 className="text-xl font-bold">Activar autenticación de dos factores</h2>

      {!qrUri ? (
        <button onClick={startSetup} className="w-full bg-primary text-primary-foreground py-2 rounded-lg">
          Comenzar configuración
        </button>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-foreground/60">
            1. Escanea este código QR con Google Authenticator o Authy.
          </p>
          <div className="flex justify-center p-4 bg-white rounded-lg">
            <QRCode value={qrUri} size={200} />
          </div>
          <p className="text-sm text-foreground/60">
            2. Ingresa el código de 6 dígitos que aparece en la app.
          </p>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={code}
            onChange={e => setCode(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            className="w-full text-center text-2xl tracking-widest border rounded-lg p-3"
          />
          {error && <p className="text-danger text-sm">{error}</p>}
          <button
            onClick={verifyCode}
            disabled={code.length !== 6}
            className="w-full bg-primary text-primary-foreground py-2 rounded-lg disabled:opacity-50"
          >
            Verificar y activar
          </button>
        </div>
      )}
    </div>
  )
}
```

### 1.3 Verificar TOTP en el Login

```tsx
export function MFAChallenge({ onSuccess }: { onSuccess: () => void }) {
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)

  const verify = async () => {
    // Obtener el factor TOTP del usuario
    const { data: factors } = await supabase.auth.mfa.listFactors()
    const totpFactor = factors?.totp?.[0]
    if (!totpFactor) return

    const { data: challenge } = await supabase.auth.mfa.challenge({
      factorId: totpFactor.id
    })

    const { error } = await supabase.auth.mfa.verify({
      factorId:    totpFactor.id,
      challengeId: challenge!.id,
      code
    })

    if (error) { setError('Código incorrecto'); return }
    onSuccess()
  }

  return (
    <div className="max-w-sm mx-auto space-y-4">
      <h2 className="text-xl font-bold">Verificación en dos pasos</h2>
      <input
        type="text"
        inputMode="numeric"
        maxLength={6}
        value={code}
        onChange={e => setCode(e.target.value.replace(/\D/g, ''))}
        placeholder="Código de 6 dígitos"
        className="w-full text-center text-2xl tracking-widest border rounded-lg p-3"
        autoFocus
      />
      {error && <p className="text-danger text-sm">{error}</p>}
      <button onClick={verify} disabled={code.length !== 6} className="w-full bg-primary text-primary-foreground py-2 rounded-lg">
        Verificar
      </button>
    </div>
  )
}
```

---

## 🔑 PARTE 2: PASSKEYS (WebAuthn / Biométrico)

Supabase Auth soporta Passkeys como método de login sin contraseña desde Supabase v2.39+. Permite autenticación con Face ID, huella dactilar o llave de seguridad hardware (YubiKey).

### 2.1 Registro de Passkey

```tsx
export async function registerPasskey() {
  const { data, error } = await supabase.auth.signInWithPasskey({
    isRegistration: true   // Indica que se está registrando una nueva passkey
  })

  if (error) {
    if (error.message.includes('not supported')) {
      throw new Error('Tu dispositivo no soporta Passkeys.')
    }
    throw error
  }

  return data
}
```

### 2.2 Login con Passkey

```tsx
export async function loginWithPasskey() {
  const { data, error } = await supabase.auth.signInWithPasskey({
    isRegistration: false  // Login con passkey existente
  })

  if (error) throw error
  return data
}

// Componente de UI
export function PasskeyButton() {
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setLoading(true)
    try {
      await loginWithPasskey()
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'No se pudo iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  // Solo mostrar si el navegador soporta WebAuthn
  if (!window.PublicKeyCredential) return null

  return (
    <button
      onClick={handleLogin}
      disabled={loading}
      className="w-full flex items-center justify-center gap-2 border py-2 rounded-lg hover:bg-surface transition-colors"
    >
      🔑 {loading ? 'Verificando...' : 'Entrar con Passkey (Face ID / Huella)'}
    </button>
  )
}
```

---

## 📧 PARTE 3: MAGIC LINKS (Login) E INVITACIONES A EQUIPO

El Magic Link (login, `AUTH-003`) es un enlace único que autentica sin contraseña — vive 15 minutos porque reemplaza una sesión completa. La invitación a equipo (`AUTH-004`) también viaja por email pero **no es el mismo mecanismo**: es una oferta de membresía con su propia tabla, su propio TTL y la capacidad de revocarse antes de expirar. Confundir ambos (usar `supabase.auth.admin.inviteUserByEmail`, que hereda la config global de "Auth OTP Expiration" pensada para login) es el error más común — produce invitaciones que expiran a los 15 minutos como si fueran un login, o logins con TTL de días si alguien "arregla" el síntoma subiendo la config global.

### 3.0 Tabla de decisión

| | Login (`AUTH-003`) | Invitación a equipo (`AUTH-004`) |
|---|---|---|
| Nivel de regla | `[REQUIRED]` Nivel 1 | `[RECOMMENDED]` (TTL configurable por producto) |
| TTL | 15 min máx, fijo | 48h default, ajustable |
| Mecanismo | `supabase.auth.signInWithOtp()` — OTP nativo de Supabase Auth | Token propio de aplicación (`crypto.randomUUID()` + hash SHA-256), tabla `team_invitations` |
| Un solo uso | Sí | Sí |
| Revocable antes de expirar | No aplica (es la sesión misma) | Sí — un admin puede invalidarla desde la UI |
| Por qué la diferencia | Ventana de secuestro de sesión mínima | Nadie revisa su email en 15 min; forzarlo produce reenvíos constantes |

**[REQUIRED]** Nunca usar `supabase.auth.admin.inviteUserByEmail` para invitaciones a equipo — ese método crea la cuenta *y* autentica en el mismo paso con el OTP de login, mezclando ambas reglas. La invitación a equipo se resuelve en dos pasos independientes: (1) validar el token propio y la pertenencia del invitado, (2) si el invitado no tiene cuenta, recién ahí se dispara un login/registro normal (que si es passwordless, usa `AUTH-003` con su propia TTL de 15 min — dos links, dos reglas, cada uno con la suya).

### 3.1 Invitación a equipo — token propio (`AUTH-004`)

```sql
-- Migración: tabla propia, nunca el mecanismo de auth de Supabase
create table team_invitations (
  id           uuid        primary key default gen_random_uuid(),
  team_id      uuid        not null references teams(id) on delete cascade,
  email        text        not null,
  role         text        not null check (role in ('admin','editor','viewer')),
  invited_by   uuid        not null references auth.users(id) on delete restrict,
  token_hash   text        not null unique,   -- nunca se guarda el token en claro
  expires_at   timestamptz not null,          -- AUTH-004: now() + 48h (default, configurable)
  revoked_at   timestamptz,                    -- AUTH-004: revocable por admin antes de expirar
  accepted_at  timestamptz,                    -- NULL = pendiente; AUTH-004: un solo uso
  created_at   timestamptz not null default now()
);
create index idx_team_invitations_team_id on team_invitations(team_id);
create unique index uq_team_invitations_pending on team_invitations(team_id, email) where accepted_at is null and revoked_at is null;

alter table team_invitations enable row level security;
create policy "admins manage invitations" on team_invitations
  for all using (team_id in (
    select team_id from team_members where user_id = (select auth.uid()) and role in ('owner','admin')
  ));
```

```typescript
// Backend: Worker de invitación
// POST /api/teams/:id/invite

import { z } from 'zod'

const inviteSchema = z.object({
  email: z.string().email().trim().toLowerCase(),
  role:  z.enum(['admin', 'editor', 'viewer'])
})

const INVITE_TTL_HOURS = 48 // AUTH-004 [RECOMMENDED] — ajustable por producto, nunca sin expiración

export async function handleInvite(request: Request, env: Env, teamId: string) {
  const auth = await requireAuth(request, env)
  if (auth.error) return auth.error
  const { user, supabase } = auth

  const body = await request.json()
  const { email, role } = inviteSchema.parse(body)  // S-001: validar SIEMPRE

  // 1. Verificar que el invitador tiene permisos (admin o owner)
  const { data: member } = await supabase
    .from('team_members')
    .select('role')
    .eq('team_id', teamId)
    .eq('user_id', user.id)
    .single()

  if (!member || !['admin', 'owner'].includes(member.role)) {
    return fail('FORBIDDEN', 'Solo admins pueden invitar miembros', 403)
  }

  // 2. Token propio — NUNCA supabase.auth.admin.inviteUserByEmail (mezcla AUTH-003 con AUTH-004)
  const rawToken = crypto.randomUUID() + crypto.randomUUID()
  const tokenHash = await sha256Hex(rawToken)
  const expiresAt = new Date(Date.now() + INVITE_TTL_HOURS * 3_600_000).toISOString()

  const { error: dbError } = await supabase.from('team_invitations').upsert({
    team_id: teamId, email, role, invited_by: user.id,
    token_hash: tokenHash, expires_at: expiresAt, accepted_at: null, revoked_at: null
  }, { onConflict: 'team_id,email' })

  if (dbError) return fail('DB_ERROR', 'No se pudo crear la invitación', 500)

  // 3. Encolar el email — NOTIF-002: nunca await directo del envío
  await env.NOTIF_QUEUE.send({
    channel: 'email',
    template: 'invitation',
    to: email,
    data: {
      inviterName: user.user_metadata?.name ?? user.email,
      teamName:    /* fetch */ '',
      joinUrl:     `https://collabscribe.com/invite/accept?token=${rawToken}`,
      expiresInHours: INVITE_TTL_HOURS
    }
  })

  return ok({ message: `Invitación enviada a ${email}`, expires_in_hours: INVITE_TTL_HOURS })
}

async function sha256Hex(input: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(input))
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('')
}
```

### 3.2 Página de Aceptación de Invitación

El invitado llega con el token propio en la URL — **no** con una sesión de Supabase ya iniciada. Si no tiene cuenta, primero pasa por login/registro normal (que si es passwordless, es un magic link de login independiente, con su propia TTL de `AUTH-003`); recién con sesión activa se valida el token de invitación contra el backend.

```tsx
// /invite/accept?token=...
export function InviteAcceptPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const { data: session } = useSession() // hook de sesión del proyecto
  const navigate = useNavigate()
  const [state, setState] = useState<'loading' | 'error' | 'accepted'>('loading')

  useEffect(() => {
    if (!token) { setState('error'); return }
    if (!session) return // esperar a que el usuario complete login/registro (AUTH-003, flujo aparte)

    api.post('/api/teams/accept-invite', { token })
      .then(({ data }) => { navigate(`/team/${data.team_id}`) })
      .catch(() => setState('error'))
  }, [token, session])

  if (state === 'error') {
    return <InviteError message="Esta invitación no es válida, expiró o ya fue utilizada." />
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="mt-4 text-foreground/60">Aceptando invitación...</p>
      </div>
    </div>
  )
}
```

---

## 📋 CHECKLIST DE SEGURIDAD AUTH

- [ ] TOTP habilitado en Supabase > Auth > Settings
- [ ] MFA obligatorio para roles `admin` y `owner`
- [ ] Magic link de **login** con TTL ≤ 15 min, un solo uso (`AUTH-003`, config "Auth OTP Expiration" en Supabase)
- [ ] Invitación a equipo con **token propio** (no `inviteUserByEmail`), tabla `team_invitations`, TTL default 48h y revocable (`AUTH-004`)
- [ ] Passkeys disponibles si el navegador lo soporta (`window.PublicKeyCredential`)
- [ ] Códigos de recuperación para TOTP (12 códigos de un solo uso)
- [ ] Tokens de sesión en memoria, refresh token en cookie `httpOnly; Secure; SameSite=Strict`
- [ ] Rate limiting en `/api/auth/*` (máx 5 intentos / 15min por IP) y en `/api/teams/*/invite` (previene spam de invitaciones)
