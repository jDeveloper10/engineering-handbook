---
title: "Playbook: Caída de API"
category: 11_Debugging
doc_type: runbook
tags: [incident, playbook, api, 500]
summary: "Playbook ante API caída con error 500 o timeout: triage inmediato, diagnóstico diferenciado de error y de timeout, y mitigación rápida."
keywords: [incident, playbook, api, 500, caida, ante, error, timeout, triage, inmediato, diagnostico, diferenciado, mitigacion, rapida]
updated: 2026-07-27
status: current
---

# 🚨 Playbook: La API está Caída (Error 500 / Timeout)

Si el frontend reporta masivamente "Error de conexión" o "Status 500", sigue estos pasos exactos (no saltes ninguno).

## 1. Triage Inmediato
1. ¿Es solo un endpoint, o toda la API? 
2. Haz curl manual o Postman: `curl -I https://api.tudominio.com/health`
3. Si el status es `522` o `524` (Cloudflare Timeout): El problema es que el origen (o Supabase) está bloqueando a Cloudflare o demorando demasiado.
4. Si el status es `500`: El código del Worker falló internamente.

## 2. Diagnóstico del Error 500
1. Lanza los logs en vivo: `npx wrangler tail --env production`
2. Dispara la petición problemática.
3. Observa la excepción exacta en consola.
   - *¿Falta una variable de entorno en producción que sí está en local?* Verifica con `npx wrangler secret list`.
   - *¿Cambió la firma de respuesta de Supabase?*

## 3. Diagnóstico de Timeouts
Si el Worker no tira excepciones pero se queda colgado, 95% de las veces es Supabase.
1. Revisa el estado de la base de datos (Supabase Dashboard -> Database -> Health).
2. Verifica si excediste el límite de conexiones concurrentes en Supabase (Connection Pooling). El Worker debe estar configurado para usar IPv4 pooling, no conexiones directas al puerto 5432.

## 4. Resolución / Mitigación Rápida
- **Si es un deploy malo reciente**: Rollback a la versión anterior con Wrangler (ver `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md`).
- **Si es tráfico masivo tirando la DB**: Activa Cache de lectura urgente en el Worker en el endpoint afectado, devolviendo la versión estancada (Stale-while-revalidate) mientras la DB se recupera.
