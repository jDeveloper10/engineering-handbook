# Estándar de Desarrollo Mobile (MOB-001 a MOB-006)

> 🔒 **Este documento define cómo se construye la app, no qué la mantiene segura.** Las reglas de seguridad del APK (cero secretos en el bundle, firma del artefacto, TLS obligatorio, tokens en Keystore, componentes exportados, OTA firmado) viven en [05_Security/MOBILE_SECURITY_STANDARD.md](../../05_Security/MOBILE_SECURITY_STANDARD.md) (`MSEC-001` a `MSEC-012`) y son de lectura obligatoria antes de publicar. En particular, `MOB-003` (biometría) solo es seguro implementado según `MSEC-009`. Ante conflicto, manda el documento de seguridad.

## 🎯 Stack
- **Framework:** React Native + Expo (managed workflow)
- **Navegación:** Expo Router (file-based)
- **Estado:** React Query + Zustand
- **UI:** NativeWind (Tailwind para React Native)
- **Offline:** WatermelonDB + NetInfo

---

## ⚡ REGLAS INQUEBRANTABLES

### MOB-001: NUNCA USAR WEBVIEW PARA FUNCIONALIDAD CORE

**Regla:**
WebView solo para:
- Mostrar contenido web externo (blog, términos)
- Pasarela de pago (Stripe, PayPal)

**Prohibido:**
- Formularios en WebView
- Navegación en WebView
- Cualquier UI principal en WebView

---

### MOB-002: OFFLINE-FIRST CON WATERMELONDB

```typescript
// model/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb'

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'proposals',
      columns: [
        { name: 'client_name', type: 'string' },
        { name: 'total_cents', type: 'number' },
        { name: 'status', type: 'string' },
        { name: 'synced_at', type: 'number' }
      ]
    })
  ]
})

// Sincronización con Supabase
import { synchronize } from '@nozbe/watermelondb/sync'

await synchronize({
  database,
  pullChanges: async ({ lastPulledAt }) => {
    const { data } = await supabase
      .from('proposals')
      .select('id, title, status, amount_cents, currency, updated_at') // DB-001
      .gt('updated_at', lastPulledAt)
    return { changes: data, timestamp: Date.now() }
  },
  pushChanges: async ({ changes }) => {
    // Enviar cambios locales al servidor
  }
})
```

---

### MOB-003: BIOMETRÍA PARA AUTENTICACIÓN

```typescript
import * as LocalAuthentication from 'expo-local-authentication'

export async function biometricLogin() {
  const compatible = await LocalAuthentication.hasHardwareAsync()
  if (!compatible) throw new Error('Dispositivo no compatible')
  
  const enrolled = await LocalAuthentication.isEnrolledAsync()
  if (!enrolled) throw new Error('No hay biometría configurada')
  
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Autenticación requerida',
    fallbackLabel: 'Usar contraseña'
  })
  
  if (result.success) {
    // Obtener token almacenado en SecureStore
    const token = await SecureStore.getItemAsync('auth_token')
    return token
  }
}
```

---

### MOB-004: PUSH NOTIFICATIONS

```typescript
// Registro de dispositivo
import * as Notifications from 'expo-notifications'

async function registerForPushNotifications() {
  const { status } = await Notifications.requestPermissionsAsync()
  if (status !== 'granted') return
  
  const token = await Notifications.getExpoPushTokenAsync()
  
  // Guardar token en backend
  await supabase.from('device_tokens').upsert({
    user_id: userId,
    token: token.data,
    platform: Platform.OS
  })
}

// Manejar notificación entrante
Notifications.addNotificationResponseReceivedListener(response => {
  const proposalId = response.notification.request.content.data.proposalId
  router.push(`/proposals/${proposalId}`)
})
```

---

### MOB-005: DEEP LINKS

```typescript
// app.json
{
  "expo": {
    "scheme": "omnisuite",
    "plugins": ["expo-router"],
    "intentFilters": [
      {
        "action": "VIEW",
        "data": [
          { "scheme": "https", "host": "omnisuite.com", "pathPrefix": "/proposals" }
        ]
      }
    ]
  }
}

// Manejar deep link
export default function RootLayout() {
  return (
    <LinkingConfiguration
      config={{
        screens: {
          Proposal: 'proposals/:id',
          Accept: 'public/:token'
        }
      }}
    />
  )
}
```

---

### MOB-006: CAPTURA DE FOTOS Y OCR

```typescript
import * as ImagePicker from 'expo-image-picker'
import { recognizeText } from 'react-native-mlkit-ocr'

export async function scanDocument() {
  const result = await ImagePicker.launchCameraAsync({
    quality: 1,
    base64: false
  })
  
  if (!result.canceled) {
    const text = await recognizeText(result.assets[0].uri)
    return text.blocks.map(b => b.text).join('\n')
  }
}
```
