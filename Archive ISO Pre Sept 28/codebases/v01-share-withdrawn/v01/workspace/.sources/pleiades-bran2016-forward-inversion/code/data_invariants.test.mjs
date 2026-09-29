import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { VectorField, buildSourceGrid, readObjects } from "./transport_core.mjs";

const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(bundle, "data");
const outputDir = path.join(bundle, "outputs");
const config = await readJson(path.join(dataDir, "config.json"));
const inputManifest = await readJson(path.join(dataDir, "input-manifest.json"));

test("all pinned source-file and grid hashes match", async function () {
  for (const source of inputManifest.source_files) {
    const filename = path.join(bundle, source.path);
    const information = await stat(filename);
    assert.equal(information.size, source.bytes, source.path + " byte count");
    assert.equal(await sha256File(filename), source.sha256, source.path + " SHA-256");
  }
  for (const dataset of inputManifest.datasets.filter(function (item) {
    return !item.status || item.status === "retrieved";
  })) {
    assert.deepEqual(dataset.dimension_order, ["time", "latitude", "longitude", "component"]);
    assert.deepEqual(dataset.variable_order, ["u_east_m_s", "v_north_m_s"]);
    assert.equal(dataset.units.replace("/", " "), "m s-1");
    assert.equal(dataset.value_count, dataset.shape.reduce(function (product, value) { return product * value; }, 1));
    const filename = path.join(dataDir, dataset.binary_file);
    assert.equal((await stat(filename)).size, dataset.value_count * 4);
    assert.equal(await sha256File(filename), dataset.sha256);
    if (dataset.source_family === "OSCAR v2 Final") {
      assert.equal(dataset.missing_vector_count, 64, "OSCAR permanent ocean-mask vectors");
      const bytes = await readFile(filename);
      const [, latitudeCount, longitudeCount] = dataset.shape;
      const missingLocations = new Set();
      for (let vector = 0; vector < dataset.value_count / 2; vector += 1) {
        const u = bytes.readFloatLE(vector * 8);
        const v = bytes.readFloatLE(vector * 8 + 4);
        if (Number.isFinite(u) && Number.isFinite(v)) continue;
        const spatial = vector % (latitudeCount * longitudeCount);
        const latitudeIndex = Math.floor(spatial / longitudeCount);
        const longitudeIndex = spatial % longitudeCount;
        missingLocations.add(
          (dataset.latitude.start_deg + latitudeIndex * dataset.latitude.step_deg)
          + ","
          + (dataset.longitude.start_deg + longitudeIndex * dataset.longitude.step_deg)
        );
      }
      assert.deepEqual(Array.from(missingLocations).sort(), [
        "-27.25,81.25",
        "-27.25,81.5",
        "-27.5,81.25",
        "-27.5,81.5",
      ]);
    } else {
      assert.equal(dataset.missing_vector_count, 0);
    }
  }
});

test("current, Stokes, and wind fields have the declared ordering and plausible values", async function () {
  const bran = await VectorField.load(path.join(dataDir, "bran2016-surface-currents-20140308-23.manifest.json"), dataDir);
  const glorys = await VectorField.load(path.join(dataDir, "cmems-glorys12-surface-currents-20140308-24.manifest.json"), dataDir);
  const stokes = await VectorField.load(path.join(dataDir, "cmems-waverys-surface-stokes-20140308-23.manifest.json"), dataDir);
  const wind = await VectorField.load(path.join(dataDir, "ncep-ncar-r1-10m-wind-20140308-23.manifest.json"), dataDir);
  const oscarManifest = await readJson(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"));
  const oscar = oscarManifest.status === "retrieved"
    ? await VectorField.load(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"), dataDir)
    : null;
  for (let day = 0; day < 16; day += 1) {
    const epoch = Date.parse("2014-03-08T12:00:00Z") + day * 86400000;
    const oceans = [bran.sample(epoch, -35.5, 92.0), glorys.sample(epoch, -35.5, 92.0)];
    if (oscar) oceans.push(oscar.sample(epoch, -35.5, 92.0));
    const wave = stokes.sample(epoch, -35.5, 92.0);
    const atmosphere = wind.sample(epoch, -35.5, 92.0);
    for (const ocean of oceans) {
      assert(ocean && ocean.every(Number.isFinite));
      assert(Math.hypot(ocean[0], ocean[1]) < 3, "ocean speed must be physically plausible");
    }
    assert(wave && wave.every(Number.isFinite));
    assert(Math.hypot(wave[0], wave[1]) < 3, "Stokes speed must be physically plausible");
    assert(atmosphere && atmosphere.every(Number.isFinite));
    assert(Math.hypot(atmosphere[0], atmosphere[1]) < 60, "10 m wind speed must be physically plausible");
  }
});

test("declared source support and object identity sets are invariant", async function () {
  const objects = readObjects(await readFile(path.join(dataDir, "pleiades-rating5-objects.csv"), "utf8"));
  assert.equal(objects.filter(function (item) { return item.sets.has("all_rating5"); }).length, 12);
  assert.equal(objects.filter(function (item) { return item.sets.has("morphology_shortlist5"); }).length, 5);
  assert.equal(new Set(objects.map(function (item) { return item.id; })).size, 12);
  const geojson = await readJson(path.join(dataDir, "seventh_arc_fl400.geojson"));
  const grid = buildSourceGrid(geojson, config);
  assert.equal(grid.crossCount, 41);
  assert.equal(grid.alongCount, 129);
  assert.equal(grid.cells.length, 5289);
  assert.equal(new Set(grid.cells.map(function (cell) { return cell.id; })).size, grid.cells.length);
  assert(Math.abs(grid.crossOffsets[0] + 100) < 1e-12);
  assert(Math.abs(grid.crossOffsets.at(-1) - 100) < 1e-12);
  const currentManifests = [
    "bran2016-surface-currents-20140308-23.manifest.json",
    "cmems-glorys12-surface-currents-20140308-24.manifest.json",
    "cmems-waverys-surface-stokes-20140308-23.manifest.json",
  ];
  const oscarManifest = await readJson(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"));
  if (oscarManifest.status === "retrieved") currentManifests.push("oscar-v2-final-20140308-23.manifest.json");
  for (const manifest of currentManifests) {
    const current = await VectorField.load(path.join(dataDir, manifest), dataDir);
    for (const cell of grid.cells) {
      assert(
        current.sample(Date.parse(config.start_utc), cell.latitude, cell.longitude),
        cell.id + " must lie in " + current.manifest.source_family + " valid ocean support"
      );
    }
  }
});

test("ensemble outputs conserve probability and retain valid trajectories", async function () {
  const summary = await readJson(path.join(outputDir, "summary.json"));
  assert.equal(summary.identity_conclusion, "unknown");
  assert.equal(summary.source_grid.cells, 5289);
  assert.deepEqual(summary.current_models.map(function (model) { return model.id; }), [
    "bran2016",
    "oscar_v2_final",
    "glorys12_waverys",
  ]);
  assert.equal(summary.current_family_comparisons.length, 3);
  assert(summary.current_family_comparisons.every(function (entry) {
    return Number.isFinite(entry.total_variation)
      && Number.isFinite(entry.mode_separation_km)
      && Number.isFinite(entry.mean_separation_km);
  }));
  const density = parseCsv(await readFile(path.join(outputDir, "conditional-impact-density.csv"), "utf8"));
  for (const model of summary.current_models.map(function (item) { return item.id; })) {
    const rows = density.filter(function (row) { return row.current_model === model; });
    assert.equal(rows.length, summary.source_grid.cells);
    const total = rows.reduce(function (sum, row) { return sum + Number(row.probabilityMass); }, 0);
    assert(Math.abs(total - 1) < 1e-10, model + " probability mass");
    for (const row of rows) {
      if (row.in_hpd50 === "true") assert.equal(row.in_hpd90, "true");
      if (row.in_hpd90 === "true") assert.equal(row.in_hpd95, "true");
      assert(Number(row.densityPerKm2) >= 0);
    }
  }

  const averaged = parseCsv(await readFile(path.join(outputDir, "model-averaged-impact-density.csv"), "utf8"));
  assert.equal(averaged.length, summary.source_grid.cells);
  assert.equal(summary.model_average.id, "equal_transport_family_model_average");
  assert.deepEqual(summary.model_average.component_weights, [
    { id: "bran2016", weight: 1 / 3 },
    { id: "oscar_v2_final", weight: 1 / 3 },
    { id: "glorys12_waverys", weight: 1 / 3 },
  ]);
  assert(Math.abs(averaged.reduce(function (sum, row) {
    return sum + Number(row.probabilityMass);
  }, 0) - 1) < 1e-10, "model-average probability mass");
  const componentRows = new Map(summary.model_average.component_weights.map(function (component) {
    return [component.id, new Map(density.filter(function (row) {
      return row.current_model === component.id;
    }).map(function (row) { return [row.id, row]; }))];
  }));
  for (const row of averaged) {
    const expected = summary.model_average.component_weights.reduce(function (sum, component) {
      return sum + component.weight * Number(componentRows.get(component.id).get(row.id).probabilityMass);
    }, 0);
    assert(Math.abs(Number(row.probabilityMass) - expected) < 1e-15, row.id + " model average");
  }
  const cardinality = parseCsv(await readFile(path.join(outputDir, "identity-cardinality-sensitivity.csv"), "utf8"));
  assert.equal(cardinality.length, 5);
  assert(cardinality.every(function (row) {
    return Math.abs(Number(row.marginal_weight_per_object) - 0.2) < 1e-15
      && Number(row.pdf_total_variation_from_exactly_one) === 0;
  }));
  assert(summary.identity_cardinality_sensitivity.maximum_absolute_difference_from_equal_weight < 1e-15);

  const primary = parseCsv(await readFile(path.join(outputDir, "forward-ensemble-primary-seeds.csv"), "utf8"));
  const expectedPrimary = config.particles_per_windage_primary * config.windage_factors.length;
  assert(
    primary.every(function (row) { return Number(row.valid_particles) === expectedPrimary; }),
    "every primary trajectory must remain in-domain"
  );
  const sensitivity = parseCsv(await readFile(path.join(outputDir, "forward-ensemble-diffusion-sensitivity.csv"), "utf8"));
  const expectedSensitivity = config.particles_per_windage_sensitivity * config.windage_factors.length;
  assert(
    sensitivity.every(function (row) { return Number(row.valid_particles) === expectedSensitivity; }),
    "every sensitivity trajectory must remain in-domain"
  );
});

test("rendered and tabular output hashes match the output manifest", async function () {
  const manifest = await readJson(path.join(outputDir, "manifest.json"));
  const summary = await readJson(path.join(outputDir, "summary.json"));
  const combined = createHash("sha256");
  for (const implementationFile of summary.implementation.files) {
    const filename = path.join(bundle, implementationFile.path);
    const digest = await sha256File(filename);
    assert.equal(digest, implementationFile.sha256, implementationFile.path + " implementation hash");
    combined.update(implementationFile.path).update("\0").update(digest).update("\n");
  }
  assert.equal(combined.digest("hex"), summary.implementation.combined_sha256);
  assert.equal(await sha256File(path.join(dataDir, "input-manifest.json")), summary.implementation.input_manifest_sha256);
  assert.deepEqual(manifest.implementation, summary.implementation);
  for (const output of manifest.outputs) {
    const filename = path.join(outputDir, output.path);
    assert.equal((await stat(filename)).size, output.bytes, output.path + " byte count");
    assert.equal(await sha256File(filename), output.sha256, output.path + " SHA-256");
  }
  const pdf = await readFile(path.join(outputDir, "pleiades-forward-impact-density.pdf"));
  const png = await readFile(path.join(outputDir, "pleiades-forward-impact-density.png"));
  const svg = await readFile(path.join(outputDir, "pleiades-forward-impact-density.svg"), "utf8");
  const pdfText = pdf.toString("latin1");
  assert.equal(pdf.subarray(0, 8).toString("latin1"), "%PDF-1.4");
  assert(pdfText.includes("/MediaBox [ 0 0 1440 604.8 ]"));
  assert(pdfText.includes("/Subtype /Type0"), "PDF must embed vector text fonts");
  const startXref = pdfText.match(/startxref\n(\d+)\n%%EOF/);
  assert(startXref, "PDF must have a terminal startxref");
  assert.equal(pdfText.slice(Number(startXref[1]), Number(startXref[1]) + 4), "xref");
  assert.deepEqual(Array.from(png.subarray(0, 8)), [137, 80, 78, 71, 13, 10, 26, 10]);
  assert.equal(png.readUInt32BE(16), 4000);
  assert.equal(png.readUInt32BE(20), 1680);
  assert(svg.includes("<title>Pléiades forward-transport conditional source compatibility</title>"));
  assert(svg.includes('viewBox="0 0 1440 604.8"'));
  assert(svg.includes("font-family: 'DejaVu Sans'"), "SVG text must remain real font text");
  assert(svg.includes("#54278f"), "50% house-style HPD colour");
  assert(svg.includes("#9e9ac8"), "90% house-style HPD colour");
  assert(svg.includes("#dadaeb"), "95% house-style HPD colour");
  assert(svg.includes(">50% HPD</text>"));
  assert(svg.includes(">seventh BTO arc</text>"));
  assert(svg.includes(">90.0</text>"), "tight west bound");
  assert(svg.includes(">94.0</text>"), "tight east bound");
  assert(svg.includes("no transverse display width was added"));
  assert(svg.includes("never multiplied as independent evidence"));
  assert(svg.includes(">Equal-prior three-family model average</text>"));
});

test("accessible paper section preserves key methods and conditional interpretation", async function () {
  const markdown = await readFile(path.join(bundle, "paper-section.md"), "utf8");
  const latex = await readFile(path.join(bundle, "paper-section.tex"), "utf8");
  const bibliography = await readFile(path.join(bundle, "paper-references.bib"), "utf8");
  const narrative = markdown.split("## References")[0]
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/^\|.*$/gm, "")
    .replace(/^#.*$/gm, "");
  const words = narrative.match(/[A-Za-z0-9±%°–—-]+(?:[’'][A-Za-z0-9]+)*/g) ?? [];
  assert(words.length >= 500 && words.length <= 650, "requested 500–650-word narrative");
  const plain = markdown.replace(/\s+/g, " ");
  assert(!/\b(?:we|our)\b/i.test(narrative), "paper section must use impersonal/passive academic voice");
  assert(!/\[[0-9]+\]/.test(narrative), "JON in-text citations must be unnumbered author-date");
  assert(latex.includes("\\operatorname{IoU}"), "LaTeX loss equation");
  assert(!bibliography.includes("and others"), "JON reference list requires full author details");
  assert(bibliography.includes("EP174155"), "correct Part III report number");
  assert(bibliography.includes("10.4225/08/599344b9beead"), "correct Part III DOI");
  assert(!bibliography.includes("EP172633"), "Part II identifier must not label Part III");
  for (const phrase of [
    "This did not identify aircraft debris",
    "not because they resembled aircraft",
    "not an identity probability",
    "not asserted weak points",
    "documented section 47",
    "whole shell ranked lowest for none",
    "clean-sheet ensemble",
    "rather than drawing one object",
    "neither independent-evidence multiplication nor a calibrated posterior",
    "none of 168 original flooding states matched",
    "All required an absent engine",
    "not Boeing tank bays",
    "conditional image-debris hypothesis",
    "GLORYS12 currents plus WAVERYS",
    "equal-prior mixture",
  ]) assert(plain.includes(phrase), phrase);
  for (const key of [
    "aaib2010ba38",
    "boeing2024acap",
    "copernicus2023glorys12",
    "copernicus2024waverys",
    "dohan2021oscar",
    "griffin2017drift",
    "hapag2016container",
    "iotc2023observer",
    "kalnay1996reanalysis",
    "lebreton2018plastic",
    "minchin2017pleiades",
    "murphy2013structures",
    "motmalaysia2018",
    "ntsb2014fueltank",
  ]) {
    assert(latex.includes(key), key + " LaTeX citation");
    assert(bibliography.includes("{" + key + ","), key + " BibTeX entry");
  }
});

async function readJson(filename) {
  return JSON.parse(await readFile(filename, "utf8"));
}

async function sha256File(filename) {
  return createHash("sha256").update(await readFile(filename)).digest("hex");
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.map(function (line) {
    const values = line.split(",");
    return Object.fromEntries(header.map(function (name, index) { return [name, values[index]]; }));
  });
}

