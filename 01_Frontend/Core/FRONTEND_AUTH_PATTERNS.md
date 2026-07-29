---
title: "Patrones de Autenticación en Frontend"
category: 01_Frontend
tags: [frontend, auth, login, ux, formularios]
summary: "Patrones de UI para autenticación: layouts de login y registro, orden de campos, minimización de datos en el alta y UX de contraseñas."
keywords: [login, registro, auth, password, formularios, layout, ux]
updated: 2026-07-27
status: current
---

# FRONTEND AUTHENTICATION PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, especialmente secciones 09 Forms y 13 Accessibility). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Autenticación tiene suficiente superficie propia (layouts, validación, seguridad percibida, recuperación de cuenta, onboarding) para merecer su propio documento — no es "un formulario más". Este documento cubre la experiencia completa, no solo el diseño visual del formulario de login.

---

## 1. Regla principal

**[REQUIRED]** El layout de autenticación se elige según el tipo de producto, no por defecto:

- SaaS / producto con propuesta de valor que vale la pena mostrar en el momento del login → Split Screen (2.1).
- Herramienta interna / admin / producto donde el login es un trámite, no una oportunidad de marketing → Centered Card (2.2).
- App premium / producto donde la marca debe sentirse minimalista y directa → Full Screen Minimal (2.3).

---

## 2. Layouts de autenticación

### 2.1 Split Screen

```
┌──────────────────┬──────────────────┐
│                   │                  │
│ Imagen            │      Login       │
│ Beneficios         │                  │
│ Estadísticas        │ Email            │
│                   │ Password         │
│                   │                  │
│                   │ [ Iniciar ]      │
└──────────────────┴──────────────────┘
```

**[RECOMMENDED]** para SaaS — el lado no-formulario se aprovecha para reforzar propuesta de valor, prueba social o contexto de marca. Ideal en desktop; en mobile el panel visual se colapsa (ver `FRONTEND_LANDING_PATTERNS.md` 7 sobre mobile-first).

### 2.2 Centered Card

```
──────────────
      Logo
    Bienvenido
Email
Password
[ Entrar ]
──────────────
```

**[RECOMMENDED]** para herramientas internas y paneles de administración — el login es un trámite rápido, no necesita reforzar marca.

### 2.3 Full Screen Minimal

```
Logo
Login
Email
Password
Entrar
```

**[RECOMMENDED]** para apps premium — sensación directa y sin distracción, la marca se comunica por la ausencia de ruido, no por un panel visual adicional.

---

## 3. Reglas base de Login

**[REQUIRED]** — no negociables en cualquier layout:

- Un solo `<h1>` en la pantalla.
- Máximo un CTA primario (`Iniciar sesión`) — cualquier otra acción (social login, crear cuenta) es visualmente secundaria.
- Logo visible (ver `FRONTEND_NAVIGATION_PATTERNS.md` 5.3 — clicable, navega a home).
- Labels visibles asociados a cada campo — nunca depender solo del `placeholder` como label (`FRONTEND_ENGINEERING_STANDARD.md` 9.4).
- Contraseña oculta por defecto, con control de mostrar/ocultar.
- `Enter` envía el formulario sin necesidad de hacer clic en el botón.
- Estados de loading, error y éxito manejados explícitamente (sección 8).
- Responsive — probado en los mismos 3 anchos de referencia del estándar principal (375/768/1280px).

---

## 4. Orden de campos — Login

**[RECOMMENDED]**

```
Email
  ↓
Password
  ↓
Remember me
  ↓
Forgot password
  ↓
[ Login ]
  ↓
Divider ("o continúa con")
  ↓
Google · GitHub · Microsoft
  ↓
Create account
```

**Por qué este orden:** el camino principal (email → password → login) se completa sin distracciones; las alternativas (recuperar contraseña, social login, crear cuenta) están disponibles pero visualmente subordinadas al flujo principal.

---

## 5. Registro — campos y minimización de datos

**[RECOMMENDED]** Orden: Nombre → Email → Password → Confirmar password → Aceptar términos → Crear cuenta.

**[REQUIRED]** No pedir teléfono, dirección o empresa en el registro si no son estrictamente necesarios para que el producto funcione desde el primer uso.

**Por qué:** cada campo adicional en un formulario de registro reduce la tasa de conversión — pedir solo lo indispensable no es solo buena UX, es minimización de datos (menos superficie de riesgo si hay una brecha de seguridad más adelante). Si un dato hace falta después (teléfono para 2FA, empresa para facturación), se pide en el momento en que realmente se necesita, no por adelantado "por si acaso".

---

## 6. Password UX

**[REQUIRED]** Mostrar los requisitos de contraseña *antes* de que el usuario envíe el formulario, actualizándose en tiempo real mientras escribe — no como un error después del submit.

```
Password
████████
✔ 8 caracteres
✔ Una mayúscula
✔ Un número
○ Un símbolo
```

```
❌ Error genérico después de enviar:
"Password inválido."

✅ Requisitos visibles mientras se escribe, sin esperar al submit.
```

---

## 7. Validación en tiempo real

**[REQUIRED]** para campos con formato verificable (email, confirmación de password) — la validación ocurre mientras el usuario escribe o al salir del campo (`blur`), no solo al enviar el formulario completo.

```
Email
juan@gmail
❌ Falta el dominio.
```

Mismo mecanismo que `FRONTEND_ENGINEERING_STANDARD.md` 9.1 (`react-hook-form` + `zod`) — la validación de auth no es un caso especial, usa el mismo patrón declarativo del resto de formularios del proyecto.

---

## 8. Estados

**[REQUIRED]** Los 3 estados de `FRONTEND_ENGINEERING_STANDARD.md` 9.3 (`idle → submitting → success | error`) aplican, con copy específico de auth:

```
Loading:  "Entrando..."         (botón deshabilitado, evita doble-submit)
Error:    "Correo o contraseña incorrectos."
Éxito:    "Redirigiendo..."
```

---

## 9. Mensajes de error

**[REQUIRED]** El mensaje de error nunca expone detalle técnico ni código de estado crudo — mismo principio que `FRONTEND_ENGINEERING_STANDARD.md` 6.3 (errores normalizados a `AppError`), aplicado a auth.

```
❌ "Error 500"
✅ "No pudimos iniciar sesión. Inténtalo nuevamente."
```

---

## 10. Social Login

```
──────────────
[ Entrar ]
──────────────
   o continúa con
Google · GitHub · Apple
```

**[RECOMMENDED]** El divisor y los botones de proveedores van **debajo** del formulario principal, nunca arriba.

**Por qué:** el formulario de email/password es la acción principal y predecible; poner el social login primero compite por atención con la acción que la mayoría de usuarios va a completar, y complica la jerarquía visual sin necesidad.

---

## 11. Recuperar contraseña — flujo completo

**[REQUIRED]** Secuencia completa, sin atajos que dejen al usuario sin salida:

```
Login → Forgot Password → Enviar correo → "Verifica tu email" → Nueva contraseña → Login
```

Cada paso confirma explícitamente lo que acaba de pasar ("Te enviamos un enlace a tu correo") — el usuario nunca queda en una pantalla ambigua sin saber si la acción funcionó.

---

## 12. Onboarding post-registro

**[RECOMMENDED]** (condicionado a la complejidad del producto — un producto simple puede saltar directo al uso). No enviar al usuario directo a un dashboard vacío sin contexto cuando el producto lo requiere:

```
Registro → Verificar correo → Completar perfil → Elegir preferencias → Dashboard
```

**Por qué es RECOMMENDED y no REQUIRED:** un producto simple (una sola función clara) puede no necesitar onboarding — agregar pasos ahí sería fricción sin beneficio. La decisión depende de si el usuario necesita contexto/configuración antes de que el producto le sea útil.

---

## 13. Seguridad UX

**[REQUIRED]**

- No revelar si un correo existe o no en el sistema durante login/registro (ej. "Credenciales incorrectas" en vez de "Ese correo no existe") — mitiga enumeración de usuarios. El nivel de esto depende del perfil de riesgo del producto; para SaaS de bajo riesgo puede relajarse, pero es la opción por defecto.
- Limitar intentos de login fallidos.
- Mostrar bloqueo temporal explícito si aplica ("Demasiados intentos, vuelve a intentar en X minutos"), no fallar en silencio.
- Confirmar cierre de sesión solo cuando tenga sentido (ej. si hay cambios sin guardar) — no agregar un modal de confirmación a una acción de bajo riesgo y alta frecuencia.
- Avisar de sesiones expiradas con un mensaje claro antes de redirigir a login, no una redirección silenciosa que parece un bug.

> Detalle de implementación de seguridad (rate limiting, hashing, tokens) vive en `05_Security` (pendiente en el handbook) — esta sección es solo la experiencia que el usuario percibe.

---

## 14. Accesibilidad

**[REQUIRED]** Se aplica `FRONTEND_ENGINEERING_STANDARD.md` sección 13 completa, con énfasis en:

- Navegable 100% por teclado, incluido el toggle de mostrar/ocultar password.
- Labels asociados correctamente a cada input (9.4).
- Contraste AA en todo el formulario, incluidos los mensajes de error y los indicadores de requisitos de password.
- `focus-visible` en todos los campos y botones.
- Mensajes de error anunciables por lectores de pantalla (`aria-live` en el mensaje de error del formulario, `aria-describedby` por campo).

---

## 15. Catálogo de patrones de autenticación

Login es solo uno de varios patrones — no todos aplican a todos los productos, pero conviene decidir explícitamente cuáles necesita el proyecto antes de empezar:

| Patrón | Propósito |
|---|---|
| Login | Acceso con credenciales existentes |
| Register | Creación de cuenta nueva |
| Forgot Password | Punto de entrada para recuperar acceso perdido |
| Reset Password | Definir una nueva contraseña tras verificar identidad |
| Verify Email | Confirmar que el correo registrado es real y accesible por el usuario |
| Two-Factor Authentication (2FA) | Capa adicional de verificación — necesaria si el producto maneja datos sensibles (pagos, trading) |
| Magic Link | Login sin password, vía enlace de un solo uso al correo — reduce fricción a costa de depender de la entrega de email |
| Social Login | Login vía proveedor externo (Google, GitHub, Apple) |
| Session Expired | Aviso claro cuando la sesión caduca, con redirección a login |
| Change Password | Cambio de contraseña estando ya autenticado (distinto del flujo de recuperación) |
| Delete Account Confirmation | Confirmación explícita e irreversible-aware antes de eliminar una cuenta |
| Onboarding | Guía post-registro antes de llegar al producto real (sección 12) |

---

## Checklist rápido antes de dar por terminada una pantalla de auth

- [ ] ¿El layout corresponde al tipo de producto (Split Screen / Centered Card / Full Screen), no elegido al azar?
- [ ] ¿Un solo `<h1>`, un solo CTA primario?
- [ ] ¿Labels visibles, no solo placeholder?
- [ ] ¿Requisitos de password visibles antes del submit, no como error después?
- [ ] ¿Validación en tiempo real en campos con formato verificable?
- [ ] ¿Estados loading/error/éxito con copy específico de auth, sin errores técnicos crudos?
- [ ] ¿Social login debajo del formulario principal, nunca arriba?
- [ ] ¿Flujo de recuperación de contraseña completo, sin pantallas ambiguas?
- [ ] ¿Registro pide solo los campos indispensables?
- [ ] ¿No se revela si un correo existe o no, intentos limitados, sesión expirada avisada?
- [ ] ¿Navegable por teclado, contraste AA, `focus-visible`, errores anunciables por lector de pantalla?
