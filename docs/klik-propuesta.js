const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Propuesta Comercial — Lead GenAI Orchestrator × KLIK Energy";

const C = {
  bg:     "111111",
  bgL:    "1A1A1A",
  coral:  "E8474A",
  coralD: "1F0E0F",
  white:  "FFFFFF",
  gray:   "888888",
  card:   "1A1A1A",
  border: "2C2C2C",
  green:  "4CAF50",
  greenD: "0D1F10",
  blue:   "2D6BE4",
  blueD:  "0A1A3A",
  gold:   "F5A623",
  goldD:  "1A1200",
};

// Tool costs (COP @ TRM $4,000)
const TOOLS = [
  { name: "Apollo.io",               plan: "Professional",        usd: 79,  cop: 316000 },
  { name: "BetterContact",           plan: "Growth",              usd: 99,  cop: 396000 },
  { name: "Lusha",                   plan: "Team",                usd: 49,  cop: 196000 },
  { name: "Anthropic API (Claude)",  plan: "Usage estimado",      usd: 80,  cop: 320000 },
];
const TOOL_TOTAL_COP = TOOLS.reduce((a, t) => a + t.cop, 0); // 1,824,000
const TOOL_TOTAL_USD = TOOLS.reduce((a, t) => a + t.usd, 0); // 456

// Pricing
const BASE_FEE    = 7500000;  // COP/mes total cobrado
const MY_MARGIN   = BASE_FEE - TOOL_TOTAL_COP; // margen neto fijo
const VAR_PER_MQL = 120000;   // COP por MQL adicional (más allá de 15)
const MQL_BASE    = 15;       // MQLs incluidos en tarifa base

function fmt(n) {
  return "$" + n.toLocaleString("es-CO");
}

function bg(s, c)  { s.background = { color: c || C.bg }; }
function hLine(s, y) { s.addShape(pres.shapes.LINE, { x: 0, y, w: 10, h: 0, line: { color: C.border, width: 0.75 } }); }
function vLine(s, x, y, h) { s.addShape(pres.shapes.LINE, { x, y, w: 0, h, line: { color: C.border, width: 0.75 } }); }

function accentBar(s, x, y, h, color) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.05, h, fill: { color: color || C.coral }, line: { color: color || C.coral } });
}

function coralFooter(s, text) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.225, w: 10, h: 0.4, fill: { color: C.coral }, line: { color: C.coral } });
  s.addText(text, { x: 0.4, y: 5.225, w: 9.2, h: 0.4, fontSize: 8.5, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
}

function tag(s, text, x, y) {
  s.addText(text, { x, y, w: 9, h: 0.2, fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1.2, bold: true, margin: 0 });
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 1 — PORTADA
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);

  s.addShape(pres.shapes.OVAL, { x: -1.5, y: 0.5, w: 5, h: 5, fill: { color: C.coral, transparency: 90 }, line: { color: C.coral, transparency: 100 } });
  s.addShape(pres.shapes.OVAL, { x: 7, y: 2, w: 5, h: 5, fill: { color: C.blue, transparency: 92 }, line: { color: C.blue, transparency: 100 } });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.7, w: 3.0, h: 0.28, fill: { color: C.coralD }, line: { color: C.coral, width: 1 } });
  s.addText("Propuesta Comercial · Confidencial · 2026", { x: 0.5, y: 0.7, w: 3.0, h: 0.28, fontSize: 7, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  s.addText("Lead GenAI Orchestrator", { x: 0.5, y: 1.15, w: 9, h: 0.72, fontSize: 44, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  s.addText("Servicio de Generación de Clientes B2B\npara KLIK Energy", { x: 0.5, y: 1.84, w: 7, h: 0.8, fontSize: 20, color: C.coral, fontFace: "Calibri", margin: 0 });

  s.addText("Sistema de prospección automatizado con IA · 7 fuentes de datos · pipeline completo de enriquecimiento · outreach multicanal · entrega mensual de MQLs calificados.", {
    x: 0.5, y: 2.84, w: 6.2, h: 0.72,
    fontSize: 10, color: C.gray, fontFace: "Calibri", lineSpacingMultiple: 1.5, margin: 0,
  });

  // Two proposal chips
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.72, w: 2.8, h: 0.38, fill: { color: C.coralD }, line: { color: C.coral, width: 1.5 } });
  s.addText("P1 · Prestación de Servicio", { x: 0.5, y: 3.72, w: 2.8, h: 0.38, fontSize: 10, bold: true, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  s.addText("·", { x: 3.38, y: 3.72, w: 0.3, h: 0.38, fontSize: 14, color: C.gray, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 3.72, y: 3.72, w: 2.5, h: 0.38, fill: { color: C.blueD }, line: { color: C.blue, width: 1.5 } });
  s.addText("P2 · Vinculación Laboral", { x: 3.72, y: 3.72, w: 2.5, h: 0.38, fontSize: 10, bold: true, color: "6E9EFF", fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  s.addText("Elaborado por Juan José Trujillo  ·  juanjosetrujillo1209@gmail.com", {
    x: 0.5, y: 4.3, w: 6, h: 0.22,
    fontSize: 7.5, color: "444444", fontFace: "Calibri", margin: 0,
  });

  coralFooter(s, "Confidencial  ·  Uso exclusivo equipo directivo KLIK Energy  ·  Propuesta válida 15 días calendario");
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 2 — P1: COSTOS REALES + ESTRUCTURA DE PRECIO
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5, C.coral);

  tag(s, "P1 — PRESTACIÓN DE SERVICIO · ESTRUCTURA DE PRECIO", 0.44, 0.15);
  s.addText("Lo que cuesta operar el sistema", { x: 0.44, y: 0.33, w: 9, h: 0.38, fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  hLine(s, 0.76);

  // Tool costs table
  s.addText("COSTOS DE PLATAFORMAS (incluidos en la tarifa)", { x: 0.3, y: 0.84, w: 5.5, h: 0.18, fontSize: 6, color: C.coral, fontFace: "Calibri", bold: true, charSpacing: 1, margin: 0 });

  // Table header
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.06, w: 5.5, h: 0.26, fill: { color: "222222" }, line: { color: C.border, width: 1 } });
  ["Plataforma", "Plan", "USD/mes", "COP/mes"].forEach((h, i) => {
    const ws = [1.9, 1.5, 0.8, 1.0];
    const xs = [0.38, 2.28, 3.78, 4.58];
    s.addText(h, { x: xs[i], y: 1.08, w: ws[i], h: 0.22, fontSize: 7, bold: true, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  TOOLS.forEach((t, i) => {
    const ty = 1.34 + i * 0.36;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: ty, w: 5.5, h: 0.34, fill: { color: i % 2 === 0 ? C.card : "161616" }, line: { color: C.border, width: 0.5 } });
    s.addText(t.name, { x: 0.38, y: ty + 0.02, w: 1.84, h: 0.28, fontSize: 7.5, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(t.plan, { x: 2.24, y: ty + 0.02, w: 1.44, h: 0.28, fontSize: 7, color: C.gray, fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText("$" + t.usd, { x: 3.74, y: ty + 0.02, w: 0.76, h: 0.28, fontSize: 7.5, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(fmt(t.cop), { x: 4.54, y: ty + 0.02, w: 1.2, h: 0.28, fontSize: 7.5, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
  });

  // LinkedIn — cargo KLIK row
  const liY = 1.34 + TOOLS.length * 0.36;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: liY, w: 5.5, h: 0.34, fill: { color: "0A1A3A" }, line: { color: C.blue, width: 1 } });
  s.addText("LinkedIn Sales Navigator", { x: 0.38, y: liY + 0.02, w: 1.84, h: 0.28, fontSize: 7.5, color: "6E9EFF", fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addText("Team", { x: 2.24, y: liY + 0.02, w: 1.44, h: 0.28, fontSize: 7, color: "6E9EFF", fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addText("$149", { x: 3.74, y: liY + 0.02, w: 0.76, h: 0.28, fontSize: 7.5, color: "6E9EFF", fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addText("Cargo KLIK ★", { x: 4.54, y: liY + 0.02, w: 1.2, h: 0.28, fontSize: 7.5, bold: true, color: "6E9EFF", fontFace: "Calibri", valign: "middle", margin: 0 });

  // Total row
  const totY = 1.34 + (TOOLS.length + 1) * 0.36;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: totY, w: 5.5, h: 0.36, fill: { color: C.coralD }, line: { color: C.coral, width: 1 } });
  s.addText("TOTAL PLATAFORMAS", { x: 0.38, y: totY + 0.02, w: 3.28, h: 0.3, fontSize: 8.5, bold: true, color: C.coral, fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addText("$" + TOOL_TOTAL_USD + " USD", { x: 3.74, y: totY + 0.02, w: 0.76, h: 0.3, fontSize: 8, bold: true, color: C.coral, fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addText(fmt(TOOL_TOTAL_COP), { x: 4.54, y: totY + 0.02, w: 1.2, h: 0.3, fontSize: 8.5, bold: true, color: C.coral, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Right: Price breakdown
  s.addText("ESTRUCTURA DE PRECIO MENSUAL", { x: 6.1, y: 0.84, w: 3.6, h: 0.18, fontSize: 6, color: C.coral, fontFace: "Calibri", bold: true, charSpacing: 1, margin: 0 });

  const blocks = [
    { label: "Costos plataformas", val: fmt(TOOL_TOTAL_COP), sub: "Pass-through transparente", col: C.gray, bgC: C.card },
    { label: "Fee de servicio", val: fmt(MY_MARGIN), sub: "Diseño · operación · estrategia · reportes", col: C.white, bgC: "1C1C1C" },
    { label: "TARIFA TOTAL MENSUAL", val: fmt(BASE_FEE), sub: "Todo incluido · sin costos ocultos", col: C.coral, bgC: C.coralD, border: C.coral },
    { label: "Variable por MQL adicional", val: fmt(VAR_PER_MQL), sub: "Por cada MQL más allá de los 15 incluidos en tarifa", col: C.green, bgC: C.greenD, border: C.green },
  ];

  blocks.forEach((b, i) => {
    const by = 1.06 + i * 0.98;
    const h = i >= 2 ? 0.9 : 0.88;
    s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: by, w: 3.6, h, fill: { color: b.bgC }, line: { color: b.border || C.border, width: b.border ? 1.5 : 1 } });
    s.addText(b.label, { x: 6.18, y: by + 0.05, w: 3.44, h: 0.2, fontSize: 7, color: b.col === C.coral || b.col === C.green ? b.col : C.gray, fontFace: "Calibri", bold: true, charSpacing: 0.3, margin: 0 });
    s.addText(b.val, { x: 6.18, y: by + 0.25, w: 3.44, h: 0.44, fontSize: 26, bold: true, color: b.col, fontFace: "Calibri", margin: 0 });
    s.addText(b.sub, { x: 6.18, y: by + 0.68, w: 3.44, h: 0.18, fontSize: 6, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  // Margin callout
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: totY + 0.48, w: 5.5, h: 0.54, fill: { color: C.greenD }, line: { color: C.green, width: 1.5 } });
  s.addText([
    { text: "Mi margen neto garantizado: ", options: { color: C.white } },
    { text: fmt(MY_MARGIN) + " COP/mes", options: { bold: true, color: C.green } },
    { text: "  +  ", options: { color: C.gray } },
    { text: fmt(VAR_PER_MQL) + " por MQL adicional", options: { bold: true, color: C.green } },
  ], { x: 0.42, y: totY + 0.5, w: 5.26, h: 0.5, fontSize: 9, fontFace: "Calibri", valign: "middle", margin: 0 });

  coralFooter(s, "TRM referencia: $4,000 COP/USD  ·  ★ LinkedIn Sales Navigator: licencia a cargo de KLIK Energy  ·  Resto de herramientas incluidas en tarifa");
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 3 — P1: PROYECCIÓN DE INGRESOS Y ROI
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5, C.coral);

  tag(s, "P1 — PROYECCIÓN DE INGRESOS Y ROI PARA KLIK", 0.44, 0.15);
  s.addText("Tres escenarios de retorno", { x: 0.44, y: 0.33, w: 9, h: 0.38, fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  hLine(s, 0.76);

  const scenarios = [
    { label: "Escenario Base",     mqls: 15, color: C.gray,  bgD: "1A1A1A",  border: C.border },
    { label: "Escenario Objetivo", mqls: 40, color: C.coral, bgD: C.coralD,  border: C.coral  },
    { label: "Escenario Alto",     mqls: 80, color: C.green, bgD: C.greenD,  border: C.green  },
  ];

  scenarios.forEach((sc, i) => {
    const cx = 0.3 + i * 3.24;
    const extraMqls     = Math.max(0, sc.mqls - MQL_BASE);
    const totalBilled   = BASE_FEE + extraMqls * VAR_PER_MQL;
    const myCOP         = MY_MARGIN + extraMqls * VAR_PER_MQL;
    const industCost    = Math.round(sc.mqls * 190 * 4000);
    const klikSaving    = industCost - totalBilled;

    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 0.86, w: 3.1, h: 4.24, fill: { color: sc.bgD }, line: { color: sc.border, width: 1.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: 0.86, w: 3.1, h: 0.3, fill: { color: sc.color === C.gray ? "252525" : (sc.color === C.coral ? "3A1416" : "163020") }, line: { color: sc.border, width: 0 } });
    s.addText(sc.label, { x: cx, y: 0.86, w: 3.1, h: 0.3, fontSize: 8, bold: true, color: sc.color, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

    // MQL count big
    s.addText(String(sc.mqls), { x: cx, y: 1.22, w: 3.1, h: 0.78, fontSize: 58, bold: true, color: sc.color, fontFace: "Calibri", align: "center", margin: 0 });
    const extraLabel = sc.mqls === MQL_BASE ? "incluidos en tarifa" : MQL_BASE + " base + " + (sc.mqls - MQL_BASE) + " adicionales";
    s.addText("MQLs/mes  ·  " + extraLabel, { x: cx, y: 1.98, w: 3.1, h: 0.2, fontSize: 7, color: C.gray, fontFace: "Calibri", align: "center", margin: 0 });

    s.addShape(pres.shapes.LINE, { x: cx + 0.2, y: 2.24, w: 2.7, h: 0, line: { color: C.border, width: 1 } });

    const rows = [
      ["Total facturado a KLIK",      fmt(totalBilled),  C.white],
      ["Costo industria equivalente", fmt(industCost),   C.gray2 || "555555"],
      ["Ahorro de KLIK vs industria", fmt(klikSaving),   C.green],
      ["Mi ingreso neto (margen)",    fmt(myCOP),        sc.color],
    ];

    rows.forEach(([label, val, col], ri) => {
      const ry = 2.34 + ri * 0.58;
      s.addText(label, { x: cx + 0.12, y: ry, w: 2.86, h: 0.2, fontSize: 6.5, color: C.gray, fontFace: "Calibri", margin: 0 });
      s.addText(val, { x: cx + 0.12, y: ry + 0.2, w: 2.86, h: 0.3, fontSize: 10.5, bold: true, color: col, fontFace: "Calibri", margin: 0 });
    });
  });

  // Bottom note
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 5.12, w: 9.4, h: 0.5, fill: { color: "161616" }, line: { color: C.border, width: 1 } });
  s.addText([
    { text: "Costo industria: ", options: { bold: true, color: C.white } },
    { text: "$190 USD × TRM $4,000 × MQLs entregados. ", options: { color: C.gray } },
    { text: "Mi margen mínimo garantizado: ", options: { bold: true, color: C.white } },
    { text: fmt(MY_MARGIN) + " COP/mes (fee fijo – herramientas). Cualquier MQL adicional es 100% margen neto.", options: { color: C.gray } },
  ], { x: 0.42, y: 5.14, w: 9.16, h: 0.46, fontSize: 7, fontFace: "Calibri", valign: "middle", margin: 0 });

  coralFooter(s, "Tarifa base incluye " + MQL_BASE + " MQLs/mes  ·  MQL adicional: " + fmt(VAR_PER_MQL) + " c/u  ·  Margen mínimo: " + fmt(MY_MARGIN) + " COP");
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 4 — P1: ENTREGABLES Y CONDICIONES
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5, C.coral);

  tag(s, "P1 — ENTREGABLES Y CONDICIONES DE SERVICIO", 0.44, 0.15);
  s.addText("Qué recibe KLIK cada mes", { x: 0.44, y: 0.33, w: 9, h: 0.38, fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  hLine(s, 0.76);

  const delivs = [
    { icon: "🤖", title: "Pipeline Lead GenAI operando", desc: "Ejecución semanal del sistema: 7 fuentes, HubSpot dedup, RUES NIT, Sales Navigator, enriquecimiento BC→Apollo→Lusha, scoring IA" },
    { icon: "📊", title: "Excel mensual de MQLs", desc: "Contactos con: nombre, cargo, empresa, NIT, LinkedIn URL, email verificado, teléfono celular, score de calificación, mercado (MNR/MR)" },
    { icon: "📣", title: "Scripts de outreach personalizados", desc: "Minutas de LinkedIn, Email, WhatsApp y Llamada por tipo de prospecto (MNR/MR) y perfil ICP (CFO, Planta, CTO)" },
    { icon: "📈", title: "Reporte mensual de performance", desc: "Empresas procesadas, MQLs generados, tasa de enriquecimiento, costo por MQL, comparativa con mes anterior" },
    { icon: "🔧", title: "Mantenimiento y mejora continua", desc: "Ajuste de queries, actualización de fuentes, corrección de errores, expansión a nuevas industrias/regiones según estrategia KLIK" },
    { icon: "🎯", title: "Consultoría de estrategia commercial", desc: "Reunión mensual de 1h para revisar resultados, ajustar ICP, refinar mensajes y priorizar pipeline según oportunidades del equipo de ventas" },
  ];

  delivs.forEach((d, i) => {
    const col = i < 3 ? 0 : 1;
    const row = i % 3;
    const dx = 0.3 + col * 4.82;
    const dy = 0.88 + row * 1.28;

    s.addShape(pres.shapes.RECTANGLE, { x: dx, y: dy, w: 4.6, h: 1.2, fill: { color: C.card }, line: { color: C.border, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: dx, y: dy, w: 0.05, h: 1.2, fill: { color: C.coral }, line: { color: C.coral } });
    s.addText(d.icon, { x: dx + 0.1, y: dy + 0.06, w: 0.5, h: 0.5, fontSize: 16, align: "center", margin: 0 });
    s.addText(d.title, { x: dx + 0.64, y: dy + 0.06, w: 3.84, h: 0.32, fontSize: 9, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
    s.addText(d.desc, { x: dx + 0.64, y: dy + 0.38, w: 3.84, h: 0.76, fontSize: 7, color: C.gray, fontFace: "Calibri", lineSpacingMultiple: 1.35, margin: 0 });
  });

  // Conditions strip
  const condY = 4.74;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: condY, w: 9.4, h: 0.38, fill: { color: "161616" }, line: { color: C.border, width: 1 } });
  const conds = ["⏱ Duración mínima: 3 meses", "📅 Pago: día 1 de cada mes", "📋 MQL: score ≥ 45 + email + tel", "🔒 Contrato de servicios", "🔄 Revisión tarifas cada 6 meses"];
  conds.forEach((c, i) => {
    s.addText(c, { x: 0.4 + i * 1.88, y: condY + 0.02, w: 1.8, h: 0.34, fontSize: 7.5, color: i === 0 || i === 2 ? C.white : C.gray, fontFace: "Calibri", bold: i === 0, valign: "middle", margin: 0 });
  });

  coralFooter(s, "P1 · Prestación de servicios · Sin vínculo laboral · Sin prestaciones · Factura mensual");
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 5 — P2: VINCULACIÓN LABORAL
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5, C.blue);

  tag(s, "P2 — VINCULACIÓN LABORAL · ALTERNATIVA", 0.44, 0.15);
  s.addText("Salario fijo + bono por resultados", { x: 0.44, y: 0.33, w: 9, h: 0.38, fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  hLine(s, 0.76);

  // Salary structure
  const blocks = [
    { label: "SALARIO FIJO", val: "$5.000.000", sub: "COP / mes · contrato indefinido", col: "6E9EFF", bgC: C.blueD, border: C.blue },
    { label: "BONO META ≥ 40 MQLs", val: "$1.000.000", sub: "COP adicional si se cumple la meta mensual", col: C.green, bgC: C.greenD, border: C.green },
    { label: "BONO META + 25%", val: "$1.500.000", sub: "COP adicional si supera la meta en 25% o más", col: C.gold, bgC: C.goldD, border: C.gold },
  ];

  blocks.forEach((b, i) => {
    const bx = 0.3 + i * 3.24;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 0.88, w: 3.1, h: 1.58, fill: { color: b.bgC }, line: { color: b.border, width: 1.5 } });
    s.addText(b.label, { x: bx + 0.1, y: 0.93, w: 2.9, h: 0.22, fontSize: 6.5, color: b.col, fontFace: "Calibri", bold: true, charSpacing: 0.5, margin: 0 });
    s.addText(b.val, { x: bx, y: 1.14, w: 3.1, h: 0.7, fontSize: 30, bold: true, color: b.col, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(b.sub, { x: bx + 0.1, y: 1.84, w: 2.9, h: 0.56, fontSize: 7, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  // Prestaciones
  s.addText("PRESTACIONES DE LEY INCLUIDAS", { x: 0.3, y: 2.6, w: 4.6, h: 0.18, fontSize: 6, color: "6E9EFF", fontFace: "Calibri", bold: true, charSpacing: 1, margin: 0 });
  const prests = [["📋", "Contrato laboral indefinido"], ["🏥", "EPS + Pensión (Sura/Colpensiones)"], ["🏖", "Vacaciones remuneradas (15 días/año)"], ["💰", "Prima de servicios (1 mes/año)"], ["💼", "Cesantías + intereses"], ["🛡", "ARL (riesgo profesional)"]];
  prests.forEach((p, i) => {
    const col = i < 3 ? 0 : 1;
    const row = i % 3;
    const px = 0.3 + col * 2.4;
    const py = 2.84 + row * 0.46;
    s.addShape(pres.shapes.RECTANGLE, { x: px, y: py, w: 2.28, h: 0.4, fill: { color: C.card }, line: { color: C.border, width: 1 } });
    s.addText(p[0], { x: px + 0.06, y: py, w: 0.3, h: 0.4, fontSize: 11, align: "center", valign: "middle", margin: 0 });
    s.addText(p[1], { x: px + 0.4, y: py + 0.02, w: 1.8, h: 0.36, fontSize: 7.5, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
  });

  // Roles right column
  s.addText("ROL Y RESPONSABILIDADES", { x: 5.1, y: 2.6, w: 4.6, h: 0.18, fontSize: 6, color: "6E9EFF", fontFace: "Calibri", bold: true, charSpacing: 1, margin: 0 });
  const roles = [
    ["🤖", "Operar Lead GenAI", "Pipeline completo semanal + mantenimiento del sistema"],
    ["📈", "Estrategia digital", "Campañas LinkedIn, ICP, hooks, optimización continua"],
    ["🔧", "Desarrollo", "Nuevas integraciones y mejoras de agentes IA"],
    ["📊", "Analytics", "Reportes, KPIs y recomendaciones al equipo comercial"],
    ["🤝", "Alineación", "Coordinar con ventas, ajustar pitch MNR/MR, iterar scripts"],
  ];
  roles.forEach((r, i) => {
    const ry = 2.84 + i * 0.46;
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: ry, w: 4.6, h: 0.4, fill: { color: C.card }, line: { color: C.border, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 5.1, y: ry, w: 0.04, h: 0.4, fill: { color: C.blue }, line: { color: C.blue } });
    s.addText(r[0], { x: 5.14, y: ry, w: 0.36, h: 0.4, fontSize: 11, align: "center", valign: "middle", margin: 0 });
    s.addText(r[1], { x: 5.54, y: ry + 0.02, w: 1.4, h: 0.18, fontSize: 7.5, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
    s.addText(r[2], { x: 5.54, y: ry + 0.2, w: 4.0, h: 0.18, fontSize: 6.5, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  coralFooter(s, "P2 · Contrato laboral indefinido · Full-time equipo KLIK · Bono medido por Excel de entrega mensual verificado");
}

// ══════════════════════════════════════════════════════════════════
// SLIDE 6 — COMPARACIÓN FINAL + PRÓXIMOS PASOS
// ══════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  tag(s, "COMPARACIÓN Y DECISIÓN", 0.44, 0.15);
  s.addText("Resumen · Propuesta más conveniente para cada parte", { x: 0.44, y: 0.33, w: 9, h: 0.38, fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
  hLine(s, 0.76);

  // Headers
  s.addShape(pres.shapes.RECTANGLE, { x: 2.6, y: 0.86, w: 3.4, h: 0.34, fill: { color: C.coralD }, line: { color: C.coral, width: 1.5 } });
  s.addText("P1 — Servicio", { x: 2.6, y: 0.86, w: 3.4, h: 0.34, fontSize: 10, bold: true, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.2, y: 0.86, w: 3.4, h: 0.34, fill: { color: C.blueD }, line: { color: C.blue, width: 1.5 } });
  s.addText("P2 — Laboral", { x: 6.2, y: 0.86, w: 3.4, h: 0.34, fontSize: 10, bold: true, color: "6E9EFF", fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  const rows = [
    ["Retribución fija",        fmt(BASE_FEE) + "/mes",           "$5.000.000/mes"],
    ["Variable",                fmt(VAR_PER_MQL) + " por MQL > 15", "Bono hasta $1.5M si meta +25%"],
    ["Mi ingreso potencial",    fmt(MY_MARGIN) + " – $13M+",      "$5M – $6.5M"],
    ["Costo real para KLIK",    fmt(BASE_FEE) + " + variable",    "$5M + prestaciones (~$6.5M)"],
    ["Herramientas",            "Incluidas en tarifa",             "KLIK debe proveerlas"],
    ["Flexibilidad",            "Alta · trabajo por entregables",  "Full-time · horario fijo"],
    ["Riesgo KLIK",             "Bajo · paga por resultados",      "Mayor · costos fijos + prestaciones"],
    ["Recomendado si...",       "Quieren probar primero",          "Quieren recurso interno dedicado"],
  ];

  rows.forEach((row, i) => {
    const ry = 1.26 + i * 0.46;
    const bgC = i % 2 === 0 ? "161616" : C.card;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: ry, w: 2.24, h: 0.42, fill: { color: bgC }, line: { color: C.border, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.6, y: ry, w: 3.4, h: 0.42, fill: { color: bgC }, line: { color: C.border, width: 0.5 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.2, y: ry, w: 3.5, h: 0.42, fill: { color: bgC }, line: { color: C.border, width: 0.5 } });
    s.addText(row[0], { x: 0.38, y: ry + 0.03, w: 2.06, h: 0.36, fontSize: 7, color: C.gray, fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addText(row[1], { x: 2.68, y: ry + 0.03, w: 3.24, h: 0.36, fontSize: 7.5, color: C.white, fontFace: "Calibri", bold: i < 4, valign: "middle", margin: 0 });
    s.addText(row[2], { x: 6.28, y: ry + 0.03, w: 3.34, h: 0.36, fontSize: 7.5, color: C.white, fontFace: "Calibri", bold: i < 4, valign: "middle", margin: 0 });
  });

  // Next steps
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.98, w: 9.4, h: 0.54, fill: { color: C.coralD }, line: { color: C.coral, width: 1.5 } });
  s.addText("Próximos pasos:", { x: 0.44, y: 5.0, w: 1.5, h: 0.5, fontSize: 9, bold: true, color: C.coral, fontFace: "Calibri", valign: "middle", margin: 0 });
  ["1. Seleccionar P1 o P2", "2. Reunión de ajuste (30 min)", "3. Firmar contrato (5 días)", "4. Conectar APIs", "5. Primera entrega mes 1"].forEach((st, i) => {
    s.addText(st, { x: 1.82 + i * 1.6, y: 5.02, w: 1.52, h: 0.5, fontSize: 7.5, color: C.white, fontFace: "Calibri", valign: "middle", bold: i === 0, margin: 0 });
  });

  coralFooter(s, "Juan José Trujillo  ·  juanjosetrujillo1209@gmail.com  ·  Propuesta válida 15 días calendario  ·  klikenergy.com");
}

// ─── Write ───────────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "/Users/juanjosetrujillo/Documents/Ai programas/klik-propuesta-comercial.pptx" });
console.log("Done: klik-propuesta-comercial.pptx");
