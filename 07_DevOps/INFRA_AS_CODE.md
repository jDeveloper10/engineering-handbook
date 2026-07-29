---
title: "Infraestructura como Código"
category: 07_DevOps
tags: [devops, iac, terraform, wrangler]
summary: "Reglas IaC-001 a IaC-004: toda la infraestructura de Cloudflare y Supabase definida en código con Terraform o Wrangler, nunca configurada a mano desde un panel."
keywords: [iac, terraform, wrangler, infraestructura, reproducible, dashboard]
updated: 2026-07-27
status: current
---

# Infraestructura como Código (IaC-001 a IaC-004)

## 🎯 Objetivo
Toda la infraestructura Cloudflare + Supabase debe estar definida en código (Terraform/Wrangler), NUNCA configurada a mano desde el dashboard.

---

## ⚡ REGLAS INQUEBRANTABLES

### IaC-001: TODO RECURSO CLOUDFLARE EN TERRAFORM

```hcl
# terraform/main.tf
terraform {
  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

# API Gateway Worker
resource "cloudflare_worker_script" "api_gateway" {
  account_id = var.cloudflare_account_id
  name       = "api-gateway"
  content    = file("../apps/api-gateway/dist/index.js")
  
  plain_text_binding {
    name = "SUPABASE_URL"
    text = var.supabase_url
  }
  
  secret_text_binding {
    name = "SUPABASE_KEY"
    text = var.supabase_anon_key
  }
}

# R2 Bucket
resource "cloudflare_r2_bucket" "uploads" {
  account_id = var.cloudflare_account_id
  name       = "omnisuite-uploads"
  location   = "WNAM" # Oeste Norteamérica
}

# KV Namespace
resource "cloudflare_workers_kv_namespace" "cache" {
  account_id = var.cloudflare_account_id
  title      = "omnisuite-cache"
}

# Durable Object para Rate Limiting
resource "cloudflare_workers_kv_namespace" "rate_limiter" {
  account_id = var.cloudflare_account_id
  title      = "omnisuite-rate-limiter"
}
```

---

### IaC-002: ENTORNOS COMO CÓDIGO

```hcl
# terraform/environments/
# ├── dev.tfvars
# ├── staging.tfvars
# └── production.tfvars

# dev.tfvars
environment = "dev"
supabase_url = "https://dev-xxxxx.supabase.co"
domain = "dev.omnisuite.com"
rate_limit_public = 100  # Más permisivo en dev

# production.tfvars
environment = "production"
supabase_url = "https://prod-xxxxx.supabase.co"
domain = "omnisuite.com"
rate_limit_public = 10   # Estricto en producción
```

```bash
# Deploy por entorno
terraform apply -var-file="environments/production.tfvars"
```

---

### IaC-003: SUPABASE COMO CÓDIGO (MIGRACIONES)

```sql
-- supabase/migrations/20240315_initial_schema.sql
-- UP
CREATE TABLE clients (...);
CREATE TABLE proposals (...);

-- DOWN
DROP TABLE IF EXISTS proposals;
DROP TABLE IF EXISTS clients;
```

```bash
# CI/CD ejecuta migraciones automáticamente
npx supabase db push --db-url $SUPABASE_URL
```

---

### IaC-004: WAF Y SEGURIDAD COMO CÓDIGO

```hcl
# Cloudflare WAF Rules
resource "cloudflare_ruleset" "waf" {
  zone_id = var.zone_id
  name    = "default"
  kind    = "zone"
  phase   = "http_request_firewall_managed"

  rules {
    action = "block"
    expression = "(ip.geoip.country ne \"US\" and ip.geoip.country ne \"MX\" and not cf.client.bot)"
    description = "Block traffic outside US/MX"
    enabled = true
  }
  
  rules {
    action = "managed_challenge"
    expression = "(cf.threat_score gt 14)"
    description = "Challenge suspicious requests"
    enabled = true
  }
}
```
