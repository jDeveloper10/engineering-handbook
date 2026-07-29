/**
 * verify-index-fresh.mjs — ¿INDEX.json refleja el frontmatter actual de los .md?
 *
 * Problema que resuelve: build-index.mjs escribe `_meta.generated_at` con la hora
 * de ejecución, así que un `git diff` crudo sobre INDEX.json siempre marca cambio
 * aunque el contenido real (los docs indexados) sea idéntico — eso volvería
 * inútil un gate de CI que comparara el archivo tal cual. Este script regenera
 * el índice en memoria y lo compara con el committeado ignorando ese campo.
 *
 * Uso: node tools/verify-index-fresh.mjs   → exit 1 si el índice está desactualizado
 */
import { execFileSync } from 'child_process'
import { readFileSync } from 'fs'

function sinTimestamp(json) {
  const { _meta, ...resto } = json
  const { generated_at, ...metaResto } = _meta || {}
  return { ...resto, _meta: metaResto }
}

const antes = sinTimestamp(JSON.parse(readFileSync('INDEX.json', 'utf8')))

execFileSync('node', ['tools/build-index.mjs'], { stdio: 'ignore' })

const despues = sinTimestamp(JSON.parse(readFileSync('INDEX.json', 'utf8')))

if (JSON.stringify(antes) === JSON.stringify(despues)) {
  console.log('✅ INDEX.json está al día con el frontmatter de los .md')
  process.exit(0)
}

console.error("❌ INDEX.json está desactualizado. Corre 'npm run build-index' y commitea el resultado.")
process.exit(1)
