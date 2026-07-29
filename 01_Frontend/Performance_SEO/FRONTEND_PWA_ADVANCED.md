---
title: "Estándar Avanzado de PWA y Capacidades Web Nativas"
category: 01_Frontend
tags: [pwa, service-worker, background-sync, web-share, badging, file-system, offline]
summary: "Estándar avanzado de Progressive Web Apps (PWA): Sincronización en segundo plano (Background Sync), Badging API, Web Share API, File System Access API e instalación personalizada."
keywords: [pwa, service-worker, background-sync, badging, web-share, file-system, offline, install-prompt]
updated: 2026-07-27
status: current
---

# 📱 ESTÁNDAR AVANZADO DE PWA Y CAPACIDADES WEB NATIVAS

## 🎯 OBJETIVO
Transformar la aplicación web React en una Progressive Web App (PWA) de nivel nativo, con capacidad de ejecución offline fluida, sincronización en segundo plano y acceso a APIs de dispositivo.

---

## 🎯 REGLAS INQUEBRANTABLES

**PWA-001: La aplicación DEBE funcionar offline con los datos de las últimas 24 horas.** La pérdida de conexión a internet no debe bloquear la interfaz ni mostrar pantallas de error en blanco.

**PWA-002: Prompt de instalación personalizado.** NUNCA depender únicamente del banner genérico del navegador; ofrecer un botón en la UI integrado con el evento `beforeinstallprompt`.

---

## 🔄 1. BACKGROUND SYNC Y BADGING API

```typescript
// Registra sincronización en segundo plano desde el Service Worker
export async function registerBackgroundSync() {
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const registration = await navigator.serviceWorker.ready
    await registration.sync.register('sync-offline-documents')
  }
}

// Actualizar el número en el ícono de la app (Badging API)
export function updateAppBadge(unreadCount: number) {
  if ('setAppBadge' in navigator) {
    if (unreadCount > 0) {
      navigator.setAppBadge(unreadCount)
    } else {
      navigator.clearAppBadge()
    }
  }
}
```

---

## 📂 2. FILE SYSTEM ACCESS API (Guardar Archivos Locales)

```typescript
// Guardar un documento directamente en el disco del usuario sin descargas por URL
export async function saveFileToDisk(content: string, defaultName: string) {
  if ('showSaveFilePicker' in window) {
    // File System Access API: todavía no vive en lib.dom.d.ts (FE-001: nada de `any`)
    const picker = window as unknown as { showSaveFilePicker: (o: unknown) => Promise<FileSystemFileHandle> }
    const handle = await picker.showSaveFilePicker({
      suggestedName: defaultName,
      types: [{
        description: 'Documento Markdown',
        accept: { 'text/markdown': ['.md'] }
      }]
    })
    const writable = await handle.createWritable()
    await writable.write(content)
    await writable.close()
  } else {
    // Fallback tradicional
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = defaultName
    a.click()
  }
}
```

---

## 📋 CHECKLIST PWA AVANZADO

- [ ] Service Worker activo con estrategia Cache-First para assets.
- [ ] Manifest de PWA válido (`manifest.webmanifest`) con íconos maskable.
- [ ] Soporte para sincronización de mutaciones con Background Sync.
- [ ] Indicador y contador de notificaciones con Badging API.
- [ ] Prompt de instalación nativo personalizado en la UI.
