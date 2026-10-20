import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

for (const path of process.argv.slice(2)) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
  const sheets = await wb.inspect({kind:"sheet", include:"id,name", maxChars:10000});
  process.stdout.write(`FILE ${path}\n${sheets.ndjson}\n`);
  const hits = await wb.inspect({kind:"match", searchTerm:"16:42|16:55|17:07|01:55|03:21|03:29", options:{useRegex:true,maxResults:200}, maxChars:30000});
  process.stdout.write(`HITS\n${hits.ndjson}\n`);
}
