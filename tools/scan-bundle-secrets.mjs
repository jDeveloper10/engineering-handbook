#!/usr/bin/env node
/**
 * Escáner de seguridad para bundles frontend y código fuente.
 * Detecta tokens JWT, claves privadas, credenciales de Stripe/AWS
 * y secretos de backend antes de desplegar a producción.
 */

import fs from 'fs'
import path from 'path'

// Patrones sin flag /g para garantizar determinismo estricto con RegExp.test()
const FORBIDDEN_PATTERNS = [
  { name: 'JWT Token con claims sensibles', regex: /eyJhbGciOi[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/ },
  { name: 'Stripe Secret Key', regex: /sk_live_[0-9a-zA-Z]{24,}/ },
  { name: 'Stripe Restricted Key', regex: /rk_live_[0-9a-zA-Z]{24,}/ },
  { name: 'Private Key PEM', regex: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: 'AWS Access Key', regex: /AKIA[0-9A-Z]{16}/ },
  { name: 'Supabase Service Role', regex: /service_role/i }
]

const TARGET_DIRS = process.argv.slice(2).length > 0 ? process.argv.slice(2) : ['./dist', './src']

function scanDirectory(dir) {
  if (!fs.existsSync(dir)) {
    return 0
  }

  let foundViolations = 0
  const files = fs.readdirSync(dir)

  for (const file of files) {
    const fullPath = path.join(dir, file)
    const stat = fs.statSync(fullPath)

    if (stat.isDirectory()) {
      foundViolations += scanDirectory(fullPath)
    } else if (file.endsWith('.js') || file.endsWith('.ts') || file.endsWith('.tsx') || file.endsWith('.html') || file.endsWith('.json')) {
      // Ignorar herramientas de build internas o metadatos de índices
      if (file.includes('scan-bundle-secrets') || file === 'package-lock.json' || file === 'INDEX.json') continue

      const content = fs.readFileSync(fullPath, 'utf8')
      for (const pattern of FORBIDDEN_PATTERNS) {
        if (pattern.regex.test(content)) {
          // Si es un patrón JWT pero corresponde a una anon key pública explícita (no service_role)
          if (pattern.name.includes('JWT') && content.includes('sb_publishable_') && !content.includes('service_role')) {
            continue
          }

          console.error(`\x1b[31m[ERROR DE SEGURIDAD] Se detectó ${pattern.name} en: ${fullPath}\x1b[0m`)
          foundViolations++
        }
      }
    }
  }
  return foundViolations
}

console.log(`🔍 Escaneando directorios (${TARGET_DIRS.join(', ')}) en busca de secretos expuestos...`)
let totalViolations = 0

for (const dir of TARGET_DIRS) {
  totalViolations += scanDirectory(dir)
}

if (totalViolations > 0) {
  console.error(`\x1b[31m❌ BUILD BLOQUEADO: Se encontraron ${totalViolations} secretos en los archivos analizados.\x1b[0m`)
  process.exit(1)
} else {
  console.log('\x1b[32m✅ Escaneo completado: 0 secretos expuestos.\x1b[0m')
}
