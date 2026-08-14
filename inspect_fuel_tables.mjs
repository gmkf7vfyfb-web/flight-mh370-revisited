const artifactModule = `${process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES}/@oai/artifact-tool/dist/artifact_tool.mjs`;
const { FileBlob, SpreadsheetFile } = await import(artifactModule);

const input = process.argv[2];
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
for (const name of ["MRC Mach", "MRC FF", "CI=52 Mach", "CI=52 FF", "LRC Mach", "LRC FF", "M0.84 FF", "Holding FF", "Endurance Model"]) {
  const out = await wb.inspect({
    kind: "region",
    sheetId: name,
    range: name === "Endurance Model" ? "A1:J40" : "A1:AL24",
    include: "sheet,name,range,values,formulas",
    maxChars: 30000,
    tableMaxRows: 30,
    tableMaxCols: 40,
    tableMaxCellChars: 120,
  });
  process.stdout.write(`SHEET ${name}\n${out.ndjson}\n`);
}
