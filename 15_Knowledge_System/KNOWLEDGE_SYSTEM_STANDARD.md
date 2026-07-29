---
title: "Knowledge System Standard"
category: knowledge
tags:
  - knowledge-management
  - rag
  - indexing
  - conventions
  - standards
summary: "Define cómo el handbook funciona como base de conocimiento consultable: schema de frontmatter, tamaño de documentos, links, READMEs por carpeta, INDEX.json generado y proceso de mantenimiento."
keywords:
  - frontmatter
  - metadata
  - yaml
  - obsidian
  - retrieval
  - base de conocimiento
  - tags
  - vocabulario controlado
  - embeddings
updated: 2026-07-20
status: current
---

# KNOWLEDGE SYSTEM STANDARD

> Nivel 1 del handbook para el dominio Knowledge System. Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../00_HANDBOOK_FORMAT.md) — cada regla es `[REQUIRED]` o `[RECOMMENDED]` y lleva su "Por qué".
>
> **Qué regula este documento:** cómo el handbook funciona como **base de conocimiento consultable** — por Obsidian, por una IA (RAG por keywords sobre `INDEX.json`), o por un humano con búsqueda de texto. **Qué NO regula:** el contenido de los estándares (eso lo regula cada dominio) ni cómo se escriben las reglas (eso es `00_HANDBOOK_FORMAT.md`).
>
> Principio de diseño: **el sistema más simple que responde las queries reales.** Cada campo de metadata existe porque una query lo usa; cada proceso existe porque un problema ya ocurrió o es inevitable. Nada se agrega "por si acaso".

---

## 01. Frontmatter — schema obligatorio

**[REQUIRED]** Todo documento de contenido del handbook lleva un bloque YAML al inicio con **exactamente estos campos** — ni más, ni menos:

```yaml
---
title: "Título legible del documento"
category: frontend          # dominio — un solo valor de la lista cerrada
tags:                       # 3-8, kebab-case, del vocabulario de la sección 02
  - design-tokens
  - accessibility
summary: "1-2 frases. Es lo que el buscador muestra como resultado."
keywords:                   # términos de búsqueda que NO están en el título
  - wcag
  - lector de pantalla
updated: 2026-07-20         # YYYY-MM-DD — última revisión de contenido
status: current             # current | needs-review | deprecated
---
```

**Por qué solo estos campos:** cada uno responde una query concreta:

| Campo | Query que lo usa |
|---|---|
| `title` | "¿cómo se llama este doc?" — resultado de búsqueda, título en Obsidian |
| `category` | "dame todos los docs de seguridad" — filtro por dominio |
| `tags` | "¿qué docs tocan accesibilidad?" — filtro transversal entre dominios |
| `summary` | "¿me sirve este resultado sin abrirlo?" — snippet del buscador |
| `keywords` | "busqué 'RLS' y el título dice 'Database Standard'" — recall de búsqueda |
| `updated` | "¿esto sigue vigente?" — orden por frescura, disparador de needs-review |
| `status` | "¿puedo confiar en esto?" — excluir deprecated del retrieval |

Campos como `author`, `version`, `created`, `aliases` o `priority` **no se agregan**: ninguna query los usa hoy, y cada campo extra es mantenimiento que se desactualiza en silencio. Si mañana una query real necesita un campo nuevo, se agrega aquí primero y después a los documentos.

**Reglas por campo:**

- **[REQUIRED]** `category` es **un solo valor** de esta lista cerrada (coincide con las carpetas del handbook): `frontend`, `backend`, `api`, `database`, `security`, `testing`, `devops`, `cloud`, `architecture`, `ai-rules`, `dx`, `knowledge`. Un doc que parece necesitar dos categorías está mal partido (ver sección 03) o la segunda categoría en realidad es un tag.
- **[REQUIRED]** `tags`: entre 3 y 8, en `kebab-case`, tomados del vocabulario controlado (sección 02). Menos de 3 = el doc es ininfiltrable transversalmente; más de 8 = los tags dejan de discriminar.
- **[REQUIRED]** `summary`: 1-2 frases, en español, autocontenidas (no "este documento define..." repetido del título — decir *qué* define). Es el texto que un buscador o una IA muestra para decidir si abre el doc.
- **[REQUIRED]** `keywords`: solo términos que un buscador usaría y que **no aparecen en el título** (sinónimos, siglas, términos en el otro idioma, nombres de herramientas). No duplicar tags ni palabras del título — eso es ruido sin recall extra.
- **[REQUIRED]** `updated`: fecha de la última revisión de **contenido** (no de metadata). Formato `YYYY-MM-DD`.
- **[REQUIRED]** `status`: `current` (confiable), `needs-review` (usable pero verificar antes de citar números/comandos), `deprecated` (no usar; el frontmatter o el encabezado dice qué lo reemplaza).

**[REQUIRED]** El frontmatter se **inserta** sin modificar el contenido existente del documento. Agregar metadata nunca es excusa para "aprovechar y retocar" el texto — son cambios separados con diffs separados.

**Excepciones:** los `README.md` de carpeta y `INDEX.json` no llevan frontmatter (son infraestructura de navegación, no contenido consultable).

## 02. Vocabulario de tags — lista controlada

**[REQUIRED]** Los tags salen de esta lista. Para agregar un tag nuevo: se agrega **aquí primero** (con un commit que lo justifique — típicamente: 2+ docs lo van a usar), después a los docs. Un tag que solo usaría un documento no se crea — para eso está `keywords`.

**Por qué:** los tags solo sirven si son consistentes. Sin lista controlada aparecen `auth`, `authentication` y `autenticacion` como tres tags distintos, y el filtro transversal muere.

Vocabulario inicial (~44 tags):

**Transversales:** `standards` · `patterns` · `conventions` · `checklists` · `error-handling` · `validation` · `performance` · `naming`

**Frontend/UI:** `design-tokens` · `components` · `accessibility` · `responsive` · `dark-mode` · `color-contrast` · `typography` · `motion` · `icons` · `microcopy` · `html-semantics` · `seo` · `react` · `typescript` · `forms` · `tables` · `dashboards` · `navigation` · `modals` · `notifications` · `ui-states` · `landing-pages` · `auth`

**Backend/API/DB:** `rest-api` · `workers` · `postgres` · `supabase` · `rls` · `migrations`

**Seguridad:** `secrets` · `threat-model` · `incident-response`

**DevOps/Cloud:** `git` · `github` · `ci-cd` · `deploy` · `rollback` · `cloudflare` · `storage` · `limits-costs`

**Knowledge:** `knowledge-management` · `rag` · `indexing`

## 03. Tamaño y alcance de un documento

**[REQUIRED]** Un documento = **un tema**. Objetivo: **1.500-3.000 palabras**. Si un documento supera sostenidamente las ~3.000 palabras (o al escribirlo ya se ve que las va a superar), se divide por subtema — el documento original queda como el de alcance más general y linkea a los derivados.

**Por qué:** el tamaño no es estética, es la unidad de retrieval. Un doc de 8.000 palabras que "toca todo el frontend" hace que cualquier query de frontend lo devuelva entero — y una IA que recibe 8.000 palabras para responder una pregunta de 200 usa mal su contexto. Un doc de 300 palabras, al revés, fragmenta un tema en 10 resultados parciales. 1.500-3.000 palabras ≈ un tema tratado con profundidad que cabe completo en el contexto de una consulta.

**Matiz:** los documentos Nivel 1 de dominio (ej. `FRONTEND_ENGINEERING_STANDARD.md`, ~5.000+ palabras) exceden el objetivo por diseño — son el índice maestro de su dominio. Se aceptan como excepción documentada, pero **no crecen más**: toda profundización nueva va a un documento Nivel 2 (eso es exactamente lo que el dominio Frontend ya hace con sus 27 documentos Nivel 2).

## 04. Links entre documentos

**[REQUIRED]** El formato de link entre documentos es **markdown relativo estándar**: `[texto](../02_Backend/BACKEND_ENGINEERING_STANDARD.md)`. Es el único formato que funciona a la vez en Obsidian, GitHub, editores de código y un pipeline RAG que resuelva rutas.

**[RECOMMENDED]** Wiki links `[[...]]` solo como **complemento** (ej. en notas personales de Obsidian que vivan fuera de los estándares), nunca como único link a un documento. Un `[[FRONTEND_MOTION_STANDARD]]` es un link roto en GitHub y una string opaca para un script.

**Por qué:** el handbook tiene tres consumidores (Obsidian, GitHub/editor, RAG) y solo el markdown relativo funciona en los tres. Elegir el formato portable como base cuesta cero y evita una migración futura.

**[REQUIRED]** Al mover o renombrar un documento, actualizar los links entrantes en la misma sesión (buscar el nombre del archivo en todo el repo antes de dar por terminado el cambio).

## 05. README por carpeta

**[REQUIRED]** Toda carpeta de dominio con contenido tiene un `README.md` corto (10-20 líneas) con: (a) **qué contiene** — lista de documentos con una línea por cada uno; (b) **relacionados en otras carpetas** — los 2-4 documentos de otros dominios que más se consultan junto a estos, con el porqué de la relación.

**Por qué:** el README es el mapa local — le ahorra al lector (humano o IA) abrir 5 documentos para saber cuál necesita. La sección de relacionados existe porque las fronteras entre dominios (Backend↔API, Security↔DevOps, Frontend↔Testing) son donde más se pierde tiempo buscando "dónde vive esta regla".

**[REQUIRED]** El README se actualiza en el mismo commit que agrega/elimina un documento de la carpeta. Un README que lista documentos que ya no existen es peor que no tener README.

## 06. INDEX.json — solo generado, nunca a mano

**[REQUIRED]** `INDEX.json` (raíz del handbook) es el índice machine-readable de todo el corpus: una entrada por documento con `title`, `path`, `category`, `tags`, `summary`, `keywords`, `tokens`, `status`, `updated`, `has_frontmatter`. Lo genera **exclusivamente** `tools/build-index.mjs` (`node tools/build-index.mjs`). Editarlo a mano está prohibido — cualquier edición manual se pierde en la próxima regeneración, y un índice medio-manual es un índice en el que no se puede confiar.

**Por qué existe:** es la capa de retrieval actual. Una IA que necesita contexto no escanea 100+ archivos: lee `INDEX.json` (barato), filtra por `category`/`tags`/`keywords`, y abre solo los 2-3 documentos relevantes. El campo `tokens` le permite además presupuestar cuánto contexto va a consumir antes de abrir nada.

**[REQUIRED]** Regenerar el índice después de: crear/eliminar/mover un documento, o cambiar frontmatter. El resumen que imprime el script (`docs sin frontmatter`) es además la lista de trabajo pendiente de metadata.

## 07. Mantenimiento

**Paso a `needs-review` — [REQUIRED]** un documento pasa a `status: needs-review` cuando ocurre cualquiera de:
- Contiene números/límites/precios verificados en fecha (patrón "verificado 2026-07-20", como en `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md`) y esa fecha de verificación tiene **más de 12 meses**. La fecha de verificación del contenido manda; `updated` solo la refleja.
- Cambió el stack de referencia declarado en el README raíz y el documento depende de la pieza cambiada (ej. se abandona Supabase → todo doc con tag `supabase` pasa a revisión).
- Al usarlo en un proyecto real se detecta una regla que ya no aplica — el que lo detecta cambia el status en el momento, aunque no tenga tiempo de corregir el contenido. `needs-review` honesto vale más que `current` falso.

**Duplicados — [RECOMMENDED]** revisión trimestral: dos documentos con 3+ tags idénticos y `summary` que se solapa son candidatos a fusión (o a redefinir su frontera y declararla en ambos, como hacen `FRONTEND_HTML_STRUCTURE_STANDARD.md` y `FRONTEND_ACCESSIBILITY_STANDARD.md`). La comparación se hace sobre `INDEX.json`, no releyendo el corpus.

**Links rotos — [REQUIRED]** antes de dar por cerrada una sesión que movió/renombró archivos, verificar links (búsqueda del nombre viejo en el repo). Un link roto en un estándar es un dead-end exactamente en el momento en que alguien necesitaba la referencia.

**Deprecación — [REQUIRED]** un documento nunca se borra directamente: pasa a `status: deprecated` indicando qué lo reemplaza, vive así al menos un ciclo de uso real, y recién entonces se elimina (actualizando links entrantes y regenerando el índice).

## 08. Embeddings / vector DB — explícitamente diferido

**[REQUIRED]** Hoy el retrieval es **por keywords sobre `INDEX.json`** (category + tags + keywords + summary). **No** se adopta base vectorial/embeddings todavía, y no se acepta "mejorarlo" agregando esa infraestructura sin que se cumpla el disparador.

**Disparador para adoptarlo (cualquiera de los dos):**
1. El corpus supera **~300 documentos** — a esa escala el vocabulario controlado de tags deja de discriminar (cada tag devuelve 20+ docs).
2. El retrieval por keywords **falla de forma medida**: se registran las queries que no encontraron el documento correcto (aunque existía), y en un mes hay 5+ casos donde la causa es semántica (la query usaba términos que ningún campo contenía) y no metadata mal cargada — porque si es metadata mal cargada, lo barato es arreglar la metadata.

**Por qué diferirlo:** con ~100 documentos bien etiquetados, keywords + un vocabulario controlado resuelven el retrieval con costo de mantenimiento casi cero. Un pipeline de embeddings agrega: re-indexado en cada edición, un servicio externo o local que mantener, y resultados no explicables cuando falla. Se paga ese costo cuando el problema exista y esté medido — no antes. Cuando se adopte, `INDEX.json` no desaparece: sigue siendo la fuente de metadata y el fallback.

---

## Checklist verificable

- [ ] Todo doc de contenido tiene frontmatter con los 7 campos exactos (ni más ni menos) — sección 01
- [ ] `category` es un valor único de la lista cerrada — sección 01
- [ ] Tags: 3-8, kebab-case, todos existen en el vocabulario de la sección 02
- [ ] `keywords` no repite palabras del título ni tags — sección 01
- [ ] Ningún doc nuevo supera ~3.000 palabras sin dividirse — sección 03
- [ ] Links entre docs en markdown relativo (wiki links solo como complemento) — sección 04
- [ ] Cada carpeta con contenido tiene README (qué contiene + relacionados) actualizado — sección 05
- [ ] `INDEX.json` regenerado tras cualquier cambio de docs/metadata; nunca editado a mano — sección 06
- [ ] Docs con verificaciones fechadas >12 meses están en `needs-review` — sección 07
- [ ] No hay infraestructura de embeddings sin disparador cumplido y medido — sección 08
