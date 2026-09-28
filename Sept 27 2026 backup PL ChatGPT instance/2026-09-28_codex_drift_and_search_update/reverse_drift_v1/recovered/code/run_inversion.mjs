#!/usr/bin/env node

import { createHash } from "node:crypto";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Worker } from "node:worker_threads";

import {
  buildSourceGrid,
  haversineKm,
  modelAverageSurface,
  normalizeSurface,
  readObjects,
  summarizeSurface,
  totalVariation,
  uniformSubsetAveragedIdentityWeights,
} from "./transport_core.mjs";

const runStarted = performance.now();
const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(bundle, "data");
const outputDir = path.join(bundle, "outputs");
const config = JSON.parse(await readFile(path.join(dataDir, "config.json"), "utf8"));
const objects = readObjects(await readFile(path.join(dataDir, "pleiades-rating5-objects.csv"), "utf8"));
const geojson = JSON.parse(await readFile(path.join(dataDir, "seventh_arc_fl400.geojson"), "utf8"));
const sourceGrid = buildSourceGrid(geojson, config);
const objectsBySet = {
  all_rating5: objects.filter((object) => object.sets.has("all_rating5")),
  morphology_shortlist5: objects.filter((object) => object.sets.has("morphology_shortlist5")),
};

await mkdir(outputDir, { recursive: true });
if (process.argv.includes("--render-only")) {
  const priorResult = JSON.parse(await readFile(path.join(outputDir, "summary.json"), "utf8"));
  await writeDerivedControls(priorResult);
  priorResult.implementation = await implementationIdentity();
  await writeFile(path.join(outputDir, "summary.json"), `${JSON.stringify(priorResult, null, 2)}\n`);
  await import("./render_report.mjs");
  await writeOutputManifest(priorResult);
  console.log("rendered existing ensemble outputs");
  process.exit(0);
}


const modelSpecifications = [
  {
    id: "bran2016",
    label: "BRAN2016 2.5 m layer",
    currentStem: "bran2016-surface-currents-20140308-23",
    stokesStem: null,
  },
  {
    id: "oscar_v2_final",
    label: "OSCAR v2 Final upper-30-m control",
    currentStem: "oscar-v2-final-20140308-23",
    stokesStem: null,
  },
  {
    id: "glorys12_waverys",
    label: "GLORYS12 0.494 m plus WAVERYS surface Stokes",
    currentStem: "cmems-glorys12-surface-currents-20140308-24",
    stokesStem: "cmems-waverys-surface-stokes-20140308-23",
  },
];
const currentModels = [];
for (const specification of modelSpecifications) {
  const manifestPath = path.join(dataDir, `${specification.currentStem}.manifest.json`);
  if (!(await exists(manifestPath))) continue;
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  if (manifest.status && manifest.status !== "retrieved") continue;
  let stokesManifest = null;
  if (specification.stokesStem) {
    const stokesPath = path.join(dataDir, `${specification.stokesStem}.manifest.json`);
    if (!(await exists(stokesPath))) continue;
    stokesManifest = JSON.parse(await readFile(stokesPath, "utf8"));
    if (stokesManifest.status && stokesManifest.status !== "retrieved") continue;
  }
  currentModels.push({
    ...specification,
    stem: specification.currentStem,
    manifest,
    stokesManifest,
  });
}
if (currentModels.length === 0) throw new Error("no current product is available");

console.log(`source cells: ${sourceGrid.cells.length}; current models: ${currentModels.map((model) => model.id).join(", ")}`);

const scenarioTasks = [];
for (const model of currentModels) {
  for (const seed of config.seeds) {
    scenarioTasks.push({
      category: "primary",
      label: `primary ${model.id} seed ${seed}`,
      currentModel: model.id,
      currentStem: model.stem,
      stokesStem: model.stokesStem,
      seed,
      particleCount: config.particles_per_windage_primary,
      diffusionRmsNmPerDay: config.primary_diffusion_rms_nm_per_day,
      kernelSigmasKm: [
        config.primary_kernel_sigma_km,
        ...config.kernel_sensitivity_km,
      ],
      objectSets: ["all_rating5", "morphology_shortlist5"],
    });
  }
}
for (const model of currentModels) {
  for (const diffusion of config.diffusion_sensitivity_nm_per_day) {
    for (const seed of config.seeds) {
      scenarioTasks.push({
        category: "sensitivity",
        label: `diffusion ${diffusion} NM/day ${model.id} seed ${seed}`,
        currentModel: model.id,
        currentStem: model.stem,
        stokesStem: model.stokesStem,
        seed,
        particleCount: config.particles_per_windage_sensitivity,
        diffusionRmsNmPerDay: diffusion,
        kernelSigmasKm: [config.primary_kernel_sigma_km],
        objectSets: ["all_rating5"],
      });
    }
  }
}

const requestedWorkers = Number(process.env.PLEIADES_WORKERS ?? 3);
if (!Number.isInteger(requestedWorkers) || requestedWorkers < 1) {
  throw new Error("PLEIADES_WORKERS must be a positive integer");
}
const workerConcurrency = Math.min(requestedWorkers, scenarioTasks.length);
console.log(`evaluating ${scenarioTasks.length} scenarios with ${workerConcurrency} workers`);
const scenarioResults = await runWorkerPool(scenarioTasks, workerConcurrency);
const primaryRows = [];
const sensitivityRows = [];
for (const result of scenarioResults) {
  if (result.task.category === "primary") primaryRows.push(...result.rows);
  else sensitivityRows.push(...result.rows);
}

await writeFile(path.join(outputDir, "forward-ensemble-primary-seeds.csv"), rowsToCsv(primaryRows));
await writeFile(path.join(outputDir, "forward-ensemble-diffusion-sensitivity.csv"), rowsToCsv(sensitivityRows));

const aggregated = aggregatePrimary(primaryRows, currentModels);
const diffusionAggregated = aggregateDiffusion(sensitivityRows, currentModels);
const summaries = {};
const surfaces = {};
for (const model of currentModels) {
  const modelRows = aggregated.filter((row) => row.current_model === model.id);
  const modelSensitivity = diffusionAggregated.filter((row) => row.current_model === model.id);
  const scenarios = {
    primary: surfaceFrom(modelRows, "likelihood_all_rating5_sigma10_mixture"),
    kernel_5km: surfaceFrom(modelRows, "likelihood_all_rating5_sigma5_mixture"),
    kernel_20km: surfaceFrom(modelRows, "likelihood_all_rating5_sigma20_mixture"),
    morphology_shortlist5: surfaceFrom(modelRows, "likelihood_morphology_shortlist5_sigma10_mixture"),
    windage_0: surfaceFrom(modelRows, "likelihood_all_rating5_sigma10_windage0"),
    windage_1p2: surfaceFrom(modelRows, "likelihood_all_rating5_sigma10_windage1"),
    windage_3: surfaceFrom(modelRows, "likelihood_all_rating5_sigma10_windage2"),
  };
  for (const diffusion of config.diffusion_sensitivity_nm_per_day) {
    scenarios[`diffusion_${diffusion}nm_day`] = surfaceFrom(
      modelSensitivity.filter((row) => row.diffusion_rms_nm_day === diffusion),
      "likelihood_all_rating5_sigma10_mixture",
    );
  }
  surfaces[model.id] = scenarios;
  summaries[model.id] = Object.fromEntries(Object.entries(scenarios).map(([name, surface]) => [name, {
    ...summarizeSurface(surface),
    massWithin30NmOfArc: massWhere(surface, (row) => Math.abs(row.crossNm) <= 30),
    massEastOfArc: massWhere(surface, (row) => row.crossNm > 0),
    massWestOfArc: massWhere(surface, (row) => row.crossNm < 0),
  }]));
}

const convergence = convergenceDiagnostics(primaryRows, currentModels);
const currentFamilyComparisons = pairwiseCurrentFamilyComparisons(currentModels, surfaces, summaries);
const branOscarComparison = currentFamilyComparisons.find((entry) => (
  entry.first_model === "bran2016" && entry.second_model === "oscar_v2_final"
));
const currentComparison = branOscarComparison ? {
  totalVariation: branOscarComparison.total_variation,
  modeSeparationKm: branOscarComparison.mode_separation_km,
  meanSeparationKm: branOscarComparison.mean_separation_km,
} : { status: "blocked_bran_or_oscar_not_available" };

const primarySurfaceRows = [];
for (const model of currentModels) {
  const surface = surfaces[model.id].primary;
  const hpd = summaries[model.id].primary.hpd;
  for (const row of surface) {
    primarySurfaceRows.push({
      current_model: model.id,
      ...row,
      in_hpd50: row.densityPerKm2 >= hpd[0.5].densityThresholdPerKm2,
      in_hpd90: row.densityPerKm2 >= hpd[0.9].densityThresholdPerKm2,
      in_hpd95: row.densityPerKm2 >= hpd[0.95].densityThresholdPerKm2,
    });
  }
}
await writeFile(path.join(outputDir, "conditional-impact-density.csv"), rowsToCsv(primarySurfaceRows));

const result = {
  schema_version: 1,
  status: "derived_model_conditional",
  identity_conclusion: "unknown",
  generated_utc: new Date().toISOString(),
  implementation: await implementationIdentity(),
  configuration: config,
  execution: {
    worker_concurrency: workerConcurrency,
    wall_seconds_before_render: (performance.now() - runStarted) / 1000,
    maximum_resident_set_mb: process.resourceUsage().maxRSS / 1024,
  },
  source_grid: {
    cells: sourceGrid.cells.length,
    along_cells: sourceGrid.alongCount,
    cross_cells: sourceGrid.crossCount,
    nominal_cell_area_km2: config.arc_spacing_nm * config.cross_arc_spacing_nm * 1.852 ** 2,
    support_area_km2: sourceGrid.cells.reduce((sum, cell) => sum + cell.cellAreaKm2, 0),
  },
  objects: {
    all_rating5: objectsBySet.all_rating5.map((object) => object.id),
    morphology_shortlist5: objectsBySet.morphology_shortlist5.map((object) => object.id),
  },
  current_models: currentModels.map((model) => ({
    id: model.id,
    label: model.label,
    input_sha256: model.manifest.sha256,
    current_input_sha256: model.manifest.sha256,
    stokes_input_sha256: model.stokesManifest?.sha256 ?? null,
    velocity_terms: model.stokesManifest
      ? ["Eulerian ocean current", "surface Stokes drift", "windage × 10 m wind"]
      : ["ocean-current product", "windage × 10 m wind"],
  })),
  summaries,
  convergence,
  current_product_comparison: currentComparison,
  current_family_comparisons: currentFamilyComparisons,
  interpretation: "Normalized forward-transport compatibility over declared support; not a calibrated crash posterior or object-identity finding.",
};
await writeDerivedControls(result);
await writeFile(path.join(outputDir, "summary.json"), `${JSON.stringify(result, null, 2)}\n`);

await import("./render_report.mjs");
await writeOutputManifest(result);
console.log(JSON.stringify({
  models: currentModels.map((model) => model.id),
  modes: Object.fromEntries(currentModels.map((model) => [model.id, summaries[model.id].primary.mode])),
  current_product_comparison: currentComparison,
}, null, 2));

async function implementationIdentity() {
  const relativeFiles = [
    "code/fetch_data.mjs",
    "code/prepare_cmems_fields.py",
    "code/transport_core.mjs",
    "code/scenario_worker.mjs",
    "code/run_inversion.mjs",
    "code/render_report.mjs",
    "code/render_report.py",
    "code/requirements-plot.txt",
  ];
  const files = [];
  const combined = createHash("sha256");
  for (const relative of relativeFiles) {
    const bytes = await readFile(path.join(bundle, relative));
    const digest = createHash("sha256").update(bytes).digest("hex");
    files.push({ path: relative, sha256: digest });
    combined.update(relative).update("\0").update(digest).update("\n");
  }
  const inputManifest = await readFile(path.join(dataDir, "input-manifest.json"));
  return {
    source_control_revision: null,
    identity_method: "SHA-256 file inventory (checkout has no usable Git revision)",
    node_version: process.version,
    files,
    combined_sha256: combined.digest("hex"),
    input_manifest_sha256: createHash("sha256").update(inputManifest).digest("hex"),
  };
}

async function exists(filename) {
  try {
    await stat(filename);
    return true;
  } catch {
    return false;
  }
}

async function runWorkerPool(tasks, concurrency) {
  const results = new Array(tasks.length);
  let nextIndex = 0;
  async function consume(slot) {
    while (nextIndex < tasks.length) {
      const index = nextIndex;
      nextIndex += 1;
      const task = tasks[index];
      console.log(`worker ${slot}: ${task.label}`);
      results[index] = { task, rows: await runWorker(task, slot) };
    }
  }
  await Promise.all(Array.from({ length: concurrency }, (_, index) => consume(index + 1)));
  return results;
}

function runWorker(task, slot) {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL("./scenario_worker.mjs", import.meta.url), { workerData: task });
    let resolved = false;
    worker.on("message", (message) => {
      if (message.type === "progress") {
        console.log(`  worker ${slot} ${task.label}: ${message.completed}/${message.total}`);
      } else if (message.type === "result") {
        resolved = true;
        resolve(message.rows);
      }
    });
    worker.on("error", reject);
    worker.on("exit", (code) => {
      if (code !== 0) reject(new Error(`worker ${slot} exited with code ${code}: ${task.label}`));
      else if (!resolved) reject(new Error(`worker ${slot} exited without a result: ${task.label}`));
    });
  });
}

function aggregatePrimary(rows, models) {
  const groups = new Map();
  for (const row of rows) {
    const key = `${row.current_model}|${row.id}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  const result = [];
  for (const model of models) {
    for (const cell of sourceGrid.cells) {
      const group = groups.get(`${model.id}|${cell.id}`);
      if (!group || group.length !== config.seeds.length) throw new Error(`incomplete seed group ${model.id} ${cell.id}`);
      result.push(meanRows(group));
    }
  }
  return result;
}

function aggregateDiffusion(rows, models) {
  const groups = new Map();
  for (const row of rows) {
    const key = `${row.current_model}|${row.diffusion_rms_nm_day}|${row.id}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  const result = [];
  for (const model of models) {
    for (const diffusion of config.diffusion_sensitivity_nm_per_day) {
      for (const cell of sourceGrid.cells) {
        const group = groups.get(`${model.id}|${diffusion}|${cell.id}`);
        if (!group || group.length !== config.seeds.length) throw new Error(`incomplete diffusion group ${model.id} ${diffusion} ${cell.id}`);
        result.push(meanRows(group));
      }
    }
  }
  return result;
}

function meanRows(group) {
  const output = { ...group[0] };
  output.seed = "mean";
  for (const key of Object.keys(output)) {
    if (key.startsWith("likelihood_") || key === "valid_particles") {
      output[key] = group.reduce((sum, row) => sum + Number(row[key]), 0) / group.length;
    }
  }
  return output;
}

function surfaceFrom(rows, likelihoodKey) {
  if (rows.length !== sourceGrid.cells.length) throw new Error(`surface ${likelihoodKey} has ${rows.length} rows`);
  return normalizeSurface(rows.map((row) => ({ ...row, likelihood: Number(row[likelihoodKey]) })), "likelihood");
}

function massWhere(surface, predicate) {
  return surface.reduce((sum, row) => sum + (predicate(row) ? row.probabilityMass : 0), 0);
}

function pairwiseCurrentFamilyComparisons(models, modelSurfaces, modelSummaries) {
  const comparisons = [];
  for (let first = 0; first < models.length; first += 1) {
    for (let second = first + 1; second < models.length; second += 1) {
      const firstId = models[first].id;
      const secondId = models[second].id;
      comparisons.push({
        first_model: firstId,
        second_model: secondId,
        total_variation: totalVariation(modelSurfaces[firstId].primary, modelSurfaces[secondId].primary),
        mode_separation_km: haversineKm(
          modelSummaries[firstId].primary.mode,
          modelSummaries[secondId].primary.mode,
        ),
        mean_separation_km: haversineKm(
          modelSummaries[firstId].primary.mean,
          modelSummaries[secondId].primary.mean,
        ),
      });
    }
  }
  return comparisons;
}

async function writeDerivedControls(result) {
  const densityText = await readFile(path.join(outputDir, "conditional-impact-density.csv"), "utf8");
  const densityRows = parseSimpleCsv(densityText).map((row) => ({
    ...row,
    alongIndex: Number(row.alongIndex),
    crossIndex: Number(row.crossIndex),
    alongNm: Number(row.alongNm),
    crossNm: Number(row.crossNm),
    latitude: Number(row.latitude),
    longitude: Number(row.longitude),
    cellAreaKm2: Number(row.cellAreaKm2),
    likelihood: Number(row.likelihood),
    densityPerKm2: Number(row.densityPerKm2),
    probabilityMass: Number(row.probabilityMass),
  }));
  const averageId = "equal_transport_family_model_average";
  const modelWeights = result.current_models.map((model) => ({
    id: model.id,
    weight: 1 / result.current_models.length,
  }));
  if (modelWeights.length > 1) {
    const averaged = modelAverageSurface(modelWeights.map((component) => ({
      ...component,
      surface: densityRows.filter((row) => row.current_model === component.id),
    })));
    const summary = {
      ...summarizeSurface(averaged),
      massWithin30NmOfArc: massWhere(averaged, (row) => Math.abs(row.crossNm) <= 30),
      massEastOfArc: massWhere(averaged, (row) => row.crossNm > 0),
      massWestOfArc: massWhere(averaged, (row) => row.crossNm < 0),
    };
    const modelAverageRows = averaged.map((row) => ({
      current_model: averageId,
      id: row.id,
      alongIndex: row.alongIndex,
      crossIndex: row.crossIndex,
      alongNm: row.alongNm,
      crossNm: row.crossNm,
      latitude: row.latitude,
      longitude: row.longitude,
      cellAreaKm2: row.cellAreaKm2,
      densityPerKm2: row.densityPerKm2,
      probabilityMass: row.probabilityMass,
      in_hpd50: row.densityPerKm2 >= summary.hpd[0.5].densityThresholdPerKm2,
      in_hpd90: row.densityPerKm2 >= summary.hpd[0.9].densityThresholdPerKm2,
      in_hpd95: row.densityPerKm2 >= summary.hpd[0.95].densityThresholdPerKm2,
    }));
    await writeFile(
      path.join(outputDir, "model-averaged-impact-density.csv"),
      rowsToCsv(modelAverageRows),
    );
    result.model_average = {
      id: averageId,
      label: `Equal prior-weighted ${modelWeights.length}-family transport-model average`,
      component_weights: modelWeights,
      primary: summary,
      interpretation: "Equal prior-weighted mixture over explicitly alternative transport families; not a product of independent evidence, an empirically calibrated family posterior, or random-sampling uncertainty.",
    };
  }

  const unnormalizedPrior = [16, 8, 4, 2, 1];
  const identityControl = uniformSubsetAveragedIdentityWeights(5, unnormalizedPrior);
  const identityRows = identityControl.cardinalities.map((entry) => ({
    selected_object_count: entry.cardinality,
    unnormalized_decreasing_prior: entry.unnormalizedPrior,
    prior_probability: entry.priorProbability,
    conditional_inclusion_probability_per_object: entry.inclusionProbabilityPerObject,
    score_weight_if_included: entry.scoreWeightIfIncluded,
    marginal_weight_per_object: entry.marginalWeightPerObject,
    pdf_total_variation_from_exactly_one: 0,
  }));
  await writeFile(
    path.join(outputDir, "identity-cardinality-sensitivity.csv"),
    rowsToCsv(identityRows),
  );
  result.identity_cardinality_sensitivity = {
    object_set: "morphology_shortlist5",
    object_count: 5,
    subset_selection: "Uniform without replacement conditional on selected-object count K.",
    subset_score: "Arithmetic mean of the K selected object-location likelihoods.",
    cardinality_prior: identityControl.cardinalities.map((entry) => ({
      selected_object_count: entry.cardinality,
      prior_probability: entry.priorProbability,
    })),
    resulting_object_weights: identityControl.objectWeights,
    maximum_absolute_difference_from_equal_weight: identityControl.maximumAbsoluteDifferenceFromEqualWeight,
    pdf_total_variation_from_exactly_one: 0,
    conclusion: "Exactly identical to the equal-weight exactly-one mixture by linearity; the result holds for any prior on K when subsets are uniform and their likelihoods are averaged.",
    excluded_alternative: "A joint/product likelihood for several objects is not this sensitivity and would require a correlated debris-survival, dispersion and image-detection model.",
  };
}

function parseSimpleCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const columns = lines.shift().split(",");
  return lines.map((line) => {
    const values = line.split(",");
    if (values.length !== columns.length) throw new Error("unexpected quoted or malformed derived-output CSV");
    return Object.fromEntries(columns.map((column, index) => [column, values[index]]));
  });
}

function convergenceDiagnostics(rows, models) {
  const output = {};
  for (const model of models) {
    const seedSurfaces = config.seeds.map((seed) => surfaceFrom(
      rows.filter((row) => row.current_model === model.id && row.seed === seed),
      "likelihood_all_rating5_sigma10_mixture",
    ));
    const pairwise = [];
    for (let first = 0; first < seedSurfaces.length; first += 1) {
      for (let second = first + 1; second < seedSurfaces.length; second += 1) {
        const firstSummary = summarizeSurface(seedSurfaces[first]);
        const secondSummary = summarizeSurface(seedSurfaces[second]);
        pairwise.push({
          first_seed: config.seeds[first],
          second_seed: config.seeds[second],
          total_variation: totalVariation(seedSurfaces[first], seedSurfaces[second]),
          mode_separation_km: haversineKm(firstSummary.mode, secondSummary.mode),
          mean_separation_km: haversineKm(firstSummary.mean, secondSummary.mean),
        });
      }
    }
    output[model.id] = pairwise;
  }
  return output;
}

function rowsToCsv(rows) {
  if (rows.length === 0) return "";
  const columns = Object.keys(rows[0]);
  return `${columns.join(",")}\n${rows.map((row) => columns.map((column) => csvValue(row[column])).join(",")).join("\n")}\n`;
}

function csvValue(value) {
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "";
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

async function writeOutputManifest(result) {
  const files = [
    "forward-ensemble-primary-seeds.csv",
    "forward-ensemble-diffusion-sensitivity.csv",
    "conditional-impact-density.csv",
    "model-averaged-impact-density.csv",
    "identity-cardinality-sensitivity.csv",
    "summary.json",
    "pleiades-forward-impact-density.svg",
    "pleiades-forward-impact-density.pdf",
    "pleiades-forward-impact-density.png",
  ];
  const entries = [];
  for (const file of files) {
    if (!(await exists(path.join(outputDir, file)))) continue;
    const bytes = await readFile(path.join(outputDir, file));
    entries.push({ path: file, bytes: bytes.length, sha256: createHash("sha256").update(bytes).digest("hex") });
  }
  const manifest = {
    schema_version: 1,
    generated_utc: result.generated_utc,
    inputs: result.current_models,
    implementation: result.implementation,
    outputs: entries,
  };
  await writeFile(path.join(outputDir, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
}


