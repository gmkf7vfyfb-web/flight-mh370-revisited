# MH370 seabed-search evidence and planning sensitivity

This source-only package distinguishes mapped data, reported search totals, and
contextual reconstructions. It also provides a deterministic interface for
ranking a supplied weighted impact-particle population into an approximately
7,500 km² search plan. It is not an estimator input and it does not implement a
negative-search likelihood.

The central scientific boundary is unchanged: no polygon, approximate outline,
surface-vessel track, or bathymetry layer is a binary searched/not-searched
mask. Calibrated probability of detection (PoD), detailed sonar quality,
holidays, navigation/overlap and target-state inputs remain unavailable.

## Release artifacts

- [Evidence atlas](outputs/evidence-atlas.html), with matching
  [SVG](outputs/evidence-atlas.svg), [PDF](outputs/evidence-atlas.pdf), and
  [PNG](outputs/evidence-atlas.png).
- [Synthetic planner fixture](outputs/planning-fixture/index.html), with its
  [machine summary](outputs/planning-fixture/plan-summary.json) and
  [manifest](outputs/planning-fixture/run-manifest.json). This fixture tests the
  interface and is **not an MH370 estimate**.
- [Detailed browser audit](outputs/report.html).
- `data/area-inventory.json`: plotted/catalog, reported, and
  reported-but-unplotted quantities kept separate.
- `data/evidence-register.json`: evidence classes and explicit nulls for
  unavailable exact swaths, quality, holidays and PoD.
- `data/readiness.json`: release-readiness decisions and the limited
  15,000 − 7,571 = 7,429 km² arithmetic.
- `provenance/citations.json`: claim-to-located-passage ledger.
- `provenance/sources.lock.json`: retrieval URLs, hashes, sizes, licences and
  bundling decisions.

## Reproduce

From the repository root, rebuild every stable derivative and the synthetic
planner fixture, then validate all hashes and scientific invariants:

```bash
.venv/bin/python -B .sources/mh370-seabed-search-coverage/code/build.py build
.venv/bin/python -B .sources/mh370-seabed-search-coverage/code/build.py check
```

Matplotlib from the repository environment renders the publication SVG/PDF/PNG
sets. Source acquisition, geometry validation, planning calculations and hash
checks otherwise use the Python standard library. Output metadata and dates are
fixed for byte-identical regeneration.

To reacquire the redistributable GA/AusSeabed records from their official live
endpoints, requiring exact canonical hash matches before replacing any pin:

```bash
.venv/bin/python -B .sources/mh370-seabed-search-coverage/code/build.py acquire
```

A live-service mismatch is a review event, not permission to overwrite a pin.
Downloads are staged under a temporary directory and committed only if every
requested hash matches. Stable unbundled PDF identities can be checked without
retaining downloads with `verify-references`.

## Run against an impact population

The CSV contract is
`data/planning/weighted-particle-csv-schema.json`. It requires canonical WGS84
`latitude_deg` and `longitude_deg` columns and a caller-selected finite weight
column. Extra provenance and family columns are retained by the caller but are
not interpreted by this planner.

Example for linear weights:

```bash
.venv/bin/python -B .sources/mh370-seabed-search-coverage/code/build.py plan \
  --particles runs/<impact-run>/weighted-impact-particles.csv \
  --weight-column baseline_weight \
  --weight-mode linear \
  --label baseline-impact
```

For a log-weight handoff, use `--weight-mode log`. Run each conditional family
separately with a distinct label; do not pool BRAN2016, OSCAR, GLORYS/WAVERYS,
an uncalibrated mixture, or an ocean-drift diagnostic. If support or effective
sample size makes a result unsuitable for operational interpretation, attach
that explicitly:

```bash
.venv/bin/python -B .sources/mh370-seabed-search-coverage/code/build.py plan \
  --particles runs/<conditional-run>/weighted-impact-particles.csv \
  --weight-column conditional_weight \
  --label ocean-diagnostic \
  --branch-status diagnostic-only \
  --status-note "Insufficient support/ESS for operational ranking"
```

Each command writes under `outputs/planning-<label>/`:

- `ordered-tiles-posterior-only.csv`: all tiles in descending posterior KDE
  mass per area; rows after the first twelve are the extension sequence.
- `ordered-tiles-proxy-logistics.csv`: all tiles under the declared contextual
  sensitivity; the first twelve also carry a greedy within-set transit order.
- `selected-tiles.geojson`, `plan-summary.json`, and `run-manifest.json`.
- self-contained `index.html` and matching `search-plan.svg/.pdf/.png`.

Manifests use package-relative or `external-input/<basename>` logical paths and
never record host-specific absolute paths.

## Planning method and interpretation

The planner normalises the supplied particle weights, projects them locally
around their weighted centroid, evaluates a deterministic isotropic 35 km
Gaussian KDE at the centres of 25 km × 25 km tiles, truncates evaluation at four
standard deviations, and renormalises grid mass. Twelve tiles therefore equal
7,500 km² exactly.

The posterior-only plan ranks by KDE mass per square kilometre. The separate
proxy/logistics sensitivity multiplies that ranking score by declared soft
opportunity factors for official source/display footprints, grade-C OI context
outlines, and proximity to surface-vessel AIS tracks. These factors are
subjective scenarios—not PoD, likelihood ratios, or evidence that a target is
absent. A greedy transit heuristic orders the selected sensitivity tiles; it is
not a globally optimal vehicle route or a costed offshore survey plan.

Both outputs default to `sensitivity_not_operational`. They become operationally
defensible only after review of terrain, weather, transit/base constraints,
exact prior-search swaths, valid-data quality and a calibrated detection model.

## Evidence interpretation

The pinned GA/AusSeabed WFS exposes three Phase-2 level-0 coverage records:

- Deep Tow: a detailed official data-footprint geometry with gaps and small
  parts.
- Dong Hai Jiu 101: a coarse official catalog footprint.
- GO Phoenix: an official rectangular catalog extent.

Their catalog area attributes overlap and are never summed. The official GA
Bluefin application layer contains two display polygons whose spherical display
area is 771.410 km². ATSB reports 860 km² for the campaign; the 88.590 km²
difference and the individual mission swaths remain unplotted. The polygons are
therefore labelled as display support, not a valid-data mask.

No exact public Ocean Infinity AUV swaths were obtained. The preserved 2018 and
March-2024 outlines and the 2025–2026 surface-vessel tracks are grade-C context
with visible dashed/dotted symbology. Reported totals remain separate: more than
112,000 km² for the 2018 operation in the earlier operator statement, 120,000
km² in later dataset context, and approximately 7,571 km² for the 2025–2026
operation. The estimated 15,000 km² contract scale minus 7,571 km² gives 7,429
km² only as rounded arithmetic, not as an exact remainder polygon.

## Readiness

- Negative-search likelihood: **not ready**.
- Posterior-only and proxy/logistics tile planning: **ready as explicit,
  non-operational sensitivities**.
- Calibrated search optimization: **not ready**.
- Exact OI remainder polygon: **not available**.

See the citation ledger for exact located source passages and the evidence
register for the machine-readable interpretation of every geometry.

## Attribution

Bundled Geoscience Australia/AusSeabed material is © Commonwealth of Australia
and released under Creative Commons Attribution 4.0 International unless its
record says otherwise. Feature metadata identifies ATSB as data owner for
relevant records and states the data are not for navigation. ATSB, Ocean
Infinity, Malaysian Ministry and community pages are linked and hash-pinned
under their recorded redistribution decisions; legacy reconstructions are
retained only with explicit grade-C warnings.
