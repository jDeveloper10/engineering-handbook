---
title: "Estándar de Firebase"
category: 02_Backend
doc_type: estandar
tags: [firebase, firestore, firebase-auth, firebase-functions, realtime-database]
summary: "Estándar del dominio Backend para Firebase: Firestore, Authentication, Cloud Functions, seguridad, patrones y anti-patrones."
keywords: [firebase, firestore, firebase-auth, cloud-functions, realtime-database, firebase-admin]
updated: 2026-08-30
status: current
---

# FIREBASE ENGINEERING STANDARD

> **Stack de referencia:** Firebase Auth + Firestore + Cloud Functions + Firebase Admin
> **Depende de:** BACKEND_ENGINEERING_STANDARD.md (Nivel 1), SECURITY_ENGINEERING_STANDARD.md
> **Aplica a:** Todo proyecto que use Firebase como backend

---

## 01. Firebase Authentication

### 1.1 Roles de Firebase

**[REQUIRED]** Separar claramente qué vive en Firebase Auth vs en Firestore:

| Firebase Auth | Firestore |
|---|---|
| Email/password | Perfil completo (nombre, foto, bio) |
| Proveedor OAuth (Google) | Roles, permisos custom |
| Token JWT (uid) | Datos de negocio |
| Email verificado | Configuración de usuario |

### 1.2 Configuración del cliente

**[REQUIRED]** Configuración de Firebase en un solo archivo `firebase.ts`:

```typescript
// src/lib/firebase.ts
import { initializeApp, getApps } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,          // ✅ Pública
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,  // ✅ Pública
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,    // ✅ Pública
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const db = getFirestore(app);

if (import.meta.env.DEV) {
  connectAuthEmulator(auth, 'http://localhost:9099');
  connectFirestoreEmulator(db, 'localhost', 8080);
}

export { app, auth, db };
```

### 1.3 NUNCA exponer service account en frontend

**[REQUIRED]** La `serviceAccount.json` o `FIREBASE_ADMIN_KEY` NUNCA viven en el frontend:

```
❌ PROHIBIDO:
src/lib/firebase-admin.ts  →  import { cert } from 'firebase-admin/app'
                               serviceAccount.json en src/

✅ CORRECTO:
firebase-functions/         →  Firebase Admin SOLO en Cloud Functions
worker/                     →  Firebase Admin SOLO en backend
```

---

## 02. Firestore

### 2.1 Estructura de colecciones

**[REQUIRED]** Estructura de Firestore por feature:

```
firestore/
├── users/
│   └── {userId}/
│       ├── profile/
│       └── settings/
├── orders/
│   └── {orderId}/
├── products/
│   └── {productId}/
└── index.ts  →  export de reglas
```

### 2.2 Reglas de seguridad (Firestore Rules)

**[REQUIRED]** Toda tabla tiene reglas de seguridad:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Usuarios: solo ven su propio perfil
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Órdenes: usuario ve las suyas, admin ve todas
    match /orders/{orderId} {
      allow read: if request.auth != null && 
        (resource.data.userId == request.auth.uid || 
         request.auth.token.admin == true);
      allow create: if request.auth != null;
    }
    
    // Productos: lectura pública, escritura solo admin
    match /products/{productId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
  }
}
```

### 2.3 Evitar reads excesivos

**[REQUIRED]** Firestore cobra por lectura. Evitar:

```typescript
// ❌ LEAK DE LECTURAS — lee TODOS los documentos
const snapshot = await getDocs(collection(db, 'orders'));
snapshot.forEach(doc => console.log(doc.data()));

// ✅ FILTRAR y LIMITAR
const q = query(
  collection(db, 'orders'),
  where('userId', '==', userId),
  orderBy('createdAt', 'desc'),
  limit(20)
);
const snapshot = await getDocs(q);
```

### 2.4 Subcolecciones vs colecciones top-level

**[RECOMMENDED]** Usar subcolecciones cuando los datos están fuertemente acoplados al padre:

```typescript
// ✅ Subcolección (datos del usuario)
users/{userId}/orders/{orderId}

// ✅ Top-level (entidad independiente)
orders/{orderId}  con  userId: string
```

---

## 03. Firebase Cloud Functions

### 3.1 Estructura de functions

**[REQUIRED]** Cloud Functions en carpeta separada `firebase-functions/`:

```
firebase-functions/
├── src/
│   ├── index.ts           # Export de todas las funciones
│   ├── triggers/
│   │   ├── onUserCreate.ts
│   │   └── onOrderStatusChange.ts
│   ├── api/
│   │   ├── send-email.ts
│   │   └── process-payment.ts
│   └── lib/
│       ├── firebase-admin.ts  # Inicialización de Admin
│       └── email.ts           # Helper de email
├── package.json
└── tsconfig.json
```

### 3.2 Inicialización de Firebase Admin

**[REQUIRED]** Firebase Admin en un solo lugar:

```typescript
// firebase-functions/src/lib/firebase-admin.ts
import * as admin from 'firebase-admin';

if (!admin.apps.length) {
  admin.initializeApp();
}

export const db = admin.firestore();
export const auth = admin.auth();
export const storage = admin.storage();
```

### 3.3 Validación con Zod en Functions

**[REQUIRED]** Todo payload validado con Zod:

```typescript
// firebase-functions/src/api/send-email.ts
import { z } from 'zod';

const SendEmailSchema = z.object({
  to: z.string().email(),
  subject: z.string().min(1).max(200),
  body: z.string().min(1).max(5000),
});

export async function handleSendEmail(
  req: { body: unknown },
  res: { status: (code: number) => { json: (data: unknown) => void } }
) {
  const validation = SendEmailSchema.safeParse(req.body);
  if (!validation.success) {
    return res.status(400).json({ error: validation.error.issues });
  }
  
  const { to, subject, body } = validation.data;
  // ... enviar email
}
```

### 3.4 CORS en Functions

**[REQUIRED]** Configurar CORS explícito en Functions HTTP:

```typescript
import * as functions from 'firebase-functions';
import cors from 'cors';

const corsHandler = cors({ 
  origin: ['https://tuapp.com', 'http://localhost:5173'],
  credentials: true 
});

export const api = functions.https.onRequest((req, res) => {
  corsHandler(req, res, async () => {
    // ... lógica
  });
});
```

---

## 04. Seguridad Firebase

### 4.1 Variables de entorno

**[REQUIRED]** Secrets de Firebase en `.env.local` (frontend) y en Functions (backend):

```bash
# Frontend (.env.local) — SOLO públicas
VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=miapp.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=miapp

# Backend (Functions) — secrets
FIREBASE_SERVICE_ACCOUNT_KEY={...}  // En Functions config
```

### 4.2 Email/Password seguro

**[REQUIRED]** Configurar reglas de contraseña en Firebase Console:

- Mínimo 8 caracteres
- Requerir email verificado para acciones sensibles
- Rate limiting en intentos de login (Firebase lo maneja)

### 4.3 Firestore Rules testing

**[REQUIRED]** Probar reglas con emulador antes de desplegar:

```bash
firebase emulators:start
# En otro terminal:
npm run test:rules
```

---

## 05. Patrones Comunes

### 5.1 Real-time listeners

**[REQUIRED]** Usar `onSnapshot` para datos en tiempo real, con cleanup:

```typescript
// ✅ Listener con cleanup
useEffect(() => {
  const unsubscribe = onSnapshot(
    query(collection(db, 'orders'), where('userId', '==', userId)),
    (snapshot) => {
      const orders = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setOrders(orders);
    }
  );
  
  return () => unsubscribe();
}, [userId]);
```

### 5.2 Batch writes

**[REQUIRED]** Operaciones atómicas con batch:

```typescript
import { writeBatch, doc } from 'firebase/firestore';

const batch = writeBatch(db);
batch.set(doc(db, 'users', userId), { name, email });
batch.set(doc(db, 'user_stats', userId), { orderCount: 0 });
await batch.commit();
```

### 5.3 Transactions

**[REQUIRED]** Lectura-escritura atómica con transactions:

```typescript
import { runTransaction, doc } from 'firebase/firestore';

await runTransaction(db, async (transaction) => {
  const productRef = doc(db, 'products', productId);
  const product = await transaction.get(productRef);
  
  if (!product.exists()) throw 'Product not found';
  if (product.data().stock < quantity) throw 'Insufficient stock';
  
  transaction.update(productRef, { stock: product.data().stock - quantity });
  transaction.set(doc(db, 'orders', newOrderId), { productId, quantity, status: 'pending' });
});
```

---

## Checklist Pre-Deploy Firebase

- [ ] `firebase.json` configurado
- [ ] Firestore Rules implementadas y probadas
- [ ] Firebase Admin SOLO en Functions/Backend
- [ ] API Key pública en frontend (no secrets)
- [ ] Cloud Functions con CORS explícito
- [ ] Validación Zod en Functions HTTP
- [ ] Real-time listeners con cleanup
- [ ] Batch writes para operaciones atómicas
