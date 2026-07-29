---
title: "Estándar Avanzado de Accesibilidad Web (WCAG 2.1 AA y ARIA)"
category: 01_Frontend
doc_type: estandar
tags: [accessibility, a11y, wcag, aria, keyboard-navigation, focus-trap, screen-readers]
summary: "Estándar avanzado de accesibilidad web (a11y): checklist WCAG 2.1 AA, navegación por teclado, captura y gestión de foco en modales (Focus Trapping), roles ARIA y pruebas automatizadas con axe-core."
keywords: [accessibility, a11y, wcag, aria, keyboard, focus-trap, screen-reader, axe-core, lighthouse]
updated: 2026-07-27
status: current
---

# ♿ ESTÁNDAR AVANZADO DE ACCESIBILIDAD WEB (WCAG 2.1 AA)

## 🎯 OBJETIVO
Garantizar que todas las interfaces del sistema sean totalmente operables por usuarios que dependen de lectores de pantalla, navegación por teclado o configuraciones de accesibilidad.

---

## 🎯 REGLAS INQUEBRANTABLES

**[REQUIRED] A11Y-001: Todo elemento interactivo DEBE ser accesible por teclado (Tecla Tab, Enter, Space).** Queda prohibido asignar eventos `onClick` en divs o spans sin `role="button"` y `tabIndex={0}`.

> **Por qué:** un `onClick` en un `div` no recibe foco de teclado ni se activa con Enter o Espacio: para quien no usa mouse, ese elemento simplemente no existe. Es la misma clase de bug que un enlace roto, solo que invisible para quien prueba con mouse.

**[REQUIRED] A11Y-002: Gestión Estricta de Foco en Modales (Focus Trap).** Cuando un modal se abre, el foco debe capturarse dentro de él y restaurarse al elemento detonador al cerrarse.

> **Por qué:** sin captura de foco, tabular dentro de un modal abierto saca el foco hacia elementos de la página que quedaron detrás, invisibles pero seleccionables — confuso con mouse y directamente inutilizable con teclado o lector de pantalla.

**[REQUIRED] A11Y-003: Contraste de Color >= 4.5:1 para texto normal.** Verificación automatizada en CI/CD con `@axe-core/playwright`.

> **Por qué:** por debajo de 4.5:1 el texto se vuelve difícil de leer con baja visión o en pantallas con reflejo de luz, y es el umbral objetivo de WCAG AA, no una preferencia estética. Verificarlo en CI es lo que impide que un ajuste de paleta lo rompa sin que nadie lo note.

---

## ⌨️ 1. GESTIÓN DE FOCO Y FOCUS TRAPPING EN MODALES

```tsx
// src/components/Modal.tsx
import { useEffect, useRef } from 'react'

export function Modal({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement
      modalRef.current?.focus()
    } else {
      previousFocusRef.current?.focus() // Restaurar foco
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div
        ref={modalRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className="bg-background p-6 rounded-lg max-w-md w-full focus:outline-none"
      >
        {children}
        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 bg-surface border rounded-lg text-sm"
        >
          Cerrar
        </button>
      </div>
    </div>
  )
}
```

---

## 🧪 2. TESTING AUTOMATIZADO CON PLAYWRIGHT Y AXE-CORE

```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('Verificar que el Dashboard cumple con WCAG 2.1 AA', async ({ page }) => {
  await page.goto('/dashboard')

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()

  expect(accessibilityScanResults.violations).toEqual([])
})
```

---

## 📋 CHECKLIST DE ACCESIBILIDAD

- [ ] Jerarquía de encabezados única por página (`<h1>` principal, luego `<h2>`, `<h3>`).
- [ ] Atributos `alt` descriptivos en todas las imágenes.
- [ ] Navegación completa por teclado con indicador de foco visible (`focus-visible`).
- [ ] Captura de foco (Focus Trap) en diálogos y modales.
- [ ] Pruebas automatizadas con `@axe-core/playwright` sin violaciones WCAG 2.1 AA.
