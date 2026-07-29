---
title: "Patrón Sistema de Temas (Claro/Oscuro)"
category: 01_Frontend
tags: [react, tailwind, css-variables, dark-mode, ux]
status: current
---

# 🌗 PATRÓN SISTEMA DE TEMAS (Claro/Oscuro/Sistema)

## 🎯 ¿Qué es y por qué es crítico?
Un sistema de temas moderno detecta la preferencia del OS del usuario, le permite sobreescribirla manualmente, y no presenta un "flashazo" blanco al cargar la página en modo oscuro.

> **REGLA INQUEBRANTABLE:** Soportar Dark Mode y System Mode es OBLIGATORIO desde el día 1. PROHIBIDO hardcodear colores de Tailwind (`bg-gray-100`); usar SIEMPRE variables CSS semánticas (`bg-surface-primary`).

---

## 🎨 1. CONFIGURACIÓN TAILWIND + CSS VARIABLES

Usamos la clase `dark` inyectada en el `<html>` y definimos paletas semánticas en `globals.css`.

**`tailwind.config.js`**
```javascript
module.exports = {
  darkMode: 'class', // <--- CRÍTICO: Basado en clase 'dark', no media query
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)',
        },
        surface: 'var(--surface)',
      }
    }
  }
}
```

**`globals.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: #ffffff;
    --foreground: #09090b;
    --primary: #2563eb;
    --primary-foreground: #ffffff;
    --surface: #f4f4f5;
  }
 
  .dark {
    --background: #09090b;
    --foreground: #fafafa;
    --primary: #3b82f6;
    --primary-foreground: #ffffff;
    --surface: #18181b;
  }
  
  /* Transición suave global (opcional pero recomendado) */
  body {
    @apply transition-colors duration-200 ease-in-out;
  }
}
```

---

## ⚡ 2. ANTI-FLASH SCRIPT (En el `<head>`)

Si React se encarga de inyectar la clase `dark`, habrá un milisegundo blanco mientras el bundle JS carga. Para evitarlo, ponemos este script minificado directamente en el `index.html` o `layout.tsx` (antes del body).

```html
<!-- index.html -->
<head>
  <script>
    try {
      var theme = localStorage.getItem('omni-theme');
      if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    // Excepción documentada al anti-patrón "catch vacío" de AGENTS.md §5:
    // localStorage lanza en modo incógnito / cookies bloqueadas. El único efecto de fallar
    // es que se usa el tema por defecto — cosmético, sin pérdida de datos ni de estado.
    } catch (_) { /* sin tema guardado: se queda el default. Intencional. */ }
  </script>
</head>
```

---

## 💻 3. CONTEXTO DE REACT (Theme Provider)

Controla el estado (`light`, `dark`, `system`), persistencia en `localStorage` y actualiza la clase del DOM.

```tsx
import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
  theme: 'system',
  setTheme: () => null,
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'omni-theme',
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (typeof window !== 'undefined' ? (localStorage.getItem(storageKey) as Theme) || defaultTheme : defaultTheme)
  )

  useEffect(() => {
    const root = window.document.documentElement

    // 1. Remover clases viejas
    root.classList.remove('light', 'dark')

    // 2. Lógica para modo "Sistema"
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches ? 'dark' : 'light'
      root.classList.add(systemTheme)
      return
    }

    // 3. Aplicar modo explícito
    root.classList.add(theme)
  }, [theme])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)
  if (context === undefined)
    throw new Error('useTheme must be used within a ThemeProvider')
  return context
}
```

---

## 🎨 4. USO EN LA UI (El Theme Switcher)

```tsx
import { useTheme } from '@/hooks/useTheme'
import { Moon, Sun, Monitor } from 'lucide-react'

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="flex border rounded-lg bg-surface">
      <button
        onClick={() => setTheme('light')}
        className={`p-2 rounded-l-lg ${theme === 'light' ? 'bg-primary text-primary-foreground' : 'text-foreground'}`}
      >
        <Sun className="w-4 h-4" />
      </button>
      
      <button
        onClick={() => setTheme('system')}
        className={`p-2 ${theme === 'system' ? 'bg-primary text-primary-foreground' : 'text-foreground'}`}
      >
        <Monitor className="w-4 h-4" />
      </button>
      
      <button
        onClick={() => setTheme('dark')}
        className={`p-2 rounded-r-lg ${theme === 'dark' ? 'bg-primary text-primary-foreground' : 'text-foreground'}`}
      >
        <Moon className="w-4 h-4" />
      </button>
    </div>
  )
}
```
