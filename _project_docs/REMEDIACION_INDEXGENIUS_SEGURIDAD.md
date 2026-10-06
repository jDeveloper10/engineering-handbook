---
title: "Plan de Remediación de Seguridad: IndexGenius / IngenusFX"
category: _project_docs
doc_type: runbook
tags: [seguridad, ingenusfx, indexgenius, metaapi, r2, nowpayments, remediation]
summary: "Plan de acción y pasos exactos para cualquier agente de IA o desarrollador: eliminar variables VITE_ con secretos (MetaApi, R2, NowPayments), mover llamadas a trading-worker y payments-worker, y rotar claves en producción."
keywords: [ingenusfx, indexgenius, metaapi, r2, nowpayments, secretos, fix, remediacion]
updated: 2026-08-14
status: current
---

# PLAN DE REMEDIACIÓN DE SEGURIDAD — INDEXGENIUS / INGENUSFX

> **Prioridad:** 🔴 **CRÍTICA (Bloqueo de Deploy)**  
> **Afecta a:** `E:\Trabajo\03_Trading\ingenusfx` y despliegues en `indexgeniusacademy.com` / `indexgenius.app`.  
> **Estándar de referencia:** [05_Security/SECRET_LEAK_PREVENTION_STANDARD.md](../05_Security/SECRET_LEAK_PREVENTION_STANDARD.md) y [08_Cloud/PATRON_R2_UPLOAD_SEGURO.md](../08_Cloud/PATRON_R2_UPLOAD_SEGURO.md).

---

## 🎯 Objetivo de la Tarea para el Agente

Eliminar el 100% de los secretos y tokens de terceros del frontend de React (`src/`), encapsular toda la lógica privada en los Cloudflare Workers existentes (`trading-worker/`, `payments-worker/`, `admin-worker/`), y rotar las credenciales en producción.

---

## 📋 Lista de Tareas Paso a Paso (Para el Agente)

### Paso 1: Limpieza del archivo `.env` del Frontend
En `ingenusfx/.env`, **ELIMINAR** todas las variables que contienen secretos privados:

```diff
- VITE_METAAPI_ACCOUNT_ID=...
- VITE_METAAPI_TOKEN=...
- VITE_R2_ACCESS_KEY_ID=...
- VITE_R2_SECRET_ACCESS_KEY=...
- VITE_NOWPAYMENTS_API_KEY=...
- VITE_NOWPAYMENTS_IPN_SECRET=...
```

**Dejar únicamente en `.env`:**
```env
VITE_SUPABASE_URL=https://lferlkuuvxtcsyonleqi.supabase.co
VITE_SUPABASE_ANON_KEY=...
VITE_API_URL=https://api.indexgeniusacademy.com (o URL del Worker)
VITE_R2_PUBLIC_URL=https://recursos.indexgeniusacademy.com
```

---

### Paso 2: Mover MetaApi a `trading-worker`
1. **Configurar el secreto en el Worker:**
   ```bash
   cd trading-worker
   npx wrangler secret put METAAPI_TOKEN
   npx wrangler secret put METAAPI_ACCOUNT_ID
   ```
2. **Crear endpoint en `trading-worker`:**
   - Crear handler `/api/trading/accounts` y `/api/trading/positions`.
   - Exigir `requireAuth(request, env)` para validar que el usuario tenga sesión en Supabase.
   - El Worker hace el `fetch()` a MetaApi con `env.METAAPI_TOKEN`.
3. **Actualizar el Frontend:**
   - En `src/services/` o donde se llame a MetaApi, reemplazar la llamada directa por un `fetch('${VITE_API_URL}/api/trading/accounts')` enviando el token de sesión en `Authorization: Bearer <token>`.

---

### Paso 3: Mover NowPayments a `payments-worker`
1. **Configurar el secreto en el Worker:**
   ```bash
   cd payments-worker
   npx wrangler secret put NOWPAYMENTS_API_KEY
   npx wrangler secret put NOWPAYMENTS_IPN_SECRET
   ```
2. **Crear endpoints en `payments-worker`:**
   - `/api/payments/create-invoice`: Recibe el plan elegido, resuelve el monto en el backend (`MONEY-001`) y crea la orden en NowPayments.
   - `/api/payments/webhook`: Recibe el IPN de NowPayments, valida la firma criptográfica HMAC con `env.NOWPAYMENTS_IPN_SECRET` y actualiza la suscripción en Supabase.
3. **Actualizar el Frontend:**
   - Eliminar cualquier llamada directa a `https://api.nowpayments.io` desde `src/`.

---

### Paso 4: Mover Subida de Archivos R2 a `admin-worker`
1. En `admin-worker/wrangler.toml`, enlazar el bucket directamente:
   ```toml
   [[r2_buckets]]
   binding = "RECURSOS_BUCKET"
   bucket_name = "indexgenius-recursos"
   ```
2. Usar el patrón de [08_Cloud/PATRON_R2_UPLOAD_SEGURO.md](../08_Cloud/PATRON_R2_UPLOAD_SEGURO.md) (`env.RECURSOS_BUCKET.put()`).
3. El frontend sube vía `FormData` a `${VITE_API_URL}/api/admin/upload`.

---

### Paso 5: Verificación y Rotación
1. **Rotar credenciales:**
   - Generar un nuevo token en MetaApi y revocar el anterior (`eyJhbGci...`).
   - Rotar las claves de NowPayments y de R2 en el panel de Cloudflare.
2. **Correr el escáner de seguridad antes de build:**
   ```bash
   node tools/scan-bundle-secrets.mjs dist
   ```
3. **Verificar que no queden rastros:**
   ```bash
   grep -rnI "eyJhbGciOi\|sk_live_\|NOWPAYMENTS" src/
   ```
   *Debe devolver 0 coincidencias.*
