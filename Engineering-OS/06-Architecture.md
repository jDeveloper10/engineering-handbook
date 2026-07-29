# 06 — Architecture (mapa real del ecosistema)

> Fotografía verificada por auditoría (2026-07-20). El Architecture-Agent la mantiene; toda
> decisión nueva se registra como T8 aquí o en el CLAUDE.md del proyecto.

## Arquitectura de referencia (el patrón que SÍ funciona — replicar)

```
[Usuario] → Cloudflare Pages (React+Vite, deploy por push a main)
              └→ Worker del producto (API, wrangler.jsonc, secrets vía wrangler secret)
                   ├→ KV (estado pequeño: órdenes, sesiones)
                   ├→ R2 (archivos: productos vendidos)
                   └→ Terceros (Wompi con firma verificada + CORS allowlist)
```

Implementación de referencia: **JCDigital + worker-pago** — el informe de seguridad lo confirmó
como el mejor construido del ecosistema (timingSafeEqual, allowlist, secrets fuera del repo).
`workers-template` (6 workers por dominio) es la generalización de este patrón.

## Estado real por capa

| Capa | Realidad 2026-07 | Veredicto |
|---|---|---|
| Frontend | React+Vite en ~80% de los ~95 proyectos; TS solo en 3-4 | ✅ consistente; TS pendiente |
| Hosting | Pages (nuevo) + Firebase Hosting (legacy *.web.app) | ⚠️ dual — migración oportunista (12-Firebase) |
| Backend | Workers (7+ proyectos) + Express suelto (n8n server, notifiers) | ✅ dirección correcta |
| Datos | Supabase (nuevo) + Firestore (legacy) + híbrido en jonnyTrader | ⚠️ híbridos = doble mantenimiento |
| Pagos | Wompi (worker-pago ✅) · NOWPayments (ingenusfx, firma no constant-time) | ⚠️ unificar patrón del template |
| Automatización | n8n en VPS Contabo + Baileys + MCPs propios | 🔴 sub-usado (piezas montadas sin flujo) |
| Discos | C:\trabajo (activo) / E:\ (todo lo demás) con árboles duplicados | 🔴 resuelto por regla 07, falta ejecutar |

## ¿Escala esta arquitectura? (respuesta CTO, honesta)

**El stack técnico escala; el sistema operativo humano no escalaba — por eso existe este OS.**
Pages+Workers+Supabase aguantan 100× el tráfico actual sin cambios. Lo que no escala:
95 proyectos sin inventario, 4 pasos del pipeline inexistentes (testing, CI, monitoreo, retro),
y conocimiento no registrado. Conclusión de auditoría: **cero necesidad de re-arquitectura
técnica; toda la inversión va a proceso (CI, git, automatización) y consolidación.**

## Qué sobra / qué falta

**Sobra:** Firebase en proyectos nuevos · 2 de las 3 plataformas de trading solapadas ·
XAMPP/pnpm-store/instaladores muertos (1.7GB) · duplicados C:/E:.
**Falta:** CI/CD (0 de 95) · tests de dinero · monitoreo con alertas · registro de decisiones
(nace con este OS).

## Decisiones de arquitectura registradas (T8 resumidos)

- **[2026-07-20]** Nuevos proyectos: patrón JCDigital (Pages + worker por producto). Alternativa
  descartada: monorepo único (rompe el aislamiento por cliente).
- **[2026-07-20]** workers-template pasa a git y se vuelve la fuente de todo worker nuevo.
- **[2026-07-20]** La línea trading requiere decisión de consolidación (propuesta CTO en
  29-Roadmap R7) — congelada la inversión en las plataformas no-flagship hasta decidir.
