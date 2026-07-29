---
title: "Estándar Avanzado de Internacionalización (i18n, RTL y Pluralización)"
category: 01_Frontend
tags: [i18n, l10n, rtl, intl, pluralization, lazy-loading, translation]
summary: "Estándar avanzado para aplicaciones i18n/L10n: soporte para lenguajes RTL (Árabe/Hebreo), reglas de pluralización complejas, formateo numérico/moneda con Intl API, detección automática de locale y lazy loading de traducciones."
keywords: [i18n, l10n, rtl, intl, pluralization, locale, translation, lazy-loading]
updated: 2026-07-27
status: current
---

# 🌐 ESTÁNDAR AVANZADO DE INTERNACIONALIZACIÓN (I18N) Y L10N

## 🎯 OBJETIVO
Garantizar la adaptación cultural y lingüística de la aplicación para mercados globales, soportando idiomas RTL (derecha a izquierda), reglas de pluralización dinámicas y formateo de fechas y divisas seguras.

---

## 🎯 REGLAS INQUEBRANTABLES

**I18N-001: NUNCA hardcodear cadenas de texto en componentes UI.** Todos los textos expuestos al usuario deben provenir de claves de traducción.

**I18N-002: Formateo de fechas, números y monedas estricto con `Intl` API.** Queda prohibido concatenar cadenas para construir fechas o formatear valores monetarios manualmente.

**I18N-003: Carga Diferida (Lazy Loading) de archivos de traducción.** Solo descargar el archivo JSON del idioma activo para evitar inflar el bundle inicial.

---

## 🌍 1. SOPORTE RTL (RIGHT-TO-LEFT) Y PLURALIZACIÓN

### Configuración del Documento y Dirección CSS
```typescript
// Cambia automáticamente la dirección del layout (dir="rtl") según el idioma seleccionado
export function setAppLanguage(lang: string) {
  const isRtl = ['ar', 'he', 'fa'].includes(lang)
  document.documentElement.lang = lang
  document.documentElement.dir = isRtl ? 'rtl' : 'ltr'
}
```

### Formateo Nativo con Intl API
```typescript
// Formatear Monedas
export function formatCurrency(amount: number, locale: string, currency: string) {
  return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount)
}

// Formatear Fechas Relativas (ej. "hace 5 minutos")
export function formatRelativeTime(value: number, unit: Intl.RelativeTimeFormatUnit, locale: string) {
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
  return rtf.format(value, unit)
}
```

---

## 📋 CHECKLIST DE I18N AVANZADO

- [ ] Cero cadenas de texto plano hardcodeadas en JSX.
- [ ] Cambio de atributo `dir="rtl"` para idiomas de derecha a izquierda.
- [ ] Uso exclusivo de `Intl.NumberFormat` e `Intl.DateTimeFormat`.
- [ ] Carga dinámica de archivos JSON de traducción por demanda.
- [ ] Tags `hreflang` configurados en las cabeceras HTML para SEO.
