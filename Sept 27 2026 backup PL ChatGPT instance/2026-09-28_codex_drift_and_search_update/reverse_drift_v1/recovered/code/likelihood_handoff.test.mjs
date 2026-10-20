import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { buildLikelihoodHandoff } from "./build_likelihood_handoff.mjs";

const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = path.join(bundle, "outputs");
const handoffDir = path.join(outputDir, "likelihood-handoff");
const schemaId = "pleiades-conditional-source-surface/1.0.0";
const components = ["bran2016", "oscar_v2_final", "glorys12_waverys"];
const mixtureId = "equal_transport_family_model_average";

test("handoff regenerates byte-identically and all artifact hashes match", async function () {
  const rebuilt = await buildLikelihoodHandoff({ bundle, outputDir, checkOnly: true });
  const manifest = await readJson(path.join(handoffDir, "manifest.json"));
  assert.deepEqual(rebuilt, manifest);
  assert.equal(manifest.schema_id, schemaId);
  for (const artifact of manifest.artifacts) {
    const filename = path.join(handoffDir, artifact.path);
    assert.equal((await stat(filename)).size, artifact.bytes, artifact.path + " bytes");
    assert.equal(await sha256File(filename), artifact.sha256, artifact.path + " SHA-256");
  }
  for (const source of Object.values(manifest.provenance.source_files)) {
    assert.equal(await sha256File(path.join(bundle, source.path)), source.sha256, source.path + " source hash");
  }
  assert.equal(
    await readFile(path.join(handoffDir, "README.md"), "utf8"),
    await readFile(path.join(bundle, "likelihood-handoff.md"), "utf8")
  );
});

test("one schema and one quadrature grid serve all four surfaces", async function () {
  const schema = await readJson(path.join(handoffDir, "likelihood-surface-schema-v1.json"));
  const manifest = await readJson(path.join(handoffDir, "manifest.json"));
  const grid = parseCsv(await readFile(path.join(handoffDir, "grid.csv"), "utf8"));
  const surfaces = parseCsv(await readFile(path.join(handoffDir, "surfaces.csv"), "utf8"));
  assert.equal(schema.$id, schemaId);
  assert.equal(grid.length, 5289);
  assert.equal(surfaces.length, 4 * grid.length);
  assert.equal(new Set(grid.map(function (row) { return row.cell_id; })).size, grid.length);
  assert.deepEqual(
    Array.from(new Set(surfaces.map(function (row) { return row.surface_id; }))),
    [...components, mixtureId]
  );
  assert(grid.every(function (row) {
    return row.schema_version === schemaId && row.grid_id === manifest.grid.grid_id;
  }));
  const gridIds = new Set(grid.map(function (row) { return row.cell_id; }));
  assert(surfaces.every(function (row) {
    return row.schema_version === schemaId && gridIds.has(row.cell_id);
  }));
  assert.equal(Number(grid[0].trapezoidal_weight), 0.25);
  assert.equal(Number(grid[1].trapezoidal_weight), 0.5);
  assert.equal(Number(grid[42].trapezoidal_weight), 1);
  assert(Math.abs(grid.reduce(function (sum, row) {
    return sum + Number(row.quadrature_area_km2);
  }, 0) - manifest.grid.support_area_km2) < 1e-7);
  assert.equal(normalizedHash(grid, [
    "cell_id", "along_index", "cross_index", "along_nm", "cross_nm",
    "latitude_deg", "longitude_deg", "quadrature_area_km2", "trapezoidal_weight",
  ]), manifest.grid.normalized_grid_sha256);
});

test("component values are prior-free relative proxies and display fields conserve mass", async function () {
  const manifest = await readJson(path.join(handoffDir, "manifest.json"));
  const grid = new Map(parseCsv(await readFile(path.join(handoffDir, "grid.csv"), "utf8")).map(function (row) {
    return [row.cell_id, row];
  }));
  const allRows = parseCsv(await readFile(path.join(handoffDir, "surfaces.csv"), "utf8"));
  assert.equal(manifest.value_semantics.primary_composition_field, "log_relative_likelihood");
  assert(Math.abs(
    manifest.value_semantics.normalization_prior.density_per_km2
      * manifest.grid.support_area_km2 - 1
  ) < 1e-15);
  assert(manifest.value_semantics.normalization_prior.removal.includes("already prior-removed"));
  assert(manifest.value_semantics.normalized_probability_mass.includes("must never be multiplied"));

  for (const metadata of manifest.surfaces) {
    const rows = allRows.filter(function (row) { return row.surface_id === metadata.surface_id; });
    assert.equal(rows.length, grid.size);
    assert.equal(metadata.is_posterior_density, false);
    assert.equal(metadata.is_calibrated_evidence_likelihood, false);
    const maximumDensity = Math.max(...rows.map(function (row) {
      return Number(row.normalized_density_per_km2);
    }));
    let mass = 0;
    for (const row of rows) {
      const relative = Number(row.relative_likelihood);
      const density = Number(row.normalized_density_per_km2);
      const probabilityMass = Number(row.normalized_probability_mass);
      const area = Number(grid.get(row.cell_id).quadrature_area_km2);
      assert(relative >= 0 && relative <= 1);
      assert(close(relative, density / maximumDensity, 1e-14), metadata.surface_id + " prior removal");
      assert(close(probabilityMass, density * area, 1e-14), metadata.surface_id + " area mass");
      if (relative === 0) assert.equal(row.log_relative_likelihood, "");
      else assert(close(Number(row.log_relative_likelihood), Math.log(relative), 1e-14));
      mass += probabilityMass;
    }
    assert(Math.abs(mass - 1) < 1e-10, metadata.surface_id + " mass");
    assert.equal(Math.max(...rows.map(function (row) {
      return Number(row.relative_likelihood);
    })), 1);
    assert.equal(
      normalizedHash(rows, ["cell_id", "relative_likelihood"]),
      metadata.normalized_relative_likelihood_sha256
    );
    assert.equal(
      normalizedHash(rows, ["cell_id", "normalized_density_per_km2"]),
      metadata.normalized_density_sha256
    );
    assert.equal(
      normalizedHash(rows, ["cell_id", "normalized_probability_mass"]),
      metadata.normalized_probability_mass_sha256
    );
  }
});

test("equal-prior surface is exactly the declared density mixture and never a fourth likelihood", async function () {
  const manifest = await readJson(path.join(handoffDir, "manifest.json"));
  const rows = parseCsv(await readFile(path.join(handoffDir, "surfaces.csv"), "utf8"));
  const bySurface = new Map([...components, mixtureId].map(function (id) {
    return [id, new Map(rows.filter(function (row) {
      return row.surface_id === id;
    }).map(function (row) { return [row.cell_id, row]; }))];
  }));
  const mixtureMetadata = manifest.surfaces.find(function (surface) {
    return surface.surface_id === mixtureId;
  });
  assert.equal(mixtureMetadata.surface_class, "uncalibrated_equal_prior_sensitivity_mixture");
  assert(mixtureMetadata.primary_value_kind.includes("not_evidence_likelihood"));
  assert(mixtureMetadata.conditional_use_status.includes("never use alongside"));
  assert(manifest.family_policy.mixture_calibration.includes("not calibrated"));
  assert.deepEqual(manifest.family_policy.alternatives_not_independent_evidence, components);
  assert(manifest.family_policy.forbidden_choice.includes("Never multiply"));

  for (const [cellId, mixture] of bySurface.get(mixtureId)) {
    const expectedDensity = components.reduce(function (sum, id) {
      return sum + Number(bySurface.get(id).get(cellId).normalized_density_per_km2) / 3;
    }, 0);
    const expectedMass = components.reduce(function (sum, id) {
      return sum + Number(bySurface.get(id).get(cellId).normalized_probability_mass) / 3;
    }, 0);
    assert(close(Number(mixture.normalized_density_per_km2), expectedDensity, 1e-14));
    assert(close(Number(mixture.normalized_probability_mass), expectedMass, 1e-14));
  }
});

test("source hypothesis, support boundary, blockers, and comparison formats are explicit", async function () {
  const manifest = await readJson(path.join(handoffDir, "manifest.json"));
  const citationLedger = await readFile(path.join(bundle, "data/citation-ledger.md"), "utf8");
  const objects = parseCsv(await readFile(path.join(bundle, "data/pleiades-rating5-objects.csv"), "utf8"));
  const html = await readFile(path.join(handoffDir, "comparison.html"), "utf8");
  const publicationPng = await readFile(path.join(outputDir, "pleiades-forward-impact-density.png"));
  const publicationSvg = await readFile(path.join(outputDir, "pleiades-forward-impact-density.svg"));
  const packagedPng = await readFile(path.join(handoffDir, "comparison.png"));
  const packagedSvg = await readFile(path.join(handoffDir, "comparison.svg"));
  const publicationSvgText = publicationSvg.toString("utf8");
  assert.equal(objects.length, 12);
  assert.equal(manifest.conditional_source_hypothesis.source_time_utc, "2014-03-08T00:19:00Z");
  assert.equal(manifest.conditional_source_hypothesis.observation_time_utc, "2014-03-23T04:00:00Z");
  assert(manifest.conditional_source_hypothesis.identity_model.includes("Exactly one"));
  assert(manifest.conditional_source_hypothesis.identity_model.includes("all twelve"));
  assert(manifest.conditional_source_hypothesis.implementation_detail.includes("No object identity is randomly drawn"));
  assert(manifest.conditional_source_hypothesis.equivalence_limit.includes("not equivalent"));
  assert(citationLedger.includes("postulate that at least some"));
  assert(citationLedger.includes("cannot determine whether they are aircraft debris"));
  assert(manifest.grid.support_rule.includes("truncation boundary"));
  assert(manifest.grid.interpolation_rule.includes("do not extrapolate"));
  assert(manifest.grid.zero_rule.includes("underflow"));
  assert(manifest.blockers_to_calibrated_conditional_likelihood.length >= 6);
  assert(manifest.family_policy.core_likelihood_rule.includes("Do not average"));
  assert.equal(manifest.browser_comparison.png, "comparison.png");
  assert.equal(manifest.browser_comparison.svg, "comparison.svg");
  assert.deepEqual(packagedPng, publicationPng);
  assert.deepEqual(packagedSvg, publicationSvg);
  assert.deepEqual(Array.from(packagedPng.subarray(0, 8)), [137, 80, 78, 71, 13, 10, 26, 10]);
  assert.equal(packagedPng.readUInt32BE(16), 4000);
  assert.equal(packagedPng.readUInt32BE(20), 1680);
  assert(publicationSvgText.includes("viewBox=\"0 0 1440 604.8\""));
  assert(html.includes("<svg"));
  assert(html.includes("Mixture not calibrated"));
  assert(html.includes("never multiply or jointly include"));
  assert(html.includes(publicationSvgText.slice(publicationSvgText.indexOf("<svg"), publicationSvgText.indexOf("<svg") + 500)));
});

async function readJson(filename) {
  return JSON.parse(await readFile(filename, "utf8"));
}

async function sha256File(filename) {
  return createHash("sha256").update(await readFile(filename)).digest("hex");
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const columns = lines.shift().split(",");
  return lines.map(function (line) {
    const values = line.split(",");
    assert.equal(values.length, columns.length);
    return Object.fromEntries(columns.map(function (column, index) {
      return [column, values[index]];
    }));
  });
}

function normalizedHash(rows, columns) {
  const hash = createHash("sha256");
  for (const row of rows) {
    for (const column of columns) {
      hash.update(column).update("\0");
      const value = row[column];
      if (columns.includes(column) && column !== "cell_id") {
        const number = Number(value);
        assert(Number.isFinite(number));
        hash.update((Object.is(number, -0) ? 0 : number).toExponential(17));
      } else {
        hash.update(String(value));
      }
      hash.update("\0");
    }
    hash.update("\n");
  }
  return hash.digest("hex");
}

function close(first, second, tolerance) {
  return Math.abs(first - second) <= tolerance * Math.max(1, Math.abs(first), Math.abs(second));
}
