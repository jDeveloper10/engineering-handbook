---
title: "Engineering OS — Policy Profiles"
category: engineering-os
doc_type: estandar
tags: [policy-as-code, profiles, stack-detection, legacy]
summary: "Perfiles composables que aplican las reglas correctas a cada stack sin convertir estándares específicos en prohibiciones globales."
keywords: [cloudflare, react, python, firebase, migration, legacy, scope]
updated: 2026-08-03
status: current
---

# 34 — Policy Profiles

## OS-PROFILE-001 — Reglas por contexto

**[REQUIRED]** La IA compone un perfil base con perfiles detectados o declarados; no aplica una
regla de plataforma a un proyecto que no usa esa plataforma. El archivo ejecutable es
[`policy-profiles.json`](policy-profiles.json).

| Perfil | Activa | No presupone |
|---|---|---|
| `baseline` | evidencia, secretos, documentación, pruebas y cierre | un framework o proveedor concreto. |
| `react-web` | UI, accesibilidad, estados async, rendimiento web | backend, PWA u offline si no aplican. |
| `cloudflare-worker` | Workers, bindings y límites edge | que todo backend sea Worker en legacy. |
| `node-api` | contrato API, validación servidor y observabilidad | Cloudflare o Supabase. |
| `python-cli` | CLI, configuración y manejo de errores | UI web o RLS. |
| `firebase-app` | reglas de Firebase y migración gradual | Supabase como requisito inmediato. |
| `legacy-migration` | inventario, compatibilidad, rollback y adopción gradual | reescritura incidental. |

## OS-PROFILE-002 — El detector informa; no impone

**[REQUIRED]** `npm run doctor -- <ruta>` detecta perfiles desde manifiestos y configuración, pero
su salida es un diagnóstico. Si el detector se equivoca, se declara el perfil correcto y se conserva
la evidencia. El comando no modifica archivos ni lee valores de secretos.

## OS-PROFILE-003 — Herencia y excepción

El perfil `baseline` siempre se aplica. Los demás se combinan. Una excepción necesita ID de regla,
motivo, riesgo aceptado, propietario, fecha de revisión y condición de eliminación. No se silencia
con una regla global más permisiva.
