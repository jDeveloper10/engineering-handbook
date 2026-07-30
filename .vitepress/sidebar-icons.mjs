/**
 * Iconos del "chrome" del sitio (sidebar y prev/next) + hoja de estilos de todos
 * los iconos, tanto los del sidebar como los que inyecta `markdown-icons.mjs`.
 *
 * Cómo se enganchan los iconos al sidebar
 * ---------------------------------------
 * El tema por defecto de VitePress renderiza el texto de cada item del sidebar con
 * `v-html` (`VPSidebarItem.vue`: `<component :is="textTag" class="text" v-html="item.text" />`,
 * y lo mismo en `VPDocFooter.vue` para prev/next). Es decir, `sidebar[].text` NO es
 * texto plano: admite HTML. Por eso no hace falta ningún hack de selectores CSS por
 * texto, ni sobreescribir el layout: basta con anteponer un `<span>` con clase propia.
 *
 * El `<span>` va vacío y el dibujo entra por `mask-image` con un data-URI, de forma
 * que `background-color: currentColor` hace que el icono herede el color exacto del
 * item (normal / hover / activo, claro y oscuro) sin duplicar reglas de color.
 * Alternativa descartada: SVG inline en cada item — son ~190 items renderizados en el
 * HTML de CADA página, y repetir la geometría ahí multiplica el peso del sitio; con
 * `mask-image` la geometría va una sola vez en el `<style>` y cada item pesa ~40 bytes.
 */

import { svgDataUri } from './icons.mjs'

/** Carpeta de primer nivel → icono Lucide. */
export const ICONO_CATEGORIA = {
  '00_Fundamentos': 'ruler',
  '01_Frontend': 'palette',
  '02_Backend': 'server',
  '03_API': 'plug',
  '04_Database': 'database',
  '05_Security': 'shield-check',
  '06_Testing': 'flask-conical',
  '07_DevOps': 'rocket',
  '08_Cloud': 'cloud',
  '09_Architecture': 'landmark',
  '10_Code_Quality': 'search-check',
  '10_Product': 'target',
  '11_Debugging': 'bug',
  '12_Documentation': 'book-open',
  '13_AI_Rules': 'brain',
  '14_DX': 'wrench',
  '15_Knowledge_System': 'refresh-cw',
  root: 'pin',
}

/** `doc_type` de INDEX.json → icono Lucide. */
export const ICONO_TIPO_DOC = {
  estandar: 'ruler',
  patron: 'puzzle',
  runbook: 'siren',
  referencia: 'book-open',
  ficha_agente: 'bot',
}

/** Modificadores de color de los iconos de contenido (`markdown-icons.mjs`). */
const COLOR_CONTENIDO = {
  yes: 'var(--vp-c-green-1)',
  no: 'var(--vp-c-red-1)',
  warn: 'var(--vp-c-yellow-1)',
  next: 'var(--vp-c-brand-1)',
}

/**
 * `<span>` del icono para un item del sidebar. Devuelve '' si no hay icono
 * asociado, para que el item se quede simplemente sin icono (nunca roto).
 */
export function spanIcono(nombreIcono) {
  if (!nombreIcono) return ''
  return `<span class="hb-si hb-si--${nombreIcono}" aria-hidden="true"></span>`
}

/** Escapa el texto que se va a inyectar como HTML en `sidebar[].text`. */
export function escaparHtml(texto) {
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

/** CSS de todos los iconos, para inyectar como `<style>` desde `config.mjs`. */
export function cssIconos() {
  const usados = [
    ...new Set([...Object.values(ICONO_CATEGORIA), ...Object.values(ICONO_TIPO_DOC)]),
  ].sort()

  const reglasMask = usados
    .map(
      (n) =>
        `.hb-si--${n}{-webkit-mask-image:url("${svgDataUri(n)}");mask-image:url("${svgDataUri(n)}")}`
    )
    .join('\n')

  const reglasColor = Object.entries(COLOR_CONTENIDO)
    .map(([mod, color]) => `.hb-icon--${mod}{color:${color}}`)
    .join('\n')

  return `
/* Iconos del contenido (ver .vitepress/markdown-icons.mjs) */
.hb-icon{display:inline-block;line-height:0;vertical-align:-.19em}
.hb-icon>svg{display:block;width:1.06em;height:1.06em}
${reglasColor}

/* Iconos del sidebar / prev-next (ver .vitepress/sidebar-icons.mjs) */
.hb-si{display:inline-block;width:1.06em;height:1.06em;margin-right:.5em;vertical-align:-.19em;background-color:currentColor;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:center;mask-position:center;-webkit-mask-size:contain;mask-size:contain}
${reglasMask}
`.trim()
}
