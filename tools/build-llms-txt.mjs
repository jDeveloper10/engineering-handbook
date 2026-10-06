import { readFile, writeFile } from 'fs/promises'
import { join } from 'path'

const ROOT_DIR = process.cwd()
const BASE_URL = 'https://handbook-explorer.pages.dev'

async function main() {
  console.log('🤖 Generando llms.txt y llms-core.txt...')

  const indexRaw = await readFile(join(ROOT_DIR, 'INDEX.json'), 'utf8')
  const index = JSON.parse(indexRaw)

  const agentsMd = await readFile(join(ROOT_DIR, 'AGENTS.md'), 'utf8')

  // 1. Construir llms.txt (Estándar oficial para LLMs)
  let llmsTxt = `# Engineering Handbook

> Sistema Operativo de Ingeniería, Arquitectura y Estándares de Desarrollo de Software de Alta Escala.

Este documento está optimizado para Agentes de Inteligencia Artificial (Claude, ChatGPT, Cursor, Gemini, Copilot).
Define las reglas obligatorias, mapa de auto-ruteo y el catálogo completo de 207 estándares de ingeniería.

## Instrucciones Fundamentales para la IA
1. Antes de implementar código o proponer arquitectura, consulta la regla específica del dominio correspondiente.
2. Sigue el flujo de desarrollo guiado por especificaciones: Spec -> Zod -> Test -> Code -> Verify.
3. Respeta estrictamente las reglas marcadas como [REQUIRED].

## Reglas Inquebrantables Críticas
- DB-001: SELECT * o .select("*") estrictamente prohibido. Columnas explícitas siempre.
- DB-002: Toda FK en base de datos debe tener un índice secundario.
- DB-008: Prohibido float/double para dinero. Usar siempre enteros (centavos) o bigint.
- S-001: Todo payload de entrada (frontend y backend) debe validarse con Zod.
- S-005: Prohibido CORS wildcard (*) en entornos autenticados o con credenciales.
- FE-001: Prohibido any en TypeScript. Usar unknown y estrechar tipos.
- FE-005: Todo componente asíncrono debe manejar Loading, Empty, Error y Success.
- MONEY-001: Los precios nunca se definen en el frontend. El backend resuelve monto y priceId.
- SEC-001: Cabeceras de seguridad estrictas (CSP, HSTS, X-Content-Type-Options).
- SEC-002: Cero secretos o API keys privadas en bundles de cliente (Vite, APK, Tauri).
- TENANT-001: Row Level Security (RLS) en base de datos es la fuente de verdad en entornos multi-tenant.
- TEST-001: Todo fix de bug P0/P1 o seguridad exige test de regresión automatizado obligatorio.

## Archivos Centrales de Operación
- [Mapa Central de Auto-Ruteo](${BASE_URL}/AGENTS): Cerebro del handbook y matriz de decisiones.
- [Operating Gate (Gate de Activación)](${BASE_URL}/Engineering-OS/32-Operating-Gate): Validación obligatoria antes de implementar (perfil, riesgo y evidencia).
- [Feature Completeness Engine](${BASE_URL}/Engineering-OS/33-Feature-Completeness-Engine): Matriz de cobertura técnica y casos límite.
- [Policy Profiles](${BASE_URL}/Engineering-OS/34-Policy-Profiles): Perfiles de rigor de políticas aplicables.
- [Rule Registry](${BASE_URL}/Engineering-OS/35-Rule-Registry): Registro de reglas inquebrantables.
- [Validation Pipeline](${BASE_URL}/Engineering-OS/36-Validation-Pipeline): Pipeline de validación pre-release.
- [Catálogo Completo de Estándares (JSON)](${BASE_URL}/INDEX.json): Catálogo estructurado para consumo por APIs y agentes.
- [Núcleo Crítico Completo (Texto Plano)](${BASE_URL}/llms-core.txt): Compilación en un solo archivo de las reglas técnicas fundamentales y del Operating Gate.

## Índice Completo de Estándares por Dominio

`

  // Agrupar por categoría
  const porCategoria = new Map()
  for (const doc of index.docs) {
    if (!porCategoria.has(doc.category)) porCategoria.set(doc.category, [])
    porCategoria.get(doc.category).push(doc)
  }

  for (const [cat, docs] of porCategoria.entries()) {
    llmsTxt += `### Dominio: ${cat}\n\n`
    for (const d of docs) {
      const docCleanPath = d.path.replace(/\.md$/, '')
      const url = `${BASE_URL}/${docCleanPath}`
      const tags = (d.tags || []).slice(0, 5).join(', ')
      llmsTxt += `- [${d.title}](${url}): ${d.summary || 'Estándar técnico oficial.'} (Tags: ${tags})\n`
    }
    llmsTxt += '\n'
  }

  // 2. Construir llms-core.txt (Núcleo técnico completo)
  const coreFiles = [
    'AGENTS.md',
    'Engineering-OS/32-Operating-Gate.md',
    'Engineering-OS/33-Feature-Completeness-Engine.md',
    'Engineering-OS/34-Policy-Profiles.md',
    'Engineering-OS/35-Rule-Registry.md',
    'Engineering-OS/36-Validation-Pipeline.md',
    '00_Fundamentos/SPEC_DRIVEN_DEVELOPMENT.md',
    '01_Frontend/Core/FRONTEND_ENGINEERING_STANDARD.md',
    '02_Backend/BACKEND_ENGINEERING_STANDARD.md',
    '03_API/API_ENGINEERING_STANDARD.md',
    '04_Database/DATABASE_ENGINEERING_STANDARD.md',
    '05_Security/SECRET_LEAK_PREVENTION_STANDARD.md',
    '10_Code_Quality/AGENCY_CODING_STANDARD.md',
  ]

  let llmsCoreTxt = `================================================================================
ENGINEERING HANDBOOK — CORE COMPILATION FOR LLMs
URL: ${BASE_URL}
================================================================================
Este archivo contiene la compilación completa de los estándares críticos del sistema.
Cualquier código o arquitectura debe alinearse con las directrices aquí presentes.
================================================================================\n\n`

  for (const file of coreFiles) {
    try {
      const content = await readFile(join(ROOT_DIR, file), 'utf8')
      llmsCoreTxt += `\n################################################################################\n`
      llmsCoreTxt += `### ARCHIVO: ${file}\n`
      llmsCoreTxt += `### URL: ${BASE_URL}/${file.replace(/\.md$/, '')}\n`
      llmsCoreTxt += `################################################################################\n\n`
      llmsCoreTxt += content + '\n\n'
    } catch (err) {
      console.warn(`Aviso: No se pudo leer el archivo core ${file}:`, err.message)
    }
  }

  // Guardar en la raíz y en las carpetas públicas de VitePress
  const targets = [
    { name: 'llms.txt', content: llmsTxt },
    { name: 'llms-core.txt', content: llmsCoreTxt }
  ]

  for (const { name, content } of targets) {
    await writeFile(join(ROOT_DIR, name), content, 'utf8')
    await writeFile(join(ROOT_DIR, '.vitepress/public', name), content, 'utf8')
    try {
      await writeFile(join(ROOT_DIR, '.vitepress/dist', name), content, 'utf8')
    } catch {}
  }

  console.log(`✅ llms.txt generado (~${Math.round(llmsTxt.length / 4)} tokens)`)
  console.log(`✅ llms-core.txt generado (~${Math.round(llmsCoreTxt.length / 4)} tokens)`)
}

main().catch(err => {
  console.error('Error generando llms:', err)
  process.exit(1)
})
