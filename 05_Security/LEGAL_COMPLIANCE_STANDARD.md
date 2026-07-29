---
title: "Estándar de Cumplimiento Legal y Privacidad para SaaS (GDPR, CCPA, DPA)"
category: 05_Security
tags: [legal, gdpr, ccpa, dpa, privacidad, cookies, privacidad-por-diseno, zod, security]
summary: "Estándar técnico y de cumplimiento legal para SaaS: estructura de Términos y Condiciones, Política de Privacidad (GDPR/CCPA), Política de Cookies (con banner React), Acuerdo de Procesamiento de Datos (DPA), esquemas SQL de consentimiento y checklist pre-lanzamiento."
keywords: [legal, gdpr, ccpa, dpa, privacidad, cookies, cookie-banner, terminos-condiciones, consent, privacidad-por-diseno]
updated: 2026-07-27
status: current
---

# 📜 ESTÁNDAR DE CUMPLIMIENTO LEGAL Y PRIVACIDAD PARA SAAS

> ⚠️ **DISCLAIMER:** Este documento es una guía técnica e ingenieril de cumplimiento y arquitectura de software. **NO sustituye el consejo legal profesional.** Siempre valida tus documentos finales con un abogado especializado en derecho digital y privacidad de tu jurisdicción.

---

## 🎯 LOS 4 DOCUMENTOS LEGALES OBLIGATORIOS

| Documento | Obligatorio | Propósito Principal |
|---|---|---|
| **Términos y Condiciones** | ✅ Sí | Contrato y reglas de uso del servicio, limitación de responsabilidad y pagos |
| **Política de Privacidad** | ✅ Sí (GDPR / CCPA) | Transparencia sobre datos recolectados, base legal y derechos de usuarios |
| **Política de Cookies** | ✅ Sí (UE / ePrivacy) | Declaración de cookies esenciales y analíticas con consentimiento |
| **Data Processing Agreement (DPA)** | ✅ Sí (GDPR B2B) | Contrato de procesamiento de datos de clientes para clientes Enterprise |

---

## 📄 1. TÉRMINOS Y CONDICIONES (Estructura Base)

```markdown
# Términos y Condiciones de [NOMBRE DEL SAAS]
**Última actualización:** [FECHA]

1. Aceptación de los Términos (Acceso y uso implican aceptación vinculante).
2. Descripción del Servicio (Definición clara de las funcionalidades SaaS).
3. Elegibilidad (Mayoría de edad 18+ y ausencia de sanciones internacionales).
4. Cuentas de Usuario (Responsabilidad de credenciales y notificación de accesos no autorizados).
5. Suscripciones y Pagos (Procesamiento vía Stripe, facturación recurrente, política de cancelación sin reembolso parcial).
6. Uso Aceptable (Prohibición de malware, scraping, hacking, spam o uso ilegal).
7. Contenido del Usuario (Propiedad intelectual del usuario sobre sus datos y licencia limitada de procesamiento).
8. Propiedad Intelectual (Derechos exclusivos sobre el software, marcas y código del SaaS).
9. Servicios de Terceros (Deslinde sobre integraciones externas: Stripe, Resend, Supabase, Cloudflare).
10. Limitación de Responsabilidad (Servicio "tal cual" / AS IS, tope de responsabilidad equivalente al monto pagado en los últimos 12 meses).
11. Terminación (Derecho a suspender por falta de pago o violación de términos).
12. Ley Aplicable y Jurisdicción (Definición explicita de tribunales y legislación competente).
```

---

## 📄 2. POLÍTICA DE PRIVACIDAD (GDPR & CCPA Compliant)

### 2.1 Matriz de Bases Legales de Procesamiento (GDPR Art. 6)

| Propósito del Tratamiento | Base Legal (GDPR) | Datos Tratados |
|---|---|---|
| Proveer el Servicio SaaS | Ejecución de Contrato (Art. 6.1.b) | Email, nombre, hashes de credenciales, contenido |
| Procesar pagos y suscripciones | Ejecución de Contrato (Art. 6.1.b) | Metadatos de Stripe (`stripe_customer_id`, `pm_xxx`) |
| Emails transaccionales | Interés Legítimo (Art. 6.1.f) | Email, nombre |
| Emails de marketing / promociones | Consentimiento Explícito (Art. 6.1.a) | Email |
| Analítica y mejora de producto | Consentimiento Explícito (Art. 6.1.a) | Datos de uso anónimos / agregados |
| Cumplimiento de obligaciones fiscales | Obligación Legal (Art. 6.1.c) | Historial de facturas e impuestos |

---

## 💻 3. IMPLEMENTACIÓN TÉCNICA EN CÓDIGO

### 3.1 Banner de Cookies Granular (`CookieBanner.tsx`)

**[REQUIRED]** En jurisdicciones de la UE/ePrivacy, las cookies no esenciales (analytics, marketing) **DEBEN estar desactivadas por defecto** hasta recibir el consentimiento explícito del usuario.

```tsx
// src/components/CookieBanner.tsx
import { useEffect, useState } from 'react'

export function CookieBanner() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const consent = localStorage.getItem('cookie_consent')
    if (!consent) setIsVisible(true)
  }, [])

  if (!isVisible) return null

  const handleAcceptAll = () => {
    localStorage.setItem('cookie_consent', 'all')
    setIsVisible(false)
    // Activar scripts de analítica (PostHog, Google Analytics)
    window.dispatchEvent(new Event('cookie_consent_all'))
  }

  const handleAcceptEssential = () => {
    localStorage.setItem('cookie_consent', 'essential')
    setIsVisible(false)
    // Desactivar o no cargar scripts no esenciales
    window.dispatchEvent(new Event('cookie_consent_essential'))
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-background border-t p-4 z-50 shadow-2xl">
      <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-foreground/80 leading-relaxed">
          Utilizamos cookies esenciales para el funcionamiento del servicio y cookies analíticas para mejorar tu experiencia. 
          Consulta nuestra <a href="/cookies" className="underline font-medium">Política de Cookies</a>.
        </p>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={handleAcceptEssential}
            className="px-3 py-1.5 border border-foreground/20 rounded-lg text-xs font-medium hover:bg-surface"
          >
            Solo Esenciales
          </button>
          <button
            onClick={handleAcceptAll}
            className="px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:opacity-90"
          >
            Aceptar Todas
          </button>
        </div>
      </div>
    </div>
  )
}
```

### 3.2 Validación Zod de Registro con Consentimiento Obligatorio

```typescript
// Ref: SECURITY_ENGINEERING_STANDARD.md S-001
import { z } from 'zod'

export const registerWithLegalConsentSchema = z.object({
  email: z.string().email().trim().toLowerCase(),
  password: z.string().min(12, 'La contraseña debe tener al menos 12 caracteres'),
  acceptTerms: z.literal(true, {
    errorMap: () => ({ message: 'Debes aceptar los Términos y Condiciones para continuar' })
  }),
  acceptPrivacy: z.literal(true, {
    errorMap: () => ({ message: 'Debes aceptar la Política de Privacidad para continuar' })
  })
})
```

### 3.3 Auditoría de Consentimiento en Base de Datos

```sql
-- DATABASE_ENGINEERING_STANDARD.md §03
-- Registrar fechas exactas de aceptación para auditorías GDPR/CCPA
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS accepted_terms_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS accepted_privacy_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS accepted_cookies_at TIMESTAMPTZ;

-- Al registrar usuario en el Worker:
UPDATE profiles
SET
  accepted_terms_at = NOW(),
  accepted_privacy_at = NOW()
WHERE id = p_user_id;
```

---

## 🛠️ 4. RUTAS LEGALES ESTÁNDAR

Todo producto SaaS debe exponer las siguientes rutas públicas accesibles desde el footer:

```text
https://tudominio.com/terms     ──→ Términos y Condiciones
https://tudominio.com/privacy   ──→ Política de Privacidad
https://tudominio.com/cookies   ──→ Política de Cookies
https://tudominio.com/dpa       ──→ Acuerdo de Procesamiento de Datos (DPA)
```

---

## 📋 CHECKLIST LEGAL PRE-LANZAMIENTO

### Documentación Pública
- [ ] Términos y Condiciones redactados y accesibles en `/terms`.
- [ ] Política de Privacidad (con detalle de responsables y derechos ARCO/GDPR) en `/privacy`.
- [ ] Política de Cookies publicada en `/cookies`.
- [ ] DPA redactado y disponible para clientes B2B/Enterprise en `/dpa`.

### Implementación y Datos
- [ ] Banner de Cookies funcional con bloqueo por defecto de cookies no esenciales.
- [ ] Checkbox obligatorio de aceptación de términos y privacidad en la pantalla de registro.
- [ ] Trazabilidad en base de datos (`accepted_terms_at`, `accepted_privacy_at`).
- [ ] Proceso para atender solicitudes de eliminación de cuenta y exportación de datos en < 30 días.
- [ ] Direcciones de email operativas: `legal@tudominio.com` y `privacy@tudominio.com`.
