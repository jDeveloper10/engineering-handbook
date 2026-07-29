---
title: "Patrón: Generación de PDFs en el Edge"
category: 08_Cloud
tags: [cloudflare-workers, edge, pdf, streaming]
summary: "Generar PDFs en el edge sin Puppeteer: llenado de plantillas estáticas con pdf-lib como opción recomendada, y la API de Browser Rendering cuando se necesita convertir HTML."
keywords: [cloudflare-workers, edge, pdf, streaming, generacion, pdfs, generar, puppeteer, llenado, plantillas, estaticas, pdf-lib, opcion, recomendada]
updated: 2026-07-27
status: current
---

# Patrón: Generación de PDFs en el Edge (Cloudflare Workers)

## El Problema
En un entorno tradicional de Node.js, la generación de PDFs suele hacerse con herramientas pesadas como Puppeteer (Chromium headless) o librerías masivas como `pdfkit`. En Cloudflare Workers (Edge), tenemos límites estrictos:
- Sin Node.js nativo (V8 Isolate puro).
- 128MB de RAM máxima.
- 30s de tiempo de CPU.
- Tamaño del worker limitado a unos pocos MBs.

## Opción 1 (Recomendada): Llenado de Plantillas Estáticas con `pdf-lib`

Esta es la forma más rápida y menos costosa en memoria. Consiste en tener una plantilla PDF base (diseñada en Illustrator/Canva y guardada en R2), cargarla en el Worker, inyectar el texto dinámico y devolverla.

**Librería soportada en Edge:** `pdf-lib` (versión pequeña).

### 1. Código del Worker

```javascript
import { PDFDocument, rgb } from 'pdf-lib';

export async function generateProposalPDF(env, proposalData) {
  // 1. Obtener la plantilla base desde el bucket R2 (rápido y no gasta memoria a largo plazo)
  const templateObject = await env.TEMPLATES_BUCKET.get('proposal_template.pdf');
  if (!templateObject) throw new Error("Template no encontrado");
  
  const templateBytes = await templateObject.arrayBuffer();

  // 2. Cargar el documento en pdf-lib
  const pdfDoc = await PDFDocument.load(templateBytes);
  const pages = pdfDoc.getPages();
  const firstPage = pages[0];

  // 3. Escribir texto dinámico
  firstPage.drawText(`Cliente: ${proposalData.client_name}`, {
    x: 50,
    y: 700,
    size: 14,
    color: rgb(0, 0.53, 0.71),
  });

  firstPage.drawText(`Total: $${(proposalData.total_cents / 100).toFixed(2)}`, {
    x: 50,
    y: 650,
    size: 12,
  });

  // 4. Guardar bytes finales
  const pdfBytes = await pdfDoc.save();

  // REGLA: SIEMPRE devolver con header Content-Type correcto.
  return new Response(pdfBytes, {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="Propuesta_${proposalData.id}.pdf"`
    }
  });
}
```

### Reglas Inquebrantables para Opción 1

- **[REQUIRED] Límite de tamaño:** El archivo plantilla base no debe superar los 500KB para evitar consumir la memoria limitada (128MB) del Worker durante el parseo.
- **[REQUIRED] Prevención de Memory Leak:** **NUNCA** guardes variables globales con instancias de `PDFDocument` fuera del handler. Las instancias deben ser destruidas por el garbage collector tras finalizar la Request.

---

## Opción 2: Cloudflare Browser Rendering API (HTML to PDF)

Cuando el PDF es demasiado complejo y requiere un diseño responsivo HTML/CSS (facturas complejas, reportes con gráficos), la inyección de texto de `pdf-lib` se vuelve inmanejable. 

Para esto, se utiliza el servicio nativo de **Cloudflare Browser Rendering API**, que permite correr una instancia de Puppeteer alojada en el Edge provista por Cloudflare.

```javascript
import puppeteer from "@cloudflare/puppeteer";

export async function generateHTMLtoPDF(env, htmlContent) {
  // Requiere un binding de browser en wrangler.toml:
  // browser = { binding = "MYBROWSER" }
  
  const browser = await puppeteer.launch(env.MYBROWSER);
  const page = await browser.newPage();
  
  await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
  
  const pdfBuffer = await page.pdf({
    format: 'A4',
    printBackground: true
  });
  
  await browser.close();
  
  return new Response(pdfBuffer, {
    headers: { "Content-Type": "application/pdf" }
  });
}
```

### Límites de la Opción 2
- Solo disponible para planes de pago (Workers Paid).
- Tiene límites de tiempo de vida de la sesión del navegador.
- Es sustancialmente más lento (latencia de segundos vs milisegundos de `pdf-lib`). Usar solo cuando la Opción 1 sea imposible.
