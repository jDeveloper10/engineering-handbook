# 21 — Business

> El negocio real observado en la auditoría, y las reglas para que la ingeniería produzca ingresos
> y no solo repos. Donde falta un dato de negocio, está marcado — no inventado.

## Fotografía del negocio (2026-07, derivada del inventario)

| Línea | Evidencia | Lectura |
|---|---|---|
| **Clientes belleza/estética** | ~8 proyectos (Dania Nails ×2, Gaby ×3, Maquillaje store, sarabeautycitas, uñapp, KeitlinStudio) | Nicho real y repetido — el mercado más probado que tiene Jeilin |
| **Clientes varios** | Clínica Salud Norte, ibarra y asociados, Xploretourspty, YingMARKETPLACE, legacy-club… | Cola larga de proyectos one-off |
| **Productos propios** | Tienda de plantillas (Wompi), Balance360, TiketsSystem, DeliveryApp, Planilla, X-Dorada-Reel | Muchos iniciados, pocos monetizando |
| **Trading** | jonnyTrader (flagship), ingenusfx, +6 | Alta inversión de tiempo; monetización no evidente en el código |

`DATO FALTANTE:` ingresos por línea, tarifa/hora efectiva, precios cobrados por sitio cliente.
Sin esos 3 números el ROI de las recomendaciones usa estimados — pedirlos una vez y fijarlos aquí.

## Lecturas estratégicas (para validar con Jeilin, no dogma)

1. **El nicho beauty es la mina probada.** 8 proyectos del mismo vertical = demanda real y código
   repetible. La jugada de proceso: consolidar una **plantilla vertical "sitio de belleza + citas
   + tienda"** (Nivel 3 del handbook) y venderla como producto configurable — el costo marginal
   del sitio #9 debería ser horas, no semanas.
2. **La tienda de plantillas es el producto con mejor apalancamiento** (se construye una vez, se
   vende N veces, ya tiene pasarela). Bloqueador actual: verificación del comercio Wompi.
3. **El portafolio de trading necesita una decisión**: 8+ proyectos solapados (3 plataformas
   parecidas detectadas). Elegir 1 flagship (jonnyTrader es el más completo) y archivar o fusionar
   el resto — es la mayor fuga de foco del ecosistema.

## Reglas de negocio para las IAs

- **[REQUIRED]** Toda feature propuesta responde: ¿quién paga por esto o qué métrica de negocio
  mueve (ventas, retención, leads)? "Estaría cool" no es respuesta.
- **[REQUIRED]** Proyecto cliente nuevo: precio y alcance escritos ANTES de codear (plantilla PRD
  de [26-Templates.md](26-Templates.md)); el cotizador de jcdigital ya define los rangos
  ($150-$350) — respetarlos o actualizarlos, no improvisarlos por chat.
- **[REQUIRED]** Los detectores de 03-Global-Rules incluyen oportunidades de negocio: código
  construido para un cliente que se puede generalizar y revender se registra aquí.
- **[RECOMMENDED]** Antes de construir un producto propio nuevo: ¿hay 3 clientes potenciales
  identificables con nombre? Si no, va a `E:\Pruebas` como experimento, no al pipeline completo.
