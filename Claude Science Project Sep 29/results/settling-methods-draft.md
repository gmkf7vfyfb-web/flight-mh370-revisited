# Methods draft: wreckage settling

Ocean settling module, 9 October 2026. This is a first draft of the paper's settling methods
section, written under the architecture entry of 9 Oct ~04:15 UTC. Source keys in square brackets
refer to `results/settling-references.md`, and ocean products to `results/ocean-references.md`. Code
is `engine/hypotheses/settling/` on branch `hypothesis/settling` at `8492de7`.

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

**On the real ocean** (`results/settling-d6-real/`), at four posterior impact points (p10, mode, p50
and p90 latitude, 37.9-35.6 S), with 1,024 draws per point and family:
- engines and gear rest within 0.22-0.47 km (p90);
- broken and fragmented sections within 0.5-0.9 km, but intact sections at 6.5-6.8 km;
- cabin contents at about 13-14 km.

Copernicus-GlobCurrent, the second ocean-model value, as the float-phase surface current spreads the
floated classes 4-12 % further (19 % at most) and leaves the dense classes unchanged. The real ocean leaves the dense classes within 2 % of the provisional page and spreads the floated
classes 5-13 % further (17 % at most). Monte Carlo halves at 512 draws differ by a median of 2.4 % in
p90 (14 % at most, for heavy-tailed classes).

**Provisional controlled-depth page:**

The results are in `results/settling-d6/`, at seabed depths of 3,500, 3,830 and 4,070 m (the p10,
p50 and p90 under the no-exhaustion-prior impact map) and 5,800 m.

At 3,830 m, engines and gear rest within 0.20-0.44 km (p90). Wing box and fuselage sections rest
within 0.45-0.83 km for broken and fragmented impacts but 5.4-5.7 km for intact ones, which float
for hours first. Cabin contents spread about 11-12 km in every family.

Depth barely matters: 3.5 to 5.8 km changes the dense classes by 1-24 %.

- Float time is the largest lever for floated classes: no float gives x0.05-0.07 for cabin contents.
- Carry is the largest lever for intact dense classes (x0.4), and glide for broken and fragmented
  ones (x0.7-0.8).
- The near-bottom band changes p90 by under 0.5 %.
- AF447's main seabed field, about 600 x 200 m [af447seabed2011], is of the same order as the
  dense-class offsets.
- DNV-RP-F107's dropped-object angular deviations [dnv2010] imply an sd of 140-1,070 m at 4 km.
- ATSB expected a debris field at these depths to be at least 100 m x 100 m and very likely more than
  200 m x 200 m [atsb2017, p. 83], consistent with the dense-class spread.

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
- The four impact points come from the 295.66° prior map. Core's reference-289 moves the 00:19 median
  0.85° north (`results/heading-ab-289-vs-29566.md`). Since depth barely matters, the points are to be
  updated, not the conclusions, once end of flight publishes impacts on the new reference.
- The afloat share is the least-constrained number in the table.
- Body properties in the occupants class carry no source yet (ledger, open item 3).
