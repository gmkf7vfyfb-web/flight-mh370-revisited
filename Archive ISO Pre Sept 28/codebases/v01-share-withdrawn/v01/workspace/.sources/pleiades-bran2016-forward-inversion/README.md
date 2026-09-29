# Pléiades forward transport inversion

This source bundle reconstructs new, explicitly conditional transport
compatibility densities for the 8–23 March 2014 Pléiades observation window
under three explicitly alternative transport formulations: BRAN2016, OSCAR v2
Final, and GLORYS12 near-surface currents plus WAVERYS surface Stokes drift.
It does not identify any image object and is not imported by the canonical
MH370 runner.

## Scientific question

Given a declared source prior around the southern seventh arc, historical
surface currents, explicit windage alternatives, and unresolved dispersion,
which source cells most readily transport simulated debris to the published
locations of the twelve objects rated 5 (probably not natural objects or
features) by Geoscience Australia?

The four Pléiades scenes were captured near 04:00 UTC on 23 March 2014 and the
published object identities remain unknown. See
[CSIRO Part III](paper/csiro-ocean-drift-part-iii.pdf), printed p. 3
(PDF p. 9), and [Geoscience Australia Record 2017/13](paper/geoscience-australia-pleiades-imagery.pdf),
printed pp. 6 and 24 (PDF pp. 7 and 25).

CSIRO treated 0%, 1.2%, and 3% of 10 m wind speed as distinct leeway cases and
used a 5 NM/day random-walk scale for unresolved dispersion. See CSIRO Part
III, printed pp. 6 and 8 and Figure 3.4.3 (PDF pp. 12, 14, and 20).

CSIRO Part III propagated hypothetical debris forward from candidate impact
locations on 8 March and compared the simulated 23 March positions with the
Pléiades scenes. The implementation here is a separate clean-sheet
forward-ensemble reconstruction, not CSIRO code: it uses newly retrieved
BRAN2016 fields, an OSCAR v2 current-family control, and a near-surface
GLORYS12/WAVERYS response family. Forward propagation is
important because random-walk diffusion has no unique particle-by-particle
time reverse. This is a modelling rationale, not a claim that Griffin and Oke
used reversed stochastic diffusion; their reported comparison was also
forward-propagated. The located passages are recorded in the
[citation ledger](data/citation-ledger.md).

BRAN2016 supplies daily 2.5 m-layer currents on a regular 0.1° grid; the NCI
dataset stores packed velocities in m/s. These are data-file facts, audited
from the downloaded
[`u` attributes](data/source-metadata/bran2016-u.das) and
[`v` attributes](data/source-metadata/bran2016-v.das), rather than a claim
in the CSIRO report. The exact subset and decoded-binary hash are in
[`input-manifest.json`](data/input-manifest.json).

OSCAR v2 Final supplies daily 0.25° total currents averaged over an assumed
well-mixed upper 30 m. It is used as a structurally different current-family
control, not as an independent observation. The authenticated 8–23 March 2014
subset was retrieved on 24 August 2026 from PO.DAAC collection
C2098858642-POCLOUD and is pinned by SHA-256 in [the input manifest](data/input-manifest.json). See the official
[NASA CMR collection record](data/source-metadata/oscar-v2-final-cmr-collection.json)
and [OSCAR v2 guide](paper/oscar-v2-user-guide.pdf).

The third formulation uses daily GLORYS12V1 currents at the returned
0.49402499 m level on the native 1/12° grid and three-hourly WAVERYS surface
Stokes vectors on the native 0.2° grid. The converter extracts the exact
March 2014 time/space subsets without resampling and preserves upstream masks.
The source receipts and converted hashes are pinned in the
[input manifest](data/input-manifest.json). See the official
[GLORYS12](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description)
and [WAVERYS](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_WAV_001_032/description)
product records.

The wind control is the NOAA NCEP–NCAR Reanalysis 1 daily mean 10 m vector
product; units and averaging metadata are preserved in the downloaded
[`u` attributes](data/source-metadata/ncep-uwnd.das) and
[`v` attributes](data/source-metadata/ncep-vwnd.das).

## Why the model families differ from the recovered-debris work

Coverage is necessary but is not the main scientific explanation. BRAN2016
itself spans 1994–2016. It is used here first for method fidelity: Griffin and
Oke compared BRAN2015 and BRAN2016 for this same 15-day Pléiades experiment and
explicitly declined findings not supported by both. They described BRAN2016 as
a model-code update from MOM4 to MOM5 with no important physics change;
its closer fit to assimilated sea-level anomaly did not guarantee more accurate
surface velocity. The reconstruction uses BRAN2016, the later of that pair.
OSCAR was added here, not by Griffin and Oke, as a structurally different
global control. Its 0.25° upper-30-m diagnostic current is useful for
model-form sensitivity but is not a higher-resolution near-surface replacement.

The recovered-flaperon problem is different: transport lasts roughly 16 months
to a coast rather than 15 days to an offshore image scene. Later MH370 work
therefore provides a separate methodological lineage. [Nesterov (2018)](https://doi.org/10.5194/os-14-387-2018) used
daily assimilative HYCOM at 0.08°, while [Durgadoo et al. (2021)](https://doi.org/10.1080/1755876X.2019.1602102) combined
1/12° CMEMS currents with an explicit wave-model Stokes term. Over that longer
duration, accumulated wave/leeway error, coastal masks, recovery time and
archive completeness become especially important.

The local longer-duration workflow did not select GLORYS12 merely because it
is newer or nominally finer. Under a matched currents-only replay, its missing
trajectory mass was about 1.1%, versus 9.5–9.7% for the retrieved native HYCOM
family, and it performed better for matched undrogued drifter trajectories.
WAVERYS is the dynamically matched wave product because its wave calculation
uses GLORYS12 currents. Its full-surface Stokes velocity nevertheless remains a
response sensitivity for partly submerged debris, not a calibrated object
leeway model.

The new Pléiades GLORYS12/WAVERYS run imports that later, richer formulation
into the short-window experiment. It changes both the Eulerian-current product
and the explicit wave term, so its difference from BRAN or OSCAR cannot be
attributed to resolution alone. The common 0%, 1.2% and 3% windage cases are
retained; with explicit Stokes, non-zero windage must be interpreted as
additional direct wind response. Griffin and Oke's empirical windage could
also absorb wave effects absent from their current field, so the mixture is a
transparent response envelope and the zero-windage result is the clean
current-plus-Stokes control.

## Declared model

- Source support: the official FL400 seventh-arc reference from 32°S to 39°S,
  resampled every 5 NM, with cross-arc offsets from −100 to +100 NM every
  5 NM. Positive cross-arc displacement is eastward.
- Time: 2014-03-08 00:19 UTC to 2014-03-23 04:00 UTC.
- Advection: deterministic midpoint integration with a 3-hour step and
  bilinear space/linear time interpolation.
- Wind: NOAA NCEP–NCAR Reanalysis 1 daily 10 m vectors, multiplied by the
  declared windage factor.
- Waves: WAVERYS surface Stokes velocity is added explicitly only in the
  GLORYS12/WAVERYS response family.
- Dispersion: independent isotropic increments scaled so the two-dimensional
  daily RMS displacement is 5 NM in the primary family.
- Identity likelihood: a latent exactly-one-of-twelve premise with equal
  identity weights is integrated analytically. Every endpoint score is the
  arithmetic mean of twelve 10 km isotropic Gaussian kernels; no object is
  randomly sampled per particle or mask. This is a model choice, not an
  interpretation of the GA rating scale.
- Current families, object sets, kernel widths, windage factors, and diffusion
  scales remain explicit alternatives. Current-family densities are never
  multiplied as if they were independent evidence. A separately labelled
  equal-prior three-family model average is supplied as a sensitivity, not as
  an empirically calibrated model posterior.

The normalized result is a transport-compatibility PDF over the declared
source support. It is not a calibrated crash posterior because it lacks a
complete image detection/false-positive model, calibrated object-identity
prior, and flight-path prior.

## Result

All three transport families completed every primary trajectory: 192/192
particles at each of 5,289 source cells for each of three fixed seeds. OSCAR
contains 64 permanent mask vectors at four grid locations near
27.25–27.5°S, 81.25–81.5°E, but none intersects the source support or any
primary or sensitivity trajectory.

| Primary metric | BRAN2016 | OSCAR v2 Final | GLORYS12 + WAVERYS | Equal-prior average |
| --- | ---: | ---: | ---: | ---: |
| Mode | 35.417887°S, 92.885846°E | 34.916713°S, 92.047164°E | 35.391240°S, 92.162666°E | 35.217849°S, 92.246983°E |
| Cross-arc mode | 15 NM east | 35 NM west | 10 NM west | 15 NM west |
| Probability-weighted mean | 35.250058°S, 92.295173°E | 34.972435°S, 91.862137°E | 35.259658°S, 91.917835°E | 35.160717°S, 92.025048°E |
| 50% highest-density area | 7,203 km² | 6,088 km² | 6,002 km² | 9,518 km² |
| 90% highest-density area | 24,309 km² | 18,393 km² | 22,123 km² | 28,768 km² |
| 95% highest-density area | 30,012 km² | 22,980 km² | 28,640 km² | 35,671 km² |
| Mass within ±30 NM of arc | 68.3% | 46.4% | 63.5% | 59.4% |
| Mass east / west of arc | 47.2% / 46.2% | 4.8% / 90.9% | 12.0% / 80.6% | 21.3% / 72.6% |
| Mode distance from CSIRO 35.6°S, 92.8°E | 21.7 km | 102.2 km | 62.2 km | 65.7 km |

The family difference is material. Across the three component pairs, cellwise
total variation is **0.484–0.570**, mode separation is **53.8–94.4 km**, and
probability-weighted-mean separation is **32.3–50.0 km**. OSCAR and
GLORYS12/WAVERYS place much more mass west of the arc than BRAN. The component
PDFs therefore remain explicit alternatives. The fourth panel is their
declared equal-prior Bayesian model average, not an independent-evidence
product, Monte Carlo sampling error, or claim that equal family weights are
empirically established.

For the proposed one-to-five-object sensitivity, a decreasing prior
proportional to 16:8:4:2:1 was placed on the selected-object count. Conditional
on that count, subsets were uniform and their object-location likelihoods were
averaged. Every object's marginal weight is then exactly 1/5, so the resulting
five-object PDF is mathematically identical to the exactly-one equal mixture
(total variation 0). A joint/product likelihood is different and was not
computed because it requires correlated debris-survival, dispersion and
image-detection assumptions.

BRAN sensitivity remains material. Removing diffusion contracts its 90% region
to 5,745 km²; 10 NM/day expands it to 48,062 km² and shifts the mode 33.4 km.
The five-object morphology subset shifts the mode 20.8 km. Kernel-width mode
shifts are at most 13.1 km. Across individual BRAN seeds, maximum pairwise
total variation is 0.146, mean separation is 1.8 km, and mode separation is
13.1 km.

OSCAR shows the same qualitative diffusion dependence: its 90% region is
4,673 km² at 0 NM/day and 41,116 km² at 10 NM/day. Relative to its primary
mode, the zero-diffusion mode shifts 66.0 km, the 10 NM/day mode shifts
20.2 km, and kernel controls shift 18.6–29.2 km. The five-object subset retains
the same grid-cell mode. Across individual OSCAR seeds, maximum pairwise total
variation is 0.155 and mean separation is 3.0 km, but mode separation reaches
47.3 km. The OSCAR mode should therefore be read as a cell-scale maximum
inside a broad density, not a precise point estimate.

GLORYS12/WAVERYS has a 5,616 km² 90% region at 0 NM/day and 47,590 km² at
10 NM/day. Those controls move its mode by 20.7 km and 29.4 km, respectively;
the 5 km kernel moves it 13.1 km, while the 20 km kernel and five-object subset
retain the primary grid-cell mode. Across its individual seeds, maximum
pairwise total variation is 0.147, mean separation is 0.8 km, and mode
separation is 38.2 km. As with OSCAR, the single highest cell is less stable
than the broad density.

The three-family run took 1,730.2 s with six workers and used 1,232.8 MB maximum
resident memory. The plotted 50%, 90%, and 95% contours are calculated from
the genuinely two-dimensional source-cell probability; unlike the earlier
along-arc reconstructions, no transverse display kernel is added.

## Fuselage morphology extension

The earlier five-family screen excluded fuselage material. A separate
equal-budget sensitivity now adds the whole 63.6577 m shell, six documented
longitudinal section intervals and uniformly cut random sections. The NTSB intervals are treated as
reproducible structural boundaries, not preferred fracture planes.

The corrected object minima are two matched-random geometries, one ocean-control
fishing-net-or-rope mask, one random-pose wing and one documented section-47
mask. The whole shell is lowest for no object. The section-47 result for object
27 depends on partial visibility: its loss rises from 0.3058 to 0.3556 under
the fully visible restriction, above the 0.3145 random-geometry control. The
non-specific morphology conclusion is unchanged. See the
[fuselage source bundle](../pleiades-image-morphology-controls/README.md), its
[common-scale mask panel](../pleiades-image-morphology-controls/outputs/fuselage-common-scale-mask-panel.pdf)
and [extended loss comparison](../pleiades-image-morphology-controls/outputs/extended-family-loss-comparison.pdf).
The [published-PCA category panel](../pleiades-image-morphology-controls/outputs/published-pca-category-minima-panel.pdf)
shows each report PCA beside the five grouped category minima. The
[separate sketch sheet](../pleiades-image-morphology-controls/outputs/selected-777-full-and-matched-sketches.pdf)
shows the two aircraft-family object minima.

## Downstream likelihood-surface handoff

A versioned source-only handoff now separates prior-free relative
endpoint-compatibility fields from the normalized densities used for display.
BRAN2016, OSCAR v2 Final and GLORYS12/WAVERYS remain alternative conditional
proxies. The equal-prior surface is explicitly an uncalibrated sensitivity
mixture, not a calibrated model posterior or a fourth evidence item; it is
excluded from core likelihood composition. See the
[scientific contract](likelihood-handoff.md), [machine manifest](outputs/likelihood-handoff/manifest.json),
[common grid](outputs/likelihood-handoff/grid.csv), [long-format surfaces](outputs/likelihood-handoff/surfaces.csv),
[row schema](outputs/likelihood-handoff/likelihood-surface-schema-v1.json),
[browser comparison](outputs/likelihood-handoff/comparison.html),
[packaged SVG](outputs/likelihood-handoff/comparison.svg) and
[packaged PNG](outputs/likelihood-handoff/comparison.png).

## RNZAF-labelled image metadata context

The user-supplied workbook
[`2017-11-26-RNZAF-Image-Data.xlsx`](data/2017-11-26-RNZAF-Image-Data.xlsx)
(SHA-256 `267ad7be372e80dd7a81b6b8a356f3a3d47c8d5eb16bfb5fdb72c17d13570719`)
contains 183 image records. Of these, 132 have both coordinates and collapse to
59 distinct reported GPS positions; 51 have neither coordinate. Six rows carry
an E suffix in the latitude column and an S suffix in the longitude column.
The context renderer retains the numeric columns and records an explicit paired
suffix correction for those six rows.

These points are metadata locations only. They are not image footprints,
searched-area coverage, debris detections, negative-search evidence, or an
estimator likelihood. The workbook does not declare a datum, timestamp time
zone, altitude, camera orientation or field of view, search outcome, or dataset
completeness. The generated locator therefore remains display context and is
never consumed by the runner. Its third panel can accept the runner's separate
parent/conditional impact-particle CSV without changing that boundary. For the
v0.1 equal-family branch it prints the conditional ESS and labels the contours
`numerically unresolved · display only`, consistent with the canonical
[resolution audit](../../runs/mh370/release-v0.1/conditional/pleiades-resolution-audit.md).

View the generated [SVG](outputs/rnzaf-context/rnzaf-pleiades-impact-context.svg),
[PDF](outputs/rnzaf-context/rnzaf-pleiades-impact-context.pdf),
[PNG](outputs/rnzaf-context/rnzaf-pleiades-impact-context.png),
[normalized record table](outputs/rnzaf-context/rnzaf-image-metadata.csv), and
[machine summary](outputs/rnzaf-context/rnzaf-context-summary.json).

Artifacts:

- [accessible paper section](paper-section.md)
- [matching LaTeX fragment](paper-section.tex) and
  [BibTeX entries](paper-references.bib)
- [house-style vector PDF](outputs/pleiades-forward-impact-density.pdf)
- [SVG](outputs/pleiades-forward-impact-density.svg)
- [4,000 × 1,680 px PNG](outputs/pleiades-forward-impact-density.png)
- [separate normalized conditional densities](outputs/conditional-impact-density.csv)
- [equal-prior three-family density](outputs/model-averaged-impact-density.csv)
- [one-to-five identity-cardinality control](outputs/identity-cardinality-sensitivity.csv)
- [likelihood-surface handoff](outputs/likelihood-handoff/README.md)
- [complete summary](outputs/summary.json)
- [output hashes](outputs/manifest.json)

The four-panel map uses the established WSPR publication style and common
tight bounds of 90.0–94.0°E and 36.25–34.0°S. Text and line work remain vector in
the PDF and SVG; the PNG is exported at 200 dpi from the same Matplotlib figure.

## Reproduce

```bash
node code/fetch_data.mjs
node --test code/transport_core.test.mjs

python3 -m venv /tmp/pleiades-plot-venv
/tmp/pleiades-plot-venv/bin/pip install -r code/requirements-plot.txt
PLEIADES_PLOT_PYTHON=/tmp/pleiades-plot-venv/bin/python node code/run_inversion.mjs
node --test code/transport_core.test.mjs code/data_invariants.test.mjs

# Build and independently audit the downstream interchange contract:
node code/build_likelihood_handoff.mjs
node code/build_likelihood_handoff.mjs --check
node --test code/likelihood_handoff.test.mjs

# If BRAN/wind inputs are already pinned and only OSCAR needs refreshing:
node code/fetch_data.mjs --oscar-only

# Convert the checksum-pinned March GLORYS12/WAVERYS source files:
PLEIADES_DATA_PYTHON=../../.venv/bin/python \
  node code/fetch_data.mjs --cmems-only

# Render the RNZAF point-metadata locator. Add --conditional-particles with a
# runner-generated conditional-spatial-particles.csv to fill comparison panel C.
../../.venv/bin/python code/render_rnzaf_context.py \
  --workbook data/2017-11-26-RNZAF-Image-Data.xlsx \
  --grid outputs/likelihood-handoff/grid.csv \
  --surfaces outputs/likelihood-handoff/surfaces.csv \
  --surface-id equal_transport_family_model_average \
  --seventh-arc data/seventh_arc_fl400.geojson \
  --land data/natural-earth-v5.1.2-50m-land.geojson \
  --output-directory outputs/rnzaf-context

../../.venv/bin/python -B code/test_rnzaf_context.py
```
To regenerate only the figure and artifact manifest from an existing ensemble,
run `PLEIADES_PLOT_PYTHON=/tmp/pleiades-plot-venv/bin/python node code/run_inversion.mjs --render-only`.


OSCAR retrieval requires `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` in the
dotenv file named by `EARTHDATA_ENV` (default:
`/tmp/mh370-oscar-earthdata.env`). The fetcher never prints those values,
creates only a mode-0600 temporary netrc, and deletes that netrc after the
request. Remove the dotenv after the authenticated subset has been verified.
The credential file used for this run was removed.

## Integration status

Not integrated: this bundle must remain source-only until transport validation,
Monte Carlo convergence, object-identity calibration, and image
detection/false-positive modelling are adequate for a calibrated likelihood.
The interchange surfaces do not change that status; component fields are
conditional proxies and the equal-prior aggregate is sensitivity-only.
