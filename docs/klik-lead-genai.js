const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Lead GenAI — KLIK Energy";

const C = {
  bg:       "111111",
  coral:    "E8474A",
  white:    "FFFFFF",
  gray:     "888888",
  gray2:    "555555",
  card:     "1A1A1A",
  border:   "2C2C2C",
  green:    "4CAF50",
  darkGreen:"0D1F10",
  darkCoral:"1F0E0F",
  li:       "0A66C2",
  wa:       "25D366",
};

const slide = pres.addSlide();
slide.background = { color: C.bg };

// ═══════════════════════════════════════════════════════════════
// HEADER
// ═══════════════════════════════════════════════════════════════
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.28, y: 0.16, w: 0.05, h: 0.5,
  fill: { color: C.coral }, line: { color: C.coral },
});
slide.addText("Lead GenAI", {
  x: 0.42, y: 0.16, w: 4, h: 0.3,
  fontSize: 24, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
});
slide.addText("GENERACIÓN DE CLIENTES B2B  ·  KLIK ENERGY  ·  klikenergy.com", {
  x: 0.42, y: 0.44, w: 7, h: 0.2,
  fontSize: 7, color: C.gray, fontFace: "Calibri", charSpacing: 1, margin: 0,
});
slide.addShape(pres.shapes.LINE, {
  x: 0.28, y: 0.72, w: 9.44, h: 0,
  line: { color: C.border, width: 1 },
});

// ═══════════════════════════════════════════════════════════════
// ROW 1: COSTO DEL LEAD (left 2.6") | PIPELINE (right 6.9")
// ═══════════════════════════════════════════════════════════════
const r1y = 0.82;
const r1h = 1.12;

// ── Cost label
slide.addText("COSTO POR LEAD", {
  x: 0.28, y: r1y, w: 2.55, h: 0.17,
  fontSize: 6, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
});

// $190 card
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.28, y: r1y + 0.22, w: 1.12, h: 0.84,
  fill: { color: C.card }, line: { color: C.border, width: 1 },
});
slide.addText("$190", {
  x: 0.28, y: r1y + 0.25, w: 1.12, h: 0.44,
  fontSize: 22, bold: true, color: C.gray2, fontFace: "Calibri", align: "center", margin: 0,
});
slide.addText("USD / lead\nPromedio industria", {
  x: 0.28, y: r1y + 0.67, w: 1.12, h: 0.3,
  fontSize: 5.5, color: C.gray, fontFace: "Calibri", align: "center", margin: 0,
});

// Arrow
slide.addText("→", {
  x: 1.44, y: r1y + 0.46, w: 0.26, h: 0.26,
  fontSize: 12, color: C.coral, fontFace: "Calibri", align: "center", margin: 0,
});

// $10 card
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1.74, y: r1y + 0.22, w: 1.12, h: 0.84,
  fill: { color: C.darkCoral }, line: { color: C.coral, width: 1.5 },
});
slide.addText("$10", {
  x: 1.74, y: r1y + 0.25, w: 1.12, h: 0.44,
  fontSize: 22, bold: true, color: C.coral, fontFace: "Calibri", align: "center", margin: 0,
});
slide.addText("USD / lead\nLead GenAI", {
  x: 1.74, y: r1y + 0.67, w: 1.12, h: 0.3,
  fontSize: 5.5, color: C.coral, fontFace: "Calibri", align: "center", margin: 0,
});

// ── Vertical separator
slide.addShape(pres.shapes.LINE, {
  x: 3.05, y: r1y, w: 0, h: r1h,
  line: { color: C.border, width: 1 },
});

// ── Pipeline label
slide.addText("PIPELINE LEAD GENAI · 7 FUENTES DE DESCUBRIMIENTO", {
  x: 3.18, y: r1y, w: 6.54, h: 0.17,
  fontSize: 6, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
});

// Pipeline steps
const pipeSteps = [
  { icon: "🔍", label: "7 Fuentes\nDescubrimiento" },
  { icon: "🔗", label: "HubSpot\nDedup" },
  { icon: "📋", label: "RUES\nNIT" },
  { icon: "👔", label: "Sales\nNavigator" },
  { icon: "✨", label: "BC · Apollo\nLusha" },
  { icon: "📊", label: "Scoring\nIA" },
  { icon: "📣", label: "Outreach\n4 etapas" },
];
const pStartX = 3.18;
const pY = r1y + 0.22;
const pBoxW = 0.75;
const pBoxH = 0.84;
const pSlotW = 6.54 / pipeSteps.length;

pipeSteps.forEach((step, i) => {
  const sx = pStartX + i * pSlotW;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: sx, y: pY, w: pBoxW, h: pBoxH,
    fill: { color: C.card }, line: { color: C.border, width: 1 },
  });
  slide.addText(step.icon, {
    x: sx, y: pY + 0.07, w: pBoxW, h: 0.26,
    fontSize: 11, align: "center", margin: 0,
  });
  slide.addText(step.label, {
    x: sx, y: pY + 0.36, w: pBoxW, h: 0.42,
    fontSize: 5.5, color: C.white, fontFace: "Calibri", align: "center", margin: 0,
  });
  if (i < pipeSteps.length - 1) {
    slide.addText("→", {
      x: sx + pBoxW, y: pY + 0.28, w: pSlotW - pBoxW, h: 0.26,
      fontSize: 8, color: "444444", fontFace: "Calibri", align: "center", margin: 0,
    });
  }
});

// ═══════════════════════════════════════════════════════════════
// ROW 2: OUTREACH (left 4.7") | MQL ROUTING (right 5.0")
// ═══════════════════════════════════════════════════════════════
const r2y = r1y + r1h + 0.14;
const r2h = 2.92;

// ── Outreach label
slide.addText("OUTREACH OUTBOUND · SECUENCIA DE ETAPAS", {
  x: 0.28, y: r2y, w: 4.6, h: 0.17,
  fontSize: 6, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
});

const channels = [
  { etapa: "ETAPA 1", name: "LinkedIn",  color: C.li,    steps: "Visualización perfil  →  Solicitud con mensaje  →  Interacción con post  →  Follow-up DM" },
  { etapa: "ETAPA 2", name: "Email",     color: C.coral, steps: "Verificación email  →  Personalización con datos del pipeline  →  Envío CTA Calendly  →  Follow-up 48h" },
  { etapa: "ETAPA 3", name: "WhatsApp",  color: C.wa,    steps: "Mensaje de apertura  →  Conversación proactiva  →  Envío 1-pager KLIK  →  Agendar llamada" },
  { etapa: "ETAPA 4", name: "Llamada",   color: "FF8C8E",steps: "Ficha completa del prospecto  →  Pitch 30 seg  →  Identificar pain point energético  →  Agendar demo KLIK" },
];

const chH = (r2h - 0.22 - 3 * 0.06) / 4;
channels.forEach((ch, i) => {
  const cy = r2y + 0.22 + i * (chH + 0.06);
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.28, y: cy, w: 4.6, h: chH,
    fill: { color: C.card }, line: { color: C.border, width: 1 },
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.28, y: cy, w: 0.04, h: chH,
    fill: { color: ch.color }, line: { color: ch.color },
  });
  slide.addText(ch.etapa, {
    x: 0.36, y: cy + 0.04, w: 0.72, h: 0.13,
    fontSize: 5, color: ch.color, fontFace: "Calibri", bold: true, charSpacing: 0.3, margin: 0,
  });
  slide.addText(ch.name, {
    x: 0.36, y: cy + 0.16, w: 1.1, h: 0.2,
    fontSize: 9.5, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  slide.addText(ch.steps, {
    x: 1.52, y: cy + 0.04, w: 3.3, h: chH - 0.08,
    fontSize: 6, color: "999999", fontFace: "Calibri", valign: "middle", margin: 0,
  });
});

// ── Vertical separator
slide.addShape(pres.shapes.LINE, {
  x: 5.08, y: r2y, w: 0, h: r2h,
  line: { color: C.border, width: 1 },
});

// ── MQL Routing label
slide.addText("ROUTING DE MQLs → PRODUCTO KLIK", {
  x: 5.2, y: r2y, w: 4.52, h: 0.17,
  fontSize: 6, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
});

// Decision diamond box
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.9, y: r2y + 0.24, w: 3.12, h: 0.4,
  fill: { color: "1F0F10" }, line: { color: C.coral, width: 1.5 },
});
slide.addText("¿Consumo ≥ 55 MWh/mes?  (CREG)", {
  x: 5.9, y: r2y + 0.24, w: 3.12, h: 0.4,
  fontSize: 8.5, bold: true, color: C.coral, fontFace: "Calibri",
  align: "center", valign: "middle", margin: 0,
});

// Branch arrows / labels
slide.addText("SÍ  ↙", {
  x: 5.2, y: r2y + 0.72, w: 1.8, h: 0.2,
  fontSize: 7.5, color: C.green, bold: true, fontFace: "Calibri", align: "center", margin: 0,
});
slide.addText("NO  ↘", {
  x: 7.92, y: r2y + 0.72, w: 1.8, h: 0.2,
  fontSize: 7.5, color: C.coral, bold: true, fontFace: "Calibri", align: "center", margin: 0,
});

const branchH = r2h - 0.97;

// MNR branch card
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: r2y + 0.97, w: 2.18, h: branchH,
  fill: { color: C.darkGreen }, line: { color: C.green, width: 1 },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: r2y + 0.97, w: 2.18, h: 0.24,
  fill: { color: "164020" }, line: { color: C.green, width: 0 },
});
slide.addText("MERCADO NO REGULADO", {
  x: 5.2, y: r2y + 0.97, w: 2.18, h: 0.24,
  fontSize: 6, color: C.green, fontFace: "Calibri", bold: true,
  align: "center", valign: "middle", charSpacing: 0.3, margin: 0,
});
slide.addText("≥ 55,000 kWh/mes", {
  x: 5.2, y: r2y + 1.24, w: 2.18, h: 0.18,
  fontSize: 6.5, color: "666666", fontFace: "Calibri", align: "center", margin: 0,
});
slide.addText([
  { text: "Pitch: ", options: { bold: true, color: "CCCCCC" } },
  { text: "Upselling en grandes organizaciones · tarifa bilateral negociada", options: { color: "888888" } },
], {
  x: 5.26, y: r2y + 1.44, w: 2.06, h: 0.56,
  fontSize: 6, fontFace: "Calibri", margin: 0,
});
slide.addShape(pres.shapes.LINE, {
  x: 5.3, y: r2y + 2.02, w: 2.0, h: 0,
  line: { color: "2A4A2A", width: 1 },
});
slide.addText("Comercialización · DDV · RD", {
  x: 5.2, y: r2y + 2.06, w: 2.18, h: branchH - 1.09 - 0.12,
  fontSize: 6.5, color: C.green, fontFace: "Calibri", italic: true, align: "center", valign: "middle", margin: 0,
});

// MR branch card
slide.addShape(pres.shapes.RECTANGLE, {
  x: 7.54, y: r2y + 0.97, w: 2.18, h: branchH,
  fill: { color: C.darkCoral }, line: { color: C.coral, width: 1 },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: 7.54, y: r2y + 0.97, w: 2.18, h: 0.24,
  fill: { color: "3A1214" }, line: { color: C.coral, width: 0 },
});
slide.addText("MERCADO REGULADO", {
  x: 7.54, y: r2y + 0.97, w: 2.18, h: 0.24,
  fontSize: 6, color: C.coral, fontFace: "Calibri", bold: true,
  align: "center", valign: "middle", charSpacing: 0.3, margin: 0,
});
slide.addText("< 55,000 kWh/mes", {
  x: 7.54, y: r2y + 1.24, w: 2.18, h: 0.18,
  fontSize: 6.5, color: "666666", fontFace: "Calibri", align: "center", margin: 0,
});
slide.addText([
  { text: "Pitch: ", options: { bold: true, color: "CCCCCC" } },
  { text: "Reducción de costos sin cambiar comercializador · tarifa CREG", options: { color: "888888" } },
], {
  x: 7.6, y: r2y + 1.44, w: 2.06, h: 0.56,
  fontSize: 6, fontFace: "Calibri", margin: 0,
});
slide.addShape(pres.shapes.LINE, {
  x: 7.62, y: r2y + 2.02, w: 2.0, h: 0,
  line: { color: "4A2022", width: 1 },
});
slide.addText("Comercialización · DDV · RD", {
  x: 7.54, y: r2y + 2.06, w: 2.18, h: branchH - 1.09 - 0.12,
  fontSize: 6.5, color: C.coral, fontFace: "Calibri", italic: true, align: "center", valign: "middle", margin: 0,
});

// ═══════════════════════════════════════════════════════════════
// FOOTER
// ═══════════════════════════════════════════════════════════════
const ftY = 5.1;
const ftH = 0.525;
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: ftY, w: 10, h: ftH,
  fill: { color: C.coral }, line: { color: C.coral },
});
slide.addText("Prospección → Lead → MQL", {
  x: 0.3, y: ftY, w: 5.5, h: ftH,
  fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0,
});
slide.addText("en menos de", {
  x: 5.8, y: ftY + 0.02, w: 1.5, h: ftH - 0.04,
  fontSize: 8, color: "FFCCCC", fontFace: "Calibri", align: "right", valign: "middle", margin: 0,
});
slide.addText("1 MES", {
  x: 7.3, y: ftY, w: 2.4, h: ftH,
  fontSize: 20, bold: true, color: C.white, fontFace: "Calibri", align: "right", valign: "middle", margin: 0,
});

pres.writeFile({ fileName: "/Users/juanjosetrujillo/Documents/Ai programas/klik-energy-lead-genai.pptx" });
console.log("Done.");
