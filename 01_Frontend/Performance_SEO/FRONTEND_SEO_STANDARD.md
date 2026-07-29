# FRONTEND SEO STANDARD (SEO técnico)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md). Relacionados: [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) (headings/semántica), [FRONTEND_ACCESSIBILITY_STANDARD.md](../UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md) (alt), `../06_Testing/08_QUALITY_STANDARDS.md` (gates de Core Web Vitals).
>
> Alcance: **páginas públicas** (landing, pricing, blog, catálogo). Las vistas privadas detrás de login (dashboard, CRUD) no se optimizan para SEO — se bloquean de indexación (sección 8) y se ignora el resto de este documento para ellas.
>
> Contexto de stack honesto: el stack actual es **React 19 + Vite en modo SPA (CSR puro)**. CSR es el peor escenario posible para SEO — este documento primero define qué debe cumplir toda página pública (secciones 2–9, agnósticas de cómo se renderice) y después (sección 10) qué estrategia de rendering hace falta para que eso realmente funcione, en orden de costo.

---

## 1. La limitación de base: CSR y crawlers

**[REQUIRED]** Antes de optimizar nada, asumir estas dos verdades del CSR puro:

1. **Google** sí ejecuta JS, pero en dos olas: primero indexa el HTML crudo, y el render con JS entra a una cola aparte (puede tardar horas o días, con presupuesto limitado). Todo lo que solo existe tras ejecutar JS se indexa tarde, a veces mal, a veces nunca (errores de JS, timeouts, contenido que depende de interacción).
2. **Casi ningún otro bot ejecuta JS**: los scrapers de WhatsApp, Slack, Discord, LinkedIn, X/Twitter y la mayoría de crawlers de IA/buscadores secundarios leen solo el HTML inicial. Meta tags OG/Twitter inyectados por React en el cliente **no existen** para ellos: el link compartido sale sin título, sin imagen.

**Por qué:** la mitad de las reglas de este documento (title, description, OG, JSON-LD) son inútiles si solo viven en el bundle de JS. La consecuencia práctica: **[REQUIRED]** toda página pública que importe para SEO o para compartir en redes debe servir sus meta tags y su contenido principal en el HTML inicial de la respuesta — cómo lograrlo sin abandonar el stack, en la sección 10.

---

## 2. Head mínimo obligatorio por página

**[REQUIRED]** Toda página pública sirve, en el HTML inicial, este mínimo:

| Elemento | Regla |
|---|---|
| `<html lang>` | Idioma real del contenido (`lang="es"`), en el documento raíz. |
| `<meta charset="utf-8">` | Primera etiqueta del head. |
| `<meta name="viewport">` | `width=device-width, initial-scale=1` (requisito de mobile-first indexing). |
| `<title>` | Único por página, ver patrón abajo. |
| `<meta name="description">` | Única por página, ver regla abajo. |
| `<link rel="canonical">` | URL absoluta canónica de la página, ver regla abajo. |
| `<meta name="robots">` | Solo cuando difiere del default (ver abajo). |

### 2.1 `<title>`
**[REQUIRED]** Único en todo el sitio (dos páginas nunca comparten title), y **[RECOMMENDED]** menor a 60 caracteres — objetivo real: que no se trunque en la SERP (~600px); 60 chars es la heurística actual. Patrón:

```
Página interior:  {Qué es la página} | {Marca}     → "Precios | Acme"
Home:             {Marca} — {Propuesta de valor}    → "Acme — Facturación para pymes"
```

**Por qué:** el title es el factor on-page de mayor peso y el texto del link en la SERP; lo importante va primero porque el final se trunca. Titles duplicados hacen que Google los reescriba a su criterio.

```
❌ <title>Home</title>                        (genérico, duplicable, sin marca)
❌ <title>Acme | Facturación electrónica online para pymes y autónomos en México 2026</title>  (se trunca)
✅ <title>Facturación para pymes | Acme</title>
```

### 2.2 `<meta name="description">`
**[REQUIRED]** Presente y única por página. **[RECOMMENDED]** ~150–160 caracteres, escrita como propuesta de valor con verbo (es el "anuncio" gratuito en la SERP), no como relleno de keywords.
**Por qué:** no es factor de ranking directo, pero determina el CTR desde la SERP; si falta o es mala, Google inventa una a partir del contenido.

```
❌ <meta name="description" content="facturación, facturas, pymes, electrónica, sat, cfdi" />
✅ <meta name="description" content="Emite facturas electrónicas en 2 clics. Planes desde $19/mes, sin permanencia. Prueba gratis 14 días." />
```

### 2.3 `<link rel="canonical">`
**[REQUIRED]** Toda página pública declara su canonical con **URL absoluta**, apuntando a la versión única oficial (con o sin `www`, siempre `https`, sin query params de tracking). En páginas sin variantes, la canonical se apunta a sí misma (self-referencing).
**Por qué:** la misma página suele ser accesible por varias URLs (`?utm_source=...`, con/sin slash final, http/https); sin canonical, Google reparte la autoridad entre duplicados o elige la versión equivocada.

```html
✅ <link rel="canonical" href="https://acme.com/precios" />   <!-- aunque se llegue por /precios?utm_source=newsletter -->
```

### 2.4 `<meta name="robots">`
**[REQUIRED]** Las páginas indexables **no** llevan meta robots (el default ya es `index, follow`). Se usa solo para excluir: `noindex, follow` en páginas públicas que no deben rankear (resultados de búsqueda interna, páginas de "gracias", paginación fina, variantes filtradas).
**Por qué:** el error típico es el inverso — dejar un `noindex` de staging en producción y desindexar el sitio entero sin síntomas visibles. Regla operativa: el deploy a producción se verifica contra `noindex` accidental (ver checklist).

```html
✅ <meta name="robots" content="noindex, follow" />   <!-- solo en /gracias, /buscar?q=..., etc. -->
```

### 2.5 Implementación de referencia (React 19)
React 19 hace hoisting nativo de `<title>`, `<meta>` y `<link>` renderizados en cualquier componente — no se necesita `react-helmet`:

```jsx
// implementación, no la regla
function PricingPage() {
  return (
    <>
      <title>Precios | Acme</title>
      <meta name="description" content="Planes desde $19/mes. Sin permanencia, factura en 2 clics." />
      <link rel="canonical" href="https://acme.com/precios" />
      {/* ...contenido... */}
    </>
  );
}
```

Advertencia (sección 1): esto solo lo ven los bots si la ruta se sirve prerenderizada — en CSR puro estos tags aparecen tarde o nunca para la mayoría de crawlers.

---

## 3. Open Graph + Twitter Cards

**[REQUIRED]** Toda página pública que pueda compartirse lleva, **en el HTML inicial** (no inyectado por JS — sección 1):

```html
<meta property="og:type" content="website" />           <!-- "article" en posts -->
<meta property="og:title" content="Precios | Acme" />
<meta property="og:description" content="Planes desde $19/mes." />
<meta property="og:url" content="https://acme.com/precios" />
<meta property="og:image" content="https://acme.com/og/precios.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
```

Reglas:
- **[REQUIRED]** `og:image` y `og:url` con **URL absoluta** (los scrapers no resuelven rutas relativas).
- **[REQUIRED]** Imagen OG de **1200×630px** (ratio 1.91:1) — el tamaño que todas las plataformas muestran completo sin recorte; menor a ~300KB para que el scraper no la descarte por timeout.
- **[RECOMMENDED]** `twitter:card` con `summary_large_image`; X/Twitter reusa `og:title`/`og:description`/`og:image` si no hay tags `twitter:*` específicos — no duplicar sin necesidad.
- **[RECOMMENDED]** `og:site_name` (la marca) y `og:locale` (`es_MX`, `es_ES`...) cuando el sitio tiene identidad/idioma que el scraper deba mostrar.
- **[RECOMMENDED]** Una imagen OG por tipo de página como mínimo (home, pricing, template de blog con el título del post renderizado sobre un fondo de marca), no una genérica para todo el sitio.

**Por qué:** el preview del link es la "primera impresión" del sitio en cualquier chat o red; un link sin imagen ni título tiene CTR drásticamente menor. Verificación: pasar la URL por los validadores de meta tags (opengraph.xyz o los debuggers de cada plataforma) tras cada deploy que toque páginas públicas.

---

## 4. Datos estructurados (JSON-LD)

**[REQUIRED]** Los datos estructurados se emiten en formato **JSON-LD** dentro de `<script type="application/ld+json">` (formato recomendado por Google — nunca microdata inline mezclada con el markup), en el HTML inicial. Solo se marca contenido **visible en la página**: marcar contenido que el usuario no ve es motivo de acción manual de Google.

**[REQUIRED]** Sitio-wide (en todas las páginas públicas o en la home): `Organization` y `WebSite`. Por tipo de página cuando aplique: `BreadcrumbList` (páginas con jerarquía), `Product` (fichas de producto), `Article` (posts). Validar cada schema con el Rich Results Test de Google antes de considerarlo terminado.

### 4.1 `Organization` + `WebSite` (home)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://acme.com/#org",
      "name": "Acme",
      "url": "https://acme.com/",
      "logo": "https://acme.com/logo-600x600.png",
      "sameAs": ["https://www.linkedin.com/company/acme", "https://x.com/acme"]
    },
    {
      "@type": "WebSite",
      "url": "https://acme.com/",
      "name": "Acme",
      "publisher": { "@id": "https://acme.com/#org" }
    }
  ]
}
</script>
```

### 4.2 `BreadcrumbList`
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://acme.com/" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://acme.com/blog" },
    { "@type": "ListItem", "position": 3, "name": "Guía de facturación" }
  ]
}
</script>
```
(El último ítem — la página actual — va sin `item`.)

### 4.3 `Product` (cuando aplique)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Plan Pro",
  "image": "https://acme.com/img/plan-pro.png",
  "description": "Facturación ilimitada para equipos de hasta 10 personas.",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://acme.com/precios"
  }
}
</script>
```

### 4.4 `Article` (cuando aplique)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Cómo facturar en 2 clics",
  "image": ["https://acme.com/blog/facturar/cover-1200x630.png"],
  "datePublished": "2026-07-01T09:00:00-06:00",
  "dateModified": "2026-07-15T10:00:00-06:00",
  "author": { "@type": "Person", "name": "Ana Ruiz", "url": "https://acme.com/equipo/ana" },
  "publisher": { "@id": "https://acme.com/#org" }
}
</script>
```

**Por qué:** JSON-LD habilita rich results (estrellas, precio, breadcrumbs, fecha en la SERP) y es la fuente de datos estructurada que consumen también los motores de respuesta con IA — el costo es bajo (un bloque estático por página) y el retorno en CTR es medible.

---

## 5. URLs y slugs

- **[REQUIRED]** Slugs en **kebab-case**, minúsculas, ASCII (sin acentos ni ñ — se translitera: `guia-de-facturacion`), sin espacios ni `_`.
- **[RECOMMENDED]** Cortos y descriptivos: 3–5 palabras significativas, sin stopwords (`de`, `la`, `y`, `para`) salvo que quitarlas rompa el sentido, sin fechas ni IDs numéricos en contenido evergreen.
- **[REQUIRED]** La URL refleja jerarquía real y estable: `/blog/guia-facturacion`, no `/index.php?p=123` ni `/blog/2026/07/15/guia`.
- **[REQUIRED]** **Un slug publicado es un contrato**: cambiarlo obliga a un redirect **301** desde la URL vieja a la nueva, mantenido indefinidamente. Nunca se cambia un slug "para mejorarlo" sin el redirect.
- **[REQUIRED]** Una sola versión canónica de dominio y formato (https + con/sin www + con/sin slash final, elegido una vez): las demás variantes redirigen 301 a ella.

**Por qué:** la URL acumula autoridad (links externos, historial de indexación); romperla sin 301 tira esa autoridad a la basura y genera 404s desde todos los links existentes. El kebab-case es lo que Google trata como separador de palabras (el `_` no separa).

```
❌ /Blog/Guía_De_Facturación_Electrónica_2026     (mayúsculas, acentos, _, fecha)
❌ /post?id=1234                                   (query param como identidad)
✅ /blog/guia-facturacion-electronica
```

**Implementación (React Router + hosting):** las rutas públicas se definen con el slug final desde el día uno; los redirects 301 se configuran en el hosting/CDN, no en JS — un redirect client-side devuelve 200 y el crawler nunca ve el 301. Ejemplo `_redirects` (Cloudflare Pages/Netlify):

```
/blog/guia-facturas   /blog/guia-facturacion-electronica   301
```

---

## 6. Jerarquía de headings

Ya normada en [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) secciones 4–5 (**[REQUIRED]** un solo `<h1>` por página, sin saltos de nivel) — no se repite aquí. Lo único que este documento agrega:

**[REQUIRED]** En páginas públicas, el `<h1>` contiene la keyword/tema principal de la página en lenguaje natural (no un genérico como "Bienvenido"), y los `<h2>` funcionan como el índice temático que un crawler (o un modelo de IA) usaría para entender de qué trata cada bloque.
**Por qué:** los headings son la señal estructural más fuerte del contenido para buscadores y answer engines; un outline de headings legible por sí solo es SEO gratis.

---

## 7. Imágenes

El `alt` según función (informativa/decorativa/funcional) ya está normado en [FRONTEND_ACCESSIBILITY_STANDARD.md](../UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md) sección 7 y [FRONTEND_HTML_STRUCTURE_STANDARD.md](../Core/FRONTEND_HTML_STRUCTURE_STANDARD.md) sección 10 — no se repite. Lo que este documento agrega para páginas públicas:

- **[REQUIRED]** Toda `<img>` declara `width` y `height` (o `aspect-ratio` en CSS) para que el navegador reserve el espacio antes de descargar.
  **Por qué:** imágenes sin dimensiones son la causa #1 de CLS — el contenido salta cuando la imagen llega.
- **[REQUIRED]** `loading="lazy"` en toda imagen **salvo** la candidata a LCP (el hero above-the-fold), que va con carga eager y **[RECOMMENDED]** `fetchpriority="high"`.
  **Por qué:** lazy en el LCP retrasa la métrica de ranking; eager en todo lo demás desperdicia ancho de banda del render inicial.
- **[RECOMMENDED]** Formatos modernos (AVIF/WebP con fallback vía `<picture>` — ver [FRONTEND_HTML_ELEMENTS_REFERENCE.md](../UI_Components/FRONTEND_HTML_ELEMENTS_REFERENCE.md) sección 5) y nombre de archivo descriptivo en kebab-case (`dashboard-facturas.webp`, no `IMG_2041.png`) — el nombre es señal para búsqueda de imágenes.

---

## 8. sitemap.xml + robots.txt

### 8.1 `sitemap.xml`
**[REQUIRED]** El sitio publica `/sitemap.xml` con **solo** las URLs públicas, canónicas e indexables (status 200, sin `noindex`, sin redirects). Se regenera en build cuando cambian rutas/contenido, y se referencia desde robots.txt y Google Search Console.
- Incluir: home, landing/pricing, posts, fichas públicas. `<lastmod>` real si se conoce (no faked — Google lo ignora si miente).
- Excluir: rutas privadas, páginas `noindex`, URLs con parámetros, duplicados.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://acme.com/</loc><lastmod>2026-07-15</lastmod></url>
  <url><loc>https://acme.com/precios</loc><lastmod>2026-07-01</lastmod></url>
  <url><loc>https://acme.com/blog/guia-facturacion-electronica</loc><lastmod>2026-06-20</lastmod></url>
</urlset>
```

**Por qué:** en una SPA los crawlers no descubren rutas siguiendo links renderizados por JS con la misma fiabilidad que en HTML estático — el sitemap es la lista explícita de "esto existe, indéxalo".

### 8.2 `robots.txt`
**[REQUIRED]** Publicado en la raíz. Bloquea el crawleo de lo que no aporta (rutas privadas de la app, endpoints de API si comparten dominio) y declara el sitemap:

```
User-agent: *
Disallow: /app/
Disallow: /api/
Allow: /

Sitemap: https://acme.com/sitemap.xml
```

- **[REQUIRED]** No usar `Disallow` como mecanismo para desindexar una página ya indexada: bloqueada por robots.txt, Google no puede ver su `noindex` y la deja indexada "a ciegas". Para desindexar: permitir crawleo + `noindex`.
- **[REQUIRED]** Nunca bloquear `/assets/` ni los bundles JS/CSS: Google necesita renderizar la página como un usuario.

---

## 9. Core Web Vitals como factor de ranking

**[REQUIRED]** Las páginas públicas cumplen los tres Core Web Vitals — **LCP**, **CLS** e **INP** — en el percentil 75 de usuarios reales. Los umbrales concretos y los gates de CI viven en `../06_Testing/08_QUALITY_STANDARDS.md` (fuente única — no se duplican aquí para que no diverjan).

Lo que este documento aporta es el ángulo SEO:
- CWV es señal de ranking confirmada (page experience); con contenido comparable, desempata a favor del sitio rápido.
- Los datos que Google usa son de **campo** (CrUX, usuarios reales de Chrome), no el Lighthouse local: pasar Lighthouse en laptop no garantiza pasar CrUX en un móvil promedio. Monitorear en Search Console → Core Web Vitals.
- Las palancas frontend típicas ya están normadas en este handbook: dimensiones de imagen y lazy/eager (sección 7), peso del hero y code-splitting (`FRONTEND_ENGINEERING_STANDARD.md`), motion sin layout shift (`FRONTEND_MOTION_STANDARD.md`).

---

## 10. SEO en SPA: estrategia de rendering

### 10.1 Qué NO va a indexar bien un CSR puro
**[REQUIRED]** Asumir como no-negociable esta lista de daños del CSR puro (Vite SPA por defecto: un `index.html` vacío + bundle JS):

1. Previews al compartir (OG) **rotos** en todas las plataformas de chat/social — sin excepción, porque sus bots no ejecutan JS.
2. Meta tags por ruta (title/description/canonical) invisibles para todo bot que no renderice JS; para Google, visibles pero con retraso y presupuesto limitado.
3. Todas las rutas sirven el **mismo** HTML vacío: sin contenido diferencial en la primera ola de indexación de Google.
4. JSON-LD inyectado en cliente: soporte incierto fuera de Google.
5. LCP penalizado de nacimiento: nada pinta hasta descargar y ejecutar el bundle.

Conclusión operativa: **[REQUIRED]** si un proyecto tiene páginas públicas cuyo tráfico orgánico o compartibilidad importa, CSR puro no es una opción aceptable para *esas* páginas — se aplica una de las estrategias siguientes. Si el proyecto es 100% app privada (login-first), nada de esto aplica: CSR está bien y solo se cumple la sección 8 (bloquear/noindex).

### 10.2 Opciones en orden de costo

**Opción A — Prerender de rutas públicas en build (costo bajo). [RECOMMENDED]** como primer paso por defecto.
- Qué es: tras `vite build`, un paso renderiza cada ruta pública a HTML estático (con sus meta tags, contenido y JSON-LD) y lo guarda como `dist/precios/index.html`, etc. El JS hidrata después y la app sigue siendo la misma SPA (ej.: `vite-prerender-plugin`, o script propio con Puppeteer/Playwright sobre `vite preview`).
- Cuándo alcanza: rutas públicas **finitas y conocidas en build** cuyo contenido no cambia entre deploys (landing, pricing, features, legal, posts que se publican vía deploy).
- Límite: no sirve para contenido que cambia sin deploy o miles de URLs dinámicas.

**Opción B — SSG parcial / por framework (costo medio).**
- Qué es: las rutas públicas se generan como HTML estático desde datos en build con un framework que lo trae de serie (Astro para el sitio público, o Vike/React Router en modo prerender dentro del mismo repo), manteniendo la app privada como SPA.
- Cuándo: catálogo/blog con decenas-cientos de URLs desde un CMS o base de datos, publicación acoplada al deploy aceptable, sin necesidad de contenido por-usuario en páginas públicas.

**Opción C — Separar el sitio público de la app, o SSR (costo alto).**
- Qué es: `acme.com` (marketing/blog/catálogo) se sirve como sitio estático/SSR independiente (Astro, Next, etc.) y la SPA vive en `app.acme.com`. SSR completo solo si hay páginas públicas *dinámicas por request* (miles de URLs, contenido que cambia a cada minuto, personalización pre-login).
- Cuándo: el negocio depende del orgánico (contenido como canal de adquisición), o A/B ya se quedaron cortas. La separación por subdominio además libera a la app privada de toda obligación SEO.

**Criterio de selección [REQUIRED]:** elegir la opción **más barata que cubra el caso**, no la más moderna: ¿rutas públicas finitas y estáticas entre deploys? → A. ¿Muchas URLs desde datos, pero publicación en build aceptable? → B. ¿Contenido público dinámico por request o el orgánico es el canal principal? → C.
**Por qué:** cada salto de opción agrega infraestructura, tiempo de build y superficie de bugs (hidratación, cache); pagar SSR para prerenderizar 6 páginas estáticas es deuda gratuita.

### 10.3 Cómo verificar (aplica a cualquier opción)

**[REQUIRED]** La prueba de aceptación de SEO no es "se ve bien en el navegador" — es **ver el HTML crudo como lo ve un bot**:

```
curl -s https://acme.com/precios | grep -E "<title>|og:image|canonical|ld\+json"
```

- Si el title/OG/JSON-LD de *esa* ruta aparecen en la respuesta → correcto.
- Si aparece el `index.html` genérico de Vite (`<div id="root"></div>` vacío) → esa ruta sigue en CSR puro y las secciones 2–4 no se están cumpliendo, aunque el navegador las muestre.

Complementos: "Ver código fuente" del navegador (no el inspector, que muestra el DOM ya hidratado), el debugger de previews de cada red social tras cada cambio, y URL Inspection en Google Search Console para ver el render que obtuvo Google.

**Por qué:** el inspector del DevTools muestra el DOM post-JS y da falsa confianza — es la trampa clásica al validar SEO en una SPA.

### 10.4 Rutas inexistentes (soft-404)

**[REQUIRED]** Una URL inexistente debe responder **status 404 real a nivel de servidor/CDN**, no un 200 con página "No encontrado" renderizada por la SPA.
**Por qué:** en una SPA todas las rutas devuelven 200 con el mismo `index.html`; Google lo clasifica como *soft-404* y contamina el índice con URLs basura. Las páginas de error en sí se diseñan según [FRONTEND_ERROR_PAGES_STANDARD.md](../Patterns/FRONTEND_ERROR_PAGES_STANDARD.md); esta regla es solo sobre el status code.

---

## Checklist final por página pública

- [ ] ¿La página sirve su contenido y meta tags en el HTML inicial (estrategia A/B/C de la sección 10, no CSR puro)?
- [ ] ¿`<title>` único, con patrón `{Página} | {Marca}`, que no se trunca en SERP (~60 chars)?
- [ ] ¿`<meta name="description">` única, ~150–160 chars, orientada a CTR?
- [ ] ¿`<link rel="canonical">` con URL absoluta? ¿Sin `noindex` accidental (verificado en producción)?
- [ ] ¿`lang` correcto en `<html>` y meta viewport presente?
- [ ] ¿OG completo (`og:title/description/url/image` absolutos, imagen 1200×630) + `twitter:card`, verificado con un validador de previews?
- [ ] ¿JSON-LD presente (Organization/WebSite; BreadcrumbList/Product/Article según el tipo) y validado en Rich Results Test?
- [ ] ¿Slug en kebab-case, sin stopwords, estable — y si alguna URL cambió, redirect 301 a nivel de servidor/CDN?
- [ ] ¿Un `<h1>` con el tema principal y outline de `<h2>` legible por sí solo (jerarquía según HTML_STRUCTURE)?
- [ ] ¿Imágenes con `width`/`height`, `loading="lazy"` salvo el LCP (eager + `fetchpriority="high"`), alt según ACCESSIBILITY?
- [ ] ¿La URL está en `sitemap.xml`, el sitemap referenciado en `robots.txt`, y las rutas privadas bloqueadas/noindex?
- [ ] ¿La página pasa los gates de Core Web Vitals definidos en `06_Testing/08_QUALITY_STANDARDS.md` (datos de campo, no solo Lighthouse local)?
