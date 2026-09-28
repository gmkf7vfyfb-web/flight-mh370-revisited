#!/usr/bin/env node

import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SCHEMA_ID = "pleiades-conditional-source-surface/1.0.0";
const GRID_ID = "seventh_arc_fl400_32s_39s_plusminus100nm_5nm";
const COMPONENT_IDS = ["bran2016", "oscar_v2_final", "glorys12_waverys"];
const MIXTURE_ID = "equal_transport_family_model_average";

export async function buildLikelihoodHandoff(options = {}) {
  const bundle = options.bundle || path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const outputDir = options.outputDir || path.join(bundle, "outputs");
  const handoffDir = path.join(outputDir, "likelihood-handoff");
  const checkOnly = options.checkOnly || false;
  const paths = {
    components: path.join(outputDir, "conditional-impact-density.csv"),
    mixture: path.join(outputDir, "model-averaged-impact-density.csv"),
    summary: path.join(outputDir, "summary.json"),
    publication_png: path.join(outputDir, "pleiades-forward-impact-density.png"),
    publication_svg: path.join(outputDir, "pleiades-forward-impact-density.svg"),
    configuration: path.join(bundle, "data/config.json"),
    objects: path.join(bundle, "data/pleiades-rating5-objects.csv"),
    seventh_arc: path.join(bundle, "data/seventh_arc_fl400.geojson"),
    input_manifest: path.join(bundle, "data/input-manifest.json"),
    contract: path.join(bundle, "likelihood-handoff.md"),
    builder: fileURLToPath(import.meta.url),
    invariant_test: path.join(bundle, "code/likelihood_handoff.test.mjs"),
  };
  const sourceBytes = {};
  for (const [name, filename] of Object.entries(paths)) {
    sourceBytes[name] = await readFile(filename);
  }
  const text = function (name) { return sourceBytes[name].toString("utf8"); };
  const componentRows = parseCsv(text("components"));
  const mixtureRows = parseCsv(text("mixture"));
  const summary = JSON.parse(text("summary"));
  const config = JSON.parse(text("configuration"));
  const grid = buildGrid(componentRows, mixtureRows, summary, config);
  const surfaces = buildSurfaces(grid, mixtureRows, summary);

  const generated = {
    "README.md": sourceBytes.contract,
    "comparison.html": comparisonHtml(text("publication_svg"), summary, surfaces.metadata),
    "comparison.png": sourceBytes.publication_png,
    "comparison.svg": sourceBytes.publication_svg,
    "grid.csv": rowsToCsv(grid.rows),
    "likelihood-surface-schema-v1.json": stableJson(schemaDocument()),
    "surfaces.csv": rowsToCsv(surfaces.rows),
  };
  const manifest = await manifestDocument({
    bundle,
    paths,
    sourceBytes,
    summary,
    config,
    grid,
    surfaceMetadata: surfaces.metadata,
    generated,
  });
  const files = { ...generated, "manifest.json": stableJson(manifest) };

  if (checkOnly) {
    for (const [name, expected] of Object.entries(files)) {
      const actual = await readFile(path.join(handoffDir, name));
      const expectedBytes = Buffer.isBuffer(expected) ? expected : Buffer.from(expected);
      assert(actual.equals(expectedBytes), name + " is not the deterministic builder output");
    }
  } else {
    await mkdir(handoffDir, { recursive: true });
    for (const [name, contents] of Object.entries(files)) {
      await writeFile(path.join(handoffDir, name), contents);
    }
  }
  return manifest;
}

function buildGrid(componentRows, mixtureRows, summary, config) {
  assert.deepEqual(
    Array.from(new Set(componentRows.map(function (row) { return row.current_model; }))),
    COMPONENT_IDS,
    "unexpected component family order or identity"
  );
  const byModel = new Map(COMPONENT_IDS.map(function (id) {
    return [id, componentRows.filter(function (row) { return row.current_model === id; })];
  }));
  const reference = byModel.get(COMPONENT_IDS[0]);
  assert.equal(reference.length, summary.source_grid.cells);
  assert.equal(mixtureRows.length, reference.length);
  for (const id of COMPONENT_IDS) assert.equal(byModel.get(id).length, reference.length);

  const gridColumns = [
    "id", "alongIndex", "crossIndex", "alongNm", "crossNm",
    "latitude", "longitude", "cellAreaKm2",
  ];
  for (let index = 0; index < reference.length; index += 1) {
    for (const id of COMPONENT_IDS.slice(1)) {
      for (const column of gridColumns) {
        assert.equal(byModel.get(id)[index][column], reference[index][column], id + " grid " + column);
      }
    }
    for (const column of gridColumns) {
      assert.equal(mixtureRows[index][column], reference[index][column], "mixture grid " + column);
    }
  }

  const nominalArea = config.arc_spacing_nm * config.cross_arc_spacing_nm * 1.852 ** 2;
  const rows = reference.map(function (row) {
    const area = finiteNumber(row.cellAreaKm2, row.id + " quadrature area");
    return {
      schema_version: SCHEMA_ID,
      grid_id: GRID_ID,
      cell_id: row.id,
      along_index: integerNumber(row.alongIndex, row.id + " along index"),
      cross_index: integerNumber(row.crossIndex, row.id + " cross index"),
      along_nm: finiteNumber(row.alongNm, row.id + " along NM"),
      cross_nm: finiteNumber(row.crossNm, row.id + " cross NM"),
      latitude_deg: finiteNumber(row.latitude, row.id + " latitude"),
      longitude_deg: finiteNumber(row.longitude, row.id + " longitude"),
      quadrature_area_km2: area,
      trapezoidal_weight: area / nominalArea,
    };
  });
  const supportArea = rows.reduce(function (sum, row) {
    return sum + row.quadrature_area_km2;
  }, 0);
  assert(Math.abs(supportArea - summary.source_grid.support_area_km2) < 1e-7);
  assert.equal(new Set(rows.map(function (row) { return row.cell_id; })).size, rows.length);
  assert.equal(Math.max(...rows.map(function (row) { return row.along_index; })) + 1, summary.source_grid.along_cells);
  assert.equal(Math.max(...rows.map(function (row) { return row.cross_index; })) + 1, summary.source_grid.cross_cells);

  return {
    rows,
    byModel,
    supportArea,
    nominalArea,
    normalizedSha256: normalizedHash(rows, [
      "cell_id", "along_index", "cross_index", "along_nm", "cross_nm",
      "latitude_deg", "longitude_deg", "quadrature_area_km2", "trapezoidal_weight",
    ]),
  };
}

function buildSurfaces(grid, mixtureRows, summary) {
  const outputRows = [];
  const metadata = [];
  for (const id of COMPONENT_IDS) {
    const rows = grid.byModel.get(id);
    const raw = rows.map(function (row) {
      return nonnegativeNumber(row.likelihood, id + " " + row.id + " score");
    });
    const maximum = Math.max(...raw);
    const integral = rows.reduce(function (sum, row, index) {
      return sum + raw[index] * finiteNumber(row.cellAreaKm2, id + " " + row.id + " area");
    }, 0);
    assert(maximum > 0 && integral > 0);

    const normalized = rows.map(function (row, index) {
      const density = nonnegativeNumber(row.densityPerKm2, id + " " + row.id + " density");
      const mass = nonnegativeNumber(row.probabilityMass, id + " " + row.id + " mass");
      const area = grid.rows[index].quadrature_area_km2;
      assert(close(density, raw[index] / integral, 5e-15), id + " " + row.id + " density normalization");
      assert(close(mass, density * area, 5e-15), id + " " + row.id + " quadrature mass");
      return surfaceRecord(id, row.id, raw[index] / maximum, density, mass);
    });
    validateSurface(id, normalized);
    outputRows.push(...normalized);

    const model = summary.current_models.find(function (item) { return item.id === id; });
    metadata.push({
      surface_id: id,
      label: model.label,
      surface_class: "transport_family_component",
      primary_value_kind: "relative_conditional_endpoint_compatibility_likelihood_proxy",
      is_posterior_density: false,
      is_calibrated_evidence_likelihood: false,
      conditional_use_status: "Usable only as an explicitly enabled conditional proxy; calibrated-likelihood use is blocked.",
      prior_removal_status: "The relative and log-relative fields already have the constant uniform normalization prior removed up to an irrelevant positive scale.",
      current_input_sha256: model.current_input_sha256,
      stokes_input_sha256: model.stokes_input_sha256,
      velocity_terms: model.velocity_terms,
      raw_score_maximum: maximum,
      raw_score_area_integral_km2: integral,
      normalized_relative_likelihood_sha256: normalizedHash(normalized, ["cell_id", "relative_likelihood"]),
      normalized_density_sha256: normalizedHash(normalized, ["cell_id", "normalized_density_per_km2"]),
      normalized_probability_mass_sha256: normalizedHash(normalized, ["cell_id", "normalized_probability_mass"]),
      exact_numeric_zero_nodes: normalized.filter(function (row) { return row.relative_likelihood === 0; }).length,
      mode: summary.summaries[id].primary.mode,
      hpd90_area_km2: summary.summaries[id].primary.hpd["0.9"].areaKm2,
    });
  }

  const maximumDensity = Math.max(...mixtureRows.map(function (row) {
    return nonnegativeNumber(row.densityPerKm2, "mixture density");
  }));
  const mixtureOutput = mixtureRows.map(function (row, index) {
    const density = nonnegativeNumber(row.densityPerKm2, "mixture " + row.id + " density");
    const mass = nonnegativeNumber(row.probabilityMass, "mixture " + row.id + " mass");
    const expectedDensity = COMPONENT_IDS.reduce(function (sum, id) {
      return sum + Number(grid.byModel.get(id)[index].densityPerKm2) / COMPONENT_IDS.length;
    }, 0);
    const expectedMass = COMPONENT_IDS.reduce(function (sum, id) {
      return sum + Number(grid.byModel.get(id)[index].probabilityMass) / COMPONENT_IDS.length;
    }, 0);
    assert(close(density, expectedDensity, 5e-15), row.id + " mixture density");
    assert(close(mass, expectedMass, 5e-15), row.id + " mixture mass");
    return surfaceRecord(MIXTURE_ID, row.id, density / maximumDensity, density, mass);
  });
  validateSurface(MIXTURE_ID, mixtureOutput);
  outputRows.push(...mixtureOutput);
  metadata.push({
    surface_id: MIXTURE_ID,
    label: "Equal-prior three-family sensitivity mixture (uncalibrated)",
    surface_class: "uncalibrated_equal_prior_sensitivity_mixture",
    primary_value_kind: "relative_sensitivity_density_shape_not_evidence_likelihood",
    is_posterior_density: false,
    is_calibrated_evidence_likelihood: false,
    conditional_use_status: "Sensitivity aggregate only; never use alongside its components or present as a calibrated family posterior.",
    prior_removal_status: "Division by the constant uniform normalization prior changes only scale but does not turn this density mixture into a calibrated evidence likelihood.",
    component_weights: COMPONENT_IDS.map(function (surfaceId) {
      return { surface_id: surfaceId, weight: 1 / COMPONENT_IDS.length };
    }),
    normalized_relative_likelihood_sha256: normalizedHash(mixtureOutput, ["cell_id", "relative_likelihood"]),
    normalized_density_sha256: normalizedHash(mixtureOutput, ["cell_id", "normalized_density_per_km2"]),
    normalized_probability_mass_sha256: normalizedHash(mixtureOutput, ["cell_id", "normalized_probability_mass"]),
    exact_numeric_zero_nodes: mixtureOutput.filter(function (row) { return row.relative_likelihood === 0; }).length,
    mode: summary.model_average.primary.mode,
    hpd90_area_km2: summary.model_average.primary.hpd["0.9"].areaKm2,
  });
  return { rows: outputRows, metadata };
}

function surfaceRecord(surfaceId, cellId, relative, density, mass) {
  return {
    schema_version: SCHEMA_ID,
    surface_id: surfaceId,
    cell_id: cellId,
    relative_likelihood: relative,
    log_relative_likelihood: relative > 0 ? Math.log(relative) : null,
    normalized_density_per_km2: density,
    normalized_probability_mass: mass,
  };
}

function validateSurface(id, rows) {
  assert.equal(rows.length, 5289, id + " row count");
  assert(Math.abs(rows.reduce(function (sum, row) {
    return sum + row.normalized_probability_mass;
  }, 0) - 1) < 1e-10, id + " mass");
  assert.equal(Math.max(...rows.map(function (row) { return row.relative_likelihood; })), 1);
  assert(rows.every(function (row) {
    return row.relative_likelihood >= 0 && row.relative_likelihood <= 1;
  }));
}

async function manifestDocument(context) {
  const sourceFiles = {};
  for (const [name, filename] of Object.entries(context.paths)) {
    sourceFiles[name] = {
      path: path.relative(context.bundle, filename),
      sha256: sha256(context.sourceBytes[name]),
    };
  }
  return {
    schema_id: SCHEMA_ID,
    handoff_status: "source_only_conditional_proxy_handoff",
    identity_conclusion: "unknown",
    scientific_claim_boundary: "No surface identifies any image object as MH370 debris or provides an unconditional crash-location posterior.",
    conditional_source_hypothesis: {
      hypothesis_id: "H_pleiades_rating5_exactly_one_equal_identity",
      source_time_utc: context.config.start_utc,
      observation_time_utc: context.config.observation_utc,
      source_support: "Declared FL400 seventh-arc strip from 32 degrees S to 39 degrees S and -100 to +100 NM cross-arc.",
      identity_model: "Exactly one latent associated object, uniformly weighted across all twelve Geoscience Australia rating-5 locations; the twelve location kernels are averaged analytically.",
      implementation_detail: "No object identity is randomly drawn per particle, mask, or source cell.",
      equivalence_limit: "A uniform subset with any prior on one-to-twelve members gives the same marginal surface only when selected location likelihoods are arithmetically averaged. It is not equivalent to a joint/product likelihood for multiple debris items.",
      literature_scope: "Griffin and Oke's located premise was broader ('at least some'); this handoff uses the narrower explicit computational premise.",
    },
    grid: {
      grid_id: GRID_ID,
      file: "grid.csv",
      cells: context.grid.rows.length,
      shape: {
        along: context.summary.source_grid.along_cells,
        cross: context.summary.source_grid.cross_cells,
      },
      ordering: "surface_id major, then along_index ascending, then cross_index ascending",
      logical_coordinates: {
        along_nm: {
          minimum: 0,
          maximum: 640,
          spacing: context.config.arc_spacing_nm,
          origin: "northern 32 degrees S arc endpoint",
        },
        cross_nm: {
          minimum: -100,
          maximum: 100,
          spacing: context.config.cross_arc_spacing_nm,
          sign: "positive eastward",
        },
      },
      support_area_km2: context.grid.supportArea,
      nominal_interior_quadrature_area_km2: context.grid.nominalArea,
      quadrature: "Two-dimensional trapezoidal rule; edge nodes have half weight and corner nodes quarter weight.",
      normalized_grid_sha256: context.grid.normalizedSha256,
      support_rule: "Only nodes and logical rectangles between adjacent nodes are supported. The outer boundary is a truncation boundary, not evidence of zero likelihood beyond it.",
      interpolation_rule: "Preferred composition is discrete by exact cell_id with quadrature_area_km2. If transfer is unavoidable, linearly interpolate relative_likelihood in logical (along_nm, cross_nm) coordinates after mapping to the same arc system; do not interpolate mass, do not extrapolate, and return unsupported outside the strip.",
      zero_rule: "Exact zeros include IEEE-754 underflow and are not physical impossibility. Blank log_relative_likelihood means log(0) = negative infinity; any finite floor must be an explicitly reported sensitivity.",
    },
    value_semantics: {
      primary_composition_field: "log_relative_likelihood",
      relative_likelihood: "Dimensionless, maximum-one relative endpoint-compatibility score. For components it is proportional to the conditional evidence proxy with the uniform normalization prior removed.",
      log_relative_likelihood: "Natural logarithm of relative_likelihood, maximum zero; blank only where relative_likelihood is exactly zero.",
      normalized_density_per_km2: "Area-normalized compatibility density q_i = raw_score_i / sum_j(raw_score_j * area_j). It integrates to one on this support but is not a calibrated posterior density.",
      normalized_probability_mass: "Quadrature mass q_i * area_i for plotting and checks only. It must never be multiplied into another grid probability as a likelihood.",
      normalization_prior: {
        kind: "uniform density with respect to area over the declared support",
        density_per_km2: 1 / context.grid.supportArea,
        role: "normalization/display prior only; not a flight-path or crash-location prior",
        removal: "relative_likelihood is already prior-removed. If reconstructing from normalized density, divide by this prior density before composing. Because it is constant, division changes only global scale. Never use probability mass because boundary quadrature weights vary.",
      },
      discrete_composition: "For downstream prior mass P_i, posterior mass is proportional to P_i * relative_likelihood_i. For prior density pi_i, posterior mass is proportional to pi_i * relative_likelihood_i * quadrature_area_km2. Add log-relative values to other conditional log-likelihoods only when conditional independence is justified.",
    },
    surfaces: context.surfaceMetadata,
    family_policy: {
      alternatives_not_independent_evidence: COMPONENT_IDS,
      permitted_choices: "Use one declared component family in a conditional run; retain the equal-prior mixture only as a separately reported sensitivity.",
      forbidden_choice: "Never multiply component surfaces together and never include the mixture alongside any component.",
      core_likelihood_rule: "Do not average transport families in a core likelihood. The equal-prior mixture is excluded from core composition.",
      mixture_calibration: "The equal-prior sensitivity mixture is not calibrated; one-third weights are declared sensitivity weights, not empirically estimated model probabilities.",
    },
    blockers_to_calibrated_conditional_likelihood: [
      "The image objects have no calibrated MH370-identity prior, false-positive model, or image-detection/selection likelihood.",
      "The 10 km endpoint kernel, equal twelve-object identity weights, equal windage weights, and diffusion are model choices rather than calibrated observation-error distributions.",
      "Support is truncated to the declared seventh-arc strip; likelihood outside it is uncomputed, not zero.",
      "Finite-particle and seed sensitivity remains material, and numeric zero includes floating-point underflow.",
      "GLORYS12/WAVERYS changes the Eulerian current family and adds explicit Stokes drift while nonzero windage remains present; its difference cannot be assigned to one calibrated model dimension.",
      "No absolute model evidence or calibrated family probabilities exist, so the equal-prior sensitivity mixture is not a model posterior.",
    ],
    provenance: {
      source_run_generated_utc: context.summary.generated_utc,
      source_run_implementation_sha256: context.summary.implementation.combined_sha256,
      builder_node_version: process.version,
      source_files: sourceFiles,
    },
    artifacts: Object.entries(context.generated).map(function (entry) {
      return {
        path: entry[0],
        bytes: Buffer.byteLength(entry[1]),
        sha256: sha256(entry[1]),
      };
    }),
    browser_comparison: {
      html: "comparison.html",
      png: "comparison.png",
      svg: "comparison.svg",
      note: "The HTML embeds the exact source-generated four-panel vector comparison; PNG and SVG are byte-identical packaged copies of the source publication artifacts.",
    },
    deterministic_regeneration: {
      write_command: "node code/build_likelihood_handoff.mjs",
      byte_check_command: "node code/build_likelihood_handoff.mjs --check",
      invariant_test_command: "node --test code/likelihood_handoff.test.mjs",
    },
  };
}

function schemaDocument() {
  return {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    $id: SCHEMA_ID,
    title: "Pleiades conditional source-surface interchange records",
    description: "CSV rows use these property names and types; metadata and scientific semantics are in manifest.json.",
    type: "object",
    $defs: {
      grid_record: {
        type: "object",
        additionalProperties: false,
        required: [
          "schema_version", "grid_id", "cell_id", "along_index", "cross_index",
          "along_nm", "cross_nm", "latitude_deg", "longitude_deg",
          "quadrature_area_km2", "trapezoidal_weight",
        ],
        properties: {
          schema_version: { const: SCHEMA_ID },
          grid_id: { const: GRID_ID },
          cell_id: { type: "string", pattern: "^a[0-9]{3}_x[+-][0-9]{3}$" },
          along_index: { type: "integer", minimum: 0, maximum: 128 },
          cross_index: { type: "integer", minimum: 0, maximum: 40 },
          along_nm: { type: "number", minimum: 0, maximum: 640 },
          cross_nm: { type: "number", minimum: -100, maximum: 100 },
          latitude_deg: { type: "number", minimum: -41, maximum: -30 },
          longitude_deg: { type: "number", minimum: 80, maximum: 105 },
          quadrature_area_km2: { type: "number", exclusiveMinimum: 0 },
          trapezoidal_weight: { enum: [0.25, 0.5, 1] },
        },
      },
      surface_record: {
        type: "object",
        additionalProperties: false,
        required: [
          "schema_version", "surface_id", "cell_id", "relative_likelihood",
          "log_relative_likelihood", "normalized_density_per_km2",
          "normalized_probability_mass",
        ],
        properties: {
          schema_version: { const: SCHEMA_ID },
          surface_id: { enum: [...COMPONENT_IDS, MIXTURE_ID] },
          cell_id: { type: "string", pattern: "^a[0-9]{3}_x[+-][0-9]{3}$" },
          relative_likelihood: { type: "number", minimum: 0, maximum: 1 },
          log_relative_likelihood: { type: ["number", "null"], maximum: 0 },
          normalized_density_per_km2: { type: "number", minimum: 0 },
          normalized_probability_mass: { type: "number", minimum: 0, maximum: 1 },
        },
      },
    },
    csv_mapping: {
      "grid.csv": { record_definition: "#/$defs/grid_record", null_encoding: "empty field" },
      "surfaces.csv": { record_definition: "#/$defs/surface_record", null_encoding: "empty field" },
    },
  };
}

function comparisonHtml(svgText, summary, metadata) {
  const svg = svgText.slice(svgText.indexOf("<svg"));
  const rows = metadata.map(function (surface) {
    const mode = Math.abs(surface.mode.latitude).toFixed(6) + " degrees S, "
      + surface.mode.longitude.toFixed(6) + " degrees E";
    const kind = surface.surface_class === "transport_family_component"
      ? "Conditional proxy" : "Uncalibrated sensitivity";
    return "<tr><th scope=\"row\">" + escapeHtml(surface.label) + "</th><td>" + kind
      + "</td><td>" + mode + "</td><td>" + Math.round(surface.hpd90_area_km2).toLocaleString("en-US")
      + " km2</td></tr>";
  }).join("\n");
  return [
    "<!doctype html>",
    "<html lang=\"en\"><head><meta charset=\"utf-8\">",
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
    "<title>Pleiades conditional source-surface comparison</title>",
    "<style>:root{color-scheme:light;--ink:#1d2430;--muted:#586274;--rule:#d9dde5;--wash:#f5f6fa;--purple:#54278f}*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font:15px/1.5 Arial,sans-serif}main{max-width:1480px;margin:24px auto;padding:24px;background:#fff;box-shadow:0 1px 8px #1d24301a}h1{font-size:24px;margin:0 0 6px}.lede,.foot{color:var(--muted)}.badges{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.badge{border:1px solid var(--rule);border-radius:999px;padding:3px 9px;background:#fafafe;font-size:12px}.warning{border-left:4px solid var(--purple);background:#f3eff8;padding:10px 13px;margin:18px 0}.figure{overflow:auto;border:1px solid var(--rule)}.figure svg{display:block;width:100%;height:auto;min-width:980px}table{border-collapse:collapse;width:100%;margin-top:20px;font-size:13px}th,td{text-align:left;border-bottom:1px solid var(--rule);padding:8px 10px}thead th{background:var(--wash)}caption{text-align:left;font-weight:600;margin-bottom:6px}.foot{font-size:12px}@media(max-width:700px){main{margin:0;padding:14px}.figure svg{min-width:900px}}</style>",
    "</head><body><main>",
    "<h1>Pleiades conditional source-surface comparison</h1>",
    "<p class=\"lede\">One 5,289-node curvilinear seventh-arc grid; three alternative transport responses and one separately labelled sensitivity mixture.</p>",
    "<div class=\"badges\"><span class=\"badge\">Source-only</span><span class=\"badge\">Relative likelihood proxies</span><span class=\"badge\">Mixture not calibrated</span><span class=\"badge\">Identity unknown</span></div>",
    "<div class=\"warning\"><strong>Composition boundary.</strong> The components are alternative conditional endpoint-compatibility proxies, not independent evidence. The fourth surface is an equal-prior sensitivity mixture, not a calibrated model posterior. Select one component or the mixture; never multiply or jointly include them.</div>",
    "<div class=\"figure\" aria-label=\"Four-panel source density comparison\">" + svg + "</div>",
    "<table><caption>Surface audit</caption><thead><tr><th>Surface</th><th>Contract status</th><th>Grid-cell mode</th><th>90% highest-density area</th></tr></thead><tbody>" + rows + "</tbody></table>",
    "<p class=\"foot\">The map shows area-normalized compatibility densities. Downstream composition uses log_relative_likelihood from surfaces.csv, subject to manifest support rules and blockers. Source run: " + escapeHtml(summary.generated_utc) + ".</p>",
    "</main></body></html>",
    "",
  ].join("\n");
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const columns = lines.shift().split(",");
  return lines.map(function (line) {
    const values = line.split(",");
    assert.equal(values.length, columns.length, "quoted CSV is not expected in numeric handoff inputs");
    return Object.fromEntries(columns.map(function (column, index) {
      return [column, values[index]];
    }));
  });
}

function rowsToCsv(rows) {
  assert(rows.length > 0);
  const columns = Object.keys(rows[0]);
  return columns.join(",") + "\n" + rows.map(function (row) {
    return columns.map(function (column) { return csvValue(row[column]); }).join(",");
  }).join("\n") + "\n";
}

function csvValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") {
    assert(Number.isFinite(value));
    return Object.is(value, -0) ? "0" : String(value);
  }
  const text = String(value);
  return /[",\n]/.test(text) ? "\"" + text.replaceAll("\"", "\"\"") + "\"" : text;
}

function normalizedHash(rows, columns) {
  const hash = createHash("sha256");
  for (const row of rows) {
    for (const column of columns) {
      const value = row[column];
      hash.update(column).update("\0");
      hash.update(typeof value === "number" ? canonicalNumber(value) : String(value));
      hash.update("\0");
    }
    hash.update("\n");
  }
  return hash.digest("hex");
}

function canonicalNumber(value) {
  assert(Number.isFinite(value));
  return (Object.is(value, -0) ? 0 : value).toExponential(17);
}

function finiteNumber(value, label) {
  const number = Number(value);
  assert(Number.isFinite(number), label);
  return number;
}

function integerNumber(value, label) {
  const number = finiteNumber(value, label);
  assert(Number.isInteger(number), label);
  return number;
}

function nonnegativeNumber(value, label) {
  const number = finiteNumber(value, label);
  assert(number >= 0, label);
  return number;
}

function close(first, second, tolerance) {
  return Math.abs(first - second) <= tolerance * Math.max(1, Math.abs(first), Math.abs(second));
}

function stableJson(value) {
  return JSON.stringify(value, null, 2) + "\n";
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("\"", "&quot;");
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const checked = process.argv.includes("--check");
  const manifest = await buildLikelihoodHandoff({ checkOnly: checked });
  console.log(JSON.stringify({
    schema_id: manifest.schema_id,
    cells: manifest.grid.cells,
    surfaces: manifest.surfaces.map(function (surface) { return surface.surface_id; }),
    checked,
  }, null, 2));
}
