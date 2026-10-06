---
title: "Playbook: Compilar y Publicar iOS en TestFlight sin Mac (Expo/React Native)"
category: 07_DevOps
doc_type: runbook
tags: [ios, testflight, expo, eas, github-actions, apns, export-compliance, code-signing, incident]
summary: "Playbook operativo para compilar, firmar y subir apps Expo/React Native a TestFlight desde Linux (sin Xcode local), con dos pipelines (GitHub Actions self-hosted en runner macOS, y EAS Build/Submit), y el diagnóstico de 6 incidentes reales encontrados en producción: bug de descifrado E2EE en CryptoKit, crash por dependencia duplicada de Expo, error 90592 de cumplimiento de exportación, migración de notificaciones del relay de Expo a APNs nativo, bloqueo de facturación de GitHub Actions, y colisión de número de build entre dos pipelines paralelos."
keywords: [ios, testflight, expo, eas-build, eas-submit, apple-developer, provisioning-profile, distribution-certificate, apns, export-compliance, 90592, expo-modules-core, cryptokit, app-store-connect-api-key, wrangler, cloudflare-worker, build-number]
updated: 2026-09-10
status: current
sources:
  - "Sesión real de shipping de LoveChat (app.online.jcdigital.jeliangel), 2026-09-09/10"
  - "Expo Docs — EAS Build/Submit (docs.expo.dev)"
  - "Apple Developer — Complying with Encryption Export Regulations"
  - "Apple Developer — App Store Connect API"
---

# Playbook: Compilar y Publicar iOS en TestFlight sin Mac

Contexto que resuelve este documento: desarrollas una app Expo/React Native en Linux (o cualquier máquina sin Xcode) y necesitas compilar un binario firmado de iOS y subirlo a TestFlight. No existe una vía soportada por Apple para compilar/firmar IPAs en Linux — el toolchain de Xcode (`xcodebuild`, `codesign`, `actool`) solo corre en macOS. Hay dos formas de resolverlo sin comprar un Mac, y este documento cubre ambas más los incidentes reales que produjeron al usarlas.

---

## 1. Las dos vías: runner macOS propio vs. EAS Build

| | GitHub Actions (`runs-on: macos-*`) | EAS Build + Submit (Expo) |
|---|---|---|
| Dónde compila | Runner macOS de GitHub, tú controlas cada paso de `xcodebuild` | Infraestructura de Expo en la nube, tú no ves el `xcodebuild` |
| Costo | Minutos de Actions — los runners macOS cuestan ~10x un runner Linux; se agota la facturación rápido si compilas seguido | Plan gratis: 15 builds iOS/mes, 1 concurrente, cola de baja prioridad (revisar https://expo.dev/pricing para cifras vigentes) |
| Gestión de credenciales | Manual: tú generas y subes `.p12`/`.mobileprovision`/`.p8` como secretos, y escribes cada paso de `security`/`PlistBuddy` | `eas credentials` gestiona certificado y provisioning profile automáticamente contra la Apple Developer API |
| Requiere login de Apple ID | No (solo API Key de App Store Connect) | Sí, la primera vez que genera credenciales de firma (ver sección 4) |
| Control fino | Total — cada línea de `xcodebuild` es tuya | Limitado — dependes de lo que EAS decida hacer |
| Cuándo usarla | Ya tienes el pipeline armado y quieres control total, o EAS no cubre algo específico | Setup nuevo, o quieres velocidad de iteración sin pelear con `xcodebuild` |

**Recomendación por defecto:** si el proyecto no tiene ya un pipeline de GitHub Actions maduro, empezar por EAS — el tiempo de configuración es menor y no depende de gestionar manualmente certificados. Mantener ambos en paralelo es posible pero introduce el incidente de la sección 6.6 (colisión de número de build) si no se sincronizan.

---

## 2. Requisitos previos (aplican a ambas vías)

1. **Apple Developer Program** activo (99 USD/año), Individual o de Organización.
2. **App ID / Bundle Identifier** registrado en Apple Developer, con las *capabilities* correctas habilitadas (ej. Push Notifications) **antes** de generar cualquier provisioning profile — un profile generado con una capability faltante no se puede "arreglar" después, hay que regenerarlo.
3. **App Store Connect API Key** — reemplaza el login interactivo de Apple ID para automatización:
   - Se genera en App Store Connect → Users and Access → Integrations → Keys (**no confundir con la sección de Keys del portal developer.apple.com, que es para APNs — ver sección 5**).
   - Rol mínimo `Developer` si solo se usa para subir builds (GitHub Actions con `altool`); rol `Admin` si además va a gestionar certificados/perfiles (EAS Build).
   - Descarga el `.p8` en el momento de crearla — Apple **no permite volver a descargarla después**.
4. **Certificado de distribución (`.p12`) y Provisioning Profile de App Store (`.mobileprovision`)** — solo necesarios para la vía GitHub Actions; EAS los gestiona solo.

---

## 3. Vía A — GitHub Actions con runner macOS

### 3.1. Secretos requeridos

| Secreto | Descripción |
|---|---|
| `APPLE_TEAM_ID` | ID de equipo (10 caracteres), extraíble del provisioning profile con `security cms -D -i perfil.mobileprovision \| grep -A1 TeamIdentifier` (o `openssl smime -verify -noverify -inform DER` en Linux, sin necesidad de `security` de macOS). |
| `IOS_DISTRIBUTION_CERTIFICATE_BASE64` / `_PASSWORD` | `.p12` en base64 (`base64 -w 0 archivo.p12`) + la contraseña puesta al exportarlo. **Guarda esta contraseña en un gestor de contraseñas al momento de crearla** — si se pierde, el `.p12` ya no sirve para nada (ni para reimportarlo en otra herramienta) y hay que generar un certificado nuevo. |
| `IOS_APP_STORE_PROFILE_BASE64` | `.mobileprovision` en base64. |
| `APP_STORE_CONNECT_ISSUER_ID` / `_KEY_ID` / `_PRIVATE_KEY_BASE64` | De la API Key de la sección 2.3, rol `Developer` basta. |

### 3.2. Pasos del pipeline

1. Decodificar `.p12` y `.mobileprovision`, crear un keychain temporal (`security create-keychain`), importar el certificado, y copiar el profile a `~/Library/MobileDevice/Provisioning Profiles/<UUID>.mobileprovision`.
2. `npx expo prebuild --platform ios --non-interactive --no-install` seguido de `pod install`.
3. Inyectar el número de build (`CFBundleVersion`) desde una variable que solo el CI conoce (ej. `$GITHUB_RUN_NUMBER`) — **nunca reutilizar un número ya subido** (ver incidente 6.6).
4. `xcodebuild ... archive` → `xcodebuild -exportArchive` con un `ExportOptions.plist` de método `app-store`.
5. Colocar el `.p8` exactamente en `~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8` con `chmod 600` — `altool` falla en autenticación si no está en esa ruta exacta con ese nombre exacto.
6. `xcrun altool --upload-app --type ios --file app.ipa --apiKey <KEY_ID> --apiIssuer <ISSUER_ID>`.

### 3.3. Fallos típicos de esta vía (síntoma → causa → fix)

- **Exit 65 en el archive**, error `doesn't include the Push Notifications capability` / `doesn't include the aps-environment entitlement` → el config plugin de `expo-notifications` inyectó `aps-environment` en el binario, pero el provisioning profile se generó **antes** de habilitar esa capability en el App ID. Fix: habilitar la capability en el App ID, regenerar el profile, volver a subir el secreto en base64.
- **`altool` falla en autenticación** sin mensaje claro → revisar que el `.p8` esté en la ruta y con el nombre exacto que exige la herramienta, con permisos `600`.
- **Rechazo por versión de build duplicada/inferior** → Apple no permite reutilizar el mismo `CFBundleVersion` dos veces para la misma versión de app; automatizar el incremento con un contador que nunca reinicie hacia atrás.

---

## 4. Vía B — EAS Build + Submit

### 4.1. Configuración mínima de `eas.json`

```json
{
  "cli": { "version": ">= 23.0.0", "appVersionSource": "remote" },
  "build": {
    "<perfil>": { "distribution": "store", "autoIncrement": true }
  },
  "submit": {
    "<perfil>": {
      "ios": {
        "ascAppId": "<Apple ID numérico de la app en App Store Connect — NO es el bundle id>",
        "ascApiKeyPath": "/ruta/fuera/del/repo/AuthKey_XXXXXXXXXX.p8",
        "ascApiKeyId": "XXXXXXXXXX",
        "ascApiKeyIssuerId": "uuid-del-issuer"
      }
    }
  }
}
```

**Regla dura de seguridad:** `ascApiKeyPath` nunca debe apuntar a un archivo dentro del repositorio git. Guardar las credenciales de Apple/EAS en una carpeta fuera de cualquier repo (ver plantilla en sección 7) y referenciarla por ruta absoluta.

### 4.2. Login y generación de credenciales (requiere intervención humana, no automatizable por un agente)

```bash
npx eas-cli login                     # OAuth de Expo, vía navegador
npx eas-cli credentials:configure-build --platform ios --profile <perfil>
```

El segundo comando pregunta *"Do you want to log in to your Apple account?"*. Si el proyecto nunca tuvo credenciales de build gestionadas por EAS, **responder que sí es inevitable** — EAS necesita autenticarse contra la Apple Developer API para crear el certificado de distribución y el provisioning profile, y eso requiere Apple ID + contraseña + 2FA. Una API Key de App Store Connect (aunque sea rol Admin) **no sustituye** este login para la creación de credenciales de firma.

> **[REQUIRED] Un agente/asistente de IA nunca debe escribir el Apple ID ni la contraseña en este prompt.** Es la persona dueña de la cuenta quien debe teclearlos directamente en su propia terminal. La sesión queda cacheada localmente (`~/.app-store/auth/<email>/cookie`) tras el primer login, así que los reintentos posteriores no vuelven a pedir contraseña — solo confirman la sesión existente.

Tras el login: aceptar "Generate a new Apple Distribution Certificate?" solo si no existe uno reutilizable con contraseña conocida; aceptar "Generate a new Apple Provisioning Profile?" para que combine con el certificado activo.

**Nota de fricción conocida de la CLI:** en `eas build:version:set`, el prompt de texto para el número de versión puede traer un valor por defecto precargado con el cursor posicionado *antes* del texto (no al final). Si se automatiza este comando (ej. vía `pexpect`), mover el cursor al final del campo y borrar hacia atrás antes de escribir el valor nuevo — escribir directamente puede insertarse *antes* del default y producir un número corrupto (ej. escribir "26" sobre un default "78" da "2678", no "26").

### 4.3. Comandos operativos

```bash
# Build + submit a TestFlight en un solo paso
npx eas-cli build --platform ios --profile <perfil> --non-interactive --auto-submit

# Ver o fijar manualmente el contador remoto de build number
npx eas-cli build:version:get --platform ios --profile <perfil>
npx eas-cli build:version:set --platform ios --profile <perfil>
```

---

## 5. Notificaciones Push: por qué "Expo" y "nativo" no son excluyentes

Confusión frecuente: *"si no uso `eas build`, ¿por qué mis notificaciones pasan por Expo?"*. Son dos cosas independientes:

- **EAS Build** = el servicio de compilación en la nube. Se puede evitar (vía A de este documento) sin dejar de usar el SDK de Expo.
- **`expo-notifications` con `getExpoPushTokenAsync()`** = una función que **siempre** enruta a través del relay `exp.host` de Expo, sin importar qué herramienta compiló el binario. Es una decisión de la librería, no del pipeline de build.

**Riesgo:** si el proyecto nunca corrió `eas build`, es probable que Expo no tenga una APNs Auth Key configurada para ese bundle ID — las notificaciones se "aceptan" en el relay pero mueren silenciosamente antes de llegar al dispositivo, sin ningún error visible del lado del cliente ni del servidor.

**Fix para tener push 100% nativo (sin depender de infraestructura de terceros):**
1. Cliente: usar `Notifications.getDevicePushTokenAsync()` en vez de `getExpoPushTokenAsync()` — da el token nativo de APNs directamente, sin pasar por Expo ni necesitar `projectId` de EAS.
2. Backend: firmar un JWT ES256 con una **APNs Auth Key** (`.p8` generado en developer.apple.com → Certificates, Identifiers & Profiles → **Keys** — sección distinta a la API Key de App Store Connect de la sección 2.3) y llamar directo a `https://api.push.apple.com/3/device/<token>`.
   - Claims del JWT: `{ iss: <Team ID>, iat: <epoch actual> }`, header `{ alg: "ES256", kid: <Key ID de la APNs key> }`.
   - En runtimes con Web Crypto (Cloudflare Workers, Deno, navegador): `crypto.subtle.sign({name:'ECDSA', hash:'SHA-256'}, key, ...)` devuelve la firma ya en formato raw `r‖s` — es exactamente el formato que exige JWS ES256, no requiere reempaquetar desde DER.
   - En Node: `crypto.sign('sha256', data, { key, dsaEncoding: 'ieee-p1363' })` da el mismo formato raw directamente.
   - Cachear el JWT en memoria (proceso/isolate) y reutilizarlo ~40-50 minutos — Apple pide no generarlo en cada request.
3. **Una misma APNs Auth Key sirve para todas las apps de la cuenta de Apple Developer** (a diferencia del certificado de distribución y el provisioning profile, que son específicos de un bundle ID) — para reutilizarla en otro proyecto solo cambia el `apns-topic` (el bundle ID) en cada request.

---

## 6. Catálogo de incidentes reales (síntoma → causa raíz → fix)

Diagnosticados en una sola sesión de shipping de una app Expo/React Native (chat E2EE con módulo nativo Swift + CryptoKit). Se documentan porque cada síntoma, por sí solo, es engañoso — parece un problema distinto del que realmente es.

### 6.1. Descifrado E2EE roto al 100% (síntoma: mensajes propios bien, entrantes nunca)

Si una app de mensajería E2EE muestra el placeholder de "no se pudo descifrar" para **absolutamente todo** mensaje entrante, de cualquier remitente, y esto persiste tras cerrar/reabrir la app o resincronizar sesión — **no es un problema de sincronización de claves**, es un bug determinista en la función de descifrado. Un bug de sincronización de claves produciría fallos intermitentes o específicos de un dispositivo, no un 100% de fallo reproducible desde el primer mensaje.

- **Causa raíz encontrada:** la función de descifrado nativa (Swift/CryptoKit) derivaba la clave pública efímera del remitente a partir de un segmento del nonce (que en realidad era el *salt* de HKDF, de 16 bytes) en vez de usar el parámetro explícito que sí traía la clave real (32 bytes). El framework de criptografía rechazaba la clave por tamaño inválido.
- **Cómo se diagnosticó sin acceso al dispositivo real:** se reimplementó el protocolo de cifrado completo (intercambio de claves + derivación + cifrado simétrico) en un script standalone en el lenguaje del backend/herramientas disponibles, usando librerías criptográficas puras (sin SDK nativo), para actuar como "segundo dispositivo" contra el backend real. Ese script sí lograba descifrar los mensajes reales de la app — lo que aisló el bug a la implementación nativa específica, no al protocolo ni al intercambio de claves.
- **Fix:** una corrección de una línea (usar el parámetro correcto en vez del segmento equivocado del string). Requiere un build nativo nuevo — no se resuelve reabriendo la app ni con hot-reload de JS.

### 6.2. Crash inmediato al abrir, sin ningún error visible

Si una app crashea **antes** de que el motor de JS (Metro/Hermes) tenga oportunidad de renderizar nada — por lo que ni siquiera aparecen logs de Metro — el problema está en la capa nativa, no en el JS.

- **Causa raíz encontrada:** se agregó un paquete que es dependencia transitiva del framework (en este caso `expo-modules-core`, transitiva de `expo`) como dependencia **directa** en el `package.json`, en el mismo commit que agregó un módulo nativo custom. Esto compila dos copias del núcleo nativo dentro del mismo binario — símbolos/clases duplicadas que crashean el proceso al lanzar.
- **Cómo se diagnosticó:** herramientas de auditoría de dependencias del framework (`npx expo-doctor` en el caso de Expo) marcan exactamente este patrón como error, con la recomendación explícita de removerlo.
- **Fix:** quitar la dependencia directa, usar la API re-exportada desde el paquete padre en los imports que la necesitaban.
- **Generalización:** cualquier vez que se agregue un módulo nativo custom que declare una dependencia nativa compartida con el framework (ej. `ExpoModulesCore`, `React-Core`), verificar que esa dependencia **no** se declare también como paquete JS directo — debe resolverse por transitividad desde el framework, nunca fijarse aparte.

### 6.3. Error de "Export Compliance" al subir a TestFlight (código 90592 en Apple, aplica a cualquier binario firmado con `altool`)

Mensaje típico: *"Invalid Export Compliance Code. The export compliance key value [] in the app's Info.plist doesn't match the key value of the app's export compliance documentation."*

- **Lo que NO es la causa (trampa común):** este error **no** se resuelve completando el cuestionario "App Encryption Documentation" en App Store Connect (App Information → App Encryption Documentation) si la app ya venía subiendo builds con `usesNonExemptEncryption: false`. Ese cuestionario puede confirmar "no necesitas subir documentos" y el error 90592 persiste igual.
- **Causa raíz real:** la clave `ITSEncryptionExportComplianceCode` en el `Info.plist` solo tiene sentido cuando Apple **ya tiene un documento de cumplimiento archivado con un código específico** para esa app (normalmente generado la primera vez que se sube un build manualmente desde Xcode Organizer, donde Xcode gestiona esta pregunta de forma transparente). Si ese registro no existe, inyectar cualquier valor (vacío o inventado) en esa clave rompe la subida.
- **Fix pragmático cuando no se puede conseguir el código real de inmediato:** declarar `usesNonExemptEncryption: false` (o el equivalente `ITSAppUsesNonExemptEncryption` en Info.plist) para desbloquear la subida — **con la advertencia de que esto es una declaración legal potencialmente inexacta** si la app sí implementa cifrado propio (E2EE, cifrado de payloads) más allá de TLS estándar. Queda como deuda técnica/legal explícita, no una solución final.
- **Camino correcto a mediano plazo:** conseguir el código de cumplimiento real haciendo al menos un archive+upload manual desde Xcode Organizer (requiere Mac o servicio de Mac en la nube), que gestiona esta negociación con Apple automáticamente la primera vez.

### 6.4. Notificaciones push que "llegan a Expo" pero no al dispositivo

Ver sección 5 completa — el resumen: `getExpoPushTokenAsync()` siempre pasa por el relay de Expo independientemente del pipeline de build usado, y sin una APNs key configurada en Expo para ese bundle ID, las notificaciones mueren silenciosamente. Migrar a `getDevicePushTokenAsync()` + entrega directa a APNs si se quiere cero dependencias de terceros.

### 6.5. Bloqueo de facturación de CI a mitad de una sesión de shipping intensiva

- **Síntoma:** un job de GitHub Actions no llega ni a iniciar (`0s`), con la anotación *"The job was not started because recent account payments have failed or your spending limit needs to be increased."*
- **Causa probable:** runners macOS consumen minutos de Actions a una tasa varias veces mayor que runners Linux estándar; varias compilaciones de iOS seguidas en una misma sesión pueden agotar un límite de gasto configurado sin previo aviso visible en el propio workflow.
- **No es resoluble desde el código** — requiere entrar a la configuración de facturación de la cuenta/organización de GitHub.
- **Mitigación estructural:** tener un pipeline alternativo que no dependa de los minutos de GitHub Actions (EAS Build, sección 4) para no bloquear el shipping completo ante este tipo de corte.

### 6.6. Colisión de número de build entre dos pipelines de CI en paralelo

- **Síntoma:** un build subido por un pipeline nuevo (ej. EAS) queda "por debajo" en la lógica de versión de TestFlight de builds subidos antes por otro pipeline (ej. GitHub Actions), **aunque se haya subido cronológicamente después** — Apple no lo rechaza, pero TestFlight sigue mostrando/recomendando el build con número más alto, no el más reciente en el tiempo.
- **Causa raíz:** cada pipeline puede mantener su **propio contador de build number**, completamente desacoplado uno del otro. Un pipeline propio típicamente deriva el número de una variable del sistema de CI (ej. el número de ejecución del workflow); un pipeline gestionado (como EAS con `"appVersionSource": "remote"`) mantiene su contador en sus propios servidores. Ninguno de los dos sabe del otro.
- **Diagnóstico:** consultar directamente la API de App Store Connect (`GET /v1/builds?filter[app]=<id>&sort=-version`, autenticado con JWT ES256 firmado por la API Key de App Store Connect) para encontrar el número de build más alto realmente subido, sin depender de lo que cualquiera de los dos pipelines "cree" que es el último.
- **Fix:** adelantar manualmente el contador del pipeline más nuevo por encima del máximo real encontrado (en EAS: `eas build:version:set`).
- **Regla operativa:** si se usan dos pipelines en paralelo de forma sostenida (no solo durante una migración), sincronizar el contador después de cada tanda de builds del "otro" pipeline, o — mejor — desactivar uno de los dos para eliminar la clase de bug por completo.

---

## 7. Plantilla de índice de credenciales (fuera del repositorio)

Ningún valor real de certificado, clave privada o API Key vive nunca dentro de un repositorio git — ni siquiera en un `.gitignore`d local, por el riesgo de un `git add -A` accidental. Consolidar todas las credenciales de una cuenta de Apple Developer (reutilizables entre proyectos distintos que compartan la misma cuenta) en una carpeta fuera de cualquier repo, con permisos restrictivos (`700` en el directorio, `600` en cada archivo), y un índice como este:

```markdown
# Apple Developer credentials (cuenta: <email>)

## App Store Connect API Keys (reutilizables en cualquier app de la cuenta)
Issuer ID: <uuid>
| Archivo | Key ID | Rol | Uso |
|---|---|---|---|
| AuthKey_XXXX.p8 | XXXX | Developer | CI propio (GitHub Actions, etc.) |
| AuthKey_YYYY.p8 | YYYY | Admin | EAS (build + submit) |

## APNs Auth Key (reutilizable en cualquier app de la cuenta — cambia solo el bundle id/topic)
Team ID: <team-id>
| Archivo | Key ID | Uso |
|---|---|---|
| AuthKey_ZZZZ.p8 | ZZZZ | Push nativo directo, firma JWT ES256 |

## <Nombre de la app> — firma específica (NO reutilizable en otras apps)
- certificado.p12 — contraseña: <dónde está guardada, o "perdida, ver nota">
- perfil.mobileprovision — bundle id: <bundle-id>
```

**Por qué separar "reutilizable" de "específico de la app":** una API Key de App Store Connect y una APNs Auth Key son propiedades de la **cuenta**, no de la app — la misma key sirve para IndexGenius, LoveChat, o cualquier otro proyecto bajo la misma cuenta de Apple Developer, cambiando solo el identificador de la app en la configuración de cada proyecto. El certificado de distribución y el provisioning profile, en cambio, están atados a un bundle ID específico y no se pueden reutilizar.
