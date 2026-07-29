# FRONTEND PERFORMANCE STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, secciones 1.7, 8.2, 11 y 17) y se coordina con [FRONTEND_RESPONSIVE_STANDARD.md](../Core/FRONTEND_RESPONSIVE_STANDARD.md) (sección 6, imágenes responsive). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> **División de responsabilidades con Testing:** los **umbrales verificables** de rendimiento (score de Lighthouse, presupuesto de bundle en KB, mediana de runs) viven en [06_Testing/08_QUALITY_STANDARDS.md](../../06_Testing/Strategy/08_QUALITY_STANDARDS.md) — gates 2.1 (Lighthouse CI), 2.2 (presupuesto de bundle) y 2.3 (variabilidad). Este documento define **cómo se construye una interfaz que pasa esos gates de serie** — no repite sus números; si un número de allá cambia, este documento sigue siendo válido.
>
> **La premisa de todo el documento:** el rendimiento no es una fase de optimización posterior — es un conjunto de decisiones que se toman al escribir el primer componente. Optimizar después cuesta 10x (re-arquitectura de imágenes, deshacer dependencias, partir bundles ya enredados); construir rápido de serie cuesta casi nada porque cada regla de aquí es un default, no un esfuerzo extra.

---

## 1. Core Web Vitals como objetivos de diseño

**[REQUIRED]** Los tres Core Web Vitals — LCP < 2.5s, CLS < 0.1, INP < 200ms — ya son regla del Nivel 1 (`FRONTEND_ENGINEERING_STANDARD.md` §11.4). Lo que este documento agrega: no son métricas que se *miden al final*, son restricciones que se *diseñan al principio*. Cada una tiene una pregunta de diseño asociada que se responde **antes** de escribir la pantalla:

| Métrica | Objetivo | Pregunta de diseño (se responde antes de codear) |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | ¿Cuál es el elemento LCP de esta página y cómo llega lo antes posible? (sección 2) |
| CLS (Cumulative Layout Shift) | < 0.1 | ¿Qué contenido llega tarde (imágenes, datos, fonts) y qué espacio reserva mientras tanto? (sección 3) |
| INP (Interaction to Next Paint) | < 200ms | ¿Qué hace el handler más pesado de esta pantalla y cuánto bloquea el main thread? (sección 4) |

**Por qué diseñar y no solo medir:** un Lighthouse rojo al final del sprint no dice *qué decisión* lo causó — dice que alguna de 30 decisiones acumuladas falló. Responder las tres preguntas por pantalla convierte el gate de CI en una confirmación de lo esperado, no en una investigación forense.

**Por qué estos tres y no otros:** son los umbrales que Google usa para clasificar una página como "buena experiencia" en campo (percentil 75 de usuarios reales) — afectan SEO y conversión directamente, y todo el resto de métricas de laboratorio (FCP, TBT, Speed Index) son diagnósticos intermedios de estas tres, no objetivos en sí mismos.

---

## 2. LCP — el elemento más grande se identifica y se optimiza

### 2.1 Identificar el elemento LCP es parte del diseño de la página

**[REQUIRED]** Toda página con contenido above-the-fold significativo (landing, dashboard, detalle) tiene su elemento LCP **identificado explícitamente** (en la práctica: se sabe cuál es y se trata distinto al resto). Típicamente es la hero image, el headline principal o la imagen destacada del contenido.

**Por qué:** el LCP es una sola cosa por página — optimizar "todas las imágenes por igual" es tratar al elemento crítico con la misma prioridad que a un thumbnail del footer. Las optimizaciones de 2.2 solo aplican a ese elemento; aplicarlas a todo las anula (todo `high` = nada `high`).

### 2.2 El elemento LCP se carga con prioridad máxima, nunca lazy

**[REQUIRED]** Si el elemento LCP es una imagen:

1. **Nunca `loading="lazy"`** — lazy loading en el elemento LCP es la causa #1 de LCP roto: el navegador espera al layout para decidir si la carga, sumando cientos de ms al elemento que define la métrica.
2. **`fetchpriority="high"`** — le dice al navegador que esa imagen compite en prioridad con el CSS, no con el resto de imágenes (que por defecto arrancan en prioridad baja).
3. **`preload` si la imagen no está en el HTML inicial** (ej. se referencia desde CSS como background, o la inserta un componente que monta tarde): `<link rel="preload" as="image" href="..." fetchpriority="high">` en el `<head>`. Si la imagen ya es un `<img>` en el HTML inicial con `fetchpriority="high"`, el preload es redundante — no se duplica.
4. **Nunca como `background-image` de CSS** si se puede evitar: un background se descubre recién cuando el CSS se parsea y el elemento se estila — un `<img>` lo descubre el preload scanner del navegador en el primer barrido del HTML.

**Implementación (hero de landing):**

```html
<!-- El elemento LCP: eager + prioridad alta + dimensiones (sección 3) -->
<img
  src="/img/hero-1280.avif"
  srcset="/img/hero-640.avif 640w, /img/hero-1280.avif 1280w, /img/hero-1920.avif 1920w"
  sizes="100vw"
  width="1280" height="720"
  fetchpriority="high"
  alt="..."
/>
<!-- ❌ jamás en el LCP: loading="lazy" -->
```

**Por qué la asimetría con el resto de imágenes (sección 5.3):** todas las demás imágenes van lazy por defecto; el LCP es la única excepción, y es una excepción *obligatoria*, no opcional.

### 2.3 El texto LCP no espera a nada

**[RECOMMENDED]** Si el elemento LCP es texto (headline de hero sin imagen), su render no debe depender de: fonts bloqueantes (sección 6 lo resuelve con `font-display: swap`), JS que lo monte tarde (el headline crítico va en el HTML/primer render, no detrás de un fetch), ni CSS-in-JS runtime (sección 9). Un headline estático que espera un `useEffect` para renderizar es LCP regalado.

### 2.4 Verificación del LCP en 2 minutos

**[RECOMMENDED]** Confirmar el supuesto, no adivinarlo: en DevTools → Performance, grabar la carga y mirar el marcador **LCP** (identifica el elemento exacto); o en el reporte de Lighthouse, el audit "Largest Contentful Paint element" lo nombra. Si el elemento real no es el que se diseñó como LCP (ej. un banner de cookies resultó más grande que la hero), o la decisión de diseño estaba mal o hay un elemento intruso — ambas cosas se corrigen antes del PR, no después del gate rojo.

---

## 3. CLS — nada se mueve después de pintarse

### 3.1 Dimensiones explícitas en toda imagen y embed

**[REQUIRED]** Toda `<img>`, `<video>`, `<iframe>` y embed de terceros declara sus dimensiones (atributos `width`/`height`, o `aspect-ratio` en CSS cuando el tamaño final es fluido). Ya exigido para imágenes en `FRONTEND_ENGINEERING_STANDARD.md` §1.7 y `FRONTEND_RESPONSIVE_STANDARD.md` §6 — aquí se extiende a **todo elemento que ocupa espacio y llega después del primer render**.

**Por qué:** el navegador no puede reservar el espacio de algo cuyo tamaño no conoce — cuando el recurso llega, empuja todo lo que está debajo. Un solo embed sin dimensiones puede consumir el presupuesto entero de CLS < 0.1.

```html
❌ <iframe src="https://www.youtube.com/embed/..."></iframe>
✅ <iframe src="..." width="560" height="315" style="aspect-ratio: 16/9; width: 100%; height: auto;"></iframe>
```

### 3.2 Skeletons del tamaño real del contenido

**[REQUIRED]** Los estados de carga (skeletons, spinners con contenedor) ocupan **el mismo espacio que el contenido final** — misma altura de card, mismo alto de fila, mismo aspect-ratio de imagen. Un skeleton correcto produce CLS ≈ 0 al llegar los datos; un spinner de 40px que se reemplaza por una tabla de 800px es un layout shift entero disfrazado de buena UX. (Los estados de carga como patrón de UX viven en `FRONTEND_STATES_PATTERNS.md` — esta regla es su cara de performance.)

**Por qué:** el usuario ya empezó a leer/apuntar cuando llegan los datos; si todo salta, el click cae en el lugar equivocado — CLS mide exactamente ese daño.

**Casos que siempre reservan espacio, no solo imágenes:**

- Banners/avisos que aparecen arriba del contenido (cookies, "versión nueva") → se superponen (overlay/fixed) o reservan su espacio desde el primer render; nunca empujan el contenido ya pintado.
- Contenido condicional al usuario (nombre, plan, avatar en el navbar) → el contenedor tiene tamaño estable con y sin dato.
- Ads/embeds de tamaño variable → contenedor con el tamaño de la variante más común, no "lo que venga".

### 3.3 Fonts sin salto de layout: fallback ajustada con `size-adjust`

**[RECOMMENDED]** Además de `font-display: swap` (sección 6), se define una fallback ajustada: un `@font-face` de la fuente del sistema con `size-adjust` (y si hace falta `ascent-override`/`descent-override`) calibrado para que ocupe casi el mismo espacio que la webfont. Así el swap de fallback → webfont no reordena párrafos.

```css
/* Fallback ajustada: Arial ocupando el espacio de Inter */
@font-face {
  font-family: "Inter-fallback";
  src: local("Arial");
  size-adjust: 107%;        /* valor calibrado con herramienta (ej. fontaine, capsize) — no a ojo */
  ascent-override: 90%;
}
body { font-family: Inter, "Inter-fallback", sans-serif; }
```

**Por qué RECOMMENDED y no REQUIRED:** con `swap` + preload de la fuente principal (sección 6) el shift suele ser pequeño; la fallback ajustada es el refinamiento que lo lleva a ~0. Se vuelve prioritaria si el gate de CLS falla por fonts o el sitio es muy pesado en texto.

---

## 4. INP — el main thread no se bloquea

### 4.1 Handlers cortos: la interacción responde primero, el trabajo pesado después

**[REQUIRED]** Ningún handler de interacción (click, input, submit) ejecuta trabajo pesado de forma síncrona antes de que la UI responda. La regla agnóstica: entre la interacción del usuario y el siguiente paint no pueden pasar más de ~200ms (el umbral de INP), lo que en la práctica significa que el handler hace **lo mínimo visible** (actualizar estado, mostrar feedback) y difiere el resto.

Mecánicas concretas, en orden de preferencia:

1. **No hacer el trabajo en el cliente:** filtrar/ordenar/agregar 10.000 filas es trabajo del backend o de un worker — el cliente pagina o virtualiza (sección 11).
2. **Diferir lo no-visible:** el trabajo que no afecta lo que el usuario ve tras la interacción se saca del camino del paint — en React 19, `startTransition` para renders no urgentes; fuera de React, `setTimeout(fn, 0)` / `requestIdleCallback` (o `scheduler.yield()` donde esté disponible — verificar soporte al usarlo).
3. **Partir el trabajo indivisible:** si un cómputo largo es inevitable en el cliente (parseo de un archivo importado, cálculo sobre dataset local), se trocea cediendo el main thread entre trozos, o se mueve a un Web Worker — el main thread se reserva para pintar.
4. **Debounce en inputs que disparan trabajo:** un buscador que filtra en cada keystroke sin debounce ejecuta el trabajo N veces por palabra escrita.

```tsx
// ❌ El filtro pesado corre síncrono en cada keystroke — teclado "pegado"
onChange={(e) => setResults(filterHeavy(allRows, e.target.value))}

// ✅ El input responde ya; el render pesado se marca como no urgente
onChange={(e) => {
  setQuery(e.target.value);                    // urgente: el input refleja la tecla
  startTransition(() => setFilter(e.target.value)); // no urgente: la lista se actualiza después
}}
```

**Por qué:** el main thread es uno solo — mientras ejecuta el handler no puede pintar. INP mide la peor interacción de la sesión, no el promedio: un solo handler de 800ms en el flujo principal arruina la métrica aunque el resto sea instantáneo.

### 4.2 Feedback inmediato aunque el resultado tarde

**[REQUIRED]** Toda interacción cuyo resultado tarda (submit que llama a la API, acción que abre un modal pesado) muestra **algo** en <200ms: estado pressed/disabled del botón, spinner inline, skeleton del modal. El resultado puede tardar 2s legítimos (red); la *respuesta* visual, no.

**Por qué:** INP no mide cuándo termina la operación — mide cuándo el usuario ve que su interacción fue registrada. Un botón que no reacciona hasta que vuelve la API es a la vez INP malo y la causa del doble-click que duplica la operación (coherente con los estados obligatorios de `FRONTEND_ENGINEERING_STANDARD.md` §1.6 y §9.3).

### 4.3 Long tasks de terceros y de inicialización

**[RECOMMENDED]** El JS de inicialización (analytics, SDKs, hidratación de widgets) no compite con la primera interacción: se difiere a después del load o a idle (sección 10 para third-party). Si el profiler (DevTools → Performance) muestra long tasks (>50ms) en la carga, se parten o difieren — una long task durante la carga es un INP arruinado si el usuario interactúa justo en ese momento.

---

## 5. Imágenes — el activo más pesado se trata como tal

### 5.1 Formato moderno con fallback

**[REQUIRED]** Toda imagen de contenido se sirve en formato moderno (AVIF y/o WebP), nunca JPEG/PNG a secas. El mecanismo de fallback depende del pipeline (5.5): si sirve Cloudflare con `format=auto`, la negociación es automática por header `Accept` (no hace falta `<picture>`); si las variantes se generan en build, el fallback es `<picture>`:

```html
<picture>
  <source srcset="/img/card-640.avif 640w, /img/card-1280.avif 1280w" type="image/avif" />
  <source srcset="/img/card-640.webp 640w, /img/card-1280.webp 1280w" type="image/webp" />
  <img src="/img/card-640.jpg" srcset="/img/card-640.jpg 640w, /img/card-1280.jpg 1280w"
       sizes="(max-width: 639px) 100vw, 50vw" width="640" height="480" loading="lazy" alt="..." />
</picture>
```

Excepciones legítimas: SVG para iconografía e ilustración vectorial (`FRONTEND_ICON_SYSTEM_STANDARD.md`); PNG solo donde se necesita sin pérdida exacta (capturas de UI con texto fino) — y aun ahí, WebP lossless suele ganar.

**Por qué:** AVIF pesa típicamente 30–50% menos que JPEG a calidad visual equivalente y WebP ~25–35% menos — en una página donde las imágenes son el 50%+ de los bytes (el caso normal), es la mejora de LCP más barata que existe.

### 5.2 Dimensionadas al tamaño de render, con `srcset`/`sizes`

**[REQUIRED]** Ninguna imagen se sirve a más de ~2x su tamaño de render en el viewport donde se muestra. Un thumbnail que se renderiza a 200px no se sirve desde un archivo de 2000px — se sirve una variante de ~400px (2x para pantallas de alta densidad). Toda imagen de contenido con tamaño de render variable por breakpoint lleva `srcset` con 2–4 anchos + `sizes` que describe el ancho real de render (coherente con `FRONTEND_RESPONSIVE_STANDARD.md` §6).

**[RECOMMENDED]** Los anchos de variante son un **set fijo por proyecto**, no anchos ad-hoc por componente. Referencia práctica alineada a los breakpoints del handbook (`FRONTEND_RESPONSIVE_STANDARD.md` §2):

| Variante | Uso típico |
|---|---|
| 320 / 640 | Thumbnails, cards en mobile |
| 960 / 1280 | Contenido principal, cards en desktop |
| 1920 | Hero full-width en pantallas grandes |

**Por qué el set fijo:** menos variantes = más hits de cache (CDN y navegador) y facturación de transformaciones acotada (5.5-A); y el que escribe el componente elige de una lista corta en vez de inventar un ancho nuevo cada vez. **Por qué la regla del 2x:** servir 2000px para 200px de render es descargar ~25x los bytes necesarios (el peso crece con el área, no con el ancho) — y el navegador además paga decodificar esos píxeles. Es el desperdicio más común y más silencioso: la imagen "se ve bien", nadie nota que pesa 1.4 MB.

### 5.3 Lazy loading por defecto — excepto above-the-fold

**[REQUIRED]** `loading="lazy"` en toda imagen que no está en el viewport inicial. Las imágenes above-the-fold van eager, y el elemento LCP además con `fetchpriority="high"` (sección 2.2 — la excepción obligatoria).

**Por qué:** sin lazy, una landing con 40 imágenes descarga las 40 compitiendo por ancho de banda con el CSS, el JS y la hero — el usuario paga por imágenes que quizá nunca scrollea hasta ver.

### 5.4 Peso objetivo

**[RECOMMENDED]** El objetivo real es el gate de LCP (Lighthouse, `06_Testing/08` gate 2.1), no un número de KB por sí mismo. Como heurística práctica hoy: hero < 200 KB, imagen de contenido < 100 KB, thumbnail < 30 KB — en AVIF/WebP bien dimensionados, superarlos es señal de dimensiones u origen incorrectos, no de que "la foto era pesada". Si el gate pasa con números mayores, el gate manda.

### 5.5 Pipeline concreto: R2 + Cloudflare

**[REQUIRED]** Las imágenes de contenido viven en R2 (regla de plataforma: `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` §04) y las variantes (tamaños/formatos) **las genera una máquina, nunca se exportan a mano**. Dos pipelines válidos — se elige por tipo de imagen y se documenta:

**Opción A — Cloudflare Image Transformations (default para imágenes dinámicas/subidas por usuarios):** se habilitan las transformaciones en la zona y las imágenes se piden vía URL `/cdn-cgi/image/` apuntando al origen en R2 (servido por dominio propio):

```
https://app.example.com/cdn-cgi/image/width=640,quality=80,format=auto/https://media.example.com/uploads/foto.jpg
```

- `format=auto` negocia AVIF/WebP/fallback por header `Accept` — el `<picture>` manual no hace falta; el `srcset` se arma variando `width=` con el set fijo de 5.2.
- Cada combinación única (imagen + parámetros) cuenta como transformación facturable (con free tier mensual y deduplicación en ventana de 30 días — verificar límites vigentes en docs de Cloudflare al configurar): el set fijo de anchos existe también para acotar esto.
- El resultado queda cacheado en el CDN — coherente con la política de cache de `08_Cloud` §08 (asset inmutable → cache largo).
- En el código, la URL no se arma a mano en cada componente: un helper único `imgUrl(key, width)` construye la URL de transformación — un solo lugar si cambia el proveedor o los parámetros.

**Opción B — variantes en build (default para imágenes estáticas del sitio: hero, ilustraciones, marketing):** un plugin de build genera AVIF/WebP en los anchos del set fijo; el output va a `dist/` con hash y se sirve como asset estático de Pages (cache `immutable` gratis, cero transformaciones facturables).

```ts
// vite.config.ts — con vite-imagetools, el import declara las variantes
// hero.jpg?w=640;1280;1920&format=avif;webp&as=picture
import heroImg from "@/assets/hero.jpg?w=640;1280;1920&format=avif;webp&as=picture";
```

**Por qué existe la regla del pipeline:** "optimizar imágenes" como paso manual se olvida siempre — la única versión sostenible es la que ocurre automáticamente en el camino del asset. Y por qué dos opciones: las estáticas del sitio se conocen en build (gratis optimizarlas ahí); las subidas por usuarios no existen en build (necesitan transformación on-the-fly).

---

## 6. Fonts

### 6.1 Self-hosted, subset, woff2

**[REQUIRED]** Las webfonts se sirven **self-hosted** (mismo origen, junto a los assets del build), en formato **woff2 únicamente**, y con **subset** de los glifos necesarios (para contenido en español/inglés: latin + latin-extended; no el set completo con cirílico, griego y vietnamita). Herramientas de referencia para el subset: descargar los woff2 ya subseteados (google-webfonts-helper, Fontsource), o generar con `glyphhanger`/`pyftsubset` para fuentes propias.

**Por qué cada pieza:** *self-hosted* — un origen de terceros (Google Fonts) suma DNS + TLS + conexión nueva antes del primer byte de la fuente, y desde 2020 los navegadores particionan el cache por sitio, así que "ya la tiene cacheada de otro sitio" es un mito; *woff2 solo* — todos los navegadores soportados lo leen, los demás formatos son bytes muertos; *subset* — una fuente completa puede pesar 300 KB donde el subset latin pesa 15–40 KB.

### 6.2 `font-display: swap` + preload de la principal

**[REQUIRED]** Todo `@font-face` lleva `font-display: swap` — el texto se pinta ya con la fallback y se intercambia al llegar la webfont; el texto **nunca** queda invisible esperando una fuente. **[RECOMMENDED]** La fuente del texto principal (la que usa el LCP si es texto) se preloadea:

```html
<link rel="preload" as="font" type="font/woff2" href="/fonts/inter-latin.woff2" crossorigin />
```

Solo la principal — preloadear 5 fuentes compite con el resto de recursos críticos y anula el beneficio (misma lógica que 2.1: todo prioritario = nada prioritario). El `crossorigin` es obligatorio aunque la fuente sea del mismo origen — los fetches de fonts son CORS por spec y sin él el preload se descarta y se descarga dos veces. El salto de layout del swap se mitiga con la fallback ajustada de 3.3.

### 6.3 Máximo 2 familias

**[REQUIRED]** Máximo 2 familias tipográficas por proyecto (típicamente: una de UI/texto + una display o mono si hace falta), y de cada familia solo los pesos que se usan (2–3 pesos, no los 9). Fuentes variables cuentan como una familia y son la mejor forma de tener varios pesos a costo de un archivo.

**Por qué:** cada familia × peso es un archivo que compite por ancho de banda en el momento más crítico de la carga — y un sistema de diseño con 4 familias no tiene un problema de performance, tiene un problema de diseño (`FRONTEND_ENGINEERING_STANDARD.md` §1.3 ya fija la escala tipográfica).

---

## 7. Red y camino crítico

### 7.1 `preconnect` a los orígenes críticos del primer render

**[RECOMMENDED]** Los orígenes de terceros que participan del primer render o del primer fetch de datos (la API si vive en otro subdominio, el dominio de media de R2) se declaran con `<link rel="preconnect">` en el `<head>` — máximo 2–3, solo los que de verdad se usan de inmediato.

```html
<link rel="preconnect" href="https://api.example.com" />
<link rel="preconnect" href="https://media.example.com" />
```

**Por qué:** cada origen nuevo cuesta DNS + TCP + TLS (~100–300ms en móvil) antes del primer byte; preconnect lo paga en paralelo con la carga del HTML en vez de en serie cuando llega el primer fetch. Y por qué solo 2–3: cada preconnect consume socket y CPU al arranque — preconnectar 8 orígenes "por si acaso" compite con los recursos críticos reales.

### 7.2 Prefetch de la ruta siguiente probable

**[RECOMMENDED]** Con el code splitting por ruta activo (sección 8.1), el chunk de la ruta a la que el usuario probablemente va (el link que hoverea, el paso siguiente del flujo) se prefetchea en idle o en hover/focus del link — la navegación se siente instantánea sin engordar el bundle inicial.

```tsx
// En el <Link> del router: al hover/focus, precargar el chunk de la ruta destino
onMouseEnter={() => import("@/features/settings")}  // el import() dinámico ya cachea el módulo
```

**Por qué RECOMMENDED:** es la segunda mitad del contrato del code splitting — split sin prefetch convierte cada navegación en una espera de red; prefetch sin criterio (todas las rutas) deshace el split. Hover/idle es el punto medio: se paga solo lo probable, fuera del camino crítico.

### 7.3 Compresión y cache de assets: resuelto por plataforma, no se rompe

Los assets del build salen con hash en el nombre y cache `immutable`, el HTML con `no-cache`, y la compresión (brotli/gzip) la aplica Cloudflare — todo ya definido en `08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md` §08 y `FRONTEND_ENGINEERING_STANDARD.md` §17; este documento no lo repite. La única regla propia aquí: **[REQUIRED]** no deshabilitar el hashing de nombres del build ni servir assets por rutas sin hash "para simplificar" — el cache inmutable de toda la sección depende de eso.

---

## 8. JavaScript — cada KB del bundle inicial se gana su lugar

### 8.1 Code splitting por ruta

**[REQUIRED]** Ya regla del Nivel 1 (`FRONTEND_ENGINEERING_STANDARD.md` §8.2): toda ruta que no sea la primera pantalla se carga con `lazy`/`import()`. Este documento agrega el criterio de verificación: el JS que se descarga antes del primer render es solo entry + vendor compartido + la ruta actual — es exactamente lo que mide el gate 2.2 de `06_Testing/08` (presupuesto de bundle inicial). Si agregar una feature nueva engorda el bundle *inicial*, el split está roto.

**[RECOMMENDED]** Además de por ruta, se difiere por componente lo pesado y condicional dentro de una ruta: un editor rico, un chart complejo o un modal de importación que la mayoría de sesiones no abre se cargan con `React.lazy` al momento de usarse — con skeleton del tamaño real (sección 3.2) mientras llega.

### 8.2 Dependencias auditadas antes de instalar

**[RECOMMENDED]** Antes de `npm install` de cualquier dependencia de producción se miran su costo (bundlephobia.com o `npx howfat`) y alternativas. Regla de decisión: **si agrega >30 KB gzip al bundle para algo que se escribe en ~50 líneas propias, se escribe.** Ejemplos clásicos del lado "se escribe": debounce, formateo de fechas simple (`Intl` lo hace nativo — ver `FRONTEND_PWA_I18N_STANDARD.md` §7.2), un modal, clases condicionales. Del lado "se instala": date math con zonas horarias, editores de texto enriquecido, charts — complejidad real que 50 líneas no cubren.

**Por qué RECOMMENDED y no REQUIRED:** el número 30 KB / 50 líneas es una heurística de juicio, no un umbral verificable por máquina — el gate verificable es el presupuesto de bundle (gate 2.2), que es quien bloquea. Esta regla existe para que el gate no falle, no para reemplazarlo. **Por qué la regla existe:** cada dependencia es KB del presupuesto + superficie de supply chain (`06_Testing/08` §4.2) + versiones que mantener — el costo real es 3x el KB visible.

### 8.3 Tree shaking real: imports nombrados, sin barrels gordos

**[REQUIRED]** Los imports son nombrados y apuntan a lo que se usa: nunca `import * as X` de una librería, y los barrel files (`index.ts` re-exportando todo) se limitan a la API pública de cada feature con pocas exports (`FRONTEND_ENGINEERING_STANDARD.md` §3.3) — jamás un barrel global que re-exporta decenas de módulos.

```ts
❌ import * as Icons from "lucide-react";        // arrastra el set completo de íconos
❌ import { UserCard } from "@/components";       // barrel gordo: importa 1, evalúa 80
✅ import { Settings } from "lucide-react";       // el bundler puede sacudir el resto
✅ import { UserCard } from "@/features/users";   // barrel chico de API pública
```

**Por qué:** el tree shaking elimina exports **no usados**, pero solo puede eliminar lo que puede *probar* que no tiene efectos. `import *` declara intención de usar todo; un barrel gordo hace que importar una card evalúe (y potencialmente empaquete) los 80 módulos hermanos, porque cualquiera puede tener side effects en su scope de módulo. El resultado no es solo bundle grande: los barrels son también la causa #1 de dependencias circulares (gate 5.3 de `06_Testing/08`, madge en cero ciclos). La regla se auto-verifica con el gate 2.2: si el bundle inicial contiene código de features que la primera pantalla no usa, hay un barrel o un `import *` filtrando.

### 8.4 Lo que ya definió el Nivel 1 y no se repite

Memoización con evidencia (no preventiva) — `FRONTEND_ENGINEERING_STANDARD.md` §11.2. Presupuesto medido, no asumido — §11.1, hecho ejecutable en el gate 2.2.

---

## 9. CSS — Tailwind ya resuelve el purge; la regla es no deshacerlo

**[REQUIRED]** Nada de CSS-in-JS **runtime** (styled-components, Emotion en modo runtime, o cualquier librería que genera/inyecta estilos en ejecución). El enfoque de estilos del proyecto ya es único por regla del Nivel 1 (`FRONTEND_ENGINEERING_STANDARD.md` §10.1) y es Tailwind — que genera CSS estático en build y elimina lo no usado; ese resultado no se contamina con una segunda vía runtime. Al evaluar una librería de componentes, su enfoque de estilos es criterio de entrada: una que arrastra Emotion runtime trae el problema embebido aunque "nosotros" no escribamos CSS-in-JS.

**Por qué:** el CSS-in-JS runtime cobra tres veces: (1) la librería viaja en el bundle (10–20 KB gzip que compiten con el presupuesto del gate 2.2), (2) genera e inyecta estilos en el main thread durante el render — trabajo que compite con INP en cada mount, (3) sus estilos no existen hasta que corre el JS — el primer paint sin estilos o bloqueado por JS, lo contrario del CSS estático que el navegador procesa en paralelo. Si un componente necesita valores dinámicos, la vía es CSS variables + clases estáticas, no generar CSS en runtime:

```tsx
// ✅ dinámico sin runtime CSS: la clase es estática, el valor viaja por CSS variable
<div className="h-2 rounded bg-brand w-[var(--progress)]" style={{ "--progress": `${pct}%` }} />
```

---

## 10. Third-party scripts — cada uno se justifica

**[REQUIRED]** Ningún script de terceros entra sin: (1) una justificación escrita de qué aporta (analytics, pagos, soporte — y por qué no se resuelve sin script), (2) carga con `async`/`defer` o inyección post-load — **nunca** un `<script>` síncrono en el `<head>` bloqueando el parser, (3) revisión periódica: el script que ya no se usa se elimina, no queda "por si acaso".

```html
❌ <head><script src="https://cdn.tercero.com/widget.js"></script></head>
✅ <script async src="..."></script>
✅ window.addEventListener("load", () => { /* inyectar el script no crítico */ });
```

**[RECOMMENDED]** Los widgets de terceros con UI (chat de soporte, video embebido) se cargan bajo demanda con *facade*: un placeholder liviano con la apariencia del widget (imagen del player, botón de chat) que carga el script real recién al primer click. El caso YouTube es el clásico: el iframe real pesa cientos de KB de JS; la facade pesa una imagen.

**Por qué:** los third-party son el JS que no controlas — cambian de peso sin avisar, corren long tasks en tu main thread (directo contra INP) y un `<script>` síncrono de un dominio caído congela la página entera. La medición de Lighthouse los castiga igual que al código propio, pero solo se pueden arreglar quitándolos o difiriéndolos — por eso la barrera está en la entrada. Analytics propio primero: para web vitals reales ya existe la sección 12.2, que no requiere terceros.

---

## 11. Listas largas

**[RECOMMENDED]** Ya regla del Nivel 1 (`FRONTEND_ENGINEERING_STANDARD.md` §11.3): listas de decenas a cientos de elementos se virtualizan (ej. `@tanstack/react-virtual`), no se renderiza todo el DOM. La cara de performance que este documento agrega: una lista de 1.000 filas renderizadas es tanto un problema de INP (cada interacción re-reconcilia 1.000 nodos) como de memoria — y la virtualización se combina con paginación del backend (no traer 10.000 registros para mostrar 20, `FRONTEND_TABLE_PATTERNS.md`). Las filas virtualizadas tienen altura conocida o estimada estable — filas de altura caótica producen scroll que salta (el CLS del scroll infinito).

---

## 12. Medición — sin medir, todo lo anterior es fe

### 12.1 Lab: Lighthouse local + el gate de CI

**[REQUIRED]** Antes de marcar una pantalla nueva como terminada se corre Lighthouse local **contra el preview build** (`vite preview`), nunca contra el dev server (sin minificar ni comprimir, sus números no significan nada). El enforcement automático es el gate 2.1 de `06_Testing/08_QUALITY_STANDARDS.md` (Lighthouse CI con sus umbrales y mediana de runs) más el gate 2.2 (presupuesto de bundle) — este documento no duplica sus números; la corrida local existe para no descubrir en el PR lo que se pudo ver en 2 minutos antes.

**Flujo cuando un gate falla** (diagnóstico, no prueba y error):

1. Gate 2.2 (bundle) rojo → `npx vite-bundle-visualizer`: *qué* módulo infló el chunk inicial. Sospechosos en orden: dependencia nueva sin auditar (8.2), barrel/`import *` filtrando una feature al entry (8.3), ruta que dejó de ser lazy (8.1), librería duplicada (`06_Testing/08` §4.3).
2. Gate 2.1 por LCP → el audit nombra el elemento (2.4): ¿lazy en el LCP? ¿imagen sin pipeline (5.5)? ¿fuente bloqueando texto (6.2)?
3. Gate 2.1 por CLS → el reporte lista los elementos que se movieron: casi siempre dimensiones ausentes (3.1) o skeleton de tamaño falso (3.2).
4. Gate 2.1 por TBT (proxy lab de interactividad) → DevTools Performance sobre la carga: qué long task, de quién (propio → 4.1/4.3; tercero → 10).

### 12.2 Field: Web Vitals de usuarios reales

**[RECOMMENDED]** La app reporta sus Core Web Vitals reales con la librería `web-vitals` hacia un endpoint propio (un worker que persiste métrica + página + user agent; el detalle de plataforma en `08_Cloud`):

```ts
// src/shared/vitals.ts
import { onLCP, onCLS, onINP, type Metric } from "web-vitals";
const report = (metric: Metric) =>
  navigator.sendBeacon("/api/vitals", JSON.stringify({
    name: metric.name, value: metric.value, rating: metric.rating, path: location.pathname,
  }));
onLCP(report); onCLS(report); onINP(report);
```

**Por qué el lab no basta:** Lighthouse corre en una máquina con throttling simulado — INP directamente **no se mide en lab** (el gate usa TBT como proxy, declarado en `06_Testing/08` §2.1). El INP real solo existe donde hay usuarios reales interactuando con datos reales en dispositivos reales; sin field data, la sección 4 entera se valida a ciegas. `sendBeacon` porque las métricas se terminan de conocer al abandonar la página, cuando un `fetch` normal ya se cancela. **Por qué RECOMMENDED:** requiere un endpoint y algo de análisis — para un producto sin tráfico todavía, el gate de lab es suficiente arranque; se activa al tener usuarios. Lo que se mira al tenerlo: el **percentil 75 por métrica y por página** (el criterio de Google), no el promedio — el promedio esconde exactamente a los usuarios lentos que las métricas existen para proteger.

---

## 13. Anti-patrones

- ❌ `loading="lazy"` en la hero / elemento LCP; hero como `background-image` de CSS.
- ❌ Imagen de 2000px servida para un render de 200px ("se ve bien" ≠ "pesa bien").
- ❌ Optimizar imágenes a mano en vez de pipeline automático (R2 + transformaciones o build).
- ❌ Spinner chico que se reemplaza por contenido grande; banner que empuja contenido ya pintado.
- ❌ `<img>`/`<iframe>`/embed sin dimensiones declaradas.
- ❌ Google Fonts por CDN de terceros, fuente completa sin subset, 4 familias, preload de todas.
- ❌ Filtro/orden de miles de filas síncrono en el handler del input, sin transition ni debounce.
- ❌ Botón que no reacciona hasta que responde la API.
- ❌ `import * as X` de librerías; barrel global que re-exporta todo el proyecto.
- ❌ Instalar 70 KB de dependencia para algo de 50 líneas, sin mirar bundlephobia.
- ❌ CSS-in-JS runtime conviviendo con Tailwind (propio o arrastrado por una librería de componentes).
- ❌ `<script>` de terceros síncrono en el `<head>`; scripts muertos que nadie quita; iframe de YouTube sin facade.
- ❌ Preconnect a 8 orígenes "por si acaso"; code splitting sin prefetch de la ruta siguiente.
- ❌ Medir performance contra el dev server y creerse los números; mirar promedios en vez de p75.
- ❌ "Optimizamos al final" — al final cuesta 10x y nunca llega.

---

## Checklist rápido

- [ ] ¿Cada pantalla nueva respondió las 3 preguntas de diseño (elemento LCP, espacio reservado para lo que llega tarde, handler más pesado)?
- [ ] ¿El elemento LCP identificado y verificado (2.4), eager, con `fetchpriority="high"` (y preload solo si no está en el HTML inicial)?
- [ ] ¿Toda imagen/embed con dimensiones declaradas; skeletons del tamaño real; banners que no empujan contenido pintado?
- [ ] ¿Fonts con `font-display: swap` (+ fallback `size-adjust` si el CLS de fonts molesta)?
- [ ] ¿Handlers de interacción cortos — trabajo pesado diferido, en transición, troceado o fuera del cliente — y feedback visual en <200ms siempre?
- [ ] ¿Imágenes en AVIF/WebP (por `format=auto` o `<picture>`), con `srcset`/`sizes` del set fijo de anchos, dimensionadas a ≤2x el render, lazy salvo above-the-fold?
- [ ] ¿Pipeline de imágenes automático elegido y documentado (Transformations sobre R2, o variantes en build), con helper único de URLs?
- [ ] ¿Fonts self-hosted, subset, woff2, ≤2 familias, preload solo de la principal con `crossorigin`?
- [ ] ¿Preconnect solo a los 2–3 orígenes del primer render; prefetch de la ruta siguiente probable?
- [ ] ¿Code splitting por ruta intacto — el bundle inicial no creció con la última feature — y lazy por componente en lo pesado condicional?
- [ ] ¿Dependencias nuevas pasaron por bundlephobia y la regla 30 KB / 50 líneas?
- [ ] ¿Imports nombrados, sin `import *`, barrels solo chicos de API pública?
- [ ] ¿Cero CSS-in-JS runtime, incluido el que arrastran librerías de componentes?
- [ ] ¿Cada third-party justificado por escrito, async/defer, facades en widgets pesados, y los muertos eliminados?
- [ ] ¿Listas largas virtualizadas + paginadas, con alturas de fila estables?
- [ ] ¿Lighthouse local contra preview build antes del PR; gates 2.1/2.2 de `06_Testing/08` en verde; al fallar, se diagnostica con el flujo de 12.1?
- [ ] ¿Web vitals de campo reportándose y leídos en p75 (si ya hay usuarios)?
