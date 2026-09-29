#!/usr/bin/env node

/**
 * Build the truth-separated MH371 final-arc BFO-width sensitivity figure.
 *
 * This is deliberately a report generator, not an inference implementation.
 * It consumes completed canonical inference artifacts. Posterior summaries are
 * calculated before the scorer-only truth file is opened; truth is used only
 * for the final reference overlay and error diagnostics.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const RUN_SCHEMA = "mh370-known-flight-inference-v2";
const EXPECTED_EPOCH = "mh371_0648";
const EXPECTED_SEEDS = [37102001, 37102002];
const BANDWIDTH_DEG = 0.18;
const GRID_POINTS = 520;

const FAMILY_SPECS = [
  {
    option: "loose-run",
    key: "loose",
    expectedModel: "mh370_analog_prior_loose_bfo",
    colour: "#3b6fb6",
  },
  {
    option: "medium-run",
    key: "medium",
    expectedModel: "mh370_analog_prior_medium_bfo",
    colour: "#7a5195",
  },
  {
    option: "tight-run",
    key: "tight",
    expectedModel: "mh370_analog_prior_observed_bfo",
    colour: "#d95f02",
  },
];

function fail(message) {
  throw new Error(message);
}

function parseArguments(argv) {
  const values = new Map();
  for (let index = 0; index < argv.length; index += 2) {
    const option = argv[index];
    const value = argv[index + 1];
    if (!option?.startsWith("--") || value === undefined) {
      fail(`arguments must be supplied as --option value pairs (at ${option ?? "end"})`);
    }
    const key = option.slice(2);
    const entries = values.get(key) ?? [];
    entries.push(value);
    values.set(key, entries);
  }
  for (const spec of FAMILY_SPECS) {
    if ((values.get(spec.option) ?? []).length !== 2) {
      fail(`--${spec.option} must be supplied exactly twice`);
    }
  }
  if ((values.get("truth") ?? []).length !== 1) {
    fail("--truth must be supplied exactly once");
  }
  if ((values.get("output-dir") ?? []).length !== 1) {
    fail("--output-dir must be supplied exactly once");
  }
  const known = new Set([
    ...FAMILY_SPECS.map((spec) => spec.option),
    "truth",
    "output-dir",
  ]);
  for (const key of values.keys()) {
    if (!known.has(key)) fail(`unknown option --${key}`);
  }
  return values;
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function readJson(filePath) {
  const bytes = fs.readFileSync(filePath);
  return { bytes, value: JSON.parse(bytes.toString("utf8")) };
}

function finite(value, label) {
  if (!Number.isFinite(value)) fail(`${label} is not finite`);
  return value;
}

function normalizedRows(snapshot) {
  if (
    !Array.isArray(snapshot?.particles) ||
    !Array.isArray(snapshot?.log_weights) ||
    !Array.isArray(snapshot?.root_ids) ||
    snapshot.particles.length === 0 ||
    snapshot.particles.length !== snapshot.log_weights.length ||
    snapshot.particles.length !== snapshot.root_ids.length
  ) {
    fail("terminal snapshot arrays are absent, empty, or misaligned");
  }
  const raw = snapshot.log_weights.map((value) => Math.exp(finite(value, "log weight")));
  const total = raw.reduce((sum, value) => sum + value, 0);
  if (!(total > 0) || !Number.isFinite(total)) fail("terminal weight total is invalid");
  return snapshot.particles.map((particle, index) => {
    const aircraft = particle?.aircraft;
    return {
      latitude: finite(aircraft?.position?.latitude, "particle latitude"),
      longitude: finite(aircraft?.position?.longitude, "particle longitude"),
      weight: raw[index] / total,
      root: snapshot.root_ids[index],
    };
  });
}

function rootEss(rows) {
  const mass = new Map();
  for (const row of rows) mass.set(row.root, (mass.get(row.root) ?? 0) + row.weight);
  return 1 / [...mass.values()].reduce((sum, value) => sum + value * value, 0);
}

function particleEss(rows) {
  return 1 / rows.reduce((sum, row) => sum + row.weight * row.weight, 0);
}

function quantile(sortedRows, probability) {
  let cumulative = 0;
  for (const row of sortedRows) {
    cumulative += row.weight;
    if (cumulative + 1e-15 >= probability) return row;
  }
  return sortedRows.at(-1);
}

function radians(degrees) {
  return (degrees * Math.PI) / 180;
}

function greatCircleNm(first, second) {
  const radiusNm = 3440.065;
  const phi1 = radians(first.latitude);
  const phi2 = radians(second.latitude);
  const deltaPhi = phi2 - phi1;
  const deltaLambda = radians(second.longitude - first.longitude);
  const haversine =
    Math.sin(deltaPhi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) ** 2;
  return 2 * radiusNm * Math.asin(Math.sqrt(Math.max(0, Math.min(1, haversine))));
}

function circularMeanDegrees(rows) {
  const sine = rows.reduce(
    (sum, row) => sum + row.weight * Math.sin(radians(row.longitude)),
    0,
  );
  const cosine = rows.reduce(
    (sum, row) => sum + row.weight * Math.cos(radians(row.longitude)),
    0,
  );
  return (Math.atan2(sine, cosine) * 180) / Math.PI;
}

function loadFamily(spec, runPaths) {
  const runs = runPaths.map((runPath) => {
    const { bytes, value: run } = readJson(runPath);
    if (run.schema_version !== RUN_SCHEMA) fail(`${runPath}: unsupported run schema`);
    if (run.model_family !== spec.expectedModel) {
      fail(`${runPath}: expected ${spec.expectedModel}, found ${run.model_family}`);
    }
    if (!EXPECTED_SEEDS.includes(run.seed)) fail(`${runPath}: unexpected seed ${run.seed}`);
    const terminalObservation = run.observations?.at(-1);
    const terminalSnapshot = run.filter?.snapshots?.at(-1);
    if (
      terminalObservation?.epoch_id !== EXPECTED_EPOCH ||
      terminalSnapshot?.observation_index !== run.observations.length - 1 ||
      Math.abs(terminalSnapshot.observation_time_s - terminalObservation.satcom.time) > 1e-6
    ) {
      fail(`${runPath}: terminal observation/snapshot is not the frozen ${EXPECTED_EPOCH} epoch`);
    }
    const bfoSd = finite(terminalObservation.satcom.bfo_sd, "BFO SD");
    for (const observation of run.observations) {
      if (Math.abs(observation.satcom.bfo_sd - bfoSd) > 1e-12) {
        fail(`${runPath}: BFO SD changes within the run`);
      }
    }
    return {
      path: runPath,
      sha256: sha256(bytes),
      seed: run.seed,
      inferenceSha256: run.inference_sha256,
      sourcePackageId: run.source_package_id,
      particleCount: run.particle_count,
      bfoSd,
      rows: normalizedRows(terminalSnapshot),
    };
  });
  runs.sort((left, right) => left.seed - right.seed);
  if (runs.map((run) => run.seed).join(",") !== EXPECTED_SEEDS.join(",")) {
    fail(`${spec.key}: seed plan differs from ${EXPECTED_SEEDS.join(", ")}`);
  }
  const invariant = (field) => new Set(runs.map((run) => run[field])).size === 1;
  for (const field of ["inferenceSha256", "sourcePackageId", "particleCount", "bfoSd"]) {
    if (!invariant(field)) fail(`${spec.key}: ${field} differs between seeds`);
  }
  const combined = runs.flatMap((run) =>
    run.rows.map((row) => ({ ...row, weight: row.weight / runs.length })),
  );
  const sorted = [...combined].sort((left, right) => left.latitude - right.latitude);
  const lower95 = quantile(sorted, 0.025);
  const upper95 = quantile(sorted, 0.975);
  return {
    ...spec,
    runs,
    combined,
    bfoSd: runs[0].bfoSd,
    lower95,
    upper95,
    q005: quantile(sorted, 0.005),
    q995: quantile(sorted, 0.995),
    endpointSeparationNm: greatCircleNm(lower95, upper95),
  };
}

function parseTruth(filePath) {
  const bytes = fs.readFileSync(filePath);
  const lines = bytes
    .toString("utf8")
    .trim()
    .split(/\r?\n/)
    .filter((line) => line.trim() !== "");
  const header = lines[0].split(",");
  const field = (name) => {
    const index = header.indexOf(name);
    if (index < 0) fail(`truth CSV lacks ${name}`);
    return index;
  };
  const epochColumn = field("epoch_id");
  const latitudeColumn = field("lat_deg");
  const longitudeColumn = field("lon_deg");
  const matches = lines.slice(1).map((line) => line.split(",")).filter(
    (values) => values[epochColumn] === EXPECTED_EPOCH,
  );
  if (matches.length !== 1) fail(`truth CSV must contain exactly one ${EXPECTED_EPOCH} row`);
  return {
    path: filePath,
    sha256: sha256(bytes),
    latitude: finite(Number(matches[0][latitudeColumn]), "truth latitude"),
    longitude: finite(Number(matches[0][longitudeColumn]), "truth longitude"),
  };
}

function posteriorMean(rows) {
  return {
    latitude: rows.reduce((sum, row) => sum + row.weight * row.latitude, 0),
    longitude: circularMeanDegrees(rows),
  };
}

function kde(rows, grid) {
  const denominator = BANDWIDTH_DEG * Math.sqrt(2 * Math.PI);
  return grid.map((latitude) => {
    let density = 0;
    for (const row of rows) {
      const standardized = (latitude - row.latitude) / BANDWIDTH_DEG;
      if (Math.abs(standardized) <= 5) {
        density += row.weight * Math.exp(-0.5 * standardized * standardized) / denominator;
      }
    }
    return density;
  });
}

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function linePath(grid, density, x, y) {
  return grid
    .map((latitude, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command}${x(latitude).toFixed(2)},${y(density[index]).toFixed(2)}`;
    })
    .join(" ");
}

function svgFigure(families, truth) {
  const width = 1600;
  const height = 1260;
  const left = 165;
  const right = 80;
  const top = 180;
  const panelHeight = 235;
  const panelGap = 34;
  const plotWidth = width - left - right;
  const xMinimum = Math.floor(
    Math.min(...families.map((family) => family.q005.latitude), truth.latitude) - 0.45,
  );
  const xMaximum = Math.ceil(
    Math.max(...families.map((family) => family.q995.latitude), truth.latitude) + 0.45,
  );
  const grid = Array.from(
    { length: GRID_POINTS },
    (_, index) => xMinimum + (index / (GRID_POINTS - 1)) * (xMaximum - xMinimum),
  );
  const x = (latitude) => left + ((latitude - xMinimum) / (xMaximum - xMinimum)) * plotWidth;
  const ticks = [];
  for (let value = Math.ceil(xMinimum); value <= Math.floor(xMaximum); value += 1) ticks.push(value);
  const output = [];
  output.push(
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,
    `<rect width="100%" height="100%" fill="#ffffff"/>`,
    `<style>text{font-family:'DejaVu Sans',Arial,sans-serif;fill:#171717}.title{font-size:34px;font-weight:700}.subtitle{font-size:21px;fill:#444}.panel-title{font-size:24px;font-weight:700}.metric{font-size:19px;fill:#333}.axis{font-size:18px;fill:#444}.note{font-size:17px;fill:#4b4b4b}.small{font-size:16px;fill:#555}</style>`,
    `<text class="title" x="${left}" y="58">MH371 final-arc localisation contracts as assumed BFO noise narrows</text>`,
    `<text class="subtitle" x="${left}" y="97">Six truth-blind BTO+BFO epochs; identical Mach/altitude prior and stochastic motion process; only BFO SD changes.</text>`,
    `<text class="subtitle" x="${left}" y="128">Narrower is not monotonically more accurate, and local bumps are not stable trajectory modes.</text>`,
  );

  families.forEach((family, familyIndex) => {
    const yTop = top + familyIndex * (panelHeight + panelGap);
    const yBottom = yTop + panelHeight;
    const combinedDensity = kde(family.combined, grid);
    const seedDensities = family.runs.map((run) => kde(run.rows, grid));
    const maximum = Math.max(...combinedDensity, ...seedDensities.flat());
    const y = (density) => yBottom - (density / maximum) * (panelHeight - 48);
    output.push(
      `<rect x="${left}" y="${yTop}" width="${plotWidth}" height="${panelHeight}" fill="#fbfcfd" stroke="#d7dbe0"/>`,
      `<rect x="${x(family.lower95.latitude).toFixed(2)}" y="${yTop}" width="${(x(family.upper95.latitude) - x(family.lower95.latitude)).toFixed(2)}" height="${panelHeight}" fill="${family.colour}" opacity="0.10"/>`,
    );
    for (const tick of ticks) {
      output.push(
        `<line x1="${x(tick).toFixed(2)}" x2="${x(tick).toFixed(2)}" y1="${yTop}" y2="${yBottom}" stroke="#e5e8eb" stroke-width="1"/>`,
      );
    }
    seedDensities.forEach((density, seedIndex) => {
      output.push(
        `<path d="${linePath(grid, density, x, y)}" fill="none" stroke="#60666d" stroke-width="2.2" opacity="0.80" stroke-dasharray="${seedIndex === 0 ? "10 7" : "2 6"}"/>`,
      );
    });
    output.push(
      `<path d="${linePath(grid, combinedDensity, x, y)}" fill="none" stroke="${family.colour}" stroke-width="5"/>`,
      `<line x1="${x(truth.latitude).toFixed(2)}" x2="${x(truth.latitude).toFixed(2)}" y1="${yTop}" y2="${yBottom}" stroke="#c62828" stroke-width="3" stroke-dasharray="8 5"/>`,
      `<text x="${(x(truth.latitude) + 9).toFixed(2)}" y="${yTop + 27}" fill="#c62828" font-size="20" font-weight="700">★ held-back truth</text>`,
      `<text class="panel-title" x="${left + 22}" y="${yTop + 37}">Assumed BFO SD ${family.bfoSd.toFixed(1)} Hz</text>`,
      `<text class="metric" x="${left + 22}" y="${yTop + 70}">95% equal-tail latitude: ${family.lower95.latitude.toFixed(2)}–${family.upper95.latitude.toFixed(2)}°N  ·  endpoint separation ≈ ${family.endpointSeparationNm.toFixed(0)} NM</text>`,
      `<text class="metric" x="${left + 22}" y="${yTop + 99}">Seed mean errors: ${family.seedMeanErrorsNm.map((value) => value.toFixed(1)).join(" / ")} NM  ·  root ESS: ${family.rootEss.map((value) => value.toFixed(1)).join(" / ")}</text>`,
    );
  });

  const axisY = top + 3 * (panelHeight + panelGap) - panelGap;
  output.push(`<line x1="${left}" x2="${width - right}" y1="${axisY}" y2="${axisY}" stroke="#333" stroke-width="2"/>`);
  for (const tick of ticks) {
    output.push(
      `<line x1="${x(tick).toFixed(2)}" x2="${x(tick).toFixed(2)}" y1="${axisY}" y2="${axisY + 9}" stroke="#333" stroke-width="2"/>`,
      `<text class="axis" x="${x(tick).toFixed(2)}" y="${axisY + 34}" text-anchor="middle">${tick}°</text>`,
    );
  }
  output.push(
    `<text class="axis" x="${left + plotWidth / 2}" y="${axisY + 70}" text-anchor="middle" font-size="21">Latitude along the 06:48:33.907 UTC BTO arc (°N)</text>`,
    `<text class="small" x="${left}" y="${axisY + 101}"><tspan stroke="${families[0].colour}" stroke-width="4">━━</tspan> equal-seed combined marginal   <tspan stroke="#60666d" stroke-width="2">━ ━</tspan> seed 37102001   <tspan stroke="#60666d" stroke-width="2">┄┄</tspan> seed 37102002   shaded band: unsmoothed 95% equal-tail interval</text>`,
    `<text class="note" x="${left}" y="${axisY + 140}">Inference boundary: stochastic piecewise constant-magnetic-heading model with 35°/√h heading updates at SATCOM boundaries.</text>`,
    `<text class="note" x="${left}" y="${axisY + 167}">It does not enforce turn rate, bank angle, flight-plan intent, or continuous manoeuvre feasibility; therefore these are conditional endpoint PDFs, not an aircraft-limit-only feasible set.</text>`,
    `<text class="note" x="${left}" y="${axisY + 194}">Truth was unavailable to inference and loaded only after posterior summaries were fixed. Curves use a display-only Gaussian kernel (h=${BANDWIDTH_DEG.toFixed(2)}°); intervals use unsmoothed weights.</text>`,
    `<text class="note" x="${left}" y="${axisY + 221}">Low terminal root ESS and visibly different seed traces warn against interpreting small peaks as physical modes. Endpoint separation is great-circle distance between weighted latitude-quantile particles.</text>`,
    `<text class="small" x="${width - right}" y="${height - 18}" text-anchor="end">Generated from canonical run artifacts · MH371 computational control, not evidence about MH370 geography</text>`,
    `</svg>`,
  );
  return output.join("\n") + "\n";
}

function csvOutput(families, truth) {
  const header = [
    "model_family",
    "bfo_sd_hz",
    "terminal_epoch",
    "truth_latitude_deg",
    "truth_longitude_deg",
    "latitude_q025_deg",
    "latitude_q975_deg",
    "quantile_endpoint_separation_nm",
    "seed_1",
    "seed_1_mean_error_nm",
    "seed_1_particle_ess",
    "seed_1_root_ess",
    "seed_2",
    "seed_2_mean_error_nm",
    "seed_2_particle_ess",
    "seed_2_root_ess",
  ];
  const rows = families.map((family) => [
    family.expectedModel,
    family.bfoSd,
    EXPECTED_EPOCH,
    truth.latitude,
    truth.longitude,
    family.lower95.latitude,
    family.upper95.latitude,
    family.endpointSeparationNm,
    family.runs[0].seed,
    family.seedMeanErrorsNm[0],
    family.particleEss[0],
    family.rootEss[0],
    family.runs[1].seed,
    family.seedMeanErrorsNm[1],
    family.particleEss[1],
    family.rootEss[1],
  ]);
  return [header, ...rows].map((row) => row.join(",")).join("\n") + "\n";
}

function main() {
  const argumentsMap = parseArguments(process.argv.slice(2));

  // All posterior quantities are fixed before the scorer-only truth file opens.
  const families = FAMILY_SPECS.map((spec) =>
    loadFamily(spec, argumentsMap.get(spec.option)),
  );
  const inferenceHashes = new Set(families.flatMap((family) => family.runs.map((run) => run.inferenceSha256)));
  if (inferenceHashes.size !== 1) fail("families do not share one frozen inference package");
  const truth = parseTruth(argumentsMap.get("truth")[0]);

  for (const family of families) {
    family.rootEss = family.runs.map((run) => rootEss(run.rows));
    family.particleEss = family.runs.map((run) => particleEss(run.rows));
    family.seedMeanErrorsNm = family.runs.map((run) =>
      greatCircleNm(posteriorMean(run.rows), truth),
    );
  }

  const outputDirectory = argumentsMap.get("output-dir")[0];
  fs.mkdirSync(outputDirectory, { recursive: true });
  const svgPath = path.join(outputDirectory, "mh371_final_arc_bfo_sensitivity.svg");
  const csvPath = path.join(outputDirectory, "mh371_final_arc_bfo_sensitivity.csv");
  const manifestPath = path.join(outputDirectory, "mh371_final_arc_bfo_sensitivity_manifest.json");
  const svg = svgFigure(families, truth);
  const csv = csvOutput(families, truth);
  fs.writeFileSync(svgPath, svg);
  fs.writeFileSync(csvPath, csv);

  const generatorPath = fs.realpathSync(new URL(import.meta.url));
  const manifest = {
    schema_version: "mh371-final-arc-bfo-sensitivity-v1",
    status: "complete_truth_separated_conditional_endpoint_sensitivity",
    terminal_epoch: EXPECTED_EPOCH,
    truth_role: "scorer_overlay_and_error_diagnostics_only_loaded_after_posterior_summary",
    inference_boundary:
      "stochastic_piecewise_constant_magnetic_heading; no turn-rate, bank-angle, route-intent, or continuous-manoeuvre constraint",
    display_kernel: {
      type: "gaussian_latitude_kde_visualization_only",
      bandwidth_deg: BANDWIDTH_DEG,
      grid_points: GRID_POINTS,
      interval_source: "unsmoothed_equal_seed_particle_weights",
    },
    generator: {
      path: generatorPath,
      sha256: sha256(fs.readFileSync(generatorPath)),
    },
    truth_input: truth,
    families: families.map((family) => ({
      model_family: family.expectedModel,
      bfo_sd_hz: family.bfoSd,
      runs: family.runs.map((run) => ({
        path: run.path,
        sha256: run.sha256,
        seed: run.seed,
        particles: run.particleCount,
      })),
      latitude_q025_deg: family.lower95.latitude,
      latitude_q975_deg: family.upper95.latitude,
      quantile_endpoint_separation_nm: family.endpointSeparationNm,
      particle_ess: family.particleEss,
      root_ess: family.rootEss,
      seed_mean_error_nm: family.seedMeanErrorsNm,
    })),
    limitations: [
      "known-flight computational control; not evidence about MH370 geography",
      "the endpoint distribution is conditional on the declared stochastic motion family and BFO width",
      "the model does not establish continuous aircraft-performance feasibility between observations",
      "terminal root ESS is low enough that local density bumps and seed differences are numerical warnings, not established physical modes",
      "great-circle separation between latitude-quantile particles is an endpoint-span summary, not a traced central-arc integral",
    ],
    outputs: {
      [path.basename(svgPath)]: sha256(Buffer.from(svg)),
      [path.basename(csvPath)]: sha256(Buffer.from(csv)),
    },
  };
  fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  process.stdout.write(
    `status=${manifest.status} svg=${svgPath} csv=${csvPath} manifest=${manifestPath}\n`,
  );
}

main();
