# FRONTEND PWA & I18N STANDARD

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1) y se coordina con [FRONTEND_PERFORMANCE_STANDARD.md](FRONTEND_PERFORMANCE_STANDARD.md) y con la política de cache de [08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md](../../08_Cloud/CLOUDFLARE_PLATFORM_STANDARD.md) §08. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> **Qué es este documento:** dos capacidades **opt-in** — PWA (instalable/offline) e i18n (multi-idioma). A diferencia del resto de estándares de Frontend, estas no aplican a todo proyecto: cada una empieza con su **criterio de adopción explícito**. Adoptarlas sin criterio es puro costo (un service worker es la fuente de bugs de cache más difícil de depurar que existe; una capa i18n completa para un producto monolingüe es fricción diaria sin beneficio). Lo que sí aplica siempre es la *preparación mínima barata* de cada una (secciones 2.4 y 7).

---

# PARTE A — PWA

## 1. Criterio de adopción

**[REQUIRED]** Un proyecto se construye como PWA **solo si** cumple al menos uno de estos criterios — y la decisión (sí o no, con el criterio que la sostiene) se deja escrita en el README del proyecto:

- **Uso recurrente con sesión iniciada** (SaaS de uso diario/semanal): el acceso desde ícono instalado y el arranque instantáneo desde cache aportan valor real.
- **Valor offline genuino:** hay algo útil que hacer sin conexión (consultar datos ya cargados, capturar datos que se sincronizan después) — no solo mostrar "sin conexión".
- **Contexto de red hostil del usuario objetivo** (móvil, campo, redes inestables) donde la resiliencia a cortes es una feature del producto.

**No es PWA:** una landing, un sitio de marketing, una web de consulta esporádica. Instalar un service worker "porque es gratis" no es gratis: es una capa de cache programable entre el usuario y cada deploy, con capacidad de servir versiones viejas indefinidamente si se configura mal.

**Por qué el criterio es REQUIRED aunque la capacidad sea opcional:** la decisión por defecto ("el template ya traía el plugin") es la peor de las opciones — se paga el costo operativo del SW sin haber diseñado offline ni updates. Opt-in significa decisión consciente, en ambos sentidos.

## 2. Manifest

**[REQUIRED]** Si el proyecto es PWA, el manifest está completo — no el mínimo que calla la consola:

```json
{
  "name": "TradePulse — Trading Journal",
  "short_name": "TradePulse",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#0F172A",
  "theme_color": "#0F172A",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

Reglas dentro del manifest:

- **Iconos maskable [REQUIRED]:** al menos un icono 512×512 con `purpose: "maskable"`, con el contenido crítico dentro de la *safe zone* (círculo interior de ~80% del canvas). **Por qué:** Android recorta los iconos a la forma del launcher (círculo, squircle); un icono normal usado como maskable pierde las esquinas o queda flotando sobre fondo blanco — es el error visual #1 de PWAs instaladas.
- **`theme_color` coherente con el tema [REQUIRED]:** el mismo color de fondo del design system (`FRONTEND_COLOR_CONTRAST_STANDARD.md` §4 — navy oscuro, no negro puro), para que la barra del sistema no desentone con la app instalada.
- **`background_color`** igual al fondo real de la app: es el color del splash mientras carga — un flash blanco antes de una app dark es un bug visual evitable.

## 3. Service worker — estrategias por tipo de recurso

**[REQUIRED]** El service worker se genera con **Workbox** vía `vite-plugin-pwa` — nunca un SW escrito a mano desde cero. **Por qué:** el ciclo de vida de un SW (install/waiting/activate, precache manifest, limpieza de caches viejos) tiene esquinas que Workbox resuelve y que a mano se hacen mal a la primera; el costo de un SW con bug no es "no funciona" sino "usuarios atrapados en una versión vieja".

**[REQUIRED]** La estrategia de cache se decide **por tipo de recurso**, nunca una sola global — es el espejo cliente de la política de CDN de `08_Cloud` §08 (misma lógica, otra capa):

| Recurso | Estrategia | Por qué |
|---|---|---|
| Assets del build con hash (JS/CSS/fonts) | **Precache / cache-first** | Inmutables por hash: si está en cache, es correcto por definición — red cero |
| Imágenes de contenido | Cache-first con expiración (días) y tope de entradas | Reutilizables entre sesiones, pero sin crecer sin límite |
| HTML / navegación | **Network-first** con fallback a cache | El HTML referencia el build vigente (`08_Cloud` §08: no se cachea largo) — la red trae la versión nueva; el cache solo salva el offline |
| API de datos | **Network-first** (o no interceptar) — y ver sección 4 | El dato fresco manda; el cache es solo resiliencia |
| Página offline | Precacheada, servida como fallback de navegación | Un "sin conexión" propio y útil, no el dinosaurio del navegador |

**Implementación (`vite-plugin-pwa`, fragmento):**

```ts
// vite.config.ts
VitePWA({
  registerType: "prompt",                 // update flow de la sección 5 — nunca autoUpdate silencioso a mitad de uso
  workbox: {
    globPatterns: ["**/*.{js,css,html,woff2,svg}"],   // precache del build
    navigateFallback: "/offline.html",
    runtimeCaching: [
      {
        urlPattern: ({ request }) => request.destination === "image",
        handler: "CacheFirst",
        options: { cacheName: "img", expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 14 } },
      },
      // La API autenticada NO aparece aquí — sección 4
    ],
  },
})
```

## 4. Qué NUNCA cachear en el service worker

**[REQUIRED]** El SW **jamás cachea respuestas autenticadas de la API** (nada que dependa de `Authorization` o cookie de sesión), ni tokens, ni cualquier respuesta por-usuario. Es la misma regla que `08_Cloud` §08 impone al CDN (`private, no-store`), aplicada a la cache del cliente — las dos capas son coherentes o el bug aparece en la que se olvidó.

**Por qué es su propia sección y no una fila más de la tabla:** el CDN comparte cache entre usuarios (el riesgo es servir datos de A a B); el SW es por-dispositivo, así que el riesgo cambia de forma pero no de gravedad — datos de la cuenta de A servidos a B que inicia sesión después en el mismo dispositivo, datos sensibles persistidos en disco fuera del control de sesión (el logout no los borra), y estados imposibles donde la UI muestra datos viejos de un usuario con el token de otro. Si una vista necesita datos offline, la vía es el estado del cliente con scope de usuario y limpieza en logout (React Query persist con clave por usuario) — una capa que *sabe* de sesiones — no la cache HTTP del SW, que no sabe.

**[REQUIRED]** El SW tampoco intercepta rutas de auth (login, logout, refresh de tokens): pasan directo a la red siempre.

## 5. Update flow — avisar, no forzar

**[REQUIRED]** El flujo de actualización del SW es: (1) el SW nuevo se instala y queda en *waiting*; (2) la UI muestra un aviso no-modal ("Hay una versión nueva — Actualizar"); (3) **el usuario decide cuándo** — al aceptar, se activa el SW nuevo (`skipWaiting`) y se recarga. **Nunca** se fuerza un reload automático a mitad de uso.

```tsx
// Con vite-plugin-pwa (registerType: "prompt")
const { needRefresh, updateServiceWorker } = useRegisterSW();
// needRefresh → toast persistente no-modal (FRONTEND_NOTIFICATIONS_PATTERNS.md):
// "Nueva versión disponible" [Actualizar] → updateServiceWorker(true)
```

**Por qué:** un reload forzado en medio de un formulario o una operación destruye trabajo del usuario — es exactamente el tipo de "optimización" que convierte una mejora de infraestructura en un bug de UX. El caso extremo (migración incompatible de API donde la versión vieja ya no puede operar) se maneja como aviso bloqueante explícito, no como reload silencioso.

## 6. Límites honestos — iOS

**[RECOMMENDED]** Antes de prometer "instalable y offline" a producto/cliente, se declaran los límites reales en iOS (Safari es el único motor en iOS; estado a 2026 — verificar contra caniuse/WebKit al prometer):

- **No hay prompt de instalación:** nada de `beforeinstallprompt`; instalar es "Compartir → Añadir a pantalla de inicio", manual y poco descubrible. Si la instalación es central al negocio en iOS, la respuesta puede ser una app nativa/wrapper, no fingir que la PWA equivale.
- **Storage evictable:** Safari puede purgar el storage de origen (caches del SW incluidas) tras períodos sin uso — el offline en iOS es *best effort*, nunca la única copia de nada (la fuente de verdad siempre es el backend).
- **Push:** las notificaciones web push en iOS existen solo para PWAs instaladas (desde iOS 16.4) y con permiso explícito — no equivalen al push nativo en fiabilidad.
- **Sin Background Sync:** la sincronización diferida "cuando vuelva la red aunque la app esté cerrada" no existe en iOS — la cola offline se reintenta al reabrir la app, y el diseño lo asume.

**Por qué está en el estándar:** el costo de descubrir estos límites después de prometerlos es un replanteo del producto; el costo de declararlos antes es un párrafo.

---

# PARTE B — i18n

## 7. Criterio de adopción — y la preparación mínima que aplica siempre

**[REQUIRED]** i18n completo (librería, archivos por idioma, selector) se implementa **desde el día 1 solo si el producto nace multi-idioma** (mercados objetivo con idiomas distintos ya definidos). Si no, **no** se instala la maquinaria — pero sí la preparación mínima barata:

**7.1 [RECOMMENDED] Cero strings de UI hardcodeados en JSX.** Todo texto visible vive en un archivo de mensajes central, aunque haya un solo idioma:

```tsx
// src/shared/messages.ts — un solo idioma, cero librerías
export const M = {
  dashboard: { title: "Panel de control", empty: "Todavía no hay operaciones" },
  actions: { save: "Guardar", cancel: "Cancelar" },
} as const;

// ❌ <h1>Panel de control</h1>
// ✅ <h1>{M.dashboard.title}</h1>
```

**Por qué RECOMMENDED y por qué barato:** cuesta ~0 al escribir (el string se escribe igual, solo que en otro archivo) y compra tres cosas: migrar a multi-idioma es mecánico (el archivo *es* el catálogo a traducir, no un grep de 400 componentes); el copy se revisa en un solo lugar (`FRONTEND_MICROCOPY_STANDARD.md` deja de ser un tour por el código); y refuerza la regla de idiomas del Nivel 1 (`FRONTEND_ENGINEERING_STANDARD.md` §3.2 — código en inglés, contenido en español, nunca mezclados).

**7.2 [REQUIRED] `Intl` para fechas, números y monedas — SIEMPRE, haya un idioma o veinte.** Nunca formateo manual con concatenación, `toFixed` + símbolo, o arrays de nombres de meses:

```ts
// ❌ const fecha = `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
// ❌ const precio = "$" + value.toFixed(2);
✅ new Intl.DateTimeFormat("es-AR", { dateStyle: "medium" }).format(d)
✅ new Intl.NumberFormat("es-AR", { style: "currency", currency: "USD" }).format(value)
```

**Por qué REQUIRED incluso monolingüe:** el formateo manual es un generador de bugs presentes, no solo una deuda futura — separadores de miles/decimales invertidos entre locales (1.234,56 vs 1,234.56), monedas con símbolo ambiguo ($ es ARS, USD, MXN...), meses a mano desincronizados del idioma. `Intl` es nativo (0 KB de bundle — coherente con la regla 30 KB/50 líneas de `FRONTEND_PERFORMANCE_STANDARD.md` §7.2: esto ya viene resuelto en la plataforma), correcto por locale, y centralizable: los formatters viven en `src/shared/format.ts` con el locale como parámetro — un solo lugar a tocar si mañana hay más idiomas (coherente con `FRONTEND_FORMATTING_STANDARD.md`, que define *qué* formato usa el producto; esta regla define *con qué mecanismo* se implementa).

## 8. Si el producto es multi-idioma — la maquinaria

### 8.1 Librería

**[RECOMMENDED]** **i18next + react-i18next** como implementación de referencia. Por qué esta y no otra: es el estándar de facto del ecosistema React (madurez, docs, plugins de detección de idioma y carga lazy de catálogos), soporta plurales vía `Intl.PluralRules` e ICU (con `i18next-icu`), interpolación segura por defecto (escapa valores — coherente con XSS, `FRONTEND_ENGINEERING_STANDARD.md` §12.3), y permite cargar cada idioma como chunk separado (coherente con el presupuesto de bundle: los usuarios no descargan idiomas que no usan). Alternativas válidas si el contexto lo justifica (se documenta el porqué): `react-intl`/FormatJS (más cerca del estándar ICU puro), o Paraglide/LinguiJS (compilados, menos KB runtime). La regla agnóstica es: **una** librería de i18n, elegida y documentada — nunca dos conviviendo, nunca i18n casero con ternarios de idioma en los componentes.

### 8.2 Claves semánticas, no textuales

**[REQUIRED]** Las claves de traducción describen **el lugar y el rol** del mensaje, no su texto:

```
❌ t("Guardar_cambios")            // clave = texto: cambiar el copy rompe la clave
❌ t("texto_boton_azul_arriba")    // clave = presentación: el botón cambia de color y miente
✅ t("settings.actions.save")      // feature.contexto.rol — sobrevive a cambios de copy y de UI
```

**Por qué:** la clave es un contrato estable entre el código y N catálogos; si la clave es el texto en un idioma, cada ajuste de copy en ese idioma obliga a tocar código y todos los demás catálogos. La estructura `feature.contexto.rol` además agrupa por feature — coherente con la organización del Nivel 1 (§2.1).

### 8.3 Plurales y variables con ICU — nunca concatenación

**[REQUIRED]** Todo mensaje con cantidad usa el mecanismo de plurales de la librería (basado en `Intl.PluralRules` / sintaxis ICU); toda variable va interpolada dentro del mensaje traducible, nunca concatenada alrededor:

```
❌ {count} + " " + t("operaciones")            // "1 operaciones"; y el orden de palabras no es universal
✅ t("trades.count", { count })
   // catálogo (ICU): "{count, plural, one {# operación} other {# operaciones}}"
```

**Por qué:** las reglas de plural no son universales — español/inglés tienen 2 formas, pero otros idiomas tienen entre 1 y 6 (ruso 3+, árabe 6); concatenar también congela el orden de las palabras, que cambia por idioma. Solo el mensaje completo, con la cantidad dentro, es traducible correctamente.

### 8.4 RTL básico: logical properties desde el día 1 multi-idioma

**[REQUIRED]** El espaciado y la alineación horizontales se escriben con **propiedades lógicas** (start/end), no físicas (left/right): en Tailwind, `ps-*`/`pe-*`, `ms-*`/`me-*`, `text-start`/`text-end` en lugar de `pl-*`/`pr-*`, `ml-*`/`mr-*`, `text-left`/`text-right`.

```
❌ <span class="ml-2 pl-4 text-left">   // en RTL el margen queda del lado equivocado
✅ <span class="ms-2 ps-4 text-start">  // "start" se voltea solo con dir="rtl"
```

**Por qué es REQUIRED ya, aunque hoy no haya árabe/hebreo en el roadmap:** escribir lógico cuesta exactamente lo mismo que escribir físico (misma clase, otras dos letras) y hace que soportar un idioma RTL sea `dir="rtl"` + revisión, en vez de una auditoría de cada margen del proyecto. Es el ejemplo puro de "barato ahora, carísimo después". `left`/`right` físicos quedan solo para lo que no debe voltearse (posicionamiento absoluto de decoración, direcciones del mundo físico).

### 8.5 `lang` en `<html>` por idioma activo

**[REQUIRED]** El atributo `lang` del `<html>` refleja el idioma **activo** de la UI, actualizado al cambiar de idioma (y `dir="rtl"` cuando corresponde). **Por qué:** los lectores de pantalla eligen el motor de voz según `lang` — un `lang="en"` con UI en español se lee con fonética inglesa, inentendible (accesibilidad real, `FRONTEND_ACCESSIBILITY_STANDARD.md`); también depende de `lang` la autotraducción del navegador y el hyphenation de CSS.

### 8.6 hreflang si hay SEO multi-idioma

**[RECOMMENDED]** Si las páginas públicas (landing, docs, pricing) existen en varios idiomas indexables, cada versión declara `hreflang` recíproco hacia las demás (incluida `x-default`) y cada idioma tiene URL propia (`/es/`, `/en/` — nunca el mismo URL que cambia por cookie). El detalle de implementación SEO (sitemaps, canonicals) vive en `FRONTEND_SEO_STANDARD.md` — este documento solo fija la obligación de coherencia: si hay contenido público multi-idioma, hay hreflang; si la app es privada (detrás de login), no aplica.

---

## 9. Anti-patrones

- ❌ Service worker "porque el template lo traía", sin criterio de adopción escrito.
- ❌ SW cacheando respuestas autenticadas de API (o interceptando rutas de auth).
- ❌ Una sola estrategia de cache global para todo tipo de recurso.
- ❌ `autoUpdate` con reload forzado a mitad de uso.
- ❌ Icono no-maskable como maskable (recortado por el launcher); splash con flash blanco en app dark.
- ❌ Prometer offline/instalación idénticos en iOS sin declarar los límites.
- ❌ Instalar i18next completo "por si acaso" en un producto que nace monolingüe.
- ❌ Strings de UI hardcodeados por 400 componentes.
- ❌ Fechas/números/monedas formateados a mano en vez de `Intl`.
- ❌ Claves de traducción que son el texto mismo, o que describen la presentación.
- ❌ Plurales por concatenación (`count + " items"`) o con ternario `count === 1`.
- ❌ `pl-*`/`mr-*`/`text-left` físicos en un producto multi-idioma.
- ❌ `lang` estático que no cambia con el idioma activo.

---

## Checklist rápido

**PWA (solo si se adoptó):**
- [ ] ¿La decisión PWA sí/no está escrita con su criterio (uso recurrente / offline genuino / red hostil)?
- [ ] ¿Manifest completo: iconos 192/512 + maskable con safe zone, `theme_color`/`background_color` coherentes con el tema?
- [ ] ¿SW generado con Workbox/vite-plugin-pwa, estrategias por tipo de recurso (precache assets con hash, network-first HTML/API, fallback offline propio)?
- [ ] ¿Cero respuestas autenticadas en la cache del SW; rutas de auth sin interceptar; datos offline por-usuario en estado de cliente con limpieza en logout?
- [ ] ¿Update flow con aviso y decisión del usuario — nunca reload forzado a mitad de uso?
- [ ] ¿Límites de iOS declarados antes de prometer features (instalación, storage evictable, push, sin background sync)?

**i18n (siempre):**
- [ ] ¿Strings de UI en archivo de mensajes central, no hardcodeados en JSX (aunque haya un solo idioma)?
- [ ] ¿Fechas/números/monedas con `Intl` vía formatters centralizados — cero formateo manual?

**i18n (si multi-idioma):**
- [ ] ¿Una sola librería elegida y justificada; catálogos cargados por chunk de idioma?
- [ ] ¿Claves semánticas `feature.contexto.rol`, no textuales?
- [ ] ¿Plurales ICU con variables interpoladas — cero concatenación?
- [ ] ¿Logical properties (`ps`/`pe`/`ms`/`me`/`text-start`) en todo espaciado horizontal?
- [ ] ¿`lang` (y `dir`) del `<html>` actualizados con el idioma activo?
- [ ] ¿hreflang recíproco + URL por idioma en páginas públicas indexables (detalle en `FRONTEND_SEO_STANDARD.md`)?
