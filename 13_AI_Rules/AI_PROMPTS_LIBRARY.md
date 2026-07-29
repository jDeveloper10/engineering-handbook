---
title: "Librería de Prompts del Handbook"
category: 13_AI_Rules
doc_type: referencia
tags: [ai-rules, prompts, ia, plantillas]
summary: "Prompts reutilizables y parametrizados para las tareas recurrentes del handbook: crear componentes, páginas completas de landing, dashboard y CRUD, endpoints con migración y refactorizaciones."
keywords: [prompts, ia, plantillas, componente, landing, dashboard, crud, refactor]
updated: 2026-07-21
status: current
---

# AI PROMPTS LIBRARY — Prompts reutilizables del handbook

> Nivel 2 del dominio `13_AI_Rules`, depende de [AI_WORKFLOW.md](AI_WORKFLOW.md) (Nivel 1). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md).
>
> Prompts listos para copiar. Cada uno está parametrizado con `{placeholders}` y ordena leer los documentos exactos del handbook que la tarea requiere, en el orden de lectura de `AI_WORKFLOW.md` §2. Todos asumen que la IA sigue el protocolo completo de `AI_WORKFLOW.md` — los prompts son el atajo de arranque, no un reemplazo del protocolo.
>
> Convención de rutas: los prompts usan rutas relativas a la raíz del handbook (`01_Frontend/...`). Si el handbook vive en otra ubicación en tu entorno, reemplaza el prefijo una sola vez. Ver la guía de adaptación por modelo al final.

---

## 1. Crear componente nuevo

**Cuándo usarlo:** una pieza de UI reutilizable (botón, card, input, badge...), no una página completa.

```
Crea el componente {nombre_componente} para {descripción_de_uso}.

Antes de escribir código, lee y aplica:
1. 13_AI_Rules/AI_WORKFLOW.md (protocolo completo)
2. 00_HANDBOOK_FORMAT.md (qué significa REQUIRED/RECOMMENDED)
3. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md — §01 (tokens de diseño),
   §04 (Component Rules), §07 (TypeScript), §13 (Accessibility)
4. 01_Frontend/FRONTEND_HTML_STRUCTURE_STANDARD.md (semántica, nada de div-soup)

Requisitos no negociables:
- Variantes vía props ({variantes_esperadas}), nunca copias del componente.
- Todos los estados visuales: default, hover, active, focus-visible, disabled
  {y loading si aplica}.
- Cero valores hardcodeados que el design system tokeniza (color, spacing, tipografía).
- Máximo ~200 líneas; si lo excede, divide antes de entregar.

Al terminar: corre el checklist final de FRONTEND_ENGINEERING_STANDARD.md sobre
el componente y declara qué reglas RECOMMENDED desviaste y por qué.
```

## 2. Crear página completa — Landing

**Cuándo usarlo:** landing de marketing/producto, pública, orientada a conversión.

```
Crea la landing page de {producto} cuyo objetivo de conversión es {CTA_principal}.
Público: {público_objetivo}. Estilo visual deseado: {estilo_o_"proponer"}.

Antes de escribir código, lee y aplica en este orden:
1. 13_AI_Rules/AI_WORKFLOW.md
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md (Nivel 1 completo)
3. 01_Frontend/FRONTEND_LANDING_PATTERNS.md (estructura de bloques, jerarquía de CTAs)
4. 01_Frontend/FRONTEND_UI_STYLE_CATALOG.md — elige UN estilo y extrae sus tokens
5. 01_Frontend/FRONTEND_RESPONSIVE_STANDARD.md y FRONTEND_COLOR_CONTRAST_STANDARD.md
6. 01_Frontend/FRONTEND_MICROCOPY_STANDARD.md para todos los textos

Requisitos no negociables:
- Un solo CTA primario por vista; el resto visualmente secundario.
- Mobile-first, validada en 375 / 768 / 1280 px.
- Un solo h1; jerarquía de headings real; imágenes con width/height y alt.
- Patrón de UI por tipo de información (FRONTEND_UI_PATTERNS.md), no cards por defecto.

Al terminar: checklist de FRONTEND_LANDING_PATTERNS.md + declaración de desviaciones.
```

## 3. Crear página completa — Dashboard

**Cuándo usarlo:** panel interno con métricas, gráficos y navegación persistente.

```
Crea el dashboard de {módulo} que muestra {métricas_y_datos_principales}
para el rol de usuario {rol}.

Antes de escribir código, lee y aplica en este orden:
1. 13_AI_Rules/AI_WORKFLOW.md
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md (Nivel 1 completo)
3. 01_Frontend/FRONTEND_DASHBOARD_PATTERNS.md (layout, jerarquía de KPIs)
4. 01_Frontend/FRONTEND_ANALYTICS_CHARTS_STANDARD.md (qué gráfico por tipo de dato)
5. 01_Frontend/FRONTEND_SIDEBAR_PATTERNS.md y FRONTEND_NAVIGATION_PATTERNS.md
6. 01_Frontend/FRONTEND_STATES_PATTERNS.md (loading, empty, error de cada widget)
7. 01_Frontend/FRONTEND_FORMATTING_STANDARD.md (números, fechas, monedas)

Requisitos no negociables:
- Cada widget maneja explícitamente loading / empty / error — sin pantallas en blanco.
- Tipo de gráfico elegido por tipo de dato, con la regla citada; no "gráfico bonito".
- Datos tabulares en tabla real (FRONTEND_TABLE_PATTERNS.md), no grid de cards.

Al terminar: checklist de FRONTEND_DASHBOARD_PATTERNS.md + declaración de desviaciones.
```

## 4. Crear página completa — Módulo CRUD

**Cuándo usarlo:** alta/listado/edición/borrado de una entidad de negocio, extremo a extremo.

```
Crea el módulo CRUD de {entidad} con campos {lista_de_campos}.
Operaciones: {crear/editar/eliminar/ver_detalle}. Volumen esperado: {n_registros}.

Antes de escribir código, lee y aplica en este orden:
1. 13_AI_Rules/AI_WORKFLOW.md
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md — especialmente §09 (Forms)
3. 01_Frontend/FRONTEND_CRUD_PATTERNS.md (secuencia listado → form → confirmar)
4. 01_Frontend/FRONTEND_TABLE_PATTERNS.md, FRONTEND_MODALS_PATTERNS.md,
   FRONTEND_STATES_PATTERNS.md, FRONTEND_NOTIFICATIONS_PATTERNS.md
5. Si incluye backend: 03_API/API_ENGINEERING_STANDARD.md y
   04_Database/DATABASE_ENGINEERING_STANDARD.md (usa además el prompt 5)

Requisitos no negociables:
- Modal vs drawer vs página según el árbol de decisión de CRUD_PATTERNS §3 — cítalo.
- Eliminación siempre con confirmación que nombra el ítem exacto.
- Listado con estados empty (primera vez vs sin resultados de filtro), loading y error.

Al terminar: checklist de FRONTEND_CRUD_PATTERNS.md + declaración de desviaciones.
```

## 5. Crear endpoint + migración

**Cuándo usarlo:** una operación de backend nueva que toca la base de datos.

```
Crea el endpoint {método} {ruta} que {qué_hace}, incluyendo la migración de DB
necesaria para {cambio_de_esquema}.

Antes de escribir código, lee y aplica en este orden:
1. 13_AI_Rules/AI_WORKFLOW.md
2. 03_API/API_ENGINEERING_STANDARD.md (naming de ruta, método, códigos de estado,
   formato de respuesta, paginación si es listado)
3. 02_Backend/BACKEND_ENGINEERING_STANDARD.md — §02 (capas handler/service),
   §04 (auth middleware), §05 (validación de entrada)
4. 04_Database/DATABASE_ENGINEERING_STANDARD.md — §01–05 (naming, tipos,
   columnas estándar, constraints), §07 (RLS), §08 (migraciones)
5. 05_Security/SECURITY_ENGINEERING_STANDARD.md — §05 (RLS), §07 (rate limiting),
   §08 (validación de entrada)

Requisitos no negociables:
- La migración es un archivo versionado en el repo, con rollback pensado.
- Toda tabla nueva lleva RLS y columnas estándar desde el día uno.
- Validación de entrada en el borde del worker; el handler no toca la DB directo.
- Respuesta en el formato estándar del handbook, con códigos de estado correctos.

Al terminar: checklists de API_ENGINEERING_STANDARD.md y
DATABASE_ENGINEERING_STANDARD.md + declaración de desviaciones.
```

## 6. Refactorizar componente gigante (>200 líneas)

**Cuándo usarlo:** un componente existente viola el límite de tamaño/responsabilidad.

```
Refactoriza {ruta_del_archivo} ({n_líneas} líneas) sin cambiar su comportamiento
observable ni su API pública salvo que sea imprescindible (y en ese caso, avisa antes).

Antes de tocar código, lee:
1. 13_AI_Rules/AI_WORKFLOW.md — en especial §6 (no inventar complejidad)
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md — §02 (arquitectura por feature,
   dependencia unidireccional UI → hooks → servicios), §04 (Component Rules:
   un componente = una responsabilidad, máx ~200 líneas), §05 (State Management)

Método:
- Lista primero las responsabilidades que hoy conviven en el archivo, citando la
  regla que cada una viola (documento + sección).
- Propón la división (subcomponentes, hooks extraídos, servicios) ANTES de escribir.
- Extrae, no abstraigas: nada de capas genéricas "por si acaso" — solo separar
  lo que ya existe.

Al terminar: confirma que cada archivo resultante cumple §04, que ningún componente
llama a la capa de red directo, y declara desviaciones RECOMMENDED.
```

## 7. Code review de un diff contra el handbook

**Cuándo usarlo:** revisar un PR o diff generado por otra persona/IA.

```
Revisa este diff contra el Engineering Handbook siguiendo el protocolo de
13_AI_Rules/AI_WORKFLOW.md §7.

Diff / PR: {diff_o_ruta_o_URL_del_PR}

Pasos obligatorios:
1. Clasifica el diff: qué dominios toca y qué documentos aplican (AI_WORKFLOW.md §1).
2. Lee los checklists de esos documentos y recorre el diff ítem por ítem.
3. Reporta SOLO observaciones con cita exacta, en este formato:
   [REQUIRED|RECOMMENDED] {documento}.md §{sección}: {regla} — {qué línea la viola}
4. Lo que "se ve mal" pero no tiene regla va aparte, bajo "Sugerencias sin regla".
5. Veredicto binario al final: "Cumple el handbook" o
   "No cumple: N violaciones REQUIRED" con la lista.

Prohibido: opiniones de estilo sin cita, y aprobar con violaciones REQUIRED abiertas.
```

## 8. Auditoría de accesibilidad de una página

**Cuándo usarlo:** verificar una página existente antes de release o tras un rediseño.

```
Audita la accesibilidad de {ruta_o_URL_de_la_página} contra el handbook.

Lee primero:
1. 01_Frontend/FRONTEND_ACCESSIBILITY_STANDARD.md (documento completo)
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md §13
3. 01_Frontend/FRONTEND_HTML_STRUCTURE_STANDARD.md (semántica y landmarks)
4. 01_Frontend/FRONTEND_COLOR_CONTRAST_STANDARD.md (ratios de contraste)

Auditar como mínimo: jerarquía de headings (un solo h1), landmarks, labels de
formulario asociados, foco visible y orden de tabulación, navegación completa por
teclado, alt de imágenes, contraste AA de texto y controles, targets táctiles.

Formato del reporte:
- Por cada hallazgo: [REQUIRED|RECOMMENDED] + documento §sección + elemento
  afectado + fix concreto propuesto.
- Ordena por severidad: bloqueantes (REQUIRED) primero.
- Cierra con veredicto binario y lista priorizada de fixes.
No arregles nada todavía: primero el reporte, los fixes se aprueban aparte.
```

## 9. Auditoría de performance

**Cuándo usarlo:** una página se siente lenta o antes de un release importante.

```
Audita la performance de {ruta_o_URL} contra el handbook.

Lee primero:
1. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md §11 (Performance) — los objetivos
   reales son Core Web Vitals (LCP, INP, CLS); los números concretos son heurísticas.
2. 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md §1.7 (imágenes: dimensiones,
   formato moderno, lazy loading salvo el LCP)
3. 06_Testing/README.md → documento 06 (Lighthouse CI y presupuestos), si existe
   configuración de presupuestos en el proyecto

Auditar como mínimo: peso y formato de imágenes, elemento LCP y su carga,
layout shifts (dimensiones explícitas), JS bloqueante y tamaño de bundle,
fuentes (carga y fallback), requests en cascada evitables.

Formato del reporte: hallazgo → métrica de Core Web Vitals que afecta → regla
citada → fix propuesto con impacto estimado. Prioriza por impacto en el usuario,
no por facilidad del fix. Veredicto binario contra los objetivos de §11.
```

## 10. Generar tests de una feature

**Cuándo usarlo:** una feature nueva o existente sin cobertura.

```
Genera los tests de la feature {nombre_feature} ({rutas_de_archivos_implicados}).

Lee primero:
1. 06_Testing/01_QA_STRATEGY.md — §5 decide QUÉ tests merece esta feature
   (no todo merece E2E; hay cosas que explícitamente NO se testean) y §4 las
   herramientas elegidas.
2. 06_Testing/06_TEST_CHECKLIST.md
3. La sección de Testing del dominio tocado: 01_Frontend/FRONTEND_ENGINEERING_STANDARD.md
   §14 o 02_Backend/BACKEND_ENGINEERING_STANDARD.md §14.

Método:
- Declara primero el plan: qué se testea a nivel unitario, qué a integración,
  qué (si algo) a E2E, y qué NO se testea — citando la estrategia.
- Cada test atrapa una clase concreta de error; si no puedes decir cuál, no lo
  escribas ("un test que no puede fallar no es un test", 06_Testing/README.md).
- Si la feature nació de un bug: el test de regresión que lo habría atrapado es
  obligatorio (05_BUG_LIFECYCLE.md).

Al terminar: corre la suite, confirma que pasa, y muestra el mapeo
test → clase de error que atrapa.
```

## 11. Adoptar el handbook en un proyecto existente (gap analysis)

**Cuándo usarlo:** un proyecto que nació sin el handbook y quiere converger a él.

```
Haz un gap analysis del proyecto en {ruta_del_proyecto} contra el Engineering
Handbook. NO modifiques código en esta pasada: solo diagnóstico y plan.

Pasos:
1. Lee 13_AI_Rules/AI_WORKFLOW.md y 00_HANDBOOK_FORMAT.md.
2. Detecta qué dominios aplican al proyecto (¿tiene frontend? ¿workers? ¿DB propia?)
   y lee el Nivel 1 de cada uno (01_Frontend, 02_Backend, 03_API, 04_Database,
   05_Security, 06_Testing, 07_DevOps, 08_Cloud según aplique).
3. Recorre el checklist final de cada Nivel 1 aplicable contra el código real.
4. Produce una tabla: regla ([REQUIRED|RECOMMENDED] + documento §sección) →
   estado (cumple / no cumple / parcial) → evidencia (archivo:línea) →
   esfuerzo estimado del fix (S/M/L).
5. Propón un plan de adopción en 3 olas: (1) REQUIRED de seguridad y datos
   (05_Security, RLS, secretos), (2) resto de REQUIRED, (3) RECOMMENDED de alto
   impacto. Nada de reescrituras big-bang.

Cierra con: % de cumplimiento por dominio y los 5 gaps más riesgosos.
```

---

## Guía de adaptación por modelo

La biblioteca asume una IA que puede **navegar archivos**. No todas pueden — adapta así:

**Agentes con acceso al filesystem (Claude Code, Cursor, aider y similares).** Las referencias por ruta bastan: el prompt se copia tal cual y el agente lee los documentos él mismo. Refuerzo útil: exigir en el prompt que el agente cite qué documentos leyó efectivamente antes de escribir código — leer es un paso verificable, no un acto de fe.

**Modelos por API / chat sin filesystem (GPT, Gemini, Claude vía web).** No pueden abrir rutas: pega el **contenido completo** de los documentos listados en el prompt, en el mismo orden, antes del prompt. Para no exceder contexto, prioriza: `00_HANDBOOK_FORMAT.md` + el Nivel 1 del dominio + solo los Nivel 2 que la tarea toca (la tabla de `AI_WORKFLOW.md` §1.1 es la lista exacta).

**Modelos pequeños / locales (7B–14B).** Además de pegar los documentos completos: un solo dominio por prompt (no mezclar frontend + DB en una pasada), recorta cada documento a las secciones citadas en el prompt, y convierte el paso "declara desviaciones" en una plantilla literal a rellenar — los modelos pequeños siguen plantillas mejor que instrucciones abstractas. Si el contexto no alcanza ni recortando, divide la tarea con los prompts más chicos (1, 5, 10) en vez de los de página completa.

**Pipelines RAG.** Indexa por sección (los encabezados `##` numerados son la unidad natural de chunk), conserva en cada chunk el nombre del documento y la etiqueta `[REQUIRED]/[RECOMMENDED]`, e incluye siempre `00_HANDBOOK_FORMAT.md` §1 y §4 como contexto fijo — sin la semántica de las etiquetas y la herencia entre niveles, los chunks recuperados pierden su fuerza normativa.
