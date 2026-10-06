---
title: "Estándar de Progressive Web Apps (PWA)"
category: 01_Frontend
doc_type: estandar
tags: [pwa, service-worker, manifest, offline, vite-plugin-pwa]
summary: "Estándar del dominio Frontend para PWAs: service workers, manifest, offline-first, caching strategies y vite-plugin-pwa."
keywords: [pwa, progressive-web-app, service-worker, manifest, offline, cache, vite-plugin-pwa, workbox]
updated: 2026-08-30
status: current
---

# PWA ENGINEERING STANDARD

> **Stack de referencia:** Vite + vite-plugin-pwa + Workbox
> **Depende de:** FRONTEND_ENGINEERING_STANDARD.md (Nivel 1)
> **Aplica a:** Todo proyecto que funcione como PWA (instalable, offline-capable)

---

## 01. Configuración de PWA

### 1.1 vite-plugin-pwa

**[REQUIRED]** Usar `vite-plugin-pwa` para generar service worker automáticamente:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Mi App',
        short_name: 'MiApp',
        description: 'Descripción de mi app',
        theme_color: '#3b82f6',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.supabase\.co\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'supabase-api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 },
            },
          },
        ],
      },
    }),
  ],
});
```

### 1.2 Registro del Service Worker

**[REQUIRED]** Registrar SW después del montaje de la app:

```typescript
// src/main.tsx
import { registerSW } from 'virtual:pwa-register';

const updateSW = registerSW({
  onNeedRefresh() {
    // Mostrar toast de "Nueva versión disponible"
    if (confirm('Nueva versión disponible. ¿Actualizar?')) {
      updateSW();
    }
  },
  onOfflineReady() {
    console.log('App lista para uso offline');
  },
});
```

---

## 02. Manifest

### 2.1 manifest.json válido

**[REQUIRED]** El manifest debe tener todos los campos obligatorios:

```json
{
  "name": "Mi App - Descripción completa",
  "short_name": "MiApp",
  "description": "Descripción de la app",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait-primary",
  "icons": [
    { "src": "/pwa-192x192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/pwa-512x512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/pwa-512x512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### 2.2 Apple Touch Icon

**[REQUIRED]** Agregar apple-touch-icon para iOS:

```html
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
```

---

## 03. Estrategias de Cache

### 3.1 Network First (APIs)

**[REQUIRED]** Para datos dinámicos, intentar red primero:

```typescript
// vite.config.ts workbox.runtimeCaching
{
  urlPattern: /^https:\/\/api\.tuapp\.com\/.*/i,
  handler: 'NetworkFirst',
  options: {
    cacheName: 'api-cache',
    networkTimeoutSeconds: 5,
    expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 },
  },
}
```

### 3.2 Cache First (Assets estáticos)

**[REQUIRED]** Para assets compilados, cachear para siempre:

```typescript
{
  urlPattern: /\.(?:js|css|woff2|png|svg|ico)$/,
  handler: 'CacheFirst',
  options: {
    cacheName: 'static-assets',
    expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 365 },
  },
}
```

### 3.3 Stale While Revalidate (imágenes de contenido)

**[RECOMMENDED]** Para imágenes que cambian poco:

```typescript
{
  urlPattern: /\.(?:png|jpg|jpeg|webp|avif)$/,
  handler: 'StaleWhileRevalidate',
  options: {
    cacheName: 'images',
    expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
  },
}
```

---

## 04. Offline-First Patterns

### 4.1 Detectar conexión

**[REQUIRED]** Hook para detectar estado de red:

```typescript
// src/hooks/useOnline.ts
import { useEffect, useState } from 'react';

export function useOnline(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  return isOnline;
}
```

### 4.2 UI adaptativa

**[REQUIRED]** Mostrar estado de conexión al usuario:

```tsx
function App() {
  const isOnline = useOnline();
  
  return (
    <div>
      {!isOnline && (
        <div className="bg-yellow-500 text-white text-center py-2 text-sm">
          Sin conexión — mostrando datos en caché
        </div>
      )}
      {/* ... resto de la app */}
    </div>
  );
}
```

### 4.3 Sync en background

**[RECOMMENDED]** Usar Background Sync para enviar datos cuando vuelva la conexión:

```typescript
// Registrar sync
if ('serviceWorker' in navigator && 'SyncManager' in window) {
  const registration = await navigator.serviceWorker.ready;
  await registration.sync.register('sync-orders');
}

// En service worker
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-orders') {
    event.waitUntil(syncPendingOrders());
  }
});
```

---

## 05. Instalación

### 5.1 Botón de instalación

**[RECOMMENDED]** Detectar si la app es instalable y ofrecer instalación:

```typescript
// src/hooks/useInstallPrompt.ts
import { useEffect, useState } from 'react';

export function useInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<Event | null>(null);
  
  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);
  
  const install = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User response: ${outcome}`);
    setDeferredPrompt(null);
  };
  
  return { canInstall: !!deferredPrompt, install };
}
```

---

## 06. Validación

### 6.1 Lighthouse PWA audit

**[REQUIRED]** Pasar Lighthouse PWA audit antes de cada release:

```bash
npx lighthouse https://tuapp.com --view
# Score PWA debe ser 100
```

### 6.2 Checklists de instalación

**[REQUIRED]** Verificar que la app es instalable:

- [ ] manifest.json válido
- [ ] Service worker registrado
- [ ] HTTPS (obligatorio para PWA)
- [ ] Icons de 192x192 y 512x512
- [ ] start_url accesible
- [ ] display: standalone

---

## Checklist Pre-Deploy PWA

- [ ] vite-plugin-pwa configurado
- [ ] manifest.json con todos los campos
- [ ] Service worker registrado
- [ ] Estrategias de cache configuradas
- [ ] Hook useOnline implementado
- [ ] UI adaptativa para offline
- [ ] Apple touch icon configurado
- [ ] Lighthouse PWA score: 100
