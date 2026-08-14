import fs from "node:fs/promises";
import path from "node:path";

const artifactModule = `${process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES}/@oai/artifact-tool/dist/artifact_tool.mjs`;
const { SpreadsheetFile, Workbook } = await import(artifactModule);

const root = process.cwd();
const outDir = path.join(root, "outputs", "mh370_stage1_0011");

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
  const endRow = startRow + matrix.length - 1;
  const endCol = startCol + Math.max(...matrix.map(r => r.length)) - 1;
  const width = endCol - startCol + 1;
  const padded = matrix.map(r => [...r, ...Array(width - r.length).fill(null)]);
  const addr = `${colName(startCol)}${startRow}:${colName(endCol)}${endRow}`;
  sheet.getRange(addr).values = padded;
  return { addr, endRow, endCol };
}

function styleDataSheet(sheet, rows, titleColor = "#12355B") {
  const width = rows[0].length;
  const lastCol = colName(width);
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: titleColor,
    font: { bold: true, color: "#FFFFFF" },
    verticalAlignment: "center",
    wrapText: true,
  };
  sheet.getRange(`A1:${lastCol}${rows.length}`).format.borders = {
    bottom: { style: "thin", color: "#D9E2F3" },
  };
  sheet.getRange(`A2:${lastCol}${rows.length}`).format.font = { size: 10 };
  sheet.freezePanes.freezeRows(1);
  sheet.getRange(`A1:${lastCol}${Math.min(rows.length, 200)}`).format.autofitColumns();
  sheet.getRange(`A1:${lastCol}${Math.min(rows.length, 200)}`).format.autofitRows();
}

const results = await readCsv("stage1_summary.csv");
const hypotheses = await readCsv("control_family_hypothesis_tests.csv");
const terminal = await readCsv("terminal_scenario_summary.csv");
const sensitivity = await readCsv("sensitivity_summary.csv");
const assumptions = await readCsv("model_assumptions.csv");

const wb = Workbook.create();
const summary = wb.worksheets.add("Summary");
const resultSheet = wb.worksheets.add("Results");
const hypSheet = wb.worksheets.add("Control Hypotheses");
const sensSheet = wb.worksheets.add("Sensitivity");
const terminalSheet = wb.worksheets.add("Terminal Scenarios");
const assumptionSheet = wb.worksheets.add("Assumptions");
const sourceSheet = wb.worksheets.add("Sources & Limits");

putMatrix(resultSheet, 1, 1, results);
putMatrix(hypSheet, 1, 1, hypotheses);
putMatrix(sensSheet, 1, 1, sensitivity);
putMatrix(terminalSheet, 1, 1, terminal);
putMatrix(assumptionSheet, 1, 1, assumptions);

for (const [sheet, rows] of [
  [resultSheet, results], [hypSheet, hypotheses], [sensSheet, sensitivity],
  [terminalSheet, terminal], [assumptionSheet, assumptions],
]) styleDataSheet(sheet, rows);

resultSheet.getRange(`C2:M${results.length}`).format.numberFormat = "0.000";
hypSheet.getRange(`C2:E${hypotheses.length}`).format.numberFormat = "0.000";
hypSheet.getRange(`F2:G${hypotheses.length}`).format.numberFormat = "0";
sensSheet.getRange(`B2:G${sensitivity.length}`).format.numberFormat = "0.000";
terminalSheet.getRange(`C2:H${terminal.length}`).format.numberFormat = "0.000";
assumptionSheet.getRange("A:A").format.columnWidth = 31;
assumptionSheet.getRange("B:B").format.columnWidth = 95;
assumptionSheet.getRange(`B1:B${assumptions.length}`).format.wrapText = true;

summary.mergeCells("A1:H1");
summary.getRange("A1").values = [["MH370 Stage-1 Integrated Bayesian Estimate — Through 00:11 UTC"]];
summary.getRange("A1:H1").format = {
  fill: "#0B1F33",
  font: { bold: true, color: "#FFFFFF", size: 18 },
  rowHeight: 32,
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
summary.mergeCells("A2:H2");
summary.getRange("A2").values = [["BTO + BFO + received power/3-D gain + aircraft performance + terminal flight + model-averaged ocean drift. No 00:19 likelihood."]];
summary.getRange("A2:H2").format = { font: { italic: true, color: "#425466" }, wrapText: true, rowHeight: 28 };

summary.getRange("A4:B4").values = [["Primary integrated impact posterior", "Value"]];
summary.getRange("A5:A12").values = [
  ["2-D mode latitude (°)"], ["2-D mode longitude (°E)"], ["Median latitude (°)"],
  ["Median longitude (°E)"], ["95% latitude low (°)"], ["95% latitude high (°)"],
  ["P(south of 36°S)"], ["Effective sample size"],
];
summary.getRange("B5:B12").formulas = [
  ["=Results!C4"], ["=Results!D4"], ["=Results!E4"], ["=Results!F4"],
  ["=Results!G4"], ["=Results!H4"], ["=Results!L4"], ["=Results!M4"],
];
summary.getRange("A4:B4").format = { fill: "#12355B", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("A5:A12").format = { fill: "#EAF1F8", font: { bold: true } };
summary.getRange("B5:B10").format.numberFormat = "0.000";
summary.getRange("B11").format.numberFormat = "0.0%";
summary.getRange("B12").format.numberFormat = "#,##0";

summary.getRange("A15:B15").values = [["Control family", "Posterior probability"]];
summary.getRange("A16:A18").formulas = [["='Control Hypotheses'!B2"], ["='Control Hypotheses'!B3"], ["='Control Hypotheses'!B4"]];
summary.getRange("B16:B18").formulas = [["='Control Hypotheses'!D2"], ["='Control Hypotheses'!D3"], ["='Control Hypotheses'!D4"]];
summary.getRange("A15:B15").format = { fill: "#2C7A7B", font: { bold: true, color: "#FFFFFF" } };
summary.getRange("B16:B18").format.numberFormat = "0.0%";

summary.getRange("A21:B21").values = [["Sensitivity case", "Impact median latitude (°)"]];
for (let i = 0; i < sensitivity.length - 1; i++) {
  summary.getRange(`A${22 + i}:B${22 + i}`).formulas = [[`=Sensitivity!A${2 + i}`, `=Sensitivity!D${2 + i}`]];
}
summary.getRange(`A21:B${20 + sensitivity.length}`).format.wrapText = true;
summary.getRange("A21:B21").format = { fill: "#6B4F8A", font: { bold: true, color: "#FFFFFF" } };
summary.getRange(`B22:B${20 + sensitivity.length}`).format.numberFormat = "0.000";

const familyChart = summary.charts.add("bar", summary.getRange("A15:B18"));
familyChart.title = "00:11 control families remain viable";
familyChart.hasLegend = false;
familyChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
familyChart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 };
familyChart.setPosition("D4", "K16");

const sensitivityEnd = 20 + sensitivity.length;
const sensitivityChart = summary.charts.add("bar", summary.getRange(`A21:B${sensitivityEnd}`));
sensitivityChart.title = "Impact median is insensitive to tested priors";
sensitivityChart.hasLegend = false;
sensitivityChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 8 } };
sensitivityChart.yAxis = { numberFormatCode: "0.0", min: -37.8, max: -36.5 };
sensitivityChart.setPosition("D18", "K33");

summary.getRange("A35:H35").merge();
summary.getRange("A35").values = [["Interpretation"]];
summary.getRange("A35:H35").format = { fill: "#0B1F33", font: { bold: true, color: "#FFFFFF" } };
summary.mergeCells("A36:H39");
summary.getRange("A36").values = [[
  "The 00:11 data favor high-altitude/near-level flight, but only weakly: active descent and an earlier completed descent together retain about half the posterior under equal prior weights. The drift mixture shifts the terminal distribution modestly north; it does not dominate the satellite/RF and performance information. The heat-map width is driven mainly by terminal-flight uncertainty, especially controlled descent/glide direction and distance."
]];
summary.getRange("A36:H39").format = { wrapText: true, verticalAlignment: "top", fill: "#F3F6FA" };
summary.freezePanes.freezeRows(2);
summary.getRange("A:A").format.columnWidth = 36;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 3;
summary.getRange("D:K").format.columnWidth = 12;

const sources = [
  ["Source / limitation", "Use in this run"],
  ["Refined v3 00:11 SMC notes and summary", "Proposal for BTO, BFO, received power, 3-D AES gain, correlated BFO bias, radar and stochastic dynamics."],
  ["Davey et al., Bayesian Methods in the Search for MH370 (2015)", "Radar prior, trajectory process, aircraft-performance bounds, ~100 nmi maximum controlled glide, and weak Reunion-debris drift likelihood."],
  ["MH370 drift meta-analysis", "Alternative broad drift likelihood: 12-study mean 30.2°S and imputed 12°S–38°S 95% range."],
  ["9M-MRO Fuel Model V5.X", "Performance/endurance plausibility and fuel-exhaustion timing prior; full workbook equations were not reimplemented here."],
  ["Proposal limitation", "The project did not contain the refined v3 particle checkpoint. Its reported multimodal marginal was reconstructed and cross-arc geometry calibrated to the reported joint median."],
  ["Weather limitation", "Exact March 2014 ACCESS-G grids were not locally available. The inherited Davey wind-error treatment and broad terminal wind term are used."],
  ["00:19 exclusion", "No 00:19 BTO, BFO, log-on, or power measurement conditions this stage. Airborne-at-00:19 probabilities are diagnostics only."],
  ["Drift dependence", "Davey and meta-analysis studies are model-averaged after unit-mean normalization; dependent studies are not multiplied as independent evidence."],
  ["Interpretive status", "Research-grade stage-1 estimate. It is suitable for narrowing and testing hypotheses, not for declaring a unique crash point."],
];
putMatrix(sourceSheet, 1, 1, sources);
styleDataSheet(sourceSheet, sources, "#7A2E2E");
sourceSheet.getRange("A:A").format.columnWidth = 32;
sourceSheet.getRange("B:B").format.columnWidth = 105;
sourceSheet.getRange(`A1:B${sources.length}`).format.wrapText = true;
sourceSheet.getRange(`A1:B${sources.length}`).format.autofitRows();

const preview = await wb.render({ sheetName: "Summary", range: "A1:K39", scale: 1, format: "png" });
await fs.writeFile(path.join(outDir, "mh370_stage1_workbook_preview.png"), new Uint8Array(await preview.arrayBuffer()));
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(outDir, "MH370_stage1_integrated_estimate_through_0011Z.xlsx"));

const inspection = await wb.inspect({
  kind: "table,formula,error,chart",
  include: "sheet,name,range,values,formulas,error,type,title",
  maxChars: 18000,
  tableMaxRows: 12,
  tableMaxCols: 14,
});
await fs.writeFile(path.join(outDir, "workbook_inspection.ndjson"), inspection.ndjson, "utf8");
process.stdout.write(inspection.ndjson + "\n");
