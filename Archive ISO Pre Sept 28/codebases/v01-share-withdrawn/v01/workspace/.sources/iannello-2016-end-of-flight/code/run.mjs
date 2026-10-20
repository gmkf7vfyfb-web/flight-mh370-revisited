import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const INPUT = path.join(ROOT, "data", "cases");
const ARCHIVE = path.join(ROOT, "data", "boeing-eof-simulations-2018-08-19.zip");
const OUTPUT = path.join(ROOT, "outputs", "results.json");
const G_FTPS2 = 32.174;

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function parseCsv(file) {
  const lines = fs.readFileSync(file, "utf8").trim().split(/\r?\n/);
  if (lines.shift() !== "Time(sec),X(nm),Y(nm),Alt(ft)") {
    throw new Error(`Unexpected header in ${file}`);
  }
  const rows = lines.map((line) => {
    const [time_s, x_nm, y_nm, altitude_ft] = line.split(",").map(Number);
    if (![time_s, x_nm, y_nm, altitude_ft].every(Number.isFinite)) {
      throw new Error(`Non-finite row in ${file}: ${line}`);
    }
    return { time_s, x_nm, y_nm, altitude_ft };
  });
  rows.forEach((row, i) => {
    if (row.time_s !== i) throw new Error(`Non-sequential time in ${file} at row ${i}`);
  });
  return rows;
}

function distanceNm(a, b) {
  return Math.hypot(a.x_nm - b.x_nm, a.y_nm - b.y_nm);
}

function finiteMax(values) {
  return Math.max(...values.filter(Number.isFinite));
}

function auditCase(file) {
  const rows = parseCsv(file);
  const descentFpm = rows.map((_, i) => {
    if (i === 0 || i + 1 === rows.length) return Number.NaN;
    return ((rows[i - 1].altitude_ft - rows[i + 1].altitude_ft) / 2) * 60;
  });
  const acceleration1sG = descentFpm.map((_, i) => {
    if (i === 0 || i + 1 === rows.length) return Number.NaN;
    return ((descentFpm[i + 1] - descentFpm[i - 1]) / 2 / 60) / G_FTPS2;
  });
  const acceleration8sG = descentFpm.map((_, i) => {
    if (i < 4 || i + 4 >= rows.length) return Number.NaN;
    return ((descentFpm[i + 4] - descentFpm[i - 4]) / 8 / 60) / G_FTPS2;
  });
  const first15kIndex = descentFpm.findIndex((value) => value >= 15_000);
  const last = rows.at(-1);
  const peakDescentFpm = finiteMax(descentFpm);
  const peakAcceleration1sG = finiteMax(acceleration1sG);
  const peakAcceleration8sG = finiteMax(acceleration8sG);
  return {
    case: path.basename(file, ".csv").replace("Case ", ""),
    input_sha256: sha256(file),
    sample_count: rows.length,
    last_record: last,
    peak_descent_fpm: peakDescentFpm,
    peak_downward_acceleration_1s_g: peakAcceleration1sG,
    peak_downward_acceleration_8s_g: peakAcceleration8sG,
    exceeds_15000_fpm: peakDescentFpm >= 15_000,
    exceeds_067g_1s: peakAcceleration1sG >= 0.67,
    exceeds_067g_8s: peakAcceleration8sG >= 0.67,
    first_15000_fpm: first15kIndex < 0 ? null : {
      time_s: rows[first15kIndex].time_s,
      descent_fpm: descentFpm[first15kIndex],
      distance_to_last_record_nm: distanceNm(rows[first15kIndex], last),
    },
  };
}

const files = fs.readdirSync(INPUT)
  .filter((name) => /^Case [0-9]{2}[.]csv$/.test(name))
  .sort()
  .map((name) => path.join(INPUT, name));
if (files.length !== 10) throw new Error(`Expected 10 case files, found ${files.length}`);

const cases = files.map(auditCase);
const high1s = cases.filter((c) => c.exceeds_15000_fpm && c.exceeds_067g_1s);
const high8s = cases.filter((c) => c.exceeds_15000_fpm && c.exceeds_067g_8s);
const distances = high1s.map((c) => c.first_15000_fpm.distance_to_last_record_nm);
const finalAltitudes = high1s.map((c) => c.last_record.altitude_ft);

const result = {
  status: "REPRODUCED CASE CLASSIFICATION; DERIVED DISTANCE TO LAST RECORD, NOT IMPACT OR ARC DISTANCE",
  archive_sha256: sha256(ARCHIVE),
  conventions: {
    descent_positive: true,
    distance_unit: "nautical mile",
    altitude_unit: "foot",
    acceleration_reference_ft_s2: G_FTPS2,
    differentiation: "two-second centred vertical rate; two-second and eight-second centred acceleration sensitivity",
  },
  reported_comparator: {
    high_rate_cases: ["03", "04", "05", "06", "10"],
    distance_interval_nm: [4.7, 7.9],
  },
  derived: {
    high_rate_cases_1s_acceleration: high1s.map((c) => c.case),
    high_rate_cases_8s_acceleration: high8s.map((c) => c.case),
    distance_from_first_15000_fpm_to_last_record_nm: [Math.min(...distances), Math.max(...distances)],
    last_record_altitude_high_rate_cases_ft: [Math.min(...finalAltitudes), Math.max(...finalAltitudes)],
  },
  limitations: [
    "The files do not include latitude/longitude or seventh-arc geometry.",
    "The files do not identify each case's 00:19 alignment time or configuration metadata.",
    "The final records are 473–1,131 ft above the altitude datum in the high-rate cases, so they are not water-contact samples.",
    "The ten engineered cases have no sampling distribution or probability weights.",
  ],
  cases,
};

fs.writeFileSync(OUTPUT, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result.derived, null, 2));

