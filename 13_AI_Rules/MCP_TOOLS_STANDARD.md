---
title: "Estándar de Servidores y Herramientas MCP (Model Context Protocol)"
category: 13_AI_Rules
doc_type: estandar
tags: [mcp, model-context-protocol, ai, claude, tools, automation, typescript]
summary: "Estándar para la creación, configuración y consumo de servidores MCP (Model Context Protocol) en el ecosistema: integración con Supabase, Stripe, Cloudflare, Resend y reglas inquebrantables de seguridad."
keywords: [mcp, model-context-protocol, ai-tools, claude-desktop, mcp-server, mcp-tools, typescript, zod]
updated: 2026-07-27
status: current
---

# 🤖 ESTÁNDAR DE HERRAMIENTAS Y SERVIDORES MCP (MODEL CONTEXT PROTOCOL)

> **Objetivo:** Definir cómo construir, integrar y extender servidores MCP (Model Context Protocol) para conectar asistentes de IA (como Claude Code o Claude Desktop) de forma segura con nuestras bases de datos, APIs de pago y servicios cloud.

---

## 🎯 LAS 4 REGLAS INQUEBRANTABLES DE MCP

**[REQUIRED] MCP-001: Todo MCP Server DEBE validar sus inputs con Zod.** NUNCA ejecutar consultas o comandos con argumentos sin validar.

> **Por qué:** un servidor MCP ejecuta acciones con argumentos que propone un modelo, no una persona. Un modelo puede alucinar un argumento o repetir uno inyectado en el contenido que acaba de leer, así que la entrada es tan poco confiable como la de un endpoint público y se valida igual (`S-001`).

**[REQUIRED] MCP-002: NUNCA exponer credenciales ni secretos en el código del servidor MCP.** Los tokens y claves API se leen de variables de entorno del proceso.

> **Por qué:** el código de un servidor MCP se comparte, se versiona y se pega en conversaciones con un modelo. Un secreto ahí escapa por más vías de las habituales, incluida la de acabar dentro del contexto de un LLM.

**[REQUIRED] MCP-003: Principio de Privilegio Mínimo.** Un servidor MCP que consulta la base de datos debe usar un rol con permisos acotados o funciones RPC específicas — NUNCA acceso ilimitado de superusuario.

> **Por qué:** un servidor MCP amplifica cualquier permiso que le des, porque quien decide qué invocar es un modelo. Con `service_role` sobre la base de datos, una petición mal interpretada es un borrado masivo; con un rol acotado o funciones RPC concretas, es un error recuperable.

**[REQUIRED] MCP-004: Todo MCP Server DEBE incluir Rate Limiting y límites de respuesta.** Evita que la IA realice cientos de peticiones involuntarias o devuelva payloads de gigabytes que saturen el contexto.

> **Por qué:** un modelo en bucle puede lanzar cientos de llamadas en segundos sin intención de hacer daño, y una respuesta enorme agota la ventana de contexto además de la cuota. El límite protege del uso accidental, que aquí es mucho más probable que el malicioso.

---

## 🌐 1. ¿QUÉ ES MCP (MODEL CONTEXT PROTOCOL)?

El **Model Context Protocol (MCP)** es un estándar abierto que permite a los modelos de lenguaje (LLMs) interactuar de forma segura con herramientas externas, recursos de datos y APIs locales o remotas a través de una interfaz cliente-servidor JSON-RPC 2.0.

```
┌────────────────────────────────┐         JSON-RPC         ┌────────────────────────────────┐
│   Cliente MCP (Claude Code /   │ ───────────────────────► │   Servidor MCP (TypeScript)    │
│   Claude Desktop / Antigravity)│ ◄─────────────────────── │  (Supabase / Stripe / R2 API)  │
└────────────────────────────────┘      Stdio / SSE         └────────────────────────────────┘
```

---

## 💻 2. ESTRUCTURA Y CÓDIGO DE UN MCP SERVER COMPLETO

A continuación se muestra la implementación de referencia de un servidor MCP en TypeScript usando el SDK oficial `@modelcontextprotocol/sdk`.

```typescript
// mcp-servers/supabase-server/src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  CallToolRequestSchema,
  ListToolsRequestSchema
} from '@modelcontextprotocol/sdk/types.js'
import { createClient } from '@supabase/supabase-supabase-js'
import { z } from 'zod'

// 1. Validar entorno
const SUPABASE_URL = process.env.SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Error: Faltan las variables SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY')
  process.exit(1)
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

// 2. Inicializar el Servidor MCP
const server = new Server(
  {
    name: 'supabase-mcp-server',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
)

// 3. Schemas de Zod para validación estricta de inputs (MCP-001)
const QueryTableSchema = z.object({
  table: z.string().regex(/^[a-zA-Z0-9_]+$/, 'Nombre de tabla inválido'),
  columns: z.string().default('id, created_at'),
  limit: z.number().min(1).max(100).default(20)
})

const ExecuteRpcSchema = z.object({
  function_name: z.string().regex(/^[a-zA-Z0-9_]+$/),
  args: z.record(z.unknown()).optional()
})

// 4. Registrar la lista de herramientas disponibles
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'query_table',
      description: 'Consulta filas de una tabla permitida en Supabase con columnas explícitas.',
      inputSchema: {
        type: 'object',
        properties: {
          table: { type: 'string', description: 'Nombre de la tabla (ej. documents, teams)' },
          columns: { type: 'string', description: 'Columnas a seleccionar separadas por comas (NUNCA *)' },
          limit: { type: 'number', description: 'Cantidad máxima de registros (1-100)' }
        },
        required: ['table']
      }
    },
    {
      name: 'execute_rpc',
      description: 'Ejecuta una función almacenada segura (RPC) en la base de datos.',
      inputSchema: {
        type: 'object',
        properties: {
          function_name: { type: 'string', description: 'Nombre de la función RPC' },
          args: { type: 'object', description: 'Argumentos clave-valor para la función' }
        },
        required: ['function_name']
      }
    }
  ]
}))

// 5. Manejar la ejecución de las herramientas (tools/call)
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  try {
    switch (name) {
      case 'query_table': {
        const validated = QueryTableSchema.parse(args)
        
        const { data, error } = await supabase
          .from(validated.table)
          .select(validated.columns)
          .limit(validated.limit)

        if (error) throw error

        return {
          content: [{ type: 'text', text: JSON.stringify(data, null, 2) }]
        }
      }

      case 'execute_rpc': {
        const validated = ExecuteRpcSchema.parse(args)

        const { data, error } = await supabase.rpc(
          validated.function_name,
          validated.args ?? {}
        )

        if (error) throw error

        return {
          content: [{ type: 'text', text: JSON.stringify(data, null, 2) }]
        }
      }

      default:
        throw new Error(`Herramienta desconocida: ${name}`)
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    return {
      isError: true,
      content: [{ type: 'text', text: `Error ejecutando ${name}: ${message}` }]
    }
  }
})

// 6. Arrancar el servidor usando transporte stdio
async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error('Supabase MCP Server corriendo en stdio...')
}

main().catch(console.error)
```

---

## ⚙️ 3. CONFIGURACIÓN EN CLAUDE DESKTOP Y ANTHROPIC CLI

Para registrar servidores MCP en tu entorno de desarrollo, edita el archivo de configuración global:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "supabase": {
      "command": "node",
      "args": ["C:/Users/usuario/projects/mcp-servers/supabase-server/dist/index.js"],
      "env": {
        "SUPABASE_URL": "https://xxx.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "sb-xxx-secret"
      }
    },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp-server-stripe"],
      "env": {
        "STRIPE_SECRET_KEY": "sk_test_xxx"
      }
    },
    "cloudflare": {
      "command": "node",
      "args": ["C:/Users/usuario/projects/mcp-servers/cloudflare-server/dist/index.js"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "cf_token_xxx",
        "CLOUDFLARE_ACCOUNT_ID": "cf_account_xxx"
      }
    }
  }
}
```

---

## 📚 4. CATÁLOGO RECOMENDADO DE SERVIDORES MCP

| Servidor MCP | Propósito | Prioridad | Variables requeridas |
|---|---|---|---|
| **supabase-mcp** | Consultas SQL asistidas, esquemas de tablas, verificación de RLS | 🔴 Crítico | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| **stripe-mcp** | Consultar clientes, eventos de pago, webhooks y productos | 🔴 Crítico | `STRIPE_SECRET_KEY` |
| **resend-mcp** | Probar plantillas React Email y estado de entregabilidad | 🟡 Importante | `RESEND_API_KEY` |
| **cloudflare-mcp** | Inspeccionar logs de Workers, namespaces KV y buckets R2 | 🟡 Importante | `CLOUDFLARE_API_TOKEN`, `ACCOUNT_ID` |
| **github-mcp** | Crear PRs, revisar issues y consultar workflows de CI/CD | 🟢 Recomendado | `GITHUB_TOKEN` |
| **playwright-mcp** | Automatización E2E e inspección visual de UI en navegadores | 🟢 Recomendado | N/A |

---

## 🛡️ 5. SEGURIDAD Y AUDITORÍA DE EJECUCIÓN MCP

```
Petición de la IA (Llamar a herramienta query_table)
        │
        ▼
Validación de Schema Zod (MCP-001)  ──→ [Si falla: Retorna Error al LLM sin ejecutar]
        │
        ▼
Verificación de Máximo de Resultados (limit <= 100)
        │
        ▼
Ejecución en Supabase con Service Role / RPC acotado
        │
        ▼
Respuesta Sanitizada (sin revelar tokens ni hashes de contraseñas)
```

1. **Respuestas Acotadas**: Las herramientas que retornan listados deben truncar arrays grandes a un máximo de 100 objetos para no agotar la ventana de contexto de la IA.
2. **Audit Logging**: El servidor MCP imprime en `stderr` (no en `stdout`, ya que `stdout` se usa para el transporte JSON-RPC) cada invocación con su timestamp y argumentos.
