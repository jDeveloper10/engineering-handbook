---
title: "Estándar y Toolkit de Auditoría Web con Kali Linux (WSL)"
category: 05_Security
doc_type: estandar
tags: [seguridad, auditoria, kali-linux, wsl, nmap, sslscan, ffuf, nuclei, pre-lanzamiento]
summary: "Protocolo y herramientas de auditoría de seguridad defensiva y caja negra usando Kali Linux en WSL 2: escaneo de puertos, análisis TLS/SSL, descubrimiento de archivos sensibles expuestos (.env, .git), validación de CORS y escaneo automatizado con Nuclei."
keywords: [kali, wsl, auditoria, pentesting-defensivo, nmap, sslscan, ffuf, nuclei, cors, csp, pre-lanzamiento, hardening]
updated: 2026-08-14
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "OWASP Web Security Testing Guide (WSTG) v4.2"
  - "OWASP ASVS v4.0.3"
  - "05_Security/SECURITY_ENGINEERING_STANDARD.md"
  - "05_Security/EXTERNAL_AUDIT_CHECKLIST.md"
---

# ESTÁNDAR Y TOOLKIT DE AUDITORÍA WEB CON KALI LINUX (WSL)

> **Capa 1 (la regla):** Ningún sistema, API o frontend web se promueve a producción sin pasar una auditoría de caja negra automatizada que verifique la ausencia de puertos directos expuestos, cifrados débiles, archivos de configuración filtrados y cabeceras inseguras.  
> **Capa 2 (implementación):** Laboratorio local de pruebas ejecutado en **Kali Linux sobre WSL 2**, utilizando herramientas estándar de la industria (`nmap`, `sslscan`, `ffuf`, `curl`, `nuclei`).

---

## 1. Setup del Entorno en Kali Linux (WSL 2)

**[REQUIRED]** El entorno de auditoría debe mantenerse actualizado y con el toolkit base instalado.

### 1.1 Inicialización de la distribución
```bash
# Desde PowerShell / Terminal de Windows
wsl -d kali-linux
```

### 1.2 Instalación del toolkit de auditoría
```bash
# Actualizar repositorios
sudo apt update && sudo apt upgrade -y

# Instalar herramientas de escaneo y fuzzing
sudo apt install -y \
  nmap \
  sslscan \
  nikto \
  curl \
  jq \
  httpie \
  ffuf \
  dirsearch \
  dnsutils \
  whois \
  nuclei \
  seclists
```

---

## 2. Los 5 Flujos de Auditoría Obligatorios

```
                  ┌─────────────────────────────────────┐
                  │   PIPELINE DE AUDITORÍA (KALI WSL)  │
                  └──────────────────┬──────────────────┘
                                     │
       ┌──────────────┬──────────────┼──────────────┬──────────────┐
       ▼              ▼              ▼              ▼              ▼
 1. Red & Puertos 2. Cifrado TLS 3. Archivos (.env) 4. CORS/Headers 5. CVEs & Paneles
    (nmap)         (sslscan)        (ffuf)          (curl)         (nuclei)
```

---

### AUDIT-001: Auditoría de Red y Superficie de Ataque (`nmap`)

**[REQUIRED]** Ningún servidor de backend o VPS puede exponer puertos de aplicación interna (ej. Node 3000, Python 8000, Vite 5173, Postgres 5432, MySQL 3306) directamente a internet. Toda petición debe entrar por reverse proxy (Caddy / Nginx) con TLS o mediante Cloudflare Tunnel.

**Por qué:** Exponer puertos internos directamente elude los firewalls de aplicación (WAF), expone middlewares desprotegidos y permite ataques de denegación de servicio o explotación directa de versiones vulnerables de runtime.

#### Comando de Verificación (Kali):
```bash
# Escaneo de los 1000 puertos principales y detección de servicios
nmap -Pn -sV --open tu-vps-ip

# Escaneo completo de 65,535 puertos para verificación de pre-lanzamiento
nmap -Pn -p- --open tu-vps-ip
```

* **Resultado esperado:** Únicamente puertos `22` (SSH con clave pública), `80` (HTTP → redirección forzada a HTTPS) y `443` (HTTPS) abiertos.

---

### AUDIT-002: Auditoría de Cifrado y Protocolos TLS (`sslscan`)

**[REQUIRED]** Todas las conexiones públicas deben negociar exclusivamente TLS 1.2 o TLS 1.3. Quedan terminantemente prohibidos SSLv2, SSLv3, TLS 1.0, TLS 1.1 y suites de cifrado débiles (RC4, 3DES, ciphers nulos o CBC vulnerables).

**Por qué:** Protocolos y cifrados obsoletos permiten ataques de degradación (*downgrade attacks*) e intercepción pasiva o activa de credenciales y tokens JWT.

#### Comandos de Verificación (Kali):
```bash
# Análisis exhaustivo de ciphers, curvas elípticas y certificados
sslscan tu-dominio.com

# O mediante scripts Nmap
nmap -Pn --script ssl-enum-ciphers -p 443 tu-dominio.com
```

* **Resultado esperado:** Calificación "Grade A" o "Strong", sin cifrados en rojo ni soporte para protocolos anteriores a TLS 1.2.

---

### AUDIT-003: Fuzzing de Archivos Sensibles Expuestos (`ffuf`)

**[REQUIRED]** Prohibido el acceso público a archivos `.env`, directorios `.git`, copias de seguridad (`.bak`, `.old`, `.sql`) o archivos temporales de editores (`.swp`).

**Por qué:** La filtración de un archivo `.env` o una carpeta `.git` descarga en segundos todas las claves de base de datos, credenciales de Stripe y secretos del servidor.

#### Comando de Verificación (Kali):
```bash
# Fuzzing de rutas críticas con ffuf
ffuf -u https://tu-dominio.com/FUZZ \
     -w /usr/share/seclists/Discovery/Web-Content/common.txt \
     -mc 200,301,302 \
     -e .env,.git,.bak,.sql,.json

# O búsqueda directa rápida con dirsearch
dirsearch -u https://tu-dominio.com -e env,git,bak,sql,json -x 404,403
```

* **Resultado esperado:** Códigos `404` para todas las rutas sensibles. Ningún `200 OK` con contenido confidencial.

---

### AUDIT-004: Verificación de Cabeceras de Seguridad y CORS (`curl`)

**[REQUIRED]** 
1. **CORS:** El header `Access-Control-Allow-Origin` debe devolver una lista blanca fija o el dominio de origen exacto del frontend, **nunca** el comodín `*` en endpoints autenticados ni reflejar arbitrariamente el header `Origin` enviado por el cliente.
2. **Security Headers:** Obligatorio incluir `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` y una `Content-Security-Policy` restrictiva sin comodines globales (`https:`).

#### Script de Verificación Automatizado (Kali):
```bash
D="tu-dominio.com"

# 1. Probar que CORS no refleje un origen malicioso
curl -s -D - -o /dev/null -H "Origin: https://evil-attacker.com" "https://api.$D" | grep -i access-control-allow-origin

# 2. Validar presencia de headers de hardening
curl -s -D - -o /dev/null "https://$D" | grep -iE "strict-transport|x-content-type|x-frame|content-security-policy|referrer-policy"
```

---

### AUDIT-005: Escaneo Automatizado de Vulnerabilidades y Misconfigs (`nuclei`)

**[RECOMMENDED]** Ejecutar un escaneo con plantillas de Nuclei antes de liberar una versión mayor a producción para detectar CVEs conocidos, paneles de administración expuestos y malas configuraciones de nube (Cloudflare, Supabase, buckets S3/R2 abiertos).

#### Comando de Verificación (Kali):
```bash
# Actualizar templates de seguridad comunitarios
nuclei -update-templates

# Escanear tecnologías expuestas, misconfigs y paneles públicos
nuclei -u https://tu-dominio.com \
       -tags misconfig,exposure,panel,cve \
       -severity low,medium,high,critical
```

---

## 3. Checklist Corto de Auditoría Pre-Lanzamiento

Antes de considerar una aplicación o API lista para producción, ejecutar este checklist de 60 segundos en Kali WSL:

- [ ] **[AUDIT-001] Puertos VPS:** `nmap -Pn --top-ports 100 $IP` solo muestra 22, 80 y 443 abiertos.
- [ ] **[AUDIT-002] Cifrado TLS:** `sslscan $DOMINIO` confirma soporte exclusivo de TLS 1.2 y 1.3 con Grade A.
- [ ] **[AUDIT-003] Archivos Ocultos:** `curl -s -o /dev/null -w "%{http_code}\n" https://$DOMINIO/.env` devuelve `404`.
- [ ] **[AUDIT-004] CORS Seguro:** Probar con `Origin: https://malicious.com` no refleja el atacante.
- [ ] **[AUDIT-005] Cabeceras:** HSTS, X-Content-Type-Options y CSP presentes en todas las respuestas.
- [ ] **[AUDIT-006] Nuclei Clean:** Escaneo final sin hallazgos de severidad `high` o `critical`.
