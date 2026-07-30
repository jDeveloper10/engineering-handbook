---
title: "Estándar de Seguridad en Aplicaciones Móviles (Android / APK)"
category: 05_Security
doc_type: estandar
tags: [seguridad, mobile, android, apk, react-native, expo, keystore, tls, ota, biometria]
summary: "Reglas de seguridad MSEC-001 a MSEC-012 para apps Android: cero secretos en el bundle, firma del APK/AAB y Play App Signing, Network Security Config y TLS, almacenamiento respaldado por Keystore, superficie exportada y App Links verificados, WebView, R8, Play Integrity, biometría, OTA firmado y permisos mínimos."
keywords: [android, apk, aab, keystore, apksigner, network-security-config, cleartext, certificate-pinning, expo-secure-store, encryptedsharedpreferences, exported, app-links, assetlinks, webview, r8, proguard, hermes, play-integrity, root-detection, biometric, eas-update, code-signing, jadx, apktool]
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "Android Developers — App security best practices / Network security configuration"
  - "Android Developers — Sign your app, Play App Signing, android:exported requirements (API 31+)"
  - "Android Developers — Jetpack Security (EncryptedSharedPreferences), BiometricPrompt"
  - "Google Play — Play Integrity API documentation"
  - "OWASP Mobile Application Security Verification Standard (MASVS) v2.0"
  - "Expo Documentation — Environment variables (EXPO_PUBLIC_), SecureStore, EAS Update code signing"
updated: 2026-07-29
---

# ESTÁNDAR DE SEGURIDAD MÓVIL / APK (MSEC-001 a MSEC-012)

> **Nivel 2 del dominio Security.** Hereda todo de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) — las 7 capas siguen aplicando íntegras al backend que la app consume. Este documento agrega lo que **solo existe cuando tu código viaja dentro de un APK que cualquiera puede descargar**.
>
> **Complementa** a [MOBILE_ENGINEERING_STANDARD.md](../01_Frontend/Core/MOBILE_ENGINEERING_STANDARD.md) (`MOB-001` a `MOB-006`), que define *cómo se construye* la app. Este define *qué la mantiene segura*. Ante conflicto, manda este documento.
>
> **Capa 1 (la regla) es Android**, no un framework: firma, manifiesto, configuración de red, Keystore y componentes exportados existen igual en Kotlin nativo, Flutter o React Native, porque son de plataforma. **Capa 2 (implementación) es React Native + Expo**, el stack de referencia del handbook. Si un proyecto sale del *managed workflow*, la capa 1 sigue vigente sin cambios.

---

## EL CAMBIO DE MODELO: UN APK ES CÓDIGO PUBLICADO

Un APK instalado se copia del dispositivo, se descomprime y se descompila. `apktool` devuelve el manifiesto y los recursos; `jadx` devuelve Java legible; en React Native, `index.android.bundle` es JavaScript que se lee con un editor de texto. Hermes cambia el formato, no el hecho: existen decompiladores de bytecode Hermes.

Consecuencia directa, sin matices:

```
Todo lo que va dentro del APK es PÚBLICO.
Todo lo que el APK puede enviar, un atacante lo puede enviar.
Todo lo que la app decide localmente, un atacante lo puede cambiar.
```

Las fronteras reales:

```
Frontera 1: Backend ←→ App          → el backend NUNCA confía en la app     ← la que de verdad protege
Frontera 2: App ←→ Otras apps del SO → intents, deep links, providers exportados
Frontera 3: App ←→ Dispositivo       → disco compartido, backups, root, pantalla, portapapeles
Frontera 4: App ←→ Red               → Wi-Fi hostil, proxy de intercepción, DNS manipulado
```

**Lo que este documento NO promete:** que la app sea inanalizable en un dispositivo rooteado. Eso es imposible y perseguirlo desperdicia el presupuesto de seguridad. Lo que sí garantiza: que comprometer el dispositivo de un usuario **no comprometa a los demás usuarios ni al backend**.

---

## REGLAS INQUEBRANTABLES

### MSEC-001: Cero secretos en el APK — `EXPO_PUBLIC_` significa público, literalmente

**[REQUIRED]** El bundle no contiene ninguna credencial que otorgue privilegios: ni claves de API de terceros con costo o alcance de escritura, ni `service_role`, ni secretos de firma, ni claves de cifrado fijas. Cualquier operación que requiera un secreto se hace en el backend, y la app llama a **tu** endpoint autenticado.

**Por qué:** extraer un string de un APK cuesta un comando. Es el mismo principio de `DSEC-004` en desktop, agravado porque el APK se distribuye masivamente: un secreto filtrado aquí lo tienen miles de personas a la vez. Ofuscar no ayuda — el secreto tiene que estar en claro en el momento de usarse, y ahí se captura.

```bash
# Verificación obligatoria antes de publicar
unzip -p app-release.apk assets/index.android.bundle | grep -inE "sk_live|service_role|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}"
```

**IMPLEMENTACIÓN (Expo):**

```javascript
// ✅ Solo valores que ya son públicos por diseño
// EXPO_PUBLIC_* se INLINEA en el bundle en tiempo de build. No es "de entorno": es una constante pública.
const apiUrl = process.env.EXPO_PUBLIC_API_URL           // ok: la URL es pública
const anonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY // ok: diseñada para el cliente y respaldada por RLS (S-010)
```

```javascript
// ❌ ANTI-PATRÓN: secreto real detrás de un prefijo público
const stripeSecret = process.env.EXPO_PUBLIC_STRIPE_SECRET_KEY
// ❌ ANTI-PATRÓN: creer que app.json/extra es privado — se empaqueta igual
const key = Constants.expoConfig.extra.openaiApiKey
```

**Regla derivada [REQUIRED]:** ningún proveedor de terceros se llama directamente desde la app si su SDK exige una clave privilegiada (OpenAI, Stripe secret, Resend, Twilio). Se llama a un Worker propio que aplica auth y rate limiting (`S-011`).

---

### MSEC-002: Firma del artefacto — keystore fuera del repo y Play App Signing

**[REQUIRED]** El release se firma con una clave de release; el *debug keystore* nunca firma un artefacto distribuible. El keystore y sus contraseñas viven en secretos del CI o en el almacén de credenciales de EAS, jamás en el repositorio. La distribución en Play usa **Play App Signing** con una *upload key* independiente y rotable.

**Por qué:** la clave de firma **es** la identidad de la app en Android. Perderla significa que no puedes volver a actualizar la app publicada; filtrarla significa que un tercero puede firmar un APK que el sistema acepta como actualización legítima de la tuya. Play App Signing separa la clave que sube (rotable si se filtra) de la que firma (custodiada por Google), y convierte una catástrofe en un trámite.

```bash
# Verificar qué firmó realmente el artefacto antes de publicarlo
apksigner verify --print-certs --verbose app-release.apk
```

**[REQUIRED]** El `.gitignore` cubre `*.keystore`, `*.jks`, `key.properties`, `google-services.json` con credenciales y los perfiles de firma de EAS. Si un keystore llegó a un commit, se considera filtrado: aplicar el runbook **(a) Secreto filtrado** de [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) — borrar el commit no basta, el historial y los clones ya lo tienen.

**[REQUIRED]** Los builds de release salen del CI, no de la laptop del desarrollador (amenaza **A** del [THREAT_MODEL.md](THREAT_MODEL.md)).

---

### MSEC-003: Todo el tráfico por TLS — tráfico en claro deshabilitado a nivel de plataforma

**[REQUIRED]** La app declara en su configuración de red que **no** admite tráfico sin cifrar. No se desactiva la validación de certificados en ningún build, ni con una bandera de "solo desarrollo".

**Por qué:** una app móvil se usa en redes que no controlas — Wi-Fi de aeropuerto, hotspot suplantado, red doméstica con DNS manipulado. Sin TLS, las credenciales viajan legibles. Y la bandera de "aceptar cualquier certificado para probar en local" es el bug de seguridad móvil que más veces llega a producción: se añade una tarde y nadie la quita.

**IMPLEMENTACIÓN (`res/xml/network_security_config.xml`, vía config plugin en Expo):**

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
  <base-config cleartextTrafficPermitted="false">
    <trust-anchors>
      <certificates src="system" />
    </trust-anchors>
  </base-config>
  <!-- Sin excepciones de dominio. El desarrollo local usa un túnel HTTPS, no una excepción en claro. -->
</network-security-config>
```

```xml
<!-- ❌ ANTI-PATRÓN: la excepción que se queda para siempre -->
<application android:usesCleartextTraffic="true" />
```

**[REQUIRED]** El `debug-overrides` (que confía en certificados de usuario, lo que habilita proxies de intercepción) solo puede existir en el build type `debug`, y se verifica su ausencia en el manifiesto del release.

**[RECOMMENDED]** *Certificate pinning* si la app maneja dinero o datos de salud. Con dos condiciones no negociables: pinear la clave pública (no el certificado hoja) y publicar un pin de respaldo, o la próxima rotación de certificado deja fuera de servicio a todas las instalaciones existentes hasta que actualicen.

---

### MSEC-004: Tokens y datos sensibles en almacenamiento respaldado por el Keystore del sistema

**[REQUIRED]** Los tokens de sesión, refresh tokens y cualquier PII se guardan en almacenamiento cifrado por hardware/Keystore. `AsyncStorage`, `SharedPreferences` en claro, archivos JSON y el estado de Redux persistido **no** son almacenamiento seguro. Los backups automáticos se desactivan o excluyen explícitamente esos datos.

**Por qué:** `AsyncStorage` es una base SQLite sin cifrar en el sandbox de la app. En un dispositivo rooteado, con un backup ADB o con una copia a la nube mal configurada, ese archivo se lee entero. El Keystore mantiene el material de clave en hardware seguro donde está disponible, de modo que ni un volcado del sistema de archivos lo entrega. Es el equivalente móvil de `S-007` (nada de tokens en almacenamiento plano).

**IMPLEMENTACIÓN (Expo):**

```javascript
import * as SecureStore from 'expo-secure-store'

const REFRESH_KEY = 'refresh_token'

export async function guardarSesion(refreshToken) {
  await SecureStore.setItemAsync(REFRESH_KEY, refreshToken, {
    keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY, // no viaja en backups a otro dispositivo
  })
}

export async function leerSesion() {
  return SecureStore.getItemAsync(REFRESH_KEY)
}

export async function cerrarSesion() {
  await SecureStore.deleteItemAsync(REFRESH_KEY)   // el logout borra el material local, no solo el estado en memoria
}
```

```javascript
// ❌ ANTI-PATRÓN: sesión en almacenamiento plano
await AsyncStorage.setItem('refresh_token', token)
```

En Kotlin nativo el equivalente es `EncryptedSharedPreferences` (Jetpack Security) con una `MasterKey` del Android Keystore.

**Reglas derivadas:**
- **[REQUIRED]** `android:allowBackup="false"`, o reglas de backup que excluyan credenciales y base offline. Un backup a la nube es una copia del sandbox fuera de tu control.
- **[REQUIRED]** Ningún token, contraseña ni PII en `console.log`. En release los logs se eliminan del bundle; en Android los lee `logcat`.
- **[REQUIRED]** La base offline (`MOB-002`, WatermelonDB) es un caché, no autoridad de permisos — misma lógica que `DSEC-008`: quien tiene root edita esa fila.
- **[RECOMMENDED]** `FLAG_SECURE` en pantallas con datos sensibles (bloquea capturas y la miniatura del multitarea) y limpiar el portapapeles tras copiar un dato sensible.

---

### MSEC-005: Superficie exportada mínima y deep links verificados

**[REQUIRED]** Cada `activity`, `service`, `receiver` y `provider` declara `android:exported` de forma explícita, y solo vale `true` cuando otra app **debe** invocarlo. Los enlaces que abren la app usan **App Links verificados** (`autoVerify` + `assetlinks.json` publicado en el dominio), no solo un esquema propio.

**Por qué:** un componente exportado es una API pública que cualquier app instalada puede llamar, sin autenticación y sin pasar por tu UI. Y un esquema propio (`miapp://`) puede registrarlo cualquier otra app: si tu flujo OAuth devuelve el código de autorización por ahí, otra app puede interceptarlo. La verificación por dominio es lo que ata el enlace a un dominio que tú controlas — la contraparte móvil de `DSEC-009`.

```xml
<activity android:name=".MainActivity" android:exported="true">
  <intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" android:host="app.midominio.com" />
  </intent-filter>
</activity>
```

**Reglas derivadas:**
- **[REQUIRED]** Los parámetros de un deep link se validan con esquema (Zod) antes de usarse, como cualquier input público (`S-001`).
- **[REQUIRED]** Ninguna acción con efecto (pagar, borrar, cambiar email) se ejecuta directamente desde un deep link sin confirmación explícita en la UI.
- **[REQUIRED]** OAuth con PKCE y validación de `state`. Sin PKCE, un código interceptado se canjea por una sesión.
- **[REQUIRED]** Ningún `ContentProvider` exportado sin permiso propio. Si no lo consume otra app, `exported="false"`.

---

### MSEC-006: WebView restringido cuando es inevitable

**[REQUIRED]** `MOB-001` ya limita el WebView a contenido externo y pasarelas de pago. Cuando se usa: la URL sale de una lista blanca del código, no de un parámetro; sin acceso a archivos locales; sin puente JS hacia código nativo salvo que sea imprescindible y con una interfaz mínima y validada.

**Por qué:** un WebView que carga una URL arbitraria y expone un `JavascriptInterface` es la misma escalada que `DSEC-003` en desktop: contenido remoto que alcanza capacidades nativas. Y `allowUniversalAccessFromFileURLs` permite que una página local lea cualquier origen, saltándose la política del mismo origen.

```javascript
const ORIGENES_PERMITIDOS = ['https://checkout.stripe.com', 'https://midominio.com']

<WebView
  source={{ uri: url }}
  originWhitelist={ORIGENES_PERMITIDOS}
  allowFileAccess={false}
  allowFileAccessFromFileURLs={false}
  allowUniversalAccessFromFileURLs={false}
  javaScriptEnabled={true}
  onShouldStartLoadWithRequest={(req) =>
    ORIGENES_PERMITIDOS.some((o) => req.url.startsWith(o + '/') || req.url === o)
  }
/>
```

La comparación de origen se hace por prefijo **con separador**: `startsWith('https://midominio.com')` a secas acepta `https://midominio.com.atacante.io`.

---

### MSEC-007: Minificación y ofuscación son fricción, no un control de seguridad

**[REQUIRED]** El release se compila con R8/ProGuard activo y con el motor JS optimizado (Hermes). **[REQUIRED]** Ninguna decisión de seguridad se apoya en que el código sea difícil de leer.

**Por qué:** ofuscar sube el costo de un análisis casual y reduce el tamaño del bundle, y por eso se hace. Pero un atacante motivado desofusca; si la única razón por la que un secreto o una comprobación resiste es que "está ofuscado", el control no existe. La distinción importa porque decide dónde va el presupuesto: en el servidor, no en el ofuscador.

**[REQUIRED]** Las reglas de `proguard-rules.pro` no desactivan la ofuscación globalmente para arreglar un crash de reflexión: se acota la excepción a la clase concreta.

---

### MSEC-008: La integridad del cliente es una señal, nunca una puerta

**[REQUIRED]** El backend jamás concede privilegios porque el cliente afirme estar en un dispositivo íntegro. La detección de root, emulador o *hooking* alimenta scoring de riesgo y telemetría; no autoriza por sí sola.

**Por qué:** cualquier comprobación que corra en el dispositivo la ejecuta el atacante y puede devolver `false`. La única atestación con valor es la que **el servidor** verifica con el proveedor de plataforma (Play Integrity: la app pide un token, el servidor lo valida contra Google). Aun así es una señal probabilística: bloquear duro por ella deja fuera a usuarios legítimos con ROMs alternativas.

```javascript
// ❌ ANTI-PATRÓN: la app se autoriza a sí misma
if (!isRooted()) { habilitarTransferencias() }
```

**[RECOMMENDED]** Play Integrity API para operaciones de alto valor, con el veredicto verificado **en el servidor** y usado para elevar fricción (pedir MFA, ver `AUTH_MFA_STANDARD.md`), no para permitir o denegar en silencio.

---

### MSEC-009: La biometría desbloquea material local; no autentica contra el backend

**[REQUIRED]** Un resultado biométrico exitoso solo puede usarse para liberar una credencial guardada en el Keystore (`MSEC-004`), que es la que se presenta al backend. Nunca para que la app decida por su cuenta que el usuario está autenticado.

**Por qué:** `MOB-003` exige biometría, y esa regla se malinterpreta con facilidad: un `if (biometriaOk) { navegar a la zona privada }` es una comprobación local que se parchea. Ligar la biometría al Keystore (la clave solo se descifra tras autenticación del usuario) convierte una comprobación booleana en una garantía criptográfica del sistema operativo.

**[REQUIRED]** Siempre hay un camino de recuperación (contraseña + MFA) cuando el biométrico falla o el usuario cambia de dispositivo, y **[REQUIRED]** re-inscribir una huella o rostro invalida las claves ligadas al usuario (`setInvalidatedByBiometricEnrollment`), para que añadir una huella nueva al dispositivo no dé acceso a la sesión existente.

---

### MSEC-010: Las actualizaciones OTA van firmadas o no existen

**[REQUIRED]** Si la app usa actualizaciones over-the-air del bundle JS (EAS Update, CodePush), se activa la firma de código de las actualizaciones y la app rechaza cualquier bundle sin firma válida. El canal de producción está separado de los de prueba.

**Por qué:** un OTA reemplaza el código de la app **saltándose la revisión de la tienda y la firma del APK**. Sin firma, quien comprometa la cuenta del servicio de updates entrega JavaScript arbitrario a toda tu base instalada. Es exactamente `DSEC-005` en móvil, y con más alcance porque llega en minutos.

**[REQUIRED]** Un OTA nunca cambia permisos ni código nativo — eso exige una release firmada por la tienda. **[RECOMMENDED]** Rollout gradual con métrica de crash rate y capacidad de rollback probada antes de necesitarla.

---

### MSEC-011: Permisos mínimos y justificados

**[REQUIRED]** El manifiesto declara solo los permisos que una función activa necesita. Se piden en el momento de usar la función, con una explicación previa en la UI, no en el arranque. Cada permiso peligroso queda justificado por escrito en el PR que lo introduce.

**Por qué:** cada permiso amplía lo que un compromiso de la app alcanza y lo que las librerías de terceros incluidas pueden hacer. Los permisos declarados son públicos en la ficha de la tienda: pedir ubicación o contactos sin necesidad clara cuesta instalaciones y puede costar el listado. Y `MOB-006` (cámara/OCR) arrastra permisos que no deben quedarse cuando la función se retira.

**[REQUIRED]** Al eliminar una función se eliminan sus permisos en el mismo PR. **[REQUIRED]** Auditar los permisos que **inyectan** las dependencias (`aapt dump permissions` sobre el APK final): la lista real suele ser mayor que la escrita a mano.

---

### MSEC-012: El backend trata a la app móvil como un cliente anónimo de internet

**[REQUIRED]** Autenticación, autorización (RBAC + RLS, `S-009`/`S-010`), rate limiting (`S-011`) y validación de entrada (`S-001`) se aplican completos a las peticiones de la app. Ningún endpoint concede nada por un header propio, un User-Agent, un "secreto de app" o el nombre del paquete.

**Por qué:** un proxy de intercepción sobre un dispositivo propio muestra cada petición que hace tu app, con sus headers y su cuerpo. Reproducirlas con `curl` es trivial. La app móvil no es un perímetro: es una UI para tu API pública. Es la misma regla que `DSEC-011`, y la razón por la que las reglas anteriores protegen al usuario mientras esta protege al sistema.

**[REQUIRED]** Los precios, los límites de plan y los permisos se calculan en el servidor (`PAYMENTS_SECURITY_STANDARD.md`, regla #7). Una app que envía `{"precio": 0}` debe recibir un error, no un pedido.

---

## CHECKLIST DE AUDITORÍA MÓVIL (PRE-PUBLICACIÓN)

**Secretos y build**
- [ ] `MSEC-001` — grep sobre el bundle del APK no revela claves privilegiadas
- [ ] `MSEC-001` — ningún SDK de tercero con clave privilegiada se llama desde la app
- [ ] `MSEC-002` — `apksigner verify --print-certs` muestra la clave de release, no la de debug
- [ ] `MSEC-002` — keystore y contraseñas fuera del repo; Play App Signing activo; build desde CI
- [ ] `MSEC-007` — R8 y Hermes activos; ninguna regla de seguridad depende de la ofuscación

**Red**
- [ ] `MSEC-003` — `cleartextTrafficPermitted="false"`; sin `usesCleartextTraffic` en el manifiesto de release
- [ ] `MSEC-003` — sin `debug-overrides` ni validación de certificados desactivada en release
- [ ] `MSEC-003` — si hay pinning: clave pública, pin de respaldo y plan de rotación escrito

**Almacenamiento**
- [ ] `MSEC-004` — tokens en SecureStore/EncryptedSharedPreferences; nada de sesión en AsyncStorage
- [ ] `MSEC-004` — `allowBackup="false"` o exclusión explícita de credenciales y base offline
- [ ] `MSEC-004` — sin tokens ni PII en logs; logout borra el material local
- [ ] `MSEC-004` — la base offline no decide permisos

**Superficie expuesta**
- [ ] `MSEC-005` — `android:exported` explícito en todos los componentes; `true` solo donde se justifica
- [ ] `MSEC-005` — App Links con `autoVerify` y `assetlinks.json` publicado; parámetros validados con Zod
- [ ] `MSEC-005` — OAuth con PKCE + `state`; ninguna acción con efecto sin confirmación
- [ ] `MSEC-006` — WebView con allowlist de origen (comparación con separador), sin acceso a archivos
- [ ] `MSEC-011` — permisos mínimos, pedidos en contexto; auditados con `aapt dump permissions`

**Confianza y distribución**
- [ ] `MSEC-008` — ninguna decisión de acceso depende de una comprobación local de integridad
- [ ] `MSEC-009` — la biometría libera material del Keystore; existe camino de recuperación
- [ ] `MSEC-010` — OTA con firma de código verificada y canal de producción separado
- [ ] `MSEC-012` — endpoints probados con `curl` sin la app: aplican auth, RBAC/RLS, rate limiting y validación
- [ ] Las 7 capas de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) siguen verdes en el backend
