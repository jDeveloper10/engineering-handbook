---
title: "Playbook: Credenciales Apple/Google reutilizables para agencias con múltiples apps + automatización de submission"
category: 07_DevOps
doc_type: runbook
tags: [ios, android, expo, eas, app-store-connect, google-play, apns, credenciales, automatizacion, agencia, incident]
summary: "Cómo estructurar credenciales de Apple Developer y Google Play cuando una misma cuenta publica varias apps de distintos clientes (patrón de agencia): qué es reutilizable entre apps y qué no, y el catálogo de 11 errores reales encontrados configurando App Store Connect API, EAS Build/Submit y push notifications directas por APNs."
keywords: [app-store-connect-api-key, apns, distribution-certificate, provisioning-profile, bundle-id, eas-submit, eas-build, ascAppId, google-play-service-account, workers-service-bindings, wrangler]
updated: 2026-09-14
status: current
sources:
  - "Sesión real configurando Apple Developer + EAS para dos apps de clientes distintos bajo la misma cuenta Apple, 2026-09-09 a 2026-09-14"
  - "Apple Developer — App Store Connect API Reference"
  - "Expo Docs — EAS Submit / EAS Build (docs.expo.dev)"
  - "Google Play Console — API access (Setup)"
---

# Playbook: Credenciales Apple/Google reutilizables entre apps (patrón agencia)

Contexto que resuelve este documento: una sola cuenta de Apple Developer (o de Google Play Console) va a publicar **varias apps de distintos clientes**. Configurar cada app desde cero como si la cuenta no tuviera historial desperdicia tiempo y, peor, genera credenciales duplicadas innecesarias. Este documento separa qué es **reutilizable a nivel de cuenta** de qué es **específico por app**, y documenta los errores reales — no hipotéticos — que salieron al hacerlo.

---

## 1. Qué es reutilizable entre apps y qué no (Apple)

| Credencial | Alcance | Reutilizable entre apps del mismo equipo/cuenta |
|---|---|---|
| App Store Connect API Key (`.p8` + Key ID + Issuer ID) | Cuenta completa | **Sí** — la misma key sirve para cualquier app nueva, solo cambia el `ascAppId` en `eas.json` |
| APNs Auth Key (`.p8` + Key ID + Team ID) | Cuenta completa | **Sí** — la misma key firma JWT para APNs de cualquier app; solo cambia el `apns-topic` (bundle ID) en cada request |
| Certificado de Distribución (`.p12`) | Por **equipo** (Team ID) | **Sí**, pero EAS pregunta "¿reusar este certificado?" — responder que sí en vez de generar uno nuevo por app |
| Provisioning Profile (`.mobileprovision`) | Por **app** (bundle ID) | **No** — uno nuevo por cada bundle ID, no se puede compartir |
| Bundle ID | Por app, global en todo Apple (no solo tu cuenta) | No aplica — cada app necesita el suyo, único en **todo el ecosistema Apple**, no solo dentro de tu cuenta |

Guardar las credenciales de cuenta (API Key, APNs Key) en una carpeta fuera de cualquier repo, con permisos restringidos (700 la carpeta, 600 los archivos), y un `README.md` al lado documentando Key ID / rol / para qué se usa cada una. Sin ese índice, la segunda app que configures vas a re-crear una key que ya existía porque no te acordás cuál era cuál.

En `eas.json`, reutilizar la API Key de cuenta así — solo `ascAppId` cambia por proyecto:

```json
{
  "submit": {
    "production": {
      "ios": {
        "ascApiKeyPath": "/ruta/fuera-del-repo/AuthKey_XXXXXXXXXX.p8",
        "ascApiKeyId": "XXXXXXXXXX",
        "ascApiKeyIssuerId": "00000000-0000-0000-0000-000000000000",
        "ascAppId": "0000000000"
      }
    }
  }
}
```

---

## 2. Catálogo de errores reales

### E1 — Un Bundle ID puede estar tomado globalmente sin estar en tu cuenta

**Síntoma:** EAS o App Store Connect responden "Bundle ID not available" para un identificador que nunca registraste vos.

**Causa real:** los Bundle IDs son únicos en **todo Apple**, no solo dentro de tu cuenta de desarrollador. Cualquier otro desarrollador — de cualquier parte del mundo, con cualquier app, publicada o no — pudo haberlo tomado antes.

**Cómo confirmarlo sin adivinar:** consultar tu propia cuenta vía API antes de asumir que el conflicto es tuyo:

```
GET https://api.appstoreconnect.apple.com/v1/bundleIds?filter[identifier]=com.tuempresa.tuapp
```

Si la respuesta viene vacía, el identificador no es tuyo — el conflicto es con un tercero y no hay forma de "liberarlo": hay que elegir otro Bundle ID. No pierdas tiempo troubleshooteando algo que no tiene arreglo.

### E2 — El auto-sync de capacidades de EAS puede fallar con un request mal formado

**Síntoma:** al aceptar "¿Configurar Push Notifications?" en el flujo interactivo de `eas build`, falla con `"Apple API error: request entity is not a valid request document object"`.

**Fix:** no depender del flujo automático de EAS para esa capacidad puntual — habilitarla directo contra la API de Apple:

```
POST https://api.appstoreconnect.apple.com/v1/bundleIdCapabilities
{
  "data": {
    "type": "bundleIdCapabilities",
    "attributes": { "capabilityType": "PUSH_NOTIFICATIONS" },
    "relationships": { "bundleId": { "data": { "type": "bundleIds", "id": "<id-del-bundle-id>" } } }
  }
}
```

### E3 — La App Store Connect API prohíbe crear apps nuevas, incluso con una key Admin

**Síntoma:** `POST /v1/apps` responde `403 FORBIDDEN_ERROR` — `"The resource 'apps' does not allow 'CREATE'. Allowed operations are: GET_COLLECTION, GET_INSTANCE, UPDATE"`.

**Esto no es un problema de permisos de la key** (se confirmó con una key de rol Admin, el más alto disponible) — es una restricción de la plataforma. **El registro de "App" en App Store Connect se crea siempre a mano**, desde la web (Apps → "+" → New App, eligiendo el Bundle ID ya registrado del dropdown). Recién después de creada a mano, la API puede leerla, gestionar sus builds, TestFlight y metadata.

Flujo correcto de principio a fin:
1. Registrar el Bundle ID por API (esto sí se puede automatizar).
2. Habilitar capacidades del Bundle ID por API (E2).
3. **Crear la App a mano en la web** (paso manual innegociable).
4. Recuperar su `ascAppId` numérico por API para usarlo en `eas.json`:
   ```
   GET https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]=com.tuempresa.tuapp
   ```
5. De ahí en adelante, `eas build` + `eas submit` corren sin intervención manual.

### E4 — `eas submit` no interactivo necesita `ascAppId` explícito

**Síntoma:** `eas submit -p ios --non-interactive` falla con `"Set ascAppId in the submit profile (eas.json) or re-run this command in interactive mode."`

**Fix:** agregar `"ascAppId": "<id numérico>"` (obtenido en E3, paso 4) al perfil de submit en `eas.json`. En modo interactivo, EAS lo pregunta y lo puede autodetectar; en CI/no-interactivo, no.

### E5 — La primera generación de certificado/perfil de iOS no se puede automatizar del todo

`eas credentials:configure-build` no tiene flag `--non-interactive`, y ni siquiera pipear stdin a `eas build --non-interactive` alcanza para la **primera** generación de un Certificado de Distribución (requiere login interactivo con Apple ID, incluyendo 2FA). Una vez que el certificado ya existe (ver §1, es reutilizable), los builds siguientes sí corren en no-interactivo/CI sin problema. Para la primera vez, hace falta una terminal interactiva real — no delegarlo a un pipe ni a un script.

**Matiz cuando la app tiene más de un target** (por ejemplo, agregaste una extensión de Widget/Live Activity vía `@bacons/apple-targets` — ver [PLAYBOOK_EXPO_LIVE_ACTIVITIES.md](PLAYBOOK_EXPO_LIVE_ACTIVITIES.md)): cada target necesita su **propio Provisioning Profile** (el Certificado de Distribución sí se comparte entre todos). Un build no-interactivo falla así apenas agregás el primer target nuevo:

```
Setting up credentials for target RoadsideLiveActivity (com.tuapp.widget)
Distribution Certificate is not validated for non-interactive builds.
Failed to set up credentials.
Credentials are not set up. Run this command again in interactive mode.
```

Mismo fix que la primera vez: correr ese build puntual en terminal interactiva, aceptar "reusar certificado" + "generar nuevo provisioning profile" para el target nuevo. Una vez generado ese perfil, vuelve a ser reutilizable — los builds siguientes (incluso con `--non-interactive`) ya no lo piden de nuevo.

### E10 — `autoSubmit` no es un campo de `eas.json`, es una flag de `eas build`

**Síntoma:** poner `"autoSubmit": true` dentro de un perfil de `build` en `eas.json` falla la validación del archivo: `"build.<perfil>.autoSubmit" is not allowed`.

**Fix:** en las versiones actuales de `eas-cli`, la sumisión automática tras el build se activa con una flag en el comando, no en la config:

```bash
eas build -p ios --profile production --auto-submit
```

Por defecto usa el perfil de `submit` con el **mismo nombre** que el perfil de `build` (`production` → `production`). Para usar uno con otro nombre: `--auto-submit-with-profile=<nombre>`.

### E11 — Agregar un target nativo (Widget/Live Activity) a un proyecto Expo managed

Ver el detalle completo, con los errores específicos de ActivityKit y módulos nativos, en [PLAYBOOK_EXPO_LIVE_ACTIVITIES.md](PLAYBOOK_EXPO_LIVE_ACTIVITIES.md). El resumen relevante para credenciales: agregar un target nuevo (aunque sea solo una extensión de widget, sin código propio de la app) dispara automáticamente el requisito de un Provisioning Profile nuevo — ver E5 arriba.

### E6 — GitHub Environments con "required reviewers" no existe en cuentas personales

Cubierto en detalle en [GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md](GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md#gate-de-producción-con-aprobación-manual): solo disponible para repos de una Organización en plan Team o superior, GitHub Pro personal no lo desbloquea. El gate real para cuenta personal es un workflow con `workflow_dispatch` como único trigger.

### E7 — Bug real de Wrangler causando crashes periódicos de `wrangler dev`

`wrangler dev` en la versión `4.124.0` se caía cada ~60 segundos durante desarrollo local. Fix: actualizar a `4.131.1` o posterior.

### E8 — Conflicto de versión entre `wrangler` y `@cloudflare/workers-types` en un Worker nuevo

Un Worker nuevo creado con `wrangler` en la serie `4.131.x` requiere `@cloudflare/workers-types` en `^5.x` — `^4.x` falla el `npm install` por conflicto de peer dependency. Si vas a crear un Worker nuevo, fijar `workers-types` en `^5.x` desde el `package.json` inicial en vez de dejar que el resolver de paquetes decida.

### E9 — Un Service Binding entre Workers rompe TODOS los tests locales si el otro Worker no corre

**Síntoma:** al agregar un `[[services]]` binding en `wrangler.toml` para llamar a otro Worker (por ejemplo, un Worker separado de push notifications), **toda** la suite de tests locales (incluso tests que no tocan ese binding) falla al arrancar con:
```
Worker "..."'s binding "X" refers to a service "nombre-del-otro-worker", but no such service is defined.
```

**Causa:** Miniflare (el runtime que usan los tests) resuelve todos los bindings declarados al arrancar, sin importar si el test en cuestión los usa. Un `[[services]]` apunta a un Worker externo que en el harness de test no existe.

**Fix — no es hacer el binding "opcional" en el tipo de TypeScript** (eso solo evita el error de compilación, no el de arranque del runtime de test). Hay que registrar un Worker auxiliar de test con el mismo nombre en la config de `vitest-pool-workers`:

```ts
// vitest.config.ts
cloudflareTest({
  wrangler: { configPath: './wrangler.toml' },
  miniflare: {
    workers: [
      {
        name: 'nombre-del-otro-worker', // debe matchear `service` en [[services]] de wrangler.toml
        modules: true,
        script: "export default { fetch: () => new Response('ok') };",
      },
    ],
  },
}),
```

Ese stub solo existe para que el runtime de test arranque — no reemplaza una prueba real de la integración entre Workers. Si necesitás probar de verdad la llamada al otro Worker, hacelo con un test de integración aparte, contra el Worker real desplegado (o corriendo localmente los dos con `wrangler dev` en paralelo).

---

## 3. Push notifications: Expo relay vs. APNs directo

Dos formas de mandar push a iOS desde Expo:

| | Relay de Expo (`getExpoPushTokenAsync`) | APNs directo (`getDevicePushTokenAsync`) |
|---|---|---|
| Dependencia extra | Servidor de Expo como intermediario | Ninguna — tu backend habla directo con `api.push.apple.com` |
| Infraestructura propia | No hace falta | Un Worker/función que firma JWT ES256 y hace POST a Apple |
| Credencial | Expo Push Key (gestionada por EAS) | APNs Auth Key de tu cuenta (ver §1 — reutilizable entre apps) |
| Cuándo conviene | Prototipos, MVPs, cuando no importa el hop extra | Cuando ya tenés backend propio y preferís no depender de un tercero para algo crítico del producto |

Si elegís APNs directo: la misma APNs Auth Key sirve para **todas** las apps de la cuenta — al replicar el patrón en una app nueva, solo cambia la variable del bundle ID (`apns-topic`), nunca la key en sí.

---

## 4. Google Play: ¿se puede automatizar igual?

**Sí, y en algunos aspectos es más automatizable que Apple** — pero con la misma restricción de fondo en el primer paso.

- **Lo que SÍ se automatiza por completo:** subir un `.aab`/`.apk` nuevo, promoverlo entre tracks (internal → closed → open → production), editar el store listing (textos, capturas), gestionar testers de un track cerrado. Todo esto vía la **Google Play Developer API**, usando una **Service Account** (cuenta de servicio de Google Cloud) con su JSON key.
- **Lo que NO se automatiza — igual que Apple con `apps`:** crear la app por primera vez dentro de Play Console. Ese registro inicial (nombre, package name, categoría) se crea a mano, una sola vez, desde la web de Play Console.
- **Una vez creada la app a mano:** `eas submit -p android` con el JSON de la Service Account referenciado en `eas.json` corre en modo no-interactivo/CI sin ningún paso manual adicional — a diferencia de iOS (E5), Android no tiene un equivalente al "primer certificado requiere login interactivo".

Configuración en `eas.json`:

```json
{
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "/ruta/fuera-del-repo/google-play-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

Pasos para generar esa Service Account (una sola vez por cuenta de Play Console, reutilizable entre todas las apps del mismo desarrollador, igual que la API Key de Apple):
1. Play Console → **Setup → API access** → vincular o crear un proyecto de Google Cloud.
2. En Google Cloud Console, crear una **Service Account** dentro de ese proyecto y descargar su clave en JSON.
3. Volver a Play Console → **API access** → conceder permisos a esa cuenta de servicio (como mínimo, permiso para gestionar releases del track que vayas a usar).
4. Referenciar el JSON descargado en `eas.json` como en el ejemplo de arriba.

**Advertencia que la automatización no evita:** el requisito de "12 testers, 14 días consecutivos" en closed testing (para cuentas de Play Console creadas después de nov-2023) sigue el reloj real de calendario — subir el build más rápido no acorta esa espera. Ver [CHECKLIST_APP_STORE_RELEASE.md](../06_Testing/CHECKLIST_APP_STORE_RELEASE.md) para el detalle completo de esa política.
