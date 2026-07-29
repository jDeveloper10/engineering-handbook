---
title: "Estándar Avanzado de SEO, Datos Estructurados y Meta Tags"
category: 01_Frontend
doc_type: estandar
tags: [seo, schema-org, json-ld, sitemap, open-graph, twitter-cards, canonical, hreflang]
summary: "Estándar avanzado de SEO técnico para aplicaciones web y SaaS: JSON-LD (Schema.org), generación de sitemap.xml dinámico, robots.txt, Open Graph, Breadcrumbs semánticos y soporte hreflang multi-idioma."
keywords: [seo, schema-org, json-ld, sitemap, robots, open-graph, og, twitter-card, canonical, hreflang]
updated: 2026-07-27
status: current
---

# 🔍 ESTÁNDAR AVANZADO DE SEO Y DATOS ESTRUCTURADOS

## 🎯 OBJETIVO
Definir las técnicas de optimización en motores de búsqueda (SEO técnico) y marcado semántico para asegurar la máxima indexabilidad, fragmentos enriquecidos (Rich Snippets) e previsualizaciones perfectas en redes sociales.

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] SEO-001: Toda página pública DEBE incluir datos estructurados JSON-LD válidos según Schema.org.**

> **Por qué:** sin JSON-LD, Google tiene que inferir qué es la página a partir del HTML visible, y la inferencia no produce fragmentos enriquecidos (rating, precio, FAQ) en los resultados. El marcado estructurado es la diferencia entre un resultado de texto plano y uno con visibilidad real.

**[REQUIRED] SEO-002: Canonical URLs obligatorias en todas las páginas.** Previene penalizaciones por contenido duplicado.

> **Por qué:** sin canonical, la misma página accesible por varias URLs (con y sin barra final, con parámetros de tracking) se indexa como contenido duplicado, y los buscadores reparten el valor de posicionamiento entre las copias en vez de concentrarlo en una.

**[REQUIRED] SEO-003: Metadatos Open Graph y Twitter Cards completos.** Toda URL pública debe mostrar una previsualización con título, descripción e imagen optimizada (`1200x630px`).

> **Por qué:** sin Open Graph, un enlace compartido en redes o mensajería aparece sin imagen ni descripción — el enlace pelado transmite mucho menos confianza y reduce el clic incluso cuando el contenido es bueno.

---

## 📄 1. SCHEMA.ORG / JSON-LD PARA SAAS

```tsx
// src/components/SEOHead.tsx
import { Helmet } from 'react-helmet-async'

export function SaaSStructuredData() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'CollabScribe',
    operatingSystem: 'All',
    applicationCategory: 'BusinessApplication',
    offers: {
      '@type': 'Offer',
      price: '19.99',
      priceCurrency: 'USD'
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.9',
      reviewCount: '128'
    }
  }

  return (
    <Helmet>
      <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
    </Helmet>
  )
}
```

---

## 🌐 2. GENERACIÓN DINÁMICA DE SITEMAP.XML Y ROBOTS.TXT EN WORKERS

```typescript
// GET /sitemap.xml (Generado dinámicamente en el Edge)
export async function handleSitemap(request: Request, env: Env): Promise<Response> {
  const { data: docs } = await supabase
    .from('documents')
    .select('public_token, updated_at')
    .eq('is_public', true)

  const baseUrl = 'https://collabscribe.com'
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${baseUrl}</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  ${(docs || []).map(d => `
  <url>
    <loc>${baseUrl}/p/${d.public_token}</loc>
    <lastmod>${new Date(d.updated_at).toISOString()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`).join('')}
</urlset>`

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml', 'Cache-Control': 'public, max-age=3600' }
  })
}
```

---

## 🏷️ 3. META TAGS META, OPEN GRAPH Y HREFLANG

```html
<!-- Cabeceras estándar en index.html -->
<title>CollabScribe - Plataforma de Escritura Colaborativa</title>
<meta name="description" content="Edita documentos técnicos en tiempo real con tu equipo.">

<!-- Canonical -->
<link rel="canonical" href="https://collabscribe.com/es/pricing">

<!-- Multi-idioma Hreflang -->
<link rel="alternate" hreflang="es" href="https://collabscribe.com/es/pricing">
<link rel="alternate" hreflang="en" href="https://collabscribe.com/en/pricing">
<link rel="alternate" hreflang="x-default" href="https://collabscribe.com/en/pricing">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://collabscribe.com/">
<meta property="og:title" content="CollabScribe - Escritura Colaborativa">
<meta property="og:description" content="Edita documentos en tiempo real con tu equipo.">
<meta property="og:image" content="https://collabscribe.com/og-image.png">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="CollabScribe">
<meta name="twitter:description" content="Edita documentos en tiempo real con tu equipo.">
<meta name="twitter:image" content="https://collabscribe.com/og-image.png">
```

---

## 📋 CHECKLIST SEO TÉCNICO

- [ ] Marcado JSON-LD válido verificado con Google Rich Results Test.
- [ ] Canonical URL presente en todas las páginas.
- [ ] Sitemap.xml dinámico accesible en `/sitemap.xml`.
- [ ] Tags Open Graph y Twitter con imagen `1200x630px`.
- [ ] Atributos `hreflang` para versiones multi-idioma.
