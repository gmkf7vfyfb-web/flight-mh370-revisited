import assert from "node:assert/strict";
import test from "node:test";

import {
  METRES_PER_NM,
  SECONDS_PER_DAY,
  VectorField,
  Xoshiro128,
  advectParticle,
  buildSourceGrid,
  endpointKernel,
  haversineKm,
  modelAverageSurface,
  normalizeSurface,
  summarizeSurface,
  uniformSubsetAveragedIdentityWeights,
} from "./transport_core.mjs";

function constantField(u, v) {
  return new VectorField({
    shape: [2, 2, 2, 2],
    time: { start_center_utc: "2014-03-08T00:00:00Z", step_days: 1 },
    latitude: { start_deg: -40, step_deg: 20, count: 2 },
    longitude: { start_deg: 80, step_deg: 40, count: 2 },
  }, new Float32Array(2 * 2 * 2 * 2).map((_, index) => index % 2 === 0 ? u : v));
}

test("bilinear and temporal interpolation preserve a constant vector", () => {
  const field = constantField(0.125, -0.25);
  assert.deepEqual(field.sample(Date.parse("2014-03-08T12:00:00Z"), -30, 100), [0.125, -0.25]);
});

test("midpoint advection agrees with analytic constant-current displacement", () => {
  const current = constantField(0.1, 0);
  const start = { latitude: -35, longitude: 92 };
  const end = advectParticle({
    start,
    startMs: 0,
    endMs: SECONDS_PER_DAY * 1000,
    stepSeconds: 3 * 3600,
    current,
    wind: null,
    windage: 0,
    diffusionRmsNmPerDay: 0,
    random: new Xoshiro128(1),
  });
  const expectedKm = 0.1 * SECONDS_PER_DAY / 1000;
  assert.ok(Math.abs(haversineKm(start, end) - expectedKm) < 0.02);
});

test("Eulerian current and Stokes drift are added as distinct velocity terms", () => {
  const current = constantField(0.1, -0.02);
  const stokes = constantField(0.05, 0.02);
  const start = { latitude: -35, longitude: 92 };
  const end = advectParticle({
    start,
    startMs: 0,
    endMs: SECONDS_PER_DAY * 1000,
    stepSeconds: 3 * 3600,
    current,
    stokes,
    wind: null,
    windage: 0,
    diffusionRmsNmPerDay: 0,
    random: new Xoshiro128(2),
  });
  const expectedKm = 0.15 * SECONDS_PER_DAY / 1000;
  assert.ok(Math.abs(haversineKm(start, end) - expectedKm) < 0.02);
});

test("random-walk scaling reproduces declared two-dimensional daily RMS", () => {
  const random = new Xoshiro128(37003801);
  const count = 200_000;
  const sigma = 5 * METRES_PER_NM / Math.sqrt(2);
  let squared = 0;
  for (let index = 0; index < count; index += 1) {
    const east = random.normal() * sigma;
    const north = random.normal() * sigma;
    squared += east * east + north * north;
  }
  const rmsNm = Math.sqrt(squared / count) / METRES_PER_NM;
  assert.ok(Math.abs(rmsNm - 5) < 0.03, `daily RMS was ${rmsNm}`);
});

test("equal object identity weights are permutation invariant", () => {
  const endpoint = { latitude: -35, longitude: 92 };
  const objects = [
    { latitude: -35.1, longitude: 92.1 },
    { latitude: -34.9, longitude: 91.9 },
  ];
  assert.equal(endpointKernel(endpoint, objects, 10), endpointKernel(endpoint, [...objects].reverse(), 10));
});

test("source grid uses east-positive cross-arc coordinates", () => {
  const geojson = { features: [{ geometry: { coordinates: [[92, -31], [92, -32], [92, -39], [92, -40]] } }] };
  const grid = buildSourceGrid(geojson, {
    arc_latitude_range_deg: [-39, -32],
    arc_spacing_nm: 50,
    cross_arc_range_nm: [-10, 10],
    cross_arc_spacing_nm: 10,
  });
  const west = grid.cells.find((cell) => cell.alongIndex === 0 && cell.crossNm === -10);
  const east = grid.cells.find((cell) => cell.alongIndex === 0 && cell.crossNm === 10);
  assert.ok(west.longitude < 92);
  assert.ok(east.longitude > 92);
});

test("surface normalization and HPD conserve probability", () => {
  const surface = normalizeSurface([
    { id: "a", likelihood: 2, cellAreaKm2: 10, latitude: -35, longitude: 92, crossNm: 0 },
    { id: "b", likelihood: 1, cellAreaKm2: 10, latitude: -36, longitude: 91, crossNm: 5 },
  ]);
  assert.ok(Math.abs(surface.reduce((sum, row) => sum + row.probabilityMass, 0) - 1) < 1e-12);
  const summary = summarizeSurface(surface);
  assert.equal(summary.mode.id, "a");
  assert.equal(summary.hpd[0.5].areaKm2, 10);
});



test("model averaging is a normalized prior-weighted mixture, not a product", () => {
  const first = [
    { id: "a", cellAreaKm2: 10, densityPerKm2: 0.08, probabilityMass: 0.8 },
    { id: "b", cellAreaKm2: 10, densityPerKm2: 0.02, probabilityMass: 0.2 },
  ];
  const second = [
    { id: "a", cellAreaKm2: 10, densityPerKm2: 0.03, probabilityMass: 0.3 },
    { id: "b", cellAreaKm2: 10, densityPerKm2: 0.07, probabilityMass: 0.7 },
  ];
  const averaged = modelAverageSurface([
    { id: "first", weight: 1, surface: first },
    { id: "second", weight: 3, surface: second },
  ]);
  assert.ok(Math.abs(averaged[0].probabilityMass - 0.425) < 1e-12);
  assert.ok(Math.abs(averaged[1].probabilityMass - 0.575) < 1e-12);
  assert.ok(Math.abs(averaged.reduce((sum, row) => sum + row.probabilityMass, 0) - 1) < 1e-12);
});

test("uniform one-to-five subset averaging is exactly equal to an exact-one mixture", () => {
  const control = uniformSubsetAveragedIdentityWeights(5, [16, 8, 4, 2, 1]);
  assert.equal(control.cardinalities.length, 5);
  assert.ok(control.maximumAbsoluteDifferenceFromEqualWeight < 1e-15);
  assert.deepEqual(control.objectWeights, new Array(5).fill(0.2));
  const objectLikelihoods = [0.04, 0.17, 0.31, 0.59, 0.83];
  const exactOne = objectLikelihoods.reduce((sum, value) => sum + value / 5, 0);
  const randomCardinality = objectLikelihoods.reduce(
    (sum, value, index) => sum + value * control.objectWeights[index],
    0,
  );
  assert.ok(Math.abs(randomCardinality - exactOne) < 1e-15);
});
