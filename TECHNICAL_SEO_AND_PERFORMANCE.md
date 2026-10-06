# Technical SEO, Web Performance & Core Web Vitals — JCDigital Engineering Handbook

> **Estándar Técnico para Desarrollo Web de Alto Rendimiento e Indexación**  
> Síntesis de Google Search Central, Google Search Essentials, Ahrefs Technical SEO, web.dev Performance y Chrome DevTools.

---

## 1. Ruta de Aprendizaje e Implementación (Developer Roadmap)

```
1. Google Search Essentials
   └── Fundamentos de rastreo (Crawling), indexación (Indexing) y requisitos de Googlebot.
2. Google SEO para Desarrolladores
   └── Renderizado de JavaScript, URLs canónicas, datos estructurados (JSON-LD) y metadatos.
3. Ahrefs Technical SEO
   └── Arquitectura web, enlazado interno, presupuestos de rastreo (Crawl Budget) y códigos HTTP.
4. web.dev Learn Performance
   └── Optimización de activos (Imágenes, Fonts, CSS/JS), Prefetching y Web Workers.
5. Chrome DevTools & Lighthouse
   └── Diagnóstico de Core Web Vitals en campo y laboratorio (LCP, INP, CLS).
6. Ahrefs SEO Strategy
   └── Semántica On-Page, intención de búsqueda y estructuración de contenido.
```

---

## 2. Core Web Vitals: Métricas y Umbrales Críticos

| Métrica | Qué Mide | Umbral Óptimo (Verde) | Estrategias Técnicas de Optimización |
| :--- | :--- | :--- | :--- |
| **LCP** *(Largest Contentful Paint)* | Velocidad de carga percibida del contenido principal | **≤ 2.5 segundos** | • Preload de imagen héroe (`<link rel="preload">`)<br>• Servir imágenes en formato AVIF / WebP<br>• CDN en el Edge (Cloudflare)<br>• Prioridad de fetch (`fetchpriority="high"`) |
| **INP** *(Interaction to Next Paint)* | Capacidad de respuesta táctil e interactiva | **≤ 200 milisegundos** | • Reducir trabajo en el Main Thread<br>• Fragmentar tareas largas (*Long Tasks* > 50ms) con `scheduler.yield()` o `requestIdleCallback`<br>• Evitar JavaScript innecesario en el primer render |
| **CLS** *(Cumulative Layout Shift)* | Estabilidad visual del diseño | **≤ 0.1** | • Definir siempre `width` y `height` o `aspect-ratio` en imágenes y videos<br>• Reservar espacio en anuncios y banners con CSS `min-height`<br>• Usar `font-display: swap` con fuentes coincidentes |

---

## 3. Checklist Técnico de SEO (Googlebot-Ready)

### A. Crawling & Indexación
- [ ] **`robots.txt`**: Permitir a Googlebot acceder a los recursos estáticos (`.js`, `.css`, imágenes). Nunca bloquear activos necesarios para el renderizado.
- [ ] **`sitemap.xml`**: Sitemap dinámico, limpio de URLs con redirecciones (`301`) o errores (`404`), actualizado automáticamente.
- [ ] **URLs Canónicas (`<link rel="canonical">`)**: Definir siempre la versión canónica absoluta para evitar contenido duplicado por parámetros de tracking o variantes `http`/`https`.

### B. Renderizado y JavaScript (Client-Side vs Edge/SSR)
- [ ] **Hydration Limpia**: Asegurar que las etiquetas críticas (`<h1>`, `<title>`, `<meta name="description">`) estén presentes en el HTML inicial.
- [ ] **Enlaces Rastreables**: Usar enlaces semánticos con atributos `<a href="/ruta">`. No usar solo `onClick` con navegación JS imperativa sin etiqueta `<a>`.
- [ ] **Gestión de Errores HTTP**: Páginas inexistentes deben devolver un código de estado real `404` o `410`, nunca un `200 OK` con mensaje visual de "no encontrado" (*Soft 404*).

### C. Metadatos y Datos Estructurados (Schema.org / JSON-LD)
- [ ] **Title Tag**: Único por página, entre 50 y 60 caracteres, priorizando la propuesta de valor y marca.
- [ ] **Meta Description**: Entre 140 y 160 caracteres, persuasiva y orientada a la acción (CTR).
- [ ] **Open Graph / Twitter Cards**: `og:title`, `og:description`, `og:image` (1200x630px) para previews en WhatsApp, Twitter, LinkedIn y Slack.
- [ ] **JSON-LD**: Estructuras válidas según el tipo de página (`Organization`, `SoftwareApplication`, `LocalBusiness`, `Article`, `FAQPage`).

---

## 4. Reglas de Optimización de Recursos (Assets Performance)

### 1. Imágenes y Multimedia
- Usar formatos modernos: **AVIF** (primera opción) y **WebP** (fallback).
- Carga diferida nativa: `loading="lazy"` en todas las imágenes bajo el primer pliegue (*below-the-fold*).
- La imagen héroe principal debe llevar `loading="eager"` y `fetchpriority="high"`.

### 2. Tipografías Web
- Alojar las fuentes localmente en el servidor/CDN en formato **WOFF2**.
- Precargar la tipografía principal en el `<head>`:
  ```html
  <link rel="preload" href="/fonts/inter-bold.woff2" as="font" type="font/woff2" crossorigin>
  ```
- Aplicar `font-display: swap` para evitar texto invisible durante la descarga (FOIT).

### 3. JavaScript y CSS
- Código CSS crítico en línea o descargado con prioridad; CSS no crítico diferido.
- Carga asíncrona de scripts: usar `defer` o `type="module"` para no bloquear el parseo del DOM.
- Eliminar librerías pesadas para tareas simples (ej. preferir Vanilla JS o utilidades nativas frente a bibliotecas masivas).

---

## 5. Propuesta de Valor Comercial para Clientes (JCDigital Offering)

> **"Ingeniería Web Completa: Desarrollo de Software + SEO Técnico + Rendimiento Extremo"**

Al presentar propuestas a clientes, diferenciamos el desarrollo común de la ingeniería de alta fidelidad:

1. **Arquitectura Rápida y Limpia:** No solo una interfaz bonita, sino una base de código que carga en sub-segundos, alojada en Cloudflare Edge.
2. **Indexación Garantizada:** Estructura semántica compatible con Googlebot, metadatos dinámicos Open Graph y Schema JSON-LD para resultados enriquecidos.
3. **Core Web Vitals en Verde:** Cumplimiento de los estándares de Google (LCP, INP, CLS) para favorecer el ranking y reducir tasas de rebote en móviles.
4. **Seguridad y Modernidad:** Certificados SSL automáticos, compresión Brotli y PWA lista para instalar en teléfonos.

---

## 6. Recursos y Documentación Oficial de Referencia

- [Google Search Central — Guía para Desarrolladores](https://developers.google.com/search/docs/fundamentals/get-started-developers)
- [Google Search Essentials](https://developers.google.com/search/docs/essentials)
- [Ahrefs — Guía y Curso de Technical SEO](https://ahrefs.com/es/seo/technical-seo)
- [web.dev — Learn Web Performance & Core Web Vitals](https://web.dev/learn/performance)
- [Chrome DevTools — Performance Documentation](https://developer.chrome.com/docs/performance)
