---
title: "Sistema de Notificaciones: Email + Push + In-App"
category: 02_Backend
doc_type: estandar
tags: [notificaciones, resend, vapid, fcm, apns, expo, push, email, realtime]
summary: "Estándar completo del sistema de notificaciones multicanal: Email transaccional con Resend + React Email, Web Push con VAPID, Mobile Push con Expo (FCM/APNs), e In-App con Supabase Realtime."
keywords: [notifications, resend, react-email, vapid, service-worker, expo-push, mobile-push, in-app]
updated: 2026-07-27
status: current
---

# 🔔 SISTEMA DE NOTIFICACIONES COMPLETO

## 🎯 Reglas Inquebrantables

**[REQUIRED] NOTIF-001: NUNCA HTML crudo en emails.** Siempre React Email templates. El HTML manual es imposible de mantener y tiene deliverability impredecible.

> **Por qué:** el HTML de email escrito a mano se rompe de forma distinta en cada cliente (Outlook, Gmail, Apple Mail) porque cada uno soporta un subconjunto distinto de CSS. React Email compila a HTML compatible con todos ellos y permite versionar el template como código en vez de como un string mantenido a mano.

**[REQUIRED] NOTIF-002: Email transaccional < 5 segundos.** Si el proceso que lo dispara tarda más, usar Cloudflare Queues — el request del usuario no espera el email.

> **Por qué:** enviar un email es una llamada de red a un proveedor externo cuya latencia no controlas. Si el request del usuario espera esa llamada, la lentitud de Resend se convierte en la lentitud de tu API. Encolarlo desacopla ambas cosas.

**[REQUIRED] NOTIF-003: VAPID private key NUNCA en el frontend.** Solo en secretos del Worker.

> **Por qué:** la clave privada VAPID es lo que demuestra ante el navegador que las notificaciones vienen de tu servidor. En el frontend es tan pública como cualquier otro string del bundle (ver `S-001`), y con ella cualquiera podría enviar push suplantando tu aplicación.

**[REQUIRED] NOTIF-004: Push subscriptions expiradas (HTTP 410) DEBEN eliminarse automáticamente.** Acumular subscriptions muertas es un bug silencioso que degrada el sistema.

> **Por qué:** un HTTP 410 significa que el navegador o el sistema operativo invalidó esa suscripción de forma permanente — seguir escribiéndole no falla ruidosamente, solo desperdicia cuota y tiempo de Worker en cada envío futuro, un bug que nadie nota hasta que la factura o la latencia lo delatan.

**NOTIF-005: Mobile Push usa Expo Push Service.** NUNCA FCM directo ni APNs directo — Expo abstrae ambos y elimina la gestión de certificados.

**NOTIF-006: La elección del canal depende del evento y del estado del usuario (online/offline).** Ver tabla §0.1.

---

## 🗺️ 0. ARQUITECTURA DEL SISTEMA

```
Usuario genera evento (nuevo comentario, mención, etc.)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              notif-worker (Worker interno)           │
│  Recibe job via Queue o Service Binding              │
└─────────────────────────────────────────────────────┘
        │
        ├──→ 📧 Email (Resend + React Email)
        │       ├── Transaccional (< 5s, encolado)
        │       ├── Magic Links y invitaciones
        │       └── Resumen semanal (cron scheduled)
        │
        ├──→ 🔔 Web Push (VAPID)
        │       └── Notificaciones en navegador (PWA/web)
        │
        ├──→ 📱 Mobile Push (Expo → FCM/APNs)
        │       └── Notificaciones en app React Native/Expo
        │
        └──→ ⚡ In-App (Supabase Realtime)
                └── Badge contador + lista en tiempo real
```

### 0.1 Tabla de decisión: ¿qué canal usar?

| Evento | Email | Web Push | Mobile Push | In-App |
|---|---|---|---|---|
| @mención (usuario online) | ❌ | ❌ | ❌ | ✅ |
| @mención (usuario offline) | ✅ | ✅ | ✅ | — |
| Nuevo comentario | ❌ | ✅ | ✅ | ✅ |
| Documento compartido contigo | ✅ | ✅ | ✅ | ✅ |
| Invitación a equipo | ✅ | ❌ | ❌ | ✅ |
| Recordatorio de fecha límite | ✅ | ✅ | ✅ | ❌ |
| Magic link de login | ✅ | ❌ | ❌ | ❌ |
| Resumen semanal | ✅ | ❌ | ❌ | ❌ |
| Pago exitoso / fallido | ✅ | ✅ | ✅ | ✅ |
| Alerta de seguridad (nuevo dispositivo) | ✅ | ✅ | ✅ | ✅ |

---

## 📧 1. EMAIL CON RESEND + REACT EMAIL

### 1.1 Instalación

```bash
npm install resend @react-email/components
```

### 1.2 Worker: Servicio de Email

```typescript
// apps/notif-worker/src/services/email.service.ts
import { Resend } from 'resend'
import {
  WelcomeTemplate,
  MagicLinkTemplate,
  InvitationTemplate,
  NotificationTemplate,
  WeeklyDigestTemplate
} from '@collabscribe/email-templates'

export type EmailTemplate =
  | 'welcome'
  | 'magic-link'
  | 'invitation'
  | 'notification'
  | 'weekly-digest'

export interface SendEmailParams {
  to: string | string[]
  template: EmailTemplate
  data: Record<string, any>
  // subject se infiere de la plantilla; se puede sobreescribir:
  subject?: string
}

export async function sendEmail(params: SendEmailParams, env: Env): Promise<void> {
  const resend = new Resend(env.RESEND_API_KEY)

  const templateConfig: Record<EmailTemplate, {
    from: string
    subject: string
    react: React.ReactElement
  }> = {
    'welcome': {
      from: 'CollabScribe <noreply@collabscribe.com>',
      subject: '¡Bienvenido a CollabScribe!',
      react: WelcomeTemplate({ name: params.data.name })
    },
    'magic-link': {
      from: 'CollabScribe <auth@collabscribe.com>',
      subject: 'Tu enlace de acceso seguro',
      react: MagicLinkTemplate({ url: params.data.url, expiresInMinutes: 15 })
    },
    'invitation': {
      from: 'CollabScribe <teams@collabscribe.com>',
      subject: `${params.data.inviterName} te invita al equipo "${params.data.teamName}"`,
      react: InvitationTemplate(params.data)
    },
    'notification': {
      from: 'CollabScribe <notifications@collabscribe.com>',
      subject: params.subject ?? params.data.title,
      react: NotificationTemplate(params.data)
    },
    'weekly-digest': {
      from: 'CollabScribe <digest@collabscribe.com>',
      subject: `Tu resumen de la semana — ${params.data.weekRange}`,
      react: WeeklyDigestTemplate(params.data)
    }
  }

  const config = templateConfig[params.template]

  const { data, error } = await resend.emails.send({
    from:    config.from,
    to:      params.to,
    subject: params.subject ?? config.subject,
    react:   config.react
  })

  if (error) {
    console.error('[EMAIL] Send failed:', { template: params.template, error })
    throw new Error(`Email send failed: ${error.message}`)
  }

  console.info('[EMAIL] Sent:', { id: data?.id, template: params.template })
}
```

### 1.3 Templates (React Email)

```tsx
// packages/email-templates/src/WelcomeTemplate.tsx
import {
  Html, Head, Preview, Body, Container,
  Heading, Text, Button, Hr, Section
} from '@react-email/components'

interface WelcomeTemplateProps {
  name: string
  dashboardUrl?: string
}

export function WelcomeTemplate({
  name,
  dashboardUrl = 'https://app.collabscribe.com'
}: WelcomeTemplateProps) {
  return (
    <Html lang="es">
      <Head />
      <Preview>¡Bienvenido a CollabScribe, {name}! Empieza a escribir.</Preview>
      <Body style={{ fontFamily: '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif', backgroundColor: '#f9fafb', padding: '40px 0' }}>
        <Container style={{ backgroundColor: '#ffffff', borderRadius: '12px', padding: '40px', maxWidth: '560px', margin: '0 auto' }}>
          <Heading style={{ fontSize: '24px', fontWeight: '700', color: '#09090b', margin: '0 0 16px' }}>
            ¡Bienvenido, {name}! 👋
          </Heading>
          <Text style={{ color: '#71717a', lineHeight: '1.6' }}>
            Tu cuenta en CollabScribe está lista. Crea documentos, colabora con tu equipo en tiempo real y organiza tu trabajo en el Kanban.
          </Text>
          <Button
            href={dashboardUrl}
            style={{ backgroundColor: '#2563eb', color: '#ffffff', borderRadius: '8px', padding: '12px 24px', fontWeight: '600', textDecoration: 'none', display: 'inline-block', marginTop: '24px' }}
          >
            Ir al dashboard →
          </Button>
          <Hr style={{ borderColor: '#e4e4e7', margin: '32px 0' }} />
          <Text style={{ color: '#a1a1aa', fontSize: '12px' }}>
            Si no creaste esta cuenta, puedes ignorar este email.
          </Text>
        </Container>
      </Body>
    </Html>
  )
}
```

```tsx
// packages/email-templates/src/MagicLinkTemplate.tsx
export function MagicLinkTemplate({ url, expiresInMinutes }: { url: string; expiresInMinutes: number }) {
  return (
    <Html lang="es">
      <Head />
      <Preview>Tu enlace de acceso a CollabScribe (expira en {expiresInMinutes} minutos)</Preview>
      <Body style={{ fontFamily: 'system-ui', backgroundColor: '#f9fafb', padding: '40px 0' }}>
        <Container style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '40px', maxWidth: '560px', margin: '0 auto' }}>
          <Heading style={{ fontSize: '22px', color: '#09090b' }}>Tu enlace de acceso seguro 🔐</Heading>
          <Text style={{ color: '#71717a' }}>
            Haz clic en el botón de abajo para iniciar sesión. El enlace expira en {expiresInMinutes} minutos.
          </Text>
          <Button href={url} style={{ backgroundColor: '#2563eb', color: '#fff', padding: '12px 24px', borderRadius: '8px', fontWeight: '600', display: 'inline-block', marginTop: '16px' }}>
            Iniciar sesión →
          </Button>
          <Text style={{ color: '#a1a1aa', fontSize: '12px', marginTop: '32px' }}>
            Si no solicitaste este enlace, ignora este email. Nadie puede acceder a tu cuenta sin él.
          </Text>
        </Container>
      </Body>
    </Html>
  )
}
```

### 1.4 Uso desde el Gateway (vía Queue)

```typescript
// En cualquier Worker que necesite enviar un email:
// NUNCA enviar directamente — siempre encolar (NOTIF-002)

await env.NOTIF_QUEUE.send({
  channel: 'email',
  template: 'invitation',
  to: 'invitado@example.com',
  data: {
    inviterName: 'Ana García',
    teamName:    'Producto',
    joinUrl:     'https://app.collabscribe.com/invite/accept?token=...'
  }
})
```

---

## 🔔 2. WEB PUSH CON VAPID (Navegador)

### 2.1 Generar VAPID Keys (una sola vez)

```bash
# En local, ejecutar una vez. Guardar ambas keys.
npx web-push generate-vapid-keys

# Resultado:
# Public Key: BLg... (va al frontend como variable de entorno)
# Private Key: ... (va a los secretos del Worker — NUNCA en el frontend)
```

### 2.2 Frontend: Registro de la Suscripción

```typescript
// src/hooks/usePushSubscription.ts
const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)))
}

export async function subscribeToPush(userId: string): Promise<void> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('Web Push no soportado en este navegador')
    return
  }

  // Pedir permiso explícito al usuario
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return

  const registration = await navigator.serviceWorker.ready

  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
  })

  // Guardar suscripción en el backend
  await fetch('/api/notifications/push-subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id:      userId,
      subscription: subscription.toJSON()
    })
  })
}

export async function unsubscribeFromPush(): Promise<void> {
  const registration = await navigator.serviceWorker.ready
  const subscription = await registration.pushManager.getSubscription()
  if (subscription) {
    await subscription.unsubscribe()
    await fetch('/api/notifications/push-unsubscribe', { method: 'POST' })
  }
}
```

### 2.3 Service Worker (Manejar push en el navegador)

```javascript
// public/sw.js  ←  registrado en el frontend (FRONTEND_PWA_STANDARD.md)

self.addEventListener('push', (event) => {
  if (!event.data) return

  const payload = event.data.json()

  const options = {
    body:    payload.body,
    icon:    payload.icon   || '/icon-192.png',
    badge:   '/badge-72.png',
    image:   payload.image,
    data:    payload.data   || {},
    actions: payload.actions || [
      { action: 'open',    title: 'Abrir' },
      { action: 'dismiss', title: 'Cerrar' }
    ],
    // Agrupar notificaciones del mismo documento
    tag:     payload.tag    || 'default',
    renotify: false
  }

  event.waitUntil(
    self.registration.showNotification(payload.title, options)
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  if (event.action === 'dismiss') return

  const url = event.notification.data?.url ?? '/'

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(clientList => {
        // Si ya hay una tab abierta, enfocarla
        const existingClient = clientList.find(c => c.url === url)
        if (existingClient) return existingClient.focus()
        // Si no, abrir nueva tab
        return clients.openWindow(url)
      })
  )
})
```

### 2.4 Worker: Enviar Web Push

```typescript
// apps/notif-worker/src/services/web-push.service.ts
import * as webpush from 'web-push'

export interface PushSubscription {
  endpoint: string
  keys: { p256dh: string; auth: string }
}

export interface PushPayload {
  title:    string
  body:     string
  icon?:    string
  url?:     string
  tag?:     string
  data?:    Record<string, any>
}

export async function sendWebPush(
  subscription: PushSubscription,
  payload: PushPayload,
  env: Env
): Promise<void> {
  webpush.setVapidDetails(
    'mailto:noreply@collabscribe.com',
    env.VAPID_PUBLIC_KEY,
    env.VAPID_PRIVATE_KEY
  )

  try {
    await webpush.sendNotification(
      subscription,
      JSON.stringify(payload)
    )
  } catch (err: unknown) {
    // NOTIF-004: Limpiar suscripciones expiradas
    const { statusCode } = err as { statusCode?: number }
    if (statusCode === 410 || statusCode === 404) {
      console.info('[PUSH] Subscription expired, removing:', subscription.endpoint)
      await supabase
        .from('push_subscriptions')
        .delete()
        .eq('endpoint', subscription.endpoint)
    } else {
      console.error('[PUSH] Send failed:', err)
    }
  }
}

// Enviar a todos los dispositivos registrados de un usuario
export async function sendWebPushToUser(
  userId: string,
  payload: PushPayload,
  env: Env
): Promise<void> {
  const { data: subs } = await supabase
    .from('push_subscriptions')
    .select('endpoint, keys')
    .eq('user_id', userId)

  await Promise.allSettled(
    (subs ?? []).map(sub => sendWebPush(sub as PushSubscription, payload, env))
  )
}
```

### 2.5 Esquema SQL para Suscripciones

```sql
-- Tabla para guardar suscripciones VAPID
CREATE TABLE push_subscriptions (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  endpoint    TEXT        NOT NULL UNIQUE,
  keys        JSONB       NOT NULL,   -- { p256dh, auth }
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_push_subscriptions_user_id ON push_subscriptions(user_id);

-- RLS: solo el dueño puede ver/borrar sus suscripciones
ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY push_sub_select ON push_subscriptions FOR SELECT USING ((SELECT auth.uid()) = user_id);
CREATE POLICY push_sub_insert ON push_subscriptions FOR INSERT WITH CHECK ((SELECT auth.uid()) = user_id);
CREATE POLICY push_sub_delete ON push_subscriptions FOR DELETE USING ((SELECT auth.uid()) = user_id);
```

---

## 📱 3. MOBILE PUSH CON EXPO (FCM + APNs)

### 3.1 Por qué Expo Push Service

Expo Push Service actúa como proxy inteligente entre tu Worker y FCM (Android) / APNs (iOS). Elimina:
- Gestión de certificados `.p8` de Apple
- Rotación de claves FCM
- Diferencias de payload entre plataformas

### 3.2 Instalación

```bash
# En el Worker
npm install expo-server-sdk

# En la app Expo (frontend móvil)
npx expo install expo-notifications expo-device
```

### 3.3 Registrar Token en la App

```typescript
// apps/mobile/src/hooks/usePushToken.ts
import * as Notifications from 'expo-notifications'
import * as Device from 'expo-device'
import Constants from 'expo-constants'

export async function registerExpoPushToken(userId: string): Promise<void> {
  if (!Device.isDevice) return  // Solo funciona en dispositivo real

  const { status: existingStatus } = await Notifications.getPermissionsAsync()
  let finalStatus = existingStatus

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync()
    finalStatus = status
  }

  if (finalStatus !== 'granted') return

  const token = (await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas?.projectId
  })).data

  // Guardar token en el backend
  await fetch(`${API_URL}/api/notifications/expo-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authToken}` },
    body: JSON.stringify({ user_id: userId, token })
  })
}
```

### 3.4 Worker: Enviar Push Móvil

```typescript
// apps/notif-worker/src/services/mobile-push.service.ts
import Expo, { ExpoPushMessage, ExpoPushTicket } from 'expo-server-sdk'

const expo = new Expo()

export interface MobilePushParams {
  userId:  string
  title:   string
  body:    string
  data?:   Record<string, any>
  badge?:  number
  sound?:  'default' | null
}

export async function sendMobilePush(params: MobilePushParams, env: Env): Promise<void> {
  // Obtener tokens Expo del usuario
  const { data: tokens } = await supabase
    .from('expo_push_tokens')
    .select('token')
    .eq('user_id', params.userId)

  if (!tokens?.length) return

  // Filtrar tokens válidos (Expo los valida con Expo.isExpoPushToken)
  const messages: ExpoPushMessage[] = tokens
    .filter(t => Expo.isExpoPushToken(t.token))
    .map(t => ({
      to:    t.token,
      sound: params.sound ?? 'default',
      title: params.title,
      body:  params.body,
      data:  params.data ?? {},
      badge: params.badge
    }))

  if (!messages.length) return

  // Expo recomienda enviar en chunks de 100
  const chunks = expo.chunkPushNotifications(messages)

  for (const chunk of chunks) {
    try {
      const tickets: ExpoPushTicket[] = await expo.sendPushNotificationsAsync(chunk)

      // Manejar tokens inválidos (limpiar DB)
      for (let i = 0; i < tickets.length; i++) {
        const ticket = tickets[i]
        if (ticket.status === 'error') {
          if (ticket.details?.error === 'DeviceNotRegistered') {
            const invalidToken = messages[i].to as string
            // Backend §10: un token NUNCA se loguea completo — se trunca.
            console.info('[MOBILE_PUSH] Removing invalid token:', `${invalidToken.slice(0, 12)}…`)
            await supabase
              .from('expo_push_tokens')
              .delete()
              .eq('token', invalidToken)
          }
        }
      }
    } catch (err) {
      console.error('[MOBILE_PUSH] Chunk send failed:', err)
    }
  }
}
```

### 3.5 Esquema SQL para Tokens Expo

```sql
CREATE TABLE expo_push_tokens (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  token       TEXT        NOT NULL UNIQUE CHECK (char_length(token) > 10),
  platform    TEXT        CHECK (platform IN ('ios', 'android')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_expo_tokens_user_id ON expo_push_tokens(user_id);

ALTER TABLE expo_push_tokens ENABLE ROW LEVEL SECURITY;
CREATE POLICY expo_token_select ON expo_push_tokens FOR SELECT USING ((SELECT auth.uid()) = user_id);
CREATE POLICY expo_token_insert ON expo_push_tokens FOR INSERT WITH CHECK ((SELECT auth.uid()) = user_id);
CREATE POLICY expo_token_delete ON expo_push_tokens FOR DELETE USING ((SELECT auth.uid()) = user_id);
```

---

## ⚡ 4. IN-APP (SUPABASE REALTIME)

```typescript
// Ref: FRONTEND_REALTIME_PATTERN.md — el código completo ya está ahí
// Aquí solo el contrato de datos de la tabla notifications

-- Ref: collabscribe schema migration (tabla notifications ya definida)
-- Campos mínimos para in-app:
-- notifications.type  IN ('mention','comment','assignment','system','payment')
-- notifications.payload JSONB: { title, body, url, actor_name, actor_avatar }
-- notifications.read  BOOLEAN DEFAULT FALSE

// Frontend: useNotifications hook suscribe a INSERT en notifications WHERE user_id = current
// Ver: 01_Frontend/Patterns/FRONTEND_REALTIME_PATTERN.md
```

---

## 🔁 5. ORQUESTADOR: Queue Consumer

```typescript
// apps/notif-worker/src/index.ts — Queue consumer

export default {
  // Handler HTTP (para API interna si es necesario)
  async fetch(request: Request, env: Env): Promise<Response> {
    return new Response('Notification Worker', { status: 200 })
  },

  // Handler de Queue — procesa jobs de notificación
  async queue(batch: MessageBatch<NotifJob>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        await processNotification(message.body, env)
        message.ack()
      } catch (err) {
        console.error('[NOTIF_QUEUE] Job failed:', message.body, err)
        message.retry()
      }
    }
  }
}

type NotifJob =
  | { channel: 'email';       template: EmailTemplate; to: string; data: Record<string, unknown> }
  | { channel: 'web-push';    userId: string; payload: PushPayload }
  | { channel: 'mobile-push'; userId: string; title: string; body: string; data?: Record<string, unknown> }

async function processNotification(job: NotifJob, env: Env): Promise<void> {
  switch (job.channel) {
    case 'email':
      await sendEmail({ to: job.to, template: job.template, data: job.data }, env)
      break
    case 'web-push':
      await sendWebPushToUser(job.userId, job.payload, env)
      break
    case 'mobile-push':
      await sendMobilePush({ userId: job.userId, title: job.title, body: job.body, data: job.data }, env)
      break
  }
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Email
- [ ] Resend API Key en secretos del Worker (nunca en código)
- [ ] Templates en `packages/email-templates` (React Email, nunca HTML crudo)
- [ ] Emails encolados en Queue (nunca await directo en el request handler)
- [ ] Dominio verificado en Resend (`mail.collabscribe.com`)
- [ ] SPF + DKIM + DMARC configurados (Resend los genera)

### Web Push
- [ ] VAPID keys generadas con `npx web-push generate-vapid-keys`
- [ ] `VAPID_PUBLIC_KEY` en frontend como `VITE_VAPID_PUBLIC_KEY`
- [ ] `VAPID_PRIVATE_KEY` en secretos del Worker (NUNCA en frontend)
- [ ] Service Worker registrado y activo (`/sw.js`)
- [ ] Tabla `push_subscriptions` con RLS habilitado
- [ ] Limpieza automática de subscriptions con 410 Gone

### Mobile Push
- [ ] Expo project ID configurado en `app.json`
- [ ] `expo-notifications` instalado en la app móvil
- [ ] `expo-server-sdk` instalado en el Worker
- [ ] Tabla `expo_push_tokens` con RLS habilitado
- [ ] Limpieza de tokens con `DeviceNotRegistered`
- [ ] Permisos de notificación pedidos con contexto (explicar por qué)
