---
title: "Dominio Database — Índice"
category: 04_Database
doc_type: referencia
tags: [database, indice]
summary: "Índice del dominio Database. El estándar operativo vive en DATABASE_ENGINEERING_STANDARD.md."
keywords: [database, indice, postgres, supabase, d1]
updated: 2026-07-09
status: current
---

# Dominio Database — PostgreSQL, Supabase y D1

Este dominio define las reglas de modelado relacional, índices secundarios, políticas de aislamiento Row Level Security (RLS), patrones de permisos RBAC, recetas de migración y planes de contingencia (Disaster Recovery).

## Documentos del Dominio

| Documento | Tipo | Descripción |
|---|---|---|
| [DATABASE_ENGINEERING_STANDARD.md](DATABASE_ENGINEERING_STANDARD.md) | Estándar | Reglas inquebrantables de base de datos: DB-001 a DB-010, snake_case, tipos monetarios |
| [OPTIMIZACION_CONSULTAS_SQL_STANDARD.md](OPTIMIZACION_CONSULTAS_SQL_STANDARD.md) | Estándar | Estándar maestro: índices parciales, cursor pagination, eliminación N+1 y EXPLAIN BUFFERS |
| [References/PATRON_RBAC_PERMISOS.md](References/PATRON_RBAC_PERMISOS.md) | Patrón | Esquema SQL de roles y permisos reutilizable con helper has_permission() para RLS |
| [References/PATRON_MULTI_TENANT_ORGANIZATIONS.md](References/PATRON_MULTI_TENANT_ORGANIZATIONS.md) | Patrón | Arquitectura multi-tenant para SaaS: organizaciones, membresías y aislamiento RLS |
| [References/GUIA_MIGRACION_DATOS_CLIENTE.md](References/GUIA_MIGRACION_DATOS_CLIENTE.md) | Runbook | Ingesta y limpieza masiva de archivos Excel/CSV desordenados con Zod y lotes |
| [References/DATABASE_DISASTER_RECOVERY_MIGRATION.md](References/DATABASE_DISASTER_RECOVERY_MIGRATION.md) | Runbook | Plan de migración de emergencia y portabilidad (pg_dump, restore en VPS Docker, D1 a Postgres) |
| [References/DATABASE_MIGRATION_RECIPES.md](References/DATABASE_MIGRATION_RECIPES.md) | Referencia | Recetas de migración sin downtime (añadir NOT NULL, renombrar columnas, índices concurrentes) |
| [References/RLS_POLICIES_LIBRARY.md](References/RLS_POLICIES_LIBRARY.md) | Referencia | Biblioteca de políticas RLS multi-tenant para Supabase |
| [References/DATABASE_COMMON_QUERIES.md](References/DATABASE_COMMON_QUERIES.md) | Referencia | Consultas comunes optimizadas y análisis con EXPLAIN ANALYZE |
| [References/DATABASE_PERFORMANCE.md](References/DATABASE_PERFORMANCE.md) | Referencia | Optimización de rendimiento, connection pooling con Supavisor e índices |


