/**
 * lint-handbook.mjs — Validador de coherencia interna del Engineering Handbook.
 *
 * Problema que resuelve: el handbook define reglas inquebrantables (DB-001, FE-001, S-005...)
 * y a la vez contiene cientos de bloques de código de ejemplo. Cuando un ejemplo viola una regla
 * que el propio handbook exige, una IA que copia ese ejemplo genera código no conforme citando
 * el handbook como fuente. Esa clase de bug es invisible en review manual y reaparece sola.
 *
 * Qué hace: escanea los bloques de código de todos los .md y reporta violaciones de las reglas
 * verificables por patrón, IGNORANDO los anti-ejemplos deliberados (líneas marcadas ❌, bloques
 * bajo encabezado ANTI-PATRÓN, y excepciones documentadas con un marcador explícito).
 *
 * Uso:
 *   node tools/lint-handbook.mjs           → reporta y sale con código 1 si hay violaciones
 *   node tools/lint-handbook.mjs --quiet   → solo el resumen
 *
 * Exit code 1 = hay violaciones (apto para CI, ver CICD-002).
 */

import { readdir, readFile } from 'fs/promises'
import { join, relative } from 'path'

const ROOT = process.cwd()
const IGNORE_DIRS = ['node_modules', '.git', 'tools', '.claude', 'pruebas', '_project_docs']

/**
 * Marcadores que indican "esta línea es un anti-ejemplo deliberado, no la violes contando".
 * El handbook enseña por contraste (❌ malo / ✅ bueno), así que el linter debe entender eso
 * o produce 100% falsos positivos en los documentos de seguridad.
 */
const ANTIPATTERN_MARKERS = ['❌', 'ANTI-PATRÓN', 'ANTI-PATRON', 'JAMÁS', 'NUNCA hagas', 'INCORRECTO', 'MAL:']
/** Marcador explícito para excepciones justificadas por escrito. */
const EXCEPTION_MARKER = 'EXCEPCIÓN DOCUMENTADA'

const RULES = [
  {
    id: 'DB-001',
    desc: 'SELECT * / .select("*") prohibido — columnas explícitas',
    pattern: /SELECT\s+\*|\.select\(\s*['"`]\*['"`]\s*\)/i,
    severity: 'ALTA',
  },
  {
    id: 'FE-001',
    desc: '`any` en TypeScript prohibido — usar unknown + narrowing',
    pattern: /:\s*any\b|<any>|\bas any\b/,
    severity: 'ALTA',
  },
  {
    id: 'S-005',
    desc: 'CORS wildcard prohibido en entorno autenticado',
    pattern: /Access-Control-Allow-Origin['"`]?\s*[:,]\s*['"`]\*['"`]|origin:\s*['"`]\*['"`]|cors\(\s*\)/,
    severity: 'CRÍTICA',
  },
  {
    id: 'S-007',
    desc: 'JWT en localStorage prohibido — cookie HttpOnly',
    pattern: /localStorage\.(set|get)Item\(\s*['"`][^'"`]*(token|jwt|auth|session)/i,
    severity: 'CRÍTICA',
  },
  {
    id: 'DB-008',
    desc: 'Dinero en float/double prohibido — bigint en centavos',
    pattern: /(amount|price|total|monto|precio)\s*:\s*(number|float|double|real)\b(?!.*cents)/i,
    severity: 'ALTA',
    // Heurística: solo alerta si la variable de dinero NO menciona cents. Ruidosa por diseño
    // (un `amount: number` puede ser centavos sin decirlo) → severidad de revisión, no bloqueo.
    advisory: true,
  },
  {
    id: 'SEC-001',
    desc: "CSP con 'unsafe-inline' en script-src (en style-src requiere EXCEPCIÓN DOCUMENTADA)",
    pattern: /script-src[^"'`\n]*'unsafe-inline'|'unsafe-eval'/,
    severity: 'CRÍTICA',
  },
  {
    id: 'AGENTS-§5',
    desc: 'catch vacío — silencia errores',
    pattern: /catch\s*(\([^)]*\))?\s*\{\s*\}/,
    severity: 'MEDIA',
  },
  {
    id: 'NOTIF-001',
    desc: 'HTML crudo en email — usar React Email',
    pattern: /resend\.emails\.send\([^)]*\bhtml\s*:/s,
    severity: 'ALTA',
  },
]

async function walk(dir, acc = []) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.includes(entry.name)) continue
      await walk(join(dir, entry.name), acc)
    } else if (entry.name.endsWith('.md')) {
      acc.push(join(dir, entry.name))
    }
  }
  return acc
}

/**
 * Devuelve el set de líneas (1-indexed) que están dentro de un bloque de código ```.
 * Solo se auditan esas — la prosa que *describe* una regla ("NUNCA usar SELECT *") no es
 * una violación, y confundirlas es el error clásico de un grep ingenuo.
 */
function codeBlockLines(lines) {
  const inCode = new Set()
  let open = false
  lines.forEach((line, i) => {
    if (/^\s*```/.test(line)) { open = !open; return }
    if (open) inCode.add(i + 1)
  })
  return inCode
}

/**
 * Quita el comentario final de una línea de código antes de auditarla.
 *
 * Por qué: el handbook documenta sus ejemplos citando la regla que cumplen
 * (`.select('id, email')  // DB-001: NUNCA SELECT *`). Sin esto, el linter marca como
 * violación el comentario que ENUNCIA la regla, junto a código que la respeta — un falso
 * positivo que además penaliza la buena práctica de citar la regla en el ejemplo.
 *
 * Conservador a propósito: solo corta `//` que no forme parte de un `://` (URLs) y `--`
 * de SQL precedido por espacio. Un patrón que solo aparece dentro de un comentario no es
 * código y, por definición, no puede ser una violación.
 */
function stripTrailingComment(line) {
  return line
    .replace(/(^|[^:])\/\/.*$/, '$1')
    .replace(/\s--\s.*$/, '')
}

/** ¿Esta línea (o su contexto cercano) está marcada como anti-ejemplo o excepción documentada? */
function isExempt(lines, idx) {
  const line = lines[idx]

  // Prosa que ENUNCIA la regla, no que la viola. Aparece dentro de bloques ```markdown
  // (checklists de PR, plantillas de documentación). Un grep ingenuo las cuenta como
  // violaciones y hace que el linter reporte que el catálogo de reglas viola las reglas.
  if (/^\s*[-*]\s*(\[[ x]\]\s*)?/.test(line) && /NUNCA|no se us|prohibid|DB-\d|FE-\d|S-\d{3}/i.test(line)) {
    return 'prosa normativa'
  }
  // Comentario que cita la regla para explicar por qué el código de al lado la cumple.
  if (/^\s*(\/\/|--|#)/.test(line) && /DB-\d|FE-\d|S-\d{3}|NOTIF-\d|SEC-\d/.test(line)) {
    return 'comentario de cita'
  }

  const window = lines.slice(Math.max(0, idx - 4), idx + 1).join('\n')
  if (ANTIPATTERN_MARKERS.some((m) => window.includes(m))) return 'anti-ejemplo'
  if (window.includes(EXCEPTION_MARKER)) return 'excepción documentada'
  return null
}

async function main() {
  const quiet = process.argv.includes('--quiet')
  const files = await walk(ROOT)
  const findings = []
  let exemptCount = 0

  for (const file of files) {
    const raw = await readFile(file, 'utf8')
    const lines = raw.split(/\r?\n/)
    const codeLines = codeBlockLines(lines)

    lines.forEach((line, i) => {
      if (!codeLines.has(i + 1)) return
      const auditable = stripTrailingComment(line)
      for (const rule of RULES) {
        if (!rule.pattern.test(auditable)) continue
        const exempt = isExempt(lines, i)
        if (exempt) { exemptCount++; continue }
        findings.push({
          rule: rule.id,
          severity: rule.severity,
          advisory: Boolean(rule.advisory),
          desc: rule.desc,
          file: relative(ROOT, file).replace(/\\/g, '/'),
          line: i + 1,
          code: line.trim().slice(0, 100),
        })
      }
    })
  }

  const blocking = findings.filter((f) => !f.advisory)
  const advisory = findings.filter((f) => f.advisory)

  if (!quiet) {
    const order = { 'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2 }
    for (const f of blocking.sort((a, b) => order[a.severity] - order[b.severity])) {
      console.log(`[${f.severity}] ${f.rule} — ${f.file}:${f.line}`)
      console.log(`   ${f.code}`)
      console.log(`   → ${f.desc}\n`)
    }
    if (advisory.length) {
      console.log(`--- ${advisory.length} hallazgo(s) de revisión manual (no bloquean) ---`)
      for (const f of advisory) console.log(`  ${f.rule} — ${f.file}:${f.line}: ${f.code}`)
      console.log()
    }
  }

  console.log('─'.repeat(60))
  console.log(`Archivos escaneados:      ${files.length}`)
  console.log(`Violaciones bloqueantes:  ${blocking.length}`)
  console.log(`Revisión manual:          ${advisory.length}`)
  console.log(`Anti-ejemplos ignorados:  ${exemptCount} (correcto: son didácticos)`)
  console.log('─'.repeat(60))

  process.exit(blocking.length > 0 ? 1 : 0)
}

main().catch((err) => { console.error(err); process.exit(2) })
