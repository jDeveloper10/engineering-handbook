---
title: "Patrón Graceful Degradation"
category: 02_Backend
tags: [resiliencia, api, fallback, bulkhead]
status: current
---

# 🛡️ PATRÓN GRACEFUL DEGRADATION (Bulkhead + Fallback)

## 🎯 ¿Qué es y por qué es crítico?
La **Degradación Graceful** es la filosofía de que si una parte no vital del sistema se rompe, la aplicación general no debe morir. 
El **Bulkhead Pattern** (inspirado en los mamparos herméticos de los submarinos) dicta aislar los recursos. Si un microservicio (Notificaciones) se inunda y colapsa, no debe arrastrar al servicio de Facturación.

> **REGLA INQUEBRANTABLE:** Si un servicio no crítico falla, la app DEBE seguir funcionando. NUNCA devolver un `Error 500` masivo si existe un Fallback o se puede mostrar la UI parcialmente.

---

## 💻 IMPLEMENTACIÓN DEL API GATEWAY (Workers)

En este ejemplo, nuestro Gateway (Cloudflare Worker) orquesta llamadas a 3 microservicios. Si uno falla, aplica el fallo controlado en lugar de matar toda la petición.

```typescript
// Backend (Worker API Gateway)
export async function handleDashboardRequest(request: Request, env: Env) {
  const userId = getUserId(request)

  // 1. Ejecución paralela aislada (Bulkhead)
  // Usamos Promise.allSettled para que un fallo no cancele las demás promesas
  const [profileReq, billingReq, notifsReq] = await Promise.allSettled([
    fetchProfile(userId, env),           // Crítico
    fetchBilling(userId, env),           // Importante pero puede degradarse
    fetchNotifications(userId, env)      // No crítico
  ])

  // 2. Componer la respuesta degradable
  const response = {
    profile: null,
    billing: null,
    notifications: null,
    status: 'ok',
    warnings: [] as string[]
  }

  // Manejo de Profile (CRÍTICO: Si falla, abortamos con 500)
  if (profileReq.status === 'fulfilled') {
    response.profile = profileReq.value
  } else {
    throw new Error('Servicio principal (Profile) inalcanzable.')
  }

  // Manejo de Facturación (FALLBACK KV: Leemos el último estado conocido)
  if (billingReq.status === 'fulfilled') {
    response.billing = billingReq.value
    // Actualizar caché en background
    env.KV.put(`billing:${userId}`, JSON.stringify(billingReq.value)).catch(() => {})
  } else {
    response.warnings.push('billing_degraded')
    const cachedBilling = await env.KV.get(`billing:${userId}`, 'json')
    response.billing = cachedBilling || { status: 'unknown', balance: 0 } 
  }

  // Manejo de Notificaciones (DEFAULT FALLBACK: Retornamos null y el front lo maneja)
  if (notifsReq.status === 'fulfilled') {
    response.notifications = notifsReq.value
  } else {
    response.warnings.push('notifications_unavailable')
    response.notifications = { count: 0, items: [] } 
  }
  
  if (response.warnings.length > 0) response.status = 'degraded'

  return Response.json(response)
}
```

---

## 🎨 IMPLEMENTACIÓN FRONTEND (Componentes Resilientes)

El frontend debe estar programado para leer la propiedad `status: 'degraded'` o los `warnings` y adaptar la UI sin arrojar una pantalla de error blanca.

```tsx
// Frontend (React Component)
import { AlertCircle } from 'lucide-react'

export function Dashboard({ data }) {
  
  // Manejo elegante de módulos degradados
  const isBillingDegraded = data.warnings.includes('billing_degraded')
  const isNotifsDegraded = data.warnings.includes('notifications_unavailable')

  return (
    <div className="layout">
      
      {/* HEADER: Graceful UI para notificaciones */}
      <header>
        <h1>Bienvenido, {data.profile.name}</h1>
        <div className="notifications-badge">
          {isNotifsDegraded ? (
            <span title="Notificaciones offline">?</span> // Fallback UI
          ) : (
            <span>{data.notifications.count}</span>
          )}
        </div>
      </header>

      {/* BANNER DE AVISO: Transparentes con el usuario */}
      {data.status === 'degraded' && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
          <p className="text-yellow-700">
            Algunos servicios están experimentando retrasos. Estás viendo información en caché.
          </p>
        </div>
      )}

      {/* MODULE: Facturación */}
      <section className="billing-card relative">
        <h2>Tu Facturación</h2>
        {isBillingDegraded && (
          <div className="absolute inset-0 bg-white/50 flex items-center justify-center backdrop-blur-sm">
            <span className="flex items-center text-gray-600 bg-white px-3 py-1 rounded shadow">
              <AlertCircle className="w-4 h-4 mr-2" />
              Sincronizando cobros...
            </span>
          </div>
        )}
        <div className={isBillingDegraded ? "opacity-50 blur-sm pointer-events-none" : ""}>
          <p>Balance actual: ${data.billing.balance}</p>
          <button>Pagar ahora</button>
        </div>
      </section>
      
    </div>
  )
}
```
