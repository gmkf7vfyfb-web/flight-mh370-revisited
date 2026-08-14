import fs from "node:fs/promises";
import path from "node:path";

const artifactModule = `${process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES}/@oai/artifact-tool/dist/artifact_tool.mjs`;
const { SpreadsheetFile, Workbook } = await import(artifactModule);

const root = process.cwd();
const outDir = path.join(root, "outputs", "mh370_pp_descent_climb_sensitivity");

function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ""; }
    else if (c === '\n') { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += c;
  }
  if (field.length || row.length) { row.push(field.replace(/\r$/, "")); rows.push(row); }
  return rows.filter(r => r.some(v => v !== ""));
}

async function readCsv(name) {
  const rows = parseCsv(await fs.readFile(path.join(outDir, name), "utf8"));
  return rows.map((r, i) => r.map(v => i === 0 || v === "" || Number.isNaN(Number(v)) ? v : Number(v)));
}

function colName(n) {
  let s = "";
  while (n > 0) { n--; s = String.fromCharCode(65 + (n % 26)) + s; n = Math.floor(n / 26); }
  return s;
}

function putMatrix(sheet, startRow, startCol, matrix) {
  const width = Math.max(...matrix.map(r => r.length));
  const padded = matrix.map(r => [...r, ...Array(width - r.length).fill(null)]);
  const endRow = startRow + matrix.length - 1;
  const endCol = startCol + width - 1;
  sheet.getRange(`${colName(startCol)}${startRow}:${colName(endCol)}${endRow}`).values = padded;
  return { endRow, endCol };
}

function styleData(sheet, rows, widths = {}) {
  const last = colName(rows[0].length);
  sheet.getRange(`A1:${last}1`).format = {
    fill: "#17324D",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
    rowHeight: 34,
  };
  sheet.getRange(`A2:${last}${rows.length}`).format.font = { size: 9 };
  sheet.getRange(`A1:${last}${rows.length}`).format.borders = {
    bottom: { style: "thin", color: "#D8E1E8" },
  };
  sheet.freezePanes.freezeRows(1);
  for (let c = 1; c <= rows[0].length; c++) {
    sheet.getRange(`${colName(c)}:${colName(c)}`).format.columnWidth = widths[c] ?? 17;
  }
  sheet.getRange(`A1:${last}${rows.length}`).format.autofitRows();
}

const scenario = await readCsv("scenario_summary.csv");
const posterior = await readCsv("posterior_latitude_sensitivity.csv");
const eof = await readCsv("eof_predictive_summary.csv");
const manoeuvre = await readCsv("pp_manoeuvre_summary.csv");
const direct = await readCsv("direct_eof_time_shift.csv");
const compensation = await readCsv("fuel_compensation_requirements.csv");
const sensitivity = await readCsv("model_sensitivity_grid.csv");
const distanceAnchor = await readCsv("distance_anchor_sensitivity.csv");
const fuelFlow = await readCsv("speed_altitude_fuel_flow_examples.csv");

const wb = Workbook.create();
const summary = wb.worksheets.add("Summary");
const sc = wb.worksheets.add("Scenario Results");
const post = wb.worksheets.add("Posterior Results");
const ef = wb.worksheets.add("EOF Timing");
const man = wb.worksheets.add("PP Manoeuvre MC");
const comp = wb.worksheets.add("Compensation");
const sens = wb.worksheets.add("Sensitivity Grid");
const anchor = wb.worksheets.add("Distance Anchor Test");
const ff = wb.worksheets.add("Fuel Flow Examples");
const sources = wb.worksheets.add("Sources & Limits");

putMatrix(sc, 1, 1, scenario);
putMatrix(post, 1, 1, posterior);
putMatrix(ef, 1, 1, eof);
putMatrix(man, 1, 1, manoeuvre);
putMatrix(comp, 1, 1, compensation);
putMatrix(comp, compensation.length + 3, 1, direct);
putMatrix(sens, 1, 1, sensitivity);
putMatrix(anchor, 1, 1, distanceAnchor);
putMatrix(ff, 1, 1, fuelFlow);

styleData(sc, scenario, {1: 18});
styleData(post, posterior, {1: 45});
styleData(ef, eof, {1: 18, 8: 28});
styleData(man, manoeuvre, {1: 15, 2: 33, 3: 11});
styleData(comp, compensation, {1: 15, 2: 24});
styleData(sens, sensitivity, {1: 15});
styleData(anchor, distanceAnchor, {1: 15, 2: 22});
styleData(ff, fuelFlow, {1: 18, 2: 15, 3: 12, 4: 24});

sc.getRange(`B2:L${scenario.length}`).format.numberFormat = "0.000";
post.getRange(`B2:X${posterior.length}`).format.numberFormat = "0.000";
ef.getRange(`B2:G${eof.length}`).format.numberFormat = "0.000";
man.getRange(`D2:I${manoeuvre.length}`).format.numberFormat = "0.000";
comp.getRange(`C2:G${compensation.length}`).format.numberFormat = "0.000";
sens.getRange(`B2:J${sensitivity.length}`).format.numberFormat = "0.000";
anchor.getRange(`C2:M${distanceAnchor.length}`).format.numberFormat = "0.000";
ff.getRange(`D2:D${fuelFlow.length}`).format.numberFormat = "0.000";

const dStart = compensation.length + 3;
comp.getRange(`A${dStart}:F${dStart}`).format = {
  fill: "#17324D", font: { bold: true, color: "#FFFFFF" }, wrapText: true, rowHeight: 34,
};
comp.getRange(`C${dStart + 1}:E${dStart + direct.length - 1}`).format.numberFormat = "0.000";
comp.getRange(`F${dStart + 1}:F${dStart + direct.length - 1}`).format.columnWidth = 29;

summary.mergeCells("A1:J1");
summary.getRange("A1").values = [["MH370 Pulau Perak Descent/Re-climb Sensitivity"]];
summary.getRange("A1:J1").format = {
  fill: "#0A2033", font: { bold: true, color: "#FFFFFF", size: 18 }, rowHeight: 34,
};
summary.mergeCells("A2:J2");
summary.getRange("A2").values = [["1.2 million-particle 00:11 posterior; refined 0.995-Hz fast-BFO model; no 00:19 RF, drift or Pleiades likelihood."]];
summary.getRange("A2:J2").format = { font: { italic: true, color: "#4A5B6A" }, wrapText: true, rowHeight: 25 };

summary.getRange("A4:D4").values = [["Central result", "No PP", "PP only", "Full PP branch"]];
summary.getRange("A5:A10").values = [
  ["Median fuel change vs FL340/M0.84 (t)"],
  ["Median EOF, minutes after 00:11"],
  ["P(EOF from 00:11 to 00:19)"],
  ["Conditioned median 00:11 latitude (°)"],
  ["Latitude shift vs same-window no-PP (°)"],
  ["Conditioned median Mach"],
];
for (let j = 0; j < 3; j++) {
  const col = colName(j + 2);
  const sourceRow = j + 2;
  summary.getRange(`${col}5:${col}10`).formulas = [
    [`='Scenario Results'!B${sourceRow}`],
    [`='Scenario Results'!E${sourceRow}`],
    [`='Scenario Results'!F${sourceRow}`],
    [`='Scenario Results'!I${sourceRow}`],
    [`='Scenario Results'!J${sourceRow}`],
    [`='Scenario Results'!K${sourceRow}`],
  ];
}
summary.getRange("A4:D4").format = { fill: "#17324D", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("A5:A10").format = { fill: "#E8F0F6", font: { bold: true } };
summary.getRange("B5:D6").format.numberFormat = "0.00";
summary.getRange("B7:D7").format.numberFormat = "0.0%";
summary.getRange("B8:D10").format.numberFormat = "0.000";

summary.mergeCells("A13:J13");
summary.getRange("A13").values = [["Interpretation"]];
summary.getRange("A13:J13").format = { fill: "#0A2033", font: { bold: true, color: "#FFFFFF" } };
summary.mergeCells("A14:J18");
summary.getRange("A14").values = [[
  "The Pulau Perak branch changes the fuel state much more than the sixth-arc position. In the central model, the descent/re-climb alone has a median fuel cost close to zero because idle descent savings offset re-climb burn. Including an earlier high-altitude climb raises the median cost to about 0.17 t and moves the unchanged-settings exhaustion centre earlier by about 1.7 minutes. Once the 00:11–00:19 exhaustion window is imposed, the 00:11 median latitude changes by only about 0.003°, while the posterior's 95% latitude interval remains about five degrees wide."
]];
summary.getRange("A14:J18").format = { wrapText: true, verticalAlignment: "top", fill: "#F3F7FA" };

summary.mergeCells("A21:J21");
summary.getRange("A21").values = [["How to read the results"]];
summary.getRange("A21:J21").format = { fill: "#8A4B08", font: { bold: true, color: "#FFFFFF" } };
summary.mergeCells("A22:J26");
summary.getRange("A22").values = [[
  "The 00:11–00:19 interval is a stress-test condition, not evidence taken from the 00:19 transmission. The 4,800-ft value is likewise a scenario input, not an accepted radar altitude. The main run treats the later radar track as a position/heading constraint. The Distance Anchor Test deliberately carries the PP speed deficit forward instead; even then, the median latitude shift remains below 0.01°. The refined particle checkpoint is absent, so exact upstream radar/Mach/gain/BFO-bias correlations are unavailable."
]];
summary.getRange("A22:J26").format = { wrapText: true, verticalAlignment: "top", fill: "#FFF6E8" };

summary.freezePanes.freezeRows(2);
summary.getRange("A:A").format.columnWidth = 42;
summary.getRange("B:D").format.columnWidth = 20;
summary.getRange("E:J").format.columnWidth = 12;

const srcRows = [
  ["Source / item", "Use in this sensitivity", "URL / local file"],
  ["9M-MRO Fuel Model V5.X", "Static Boeing-derived LRC, MRC, M0.84 and holding tables; 1.5% PDA; 870 kg/h/engine idle descent; 87.5 kg/h/engine packs-off saving; +37% climb response per 1,000 fpm as central case.", "downloads/MH370/9M-MRO Fuel Model V5.X.xlsm"],
  ["Malaysia MH370 Safety Investigation", "Official source family for the unreliable military-radar height labels and the investigation record.", "https://www.mot.gov.my/en/aviation/reports/archived-report/mh370"],
  ["ATSB MH370 investigation", "Documents the DSTG 6th-arc PDF, aircraft-dynamics/weather modelling and Boeing achievable-range comparison.", "https://www.atsb.gov.au/investigations/ae-2014-054"],
  ["Davey et al. (2015)", "Radar prior at 18:01:49; 18:22 point not used numerically; note that the aircraft may have slowed and climbed after 18:02.", "downloads/MH370/Bayesian_Methods_MH370_Search_3Dec2015.pdf"],
  ["Refined project estimator", "Reconstructed 00:11 BTO+BFO+RSL/gain posterior; random fast-BFO sigma 0.995 Hz.", "run_refined_bfo_0011_airborne.py"],
  ["PP scenario", "Reported gap 18:03:09--18:15:25; 4,800-ft stress value; 29,500-ft reappearance. Values are not treated as reliable measured altitudes.", "build_mh370_paper_draft.py and user dissertation"],
  ["Position inference limit", "The model treats the 18:15/18:22 track as a position/heading constraint, so PP influences the sixth arc through fuel feasibility rather than a post-radar catch-up distance.", "run_pp_descent_climb_sensitivity.py"],
];
putMatrix(sources, 1, 1, srcRows);
styleData(sources, srcRows, {1: 28, 2: 91, 3: 75});
sources.getRange(`A1:C${srcRows.length}`).format.wrapText = true;
sources.getRange(`A1:C${srcRows.length}`).format.autofitRows();

// Render every sheet for visual QA before export.
for (const [sheetName, range] of [
  ["Summary", "A1:J26"],
  ["Scenario Results", `A1:K${scenario.length}`],
  ["Posterior Results", `A1:X${posterior.length}`],
  ["EOF Timing", `A1:H${eof.length}`],
  ["PP Manoeuvre MC", `A1:I${manoeuvre.length}`],
  ["Compensation", `A1:G${dStart + direct.length - 1}`],
  ["Sensitivity Grid", `A1:J${sensitivity.length}`],
  ["Distance Anchor Test", `A1:M${distanceAnchor.length}`],
  ["Fuel Flow Examples", `A1:D${fuelFlow.length}`],
  ["Sources & Limits", `A1:C${srcRows.length}`],
]) {
  const png = await wb.render({ sheetName, range, scale: sheetName === "Summary" ? 1.3 : 0.9, format: "png" });
  const safe = sheetName.toLowerCase().replaceAll(" ", "_").replaceAll("&", "and");
  await fs.writeFile(path.join(outDir, `workbook_preview_${safe}.png`), new Uint8Array(await png.arrayBuffer()));
}

const check = await wb.inspect({
  kind: "table,formula,chart",
  include: "sheet,name,range,values,formulas,type,title",
  maxChars: 22000,
  tableMaxRows: 14,
  tableMaxCols: 14,
});
await fs.writeFile(path.join(outDir, "workbook_inspection.ndjson"), check.ndjson, "utf8");
const errors = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(outDir, "workbook_error_scan.ndjson"), errors.ndjson, "utf8");

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outDir, "MH370_Pulau_Perak_sensitivity.xlsx"));
process.stdout.write(check.ndjson + "\nERROR_SCAN\n" + errors.ndjson + "\n");
