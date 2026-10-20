import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parentPort, workerData } from "node:worker_threads";

import { VectorField, buildSourceGrid, readObjects, simulateCell } from "../recovered/code/transport_core.mjs";

const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(bundle, "recovered/data");
const task = workerData;
const config = JSON.parse(await readFile(path.join(dataDir, "config.json"), "utf8"));
const objects = readObjects(await readFile(path.join(dataDir, "pleiades-rating5-objects.csv"), "utf8"));
const geojson = JSON.parse(await readFile(path.join(dataDir, "seventh_arc_fl400.geojson"), "utf8"));
const sourceGrid = buildSourceGrid(geojson, config);
const current = await VectorField.load(path.join(dataDir, task.currentStem + ".manifest.json"), dataDir);
const stokes = task.stokesStem
  ? await VectorField.load(path.join(dataDir, task.stokesStem + ".manifest.json"), dataDir)
  : null;
const wind = await VectorField.load(path.join(dataDir, "ncep-ncar-r1-10m-wind-20140308-23.manifest.json"), dataDir);
const availableSets = {
  all_rating5: objects.filter(function (object) { return object.sets.has("all_rating5"); }),
  morphology_shortlist5: objects.filter(function (object) { return object.sets.has("morphology_shortlist5"); }),
};
const french = JSON.parse(await readFile(path.join(bundle, "french_coordinates.json"), "utf8"));
const objectsBySet = {french4:french, eastern3:french.slice(0,3), F4:[french[3]], pleiades:objects};
const rows = [];
const startMs = Date.parse(config.start_utc);
const endMs = Date.parse(task.observationUtc);

for (let cellIndex = 0; cellIndex < sourceGrid.cells.length; cellIndex += 1) {
  const cell = sourceGrid.cells[cellIndex];
  const simulation = simulateCell({
    cell: cell,
    cellIndex: cellIndex,
    current: current,
    stokes: stokes,
    wind: wind,
    objectsBySet: objectsBySet,
    windageFactors: config.windage_factors,
    windagePrior: config.windage_prior,
    particleCount: task.particleCount,
    startMs: startMs,
    endMs: endMs,
    stepSeconds: config.integration_step_hours * 3600,
    diffusionRmsNmPerDay: task.diffusionRmsNmPerDay,
    kernelSigmasKm: task.kernelSigmasKm,
    seed: task.seed,
  });
  const row = {
    current_model: task.currentModel,
    seed: task.seed,
    diffusion_rms_nm_day: task.diffusionRmsNmPerDay,
    particles_per_windage: task.particleCount,
    valid_particles: simulation.validParticles,
    id: cell.id,
    alongIndex: cell.alongIndex,
    crossIndex: cell.crossIndex,
    alongNm: cell.alongNm,
    crossNm: cell.crossNm,
    latitude: cell.latitude,
    longitude: cell.longitude,
    cellAreaKm2: cell.cellAreaKm2,
  };
  for (const [setName, scores] of Object.entries(simulation.scores)) {
    for (const [sigma, score] of Object.entries(scores)) {
      row["likelihood_" + setName + "_sigma" + sigma + "_mixture"] = score.mixture;
      score.byWindage.forEach(function (value, index) {
        row["likelihood_" + setName + "_sigma" + sigma + "_windage" + index] = value;
      });
    }
  }
  rows.push(row);
  if ((cellIndex + 1) % 500 === 0) {
    parentPort.postMessage({ type: "progress", completed: cellIndex + 1, total: sourceGrid.cells.length });
  }
}

parentPort.postMessage({ type: "result", rows: rows });

