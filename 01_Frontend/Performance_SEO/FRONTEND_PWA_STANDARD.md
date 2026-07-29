---
title: "Patrón Progressive Web App (PWA) Offline-First"
category: 01_Frontend
tags: [pwa, offline, service-worker, workbox, dexie]
status: current
---

# 📱 PATRÓN PWA & OFFLINE-FIRST

## 🎯 ¿Qué es y por qué es crítico?
Una Progressive Web App (PWA) permite a tu web instalarse como una app nativa, enviar notificaciones push y funcionar sin conexión a internet. Una arquitectura Offline-First garantiza que el usuario pueda interactuar con la app en el metro, en un avión o con mala señal, y sincronizar los datos automáticamente cuando recupere la conexión.

> **REGLA INQUEBRANTABLE:** Toda app SaaS en producción DEBE funcionar sin conexión básica (caché). Si permite edición, DEBE encolar las operaciones y sincronizarlas en background cuando vuelva la red.

---

## ⚙️ 1. MANIFEST (El ADN de la App)

El archivo `manifest.json` va en la raíz de `public/` y le dice al móvil/desktop cómo instalarse.

```json
{
  "name": "OmniSuite Enterprise",
  "short_name": "OmniSuite",
  "description": "Tu suite de gestión offline-first.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

---

## 🧠 2. SERVICE WORKER CON WORKBOX (Estrategias de Caché)

Usamos Workbox de Google para no lidiar con la API cruda del Service Worker.

**`service-worker.js`**
```javascript
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { BackgroundSyncPlugin } from 'workbox-background-sync';

// 1. CACHE FIRST (Para Assets Estáticos: JS, CSS, Fuentes)
// Si está en caché lo sirve instantáneo. Solo va a red si no existe.
registerRoute(
  ({ request }) => request.destination === 'script' || request.destination === 'style' || request.destination === 'font',
  new CacheFirst({
    cacheName: 'static-assets',
    plugins: [
      new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 30 * 24 * 60 * 60 }), // 30 días
    ],
  })
);

// 2. STALE WHILE REVALIDATE (Para Imágenes y Avatars)
// Sirve caché instantáneo, pero revalida en background para actualizar en el próximo reload
registerRoute(
  ({ request }) => request.destination === 'image',
  new StaleWhileRevalidate({ cacheName: 'images' })
);

// 3. NETWORK FIRST (Para llamadas API /fetch)
// Siempre busca la API fresca. Si estás sin red, devuelve el caché anterior de la DB.
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-responses',
    networkTimeoutSeconds: 3, // Si tarda >3s asume offline y sirve caché
  })
);

// 4. BACKGROUND SYNC (Cola de mutaciones offline)
// Si intentas hacer un POST/PUT sin red, lo guarda y lo envía al reconectar
const bgSyncPlugin = new BackgroundSyncPlugin('offline-mutations-queue', {
  maxRetentionTime: 24 * 60 // Reintentar hasta por 24 horas
});

registerRoute(
  ({ request }) => request.method === 'POST' || request.method === 'PUT',
  new NetworkFirst({ plugins: [bgSyncPlugin] })
);
```

---

## 💻 3. LÓGICA EN FRONTEND (React)

En el frontend detectamos el estado de la red y gestionamos el banner de instalación.

```tsx
import { useState, useEffect } from 'react'
import Dexie from 'dexie'

// 1. Base de datos local (IndexedDB) para guardar borradores complejos offline
export const localDb = new Dexie('OmniSuiteLocalDB')
localDb.version(1).stores({
  drafts: 'id, type, payload, updated_at' // Primary key 'id'
})

// `beforeinstallprompt` no está en lib.dom.d.ts — se declara su forma mínima (FE-001: nada de `any`)
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function PwaManager() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine)
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null)

  useEffect(() => {
    // 1. Registro del Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
      })
    }

    // 2. Monitoreo de Red (Online / Offline)
    const handleOnline = () => setIsOffline(false)
    const handleOffline = () => setIsOffline(true)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // 3. Capturar el prompt de Instalación (Añadir a Pantalla de Inicio)
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      setInstallPrompt(e as BeforeInstallPromptEvent)
    })

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Disparar la instalación manual
  const handleInstallClick = async () => {
    if (!installPrompt) return
    installPrompt.prompt()
    const { outcome } = await installPrompt.userChoice
    if (outcome === 'accepted') setInstallPrompt(null)
  }

  return (
    <>
      {/* BANNER OFFLINE */}
      {isOffline && (
        <div className="fixed bottom-0 w-full bg-red-600 text-white text-center py-2 z-50">
          ⚠️ Estás desconectado. Los cambios se guardarán localmente y se sincronizarán al volver.
        </div>
      )}

      {/* BOTÓN INSTALAR APP */}
      {installPrompt && !isOffline && (
        <button 
          onClick={handleInstallClick}
          className="fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg"
        >
          ⬇️ Instalar App Nativamente
        </button>
      )}
    </>
  )
}
```

---

## 🔔 4. NOTIFICACIONES PUSH NATIVAS

Un PWA puede recibir notificaciones Push (Web Push API) incluso cuando está cerrado.

```javascript
// En frontend: Pedir permiso
async function requestPushPermission() {
  const permission = await Notification.requestPermission()
  if (permission === 'granted') {
    const swRegistration = await navigator.serviceWorker.ready
    
    // Suscribirse al Push Service de Google/Mozilla
    const subscription = await swRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: 'TU_VAPID_PUBLIC_KEY' // Generado en el backend
    })
    
    // Enviar el token (subscription) a tu base de datos para guardarlo en el Perfil del usuario
    await fetch('/api/user/push-subscription', {
      method: 'POST',
      body: JSON.stringify(subscription)
    })
  }
}

// En service-worker.js: Escuchar la llegada del Push y mostrarlo
self.addEventListener('push', (event) => {
  const data = event.data.json()
  
  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge.png',
    data: { url: data.url } // Guardar URL para abrir al clickear
  }
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  )
})

// Clic en la notificación: Abrir la PWA en esa ruta
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  )
})
```
