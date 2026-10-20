import fs from "node:fs/promises";
const artifactModule = `${process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES}/@oai/artifact-tool/dist/artifact_tool.mjs`;
const { FileBlob, SpreadsheetFile } = await import(artifactModule);

const input = process.argv[2];
const output = process.argv[3];
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const specs = {
  "MRC Mach": "B2:T18",
  "MRC FF": "B2:T18",
  "CI=52 Mach": "B2:T18",
  "CI=52 FF": "B2:T18",
  "LRC Mach": "B2:AL21",
  "LRC FF": "B2:AL21",
  "M0.84 FF": "B2:Q21",
  "Holding KIAS": "B2:M13",
  "Holding Mach": "B2:M13",
  "Holding FF": "B2:M13",
  "Endurance Model": "A1:E40",
};
const result = {};
for (const [name, address] of Object.entries(specs)) {
  const sheet = wb.worksheets.getItem(name);
  result[name] = { address, values: sheet.getRange(address).values };
}
await fs.writeFile(output, JSON.stringify(result, null, 2), "utf8");
