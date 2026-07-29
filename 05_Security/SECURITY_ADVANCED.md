---
title: "Estándar Avanzado de Ciberseguridad, CSP, SRI y Hardening"
category: 05_Security
doc_type: estandar
tags: [security, csp, sri, dnssec, supply-chain, gitleaks, security-txt, hardening]
summary: "Estándar avanzado de seguridad ofensiva y defensiva: Content Security Policy (CSP) en Workers, Subresource Integrity (SRI), seguridad de cadena de suministro (Supply Chain), DNSSEC y archivo security.txt."
keywords: [security, csp, content-security-policy, sri, dnssec, supply-chain, gitleaks, security.txt, hardening]
updated: 2026-07-27
status: current
---

# 🛡️ ESTÁNDAR AVANZADO DE CIBERSEGURIDAD Y HARDENING

## 🎯 OBJETIVO
Implementar capas de defensa en profundidad para proteger la infraestructura, mitigar vectores de ataque avanzados (XSS, Clickjacking, Supply Chain Attacks, Man-in-the-Middle) y garantizar la postura de seguridad de la organización.

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] SEC-001: Content Security Policy (CSP) Estricta en todas las respuestas HTTP.**

> **Por qué:** una CSP estricta es la red que atrapa un XSS que ya pasó todas las demás defensas (`S-001` a `S-003`): aunque un script malicioso logre inyectarse, el navegador se niega a ejecutarlo si su origen no está en la lista permitida.

**[REQUIRED] SEC-002: Subresource Integrity (SRI) obligatorio para cualquier script o asset cargado de CDN externo.**

> **Por qué:** un script cargado de un CDN externo se ejecuta con la misma confianza que tu propio código; si el CDN se compromete, el script modificado también. SRI verifica el hash antes de ejecutar, así que un script alterado se rechaza en vez de correr.

**[RECOMMENDED] SEC-003: Publicar el archivo `/.well-known/security.txt`** para divulgación responsable de vulnerabilidades.

> **Por qué:** sin un canal declarado, un investigador que encuentra una vulnerabilidad no tiene forma clara de reportarla de manera responsable y puede optar por publicarla directamente. Es recomendado porque es una práctica de buena higiene sin la cual el producto sigue funcionando, no una defensa técnica.

---

## 🛡️ 1. CONTENT SECURITY POLICY (CSP) ESTRUCTURADA EN WORKERS

```typescript
// Middleware de cabeceras de seguridad en Cloudflare Worker
export function applySecurityHeaders(headers: Headers): Headers {
  const cspDirectives = [
    "default-src 'self'",
    "script-src 'self' https://js.stripe.com",
    // ⚠️ EXCEPCIÓN DOCUMENTADA a SEC-001: `'unsafe-inline'` en style-src (NUNCA en script-src).
    // Motivo: librerías de UI y Tailwind inyectan estilos inline en runtime; sin esto se rompen.
    // Riesgo aceptado: habilita CSS-based UI-redressing, NO ejecución de JS.
    // Vía de eliminación cuando el proyecto lo permita: nonce por request o hashes de estilo.
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: https://assets.collabscribe.com https://*.stripe.com",
    "connect-src 'self' https://api.stripe.com https://*.supabase.co wss://*.supabase.co",
    "frame-ancestors 'none'", // Previene Clickjacking
    "block-all-mixed-content",
    "upgrade-insecure-requests"
  ]

  headers.set('Content-Security-Policy', cspDirectives.join('; '))
  headers.set('X-Frame-Options', 'DENY')
  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  headers.set('Permissions-Policy', 'geolocation=(), camera=(), microphone=()')

  return headers
}
```

---

## 📄 2. ARCHIVO ESTÁNDAR `/.well-known/security.txt`

```text
Contact: mailto:security@collabscribe.com
Expires: 2027-12-31T23:59:59.000Z
Preferred-Languages: es, en
Canonical: https://collabscribe.com/.well-known/security.txt
Policy: https://collabscribe.com/security
```

---

## 📋 CHECKLIST DE SEGURIDAD AVANZADA

- [ ] Cabeceras CSP activas sin la directiva `'unsafe-eval'`.
- [ ] Atributos SRI `integrity="sha384-..."` en scripts de CDNs de terceros.
- [ ] DNSSEC activado en el panel de Cloudflare DNS.
- [ ] Escaneo de dependencias en CI con `socket.dev` / `npm audit`.
- [ ] Archivo `security.txt` desplegado y accesible públicamente.
