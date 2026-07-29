---
title: "Estándar de Formateo de Números, Moneda y Fechas"
category: 01_Frontend
doc_type: estandar
tags: [frontend, formato, intl, moneda, fechas]
summary: "Cómo se muestran números, moneda, porcentajes y fechas en la interfaz: uso de la API Intl, fecha absoluta frente a relativa y manejo de zona horaria."
keywords: [intl, numberformat, datetimeformat, moneda, porcentaje, fechas, timezone]
updated: 2026-07-27
status: current
---

# FRONTEND FORMATTING STANDARD (Números, Moneda y Fechas)

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> Existe porque este es un error que la IA (y el propio handbook) comete por defecto: el dashboard de prueba de este repo (`pruebas/test_dashboard_standard.html`) muestra `"Actualizado hace 2 min"` como texto **literal** escrito a mano en el HTML, no calculado — exactamente el anti-patrón que esta sección corrige. "Se ve bien en la demo" no es lo mismo que "funciona con datos reales".

---

## 1. Regla principal

**[REQUIRED]** Todo número, moneda o fecha mostrado al usuario se formatea con las APIs de internacionalización nativas del navegador (`Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`) — nunca con concatenación manual de strings.

```
❌ "$" + amount.toString()
❌ date.getMonth() + 1 + "/" + date.getDate() + "/" + date.getFullYear()
✅ new Intl.NumberFormat("es-CO", { style: "currency", currency: "USD" }).format(amount)
✅ new Intl.DateTimeFormat("es-CO", { dateStyle: "long" }).format(date)
```

**Por qué:** la concatenación manual asume un formato (agrupación de miles, orden día/mes/año, símbolo de moneda) que varía por región del usuario — `1,234.56` en `en-US` es `1.234,56` en `es-CO`. `Intl` ya resuelve esto correctamente sin librerías externas.

---

## 2. Números

**[REQUIRED]** Agrupación de miles y decimales según el locale del usuario, no asumidos a mano.

```js
new Intl.NumberFormat("es-CO").format(1234567) // "1.234.567"
new Intl.NumberFormat("en-US").format(1234567) // "1,234,567"
```

---

## 3. Moneda

**[REQUIRED]** `Intl.NumberFormat` con `style: "currency"` y el código de moneda explícito — nunca un símbolo `"$"` pegado manualmente al número (¿dólar de qué país? un `$` ambiguo es un problema real en productos con usuarios en Panamá/Colombia/LatAm).

```js
new Intl.NumberFormat("es-CO", { style: "currency", currency: "USD" }).format(2340)
```

**[REQUIRED]** Decimales definidos explícitamente (`minimumFractionDigits`/`maximumFractionDigits`) — algunas monedas no llevan decimales (JPY), otras sí (USD) y el default puede no ser el que el producto necesita.

---

## 4. Porcentajes

**[REQUIRED]** `Intl.NumberFormat` con `style: "percent"` en vez de concatenar `"%"` a mano.

```js
new Intl.NumberFormat("es-CO", { style: "percent", maximumFractionDigits: 1 }).format(0.78) // "78%"
```

**[REQUIRED]** Documentar explícitamente si la función que formatea espera el valor en escala 0-1 o 0-100 — es la fuente de bugs más común en este punto (mostrar `"7800%"` por no dividir entre 100, o `"0.78%"` por dividir de más). `Intl` con `style: "percent"` espera 0-1; si el dato viene de una API en 0-100, se divide antes de formatear, no después.

---

## 5. Fechas — absoluta vs relativa

**[REQUIRED]** Se elige el tipo de fecha según qué comunica mejor, no por costumbre:

- **Fecha absoluta** (`"9 de julio de 2026"`) para eventos que no son recientes — nadie quiere leer "hace 47 días", prefiere la fecha real.
- **Fecha relativa** (`"hace 2 minutos"`) para actividad reciente (hasta ~24-48h) — comunica frescura mejor que una marca de tiempo exacta.

```js
new Intl.DateTimeFormat("es-CO", { dateStyle: "long" }).format(date)
// "9 de julio de 2026"

const rtf = new Intl.RelativeTimeFormat("es", { numeric: "auto" });
rtf.format(-2, "minute") // "hace 2 minutos"
```

**[REQUIRED]** Una fecha relativa se **calcula**, nunca se hardcodea como texto fijo — un `"Actualizado hace 2 min"` escrito a mano queda desactualizado en el instante en que el usuario sigue mirando la pantalla.

---

## 6. Zona horaria

**[REQUIRED]** Las fechas se muestran en la zona horaria del usuario (`timeZone` en las opciones de `Intl.DateTimeFormat`, o la que resuelva el entorno por defecto) — nunca UTC crudo sin conversión, salvo un contexto explícitamente técnico (logs internos, no cara al usuario).

---

## 7. Centralización

**[RECOMMENDED]** Estas funciones viven en utilidades compartidas (`formatCurrency`, `formatDate`, `formatRelativeTime` en `shared/utils/`, ver `FRONTEND_ENGINEERING_STANDARD.md` sección 03) — no se reimplementa una llamada a `Intl` ligeramente distinta en cada componente que necesita mostrar un número.

```ts
// shared/utils/format.ts
export const formatCurrency = (amount: number, currency = "USD") =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency }).format(amount);
```

---

## 8. Anti-patrones

- ❌ `"$" + amount` en vez de `Intl.NumberFormat` con `style: "currency"`.
- ❌ Fecha relativa hardcodeada como texto fijo (`"hace 2 min"` escrito a mano, no calculado).
- ❌ `date.toString()` o `date.toISOString()` mostrado directo al usuario.
- ❌ Porcentaje sin aclarar si la función espera 0-1 o 0-100.
- ❌ Fechas en UTC mostradas sin convertir a la zona horaria del usuario.
- ❌ La misma lógica de formato reimplementada distinta en cada componente.

---

## Checklist rápido

- [ ] ¿Todo número/moneda/fecha usa `Intl`, no concatenación manual de strings?
- [ ] ¿Moneda con código explícito (`currency: "USD"`), no un `$` ambiguo?
- [ ] ¿Porcentaje con la escala de entrada (0-1 vs 0-100) documentada y correcta?
- [ ] ¿Fecha relativa calculada en tiempo real, no un texto fijo?
- [ ] ¿Fechas en la zona horaria del usuario, no UTC crudo?
- [ ] ¿Funciones de formato centralizadas en `shared/utils/`, no reimplementadas por componente?
