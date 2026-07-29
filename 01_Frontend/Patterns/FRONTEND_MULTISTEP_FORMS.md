---
title: "Patrón Formularios Multi-Step"
category: 01_Frontend
tags: [react, formularios, wizard, zod, ux]
summary: "Formularios largos divididos en pasos tipo wizard para reducir abandono: hook useMultiStepForm, validación por paso con Zod, persistencia del progreso y patrones de navegación."
keywords: [react, formularios, wizard, zod, ux, multi-step, largos, divididos, pasos, tipo, reducir, abandono, hook, usemultistepform]
updated: 2026-07-29
status: current
---

# 📝 PATRÓN FORMULARIOS MULTI-STEP

## 🎯 ¿Qué es y cuándo usarlo?
Los formularios largos (> 10 campos) causan fatiga cognitiva y abandono. Dividir el formulario en pasos lógicos (Wizard) aumenta exponencialmente la tasa de conversión.

> **REGLA INQUEBRANTABLE:** NUNCA perder datos del formulario al cambiar de paso o si el usuario recarga accidentalmente la página. Persistencia en `localStorage` o URL es OBLIGATORIA.

---

## 💻 HOOK: `useMultiStepForm`

Un hook para orquestar la navegación y el estado de guardado.

```tsx
import { useState, useEffect } from 'react'
import { useForm, FieldValues, UseFormReturn } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

interface MultiStepConfig<T extends FieldValues> {
  schema: z.ZodType<T>
  storageKey: string
  steps: string[]
}

export function useMultiStepForm<T extends FieldValues>({
  schema,
  storageKey,
  steps
}: MultiStepConfig<T>) {
  
  // 1. Persistencia en LocalStorage (Recarga de página segura)
  const loadSavedData = (): Partial<T> => {
    if (typeof window === 'undefined') return {}
    const saved = localStorage.getItem(storageKey)
    return saved ? JSON.parse(saved) : {}
  }

  const methods = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues: loadSavedData() as DefaultValues<T>,
    mode: 'onTouched' // Validar al salir del input
  })

  // Auto-guardar en localStorage ante cualquier cambio (Debounced en apps grandes)
  useEffect(() => {
    const subscription = methods.watch((value) => {
      localStorage.setItem(storageKey, JSON.stringify(value))
    })
    return () => subscription.unsubscribe()
  }, [methods.watch, storageKey])

  // 2. Navegación de Pasos
  const [currentStep, setCurrentStep] = useState(0)
  
  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === steps.length - 1

  // 3. Patrón 2: Validación Parcial por Paso
  // NUNCA dejar avanzar si el paso actual es inválido
  const next = async (fieldsToValidate?: (keyof T)[]) => {
    let isValid = true
    if (fieldsToValidate && fieldsToValidate.length > 0) {
      isValid = await methods.trigger(fieldsToValidate)
    }
    
    if (isValid && !isLastStep) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const back = () => {
    if (!isFirstStep) setCurrentStep(prev => prev - 1)
  }

  const clearStorage = () => localStorage.removeItem(storageKey)

  return {
    methods,
    currentStep,
    stepName: steps[currentStep],
    isFirstStep,
    isLastStep,
    next,
    back,
    clearStorage,
    progress: ((currentStep + 1) / steps.length) * 100
  }
}
```

---

## 🚀 IMPLEMENTACIÓN DEL WIZARD (UI)

```tsx
// Validación por Paso usando Pick de Zod
const accountSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

const profileSchema = z.object({
  fullName: z.string().min(3),
  phone: z.string().optional() // Pasos opcionales
})

const fullSchema = accountSchema.merge(profileSchema)
type FormData = z.infer<typeof fullSchema>

export function OnboardingWizard() {
  const { 
    methods, currentStep, next, back, isFirstStep, isLastStep, progress, clearStorage 
  } = useMultiStepForm<FormData>({
    schema: fullSchema,
    storageKey: 'onboarding-draft',
    steps: ['Account', 'Profile', 'Summary']
  })

  const onSubmit = async (data: FormData) => {
    if (!isLastStep) return // Prevenir submit prematuro en "Enter"
    
    await api.register(data)
    clearStorage() // Limpiar draft
    window.location.href = '/dashboard'
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg">
      
      {/* 1. Barra de Progreso Animada */}
      <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
        <div 
          className="h-full bg-blue-600 transition-all duration-300 ease-in-out" 
          style={{ width: `${progress}%` }}
        />
      </div>

      <form onSubmit={methods.handleSubmit(onSubmit)}>
        
        {/* 2. Renderizado Condicional del Paso Actual */}
        {currentStep === 0 && (
          <div className="step-account">
            <h2>Crea tu cuenta</h2>
            <input {...methods.register('email')} placeholder="Email" />
            {methods.formState.errors.email && <span>{methods.formState.errors.email.message}</span>}
            <input type="password" {...methods.register('password')} placeholder="Password" />
          </div>
        )}

        {currentStep === 1 && (
          <div className="step-profile">
            <h2>Completa tu perfil</h2>
            <input {...methods.register('fullName')} placeholder="Nombre Completo" />
          </div>
        )}

        {currentStep === 2 && (
          <div className="step-summary">
            <h2>Resumen (Antes de enviar)</h2>
            <pre className="text-sm bg-gray-50 p-2">
              {JSON.stringify(methods.getValues(), null, 2)}
            </pre>
          </div>
        )}

        {/* 3. Controles de Navegación */}
        <div className="flex justify-between mt-8">
          <button type="button" onClick={back} disabled={isFirstStep}>Atrás</button>
          
          {!isLastStep ? (
            <button 
              type="button" 
              // Validar explícitamente los campos del paso 0 antes de ir al 1
              onClick={() => next(currentStep === 0 ? ['email', 'password'] : ['fullName'])}
            >
              Siguiente
            </button>
          ) : (
            <button type="submit" className="bg-blue-600 text-white">Finalizar</button>
          )}
        </div>
      </form>
    </div>
  )
}
```

## 🧠 PATRONES DE NAVEGACIÓN
1. **Wizard Lineal Estricto:** Validación dura, sin atajos. Botón "Siguiente" bloqueado hasta que el paso es válido.
2. **Navegación por Pestañas:** El usuario puede saltar libremente, pero no puede hacer `Submit` final sin llenar los requeridos.
3. **Pasos Opcionales (Skippable):** Incluir un botón claro "Omitir este paso por ahora" que limpia las validaciones de ese tab y avanza.
