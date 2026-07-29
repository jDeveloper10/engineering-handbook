import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const INDEX = JSON.parse(readFileSync(join(ROOT, 'INDEX.json'), 'utf8'))

// Etiquetas humanas para las carpetas de primer nivel (= `category` en INDEX.json).
// Deliberadamente centralizado aquí: si se agrega un dominio nuevo al handbook,
// basta con añadir su etiqueta a este mapa para que el sidebar lo reconozca.
const ETIQUETA_CATEGORIA = {
  '00_Fundamentos': '📐 Fundamentos',
  '01_Frontend': '🎨 Frontend',
  '02_Backend': '⚙️ Backend',
  '03_API': '🔌 API',
  '04_Database': '🗄️ Database',
  '05_Security': '🔒 Security',
  '06_Testing': '🧪 Testing / QA',
  '07_DevOps': '🚀 DevOps',
  '08_Cloud': '☁️ Cloud',
  '09_Architecture': '🏛️ Architecture',
  '10_Code_Quality': '🕵️ Code Quality',
  '10_Product': '🎯 Product',
  '11_Debugging': '🐛 Debugging',
  '12_Documentation': '📚 Documentation',
  '13_AI_Rules': '🧠 AI Rules',
  '14_DX': '🛠️ Developer Experience',
  '15_Knowledge_System': '🔄 Knowledge System',
  root: '📌 Raíz del handbook',
}

const ETIQUETA_SUBCARPETA = {
  Core: 'Core',
  Patterns: 'Patrones',
  Performance_SEO: 'Performance & SEO',
  UI_Components: 'Componentes de UI',
  Advanced: 'Análisis avanzado',
  Agents: 'Agentes QA',
  Guides: 'Guías',
  Pipelines: 'Pipelines',
  Strategy: 'Estrategia',
  References: 'Referencias rápidas',
  Metrics: 'Métricas',
  Reviews: 'Reviews',
  TEMPLATES: 'Plantillas',
}

const ORDEN_CATEGORIAS = [
  'root', '00_Fundamentos', '01_Frontend', '02_Backend', '03_API', '04_Database',
  '05_Security', '06_Testing', '07_DevOps', '08_Cloud', '09_Architecture',
  '10_Code_Quality', '10_Product', '11_Debugging', '12_Documentation',
  '13_AI_Rules', '14_DX', '15_Knowledge_System',
]

const DOC_TYPE_ICON = { estandar: '📏', patron: '🧩', runbook: '🚑', referencia: '📖', ficha_agente: '🤖' }

function rutaSitio(path) {
  return '/' + path.replace(/\.md$/, '')
}

function subcarpeta(path) {
  const partes = path.split('/')
  return partes.length > 2 ? partes[1] : null
}

/** Construye el sidebar completo agrupando por categoría y, si aplica, por subcarpeta. */
function construirSidebar() {
  const porCategoria = new Map()
  for (const doc of INDEX.docs) {
    if (!porCategoria.has(doc.category)) porCategoria.set(doc.category, [])
    porCategoria.get(doc.category).push(doc)
  }

  const grupos = []
  for (const cat of ORDEN_CATEGORIAS) {
    const docs = porCategoria.get(cat)
    if (!docs || !docs.length) continue

    const conSub = docs.some((d) => subcarpeta(d.path))
    let items
    if (conSub) {
      const porSub = new Map()
      for (const d of docs) {
        const s = subcarpeta(d.path) || '(raíz)'
        if (!porSub.has(s)) porSub.set(s, [])
        porSub.get(s).push(d)
      }
      items = [...porSub.entries()].map(([sub, ds]) => ({
        text: sub === '(raíz)' ? 'General' : (ETIQUETA_SUBCARPETA[sub] || sub),
        collapsed: true,
        items: ds
          .sort((a, b) => a.title.localeCompare(b.title, 'es'))
          .map((d) => ({ text: `${DOC_TYPE_ICON[d.doc_type] || ''} ${d.title}`.trim(), link: rutaSitio(d.path) })),
      }))
    } else {
      items = docs
        .sort((a, b) => a.title.localeCompare(b.title, 'es'))
        .map((d) => ({ text: `${DOC_TYPE_ICON[d.doc_type] || ''} ${d.title}`.trim(), link: rutaSitio(d.path) }))
    }

    grupos.push({ text: `${ETIQUETA_CATEGORIA[cat] || cat} (${docs.length})`, collapsed: cat !== 'root', items })
  }
  return grupos
}

export default {
  title: 'Engineering Handbook',
  description: 'Base de conocimiento de estándares de ingeniería de software — 171 documentos, auto-ruteo para IA vía AGENTS.md.',
  lang: 'es-ES',
  cleanUrls: true,
  lastUpdated: true,

  // Todo el repo es el srcDir: el sitio lee el contenido en su ubicación real,
  // sin duplicarlo. Solo se excluye lo que no es contenido navegable.
  srcExclude: [
    'node_modules/**',
    '.git/**',
    '.github/**',
    '.claude/**',
    'tools/**',
    '_project_docs/**',
    '**/pruebas/**',
    'CHANGELOG.md',
  ],

  ignoreDeadLinks: [
    // Ejemplos de código dentro de fences ```: DOCUMENTATION_STANDARD.md muestra una
    // plantilla de README que referencia este mismo handbook desde OTRO repo — no es
    // un enlace real del sitio, es texto ilustrativo. VitePress solo lo marcaría si
    // alguna vez saliera de un bloque de código; este patrón cubre esa ruta exacta.
    /\/ENGINEERING_HANDBOOK\/AGENTS$/,
  ],

  head: [['link', { rel: 'icon', href: '/favicon.svg' }]],

  themeConfig: {
    logo: undefined,
    outline: { level: [2, 3], label: 'En esta página' },

    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: { buttonText: 'Buscar en el handbook', buttonAriaLabel: 'Buscar' },
              modal: {
                noResultsText: 'Sin resultados para',
                resetButtonTitle: 'Limpiar búsqueda',
                footer: { selectText: 'seleccionar', navigateText: 'navegar', closeText: 'cerrar' },
              },
            },
          },
        },
      },
    },

    nav: [
      { text: 'Inicio', link: '/' },
      { text: 'Mapa de auto-ruteo (AGENTS.md)', link: '/AGENTS' },
      { text: 'Convenciones (§00)', link: '/00_HANDBOOK_FORMAT' },
      { text: 'Índice completo', link: '/README' },
    ],

    sidebar: construirSidebar(),

    socialLinks: [{ icon: 'github', link: 'https://github.com/jDeveloper10/engineering-handbook' }],

    footer: {
      message: `${INDEX.docs.length} documentos indexados · generado desde INDEX.json`,
      copyright: 'Engineering Handbook — uso interno',
    },

    docFooter: { prev: 'Anterior', next: 'Siguiente' },
    darkModeSwitchLabel: 'Apariencia',
    returnToTopLabel: 'Volver arriba',
    sidebarMenuLabel: 'Menú',
    lastUpdatedText: 'Actualizado el',
  },

  markdown: {
    theme: { light: 'github-light', dark: 'github-dark' },
  },
}
