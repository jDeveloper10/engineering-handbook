#!/usr/bin/env node
// tools/find-standard.mjs — Buscador ultra-rápido de estándares en el Handbook
import fs from 'node:fs'
import path from 'node:path'

const rawArgs = process.argv.slice(2).join(' ').trim().toLowerCase()

if (!rawArgs) {
  console.log(`
🔍 BUSCADOR INTELIGENTE DEL ENGINEERING HANDBOOK:
   npm run find <tema o palabra clave>

Ejemplos:
   npm run find pagos
   npm run find rls
   npm run find migracion
   npm run find cliente
   npm run find error
   npm run find mobile
`)
  process.exit(0)
}

const indexPath = path.resolve('INDEX.json')

if (!fs.existsSync(indexPath)) {
  console.error('❌ No se encontró INDEX.json. Ejecuta "npm run build-index" primero.')
  process.exit(1)
}

const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'))
const documents = indexData.docs || []
const queryTokens = rawArgs.split(/\s+/).filter(Boolean)

const results = []

for (const doc of documents) {
  let score = 0
  const title = (doc.title || '').toLowerCase()
  const summary = (doc.summary || '').toLowerCase()
  const keywords = (doc.keywords || []).map(k => String(k).toLowerCase())
  const tags = (doc.tags || []).map(t => String(t).toLowerCase())
  const docPath = (doc.path || '').toLowerCase()

  for (const token of queryTokens) {
    if (title.includes(token)) score += 15
    if (docPath.includes(token)) score += 10
    if (keywords.some(k => k.includes(token))) score += 8
    if (tags.some(t => t.includes(token))) score += 6
    if (summary.includes(token)) score += 4
  }

  if (score > 0) {
    results.push({ doc, score })
  }
}

results.sort((a, b) => b.score - a.score)

const topResults = results.slice(0, 5)

console.log(`\n🔎 Resultados para: "${rawArgs}" (${results.length} documento(s) encontrado(s))\n`)

if (topResults.length === 0) {
  console.log('⚠️ No se encontraron documentos exactos. Prueba con términos generales como: db, rls, pagos, auth, front, test, deploy, cliente, worker.')
  process.exit(0)
}

topResults.forEach(({ doc, score }, idx) => {
  console.log(`  ${idx + 1}. 📄 ${doc.title}`)
  console.log(`     📁 Archivo: ${doc.path}`)
  if (doc.summary) {
    console.log(`     💡 Resumen: ${doc.summary}`)
  }
  if (doc.tags && doc.tags.length > 0) {
    console.log(`     🏷️  Tags: [${doc.tags.join(', ')}]`)
  }
  console.log('')
})
