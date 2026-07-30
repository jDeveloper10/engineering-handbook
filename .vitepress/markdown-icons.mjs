/**
 * Plugin de markdown-it: sustituye los emojis SEMÁNTICOS del contenido por iconos SVG.
 *
 * Por qué existe
 * -------------
 * Los `.md` del handbook se consumen de dos formas:
 *   a) como texto plano por agentes de IA (ver `AGENTS.md`, auto-ruteo);
 *   b) como sitio web (VitePress).
 * En (a) los emojis ✅/❌/👉/⚠ tienen valor semántico y NO se pueden borrar del fuente.
 * En (b) quedan mal. Solución: el fuente conserva el emoji y la sustitución ocurre
 * en tiempo de render, aquí.
 *
 * Garantías
 * ---------
 * - Solo se tocan los tokens `text` que cuelgan de un token `inline`. Los bloques de
 *   código (`fence`, `code_block`) y el código inline (`code_inline`) son tipos de
 *   token distintos, así que quedan intactos por construcción — sin listas de
 *   exclusión ni heurísticas sobre el markdown crudo.
 * - No se toca `token.content` del token `inline`, solo `token.children`. Los `id`
 *   de los encabezados (que markdown-it-anchor calcula antes) no cambian.
 * - Solo se sustituyen los 4 caracteres del mapa. Los caracteres de dibujo de cajas
 *   (─ │ ├ └ ═ █ ┌ ┐ ┬ ┴ ▼) y las flechas (→ ← ↔ ↓) NO están en el mapa y por tanto
 *   ni se miran.
 */

import { svgInline } from './icons.mjs'

/**
 * Emoji → { icono Lucide, modificador CSS, etiqueta accesible }.
 * Las claves usan escapes Unicode para que el archivo sea legible sin depender
 * de cómo renderice el editor.
 */
export const MAPA_ICONOS = {
  '✅': { icono: 'check-circle-2', mod: 'yes', etiqueta: 'Correcto' }, // ✅
  '❌': { icono: 'x-circle', mod: 'no', etiqueta: 'Incorrecto' }, // ❌
  '\u{1F449}': { icono: 'arrow-right-circle', mod: 'next', etiqueta: 'Nota' }, // 👉
  '⚠': { icono: 'alert-triangle', mod: 'warn', etiqueta: 'Atención' }, // ⚠
}

// Cada emoji, opcionalmente seguido del selector de variación VS16 (U+FE0F),
// que es lo que distingue "⚠" de "⚠️" y que hay que consumir para no dejarlo suelto.
const RE_EMOJI = /(✅|❌|\u{1F449}|⚠)️?/gu

const CACHE = new Map()

function html(emoji) {
  let cacheado = CACHE.get(emoji)
  if (cacheado) return cacheado
  const { icono, mod, etiqueta } = MAPA_ICONOS[emoji]
  // `ignore-header` hace que VitePress excluya el span al construir el índice de
  // la página (outline), por si el emoji aparece dentro de un encabezado.
  cacheado =
    `<span class="hb-icon hb-icon--${mod} ignore-header" role="img" aria-label="${etiqueta}">` +
    svgInline(icono) +
    '</span>'
  CACHE.set(emoji, cacheado)
  return cacheado
}

/** Parte un token `text` en text + html_inline. Devuelve null si no hay nada que hacer. */
function expandir(token, Token) {
  RE_EMOJI.lastIndex = 0
  if (!RE_EMOJI.test(token.content)) return null
  RE_EMOJI.lastIndex = 0

  const salida = []
  let ultimo = 0
  let m
  while ((m = RE_EMOJI.exec(token.content)) !== null) {
    if (m.index > ultimo) {
      const t = new Token('text', '', 0)
      t.content = token.content.slice(ultimo, m.index)
      t.level = token.level
      salida.push(t)
    }
    const t = new Token('html_inline', '', 0)
    t.content = html(m[1])
    t.level = token.level
    salida.push(t)
    ultimo = m.index + m[0].length
  }
  if (ultimo < token.content.length) {
    const t = new Token('text', '', 0)
    t.content = token.content.slice(ultimo)
    t.level = token.level
    salida.push(t)
  }
  return salida
}

export function markdownIcons(md) {
  md.core.ruler.push('hb_icons', (state) => {
    for (const bloque of state.tokens) {
      if (bloque.type !== 'inline' || !bloque.children) continue

      let cambiado = false
      const hijos = []
      for (const hijo of bloque.children) {
        // Cualquier token que no sea `text` se deja tal cual: eso incluye
        // `code_inline`, `html_inline`, `image`, `softbreak`, etc.
        if (hijo.type !== 'text') {
          hijos.push(hijo)
          continue
        }
        const trozos = expandir(hijo, state.Token)
        if (!trozos) {
          hijos.push(hijo)
          continue
        }
        hijos.push(...trozos)
        cambiado = true
      }
      if (cambiado) bloque.children = hijos
    }
  })
}

export default markdownIcons
