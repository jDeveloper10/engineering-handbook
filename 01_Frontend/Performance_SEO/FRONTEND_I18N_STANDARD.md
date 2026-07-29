---
title: "Patrón de Internacionalización (i18n)"
category: 01_Frontend
tags: [react, i18next, idiomas, traducciones]
status: current
---

# 🌍 PATRÓN INTERNACIONALIZACIÓN (i18n)

## 🎯 ¿Qué es y por qué es crítico?
Un software global debe adaptarse a diferentes idiomas, formatos de fecha, monedas y direcciones de lectura (RTL). Hardcodear texto en los componentes hace imposible escalar a nuevos mercados.

> **REGLA INQUEBRANTABLE:** NUNCA hardcodear strings en la UI. TODO texto (botones, alertas, tooltips) DEBE vivir en los archivos de traducción JSON. El componente solo llama a `t('clave')`.

---

## 🗂️ ESTRUCTURA DE ARCHIVOS

Se separa por idioma, y dentro del idioma, por *namespaces* (archivos JSON) para no tener un solo archivo gigante de 10,000 líneas que sature la memoria inicial.

```text
/locales
  ├── es/
  │   ├── common.json     # Botones genéricos, navbar, footer
  │   ├── auth.json       # Login, registro, errores auth
  │   └── billing.json    # Pagos, facturas
  ├── en/
  │   ├── common.json
  │   ├── auth.json
  │   └── billing.json
  ├── pt/ (Portugués)
  ├── fr/ (Francés)
  └── de/ (Alemán)
```

**Ejemplo de `en/common.json`:**
```json
{
  "welcomeMessage": "Welcome back, {{name}}!",
  "buttons": {
    "save": "Save Changes",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "messagesCount_one": "You have 1 new message.",
  "messagesCount_other": "You have {{count}} new messages."
}
```

---

## ⚙️ CONFIGURACIÓN CORE (react-i18next)

Usamos `i18next` con detección automática de idioma en el navegador.

```typescript
// src/i18n.ts
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import Backend from 'i18next-http-backend' // Carga JSONs asíncronamente

i18n
  // Detectar idioma (LocalStorage > URL > Browser settings)
  .use(LanguageDetector)
  // Cargar traducciones lazy (no engorda el bundle JS)
  .use(Backend)
  // Conectar con React
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',      // Idioma si el detectado no existe
    supportedLngs: ['en', 'es', 'pt', 'fr', 'de'],
    ns: ['common', 'auth', 'billing'], // Namespaces declarados
    defaultNS: 'common',    // Archivo por defecto si no se especifica
    interpolation: {
      escapeValue: false    // React ya protege contra XSS
    },
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json', // Ruta de los assets
    }
  })

export default i18n
```

---

## 💻 USO EN COMPONENTES (React Hooks)

El hook `useTranslation` nos da la función `t()` para traducir y el objeto `i18n` para cambiar de idioma.

```tsx
import { useTranslation } from 'react-i18next'

export function UserDashboard({ user, messagesCount }) {
  // Cargamos el namespace 'common' por defecto, y 'billing' explícitamente
  const { t, i18n } = useTranslation(['common', 'billing'])

  // Cambiar idioma en caliente (sin recargar página)
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng)
    
    // Soporte RTL (Árabe, Hebreo)
    document.dir = i18n.dir(lng)
    document.documentElement.lang = lng
  }

  return (
    <div>
      <header className="flex justify-between">
        {/* Interpolación de variables: "Bienvenido de nuevo, Juan!" */}
        <h1>{t('welcomeMessage', { name: user.name })}</h1>
        
        {/* Selector de idioma */}
        <select value={i18n.language} onChange={(e) => changeLanguage(e.target.value)}>
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="ar">العربية (RTL)</option>
        </select>
      </header>

      {/* Pluralización Automática basada en 'count' */}
      <div className="alert">
        {t('messagesCount', { count: messagesCount })}
      </div>

      {/* Accediendo a Keys Anidadas */}
      <button className="bg-blue-600">
        {t('buttons.save')}
      </button>

      {/* Accediendo a otro namespace (billing.json) */}
      <p>{t('billing:invoice.overdue')}</p>
      
      {/* Formateo Nativo de Moneda por Locale (Intl.NumberFormat) */}
      <p>
        Balance: {new Intl.NumberFormat(i18n.language, { 
          style: 'currency', currency: 'USD' 
        }).format(user.balance)}
      </p>
    </div>
  )
}
```

---

## 🚀 FORMATOS LOCALIZADOS (Fechas y Monedas)

No uses librerías pesadas como `moment`. Confía en el API nativa de JavaScript `Intl`, pasándole el `i18n.language`.

```tsx
// FECHAS (jueves, 15 de marzo de 2024 vs Thursday, March 15, 2024)
const formatDate = (date: Date, locale: string) => {
  return new Intl.DateTimeFormat(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

// NÚMEROS (1.000,50 vs 1,000.50)
const formatNumber = (num: number, locale: string) => {
  return new Intl.NumberFormat(locale).format(num)
}
```
