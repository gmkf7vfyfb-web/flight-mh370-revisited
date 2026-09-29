# Ocean-drift scientific status

## Decision

The canonical ocean-drift spoke, data preparation, adaptive source estimator,
validation, runner integration, and deterministic reporting are implemented.
Native time-varying current and matched wave data are no longer blocked:
CMEMS GLORYS12V1 daily 1/12° currents and WAVERYS 3-hourly 0.2° surface
Stokes velocity cover 10°E–150°E, 50°S–30°N for the complete 2014-03-07
through 2015-07-30 interval. Current, Stokes, and direct windage remain
distinct.

GLORYS12 is the supported primary current-field diagnostic. It has better
matched drifter replay than retrieved native HYCOM and persistence. It is not,
by itself, a complete flaperon-motion model. The matched WAVERYS experiment
finds that a defensible 0.5×–1.5× surface-response range moves the source mode
from 11.91°S to 34.90°S and changes normalized source mass by total variation
up to 0.741. The nominal 1× seed/particle replication also moves its mode by
17 arc cells. Coastal termination changes sharply with response, while the
available coast field has no calibrated retention or refloating process.

Accordingly, the far-north mode is **not** a sufficiently robust alternative
to call prior drift studies wrong, and the southern response sensitivity is
not a calibrated confirmation of the flight posteriors. Publication-quality
plots and numeric diagnostics are delivered, but no ocean-drift evidence is
accepted into the central flight estimator and no new narrow combined crash
posterior is published. The existing currents-only family-conditioned report
remains explicitly diagnostic.

The bounded family-likelihood handoff now makes that decision executable. The
corrected native-HYCOM flaperon-response surface peaks at 36.97°S with a
32.16–41.97°S 90% diagnostic interval, but it covers only the Réunion episode,
has 45.66% likelihood-weighted out-of-support termination, and never reaches
arrival ESS 200. The stringent GDP run represents nine recovery episodes,
stochastic beaching-to-discovery delays, and two independent Australian
non-recovery populations. It peaks at 36.57°S, but 76.01% of its
likelihood-weighted paths are out of support and no source mass has all-event
ESS at least 200. Its one-cell 90% interval is rare-event collapse, not
publishable precision. Both handoff families are `diagnostic_only`.

## Delivered implementation

1. The 49-row isotope density ranking is replaced by a conservative
   compatibility screen conditional on an already represented confirmed
   flaperon arrival. It carries common isotope-temperature calibration and
   seawater uncertainty, SST field uncertainty, seven-day shell smoothing,
   14-day correlated residuals, and 115/154/192-day growth chronologies. Any
   compatible chronology is neutral. Marginal penalty is capped at ln(2);
   strong all-chronology rejection uses a 99.5% simultaneous envelope and is
   capped at ln(100). No path receives a positive isotope boost and the 49 rows
   are never multiplied as independent evidence.
2. Native HYCOM and authenticated CMEMS GLORYS12/WAVERYS retrievals are
   checksum-pinned with exact product/dataset/version, commands, units, time
   basis, coordinates, file hashes, and upstream attributes. The older
   approximately 0.96° HYCOM preservation remains a fallback diagnostic.
3. GDP remains a separately reported observational monthly climatology. No
   HYCOM/GDP mixture weight is invented; families are never pooled.
4. Rare-arrival brute force is replaced by deterministic keyed adaptive SMC.
   It stores proposal probabilities, exact correction weights, ancestor
   counts, and correction ESS. Two 20,000-replication synthetic fixtures
   recover known targets within their stated tolerances.
5. Transport distinguishes intermittent missing coverage, outside spatial
   support, persistent land encounter, beaching, outside-time support, and
   numerical failure. Schema 3 distinguishes intermittent missing from
   persistent land at interpolation corners. Failed paths remain in scoring;
   no missing value is converted to zero current.
6. Validation covers multiple years, 5/15/30-day horizons, three longitude
   regions, drogued/undrogued/transition targets, persistence and prior-
   velocity baselines, every attempted path, seed change, particle doubling,
   and 0.5×/1×/1.5× WAVERYS response. Assimilation/climatology leakage is
   stated explicitly.
7. Separate native HYCOM currents-only, GLORYS12 currents-only, GDP, and
   GLORYS12-plus-WAVERYS diagnostics and publication figures are generated.
   Because the complete-motion sensitivity is not stable, the central flight
   estimator is deliberately not rerun with accepted drift evidence.

The native-HYCOM surface represents only the confirmed flaperon because its
time support cannot cover the later evidence. The GDP stringent surface uses
nine recovery episodes from the audited 41-item list. It keeps the flaperon,
six exterior low-exposure pieces, and two uncertain interior panels in
separate motion families; no other object inherits the flaperon's measured
response or isotope record. The expanded 20-object audit remains a sensitivity
configuration and is not promoted after the stringent surface fails admission.

## Exact data identity

### Native HYCOM control

The public GOFS 3.1-like HYCOM+NCODA retrieval contains 501 native-grid
surface analyses with 21–30-hour spacing. Two exact analyses repair
stride-created 48/54-hour gaps. Its exact NCSS requests and source hashes are
in [`native-hycom-retrieval-manifest.json`](native-hycom-retrieval-manifest.json).

| Item | Value |
| --- | --- |
| Primary / supplemental tiles | 56 / 56 |
| Compressed source bytes | 1,619,404,694 |
| Retrieval manifest SHA-256 | `ef79539d15d75ed598bf27420013a7797462ea17ea5bce7573f4b714222ce742` |
| Packed current SHA-256 | `a0ac448d1f180cc591bfdb82ba07c904d33e1b953d6db7d796ea52052be3903f` |
| Persistent wet-mask SHA-256 | `b4471f0f9eba79a1d1f9aab958715e35659e548979dcf033f08a0a87efd2e2f2` |
| Independent check | 36 values, zero mismatches; receipt `a6bf86b4c4fa180a086ef8fa49d6c91012364d38efa05477a500f7a4bdfa0ed1` |

### CMEMS GLORYS12 currents

Product `GLOBAL_MULTIYEAR_PHY_001_030`, dataset
`cmems_mod_glo_phy_my_0.083deg_P1D-m`, contains 511 consecutive daily means
at the returned 0.49402499 m surface level. The 17 monthly files total
1,359,205,398 compressed bytes.

| Item | SHA-256 |
| --- | --- |
| Retrieval manifest | `0f031a8e850006341f4d88ce8c84e1ca4c3e55680003036cf7f5fc6747d8a766` |
| Aggregate monthly-file identity | `63d2e67f19b08b68e9df2d5b4e94d0dd0fc19d83d4e387543d9a971ea8668423` |
| Packed current field | `919405cbf4c03c257101794f977850df2385ac3ae976543858d59c480adb1470` |
| Current metadata | `363d203a7f67b8918ea4a7074676f2c97c89103a58aa43164864ea776cc23448` |
| Persistent wet mask | `fff1f2776117e98372f40811690c95110eac547a386e3b05f8d22d701b3981ae` |
| Independent 48-value check | `b79bafbebf9fc40c6e58630d7252ba57e69a534c352cc6961c510e4f142b5eab` |

The mask audit finds 526,262 persistently missing cells and 3,365
intermittently missing/changed cells over 1,021 component/time comparisons.
Only the former can be ignored during typed finite-corner interpolation.

### CMEMS WAVERYS Stokes

Product `GLOBAL_MULTIYEAR_WAV_001_032`, dataset
`cmems_mod_glo_wav_my_0.2deg_PT3H-i`, version `202411`, part `default`, was
retrieved with Copernicus Marine Toolbox 2.4.1. It contains 4,088 consecutive
3-hourly instantaneous `VSDX`/`VSDY` fields in m/s on a Gregorian UTC axis
from 2014-03-07 00:00 through 2015-07-30 21:00. The 17 files total
401,562,256 compressed bytes. Credentials were supplied through the secure
handoff and remain outside the repository; no value appears in a command or
manifest.

| Item | SHA-256 |
| --- | --- |
| Retrieval manifest | `4790a438a3938686e7b778e417ff6d9245f6d84be9f8a79e17c73aca07a59cd0` |
| Aggregate monthly-file identity | `d41a6bab685c085abf8f6175b012aa78aefb83b59d7250a53e8c8455cb40ade4` |
| Packed Stokes field | `ca98420ad3ee5d7a59d69c85d78e5ba8fc5216862c4c8e26357c1eeb7b9767fe` |
| Stokes metadata | `1ad6ad0a821ba83bcfb68c1a2bbe5cce958d39da6ed62ca3abce2ebd25fcf36b` |
| Persistent wave mask | `e9b97c21272bac674f9dba3dd28121e73775438e7eee8493c94770385c1ddec4` |
| GLORYS12/WAVERYS union coast | `1cb1a11df0a6c7b4d997e2ecec0aa4a13e86766787e910c58f8a2a9486b03cab` |
| Independent 48-value check | `eb5184d94687d4dfa6d8f6a53301f01d8a287441893bb415b57937c0b2076a58` |

The WAVERYS mask is invariant: 90,617 persistent cells, zero intermittent or
changed cells over 8,175 comparisons. The union coast field marks 529,441 of
1,615,441 GLORYS12-grid cells. It is a conservative model-support boundary,
not a measured shoreline or a beaching/retention/refloating model.

## Quantitative validation

Complete tables are in [`VALIDATION.md`](../VALIDATION.md). The central
findings are:

- GLORYS12 currents-only completes 98.8–99.8% of 600 attempted paths per
  year/horizon and beats persistence in 67.0–72.2%. It has lower matched
  median errors than native HYCOM.
- At 30 days, undrogued medians for currents-only / 0.5× / 1× / 1.5×
  WAVERYS are 317.7 / 274.8 / 245.2 / 292.9 km in 2014 and
  255.9 / 231.0 / 236.3 / 262.5 km in 2015. No response wins both years.
- The same Stokes addition degrades drogued-target replay, as expected for a
  15 m drogued current follower. Drogue states are never pooled to calibrate
  the surface flaperon.
- The 24-case replay took about 278 s wall time and peaked at 12,036,096 KiB
  resident memory.
- Nominal 1× source replications at 1,024 / 1,024 / 2,048 particles per cell
  have peak arcs 146 / 129 / 129, maximum arrival ESS 263 / 220 / 418, and
  pairwise total variation 0.232–0.283.
- In the doubled 1× run, 91.7% of source mass has arrival ESS at least 100
  and 82.6% has ESS at least 200. Its mean termination is 0.379% internal
  missing, 2.648% outside spatial support, 43.400% land encounter, and zero
  beaching/outside-time/numerical failure.
- The 0.5× / 1× / 1.5× response source modes are arc-119 (11.91°S),
  arc-129 (18.00°S), and arc-161 (34.90°S). Total termination is 10.685%,
  46.427%, and 60.932%; land encounter is the dominant change.
- Response pairwise total variation is 0.471 / 0.494 / 0.741, with 90% and
  95% equal-tail endpoints shifting by as many as 16 arc cells.
- The doubled 1× isotope counts are 96,061 compatible, 1,098 marginal,
  223 rejected, and 15,221 missing-SST/chronology paths. Removing the screen
  changes source mass by only `1.39e-7` total variation.

All attempted drifter paths and all importance-corrected source terminations
remain in the scores. HYCOM+NCODA and GLORYS12 are assimilative, WAVERYS
assimilates wave-height observations and uses GLORYS12 currents, and GDP is
derived from the drifter network. The replay is not guaranteed held out and
no model weights are inferred from it.

## What changed in the plots

The broadening after the isotope change is real probability support, not PDF
or PNG rescaling. The old isotope density ranking changed its debris-only
profile by total variation 0.6405 and operated on rare-arrival ESS near one.
The conservative screen supplies no positive boost and is nearly neutral.
Removing the artificial ranking therefore broadened the distribution. The
matched current-only profiles then isolated a separate confound: native HYCOM
and GLORYS12 current-only peak at 13.15°S and 14.37°S, while the old ~34°S
native plot had also included a coarse Stokes field.

The new WAVERYS results show that neither currents-only northern peak nor one
nominal complete-motion peak is robust. The football-field plot therefore
shows prior-study ranges beneath the current diagnostic rather than implying
that one lane supersedes the literature. All versions include 50%, 90%, 95%,
and 99% current intervals. The renderer's deterministic layout audit measures
the y-axis-title/tick-label gap and the remaining legend/footer bounds, fixing
the reported y-axis overwrite.

Publication outputs:

- WAVERYS nominal 1×:
  [PNG](source-comparison/cmems-glorys12-waverys-football-field.png),
  [SVG](source-comparison/cmems-glorys12-waverys-football-field.svg),
  [PDF](source-comparison/cmems-glorys12-waverys-football-field.pdf),
  [CSV](source-comparison/cmems-glorys12-waverys-source-comparison.csv), and
  [layout receipt](source-comparison/cmems-glorys12-waverys-source-comparison.json).
- Native HYCOM currents-only:
  [PNG](source-comparison/native-hycom-football-field.png),
  [SVG](source-comparison/native-hycom-football-field.svg),
  [PDF](source-comparison/native-hycom-football-field.pdf),
  [CSV](source-comparison/native-hycom-source-comparison.csv), and
  [layout receipt](source-comparison/native-hycom-source-comparison.json).
- GLORYS12 currents-only:
  [PNG](source-comparison/cmems-glorys12-football-field.png),
  [SVG](source-comparison/cmems-glorys12-football-field.svg),
  [PDF](source-comparison/cmems-glorys12-football-field.pdf),
  [CSV](source-comparison/cmems-glorys12-source-comparison.csv), and
  [layout receipt](source-comparison/cmems-glorys12-source-comparison.json).

The existing three-page
[family-conditioned PDF](family-conditioned-source-crash/family-conditioned-source-crash.pdf)
and its [PNG](family-conditioned-source-crash/family-conditioned-source-crash.png),
[SVG](family-conditioned-source-crash/family-conditioned-source-crash.svg),
[CSV](family-conditioned-source-crash/family-conditioned-source-crash.csv),
and [JSON receipt](family-conditioned-source-crash/family-conditioned-source-crash.json)
are currents-only mathematical intersections with the four converged flight
families. They are retained for comparison, not updated or relabelled as an
accepted combined posterior.

## Deterministic artifacts and hashes

All curated artifact hashes are in
[`ARTIFACT-SHA256.txt`](ARTIFACT-SHA256.txt). Each source run also carries a
manifest pinning the runner, resolved configuration, inputs, outputs, seed,
response, and executable hash, plus a runtime receipt.

- Nominal 1× replication:
  [summary JSON](cmems-glorys12-waverys-stability/stability-summary.json),
  [summary CSV](cmems-glorys12-waverys-stability/stability-runs.csv), and
  doubled-run [PNG](cmems-glorys12-waverys-stability/runs/doubled/source-area.png),
  [SVG](cmems-glorys12-waverys-stability/runs/doubled/source-area.svg),
  [PDF](cmems-glorys12-waverys-stability/runs/doubled/source-area.pdf),
  [JSON](cmems-glorys12-waverys-stability/runs/doubled/source-area.json),
  [CSV](cmems-glorys12-waverys-stability/runs/doubled/source-area.csv), and
  [manifest](cmems-glorys12-waverys-stability/runs/doubled/run-manifest.json).
- Response sensitivity:
  [summary JSON](cmems-glorys12-waverys-response-sensitivity/stability-summary.json),
  [summary CSV](cmems-glorys12-waverys-response-sensitivity/stability-runs.csv),
  and separate 0.5× and 1.5× runs under the same directory.
- Predictive replay:
  [human table](validation/waverys/waverys-current-trajectory.md),
  [overall CSV](validation/waverys/waverys-current-trajectory-overall.csv),
  [regional CSV](validation/waverys/waverys-current-trajectory-regions.csv),
  [drogue CSV](validation/waverys/waverys-current-trajectory-drogue-status.csv),
  and [resource receipt](validation/waverys/cmems-glorys12-daily-currents-validation-resource.json).

## Reproduction commands

Large NetCDF and MHGRID files remain outside the repository. The manifests and
metadata make them exactly re-retrievable and verify their identities.

```bash
python -m pip install copernicusmarine==2.4.1

set -a
source /secure/location/MH370-cmems.env
set +a

python .sources/ocean-drift-input-preparation/code/retrieve_cmems_glorys12.py \
  --output /data/mh370-cmems-glorys12 \
  --manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-glorys12-retrieval-manifest.json

python .sources/ocean-drift-input-preparation/code/retrieve_waverys.py \
  --output /data/mh370-cmems-waverys \
  --manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-waverys-retrieval-manifest.json

python .sources/ocean-drift-input-preparation/code/prepare_inputs.py \
  --cmems-glorys12-manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-glorys12-retrieval-manifest.json \
  --cmems-waverys-manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-waverys-retrieval-manifest.json \
  --combine-cmems-coast-support \
  --output /data/mh370-ocean-inputs-cmems

python .sources/ocean-drift-input-preparation/code/verify_native_field.py \
  --manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-glorys12-retrieval-manifest.json \
  --field /data/mh370-ocean-inputs-cmems/cmems-glorys12.mhgrid \
  --output /tmp/cmems-glorys12-spot-check.json --tiles 8

python .sources/ocean-drift-input-preparation/code/verify_native_field.py \
  --manifest \
    .sources/ocean-drift-input-preparation/outputs/cmems-waverys-retrieval-manifest.json \
  --field /data/mh370-ocean-inputs-cmems/cmems-waverys-stokes.mhgrid \
  --output /tmp/cmems-waverys-spot-check.json --tiles 8

cargo build --release -p mh370-runner \
  -p mh370-ocean-drift --example validate_current_trajectories

python .sources/ocean-drift-input-preparation/code/run_trajectory_validation.py \
  --runner target/release/examples/validate_current_trajectories \
  --family cmems_glorys12_daily_currents \
  --field /data/mh370-ocean-inputs-cmems/cmems-glorys12.mhgrid \
  --trajectory 2014:/data/gdp_6hour_2014.csv \
  --trajectory 2015:/data/gdp_6hour_2015.csv \
  --horizon 5 --horizon 15 --horizon 30 --attempts 600 \
  --stokes /data/mh370-ocean-inputs-cmems/cmems-waverys-stokes.mhgrid \
  --stokes-scale 0.5 --stokes-scale 1.0 --stokes-scale 1.5 \
  --renormalize-finite-current-corners \
  --renormalize-finite-stokes-corners \
  --maximum-interpolation-gap-hours 36 \
  --output /tmp/waverys-trajectory-validation

python .sources/ocean-drift-input-preparation/code/run_source_stability.py \
  --runner target/release/mh370 \
  --base-config \
    .sources/ocean-drift-input-preparation/outputs/cmems-glorys12-waverys-diagnostic.toml \
  --output /tmp/cmems-glorys12-waverys-stability \
  --case reference:3700019:1024 \
  --case alternate:3701019:1024 \
  --case doubled:3700019:2048

python .sources/ocean-drift-input-preparation/code/run_source_stability.py \
  --runner target/release/mh370 \
  --base-config \
    .sources/ocean-drift-input-preparation/outputs/cmems-glorys12-waverys-diagnostic.toml \
  --output /tmp/cmems-glorys12-waverys-response \
  --existing-case \
    full-surface:/tmp/cmems-glorys12-waverys-stability/runs/doubled:/tmp/cmems-glorys12-waverys-stability/configs/doubled.toml \
  --case half-surface:3700019:2048:0.5 \
  --case enhanced-surface:3700019:2048:1.5

python .sources/ocean-drift-input-preparation/code/compare_source_surfaces.py \
  --current /tmp/cmems-glorys12-waverys-stability/runs/doubled/source-area.json \
  --earlier \
    .sources/ocean-drift-input-preparation/outputs/demo-hycom-run/source-area.json \
  --comparators \
    .sources/ocean-drift-input-preparation/inputs/published-drift-comparators.csv \
  --output /tmp/cmems-waverys-source-comparison \
  --current-label "CMEMS GLORYS12 + 1x WAVERYS" \
  --current-description \
    "Daily 1/12-degree currents plus distinct 3-hourly 0.2-degree surface Stokes" \
  --output-stem cmems-glorys12-waverys
```

No ocean-drift-enabled central `estimate` command is part of the accepted
workflow because the evidence does not meet the scientific stability
requirement.

## Verification

The final verification commands are:

```bash
cargo fmt --all -- --check
cargo test -p mh370-ocean-drift
cargo test -p mh370-runner ocean_drift
cargo check --workspace --all-targets
cargo clippy -p mh370-ocean-drift --all-targets --no-deps -- -D warnings
cargo clippy -p mh370-runner --all-targets --no-deps -- \
  -D warnings -A clippy::too_many_arguments
python -m py_compile .sources/ocean-drift-input-preparation/code/*.py
.venv/bin/python \
  .sources/ocean-drift-input-preparation/code/report_family_conditioned_crash.py \
  --self-test
```

Focused ocean-drift tests include isotope limiting/synthetic fixtures,
schema-3 land-versus-intermittent-missing interpolation, explicit termination
reasons, Stokes response scaling, midpoint land detection, conditional source
evidence, and the two adaptive-SMC unbiasedness fixtures. Independent raw
NetCDF spot checks passed with zero mismatches. One external raw-field Rust
test remains ignored by default because it requires the non-repository
multi-gigabyte fields.

All listed checks passed on 27 August 2026. `cargo test --workspace` passed the
complete workspace suite; ocean-drift ran 18 unit tests plus 8 focused
integration/fixture tests, with only the declared external-field test ignored.
Both focused clippy invocations passed with warnings denied. The generated
Python bytecode cache was removed after verification.

## Changed canonical files

Product implementation:

- `crates/ocean-drift/src/field.rs`
- `crates/ocean-drift/src/isotope.rs`
- `crates/ocean-drift/src/lib.rs`
- `crates/ocean-drift/src/observations.rs`
- `crates/ocean-drift/src/sampling.rs`
- `crates/ocean-drift/src/source_area.rs`
- `crates/ocean-drift/src/transport.rs`
- `crates/ocean-drift/examples/validate_current_trajectories.rs`
- `crates/ocean-drift/tests/isotope_compatibility.rs`
- `crates/ocean-drift/tests/source_area_conditional.rs`
- `crates/runner/src/ocean_drift_commands.rs`
- `crates/runner/src/ocean_drift_application.rs`
- `README.md`

Source preparation, validation, and reporting:

- `.sources/ocean-drift-input-preparation/code/prepare_inputs.py`
- `.sources/ocean-drift-input-preparation/code/retrieve_cmems_glorys12.py`
- `.sources/ocean-drift-input-preparation/code/retrieve_native_hycom.py`
- `.sources/ocean-drift-input-preparation/code/retrieve_waverys.py`
- `.sources/ocean-drift-input-preparation/code/verify_native_field.py`
- `.sources/ocean-drift-input-preparation/code/run_trajectory_validation.py`
- `.sources/ocean-drift-input-preparation/code/summarize_trajectory_validation.py`
- `.sources/ocean-drift-input-preparation/code/run_source_stability.py`
- `.sources/ocean-drift-input-preparation/code/compare_source_surfaces.py`
- `.sources/ocean-drift-input-preparation/code/report_family_conditioned_crash.py`
- `.sources/ocean-drift-input-preparation/README.md`
- `.sources/ocean-drift-input-preparation/VALIDATION.md`
- `.sources/ocean-drift-input-preparation/outputs/` retrieval records,
  metadata, configurations, deterministic validations, plots, numeric tables,
  manifests, runtime receipts, status, and consolidated hashes.

No unrelated MH370 capability was integrated by this spoke.

## Remaining blockers and limitations

- Authentication is resolved. GLORYS12 and WAVERYS source files are fully
  retrieved and checksum-pinned.
- The main blocker is scientific: the flaperon's effective response to surface
  Stokes is not calibrated, and plausible response values produce source
  profiles with total variation up to 0.741 and modes spanning 11.91°S to
  34.90°S.
- The conservative union coast field is an absorbing model support boundary,
  not a calibrated beaching, retention, or refloating model. Land encounter
  changes from 10.3% to 53.2% over the response range.
- GLORYS12/HYCOM and WAVERYS are assimilative; GDP replay is not guaranteed
  held out. GDP climatology shares the drifter observation network.
- Some supported source cells still have arrival ESS below the requested
  hundreds, despite hundreds of effective arrivals across most high-mass
  cells.
- Full-global GLORYS12-plus-WAVERYS packing would require roughly 28 GB before
  runner overhead. The current host has 23 GiB RAM and regional runs already
  use about 11.5 GiB. The regional domain therefore remains canonical for this
  diagnostic and reports outside spatial support explicitly; it never fills or
  silently conditions on missing coverage.
- Diffusivity, recovery bandwidth/window, direct windage, and object-specific
  residual leeway remain explicit sensitivities rather than fitted parameters.
- This workspace has no `.git` metadata. Run manifests pin exact executable,
  input, configuration, and output hashes but cannot record a commit ID.

Until these limitations are resolved, the plots must remain labelled
diagnostic and must not be used to narrow the central flight posterior.
