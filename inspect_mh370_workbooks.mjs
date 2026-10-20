import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

for (const path of process.argv.slice(2)) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
  const out = await wb.inspect({
    kind: "sheet,table",
    include: "id,name,range,values,formulas",
    maxChars: 24000,
    tableMaxRows: 10,
    tableMaxCols: 12,
    tableMaxCellChars: 100,
  });
  process.stdout.write(`FILE ${path}\n${out.ndjson}\n`);
  for (const term of ["18:01", "18:11", "00:11", "fuel flow", "altitude", "Mach", "latitude", "longitude"]) {
    const hits = await wb.inspect({kind:"match",searchTerm:term,options:{useRegex:false,maxResults:40},maxChars:8000});
    process.stdout.write(`MATCH ${term}\n${hits.ndjson}\n`);
  }
}
