# Cowling arrival sampling under fixed physical assumptions

The 1,024-path comparison is complete. It uses four source cells selected near 30, 32.5, 35 and 37.5°S before seeing its results, both 365- and 540-day numerical guidance, and two seeds. Transport, Stokes, diffusion, coastline, object-response and discovery-delay settings are identical. This is a numerical control of one recovery; its four-cell weights are not a full impact PDF.

The centred, equally weighted, between-seed log-score RMS is 2.9885 with 365-day guidance and 0.9597 with 540-day guidance. Earlier guidance is promising, but one or two initial paths still dominate the southernmost source. Recovery-weighted ancestry groups resampled descendants by their initial path. This concentration measure is not an independent sample count or calibrated standard error.

The archived-seed baseline exactly reproduces all four recovery-score objects and shared event-ensemble diagnostics. `archived-baseline-check.json` names and hashes the earlier output. New ancestry fields were additive; the proposal and physical scoring did not change. The canonical ocean checks passed: 35 active tests, four explicitly ignored external-field fixtures; Cargo formatting also passed.

The fourfold follow-up is specified in `effort-design.json`: 4,096 original paths per cell, both guidance starts, fresh seeds 37093011 and 37093012, and the same four source positions. Its actual progress is `effort-status.json`; completion creates `effort-summary.json` and regenerates the browser. Read those files for current state. The correction is a larger original-path population, justified by measured ancestral concentration and initial guidance improvement. Neither a convergence threshold nor a new physical delay prior is imposed.

## Reproduction

The fixed queues refuse existing output directories and use a creation lock. Do not rerun them in place. Each run records its exact canonical command, config/input/executable identities, elapsed time, and peak memory. For one numerical member with a fresh destination:

```bash
RAYON_NUM_THREADS=2 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/cowling-arrival-sampling/mh370 estimate-ocean-drift --config /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/cowling-arrival-sampling/configs/paths4096-guidance-365-seed-37093011.toml --output /tmp/mh370-cowling-reproduction
```

The frozen `mh370` and `source-snapshot.tar.gz` retain the inference implementation. The original pilot queue source is preserved in `pilot-driver-source.tar.gz`; the current queue and report sources are recorded in `report-and-queue-source-identities.json`. The deterministic assessment and browser regeneration command is in `../flight-drift-comparison/README.md`. Its current numerical comparisons leave all original flight/drift weights intact, as checked in `report-verification.json`.

## Completed larger control and active full-grid extension

The fourfold comparison completed with centred log-score RMS 0.4922 (365 days) and 0.1496 (540 days). The full-grid extension is `arc-design.json`, with actual state in `arc-status.json`. It computes 73 remaining cells for each seed and retains four completed cells, without repetition. Completion creates `arc-summary.json`; the report verifies physical configurations, field hashes, exact 77-cell coverage and the join before displaying per-cell contributions. A focused split/join control using actual completed records is in `full-grid-reader-control.json`. No original joint impact weights have changed.

Some frozen fourfold configuration display names still contain the pilot seed phrase. Their numeric seed fields, manifests and run labels identify the actual independent seeds; the input identities remain frozen. Full-grid configuration names have the correct seeds and sample counts.
