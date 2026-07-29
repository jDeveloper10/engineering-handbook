---
title: "FRONTEND LANDING PAGE STANDARD"
category: frontend
tags:
  - landing-pages
  - patterns
  - standards
  - seo
  - responsive
  - performance
summary: "Nivel 2 del dominio Frontend. Define la estructura de bloques, CTAs, tipografía del Hero, espaciado entre secciones, imágenes, SEO, rendimiento y accesibilidad específicos de landing pages de alto tráfico y conversión."
keywords:
  - conversion
  - hero
  - cta
  - social-proof
  - pricing
  - testimonials
  - faq
  - lead-generation
updated: 2026-07-26
status: current
---

# FRONTEND LANDING PAGE STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) — todas sus reglas (tokens, componentes, accesibilidad, performance) siguen aplicando. Este documento agrega solo lo específico de una landing: es la página de más tráfico frío, la que más pesa en conversión, y la que menos tolera lentitud o desorden visual.
>
> Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md): regla agnóstica primero, implementación Tailwind como ejemplo de referencia.
>
> Para identidad visual (colores/efectos), usar [FRONTEND_UI_STYLE_CATALOG.md](../UI_Components/FRONTEND_UI_STYLE_CATALOG.md) — Glassmorphism, Aurora_UI, Web3 y SaaS_Modern son los candidatos naturales para landing.
>
> Documentos de Nivel 3 pendientes (se crean bajo demanda, ver `00_HANDBOOK_FORMAT.md` sección 4): `SAAS_LANDING_STANDARD.md`, `TRADING_LANDING_STANDARD.md` — hoy no existen, ninguna landing real ha acumulado todavía 3+ reglas propias de vertical que no quepan aquí.

---

## 1. Estructura de bloques

**[REQUIRED]** Una landing sigue un orden fijo de bloques, no lo improvisa por proyecto:

```
1. Hero               — promesa principal + CTA primario, siempre sobre el fold
2. Social proof        — métricas, testimonio o logos (solo si existe contenido real; ver reglas de formato en FRONTEND_UI_PATTERNS.md sección 5 — nunca un Logo Cloud aislado y vacío)
3. Features/Beneficios  — qué resuelve para el usuario, no qué hace técnicamente
4. Cómo funciona         — 3-4 pasos, reduce fricción de "no entiendo cómo usar esto"
5. Pricing                — si aplica, nunca escondido en otra página
6. Testimonios              — prueba social cualitativa
7. FAQ                       — objeciones comunes, reduce fricción de conversión
8. CTA final                  — repite la misma promesa/botón del Hero
9. Footer                      — legal, contacto, links secundarios
```

**Por qué:** este orden sigue el nivel de compromiso creciente del usuario — primero capta atención (Hero), después genera confianza (social proof, features), después resuelve dudas (cómo funciona, FAQ) y recién ahí pide la conversión. Invertir el orden (ej. pricing antes que features) aumenta el rebote porque pide una decisión antes de justificarla.

**[REQUIRED]** El CTA primario y su copy son el mismo texto/objetivo en el Hero y en el CTA final — no se inventan variantes distintas del mismo objetivo.

**[REQUIRED]** Nunca hay más de un CTA primario visible en un mismo viewport.

---

## 2. Reglas de código

### 2.1 Un componente por sección

**[REQUIRED]** Cada bloque de la sección 1 es su propio componente independiente. El componente de la página solo orquesta — no tiene lógica ni estilos propios.

**Implementación (React):**
```tsx
export function LandingPage() {
  return (
    <>
      <HeroSection />
      <SocialProofSection />
      <FeaturesSection />
      <HowItWorksSection />
      <PricingSection />
      <TestimonialsSection />
      <FaqSection />
      <FinalCtaSection />
    </>
  );
}
```

Cada sección respeta el límite de tamaño/responsabilidad de `FRONTEND_ENGINEERING_STANDARD.md` sección 04. Si una sección crece (ej. Pricing con toggle mensual/anual), esa lógica va a un hook propio, no al componente.

### 2.2 Un único `<h1>`, jerarquía sin saltos

**[REQUIRED]** Toda la landing tiene un solo `<h1>` (el del Hero). Cada bloque siguiente usa `<h2>`; subsecciones dentro de un bloque usan `<h3>`. No se saltan niveles.

**Por qué:** afecta tanto accesibilidad (lectores de pantalla navegan por heading) como SEO (los motores de búsqueda usan la jerarquía de headings para entender la estructura del contenido).

### 2.3 Landing es contenido, no lógica de negocio

**[REQUIRED]** Si hay algo dinámico (contador de usuarios, testimonios desde CMS), pasa por el cliente de API único (`FRONTEND_ENGINEERING_STANDARD.md` sección 06) — nunca una llamada de red suelta "porque es solo una landing".

### 2.4 SEO obligatorio

**[REQUIRED]** Toda landing define: título único, descripción de 150-160 caracteres, URL canónica, imagen social (1200×630px aprox.) y título/descripción para compartidos sociales.

**Por qué:** sin esto, cualquier link compartido en WhatsApp/Telegram/redes se ve roto o genérico — relevante porque la distribución real de estas landings (academias, promos) es principalmente por WhatsApp.

**Implementación (HTML head):**
```html
<title>Producto — promesa en 60 caracteres</title>
<meta name="description" content="150-160 caracteres, la promesa + para quién es" />
<link rel="canonical" href="https://dominio.com/" />
<meta property="og:image" content="https://dominio.com/og-image.png" />
<meta property="og:title" content="..." />
<meta property="og:description" content="..." />
```

---

## 3. Imágenes

### 3.1 La imagen del Hero se trata distinto al resto

**[REQUIRED]** La imagen o video principal del Hero **no se carga en diferido** (nunca `lazy`) — se prioriza su carga.

**Por qué:** casi siempre es el elemento LCP (Largest Contentful Paint) de la página; cargarla en diferido retrasa directamente esa métrica, que es la más visible para el usuario y la más pesada en SEO.

**Implementación (HTML):**
```html
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />
```

### 3.2 Resto de imágenes

**[REQUIRED]** Se aplica la regla general de `FRONTEND_ENGINEERING_STANDARD.md` 1.7: carga diferida por defecto, `width`/`height` explícitos.

### 3.3 Peso de imagen

**[RECOMMENDED]** Optimizar cada imagen para no comprometer el objetivo de Core Web Vitals (LCP <2.5s, sección 11 del estándar principal). Como referencia práctica actual, eso suele traducirse en: hero ~200KB, resto de imágenes ~100KB — esta cifra es una heurística de hoy, no una ley; lo que no se negocia es el objetivo de LCP que la sostiene.

### 3.4 Consistencia visual

**[RECOMMENDED]** Un solo estilo de imagen por landing (todo fotografía real, o todo ilustración) — mezclar ambos sin criterio comunica una landing armada con recursos de stock inconsistentes. Logos de "social proof" al mismo tamaño y alineación entre sí.

### 3.5 Texto alternativo

**[REQUIRED]** Se aplica la regla general de accesibilidad (`FRONTEND_ENGINEERING_STANDARD.md` sección 13.5).

---

## 4. Botones / CTAs

### 4.1 Jerarquía

**[REQUIRED]** Un CTA primario por viewport (máximo contraste, color de marca). CTAs secundarios con menor peso visual para acciones de menor prioridad (ej. "Ver demo" junto a "Empezar gratis").

### 4.2 Tamaño mayor que en el resto de la app

**[RECOMMENDED]** El CTA primario del Hero usa el tamaño de botón más grande disponible en el design system.

**Por qué:** el CTA de landing compite por atención en una página que el usuario nunca usó antes — necesita más peso visual que un botón dentro de una app donde el usuario ya sabe qué hacer.

**Implementación (Tailwind):**
```tsx
<Button variant="primary" size="lg" className="px-8 py-4 text-base font-semibold">
  Empezar gratis
</Button>
```

### 4.3 Microcopy

**[REQUIRED]** Texto de CTA con verbo de acción + beneficio o gratuidad, nunca genérico.

```
❌ "Enviar" / "Click aquí" / "Más información"
✅ "Empezar gratis" / "Reservar mi cupo" / "Ver planes"
```

### 4.4 Above the fold

**[REQUIRED]** El CTA primario del Hero es visible sin hacer scroll, tanto en el viewport de desktop como en el de mobile más común. Si no cabe con el copy actual, se acorta el copy — no se empuja el CTA fuera de vista.

### 4.5 Tracking

**[RECOMMENDED]** Cada CTA lleva un identificador único y descriptivo en un atributo de datos, para trackear conversión por bloque sin acoplar el componente a una librería de analytics específica.

**Implementación (React):**
```tsx
<Button data-cta="hero-primary" variant="primary" size="lg">Empezar gratis</Button>
<Button data-cta="pricing-cta" variant="primary" size="lg">Elegir plan</Button>
```

---

## 5. Espaciado entre secciones

### 5.1 Escala propia de padding vertical de sección

**[REQUIRED]** El padding vertical de cada bloque sigue una escala fija propia de landing, mayor que la escala de componentes de una app (`FRONTEND_ENGINEERING_STANDARD.md` 1.1) porque cada bloque necesita funcionar casi como una "pantalla" independiente.

```
Mobile:   64px
Tablet:   96px
Desktop:  128px
```

**Implementación (Tailwind):**
```tsx
<section className="py-16 md:py-24 lg:py-32">
```

### 5.2 Ancho de contenedor

**[RECOMMENDED]** Contenedor ancho (~1280px) para bloques con grid/cards; contenedor angosto (~640-768px, equivalente a 60-75 caracteres por línea) para bloques de puro texto (FAQ, testimonio individual).

### 5.3 Separación interna consistente

**[RECOMMENDED]** Separación fija entre el título de una sección y su subtítulo (~16px), y entre el header de la sección y su contenido principal (~48-64px).

### 5.4 Ritmo visual entre secciones

**[RECOMMENDED]** Alternar el color de fondo entre secciones consecutivas para crear separación visual, en vez de depender de líneas divisorias.

---

## 6. Tipografía del Hero y jerarquía

**[REQUIRED]** El headline del Hero es visualmente el elemento de mayor peso tipográfico de toda la página — nunca compite con un tamaño casi igual en otro bloque.

**[RECOMMENDED]**
- Headline: tamaño grande y responsive (ej. 36px mobile → 60px desktop), peso bold, interlineado ajustado. Menos de 10 palabras — si necesita más, es un párrafo, no un headline.
- Subheadline: tamaño intermedio (ej. 18-20px), color secundario (nunca el mismo tono del headline, para marcar jerarquía), ancho máximo para no estirar la línea. Menos de 25 palabras.

**Implementación (Tailwind):**
```tsx
<h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
  Promesa principal en pocas palabras
</h1>
<p className="mt-4 text-lg sm:text-xl text-ink-600 max-w-2xl">
  Subheadline que aclara para quién es y qué gana, sin repetir el headline.
</p>
```

---

## 7. Responsive

**[REQUIRED]** Mobile-first, igual que el resto del estándar (`FRONTEND_ENGINEERING_STANDARD.md` 1.8).

**[REQUIRED]** En mobile, si el Hero tiene imagen/video de apoyo, va debajo del texto y CTA — nunca empujando el CTA fuera del viewport inicial.

**[RECOMMENDED]** Logos de social proof / testimonios en mobile: carrusel horizontal con scroll, no un grid apretado e ilegible.

**[REQUIRED]** Se valida en los mismos 3 anchos de referencia del estándar principal (375 / 768 / 1280px) antes de dar la landing por terminada.

---

## 8. Performance y SEO

**[REQUIRED]** Los objetivos de Core Web Vitals de `FRONTEND_ENGINEERING_STANDARD.md` 11.4 aplican con más rigor aquí que en una app interna — la landing recibe tráfico frío (primera impresión, a menudo desde ads o WhatsApp), y ahí no hay margen: un usuario que nunca usó el producto no espera a que cargue.

**[REQUIRED]** Scripts de terceros (analytics, chat widget, pixels de ads) se cargan sin bloquear el render del Hero.

**[RECOMMENDED]** Ninguna animación en el Hero retrasa la pintura del contenido crítico — se anima después de que el contenido ya es visible.

---

## 9. Accesibilidad heredada

Aplica `FRONTEND_ENGINEERING_STANDARD.md` sección 13 sin excepción, con dos puntos específicos de landing:

**[REQUIRED]** Cuando el headline del Hero va sobre una imagen o gradiente, se agrega un overlay si el contraste real de texto no llega al mínimo AA — no se asume "se ve bien" a simple vista, se valida.

**[REQUIRED]** Los CTAs grandes del Hero y del CTA final llevan indicador de foco visible igual que cualquier botón de la app — son los elementos más importantes de toda la página, no pueden ser el punto débil de accesibilidad.

---

## Checklist rápido antes de dar por terminada una landing

- [ ] ¿Sigue el orden de bloques de la sección 1, sin secciones que no aportan a la conversión?
- [ ] ¿Un solo `<h1>`, jerarquía de headings sin saltos?
- [ ] ¿CTA primario del Hero y del CTA final usan el mismo texto/objetivo?
- [ ] ¿CTA visible sin scroll en desktop y mobile?
- [ ] ¿Hero image priorizada (no lazy), resto de imágenes lazy con width/height?
- [ ] ¿Meta tags (title, description, og:image) completos?
- [ ] ¿Padding de sección en la escala 64/96/128px, no valores sueltos?
- [ ] ¿Cada sección es su propio componente, dentro del límite de tamaño del estándar?
- [ ] ¿CTAs con atributo de tracking?
- [ ] ¿LCP <2.5s medido, no asumido?
- [ ] ¿Contraste de texto sobre imagen validado, foco visible en CTAs?
