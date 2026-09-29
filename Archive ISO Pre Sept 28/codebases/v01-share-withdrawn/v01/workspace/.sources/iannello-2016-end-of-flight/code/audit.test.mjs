import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const result = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "results.json"), "utf8"));

test("archive identity is frozen", () => {
  assert.equal(result.archive_sha256, "e400ac73478dff8698cd344a69d7969804f6adb0eb2121d5cacd3b58d63111db");
});

test("reported five-case classification is reproduced under both windows", () => {
  const expected = ["03", "04", "05", "06", "10"];
  assert.deepEqual(result.derived.high_rate_cases_1s_acceleration, expected);
  assert.deepEqual(result.derived.high_rate_cases_8s_acceleration, expected);
});

test("distance-to-last-record interval agrees with the rounded report", () => {
  const [minimum, maximum] = result.derived.distance_from_first_15000_fpm_to_last_record_nm;
  assert.ok(Math.abs(minimum - 4.7) <= 0.15, `${minimum} differs from 4.7 NM`);
  assert.ok(Math.abs(maximum - 7.9) <= 0.15, `${maximum} differs from 7.9 NM`);
});

test("last records are not mislabeled as water impact", () => {
  const [minimum, maximum] = result.derived.last_record_altitude_high_rate_cases_ft;
  assert.equal(minimum, 484);
  assert.equal(maximum, 1131);
  assert.ok(result.status.includes("NOT IMPACT OR ARC DISTANCE"));
});

