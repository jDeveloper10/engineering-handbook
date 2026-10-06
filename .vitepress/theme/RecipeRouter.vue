<template>
  <div class="router-root">
    <!-- Header sobrio y minimalista -->
    <div class="router-header">
      <div class="router-kicker">
        <span class="kicker-dot"></span>
        <span>DECISION ROUTER // SYSTEM ONE</span>
      </div>
      <h2 class="router-heading">Ruteo de Acciones y Estándares</h2>
      <p class="router-lead">
        Localiza la arquitectura canónica para cualquier flujo entre los 281 estándares del Handbook.
      </p>
    </div>

    <!-- Barra de búsqueda tipo command bar -->
    <div class="router-search-wrapper">
      <div class="search-bar">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="11" cy="11" r="7"></circle>
          <line x1="21" y1="21" x2="16" y2="16"></line>
        </svg>
        <input
          v-model="query"
          type="text"
          placeholder="Buscar flujo (ej. login, pagos panama, bd timeout, k6, ley 81, r2)..."
          class="search-field"
          @input="onSearch"
        />
        <button v-if="query" class="clear-trigger" @click="resetQuery">Limpiar</button>
      </div>

      <!-- Chips sobrios -->
      <div class="quick-chips">
        <button
          v-for="chip in chips"
          :key="chip.id"
          class="chip-item"
          :class="{ active: currentId === chip.id }"
          @click="pickChip(chip.id)"
        >
          {{ chip.label }}
        </button>
      </div>
    </div>

    <!-- Panel de Resolución / Acción -->
    <transition name="fade" mode="out-in">
      <div v-if="activeItem" :key="activeItem.id" class="result-panel">
        <div class="panel-meta">
          <span class="meta-tag domain">{{ activeItem.domain }}</span>
          <span class="meta-tag">{{ activeItem.time }}</span>
          <span class="meta-tag risk" :class="activeItem.riskClass">Riesgo: {{ activeItem.risk }}</span>
          <span class="meta-metric">Confianza: {{ activeItem.confidence }}%</span>
        </div>

        <h3 class="panel-title">{{ activeItem.title }}</h3>
        <p class="panel-summary">{{ activeItem.summary }}</p>

        <!-- Dos columnas: Estándares y Reglas -->
        <div class="panel-grid">
          <!-- Columna: Estándares -->
          <div class="grid-col">
            <div class="col-head">Estándares Aplicables</div>
            <div class="standards-stack">
              <a
                v-for="(std, i) in activeItem.standards"
                :key="i"
                :href="std.link"
                class="std-card"
              >
                <div class="std-file">{{ std.name }}</div>
                <div class="std-note">{{ std.desc }}</div>
              </a>
            </div>
          </div>

          <!-- Columna: Reglas Inquebrantables -->
          <div class="grid-col">
            <div class="col-head">Reglas Innegociables</div>
            <div class="rules-stack">
              <div v-for="(rule, i) in activeItem.rules" :key="i" class="rule-row">
                <span class="rule-id">{{ rule.id }}</span>
                <div class="rule-text">
                  <div class="rule-req">{{ rule.req }}</div>
                  <div class="rule-reason">{{ rule.why }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Flujo Canónico -->
        <div class="flow-block">
          <div class="col-head">Flujo de Implementación Canónico</div>
          <div class="steps-flow">
            <div v-for="(step, i) in activeItem.steps" :key="i" class="flow-step">
              <div class="step-idx">{{ i + 1 }}</div>
              <div class="step-detail">
                <span class="step-name">{{ step.name }}</span>
                <span class="step-desc">{{ step.desc }}</span>
                <pre v-if="step.code" class="code-box"><code>{{ step.code }}</code></pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Gotcha Técnico -->
        <div class="gotcha-bar">
          <span class="gotcha-label">NOTA DE INGENIERÍA:</span>
          <span class="gotcha-text">{{ activeItem.gotcha }}</span>
        </div>
      </div>

      <!-- No match -->
      <div v-else-if="query" class="empty-panel">
        <p>No hay un ruteo directo precompilado para <strong>"{{ query }}"</strong>.</p>
        <div class="empty-links">
          <a href="/README">Consultar Índice de Estándares →</a>
          <a href="/AGENTS">Ver Árbol de Decisión AGENTS.md →</a>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const query = ref('')
const currentId = ref('login')

const chips = [
  { id: 'login', label: 'Auth & Login' },
  { id: 'pagos', label: 'Pagos Panamá' },
  { id: 'db-resilience', label: 'Resiliencia BD' },
  { id: 'k6', label: 'Carga K6' },
  { id: 'ley81', label: 'Ley 81 ANTAI' },
  { id: 'system-one', label: 'System One' },
  { id: 'deploy-cf', label: 'Deploy Cloudflare' },
  { id: 'r2-upload', label: 'Upload R2' }
]

const items = [
  {
    id: 'login',
    keys: ['login', 'auth', 'sesion', 'cookie', 'jwt', 'password', 'turnstile', 'argon2'],
    title: 'Autenticación y Sesiones en el Edge',
    domain: '05_Security // 02_Backend',
    time: '30 min',
    risk: 'Crítico',
    riskClass: 'crit',
    confidence: 99.4,
    summary: 'Emisión de credenciales seguras, almacenamiento en cookies HttpOnly y validación de tokens en Cloudflare KV/D1 con mitigación de fuerza bruta.',
    standards: [
      {
        name: '05_Security/SECURITY_ENGINEERING_STANDARD.md',
        desc: 'Directiva de cookies httpOnly, SameSite, hashing criptográfico y defensa en profundidad.',
        link: '/05_Security/SECURITY_ENGINEERING_STANDARD'
      },
      {
        name: '02_Backend/WORKERS_CLOUDFLARE_STANDARD.md',
        desc: 'Sesiones en KV/D1 y cabeceras Cache-Control: no-store.',
        link: '/02_Backend/WORKERS_CLOUDFLARE_STANDARD'
      },
      {
        name: '01_Frontend/Patterns/FRONTEND_MODALS_PATTERNS.md',
        desc: 'Validación Zod en formularios y Cloudflare Turnstile.',
        link: '/01_Frontend/Patterns/FRONTEND_MODALS_PATTERNS'
      }
    ],
    rules: [
      {
        id: 'S-001',
        req: 'Cookies httpOnly + Secure obligatorias. Nunca persistir tokens de sesión en localStorage.',
        why: 'localStorage es accesible por cualquier script inyectado vía XSS. La cookie httpOnly está protegida por el navegador.'
      },
      {
        id: 'S-002',
        req: 'Hashing de contraseñas exclusivamente con Argon2id o WebCrypto PBKDF2.',
        why: 'Algoritmos rápidos como MD5 o SHA-256 son vulnerables a colisiones masivas en GPUs comerciales.'
      },
      {
        id: 'S-003',
        req: 'Rate limiting estricto de máximo 5 intentos fallidos por IP/minuto en rutas de auth.',
        why: 'Protección contra ataques de diccionario automatizados en endpoints públicos.'
      }
    ],
    steps: [
      {
        name: 'Frontend: Formulario validado con Zod y widget Turnstile',
        desc: 'Mitiga bots antes de activar la solicitud HTTP al Worker.',
        code: 'const schema = z.object({ email: z.string().email(), password: z.string().min(8) });'
      },
      {
        name: 'Backend: Verificación de hash y persistencia en KV',
        desc: 'Emisión de sessionId criptográfico con TTL de expiración fija.',
        code: 'const sid = crypto.randomUUID();\nawait env.KV_SESSIONS.put(sid, JSON.stringify({ userId }), { expirationTtl: 604800 });'
      },
      {
        name: 'Respuesta: Cookie blindada con Cache-Control no-store',
        desc: 'Garantiza que la CDN jamás cachee ni sirva sesiones entre usuarios.',
        code: 'headers.set("Set-Cookie", "session=" + sid + "; HttpOnly; Secure; SameSite=Lax; Path=/");\nheaders.set("Cache-Control", "no-store");'
      }
    ],
    gotcha: 'Cualquier endpoint que lea cookies de sesión debe devolver "Cache-Control: no-store" explícito para evitar respuestas cacheadas en el CDN.'
  },
  {
    id: 'pagos',
    keys: ['pagos', 'tarjeta', 'paguelofacil', 'panama', 'checkout', 'dgi', 'itbms', 'webhook'],
    title: 'Cobros con Tarjeta en Panamá (PagueloFacil)',
    domain: '03_API // 16_Accounting',
    time: '45 min',
    risk: 'Financiero',
    riskClass: 'high',
    confidence: 98.7,
    summary: 'Integración del gateway PagueloFacil con cálculo server-side de montos, verificación de webhooks e idempotencia de codOper.',
    standards: [
      {
        name: '03_API/PAGUELOFACIL_INTEGRATION.md',
        desc: 'Mapeo de CMTN, captura de fondos y resolución de codOper.',
        link: '/03_API/PAGUELOFACIL_INTEGRATION'
      },
      {
        name: '03_API/WEBHOOK_IDEMPOTENCY_STANDARD.md',
        desc: 'Patrón de deduplicación con cerrojo UNIQUE en base de datos.',
        link: '/03_API/WEBHOOK_IDEMPOTENCY_STANDARD'
      },
      {
        name: '16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md',
        desc: 'Retención de ITBMS (7%) y auditoría fiscal DGI.',
        link: '/16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD'
      }
    ],
    rules: [
      {
        id: 'API-001',
        req: 'El monto a cobrar (CMTN) SIEMPRE se calcula en el backend.',
        why: 'Confiar en valores enviados por el cliente permite manipular el precio a montos arbitrarios.'
      },
      {
        id: 'API-002',
        req: 'Constraint UNIQUE sobre codOper en la tabla de pagos para idempotencia.',
        why: 'Las pasarelas reintentan webhooks ante timeouts; evita duplicar la acreditación del servicio.'
      },
      {
        id: 'API-003',
        req: 'Validar operationType in (CAPTURE, AUTH_CAPTURE, RECURRENT).',
        why: 'Eventos AUTH o 3DS representan validación de tarjeta sin liquidación de fondos.'
      }
    ],
    steps: [
      {
        name: 'Orden Server-Side',
        desc: 'El cliente envía product_id. El servidor calcula el precio real y solicita token a PagueloFacil.',
        code: 'const payload = { CMTN: product.price, CDSC: product.name, PF_CF: orderId };'
      },
      {
        name: 'Procesamiento Atómico de Webhook',
        desc: 'Inserción condicionada al codOper único para neutralizar envíos duplicados.',
        code: 'INSERT INTO payments (cod_oper, order_id, amount) VALUES (?, ?, ?) ON CONFLICT DO NOTHING;'
      }
    ],
    gotcha: 'Conserva el codOper en logs estructurados con id de correlación; es el identificador requerido ante disputas bancarias.'
  },
  {
    id: 'db-resilience',
    keys: ['base de datos', 'bd', 'caida', 'resiliencia', 'timeout', 'jitter', 'backoff', 'circuit breaker'],
    title: 'Resiliencia y Mitigación de Caídas en Base de Datos',
    domain: '04_Database // SRE',
    time: '25 min',
    risk: 'Disponibilidad',
    riskClass: 'crit',
    confidence: 99.1,
    summary: 'Implementación de Exponential Backoff con Full Jitter, Circuit Breaker de 3 estados y timeouts defensivos según principios de Google SRE.',
    standards: [
      {
        name: '04_Database/DATABASE_ROBUSTNESS_AND_RELIABILITY_STANDARD.md',
        desc: 'Patrón withResilience, circuit breaker y pruebas de concurrencia.',
        link: '/04_Database/DATABASE_ROBUSTNESS_AND_RELIABILITY_STANDARD'
      },
      {
        name: '04_Database/DATABASE_ENGINEERING_STANDARD.md',
        desc: 'Aislamiento de transacciones e índices defensivos.',
        link: '/04_Database/DATABASE_ENGINEERING_STANDARD'
      }
    ],
    rules: [
      {
        id: 'DB-R01',
        req: 'Exponential Backoff con Full Jitter obligatorio en reintentos transitorios.',
        why: 'Reintentar a intervalos fijos genera oleadas sincronizadas (Thundering Herd) que saturan la base de datos caída.'
      },
      {
        id: 'DB-R02',
        req: 'Fail-Fast con timeout estricto (5,000ms lecturas / 15,000ms transacciones).',
        why: 'Consultas lentas retienen conexiones y agotan el pool de sockets del backend.'
      },
      {
        id: 'DB-R03',
        req: 'Circuit Breaker abre tras 5 fallos consecutivos.',
        why: 'Si la base de datos no responde, corta peticiones en 1ms en lugar de consumir recursos esperando timeouts.'
      }
    ],
    steps: [
      {
        name: 'Envolver consultas críticas',
        desc: 'Aplica el helper defensivo con límite de reintentos y control de timeout.',
        code: 'const res = await withResilience(() => db.query(...), { maxRetries: 3, timeoutMs: 5000 });'
      },
      {
        name: 'Protección de Circuit Breaker',
        desc: 'Mantiene el estado global y degrada elegantemente a caché en fallo persistente.',
        code: 'const breaker = getCircuitBreaker("main-db", { failureThreshold: 5, resetTimeoutMs: 30000 });'
      }
    ],
    gotcha: 'Nunca reintentes fallos deterministas (violación de UNIQUE, errores sintácticos); solo se reintentan desconexiones y timeouts.'
  },
  {
    id: 'k6',
    keys: ['k6', 'carga', 'estres', 'load testing', 'performance', 'rps', 'vus'],
    title: 'Pruebas de Carga y Límites de Rendimiento (K6)',
    domain: '06_Testing // QA',
    time: '20 min',
    risk: 'Rendimiento',
    riskClass: 'med',
    confidence: 97.9,
    summary: 'Ejecución de pruebas de carga con Grafana K6 para determinar concurrencia máxima, latencia p95 y breaking point del sistema.',
    standards: [
      {
        name: '06_Testing/Guides/08_K6_LOAD_TESTING.md',
        desc: 'Guía de k6 portátil, etapas de calentamiento y métricas p95.',
        link: '/06_Testing/Guides/08_K6_LOAD_TESTING'
      },
      {
        name: '06_Testing/CHECKLIST_RELEASE_PRODUCCION.md',
        desc: 'Criterios de salida: p95 < 500ms y tasa de fallo < 1%.',
        link: '/06_Testing/CHECKLIST_RELEASE_PRODUCCION'
      }
    ],
    rules: [
      {
        id: 'K6-001',
        req: 'Toda prueba de carga DEBE incluir Thresholds cuantitativos obligatorios.',
        why: 'Sin assertions de percentiles (p95 < 500ms), las pruebas en CI/CD no previenen degradaciones reales.'
      },
      {
        id: 'K6-002',
        req: 'Prohibido inyectar carga máxima sin etapa previa de ramp-up.',
        why: 'Inyectar 100 VUs en el segundo cero causa picos anómalos por cold starts y pools no inicializados.'
      }
    ],
    steps: [
      {
        name: 'Definir script con 3 etapas',
        desc: 'Calentamiento (30s), sostenido (1m) y enfriamiento (30s).',
        code: 'export const options = {\n  stages: [{ duration: "30s", target: 50 }, { duration: "1m", target: 50 }, { duration: "30s", target: 0 }],\n  thresholds: { http_req_duration: ["p(95)<500"] }\n};'
      },
      {
        name: 'Ejecución y telemetría',
        desc: 'Monitorea métricas en tiempo real.',
        code: 'k6 run test-load.js'
      }
    ],
    gotcha: 'Monitorea el CPU de la base de datos durante la prueba: el 90% de los cuellos de botella se originan en el pool de BD y no en el servidor HTTP.'
  },
  {
    id: 'ley81',
    keys: ['ley 81', 'panama', 'antai', 'privacidad', 'datos', 'legal', 'multa', 'arco'],
    title: 'Protección de Datos y Cumplimiento Legal (Ley 81 Panamá)',
    domain: '05_Security // Legal',
    time: '35 min',
    risk: 'Regulatorio',
    riskClass: 'high',
    confidence: 99.0,
    summary: 'Alineación de sistemas con la Ley 81 de 2019 de Panamá, registro auditable de consentimiento, derechos ARCO y aislamiento de registros fiscales.',
    standards: [
      {
        name: '05_Security/PANAMA_LEGAL_DATA_PRIVACY_STANDARD.md',
        desc: 'Consentimiento informado, derechos ARCO, encriptación y sanciones ANTAI.',
        link: '/05_Security/PANAMA_LEGAL_DATA_PRIVACY_STANDARD'
      },
      {
        name: '16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md',
        desc: 'Retención de facturas por 5 años bajo Código de Comercio.',
        link: '/16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD'
      }
    ],
    rules: [
      {
        id: 'PAN-001',
        req: 'Consentimiento expreso e informado antes de recopilar PII.',
        why: 'La ANTAI aplica multas de hasta $10,000 USD por recolección o transferencia no autorizada de datos.'
      },
      {
        id: 'PAN-002',
        req: 'Encriptación en reposo (AES-256) y tránsito (TLS 1.3) para bases de datos con PII.',
        why: 'Exigencia técnica explícita de seguridad proporcional al riesgo de filtración.'
      },
      {
        id: 'PAN-003',
        req: 'Preservar registros contables 5 años independientemente de solicitudes de borrado.',
        why: 'El deber tributario ante la DGI prevalece sobre el derecho de cancelación de datos personales.'
      }
    ],
    steps: [
      {
        name: 'Trazabilidad de términos',
        desc: 'Persiste fecha y versión legal en la tabla de usuarios.',
        code: 'ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMPTZ;'
      },
      {
        name: 'Aislamiento en borrado de cuenta',
        desc: 'Anonimiza los datos de perfil pero retiene las transacciones contables.',
        code: 'UPDATE payments SET client_name = "[ANON_LEY81]" WHERE user_id = ?;'
      }
    ],
    gotcha: 'El borrado total de facturas ante una solicitud ARCO es ilegal: la normativa DGI exige conservar comprobantes 5 años.'
  },
  {
    id: 'system-one',
    keys: ['system one', 'jev', 'clef', 'clef-flash', 'typesafe', 'laya', 'ia', 'decisiones'],
    title: 'Modelos System One (Clef-flash & Jev) para Decisiones en el Edge',
    domain: '13_AI_Rules',
    time: '15 min',
    risk: 'Eficiencia',
    riskClass: 'low',
    confidence: 99.5,
    summary: 'Uso de modelos de inferencia ultra rápida (<40ms) para clasificación y control de flujo tipado sin el coste ni latencia de LLMs generativos.',
    standards: [
      {
        name: '13_AI_Rules/SYSTEM_ONE_MODELS_JEV_STANDARD.md',
        desc: 'Estándar oficial: Clef-flash en Cloudflare (10k neuronas gratis), Laya y Jev.',
        link: '/13_AI_Rules/SYSTEM_ONE_MODELS_JEV_STANDARD'
      },
      {
        name: '13_AI_Rules/AI_ML_PRODUCTION.md',
        desc: 'Prácticas de IA en el Edge y caché KV.',
        link: '/13_AI_Rules/AI_ML_PRODUCTION'
      }
    ],
    rules: [
      {
        id: 'S1-001',
        req: 'Prohibido usar LLMs generativos para decisiones booleanas si el SLA exige < 200ms.',
        why: 'Un LLM generativo tarda segundos y cobra por tokens de salida. Clef-flash responde en 25ms en un solo forward-pass.'
      },
      {
        id: 'S1-002',
        req: 'Evaluación en paralelo obligatoria (Batch Questions).',
        why: 'Proyecta el embedding de estado contra múltiples cabezales de decisión simultáneos sin coste lineal.'
      }
    ],
    steps: [
      {
        name: 'Llamada nativa en Cloudflare Workers AI',
        desc: 'Aprovecha las 10,000 neuronas gratuitas diarias.',
        code: 'const res = await env.AI.run("@cf/cloudflare/clef-flash", {\n  state: input,\n  questions: { isUrgent: { type: "noul", instructions: "¿Es urgente?" } }\n});'
      }
    ],
    gotcha: 'Clef-flash no genera texto ni responde en lenguaje libre; solo devuelve tipos estrictos y puntuaciones de confianza calibrada.'
  },
  {
    id: 'deploy-cf',
    keys: ['deploy', 'cloudflare', 'pages', 'workers', 'wrangler', 'build'],
    title: 'Despliegue a Cloudflare Pages & Workers con Wrangler',
    domain: '07_DevOps // 08_Cloud',
    time: '10 min',
    risk: 'Operativo',
    riskClass: 'med',
    confidence: 99.2,
    summary: 'Procedimiento seguro para empaquetar y publicar sitios estáticos y Workers en Cloudflare con control de entorno.',
    standards: [
      {
        name: '07_DevOps/GITHUB_STANDARD.md',
        desc: 'Flujo de ramas, commits y directivas de despliegue.',
        link: '/07_DevOps/GITHUB_STANDARD'
      },
      {
        name: '02_Backend/WORKERS_CLOUDFLARE_STANDARD.md',
        desc: 'Bindings de KV, D1 y secrets en wrangler.toml.',
        link: '/02_Backend/WORKERS_CLOUDFLARE_STANDARD'
      }
    ],
    rules: [
      {
        id: 'DEP-001',
        req: 'Nunca comitear archivos .env ni tokens en Git.',
        why: 'Permite que credenciales de infraestructura queden indexadas o expuestas públicamente.'
      },
      {
        id: 'DEP-002',
        req: 'Validar cuenta y token con wrangler whoami antes del deploy.',
        why: 'Evita desplegar sobre el proyecto o cuenta errónea.'
      }
    ],
    steps: [
      {
        name: 'Compilar build limpio',
        desc: 'Verificar cero errores en el bundle estático.',
        code: 'npm run docs:build'
      },
      {
        name: 'Publicar a Pages con Wrangler',
        desc: 'Envía los archivos estáticos a la rama main de producción.',
        code: 'npx wrangler pages deploy .vitepress/dist --project-name handbook-explorer --branch main'
      }
    ],
    gotcha: 'Mantén tokens exclusivamente en .env.local y asegura que .env* esté en .gitignore.'
  },
  {
    id: 'r2-upload',
    keys: ['r2', 'upload', 'archivos', 'presigned', 'url firmada', 's3', 'bucket'],
    title: 'Subida Directa a Cloudflare R2 con Presigned URLs',
    domain: '08_Cloud // 05_Security',
    time: '20 min',
    risk: 'Infraestructura',
    riskClass: 'med',
    confidence: 98.4,
    summary: 'Patrón de emisión de URLs firmadas temporales para transferir archivos directamente desde el cliente al bucket R2 sin sobrecargar memoria del Worker.',
    standards: [
      {
        name: '08_Cloud/PATRON_R2_UPLOAD_SEGURO.md',
        desc: 'Arquitectura de upload seguro y presigned URLs.',
        link: '/08_Cloud/PATRON_R2_UPLOAD_SEGURO'
      },
      {
        name: '05_Security/SECRET_LEAK_PREVENTION_STANDARD.md',
        desc: 'Protección de credenciales de bucket.',
        link: '/05_Security/SECRET_LEAK_PREVENTION_STANDARD'
      }
    ],
    rules: [
      {
        id: 'R2-001',
        req: 'Nunca recibir el binario del archivo en la memoria del Worker.',
        why: 'Satura los 128MB de RAM del Worker y causa timeouts en conexiones lentas.'
      },
      {
        id: 'R2-002',
        req: 'Validar MIME-Type y tamaño máximo antes de generar la URL firmada.',
        why: 'Previene el almacenamiento de archivos no autorizados en el bucket.'
      }
    ],
    steps: [
      {
        name: 'Worker emite URL firmada con TTL de 5 minutos',
        desc: 'Genera el enlace presigned autorizado.',
        code: 'const { url } = await generateR2PresignedUrl(bucket, fileKey, contentType, 300);'
      },
      {
        name: 'Cliente realiza PUT directo al bucket',
        desc: 'El navegador transfiere directo a Cloudflare R2 sin costo de egress.',
        code: 'await fetch(presignedUrl, { method: "PUT", body: fileBlob });'
      }
    ],
    gotcha: 'Cloudflare R2 tiene 0 costos de salida (egress fees), ahorrando un 90% comparado con Amazon AWS S3.'
  }
]

const activeItem = computed(() => {
  return items.find(it => it.id === currentId.value) || null
})

function pickChip(id) {
  currentId.value = id
  const target = items.find(it => it.id === id)
  if (target) {
    query.value = target.title
  }
}

function onSearch() {
  const q = query.value.trim().toLowerCase()
  if (!q) {
    currentId.value = 'login'
    return
  }

  const match = items.find(it => {
    if (it.title.toLowerCase().includes(q)) return true
    if (it.domain.toLowerCase().includes(q)) return true
    return it.keys.some(k => q.includes(k) || k.includes(q))
  })

  currentId.value = match ? match.id : null
}

function resetQuery() {
  query.value = ''
  currentId.value = 'login'
}
</script>

<style scoped>
.router-root {
  margin: 3.5rem 0 2.5rem;
  padding: 2rem 2.25rem;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-family: var(--vp-font-family-base, 'Inter', sans-serif);
}

.router-header {
  margin-bottom: 1.5rem;
}

.router-kicker {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--vp-c-brand-1);
  text-transform: uppercase;
  margin-bottom: 0.4rem;
}

.kicker-dot {
  width: 5px;
  height: 5px;
  background: var(--vp-c-brand-1);
  border-radius: 50%;
}

.router-heading {
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--vp-c-text-1);
  margin: 0 0 0.35rem 0;
  border: none;
  padding: 0;
}

.router-lead {
  font-size: 0.92rem;
  color: var(--vp-c-text-2);
  margin: 0;
  line-height: 1.5;
}

/* Buscador */
.router-search-wrapper {
  margin-bottom: 1.75rem;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  transition: border-color 0.15s ease;
  margin-bottom: 0.85rem;
}

.search-bar:focus-within {
  border-color: var(--vp-c-brand-1);
}

.search-icon {
  width: 16px;
  height: 16px;
  color: var(--vp-c-text-3);
  flex-shrink: 0;
}

.search-field {
  flex: 1;
  padding: 10px 0;
  font-size: 0.92rem;
  background: transparent;
  border: none;
  outline: none;
  color: var(--vp-c-text-1);
  font-family: inherit;
}

.search-field::placeholder {
  color: var(--vp-c-text-3);
}

.clear-trigger {
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--vp-c-text-3);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
}

.clear-trigger:hover {
  color: var(--vp-c-brand-1);
}

/* Chips */
.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip-item {
  padding: 4px 10px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  font-size: 0.78rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip-item:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.chip-item.active {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

/* Panel de Resultados */
.result-panel {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  padding: 1.5rem;
}

.panel-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 0.85rem;
}

.meta-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  padding: 2px 7px;
  border-radius: 3px;
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-2);
  border: 1px solid var(--vp-c-divider);
}

.meta-tag.domain {
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-soft);
  background: var(--vp-c-brand-soft);
  font-weight: 600;
}

.meta-tag.risk.crit { color: #e5484d; border-color: rgba(229, 72, 77, 0.2); }
.meta-tag.risk.high { color: #f76808; border-color: rgba(247, 104, 8, 0.2); }
.meta-tag.risk.med { color: #f5a623; border-color: rgba(245, 166, 35, 0.2); }
.meta-tag.risk.low { color: #30a46c; border-color: rgba(48, 164, 108, 0.2); }

.meta-metric {
  margin-left: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--vp-c-text-3);
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin: 0 0 0.45rem 0;
  border: none;
  padding: 0;
  letter-spacing: -0.01em;
}

.panel-summary {
  font-size: 0.88rem;
  color: var(--vp-c-text-2);
  line-height: 1.55;
  margin: 0 0 1.25rem 0;
}

/* Grilla de 2 columnas */
.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--vp-c-divider);
}

@media (max-width: 820px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}

.col-head {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
  margin-bottom: 0.75rem;
}

.standards-stack {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.std-card {
  display: block;
  padding: 8px 10px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  text-decoration: none !important;
  transition: all 0.15s ease;
}

.std-card:hover {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-bg-alt);
}

.std-file {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--vp-c-brand-1);
  margin-bottom: 2px;
}

.std-note {
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
  line-height: 1.35;
}

.rules-stack {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rule-row {
  display: flex;
  gap: 8px;
  padding: 8px 10px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
}

.rule-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--vp-c-brand-1);
  flex-shrink: 0;
}

.rule-text {
  flex: 1;
}

.rule-req {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 2px;
  line-height: 1.35;
}

.rule-reason {
  font-size: 0.74rem;
  color: var(--vp-c-text-3);
  line-height: 1.35;
}

/* Flujo de Pasos */
.flow-block {
  padding-top: 1rem;
  border-top: 1px solid var(--vp-c-divider);
  margin-bottom: 1.25rem;
}

.steps-flow {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.flow-step {
  display: flex;
  gap: 10px;
}

.step-idx {
  width: 20px;
  height: 20px;
  background: var(--vp-c-default-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--vp-c-text-2);
  flex-shrink: 0;
  margin-top: 2px;
}

.step-detail {
  flex: 1;
}

.step-name {
  display: block;
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 2px;
}

.step-desc {
  display: block;
  font-size: 0.78rem;
  color: var(--vp-c-text-2);
  line-height: 1.4;
  margin-bottom: 4px;
}

.code-box {
  margin: 3px 0 0;
  padding: 6px 10px;
  background: var(--vp-code-block-bg);
  border: 1px solid var(--vp-code-block-divider-color);
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.76rem;
  color: var(--vp-code-block-color);
  overflow-x: auto;
}

/* Gotcha */
.gotcha-bar {
  padding: 8px 12px;
  background: var(--vp-c-brand-soft);
  border-left: 2px solid var(--vp-c-brand-1);
  border-radius: 0 3px 3px 0;
  font-size: 0.78rem;
  line-height: 1.4;
}

.gotcha-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--vp-c-brand-1);
  margin-right: 6px;
}

.gotcha-text {
  color: var(--vp-c-text-2);
}

/* Empty */
.empty-panel {
  padding: 2rem 1rem;
  text-align: center;
  color: var(--vp-c-text-3);
  font-size: 0.88rem;
}

.empty-links {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 0.75rem;
}

.empty-links a {
  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  color: var(--vp-c-brand-1);
  text-decoration: none;
}

.empty-links a:hover {
  text-decoration: underline;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
