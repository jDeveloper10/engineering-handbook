---
title: "Playbook: Live Activities y módulos nativos custom en Expo managed workflow"
category: 07_DevOps
doc_type: runbook
tags: [ios, expo, live-activities, activitykit, expo-modules, widgetkit, apns, config-plugins, incident]
summary: "Cómo agregar ActivityKit (Live Activities de Dynamic Island / pantalla de bloqueo) con actualizaciones remotas por push a un proyecto Expo managed, sin eyectar: la arquitectura correcta (config plugin para el widget + módulo local de Expo para el puente nativo), por qué NO sirve copiar un bridge estilo React Native clásico, y el formato real del push de ActivityKit."
keywords: [activitykit, live-activity, dynamic-island, widgetkit, bacons-apple-targets, create-expo-module, expo-modules-core, pushtokenupdates, push-type-liveactivity, continuous-native-generation]
updated: 2026-09-14
status: current
sources:
  - "Sesión real agregando Live Activity con push updates a ViaYa (Expo SDK 57), 2026-09-14"
  - "Apple Developer — Updating and ending your Live Activity with ActivityKit push notifications"
  - "@bacons/apple-targets README (github.com/EvanBacon/expo-apple-targets)"
  - "Expo Docs — Module API (Expo Modules API)"
---

# Playbook: Live Activities en Expo managed (con push updates reales)

Contexto que resuelve este documento: querés que tu app Expo (managed, sin eyectar) muestre una Live Activity en la Dynamic Island / pantalla de bloqueo de iOS, y que se actualice **aunque la app esté cerrada** (vía push de ActivityKit, no solo mientras la app está abierta). Esto toca tres piezas que Expo managed no trae por defecto: una extensión de Widget, un puente nativo hacia esa extensión, y un formato de push distinto al de una notificación normal.

---

## 1. La arquitectura correcta (y por qué la obvia no sirve)

Un error fácil de cometer: copiar el patrón de un ejemplo de **React Native bare** (bridge con `RCTBridgeModule` + archivo `.m` de `RCT_EXTERN_MODULE`) directo a un proyecto Expo managed. Eso NO funciona de forma sostenible acá, porque:

- Expo managed usa **Continuous Native Generation (CNG)**: la carpeta `ios/` se borra y se regenera por completo en cada `expo prebuild`/`eas build`. Cualquier archivo Swift que hayas puesto a mano ahí (o que haya puesto un agente/IDE) **desaparece en el próximo build** si nada lo vuelve a inyectar.
- Un archivo Swift suelto con `@objc(MiClase)` no alcanza para que React Native lo vea como Native Module — sin el `.m` de puente Y sin estar en el target correcto del proyecto Xcode, el bridge simplemente no existe para JS.

La arquitectura que sí sobrevive a CNG tiene dos piezas separadas, cada una con su propia herramienta:

| Pieza | Qué es | Herramienta correcta |
|---|---|---|
| Puente nativo (código que corre en la app, ej. `Activity.request(...)`) | Un módulo de Expo | **Módulo local de Expo** (`npx create-expo-module --local`) |
| UI del widget (lo que se ve en Dynamic Island / lock screen) | Una extensión de Xcode separada | **Config plugin `@bacons/apple-targets`** |

No son intercambiables: un módulo de Expo se compila como parte de la app principal (vía autolinking), nunca como una extensión de Widget; el config plugin de targets crea extensiones de Xcode reales, pero no está pensado para inyectar código en el target principal de la app.

---

## 2. Módulo local de Expo (el puente nativo)

```bash
npx create-expo-module@latest --local --barrel --name TuModulo -p apple modules/tu-modulo
```

Notas reales de esta sesión:

- **Bug del path**: si le pasás `modules/tu-modulo` como destino, el CLI lo crea en `modules/modules/tu-modulo` (duplica el prefijo). Hay que moverlo a mano un nivel arriba después.
- **`expo-module.config.json` usa la clave `"apple"`** (no `"ios"`) en SDK 53+. Copiar un ejemplo viejo con `"ios"` hace que el módulo nunca se detecte.
- El módulo scaffolded no trae `package.json` — no hace falta, el autolinking de módulos locales los descubre por convención de carpeta (`modules/`), no por npm.
- Para argumentos estructurados a una función nativa, usar un `struct: Record` con propiedades `@Field`, no un diccionario `[String: Any]` suelto — es el patrón que usa el propio Expo en sus módulos (`expo-location`, por ejemplo) y evita líos de conversión de tipos.
- `AsyncFunction` acepta cuerpos `async`/`await` directamente, sin envolver en un `Task {}` — solo hace falta un `Task {}` propio para una suscripción de larga duración (como escuchar un `AsyncSequence`) que no debe bloquear el retorno de la función.

**Cómo verificar que el autolinking realmente lo encuentra**, sin necesitar una Mac:

```bash
npx expo-modules-autolinking resolve --platform apple --json
```

Si tu módulo no aparece en el resultado, el problema está en `expo-module.config.json` o en la ubicación de la carpeta — antes de gastar minutos de build en EAS para descubrirlo.

---

## 3. Config plugin para el Widget (`@bacons/apple-targets`)

```bash
npm install @bacons/apple-targets
```

Estructura esperada (no la genera el `create-expo-module`, se arma a mano):

```
targets/
  tu-widget/
    expo-target.config.js   # type: "widget", ver docs del paquete
    TusArchivos.swift
```

Agregar `"@bacons/apple-targets"` al array de `plugins` en `app.json`. El plugin, en cada `prebuild`, genera un `PBXNativeTarget` de extensión que **vive fuera de `ios/`** (referenciado con rutas relativas tipo `../targets/tu-widget/...`), y solo si falta, te genera un `Info.plist` mínimo — no lo vuelve a tocar después.

**Cómo verificar que el target se armó bien, sin Xcode ni Mac:**

```bash
npx expo prebuild -p ios --clean
grep -n "nombre-de-tu-widget" ios/*.xcodeproj/project.pbxproj
```

`expo prebuild` corre perfectamente en Linux (no necesita compilar, solo generar archivos de proyecto) — buscá en el `.pbxproj` resultante un `PBXNativeTarget` con el nombre de tu widget y una línea `INFOPLIST_FILE = "../targets/tu-widget/Info.plist"`. Si aparece, el plugin funcionó; si no aparece nada, algo en la config está mal y conviene arreglarlo ahí, no después de subir un build entero a EAS.

### Atributos compartidos entre la app y el widget: duplicar, no enlazar

`ActivityAttributes` (el struct que define el estado de una Live Activity) lo necesitan **ambos lados**: la app (para pedir la actividad) y el widget (para dibujarla). Como corren en procesos separados, ActivityKit no necesita que compartan el mismo binario Swift — decodifica el `ContentState` vía `Codable` de forma independiente en cada proceso. Por eso la solución simple y correcta es **duplicar el archivo** (uno en el módulo, otro en el target del widget) con un comentario cruzado avisando que hay que mantenerlos en sync — intentar compartirlo vía un framework o el mecanismo `_shared` del plugin es una complejidad innecesaria para un struct de 8 líneas.

---

## 4. Push updates reales (ActivityKit, no solo local)

Si solo llamás `Activity.request(..., pushType: nil)`, la Live Activity **únicamente se actualiza mientras tu app JS está corriendo y llama a `update()`** — se congela apenas el usuario cierra la app o bloquea el teléfono. Para que el backend la actualice de verdad hace falta `pushType: .token` y todo lo siguiente:

1. **El token de push de la actividad es distinto al token de push normal del dispositivo**, y encima ActivityKit puede regenerarlo más de una vez durante la vida de la actividad — hay que escuchar `activity.pushTokenUpdates` (un `AsyncSequence`), no pedirlo una sola vez.
2. **El formato del payload es distinto al de una notificación normal.** Reusar el mismo código de envío de push "de alerta" no funciona:

   | | Push normal | Push de Live Activity |
   |---|---|---|
   | `apns-topic` | `<bundle-id>` | `<bundle-id>.push-type.liveactivity` |
   | `apns-push-type` | `alert` | `liveactivity` |
   | `apns-priority` | libre | `10` (obligatorio) |
   | body | `{"aps": {"alert": {...}}}` | `{"aps": {"event": "update"\|"end", "content-state": {...}, "timestamp": ...}}` |

3. **Guardar el token por actividad, no por dispositivo.** Un usuario puede tener como máximo una Live Activity de un tipo dado a la vez (para este caso de uso, una por solicitud/pedido activo) — la tabla que lo guarda se indexa por el ID de ese recurso de negocio, no por usuario ni por dispositivo.
4. **Reusar la actividad existente, no duplicarla.** Si el usuario cierra y reabre la app mientras la Live Activity sigue viva en el sistema (esto pasa: las Live Activities sobreviven a que la app se cierre), pedir una nueva con `Activity.request` sin chequear primero crea una segunda superpuesta en la Dynamic Island. Antes de pedir una nueva, buscar en `Activity<TusAtributos>.activities` una con el mismo identificador de negocio y reusarla.

---

## 5. Límite real de verificación sin Mac

`expo prebuild` y `expo-modules-autolinking resolve` (arriba) confirman que la **configuración** está bien armada — que el target existe, que el módulo se linkea. Ninguno de los dos compila Swift ni corre ActivityKit de verdad. Lo único que confirma que el widget realmente compila, se ve bien y se actualiza por push es un build real de EAS instalado en un iPhone físico (el simulador de iOS no es confiable para probar la entrega de push a Live Activities). Tratar la verificación de config como si fuera la verificación completa es el mismo error que fingir éxito — hay que decir explícitamente cuál de las dos se hizo.
