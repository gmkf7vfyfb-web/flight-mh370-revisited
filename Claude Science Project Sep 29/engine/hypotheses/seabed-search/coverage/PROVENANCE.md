# Coverage layers: where each one comes from, and the footnote it must carry

Pete's ruling of 9 October 2026 (~18:30 UTC, `coordination/architecture.md`) withdrew the brief's
"never commit the traced outline" line: the Ocean Infinity outlines are used and committed, provided
every use carries the footnote below. This file is the single record of that.

| layer | source | grade |
|---|---|---|
| `phase2.cov`, `phase2-deep-tow.cov`, `phase2-go-phoenix.cov`, `phase2-dhj.cov`, `phase2-auv.cov` | Geoscience Australia published survey geometry (WFS and FeatureServer), fetched by `prepare/build_coverage.py` | official |
| `bluefin-2014.cov` | Geoscience Australia "area searched 2014" feature | official |
| `ocean-infinity-2018.cov` | **community tracing**, read from the frozen snapshot at `ISO Sept 28 Status/inputs/search-coverage/ocean-infinity-2018-outline.geojson` | **C** |
| `ocean-infinity-2025.cov` | **community tracing** of the two bands in Ocean Infinity's March 2024 presentation, read from the frozen snapshot at `Sept 27 2026 backup PL ChatGPT instance/2026-09-28_codex_drift_and_search_update/combined_panel_versions/search_footprints.geojson` | **C** |

## The required footnote

Any chart, table or statement that uses either Ocean Infinity layer carries, beneath it:

> Ocean Infinity coverage is **inferred, not official**: a community tracing (MH370-CAPTION, grade C)
> of published map imagery and vessel tracks. Ocean Infinity has released no survey geometry for
> either campaign. The layer is a planning envelope with a coverage fraction applied, not measured
> swath coverage, and the result is reported separately from the ATSB-only estimate, never merged
> into it.

## Why the tracings are read from the frozen snapshots rather than re-committed

Both files are already in this repository, inside the September snapshots, which are immutable. Taking
them from there gives one copy, a stable checksum, and a clean-clone build with no external fetch.
`ocean-infinity-2018-outline.geojson` in the snapshot is byte-identical to the working copy
(sha1 `4ab36299…`).

The ATSB layers are not affected by any of this: they are official geometry, they carry no such
footnote, and `run.toml` — the main estimate — contains no Ocean Infinity layer at all.
