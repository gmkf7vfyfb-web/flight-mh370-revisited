#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const codeDirectory = path.dirname(fileURLToPath(import.meta.url));
const python = process.env.PLEIADES_PLOT_PYTHON || "python3";
const result = spawnSync(python, [path.join(codeDirectory, "render_report.py")], {
  cwd: path.resolve(codeDirectory, ".."),
  encoding: "utf8",
  stdio: "inherit",
});

if (result.error) {
  throw new Error(`Could not start ${python}: ${result.error.message}`);
}
if (result.status !== 0) {
  throw new Error(
    `Publication renderer failed with status ${result.status}. `
      + "Install code/requirements-plot.txt and set PLEIADES_PLOT_PYTHON to that environment's Python.",
  );
}
