---
title: "AI WORKFLOW — Protocolo de razonamiento antes de escribir código"
category: 13_AI_Rules
tags:
  - conventions
  - standards
  - checklists
  - error-handling
summary: "Protocolo obligatorio para toda IA que genere o revise código: clasificar tarea, leer el estándar aplicable en orden, verificar contra el checklist y reportar desviaciones. Define la jerarquía de conflicto entre documentos y los anti-comportamientos de IA."
keywords:
  - workflow
  - reasoning
  - anti-patterns
  - code-generation
  - review
  - classification
updated: 2026-07-26
status: current
---

# AI WORKFLOW — Protocolo de razonamiento antes de escribir código

> Nivel 1 del dominio `13_AI_Rules`. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md). Documentos de Nivel 2 que dependen de este: [AI_PROMPTS_LIBRARY.md](AI_PROMPTS_LIBRARY.md).
>
> Este documento es el meta-nivel del handbook: define **cómo cualquier IA (Claude, GPT, Gemini, modelo local, pipeline RAG) debe usar los demás dominios** antes de generar una sola línea de código. Todas las reglas de este documento son `[REQUIRED]` — una IA que escribe código sin seguir este protocolo está improvisando, y la improvisación es exactamente lo que el handbook existe para eliminar.
>
> Nota de estado: el mapa vivo de qué documentos existen está en el [README.md](../README.md) raíz, pero puede quedar desactualizado respecto al disco. Ante la duda, **listar la carpeta del dominio es la fuente de verdad**, no el README.

---

## 1. Clasificar la tarea antes de escribir código

**[REQUIRED]** Antes de generar código, la IA declara explícitamente: (a) qué dominio(s) del handbook toca la tarea, (b) qué documentos va a consultar y en qué orden. Si la tarea toca 2+ dominios (casi siempre: una "página de login" es frontend + API + seguridad), se listan todos — no solo el más obvio.

**Por qué:** el error típico de una IA no es romper una regla que leyó, sino no leer el documento que la contenía. Clasificar primero convierte "se me olvidó la accesibilidad" en un fallo imposible: si la tarea es frontend, el documento de accesibilidad está en la lista antes de empezar.

### 1.1 Tabla de clasificación — tareas comunes

| Tarea | Documentos a consultar, en orden |
|---|---|
| Página de login / registro / recuperación | `01_Frontend/FRONTEND_AUTH_PATTERNS.md` → `01_Frontend/FRONTEND_FORMS_PATTERNS.md` (anatomía de campo, validación, errores de servidor) → `FRONTEND_ACCESSIBILITY_STANDARD.md` → `03_API/API_ENGINEERING_STANDARD.md` §10 (Auth) → `05_Security/SECURITY_ENGINEERING_STANDARD.md` §04 (Auth y sesiones) |
| Landing page | `01_Frontend/FRONTEND_LANDING_PATTERNS.md` → `FRONTEND_UI_STYLE_CATALOG.md` (elegir estilo) → `FRONTEND_RESPONSIVE_STANDARD.md` → `FRONTEND_COLOR_CONTRAST_STANDARD.md` → `FRONTEND_ENGINEERING_STANDARD.md` §11 (Performance) |
| Dashboard / panel de analítica | `01_Frontend/FRONTEND_DASHBOARD_PATTERNS.md` → `FRONTEND_ANALYTICS_CHARTS_STANDARD.md` → `FRONTEND_TABLE_PATTERNS.md` → `FRONTEND_SIDEBAR_PATTERNS.md` / `FRONTEND_NAVIGATION_PATTERNS.md` |
| Módulo CRUD completo (lista + crear/editar + borrar) | `01_Frontend/FRONTEND_CRUD_PATTERNS.md` → `FRONTEND_TABLE_PATTERNS.md` → `FRONTEND_MODALS_PATTERNS.md` → `FRONTEND_STATES_PATTERNS.md` → `03_API/API_ENGINEERING_STANDARD.md` → `04_Database/DATABASE_ENGINEERING_STANDARD.md` |
| Crear una tabla nueva en DB | `04_Database/DATABASE_ENGINEERING_STANDARD.md` §01–05 (naming, tipos, columnas estándar, constraints) → §07 (RLS) → §08 (Migraciones) → `05_Security/SECURITY_ENGINEERING_STANDARD.md` §05 (RLS como fuente de verdad) |
| Nuevo endpoint | `03_API/API_ENGINEERING_STANDARD.md` (rutas, métodos, códigos, formato de respuesta) → `02_Backend/BACKEND_ENGINEERING_STANDARD.md` §02 (capas) y §04–05 (auth, validación) → `05_Security/SECURITY_ENGINEERING_STANDARD.md` §07–08 (rate limiting, validación de entrada) |
| Nuevo worker (servicio backend) | `02_Backend/BACKEND_ENGINEERING_STANDARD.md` §07 (multi-worker) y todo el documento → `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` → `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` |
| Webhook (recibir o emitir) | `02_Backend/BACKEND_ENGINEERING_STANDARD.md` §12 → `05_Security/SECURITY_ENGINEERING_STANDARD.md` §09 (seguridad de webhooks) → `03_API/API_ENGINEERING_STANDARD.md` §11 (idempotencia) |
| Escribir tests de una feature | `06_Testing/01_QA_STRATEGY.md` §5 (qué tests escribir) → `06_Testing/06_TEST_CHECKLIST.md` → sección de Testing del dominio tocado (`01_Frontend` §14 o `02_Backend` §14) |
| Deploy / pipeline CI | `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` → `06_Testing/03_CI_CD.md` → `07_DevOps/GITHUB_STANDARD.md` |
| Fix de bug (producción o no) | `06_Testing/05_BUG_LIFECYCLE.md` (severidad, regla de oro del test de regresión) → si es de seguridad: `05_Security/INCIDENT_RESPONSE.md` |
| Refactor de un componente/módulo existente | `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` §02 (arquitectura) y §04 (Component Rules) — o el equivalente del dominio — sin cambiar comportamiento observable |

Si la tarea no está en la tabla, se clasifica por analogía (¿a qué fila se parece más?) y se declara la analogía usada. Si no se parece a ninguna, aplicar la sección 5.

### 1.2 Formato de la declaración de clasificación

**[REQUIRED]** La declaración es breve y precede al código en la misma respuesta:

```
CLASIFICACIÓN
Tarea: página de configuración de perfil con cambio de contraseña
Dominios: 01_Frontend, 03_API, 05_Security
Documentos, en orden:
  1. FRONTEND_ENGINEERING_STANDARD.md §09, §13
  2. FRONTEND_AUTH_PATTERNS.md (secciones de cambio de contraseña)
  3. API_ENGINEERING_STANDARD.md §10
  4. SECURITY_ENGINEERING_STANDARD.md §04
No cubierto por la tabla: "página de settings" — clasifico por analogía
con la fila de login (formularios + auth). Settings Patterns está pendiente
en 01_Frontend; aplico sección 5 de este documento para esa parte.
```

**Por qué el formato es fijo:** una declaración con estructura constante se puede verificar de un vistazo (¿están todos los dominios?, ¿falta seguridad?) y los modelos pequeños la producen de forma fiable si es una plantilla, no una instrucción abstracta.

---

## 2. Orden de lectura

**[REQUIRED]** El orden es siempre el mismo y no se salta ningún paso:

1. **Formato** — `00_HANDBOOK_FORMAT.md`, una sola vez por sesión/proyecto. Sin esto, la IA no sabe qué significa `[REQUIRED]` ni cómo funciona la herencia entre niveles.
2. **Nivel 1 del dominio** — el `*_ENGINEERING_STANDARD.md` de cada dominio clasificado en la sección 1. Aplica siempre, a todo el dominio.
3. **Nivel 2 aplicable** — solo los documentos de patrón que la tabla de clasificación señala para esta tarea. No se leen los 20+ documentos de patrón "por si acaso": se leen los que la tarea toca.
4. **Nivel 3 si existe** — estándar de vertical del rubro del proyecto (hoy no existe ninguno; ver `00_HANDBOOK_FORMAT.md` §4).
5. **Recién entonces, código.**

**Por qué:** el orden replica la herencia. Leer un documento de patrón sin su Nivel 1 produce código que cumple el patrón pero rompe las bases (un login con el layout correcto pero colores hardcodeados). Leer código antes que estándar produce código que después hay que rehacer — más caro que leer primero.

### 2.1 Ejemplo aplicado — "crear una tabla nueva en DB"

```
1. 00_HANDBOOK_FORMAT.md            → ya leído esta sesión, no se repite
2. DATABASE_ENGINEERING_STANDARD.md → Nivel 1: naming (§01), tipos (§02),
                                      columnas estándar (§03), constraints (§05)
3. Secciones específicas aplicables → §07 RLS (la tabla expone datos por
                                      usuario), §08 migraciones
4. SECURITY_ENGINEERING_STANDARD.md → §05: RLS como fuente de verdad de
                                      autorización (dominio cruzado, lo señaló
                                      la tabla de clasificación)
5. Nivel 3                          → no existe vertical aplicable
6. Código                           → migración + política RLS
```

### 2.2 Alcance de lectura

**[RECOMMENDED]** Dentro de un documento de Nivel 1 largo, leer completo la primera vez que se trabaja en el dominio en esa sesión; en tareas siguientes de la misma sesión basta releer las secciones que la tarea toca más el checklist final. **[REQUIRED]** El checklist final se relee siempre — es la parte que se verifica en la sección 4.

**Por qué:** releer 30KB por cada micro-tarea quema contexto sin ganancia; pero el checklist es barato y es lo que convierte la lectura en verificación.

---

## 3. Jerarquía de conflicto

**[REQUIRED]** Cuando dos fuentes dicen cosas distintas, se resuelve en este orden:

1. **REQUIRED gana siempre sobre RECOMMENDED.** Un `[RECOMMENDED]` de cualquier documento nunca justifica romper un `[REQUIRED]` de otro.
2. **A igual etiqueta, el documento más específico gana.** Nivel 3 sobrescribe a Nivel 2, Nivel 2 a Nivel 1 — pero solo cuando el documento específico declara explícitamente que sobrescribe y por qué (regla de herencia de `00_HANDBOOK_FORMAT.md` §4). Si dos documentos del mismo nivel parecen contradecirse, gana el que trata el tema como asunto central sobre el que lo menciona de pasada — y la IA reporta la contradicción como posible bug del handbook.
3. **Si el usuario pide romper un `[REQUIRED]`**, la IA no lo rompe en silencio ni se niega en silencio: señala la regla exacta (documento + sección), explica el "Por qué" de esa regla, y pide confirmación explícita en esa conversación. Solo con la confirmación escrita procede, dejando un comentario en el código que registre la excepción y quién la autorizó.
4. **Desviarse de un `[RECOMMENDED]`** no requiere confirmación, pero sí justificación: un comentario corto en el código o una línea en el reporte final (sección 4). Nunca en silencio.

**Por qué:** la diferencia entre un handbook y una sugerencia es que el conflicto tiene un resultado determinista. Si cada IA resuelve los conflictos a su criterio, dos generaciones de la misma tarea divergen — que es el problema que el handbook existe para evitar.

### 3.1 Ejemplo — el usuario pide romper un REQUIRED

```
Usuario: "borra los registros directo, sin modal de confirmación, es más rápido"

Respuesta correcta de la IA (antes de escribir código):
  "Eso rompe un REQUIRED del handbook: FRONTEND_CRUD_PATTERNS.md §5 —
   ninguna eliminación ocurre con un solo clic sin confirmación que nombre
   el ítem. El motivo de la regla: el modal que nombra el ítem es lo que
   previene borrar el registro equivocado, no el '¿estás seguro?' genérico.
   ¿Confirmas que quieres eliminar sin confirmación de todos modos?"

Solo si el usuario responde que sí, se implementa, con comentario:
  // EXCEPCIÓN a FRONTEND_CRUD_PATTERNS.md §5 autorizada por el usuario
  // en conversación del {fecha}: eliminación sin confirmación.
```

Respuestas incorrectas: implementarlo callado (rompe el handbook en silencio) y negarse callado implementando el modal igual (ignora al usuario en silencio). Ambas destruyen la confianza en direcciones opuestas.

---

## 4. Al terminar — verificación y declaración

**[REQUIRED]** Ningún entregable se declara terminado sin estos dos pasos:

1. **Correr el checklist** del documento aplicable (todos los Nivel 1 terminan en "Checklist rápido"; varios Nivel 2 también). Se recorre ítem por ítem contra el código generado, no de memoria. Si un ítem no aplica, se dice por qué no aplica.
2. **Declarar desviaciones**: lista explícita de qué reglas `[RECOMMENDED]` no se siguieron y la razón de contexto de cada una. Lista vacía también se declara ("sin desviaciones"). Las `[REQUIRED]` no aparecen en esta lista — o se cumplieron, o hubo confirmación explícita del usuario (sección 3.3), sin tercera opción.

**Por qué:** el checklist convierte "creo que está bien" en "verifiqué estos 12 puntos". La declaración de desviaciones hace auditable la generación: quien revisa después no tiene que adivinar si la desviación fue decisión o descuido.

### 4.1 Plantilla del reporte final

```
REPORTE DE CIERRE
Checklist aplicado: FRONTEND_CRUD_PATTERNS.md (final) +
                    FRONTEND_ENGINEERING_STANDARD.md (final)
  [x] Secuencia listado → form → confirmación
  [x] Modal elegido por árbol de decisión §3 (4 campos, sin contexto extra)
  [x] Eliminación nombra el ítem
  [—] Acciones en bulk: no aplica (volumen esperado < 50 registros)
  ... (todos los ítems, ninguno omitido)

Desviaciones RECOMMENDED:
  - FRONTEND_CRUD_PATTERNS.md §4 (Master-Detail): usé página de detalle
    dedicada — el usuario trabaja un registro largo rato, no compara.

Excepciones REQUIRED autorizadas: ninguna.
No cubierto por el handbook: ninguna parte.
```

Un reporte sin la línea de desviaciones (aunque sea "ninguna") está incompleto: el silencio es indistinguible del descuido.

---

## 5. Cuando el handbook no cubre el caso

**[REQUIRED]** Si la tarea (o parte de ella) no tiene documento ni regla aplicable:

1. **Identificar el documento más cercano** por analogía (mismo dominio, patrón más parecido).
2. **Aplicar el "Por qué", no el "qué".** Cada regla del handbook lleva su motivo escrito precisamente para esto: la regla literal puede no cubrir el caso nuevo, pero el principio detrás casi siempre sí. Ejemplo: no existe documento de "chat interface", pero el "Por qué" de `FRONTEND_STATES_PATTERNS.md` (todo estado async se muestra explícitamente) y el de CRUD (confirmación nombrando el ítem antes de acciones destructivas) generalizan directo.
3. **Proponer, no crear.** La IA describe el estándar faltante en su respuesta (nombre de documento sugerido, nivel, 3–5 reglas candidatas con su porqué) para que el dueño del handbook decida crearlo. **Nunca crea el archivo de estándar por iniciativa propia** — el handbook tiene un dueño y un criterio de admisión (un Nivel 3, por ejemplo, requiere 3+ reglas propias acumuladas, ver `00_HANDBOOK_FORMAT.md` §4).
4. **Declararlo en el reporte final**: "esta parte no está cubierta por el handbook; apliqué el principio X de tal documento".

**Por qué:** un handbook que crece por iniciativa de cada IA que pasa se llena de documentos redundantes y contradictorios en semanas. La generalización por el "Por qué" da consistencia sin necesitar un documento por cada caso posible.

### 5.1 Formato de la propuesta de estándar faltante

```
PROPUESTA DE ESTÁNDAR (no creado — requiere aprobación del dueño del handbook)
Nombre sugerido: FRONTEND_CHAT_PATTERNS.md
Nivel: 2 (patrón de 01_Frontend, dependería del Nivel 1)
Hueco detectado en: tarea "interfaz de chat de soporte", 2026-07-20
Reglas candidatas:
  1. [REQUIRED] Mensajes propios y ajenos visualmente distinguibles por
     posición Y color, nunca solo color. Por qué: accesibilidad — el color
     solo falla para daltónicos (mismo principio que COLOR_CONTRAST §…).
  2. [REQUIRED] Estado de envío explícito por mensaje (enviando/enviado/error
     con reintento). Por qué: mismo principio que STATES_PATTERNS.
  3. [RECOMMENDED] Autoscroll solo si el usuario está al fondo. Por qué:
     robar el scroll durante lectura es el equivalente al layout shift.
Mientras tanto apliqué: los principios citados arriba.
```

---

## 6. Anti-comportamientos de IA

**[REQUIRED]** Prohibiciones explícitas — corrigen los sesgos conocidos de los modelos generativos, no errores hipotéticos:

1. **No inventar complejidad no pedida.** Nada de versionado de API, capas de abstracción especulativas ("por si mañana cambiamos de DB"), patrones enterprise, ni librerías extra que la tarea no requiere. El versionado, por ejemplo, tiene su propia regla en `03_API/API_ENGINEERING_STANDARD.md` §07 — se aplica cuando ese documento lo indica, no por reflejo. La abstracción se introduce cuando hay 2+ usos reales, no antes.
2. **No generar div-soup.** HTML semántico según `01_Frontend/FRONTEND_HTML_STRUCTURE_STANDARD.md`: landmarks, jerarquía de headings real (un solo `<h1>`), elementos nativos (`<button>`, `<nav>`, `<table>`) antes que `<div onclick>`.
3. **No hardcodear lo que el design system tokeniza.** Colores, espaciados, tamaños tipográficos y sombras salen de los tokens (`FRONTEND_ENGINEERING_STANDARD.md` §1.1–1.3, `FRONTEND_ELEVATION_STANDARD.md`). Un `#3b82f6` o un `margin: 37px` sueltos en un componente son bugs, aunque "se vean bien".
4. **No usar el patrón por defecto del dataset de entrenamiento.** La card-por-todo está explícitamente prohibida (`FRONTEND_ENGINEERING_STANDARD.md` §1.12): el patrón de UI se elige según el tipo de información, con la tabla de decisión de `FRONTEND_UI_PATTERNS.md`.
5. **No crear archivos de estándar, README ni documentación nueva sin que se pida.** Aplica al handbook (sección 5.3) y a los proyectos: la documentación tiene reglas propias (`01_Frontend` §16, `02_Backend` §15) y se genera cuando esas reglas o el usuario lo piden.
6. **No dar por existente lo que no se verificó.** Antes de referenciar un documento, archivo o sección del handbook, confirmar que existe en disco. Citar un documento inexistente es peor que declarar el hueco (sección 5).
7. **No rellenar la UI con datos mock/placeholder cuando el contenido debe venir de una fuente real.** Nada de arrays de ejemplo hardcodeados (testimonios, productos, filas de tabla), texto *lorem*, ni slots "pendiente de activar" que sobrevivan a producción. Todo contenido dinámico sale de su fuente real (DB/API); si aún no existen datos, se **siembra seed real** en la base —usando el mismo hashing/validación del backend para que el registro sea usable de verdad—, no se simula con constantes en el código. Un bloque que todavía no puede tener datos reales (ej. anuncios sin publisher ID) se **oculta**, no se muestra con texto de relleno. El mock data se filtra a producción, da sensación de maqueta y esconde que la integración con la fuente real nunca se hizo.
8. **No dejar estados terminales que no cumplen lo que prometen.** Un estado que anuncia una acción — "Redirigiendo…", "Guardando…", "Enviando…" — debe ejecutarla (navegar, persistir, enviar): no puede quedarse fijo en pantalla. Todo estado `loading`/`success` visible tiene su transición de salida cableada (`FRONTEND_ENGINEERING_STANDARD.md` §9.3 estados, `FRONTEND_AUTH_PATTERNS.md` §8/§11). El modelo tiende a "pintar" el estado feliz sin conectar la consecuencia, dejando flujos que parecen andar pero se cuelgan.
9. **No pegar elementos al borde ni fundir bloques del mismo color.** El contenido y los rieles/elementos fijos dejan un gutter contra el borde de la ventana (no lo tocan); las secciones mantienen la separación vertical del estándar; dos superficies oscuras adyacentes (ej. una sección y el footer, ambos del mismo navy) no se funden —se separan con espacio o un cambio de superficie— y la última sección antes del footer lleva separación inferior (`FRONTEND_LANDING_PATTERNS.md` escala de padding por sección, `FRONTEND_ELEVATION_STANDARD.md`, `FRONTEND_RESPONSIVE_STANDARD.md`). El modelo tiende a apilar secciones sin colchón y a no percibir que dos bloques del mismo color se leen como uno solo.
10. **No poner autoridad de validación ni lógica de negocio en el frontend.** El frontend no accede a la base de datos ni ejecuta reglas de negocio; su validación (zod/react-hook-form) es **solo UX**. El **Worker re-valida toda entrada**, aplica toda regla de negocio y es el único con acceso a datos (D1/R2/KV) — `02_Backend/BACKEND_ENGINEERING_STANDARD.md` §00/§05, `01_Frontend/FRONTEND_ENGINEERING_STANDARD.md` §6.6. Un chequeo que solo vive en el cliente no existe para quien llama la API directo (`fetch` a mano, DevTools). El modelo tiende a "validar en el form" y dar por hecho que el backend no necesita re-validar.

**Por qué:** estos no son errores aleatorios sino sesgos sistemáticos — los modelos sobregeneran estructura, abstracción y "completitud" porque eso abunda en sus datos de entrenamiento. Nombrarlos como prohibiciones explícitas es más efectivo que esperar que el contexto los suprima.

---

## 7. Protocolo de code review por IA

**[REQUIRED]** Cuando la tarea es revisar código (un diff, un PR, un archivo) contra el handbook:

1. **Clasificar el diff** igual que en la sección 1: qué dominios toca, qué documentos aplican.
2. **Revisar contra los checklists** de esos documentos, ítem por ítem sobre las líneas del diff — no impresiones generales sobre "calidad".
3. **Toda observación cita la regla exacta**: documento + sección + etiqueta. Formato: `[REQUIRED] FRONTEND_AUTH_PATTERNS.md §3: máximo un CTA primario por pantalla — este login tiene dos botones primarios`. Sin cita, la observación no se emite.
4. **No opinar sin regla.** Si algo "se ve mal" pero ningún documento lo cubre, se marca como **sugerencia sin regla**, separada de las violaciones, y opcionalmente se propone el estándar faltante (sección 5.3). Nunca se mezcla gusto personal con incumplimiento del handbook.
5. **Severidad por etiqueta**: violación de `[REQUIRED]` = bloqueante (el código no está terminado, por definición de `00_HANDBOOK_FORMAT.md` §1); desviación de `[RECOMMENDED]` sin justificación escrita = observación no bloqueante que pide la justificación; desviación con justificación = se verifica que la razón sea de contexto real y se deja pasar.
6. **El veredicto final es binario**: "cumple el handbook" o "no cumple: N violaciones REQUIRED listadas". Nada de "en general se ve bien".

**Por qué:** una review sin citas es una opinión con formato de autoridad — genera discusiones de gusto en vez de correcciones verificables. La cita exacta hace la review reproducible: otra IA (u otro humano) llega a la misma conclusión leyendo la misma regla.

### 7.1 Ejemplo de salida de review

```
REVIEW — diff: feature/user-invites (dominios: 01_Frontend, 03_API)

Violaciones REQUIRED (bloqueantes):
1. [REQUIRED] FRONTEND_AUTH_PATTERNS.md §3: máximo un CTA primario por
   pantalla — InviteForm.tsx:41 renderiza "Enviar" y "Enviar y crear otro"
   ambos como variant="primary".
2. [REQUIRED] API_ENGINEERING_STANDARD.md §04: formato de respuesta
   estándar — invites.ts:88 devuelve el objeto crudo sin el envelope.

Desviaciones RECOMMENDED sin justificar:
3. [RECOMMENDED] FRONTEND_ENGINEERING_STANDARD.md §1.7: imagen de avatar
   sin lazy loading — falta el comentario justificando o el atributo.

Sugerencias sin regla (no bloqueantes, sin cita porque no la hay):
- El nombre `doInviteStuff()` es vago; el handbook no regula naming de
  funciones a este nivel. Candidato a propuesta de estándar: no.

VEREDICTO: No cumple — 2 violaciones REQUIRED.
```

---

## Checklist — antes de dar por terminada cualquier tarea guiada por el handbook

- [ ] Clasifiqué la tarea y declaré dominios + documentos antes de escribir código (§1).
- [ ] Leí en orden: formato → Nivel 1 de cada dominio → Nivel 2 aplicable (§2).
- [ ] Resolví todo conflicto con la jerarquía (REQUIRED > específico > general) y no rompí ningún REQUIRED sin confirmación explícita del usuario (§3).
- [ ] Corrí el checklist del documento aplicable ítem por ítem (§4.1).
- [ ] Declaré las desviaciones de RECOMMENDED con su razón, o declaré "sin desviaciones" (§4.2).
- [ ] Para lo no cubierto: apliqué el "Por qué" del documento más cercano y propuse (no creé) el estándar faltante (§5).
- [ ] Cero anti-comportamientos: sin complejidad especulativa, sin div-soup, sin valores hardcodeados que el sistema tokeniza, sin archivos de estándar no pedidos, sin referencias no verificadas (§6).
- [ ] Si fue review: toda observación con cita documento + sección + etiqueta, veredicto binario (§7).
