# Ocean-drift input preparation

This directory converts attributed source data into the compact, typed field
format consumed by the canonical Rust `ocean-drift` spoke. Product code does
not depend on this directory. Schema 3 preserves intermittent missing ocean
cells as `-30000` and identifies only time-invariant land-mask cells as
`-29999`. The runner may renormalize a bilinear interpolation over finite
corners only when metadata declares that typed persistent-land sentinel;
intermittent missing data and sparse GDP coverage remain failures and are
never converted to zero velocity.

## Input identity and retrieval

- Native current sensitivity: public HYCOM NCSS access to the GOFS 3.1-like
  HYCOM+NCODA GLBv0.08 experiment 53.X reanalysis. The retrieval covers
  10°E–150°E, 50°S–30°N from 2014-03-07 through 2015-07-29 12:00 UTC at horizontal
  stride 1 (0.08° equatorward of 40° and 0.04° poleward) and the surface
  level. It keeps every eighth available three-hour analysis, audits the full
  time axis, and inserts exact analyses at 2014-06-29 12:00 UTC and
  2014-12-31 06:00 UTC where the stride created 48/54-hour gaps. The resulting
  native-grid sequence has 24–30-hour spacing but is not a daily mean. Official description:
  <https://www.hycom.org/dataserver/gofs-3pt1/reanalysis>. Exact NCSS request
  URLs, returned coordinates/times, byte sizes, SHA-256 hashes, units, and gap
  counts are in `outputs/native-hycom-retrieval-manifest.json` after retrieval.
- CMEMS GLORYS12V1 delayed-mode daily currents are the candidate primary
  time-varying family. Authenticated Copernicus Marine Toolbox 2.4.1 retrieval
  completed for 10°E–150°E, 50°S–30°N from 2014-03-07 through 2015-07-30,
  using `uo`/`vo` at the returned 0.49402499 m surface level. The 511 daily
  fields retain the native 1/12° grid and upstream missing values. Exact
  sanitized commands, versions, returned coordinates, time labels, units,
  per-file hashes, and global attributes are in
  `outputs/cmems-glorys12-retrieval-manifest.json`. Product page:
  <https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description>;
  authentication instructions:
  <https://help.marine.copernicus.eu/en/articles/8185007-copernicus-marine-toolbox-credentials-configuration>.
  A full evidence-domain retrieval also completed for 0°E–180°E,
  55°S–15°N, 2014-03-07 through 2017-01-31: 35 monthly files, 1,062 daily
  fields, 3,721,251,223 bytes, aggregate SHA-256
  `9016b8b4bc9f532b37e4919b759017eb1453fcaf9e1db008ed7757647c0b502e`.
  Its exact record is
  `outputs/cmems-glorys12-full-domain-retrieval-manifest.json`.

- HYCOM GLBu0.08 surface currents: the official product describes NetCDF
  output on a uniform 0.08° grid with eastward and northward velocities. The
  locally preserved regional extracts used here were subsequently resampled
  to approximately 0.96°, a material loss of spatial resolution. Official
  page: <https://www.hycom.org/data/glbu0pt08>.
- NOAA/AOML GDP monthly climatology: U and V are zonal/eastward and
  meridional/northward velocity in m/s; eU and eV are their standard errors.
  ClimatologicalMonth is 0=January through 11=December. Official data page:
  <https://erddap.aoml.noaa.gov/gdp/erddap/griddap/drifter_monthlymeans.html>.
  The preserved regional file is 0.5°; the current official dataset is 0.25°.
- NOAA daily OISST v2.1: the official product is a 1/4° daily blended analysis,
  not a point observation along a debris path. Official page:
  <https://www.ncei.noaa.gov/products/optimum-interpolation-sst>.
- ERA5 daily Stokes drift and NCEP-DOE Reanalysis 2 daily 10 m winds are
  converted as distinct velocity fields. The earlier native and GDP
  sensitivities use 100% of the coarse Stokes field and zero direct windage.
  The matched native/CMEMS source comparison is currents-only and therefore
  diagnoses current fields, not complete flaperon motion. An earlier replay
  pooled drogued and undrogued drifters and incorrectly suggested that the 1°
  field degraded skill overall. Correct separation shows improved CMEMS
  prediction for undrogued trajectories and severe degradation for drogued
  trajectories. The 1° field still has excessive coastal missing-data loss
  and is not accepted as the production Stokes input.
- The matched wave reanalysis is Copernicus WAVERYS
  `GLOBAL_MULTIYEAR_WAV_001_032`, dataset
  `cmems_mod_glo_wav_my_0.2deg_PT3H-i`: 3-hourly 0.2° `VSDX`/`VSDY` surface
  Stokes velocities. It uses GLORYS12 currents in the wave calculation and is
  the matched forcing tested with the GLORYS12 current family. Authenticated,
  checksum-pinned retrieval and conversion completed on 26 August 2026. With
  typed land-corner interpolation, internal missing loss is below 0.5%; an
  explicit union coast mask instead classifies 10–53% of source-weighted mass
  as land encounter depending on 0.5×–1.5× surface response. The corresponding
  source profiles differ by total variation up to 0.741. WAVERYS therefore
  remains a calibrated-response sensitivity, not an accepted production
  flaperon family; see `outputs/cmems-glorys12-waverys-response-sensitivity/`.
  A full evidence-domain retrieval also completed for 0°E–180°E,
  55°S–15°N, 2014-03-07 through 2017-01-31: 35 monthly files, 8,496
  three-hourly fields, 1,036,618,373 bytes, aggregate SHA-256
  `6d88e6da3205a22a053f413ec41e81609aac5fe3b98bc129965d794dd6b9c5fb`.
  Its exact commands, per-file hashes, returned coordinates, units, time basis,
  coverage, and assimilation limitation are recorded in
  `outputs/cmems-waverys-full-domain-retrieval-manifest.json`.
- CSIRO (2017), *The search for MH370 and ocean surface drift – Part II*,
  reports flaperon-specific leeway experiments and the relationship among
  undrogued drifters, Stokes drift, and windage.
- Durgadoo et al. (2021), DOI 10.1080/1755876X.2019.1602102, separates Stokes
  velocity from direct windage and documents the native 1/12° current product
  and recovery-date/location uncertainty used in its MH370 study.
- Al-Qattan et al. (2023), *A Stable Isotope Sclerochronology-Based Forensic
  Method for Reconstructing Debris Drift Paths With Application to the MH370
  Crash*, DOI 10.1029/2023AV000915. Full text:
  <https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2023AV000915>.

Large NetCDF inputs are not committed. Supply the exact files to the converter;
it records their paths and SHA-256 hashes in JSON sidecars. Legacy inputs are
preserved outside the product workspace, and native HYCOM tiles are
deterministically re-retrievable from the request URLs in the committed
manifest. CMEMS monthly files and packed fields likewise remain in external
cache/storage and are pinned by the committed manifest and metadata. Neither
location is a product runtime dependency.

## Family-specific likelihood handoff

The current bounded integration deliverable is generated without editing the
runner or central estimator:

```bash
python code/build_family_likelihood_handoff.py \
  --specification inputs/family-likelihood-handoff.json \
  --output outputs/family-likelihood-handoff

python code/query_family_likelihood.py \
  --handoff outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.json \
  --family native-hycom \
  --latitude -36.97 \
  --longitude 90.4
```

The JSON removes the source-cell prior before exposing the likelihood, uses a
single nearest-cell WGS84 query contract, and returns an explicit
`out_of_support` result beyond 75 NM. It preserves HYCOM and GDP as distinct
families and marks both current surfaces `diagnostic_only`; neither may update
the integrated estimator. See `VALIDATION.md` for the quantitative admission
failures and `outputs/family-likelihood-handoff/index.html` for the interactive
browser report.

The separate full-evidence-domain CMEMS handoff is generated from its
output-local specification and is never added to or averaged with the HYCOM/GDP
handoff:

```bash
python code/build_family_likelihood_handoff.py \
  --specification \
    outputs/cmems-full-domain-family-likelihood-handoff/specification.json \
  --output outputs/cmems-full-domain-family-likelihood-handoff
```

Its prior-removed conditional surface peaks at arc-152 (30.70°S), but the
machine decision is `diagnostic_only`: likelihood-weighted missing/outside
support is 1.746%, no surface mass has ESS at least 200 for every recovery,
and matched replication has total variation 0.394, interval-endpoint movement
up to six cells, and minimum highest-weight-set Jaccard 0.533. Predictive
replay and the conservative isotope screen pass their declared diagnostics;
they do not override the failed arrival/calibration diagnostics. The
browser-viewable result is
[`outputs/cmems-full-domain-family-likelihood-handoff/index.html`](outputs/cmems-full-domain-family-likelihood-handoff/index.html).

## Reproducible native retrieval and conversion

The native sequence is resumable tile by tile. The default command is the
canonical domain and period above:

```bash
python code/retrieve_native_hycom.py \
  --output /data/mh370-native-hycom-tiles \
  --workers 4

python code/prepare_inputs.py \
  --native-hycom-manifest \
    /data/mh370-native-hycom-tiles/retrieval-manifest.json \
  --output /data/mh370-ocean-inputs-native

python code/verify_native_field.py \
  --manifest /data/mh370-native-hycom-tiles/retrieval-manifest.json \
  --field /data/mh370-ocean-inputs-native/hycom-native.mhgrid \
  --output /data/native-hycom-spot-check.json
```

`hycom-native.mhgrid` preserves the upstream signed-int16 packing (0.001 m/s
scale and -30000 missing sentinel) to keep the full field practical. The
separate `hycom-native-coast.mhgrid` is a persistent model wet mask used only
to distinguish land encounter from intermittent field loss. It contains no
`beaching_rate`, so it cannot silently invent coastal retention. The canonical
configuration refuses to interpolate across current timestamps more than 36
hours apart; the audited and repaired sequence has a 30-hour maximum gap.

The verified local preparation used 56 primary and 56 supplemental tiles
(1,619,404,694 compressed bytes) and produced 501 native-grid analyses. Key
identities are:

| Artifact | SHA-256 |
| --- | --- |
| Retrieval manifest | `ef79539d15d75ed598bf27420013a7797462ea17ea5bce7573f4b714222ce742` |
| Packed native current field | `a0ac448d1f180cc591bfdb82ba07c904d33e1b953d6db7d796ea52052be3903f` |
| Current-field metadata | `905a98c4dde507a73874b232417915b0e9286e1f496cdba48f9ccb527da29579` |
| Persistent wet-mask field | `b4471f0f9eba79a1d1f9aab958715e35659e548979dcf033f08a0a87efd2e2f2` |
| Independent 36-value spot check | `a6bf86b4c4fa180a086ef8fa49d6c91012364d38efa05477a500f7a4bdfa0ed1` |

The spot check read raw NetCDF and packed MHGRID independently and found zero
mismatches. The manifest also pins the full archive time-axis ASCII responses:
2014 `41e08872079fcb5f3feb9984d99d1fe44ddbf0ebdb63d6375310274124b7f1de`
and 2015 `ce11abd49a261719da1a143d0a14117f87a1f34a1e0c0a87211cd0f5be708838`.

## CMEMS GLORYS12 retrieval and conversion

The earlier native-HYCOM source sensitivity terminated about 72% of
importance-weighted mass, but that run also included the separate coarse
Stokes field. A matched native-current-only control reduces termination to
9.5–9.7%. GLORYS12 was retrieved and tested as the more complete alternative;
its corresponding loss is about 1.1%, and it has better matched drifter replay.
It was not assumed to be better merely because it is another 1/12° assimilative
reanalysis.

`retrieve_cmems_glorys12.py` pins product
`GLOBAL_MULTIYEAR_PHY_001_030`, daily dataset
`cmems_mod_glo_phy_my_0.083deg_P1D-m`, Toolbox version, `uo`/`vo` units,
surface depth, UTC daily-mean basis, domain, dates, exact sanitized command,
file hashes, returned coordinates, finite fractions, and global attributes.
It retrieves one month at a time so completed files are resumable and
independently auditable. Credentials are consumed only from the official
environment-variable names and are never written to a command, manifest, or
repository file.

```bash
python -m pip install copernicusmarine==2.4.1

set -a
source /secure/location/MH370-cmems.env
set +a
python code/retrieve_cmems_glorys12.py \
  --output /data/mh370-cmems-glorys12 \
  --manifest outputs/cmems-glorys12-retrieval-manifest.json

python code/prepare_inputs.py \
  --cmems-glorys12-manifest outputs/cmems-glorys12-retrieval-manifest.json \
  --output /data/mh370-ocean-inputs-cmems

python code/verify_native_field.py \
  --manifest outputs/cmems-glorys12-retrieval-manifest.json \
  --field /data/mh370-ocean-inputs-cmems/cmems-glorys12.mhgrid \
  --output outputs/cmems-glorys12-spot-check.json \
  --tiles 8
```

The authenticated retrieval produced 17 monthly NetCDF files containing 511
consecutive daily fields and 1,359,205,398 compressed bytes. The packed current
field is 3.1 GB with scale 0.001 m/s, intermittent-missing sentinel `-30000`,
and persistent-land sentinel `-29999`; no missing value is converted to zero.
Across 1,022 component/time states, 526,262 cells are persistently masked and
3,365 are intermittently missing or change mask status. The latter always
remain data failures. The separate persistent wet mask has no beaching rate.
An independent check read eight raw NetCDF tiles and 48 component values and
found zero packed-field mismatches.

| Artifact | SHA-256 |
| --- | --- |
| Retrieval manifest | `0f031a8e850006341f4d88ce8c84e1ca4c3e55680003036cf7f5fc6747d8a766` |
| Aggregate monthly-file identity | `63d2e67f19b08b68e9df2d5b4e94d0dd0fc19d83d4e387543d9a971ea8668423` |
| Packed GLORYS12 current field | `919405cbf4c03c257101794f977850df2385ac3ae976543858d59c480adb1470` |
| Current-field metadata | `363d203a7f67b8918ea4a7074676f2c97c89103a58aa43164864ea776cc23448` |
| Persistent wet-mask field | `fff1f2776117e98372f40811690c95110eac547a386e3b05f8d22d701b3981ae` |
| Wet-mask metadata | `e7eb99fc4a126c189081e526359739b034dd20e17eaf23d679ceb1cb5bec12fe` |
| Independent 48-value spot check | `b79bafbebf9fc40c6e58630d7252ba57e69a534c352cc6961c510e4f142b5eab` |

CMEMS currents-only replay completed 98.3–99.8% of attempted paths and beat
persistence at every matched year/horizon. Long source-run missing coverage
fell to about 1.0–1.1%. These results support GLORYS12 over the retrieved native
HYCOM family as the current-field diagnostic, subject to assimilation leakage
and the separate object-motion limitations below.

## CMEMS WAVERYS retrieval, conversion, and coastal support

`retrieve_waverys.py` pins product `GLOBAL_MULTIYEAR_WAV_001_032`, dataset
`cmems_mod_glo_wav_my_0.2deg_PT3H-i`, version `202411`, part `default`, and
Toolbox 2.4.1. The 17 monthly files contain 4,088 consecutive 3-hourly
instantaneous fields from 2014-03-07 00:00 through 2015-07-30 21:00 UTC on a
Gregorian axis (`hours since 1950-01-01`). `VSDX` and `VSDY` are eastward and
northward surface Stokes velocity in m/s. The returned 0.2° grid covers
10°E–150°E, 50°S–30°N. Credentials are read only from the official
environment variables and are absent from commands, manifests, and outputs.

```bash
set -a
source /secure/location/MH370-cmems.env
set +a
python code/retrieve_waverys.py \
  --output /data/mh370-cmems-waverys \
  --manifest outputs/cmems-waverys-retrieval-manifest.json

python code/prepare_inputs.py \
  --cmems-waverys-manifest outputs/cmems-waverys-retrieval-manifest.json \
  --output /data/mh370-ocean-inputs-cmems

# Run after both GLORYS12 and WAVERYS support fields exist in this directory.
python code/prepare_inputs.py \
  --combine-cmems-coast-support \
  --output /data/mh370-ocean-inputs-cmems

python code/verify_native_field.py \
  --manifest outputs/cmems-waverys-retrieval-manifest.json \
  --field /data/mh370-ocean-inputs-cmems/cmems-waverys-stokes.mhgrid \
  --output outputs/cmems-waverys-spot-check.json \
  --tiles 8
```

The packed Stokes field is 4.3 GB. Its upstream mask is invariant across all
8,176 component/time states: 90,617 cells (32.236%, predominantly land) are
persistently masked, with zero intermittently missing or changed cells. The
independent raw-NetCDF check sampled 48 component values with zero mismatch.
The union coast field maps the 0.2° WAVERYS mask onto the GLORYS12 grid and
marks 529,441 of 1,615,441 cells as persistent support boundaries. It is an
absorbing model-support mask, not a measured shoreline or calibrated
beaching, retention, or refloating model.

| Artifact | SHA-256 |
| --- | --- |
| Retrieval manifest | `4790a438a3938686e7b778e417ff6d9245f6d84be9f8a79e17c73aca07a59cd0` |
| Aggregate monthly-file identity | `d41a6bab685c085abf8f6175b012aa78aefb83b59d7250a53e8c8455cb40ade4` |
| Packed WAVERYS Stokes field | `ca98420ad3ee5d7a59d69c85d78e5ba8fc5216862c4c8e26357c1eeb7b9767fe` |
| Stokes-field metadata | `1ad6ad0a821ba83bcfb68c1a2bbe5cce958d39da6ed62ca3abce2ebd25fcf36b` |
| Persistent WAVERYS mask | `e9b97c21272bac674f9dba3dd28121e73775438e7eee8493c94770385c1ddec4` |
| WAVERYS-mask metadata | `e157d1455f0984474ac22950b9a4ba564b5e16a250ada6ff8c0cfa0bc8c82585` |
| GLORYS12/WAVERYS union coast | `1cb1a11df0a6c7b4d997e2ecec0aa4a13e86766787e910c58f8a2a9486b03cab` |
| Union-coast metadata | `ead44535914a8539ac1ac2f7d9b9bee04d021caa85c1d4034e287125e2239371` |
| Independent 48-value spot check | `eb5184d94687d4dfa6d8f6a53301f01d8a287441893bb415b57937c0b2076a58` |

The regional packed fields are scientifically adequate for the represented
source mass: the 1× doubled run has 0.379% internal missing loss and the
normalized diagnostic source-mass-weighted outside-domain fraction is about
0.010%. The full evidence-domain GLORYS12 and WAVERYS fields have now also been
converted: 7,720,352,072 and 10,747,552,080 bytes respectively. Large packed
components use immutable unnamed file-backed mappings, avoiding a second
multi-gigabyte in-memory copy while preserving the same typed interpolation
path used by fixtures. The preserved reference scientific run, made before
that loader-only change, completed in 1,694.6 s at 11,724,316 KiB peak RSS.
Hash-pinned file-backed alternate-seed and doubled-particle replicas then
completed in 2,964.7/6,726.1 s at 12,424,696/12,432,604 KiB peak RSS under a
12 GiB memory limit. Exact conversion commands, versions, hashes, mask counts,
units, time bases, 165.1/790.4 s conversion runtimes, and memory are in
[`outputs/cmems-full-domain-conversion-receipt.json`](outputs/cmems-full-domain-conversion-receipt.json).

This removes authentication, upstream coverage, packing, and executable-memory
blockers. It does not make the source result admissible: missing and outside
support remain explicit termination reasons, and surface response, coastal
behavior, eventwise arrival ESS, and replication stability remain limiting.

## Source-area comparison and published context

The broader current map is a change in the source-mass profile, not a PDF or
PNG scaling change. The same reporting bounds and smoothing are used. The
earlier result used the coarsened field, 64 particles per cell, rare-arrival
ESS near one, and the superseded isotope density ranking. The current native
figure uses native HYCOM currents, distinct WAVERYS Stokes, and the measured
flaperon response of 0.10 m/s at 20° left of wind. Its comparison to the
earlier result is deliberately labelled not like-for-like. The separate
native-current-only and CMEMS comparison remains the matched current-field
control.

| Screened profile | Entropy-effective cells | 90% equal-tail width | 95% width | 99% width |
| --- | ---: | ---: | ---: | ---: |
| Earlier coarsened/density-ranked diagnostic | 5.91 | 8.95° | 9.73° | 9.73° |
| Native HYCOM + corrected flaperon response diagnostic | 28.87 | 9.80° | 12.89° | 16.68° |
| Current CMEMS GLORYS12 diagnostic | 25.17 | 20.16° | 21.64° | 22.12° |

For the corrected native flaperon-response run, removing the isotope screen
changes the normalized source profile by total variation `8.6313e-5`
(Jensen–Shannon divergence `8.67e-9` nats). In the matched native-current-only
control the total variation is `3.4331e-6`; for CMEMS it is `1.2101e-8`.
Equal-tail intervals are unchanged at reported precision. The conservative
isotope inclusion therefore neither causes nor cures the visible broadening.
The earlier density-ranked isotope term had total variation `0.6405` against
its debris-only profile and was scientifically overconfident.

The generated family-specific football-field figures place the current 50%,
90%, 95%, and 99% intervals above seven cited prior-study outputs. Those lanes
are labelled context only and are never pooled. Exact primary-paper passages
and hashes are in `PUBLISHED-COMPARATORS.md`.

```bash
python code/compare_source_surfaces.py \
  --current outputs/native-hycom-flaperon-response/source-area.json \
  --earlier outputs/demo-hycom-run/source-area.json \
  --comparators inputs/published-drift-comparators.csv \
  --output outputs/source-comparison \
  --plot-title "Native HYCOM flaperon response and published drift context" \
  --current-label "Native HYCOM + WAVERYS" \
  --current-description \
    "Native 1/12° currents, distinct WAVERYS Stokes, and measured 0.10 m/s extra flaperon response; diagnostic only" \
  --earlier-label "Superseded density-ranked result" \
  --output-stem native-hycom
```

Outputs are publication-quality
[`PNG`](outputs/source-comparison/native-hycom-football-field.png),
[`SVG`](outputs/source-comparison/native-hycom-football-field.svg), and
[`PDF`](outputs/source-comparison/native-hycom-football-field.pdf), plus a
numeric [`CSV`](outputs/source-comparison/native-hycom-source-comparison.csv)
and deterministic [`JSON receipt`](outputs/source-comparison/native-hycom-source-comparison.json).
The receipt includes a measured layout audit; the y-axis title clears its tick
labels by 59.8 pixels. The separate CMEMS outputs are
[`PNG`](outputs/source-comparison/cmems-glorys12-football-field.png),
[`SVG`](outputs/source-comparison/cmems-glorys12-football-field.svg),
[`PDF`](outputs/source-comparison/cmems-glorys12-football-field.pdf),
[`CSV`](outputs/source-comparison/cmems-glorys12-source-comparison.csv), and
[`JSON`](outputs/source-comparison/cmems-glorys12-source-comparison.json).

The WAVERYS 1× doubled diagnostic has its own
[`PNG`](outputs/source-comparison/cmems-glorys12-waverys-football-field.png),
[`SVG`](outputs/source-comparison/cmems-glorys12-waverys-football-field.svg),
[`PDF`](outputs/source-comparison/cmems-glorys12-waverys-football-field.pdf),
[`CSV`](outputs/source-comparison/cmems-glorys12-waverys-source-comparison.csv),
and deterministic
[`JSON layout receipt`](outputs/source-comparison/cmems-glorys12-waverys-source-comparison.json).
All three football-field figures render the same seven prior studies beneath
the current family, with 50%, 90%, 95%, and 99% current intervals. The layout
receipt measures y-axis-title/tick-label clearance, x-axis/legend clearance,
legend/footer clearance, and study-label canvas bounds. The global source
PNG/PDF broadening is a wider probability surface, not image scaling.

## Matched source families and candidate crash locations

The matched doubled runs remove the confound in the earlier plots. Native
HYCOM current-only peaks at 13.15°S and CMEMS current-only at 14.37°S. Their
profiles have total variation `0.3925` and Bhattacharyya coefficient `0.8861`:
the northern modes agree, while native HYCOM retains a broader southern tail.
The old native ~34°S peak was a native-current-plus-coarse-Stokes sensitivity,
not a currents-only result.

The matched WAVERYS experiment shows why neither currents-only northern mode
can be promoted to a crash estimate. At 2,048 particles per cell and the same
seed, 0.5×, 1×, and 1.5× surface response peak at arc-119 (11.91°S), arc-129
(18.00°S), and arc-161 (34.90°S). Pairwise source-profile total variation is
0.471–0.741, and 90%/95% equal-tail endpoints move by as many as 16 arc cells.
Within the nominal 1× response, changing seed and doubling particles shifts
the peak by 17 cells and leaves pairwise total variation 0.232–0.283. Broad
interval endpoints are steadier, but the response, coast interaction, and
local profile are not calibrated well enough to call any one mode a crash
site. These families are reported separately and are not pooled.

A source cell is a candidate crash point only conditional on the flaperon
being released at impact on the represented seventh arc at 00:19 UTC. It is
not an all-evidence crash estimate by itself because it does not enforce flight
feasibility. `code/report_family_conditioned_crash.py` therefore also computes
the family-conditioned mathematical intersection with the four converged
central flight posteriors. It exactly mirrors the runner's nearest-cell
composition and removes the source prior before applying the drift likelihood.
It does not pool current families or flight-control families.

```bash
source ../../.venv/bin/activate
python code/report_family_conditioned_crash.py
```

The drift-only modes are 13–14°S, whereas the four flight families occupy
31.8–36.5°S. Their intersections consequently use the weak southern drift
tails. Every CMEMS intersection and three of four native intersections put
material mass on source cells with fewer than 100 effective Reunion arrivals;
the CMEMS constant-true-heading intersection has post-hoc ESS `16.6`. The
result is delivered as a three-page diagnostic
[`PDF`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.pdf),
one-page [`PNG`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.png)
and [`SVG`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.svg),
numeric [`CSV`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.csv),
and deterministic [`JSON receipt`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.json).
It is not an accepted narrow crash posterior.

## Reproducible legacy-input conversion

The converter needs Python 3, NumPy, and netCDF4 only:

```bash
python code/prepare_inputs.py \
  --hycom /data/hycom_e910.nc /data/hycom_e911.nc /data/hycom_e912.nc \
  --gdp /data/gdp_monthlymeans.nc \
  --oisst /data/oisst_20150117_20150224.nc /data/oisst_20150225_20150729.nc \
  --isotope /data/Isotope_day2.csv \
  --stokes /data/era5_stokes_daily.npz \
  --wind-u /data/ncep_uwnd_2014.nc /data/ncep_uwnd_2015.nc \
  --wind-v /data/ncep_vwnd_2014.nc /data/ncep_vwnd_2015.nc \
  --source-arc /data/seventh_arc_fl400.geojson \
  --output /data/mh370-ocean-inputs
```

Outputs are `hycom.mhgrid`, `gdp.mhgrid`, `oisst.mhgrid`, `stokes.mhgrid`,
optional `wind.mhgrid`, their metadata sidecars, `source-cells.json`, and
`a2-g1-isotope.json`. The isotope converter loads exactly the 49
nonblank A2-G1 target rows. The preserved table contains reconstructed SST
rather than raw calcite isotope; the converter algebraically inverts Equation 2
with δ18Ow=0.4‰ so that the Rust implementation of Equation 2 reproduces that
published target. This retains the table's rounding and must not be described
as a new raw-isotope measurement.

## Citation ledger

| Claim used in code or configuration | Source and locator | Located passage | Status |
| --- | --- | --- | --- |
| GOFS 3.1 reanalysis identity, grid, period, and assimilation | HYCOM official GOFS 3.1 reanalysis page, product description and data sections | GLBv0.08 is the 1994–2015 1/12° reanalysis, 0.08° between 40°S and 40°N and 0.04° poleward, with three-hourly output and NCODA assimilation; known issues are listed. | FOUND |
| Exact public 2014–2015 subsets | HYCOM THREDDS experiment 53.X 2014 and 2015 catalogs | The yearly datasets expose OPeNDAP and NetCDF Subset services and their exact time coverages. | FOUND |
| GLORYS12 delayed-mode identity and access method | Copernicus Marine GLOBAL_MULTIYEAR_PHY_001_030 description/PUM pp. 5–8; Toolbox credential instructions | GLORYS12V1 provides daily 1/12° physical fields. Toolbox data access requires a Copernicus Marine username and password; the authenticated retrieval manifest records the returned 00:00 UTC coordinate labels. | FOUND |
| HYCOM source variables and native grid | HYCOM GLBu0.08 official page, lines 20–27 | The NetCDF is on a uniform 0.08° grid and provides eastward and northward velocity; the page also disclaims fitness for a purpose. | FOUND |
| GDP coordinate/component semantics | NOAA/AOML GDP ERDDAP metadata, lines 17–30 and 43–47 | The grid is 0.25°; U/V are zonal/meridional m/s, eU/eV are standard errors, and month values are 0–11 with 0=January. | FOUND |
| GDP climatology is observational and formal errors may be optimistic | NOAA/AOML mean-velocity page, lines 112–115, 146–155 | The monthly near-surface climatology is derived from satellite-tracked drifters; formal errors underestimated actual errors by about a factor of two in the cited toy evaluation. | FOUND |
| OISST identity and resolution | NOAA/NCEI OISST page, lines 86–92 | The product blends satellite and in-situ data with bias adjustment and identifies the 1/4° daily v2.1 reference. | FOUND |
| Flaperon leeway alternatives | CSIRO 2017 Part II, report pp. 7 and 10–12 (PDF pp. 13 and 16–18) | Leeway is current-relative wind/wave motion; undrogued GDP leeway was indistinguishable from modelled Stokes and close to 1.2% of wind speed; cut-down flaperon tests gave about 0.10 m/s extra leeway and a mean 16° leftward angle, while strong-wind fit remained limited. | FOUND |
| Stokes, windage, grid, and recovery uncertainty | Durgadoo et al. 2021, report pp. 3–4 (PDF pp. 4–5) | The study used 1/12° delayed-mode currents, separate 1/4° wave-model Stokes drift with a 100% central scale, negligible direct windage for a near-horizontal flaperon, and 1°×1°/30-day recovery uncertainty. | FOUND |
| Matched wave-reanalysis candidate | Copernicus Marine `GLOBAL_MULTIYEAR_WAV_001_032` product description and PUM | WAVERYS supplies 3-hourly 0.2° `VSDX`/`VSDY` surface Stokes velocity, uses GLORYS12 currents, and assimilates significant wave height. | FOUND |
| Isotope-to-temperature equation | Al-Qattan et al. 2023, section 3.1, Equation 2, lines 333–340 | T°C = 19.0 − 4.63[δ18Oc − (δ18Ow − 0.27)], N=43, R²=0.97. | FOUND |
| Recovery anchor and central chronology | Al-Qattan et al. 2023, section 2.5, lines 316–326 | The last value is anchored to 29 July 2015; inferred age is 154 days and colonization date is 25 February 2015. | FOUND |
| Chronology and record limitations | Al-Qattan et al. 2023, section 3.4, lines 378–386 | A2-G1 covers only several months; the age model is the most error-sensitive step; later shell samples have lower temporal resolution. | FOUND |

## Scientific limitations

- Native-grid HYCOM is now available, but it is an approximately daily
  subsample of three-hour analyses rather than a daily mean. Its validation is
  assimilative rather than guaranteed held out. Matched current-only source
  runs terminate 9.5–9.7% of importance-weighted mass; the earlier ~72% value
  belongs to the separate coarse-Stokes sensitivity. It remains a diagnostic
  family rather than an accepted primary field.
- CMEMS GLORYS12 is the best-performing time-varying current family in the
  available replay and materially repairs missing coverage. It is assimilative,
  so the GDP drifter replay is not guaranteed held out. It is supported as the
  current field, not as a complete flaperon-motion calibration.
- WAVERYS removes the coarse-field and authentication blockers, and its
  invariant mask permits typed finite-corner interpolation without filling a
  data gap. It does not remove the scientific blocker: 0.5×–1.5× surface
  response changes the source profile by total variation up to 0.741 and
  changes land encounter from 10.3% to 53.2%. The union coast field is an
  absorbing model mask with no measured retention or refloating process.
- Full evidence-domain GLORYS12-plus-WAVERYS packing and source simulation now
  complete with immutable file-backed packed components. The primary run uses
  18.47 GB of packed fields and peaks at 11,724,316 KiB RSS under the 12 GiB
  process limit. This solves the earlier loader-memory blocker, but the result
  still has 1.746% likelihood-weighted missing/outside support, 58.82% land
  encounter under the absorbing model-support mask, zero surface mass with
  ESS at least 200 for every recovery, and unstable seed/particle replication.
- The preserved ~0.96° HYCOM extract remains a diagnostic fallback only. It is
  not used by the native-field results.
- GDP is a monthly climatology, not the realized 2014–2015 current sequence.
  HYCOM and GDP are therefore separate model families, never samples from one
  interchangeable error distribution.
- BRAN2016 would be a useful Pléiades-family comparator, but its current NCI
  access terms require prior CSIRO registration and restrict use to
  government-funded research under a non-transferable, revocable licence.
  No full-period BRAN field was retrieved for this run. The exact terms URL and
  SHA-256 are recorded in `DEBRIS-EVIDENCE.md`; GLORYS12/WAVERYS is the
  explicit accessible alternative, not a claim that BRAN agrees with it.
- OISST coverage is required for every isotope time on a represented arrival
  path. Missing coverage is reported, not converted to zero probability.
- The isotope term is conditional on the already represented flaperon arrival:
  P(arrival) × P(isotope | arrival). It must not count Réunion recovery twice.
- The Rust isotope screen uses a simultaneous predictive covariance envelope
  with shared calibration/seawater uncertainty, correlated residuals, SST
  uncertainty, and shell smoothing. If any defensible chronology is compatible
  the path is neutral; if any chronology lacks coverage, all-chronology
  rejection is untestable and the path is also neutral. The 49 rows are never
  multiplied as independent likelihood terms.
- Stokes drift is a distinct physical field. If it is omitted from a run, the
  report must say so; scalar windage is not relabelled as Stokes drift. A
  drifter replay must also preserve drogue state: explicit surface Stokes is
  an appropriate sensitivity for undrogued surface motion, not for a drogued
  current follower. Neither currents-only nor currents-plus-Stokes alone
  substitutes for the flaperon's separately calibrated object leeway.
- The Gaussian encounter kernel and midpoint RK2 integrator are explicit model
  choices made here, not equations attributed to CSIRO, Durgadoo, or
  Al-Qattan.
- Complete multi-year validation tables and seed/particle replication results
  are in `VALIDATION.md`. CMEMS supports a broad diagnostic, but no family met
  the full calibration standard in the flight-supported southern tail. The
  family-conditioned crash report is therefore explicitly diagnostic and was
  not accepted into the central flight estimator.
