---
title: "Checklist Completo — App lista para producción (Apple, Google Play y Web)"
category: 06_Testing
doc_type: referencia
tags: [checklist, app-store, google-play, mobile, release, submission, produccion]
summary: "Catálogo exhaustivo de todo lo que una app necesita para pasar submission en App Store y Google Play, más web — funcional, compliance de tienda, seguridad y proceso. Distingue lo que un script puede verificar de lo que depende de revisión humana."
keywords: [app store, google play, submission, review, target-sdk, iap, privacy-manifest, account-deletion, closed-testing]
updated: 2026-09-14
status: VERIFIED
confidence: alta — hechos de plataforma verificados en fuentes oficiales en la fecha de arriba; las políticas de Apple/Google cambian sin aviso, revalidar antes de confiar en una fecha vieja
reviewed: false
sources:
  - "https://developer.android.com/google/play/requirements/target-sdk"
  - "https://support.google.com/googleplay/android-developer/answer/11926878"
  - "https://support.google.com/googleplay/android-developer/answer/14151465"
  - "06_Testing/CHECKLIST_RELEASE_PRODUCCION.md"
  - "07_DevOps/GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md"
---

# CHECKLIST DE APP STORE RELEASE — Apple, Google Play y Web

> **Relación con `CHECKLIST_RELEASE_PRODUCCION.md`:** ese documento cubre el release de un proyecto **web** (QA funcional, seguridad, performance). Este lo complementa para todo lo que aplica **cuando ese mismo producto también se distribuye como app nativa** — son requisitos de las tiendas, no de ingeniería de software, y por eso ningún checklist de QA genérico los cubre.
>
> **Regla de lectura obligatoria antes de usar esto como gate automático:** cada fila dice si hoy existe una herramienta real que la verifique sola, o si depende de un servicio pago o de juicio humano. No conviertas esto en un pipeline de 40 pasos "✅" donde la mitad son aspiracionales — eso ya nos costó una vez (`Engineering-OS/33-Feature-Completeness-Engine.md` documentó una herramienta que nunca se construyó). Arrancar con los 8-10 ítems marcados **[SCRIPT]** como gate real; el resto se revisa a mano antes de cada submission.

---

## 0. Antes de tocar cualquier checklist de tienda

**[SCRIPT]** El código que vas a subir está commiteado y pusheado — no en el disco de una sola máquina. Verificado con `git status --short` (vacío) y `git log origin/main..HEAD` (vacío). Sin esto, nada de lo que sigue importa: no hay "app lista" si el código que la compone puede desaparecer con un disco.

**[SCRIPT]** `typecheck` + tests unitarios/integración en verde, en el backend y en la app — ver `06_TEST_CHECKLIST.md` §3.

**Manual** — ¿la cuenta de Apple Developer / Google Play Console con la que vas a publicar es tuya o del cliente? Quién es el "legal owner" de la ficha en la tienda importa para soporte, pagos y qué pasa si termina la relación comercial. Decidirlo antes de crear la ficha, no después.

---

## 1. Funcional — QA que aplica a las tres plataformas

| Test | Qué comprueba | Cómo se verifica hoy |
|---|---|---|
| **Install** | Instala desde cero sin error | Manual en dispositivo real — un simulador/Expo Go no basta, hay diferencias de permisos y firma |
| **Launch** | Abre sin pantalla negra ni crash frío | Manual, dispositivo real |
| **Navigation** | Todos los botones/tabs/back/enlaces funcionan | [SCRIPT] E2E (Playwright/Detox) si existe suite; si no, manual completo |
| **Core Flow** | La función principal funciona de punta a punta con datos reales | Manual + [SCRIPT] si hay E2E — ver nota de "camino feliz no alcanza" en `06_TEST_CHECKLIST.md` §7 |
| **Authentication** | Registro/login/logout/reset/expiración de sesión | [SCRIPT] parcial (unit/integration del backend) + manual del flujo completo en la app real |
| **Account Deletion** | Ver sección 4 — tiene reglas propias por tienda, no es un ítem genérico | — |
| **API** | Endpoints responden bien y los errores se manejan (no crashea con un 500/timeout) | [SCRIPT] integration tests con error inyectado (route interception o mock del servidor) |
| **Offline/Network** | Sin internet no rompe ni queda congelada | Manual (modo avión) — difícil de automatizar de forma confiable en dispositivo real |
| **Permission** | Cámara/GPS/fotos/notificaciones piden permiso y manejan "Denegar" sin crashear | Manual — automatizar el diálogo nativo de permisos es frágil en CI |
| **Privacy** | Lo declarado en la ficha de la tienda coincide con lo que la app **realmente** recopila | Manual — cruzar el formulario de la tienda contra el código (ver sección 3 y 4) |
| **Payment** | Ver sección 5 — In-App Purchase tiene reglas propias, no es un ítem genérico | — |
| **Restore Purchase** | Restaurar compras/suscripciones al reinstalar o cambiar de dispositivo | Manual, solo si hay compras digitales reales (ver sección 5) |
| **Crash** | Navegación completa sin crashes | [SCRIPT] si hay Crashlytics/Sentry con umbral; si no, manual exhaustivo |
| **Freeze/ANR** | La interfaz nunca queda bloqueada (Android mide esto activamente, "Application Not Responding") | Manual + Play Console "Android Vitals" post-lanzamiento |
| **Device** | Varios tamaños/resoluciones/fabricantes | Manual — un servicio de device farm (Firebase Test Lab, BrowserStack) es lo único que lo hace barato a escala |
| **OS Version** | Última versión y la mínima soportada declarada | Manual en al menos 2 dispositivos reales (más viejo y más nuevo disponible) |
| **Notification** | Push en foreground/background y al tocar la notificación | Manual — **aplica siempre que `expo-notifications` (u otro SDK push) esté en las dependencias**, no es condicional a "si usa": revisar `package.json`, no la memoria de si "se usó" |
| **Deep Link** | Los links abren la pantalla correcta, no solo la home | Manual + [SCRIPT] si hay E2E con URL scheme |
| **Reviewer** | Cuenta demo funcional + backend real disponible durante la revisión | Manual — dejar credenciales y notas para el revisor en el campo de App Review Information / Play Console |
| **Store Metadata** | Screenshots, textos, URLs y políticas correctos y vigentes | Manual |

---

## 2. Seguridad — no es opcional, es lo primero que un atacante prueba

**[SCRIPT]** Auth bypass, IDOR (acceso a datos de otro usuario cambiando un ID en la URL/request), endpoints sin autenticar que deberían estarlo, tokens/secrets expuestos en el bundle cliente — ver `05_Security/SECURITY_ENGINEERING_STANDARD.md` y `05_Security/AUDIT_TOOLKIT_KALI_WSL.md` para las herramientas concretas (nmap, ffuf, nuclei) que sí existen y corren solas.

**[SCRIPT]** Escaneo de secretos en el bundle antes de publicar — un API key de servidor compilado dentro del `.ipa`/`.apk` es extraíble por cualquiera con el binario, distinto a un secreto en el backend.

---

## 3. Específico de Apple (App Store)

**Manual — Guideline 2.1, App Completeness:** Apple rechaza contenido de relleno, datos de ejemplo hardcodeados presentados como reales, o funciones "coming soon". Esto no es un bug de código, es un motivo de rechazo formal — auditar la app buscando específicamente cualquier dato que no venga del backend real (nombres de usuario fijos, precios hardcodeados, resultados fingidos).

**Manual — Guideline 4.8, Sign in with Apple:** si la app ofrece login con Google/Facebook/X como opción, Apple exige ofrecer también "Sign in with Apple" como alternativa equivalente. No aplica si el único login es con correo/teléfono y contraseña propios.

**[SCRIPT/CONFIG] Privacy Manifest:** desde 2024 Apple exige el archivo `PrivacyInfo.xcprivacy` declarando el motivo de uso de ciertas "Required Reason APIs" (UserDefaults, timestamps de archivos, etc.). Sin esto, App Store Connect puede rechazar el build directamente en validación automática, antes de llegar a un revisor humano. En Expo: `expo-build-properties` u otro config plugin según qué librería nativa dispare el requisito — verificar cuáles de las dependencias instaladas lo activan.

**Manual — Export Compliance:** en cada submission, App Store Connect pregunta si la app usa cifrado no exento. HTTPS estándar suele calificar como exento, pero la pregunta hay que responderla correctamente cada vez (o declararlo una vez en `Info.plist` con `ITSAppUsesNonExemptEncryption`).

**Manual — Reviewer access:** cuenta demo real + backend real funcionando durante la ventana de revisión. Si el backend está en modo mantenimiento o la cuenta demo expiró, el rechazo es automático y no es un problema de tu código.

**Obligatorio, no negociable:** URL de política de privacidad pública y accesible, más la sección de privacidad de App Store Connect ("App Privacy" / nutrition label) completada con precisión — debe reflejar los datos que la app **realmente** envía a terceros (analytics, crash reporting, ads), no una copia genérica.

---

## 4. Específico de Google Play

**[SCRIPT/CONFIG] Target API Level — verificado en fuente oficial (14 sep 2026):** a partir del **31 de agosto de 2026**, apps nuevas y actualizaciones deben apuntar a **Android 16 (API level 36)** o superior para poder subirse. Apps existentes necesitan al menos API 35 para seguir siendo visibles a usuarios nuevos en dispositivos con Android más reciente que el target de la app. Hay extensión disponible (solicitándola) hasta el **1 de noviembre de 2026**. Wear OS/Automotive: API 35 mínimo; Android TV/XR: API 34 mínimo.
Verificación real, no de memoria: `npx expo config --type public` (o el equivalente de tu build system) y confirmar `targetSdkVersion`/`compileSdkVersion` — **el default interno de las herramientas puede no coincidir con lo que la política exige**, hay que fijarlo explícito (ver `expo-build-properties` como patrón de referencia).

**Regla de gate sugerida para CI:**
```
targetSdk < 36  →  release bloqueado (o exención explícita documentada por qué)
```

**Manual/proceso — 12 testers, 14 días:** aplica **solo** a cuentas personales de Play Console creadas **después del 13 de noviembre de 2023**. Cuentas de organización o creadas antes de esa fecha no están sujetas. Si aplica: closed testing con mínimo 12 testers reales (no emuladores, no cuentas duplicadas) durante 14 días consecutivos, **antes** de poder solicitar acceso a producción. Esto es tiempo de calendario — ningún script lo acelera.

**Obligatorio — Account Deletion vía web:** además del borrado in-app, Google exige un método de solicitud de borrado de cuenta **accesible desde fuera de la app** (una URL pública), declarado en la ficha de Play Console. No alcanza con el botón dentro de la app.

**Obligatorio — Data Safety form:** formulario de Play Console declarando qué datos se recolectan, para qué y si se comparten con terceros — debe coincidir con el comportamiento real de la app (mismo principio que el "nutrition label" de Apple).

---

## 5. In-App Purchase / compras y suscripciones digitales

**Aplica si vendés contenido o funcionalidad digital dentro de la app** (cursos, premium, suscripciones tipo "$9.99/mes", desbloqueo de funciones). Si es un servicio del mundo físico (ej. una grúa que llega a tu ubicación), suele calificar como exento de IAP — pero **la decisión la toma el revisor de Apple viendo tu app**, no vos: documentar el razonamiento de por qué calificás como exento antes de someter, para poder responder rápido si el revisor pregunta.

Si aplica IAP real, el flujo mínimo a probar:

```
Purchase → Store verification → Backend verification → Entitlement → Restore purchase
```

Y estos casos, no solo el camino feliz (mismo principio de `06_TEST_CHECKLIST.md` §7, aplicado a pagos):
- [ ] Compra exitosa
- [ ] Compra cancelada por el usuario
- [ ] Compra pendiente (ej. método de pago que requiere aprobación)
- [ ] Pago duplicado / doble tap en el botón de compra
- [ ] Restore en un dispositivo nuevo
- [ ] Suscripción expirada
- [ ] Suscripción renovada
- [ ] Refund / revocación iniciada desde la tienda

**Nunca** fingir una compra exitosa en el cliente sin la confirmación real del servidor de la tienda — mismo principio que ya está en el prompt maestro del usuario: ningún código finge éxito para evitar mostrar un error.

---

## 6. OTA / actualizaciones sin pasar por la tienda

Si el stack soporta actualizar JS sin republicar el binario (EAS Update, CodePush u equivalente): probar que una actualización mala se puede **revertir** sin depender de una nueva revisión de tienda. Un update que rompe el core flow y no se puede deshacer rápido es un incidente de producción sin el rollback normal de un deploy web.

---

## 7. Rendimiento bajo carga (no está en los checklists de QA típicos)

**[SCRIPT]** Cuántas requests concurrentes aguanta el backend antes de degradar — relevante especialmente en features de "tiempo real" (ubicación, matching, tracking) donde la lógica de negocio es sensible a latencia. No es un requisito de tienda, es un requisito de que el "Core Flow" siga siendo cierto con más de un usuario a la vez.

---

## 8. Accesibilidad (no obligatorio para submission, sí para calidad real)

VoiceOver (iOS) y TalkBack (Android) pueden completar el flujo principal sin quedar atascados. Ninguna tienda lo exige como gate de submission hoy, pero Apple lo pondera cada vez más en revisiones de apps con audiencia amplia, y es la misma exigencia que ya vive en `01_Frontend/FRONTEND_ACCESSIBILITY_ADVANCED.md` para la versión web del mismo producto — no hay razón para que la versión nativa tenga un estándar menor.

---

## 9. Lo que ningún script te puede garantizar

Pasar todo lo de arriba en verde reduce los rechazos **técnicos** a casi cero. No garantiza la aprobación, porque una parte real de la revisión es juicio humano:

- Que el revisor considere que la app "aporta valor real" y no parece una plantilla genérica (Apple Guideline 4.3 — subjetivo, no medible por máquina).
- Que tu clasificación de "servicio físico exento de IAP" (sección 5) sea la que el revisor acepte.
- Que tus screenshots y descripción coincidan exactamente con lo que el revisor prueba a mano.
- Heurísticas antifraude/antispam de Google, no publicadas, que cambian sin aviso.

**Consecuencia de planeación, no de código:** presupuestar al menos un ciclo de rechazo-y-reenvío como parte normal del cronograma, no como contingencia. En Google, si el gate de 12 testers/14 días aplica, eso es tiempo de calendario que ningún pipeline acelera — planificarlo con 2+ semanas de anticipación a la fecha de lanzamiento deseada.

---

## 10. Versionado de builds — obligatorio, Apple y Google Play

Hay **dos números distintos** en juego y confundirlos es la causa más común de un submit rechazado por algo que no tiene nada que ver con la calidad de la app:

### El número de build tiene que ser SIEMPRE mayor al anterior, sin excepción

- **Apple (`CFBundleVersion` / build number):** cada build que subís a App Store Connect necesita un número **estrictamente mayor** que cualquier build subido antes para esa app — no alcanza con que sea distinto, no puede repetirse ni bajar, y esto es independiente de a qué versión "marketing" (1.0.0, 1.1.0, etc.) pertenezca. Subir un build con el mismo número que uno anterior, o uno menor, se rechaza automáticamente en la subida — ni siquiera llega a revisión.
- **Google Play (`versionCode`):** misma regla, más estricta todavía — tiene que subir en **cada** subida a Play Console, incluida entre builds que solo van a testing interno. No hay forma de reusar ni de "saltar hacia atrás" un versionCode ya usado, ni siquiera si borrás el release.

**Con EAS Build, esto se resuelve solo** si `eas.json` tiene `"cli": { "appVersionSource": "remote" }` y el perfil de build tiene `"autoIncrement": true` — el número de build se pide y se incrementa automáticamente contra los servidores de EAS en cada build (`2 → 3 → 4 → ...`), sin que haga falta tocarlo a mano. Si ves un build fallar por número de versión duplicado/menor, lo primero a revisar es si algo pisó esa config (por ejemplo, fijar el número a mano en `app.json` en vez de dejarlo en `"remote"`).

### Qué significa cada número de la versión "de marketing" (la que ve el usuario)

La versión visible (`1.0.0`, la que aparece en la ficha de la tienda) sigue, en general, la convención **[Semantic Versioning](https://semver.org/)**: `MAJOR.MINOR.PATCH`.

| Posición | Nombre | Cuándo se sube |
|---|---|---|
| `1`.0.0 | MAJOR | Cambios grandes/incompatibles, un relanzamiento, un rediseño de fondo |
| 1.`0`.0 | MINOR | Funcionalidad nueva, compatible con lo anterior (agregaste una pantalla, un flujo nuevo) |
| 1.0.`0` | PATCH | Solo corrección de errores, sin funcionalidad nueva |

**Sobre el cuarto número que preguntaste (tipo `1.0.0.1` o `1.2.0.0`):** no es parte del estándar SemVer ni tiene un significado que Apple o Google exijan — es una convención informal que algunos equipos agregan como `MAJOR.MINOR.PATCH.BUILD`, pegando el número de build al final de la versión de marketing para tener todo en un solo string legible. **Las tiendas no lo leen ni lo validan** — a Apple y Google les importa únicamente el campo de build number/versionCode por separado (ver arriba), no cuántos puntos tiene el string de versión de marketing. Si tu equipo no tiene ya esa convención en uso, no hace falta inventarla: alcanza con `MAJOR.MINOR.PATCH` de marketing + el build number autoincrementado por separado.

### Después de que el build quede APROBADO en la tienda (no antes): avisar a los usuarios viejos

La app mobile (`components/ui/UpdateBanner.tsx`) compara su propio `app.json#version` contra `GET /api/app/latest-version` y muestra "Actualización disponible" si el backend dice que hay una versión mayor. Ese valor NO se auto-detecta (no hay API pública confiable de "última versión publicada", sobre todo en Android) — se actualiza a mano:

```bash
npx wrangler d1 execute gruas-prod --remote --command \
  "UPDATE app_config SET value='1.1.0', updated_at=datetime('now') WHERE key='latest_version_ios'; \
   UPDATE app_config SET value='1.1.0', updated_at=datetime('now') WHERE key='latest_version_android';"
```

Hacerlo ANTES de que Apple/Google terminen de aprobar el build manda a los usuarios viejos a la tienda a buscar una versión que todavía no existe ahí.

---

## Checklist final — arrancar por acá, no por la lista completa

- [ ] Código commiteado y pusheado (sección 0)
- [ ] `targetSdkVersion`/`compileSdkVersion` ≥ 36 fijado explícito, no confiado al default de la herramienta (sección 4)
- [ ] Cero contenido de relleno / datos fingidos en pantallas que un revisor va a ver (sección 3)
- [ ] Privacy Manifest presente si alguna dependencia lo dispara (sección 3)
- [ ] Política de privacidad pública y accesible + formularios de privacidad de ambas tiendas completados con precisión (secciones 3 y 4)
- [ ] Método de borrado de cuenta in-app **y** vía web si publicás en Play (sección 4)
- [ ] Número de build estrictamente mayor al último subido (`appVersionSource: remote` + `autoIncrement: true` en EAS, o equivalente) — nunca igual ni menor (sección 10)
- [ ] Decisión documentada sobre exención de IAP si hay contenido digital de pago (sección 5)
- [ ] Cuenta demo + backend real disponibles para el reviewer (sección 3)
- [ ] Si aplica el gate de 12 testers de Google: arrancado con semanas de margen, no la semana del lanzamiento (sección 4)
