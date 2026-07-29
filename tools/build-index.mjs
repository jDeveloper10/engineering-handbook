import { readdir, readFile, writeFile } from 'fs/promises'
import { join, extname } from 'path'

const ROOT_DIR = process.cwd()
const IGNORE_DIRS = ['node_modules', '.git', 'tools', 'Engineering-OS', '.claude', 'pruebas', '_project_docs', '.vitepress']
// Archivos de chrome del sitio VitePress en la raíz — no son documentos del handbook
// (sin category/summary/tags reales), así que no deben ensuciar INDEX.json.
const IGNORE_FILES = ['index.md']
const INDEX_PATH = join(ROOT_DIR, 'INDEX.json')

function parseFrontmatter(rawContent) {
  const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/
  const match = rawContent.match(frontmatterRegex)
  
  if (!match) {
    return { data: {}, body: rawContent }
  }
  
  const yamlText = match[1]
  const body = rawContent.slice(match[0].length)
  const data = {}
  
  const lines = yamlText.split(/\r?\n/)
  let currentKey = null
  let isList = false
  
  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith('#')) continue
    
    // Check for list item '- item'
    const listItemMatch = line.match(/^\s*-\s+(.*)$/)
    if (listItemMatch && currentKey && isList) {
      const val = listItemMatch[1].trim().replace(/^['"]|['"]$/g, '')
      data[currentKey].push(val)
      continue
    }
    
    const keyValMatch = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/)
    if (keyValMatch) {
      const key = keyValMatch[1].trim()
      const val = keyValMatch[2].trim()
      
      if (!val) {
        // Starts a list or empty object
        currentKey = key
        data[key] = []
        isList = true
      } else if (val.startsWith('[') && val.endsWith(']')) {
        // Inline array [a, b, c]
        const items = val.slice(1, -1).split(',').map(s => s.trim().replace(/^['"]|['"]$/g, '')).filter(Boolean)
        data[key] = items
        isList = false
        currentKey = null
      } else {
        data[key] = val.replace(/^['"]|['"]$/g, '')
        isList = false
        currentKey = null
      }
    }
  }
  
  return { data, body }
}

async function scanDirectory(dir) {
  const entries = await readdir(dir, { withFileTypes: true })
  const results = []
  
  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.includes(entry.name)) continue
      const subResults = await scanDirectory(fullPath)
      results.push(...subResults)
      continue
    }
    
    if (entry.isFile() && extname(entry.name) === '.md' && !(dir === ROOT_DIR && IGNORE_FILES.includes(entry.name))) {
      const content = await readFile(fullPath, 'utf-8')
      const { data: frontmatter, body } = parseFrontmatter(content)
      
      // Contar tokens (aproximado: 3.8 chars = 1 token en español/markdown).
      // Normalizar CRLF→LF antes de contar: sin esto, el mismo archivo produce un
      // conteo distinto en Windows (CRLF) que en CI/Linux (LF), y verify-index-fresh.mjs
      // marcaría el índice como desactualizado sin que nada real haya cambiado.
      const tokens = Math.ceil(body.replace(/\r\n/g, '\n').length / 3.8)
      const relPath = fullPath.replace(ROOT_DIR + '\\', '').replace(ROOT_DIR + '/', '').replace(/\\/g, '/')
      
      results.push({
        title: frontmatter.title || entry.name.replace('.md', ''),
        path: relPath,
        category: frontmatter.category || guessCategory(relPath),
        // doc_type decide si el documento DEBE llevar [REQUIRED]/[RECOMMENDED]
        // (estandar y patron sí; runbook, referencia y ficha_agente no).
        // Ver 00_HANDBOOK_FORMAT.md §1.b. Sin este campo en el índice, no se puede
        // auditar la cobertura del etiquetado sin abrir los 171 archivos.
        doc_type: frontmatter.doc_type || null,
        tags: Array.isArray(frontmatter.tags) ? frontmatter.tags : [],
        summary: frontmatter.summary || extractSummary(body),
        keywords: Array.isArray(frontmatter.keywords) ? frontmatter.keywords : [],
        tokens,
        status: frontmatter.status || 'current',
        updated: frontmatter.updated || null,
        has_frontmatter: !!frontmatter.title
      })
    }
  }
  
  return results
}

function guessCategory(relPath) {
  if (relPath.includes('01_Frontend')) return 'frontend'
  if (relPath.includes('02_Backend')) return 'backend'
  if (relPath.includes('03_API')) return 'api'
  if (relPath.includes('04_Database')) return 'database'
  if (relPath.includes('05_Security')) return 'security'
  if (relPath.includes('06_Testing')) return 'testing'
  if (relPath.includes('07_DevOps')) return 'devops'
  if (relPath.includes('08_Cloud')) return 'cloud'
  if (relPath.includes('09_Architecture')) return 'architecture'
  if (relPath.includes('10_Product')) return 'product'
  if (relPath.includes('11_Debugging')) return 'debugging'
  if (relPath.includes('12_Documentation')) return 'documentation'
  if (relPath.includes('13_AI_Rules')) return 'ai-rules'
  if (relPath.includes('14_DX')) return 'dx'
  if (relPath.includes('15_Knowledge_System')) return 'knowledge'
  return 'general'
}

function extractSummary(body) {
  const cleaned = body.replace(/^---[\s\S]*?---\n/, '').trim()
  const firstParagraph = cleaned.split(/\r?\n\r?\n/)[0] || ''
  return firstParagraph.replace(/^#+\s+.*\n?/, '').trim().substring(0, 200)
}

async function main() {
  console.log('🔍 Escaneando Engineering Handbook...')
  const docs = await scanDirectory(ROOT_DIR)
  
  docs.sort((a, b) => a.path.localeCompare(b.path))

  const index = {
    docs,
    _meta: {
      generated_at: new Date().toISOString(),
      total_docs: docs.length,
      total_tokens: docs.reduce((sum, doc) => sum + doc.tokens, 0)
    }
  }
  
  await writeFile(INDEX_PATH, JSON.stringify(index, null, 2))
  console.log(`✅ INDEX.json generado exitosamente: ${docs.length} documentos indexados.`)
  console.log(`📊 Total estimado de tokens: ${index._meta.total_tokens.toLocaleString()}`)
}

main().catch(console.error)
