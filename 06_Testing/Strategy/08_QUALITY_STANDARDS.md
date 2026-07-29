---
title: "Quality Gates del Build"
category: 06_Testing
tags: [testing, quality-gates, accesibilidad, performance, seguridad]
summary: "Principios de diseño de los gates y su definición numérica: accesibilidad, rendimiento, seguridad de build, dependencias y calidad de código."
keywords: [quality-gates, accesibilidad, performance, seguridad, dependencias, umbrales]
updated: 2026-07-27
status: current
---

# QUALITY STANDARDS — Quality Gates del build

> Documento del dominio `06_Testing`. Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> **Qué es este documento:** los umbrales mínimos de calidad **no funcional** (accesibilidad, rendimiento, seguridad de build, dependencias, calidad de código) que un build debe cumplir para considerarse desplegable. Cada gate define **qué se mide, con qué herramienta y con qué umbral**. El *cuándo y cómo* corre cada gate dentro del pipeline (jobs, orden, caching, status checks) vive en [03_CI_CD.md](../Pipelines/03_CI_CD.md) — aquí solo se declara la frecuencia mínima esperada: "por PR" o "nightly".
>
> **Regla de herencia:** las **reglas** de accesibilidad viven en [01_Frontend/FRONTEND_ACCESSIBILITY_STANDARD.md](../../01_Frontend/UI_Components/FRONTEND_ACCESSIBILITY_STANDARD.md) y [01_Frontend/FRONTEND_COLOR_CONTRAST_STANDARD.md](../../01_Frontend/UI_Components/FRONTEND_COLOR_CONTRAST_STANDARD.md); las de seguridad en `05_Security/SECURITY_ENGINEERING_STANDARD.md`; las de plataforma GitHub en [07_DevOps/GITHUB_STANDARD.md](../../07_DevOps/GITHUB_STANDARD.md). Este documento **no repite ninguna regla** — define cómo se **verifica automáticamente** cada una. El patrón de todo el documento es: *regla en X, gate aquí*.

---

## 0. Principios de diseño de los gates

Tres principios atraviesan todo el documento — se enuncian una vez aquí y cada sección los aplica:

**[REQUIRED] 0.1 — Un gate solo sirve si se respeta; solo se respeta si es confiable.** Un gate que falla por ruido (flakiness de Lighthouse, warnings triviales de axe, advisories sin fix de dev-deps) entrena al equipo — aunque el equipo sea una persona — a ignorarlo o apagarlo, y con el ruido se va también la señal. Por eso cada gate de este documento bloquea **solo lo grave y estable** (violaciones serious+, mediana de runs, prod-deps) y degrada el resto a warning visible. Un gate estricto pero apagado protege menos que uno laxo pero encendido.

**[REQUIRED] 0.2 — Umbral absoluto, no delta.** Los gates comparan contra un piso fijo ("Performance ≥ 90"), nunca contra el run anterior ("bajó 2 puntos"). Los deltas convierten ruido de medición en rojos aleatorios y permiten degradación por goteo (100 caídas de 1 punto pasan; una de 10 no — el resultado es el mismo). El piso se recalibra con evidencia y por escrito (formato del handbook §3), no por acumulación de excepciones.

**[REQUIRED] 0.3 — La deuda vieja se congela, no bloquea PRs ajenos.** Cuando un gate se introduce sobre un proyecto con deuda existente (exports muertos, warnings de lint), el estado actual se registra como baseline y el gate bloquea solo lo **nuevo**. La alternativa — exigir limpiar todo antes de encender el gate — pospone el gate indefinidamente, que es peor que tolerar deuda conocida y acotada. Excepción deliberada: dependencias circulares (5.3), donde el baseline correcto es cero porque cada ciclo legitima al siguiente.

---

## 1. Gate de accesibilidad

### 1.1 axe-core en las páginas del smoke

**[REQUIRED]** Regla en `01_Frontend/FRONTEND_ACCESSIBILITY_STANDARD.md` (secciones 3–9) y `FRONTEND_COLOR_CONTRAST_STANDARD.md` (sección 5) — **gate aquí:** todas las páginas del smoke test (login, registro, dashboard, y la landing si existe) pasan por axe-core vía `@axe-core/playwright`, y el build falla si existe **una sola violación de impacto `serious` o `critical`**. Corre por PR.

**Por qué `serious`/`critical` y no "cero de todo":** axe clasifica cada violación en `minor` / `moderate` / `serious` / `critical`. Exigir cero absoluto suena más estricto pero mata la adopción del gate: las violaciones `minor`/`moderate` (ej. landmarks duplicados, regiones sin nombre) generan ruido constante, el equipo aprende a ignorar el gate o lo apaga "temporalmente", y con él se van también las violaciones graves. Un gate que bloquea solo lo grave se respeta; lo `moderate` se revisa en el reporte, no bloquea. El objetivo real es WCAG 2.1 AA (regla en `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 1) — el nivel `serious`+ es la heurística de bloqueo que mantiene el gate vivo.

**Implementación (Playwright):**

```ts
// e2e/a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const SMOKE_PAGES = ['/', '/login', '/register', '/dashboard'];

for (const path of SMOKE_PAGES) {
  test(`a11y: ${path} sin violaciones serious/critical`, async ({ page }) => {
    await page.goto(path);
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    const graves = results.violations.filter(
      (v) => v.impact === 'serious' || v.impact === 'critical'
    );
    // El mensaje de error incluye el detalle completo para no tener que re-correr localmente
    expect(graves, JSON.stringify(graves, null, 2)).toEqual([]);
  });
}
```

`withTags` limita el análisis a las reglas WCAG A/AA — coherente con el nivel objetivo del handbook (AA, no AAA). Las páginas detrás de auth reutilizan el estado de sesión del smoke (setup de auth compartido — ver el documento de E2E de esta carpeta).

Detalles operativos del mismo gate:

- **Estados, no solo páginas:** **[RECOMMENDED]** el análisis se repite con los estados abiertos que la URL sola no muestra — modal principal abierto, dropdown desplegado, formulario con errores visibles. axe solo ve el DOM del momento; un modal sin nombre accesible es invisible para el gate si nunca se abre. Se implementa como pasos extra en el mismo spec (`abrir modal → new AxeBuilder(...).analyze()`), no como páginas nuevas.
- **Widgets de terceros:** si un embed externo (Turnstile, un chat de soporte) genera violaciones que no se pueden corregir, se excluye con `.exclude('#selector-del-widget')` **más un comentario con el motivo y fecha** — la exclusión silenciosa es cómo los gates se vacían de contenido. Lo propio nunca se excluye.
- **`moderate`/`minor` no desaparecen:** el reporte completo de axe se publica como artifact del run de CI; en la pasada trimestral (1.2) se revisan los `moderate` acumulados. No bloquean, pero tampoco se pierden.

### 1.2 Qué detecta axe y qué no — el límite se declara, no se disimula

**[REQUIRED]** Se asume explícitamente que axe (y cualquier linter automático) detecta **~30–40% de los problemas reales de accesibilidad** — el mismo número que ya declara `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 10. Lo que el gate automático **sí** cubre:

| Detectable por axe | Regla origen |
|---|---|
| Contraste insuficiente (4.5:1 / 3:1) | `FRONTEND_COLOR_CONTRAST_STANDARD.md` §5 |
| Inputs sin label asociado | `FRONTEND_ACCESSIBILITY_STANDARD.md` §9 |
| `role`/ARIA inválido o contradictorio | `FRONTEND_ACCESSIBILITY_STANDARD.md` §5 |
| Landmarks/estructura HTML rota | `FRONTEND_HTML_STRUCTURE_STANDARD.md` |
| Imágenes sin `alt` | `FRONTEND_ACCESSIBILITY_STANDARD.md` §7 |

Lo que **ningún** gate automático puede evaluar — y por eso **no se finge que está automatizado**:

- Si el **orden de foco** tiene sentido para la tarea (axe ve que todo es enfocable, no si el orden ayuda).
- Si el **texto del `alt`** describe algo útil (axe ve que existe, no que sea sensato).
- La **experiencia real con lector de pantalla**: qué se anuncia, en qué orden, y si comunica lo que el usuario necesita.

**[REQUIRED]** Eso no-detectable va a un **checklist manual trimestral corto** (30–45 min, no una auditoría): (1) navegar los 2–3 flujos críticos solo con teclado; (2) recorrer el flujo principal con NVDA (Windows) o VoiceOver (Mac); (3) leer en voz alta los `alt` de las imágenes con significado y preguntarse si describen algo. El resultado se anota como issue si algo falla — es la validación de `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 10 con calendario, no una regla nueva.

**Por qué trimestral y no por PR:** el paso manual por PR no se sostiene para un dev solo — se degradaría a un checkbox mentiroso. Trimestral es la frecuencia máxima honesta, y la superficie de UI de un SaaS pequeño no cambia tan rápido como para dejar huecos grandes entre pasadas.

### 1.3 Test de navegación por teclado en flujos críticos

**[REQUIRED]** Regla en `FRONTEND_ACCESSIBILITY_STANDARD.md` sección 3 (todo alcanzable con teclado, orden natural del DOM, sin `tabindex` positivo) — **gate aquí:** un test de Playwright que recorre con `Tab` el formulario de login y el de registro y verifica que el orden de foco coincide con el orden visual/lógico esperado. Corre por PR.

```ts
// e2e/keyboard-nav.spec.ts
import { test, expect } from '@playwright/test';

test('login: tab order lógico y submit con Enter', async ({ page }) => {
  await page.goto('/login');
  const ordenEsperado = ['email', 'password', 'toggle-password', 'submit', 'link-forgot'];

  for (const testId of ordenEsperado) {
    await page.keyboard.press('Tab');
    await expect(page.getByTestId(testId)).toBeFocused();
  }
  // El form se envía con Enter desde cualquier input (comportamiento nativo de <form>)
  await page.getByTestId('email').focus();
  await page.keyboard.press('Enter');
  // aserción sobre el resultado del submit según el estado del form...
});
```

**Por qué este test es distinto del de axe:** axe nunca va a fallar por un orden de tabulación absurdo si técnicamente todo es enfocable. Este test congela el orden correcto como contrato: si un refactor de layout reordena el DOM y rompe el orden de foco, el gate lo ve — es exactamente la clase de regresión silenciosa que nadie nota con mouse.

---

## 2. Gate de rendimiento

### 2.1 Lighthouse CI contra el preview build

**[REQUIRED]** Lighthouse CI corre contra el **preview build** (deploy de preview de Cloudflare Pages, o `vite preview` servido en CI — nunca el dev server, que no minifica ni comprime). Umbrales mínimos por categoría, en modo `error` (bloquean):

| Categoría | Umbral | Objetivo real detrás del número |
|---|---|---|
| Performance | ≥ 90 | Proxy de laboratorio de Core Web Vitals — LCP < 2.5s, CLS < 0.1, INP < 200ms (`FRONTEND_ENGINEERING_STANDARD.md` §11.4). Un score ≥90 en condiciones de throttling de Lighthouse implica con alta probabilidad CWV "good" en campo para un SaaS servido desde CDN. Nota: Lighthouse (lab) no mide INP directamente — usa TBT como proxy de interactividad; INP real se observa en campo. |
| Accessibility | ≥ 95 | Redundante a propósito con el gate 1.1 (doble red: axe standalone + axe embebido en Lighthouse). 95 y no 100 porque algunos puntos del score de Lighthouse dependen de heurísticas con falsos positivos; las violaciones graves ya las bloquea 1.1 en cero. |
| Best Practices | ≥ 95 | Captura errores de consola, APIs deprecadas, imágenes con aspect ratio roto, falta de HTTPS en recursos — cosas que otros gates no miran. |
| SEO | ≥ 90 | Un SaaS vive de su landing indexable: meta description, títulos, links rastreables. 90 tolera los puntos que dependen del contenido de la página concreta. |

**[REQUIRED]** Las assertions van en **modo `error` con umbral absoluto**, no como comparación contra el run anterior. "El score bajó 1 punto" no es una señal accionable (ver 2.3, variabilidad); "Performance cayó debajo de 90" sí lo es. El gate protege un piso, no persigue deltas.

**Implementación (`lighthouserc.json`):**

```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["http://localhost:4173/", "http://localhost:4173/login"],
      "startServerCommand": "npm run preview"
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9, "aggregationMethod": "median" }],
        "categories:accessibility": ["error", { "minScore": 0.95, "aggregationMethod": "median" }],
        "categories:best-practices": ["error", { "minScore": 0.95, "aggregationMethod": "median" }],
        "categories:seo": ["error", { "minScore": 0.9, "aggregationMethod": "median" }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500, "aggregationMethod": "median" }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1, "aggregationMethod": "median" }]
      }
    }
  }
}
```

Las dos últimas assertions atan el gate a las métricas de CWV directamente, no solo al score compuesto — un score de 90 con LCP de 3s es posible y no es aceptable. (Los nombres exactos de audit-ids y `aggregationMethod` — verificar en docs oficiales de `@lhci/cli` al configurar; la semántica de arriba es la regla.)

### 2.2 Presupuesto de bundle

**[REQUIRED]** Regla origen en `FRONTEND_ENGINEERING_STANDARD.md` §11.1 (medir el bundle, no asumirlo) — **gate aquí:** el presupuesto se hace ejecutable con `size-limit` (o equivalente que mida el output real del build, gzip/brotli). Umbral inicial: **JS inicial ≤ 200 KB gzip** (el chunk de entrada + vendor compartido que se descarga antes del primer render, sin contar rutas lazy). Corre por PR.

**Por qué ~200 KB:** el objetivo real es que la app sea interactiva rápido en un móvil medio con red regular (3G rápido / 4G débil, el escenario de throttling de Lighthouse: ~1.6 Mbps down, CPU x4 más lenta). A ese ritmo, 200 KB gzip son ~1s de descarga más el costo real que domina en móvil: descomprimir, parsear y ejecutar ~600–800 KB de JS resultante. Por encima de eso, el presupuesto de LCP < 2.5s / TBT bajo se vuelve muy difícil de cumplir. Es una heurística recalibrable (formato del handbook §3): si el gate 2.1 pasa holgado con 220 KB medidos, se sube el límite con esa evidencia — lo que no se negocia es que el número exista y bloquee.

**Implementación (`package.json`):**

```json
{
  "size-limit": [
    {
      "name": "JS inicial (entry + vendor)",
      "path": "dist/assets/index-*.js",
      "limit": "200 KB",
      "gzip": true
    }
  ],
  "scripts": { "size": "size-limit" }
}
```

El glob debe cubrir los chunks que Vite carga en el HTML inicial (no los de `import()` dinámico). Si el naming de chunks del proyecto difiere, se ajusta el `path` — verificar contra el `dist/index.html` real qué scripts se cargan eager.

### 2.3 Variabilidad de Lighthouse en CI

**[REQUIRED]** Todo umbral de Lighthouse se evalúa sobre la **mediana de 3 runs** (`numberOfRuns: 3` + `aggregationMethod: "median"`), nunca sobre un run único.

**Por qué:** el score de Performance en un runner de CI compartido varía ±5 puntos entre runs idénticos (ruido de CPU del runner, red, GC). Con un solo run, un build idéntico pasa hoy y falla mañana — y un gate que falla aleatoriamente se deja de respetar (principio 0.1). La mediana de 3 elimina el outlier sin triplicar demasiado el costo. Si aún con mediana el gate "flakea" cerca del umbral, la respuesta es mejorar el margen real de la app o ajustar el umbral con justificación — no re-correr hasta que pase.

### 2.4 El laboratorio no es el campo

**[RECOMMENDED]** Nightly, el mismo `lighthouserc` corre contra la **URL de producción real** (no bloquea nada — genera reporte/alerta). El run de PR mide el build aislado; el de producción captura lo que el PR no ve: headers de cache reales del CDN, peso acumulado de scripts de terceros (analytics), certificados, redirects.

**Por qué además y no en vez:** el gate de PR atribuye la regresión a un cambio concreto (accionable); el nightly de producción detecta degradación que no vino de ningún PR (un script de terceros que engordó, un cambio de config en el dashboard de Cloudflare). Son dos preguntas distintas: "¿este PR empeora algo?" vs "¿producción sigue sana?". Para INP real — que Lighthouse no mide, ver 2.1 — la fuente es campo: CrUX (si el sitio tiene tráfico suficiente) o el RUM básico de Cloudflare Web Analytics, revisado en la misma pasada trimestral de 1.2, no un gate de CI.

---

## 3. Gate de seguridad de build

> Las reglas de seguridad viven en `05_Security/SECURITY_ENGINEERING_STANDARD.md` — este gate las verifica, no las redefine.

### 3.1 npm audit con política diferenciada

**[REQUIRED]** Regla en `05_Security/SECURITY_ENGINEERING_STANDARD.md` §10 (hallazgo high/critical en producción se resuelve antes del siguiente deploy) — **gate aquí:** en cada PR corre `npm audit` con esta política:

```bash
# Bloquea: high/critical en dependencias de PRODUCCIÓN
npm audit --omit=dev --audit-level=high

# Informa (no bloquea): todo lo demás, incluidas devDependencies
npm audit || true
```

El audit corre sobre el lockfile comiteado tras `npm ci` (nunca `npm install` en CI — regla en `05_Security/SECURITY_ENGINEERING_STANDARD.md` §10): auditar un árbol distinto del que se despliega es auditar otra aplicación.

**Por qué la distinción prod vs dev:** una vulnerabilidad en una dependencia de producción es código explotable que corre en el navegador del usuario o en el Worker — bloquea. Una vulnerabilidad en una devDependency (el bundler, un plugin de ESLint) corre solo en la máquina de desarrollo y en CI: el riesgo real existe (supply chain del build) pero es de otra clase y su ruido es enorme — la mayoría de advisories de dev-deps son ReDoS en herramientas que procesan input propio. Si bloqueara, el gate estaría rojo semanas por cosas sin fix upstream y se apagaría. Dev-deps quedan como warning visible + la revisión de Dependabot (sección 4.1).

### 3.2 gitleaks en cada PR

**[REQUIRED]** En cada PR corre **gitleaks** sobre los commits del PR (el diff contra la base, no todo el historial en cada run):

```bash
# gitleaks v8.19+: subcomando `git`; en versiones previas era `detect --log-opts`
# (verificar sintaxis exacta en docs oficiales según versión instalada)
gitleaks git --log-opts="origin/main..HEAD" --redact --exit-code 1
```

**Por qué además del secret scanning de GitHub** (`07_DevOps/GITHUB_STANDARD.md` §05): son capas complementarias, no redundancia inútil — push protection puede no estar disponible según plan en repos privados, y sus patrones no cubren secretos custom (el header secreto de un webhook propio, por ejemplo). gitleaks corre con las reglas propias del repo y falla el PR antes del merge. Si detecta algo que ya se pusheó: el secreto está comprometido — aplica el runbook de rotación de `GITHUB_STANDARD.md` §05 (rotar ANTES de limpiar historial), no solo borrar la línea.

```toml
# .gitleaks.toml — extiende las reglas default con los secretos propios del stack
[extend]
useDefault = true

[[rules]]
id = "supabase-service-role"
description = "Supabase service_role key referenciada fuera de wrangler secrets"
regex = '''service_role["'\s:=]+ey[A-Za-z0-9_-]{20,}'''

[[rules]]
id = "webhook-shared-secret"
description = "Header secreto de webhooks propios (05_Security §09)"
regex = '''X-Webhook-Secret["'\s:=]+[A-Za-z0-9+/=_-]{16,}'''

# allowlist para falsos positivos CONCRETOS (por path + motivo), nunca patrones enteros
[allowlist]
paths = ['''e2e/fixtures/fake-jwt\.ts''']  # JWT de prueba, no es credencial real
```

La allowlist se usa por archivo puntual con motivo en comentario — deshabilitar una regla entera para callar un falso positivo repite el anti-patrón de 1.1 (exclusión silenciosa que vacía el gate).

### 3.3 Headers de seguridad verificados en staging

**[RECOMMENDED]** Regla (el set de headers y sus valores) en `05_Security/SECURITY_ENGINEERING_STANDARD.md` §06 — **gate aquí:** un check nightly contra el deploy de staging/preview que verifica que los headers **realmente salen** en las respuestas, porque un `_headers` mal ubicado o un refactor del helper de respuesta los apaga en silencio y ningún test unitario lo nota.

```bash
#!/usr/bin/env bash
# scripts/check-headers.sh <url-staging>
URL="$1"
HEADERS=$(curl -s -D - -o /dev/null "$URL")
FALTAN=0
for h in "strict-transport-security" "x-content-type-options" \
         "referrer-policy" "content-security-policy" "permissions-policy"; do
  if ! echo "$HEADERS" | grep -qi "^$h:"; then
    echo "FALTA header: $h"; FALTAN=1
  fi
done
exit $FALTAN
```

El script verifica **presencia**; los **valores** correctos son los de la tabla de `05_Security` §06 — si se quiere verificar valores, se comparan contra esa tabla como fuente única (no se duplican aquí, para que un cambio en el estándar de seguridad no deje este gate verificando valores viejos). Equivalente en Playwright: un test que hace `page.goto()` y asserta sobre `response.headers()` — misma regla, otra capa 2.

### 3.4 Cero secretos server-side en el bundle del cliente

**[REQUIRED]** Regla en `FRONTEND_ENGINEERING_STANDARD.md` §12.2 (cero secretos en el bundle) y `05_Security/SECURITY_ENGINEERING_STANDARD.md` §03 (gestión de secretos) — **gate aquí:** tras cada build de PR, un grep del output (`dist/`) buscando patrones de secretos conocidos del stack. Vite solo expone variables con prefijo `VITE_`, pero ese mecanismo no protege contra el error real: pegar una key directamente en el código, o prefijar con `VITE_` algo que nunca debió ser público.

```bash
#!/usr/bin/env bash
# scripts/check-bundle-secrets.sh — corre después de `npm run build`
set -u
PATTERNS=(
  'service_role'                          # rol server-side de Supabase — NUNCA en cliente
  'sk_live_[A-Za-z0-9]+'                  # secret keys estilo Stripe
  'sk_test_[A-Za-z0-9]+'
  'whsec_[A-Za-z0-9]+'                    # signing secrets de webhooks (Svix/Resend)
  're_[A-Za-z0-9_]{20,}'                  # API keys de Resend
  'AKIA[0-9A-Z]{16}'                      # AWS access key id
  'ghp_[A-Za-z0-9]{36}'                   # GitHub PAT
  '-----BEGIN[A-Z ]*PRIVATE KEY'          # llaves privadas PEM
)
FOUND=0
for p in "${PATTERNS[@]}"; do
  if grep -rIEn "$p" dist/ 2>/dev/null; then
    echo "POSIBLE SECRETO EN EL BUNDLE (patrón: $p)"; FOUND=1
  fi
done
exit $FOUND
```

**Por qué grep del output y no del código fuente:** el bundle es lo que de verdad llega al navegador — un secreto puede entrar por una variable de entorno inyectada en build, no solo por código fuente. Nota deliberada: la `anon key` (publishable) de Supabase **sí** puede aparecer en el bundle — es pública por diseño (la seguridad real es RLS, `05_Security` §05); por eso el patrón busca `service_role` y no cualquier key de Supabase. Los patrones se mantienen como lista viva: al integrar un proveedor nuevo con secret key, su prefijo se agrega al script en el mismo PR.

---

## 4. Gate de dependencias

### 4.1 Vulnerabilidades conocidas — Dependabot

Ya definido en [07_DevOps/GITHUB_STANDARD.md](../../07_DevOps/GITHUB_STANDARD.md) §06 (alerts [REQUIRED], security updates y política de auto-merge) — este documento no lo repite. La relación con 3.1: Dependabot avisa de CVEs nuevos en dependencias ya instaladas (continuo); `npm audit` bloquea la entrada de vulnerabilidades en el momento del PR. Se necesitan ambos.

### 4.2 Código, exports y dependencias muertas — knip

**[REQUIRED]** `knip` corre por PR con umbral: **cero unused exports, archivos muertos o dependencias no usadas nuevos** respecto al baseline. Si el proyecto arranca con deuda existente, esa deuda se congela en el reporte inicial y el gate solo bloquea lo que se agrega — la deuda vieja se paga aparte, no bloquea PRs ajenos a ella.

**Por qué es un gate y no una limpieza ocasional:** un export muerto es superficie de mantenimiento gratis-negativa: se refactoriza, se testea mentalmente y se carga en el bundle sin que nadie lo use. Una dependencia muerta en `package.json` es superficie de supply chain (cada paquete instalado es código de terceros con todos los permisos — `05_Security` §10) que además sigue generando alertas de Dependabot por código que ni corre. Para un dev solo, knip es el "segundo par de ojos" que nota lo que quedó huérfano tras un refactor.

```jsonc
// knip.json — mínimo para Vite + React + Workers
{
  "entry": ["src/main.tsx", "worker/src/index.ts"],
  "project": ["src/**/*.{ts,tsx}", "worker/src/**/*.ts"]
}
```

```bash
npx knip --production   # exit code != 0 si hay hallazgos → falla el job
```

### 4.3 Dependencias duplicadas

**[RECOMMENDED]** Nightly (no por PR): `npm dedupe --dry-run` — si reporta duplicados colapsables, se abre issue y se ejecuta `npm dedupe` real en un PR propio. Complemento: `npx vite-bundle-visualizer` (o `rollup-plugin-visualizer`) cuando el gate 2.2 falle, para ver *qué* infló el bundle — dos copias de una librería por rangos de versión incompatibles es la causa clásica.

**Por qué warning y no bloqueo:** un duplicado no rompe nada hoy — cuesta KB del presupuesto 2.2, y ese gate ya bloquea el síntoma con número. Bloquear por el diagnóstico además del síntoma sería castigar dos veces lo mismo.

### 4.4 Licencias con allowlist

**[REQUIRED]** Toda dependencia de **producción** tiene licencia dentro de la allowlist: **MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD**. Cualquier otra (GPL/AGPL/LGPL, SSPL, BUSL, "UNLICENSED", licencias custom) bloquea hasta decisión explícita documentada. Corre por PR (es barato).

```bash
# license-checker original está poco mantenido; usar el fork mantenido
# license-checker-rseidelsohn (verificar en npm cuál es el fork vivo al configurar)
npx license-checker-rseidelsohn --production \
  --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC;0BSD"
# exit code != 0 si algún paquete queda fuera de la allowlist
```

**Por qué importa aunque seas dev solo:** (1) un SaaS **distribuye y monetiza** el código — AGPL en una dependencia puede obligar a liberar el código propio del servicio, y "no sabía" no es defensa; (2) si el producto algún día se vende o recibe inversión, el due diligence de licencias es checklist estándar y limpiarlo retroactivamente (reemplazar una dependencia enraizada) cuesta 100x más que bloquearla al entrar; (3) el gate cuesta un comando — la asimetría costo/riesgo es total. Las devDependencies quedan fuera del gate: no se distribuyen con el producto.

---

## 5. Gate de calidad de código

### 5.1 Typecheck estricto

Ya es gate bloqueante del pipeline — definido en [03_CI_CD.md](../Pipelines/03_CI_CD.md) (y exigido por `07_DevOps/DEPLOY_AND_FAILURES_STANDARD.md` §01: typecheck + tests + build como CI mínimo). No se repite aquí; se menciona solo para que la tabla final (sección 6) muestre el cuadro completo de gates.

### 5.2 ESLint como verificador del handbook

**[REQUIRED]** ESLint no es "estilo": las reglas se eligen para detectar automáticamente lo que el handbook ya prohíbe en prosa. Configuración mínima de este gate (flat config, `eslint.config.js`):

```js
// Fragmento — solo las reglas de ESTE gate; el resto de la config vive en el repo
export default [
  {
    rules: {
      // REGLA: ninguna función supera ~10 caminos de ejecución independientes.
      'complexity': ['error', { max: 10 }],

      // REGLA: funciones cortas; el límite duro real (~200 líneas/componente)
      // vive en FRONTEND_ENGINEERING_STANDARD — esto avisa antes.
      'max-lines-per-function': ['warn', {
        max: 80, skipBlankLines: true, skipComments: true
      }],

      // REGLA: números con significado llevan nombre.
      'no-magic-numbers': ['warn', {
        ignore: [-1, 0, 1, 2, 100],
        ignoreArrayIndexes: true,
        ignoreDefaultValues: true,
        enforceConst: true
      }],

      // REGLA: anidamiento profundo = misma enfermedad que complejidad alta,
      // vista desde la indentación. 4 niveles ya pide extraer función/early return.
      'max-depth': ['warn', { max: 4 }],

      // REGLA: >4 parámetros posicionales = pedir un objeto de opciones.
      'max-params': ['warn', { max: 4 }],

      // REGLA: los barrel files son la causa #1 de ciclos (FRONTEND_ENGINEERING_
      // STANDARD §imports) — prohibir importar del barrel propio dentro del mismo módulo.
      'no-restricted-imports': ['error', {
        patterns: [{ group: ['**/index'], message: 'Importa el archivo concreto, no el barrel.' }]
      }]
    }
  }
];
```

`max-depth` y `max-params` van como `warn` por la misma lógica que `max-lines-per-function`: son proxies con excepciones legítimas. `no-restricted-imports` va como `error` porque es prevención directa del gate 5.3 — mejor que el lint señale el import problemático en el editor a que madge falle en CI con el ciclo ya formado.

**Por qué complejidad 10 como `error`:** la complejidad ciclomática es el número de caminos independientes = el número mínimo de tests para cubrir la función. Por encima de ~10, la función es efectivamente intesteable de forma exhaustiva y es donde se esconden los branches que nadie probó (heurística clásica de McCabe; el valor exacto es recalibrable, el objetivo — funciones testeables — no). **Por qué `max-lines-per-function` es `warn` y no `error`:** líneas es un proxy mucho más ruidoso que complejidad (un switch de mapeo largo y trivial es líneas sin complejidad); como error generaría refactors artificiales para callar al linter. **Por qué `no-magic-numbers` "pragmático":** la lista `ignore` existe porque `arr.length - 1`, índices y porcentajes son legítimos — la versión estricta de esta regla es la razón #1 por la que la gente la apaga entera; mejor pragmática y encendida que pura y apagada.

### 5.3 Código muerto y dependencias circulares

**[REQUIRED]** Dos verificaciones bloqueantes por PR:

1. **Código muerto:** knip — ya definido en 4.2 (mismo run cubre exports muertos y dependencias muertas; no se corre dos veces).
2. **Dependencias circulares:** `madge --circular` sobre `src/` — umbral: **cero ciclos**.

```bash
npx madge --circular --extensions ts,tsx src/
# exit code != 0 si encuentra al menos un ciclo → falla el job
```

**Por qué cero y no "pocos":** un ciclo de imports es el punto donde el orden de evaluación de módulos se vuelve impredecible (`undefined` en tiempo de import según quién cargó primero — bugs que solo aparecen en el build de producción), rompe el tree-shaking y es la grieta por la que la arquitectura de capas se erosiona: el primer ciclo legitima el segundo. `FRONTEND_ENGINEERING_STANDARD.md` ya señala los barrel files como causa #1 de ciclos — este gate es su verificación automática. A diferencia de knip (que tolera baseline), aquí no hay deuda tolerable: un proyecto que hoy tiene cero ciclos debe seguir en cero, y es mucho más barato deshacer el ciclo en el PR que lo introduce que un año después.

---

## 6. Tabla resumen de gates

| # | Gate | Herramienta | Umbral | Cuándo corre | Si falla |
|---|---|---|---|---|---|
| 1.1 | Accesibilidad automática | axe-core (`@axe-core/playwright`) en páginas del smoke | 0 violaciones `serious`/`critical` (WCAG A/AA) | PR | **Bloquea** |
| 1.2 | Accesibilidad no automatizable | Checklist manual (teclado + lector de pantalla + alt) | Flujos críticos revisados | Trimestral | Issue, no bloquea CI |
| 1.3 | Navegación por teclado | Playwright (tab order login/registro) | Orden de foco = orden esperado | PR | **Bloquea** |
| 2.1 | Lighthouse | `@lhci/cli` contra preview build | Perf ≥90, A11y ≥95, BP ≥95, SEO ≥90; LCP ≤2500ms, CLS ≤0.1 — mediana de 3 runs | PR | **Bloquea** |
| 2.2 | Presupuesto de bundle | size-limit | JS inicial ≤ 200 KB gzip | PR | **Bloquea** |
| 2.4 | Lighthouse producción | `@lhci/cli` contra URL de producción | Mismos umbrales de 2.1, informativo | Nightly | Issue/alerta |
| 3.1 | Vulnerabilidades npm (prod) | `npm audit --omit=dev --audit-level=high` | 0 high/critical en prod deps | PR | **Bloquea** |
| 3.1b | Vulnerabilidades npm (dev) | `npm audit` completo | — | PR | Warning |
| 3.2 | Secretos en el diff | gitleaks | 0 hallazgos | PR | **Bloquea** |
| 3.3 | Headers de seguridad | `check-headers.sh` (curl) contra staging | Set completo de `05_Security` §06 presente | Nightly | Issue/alerta |
| 3.4 | Secretos en bundle cliente | `check-bundle-secrets.sh` (grep de `dist/`) | 0 patrones de secretos server-side | PR | **Bloquea** |
| 4.1 | CVEs continuos | Dependabot (ver `GITHUB_STANDARD.md` §06) | — | Continuo | Alerta/PR automático |
| 4.2 | Código/deps muertas | knip | 0 hallazgos nuevos sobre baseline | PR | **Bloquea** |
| 4.3 | Dependencias duplicadas | `npm dedupe --dry-run` | Informativo | Nightly | Warning/issue |
| 4.4 | Licencias | license-checker (fork mantenido), allowlist | 0 prod deps fuera de MIT/Apache-2.0/BSD/ISC/0BSD | PR | **Bloquea** |
| 5.1 | Typecheck estricto | tsc (ver `03_CI_CD.md`) | 0 errores | PR | **Bloquea** |
| 5.2 | Reglas de handbook en lint | ESLint (`complexity` error 10; resto warn) | 0 errores; warnings visibles | PR | **Bloquea** (solo errors) |
| 5.3 | Dependencias circulares | `madge --circular` | 0 ciclos | PR | **Bloquea** |

Regla de lectura de la tabla: **"Bloquea" significa status check requerido en el PR** (mecánica en `03_CI_CD.md` y `GITHUB_STANDARD.md`); "Warning" significa visible en el log/reporte del run sin frenar el merge; "Nightly" significa que el fallo genera un issue o alerta, no un PR rojo.

**[RECOMMENDED]** Orden de ejecución por costo: los gates baratos y deterministas fallan primero — lint/typecheck (segundos) → knip/madge/licencias/audit (segundos) → build + grep de bundle + size-limit (~1 min) → Playwright axe/teclado (minutos) → Lighthouse (el más caro y el único con varianza). **Por qué:** el feedback loop de un dev solo es el recurso más escaso — no tiene sentido esperar 5 minutos de Lighthouse para enterarse de un error de tipos que el typecheck habría dado en 10 segundos. El detalle de jobs y paralelización vive en `03_CI_CD.md`; aquí solo el principio.

---

## 7. Qué hacer cuando un gate falla (y qué no es este documento)

**[REQUIRED]** Ante un gate rojo, el orden de respuesta es siempre el mismo:

1. **Arreglar la causa** — el default. El gate existe para esto.
2. **Recalibrar el umbral con evidencia y por escrito** — si el análisis muestra que el umbral era la parte equivocada (ej. el bundle pasa a 210 KB porque entró una librería justificada y Lighthouse sigue ≥90), se cambia el número **en este documento**, en el mismo PR, con el porqué. El umbral vive aquí, no en 20 configs dispersas con valores distintos.
3. **Nunca** deshabilitar el gate, marcarlo como no-requerido "por ahora", o re-correr hasta que pase. Un gate apagado temporalmente es un gate apagado (principio 0.1) — y para un dev solo no hay un segundo revisor que note que sigue apagado seis meses después.

Ejemplos de respuesta correcta a los fallos más comunes: bundle excedido → ¿la ruta nueva es lazy? ¿la librería tiene alternativa liviana o import parcial? (antes de subir el límite); ciclo de madge → extraer lo compartido a un módulo tercero, no `eslint-disable`; licencia fuera de allowlist → buscar alternativa antes de evaluar aceptar la licencia.

**Qué NO cubre este documento:** los gates funcionales (tests unitarios, integración, E2E y su cobertura) viven en los demás documentos de `06_Testing`; el pipeline que ejecuta todo, en [03_CI_CD.md](../Pipelines/03_CI_CD.md); la calidad de código en tiempo de escritura (convenciones, naming, estructura), en el estándar de cada dominio. Este documento es solo el **piso no funcional medible** que separa "compila y los tests pasan" de "es desplegable".

---

## Checklist rápido

- [ ] ¿Cada gate bloquea solo lo grave/estable, con umbral absoluto (no delta) y baseline congelado para deuda vieja (sección 0)?
- [ ] ¿axe corre sobre todas las páginas del smoke y bloquea en `serious`/`critical` (no en "todo")?
- [ ] ¿Los estados no-URL (modales, dropdowns, errores de form) también pasan por axe; exclusiones de terceros documentadas con motivo?
- [ ] ¿El checklist manual trimestral (teclado, lector de pantalla, alt) está calendarizado — no fingido como automatizado?
- [ ] ¿Hay test de tab order en Playwright para login/registro?
- [ ] ¿Lighthouse corre contra preview build, con mediana de 3 runs y assertions absolutas en modo error (Perf ≥90, A11y ≥95, BP ≥95, SEO ≥90, LCP/CLS explícitos)?
- [ ] ¿size-limit bloquea si el JS inicial supera 200 KB gzip?
- [ ] ¿`npm audit` bloquea high/critical solo en prod deps, y dev-deps quedan como warning?
- [ ] ¿gitleaks corre en cada PR sobre el diff; si encuentra algo pusheado se rota primero (runbook `GITHUB_STANDARD.md` §05)?
- [ ] ¿Los headers de `05_Security` §06 se verifican contra staging (nightly), presencia contra la tabla fuente?
- [ ] ¿El build output se escanea por patrones de secretos server-side (`service_role`, `sk_live_`, `whsec_`, PEM...) antes de desplegar?
- [ ] ¿knip en cero-hallazgos-nuevos y madge en cero ciclos, ambos bloqueantes?
- [ ] ¿Licencias de prod deps dentro de la allowlist (MIT/Apache-2.0/BSD/ISC/0BSD)?
- [ ] ¿ESLint verifica lo que el handbook prohíbe (complejidad ≤10 error; max-lines y magic numbers como warn pragmático)?
- [ ] ¿Lighthouse corre además nightly contra producción (informativo), e INP real se mira en campo (CrUX/RUM), no en lab?
- [ ] ¿Los gates corren en orden de costo: lint/typecheck → análisis estático → build → Playwright → Lighthouse?
- [ ] ¿La tabla de la sección 6 coincide con los status checks realmente configurados en `03_CI_CD.md`?
- [ ] ¿Ante un gate rojo se arregló la causa o se recalibró el umbral por escrito en este documento — nunca se apagó el gate ni se re-corrió hasta que pasara?
- [ ] ¿Los umbrales numéricos viven solo aquí (fuente única) y las configs del repo los reflejan, no al revés?
