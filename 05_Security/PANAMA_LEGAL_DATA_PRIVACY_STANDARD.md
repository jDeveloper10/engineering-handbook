---
title: "Estándar de Cumplimiento Legal y Privacidad de Datos — Panamá (Ley 81 y Ley 51)"
category: 05_Security
doc_type: estandar
tags: [panama, ley-81, antai, privacidad, datos-personales, mici, ley-51, comercio-electronico, arco, consentimientos]
summary: "Vertical Panamá para privacidad y legalidad de software: Ley 81 de 2019 (Protección de datos personales, ANTAI, derechos ARCO, transferencias transfronterizas), Ley 51 de 2008 / Ley 82 de 2012 (Comercio electrónico, validez de acuerdos, logs de auditoría MICI) y conciliación con retención fiscal DGI."
keywords: [panama, ley-81, ley-51, antai, mici, dgi, privacidad, datos-personales, arco, consentimiento, terminos-condiciones, soft-delete, cloudflare, supabase]
status: VERIFIED
confidence: 90%
reviewed: false
sources:
  - "Ley 81 de 26 de marzo de 2019 (Sobre Protección de Datos Personales de Panamá)"
  - "Decreto Ejecutivo 285 de 28 de mayo de 2021 (Reglamentación de la Ley 81 de 2019)"
  - "ANTAI — Guías y Criterios Orientadores sobre Protección de Datos Personales — antai.gob.pa"
  - "Ley 51 de 22 de julio de 2008, modificada por Ley 82 de 2012 (Comercio Electrónico y Documentos Electrónicos, MICI)"
  - "Código de Comercio de Panamá, art. 93 y Ley 52 de 2016 (Conservación de registros contables por 5 años)"
updated: 2026-10-05
---

# ESTÁNDAR DE CUMPLIMIENTO LEGAL Y PRIVACIDAD DE DATOS — PANAMÁ (Ley 81 y Ley 51)

> Nivel 3 (Vertical de país: Panamá). Complementa a [LEGAL_COMPLIANCE_STANDARD.md](LEGAL_COMPLIANCE_STANDARD.md) y se armoniza con el estándar contable [PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md](../16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md).
> Este documento regula los requisitos jurídicos y arquitectónicos obligatorios para cualquier aplicación web, SaaS, backend o aplicación móvil que opere en Panamá o procese datos de ciudadanos/residentes panameños.

---

## MARCO JURÍDICO REGULATORIO EN PANAMÁ

| Ley / Ente Regulador | Ámbito de Aplicación | Requisito Principal para el Software |
|---|---|---|
| **Ley 81 de 2019 / ANTAI** | Protección de Datos Personales | Consentimiento expreso, derechos ARCO, seguridad técnica y declaración de transferencias transfronterizas. Multas de hasta B/. 10,000. |
| **Ley 51 de 2008 / MICI** | Comercio Electrónico y Firmas | Validez legal de contratos en línea (Clickwrap), integridad de mensajes de datos y logs inmutables. |
| **Ley 52 de 2016 / DGI** | Conservación Fiscal / Contable | Obligación de conservar registros contables y facturas electrónicas durante mínimo **5 años**. |

---

## REGLAS INQUEBRANTABLES

### LEG-PA-001: Consentimiento Previo, Informado y Verificable (Ley 81 art. 5)

**[REQUIRED]** **Por qué:** La Ley 81 prohíbe el tratamiento de datos personales sin el consentimiento previo, inequívoco e informado del titular. Las casillas pre-marcadas (*opt-out*) son consideradas nulas de pleno derecho por la ANTAI y constituyen infracción grave.

**Agnóstico:**
1. Las casillas de verificación de Términos y Condiciones y Política de Privacidad deben presentarse **desmarcadas** por defecto en cualquier formulario de registro o captura de datos.
2. La aceptación debe registrar una prueba auditable en la base de datos con: identificador del usuario, versión exacta de los términos aceptados, fecha/hora UTC, dirección IP y User-Agent.

**Implementación de Referencia (Esquema SQL / Prisma):**
```prisma
model UserConsent {
  id              String   @id @default(cuid())
  userId          String
  termsVersion    String   // ej. "2026.1"
  privacyVersion  String   // ej. "2026.1"
  acceptedAt      DateTime @default(now())
  ipAddress       String?  // Hash o IP truncada de registro
  userAgent       String?
  user            User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, termsVersion])
}
```

---

### LEG-PA-002: Implementación de Derechos ARCO y Conciliación Fiscal (DGI vs ANTAI)

**[REQUIRED]** **Por qué:** El titular tiene derecho de **Cancelación (Supresión)** de sus datos. Sin embargo, el Código de Comercio (art. 93) y la DGI exigen conservar registros contables y facturas por 5 años. Borrar una factura electrónica (CUFE) o asiento contable por pedido de un usuario comete un delito tributario; negar el borrado total de sus datos personales viola la Ley 81.

**Regla de Conciliación Técnica ("Anonimización con Retención Fiscal"):**
Cuando un usuario ejerce su derecho de cancelación en un SaaS o plataforma:
1. **Datos de Perfil / Marketing / Sesión:** Se eliminan definitivamente (*Hard delete*) de sesiones, tokens, carritos y listas de correo.
2. **Datos en Facturas y Asientos Fiscales:** Se conservan las facturas emitidas por 5 años, pero se disocia el perfil activo. El registro en la tabla de usuarios se anonimiza:
   * `name = "Usuario Anonimizado (ARCO)"`
   * `email = "anon_${id}@deleted.local"`
   * `phone = null`
   * `passwordHash = "PURGED"`
   * `deletedAt = NOW()`

**Implementación de Referencia (TypeScript / Servicio de Supresión):**
```typescript
interface TransactionalClient {
  session: { deleteMany: (args: { where: { userId: string } }) => Promise<unknown> }
  user: { update: (args: { where: { id: string }; data: Record<string, unknown> }) => Promise<unknown> }
  auditLog: { create: (args: { data: Record<string, unknown> }) => Promise<unknown> }
}

export async function executeArcoRightToForget(userId: string, tx: TransactionalClient) {
  // 1. Purgar credenciales, sesiones y tokens
  await tx.session.deleteMany({ where: { userId } })

  // 2. Anonimizar perfil preservando registros contables obligatorios
  await tx.user.update({
    where: { id: userId },
    data: {
      name: 'Usuario Anonimizado',
      email: `anon_${userId.slice(0, 8)}@purged.invalid`,
      passwordHash: 'PURGED_BY_ARCO_REQUEST',
      isPending: false,
      isApproved: false,
      updatedAt: new Date(),
    },
  })

  // 3. Registrar auditoría interna del ejercicio del derecho
  await tx.auditLog.create({
    data: {
      action: 'ARCO_RIGHT_TO_FORGET_APPLIED',
      entityId: userId,
      performedAt: new Date(),
    },
  })
}
```

---

### LEG-PA-003: Declaración Obligatoria de Transferencia Transfronteriza de Datos

**[REQUIRED]** **Por qué:** El artículo 33 de la Ley 81 y el Decreto 285 regulan la transferencia de datos personales fuera de Panamá. Dado que la infraestructura en la nube moderna (Cloudflare Workers, Supabase en AWS us-east-1, Vercel, Resend) almacena y procesa peticiones en centros de datos internacionales, la Política de Privacidad debe informarlo expresamente.

**Cláusula Mandatoria en la Política de Privacidad de todo proyecto:**
> *"Sus datos personales pueden ser alojados y procesados en servidores ubicados fuera de la República de Panamá (incluyendo infraestructura en la nube de proveedores como Cloudflare, Inc. y Amazon Web Services, Inc.). Dicha transferencia se realiza bajo estrictos estándares de seguridad técnica (cifrado TLS 1.3 y AES-256 en reposo) y exclusivamente para la prestación de los servicios contratados, en estricto cumplimiento con la Ley 81 de 2019."*

---

### LEG-PA-004: Validez de Acuerdos de Comercio Electrónico (Ley 51 de 2008 / MICI)

**[REQUIRED]** **Por qué:** Un usuario no puede alegar desconocimiento de los Términos de Servicio si el sistema implementa un mecanismo *Clickwrap* claro. En Panamá, la manifestación electrónica de la voluntad tiene plena validez jurídica si existe constancia de acceso a las condiciones antes de contratar.

**Reglas de Interfaz (UI/UX):**
1. El enlace a los **Términos y Condiciones** y a la **Política de Privacidad** debe ser claramente legible y abrirse en pestaña nueva (`target="_blank"`).
2. El botón de envío debe indicar la consecuencia jurídica: *"Al registrarte o continuar, aceptas los Términos y Condiciones y la Política de Privacidad"*.
3. En transacciones de pago (ej. suscripciones a Balance360 o compras en tiendas cliente), debe presentarse el desglose con el impuesto **ITBMS (7%)** desglosado antes del clic final de cobro.

---

### LEG-PA-005: Registro de Trazabilidad e Integridad de Transacciones (Logs de Auditoría)

**[RECOMMENDED]** **Por qué:** La Ley 51 exige garantizar la integridad y no repudio de las transacciones comerciales electrónicas. Si un cliente disputa un cobro o una alteración de factura, la base de datos debe ser capaz de demostrar la cronología exacta.

**Regla:** Toda mutación de estado sensible (cambio de rol de usuario, emisión o anulación de factura, cobro a través de pasarelas como PágueloFácil) debe registrar un log inmutable con fecha, hora, actor y estado anterior/nuevo.

---

## 3. CHECKLIST DE CUMPLIMIENTO LEGAL PANAMÁ (PRE-LANZAMIENTO)

- [ ] **Formularios:** Casillas de verificación de términos desmarcadas por defecto.
- [ ] **Legal URLs:** Rutas públicas accesibles en la web (`/terminos` y `/privacidad`).
- [ ] **Política de Privacidad:** Menciona explícitamente la **Ley 81 de 2019**, el rol de la **ANTAI** y la transferencia transfronteriza a servidores cloud.
- [ ] **Términos y Condiciones:** Declara jurisdicción en la **República de Panamá** y tribunales de la ciudad de Panamá.
- [ ] **Precios y Facturación:** Muestran el precio base y el **ITBMS (7%)** claramente desglosado.
- [ ] **Flujo ARCO:** La base de datos y el backend soportan anonimización de usuario sin corromper la retención fiscal de 5 años.
- [ ] **Ciberseguridad:** Contraseñas hasheadas con bcrypt/argon2, conexiones forzadas por HTTPS (HSTS) y variables de entorno protegidas.
