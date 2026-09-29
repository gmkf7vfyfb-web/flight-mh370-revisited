# Ocean-current and source-area validation

## Outcome

CMEMS GLORYS12V1 is the supported primary *current-field diagnostic*. It has
the best matched currents-only drifter replay, retains 98.8–99.8% completion in
the canonical regional replay, and materially improves on native HYCOM and
persistence. Native HYCOM, GLORYS12, and GDP remain separate families; no
subjective mixture weights are used.

The matched complete-motion experiment does **not** yet support an accepted
crash posterior. Copernicus WAVERYS 3-hourly 0.2° Stokes velocity was retrieved,
converted, independently checked against raw NetCDF, and kept distinct from
currents and direct windage. In 30-day undrogued drifter replay, 1× surface
Stokes is best in 2014 while 0.5× is slightly best in 2015. More importantly,
the matched 2,048-particle source runs move their mode from 11.91°S at 0.5× to
34.90°S at 1.5×, with pairwise total variation up to 0.741 and 90%/95%
equal-tail endpoint shifts up to 16 arc cells. The nominal 1× seed/particle
replication still moves the mode by 17 arc cells and has total variation
0.232–0.283.

Those variations are model sensitivity, not posterior sampling error. The
flaperon's response to surface Stokes, coastal retention/refloating, residual
object leeway, diffusivity, and the recovery kernel are not independently
calibrated. The deterministic PNG, SVG, PDF, CSV, JSON, manifests, validation
tables, and runtime receipts are retained as diagnostics. No ocean-drift
surface was accepted into the central flight estimator, and no new narrow
crash posterior was published.

The later full-evidence-domain experiment removes the earlier field-coverage
and loader-memory uncertainty. It uses daily native-grid GLORYS12 currents and
three-hourly WAVERYS Stokes over 0°E–180°E, 55°S–15°N through 31 January 2017,
the same nine recovery episodes and two Australian non-recovery populations,
and the same object-response and isotope assumptions as the regional family.
The reference/alternate/doubled runs peak at arc-152/156/154. The reference
prior-removed surface peaks at 30.70°S with a 90% equal-tail interval of
29.70–35.75°S. This is still not an accepted crash posterior: the exact surface
fails out-of-support, every-event ESS, and seed/particle stability diagnostics.

## Family-likelihood admission handoff

The bounded integration handoff is
[`outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.json`](outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.json).
It exposes one family-independent query contract: remove the configured source
prior, select the nearest seventh-arc cell by WGS84 great-circle distance, and
return `out_of_support` rather than a likelihood beyond 75 NM. A
`diagnostic_only` family must not update the integrated estimator. The companion
[`query utility`](code/query_family_likelihood.py) implements that contract and
can require an admitted family with `--require-admissible`.

The explicit admission sensitivities are no more than 1% likelihood-weighted
missing/outside support, ESS at least 200 for every represented recovery over
at least 90% of the likelihood surface, total variation no more than 0.1 under
matched seed/particle replication, stable 90%/95%/99% contour sets, and
all-path predictive replay that is at least 95% complete and competitive with
persistence. These are scientific diagnostics, not family weights.

| Family surface | Evidence represented | Diagnostic peak / 90% equal-tail | Likelihood-weighted out of support | Mass with every recovery ESS ≥200 | Decision |
| --- | --- | --- | ---: | ---: | --- |
| Native HYCOM + distinct WAVERYS Stokes + measured flaperon response | Réunion flaperon only; the retained/upstream time support cannot represent the complete later evidence set | arc-166, 36.97°S / 32.16–41.97°S | 45.66% | 0% | diagnostic only |
| GDP monthly climatology + distinct WAVERYS Stokes | nine stringent recovery episodes and two Australian non-recovery response populations | arc-165, 36.57°S / a one-cell 90% interval | 76.01% | 0% | diagnostic only |
| Full-domain GLORYS12 + distinct WAVERYS Stokes | the same nine recovery episodes and two Australian non-recovery populations | arc-152, 30.70°S / 29.70–35.75°S | 1.746% | 0% | diagnostic only |

The GDP one-cell interval is not calibrated precision. Three recovery episodes
never reach ESS 50 in any cell, Mossel Bay never reaches ESS 83, and the joint
product is dominated by rare, unevenly represented events. The native surface
has a broad southern mode but does not cover eight later recoveries or either
Australian non-recovery population. Neither surface has matched replication
for its exact current evidence configuration; both also fail the configured
predictive replay completion criterion. The family peaks are therefore
diagnostic source-condition modes, not standalone crash estimates.

The full-domain CMEMS family passes complete evidence scope, conservative
isotope behavior, and 5,400-path currents-plus-Stokes replay. It fails three
independent diagnostics. Its likelihood-weighted missing/outside-support
fraction is 1.746% against the declared 1% sensitivity. Mossel Bay reaches at
most ESS 66.7, Chidenguele 179.0, and Paindane 130.1; no source mass has ESS at
least 200 simultaneously for all nine recoveries. Reference-versus-doubled
total variation is 0.394, the maximum 90%/95%/99% equal-tail endpoint movement
is six cells, and minimum highest-weight-set Jaccard is 0.533. The separate
full-domain machine-readable handoff and publication outputs are
[`JSON`](outputs/cmems-full-domain-family-likelihood-handoff/ocean-drift-family-likelihoods.json),
[`HTML`](outputs/cmems-full-domain-family-likelihood-handoff/index.html),
[`PNG`](outputs/cmems-full-domain-family-likelihood-handoff/ocean-drift-family-likelihoods.png),
[`SVG`](outputs/cmems-full-domain-family-likelihood-handoff/ocean-drift-family-likelihoods.svg),
and [`PDF`](outputs/cmems-full-domain-family-likelihood-handoff/ocean-drift-family-likelihoods.pdf).

The browser report and publication outputs are
[`HTML`](outputs/family-likelihood-handoff/index.html),
[`PNG`](outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.png),
[`SVG`](outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.svg),
and [`PDF`](outputs/family-likelihood-handoff/ocean-drift-family-likelihoods.pdf).
Their hashes are in
[`artifact-sha256.json`](outputs/family-likelihood-handoff/artifact-sha256.json).

## Native-field and mask verification

The production-format fields use MHGRID schema 3. `-30000` means intermittent
missing data and `-29999` means a time-invariant persistent land mask. Bilinear
interpolation may renormalize finite corners only across the latter. A
limiting-case Rust fixture proves that a persistent-land corner can be
renormalized while the same geometry with an intermittent-missing corner
fails. Missing values are never converted to zero current or zero Stokes
velocity.

| Field | Time/grid support | Persistent-mask audit | Independent raw check |
| --- | --- | --- | --- |
| Regional GLORYS12 `uo`/`vo` | 511 daily 1/12° fields | 526,262 persistent cells; 3,365 intermittently missing/changed cells over 1,021 comparisons | 48 component values, 0 mismatches |
| Regional WAVERYS `VSDX`/`VSDY` | 4,088 three-hourly 0.2° fields | 90,617 persistent cells; 0 intermittent/changed cells over 8,175 comparisons | 48 component values, 0 mismatches |
| Full-domain GLORYS12 `uo`/`vo` | 1,062 daily 1/12° fields | 365,620 persistent cells; 5,418 intermittently missing/changed cells over 2,123 comparisons | 48 component values, 0 mismatches |
| Full-domain WAVERYS `VSDX`/`VSDY` | 8,496 three-hourly 0.2° fields | 62,542 persistent cells; 1,136 intermittent/component-specific gaps over 16,991 comparisons | 48 component values, 0 mismatches |

The explicit GLORYS12/WAVERYS union coastal-support field has 529,441 masked
cells on the 1,615,441-cell GLORYS12 grid. It is an absorbing model-support
boundary only. It contains no beaching rate and does not model retention or
refloating.

## All-path drifter replay

`crates/ocean-drift/examples/validate_current_trajectories.rs` replays raw NOAA
GDP six-hour trajectories with zero diffusion and zero direct windage. It uses
the supplied drogue-loss date and reports still-drogued, undrogued, and
drogue-transition intervals separately. Each case samples 600 starts spanning
western 10°E–60°E, central 60°E–100°E, and eastern 100°E–150°E regions.
Every attempted path is scored. A terminated forecast holds its last valid
position to the target epoch and remains in the accuracy denominator, while
its termination reason is reported separately. Baselines are persistence and
a constant velocity inferred from the 24 hours before release.

The complete matched 24-case GLORYS12/WAVERYS table is
[`outputs/validation/waverys/waverys-current-trajectory.md`](outputs/validation/waverys/waverys-current-trajectory.md).
Machine-readable overall, regional, and drogue-state results are beside it.

### Currents-only comparison

| Family | Year | Horizon | Complete | Median current / persistence error | Current better than persistence |
| --- | ---: | ---: | ---: | ---: | ---: |
| GDP climatology | 2014 | 5 d | 97.3% | 80.2 / 95.1 km | 62.5% |
| GDP climatology | 2014 | 30 d | 95.2% | 300.0 / 370.2 km | 63.8% |
| GDP climatology | 2015 | 5 d | 97.5% | 75.4 / 87.1 km | 59.5% |
| GDP climatology | 2015 | 30 d | 97.5% | 270.2 / 352.5 km | 61.2% |
| Native HYCOM | 2014 | 5 d | 99.2% | 79.3 / 95.8 km | 57.8% |
| Native HYCOM | 2014 | 30 d | 97.2% | 312.0 / 398.2 km | 59.3% |
| Native HYCOM | 2015 | 5 d | 99.0% | 71.0 / 85.6 km | 58.8% |
| Native HYCOM | 2015 | 30 d | 96.2% | 317.2 / 340.2 km | 52.0% |
| CMEMS GLORYS12 | 2014 | 5 d | 99.8% | 59.3 / 95.8 km | 72.2% |
| CMEMS GLORYS12 | 2014 | 30 d | 99.0% | 268.4 / 398.2 km | 67.5% |
| CMEMS GLORYS12 | 2015 | 5 d | 99.8% | 59.1 / 90.0 km | 68.8% |
| CMEMS GLORYS12 | 2015 | 30 d | 99.5% | 238.4 / 338.3 km | 67.3% |

GLORYS12 currents-only beats persistence at every tested horizon/year and has
lower matched median error than native HYCOM. This supports selection of the
current field only; it does not calibrate a flaperon motion model.

### Full evidence-domain replay

The full-domain replay repeats exactly 600 attempted paths in 2014, 2015, and
2016 at 5, 15, and 30 days, first with currents only and then with distinct 1×
WAVERYS Stokes. All 10,800 attempts remain in the score. At 30 days:

| Family | Year | Complete | Median model / persistence error | Model better than persistence |
| --- | ---: | ---: | ---: | ---: |
| GLORYS12 currents only | 2014 | 99.8% | 268.0 / 398.2 km | 67.5% |
| GLORYS12 currents only | 2015 | 100.0% | 241.5 / 352.5 km | 66.8% |
| GLORYS12 currents only | 2016 | 99.8% | 226.6 / 320.0 km | 68.0% |
| GLORYS12 + distinct Stokes | 2014 | 98.8% | 307.6 / 398.2 km | 59.5% |
| GLORYS12 + distinct Stokes | 2015 | 99.2% | 254.1 / 352.5 km | 61.8% |
| GLORYS12 + distinct Stokes | 2016 | 99.7% | 244.3 / 320.0 km | 62.0% |

The nine currents-plus-Stokes aggregate rows pass the declared predictive
diagnostic: minimum completion 98.83%, median error ratio to persistence 0.695,
and median fraction better than persistence 0.638. Sequential case runtimes
sum to 837.0 s and peak child RSS is 4,617,464 KiB. The complete overall,
regional, drogue-state, runtime, and hash records are under
[`outputs/validation/cmems-full-domain/`](outputs/validation/cmems-full-domain/).
GLORYS12 assimilates ocean observations and WAVERYS assimilates significant
wave height while using GLORYS12 currents, so this replay is not guaranteed
statistically held out.

### Matched WAVERYS response

Stokes drift is the wave-induced net Lagrangian transport of water parcels
beneath oscillatory surface waves. It is physically distinct from Eulerian
ocean current and from direct aerodynamic windage on the object. The runner
therefore evaluates

`transport velocity = current + response × Stokes + direct windage`

with separate fields and an explicit response sensitivity. CSIRO compared
undrogued-drifter leeway with modelled Stokes and also measured separate
flaperon leeway. Durgadoo used daily 1/12° currents, separate wave-model Stokes
with a 100% central scale, negligible direct windage for a near-horizontal
flaperon, and explicit recovery uncertainty. Neither source demonstrates that
the intact MH370 flaperon must follow exactly 100% of WAVERYS surface Stokes.

Thirty-day drogue-state medians make the target dependence visible:

| Surface response | Undrogued error 2014 / 2015 | Undrogued complete | Drogued error 2014 / 2015 |
| ---: | ---: | ---: | ---: |
| currents only | 317.7 / 255.9 km | 99.2% / 99.5% | 227.2 / 207.5 km |
| 0.5× WAVERYS | 274.8 / 231.0 km | 98.4% / 99.5% | 258.3 / 257.2 km |
| 1.0× WAVERYS | 245.2 / 236.3 km | 98.0% / 98.0% | 348.2 / 337.5 km |
| 1.5× WAVERYS | 292.9 / 262.5 km | 96.4% / 97.5% | 417.1 / 409.7 km |

One response is not selected by both years. As expected, adding surface Stokes
to drogued 15 m current followers degrades their replay, so drogued and
undrogued cases are not pooled into an object calibration. The full 24-case
sweep took about 278 s observed wall time; sequential children used 92.0 s
user CPU, 116.1 s system CPU, and at most 12,036,096 KiB resident memory.

HYCOM+NCODA and GLORYS12 assimilate ocean observations and WAVERYS assimilates
significant wave height while using GLORYS12 currents. No GDP replay is
guaranteed statistically held out. GDP validation against GDP drifters also
shares the observational network. These tests check units, axes, signs,
integration, coverage, gross predictive behavior, and drogue-state
separation; they cannot by themselves estimate unbiased model weights or a
flaperon response coefficient.

## Adaptive source-area sampling

The source estimator uses deterministic keyed adaptive sequential Monte Carlo
with 30-day selection. Every result records proposal probabilities, exact
correction weights, ancestor counts, correction-weight ESS, seed, resolved
configuration, input hashes, runtime, and memory. One-level and three-level
synthetic fixtures each use 20,000 independent replications and recover the
known 0.5 target within 0.01 and 0.015. This is the independent unbiasedness
check for the proposal/correction implementation.

Earlier family-specific diagnostics remain separate:

| Family/doubled run | Particles/cell | Maximum / median arrival ESS | Mass with ESS ≥100 / ≥200 | Importance-weighted termination |
| --- | ---: | ---: | ---: | ---: |
| GDP monthly climatology | 2,048 | 292.9 / 75.0 | not pooled / 2 cells | 60.58% |
| Native HYCOM + coarse Stokes | 2,048 | 445.8 / 66.2 | 35 / 25 cells | 72.63% |
| Native HYCOM currents only | 8,192 | 944.7 / 159.1 | 97.9% / 91.3% | 9.52% |
| GLORYS12 currents only | 8,192 | 493.8 / 12.8 | 83.2% / 65.4% | 1.10% |

GDP is an observational monthly climatology sensitivity, not an equally
weighted substitute for time-varying currents. The older coarse-Stokes and
currents-only results are controls, not candidates to average with WAVERYS.

### Nominal 1× WAVERYS replication

The canonical configuration uses GLORYS12 daily currents, distinct 3-hourly
WAVERYS Stokes, the union coast support, zero direct windage, and the same
flaperon recovery/isotope model in all cases.

| Case | Particles/cell | Peak arc | Max / median arrival ESS | Source mass ESS ≥100 / ≥200 | Terminated | Runtime / peak RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reference seed | 1,024 | 146 | 263.3 / 53.5 | 81.4% / 3.8% | 46.52% | 155.2 s / 11,960,992 KiB |
| alternate seed | 1,024 | 129 | 220.0 / 42.6 | 76.6% / 11.1% | 47.74% | 162.7 s / 11,925,840 KiB |
| doubled | 2,048 | 129 | 417.7 / 111.9 | 91.7% / 82.6% | 46.43% | 236.4 s / 11,852,984 KiB |

For the doubled run, termination is 0.379% intermittent missing coverage,
2.648% outside spatial support, and 43.400% land encounter. Beaching,
outside-time support, and numerical failure are zero. These fractions use
proposal correction weights and remain in the physical accounting; the run
does not condition on survivors. Outside-support loss is concentrated in
negligible far-south source cells, while the normalized supported source mass
is almost entirely inside the regional domain.

Pairwise total variation is 0.232–0.283. Peak shifts are 0–17 arc cells. The
maximum equal-tail endpoint shifts are four cells at 90%, two at 95%, and two
at 99%; corresponding highest-weight-set Jaccards are 0.778–0.833,
0.791–0.818, and 0.846–0.923. Broad intervals are steadier than the local mode,
but the nominal response is not fully replicated.

### Surface-response sensitivity

The 2,048-particle matched runs differ only in `stokes_velocity_scale`:

| Response | Peak and latitude | Max / median arrival ESS | Mass ESS ≥200 | Missing / outside / land | Total terminated |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0.5× | arc-119, 11.91°S | 498.6 / 113.5 | 83.4% | 0.150% / 0.259% / 10.275% | 10.685% |
| 1.0× | arc-129, 18.00°S | 417.7 / 111.9 | 82.6% | 0.379% / 2.648% / 43.400% | 46.427% |
| 1.5× | arc-161, 34.90°S | 451.9 / 64.7 | 69.0% | 0.304% / 7.457% / 53.171% | 60.932% |

Pairwise total variation is 0.471 for 0.5× versus 1×, 0.494 for 1× versus
1.5×, and 0.741 for 0.5× versus 1.5×. Peak shifts are 10, 32, and 42 arc
cells. The 90%/95%/99% equal-tail endpoint shifts reach 16/16/12 cells. This
response instability is decisive: a plotted peak is not a calibrated crash
location.

### Full evidence-domain matched CMEMS family

The 1,024-particle full-domain run simulates 867,328 paths and completes in
1,694.6 s at 11,724,316 KiB peak RSS. Its prior-removed conditional surface
peaks at arc-152 (30.70°S); 90%, 95%, and 99% equal-tail intervals are
29.70–35.75°S, 27.62–35.75°S, and 26.55–36.97°S. Likelihood-weighted
termination is 1.011% missing coverage, 0.735% outside spatial support, and
58.821% land encounter; beaching, outside-time support, and numerical failure
are zero. The absorbing support-mask land fraction is not a calibrated beach
retention probability.

Changing the seed moves the peak to arc-156 and doubling particles moves it to
arc-154. Reference comparisons reach total variation 0.394, equal-tail
endpoint movement of six cells, and a minimum highest-weight-set Jaccard of
0.533. Every-recovery ESS at least 200 covers zero likelihood-surface mass.
The adaptive sampler has therefore made the surviving rare-event populations
measurable without making the nine-event product calibrated or stable.

| Replication | Seed | Particles/cell | Runtime | Peak RSS |
| --- | ---: | ---: | ---: | ---: |
| reference | 3700271 | 1,024 | 1,694.6 s | 11,724,316 KiB |
| alternate seed, file-backed loader | 3701271 | 1,024 | 2,964.7 s | 12,424,696 KiB |
| doubled, file-backed loader | 3700271 | 2,048 | 6,726.1 s | 12,432,604 KiB |

The reference executable predates the loader-only file-backing change; its
field hashes and scientific configuration are identical. The private
file-backed executable is pinned in the two replication manifests. The loader
change is independently covered by owned-versus-file-backed equality and
truncation fixtures.

## Conditional isotope compatibility screen

The screen is applied only to already represented confirmed-flaperon arrivals.
It uses 115-, 154-, and 192-day growth chronologies, common
isotope-temperature calibration and seawater uncertainty, SST uncertainty,
seven-day shell smoothing, 14-day correlated residuals, and a simultaneous
predictive covariance envelope. Compatibility under any defensible chronology
is neutral. Marginal penalty is capped at ln(2). Strong rejection requires all
chronologies outside a 99.5% envelope and is capped at ln(100). Missing SST for
any chronology prevents strong rejection. The 49 rows are never multiplied as
independent likelihood terms, and no path receives a positive boost.

The 1× doubled regional WAVERYS run classifies 96,061 arrival paths compatible,
1,098 marginal, 223 rejected, and 15,221 as lacking complete chronology/SST
support. The full-domain reference run classifies 24,716 compatible, 756
marginal, 149 rejected, and 17,454 missing-coverage paths. In both cases the
screen is neutral or suppressive and never a positive localization term.
Removing the screen changes its normalized source profile by total variation
`1.39e-7`; equal-tail intervals are unchanged. The current broadening versus
the superseded result comes from removing the old density-ranking term, not
from positive evidence added by the conservative screen.

## Reporting and crash-location decision

The football-field renderer places seven cited prior-study ranges beneath the
current family and includes 50%, 90%, 95%, and 99% intervals. Its deterministic
layout audit checks y-axis title/tick clearance, x-axis/legend clearance,
legend/footer clearance, and study-label bounds. Publication-quality WAVERYS
outputs are
[`PNG`](outputs/source-comparison/cmems-glorys12-waverys-football-field.png),
[`SVG`](outputs/source-comparison/cmems-glorys12-waverys-football-field.svg),
and [`PDF`](outputs/source-comparison/cmems-glorys12-waverys-football-field.pdf),
with numeric
[`CSV`](outputs/source-comparison/cmems-glorys12-waverys-source-comparison.csv)
and [`JSON receipt`](outputs/source-comparison/cmems-glorys12-waverys-source-comparison.json).

The earlier currents-only
[`family-conditioned report`](outputs/family-conditioned-source-crash/family-conditioned-source-crash.pdf)
remains a labelled mathematical intersection and is not updated as an accepted
estimate. A source cell is a crash-site candidate only conditional on immediate
release at impact on the represented seventh arc; it is not an all-evidence
crash estimate by itself. Because Stokes response alone spans northern and
flight-compatible southern modes, updating the central estimator would create
false precision.

The requested minimum evidence was materially low missing-data loss, hundreds
of effective arrivals in supported regions, and stable 90%, 95%, and 99%
regions under seed and particle replication. Full-domain acquisition and
field mechanics are now adequate, but the CMEMS family still has 1.746%
likelihood-weighted missing/outside support, no surface mass with every-event
ESS at least 200, and seed/particle instability. Surface-response and coast
sensitivity also remain uncalibrated. These are scientific diagnostics, not a
family weight or publication claim. The defensible status is therefore:

- GLORYS12 is preferred to native HYCOM as the time-varying current field.
- WAVERYS is the matched, verified Stokes field, not a calibrated flaperon
  response.
- GDP remains a separate observational climatology sensitivity.
- No family weights are estimated; failed paths remain in all scores.
- No drift family is accepted for central flight-posterior narrowing.
