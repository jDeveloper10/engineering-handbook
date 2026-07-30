---
title: "Estándar de Autenticación Avanzada: SAML SSO, Social Login, Passkeys y Sesiones"
category: 05_Security
doc_type: estandar
tags: [auth, saml, sso, oauth, passkeys, webauthn, magic-links, sessions, rate-limit]
summary: "Estándar para esquemas avanzados de autenticación: SAML Enterprise SSO (Okta, Azure AD), Social OAuth (Google, GitHub, Apple), Magic Links con expiración corta, Passkeys (WebAuthn) y gestión de sesiones sospechosas."
keywords: [saml, sso, oauth, passkeys, webauthn, magic-links, sessions, security, rate-limit, okta, azure-ad]
updated: 2026-07-27
status: current
---

# ESTÁNDAR DE AUTENTICACIÓN AVANZADA Y CONTROL DE SESIONES

## OBJETIVO
Definir los mecanismos de autenticación empresarial y biométrica (Enterprise SSO, Social Login, Passkeys) y la gestión de sesiones seguras contra ataques de fuerza bruta y suplantación de identidad.

---

## REGLAS INQUEBRANTABLES

**[REQUIRED] AUTH-001: Bloqueo Progresivo en Login.** Máximo 5 intentos fallidos en 5 minutos por IP o cuenta. El intento 6 impone un bloqueo de 15 minutos.

> **Por qué:** sin límite de intentos, el login es vulnerable a fuerza bruta y credential stuffing con listas de contraseñas filtradas. El bloqueo progresivo hace que probar contraseñas a escala sea económicamente inviable sin bloquear al usuario legítimo que solo se equivocó una vez.

**[REQUIRED] AUTH-002: SAML / Enterprise SSO obligatorio para clientes Enterprise.** Integración con Okta, Microsoft Entra ID (Azure AD) y Google Workspace.

> **Por qué:** una cuenta Enterprise gestiona el acceso de sus empleados de forma centralizada; sin SSO, cada baja de empleado exige revocar manualmente su acceso en tu producto, y ese paso manual es el que se olvida.

**[REQUIRED] AUTH-003: Magic Links con TTL máximo de 15 minutos y un solo uso.** Una vez consumido el token, se invalida inmediatamente.

> **Por qué:** un magic link es una contraseña de un solo uso enviada por un canal que no controlas del todo (el proveedor de email, el cliente de correo del usuario). Limitar su vida a 15 minutos y a un solo uso acota la ventana en la que un link interceptado sirve para algo.

---

## 1. AUTHENTICATION CON PASSKEYS (WEBAUTHN) NATIVAS

```typescript
// Registro de Passkey en el navegador del usuario
export async function registerWebAuthnPasskey(userId: string) {
  if (!window.PublicKeyCredential) {
    throw new Error('Este dispositivo/navegador no soporta Passkeys.')
  }

  // 1. Obtener challenge del Worker Backend
  const challengeRes = await fetch('/api/auth/passkey/challenge', { method: 'POST' })
  const { challenge, options } = await challengeRes.json()

  // 2. Crear credencial biométrica (Face ID / Touch ID / Windows Hello)
  const credential = await navigator.credentials.create({
    publicKey: {
      ...options,
      challenge: Uint8Array.from(atob(challenge), c => c.charCodeAt(0))
    }
  })

  // 3. Registrar credencial pública en el servidor
  await fetch('/api/auth/passkey/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, credential })
  })
}
```

---

## 2. ENTERPRISE SSO / SAML 2.0 (SUPABASE / WORKERS)

```typescript
// Redirección a SSO Empresarial según el dominio del email corporativo
export async function redirectToEnterpriseSSO(email: string, env: Env) {
  const domain = email.split('@')[1]

  // 1. Verificar si el dominio tiene SAML SSO configurado
  const { data: ssoConfig } = await supabase
    .from('sso_providers')
    .select('domain, provider_id')
    .eq('domain', domain)
    .single()

  if (!ssoConfig) {
    throw new Error('El dominio no tiene SSO configurado. Inicia sesión con contraseña.')
  }

  // 2. Iniciar Auth Flow SAML con Supabase
  const { data, error } = await supabase.auth.signInWithSSO({
    domain: ssoConfig.domain
  })

  if (error) throw error
  return data.url // Redirige a Okta / Azure AD
}
```

---

## 3. DETECCIÓN DE SESIONES SOSPECHOSAS Y RATE LIMITING

```typescript
// Middleware para verificar integridad de sesión en cada petición
export async function validateSessionIntegrity(request: Request, env: Env) {
  const ip = request.headers.get('CF-Connecting-IP') ?? 'unknown'
  const userAgent = request.headers.get('User-Agent') ?? 'unknown'
  const userId = request.headers.get('x-user-id')!

  const sessionKey = `session_meta:${userId}`
  const lastMeta = await env.KV.get(sessionKey, 'json') as { ip: string; ua: string } | null

  if (lastMeta) {
    // Alerta si la IP cambia drásticamente de país o User-Agent
    if (lastMeta.ip !== ip && lastMeta.ua !== userAgent) {
      console.warn(`[SUSPICIOUS_SESSION] Cambio abrupto de contexto para usuario ${userId}`)
      await env.NOTIF_QUEUE.send({
        channel: 'email',
        template: 'notification',
        to: userId,
        data: { title: 'Nuevo inicio de sesión sospechoso', body: `IP: ${ip}, Dispositivo: ${userAgent}` }
      })
    }
  }

  await env.KV.put(sessionKey, JSON.stringify({ ip, ua: userAgent }), { expirationTtl: 86400 })
}
```

---

## CHECKLIST DE AUTENTICACIÓN AVANZADA

- [ ] Rate limiting de 5 intentos / 5 min activado en `/api/auth/login`.
- [ ] Passkeys (WebAuthn) integradas y probadas en iOS/Android/Windows.
- [ ] Módulo SAML 2.0 disponible para dominios corporativos.
- [ ] Magic Links con expiración en <= 15 minutos e invalidación tras 1er uso.
- [ ] Monitoreo de cambio de IP/User-Agent en tiempo de ejecución.
