---
title: "Dominio Security — Índice y Mapa de Cobertura"
category: 05_Security
doc_type: referencia
tags: [seguridad, indice, cobertura, plataformas]
summary: "Índice del dominio Security: qué documento aplica a cada plataforma (web, desktop, móvil), cómo se relacionan los tres niveles y qué queda explícitamente fuera de alcance."
keywords: [seguridad, indice, web, desktop, apk, android, tauri, cobertura, alcance]
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "00_HANDBOOK_FORMAT.md — jerarquía de especialización de 3 niveles"
  - "OWASP Application Security Verification Standard (ASVS) v4.0.3"
  - "OWASP Mobile Application Security Verification Standard (MASVS) v2.0"
updated: 2026-07-29
---

# 🔒 DOMINIO SECURITY — ÍNDICE

Este dominio cubre **tres superficies de despliegue**: web, escritorio y móvil. El principio que las une es uno solo:

> **El backend es la única frontera de confianza. Todo lo que se distribuye al usuario es público y modificable.**

Todo lo demás son consecuencias de aplicar ese principio a un runtime distinto.

---

## 🗺️ Qué documento aplica según lo que estés construyendo

| Estás trabajando en… | Empieza por | Y además |
|---|---|---|
| API, Worker, base de datos, cualquier backend | [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) | [ESTANDAR_RATE_LIMITING.md](ESTANDAR_RATE_LIMITING.md) |
| Frontend web / SPA | [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) | [SECURITY_ADVANCED.md](SECURITY_ADVANCED.md) (CSP, SRI, security.txt) |
| App de escritorio (Tauri) | [DESKTOP_SECURITY_STANDARD.md](DESKTOP_SECURITY_STANDARD.md) | el estándar base, que sigue aplicando al backend |
| App móvil / APK (Android) | [MOBILE_SECURITY_STANDARD.md](MOBILE_SECURITY_STANDARD.md) | el estándar base, que sigue aplicando al backend |
| Login, MFA, passkeys, magic links | [AUTH_MFA_STANDARD.md](AUTH_MFA_STANDARD.md) | [AUTH_ADVANCED_STANDARD.md](AUTH_ADVANCED_STANDARD.md) (SSO, SAML, sesiones) |
| Cobros, suscripciones, webhooks de pago | [PAYMENTS_SECURITY_STANDARD.md](PAYMENTS_SECURITY_STANDARD.md) | — |
| GDPR, CCPA, términos, cookies | [LEGAL_COMPLIANCE_STANDARD.md](LEGAL_COMPLIANCE_STANDARD.md) | — |
| Diseñar defensas / priorizar hardening | [THREAT_MODEL.md](THREAT_MODEL.md) | — |
| Algo ya se rompió | [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) | — |

---

## 🧱 Estructura del dominio

```
Nivel 1 — Base, aplica SIEMPRE
  SECURITY_ENGINEERING_STANDARD.md    7 capas: input, CORS, auth, authz, rate limit, cifrado, headers  (S-001…S-014)

Nivel 2 — Por superficie de despliegue
  DESKTOP_SECURITY_STANDARD.md        Tauri: ACL de IPC, CSP, keychain, updater firmado, code signing  (DSEC-001…011)
  MOBILE_SECURITY_STANDARD.md         Android: firma, TLS, Keystore, exported, OTA firmado             (MSEC-001…012)
  SECURITY_ADVANCED.md                Web: CSP estructurada, security.txt, hardening de cabeceras

Nivel 2 — Por función transversal
  AUTH_MFA_STANDARD.md / AUTH_ADVANCED_STANDARD.md    identidad y sesión
  ESTANDAR_RATE_LIMITING.md                           abuso y cuota
  PAYMENTS_SECURITY_STANDARD.md                       dinero (PCI DSS)
  LEGAL_COMPLIANCE_STANDARD.md                        obligaciones legales

Operación
  THREAT_MODEL.md        qué puede pasar y qué prevenirlo cuesta menos que sufrirlo
  INCIDENT_RESPONSE.md   runbook de la primera hora
```

**Regla de herencia (`00_HANDBOOK_FORMAT.md` §4):** los documentos de Nivel 2 **no repiten** el Nivel 1. Si `DESKTOP_SECURITY_STANDARD.md` no menciona la validación de inputs del backend, no es un olvido: es que `S-001` ya la exige y sigue vigente.

---

## 🔗 Las tres reglas que se repiten en las tres plataformas

No son duplicación; son la misma regla vista desde cada runtime, y por eso llevan un identificador en cada documento:

| Principio | Web | Desktop | Móvil |
|---|---|---|---|
| Ningún secreto de servidor en el cliente | `S-001` + variables públicas | `DSEC-004` | `MSEC-001` |
| El token no vive en almacenamiento plano | `S-007` (cookie HttpOnly) | `DSEC-004` (keychain del SO) | `MSEC-004` (Keystore) |
| El servidor no confía en el cliente jamás | `S-009` / `S-010` | `DSEC-011` | `MSEC-008` / `MSEC-012` |

Si una de las tres se rompe en cualquier plataforma, las demás capas no compensan.

---

## 🚫 Alcance: qué NO cubre este dominio

Declarado explícitamente para que nadie asuma cobertura que no existe:

- **iOS.** [MOBILE_SECURITY_STANDARD.md](MOBILE_SECURITY_STANDARD.md) cubre Android/APK. Las reglas de plataforma iOS (Keychain ACL, ATS, App Attest, provisioning) no están escritas todavía — se añadirán cuando un proyecto real las necesite (`00_HANDBOOK_FORMAT.md` §4: los documentos se crean bajo demanda).
- **Electron.** El estándar desktop asume Tauri v2. Las reglas de capa 1 se transfieren, pero `nodeIntegration`, `contextIsolation` y `sandbox` de Electron no están documentadas.
- **Seguridad de infraestructura corporativa.** Fuera del modelo de adversario declarado en [THREAT_MODEL.md](THREAT_MODEL.md) (dev solo o equipo de 2-3): sin SOC, sin red interna, sin insider threat corporativo.
- **Certificación formal** (SOC 2, ISO 27001, PCI DSS nivel 1). [LEGAL_COMPLIANCE_STANDARD.md](LEGAL_COMPLIANCE_STANDARD.md) cubre obligaciones de privacidad, no auditoría certificada.
