# 29 — Roadmap (síntesis de la auditoría 2026-07-20)

> Priorizado con la fórmula de 05-Decision-Matrix. Regla de ejecución: máximo 2 ítems en curso;
> cada ítem cerrado se re-mide contra 24-Metrics y se anota el resultado ANTES de abrir el
> siguiente. Estados: `pendiente → en curso → cerrado: mejoró/sin efecto/empeoró`.

## P0 — Esta semana (protegen dinero y trabajo)

### R1 · Cerrar críticos de seguridad S1-S4 · **pendiente**
Rotar claves de webtradingpro, desstagear .env de IA-compilation, arreglar RLS de
JeilinOrganizacion (escalación a admin + anon abierto). Detalle en [16-Security.md](16-Security.md).
**Esfuerzo:** S (2-3h) · **Riesgo si no:** cuentas de trading/DB comprometibles hoy.
**Éxito:** Security Score 0→88 · S1-S4 = CERRADO.

### R2 · Rescate de trabajo en riesgo · **pendiente**
uñapp (git corrupto + 32 archivos): zip del working tree → repo nuevo → remote → push.
Commitear+push los pendientes: Dania Nails Beauty (37), MadelineWeb (34), JCDigital (16, incluye
el rediseño), gabyandbeautyacademy (14), Xworked (54), ingenusfx (134).
**Esfuerzo:** S · **Éxito:** 0 repos con >10 cambios sin push · uñapp recuperado.

### R3 · workers-template y mcps a git+remote · **pendiente**
La infra más reutilizada no tiene backup. Cuidado con S9 (crear .gitignore ANTES del init en
mcp-jcdigital — tiene TELEGRAM_TOKEN en .env).
**Esfuerzo:** XS · **Éxito:** ambos en github.com/JCDIGITALL, privados.

## P1 — Este mes (multiplican velocidad)

### R4 · A2: CI/CD en repos activos · **pendiente**
ci.yml (T3) en: JCDigital+worker-pago primero, luego los ~8 activos restantes. Workers se
despliegan solos en push.
**Esfuerzo:** S/repo · **Éxito:** Scalability 30→42 · 2 semanas sin deploy manual.

### R5 · A1: script de proyecto nuevo · **pendiente**
`new-project.ps1`: plantilla + git + gh repo + docs (T1/T2) + ci.yml + registro en MCP.
**Esfuerzo:** S · **Éxito:** próximo proyecto nace conforme en <10 min.

### R6 · Tests de dinero en worker-pago (17-Testing §2) · **pendiente**
~6 tests vitest (orden, firma, estados, descarga). IA básica genera, potente revisa.
**Esfuerzo:** S · **Éxito:** en CI, verdes; prerequisito para auto-deploy del worker de pagos.

### R7 · Decisión de portafolio trading (CTO→Jeilin) · **pendiente**
8 proyectos, 3 solapados, ingreso no evidente. Propuesta: jonnyTrader flagship, resto archivo o
fusión. **Es una decisión de Jeilin** — el roadmap solo la agenda.
**Esfuerzo:** decisión + XS de ejecución · **Éxito:** línea trading = 1-2 proyectos activos.

### R8 · A4: README+CLAUDE.md+.env.example en los ~10 activos · **pendiente**
Lote de IA básica con T1/T2. Incluye S6 (gitignores) en el mismo barrido.
**Esfuerzo:** S (IA) · **Éxito:** Documentation Score ~10→100 en activos.

## P2 — Este trimestre (consolidan y monetizan)

### R9 · A5: plantilla vertical beauty · **pendiente**
El activo de negocio #1: 8 proyectos del nicho → 1 plantilla configurable (sitio+citas+catálogo).
**Esfuerzo:** L · **Éxito:** próximo cliente beauty entregado en días, no semanas.

### R10 · Catálogo de la tienda ×4 con E:\Pruebas · **pendiente**
Empaquetar los 10 mejores estilos UI ya construidos como plantillas ($12-20). Bloqueador externo:
verificación Wompi (seguimiento en 21-Business).
**Esfuerzo:** M · **Éxito:** 10+ productos publicados.

### R11 · A3+A6: guardián de commits + alertas de workers (vía send_telegram/n8n) · **pendiente**
**Éxito:** aviso automático de trabajo sin push y de errores de producción.

### R12 · Consolidación de discos + limpieza (regla 07 + A7) · **pendiente**
Duplicados C:/E: resueltos, 1.7GB liberados, archivo unificado en 05_Archive.
**Esfuerzo:** M (mover con cuidado) · **Éxito:** un proyecto = una ruta.

### R13 · Cerrar S5-S9 (seguridad media) + estándar 05_Security del handbook · **pendiente**
Standards-Agent redacta el Nivel 1 con las reglas ya probadas por la auditoría.

## Registro de re-evaluación (se llena al cerrar cada ítem)

| Ítem | Fecha cierre | Métrica prometida | Antes → Después | Veredicto |
|---|---|---|---|---|
| — | — | — | — | — |
