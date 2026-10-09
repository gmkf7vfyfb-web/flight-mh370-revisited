# OCEAN_TRANSPORT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture

This module has **no owner and no brief yet**, and it is the shared dependency of three others -
ocean drift, settling and Pleiades. Decision 4 in `ARCHITECTURE.md` put `crates/ocean` under a
third owner precisely so that no consumer's assumptions become the project's ocean model.

The three consumers have been told, today, not to implement advection, field interpolation or
reanalysis access themselves, not to choose a reanalysis product, and to raise what they need
here as interface requests. **This file is therefore the input to the shared brief.** Whoever
picks this module up writes the brief from the accumulated requests rather than from first
principles, and should read them all before designing anything.

Known shape so far, pending those requests: surface currents, Stokes drift and wind for drift;
full-depth currents and density for settling; and TEOS-10 sound-speed profiles for hydroacoustics
if they are not sourced from settling - that last allocation is open. Provisioning of the
full-depth reanalyses and of bathymetry is unresolved, and the machine has about 45 GiB free on a
95% full volume, so dataset footprint is a design constraint and not an afterthought.

## 2026-10-08 - interface request from ocean settling (currents, T/S; bathymetry held)

What settling needs from `crates/ocean`, per the 8 Oct ruling in my inbox. Written before any of
my own physics is ported, so it reflects the requirement rather than an implementation already in
hand. One caveat up front: the bathymetry half of this request is **held** pending an architecture
ruling on open item 6 (where seafloor-depth lookup lives); if it lands with settling I will build
it and withdraw nothing here, and if it lands with you I will append it.

**The query I need.** Given a position, a depth and a time, the three-dimensional current and the
thermodynamic state, along a descent path that is integrated downward in depth rather than sampled
at fixed times. The natural call is therefore a *profile* at a horizontal position and time —
current, temperature, salinity and pressure on the product's depth levels, from the surface to the
local bottom — evaluated once per descending element, not a scattered point-by-point lookup. A
point query is the fallback; a profile query is what the physics wants, because the descent
integral dt = dz / w walks the column monotonically.

**Frame.** Horizontal velocity east and north in m/s, geographic, not grid-relative. Resolved
vertical velocity where the product has one, flagged as present or absent rather than returned as
zero — a silent zero systematically shortens displacement and is the one failure mode I would ask
you to make structurally impossible. Depth positive downward in metres; please state whether it is
geometric depth or pressure-derived, since that choice has to be consistent with the TEOS-10 call.

**Resolution and coverage.** The full impact posterior's support along the 7th arc, which is
roughly 30-40 deg S with a spatial buffer, surface to ~6,000 m, 7-10 March 2014 initially and
extendable later for delayed-flooding and slow-sinking scenarios. Temporally, daily means are
adequate for a 15-70 minute descent at 1-5 m/s but not for the slow-sinker tail, where an element
can be in the water column for many hours; so a product with sub-daily output, or an explicit
statement that the time axis is daily, matters more to me than horizontal resolution.

**Two things that are not conveniences.** First, the case where a detailed bathymetry cell is
*deeper than the ocean model's local bottom* needs to be a flagged, testable condition in the API,
not an interpolation artefact — I have to be able to apply and vary an explicit extrapolation
assumption there. Second, unresolved deep and near-bottom motion (internal waves, topographic
steering, the bottom boundary layer) is not in an 8-11 km grid and interpolating onto 150 m
bathymetry does not create it; I need a declared uncertainty model for it that I can vary, rather
than a deterministic field I have to add noise to myself. Related: one coherent ocean-error
realisation per impact event, since nearby fragments from one impact experience the same uncertain
ocean, not independent draws (my rule 10).

**Thermodynamics.** Density and buoyancy via TEOS-10, handling potential versus in-situ
temperature consistently - GLORYS12V1 reports potential temperature and HYCOM in-situ, so the
conversion cannot live at the call site in three different modules. Sound speed falls out of the
same evaluation; I have recommended to architecture that it be exposed here for hydroacoustics
rather than emitted by settling, which would make an acoustics input wait on a wreckage transform.

**Product choice is yours, not mine** - I am not requesting one. What I do need is that a run can
be repeated against a *different* product without changing my code, because settling contract rule 8 (composition rule 7 in common.txt) makes competing
products a labelled sensitivity and never an average.

**What I will do with it.** Integrate descent from first water contact to first seabed contact,
per element class and breakup family, keeping the uncertainty contributions separable: object
behaviour, current product, unresolved flow, bathymetry (rule 9 of my brief stops the calculation
at contact). The measurement in my inbox - current product moved the drift mode 1.2 deg against
11.9-34.9 deg for the Stokes scaling - says object response dominates here too, so I would rather
have a simple interface early than a precise one late.

**Prior work you should see before designing.** `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz`
contains `hypotheses/settling/environment.rs` (274 lines, a `Bathymetry` and a depth `Stack`) and
`prepare/ocean.py` (192 lines), written under the previous harness before this boundary existed.
They are evidence of the requirement, not a proposed interface, and I am not porting them.

- ocean settling

## 2026-10-08 - interface request from ocean drift (surface transport of floating objects)

What drift needs from `crates/ocean`, per the 8 Oct ruling in my inbox. Written before any code, so
it states the requirement rather than an implementation. No product is requested.

**The call I need is a batch forward integrator, not a field sampler.** Given N particles, each
with a release position, release time and a **persistent per-particle object-response vector**,
integrate forward for up to 730 days and return (a) positions at caller-chosen output times and (b)
termination events — beaching with a coast-segment ID and time, leaving the domain, and NaN fields
flagged as such. Since advection is yours, the integrator has to be yours; drift supplies the
object response and consumes the trajectories.

**Velocity components must reach the integrator separately, never pre-summed.**
`v = u_current + a_stokes * u_stokes + c_wind * U10 + diffusion`, with `a_stokes` and `c_wind`
per particle and persistent (or evolving under a declared model — never redrawn per step). Two
reasons. The measured sensitivity in my inbox: scaling Stokes by 0.5/1/1.5 moved the drift mode
11.9 -> 18.0 -> 34.9 deg S while changing the current product moved it 1.2 deg, so object response
is the dominant axis and has to be integrated per object class inside the likelihood. And
double-counting: an empirically fitted leeway may already absorb Stokes (arXiv:2005.09527), and
OSCAR v2 carries its own wind-driven term. **So each product needs a metadata declaration of what
its "current" already contains** — Ekman, Stokes, tides, inertial — so a consumer can refuse a
composition that counts a component twice.

**Diffusion as a declared, variable model.** The archive used 100 m^2/s; CSIRO used a 5 NM/day
random walk; neither was tested and the answer is sensitive to it. Expose the diffusivity (or walk
rate) as a parameter, and say whether it is applied per step or per field cell.

**Coastline and the land rule.** A coastline that keeps Reunion, Mauritius and Rodrigues — the
1:110m mask dropped Reunion, where the first confirmed piece was found. Beaching returns a segment
ID on a segmentation I can map the evidence table onto. The archive's field rule carries over:
**renormalise across land, never fill with zero.** A refloat hook (probability per unit time
after beaching), off by default, for the refinement.

**Domain, time, resolution.** Source region along the 7th arc, about 26-40 deg S, roughly
92-106 deg E (to be re-derived from the impact posterior); destination coasts from Tanzania
(5 deg S) to Mossel Bay (34 deg S, 22 deg E) and the whole Western Australian coast for the
non-recovery term. So about 15-120 deg E, 0-50 deg S. Time: 8 Mar 2014 to at least 30 Sep 2016
(the latest stringent-set find is 23 Jun 2016). Daily fields or better; a 6 h step matched to the
GDP drifter cadence.

**Throughput and footprint.** The pilot is ~11 M trajectories x 2,920 steps (730 d at 6 h, RK2);
the brief assumed 2e7 field evaluations per second per core over 16 cores. Please report the
achieved figure — it is one of the three numbers my pilot exists to measure. Indicative
**uncompressed float32 surface-only** footprint over that box and period (937 days), all cells:
GLORYS12 u,v daily 5.7 GB; WAVERYS Stokes 3-hourly 7.9 GB; ERA5 10 m wind 6-hourly 2.5 GB;
BRAN2016 u,v daily 3.9 GB; OSCAR v2 u,v daily 0.6 GB. About 20 GB for all five, against ~45 GiB
free, before any full-depth fields for settling.

**Repeatability across products.** Same as settling: the product is a run argument, and the
alternative is declared as `ocean-model`, shared with Pleiades and marginalised jointly by the
composer. One coherent environmental realisation per run across all particles — every recovered
object travelled through the same ocean (rule 8 of my brief) — so ocean error must not be
independent per particle.

**Shared with Pleiades.** Object positions on 23 Mar 2014, and on the 2014 aerial-search dates,
come from the same call with different output times.

**Proposed split of validation.** Drogued-drifter GDP replay tests fields and integrator, so it is
yours; undrogued and windage comparisons test object response and stay with drift. Raised with
architecture for ruling.

**Stub disclosed.** Pending a ruling, I propose a provisional analytic stub in my own directory —
closed-form fields only, no data, no gridded interpolation — for tests and plumbing. It assumes
exactly the call shape above: batch release, persistent per-particle (a_stokes, c_wind), separate
components, segment-ID beaching. Reject any of those assumptions here rather than inherit them.

- ocean drift

## 2026-10-08 - architecture: the brief is written - start here

`threads/master-prompts/ocean-transport.md`, written from the requests above. Read them all; the
brief summarises and rules, it does not replace them.

**Overnight priority: deliverable 1, the API with analytic fields.** Drift and settling are both
stubbing the same closed-form fields in their own directories right now. The sooner yours exists, the
sooner theirs are deleted. That unblocks three modules and outranks everything else tonight.

**Downloads tonight: at most 6 GiB in total**, to `/Users/pete/Downloads/mh370-ocean-data/`, subset
server-side to drift's pilot box and period, floor 25 GiB free checked before each file. GLORYS12
surface currents is the natural first. Credentials `COPERNICUS` and `NASA_EARTHDATA` are configured.
Start `results/ocean-data-manifest.md` with the first file.

### Overnight rules for every module, 8-9 October (binding until Pete is back, ~08:30 MT)

- **CPU:** core's 16-hour run is live until about 08:30 MT. Build with `cargo ... -j 4` and run nothing
  heavier than 4 threads. If the core run is slowed, everything downstream waits on it.
- **Disk:** 38 GiB free and falling while core writes. **Download nothing** unless your entry below
  says you may, and then only within the stated cap. Never save a multi-GB file as an artifact. Never
  let free space fall below 25 GiB - check `df` before each file.
- **Nobody can answer you tonight.** If you hit a question only Pete or the architect can answer,
  write it in `coordination/architecture.md`, choose the more reversible option, label the work
  provisional, and keep going. Do not stop and wait.
- **Concurrent appends:** if a push conflicts on a coordination file, keep BOTH entries in
  chronological order. Never resolve by taking one side.
- **Finish the night with a dated entry in `coordination/architecture.md`**: what landed, with commit
  hashes; what is provisional and why; what you need in the morning.

## 2026-10-08 - architecture: who is building this

Pete's ruling tonight: **shared ocean transport is built by a sub-agent the architecture session runs**,
not by a Pete-facing thread, at least for the first increment. Branch `core/ocean-transport`. Consumers:
your requests above are its specification; it signs its entries "ocean transport (architecture
sub-agent)". First deliverable is the API with analytic fields, which needs no network. It will stop
for Pete's approval at the first real data download, which is the correct place to stop.

## 2026-10-08 — ocean transport (architecture sub-agent): the API exists — call shapes, and how to swap your stubs

**What landed.** `crates/ocean` (package `mh370-ocean`) on branch `core/ocean-transport`, commit `311e481`,
cut from `claude-science-sep29` at `a90044d`. Analytic fields only, no data. 14 of 14 tests pass:
`cargo test -p mh370-ocean --release -j 2 -- --test-threads=2` (0.1 s of test time). **You cannot import it
yet:** hypotheses may depend only on `geo`, `hypothesis`, `serde` and `toml`. Core requests O1 (membership)
and O2 (let `mh370-hypotheses` depend on `ocean`, plus an `AGENTS.md` ruling) are in `CORE_STAGES.md`.
Until they land, keep your stubs and make them match the shapes below exactly; the swap is then a
`use mh370_ocean::...` line and deleting the stub.

**Conventions.** Positions `[lon_deg, lat_deg]` (type `LonLat`), east-positive, -180..180. Times are unix
seconds UTC, as in the hook API. Velocities geographic east/north, m/s. Depth geometric, m, positive down.
Sphere of radius 6,371,008.8 m; RK2 midpoint; fixed step shortened to land exactly on output times.

### Drift and Pléiades: the batch forward integrator

```rust
use mh370_ocean::{integrate, Forcing, RunSpec, Particle, ObjectResponse, Domain, Diffusion,
                  OceanErrorModel, Refloat, StraightCoast, Snapshot, Event, Fate, Component};
use mh370_ocean::analytic::{Uniform, SolidBodyGyre};

let current = Uniform::current(0.10, -0.02);                      // any VectorField
let stokes  = Uniform::new(Component::StokesDrift, 0.05, 0.02);
let wind    = Uniform::new(Component::Wind10m, 6.0, 2.0);
let coast   = StraightCoast { a: [100.0, -40.0], b: [100.0, -30.0], segments: 10, first_id: 500, land_left: false };
let spec = RunSpec {
    forcing: Forcing { current: &current, stokes: Some(&stokes), wind10: Some(&wind) },
    coast: &coast,                                  // or &NoCoast
    domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
    step_s: 6.0 * 3600.0,
    output_times: vec![/* ascending unix s; the run ends at the last */],
    diffusion: Diffusion::random_walk_nm_per_day(5.0),   // or Diffusivity{k_m2_s}, RandomFlight{..}, None
    ocean_error: OceanErrorModel::none(),                // or uniform_offset(s), eddying(s, L_m, T_s, modes)
    refloat: Refloat::Off,                               // or RatePerDay(r)
    seed: 1,
    leeway_absorbs_stokes: false,      // drift declares this for a fitted leeway (arXiv:2005.09527)
    accept_partial_stokes_overlap: false,
    threads: 4,                        // 0 = rayon default; results are identical for any count
};
let particles = vec![Particle { release: [96.5, -35.2], release_time: t_impact,
                                response: ObjectResponse { a_stokes: 1.0, c_wind: 0.02, leeway_angle_deg: 0.0 } }];
let out = integrate(&spec, &particles)?;   // Err(CompositionError) if a component would be double counted
// out.tracks[i].snapshots[k]: NotReleased | Afloat(LonLat) | Beached { at, segment } | Ended
// out.tracks[i].events: Beached { t, at, segment } | Refloated | LeftDomain | FieldGap { t, at, component, gap }
//                       | NonFinitePosition | ReleasedOnLand
// out.tracks[i].fate:   Afloat | Beached | LeftDomain | FieldGap | NonFinite | ReleasedOnLand
// out.provenance.ocean_model: the value of the `ocean-model` alternative for this run (product ids joined by "+")
```

- `v = u_current + a_stokes*u_stokes + c_wind*R(leeway_angle)*U10 + u_ocean_error + u_random_flight`, formed
  inside the integrator; a random-walk displacement is added after each step. `ObjectResponse` is fixed for the
  particle's whole life. `ObjectResponse::new(a_stokes, c_wind)` sets the leeway angle to 0, which is drift's
  request exactly; the angle (degrees, positive clockwise from downwind) is an addition, off by default.
- **Composition refusals:** a particle with `a_stokes != 0` and no Stokes field, or `c_wind != 0` and no wind;
  Stokes with a current whose metadata says it contains Stokes (`Partial`/`Unknown` refused unless
  `accept_partial_stokes_overlap`, which is recorded in provenance); Stokes with `leeway_absorbs_stokes`.
- **One ocean per run.** `ocean_error` is realised once from `seed` and shared by every particle; diffusion is
  the only per-particle randomness (particle i uses its own random stream, so thread count never matters).
- **Pléiades:** 21 and 23 March come from one call with both in `output_times`.
- **Field gaps end a trajectory as themselves.** A gridded product's `Land` gap means stranded in the
  product's land mask before the coastline caught the particle; time outside a field's axis is
  `OutsideTime`, never clamped (the archive clamped).

### Settling: the profile query

```rust
use mh370_ocean::profile::{ProfileSource, BelowModelBottom, BottomRelation, DepthStatus, VerticalVelocity};
use mh370_ocean::analytic::UniformColumn;
use mh370_ocean::stochastic::{OceanErrorModel, ErrorKind, VerticalStructure};

let col  = UniformColumn::new(0.10, -0.05, None, vec![0.5, 10.0, 100.0, 1000.0, 3000.0], 4000.0); // w absent
let prof = col.profile(t, [lon, lat])?;          // Profile: depth_m, u_east, v_north, w_up, temperature,
                                                 // salinity, pressure_dbar, model_bottom_m, time_axis
match prof.bottom_relation(seabed_m) {           // WithinModel | SeabedDeeperThanModel { model_bottom_m, seabed_m, gap_m }
    _ => {}
}
let s = prof.at_depth(z_m, Some(seabed_m), BelowModelBottom::HoldDeepestLevel)?;
// s.u_east, s.v_north; s.w_up: Option<f64> (None when the product has none - never 0);
// s.status: Resolved | Extrapolated { rule, model_bottom_m, seabed_m }
// rules: Refuse | HoldDeepestLevel | LinearToZeroAtSeabed; Err(DepthGap) for AboveSurface, BelowSeabed, refused
let err = OceanErrorModel { kind: ErrorKind::Eddying { sigma_m_s: 0.05, length_scale_m: 50e3, time_scale_s: 5.0 * 86400.0, modes: 64 },
                            vertical: VerticalStructure::Exponential { efold_m: 500.0, deep_ratio: 0.3 } }
          .realise(impact_event_seed);           // one realisation per impact event, shared by its fragments
let e = err.velocity(t, [lon, lat], z_m);        // add it yourself: components stay separate
```

`w_up` is `VerticalVelocity::Absent | Present(Vec<f64>)` on the profile; the type has no way to say zero for
absent. Temperature keeps its product's kind (`Potential` or `InSitu`) for the TEOS-10 layer to convert once.
Pressure is Saunders (1981) until TEOS-10 lands (deliverable 8) — provisional.

### Products

`mh370_ocean::products::catalogue()` holds machine-readable records for GLORYS12V1, WAVERYS, OSCAR v2 Final,
BRAN2016 and ERA5 10 m wind: dataset id, credential, resolution, coverage, time axis, depth convention,
variables with units, and `Contents { geostrophic, ekman, stokes, tides, inertial }`. Findings worth your
attention:
- **BRAN2016 may not reach drift's period end.** CSIRO states it spans January 1994 to August 2016; drift
  needs 30 September 2016 (latest stringent find 23 June 2016, so a run ending in August loses only the
  tail). Marked `covers_drift_period: Partial` until the NCI catalogue is checked.
- **OSCAR v2 already contains the wind-driven term** (geostrophic + Ekman + thermal wind, averaged over the
  top 30 m; `ug`, `vg` are the geostrophic part). Never add a separate Ekman term to it.
- **GLORYS12V1 has no Stokes and no tides**; its daily mean attenuates near-inertial motion without removing
  it. Its multiyear daily dataset carries no vertical velocity, so settling will see `Absent`.
- **ERA5 `u10` is the actual wind, not the neutral wind `u10n`.** A fitted leeway must say which.
- The archive's 100 m²/s and CSIRO's 5 NM/day are not the same diffusion: 3.17 NM vs 5 NM RMS after one day
  (K = 100 vs 248 m²/s).

### Provisional, and what is not done

Throughput (deliverable 5) is **not measured**: the machine is at load ~40 under the core run and a number
taken now would be wrong. The real coastline and segmentation (6), bathymetry (7), TEOS-10 (8), drogued GDP
replay (9) and the product recommendation (10) are not started. Diffusion and ocean-error **parameter values
are not chosen**: the API exposes them; the defaults in my tests are test values. The ocean-error model's form
(one model for drift and settling, or two) is still the open question of brief §8. Beaching is tested at step
end points, which is exact for a straight coast; the real coastline will need sub-stepping at headlands.

— ocean transport (architecture sub-agent)

## 2026-10-09 - ocean settling: stub matched to 311e481, and one new requirement from a measurement

**Matched.** Settling's stub (`hypotheses/settling/ocean_stub.rs`, `hypothesis/settling` 9fb50ef) now
uses your `Profile` field names, `at_depth(z, seabed, rule) -> Result<DepthSample, DepthGap>`,
`BelowModelBottom { Refuse, HoldDeepestLevel, LinearToZeroAtSeabed }` and `VerticalVelocity::Absent`,
with the same semantics. Settling selects the rule per run (`hold-deepest-level` default; the other two
are declared alternatives) and reports the extrapolated depth range per element; `Refuse` leaves the
element not computed. The swap should be a field change. Two things it still needs from you:

1. **In-situ density per level** (or a `rho(z)` beside `at_depth`) from the TEOS-10 layer. Settling's
   terminal speed depends on rho_w(z): about -1.5% in w by 6 km. Until deliverable 8, the stub carries a
   provisional density column, labelled stub-only.
2. **Hypotheses may not depend on `mh370-ocean` today** (`hypotheses/Cargo.toml` allows only
   hypothesis, geo, serde, toml). Raised with core and architecture; noted here so the swap is not
   assumed to be free.

**New requirement, from a measurement.** Settling's first sensitivity pass (stub ocean, provisional;
`results/settling-first-pass/`) finds that **the float phase before sinking dominates where light
elements rest**. Removing it shrinks cabin contents' 90th-percentile resting offset to 0.07 of baseline,
and it moves intact wing and fuselage sections by kilometres. The float phase is up to a day of **surface
transport with a leeway term**. That is advection, and under the 8 October ruling it is yours, not
settling's. The stub currently multiplies a constant velocity by the float time, which is acceptable only
as a stub. Settling therefore asks to use your **batch forward integrator** for that phase:

- release position and time per element (impact plus carry), output time = that element's own sink time,
  which varies per element (minutes to about 24 h);
- an `ObjectResponse` with `c_wind` = the element's leeway (0.01-0.05) and `a_stokes` taken from
  whatever drift settles on for low-windage floating debris;
- the **same ocean-error realisation per impact event** as the descent, so the float and sink phases
  see one ocean (rule 10).

This makes settling a third consumer of the integrator, beside drift and Pleiades, for short horizons.
It also puts an overlap with drift on the record: an element that floats for a day before sinking and
one that stays afloat differ only by where the float-time distribution is cut. That boundary belongs in
the shared breakup-field freeze (`results/breakup-field-candidate.md` section 5), not in either module.

**Ocean error.** Settling's stub error is banded by depth (surface, upper 1 km, deep, and a near-bottom
band within 200 m of the seabed for unresolved bottom-boundary-layer and topographic motion), with one
realisation per impact event. If `VerticalStructure` can express those bands, with a near-bottom band
keyed to distance above the seabed rather than to depth, settling can take `OceanErrorModel::realise(seed)`
unchanged, seeded per impact event.

- ocean settling

## 2026-10-09 01:58 UTC - architecture: URGENT - CPU, read before your next run or build

**Machine load is 112 / 142 / 154 on 18 cores** (1/5/15-minute averages). Core's 16-hour run is on
seed 2 of 8 and every minute of oversubscription moves its 08:30 MT finish later.

**My overnight rule was incomplete.** `cargo -j 4` limits compilation only. Engine binaries and test
suites use every core through Rayon regardless. From now until core posts DELIVERED:

1. **Every engine run and test: `RAYON_NUM_THREADS=2`**, and `cargo test ... -- --test-threads=2`.
2. **No full-scale or pilot runs.** Smoke-scale only. End of flight: the children-per-parent pilot waits
   for the morning. Settling: first-pass runs at smoke scale only.
3. **No more than one heavy process per module at a time**, sub-agents included. If you have spawned a
   sub-agent that runs code, tell it the same.
4. **Disk:** free space fell to about 1.2 GiB around 01:45 UTC and has recovered to 41 GiB; the writer
   is not identified. If your session wrote and deleted large files in that window, say so here. The
   25 GiB floor stands.

Code-reading, writing, review, literature work and small tests are unaffected. Keep going on those.

## 2026-10-09 - ocean drift: stub matched to 311e481, and one field the API does not yet return

Drift's stub now sits behind a drift-side `Transport` trait whose types mirror yours exactly -
`[lon, lat]`, unix seconds, `Particle { release, release_time, response: ObjectResponse { a_stokes,
c_wind, leeway_angle_deg } }`, one ocean realisation per call from `seed`, a terminal fate per
particle (`hypotheses/debris-drift/transport.rs`, branch `hypothesis/debris-drift` at `bf82159`).
When O1/O2 land, the swap is one `impl Transport for` your `integrate`, and the stub is deleted.

**One request: along-coast chainage on every beaching.** `Event::Beached { t, at, segment }` places a
find in a segment but not within it. Drift's recovery layer (D5 of `results/davey-ch11-alignment.md`)
puts a locality kernel along the coast and normalises it over the coast, Q(x) = sum over segments of
the kernel mass in each segment times the identification integral. That needs a continuous
along-coast coordinate: please add `chainage_m` (arc length along the segmented coastline, continuous
across segment boundaries, with a per-island origin) to `Beached`, and publish the segment edges in
the same chainage. With a GSHHG coast, each island needs its own chainage line; a find on Reunion
and a beaching on Mauritius are then never "close along the coast", which is correct.

**How drift will read the other fates.** `LeftDomain`, `FieldGap`, `NonFinitePosition` and
`ReleasedOnLand` stay in the release count and are reported as a model-error fraction per node, never
dropped and never treated as lost at sea (the review of prior work, item 4: dropping them
survivor-conditions Q). `Afloat` at the window end is a genuine non-arrival. If the model-error
fraction is non-negligible at a node, drift flags the node rather than scoring it.

**Two smaller points.** (1) Drift runs `threads: 2` until core delivers, per tonight's CPU rule.
(2) Drift's shared-environment realisations are separate calls with separate `seed`s, marginalised
outside the product over finds; please confirm that varying `seed` with `OceanErrorModel::none()`
changes only the diffusion streams, so that "one realisation per seed" has a defined meaning when the
error model is off.

- ocean drift

## 2026-10-09 — ocean transport (architecture sub-agent): first real product, throughput, chainage, K as eta

**Commit `f71a7d2` on `core/ocean-transport`**, 17 of 17 tests pass. Still not importable until O1/O2 land.

**1. Chainage on beaching (drift's request). BREAKING, small.** `Event::Beached { t, at, segment, line,
chainage_m }` and `Snapshot::Beached { at, segment, line, chainage_m }`. `line` is one continuous chainage
line: a mainland stretch, or one island with its own origin. `chainage_m` is arc length on the sphere along
that line from its origin, continuous across segment boundaries. `Coastline::segments() -> Vec<SegmentEdges
{ segment, line, start_m, end_m }>` publishes the edges in the same chainage. `StraightCoast` gains a `line`
field and measures chainage from `a`; its end segments extend to plus or minus infinity. Patterns written as
`Beached { t, at, segment }` without `..` need the two new fields. Tested: chainage = R x (lat + 40 deg) on a
meridian coast to 1e-6, a find lies within its own segment's edges, edges are contiguous, and an oblique line's
edges are exact on a parallel.

**2. Diffusivity is an eta component (ruled this morning).** `DiffusivityPrior::{Fixed { k_m2_s },
LogUniform { k_min_m2_s, k_max_m2_s }}`. `prior.draw(seed) -> Diffusion::Diffusivity { k }` gives **one K per
run** on its own random stream, so one run seed fixes one eta = (K, ocean-error realisation), shared by every
particle and every find. `ln_density(k)` is there for reweighting. **Provisional prior:**
`DiffusivityPrior::provisional(ocean_model)` is log-uniform on **30-1000 m²/s** (one-day 2-D RMS 1.7-9.9 NM)
for every product. It spans the archive's 100 and CSIRO's 248 m²/s (5 NM/day; drift's correction is right).
It is conditional on the product because the sub-grid part depends on resolution, and it is to be narrowed
per product by the drogued-drifter replay (deliverable 9).
Use: `spec.diffusion = DiffusivityPrior::provisional(&forcing.ocean_model()).draw(seed); spec.seed = seed;`.

**3. Drift's seed question: confirmed and tested.** With `OceanErrorModel::none()` and a fixed diffusion,
varying `seed` changes only the per-particle diffusion and refloat streams. With no diffusion either, it
changes nothing (`diffusivity_is_one_eta_draw_per_run`).

**4. First real product: GLORYS12V1 surface `uo`/`vo`**, 15-120 E, 50-0 S, 7 March to 30 April 2014, 55 daily
means, in `/Users/pete/Downloads/mh370-ocean-data/glorys12/`. Recorded in `results/ocean-data-manifest.md`,
appended after drift's GDP section. Load it with
`GridField::load(Path::new(".../glorys12v1_uo_vo_surface_20140307-20140430.json"))`. Its contents and time
axis come from the catalogue, not the file. Two conventions to know:
- each daily mean is placed at **label + 12 h** (labels are 00:00 UTC). This is provisional: the other reading
  shifts the field 12 h;
- values are int16-quantised at 0.6 mm/s.
It covers Pléiades' 8-23 March window and drift's first 52 days, not drift's full period.

**5. Throughput (deliverable 5), measured on that product.** `examples/throughput.rs`, run under
`/tmp/.mh370-heavy.lock` with up to 12 threads. Particles were released on a grid over 92-106 E, 26-40 S at
12:00 UTC on 8 March 2014 and run 52 days at a 6 h step, current only, K = 248 m²/s; all stayed afloat.
One evaluation is one 8-node trilinear sample with land renormalisation, wall time over all integrator work.

| threads | particles | field evaluations | wall | evaluations/s | per thread |
|---|---|---|---|---|---|
| 1 | 40,000 | 1.66e7 | 2.38 s | 7.0e6 | 7.0e6 |
| 12 | 480,000 | 2.00e8 | 2.92 s | 6.8e7 | 5.7e6 |
| 1 (repeat) | 40,000 | 1.66e7 | 2.83 s | 5.9e6 | 5.9e6 |

**Machine load averaged 105-120 on 18 cores during the measurement** (another job was running), so these are
lower bounds, not a quiet-machine figure. Against drift's assumed **2e7 per second per core**, the achieved
**5.7-7.0e6 per thread** is 2.9-3.5 times lower. The pilot at 11 M trajectories x 2,920 steps x 2 evaluations is
6.4e10 evaluations. Current only, at 6.8e7/s on 12 threads, that is about **16 minutes**. With Stokes and wind
fields as well, roughly three evaluations per stage, it is about **0.8 h**, against the brief's 0.06 h.
That is still cheap; re-measure on a quiet machine before sizing production.

**6. Settling's three requests: queued, not built today.**
- Per-element output time for the float phase. Today one output-time list is shared per call; a per-particle
  end time is the clean form, and changes `Particle`.
- `VerticalStructure` bands, including one keyed to height above the seabed.
- In-situ density per level, with TEOS-10 (deliverable 8).
Until then settling can call `integrate` once per sink-time bin with that bin's own `output_times`, sharing
one `seed`, so all bins see the same ocean.

— ocean transport (architecture sub-agent)

## 2026-10-09 - ocean drift: one more ObjectResponse term, from the CSIRO Part II primary text

CSIRO's measured flaperon response is a **constant-magnitude** extra leeway of about 10 cm/s, directed
about 16° left of downwind (field mean; range 0-30°), on top of a 1.2%-of-wind baseline. See Griffin
et al. 2017, Part II, pp. 9-10, and `results/debris-drift-flaperon-provenance.md`. `ObjectResponse`
can express `c_wind · R(angle) · U10`, which scales with wind speed, but not a constant speed along
the rotated downwind direction.

Request: add `leeway_speed_mps` to `ObjectResponse`, defaulting to 0. Its velocity contribution is
`leeway_speed_mps · R(leeway_angle_deg) · U10/|U10|`, set to zero (or declared) when |U10| is below a
small threshold. The one angle applies to both wind terms. Persistent per particle like the rest.
Composition rule: a particle with `leeway_speed_mps > 0` and `a_stokes > 0` is the transplanted-system
case of review error E1. Refuse it unless the caller declares `explicit_residual = true`, recorded in
provenance.

- ocean drift

## 2026-10-09 - interface request from hydroacoustics (sound speed, path bathymetry), and a stub disclosed

Hydroacoustics needs two things from the shared layer. Neither is a likelihood input on its own:
both feed a propagation engine (KRAKEN normal modes; RAM PE as a cross-check), whose transmission
loss and travel time then enter the module's predictions.

**1. Sound-speed profiles.** c(z) from the surface to the local bottom at an arbitrary
(lat, lon, time), from the same TEOS-10 evaluation that serves settling's density, as settling
recommended. Climatology is adequate for propagation, but the time axis must be at least seasonal
and should be monthly in the upper 1,500 m. I need the product's own spread as well as its mean
(WOA's standard deviation or an ensemble), so that sound-speed uncertainty becomes a declared
alternative rather than a hidden constant. Times needed: October 2001 (Blackman airgun lines),
May-June 2003 (Blackman A1-A11), March 2014 (MH370), and the F-35A event at H11 (Brown et al. 2026).
Product choice is yours.

**2. Bathymetry along geodesic paths, not at points.** Depth along WGS84 geodesics of 1,600 to
about 10,000 km: source region to H01 and H08 for MH370 and Blackman, and to H11 for the F-35
calibration. It should come at the native grid resolution, with the Type Identifier kept per sample
and with a cross-track corridor query (the maximum elevation within a stated half-width), because
blockage is set by the shallowest feature in the ensonified corridor, not only on the track. It
should be one surface shared with settling's impact-point lookup (AusSeabed near source, GEBCO
elsewhere, with a provenance flag), never two.

Frame: geographic WGS84, depth positive down in metres, pressure from depth by gsw.

**Stub disclosed (approved 2026-10-09, morning rulings item 5), so that you can reject it rather than
inherit it.** It lives in `hypotheses/hydroacoustics/data/stub/`, built by
`prepare/build_path_stub.py`. Every number through it is PROVISIONAL, and it is deleted when this
API serves profiles and bathymetry. Its assumptions:
- **Two paths only:** air9 (line midpoint -27.5612, 98.8821) to the H01W and H08S triad centroids
  (FDSN). The H08S position is the 2002 FDSN epoch, used for a 2001 event.
- **Bathymetry:** GEBCO_2026 ice-surface grid and TID via OPeNDAP at CEDA. Nearest cell (no
  interpolation) every 0.5 km along track, plus the corridor maximum within +/-2 km across track.
- **Sound speed:** WOA23 decade 95A4 (1995-2004), season 16 (Oct-Dec), 1.00 deg, t_an and s_an only
  (no spread yet), bilinear in latitude and longitude, native levels, every 25 km. gsw SA_from_SP,
  CT_from_t, sound_speed at in-situ pressure. A level is NaN where WOA has no data, never filled.
- **What it does NOT do:** no time interpolation within a season, no mesoscale variability, no
  sediment or geoacoustic bottom model (that is mine to declare inside the propagation engine), no
  uncertainty.
- **As built** (module branch `74d9901`, DOI fixed at `59d834d`): air9 to H01W is 1,662.5 km, with 3,326
  bathymetry samples and 67 profile nodes; air9 to H08S is 3,549.0 km, with 7,099 samples and 142 nodes.
  The stub totals 1.9 MB committed. The WOA box netCDF (1.35 MB) is an artifact only. GEBCO_2026 DOI
  10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa.

— hydroacoustics

## 2026-10-09 — ocean transport (architecture sub-agent): item 1 landed — `leeway_speed_mps` (ruling D-d)

**Merged to `claude-science-sep29`** together with `f71a7d2` (chainage, `DiffusivityPrior`, `GridField::load`),
now that O1/O2 are in: commit `8d1160f`, 19 of 19 tests pass. `mh370-ocean` is importable from hypotheses.

- `ObjectResponse { a_stokes, c_wind, leeway_angle_deg, leeway_speed_mps }`; `ObjectResponse::new` sets the
  last two to 0. Contribution `(c_wind + leeway_speed_mps/|U10|) * R(leeway_angle_deg) * U10`, so **one angle
  serves both wind terms**. The constant-magnitude term is **zero for |U10| < `LEEWAY_CALM_WIND_MPS` = 0.5 m/s**
  (declared, in provenance). Persistent per particle like the rest.
- **Sign:** `leeway_angle_deg` is positive clockwise (right of downwind). CSIRO's "16 deg left of downwind" is
  **-16**; D-a's U(0, 30) left is U(-30, 0) here.
- **Refusal:** any particle with `leeway_speed_mps > 0` and `a_stokes > 0` is refused
  (`CompositionError::DoubleCount`) unless `RunSpec.explicit_residual = true`, which provenance records.
  `leeway_speed_mps` without a wind field is `MissingComponent(Wind10m)`.
- **BREAKING:** `RunSpec` gains `explicit_residual: bool`; `ObjectResponse` literals need the new field.
- Tests: 0.10 m/s at -16 deg gives 8.64 km/day at 5 and at 15 m/s wind, with the westward share sin 16 deg;
  1.2% of 10 m/s plus 0.10 m/s on one angle gives 0.22 m/s; calm wind gives zero; refusal and override.

— ocean transport (architecture sub-agent)

## 2026-10-09 — ocean transport (architecture sub-agent): item 2 — production forcing, sized before starting

**Domain and period.**
- **Box:** drift's, 15-120 E by 50-0 S. Every find in `debris-evidence-audit.csv` lies inside it, between
  22.0 and 63.5 E and between 5.1 and 34.2 S.
- **Period:** 7 March 2014 to 31 January 2017, which is 1,062 days.
  - The stringent nine run from 29 July 2015 to 23 June 2016.
  - The expanded dated set ends on 27 January 2017, so the window covers it as a sensitivity with a few
    days' margin.
  - Drift asked for at least 30 September 2016.

**Products, with disk and network estimates.**
- Disk figures are from Toolbox dry runs or exact array sizes.
- Network figures are the bytes moved, which mostly never reach disk.
- The derived float32 grids are what `GridField::load` reads.

| product | what | cadence | disk (downloaded) | derived f32 | network |
|---|---|---|---|---|---|
| GLORYS12V1 `uo`/`vo` at 0.494 m, 1/12 deg | extends the existing 7 Mar-30 Apr 2014 slice to 31 Jan 2017 | daily mean | 2.9 GB | 6.4 GB (whole period) | ~64 GB |
| WAVERYS `VSDX`/`VSDY`, 0.2 deg | surface Stokes drift | 3-hourly instantaneous | 4.3 GB | 9.0 GB | ~76 GB |
| **ERA5** `u10`/`v10`, 0.25 deg | 10 m wind, **genuine ERA5** from Google's public ARCO-ERA5 store (`gcp-public-data-arco-era5`, Carver et al. 2023), so no CDS key is needed and **there is no substitution** | 3-hourly instantaneous (00, 03 ... 21 UTC), taken from the hourly store | written directly as f32 | 5.8 GB | ~45 GB |
| BRAN2016 `u`/`v` top level, 0.1 deg | CSIRO-system reproduction arm (D-b), NCI THREDDS NetCDF Subset Service | daily mean | ~2.0 GB | 3.8 GB | ~2 GB |

**Total on disk: about 34 GB**, against the 300 GB budget, with 401 GiB free. Network transfer is about 190 GB.
All of it goes to `/Users/pete/Downloads/mh370-ocean-data/<product>/`, with sha256 values in
`results/ocean-data-manifest.md`.

**Confirmed from the NCI catalogue: BRAN2016 ends in August 2016.** `ocean_u_2016_08.nc` is the last file,
which settles the conflict between sources. The CSIRO-system arm on BRAN2016 therefore covers the
stringent nine (last find 23 June 2016) but none of the later finds. The same catalogue shows that
**BRAN2016 does distribute vertical velocity** (`ocean_w_*`), so the product record changes from Unknown to
Included.

**Wind cadence, a decision inside my module.** ERA5 is used at 3-hourly instantaneous values. With drift's
6 h RK2 step, every evaluation time (t and t + 3 h) then falls on a stored instant. Hourly data would quadruple
the volume for no gain at this step, and 6-hourly data would put every midpoint between stored instants.

New hosts were approved by Pete: `thredds.nci.org.au` and `gcp-public-data-arco-era5.storage.googleapis.com`.
The plain `storage.googleapis.com` host is permanently denied by the sandbox.

— ocean transport (architecture sub-agent)

## 2026-10-09 ~01:00 UTC - ocean drift: what the pilot needs loadable, and the arm it runs

**The pilot runs the CSIRO-system arm (ruling D-b).** That is current plus ERA5 10 m wind, with no
explicit Stokes, for every motion class. So it needs **GLORYS12 currents and ERA5 wind only. WAVERYS
is not needed for the pilot**; it is needed only by the explicit-Stokes extension, which is off by
default. BRAN2016 is the reproduction setting for the same arm and follows when you deliver it.

**One blocker, and it is in your crate: multi-file time axes.** The pilot integrates from 8 March 2014
00:19 UTC to 30 June 2016 (day 845), the end of the discovery window for the stringent nine.
`GridField::load` reads one manifest and one file:
- GLORYS12 is converted only for 7 Mar-30 Apr 2014; the rest is NetCDF, by year;
- ERA5 is in four yearly f32 files.

A query between the last slice of one file and the first of the next is `OutsideTime` in both. The
seam between two daily means is 24 h, and every year-end falls inside the run. A consumer-side
concatenation would be field interpolation across files, which is yours by rule.

Either form meets the need:
1. `GridField::load_many(&[manifest...])`, which checks that the axes match and interpolates across
   file seams; or
2. one converted manifest per product for 7 Mar 2014 to 30 Jun 2016 (or to 31 Jan 2017).

RAM is not a constraint: GLORYS12 for 7 Mar 2014-31 Jan 2017 is 6.4 GB and ERA5 5.8 GB, against 64 GB.

**What I will do with the fields, so they are sized right:**
- 1,709 release nodes (99% main band, 10 NM spacing), 10^4 particles per node, split across the three
  motion classes;
- one diffusivity draw (K = 248 m²/s fixed for the pilot only; production marginalises K under your
  `DiffusivityPrior`);
- 6 h RK2 step, about 3,380 steps;
- `NoCoast` until deliverable 6 lands.

Under `NoCoast`, drift reads **`FieldGap { gap: Land }` stranding in the GLORYS12 1/12° mask as
beaching**, at the event's `at`, and maps that position to its own find segments. This is declared
PROVISIONAL. The 1/12° mask keeps Réunion, Mauritius and Rodrigues. Please confirm that a Land gap from
the **current** field reports `at` within about one grid cell of the first all-land bracket. ERA5 has
values over land and will not strand.

At your measured 6.8e7 evaluations/s on 12 threads, the pilot is about 1 h under the lock.

- ocean drift

## 2026-10-09 — ocean transport (architecture sub-agent): item 2 landed — production forcing on disk, one product stopped on licence

**Code `4f58d5d`, merged to `claude-science-sep29`.** Data are in `/Users/pete/Downloads/mh370-ocean-data/`, with
per-file sha256 in `results/ocean-data-manifest.md` and citations and licences in `crates/ocean/REFERENCES.md`.

Each series loads with `GridField::load_series(path)` and covers 15-120 E, 50-0 S:

| component | series manifest | period | step | derived f32 |
|---|---|---|---|---|
| current: GLORYS12V1 | `glorys12/grid/glorys12v1_uo_vo_surface.series.json` | 2014-03-07 to 2017-01-31 (1,062 daily means at label + 12 h) | 24 h | 6.4 GB |
| Stokes: WAVERYS | `waverys/grid/waverys_vsdx_vsdy.series.json` | 2014-03-07T00 to 2017-01-31T00 | 3 h | 9.0 GB |
| wind: **ERA5** (ARCO-ERA5) | `era5/era5_u10_v10_3h.series.json` | 2014-03-07T00 to 2017-01-31T21 | 3 h | 5.8 GB |

- `examples/forcing_check.rs` verified each series: a uniform step, the expected axes, and sane samples. For
  example, GLORYS at 35 S, 95 E on 1 July 2015 gives (0.04, -0.10) m/s, and land in Madagascar is flagged.
- **Wind: no substitution.** This is genuine ERA5 from Google's public ARCO-ERA5 store, so no CDS key was needed.
- **WAVERYS Stokes is quantised at 0.005 m/s** in the distributed file. The maximum in 2016 is 1.4 m/s, which
  is unusual and is on my list to check.

**BRAN2016: stopped on licence, decision with Pete.**
- NCI serves the files anonymously. The CSIRO terms (`gb6_license.txt`), however, require **registration
  with CSIRO before access**, and they license use **for government-funded research only** (clauses 1, 4
  and 5).
- 15 monthly files (March to October 2014, 544 MB) arrived before I read the terms. **Nothing uses them.**
- Pete's options:
  1. register with CSIRO and confirm the use qualifies;
  2. seek a licence from CSIRO;
  3. drop BRAN. The D-b reproduction arm then runs on GLORYS12 as a declared departure.
- **This blocks D-b's reproduction setting only.** Nothing else depends on BRAN.
- The catalogue also settles two facts: coverage is January 1994 to August 2016, and BRAN2016 distributes
  `ocean_w`.

**Swap for drift.** Use the three series with `Forcing { current, stokes, wind10 }`. The CSIRO-system arm
(D-b) is `ObjectResponse { a_stokes: 0.0, c_wind: 0.012, leeway_angle_deg: θ, leeway_speed_mps: c0 }` with
the Stokes field omitted.

— ocean transport (architecture sub-agent)
## 2026-10-09 ~02:00 UTC - ocean drift: two follow-ups

1. **Full-period fields.** I see `glorys12/grid/` being written. When it and ERA5 can be loaded across
   file seams, drift's pilot runs. Please post the manifests' paths and the loader call.
2. **A second leeway angle, small.** CSIRO rotates only the *extra* leeway (Part II, p. 13, Fig. 3.1
   caption: "the direction of the 'extra' leeway velocity"), not the 1.2% baseline. Please add
   `leeway_speed_angle_deg`, applied to the `leeway_speed_mps` term only, with `leeway_angle_deg`
   continuing to rotate `c_wind`. The default (NaN, or the same value) keeps today's behaviour. Until
   it lands, the pilot runs with one angle as a declared departure.

- ocean drift

## 2026-10-09 — ocean transport (architecture sub-agent): item 3 landed — one bathymetry surface, sound speed with spread (hydroacoustics, settling, searched areas)

**Code `75ac7df`, merged.** 24 tests pass. Data and sha256 values are in `results/ocean-data-manifest.md`; citations
are in `results/ocean-references.md` (moved from the crate per the 02:25 ruling).

**Bathymetry: `mh370_ocean::bathy::Bathymetry`, one surface for everyone.**
- `Bathymetry::load(&[layer manifests, finest first], Some([lon_min, lon_max, lat_min, lat_max]))` reads only
  the window it needs. The full layer is 2.2 GB.
- `.at([lon, lat]) -> Option<BathySample { elevation_m, depth_m, source, tid }>` returns the nearest native cell,
  with its provenance flag (`BathySource`) and the GEBCO Type Identifier.
- `.path(a, b, spacing_m, half_width_m)` samples along the WGS84 geodesic (Karney, geographiclib-rs). Each
  `PathSample` has the track sample and the **corridor maximum** (the highest cell within the half-width,
  sampled on perpendicular geodesics), with its signed cross-track offset (positive to the right) and its TID.
- `.inverse(a, b) -> (metres, azimuth)`.
- The layer is GEBCO_2026 at 40-180 E, 60 S-30 N:
  `/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json`.
- **AusSeabed (GA MH370 Phase 1, 150 m) is NOT yet in the surface: data not obtained.** The GA geoserver
  returned 502, and the dataset is not in NCI `rr1`. The layer mechanism is ready (f32, NaN outside
  coverage, `BathySource::AusSeabed`, first in priority). Until then every answer says `Gebco2026`, and TID
  10/11 marks where GEBCO already carries multibeam, including GA's MH370 surveys.
- **Settling:** `bathy.at(impact).depth_m` feeds `profile.bottom_relation(seabed)` and `at_depth(z, Some(seabed), rule)`.
- **Searched areas:** use the same `at`, or `path` along sonar lines for terrain masking.

**Sound speed: `mh370_ocean::soundspeed::SoundSpeedClimatology`.**
- **Product:** WOA23, 1 degree. Each epoch uses its own decade: 1995-2004 for October 2001 and May-June
  2003, 2005-2014 for March 2014, and 2015-2022 for later events, including F-35A at H11. Monthly fields are
  used above 1,500 m and seasonal ones below.
- **TEOS-10:** applied once in preparation with official `gsw` (`p_from_z`, `SA_from_SP`, `CT_from_t`,
  `sound_speed`). At runtime only `p_from_z` is computed, with GSW-rs. The two agree to 1e-9 on fixtures, and
  re-evaluating exported SA/CT/p with `gsw` reproduces the exported c to 0.012 m/s at most, the residue of
  interpolating c, SA and CT separately.
- **Spread:** `c_sd` is linearised from the **all-decade objectively analysed SDs** (`decav` `t_sdo`/`s_sdo`),
  with T and S deviations treated as independent. This is **declared**: warm-salty correlation would make the
  true spread larger.
  - **Finding:** WOA23's decadal `*_sd` exist in only 16-38% of cells, and the 1995-2004 `*_sdo` are exactly
    zero in about 30% of ocean cells, which would call a sparsely sampled profile certain. With `decav`, the
    zero-spread fraction is 0.04%. Those cells are reported, never floored.
- **Lookup:** `clim.profile([lon, lat])` is bilinear, renormalised over corners with data at each level, and a
  level with no data is NaN, never filled. `woa23_period(unix_t) -> (decade, month)` selects the file.

**Hydroacoustics: files for KRAKEN/RAM.** `examples/ocean_paths.rs <request.json> <out-dir>` writes
`<name>_bathymetry.csv`, `<name>_soundspeed.csv` and `<name>_meta.json`. They are already built for your two
paths at 8 October 2001 in `/Users/pete/Downloads/mh370-ocean-data/products/hydro-paths-2001-10/`:

| path | geodesic | samples (250 m) | track depth | corridor max (±2 km) | TIDs on track |
|---|---|---|---|---|---|
| air9 to H01W | **1,662.8 km** | 6,653 | 1,537-5,862 m | -1,474 m | 11, 40, 44, 70 |
| air9 to H08S | **3,549.2 km** | 14,198 | 1,613-5,621 m | -1,576 m | 11, 40, 44 |

Both lengths agree with ruling H1. **Your stub's 1,662.5 km is its last 0.5 km sample, not the geodesic.**

**Your stub assumptions, adopted or rejected:**
1. *Two paths only:* **extended.** The export takes any list. Send air8's coordinates (ruling H3) and the
   F-35A event position and time, and I will add them.
2. *H08S at its 2002 FDSN epoch for a 2001 event:* yours to declare. Not changed.
3. *GEBCO nearest cell every 0.5 km, corridor ±2 km:* **nearest cell adopted.** The spacing now defaults to
   **250 m**, because 0.5 km is coarser than GEBCO's native 15 arc-seconds (about 0.46 km north-south and
   0.40 km east-west at 30 S) and can step over a cell. The half-width stays your choice.
4. *WOA23 95A4 season 16, t_an/s_an only, bilinear every 25 km:*
   - **bilinear and 25 km adopted**;
   - **season-only rejected:** the October monthly field is used above 1,500 m, as WOA itself provides it;
   - **no-spread rejected:** `c_sd` is supplied.
5. *gsw at in-situ pressure; NaN never filled:* **adopted.**
6. *No time interpolation within the period, no mesoscale:* still true here (month resolution, climatology).
   **Suggested declared alternative:** GLORYS12 T/S (daily, 1/12 deg, 1993 onward, so all your epochs
   including 2001 and 2003) through the same TEOS-10 path would add the mesoscale. Say if you want it; it is
   a full-depth download for your path corridors only.

— ocean transport (architecture sub-agent)

## 2026-10-09 — ocean transport (architecture sub-agent): item 4 landed — settling's three queued items

**Code `fe05b0b`, merged.** Tests: `per_particle_end_time_stops_each_particle_at_its_own_time`,
`banded_error_keys_the_bottom_band_to_height_above_seabed` and `teos10_matches_official_gsw`.

1. **Per-particle end time for the float phase.**
   - `Particle { ..., end_time: Option<f64> }`; `Particle::new(release, release_time, response)` sets `None`.
   - The state at each element's own sink time is `Track.end: Option<Snapshot>`. Output times after it are
     `Snapshot::PastEnd`.
   - One call takes elements with different sink times and shares one ocean. Tested: identical to a run with
     that single output time under the same seed and eddying error.
   - **BREAKING:** `Particle` literals need `end_time` (use `Particle::new`), and `Snapshot` has a new variant.
2. **Bands.**
   - `VerticalStructure::Banded { surface_to_m, upper_to_m, near_bottom_m, factors: [surface, upper, deep,
     near_bottom] }`.
   - The **near-bottom band is keyed to height above the seabed** and takes precedence where the seabed depth
     is known: `realisation.velocity_with_seabed(t, p, z, Some(seabed_m))`.
   - **Each band has its own independent realisation** (separate random streams), so correlation holds within
     a band and not across bands. Surface, interior and bottom-boundary-layer flows are different processes.
   - Still one draw per impact event: `model.realise(event_seed)`.
   - Tested: surface-deep correlation below 0.1 over 2,000 draws; band amplitudes within 8%.
   - If you would rather have one realisation scaled by band, say so; it is a one-line switch, but it is a
     modelling choice and I made the more conservative one.
3. **In-situ density per level.**
   - `profile.teos10()? -> Teos10Profile { depth_m, absolute_salinity_g_kg, conservative_temperature_c,
     pressure_dbar, in_situ_density_kg_m3, sound_speed_m_s, sa_anomaly_included }`, and `.rho_at(z)` interpolates
     linearly.
   - For GLORYS-like profiles (potential temperature, practical salinity), SA is Reference Salinity with the
     **anomaly set to zero and flagged**. That is under 2e-5 relative in density here.
   - In-situ temperature is refused at runtime (it must be converted in preparation).
   - Pressure is now TEOS-10 `p_from_z`, which replaces Saunders.
   - Tested against official `gsw` to 1e-9 (rho 1041.5724 kg/m3 at 3,000 m, 33 S, potential temperature 2 C,
     SP 34.7).

— ocean transport (architecture sub-agent)

## 2026-10-09 — Pléiades: how the module uses the integrator, and two requests

- **Call shape used:**
  - `integrate` with GLORYS12V1 surface current plus ERA5 10 m wind, `stokes: None`;
  - `ObjectResponse { a_stokes: 0, c_wind: c, leeway_angle_deg: 0, leeway_speed_mps: 0 }`,
    `leeway_absorbs_stokes: true`;
  - `Diffusion::None`, `OceanErrorModel::none()`, `NoCoast`, 1 h step, `threads` = 2.
  - Tracks are deterministic. The module adds the spread **analytically** (2KΔt with your provisional K
    prior as quadrature nodes, plus a declared OU model error), so its likelihood is normalised and
    seed-free.
  - Two tables, written to the gitignored `engine/runs/pleiades/`: COSMO contacts to Pléiades times,
    and a 0.1° release grid at 00:20 UTC on 8 March to the COSMO and Pléiades times. All 214,221
    particles stayed afloat.
- **Request 1: the 15-day and 2-day transport-error size per product** (σ_e and decorrelation time, or
  the drifter-replay residual statistics they come from). The Pléiades two-epoch calibration is
  information-limited exactly at that scale: below about 6 km per component over 40-53 h it carries
  information, above about 10 km it carries none.
- **Request 2: a derived WAVERYS grid** if the explicit-Stokes system is to be an arm. Until then the
  module runs the absorbed-Stokes system only, and it says so.
- **The `ocean-model` label** the hook declares is `Forcing::ocean_model()` verbatim:
  `glorys12v1+era5-wind10`. Drift and Pléiades must declare the same string for joint
  marginalisation.

— Pléiades
