#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, readFile, rm, stat, writeFile, copyFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(bundle, "data");
const paperDir = path.join(bundle, "paper");
const sourceDir = path.join(dataDir, "source-metadata");
const config = JSON.parse(await readFile(path.join(dataDir, "config.json"), "utf8"));
const legacy = process.env.MH370_LEGACY_ARCHIVE
  ?? "/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824";

const NCI_ROOT = "https://thredds.nci.org.au/thredds/dodsC/gb6/BRAN/BRAN_2016/OFAM";
const NOAA_ROOT = "https://psl.noaa.gov/thredds/dodsC/Datasets/ncep.reanalysis.dailyavgs/surface_gauss";
const OSCAR_COLLECTION = "C2098858642-POCLOUD";
const OSCAR_ROOT = `https://opendap.earthdata.nasa.gov/collections/${OSCAR_COLLECTION}/granules`;
const OSCAR_GUIDE = "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-docs/oscar/open/L4/oscar_v2.0/docs/oscarv2guide.pdf";

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

async function fetchBytes(url, attempts = 3) {
  let last;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(url, {
        headers: { "user-agent": "mh370-pleiades-forward-inversion/1" },
        signal: AbortSignal.timeout(300_000),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
      return Buffer.from(await response.arrayBuffer());
    } catch (error) {
      last = error;
      if (attempt < attempts) await new Promise((resolve) => setTimeout(resolve, 1000 * attempt));
    }
  }
  throw last;
}

async function fetchText(url, attempts = 3) {
  return (await fetchBytes(url, attempts)).toString("utf8");
}

function parseGridRows(text, qualifiedVariable, expectedCount) {
  const lines = text.split(/\r?\n/);
  const values = [];
  function appendRow(line) {
    const comma = line.indexOf(",");
    if (comma < 0) throw new Error("invalid OPeNDAP row for " + qualifiedVariable);
    for (const token of line.slice(comma + 1).split(",")) {
      const value = Number(token.trim());
      if (!Number.isFinite(value)) throw new Error("non-numeric OPeNDAP value for " + qualifiedVariable);
      values.push(value);
    }
  }

  const qualifiedRows = lines.filter(function (line) {
    return line.startsWith(qualifiedVariable + "[") && line.includes(",");
  });
  if (qualifiedRows.length) {
    qualifiedRows.forEach(appendRow);
  } else {
    const header = lines.findIndex(function (line) { return line.startsWith(qualifiedVariable + "["); });
    if (header < 0) throw new Error("missing " + qualifiedVariable + " data header");
    for (let index = header + 1; index < lines.length; index += 1) {
      const line = lines[index].trim();
      if (!line.startsWith("[")) break;
      appendRow(line);
    }
  }
  if (values.length !== expectedCount) {
    throw new Error(qualifiedVariable + ": expected " + expectedCount + " values, received " + values.length);
  }
  return values;
}
function float32Buffer(values) {
  const buffer = Buffer.allocUnsafe(values.length * 4);
  for (let index = 0; index < values.length; index += 1) {
    buffer.writeFloatLE(values[index], index * 4);
  }
  return buffer;
}

async function writeGrid(name, values, metadata) {
  const bytes = float32Buffer(values);
  const binaryName = `${name}.f32le`;
  await writeFile(path.join(dataDir, binaryName), bytes);
  const manifest = {
    schema_version: 1,
    name,
    binary_file: binaryName,
    byte_order: "little_endian",
    scalar_type: "float32",
    value_count: values.length,
    sha256: sha256(bytes),
    ...metadata,
  };
  await writeFile(path.join(dataDir, `${name}.manifest.json`), `${JSON.stringify(manifest, null, 2)}\n`);
  return manifest;
}

async function fetchBran() {
  const subset = config.bran_subset;
  const [time0, time1] = subset.time_indices;
  const [lat0, lat1] = subset.latitude_indices;
  const [lon0, lon1] = subset.longitude_indices;
  const nt = time1 - time0 + 1;
  const nlat = lat1 - lat0 + 1;
  const nlon = lon1 - lon0 + 1;
  const count = nt * nlat * nlon;
  const outputs = {};
  for (const component of ["u", "v"]) {
    const file = `ocean_${component}_2014_03.nc`;
    const base = `${NCI_ROOT}/${file}`;
    const query = `${component}[${time0}:1:${time1}][${subset.depth_index}:1:${subset.depth_index}][${lat0}:1:${lat1}][${lon0}:1:${lon1}]`;
    const text = await fetchText(`${base}.ascii?${query}`);
    const packed = parseGridRows(text, `${component}.${component}`, count);
    const physical = packed.map((value) => value === subset.missing_packed_value
      ? Number.NaN
      : value * subset.scale_factor);
    outputs[component] = physical;
    await writeFile(path.join(sourceDir, `bran2016-${component}.dds`), await fetchText(`${base}.dds`));
    await writeFile(path.join(sourceDir, `bran2016-${component}.das`), await fetchText(`${base}.das`));
  }
  const missing = outputs.u.reduce((sum, value, index) => sum + (!Number.isFinite(value) || !Number.isFinite(outputs.v[index]) ? 1 : 0), 0);
  return writeGrid("bran2016-surface-currents-20140308-23", interleave(outputs.u, outputs.v), {
    source_family: "BRAN2016",
    source_urls: [`${NCI_ROOT}/ocean_u_2014_03.nc`, `${NCI_ROOT}/ocean_v_2014_03.nc`],
    variable_order: ["u_east_m_s", "v_north_m_s"],
    dimension_order: ["time", "latitude", "longitude", "component"],
    shape: [nt, nlat, nlon, 2],
    time: { start_center_utc: "2014-03-08T12:00:00Z", step_days: 1, count: nt },
    latitude: { start_deg: -45.0, step_deg: 0.1, count: nlat, ascending: true },
    longitude: { start_deg: 80.0, step_deg: 0.1, count: nlon, ascending: true },
    depth_m: 2.5,
    units: "m s-1",
    packed_scale_factor: subset.scale_factor,
    missing_vector_count: missing,
  });
}

function interleave(first, second) {
  if (first.length !== second.length) throw new Error("component length mismatch");
  const output = new Array(first.length * 2);
  for (let index = 0; index < first.length; index += 1) {
    output[2 * index] = first[index];
    output[2 * index + 1] = second[index];
  }
  return output;
}

async function fetchNcepWind() {
  const subset = config.ncep_wind_subset;
  const [time0, time1] = subset.time_indices;
  const [lat0, lat1] = subset.latitude_indices;
  const [lon0, lon1] = subset.longitude_indices;
  const nt = time1 - time0 + 1;
  const nlat = lat1 - lat0 + 1;
  const nlon = lon1 - lon0 + 1;
  const count = nt * nlat * nlon;
  const values = {};
  for (const [filePrefix, variable] of [["uwnd", "uwnd"], ["vwnd", "vwnd"]]) {
    const file = `${filePrefix}.10m.gauss.2014.nc`;
    const base = `${NOAA_ROOT}/${file}`;
    const query = `${variable}[${time0}:1:${time1}][${lat0}:1:${lat1}][${lon0}:1:${lon1}]`;
    const text = await fetchText(`${base}.ascii?${query}`);
    values[variable] = parseGridRows(text, `${variable}.${variable}`, count);
    await writeFile(path.join(sourceDir, `ncep-${variable}.dds`), await fetchText(`${base}.dds`));
    await writeFile(path.join(sourceDir, `ncep-${variable}.das`), await fetchText(`${base}.das`));
  }
  const coordinates = await fetchText(`${NOAA_ROOT}/uwnd.10m.gauss.2014.nc.ascii?lat[${lat0}:1:${lat1}],lon[${lon0}:1:${lon1}],time[${time0}:1:${time1}]`);
  await writeFile(path.join(sourceDir, "ncep-subset-coordinates.txt"), coordinates);
  const latitudes = parseVector(coordinates, "lat", nlat);
  const longitudes = parseVector(coordinates, "lon", nlon);
  const reorderedU = reorderLatitude(values.uwnd, nt, nlat, nlon);
  const reorderedV = reorderLatitude(values.vwnd, nt, nlat, nlon);
  return writeGrid("ncep-ncar-r1-10m-wind-20140308-23", interleave(reorderedU, reorderedV), {
    source_family: "NCEP-NCAR Reanalysis 1",
    source_urls: [`${NOAA_ROOT}/uwnd.10m.gauss.2014.nc`, `${NOAA_ROOT}/vwnd.10m.gauss.2014.nc`],
    variable_order: ["u_east_m_s", "v_north_m_s"],
    dimension_order: ["time", "latitude", "longitude", "component"],
    shape: [nt, nlat, nlon, 2],
    time: { start_center_utc: "2014-03-08T00:00:00Z", step_days: 1, count: nt },
    latitude: { values_deg: [...latitudes].reverse(), ascending: true },
    longitude: { values_deg: longitudes, ascending: true },
    height_m: 10,
    units: "m s-1",
    missing_vector_count: reorderedU.reduce((sum, value, index) => sum + (!Number.isFinite(value) || !Number.isFinite(reorderedV[index]) ? 1 : 0), 0),
  });
}

function parseVector(text, name, expectedCount) {
  const pattern = new RegExp(`(?:^|\\n)${name}\\[${expectedCount}\\]\\n([^\\n]+)`);
  const match = text.match(pattern);
  if (!match) throw new Error(`missing ${name} coordinate vector`);
  const values = match[1].split(",").map((value) => Number(value.trim()));
  if (values.length !== expectedCount || values.some((value) => !Number.isFinite(value))) {
    throw new Error(`invalid ${name} coordinate vector`);
  }
  return values;
}

function reorderLatitude(values, nt, nlat, nlon) {
  const output = new Array(values.length);
  for (let time = 0; time < nt; time += 1) {
    for (let latitude = 0; latitude < nlat; latitude += 1) {
      const targetLatitude = nlat - 1 - latitude;
      for (let longitude = 0; longitude < nlon; longitude += 1) {
        output[(time * nlat + targetLatitude) * nlon + longitude]
          = values[(time * nlat + latitude) * nlon + longitude];
      }
    }
  }
  return output;
}

function parseDotenv(text) {
  const output = {};
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const equals = line.indexOf("=");
    if (equals < 1) continue;
    const key = line.slice(0, equals).trim();
    let value = line.slice(equals + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    output[key] = value;
  }
  return output;
}

async function exists(filename) {
  try {
    await stat(filename);
    return true;
  } catch {
    return false;
  }
}

async function curlEarthdata(url, netrc, cookie) {
  return new Promise((resolve, reject) => {
    const child = spawn("curl", [
      "--silent", "--show-error", "--fail", "--location", "--location-trusted",
      "--globoff",
      "--netrc-file", netrc, "--cookie", cookie, "--cookie-jar", cookie,
      "--max-time", "300", url,
    ], { stdio: ["ignore", "pipe", "pipe"] });
    const stdout = [];
    const stderr = [];
    child.stdout.on("data", (chunk) => stdout.push(chunk));
    child.stderr.on("data", (chunk) => stderr.push(chunk));
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(Buffer.concat(stdout));
      else reject(new Error(`Earthdata curl failed with exit ${code}: ${Buffer.concat(stderr).toString("utf8").trim()}`));
    });
  });
}

async function fetchOscar() {
  const envPath = process.env.EARTHDATA_ENV ?? "/tmp/mh370-oscar-earthdata.env";
  if (!(await exists(envPath))) {
    const manifest = { schema_version: 1, source_family: "OSCAR v2 Final", status: "blocked_missing_earthdata_credentials", credential_file: envPath };
    await writeFile(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
    return manifest;
  }
  const credentials = parseDotenv(await readFile(envPath, "utf8"));
  if (!credentials.EARTHDATA_USERNAME || !credentials.EARTHDATA_PASSWORD) {
    throw new Error("Earthdata dotenv lacks required assignments");
  }
  const temporary = await mkdtemp(path.join(tmpdir(), "mh370-earthdata-"));
  const netrc = path.join(temporary, "netrc");
  const cookie = path.join(temporary, "cookies.txt");
  await writeFile(netrc, `machine urs.earthdata.nasa.gov login ${credentials.EARTHDATA_USERNAME} password ${credentials.EARTHDATA_PASSWORD}\n`, { mode: 0o600 });
  credentials.EARTHDATA_USERNAME = "";
  credentials.EARTHDATA_PASSWORD = "";
  try {
    const subset = config.oscar_subset;
    const [lat0, lat1] = subset.latitude_indices;
    const [lon0, lon1] = subset.longitude_indices;
    const nt = 16;
    const nlat = lat1 - lat0 + 1;
    const nlon = lon1 - lon0 + 1;
    const u = new Array(nt * nlat * nlon);
    const v = new Array(nt * nlat * nlon);
    for (let day = 0; day < nt; day += 1) {
      const date = new Date(Date.UTC(2014, 2, 8 + day)).toISOString().slice(0, 10).replaceAll("-", "");
      console.log("OSCAR " + date + " (" + (day + 1) + "/" + nt + ")");
      const granule = `oscar_currents_final_${date}`;
      const base = `${OSCAR_ROOT}/${granule}`;
      if (day === 0) {
        await writeFile(path.join(sourceDir, "oscar-v2-final-sample.dds"), await curlEarthdata(`${base}.dds`, netrc, cookie));
        await writeFile(path.join(sourceDir, "oscar-v2-final-sample.das"), await curlEarthdata(`${base}.das`, netrc, cookie));
      }
      const query = `u.u[0:1:0][${lon0}:1:${lon1}][${lat0}:1:${lat1}],v.v[0:1:0][${lon0}:1:${lon1}][${lat0}:1:${lat1}]`;
      const text = (await curlEarthdata(`${base}.ascii?${encodeURIComponent(query)}`, netrc, cookie)).toString("utf8");
      const dayU = parseGridRows(text, "u.u", nlat * nlon);
      const dayV = parseGridRows(text, "v.v", nlat * nlon);
      for (let longitude = 0; longitude < nlon; longitude += 1) {
        for (let latitude = 0; latitude < nlat; latitude += 1) {
          const target = (day * nlat + latitude) * nlon + longitude;
          const source = longitude * nlat + latitude;
          u[target] = dayU[source] <= -998 ? Number.NaN : dayU[source];
          v[target] = dayV[source] <= -998 ? Number.NaN : dayV[source];
        }
      }

    }
    return writeGrid("oscar-v2-final-20140308-23", interleave(u, v), {
      source_family: "OSCAR v2 Final",
      status: "retrieved",
      collection_concept_id: OSCAR_COLLECTION,
      doi: "10.5067/OSCAR-25F20",
      variable_order: ["u_east_m_s", "v_north_m_s"],
      dimension_order: ["time", "latitude", "longitude", "component"],
      shape: [nt, nlat, nlon, 2],
      time: { start_center_utc: "2014-03-08T12:00:00Z", step_days: 1, count: nt },
      latitude: { start_deg: -45.0, step_deg: 0.25, count: nlat, ascending: true },
      longitude: { start_deg: 80.0, step_deg: 0.25, count: nlon, ascending: true },
      effective_depth: "assumed well-mixed upper 30 m",
      units: "m s-1",
      missing_vector_count: u.reduce((sum, value, index) => sum + (!Number.isFinite(value) || !Number.isFinite(v[index]) ? 1 : 0), 0),
    });
  } catch (error) {
    const manifest = { schema_version: 1, source_family: "OSCAR v2 Final", status: "blocked_download_failed", error: String(error.message).replaceAll(/[^\x20-\x7E]/g, " ") };
    await writeFile(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
    return manifest;
  } finally {
    await rm(temporary, { recursive: true, force: true });
  }
}

async function copySources() {
  const sources = [
    {
      source: path.join(legacy, "corpus/papers/csiro-2017-ocean-drift-part-iii.pdf"),
      target: path.join(paperDir, "csiro-ocean-drift-part-iii.pdf"),
    },
    {
      source: path.join(legacy, "corpus/papers/geoscience-australia-2017-pleiades-imagery.pdf"),
      target: path.join(paperDir, "geoscience-australia-pleiades-imagery.pdf"),
    },
    {
      source: path.resolve(bundle, "../kadri-2024-hydroacoustics/data/seventh_arc_fl400.geojson"),
      target: path.join(dataDir, "seventh_arc_fl400.geojson"),
    },
    {
      source: path.join(legacy, "analyses/D-0043-generative-debris-drift/inputs/natural_earth_v5.1.2_50m_land.geojson"),
      target: path.join(dataDir, "natural-earth-v5.1.2-50m-land.geojson"),
    },
  ];
  for (const item of sources) await copyFile(item.source, item.target);
  await writeFile(path.join(paperDir, "oscar-v2-user-guide.pdf"), await fetchBytes(OSCAR_GUIDE));
  const cmr = await fetchBytes(`https://cmr.earthdata.nasa.gov/search/collections.json?short_name=OSCAR_L4_OC_FINAL_V2.0&page_size=10`);
  await writeFile(path.join(sourceDir, "oscar-v2-final-cmr-collection.json"), cmr);
}

async function runProcess(command, args) {
  await new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: "inherit" });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} exited with status ${code}`));
    });
  });
}

const cmemsStems = [
  "cmems-glorys12-surface-currents-20140308-24",
  "cmems-waverys-surface-stokes-20140308-23",
];

async function prepareCmemsFields() {
  const python = process.env.PLEIADES_DATA_PYTHON
    ?? path.resolve(bundle, "../..", ".venv/bin/python");
  await runProcess(python, [
    path.join(bundle, "code/prepare_cmems_fields.py"),
    "--output-dir", dataDir,
  ]);
}

async function loadCmemsFields() {
  const manifests = [];
  for (const stem of cmemsStems) {
    const filename = path.join(dataDir, `${stem}.manifest.json`);
    if (!(await exists(filename))) return [];
    const manifest = JSON.parse(await readFile(filename, "utf8"));
    if (manifest.status && manifest.status !== "retrieved") return [];
    manifests.push(manifest);
  }
  return manifests;
}

async function buildSourceManifest(manifests) {
  const relativeFiles = [
    "paper/csiro-ocean-drift-part-iii.pdf",
    "paper/geoscience-australia-pleiades-imagery.pdf",
    "paper/oscar-v2-user-guide.pdf",
    "data/seventh_arc_fl400.geojson",
    "data/natural-earth-v5.1.2-50m-land.geojson",
    "data/pleiades-rating5-objects.csv",
    "data/config.json",
  ];
  for (const relative of [
    "data/source-metadata/cmems-glorys12-2014-03-source-receipt.json",
    "data/source-metadata/cmems-waverys-2014-03-source-receipt.json",
  ]) {
    if (await exists(path.join(bundle, relative))) relativeFiles.push(relative);
  }
  const files = [];
  for (const relative of relativeFiles) {
    const bytes = await readFile(path.join(bundle, relative));
    files.push({ path: relative, bytes: bytes.length, sha256: sha256(bytes) });
  }
  const output = { schema_version: 1, generated_utc: new Date().toISOString(), datasets: manifests, source_files: files };
  await writeFile(path.join(dataDir, "input-manifest.json"), `${JSON.stringify(output, null, 2)}\n`);
}

await mkdir(sourceDir, { recursive: true });
await mkdir(paperDir, { recursive: true });
let bran;
let wind;
let oscar;
let cmems = [];
if (process.argv.includes("--cmems-only")) {
  bran = JSON.parse(await readFile(path.join(dataDir, "bran2016-surface-currents-20140308-23.manifest.json"), "utf8"));
  wind = JSON.parse(await readFile(path.join(dataDir, "ncep-ncar-r1-10m-wind-20140308-23.manifest.json"), "utf8"));
  oscar = JSON.parse(await readFile(path.join(dataDir, "oscar-v2-final-20140308-23.manifest.json"), "utf8"));
  await prepareCmemsFields();
  cmems = await loadCmemsFields();
} else if (process.argv.includes("--oscar-only")) {
  bran = JSON.parse(await readFile(path.join(dataDir, "bran2016-surface-currents-20140308-23.manifest.json"), "utf8"));
  wind = JSON.parse(await readFile(path.join(dataDir, "ncep-ncar-r1-10m-wind-20140308-23.manifest.json"), "utf8"));
  oscar = await fetchOscar();
  cmems = await loadCmemsFields();
} else {
  await copySources();
  bran = await fetchBran();
  wind = await fetchNcepWind();
  oscar = await fetchOscar();
  cmems = await loadCmemsFields();
}
await buildSourceManifest([bran, wind, oscar, ...cmems]);
console.log(JSON.stringify({
  bran: bran.status ?? "retrieved",
  wind: wind.status ?? "retrieved",
  oscar: oscar.status ?? "retrieved",
  cmems: cmems.length === 2 ? "retrieved" : "not_prepared",
}));

