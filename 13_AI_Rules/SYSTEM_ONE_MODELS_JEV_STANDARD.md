---
title: "Modelos System One (Jev, Clef-flash y Laya) en Arquitectura de Software"
category: 13_AI_Rules
doc_type: estandar
tags: [ai, system-one, jev, clef-flash, laya, cloudflare, agents, latency, decisions, rlcd, probabilistic-branching]
summary: "Estándar de arquitectura para modelos System One: decisiones deterministas y tipadas de ultra baja latencia (<50ms), paralelismo masivo de preguntas, calibración de confianza RLCD, uso de Cloudflare Clef-flash a coste $0 (10k neuronas diarias), Laya en local y orquestación híbrida System 1 + System 2."
keywords: [system-one, jev, clef-flash, laya, cloudflare-workers-ai, rlcd, llm, fast-decisions, agents, compound-ai, conditional-logic, typescript-sdk]
updated: 2026-10-05
status: current
---

# MODELOS SYSTEM ONE (JEV, CLEF-FLASH Y LAYA) EN ARQUITECTURA DE SOFTWARE

## OBJETIVO
Definir los principios de arquitectura, patrones de integración y reglas de diseño para incorporar modelos de inteligencia artificial **System One** (específicamente **Clef-flash** de Cloudflare Workers AI, **Laya** de código abierto y **Jev** de TypeSafe AI) en sistemas backend, portales web, microservicios y agentes de software autónomos.

Este estándar establece cómo utilizar modelos no generativos de decisiones rápidas para erradicar la sobrecarga de latencia y costo provocada por el uso indebido de Large Language Models (LLMs) generativos en tareas de clasificación y bifurcación condicional.

---

## CONCEPTO FUNDAMENTAL: SISTEMA 1 VS SISTEMA 2 EN IA

Inspirado en la teoría cognitiva de Daniel Kahneman (*Thinking, Fast and Slow*), los sistemas de inteligencia artificial modernos se dividen en dos paradigmas complementarios:

| Característica | Sistema 1 (System One: Clef-flash, Laya, Jev) | Sistema 2 (System Two: Claude, GPT-4, o1, Gemini) |
|---|---|---|
| **Naturaleza** | **No generativo**. Clasificación y toma de decisiones directa. | **Generativo autoregresivo**. Predicción token por token. |
| **Mecánica** | Un solo forward-pass evaluando múltiples preguntas en paralelo. | Bucle recursivo con atención densa y Chain-of-Thought (CoT). |
| **Latencia típica** | **15 ms – 60 ms** (tiempo de red casi puro). | **1,500 ms – 12,000 ms** (depende de la longitud de tokens). |
| **Salida** | Tipos estructurados nativos (booleanos, categorías, escalares, intervalos). | Texto libre en lenguaje natural o JSON parseado por regex/grammar. |
| **Entrenamiento** | **RLCD** (Reinforcement Learning for Calibrated Decisions). | RLHF / RLAIF orientado a conversación y seguimiento de instrucciones. |
| **Rol en el sistema** | **If / Else probabilístico** integrado en el código backend. | Razonamiento reflexivo, síntesis compleja y redacción humana. |

---

## CATÁLOGO DE MODELOS SYSTEM ONE DISPONIBLES

### 1. Cloudflare Clef & Clef-flash (Recomendación Primaria Cloud / Edge)
* **Licencia:** Apache 2.0 (Open Source).
* **Entorno de ejecución:** Cloudflare Workers AI (nativo en el Edge) o autoalojado con vLLM.
* **Coste:** **$0.00 en la cuota gratuita diaria de 10,000 Neurons de Cloudflare** (suficiente para ~700 a 1,200 decisiones/día). Después del límite, cuesta apenas $0.011 por cada 1,000 Neurons adicionales.
* **Ventaja clave:** Sin servidores, sin GPU propia, latencia de borde (<30ms) acoplado a Workers, Pages, D1 y KV.

### 2. Laya (Recomendación Primaria On-Premise / Local)
* **Creador:** Convai Innovations (basado en ModernBERT-large, 421M parámetros).
* **Licencia:** Apache 2.0.
* **Entorno de ejecución:** Local en CPU o GPU ligera vía ONNX / HuggingFace.
* **Coste:** **100% Gratis e ilimitado de por vida**. Ideal para CI/CD, scripts de terminal y herramientas locales.

### 3. Jev (TypeSafe AI - SaaS Comercial)
* **Creador:** TypeSafe AI (fundada por Diogo Almeida, ex-OpenAI / InstructGPT).
* **Licencia:** API propietaria de pago ($0.042 por millón de tokens de entrada).
* **Uso recomendado:** Proyectos con clientes corporativos que ya mantengan contratos y SLA centralizado con TypeSafe AI.

---

## REGLAS INQUEBRANTABLES

**[REQUIRED] S1-001: NUNCA usar un LLM generativo (System 2) para decisiones binarias, routing o clasificación cuando el SLA exija < 200ms.**
Cualquier tarea de clasificación condicional, etiquetado de intenciones, triaje o control de flujo debe resolverse mediante un modelo System 1 (Clef-flash o Laya). Invocar un LLM pesado para retornar un booleano es un antipatrón crítico de latencia y coste.

> **Por qué:** un LLM autoregresivo genera tokens secuencialmente a través de capas de atención complejas, tardando segundos y cobrando por entrada/salida. Un modelo System 1 ejecuta un forward-pass único en decenas de milisegundos a una fracción insignificante del coste.

**[REQUIRED] S1-002: Inferencia en paralelo obligatoria (Batch Evaluation).**
Al evaluar un estado (texto, ticket, payload, log), todas las preguntas y variables de decisión requeridas para esa entidad deben formularse en una única llamada `predict()` o invocación al modelo. NUNCA encadenar llamadas secuenciales para evaluar propiedades del mismo estado.

> **Por qué:** la arquitectura de los modelos System One está optimizada para proyectar el embedding de estado contra múltiples cabezales de decisión en paralelo. Hacer llamadas secuenciales multiplica la latencia de red innecesariamente.

**[REQUIRED] S1-003: Validación estricta con esquemas Zod / Pydantic antes de side-effects.**
Aunque el SDK o la API garantice retornos estructurados y tipados, el backend debe validar y sanear la carga útil contra un esquema en tiempo de ejecución (runtime schema) antes de mutar base de datos o activar webhooks financieros.

> **Por qué:** la IA sigue siendo probabilística. Tipar estáticamente con TypeScript no protege contra valores fuera de rango o campos ausentes si la red o el servicio sufren una degradación.

**[REQUIRED] S1-004: Umbral de confianza calibrada (RLCD Thresholding).**
Ninguna acción destructiva o transacción irreversible debe ejecutarse de forma automática si la puntuación de confianza reportada es inferior al umbral configurado (`MIN_CONFIDENCE`, mínimo recomendado: `0.85`). Si la confianza es baja, el sistema debe derivar el flujo a revisión humana o escalar a un modelo System 2 deliberativo.

> **Por qué:** los modelos System One están entrenados con RLCD para que sus probabilidades correspondan matemáticamente con la probabilidad real de acierto. Ignorar esta confianza equivale a ignorar la telemetría de riesgo del modelo.

**[REQUIRED] S1-005: Anonimización estricta de PII antes de enviar el `state`.**
Aplica la regla transversal **AI-001**: nunca enviar correos reales, tarjetas de crédito, contraseñas ni números de documento de identidad al payload de inferencia sin sanitización previa.

---

## ARQUITECTURA HÍBRIDA: PATRÓN COMPOUND AI (SISTEMA 1 + SISTEMA 2)

El mayor valor de los modelos System One no es reemplazar a los LLMs, sino actuar como **capa de corte rápido (Fast Path)**, **buscador para usuarios no técnicos** y **filtro de guardia (Guardrails)** en sistemas compuestos:

```
                 ┌────────────────────────────────┐
                 │    Petición / Evento Entrante  │
                 └────────────────┬───────────────┘
                                  │
                                  ▼
                 ┌────────────────────────────────┐
                 │       Sanitización de PII      │
                 └────────────────┬───────────────┘
                                  │
                                  ▼
                 ┌────────────────────────────────┐
                 │   SYSTEM 1 (Clef-flash / 30ms) │
                 │  - Intención: "consulta_saldo" │
                 │  - Urgencia: 2                 │
                 │  - Requiere Razonamiento: NO   │
                 │  - Confianza: 0.98             │
                 └───────┬────────────────┬───────┘
                         │                │
            [Requiere LLM? NO]      [Requiere LLM? SÍ]
                         │                │
                         ▼                ▼
        ┌────────────────────────┐  ┌────────────────────────┐
        │       FAST PATH        │  │     SLOW / DEEP PATH   │
        │ Consulta DB directa    │  │ LLM System 2 (Claude)  │
        │ Respuesta en < 80ms    │  │ Razonamiento y síntesis│
        │ Coste: $0.0000         │  │ Respuesta en 2-4 segs  │
        └────────────────────────┘  └────────────────────────┘
```

---

## CASO DE APLICACIÓN: BUSCADOR INTELIGENTE PARA USUARIOS NO TÉCNICOS

Cuando un usuario no técnico (cliente, socio, auditor legal) consulta una plataforma técnica o el propio Handbook (280+ documentos), no conoce la jerga ni los nombres de archivos.

### Flujo de Experiencia:
1. El usuario escribe en lenguaje llano: *"¿Qué leyes de Panamá me aplican si quiero cobrar suscripciones y retener impuestos?"*
2. **Clef-flash (en 25 ms)** analiza el texto:
   - `isTechnicalUser`: `false`
   - `primaryDomain`: `"16_Accounting"`
   - `secondaryDomain`: `"05_Security"`
   - `matchedDocuments`: `["PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md", "PANAMA_LEGAL_DATA_PRIVACY_STANDARD.md"]`
   - `confidence`: `0.96`
3. La interfaz web responde inmediatamente destacando las 2 normas exactas con explicaciones resumidas sin obligarlo a navegar árboles de carpetas complejos.

---

## IMPLEMENTACIÓN EN CLOUDFLARE WORKERS AI (CLEF-FLASH A COSTE $0)

Aprovechando el paquete diario de **10,000 Neurons gratuitas** de Cloudflare:

```typescript
export interface Env {
  AI: any; // Binding de Cloudflare Workers AI
}

export interface DecisionResult {
  intent: 'billing' | 'technical' | 'legal' | 'general';
  urgency: number;
  requiresHumanReview: boolean;
  confidence: number;
}

export async function routeUserRequest(
  text: string,
  env: Env
): Promise<DecisionResult> {
  // 1. Sanitizar datos sensibles
  const sanitized = text.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]');

  // 2. Inferencia en el Edge con Clef-flash (System 1)
  const response = await env.AI.run('@cf/cloudflare/clef-flash', {
    state: sanitized,
    questions: {
      intent: 'What is the user intent? (billing, technical, legal, general)',
      urgency: 'Rate urgency from 1 to 5',
      requiresHumanReview: 'Does this issue require human oversight or escalate to tier 2?',
    },
  });

  return {
    intent: response.answers.intent.value,
    urgency: Number(response.answers.urgency.value),
    requiresHumanReview: Boolean(response.answers.requiresHumanReview.value),
    confidence: response.overallConfidence ?? 0.95,
  };
}
```

---

## IMPLEMENTACIÓN ALTERNATIVA EN TYPESCRIPT CON TYPESAFE SDK (JEV)

```typescript
import { TypeSafeClient } from '@typesafe-ai/sdk';
import { z } from 'zod';

const TriageSchema = z.object({
  department: z.enum(['billing', 'technical', 'sales', 'security']),
  isChurnRisk: z.boolean(),
  urgency: z.number().min(1).max(5),
  confidence: z.number().min(0).max(1),
});

export async function triageWithJev(stateText: string) {
  const client = new TypeSafeClient({
    apiKey: process.env.TYPESAFE_API_KEY!,
  });

  const prediction = await client.predict({
    state: stateText,
    questions: {
      department: "Which department should handle this? (billing, technical, sales, security)",
      isChurnRisk: "Is the user expressing intent to cancel or refund?",
      urgency: "Rate the urgency from 1 to 5",
    },
  });

  return TriageSchema.parse({
    department: prediction.answers.department?.value,
    isChurnRisk: Boolean(prediction.answers.isChurnRisk?.value),
    urgency: Number(prediction.answers.urgency?.value),
    confidence: prediction.overallConfidence ?? 1.0,
  });
}
```

---

## MATRIZ DE DECISIÓN: CUÁNDO USAR SYSTEM 1 VS SYSTEM 2

| Criterio del Requerimiento | Seleccionar System 1 (Clef-flash / Laya) | Seleccionar System 2 (LLM Tradicional) |
|---|---|---|
| **Latencia requerida** | Crítica (< 100 ms). | Flexible (> 1,000 ms). |
| **Tipo de salida** | Estructurada, tipada, categórica o numérica. | Prosa, código sintáctico, explicaciones o resúmenes. |
| **Control de flujo** | Routing, bifurcación condicional, filtros. | Agente conversacional, redacción de email, análisis libre. |
| **Calibración de error** | Necesitas conocer la probabilidad matemática de acierto. | El modelo puede alucinar con alta convicción. |
| **Coste por millón de eventos** | **$0.00** (Cloudflare Free / Local) o fracción de centavo. | Alto ($5 - $30 por millón de tokens). |

---

## CHECKLIST DE REVISIÓN PARA AUDITORÍAS (PR REVIEW)

- [ ] ¿Se utiliza System 1 (Clef-flash / Laya) en lugar de un LLM generativo para decisiones de clasificación o control de flujo?
- [ ] ¿Se agruparon todas las preguntas sobre el mismo estado en un único llamado batch en paralelo?
- [ ] ¿Existe un esquema Zod o runtime schema validando la respuesta antes de ejecutar lógica crítica de negocio?
- [ ] ¿Se implementó un umbral de confianza (`confidence >= 0.85`) con fallback a revisión humana o modelo deliberativo?
- [ ] ¿Se comprobó que el payload no incluye PII sensible sin anonimizar?
- [ ] ¿Se priorizó el uso de Cloudflare Clef-flash (coste $0 en 10k neuronas) o Laya antes de incurrir en APIs de pago?
