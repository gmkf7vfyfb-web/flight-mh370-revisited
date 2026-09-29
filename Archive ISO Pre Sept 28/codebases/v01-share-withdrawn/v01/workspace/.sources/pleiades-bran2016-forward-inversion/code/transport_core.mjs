import { readFile } from "node:fs/promises";
import path from "node:path";

export const EARTH_RADIUS_M = 6_371_008.8;
export const METRES_PER_NM = 1852;
export const SECONDS_PER_DAY = 86_400;

export class Xoshiro128 {
  constructor(seed) {
    let state = seed >>> 0;
    this.s = new Uint32Array(4);
    for (let index = 0; index < 4; index += 1) {
      state = (state + 0x9e3779b9) >>> 0;
      let value = state;
      value = Math.imul(value ^ (value >>> 16), 0x21f0aaad);
      value = Math.imul(value ^ (value >>> 15), 0x735a2d97);
      this.s[index] = (value ^ (value >>> 15)) >>> 0;
    }
    if (this.s.every((value) => value === 0)) this.s[0] = 1;
    this.spare = null;
  }

  nextUint32() {
    const s = this.s;
    const result = Math.imul(rotl(Math.imul(s[1], 5) >>> 0, 7), 9) >>> 0;
    const temporary = (s[1] << 9) >>> 0;
    s[2] ^= s[0];
    s[3] ^= s[1];
    s[1] ^= s[2];
    s[0] ^= s[3];
    s[2] ^= temporary;
    s[3] = rotl(s[3], 11);
    return result;
  }

  uniform() {
    return (this.nextUint32() + 0.5) / 4_294_967_296;
  }

  normal() {
    if (this.spare !== null) {
      const value = this.spare;
      this.spare = null;
      return value;
    }
    const radius = Math.sqrt(-2 * Math.log(this.uniform()));
    const angle = 2 * Math.PI * this.uniform();
    this.spare = radius * Math.sin(angle);
    return radius * Math.cos(angle);
  }
}

function rotl(value, shift) {
  return ((value << shift) | (value >>> (32 - shift))) >>> 0;
}

export class VectorField {
  constructor(manifest, values) {
    if (!Array.isArray(manifest.shape) || manifest.shape.length !== 4 || manifest.shape[3] !== 2) {
      throw new Error("vector field requires [time, latitude, longitude, 2] shape");
    }
    const expected = manifest.shape.reduce((product, value) => product * value, 1);
    if (values.length !== expected) throw new Error(`vector field length ${values.length} does not match ${expected}`);
    this.manifest = manifest;
    this.values = values;
    [this.nt, this.nlat, this.nlon] = manifest.shape;
    this.timeStartMs = Date.parse(manifest.time.start_center_utc);
    this.timeStepMs = manifest.time.step_days * SECONDS_PER_DAY * 1000;
    this.latitudes = coordinateValues(manifest.latitude);
    this.longitudes = coordinateValues(manifest.longitude);
    if (!strictlyAscending(this.latitudes) || !strictlyAscending(this.longitudes)) {
      throw new Error("field coordinates must be strictly ascending");
    }
  }

  static async load(manifestPath, dataDirectory) {
    const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
    if (manifest.status && manifest.status !== "retrieved") {
      throw new Error(`field is not available: ${manifest.status}`);
    }
    const bytes = await readFile(path.resolve(dataDirectory, manifest.binary_file));
    if (bytes.length !== manifest.value_count * 4) throw new Error("binary byte count does not match manifest");
    const values = new Float32Array(manifest.value_count);
    for (let index = 0; index < values.length; index += 1) values[index] = bytes.readFloatLE(index * 4);
    return new VectorField(manifest, values);
  }

  sample(epochMs, latitude, longitude) {
    const timeCoordinate = clamp((epochMs - this.timeStartMs) / this.timeStepMs, 0, this.nt - 1);
    const time0 = Math.floor(timeCoordinate);
    const time1 = Math.min(time0 + 1, this.nt - 1);
    const timeWeight = timeCoordinate - time0;
    const lat = bracket(this.latitudes, latitude);
    const lon = bracket(this.longitudes, longitude);
    if (!lat || !lon) return null;
    const first = this.sampleSpace(time0, lat, lon);
    const second = this.sampleSpace(time1, lat, lon);
    if (!first && !second) return null;
    if (!first) return second;
    if (!second) return first;
    return [
      first[0] * (1 - timeWeight) + second[0] * timeWeight,
      first[1] * (1 - timeWeight) + second[1] * timeWeight,
    ];
  }

  sampleSpace(time, latitudeBracket, longitudeBracket) {
    const corners = [
      [latitudeBracket.low, longitudeBracket.low, (1 - latitudeBracket.weight) * (1 - longitudeBracket.weight)],
      [latitudeBracket.low, longitudeBracket.high, (1 - latitudeBracket.weight) * longitudeBracket.weight],
      [latitudeBracket.high, longitudeBracket.low, latitudeBracket.weight * (1 - longitudeBracket.weight)],
      [latitudeBracket.high, longitudeBracket.high, latitudeBracket.weight * longitudeBracket.weight],
    ];
    let u = 0;
    let v = 0;
    let total = 0;
    for (const [latitude, longitude, weight] of corners) {
      if (weight === 0) continue;
      const index = ((time * this.nlat + latitude) * this.nlon + longitude) * 2;
      const cornerU = this.values[index];
      const cornerV = this.values[index + 1];
      if (!Number.isFinite(cornerU) || !Number.isFinite(cornerV)) continue;
      u += weight * cornerU;
      v += weight * cornerV;
      total += weight;
    }
    return total > 0 ? [u / total, v / total] : null;
  }
}

function coordinateValues(specification) {
  if (Array.isArray(specification.values_deg)) return specification.values_deg;
  if (![specification.start_deg, specification.step_deg, specification.count].every(Number.isFinite)) {
    throw new Error("invalid coordinate specification");
  }
  return Array.from({ length: specification.count }, (_, index) => specification.start_deg + index * specification.step_deg);
}

function strictlyAscending(values) {
  return values.every((value, index) => index === 0 || value > values[index - 1]);
}

function bracket(values, target) {
  if (target < values[0] || target > values.at(-1)) return null;
  let low = 0;
  let high = values.length - 1;
  while (high - low > 1) {
    const middle = Math.floor((low + high) / 2);
    if (values[middle] <= target) low = middle;
    else high = middle;
  }
  if (target === values.at(-1)) return { low: high, high, weight: 0 };
  const span = values[high] - values[low];
  return { low, high, weight: span === 0 ? 0 : (target - values[low]) / span };
}

function clamp(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, value));
}

export function haversineKm(first, second) {
  const latitude1 = radians(first.latitude);
  const latitude2 = radians(second.latitude);
  const deltaLatitude = latitude2 - latitude1;
  const deltaLongitude = radians(second.longitude - first.longitude);
  const a = Math.sin(deltaLatitude / 2) ** 2
    + Math.cos(latitude1) * Math.cos(latitude2) * Math.sin(deltaLongitude / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.min(1, Math.sqrt(a))) / 1000;
}

function radians(degrees) {
  return degrees * Math.PI / 180;
}

export function velocityStep(position, velocity, seconds) {
  const latitudeRadians = radians(position.latitude);
  return {
    latitude: position.latitude + velocity[1] * seconds / EARTH_RADIUS_M * 180 / Math.PI,
    longitude: position.longitude + velocity[0] * seconds / (EARTH_RADIUS_M * Math.max(1e-8, Math.cos(latitudeRadians))) * 180 / Math.PI,
  };
}

export function advectParticle({
  start,
  startMs,
  endMs,
  stepSeconds,
  current,
  stokes = null,
  wind,
  windage,
  diffusionRmsNmPerDay,
  random,
}) {
  let position = { ...start };
  let time = startMs;
  let valid = true;
  while (time < endMs) {
    const seconds = Math.min(stepSeconds, (endMs - time) / 1000);
    const initial = combinedVelocity(current, stokes, wind, windage, time, position);
    if (!initial) {
      valid = false;
      break;
    }
    const midpoint = velocityStep(position, initial, seconds / 2);
    const middleVelocity = combinedVelocity(current, stokes, wind, windage, time + seconds * 500, midpoint);
    if (!middleVelocity) {
      valid = false;
      break;
    }
    position = velocityStep(position, middleVelocity, seconds);
    if (diffusionRmsNmPerDay > 0) {
      const componentSigmaM = diffusionRmsNmPerDay * METRES_PER_NM
        * Math.sqrt(seconds / SECONDS_PER_DAY) / Math.sqrt(2);
      position = velocityStep(position, [random.normal() * componentSigmaM / seconds, random.normal() * componentSigmaM / seconds], seconds);
    }
    time += seconds * 1000;
  }
  return { ...position, valid };
}

function combinedVelocity(current, stokes, wind, windage, time, position) {
  const ocean = current.sample(time, position.latitude, position.longitude);
  if (!ocean) return null;
  const wave = stokes ? stokes.sample(time, position.latitude, position.longitude) : [0, 0];
  if (!wave) return null;
  const base = [ocean[0] + wave[0], ocean[1] + wave[1]];
  if (!wind || windage === 0) return base;
  const atmosphere = wind.sample(time, position.latitude, position.longitude);
  if (!atmosphere) return null;
  return [base[0] + windage * atmosphere[0], base[1] + windage * atmosphere[1]];
}

export function endpointKernel(endpoint, objects, sigmaKm) {
  let total = 0;
  for (const object of objects) {
    const distance = haversineKm(endpoint, object);
    total += Math.exp(-0.5 * (distance / sigmaKm) ** 2);
  }
  return total / objects.length;
}

export function readObjects(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  const header = lines.shift().split(",");
  const index = Object.fromEntries(header.map((name, position) => [name, position]));
  return lines.map((line) => {
    const fields = line.split(",");
    return {
      id: `${fields[index.scene]}-${fields[index.object]}`,
      scene: fields[index.scene],
      object: Number(fields[index.object]),
      latitude: Number(fields[index.latitude_deg]),
      longitude: Number(fields[index.longitude_deg]),
      areaM2: Number(fields[index.reported_area_m2]),
      sets: new Set(fields[index.object_set].split(";")),
    };
  });
}

export function buildSourceGrid(geojson, configuration) {
  const coordinates = geojson.features[0].geometry.coordinates
    .map(([longitude, latitude]) => ({ latitude, longitude }));
  const minimumLatitude = configuration.arc_latitude_range_deg[0];
  const maximumLatitude = configuration.arc_latitude_range_deg[1];
  const southern = coordinates.filter((point) => point.latitude < 0);
  const endpoints = [
    interpolateAtLatitude(southern, maximumLatitude),
    ...southern.filter((point) => point.latitude < maximumLatitude && point.latitude > minimumLatitude),
    interpolateAtLatitude(southern, minimumLatitude),
  ];
  endpoints.sort((first, second) => second.latitude - first.latitude);
  const arc = resamplePolyline(endpoints, configuration.arc_spacing_nm * METRES_PER_NM / 1000);
  const [crossMinimum, crossMaximum] = configuration.cross_arc_range_nm;
  const spacing = configuration.cross_arc_spacing_nm;
  const crossOffsets = [];
  for (let offset = crossMinimum; offset <= crossMaximum + 1e-9; offset += spacing) crossOffsets.push(offset);
  const cells = [];
  for (let alongIndex = 0; alongIndex < arc.length; alongIndex += 1) {
    const previous = arc[Math.max(0, alongIndex - 1)];
    const next = arc[Math.min(arc.length - 1, alongIndex + 1)];
    const meanLatitude = radians((previous.latitude + next.latitude) / 2);
    const tangentEast = radians(next.longitude - previous.longitude) * Math.cos(meanLatitude) * EARTH_RADIUS_M;
    const tangentNorth = radians(next.latitude - previous.latitude) * EARTH_RADIUS_M;
    const magnitude = Math.hypot(tangentEast, tangentNorth);
    let normalEast = -tangentNorth / magnitude;
    let normalNorth = tangentEast / magnitude;
    if (normalEast < 0) {
      normalEast *= -1;
      normalNorth *= -1;
    }
    for (let crossIndex = 0; crossIndex < crossOffsets.length; crossIndex += 1) {
      const crossNm = crossOffsets[crossIndex];
      const metres = crossNm * METRES_PER_NM;
      const origin = arc[alongIndex];
      const position = velocityStep(origin, [normalEast * metres, normalNorth * metres], 1);
      const alongFactor = alongIndex === 0 || alongIndex === arc.length - 1 ? 0.5 : 1;
      const crossFactor = crossIndex === 0 || crossIndex === crossOffsets.length - 1 ? 0.5 : 1;
      cells.push({
        id: `a${String(alongIndex).padStart(3, "0")}_x${crossNm >= 0 ? "+" : "-"}${String(Math.abs(crossNm)).padStart(3, "0")}`,
        alongIndex,
        crossIndex,
        alongNm: alongIndex * configuration.arc_spacing_nm,
        crossNm,
        latitude: position.latitude,
        longitude: position.longitude,
        cellAreaKm2: configuration.arc_spacing_nm * configuration.cross_arc_spacing_nm
          * (METRES_PER_NM / 1000) ** 2 * alongFactor * crossFactor,
      });
    }
  }
  return { cells, arc, crossOffsets, alongCount: arc.length, crossCount: crossOffsets.length };
}

function interpolateAtLatitude(points, target) {
  for (let index = 1; index < points.length; index += 1) {
    const first = points[index - 1];
    const second = points[index];
    if ((first.latitude - target) * (second.latitude - target) <= 0 && first.latitude !== second.latitude) {
      const weight = (target - first.latitude) / (second.latitude - first.latitude);
      return {
        latitude: target,
        longitude: first.longitude + weight * (second.longitude - first.longitude),
      };
    }
  }
  throw new Error(`arc does not cross latitude ${target}`);
}

function resamplePolyline(points, spacingKm) {
  const cumulative = [0];
  for (let index = 1; index < points.length; index += 1) {
    cumulative.push(cumulative.at(-1) + haversineKm(points[index - 1], points[index]));
  }
  const total = cumulative.at(-1);
  const count = Math.floor(total / spacingKm);
  const distances = Array.from({ length: count + 1 }, (_, index) => index * spacingKm);
  if (total - distances.at(-1) > spacingKm * 0.25) distances.push(total);
  else distances[distances.length - 1] = total;
  return distances.map((distance) => {
    let high = cumulative.findIndex((value) => value >= distance);
    if (high <= 0) return { ...points[0] };
    const low = high - 1;
    const span = cumulative[high] - cumulative[low];
    const weight = span === 0 ? 0 : (distance - cumulative[low]) / span;
    return {
      latitude: points[low].latitude + weight * (points[high].latitude - points[low].latitude),
      longitude: points[low].longitude + weight * (points[high].longitude - points[low].longitude),
    };
  });
}

export function simulateCell({
  cell,
  cellIndex,
  current,
  stokes = null,
  wind,
  objectsBySet,
  windageFactors,
  windagePrior,
  particleCount,
  startMs,
  endMs,
  stepSeconds,
  diffusionRmsNmPerDay,
  kernelSigmasKm,
  seed,
}) {
  const scores = {};
  let validParticles = 0;
  for (const setName of Object.keys(objectsBySet)) {
    scores[setName] = Object.fromEntries(kernelSigmasKm.map((sigma) => [sigma, {
      byWindage: new Array(windageFactors.length).fill(0),
      mixture: 0,
    }]));
  }
  for (let windageIndex = 0; windageIndex < windageFactors.length; windageIndex += 1) {
    let validForWindage = 0;
    for (let particle = 0; particle < particleCount; particle += 1) {
      const random = new Xoshiro128(mixSeed(seed, cellIndex, windageIndex, particle));
      const endpoint = advectParticle({
        start: cell,
        startMs,
        endMs,
        stepSeconds,
        current,
        stokes,
        wind,
        windage: windageFactors[windageIndex],
        diffusionRmsNmPerDay,
        random,
      });
      if (!endpoint.valid) continue;
      validParticles += 1;
      validForWindage += 1;
      for (const [setName, objects] of Object.entries(objectsBySet)) {
        for (const sigma of kernelSigmasKm) {
          scores[setName][sigma].byWindage[windageIndex] += endpointKernel(endpoint, objects, sigma);
        }
      }
    }
    for (const setName of Object.keys(objectsBySet)) {
      for (const sigma of kernelSigmasKm) {
        const entry = scores[setName][sigma];
        entry.byWindage[windageIndex] = validForWindage > 0
          ? entry.byWindage[windageIndex] / validForWindage
          : 0;
      }
    }
  }
  for (const setName of Object.keys(objectsBySet)) {
    for (const sigma of kernelSigmasKm) {
      const entry = scores[setName][sigma];
      entry.mixture = entry.byWindage.reduce((sum, value, index) => sum + value * windagePrior[index], 0);
    }
  }
  return { scores, validParticles };
}

function mixSeed(seed, cell, windage, particle) {
  let value = seed >>> 0;
  value ^= Math.imul((cell + 1) >>> 0, 0x9e3779b1);
  value ^= Math.imul((windage + 1) >>> 0, 0x85ebca77);
  value ^= Math.imul((particle + 1) >>> 0, 0xc2b2ae3d);
  value ^= value >>> 16;
  value = Math.imul(value, 0x7feb352d);
  value ^= value >>> 15;
  return value >>> 0;
}

export function normalizeSurface(rows, likelihoodKey = "likelihood") {
  let total = 0;
  for (const row of rows) total += Math.max(0, row[likelihoodKey]) * row.cellAreaKm2;
  if (!(total > 0)) throw new Error("surface has no positive finite likelihood");
  return rows.map((row) => ({
    ...row,
    densityPerKm2: Math.max(0, row[likelihoodKey]) / total,
    probabilityMass: Math.max(0, row[likelihoodKey]) * row.cellAreaKm2 / total,
  }));
}


export function modelAverageSurface(components) {
  if (!Array.isArray(components) || components.length < 2) {
    throw new Error("model average requires at least two component surfaces");
  }
  const totalWeight = components.reduce((sum, component) => {
    if (!Number.isFinite(component.weight) || component.weight < 0) {
      throw new Error("model-average weights must be finite and non-negative");
    }
    return sum + component.weight;
  }, 0);
  if (!(totalWeight > 0)) throw new Error("model-average weights have no positive mass");
  const reference = components[0].surface;
  if (!Array.isArray(reference) || reference.length === 0) {
    throw new Error("model-average component surface is empty");
  }
  for (const component of components) {
    if (!Array.isArray(component.surface) || component.surface.length !== reference.length) {
      throw new Error("model-average component surface length mismatch");
    }
  }
  return reference.map((row, index) => {
    let densityPerKm2 = 0;
    let probabilityMass = 0;
    for (const component of components) {
      const candidate = component.surface[index];
      if (candidate.id !== row.id || Math.abs(candidate.cellAreaKm2 - row.cellAreaKm2) > 1e-9) {
        throw new Error(`model-average grid mismatch at ${row.id}`);
      }
      const weight = component.weight / totalWeight;
      densityPerKm2 += weight * candidate.densityPerKm2;
      probabilityMass += weight * candidate.probabilityMass;
    }
    return { ...row, densityPerKm2, probabilityMass };
  });
}

export function uniformSubsetAveragedIdentityWeights(objectCount, cardinalityPrior) {
  if (!Number.isInteger(objectCount) || objectCount < 1) {
    throw new Error("object count must be a positive integer");
  }
  if (!Array.isArray(cardinalityPrior) || cardinalityPrior.length < 1
      || cardinalityPrior.length > objectCount) {
    throw new Error("cardinality prior must cover between one and objectCount cardinalities");
  }
  const totalPrior = cardinalityPrior.reduce((sum, value) => {
    if (!Number.isFinite(value) || value < 0) {
      throw new Error("cardinality-prior entries must be finite and non-negative");
    }
    return sum + value;
  }, 0);
  if (!(totalPrior > 0)) throw new Error("cardinality prior has no positive mass");
  const cardinalities = cardinalityPrior.map((value, index) => {
    const cardinality = index + 1;
    const priorProbability = value / totalPrior;
    const inclusionProbabilityPerObject = cardinality / objectCount;
    const scoreWeightIfIncluded = 1 / cardinality;
    return {
      cardinality,
      unnormalizedPrior: value,
      priorProbability,
      inclusionProbabilityPerObject,
      scoreWeightIfIncluded,
      marginalWeightPerObject: inclusionProbabilityPerObject * scoreWeightIfIncluded,
    };
  });
  const objectWeights = new Array(objectCount).fill(0).map(() => cardinalities.reduce(
    (sum, entry) => sum + entry.priorProbability * entry.marginalWeightPerObject,
    0,
  ));
  return {
    cardinalities,
    objectWeights,
    maximumAbsoluteDifferenceFromEqualWeight: Math.max(
      ...objectWeights.map((weight) => Math.abs(weight - 1 / objectCount)),
    ),
  };
}
export function summarizeSurface(surface) {
  const ordered = [...surface].sort((first, second) => second.densityPerKm2 - first.densityPerKm2);
  const thresholds = {};
  for (const level of [0.5, 0.9, 0.95]) {
    let mass = 0;
    let area = 0;
    let threshold = 0;
    for (const row of ordered) {
      mass += row.probabilityMass;
      area += row.cellAreaKm2;
      threshold = row.densityPerKm2;
      if (mass >= level) break;
    }
    thresholds[level] = { achievedMass: mass, areaKm2: area, densityThresholdPerKm2: threshold };
  }
  const mode = ordered[0];
  const mean = surface.reduce((output, row) => {
    output.latitude += row.latitude * row.probabilityMass;
    output.longitude += row.longitude * row.probabilityMass;
    output.crossNm += row.crossNm * row.probabilityMass;
    return output;
  }, { latitude: 0, longitude: 0, crossNm: 0 });
  return {
    mode: { id: mode.id, latitude: mode.latitude, longitude: mode.longitude, crossNm: mode.crossNm },
    mean,
    hpd: thresholds,
  };
}

export function totalVariation(first, second) {
  if (first.length !== second.length) throw new Error("surface length mismatch");
  return 0.5 * first.reduce((sum, row, index) => sum + Math.abs(row.probabilityMass - second[index].probabilityMass), 0);
}

