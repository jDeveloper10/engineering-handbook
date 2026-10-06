---
title: "Estándar de Tailwind CSS v4"
category: 01_Frontend
doc_type: estandar
tags: [tailwind, css, v4, design-system, tokens]
summary: "Estándar del dominio Frontend para Tailwind CSS v4: configuración, tokens, design system, responsive, dark mode y patrones."
keywords: [tailwind, css, v4, design-system, tokens, responsive, dark-mode]
updated: 2026-08-30
status: current
---

# TAILWIND CSS V4 ENGINEERING STANDARD

> **Stack de referencia:** Tailwind CSS v4 + Vite + @tailwindcss/vite
> **Depende de:** FRONTEND_ENGINEERING_STANDARD.md (Nivel 1)
> **Aplica a:** Todo proyecto que use Tailwind CSS v4

---

## 01. Configuración

### 1.1 Instalación con Vite

**[REQUIRED]** Usar `@tailwindcss/vite` plugin (no postcss):

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

### 1.2 Importación CSS

**[REQUIRED]** Importar Tailwind en CSS principal:

```css
/* src/index.css */
@import "tailwindcss";
```

### 1.3 Configuración de theme

**[REQUIRED]** Definir tokens en CSS (v4 usa CSS-first config):

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  /* Colores semánticos */
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --color-brand-900: #1e3a8a;
  
  --color-success: #16a34a;
  --color-danger: #dc2626;
  --color-warning: #d97706;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  
  /* Tipografía */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-display: 'Playfair Display', serif;
}
```

---

## 02. Design System

### 2.1 Tokens semánticos

**[REQUIRED]** Colores nombrados por significado, no por color:

```tsx
// ✅ CORRECTO — tokens semánticos
<button className="bg-brand-500 hover:bg-brand-600 text-white">
  Guardar
</button>
<button className="bg-danger hover:bg-red-700 text-white">
  Eliminar
</button>

// ❌ PROHIBIDO — colores hardcodeados
<button className="bg-[#3b82f6] hover:bg-[#2563eb] text-white">
  Guardar
</button>
```

### 2.2 Escala de spacing

**[REQUIRED]** Usar escala fija, nunca valores libres:

```tsx
// ✅ CORRECTO — escala fija
<div className="p-4 gap-8">   {/* 16px, 32px */}
<div className="m-2 mt-4">   {/* 8px, 16px */}

// ❌ PROHIBIDO — valores libres
<div className="p-[13px] gap-[37px]">
```

### 2.2 Tipografía

**[REQUIRED]** Máximo 2 familias tipográficas:

```css
@theme {
  --font-sans: 'Inter', system-ui, sans-serif;     /* Body text */
  --font-display: 'Playfair Display', serif;        /* Headlines */
}
```

```tsx
<h1 className="font-display text-4xl font-bold">Título</h1>
<p className="font-sans text-base">Párrafo</p>
```

---

## 03. Responsive Design

### 3.1 Mobile-first

**[REQUIRED]** Estilos base para mobile, breakpoints hacia arriba:

```tsx
// ✅ CORRECTO — mobile-first
<div className="p-4 md:p-8 lg:p-12">
  {/* Mobile: 16px, Tablet: 32px, Desktop: 48px */}
</div>

// ❌ PROHIBIDO — desktop-first
<div className="p-12 md:p-8 lg:p-4">
```

### 3.2 Breakpoints estándar

**[REQUIRED]** Usar breakpoints de Tailwind:

| Breakpoint | Clase | Ancho |
|---|---|---|
| sm | `sm:` | 640px |
| md | `md:` | 768px |
| lg | `lg:` | 1024px |
| xl | `xl:` | 1280px |
| 2xl | `2xl:` | 1536px |

### 3.3 Contenedor

**[REQUIRED]** Contenedor centrado con max-width:

```tsx
<div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  {/* Contenido centrado, max 1280px */}
</div>
```

---

## 04. Dark Mode

### 4.1 Toggle explícito

**[REQUIRED]** Dark mode con toggle del usuario (no solo `prefers-color-scheme`):

```tsx
// src/components/ThemeToggle.tsx
export function ThemeToggle() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark';
  });
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);
  
  return (
    <button onClick={() => setDark(!dark)}>
      {dark ? '☀️' : '🌙'}
    </button>
  );
}
```

### 4.2 Clases dark

**[REQUIRED]** Usar prefijo `dark:`:

```tsx
<div className="bg-white dark:bg-gray-900 text-black dark:text-white">
  {/* Se adapta al modo oscuro */}
</div>
```

---

## 05. Componentes

### 5.1 Variantes con cva

**[REQUIRED]** Usar `class-variance-authority` para variantes:

```typescript
// src/components/ui/button.tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-brand-500 text-white hover:bg-brand-600',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
        danger: 'bg-danger text-white hover:bg-red-700',
        ghost: 'hover:bg-gray-100 text-gray-900',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-12 px-6 text-lg',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
);

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, 
  VariantProps<typeof buttonVariants> {}

export function Button({ variant, size, className, ...props }: ButtonProps) {
  return <button className={buttonVariants({ variant, size, className })} {...props} />;
}
```

### 5.2 clsx + tailwind-merge

**[REQUIRED]** Combinar clases con `clsx` y `tailwind-merge`:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Uso
<div className={cn(
  'base-class',
  isActive && 'active-class',
  isDisabled && 'disabled-class'
)}>
```

---

## 06. Anti-patrones

### 6.1 @apply moderado

**[RECOMMENDED]** `@apply` solo para patrones de bajo nivel reusados por 10+ elementos:

```css
/* ✅ ACEPTABLE — patrón reusado */
@layer components {
  .btn-primary {
    @apply bg-brand-500 text-white px-4 py-2 rounded-md hover:bg-brand-600;
  }
}

/* ❌ PROHIBIDO — @apply para no escribir clases */
<div class="@apply p-4 m-2 flex items-center">
```

### 6.2 CSS Modules no mezclar

**[REQUIRED]** No mezclar Tailwind con CSS Modules o styled-components:

```tsx
// ❌ PROHIBIDO — mezclar sistemas
import styles from './Button.module.css';
<button className={`${styles.button} bg-brand-500`}>

// ✅ CORRECTO — solo Tailwind
<button className="bg-brand-500 px-4 py-2">
```

---

## Checklist Tailwind

- [ ] @tailwindcss/vite configurado
- [ ] Tokens semánticos definidos en @theme
- [ ] Spacing en escala fija (4, 8, 16, 24, 32, 48)
- [ ] Máximo 2 familias tipográficas
- [ ] Mobile-first responsive
- [ ] Dark mode con toggle explícito
- [ ] cva para variantes de componentes
- [ ] cn() para combinar clases
- [ ] Sin colores hardcodeados
- [ ] Sin @apply excesivo
