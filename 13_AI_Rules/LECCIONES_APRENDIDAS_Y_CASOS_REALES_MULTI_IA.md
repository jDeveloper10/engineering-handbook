---
title: "Lecciones Aprendidas, Post-Mortems y Patrones de Producción Multi-IA"
category: 13_AI_Rules
doc_type: patron
tags: [post-mortem, lecciones-aprendidas, testing, multi-ia, dolores-de-cabeza, produccion, vitest, cloudflare]
summary: "Catálogo exhaustivo de arquitectura validada (lo bueno), fallos críticos y antipatrones resueltos (lo malo/dolores de cabeza), y doctrina de testing automatizado consolidada en el trabajo real de JDeveloper junto a Claude Code, OpenAI Codex y Antigravity."
keywords: [post-mortem, fake-success, toctou, codemagic, paguelofacil, vitest, cerrojos, iaspro, 4-pruebas]
updated: 2026-09-22
status: current
---

# 🛡️ Lecciones Aprendidas, Post-Mortems y Patrones de Producción Multi-IA

> Este estándar recopila la evidencia empírica extraída de más de 79 sesiones de ingeniería y auditorías de código en proyectos reales (*VíaYa*, *Legacy Club*, *Mónica Academy*, *Keithlin*, *Steven Castillo*). Su propósito es blindar a cualquier IA contra la repetición de errores que costaron horas de depuración y consolidar las arquitecturas que demostraron estabilidad en producción.

---

## 1. LO BUENO: Arquitecturas y Patrones Validados en Producción

Estos patrones han demostrado resistencia contra condiciones de carrera, errores de concurrencia y desincronización entre clientes y servidores.

### Patrón 1.1: Contratos Zod Compartidos en Monorepo (*Single Source of Truth*)
- **REQUIRED:** La validación de tipos, esquemas de entrada y salidas de endpoints debe definirse en un paquete común (ej. `packages/contracts`), importado directamente tanto por el backend (Hono/Cloudflare Worker) como por los clientes (React/Vite y React Native/Expo).
- **Prohibido:** Duplicar interfaces TypeScript a mano en frontend y backend. Si el backend cambia una columna o tipo, el compilador debe fallar de inmediato en el cliente (`tsc --noEmit`).
- **Implementación de referencia:** Validado en *Mónica Academy* y *VíaYa*.

### Patrón 1.2: Transacciones Atómicas en Lote (`DB.batch`) para Idempotencia Financiera
- **REQUIRED:** Toda operación que involucre balance, débito, rendimientos (*yields*) o cambios de estado contable en Cloudflare D1 / SQLite debe ejecutarse en una sola llamada atómica `DB.batch()`.
- **REQUIRED:** La idempotencia debe estar respaldada por restricciones `UNIQUE` en la base de datos (ej. `UNIQUE(assignment_id, period_start)`), jamás verificada únicamente mediante consultas previas en memoria.
- **Implementación de referencia:** Validado en *Legacy Club* (`apps/api/src/services/yields.ts`) tras corregir el riesgo de doble débito por transacciones no atómicas.

### Patrón 1.3: Cerrojos Atómicos con Caducidad TTL para Edición Multi-IA (`iaspro lock`)
- **REQUIRED:** Ningún agente de IA puede modificar un archivo sin antes adquirir un cerrojo atómico vía `lock_manager.sh` / `iaspro lock`.
- **REQUIRED:** Todo cerrojo tiene un tiempo de expiración estricto (*TTL*) de 5 minutos para evitar bloqueos permanentes si una sesión se desconecta.
- **Implementación de referencia:** Protocolo activo en `/home/JDeveloper/Escritorio/ORCHESTRATOR/04_SCRIPTS/` y replicado localmente en cada repositorio en `.orchestration/`.

### Patrón 1.4: Jerarquía de Cierre Unívoco en Metas Multi-IA
- **REQUIRED:** En sprints donde colaboran múltiples IAs (Claude en backend, Codex en web, Antigravity en móvil), solo el coordinador central (**Antigravity**) tiene la potestad de emitir el evento final de éxito:
  ```bash
  intercom send --from antigravity --to all --goal "<meta>" --msg "GOAL_COMPLETED: <resumen>" --status completed
  ```
- **RECOMMENDED:** Claude y Codex deben marcar sus subtareas como `waiting_for_antigravity` y liberar cerrojos antes de desconectarse.

---

## 2. LO MALO: Funcionalidades que Dieron Dolores de Cabeza (Post-Mortems)

Análisis de causas raíz de los incidentes más complejos descubiertos durante el desarrollo y cómo evitarlos.

### Dolor de Cabeza #01: Keychain Aleatorio en CI/CD iOS (*Codemagic*)
- **Contexto:** Compilación y firmado de la app móvil *VíaYa* con extensión de Live Activity en Codemagic.
- **Síntoma:** Error fatal recurrente en CI: `Cannot save Signing Certificates without certificate private key`.
- **Causa Raíz:** El comando `keychain initialize` genera un llavero temporal con un nombre aleatorio cada vez que se ejecuta. Al correr `keychain initialize` en un paso del script y luego llamar a herramientas de Apple (`fetch-signing-files`) en pasos separados, el certificado `.p12` se importaba en un llavero que el paso de compilación final de `xcodebuild` no tenía configurado como predeterminado.
- **Solución Obligatoria:** Unificar inicialización, importación de certificados, inyección de perfiles de aprovisionamiento y llamada de firma en un **único bloque de script continuo**:
  ```bash
  # En codemagic.yaml (flujo atómico de llavero)
  keychain initialize
  keychain add-certificates -c ~/certs/dist.p12 --certificate-password "$CERT_PASS"
  xcode-project use-profiles --project App.xcodeproj
  ```

### Dolor de Cabeza #02: El Antipatrón de Éxito Fingido (*Fake Success y Mocking Tóxico*)
- **Contexto:** Módulos de cuenta, calificaciones y pagos en *VíaYa* y *Mónica Academy*.
- **Síntoma:** Pantallas que mostraban usuarios prefabricados ("Carlos Mendoza"), propinas inventadas o compras confirmadas con un simple temporizador `setTimeout(resolve, 2000)`.
- **Causa Raíz:** Tendencia del modelo de IA a fabricar respuestas positivas cuando un endpoint aún no está cableado o falla, para "evitar mostrar un error".
- **Regla Innegociable:** **Cero éxito fingido.** Si una API falla o no existe, el componente debe mostrar el error real del servidor (HTTP 500/404) y un botón interactivo de reintento. Ocultar un fallo es considerado una regresión de calidad crítica.

### Dolor de Cabeza #03: Vulnerabilidad FB-001 — Retorno de Pasarela sin HMAC (*PagueloFácil*)
- **Contexto:** Pasarela de pago en *VíaYa* y *Mónica Academy*.
- **Síntoma:** Documentado en `FIX_VERIFICATION_REPORT.md` (Severidad P0, STILL_BROKEN por proveedor externo). El retorno del usuario (`RETURN_URL`) expone parámetros en la URL (ej. `?status=Approved&order=123`) sin firma criptográfica HMAC que garantice que provienen del banco.
- **Causa Raíz:** Confiar en el frontend para confirmar transacciones. Un usuario malicioso podría alterar los parámetros en la barra de direcciones y activar un servicio sin pagar.
- **Solución Obligatoria:** El frontend **NUNCA** da por pagada una orden basándose en la URL de retorno. El backend es la única autoridad: debe esperar el webhook asíncrono firmado con secreto compartido o hacer una consulta directa servidor-a-servidor a la API de PagueloFácil antes de liberar el producto/viaje.

### Dolor de Cabeza #04: Condición de Carrera TOCTOU en Retiros (*Legacy Club*)
- **Contexto:** Despacho de rendimientos en `apps/api/src/services/yields.ts`.
- **Síntoma:** Posibilidad de pérdida silenciosa de dinero si ocurría una falla de red entre la inserción del pago y la actualización del saldo.
- **Causa Raíz:** En `payAssignment`, la inserción de `yield_payouts`, el registro contable en `transactions` y la deducción de saldo en `balance_cents` eran tres peticiones HTTP independientes a Cloudflare D1. Si la segunda fallaba, la restricción `UNIQUE` ya se había disparado, impidiendo que reintentos futuros acreditaran el dinero.
- **Solución Obligatoria:** Empaquetar siempre la verificación condicional de saldo y las tres operaciones en una transacción atómica `DB.batch()`.

### Dolor de Cabeza #05: El Parche Cosmético en Maquetación (*Layout Masking*)
- **Contexto:** Ajustes de formulario en *VíaYa* (Sesión `172e609f`).
- **Síntoma:** Cambiar el color de fondo de un contenedor azul a blanco para disimular un margen sobrante fantasma debajo del formulario.
- **Causa Raíz:** Resolver el síntoma visible alterando estilos superficiales en lugar de inspeccionar el cálculo de altura en Flexbox/CSS.
- **Regla:** Queda prohibido alterar colores, opacidades o márgenes negativos para tapar errores de contenedor. Se debe auditar el DOM/árbol de maquetación y corregir la propiedad estructural causante.

### Dolor de Cabeza #06: Filtro de Sockets que Destruye Estados Vacíos Válidos (*Steven Castillo*)
- **Contexto:** Módulo de señales de trading en tiempo real sobre Supabase + Workers.
- **Síntoma:** Las alertas no llegaban y la interfaz no respondía tras desconexiones.
- **Causa Raíz:** La suscripción tenía un filtro `signals.length > 0`. Cuando el mercado no tenía operaciones activas (array con longitud 0), el observable no emitía nada, dejando la aplicación congelada en estado de carga.
- **Solución:** Comprender que `length === 0` es un estado de datos válido (vacío honesto). El flujo debe emitir siempre el array y el frontend debe renderizar su pantalla de "Sin señales activas".

---

## 3. DOCTRINA DE SUITES DE PRUEBA Y QUALITY GATES

Ninguna funcionalidad se declara terminada sin validación automatizada y control de las 4 pruebas canónicas.

### 3.1 Resumen Contable de la Suite Canónica (509 Tests en Vitest)
Basado en la suite de verificación de *VíaYa* (`cd backend && npm test -- --run`):
- **508 PASS / 1 FAIL esperado** (FB-001 por limitación externa de pasarela).
- **36 de 37 archivos de prueba aprobados**.
- **Control de regresiones:** 26 hallazgos de seguridad y flujo verificados contra regresión (`FIXED_VERIFIED`).
- **Typecheck estricto:** 0 errores en TypeScript backend y mobile antes de cualquier commit.

### 3.2 La Regla de las 4 Pruebas Obligatorias por Característica (REQUIRED)
Antes de marcar cualquier tarea como completada, es obligatorio verificar:
1. **Validación de Entradas (*Input Validation*):** Casos extremos, cadenas vacías, payloads gigantes y caracteres especiales.
2. **Caída de Red / Servidor (*Network Resilience*):** Cortar la conexión o forzar un 500; la interfaz debe alertar con claridad y ofrecer un botón de reintento.
3. **Estado Vacío Real (*Honest Empty State*):** Visualización clara cuando la base de datos no contiene registros, sin spinners infinitos ni mocks.
4. **Adaptación Móvil en 375px (*Mobile Viewport*):** Verificación visual comprobada en el ancho de pantalla de un iPhone SE / Android compacto sin desbordes horizontales.

---

## 4. Checklist para la IA antes de decir "Listo"

- [ ] ¿Ejecuté `npx tsc --noEmit` y el resultado fue 0 errores?
- [ ] ¿Corrí la suite de Vitest (`npm test`) y todos los tests pasaron?
- [ ] ¿Verifiqué que no existan `console.log` con datos sensibles ni secretos expuestos?
- [ ] ¿Eliminé todo código simulado (`mock`, `setTimeout`, datos harcodeados)?
- [ ] ¿Comprobé las 4 pruebas (inputs, caída de red, estado vacío, mobile 375px)?
- [ ] Si se editaron archivos concurrentes, ¿liberé todos los cerrojos con `iaspro unlock`?
