#!/usr/bin/env node
// mcp-server/installer.mjs — Instalador automático del MCP del Handbook en todas las IAs
import fs from 'node:fs'
import path from 'node:path'
import os from 'os'

import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const HANDBOOK_ROOT = path.resolve(__dirname, '..')
const SERVER_SCRIPT = path.join(HANDBOOK_ROOT, 'mcp-server', 'index.mjs').replace(/\\/g, '/')

console.log('==================================================================')
console.log('🚀 INSTALADOR AUTOMÁTICO DE MCP — ENGINEERING HANDBOOK')
console.log('==================================================================')
console.log(`📁 Ruta del Servidor MCP: ${SERVER_SCRIPT}\n`)

const mcpConfigEntry = {
  command: 'node',
  args: [SERVER_SCRIPT]
}

const targets = [
  {
    name: 'Claude Desktop',
    path: path.join(os.homedir(), 'AppData', 'Roaming', 'Claude', 'claude_desktop_config.json')
  },
  {
    name: 'Cursor IDE (Global)',
    path: path.join(os.homedir(), '.cursor', 'mcp.json')
  },
  {
    name: 'Roo Code / Cline (VS Code)',
    path: path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User', 'globalStorage', 'rooveterinaryinc.roo-cline', 'settings', 'cline_mcp_settings.json')
  },
  {
    name: 'Antigravity IDE (User Config)',
    path: path.join(os.homedir(), '.gemini', 'config', 'mcp_config.json')
  },
  {
    name: 'Handbook Local Workspace (.mcp.json)',
    path: path.join(HANDBOOK_ROOT, '.mcp.json')
  }
]

let installedCount = 0

for (const target of targets) {
  try {
    const dir = path.dirname(target.path)
    if (!fs.existsSync(dir)) {
      // Si la carpeta de la app no existe en este PC, omitir silenciosamente
      continue
    }

    let config = { mcpServers: {} }
    if (fs.existsSync(target.path)) {
      try {
        config = JSON.parse(fs.readFileSync(target.path, 'utf-8'))
        if (!config.mcpServers) config.mcpServers = {}
      } catch {
        config = { mcpServers: {} }
      }
    }

    config.mcpServers['engineering-handbook'] = mcpConfigEntry

    fs.writeFileSync(target.path, JSON.stringify(config, null, 2), 'utf-8')
    console.log(`✅ Instalado con éxito en: ${target.name}`)
    console.log(`   📄 Archivo: ${target.path}\n`)
    installedCount++
  } catch (err) {
    console.warn(`⚠️ No se pudo configurar en ${target.name}: ${err.message}`)
  }
}

// Crear también .mcp.json en la raíz del Handbook
try {
  const rootMcp = path.join(HANDBOOK_ROOT, '.mcp.json')
  const rootConfig = {
    mcpServers: {
      'engineering-handbook': mcpConfigEntry
    }
  }
  fs.writeFileSync(rootMcp, JSON.stringify(rootConfig, null, 2), 'utf-8')
  console.log(`✅ Archivo .mcp.json creado en la raíz del repositorio: ${rootMcp}\n`)
  installedCount++
} catch {}

console.log('==================================================================')
console.log(`🎉 ¡PROCESO COMPLETADO! El MCP quedó instalado en ${installedCount} entornos.`)
console.log('Ahora cualquier IA conectada tiene acceso a las siguientes herramientas:')
console.log('  🔍 search_standards(query)   ➔ Búsqueda en los 195 estándares')
console.log('  📖 get_standard(path)        ➔ Lectura completa del estándar')
console.log('  🛡️ get_rule(rule_id)         ➔ Consulta rápida de reglas (S-001, DB-008...)')
console.log('  📋 get_template(name)        ➔ Descarga de plantillas (Discovery, CI/CD...)')
console.log('  ⚡ get_cheatsheet()          ➔ Guía de bolsillo de 1 página')
console.log('==================================================================')
