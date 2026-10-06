---
title: "Checklist de Calidad y Release a Producción (QA Agencia)"
category: 06_Testing
doc_type: referencia
tags: [qa, checklist, release, produccion, go-live, pre-entrega]
summary: "Checklist integral de control de calidad antes de liberar un proyecto a producción o entregarlo al cliente. Cubre pruebas unitarias, E2E, responsividad móvil (375px), 4 estados UI, auditoría de seguridad y rendimiento Core Web Vitals."
keywords: [qa, checklist, release, produccion, go-live, criterios, testing]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "06_Testing/Strategy/01_QA_STRATEGY.md"
  - "06_Testing/Strategy/06_TEST_CHECKLIST.md"
---

# CHECKLIST DE RELEASE Y ENTREGA A PRODUCCIÓN (GO-LIVE)

> 🚀 **Objetivo:** Ningún proyecto se entrega al cliente ni se despliega en producción sin marcar el 100% de estas casillas. Garantiza cero sorpresas, cero bugs vergonzosos y estabilidad total.

---

## 1. Pruebas Funcionales y de Código

- [ ] **Tests Unitarios e Integración:** `npm run test` termina en verde (100% passing).
- [ ] **Test de Regresión Obligatorio (`TEST-001`):** Todo bug P0/P1 o fallo de seguridad resuelto incluye un test automatizado que reproduce el caso y evita regresiones antes del merge.
- [ ] **Typecheck Estricto:** `npx tsc --noEmit` sin errores de TypeScript y sin ningún `any` indebido (`FE-001`).
- [ ] **Linter Limpio:** `npm run lint` sin advertencias críticas ni errores.
- [ ] **Flujo de Pago Completo:** Verificado cobro real en pasarela (Wompi / Stripe / NowPayments) y activación instantánea vía webhook.

---

## 2. Experiencia de Usuario (UI/UX) y Responsividad

- [ ] **Mobile First (375px):** Todos los flujos, tablas y modales son completamente usables en un iPhone SE / viewport de 375px.
- [ ] **Los 4 Estados UI Obligatorios (`FE-005`):** Cada vista que consume datos async maneja:
  - ⏳ *Loading:* Skeletons o spinners elegantes.
  - 📭 *Empty:* Ilustración o mensaje amigable cuando no hay datos.
  - ❌ *Error:* Mensaje de error claro con botón de reintentar.
  - ✅ *Success:* Datos renderizados correctamente.
- [ ] **Formularios con Feedback:** Los botones muestran estado de carga durante el submit (`isSubmitting`) para evitar dobles clics.

---

## 3. Seguridad y Secretos

- [ ] **Escaneo de Secretos:** `npm run scan-secrets` ejecutado con éxito (0 tokens o claves privadas en `dist/`).
- [ ] **Variables .env del Frontend:** Solo contienen variables públicas (`VITE_SUPABASE_ANON_KEY`, URLs públicas).
- [ ] **Row Level Security (RLS):** Toda tabla en Supabase tiene RLS habilitado y políticas restrictivas por `auth.uid()`.
- [ ] **Cabeceras de Seguridad:** Verificado HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.
- [ ] **CORS Acotado:** APIs protegidas no reflejan orígenes de atacantes ni usan comodín `*` en endpoints autenticados.

---

## 4. Rendimiento y SEO

- [ ] **Core Web Vitals:** LCP < 2.5s, CLS < 0.1, FID/INP < 200ms.
- [ ] **Favicon y Meta Tags:** Iconos configurados para tema oscuro/claro y tags OpenGraph (`og:image`, `og:title`) listos para compartir en WhatsApp y redes.
- [ ] **Página 404:** Página de error 404 personalizada con botón para volver al inicio.

---

## 5. Cierre de Entrega

- [ ] Dominio personalizado configurado con SSL activo en Cloudflare.
- [ ] Credenciales maestras entregadas de forma segura al cliente.
- [ ] Firma de aceptación de entrega y activación de los 30 días de garantía.
