# Methods draft: wreckage settling

Ocean settling module, 9 October 2026; updated 10 October (overnight) with the reference-289 results and the seabed
wreckage PDFs. This is a first draft of the paper's settling methods
section, written under the architecture entry of 9 Oct ~04:15 UTC. Source keys in square brackets
refer to `results/settling-references.md`, and ocean products to `results/ocean-references.md`. Code
is `engine/hypotheses/settling/` on branch `hypothesis/settling` (`8492de7` for §§1-5; `d1e32ab` for the
D6 pages; `9823b4e` for the wreckage-field generator).

**Status.** Since `bfb71d5` the ocean is real: the GLORYS12V1 column, surface current, ERA5 wind,
AusSeabed and GEBCO bathymetry, and TEOS-10. The breakup table is still a set of declared educated
estimates, so every number below remains PROVISIONAL. No number here is evidence about where MH370
lies.

## 1. What settling is

Settling is a **transform, not a likelihood**. It carries each ocean-surface impact sample from end
of flight to the point where its wreckage first touches the seabed, and emits the result as wreckage
samples. It adds no term to the posterior. Searched areas reads its output when it evaluates the
non-detection of each seabed search, and drift receives the elements that stay afloat.

A **wreckage draw** is one whole-field configuration:
- one breakup family;
- one ocean-error realisation;
- every element class.

Each draw carries weight 1/N of its impact sample. A consumer averages its per-draw value over the
draws and never multiplies across them, because draws are alternative outcomes, not additional
wreckage (`stream.rs`). Draw d depends only on the impact and on d, so refining from 512 to 4,096
draws leaves the first 512 unchanged. The runner streams draws to the consumer rather than storing
them (core request 12, ruled 9 Oct). Stored, they would be 40-74 rows per draw at 144 B each.

## 2. Breakup families

The family comes from end of flight's `debris_class`, drawn once per impact. Its probabilities
follow settling's rule (`breakup.rs`) on the descent speed V_d and total speed V at first contact:

  P(intact) = L(ln(a/V_d)/s) L(ln(c/V)/s),
  P(fragmented) = (1 - P(intact)) L(ln(V/b)/s),
  P(broken) = the remainder,

where L is the logistic function, a = 8 m/s, c = 100 m/s, b = 110 m/s and s = 0.2. Three accidents
anchor the rule as calibration points, not as independent tests:

| accident | family | contact | P(family) | source |
|---|---|---|---|---|
| US Airways 1549 | intact | about 64 m/s, 3.8 m/s down | 0.88 | [ntsb2010] Table 2 |
| AF447 | broken | 55.4 m/s down, 78.1 m/s total | 0.85 | [bea2012af447] |
| Swissair 111 | fragmented | about 154 m/s, 20 deg nose down | 0.84 | [tsb2003] |

## 3. Element classes and fates

There are six classes: engine, landing gear, wing box, fuselage section, flat panel and cabin
contents. Each has, per family:
- a mass share (the shares sum to one);
- a piece count;
- distributions of areal density, material density, drag coefficient, descent factor, glide ratio,
  glide memory, carry time, float time and leeway (`breakup.toml`).

Sixteen representatives per class carry the pieces as multiplicities. That is a computational
choice, not a statement of probability.

Each element takes one of three fates:
1. it sinks at once;
2. it floats for up to T_c = 48 h and then sinks;
3. it stays afloat beyond T_c and is handed to drift with no seabed position.

T_c is enforced when the table is loaded (`results/breakup-field-candidate.md` §8). The afloat
mass share is 0.146 for intact, 0.163 for broken and 0.201 for fragmented. Pete's 9 Oct choice was
to keep that share and carry x0.5 and x1.5 as a declared sensitivity (`floating_share_scale`), which
gives 0.070-0.299 across the families.

## 4. Carry and the float phase

Each element starts at the impact point displaced along the track by the horizontal impact speed
times its carry time, with lateral scatter.

Floating elements then move through the shared batch integrator `mh370_ocean::integrate`, one call
per draw:
- each element is a particle with Stokes response a = 0 (declared, pending drift's object-response
  result) and wind response equal to its leeway;
- each stops at its own sink time (`Particle.end_time`);
- the run uses a 600 s step and sub-grid diffusion from the shared provisional prior, one K per draw.

Forcing comes from the GLORYS12V1 daily surface current [lellouche2021glorys12] and ERA5 3-hourly 10 m
wind [era5 in the drift ledger], through the shared `GridField`. On the provisional controlled-depth
page, a uniform 0.13 m/s current stands in: the median of GLORYS12V1's top level on 8 March 2014 over
30-40 S, 88-106 E, with the p90, 0.31 m/s, as a variant.

## 5. Descent

An element sinks at a speed relative to the water of

  w = k sqrt(2 g s (1 - rho_w/rho_m) / (rho_w C_d)),

where s is the areal density, rho_m the material density, C_d the drag coefficient and k >= 1 a
descent factor for fluttering and tumbling bodies [andersen2005; field1997]. Its speed relative to
the ground is w - w_up wherever the product resolves vertical velocity. An absent vertical velocity
is never read as zero.

The descent is integrated in 50 m depth steps. Each step adds three horizontal terms:
1. the current at mid-step, from the shared `Profile::at_depth`;
2. the draw's ocean-error realisation at the element's time, position and depth;
3. a glide at speed G w, whose heading decorrelates as exp(-dz/l) over depth, or in its diffusive
   limit (variance G^2 l dz per component) when l <= dz.

Contact is found against the seabed at the element's current position. The calculation stops at
first contact (rule 9): sliding and burial are not modelled.

Below the ocean model's bottom, one of the shared crate's three explicit rules applies, and the
extrapolated depth is recorded for each element.

**Inputs:**
- **Seabed:** AusSeabed MH370 Phase 1 at 150 m where it covers, else GEBCO_2026 at 15 arc-seconds
  [gebco2026; AusSeabed under ocean transport's ledger], loaded through `Bathymetry` for 80-112 E,
  45-18 S. Land and points outside the window are refused.
- **In-situ density:** TEOS-10 [ioc2010teos10; mcdougall2011gsw] on the column's own potential
  temperature and practical salinity at the impact. At 92 E, 35 S it gives 1025.35 kg/m3 at the
  surface and 1044.46 kg/m3 at the GLORYS floor (3,796.5 m), held below it. WOA23 [reagan2024woa23]
  is the declared alternative; changing to it moves p90 by under 0.01 %.
- **Ocean error:** the shared banded model, with one independent realisation per band and one draw
  per wreckage configuration. Per component it is 0.10 m/s in the top 100 m, 0.05 m/s to 1,000 m,
  0.02 m/s below that, and 0.03 m/s within 200 m of the seabed.
- **Column:** GLORYS12V1 daily uo and vo on 50 levels (`GridProfile`), interpolated linearly in time
  and bilinearly in space, held at the deepest level below the model floor (`hold-deepest-level`;
  linear-to-zero changes p90 by under 0.2 %). The analytic two-layer column survives only for
  closed-form tests and the controlled-depth page.

## 6. Representative results (deliverable 6)

All impacts below come from end of flight's `reference-289` sweep (`eof-289-full-s1..s4`; prior track 289.7°;
source run `runs/snap289-m0011`), with its dive class (b) and Boeing-calibrated glide PROVISIONAL-OVERNIGHT and
fuel uncorrected (fuel-model audit F1-F14 open). The 295.66° pages (`results/settling-d6/`, `settling-d6-real/`)
stay as the comparison.

**Seabed depth under the impacts** (`results/settling-d6-289/`; GEBCO_2026 nearest cell, `option_posteriors`
weights, equal weight per seed). With the 00:19 bursts held out and no log-on cause, p10 / p50 / p90 are 3,362 /
3,846 / 4,341 m. Across six option × cause rows the median is 3,787-3,890 m and p90 4,143-4,341 m. No mass lies
shallower than 200 m or on land. Against the 295.66° map, p90 is about 270 m deeper.

**On the real ocean** (`results/settling-d6-real-289/`), at four impact points (p10, p50 and p90 latitude and
the densest cell, 39.1-32.9 S), 1,024 draws per point and family:
- engines and gear rest within 0.18-0.48 km (p90);
- broken and fragmented sections within 0.4-0.8 km, intact sections at about 5.6 km;
- cabin contents at about 9-13 km.

The analytic column with uniform surface fields over-estimates here (dense classes x1.07-1.10, floated up to
x1.27); at the 295.66° points it under-estimated (x0.88-0.96). It is within about ±25 % of the real ocean with a
location-dependent sign, so the real-ocean numbers are the ones to quote. Copernicus-GlobCurrent as the
float-phase surface current moves floated classes by x1.00-1.23 (x1.37 at one point) and leaves dense classes
unchanged: the ocean-model choice is the largest real-ocean uncertainty for floated classes. Density source,
GEBCO-only seabed and the below-floor rule each change p90 by under 1.5 %. Monte Carlo halves at 512 draws
differ by a median of 2.7 % (11 % at most).

**Provisional controlled-depth page** (`results/settling-d6-289/`, depths 3,360 / 3,850 / 4,340 m and 5,800 m,
the ATSB maximum north of Broken Ridge [atsb2017, p. 49]). At 3,850 m engines and gear rest within 0.20-0.44 km
(p90); wing box and fuselage sections within 0.45-0.82 km for broken and fragmented impacts but 5.4-5.7 km for
intact ones, which float for hours first; cabin contents about 11-12 km. From 3,360 to 5,800 m the dense classes
change by 2-28 %.
- Float time is the largest lever for floated classes: no float gives x0.05-0.07 for cabin contents.
- Carry is the largest lever for intact dense classes (x0.4), and glide for broken and fragmented ones
  (x0.7-0.8).

**Analogue fields.** AF447's main seabed field, about 600 x 200 m at 3,900 m [af447seabed2011]; Flash 604's,
within about 275 x 440 m at about 1,000 m after a 416 kt, 25° nose-down entry [mca2006fsh604, pp. 5, 130];
Swissair 111's, about 125 x 95 m at about 55 m [tsb2003, p. 77]. ATSB expected a field at these depths to be
at least 100 m x 100 m and very likely more than 200 m x 200 m [atsb2017, p. 83]. All are of the order of the
dense-class offsets. DNV-RP-F107's dropped-object angular deviations [dnv2010] imply an sd of 140-1,070 m at 4 km.

## 6a. The seabed wreckage PDF under the 00:19 interpretations

`results/settling-wreckage-field-289/` and `results/settling-wreckage-field-289-priorities/`. Impacts are
systematically resampled from each option's posterior (end of flight's `option_posteriors`, seeds pooled with
equal weight). Each resampled impact is carried through the transform once on the real ocean
(`settling::tests::wreckage_field`). The seabed density gives each draw's settled elements the impact's
probability in proportion to element mass, so it is dominated by the dense, sonar-detectable pieces. Pieces still
afloat (about 18 % of mass) have no seabed position and are excluded. Grid 0.02°, Gaussian 0.1° (6 NM), HPD
50/90/99 %, areas on the authalic sphere. Each impact field is compared with the same resampled impacts, smoothed
identically, so that the difference is settling alone.

| impact PDF (00:19 option × log-on cause) | impact ESS | 90 % area, impacts → seabed (km²) | settling |
|---|---|---|---|
| held out × none | 12.4 M | 700,600 → 701,300 | +0.1 % |
| R600 as observed (no offset) × fuel exhaustion | 59,512 | 265,700 → 266,500 | +0.3 % |
| R600, Holland offset × fuel exhaustion | 67,598 | 246,200 → 247,500 | +0.5 % |
| R1200, Holland offset × fuel exhaustion | 10,065 | 166,200 → 167,300 | +0.7 % |
| both bursts, inflated × fuel exhaustion | 2,042 | 170,100 → 172,100 | +1.2 % |
| Holland H1: both, start-up offset × fuel exhaustion | 36 | not estimable | — |
| Holland H2: both, no offset × other | 82 | not estimable | — |

The settled-offset kernel is the same under every option: half the settled mass rests within 0.34-0.36 km of its
impact and 90 % within 2-3.6 km. About 5-7 % lies more than 5 km away (p99 20-22 km); this is floated contents. So
the seabed PDF of the main wreckage is the impact PDF to about 1 % in area. Settling matters at the scale of a search
cell, not at the scale of the impact PDF: the 00:19 interpretation sets the search area, and settling does not.
Impacts north of 18° S (under 0.02 % of any panel) lie outside the ocean window and are excluded as not computed.

## 7. Declared alternatives (off in the baseline)

- **Implosion at depth** (Pete, 9 Oct). A share of cabin contents rides a fuselage section to a
  collapse depth and is released there. The report uses 0.8 / 0.4 / 0 inside and a log-uniform
  depth over 10-1,000 m. There is no airliner calibration case; Derbyshire and Thresher
  [mearns1994; thresher1963] show only that such collapses happen. Cabin-contents p90 falls to x0.5-0.6.
- **Occupants class** (architecture ruling, ~04:15). It contains 239 people [mot2018mh370], 10 % of
  impact mass taken from cabin contents, with stays-afloat shares of 0.05 / 0.22 / 0.35. Broken's 0.22
  is AF447's 50 of 228 recovered at the surface within days [metron2011], a lower bound. Bodies afloat
  per family come to 11 / 54 / 84. The class is evidential only once drift has a 2014 surface-search
  model.

- **Implosion events** for hydroacoustics (`results/settling-implosion-events/`): the time and place
  where each sealed section reaches its collapse depth. An intact contact's sections collapse 14 min to
  5 h after impact (median 1.0 h), after floating; a broken contact's within about 34 min (median
  2.7 min). Depth and trapped-air volume are the declared priors.

## 8. Limitations

- The column and the breakup table are provisional.
- No post-contact movement is modelled.
- Family probabilities rest on three calibration points.
- The impacts are reference-289's, which carry uncorrected fuel and two PROVISIONAL-OVERNIGHT end-of-flight
  choices. Settling's conclusions depend on them only through depth and location, which barely matter; the
  pages are re-run unchanged on each new impact set.
- Holland's H1 and H2 are not estimable on reference-289 (impact ESS 36 and 82). Their seabed PDFs wait on end
  of flight's per-hypothesis sampling.
- The afloat share is the least-constrained number in the table.
- Body properties in the occupants class carry no source yet (ledger, open item 3).
