---
title: "Guía Operativa de Pruebas de Carga y Rendimiento con Grafana k6"
category: 06_Testing
doc_type: estandar
tags: [testing, k6, load-testing, stress-testing, performance, thresholds, grafana, cloudflare]
summary: "Estándar y guía operativa de pruebas de carga con Grafana k6: instalación en Windows y CI/CD, definición de umbrales P95/P99, diseño de escenarios (smoke, load, stress, spike) y suite lista para producción sobre Cloudflare Workers, Pages y APIs."
keywords: [k6, load-testing, stress-testing, thresholds, vus, latency, grafana, performance, cloudflare]
updated: 2026-10-05
status: current
---

# 08 — GUÍA OPERATIVA DE PRUEBAS DE CARGA Y RENDIMIENTO CON GRAFANA K6

> Documento del dominio Testing (06). Sigue las convenciones de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
> Complementa a [ADVANCED_TESTING_STANDARD.md](../ADVANCED_TESTING_STANDARD.md) (`TEST-001`) y a [07_AUTOMATION_GUIDE.md](07_AUTOMATION_GUIDE.md).
> Este documento define el estándar operativo para validar la estabilidad y latencia de endpoints, Cloudflare Workers, aplicaciones SPA/SSR y backends bajo condiciones de concurrencia real.

---

## REGLAS INQUEBRANTABLES

**[REQUIRED] K6-001: Todo endpoint público o API debe certificar P95 < 400ms y tasa de error < 1% bajo carga esperada.**
Ninguna API o Worker pasa a producción si en una prueba de carga base (150% del tráfico pico proyectado) el percentil 95 supera los 400 ms o si la tasa de fallos (`http_req_failed`) supera el 1.0%.

> **Por qué:** Un servicio que responde en 80 ms con 1 usuario puede sufrir saturación de CPU, cuellos de botella en base de datos o throttling en Cloudflare Workers al recibir 50 usuarios concurrentes. Los umbrales automáticos (`thresholds`) garantizan que el pipeline falle antes de impactar usuarios reales.

**[REQUIRED] K6-002: Las pruebas de carga deben usar datos sintéticos y no alterar estados irreversibles de producción.**
Las pruebas de escritura masiva (POST/PUT/DELETE) jamás deben ejecutarse sobre bases de datos de clientes con datos reales. Se deben utilizar endpoints de lectura, réplicas de staging, o payloads aislados identificados con cabeceras `X-Load-Test: true`.

> **Por qué:** Disparar 500 VUs ejecutando compras o mutaciones reales ensucia el inventario, distorsiona las métricas de Stripe/facturación y agota cuotas de proveedores externos.

**[RECOMMENDED] K6-003: Todo test debe incluir simulación de comportamiento humano (*think time*) y ramp-up progresivo.**
No bombardear con tráfico en bloque de 0 a 1000 usuarios en 1 segundo a menos que se trate específicamente de un *Spike Test*. Usar etapas de calentamiento (`stages` con ramp-up) y pausas con `sleep(Math.random() * 2 + 1)`.

> **Por qué:** Los usuarios reales no hacen clics a velocidad de microsegundos de forma sincronizada. El tráfico escalonado permite observar en qué percentil exacto empieza a degradarse la latencia antes del fallo catastrófico.

**[RECOMMENDED] K6-004: Versionar los scripts de prueba dentro del repositorio en `tests/load/`.**
Los archivos de k6 deben llamarse `tests/load/<flujo>.load.js` y añadirse a los scripts de `package.json` (`"test:load": "k6 run tests/load/api.load.js"`).

> **Por qué:** La memoria de las pruebas de estrés debe pertenecer al código fuente del proyecto, permitiendo comparar el rendimiento entre versiones y commits.

---

## 1. INSTALACIÓN Y CONFIGURACIÓN

### 1.1 En Windows (Entorno Local)
Instalación mediante PowerShell (vía binario oficial o winget):

```powershell
# Opción 1: Winget
winget install --id GrafanaLabs.k6 --silent

# Opción 2: Binario portable en AppData Programs
$k6Dir = "$env:LOCALAPPDATA\Programs\k6"
& "$k6Dir\k6.exe" version
```

### 1.2 En CI/CD (GitHub Actions)
```yaml
# .github/workflows/load-test.yml
name: Load Testing (k6)
on:
  workflow_dispatch:
  schedule:
    - cron: '0 4 * * 1' # Cada lunes a las 4 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup k6
        uses: grafana/setup-k6-action@v1
      - name: Run k6 load test
        run: k6 run tests/load/smoke.load.js
        env:
          TARGET_URL: ${{ secrets.PRODUCTION_OR_STAGING_URL }}
```

---

## 2. ARQUITECTURA DE UN TEST DE K6

Un script de k6 se compone de 4 bloques fundamentales:
1. **`options`**: Configuración de VUs (Virtual Users), duración, `stages` y `thresholds`.
2. **`setup()` (Opcional)**: Ejecución de arranque (ej. login para obtener un token JWT de prueba).
3. **`default function(data)`**: El bucle de ejecución ejecutado por cada VU repetidamente.
4. **`teardown(data)` (Opcional)**: Limpieza tras terminar la prueba.

---

## 3. PLANTILLAS DE PRUEBA OFICIALES

### 3.1 Smoke Test (Validación Rápida de Salud)
> **Objetivo:** 1 a 5 usuarios durante 30 segundos. Verifica que el sistema responda con código 200 y que la configuración no esté rota.

```javascript
// tests/load/smoke.load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.01'],    // Errores < 1%
    http_req_duration: ['p(95)<350'],  // 95% de requests en < 350ms
  },
};

export default function () {
  const target = __ENV.TARGET_URL || 'https://api.tu-dominio.com';
  const res = http.get(target);

  check(res, {
    'código de respuesta 200': (r) => r.status === 200,
    'tiempo de respuesta < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### 3.2 Load Test Estándar (Carga Sostenida)
> **Objetivo:** Simula el tráfico normal y picos esperados con ramp-up, meseta y ramp-down.

```javascript
// tests/load/standard.load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp-up a 20 VUs
    { duration: '1m',  target: 50 },  // Subida a 50 VUs (carga objetivo)
    { duration: '1m',  target: 50 },  // Mantener meseta
    { duration: '20s', target: 0 },   // Ramp-down a 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<400', 'p(99)<800'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const target = __ENV.TARGET_URL || 'https://api.tu-dominio.com';
  const params = {
    headers: {
      'Accept': 'application/json',
      'User-Agent': 'k6-load-testing-suite/1.0',
    },
  };

  const res = http.get(target, params);

  check(res, {
    'status es 200': (r) => r.status === 200,
    'cuerpo no vacío': (r) => r.body && r.body.length > 0,
  });

  // Think time humano realista (entre 1s y 2.5s)
  sleep(Math.random() * 1.5 + 1);
}
```

### 3.3 Spike Test (Pico Agresivo de Tráfico)
> **Objetivo:** Evaluar si el sistema sobrevive a una avalancha súbita (ej. una notificación masiva push o campaña en redes).

```javascript
// tests/load/spike.load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Línea base
    { duration: '15s', target: 200 },  // PICO AGRESIVO repentino
    { duration: '30s', target: 200 },  // Sostener pico
    { duration: '15s', target: 10 },   // Enfriamiento rápido
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],    // En spike se tolera hasta 5% de error
    http_req_duration: ['p(95)<1000'], // Latencia esperada sube hasta 1s
  },
};

export default function () {
  const target = __ENV.TARGET_URL || 'https://api.tu-dominio.com';
  const res = http.get(target);
  check(res, { 'status no 5xx': (r) => r.status < 500 });
  sleep(0.5);
}
```

---

## 4. SUITE DE AUDITORÍA MULTIDOMINIO (CLIENTES Y APPS PROPIAS)

Para validar múltiples proyectos y Cloudflare Workers en una sola corrida:

```javascript
// tests/load/multi-domain-audit.js
import http from 'k6/http';
import { check, sleep } from 'k6';

// Listado de dominios y endpoints a auditar
const TARGETS = [
  { name: 'Dania Nails', url: 'https://stream.danianailsacademy.com' },
  { name: 'IndexGenius', url: 'https://indexgeniusacademy.com' },
  { name: 'Citoo Client', url: 'https://clientes.citoo.world' },
  { name: 'Monica Academy', url: 'https://monicarioscursos.online' },
  { name: 'PulseMarkets API', url: 'https://pulsemarkets-api.jeilincastro989.workers.dev' },
  { name: 'Camarones Panama', url: 'https://camarones-panama-worker.xworked9.workers.dev' }
];

export const options = {
  vus: 10,
  duration: '45s',
  thresholds: {
    'http_req_duration': ['p(95)<500'],
    'http_req_failed': ['rate<0.02'],
  },
};

export default function () {
  for (const item of TARGETS) {
    const res = http.get(item.url, {
      headers: { 'User-Agent': 'k6-health-check' },
      timeout: '10s'
    });

    check(res, {
      [`${item.name} responde OK (200..399)`]: (r) => r.status >= 200 && r.status < 400,
      [`${item.name} latencia aceptable`]: (r) => r.timings.duration < 600,
    });
  }

  sleep(2);
}
```

---

## 5. INTERPRETACIÓN DE MÉTRICAS CLAVE

| Métrica k6 | Significado | Meta para Producción |
|---|---|---|
| `http_req_duration` | Tiempo total de ida y vuelta (latencia) | `p(95) < 400ms`, `p(99) < 800ms` |
| `http_req_failed` | Porcentaje de respuestas 4xx y 5xx | `< 1.0%` |
| `http_req_waiting` | Tiempo de espera por el primer byte (TTFB) | `< 250ms` |
| `http_reqs` | Solicitudes totales por segundo (RPS) | Depende del objetivo de capacidad |
| `vus` | Usuarios virtuales concurrentes activos | Según el stage configurado |

---

## 6. CHECKLIST DE VERIFICACIÓN

- [ ] k6 instalado y verificado con `k6 version`.
- [ ] El script incluye `thresholds` automáticos (P95 y tasa de fallos).
- [ ] Se verifica código de estado (`check(res, { 'status es 200': ... })`).
- [ ] Se incluye `sleep()` para simular intervalos reales.
- [ ] No se mutan datos productivos de clientes ni inventario real.
- [ ] La salida en consola confirma: **todos los checks en verde y thresholds satisfechos**.
