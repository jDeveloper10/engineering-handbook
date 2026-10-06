<template>
  <div class="recipe-router-container">
    <!-- Encabezado del Recetario -->
    <div class="recipe-header">
      <div class="recipe-badge">
        <span class="pulse-dot"></span>
        <span>SYSTEM ONE ACTION ROUTER</span>
      </div>
      <h2 class="recipe-title">
        🍳 Recetario de Ingeniería & Arquitectura
      </h2>
      <p class="recipe-subtitle">
        Pregunta en lenguaje común o selecciona una receta. El sistema mapea instantáneamente los <strong>281 estándares</strong> para darte la solución canónica: ingredientes, reglas inquebrantables y código.
      </p>
    </div>

    <!-- Barra de Búsqueda -->
    <div class="recipe-search-box">
      <div class="search-input-wrapper">
        <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Ej: cómo hacer un login, cobrar con tarjeta en Panamá, base de datos caída, k6, leyes ANTAI..."
          class="recipe-input"
          @input="handleSearch"
        />
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="clear-btn"
          title="Limpiar búsqueda"
        >
          ✕
        </button>
      </div>

      <!-- Píldoras de Acceso Rápido -->
      <div class="quick-pills">
        <span class="pills-label">Recetas frecuentes:</span>
        <button
          v-for="pill in popularPills"
          :key="pill.id"
          @click="selectRecipe(pill.id)"
          class="pill-btn"
          :class="{ active: activeRecipeId === pill.id }"
        >
          {{ pill.icon }} {{ pill.label }}
        </button>
      </div>
    </div>

    <!-- Ficha de la Receta Activa -->
    <transition name="fade-slide" mode="out-in">
      <div v-if="activeRecipe" :key="activeRecipe.id" class="recipe-card">
        <!-- Barra Superior de la Ficha -->
        <div class="card-top-bar">
          <div class="card-tags">
            <span class="domain-tag" :style="{ backgroundColor: activeRecipe.badgeBg, color: activeRecipe.badgeColor }">
              {{ activeRecipe.domain }}
            </span>
            <span class="complexity-tag">
              ⏱️ {{ activeRecipe.complexity }}
            </span>
            <span class="risk-tag" :class="activeRecipe.riskClass">
              🛡️ Riesgo: {{ activeRecipe.riskLevel }}
            </span>
          </div>
          <div class="confidence-badge">
            <span class="conf-dot"></span>
            <span>Confianza Calibrada: {{ activeRecipe.confidence }}%</span>
          </div>
        </div>

        <!-- Título y Diagnóstico -->
        <h3 class="card-title">
          {{ activeRecipe.title }}
        </h3>
        <p class="card-diagnosis">
          <strong>🎯 Diagnóstico Arquitectónico:</strong> {{ activeRecipe.diagnosis }}
        </p>

        <!-- Grilla de Secciones -->
        <div class="card-grid">
          <!-- Ingredientes / Estándares -->
          <div class="grid-section ingredients-section">
            <h4 class="section-title">
              📦 Ingredientes Obligatorios (Estándares)
            </h4>
            <ul class="standards-list">
              <li v-for="(std, idx) in activeRecipe.standards" :key="idx" class="standard-item">
                <a :href="std.link" class="standard-link">
                  <span class="std-icon">📄</span>
                  <div class="std-info">
                    <span class="std-name">{{ std.name }}</span>
                    <span class="std-desc">{{ std.desc }}</span>
                  </div>
                  <span class="arrow-icon">↗</span>
                </a>
              </li>
            </ul>
          </div>

          <!-- Reglas Inquebrantables -->
          <div class="grid-section rules-section">
            <h4 class="section-title rules-title">
              ⚠️ Reglas Inquebrantables (REQUIRED)
            </h4>
            <div class="rules-list">
              <div v-for="(rule, idx) in activeRecipe.rules" :key="idx" class="rule-card">
                <div class="rule-code">{{ rule.code }}</div>
                <div class="rule-body">
                  <div class="rule-statement">{{ rule.statement }}</div>
                  <div class="rule-why"><strong>Por qué:</strong> {{ rule.why }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Paso a Paso Canónico -->
        <div class="steps-section">
          <h4 class="section-title">
            🛠️ Paso a Paso Canónico (Receta de Ejecución)
          </h4>
          <ol class="steps-timeline">
            <li v-for="(step, idx) in activeRecipe.steps" :key="idx" class="step-item">
              <div class="step-number">{{ idx + 1 }}</div>
              <div class="step-content">
                <strong class="step-title">{{ step.title }}</strong>
                <p class="step-desc">{{ step.desc }}</p>
                <pre v-if="step.code" class="step-snippet"><code>{{ step.code }}</code></pre>
              </div>
            </li>
          </ol>
        </div>

        <!-- Consejo Pro & Gotcha Común -->
        <div class="pro-tip-box">
          <span class="tip-icon">💡</span>
          <div class="tip-body">
            <strong>Consejo Pro / Gotcha Frecuente:</strong>
            <p>{{ activeRecipe.proTip }}</p>
          </div>
        </div>
      </div>

      <!-- Estado: No Encontrado o Buscando -->
      <div v-else-if="searchQuery" class="no-recipe-card">
        <div class="no-recipe-icon">🔍</div>
        <h3>No encontramos una receta exacta para "{{ searchQuery }}"</h3>
        <p>Prueba con términos como: <em>login, tarjeta, panama, k6, base de datos, system one, r2, websocket, leyes</em>.</p>
        <div class="suggested-actions">
          <a href="/README" class="action-btn">Ver Índice de los 281 Documentos ↗</a>
          <a href="/AGENTS" class="action-btn alt">Consultar Árbol de Ruteo AGENTS.md ↗</a>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const activeRecipeId = ref('login')

const popularPills = [
  { id: 'login', icon: '🔐', label: 'Login & Autenticación' },
  { id: 'pagos', icon: '💳', label: 'Cobrar en Panamá (PagueloFacil)' },
  { id: 'db-resilience', icon: '🛡️', label: 'Resiliencia en Base de Datos' },
  { id: 'k6', icon: '⚡', label: 'Pruebas de Estrés K6' },
  { id: 'ley81', icon: '📜', label: 'Leyes Panamá (Ley 81 ANTAI)' },
  { id: 'system-one', icon: '🧠', label: 'System One (Clef-flash & Jev)' },
  { id: 'deploy-cf', icon: '🚀', label: 'Deploy Cloudflare Pages/Workers' },
  { id: 'r2-upload', icon: '☁️', label: 'Subida Directa a R2' }
]

const recipes = [
  {
    id: 'login',
    keywords: ['login', 'auth', 'autenticacion', 'password', 'jwt', 'cookie', 'sesion', 'session', 'seguridad', 'turnstile', 'argon2'],
    title: 'Autenticación Canónica & Login Seguro',
    domain: '05_Security & 02_Backend',
    badgeBg: 'rgba(239, 68, 68, 0.15)',
    badgeColor: '#ef4444',
    complexity: 'Media (30 min)',
    riskLevel: 'Crítico',
    riskClass: 'risk-critical',
    confidence: 99.4,
    diagnosis: 'El sistema requiere emitir credenciales de sesión protegidas contra robos por XSS, inyecciones y ataques de fuerza bruta en los endpoints de entrada.',
    standards: [
      {
        name: 'SECURITY_ENGINEERING_STANDARD.md',
        desc: 'Reglas de cookies httpOnly, SameSite, hashing criptográfico y defensa en profundidad.',
        link: '/05_Security/SECURITY_ENGINEERING_STANDARD'
      },
      {
        name: 'WORKERS_CLOUDFLARE_STANDARD.md',
        desc: 'Manejo de sesiones ultrarrápidas con Cloudflare KV o D1 y validación en el Edge.',
        link: '/02_Backend/WORKERS_CLOUDFLARE_STANDARD'
      },
      {
        name: 'FRONTEND_MODALS_PATTERNS.md',
        desc: 'Formulario de login reactivo accesible con Zod, manejo de estados y Cloudflare Turnstile.',
        link: '/01_Frontend/Patterns/FRONTEND_MODALS_PATTERNS'
      }
    ],
    rules: [
      {
        code: 'S-001',
        statement: 'Cookies httpOnly + Secure obligatorias. JAMÁS guardar tokens de sesión en localStorage.',
        why: 'localStorage es legible por cualquier script inyectado (XSS). Las cookies httpOnly son inaccesibles para JavaScript del navegador.'
      },
      {
        code: 'S-002',
        statement: 'Hashing de contraseñas con Argon2id o WebCrypto PBKDF2 (nunca MD5 o SHA-256 plano).',
        why: 'Los algoritmos rápidos como SHA-256 permiten que atacantes calculen miles de millones de hashes por segundo con GPUs comerciales.'
      },
      {
        code: 'S-003',
        statement: 'Rate Limiting estricto: máximo 5 intentos fallidos por IP/minuto en el endpoint de login.',
        why: 'Evita ataques de diccionario y colisiones forzadas que saturan el backend y comprometen cuentas débiles.'
      }
    ],
    steps: [
      {
        title: '1. Validación de Entrada en Frontend (React / Svelte)',
        desc: 'Validar correo y longitud mínima de contraseña con Zod e incorporar el widget de Cloudflare Turnstile para mitigar bots antes del submit.',
        code: 'const schema = z.object({ email: z.string().email(), password: z.string().min(8) });'
      },
      {
        title: '2. Endpoint Server-Side en Cloudflare Worker',
        desc: 'Validar el token de Turnstile, verificar el hash criptográfico del usuario y emitir un ID de sesión criptográfico (crypto.getRandomValues).',
        code: 'const sessionId = crypto.randomUUID();\nawait env.KV_SESSIONS.put(sessionId, JSON.stringify({ userId }), { expirationTtl: 86400 * 7 });'
      },
      {
        title: '3. Encabezado Set-Cookie Seguro y Cache-Control',
        desc: 'Retornar la cookie blindada y el encabezado no-store para que Cloudflare CDN jamás cachee respuestas autenticadas.',
        code: 'headers.set("Set-Cookie", `session=${sessionId}; HttpOnly; Secure; SameSite=Lax; Path=/`);\nheaders.set("Cache-Control", "no-store");'
      }
    ],
    proTip: 'Si estás detrás del CDN de Cloudflare, olvida un solo momento el Cache-Control: no-store y la respuesta de un usuario autenticado podría servirse por caché a otro cliente.'
  },
  {
    id: 'pagos',
    keywords: ['pagos', 'tarjeta', 'paguelofacil', 'panama', 'checkout', 'cobro', 'dgi', 'itbms', 'webhook', 'idempotencia', 'banco'],
    title: 'Cobros con Tarjeta en Panamá (Integración PagueloFacil)',
    domain: '03_API & 16_Accounting',
    badgeBg: 'rgba(16, 185, 129, 0.15)',
    badgeColor: '#10b981',
    complexity: 'Avanzada (45 min)',
    riskLevel: 'Financiero Alto',
    riskClass: 'risk-high',
    confidence: 98.7,
    diagnosis: 'El sistema requiere cobrar con tarjeta de crédito/débito en territorio panameño con conciliación bancaria e idempotencia estricta en webhooks.',
    standards: [
      {
        name: 'PAGUELOFACIL_INTEGRATION.md',
        desc: 'Flujo completo de checkout, captura de fondos, manejo de tokens y codOper en Panamá.',
        link: '/03_API/PAGUELOFACIL_INTEGRATION'
      },
      {
        name: 'WEBHOOK_IDEMPOTENCY_STANDARD.md',
        desc: 'Mecanismo de deduplicación con cerrojos UNIQUE en base de datos para evitar cobros dobles.',
        link: '/03_API/WEBHOOK_IDEMPOTENCY_STANDARD'
      },
      {
        name: 'PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md',
        desc: 'Retención de ITBMS (7%), facturación electrónica DGI y conciliación con el Código de Comercio.',
        link: '/16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD'
      }
    ],
    rules: [
      {
        code: 'API-001',
        statement: 'NUNCA confiar en montos que provengan del cliente. El total SIEMPRE se calcula server-side.',
        why: 'Un usuario malicioso puede alterar el campo CMTN en el request HTTP y pagar $0.01 por un servicio de $100.'
      },
      {
        code: 'API-002',
        statement: 'Idempotencia estricta en Webhook usando codOper como constraint UNIQUE en base de datos.',
        why: 'Las pasarelas reintentan el envío de webhooks ante fallos de red; procesar dos veces el mismo codOper acredita doble servicio.'
      },
      {
        code: 'API-003',
        statement: 'Validar que operationType sea CAPTURE, AUTH_CAPTURE o RECURRENT antes de liberar servicio.',
        why: 'Eventos tipo AUTH o 3DS representan solo validaciones de tarjeta, no ingreso real de dinero a tu cuenta.'
      }
    ],
    steps: [
      {
        title: '1. Inicialización de Orden en el Backend',
        desc: 'El cliente envía solo el product_id. El servidor consulta el precio oficial en D1, calcula impuestos (7% ITBMS si aplica) y solicita el token de pago a PagueloFacil.',
        code: 'const payload = { CMTN: product.price, CDSC: product.name, PF_CF: orderId };'
      },
      {
        title: '2. Recepción del Webhook con Cerrojo Atómico',
        desc: 'Al recibir el POST de notificación, realizar un INSERT condicional atómico del codOper para garantizar que solo un hilo procese el pago.',
        code: 'INSERT INTO payments (cod_oper, order_id, amount, status) VALUES (?, ?, ?, ?) ON CONFLICT (cod_oper) DO NOTHING;'
      },
      {
        title: '3. Actualización de Balance / Entrega de Bien',
        desc: 'Si la fila fue insertada con éxito y status == 1 y operationType == CAPTURE, marcar orden pagada y emitir evento de factura DGI.',
        code: "await db.execute(\"UPDATE orders SET status = 'paid' WHERE id = ?\", [orderId]);"
      }
    ],
    proTip: 'Guarda siempre el codOper original en los logs estructurados con id de correlación; es el único dato que soporte de PagueloFacil te pedirá si hay una disputa bancaria.'
  },
  {
    id: 'db-resilience',
    keywords: ['base de datos', 'caida', 'resiliencia', 'db', 'sql', 'timeout', 'postgres', 'd1', 'jitter', 'backoff', 'circuit breaker', 'reintento'],
    title: 'Resiliencia y Caídas en Base de Datos (Google SRE)',
    domain: '04_Database',
    badgeBg: 'rgba(59, 130, 246, 0.15)',
    badgeColor: '#3b82f6',
    complexity: 'Media (25 min)',
    riskLevel: 'Disponibilidad Crítica',
    riskClass: 'risk-critical',
    confidence: 99.1,
    diagnosis: 'Prevenir que desconexiones intermitentes o picos de concurrencia en la base de datos tiren el backend completo o creen efectos Thundering Herd.',
    standards: [
      {
        name: 'DATABASE_ROBUSTNESS_AND_RELIABILITY_STANDARD.md',
        desc: 'Exponential Backoff con Full Jitter, Fail-Fast, Circuit Breaker de 3 estados y pruebas de concurrencia.',
        link: '/04_Database/DATABASE_ROBUSTNESS_AND_RELIABILITY_STANDARD'
      },
      {
        name: 'DATABASE_ENGINEERING_STANDARD.md',
        desc: 'Índices compuestos, Row Level Security (RLS) y aislamiento de transacciones ACID.',
        link: '/04_Database/DATABASE_ENGINEERING_STANDARD'
      }
    ],
    rules: [
      {
        code: 'DB-R01',
        statement: 'Exponential Backoff con Full Jitter obligatorio en reintentos transitorios.',
        why: 'Reintentar a intervalos fijos provoca que cientos de peticiones golpeen la base de datos simultáneamente, rematando el servidor caído.'
      },
      {
        code: 'DB-R02',
        statement: 'Fail-Fast y Timeout Estricto (5,000ms en lecturas, 15,000ms en transacciones).',
        why: 'Una consulta colgada retiene conexiones en el pool hasta agotar todos los sockets del backend.'
      },
      {
        code: 'DB-R03',
        statement: 'Circuit Breaker de 3 estados (CLOSED, OPEN, HALF_OPEN) tras 5 fallos consecutivos.',
        why: 'Si la base de datos está caída, el backend debe cortar peticiones en 1ms en lugar de esperar 5 segundos por cada cliente.'
      }
    ],
    steps: [
      {
        title: '1. Envolver Consultas con withResilience()',
        desc: 'Usa el módulo src/server/lib/db-resilience.ts para ejecutar queries con backoff dinámico y protección de timeout.',
        code: 'const user = await withResilience(() => db.query.users.findFirst({ where: ... }), { maxRetries: 3, timeoutMs: 5000 });'
      },
      {
        title: '2. Configurar el Circuit Breaker de la Aplicación',
        desc: 'Monitorea la salud del pool de conexiones. Al abrirse el circuito, responde con datos cacheados en KV o error 503 instantáneo.',
        code: 'const dbBreaker = getCircuitBreaker("main-db", { failureThreshold: 5, resetTimeoutMs: 30000 });'
      },
      {
        title: '3. Validar con Pruebas de Estrés en Vitest',
        desc: 'Ejecuta la suite con 20 promesas concurrentes simulando fallos temporales para verificar que el jitter distribuya los reintentos.',
        code: 'npm run test:unit -- src/server/lib/db-resilience.test.ts'
      }
    ],
    proTip: 'Nunca reintentes errores lógicos o deterministas (como violación de clave UNIQUE o Syntax Error); solo se reintentan fallos de socket, timeout o conexión cerrada.'
  },
  {
    id: 'k6',
    keywords: ['k6', 'carga', 'estres', 'load testing', 'performance', 'rps', 'vus', 'benchmark', 'cuello de botella'],
    title: 'Pruebas de Estrés y Carga con Grafana K6',
    domain: '06_Testing',
    badgeBg: 'rgba(168, 85, 247, 0.15)',
    badgeColor: '#a855f7',
    complexity: 'Básica a Media (20 min)',
    riskLevel: 'Rendimiento',
    riskClass: 'risk-medium',
    confidence: 97.9,
    diagnosis: 'Encontrar el punto de quiebre (Breaking Point), concurrencia máxima y latencia p95 bajo tráfico real antes de salir a producción.',
    standards: [
      {
        name: '08_K6_LOAD_TESTING.md',
        desc: 'Guía práctica de Grafana K6: instalación portátil, diseño de stages de ramp-up y análisis de percentiles.',
        link: '/06_Testing/Guides/08_K6_LOAD_TESTING'
      },
      {
        name: 'CHECKLIST_RELEASE_PRODUCCION.md',
        desc: 'Criterios de aceptación antes de desplegar: umbrales p95 < 500ms y tasa de error < 1%.',
        link: '/06_Testing/CHECKLIST_RELEASE_PRODUCCION'
      }
    ],
    rules: [
      {
        code: 'K6-001',
        statement: 'Toda prueba de carga DEBE incluir Thresholds que fallen el comando ante degradación.',
        why: 'Sin assertions cuantitativas (ej. p(95) < 500ms), las pruebas en CI/CD no previenen regresiones de rendimiento.'
      },
      {
        code: 'K6-002',
        statement: 'NUNCA lanzar un test de estrés de golpe. Usar siempre ramp-up de calentamiento.',
        why: 'Inyectar 100 usuarios virtuales en el segundo cero causa falsos positivos por cold-starts de lambdas y pools de BD vacíos.'
      }
    ],
    steps: [
      {
        title: '1. Definición del Script de Prueba (test-load.js)',
        desc: 'Configurar 3 fases de tráfico: calentamiento gradual (30s), carga sostenida (1m) y enfriamiento (30s).',
        code: 'export const options = {\n  stages: [\n    { duration: "30s", target: 50 },\n    { duration: "1m", target: 50 },\n    { duration: "30s", target: 0 }\n  ],\n  thresholds: { http_req_failed: ["rate<0.01"], http_req_duration: ["p(95)<500"] }\n};'
      },
      {
        title: '2. Ejecución desde la Terminal',
        desc: 'Ejecutar el binario de K6 apuntando al entorno de staging o producción.',
        code: 'k6 run test-load.js'
      },
      {
        title: '3. Identificación del Breaking Point',
        desc: 'Revisar la métrica http_req_duration y buscar en qué número de VUs la latencia se dispara o aparecen códigos 502/504.',
        code: '✓ http_req_duration: p(95)=182ms  |  http_req_failed: 0.00%  |  reqs: 5,488'
      }
    ],
    proTip: 'Monitorea el CPU de la base de datos mientras corre K6: el 90% de los breaking points ocurren por saturación de conexiones en la base de datos, no por el servidor web.'
  },
  {
    id: 'ley81',
    keywords: ['ley 81', 'panama', 'antai', 'privacidad', 'datos', 'legal', 'multa', 'arco', 'dgi', 'consentimiento', 'terminos'],
    title: 'Cumplimiento Legal y Privacidad en Panamá (Ley 81 / ANTAI)',
    domain: '05_Security & Legal',
    badgeBg: 'rgba(234, 179, 8, 0.15)',
    badgeColor: '#eab308',
    complexity: 'Media (35 min)',
    riskLevel: 'Regulatorio / Legal',
    riskClass: 'risk-high',
    confidence: 99.0,
    diagnosis: 'Alinear la arquitectura de software con la Ley 81 de 2019 de Protección de Datos Personales de Panamá y las regulaciones de la ANTAI y DGI.',
    standards: [
      {
        name: 'PANAMA_LEGAL_DATA_PRIVACY_STANDARD.md',
        desc: 'Requisitos de la Ley 81 de 2019: consentimiento expreso, derechos ARCO, encriptación y multas de ANTAI.',
        link: '/05_Security/PANAMA_LEGAL_DATA_PRIVACY_STANDARD'
      },
      {
        name: 'PANAMA_ACCOUNTING_COMPLIANCE_STANDARD.md',
        desc: 'Retención contable obligatoria de 5 años bajo Código de Comercio de Panamá y auditoría DGI.',
        link: '/16_Accounting/PANAMA_ACCOUNTING_COMPLIANCE_STANDARD'
      }
    ],
    rules: [
      {
        code: 'PAN-001',
        statement: 'Consentimiento previo, inequívoco y expreso antes de almacenar datos personales.',
        why: 'La ANTAI sanciona con multas de $1,000 a $10,000 USD el tratamiento de datos sin consentimiento auditable.'
      },
      {
        code: 'PAN-002',
        statement: 'Encriptación en reposo (AES-256) y en tránsito (TLS 1.3) para bases de datos con PII.',
        why: 'Obligatoriedad de medidas técnicas de seguridad proporcionales al riesgo de fuga de datos en software comercial.'
      },
      {
        code: 'PAN-003',
        statement: 'Conservación contable de 5 años inmutable separada de datos personales borrables.',
        why: 'El derecho de cancelación de la Ley 81 no prevalece sobre la obligación mercantil y fiscal de la DGI de retener facturación.'
      }
    ],
    steps: [
      {
        title: '1. Registro de Consentimiento Auditable',
        desc: 'Guardar timestamp ISO, dirección IP y versión de términos aceptados en la tabla users.',
        code: 'ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMPTZ;\nALTER TABLE users ADD COLUMN privacy_version VARCHAR(20);'
      },
      {
        title: '2. Implementar Endpoints de Derechos ARCO',
        desc: 'Proveer a los usuarios endpoints para exportar todos sus datos (/api/me/export) y solicitar eliminación de cuenta.',
        code: 'router.delete("/api/me", async (req, res) => { await anonymizeUserAccount(req.user.id); });'
      },
      {
        title: '3. Aislamiento de Registros de Facturación',
        desc: 'Si un usuario pide borrado de cuenta, anonimizar sus datos de contacto pero preservar facturas e historial DGI por 5 años.',
        code: 'UPDATE payments SET client_name = "[ANONIMIZADO_LEY81]" WHERE user_id = ?;'
      }
    ],
    proTip: 'Nunca borres físicamente facturas cuando un usuario pide eliminar su cuenta; la ley fiscal panameña exige conservarlas 5 años ante la DGI. Anonimiza los datos personales pero preserva la transacción contable.'
  },
  {
    id: 'system-one',
    keywords: ['system one', 'jev', 'clef', 'clef-flash', 'typesafe', 'laya', 'ia', 'decisiones', 'routing', 'rlcd', 'fast path'],
    title: 'Decisiones Rápidas & Tipadas con System One (Clef-flash & Jev)',
    domain: '13_AI_Rules',
    badgeBg: 'rgba(255, 107, 0, 0.15)',
    badgeColor: '#ff6b00',
    complexity: 'Básica (15 min)',
    riskLevel: 'Eficiencia / Coste',
    riskClass: 'risk-low',
    confidence: 99.5,
    diagnosis: 'Erradicar la latencia de 3 a 5 segundos y los costes por token de los LLMs tradicionales en tareas de bifurcación condicional y triaje.',
    standards: [
      {
        name: 'SYSTEM_ONE_MODELS_JEV_STANDARD.md',
        desc: 'Estándar oficial de System One: Cloudflare Clef-flash a coste $0 (10k neuronas), Laya y Jev.',
        link: '/13_AI_Rules/SYSTEM_ONE_MODELS_JEV_STANDARD'
      },
      {
        name: 'AI_ML_PRODUCTION.md',
        desc: 'Buenas prácticas de IA en el Edge, caché con KV y sanitización estricta de PII.',
        link: '/13_AI_Rules/AI_ML_PRODUCTION'
      }
    ],
    rules: [
      {
        code: 'S1-001',
        statement: 'NUNCA usar LLMs generativos para decisiones binarias o routing si el SLA exige < 200ms.',
        why: 'Un LLM generativo tarda segundos y cobra por tokens secuenciales. Clef-flash toma la decisión en 25ms en un solo forward-pass.'
      },
      {
        code: 'S1-002',
        statement: 'Inferencia en paralelo obligatoria: enviar todas las preguntas del mismo estado en un único llamado.',
        why: 'La arquitectura proyecta el embedding contra múltiples cabezales de decisión en paralelo sin costo lineal de tiempo.'
      },
      {
        code: 'S1-003',
        statement: 'Validar siempre el output con Zod antes de ejecutar efectos secundarios en bases de datos.',
        why: 'Previene inconsistencias de tipos si el servicio sufre una degradación o responde fuera de rango.'
      }
    ],
    steps: [
      {
        title: '1. Invocación en Cloudflare Workers AI',
        desc: 'Usa el modelo oficial @cf/cloudflare/clef-flash dentro de tu Worker sin costo adicional.',
        code: 'const result = await env.AI.run("@cf/cloudflare/clef-flash", {\n  state: userMessage,\n  questions: {\n    isUrgent: { type: "noul", instructions: "¿Es urgente?" },\n    category: { type: "choice", choices: ["billing", "tech", "sales"] }\n  }\n});'
      },
      {
        title: '2. Enrutamiento Condicional Fast-Path',
        desc: 'Si la intención no requiere redacción humana compleja, resuelve en menos de 50ms directamente en la base de datos.',
        code: 'if (result.answers.category.choice === "billing") {\n  return Response.json(await getBillingStatus(userId));\n}'
      },
      {
        title: '3. Fallback a Modelo Generativo (System 2)',
        desc: 'Solo si requiresReasoning == true, delega el caso a Claude o GPT-4 con el contexto ya preclasificado.',
        code: 'return streamLLMResponse(userMessage, result.answers);'
      }
    ],
    proTip: 'Cloudflare te da 10,000 Neurons gratis todos los días; con Clef-flash puedes ejecutar entre 700 y 1,200 decisiones estructuradas diarias a coste $0.'
  },
  {
    id: 'deploy-cf',
    keywords: ['deploy', 'cloudflare', 'pages', 'workers', 'wrangler', 'build', 'env', 'produccion', 'hosting'],
    title: 'Despliegue a Cloudflare Pages & Workers con Wrangler',
    domain: '07_DevOps & 08_Cloud',
    badgeBg: 'rgba(249, 115, 22, 0.15)',
    badgeColor: '#f97316',
    complexity: 'Básica (10 min)',
    riskLevel: 'Despliegue',
    riskClass: 'risk-medium',
    confidence: 99.2,
    diagnosis: 'Publicar sitios web estáticos (Vite, Next, VitePress) o APIs serverless en la red edge global de Cloudflare.',
    standards: [
      {
        name: 'GITHUB_STANDARD.md',
        desc: 'Normas de commits, protección de ramas main y automatización de despliegues.',
        link: '/07_DevOps/GITHUB_STANDARD'
      },
      {
        name: 'WORKERS_CLOUDFLARE_STANDARD.md',
        desc: 'Configuración de wrangler.toml, bindings de KV, D1 y secrets.',
        link: '/02_Backend/WORKERS_CLOUDFLARE_STANDARD'
      }
    ],
    rules: [
      {
        code: 'DEP-001',
        statement: 'JAMÁS subir archivos .env ni tokens en commits de Git.',
        why: 'Cualquier commit público o compartido con tokens permite a terceros tomar control de tu infraestructura Cloudflare.'
      },
      {
        code: 'DEP-002',
        statement: 'Verificar cuenta y token con wrangler whoami antes de iniciar el despliegue.',
        why: 'Previene despliegues accidentales en la cuenta equivocada de un cliente o proyecto personal.'
      }
    ],
    steps: [
      {
        title: '1. Generar el Build de Producción',
        desc: 'Asegurar que la carpeta dist o .vitepress/dist se compile con cero errores.',
        code: 'npm run docs:build # o npm run build'
      },
      {
        title: '2. Desplegar con Wrangler CLI a Cloudflare Pages',
        desc: 'Especificar la carpeta de salida, el nombre del proyecto y la rama destino.',
        code: 'npx wrangler pages deploy .vitepress/dist --project-name handbook-explorer --branch main'
      },
      {
        title: '3. Verificación de Salida',
        desc: 'Wrangler confirmará con la URL de producción y el hash del deploy único.',
        code: '✨ Deployment complete! Take a peek over at https://handbook-explorer.pages.dev'
      }
    ],
    proTip: 'Si trabajas en equipo o con IAs, mantén las variables sensibles exclusivamente en .env.local y asegúrate de que esté listado en .gitignore.'
  },
  {
    id: 'r2-upload',
    keywords: ['r2', 'upload', 'imagenes', 'archivos', 'presigned', 'url firmada', 's3', 'bucket', 'cloudflare'],
    title: 'Subida Segura de Archivos a Cloudflare R2 (Presigned URLs)',
    domain: '08_Cloud & 05_Security',
    badgeBg: 'rgba(6, 182, 212, 0.15)',
    badgeColor: '#06b6d4',
    complexity: 'Media (25 min)',
    riskLevel: 'Seguridad / Infra',
    riskClass: 'risk-medium',
    confidence: 98.4,
    diagnosis: 'Permitir a los clientes subir imágenes y PDFs pesados a buckets R2 sin saturar la memoria o CPU de los servidores backend.',
    standards: [
      {
        name: 'PATRON_R2_UPLOAD_SEGURO.md',
        desc: 'Patrón oficial de URLs prefirmadas en Cloudflare Workers y almacenamiento en R2.',
        link: '/08_Cloud/PATRON_R2_UPLOAD_SEGURO'
      },
      {
        name: 'SECRET_LEAK_PREVENTION_STANDARD.md',
        desc: 'Gestión segura de credenciales S3/R2 mediante bindings privados.',
        link: '/05_Security/SECRET_LEAK_PREVENTION_STANDARD'
      }
    ],
    rules: [
      {
        code: 'R2-001',
        statement: 'NUNCA reenviar el binario del archivo a través de la memoria del Worker. Usar Presigned URLs directas.',
        why: 'Procesar uploads en el Worker satura los 128MB de RAM y genera timeouts de CPU en conexiones lentas.'
      },
      {
        code: 'R2-002',
        statement: 'Validar MIME-Type y tamaño máximo en el backend antes de emitir la URL prefirmada.',
        why: 'Evita que atacantes utilicen tu bucket como servidor de distribución de malware o archivos maliciosos.'
      }
    ],
    steps: [
      {
        title: '1. Endpoint en el Worker para Solicitar Upload URL',
        desc: 'El cliente envía el nombre del archivo, tipo de contenido y tamaño. El Worker valida los parámetros.',
        code: 'const { url } = await generateR2PresignedUrl(bucket, fileName, contentType, 300);'
      },
      {
        title: '2. Carga Directa desde el Navegador (PUT directo)',
        desc: 'El frontend envía el archivo directamente a la URL de R2 usando un fetch PUT simple con la barra de progreso.',
        code: 'await fetch(presignedUrl, { method: "PUT", body: file, headers: { "Content-Type": file.type } });'
      },
      {
        title: '3. Notificación y Guardado de Metadata',
        desc: 'Una vez completado el PUT en R2, el cliente envía la confirmación al backend para registrar la URL final en la base de datos.',
        code: 'await db.insert(files).values({ url: `https://cdn.tudominio.com/${fileName}` });'
      }
    ],
    proTip: 'R2 de Cloudflare no cobra tarifas de salida (egress fees), lo que te ahorra hasta un 90% comparado con Amazon AWS S3.'
  }
]

const activeRecipe = computed(() => {
  return recipes.find(r => r.id === activeRecipeId.value) || null
})

function selectRecipe(id) {
  activeRecipeId.value = id
  const target = recipes.find(r => r.id === id)
  if (target) {
    searchQuery.value = target.title
  }
}

function handleSearch() {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    activeRecipeId.value = 'login'
    return
  }

  const match = recipes.find(recipe => {
    if (recipe.title.toLowerCase().includes(query)) return true
    if (recipe.domain.toLowerCase().includes(query)) return true
    return recipe.keywords.some(k => query.includes(k) || k.includes(query))
  })

  if (match) {
    activeRecipeId.value = match.id
  } else {
    activeRecipeId.value = null
  }
}

function clearSearch() {
  searchQuery.value = ''
  activeRecipeId.value = 'login'
}
</script>

<style scoped>
.recipe-router-container {
  margin: 3rem 0;
  padding: 2.5rem;
  background: radial-gradient(circle at top, rgba(255, 107, 0, 0.05) 0%, rgba(20, 20, 20, 0.45) 100%), var(--vp-c-bg-soft);
  border: 1px solid rgba(255, 107, 0, 0.28);
  border-radius: 18px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
}

.recipe-header {
  text-align: center;
  margin-bottom: 2rem;
}

.recipe-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 14px;
  background: rgba(255, 107, 0, 0.12);
  border: 1px solid rgba(255, 107, 0, 0.3);
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  color: #ff6b00;
  letter-spacing: 0.08em;
  margin-bottom: 0.85rem;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: #ff6b00;
  border-radius: 50%;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 107, 0, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(255, 107, 0, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 107, 0, 0); }
}

.recipe-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--vp-c-text-1);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.recipe-subtitle {
  font-size: 1.05rem;
  color: var(--vp-c-text-2);
  max-width: 760px;
  margin: 0 auto;
  line-height: 1.6;
}

.recipe-search-box {
  margin-bottom: 2rem;
}

.search-input-wrapper {
  position: relative;
  max-width: 820px;
  margin: 0 auto 1.25rem;
}

.search-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: #ff6b00;
  pointer-events: none;
}

.recipe-input {
  width: 100%;
  padding: 16px 50px 16px 52px;
  font-size: 1.05rem;
  font-family: 'Inter', sans-serif;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg);
  border: 2px solid rgba(255, 107, 0, 0.3);
  border-radius: 12px;
  outline: none;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.recipe-input:focus {
  border-color: #ff6b00;
  box-shadow: 0 0 0 4px rgba(255, 107, 0, 0.2);
}

.clear-btn {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--vp-c-text-3);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px;
}

.clear-btn:hover {
  color: var(--vp-c-text-1);
}

.quick-pills {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 8px;
  max-width: 900px;
  margin: 0 auto;
}

.pills-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--vp-c-text-3);
  margin-right: 4px;
}

.pill-btn {
  padding: 6px 14px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  border-color: #ff6b00;
  color: #ff6b00;
  transform: translateY(-1px);
}

.pill-btn.active {
  background: rgba(255, 107, 0, 0.15);
  border-color: #ff6b00;
  color: #ff6b00;
  font-weight: 700;
}

.recipe-card {
  background: var(--vp-c-bg);
  border: 1px solid rgba(255, 107, 0, 0.3);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}

.card-top-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-divider);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.domain-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

.complexity-tag, .risk-tag {
  padding: 4px 10px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
}

.risk-critical { border-color: rgba(239, 68, 68, 0.4); color: #ef4444; }
.risk-high { border-color: rgba(249, 115, 22, 0.4); color: #f97316; }
.risk-medium { border-color: rgba(234, 179, 8, 0.4); color: #eab308; }
.risk-low { border-color: rgba(16, 185, 129, 0.4); color: #10b981; }

.confidence-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: #10b981;
}

.conf-dot {
  width: 7px;
  height: 7px;
  background: #10b981;
  border-radius: 50%;
}

.card-title {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--vp-c-text-1);
  margin-bottom: 0.75rem;
  letter-spacing: -0.01em;
}

.card-diagnosis {
  font-size: 1rem;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin-bottom: 1.75rem;
  padding: 12px 16px;
  background: var(--vp-c-bg-soft);
  border-left: 4px solid #ff6b00;
  border-radius: 0 8px 8px 0;
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (max-width: 860px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin-bottom: 1rem;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.standards-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.standard-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.standard-link:hover {
  border-color: #ff6b00;
  background: rgba(255, 107, 0, 0.05);
  transform: translateX(3px);
}

.std-icon {
  font-size: 1.3rem;
}

.std-info {
  flex: 1;
}

.std-name {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 700;
  color: #ff6b00;
}

.std-desc {
  display: block;
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 3px;
  line-height: 1.35;
}

.arrow-icon {
  color: var(--vp-c-text-3);
  font-size: 1rem;
  font-weight: bold;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rule-card {
  padding: 12px;
  background: rgba(239, 68, 68, 0.04);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 10px;
}

.rule-code {
  display: inline-block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 800;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 6px;
}

.rule-statement {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
}

.rule-why {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  line-height: 1.4;
}

.steps-section {
  margin-bottom: 2rem;
}

.steps-timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.step-item {
  display: flex;
  gap: 16px;
}

.step-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: #ff6b00;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 0.95rem;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 0.98rem;
  color: var(--vp-c-text-1);
  display: block;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.88rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  margin-bottom: 8px;
}

.step-snippet {
  background: #111;
  color: #f1f1f1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  overflow-x: auto;
  margin: 6px 0 0;
}

.pro-tip-box {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px 18px;
  background: rgba(255, 107, 0, 0.08);
  border: 1px solid rgba(255, 107, 0, 0.25);
  border-radius: 12px;
}

.tip-icon {
  font-size: 1.4rem;
}

.tip-body {
  font-size: 0.88rem;
  color: var(--vp-c-text-1);
  line-height: 1.5;
}

.tip-body strong {
  color: #ff6b00;
}

.no-recipe-card {
  text-align: center;
  padding: 3rem 1.5rem;
  background: var(--vp-c-bg);
  border: 1px dashed var(--vp-c-divider);
  border-radius: 16px;
}

.no-recipe-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.suggested-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 1.5rem;
}

.action-btn {
  padding: 8px 18px;
  background: #ff6b00;
  color: #fff;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9rem;
}

.action-btn.alt {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-divider);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
