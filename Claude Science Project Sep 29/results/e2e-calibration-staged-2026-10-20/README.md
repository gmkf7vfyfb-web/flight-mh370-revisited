# End-to-end calibration, staged run — started 20 Oct 2026 20:29Z on deskstar

Pete's rulings (protocol §12, 20 Oct 2026): A1, A2, A4, A5 adopted; A3 (scale) held; a STAGED run instead of the full
100 + 40 first: 30 tier 1a′ cases at 4 × 3.5 M particles, extendable to 50 and later to the full run with the same seeds and pool.
§6.3 (ranked-block table) may be built provisionally on the 30-case result, footnoted "provisional; calibration at reduced depth".

## What runs
One detached, resumable driver on deskstar: `~/mh370/e2e/calib_driver.sh` (copy in `scripts/`). It holds the heavy lock
(`flock ~/.mh370-heavy.lock`) for the whole run and does, in order:

0. Self-test: mini pool (1,000 replicates) and one toy case (2 × 50 k particles) through truth → inference → scoring; aborts on failure.
1. Shared truth pool (A2): 300,000 single-particle fuel-only prior replicates, seeds 5,000,001–5,300,000, in chunks of 1,000 at 80 threads
   (≈ 15–20 s per 500 → ≈ 2.5–3 h). Per chunk: `chunk-NNNNN.npz` (fuel weight, hand-off row, state and deterministic BTO/BFO prediction
   per cruise epoch per candidate) and `chunk-NNNNN-handoff.tar` (the hand-off header and rows of every replicate, header gzipped).
2. Cases on two lanes of 44 threads (11.3 GB RSS each, inside the 36 GiB cgroup cap): first case 39005 (generator re-check on the
   seed-9005 stream — a NEW truth under the corrected generator, reported apart from the main set), then tier 1a′ cases 3001–3030.

Per case (`case_pipeline2.sh`):
- truth: `pick_truth_pool.py` draws, with the case seed, the constant BFO bias b ~ N(150, 25) and the measurement noise for every pool
  candidate, applies the data-only event (A1 tier 1a′), and keeps the accepted set resampled to ≤ 400 distinct candidates with weights;
  `truth_eof_pool.sh` flies the end-of-flight production recipe for EVERY accepted candidate (192 descents per hand-off row);
  `pick_flight.py` chooses the flight with weight × Z(parent) (S2 fix; Z = marginal 00:19 log-on likelihood of the hand-off row);
  `make_synth.py` (unchanged) draws the descent within that parent ∝ weight × likelihood, so (flight, descent) is a joint draw from
  prior × log-on likelihood; it then makes the synthetic 00:19 bursts, drift finds and search outcome.
- infer: `infer_case_lane.sh`, 4 replicates × 3.5 M particles (`[500_000, 250_000, 1_250_000, 250_000, 1_250_000]`), 20,000 hand-off rows,
  production end-of-flight recipe, pruned at once (low-disk mode).
- score: `score_case.py` with the A4 rule patched in (`patch_score_a4.py`): the drift stacks (core+drift, all) are scored only if the pooled
  D0 core posterior puts ≥ 0.99 of its mass inside the drift node span — a function of the data only, so rank statistics stay valid;
  `truth_inside_drift_nodes` is kept as a diagnostic.

Tier 1a′ event (A1): synthetic BTO within ±500 µs and BFO within ±50 Hz of the real values at 00:11 (BTO 18,040 µs, BFO 252 Hz) AND at
22:41 (BTO 14,540 µs, BFO 204 Hz): `m0011.bto:17540:18540,m0011.bfo:202:302,m2241.bto:14040:15040,m2241.bfo:154:254`.
The event depends on the data only, so the test is simulation-based calibration conditional on the event (reported as such).

## Where the results are (on deskstar) — nothing depends on a live Claude session
- `~/mh370/e2e/calib-2026-10-20/case-stats/case-N/` — per finished case: `case-stats.json`, `truth.json`, `truth-core.json`,
  `truth-candidates.json` (epochs stripped), `walltimes.txt`, `hist.json`, `memory-events.txt`.
- `~/mh370/e2e/calib-2026-10-20/progress.csv` and `STATUS.txt` — rebuilt after every case by `aggregate.py`.
- `~/mh370/e2e/calib-2026-10-20/driver.log`, `lane-A.log`, `lane-B.log`, `pool.log`, `selftest-*.log`, `failed.txt`, `driver-starts.txt`.
- `~/mh370/e2e/timeline.txt` — one line per event (`tl`).
- `~/mh370/e2e/pool/` — the shared pool (keep: the 50-case and full runs reuse it; `COMPLETE` records NREP, chunking and seed base).

## If the run stops (session limit, reboot, OOM)
Everything finished stays on disk. Restart with exactly:

    cd ~/mh370/e2e && setsid nohup bash calib_driver.sh >> calib-2026-10-20/driver.log 2>&1 < /dev/null &

It skips the self-test (`SELFTEST-OK`), finished pool chunks (`chunk-*.npz` present) and finished cases (`case-stats/case-N/case-stats.json`),
removes stale claims, and continues. Check first that no driver is alive: `pgrep -af calib_driver`. Check `cat /sys/fs/cgroup/memory.events`
for `oom_kill`. Disk guard: a lane stops if `/home/pete` has < 8 GB free (29 GB free at start; a case peaks near 6.5 GB; the pool ≈ 2–4 GB).

## To extend to 50 cases
Edit `CASES` in `calib_driver.sh` to `39005 $(seq 3001 3050)` and restart as above; cases 3001–3030 are skipped as finished. Same pool, same seeds.

## Reporting rules
30 cases at half production scale: the 95 % binomial band on a 90 % coverage is about ±11 points. Any statement built on it carries
"provisional; calibration at reduced depth (30 cases, 4 × 3.5 M particles)". Case 39005 is not pooled with 3001–3030. Monte Carlo SD
between replicates and ESS per case are in `case-stats.json`; the §8 criteria (≥ 1,000 effective parents, rank SD ≤ 0.05) are checked per case.
