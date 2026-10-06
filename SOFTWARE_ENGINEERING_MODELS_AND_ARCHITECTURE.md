# Modelos de Ingeniería de Software, Metodologías y Arquitectura — JCDigital Engineering Handbook

> **Guía y Manual de Referencia de Ingeniería de Software Profesional**  
> Síntesis completa de ciclos de vida, metodologías ágiles, patrones arquitectónicos, prácticas de ingeniería y bibliografía esencial.

---

## 1. Clasificación General del Ecosistema de Desarrollo

```
                    INGENIERÍA DE SOFTWARE
                              │
  ┌─────────────────┬─────────┴─────────┬──────────────────┐
  ↓                 ↓                   ↓                  ↓
CICLOS DE VIDA    ÁGILES & MARCOS    PRÁCTICAS ENG       ARQUITECTURA
• Waterfall       • Scrum            • TDD / BDD         • Modular Monolith
• V-Model         • Kanban           • CI/CD             • Event-Driven
• Iterativo       • XP               • GitHub Flow       • DDD
• Prototipado     • Shape Up         • Trunk-Based       • Microservicios
```

---

## 2. Modelos Clásicos de Ciclo de Vida

| Modelo | Concepto Principal | Cuándo Conviene |
| :--- | :--- | :--- |
| **Waterfall (Cascada)** | Fases secuenciales estrictas (Requisitos → Diseño → Código → QA → Deploy). | Requisitos 100% estables, contratos cerrados, hardware o proyectos altamente regulados. |
| **V-Model** | Cada fase de desarrollo tiene una fase correspondiente de verificación/pruebas. | Sistemas críticos donde la validación y certificación formal son prioritarias. |
| **W-Model** | Las pruebas comienzan en paralelo desde la definición misma de requisitos. | Proyectos con tolerancia cero a errores tardíos. |
| **Iterativo** | Se construye una versión base completa y se refina en cada ciclo. | Cuando los requisitos técnicos evolucionan con el aprendizaje. |
| **Incremental** | El sistema se entrega dividido en módulos funcionales utilizables. | Productos que necesitan generar valor financiero y tracción rápidamente. |
| **Prototyping** | Construcción de prototipos rápidos interactivos para validar con el usuario. | Requisitos ambiguos o interfaces innovadoras. |
| **Spiral (Espiral)** | Iteraciones centradas en la identificación y mitigación constante de riesgos. | Proyectos masivos, de alto riesgo técnico o financiero. |
| **RAD** | *Rapid Application Development*; ciclos ultrarrápidos basados en prototipos y herramientas no-code/low-code. | Aplicaciones internas de negocio donde la velocidad prima sobre la perfección técnica. |

---

## 3. Metodologías Ágiles & Marcos de Trabajo

### A. Scrum
- **Flujo:** `Product Backlog → Sprint Planning → Sprint (1-4 sem) → Incremento → Review → Retrospectiva`.
- **Ideal para:** Equipos medianos/grandes que desarrollan un producto propio continuamente.
- **Advertencia:** Para un desarrollador individual o freelancer, el Scrum estricto suele generar burocracia y reuniones innecesarias.

### B. Kanban (El Estándar Recomendado para JCDigital)
- **Flujo:** `Backlog → Solicitado → Análisis → Diseño → Desarrollo → QA → Deploy → Mantenimiento`.
- **Principio:** Visualización del flujo y **Límites de WIP (*Work in Progress*)** para evitar cuellos de botella y multitarea.
- **Ideal para:** Freelancers, agencias, soporte técnico y proyectos con flujo continuo de requerimientos.

### C. Extreme Programming (XP)
- **Pilares:** Pair programming, TDD, refactorización constante, lanzamientos pequeños e integración continua.
- **Ideal para:** Código que requiere calidad extrema y resistencia al cambio.

### D. Shape Up (37signals)
- **Concepto:** En lugar de estimar *"¿cuánto tiempo tardará X?"*, se define el **Apetito (*Appetite*)**: *"¿Cuánto tiempo estamos dispuestos a invertir para resolver este problema?"*.
- **Ciclos:** 6 semanas de desarrollo enfocado + 2 semanas de enfriamiento (*Cooldown*).

---

## 4. Prácticas de Ingeniería & Entrega de Software

### A. CI/CD & Pipeline de Automatización
```
git push ──> Cloudflare Edge / GitHub Actions ──> Tests & Lint ──> Build ──> Deploy Automático (0 Downtime)
```
- **Beneficio:** Elimina las transferencias manuales (FTP/SSH), garantizando que lo que se aprueba en Git pasa a producción de inmediato.

### B. TDD (Test-Driven Development) & BDD (Behavior-Driven Development)
- **Ciclo TDD:** `RED` (Escribir prueba que falla) ➔ `GREEN` (Escribir código mínimo que pasa) ➔ `REFACTOR` (Optimizar diseño).
- **BDD:** Especificación mediante escenarios en lenguaje ubicuo:  
  *Dado que [Contexto] ➔ Cuando [Acción] ➔ Entonces [Resultado Esperado]*.

### C. Estrategias de Ramas en Git
- **GitHub Flow:** Rama principal `main` siempre desplegable + ramas cortas `feature/*` o `fix/*` fusionadas mediante *Pull Request*. (Ideal para JCDigital).
- **Trunk-Based Development:** Todos los desarrolladores integran directamente en `main` múltiples veces al día, usando *Feature Flags* para ocultar funciones en progreso.

---

## 5. Diseño y Arquitectura de Software

### A. Modular Monolith (Monolito Modular)
> **La arquitectura más eficiente y práctica para freelancers y startups.**

- Una sola base de código y un solo despliegue, pero organizada rígidamente por módulos desacoplados:
```
src/
├── clientes/       (Dominio, Servicios, UI)
├── proyectos/      (Dominio, Servicios, UI)
├── cobros/         (Dominio, Servicios, UI)
├── proveedores/    (Dominio, Servicios, UI)
└── shared/         (UI Kit, DB Client, Utilidades)
```
- **Ventaja:** Cero sobrecoste de red o microservicios, pero lista para dividirse si un módulo requiere escalado independiente en el futuro.

### B. Domain-Driven Design (DDD)
- Enfoque centrado en modelar la lógica pura del negocio antes de escribir infraestructura:
  - **Entidades:** Objetos con identidad única (`Cliente`, `Proyecto`).
  - **Value Objects:** Objetos inmutables definidos solo por sus atributos (`Dinero`, `Dirección`, `Email`).
  - **Agregados & Repositorios:** Límites de consistencia y persistencia.
  - **Bounded Context:** Fronteras donde un término del negocio tiene un significado inequívoco.

### C. Event-Driven Architecture
- Los componentes se comunican mediante publicación y suscripción de eventos asíncronos (`PedidoCreado`, `PagoRecibido`).

---

## 6. El Blueprint Recomendado para JCDigital

```
                    PROYECTO JCDIGITAL
                            │
             Fase 1: Discovery & Prototipado
                            │
              ┌─────────────┴─────────────┐
              ↓                           ↓
        Kanban Board             Prototipo Interactivo
              │                           │
              └─────────────┬─────────────┘
                            ↓
             Fase 2: Arquitectura Monolito Modular
                            │
             Fase 3: Git Flow + CI/CD en Cloudflare
                            │
             Fase 4: Core Web Vitals + QA
                            │
             Fase 5: Deploy & Monitoreo en Vivo
```

---

## 7. Bibliografía y Recursos de Estudio Recomendados

### 📚 Libros Gratuitos y Abiertos
1. **Software Engineering: Standing on the Shoulders of Giants** — Libro abierto y moderno sobre procesos, arquitectura, testing y calidad.
2. **Scrum y XP desde las trincheras** *(Henrik Kniberg)* — Casos reales y prácticos de implementación sin rodeos teóricos.
3. **Ingeniería de Software Moderna** *(Marco Tulio Valente)* — Cobertura amplia y práctica en español.
4. **Domain-Driven Design Reference** *(Eric Evans)* — Compendio oficial de conceptos clave de DDD.
5. **Recursos de Martin Fowler** (`martinfowler.com`) — Biblioteca esencial sobre refactorización, microservicios y patrones.

### 📖 Libros Clave para Inversión a Largo Plazo
1. *The Pragmatic Programmer* — Andrew Hunt & David Thomas.
2. *Clean Architecture* — Robert C. Martin.
3. *Refactoring* — Martin Fowler.
4. *Domain-Driven Design* — Eric Evans.
5. *Designing Data-Intensive Applications* — Martin Kleppmann.
6. *Continuous Delivery* — Jez Humble & David Farley.

---

### 🎓 Orden de Lectura Óptimo:
`1. Open SWE Book` ➔ `2. Scrum/XP Trincheras` ➔ `3. Refactoring` ➔ `4. Clean Architecture` ➔ `5. DDD Reference` ➔ `6. Designing Data-Intensive Applications`.
