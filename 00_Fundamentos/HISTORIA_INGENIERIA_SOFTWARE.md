---
title: "00_Fundamentos — Historia de la Ingeniería de Software"
category: 00_Fundamentos
tags:
  - history
  - foundations
  - software-engineering
  - methodologies
  - paradigms
summary: "Recorrido cronológico y conceptual de la Ingeniería de Software como disciplina: desde la 'crisis del software' de 1968 hasta la era de la IA generativa. No es un estándar normativo; es el contexto histórico que explica por qué cada estándar del handbook existe."
keywords:
  - historia
  - nato-conference
  - waterfall
  - agile
  - devops
  - dijkstra
  - brooks
  - beck
  - hamilton
  - crisis-del-software
  - metodologias
  - paradigmas
updated: 2026-07-26
status: current
---

# Historia de la Ingeniería de Software

> Este documento no contiene reglas `[REQUIRED]` ni `[RECOMMENDED]`. No es un estándar técnico:
> es el **contexto histórico** que subyace a todos los estándares del handbook. Explica por qué
> el software se escribe, se prueba, se despliega y se mantiene como se hace hoy — y por qué
> este handbook existe.

---

## 1. Antes de la Ingeniería de Software (1945–1967)

### 1.1 Los primeros programas

El software nació atado al hardware. Los primeros programas se escribían en **código máquina** o
**ensamblador**, directamente en los paneles de la computadora (ENIAC, 1945). No existía el concepto
de "programador" como rol separado del ingeniero eléctrico.

**Hitos tempranos:**

| Año | Evento | Significado |
|-----|--------|-------------|
| 1945 | Von Neumann Architecture | El concepto de programa almacenado — software separable del hardware |
| 1954 | FORTRAN (Backus, IBM) | Primer lenguaje de alto nivel; separa al programador del hardware |
| 1958 | ALGOL | Introduce bloques estructurados, la base de la programación moderna |
| 1960 | COBOL | Primer lenguaje orientado a negocios |
| 1964 | PL/I | Intento de lenguaje universal para negocio + científico; prefigura la complejidad |

### 1.2 La crisis del software

Para mediados de la década de 1960, el hardware avanzaba según la Ley de Moore (1965), pero el
software no: los proyectos crecían en complejidad más rápido que la capacidad de gestionarlos.
Los presupuestos se duplicaban, los cronogramas se triplicaban, y el software entregado solía ser
incorrecto o inutilizable.

**Problemas concretos detectados:**

- No existían metodologías de desarrollo — cada programador trabajaba a su criterio.
- No había gestión de requisitos: se asumía que el cliente sabía lo que quería y no cambiaría de
  opinión.
- El testing era informal o inexistente.
- Un programador eficiente y otro ineficiente tenían diferencias de 10x en productividad, sin que
  la organización pudiera cerrar esa brecha.
- Los proyectos grandes (sistemas operativos, bancarios, militares) fallaban sistemáticamente.

---

## 2. El nacimiento de la disciplina (1968–1979)

### 2.1 La Conferencia NATO de 1968

El 7 de octubre de 1968, el Comité de Ciencia de la OTAN reunió en Garmisch (Alemania Occidental)
a más de 50 expertos para discutir lo que llamaron la **"Crisis del Software"**. Allí se acuñó
oficialmente el término **"Ingeniería de Software"**.

Friedrich L. Bauer, uno de los organizadores, lo definió así:

> *"El establecimiento y uso de principios de ingeniería sólidos para obtener software económicamente
> que sea fiable y funcione en máquinas reales."*

**Por qué importa:** por primera vez, se reconoció que construir software no era un acto artesanal
individual, sino un proceso de ingeniería que requería métodos, medición, estándares y repetibilidad.

Una segunda conferencia NATO en 1969 (Roma) profundizó estos temas.

### 2.2 Edsger Dijkstra y la programación estructurada

Edsger Dijkstra (1930–2002) fue el primer teórico en demostrar que la lógica del software podía y
debía formalizarse. Su carta de 1968 *"Go To Statement Considered Harmful"* (Communications of the
ACM) argumentó que la sentencia `GOTO` hacía que los programas fueran imposibles de razonar
formalmente.

**Aporte clave:** la **programación estructurada** — todo programa puede escribirse con solo tres
estructuras de control: secuencia, selección (if), e iteración (while). Esto no era solo estética:
era la base para poder demostrar que un programa hacía lo que decía hacer.

### 2.3 Margaret Hamilton y el término "ingeniería de software"

Margaret Hamilton, líder del equipo de software del proyecto Apolo de la NASA, usó el término
**"software engineering"** en los años 60, antes de la conferencia NATO, para que el desarrollo de
software fuera tratado con la misma seriedad que otras disciplinas de ingeniería en el programa
espacial. Su trabajo en tolerancia a fallos (el software del Apolo 11 se recuperó de errores de
hardware en pleno alunizaje) estableció estándares de robustez que hoy damos por sentados.

### 2.4 El modelo en cascada (1970)

Winston Royce publicó en 1970 *"Managing the Development of Large Software Systems"*, donde describió
un proceso lineal de fases:

```
Requisitos → Diseño → Implementación → Verificación → Mantenimiento
```

Irónicamente, Royce **criticaba** este modelo como riesgoso y proponía un enfoque iterativo con
retroalimentación entre fases. Pero la industria leyó la descripción, no la crítica, y adoptó el
modelo en cascada como el estándar durante más de 20 años.

### 2.5 Fred Brooks y *The Mythical Man-Month* (1975)

Fred Brooks, gerente del desarrollo de IBM System/360, publicó en 1975 *The Mythical Man-Month*,
una colección de ensayos sobre por qué los proyectos de software fracasan.

**Leyes de Brooks (vigentes 50 años después):**

1. **Ley de Brooks:** "Agregar gente a un proyecto atrasado lo atrasa más" — porque la comunicación
   crece cuadráticamente con el tamaño del equipo.
2. **No hay bala de plata** (1986): ninguna tecnología, herramienta o metodología producirá por sí
   sola una mejora de 10x en productividad en una década. El software es complejo por naturaleza
   (esencia) y solo se puede atacar la complejidad accidental.

Brooks distinguió entre **complejidad esencial** (inherente al problema) y **complejidad accidental**
(impuesta por la tecnología/herramientas). Esta distinción es la razón de ser de este handbook:
los estándares reducen la complejidad accidental para que el equipo pueda concentrarse en la esencial.

---

## 3. La era de la metodología (1980–2000)

### 3.1 Métodos formales y CASE

En los 80 proliferaron los **métodos formales** (VDM, Z, B-Method) para especificar y verificar
software matemáticamente, principalmente en sistemas críticos (ferroviarios, aeroespaciales).
Paralelamente, las herramientas **CASE** (Computer-Aided Software Engineering) intentaron automatizar
el análisis y diseño con diagramas (Yourdon, Gane & Sarson).

Ninguno logró adopción masiva fuera de nichos de alta criticidad, por su alto costo de aprendizaje
y rigidez.

### 3.2 La orientación a objetos (1980s–1990s)

La programación orientada a objetos (OO) —Smalltalk (70s), C++ (1985), Java (1995)— no fue solo un
cambio de sintaxis, sino de paradigma: encapsular datos y comportamiento en entidades que modelan el
mundo real. Esto permitió manejar complejidades que los lenguajes procedurales no soportaban bien.

**Grady Booch, Ivar Jacobson y James Rumbaugh** unificaron sus metodologías OO en el **UML** (Unified
Modeling Language, 1997) y el **Proceso Unificado Rational (RUP)**, el intento más serio de
estandarizar el proceso completo de desarrollo.

### 3.3 El Manifiesto Ágil (2001)

En febrero de 2001, 17 desarrolladores (Kent Beck, Martin Fowler, Robert C. Martin, Jeff Sutherland,
Ken Schwaber, entre otros) se reunieron en Snowbird, Utah, y publicaron el **Manifiesto por el
Desarrollo Ágil de Software**:

> *"Estamos descubriendo formas mejores de desarrollar software tanto por nuestra propia experiencia
> como ayudando a otros. A través de este trabajo hemos llegado a valorar:*
>
> - *Individuos e interacciones* sobre procesos y herramientas.
> - *Software funcionando* sobre documentación exhaustiva.
> - *Colaboración con el cliente* sobre negociación contractual.
> - *Respuesta ante el cambio* sobre seguir un plan.
>
> *Esto es, aunque valoramos los elementos de la derecha, valoramos más los de la izquierda."*

**Por qué importa:** el Manifiesto Ágil no inventó nada nuevo — XP (Extreme Programming) ya existía,
Scrum también — pero dio un marco conceptual que legitimó la iteración rápida, el feedback continuo
y la priorización flexible. Hoy, Agile en sus diversas formas (Scrum, Kanban, XP) es el paradigma
dominante, aunque frecuentemente mal implementado (Agile institucional vs. Agile real).

### 3.4 Figuras del Agile

- **Kent Beck:** creador de **Extreme Programming (XP)** — integración continua, TDD, pair
  programming, releases cortos. Su libro *Extreme Programming Explained* (1999) fue el texto
  fundacional del movimiento.
- **Martin Fowler:** refactorización como disciplina. *Refactoring* (1999) estableció que el código
  debía mejorarse continuamente (no solo escribirse una vez).
- **Robert C. Martin ("Uncle Bob"):** principios SOLID, código limpio. *Clean Code* (2008) definió
  estándares de legibilidad que este handbook hereda.
- **Jeff Sutherland y Ken Schwaber:** cocreadores de **Scrum**, el marco ágil más usado en la
  industria.

---

## 4. DevOps y la automatización total (2009–presente)

### 4.1 El origen de DevOps

En 2009, en la conferencia Velocity (San José), John Allspaw y Paul Hammond (Flickr) presentaron
*"10+ Deploys Per Day: Dev and Ops Cooperation"*. Mostraron cómo Flickr desplegaba más de 10 veces
al día integrando los equipos de desarrollo y operaciones.

Patrick Debois, inspirado por esa charla, organizó la primera conferencia **DevOpsDays** en Gante
(Bélgica) en 2009, acuñando el término **DevOps**.

DevOps no es una metodología ni una herramienta: es una **cultura** que elimina el muro entre
"desarrollar" y "operar". Se apoya en tres pilares:

1. **Integración Continua (CI):** todo cambio se integra y prueba automáticamente.
2. **Entrega Continua (CD):** todo cambio integrado puede desplegarse a producción con un clic.
3. **Infraestructura como Código (IaC):** servidores, redes y configuraciones se versionan como
   código.

### 4.2 La automatización como principio

La automatización elimina el error humano y la fatiga de tareas repetitivas:

- Testing automatizado (unitario, integración, E2E, regresión visual)
- Linters y formateadores (ESLint, Prettier)
- Despliegue automático (GitHub Actions → Cloudflare Pages/Workers)
- Monitoreo y alertas (Sentry, Datadog, Grafana)

Este handbook incorpora estos principios en todos sus dominios: no se documenta un proceso manual
que pueda automatizarse.

---

## 5. Paradigmas de programación

### 5.1 Programación imperativa (1950s–)

El programador le dice a la máquina **cómo** hacer algo, paso a paso. Lenguajes: C, Pascal, BASIC.

### 5.2 Programación funcional (1958–)

Basada en funciones matemáticas, sin estado mutable ni efectos secundarios. Lisp (1958) fue el
primer lenguaje funcional. Haskell (1990) es su exponente puro. Hoy, lenguajes mainstream adoptan
características funcionales: map, filter, reduce, inmutabilidad (JavaScript, Python, Rust).

### 5.3 Programación orientada a objetos (1960s–)

Objetos que combinan estado y comportamiento. Smalltalk (72), C++ (85), Java (95), TypeScript (12).

### 5.4 Programación declarativa

El programador dice **qué** quiere, no cómo lograrlo. SQL es el ejemplo más exitoso. También: HTML,
expresiones regulares, herramientas de IaC (Terraform, Pulumi).

### 5.5 Convergencia moderna

Los lenguajes modernos son **multiparadigma**: TypeScript, Rust, Kotlin, Swift, Go. No se trata de
elegir uno, sino de aplicar el paradigma correcto para cada problema.

---

## 6. Lecciones de la historia para este handbook

Cada sección del handbook existe porque la historia demostró que sin ella, el software fracasa:

| Lección | Fundamento histórico | Documento del handbook |
|---------|---------------------|----------------------|
| Los requisitos cambian — el proceso debe acomodarlo | Crisis del software + Agile | [`../02_Backend/`](../02_Backend/), [`../03_API/`](../03_API/) |
| El testing no es opcional — es ingeniería | Crash del Ariane 5 (1996), Therac-25 (1987) | [`../06_Testing/`](../06_Testing/) |
| Los estándares reducen complejidad accidental | Brooks, *No Silver Bullet* | Todos los documentos |
| La automatización elimina errores humanos | DevOps, deploys manuales → accidentes | [`../07_DevOps/`](../07_DevOps/), [`../Engineering-OS/23-Automations.md`](../Engineering-OS/23-Automations.md) |
| El código se lee más de lo que se escribe | Clean Code (Martin), Refactoring (Fowler) | [`../01_Frontend/`](../01_Frontend/), [`../14_DX/`](../14_DX/) |
| Sin seguridad desde el diseño, el costo es 10x mayor | OWASP Top 10, incidentes reales | [`../05_Security/`](../05_Security/) |
| El software se escribe para humanos primero | Dijkstra, programación estructurada | [`../01_Frontend/`](../01_Frontend/), [`../13_AI_Rules/`](../13_AI_Rules/) |

---

## 7. La era actual: IA generativa (2022–presente)

A partir de 2022 (ChatGPT, GitHub Copilot), la IA generativa comenzó a transformar la ingeniería
de software de formas que los paradigmas anteriores no anticiparon:

- **Generación de código:** Copilot, Cursor, Codebuff asisten o reemplazan escritura manual.
- **Revisión automatizada:** IA revisa PRs, detecta bugs y sugiere mejoras.
- **Documentación y tests:** la IA escribe documentación y pruebas que los humanos eluden.
- **Prototipado rápido:** de idea a prototipo funcional en minutos en vez de días.

**Implicación para este handbook:** los estándares se vuelven **más** importantes, no menos. La IA
produce mucho código rápido, pero sin estándares verificables produce mucha deuda rápido también.
Este handbook es el contrato que garantiza que la velocidad de la IA no sacrifica la calidad.

---

## 8. Cronología visual

```
1945 ─ Arquitectura Von Neumann (programa almacenado)
1954 ─ FORTRAN (primer lenguaje de alto nivel)
1957 ─ FORTRAN II (subrutinas, separación en módulos)
1958 ─ ALGOL (bloques estructurados) · Lisp (programación funcional)
1960 ─ COBOL (software de negocio)
1964 ─ PL/I (intento de lenguaje universal)
1968 ─ CONFERENCIA NATO ─ se acuña "Ingeniería de Software"
1968 ─ Dijkstra: "Go To Statement Considered Harmful"
1969 ─ Nace Unix (Kernighan, Ritchie, Thompson)
1970 ─ Royce: modelo en cascada (malinterpretado)
1972 ─ C (Ritchie) · Smalltalk (OO real) · Tesis de la "Ingeniería de Software" (Hamilton)
1975 ─ Brooks: The Mythical Man-Month
1985 ─ C++ (Stroustrup) · Métodos formales en sistemas críticos
1986 ─ Brooks: "No Silver Bullet"
1995 ─ Java (Gosling) · JavaScript (Eich) · Nace la web
1997 ─ UML (Booch, Jacobson, Rumbaugh) · RUP
1999 ─ XP (Beck) · Refactoring (Fowler)
2001 ─ MANIFIESTO ÁGIL (Snowbird, Utah)
2003 ─ Scrum (Sutherland, Schwaber) formalizado
2008 ─ Clean Code (Martin) · Git (Linus Torvalds, 2005) domina
2009 ─ DEVOPS nace (DevOpsDays Ghent, Allspaw+Hammond)
2012 ─ TypeScript (Anders Hejlsberg)
2015 ─ React (Facebook) · Docker (portabilidad de infra)
2019 ─ GitHub Actions (CI/CD nativo)
2022 ─ ChatGPT · GitHub Copilot · Era de IA generativa en el desarrollo
2024 ─ AI-agents autónomos para tareas de ingeniería (DevOps, testing, revisión)
2026 ─ Este handbook: el estándar que permite a la IA y al humano producir juntos
```

---

## 9. Para seguir aprendiendo

| Recurso | Tipo | Por qué |
|---------|------|---------|
| *The Mythical Man-Month* (Brooks, 1975) | Libro | Sigue siendo el mejor libro sobre por qué los proyectos fracasan |
| *No Silver Bullet* (Brooks, 1986) | Artículo | Distingue complejidad esencial de accidental |
| *Extreme Programming Explained* (Beck, 1999) | Libro | El texto fundacional de las prácticas ágiles reales |
| *The Clean Architecture* (Martin, 2017) | Libro | Cómo estructurar software que dure |
| *The DevOps Handbook* (Kim et al., 2016) | Libro | El manual de la cultura DevOps |
| *A History of Software Engineering* (IEEE) | Artículo | Línea de tiempo estándar de la disciplina |
| *SWEBOK* (IEEE Computer Society) | Estándar | El cuerpo de conocimiento de la ingeniería de software |
| [Wikipedia: Historia de la ingeniería del software](https://es.wikipedia.org/wiki/Historia_de_la_ingenier%C3%ADa_del_software) | Web | Referencia abierta y actualizada |

---

## Checklist de verificación

- [ ] ¿El documento cubre desde 1945 hasta el presente (2026)?
- [ ] ¿Cada hito importante tiene su año y contexto?
- [ ] ¿Las figuras clave están nombradas con su aporte específico?
- [ ] ¿La cronología es coherente y completa?
- [ ] ¿El documento explica *por qué* la historia importa para el resto del handbook?
- [ ] ¿Las lecciones históricas se mapean contra documentos reales del handbook?
- [ ] ¿El frontmatter YAML tiene title, category, tags, summary, keywords, updated y status?
