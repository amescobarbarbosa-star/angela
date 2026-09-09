const pptxgen = require("pptxgenjs");
const { circleIcon } = require("./icons");

// ---------- palette ----------
const NAVY = "1E2761"; // primary / dark bg
const NAVY_CARD = "2A3577"; // card on dark bg
const ICE = "CADCFC"; // secondary
const ICE_TEXT = "B9C6EA"; // muted text on dark bg
const ICE_TINT = "E4EAF8"; // ghost numerals / light chips on white bg
const CARD_TINT = "F2F5FC"; // subtle card fill on white bg
const AMBER = "C68A2E"; // sharp accent
const WHITE = "FFFFFF";
const SLATE = "44546A"; // body text on white bg
const SLATE_LIGHT = "7A88A8"; // captions

const TITLE_FONT = "Cambria";
const BODY_FONT = "Calibri";

const PAGE_W = 13.333;
const MARGIN = 0.6;
const CONTENT_W = PAGE_W - MARGIN * 2; // 12.133
const RIGHT_EDGE = MARGIN + CONTENT_W; // 12.733

async function main() {
  const icons = {};
  async function get(key, opts) {
    if (!icons[key]) icons[key] = await circleIcon(opts);
    return icons[key];
  }

  // Slide 1 icons (on navy bg)
  const ic_calendar_ice = await get("cal_ice", { iconName: "FiCalendar", circleColor: ICE, iconColor: NAVY });
  const ic_upload_amber = await get("up_amber", { iconName: "FiUpload", circleColor: AMBER, iconColor: NAVY });
  const ic_alert_amber = await get("alert_amber", { iconName: "FiAlertTriangle", circleColor: AMBER, iconColor: NAVY });
  const ic_check_ice = await get("check_ice", { iconName: "FiCheckCircle", circleColor: ICE, iconColor: NAVY });
  const ic_repeat_ice_sm = await get("repeat_ice_sm", { iconName: "FiRepeat", circleColor: ICE, iconColor: NAVY });
  const ic_card_ice_sm = await get("card_ice_sm", { iconName: "FiCreditCard", circleColor: ICE, iconColor: NAVY });
  const ic_alert_amber_sm = ic_alert_amber; // reuse

  // Slide 2 icons (on white bg)
  const ic_upload_navy = await get("up_navy", { iconName: "FiUpload", circleColor: ICE, iconColor: NAVY });
  const ic_folder_navy = await get("folder_navy", { iconName: "FiFolder", circleColor: ICE, iconColor: NAVY });
  const ic_db_navy = await get("db_navy", { iconName: "FiDatabase", circleColor: ICE, iconColor: NAVY });
  const ic_check_navy = await get("check_navy", { iconName: "FiCheckCircle", circleColor: ICE, iconColor: NAVY });
  const ic_cpu_navy_sm = await get("cpu_navy_sm", { iconName: "FiCpu", circleColor: ICE, iconColor: NAVY });
  const ic_edit_navy_sm = await get("edit_navy_sm", { iconName: "FiEdit3", circleColor: ICE, iconColor: NAVY });

  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
  pres.theme = { headFontFace: TITLE_FONT, bodyFontFace: BODY_FONT };

  // ============================================================
  // SLIDE 1 — General overview + timing
  // ============================================================
  const s1 = pres.addSlide();
  s1.background = { color: NAVY };

  s1.addText("PROCESO DE CIERRE SEMANAL", {
    x: MARGIN, y: 0.42, w: 8, h: 0.3,
    fontFace: BODY_FONT, fontSize: 12, bold: true, color: ICE, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s1.addText("Contabilización de gastos — Expensys", {
    x: MARGIN, y: 0.72, w: 11.8, h: 0.62,
    fontFace: TITLE_FONT, fontSize: 32, bold: true, color: WHITE,
    isTextBox: true, margin: 0,
  });
  s1.addText(
    "Cada jueves se contabilizan en SAP los gastos de empleados de todas las sociedades " +
      "(P02 · Gopaca · SFR) a partir de lo exportado de la plataforma Expenses.",
    {
      x: MARGIN, y: 1.42, w: 11.4, h: 0.5,
      fontFace: BODY_FONT, fontSize: 14, color: ICE_TEXT,
      isTextBox: true, margin: 0,
    }
  );

  // --- timeline ---
  const nodes = [
    { icon: ic_calendar_ice, big: "JUEVES", bigColor: WHITE, sub: "Inicio del ciclo semanal" },
    { icon: ic_upload_amber, big: "09:30h", bigColor: AMBER, sub: "Límite para exportar de Expenses" },
    { icon: ic_alert_amber, big: "12:00h", bigColor: AMBER, sub: "Corte automático: batch inputs P02" },
    { icon: ic_check_ice, big: "VERIFICACIÓN", bigColor: WHITE, sub: "Cuadre SAP + control semanal" },
  ];
  const slot = CONTENT_W / 4;
  const centers = nodes.map((_, i) => MARGIN + slot * (i + 0.5));
  const circleD = 0.85;
  const circleY = 2.5;
  const circleCenterY = circleY + circleD / 2;

  // connector line behind the nodes
  s1.addShape(pres.ShapeType.line, {
    x: centers[0], y: circleCenterY, w: centers[3] - centers[0], h: 0,
    line: { color: "5567A8", width: 1.5 },
  });

  nodes.forEach((n, i) => {
    const cx = centers[i];
    s1.addImage({ data: n.icon, x: cx - circleD / 2, y: circleY, w: circleD, h: circleD });
    s1.addText(n.big, {
      x: cx - 1.4, y: circleY + circleD + 0.14, w: 2.8, h: 0.36,
      fontFace: TITLE_FONT, fontSize: 17, bold: true, color: n.bigColor,
      align: "center", isTextBox: true, margin: 0,
    });
    s1.addText(n.sub, {
      x: cx - 1.35, y: circleY + circleD + 0.52, w: 2.7, h: 0.6,
      fontFace: BODY_FONT, fontSize: 10.5, color: ICE_TEXT,
      align: "center", isTextBox: true, margin: 0, valign: "top",
    });
  });

  // --- warning callout ---
  const warnY = 5.05;
  s1.addShape(pres.ShapeType.roundRect, {
    x: MARGIN, y: warnY, w: CONTENT_W, h: 0.82,
    rectRadius: 0.08, fill: { color: NAVY_CARD }, line: { type: "none" },
    shadow: { type: "outer", color: "0B0F2E", opacity: 0.35, blur: 8, offset: 2, angle: 90 },
  });
  s1.addImage({ data: ic_alert_amber_sm, x: MARGIN + 0.24, y: warnY + 0.16, w: 0.5, h: 0.5 });
  s1.addText(
    [
      { text: "Plazo crítico:  ", options: { bold: true, color: AMBER } },
      {
        text:
          "hay que exportar antes de las 9:30h. A las 12:00h el robot genera automáticamente los " +
          "batch inputs de P02; si se exporta después, pueden producirse conflictos.",
        options: { color: WHITE },
      },
    ],
    {
      x: MARGIN + 0.94, y: warnY + 0.1, w: CONTENT_W - 1.2, h: 0.62,
      fontFace: BODY_FONT, fontSize: 12.5, valign: "middle",
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
    }
  );

  // --- footer notes ---
  const footY = 6.18;
  s1.addImage({ data: ic_repeat_ice_sm, x: MARGIN, y: footY, w: 0.4, h: 0.4 });
  s1.addText("Cadencia: todos los jueves, para todas las sociedades.", {
    x: MARGIN + 0.55, y: footY, w: 5.6, h: 0.4,
    fontFace: BODY_FONT, fontSize: 12, color: ICE_TEXT, valign: "middle",
    isTextBox: true, margin: 0,
  });
  s1.addImage({ data: ic_card_ice_sm, x: 6.95, y: footY, w: 0.4, h: 0.4 });
  s1.addText("En paralelo, cada mes: cierre de tarjetas (aging) el día 16-17.", {
    x: 7.5, y: footY, w: 5.23, h: 0.4,
    fontFace: BODY_FONT, fontSize: 12, color: ICE_TEXT, valign: "middle",
    isTextBox: true, margin: 0,
  });

  s1.addNotes(
    "Puntos clave: proceso semanal (jueves) de contabilización de notas de gasto para todas las " +
      "sociedades (al menos P02, Gopaca y SFR) desde la plataforma Expenses hacia SAP. Hay una " +
      "ventana crítica: exportar antes de las 9:30h, porque a las 12:00h un robot genera los batch " +
      "inputs de P02 automáticamente y una exportación tardía puede generar conflictos. Tras " +
      "contabilizar se hacen dos controles: cuadre SAP vs. Expenses y una plantilla de seguimiento " +
      "semanal con semáforos por compañía. En paralelo, cada mes (día 16-17) se cierran y concilian " +
      "los cargos de las tarjetas corporativas (aging)."
  );

  // ============================================================
  // SLIDE 2 — Process detail
  // ============================================================
  const s2 = pres.addSlide();
  s2.background = { color: WHITE };

  s2.addText("DETALLE OPERATIVO", {
    x: MARGIN, y: 0.4, w: 8, h: 0.3,
    fontFace: BODY_FONT, fontSize: 12, bold: true, color: AMBER, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s2.addText("El proceso, paso a paso", {
    x: MARGIN, y: 0.68, w: 10, h: 0.6,
    fontFace: TITLE_FONT, fontSize: 32, bold: true, color: NAVY,
    isTextBox: true, margin: 0,
  });
  s2.addText("De la exportación en Expenses al control semanal en SAP", {
    x: MARGIN, y: 1.36, w: 10.5, h: 0.4,
    fontFace: BODY_FONT, fontSize: 13, color: SLATE_LIGHT,
    isTextBox: true, margin: 0,
  });

  const TEXTX = 2.35;
  const TEXTW = RIGHT_EDGE - TEXTX; // 10.383

  function ghostNumber(n, y, h) {
    s2.addText(n, {
      x: 0.45, y: y, w: 1.05, h: h,
      fontFace: TITLE_FONT, fontSize: 46, bold: true, color: ICE_TINT,
      isTextBox: true, margin: 0, valign: "top",
    });
  }
  function rowIcon(icon, y) {
    s2.addImage({ data: icon, x: 1.55, y: y + 0.12, w: 0.62, h: 0.62 });
  }
  function rowHeader(text, y) {
    s2.addText(text, {
      x: TEXTX, y: y + 0.05, w: TEXTW, h: 0.4,
      fontFace: TITLE_FONT, fontSize: 17, bold: true, color: NAVY,
      isTextBox: true, margin: 0,
    });
  }
  function rowDesc(text, y, h) {
    s2.addText(text, {
      x: TEXTX, y: y, w: TEXTW, h: h,
      fontFace: BODY_FONT, fontSize: 12.5, color: SLATE,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.18,
    });
  }

  // Row 1
  let rY = 1.95, rH = 0.95;
  ghostNumber("01", rY, rH);
  rowIcon(ic_upload_navy, rY);
  rowHeader("Exportar desde Expenses", rY);
  rowDesc(
    "Antes de las 9:30h: Cuentas → Exportar a empresa → todas las compañías → Aceptar. " +
      "La plataforma envía un correo automático con los ficheros a expenses.iberia.",
    rY + 0.47, 0.45
  );

  // Row 2
  rY = rY + rH + 0.16; rH = 0.95;
  ghostNumber("02", rY, rH);
  rowIcon(ic_folder_navy, rY);
  rowHeader("Guardar en carpeta compartida", rY);
  rowDesc(
    "Se crea la carpeta del día en Información R2R > Contabilización Expenses > Expenses nº [n], " +
      "por motivos de soporte y auditoría.",
    rY + 0.47, 0.45
  );

  // Row 3 (taller — P02 vs SFR comparison)
  rY = rY + rH + 0.16; rH = 1.75;
  ghostNumber("03", rY, rH);
  rowIcon(ic_db_navy, rY);
  rowHeader("Contabilizar en SAP", rY);
  rowDesc("Dos flujos distintos según la sociedad:", rY + 0.47, 0.3);

  const cardY = rY + 0.8, cardH = 0.95;
  const colGap = 0.3;
  const colW = (TEXTW - colGap) / 2;
  const colAx = TEXTX, colBx = TEXTX + colW + colGap;

  [
    { x: colAx, icon: ic_cpu_navy_sm, label: "P02 — Automático", desc: "El robot genera las notas de gasto; solo hay que desbloquearlas y contabilizarlas (SM35)." },
    { x: colBx, icon: ic_edit_navy_sm, label: "SFR — Manual", desc: "Contabilización por JV según el CSV exportado de SAP: Gasto Expensys a Tarjeta Empleado / pago directo, un asiento por sociedad." },
  ].forEach((c) => {
    s2.addShape(pres.ShapeType.roundRect, {
      x: c.x, y: cardY, w: colW, h: cardH,
      rectRadius: 0.06, fill: { color: CARD_TINT }, line: { type: "none" },
    });
    s2.addImage({ data: c.icon, x: c.x + 0.16, y: cardY + 0.14, w: 0.36, h: 0.36 });
    s2.addText(c.label, {
      x: c.x + 0.62, y: cardY + 0.1, w: colW - 0.78, h: 0.34,
      fontFace: BODY_FONT, fontSize: 13, bold: true, color: NAVY,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s2.addText(c.desc, {
      x: c.x + 0.18, y: cardY + 0.46, w: colW - 0.36, h: cardH - 0.56,
      fontFace: BODY_FONT, fontSize: 10.5, color: SLATE,
      isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.1,
    });
  });

  // Row 4
  rY = rY + rH + 0.16; rH = 0.95;
  ghostNumber("04", rY, rH);
  rowIcon(ic_check_navy, rY);
  rowHeader("Verificar y controlar", rY);
  rowDesc(
    "Cuadre SAP vs. Expenses y actualización del control semanal (fichero con semáforos) " +
      "por compañía.",
    rY + 0.47, 0.45
  );

  s2.addNotes(
    "Los 4 pasos: 1) Exportar de Expenses antes de las 9:30h (llega email a expenses.iberia). " +
      "2) Guardar los ficheros en la carpeta compartida del día (R2R) para soporte/auditoría. " +
      "3) Contabilizar en SAP: P02 está automatizado (robot + SM35); SFR sigue siendo manual " +
      "(JV a partir de CSV, un asiento por sociedad que agrupa a varios empleados) — esta es la " +
      "brecha de automatización a resolver. 4) Verificar: cuadre SAP vs Expenses y control semanal " +
      "con semáforos por compañía."
  );

  const path = require("path");
  const outFile = path.join(__dirname, "..", "salida", "Expensys-Proceso-Contabilizacion.pptx");
  await pres.writeFile({ fileName: outFile });
  console.log("Generado:", outFile);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
