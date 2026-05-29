const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Lead GenAI — KLIK Energy";

const C = {
  bg:       "111111",
  bgL:      "1A1A1A",
  coral:    "E8474A",
  coralD:   "1F0E0F",
  white:    "FFFFFF",
  gray:     "888888",
  gray2:    "555555",
  card:     "1A1A1A",
  border:   "2C2C2C",
  green:    "4CAF50",
  greenD:   "0D1F10",
  li:       "0A66C2",
  wa:       "25D366",
  pink:     "FF8C8E",
};

const mkShadow = () => ({ type: "outer", blur: 10, offset: 3, angle: 135, color: "000000", opacity: 0.2 });

// ─── helpers ────────────────────────────────────────────────────────────────

function bg(slide, color) {
  slide.background = { color: color || C.bg };
}

function hLine(slide, y) {
  slide.addShape(pres.shapes.LINE, {
    x: 0, y, w: 10, h: 0,
    line: { color: C.border, width: 0.75 },
  });
}

function vLine(slide, x, y, h) {
  slide.addShape(pres.shapes.LINE, {
    x, y, w: 0, h,
    line: { color: C.border, width: 0.75 },
  });
}

function sectionTag(slide, text, x, y) {
  slide.addText(text, {
    x, y, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1.2, bold: true, margin: 0,
  });
}

function sectionTitle(slide, text, x, y, w, sz) {
  slide.addText(text, {
    x, y, w: w || 9, h: 0.5,
    fontSize: sz || 26, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
}

function accentBar(slide, x, y, h) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.05, h,
    fill: { color: C.coral }, line: { color: C.coral },
  });
}

function coralFooter(slide, text) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.225, w: 10, h: 0.4,
    fill: { color: C.coral }, line: { color: C.coral },
  });
  slide.addText(text, {
    x: 0.4, y: 5.225, w: 9.2, h: 0.4,
    fontSize: 9, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0,
  });
}

function pill(slide, text, x, y, color, bgColor) {
  const w = text.length * 0.068 + 0.3;
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.22,
    fill: { color: bgColor || "222222" },
    line: { color: color || C.coral, width: 1 },
  });
  slide.addText(text, {
    x, y, w, h: 0.22,
    fontSize: 6, color: color || C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });
  return w;
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 1 — HERO
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);

  // Coral glow shape (left side visual)
  s.addShape(pres.shapes.OVAL, {
    x: -1.5, y: 0.5, w: 5, h: 5,
    fill: { color: C.coral, transparency: 88 },
    line: { color: C.coral, transparency: 100 },
  });

  // Badge
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.55, y: 0.9, w: 1.8, h: 0.25,
    fill: { color: "1F0E0F" }, line: { color: C.coral, width: 1 },
  });
  s.addText("⚡  Estrategia Comercial", {
    x: 0.55, y: 0.9, w: 1.8, h: 0.25,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });

  // Main title
  s.addText("Generación de clientes", {
    x: 0.5, y: 1.3, w: 7, h: 0.65,
    fontSize: 40, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("para KLIK Energy", {
    x: 0.5, y: 1.92, w: 7, h: 0.65,
    fontSize: 40, bold: true, color: C.coral, fontFace: "Calibri", margin: 0,
  });

  // Subtitle
  s.addText("A quién prospectar, qué mensaje usar y cómo capturar leads calificados\ncon LinkedIn Lead Gen Forms — datos reales, sin fricciones.", {
    x: 0.5, y: 2.72, w: 6.2, h: 0.8,
    fontSize: 11, color: C.gray, fontFace: "Calibri", lineSpacingMultiple: 1.4, margin: 0,
  });

  // Pills row
  const tags = ["Claude AI", "LinkedIn Sales Nav", "Apollo API", "BetterContact", "RUES Colombia", "HubSpot CRM"];
  let px = 0.5;
  tags.forEach(t => {
    px += pill(s, t, px, 3.68) + 0.12;
  });

  // Right side big stat
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.2, y: 1.1, w: 2.55, h: 3.9,
    fill: { color: C.bgL }, line: { color: C.border, width: 1 },
  });
  accentBar(s, 7.2, 1.1, 3.9);
  s.addText("$10", {
    x: 7.28, y: 1.4, w: 2.42, h: 1.1,
    fontSize: 72, bold: true, color: C.coral, fontFace: "Calibri", align: "center", margin: 0,
  });
  s.addText("USD / lead", {
    x: 7.28, y: 2.5, w: 2.42, h: 0.3,
    fontSize: 11, color: C.white, fontFace: "Calibri", align: "center", margin: 0,
  });
  s.addText("vs $190 industria", {
    x: 7.28, y: 2.82, w: 2.42, h: 0.22,
    fontSize: 8.5, color: C.gray, fontFace: "Calibri", align: "center", margin: 0,
  });
  s.addShape(pres.shapes.LINE, { x: 7.5, y: 3.16, w: 2.0, h: 0, line: { color: C.border, width: 1 } });
  s.addText("Prospección → MQL\nen menos de 1 mes", {
    x: 7.28, y: 3.22, w: 2.42, h: 0.6,
    fontSize: 8, color: C.gray, fontFace: "Calibri", align: "center", margin: 0,
  });
  s.addText("19× más barato", {
    x: 7.28, y: 3.88, w: 2.42, h: 0.8,
    fontSize: 13, bold: true, color: C.green, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });

  coralFooter(s, "klikenergy.com  ·  Lead GenAI  ·  B2B Prospección Automatizada");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 2 — LEAD GENAI ARCHITECTURE
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("00 — ARQUITECTURA DEL SISTEMA", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("Lead GenAI — Pipeline completo", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("5 agentes especializados coordinados por Claude AI. Desde un query hasta un prospecto con nombre, cargo, email y teléfono.", {
    x: 0.44, y: 0.65, w: 9.2, h: 0.26,
    fontSize: 8.5, color: C.gray, fontFace: "Calibri", margin: 0,
  });

  hLine(s, 0.97);

  // ── 7 Discovery sources (top row)
  s.addText("PASO 1 — AGENTE DE DESCUBRIMIENTO · 7 FUENTES SIMULTÁNEAS", {
    x: 0.3, y: 1.05, w: 9.4, h: 0.16,
    fontSize: 6, color: C.coral, fontFace: "Calibri", charSpacing: 0.8, bold: true, margin: 0,
  });

  const sources = [
    { icon: "🗺️", name: "Google Maps", sub: "Playwright" },
    { icon: "🔵", name: "Bing Maps", sub: "Playwright" },
    { icon: "📒", name: "Páginas\nAmarillas", sub: "Colombia" },
    { icon: "🏭", name: "Kompass B2B", sub: "Industrial" },
    { icon: "🌐", name: "OpenStreetMap", sub: "Overpass API" },
    { icon: "🔍", name: "Google Search", sub: "Orgánico" },
    { icon: "⚡", name: "XM", sub: "Mercado eléctrico" },
  ];

  const srcW = 9.4 / 7;
  sources.forEach((src, i) => {
    const sx = 0.3 + i * srcW;
    s.addShape(pres.shapes.RECTANGLE, {
      x: sx, y: 1.25, w: srcW - 0.08, h: 0.88,
      fill: { color: C.card }, line: { color: C.border, width: 1 },
    });
    s.addText(src.icon, { x: sx, y: 1.29, w: srcW - 0.08, h: 0.28, fontSize: 11, align: "center", margin: 0 });
    s.addText(src.name, { x: sx, y: 1.56, w: srcW - 0.08, h: 0.3, fontSize: 5.8, color: C.white, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(src.sub, { x: sx, y: 1.84, w: srcW - 0.08, h: 0.22, fontSize: 5, color: C.gray, fontFace: "Calibri", align: "center", margin: 0 });
  });

  // ── Pipeline arrow
  s.addText("↓  HubSpot Dedup Filter  (solo empresas nuevas pasan)  ↓", {
    x: 0.3, y: 2.2, w: 9.4, h: 0.22,
    fontSize: 7.5, color: C.gray, fontFace: "Calibri", align: "center", italic: true, margin: 0,
  });

  // ── 5 Pipeline agents (bottom row)
  const steps = [
    { n: "2", icon: "📋", name: "NIT Resolver", api: "RUES Colombia", file: "nit_resolver.py" },
    { n: "3", icon: "👔", name: "Sales Navigator", api: "LinkedIn SN", file: "salesnav_scraper.py" },
    { n: "4", icon: "✨", name: "Enriquecimiento", api: "BC → Apollo → Lusha", file: "contact_enricher.py" },
    { n: "5", icon: "📊", name: "Scoring IA", api: "HOT · WARM · COLD", file: "qualification.py" },
    { n: "6", icon: "📤", name: "Export Excel", api: "LinkedIn + Email + Tel", file: "exporter.py" },
  ];

  const stW = 9.4 / 5;
  const stY = 2.48;
  steps.forEach((st, i) => {
    const sx = 0.3 + i * stW;
    s.addShape(pres.shapes.RECTANGLE, {
      x: sx, y: stY, w: stW - 0.1, h: 1.42,
      fill: { color: C.card }, line: { color: C.border, width: 1 },
    });
    // Top coral accent
    s.addShape(pres.shapes.RECTANGLE, {
      x: sx, y: stY, w: stW - 0.1, h: 0.06,
      fill: { color: C.coral }, line: { color: C.coral },
    });
    s.addText("PASO " + st.n, { x: sx + 0.08, y: stY + 0.1, w: 0.5, h: 0.14, fontSize: 5, color: C.coral, fontFace: "Calibri", bold: true, margin: 0 });
    s.addText(st.icon, { x: sx, y: stY + 0.2, w: stW - 0.1, h: 0.3, fontSize: 14, align: "center", margin: 0 });
    s.addText(st.name, { x: sx + 0.06, y: stY + 0.55, w: stW - 0.22, h: 0.28, fontSize: 8, bold: true, color: C.white, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(st.api, { x: sx + 0.06, y: stY + 0.82, w: stW - 0.22, h: 0.28, fontSize: 6.5, color: C.gray, fontFace: "Calibri", align: "center", margin: 0 });
    s.addShape(pres.shapes.LINE, { x: sx + 0.1, y: stY + 1.12, w: stW - 0.3, h: 0, line: { color: C.border, width: 1 } });
    s.addText(st.file, { x: sx + 0.06, y: stY + 1.16, w: stW - 0.22, h: 0.2, fontSize: 5.5, color: C.coral, fontFace: "Calibri", align: "center", italic: true, margin: 0 });

    if (i < steps.length - 1) {
      s.addText("→", { x: sx + stW - 0.18, y: stY + 0.55, w: 0.22, h: 0.3, fontSize: 10, color: "444444", fontFace: "Calibri", align: "center", margin: 0 });
    }
  });

  // Score pills
  const scoreY = 4.06;
  [[" HOT > 70 ", C.coral, C.coralD], [" WARM 50–70 ", C.pink, "1A1218"], [" COLD < 50 ", C.gray, "1A1A1A"],
   [" MNR ≥ 55k kWh → +15 pts ", C.green, C.greenD], [" No Regulado → +10 pts ", C.green, C.greenD]].forEach(([t, col, bgc], i) => {
    const spx = 0.3 + i * 1.9;
    s.addShape(pres.shapes.RECTANGLE, { x: spx, y: scoreY, w: 1.78, h: 0.28, fill: { color: bgc }, line: { color: col, width: 1 } });
    s.addText(t, { x: spx, y: scoreY, w: 1.78, h: 0.28, fontSize: 6.5, color: col, fontFace: "Calibri", bold: true, align: "center", valign: "middle", margin: 0 });
  });

  coralFooter(s, "Orquestador: claude-sonnet-4-6  ·  MODEL = pipeline_agent.py  ·  Resultado: Excel con LinkedIn + Email + Teléfono");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 3 — OUTREACH SEQUENCE
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("OUTREACH OUTBOUND — POST PIPELINE", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("Secuencia de 4 etapas — Prospecto con datos completos", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.75);

  // Timeline connector bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.95, y: 1.12, w: 8.1, h: 0.06,
    fill: { color: "222222" }, line: { color: "222222" },
  });

  const channels = [
    { etapa: "ETAPA 1", icon: "💼", name: "LinkedIn", color: C.li, bgD: "080F1A",
      steps: ["Visualización de perfil — genera curiosidad", "Solicitud de conexión con nota personalizada", "Interacción con post reciente del prospecto", "Follow-up DM si no responde en 48h"] },
    { etapa: "ETAPA 2", icon: "✉️", name: "Email", color: C.coral, bgD: C.coralD,
      steps: ["Verificación email: BC → Apollo → Lusha", "Personalización con datos del pipeline (NIT, ciudad, sector)", "Envío con asunto gancho + CTA único Calendly", "Follow-up automático 48h si no abre"] },
    { etapa: "ETAPA 3", icon: "💬", name: "WhatsApp", color: C.wa, bgD: "091A0E",
      steps: ["Mensaje de apertura corto con gancho económico", "Conversación proactiva — responder, mantener hilo", "Envío del 1-pager KLIK (servicios + CTA)", "Agendar llamada — link Calendly en el mismo chat"] },
    { etapa: "ETAPA 4", icon: "📞", name: "Llamada", color: C.pink, bgD: "1A1018",
      steps: ["Cargar ficha completa: cargo, NIT, consumo, sector", "Pitch apertura 30 seg — referencia canales previos", "Identificar pain point energético del prospecto", "Objetivo único: agendar demo de plataforma KLIK"] },
  ];

  const colW = 9.4 / 4;
  channels.forEach((ch, i) => {
    const cx = 0.3 + i * colW;

    // Bubble
    s.addShape(pres.shapes.OVAL, {
      x: cx + colW / 2 - 0.32, y: 0.85, w: 0.64, h: 0.64,
      fill: { color: ch.bgD }, line: { color: ch.color, width: 2 },
    });
    s.addText(ch.icon, { x: cx + colW / 2 - 0.32, y: 0.85, w: 0.64, h: 0.64, fontSize: 14, align: "center", valign: "middle", margin: 0 });

    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx + 0.04, y: 1.55, w: colW - 0.08, h: 3.52,
      fill: { color: C.card }, line: { color: ch.color, width: 1 },
    });
    // Top header bar
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx + 0.04, y: 1.55, w: colW - 0.08, h: 0.56,
      fill: { color: ch.bgD }, line: { color: ch.bgD },
    });
    s.addText(ch.etapa, { x: cx + 0.1, y: 1.58, w: colW - 0.2, h: 0.14, fontSize: 5.5, color: ch.color, fontFace: "Calibri", bold: true, charSpacing: 0.3, margin: 0 });
    s.addText(ch.name, { x: cx + 0.1, y: 1.7, w: colW - 0.2, h: 0.28, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });

    // Steps
    ch.steps.forEach((step, si) => {
      const sy = 2.18 + si * 0.76;
      // Number circle
      s.addShape(pres.shapes.OVAL, { x: cx + 0.1, y: sy, w: 0.22, h: 0.22, fill: { color: ch.color }, line: { color: ch.color } });
      s.addText(String(si + 1), { x: cx + 0.1, y: sy, w: 0.22, h: 0.22, fontSize: 6.5, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
      s.addText(step, { x: cx + 0.38, y: sy - 0.02, w: colW - 0.5, h: 0.7, fontSize: 6.8, color: "AAAAAA", fontFace: "Calibri", margin: 0 });
    });
  });

  // Re-engagement strip
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 5.15, w: 9.4, h: 0.06, fill: { color: C.coral }, line: { color: C.coral } });
  coralFooter(s, "Sin respuesta: D+10 LinkedIn follow-up  ·  D+14 Email + calculadora ahorro  ·  D+21 Llamada final  ·  D+30 → Nurturing 60 días");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 4 — MQL ROUTING
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("ROUTING DE MQLs — CLASIFICACIÓN AUTOMÁTICA", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("MQL calificado → Producto KLIK correcto", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.75);

  // Input node
  s.addShape(pres.shapes.RECTANGLE, {
    x: 3.6, y: 0.9, w: 2.8, h: 0.42,
    fill: { color: C.coralD }, line: { color: C.coral, width: 1.5 },
  });
  s.addText("⚡  MQL Calificado  ·  Score ≥ 45", {
    x: 3.6, y: 0.9, w: 2.8, h: 0.42,
    fontSize: 9, bold: true, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });

  // Arrow down
  s.addShape(pres.shapes.LINE, { x: 5, y: 1.32, w: 0, h: 0.28, line: { color: C.coral, width: 2 } });

  // Decision diamond
  s.addShape(pres.shapes.RECTANGLE, {
    x: 3.2, y: 1.6, w: 3.6, h: 0.5,
    fill: { color: "1A0E0E" }, line: { color: C.coral, width: 2 },
  });
  s.addText("¿Consumo ≥ 55 MWh/mes?  (CREG · Umbral No Regulado)", {
    x: 3.2, y: 1.6, w: 3.6, h: 0.5,
    fontSize: 9.5, bold: true, color: C.coral, fontFace: "Calibri", align: "center", valign: "middle", margin: 0,
  });

  // Branch lines and labels
  s.addText("SÍ  ←", { x: 0.3, y: 2.16, w: 2.6, h: 0.26, fontSize: 10, color: C.green, bold: true, fontFace: "Calibri", align: "right", margin: 0 });
  s.addText("→  NO", { x: 7.1, y: 2.16, w: 2.6, h: 0.26, fontSize: 10, color: C.coral, bold: true, fontFace: "Calibri", align: "left", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 0.3, y: 2.29, w: 3.0, h: 0, line: { color: C.green, width: 1.5 } });
  s.addShape(pres.shapes.LINE, { x: 6.7, y: 2.29, w: 3.0, h: 0, line: { color: C.coral, width: 1.5 } });

  // MNR Card
  const cardH = 2.7;
  const cardY = 2.35;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: cardY, w: 4.3, h: cardH, fill: { color: C.greenD }, line: { color: C.green, width: 1.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: cardY, w: 4.3, h: 0.32, fill: { color: "164020" }, line: { color: C.green, width: 0 } });
  s.addText("MERCADO NO REGULADO  ·  ≥ 55,000 kWh/mes", { x: 0.3, y: cardY, w: 4.3, h: 0.32, fontSize: 8, color: C.green, fontFace: "Calibri", bold: true, align: "center", valign: "middle", margin: 0 });
  s.addText([
    { text: "Pitch: ", options: { bold: true, color: C.white } },
    { text: "Upselling dentro de grandes organizaciones · tarifa bilateral negociada fuera de bolsa", options: { color: C.gray } },
  ], { x: 0.42, y: cardY + 0.38, w: 4.06, h: 0.5, fontSize: 8, fontFace: "Calibri", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 0.5, y: cardY + 0.96, w: 3.9, h: 0, line: { color: "2A4A2A", width: 1 } });
  // Products
  [["Comercialización", "Trading energía · contratos bilaterales · libre elección proveedor"],
   ["DDV · Desconexión Voluntaria", "Monetiza capacidad ociosa · ingresos adicionales por flexibilidad"],
   ["RD · Respuesta a la Demanda", "Reduce picos · crédito en factura + incentivos XM"]].forEach(([name, desc], pi) => {
    const py = cardY + 1.06 + pi * 0.54;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.42, y: py, w: 4.06, h: 0.46, fill: { color: "122018" }, line: { color: "2A4A2A", width: 1 } });
    s.addText(name, { x: 0.52, y: py + 0.03, w: 3.86, h: 0.18, fontSize: 7.5, bold: true, color: C.green, fontFace: "Calibri", margin: 0 });
    s.addText(desc, { x: 0.52, y: py + 0.2, w: 3.86, h: 0.22, fontSize: 6.5, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  // MR Card
  s.addShape(pres.shapes.RECTANGLE, { x: 5.4, y: cardY, w: 4.3, h: cardH, fill: { color: C.coralD }, line: { color: C.coral, width: 1.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.4, y: cardY, w: 4.3, h: 0.32, fill: { color: "3A1214" }, line: { color: C.coral, width: 0 } });
  s.addText("MERCADO REGULADO  ·  < 55,000 kWh/mes", { x: 5.4, y: cardY, w: 4.3, h: 0.32, fontSize: 8, color: C.coral, fontFace: "Calibri", bold: true, align: "center", valign: "middle", margin: 0 });
  s.addText([
    { text: "Pitch: ", options: { bold: true, color: C.white } },
    { text: "Reducción de costos sin cambiar comercializador · tarifa regulada CREG · entrada de bajo riesgo", options: { color: C.gray } },
  ], { x: 5.52, y: cardY + 0.38, w: 4.06, h: 0.5, fontSize: 8, fontFace: "Calibri", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 5.6, y: cardY + 0.96, w: 3.9, h: 0, line: { color: "4A2022", width: 1 } });
  [["Comercialización", "Tarifa regulada CREG · valor en eficiencia y gestión"],
   ["DDV · Desconexión Voluntaria", "Ingresos adicionales sin cambiar proveedor · contrato disponibilidad"],
   ["RD · Respuesta a la Demanda", "Crédito en factura regulada · optimización curva de carga CREG"]].forEach(([name, desc], pi) => {
    const py = cardY + 1.06 + pi * 0.54;
    s.addShape(pres.shapes.RECTANGLE, { x: 5.52, y: py, w: 4.06, h: 0.46, fill: { color: "200E10" }, line: { color: "4A2022", width: 1 } });
    s.addText(name, { x: 5.62, y: py + 0.03, w: 3.86, h: 0.18, fontSize: 7.5, bold: true, color: C.coral, fontFace: "Calibri", margin: 0 });
    s.addText(desc, { x: 5.62, y: py + 0.2, w: 3.86, h: 0.22, fontSize: 6.5, color: C.gray, fontFace: "Calibri", margin: 0 });
  });

  coralFooter(s, "HOT > 70 pts  ·  WARM 50–70  ·  COLD < 50  ·  MNR ≥ 55k kWh → +15 pts  ·  market_type No Regulado → +10 pts");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 5 — COST COMPARISON
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("00B — EFICIENCIA DE INVERSIÓN", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("El costo real de un lead en energía", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.75);

  // BAD card
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 0.9, w: 3.6, h: 4.2, fill: { color: C.card }, line: { color: "333333", width: 1 } });
  s.addText("Comercializadoras nacionales", { x: 0.42, y: 1.0, w: 3.36, h: 0.24, fontSize: 9, color: C.gray, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("Canales tradicionales: eventos, referidos,\nfuerza de ventas presencial, llamadas en frío", { x: 0.42, y: 1.26, w: 3.36, h: 0.46, fontSize: 7.5, color: C.gray, fontFace: "Calibri", margin: 0 });
  s.addText("$190", { x: 0.3, y: 1.8, w: 3.6, h: 1.0, fontSize: 80, bold: true, color: C.gray2, fontFace: "Calibri", align: "center", margin: 0 });
  s.addText("USD por lead", { x: 0.3, y: 2.82, w: 3.6, h: 0.28, fontSize: 12, color: C.gray, fontFace: "Calibri", align: "center", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 0.5, y: 3.18, w: 3.2, h: 0, line: { color: C.border, width: 1 } });
  [["Ciclo de venta: 3–6 meses", "D00000"], ["Datos de baja calidad", "D00000"], ["Escalabilidad limitada", "D00000"], ["Sin trazabilidad digital", "D00000"]].forEach(([t, c], i) => {
    s.addText("✗  " + t, { x: 0.42, y: 3.26 + i * 0.26, w: 3.36, h: 0.24, fontSize: 7.5, color: "AA4444", fontFace: "Calibri", margin: 0 });
  });

  // Middle
  s.addText("19×\nmás barato", { x: 4.1, y: 1.9, w: 1.8, h: 0.8, fontSize: 18, bold: true, color: C.green, fontFace: "Calibri", align: "center", margin: 0 });
  s.addText("−94%\ncosto / lead", { x: 4.1, y: 2.82, w: 1.8, h: 0.6, fontSize: 13, bold: true, color: C.green, fontFace: "Calibri", align: "center", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 4.8, y: 1.6, w: 0, h: 2.6, line: { color: C.border, width: 1 } });

  // GOOD card
  s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 0.9, w: 3.6, h: 4.2, fill: { color: "0D1A0D" }, line: { color: C.green, width: 1.5 } });
  s.addText("KLIK × Lead GenAI", { x: 6.22, y: 1.0, w: 3.36, h: 0.24, fontSize: 9, color: C.green, fontFace: "Calibri", bold: true, margin: 0 });
  s.addText("LinkedIn Lead Gen Forms + scoring IA\n+ CRM automático + nurturing digital", { x: 6.22, y: 1.26, w: 3.36, h: 0.46, fontSize: 7.5, color: C.gray, fontFace: "Calibri", margin: 0 });
  s.addText("$10", { x: 6.1, y: 1.8, w: 3.6, h: 1.0, fontSize: 80, bold: true, color: C.green, fontFace: "Calibri", align: "center", margin: 0 });
  s.addText("USD por lead", { x: 6.1, y: 2.82, w: 3.6, h: 0.28, fontSize: 12, color: C.green, fontFace: "Calibri", align: "center", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 6.3, y: 3.18, w: 3.2, h: 0, line: { color: "2A4A2A", width: 1 } });
  [["Ciclo: <1 mes (prospecto → MQL)"], ["Datos verificados de LinkedIn"], ["Escala sin costo lineal"], ["Trazabilidad completa en CRM"]].forEach(([t], i) => {
    s.addText("✓  " + t, { x: 6.22, y: 3.26 + i * 0.26, w: 3.36, h: 0.24, fontSize: 7.5, color: C.green, fontFace: "Calibri", margin: 0 });
  });

  coralFooter(s, "De $190 a $10 por lead  ·  19× más barato  ·  -94% costo por lead calificado");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 6 — ICP
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("01 — PERFIL DE CLIENTE IDEAL", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("¿A quién le vende KLIK?", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("Tres perfiles con poder de decisión, cada uno con un dolor distinto y una puerta de entrada diferente.", {
    x: 0.44, y: 0.65, w: 9.2, h: 0.22,
    fontSize: 8.5, color: C.gray, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.93);

  const icps = [
    {
      icon: "💰", title: "El que controla los costos",
      role: "CFO · Director Financiero · Gerente Administrativo",
      items: ["La energía es su 2do o 3er costo operativo", "Recibe facturas pero no entiende los componentes", "Urge reducir OPEX sin afectar producción", "Sectores: manufactura, retail, telecomunicaciones"],
      hook: '"¿Cuánto de tu factura de energía podrías convertir en ingreso?"',
    },
    {
      icon: "🏭", title: "El que opera la planta",
      role: "Gerente de Planta · Director de Energía · COO",
      items: ["Sabe cuándo consume más y por qué", "Tiene flexibilidad de carga en ciertas horas", "Busca justificar inversiones en eficiencia", "Sectores: alimentos, cemento, papel, frío industrial"],
      hook: '"Tu planta ya puede cobrar por bajar consumo en pico — ¿lo sabías?"',
    },
    {
      icon: "🔋", title: "El que lidera la transformación",
      role: "CTO · Director de Innovación · VP Sostenibilidad",
      items: ["Tiene metas ESG y de huella de carbono", "Busca tecnología que genere datos y reportes", "Necesita demostrar ROI de proyectos digitales", "Sectores: telecomunicaciones, banca, retail moderno"],
      hook: '"Datos de consumo en tiempo real + ingresos DDV + reporte ESG automático."',
    },
  ];

  const colW = 9.4 / 3;
  icps.forEach((icp, i) => {
    const cx = 0.3 + i * colW;
    const cardH = 4.1;

    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.04, y: 1.0, w: colW - 0.08, h: cardH, fill: { color: C.card }, line: { color: C.border, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.04, y: 1.0, w: colW - 0.08, h: 0.06, fill: { color: C.coral }, line: { color: C.coral } });

    s.addText(icp.icon, { x: cx + 0.04, y: 1.1, w: colW - 0.08, h: 0.4, fontSize: 18, align: "center", margin: 0 });
    s.addText(icp.title, { x: cx + 0.12, y: 1.54, w: colW - 0.24, h: 0.38, fontSize: 9.5, bold: true, color: C.white, fontFace: "Calibri", align: "center", margin: 0 });
    s.addText(icp.role, { x: cx + 0.12, y: 1.9, w: colW - 0.24, h: 0.28, fontSize: 6.5, color: C.coral, fontFace: "Calibri", align: "center", margin: 0 });
    s.addShape(pres.shapes.LINE, { x: cx + 0.2, y: 2.22, w: colW - 0.4, h: 0, line: { color: C.border, width: 1 } });

    icp.items.forEach((item, ii) => {
      s.addText("→  " + item, { x: cx + 0.14, y: 2.3 + ii * 0.28, w: colW - 0.28, h: 0.26, fontSize: 7, color: "AAAAAA", fontFace: "Calibri", margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.12, y: 3.48, w: colW - 0.24, h: 0.56, fill: { color: C.coralD }, line: { color: C.coral, width: 1 } });
    s.addText([
      { text: "Puerta de entrada:\n", options: { bold: true, color: C.coral, breakLine: true } },
      { text: icp.hook, options: { color: "CCCCCC", italic: true } },
    ], { x: cx + 0.16, y: 3.5, w: colW - 0.32, h: 0.52, fontSize: 6.5, fontFace: "Calibri", margin: 0 });
  });

  coralFooter(s, "CFO = reducción OPEX  ·  Gerente Planta = monetizar flexibilidad  ·  CTO = ROI digital + ESG");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 7 — HOOKS
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s, C.bgL);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("02 — MENSAJES QUE ABREN PUERTAS", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("Los 4 ganchos que funcionan", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.75);

  const hooks = [
    { n: "1", title: "El dinero que ya existe",
      body: "La mayoría de empresas industriales desconoce el programa DDV de la CREG. No es promesa de ahorro futuro — es ingreso que ya podrían estar recibiendo.",
      quote: '"Empresas similares a la tuya generaron $6M USD reduciendo consumo en horas pico. ¿Ya tienes acceso a ese programa?"' },
    { n: "2", title: "El costo oculto en la factura",
      body: "Las tarifas horarias tienen componentes que pocas empresas optimizan: cargos de respaldo, restricciones, bloques comercializables. KLIK los convierte en palancas.",
      quote: '"El 12% de ahorro promedio no viene de consumir menos — viene de comprar mejor. ¿Cuándo fue la última auditoría de tu factura?"' },
    { n: "3", title: "La prueba social del sector",
      body: "Claro, Tigo, Bavaria, Postobón, D1 ya lo hacen. Cuando el prospecto ve que sus pares de industria están en el programa, la conversación cambia.",
      quote: '"Bavaria y Postobón ya generan ingresos DDV con KLIK. ¿Tu operación tiene el mismo potencial? Te mostramos el cálculo en 20 minutos."' },
    { n: "4", title: "La urgencia regulatoria",
      body: "Las reglas del mercado de energía en Colombia evolucionan. Los que se inscriben hoy en DDV/RD tienen ventaja frente a los que esperan.",
      quote: '"Los cupos DDV en tu región tienen límite de frontera. ¿Ya verificamos si tu empresa califica antes de que se asignen?"' },
  ];

  const colW = 9.4 / 4;
  hooks.forEach((h, i) => {
    const cx = 0.3 + i * colW;
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.04, y: 0.92, w: colW - 0.08, h: 4.18, fill: { color: C.bg }, line: { color: C.border, width: 1 } });

    // Number badge
    s.addShape(pres.shapes.OVAL, { x: cx + colW / 2 - 0.28, y: 0.98, w: 0.56, h: 0.56, fill: { color: C.coral }, line: { color: C.coral } });
    s.addText(h.n, { x: cx + colW / 2 - 0.28, y: 0.98, w: 0.56, h: 0.56, fontSize: 16, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

    s.addText(h.title, { x: cx + 0.1, y: 1.62, w: colW - 0.2, h: 0.46, fontSize: 9, bold: true, color: C.white, fontFace: "Calibri", align: "center", margin: 0 });
    s.addShape(pres.shapes.LINE, { x: cx + 0.2, y: 2.1, w: colW - 0.4, h: 0, line: { color: C.border, width: 1 } });
    s.addText(h.body, { x: cx + 0.1, y: 2.18, w: colW - 0.2, h: 1.24, fontSize: 7, color: "AAAAAA", fontFace: "Calibri", lineSpacingMultiple: 1.3, margin: 0 });

    // Quote box
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.1, y: 3.5, w: colW - 0.2, h: 1.5, fill: { color: C.coralD }, line: { color: "3A1414", width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.1, y: 3.5, w: 0.04, h: 1.5, fill: { color: C.coral }, line: { color: C.coral } });
    s.addText(h.quote, { x: cx + 0.18, y: 3.56, w: colW - 0.32, h: 1.38, fontSize: 6.8, color: "CCCCCC", fontFace: "Calibri", italic: true, lineSpacingMultiple: 1.3, margin: 0 });
  });

  coralFooter(s, "Usar en primer contacto  ·  Personalizar con nombre + empresa + sector del Excel generado por Lead GenAI");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 8 — LINKEDIN CAMPAIGNS
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);
  accentBar(s, 0.3, 0.15, 0.5);

  s.addText("03 — CAMPAÑAS LINKEDIN", {
    x: 0.44, y: 0.15, w: 9, h: 0.2,
    fontSize: 6.5, color: C.coral, fontFace: "Calibri", charSpacing: 1, bold: true, margin: 0,
  });
  s.addText("3 campañas con Lead Gen Forms", {
    x: 0.44, y: 0.33, w: 9, h: 0.34,
    fontSize: 22, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("Formularios nativos pre-llenados con datos del perfil LinkedIn  ·  El prospecto solo responde 2 preguntas  ·  Conversión 3× mayor que landing pages", {
    x: 0.44, y: 0.65, w: 9.2, h: 0.22,
    fontSize: 8, color: C.gray, fontFace: "Calibri", margin: 0,
  });
  hLine(s, 0.93);

  const camps = [
    {
      n: "C1", title: "CFOs & Finanzas",
      target: "CFOs · Directores Financieros",
      sectors: "Manufactura · Retail · Telecom",
      cta: "Calcular mi ahorro →",
      headline: "¿Tu empresa paga energía de más?",
      copy: "En Colombia el 78% de las empresas industriales no conoce el programa DDV de la CREG.\n\nCalcula en 2 minutos cuánto podrías generar — no solo ahorrar.",
      banner: "⚡ $6M+ generados para clientes KLIK",
      fields: ["Consumo mensual estimado", "¿Conoce el programa DDV?"],
    },
    {
      n: "C2", title: "Operaciones & Planta",
      target: "Gerentes de Planta · COOs",
      sectors: "Alimentos · Cemento · Frío industrial",
      cta: "Ver cómo funciona el DDV →",
      headline: "Convierte el consumo de tu planta en ingresos",
      copy: "El programa DDV permite cobrar por reducir consumo en horas pico, sin afectar tu operación.\n\nBavaria, D1 y Smurfit ya lo hacen.",
      banner: "🏭 4.8 GWh/día gestionados · 750+ fronteras activas",
      fields: ["¿Tu planta opera 24/7?", "Sector industrial"],
    },
    {
      n: "C3", title: "Digital & ESG",
      target: "CTOs · Directores de Innovación",
      sectors: "Telecom · Banca · Retail moderno",
      cta: "Solicitar diagnóstico ESG →",
      headline: "Energía que genera datos, ingresos y reporte ESG",
      copy: "La plataforma KLIK conecta tu operación al mercado eléctrico en tiempo real.\n\nDatos, DDV, Respuesta a la Demanda y reporte automático de huella de carbono.",
      banner: "📊 Dashboard en tiempo real · Reporte ESG automático",
      fields: ["¿Tienen metas ESG activas?", "Número de sedes con medición"],
    },
  ];

  const colW = 9.4 / 3;
  camps.forEach((c, i) => {
    const cx = 0.3 + i * colW;
    const cardH = 4.18;

    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.04, y: 0.98, w: colW - 0.08, h: cardH, fill: { color: C.card }, line: { color: C.border, width: 1 } });

    // Header
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.04, y: 0.98, w: colW - 0.08, h: 0.52, fill: { color: C.coralD }, line: { color: C.coral, width: 1 } });
    s.addText(c.n + " — " + c.title, { x: cx + 0.1, y: 1.01, w: colW - 0.22, h: 0.22, fontSize: 9, bold: true, color: C.coral, fontFace: "Calibri", margin: 0 });
    s.addText(c.target + "  ·  " + c.sectors, { x: cx + 0.1, y: 1.22, w: colW - 0.22, h: 0.18, fontSize: 6, color: "AAAAAA", fontFace: "Calibri", margin: 0 });

    // Ad copy
    s.addText(c.headline, { x: cx + 0.1, y: 1.56, w: colW - 0.22, h: 0.26, fontSize: 8, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
    s.addText(c.copy, { x: cx + 0.1, y: 1.82, w: colW - 0.22, h: 0.72, fontSize: 6.8, color: C.gray, fontFace: "Calibri", lineSpacingMultiple: 1.3, margin: 0 });

    // Banner
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.1, y: 2.58, w: colW - 0.22, h: 0.24, fill: { color: "1A1A2A" }, line: { color: "333355", width: 1 } });
    s.addText(c.banner, { x: cx + 0.1, y: 2.58, w: colW - 0.22, h: 0.24, fontSize: 6.5, color: "8888CC", fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

    // CTA
    s.addShape(pres.shapes.RECTANGLE, { x: cx + 0.1, y: 2.9, w: colW - 0.22, h: 0.26, fill: { color: C.li }, line: { color: C.li } });
    s.addText(c.cta, { x: cx + 0.1, y: 2.9, w: colW - 0.22, h: 0.26, fontSize: 7.5, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

    // Form fields
    s.addShape(pres.shapes.LINE, { x: cx + 0.1, y: 3.24, w: colW - 0.22, h: 0, line: { color: C.border, width: 1 } });
    s.addText("FORMULARIO LEAD GEN · AUTO-PRELLENADO", { x: cx + 0.1, y: 3.3, w: colW - 0.22, h: 0.16, fontSize: 5.5, color: C.coral, fontFace: "Calibri", bold: true, charSpacing: 0.5, margin: 0 });
    ["Nombre completo  [AUTO]", "Empresa  [AUTO]", "Cargo  [AUTO]", ...c.fields].forEach((f, fi) => {
      s.addText(f, { x: cx + 0.1, y: 3.5 + fi * 0.2, w: colW - 0.22, h: 0.18, fontSize: 6.5, color: fi < 3 ? "555555" : "AAAAAA", fontFace: "Calibri", margin: 0 });
    });
  });

  coralFooter(s, "Lead Gen Forms: datos pre-llenados desde perfil LinkedIn  ·  3× mayor conversión vs landing pages  ·  Sin fricción");
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDE 9 — CTA / RESUMEN
// ═══════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  bg(s);

  s.addShape(pres.shapes.OVAL, {
    x: 6, y: -1, w: 6, h: 6,
    fill: { color: C.coral, transparency: 90 }, line: { color: C.coral, transparency: 100 },
  });

  s.addText("RESUMEN EJECUTIVO", {
    x: 0.5, y: 0.4, w: 5.5, h: 0.22,
    fontSize: 7, color: C.coral, fontFace: "Calibri", charSpacing: 1.5, bold: true, margin: 0,
  });
  s.addText("Lead GenAI — lo que\nKLIK puede hacer ahora", {
    x: 0.5, y: 0.6, w: 5.5, h: 1.1,
    fontSize: 30, bold: true, color: C.white, fontFace: "Calibri", lineSpacingMultiple: 1.1, margin: 0,
  });

  const summary = [
    ["🤖", "Lead GenAI", "7 fuentes → HubSpot → RUES → Sales Nav → Enriquecimiento → Scoring"],
    ["📣", "Outreach 4 etapas", "LinkedIn → Email → WhatsApp → Llamada · proceso documentado por canal"],
    ["⚡", "Routing MQL", "≥ 55 MWh/mes → MNR · < 55 MWh/mes → MR · pitch diferenciado"],
    ["💰", "$10 / lead", "vs $190 industria · 19× más barato · -94% costo por lead calificado"],
    ["🎯", "3 campañas LinkedIn", "Lead Gen Forms · CFO · Operaciones · Digital/ESG · Conversión 3×"],
    ["📅", "< 1 mes", "Prospección → Lead → MQL · datos completos para el equipo comercial"],
  ];

  summary.forEach(([icon, title, desc], i) => {
    const ry = 1.88 + i * 0.5;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: ry, w: 5.6, h: 0.42, fill: { color: C.card }, line: { color: C.border, width: 1 } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: ry, w: 0.04, h: 0.42, fill: { color: C.coral }, line: { color: C.coral } });
    s.addText(icon, { x: 0.58, y: ry, w: 0.36, h: 0.42, fontSize: 12, align: "center", valign: "middle", margin: 0 });
    s.addText(title, { x: 0.98, y: ry + 0.02, w: 1.3, h: 0.18, fontSize: 7.5, bold: true, color: C.coral, fontFace: "Calibri", margin: 0 });
    s.addText(desc, { x: 0.98, y: ry + 0.2, w: 5.0, h: 0.18, fontSize: 7, color: "AAAAAA", fontFace: "Calibri", margin: 0 });
  });

  // Right: CTA box
  s.addShape(pres.shapes.RECTANGLE, { x: 6.6, y: 0.9, w: 3.1, h: 4.22, fill: { color: C.coralD }, line: { color: C.coral, width: 2 } });
  s.addText("Próximos\npasos", { x: 6.6, y: 1.1, w: 3.1, h: 0.8, fontSize: 22, bold: true, color: C.coral, fontFace: "Calibri", align: "center", margin: 0 });
  s.addShape(pres.shapes.LINE, { x: 6.8, y: 1.96, w: 2.7, h: 0, line: { color: C.coral, width: 1 } });

  [
    ["1", "Aprobar estrategia Lead GenAI"],
    ["2", "Conectar Apollo + BetterContact\n+ LinkedIn Sales Navigator"],
    ["3", "Definir query inicial de búsqueda\n(industria + región + consumo)"],
    ["4", "Lanzar primeras 3 campañas\nLinkedIn Lead Gen Forms"],
    ["5", "Primera lista de MQLs calificados\nen < 30 días"],
  ].forEach(([n, txt], i) => {
    const sy = 2.06 + i * 0.62;
    s.addShape(pres.shapes.OVAL, { x: 6.72, y: sy + 0.06, w: 0.3, h: 0.3, fill: { color: C.coral }, line: { color: C.coral } });
    s.addText(n, { x: 6.72, y: sy + 0.06, w: 0.3, h: 0.3, fontSize: 8, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    s.addText(txt, { x: 7.08, y: sy + 0.02, w: 2.52, h: 0.52, fontSize: 7.5, color: C.white, fontFace: "Calibri", margin: 0 });
  });

  coralFooter(s, "klikenergy.com  ·  Lead GenAI by Claude AI  ·  juanjosetrujillo1209@gmail.com");
}

// ─── Write file ─────────────────────────────────────────────────────────────
pres.writeFile({ fileName: "/Users/juanjosetrujillo/Documents/Ai programas/klik-energy-deck.pptx" });
console.log("Done: klik-energy-deck.pptx");
