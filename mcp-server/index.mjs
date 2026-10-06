#!/usr/bin/env node
// mcp-server/index.mjs — Servidor MCP (Model Context Protocol) para el Engineering Handbook
// 100% nativo en Node.js (cero dependencias externas). Compatible con Claude Desktop, Cursor, Antigravity y Cline.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import readline from 'node:readline'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const HANDBOOK_ROOT = path.resolve(__dirname, '..')
const INDEX_PATH = path.join(HANDBOOK_ROOT, 'INDEX.json')

// Cargar índice del Handbook
function loadIndex() {
  if (!fs.existsSync(INDEX_PATH)) return { docs: [] }
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'))
  } catch (err) {
    return { docs: [] }
  }
}

// Herramientas expuestas al modelo de IA
const TOOLS = [
  {
    name: 'auto_assist',
    description: 'Herramienta de auto-detección para usuarios NO programadores y peticiones en lenguaje natural común (ej. "quiero una tienda online", "tengo un excel con clientes", "el cliente pide cosas extras", "quiero cobrar con tarjeta", "roles y permisos", "entregar proyecto"). Devuelve la solución completa: arquitectura, estándares aplicables, reglas de oro y plantillas listas.',
    inputSchema: {
      type: 'object',
      properties: {
        user_prompt: {
          type: 'string',
          description: 'La petición o deseo del usuario en palabras comunes en español o inglés sin tecnicismos.'
        }
      },
      required: ['user_prompt']
    }
  },
  {
    name: 'search_standards',
    description: 'Busca estándares, patrones, runbooks y guías técnicas en el Engineering Handbook por palabras clave o problema a resolver.',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Palabra clave o tema técnico (ej. "pagos", "rls", "migracion", "cliente", "errores", "mobile", "workers")'
        }
      },
      required: ['query']
    }
  },
  {
    name: 'get_standard',
    description: 'Obtiene el contenido completo de un estándar técnico del Handbook a partir de su ruta relativa o nombre.',
    inputSchema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Ruta relativa del archivo (ej. "03_API/WEBHOOK_IDEMPOTENCY_STANDARD.md" o "10_Code_Quality/AGENCY_CODING_STANDARD.md")'
        }
      },
      required: ['path']
    }
  },
  {
    name: 'get_rule',
    description: 'Consulta una regla de ingeniería inquebrantable por su ID (ej. S-001, DB-001, DB-008, SEC-002, ERR-001, MONEY-001, TENANT-001).',
    inputSchema: {
      type: 'object',
      properties: {
        rule_id: {
          type: 'string',
          description: 'ID de la regla a consultar (ej. "S-001", "SEC-002", "ERR-001", "MONEY-001")'
        }
      },
      required: ['rule_id']
    }
  },
  {
    name: 'get_template',
    description: 'Obtiene una plantilla lista para usar de la agencia (Discovery de clientes, Propuesta Técnica, Change Request, Handover, CI/CD Actions, RBAC).',
    inputSchema: {
      type: 'object',
      properties: {
        template_name: {
          type: 'string',
          description: 'Nombre de la plantilla (opciones: "discovery", "propuesta", "change_request", "handover", "soporte", "cicd", "rbac")',
          enum: ['discovery', 'propuesta', 'change_request', 'handover', 'soporte', 'cicd', 'rbac']
        }
      },
      required: ['template_name']
    }
  },
  {
    name: 'get_cheatsheet',
    description: 'Obtiene la guía de bolsillo rápida de 1 página con el resumen de reglas de oro y flujo de desarrollo de la agencia.',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
]

// Diccionario de plantillas conocidas
const TEMPLATE_MAP = {
  discovery: '10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md',
  propuesta: '10_Product/TEMPLATES/TEMPLATE_PROPUESTA_TECNICA.md',
  change_request: '10_Product/TEMPLATES/TEMPLATE_CHANGE_REQUEST.md',
  handover: '10_Product/TEMPLATES/TEMPLATE_ACTA_ENTREGA_HANDOVER.md',
  soporte: '10_Product/TEMPLATES/TEMPLATE_CONTRATO_SOPORTE_MENSUAL.md',
  cicd: '07_DevOps/GITHUB_ACTIONS_WORKFLOW_TEMPLATE.md',
  rbac: '04_Database/References/PATRON_RBAC_PERMISOS.md'
}

// Analizador de intención en lenguaje natural (Para usuarios no técnicos)
function analyzeHumanIntent(userPrompt) {
  const p = (userPrompt || '').toLowerCase()
  
  if (p.includes('tienda') || p.includes('e-commerce') || p.includes('vender') || p.includes('carrito') || p.includes('producto')) {
    return {
      category: 'E-Commerce / Tienda Online',
      stack: 'React 19 + Vite (o Astro) + Supabase (Catálogo/Órdenes) + Wompi/Stripe (Pagos) + Cloudflare R2 (Fotos)',
      rules: ['MONEY-001 (Precios resueltos en backend)', 'ERR-001 (Cero falsos 200)', 'API-IDEMP (Idempotencia de webhooks)'],
      standards: ['03_API/WEBHOOK_IDEMPOTENCY_STANDARD.md', '10_Product/TEMPLATES/TEMPLATE_REQUERIMIENTOS_CLIENTE.md', '05_Security/PAYMENTS_SECURITY_STANDARD.md'],
      nextSteps: [
        '1. Llenar el formulario de requerimientos para delimitar productos y pasarelas.',
        '2. Modelar tablas `products`, `orders` e `idempotency_keys` en Supabase con RLS.',
        '3. Configurar webhook de pago seguro en un Cloudflare Worker.'
      ]
    }
  }

  if (p.includes('excel') || p.includes('csv') || p.includes('importar') || p.includes('datos viejos') || p.includes('migrar clientes')) {
    return {
      category: 'Ingesta y Migración de Datos de Clientes',
      stack: 'Node.js + Zod + Supabase Client (Bulk Insert)',
      rules: ['S-001 (Validación Zod por fila)', 'MONEY-001 (Centavos enteros)'],
      standards: ['04_Database/References/GUIA_MIGRACION_DATOS_CLIENTE.md'],
      nextSteps: [
        '1. Crear el script scripts/import-client-data.mjs.',
        '2. Sanitizar emails, teléfonos y convertir precios a centavos.',
        '3. Ejecutar inserción en lotes de 500 filas con deduplicación.'
      ]
    }
  }

  if (p.includes('pagar') || p.includes('cobrar') || p.includes('pasarela') || p.includes('tarjeta') || p.includes('wompi') || p.includes('stripe') || p.includes('nowpayments') || p.includes('crypto')) {
    return {
      category: 'Integración de Pagos y Webhooks',
      stack: 'Cloudflare Workers (Backend Proxy) + Pasarela (Wompi/Stripe/NowPayments) + Supabase',
      rules: ['MONEY-001 (Precios nunca en frontend)', 'SEC-002 (Cero API keys privadas en React)', 'API-IDEMP (Idempotencia)'],
      standards: ['03_API/WEBHOOK_IDEMPOTENCY_STANDARD.md', '05_Security/PAYMENTS_SECURITY_STANDARD.md', '05_Security/SECRET_LEAK_PREVENTION_STANDARD.md'],
      nextSteps: [
        '1. Mover API keys privadas al Worker con wrangler secret put.',
        '2. Crear endpoint /api/create-payment que devuelve el checkout.',
        '3. Configurar handler de webhook con verificación HMAC y tabla processed_webhooks.'
      ]
    }
  }

  if (p.includes('roles') || p.includes('permisos') || p.includes('administrador') || p.includes('admin') || p.includes('quien puede')) {
    return {
      category: 'Roles y Permisos Granulares (RBAC & Multi-tenant)',
      stack: 'PostgreSQL + Supabase RLS (has_permission helper)',
      rules: ['TENANT-001 (Aislamiento por RLS)', 'FE-001 (Cero any en types de permisos)'],
      standards: ['04_Database/References/PATRON_RBAC_PERMISOS.md', '04_Database/References/PATRON_MULTI_TENANT_ORGANIZATIONS.md'],
      nextSteps: [
        '1. Ejecutar migración con tablas roles, permissions y user_roles.',
        '2. Crear función SQL has_permission() en Supabase.',
        '3. Proteger tablas con políticas RLS basadas en permisos.'
      ]
    }
  }

  if (p.includes('cambio') || p.includes('extra') || p.includes('pidio mas') || p.includes('nuevo boton') || p.includes('scope')) {
    return {
      category: 'Gestión de Cambios de Alcance (Scope Creep)',
      stack: 'Proceso Comercial & Gobernanza',
      rules: ['Toda petición fuera de Discovery requiere Change Request firmado.'],
      standards: ['10_Product/TEMPLATES/TEMPLATE_CHANGE_REQUEST.md'],
      nextSteps: [
        '1. Rellenar la plantilla TEMPLATE_CHANGE_REQUEST.md.',
        '2. Estimar costo adicional y semanas de extensión de plazo.',
        '3. Enviar al cliente para firma antes de programar.'
      ]
    }
  }

  if (p.includes('entregar') || p.includes('finalizar') || p.includes('garantia') || p.includes('terminar') || p.includes('cerrar')) {
    return {
      category: 'Cierre de Proyecto, Handover y Garantía',
      stack: 'QA, Despliegue y Traspaso de Cuentas',
      rules: ['FE-005 (4 estados UI)', 'SEC-002 (Escaneo de secretos en verde)'],
      standards: ['10_Product/TEMPLATES/TEMPLATE_ACTA_ENTREGA_HANDOVER.md', '06_Testing/CHECKLIST_RELEASE_PRODUCCION.md'],
      nextSteps: [
        '1. Completar el CHECKLIST_RELEASE_PRODUCCION.md al 100%.',
        '2. Transferir cuentas de Supabase y Cloudflare a la cuenta del cliente.',
        '3. Firmar el Acta de Entrega con activación de 30 días de garantía.'
      ]
    }
  }

  if (p.includes('cotizar') || p.includes('cobrar') || p.includes('cuanto') || p.includes('propuesta') || p.includes('presupuesto')) {
    return {
      category: 'Propuesta Técnico-Comercial y Cotización',
      stack: '4 Hitos (Milestones) con esquema 30/30/20/20',
      rules: ['Dividir entregas en hitos demostrables para cobrar por avance.'],
      standards: ['10_Product/TEMPLATES/TEMPLATE_PROPUESTA_TECNICA.md', '09_Architecture/STACK_SELECTION_MATRIX.md'],
      nextSteps: [
        '1. Seleccionar el stack óptimo con STACK_SELECTION_MATRIX.md.',
        '2. Personalizar TEMPLATE_PROPUESTA_TECNICA.md con fechas y montos.',
        '3. Incluir los 30 días de garantía y opción de soporte mensual recurrente.'
      ]
    }
  }

  // Fallback general inteligente
  return {
    category: 'Asistencia General de Ingeniería',
    stack: 'Cloudflare Workers + Supabase (PostgreSQL) + React 19 / Vite + Tailwind',
    rules: ['S-001 (Zod en todo input)', 'ERR-001 (Cero falsos 200)', 'FE-001 (Cero any)'],
    standards: ['CHEATSHEET_OPERATIVO.md', '00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md', '10_Code_Quality/AGENCY_CODING_STANDARD.md'],
    nextSteps: [
      '1. Consultar CHEATSHEET_OPERATIVO.md para ver el flujo en 4 pasos.',
      '2. Buscar estándares específicos con search_standards().',
      '3. Ejecutar Spec -> Schema Zod -> Test -> Código.'
    ]
  }
}

// Ejecución de herramientas
function handleToolCall(name, args) {
  const indexData = loadIndex()
  const docs = indexData.docs || []

  switch (name) {
    case 'auto_assist': {
      const intent = analyzeHumanIntent(args.user_prompt)
      const text = `🎯 **AUTO-DETECCIÓN DE REQUERIMIENTO (AGENCY-OS)**\n\n` +
        `🏷️ **Categoría Identificada:** ${intent.category}\n` +
        `🏛️ **Stack Arquitectónico Recomendado:** ${intent.stack}\n\n` +
        `🛡️ **Reglas Inquebrantables Aplicables:**\n${intent.rules.map(r => `  - ${r}`).join('\n')}\n\n` +
        `📚 **Estándares y Plantillas del Handbook a Usar:**\n${intent.standards.map(s => `  - [${s}]`).join('\n')}\n\n` +
        `🚀 **Plan de Acción Paso a Paso para la IA:**\n${intent.nextSteps.join('\n')}\n\n` +
        `💡 *La IA debe guiar al usuario aplicando directamente estos estándares sin pedirle detalles técnicos complejos.*`

      return {
        content: [{ type: 'text', text }]
      }
    }

    case 'search_standards': {
      const query = (args.query || '').toLowerCase()
      const tokens = query.split(/\s+/).filter(Boolean)
      const results = []

      for (const doc of docs) {
        let score = 0
        const title = (doc.title || '').toLowerCase()
        const summary = (doc.summary || '').toLowerCase()
        const keywords = (doc.keywords || []).map(k => String(k).toLowerCase())
        const tags = (doc.tags || []).map(t => String(t).toLowerCase())
        const docPath = (doc.path || '').toLowerCase()

        for (const token of tokens) {
          if (title.includes(token)) score += 15
          if (docPath.includes(token)) score += 10
          if (keywords.some(k => k.includes(token))) score += 8
          if (tags.some(t => t.includes(token))) score += 6
          if (summary.includes(token)) score += 4
        }

        if (score > 0) results.push({ doc, score })
      }

      results.sort((a, b) => b.score - a.score)
      const top = results.slice(0, 5)

      if (top.length === 0) {
        return {
          content: [{ type: 'text', text: `No se encontraron documentos exactos para "${query}". Intenta buscar por: db, rls, pagos, auth, front, test, deploy, cliente, workers.` }]
        }
      }

      const output = top.map((r, i) => 
        `[${i+1}] ${r.doc.title}\n📁 Ruta: ${r.doc.path}\n💡 Resumen: ${r.doc.summary || 'N/A'}\n🏷️ Tags: ${(r.doc.tags || []).join(', ')}`
      ).join('\n\n')

      return {
        content: [{ type: 'text', text: `Resultados encontrados en el Handbook:\n\n${output}` }]
      }
    }

    case 'get_standard': {
      const targetRel = (args.path || '').replace(/^\/+/, '')
      if (!targetRel) {
        return {
          content: [{ type: 'text', text: '❌ Debes especificar el parámetro "path" (ej. "05_Mobile/REACT_NATIVE_EXPO_STANDARD.md"). Usa search_standards para encontrarlo.' }]
        }
      }
      const fullPath = path.join(HANDBOOK_ROOT, targetRel)

      if (!fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
        return {
          content: [{ type: 'text', text: `❌ No se encontró el archivo: ${targetRel}. Usa search_standards para encontrar la ruta exacta.` }]
        }
      }

      const content = fs.readFileSync(fullPath, 'utf-8')
      return {
        content: [{ type: 'text', text: content }]
      }
    }

    case 'get_rule': {
      const ruleId = (args.rule_id || '').toUpperCase().trim()
      const agentsMdPath = path.join(HANDBOOK_ROOT, 'AGENTS.md')
      const content = fs.readFileSync(agentsMdPath, 'utf-8')
      
      const lines = content.split('\n')
      const matchingLines = lines.filter(l => l.includes(ruleId))

      if (matchingLines.length === 0) {
        return {
          content: [{ type: 'text', text: `Regla ${ruleId} no encontrada en la tabla principal de AGENTS.md. Consulta el estándar del dominio correspondiente con search_standards.` }]
        }
      }

      return {
        content: [{ type: 'text', text: `Regla encontrada en AGENTS.md:\n\n${matchingLines.join('\n')}` }]
      }
    }

    case 'get_template': {
      const relPath = TEMPLATE_MAP[args.template_name]
      if (!relPath) {
        return {
          content: [{ type: 'text', text: `Plantilla desconocida: ${args.template_name}. Opciones válidas: ${Object.keys(TEMPLATE_MAP).join(', ')}` }]
        }
      }

      const fullPath = path.join(HANDBOOK_ROOT, relPath)
      const content = fs.readFileSync(fullPath, 'utf-8')
      return {
        content: [{ type: 'text', text: content }]
      }
    }

    case 'get_cheatsheet': {
      const fullPath = path.join(HANDBOOK_ROOT, 'CHEATSHEET_OPERATIVO.md')
      const content = fs.readFileSync(fullPath, 'utf-8')
      return {
        content: [{ type: 'text', text: content }]
      }
    }

    default:
      return {
        content: [{ type: 'text', text: `Herramienta no implementada: ${name}` }]
      }
  }
}

// Bucle JSON-RPC por STDIN / STDOUT (Protocolo Oficial MCP)
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
})

rl.on('line', (line) => {
  if (!line.trim()) return

  let msg
  try {
    msg = JSON.parse(line)
  } catch (err) {
    return
  }

  const { id, method, params } = msg

  if (method === 'initialize') {
    sendResponse(id, {
      protocolVersion: '2024-11-05',
      capabilities: {
        tools: {}
      },
      serverInfo: {
        name: 'engineering-handbook-mcp',
        version: '1.0.0'
      }
    })
  } else if (method === 'notifications/initialized') {
    // No requiere respuesta
  } else if (method === 'tools/list') {
    sendResponse(id, {
      tools: TOOLS
    })
  } else if (method === 'tools/call') {
    const { name, arguments: toolArgs } = params || {}
    try {
      const result = handleToolCall(name, toolArgs || {})
      sendResponse(id, result)
    } catch (err) {
      sendResponse(id, {
        content: [{ type: 'text', text: `Error al ejecutar ${name}: ${err.message}` }],
        isError: true
      })
    }
  } else if (method === 'ping') {
    sendResponse(id, {})
  } else {
    // Método no soportado
    if (id !== undefined) {
      sendError(id, -32601, `Método no soportado: ${method}`)
    }
  }
})

function sendResponse(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id, result }) + '\n')
}

function sendError(id, code, message) {
  process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id, error: { code, message } }) + '\n')
}
